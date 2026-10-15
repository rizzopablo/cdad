#!/usr/bin/env python3
"""005-006 T5 RED — Aceptación PD-16 (R1/R3) + comprobación empírica
PD-17 (`resume` sin checkpoint), caja negra sobre el CLI del repo.

Contract:
- docs/specs/005-006-guided-project-start/spec.md §1 (R1/R3), §2 (PD-16,
  PD-17), §3 (INV-4), §4 (criterios PD-16/PD-17).
- docs/specs/005-006-guided-project-start/plan.md (T5; test focal declarado
  `tests/test_005_006_t5_acceptance.py`; R2 real NO se simula: es el gate de
  integración que corre el orquestador con el dueño).

Superficie observable bajo prueba (caja negra por subprocess sobre los
entrypoint del repo — nunca se importa el módulo):

    python3 scripts/cdad_continuity.py resume \
        --project-root ROOT --execution-context EXEC.json [--json]
    python3 scripts/cdad_packet.py prepare --project-root ROOT \
        --role <rol> --substage <sub> --objective <texto>
    python3 scripts/cdad_packet.py validate-request --project-root ROOT \
        --execution-context EXEC.json --request REQUEST.json

Marcadores de diagnóstico (anclados por el contrato y la metodología
existente, 004-002/005-001): `approval pending`, `no-checkpoint`.

RED HOY (situación declarada, probada empíricamente sobre fixtures en
tempdir antes de escribir este archivo):

- **PD-17**: el CLI ya rinde `state: "no-checkpoint"` con proyección vacía
  (`goal/next_action` null, `decisions`/`uncertainties` []) y rc=0, sin
  efectos. El test NO fuerza un rojo: es un **lock de regresión** anclado a
  la postcondición (la espec declaró: si el CLI discrepara, se reporta el
  defecto; no discrepa).
- **PD-16/R3 (policy ausente)**: `prepare` ya falla cerrado (rc=2, stdout
  vacío, sin efectos) y el diagnóstico nombra el insumo faltante
  (`cdad-policy.json`). Lock de regresión anclado a la postcondición.
- **PD-16/R3 (autoridad sin pin)**: `prepare` ya emite rc=2 con el marcador
  `approval pending`, nombra el registro (`stage_history`) y cómo seguir
  (re-registrar la aprobación con path+sha). Lock de regresión anclado a la
  postcondición.
- **PD-16/R1**: con la política y la autoridad mínimas (fixture
  determinista, tempdir, sin Memory Bank y sin ejecución preparada), el
  camino de ejecución preparada alcanza el fin observable declarado: un
  **encargo preparado y despachable** (paquete publicado, contrato
  resuelto al pin del día, `REQUEST.json` válido según el propio
  `validate-request`, binding `execution` en disco). Lock de regresión
  anclado a la postcondición.

Límite declarado con precisión (se pidió no fabricar un verde): la
composición del arranque guiado (reconocimiento del proyecto, bootstrap de
Memory Bank preguntando lo mínimo, registro de restricciones) es
**comportamiento del procedimiento** (`references/project-start.md`, PD-1)
y del rol orquestador (intake, PD-2): los fija el test de consistencia
documental de T1/T2 y la review; **no es verificable por fixture de CLI**.
Por eso este oráculo de R1 ancla el fin observable que el producto
garantiza hoy: dado el estado **mínimo autorizado** que el procedimiento
produce inmediatamente antes del encargo (política, fuente de autoridad,
aprobación pineada, feature registrada), el camino de ejecución preparada
termina en el encargo despachable. La fixture NO simula el reconocimiento (no hay Memory Bank:
`docs/projectbrief.md`, `docs/activeContext.md` y `docs/systemPatterns.md`
ausentes por construcción, pre-verificados como precondición).

Fixtures (patrón test_005_001_t3_idle / test_005_001_t4_decisive /
test_005_001_t3_idle... ver `tests/test_003_004_t1_resume.py` para `resume`):
proyectos sintéticos en tempdirs, deterministas y agnósticos de proyecto y
entorno; stdin cerrado (DEVNULL) y timeout en cada corrida del CLI
("sin preguntar al usuario"); ninguna escritura en este repo y ninguna
lectura de implementación (`scripts/cdad_packet.py`,
`scripts/cdad_continuity.py`). Todo fallo debe ser una AssertionError de
comportamiento, nunca ImportError/SyntaxError/NameError.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = REPO_ROOT / "scripts" / "cdad_continuity.py"

EPIC_ID = "epic-005-real-operation"
FEATURE_ID = "005-006-guided-project-start"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
PLAN_FILE = f"docs/epics/{EPIC_ID}/plan.md"

SPEC_BYTES = b"# Spec fixture (005-006 T5)\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()

APPROVER = "Pablo"
APPROVED_AT = "2026-10-10T00:00:00Z"
OBJECTIVE = "005-006 T5 PD-16/R1: primer encargo preparado y despachable"
EXEC_ID = "exec-005-006-t5-resume-no-checkpoint-001"
CLI_TIMEOUT_S = 120

PACKET_BEGIN = "---cdad-packet-json"
PENDING_MARKER = "approval pending"
NO_CHECKPOINT_TOKEN = "no-checkpoint"

# Archivos Memory Bank ausentes por construcción en la fixture de R1
# (proyecto nuevo = sin Memory Bank, spec §1 R1 / PD-4).
MEMORY_BANK_FILES = (
    "docs/projectbrief.md",
    "docs/activeContext.md",
    "docs/systemPatterns.md",
)


# ---------------------------------------------------------------- fixtures


def run_packet_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
        timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL,
    )


def run_continuity_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CONTINUITY_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
        timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL,
    )


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    """Contenido byte a byte del árbol del fixture (archivos y paths)."""
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


def read_state(root: Path) -> dict:
    return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))


def write_state(root: Path, state: dict) -> None:
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n", encoding="utf-8")


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(root: Path, rel: str, doc: dict) -> None:
    write_text(root, rel,
               json.dumps(doc, indent=2, sort_keys=True) + "\n")


def write_policy(root: Path) -> None:
    write_json(root, POLICY_FILE, {
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    })


def spec_approval_entry() -> dict:
    """Aprobación pineada de la spec (pin obligatorio: path + sha256)."""
    return {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": APPROVER,
        "approved_at": APPROVED_AT,
        "contract_path": SPEC_FILE,
        "contract_sha256": SPEC_SHA256,
    }


def base_state(*, stage_history: list[dict] | None = None) -> dict:
    """State mínimo del fixture (epic E aprobado, feature F activa)."""
    return {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": [{
            "epic": EPIC_ID,
            "stage": "epic-plan",
            "approved_by": APPROVER,
            "approved_at": APPROVED_AT,
        }],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": stage_history or [],
        "approver": APPROVER,
        "last_updated": APPROVED_AT,
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


class T5Case(unittest.TestCase):
    """Base: fixture sintético en tempdir propio por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-006-t5-")
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", self._tmp], check=False)

    def make_project_root(self, name: str) -> Path:
        tmp = tempfile.mkdtemp(prefix="cdad-005-006-t5-", dir=self._tmp)
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", tmp], check=False)
        root = Path(tmp) / name
        root.mkdir(parents=True)
        return root

    # -- asserts compartidos -------------------------------------------

    def prepare(self, root: Path, *, role: str, substage: str,
                objective: str) -> subprocess.CompletedProcess:
        return run_packet_cli([
            "prepare", "--project-root", str(root),
            "--role", role, "--substage", substage,
            "--objective", objective,
        ])

    def assert_no_publication(self, label: str, root: Path,
                              before: dict[str, bytes | None],
                              state_before: bytes) -> None:
        """Parada cerrada: árbol y state byte a byte idénticos; ningún
        paquete ni contexto de ejecución publicado."""
        self.assertEqual(
            tree_snapshot(root), before,
            msg=f"{label}: hubo publicación (árbol modificado)")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg=f"{label}: el state cambió")
        self.assertFalse(
            (root / ".cdad").exists(),
            msg=f"{label}: quedó un espacio de publicación `.cdad/`")


