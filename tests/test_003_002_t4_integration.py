#!/usr/bin/env python3
"""003-002 T4 RED — recorrido de integración desde el producto INSTALADO.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (§1 instalación, §2 interfaz,
  §5 persistencia/retry, §6 recibo, §7 materialización, §9 propiedad del
  estado; P1, P2, P4; invariantes; criterios de aceptación: smoke instalado,
  recorrido receive → reconcile → materialize sin duplicar efectos ni
  escribir state desde las herramientas).
- docs/specs/003-002-artifact-tools/plan.md (T4; test focal declarado
  `tests/test_003_002_t4_integration.py`).

El objeto es el RECORRIDO DESDE EL PRODUCTO INSTALADO, no el wrapper del
repo: T1/T2 invocan REPO_ROOT/scripts/cdad_result.py; aquí el entrypoint es
el INSTALADO por `install.sh --basic`:

    <install_root>/.config/opencode/skills/cdad-cycle/scripts/cdad_result.py

invocado desde un PROYECTO FIXTURE (tempdir) que contiene sólo los
artefactos del proyecto (docs/cdad-policy.json,
.cdad/executions/<id>/execution.json,
.cdad/packets/<id>/{REQUEST.json,PACKET.md}, docs/.cdad-state.json) y
NINGÚN wrapper del repo. Patrón de instalación aislada reutilizado
(sin modificar): tests/product_staging.py (PRODUCT_ROOT) y
tests/test_004_001_acceptance_matrix.py (PRODUCT_ENTRIES = install.sh,
scripts, skills, sources, agents; copia del producto a tempdir +
CDAD_INSTALL_ROOT apuntando a un tempdir EXISTENTE + install.sh --basic).

Fixtures offline: proyecto sintético v2 preparado con el runtime de 001
(`prepare` + `--record-dispatch`, I8), igual que T1/T2; parts staged bajo
`.cdad/inbox`. Todo proyecto es tempdir; NUNCA se escribe en el repo ni se
instala en el HOME real.

RED honesto: T1–T3 ya entregaron `cdad_result.py`; si una aserción pasa hoy
se declara GUARD (pre-satisfecha) con su razón; no se fabrica una falla.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    tree_snapshot,
)

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"     # staging del producto
PACKET_SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"   # runtime v2 de 001 (fixture)

# Patrón de instalación aislada (test_004_001_acceptance_matrix.py).
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIME = "opencode"
# 006-003 U1/PD-1f: el generador no tiene `--profile`; `PROFILE = "basic"` se
# retiró con el argumento (ver tests/test_006_003_u1_generator_without_profiles.py).
FLAG = "--basic"
SKILL_REL = Path(".config") / RUNTIME / "skills" / "cdad-cycle"
INSTALLED_RESULT_REL = SKILL_REL / "scripts" / "cdad_result.py"

POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
FEATURE_ID = "003-002-artifact-tools"
EPIC_ID = "epic-003-context-efficiency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture 003-002 (T4 RED)\n"

ROLE = "test-writer"
SUBSTAGE = "red"
ATTEMPT_ID = "attempt-t4-red-001"
AUTHORIZED_BY = "Pablo (HITL delegada al orquestador OpenCode)"

# staged parts del fixture (§3; kinds de la tabla cerrada del rol).
STAGED_PARTS: dict[str, bytes] = {
    "role-report": (
        b"# Role report (fixture T4 RED)\n"
        b"Evidencia mecanica del intento test-writer/red de 003-002.\n"
    ),
    "role-notes": (
        b"# Role notes (fixture T4 RED)\n"
        b"Notas auxiliares del mismo intento; bytes separados.\n"
    ),
}
PART_KINDS: dict[str, str] = {
    "role-report": "test-writer-role-report",
    "role-notes": "test-writer-notes",
}
PART_NAME = "role-report"

BASELINE_REF = "orchestrator-prepared-reference"
BASELINE_SHA256 = "0" * 64
MANIFEST_PATH = ".cdad/inbox/changes.json"
DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"

# Raíz permitida por kind `test-writer-role-report` (§7) y target exacto.
ALLOWED_ROOT = f"docs/specs/{FEATURE_ID}/"
TARGET_REPORT = ALLOWED_ROOT + "test-writer-role-report.md"

# Esquemas que la instalación debe ofrecer al entrypoint (§1: assets).
REQUIRED_SCHEMAS = (
    "result-descriptor.schema.json",
    "result-receipt.schema.json",
    "result-bundle.schema.json",
    "materialize.schema.json",
    "run-request.schema.json",
    "run-evidence.schema.json",
)


# ---------------------------------------------------------------- fixtures


def _as_text(data: bytes | str | None) -> str:
    if data is None:
        return ""
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return data


def out_text(proc: subprocess.CompletedProcess) -> str:
    return _as_text(proc.stdout)


def err_text(proc: subprocess.CompletedProcess) -> str:
    return _as_text(proc.stderr)


def fixture_state_document() -> dict:
    """State sintético con los registros I2 para `prepare` del fixture."""
    hitl = {
        "status": "active",
        "epic_id": EPIC_ID,
        "source": AUTHORITY_REF,
        "scope": EPIC_ID,
        "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
    }
    return {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": [],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": SUBSTAGE,
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [{
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-10-05T00:00:00Z",
            # 005-001 T1 (D3): forma pineada — CONTRACT_BYTES es lo que
            # build_project escribe en CONTRACT_FILE (migración mecánica).
            "contract_path": CONTRACT_FILE,
            "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
        }],
        "approver": "Pablo",
        "last_updated": "2026-10-05T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": hitl,
    }


def build_project(root: Path) -> Path:
    """Proyecto sintético válido para `prepare` (política v2, I2)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    (root / POLICY_FILE).write_text(
        json.dumps({
            "schema_version": 1,
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src", "lib"],
                "documentation_roots": ["docs"],
            },
            "temporary_roots": [".cdad/tmp"],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / CONTRACT_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-003)\n",
                         encoding="utf-8")
    (root / STATE_FILE).write_text(
        json.dumps(fixture_state_document(), ensure_ascii=False) + "\n",
        encoding="utf-8")
    return root


