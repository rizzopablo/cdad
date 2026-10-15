#!/usr/bin/env python3
"""005-012 T4 RED — la entrega TARDÍA: el modo declarado `receive --late` de
`cdad_result.py` (máquina de recibos reusada) + la clase `late-delivery` de
`register-transition` (traza durable, sin reabrir ni aprobar).

Contract:
- docs/specs/005-012-transition-registration/spec.md §1 (el caso real 005-011:
  la entrega que quedó en el buzón), §2.1 (superficie CLI: `receive --late` y
  `register-transition --transition late-delivery …`), §2.2 (forma del registro
  y efecto de cada clase: `late-delivery` NO toca la feature, sólo la traza),
  §2.3 (**PD-13** + **PD-4** re-aplicado + PD-20), §2.4 (invariantes INV-2,
  INV-3, INV-7, INV-9), §5 D-5.
- docs/specs/005-012-transition-registration/plan.md §4 ficha T4 (test focal
  declarado `tests/test_005_012_t4_late_delivery.py`) + el bloque canónico
  `plan-tasks` (T4) rendido por el paquete.

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo de implementación NUNCA se importa y su código NUNCA se lee):

    python3 skills/cdad-cycle/scripts/cdad_result.py receive \
        --project-root <ABS> --execution-context <execution.json> \
        --packet <PACKET.md> --request <REQUEST.json> \
        --descriptor <RESULT.json> [--late]
    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
        --project-root <ABS> --transition late-delivery \
        --feature <closed-feature> --packet <packet-id> [--note <texto>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>

HOY el modo `--late` NO existe (el subcomando `receive` responde con un error de
uso, rc=2 «unrecognized arguments: --late») y la clase `late-delivery` NO existe
(el subcomando `register-transition` responde con un error de uso, rc=2
«invalid choice: 'late-delivery'»). Por eso cada test falla en la ASERCIÓN sobre
el comportamiento del contrato (rc, `semantic_status` del recibo durable, bytes
y campos del state, marcadores de rechazo), nunca en la invocación ni en una
precondición de fixture: los fallos RED son AssertionError de contrato, jamás
ImportError, SyntaxError, JSONDecodeError ni error de setup. En los rechazos la
aserción discriminante es el **marcador** (un error de uso de argparse también da
rc=2; los marcadores de dominio no).

Fixture: proyecto descartable en un tempdir, con el `HOME` del subproceso en un
tempdir VACÍO (nunca el HOME real, nunca este repo). La capa previa se produce
por el CAMINO LEGÍTIMO del CLI (`prepare` → `prepare --record-dispatch` →
`cdad_result.py receive` → `register-transition --transition delivery` →
`prepare` de un segundo paquete → `register-transition --transition closure` de
T3), y la entrega tardía se staged en el buzón `.cdad/inbox` con la forma de
`tests/test_003_002_t1_receive.py`. Los ids del fixture son sintéticos y
anónimos. Aislamiento: el fixture de la entrega tardía tiene DOS paquetes de la
MISMA ejecución — el primero con recibo durable y ya entregado (T1) y el segundo
`prepared` (SIN registro de despacho) — de modo que el cierre legitimo de T3
queda verde (PD-8(a) sólo exige recibo o disposición a los paquetes CON registro
de despacho) y el paquete de la entrega tardía pertenece a la ejecución de la
feature cerrada.

Mapeo test → postcondición (y caso mínimo del encargo):

  test_pd13_receive_late_persists_durable_receipt_and_normal_receive_stays_closed
      -> PD-13 (1) + INV-2. Caso **1**: con la feature CERRADA por el camino
         legítimo y una entrega staged en el buzón, `receive --late` → rc=0 y
         recibo durable bajo el root de resultados con `semantic_status:
         "pending"`; el `receive` NORMAL (sin `--late`) sobre la MISMA feature
         cerrada sigue fallando cerrado (no se relajó esa precondición) y no
         deja recibo. El `receive --late` NO escribe el state (INV-2).
  test_pd13_late_delivery_leaves_durable_trace_without_reopening_or_approving
      -> PD-13 (2) + INV-9 + PD-17. Caso **2**: `--transition late-delivery
         --feature <closed-feature> --packet <id>` → rc=0; la feature SIN
         cambio de estado (`status` sigue `done`, `closed_at`, `active_feature`
         y `current_stage` sin cambios); NINGUNA aprobación nueva
         (`approval_effect: false`, sin `approved_by`); y traza durable: UNA
         entrada de `stage_history` con `stage: "late-delivery"` y
         `transition: "late-delivery"` que nombra el paquete. La única
         diferencia del state (sha256 antes/después) es el append de la traza
         más `last_updated`.
  test_pd13_late_delivery_with_open_feature_fails_closed_state_incoherent
      -> PD-13 (rechazo) + INV-7. Caso **3(a)**: con la feature ABIERTA →
         rc=2, marcador `state incoherent` (la salida tardía es SÓLO para lo
         cerrado), sin efectos. Aislamiento: el paquete citado tiene recibo
         durable y pertenece a la ejecución activa, así que la única causa es la
         feature abierta.
  test_pd13_late_delivery_without_durable_receipt_fails_closed_evidence_missing
      -> PD-13 (rechazo) + PD-3 (reparto de marcadores) + INV-7. Caso **3(b)**:
         con la feature CERRADA pero SIN recibo durable para el paquete citado →
         rc=2, marcador `evidence missing`, nombrando el paquete y el recibo
         faltante, sin efectos. Aislamiento: la feature está cerrada (correcto)
         y el paquete pertenece a su ejecución; la única causa es la evidencia
         ausente.
  test_pd4_late_delivery_entry_has_no_approval_or_judgement_fields_and_prepare_stays_closed
      -> PD-4 (re-aplicado) + PD-18 + INV-9 + PD-13. Caso **4**: la entrada de
         `late-delivery` NO lleva `approved_by` ni campos de juicio
         (`verdict`, `disposition`, `criterion`, `review_*`) ni pin de contrato;
         y con la feature cerrada, un `prepare --role test-writer` posterior
         SIGUE fallando cerrado (la entrega tardía no reabre el ciclo ni
         habilita roles) y no publica paquete.
  test_pd10_pd11_late_delivery_entry_has_transition_key_and_identical_repetition_is_noop
      -> PD-10 + PD-11 (+ PD-13 condición 3). Caso **5**: la entrada lleva
         `transition_key` (clave nueva y aditiva); repetir la invocación
         IDÉNTICA → rc=0, SIN segunda entrada, state byte a byte idéntico y
         salida que nombra la entrada existente.
  test_pd17_validate_state_stays_green_across_the_late_delivery
      -> PD-17 (+ PD-13, + PD-20). Caso **6**: `validate-state` rc=0 ANTES de la
         operación, tras el `receive --late` y tras el `late-delivery`. El
         oráculo es `validate-state rc=0` —sin porcentajes ni conteos del state
         vivo del repo (el state auditado es el del FIXTURE).

Interpretaciones y límites declarados (no se inventó oráculo ni se debilitó un
test; el contrato fue verificable y no hubo detención):

1. **`late-delivery` se invoca SIN `--stage`.** §2.1 declara `--stage`
   obligatoria «salvo `disposition`» y PD-13 (2) muestra la invocación de
   `late-delivery` sin `--stage` esperando la etiqueta canónica
   `stage: "late-delivery"` (misma forma que la etiqueta canónica
   `dispatch-disposition` de PD-21). El paquete rendido por el orquestador fija
   además la superficie exacta a ejercer sin `--stage`, así que se invoca sin
   `--stage` y se asevera la etiqueta canónica. Ambigüedad declarada.
2. **El paquete de la entrega tardía es un paquete `prepared` de la ejecución
   cerrada.** PD-13 reemplaza la precondición «el paquete activo está
   `dispatched`» por «el paquete pertenece a su ejecución» (no exige
   `dispatched`), y el cierre legítimo de T3 (PD-8(a)) sólo exige recibo o
   disposición a los paquetes CON registro de despacho: un paquete despachado
   sin recibo bloquearía el cierre (contradiciendo PD-13), así que el paquete de
   la entrega tardía es el segundo paquete publicado (`prepared`) de la misma
   ejecución.
3. **La ausencia de recibo se asevera por el path del recibo durable**
   (`.cdad/runtime/results/<exec>/<packet>/receipt.json`), el mismo que resuelve
   `register-transition` (PD-13/§2.1).
4. **Sin cifras del state vivo.** PD-17 se verifica con `validate-state` rc=0
   antes y después sobre el state del FIXTURE (nunca el del repo): ninguna
   aserción sobre porcentajes ni conteos del state vivo.
5. **Mitad «árbol» de INV-7:** como declararon los RED de T1/T2/T3/T5, se asevera
   el **state byte a byte idéntico** en los rechazos; el snapshot completo del
   árbol no se asevera.
6. **Las salidas legítimas ofrecidas por un rechazo** (T3) no se juzgan aquí: T4
   sólo asevera los marcadores de dominio de sus propias causas.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER,
    FEATURE_ID,
    RECEIPT_NAME,
    EVIDENCE_MISSING,
    STATE_INCOHERENT,
    TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture,
    assert_unchanged,
    entries,
    last_entry,
    last_entry_with,
)
from test_005_012_t3_closure_dispatch_resolution import (
    CLOSURE_BYTES,
    CLOSURE_REL,
    CLOSURE_STAGE,
    FEATURE_CLOSED,
    IDLE,
    _feature_entry,
    assert_validate_green,
    names_path,
)

# La clase de la entrega tardía y su etiqueta canónica (PD-13: `stage:
# "late-delivery"`; §2.2 la escribe la operación, no hace falta `--stage`).
LATE_TRANSITION = "late-delivery"
LATE_STAGE = "late-delivery"

# El recibo durable de la entrega tardía conserva el esquema de la máquina de
# recibos y su `semantic_status` SIEMPRE `pending` (PD-13/INV-2).
SEMANTIC_PENDING = "pending"

# La entrega tardía: partes staged bajo el buzón `.cdad/inbox` (forma de
# `tests/test_003_002_t1_receive.py`), sintéticas y anónimas.
LATE_REPORT_BYTES = (
    b"# Role report (fixture demo-100, entrega tardia)\n"
    b"Evidencia mecanica de la entrega que llego despues del cierre.\n"
)
BASELINE_REF = "demo-baseline"
BASELINE_SHA256 = "0" * 64

# Claves que NO pueden aparecer en la entrada de una recepción: el juicio no se
# escribe (PD-18) y recibir nunca aprueba (PD-4/INV-9).
NO_JUDGEMENT_FIELDS = (
    "verdict", "disposition", "criterion", "review_path", "review_sha256",
    "approved_by", "contract_path", "contract_sha256", "plan_path",
    "plan_sha256",
)


# ---------------------------------------------------------------- helpers


def _late_entries(state: dict) -> list[dict]:
    """Las entradas de la entrega tardía (por su clase)."""
    return [e for e in entries(state) if e.get("transition") == LATE_TRANSITION]


def _snapshot_without_trace(state: dict) -> dict:
    """El state SIN la traza append-only ni `last_updated`.

    PD-13 (2): la única diferencia que la entrega tardía produce es el append de
    su entrada de `stage_history` (más `last_updated`).
    """
    return {
        key: value for key, value in state.items()
        if key not in ("stage_history", "last_updated")
    }


def _state_sha256(fx: _BaseFixture) -> str:
    return hashlib.sha256(fx.state_bytes()).hexdigest()


# ---------------------------------------------------------------- fixture


class _LateFixture(_BaseFixture):
    """Proyecto descartable con la feature CERRADA por el camino legítimo y un
    paquete de su ejecución SIN recibo durable (el objetivo de la entrega
    tardía).

    Construcción (todo por el camino legítimo del CLI, comportamiento
    EXISTENTE — se asertan como precondiciones):

      1. packet1 `dispatched` + recibo durable (fixture base `ready`);
      2. `register-transition --transition delivery` (T1) → packet1 `completed`;
      3. `prepare` publica un SEGUNDO paquete de la MISMA ejecución, que queda
         `prepared` (SIN registro de despacho): PD-8(a) sólo exige recibo o
         disposición a los paquetes CON registro de despacho, así que el cierre
         legítimo (T3) queda verde;
      4. el cierre citado se materializa y `register-transition --transition
         closure` (T3) cierra la feature: queda `done` (con `closed_at` y
         `closure_evidence`), `active_feature: null` y `current_stage: "idle"`;
      5. la entrega tardía del packet2 se staged en el buzón `.cdad/inbox`.
    """

    def __init__(self, base: Path, *, closed: bool = True) -> None:
        super().__init__(base, mode="ready")
        delivered = self.delivery()
        assert delivered.returncode == 0, (
            "precondición (fixture, comportamiento existente T1): la entrega "
            "del primer paquete debe registrarse (rc=0): "
            f"{delivered.stdout!r} {delivered.stderr!r}")
        self.packet1 = self.packet_id

        published = self.run_packet(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="segundo encargo demo-100 (entrega tardía)"))
        assert published.returncode == 0, (
            "precondición (fixture, comportamiento existente): con el primer "
            "paquete terminal, un segundo `prepare` publica el paquete "
            f"siguiente (rc=0): {published.stdout!r} {published.stderr!r}")
        second = (self.read_state().get("active_packet") or {}).get("id")
        assert second and second != self.packet1, (
            "precondición (fixture): el segundo paquete debe ser distinto del "
            f"primero ({self.packet1!r}): {second!r}")
        self.packet2 = second
        self.packet_id = second

        self.closure_file = self.root / CLOSURE_REL
        self.closure_file.parent.mkdir(parents=True, exist_ok=True)
        self.closure_file.write_bytes(CLOSURE_BYTES)

        if closed:
            closed_proc = self.closure()
            assert closed_proc.returncode == 0, (
                "precondición (fixture, comportamiento existente T3): el cierre "
                "legítimo de la feature debe aplicarse (rc=0); PD-8(a) sólo "
                "exige recibo o disposición a los paquetes con registro de "
                "despacho y PD-8(b) está verde con el pin del fixture: "
                f"{closed_proc.stdout!r} {closed_proc.stderr!r}")
            state = self.read_state()
            assert (_feature_entry(state, FEATURE_ID) or {}).get(
                "status") == FEATURE_CLOSED, (
                "precondición (fixture): la feature debe quedar "
                f"{FEATURE_CLOSED!r}: {_feature_entry(state, FEATURE_ID)!r}")
            assert state.get("active_feature") is None, (
                "precondición (fixture): `active_feature` debe quedar null tras "
                f"el cierre: {state.get('active_feature')!r}")
            assert state.get("current_stage") == IDLE, (
                "precondición (fixture): `current_stage` debe quedar "
                f"{IDLE!r} tras el cierre: {state.get('current_stage')!r}")

        self._stage_late_delivery()

    # -- construcción adicional (interfaz pública del CLI) ----------------

    def _stage_late_delivery(self) -> None:
        """Staged de la entrega tardía bajo `.cdad/inbox` (forma del focal de
        `receive` de 003-002) y del descriptor `RESULT.json` del packet2."""
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "role-report.md").write_bytes(LATE_REPORT_BYTES)
        (inbox / "changes.json").write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": BASELINE_REF,
            "baseline_sha256": BASELINE_SHA256,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.descriptor = inbox / "RESULT.json"
        self.descriptor.write_text(json.dumps({
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet2,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [{
                "name": "role-report",
                "artifact_kind": "test-writer-role-report",
                "staged_path": ".cdad/inbox/role-report.md",
            }],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "manifest_path": ".cdad/inbox/changes.json",
            },
            "run_evidence_ref": None,
        }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        self.packet_md = (self.root / ".cdad" / "packets" / self.packet2
                          / "PACKET.md")
        self.request_json = (self.root / ".cdad" / "packets" / self.packet2
                             / "REQUEST.json")
        assert self.packet_md.is_file() and self.request_json.is_file(), (
            "precondición (fixture): el paquete del fixture debe estar "
            "publicado bajo `.cdad/packets/`")

    # -- invocación (caja negra) ------------------------------------------

    def receive_argv(self) -> list[str]:
        """La superficie de `receive`: el modo `--late` se agrega aparte
        (§2.1 / ficha T4)."""
        return [
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(
                self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json"),
            "--packet", str(self.packet_md),
            "--request", str(self.request_json),
            "--descriptor", str(self.descriptor),
        ]

    def receive_normal(self) -> subprocess.CompletedProcess:
        return self.run_result(*self.receive_argv())

    def receive_late(self) -> subprocess.CompletedProcess:
        return self.run_result(*self.receive_argv(), "--late")

    def closure(self) -> subprocess.CompletedProcess:
        """El cierre legítimo de T3 (comportamiento EXISTENTE): la feature
        activa se cierra con su documento citado materializado."""
        return self.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)

    def late_delivery(self, *extra: str) -> subprocess.CompletedProcess:
        """La clase `late-delivery`: la entrega tardía de la feature cerrada
        (sin `--stage`: §2.2/PD-13 fijan la etiqueta canónica)."""
        return self.register_transition(
            "--transition", LATE_TRANSITION, "--feature", FEATURE_ID,
            "--packet", self.packet2, *extra)

    # -- observación ------------------------------------------------------

    def receipt_path_for(self, packet_id: str) -> Path:
        return (self.root / ".cdad" / "runtime" / "results" / self.execution_id
                / packet_id / RECEIPT_NAME)


@pytest.fixture
def closed_fx(tmp_path: Path) -> _LateFixture:
    """Feature cerrada por el camino legítimo + entrega tardía staged."""
    return _LateFixture(tmp_path, closed=True)


# ---------------------------------------------------------------- PD-13 (1)


def test_pd13_receive_late_persists_durable_receipt_and_normal_receive_stays_closed(
        closed_fx: _LateFixture) -> None:
    """PD-13 (1) + INV-2, caso 1: con la feature CERRADA por el camino legítimo
    y una entrega staged en el buzón `.cdad/inbox`, `receive --late` → rc=0 y
    recibo durable bajo el root de resultados con `semantic_status: "pending"`;
    el `receive` NORMAL (sin `--late`) sobre la MISMA feature cerrada SIGUE
    fallando cerrado (la única precondición que el modo tardío invierte es la de
    vigencia, no se relajó nada más) y no deja recibo. El `receive --late` NO
    escribe el state (INV-2: la máquina de recibos no aprueba ni transiciona).

    Aislamiento de causas: la feature está cerrada (precondición del modo
    tardío), el paquete pertenece a su ejecución y la entrega está staged; la
    ÚNICA diferencia entre el `receive` que falla y el que prospera es `--late`.

    RED hoy: `receive` no acepta `--late` (rc=2 «unrecognized arguments:
    --late») → falla la aserción de contrato (rc=0 + recibo durable).
    """
    assert closed_fx.receipt_path_for(closed_fx.packet2).exists() is False, (
        "precondición (fixture): el paquete de la entrega tardía NO tiene "
        "recibo durable")
    assert closed_fx.descriptor.is_file(), (
        "precondición (fixture): la entrega está staged en el buzón")
    assert_validate_green(closed_fx, "caso 1 (state cerrado antes de recibir)")
    state_before = closed_fx.state_bytes()

    normal = closed_fx.receive_normal()
    out_normal = normal.stdout + normal.stderr
    assert normal.returncode != 0, (
        "PD-13 violada: el `receive` NORMAL sobre una feature CERRADA debe "
        "seguir fallando cerrado (el modo tardío no relaja esa precondición); "
        f"rc={normal.returncode}: {out_normal!r}")
    assert closed_fx.receipt_path_for(closed_fx.packet2).exists() is False, (
        "PD-13 violada: el `receive` NORMAL rechazado sobre la feature cerrada "
        "no debe dejar recibo durable")

    late = closed_fx.receive_late()
    out_late = late.stdout + late.stderr

    assert late.returncode == 0, (
        "PD-13 violada (1): `receive --late` sobre la feature CERRADA debe "
        "persistir el recibo durable (rc=0); hoy rc="
        f"{late.returncode}: {out_late!r}")
    receipt_path = closed_fx.receipt_path_for(closed_fx.packet2)
    assert receipt_path.is_file(), (
        "PD-13 violada (1): el modo tardío debe dejar el recibo durable bajo el "
        f"root de resultados ({receipt_path})")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt.get("semantic_status") == SEMANTIC_PENDING, (
        "PD-13/INV-2 violada (1): el recibo tardío conserva el esquema de la "
        "máquina de recibos y su `semantic_status` SIEMPRE `pending`: "
        f"{receipt.get('semantic_status')!r}")
    assert receipt.get("packet_id") == closed_fx.packet2, (
        "PD-13 violada (1): el recibo durable debe ligar el paquete de la "
        f"entrega tardía ({closed_fx.packet2!r}): {receipt.get('packet_id')!r}")
    assert receipt.get("execution_id") == closed_fx.execution_id, (
        "PD-13 violada (1): el recibo durable debe ligar la ejecución de la "
        f"feature cerrada ({closed_fx.execution_id!r}): "
        f"{receipt.get('execution_id')!r}")
    assert receipt.get("feature_id") == FEATURE_ID, (
        "PD-13 violada (1): el recibo durable debe ligar la feature cerrada "
        f"({FEATURE_ID!r}): {receipt.get('feature_id')!r}")
    assert closed_fx.state_bytes() == state_before, (
        "INV-2/PD-13 violada (1): el `receive --late` NO escribe el state (la "
        "máquina de recibos no transiciona ni aprueba): el state cambió")


# ---------------------------------------------------------------- PD-13 (2)


def test_pd13_late_delivery_leaves_durable_trace_without_reopening_or_approving(
        closed_fx: _LateFixture) -> None:
    """PD-13 (2) + INV-9 + PD-17, caso 2: con el recibo durable presente,
    `--transition late-delivery --feature <closed-feature> --packet <id>` →
    rc=0 y el state queda:
      * la feature SIN cambio de estado: `epic_features[<feat>].status` sigue
        `done`, y `closed_at`, `active_feature` (null/idle) y `current_stage`
        (idle) NO cambian;
      * NINGUNA aprobación nueva (`approval_effect: false`, sin `approved_by`);
      * traza durable: UNA entrada de `stage_history` con `stage:
        "late-delivery"` y `transition: "late-delivery"` que nombra el paquete;
      * la única diferencia del state (sha256 antes/después) es el append de la
        traza (más `last_updated`);
      * `validate-state` rc=0 antes y después (PD-17).

    RED hoy: `register-transition` no acepta `--transition late-delivery` (rc=2
    «invalid choice») → falla la primera aserción de contrato.
    """
    received = closed_fx.receive_late()
    assert received.returncode == 0, (
        "PD-13 violada (1): el recibo durable de la entrega tardía debe "
        f"existir para poder registrar la traza (rc=0); rc="
        f"{received.returncode}: {received.stdout!r} {received.stderr!r}")
    before_state = closed_fx.read_state()
    before_entries = entries(before_state)
    before_feature = _feature_entry(before_state, FEATURE_ID)
    before_sha = _state_sha256(closed_fx)
    assert_validate_green(closed_fx, "caso 2 (antes del late-delivery)")

    proc = closed_fx.late_delivery()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-13 violada (2): `--transition late-delivery` con el recibo durable "
        "y la feature cerrada debe registrarse (rc=0); hoy rc="
        f"{proc.returncode}: {out!r}")

    after_state = closed_fx.read_state()
    entry = last_entry_with(after_state, transition=LATE_TRANSITION)
    assert entry is not None and entry is entries(after_state)[-1], (
        "PD-13 violada (2): la traza durable debe ser UNA entrada de "
        f"`stage_history` con `transition: \"{LATE_TRANSITION}\"`: "
        f"{entries(after_state)[-2:]!r}")
    assert entry.get("stage") == LATE_STAGE, (
        "PD-13 violada (2): la entrada debe llevar la etiqueta canónica "
        f"`stage: \"{LATE_STAGE}\"`: {entry!r}")
    assert entry.get("packet_id") == closed_fx.packet2, (
        "PD-13 violada (2): la traza debe NOMBRAR el paquete de la entrega "
        f"tardía ({closed_fx.packet2!r}): {entry.get('packet_id')!r}")
    assert entry.get("approval_effect") is False, (
        "PD-13 violada (2): la entrega tardía NO aprueba nada "
        f"(`approval_effect: false`): {entry.get('approval_effect')!r}")
    assert not entry.get("approved_by"), (
        "PD-13 violada (2): la entrada de `late-delivery` NO lleva "
        f"`approved_by` (no hay aprobación nueva): {entry.get('approved_by')!r}")

    after_feature = _feature_entry(after_state, FEATURE_ID)
    assert (after_feature or {}).get("status") == FEATURE_CLOSED, (
        "PD-13 violada (2): la entrega tardía NO reabre la feature; "
        f"`epic_features[].status` sigue {FEATURE_CLOSED!r}: {after_feature!r}")
    assert after_feature == before_feature, (
        "PD-13 violada (2): la entrega tardía NO toca la entrada de la feature "
        f"(`status`/`closed_at`/`closure_evidence` sin cambios): "
        f"{before_feature!r} → {after_feature!r}")
    assert after_state.get("active_feature") == before_state.get("active_feature"), (
        "PD-13 violada (2): `active_feature` NO cambia (sigue null/idle): "
        f"{before_state.get('active_feature')!r} → "
        f"{after_state.get('active_feature')!r}")
    assert after_state.get("active_feature") is None, (
        "PD-13 violada (2): con la feature cerrada `active_feature` es null: "
        f"{after_state.get('active_feature')!r}")
    assert after_state.get("current_stage") == before_state.get("current_stage"), (
        "PD-13 violada (2): `current_stage` NO cambia: "
        f"{before_state.get('current_stage')!r} → "
        f"{after_state.get('current_stage')!r}")
    assert after_state.get("current_stage") == IDLE, (
        f"PD-13 violada (2): el reposo sigue {IDLE!r}: "
        f"{after_state.get('current_stage')!r}")

    assert len(entries(after_state)) == len(before_entries) + 1, (
        "PD-13 violada (2): la entrega tardía deja UNA entrada nueva de traza "
        f"(antes {len(before_entries)}, después {len(entries(after_state))})")
    assert entries(after_state)[:len(before_entries)] == before_entries, (
        "PD-13/INV-3 violada (2): la historia previa no debe reescribirse "
        "(append-only)")
    assert _snapshot_without_trace(after_state) == (
        _snapshot_without_trace(before_state)), (
        "PD-13/INV-9 violada (2): la única diferencia del state debe ser el "
        "append de la traza (más `last_updated`); un campo de la feature o del "
        "reposo cambió")
    assert _state_sha256(closed_fx) != before_sha, (
        "PD-13 violada (2): el state debe cambiar (el append de la traza)")

    assert_validate_green(closed_fx, "caso 2 (después del late-delivery)")


# ---------------------------------------------------------------- PD-13 (rechazos)


def test_pd13_late_delivery_with_open_feature_fails_closed_state_incoherent(
        tmp_path: Path) -> None:
    """PD-13 (rechazo) + INV-7, caso 3(a): con la feature ABIERTA, la salida
    tardía NO aplica (es SÓLO para lo cerrado; el camino normal es `receive` +
    `delivery` y, para un despacho que no vuelve, `disposition`) → rc=2, marcador
    `state incoherent`, sin efectos (state byte a byte idéntico).

    Aislamiento de causas: el fixture base `ready` tiene la feature ABIERTA, el
    paquete `dispatched` CON recibo durable y perteneciente a la ejecución
    activa; la ÚNICA causa posible del rechazo es la feature abierta.

    RED hoy: rc=2 por error de uso («invalid choice: 'late-delivery'») → falla
    la aserción del marcador.
    """
    fixture = _BaseFixture(tmp_path, mode="ready")
    assert fixture.receipt_path().is_file(), (
        "precondición (fixture): el paquete citado TIENE recibo durable "
        "(aislamiento: no es la causa del rechazo)")
    state = fixture.read_state()
    assert (_feature_entry(state, FEATURE_ID) or {}).get("status") != (
        FEATURE_CLOSED), (
        "precondición (fixture): la feature está ABIERTA")
    assert state["active_packet"]["status"] == "dispatched", (
        "precondición (fixture): hay ejecución activa con el paquete "
        "`dispatched`")
    before = fixture.state_bytes()

    proc = fixture.register_transition(
        "--transition", LATE_TRANSITION, "--feature", FEATURE_ID,
        "--packet", fixture.packet_id)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-13 violada (3a): la entrega tardía con la feature ABIERTA debe "
        f"fallar cerrado (rc=2); hoy rc={proc.returncode}: {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-13 violada (3a): el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert not _late_entries(fixture.read_state()), (
        "PD-13 violada (3a): el rechazo no debe dejar entrada de "
        "`late-delivery`")
    assert_unchanged(fixture, before, "PD-13", "3a (feature abierta)")


def test_pd13_late_delivery_without_durable_receipt_fails_closed_evidence_missing(
        closed_fx: _LateFixture) -> None:
    """PD-13 (rechazo) + reparto de marcadores + INV-7, caso 3(b): con la
    feature CERRADA pero SIN recibo durable para el paquete citado → rc=2,
    marcador `evidence missing`, diagnóstico que NOMBRA el paquete y el recibo
    faltante, sin efectos (state byte a byte idéntico).

    Aislamiento de causas: la feature está CERRADA (la precondición de vigencia
    del modo tardío se cumple) y el paquete pertenece a su ejecución; la ÚNICA
    causa del rechazo es la evidencia ausente (no se corrió `receive --late`).

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    assert closed_fx.receipt_path_for(closed_fx.packet2).exists() is False, (
        "precondición (fixture): NO hay recibo durable para el paquete de la "
        "entrega tardía")
    assert (_feature_entry(closed_fx.read_state(), FEATURE_ID) or {}).get(
        "status") == FEATURE_CLOSED, (
        "precondición (fixture): la feature está cerrada (la vigencia no es la "
        "causa)")
    before = closed_fx.state_bytes()

    proc = closed_fx.late_delivery()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-13 violada (3b): la entrega tardía sin recibo durable debe fallar "
        f"cerrado (rc=2); hoy rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-13 violada (3b): el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}» (reparto por condición: sin recibo → evidencia "
        f"faltante): {out!r}")
    assert closed_fx.packet2 in out, (
        "PD-13 violada (3b): el diagnóstico debe NOMBRAR el paquete sin recibo "
        f"({closed_fx.packet2!r}): {out!r}")
    assert RECEIPT_NAME in out, (
        "PD-13 violada (3b): el diagnóstico debe nombrar la evidencia faltante "
        f"({RECEIPT_NAME!r}): {out!r}")
    assert not _late_entries(closed_fx.read_state()), (
        "PD-13 violada (3b): el rechazo no debe dejar entrada de "
        "`late-delivery`")
    assert_unchanged(closed_fx, before, "PD-13", "3b (sin recibo durable)")


