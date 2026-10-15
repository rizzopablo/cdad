#!/usr/bin/env python3
"""005-001 T3 RED — Reposo legítimo y estado incoherente (PD-13, PD-14,
PD-15 y el slice «state incoherent» de PD-12).

Contract:
- docs/specs/005-001-idle-and-v7-bootstrap/spec.md §2 (PD-13, PD-14, PD-15;
  slice PD-12 de la condición `state incoherent`), §3 (invariante de
  coherencia de reposo: active_feature == null ⟺ current_stage == "idle")
  y §7 D5 (el oráculo usa el token "idle").
- docs/specs/005-001-idle-and-v7-bootstrap/plan.md (T3; test focal declarado
  `tests/test_005_001_t3_idle.py`).

Superficie observable bajo prueba (§2, caja negra por subprocess sobre el
entrypoint del repo — nunca se importa el módulo):

    python3 scripts/cdad_packet.py validate-state --project-root R

Marcador de diagnóstico (PD-12): `state incoherent` (el state contradice
sus propios registros), estable y observable en stderr con rc=2.

Contrato observable:
- PD-13: state en reposo legítimo (active_feature null + current_stage
  "idle", conservando el bloque `execution` de la última feature y/o un
  `active_packet` terminal completed|failed) → rc=0 y stdout declara VALID
  con el token "idle".
- PD-14: (a) active_feature null con current_stage != "idle" → rc=2 con
  `state incoherent` en stderr; (b) active_feature no nulo con
  current_stage == "idle" → rc=2 con `state incoherent`.
- PD-15: active_feature null + current_stage "idle" + active_packet.status
  en {prepared, dispatched} → rc=2 con `state incoherent` (un paquete en
  vuelo no coexiste con el reposo).
- PD-12 (slice reposo): en cada rechazo rc=2, el stderr contiene el
  marcador `state incoherent`, nombra el registro concreto contradicho y la
  acción legítima siguiente, sin efectos: state y árbol byte a byte
  idénticos; los marcadores son mutuamente excluyentes por condición.

Fixtures (patrón ya existente en tests/test_005_001_t2_replace_packet.py y
tests/test_004_002_t2_reviewfix.py): proyectos sintéticos en tempdirs;
el reposo se construye por interfaz pública — proyecto activo válido
(política, spec pineada, fuente de autoridad, delegación HITL) +
`prepare` (rc=0, precondición del fixture) + mutación del fixture a
reposo (active_feature null, current_stage "idle", feature done,
paquete terminal/in-vuelo), conservando el binding `state.execution` y el
paquete REALES publicados en disco por prepare. Ninguna escritura en este
repo y ninguna lectura de implementación
(skills/cdad-cycle/scripts/cdad_packet.py).

RED hoy (probe sobre un proyecto sintético, caja negra): `validate-state`
exige un binding de ejecución activo — con el bloque `execution` de la
última feature conservado y el reposo declarado rechaza con
`active_feature None does not match the execution feature '<feature>'`
(rc=2); con execution vacío rechaza `state.execution is empty`; y si el
state nombra una ejecución sin documento en disco, `execution context not
found`. En ningún caso aparece el marcador `state incoherent`. Cada test
preverifica el control positivo interno (el reposo aceptado es
precondición de los negativos) y después afirma la postcondición; todo
fallo RED debe ser una AssertionError de comportamiento, nunca ImportError
ni SyntaxError.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-005-real-operation"
FEATURE_ID = "005-001-idle-and-v7-bootstrap"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"

SPEC_BYTES = b"# Spec fixture (005-001 T3)\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()

APPROVER = "Pablo"
OBJECTIVE = "005-001 T3 objective"
ROLE, SUBSTAGE = "test-writer", "red"
IDLE = "idle"
VALID_TOKEN = "VALID"
INCOHERENT_MARKER = "state incoherent"
PENDING_MARKER = "approval pending"
OBSOLETE_MARKER = "packet obsolete"


# ---------------------------------------------------------------- fixtures


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def prepare(root: Path, *, role: str = ROLE, substage: str = SUBSTAGE,
            objective: str = OBJECTIVE) -> subprocess.CompletedProcess:
    return run_cli([
        "prepare", "--project-root", str(root),
        "--role", role, "--substage", substage,
        "--objective", objective,
    ])


def run_validate_state(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return run_cli(["validate-state", "--project-root", str(root), *extra])


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


def state_bytes(root: Path) -> bytes:
    return (root / STATE_FILE).read_bytes()


def read_state(root: Path) -> dict:
    return json.loads(state_bytes(root).decode("utf-8"))


def write_state(root: Path, state: dict) -> None:
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")


def write_policy(root: Path) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / POLICY_FILE).write_text(json.dumps({
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def spec_approval_entry() -> dict:
    """Entrada pineada de especificación (D3: path + sha256 obligatorios)."""
    return {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": APPROVER,
        "approved_at": "2026-10-08T00:00:00Z",
        "contract_path": SPEC_FILE,
        "contract_sha256": SPEC_SHA256,
    }


def write_base_project(root: Path) -> None:
    """Proyecto sintético válido (política + spec pineada + fuente de
    autoridad + delegación HITL activa), feature activa en tdd/red."""
    root.mkdir(parents=True)
    for rel in ("tests", "src", "lib"):
        (root / rel).mkdir(exist_ok=True)
    write_policy(root)
    spec = root / SPEC_FILE
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_bytes(SPEC_BYTES)
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-005)\n",
                         encoding="utf-8")
    write_state(root, {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": [],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [spec_approval_entry()],
        "approver": APPROVER,
        "last_updated": "2026-10-08T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        },
    })


def build_idle_project(root: Path, *,
                       execution_mode: str = "preserved",
                       packet_status: str | None = "completed",
                       current_stage: str = IDLE,
                       active_feature: str | None = None) -> Path:
    """Proyecto sintético en REPOSO (o mutación incoherente), construido
    por interfaz pública: proyecto activo válido + `prepare` (precondición
    del fixture) + mutación del fixture a reposo con el binding y el
    paquete reales publicados en disco.

    - execution_mode: "preserved" conserva el bloque `execution` de la
      última feature (PD-13, remanente tolerado); "none" lo vacía.
    - packet_status: "completed"/"failed" (terminal, tolerado), None
      (sin paquete activo) o "prepared"/"dispatched" (en vuelo, PD-15).
    - current_stage/active_feature: para las mutaciones PD-14.
    """
    write_base_project(root)
    proc = prepare(root)
    assert proc.returncode == 0, (
        f"precondición (fixture): la aprobación pineada vigente debe "
        f"habilitar prepare: {proc.stdout!r} {proc.stderr!r}")
    state = read_state(root)
    assert (state.get("active_packet") or {}).get("status") == "prepared", (
        f"precondición (fixture): paquete activo prepared: "
        f"{state.get('active_packet')!r}")
    assert (state.get("execution") or {}).get("feature_id") == FEATURE_ID, (
        f"precondición (fixture): binding de ejecución: "
        f"{state.get('execution')!r}")
    # Mutación del fixture a reposo legítimo (o su variante incoherente):
    # la feature terminó; el binding `execution` y el paquete permanecen
    # como registros reales en disco.
    state["active_feature"] = active_feature
    state["current_stage"] = current_stage
    state["tdd_substage"] = None
    state["epic_features"] = [{"id": FEATURE_ID, "status": "done"}]
    if execution_mode == "none":
        state["execution"] = None
    elif execution_mode != "preserved":
        raise AssertionError(
            f"fixture: execution_mode desconocido: {execution_mode!r}")
    if packet_status is None:
        state["active_packet"] = None
    else:
        assert state.get("active_packet"), (
            "fixture: prepare no dejó paquete activo")
        state["active_packet"]["status"] = packet_status
    write_state(root, state)
    return root


def incoherent_state(case: str, base: dict) -> dict:
    """Mutación incoherente declarada por PD-14/PD-15 sobre el reposo base."""
    state = copy.deepcopy(base)
    if case == "null-feature-non-idle-stage":        # PD-14 (a)
        state["current_stage"] = "tdd"
    elif case == "active-feature-with-idle-stage":   # PD-14 (b)
        state["active_feature"] = FEATURE_ID
    else:
        raise AssertionError(f"fixture: caso incoherente desconocido: {case}")
    return state


# Tokens que identifican el registro concreto contradicho (PD-12: el
# diagnóstico nombra el registro), por caso.
RECORD_TOKENS: dict[str, tuple[str, ...]] = {
    "null-feature-non-idle-stage": ("current_stage", "tdd", "active_feature"),
    "active-feature-with-idle-stage": ("active_feature", FEATURE_ID,
                                       "current_stage"),
    "idle-with-prepared-packet": ("active_packet", "prepared"),
    "idle-with-dispatched-packet": ("active_packet", "dispatched"),
}


def assert_valid_idle(label: str, proc: subprocess.CompletedProcess) -> None:
    """PD-13: rc=0 y stdout declara VALID declarando el reposo con el
    token "idle" (D5)."""
    assert proc.returncode == 0, (
        f"{label}: validate-state debe aceptar el reposo legítimo (rc=0): "
        f"{proc.stdout!r} {proc.stderr!r}")
    assert VALID_TOKEN in proc.stdout, (
        f"{label}: stdout sin {VALID_TOKEN!r}: {proc.stdout!r}")
    assert IDLE in proc.stdout, (
        f"{label}: stdout no declara el reposo con el token {IDLE!r} (D5): "
        f"{proc.stdout!r}")


def assert_no_writes(label: str, root: Path, before: dict,
                     state_before: bytes) -> None:
    """Ninguna escritura: árbol y state byte a byte idénticos tras la
    invocación (PD-12: «no hay efectos»)."""
    assert tree_snapshot(root) == before, (
        f"{label}: hubo escrituras (árbol modificado)")
    assert state_bytes(root) == state_before, (
        f"{label}: el state cambió")


def assert_rejection(label: str, root: Path, before: dict,
                     state_before: bytes,
                     proc: subprocess.CompletedProcess) -> None:
    """Rechazo PD-12 (slice reposo): rc=2, stdout vacío, sin traceback,
    marcador `state incoherent` y sin los marcadores de las otras
    condiciones (exclusividad), sin efectos."""
    out = proc.stdout + proc.stderr
    assert proc.returncode == 2, (
        f"{label}: rc esperado 2: {out!r}")
    assert proc.stdout == "", (
        f"{label}: el rechazo imprimió contenido por stdout: {proc.stdout!r}")
    assert "Traceback" not in proc.stderr, (
        f"{label}: fallo con traceback: {proc.stderr!r}")
    assert INCOHERENT_MARKER in proc.stderr, (
        f"{label}: stderr sin el marcador {INCOHERENT_MARKER!r}: "
        f"{proc.stderr!r}")
    for banned in (PENDING_MARKER, OBSOLETE_MARKER):
        assert banned not in out, (
            f"{label}: el marcador {INCOHERENT_MARKER!r} se mezcló con el "
            f"marcador {banned!r} (PD-12: exclusivos por condición): {out!r}")
    assert_no_writes(label, root, before, state_before)


class T3Case(unittest.TestCase):
    """Base: proyecto sintético en tempdir propio por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-001-t3-")
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", self._tmp], check=False)

    def make_idle_project(self, **build_kwargs) -> Path:
        tmp = tempfile.mkdtemp(prefix="cdad-005-001-t3-", dir=self._tmp)
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", tmp], check=False)
        return build_idle_project(Path(tmp) / "proj", **build_kwargs)

    def make_incoherent_project(self, case: str) -> Path:
        """Proyecto con la mutación incoherente de PD-14/PD-15 aplicada."""
        if case == "idle-with-prepared-packet":          # PD-15 (prepared)
            return self.make_idle_project(packet_status="prepared")
        if case == "idle-with-dispatched-packet":        # PD-15 (dispatched)
            return self.make_idle_project(packet_status="dispatched")
        root = self.make_idle_project()
        write_state(root, incoherent_state(case, read_state(root)))
        return root

    def assert_idle_accepted(self, root: Path, label: str) -> None:
        """Control positivo interno (PD-13): el reposo base es aceptado."""
        assert_valid_idle(label, run_validate_state(root))


