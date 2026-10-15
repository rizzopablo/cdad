#!/usr/bin/env python3
"""004-002 T2 RED — Bootstrap autorizado e identidad (PD-3, PD-4, PD-10).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-3, PD-4, PD-10) + docs/specs/004-002-project-execution-bootstrap/plan.md
(decisiones de interfaz I2, I3, I4 del orquestador).

Superficie observable bajo prueba (ninguna escritura en este repo; los
proyectos son fixtures sintéticos en tempdirs):

    python3 scripts/cdad_packet.py prepare --project-root <raíz> \
        --role <rol> --substage <subfase> --objective <encargo> [opciones]
    python3 scripts/cdad_packet.py validate-state --project-root <raíz>

NUEVO `prepare` bajo T2 (contrato v2): `--new-execution`, `--resume-packet
<id>`, `validate-state` sin `--execution-context`, contexto v2 en
`.cdad/executions/<id>/execution.json` (`schema_version: 2`) y rechazo de
contextos v1 sin flag explícito. Opciones que NO deben existir:
`--migrate-execution` (PD-10).

Fixtures (I2 — autoridad verificable): state con `stage_history` que acredita
la aprobación del contrato (`feature`, `stage: "specification"`,
`approved_by` no vacío), `hitl_delegation` activa con `source` existente y
`scope` que nombra el epic activo, feature `in-progress` en `epic_features`
igual a `active_feature`, y política válida en `docs/cdad-policy.json`.

RED hoy: el bootstrap implícito no existe (la preparación ordinaria exige
`--execution-context`), `--new-execution`/`--resume-packet` no existen y no
hay contexto v2; cada aserción expresa el comportamiento de la postcondición,
no la mecánica del CLI.
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
SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-004-single-source-planning"
FEATURE_ID = "004-002-project-execution-bootstrap"
OTHER_FEATURE_ID = "004-002-other-active-feature"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture for 004-002 T2 bootstrap tests\n"

PACKET_BEGIN = "---cdad-packet-json"


# ---------------------------------------------------------------- helpers


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def prepare_args(root: Path, *, role: str = "test-writer",
                 substage: str = "red", objective: str = "T2 objective",
                 extra: tuple[str, ...] = ()) -> list[str]:
    return [
        "prepare", "--project-root", str(root),
        "--role", role, "--substage", substage,
        "--objective", objective, *extra,
    ]


def run_prepare(root: Path, *extra: str, role: str = "test-writer") -> subprocess.CompletedProcess:
    return run_cli(prepare_args(root, role=role, extra=extra))


def run_validate_state(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return run_cli(["validate-state", "--project-root", str(root), *extra])


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Cada entrada bajo root: archivos → bytes, directorios → None."""
    snap: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snap[rel] = path.read_bytes() if path.is_file() else None
    return snap


def write_policy(root: Path) -> None:
    """Política válida de tres campos (soportada por T1)."""
    (root / "docs").mkdir(parents=True, exist_ok=True)
    doc = {
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    }
    (root / POLICY_FILE).write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_contract(root: Path) -> None:
    (root / "docs" / "specs" / FEATURE_ID).mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)


def write_authority_source(root: Path, *, present: bool = True) -> None:
    if not present:
        return
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture\n", encoding="utf-8")


def state_document(
    *,
    epic: str | None = EPIC_ID,
    approved: bool = True,
    delegation: str = "active",  # active | revoked | missing
    delegation_scope: str | None = EPIC_ID,
    feature_status: str = "in-progress",
    epic_features_id: str | None = None,
) -> dict:
    """State sintético con los registros I2 (o sus mutaciones negativas)."""
    stage_history: list[dict] = []
    if approved:
        stage_history.append({
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-09-29T00:00:00Z",
            # 005-001 T1 (D3): forma pineada — sha256 de los bytes que
            # write_contract() escribe en CONTRACT_FILE (migración mecánica).
            "contract_path": CONTRACT_FILE,
            "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
        })
    hitl: dict | None
    if delegation == "active":
        hitl = {
            "status": "active",
            "epic_id": epic or EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID if delegation_scope is None else delegation_scope,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        }
    elif delegation == "revoked":
        hitl = {
            "status": "revoked",
            "epic_id": epic or EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID if delegation_scope is None else delegation_scope,
            "revoked_at": "2026-09-29T12:00:00Z",
        }
    else:
        hitl = None
    return {
        "version": 1,
        "stack": None,
        "active_epic": epic,
        "epic_stage": "features-loop",
        "epic_features": [{"id": epic_features_id or FEATURE_ID,
                           "status": feature_status}],
        "epic_history": [],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": stage_history,
        "approver": "Pablo",
        "last_updated": "2026-09-29T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": hitl,
    }


