#!/usr/bin/env python3
"""005-001 T2 RED — Reemplazo de paquete preparado no despachado y
diagnósticos de obsolescencia (PD-7..PD-11, PD-16; slice PD-12).

Contract:
- docs/specs/005-001-idle-and-v7-bootstrap/spec.md §2 (PD-7..PD-11, PD-16;
  slice PD-12 de la condición `packet obsolete`).
- docs/specs/005-001-idle-and-v7-bootstrap/plan.md (T2; test focal declarado
  `tests/test_005_001_t2_replace_packet.py`).

Superficie observable bajo prueba (§2; sub-modo D4 con argv PURO, sin
opciones ordinarias — identidad/rol/subfase/objetivo se reusan del
REQUEST.json anterior):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --replace-packet <packet-id> --reason <texto>   # NUEVO sub-modo
    python3 scripts/cdad_packet.py prepare --project-root R \
        --resume-packet <packet-id>                     # I11 vigente
    python3 scripts/cdad_packet.py prepare --project-root R \
        --record-dispatch <id> --attempt-id <a> --input <obs.json>  # fixture

Registros: la reautorización del contrato nuevo la SIEMBRA el fixture
escribiendo el pin en `stage_history` (el registro de aprobación es del
orquestador, no del CLI — INV-2); `--record-dispatch` (I8) es la vía
pública para llevar el paquete activo a `dispatched` (PD-10/PD-16).

Marcadores de diagnóstico (PD-12): `packet obsolete` (obsolescencia del
paquete) y `approval pending` (contrato nuevo no autorizado),
mutuamente excluyentes por condición.

RED hoy (probe sobre un proyecto sintético):
- `--replace-packet`/`--reason` NO existen en el parser (argv →
  "unrecognized arguments"); cada test preverifica la superficie
  declarada en §2 (assertNotIn "unrecognized", patrón 004-002 T4/B-1)
  y después afirma la postcondición: todo fallo RED es una
  AssertionError de comportamiento, nunca ImportError.
- PD-16: `--resume-packet` de un paquete con contrato derivado hoy fracasa
  con mensaje genérico ("contract sha256 does not match exact content"),
  sin el marcador `packet obsolete`, sin los valores registrados/actual
  y sin señalar --replace-packet/reconciliación: el RED fracasa en esas
  aserciones de diagnóstico.

Fixtures offline: proyectos sintéticos en tempdirs (política válida, spec
pineada aprobada, delegación HITL activa); ninguna escritura en este repo
y ninguna lectura de implementación. La obsolescencia se construye por
interfaz pública: editar `docs/specs/<feature>/spec.md` deriva el sha
registrado en el REQUEST.json del paquete (PD-8a) y, con re-pin del
registro `specification`, deja la autorización VIGENTE para el contrato
nuevo (PD-7/PD-10/PD-16) o NO vigente (PD-11).
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
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"

SPEC_BYTES = b"# Spec fixture (005-001 T2)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada despues de aprobar\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()
SPEC_DRIFT_SHA256 = hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest()

APPROVER = "Pablo"
OBJECTIVE = "005-001 T2 objective"
REASON = "contrato editado despues de preparar el paquete"

ROLE, SUBSTAGE = "test-writer", "red"
PACKET_BEGIN = "---cdad-packet-json"
PENDING_MARKER = "approval pending"
OBSOLETE_MARKER = "packet obsolete"
INCOHERENT_MARKER = "state incoherent"
SUPERSEDED_FILE = ".superseded.json"

REPLACE_PACKET_RE = re.compile(
    r"(?i)replace[-_ ]packet|reemplaz\w*\s+paquete")
RECONCILE_RE = re.compile(r"(?i)reconcil")


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


def run_replace(root: Path, packet_id: str,
                *, reason: str | None = REASON) -> subprocess.CompletedProcess:
    """Sub-modo §2/D4 con argv PURO (sin flags ordinarios)."""
    args = ["prepare", "--project-root", str(root),
            "--replace-packet", packet_id]
    if reason is not None:
        args += ["--reason", reason]
    return run_cli(args)


def run_resume(root: Path, packet_id: str) -> subprocess.CompletedProcess:
    return run_cli([
        "prepare", "--project-root", str(root),
        "--resume-packet", packet_id,
    ])


def run_record_dispatch(root: Path, packet_id: str, attempt_id: str,
                        input_path: Path) -> subprocess.CompletedProcess:
    return run_cli([
        "prepare", "--project-root", str(root),
        "--record-dispatch", packet_id, "--attempt-id", attempt_id,
        "--input", str(input_path),
    ])


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


def registered_contract_sha(root: Path, packet_id: str) -> str:
    return request_of(root, packet_id)["contract"]["sha256"]


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


def spec_approval_entry(spec_sha: str) -> dict:
    """Entrada pineada de especificación (D3: path + sha256 obligatorios)."""
    return {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": APPROVER,
        "approved_at": "2026-10-08T00:00:00Z",
        "contract_path": SPEC_FILE,
        "contract_sha256": spec_sha,
    }


def build_project(root: Path) -> Path:
    """Proyecto sintético válido para T2 (política + spec pineada +
    fuente de autoridad + delegación HITL activa)."""
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
    state = {
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
        "stage_history": [spec_approval_entry(SPEC_SHA256)],
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
    """Documento de observación I8 (claves cerradas, cinco campos +
    provenance) para el registro de despacho del fixture."""
    return {
        "runtime": "opencode",
        "model_configured": "glm-5.3-flash",
        "model_reported": "glm-5.3-flash",
        "session": "ses-005-001-t2-0001",
        "started_at": "2026-10-08T00:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }


def outdate_contract(root: Path, packet_id: str, *,
                     reauthorize: bool) -> tuple[str, str]:
    """Obsolescencia PD-8(a) por interfaz pública: edita la spec (los bytes
    derivan del sha registrado en el REQUEST.json del paquete) y, si
    `reauthorize`, re-pinea la entrada `specification` al sha ACTUAL
    (el orquestador registra aprobaciones — INV-2). Devuelve (registrado,
    actual)."""
    stale = (root / SPEC_FILE).read_bytes()
    if stale == SPEC_DRIFT_BYTES:
        raise AssertionError("fixture: la spec ya estaba derivada")
    (root / SPEC_FILE).write_bytes(SPEC_DRIFT_BYTES)
    if reauthorize:
        state = read_state(root)
        re_pinned = False
        for entry in state.get("stage_history", []):
            if (entry.get("feature") == FEATURE_ID
                    and entry.get("stage") == "specification"):
                entry["contract_sha256"] = SPEC_DRIFT_SHA256
                re_pinned = True
        if not re_pinned:
            raise AssertionError(
                "fixture: no hay entrada `specification` que re-pinear")
        write_state(root, state)
    registered = registered_contract_sha(root, packet_id)
    if registered != SPEC_SHA256:
        raise AssertionError(
            f"fixture: el sha registrado en REQUEST.json no es el de los "
            f"bytes aprobados: {registered[:12]}… != {SPEC_SHA256[:12]}…")
    return registered, SPEC_DRIFT_SHA256


class T2Case(unittest.TestCase):
    """Base: proyecto sintético en tempdir propio por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-001-t2-")
        self.addCleanup(subprocess.run,
                        ["rm", "-rf", self._tmp], check=False)

    def make_project(self) -> Path:
        return build_project(Path(self._tmp) / "proj")

    def prepared_packet(self) -> tuple[Path, str]:
        """Fixture precondición (PD-5/T1 vigente): política + spec pineada
        → `prepare` habilita y deja el paquete activo `prepared`.
        Devuelve (root, packet_id)."""
        root = self.make_project()
        proc = prepare(root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): la aprobación pineada vigente "
                f"debe habilitar prepare (PD-5): "
                f"{proc.stdout!r} {proc.stderr!r}")
        active = read_state(root)["active_packet"]
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"precondición (fixture): paquete activo: {active!r}")
        return root, active["id"]

    def dispatch_prepared_packet(self, root: Path, packet_id: str,
                                 attempt_id: str) -> None:
        """Fixture precondición `dispatched` por vía pública (I8):
        `--record-dispatch` con documento de observación de claves
        cerradas; deja `active_packet.status == "dispatched"`."""
        obs = root / "docs" / "dispatch-observation.json"
        obs.parent.mkdir(parents=True, exist_ok=True)
        obs.write_text(
            json.dumps(observation_document(), indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        proc = run_record_dispatch(root, packet_id, attempt_id, obs)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): --record-dispatch debe registrar "
                f"el intento: {proc.stdout!r} {proc.stderr!r}")
        self.assertEqual(
            read_state(root)["active_packet"].get("status"), "dispatched",
            msg="precondición (fixture): el paquete quedó dispatched (I8)")

    def assert_no_writes(self, label: str, root: Path, before: dict,
                         state_before: bytes) -> None:
        """Ninguna publicación ni escritura: árbol y state byte a byte
        idénticos, y ningún `.superseded.json`."""
        self.assertEqual(
            tree_snapshot(root), before,
            msg=f"{label}: hubo escrituras (árbol modificado)")
        self.assertEqual(
            state_bytes(root), state_before,
            msg=f"{label}: el state cambió")
        for pid in packet_ids(root):
            self.assertFalse(
                (packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
                msg=f"{label}: quedó un registro de superación con rc≠0 "
                    f"({SUPERSEDED_FILE} en {pid})")

    def assert_rejection(self, label: str, root: Path, before: dict,
                         state_before: bytes,
                         proc: subprocess.CompletedProcess, *,
                         marker: str | None = None,
                         forbidden_markers: tuple[str, ...] = ()) -> None:
        """Rechazo §2: rc=2, stdout vacío, sin traceback, con el marcador
        pedido (y sin los excluidos), sin efectos (PD-8/PD-9/PD-10/PD-11
        «sin efectos»; PD-12 «no altera el state ni publica archivos»)."""
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"{label}: la superficie declarada en spec §2 "
                f"(--replace-packet/--reason) debe reconocerse; hoy el "
                f"parser no la conoce: {out!r}")
        self.assertEqual(
            proc.returncode, 2,
            msg=f"{label}: rc esperado 2: {out!r}")
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
                msg=f"{label}: el marcador {marker!r} se mezcló con el "
                    f"marcador {banned!r} (PD-12: exclusivos por "
                    f"condición): {out!r}")
        self.assert_no_writes(label, root, before, state_before)


