#!/usr/bin/env python3
"""006-005 U3 RED — el temporal del test-writer: autorizado y verificable (PD-15..PD-18).

Contract: `docs/specs/006-005-native-path-parity/spec.md` §2.9, §3 PD-15, PD-16,
PD-17, PD-18; §4 INV-3, INV-7; §5 D-5 (C1..C5). Plan: §3 ficha U3 y su bloque
`plan-tasks`. Todas las aserciones se derivan del contrato aprobado: NO se lee
código de implementación; el CLI se invoca como proceso (caja negra) sobre
proyectos descartables bajo tempdir, con `git init` cuando el caso lo pide.

Superficie observable bajo prueba (la que el contrato declara):

    python3 scripts/cdad_packet.py prepare --project-root R --role test-writer \
        --substage red --objective ... \
        --write-scope tests=tests --write-scope temporary=<selector>
    python3 scripts/cdad_packet.py validate-policy --project-root R
    python3 scripts/cdad_packet.py prepare --project-root R --record-dispatch <id> \
        --attempt-id <A> --input <observación I8>
    python3 scripts/cdad_result.py receive --project-root R \
        --execution-context E --packet P --request Q --descriptor D

Mapa test → postcondición:

  TestPd15TemporaryScopeAuthorized
    test_pd15_empty_policy_rejects_naming_file_and_field
        -> PD-15: con `temporary_roots: []` el encargo se rechaza nombrando el
           archivo de política y el campo; ningún paquete publicado.
    test_pd15_declared_root_accepts_and_packet_declares_scope
        -> PD-15: con la raíz declarada, `prepare` acepta y el `REQUEST.json`
           del paquete declara `{"class": "temporary", "root": <selector>}`.
  TestPd16SelectorMustBeGitIgnored
    test_pd16_selector_not_ignored_is_rejected_naming_both_exits
        -> PD-16: selector no ignorado ⇒ rc≠0 nombrando las dos salidas
           legítimas (declararlo en `.gitignore` o no pedir el temporal).
    test_pd16_non_git_tree_is_rejected_naming_both_exits
        -> PD-16: proyecto que no es árbol Git ⇒ el mismo rechazo.
    test_pd16_ignored_selector_is_accepted
        -> PD-16: selector ignorado ⇒ acepta.
  TestPd17ReceiptWithTemporaryScope
    test_pd17_real_test_plus_ignored_probe_is_received_pending
        -> PD-17: un test real en `tests/` más una sonda dentro del temporal se
           reciben con `scope_validation: passed` y recibo `pending`.
    test_pd17_change_outside_every_declared_scope_is_still_rejected
        -> PD-17: un cambio fuera de todo scope declarado sigue rechazándose.
  TestPd18TemporaryRootIsNotProduct
    test_pd18_temporary_root_overlapping_product_is_rejected
        -> PD-18: una raíz temporal que se solapa con rutas de producto sigue
           rechazada por la política.

Alcance declarado de PD-17 (lo exige la spec junto al oráculo de PD-24):
`scope_validation: passed` NO prueba que el auxiliar se haya podido escribir.
Un cambio en una raíz temporal ignorada nunca entra al manifiesto (INV-3: el
manifiesto usa `git ls-files --cached --others --exclude-standard`), así que
`passed` es compatible con que la escritura del auxiliar esté bloqueada. Esa
prueba es una escritura REAL con la herramienta del rol en el recorrido de U6
(E2, V-14); aquí no se sustituye por `passed` ni se declara escrita.

Estado RED (HEAD del paquete): la clase de scope `temporary` no existe en el
vocabulario (`prepare --write-scope temporary=…` ⇒ rc≠0 «scope class is
invalid»), así que los casos positivos fallan en su aserción de aceptación
(AssertionError de comportamiento ausente, no ImportError ni error de fixture).
PD-18 es un ancla: la disjunción temporal↔producto ya se valida hoy y debe
seguir valiendo después de U3.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (  # noqa: E402
    POLICY_FILE,
    REPO_ROOT,
    SCRIPT,
    build_project,
    prepare_args,
    read_state,
    write_state,
)

RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"
AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"
AGENTS_SOURCE = REPO_ROOT / "agents"

# Selector del fixture: un subdirectorio de la raíz temporal declarada por la
# política (contención, no igualdad) — D-5 C2/C3: `.cdad/tmp` es subdirectorio
# disjunto de los subárboles que el CLI escribe.
TEMPORARY_ROOT = ".cdad/tmp"
SELECTOR = ".cdad/tmp/work"

ROLE = "test-writer"
SUBSTAGE = "red"
ATTEMPT_ID = "attempt-u3-red-001"
PART_NAME = "role-report"
PART_KIND = "test-writer-role-report"  # §2.8: test-writer fuera de `audit`
REAL_TEST_REL = "tests/test_u3_real_fixture.py"
OUT_OF_SCOPE_REL = "src/leaked_implementation.py"
MANIFEST_REL = ".cdad/inbox/changes.json"
DESCRIPTOR_REL = ".cdad/inbox/RESULT.json"


# ---------------------------------------------------------------- helpers


def run_cli(script: Path, args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env[AGENTS_ENV] = str(AGENTS_SOURCE)
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
    )


def write_policy_doc(root: Path, *, temporary_roots: list[str],
                     path_policy: dict | None = None) -> None:
    """Política válida con la lista de temporales del caso (autoridad: dueño)."""
    if path_policy is None:
        path_policy = {
            "test_roots": ["tests"],
            "implementation_roots": ["src", "lib"],
            "documentation_roots": ["docs"],
        }
    doc = {
        "schema_version": 1,
        "path_policy": path_policy,
        "temporary_roots": list(temporary_roots),
    }
    (root / POLICY_FILE).write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root),
                          capture_output=True, text=True)


def git_init(root: Path) -> None:
    proc = git(root, "init", "-q")
    if proc.returncode != 0:  # precondition of the fixture, not the contract
        raise AssertionError(f"fixture: `git init` falló: {proc.stderr}")


def git_commit_baseline(root: Path) -> str:
    git(root, "add", "-A")
    proc = git(root, "-c", "user.email=cdad@example.invalid",
               "-c", "user.name=cdad", "commit", "-q", "-m", "baseline")
    if proc.returncode != 0:  # precondition of the fixture
        raise AssertionError(f"fixture: el commit baseline falló: {proc.stderr}")
    return git(root, "rev-parse", "HEAD").stdout.strip()


def temporary_prepare_args(root: Path, *extra: str) -> list[str]:
    return prepare_args(
        root,
        role=ROLE,
        substage=SUBSTAGE,
        objective="U3 temporary scope",
        extra=(
            "--write-scope", "tests=tests",
            "--write-scope", f"temporary={SELECTOR}",
            *extra,
        ),
    )


def packet_dirs(root: Path) -> list[Path]:
    base = root / ".cdad" / "packets"
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if (p / "REQUEST.json").is_file())


def only_packet_dir(tc: unittest.TestCase, root: Path) -> Path:
    dirs = packet_dirs(root)
    tc.assertEqual(
        len(dirs), 1,
        msg=f"PD-15: se esperaba exactamente un paquete publicado, hay: {dirs}")
    return dirs[0]


class TemporaryProjectCase(unittest.TestCase):
    """Proyecto sintético (bootstrap v2 de 004-002) con la política del caso."""

    TEMPORARY_ROOTS: tuple[str, ...] = (TEMPORARY_ROOT,)
    PATH_POLICY: dict | None = None
    GIT: bool = True
    GITIGNORE: str | None = ".cdad/\n"

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u3-red-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        write_policy_doc(self.root, temporary_roots=list(self.TEMPORARY_ROOTS),
                         path_policy=self.PATH_POLICY)
        if self.GITIGNORE is not None:
            (self.root / ".gitignore").write_text(self.GITIGNORE,
                                                  encoding="utf-8")
        if self.GIT:
            git_init(self.root)
            self.baseline = git_commit_baseline(self.root)

    def prepare(self, *extra: str) -> subprocess.CompletedProcess:
        return run_cli(SCRIPT, temporary_prepare_args(self.root, *extra))


# ------------------------------------------------------------------- PD-15


class TestPd15TemporaryScopeAuthorized(TemporaryProjectCase):
    """PD-15: el paquete declara `temporary`; se acepta sólo dentro de
    `temporary_roots` de `docs/cdad-policy.json`."""

    TEMPORARY_ROOTS = ()

    def test_pd15_empty_policy_rejects_naming_file_and_field(self) -> None:
        """PD-15: con `temporary_roots: []` el encargo se rechaza nombrando el
        archivo de la política y el campo; no se publica paquete."""
        proc = self.prepare()
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"PD-15: con `temporary_roots: []` el paquete NO puede "
                f"declarar un temporal (la lista vacía no autoriza "
                f"temporales); rc={proc.returncode} stdout={proc.stdout!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-15: el rechazo no debe imprimir un paquete despachable")
        self.assertIn(
            POLICY_FILE, out,
            msg=f"PD-15: el diagnóstico debe nombrar el archivo de la política "
                f"({POLICY_FILE}); obtenido: {out!r}")
        self.assertIn(
            "temporary_roots", out,
            msg=f"PD-15: el diagnóstico debe nombrar el campo "
                f"`temporary_roots`; obtenido: {out!r}")
        self.assertEqual(
            packet_dirs(self.root), [],
            msg="PD-15: el rechazo publicó un paquete")


class TestPd15DeclaredRootAccepts(TemporaryProjectCase):
    """PD-15 (lado positivo): con la raíz declarada, `prepare` acepta y el
    request del paquete declara el scope temporal."""

    TEMPORARY_ROOTS = (TEMPORARY_ROOT,)

    def test_pd15_declared_root_accepts_and_packet_declares_scope(self) -> None:
        """PD-15: `temporary_roots: [<raíz>]` y un selector dentro de ella ⇒
        rc=0 y el `REQUEST.json` del paquete lleva
        `{"class": "temporary", "root": <selector>}`."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-15: con la raíz temporal declarada por la política el "
                f"paquete debe aceptarse; rc={proc.returncode} "
                f"stdout={proc.stdout[:400]!r} stderr={proc.stderr[:400]!r}")
        packet_dir = only_packet_dir(self, self.root)
        request = json.loads(
            (packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertIn(
            {"class": "temporary", "root": SELECTOR},
            request["write_scope"],
            msg=f"PD-15: el request del paquete debe declarar el temporal "
                f"`{SELECTOR}` como clase `temporary`; write_scope="
                f"{request['write_scope']!r}")
        self.assertIn(
            {"class": "tests", "root": "tests"},
            request["write_scope"],
            msg="PD-15: el scope de tests del rol se conserva")


# ------------------------------------------------------------------- PD-16


class TestPd16SelectorNotIgnored(TemporaryProjectCase):
    """PD-16: con temporal declarado, `prepare` verifica `git check-ignore`."""

    GITIGNORE = "*.log\n"  # NO cubre `.cdad/`

    def test_pd16_selector_not_ignored_is_rejected_naming_both_exits(self) -> None:
        """PD-16: selector no ignorado ⇒ rc≠0 nombrando las dos salidas
        legítimas (declararlo en `.gitignore`, o no pedir el temporal)."""
        proc = self.prepare()
        err = proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"PD-16: el selector {SELECTOR!r} NO está ignorado por Git y "
                f"prepare debe fallar cerrado; rc={proc.returncode} "
                f"stdout={proc.stdout[:400]!r}")
        self.assertIn(
            "gitignore", err.lower(),
            msg=f"PD-16: el diagnóstico debe nombrar la primera salida "
                f"legítima (`.gitignore`); obtenido: {err!r}")
        # La segunda salida legítima: no pedir el temporal. Se exige que el
        # diagnóstico nombre el TEMPORAL y, junto a él, la acción de omitirlo
        # (no basta un «without» suelto: el oráculo es la salida declarada).
        self.assertRegex(
            err,
            r"(?i)(temporar(y|ies)|temporal)",
            msg=f"PD-16: el diagnóstico debe nombrar el temporal; "
                f"obtenido: {err!r}")
        self.assertRegex(
            err,
            r"(?i)(omit|without|not request|do not request|do not declare|"
            r"drop the temporary|remove the temporary|stop requesting|"
            r"no pedir|no solicitar|no declar|omitir|quitar)",
            msg=f"PD-16: el diagnóstico debe nombrar la segunda salida "
                f"legítima (no pedir el temporal); obtenido: {err!r}")
        self.assertEqual(
            packet_dirs(self.root), [],
            msg="PD-16: el rechazo publicó un paquete")


class TestPd16NonGitTree(TemporaryProjectCase):
    """PD-16: un proyecto que no es árbol Git se rechaza igual."""

    GIT = False

    def test_pd16_non_git_tree_is_rejected_naming_both_exits(self) -> None:
        """PD-16: sin árbol Git no hay `git check-ignore` posible ⇒ falla
        cerrado con el mismo diagnóstico de las dos salidas legítimas."""
        self.assertFalse(
            (self.root / ".git").exists(),
            msg="precondición del fixture: el proyecto no debe ser árbol Git")
        proc = self.prepare()
        err = proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"PD-16: un proyecto sin árbol Git no puede verificar el "
                f"temporal y debe fallar cerrado; rc={proc.returncode} "
                f"stdout={proc.stdout[:400]!r}")
        self.assertIn(
            "gitignore", err.lower(),
            msg=f"PD-16: el diagnóstico debe nombrar `.gitignore`; "
                f"obtenido: {err!r}")
        self.assertRegex(
            err,
            r"(?i)(temporar(y|ies)|temporal)",
            msg=f"PD-16: el diagnóstico debe nombrar el temporal; "
                f"obtenido: {err!r}")
        self.assertRegex(
            err,
            r"(?i)(omit|without|not request|do not request|do not declare|"
            r"drop the temporary|remove the temporary|stop requesting|"
            r"no pedir|no solicitar|no declar|omitir|quitar)",
            msg=f"PD-16: el diagnóstico debe nombrar la salida de no pedir el "
                f"temporal; obtenido: {err!r}")
        self.assertEqual(packet_dirs(self.root), [],
                         msg="PD-16: el rechazo publicó un paquete")