# ---------------------------------------------------------------- PD-17


class TestPd17ResumeWithoutCheckpoint(T5Case):
    """PD-17 (empírico, contra el CLI): `resume` sin checkpoint rinde la
    proyección vacía `no-checkpoint` con rc=0, sin efectos.

    LOCK declarado (RED de T5): el comportamiento ya es conforme hoy
    (probe previo a este archivo: rc=0, `state: "no-checkpoint"`,
    proyección vacía, árbol intacto). El test lo ancla a la postcondición;
    si el CLI discrepara, fallaría aquí reportando el defecto (no se
    asume)."""

    def test_pd17_resume_without_checkpoint_yields_empty_no_checkpoint_rc0(
            self) -> None:
        root = self.make_project_root("proj")
        # Fixture: execution context mínimo; SIN checkpoint de continuidad
        # (precondición verificada: nunca hubo una ejecución activa).
        write_json(root, "execution-context.json", {
            "schema_version": 1,
            "execution_id": EXEC_ID,
            "runtime": "opencode",
            "hitl_delegation": {
                "authority_ref": AUTHORITY_REF,
                "expires_on": "2099-12-31",
            },
        })
        head_rel = f".cdad/executions/{EXEC_ID}/continuity/head.json"
        self.assertFalse(
            (root / head_rel).is_file(),
            msg="PD-17 (precondición): el fixture no debe tener head de "
                "continuidad")
        before = tree_snapshot(root)

        proc = run_continuity_cli([
            "resume", "--project-root", str(root),
            "--execution-context", str(root / "execution-context.json"),
            "--json",
        ])

        # PD-17: rc=0 y proyección vacía no-checkpoint.
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-17: `resume` sin checkpoint debe rendir rc=0 (la "
                f"ausencia de checkpoint NO es un error que reanude): "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-17: el CLI corrió con stdin cerrado y timeout: "
                "ninguna pregunta interactiva")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"PD-17: fallo con traceback: {proc.stderr!r}")
        envelope = json.loads(proc.stdout)
        self.assertEqual(
            envelope.get("state"), NO_CHECKPOINT_TOKEN,
            msg=f"PD-17: el envelope no declara la proyección vacía "
                f"no-checkpoint; got state={envelope.get('state')!r} "
                f"(envelope keys={sorted(envelope)!r})")
        projection = envelope.get("projection")
        self.assertIsInstance(
            projection, dict,
            msg=f"PD-17: el render expone la proyección on-demand bajo "
                f"`projection`; got {projection!r}")
        self.assertIsNone(
            projection.get("goal"),
            msg=f"PD-17: la proyección debe ser vacía (sin objetivo "
                f"reconstruido); got {projection.get('goal')!r}")
        self.assertIsNone(
            projection.get("next_action"),
            msg=f"PD-17: la proyección debe ser vacía (sin próxima "
                f"acción); got {projection.get('next_action')!r}")
        self.assertEqual(
            projection.get("decisions"), [],
            msg=f"PD-17: la proyección vacía no lleva decisiones; got "
                f"{projection.get('decisions')!r}")
        self.assertEqual(
            projection.get("uncertainties"), [],
            msg=f"PD-17: la proyección vacía no lleva incertidumbres; got "
                f"{projection.get('uncertainties')!r}")
        # Sin efectos: `resume` en reposo es una lectura; no escribe
        # checkpoint ni ningún registro.
        self.assertEqual(
            tree_snapshot(root), before,
            msg="PD-17: `resume` sin checkpoint no debe publicar nada "
                "(árbol modificado; un checkpoint no debe fabricarse "
                "en el arranque)")