class InstalledProductCase(unittest.TestCase):
    """Instalación aislada del producto (una vez por clase).

    Copia del producto (PRODUCT_ENTRIES) a tempdir + staging del runtime
    opencode/perfil basic + `install.sh --basic` con CDAD_INSTALL_ROOT en
    un tempdir EXISTENTE. Jamás se escribe en el repo ni en el HOME real.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-003-002-t4-red-")
        cls.addClassCleanup(cls._tmp.cleanup)
        base = Path(cls._tmp.name).resolve()
        cls.product_copy = base / "product"
        cls.product_copy.mkdir()
        for entry in PRODUCT_ENTRIES:
            source = REPO_ROOT / entry
            destination = cls.product_copy / entry
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_"):
                env.pop(key)
        cls.staging_result = subprocess.run(
            [sys.executable, str(GENERATOR), "--runtime", RUNTIME,
             "--stack", "odoo", "--out",
             str(cls.product_copy / "build" / "staging")],
            cwd=str(cls.product_copy), text=True, capture_output=True,
            check=False)
        cls.install_root = base / "install-root"
        cls.install_root.mkdir()
        install_env = env | {"CDAD_INSTALL_ROOT": str(cls.install_root),
                             "CDAD_SKILL_EXTRA_DIRS": ""}
        cls.install_result = subprocess.run(
            ["bash", str(cls.product_copy / "install.sh"), FLAG],
            cwd=str(cls.product_copy), env=install_env, text=True,
            capture_output=True, check=False)
        cls.installed_result = cls.install_root / INSTALLED_RESULT_REL

    # -- corridas -----------------------------------------------------------

    def run_packet_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        """Runtime v2 de 001 para preparar el fixture (no es 003-002)."""
        return subprocess.run(
            [sys.executable, str(PACKET_SCRIPT), *args],
            cwd=REPO_ROOT, capture_output=True)

    def run_installed(self, args: list[str]) -> subprocess.CompletedProcess:
        """Corrida del entrypoint INSTALADO, cwd = raíz del fixture.

        Probar el recorrido desde el producto instalado exige que el cwd
        sea el proyecto fixture: nada del repo puede contaminar la corrida.
        """
        return subprocess.run(
            [sys.executable, str(self.installed_result), *args],
            cwd=self.root, capture_output=True)


class FixtureProjectCase(InstalledProductCase):
    """Proyecto fixture (tempdir, sin wrappers del repo) + receipt durable."""

    def setUp(self) -> None:
        self._proj_tmp = tempfile.mkdtemp(prefix="cdad-003-002-t4-proj-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._proj_tmp], check=False))
        self.new_fixture_project()

    # -- oráculos del store ---------------------------------------------------

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

    def target_path(self, target: str) -> Path:
        return self.root / target

    # -- construcción del fixture ---------------------------------------------

    def new_fixture_project(self) -> None:
        """Proyecto fixture: artefactos del proyecto, cero wrappers del repo.

        El proyecto se prepara con el runtime de 001 en un tempdir
        intermedio y luego se copia COMPLETO al fixture: el fixture contiene
        sólo los artefactos del proyecto (docs/cdad-policy.json,
        docs/.cdad-state.json, .cdad/executions, .cdad/packets, .cdad/inbox)
        y ningún script del repo.
        """
        source = build_project(Path(self._proj_tmp) / "prep")
        self.establish_dispatched(source)
        self.establish_inbox(source)
        self.root = Path(self._proj_tmp) / "fixture"
        shutil.copytree(source, self.root, symlinks=True)
        # El fixture no debe contener wrappers del repo (recorrido puro).
        for wrapper in ("scripts", "skills", "agents", "install.sh"):
            self.assertFalse(
                (self.root / wrapper).exists(),
                msg=f"precondición (fixture): el fixture no debe contener "
                    f"{wrapper!r} del repo")

    def establish_dispatched(self, root: Path) -> None:
        """`prepare` v2 de 001 + observación de dispatch (I8) en el tempdir."""
        prep = self.run_packet_cli([
            "prepare", "--project-root", str(root),
            "--role", ROLE, "--substage", SUBSTAGE,
            "--objective", "T4 objective",
        ])
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` debe tener éxito: "
                f"{out_text(prep)} {err_text(prep)}")
        state = json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
        self.packet_id = state["active_packet"]["id"]
        self.execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            self.execution_id,
            msg="precondición (fixture): state.execution debe referenciar "
                "el contexto v2 de 001")
        for rel in (f".cdad/executions/{self.execution_id}/execution.json",
                    f".cdad/packets/{self.packet_id}/PACKET.md",
                    f".cdad/packets/{self.packet_id}/REQUEST.json"):
            self.assertTrue(
                (root / rel).is_file(),
                msg=f"precondición (fixture): debe existir {rel} (runtime v2)")
        observation_path = root / "docs" / "observations-t4.json"
        observation_path.write_text(json.dumps({
            "runtime": RUNTIME,
            "model_configured": "glm-5.3-flash",
            "model_reported": "glm-5.3-flash",
            "session": "ses-003-002-t4-red-0001",
            "started_at": "2026-10-05T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = self.run_packet_cli([
            "prepare", "--project-root", str(root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"precondición (fixture): --record-dispatch debe registrar "
                f"el intento: {out_text(record)} {err_text(record)}")
        state = json.loads((root / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): el paquete activo debe quedar "
                "dispatched (status I8)")

    def establish_inbox(self, root: Path) -> None:
        """Parts staged + manifest trusted vacío + descriptor (§3/§4)."""
        inbox = root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in STAGED_PARTS.items():
            (inbox / f"{name}.md").write_bytes(data)
        (root / MANIFEST_PATH).write_text(
            json.dumps({
                "schema_version": 1,
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "changes": [],
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (root / DESCRIPTOR_PATH).write_text(
            json.dumps({
                "schema_version": 1,
                "execution_id": self.execution_id,
                "packet_id": self.packet_id,
                "feature_id": FEATURE_ID,
                "source": {"kind": "staged-file", "sdk_message_ref": None},
                "parts": [
                    {"name": name,
                     "artifact_kind": PART_KINDS[name],
                     "staged_path": f".cdad/inbox/{name}.md"}
                    for name in STAGED_PARTS
                ],
                "observed_changes": {
                    "observation_status": "trusted",
                    "baseline_ref": BASELINE_REF,
                    "baseline_sha256": BASELINE_SHA256,
                    "manifest_path": MANIFEST_PATH,
                },
                "run_evidence_ref": None,
            }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")

    # -- paths del fixture (tras la copia) --------------------------------------

    @property
    def execution_context_path(self) -> Path:
        return (self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json")

    @property
    def packet_path(self) -> Path:
        return self.root / ".cdad" / "packets" / self.packet_id / "PACKET.md"

    @property
    def request_path(self) -> Path:
        return self.root / ".cdad" / "packets" / self.packet_id / "REQUEST.json"

    # -- recorrido --------------------------------------------------------------

    def receive(self) -> subprocess.CompletedProcess:
        """`receive` (§2) del entrypoint INSTALADO, cwd = fixture."""
        return self.run_installed([
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(self.root / DESCRIPTOR_PATH),
        ])

    def materialize(self) -> subprocess.CompletedProcess:
        """`materialize` (§2) del entrypoint INSTALADO, cwd = fixture."""
        return self.run_installed([
            "materialize",
            "--project-root", str(self.root),
            "--receipt", str(self.receipt_path),
            "--authorization", str(self.root / ".cdad" / "inbox"
                                   / "MATERIALIZE.json"),
        ])

    def write_authorization(self) -> Path:
        auth_path = self.root / ".cdad" / "inbox" / "MATERIALIZE.json"
        auth_path.write_text(
            json.dumps({
                "schema_version": 1,
                "execution_id": self.execution_id,
                "packet_id": self.packet_id,
                "receipt_sha256": self.receipt_sha256,
                "authorized_by": AUTHORIZED_BY,
                "authority_ref": AUTHORITY_REF,
                "approval_effect": False,
                "copies": [{
                    "part": PART_NAME,
                    "target": TARGET_REPORT,
                    "expected_previous_sha256": None,
                }],
            }, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")
        return auth_path

    def assert_part_bytes(self, name: str, data: bytes) -> None:
        stored = self.final_dir / "parts" / f"{name}.utf8"
        self.assertTrue(
            stored.is_file(),
            msg=f"P1: no se persistió el part {name!r} en {stored}")
        self.assertEqual(
            stored.read_bytes(), data,
            msg=f"P1: el part {name!r} persistido difiere de los bytes staged")

    def assert_target_bytes(self, target: str, data: bytes) -> None:
        stored = self.target_path(target)
        self.assertTrue(
            stored.is_file(),
            msg=f"P4: debe existir el target declarado en la autorización: "
                f"{stored}")
        self.assertEqual(
            stored.read_bytes(), data,
            msg=f"P4: el materializado {target!r} no conserva los bytes "
                f"originales del part (§7)")

    def reconcile_state(self) -> bytes:
        """Simulación del orquestador (§6): mapea la transición lógica
        `received` al estado válido de paquete `completed` (vocabulario de
        001) y registra una referencia pequeña del receipt en stage_history.
        Devuelve el state reconciliado (bytes) para comparar después."""
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        state["active_packet"]["status"] = "completed"
        state["stage_history"].append({
            "feature": FEATURE_ID,
            "stage": "tdd",
            "approved_by": "Pablo",
            "approved_at": "2026-10-05T00:00:01Z",
            "receipt_sha256": self.receipt_sha256,
        })
        state["last_updated"] = "2026-10-05T00:00:01Z"
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        return self.state_path.read_bytes()


# ------------------------------------------------------------------- tests


class TestT4SmokeInstalled(FixtureProjectCase):
    """Smoke instalado — la instalación ofrece el entrypoint y sus esquemas."""

    def test_t4_smoke_installed_entrypoint_and_schemas_exist(self) -> None:
        """Criterio de aceptación «Smoke instalado funciona desde proyecto
        fixture sin wrappers del repo» + §1: la instalación (--basic,
        runtime opencode) debe ofrecer el entrypoint equivalente
        `.config/opencode/skills/cdad-cycle/scripts/cdad_result.py` y los
        esquemas que necesita (`assets/*.schema.json`) dentro del árbol
        instalado; además `install.sh --basic` debe terminar rc=0."""
        self.assertEqual(
            self.install_result.returncode, 0,
            msg=f"Smoke: la instalación aislada (--basic) debe tener éxito:\n"
                f"{err_text(self.install_result) or out_text(self.install_result)}")
        self.assertTrue(
            self.installed_result.is_file(),
            msg=f"Smoke: la instalación debe exponer el entrypoint en "
                f"{self.installed_result}")
        assets = self.install_root / SKILL_REL / "assets"
        missing = [name for name in REQUIRED_SCHEMAS
                   if not (assets / name).is_file()]
        self.assertEqual(
            missing, [],
            msg=f"Smoke: la instalación no ofrece los esquemas que el "
                f"entrypoint necesita (§1 assets/*.schema.json): {missing}")


class TestT4IntegrationWalkthrough(FixtureProjectCase):
    """Recorrido receive → materialize desde el proyecto fixture (P1/P4)."""

    def test_t4_receive_then_materialize_from_installed_entrypoint(self) -> None:
        """P1/P4 + criterio «Smoke instalado»: desde el proyecto fixture y
        con el entrypoint INSTALADO, `receive` persiste cada part con bytes
        idénticos bajo `.cdad/runtime/results/<execution_id>/<packet_id>/`
        (§5), escribe en stdout exactamente los bytes del receipt canónico y
        `materialize` copia los bytes originales al target exacto declarado
        en la autorización (§7), con exit 0 en ambos."""
        before = tree_snapshot(self.root)
        proc = self.receive()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P1: receive (instalado) debe tener éxito desde el "
                f"proyecto fixture: rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P1: receive terminó con traceback")
        receipt_bytes = self.receipt_path.read_bytes()
        self.assertEqual(
            proc.stdout, receipt_bytes,
            msg="P1: stdout debe ser exactamente los bytes del receipt.json "
                "canónico (§2)")
        for name, data in STAGED_PARTS.items():
            self.assert_part_bytes(name, data)

        auth = self.write_authorization()
        mat = self.materialize()
        self.assertEqual(
            mat.returncode, 0,
            msg=f"P4: materialize (instalado) debe aplicar la autorización "
                f"válida: rc={mat.returncode} stdout={out_text(mat)!r} "
                f"stderr={err_text(mat)!r}")
        self.assertNotIn("Traceback", err_text(mat),
                         msg="P4: materialize terminó con traceback")
        self.assert_target_bytes(TARGET_REPORT, STAGED_PARTS[PART_NAME])
        # Sólo targets + store/journal bajo `.cdad/` cambian (§9).
        changed = sorted(
            rel for rel, data in tree_snapshot(self.root).items()
            if before.get(rel) != data)
        for rel in changed:
            self.assertTrue(
                rel == TARGET_REPORT or rel.startswith(".cdad/"),
                msg=f"P1/P4: el recorrido escribió fuera de los targets y "
                    f"del store operacional: {rel}")


class TestT4IdempotentIntegration(FixtureProjectCase):
    """Invariantes de integración — una sola finalización; retry sin efectos
    duplicados (P2 + invariantes §9)."""

    def setUp(self) -> None:
        super().setUp()
        self.first_receive = self.receive()
        self.assertEqual(
            self.first_receive.returncode, 0,
            msg=f"precondición (fixture): el receive inicial debe tener "
                f"éxito: rc={self.first_receive.returncode} "
                f"stdout={out_text(self.first_receive)!r} "
                f"stderr={err_text(self.first_receive)!r}")
        self.durable_receipt = self.receipt_path.read_bytes()
        self.auth = self.write_authorization()
        self.first_materialize = self.materialize()
        self.assertEqual(
            self.first_materialize.returncode, 0,
            msg=f"precondición (fixture): el materialize inicial debe tener "
                f"éxito: rc={self.first_materialize.returncode} "
                f"stdout={out_text(self.first_materialize)!r} "
                f"stderr={err_text(self.first_materialize)!r}")

    def test_t4_single_durable_completion_receive_retry_byte_identical(self) -> None:
        """P2 + invariante «una pareja execution/packet tiene como máximo un
        bundle final durable»: el retry de receive converge al mismo receipt
        durable byte a byte, NO duplica efectos (una sola finalización: los
        parts persistidos siguen siendo los originales y no hay segunda
        copia) (§5)."""
        retry = self.receive()
        self.assertEqual(
            retry.returncode, 0,
            msg=f"P2: el retry de receive debe converger al receipt durable: "
                f"rc={retry.returncode} stdout={out_text(retry)!r} "
                f"stderr={err_text(retry)!r}")
        self.assertEqual(
            retry.stdout, self.durable_receipt,
            msg="P2: el retry de receive debe devolver el mismo receipt "
                "durable byte a byte (§5)")
        self.assertEqual(
            self.receipt_path.read_bytes(), self.durable_receipt,
            msg="P2: el receipt durable no cambió tras el retry")
        for name, data in STAGED_PARTS.items():
            self.assert_part_bytes(name, data)

    def test_t4_materialize_retry_idempotent_targets_unchanged(self) -> None:
        """P2/P4 + invariante «los bytes persistidos y materializados
        conservan SHA-256 y longitud»: el retry de materialize es idempotente
        (§7), NO duplica efectos y los bytes de destino siguen siendo los
        originales."""
        before = tree_snapshot(self.root)
        retry = self.materialize()
        self.assertEqual(
            retry.returncode, 0,
            msg=f"P2/P4: el retry de materialize debe ser idempotente: "
                f"rc={retry.returncode} stdout={out_text(retry)!r} "
                f"stderr={err_text(retry)!r}")
        self.assert_target_bytes(TARGET_REPORT, STAGED_PARTS[PART_NAME])
        after = tree_snapshot(self.root)
        changed = sorted(
            rel for rel, data in after.items() if before.get(rel) != data)
        for rel in changed:
            self.assertTrue(
                rel.startswith(".cdad/"),
                msg=f"P2/P4: el retry de materialize sólo puede tocar el "
                    f"journal/store bajo `.cdad/`, nunca duplicar efectos "
                    f"en targets: {rel}")


class TestT4StateOwnership(FixtureProjectCase):
    """Ninguna herramienta escribe el state (§9 + criterio de aceptación)."""

    def test_t4_walkthrough_leaves_state_byte_identical(self) -> None:
        """Invariante §9 «docs/.cdad-state.json sólo lo cambia el
        orquestador; receive, materialize y run-evidence no lo tocan» +
        criterio «el recorrido de integración receive → reconcile →
        materialize no duplica efectos ni escribe state desde las
        herramientas»: el state del fixture queda byte-idéntico antes y
        después de TODO el recorrido (receive + materialize + retries)."""
        state_before = self.state_path.read_bytes()
        first = self.receive()
        self.assertEqual(
            first.returncode, 0,
            msg=f"P3: receive (instalado) debe tener éxito: "
                f"rc={first.returncode} stdout={out_text(first)!r} "
                f"stderr={err_text(first)!r}")
        self.write_authorization()
        mat = self.materialize()
        self.assertEqual(
            mat.returncode, 0,
            msg=f"P4: materialize (instalado) debe tener éxito: "
                f"rc={mat.returncode} stdout={out_text(mat)!r} "
                f"stderr={err_text(mat)!r}")
        retry_receive = self.receive()
        self.assertEqual(
            retry_receive.returncode, 0,
            msg=f"P2: retry de receive debe tener éxito: "
                f"rc={retry_receive.returncode} "
                f"stdout={out_text(retry_receive)!r} "
                f"stderr={err_text(retry_receive)!r}")
        retry_mat = self.materialize()
        self.assertEqual(
            retry_mat.returncode, 0,
            msg=f"P4: retry de materialize debe tener éxito: "
                f"rc={retry_mat.returncode} "
                f"stdout={out_text(retry_mat)!r} "
                f"stderr={err_text(retry_mat)!r}")
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="§9: ninguna herramienta de 003-002 (receive/materialize) "
                "debe modificar docs/.cdad-state.json durante el recorrido; "
                "el único escritor es el orquestador")


class TestT4RetryAfterReconciledState(FixtureProjectCase):
    """Retry con el state YA reconciliado (§5 + plan T4)."""

    def test_t4_retry_after_orchestrator_transition_repeats_no_effect(self) -> None:
        """Plan T4: «retry con state ya reconciliado no repite efecto».
        Tras simular la transición del orquestador (mapear
        `state_transition_requested` `received` al estado válido de paquete
        `completed` + una referencia pequeña en stage_history), el retry de
        receive converge al mismo receipt byte a byte (§5: el retry
        read-only funciona aunque el orquestador ya haya avanzado el
        packet) y el retry de materialize no repite el efecto (los bytes de
        destino siguen siendo los originales)."""
        first = self.receive()
        self.assertEqual(
            first.returncode, 0,
            msg=f"precondición (fixture): receive debe tener éxito: "
                f"rc={first.returncode} stdout={out_text(first)!r} "
                f"stderr={err_text(first)!r}")
        durable = self.receipt_path.read_bytes()
        self.write_authorization()
        mat = self.materialize()
        self.assertEqual(
            mat.returncode, 0,
            msg=f"precondición (fixture): materialize debe tener éxito: "
                f"rc={mat.returncode} stdout={out_text(mat)!r} "
                f"stderr={err_text(mat)!r}")

        # Transición del orquestador (única escritura del state permitida).
        reconciled = self.reconcile_state()
        # El baseline de efectos se toma DESPUÉS de la transición simulada:
        # el cambio del state es del orquestador, no de las herramientas.
        targets_before = tree_snapshot(self.root)
        self.assertEqual(
            targets_before.get("docs/.cdad-state.json"), reconciled,
            msg="precondición: el baseline post-transición debe contener el "
                "state reconciliado")

        retry = self.receive()
        self.assertEqual(
            retry.returncode, 0,
            msg=f"§5/plan T4: el retry de receive con el state ya "
                f"reconciliado debe converger: rc={retry.returncode} "
                f"stdout={out_text(retry)!r} stderr={err_text(retry)!r}")
        self.assertEqual(
            retry.stdout, durable,
            msg="§5: el retry con el packet avanzado por el orquestador "
                "debe devolver el mismo receipt durable byte a byte")
        # El state reconciliado no lo vuelve a tocar ninguna herramienta.
        self.assertEqual(
            self.state_path.read_bytes(), reconciled,
            msg="§9: el retry no debe modificar el state ya reconciliado "
                "por el orquestador")
        retry_mat = self.materialize()
        self.assertEqual(
            retry_mat.returncode, 0,
            msg=f"plan T4: el retry de materialize con el state ya "
                f"reconciliado no repite el efecto: rc={retry_mat.returncode} "
                f"stdout={out_text(retry_mat)!r} stderr={err_text(retry_mat)!r}")
        self.assert_target_bytes(TARGET_REPORT, STAGED_PARTS[PART_NAME])
        after = tree_snapshot(self.root)
        changed = sorted(
            rel for rel, data in after.items()
            if targets_before.get(rel) != data)
        for rel in changed:
            self.assertTrue(
                rel.startswith(".cdad/"),
                msg=f"plan T4: el retry con el state ya reconciliado no "
                    f"debe repetir efectos fuera del journal/store: {rel}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
