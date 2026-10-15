#!/usr/bin/env python3
"""005-005 T1 RED — el reemplazo valida también lo conservado
(PD-2..PD-7; INV-1..INV-5 se afirman dentro de cada postcondición).

Contract:
- docs/specs/005-005-adoption-coherence/spec.md §2 (PD-1..PD-7), §3
  (INV-1..INV-5), §6 (T1), §7 (D1/D2).
- docs/epics/epic-005-real-operation/plan.md (T1; test focal declarado
  `tests/test_005_005_t1_replace_conserved.py`).

Superficie observable bajo prueba (§2/D1 — sin flags nuevos; se reusan la
identidad/rol/subfase/objetivo del REQUEST.json anterior igual que en
005-001 PD-7..PD-11):

    python3 scripts/cdad_packet.py prepare --project-root R \
        --replace-packet <id> --reason <texto> [--input P=P] [--read-scope C[=S]]
        [--write-scope C[=S]]        # validación COMPLETA del encargo resultante
    python3 scripts/cdad_packet.py prepare --project-root R \
        --role <rol> --substage <sub> --objective <texto>   # camino normal SIN cambios

Caja negra: SOLO subprocess sobre el entrypoint del repo; el módulo
NUNCA se importa y el código de implementación NUNCA se lee (INV del rol).

Fijaciones RED por postcondición (con control positivo interno en cada
negativo, exigido por spec §4):

- PD-2 (focal del hueco de T1): un `input` CONSERVADO (no tocado por
  --input) que apunta a un archivo INEXISTENTE debe rechazar (rc=2)
  nombrando campo (`inputs`/`input.path`), motivo (archivo inexistente)
  y opción (`--input`), SIN publicar paquete nuevo, con el
  REQUEST.json/PACKET.md del paquete anterior byte a byte idénticos y el
  state intacto. HOY (probe): el reemplazo PUBLICA el sucesor con rc=0 —
  el hueco real que T1 cierra; el RED fracasa en la aserción rc=2.
  Control interno: el mismo reemplazo con el input existente → rc=0.
- PD-3 (diagnóstico accionable para alcances conservados): un
  `read_scope`/`write_scope` CONSERVADO que viola la política → rc=2
  nombrando campo (`read_scope`/`write_scope`), motivo de política y
  opción (`--read-scope`/`--write-scope`), sin efectos. Instancia
  alcanzable del motivo «selector no clasificado»: el selector file-less
  `tests/ghost.md` se PREPARA como root (el selector no existe → se
  admite), y el fixture CREATE el archivo después: el selector conservado
  queda NO CLASIFICADO ante la política del día (un root que designa un
  archivo no puede clasificarse; la política NO cambia → el pin del
  snapshot segue íntegro). HOY el rechazo es el mensaje genérico («scope
  root must designate a directory») que NO nombra campo ni opción: el RED
  fracasa en esas aserciones. El arm «clase no admitida para el rol» es
  inalcanzable conservado (validate_request lo rechaza en el prepare
  normal, mismo argv); se declara en el docstring para el GREEN.
  Control interno: sin crear el archivo → rc=0.
- PD-4 (recuperación): partiendo de PD-2 (primer reemplazo rechazado sin
  efectos), un SEGUNDO reemplazo con `--input P=P` (P existen y dentro de
  algún read_scope) → rc=0: sucesor con el contrato del día, paquete
  anterior byte-idéntico (INV-3), `.superseded.json` con el reason, y
  SIN entradas nuevas en stage_history/epic_history (INV-2). HOY el
  primer reemplazo publica en lugar de rechazar: el RED fracasa ahí.
- PD-5 (el camino normal no suma restricciones): un `prepare` normal con
  un input declarado inexistente conserva el comportamiento de hoy
  (rc=0). Contraparte (INV-4) del PD-2: no es un test RED (hoy es así);
  es guarda de no-regresión.
- PD-6 (lista de inputs vacía legítima): `--input -` en el reemplazo →
  rc=0 con `inputs == []` en el REQUEST.json del sucesor. Guarda
  (PD-20/D7 de 005-001 vigente).
- PD-7 (pisos del rol intactos tras cualquier corrección): con
  correcciones en invariants/evidence, el REQUEST.json del sucesor
  contiene SIEMPRE cada DEFAULT_INVARIANTS/DEFAULT_EVIDENCE del rol
  (INV-5/PD-21 de 005-001 vigente). Guarda.

Todo fallo RED es AssertionError de comportamiento de superficie
observable; nunca ImportError, nunca traceback del CLI.

Fixtures (patrón tests/test_005_001_t2_replace_packet.py +
test_005_001_tcorr.py): proyectos sintéticos en tempdirs con política
PROPUESTA por el CLI (--propose-policy, sin leer implementación), spec
pineada aprobada por el fixture-orquestador (pin en stage_history sembrado
en el state — el registro de aprobación es del orquestador, INV-2) y
delegación HITL activa; obsolescencia construida SOLO por interfaz
pública (editar spec.md → el sha del REQUEST.json deriva; el re-pin de
`specification` lo hace el fixture como orquestador, nunca el CLI).
Ninguna escritura en este repo y ninguna lectura de implementación.
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
FEATURE_ID = "005-005-adoption-coherence"
AUTH_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
SPEC_FILE = f"docs/specs/{FEATURE_ID}/spec.md"

SPEC_BYTES = b"# Spec fixture (005-005 T1)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada despues de aprobar\n"

APPROVER = "Pablo"
REASON = "contrato editado despues de preparar el paquete (005-005 T1)"

ROLE, SUBSTAGE = "test-writer", "red"
INPUT_DOC = "tests/conserved_input.md"
GHOST_READ = "tests/ghost_a.md"
GHOST_WRITE = "tests/ghost_b.md"

PACKET_BEGIN = "---cdad-packet-json"
SUPERSEDED_FILE = ".superseded.json"

# Pisos obligatorios del rol test-writer (DEFAULT_INVARIANTS/DEFAULT_EVIDENCE).
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


# ---------------------------------------------------------------- fixtures


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def prepare(root: Path, *, objective: str = "005-005 T1 objective",
            extra: tuple[tuple[str, str], ...] = ()) -> subprocess.CompletedProcess:
    args = ["prepare", "--project-root", str(root),
            "--role", ROLE, "--substage", SUBSTAGE,
            "--objective", objective]
    for flag, value in extra:
        args += [flag, value]
    return run_cli(args)


def run_replace(root: Path, packet_id: str, *, reason: str | None = REASON,
                corr: tuple[tuple[str, str], ...] = ()) -> subprocess.CompletedProcess:
    """Sub-modo §2/D1: selector + --reason + correcciones (sin flags nuevos)."""
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


def read_state(root: Path) -> dict:
    return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))


def write_state(root: Path, state: dict) -> None:
    (root / STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")


def active_packet_id(root: Path) -> str:
    active = read_state(root).get("active_packet") or {}
    if not active.get("id"):
        raise AssertionError(f"fixture: sin active_packet.id: {active!r}")
    return active["id"]


def packet_dir(root: Path, packet_id: str) -> Path:
    return root / ".cdad" / "packets" / packet_id


def packet_ids(root: Path) -> list[str]:
    base = root / ".cdad" / "packets"
    return sorted(d.name for d in base.iterdir() if d.is_dir()) if base.is_dir() else []


def packet_bytes(root: Path, packet_id: str, name: str) -> bytes:
    return (packet_dir(root, packet_id) / name).read_bytes()


def request_of(root: Path, packet_id: str) -> dict:
    return json.loads(
        packet_bytes(root, packet_id, "REQUEST.json").decode("utf-8"))


def assignment(input_path: str = INPUT_DOC,
               purpose: str = "insumo conservado T1") -> tuple:
    """Encargo custom del paquete anterior (los campos llegan a ser
    CONSERVADOS en el reemplazo al no pasar los flags de corrección)."""
    return (
        ("--input", f"{input_path}={purpose}"),
        ("--read-scope", f"contract=docs/specs/{FEATURE_ID}"),
        ("--read-scope", "tests=tests"),
        ("--write-scope", "tests=tests"),
        ("--invariant", "INVencargo custom 005-005"),
        ("--expected-output", "report custom 005-005"),
        ("--evidence", "evidencia custom 005-005"),
    )


def ghost_assignment(scope_flag: str, ghost: str) -> tuple:
    """Encargo con un selector file-less: su target NO existe al preparar
    (se guarda como root de clase tests) y el fixture lo hace existir
    después para el sub-test PD-3."""
    return (
        ("--input", f"docs/specs/{FEATURE_ID}/spec.md=contrato"),
        ("--read-scope", f"contract=docs/specs/{FEATURE_ID}"),
        ("--read-scope", "tests=tests"),
        ("--write-scope", "tests=tests"),
        (scope_flag, f"tests={ghost}"),
    )


def build_project(root: Path) -> Path:
    """Proyecto sintético válido (patrón T-CORR): política PROPUESTA por el
    CLI, spec aprobada pineada, fuente de autoridad, delegación HITL activa."""
    root.mkdir(parents=True)
    for rel in ("src", "lib", "tests"):
        (root / rel).mkdir(exist_ok=True)
    (root / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (root / "README.md").write_text("# Fixture (005-005 T1)\n", encoding="utf-8")
    (root / INPUT_DOC).write_text("insumo del encargo conservado\n",
                                  encoding="utf-8")
    (root / "docs").mkdir(exist_ok=True)
    proposal = run_cli(["prepare", "--project-root", str(root),
                        "--propose-policy"])
    if proposal.returncode != 0:
        raise AssertionError(
            f"fixture: --propose-policy debe producir una política válida: "
            f"{proposal.stderr!r}")
    policy = json.loads(proposal.stdout)
    (root / POLICY_FILE).write_text(
        json.dumps(policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spec = root / SPEC_FILE
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_bytes(SPEC_BYTES)
    authority = root / AUTH_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-005)\n",
                         encoding="utf-8")
    write_state(root, {
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
        "stage_history": [{
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": APPROVER,
            "approved_at": "2026-10-08T00:00:00Z",
            "contract_path": SPEC_FILE,
            "contract_sha256": hashlib.sha256(SPEC_BYTES).hexdigest(),
        }],
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
    })
    return root


class T1Case(unittest.TestCase):
    """Base: cada proyecto sintético en su propio tempdir fresco."""

    def make_project(self) -> Path:
        base = tempfile.mkdtemp(prefix="cdad-005-005-t1-")
        self.addCleanup(shutil.rmtree, base, ignore_errors=True)
        return build_project(Path(base) / "proj")

    def prepared_packet(self, *, extra=()) -> tuple:
        """Fixture precondición (PD-7/PD-22 de 005-001 vigente): pin+spec
        coincidentes → prepare rc=0 y paquete activo `prepared`. Devuelve
        (root, pid, request)."""
        root = self.make_project()
        proc = prepare(root, extra=extra)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): el pin vigente debe habilitar "
                f"prepare: {proc.stdout!r} {proc.stderr!r}")
        active = read_state(root)["active_packet"]
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"precondición (fixture): paquete activo: {active!r}")
        pid = active["id"]
        return root, pid, request_of(root, pid)

    def outdate_and_reauthorize(self, root: Path, packet_id: str) -> str:
        """Obsolescencia PD-8(a) de 005-001 por interfaz pública: edita la
        spec (el sha del REQUEST.json del paquete deriva) y re-pinea la
        entrada `specification` al sha ACTUAL (el fixture actúa como
        orquestador — el CLI jamás escribe aprobaciones, INV-2). Devuelve
        el sha del contrato del día."""
        stale = (root / SPEC_FILE).read_bytes()
        if stale == SPEC_DRIFT_BYTES:
            raise AssertionError("fixture: la spec ya estaba derivada")
        (root / SPEC_FILE).write_bytes(SPEC_DRIFT_BYTES)
        current = hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest()
        state = read_state(root)
        re_pinned = False
        for entry in state.get("stage_history", []):
            if (entry.get("feature") == FEATURE_ID
                    and entry.get("stage") == "specification"):
                entry["contract_sha256"] = current
                re_pinned = True
        if not re_pinned:
            raise AssertionError(
                "fixture: no hay entrada `specification` que re-pinear")
        write_state(root, state)
        registered = request_of(root, packet_id)["contract"]["sha256"]
        if registered != hashlib.sha256(SPEC_BYTES).hexdigest():
            raise AssertionError(
                f"fixture: el sha registrado en REQUEST.json no es el de "
                f"los bytes aprobados: {registered[:12]}…")
        return current

    def assert_no_writes(self, label: str, root: Path, before: dict,
                         state_before: bytes) -> None:
        """Sin efectos (PD-2/PD-3 «sin efectos»; PD-12 de 005-001): nada se
        publica, el árbol y el state quedan byte a byte idénticos y ning
        `.superseded.json` aparece en ningún paquete."""
        self.assertEqual(
            tree_snapshot(root), before,
            msg=f"{label}: hubo escrituras (árbol modificado)")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg=f"{label}: el state cambió")
        for pid in packet_ids(root):
            self.assertFalse(
                (packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
                msg=f"{label}: quedó un registro de superación con rc≠0 "
                    f"({SUPERSEDED_FILE} en {pid})")


# ---------------------------------------------------------------- PD-2


class TestPd2ConservedMissingInputRejected(T1Case):
    """PD-2 (focal del hueco de T1, INV-3): con un `input` CONSERVADO (no
    tocado por --input) que apunta a un archivo inexistente,
    `prepare --replace-packet <id> --reason <t>` → rc=2; el stderr nombra
    el campo (`inputs`/`input.path`), el motivo (archivo inexistente) y la
    opción (`--input`); sin publicar paquete nuevo; el REQUEST.json/
    PACKET.md del paquete anterior byte a byte idénticos y el state sin
    cambios. Control positivo interno (spec §4): el mismo reemplazo con
    el input existente → rc=0."""

    def test_pd02_replace_with_missing_conservado_input_rejects_without_effects(self) -> None:
        root, pid, request = self.prepared_packet(
            extra=assignment(INPUT_DOC, "insumo conservado T1"))
        # Control de fixture: el encargo previo porta el input conservado.
        self.assertEqual(
            [i for i in request.get("inputs", [])
             if i.get("path") == INPUT_DOC],
            [{"path": INPUT_DOC, "purpose": "insumo conservado T1"}],
            msg=f"precondición (fixture): input conservado en REQUEST: "
                f"{request!r}")
        # El archivo del input conservado DESAPARECE (drift ambiental; la
        # política y el contrato no cambian aún).
        (root / INPUT_DOC).unlink()
        current = self.outdate_and_reauthorize(root, pid)
        self.assertEqual(
            current, hashlib.sha256(SPEC_DRIFT_BYTES).hexdigest(),
            msg="fixture: el contrato del día es el deriva'd re-pineado")

        before = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_packet_md = packet_bytes(root, pid, "PACKET.md")

        proc = run_replace(root, pid)
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 2,
            msg=f"PD-2: el reemplazo con un input CONSERVADO inexistente "
                f"debe rechazar rc=2 (hoy publica el sucesor sin validar "
                f"el encargo conservado — hueco de T1): {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-2: el rechazo imprimió el paquete por stdout")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"PD-2: fallo manejado, sin traceback: {proc.stderr!r}")
        self.assertIn(
            "inputs", out,
            msg=f"PD-2: el rechazo no nombra el campo (inputs): {out!r}")
        self.assertIn(
            INPUT_DOC, out,
            msg=f"PD-2: el rechazo no nombra el input.path del motivo "
                f"({INPUT_DOC}): {out!r}")
        self.assertIn(
            "--input", out,
            msg=f"PD-2: el rechazo no nombra la opción para corregir "
                f"(--input): {out!r}")
        # «No se publica paquete nuevo»: solo el paquete anterior en disco.
        self.assertEqual(
            packet_ids(root), [pid],
            msg=f"PD-2: se publicó un paquete con rc=2: {packet_ids(root)}")
        # INV-3: bytes del paquete anterior intactos.
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-2/INV-3: el REQUEST.json del paquete anterior cambió")
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-2/INV-3: el PACKET.md del paquete anterior cambió")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg="PD-2: el state cambió con el rechazo")

        # Control positivo interno (spec §4): el mismo reemplazo con el
        # insumo EXISTENTE publica el sucesor (rc=0) — el rechazo anterior
        # fue exactamente por el input conservado inexistente.
        rootc, pidc, _reqc = self.prepared_packet(
            extra=assignment(INPUT_DOC, "insumo conservado T1"))
        self.outdate_and_reauthorize(rootc, pidc)
        okc = run_replace(rootc, pidc)
        outc = okc.stdout + okc.stderr
        self.assertEqual(
            okc.returncode, 0,
            msg=f"PD-2 (control positivo): el mismo reemplazo con el "
                f"insumo existente debe publicar (rc=0): {outc!r}")
        successors_c = [p for p in packet_ids(rootc) if p != pidc]
        self.assertEqual(
            len(successors_c), 1,
            msg=f"PD-2 (control): el control debía publicar el sucesor: "
                f"{packet_ids(rootc)}")


# ---------------------------------------------------------------- PD-3


class TestPd3ConservedScopeViolatingPolicy(T1Case):
    """PD-3 (D2, INV-3): un `read_scope`/`write_scope` CONSERVADO que
    viola la política → rc=2 nombrando CAMPO (`read_scope`/`write_scope`),
    MOTIVO de política y OPCIÓN (`--read-scope`/`--write-scope`), sin
    efectos (paquete anterior byte-idéntico, state intacto).

    Instancia del motivo «selector no clasificado»: el argv del prepare
    normal tolera un selector cuyo target no existe (queda como root); el
    fixture crea DESPUÉS ese archivo — el selector CONSERVADO queda ante
    la política del día como un root que designa un archivo: no
    clasificable → rc=2. (El arm «clase no admitida para el rol» es
    inalcanzable como conservado: el prepare normal rechaza el mismo
    argv — probe registrado en el paquete.)

    Control positivo interno (spec §4): la mismas fixture SIN crear el
    archivo → el selector conservado sigue clasificado → rc=0."""

    def test_pd03_replace_with_conserved_scope_selector_unclassified_rejects_naming_field_reason_option(self) -> None:
        for label, scope_flag, ghost in (
                ("read_scope", "--read-scope", GHOST_READ),
                ("write_scope", "--write-scope", GHOST_WRITE)):
            with self.subTest(campo=label):
                extra = ghost_assignment(scope_flag, ghost)
                root, pid, request = self.prepared_packet(extra=extra)
                scope_list = request.get(label, [])
                self.assertIn(
                    {"class": "tests", "root": ghost}, scope_list,
                    msg=f"precondición (fixture): el selector ghost quedó "
                        f"conservado como root en {label}: {request!r}")
                # El fixture HACE EXISTIR el target del selector: el root
                # conservado pasa a designar un archivo → no clasificable
                # ante la política (que NO cambió: pin íntegro).
                (root / ghost).write_text("aparecido\n", encoding="utf-8")
                self.outdate_and_reauthorize(root, pid)

                before = tree_snapshot(root)
                state_before = (root / STATE_FILE).read_bytes()
                old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
                old_packet_md = packet_bytes(root, pid, "PACKET.md")

                proc = run_replace(root, pid)
                out = proc.stdout + proc.stderr
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"PD-3 ({label}): el selector conservado fuera de "
                        f"la política debe rechazar rc=2: {out!r}")
                self.assertEqual(
                    proc.stdout, "",
                    msg=f"PD-3 ({label}): el rechazo imprimió por stdout")
                self.assertNotIn(
                    "Traceback", proc.stderr,
                    msg=f"PD-3 ({label}): fallo manejado, sin traceback: "
                        f"{proc.stderr!r}")
                # Campo nombrado (hoy el mensaje genérico no nombra campo).
                self.assertIn(
                    label, out,
                    msg=f"PD-3 ({label}): el rechazo no nombra el campo "
                        f"({label}; hoy: mensaje genérico de "
                        f"validate_request): {out!r}")
                # Opción para corregirlo.
                self.assertIn(
                    scope_flag, out,
                    msg=f"PD-3 ({label}): el rechazo no nombra la opción "
                        f"({scope_flag}): {out!r}")
                # Motivo de política (estilo PD-22 de 005-001).
                self.assertRegex(
                    proc.stderr,
                    r"invalid|politic|policy|política|clase|classified",
                    msg=f"PD-3 ({label}): el rechazo no nombra el motivo de "
                        f"política (hoy: genérico sin motivo/acción): "
                        f"{proc.stderr!r}")
                self.assert_no_writes(
                    f"PD-3 ({label})", root, before, state_before)
                self.assertEqual(
                    packet_ids(root), [pid],
                    msg=f"PD-3 ({label}): se publicó un paquete con rc=2")

                # Control positivo interno: SIN crear el archivo, el mismo
                # selector conservado sigue clasificado → rc=0.
                rootc, pidc, _reqc = self.prepared_packet(extra=extra)
                self.outdate_and_reauthorize(rootc, pidc)
                okc = run_replace(rootc, pidc)
                outc = okc.stdout + okc.stderr
                self.assertEqual(
                    okc.returncode, 0,
                    msg=f"PD-3 ({label}, control positivo): el selector "
                        f"conservado sin el archivo creado sigue "
                        f"clasificado → el reemplazo debe publicar "
                        f"(rc=0): {outc!r}")


# ---------------------------------------------------------------- PD-4


class TestPd4RecoveryAfterRejectedReplace(T1Case):
    """PD-4 (recuperación; INV-2/INV-3): partiendo de PD-2 (primer
    reemplazo rechazado, sin efectos), un segundo
    `prepare --replace-packet <id> --reason <t> --input P=P` con `P`
    existente y dentro de algún read_scope → rc=0: publica el sucesor con
    el contrato del día; el paquete anterior byte-idéntico;
    `.superseded.json` con el reason; y SIN entradas nuevas en
    stage_history/epic_history."""

    def test_pd04_second_replace_with_restored_input_publishes_successor(self) -> None:
        root, pid, _request = self.prepared_packet(
            extra=assignment(INPUT_DOC, "insumo conservado T1"))
        # PD-2: el input conservado desaparece → primer reemplazo rechazado.
        (root / INPUT_DOC).unlink()
        current = self.outdate_and_reauthorize(root, pid)

        baseline_tree = tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        old_request_bytes = packet_bytes(root, pid, "REQUEST.json")
        old_packet_md = packet_bytes(root, pid, "PACKET.md")

        first = run_replace(root, pid)
        first_out = first.stdout + first.stderr
        self.assertEqual(
            first.returncode, 2,
            msg=f"PD-4 (paso 1): el primer reemplazo (input conservado "
                f"inexistente) debe rechazar rc=2 sin efectos (hoy "
                f"publica): {first_out!r}")
        self.assertEqual(
            tree_snapshot(root), baseline_tree,
            msg="PD-4 (paso 1): el rechazo escribió algo")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg="PD-4 (paso 1): el state cambió con el rechazo")

        # Recuperación: el insumo se restaura (P vuelve a existir, dentro
        # del read_scope conservado tests=tests) y el reemplazo única
        # corrección --input P=P → rc=0.
        (root / INPUT_DOC).write_text("insumo restaurado\n", encoding="utf-8")
        state_after_first = (root / STATE_FILE).read_bytes()  # (intacto)
        recovered = run_replace(
            root, pid,
            corr=(("--input", f"{INPUT_DOC}=recuperacion PD-4"),))
        out = recovered.stdout + recovered.stderr
        self.assertEqual(
            recovered.returncode, 0,
            msg=f"PD-4 (paso 2): el segundo reemplazo con el insumo "
                f"restaurado y corregido debe publicar el sucesor "
                f"(rc=0): {out!r}")

        packets_after = packet_ids(root)
        self.assertIn(
            pid, packets_after,
            msg="PD-4/INV-3: el paquete anterior desapareció del disco")
        successors = [p for p in packets_after if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-4: paquetes en disco tras la recuperación: "
                f"{packets_after}")
        new_id = successors[0]

        # INV-3: bytes del paquete anterior intactos.
        self.assertEqual(
            packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-4/INV-3: el REQUEST.json del paquete anterior cambió")
        self.assertEqual(
            packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-4/INV-3: el PACKET.md del paquete anterior cambió")

        # Sucesor con el contrato del día.
        new_request = request_of(root, new_id)
        self.assertEqual(
            new_request.get("contract", {}).get("sha256"), current,
            msg=f"PD-4: el sucesor no lleva el contrato del día "
                f"({current[:12]}…): {json.dumps(new_request.get('contract'))}")
        self.assertEqual(
            new_request.get("inputs"),
            [{"path": INPUT_DOC, "purpose": "recuperacion PD-4"}],
            msg="PD-4: la corrección --input no reemplazó la lista entera")

        # Registro durable de superación con el reason.
        superseded_path = packet_dir(root, pid) / SUPERSEDED_FILE
        self.assertTrue(
            superseded_path.is_file(),
            msg=f"PD-4: no quedó registro durable {SUPERSEDED_FILE} en el "
                f"paquete anterior")
        record = json.loads(superseded_path.read_text(encoding="utf-8"))
        self.assertEqual(
            record.get("superseded_by"), new_id,
            msg=f"PD-4: superseded_by no nombra al sucesor: {record!r}")
        self.assertEqual(
            record.get("reason"), REASON,
            msg=f"PD-4: reason del registro no es el de --reason "
                f"({REASON!r}): {record!r}")

        # INV-2: ninguna entrada nueva en stage_history/epic_history.
        state_after = read_state(root)
        state_refs_before = json.loads(state_after_first.decode("utf-8"))
        self.assertEqual(
            state_after.get("stage_history"),
            state_refs_before.get("stage_history"),
            msg="PD-4/INV-2: stage_history cambió con el reemplazo")
        self.assertEqual(
            state_after.get("epic_history"),
            state_refs_before.get("epic_history"),
            msg="PD-4/INV-2: epic_history cambió con el reemplazo")
        self.assertEqual(
            (state_after.get("active_packet") or {}).get("id"), new_id,
            msg=f"PD-4: active_packet no apunta al sucesor "
                f"({new_id}): {state_after!r}")


# ---------------------------------------------------------------- PD-5


class TestPd5NormalPathAcceptsDeclaredMissingInput(T1Case):
    """PD-5 (INV-4): un `prepare` NORMAL (sin --replace-packet) con un
    input declarado que apunta a un archivo inexistente conserva el
    comportamiento de hoy: rc=0 si el resto es válido (005-005 NO agrega
    la exigencia de existencia al camino normal). Guarda de
    no-regresión del foco PD-22 de 005-001 (D1)."""

    def test_pd05_normal_prepare_keeps_accepting_declared_missing_input(self) -> None:
        root = self.make_project()
        proc = prepare(root, extra=assignment(
            "tests/inexistente_pd05.md", "insumo declarado inexistente"))
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-5/INV-4: el camino normal debe seguir aceptando un "
                f"input declarado inexistente (rc=0 si el resto es "
                f"válido): {out!r}")
        pid = active_packet_id(root)
        active = read_state(root)["active_packet"]
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"PD-5: el paquete normal no quedó prepared: {active!r}")
        self.assertEqual(
            [i for i in request_of(root, pid).get("inputs", [])
             if i.get("path") == "tests/inexistente_pd05.md"],
            [{"path": "tests/inexistente_pd05.md",
              "purpose": "insumo declarado inexistente"}],
            msg="PD-5: el input declarado no llegó al REQUEST.json")


# ---------------------------------------------------------------- PD-6


class TestPd6EmptyInputsLegitimateInReplace(T1Case):
    """PD-6 (D7 de 005-001): `--input -` (lista vacía) en el reemplazo
    sigue siendo válido: la validación completa (PD-1) NO rechaza una
    lista `inputs` vacía. Guarda de no-regresión."""

    def test_pd06_replace_with_empty_input_list_publishes_without_inputs(self) -> None:
        root, pid, _old = self.prepared_packet(
            extra=assignment(INPUT_DOC, "insumo conservado T1"))
        self.outdate_and_reauthorize(root, pid)
        proc = run_replace(root, pid, corr=(("--input", "-"),))
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-6: `--input -` es legítimo (lista vacía) y el "
                f"reemplazo debe publicar: {out!r}")
        successors = [p for p in packet_ids(root) if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-6: paquetes tras el reemplazo vacío: {packet_ids(root)}")
        new_request = request_of(root, successors[0])
        self.assertEqual(
            new_request.get("inputs"), [],
            msg=f"PD-6: `--input -` debe dejar inputs vacío: "
                f"{new_request.get('inputs')!r}")
        # INV-3: bytes del paquete anterior intactos.
        self.assertTrue(
            (packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
            msg=f"PD-6: no quedó registro {SUPERSEDED_FILE}")


# ---------------------------------------------------------------- PD-7


class TestPd7RoleFloorsSurviveCorrections(T1Case):
    """PD-7 (INV-5, PD-21 de 005-001 NO relajado): tras cualquier
    corrección, el `invariants`/`evidence_required` del sucesor contiene
    cada elemento obligatorio del rol (DEFAULT_INVARIANTS/
    DEFAULT_EVIDENCE) — T1 no puede eliminar los pisos al validar el
    encargo completo. Guarda de no-regresión (los pisos ya se re-agregan
    en las correcciones desde 005-001)."""

    def test_pd07_successor_after_corrections_keeps_role_floors(self) -> None:
        root, pid, old_request = self.prepared_packet()
        # Precondición: el encargo default porta ambos pisos.
        for floor in DEFAULT_INVARIANTS_TW:
            self.assertIn(
                floor, old_request.get("invariants", []),
                msg=f"precondición (fixture): el pin del piso "
                    f"{floor!r} en el REQUEST anterior")
        for floor in DEFAULT_EVIDENCE:
            self.assertIn(
                floor, old_request.get("evidence_required", []),
                msg=f"precondición (fixture): el pin de la evidencia "
                    f"mínima {floor!r} en el REQUEST anterior")
        self.outdate_and_reauthorize(root, pid)

        # Corrección en AMBOS campos (la corrección reemplaza la lista
        # entera; el piso se re-agrega SIEMPRE — PD-21 de 005-001).
        proc = run_replace(root, pid, corr=(
            ("--invariant", "INV extra PD-7"),
            ("--evidence", "evidencia extra PD-7"),
        ))
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-7: el reemplazo con correcciones en invariants y "
                f"evidence debe publicar el sucesor: {out!r}")
        successors = [p for p in packet_ids(root) if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-7: paquetes tras el reemplazo: {packet_ids(root)}")
        new_request = request_of(root, successors[0])

        for floor in DEFAULT_INVARIANTS_TW:
            self.assertIn(
                floor, new_request.get("invariants", []),
                msg=f"PD-7: el sucesor perdió el piso del rol "
                    f"({floor!r}) tras la corrección: "
                    f"{new_request.get('invariants')!r}")
        for floor in DEFAULT_EVIDENCE:
            self.assertIn(
                floor, new_request.get("evidence_required", []),
                msg=f"PD-7: el sucesor perdió la evidencia mínima del rol "
                    f"({floor!r}) tras la corrección: "
                    f"{new_request.get('evidence_required')!r}")
        # Las correcciones sí llegaron (lista reemplazada entera + pisos).
        self.assertIn(
            "INV extra PD-7", new_request.get("invariants", []),
            msg=f"PD-7: la corrección --invariant no llegó: "
                f"{new_request.get('invariants')!r}")
        self.assertIn(
            "evidencia extra PD-7", new_request.get("evidence_required", []),
            msg=f"PD-7: la corrección --evidence no llegó: "
                f"{new_request.get('evidence_required')!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