# ---------------------------------------------------------------- PD-16/R3


class TestPd16R3IncompleteConfigFailsClosed(T5Case):
    """PD-16/R3 — configuración incompleta: parada cerrada con diagnóstico
    accionable, sin publicar nada.

    Caso (a) `docs/cdad-policy.json` ausente: `prepare` falla rc=2 (PD-1
    de 005-005/004-002) y el diagnóstico NOMBRA qué falta (la política del
    proyecto: token `cdad-policy.json`); efecto observable = rc + ausencia
    de efectos, no el texto exacto.

    LOCK declarado (RED de T5): el comportamiento ya es conforme hoy
    (probe previo: rc=2, stdout vacío, árbol intacto, sin `.cdad/`); el
    test lo ancla a la postcondición."""

    def test_r3_policy_missing_prepare_fails_closed_and_names_the_missing(self) -> None:
        root = self.make_project_root("proj")
        # Fixture determinista: state presente, autoridad presente, natura
        # política ausente (precondición verificada).
        for rel in ("tests", "src", "lib"):
            (root / rel).mkdir(exist_ok=True)
        write_text(root, AUTHORITY_REF,
                   "# Authorized execution fixture (epic-005)\n")
        write_state(root, base_state())
        self.assertFalse(
            (root / POLICY_FILE).is_file(),
            msg="R3 (precondición): la política debe estar ABSENT en el "
                "fixture de configuración incompleta")
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()

        proc = self.prepare(root, role="test-writer", substage="red",
                            objective="R3: prepare sin política")

        # Parada cerrada (PD-1 de 005-005/004-002): rc≠0, stdout vacío,
        # sin traceback.
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"R3: la configuración incompleta (policy ausente) debe "
                f"fallar CERRADO (rc!=0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertEqual(
            proc.stdout, "",
            msg=f"R3: el fallo cerrado imprimió contenido por stdout: "
                f"{proc.stdout!r}")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"R3: fallo con traceback: {proc.stderr!r}")
        # Diagnóstico accionable: NOMBRA qué falta.
        self.assertIn(
            "cdad-policy.json", proc.stderr,
            msg=f"R3: el diagnóstico no nombra el insumo faltante "
                f"(la política `{POLICY_FILE}`): {proc.stderr!r}")
        # Sin publicar nada (PD-14/INV-4: no paquete inválido).
        self.assert_no_publication(
            "R3 (policy ausente): sin publicación", root, before,
            state_before)