def write_state(root: Path, state: dict) -> None:
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")


def read_state(root: Path) -> dict:
    return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))


def build_project(root: Path, **state_kwargs) -> Path:
    """Proyecto sintético válido (política + state I2 + contrato + autoridad)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    write_policy(root)
    write_contract(root)
    write_authority_source(root)
    write_state(root, state_document(**state_kwargs))
    return root


def make_project(**state_kwargs) -> tuple[Path, str]:
    tmp = tempfile.mkdtemp(prefix="cdad-t2-red-")
    root = Path(tmp) / "proj"
    build_project(root, **state_kwargs)
    return root, tmp


class ProjectTestCase(unittest.TestCase):
    """Base: proyecto sintético en tempdir propio por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t2-red-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        self.before = tree_snapshot(self.root)
        self.state_before = (self.root / STATE_FILE).read_bytes()

    def assert_state_unchanged(self) -> None:
        self.assertEqual((self.root / STATE_FILE).read_bytes(),
                         self.state_before_bytes(),
                         msg="state.json cambió en un caso de fallo")

    def state_before_bytes(self) -> bytes:
        return self.before[STATE_FILE]


def packets_dir(root: Path) -> Path:
    return root / ".cdad" / "packets"


def executions_dir(root: Path) -> Path:
    return root / ".cdad" / "executions"


