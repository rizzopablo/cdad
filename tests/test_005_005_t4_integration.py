#!/usr/bin/env python3
"""005-005 T4 RED — integración desde una instalación aislada, sin rodeos
manuales (PD-18, INV-8) y procedencia in situ (PD-14), con la política única
presente en el árbol INSTALADO (PD-8/PD-9/PD-10 in situ).

Contract:
- docs/specs/005-005-adoption-coherence/spec.md §2 (PD-14, PD-18 y los PD de
  T1/T2 reafirmados end-to-end), §3 (INV-7, INV-8), §7 (D4/D5/D8).
- Encargo del paquete test-writer-red-004 (objetivo T4): secuencia
  caja negra sobre una instalación REAL de este repo en una raíz AISLADA
  (NUNCA HOME), con el precedente de tests/test_003_002_t4_integration.py
  (CDAD_INSTALL_ROOT en tempdir EXISTENTE + HOME/XDG temporales +
  `bash <copia del producto>/install.sh --basic`).

Superficie observable (sin flags nuevos; todo por subprocess contra el
CLI INSTALADO `.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py`):

    prepare --project-root R --role r --substage s --objective t   # paso 1
    prepare --project-root R --replace-packet <id> --reason t [--input P=P]
    prepare --project-root R --record-dispatch <id> --attempt-id a --input obs

La copia del producto se hace MECÁNICAMENTE (shutil.copytree/copy2, sin
leer contenido: precedente 004-002 T5/T7 «copiada sin inspección: es
fixture, no lectura de implementación»); el test no importa ni lee
módulos de implementación (INV del rol: skills/, scripts/ e install.sh son
implementación, fuera del read scope del role).

Fijaciones RED (honesto; un fallo es AssertionError de comportamiento,
nunca ImportError ni traceback):

- PD-18 (paso 1: prepare) — GUARD (camino vigente): la instalación aislada
  publica el paquete y queda `prepared`/despachable.
- PD-18 (paso 2: reemplazo con validación COMPLETA T1) — GUARD (T1 GREEN):
  un input CONSERVADO inexistente → rc=2 campo/motivo/opción y SIN efectos;
  la corrección explícita `--input` válido → rc=0 (sucesor publicado).
- PD-18 (paso 3: despacho con validación proporcional T2) — GUARD (T2
  GREEN): `prepare --record-dispatch` rc=0 y «Test evidence policy» +
  paquete canónico de GREEN alineados también en el árbol INSTALADO
  (PD-8/PD-9/PD-10 in situ: política única, sin «required full regression
  suite», consumidores referenciando).
- PD-14 (paso 4: procedencia in situ) — FOCAL RED: la instalación aislada
  debe declarar su versión/commit EN SU RAÍZ y el manifiesto `.cdad-derived.json`
  publicado por ese mismo CLI debe declarar `source_version` IGUAL a esa
  versión. HOY (probe): `install.sh --basic` NO escribe ninguna declaración
  de versión en la raíz instalada (ni campo en `.cdad-install-manifest.json`,
  ni marcador raíz) y el CLI publica `source_version: null` — la versión
  cargada queda INVERIFICABLE por el artefacto (INV-7: procedencia sin
  evidencia). El RED fracasa exactamente ahí: AssertionError con
  contador-evidencia (lista de candidatos raíz escaneados).
- INV-8 — guarda estructural: NADA del test instala/activa en HOME (raíz de
  install, HOME de cada subproceso y HOME sierven aislados en tempdir, y el
  helper rechaza cualquier HOME igual al real).

Mapa test → postcondición:
  test_t4_pd18_walkthrough_prepares_replaces_and_dispatches_from_isolated_install
    -> PD-18 (pasos 1..3) + INV-8 (guarda estructural del recorrido)
  test_t4_pd14_isolated_install_declares_version_and_manifest_declares_it
    -> PD-14 (+ INV-7 coherencia del origen con el árbol instalado)
  test_t4_pd08_policy_unique_in_installed_tree
  test_t4_pd09_no_full_suite_per_green_in_installed_tree
  test_t4_pd10_installed_green_packet_aligned
    -> PD-8/PD-9/PD-10 (in situ, sobre el árbol instalado)
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.product_staging import run_scoped_base

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"  # staging del producto

# Patrón de instalación aislada (tests/test_003_002_t4_integration.py).
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIME = "opencode"
# 006-003 U1/PD-1f: el generador no tiene `--profile`; `PROFILE = "basic"` se
# retiró con el argumento. `--basic` sobrevive solo como alias deprecado del
# instalador (D1), que es lo que FLAG ejercita.
FLAG = "--basic"
SKILL_REL = Path(".config") / RUNTIME / "skills" / "cdad-cycle"
INSTALLED_PACKET_CLI_REL = SKILL_REL / "scripts" / "cdad_packet.py"
INSTALLED_REFS_REL = SKILL_REL / "references"
INSTALLED_PACKETS_REL = SKILL_REL / "packets"
INSTALL_MANIFEST = ".cdad-install-manifest.json"

EPIC_ID = "epic-005-real-operation"
FEATURE_ID = "005-005-adoption-coherence"
AUTH_REF = f"docs/epics/{EPIC_ID}/execution.md"
POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
SPEC_REL = f"docs/specs/{FEATURE_ID}/spec.md"

SPEC_BYTES = b"# Spec fixture (005-005 T4 RED)\n"
SPEC_DRIFT_BYTES = SPEC_BYTES + b"# linea editada despues de aprobar\n"

APPROVER = "Pablo"
REASON = "contrato editado despues de preparar el paquete (005-005 T4)"
ROLE, SUBSTAGE = "test-writer", "red"
CONSERVED_INPUT = "tests/conserved_input.md"
ATTEMPT_ID = "attempt-t4-red-001"

PACKET_BEGIN = "---cdad-packet-json"
SUPERSEDED_FILE = ".superseded.json"

DERIVED_DIR = ".opencode/agents"
DERIVED_MANIFEST = ".cdad-derived.json"

# Esquema cerrado del registro de despacho (003-002 T4, observación).
OBSERVATION = {
    "runtime": RUNTIME,
    "model_configured": "glm-5.3-flash",
    "model_reported": "glm-5.3-flash",
    "session": "ses-005-005-t4-red-0001",
    "started_at": "2026-10-09T00:00:00Z",
    "provenance": {
        "runtime": "reported by runtime",
        "model_reported": "orchestrator",
        "session": "orchestrator",
    },
}

# T2 in situ (PD-9): afirmaciones de frecuencia por GREEN prohibidas.
PD9_FORBIDDEN = re.compile(
    r"(?i)once per GREEN|full suite per GREEN|required full regression suite")
POLICY_REFERENCE = re.compile(r"(?i)test evidence policy|evidence policy|\bPD-8\b")
POLICY_HEADING = re.compile(r"^#{1,6}\s+Test evidence policy\s*$")


# ---------------------------------------------------------------- fixtures


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _IsolatedInstall:
    """Instalación aislada del producto (UNA por proceso, cacheada).

    Copia mecánica del producto (PRODUCT_ENTRIES) a un tempdir + staging
    (`cdad-generate.py`) + `install.sh --basic` con CDAD_INSTALL_ROOT en un
    tempdir EXISTENTE. Jamás toca el HOME real: HOME del staging/install es
    `iso_home` (tempdir vacío) y la raíz de instalación es un tempdir.
    """

    def __init__(self, base: Path) -> None:
        self.base = base
        self.product = base / "product"
        self.product.mkdir(parents=True, exist_ok=True)
        for entry in PRODUCT_ENTRIES:
            source = REPO_ROOT / entry
            destination = self.product / entry
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        self.home = base / "iso-home"
        self.home.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_") or key == "CDAD_OPENCODE_AGENTS_DIR":
                env.pop(key, None)
        staging_result = subprocess.run(
            [sys.executable, str(GENERATOR), "--runtime", RUNTIME,
             "--stack", "odoo", "--out",
             str(self.product / "build" / "staging")],
            cwd=str(REPO_ROOT), env=env | {"HOME": str(self.home)},
            text=True, capture_output=True, check=False)
        self.staging_result = staging_result
        self.install_root = base / "install-root"
        self.install_root.mkdir(parents=True, exist_ok=True)
        self.install_result = subprocess.run(
            ["bash", str(self.product / "install.sh"), FLAG],
            cwd=str(self.product),
            env=env | {"HOME": str(self.home),
                       "CDAD_INSTALL_ROOT": str(self.install_root),
                       "CDAD_SKILL_EXTRA_DIRS": ""},
            text=True, capture_output=True, check=False)
        self.packet_cli = self.install_root / INSTALLED_PACKET_CLI_REL

    def assert_ready(self) -> None:
        assert self.staging_result.returncode == 0, (
            "precondición (fixture): el staging del producto debe tener "
            f"éxito: {self.staging_result.returncode} "
            f"{self.staging_result.stderr!r}")
        assert self.install_result.returncode == 0, (
            "precondición (fixture): la instalación aislada (--basic) debe "
            f"tener éxito: {self.install_result.returncode} "
            f"{self.install_result.stderr!r}")
        assert self.packet_cli.is_file(), (
            "precondición (fixture): la instalación debe exponer el CLI de "
            f"paquetes en {self.packet_cli}")
        agents_dir = self.install_root / ".config" / "opencode" / "agents"
        assert agents_dir.is_dir() and any(agents_dir.glob("cdad-*.md")), (
            "precondición (fixture): la instalación debe exponer los agentes "
            f"del runtime en {agents_dir} (origen de derivados del árbol "
            "instalado, PD-12 orden 3)")


_INSTALL: _IsolatedInstall | None = None
_INSTALL_BASE: tempfile.TemporaryDirectory | None = None


def install() -> _IsolatedInstall:
    global _INSTALL, _INSTALL_BASE
    if _INSTALL is None:
        _INSTALL_BASE = tempfile.TemporaryDirectory(
            prefix="cdad-005-005-t4-red-", dir=run_scoped_base())
        atexit.register(_INSTALL_BASE.cleanup)
        _INSTALL = _IsolatedInstall(Path(_INSTALL_BASE.name).resolve())
    return _INSTALL


# ------------------------------------------------------------------- base


class T4Case(unittest.TestCase):
    """Base: instalación aislada cacheada + proyecto sintético por test."""

    maxDiff = None

    def setUp(self) -> None:
        self._install = install()
        self._install.assert_ready()
        self._tmp = tempfile.mkdtemp(prefix="cdad-005-005-t4-proj-")
        self.addCleanup(shutil.rmtree, self._tmp, ignore_errors=True)
        self.base = Path(self._tmp).resolve()
        self.warehouse_home = self.base / "warehouse-home"
        self._homes_used: list[str] = []

    # -- corridas del CLI instalado -----------------------------------------

    def run_packet(self, args: list[str], *, home: Path | None = None,
                   cwd: Path | None = None) -> subprocess.CompletedProcess:
        """CLI INSTALADO por subprocess (caja negra).

        INV-8: el HOME del subproceso SIEMPRE es aislado (raíz instalada o
        tempdir del test) y se rechaza explícitamente el HOME real; el
        `CDAD_OPENCODE_AGENTS_DIR` ambiente NUNCA se hereda (la elección del
        origen es parte del comportamiento bajo prueba).
        """
        home = home if home is not None else self.warehouse_home
        home.mkdir(parents=True, exist_ok=True)
        resolved = Path(home).resolve()
        self.assertNotEqual(
            resolved, Path.home().resolve(),
            "INV-8: ninguna corrida del test debe ejecutarse con el HOME "
            "real del dueño")
        self._homes_used.append(str(resolved))
        env = dict(os.environ)
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_") or key == "CDAD_OPENCODE_AGENTS_DIR":
                env.pop(key, None)
        env["HOME"] = str(resolved)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        return subprocess.run(
            [sys.executable, str(self._install.packet_cli), *args],
            capture_output=True, text=True,
            cwd=str(cwd) if cwd else str(self.base), env=env,
            stdin=subprocess.DEVNULL)

    def out(self, proc: subprocess.CompletedProcess) -> str:
        return proc.stdout + proc.stderr

    # -- proyecto sintético (fixture-orquestador siembra aprobaciones) -------

    def make_project(self) -> Path:
        root = self.base / "project"
        root.mkdir(parents=True, exist_ok=True)
        for rel in ("src", "lib", "tests"):
            (root / rel).mkdir(exist_ok=True)
        (root / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        (root / "README.md").write_text("# Fixture (005-005 T4)\n",
                                        encoding="utf-8")
        (root / CONSERVED_INPUT).write_text("insumo conservado T4\n",
                                            encoding="utf-8")
        proposal = self.run_packet(
            ["prepare", "--propose-policy", "--project-root", str(root)])
        self.assertEqual(
            proposal.returncode, 0,
            msg=f"precondición (fixture): --propose-policy debe producir "
                f"una política válida: {self.out(proposal)!r}")
        (root / POLICY_FILE).parent.mkdir(parents=True, exist_ok=True)
        (root / POLICY_FILE).write_text(proposal.stdout, encoding="utf-8")
        spec = root / SPEC_REL
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
            "stage_history": [{
                "feature": FEATURE_ID,
                "stage": "specification",
                "approved_by": APPROVER,
                "approved_at": "2026-10-09T00:00:00Z",
                "contract_path": SPEC_REL,
                "contract_sha256": _sha256_bytes(SPEC_BYTES),
            }],
            "approver": APPROVER,
            "last_updated": "2026-10-09T00:00:00Z",
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
        (root / STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        return root

    def assignment(self, input_path: str = CONSERVED_INPUT,
                   purpose: str = "insumo conservado T4") -> list[str]:
        return [
            "--input", f"{input_path}={purpose}",
            "--read-scope", f"contract=docs/specs/{FEATURE_ID}",
            "--read-scope", "tests=tests",
            "--write-scope", "tests=tests",
            "--invariant", "INVencargo custom 005-005 T4",
            "--expected-output", "report custom 005-005 T4",
            "--evidence", "evidencia custom 005-005 T4",
        ]

    def prepare(self, root: Path, extra: list[str] | None = None,
                home: Path | None = None) -> subprocess.CompletedProcess:
        args = ["prepare", "--project-root", str(root),
                "--role", ROLE, "--substage", SUBSTAGE,
                "--objective", "T4 objective"]
        return self.run_packet(args + (extra or []), home=home)

    def replace(self, root: Path, packet_id: str, corr: list[str] | None = None
                ) -> subprocess.CompletedProcess:
        return self.run_packet(
            ["prepare", "--project-root", str(root),
             "--replace-packet", packet_id, "--reason", REASON, *(corr or [])])

    def observe_dispatch(self, root: Path, packet_id: str
                         ) -> subprocess.CompletedProcess:
        obs_path = root / ".cdad" / "inbox" / "observation-t4.json"
        obs_path.parent.mkdir(parents=True, exist_ok=True)
        obs_path.write_text(
            json.dumps(OBSERVATION, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return self.run_packet([
            "prepare", "--record-dispatch", packet_id,
            "--project-root", str(root),
            "--attempt-id", ATTEMPT_ID, "--input", str(obs_path)])

    # -- oráculos del store del fixture --------------------------------------

    def read_state(self, root: Path) -> dict:
        return json.loads((root / STATE_FILE).read_text(encoding="utf-8"))

    def active_packet(self, root: Path) -> dict:
        return self.read_state(root).get("active_packet") or {}

    def packet_dir(self, root: Path, packet_id: str) -> Path:
        return root / ".cdad" / "packets" / packet_id

    def packet_ids(self, root: Path) -> list[str]:
        base = root / ".cdad" / "packets"
        if not base.is_dir():
            return []
        return sorted(p.name for p in base.iterdir() if p.is_dir())

    def request_of(self, root: Path, packet_id: str) -> dict:
        return json.loads((self.packet_dir(root, packet_id)
                           / "REQUEST.json").read_text(encoding="utf-8"))

    def packet_bytes(self, root: Path, packet_id: str, name: str) -> bytes:
        return (self.packet_dir(root, packet_id) / name).read_bytes()

    def tree_snapshot(self, root: Path) -> dict[str, bytes | None]:
        snapshot: dict[str, bytes | None] = {}
        for path in sorted(root.rglob("*")):
            rel = path.relative_to(root).as_posix()
            snapshot[rel] = path.read_bytes() if path.is_file() else None
        return snapshot

    def outdate_and_reauthorize(self, root: Path, packet_id: str) -> str:
        """Obsolescencia PD-8(a) de 005-001 por interfaz pública + re-pin
        del `specification` (el fixture actúa como ORQUESTADOR; el CLI jamás
        escribe aprobaciones, INV-2)."""
        current = self.read_state(root).get("active_packet") or {}
        if current.get("id") != packet_id:
            raise AssertionError(
                f"fixture: el paquete {packet_id} no está activo: {current!r}")
        self.assertEqual(
            current.get("status"), "prepared",
            msg=f"fixture: el paquete debe estar prepared para el reemplazo: "
                f"{current!r}")
        spec = root / SPEC_REL
        spec.write_bytes(SPEC_DRIFT_BYTES)
        drift_sha = _sha256_bytes(SPEC_DRIFT_BYTES)
        state = self.read_state(root)
        re_pinned = False
        for entry in state.get("stage_history", []):
            if (entry.get("feature") == FEATURE_ID
                    and entry.get("stage") == "specification"):
                entry["contract_sha256"] = drift_sha
                re_pinned = True
        if not re_pinned:
            raise AssertionError(
                "fixture: no hay entrada `specification` que re-pinear")
        (root / STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        return drift_sha

    def assert_no_writes(self, label: str, root: Path, before: dict,
                         state_before: bytes) -> None:
        self.assertEqual(
            self.tree_snapshot(root), before,
            msg=f"{label}: hubo escrituras (árbol modificado)")
        self.assertEqual(
            (root / STATE_FILE).read_bytes(), state_before,
            msg=f"{label}: el state cambió")


# --------------------------------------------------------- PD-18 (pasos 1..3)


class TestT4Pd18Walkthrough(T4Case):
    """PD-18: secuencia end-to-end caja negra con el CLI de la instalación
    aislada: (1) `prepare` de un encargo → rc=0 y paquete publicado y
    despachable; (2) reemplazo con la validación COMPLETA de T1 (input
    conservado inexistente → rc=2 campo/motivo/opción, sin efectos;
    corrección explícita → rc=0); (3) despacho con la validación
    proporcional (`--record-dispatch` rc=0). INV-8 guard: todo lo corrido
    vive en tempdir; NADA instala o activa en HOME."""

    def test_t4_pd18_walkthrough_prepares_replaces_and_dispatches_from_isolated_install(self) -> None:
        root = self.make_project()

        # ---- paso 1: prepare (el CLI instalado sobre el proyecto sintético)
        proc = self.prepare(root, extra=self.assignment())
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-18 (1): `prepare` con el CLI instalado debe publicar el "
                f"encargo: {self.out(proc)!r}")
        self.assertNotIn("Traceback", self.out(proc),
                         msg="PD-18 (1): prepare terminó con traceback")
        active = self.active_packet(root)
        self.assertEqual(
            active.get("status"), "prepared",
            msg=f"PD-18 (1): el paquete publicado debe quedar despachable "
                f"(prepared): {self.read_state(root)!r}")
        pid = active.get("id")
        self.assertTrue(pid, msg=f"PD-18 (1): sin active_packet.id: {active!r}")
        for rel in ("REQUEST.json", "PACKET.md"):
            self.assertTrue(
                (self.packet_dir(root, pid) / rel).is_file(),
                msg=f"PD-18 (1): el paquete publicado no contiene {rel} "
                    f"(paquete despachable): {self.packet_dir(root, pid)}")
        self.assertIn(PACKET_BEGIN,
                      self.packet_bytes(root, pid, "PACKET.md").decode("utf-8", errors="replace"),
                      msg="PD-18 (1): el PACKET.md publicado no es un paquete canónico")

        # ---- paso 2: reemplazo con validación COMPLETA (T1) --------------
        conserved = root / CONSERVED_INPUT
        self.assertTrue(
            conserved.is_file(),
            msg="precondición (fixture): el input conservado existe")
        conserved.unlink()
        self.outdate_and_reauthorize(root, pid)

        before = self.tree_snapshot(root)
        state_before = (root / STATE_FILE).read_bytes()
        old_request_bytes = self.packet_bytes(root, pid, "REQUEST.json")
        old_packet_md = self.packet_bytes(root, pid, "PACKET.md")

        first = self.replace(root, pid)
        out = self.out(first)
        self.assertEqual(
            first.returncode, 2,
            msg=f"PD-18 (2, T1 PD-2): el reemplazo con un input CONSERVADO "
                f"inexistente debe rechazar rc=2 con campo/motivo/opción "
                f"(hoy GREEN: valida también lo conservado): {out!r}")
        self.assertNotIn("Traceback", first.stderr,
                         msg="PD-18 (2): rechazo manejado, sin traceback")
        self.assertIn("inputs", out,
                      msg=f"PD-18 (2): el rechazo no nombra el campo "
                          f"(inputs): {out!r}")
        self.assertIn(CONSERVED_INPUT, out,
                      msg=f"PD-18 (2): el rechazo no nombra el motivo "
                          f"({CONSERVED_INPUT} inexistente): {out!r}")
        self.assertIn("--input", out,
                      msg=f"PD-18 (2): el rechazo no nombra la opción para "
                          f"corregir (--input): {out!r}")
        self.assert_no_writes("PD-18 (2)", root, before, state_before)
        self.assertEqual(
            self.packet_ids(root), [pid],
            msg=f"PD-18 (2): el rechazo publicó un paquete con rc=2: "
                f"{self.packet_ids(root)}")
        self.assertEqual(
            self.packet_bytes(root, pid, "REQUEST.json"), old_request_bytes,
            msg="PD-18 (2)/INV-3: el REQUEST.json del paquete anterior cambió")
        self.assertEqual(
            self.packet_bytes(root, pid, "PACKET.md"), old_packet_md,
            msg="PD-18 (2)/INV-3: el PACKET.md del paquete anterior cambió")

        # corrección explícita (--input válido, dentro del read_scope;
        # el contrato del día y el re-pin ya quedaron fijados arriba).
        fixed = self.run_packet([
            "prepare", "--project-root", str(root),
            "--replace-packet", pid, "--reason", REASON,
            "--input", f"{SPEC_REL}=contrato vigente T4"])
        self.assertEqual(
            fixed.returncode, 0,
            msg=f"PD-18 (2, T1 PD-4): la corrección explícita con el insumo "
                f"existente debe publicar el sucesor (rc=0): "
                f"{self.out(fixed)!r}")
        successors = [p for p in self.packet_ids(root) if p != pid]
        self.assertEqual(
            len(successors), 1,
            msg=f"PD-18 (2): paquetes en disco tras la corrección: "
                f"{self.packet_ids(root)}")
        new_id = successors[0]
        self.assertEqual(
            self.request_of(root, new_id).get("inputs"),
            [{"path": SPEC_REL, "purpose": "contrato vigente T4"}],
            msg="PD-18 (2): la corrección --input no dejó el insumo existente")
        self.assertEqual(
            self.request_of(root, new_id).get("contract", {}).get("sha256"),
            _sha256_bytes(SPEC_DRIFT_BYTES),
            msg="PD-18 (2): el sucesor no lleva el contrato del día")
        self.assertTrue(
            (self.packet_dir(root, pid) / SUPERSEDED_FILE).is_file(),
            msg=f"PD-18 (2): no quedó el registro durable {SUPERSEDED_FILE}")
        self.assertEqual(
            (self.active_packet(root) or {}).get("id"), new_id,
            msg=f"PD-18 (2): active_packet no apunta al sucesor {new_id}")

        # ---- paso 3: despacho con la validación proporcional (T2) ---------
        record = self.observe_dispatch(root, new_id)
        self.assertEqual(
            record.returncode, 0,
            msg=f"PD-18 (3): `prepare --record-dispatch` con el CLI instalado "
                f"debe registrar el despacho (rc=0): {self.out(record)!r}")
        self.assertNotIn("Traceback", self.out(record),
                         msg="PD-18 (3): record-dispatch terminó con traceback")
        state_after = self.read_state(root)
        self.assertEqual(
            (state_after.get("active_packet") or {}).get("status"),
            "dispatched",
            msg=f"PD-18 (3): el paquete despachable debe quedar despachado: "
                f"{state_after.get('active_packet')!r}")
        self.assertEqual(
            (state_after.get("active_packet") or {}).get("id"), new_id,
            msg="PD-18 (3): el paquete despachado no es el sucesor corregido")

        # ---- INV-8 (guarda estructural): nada del recorrido live fuera del
        # tempdir y ninguna corrida usó el HOME real (run_packet ya lo
        # fuerza en cada llamada).
        real_home = Path.home().resolve()
        for used in self._homes_used:
            self.assertNotEqual(
                Path(used), real_home,
                msg=f"INV-8: una corrida del recorrido usó el HOME real: "
                    f"{used}")
        self.assertTrue(
            str(root).startswith(str(self.base)) and
            str(self._install.install_root).startswith(str(self._install.base)),
            msg="INV-8: la raíz del proyecto o la de instalación escaparon "
                "del tempdir del test")


# -------------------------------------------------------------------- PD-14


def _is_versionish(value: str) -> bool:
    value = value.strip().strip('"\'')
    if re.fullmatch(r"[0-9a-f]{7,64}", value):
        return True
    return bool(re.fullmatch(r"v?\d+(\.\d+)+([+_-]?\w+)?|v\d+", value))


def _maybe_json_version(data: object) -> str | None:
    if isinstance(data, dict):
        for key in ("source_version", "source_commit", "version", "commit",
                    "commit_sha", "commit_id"):
            value = data.get(key)
            if isinstance(value, str) and _is_versionish(value):
                return value
    return None


def _version_declaration_in_file(path: Path) -> str | None:
    try:
        if path.stat().st_size > 131072:
            return None
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        declared = _maybe_json_version(json.loads(text))
        if declared:
            return declared
    except (json.JSONDecodeError, ValueError):
        pass
    stripped = [line.strip() for line in text.splitlines() if line.strip()]
    if len(stripped) == 1 and _is_versionish(stripped[0]):
        return stripped[0]
    return None


def find_version_declaration(install_root: Path) -> tuple[str | None, list[str]]:
    """Escaneo caja negra de la DECLARACIÓN de versión/commit de la raíz de
    la instalación (PD-14: «la instalación declara su versión/commit en su
    raíz»). Acepta cualquier artefacto declarativo: un marcador de
    texto plano (`version.txt` etc.) o un campo version/commit de un JSON
    de raíz (p. ej. `.cdad-install-manifest.json`); NO asume un formato.
    Devuelve (versión declarada, contador-evidencia de candidatos)."""
    candidates: list[Path] = []
    for path in sorted(install_root.rglob("*")):
        if path.is_dir():
            continue
        depth = len(path.relative_to(install_root).parts)
        if depth <= 2 or "version" in path.name.lower():
            candidates.append(path)
    declared: str | None = None
    evidence: list[str] = []
    for path in candidates:
        value = _version_declaration_in_file(path)
        evidence.append(
            f"{'-> ' + value if value else '–  sin declaración'} "
            f"[{path.relative_to(install_root).as_posix()}]")
        if value and declared is None:
            declared = value
    return declared, evidence


class TestT4Pd14ProvenanceInSitu(T4Case):
    """PD-14 (in situ, INV-7): con el CLI de la instalación aislada corriendo
    en su propio mundo (HOME = raíz instalada aislada, NUNCA el HOME real,
    sin variable de origen ni registro), `prepare` publica el manifiesto de
    agentes derivados con `source_version` IGUAL a la versión/commit que la
    instalación aislada declara EN SU RAÍZ. La versión cargada por una
    sesión debe ser verificable desde el artefacto publicado."""

    def test_t4_pd14_isolated_install_declares_version_and_manifest_declares_it(self) -> None:
        root = self.make_project()
        proc = self.prepare(root, home=self._install.install_root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-14 (precondición): el prepare con el CLI de la "
                f"instalación aislada debe correr (rc=0): {self.out(proc)!r}")

        manifest_path = root / DERIVED_DIR / DERIVED_MANIFEST
        self.assertTrue(
            manifest_path.is_file(),
            msg=f"PD-14 (precondición): el CLI instalado debe publicar el "
                f"manifiesto de derivados en {manifest_path} (el origen "
                f"resuelto es la instalación aislada misma, PD-12 orden 3): "
                f"{self.out(proc)!r}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        expected_source = str(
            self._install.install_root / ".config" / "opencode" / "agents")
        self.assertEqual(
            manifest.get("source_dir"), expected_source,
            msg=f"PD-14/INV-7 (precondición): el origen resuelto debe ser la "
                f"instalación aislada ({expected_source!r}): "
                f"{manifest.get('source_dir')!r}")

        declared, evidence = find_version_declaration(
            self._install.install_root)
        self.assertIsNotNone(
            declared,
            msg="PD-14: la instalación aislada NO declara su versión/commit "
                "en su raíz — el producto instalado es una copia sin "
                "procedencia (sin campo de versión en el manifiesto de "
                "instalación ni marcador raíz), de modo que `source_version` "
                "no puede declarar la versión cargada: candidatos "
                "escaneados en la raíz instalada:\n  "
                + "\n  ".join(evidence))
        self.assertEqual(
            manifest.get("source_version"), declared,
            msg=f"PD-14: el manifiesto de derivados publicado por el CLI de "
                f"la instalación aislada declara "
                f"source_version={manifest.get('source_version')!r} que no "
                f"es la versión que la instalación declara en su raíz "
                f"({declared!r}) — qué versión cargó una sesión queda "
                f"inverificable (INV-7)")


# ------------------------------------------------- PD-8/PD-9/PD-10 (in situ)


class TestT4InstalledPolicyDocs(T4Case):
    """La política única de evidencia (T2) debe atravesar la instalación:
    los documentos que el CLI instalado ofrece a los roles llevan la sección
    «Test evidence policy» y ningún documento instalado afirma la suite
    completa por GREEN (sin «required full regression suite»).

    Un test por postcondición (criterio de aceptación de la spec):
    PD-8 / PD-9 / PD-10, cada uno con su método sobre el árbol instalado.
    """


    def _installed_document(self, rel: Path) -> str:
        path = self._install.install_root / rel
        self.assertTrue(
            path.is_file(),
            msg=f"precondición (in situ): documento requerido no existe en el "
                f"árbol instalado: {path}")
        return path.read_text(encoding="utf-8")

    def test_t4_pd08_policy_unique_in_installed_tree(self) -> None:
        stage3 = self._installed_document(
            INSTALLED_REFS_REL / "stage-3-tdd.md")
        headings = [line.strip() for line in stage3.splitlines()
                    if POLICY_HEADING.match(line.strip())]
        self.assertEqual(
            len(headings), 1,
            msg="PD-8 (in situ): la sección de política de evidencia debe "
                f"existir y ser ÚNICA en el árbol instalado "
                f"(headings: {headings!r})")

    def test_t4_pd09_no_full_suite_per_green_in_installed_tree(self) -> None:
        offenders: list[str] = []
        for scanned in (INSTALLED_REFS_REL, INSTALLED_PACKETS_REL):
            base = self._install.install_root / scanned
            self.assertTrue(
                base.is_dir(),
                msg=f"PD-9 (in situ): el árbol instalado debe incluir "
                    f"{scanned}")
            for path in sorted(base.rglob("*")):
                if not path.is_file():
                    continue
                if path.suffix not in {".md", ".txt", ""}:
                    continue
                if PD9_FORBIDDEN.search(path.read_text(encoding="utf-8")):
                    offenders.append(
                        path.relative_to(self._install.install_root).as_posix())
        self.assertEqual(
            offenders, [],
            msg="PD-9 (in situ): quedan afirmaciones de frecuencia por GREEN "
                f"en el árbol instalado: {offenders}")

    def test_t4_pd10_installed_green_packet_aligned(self) -> None:
        green = self._installed_document(
            INSTALLED_PACKETS_REL / "substages"
            / "implementer-green.md")
        self.assertFalse(
            PD9_FORBIDDEN.search(green),
            msg="PD-10 (in situ): el paquete canónico de GREEN instalado "
                "conserva el término indefinido «required full regression "
                "suite»")
        self.assertTrue(
            POLICY_REFERENCE.search(green),
            msg="PD-10 (in situ): el paquete canónico de GREEN instalado no "
                "remite a la política de evidencia (PD-8)")


# Nota mapeo: TestT4InstalledPolicyDocs agrupa los tres tests vía T4Case
# (instalación compartida); los tres mapean cada uno a UNA postcondición
# (PD-8/PD-9/PD-10) tal como el criterio de aceptación de la spec exige.


if __name__ == "__main__":
    unittest.main(verbosity=2)
