#!/usr/bin/env python3
"""005-001 T1 RED — Modelo de autorización por rol (corrige I2 circular).

Contract:
- docs/specs/005-001-idle-and-v7-bootstrap/spec.md (PD-1..PD-6; slice PD-12
  del marcador `approval pending`).
- docs/specs/005-001-idle-and-v7-bootstrap/plan.md (T1; test focal declarado
  `tests/test_005_001_t1_role_approval.py`).

Superficie observable bajo prueba (§2 del contrato; nada de plomería):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --role <rol> --substage <sub> --objective <texto>

Registros de aprobación (§2, decisiones D1/D2/D3):
- spec (roles de construcción): entrada de `stage_history`
  {feature, stage: "specification", approved_by no vacío,
   contract_path, contract_sha256} — pin obligatorio.
- plan del epic (architect): entrada de `epic_history`
  {epic, stage: "epic-plan", approved_by no vacío} — sin pin.

Marcador diagnóstico (PD-12): stderr de rc=2 contiene `approval pending`,
nombra el registro faltante y la spec, y no altera el state ni publica
archivos; no mezcla los otros marcadores (`packet obsolete`,
`state incoherent`).

RED hoy: la implementación vigente es rol-agnóstica (I2 circular: exige la
entrada `specification` también para architect y no verifica el pin). Cada
test de comportamiento ausente fracasa por AssertionError:
- PD-1: con plan del epic aprobado, hoy rc=2 (se exige rc=0).
- PD-2: con aprobación de spec, hoy architect pasa con rc=0 (se exige rc=2).
- PD-3/PD-12: hoy rc=2 pero SIN el marcador `approval pending`.
- PD-4: hoy el drift del contrato NO invalida la aprobación (rc=0 en vez de 2).
- PD-5/PD-6 ya hoy se comportan conforme el contrato: quedan como control
  positivo/regresión anclado a la postcondición (control positivo interno
  del criterio de aceptación; no se fuerzan para no debilitar el contrato).

Fixtures offline: proyectos sintéticos en tempdirs (política válida, spec
y/o plan del epic, delegación HITL activa); ninguna escritura en este repo y
ninguna lectura de implementación.
"""

from __future__ import annotations

import hashlib
import json
import re
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
PLAN_FILE = f"docs/epics/{EPIC_ID}/plan.md"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
PLAN_BYTES = b"# Epic plan fixture (005-001 T1)\n"
SPEC_BYTES = b"# Spec fixture (005-001 T1)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada tras la aprobacion\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()
SPEC_DRIFT_SHA256 = hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest()

APPROVER = "Pablo"
MARKER = "approval pending"
CONSTRUCTION_ROLES = (
    ("test-writer", "red"),
    ("implementer", "green"),
    ("reviewer", "review"),
)
PACKET_BEGIN = "---cdad-packet-json"


# ---------------------------------------------------------------- fixtures


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def prepare(plan_root: Path, *, role: str, substage: str,
            objective: str = "005-001 T1 objective") -> subprocess.CompletedProcess:
    return run_cli([
        "prepare", "--project-root", str(plan_root),
        "--role", role, "--substage", substage,
        "--objective", objective,
    ])


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


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


def spec_approval_entry(*, feature: str = FEATURE_ID) -> dict:
    """Entrada pineada de especificación (D3: path + sha256 obligatorios)."""
    return {
        "feature": feature,
        "stage": "specification",
        "approved_by": APPROVER,
        "approved_at": "2026-10-08T00:00:00Z",
        "contract_path": SPEC_FILE,
        "contract_sha256": SPEC_SHA256,
    }


def epic_plan_entry() -> dict:
    """Aprobación del plan del epic (D1/D2: sin pin de hash)."""
    return {
        "epic": EPIC_ID,
        "stage": "epic-plan",
        "approved_by": APPROVER,
        "approved_at": "2026-10-08T00:00:00Z",
    }


def rectified_entry() -> dict:
    """Entrada histórica rectificada, de otro vocabulario (INV-6/PD-6): no
    habilita autoridad para ningún rol (no es `epic-plan` ni
    `specification`)."""
    return {
        "stage": "discovery-authorization",
        "authorized_by": APPROVER,
        "rectified_at": "2026-10-08T00:00:00Z",
    }


