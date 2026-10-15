#!/usr/bin/env python3
"""005-001 T4 RED — Prueba decisiva PD-17: un único escenario secuencial
end-to-end, caja negra sobre el CLI (subprocess del entrypoint del repo).

Contract:
- docs/specs/005-001-idle-and-v7-bootstrap/spec.md (§2 PD-17 como prueba
  decisiva; además PD-1, PD-3+PD-12 slice, PD-5, PD-16, PD-11, PD-7, PD-19,
  PD-24, PD-8 e INV-1/INV-2/INV-3/INV-5; §7 D1/D2/D3).
- docs/specs/005-001-idle-and-v7-bootstrap/plan.md (T4; test focal declarado
  `tests/test_005_001_t4_decisive.py`; consume T1, T2, T3 y T-CORR).

Superficie observable bajo prueba (§2 del contrato; nada de plomería):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --role <rol> --substage <sub> --objective <texto>
    python3 scripts/cdad_packet.py prepare --project-root R \
        --record-dispatch <id> --attempt-id <a> --input <obs.json>     # I8
    python3 scripts/cdad_packet.py prepare --project-root R \
        --resume-packet <id>                                           # PD-16
    python3 scripts/cdad_packet.py prepare --project-root R \
        --replace-packet <id> --reason <texto>                         # PD-7
    python3 scripts/cdad_result.py receive \
        --project-root R --execution-context E.json --packet PACKET.md \
        --request REQUEST.json --descriptor RESULT.json                # 003-002
    python3 scripts/cdad_result.py validate-receipt \
        --project-root R --receipt receipt.json

Escenario (PD-17, un solo método secuencial; cada bloque nombra su PD):

  S1. fixture con epic E (epic_history stage "epic-plan", approved_by) y
      feature F SIN spec aprobada (el archivo `docs/specs/F/spec.md` NO
      existe aún: PD-17 lo CREA en el paso siguiente). `prepare --role
      architect --substage discovery` → rc=0 (discovery autorizado sin
      spec; PD-1; el contrato del architect es el plan del epic, D1/D2).
  S2. RECEPCIÓN del paquete del architect por el flujo real del
      orquestador: `prepare --record-dispatch` (I8) → dispatched; staging
      del texto final bajo `.cdad/inbox` + manifest + descriptor;
      `cdad_result.py receive` → receipt durable ligado a la identidad;
      `validate-receipt` → rc=0; transición de estado del orquestador
      (único escritor del state) a `completed` (INV-4: la misma llave
      `active_packet.status`).
  S3. `prepare --role test-writer --substage red` → rc=2, marcador
      `approval pending` que nombra el registro y la ruta de la spec
      (PD-3+PD-12), SIN paquete nuevo en disco ni efectos (árbol y state
      byte a byte idénticos).
  S4. Se CREA la spec del fixture y se registra la aprobación pineada
      (contract_path + contract_sha256; INV-2: el registro de aprobación
      es del orquestador, no del CLI) → `prepare --role test-writer
      --substage red` → rc=0; paquete P1 queda `prepared` y NO se
      despacha (PD-5).
  S5. OBSOLESCENCIA Y REEMPLAZO sobre un paquete TODAVÍA PREPARADO y NO
      DESPACHADO. Elección explícita del paquete a reemplazar: **P1**
      (contrato = la spec del fixture), porque: (i) el paquete del
      architect quedó `completed` en S2 y el negativo del paso 6 excluye
      explícitamente reemplazar un paquete terminado; (ii) P1 es el único
      paquete `prepared` del árbol y es el paquete ACTIVO; (iii) su
      contrato (la spec pineada C1, path+sha) permite ejercitar la cadena
      completa PD-8 → PD-11 → PD-7 sin inventar evidencia: la spec se
      edita y se re-registra su aprobación. Se verifica:
      (a) el sha registrado en el REQUEST.json difiere del actual
      (PD-8a); (b) `prepare --resume-packet P1` → rc=2 `packet obsolete`
      nombrando el valor REGISTRADO y el ACTUAL y señalando
      `--replace-packet` (PD-16); (c) `prepare --replace-packet P1
      --reason` → rc=2 `approval pending` mientras el contrato nuevo NO
      está aprobado (PD-11: el reemplazo no inventa evidencia); con la
      autorización re-registrada (re-pin del registro `specification`)
      → rc=0: paquete nuevo (id siguiente libre), P1 byte a byte
      idéntico (INV-3), `.superseded.json` con motivo y traza PD-24,
      encargo conservado campo a campo (PD-19) y contrato re-resuelto al
      actual; sin cambios en `stage_history`/`epic_history` (INV-2).
  S6. Negativos: `--replace-packet` sobre el paquete del architect (que
      quedó `completed`) → rc=2 sin efectos; `--replace-packet` sobre un
      paquete preparado SIN obsolescencia verificable (el paquete nuevo
      del reemplazo) → rc=2 sin efectos (PD-8: no es un atajo).

RED hoy: el escenario fracasa en S3 — el CLI devuelve rc=2 y NO publica
paquete (el bloqueo existe), pero su stderr es el error genérico
`ERROR: cannot read contract <ruta-de-la-spec>: [Errno 2] ...` SIN el
marcador `approval pending` ni los tokens `stage_history|specification|
approved` (PD-3/PD-12 en el subcaso PD-17-2 con el archivo de la spec
ausente: PD-17 lo crea recién en el paso 3). Con el archivo presente y
sin aprobación el marcador sí aparece (T1 PD-3 verde). Defecto reportado
al orquestador con esta evidencia; el resto del escenario (S1-S2, S4-S6)
conforma el contrato. Todo fallo del RED debe ser una AssertionError de
comportamiento, nunca ImportError/SyntaxError; cada test preverifica la
superficie declarada (patrón B-1: sin "unrecognized").

Fixtures offline: proyectos sintéticos en tempdirs (política válida, plan
del epic aprobado en `epic_history`, delegación HITL activa); el registro
de despacho usa el documento de observación de claves cerradas (I8); el
`receive` usa kinds plausibles del rol (la tabla cerrada de kinds gatea en
`materialize`, no en `receive` — evidencia R5 de 003-002 — y este
escenario nunca materializa). Ninguna escritura en este repo y ninguna
lectura de implementación (skills/cdad-cycle/scripts/cdad_packet.py).
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
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

EPIC_ID = "epic-005-real-operation"
FEATURE_ID = "005-001-idle-and-v7-bootstrap"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
PLAN_FILE = f"docs/epics/{EPIC_ID}/plan.md"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"

APPROVER = "Pablo"
ARCHITECT_OBJECTIVE = "005-001 T4 PD-17: discovery del architect sin spec aprobada"
WRITER_OBJECTIVE = "005-001 T4 PD-17: red del test-writer tras la aprobación pineada"
REASON = "spec re-aprobada despues de editar el contrato del paquete P1"
ATTEMPT_ID = "att-005-001-t4-pd17-discovery"

PLAN_BYTES = b"# Epic plan fixture (005-001 T4)\n"
# La spec creada en S4 (PD-17 paso 3); NO existe durante S1-S3.
SPEC_BYTES = b"# Spec fixture (005-001 T4)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada tras aprobar (deriva el sha)\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()
SPEC_DRIFT_SHA256 = hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest()

PACKET_BEGIN = "---cdad-packet-json"
PENDING_MARKER = "approval pending"
OBSOLETE_MARKER = "packet obsolete"
INCOHERENT_MARKER = "state incoherent"
SUPERSEDED_FILE = ".superseded.json"
PENDING_TOKENS_RE = re.compile(r"stage_history|specification|approved")
REPLACE_PACKET_RE = re.compile(r"(?i)replace[-_ ]packet|reemplaz\w*\s+paquete")

# PD-19/PD-24: el encargo del REQUEST.json (universo cerrado del contrato).
ASSIGNMENT_FIELDS = (
    "execution_id",
    "role",
    "substage",
    "objective",
    "inputs",
    "read_scope",
    "write_scope",
    "invariants",
    "expected_output",
    "evidence_required",
)

# Texto final del architect (S2): staging bajo el inbox fijo `.cdad/inbox`.
FINAL_TEXT_PARTS: dict[str, bytes] = {
    "architect-report": (
        b"# Architect discovery draft (fixture T4 PD-17)\n"
        b"Reporte de discovery del architect; la feature NO tiene spec aprobada.\n"
    ),
    "architect-notes": (
        b"# Architect discovery notes (fixture T4 PD-17)\n"
        b"Notas auxiliares del mismo intento; bytes separados conservados.\n"
    ),
}
PART_KINDS: dict[str, str] = {
    "architect-report": "architect-role-report",
    "architect-notes": "architect-notes",
}
BASELINE_REF = "orchestrator-staged-reference"
BASELINE_SHA256 = "0" * 64
MANIFEST_PATH = ".cdad/inbox/changes.json"
DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"


# ---------------------------------------------------------------- fixtures


def run_packet_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def run_result_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RESULT_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def tree_snapshot(root: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        snapshot[rel] = path.read_bytes() if path.is_file() else None
    return snapshot


def read_state(root: Path) -> dict:
    return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))


def write_state(root: Path, state: dict) -> None:
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")


def packet_dir(root: Path, packet_id: str) -> Path:
    return root / ".cdad" / "packets" / packet_id


def packet_ids(root: Path) -> list[str]:
    base = root / ".cdad" / "packets"
    if not base.is_dir():
        return []
    return sorted(d.name for d in base.iterdir() if d.is_dir())


def packet_bytes(root: Path, packet_id: str, name: str) -> bytes:
    return (packet_dir(root, packet_id) / name).read_bytes()


def request_of(root: Path, packet_id: str) -> dict:
    return json.loads(
        packet_bytes(root, packet_id, "REQUEST.json").decode("utf-8"))


def build_fixture(root: Path) -> Path:
    """Proyecto sintético del escenario PD-17: epic E con `epic-plan`
    aprobado en `epic_history`, feature F activa, SIN spec aprobada ni
    archivo `docs/specs/F/spec.md` (PD-17 lo crea recién en su paso 3)."""
    root.mkdir(parents=True)
    for rel in ("tests", "src", "lib"):
        (root / rel).mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    (root / POLICY_FILE).write_text(json.dumps({
        "schema_version": 1,
        "path_policy": {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        },
        "temporary_roots": [".cdad/tmp"],
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = root / PLAN_FILE
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_bytes(PLAN_BYTES)
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-005)\n",
                         encoding="utf-8")
    state = {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        # D1/D2: la aprobación del plan del epic habilita al architect,
        # sin pin de hash (mandato vivo del epic).
        "epic_history": [{
            "epic": EPIC_ID,
            "stage": "epic-plan",
            "approved_by": APPROVER,
            "approved_at": "2026-10-08T00:00:00Z",
        }],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": "red",
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [],
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
    write_state(root, state)
    return root


def observation_document() -> dict:
    """Documento de observación I8 (claves cerradas: cinco campos +
    provenance) para el registro de despacho del fixture."""
    return {
        "runtime": "opencode",
        "model_configured": "mofgw/deepseek-v4.1-flash",
        "model_reported": "mofgw/deepseek-v4.1-flash",
        "session": "ses-005-001-t4-pd17-0001",
        "started_at": "2026-10-08T00:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def spec_sha_of(root: Path) -> str:
    return hashlib.sha256((root / SPEC_FILE).read_bytes()).hexdigest()


class T4Decisive(unittest.TestCase):
    """PD-17 — un único escenario secuencial end-to-end (decode en S1..S6)."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-001-t4-")
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", self._tmp], check=False)

    def assert_no_effects(self, label: str, root: Path, before: dict,
                          state_before: bytes,
                          proc: subprocess.CompletedProcess, *,
                          expect_rc: int = 2, marker: str | None = None,
                          forbidden_markers: tuple[str, ...] = ()) -> None:
        """Rechazo del contrato: rc/stdout/traceback/marcador esperados y
        ninguna publicación (árbol y state byte a byte idénticos; ningún
        `.superseded.json` creado)."""
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"{label}: la superficie declarada en spec §2 debe "
                f"reconocerse; un fallo por argv desconocido no es "
                f"comportamiento: {out!r}")
        self.assertEqual(
            proc.returncode, expect_rc,
            msg=f"{label}: rc esperado {expect_rc}: {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg=f"{label}: el rechazo imprimió contenido por stdout")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"{label}: fallo con traceback: {proc.stderr!r}")
        if marker is not None:
            self.assertIn(
                marker, proc.stderr,
                msg=f"{label}: stderr sin el marcador {marker!r}: "
                    f"{proc.stderr!r}")
        for banned in forbidden_markers:
            self.assertNotIn(
                banned, out,
                msg=f"{label}: el marcador se mezcló con {banned!r} "
                    f"(PD-12: exclusivos por condición): {out!r}")
        self.assertEqual(
            tree_snapshot(root), before,
            msg=f"{label}: hubo publicación parcial (árbol modificado)")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg=f"{label}: el state cambió en un rechazo")
        for pid in packet_ids(root):
            superseded = packet_dir(root, pid) / SUPERSEDED_FILE
            rel = superseded.relative_to(root).as_posix()
            if rel in before and before[rel] is not None:
                # Registro de superación legítimo preexistente (p.ej. el
                # `.superseded.json` de un paquete reemplazado en S5c3,
                # PD-7/PD-24): no fue creado por la operación rechazada.
                continue
            self.assertFalse(
                superseded.is_file(),
                msg=f"{label}: quedó un registro de superación ({pid})")

    def assert_precondition(self, label: str, condition: bool, detail: str) -> None:
        self.assertTrue(
            condition,
            msg=f"precondición (fixture) {label}: {detail}")

    # -------------------------------------------------------- el escenario

    def test_pd17_decisive_single_sequence(self) -> None:
        root = build_fixture(Path(self._tmp) / "proj")

        # -------------------------------------------------- S1 (PD-1/D1)
        prepare_architect = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--role", "architect", "--substage", "discovery",
            "--objective", ARCHITECT_OBJECTIVE,
        ])
        self.assertEqual(
            prepare_architect.returncode, 0,
            msg=f"S1/PD-1: el architect con el plan del epic aprobado debe "
                f"habilitarse SIN entrada `specification` de la feature: "
                f"{prepare_architect.stdout!r} {prepare_architect.stderr!r}")
        self.assertTrue(
            prepare_architect.stdout.startswith(PACKET_BEGIN),
            msg="S1/PD-1: stdout sin paquete canónico")
        state = read_state(root)
        architect_id = state["active_packet"]["id"]
        self.assertEqual(
            state["active_packet"].get("status"), "prepared",
            msg=f"S1: paquete activo tras prepare: {state['active_packet']!r}")
        self.assertEqual(
            state["active_packet"].get("role"), "architect",
            msg=f"S1: el paquete activo no lleva el rol architect: "
                f"{state['active_packet']!r}")
        execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            execution_id, msg=f"S1: state.execution sin id: {execution_id!r}")
        context_path = (root / ".cdad" / "executions" / execution_id
                        / "execution.json")
        self.assert_precondition(
            "S1", context_path.is_file(),
            "el contexto v2 no fue publicado en .cdad/executions")
        architect_request = request_of(root, architect_id)
        self.assertEqual(
            (architect_request.get("contract") or {}).get("kind"),
            "approved-epic-plan",
            msg=f"S1/D1: el contrato del architect no es el plan del epic: "
                f"{architect_request.get('contract')!r}")
        self.assertEqual(
            (architect_request.get("contract") or {}).get("path"), PLAN_FILE,
            msg=f"S1/D1: el contrato del architect no nombra {PLAN_FILE}: "
                f"{architect_request.get('contract')!r}")
        self.assertEqual(
            [architect_id], packet_ids(root),
            msg=f"S1: paquetes en disco: {packet_ids(root)}")
        self.assertEqual(
            prepare_architect.stdout,
            packet_bytes(root, architect_id, "PACKET.md").decode("utf-8"),
            msg="S1: PACKET.md difiere del stdout de prepare")

        # --------------------------- S2 (flujo real del orquestador: I8,
        # receive, validate-receipt y transición a completed)
        observation_path = root / "docs" / "dispatch-observations-t4.json"
        observation_path.parent.mkdir(parents=True, exist_ok=True)
        observation_path.write_text(
            json.dumps(observation_document(), indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        record = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--record-dispatch", architect_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"S2/I8: --record-dispatch debe registrar el intento: "
                f"{record.stdout!r} {record.stderr!r}")
        self.assertEqual(
            read_state(root)["active_packet"].get("status"), "dispatched",
            msg="S2/I8: el paquete activo no quedó dispatched")
        inbox = root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in FINAL_TEXT_PARTS.items():
            (inbox / f"{name}.md").write_bytes(data)
        (root / MANIFEST_PATH).write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": BASELINE_REF,
            "baseline_sha256": BASELINE_SHA256,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        descriptor_doc = {
            "schema_version": 1,
            "execution_id": execution_id,
            "packet_id": architect_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [
                {"name": name, "artifact_kind": PART_KINDS[name],
                 "staged_path": f".cdad/inbox/{name}.md"}
                for name in sorted(FINAL_TEXT_PARTS)
            ],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": BASELINE_REF,
                "baseline_sha256": BASELINE_SHA256,
                "manifest_path": MANIFEST_PATH,
            },
            "run_evidence_ref": None,
        }
        descriptor_path = root / DESCRIPTOR_PATH
        descriptor_path.write_text(
            json.dumps(descriptor_doc, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
        receive = run_result_cli([
            "receive", "--project-root", str(root),
            "--execution-context", str(context_path),
            "--packet", str(packet_dir(root, architect_id) / "PACKET.md"),
            "--request", str(packet_dir(root, architect_id) / "REQUEST.json"),
            "--descriptor", str(descriptor_path),
        ])
        self.assertNotIn(
            "unrecognized", receive.stdout + receive.stderr,
            msg=f"S2: la superficie `receive` de 003-002 debe reconocerse: "
                f"{receive.stdout!r} {receive.stderr!r}")
        self.assertEqual(
            receive.returncode, 0,
            msg=f"S2: receive debe aceptar el paquete dispatched y persistir "
                f"los bytes del texto final: rc={receive.returncode} "
                f"stdout={receive.stdout!r} stderr={receive.stderr!r}")
        self.assertNotIn("Traceback", receive.stderr,
                         msg=f"S2: receive terminó con traceback: "
                             f"{receive.stderr!r}")
        receipt = json.loads(receive.stdout)
        final_dir = (root / ".cdad" / "runtime" / "results"
                     / execution_id / architect_id)
        receipt_path = final_dir / "receipt.json"
        self.assertTrue(
            receipt_path.is_file(),
            msg=f"S2: no quedó receipt durable en {receipt_path}")
        self.assertEqual(
            receipt.get("schema_version"), 1,
            msg=f"S2: schema_version del receipt: {receipt.get('schema_version')!r}")
        self.assertEqual(
            receipt.get("packet_id"), architect_id,
            msg=f"S2: el receipt no liga el paquete del architect: {receipt!r}")
        self.assertEqual(
            receipt.get("execution_id"), execution_id,
            msg=f"S2: el receipt no liga la ejecución: {receipt!r}")
        self.assertEqual(
            receipt.get("feature_id"), FEATURE_ID,
            msg=f"S2: el receipt no liga la feature: {receipt!r}")
        self.assertEqual(
            receipt.get("role"), "architect",
            msg=f"S2: el receipt no liga el rol: {receipt!r}")
        self.assertEqual(
            receipt.get("substage"), "discovery",
            msg=f"S2: el receipt no liga la subfase: {receipt!r}")
        self.assertEqual(
            receipt.get("semantic_status"), "pending",
            msg=f"S2: ningún recibo aprueba semánticamente (§6): "
                f"{receipt.get('semantic_status')!r}")
        self.assertEqual(
            receipt.get("state_transition_requested"), "received",
            msg=f"S2: transición lógica del recibo: "
                f"{receipt.get('state_transition_requested')!r}")
        receipt_parts = {part["name"]: part for part in receipt["parts"]}
        self.assertEqual(
            sorted(receipt_parts), sorted(FINAL_TEXT_PARTS),
            msg=f"S2: parts del receipt: {sorted(receipt_parts)}")
        for name, data in FINAL_TEXT_PARTS.items():
            self.assertEqual(
                receipt_parts[name]["sha256"],
                hashlib.sha256(data).hexdigest(),
                msg=f"S2: digest del part {name!r} no corresponde a los "
                    f"bytes staged")
            stored = final_dir / "parts" / f"{name}.utf8"
            self.assertEqual(
                stored.is_file() and stored.read_bytes(), data,
                msg=f"S2: el part {name!r} persistido difiere de los bytes "
                    f"staged")
        self.assertEqual(
            receive.stdout, receipt_path.read_text(encoding="utf-8"),
            msg="S2: stdout debe ser exactamente el receipt.json canónico")
        valid = run_result_cli([
            "validate-receipt", "--project-root", str(root),
            "--receipt", str(receipt_path),
        ])
        self.assertEqual(
            valid.returncode, 0,
            msg=f"S2: validate-receipt debe aceptar el receipt durable "
                f"íntegro: rc={valid.returncode} stderr={valid.stderr!r}")
        # Transición de estado del orquestador (el state solo lo escribe el
        # orquestador, §9): el paquete del architect queda `completed`.
        state = read_state(root)
        state["active_packet"]["status"] = "completed"
        write_state(root, state)
        state = read_state(root)
        self.assertEqual(
            state["active_packet"].get("id"), architect_id,
            msg=f"S2: binding del paquete terminado: "
                f"{state['active_packet']!r}")
        self.assertEqual(
            state["active_packet"].get("status"), "completed",
            msg=f"S2/INV-4: el paquete del architect no quedó `completed`: "
                f"{state['active_packet']!r}")
        self.assertTrue(
            (packet_dir(root, architect_id) / "PACKET.md").is_file(),
            msg="S2: el paquete terminado debe seguir durable en disco")
        self.assertTrue(
            receipt_path.is_file(),
            msg="S2: el receipt durable debe sobrevivir la transición")

        # ------------------- S3 (PD-17 paso 2: PD-3 + slice PD-12) — RED
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        blocked = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", WRITER_OBJECTIVE,
        ])
        self.assertEqual(
            blocked.returncode, 2,
            msg=f"S3/PD-3: la construcción sin spec aprobada debe "
                f"bloquearse (rc=2): {blocked.stdout!r} "
                f"{blocked.stderr!r}")
        self.assertIn(
            PENDING_MARKER, blocked.stderr,
            msg=f"S3/PD-3+PD-12 (RED): sin la aprobación pineada de la spec "
                f"(el archivo `docs/specs/F/spec.md` aún NO existe: PD-17 lo "
                f"crea recién en su paso 3), prepare --role test-writer debe "
                f"emitir rc=2 con el marcador {PENDING_MARKER!r} en stderr; "
                f"hoy emite el error genérico «cannot read contract» sin el "
                f"marcador (defecto reportado): {blocked.stderr!r}")
        self.assertRegex(
            blocked.stderr, PENDING_TOKENS_RE,
            msg=f"S3/PD-3: el diagnóstico no nombra el registro faltante "
                f"(stage_history/specification/approved): "
                f"{blocked.stderr!r}")
        self.assertIn(
            SPEC_FILE, blocked.stderr,
            msg=f"S3/PD-3: el diagnóstico no nombra la ruta de la spec: "
                f"{blocked.stderr!r}")
        self.assert_no_effects(
            "S3 (sin paquete nuevo en disco, construcción bloqueada)",
            root, before, state_before, blocked)

        # --------------------------------- S4 (PD-17 paso 3: PD-5/INV-2)
        (root / SPEC_FILE).parent.mkdir(parents=True, exist_ok=True)
        (root / SPEC_FILE).write_bytes(SPEC_BYTES)
        self.assert_precondition(
            "S4", spec_sha_of(root) == SPEC_SHA256,
            "sha del archivo de la spec creado")
        state = read_state(root)
        state["stage_history"].append({
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": APPROVER,
            "approved_at": "2026-10-08T00:00:00Z",
            "contract_path": SPEC_FILE,
            "contract_sha256": SPEC_SHA256,
        })
        write_state(root, state)
        prepare_writer = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", WRITER_OBJECTIVE,
        ])
        self.assertEqual(
            prepare_writer.returncode, 0,
            msg=f"S4/PD-5: la aprobación pineada (path+sha) debe habilitar a "
                f"test-writer: {prepare_writer.stdout!r} "
                f"{prepare_writer.stderr!r}")
        self.assertTrue(
            prepare_writer.stdout.startswith(PACKET_BEGIN),
            msg="S4/PD-5: stdout sin paquete canónico")
        state = read_state(root)
        p1_id = state["active_packet"]["id"]
        self.assertEqual(
            state["active_packet"].get("status"), "prepared",
            msg=f"S4: el paquete P1 no quedó `prepared` (debe quedar "
                f"PREPARADO y NO despachado): {state['active_packet']!r}")
        self.assertNotEqual(
            p1_id, architect_id,
            msg=f"S4: el paquete del test-writer reutilizó el id del "
                f"architect: {p1_id!r}")
        p1_request = request_of(root, p1_id)
        self.assertEqual(
            (p1_request.get("contract") or {}).get("kind"),
            "approved-feature-spec",
            msg=f"S4: el contrato del paquete P1: "
                f"{p1_request.get('contract')!r}")
        self.assertEqual(
            (p1_request.get("contract") or {}).get("path"), SPEC_FILE,
            msg=f"S4: el contrato del paquete P1 no nombra la spec: "
                f"{p1_request.get('contract')!r}")
        self.assertEqual(
            (p1_request.get("contract") or {}).get("sha256"), SPEC_SHA256,
            msg=f"S4: el sha del contrato de P1 no es el sha aprobado: "
                f"{p1_request.get('contract')!r}")
        self.assertEqual(
            prepare_writer.stdout,
            packet_bytes(root, p1_id, "PACKET.md").decode("utf-8"),
            msg="S4: PACKET.md de P1 difiere del stdout de prepare")
        p1_request_bytes = packet_bytes(root, p1_id, "REQUEST.json")
        p1_packet_bytes = packet_bytes(root, p1_id, "PACKET.md")

        # ------------------------- S5 (PD-17 pasos 4-5 ampliados por el
        # objetivo T4: obsolescencia y reemplazo sobre P1)
        # Elección del paquete (declarada): P1 — el del architect quedó
        # `completed` (excluido por el negativo del paso 6) y P1 es el
        # único paquete `prepared`/activo, con contrato pineado que se
        # reaprueba legítimamente tras la edición (PD-11 sin inventar
        # evidencia).
        self.assertEqual(
            read_state(root)["active_packet"].get("status"), "prepared",
            msg="S5 (precondición): el paquete a reemplazar sigue prepared")
        (root / SPEC_FILE).write_bytes(SPEC_DRIFT_BYTES)
        self.assert_precondition(
            "S5a", spec_sha_of(root) == SPEC_DRIFT_SHA256,
            "sha de la spec editada")
        self.assertEqual(
            (p1_request.get("contract") or {}).get("sha256"), SPEC_SHA256,
            msg="S5a/PD-8: el sha registrado en REQUEST.json de P1 ya no "
                "puede coincidir con el archivo")
        self.assertNotEqual(
            spec_sha_of(root), SPEC_SHA256,
            msg="S5a/PD-8a: el contrato registrado difiere del actual")
        self.assertEqual(
            read_state(root)["stage_history"][-1]["contract_sha256"],
            SPEC_SHA256,
            msg="S5a (fixture): el pin sigue en los bytes aprobados; "
                "Pablo/orquestador registra aprobaciones, no el CLI (INV-2)")

        # (b) PD-16: resume de un paquete obsoleto → marcador + acción.
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        resume = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--resume-packet", p1_id,
        ])
        self.assertEqual(
            resume.returncode, 2,
            msg=f"S5b/PD-16: el resume de un paquete con contrato derivado "
                f"debe rechazar: {resume.stdout!r} {resume.stderr!r}")
        self.assertEqual(
            resume.stdout, "", msg="S5b/PD-16: stdout no vacío")
        self.assertNotIn(
            "Traceback", resume.stderr,
            msg=f"S5b/PD-16: fallo con traceback: {resume.stderr!r}")
        self.assertIn(
            OBSOLETE_MARKER, resume.stderr,
            msg=f"S5b/PD-16: stderr sin el marcador {OBSOLETE_MARKER!r}: "
                f"{resume.stderr!r}")
        self.assertIn(
            SPEC_SHA256, resume.stderr,
            msg=f"S5b/PD-16: el diagnóstico no nombra el valor REGISTRADO "
                f"({SPEC_SHA256[:12]}…): {resume.stderr!r}")
        self.assertIn(
            SPEC_DRIFT_SHA256, resume.stderr,
            msg=f"S5b/PD-16: el diagnóstico no nombra el valor ACTUAL "
                f"({SPEC_DRIFT_SHA256[:12]}…): {resume.stderr!r}")
        self.assertRegex(
            resume.stderr, REPLACE_PACKET_RE,
            msg=f"S5b/PD-16 (prepared): el diagnóstico no señala "
                f"--replace-packet como acción legítima: {resume.stderr!r}")
        self.assertNotIn(
            PENDING_MARKER, resume.stdout + resume.stderr,
            msg=f"S5b/PD-12: el marcador {OBSOLETE_MARKER!r} se mezcló con "
                f"{PENDING_MARKER!r}: {resume.stdout + resume.stderr!r}")
        self.assert_no_effects("S5b (resume sin efectos)",
                               root, before, state_before, resume)

        # (c1) PD-11: el reemplazo NO inventa autorización.
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        replace_unauthorized = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--replace-packet", p1_id, "--reason", REASON,
        ])
        self.assertEqual(
            replace_unauthorized.returncode, 2,
            msg=f"S5c/PD-11: el reemplazo con el contrato nuevo NO aprobado "
                f"debe rechazar: {replace_unauthorized.stdout!r} "
                f"{replace_unauthorized.stderr!r}")
        self.assertIn(
            PENDING_MARKER, replace_unauthorized.stderr,
            msg=f"S5c/PD-11: stderr sin el marcador {PENDING_MARKER!r}: "
                f"{replace_unauthorized.stderr!r}")
        self.assertIn(
            SPEC_FILE, replace_unauthorized.stderr,
            msg=f"S5c/PD-11: el diagnóstico no nombra la spec concreta: "
                f"{replace_unauthorized.stderr!r}")
        self.assert_no_effects(
            "S5c1 (reemplazo rechazado sin inventar evidencia; P1 intacto)",
            root, before, state_before, replace_unauthorized)
        for name, expected in (("REQUEST.json", p1_request_bytes),
                               ("PACKET.md", p1_packet_bytes)):
            self.assertEqual(
                packet_bytes(root, p1_id, name), expected,
                msg=f"S5c1: {name} de P1 cambió durante el rechazo")
        self.assertFalse(
            (packet_dir(root, p1_id) / SUPERSEDED_FILE).is_file(),
            msg="S5c1: el rechazo dejó un registro de superación")

        # (c2) El orquestador re-registra la aprobación pineada del
        # contrato nuevo (misma ruta; solo deriva el sha — INV-2).
        state = read_state(root)
        re_pinned = False
        for entry in state["stage_history"]:
            if (entry.get("feature") == FEATURE_ID
                    and entry.get("stage") == "specification"):
                entry["contract_sha256"] = SPEC_DRIFT_SHA256
                re_pinned = True
        self.assert_precondition(
            "S5c2", re_pinned,
            "no hay entrada specification que re-registrar")
        write_state(root, state)
        # Baseline para INV-2 DESPUÉS del re-pin legítimo del orquestador.
        state_pre = read_state(root)
        packets_pre = packet_ids(root)

        # (c3) PD-7/PD-19/PD-24/INV-2/INV-3/INV-5: reemplazo exitoso.
        replace_ok = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--replace-packet", p1_id, "--reason", REASON,
        ])
        out = replace_ok.stdout + replace_ok.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"S5c3: la superficie --replace-packet/--reason debe "
                f"reconocerse: {out!r}")
        self.assertEqual(
            replace_ok.returncode, 0,
            msg=f"S5c3/PD-7: el reemplazo de P1 (prepared, obsolescencia "
                f"verificada, autorización re-registrada) debe tener éxito: "
                f"{out!r}")
        self.assertTrue(
            replace_ok.stdout.startswith(PACKET_BEGIN),
            msg="S5c3/PD-7: stdout sin paquete canónico")
        self.assertEqual(
            packet_bytes(root, p1_id, "REQUEST.json"), p1_request_bytes,
            msg="S5c3/INV-3: REQUEST.json de P1 cambió")
        self.assertEqual(
            packet_bytes(root, p1_id, "PACKET.md"), p1_packet_bytes,
            msg="S5c3/INV-3: PACKET.md de P1 cambió")
        packets_after = packet_ids(root)
        self.assertIn(
            p1_id, packets_after,
            msg="S5c3/INV-3: el paquete anterior desapareció del disco")
        successors = [p for p in packets_after
                      if p not in (architect_id, p1_id)]
        self.assertEqual(
            successors, [f"{p1_id[:-3]}{int(p1_id[-3:]) + 1:03d}"],
            msg=f"S5c3/PD-7: ids tras el reemplazo: {packets_after} "
                f"(baseline: {packets_pre})")
        p2_id = successors[0]
        # .superseded.json: motivo + traza de conservación/cambio (PD-24).
        superseded_path = packet_dir(root, p1_id) / SUPERSEDED_FILE
        self.assertTrue(
            superseded_path.is_file(),
            msg=f"S5c3/PD-7: no quedó {SUPERSEDED_FILE} en el paquete "
                f"anterior")
        record = json.loads(superseded_path.read_text(encoding="utf-8"))
        self.assertEqual(
            record.get("superseded_by"), p2_id,
            msg=f"S5c3: superseded_by: {record!r}")
        self.assertEqual(
            record.get("reason"), REASON,
            msg=f"S5c3: reason: {record!r}")
        self.assertTrue(
            record.get("superseded_at"),
            msg=f"S5c3: superseded_at vacío: {record!r}")
        self.assertEqual(
            record.get("contract_sha256_old"), SPEC_SHA256,
            msg=f"S5c3: contract_sha256_old: {record!r}")
        self.assertEqual(
            record.get("contract_sha256_new"), SPEC_DRIFT_SHA256,
            msg=f"S5c3: contract_sha256_new: {record!r}")
        conserved = set(record.get("conserved_fields") or [])
        changed = set(record.get("changed_fields") or [])
        self.assertFalse(
            conserved & changed,
            msg=f"S5c3/PD-24: conserved_fields y changed_fields no son "
                f"disjuntos: {record!r}")
        self.assertEqual(
            conserved | changed, set(ASSIGNMENT_FIELDS),
            msg=f"S5c3/PD-24: la unión de conserved_fields y changed_fields "
                f"debe ser el universo del encargo: {record!r}")
        self.assertEqual(
            changed, set(),
            msg=f"S5c3/PD-24: sin opciones de corrección no hay campo "
                f"cambiado: {record!r}")
        self.assertEqual(
            conserved, set(ASSIGNMENT_FIELDS),
            msg=f"S5c3/PD-24: sin opciones de corrección se conserva el "
                f"encargo completo: {record!r}")
        # INV-2: el reemplazo no crea ni modifica aprobaciones.
        state_after = read_state(root)
        self.assertEqual(
            state_after.get("stage_history"), state_pre.get("stage_history"),
            msg="S5c3/INV-2: stage_history cambió con el reemplazo")
        self.assertEqual(
            state_after.get("epic_history"), state_pre.get("epic_history"),
            msg="S5c3/INV-2: epic_history cambió con el reemplazo")
        active = state_after.get("active_packet") or {}
        self.assertEqual(
            active.get("id"), p2_id,
            msg=f"S5c3/PD-7: active_packet no apunta al paquete nuevo: "
                f"{active!r}")
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"S5c3/PD-7: el paquete nuevo no quedó `prepared`: {active!r}")
        self.assertEqual(
            active.get("contract_sha256"), SPEC_DRIFT_SHA256,
            msg=f"S5c3/PD-7: active_packet no lleva el contrato del día: "
                f"{active!r}")
        self.assertEqual(
            state_after.get("execution"), state_pre.get("execution"),
            msg="S5c3: la identidad de ejecución cambió con el reemplazo")
        # PD-19: el paquete nuevo conserva el encargo anterior campo a
        # campo (las diez llaves del universo cerrado).
        p2_request = request_of(root, p2_id)
        for field in ASSIGNMENT_FIELDS:
            self.assertEqual(
                p2_request.get(field), p1_request.get(field),
                msg=f"S5c3/PD-19: el campo {field!r} del encargo no fue "
                    f"conservado en el paquete nuevo")
        self.assertEqual(
            (p2_request.get("contract") or {}).get("sha256"),
            SPEC_DRIFT_SHA256,
            msg=f"S5c3: el contrato del paquete nuevo no fue re-resuelto al "
                f"contrato actual ({SPEC_DRIFT_SHA256[:12]}…)")
        self.assertEqual(
            (p2_request.get("contract") or {}).get("path"), SPEC_FILE,
            msg=f"S5c3: el contrato del paquete nuevo no nombra la spec: "
                f"{p2_request.get('contract')!r}")
        self.assertEqual(
            replace_ok.stdout,
            packet_bytes(root, p2_id, "PACKET.md").decode("utf-8"),
            msg="S5c3/INV-5: stdout difiere del PACKET.md publicado")

        # ------------------------------- S6a (negativo: paquete completed)
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        replace_completed = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--replace-packet", architect_id, "--reason",
            "negativo: el paquete del architect ya se recibió (completed)",
        ])
        self.assertIn(
            architect_id, replace_completed.stderr,
            msg=f"S6a: el diagnóstico no nombra el paquete objetivo: "
                f"{replace_completed.stderr!r}")
        self.assert_no_effects(
            "S6a (reemplazo del paquete del architect `completed` rechazado "
            "sin efectos)", root, before, state_before, replace_completed)

        # ------------------- S6b (negativo PD-8: sin obsolescencia real)
        self.assertEqual(
            read_state(root)["active_packet"].get("status"), "prepared",
            msg="S6b (precondición): el paquete nuevo sigue prepared")
        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        replace_clean = run_packet_cli([
            "prepare", "--project-root", str(root),
            "--replace-packet", p2_id, "--reason",
            "negativo: no hay obsolescencia verificable",
        ])
        self.assertEqual(
            spec_sha_of(root),
            (request_of(root, p2_id).get("contract") or {}).get("sha256"),
            msg="S6b (precondición): el contrato de P2 coincide con el "
                "archivo del día (no hay drift)")
        self.assert_no_effects(
            "S6b (reemplazo sin obsolescencia verificable rechazado sin "
            "efectos, PD-8)", root, before, state_before, replace_clean)


if __name__ == "__main__":
    unittest.main(verbosity=2)