# ---------------------------------------------------------------- PD-7


class TestPd7ReplacePreparedPacket(T2Case):
    """PD-7: con `active_packet.id == <id>`, `status == "prepared"` y
    obsolescencia verificada (PD-8a) y el contrato del día AUTORIZADO (pin
    re-registrado), `prepare --replace-packet <id> --reason "<texto>"` →
    rc=0: paquete nuevo (id siguiente libre) con el contrato actual y la
    autorización vigente; `active_packet` apunta al nuevo con
    `status: "prepared"`; REQUEST.json/PACKET.md del anterior byte a byte
    idénticos (INV-3); `.superseded.json` durable en el directorio del
    anterior con `{superseded_by, reason, superseded_at,
    contract_sha256_old, contract_sha256_new}`; sin entradas creadas ni
    modificadas en `stage_history`/`epic_history` (INV-2)."""

    def test_pd7_replace_publishes_successor_superseded_record_keeps_old_bytes(self) -> None:
        root, pid = self.prepared_packet()
        old_packet_md = packet_bytes(root, pid, "PACKET.md")
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_request = json.loads(old_request_bytes.decode("utf-8"))

        # Obsolescencia genuina (a) + autorización vigente del contrato nuevo.
        # (El re-pin de `specification` en stage_history es la autorización
        # legítima del registro del orquestador — INV-2 lo exige —, no un
        # efecto del CLI.)
        registered, current = outdate_contract(root, pid, reauthorize=True)

        # Snapshot INV-2 DESPUÉS del re-pin legítimo del fixture: el baseline
        # debe ser el estado ya sembrado por el orquestador antes de invocar
        # el CLI, no el estado previo al re-pin.
        state_pre = read_state(root)

        proc = run_replace(root, pid)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg="PD-7: la superficie declarada en spec §2 "
                "(--replace-packet/--reason) debe reconocerse; hoy el "
                f"parser no la conoce: {out!r}")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-7: el reemplazo del paquete prepared con obsolescencia "
                f"verificada y autorización vigente debe tener éxito: "
                f"{out!r}")
        self.assertTrue(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="PD-7: stdout no comienza con el paquete canónico")

        # Paquete NUEVO publicado; el anterior no se borra ni reescribe.
        packets_after = packet_ids(root)
        self.assertIn(
            pid, packets_after,
            msg="PD-7/INV-3: el paquete anterior desapareció del disco")
        successors = [p for p in packets_after if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-7: paquetes en disco tras el reemplazo: {packets_after}")
        new_id = successors[0]
        match_old = re.match(r"^(.*-)(\d{3})$", pid)
        self.assertIsNotNone(
            match_old, msg=f"fixture: esquema de id inesperado: {pid!r}")
        expected_next = f"{match_old.group(1)}{int(match_old.group(2)) + 1:03d}"
        self.assertEqual(
            new_id, expected_next,
            msg=f"PD-7: se esperaba publicar el id siguiente libre "
                f"({expected_next!r}) y se publicó {new_id!r}")
        # INV-3: bytes del paquete anterior intactos.
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-7/INV-3: PACKET.md del paquete anterior cambió")
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-7/INV-3: REQUEST.json del paquete anterior cambió")

        # active_packet apunta al nuevo, `prepared`, identidad reusada (D4).
        state_after = read_state(root)
        active = state_after.get("active_packet") or {}
        self.assertEqual(
            active.get("id"), new_id,
            msg=f"PD-7: state.active_packet no apunta al paquete nuevo: "
                f"{active!r}")
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"PD-7: el paquete nuevo no quedó `prepared`: {active!r}")
        self.assertEqual(
            active.get("role"), ROLE,
            msg=f"PD-7: identidad D4 no reusada (role): {active!r}")
        self.assertEqual(
            active.get("substage"), SUBSTAGE,
            msg=f"PD-7: identidad D4 no reusada (substage): {active!r}")
        self.assertEqual(
            active.get("contract_sha256"), current,
            msg=f"PD-7: active_packet no lleva el contrato del día "
                f"({current[:12]}…): {active!r}")
        self.assertEqual(
            state_after.get("execution"), state_pre.get("execution"),
            msg="PD-7: la identidad de ejecución cambió con el reemplazo")
        new_request = request_of(root, new_id)
        self.assertEqual(
            new_request.get("execution_id"), old_request.get("execution_id"),
            msg="PD-7/D4: el paquete nuevo no reusa execution_id")
        self.assertEqual(
            new_request.get("role"), ROLE,
            msg="PD-7/D4: el paquete nuevo no reusa role")
        self.assertEqual(
            new_request.get("substage"), SUBSTAGE,
            msg="PD-7/D4: el paquete nuevo no reusa substage")
        self.assertEqual(
            new_request.get("objective"), old_request.get("objective"),
            msg="PD-7/D4: el paquete nuevo no reusa objective")

        # Contrato actual (el re-resuelto del día) y autorización vigente.
        self.assertEqual(
            new_request.get("contract", {}).get("sha256"), current,
            msg=f"PD-7: el paquete nuevo no lleva el contrato actual "
                f"({current[:12]}…): "
                f"{json.dumps(new_request.get('contract'))!r}")
        self.assertEqual(
            new_request.get("contract", {}).get("path"), SPEC_FILE,
            msg="PD-7: el paquete nuevo no lleva la ruta del contrato")

        # Registro durable de superación en el directorio del anterior.
        superseded_path = packet_dir(root, pid) / SUPERSEDED_FILE
        self.assertTrue(
            superseded_path.is_file(),
            msg=f"PD-7: no quedó registro durable {SUPERSEDED_FILE} en el "
                f"paquete anterior")
        record = json.loads(superseded_path.read_text(encoding="utf-8"))
        self.assertEqual(
            record.get("superseded_by"), new_id,
            msg=f"PD-7: superseded_by no nombra al paquete nuevo "
                f"({new_id!r}): {record!r}")
        self.assertEqual(
            record.get("reason"), REASON,
            msg=f"PD-7: reason no es el motivo de --reason ({REASON!r}): "
                f"{record!r}")
        self.assertTrue(
            record.get("superseded_at"),
            msg=f"PD-7: superseded_at vacío: {record!r}")
        self.assertEqual(
            record.get("contract_sha256_old"), registered,
            msg=f"PD-7: contract_sha256_old no es el sha registrado "
                f"({registered[:12]}…): {record!r}")
        self.assertEqual(
            record.get("contract_sha256_new"), current,
            msg=f"PD-7: contract_sha256_new no es el sha actual "
                f"({current[:12]}…): {record!r}")

        # INV-2: ninguna entrada de stage_history/epic_history creada ni
        # modificada por el reemplazo.
        self.assertEqual(
            state_after.get("stage_history"), state_pre.get("stage_history"),
            msg="PD-7/INV-2: stage_history cambió con el reemplazo")
        self.assertEqual(
            state_after.get("epic_history"), state_pre.get("epic_history"),
            msg="PD-7/INV-2: epic_history cambió con el reemplazo")

        # INV-5: stdout == los bytes del nuevo PACKET.md publicado
        # (el paquete impreso es el mismo que quedó en disco).
        self.assertEqual(
            proc.stdout,
            packet_bytes(root, new_id, "PACKET.md").decode("utf-8"),
            msg="PD-7/INV-5: stdout difiere del PACKET.md publicado")


