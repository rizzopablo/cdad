#!/usr/bin/env python3
"""005-001 T-CORR RED — Dos correcciones acotadas de T1/T2 (enmienda 2026-10-09).

Contract:
- docs/specs/005-001-idle-and-v7-bootstrap/spec.md §2 (PD-18..PD-24), §3
  (INV-7, INV-8), §7 (D4 enmendada, D7).
- docs/epics/epic-005-real-operation/plan.md (T-CORR).

Alcance del punto (objetivo del packet):
- C1 (PD-18, INV-8): el pin de la aprobación de spec debe NOMBRAR el
  contrato: `contract_path == contract["path"]` Y `contract_sha256` verificado.
  Test focal: sha correcto con path otro (o ausente) → rc=2 `approval pending`
  que nombra el path REGISTRADO y el ESPERADO y la acción para corregir;
  control positivo interno: la misma entrada con el path correcto → rc=0 (PD-5).
- C2 (PD-19..PD-24, INV-7): cinco focales (conservación sin opciones,
  rechazo sin efectos ante insumo inexistente, recuperación con la corrección
  explícita, rechazo de alcance fuera de la política, pisos del rol
  imposibles de quitar) + centinela de lista vacía (PD-20/D7, permitida y
  no permitida) + PD-23 (argv mezclado, con control positivo de PD-20) +
  PD-24 (traza conserved_fields/changed_fields en `.superseded.json`).

Superficie observable bajo prueba (§2/D4 enmendada):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --replace-packet <packet-id> --reason <texto> \
        [--input P=P] [--read-scope C[=S]] [--write-scope C[=S]] \
        [--invariant T] [--expected-output T] [--evidence T]
    python3 scripts/cdad_packet.py prepare --project-root R \
        --role <rol> --substage <sub> --objective <texto>   # C1 / fixtures

RED hoy (probe caja negra sobre proyectos sintéticos, dictado del contrato
solamente — NINGUNA lectura de implementación):
- PD-18: hoy la entrada con `contract_sha256` correcto y `contract_path`
  otro/ausente HABILITA (rc=0): el RED fracasa en la aserción de rc/marcador.
- PD-19: hoy `--replace-packet` sin opciones RECOMPONE los defaults
  (inputs/read_scope/invariants/expected_output/evidence_required del
  REQUEST.json nuevo difieren del anterior cuando el encargo era no-default):
  el RED fracasa en las aserciones de conservación campo a campo.
- PD-20/PD-22: hoy las opciones de corrección en el sub-modo replace se
  rechazan por mezcla de modos («unexpected: --input…»): el RED fracasa en
  rc (controles positivos) y en las aserciones de motivo/campo/opción.
- PD-21: hoy no existen los pisos del reemplazo (mismo argv rechazado).
- PD-23: el argv mezclado ya fracasa con rc=2 (T2 GREEN); el control
  positivo interno exigido por §2 (correcciones de PD-20 → rc=0) fracasa:
  el RED del test vive en ese control, no en el negativo (regresión).
- PD-24: el `.superseded.json` publicado hoy no lleva `conserved_fields` /
  `changed_fields`: el RED fracasa en esas aserciones.

Todo fallo RED es AssertionError de comportamiento de superficie observable;
nunca ImportError, nunca traceback del CLI.

Fixtures offline (patrón 005-001 T1/T2 y carrier v2 de test_role_packets.py):
proyectos sintéticos en tempdirs con política PROPUESTA por el CLI
(`--propose-policy`) y materializada por el fixture «dueño» (que declara el
`test_files` del archivo custom), spec pineada aprobada, delegación HITL
activa. La obsolescencia se construye por interfaz pública (editar spec.md →
derivación del sha; re-pin del registro `specification` lo realiza el
orquestador del fixture, nunca el CLI — INV-2). Ninguna escritura en este
repo y ninguna lectura de implementación.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-005-real-operation"
FEATURE_ID = "005-001-idle-and-v7-bootstrap"
AUTH_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"

SPEC_BYTES = b"# Spec fixture (005-001 T-CORR)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada despues de aprobar (TCORR)\n"
SPEC_SHA256 = hashlib.sha256(SPEC_BYTES).hexdigest()
SPEC_DRIFT_SHA256 = hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest()

# Valores default del encargo de test-writer (estabilidad conocida del
# contrato de rol; ver tests/test_packet_prepare.py, constantes de rol).
DEFAULT_INVARIANTS_TW = (
    "Do not read implementation code",
    "Each test maps to a postcondition",
)
DEFAULT_EVIDENCE = (
    "modified files",
    "exact commands",
    "command output",
    "commit",
)

APPROVER = "Pablo"
REASON = "contrato editado despues de preparar el paquete (T-CORR)"

ROLE, SUBSTAGE = "test-writer", "red"
CUSTOM_TEST_FILE = "tests/test_probe.py"
CONSTRUCTION_ROLES = (
    ("test-writer", "red"),
    ("implementer", "green"),
    ("reviewer", "review"),
)

PACKET_BEGIN = "---cdad-packet-json"
PENDING_MARKER = "approval pending"
OBSOLETE_MARKER = "packet obsolete"
INCOHERENT_MARKER = "state incoherent"
SUPERSEDED_FILE = ".superseded.json"

# Universo PD-24 de campos del encargo observable en REQUEST.json.
ASSIGNMENT_UNIVERSE = (
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


# ---------------------------------------------------------------- fixtures


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def prepare(root: Path, *, role: str = ROLE, substage: str = SUBSTAGE,
            objective: str = "005-001 T-CORR objective",
            extra: tuple[tuple[str, str | None], ...] = ()) -> subprocess.CompletedProcess:
    args = ["prepare", "--project-root", str(root),
            "--role", role, "--substage", substage,
            "--objective", objective]
    for flag, value in extra:
        args += [flag, *( [value] if value is not None else [] )]
    return run_cli(args)


def run_replace(root: Path, packet_id: str, *, reason: str | None = REASON,
                corr: tuple[tuple[str, str], ...] = ()) -> subprocess.CompletedProcess:
    """Sub-modo §2/D4 enmendado: selector + --reason + correcciones."""
    args = ["prepare", "--project-root", str(root),
            "--replace-packet", packet_id]
    if reason is not None:
        args += ["--reason", reason]
    for flag, value in corr:
        args += [flag, value]
    return run_cli(args)


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


def active_packet_id(root: Path) -> str:
    active = read_state(root).get("active_packet") or {}
    if not active.get("id"):
        raise AssertionError(f"fixture: sin active_packet.id: {active!r}")
    return active["id"]


def spec_approval_entry(*, contract_path: str | None = SPEC_FILE,
                        contract_sha256: str = SPEC_SHA256) -> dict:
    """Entrada pineada de especificación (D3: path + sha256 obligatorios;
    C1: si la entrada NO nombra el contrato, cada variante la admite)."""
    entry = {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": APPROVER,
        "approved_at": "2026-10-08T00:00:00Z",
        "contract_sha256": contract_sha256,
    }
    if contract_path is not None:
        entry["contract_path"] = contract_path
    return entry


def build_project(root: Path, *,
                  approval: dict | None = None,
                  stage_history: list[dict] | None = None) -> Path:
    """Proyecto sintético válido (carrier v2 del patrón test_role_packets):
    política PROPUESTA por el CLI + test_files del archivo custom, spec
    aprobada pineada, fuente de autoridad y delegación HITL activa."""
    root.mkdir(parents=True)
    for rel in ("src", "lib", "tests"):
        (root / rel).mkdir(exist_ok=True)
    (root / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (root / "README.md").write_text("# Fixture (T-CORR)\n", encoding="utf-8")
    (root / CUSTOM_TEST_FILE).write_text(
        "# custom invocation target (fixture)\n", encoding="utf-8")
    (root / "docs").mkdir(exist_ok=True)
    proposal = run_cli([
        "prepare", "--project-root", str(root), "--propose-policy"])
    if proposal.returncode != 0:
        raise AssertionError(
            f"fixture: --propose-policy debe autocompletar la política "
            f"válida: {proposal.stderr!r}")
    policy = json.loads(proposal.stdout)
    path_policy = policy.setdefault("path_policy", {})
    test_files = path_policy.setdefault("test_files", [])
    if CUSTOM_TEST_FILE not in test_files:
        test_files.append(CUSTOM_TEST_FILE)
    (root / POLICY_FILE).write_text(
        json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spec = root / SPEC_FILE
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_bytes(SPEC_BYTES)
    authority = root / AUTH_REF
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
        "stage_history": ([approval] if approval is not None
                          else (stage_history if stage_history is not None
                                else [spec_approval_entry()])),
        "approver": APPROVER,
        "last_updated": "2026-10-08T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTH_REF,
            "scope": EPIC_ID,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        },
    }
    write_state(root, state)
    return root


def custom_assignment() -> tuple[tuple[str, str | None], ...]:
    """Encargo NO-default para el REQUEST.json anterior (falsifica PD-19:
    si el reemplazo recompone defaults, las aserciones de conservación
    fracasan campo a campo)."""
    return (
        ("--input", f"{CUSTOM_TEST_FILE}=encargo custom T-CORR"),
        ("--read-scope", f"contract=docs/specs/{FEATURE_ID}"),
        ("--read-scope", f"tests={CUSTOM_TEST_FILE}"),
        ("--write-scope", "tests=tests"),
        ("--invariant", "INVencargo custom T-CORR"),
        ("--expected-output", "report custom T-CORR"),
        ("--evidence", "evidencia custom T-CORR"),
    )


def make_prepared_project(base: Path, **build_kwargs) -> Path:
    return build_project(Path(base) / "proj", **build_kwargs)


class TCorrCase(unittest.TestCase):
    """Base: cada proyecto sintético en su propio tempdir Fresh."""

    def make_project(self, **build_kwargs) -> Path:
        base = tempfile.mkdtemp(prefix="cdad-005-001-tcorr-")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        return make_prepared_project(Path(base), **build_kwargs)

    def prepared_packet(self, *, custom: bool = False) -> tuple[Path, str, dict]:
        """Fixture precondición (PD-5 vigente): política + pin+spec
        coincidentes → `prepare` habilita y deja el paquete activo
        `prepared`. Con `custom`, el REQUEST.json previo lleva un encargo
        no-default (para falsificar la conservación de PD-19)."""
        root = self.make_project()
        proc = prepare(root, extra=custom_assignment() if custom else ())
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): el pin vigente debe habilitar "
                f"prepare (PD-5): {proc.stdout!r} {proc.stderr!r}")
        active = read_state(root)["active_packet"]
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"precondición (fixture): paquete activo: {active!r}")
        pid = active["id"]
        request = request_of(root, pid)
        if custom:
            # Control de fixture: el encargo previo es no-default en los
            # campos que PD-19 exige conservar.
            self.assertEqual(
                request.get("expected_output"), "report custom T-CORR",
                msg=f"precondición (fixture): expected_output custom: "
                    f"{request!r}")
            self.assertIn(
                "INVencargo custom T-CORR", request.get("invariants", []),
                msg=f"precondición (fixture): invariant custom: {request!r}")
            self.assertIn(
                "evidencia custom T-CORR", request.get("evidence_required", []),
                msg=f"precondición (fixture): evidence custom: {request!r}")
            self.assertEqual(
                [{"path": CUSTOM_TEST_FILE, "purpose": "encargo custom T-CORR"}],
                [i for i in request.get("inputs", [])
                 if i.get("path") == CUSTOM_TEST_FILE],
                msg=f"precondición (fixture): input custom: {request!r}")
        return root, pid, request

    def outdate_and_reauthorize(self, root: Path, packet_id: str) -> tuple[str, str]:
        """Obsolescencia PD-8(a) por interfaz pública: edita la spec (deriva
        el sha del REQUEST.json del paquete) y re-pinea la entrada
        `specification` al sha ACTUAL (el orquestador del fixture registra
        la aprobación — el CLI jamás escribe aprobaciones, INV-2). El
        contract_path del pin queda SIEMPRE en SPEC_FILE (nombra el
        contrato del día). Devuelve (registrado, actual)."""
        stale = (root / SPEC_FILE).read_bytes()
        if stale == SPEC_DRIFT_BYTES:
            raise AssertionError("fixture: la spec ya estaba derivada")
        (root / SPEC_FILE).write_bytes(SPEC_DRIFT_BYTES)
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
        registered = request_of(root, packet_id)["contract"]["sha256"]
        if registered != SPEC_SHA256:
            raise AssertionError(
                f"fixture: el sha registrado no es el de los bytes "
                f"aprobados: {registered[:12]}… != {SPEC_SHA256[:12]}…")
        return registered, SPEC_DRIFT_SHA256

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
        pedido (y sin los excluidos), sin efectos (PD-22 «sin publicar
        nada» y PD-12 «no altera el state ni publica archivos»)."""
        out = proc.stdout + proc.stderr
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
                msg=f"{label}: el marcador se mezcló con {banned!r} "
                    f"(PD-12: exclusivos por condición): {out!r}")
        self.assert_no_writes(label, root, before, state_before)


