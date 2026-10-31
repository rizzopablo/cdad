#!/usr/bin/env python3
"""004-002 T6 — Aterrizaje utilizable (PD-10 y PD-12).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-10, PD-12) + review-t1.md (hallazgo lateral de portabilidad) + plan.md
(decisiones de interfaz I4, I9, I10 del orquestador; condición C1).

Superficie observable bajo prueba (todo black-box; ninguna escritura en este
repositorio; los proyectos consumidores son sintéticos y con git):

  install.sh --basic  sobre una COPIA del producto SIN el directorio fuente
                      agents/ y con build/staging generado en el fixture,
                      bajo CDAD_INSTALL_ROOT temporal (nunca el HOME real).
  cdad_packet.py (INSTALADO)  para el flujo del consumidor aislado:
      propuesta de política -> el dueño la materializa -> bootstrap ->
      reanudación -> registro de despacho.

Mapa test -> postcondición:

  TestPd12InstallConsumesStaging
    test_pd12_install_succeeds_without_source_agents_dir     -> PD-12
        (la instalación consume staging sin exigir el directorio fuente
        agents/).
    test_pd12_install_deploys_entrypoints_for_isolated_consumer -> PD-12
        (entrypoints instalados que el consumidor necesita).
  TestPd12InstalledConsumerFlow
    test_pd12_installed_propose_materialize_bootstrap_resume_record -> PD-12
        (flujo completo v2 desde la instalación aislada, sin el checkout en
        PATH/PYTHONPATH ni como cwd; candidato de trabajo nuevo, v2).
    test_pd12_standalone_bootstrap_without_epic_from_install -> PD-12
        (standalone: active_epic null + spec aprobada -> bootstrap sin
        fabricar un epic).
  TestPd12RuntimeMechanismsFromInstall
    test_pd12_i9_local_opencode_agents_generated_from_install -> PD-12/I9
        (CDAD_OPENCODE_AGENTS_DIR apunta a la instalación aislada; el
        bootstrap del consumidor ya corre con esa variable y el test verifica
        los derivados publicados por ESE prepare).
    test_pd12_i10_installed_cc_guard_finds_its_cli            -> PD-12/I10
        (el guard CC instalado encuentra su CLI sin CDAD_PACKET_CLI, con
        HOME aislado; discrimina el clasificador de la política del
        proyecto, no el mapa legacy).
  TestPd12LegacyIntake
    test_pd12_legacy_without_policy_keeps_legacy_intake       -> PD-12
        (proyecto legacy: camino implícito conservado; caso de humo que debe
        seguir en verde durante y después del corte C).
  TestPd10ExplicitV1Context
    test_pd10_explicit_v1_execution_context_fails_with_diagnostic -> PD-10
        (I4 eliminado en el GREEN de T6: un --execution-context explícito a
        un v1 falla con diagnóstico, sin conversión ni sobrescritura).

GREEN (T6, contra el código commiteado 87bca83/20be19c/697a61a): la
instalación consume staging, el flujo del consumidor aislado completa v2, el
bootstrap standalone funciona, I9/I10 publican sus mecanismos desde la
instalación, el intake legacy se conserva y el v1 explícito es rechazado con
diagnóstico. Sin lectura de implementación.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

PACKET_BEGIN = "---cdad-packet-json"

# Identidad sintética del proyecto consumidor (cualquier feature plana vale;
# la aprobación del contrato y la delegación siguen I2 del plan).
CONSUMER_FEATURE = "004-002-t6-consumer-demo"
CONSUMER_EPIC = "epic-consumer-demo"
CONSUMER_AUTHORITY = f"docs/epics/{CONSUMER_EPIC}/execution.md"
CONSUMER_CONTRACT = f"docs/specs/{CONSUMER_FEATURE}/spec.md"
CONTRACT_BYTES = b"# Consumer demo contract for 004-002 T6\n"

OBSERVATION_DOC = {
    "runtime": "opencode",
    "model_configured": None,
    "model_reported": None,
    "session": "ses-t6-landing-0001",
    "started_at": "2026-09-30T12:00:00Z",
    "provenance": {"runtime": "reported by runtime", "session": "orchestrator"},
}


def consumer_state(*, epic: str | None = CONSUMER_EPIC) -> dict:
    """Estado I2 del consumidor: aprobación del contrato + delegación vigente
    (o standalone: active_epic null sin delegación, I2)."""
    delegation = None
    if epic is not None:
        delegation = {
            "status": "active",
            "epic_id": epic,
            "source": CONSUMER_AUTHORITY,
            "scope": epic,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        }
    return {
        "version": 1,
        "stack": None,
        "active_epic": epic,
        "epic_stage": "features-loop",
        "epic_features": [{"id": CONSUMER_FEATURE, "status": "in-progress"}],
        "epic_history": [],
        "active_feature": CONSUMER_FEATURE,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [
            {
                "feature": CONSUMER_FEATURE,
                "stage": "specification",
                "approved_by": "Pablo",
                "approved_at": "2026-09-29T00:00:00Z",
                # 005-001 T1 (D3): forma pineada — el contrato del fixture
                # es CONTRACT_BYTES, escrito en CONSUMER_CONTRACT (migración
                # mecánica del RED).
                "contract_path": CONSUMER_CONTRACT,
                "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
            }
        ],
        "approver": "Pablo",
        "last_updated": "2026-09-29T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": delegation,
    }


def v1_execution_document(feature: str = CONSUMER_FEATURE) -> dict:
    """Contexto v1 sintético (la forma anterior a 004-002)."""
    return {
        "schema_version": 1,
        "execution": {
            "id": "exec-consumer-legacy-v1",
            "epic_id": CONSUMER_EPIC,
            "feature_id": feature,
            "runtime": "opencode",
            "scope": "consumer-legacy-scope",
            "model_policy": "ordinary",
            "authority_ref": CONSUMER_AUTHORITY,
            "model": {"configured": None, "reported": None},
        },
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
            "colocated_test_roots": ["src", "lib"],
            "colocated_test_suffixes": ["_test.go", ".test.js"],
            "colocated_test_prefixes": ["test_"],
        },
    }


def write_git_project(root: Path) -> None:
    """Proyecto consumidor sintético con git completa (PD-12: consumidor con
    git; el checkout nunca es parte del camino de ejecución)."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    for step in (
        ["init"],
        ["config", "user.email", "t6-consumer@example.invalid"],
        ["config", "user.name", "T6 Consumer Fixture"],
        ["add", "-A"],
        ["commit", "-m", "consumer fixture", "--allow-empty"],
    ):
        proc = subprocess.run(
            ["git", *step], cwd=str(root), capture_output=True, text=True
        )
        assert proc.returncode == 0, (
            f"fixture: git {step[0]} falló en el consumidor: "
            f"{proc.stdout} {proc.stderr}"
        )


