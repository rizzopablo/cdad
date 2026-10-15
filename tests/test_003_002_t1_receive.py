#!/usr/bin/env python3
"""003-002 T1 RED — receive atómico e idempotente (P1, P2, P3, base de P6).

Contract:
- docs/specs/003-002-artifact-tools/spec.md (P1, P2, P3, P6 — base T1)
- docs/specs/003-002-artifact-tools/plan.md (T1; test focal declarado
  `tests/test_003_002_t1_receive.py`).

Superficie observable bajo prueba (§2 del contrato; nada de plomería:

    python3 scripts/cdad_result.py receive \
        --project-root ROOT \
        --execution-context EXECUTION.json \
        --packet PACKET.md \
        --request REQUEST.json \
        --descriptor RESULT.json

Destino final declarado (§5):

    PROJECT_ROOT/.cdad/runtime/results/<execution_id>/<packet_id>/
      ├── parts/<name>.utf8
      ├── bundle.json
      └── receipt.json

Fixtures offline: proyecto sintético v2 (política válida, state con
aprobación de contrato en stage_history y delegación HITL activa); paquete
test-writer/red publicado por `prepare` y observado como dispatched
(--record-dispatch, I8); staged parts bajo `.cdad/inbox`. Los proyectos son
tempdirs; ninguna escritura en este repo.

RED hoy: `scripts/cdad_result.py` no existe; cada aserción positiva fracasa
por comportamiento ausente (rc≠0/resultado final ausente según el mensaje
misma prima `scripts/cdad_result.py no existe aún`), no por ImportError.
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
RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"   # helper de 003-002 (aún inexistente)

POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
FEATURE_ID = "003-002-artifact-tools"
EPIC_ID = "epic-003-context-efficiency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture 003-002 (T1 RED)\n"

ROLE = "test-writer"
SUBSTAGE = "red"
ATTEMPT_ID = "attempt-t1-red-001"

# staged parts del fixture (§3: cada part es un archivo regular UTF-8 no vacío
# bajo el inbox fijo `.cdad/inbox`; artifact-kind por tabla del rol).
STAGED_PARTS: dict[str, bytes] = {
    "role-report": (
        b"# Role report (fixture T1 RED)\n"
        b"Evidencia mecanica del intento test-writer/red de 003-002.\n"
    ),
    "role-notes": (
        b"# Role notes (fixture T1 RED)\n"
        b"Notas auxiliares del mismo intento; se conservan bytes separados.\n"
    ),
}
PART_KINDS: dict[str, str] = {
    "role-report": "test-writer-role-report",
    "role-notes": "test-writer-notes",
}

# manifest observado (§4): paths declarados por la orquestación.
BASELINE_REF = "orchestrator-prepared-reference"
BASELINE_SHA256 = "0" * 64
IN_SCOPE_CHANGE = "tests/role_report_fixture.py"
OUT_OF_SCOPE_CHANGE = "src/leaked_implementation.py"
DESCRIPTOR_PATH = ".cdad/inbox/RESULT.json"
MANIFEST_PATH = ".cdad/inbox/changes.json"

# Tamaño límite del bundle (§3): la suma de bytes de todas las parts de un
# packet no supera 1 MiB.
BUNDLE_LIMIT_BYTES = 1024 * 1024


# ---------------------------------------------------------------- fixtures


def prepare_args(root: Path, *, role: str = ROLE, substage: str = SUBSTAGE,
                 objective: str = "T1 objective") -> list[str]:
    """Argv de `prepare` v2 de 001 sobre el proyecto sintético."""
    return [
        "prepare", "--project-root", str(root),
        "--role", role, "--substage", substage, "--objective", objective,
    ]


def run_packet_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Corrida del CLI de 001 (prepare/validate) con bytes de salida."""
    return subprocess.run(
        [sys.executable, str(PACKET_SCRIPT), *args],
        cwd=REPO_ROOT, capture_output=True,
    )