# ---------------------------------------------------------------- PD-13


class TestPd13LegitimateIdleAccepted(T3Case):
    """PD-13: con `active_feature == null` y `current_stage == "idle"`, un
    state que conserva el bloque `execution` de la última feature (y/o un
    `active_packet` terminal `completed|failed`) → `validate-state` rc=0
    con salida VALID que declara el reposo (token "idle", D5)."""

    def test_pd13_idle_state_with_execution_remnant_or_terminal_packet_valid(self) -> None:
        variants = (
            ("bloque execution conservado, sin paquete",
             dict(execution_mode="preserved", packet_status=None)),
            ("bloque execution conservado + paquete completed",
             dict(execution_mode="preserved", packet_status="completed")),
            ("solo paquete completed (sin execution)",
             dict(execution_mode="none", packet_status="completed")),
            ("solo paquete failed (sin execution)",
             dict(execution_mode="none", packet_status="failed")),
        )
        for label, kwargs in variants:
            with self.subTest(caso=label):
                root = self.make_idle_project(**kwargs)
                state = read_state(root)
                assert state["active_feature"] is None, (
                    f"fixture ({label}): active_feature debe ser null")
                assert state["current_stage"] == IDLE, (
                    f"fixture ({label}): current_stage debe ser 'idle'")
                proc = run_validate_state(root)
                assert_valid_idle(f"PD-13 ({label})", proc)