# ---------------------------------------------------------------- PD-8


class TestPd8ReplaceOnlyUnderGenuineObsolescence(T2Case):
    """PD-8: `--replace-packet` se acepta SOLO con obsolescencia verificable
    (sha del contrato registrado ≠ actual, o revisión de política ≠
    aceptada I11). Sin obsolescencia → rc=2, sin efectos (no es un atajo
    para saltar PD-4). Control positivo: PD-7 (obsolescencia (a) habilita)."""

    def test_pd8_replace_without_obsolescence_rejected_without_effects(self) -> None:
        # El paquete es íntegro respecto al contrato del día y la política
        # no cambió desde el render: no hay obsolescencia verificable.
        root, pid = self.prepared_packet()
        self.assertEqual(
            registered_contract_sha(root, pid), SPEC_SHA256,
            msg="fixture (control): el contrato del paquete sigue íntegro")
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_replace(root, pid)
        self.assert_rejection("PD-8", root, before, state_before, proc)


# ---------------------------------------------------------------- PD-9


class TestPd9ReplaceRequiresReason(T2Case):
    """PD-9: `--replace-packet` sin `--reason` no vacío → rc=2, sin efectos;
    `--reason` sin `--replace-packet` → rc=2."""

    def test_pd9_replace_requires_non_empty_reason_and_reason_alone_rejected(self) -> None:
        root, pid = self.prepared_packet()
        cases = (
            ("sin --reason", lambda: run_replace(root, pid, reason=None)),
            ("--reason vacio", lambda: run_replace(root, pid, reason="")),
            ("--reason sin --replace-packet",
             lambda: run_cli(["prepare", "--project-root", str(root),
                              "--reason", REASON])),
        )
        for label, call in cases:
            with self.subTest(caso=label):
                before = tree_snapshot(root)
                state_before = state_bytes(root)
                proc = call()
                self.assert_rejection(
                    f"PD-9 ({label})", root, before, state_before, proc)