# ---------------------------------------------------------------- PD-4 re-aplicado


def test_pd4_late_delivery_entry_has_no_approval_or_judgement_fields_and_prepare_stays_closed(
        closed_fx: _LateFixture) -> None:
    """PD-4 (re-aplicado) + PD-18 + INV-9 + PD-13, caso 4: la entrada de
    `late-delivery` NO lleva `approved_by`, pin de contrato/plan, `verdict`,
    `disposition`, `criterion`, `review_path` ni `review_sha256` (recibir una
    entrega nunca aprueba, ni siquiera tarde); y con la feature cerrada, un
    `prepare --role test-writer` posterior SIGUE fallando cerrado (la entrega
    tardía no reabre el ciclo ni habilita roles) sin publicar paquete.

    RED hoy: `late-delivery` no existe (rc=2 «invalid choice») → falla la
    primera aserción de contrato (la traza registrada). La mitad «prepare sigue
    cerrado» ya se satisface con el comportamiento de hoy (declarado).
    """
    received = closed_fx.receive_late()
    assert received.returncode == 0, (
        "PD-13 violada (1): recibo durable de la entrega tardía (rc=0); "
        f"rc={received.returncode}: {received.stdout!r} {received.stderr!r}")

    proc = closed_fx.late_delivery()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PD-4 violada: la entrega tardía debe registrarse (rc=0) para evaluar "
        f"que no aprueba; hoy rc={proc.returncode}: {out!r}")

    state = closed_fx.read_state()
    entry = last_entry_with(state, transition=LATE_TRANSITION)
    assert entry is not None, (
        "PD-4 violada: no hay entrada de `late-delivery` en `stage_history`")
    for field in NO_JUDGEMENT_FIELDS:
        assert field not in entry, (
            "PD-4/PD-18 violada: la entrada de `late-delivery` registra una "
            "entrega (no una aprobación) y no escribe juicio; no debe llevar "
            f"{field!r}: {entry!r}")

    # Control: tras la entrega tardía, con la feature cerrada, `prepare` sigue
    # fallando cerrado y no publica un paquete nuevo.
    entries_before = len(entries(state))
    before_packet = state.get("active_packet")
    control = closed_fx.run_packet(*prepare_args(
        closed_fx.root, role="test-writer", substage="red",
        objective="control PD-4 (feature cerrada tras la entrega tardía)"))
    out_control = control.stdout + control.stderr
    assert control.returncode != 0, (
        "PD-13/PD-4 violada (control): con la feature CERRADA, un `prepare` "
        "posterior a la entrega tardía debe SEGUIR fallando cerrado (la "
        f"entrega tardía no reabre el ciclo): {out_control!r}")
    after_state = closed_fx.read_state()
    assert after_state.get("active_packet") == before_packet, (
        "PD-13 violada (control): el `prepare` rechazado no debe publicar un "
        f"paquete nuevo: {before_packet!r} → "
        f"{after_state.get('active_packet')!r}")
    assert len(entries(after_state)) == entries_before, (
        "PD-13 violada (control): el `prepare` rechazado no debe escribir la "
        "traza")