# ---------------------------------------------------------------- PD-18


class TestPd18SpecPinMustNameTheContract(TCorrCase):
    """PD-18 (C1, INV-8): la entrada `specification` habilita SOLO si su pin
    nombra el contrato verificado: `contract_path == contract["path"]` Y
    `contract_sha256` verificado. Con el sha correcto pero el path otro (o
    ausente) → rc=2 `approval pending` que nombra el contract_path
    REGISTRADO y el ESPERADO y la acción para corregir; sin efectos.
    Control positivo interno: la misma entrada con el path correcto → rc=0
    (PD-5)."""

    def test_pd18_pin_with_correct_sha_but_foreign_or_missing_path_blocks(self) -> None:
        wrong_path = "docs/specs/OTHER-approval-source/spec.md"
        cases = (
            ("path registrado de otra feature", wrong_path),
            ("path registrado ausente", None),
        )
        for role, substage in CONSTRUCTION_ROLES:
            for label, pin_path in cases:
                with self.subTest(role=role, case=label):
                    project = self.make_project(
                        approval=spec_approval_entry(contract_path=pin_path))
                    before = tree_snapshot(project)
                    state_before = state_bytes(project)
                    proc = prepare(project, role=role, substage=substage)
                    self.assert_rejection(
                        f"PD-18 {role} ({label})", project, before,
                        state_before, proc,
                        marker=PENDING_MARKER,
                        forbidden_markers=(OBSOLETE_MARKER, INCOHERENT_MARKER))
                    stderr = proc.stderr
                    # El diagnóstico nombra el path REGISTRADO…
                    if pin_path is not None:
                        self.assertIn(
                            pin_path, stderr,
                            msg=f"PD-18 {role} ({label}): el diagnóstico no "
                                f"nombra el contract_path registrado: "
                                f"{stderr!r}")
                    # …y el path ESPERADO (el del contrato verificado)…
                    self.assertIn(
                        SPEC_FILE, stderr,
                        msg=f"PD-18 {role} ({label}): el diagnóstico no "
                            f"nombra el contract_path esperado "
                            f"({SPEC_FILE}): {stderr!r}")
                    # …y el registro y la acción para corregir (R2/PD-3).
                    self.assertRegex(
                        stderr, r"stage_history|specification|approved",
                        msg=f"PD-18 {role} ({label}): el diagnóstico no nombra "
                            f"el registro stage_history/specification/approved "
                            f"ni la acción de corregirlo: {stderr!r}")

    def test_pd18_control_pin_with_correct_path_and_sha_enables_each_role(self) -> None:
        """Control positivo interno (PD-5): la MISMA entrada (sha correcto)
        con el contract_path correcto habilita a cada rol → rc=0."""
        for role, substage in CONSTRUCTION_ROLES:
            with self.subTest(role=role):
                project = self.make_project(
                    approval=spec_approval_entry())
                proc = prepare(project, role=role, substage=substage)
                combined = proc.stdout + proc.stderr
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"PD-18 control {role}: la misma entrada con el "
                        f"contract_path correcto debe habilitar "
                        f"(PD-5): {combined!r}")
                self.assertTrue(
                    proc.stdout.startswith(PACKET_BEGIN),
                    msg=f"PD-18 control {role}: stdout sin paquete canónico")