# ---------------------------------------------------------------- PD-10


class TestPd10DispatchedPacketNotReplaced(T2Case):
    """PD-10: con `status == "dispatched"`, `--replace-packet` → rc=2, marcador
    `packet obsolete`, mensaje que nombra la reconciliación requerida; sin
    efectos. Precondición fuerte por vía pública (I8): el paquete se
    despachó con `--record-dispatch`; después el contrato derivó (a) y el
    contrato nuevo quedó AUTORIZADO (pin re-registrado) — lo único que
    bloquea sigue siendo el despacho."""


    def test_pd10_dispatched_packet_rejected_with_reconciliation_action(self) -> None:
        root, pid = self.prepared_packet()
        self.dispatch_prepared_packet(root, pid, "att-t2-pd10")
        outdate_contract(root, pid, reauthorize=True)
        self.assertEqual(
            read_state(root)["active_packet"].get("status"), "dispatched",
            msg="fixture: el paquete sigue dispatched antes del reemplazo")
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_replace(root, pid)
        self.assert_rejection(
            "PD-10", root, before, state_before, proc,
            marker=OBSOLETE_MARKER, forbidden_markers=(PENDING_MARKER,))
        self.assertRegex(
            proc.stderr, RECONCILE_RE,
            msg=f"PD-10: el diagnóstico no nombra la reconciliación "
                f"requerida: {proc.stderr!r}")