# ---------------------------------------------------------------- PD-10 / PD-11


def test_pd10_pd11_late_delivery_entry_has_transition_key_and_identical_repetition_is_noop(
        closed_fx: _LateFixture) -> None:
    """PD-10 + PD-11 (+ PD-13 condición 3), caso 5: la entrada de
    `late-delivery` lleva `transition_key` —clave nueva y aditiva, derivada
    como sha256 de la identidad de la transición—; y repetir la invocación
    IDÉNTICA → rc=0, SIN segunda entrada de `stage_history`, con el state byte a
    byte idéntico y una salida que nombra la entrada existente.

    RED hoy: `late-delivery` no existe (rc=2 «invalid choice») → falla la
    primera aserción de contrato.
    """
    received = closed_fx.receive_late()
    assert received.returncode == 0, (
        "PD-13 violada (1): recibo durable de la entrega tardía (rc=0); "
        f"rc={received.returncode}: {received.stdout!r} {received.stderr!r}")

    first = closed_fx.late_delivery()
    assert first.returncode == 0, (
        "PD-10 violada: la entrega tardía debe registrarse (rc=0) para llevar "
        f"su clave de identidad; hoy rc={first.returncode}: {first.stdout!r} "
        f"{first.stderr!r}")
    state_after_first = closed_fx.state_bytes()
    count_after_first = len(entries(closed_fx.read_state()))
    entry = last_entry(closed_fx.read_state())
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        "PD-10 violada: la entrada de `late-delivery` debe llevar "
        f"`transition_key` (clave nueva y aditiva): {key!r}")

    second = closed_fx.late_delivery()

    assert second.returncode == 0, (
        "PD-11 violada: repetir la invocación IDÉNTICA de la entrega tardía "
        f"debe ser un no-op exitoso (rc=0); rc={second.returncode}: "
        f"{second.stdout!r} {second.stderr!r}")
    assert len(entries(closed_fx.read_state())) == count_after_first, (
        "PD-11 violada: la repetición idéntica NO debe agregar una segunda "
        f"entrada de `stage_history` (sigue habiendo {count_after_first})")
    assert closed_fx.state_bytes() == state_after_first, (
        "PD-11 violada: el state tras la repetición idéntica debe ser byte a "
        "byte idéntico al de la primera invocación")
    assert key and key in (second.stdout + second.stderr), (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key!r}): {second.stdout!r} {second.stderr!r}")