# ---------------------------------------------------------------- PD-14


class TestPd14IncoherentStateRejected(T3Case):
    """PD-14: (a) `active_feature == null` con `current_stage` distinto de
    "idle" → rc=2 con `state incoherent`; (b) `active_feature` no nulo con
    `current_stage == "idle"` → rc=2 con `state incoherent`. Control
    positivo interno: el reposo base equivalente (sin la mutación) es
    aceptado (PD-13). El negativo se afirma PRIMERO para que el RED nombre
    el diagnóstico faltante (hoy rc=2 con mensaje genérico de binding, sin
    el marcador); el control (RED hoy también, depende de PD-13) corre
    después."""

    def test_pd14_null_feature_non_idle_stage_and_active_feature_idle_rejected(self) -> None:
        cases = (
            ("active_feature null con current_stage 'tdd'",
             "null-feature-non-idle-stage"),
            ("active_feature no nulo con current_stage 'idle'",
             "active-feature-with-idle-stage"),
        )
        for label, case in cases:
            with self.subTest(caso=label):
                root = self.make_incoherent_project(case)
                before = tree_snapshot(root)
                state_before = state_bytes(root)
                proc = run_validate_state(root)
                assert_rejection(f"PD-14 ({label})", root, before,
                                 state_before, proc)
                # Control positivo interno: el mismo fixture SIN la
                # mutación (reposo legítimo) es aceptado (PD-13).
                control = self.make_idle_project()
                self.assert_idle_accepted(
                    control, f"PD-14 ({label}) [control]")