def write_consumer_authority_and_contract(root: Path) -> None:
    authority = root / CONSUMER_AUTHORITY
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture\n", encoding="utf-8")
    contract = root / CONSUMER_CONTRACT
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_bytes(CONTRACT_BYTES)


def write_consumer_state(root: Path, state: dict) -> None:
    (root / "docs" / ".cdad-state.json").write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def v2_execution_docs(root: Path) -> dict[str, dict]:
    docs: dict[str, dict] = {}
    base = root / ".cdad" / "executions"
    if not base.is_dir():
        return docs
    for path in sorted(base.glob("*/execution.json")):
        docs[path.parent.name] = json.loads(path.read_text(encoding="utf-8"))
    return docs


def published_packets(root: Path) -> dict[str, bytes]:
    pkts: dict[str, bytes] = {}
    base = root / ".cdad" / "packets"
    if not base.is_dir():
        return pkts
    for path in sorted(base.glob("*/PACKET.md")):
        pkts[path.parent.name] = path.read_bytes()
    return pkts


class LandingInstall(unittest.TestCase):
    """Una instalación aislada compartida por la suite: COPIA del producto sin
    el directorio fuente agents/ y con build/staging generado EN el fixture
    (portabilidad, review-t1); CDAD_INSTALL_ROOT temporal, nunca el HOME real.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-t6-landing-")
        base = Path(cls._tmp.name).resolve()
        cls.product = base / "product"
        shutil.copytree(
            REPO_ROOT,
            cls.product,
            symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", ".pytest_cache", "__pycache__", "build"
            ),
        )
        # Fixture: build/staging generado aquí (un checkout limpio pasa).
        staging_run = subprocess.run(
            ["make", "staging"],
            cwd=str(cls.product),
            text=True,
            capture_output=True,
        )
        cls.staging_run = staging_run
        cls.staging_manifest = cls.product / "build" / "staging" / "manifest.json"
        cls.install_root = base / "install-root"
        cls.install_root.mkdir()
        # PD-12: la COPIA pierde el directorio fuente agents/ DESPUÉS de
        # generar staging: la instalación debe consumir staging.
        shutil.rmtree(cls.product / "agents")
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        cls.install_result = subprocess.run(
            ["bash", str(cls.product / "install.sh"), "--basic"],
            cwd=str(cls.product),
            env=env,
            text=True,
            capture_output=True,
        )
        cls.installed_oc_cli = (
            cls.install_root
            / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py"
        )
        cls.installed_cc_cli = (
            cls.install_root / ".claude/skills/cdad-cycle/scripts/cdad_packet.py"
        )
        cls.installed_oc_agents = cls.install_root / ".config/opencode/agents"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def assert_install_succeeded(self) -> None:
        """PD-12: la instalación aislada tiene éxito sin agents/ fuente
        (los bytes desplegados provienen exclusivamente de build/staging,
        PD-18)."""
        self.assertEqual(
            self.install_result.returncode,
            0,
            "PD-12: la instalación debe consumir staging y dejar de exigir el "
            f"directorio fuente agents/: rc={self.install_result.returncode}; "
            f"stdout={self.install_result.stdout!r} "
            f"stderr={self.install_result.stderr!r}",
        )

    def installed_cli(self) -> Path:
        """El CLI instalado del consumidor (destino real, orquestador)."""
        self.assertTrue(
            self.installed_oc_cli.is_file(),
            f"la instalación no desplegó el CLI del consumidor: "
            f"{self.installed_oc_cli}",
        )
        return self.installed_oc_cli

    def run_installed(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        """Invoca el CLI INSTALADO desde el proyecto consumidor sin el
        checkout en PATH ni PYTHONPATH (PD-12: el checkout no es parte del
        camino de ejecución)."""
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        return subprocess.run(
            [sys.executable, str(self.installed_cli()), *args],
            cwd=str(root),
            env=env,
            text=True,
            capture_output=True,
        )


class TestPd12InstallConsumesStaging(LandingInstall):
    """PD-12: la instalación consume staging y ya no exige agents/ fuente."""

    def test_pd12_install_succeeds_without_source_agents_dir(self) -> None:
        """PD-12: install.sh --basic sobre una COPIA del producto SIN el
        directorio fuente agents/ y con build/staging generado en el fixture
        debe tener éxito."""
        # Precondición del fixture: el staging fue generado en la copia.
        self.assertTrue(
            self.staging_manifest.is_file(),
            "fixture: `make staging` no produjo build/staging/manifest.json en "
            f"la copia del producto: {self.staging_run.stdout!r} "
            f"{self.staging_run.stderr!r}",
        )
        self.assertFalse(
            (self.product / "agents").exists(),
            "fixture: la copia debe perder el directorio fuente agents/",
        )
        self.assert_install_succeeded()

    def test_pd12_install_deploys_entrypoints_for_isolated_consumer(self) -> None:
        """PD-12: la instalación despliega los entrypoints que el consumidor
        aislado necesita (CLI por runtime y agentes OpenCode instalados)."""
        self.assert_install_succeeded()
        for entrypoint in (
            self.installed_oc_cli,
            self.installed_cc_cli,
            self.installed_oc_agents,
            self.install_root / ".claude/cdad-scripts",
        ):
            with self.subTest(entrypoint=str(entrypoint.relative_to(self.install_root))):
                self.assertTrue(
                    entrypoint.exists(),
                    f"PD-12: la instalación omitió el entrypoint {entrypoint}",
                )


class TestPd12InstalledConsumerFlow(LandingInstall):
    """PD-12: el flujo completo del consumidor funciona desde la instalación
    aislada, sin usar el checkout como ruta de ejecución."""

    def _new_consumer(self) -> Path:
        temp = tempfile.mkdtemp(prefix="cdad-t6-consumer-")
        self.addCleanup(shutil.rmtree, temp, ignore_errors=True)
        root = Path(temp) / "consumer"
        write_git_project(root)
        write_consumer_authority_and_contract(root)
        return root

    def test_pd12_installed_propose_materialize_bootstrap_resume_record(self) -> None:
        """PD-12: desde la instalación aislada, un proyecto consumidor con git
        completa el ciclo: propuesta de política (sin escrituras) -> el dueño
        la materializa -> bootstrap (prepare) -> reanudación -> registro de
        despacho. Todo con el cdad_packet.py INSTALADO y sin el checkout en
        PATH ni PYTHONPATH."""
        root = self._new_consumer()
        tree_before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))

        # (1) Propuesta de política: determinista, sin escrituras, sin
        # aprobar nada (PD-1/I1).
        proposal = self.run_installed(root, "prepare", "--project-root", str(root),
                                      "--propose-policy")
        self.assertEqual(
            proposal.returncode, 0,
            f"la propuesta de política falló desde la instalación: "
            f"{proposal.stderr}")
        try:
            policy_doc = json.loads(proposal.stdout)
        except ValueError as exc:  # pragma: no cover - diagnóstico de oráculo
            self.fail(f"la propuesta no imprimió JSON válido: {exc}: {proposal.stdout[:200]}")
        self.assertEqual(
            sorted(policy_doc), ["path_policy", "schema_version", "temporary_roots"],
            f"la propuesta debe contener exclusivamente schema_version, "
            f"path_policy y temporary_roots: {sorted(policy_doc)}")
        tree_after_proposal = sorted(
            p.relative_to(root).as_posix() for p in root.rglob("*"))
        self.assertEqual(
            tree_after_proposal, tree_before,
            "la propuesta escribió en el proyecto (PD-1: sin escrituras)")

        # (2) El dueño materializa la política EXACTAMENTE como la propuesta.
        policy_path = root / "docs" / "cdad-policy.json"
        policy_path.write_text(proposal.stdout, encoding="utf-8")

        # (3) El dueño registra la autoridad vigente (I2) y el contrato.
        write_consumer_state(root, consumer_state())
        tree_after_records = sorted(
            p.relative_to(root).as_posix() for p in root.rglob("*"))

        # (4) Bootstrap: prepare crea la ejecución v2 y publica el paquete.
        bootstrap = self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "T6 consumidor aislado")
        self.assertEqual(
            bootstrap.returncode, 0,
            f"el bootstrap desde la instalación aislada falló: {bootstrap.stderr}")
        self.assertTrue(
            bootstrap.stdout.startswith(PACKET_BEGIN),
            "el bootstrap no imprimió el paquete canónico por stdout")
        docs = v2_execution_docs(root)
        self.assertEqual(
            len(docs), 1, msg=f"contextos v2 publicados: {sorted(docs)}")
        execution_id, doc = next(iter(docs.items()))
        self.assertEqual(
            doc.get("schema_version"), 2, msg="el contexto creado no es v2")
        self.assertEqual(
            execution_id,
            json.loads(
                (root / "docs" / ".cdad-state.json")
                .read_text(encoding="utf-8"))["execution"]["id"],
            msg="state.execution no referencia el contexto creado")
        packets = published_packets(root)
        self.assertEqual(
            len(packets), 1, msg=f"paquetes publicados: {sorted(packets)}")
        packet_id = next(iter(packets))

        # (5) Reanudación: los bytes idénticos del paquete (PD-4/I7: argv puro).
        packet_bytes = packets[packet_id]
        resume = self.run_installed(root, "prepare", "--project-root", str(root),
                                    "--resume-packet", packet_id)
        self.assertEqual(
            resume.returncode, 0,
            f"la reanudación falló desde la instalación: {resume.stderr}")
        self.assertEqual(
            resume.stdout, packet_bytes.decode("utf-8"),
            "la reanudación no devolvió los bytes idénticos del paquete")

        # (6) Registro de despacho desde un documento de observaciones (I8).
        observation = root / "docs" / "obs-t6.json"
        observation.write_text(
            json.dumps(OBSERVATION_DOC, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        record = self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--record-dispatch", packet_id,
            "--attempt-id", "attempt-a1",
            "--input", "docs/obs-t6.json")
        self.assertEqual(
            record.returncode, 0,
            f"el registro de despacho falló desde la instalación: {record.stderr}")
        dispatch = (root / ".cdad" / "executions" / execution_id / "dispatches"
                    / "attempt-a1.json")
        self.assertTrue(
            dispatch.is_file(),
            f"el registro no dejó el intento en {dispatch}")

    def test_pd12_standalone_bootstrap_without_epic_from_install(self) -> None:
        """PD-12 (standalone): con active_epic null y la aprobación del
        contrato en stage_history, el bootstrap desde la instalación aislada
        tiene éxito sin fabricar un epic (el contexto lleva epic null)."""
        root = self._new_consumer()
        # El dueño materializa una política válida (no propuesta aquí: la
        # propuesta ya está verificada en el flujo completo).
        proposal = self.run_installed(root, "prepare", "--project-root", str(root),
                                      "--propose-policy")
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        (root / "docs" / "cdad-policy.json").write_text(
            proposal.stdout, encoding="utf-8")
        write_consumer_state(root, consumer_state(epic=None))

        proc = self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "standalone consumidor")
        self.assertEqual(
            proc.returncode, 0,
            f"el bootstrap standalone falló: {proc.stdout} {proc.stderr}")
        docs = v2_execution_docs(root)
        self.assertEqual(len(docs), 1, msg=f"contextos: {sorted(docs)}")
        _, doc = next(iter(docs.items()))
        execution = doc.get("execution", doc)
        self.assertIsNone(
            execution.get("epic_id"),
            msg=f"standalone fabricó un epic: {execution.get('epic_id')!r}")
        self.assertTrue(proc.stdout.startswith(PACKET_BEGIN),
                        msg="standalone no imprimió el paquete canónico")
        self.assertEqual(len(published_packets(root)), 1,
                         msg="standalone no publicó el paquete")


class TestPd12RuntimeMechanismsFromInstall(LandingInstall):
    """PD-12: mecanismos runtime del consumidor aislado (I9/I10).

    El bootstrap del consumidor acepta entorno extra; PD-4 impide un segundo
    encargo ordinario mientras el paquete activo está `prepared`, así que el
    test I9 corre SU bootstrap ya con CDAD_OPENCODE_AGENTS_DIR y verifica los
    derivados publicados por ESE prepare (sin segundo paquete).
    """

    def _bootstrapped_consumer(
        self, extra_env: dict[str, str] | None = None
    ) -> Path:
        temp = tempfile.mkdtemp(prefix="cdad-t6-consumer-")
        self.addCleanup(shutil.rmtree, temp, ignore_errors=True)
        root = Path(temp) / "consumer"
        write_git_project(root)
        write_consumer_authority_and_contract(root)
        proposal = self.run_installed(root, "prepare", "--project-root",
                                      str(root), "--propose-policy")
        self.assertEqual(proposal.returncode, 0, proposal.stderr)
        (root / "docs" / "cdad-policy.json").write_text(
            proposal.stdout, encoding="utf-8")
        write_consumer_state(root, consumer_state())
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        if extra_env:
            env.update(extra_env)
        proc = subprocess.run(
            [sys.executable, str(self.installed_cli()),
             "prepare", "--project-root", str(root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "T6 mecanismos runtime"],
            cwd=str(root), env=env, text=True, capture_output=True,
        )
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (bootstrap del consumidor): {proc.stderr}")
        return root

    def test_pd12_i9_local_opencode_agents_generated_from_install(self) -> None:
        """PD-12/I9: la generación local de agentes OpenCode toma los agentes
        INSTALADOS: el bootstrap del consumidor corre con
        CDAD_OPENCODE_AGENTS_DIR apuntando a la instalación aislada y ESE
        prepare publica .opencode/agents/cdad-*.md en el proyecto consumidor
        (un solo encargo: PD-4 impide reemplazar un paquete activo)."""
        root = self._bootstrapped_consumer(extra_env={
            "CDAD_OPENCODE_AGENTS_DIR": str(self.installed_oc_agents),
        })
        local_agents = root / ".opencode" / "agents"
        published = sorted(p.name for p in local_agents.glob("cdad-*.md")) \
            if local_agents.is_dir() else []
        self.assertIn(
            "cdad-test-writer.md", published,
            msg="PD-12/I9: prepare no publicó los agentes locales en "
                f".opencode/agents/ desde los agentes INSTALADOS "
                f"({self.installed_oc_agents}); publicados: {published}")
        self.assertTrue(
            (local_agents / ".cdad-derived.json").is_file(),
            msg="PD-12/I9: falta el manifest de derivados .cdad-derived.json")

    def test_pd12_i10_installed_cc_guard_finds_its_cli(self) -> None:
        """PD-12/I10: el guard CC instalado encuentra su CLI SIN
        CDAD_PACKET_CLI (fallback $HOME dentro de la instalación aislada) y
        aplica la clasificación del proyecto: deniega la lectura de
        implementación y permite tests."""
        root = self._bootstrapped_consumer()
        # La política del consumidor NO declara scripts/ como implementación
        # del mapa legacy: si el guard carga la política del proyecto vía el
        # CLI instalado, deniega; si se queda en el mapa legacy, permite.
        policy_doc = json.loads((root / "docs" / "cdad-policy.json")
                                .read_text(encoding="utf-8"))
        policy_doc["path_policy"]["implementation_roots"] = ["scripts"]
        (root / "docs" / "cdad-policy.json").write_text(
            json.dumps(policy_doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        (root / "scripts").mkdir(exist_ok=True)
        (root / "scripts" / "x.py").write_text("# impl del consumidor\n",
                                               encoding="utf-8")
        (root / "tests" / "test_a.py").write_text("# test\n", encoding="utf-8")

        guards = sorted(self.install_root.glob(".claude/cdad-scripts/path-guard.sh"))
        self.assertTrue(
            guards, msg="la instalación no desplegó path-guard.sh en .claude/cdad-scripts")
        guard = guards[0]
        env = os.environ.copy()
        # HOME aislado: el fallback $HOME/.claude/skills/... resuelve DENTRO de
        # la instalación; el HOME real nunca se toca.
        env["HOME"] = str(self.install_root)
        env.pop("CDAD_PACKET_CLI", None)
        env.pop("PYTHONPATH", None)
        for tool_name, tool_input, expected in (
            ("Read", {"file_path": "tests/test_a.py"}, 0),
            ("Read", {"file_path": "scripts/x.py"}, 2),
        ):
            with self.subTest(tool=tool_name, tool_input=tool_input):
                proc = subprocess.run(
                    ["bash", str(guard), "test-writer-read"],
                    input=json.dumps({"tool_name": tool_name,
                                      "tool_input": tool_input}),
                    capture_output=True, text=True, cwd=str(root), env=env,
                )
                self.assertEqual(
                    proc.returncode, expected,
                    msg=f"PD-12/I10: el guard instalado medió {tool_name}"
                        f"({tool_input}) con rc={proc.returncode}, esperado "
                        f"{expected} (stdout/stderr: {proc.stdout} {proc.stderr})")


class TestPd12LegacyIntake(LandingInstall):
    """PD-12: el proyecto legacy conserva su intake (caso de humo, debe
    permanecer en verde durante y después del corte C)."""

    def test_pd12_legacy_without_policy_keeps_legacy_intake(self) -> None:
        """PC-04 (010-004 §4.1/§7/INV-11, sustitución N-3 del owner). Un
        proyecto legacy SIN política y SIN contexto v2, con su documento de
        ejecución v1 en .cdad/execution.json, ya NO conserva el camino
        implícito anterior (PD-12 de 004-002:112-115): la selección v1
        implícita se RECHAZA antes de publicar (rc != 0, stdout vacío), sin
        publicar paquete y sin efectos persistentes (INV-11). El v1 queda
        byte-idéntico, no se fabrica contexto v2 y el state conserva su
        intake histórico (§4.1) sin binding v2 ni paquete activo: su mera
        presencia no habilita preparación nueva v1."""
        temp = tempfile.mkdtemp(prefix="cdad-t6-legacy-")
        self.addCleanup(shutil.rmtree, temp, ignore_errors=True)
        root = Path(temp) / "legacy"
        write_git_project(root)
        write_consumer_authority_and_contract(root)
        cdad = root / ".cdad"
        cdad.mkdir()
        v1_path = cdad / "execution.json"
        v1_path.write_text(
            json.dumps(v1_execution_document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        v1_bytes = v1_path.read_bytes()
        # state sin binding v2 ni paquete activo (el intake legacy manda).
        state_path = root / "docs" / ".cdad-state.json"
        write_consumer_state(root, consumer_state())

        proc = self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "intake legacy conservado")
        # PC-04/INV-11: rechazo antes de publicar, sin paquete ni efectos.
        self.assertNotEqual(
            proc.returncode, 0,
            msg="PC-04 (010-004 §4.1/§7): la selección v1 implícita sin "
                "policy debe rechazarse antes de publicar; prepare respondió "
                f"exit 0 con stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="el rechazo PC-04 no debe publicar paquete: stdout vacío "
                f"exigido, recibido {proc.stdout!r}")
        self.assertEqual(
            published_packets(root), {},
            msg="el rechazo PC-04 publicó un paquete (INV-11)")
        self.assertEqual(
            v1_path.read_bytes(), v1_bytes,
            msg="el documento v1 del proyecto legacy fue modificado")
        self.assertEqual(
            v2_execution_docs(root), {},
            msg="el rechazo PC-04 fabricó un contexto v2 (§4.1: no se copia, "
                "convierte ni reubica el contexto para hacerla pasar)")
        post_state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertIsNone(
            post_state["execution"],
            msg="el rechazo PC-04 dejó binding v2 en state (INV-11)")
        self.assertIsNone(
            post_state["active_packet"],
            msg="el rechazo PC-04 dejó paquete activo en state (INV-11)")


class TestPd10ExplicitV1Context(unittest.TestCase):
    """PD-10/I4: el camino v1 explícito quedó eliminado en el GREEN de T6
    (un --execution-context explícito a un v1 falla con diagnóstico, sin
    conversión ni sobrescritura, PD-10)."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t6-v1-")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        self.root = Path(self._tmp) / "proj"
        # Proyecto v2-adoptante: política presente (la adopción la señala la
        # política, I4 refinado) + registro I2 + contrato + autoridad.
        self.root.mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "tests").mkdir()
        policy = {
            "schema_version": 1,
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src", "lib"],
                "documentation_roots": ["docs"],
            },
            "temporary_roots": [".cdad/tmp"],
        }
        (self.root / "docs").mkdir()
        (self.root / "docs" / "cdad-policy.json").write_text(
            json.dumps(policy, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        write_consumer_authority_and_contract(self.root)
        write_consumer_state(self.root, consumer_state())
        cdad = self.root / ".cdad"
        cdad.mkdir()
        self.v1_path = cdad / "execution.json"
        self.v1_path.write_text(
            json.dumps(v1_execution_document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        self.v1_bytes = self.v1_path.read_bytes()

    def test_pd10_explicit_v1_execution_context_fails_with_diagnostic(self) -> None:
        """PD-10/I4: un --execution-context explícito que apunta a un
        contexto v1 falla con diagnóstico (rc≠0), sin conversión ni
        sobrescritura del v1 y sin publicar paquete."""
        proc = subprocess.run(
            [sys.executable, str(REPO_CLI), "prepare",
             "--project-root", str(self.root),
             "--execution-context", str(self.v1_path),
             "--role", "test-writer", "--substage", "red",
             "--objective", "encargo sobre v1 explícito"],
            capture_output=True, text=True, cwd=str(self.root),
        )
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="PD-10/I4: el camino v1 explícito fue aceptado (rc=0); el "
                "GREEN de T6 debe eliminarlo: el v1 no se convierte ni se "
                "reescribe (el contexto de trabajo nuevo es v2)")
        self.assertIn(
            "ERROR", out,
            msg=f"PD-10/I4: el rechazo del v1 explícito no produjo un "
                f"diagnóstico: {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-10/I4: el rechazo del v1 explícito imprimió un paquete")
        self.assertEqual(
            self.v1_path.read_bytes(), self.v1_bytes,
            msg="PD-10: el contexto v1 fue modificado durante el rechazo")
        self.assertEqual(
            v2_execution_docs(self.root), {},
            msg="PD-10/I4: el rechazo del v1 explícito fabricó un contexto v2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