# ---------------------------------------------------------------- PD-11


class TestPd11ReplaceDoesNotInventAuthorization(T2Case):
    """PD-11: si el contrato ACTUAL no está autorizado (la spec cambió y el
    pin registrado ya no coincide), `--replace-packet` → rc=2 `approval
    pending`; no se publica paquete nuevo; el paquete viejo queda intacto
    (recuperación sin inventar evidencia)."""


    def test_pd11_unauthorized_new_contract_rejected_old_packet_intact(self) -> None:
        root, pid = self.prepared_packet()
        # El contrato deriva pero NO hay re-pin: el contrato del día NO
        # está autorizado (la entrada pineada quedó en el sha viejo).
        outdate_contract(root, pid, reauthorize=False)
        state = read_state(root)
        self.assertEqual(
            state["stage_history"][-1]["contract_sha256"], SPEC_SHA256,
            msg="fixture: el pin sigue en los bytes aprobados (Pablo, no el "
                "CLI, registra aprobaciones — INV-2)")
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_replace(root, pid)
        self.assert_rejection(
            "PD-11", root, before, state_before, proc,
            marker=PENDING_MARKER, forbidden_markers=(OBSOLETE_MARKER,))
        self.assertIn(
            SPEC_FILE, proc.stderr,
            msg=f"PD-11: el diagnóstico no nombra la spec concreta: "
                f"{proc.stderr!r}")