class TestPd16IgnoredSelector(TemporaryProjectCase):
    """PD-16 (lado positivo): selector ignorado ⇒ acepta."""

    GITIGNORE = ".cdad/\n"

    def test_pd16_ignored_selector_is_accepted(self) -> None:
        """PD-16: `.gitignore` cubre `.cdad/` ⇒ `git check-ignore` lo acredita
        y el paquete se acepta."""
        probe = git(self.root, "check-ignore", "-q", SELECTOR)
        self.assertEqual(
            probe.returncode, 0,
            msg=f"precondición del fixture: `git check-ignore` debe ignorar "
                f"{SELECTOR!r}")
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-16: con el selector ignorado el paquete debe aceptarse; "
                f"rc={proc.returncode} stdout={proc.stdout[:400]!r} "
                f"stderr={proc.stderr[:400]!r}")
        only_packet_dir(self, self.root)


# ------------------------------------------------------------------- PD-17


class TestPd17ReceiptWithTemporaryScope(TemporaryProjectCase):
    """PD-17: el temporal declarado e ignorado no rompe el recibo; un cambio
    fuera de todo scope sigue rechazado."""

    TEMPORARY_ROOTS = (TEMPORARY_ROOT,)
    # `.cdad/` (raíz temporal y espacio de coordinación) y `.opencode/`
    # (derivados que publica prepare) quedan fuera del árbol observado, igual
    # que en el repo del producto: el manifiesto sólo ve producto y tests.
    GITIGNORE = ".cdad/\n.opencode/\n"

    def _dispatch(self) -> tuple[Path, Path, Path, str]:
        """prepare + record-dispatch: paquete dispatched con scope temporal."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-17 (precondición): el paquete con temporal declarado e "
                f"ignorado debe aceptarse; rc={proc.returncode} "
                f"stderr={proc.stderr[:400]!r}")
        state = read_state(self.root)
        packet_id = state["active_packet"]["id"]
        execution_id = state["execution"]["id"]
        packet_dir = self.root / ".cdad" / "packets" / packet_id
        packet_path = packet_dir / "PACKET.md"
        request_path = packet_dir / "REQUEST.json"
        execution_path = (self.root / ".cdad" / "executions" / execution_id
                          / "execution.json")
        for path in (packet_path, request_path, execution_path):
            self.assertTrue(path.is_file(),
                            msg=f"PD-17 (precondición): falta {path}")
        # Registro I8 del intento (claves cerradas del documento de despacho).
        # Fuera del árbol observado: el manifiesto sólo ve producto y tests.
        observation = Path(self._tmp) / "observation-u3.json"
        observation.write_text(json.dumps({
            "runtime": "opencode",
            "model_configured": "fixture-model",
            "model_reported": "fixture-model",
            "session": "ses-006-005-u3-red-0001",
            "started_at": "2026-10-19T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = run_cli(SCRIPT, [
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", packet_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"PD-17 (precondición): --record-dispatch debe registrar el "
                f"intento: {record.stdout} {record.stderr}")
        self.assertEqual(
            read_state(self.root)["active_packet"]["status"], "dispatched",
            msg="PD-17 (precondición): el paquete activo debe quedar dispatched")
        return packet_path, request_path, execution_path, execution_id

    def _observed_manifest(self) -> tuple[Path, dict]:
        """Manifiesto construido con el comando que el contrato declara
        (INV-3): `git ls-files --cached --others --exclude-standard`."""
        listed = git(self.root, "ls-files", "-z", "--cached", "--others",
                     "--exclude-standard")
        self.assertEqual(listed.returncode, 0,
                         msg=f"fixture: git ls-files falló: {listed.stderr}")
        tracked = {p for p in listed.stdout.split("\0") if p}
        changes = [{"path": p, "operation": "added"}
                   for p in sorted(tracked - set(self._baseline_paths()))]
        doc = {
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": self.baseline,
            # El baseline del manifiesto es un digest opaco (forma pineada por
            # 003-002 §4); el ref identifica el commit del fixture.
            "baseline_sha256": "0" * 64,
            "changes": changes,
        }
        path = self.root / MANIFEST_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path, doc

    def _baseline_paths(self) -> list[str]:
        listed = git(self.root, "ls-tree", "-r", "--name-only", "-z",
                     self.baseline)
        self.assertEqual(listed.returncode, 0,
                         msg=f"fixture: git ls-tree falló: {listed.stderr}")
        return [p for p in listed.stdout.split("\0") if p]

    def _descriptor(self, *, manifest_path: str) -> Path:
        inbox = ".cdad/inbox"
        doc = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": self.feature_id,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [{
                "name": PART_NAME,
                "artifact_kind": PART_KIND,
                "staged_path": f"{inbox}/{PART_NAME}.md",
            }],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": self.baseline,
                "baseline_sha256": "0" * 64,
                "manifest_path": manifest_path,
            },
            "run_evidence_ref": None,
        }
        path = self.root / DESCRIPTOR_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def _receive(self, descriptor: Path) -> subprocess.CompletedProcess:
        return run_cli(RESULT_SCRIPT, [
            "receive",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--descriptor", str(descriptor),
        ])

    def _stage_part(self) -> None:
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / f"{PART_NAME}.md").write_bytes(
            b"# Role report (fixture U3 RED)\nTemporal declarado e ignorado.\n")

    def _prepare_receipt(self) -> None:
        (self.packet_path, self.request_path,
         self.execution_path, execution_id) = self._dispatch()
        request = json.loads(self.request_path.read_text(encoding="utf-8"))
        self.packet_id = request["packet_id"]
        self.feature_id = request["feature_id"]
        self.execution_id = execution_id
        self._stage_part()

    def test_pd17_real_test_plus_ignored_probe_is_received_pending(self) -> None:
        """PD-17: un test real en `tests/` más una sonda dentro del temporal
        declarado e ignorado ⇒ `scope_validation: passed` y recibo `pending`.

        ALCANCE DECLARADO: `passed` NO prueba que el auxiliar se haya podido
        escribir. La sonda queda fuera del manifiesto por construcción (INV-3:
        un temporal ignorado nunca aparece como cambio observado), así que el
        recibo es compatible con una escritura bloqueada por el mapa del
        agente. La prueba de escritura real es U6 (E2, V-14); aquí no se
        sustituye por `passed`.
        """
        self._prepare_receipt()
        # (1) El test real y la sonda del auxiliar, ambos escritos en disco.
        real_test = self.root / REAL_TEST_REL
        real_test.parent.mkdir(parents=True, exist_ok=True)
        real_test.write_text(
            "def test_u3_real_fixture():\n    assert True\n", encoding="utf-8")
        probe = self.root / SELECTOR / "aux_probe.py"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("# sonda del auxiliar en el temporal\n",
                         encoding="utf-8")
        # (2) La sonda está ignorada de verdad y por eso no entra al manifiesto.
        ignored = git(self.root, "check-ignore", "-q", f"{SELECTOR}/aux_probe.py")
        self.assertEqual(
            ignored.returncode, 0,
            msg=f"PD-17 (precondición): la sonda en {SELECTOR!r} debe estar "
                f"ignorada por Git")
        manifest_path, manifest = self._observed_manifest()
        paths = [c["path"] for c in manifest["changes"]]
        self.assertIn(
            REAL_TEST_REL, paths,
            msg=f"PD-17: el manifiesto debe observar el test real escrito en "
                f"`tests/`; observados: {paths!r}")
        self.assertNotIn(
            f"{SELECTOR}/aux_probe.py", paths,
            msg=f"PD-17: INV-3 — un cambio en una raíz temporal ignorada "
                f"NUNCA aparece en el manifiesto; observados: {paths!r}")
        # (3) El recibo acepta: scope passed y semantic pending.
        descriptor = self._descriptor(manifest_path=MANIFEST_REL)
        proc = self._receive(descriptor)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-17: con el temporal declarado e ignorado, el test real "
                f"más la sonda deben recibirse; rc={proc.returncode} "
                f"stdout={proc.stdout[:600]!r} stderr={proc.stderr[:600]!r}")
        receipt = json.loads(proc.stdout)
        self.assertEqual(
            receipt["scope_validation"], "passed",
            msg=f"PD-17: el scope declarado (tests + temporal) debe validar; "
                f"scope_validation={receipt.get('scope_validation')!r}")
        self.assertEqual(
            receipt["semantic_status"], "pending",
            msg=f"PD-17: el recibo nace `pending` y no aprueba; "
                f"semantic_status={receipt.get('semantic_status')!r}")
        self.assertFalse(
            receipt.get("approval_effect", False),
            msg="PD-17: el recibo no aprueba (approval_effect siempre false)")

    def test_pd17_change_outside_every_declared_scope_is_still_rejected(self) -> None:
        """PD-17 (negativo): un cambio fuera de todo scope declarado sigue
        rechazándose, sin finalización durable."""
        self._prepare_receipt()
        manifest = {
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": self.baseline,
            "baseline_sha256": "0" * 64,
            "changes": [{"path": OUT_OF_SCOPE_REL, "operation": "added"}],
        }
        manifest_path = self.root / MANIFEST_REL
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        descriptor = self._descriptor(manifest_path=MANIFEST_REL)
        proc = self._receive(descriptor)
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"PD-17: un cambio en {OUT_OF_SCOPE_REL!r} está fuera de todo "
                f"scope declarado y debe rechazarse; rc={proc.returncode} "
                f"stdout={proc.stdout[:400]!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="PD-17: el rechazo no publica un recibo por stdout")
        final_dir = (self.root / ".cdad" / "runtime" / "results"
                     / self.execution_id / self.packet_id)
        self.assertFalse(
            (final_dir / "receipt.json").exists(),
            msg=f"PD-17: el rechazo fuera de scope dejó un recibo durable en "
                f"{final_dir}")


# ------------------------------------------------------------------- PD-18


class TestPd18TemporaryRootIsNotProduct(unittest.TestCase):
    """PD-18: el temporal no es producto — la disjunción sigue vigente."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u3-pd18-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)

    def _policy(self, temporary_roots: list[str], path_policy: dict) -> None:
        write_policy_doc(self.root, temporary_roots=temporary_roots,
                         path_policy=path_policy)

    def test_pd18_temporary_root_overlapping_product_is_rejected(self) -> None:
        """PD-18: una raíz temporal que se solapa con una raíz de producto
        (implementación o tests) sigue rechazada por la política y ningún
        paquete se prepara con ella."""
        cases = {
            "implementation-root": (
                ["src/tmp"],
                {"test_roots": ["tests"],
                 "implementation_roots": ["src", "lib"],
                 "documentation_roots": ["docs"]},
            ),
            "test-root": (
                ["tests/tmp"],
                {"test_roots": ["tests"],
                 "implementation_roots": ["src", "lib"],
                 "documentation_roots": ["docs"]},
            ),
        }
        for label, (roots, path_policy) in cases.items():
            with self.subTest(caso=label):
                self._policy(roots, path_policy)
                validated = run_cli(
                    SCRIPT, ["validate-policy", "--project-root",
                             str(self.root)])
                out = validated.stdout + validated.stderr
                self.assertNotEqual(
                    validated.returncode, 0,
                    msg=f"PD-18: la raíz temporal {roots[0]!r} se solapa con "
                        f"producto y la política debe rechazarse; "
                        f"salida={out!r}")
                self.assertIn(
                    roots[0], out,
                    msg=f"PD-18: el diagnóstico debe nombrar la raíz temporal "
                        f"rechazada; obtenido: {out!r}")
                prepared = run_cli(
                    SCRIPT, temporary_prepare_args(self.root))
                self.assertNotEqual(
                    prepared.returncode, 0,
                    msg=f"PD-18: prepare no puede aceptar una política con la "
                        f"raíz temporal {roots[0]!r} solapada con producto")
                self.assertEqual(
                    packet_dirs(self.root), [],
                    msg="PD-18: el rechazo publicó un paquete")


if __name__ == "__main__":
    unittest.main()