# ---------------------------------------------------------------- PD-17


def test_pd17_validate_state_stays_green_across_the_late_delivery(
        closed_fx: _LateFixture) -> None:
    """PD-17 (+ PD-13, + PD-20), caso 6: `validate-state` rc=0 ANTES de la
    operación, tras el `receive --late` y tras el `late-delivery` — la
    operación y sus validaciones no exigen ningún campo a las entradas
    existentes y el state resultante sigue siendo coherente (reposo `idle`). El
    oráculo es `validate-state rc=0`; SIN porcentajes ni conteos del state vivo
    del repo (el state auditado es el del FIXTURE).

    RED hoy: `receive --late` no existe → falla la primera aserción de contrato
    (el rc=0 del modo tardío con el reposo vigente).
    """
    assert_validate_green(closed_fx, "caso 6 (antes del receive --late)")

    late = closed_fx.receive_late()
    assert late.returncode == 0, (
        "PD-17 violada: el `receive --late` debe prosperar sobre el reposo "
        f"coherente (rc=0); hoy rc={late.returncode}: {late.stdout!r} "
        f"{late.stderr!r}")
    assert_validate_green(closed_fx, "caso 6 (tras el receive --late)")

    proc = closed_fx.late_delivery()
    assert proc.returncode == 0, (
        "PD-17 violada: el `late-delivery` debe aplicarse (rc=0); hoy rc="
        f"{proc.returncode}: {proc.stdout!r} {proc.stderr!r}")
    after_out = assert_validate_green(
        closed_fx, "caso 6 (tras el late-delivery)")
    assert IDLE in after_out, (
        "PD-17 violada: el state tras la entrega tardía debe seguir "
        f"aceptándose por la vía de reposo (token {IDLE!r}): {after_out!r}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
