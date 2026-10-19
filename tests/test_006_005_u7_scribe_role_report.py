#!/usr/bin/env python3
"""006-005 U7 RED — fila del scribe en la tabla cerrada de materialización
(PD-26 de `docs/specs/006-005-native-path-parity/spec.md`; §2.8.3, PD-23,
INV-14, D-17).

Contract:
- `docs/specs/006-005-native-path-parity/spec.md` (aprobada; §2.8.3, §3 PD-26,
  §3 PD-23 (tabla), §4 INV-14, §5 D-15/D-17, §6 V-13, §8 item 3).
- `docs/specs/006-005-native-path-parity/plan.md` §3 ficha U7 y su bloque
  `plan-tasks`; §4 regla A-1 (fila U7).
- Task provenance: `exec-006-005-native-path-parity-001`.

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre los CLI
del repo; ningún módulo de implementación se importa ni se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root R --role <rol> --substage <subfase> --objective <texto>
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \\
        --project-root R --record-dispatch <id> --attempt-id <a> --input <obs>
    python3 skills/cdad-cycle/scripts/cdad_result.py receive \\
        --project-root R --execution-context E.json --packet PACKET.md \\
        --request REQUEST.json --descriptor RESULT.json
    python3 skills/cdad-cycle/scripts/cdad_result.py materialize \\
        --project-root R --receipt receipt.json --authorization MATERIALIZE.json

PD-26: `_allowed_kinds("scribe", "memory")` admite `role-report`, así que la
entrega del scribe por la vía del adaptador **se materializa** —`role-report`
tiene raíz permitida `docs/specs/<feature>/`— y **nunca escribe el Memory
Bank**: un target `docs/projectbrief.md` (o cualquiera de los cuatro archivos
del Memory Bank) con ese kind se rechaza por quedar fuera de la raíz permitida.
La separación del informe en los cuatro archivos sigue siendo el acto declarado
del orquestador (ADR-003), no un paso de `materialize`; los cuatro `scribe-*`
quedan como la entrega por archivo. La entrega no aprueba: recibo `pending`.
Ninguna otra fila de la tabla cambia y `artifact-policy.json` no cambia.

Mapeo test → postcondición («RED» = falla hoy por aserción sobre el
comportamiento ausente; «ancla» = pasa hoy y se declara como tal porque la
postcondición que fija ya está satisfecha por el árbol actual):

  test_pd26_scribe_role_report_materializes_into_the_spec_folder
      -> PD-26 (positivo, RED): recibo de rol `scribe`/subfase `memory` con la
         parte única `role-report` => `materialize` rc=0 hacia un target dentro
         de `docs/specs/<feature>/`, con sha IDÉNTICO al de la parte recibida,
         recibo `pending`, state y receipt intactos (hoy rc≠0: la fila del
         scribe no admite `role-report`).
  test_pd26_memory_bank_targets_stay_rejected_naming_the_allowed_root
      -> PD-26 (destino negativo, RED): un target del Memory Bank
         (`docs/projectbrief.md`, `docs/systemPatterns.md`,
         `docs/activeContext.md`, `docs/progress.md`) con `role-report` =>
         rc≠0 NOMBRANDO la raíz permitida `docs/specs/<feature>/`; sin target
         escrito, sin stdout, sin traceback, state y receipt intactos (hoy el
         rechazo existe pero por el eje rol y NO nombra la raíz permitida: la
         frontera declarada «el Memory Bank no es alcanzable por ese kind» no
         está establecida).
  test_pd26_role_axis_role_report_of_other_roles_stays_rejected
      -> PD-26/PD-23 (eje rol, ancla): `role-report` de test-writer,
         implementer y reviewer sigue rechazado por el eje rol (D-17 rechaza
         admitirlo «para todos los roles»).
  test_pd26_r3_crossings_stay_rejected
      -> PD-26/PD-23 (R3, ancla): los cruces rol↔kind de R3 siguen rechazados
         (incluido `("scribe","memory","test-audit")`: la fila del scribe gana
         `role-report`, no kinds de otros roles).
  test_pd26_r5_scribe_file_kinds_still_materialize
      -> PD-26 (R5, ancla): los cuatro `scribe-*` siguen materializando sus
         raíces-archivo del Memory Bank con bytes idénticos.
  test_pd26_materialization_table_asset_is_unchanged
      -> PD-26/PD-23 (ancla): `skills/cdad-cycle/assets/artifact-policy.json`
         conserva sus bytes (inspección por sha256; el archivo NO se parsea ni
         se lee su contenido como contrato: `role-report` ya existe en la tabla
         con raíz `docs/specs/<feature>/`, así que el oráculo es alcanzable sin
         tocarla).

Fixture: proyecto descartable en un tempdir, `HOME`/`XDG_CONFIG_HOME`
redirigidos dentro del tempdir y las variables de credencial del runtime
retiradas del entorno hijo (nunca el HOME real, nunca este repo). Construido
por el camino legítimo del CLI (`prepare` → `prepare --record-dispatch` →
`receive`). Los ids son sintéticos y anónimos; ninguna ruta del host aparece en
las aserciones. Los targets son project-relative y `materialize` corre con cwd
en la raíz del fixture (un target mal resuelto caería dentro del fixture, nunca
en este repo).

Regla A-1 (declarada): esta unidad **no reemplaza ningún test existente**. Se
buscó un test que fije la fila del scribe **incluyendo la ausencia de
`role-report`** y no existe: R2 cubre sólo los kinds de auditoría, R3 cruza
`("scribe","memory","test-audit")` y las clases R5 usan los cuatro `scribe-*`.
Este archivo sólo agrega oráculos nuevos.

RED hoy (medido en HEAD `4463969`, declarado, nunca accidental): el
`materialize` de la parte única `role-report` de un recibo `scribe`/`memory`
falla con rc=2 y el diagnóstico
«artifact_kind 'role-report' is not permitted for role 'scribe'/substage
'memory': a kind of another role fails in the closed §7 table». El caso
positivo y los cuatro casos de destino del Memory Bank fallan por ASERCIÓN
sobre ese comportamiento ausente; el resto son anclas declaradas.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_SCRIPT = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
RESULT_SCRIPT = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"

# La tabla de materialización (dato del producto, NO implementación): PD-26
# exige que no cambie. Se inspecciona SÓLO su digest — el archivo no se parsea
# ni su contenido se usa como oráculo de comportamiento.
ARTIFACT_POLICY = (
    REPO_ROOT / "skills" / "cdad-cycle" / "assets" / "artifact-policy.json")
ARTIFACT_POLICY_SHA256 = (
    "a171273c7a589588367194139850ff6587b0a3037b7bf74e54bc95c53cfa872d")

EPIC_ID = "epic-006-opencode-concurrency"
# IMPORTANTE: feature del FIXTURE, no la feature real (006-005). Toda escritura
# cae bajo `docs/specs/<FIXTURE>/` en un tempdir; nada de este repo se toca.
FEATURE_ID = "006-999-u7-scribe-row-fixture"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture (006-005 U7 scribe row)\n"
# Plan del epic: contrato que exige el architect en `brainstorm` (§2.8.2: en
# `brainstorm` el kind `role-report` sigue rechazándose).
PLAN_FILE = f"docs/epics/{EPIC_ID}/plan.md"
PLAN_BYTES = b"# Epic plan fixture (006-005 U7)\n"

APPROVER = "fixture-u7"
AUTHORIZED_BY = "fixture-u7 (orquestador declarado del fixture)"
ATTEMPT_ID = "att-006-005-u7-red-001"
SESSION = "ses-006-005-u7-red-fixture-0001"

# La raíz permitida del kind `role-report` (§2.8.3) y el target exacto de cada
# caso positivo: dentro de la carpeta de la spec de la feature.
ALLOWED_ROOT = f"docs/specs/{FEATURE_ID}/"
TARGET_REPORT = ALLOWED_ROOT + "scribe-report.md"

# Los cuatro archivos del Memory Bank: el destino que PD-26 declara NO
# alcanzable por el informe del rol.
MEMORY_BANK_TARGETS = (
    "docs/projectbrief.md",
    "docs/systemPatterns.md",
    "docs/activeContext.md",
    "docs/progress.md",
)

DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"
MANIFEST_PATH = ".cdad/inbox/changes.json"
BASELINE_REF = "orchestrator-prepared-reference"
BASELINE_SHA256 = "0" * 64

CLI_AUSENTE_MARKERS = (
    "No such file or directory",
    "invalid choice",
    "unrecognized",
    "No module named",
)

# Cruces de R3 que la ficha U7 lista como regresión (rol/subfase con el kind de
# OTRO rol y el target que ese kind solo autoriza).
R3_CROSSINGS = (
    ("test-writer", "red", "review", ALLOWED_ROOT + "review-u7.md"),
    ("test-writer", "red", "scribe-projectbrief", "docs/projectbrief.md"),
    ("reviewer", "review", "test-writer-role-report",
     ALLOWED_ROOT + "reviewer-crossing.md"),
    ("scribe", "memory", "test-audit", ALLOWED_ROOT + "test-audit.md"),
)

# Los cuatro kinds por archivo del scribe y su raíz-archivo (R5).
SCRIBE_FILE_KINDS = (
    ("scribe-projectbrief", "docs/projectbrief.md"),
    ("scribe-systemPatterns", "docs/systemPatterns.md"),
    ("scribe-activeContext", "docs/activeContext.md"),
    ("scribe-progress", "docs/progress.md"),
)


# ---------------------------------------------------------------- helpers


def out_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout.decode("utf-8", errors="replace")


def err_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stderr.decode("utf-8", errors="replace")


def assert_reachable_or_invalid_red(stderr: str, contexto: str) -> None:
    """Guard anti-RED inválida: el fallo del CLI no debe indicar ausencia del
    comando/módulo (eso sería RED falsa); debe nombrar la conducta."""
    for marker in CLI_AUSENTE_MARKERS:
        assert marker not in stderr, (
            f"RED inválida ({contexto}): el fallo es por CLI ausente "
            f"({marker!r} en stderr), no por el comportamiento bajo prueba: "
            f"{stderr!r}")


def observation_document(session: str) -> dict:
    """Documento de observación I8 (claves cerradas; sin datos de host)."""
    return {
        "runtime": "opencode",
        "model_configured": "fixture/model",
        "model_reported": "fixture/model",
        "session": session,
        "started_at": "2026-10-19T00:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def fixture_state_document() -> dict:
    """State sintético con los registros I2 que `prepare` exige."""
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
            "approved_at": "2026-10-19T00:00:00Z",
        }],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [{
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": APPROVER,
            "approved_at": "2026-10-19T00:00:00Z",
            "contract_path": CONTRACT_FILE,
            "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
        }],
        "approver": APPROVER,
        "last_updated": "2026-10-19T00:00:00Z",
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


def build_project(root: Path) -> Path:
    """Proyecto sintético válido para `prepare` (política v2)."""
    for rel in ("tests", "src", "docs"):
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
    (root / CONTRACT_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
    (root / PLAN_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / PLAN_FILE).write_bytes(PLAN_BYTES)
    (root / AUTHORITY_REF).parent.mkdir(parents=True, exist_ok=True)
    (root / AUTHORITY_REF).write_text(
        "# Authorized execution fixture (epic-006)\n", encoding="utf-8")
    (root / STATE_FILE).write_text(
        json.dumps(fixture_state_document(), ensure_ascii=False) + "\n",
        encoding="utf-8")
    return root


# ---------------------------------------------------------------- fixture


class ScribeRowCase(unittest.TestCase):
    """Proyecto sintético con paquete dispatched y recibo durable de la única
    parte entregada (flujo receive de 003-002).

    Cada caso fija rol/subfase/kind por atributos de instancia: el kind va
    ligado en el recibo, así que cada probe construye un proyecto fresco.
    """

    ROLE = "scribe"
    SUBSTAGE = "memory"
    PART_NAME = "scribe-report"
    PART_BYTES = (
        b"# Scribe role report (fixture U7 006-005)\n"
        b"Informe unico del scribe entregado por la via del adaptador como UNA\n"
        b"sola parte con artifact_kind: role-report.\n"
    )
    DEFAULT_PART_KIND = "role-report"

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u7-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        # HOME/XDG redirigidos dentro del tempdir: nunca la config real del
        # host. Las credenciales del runtime se retiran del entorno hijo.
        self.home = Path(self._tmp) / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        (self.home / ".config").mkdir(parents=True, exist_ok=True)

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

    def new_dispatched_project(self, *, role: str | None = None,
                               substage: str | None = None,
                               part_kind: str | None = None) -> None:
        """Proyecto sintético nuevo (tempdir) con el paquete dispatched y el
        recibo durable de la única parte entregada."""
        tmp = tempfile.mkdtemp(prefix="cdad-006-005-u7red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.role = role or self.ROLE
        self.substage = substage or self.SUBSTAGE
        self.part_kind = part_kind or self.DEFAULT_PART_KIND
        self.root = build_project(Path(tmp) / "proj")
        self.establish_dispatched()
        self.establish_received()

    def establish_dispatched(self) -> None:
        """Prepara el paquete del fixture y lo observa como dispatched (I8)."""
        prep = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--role", self.role, "--substage", self.substage,
            "--objective",
            f"006-005 U7 RED fixture ({self.role}/{self.substage})",
        ])
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` de {self.role}/"
                f"{self.substage} debe publicar el paquete: "
                f"{out_text(prep)} {err_text(prep)}")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.packet_id = state["active_packet"]["id"]
        self.assertEqual(
            state["active_packet"]["role"], self.role,
            msg="precondición (fixture): el paquete activo pertenece al rol "
                "del caso")
        self.assertEqual(
            state["active_packet"]["substage"], self.substage,
            msg="precondición (fixture): el paquete activo pertenece a la "
                "subfase del caso")
        execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            execution_id,
            msg="precondición (fixture): state.execution debe referenciar el "
                "contexto v2")
        self.execution_id = execution_id
        self.execution_context_path = (
            self.root / ".cdad" / "executions" / execution_id
            / "execution.json")
        self.assertTrue(
            self.execution_context_path.is_file(),
            msg="precondición (fixture): el contexto v2 debe existir")
        self.packet_dir = self.root / ".cdad" / "packets" / self.packet_id
        self.packet_path = self.packet_dir / "PACKET.md"
        self.request_path = self.packet_dir / "REQUEST.json"
        for path in (self.packet_path, self.request_path):
            self.assertTrue(
                path.is_file(),
                msg=f"precondición (fixture): paquete publicado {path}")
        observation_path = self.root / "docs" / "observations-u7.json"
        observation_path.write_text(
            json.dumps(observation_document(SESSION), indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        record = self.run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg="precondición (fixture): --record-dispatch debe registrar el "
                f"intento: {out_text(record)} {err_text(record)}")
        state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): el paquete activo queda dispatched")

    def establish_received(self) -> None:
        """Recibo durable de la única parte (receive de 003-002, rc=0): el kind
        declarado va en el descriptor y gatea en `materialize`, no en
        `receive`."""
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
            msg="precondición (fixture): `receive` debe aceptar la entrega "
                "(la tabla cerrada gatea en materialize, no en receive): "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r} part_kind={self.part_kind!r}")
        self.assertTrue(
            self.receipt_path.is_file(),
            msg="precondición (fixture): el receipt durable debe existir")

    # -- corridas del CLI ---------------------------------------------------

    def child_env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)
        env["XDG_CONFIG_HOME"] = str(self.home / ".config")
        for key in ("OPENCODE_PASSWORD", "OPENCODE_SERVER_PASSWORD"):
            env.pop(key, None)
        return env

    def run_packet_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(PACKET_SCRIPT), *args],
            cwd=str(REPO_ROOT), capture_output=True, env=self.child_env(),
            timeout=180,
        )

    def run_result_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        """Corrida del CLI de 003-002 con cwd en la raíz del fixture: los
        targets declarados son project-relative, no cwd-relative."""
        return subprocess.run(
            [sys.executable, str(RESULT_SCRIPT), *args],
            cwd=str(self.root), capture_output=True, env=self.child_env(),
            timeout=180,
        )

    # -- autorización --------------------------------------------------------

    def build_authorization(self, copies: list[dict], *,
                            receipt_sha: str | None = None) -> dict:
        return {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "receipt_sha256": receipt_sha or self.receipt_sha256,
            "authorized_by": AUTHORIZED_BY,
            "authority_ref": AUTHORITY_REF,
            "approval_effect": False,
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

    def prepare_target(self, target: str) -> None:
        """Crea el directorio del target dentro del fixture (un target mal
        resuelto cae dentro del fixture, nunca en este repo)."""
        (self.root / target).parent.mkdir(parents=True, exist_ok=True)

    # -- oráculos de efecto --------------------------------------------------

    def snapshot_state_and_receipt(self) -> None:
        self.state_before = self.state_path.read_bytes()
        self.receipt_before = self.receipt_path.read_bytes()

    def assert_no_state_or_receipt_change(self, label: str) -> None:
        self.assertEqual(
            self.state_path.read_bytes(), self.state_before,
            msg=f"{label}: docs/.cdad-state.json debe permanecer intacto (el "
                f"único escritor del state es el orquestador; la "
                f"materialización no aprueba nada)")
        self.assertEqual(
            self.receipt_path.read_bytes(), self.receipt_before,
            msg=f"{label}: el receipt durable debe permanecer intacto")

    def assert_target_identical(self, target: Path) -> None:
        """El materializado existe y su sha es idéntico al de la parte
        recibida (y el part del store conserva los bytes originales, de modo
        que el materializado deriva de `receive`, no de una copia manual)."""
        self.assertTrue(
            target.is_file(),
            msg=f"debe existir el materializado en {target}")
        stored_part = self.final_dir / "parts" / f"{self.PART_NAME}.utf8"
        self.assertTrue(
            stored_part.is_file(),
            msg="precondición: el part recibido debe existir en el store")
        part_sha = hashlib.sha256(self.PART_BYTES).hexdigest()
        self.assertEqual(
            hashlib.sha256(stored_part.read_bytes()).hexdigest(), part_sha,
            msg="el part recibido en el store debe conservar los bytes "
                "originales")
        self.assertEqual(
            hashlib.sha256(target.read_bytes()).hexdigest(), part_sha,
            msg=f"el sha del materializado {target.name!r} debe ser idéntico "
                f"al de la parte recibida (sin copia manual)")

    def assert_rejection(self, proc, label: str, targets: tuple) -> None:
        """Clausura fail-closed común: rc≠0, guard de CLI ausente, sin
        traceback, sin stdout, sin target escrito y state/receipt intactos."""
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"{label}: el rechazo debe fallar cerrado (rc=0 con escritura "
                f"sería un bypass del fail-closed): rc={proc.returncode} "
                f"stdout={out_text(proc)!r}")
        assert_reachable_or_invalid_red(err_text(proc), label)
        self.assertNotIn("Traceback", err_text(proc),
                         msg=f"{label}: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg=f"{label}: en rechazo no debe emitirse evidencia por stdout")
        for target in targets:
            self.assertFalse(
                (self.root / target).exists(),
                msg=f"{label}: el rechazo dejó el target {target!r} (sin "
                    f"prefijo parcial)")
        self.assert_no_state_or_receipt_change(label)


# ------------------------------------------------------------ PD-26 positivo


class TestPd26ScribeRoleReportMaterializes(ScribeRowCase):
    """PD-26/§2.8.3 (positivo — el RED): la parte única `role-report` de un
    recibo `scribe`/`memory` se materializa dentro de la carpeta de la spec."""

    def test_pd26_scribe_role_report_materializes_into_the_spec_folder(
            self) -> None:
        """PD-26 (RED): `materialize` rc=0 hacia un target dentro de
        `docs/specs/<feature>/`, con sha IDÉNTICO al de la parte recibida;
        recibo `pending`; `approval_effect` declarado `false` y el state y el
        receipt intactos (la materialización no aprueba). Hoy rc≠0: la fila del
        scribe no admite `role-report` y el informe del rol no tiene camino
        mecánico (el rodeo medido en `execution.md`:255, ahora en cada
        cierre)."""
        self.new_dispatched_project()  # scribe/memory, parte role-report
        receipt = json.loads(self.receipt_path.read_text(encoding="utf-8"))
        self.assertEqual(
            receipt["role"], "scribe",
            msg="precondición (fixture): el recibo liga el rol scribe")
        self.assertEqual(
            receipt["substage"], "memory",
            msg="precondición (fixture): el recibo liga la subfase memory")
        self.assertEqual(
            [part["artifact_kind"] for part in receipt["parts"]],
            ["role-report"],
            msg="precondición (fixture): la entrega común del scribe produce "
                "UNA sola parte con kind `role-report`")
        self.assertEqual(
            receipt["semantic_status"], "pending",
            msg="PD-26: el recibo nace `pending` y no aprueba nada")

        authorization = self.build_authorization(
            [{"part": self.PART_NAME, "target": TARGET_REPORT,
              "expected_previous_sha256": None}])
        self.assertFalse(
            authorization["approval_effect"],
            msg="PD-26: la materialización del informe no aprueba "
                "(`approval_effect: false`)")
        self.prepare_target(TARGET_REPORT)
        auth_path = self.write_authorization(authorization)
        self.snapshot_state_and_receipt()
        proc = self.materialize(auth_path)
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-26/§2.8.3: la tabla cerrada debe admitir `role-report` "
                "para el scribe (`memory`), de modo que el informe del rol se "
                "materialice dentro de `docs/specs/<feature>/` — es la misma "
                "responsabilidad y la misma forma que el informe del architect "
                "(precedente 005-007 T4) y el scribe corre en cada cierre: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="PD-26: materialize terminó con traceback")
        self.assert_target_identical(self.root / TARGET_REPORT)
        self.assert_no_state_or_receipt_change("PD-26 (positivo)")


# -------------------------------------------------------- PD-26 destino negativo


class TestPd26MemoryBankTargetsStayRejected(ScribeRowCase):
    """PD-26/§2.8.3 (destino negativo): el Memory Bank NO es alcanzable por el
    informe del rol; su separación en los cuatro archivos sigue siendo el acto
    declarado del orquestador (ADR-003)."""

    def test_pd26_memory_bank_targets_stay_rejected_naming_the_allowed_root(
            self) -> None:
        """PD-26 (RED): un target del Memory Bank con `role-report` ⇒ rc≠0
        NOMBRANDO la raíz permitida `docs/specs/<feature>/`; sin target
        escrito, sin stdout, sin traceback, state y receipt intactos. Hoy el
        rechazo existe pero por el eje rol (la fila no admite el kind) y no
        nombra la raíz permitida: la frontera declarada «el Memory Bank no es
        alcanzable por ese kind» no está establecida."""
        for target in MEMORY_BANK_TARGETS:
            with self.subTest(target=target):
                self.new_dispatched_project()  # scribe/memory, role-report
                self.prepare_target(target)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": target,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assert_rejection(
                    proc, f"PD-26 (Memory Bank {target!r})", (target,))
                self.assertTrue(
                    ALLOWED_ROOT in err_text(proc),
                    msg="PD-26/§2.8.3: con la fila del scribe admitiendo "
                        "`role-report`, un target del Memory Bank debe "
                        "rechazarse POR LA RAÍZ PERMITIDA y el diagnóstico "
                        f"debe nombrar {ALLOWED_ROOT!r}: "
                        f"stderr={err_text(proc)!r}")


# ------------------------------------------------------- PD-26 eje rol (ancla)


class TestPd26RoleAxisStaysClosed(ScribeRowCase):
    """PD-26/PD-23/D-17 (ancla): la fila del scribe gana `role-report`; el
    resto del eje rol no se relaja (D-17 rechaza admitirlo «para todos los
    roles»)."""

    def test_pd26_role_axis_role_report_of_other_roles_stays_rejected(
            self) -> None:
        """PD-26 (ancla, pasa hoy): `role-report` de test-writer, implementer y
        reviewer sigue rechazado por el eje rol, sin escribir el target."""
        cases = (
            ("test-writer", "red"),
            ("test-writer", "audit"),
            ("implementer", "green"),
            ("reviewer", "review"),
            ("architect", "brainstorm"),
        )
        for role, substage in cases:
            with self.subTest(role=role, substage=substage):
                self.new_dispatched_project(role=role, substage=substage,
                                            part_kind="role-report")
                self.prepare_target(TARGET_REPORT)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": TARGET_REPORT,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assert_rejection(
                    proc, f"PD-26 (eje rol {role}/{substage})",
                    (TARGET_REPORT,))
                self.assertTrue(
                    re.search(r"rol|role|kind|artifact", err_text(proc),
                              re.IGNORECASE),
                    msg=f"PD-26 ({role}/{substage}): el diagnóstico no nombra "
                        f"el motivo (rol/kind): {err_text(proc)!r}")


# ------------------------------------------------------------- R3 (ancla)


class TestPd26R3CrossingsStayRejected(ScribeRowCase):
    """PD-26/PD-23 (ancla, R3): los cruces rol↔kind siguen rechazados; la
    fila del scribe admite `role-report`, no los kinds de otros roles."""

    def test_pd26_r3_crossings_stay_rejected(self) -> None:
        """PD-26 (ancla, pasa hoy): cada cruce usa el target que ese kind solo
        autoriza, de modo que la única razón de rechazo observable sea el
        cierre rol↔kind (no la raíz)."""
        for role, substage, kind, target in R3_CROSSINGS:
            with self.subTest(role=role, substage=substage, kind=kind):
                self.new_dispatched_project(role=role, substage=substage,
                                            part_kind=kind)
                self.prepare_target(target)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": target,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assert_rejection(
                    proc, f"R3 ({role}/{substage} con kind {kind!r})",
                    (target,))
                self.assertTrue(
                    re.search(r"rol|role|kind|artifact", err_text(proc),
                              re.IGNORECASE),
                    msg=f"R3 ({role}/{substage}): el diagnóstico no nombra el "
                        f"motivo: {err_text(proc)!r}")


# ------------------------------------------------------------- R5 (ancla)


class TestPd26R5ScribeFileKindsStillMaterialize(ScribeRowCase):
    """PD-26 (ancla, R5): los cuatro `scribe-*` siguen siendo la entrega por
    archivo y materializan sus raíces-archivo del Memory Bank."""

    def test_pd26_r5_scribe_file_kinds_still_materialize(self) -> None:
        """PD-26 (ancla, pasa hoy): los cuatro kinds por archivo del scribe
        materializan sus raíces-archivo con bytes idénticos y sin tocar el
        state (la deuda §8 item 3 sigue vigente: la entrega por archivo no se
        retira)."""
        for kind, target in SCRIBE_FILE_KINDS:
            with self.subTest(kind=kind):
                self.new_dispatched_project(part_kind=kind)
                self.prepare_target(target)
                auth_path = self.write_authorization(
                    self.build_authorization(
                        [{"part": self.PART_NAME, "target": target,
                          "expected_previous_sha256": None}]))
                self.snapshot_state_and_receipt()
                proc = self.materialize(auth_path)
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"R5 ({kind}): el kind por archivo del scribe debe "
                        f"seguir materializando su raíz-archivo "
                        f"({target!r}) exactamente como hoy: "
                        f"rc={proc.returncode} stdout={out_text(proc)!r} "
                        f"stderr={err_text(proc)!r}")
                self.assert_target_identical(self.root / target)
                self.assert_no_state_or_receipt_change(f"R5 ({kind})")


# ------------------------------------------------- tabla de materialización


class TestPd26MaterializationTableAssetIsUnchanged(unittest.TestCase):
    """PD-26/PD-23 (ancla): `artifact-policy.json` no cambia — `role-report`
    ya existe en la tabla con raíz `docs/specs/<feature>/`, así que el oráculo
    es alcanzable sin tocar el dato del producto."""

    def test_pd26_materialization_table_asset_is_unchanged(self) -> None:
        """PD-26 (ancla, pasa hoy): el digest del asset es el del HEAD medido.
        Se inspeccionan SÓLO los bytes (sha256): el archivo no se parsea ni su
        contenido se usa como oráculo de comportamiento."""
        self.assertTrue(
            ARTIFACT_POLICY.is_file(),
            msg=f"precondición: debe existir {ARTIFACT_POLICY.name}")
        digest = hashlib.sha256(ARTIFACT_POLICY.read_bytes()).hexdigest()
        self.assertEqual(
            digest, ARTIFACT_POLICY_SHA256,
            msg="PD-26/PD-23: la tabla de materialización "
                "(`skills/cdad-cycle/assets/artifact-policy.json`) no cambia "
                "en esta feature: el kind `role-report` y su raíz ya existen, "
                f"la fila del scribe es de `_allowed_kinds` — digest "
                f"observado {digest}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
