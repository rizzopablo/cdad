#!/usr/bin/env python3
"""005-007 T4 RED — Delta 2: el informe del architect se materializa por el
camino legítimo (receive + materialize), PD-8, y la observación 1 de la
revisión de Claude (el draft entregado por la interfaz común llega como UNA
sola parte `role-report`).

Contract:
- docs/specs/005-007-progressive-planning/spec.md (PD-8; INV-4 fail-closed,
  INV-5 compatibilidad de receive/materialize existentes).
- docs/specs/005-007-progressive-planning/plan.md (ficha T4; test focal
  declarado `tests/test_005_007_t4_architect_report_materialization.py`;
  regresiones declaradas tests/test_003_002_t1_receive.py,
  tests/test_003_002_t2_materialize.py).
- docs/specs/005-007-progressive-planning/review-claude-spec-2026-10-13.md
  (observación 1: la interfaz común entrega el draft como UNA sola parte;
  el kind que emite es `role-report`).

Oráculo del RED (hecho medido fijado por el encargo T4; derivado del
contrato, sin leer implementación): hoy la tabla cerrada de materialización
(`artifact-policy.json` + el eje rol/subfase de `cdad_result.py`) admite
para el architect sólo `architect-spec-draft` y `architect-plan-draft`; el
recibo real del discovery de 005-007 lleva `artifact_kind: role-report`,
que NO pertenece a la tabla, y el adaptador de la interfaz común
(`cdad_delegate_opencode.py`) emite siempre `role-report`.

Mapa de casos (cada uno trazado a PD-8/AC-3 y a la ficha T4):

1. POSITIVO (RED, AssertionError hoy): una parte con
   `artifact_kind: role-report` de un paquete del rol `architect`
   (subetapa `discovery`) se materializa por `materialize` a un destino
   dentro de `docs/specs/<feature>/`, con sha IDÉNTICO al de la parte
   recibida y sin copia manual.
2. CONTROL (negativo, clausura del eje rol): un kind NOMBRADO de otro rol
   (`implementer-role-report` / `test-writer-role-report` sobre un paquete
   del architect) sigue rechazándose (rc≠0), sin dejar prefijo parcial.
3. CONTROL (negativo): un destino FUERA de la raíz permitida
   `docs/specs/<feature>/` sigue rechazándose.
4. CONTROL (binding): la materialización sigue exigiendo el
   `receipt_sha256` correcto del recibo durable (un `receipt_sha256`
   erróneo se rechaza), con `approval_effect: false`.
5. CONTROL (regresión/INV-5): los kinds vigentes siguen materializando
   igual (`architect-spec-draft`, `architect-plan-draft`, `review`) y
   `receive` no cambia su comportamiento.

Superficie observable (§2 de 003-002, reutilizada; nada de plomería):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --role architect --substage discovery --objective <texto>
    python3 scripts/cdad_packet.py prepare --project-root R \
        --record-dispatch <id> --attempt-id <a> --input <obs.json>  # I8
    python3 scripts/cdad_result.py receive --project-root R \
        --execution-context E.json --packet PACKET.md \
        --request REQUEST.json --descriptor RESULT.json
    python3 scripts/cdad_result.py materialize --project-root R \
        --receipt receipt.json --authorization MATERIALIZE.json

Fixtures offline (patrón de `tests/test_003_002_t1_receive.py` /
`test_003_002_t2_materialize.py` + el encargo de architect de
`test_005_001_t4_decisive` S1: plan del epic aprobado en `epic_history`;
los proyectos son tempdirs, ninguna escritura en este repo, ninguna ruta
absoluta del host, ningún despliegue, ninguna base de sesiones real.
Los targets declarados son project-relative y las corridas de
`materialize` usan cwd en la raíz del fixture, como T2 de 003-002 — un
target mal resuelto caería dentro del fixture, nunca en este repo).

Del contrato de 003-002 (R5, evidencia del ciclo): `receive` NO gatea por
la tabla cerrada de kinds — lo hace `materialize`. Por eso la parte única
`role-report` puede recibirse hoy (y el caso 1 muere en `materialize`),
y los kinds foráneos del caso 2 también (gateados por `materialize`).

RED hoy: los casos 1 fallan por AssertionError sobre el comportamiento
ausente (la tabla cerrada rechaza `role-report` para el architect); los
controles 2-5 pasan hoy y se declaran como tales.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"   # runtime v2 de 001 (no se redefine)
RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"   # helper de 003-002 (superficie reutilizada)

EPIC_ID = "epic-005-real-operation"
# IMPORTANTE: feature del FIXTURE, no la feature real (005-007). Toda
# escritura cae bajo `docs/specs/<FIXTURE>/` en un tempdir de /tmp; nada
# de este repo se toca (INV-6: sin HOME, sin rutas absolutas del host, sin
# desplegar).
FEATURE_ID = "005-999-t4-architect-report-fixture"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
PLAN_FILE = f"docs/epics/{EPIC_ID}/plan.md"
PLAN_BYTES = b"# Epic plan fixture (005-007 T4)\n"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture (solo necesaria para el fixture del reviewer)\n"

APPROVER = "Pablo"
AUTHORIZED_BY = "Pablo (HITL delegada al orquestador OpenCode)"
ATTEMPT_ID = "att-005-007-t4-red-001"
OBJECTIVE_ARCHITECT = "005-007 T4 RED: materialización legítima del informe del architect"
OBJECTIVE_REVIEWER = "005-007 T4 RED: fixture del reviewer para la regresión del kind review"

# La raíz permitida declarada por PD-8 para los kinds del informe
# (`docs/specs/<feature>/`) y el target exacto que declara la
# autorización en cada caso.
ALLOWED_ROOT = f"docs/specs/{FEATURE_ID}/"
TARGET_REPORT = ALLOWED_ROOT + "discovery.md"
TARGET_REVIEW = ALLOWED_ROOT + "review.md"

DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"
MANIFEST_PATH = ".cdad/inbox/changes.json"
BASELINE_REF = "orchestrator-staged-reference"
BASELINE_SHA256 = "0" * 64

# Los kinds nombrados de otros roles (clausura del eje rol, PD-8/AC-3).
FOREIGN_KINDS = ("implementer-role-report", "test-writer-role-report")

# Kinds vigentes de la tabla cerrada que la ficha T4 lista como regresión.
ARCHITECT_EXISTING_KINDS = ("architect-spec-draft", "architect-plan-draft")


# ---------------------------------------------------------------- helpers


def out_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout.decode("utf-8", errors="replace")


def err_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stderr.decode("utf-8", errors="replace")


CLI_AUSENTE_MARKERS = (
    "No such file or directory",
    "invalid choice",
    "unrecognized",
    "No module named",
)


def assert_reachable_or_invalid_red(stderr: str, contexto: str) -> None:
    """Guard anti-RED inválida: el fallo del CLI no debe indicar ausencia
    del comando/módulo (eso sería RED falsa); debe nombrar la conducta."""
    for marker in CLI_AUSENTE_MARKERS:
        assert marker not in stderr, (
            f"RED inválida ({contexto}): el fallo es por CLI ausente "
            f"({marker!r} en stderr), no por el comportamiento bajo "
            f"prueba: {stderr!r}")


def observation_document(session: str) -> dict:
    """Documento de observación I8 (claves cerradas; sin datos de host)."""
    return {
        "runtime": "opencode",
        "model_configured": "mofgw/glm-5.3-flash",
        "model_reported": "mofgw/glm-5.3-flash",
        "session": session,
        "started_at": "2026-10-13T00:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def fixture_state_document(
        epic_plan_approved: bool, spec_approved: bool) -> dict:
    """State sintético.

    - `epic_plan_approved=True` habilita al architect sin spec aprobada
      (el encargo del epic con plan aprobado en `epic_history`, patrón
      `test_005_001_t4_decisive` S1).
    - `spec_approved=True` añade la aprobación pineada de la spec de la
      feature en `stage_history` (necesaria para `prepare --role
      reviewer`, que valida contra la spec de la feature).
    """
    stage_history = []
    if spec_approved:
        stage_history.append({
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": APPROVER,
            "approved_at": "2026-10-13T00:00:00Z",
            "contract_path": CONTRACT_FILE,
            "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
        })
    epic_history = []
    if epic_plan_approved:
        epic_history.append({
            "epic": EPIC_ID,
            "stage": "epic-plan",
            "approved_by": APPROVER,
            "approved_at": "2026-10-13T00:00:00Z",
        })
    return {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": epic_history,
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": stage_history,
        "approver": APPROVER,
        "last_updated": "2026-10-13T00:00:00Z",
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


def build_project(root: Path, *, state: dict) -> Path:
    """Proyecto sintético válido para `prepare` (política v2)."""
    for rel in ("tests", "src", "lib", "docs"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / POLICY_FILE).write_text(json.dumps({
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Plan del epic (contrato del architect en el fixture Architect).
    (root / PLAN_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / PLAN_FILE).write_bytes(PLAN_BYTES)
    # Spec de la feature (contrato del reviewer en el fixture Reviewer).
    (root / CONTRACT_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
    (root / AUTHORITY_REF).parent.mkdir(parents=True, exist_ok=True)
    (root / AUTHORITY_REF).write_text(
        "# Authorized execution fixture (epic-005)\n", encoding="utf-8")
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")
    return root


# ---------------------------------------------------------------- fixture


class ReceivedProjectCase(unittest.TestCase):
    """Proyecto sintético con paquete dispatched y recibo durable de la
    única parte entregada (flujo receive de 003-002).

    Cada subclase fija su rol/subfase/kind por atributos de clase:
    - `Architect`: rol `architect`, subetapa `discovery`, parte única
      `role-report` (el kind que emite la interfaz común, observación 1;
      el fixture tiene el plan del epic aprobado y NO la spec aprobada —
      el descubrir del architect es legítimo sin ella).
    - `Reviewer`: rol `reviewer`, subetapa `review`, parte `review`
      (fixture con la spec aprobada en `stage_history`; usado sólo para
      la regresión del kind vigente `review`).
    """

    ROLE: str = "architect"
    SUBSTAGE: str = "discovery"
    PART_NAME: str = "architect-report"
    PART_BYTES: bytes = (
        b"# Role report (fixture T4 005-007)\n"
        b"Informe de discovery del architect entregado por la interfaz "
        b"comun\ncomo UNA sola parte con artifact_kind: role-report.\n"
    )
    DEFAULT_PART_KIND: str = "role-report"
    EPIC_PLAN_APPROVED: bool = True
    SPEC_APPROVED: bool = False
    OBJECTIVE: str = OBJECTIVE_ARCHITECT
    SESSION: str = "ses-005-007-t4-red-fixture-0001"

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-007-t4-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))

    # -- oráculos del store -------------------------------------------------

    @property
    def final_dir(self) -> Path:
        return (self.root / ".cdad" / "runtime" / "results"
                / self.execution_id / self.packet_id)

    @property
    def receipt_path(self) -> Path:
        return self.final_dir / "receipt.json"

    @property
    def receipt_sha256(self) -> str:
        return hashlib.sha256(self.receipt_path.read_bytes()).hexdigest()

    @property
    def state_path(self) -> Path:
        return self.root / STATE_FILE

    # -- construcción del fixture ------------------------------------------

    def new_dispatched_project(self, *,
                               part_kind: str | None = None) -> None:
        """Proyecto sintético nuevo (tempdir) con el paquete dispatched y
        el receipt durable de la única parte entregada. `part_kind` permite
        variar el kind declarado del descriptor (casos negativos)."""
        tmp = tempfile.mkdtemp(prefix="cdad-005-007-t4red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.part_kind = part_kind or self.DEFAULT_PART_KIND
        self.root = build_project(Path(tmp) / "proj", state=fixture_state_document(
            self.EPIC_PLAN_APPROVED, self.SPEC_APPROVED))
        self.establish_dispatched()
        self.establish_received()

    def establish_dispatched(self) -> None:
        """Prepara el paquete del fixture y lo observa como dispatched
        (I8); deja execution_id/packet_id/durables."""
        prep = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--role", self.ROLE, "--substage", self.SUBSTAGE,
            "--objective", self.OBJECTIVE,
        ])
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` de {self.ROLE}/"
                f"{self.SUBSTAGE} debe tener éxito: "
                f"{out_text(prep)} {err_text(prep)}")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.packet_id = state["active_packet"]["id"]
        execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            execution_id,
            msg="precondición (fixture): state.execution debe referenciar "
                "el contexto v2 de 001")
        self.execution_id = execution_id
        self.execution_context_path = (
            self.root / ".cdad" / "executions" / execution_id
            / "execution.json")
        self.assertTrue(
            self.execution_context_path.is_file(),
            msg="precondición (fixture): el contexto v2 debe existir en "
                ".cdad/executions")
        self.packet_dir = self.root / ".cdad" / "packets" / self.packet_id
        self.packet_path = self.packet_dir / "PACKET.md"
        self.request_path = self.packet_dir / "REQUEST.json"
        for path in (self.packet_path, self.request_path):
            self.assertTrue(
                path.is_file(),
                msg=f"precondición (fixture): debe existir el paquete "
                    f"publicado en {path}")
        observation_path = self.root / "docs" / "observations-fixture.json"
        observation_path.write_text(
            json.dumps(
                observation_document(self.SESSION),
                indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"precondición (fixture): --record-dispatch debe registrar "
                f"el intento: {out_text(record)} {err_text(record)}")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): el paquete activo debe quedar "
                "dispatched (status I8)")

    def establish_received(self) -> None:
        """Recibo durable de la única parte (receive de 003-002, rc=0):
        el kind declarado va en el descriptor (gatea en `materialize`,
        no en `receive` — R5 de 003-002)."""
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / f"{self.PART_NAME}.md").write_bytes(self.PART_BYTES)
        (self.root / MANIFEST_PATH).write_text(
            json.dumps({
                "schema_version": 1,
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "changes": [],
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor_doc = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [
                {"name": self.PART_NAME,
                 "artifact_kind": self.part_kind,
                 "staged_path": f".cdad/inbox/{self.PART_NAME}.md"}
            ],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "manifest_path": MANIFEST_PATH,
            },
            "run_evidence_ref": None,
        }
        descriptor_path = self.root / DESCRIPTOR_PATH
        descriptor_path.write_text(
            json.dumps(descriptor_doc, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
        proc = self.run_result_cli([
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(descriptor_path),
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): `receive` debe aceptar la "
                f"entrega (kinds plausibles; la tabla cerrada gatea en "
                f"materialize, no en receive — R5 de 003-002): "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r} "
                f"part_kind={self.part_kind!r}")
        self.assertTrue(
            self.receipt_path.is_file(),
            msg="precondición (fixture): el receipt durable debe existir")

    # -- corridas del CLI ----------------------------------------------------

    def run_packet_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(PACKET_SCRIPT), *args],
            cwd=REPO_ROOT, capture_output=True,
        )

    def run_result_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        """Corrida del CLI de 003-002 con cwd en la raíz del fixture: los
        targets declarados son project-relative, no cwd-relative (un
        target mal resuelto cae dentro del fixture, nunca en este repo)."""
        return subprocess.run(
            [sys.executable, str(RESULT_SCRIPT), *args],
            cwd=self.root, capture_output=True,
        )

    # -- autorización (§7 de 003-002) -----------------------------------------

    def build_authorization(
            self, copies: list[dict], *,
            receipt_sha: str | None = None,
            approval_effect: bool = False) -> dict:
        return {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "receipt_sha256": receipt_sha or self.receipt_sha256,
            "authorized_by": AUTHORIZED_BY,
            "authority_ref": AUTHORITY_REF,
            "approval_effect": approval_effect,
            "copies": copies,
        }

    def write_authorization(self, doc: dict) -> Path:
        path = self.root / ".cdad" / "inbox" / "MATERIALIZE.json"
        path.write_text(
            json.dumps(doc, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def materialize(self, auth_path: Path) -> subprocess.CompletedProcess:
        return self.run_result_cli([
            "materialize",
            "--project-root", str(self.root),
            "--receipt", str(self.receipt_path),
            "--authorization", str(auth_path),
        ])

    # -- oráculos de efecto ---------------------------------------------------

    def snapshot_state_and_receipt(self) -> None:
        self.state_before = self.state_path.read_bytes()
        self.receipt_before = self.receipt_path.read_bytes()

    def assert_target_identical(self, target: Path) -> None:
        """El materializado existe y su sha es idéntico al de la parte
        recibida (y el part del store conserva los bytes originales, de
        modo que el materializado deriva de `receive`, no de una copia
        manual)."""
        self.assertTrue(
            target.is_file(),
            msg=f"debe existir el materializado en {target}")
        stored_part = (
            self.final_dir / "parts" / f"{self.PART_NAME}.utf8")
        self.assertTrue(
            stored_part.is_file(),
            msg="precondición: el part recibido debe existir en el store "
                "de 003-002 ")
        part_sha = hashlib.sha256(self.PART_BYTES).hexdigest()
        self.assertEqual(
            hashlib.sha256(stored_part.read_bytes()).hexdigest(), part_sha,
            msg="el part recibido en el store debe conservar los bytes "
                "originales (PD-1 de 003-002)")
        self.assertEqual(
            hashlib.sha256(target.read_bytes()).hexdigest(), part_sha,
            msg=f"el sha del materializado {target.name!r} debe ser "
                f"idéntico al de la parte recibida (sin copia manual)")

    def assert_no_state_or_receipt_change(self, label: str) -> None:
        self.assertEqual(
            self.state_path.read_bytes(), self.state_before,
            msg=f"{label}: docs/.cdad-state.json debe permanecer intacto "
                f"(el único escritor del state es el orquestador; la "
                f"materialización no aprueba nada)")
        self.assertEqual(
            self.receipt_path.read_bytes(), self.receipt_before,
            msg=f"{label}: el receipt durable debe permanecer intacto")

    def assert_rejection_no_partial(self, proc, label: str) -> None:
        """Clausura fail-closed comun: rc≠0, guard de CLI ausente, stdout
        vacío, target ausente (sin prefijo parcial) y state/receipt
        intactos."""
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"{label}: el rechazo debe fallar cerrado (rc=0 con "
                f"escritura sería un bypass del fail-closed, INV-4): "
                f"rc={proc.returncode} stdout={out_text(proc)!r}")
        assert_reachable_or_invalid_red(err_text(proc), label)
        self.assertNotIn("Traceback", err_text(proc),
                         msg=f"{label}: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg=f"{label}: en rechazo no debe emitirse evidencia por "
                f"stdout")
        self.assertFalse(
            (self.root / TARGET_REPORT).exists(),
            msg=f"{label}: el rechazo dejó el target {TARGET_REPORT!r} "
                f"(sin prefijo parcial, INV-4)")
        self.assertFalse(
            (self.root / TARGET_REVIEW).exists(),
            msg=f"{label}: el rechazo dejó el target {TARGET_REVIEW!r} "
                f"(sin prefijo parcial, INV-4)")
        self.assert_no_state_or_receipt_change(label)


# ------------------------------------------------------------ PD-8 positivo


class TestArchitectRoleReportMaterializes(ReceivedProjectCase):
    """PD-8/AC-3 (positivo; caso 1 de la ficha T4 — el RED): una parte
    `role-report` del architect (el kind único que emite la interfaz
    común; el draft llega como UNA sola parte, observación 1) se
    materializa por el camino legítimo."""

    def test_pd8_role_report_materializes_with_identical_sha_into_specs_root(self) -> None:
        """PD-8/AC-3 (RED): el informe recibido con
        `artifact_kind: role-report` (el kind que hoy emite siempre el
        adaptador de la interfaz común; una sola parte del draft, al
        menos hasta T4) se materializa vía `materialize` a un destino
        dentro de `docs/specs/<feature>/`, con sha idéntico al de la
        parte recibida y sin copia manual, sin aprobar nada (`approval_
        effect` sigue `false`, state y receipt intactos). Hoy se rechaza
        por no estar el kind admitido en la tabla cerrada para el
        architect (precondición del fail-closed de 003-002)."""
        self.new_dispatched_project()  # parte única kind="role-report"
        auth_path = self.write_authorization(self.build_authorization(
            [{"part": self.PART_NAME, "target": TARGET_REPORT,
              "expected_previous_sha256": None}]))
        self.snapshot_state_and_receipt()
        proc = self.materialize(auth_path)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-8: la tabla cerrada de materialización debe admitir "
                f"el kind `role-report` para el kind del architect "
                f"(subetapa {self.SUBSTAGE!r}) — es el kind que emite el "
                f"adaptador de la interfaz común, y el recibo del "
                f"discovery real de 005-007 lo lleva (hoy el kind no está "
                f"en la tabla cerrada del architect y materialize lo "
                f"rechaza, sin vía legítima para el informe): "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="PD-8: materialize terminó con traceback")
        self.assert_target_identical(self.root / TARGET_REPORT)
        self.assert_no_state_or_receipt_change("PD-8 (positivo)")


# ------------------------------------------------------------ PD-8 negativos


class TestArchitectRoleClosure(ReceivedProjectCase):
    """PD-8/AC-3 (control; caso 2 de la ficha T4): un kind NOMBRADO de
    otro rol sigue rechazándose, incluso si estuviera en la tabla — el
    eje rol cerrado (clausura del eje rol)."""

    def test_pd8_foreign_role_named_kinds_stay_rejected(self) -> None:
        for label, kind in {
            "reporte del implementer": "implementer-role-report",
            "reporte del test-writer": "test-writer-role-report",
        }.items():
            with self.subTest(caso=label):
                self.new_dispatched_project(part_kind=kind)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": TARGET_REPORT,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assert_rejection_no_partial(
                    proc, f"PD-8 AC-3 ({label})")


class TestOutsideAllowedRoot(ReceivedProjectCase):
    """PD-8/AC-3 (control; caso 3 de la ficha T4): un destino FUERA de la
    raíz permitida `docs/specs/<feature>/` sigue rechazándose."""

    def test_pd8_target_outside_specs_feature_root_stays_rejected(self) -> None:
        for label, target in {
            "fuera de docs (sin specs)": "informe-arquitecto.md",
            "specs de otra feature":
                "docs/specs/005-998-otra-feature/informe.md",
            "docs de sistema": "docs/systemPatterns.md",
        }.items():
            with self.subTest(caso=label):
                self.new_dispatched_project()
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": target,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assert_rejection_no_partial(
                    proc, f"PD-8 AC-3 ({label})")
                self.assertFalse(
                    (self.root / target).exists(),
                    msg=f"PD-8 ({label}): el rechazo creó el target "
                        f"{target!r} fuera de la raíz permitida")


class TestMaterializeBinding(ReceivedProjectCase):
    """PD-8 (control; binding de autorización de la ficha T4): la
    materialización sigue exigiendo el recibo durable con su
    `receipt_sha256` correcto y `approval_effect: false`; un
    `receipt_sha256` erróneo se rechaza."""

    def test_pd8_materialize_binding_bad_receipt_sha256_rejected(self) -> None:
        """El binding usa `architect-spec-draft` (kind vigente de la
        tabla, admitido hoy) para probar el binding ORTOGONALMENTE al
        RED: el sha erróneo debe rechazarse ANTES de aplicar cualquier
        copia (mismo gating pre-copia que en 003-002 P4)."""
        self.new_dispatched_project(part_kind="architect-spec-draft")
        auth_path = self.write_authorization(self.build_authorization(
            [{"part": self.PART_NAME, "target": TARGET_REPORT,
              "expected_previous_sha256": None}],
            receipt_sha="f" * 64))
        self.snapshot_state_and_receipt()
        proc = self.materialize(auth_path)
        self.assert_rejection_no_partial(
            proc, "PD-8 (binding con `receipt_sha256` erróneo)")


# --------------------------------------------------------------- regresión


class TestArchitectExistingKindsRegression(ReceivedProjectCase):
    """PD-8/INV-5 (regresión, parte 1; caso 5 de la ficha): los kinds
    vigentes del architect (`architect-spec-draft`,
    `architect-plan-draft`) siguen materializando exactamente como hoy.
    (No se usa la via forzada: el architect declara el kind vigente en su
    propio paquete — mismo fixture del RED)."""

    def test_regression_architect_existing_kinds_materialize_unchanged(self) -> None:
        for kind in ARCHITECT_EXISTING_KINDS:
            with self.subTest(kind=kind):
                self.new_dispatched_project(part_kind=kind)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": TARGET_REPORT,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"regresión ({kind}): el kind vigente {kind!r} del "
                        f"architect debe seguir materializando "
                        f"exactamente como hoy: rc={proc.returncode} "
                        f"stdout={out_text(proc)!r} "
                        f"stderr={err_text(proc)!r}")
                self.assert_target_identical(self.root / TARGET_REPORT)
                self.assert_no_state_or_receipt_change(
                    f"regresión ({kind})")


class TestReviewerReviewKindRegression(ReceivedProjectCase):
    """PD-8/INV-5 (regresión, parte 2; caso 5 de la ficha): el kind
    `review` (del reviewer) sigue materializando exactamente como hoy.
    El fixture del reviewer exige la spec aprobada en `stage_history`
    (subfase válida del reviewer); el kind declarado es `review`."""

    ROLE = "reviewer"
    SUBSTAGE = "review"
    PART_NAME = "review-part"
    PART_BYTES = b"# Review (fixture T4 005-007)\nInforme de revision.\n"
    DEFAULT_PART_KIND = "review"
    EPIC_PLAN_APPROVED = False
    SPEC_APPROVED = True
    OBJECTIVE = OBJECTIVE_REVIEWER
    SESSION = "ses-005-007-t4-red-fixture-0002"

    def test_regression_review_kind_materializes_unchanged(self) -> None:
        self.new_dispatched_project()  # parte kind="review"
        auth_path = self.write_authorization(self.build_authorization(
            [{"part": self.PART_NAME, "target": TARGET_REVIEW,
              "expected_previous_sha256": None}]))
        self.snapshot_state_and_receipt()
        proc = self.materialize(auth_path)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"regresión (review): el kind vigente `review` del "
                f"reviewer debe seguir materializando exactamente como "
                f"hoy: rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assert_target_identical(self.root / TARGET_REVIEW)
        self.assert_no_state_or_receipt_change("regresión (review)")


class TestReceiveUnchanged(ReceivedProjectCase):
    """PD-8/INV-5 (regresión, parte 3; caso 5 de la ficha): `receive` no
    cambia su comportamiento — el mismo proyecto fixture recibe la
    entrega con rc=0, receipt durable mecánico (`semantic_status
    pending`), identidad ligada y el part persistido byte-idéntico."""

    def test_regression_receive_of_role_report_part_mechanical(self) -> None:
        self.new_dispatched_project()
        receipt = json.loads(
            self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt["semantic_status"], "pending",
            msg="regresión: el recibo de `receive` debe seguir mecánico"
                " (semantic_status=pending); ninguna recepción aprueba")
        self.assertEqual(
            receipt["role"], self.ROLE,
            msg="regresión: el recibo sigue ligando el rol del paquete")
        self.assertEqual(
            receipt["substage"], self.SUBSTAGE,
            msg="regresión: el recibo sigue ligando la subfase del "
                "paquete")
        self.assertEqual(
            receipt["feature_id"], FEATURE_ID,
            msg="regresión: el recibo sigue ligando la feature")
        stored_part = (
            self.final_dir / "parts" / f"{self.PART_NAME}.utf8")
        self.assertTrue(
            stored_part.is_file(),
            msg="regresión: receive sigue persistiendo el part con bytes "
                "idénticos (PD-1 de 003-002)")
        self.assertEqual(
            stored_part.read_bytes(), self.PART_BYTES,
            msg="regresión: los bytes recibidos permanecen intactos tras "
                "el part único `role-report`")
        # receive es la única operación del CLI ejecutada sobre el fixture
        # tras build_project: ninguna escritura fuera del store
        # operacional `.cdad/` salvo el part staged + descriptor + manifest
        # del propio fixture (inbox). En particular, nada en docs/specs/
        # más allá de la spec sintética del proyecto: receive JAMÁS
        # materializa (sólo materialize lo hace).
        tree = tree_snapshot(self.root)
        outside = [
            rel for rel, data in tree.items()
            if data is not None          # sólo archivos (los dirs del
                                         # fixture sintético van con
                                         # None; no son escrituras)
            and rel.startswith("docs/specs/")
            and rel != f"docs/specs/{FEATURE_ID}/spec.md"
        ]
        self.assertFalse(
            outside,
            msg="regresión: receive no debe materializar nada (los "
                "targets de bajo docs/specs/ sólo los escribe "
                "materialize): escribió " + ", ".join(sorted(outside)[:8]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