def v2_execution_docs(root: Path) -> dict[str, dict]:
    """Los contextos v2 publicados bajo .cdad/executions (orclé de contenido)."""
    docs: dict[str, dict] = {}
    base = executions_dir(root)
    if not base.is_dir():
        return docs
    for path in sorted(base.glob("*/execution.json")):
        docs[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
    return docs


def published_packets(root: Path) -> dict[str, bytes]:
    pkts: dict[str, bytes] = {}
    base = packets_dir(root)
    if not base.is_dir():
        return pkts
    for path in sorted(base.glob("*/PACKET.md")):
        pkts[path.parent.name] = path.read_bytes()
    return pkts


def policy_hash(root: Path) -> str:
    return hashlib.sha256((root / POLICY_FILE).read_bytes()).hexdigest()


def diagnostic(output: str, *patterns: str) -> str | None:
    """Devuelve la línea de diagnóstico que menciona alguno de los patrones."""
    for line in output.splitlines():
        if any(re.search(p, line, re.IGNORECASE) for p in patterns):
            return line
    return None


# ---------------------------------------------------------------- PD-3


class TestPd3BootstrapAuthorized(ProjectTestCase):
    """PD-3 / I3: bootstrap implícito de una ejecución v2 autorizada."""

    def test_pd3_implicit_bootstrap_creates_v2_context_binding_and_packet(self) -> None:
        """PD-3/I3: sin ningún contexto previo, `prepare` (sin
        --execution-context) crea .cdad/executions/<id>/execution.json con
        schema_version 2, feature, epic, scope, authority_ref y hash de la
        política vigente; state.execution referencia esa ejecución; publica el
        paquete; validate-state sin --execution-context da VALID con ese id."""
        proc = run_prepare(self.root)
        self.assertNotIn("unrecognized", proc.stdout + proc.stderr,
                         msg="--new-execution no es necesario y otras opciones fallan")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"bootstrap implícito debe tener éxito: {proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"se esperaba exactamente un contexto v2, hay: {sorted(docs)}")
        execution_id, doc = next(iter(docs.items()))
        self.assertEqual(
            doc.get("schema_version"), 2,
            msg=f"schema_version del contexto v2: {doc.get('schema_version')!r}")
        execution = doc.get("execution", doc)
        self.assertEqual(execution.get("feature_id"), FEATURE_ID,
                         msg=f"feature en el contexto: {execution.get('feature_id')!r}")
        self.assertEqual(execution.get("epic_id"), EPIC_ID,
                         msg=f"epic en el contexto: {execution.get('epic_id')!r}")
        self.assertTrue(execution.get("scope"),
                        msg="scope faltante en el contexto v2")
        self.assertTrue(execution.get("authority_ref"),
                        msg="authority_ref faltante en el contexto v2")
        self.assertIn(policy_hash(self.root),
                      json.dumps(doc),
                      msg="el contexto v2 no contiene el hash de la política vigente")
        # binding en state
        state = read_state(self.root)
        self.assertEqual(
            state.get("execution", {}).get("id"), execution_id,
            msg=f"state.execution no referencia al contexto creado: "
                f"{state.get('execution')!r} vs {execution_id}")
        # paquete publicado (stdout == PACKET.md)
        self.assertTrue(proc.stdout.startswith(PACKET_BEGIN),
                        msg="stdout no comienza con el paquete canónico")
        packets = published_packets(self.root)
        self.assertEqual(
            len(packets), 1, msg=f"paquetes publicados: {sorted(packets)}")
        self.assertEqual(
            next(iter(packets.values())).decode("utf-8"), proc.stdout,
            msg="PACKET.md difiere del stdout de prepare")
        # validate-state resuelve sin --execution-context
        validated = run_validate_state(self.root)
        self.assertEqual(
            validated.returncode, 0,
            msg=f"validate-state sin contexto explícito: "
                f"{validated.stdout} {validated.stderr}")
        self.assertIn(execution_id, validated.stdout + validated.stderr,
                      msg="validate-state no nombra el execution_id activo")

    def test_pd3_standalone_bootstrap_without_epic(self) -> None:
        """PD-12/I2 (standalone, trazado a PD-3): con active_epic null, sin
        delegación y con la aprobación del contrato en stage_history, el
        bootstrap tiene éxito y el contexto v2 y el paquete llevan epic null."""
        self.setUp_standalone()
        proc = run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"bootstrap standalone debe tener éxito: {proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1, msg=f"contextos v2: {sorted(docs)}")
        _, doc = next(iter(docs.items()))
        execution = doc.get("execution", doc)
        self.assertIsNone(
            execution.get("epic_id"),
            msg=f"epic debe ser null en standalone: {execution.get('epic_id')!r}")
        self.assertTrue(proc.stdout.startswith(PACKET_BEGIN),
                        msg="stdout no comienza con el paquete canónico")
        self.assertEqual(
            len(published_packets(self.root)), 1,
            msg="standalone no publicó el paquete")

    def setUp_standalone(self) -> None:
        write_state(self.root, state_document(epic=None, delegation="missing"))


class TestPd3AuthorityNegatives(ProjectTestCase):
    """PD-3/I2: autoridad ausente/inválida → error específico, rc≠0 y ninguna
    publicación (árbol y state idénticos)."""

    def _assert_rejected(self, label: str, *, diagnostic_patterns: tuple[str, ...],
                         state_kwargs: dict | None = None,
                         remove_policy: bool = False,
                         invalid_policy: bool = False) -> None:
        state_kwargs = state_kwargs or {}
        if state_kwargs:
            write_state(self.root, state_document(**state_kwargs))
        if remove_policy:
            (self.root / POLICY_FILE).unlink()
        if invalid_policy:
            doc = json.loads((self.root / POLICY_FILE).read_text(encoding="utf-8"))
            doc["models"] = {"policy": "cheap"}  # campo extra → inválida (PD-1)
            (self.root / POLICY_FILE).write_text(
                json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        # Snapshot DESPUÉS de mutar: el examen de no-publicación compara
        # contra el estado exacto que ve prepare.
        self.before = tree_snapshot(self.root)
        self.state_before = (self.root / STATE_FILE).read_bytes()
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0, msg=f"{label}: prepare fue aceptado")
        self.assertNotIn("Traceback", proc.stderr, msg=f"{label}: fallo con traceback")
        self.assertEqual(proc.stdout, "", msg=f"{label}: stdout no vacío")
        self.assertTrue(
            re.search(diagnostic_patterns[0], out, re.IGNORECASE) or
            any(re.search(p, out, re.IGNORECASE) for p in diagnostic_patterns),
            msg=f"{label}: diagnóstico no nombra el registro faltante "
                f"(patrones {diagnostic_patterns}, salida: {out!r})")
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg=f"{label}: hubo publicación parcial (árbol modificado)")
        self.assert_state_unchanged()

    def test_pd3_negative_contract_not_approved_in_stage_history(self) -> None:
        """PD-3/I2: sin aprobación del contrato (stage_history sin
        approved_by) → rechaza nombrando el registro."""
        self._assert_rejected(
            "sin aprobación del contrato",
            diagnostic_patterns=(r"stage_history|specification|approved",
                                 r"aprobaci|contrato",),
            state_kwargs={"approved": False})

    def test_pd3_negative_delegation_missing_with_active_epic(self) -> None:
        """PD-3/I2: epic activo sin hitl_delegation → rechaza nombrándola."""
        self._assert_rejected(
            "delegación ausente con epic activo",
            diagnostic_patterns=(r"hitl_delegation|delegaci|authority",
                                 r"autoridad",),
            state_kwargs={"delegation": "missing"})

    def test_pd3_negative_delegation_revoked(self) -> None:
        """PD-3/I2: delegación con revoked_at → rechaza nombrando la revocación."""
        self._assert_rejected(
            "delegación revocada",
            diagnostic_patterns=(r"revok|revocad", r"hitl_delegation|delegaci"),
            state_kwargs={"delegation": "revoked"})

    def test_pd3_negative_delegation_scope_does_not_name_epic(self) -> None:
        """PD-3/I2: scope de la delegación que no nombra el epic → rechaza."""
        self._assert_rejected(
            "scope sin epic",
            diagnostic_patterns=(r"scope",),
            state_kwargs={"delegation_scope": "epic-unrelated-other"})

    def test_pd3_negative_feature_closed(self) -> None:
        """PD-3/I2: feature cerrada (status done) → rechaza nombrándola."""
        self._assert_rejected(
            "feature cerrada",
            diagnostic_patterns=(rf"{re.escape(FEATURE_ID)}|epic_features|"
                                 r"status|done|cerrada|in-progress",),
            state_kwargs={"feature_status": "done"})

    def test_pd3_negative_feature_differs_from_active_feature(self) -> None:
        """PD-3/I2: la feature del registro difiere de active_feature → rechaza."""
        self._assert_rejected(
            "feature distinta de active_feature",
            diagnostic_patterns=(rf"{re.escape(FEATURE_ID)}|"
                                 rf"{re.escape(OTHER_FEATURE_ID)}|"
                                 r"active_feature|epic_features",),
            state_kwargs={"epic_features_id": OTHER_FEATURE_ID})

    def test_pd3_negative_policy_missing(self) -> None:
        """PD-3/PD-1/I2: sin docs/cdad-policy.json → rechaza sin defaults silenciosos."""
        self._assert_rejected(
            "política ausente",
            diagnostic_patterns=(r"policy|pol[íi]tica",),
            remove_policy=True)

    def test_pd3_negative_policy_invalid(self) -> None:
        """PD-3/PD-1/I2: política inválida (campo extra) → rechaza."""
        self._assert_rejected(
            "política inválida",
            diagnostic_patterns=(r"policy|pol[íi]tica",),
            invalid_policy=True)