# ---------------------------------------------------------------- PD-16


class TestPd16ResumeObsoleteFailsWithMarker(T2Case):
    """PD-16: `prepare --resume-packet <id>` sobre un paquete cuyo contrato
    (o revisión de política) cambió → rc=2, marcador `packet obsolete`,
    nombrando el valor REGISTRADO y el ACTUAL; si `status == prepared`
    señala `--replace-packet`; si `dispatched`, señala reconciliación
    (I11 vigente). El contrato del día queda AUTORIZADO (re-pin) para
    aislar la obsolescencia del paquete de la falta de aprobación."""


    def test_pd16_resume_prepared_obsolete_names_registered_current_and_replace(self) -> None:
        root, pid = self.prepared_packet()
        registered, current = outdate_contract(root, pid, reauthorize=True)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_resume(root, pid)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"PD-16: la superficie --resume-packet debe seguir "
                f"reconociéndose: {out!r}")
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-16: el resume de un paquete con contrato derivado debe "
                f"rechazar: {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-16: el rechazo imprimió contenido por stdout")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"PD-16: fallo con traceback: {proc.stderr!r}")
        self.assertIn(
            OBSOLETE_MARKER, proc.stderr,
            msg=f"PD-16: stderr sin el marcador {OBSOLETE_MARKER!r} "
                f"(hoy: mensaje genérico sin marcador): {proc.stderr!r}")
        self.assertIn(
            registered, proc.stderr,
            msg=f"PD-16: el diagnóstico no nombra el valor registrado "
                f"({registered[:12]}…): {proc.stderr!r}")
        self.assertIn(
            current, proc.stderr,
            msg=f"PD-16: el diagnóstico no nombra el valor actual "
                f"({current[:12]}…): {proc.stderr!r}")
        self.assertRegex(
            proc.stderr, REPLACE_PACKET_RE,
            msg=f"PD-16 (prepared): el diagnóstico no señala "
                f"--replace-packet como acción legítima: {proc.stderr!r}")
        self.assert_no_writes("PD-16", root, before, state_before)

    def test_pd16_resume_dispatched_obsolete_names_reconciliation(self) -> None:
        root, pid = self.prepared_packet()
        self.dispatch_prepared_packet(root, pid, "att-t2-pd16d")
        registered, current = outdate_contract(root, pid, reauthorize=True)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_resume(root, pid)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"PD-16: la superficie --resume-packet debe seguir "
                f"reconociéndose: {out!r}")
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-16: el resume de un paquete dispatched con contrato "
                f"derivado debe rechazar: {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-16: el rechazo imprimió contenido por stdout")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"PD-16: fallo con traceback: {proc.stderr!r}")
        self.assertIn(
            OBSOLETE_MARKER, proc.stderr,
            msg=f"PD-16: stderr sin el marcador {OBSOLETE_MARKER!r}: "
                f"{proc.stderr!r}")
        self.assertIn(
            registered, proc.stderr,
            msg=f"PD-16: el diagnóstico no nombra el valor registrado "
                f"({registered[:12]}…): {proc.stderr!r}")
        self.assertIn(
            current, proc.stderr,
            msg=f"PD-16: el diagnóstico no nombra el valor actual "
                f"({current[:12]}…): {proc.stderr!r}")
        self.assertRegex(
            proc.stderr, RECONCILE_RE,
            msg=f"PD-16 (dispatched): el diagnóstico no señala la "
                f"reconciliación como acción legítima: {proc.stderr!r}")
        self.assert_no_writes("PD-16", root, before, state_before)