# ---------------------------------------------------------------- PD-19


class TestPd19ReplaceWithoutOptionsConservesPredecessor(TCorrCase):
    """PD-19 (C2): con paquete prepared y obsolescencia verificada,
    `--replace-packet <id> --reason <texto>` SIN opciones de corrección
    publica un paquete nuevo cuyo REQUEST.json conservA, tal cual, los
    valores del REQUEST.json anterior para execution_id, role, substage,
    objective, inputs, read_scope, write_scope, invariants, expected_output
    y evidence_required. El contrato se re-resuelve al actual."""

    def test_pd19_replace_without_options_conserves_assignment_field_by_field(self) -> None:
        root, pid, old_request = self.prepared_packet(custom=True)
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_packet_md = packet_bytes(root, pid, "PACKET.md")
        registered, current = self.outdate_and_reauthorize(root, pid)

        proc = run_replace(root, pid)
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-19: el reemplazo sin opciones del paquete prepared "
                f"con obsolescencia y autorización vigentes debe publicar "
                f"el sucesor: {out!r}")
        successors = [p for p in packet_ids(root) if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-19: paquetes en disco tras el reemplazo: "
                f"{packet_ids(root)}")
        new_id = successors[0]
        new_request = request_of(root, new_id)

        # Conservación campo a campo del encargo anterior (PD-19/INV-7).
        for field in ASSIGNMENT_UNIVERSE:
            self.assertEqual(
                new_request.get(field), old_request.get(field),
                msg=f"PD-19: el paquete nuevo no conservó {field} del "
                    f"REQUEST.json anterior "
                    f"(anterior={json.dumps(old_request.get(field), ensure_ascii=False)}; "
                    f"nuevo={json.dumps(new_request.get(field), ensure_ascii=False)})")
        # INV-3: los bytes del paquete anterior quedan intactos.
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-19/INV-3: REQUEST.json del paquete anterior cambió")
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-19/INV-3: PACKET.md del paquete anterior cambió")
        # El contrato se RE-RESUELVE al actual (no se conserva).
        self.assertEqual(
            new_request.get("contract", {}).get("sha256"), current,
            msg=f"PD-19: el paquete nuevo no lleva el contrato actual "
                f"({current[:12]}…): "
                f"{json.dumps(new_request.get('contract'))}")
        self.assertEqual(
            new_request.get("contract", {}).get("path"), SPEC_FILE,
            msg="PD-19: el paquete nuevo no lleva la ruta del contrato")
        state_after = read_state(root)
        active = state_after.get("active_packet") or {}
        self.assertEqual(
            active.get("id"), new_id,
            msg=f"PD-19: state.active_packet no apunta al nuevo: {active!r}")