# ---------------------------------------------------------------- PD-4


class TestPd4IdentityAndResume(ProjectTestCase):
    """PD-4: identidad estable entre roles; paquete activo impide reemplazo;
    --resume-packet devuelve bytes idénticos."""

    def prepare_ok(self, *extra: str, role: str = "test-writer",
                   substage: str = "red", label: str) -> subprocess.CompletedProcess:
        args = prepare_args(self.root, role=role, substage=substage,
                            objective=f"encargo {label}", extra=extra)
        proc = run_cli(args)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: {proc.stdout} {proc.stderr}")
        return proc

    def require_bootstrap(self) -> str:
        """Precondición del escenario: un primer prepare debe producir un
        contexto v2. También cubre el fallo RED de hoy (bootstrap ausente)."""
        proc = self.prepare_ok(label="primera preparación")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"primera preparación debe crear un único contexto v2: {sorted(docs)}")
        return next(iter(docs))

    def test_pd4_role_change_keeps_execution_id(self) -> None:
        """PD-4: dos prepare sucesivos (roles distintos, el primero marcado
        completed por el orquestador) conservan execution_id."""
        execution_id = self.require_bootstrap()
        # El orquestador marca el paquete activo como completed.
        state = read_state(self.root)
        self.assertIsNotNone(state.get("active_packet"),
                             msg="primera preparación no dejó paquete activo")
        state["active_packet"]["status"] = "completed"
        write_state(self.root, state)
        # Segunda preparación, rol distinto.
        self.prepare_ok(role="implementer", substage="green",
                        label="segunda preparación (otro rol)")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            sorted(docs), [execution_id],
            msg=f"cambiar el rol creó otro execution_id: {sorted(docs)} != "
                f"[{execution_id}]")
        state = read_state(self.root)
        self.assertEqual(
            state.get("execution", {}).get("id"), execution_id,
            msg="state.execution cambió de identidad tras el segundo prepare")
        self.assertEqual(
            state.get("active_packet", {}).get("role"), "implementer",
            msg="el segundo prepare no publicó su paquete con su rol")

    def test_pd4_active_packet_prepared_or_dispatched_blocks_replacement(self) -> None:
        """PD-4: con paquete activo en `prepared` o `dispatched`, un prepare
        nuevo falla sin reemplazar (state e IDs intactos)."""
        self.require_bootstrap()
        for status in ("prepared", "dispatched"):
            with self.subTest(status=status):
                # Reinicio del escenario por subprueba: restaurar árbol y
                # repetir la primera preparación.
                subprocess.run(["rm", "-rf", str(executions_dir(self.root)),
                                str(packets_dir(self.root))], check=False)
                write_state(self.root, state_document())
                self.prepare_ok(label=f"primera con status {status}")
                state = read_state(self.root)
                state["active_packet"]["status"] = status
                write_state(self.root, state)
                snapshot = tree_snapshot(self.root)
                active_before = read_state(self.root)["active_packet"]
                proc = run_prepare(self.root)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"{status}: prepare reemplazó el paquete activo")
                self.assertEqual(
                    proc.stdout, "", msg=f"{status}: stdout no vacío en fallo")
                active_after = read_state(self.root)["active_packet"]
                self.assertEqual(
                    active_after, active_before,
                    msg=f"{status}: active_packet cambió: "
                        f"{active_before!r} → {active_after!r}")
                self.assertEqual(
                    tree_snapshot(self.root), snapshot,
                    msg=f"{status}: el fallo publicó archivos nuevos")

    def test_pd4_resume_packet_returns_identical_bytes_without_changes(self) -> None:
        """PD-4: `prepare --resume-packet <id>` devuelve exactamente los mismos
        bytes del paquete y no cambia IDs."""
        execution_id = self.require_bootstrap()
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_bytes = published_packets(self.root)[packet_id]
        snapshot = tree_snapshot(self.root)
        # I7 (oráculo firmado): resume puro, sin opciones ordinarias.
        proc = run_cli(["prepare", "--project-root", str(self.root),
                        "--resume-packet", packet_id])
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg=f"--resume-packet no existe: {proc.stderr}")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"resume-packet falló: {proc.stdout} {proc.stderr}")
        self.assertEqual(
            proc.stdout, packet_bytes.decode("utf-8"),
            msg="--resume-packet no devolvió los bytes idénticos del paquete")
        # Paquete activo intacto y en prepared tras la reanudación pura (I7).
        state = read_state(self.root)
        self.assertEqual(
            state.get("active_packet", {}).get("id"), packet_id,
            msg="resume cambió el packet_id activo")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            sorted(docs), [execution_id], msg="resume cambió el execution_id")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="--resume-packet modificó el árbol")

    def test_pd4_resume_packet_with_modifying_options_fails(self) -> None:
        """PD-4: `--resume-packet` con opciones que lo modificarían falla sin
        publicar ni cambiar el paquete activo."""
        execution_id = self.require_bootstrap()
        packet_id = read_state(self.root)["active_packet"]["id"]
        snapshot = tree_snapshot(self.root)
        proc = run_prepare(self.root, "--resume-packet", packet_id,
                           "--objective", "objective que cambia el paquete")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume-packet aceptó opciones que modificarían el paquete")
        self.assertEqual(
            proc.stdout, "", msg="resume fallido publicó stdout")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="resume fallido modificó el árbol")
        self.assertEqual(
            read_state(self.root).get("active_packet", {}).get("id"), packet_id,
            msg="resume fallido cambió el packet_id activo")


