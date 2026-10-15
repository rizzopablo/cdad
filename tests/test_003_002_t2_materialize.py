#!/usr/bin/env python3
"""003-002 T2 RED — materialización por política de artefactos (P4; P3/P6 parte).

Contract:
- docs/specs/003-002-artifact-tools/spec.md (§7 materialización explícita;
  P4, P3-parte, P6-parte; invariantes §9 y verificación de postcondiciones)
- docs/specs/003-002-artifact-tools/plan.md (T2; test focal declarado
  `tests/test_003_002_t2_materialize.py`).

Superficie observable bajo prueba (§2 del contrato; nada de plomería):

    python3 scripts/cdad_result.py materialize \
        --project-root ROOT \
        --receipt RECEIPT.json \
        --authorization MATERIALIZE.json

Semántica de la autorización (§7 + precisión del plan T2): la tabla cerrada
fija la **raíz permitida** por `artifact_kind` y el **target exacto se declara
en la autorización** (no se infiere del texto del payload). `expected_previous_sha256=null` es create-only
(el target debe estar ausente, salvo que ya contenga los bytes nuevos, caso
idempotente); un digest no nulo autoriza reemplazo CAS sólo contra el contenido
actual exacto; otro digest produce conflicto sin sobrescribir. El journal es
durable y el retry multi-copy es idempotente; la responsabilidad declarada es
"continúa desde el journal, omitiendo copias ya aplicadas e idénticas, sin
prometer atomicidad global". `approval_effect` es siempre `false` y el comando
no modifica el state ni el receipt (P3/P6).

Fixtures offline: proyecto sintético v2 (misma maquinaria que T1: `prepare`
de 001, observación I8, parts staged bajo `.cdad/inbox`, manifest vacío
trusted) + `receive` de T1 para obtener el recibo durable. Las corridas de
`materialize` contra el fixture se ejecutan con `cwd` en la raíz del fixture:
los targets declarados son project-relative, no cwd-relative (un target mal
resuelto cae dentro del fixture, nunca en este repo).

RED hoy: el comando `materialize` no existe aún (T1 publicó `receive`); cada
aserción falla con rc≠0 por comportamiento ausente (y los negativos guardan
que el rechazo nombra el motivo del comportamiento, no la ausencia del CLI),
nunca por ImportError o syntax error.
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

from test_004_002_t2_bootstrap import (
    tree_snapshot,
)

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"   # runtime v2 de 001 (no se redefine)
RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"   # helper de 003-002 (materialize aún inexistente)

POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
FEATURE_ID = "003-002-artifact-tools"
EPIC_ID = "epic-003-context-efficiency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
AUTHORITY_REF_VALID = AUTHORITY_REF
AUTHORITY_REF_OTHER = "docs/epics/epic-otra-feature/execution.md"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture 003-002 (T2 RED)\n"

ROLE = "test-writer"
SUBSTAGE = "red"
ATTEMPT_ID = "attempt-t2-red-001"
AUTHORIZED_BY = "Pablo (HITL delegada al orquestador OpenCode)"

# staged part del fixture con materialización declarada (§7; kind de la tabla
# cerrada para test-writer no-audit: raíz permitida `docs/specs/<feature>/`).
PART_BYTES = (
    b"# Role report (fixture T2 RED)\n"
    b"Evidencia mecanica del intento test-writer/red de 003-002.\n"
)
STAGED_PARTS: dict[str, bytes] = {
    "role-report": PART_BYTES,
    "role-notes": (
        b"# Role notes (fixture T2 RED)\n"
        b"Notas auxiliares del mismo intento.\n"
    ),
}
PART_KINDS: dict[str, str] = {
    "role-report": "test-writer-role-report",
    "role-notes": "test-writer-notes",
}
PART_NAME = "role-report"

# raíz permitida para el kind del part (tabla §7 test-writer no-audit) y
# targets exactos declarados en la autorización.
ALLOWED_ROOT = f"docs/specs/{FEATURE_ID}/"
TARGET_REPORT = ALLOWED_ROOT + "test-writer-role-report.md"
TARGET_SECOND = ALLOWED_ROOT + "test-writer-red-copy.md"

# bytes previos conocidos para los casos CAS (contenido actual del target).
PRIOR_BYTES = b"# contenido previo (fixture CAS T2)\n"
OTHER_BYTES = b"# contenido otro (no es el previo declarado)\n"

DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"
MANIFEST_PATH = ".cdad/inbox/changes.json"
BASELINE_REF = "orchestrator-prepared-reference"
BASELINE_SHA256 = "0" * 64


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
    """Guard anti-RED inválida: el fallo del CLI no debe indicar ausencia del
    comando/módulo (eso es RED falsa); debe nombrar el comportamiento."""
    for marker in CLI_AUSENTE_MARKERS:
        assert marker not in stderr, (
            f"RED inválida ({contexto}): el fallo es por CLI ausente "
            f"({marker!r} en stderr), no por el comportamiento bajo prueba: "
            f"{stderr!r}")


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


class MaterializeProjectCase(unittest.TestCase):
    """Proyecto sintético con paquete dispatched y receipt durable de T1."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-002-t2-red-")
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

    def new_dispatched_project(self) -> None:
        """Proyecto sintético nuevo (tempdir), paquete dispatched listo."""
        tmp = tempfile.mkdtemp(prefix="cdad-003-002-t2red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.root = self.build_project(Path(tmp) / "proj")
        self.establish_dispatched()

    def build_project(self, root: Path) -> Path:
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

    def establish_dispatched(self) -> None:
        """Prepara el paquete del fixture y lo observa como dispatched (I8)."""
        prep = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--role", ROLE, "--substage", SUBSTAGE,
            "--objective", "T2 objective",
        ])
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` debe tener éxito: "
                f"{out_text(prep)} {err_text(prep)}")
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
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
        # Registro I8 del intento (claves cerradas del documento de despacho).
        observation_path = self.root / "docs" / "observations-t2.json"
        observation_path.write_text(json.dumps({
            "runtime": "opencode",
            "model_configured": "glm-5.3-flash",
            "model_reported": "glm-5.3-flash",
            "session": "ses-003-002-t2-red-0001",
            "started_at": "2026-10-05T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): el paquete activo debe quedar "
                "dispatched (status I8)")

    def establish_received(self) -> None:
        """Fixture hasta el recibo durable de T1 (receive idéntico y verde)."""
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in STAGED_PARTS.items():
            (inbox / f"{name}.md").write_bytes(data)
        manifest_doc = {
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": BASELINE_REF,
            "baseline_sha256": BASELINE_SHA256,
            "changes": [],
        }
        (self.root / MANIFEST_PATH).write_text(
            json.dumps(manifest_doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        descriptor_doc = {
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
        }
        descriptor_path = self.root / DESCRIPTOR_PATH
        descriptor_path.write_text(
            json.dumps(descriptor_doc, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
        proc = self.run_receive_cli([
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(descriptor_path),
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): `receive` de T1 debe tener éxito: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
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
        targets declarados son project-relative, no cwd-relative (un target
        mal resuelto debe caer dentro del fixture, nunca en este repo)."""
        return subprocess.run(
            [sys.executable, str(RESULT_SCRIPT), *args],
            cwd=self.root, capture_output=True,
        )

    def run_receive_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        """Corrida de `receive` (T1) —argv §2; cwd REPO_ROOT como en T1."""
        return subprocess.run(
            [sys.executable, str(RESULT_SCRIPT), *args],
            cwd=REPO_ROOT, capture_output=True,
        )

    # -- autorización (§7) --------------------------------------------------

    def build_authorization(
            self, copies: list[dict], *,
            receipt_sha: str | None = None,
            authority_ref: str = AUTHORITY_REF_VALID,
            execution_id: str | None = None,
            packet_id: str | None = None,
            approval_effect: bool = False) -> dict:
        assert copies and all(
            c.get("part") and c.get("target") is not None
            and c.get("expected_previous_sha256", "missing") != "missing"
            for c in copies), "precondición: copies completas"
        return {
            "schema_version": 1,
            "execution_id": execution_id or self.execution_id,
            "packet_id": packet_id or self.packet_id,
            "receipt_sha256": receipt_sha or self.receipt_sha256,
            "authorized_by": AUTHORIZED_BY,
            "authority_ref": authority_ref,
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

    # -- oráculos de efectos --------------------------------------------------

    def target_path(self, target: str) -> Path:
        return self.root / target

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

    def assert_no_state_change(self, before: bytes | None = None) -> None:
        state = self.state_path.read_bytes()
        if before is not None:
            self.assertEqual(
                state, before,
                msg="P4: materialize no debe modificar docs/.cdad-state.json "
                    "(§9: el único escritor es el orquestador)")

    def assert_receipt_untouched(self) -> None:
        """P4/P3: materialize no agrega marcas de aprobación ni toca el
        receipt (§7: approval_effect siempre false, semantic_status intacto)."""
        self.assertTrue(
            self.receipt_path.is_file(),
            msg="precondición: receipt durable desapareció")
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt["semantic_status"], "pending",
            msg="P4: semantic_status del receipt debe permanecer `pending` "
                "(la materialización no aprueba nada)")


# ------------------------------------------------------------------- P4


class TestP4CreateOnlyExactTargets(MaterializeProjectCase):
    """P4 — creación create-only hacia targets exactos declarados en auth."""

    def test_p4_create_only_copies_exact_bytes_to_declared_targets_idempotently(self) -> None:
        """P4: con `expected_previous_sha256=null` y targets ausentes,
        materializar copia los bytes originales del part a los targets
        exactos declarados en la autorización (raíz permitida por kind
        `docs/specs/<feature>/`), registra SHA-256 final, no toca ni el state
        ni el receipt, sólo escribe los targets + el store/journal bajo
        `.cdad/`, y repetir la autorización idéntica es idempotente (§7)."""
        self.new_dispatched_project()
        self.establish_received()
        copies = [
            {"part": PART_NAME, "target": TARGET_REPORT,
             "expected_previous_sha256": None},
            {"part": PART_NAME, "target": TARGET_SECOND,
             "expected_previous_sha256": None},
        ]
        auth_path = self.write_authorization(self.build_authorization(copies))
        before = tree_snapshot(self.root)
        state_before = self.state_path.read_bytes()
        receipt_before = self.receipt_path.read_bytes()

        proc = self.materialize(auth_path)
        self.assertNotIn(
            "invalid choice", err_text(proc),
            msg="P4: el comando `materialize` no existe aún (RED por CLI "
                "ausente): los argv declarados en §2 son obligatorios")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P4: materialize debe aplicar la autorización válida: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P4: materialize terminó con traceback")

        # Target exacto declarado en la autorización (§7).
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        self.assert_target_bytes(TARGET_SECOND, PART_BYTES)
        # State, receipt y paquete intactos.
        self.assert_no_state_change(state_before)
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="P4: materialize no debe modificar el receipt durable")
        # Sólo targets + journal/store bajo `.cdad/` (§9 propiedad del estado).
        after = tree_snapshot(self.root)
        changed = sorted(
            rel for rel, data in after.items() if before.get(rel) != data)
        for rel in changed:
            self.assertTrue(
                rel in (TARGET_REPORT, TARGET_SECOND) or rel.startswith(".cdad/"),
                msg=f"P4: materialize escribió fuera de los targets "
                    f"declarados y del store/journal: {rel}")

        # Idempotencia: repetir con iguales bytes es idempotente (§7).
        second = self.materialize(auth_path)
        self.assertEqual(
            second.returncode, 0,
            msg=f"P4: repetir la autorización idéntica debe ser idempotente: "
                f"rc={second.returncode} stdout={out_text(second)!r} "
                f"stderr={err_text(second)!r}")
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        self.assert_target_bytes(TARGET_SECOND, PART_BYTES)
        self.assert_no_state_change(state_before)
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="P4: el retry idéntico no debe modificar el receipt")
        self.assert_receipt_untouched()


class TestP4RejectedTargets(MaterializeProjectCase):
    """P4 — target fuera de la raíz permitida por artifact_kind / escape."""

    def test_p4_target_outside_allowed_root_fails_without_writing(self) -> None:
        """P4: un target declarado bajo otra raíz que la permitida para el
        `artifact_kind` del part (p. ej. test-writer no-audit bajo
        `docs/systemPatterns.md`, `src/…` o la spec de otra feature) falla
        sin sobrescribir/crear: rc≠0, stdout vacío, diagnóstico por stderr y
        el target no aparece (§7)."""
        for label, target in {
            "raíz scribe": "docs/systemPatterns.md",
            "raíz implementación": "src/role-report.md",
            "raíz otra feature": "docs/specs/003-003-loop-detection/report.md",
        }.items():
            with self.subTest(caso=label):
                self.new_dispatched_project()
                self.establish_received()
                auth = self.build_authorization([{
                    "part": PART_NAME, "target": target,
                    "expected_previous_sha256": None,
                }])
                auth_path = self.write_authorization(auth)
                state_before = self.state_path.read_bytes()

                proc = self.materialize(auth_path)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P4 ({label}): un target fuera de la raíz permitida "
                        f"por artifact_kind debe rechazarse")
                assert_reachable_or_invalid_red(
                    err_text(proc),
                    f"P4 ({label}): rechazo por raíz no permitida")
                self.assertNotIn("Traceback", err_text(proc),
                                 msg=f"P4 ({label}): fallo con traceback")
                self.assertEqual(
                    proc.stdout, b"",
                    msg=f"P4 ({label}): el rechazo no debe emitir "
                        f"evidencia por stdout")
                self.assertFalse(
                    self.target_path(target).exists(),
                    msg=f"P4 ({label}): el rechazo creó el target "
                        f"{target!r} fuera de la raíz permitida")
                self.assert_no_state_change(state_before)
                # El diagnóstico nombra el motivo (§7).
                self.assertTrue(
                    re.search(
                        r"target|ra[íi]z|scope|pol[íi]tica|artifact",
                        err_text(proc), re.IGNORECASE),
                    msg=f"P4 ({label}): el diagnóstico no nombra el motivo "
                        f"(spec §7 target/raíz/política): "
                        f"{err_text(proc)!r}")

    def test_p4_project_root_escape_rejected(self) -> None:
        """P4: un target que escapa del project root (traversal `../`,
        `…/../` o path absoluto externo) falla sin escribir nada fuera de la
        raíz (§7: el target debe permanecer bajo project root)."""
        for label, escape_case in {
            "traversal ..": lambda: "../escape-t2.md",
            "traversal mezclado": lambda: f"{ALLOWED_ROOT}../escape-t2.md",
            "absoluto externo": lambda: str(
                self.root.parent / "escape-above-root.md"),
        }.items():
            with self.subTest(caso=label):
                escape_target = escape_case()
                self.new_dispatched_project()
                self.establish_received()
                auth = self.build_authorization([{
                    "part": PART_NAME, "target": escape_target,
                    "expected_previous_sha256": None,
                }])
                auth_path = self.write_authorization(auth)
                state_before = self.state_path.read_bytes()

                proc = self.materialize(auth_path)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P4 ({label}): un target que escapa del project "
                        f"root debe rechazarse")
                assert_reachable_or_invalid_red(
                    err_text(proc), f"P4 ({label}): rechazo por escape")
                self.assertNotIn("Traceback", err_text(proc),
                                 msg=f"P4 ({label}): fallo con traceback")
                self.assertEqual(
                    proc.stdout, b"",
                    msg=f"P4 ({label}): el rechazo no debe emitir stdout")
                self.assert_no_state_change(state_before)
                # Nada escrito en la ruta de escape (resuelta contra el
                # project root para targets relativos).
                escaped = (Path(escape_target)
                           if Path(escape_target).is_absolute()
                           else self.root / escape_target)
                self.assertFalse(
                    escaped.exists(),
                    msg=f"P4 ({label}): el escape escribió {escaped} fuera "
                        f"del project root")


class TestP4BindingDiscordance(MaterializeProjectCase):
    """P4 — receipt/authority discordante falla sin escribir (§7)."""

    def test_p4_receipt_sha256_discordant_fails_without_writing(self) -> None:
        """P4: la autorización ligada a un digest de receipt distinto del
        durable falla sin aplicar copias ni tocar el state (§7 authority
        binding)."""
        self.new_dispatched_project()
        self.establish_received()
        auth = self.build_authorization(
            [{"part": PART_NAME, "target": TARGET_REPORT,
              "expected_previous_sha256": None}],
            receipt_sha="f" * 64)
        auth_path = self.write_authorization(auth)
        state_before = self.state_path.read_bytes()
        receipt_before = self.receipt_path.read_bytes()

        proc = self.materialize(auth_path)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P4: receipt_sha256 discordante del receipt durable debe "
                "rechazarse (§7)")
        assert_reachable_or_invalid_red(err_text(proc),
                                        "P4: rechazo por receipt discordante")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P4: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="P4: el rechazo no debe emitir evidencia por stdout")
        self.assertFalse(
            self.target_path(TARGET_REPORT).exists(),
            msg="P4: el rechazo por receipt discordante creó el target")
        self.assert_no_state_change(state_before)
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="P4: el rechazo modificó el receipt durable")

    def test_p4_authority_or_identity_discordant_fails_without_writing(self) -> None:
        """P4: authority_ref distinto del binding vigente del contexto de
        ejecución, o execution/packet id ajenos al receipt, fallan sin
        aplicar copias (§7 authority binding / identidad)."""
        cases = {
            "authority_ref ajeno": {"authority_ref": AUTHORITY_REF_OTHER},
            "packet_id ajeno": {"packet_id": "003-002-artifact-tools-otro-packet-001"},
            "execution_id ajeno": {"execution_id": "exec-003-002-artifact-tools-999"},
        }
        for label, override in cases.items():
            with self.subTest(caso=label):
                self.new_dispatched_project()
                self.establish_received()
                auth = self.build_authorization(
                    [{"part": PART_NAME, "target": TARGET_REPORT,
                      "expected_previous_sha256": None}],
                    **override)
                auth_path = self.write_authorization(auth)
                state_before = self.state_path.read_bytes()

                proc = self.materialize(auth_path)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P4 ({label}): binding discordante debe rechazarse "
                        f"(§7 authority binding)")
                assert_reachable_or_invalid_red(
                    err_text(proc), f"P4 ({label}): rechazo por binding")
                self.assertNotIn("Traceback", err_text(proc),
                                 msg=f"P4 ({label}): fallo con traceback")
                self.assertEqual(
                    proc.stdout, b"",
                    msg=f"P4 ({label}): el rechazo no debe emitir stdout")
                self.assertFalse(
                    self.target_path(TARGET_REPORT).exists(),
                    msg=f"P4 ({label}): el rechazo creó el target")
                self.assert_no_state_change(state_before)


class TestP4CASAndCreateOnly(MaterializeProjectCase):
    """P4 — CAS contra el digest anterior exacto; create-only estricto."""

    def establish_received_with_target(self, data: bytes) -> None:
        self.establish_received()
        target = self.target_path(TARGET_REPORT)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def test_p4_cas_replaces_only_against_exact_previous_digest(self) -> None:
        """P4: codificando `expected_previous_sha256` con el digest exacto
        del contenido actual, materialize reemplaza el contenido y sostiene
        los bytes originales del part (§7: reemplazo CAS)."""
        self.new_dispatched_project()
        self.establish_received_with_target(PRIOR_BYTES)
        auth = self.build_authorization([{
            "part": PART_NAME, "target": TARGET_REPORT,
            "expected_previous_sha256":
                hashlib.sha256(PRIOR_BYTES).hexdigest(),
        }])
        state_before = self.state_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P4: reemplazo CAS contra el digest anterior exacto debe "
                f"aplicarse: rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        self.assert_no_state_change(state_before)

    def test_p4_cas_wrong_digest_conflicts_without_overwrite(self) -> None:
        """P4: un digest no nulo que no corresponde al contenido actual
        produce conflicto sin overwrite (§7), stdout vacío y target intacto."""
        self.new_dispatched_project()
        self.establish_received_with_target(PRIOR_BYTES)
        auth = self.build_authorization([{
            "part": PART_NAME, "target": TARGET_REPORT,
            "expected_previous_sha256":
                hashlib.sha256(OTHER_BYTES).hexdigest(),
        }])
        state_before = self.state_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P4: CAS con digest que no coincide con el contenido actual "
                "debe fallar (§7)")
        assert_reachable_or_invalid_red(err_text(proc),
                                        "P4: conflicto CAS por digest ajeno")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P4: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"", msg="P4: conflicto sin evidencia por stdout")
        self.assert_target_bytes(TARGET_REPORT, PRIOR_BYTES)
        self.assert_no_state_change(state_before)
        self.assertTrue(
            re.search(
                r"digest|sha|conflict|conflicto|contenido",
                err_text(proc), re.IGNORECASE),
            msg="P4: el diagnóstico no nombra el conflicto CAS (spec §7): "
                f"{err_text(proc)!r}")

    def test_p4_create_only_divergent_target_conflicts_without_overwrite(self) -> None:
        """P4: `expected_previous_sha256=null` sobre un target con contenido
        divergente (no son los bytes nuevos) falla sin sobrescribir (§7)."""
        self.new_dispatched_project()
        self.establish_received_with_target(PRIOR_BYTES)
        auth = self.build_authorization([{
            "part": PART_NAME, "target": TARGET_REPORT,
            "expected_previous_sha256": None,
        }])
        state_before = self.state_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P4: create-only debe rechazar un target con contenido "
                "divergente (§7)")
        assert_reachable_or_invalid_red(err_text(proc),
                                        "P4: conflicto create-only divergente")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P4: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"", msg="P4: conflicto sin evidencia por stdout")
        self.assert_target_bytes(TARGET_REPORT, PRIOR_BYTES)
        self.assert_no_state_change(state_before)

    def test_p4_create_only_target_already_new_is_idempotent(self) -> None:
        """P4: `expected_previous_sha256=null` sobre un target que ya contiene
        exactamente los bytes nuevos es el caso idempotente declarado (§7):
        éxito sin duplicar ni mutar bytes."""
        self.new_dispatched_project()
        self.establish_received_with_target(PART_BYTES)
        auth = self.build_authorization([{
            "part": PART_NAME, "target": TARGET_REPORT,
            "expected_previous_sha256": None,
        }])
        state_before = self.state_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P4: target ya con los bytes nuevos y digest null es el "
                f"caso idempotente (§7): rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        self.assert_no_state_change(state_before)


class TestP4JournalRetryContinuation(MaterializeProjectCase):
    """P4 — retry multi-copy continúa desde lo ya aplicado (journal)."""

    def test_p4_retry_multicopy_continues_over_applied_prefix(self) -> None:
        """P4: con un prefijo aplicado por una corrida anterior (copias ya
        efectuadas e idénticas) el retry multi-copy omite las copias ya
        aplicadas, continúa con las restantes y no repite ni sobreescribe un
        efecto divergente (§7: riesgo limitado por copia, idempotencia de los
        ya aplicados)."""
        self.new_dispatched_project()
        self.establish_received()
        # Prefijo aplicado antes de la interrupción (registro en el journal):
        # copia 1 ya efectuada con los bytes nuevos.
        first = self.target_path(TARGET_REPORT)
        first.parent.mkdir(parents=True, exist_ok=True)
        first.write_bytes(PART_BYTES)
        copies = [
            {"part": PART_NAME, "target": TARGET_REPORT,
             "expected_previous_sha256": None},
            {"part": PART_NAME, "target": TARGET_SECOND,
             "expected_previous_sha256": None},
        ]
        auth = self.build_authorization(copies)
        state_before = self.state_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P4: el retry debe continuar desde el journal (omitiendo la "
                f"copia ya aplicada e idéntica): rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        # Copia ya aplicada: sigue idéntica (sin doble escritura ni mutación).
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        # Copia restante: aplicada exactamente y con registro de SHA final.
        self.assert_target_bytes(TARGET_SECOND, PART_BYTES)
        self.assert_no_state_change(state_before)


class TestP4NoApprovalEffect(MaterializeProjectCase):
    """P4/P3 — la materialización no aprueba y no toca el state (P3 parte)."""

    def test_p4_approval_effect_false_no_state_no_semantic_change(self) -> None:
        """P4/P3: con `approval_effect=false` (único valor de la feature,
        §7), materialize copia los bytes declarados sin agregar marcas de
        aprobación (receipt intacto, `semantic_status=pending`) y sin tocar
        `docs/.cdad-state.json` (invariante verificable: el único escritor del
        state es el orquestador)."""
        self.new_dispatched_project()
        self.establish_received()
        auth = self.build_authorization(
            [{"part": PART_NAME, "target": TARGET_REPORT,
              "expected_previous_sha256": None}],
            approval_effect=False)
        state_before = self.state_path.read_bytes()
        receipt_before = self.receipt_path.read_bytes()
        context_before = self.execution_context_path.read_bytes()

        proc = self.materialize(self.write_authorization(auth))
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P4/P3: materialize con approval_effect=false debe aplicar "
                f"la autorización: rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        self.assert_target_bytes(TARGET_REPORT, PART_BYTES)
        # Sin aprobación: receipt byte-idéntico (semantic_status sigue
        # `pending`, sin marcas) — el receipt es inmutable (§6/§7).
        self.assertEqual(
            self.receipt_path.read_bytes(), receipt_before,
            msg="P4/P3: materialize modificó el receipt durable (ninguna "
                "aprobación agregada)")
        # State intacto: único escritor es el orquestador (§9).
        self.assertEqual(
            self.state_path.read_bytes(), state_before,
            msg="P4/P3: materialize no debe modificar docs/.cdad-state.json")
        self.assertEqual(
            self.execution_context_path.read_bytes(), context_before,
            msg="P4/P3: materialize no debe modificar el contexto de "
                "ejecución v2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