# ---------------------------------------------------------------- PD-20


class TestPd20CorrectionOptionsReplaceWholeLists(TCorrCase):
    """PD-20 (C2, D7): en el sub-modo reemplazo cada opción de corrección
    (--input/--read-scope/--write-scope/--invariant/--expected-output/
    --evidence) reemplaza esa lista/campo ENTERO; el centinela `-` como
    único valor deja la lista vacía; `-` mezclado con otros valores del
    mismo campo → rc=2 (ambigüedad) sin efectos. Lista vacía permitida
    cuando el resultado sigue siendo un encargo válido (PD-22):
    `--input -` es legítimo; un `read_scope` vacío que deja un input fuera
    de alcance es rechazado."""

    def test_pd20_sentinel_empty_list_allowed_and_ambiguity_rejected(self) -> None:
        root, pid, _old = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root, pid)

        # (a) Recuperación con la corrección explícita (focal C2-3): tras el
        # rechazo, la misma invocación con el insumo correcto → rc=0 y la
        # lista reemplazada ENTERA (no agregada a lo conservado).
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        rejected = run_replace(root, pid, corr=(
            ("--input", f"{CUSTOM_TEST_FILE}/missing.py=meti errado"),))
        self.assertEqual(
            rejected.returncode, 2,
            msg=f"PD-20 (a): el insumo inexistente debe rechazar antes de "
                f"publicar: {rejected.stdout + rejected.stderr!r}")
        self.assertEqual(
            tree_snapshot(root), before,
            msg="PD-20 (a): el rechazo escribió algo")
        accepted = run_replace(root, pid, corr=(
            ("--input", f"{CUSTOM_TEST_FILE}=correccion explicita"),))
        out = accepted.stdout + accepted.stderr
        self.assertEqual(
            accepted.returncode, 0,
            msg=f"PD-20 (a): la misma invocación con el insumo correcto "
                f"debe publicar el paquete corregido (PD-22 control "
                f"positivo): {out!r}")
        new_id = active_packet_id(root)
        new_request = request_of(root, new_id)
        self.assertEqual(
            new_request.get("inputs"),
            [{"path": CUSTOM_TEST_FILE, "purpose": "correccion explicita"}],
            msg=f"PD-20 (a): --input debe reemplazar la lista entera (sin "
                f"agregar a lo conservado): {new_request.get('inputs')!r}")
        # Enmienda de oráculo: para reemplazar inputs el reemplazo puede
        # necesitar el reemplazo de read_scope explícito; sin él, el input
        # sigue dentro del alcance conservado.
        self.assertIn(
            {"class": "tests", "path": CUSTOM_TEST_FILE},
            new_request.get("read_scope", []),
            msg=f"PD-20 (a): el read_scope conservado sigue admitiendo el "
                f"input corregido: {new_request.get('read_scope')!r}")

        # (b) Lista vacía PERMITIDA: `--input -` → rc=0 con inputs == []
        # (proyecto fresco con el mismo encargo custom; el centinela deja
        # la lista VACÍA).
        rootb, pidb, _reqb = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(rootb, pidb)
        empty = run_replace(rootb, pidb, corr=(("--input", "-"),))
        outb = empty.stdout + empty.stderr
        self.assertEqual(
            empty.returncode, 0,
            msg=f"PD-20 (b): `--input -` deja la lista vacía y el encargo "
                f"sigue siendo válido (PD-20/D7): rc debe ser 0: {outb!r}")
        reqb_new = request_of(rootb, active_packet_id(rootb))
        self.assertEqual(
            reqb_new.get("inputs"), [],
            msg=f"PD-20 (b): `--input -` debe dejar inputs vacío: "
                f"{reqb_new.get('inputs')!r}")

        # (c) `-` MEZCLADO con otros valores del mismo campo → rc=2
        # (ambigüedad), sin efectos; NO es el rechazo de argv mezclado.
        rootc, pidc, _reqc = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(rootc, pidc)
        before_c = tree_snapshot(rootc)
        state_before_c = state_bytes(rootc)
        ambiguous = run_replace(rootc, pidc, corr=(
            ("--invariant", "-"), ("--invariant", "INV adicional"),))
        self.assert_rejection(
            "PD-20 (c)", rootc, before_c, state_before_c, ambiguous)
        self.assertNotIn(
            "unexpected", ambiguous.stderr,
            msg=f"PD-20 (c): el motivo debe ser la AMBIGÜEDAD del centinela "
                f"(no el rechazo de argv mezclado de otro modo): "
                f"{ambiguous.stderr!r}")
        self.assertIn(
            "invariant", ambiguous.stdout + ambiguous.stderr,
            msg=f"PD-20 (c): el rechazo no nombra el campo del centinela "
                f"ambiguo: {ambiguous.stderr!r}")

        # (d) Lista vacía NO permitida si deja un input fuera de alcance:
        # `--read-scope -` con el input del contrato en la lista conservada
        # → rc=2 (input fuera de alcance), sin efectos.
        rootd, pidd, _reqd = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(rootd, pidd)
        before_d = tree_snapshot(rootd)
        state_before_d = state_bytes(rootd)
        narrow = run_replace(rootd, pidd, corr=(("--read-scope", "-"),))
        self.assert_rejection(
            "PD-20 (d)", rootd, before_d, state_before_d, narrow)
        self.assertNotIn(
            "unexpected", narrow.stderr,
            msg=f"PD-20 (d): el motivo debe ser la validación del encargo "
                f"(input fuera de alcance), no el argv-mix: "
                f"{narrow.stderr!r}")
        self.assertIn(
            "read-scope", narrow.stdout + narrow.stderr,
            msg=f"PD-20 (d): el rechazo no nombra la opción --read-scope: "
                f"{narrow.stderr!r}")
        self.assertIn(
            SPEC_FILE, narrow.stderr,
            msg=f"PD-20 (d): el rechazo no nombra el input que quedó fuera "
                f"de alcance: {narrow.stderr!r}")


