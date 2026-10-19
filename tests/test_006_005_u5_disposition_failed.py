#!/usr/bin/env python3
"""006-005 U5 RED — camino mecánico a `failed` con las condiciones aprobadas
(PD-19 de `docs/specs/006-005-native-path-parity/spec.md`, D-4).

Contract:
- docs/specs/006-005-native-path-parity/spec.md PD-19 (aprobada por el owner,
  `docs/epics/epic-006-opencode-concurrency/execution.md`:260) y D-4.
- docs/specs/006-005-native-path-parity/plan.md §3 ficha U5, §4 regla A-1.

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; ningún módulo de implementación se importa ni se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition disposition --packet <id> \\
        --resolution abandoned|superseded
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare --project-root <ABS> ...
    python3 scripts/cdad_continuity.py reconcile --project-root <ABS> \\
        --execution-context <execution.json> --packet <id> --json
    python3 skills/cdad-cycle/scripts/cdad_result.py receive ... [--late]
    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \\
        --project-root <ABS> --transition late-delivery --feature <feat> --packet <id>

PD-19: `register-transition --transition disposition --packet <activo>
--resolution abandoned|superseded`, SIN recibo durable ⇒
`active_packet.status: failed`. Condiciones aprobadas, cada una observable:

  (a) sólo el paquete identificado — ninguna otra clave del estado cambia salvo
      el registro de la transición en `stage_history`;
  (b) idempotente — repetir la misma disposición es un no-op exitoso y el
      estado no se reescribe (byte-idéntico);
  (c) entregas tardías intactas — `late-delivery` sigue registrable sobre el
      mismo paquete (fixture de feature cerrada con recibo durable);
  (d) `failed` no detiene ningún worker ni proceso remoto — es una marca de
      estado; lo observable es que la disposición no escribe más que el estado
      y que `reconcile` sigue siendo de solo lectura sobre ese paquete.

Oráculos adicionales de PD-19: `validate-state` VALID; `prepare` bloqueado antes
del comando y desbloqueado después; con recibo durable ⇒ rechazo que nombra
`receive`; la disposición no aprueba nada (`approval_effect: false`, sin
`approved_by`).

RED hoy: la disposición existe (005-012 T3 GREEN) y registra la entrada, pero su
efecto sobre el paquete es `pass`: `active_packet.status` sigue `dispatched`
(`cdad_packet.py`:5586 en el HEAD medido). Por eso los casos del efecto nuevo
fallan en la ASERCIÓN de contrato sobre el estado (nunca en la invocación ni en
una precondición de fixture). El caso del rechazo con recibo durable ya está
satisfecho por la guarda de 005-012 (el diagnóstico nombra `receive`): se
conserva como guarda de PD-19 y se declara GREEN hoy, sin inventarle un oráculo.

Mapeo test → postcondición:

  test_pd19_a_disposition_marks_only_the_identified_packet_failed
      -> PD-19 (a): tras el comando, `active_packet.id` es el paquete citado y
         `status: failed`; sólo `active_packet.status`, la entrada NUEVA de
         `stage_history` y `last_updated` cambian; la entrada lleva
         `transition: disposition`, `stage: dispatch-disposition`, `resolution`,
         `approval_effect: false`, `transition_key` y NO `approved_by`;
         `validate-state` VALID antes y después.
  test_pd19_b_identical_disposition_is_a_byte_identical_noop
      -> PD-19 (b): la segunda invocación idéntica → rc=0, sin entrada nueva y
         estado byte-idéntico al de la primera.
  test_pd19_prepare_is_blocked_before_and_unblocked_after
      -> PD-19 (oráculo de `prepare`): con el paquete `dispatched` un `prepare`
         falla sin escribir; tras la disposición (`failed` es terminal, fuera de
         `ACTIVE_PACKET_STATUSES`) el `prepare` publica un paquete nuevo.
  test_pd19_durable_receipt_rejection_names_receive
      -> PD-19 (cláusula del recibo durable): con recibo durable ⇒ rechazo que
         NOMBRA `receive`, sin efectos (estado byte-idéntico) y sin entrada de
         disposición.
  test_pd19_c_late_delivery_stays_registrable_on_the_same_failed_packet
      -> PD-19 (c): sobre el MISMO paquete marcado `failed`, la feature se cierra
         por el camino legítimo, el recibo llega tarde (`receive --late`) y
         `late-delivery` se registra (rc=0) con su traza; la feature no reabre.
  test_pd19_d_failed_is_a_state_mark_and_reconcile_stays_read_only
      -> PD-19 (d): la disposición no escribe nada más que
         `docs/.cdad-state.json` (ni recibo, ni ledger, ni pid) y `reconcile`
         sobre el paquete `failed` sigue siendo de solo lectura: rc=0, sobre
         JSON, estado byte-idéntico.

Fixture: proyecto descartable en un tempdir, con el `HOME` del subproceso en un
tempdir VACÍO (nunca el HOME real, nunca este repo), construido por el camino
legítimo del CLI (`prepare` → `prepare --record-dispatch`). Los ids del fixture
son sintéticos y anónimos. La entrega tardía se staged con la forma del focal de
`tests/test_005_012_t4_late_delivery.py`.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import prepare_args
from test_005_012_t1_register_transition_base import (
    APPROVER,
    FEATURE_ID,
    REPO_ROOT,
    RECEIPT_NAME,
    STATE_REL,
    TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture,
    entries,
    last_entry,
)
from test_005_012_t3_closure_dispatch_resolution import (
    CLOSURE_BYTES,
    CLOSURE_REL,
    CLOSURE_STAGE,
    DISPOSITION_STAGE,
    FEATURE_CLOSED,
    IDLE,
    RESOLUTION_ABANDONED,
    _disposition_entries,
    _feature_entry,
    assert_validate_green,
    names_any,
)
from test_005_012_t4_late_delivery import (
    BASELINE_REF,
    BASELINE_SHA256,
    LATE_REPORT_BYTES,
)

# El estado terminal que PD-19 introduce para el intento que no vuelve.
FAILED = "failed"

# La CLI de continuidad (contrato `reconcile-v1`): `reconcile` es read-only.
CONTINUITY_CLI = REPO_ROOT / "scripts" / "cdad_continuity.py"
PACKET_BEGIN = "---cdad-packet-json"

# La etiqueta canónica de la entrega tardía (PD-13 de 005-012).
LATE_TRANSITION = "late-delivery"


# ---------------------------------------------------------------- helpers


def _tree(root: Path) -> dict[str, bytes | None]:
    """Cada entrada bajo el proyecto: archivos → bytes, directorios → None."""
    return {
        path.relative_to(root).as_posix():
            path.read_bytes() if path.is_file() else None
        for path in sorted(root.rglob("*"))
    }


def _late_entries(state: dict) -> list[dict]:
    return [e for e in entries(state) if e.get("transition") == LATE_TRANSITION]


def _tree_delta(before: dict, after: dict) -> set[str]:
    return {
        rel for rel in set(before) | set(after)
        if before.get(rel) != after.get(rel)
        or (rel in before) != (rel in after)
    }


# ---------------------------------------------------------------- fixture


class _U5Fixture(_BaseFixture):
    """Proyecto descartable con un paquete `dispatched` listo para disponer.

    `durable_receipt=False` (por defecto) deja el paquete activo `dispatched`
    SIN recibo durable: la precondición de PD-19. `durable_receipt=True` deja el
    mismo paquete con recibo durable: la precondición del rechazo por
    contradicción de evidencia.
    """

    def __init__(self, base: Path, *, durable_receipt: bool = False) -> None:
        super().__init__(
            base, mode="ready" if durable_receipt else "dispatched_no_receipt")
        self.closure_file = self.root / CLOSURE_REL
        self.closure_file.parent.mkdir(parents=True, exist_ok=True)
        self.closure_file.write_bytes(CLOSURE_BYTES)

    # -- invocación (caja negra) ------------------------------------------

    def disposition(self, *extra: str) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "disposition", "--packet", self.packet_id, *extra)

    def closure(self) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)

    def prepare_new(self) -> subprocess.CompletedProcess:
        return self.run_packet(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="006-005 U5: siguiente encargo tras el intento fallido"))

    def receipt_path_for(self, packet_id: str) -> Path:
        return (self.root / ".cdad" / "runtime" / "results" / self.execution_id
                / packet_id / RECEIPT_NAME)

    def reconcile(self) -> subprocess.CompletedProcess:
        return self._run(CONTINUITY_CLI, [
            "reconcile",
            "--project-root", str(self.root),
            "--execution-context", str(
                self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json"),
            "--packet", self.packet_id,
            "--json",
        ])

    # -- entrega tardía (PD-19 (c)) ---------------------------------------

    def stage_late_delivery(self) -> None:
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
            "packet_id": self.packet_id,
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
        self.packet_md = (self.root / ".cdad" / "packets" / self.packet_id
                          / "PACKET.md")
        self.request_json = (self.root / ".cdad" / "packets" / self.packet_id
                             / "REQUEST.json")
        assert self.packet_md.is_file() and self.request_json.is_file(), (
            "precondición (fixture): el paquete del fixture está publicado")

    def receive_late(self) -> subprocess.CompletedProcess:
        return self.run_result(
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(
                self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json"),
            "--packet", str(self.packet_md),
            "--request", str(self.request_json),
            "--descriptor", str(self.descriptor),
            "--late",
        )

    def late_delivery(self) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", LATE_TRANSITION, "--feature", FEATURE_ID,
            "--packet", self.packet_id)


@pytest.fixture
def dispatch_fx(tmp_path: Path) -> _U5Fixture:
    """Paquete `dispatched` SIN recibo durable (precondición de PD-19)."""
    return _U5Fixture(tmp_path)


@pytest.fixture
def receipted_fx(tmp_path: Path) -> _U5Fixture:
    """El mismo paquete CON recibo durable (rechazo por contradicción)."""
    return _U5Fixture(tmp_path, durable_receipt=True)


# ---------------------------------------------------------------- PD-19 (a)


def test_pd19_a_disposition_marks_only_the_identified_packet_failed(
        dispatch_fx: _U5Fixture) -> None:
    """PD-19 (a): con la feature abierta y un despacho SIN recibo durable,
    `--transition disposition --packet <id> --resolution abandoned` → rc=0 y
    `active_packet.status: failed`.

    Sólo cambian `active_packet.status`, la entrada NUEVA de `stage_history` y
    `last_updated`; el resto del paquete queda intacto; la entrada lleva
    `transition: disposition`, `stage: dispatch-disposition`, `resolution`,
    `approval_effect: false`, `transition_key` y NO `approved_by`; `validate-state`
    VALID antes y después.

    RED hoy: rc=0 pero `active_packet.status` sigue `dispatched` (el efecto del
    `disposition` es `pass`) → falla la aserción del estado nuevo.
    """
    before = dispatch_fx.read_state()
    before_entries = entries(before)
    assert before["active_packet"]["status"] == "dispatched", (
        "precondición (fixture): el paquete está `dispatched`")
    assert dispatch_fx.receipt_path_for(dispatch_fx.packet_id).exists() is False, (
        "precondición (fixture): el despacho NO tiene recibo durable")
    assert_validate_green(dispatch_fx, "PD-19 (a) antes de la disposición")

    proc = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        "PD-19 violada (a): la disposición de un despacho sin recibo debe "
        f"registrarse (rc=0); rc={proc.returncode}: {out!r}")

    state = dispatch_fx.read_state()
    after_packet = state.get("active_packet") or {}
    assert after_packet.get("id") == dispatch_fx.packet_id, (
        "PD-19 violada (a): la disposición no debe cambiar el paquete "
        f"identificado ({dispatch_fx.packet_id!r}): {after_packet!r}")
    assert after_packet.get("status") == FAILED, (
        "PD-19 violada (a): el efecto del `disposition` sobre el paquete citado "
        f"es `status: {FAILED!r}` (terminal, sin recibo); visto "
        f"{after_packet.get('status')!r}")
    for field, value in before["active_packet"].items():
        if field == "status":
            continue
        assert after_packet.get(field) == value, (
            "PD-19 violada (a): el resto del paquete identificado queda "
            f"intacto; `active_packet.{field}` cambió: {value!r} → "
            f"{after_packet.get(field)!r}")

    untouched = sorted(
        key for key in set(state) | set(before)
        if key not in ("stage_history", "last_updated", "active_packet"))
    for key in untouched:
        assert state.get(key) == before.get(key), (
            "PD-19 violada (a): la disposición sólo escribe el paquete "
            f"identificado y su traza; `{key}` cambió: "
            f"{before.get(key)!r} → {state.get(key)!r}")

    after_entries = entries(state)
    assert after_entries[:len(before_entries)] == before_entries, (
        "PD-19 violada (a): la historia previa no se reescribe (append-only)")
    assert len(after_entries) == len(before_entries) + 1, (
        "PD-19 violada (a): la disposición deja UNA entrada nueva de "
        f"`stage_history` (antes {len(before_entries)}, después "
        f"{len(after_entries)})")

    entry = last_entry(state)
    assert entry.get("transition") == "disposition", (
        f"PD-19 violada (a): la entrada declara `transition: disposition`: {entry!r}")
    assert entry.get("stage") == DISPOSITION_STAGE, (
        "PD-19 violada (a): la etiqueta canónica de la disposición es "
        f"{DISPOSITION_STAGE!r}: {entry!r}")
    assert entry.get("packet_id") == dispatch_fx.packet_id, (
        "PD-19 violada (a): la entrada cita el paquete dispuesto: "
        f"{entry.get('packet_id')!r}")
    assert entry.get("resolution") == RESOLUTION_ABANDONED, (
        f"PD-19 violada (a): la entrada lleva la resolución: {entry!r}")
    assert entry.get("approval_effect") is False, (
        "PD-19 violada (a)/INV-1: la disposición NO aprueba nada "
        f"(`approval_effect: false`): {entry.get('approval_effect')!r}")
    assert not entry.get("approved_by"), (
        f"PD-19 violada (a): la disposición NO lleva `approved_by`: "
        f"{entry.get('approved_by')!r}")
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        f"PD-19 violada (a): la entrada lleva su `transition_key`: {key!r}")

    assert_validate_green(dispatch_fx, "PD-19 (a) después de la disposición")


# ---------------------------------------------------------------- PD-19 (b)


def test_pd19_b_identical_disposition_is_a_byte_identical_noop(
        dispatch_fx: _U5Fixture) -> None:
    """PD-19 (b): repetir la MISMA disposición → rc=0, sin segunda entrada y
    estado byte-idéntico al de la primera invocación.

    RED hoy: la primera invocación no deja el paquete `failed` (falla la
    precondición observable del no-op).
    """
    first = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out_first = first.stdout + first.stderr
    assert first.returncode == 0, (
        "PD-19 violada (b): la primera disposición debe registrarse (rc=0); "
        f"rc={first.returncode}: {out_first!r}")

    state_after_first = dispatch_fx.read_state()
    assert (state_after_first.get("active_packet") or {}).get(
        "status") == FAILED, (
        "PD-19 violada (b): la primera disposición deja el paquete "
        f"`{FAILED}` (precondición observable del no-op); visto "
        f"{(state_after_first.get('active_packet') or {}).get('status')!r}")
    entries_after_first = entries(state_after_first)
    bytes_after_first = dispatch_fx.state_bytes()

    repeat = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out_repeat = repeat.stdout + repeat.stderr

    assert repeat.returncode == 0, (
        "PD-19 violada (b): repetir la disposición idéntica es un no-op "
        f"EXITOSO (rc=0); rc={repeat.returncode}: {out_repeat!r}")
    assert entries(dispatch_fx.read_state()) == entries_after_first, (
        "PD-19 violada (b): la repetición idéntica NO agrega una segunda "
        f"entrada (sigue habiendo {len(entries_after_first)})")
    assert dispatch_fx.state_bytes() == bytes_after_first, (
        "PD-19 violada (b): el estado tras la repetición idéntica es byte a "
        "byte idéntico (no se reescribe)")
    assert_validate_green(dispatch_fx, "PD-19 (b) tras el no-op")


# ---------------------------------------------------------------- PD-19 prepare


def test_pd19_prepare_is_blocked_before_and_unblocked_after(
        dispatch_fx: _U5Fixture) -> None:
    """PD-19 (oráculo de `prepare`): con el paquete `dispatched` el `prepare`
    falla sin escribir; tras la disposición (`failed` no está en
    `ACTIVE_PACKET_STATUSES`) el `prepare` publica un paquete nuevo.

    RED hoy: tras la disposición el paquete sigue `dispatched`, así que el
    segundo `prepare` sigue bloqueado (rc≠0) en vez de publicar.
    """
    before_bytes = dispatch_fx.state_bytes()
    blocked = dispatch_fx.prepare_new()
    out_blocked = blocked.stdout + blocked.stderr
    assert blocked.returncode != 0, (
        "PD-19 violada: con el paquete `dispatched` un `prepare` nuevo debe "
        f"estar bloqueado; rc={blocked.returncode}: {out_blocked!r}")
    assert PACKET_BEGIN not in blocked.stdout, (
        "PD-19 violada: el `prepare` bloqueado no publica un paquete")
    assert dispatch_fx.state_bytes() == before_bytes, (
        "PD-19 violada: el `prepare` bloqueado no cambia el estado")

    disposed = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    assert disposed.returncode == 0, (
        "precondición: la disposición debe registrarse (rc=0): "
        f"{disposed.stdout!r} {disposed.stderr!r}")
    state = dispatch_fx.read_state()
    assert (state.get("active_packet") or {}).get("status") == FAILED, (
        "PD-19 violada: la disposición deja el paquete "
        f"`{FAILED}`; visto "
        f"{(state.get('active_packet') or {}).get('status')!r}")

    published = dispatch_fx.prepare_new()
    out_published = published.stdout + published.stderr
    assert published.returncode == 0, (
        "PD-19 violada: con el paquete `failed` (terminal) el `prepare` debe "
        f"quedar desbloqueado (rc=0); rc={published.returncode}: {out_published!r}")

    new_state = dispatch_fx.read_state()
    new_packet = new_state.get("active_packet") or {}
    assert new_packet.get("id") and new_packet.get("id") != dispatch_fx.packet_id, (
        "PD-19 violada: el `prepare` desbloqueado publica un paquete NUEVO: "
        f"{new_packet!r}")
    assert new_packet.get("status") == "prepared", (
        f"PD-19 violada: el paquete nuevo queda `prepared`: {new_packet!r}")
    assert_validate_green(dispatch_fx, "PD-19 prepare tras la disposición")


# ---------------------------------------------------------------- PD-19 recibo


def test_pd19_durable_receipt_rejection_names_receive(
        receipted_fx: _U5Fixture) -> None:
    """PD-19 (cláusula del recibo durable): si el paquete YA tiene recibo
    durable, la disposición se rechaza nombrando `receive`, sin efectos.

    GREEN hoy (guarda de 005-012/PD-21(iv)): se conserva como guarda de la
    condición de PD-19; no se le inventa un oráculo para forzar el RED.
    """
    assert receipted_fx.receipt_path_for(receipted_fx.packet_id).is_file(), (
        "precondición (fixture): el paquete tiene recibo durable")
    before_bytes = receipted_fx.state_bytes()

    proc = receipted_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0, (
        "PD-19 violada: con recibo durable la disposición se rechaza; "
        f"rc={proc.returncode}: {out!r}")
    assert "receive" in out.lower(), (
        "PD-19 violada: el rechazo NOMBRA `receive` como la ruta correcta "
        f"para la entrega que existe: {out!r}")
    assert names_any(
        out, receipted_fx.packet_id, RECEIPT_NAME, receipted_fx.execution_id), (
        "PD-19 violada: el rechazo nombra el paquete y/o el recibo que ya "
        f"existe: {out!r}")
    assert not _disposition_entries(receipted_fx.read_state()), (
        "PD-19 violada: el rechazo no deja entrada de disposición")
    assert receipted_fx.state_bytes() == before_bytes, (
        "PD-19 violada: el rechazo no cambia el estado (fallo cerrado)")


# ---------------------------------------------------------------- PD-19 (c)


def test_pd19_c_late_delivery_stays_registrable_on_the_same_failed_packet(
        dispatch_fx: _U5Fixture) -> None:
    """PD-19 (c): marcar `failed` no cierra la ruta `late-delivery`. Sobre el
    MISMO paquete: disposición → `failed`; la feature se cierra por el camino
    legítimo (la disposición satisface la entrega requerida); el recibo llega
    tarde (`receive --late`) y `late-delivery` se registra (rc=0) con su traza
    sin reabrir ni aprobar la feature.

    RED hoy: tras la disposición el paquete sigue `dispatched` (falla la
    aserción del estado nuevo que precede al recorrido tardío).
    """
    disposed = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out_disposed = disposed.stdout + disposed.stderr
    assert disposed.returncode == 0, (
        "PD-19 violada (c): la disposición debe registrarse (rc=0); "
        f"rc={disposed.returncode}: {out_disposed!r}")
    state = dispatch_fx.read_state()
    assert (state.get("active_packet") or {}).get("status") == FAILED, (
        "PD-19 violada (c): el paquete queda "
        f"`{FAILED}` antes del recorrido tardío; visto "
        f"{(state.get('active_packet') or {}).get('status')!r}")

    closed = dispatch_fx.closure()
    out_closed = closed.stdout + closed.stderr
    assert closed.returncode == 0, (
        "PD-19 violada (c): la disposición satisface la entrega requerida y la "
        f"feature se cierra por el camino legítimo (rc=0); rc={closed.returncode}: "
        f"{out_closed!r}")
    closed_state = dispatch_fx.read_state()
    assert (_feature_entry(closed_state, FEATURE_ID) or {}).get(
        "status") == FEATURE_CLOSED, (
        "precondición/PD-19 (c): la feature queda cerrada")
    assert closed_state.get("current_stage") == IDLE, (
        f"precondición/PD-19 (c): el cierre deja reposo ({IDLE!r})")

    dispatch_fx.stage_late_delivery()
    late_receipt = dispatch_fx.receive_late()
    out_receipt = late_receipt.stdout + late_receipt.stderr
    assert late_receipt.returncode == 0, (
        "PD-19 violada (c): el recibo tardío del mismo paquete se persiste "
        f"(`receive --late`, rc=0); rc={late_receipt.returncode}: {out_receipt!r}")
    assert dispatch_fx.receipt_path_for(dispatch_fx.packet_id).is_file(), (
        "PD-19 violada (c): el recibo durable del paquete tardío existe")

    trace = dispatch_fx.late_delivery()
    out_trace = trace.stdout + trace.stderr
    assert trace.returncode == 0, (
        "PD-19 violada (c): `late-delivery` sigue registrable sobre el mismo "
        f"paquete marcado `{FAILED}` (rc=0); rc={trace.returncode}: {out_trace!r}")

    after = dispatch_fx.read_state()
    late_entries = _late_entries(after)
    assert len(late_entries) == 1, (
        "PD-19 violada (c): la entrega tardía deja UNA traza: "
        f"{late_entries!r}")
    entry = late_entries[0]
    assert entry.get("packet_id") == dispatch_fx.packet_id, (
        "PD-19 violada (c): la traza cita el MISMO paquete: "
        f"{entry.get('packet_id')!r}")
    assert entry.get("approval_effect") is False and not entry.get("approved_by"), (
        f"PD-19 violada (c): la entrega tardía no aprueba nada: {entry!r}")
    assert (_feature_entry(after, FEATURE_ID) or {}).get(
        "status") == FEATURE_CLOSED, (
        "PD-19 violada (c): la entrega tardía no reabre la feature")
    assert after.get("active_feature") is None, (
        "PD-19 violada (c): la entrega tardía no reabre el ciclo activo")
    assert_validate_green(dispatch_fx, "PD-19 (c) tras la entrega tardía")


# ---------------------------------------------------------------- PD-19 (d)


def test_pd19_d_failed_is_a_state_mark_and_reconcile_stays_read_only(
        dispatch_fx: _U5Fixture) -> None:
    """PD-19 (d): `failed` no detiene ningún worker ni proceso remoto: es una
    marca de estado. Lo observable —la disposición no escribe nada más que
    `docs/.cdad-state.json` (ni recibo, ni ledger, ni pid)— y antes de repetir
    el encargo `reconcile` sigue siendo de SOLO LECTURA sobre ese paquete:
    rc=0, sobre JSON con su `packet_id`, estado byte-idéntico.

    RED hoy: el estado nuevo no aparece (falla la aserción `failed`).
    """
    before_tree = _tree(dispatch_fx.root)
    disposed = dispatch_fx.disposition("--resolution", RESOLUTION_ABANDONED)
    out = disposed.stdout + disposed.stderr
    assert disposed.returncode == 0, (
        f"PD-19 violada (d): la disposición se registra (rc=0); rc={disposed.returncode}: "
        f"{out!r}")
    state = dispatch_fx.read_state()
    assert (state.get("active_packet") or {}).get("status") == FAILED, (
        "PD-19 violada (d): el paquete queda "
        f"`{FAILED}`; visto "
        f"{(state.get('active_packet') or {}).get('status')!r}")

    after_tree = _tree(dispatch_fx.root)
    assert _tree_delta(before_tree, after_tree) == {STATE_REL}, (
        "PD-19 violada (d): la disposición sólo escribe el estado; el delta del "
        f"árbol es {sorted(_tree_delta(before_tree, after_tree))!r} "
        f"(esperado [{STATE_REL!r}]: sin recibo, sin ledger, sin pid)")

    before_reconcile = dispatch_fx.state_bytes()
    reconciled = dispatch_fx.reconcile()
    out_reconcile = reconciled.stdout + reconciled.stderr
    assert reconciled.returncode == 0, (
        "PD-19 violada (d)/D-6 fila 2: `reconcile` sobre el paquete "
        f"`{FAILED}` es de solo lectura y termina (rc=0); rc="
        f"{reconciled.returncode}: {out_reconcile!r}")
    envelope = json.loads(reconciled.stdout)
    assert envelope.get("packet_id") == dispatch_fx.packet_id, (
        "PD-19 violada (d): `reconcile` reporta el paquete dispuesto: "
        f"{envelope.get('packet_id')!r}")
    assert dispatch_fx.state_bytes() == before_reconcile, (
        "PD-19 violada (d): `reconcile` es read-only y no reescribe el estado")