# ---------------------------------------------------------------- PD-10 / I3 / I4


class TestPd10ForwardAdoption(ProjectTestCase):
    """PD-10 / I3 / I4: adopción hacia adelante; v1 nunca se convierte ni
    reescribe; --migrate-execution no existe."""

    def setUp(self) -> None:
        super().setUp()

    def write_v1_context(self) -> bytes:
        """Contexto v1 sintético en .cdad/execution.json (cimento de I3/I4)."""
        doc = {
            "schema_version": 1,
            "execution": {
                "id": "exec-legacy-v1",
                "epic_id": EPIC_ID,
                "feature_id": FEATURE_ID,
                "runtime": "opencode",
                "scope": "legacy-scope",
                "model_policy": "ordinary",
                "authority_ref": AUTHORITY_REF,
                "model": {"configured": None, "reported": None},
            },
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src", "lib"],
                "documentation_roots": ["docs"],
                "colocated_test_roots": ["src", "lib"],
                "colocated_test_suffixes": [
                    "_test.go", ".test.js", ".test.ts", ".test.mjs",
                    ".test.cjs", ".spec.js", ".spec.ts",
                ],
                "colocated_test_prefixes": ["test_"],
            },
        }
        cdad = self.root / ".cdad"
        cdad.mkdir(exist_ok=True)
        v1 = cdad / "execution.json"
        v1.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
        return v1.read_bytes()

    def test_pd10_v1_present_without_flag_fails_demanding_new_execution(self) -> None:
        """PD-10/I3: con .cdad/execution.json v1 presente y sin
        --execution-context, prepare falla con diagnóstico que pide
        --new-execution y NO modifica el v1 (bytes idénticos)."""
        v1_bytes = self.write_v1_context()
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="sin --execution-context preparó usando el v1 (adopción "
                "hacia adelante violada)")
        self.assertRegex(
            out, r"--new-execution",
            msg=f"el diagnóstico no pide --new-execution: {out!r}")
        self.assertEqual(
            (self.root / ".cdad" / "execution.json").read_bytes(), v1_bytes,
            msg="el contexto v1 fue modificado")

    def test_pd10_new_execution_flag_creates_v2_leaving_v1_intact(self) -> None:
        """PD-10/I3: `--new-execution` sobre v1 crea una ejecución v2 nueva
        (otro execution_id) dejando el v1 intacto."""
        v1_bytes = self.write_v1_context()
        proc = run_prepare(self.root, "--new-execution")
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg=f"--new-execution no existe: {proc.stderr}")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"new-execution falló: {proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1, msg=f"contextos v2: {sorted(docs)}")
        execution_id, doc = next(iter(docs.items()))
        self.assertEqual(doc.get("schema_version"), 2,
                         msg="el nuevo contexto no es v2")
        self.assertNotEqual(
            execution_id, "exec-legacy-v1",
            msg="--new-execution reutilizó el id del contexto v1")
        self.assertEqual(
            (self.root / ".cdad" / "execution.json").read_bytes(), v1_bytes,
            msg="--new-execution modificó el v1")
        state = read_state(self.root)
        self.assertEqual(
            state.get("execution", {}).get("id"), execution_id,
            msg="state.execution no referencia el contexto v2 nuevo")

    # Trazabilidad v1 (PD-10, T6): el caso de humo del camino v1 explícito
    # (test_pd10_explicit_v1_execution_context_preserves_previous_behavior)
    # fue RETIRADO en este paquete: su garantía (I4, preservación del camino
    # v1 explícito) caduca en el GREEN de T6 y su reemplazo es el RED firmado
    # tests/test_004_002_t6_landing.py::
    # TestPd10ExplicitV1Context::test_pd10_explicit_v1_execution_context_fails_with_diagnostic.
    # Entrada completa: docs/specs/004-002-project-execution-bootstrap/
    # v1-fixture-trace.md (materializada por el orquestador).

    def test_pd10_migrate_execution_option_does_not_exist(self) -> None:
        """PD-10: no existe --migrate-execution: rc≠0 si se pasa y no
        publica nada."""
        proc = run_prepare(self.root, "--migrate-execution")
        self.assertNotEqual(
            proc.returncode, 0, msg="--migrate-execution fue aceptado")
        self.assertEqual(
            v2_execution_docs(self.root), {},
            msg="--migrate-execution creó un contexto v2")
        self.assertEqual(
            published_packets(self.root), {},
            msg="--migrate-execution publicó un paquete")


if __name__ == "__main__":
    unittest.main(verbosity=2)