# ---------------------------------------------------------------- PD-21


class TestPd21RoleFloorsImpossibleToDrop(TCorrCase):
    """PD-21 (C2, INV-7): `--invariant` reemplaza la lista pero NUNCA
    elimina los DEFAULT_INVARIANTS del rol (se re-agregan), aunque se dé
    `--invariant -`. `--evidence` reemplaza pero nunca elimina la
    evidencia mínima del rol (DEFAULT_Evidence, se re-agrega). Observable
    en el REQUEST.json del paquete publicado."""

    def test_pd21_floor_invariants_and_evidence_survive_the_correction(self) -> None:
        root, pid, old_request = self.prepared_packet(custom=True)
        # Control de fixture: el encargo previo custom portaba el valor
        # extra 'INVencargo custom T-CORR' fuera del piso; la corrección
        # debe reemplazarlo SIN perder el piso.
        self.assertIn(
            "INVencargo custom T-CORR", old_request.get("invariants", []),
            msg="precondición (fixture): el encargo previo portaba el "
                "invariant custom")
        self.outdate_and_reauthorize(root, pid)

        # `--invariant -`: la lista queda vacía por corrección y el piso del
        # rol se re-agrega SIEMPRE.
        empty = run_replace(root, pid, corr=(("--invariant", "-"),))
        out = empty.stdout + empty.stderr
        self.assertEqual(
            empty.returncode, 0,
            msg=f"PD-21: `--invariant -` debe vaciar la lista corregida y "
                f"re-agregar el piso del rol (rc=0): {out!r}")
        new_request = request_of(root, active_packet_id(root))
        floors = list(DEFAULT_INVARIANTS_TW)
        for floor in floors:
            self.assertIn(
                floor, new_request.get("invariants", []),
                msg=f"PD-21: el invariants publicado perdió el piso del rol "
                    f"({floor!r}) con --invariant -: "
                    f"{new_request.get('invariants')!r}")
        self.assertNotIn(
            "INVencargo custom T-CORR", new_request.get("invariants", []),
            msg=f"PD-21: el encargo anterior no debe filtrarse por encima "
                f"de la corrección (--invariant lo reemplaza ENTERO): "
                f"{new_request.get('invariants')!r}")

        # `--evidence -`: ídem con la evidencia mínima del rol.
        root2, pid2, _old2 = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root2, pid2)
        empty_ev = run_replace(root2, pid2, corr=(("--evidence", "-"),))
        out_ev = empty_ev.stdout + empty_ev.stderr
        self.assertEqual(
            empty_ev.returncode, 0,
            msg=f"PD-21: `--evidence -` debe vaciar la lista corregida y "
                f"re-agregar la evidencia mínima del rol (rc=0): {out_ev!r}")
        new_request2 = request_of(root2, active_packet_id(root2))
        for floor in DEFAULT_EVIDENCE:
            self.assertIn(
                floor, new_request2.get("evidence_required", []),
                msg=f"PD-21: la evidence_required publicada perdió el piso "
                    f"mínimo del rol ({floor!r}) con --evidence -: "
                    f"{new_request2.get('evidence_required')!r}")


