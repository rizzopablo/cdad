#!/usr/bin/env python3
"""005-012 T3 RED — la clase `closure` (comprobación ANTES de aplicar: entregas
requeridas + aprobación vigente) y la clase `disposition` (la salida del
despacho que NUNCA vuelve, B1), con la feature ABIERTA.

Contract:
- docs/specs/005-012-transition-registration/spec.md §1 (el caso real 005-011 y
  el caso B1: el run que no vuelve), §2.1 (superficie CLI de `closure` y
  `disposition`), §2.2 (forma aditiva del registro y efecto de cada clase),
  §2.3 (postcondiciones **PD-8**, **PD-9**, **PD-21**; soporte PD-11/PD-12(iv)/
  PD-17/PD-20), §2.4 (invariantes INV-3, INV-7, INV-9), §3 (frontera del
  juicio), §4 (AC-4, el caso B1), §5 D-4/D-13/D-14.
- docs/specs/005-012-transition-registration/plan.md §4 ficha T3 (test focal
  declarado `tests/test_005_012_t3_closure_dispatch_resolution.py`) + bloque
  canónico `plan-tasks` (T3) rendido por el paquete.

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo de implementación NUNCA se importa y su código NUNCA se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition closure --stage <token> \\
        --approve-by <texto> --closure-path <p> [--closure-sha256 <hex>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition disposition --packet <packet-id> \\
        --resolution <abandoned|superseded> [--replaced-by <packet-id>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>

HOY el subcomando `register-transition` existe (T1 GREEN: `delivery`/`advance`;
T2 GREEN: `gate`; T5 GREEN: `supersedes` + lector aditivo) pero las clases
`closure` y `disposition` NO: el CLI responde con un error de uso (rc=2,
«invalid choice: 'closure'» / «'disposition'») y ningún efecto sobre el state.
Por eso cada test falla en la ASERCIÓN sobre el comportamiento del contrato
(efecto sobre el state, marcador del rechazo, diagnóstico que nombra el hecho,
oferta de las salidas legítimas, bytes del state), nunca en la invocación ni en
una precondición de fixture: los fallos RED son AssertionError de contrato,
jamás ImportError, SyntaxError, JSONDecodeError ni error de setup. En los casos
de rechazo la aserción discriminante es el **marcador** (un error de uso de
argparse también da rc=2; los marcadores de dominio no).

REVIEW-FIX B1 (paquete `005-012-transition-registration-test-writer-red-009`).
La review formal única (`review.md` §1 B1) encontró que PD-6 cubre **`gate` Y
`closure`** —«`gate` y `closure` exigen `--approve-by` no vacío… Una delegación
revocada o vencida → rc=2, marcador `approval pending`»—, pero la implementación
consumía el control de autoridad **sólo** en la clase `gate`: un `closure` bajo
delegación revocada o vencida **prosperaba** (rc=0, escribía `approved_by` y
marcaba la feature `done`). Los casos `test_b1_pd6_*` son el RED de esa
postcondición sobre `closure`, con el fixture LISTO PARA CERRAR (las dos
comprobaciones de PD-8 verdes) para que la ÚNICA causa del rechazo sea la
autoridad; y el control positivo `test_pd6_case_c_*` conserva que sin delegación
el dueño NO se bloquea (P2/D-10). El `closure` legítimo (delegación vigente +
PD-8 verde) sigue cubierto por `test_pd9_*`, que no se toca.

Fixture: proyecto descartable en un tempdir (política válida, contrato pineado
en `stage_history`, delegación HITL vigente con `source` resoluble, ejecución v2
y paquete(s) reales) construido por el camino legítimo del CLI (`prepare` →
`prepare --record-dispatch` → `cdad_result.py receive` → `register-transition
--transition delivery`), con el `HOME` del subproceso en un tempdir VACÍO
(nunca el HOME real, nunca este repo). Los ids del fixture son sintéticos y
anónimos. Se reutilizan el patrón y los helpers de los focales T1/T2/T5
(`tests/test_005_012_t1_register_transition_base.py`: fixture base,
`entries`/`last_entry_with`/`assert_unchanged`; T2: subclase de fixture con
helpers de invocación; T5: mutaciones declaradas de `stage_history`).

Aislamiento de causas (declarado, como exige el encargo): el cierre exige que
(a) cada paquete despachado de la ejecución activa tenga recibo durable **o**
disposición y (b) exista una aprobación `specification` **vigente** cuyo pin
nombre el contrato. Cada caso arma el fixture para que la ÚNICA causa del
rechazo sea la que quiere probar:

  * PD-8(a): el fixture `double` tiene **dos** paquetes despachados de la
    ejecución activa — el primero CON recibo durable (y entregado, T1) y el
    segundo SIN recibo (el caso B1: el run que no volvió) — y la aprobación
    vigente con el pin correcto. La única entrega sin resolver es la segunda.
  * PD-8(b): el fixture `ready` tiene TODAS las entregas satisfechas (el único
    paquete despachado tiene recibo); la única causa es la aprobación (falta, o
    el pin no nombra los bytes actuales del contrato).
  * PD-21 (rechazos): el fixture `single` tiene el paquete despachado SIN
    recibo y la aprobación vigente; cada variante incumple UNA condición de la
    disposición (paquete ajeno, no despachado, con recibo, feature cerrada).

Mapeo test → postcondición (y caso mínimo del encargo):

  test_pd8a_closure_with_unreceipted_dispatch_fails_closed_naming_evidence
      -> PD-8(a) + INV-7. Caso **1**: con un paquete de la ejecución activa con
         registro de despacho y SIN recibo durable → `closure` rc=2, marcador
         `evidence missing`, nombrando el `<packet_id>` y el recibo faltante, y
         ofreciendo las DOS salidas legítimas (recibir / disponer; `late-delivery`
         ya no se ofrece: es de feature cerrada, B1); state byte a byte idéntico
         (PD-8 comprueba ANTES de cualquier escritura).
  test_pd8b_closure_without_vigent_specification_pin_fails_closed
      -> PD-8(b) + INV-7. Caso **2**, dos variantes: (a) sin ninguna entrada
         `specification` de la feature; (b) con la entrada cuyo pin ya NO nombra
         los bytes actuales del contrato (digest divergente) → rc=2, marcador
         `approval pending`, nombrando la aprobación faltante, sin efectos.
  test_pd9_closure_applied_records_evidence_and_rests
      -> PD-9 (+ PD-20, + PD-17). Caso **3**: con las dos comprobaciones verdes →
         rc=0 y el state queda con la entrada de traza (`transition: "closure"`,
         `closure_path`/`closure_sha256` DERIVADO de los bytes, PD-20),
         `epic_features[<feat>].status: "done"` + `closed_at` +
         `closure_evidence{path, sha256}`, `active_feature: null`,
         `current_stage: "idle"`, `active_packet` null o terminal; el digest
         derivado se imprime; `validate-state` rc=0 ANTES y DESPUÉS (vía de
         reposo, token `idle`) y la historia previa queda intacta (append-only).
  test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest
      -> PD-21 (condición 1) + INV-9 (+ PD-10, + PD-17). Caso **4(a)**: con la
         feature ABIERTA y un despacho SIN recibo → `--transition disposition
         --packet <id> --resolution abandoned` rc=0; UNA entrada con
         `transition: "disposition"`, `stage: "dispatch-disposition"`,
         `resolution`, `approval_effect: false`, `transition_key`, SIN
         `approved_by`; y NINGÚN otro campo del state cambia salvo
         `stage_history`, `last_updated` y el **status del paquete identificado**
         (no fabrica un `completed` ni un recibo): el paquete pasa a `failed`
         —REEMPLAZO DECLARADO de A-1 de 006-005 U5, PD-19/D-4, enmienda
         aprobada por el dueño—, `epic_features`/`closed_at`/`active_feature`/
         `current_stage` intactos.
  test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances
      -> PD-21 (condición 2) + PD-8(a) + PD-9 + PD-17. Caso **4(b)** (el caso que
         la review del orquestador exigió): el cierre rechaza nombrando el
         despacho sin recibo → se registra la disposición → el cierre AVANZA
         (rc=0) y el reposo queda coherente (`validate-state` rc=0).
  test_pd21_superseded_disposition_records_replaced_by
      -> PD-21 (condición 1, resolución `superseded`) + PD-12. Caso **4(c)**:
         `--resolution superseded --replaced-by <packet-id>` → rc=0 y la entrada
         lleva `resolution`/`replaced_by`; el negativo (sin `--replaced-by`) →
         rc=2 sin efectos y sin ser un error de uso del CLI (la clase existe).
  test_pd21_disposition_rejections_fail_closed_state_incoherent
      -> PD-21 + PD-12(iv). Caso **5**: marcador `state incoherent`, nombrando el
         hecho y SIN efectos, en cuatro variantes — (i) paquete que NO pertenece
         a la ejecución activa, (ii) paquete NO `dispatched`, (iii) paquete que YA
         tiene recibo durable (la evidencia contradice la disposición: guarda que
         impide saltar una entrega que existe), (iv) feature CERRADA.
  test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends
      -> PD-11 + PD-21 (condición 3) + PD-12. Caso **6**: repetir la invocación
         idéntica → rc=0, sin segunda entrada, state byte a byte idéntico y salida
         que nombra la entrada existente; y una resolución DISTINTA
         (`abandoned` y luego `superseded`) es una transición distinta → entrada
         nueva (append).

Review-fix B1 (PD-6 aplicada a `closure`; spec PD-6 + review.md §1 B1):

  test_b1_pd6_revoked_delegation_fails_closed_approval_pending
      -> PD-6 (B1) + INV-7: con el fixture LISTO PARA CERRAR (PD-8 verde) y la
         delegación REVOCADA (`status: "revoked"` + `revoked_at`, la forma del
         focal de T2) → `closure` rc=2, marcador `approval pending`, nombrando
         el registro, y state byte a byte idéntico (nada de
         `epic_features[].status: "done"` ni `active_feature: null`).
  test_b1_pd6_expired_delegation_fails_closed_approval_pending
      -> PD-6 (B1) + INV-7: ídem con la delegación VENCIDA por `expires_on` ISO
         en el pasado (la forma de
         `test_pd6_case_b_expired_delegation_fails_closed_approval_pending`).
  test_pd6_case_c_closure_without_delegation_keeps_the_owner_unblocked
      -> PD-6 (caso C, P2/D-10) + PD-9: SIN registro `hitl_delegation` —y en la
         variante que PD-6 declara idéntica, además `active_epic: null`— el
         `closure` sigue rc=0: registra el aprobador DECLARADO y la salida
         declara que no hubo delegación que verificar (el dueño no se bloquea).

Interpretaciones y límites declarados (no se inventó oráculo ni se debilitó un
test; el contrato fue verificable y no hubo detención):

1. **La etiqueta de la clase `closure`.** §2.1 deja `--stage` como token plano
   libre; el informe de discovery (§4, tabla del ciclo: el script de cierre
   escribía `stage: "feature-closure"`) fija la etiqueta real, que es la que se
   usa y se asevera.
2. **Forma del path guardado (`closure_path`/`closure_evidence.path`).** PD-9
   exige que el `closure_evidence{path, sha256}` y la traza nombren el cierre
   citado; el contrato no fija si el path se guarda tal como se pasó o
   resuelto. `names_path()` acepta cualquiera de las dos formas y el oráculo
   fuerte es el **digest derivado de los bytes** (PD-20).
3. **`active_packet` al cerrar.** PD-9 lo declara `null` **o terminal**; el
   fixture puede dejarlo `dispatched` (sin `delivery`), así que la aserción
   acepta `null` o un status terminal (`completed`/`failed`) y no impone cuál.
4. **Marcador del negativo de `superseded` sin `--replaced-by`.** PD-21 declara
   que `--replaced-by` es OBLIGATORIO para `superseded`, pero no declara qué
   marcador lleva su ausencia (el vocabulario de PD-12 es por condición de
   estado/evidencia, no por argumento faltante). Por eso ese negativo asevera
   `rc=2` + **sin efectos** (INV-7), sin inventar marcador. Declarado.
5. **El caso «aprobación reemplazada» de PD-8(b).** Se cubre con las dos formas
   que el contrato hace observables: la aprobación **falta** (no hay entrada
   `specification` de la feature) o su pin **ya no nombra** los bytes actuales
   del contrato (digest divergente). La sustitución **estructural**
   (`supersedes`, PD-14/PD-15) NO es causa de `approval pending` de por sí: una
   segunda entrada con el pin correcto que sustituye a la primera deja a la
   nueva **vigente y habilitada** (y una nota en prosa sin `supersedes` no
   reemplaza nada, PD-15); ese comportamiento vive en el focal de T5.
6. **El negativo de `superseded` y el caso (iv) del rechazo** se arman sobre el
   state del fixture con las mutaciones declaradas por la suite (`epic_features
   status: "done"`, el vocabulario de `CLOSED_FEATURE_STATUSES` que el discovery
   enumera) y la forma de §2.2; ningún campo inventado.
7. **Sin cifras del state vivo.** PD-17 se verifica con `validate-state` rc=0
   antes y después sobre el state del FIXTURE (nunca el del repo): ninguna
   aserción sobre porcentajes ni conteos del state vivo.
8. **Mitad «árbol» de INV-7:** como declararon los RED de T1/T2/T5, se asevera el
   **state byte a byte idéntico**; el snapshot completo del árbol no se asevera.
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
    AUTHORITY_REF,
    CONTRACT_BYTES,
    CONTRACT_FILE,
    EPIC_ID,
    EVIDENCE_MISSING,
    FEATURE_ID,
    RECEIPT_NAME,
    STATE_INCOHERENT,
    APPROVAL_PENDING,
    TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture,
    assert_unchanged,
    entries,
    last_entry,
    last_entry_with,
)

# La clase `closure` es la DECISIÓN; `--stage` es la etiqueta (token plano
# libre). La etiqueta real del cierre del ciclo es «feature-closure»
# (discovery §4: el script de cierre escribía `stage: "feature-closure"`).
CLOSURE_STAGE = "feature-closure"
# La disposición usa la etiqueta CANÓNICA de §2.1 (no admite `--stage`).
DISPOSITION_STAGE = "dispatch-disposition"

# El cierre citado: path RELATIVO a la raíz del proyecto (misma convención que
# `--contract-path` en el focal T2) y sus bytes.
CLOSURE_REL = f"docs/specs/{FEATURE_ID}/closure.md"
CLOSURE_BYTES = b"# Closure fixture (demo-100 transition registration)\n"
# Bytes divergentes del contrato: la re-aprobación real cambia el contenido del
# mismo `contract_path`; con ellos el pin de la entrada ya no nombra el contrato.
CONTRACT_BYTES_DIVERGENT = (
    b"# Spec fixture (demo-100 transition registration, divergent bytes)\n")

# Resoluciones del vocabulario cerrado de PD-21.
RESOLUTION_ABANDONED = "abandoned"
RESOLUTION_SUPERSEDED = "superseded"

# Vocabulario de `active_packet.status` terminal (PD-9: «null o terminal»; el
# reposo de 005-001 PD-13 tolera `completed|failed`).
TERMINAL_PACKET_STATUSES = ("completed", "failed")

# Estado/token de feature CERRADA (PD-21: `CLOSED_FEATURE_STATUSES`, `done`).
FEATURE_CLOSED = "done"
IDLE = "idle"

# El paquete ajeno (ninguna ejecución del fixture lo conoce) y el intento del
# segundo despacho: ids sintéticos y anónimos del fixture.
FOREIGN_PACKET_ID = f"{FEATURE_ID}-test-writer-green-900"
ATTEMPT_SECOND = "attempt-demo-002"


# ---------------------------------------------------------------- helpers


def _feature_entry(state: dict, feature_id: str) -> dict | None:
    for entry in state.get("epic_features") or []:
        if entry.get("id") == feature_id:
            return entry
    return None


def _disposition_entries(state: dict) -> list[dict]:
    return [e for e in entries(state) if e.get("transition") == "disposition"]


def names_path(value: object, rel: str) -> bool:
    """El valor NOMBRA el archivo citado (la ruta tal como se pasó o resuelta).

    PD-9 no fija la normalización del path (relativo como se pasó, o absoluto);
    el oráculo fuerte del cierre es el digest derivado de sus bytes (PD-20).
    """
    if not isinstance(value, str) or not value:
        return False
    return value == rel or value.endswith(rel) or Path(value).name == Path(rel).name


def names_any(out: str, *tokens: str) -> bool:
    """El diagnóstico NOMBRA el hecho por al menos uno de sus nombres."""
    return any(token and token in out for token in tokens)


def assert_validate_green(fx: _BaseFixture, label: str) -> str:
    """PD-17: el oráculo es `validate-state` rc=0 (sin porcentajes ni conteos)."""
    proc = fx.validate_state()
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"PD-17 violada ({label}): `validate-state` debe dar rc=0: {out!r}")
    return out


class _ClosureFixture(_BaseFixture):
    """Proyecto descartable (capa legítima del CLI) para el cierre y la
    disposición.

    Modos:
      - `single`: UN paquete `dispatched` SIN recibo durable (el caso B1: el
        run que no volvió). Es la precondición mínima de PD-8(a)/PD-21.
      - `double`: DOS paquetes de la MISMA ejecución — el primero con recibo
        durable y ya entregado (T1) y el segundo `dispatched` sin recibo — de
        modo que la única entrega sin resolver sea la segunda, y el
        `--replaced-by` de la disposición `superseded` nombre un paquete REAL
        de la ejecución.
      - `ready`: UN paquete `dispatched` CON recibo durable y la aprobación
        `specification` vigente → las DOS comprobaciones de PD-8 verdes. Es la
        precondición del review-fix B1 (PD-6 sobre `closure`): la ÚNICA causa
        evaluada es la autoridad.

    La capa previa se produce por el camino legítimo del CLI (`prepare` →
    `--record-dispatch` → `receive` → `register-transition delivery`); el
    cierre citado se escribe con bytes conocidos (digest derivable).
    """

    def __init__(self, base: Path, mode: str = "single") -> None:
        assert mode in ("single", "double", "ready"), mode
        self.mode = mode
        super().__init__(
            base,
            mode="ready" if mode in ("double", "ready")
            else "dispatched_no_receipt")
        self.closure_file = self.root / CLOSURE_REL
        self.closure_file.parent.mkdir(parents=True, exist_ok=True)
        self.closure_file.write_bytes(CLOSURE_BYTES)
        if mode == "double":
            self.packet1: str = self.packet_id
            self.packet2: str | None = None
            delivered = self.delivery()
            assert delivered.returncode == 0, (
                "precondición (fixture, comportamiento existente T1): la "
                "entrega del primer paquete lo deja terminal (rc=0): "
                f"{delivered.stdout!r} {delivered.stderr!r}")
            self._second_dispatch()

    # -- construcción adicional (interfaz pública del CLI) ----------------

    def _second_dispatch(self) -> None:
        proc = self.run_packet(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="segundo encargo del fixture demo-100 (despacho sin recibo)"))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente): con el primer "
            "paquete terminal, un segundo `prepare` publica el paquete "
            f"siguiente (rc=0): {proc.stdout!r} {proc.stderr!r}")
        packet2 = (self.read_state().get("active_packet") or {}).get("id")
        assert packet2 and packet2 != self.packet1, (
            "precondición (fixture): el segundo paquete debe ser distinto del "
            f"primero ({self.packet1!r}): {packet2!r}")
        self.packet2 = packet2
        self.packet_id = packet2
        dispatched = self.dispatch(packet2, ATTEMPT_SECOND)
        assert dispatched.returncode == 0, (
            "precondición (fixture, comportamiento existente): el segundo "
            f"paquete queda `dispatched` (rc=0): {dispatched.stdout!r} "
            f"{dispatched.stderr!r}")
        assert self.read_state()["active_packet"]["status"] == "dispatched", (
            "precondición (fixture): el segundo paquete debe quedar `dispatched`")

    def dispatch(self, packet_id: str, attempt_id: str
                 ) -> subprocess.CompletedProcess:
        """Registra el despacho de un paquete (camino legítimo existente)."""
        observation = self.root / "docs" / f"observation-{attempt_id}.json"
        observation.write_text(json.dumps({
            "runtime": "demo-runtime",
            "model_configured": "demo-model",
            "model_reported": "demo-model",
            "session": "ses-demo-0002",
            "started_at": "2026-10-14T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return self.run_packet(
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", packet_id,
            "--attempt-id", attempt_id,
            "--input", str(observation))

    # -- mutaciones declaradas de la delegación (PD-6, review-fix B1) ------
    # La forma exacta del focal de T2 (`test_005_012_t2_gate_authority.py`):
    # la delegación revocada (`status: "revoked"` + `revoked_at`) y la vencida
    # por fecha (`expires_on` ISO en el pasado). Ningún campo inventado.

    def delegation(self) -> dict | None:
        return self.read_state().get("hitl_delegation")

    def revoke_delegation(self) -> None:
        """Delegación REVOCADA (forma de la suite: `status: "revoked"` +
        `revoked_at`)."""
        state = self.read_state()
        state["hitl_delegation"] = {
            "status": "revoked",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "revoked_at": "2026-10-14T12:00:00Z",
        }
        self.write_state(state)

    def expire_delegation(self) -> None:
        """Delegación VENCIDA por su `expires_on` (fecha ISO en el pasado; la
        forma de `test_pd6_case_b_expired_delegation_fails_closed…`)."""
        state = self.read_state()
        state["hitl_delegation"] = {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "expires_on": "2020-01-01",
        }
        self.write_state(state)

    def remove_delegation(self, *, epic_null: bool = False) -> None:
        """SIN registro `hitl_delegation` (la corrección P2/PD-6 caso C). Con
        `epic_null=True` además `active_epic: null` (la variante que PD-6
        declara idéntica)."""
        state = self.read_state()
        state["hitl_delegation"] = None
        if epic_null:
            state["active_epic"] = None
            state["epic_stage"] = None
        self.write_state(state)

    # -- invocación (caja negra) ------------------------------------------

    def closure(self, *extra: str) -> subprocess.CompletedProcess:
        """La clase `closure`: la decisión de cierre con su cierre citado."""
        return self.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL, *extra)

    def disposition(self, packet_id: str, *extra: str
                    ) -> subprocess.CompletedProcess:
        """La clase `disposition`: la decisión sobre un despacho sin recibo.
        Sin `--stage`: §2.1 declara que esa clase no lo acepta."""
        return self.register_transition(
            "--transition", "disposition", "--packet", packet_id, *extra)

    # -- observación ------------------------------------------------------

    def receipt_path_for(self, packet_id: str) -> Path:
        return (self.root / ".cdad" / "runtime" / "results" / self.execution_id
                / packet_id / RECEIPT_NAME)

    def write_contract(self, data: bytes) -> None:
        (self.root / CONTRACT_FILE).write_bytes(data)

    def close_feature_in_state(self) -> None:
        """Marca la feature activa como CERRADA en `epic_features` (forma del
        vocabulario `CLOSED_FEATURE_STATUSES`; mutación declarada del fixture)."""
        state = self.read_state()
        for entry in state.get("epic_features") or []:
            if entry.get("id") == FEATURE_ID:
                entry["status"] = FEATURE_CLOSED
        self.write_state(state)


@pytest.fixture
def single_fx(tmp_path: Path) -> _ClosureFixture:
    """Un paquete `dispatched` SIN recibo (el despacho que no volvió, B1)."""
    return _ClosureFixture(tmp_path, mode="single")


@pytest.fixture
def double_fx(tmp_path: Path) -> _ClosureFixture:
    """Dos paquetes de la ejecución activa: el primero con recibo, el segundo
    `dispatched` sin recibo."""
    return _ClosureFixture(tmp_path, mode="double")


@pytest.fixture
def authority_fx(tmp_path: Path) -> _ClosureFixture:
    """Fixture LISTO PARA CERRAR (las dos comprobaciones de PD-8 verdes): un
    paquete `dispatched` CON recibo durable y la aprobación `specification`
    vigente. La delegación HITL se muta por caso (PD-6, review-fix B1)."""
    return _ClosureFixture(tmp_path, mode="ready")


# ---------------------------------------------------------------- PD-8 (a)


def test_pd8a_closure_with_unreceipted_dispatch_fails_closed_naming_evidence(
        double_fx: _ClosureFixture) -> None:
    """PD-8(a) + INV-7, caso 1: con la ejecución activa y un paquete que tiene
    registro de despacho y NO tiene recibo durable (el segundo paquete del
    fixture; el primero SÍ tiene recibo, y la aprobación vigente está), el
    cierre → rc=2, marcador `evidence missing`, nombrando el `<packet_id>` y el
    recibo faltante, y ofreciendo las DOS salidas legítimas (recibir por el
    camino normal, o disponer). El state queda byte a byte idéntico (PD-8
    comprueba ANTES de cualquier escritura).

    Aislamiento de causas: el primer paquete tiene recibo durable (PD-8(a)
    satisfecho para él) y la aprobación `specification` vigente con el pin
    correcto (PD-8(b) verde); la ÚNICA entrega sin resolver es la segunda.

    RED hoy: rc=2 por error de uso («invalid choice: 'closure'», no es el
    rechazo del contrato) → falla la aserción del marcador.
    """
    assert double_fx.packet2 is not None, (
        "precondición (fixture): el fixture `double` debe tener dos paquetes")
    assert double_fx.receipt_path_for(double_fx.packet1).is_file(), (
        "precondición (fixture): el PRIMER paquete tiene recibo durable "
        "(aislamiento: no es la causa del rechazo)")
    assert not double_fx.receipt_path_for(double_fx.packet2).exists(), (
        "precondición (fixture): el SEGUNDO paquete NO tiene recibo durable")
    assert double_fx.read_state()["active_packet"]["status"] == "dispatched", (
        "precondición (fixture): el paquete despachado sin recibo está "
        "`dispatched`")
    assert_validate_green(double_fx, "precondición del caso 1")
    before = double_fx.state_bytes()

    proc = double_fx.closure()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-8(a) violada: el cierre con un despacho sin recibo durable debe "
        f"fallar cerrado (rc=2); hoy rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-8(a) violada: el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert double_fx.packet2 in out, (
        "PD-8(a) violada: el diagnóstico debe NOMBRAR el paquete despachado sin "
        f"recibo ({double_fx.packet2!r}): {out!r}")
    assert RECEIPT_NAME in out, (
        "PD-8(a) violada: el diagnóstico debe nombrar el recibo faltante "
        f"({RECEIPT_NAME!r}): {out!r}")
    assert "receive" in out.lower(), (
        "PD-8(a) violada: el rechazo debe OFRECER la salida legítima de recibir "
        f"la entrega por el camino normal (`receive`): {out!r}")
    assert "disposition" in out.lower(), (
        "PD-8(a) violada: el rechazo debe OFRECER la salida legítima de disponer "
        f"el despacho (`--transition disposition`, feature abierta): {out!r}")
    assert "late-delivery" not in out.lower(), (
        "PD-8(a)/B1 violada: el camino `receive --late` + `late-delivery` es "
        "SÓLO para una feature cerrada y el rechazo del cierre debe DEJAR de "
        f"ofrecerlo: {out!r}")
    assert_unchanged(double_fx, before, "PD-8", "a (rechazo del cierre)")


# ---------------------------------------------------------------- PD-8 (b)


def test_pd8b_closure_without_vigent_specification_pin_fails_closed(
        tmp_path: Path) -> None:
    """PD-8(b) + INV-7, caso 2 (dos variantes): con TODAS las entregas
    requeridas satisfechas (el único paquete despachado tiene recibo durable) y
    la feature activa, si NO existe una entrada `specification` cuyo pin nombre
    el contrato → `closure` rc=2, marcador `approval pending`, nombrando la
    aprobación faltante, sin efectos.

      (a) la feature NO tiene ninguna entrada `specification`;
      (b) la entrada existe pero su pin YA NO nombra el contrato: los bytes
          actuales del contrato divergen del digest pineado (el caso real de la
          re-aprobación: el contrato cambia).

    Aislamiento de causas: PD-8(a) está verde en ambos casos (el paquete tiene
    recibo); la única causa del rechazo es la aprobación vigente.

    RED hoy: rc=2 por error de uso → falla la aserción del marcador, en cada
    variante.
    """
    for label, case in (("sin entrada `specification`", "missing"),
                        ("pin con digest divergente", "divergent")):
        fixture = _BaseFixture(tmp_path / case, mode="ready")
        assert fixture.receipt_path().is_file(), (
            "precondición (fixture): el paquete despachado tiene recibo durable "
            "(aislamiento: PD-8(a) no es la causa)")
        if case == "missing":
            state = fixture.read_state()
            state["stage_history"] = [
                e for e in entries(state)
                if not (e.get("feature") == FEATURE_ID
                        and e.get("stage") == "specification")
            ]
            fixture.write_state(state)
            assert not [
                e for e in entries(fixture.read_state())
                if e.get("stage") == "specification"
            ], "precondición (fixture): sin entradas `specification`"
        else:
            (fixture.root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES_DIVERGENT)
            pinned = [
                e for e in entries(fixture.read_state())
                if e.get("stage") == "specification"
                and e.get("feature") == FEATURE_ID
            ]
            assert pinned, (
                "precondición (fixture): la entrada `specification` existe")
            assert all(
                e.get("contract_sha256") != hashlib.sha256(
                    CONTRACT_BYTES_DIVERGENT).hexdigest()
                for e in pinned), (
                "precondición (fixture): el digest pineado diverge de los bytes "
                "actuales del contrato")

        before = fixture.state_bytes()
        proc = fixture.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)
        out = proc.stdout + proc.stderr

        assert proc.returncode == 2, (
            f"PD-8(b) violada ({label}): el cierre sin una aprobación "
            f"`specification` vigente que pinne el contrato debe fallar cerrado "
            f"(rc=2); hoy rc={proc.returncode}: {out!r}")
        assert APPROVAL_PENDING in out.lower(), (
            f"PD-8(b) violada ({label}): el rechazo debe llevar el marcador "
            f"«{APPROVAL_PENDING}»: {out!r}")
        assert names_any(out, FEATURE_ID, CONTRACT_FILE, "specification"), (
            f"PD-8(b) violada ({label}): el diagnóstico debe NOMBRAR la "
            f"aprobación faltante (la feature {FEATURE_ID!r}, el contrato "
            f"{CONTRACT_FILE!r} o la entrada `specification`): {out!r}")
        assert_unchanged(fixture, before, "PD-8", f"b ({label})")


# ---------------------------------------------------------------- PD-9


def test_pd9_closure_applied_records_evidence_and_rests(
        tmp_path: Path) -> None:
    """PD-9 (+ PD-20, + PD-17), caso 3: con las dos comprobaciones verdes →
    `closure` rc=0 y el state queda:
      * una entrada de traza con `transition: "closure"`, la etiqueta de
        `--stage`, `closure_path` y el `closure_sha256` DERIVADO de los bytes
        del cierre (PD-20), que además se IMPRIME;
      * `epic_features[<feat>].status: "done"` + `closed_at` +
        `closure_evidence{path, sha256}`;
      * `active_feature: null`, `current_stage: "idle"`, `active_packet` null o
        terminal;
      * la historia previa intacta (append-only, INV-3) y `validate-state` rc=0
        ANTES y DESPUÉS (vía de reposo, token `idle`).

    Aislamiento de causas: el único paquete despachado tiene recibo durable y
    la aprobación vigente pinnea el contrato → PD-8 verde.

    RED hoy: rc=2 por error de uso («invalid choice: 'closure'») → falla la
    primera aserción de contrato (el cierre aplicado).
    """
    fixture = _BaseFixture(tmp_path, mode="ready")
    assert fixture.receipt_path().is_file(), (
        "precondición (fixture): el paquete despachado tiene recibo durable")
    # Precondición (fixture): materializar el documento de cierre que este caso
    # cita, con los bytes declarados, en el path relativo `CLOSURE_REL`. El
    # fixture base `mode="ready"` NO lo escribe (sólo `_ClosureFixture` lo hace,
    # y sus modos dejan un despacho sin recibo: aquí se necesita TODAS las
    # entregas satisfechas para que PD-8 esté verde y la única causa evaluada
    # sea el cierre aplicado). Sin este artefacto el cierre rechaza por
    # `evidence missing` (PD-20: el digest no se puede derivar de bytes ausentes)
    # en vez de aplicarse (PD-9). Sólo precondición de fixture: ninguna aserción
    # de contrato cambia.
    closure_file = fixture.root / CLOSURE_REL
    closure_file.parent.mkdir(parents=True, exist_ok=True)
    closure_file.write_bytes(CLOSURE_BYTES)
    assert closure_file.is_file(), (
        "precondición (fixture): el cierre citado existe en la ruta declarada")
    before_state = fixture.read_state()
    before_entries = entries(before_state)
    derived = hashlib.sha256(CLOSURE_BYTES).hexdigest()
    assert_validate_green(fixture, "caso 3 (antes del cierre)")

    proc = fixture.register_transition(
        "--transition", "closure", "--stage", CLOSURE_STAGE,
        "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-9 violada: con las dos comprobaciones verdes el cierre debe "
        f"aplicarse (rc=0); hoy rc={proc.returncode}: {out!r}")

    state = fixture.read_state()
    entry = last_entry_with(state, transition="closure")
    assert entry is not None, (
        "PD-9 violada: no hay entrada con `transition: \"closure\"` en "
        f"`stage_history`: {entries(state)[-3:]!r}")
    assert entry.get("stage") == CLOSURE_STAGE, (
        "PD-9 violada: la entrada debe llevar la etiqueta declarada en "
        f"`--stage` ({CLOSURE_STAGE!r}): {entry!r}")
    assert names_path(entry.get("closure_path"), CLOSURE_REL), (
        "PD-9 violada: la entrada de traza debe nombrar el cierre citado "
        f"({CLOSURE_REL!r}): {entry.get('closure_path')!r}")
    assert entry.get("closure_sha256") == derived, (
        "PD-20 violada: sin `--closure-sha256`, el digest del cierre debe "
        "DERIVARSE de los bytes actuales y escribirse en la entrada; esperado "
        f"{derived!r}, entrada {entry.get('closure_sha256')!r}")
    assert derived in out, (
        "PD-20 violada: la salida debe IMPRIMIR el digest usado (derivado) para "
        f"que la entrada quede auditable: {derived!r} no aparece en {out!r}")
    assert entry.get("approved_by") == APPROVER, (
        "PD-6/PD-9 violada: el cierre lo registra el aprobador declarado "
        f"({APPROVER!r}): {entry.get('approved_by')!r}")

    feature = _feature_entry(state, FEATURE_ID)
    assert feature is not None, (
        f"PD-9 violada: la feature {FEATURE_ID!r} debe seguir en `epic_features`")
    assert feature.get("status") == FEATURE_CLOSED, (
        "PD-9 violada: `epic_features[<feat>].status` debe quedar "
        f"{FEATURE_CLOSED!r}: {feature.get('status')!r}")
    assert feature.get("closed_at"), (
        f"PD-9 violada: la feature cerrada debe registrar `closed_at`: {feature!r}")
    evidence = feature.get("closure_evidence")
    assert isinstance(evidence, dict), (
        "PD-9 violada: la feature cerrada debe llevar "
        f"`closure_evidence{{path, sha256}}`: {evidence!r}")
    assert names_path(evidence.get("path"), CLOSURE_REL), (
        "PD-9 violada: `closure_evidence.path` debe nombrar el cierre citado "
        f"({CLOSURE_REL!r}): {evidence.get('path')!r}")
    assert evidence.get("sha256") == derived, (
        "PD-20 violada: `closure_evidence.sha256` debe ser el digest derivado "
        f"de los bytes del cierre; esperado {derived!r}, "
        f"visto {evidence.get('sha256')!r}")

    assert state.get("active_feature") is None, (
        "PD-9 violada: tras el cierre `active_feature` debe ser null: "
        f"{state.get('active_feature')!r}")
    assert state.get("current_stage") == IDLE, (
        f"PD-9 violada: tras el cierre `current_stage` debe ser {IDLE!r}: "
        f"{state.get('current_stage')!r}")
    active_packet = state.get("active_packet")
    assert active_packet is None or (
        active_packet.get("status") in TERMINAL_PACKET_STATUSES), (
        "PD-9 violada: tras el cierre `active_packet` debe ser null o terminal "
        f"({TERMINAL_PACKET_STATUSES}): {active_packet!r}")

    assert len(entries(state)) == len(before_entries) + 1, (
        "PD-9 violada: el cierre debe dejar la traza como UNA entrada nueva "
        f"(antes {len(before_entries)}, después {len(entries(state))})")
    assert entries(state)[:len(before_entries)] == before_entries, (
        "PD-9/INV-3 violada: la historia previa no debe reescribirse "
        "(append-only)")

    after_out = assert_validate_green(fixture, "caso 3 (después del cierre)")
    assert IDLE in after_out, (
        "PD-9 violada: el cierre debe dejar un reposo que `validate-state` "
        f"acepte por la vía de reposo (token {IDLE!r}): {after_out!r}")


# ---------------------------------------------------------------- PD-21 (a)


def test_pd21_disposition_of_unreceipted_dispatch_is_structural_and_does_not_touch_the_rest(
        single_fx: _ClosureFixture) -> None:
    """PD-21 (condición 1) + INV-9 (+ PD-10, + PD-17), caso 4(a): con la feature
    ABIERTA y un despacho SIN recibo durable, `--transition disposition --packet
    <id> --resolution abandoned` → rc=0 y deja UNA entrada de `stage_history`
    con `transition: "disposition"`, `stage: "dispatch-disposition"`,
    `resolution`, `approval_effect: false`, `transition_key` (forma sha256) y
    SIN `approved_by`; y NO toca nada más: ningún otro campo del state cambia
    salvo `stage_history`, `last_updated` y el **status del paquete identificado**,
    y `epic_features`/`closed_at`/`active_feature`/`current_stage` quedan
    intactos. `validate-state` rc=0 antes y después (PD-17).

    REEMPLAZO DECLARADO — regla A-1 de 006-005 U5 (`docs/specs/
    006-005-native-path-parity/plan.md` §4, fila U5): este test afirmaba que el
    paquete seguía `dispatched` tras la disposición. La postcondición nueva es
    «`active_packet.status` pasa a `failed` (terminal); el resto del estado
    intacto» (PD-19 de 006-005, D-4). La enmienda de esa consecuencia de INV-9
    está **aprobada por el dueño** (`docs/epics/epic-006-opencode-concurrency/
    execution.md`:260). Motivo: la disposición es el camino mecánico a `failed`
    para el intento que no vuelve, así que el efecto deja de ser `pass`. El
    resto del test —la forma de la entrada, la ausencia de `approved_by`, la
    inmutabilidad de todo lo demás— NO se toca ni se debilita.

    RED hoy (006-005 U5): rc=0 y la entrada correcta, pero el paquete sigue
    `dispatched` → falla la aserción del estado nuevo.
    """
    before_state = single_fx.read_state()
    assert single_fx.receipt_path_for(single_fx.packet_id).exists() is False, (
        "precondición (fixture): el despacho NO tiene recibo durable")
    assert before_state["active_packet"]["status"] == "dispatched", (
        "precondición (fixture): el paquete está `dispatched`")
    assert (_feature_entry(before_state, FEATURE_ID) or {}).get("status") != (
        FEATURE_CLOSED), "precondición (fixture): la feature está ABIERTA"
    assert_validate_green(single_fx, "caso 4(a) (antes de la disposición)")

    proc = single_fx.disposition(
        single_fx.packet_id, "--resolution", RESOLUTION_ABANDONED)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-21 violada: la disposición de un despacho sin recibo con la feature "
        f"abierta debe registrarse (rc=0); hoy rc={proc.returncode}: {out!r}")

    state = single_fx.read_state()
    entry = last_entry(state)
    assert entry.get("transition") == "disposition", (
        "PD-21 violada: la entrada nueva debe declarar "
        f"`transition: \"disposition\"`: {entry!r}")
    assert entry.get("stage") == DISPOSITION_STAGE, (
        "PD-21 violada: la disposición usa la etiqueta canónica "
        f"({DISPOSITION_STAGE!r}, §2.1 no admite `--stage`): {entry!r}")
    assert entry.get("packet_id") == single_fx.packet_id, (
        "PD-21 violada: la entrada debe citar el paquete dispuesto "
        f"({single_fx.packet_id!r}): {entry.get('packet_id')!r}")
    assert entry.get("resolution") == RESOLUTION_ABANDONED, (
        "PD-21 violada: la entrada debe llevar la resolución declarada "
        f"({RESOLUTION_ABANDONED!r}): {entry.get('resolution')!r}")
    assert entry.get("approval_effect") is False, (
        "PD-21 violada: la disposición NO aprueba nada (`approval_effect: "
        f"false`): {entry.get('approval_effect')!r}")
    assert not entry.get("approved_by"), (
        "PD-21 violada: la disposición NO lleva `approved_by` (registra una "
        f"decisión, no una aprobación): {entry.get('approved_by')!r}")
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        "PD-10/PD-21 violada: la entrada de la disposición debe llevar "
        f"`transition_key` (clave nueva y aditiva): {key!r}")

    after_packet = state.get("active_packet") or {}
    assert after_packet.get("id") == single_fx.packet_id, (
        "PD-21 violada: la disposición no debe cambiar el paquete identificado: "
        f"{after_packet!r}")
    # REEMPLAZO A-1 (006-005 U5, PD-19/D-4): el efecto del `disposition` sobre
    # el paquete citado es `failed` (terminal, sin recibo ni aprobación). Antes
    # de la enmienda aprobada por el dueño, este test afirmaba `dispatched`.
    assert after_packet.get("status") == "failed", (
        "PD-19 violada (006-005 U5, A-1): la disposición del despacho sin "
        "recibo debe dejar `active_packet.status: failed` (terminal); visto "
        f"{after_packet.get('status')!r}")
    assert {k: v for k, v in after_packet.items() if k != "status"} == (
        {k: v for k, v in (before_state.get("active_packet") or {}).items()
         if k != "status"}), (
        "PD-19 violada (a): sólo `active_packet.status` cambia dentro del "
        f"paquete: {(before_state.get('active_packet') or {})!r} → "
        f"{after_packet!r}")
    unchanged_keys = sorted(
        k for k in set(state) | set(before_state)
        if k not in ("stage_history", "last_updated", "active_packet"))
    for key_name in unchanged_keys:
        assert state.get(key_name) == before_state.get(key_name), (
            "PD-21/INV-9 violada: la disposición sólo escribe la entrada de "
            f"`stage_history`, `last_updated` y el status del paquete "
            f"identificado; `{key_name}` cambió: "
            f"{before_state.get(key_name)!r} → {state.get(key_name)!r}")
    assert (_feature_entry(state, FEATURE_ID) or {}).get("status") == (
        _feature_entry(before_state, FEATURE_ID) or {}).get("status"), (
        "PD-21 violada: la disposición no toca el status de la feature")
    assert "closed_at" not in (_feature_entry(state, FEATURE_ID) or {}), (
        "PD-21 violada: la disposición no cierra la feature (ni escribe "
        "`closed_at`)")
    assert state.get("active_feature") == before_state.get("active_feature"), (
        "PD-21 violada: la disposición no toca `active_feature`")
    assert state.get("current_stage") == before_state.get("current_stage"), (
        "PD-21 violada: la disposición no toca `current_stage`")

    assert_validate_green(single_fx, "caso 4(a) (después de la disposición)")


# ---------------------------------------------------------------- PD-21 (b) / B1


def test_pd21_b1_closure_rejects_then_the_disposition_unblocks_and_the_closure_advances(
        single_fx: _ClosureFixture) -> None:
    """PD-21 (condición 2) + PD-8(a) + PD-9 + PD-17, caso 4(b) — el caso que la
    review del orquestador exigió (B1): con la feature ABIERTA y un despacho
    SIN recibo, el cierre rechaza nombrando el despacho (`evidence missing`); se
    registra la disposición (`--resolution abandoned`) y **entonces el cierre
    AVANZA** (rc=0), dejando el reposo coherente (`validate-state` rc=0, vía de
    reposo). La disposición satisface PD-8(a) para ese paquete (PD-21,
    condición 2).

    RED hoy: el primer rechazo no es el del contrato (rc=2 por error de uso: el
    marcador y el nombre del paquete faltan) → falla la aserción del marcador y
    con ella el flujo; la disposición tampoco existe.
    """
    assert_validate_green(single_fx, "B1 (antes)")
    before_reject = single_fx.state_bytes()

    rejected = single_fx.closure()
    out_reject = rejected.stdout + rejected.stderr
    assert rejected.returncode == 2, (
        "PD-8(a) violada (B1): el cierre con un despacho sin recibo debe "
        f"rechazar (rc=2); hoy rc={rejected.returncode}: {out_reject!r}")
    assert EVIDENCE_MISSING in out_reject.lower(), (
        "PD-8(a) violada (B1): el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out_reject!r}")
    assert single_fx.packet_id in out_reject, (
        "PD-8(a) violada (B1): el rechazo debe NOMBRAR el despacho sin recibo "
        f"({single_fx.packet_id!r}): {out_reject!r}")
    assert_unchanged(single_fx, before_reject, "PD-8(a)", "B1 (rechazo)")

    disposed = single_fx.disposition(
        single_fx.packet_id, "--resolution", RESOLUTION_ABANDONED)
    out_disposed = disposed.stdout + disposed.stderr
    assert disposed.returncode == 0, (
        "PD-21 violada (B1): la disposición del despacho sin recibo debe "
        f"registrarse (rc=0); hoy rc={disposed.returncode}: {out_disposed!r}")
    assert _disposition_entries(single_fx.read_state()), (
        "PD-21 violada (B1, condición 4): la disposición debe dejar su traza en "
        "`stage_history`")

    advanced = single_fx.closure()
    out_advanced = advanced.stdout + advanced.stderr
    assert advanced.returncode == 0, (
        "PD-21 violada (B1, condición 2): tras la disposición el cierre debe "
        "AVANZAR (rc=0) — la disposición satisface PD-8(a) para ese paquete; "
        f"hoy rc={advanced.returncode}: {out_advanced!r}")

    state = single_fx.read_state()
    assert state.get("active_feature") is None, (
        "PD-9 violada (B1): el cierre debe dejar `active_feature: null`: "
        f"{state.get('active_feature')!r}")
    assert state.get("current_stage") == IDLE, (
        f"PD-9 violada (B1): el cierre debe dejar `current_stage: {IDLE!r}`: "
        f"{state.get('current_stage')!r}")
    feature = _feature_entry(state, FEATURE_ID)
    assert (feature or {}).get("status") == FEATURE_CLOSED, (
        f"PD-9 violada (B1): la feature debe quedar {FEATURE_CLOSED!r}: "
        f"{feature!r}")

    after_out = assert_validate_green(single_fx, "B1 (después del cierre)")
    assert IDLE in after_out, (
        f"PD-9 violada (B1): el reposo debe aceptarse con el token {IDLE!r}: "
        f"{after_out!r}")


# ---------------------------------------------------------------- PD-21 (c)


def test_pd21_superseded_disposition_records_replaced_by(
        double_fx: _ClosureFixture) -> None:
    """PD-21 (condición 1, resolución `superseded`) + PD-12, caso 4(c):
    `--resolution superseded --replaced-by <packet-id>` → rc=0 y la entrada
    lleva `resolution` y `replaced_by` (el paquete que reemplaza: el PRIMER
    paquete del fixture, real y de la misma ejecución); y el negativo —la misma
    resolución SIN `--replaced-by`— → rc=2 SIN efectos (PD-21 lo declara
    obligatorio para `superseded`).

    RED hoy: rc=2 por error de uso en ambos lados → fallan la aserción de
    registro y, en el negativo, la de «sin efectos» (hoy no distingue la causa).
    """
    assert double_fx.packet2 is not None, (
        "precondición (fixture): el fixture `double` debe tener dos paquetes")
    first = double_fx.disposition(
        double_fx.packet2, "--resolution", RESOLUTION_SUPERSEDED,
        "--replaced-by", double_fx.packet1)
    out = first.stdout + first.stderr

    assert first.returncode == 0, (
        "PD-21 violada (superseded): la disposición `superseded` con "
        "`--replaced-by` debe registrarse (rc=0); hoy rc="
        f"{first.returncode}: {out!r}")
    entry = last_entry(double_fx.read_state())
    assert entry.get("transition") == "disposition", (
        f"PD-21 violada (superseded): la entrada debe ser de disposición: {entry!r}")
    assert entry.get("resolution") == RESOLUTION_SUPERSEDED, (
        "PD-21 violada (superseded): la entrada debe llevar la resolución "
        f"`{RESOLUTION_SUPERSEDED}`: {entry.get('resolution')!r}")
    assert entry.get("replaced_by") == double_fx.packet1, (
        "PD-21 violada (superseded): la entrada debe llevar `replaced_by` con el "
        f"paquete declarado ({double_fx.packet1!r}): {entry.get('replaced_by')!r}")
    assert entry.get("approval_effect") is False, (
        "PD-21 violada (superseded): la disposición NO aprueba nada "
        f"(`approval_effect: false`): {entry.get('approval_effect')!r}")
    assert not entry.get("approved_by"), (
        "PD-21 violada (superseded): la disposición NO lleva `approved_by`: "
        f"{entry.get('approved_by')!r}")

    # Negativo: `superseded` exige `--replaced-by` (PD-21). El contrato declara
    # la obligatoriedad pero no el marcador de su ausencia (interpretación 4),
    # así que se asevera el fallo cerrado sin efectos (INV-7).
    other = _ClosureFixture(double_fx.base / "no-replaced-by", mode="double")
    assert other.packet2 is not None, "precondición (fixture): dos paquetes"
    state_before = other.state_bytes()
    missing = other.disposition(
        other.packet2, "--resolution", RESOLUTION_SUPERSEDED)
    out_missing = missing.stdout + missing.stderr
    assert missing.returncode == 2, (
        "PD-21 violada (negativo): la resolución `superseded` SIN "
        "`--replaced-by` debe fallar cerrado (rc=2); hoy rc="
        f"{missing.returncode}: {out_missing!r}")
    assert "invalid choice" not in out_missing, (
        "PD-21 violada (negativo): el rechazo debe venir de la coherencia de la "
        "disposición (la clase existe y le falta el argumento obligatorio), no "
        f"del error de uso del CLI (la clase no existe): {out_missing!r}")
    assert_unchanged(other, state_before, "PD-21", "superseded sin `--replaced-by`")


# ---------------------------------------------------------------- PD-21 (rechazos)


def test_pd21_disposition_rejections_fail_closed_state_incoherent(
        tmp_path: Path) -> None:
    """PD-21 + PD-12(iv), caso 5: cuatro variantes de incumplimiento de las
    comprobaciones mecánicas de la disposición → rc=2, marcador
    `state incoherent`, NOMBRANDO el hecho, y state byte a byte idéntico
    (INV-7), todas con la feature abierta y la aprobación vigente:

      (i)   el paquete citado NO pertenece a la ejecución activa;
      (ii)  el paquete citado NO está `dispatched` (no tiene registro de
            despacho);
      (iii) el paquete citado YA tiene recibo durable (la evidencia contradice la
            disposición: la guarda que impide saltar una entrega que existe);
      (iv)  la feature está CERRADA (no hay ejecución activa que disponer).

    RED hoy: rc=2 por error de uso (no es el rechazo del contrato) → falla la
    aserción del marcador en cada variante.
    """
    variants: list[tuple[str, _BaseFixture | _ClosureFixture, str, tuple[str, ...]]] = []

    # (i) paquete ajeno a la ejecución activa.
    foreign = _ClosureFixture(tmp_path / "foreign", mode="single")
    variants.append((
        "paquete ajeno a la ejecución activa", foreign, FOREIGN_PACKET_ID,
        (FOREIGN_PACKET_ID, FEATURE_ID)))

    # (ii) paquete NO `dispatched` (sin registro de despacho).
    prepared = _BaseFixture(tmp_path / "prepared", mode="prepared")
    prepared_packet = (prepared.read_state().get("active_packet") or {}).get("id")
    assert prepared_packet, "precondición (fixture): paquete activo `prepared`"
    variants.append((
        "paquete no `dispatched`", prepared, prepared_packet,
        (prepared_packet, "dispatched", "dispatch")))

    # (iii) paquete que YA tiene recibo durable.
    receipted = _BaseFixture(tmp_path / "receipted", mode="ready")
    receipted_packet = (receipted.read_state().get("active_packet") or {}).get("id")
    assert receipted.receipt_path().is_file(), (
        "precondición (fixture): el paquete tiene recibo durable")
    variants.append((
        "paquete con recibo durable", receipted, receipted_packet,
        (receipted_packet, RECEIPT_NAME, "receipt")))

    # (iv) feature cerrada.
    closed = _ClosureFixture(tmp_path / "closed", mode="single")
    closed.close_feature_in_state()
    closed_packet = closed.packet_id
    assert (_feature_entry(closed.read_state(), FEATURE_ID) or {}).get(
        "status") == FEATURE_CLOSED, (
        "precondición (fixture): la feature está cerrada")
    variants.append((
        "feature cerrada", closed, closed_packet,
        (FEATURE_ID, FEATURE_CLOSED, "closed", "cerrada")))

    for label, fixture, packet_id, tokens in variants:
        before = fixture.state_bytes()
        proc = fixture.register_transition(
            "--transition", "disposition", "--packet", packet_id,
            "--resolution", RESOLUTION_ABANDONED)
        out = proc.stdout + proc.stderr

        assert proc.returncode == 2, (
            f"PD-21 violada ({label}): la disposición que incumple la "
            f"coherencia mecánica debe fallar cerrado (rc=2); hoy rc="
            f"{proc.returncode}: {out!r}")
        assert STATE_INCOHERENT in out.lower(), (
            f"PD-21 violada ({label}): el rechazo debe llevar el marcador "
            f"«{STATE_INCOHERENT}»: {out!r}")
        assert not _disposition_entries(fixture.read_state()), (
            f"PD-21 violada ({label}): el rechazo no debe dejar entrada de "
            "disposición")
        assert names_any(out, *tokens), (
            f"PD-21 violada ({label}): el diagnóstico debe NOMBRAR el hecho "
            f"({tokens}): {out!r}")
        assert_unchanged(fixture, before, "PD-21", label)


# ---------------------------------------------------------------- PD-11 / PD-21 (idempotencia)


def test_pd11_pd21_identical_disposition_is_noop_and_another_resolution_appends(
        double_fx: _ClosureFixture) -> None:
    """PD-11 + PD-21 (condición 3) + PD-12, caso 6: repetir la invocación
    IDÉNTICA de la disposición → rc=0, SIN segunda entrada de `stage_history`,
    con el state byte a byte idéntico al de la primera invocación y una salida
    que nombra la entrada existente (su `transition_key`); y una resolución
    DISTINTA del mismo despacho (`abandoned` y luego `superseded`) es un
    `transition_key` distinto → entrada NUEVA (append), sin reescribir la
    anterior (INV-3/PD-12).

    RED hoy: rc=2 por error de uso → falla la primera aserción de contrato.
    """
    assert double_fx.packet2 is not None, (
        "precondición (fixture): el fixture `double` debe tener dos paquetes")
    first = double_fx.disposition(
        double_fx.packet2, "--resolution", RESOLUTION_ABANDONED)
    out_first = first.stdout + first.stderr
    assert first.returncode == 0, (
        "PD-11 violada: la primera disposición debe registrar la transición "
        f"(rc=0); hoy rc={first.returncode}: {out_first!r}")
    state_after_first = double_fx.state_bytes()
    entries_after_first = entries(double_fx.read_state())
    key = last_entry(double_fx.read_state()).get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        f"PD-11 violada: la entrada de la disposición lleva su clave: {key!r}")

    repeat = double_fx.disposition(
        double_fx.packet2, "--resolution", RESOLUTION_ABANDONED)
    out_repeat = repeat.stdout + repeat.stderr

    assert repeat.returncode == 0, (
        "PD-11 violada: repetir la invocación idéntica de la disposición debe "
        f"ser un no-op exitoso (rc=0); rc={repeat.returncode}: {out_repeat!r}")
    assert len(entries(double_fx.read_state())) == len(entries_after_first), (
        "PD-11 violada: la repetición idéntica NO debe agregar una segunda "
        f"entrada de `stage_history` (sigue habiendo {len(entries_after_first)})")
    assert double_fx.state_bytes() == state_after_first, (
        "PD-11 violada: el state tras la repetición idéntica debe ser byte a "
        "byte idéntico al de la primera invocación")
    assert key and key in out_repeat, (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key!r}): {out_repeat!r}")

    other = double_fx.disposition(
        double_fx.packet2, "--resolution", RESOLUTION_SUPERSEDED,
        "--replaced-by", double_fx.packet1)
    out_other = other.stdout + other.stderr
    assert other.returncode == 0, (
        "PD-12 violada: una resolución DISTINTA del mismo despacho es una "
        f"transición distinta y debe registrarse (rc=0); rc={other.returncode}: "
        f"{out_other!r}")
    entries_after_other = entries(double_fx.read_state())
    assert len(entries_after_other) == len(entries_after_first) + 1, (
        "PD-12 violada: la resolución distinta debe dejar UNA entrada NUEVA "
        f"(antes {len(entries_after_first)}, después {len(entries_after_other)})")
    new_entry = entries_after_other[-1]
    assert new_entry.get("resolution") == RESOLUTION_SUPERSEDED, (
        f"PD-12 violada: la entrada nueva lleva la resolución nueva: {new_entry!r}")
    assert new_entry.get("replaced_by") == double_fx.packet1, (
        f"PD-12 violada: la entrada nueva lleva `replaced_by`: {new_entry!r}")
    assert entries_after_other[:len(entries_after_first)] == entries_after_first, (
        "PD-12/INV-3 violada: las entradas previas no deben reescribirse "
        "(append-only)")


# ---------------------------------------------------------------- PD-6 (B1)
# Review-fix B1 (review.md §1): PD-6 cubre `gate` **Y** `closure` («`gate` y
# `closure` exigen `--approve-by` no vacío… Una delegación revocada o vencida →
# rc=2, marcador `approval pending`»). La implementación consumía el control de
# autoridad SÓLO en la clase `gate`: un `closure` bajo delegación revocada o
# vencida PROSPERABA (rc=0, escribía `approved_by` y marcaba la feature `done`).
# Estos casos son el RED de esa postcondición sobre `closure`, con el fixture
# LISTO PARA CERRAR (las dos comprobaciones de PD-8 verdes) de modo que la ÚNICA
# causa del rechazo sea la autoridad, y su control positivo (caso C, P2/D-10).


def test_b1_pd6_revoked_delegation_fails_closed_approval_pending(
        authority_fx: _ClosureFixture) -> None:
    """PD-6 (B1) + INV-7: con el fixture LISTO PARA CERRAR (PD-8 verde) y la
    delegación REVOCADA (`status: "revoked"` + `revoked_at`, la forma del focal
    de T2), `closure` → rc=2, marcador `approval pending`, NOMBRANDO el registro
    de autoridad, y SIN efectos: el state queda byte a byte idéntico (nada de
    `epic_features[].status: "done"` ni `active_feature: null`).

    Aislamiento de causas: el paquete despachado tiene recibo durable (PD-8(a)
    verde) y la aprobación `specification` vigente pinnea el contrato (PD-8(b)
    verde), así que la única causa posible del rechazo es la autoridad.

    RED hoy (defecto B1): el `closure` no consulta la autoridad → prospera
    (rc=0) y MARCA la feature `done` → falla la ASERCIÓN del rc (AssertionError
    de contrato), nunca por import, sintaxis o fixture.
    """
    authority_fx.revoke_delegation()
    delegation = authority_fx.delegation()
    assert delegation is not None and delegation.get("status") == "revoked", (
        "precondición (fixture): la delegación debe quedar revocada: "
        f"{delegation!r}")
    assert authority_fx.receipt_path().is_file(), (
        "precondición (fixture): PD-8(a) verde — el paquete despachado tiene "
        "recibo durable (aislamiento: no es la causa del rechazo)")
    before = authority_fx.state_bytes()

    proc = authority_fx.closure()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-6 violada (B1, revocada): con la delegación revocada el cierre debe "
        f"fallar cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert APPROVAL_PENDING in out.lower(), (
        "PD-6 violada (B1, revocada): el fallo cerrado de la autoridad debe "
        f"llevar el marcador «{APPROVAL_PENDING}»: {out!r}")
    assert ("delegation" in out.lower()) or (EPIC_ID in out), (
        "PD-6 violada (B1, revocada): el diagnóstico debe NOMBRAR el registro "
        f"de autoridad que no es vigente: {out!r}")
    # INV-7: byte a byte idéntico ⇒ nada de `epic_features[].status: "done"` ni
    # de `active_feature: null` (la aprobación de cierre NO se aplica).
    assert_unchanged(authority_fx, before, "PD-6", "B1 (delegación revocada)")


def test_b1_pd6_expired_delegation_fails_closed_approval_pending(
        authority_fx: _ClosureFixture) -> None:
    """PD-6 (B1) + INV-7: ídem con la delegación VENCIDA por su `expires_on`
    (fecha ISO en el pasado; la forma de
    `test_pd6_case_b_expired_delegation_fails_closed_approval_pending`):
    `closure` → rc=2, marcador `approval pending`, nombrando el registro, y
    state byte a byte idéntico (sin `done` ni `active_feature: null`).

    Aislamiento de causas: PD-8(a) y PD-8(b) verdes; la única causa es la
    autoridad.

    RED hoy (defecto B1): el `closure` prospera (rc=0) → falla la ASERCIÓN del
    rc.
    """
    authority_fx.expire_delegation()
    delegation = authority_fx.delegation()
    assert delegation is not None and delegation.get("expires_on") == "2020-01-01", (
        "precondición (fixture): la delegación debe quedar vencida por fecha: "
        f"{delegation!r}")
    assert authority_fx.receipt_path().is_file(), (
        "precondición (fixture): PD-8(a) verde (aislamiento)")
    before = authority_fx.state_bytes()

    proc = authority_fx.closure()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-6 violada (B1, vencida): con la delegación vencida por fecha el "
        f"cierre debe fallar cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert APPROVAL_PENDING in out.lower(), (
        "PD-6 violada (B1, vencida): el fallo cerrado de la autoridad debe "
        f"llevar el marcador «{APPROVAL_PENDING}»: {out!r}")
    assert ("delegation" in out.lower()) or (EPIC_ID in out), (
        "PD-6 violada (B1, vencida): el diagnóstico debe NOMBRAR el registro "
        f"de autoridad que no es vigente: {out!r}")
    assert_unchanged(authority_fx, before, "PD-6", "B1 (delegación vencida)")


def test_pd6_case_c_closure_without_delegation_keeps_the_owner_unblocked(
        tmp_path: Path) -> None:
    """PD-6 (caso C, corrección P2/D-10) + PD-9 — CONTROL POSITIVO que la review
    exige conservar: SIN registro `hitl_delegation` —y en la variante que PD-6
    declara idéntica, además `active_epic: null`— el CLI NO inventa una
    autoridad ni puede verificar identidades: NO bloquea al dueño (la autoridad
    original). Con el fixture LISTO PARA CERRAR (PD-8 verde), el `closure` sigue
    rc=0, la entrada registra el aprobador DECLARADO (`--approve-by`) y la
    salida DECLARA que no hubo delegación que verificar.

    RED hoy: el control es la conducta que debe CONSERVARSE; el defecto B1 es el
    caso inverso (con delegación no vigente SÍ debe bloquear). Este test no
    asertá `validate-state` (D-10: el límite del estado con epic activo y sin
    delegación queda declarado como deuda, no lo cambia esta operación).
    """
    variants = (
        ("sin delegación", False),
        ("sin delegación + `active_epic: null`", True),
    )
    for label, epic_null in variants:
        fixture = _ClosureFixture(
            tmp_path / ("epic-null" if epic_null else "no-delegation"),
            mode="ready")
        fixture.remove_delegation(epic_null=epic_null)
        state = fixture.read_state()
        assert state.get("hitl_delegation") is None, (
            f"precondición (fixture, {label}): sin registro `hitl_delegation`")
        if epic_null:
            assert state.get("active_epic") is None, (
                f"precondición (fixture, {label}): `active_epic: null`")
        assert fixture.receipt_path().is_file(), (
            f"precondición (fixture, {label}): PD-8(a) verde")
        assert _feature_entry(state, FEATURE_ID) is not None, (
            f"precondición (fixture, {label}): la feature activa sigue en "
            "`epic_features`")

        proc = fixture.closure()
        out = proc.stdout + proc.stderr

        assert proc.returncode == 0, (
            f"PD-6 violada (caso C, {label}): sin delegación el CLI NO debe "
            "bloquear al dueño (la autoridad original) → el cierre sigue "
            f"(rc=0); rc={proc.returncode}: {out!r}")
        entry = last_entry_with(fixture.read_state(), transition="closure")
        assert entry is not None, (
            f"PD-6 violada (caso C, {label}): el cierre debe dejar su entrada "
            "de traza (`transition: \"closure\"`)")
        assert entry.get("approved_by") == APPROVER, (
            f"PD-6 violada (caso C, {label}): debe registrarse el aprobador "
            f"DECLARADO ({APPROVER!r}): {entry.get('approved_by')!r}")
        assert "delegation" in out.lower(), (
            f"PD-6 violada (caso C, {label}): la salida debe DECLARAR que no "
            f"hubo delegación que verificar: {out!r}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