# ------------------------------------------------------ PD-12 (slice T2)


class TestPd12PacketObsoleteMarker(T2Case):
    """PD-12 (slice T2, condición `paquete obsoleto`): rc=2 y el stderr
    contiene el marcador `packet obsolete`, nombra el registro concreto
    (los valores registrados en el REQUEST.json y los actuales) y la
    acción legítima siguiente (`--replace-packet`), sin alterar el state
    ni publicar archivos; los marcadores son mutuamente excluyentes por
    condición (no `approval pending`, no `state incoherent`)."""


    def test_pd12_packet_obsolete_is_distinguishable_and_actionable(self) -> None:
        root, pid = self.prepared_packet()
        registered, current = outdate_contract(root, pid, reauthorize=True)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_resume(root, pid)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"PD-12: la superficie --resume-packet debe seguir "
                f"reconociéndose: {out!r}")
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-12: rc esperado 2: {out!r}")
        self.assertIn(
            OBSOLETE_MARKER, proc.stderr,
            msg=f"PD-12: stderr sin el marcador {OBSOLETE_MARKER!r}: "
                f"{proc.stderr!r}")
        # Exclusividad por condición (PD-12).
        self.assertNotIn(
            PENDING_MARKER, out,
            msg=f"PD-12: el marcador {OBSOLETE_MARKER!r} se mezcló con "
                f"{PENDING_MARKER!r}: {out!r}")
        self.assertNotIn(
            INCOHERENT_MARKER, out,
            msg=f"PD-12: el marcador {OBSOLETE_MARKER!r} se mezcló con "
                f"{INCOHERENT_MARKER!r}: {out!r}")
        # Registro concreto + valores + acción legítima.
        self.assertIn(
            pid, out,
            msg=f"PD-12: el diagnóstico no nombra el paquete ({pid!r}): "
                f"{out!r}")
        self.assertIn(
            registered, proc.stderr,
            msg=f"PD-12: el diagnóstico no nombra el valor registrado "
                f"({registered[:12]}…): {proc.stderr!r}")
        self.assertIn(
            current, proc.stderr,
            msg=f"PD-12: el diagnóstico no nombra el valor actual "
                f"({current[:12]}…): {proc.stderr!r}")
        self.assertRegex(
            proc.stderr, REPLACE_PACKET_RE,
            msg=f"PD-12: el diagnóstico no señala la acción legítima "
                f"(--replace-packet): {proc.stderr!r}")
        self.assert_no_writes("PD-12", root, before, state_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