# ---------------------------------------------------------------- PD-22


class TestPd22CorrectionsPassSameValidations(TCorrCase):
    """PD-22 (C2): las correcciones pasan las MISMAS validaciones de un
    prepare normal: scopes contra la política, inputs dentro del read_scope
    y campos cerrados. Ante una corrección invalida → rc=2,_sin publicar
    nada, con el paquete anterior byte a byte intacto; el stderr nombra el
    CAMPO, el MOTIVO y la OPCIÓN para corregirlo."""

    def test_pd22_missing_input_rejected_naming_field_reason_and_option(self) -> None:
        root, pid, _old = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root, pid)
        missing = f"{CUSTOM_TEST_FILE}/inexistente.py"
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_packet_md = packet_bytes(root, pid, "PACKET.md")
        proc = run_replace(root, pid, corr=(
            ("--input", f"{missing}=meti inexistente"),))
        self.assert_rejection(
            "PD-22 (input inexistente)", root, before, state_before, proc)
        out = proc.stdout + proc.stderr
        self.assertIn(
            "inputs", out,
            msg=f"PD-22: el rechazo no nombra el campo (inputs): {out!r}")
        self.assertIn(
            missing, out,
            msg=f"PD-22: el rechazo no nombra el input.path del motivo: "
                f"{out!r}")
        self.assertIn(
            "--input", out,
            msg=f"PD-22: el rechazo no nombra la opción para corregir "
                f"(--input): {out!r}")
        # El paquete anterior queda byte a byte intacto (PD-22).
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-22: el REQUEST.json del paquete anterior cambió")
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-22: el PACKET.md del paquete anterior cambió")

    def test_pd22_write_scope_outside_policy_rejected_naming_field_reason(self) -> None:
        root, pid, _old = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root, pid)
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc = run_replace(root, pid, corr=(
            ("--write-scope", "implementation=src"),))
        self.assert_rejection(
            "PD-22 (write-scope fuera de la política)", root, before,
            state_before, proc)
        out = proc.stdout + proc.stderr
        self.assertIn(
            "write_scope", out,
            msg=f"PD-22: el rechazo no nombra el campo (write_scope): "
                f"{out!r}")
        self.assertIn(
            "--write-scope", out,
            msg=f"PD-22: el rechazo no nombra la opción para corregir "
                f"(--write-scope): {out!r}")
        self.assertRegex(
            proc.stderr, r"politic|policy|no admite|not permitido|invalid",
            msg=f"PD-22: el rechazo no nombra el motivo de política en "
                f"write_scope: {proc.stderr!r}")