def build_project(
    root: Path,
    *,
    spec_approval: dict | None = None,
    epic_plan: bool = False,
    write_spec_file: bool = True,
    spec_drift: bool = False,
) -> Path:
    """Proyecto sintético de 005-001 T1.

    - `spec_approval`: entrada de `stage_history` a insertar
      (spec_approval_entry()/None).
    - `epic_plan`: inserta la aprobación del plan del epic en
      `epic_history` y escribe el plan fixture.
    - `write_spec_file`: escribe (o no) el spec fixture en su ruta.
    - `spec_drift`: edita el spec después de "aprobar" (deriva el sha).
    """
    root.mkdir(parents=True)
    for rel in ("tests", "src", "lib"):
        (root / rel).mkdir(exist_ok=True)
    write_policy(root)
    plan = root / PLAN_FILE
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_bytes(PLAN_BYTES)
    if write_spec_file:
        spec = root / SPEC_FILE
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_bytes(SPEC_DRIFT_BYTES if spec_drift else SPEC_BYTES)
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-005)\n",
                         encoding="utf-8")
    stage_history = [spec_approval] if spec_approval is not None else []
    state = {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": [epic_plan_entry()] if epic_plan else [],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": stage_history,
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
    }
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    return root


def make_project(**kwargs) -> Path:
    return build_project(Path(tempfile.mkdtemp(
        prefix="cdad-005-001-t1-")) / "proj", **kwargs)


def v2_execution_ids(root: Path) -> dict[str, dict]:
    base = root / ".cdad" / "executions"
    if not base.is_dir():
        return {}
    return {path.parent.name: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(base.glob("*/execution.json"))}


def published_packets(root: Path) -> dict[str, bytes]:
    base = root / ".cdad" / "packets"
    if not base.is_dir():
        return {}
    return {path.parent.name: path.read_bytes()
            for path in sorted(base.glob("*/PACKET.md"))}


class T1Case(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-001-t1-tests-")
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", self._tmp], check=False)

    def assert_no_effects(self, project: Path, before: dict,
                          state_before: bytes, *,
                          label: str, stderr: str,
                          rc: int, expect_rc: int = 2,
                          expect_marker: bool = True) -> None:
        """rc/marcador esperados y ninguna publicación (árbol y state
        byte a byte idénticos; PD-2/PD-3/PD-12 «sin efectos»)."""
        self.assertEqual(
            rc, expect_rc,
            msg=f"{label}: rc esperado {expect_rc}, visto {rc}: {stderr!r}")
        if expect_marker:
            self.assertIn(
                MARKER, stderr,
                msg=f"{label}: stderr sin el marcador {MARKER!r}: {stderr!r}")
        self.assertEqual(
            tree_snapshot(project), before,
            msg=f"{label}: hubo publicación parcial (árbol modificado)")
        self.assertEqual(
            (project / STATE_FILE).read_bytes(), state_before,
            msg=f"{label}: el state cambió en un caso de fallo")


# ---------------------------------------------------------------- PD-1


class TestPd1ArchitectEnabledByEpicPlan(T1Case):
    """PD-1: con epic activo E y entrada `epic-plan` aprobada en
    `epic_history`, `prepare --role architect` (subfase válida) → rc=0,
    publica contexto v2 + paquete, SIN requerir entrada `specification`
    de la feature."""

    def test_pd1_architect_prepares_with_epic_plan_only(self) -> None:
        project = make_project(epic_plan=True)
        proc = prepare(project, role="architect", substage="discovery")
        combined = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-1: el architect con plan de epic aprobado debe "
                f"prepararse sin aprobación de spec: {combined!r}")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="PD-1: stdout no comienza con el paquete canónico")
        # contexto v2 publicado + binding en state
        docs = v2_execution_ids(project)
        self.assertEqual(
            len(docs), 1, msg=f"PD-1: contextos publicados: {sorted(docs)}")
        execution_id, document = next(iter(docs.items()))
        self.assertEqual(
            document.get("schema_version"), 2,
            msg=f"PD-1: el contexto no es v2: {document.get('schema_version')!r}")
        binding = document.get("execution", document)
        self.assertEqual(
            binding.get("feature_id"), FEATURE_ID,
            msg=f"PD-1: feature en el contexto: {binding.get('feature_id')!r}")
        self.assertEqual(
            json.loads((project / STATE_FILE).read_text(encoding="utf-8"))
            .get("execution", {}).get("id"), execution_id,
            msg="PD-1: state.execution no referencia el contexto creado")
        # paquete publicado y byte-idéntico al stdout
        packets = published_packets(project)
        self.assertEqual(
            len(packets), 1, msg=f"PD-1: paquetes publicados: {sorted(packets)}")
        self.assertEqual(
            next(iter(packets.values())).decode("utf-8"), proc.stdout,
            msg="PD-1: PACKET.md difiere del stdout de prepare")