# ---------------------------------------------------------------- PD-15


class TestPd15IdleWithPacketInFlightRejected(T3Case):
    """PD-15: `active_feature == null`, `current_stage == "idle"`, pero
    `active_packet.status ∈ {prepared, dispatched}` → rc=2 con `state
    incoherent` (un paquete en vuelo no coexiste con el reposo). Control
    positivo interno: el reposo con paquete TERMINAL es aceptado (PD-13).
    El negativo se afirma PRIMERO (hoy rc=2 con mensaje genérico de
    binding, sin el marcador); el control corre después."""

    def test_pd15_idle_with_prepared_or_dispatched_packet_rejected(self) -> None:
        cases = (
            ("active_packet prepared", "idle-with-prepared-packet"),
            ("active_packet dispatched", "idle-with-dispatched-packet"),
        )
        for label, case in cases:
            with self.subTest(caso=label):
                root = self.make_incoherent_project(case)
                state = read_state(root)
                assert state["active_packet"].get("status") in (
                    "prepared", "dispatched"), (
                    f"fixture ({label}): paquete en vuelo: "
                    f"{state['active_packet']!r}")
                before = tree_snapshot(root)
                state_before = state_bytes(root)
                proc = run_validate_state(root)
                assert_rejection(f"PD-15 ({label})", root, before,
                                 state_before, proc)
                # Control positivo interno: el mismo fixture con el
                # paquete TERMINAL (reposo legítimo) es aceptado (PD-13).
                control = self.make_idle_project(packet_status="completed")
                self.assert_idle_accepted(
                    control, f"PD-15 ({label}) [control: paquete terminal]")


# ------------------------------------------------------ PD-12 (slice T3)


class TestPd12StateIncoherentMarker(T3Case):
    """PD-12 (slice T3, condición `estado incoherente`): en cada rechazo
    rc=2 el stderr contiene el marcador `state incoherent`, nombra el
    registro concreto que se contradice y la acción legítima siguiente, y
    NO hay efectos: el state y el árbol del fixture quedan byte a byte
    idénticos tras la invocación; los marcadores son mutuamente excluyentes
    por condición."""

    def test_pd12_state_incoherent_names_record_and_next_action_without_effects(self) -> None:
        cases = (
            ("active_feature null con current_stage 'tdd'",
             "null-feature-non-idle-stage"),
            ("active_feature no nulo con current_stage 'idle'",
             "active-feature-with-idle-stage"),
            ("reposo con active_packet prepared",
             "idle-with-prepared-packet"),
            ("reposo con active_packet dispatched",
             "idle-with-dispatched-packet"),
        )
        for label, case in cases:
            with self.subTest(caso=label):
                root = self.make_incoherent_project(case)
                before = tree_snapshot(root)
                state_before = state_bytes(root)
                proc = run_validate_state(root)
                assert_rejection(f"PD-12 ({label})", root, before,
                                 state_before, proc)
                # Nombra el registro concreto contradicho (al menos uno de
                # los campos/valores involucrados en la contradicción).
                named = [token for token in RECORD_TOKENS[case]
                         if token in proc.stderr]
                self.assertTrue(
                    named,
                    msg=f"PD-12 ({label}): el diagnóstico no nombra el "
                        f"registro concreto contradicho "
                        f"({RECORD_TOKENS[case]}): {proc.stderr!r}")
                # Acción legítima siguiente: nombrar el registro a reparar
                # (el state del proyecto).
                self.assertIn(
                    ".cdad-state.json", proc.stderr,
                    msg=f"PD-12 ({label}): el diagnóstico no nombra el "
                        f"registro a reparar (el state del proyecto) como "
                        f"acción legítima siguiente: {proc.stderr!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