# ---------------------------------------------------------------- PD-23


class TestPd23MixedArgvRejectedInReplace(TCorrCase):
    """PD-23 (C2): `--replace-packet` NO acepta flags ordinarios de otros
    sub-modos (--role, --substage, --objective, --new-execution, --out-dir,
    --contract-kind, --resume-packet…): el argv mezclado → rc=2, sin
    efectos (rechazado antes de cualquier lock o escritura). El contrato
    se re-resuelve al actual y se publica solo si la aprobación lo
    habilita. Control positivo interno: `--replace-packet` con las
    opciones de corrección de PD-20 → rc=0."""

    FORBIDDEN_FLAGS: tuple[tuple[str, str | None], ...] = (
        ("--role", "implementer"),
        ("--substage", "green"),
        ("--objective", "objetivo intruso"),
        ("--new-execution", None),
        ("--out-dir", "out-intruso"),
        ("--contract-kind", "approved-epic-plan"),
        ("--resume-packet", "packet-id intruso"),
    )

    def test_pd23_replace_with_foreign_flags_rejected_without_effects(self) -> None:
        root, pid, _old = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root, pid)
        for flag, value in self.FORBIDDEN_FLAGS:
            with self.subTest(flag=flag):
                before = tree_snapshot(root)
                state_before = state_bytes(root)
                args = ["prepare", "--project-root", str(root),
                        "--replace-packet", pid, "--reason", REASON,
                        flag, *( [value] if value is not None else [] )]
                proc = run_cli(args)
                self.assert_rejection(
                    f"PD-23 ({flag})", root, before, state_before, proc)
                self.assertNotIn(
                    "Traceback", proc.stderr,
                    msg=f"PD-23 ({flag}): fallo con traceback")

    def test_pd23_control_replace_with_pd20_correction_options_succeeds(self) -> None:
        """Control positivo interno exigido por §2 (PD-23): mismas opciones
        de corrección de PD-20 SIN flags foráneos → rc=0."""
        root, pid, _old = self.prepared_packet(custom=True)
        self.outdate_and_reauthorize(root, pid)
        proc = run_replace(root, pid, corr=(
            ("--invariant", "INV del control PD-23"),
            ("--expected-output", "report del control PD-23"),
            ("--evidence", "evidencia del control PD-23"),
        ))
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-23 control: --replace-packet con las opciones de "
                f"corrección de PD-20 (sin flags foráneos) debe publicar "
                f"(hoy el sub-modo rechaza las correcciones): {out!r}")
        new_request = request_of(root, active_packet_id(root))
        self.assertIn(
            "INV del control PD-23", new_request.get("invariants", []),
            msg=f"PD-23 control: la corrección --invariant no llegó al "
                f"paquete: {new_request.get('invariants')!r}")


# ---------------------------------------------------------------- PD-24