# ---------------------------------------------------------------- PD-2


class TestPd2ArchitectNotEnabledBySpecApproval(T1Case):
    """PD-2: sin la entrada `epic-plan` de E, aunque exista una entrada
    `specification` con approved_by, `prepare --role architect` → rc=2 con
    marcador `approval pending` que nombra el plan del epic; sin efectos."""

    def test_pd2_architect_with_spec_approval_only_is_rejected(self) -> None:
        # La aprobación de spec está presente en su forma MÁS fuerte (entrada
        # pineada y archivo coincidente): lo único ausente es el plan del epic.
        project = make_project(spec_approval=spec_approval_entry())
        before = tree_snapshot(project)
        state_before = (project / STATE_FILE).read_bytes()
        proc = prepare(project, role="architect", substage="discovery")
        stderr = proc.stderr
        self.assert_no_effects(
            project, before, state_before, label="PD-2",
            stderr=stderr, rc=proc.returncode)
        self.assertRegex(
            stderr, r"(?i)plan del epic|epic[-_ ]plan",
            msg=f"PD-2: el diagnóstico no nombra el plan del epic: {stderr!r}")


# ---------------------------------------------------------------- PD-3


class TestPd3ConstructionRolesBlockedWithoutSpecApproval(T1Case):
    """PD-3: sin entrada `specification` cuyo contract_sha256 coincida con
    sha256(docs/specs/<feature>/spec.md), `prepare` para
    test-writer|implementer|reviewer → rc=2, marcador `approval pending`,
    nombra stage_history/specification/approved y la ruta de la spec; el
    árbol y el state quedan idénticos."""

    def test_pd3_construction_role_blocked_names_missing_spec_approval(self) -> None:
        # El plan del epic SÍ está aprobado (hoy no alcanza) y el archivo de
        # la spec existe: lo único que falta es la aprobación pineada de la
        # spec en stage_history (el negativo es exactamente ese registro).
        for role, substage in CONSTRUCTION_ROLES:
            with self.subTest(role=role, substage=substage):
                project = make_project(epic_plan=True)
                before = tree_snapshot(project)
                state_before = (project / STATE_FILE).read_bytes()
                proc = prepare(project, role=role, substage=substage)
                stderr = proc.stderr
                self.assert_no_effects(
                    project, before, state_before, label=f"PD-3 {role}",
                    stderr=stderr, rc=proc.returncode)
                self.assertRegex(
                    stderr, r"stage_history|specification|approved",
                    msg=f"PD-3 {role}: el diagnóstico no nombra el registro "
                        f"faltante: {stderr!r}")
                self.assertIn(
                    SPEC_FILE, stderr,
                    msg=f"PD-3 {role}: el diagnóstico no nombra la ruta de la "
                        f"spec: {stderr!r}")


# ---------------------------------------------------------------- PD-4


class TestPd4ContractDriftInvalidatesApproval(T1Case):
    """PD-4: si la entrada `specification` existe con pin y luego se edita
    `spec.md` (el sha deja de coincidir), `prepare` para los roles de
    construcción → rc=2 `approval pending`, nombrando el digest registrado y
    el actual."""

    def test_pd4_drifted_contract_blocks_construction_role(self) -> None:
        # La entrada aprobó los bytes ORIGINALES; el archivo se edita después.
        project = make_project(
            spec_approval=spec_approval_entry(), spec_drift=True)
        before = tree_snapshot(project)
        state_before = (project / STATE_FILE).read_bytes()
        proc = prepare(project, role="test-writer", substage="red")
        stderr = proc.stderr
        self.assert_no_effects(
            project, before, state_before, label="PD-4",
            stderr=stderr, rc=proc.returncode)
        self.assertIn(
            SPEC_SHA256, stderr,
            msg=f"PD-4: el diagnóstico no nombra el digest registrado: "
                f"{stderr!r}")
        self.assertIn(
            SPEC_DRIFT_SHA256, stderr,
            msg=f"PD-4: el diagnóstico no nombra el digest actual: {stderr!r}")


# ---------------------------------------------------------------- PD-5