class TestPd16R3AuthorityWithoutPinPending(T5Case):
    """PD-16/R3 — autoridad sin pin: marcador `approval pending` rc=2, con
    diagnóstico que nombra el registro y cómo seguir, sin publicar nada.

    Caso (b): la entrada `specification` de `stage_history` existe pero SIN
    el pin obligatorio (path + contract_sha256, D3/005-001) → `prepare`
    rechaza rc=2 con el marcador `approval pending`, nombra el registro
    (`stage_history`, stage `specification`) y la acción legítima
    siguiente (re-registrar la aprobación pineada con path+sha).

    LOCK declarado (RED de T5): el comportamiento ya es conforme hoy
    (probe previo: rc=2, marcador `approval pending`, tokens
    `stage_history`/`specification`/`contract_sha256`, árbol intacto)."""

    def test_r3_authority_without_pin_emits_approval_pending_rc2(
            self) -> None:
        root = self.make_project_root("proj")
        for rel in ("tests", "src", "lib"):
            (root / rel).mkdir(exist_ok=True)
        write_policy(root)
        write_text(root, SPEC_FILE, SPEC_BYTES.decode())
        write_text(root, AUTHORITY_REF,
                   "# Authorized execution fixture (epic-005)\n")
        entry = spec_approval_entry()
        del entry["contract_sha256"]  # sin pin (precondición del R3-b)
        write_state(root, base_state(stage_history=[entry]))
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()

        proc = self.prepare(root, role="test-writer", substage="red",
                            objective="R3: prepare con autoridad sin pin")

        # rc=2 con el marcador canonical de aprobación faltante (PD-12
        # slice de 005-005: `approval pending`).
        self.assertEqual(
            proc.returncode, 2,
            msg=f"R3: la autoridad sin pin debe rechazar con rc=2 y "
                f"`approval pending`; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertEqual(
            proc.stdout, "",
            msg=f"R3: el rechazo imprimió contenido por stdout: "
                f"{proc.stdout!r}")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"R3: fallo con traceback: {proc.stderr!r}")
        self.assertIn(
            PENDING_MARKER, proc.stderr,
            msg=f"R3: stderr sin el marcador {PENDING_MARKER!r} (la spec "
                f"declara reusarlo para autoridad sin pin): "
                f"{proc.stderr!r}")
        # Diagnóstico: nombra el registro contradicho y cómo seguir
        # (el registro `stage_history`/`specification` y el pin que falta).
        for token in ("stage_history", "specification", "contract_sha256"):
            self.assertIn(
                token, proc.stderr,
                msg=f"R3: el diagnóstico no nombra el registro/campo "
                    f"involucrado y cómo seguir ({token!r}): "
                    f"{proc.stderr!r}")
        self.assertIn(
            SPEC_FILE, proc.stderr,
            msg=f"R3: el diagnóstico no nombra la spec concreta "
                f"({SPEC_FILE}): {proc.stderr!r}")
        # Sin publicar nada (no inventa autoridad; no paquete en vuelo).
        self.assert_no_publication(
            "R3 (autoridad sin pin): sin publicación", root, before,
            state_before)