class TestPd24SupersededRecordTracksConservation(TCorrCase):
    """PD-24 (C2): el registro durable `.superseded.json` conserva
    {superseded_by, reason, superseded_at, contract_sha256_old,
    contract_sha256_new} y AGREGA la traza por campo: `conserved_fields`
    y `changed_fields`, disjuntos y con unión = universo del encargo;
    un campo aparece en changed si su valor nuevo difiere, y en conserved
    si es idéntico."""

    def test_pd24_superseded_record_tracks_conserved_and_changed_fields(self) -> None:
        # (1) Reemplazo POR CONSERVACIÓN (sin correcciones): la traza debe
        # quedar con conserved_fields == universo y changed_fields == [].
        root, pid, old_request = self.prepared_packet(custom=True)
        registered, current = self.outdate_and_reauthorize(root, pid)
        proc = run_replace(root, pid)
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-24 (conservación): el reemplazo sin opciones debe "
                f"publicar (PD-19): {out!r}")
        new_id = active_packet_id(root)
        new_request = request_of(root, new_id)
        record_path = packet_dir(root, pid) / SUPERSEDED_FILE
        self.assertTrue(
            record_path.is_file(),
            msg=f"PD-24: no quedó el registro {SUPERSEDED_FILE} en el "
                f"paquete anterior")
        record = json.loads(record_path.read_text(encoding="utf-8"))
        self.assert_trace_consistency(
            record, old_request, new_request, registered, current)

        # (2) Corrección explícita EXACTAMENTE sobre `invariants`: el resto
        # queda conservado idéntico → changed == {invariants}.
        root2, pid2, old_request2 = self.prepared_packet(custom=True)
        registered2, current2 = self.outdate_and_reauthorize(root2, pid2)
        proc2 = run_replace(root2, pid2,
                            corr=(("--invariant", "INV traza PD-24"),))
        out2 = proc2.stdout + proc2.stderr
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"PD-24 (cambio): el reemplazo con corrección de "
                f"invariants debe publicar (hoy el sub-modo rechaza las "
                f"correcciones): {out2!r}")
        new_id2 = active_packet_id(root2)
        new_request2 = request_of(root2, new_id2)
        record2 = json.loads(
            (packet_dir(root2, pid2) / SUPERSEDED_FILE).read_text(
                encoding="utf-8"))
        self.assert_trace_consistency(
            record2, old_request2, new_request2, registered2, current2)
        self.assertEqual(
            set(record2.get("changed_fields") or set()), {"invariants"},
            msg=f"PD-24: la corrección --invariant debe quedar exactamente "
                f"en changed_fields: {record2!r}")

    def assert_trace_consistency(self, record, old_request, new_request,
                                 registered, current) -> None:
        """Traza dura PD-7+PD-24: base PD-7 y traza por campo coherente con
        el dif observable entre los dos REQUEST.json guardados."""
        expected_base = {
            "superseded_by": record.get("superseded_by"),
            "reason": REASON,
            "contract_sha256_old": registered,
            "contract_sha256_new": current,
        }
        for base_key, expected in expected_base.items():
            self.assertEqual(
                record.get(base_key), expected,
                msg=f"PD-24: {base_key} del registro durable: {record!r}")
        self.assertTrue(
            record.get("superseded_at"),
            msg=f"PD-24: superseded_at vacío: {record!r}")
        self.assertTrue(
            record.get("superseded_by"),
            msg=f"PD-24: superseded_by vacío (debe nombrar al sucesor): "
                f"{record!r}")

        conserved = record.get("conserved_fields")
        changed = record.get("changed_fields")
        self.assertIsInstance(
            conserved, list,
            msg=f"PD-24: el registro no lleva conserved_fields: {record!r}")
        self.assertIsInstance(
            changed, list,
            msg=f"PD-24: el registro no lleva changed_fields: {record!r}")
        conserved_set, changed_set = set(conserved), set(changed)
        self.assertEqual(
            conserved_set & changed_set, set(),
            msg=f"PD-24: conserved_fields y changed_fields deben ser "
                f"disjuntos: conserved={sorted(conserved_set)} "
                f"changed={sorted(changed_set)}")
        self.assertEqual(
            conserved_set | changed_set, set(ASSIGNMENT_UNIVERSE),
            msg=f"PD-24: la unión de conserved+changed es el universo de "
                f"campos del encargo; faltó "
                f"{sorted(set(ASSIGNMENT_UNIVERSE) - (conserved_set | changed_set))} "
                f"sobró {sorted((conserved_set | changed_set) - set(ASSIGNMENT_UNIVERSE))}")
        # Dif observable contra los dos REQUEST.json guardados.
        for field in ASSIGNMENT_UNIVERSE:
            differs = new_request.get(field) != old_request.get(field)
            self.assertEqual(
                field in changed_set, differs,
                msg=f"PD-24: el campo {field} debe figurar en "
                    f"{'changed' if differs else 'conserved'}_fields "
                    f"(cambió={differs}): conserved={sorted(conserved_set)} "
                    f"changed={sorted(changed_set)}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