class TestPd5PinnedSpecApprovalEnablesConstructionRoles(T1Case):
    """PD-5 (control positivo interno): con la entrada del PD-3/PD-4
    presente y el sha256 coincidente con el archivo, `prepare` para esos
    roles → rc=0."""

    def test_pd5_pinned_spec_approval_enables_each_construction_role(self) -> None:
        for role, substage in CONSTRUCTION_ROLES:
            with self.subTest(role=role, substage=substage):
                project = make_project(spec_approval=spec_approval_entry())
                proc = prepare(project, role=role, substage=substage)
                combined = proc.stdout + proc.stderr
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"PD-5 {role}: la aprobación pineada coincidente debe "
                        f"habilitar: {combined!r}")
                self.assertTrue(
                    proc.stdout.startswith(PACKET_BEGIN),
                    msg=f"PD-5 {role}: stdout sin paquete canónico")
                state = json.loads(
                    (project / STATE_FILE).read_text(encoding="utf-8"))
                self.assertEqual(
                    state.get("active_packet", {}).get("role"), role,
                    msg=f"PD-5 {role}: el paquete activo no lleva el rol")


# ---------------------------------------------------------------- PD-6


class TestPd6RectifiedEntryAuthorizesNothing(T1Case):
    """PD-6: un state cuya única señal es una entrada
    {stage: "discovery-authorization", authorized_by, rectified_at} no
    habilita: architect → rc=2 (no es `epic-plan`); test-writer → rc=2 (no
    es `specification`)."""

    def test_pd6_rectified_entry_does_not_authorize_any_role(self) -> None:
        # Entrada rectificada real (stage_history[161] del 2026-10-08): ningún
        # preparar hace efecto aunque el resto del state sea coherente.
        for role, substage in (("architect", "discovery"),
                               ("test-writer", "red")):
            with self.subTest(role=role, substage=substage):
                project = make_project(spec_approval=rectified_entry())
                before = tree_snapshot(project)
                state_before = (project / STATE_FILE).read_bytes()
                proc = prepare(project, role=role, substage=substage)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"PD-6 {role}: la entrada rectificada autorizó la "
                        f"preparación: {proc.stdout + proc.stderr!r}")
                self.assertEqual(
                    proc.stdout, "",
                    msg=f"PD-6 {role}: stdout no vacío en rechazo")
                self.assertNotIn(
                    "Traceback", proc.stderr,
                    msg=f"PD-6 {role}: fallo con traceback")
                self.assertEqual(
                    tree_snapshot(project), before,
                    msg=f"PD-6 {role}: hubo publicación parcial")
                self.assertEqual(
                    (project / STATE_FILE).read_bytes(), state_before,
                    msg=f"PD-6 {role}: el state cambió en el rechazo")


# ---------------------------------------------------------------- PD-12 (slice)


class TestPd12ApprovalPendingMarker(T1Case):
    """PD-12 (slice T1: condición `approval pending`): rc=2 y stderr con el
    marcador, nombrando el registro/falta concreto y la acción legítima
    siguiente (registrar la aprobación en `stage_history`); sin alterar el
    state ni publicar archivos; sin mezclar los otros marcadores."""

    def test_pd12_missing_spec_approval_names_record_and_next_action(self) -> None:
        project = make_project(spec_approval=rectified_entry())
        before = tree_snapshot(project)
        state_before = (project / STATE_FILE).read_bytes()
        proc = prepare(project, role="test-writer", substage="red")
        stderr = proc.stderr
        self.assert_no_effects(
            project, before, state_before, label="PD-12",
            stderr=stderr, rc=proc.returncode)
        self.assertRegex(
            stderr, r"stage_history|specification|approved",
            msg=f"PD-12: el diagnóstico no nombra el registro concreto y su "
                f"acción legítima (registrar la aprobación en stage_history): "
                f"{stderr!r}")
        self.assertIn(
            SPEC_FILE, stderr,
            msg=f"PD-12: el diagnóstico no nombra la spec concreta: {stderr!r}")
        # Marcadores mutuamente excluyentes por condición (PD-12): la falta de
        # aprobación no es `packet obsolete` ni `state incoherent`.
        self.assertNotIn(
            "packet obsolete", stderr,
            msg=f"PD-12: el marcador approval pending se mezcló con "
                f"`packet obsolete`: {stderr!r}")
        self.assertNotIn(
            "state incoherent", stderr,
            msg=f"PD-12: el marcador approval pending se mezcló con "
                f"`state incoherent`: {stderr!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