def run_result_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Corrida del CLI de 003-002 (`scripts/cdad_result.py`) con bytes."""
    return subprocess.run(
        [sys.executable, str(RESULT_SCRIPT), *args],
        cwd=REPO_ROOT, capture_output=True,
    )


def out_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stdout.decode("utf-8", errors="replace")


def err_text(proc: subprocess.CompletedProcess) -> str:
    return proc.stderr.decode("utf-8", errors="replace")


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
    """Proyecto sintético válido para `prepare` (003-002)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    # Política válida de tres campos (soportada por el runtime v2).
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


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético con el paquete dispatched y stage-ready."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-002-t1-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))

    def new_dispatched_project(self) -> None:
        """Proyecto sintético nuevo (tempdir), paquete dispatched listo."""
        tmp = tempfile.mkdtemp(prefix="cdad-003-002-t1red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.root = build_project(Path(tmp) / "proj")
        self.establish_dispatched()

    # -- oráculos de salida ------------------------------------------------

    def final_dir(self) -> Path:
        return (self.root / ".cdad" / "runtime" / "results"
                / self.execution_id / self.packet_id)

    def receipt_path(self) -> Path:
        return self.final_dir() / "receipt.json"

    def bundle_path(self) -> Path:
        return self.final_dir() / "bundle.json"

    def receipt_digest(self, receipt: dict) -> str:
        """Digest coyuntural; el bundle real se calcula en el test."""
        return hashlib.sha256(self.bundle_path().read_bytes()).hexdigest()

    def assert_part_file_matches(self, name: str, data: bytes) -> None:
        """El part persistido conserva los bytes originales (§5 layout)."""
        stored = self.final_dir() / "parts" / f"{name}.utf8"
        self.assertTrue(
            stored.is_file(),
            msg=f"P1: no se persistió el part {name!r} en {stored}")
        self.assertEqual(
            stored.read_bytes(), data,
            msg=f"P1: el part {name!r} persistido difiere de los bytes staged")

    # -- escrituras del fixture -------------------------------------------

    def write_staged_parts(self, root: Path | None = None,
                           parts: dict[str, bytes] | None = None) -> dict[str, bytes]:
        """Escribe los parts staged bajo `.cdad/inbox` del project root."""
        root = root if root is not None else self.root
        parts = parts if parts is not None else dict(STAGED_PARTS)
        inbox = root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        for name, data in parts.items():
            (inbox / f"{name}.md").write_bytes(data)
        return parts

    def write_manifest(self, root: Path | None = None,
                       *, changes: list[dict], status: str = "trusted",
                       manifest_path: str = MANIFEST_PATH) -> dict:
        """Escribe el manifest de cambios observado (§4) y devuelve el doc."""
        root = root if root is not None else self.root
        doc = {
            "schema_version": 1,
            "observation_status": status,
            "baseline_ref": BASELINE_REF,
            "baseline_sha256": BASELINE_SHA256,
            "changes": changes,
        }
        target = root / manifest_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        return doc

    def observed_changes(self, *, manifest_path: str = MANIFEST_PATH,
                         status: str = "trusted",
                         ref: str = BASELINE_REF,
                         sha: str = BASELINE_SHA256) -> dict:
        """Bloque `observed_changes` del descriptor (§3)."""
        return {
            "observation_status": status,
            "baseline_ref": ref,
            "baseline_sha256": sha,
            "manifest_path": manifest_path,
        }

    def build_descriptor(self, *, parts: dict[str, bytes],
                         observed: dict | None) -> dict:
        """RESULT.json canónico (§3) — source.kind staged-file."""
        inbox_rel = ".cdad/inbox"
        return {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [
                {"name": name,
                 "artifact_kind": PART_KINDS[name],
                 "staged_path": f"{inbox_rel}/{name}.md"}
                for name in parts
            ],
            **({"observed_changes": observed} if observed is not None else {}),
            "run_evidence_ref": None,
        }

    def write_descriptor(self, doc: dict) -> Path:
        path = self.root / DESCRIPTOR_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True)
                        + "\n", encoding="utf-8")
        return path

    # -- arranque del fixture ----------------------------------------------

    def establish_dispatched(self) -> None:
        """Prepara el paquete del fixture y lo observa como dispatched (I8)."""
        prep = run_packet_cli(prepare_args(self.root))
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
        observation_path = self.root / "docs" / "observations-t1.json"
        observation_path.write_text(json.dumps({
            "runtime": "opencode",
            "model_configured": "glm-5.3-flash",
            "model_reported": "glm-5.3-flash",
            "session": "ses-003-002-t1-red-0001",
            "started_at": "2026-10-05T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = run_packet_cli([
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

    def staged_report_data(self) -> bytes:
        return (self.root / ".cdad" / "inbox" / "role-report.md").read_bytes()

    def staged_notes_data(self) -> bytes:
        return (self.root / ".cdad" / "inbox" / "role-notes.md").read_bytes()

    def receive_args(self, descriptor: Path) -> list[str]:
        """Argv canónico de `receive` (§2)."""
        return [
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(descriptor),
        ]

    def run_receive(self, descriptor: Path) -> subprocess.CompletedProcess:
        return run_result_cli(self.receive_args(descriptor))


# ------------------------------------------------------------------- P1


class TestP1ExactReceivedBytes(EstablishedProjectCase):
    """P1 — recepción exacta e identificada."""

    def test_p1_receive_persists_identical_bytes_and_binds_identity(self) -> None:
        """P1: receive persiste cada part con bytes idénticos bajo
        `.cdad/runtime/results/<execution_id>/<packet_id>/parts/<name>.utf8`,
        liga execution/packet/feature/role/substage en el recibo mecánico y
        devuelve un receipt cuyos digests y longitudes corresponden al
        payload (stdout == bytes del receipt.json canónico)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.assertTrue(
            all(parts.values()),
            msg="precondición (fixture): todos los parts tienen bytes")
        # Manifest observable vacío pero válido (arquitecto/draft read-only
        # no escribe árbol; el bundle de identidades se materializa luego).
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        before_tree = tree_snapshot(self.root)

        proc = self.run_receive(descriptor)
        out = out_text(proc)
        self.assertNotIn(
            "unrecognized", out,
            msg="P1: el comando `receive` no existe aún (RED por CLI "
                "ausente): los argv declarados en §2 son obligatorios")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P1: receive debe aceptar el paquete dispatched y "
                f"persistir los bytes: rc={proc.returncode} "
                f"stdout={out!r} stderr={err_text(proc)!r}")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P1: receive terminó con traceback")

        final = self.final_dir()
        self.assertTrue(
            final.is_dir(),
            msg=f"P1: debe existir el destino final {final} (§5)")
        # Cada part persiste bytes idénticos (§5: parts/<name>.utf8).
        for name, data in parts.items():
            self.assert_part_file_matches(name, data)
        # Receipt mecánico ligado y con digests/longitudes correspondientes.
        self.assertTrue(
            self.receipt_path().is_file(),
            msg=f"P1: receipt.json debe existir en {self.receipt_path()}")
        receipt = json.loads(out)
        self.assertEqual(
            receipt["schema_version"], 1,
            msg=f"P1: schema_version del receipt: {receipt.get('schema_version')!r}")
        self.assertEqual(receipt["execution_id"], self.execution_id,
                         msg="P1: el recibo debe ligar el execution_id")
        self.assertEqual(receipt["packet_id"], self.packet_id,
                         msg="P1: el recibo debe ligar el packet_id")
        self.assertEqual(receipt["feature_id"], FEATURE_ID,
                         msg="P1: el recibo debe ligar la feature")
        self.assertEqual(receipt["role"], ROLE,
                         msg="P1: el recibo debe ligar el rol del paquete")
        self.assertEqual(receipt["substage"], SUBSTAGE,
                         msg="P1: el recibo debe ligar la subfase del paquete")
        receipt_parts = {part["name"]: part for part in receipt["parts"]}
        self.assertEqual(
            sorted(receipt_parts), sorted(parts),
            msg="P1: el recibo debe listar exactamente los parts del "
                "descriptor")
        for name, data in parts.items():
            part = receipt_parts[name]
            self.assertEqual(part["sha256"], hashlib.sha256(data).hexdigest(),
                             msg=f"P1: digest del part {name!r} en el receipt "
                                 f"no corresponde a los bytes staged")
            self.assertEqual(part["bytes"], len(data),
                             msg=f"P1: longitud del part {name!r} en el "
                                 f"receipt no corresponde")
        bundle_sha = hashlib.sha256(self.bundle_path().read_bytes()).hexdigest()
        self.assertEqual(receipt["bundle_sha256"], bundle_sha,
                         msg="P1: bundle_sha256 del receipt debe corresponder "
                             "a los bytes de bundle.json")
        # stdout == bytes exactos del receipt.json canónico (§2).
        self.assertEqual(
            proc.stdout, self.receipt_path().read_bytes(),
            msg="P1: receive debe escribir en stdout exactamente los bytes "
                "del receipt.json canónico")
        # Árbol: receive no escribe más allá del store operacional (§9).
        changed = sorted(
            {rel for rel, data in tree_snapshot(self.root).items()
             if before_tree.get(rel) != data})
        self.assertTrue(
            changed, msg="P1: receive debe persistir algo en el store")
        for rel in changed:
            self.assertTrue(
                rel.startswith(".cdad/runtime/"),
                msg=f"P1: receive escribió fuera del store operacional "
                    f"(§9): {rel}")

    def test_p1_invalid_or_oversized_payload_fails_without_final_result(self) -> None:
        """P1 (negativos): UTF-8 inválido, payload vacío y bundle mayor a
        1 MiB fallan con rc≠0, diagnóstico por stderr, ningún stdout y ningún
        resultado final (§5)."""
        invalid_utf8 = STAGED_PARTS | {"role-report": b"\xff\xfe no utf8"}
        empty_payload = STAGED_PARTS | {"role-report": b""}
        big_report = b"x" * (BUNDLE_LIMIT_BYTES + 1)
        oversized = STAGED_PARTS | {"role-report": big_report}
        cases = {
            "utf-8 inválido": (invalid_utf8, MANIFEST_PATH),
            "parte vacía": (empty_payload, MANIFEST_PATH),
            "bundle > 1 MiB": (oversized, MANIFEST_PATH),
        }
        for label, (parts, manifest_path) in cases.items():
            with self.subTest(caso=label):
                self.new_dispatched_project()
                self.write_staged_parts(parts=parts)
                self.write_manifest(manifest_path=manifest_path, changes=[])
                doc = self.build_descriptor(
                    parts=parts,
                    observed=self.observed_changes(
                        manifest_path=manifest_path))
                descriptor = self.write_descriptor(doc)
                before_tree = tree_snapshot(self.root)

                proc = self.run_receive(descriptor)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P1 ({label}): receive no debe aceptar el payload "
                        f"inválido")
                self.assertNotIn(
                    "No such file or directory", err_text(proc),
                    msg=f"P1 ({label}: RED inválida: el rechazo es por CLI "
                        f"ausente, no por el comportamiento bajo prueba")
                self.assertNotIn("Traceback", err_text(proc),
                                 msg=f"P1 ({label}): fallo con traceback")
                self.assertEqual(
                    proc.stdout, b"",
                    msg=f"P1 ({label}: se emitió evidencia parcial por "
                        f"stdout en un rechazo")
                self.assertEqual(
                    tree_snapshot(self.root), before_tree,
                    msg=f"P1 ({label}: el rechazo escribió el árbol o dejó "
                        f"un resultado final (§5)")
                self.assertFalse(
                    self.receipt_path().exists(),
                    msg=f"P1 ({label}: el rechazo dejó un receipt final")
                self.assertFalse(
                    self.final_dir().is_dir(),
                    msg=f"P1 ({label}: el rechazo dejó el directorio final")
                # El diagnóstico debe nombrar el motivo del rechazo (§5).
                self.assertTrue(
                    err_text(proc).strip(),
                    msg=f"P1 ({label}: el rechazo no proporcionó "
                        f"diagnóstico por stderr")


class TestP2RetryAndConflict(EstablishedProjectCase):
    """P2 — publicación atómica e idempotente."""

    def test_p2_retry_identical_converges_to_same_durable_receipt(self) -> None:
        """P2: repetir con contenido idéntico devuelve el receipt durable
        byte a byte y existe una sola finalización por execution/packet
        (§5)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)

        first = self.run_receive(descriptor)
        self.assertEqual(
            first.returncode, 0,
            msg=f"P2 (precondición de retry): el receive inicial debe "
                f"tener éxito: rc={first.returncode} "
                f"stdout={out_text(first)!r} stderr={err_text(first)!r}")
        first_receipt = self.receipt_path().read_bytes()
        self.assertEqual(
            first.stdout, first_receipt,
            msg="P2 (precondición de retry): stdout debe ser el receipt")

        second = self.run_receive(descriptor)
        self.assertEqual(
            second.returncode, 0,
            msg=f"P2: el retry idéntico debe converger al receipt durable "
                f"(rc={second.returncode}) stdout={out_text(second)!r} "
                f"stderr={err_text(second)!r}")
        self.assertEqual(
            second.stdout, first_receipt,
            msg="P2: el retry debe devolver exactamente el mismo receipt "
                "durable (§5)")
        self.assertEqual(
            self.receipt_path().read_bytes(), first_receipt,
            msg="P2: el receipt durable no cambió tras el retry")
        # Una sola finalización por execution/packet: los parts siguen siendo
        # exactamente los originales (no hay segunda copia / PKTS añadidos).
        for name, data in parts.items():
            self.assert_part_file_matches(name, data)

    def test_p2_conflicting_payload_fails_without_overwrite(self) -> None:
        """P2: mismo execution/packet con bytes conflictivos falla sin
        sobrescribir ni crear una segunda finalización (§5)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)

        first = self.run_receive(descriptor)
        self.assertEqual(
            first.returncode, 0,
            msg=f"P2 (precondición de conflicto): el receive inicial debe "
                f"tener éxito: rc={first.returncode} "
                f"stdout={out_text(first)!r} stderr={err_text(first)!r}")
        first_receipt = self.receipt_path().read_bytes()
        self.assertEqual(
            first.stdout, first_receipt,
            msg="P2 (precondición de conflicto): stdout debe ser el receipt")
        self.assertTrue(
            self.final_dir().is_dir(),
            msg="P2 (precondición de conflicto): la finalización debe existir")

        # Cambio conflictivo del mismo execution/packet: bytes distintos.
        conflicting = STAGED_PARTS | {
            "role-report": b"# Role report (version conflictiva)\n"
        }
        parts = self.write_staged_parts(parts=conflicting)
        proc = self.run_receive(descriptor)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P2: receive debe rechazar contenido conflictivo para el "
                "mismo execution/packet")
        self.assertNotIn("Traceback", err_text(proc),
                         msg="P2: fallo con traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="P2: en conflicto debe devolver vacío stdout (no un segundo "
                "receipt)")
        # No sobrescribe ni crea una segunda finalización: el receipt durable
        # y los parts persistidos son exactamente los primeros.
        self.assertEqual(
            self.receipt_path().read_bytes(), first_receipt,
            msg="P2: conflicto sobrescribió el receipt durable")
        for name, data in STAGED_PARTS.items():
            self.assert_part_file_matches(name, data)


class TestP3MechanicalReceipt(EstablishedProjectCase):
    """P3 — recibo mecánico sin aprobación semántica."""

    def test_p3_receipt_mechanical_semantic_pending_no_state_write(self) -> None:
        """P3: el recibo valida paquete/identidad/scope declarado y conserva
        los valores mecánicos (§6): `semantic_status=pending` siempre,
        `packet_validation`/`identity_validation`/`scope_validation` con los
        estados evidenciados, `run_evidence_status=not-provided`,
        `state_transition_requested=received`, presente `received_at`, y
        receive no modifica ni el state ni el contexto de ejecución
        (`docs/.cdad-state.json` sólo lo cambia el orquestador)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        state_before = (self.root / STATE_FILE).read_bytes()
        context_before = self.execution_context_path.read_bytes()
        tree_before = tree_snapshot(self.root)

        proc = self.run_receive(descriptor)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P3 (precondición): el receive debe tener éxito: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        receipt = json.loads(proc.stdout)

        # Valores mecánicos del recibo (§6).
        self.assertEqual(receipt["schema_version"], 1,
                         msg="P3: schema_version mecánica")
        self.assertEqual(receipt["packet_validation"], "passed",
                         msg="P3: validate-packet de 001 debe estar aprobado")
        self.assertEqual(receipt["identity_validation"], "passed",
                         msg="P3: la identidad del paquete debe validar")
        self.assertEqual(receipt["scope_validation"], "passed",
                         msg="P3: el scope declarado (§4 paso 6) debe validar")
        self.assertEqual(receipt["run_evidence_status"], "not-provided",
                         msg="P3: el run evidence no fue proporcionado")
        self.assertEqual(receipt["state_transition_requested"], "received",
                         msg="P3: la transición lógica solicitada es `received`")
        self.assertEqual(receipt["semantic_status"], "pending",
                         msg="P3: semantic_status siempre `pending` (§6): "
                             "ningún recibo aprueba semánticamente")
        self.assertTrue(receipt.get("received_at"),
                        msg="P3: recibido debe registrar received_at")
        self.assertEqual(receipt["source"], doc["source"],
                         msg="P3: el recibo debe conservar la fuente declarada")

        # Receive no modifica ni state ni contexto de ejecución.
        self.assertEqual(
            (self.root / STATE_FILE).read_bytes(), state_before,
            msg="P3: receive no debe modificar docs/.cdad-state.json "
                "(§9: el único escritor es el orquestador)")
        self.assertEqual(
            self.execution_context_path.read_bytes(), context_before,
            msg="P3: receive no debe modificar el contexto de ejecución v2")
        # Receive no materializa artefactos de rol: única escritura del
        # árbol bajo `.cdad/runtime/` (§9 propiedad del estado). El paquete
        # publicado bajo `.cdad/packets/` no cambia.
        tree_after = tree_snapshot(self.root)
        changed = sorted(
            rel for rel, data in tree_after.items()
            if tree_before.get(rel) != data)
        self.assertTrue(
            changed, msg="P3: receive debe de persistir el recibo en el store")
        for rel in changed:
            self.assertTrue(
                rel.startswith(".cdad/runtime/"),
                msg=f"P3: receive no debe escribir fuera del store "
                    f"operacional (§9): {rel}")
        # El paquete publicado no cambia (receive no lo reescribe).
        self.assertEqual(
            self.packet_path.read_bytes(),
            tree_before[self.packet_path.relative_to(self.root).as_posix()],
            msg="P3: receive no debe reescribir el PACKET.md del paquete")


# ------------------------------------------------------------------- P6


class TestP6ManifestScope(EstablishedProjectCase):
    """P6 (base T1) — scopes y límites de prueba explícitos."""

    def test_p6_manifest_outside_write_scope_fails_without_finalization(self) -> None:
        """P6: un path observado fuera del write scope declarado falla antes
        de publicar y no deja finalización durable (§4 paso 6)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[{"path": OUT_OF_SCOPE_CHANGE,
                                      "operation": "modified"}])
        descriptor = self.write_descriptor(
            self.build_descriptor(parts=parts,
                                  observed=self.observed_changes()))
        before_tree = tree_snapshot(self.root)

        proc = self.run_receive(descriptor)
        out = out_text(proc)
        self.assertNotIn(
            "unrecognized", out,
            msg="P6: el comando `receive` no existe aún (RED por CLI "
                "ausente)")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P6: un path observado fuera del write scope debe "
                f"rechazarse antes de publicar; rc={proc.returncode}")
        self.assertEqual(
            tree_snapshot(self.root), before_tree,
            msg="P6: el rechazo fuera de scope dejó.partial final")
        self.assertFalse(
            self.receipt_path().exists(),
            msg="P6: el rechazo fuera de scope dejó un receipt final")
        self.assertEqual(
            proc.stdout, b"",
            msg="P6: en rechazo fuera de scope no se publicó stdout")
        self.assertTrue(
            re.search(r"scope|alcance", err_text(proc), re.IGNORECASE),
            msg=f"P6: el diagnóstico no nombra el scope/alcance "
                f"(spec §4: «path observado fuera de scope»): "
                f"{err_text(proc)!r}")

    def test_p6_absent_manifest_persists_pending_receipt_with_scope_unknown(self) -> None:
        """P6: la ausencia de manifest deja `scope_validation=unknown`: el
        receipt pending se publica, pero no puede gatear ni materializarse
        hasta una comprobación trusted (§4/§6)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        # Descriptor SIN observed_changes (no hay manifest confiable).
        doc = self.build_descriptor(parts=parts, observed=None)
        descriptor = self.write_descriptor(doc)

        proc = self.run_receive(descriptor)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P6: la ausencia de manifest es `unknown`: publish del "
                f"receipt pending con rc=0; rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        receipt = json.loads(proc.stdout)
        self.assertEqual(
            receipt["scope_validation"], "unknown",
            msg=f"P6: scope_validation debe ser `unknown` sin manifest "
                f"confiable: {receipt.get('scope_validation')!r}")
        self.assertEqual(
            receipt["semantic_status"], "pending",
            msg="P6: el receipt publicado sin manifest debe permanecer "
                "pending (no sirve como gate)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