# ---------------------------------------------------------------- PD-16/R1


class TestPd16R1FirstCommissionPreparedAndDispatchable(T5Case):
    """PD-16/R1 — proyecto nuevo, desde reposo: con la política y la
    autoridad mínimas, el camino de ejecución preparada alcanza el fin
    observable declarado: un **encargo preparado y despachable**.

    Fixture determinista (tempdir, agnóstico de proyecto/entorno):
    - SIN Memory Bank por construcción (`docs/projectbrief.md`,
      `docs/activeContext.md`, `docs/systemPatterns.md` ausentes —
      pre-verificado: clasificación `nuevo`, spec §1 R1/PD-4).
    - SIN ejecución preparada (`.cdad/` ausente, `execution` null,
      `active_packet` null — pre-verificado).
    - Con la política y la autoridad mínimas: política válida, fuente de
      autoridad, plan del epic aprobado y la aprobación de spec pineada
      (path+sha) — el estado enemediata que el arranque guiado registra
      antes del primer encargo.

    Límite declarado (sin fabricar un verde): el bootstrap de Memory Bank
    y el reconocimiento son comportamiento del procedimiento (`project-start.md`
    T1) y del intake (T2), verificados por consistencia documental + review;
    el CLI no puede verificarlos por fixture. Este oráculo ancla el FIN
    observable: el paquete existe, está `prepared`, su `REQUEST.json`
    resuelve al contrato pineado y es VÁLIDO según `validate-request` del
    propio producto (despachable), y el binding `execution` queda
    publicado.

    LOCK declarado (RED de T5): el comportamiento ya es conforme hoy
    (probe previo rc=0 / paquete prepared / validate-request rc=0)."""

    def test_r1_new_project_reaches_prepared_dispatchable_commission(
            self) -> None:
        root = self.make_project_root("proj")
        for rel in ("tests", "src", "lib"):
            (root / rel).mkdir(exist_ok=True)
        write_policy(root)
        write_text(root, SPEC_FILE, SPEC_BYTES.decode())
        write_text(root, PLAN_FILE, "# Epic plan fixture (005-006 T5)\n")
        write_text(root, AUTHORITY_REF,
                   "# Authorized execution fixture (epic-005)\n")
        write_state(root, base_state(stage_history=[spec_approval_entry()]))
        # Precondiciones del fixture R1: proyecto nuevo (sin Memory Bank)
        # y sin ejecución preparada.
        for rel in MEMORY_BANK_FILES:
            self.assertFalse(
                (root / rel).is_file(),
                msg=f"R1 (precondición): el proyecto nuevo NO debe tener "
                    f"Memory Bank preexistente ({rel} existe)")
        self.assertFalse(
            (root / ".cdad").exists(),
            msg="R1 (precondición): sin ejecución preparada no debe "
                "existir `.cdad/`")
        state0 = read_state(root)
        self.assertIsNone(
            state0.get("execution"),
            msg="R1 (precondición): sin ejecución preparada el state no "
                "lleva binding de ejecución")
        self.assertIsNone(
            state0.get("active_packet"),
            msg="R1 (precondición): sin ejecución preparada el state no "
                "lleva paquete activo")

        proc = self.prepare(root, role="test-writer", substage="red",
                            objective=OBJECTIVE)

        # --- el encargo PREPARADO (paquete publicado, activo, contrato
        # resuelto al pin aprobado) ---
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R1: con la política y la autoridad mínimas el primer "
                f"encargo debe prepararse (rc=0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="R1: stdout sin paquete canónico (`---cdad-packet-json`)")
        state = read_state(root)
        active = state.get("active_packet") or {}
        packet_id = active.get("id")
        self.assertTrue(
            packet_id,
            msg=f"R1: el state no dejó paquete activo identificado: "
                f"{state.get('active_packet')!r}")
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"R1: el primer encargo debe quedar PREPARADO y "
                f"despachable; got {state.get('active_packet')!r}")
        packet_dir = root / ".cdad" / "packets" / packet_id
        self.assertTrue(
            (packet_dir / "REQUEST.json").is_file(),
            msg=f"R1: el paquete preparado sin REQUEST.json publicado: "
                f"{packet_dir}")
        self.assertTrue(
            (packet_dir / "PACKET.md").is_file(),
            msg=f"R1: el paquete preparado sin PACKET.md publicado: "
                f"{packet_dir}")
        self.assertEqual(
            proc.stdout,
            (packet_dir / "PACKET.md").read_text(encoding="utf-8"),
            msg="R1: PACKET.md difiere del stdout de prepare")
        request = json.loads(
            (packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(
            request.get("role"), "test-writer",
            msg=f"R1: el encargo no lleva el rol solicitado: "
                f"{request.get('role')!r}")
        contract = request.get("contract") or {}
        self.assertEqual(
            contract.get("kind"), "approved-feature-spec",
            msg=f"R1: el contrato del encargo no es la spec aprobada: "
                f"{contract!r}")
        self.assertEqual(
            contract.get("path"), SPEC_FILE,
            msg=f"R1: el contrato del encargo no nombra la spec de la "
                f"fixture: {contract!r}")
        self.assertEqual(
            contract.get("sha256"), SPEC_SHA256,
            msg="R1: el contrato del encargo no resuelve al pin aprobado")
        self.assertTrue(
            request.get("read_scope") and request.get("write_scope"),
            msg=f"R1: el encargo despachable debe declarar scopes de "
                f"lectura/escritura: read={request.get('read_scope')!r} "
                f"write={request.get('write_scope')!r}")

        # --- DESPACHABLE: el propio producto valida el REQUEST.json
        # publicado del paquete activo (binding de ejecución publicado) ---
        execution = state.get("execution") or {}
        self.assertEqual(
            execution.get("feature_id"), FEATURE_ID,
            msg=f"R1: el binding de ejecución no liga la feature: "
                f"{execution!r}")
        context_path = (root / ".cdad" / "executions"
                        / (execution.get("id") or "")
                        / "execution.json")
        self.assertTrue(
            context_path.is_file(),
            msg=f"R1: el contexto de ejecución no fue publicado en "
                f"`.cdad/executions/`: {context_path}")
        valid = run_packet_cli([
            "validate-request", "--project-root", str(root),
            "--execution-context", str(context_path),
            "--request", str(packet_dir / "REQUEST.json"),
        ])
        self.assertEqual(
            valid.returncode, 0,
            msg=f"R1: el REQUEST.json del encargo preparado debe ser "
                f"VÁLIDO según `validate-request` del propio producto "
                f"(fin observable: encargo despachable); got "
                f"rc={valid.returncode} stdout={valid.stdout!r} "
                f"stderr={valid.stderr!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
