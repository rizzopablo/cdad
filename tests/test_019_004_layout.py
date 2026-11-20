#!/usr/bin/env python3
"""019-004 T1 RED — resolución de layout de proyecto (`cdad_packet.py layout`).

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 29f7c39b…b21be1), §4.1–4.3, §5, promesas A y C.

Método: caja negra por subproceso sobre `scripts/cdad_packet.py`; fixtures
mínimos en directorios temporales; ningún fuente de producto se lee. Cada
invocación comprueba primero que el subcomando EXISTE (el rechazo
"invalid choice" de argparse no cuenta como el rechazo contractual), de modo
que hoy todo test falla por AserciónError de comportamiento pendiente y no por
un error de importación/sintaxis/fixture.

Mapeo test -> postcondición (una promesa observable por test, R2):

  test_registered_locator_selects_its_directory_exclusively
      -> PC-01. Sin este test, un proyecto con layout propio seguiría
         resuelto contra docs/ y sus artefactos se buscarían donde no están.
  test_exact_legacy_markers_select_docs_without_writing
      -> PC-02. Sin este test, un proyecto histórico sin locator sería
         tratado como ambiguo/nuevo o se le escribiría un locator.
  test_insufficient_evidence_is_ambiguous_not_guessed
      -> PC-04 (ambiguo). Sin este test, un Memory Bank suelto, docs/specs o
         un cdad/ sin registrar harían seleccionar un layout por conjetura.
  test_ordinary_documentation_is_not_a_cdad_marker
      -> PC-04 (docs ordinarios) + PC-03 (resolución de bootstrap nuevo).
         Sin este test, la documentación de usuario final se confundiría con
         un proyecto CDAD, o un proyecto genuinamente nuevo no obtendría cdad/.
  test_invalid_locator_is_rejected_without_fallback_or_writes
      -> PC-04 (inválido). Sin este test, metadata corrupta o con escape se
         ignoraría cayendo a docs/, o se aceptaría un destino inseguro.
  test_resolution_depends_only_on_explicit_root
      -> PC-08/PC-09 (resolución). Sin este test, el resultado cambiaría con
         el cwd del coordinador o con el nombre del repositorio.
  test_placement_success_is_not_operational_validation
      -> §4.3 (exit 0 = ubicación), PC-02. Sin este test, un exit 0 se leería
         como "estado/política válidos" o la resolución exigiría artefactos.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import re
import unittest
from pathlib import Path

from _layout_support import (
    DECLARATION_REL, OLD_OPERATIONAL_DIR, OPERATIONAL_DIR, declaration_document,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"
# 020-001: la declaración versionable vive en la ruta fija
# `cdad/project-layout.json` (schema 2: schema_version, methodology_dir,
# operational_dir); `.cdad/project-layout.json` es el localizador VIEJO.
LOCATOR = Path(DECLARATION_REL)
OLD_LOCATOR = Path(OLD_OPERATIONAL_DIR) / "project-layout.json"


def run_layout(root, *extra, cwd=None, root_arg="__default__", env_home=None):
    """Run `layout` and assert the subcommand exists (right-reason guard)."""
    args = [sys.executable, str(SCRIPT), "layout"]
    if root_arg == "__default__":
        args += ["--project-root", str(root)]
    elif root_arg is not None:
        args += ["--project-root", str(root_arg)]
    args += list(extra)
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, HOME=env_home or home)
        proc = subprocess.run(
            args, capture_output=True, text=True,
            cwd=str(cwd) if cwd else str(REPO_ROOT), env=env,
        )
    if "invalid choice" in proc.stderr and "layout" in proc.stderr:
        raise AssertionError(
            "cdad_packet.py has no `layout` subcommand yet "
            f"(argparse rejected it): {proc.stderr.strip()[-200:]}"
        )
    return proc


def parse_success(test, proc):
    test.assertEqual(proc.returncode, 0, f"stderr={proc.stderr!r}")
    try:
        return json.loads(proc.stdout)
    except ValueError:
        test.fail(f"stdout is not one JSON object: {proc.stdout!r}")


def assert_failure(test, proc, *, mention=None):
    test.assertNotEqual(proc.returncode, 0, f"stdout={proc.stdout!r}")
    test.assertNotIn("schema_version", proc.stdout, "success object on failure")
    test.assertTrue(proc.stderr.strip(), "failure must explain itself on stderr")
    if mention:
        test.assertIn(mention, proc.stderr.lower())


def assert_migration_guidance(proc, label: str = "") -> None:
    """020-001 PC-2: proyecto no migrado => rechazo con guía breve que apunta a
    la guía canónica `layout-migration.md` y nombra el layout viejo `.cdad/`
    (no basta `.cdad-state.json` / `.cdad-execution`)."""
    where = f"{label}: " if label else ""
    assert proc.returncode != 0, f"{where}debe rechazar; stdout={proc.stdout!r}"
    assert "schema_version" not in proc.stdout, f"{where}objeto de éxito en fallo"
    assert "layout-migration.md" in proc.stderr, (
        f"{where}la guía debe apuntar a layout-migration.md; stderr={proc.stderr!r}")
    assert re.search(r"\.cdad(?![-\w])", proc.stderr), (
        f"{where}la guía debe nombrar el layout viejo `.cdad`; stderr={proc.stderr!r}")


def snapshot(root: Path):
    """Full tree snapshot: relative path -> (kind, content/target)."""
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            out[rel] = ("link", os.readlink(p))
        elif p.is_dir():
            out[rel] = ("dir", None)
        else:
            out[rel] = ("file", p.read_bytes())
    return out


def put(root: Path, rel: str, text: str = "x\n"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def write_locator(root: Path, doc):
    """Escribe la declaración en la ruta fija (`doc` ya es el contenido)."""
    text = doc if isinstance(doc, str) else json.dumps(doc)
    return put(root, str(LOCATOR), text)


def decl(methodology_dir, operational_dir=OPERATIONAL_DIR, **overrides):
    """Declaración schema 2 válida con campos sobreescribibles (para romper
    exactamente un campo por fila)."""
    doc = declaration_document(methodology_dir, operational_dir)
    doc.update(overrides)
    return doc


class LayoutBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(os.path.realpath(self._tmp.name))
        self.root = self.tmp / "repo"
        self.root.mkdir()

    def expect(self, root, source, methodology_dir):
        return {
            "schema_version": 1,
            "project_root": str(Path(os.path.realpath(root))),
            "source": source,
            "methodology_dir": methodology_dir,
            "state": f"{methodology_dir}/.cdad-state.json",
            "policy": f"{methodology_dir}/cdad-policy.json",
        }


class TestLayout(LayoutBase):
    # PC-01
    def test_registered_locator_selects_its_directory_exclusively(self):
        # 020-001: declaración schema 2 con un operational_dir NO por defecto
        # (la resolución de metodología no depende del valor operacional).
        write_locator(self.root, decl("process/cdad", "var/cdad-exec"))
        # Distractors that must NOT win: legacy markers, bare cdad/ and docs/.
        put(self.root, "docs/.cdad-state.json", "{}")
        put(self.root, "docs/cdad-policy.json", "{}")
        put(self.root, "cdad/.cdad-state.json", "{}")
        before = snapshot(self.root)
        proc = run_layout(self.root)
        self.assertEqual(parse_success(self, proc),
                         self.expect(self.root, "registered", "process/cdad"))
        self.assertEqual(snapshot(self.root), before, "layout must be read-only")

    # PC-02
    def test_exact_legacy_markers_select_docs_without_writing(self):
        for marker in ("docs/.cdad-state.json", "docs/cdad-policy.json"):
            with self.subTest(marker=marker):
                root = self.tmp / marker.replace("/", "_").replace(".", "")
                root.mkdir()
                put(root, marker, "not even json")  # selection != content validation
                put(root, "docs/guide.md", "end-user page\n")
                before = snapshot(root)
                proc = run_layout(root)
                self.assertEqual(parse_success(self, proc),
                                 self.expect(root, "legacy", "docs"))
                self.assertEqual(snapshot(root), before)
                self.assertFalse((root / LOCATOR).exists(), "no locator may be registered")

    # PC-04 (ambiguous)
    def test_insufficient_evidence_is_ambiguous_not_guessed(self):
        cases = {
            "memory-bank-file": ["docs/projectbrief.md"],
            "memory-bank-progress": ["docs/progress.md", "docs/activeContext.md"],
            "docs-epics": ["docs/epics/epic-001/plan.md"],
            "docs-specs": ["docs/specs/001-x/spec.md"],
            "unregistered-cdad": ["cdad/projectbrief.md"],
            "unregistered-cdad-state": ["cdad/.cdad-state.json"],
            "operational-records-only": [".cdad/executions/exec-1/execution.json",
                                         ".cdad/packets/p1/REQUEST.json"],
        }
        for name, files in cases.items():
            for flags in ((), ("--for-bootstrap",)):
                with self.subTest(case=name, flags=flags):
                    root = self.tmp / f"{name}{'-b' if flags else ''}"
                    root.mkdir()
                    for f in files:
                        put(root, f, "{}")
                    before = snapshot(root)
                    proc = run_layout(root, *flags)
                    if name == "operational-records-only":
                        # 020-001 (INVERTIDO): un `.cdad/` poblado sin
                        # declaración es un proyecto no migrado: guía, no
                        # «ambiguo».
                        assert_migration_guidance(proc, name)
                    else:
                        assert_failure(self, proc, mention="ambiguous")
                    self.assertEqual(snapshot(root), before)

    # PC-04 (ordinary docs) + PC-03 resolution
    def test_ordinary_documentation_is_not_a_cdad_marker(self):
        put(self.root, "docs/index.md", "# user guide\n")
        put(self.root, "docs/adr/0001-choice.md", "# adr\n")
        put(self.root, "README.md", "readme\n")
        before = snapshot(self.root)
        # Ordinary query: uninitialized, explicit failure, never "legacy".
        proc = run_layout(self.root)
        assert_failure(self, proc)
        self.assertNotIn('"legacy"', proc.stdout)
        self.assertEqual(snapshot(self.root), before)
        # Explicit bootstrap query proposes the new default without writing.
        proc = run_layout(self.root, "--for-bootstrap")
        self.assertEqual(parse_success(self, proc),
                         self.expect(self.root, "new", "cdad"))
        self.assertEqual(snapshot(self.root), before, "proposal must not create anything")
        # A genuinely empty root behaves the same.
        empty = self.tmp / "empty"
        empty.mkdir()
        proc = run_layout(empty, "--for-bootstrap")
        self.assertEqual(parse_success(self, proc)["source"], "new")
        assert_failure(self, run_layout(empty))
        self.assertEqual(snapshot(empty), {})

    # PC-04 (invalid)
    def test_invalid_locator_is_rejected_without_fallback_or_writes(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        # 020-001: cada fila es schema 2 con un operational_dir válido y rompe
        # SOLO el campo nombrado (si no, cualquier fila fallaría por «schema
        # viejo» y no comprobaría su regla de ruta).
        bad = {
            "unknown-field": decl("cdad", x=1),
            "missing-field": {"schema_version": 2, "operational_dir": OPERATIONAL_DIR},
            "bad-version": decl("cdad", schema_version=3),
            "empty": decl(""),
            "non-string": decl(7),
            "absolute": decl("/etc"),
            "dotdot": decl("../up"),
            "inner-dotdot": decl("a/../b"),
            "dot": decl("."),
            "dot-component": decl("a/./b"),
            "backslash": decl("a\\b"),
            "cdad-ops": decl(OPERATIONAL_DIR),
            "beneath-cdad-ops": decl(f"{OPERATIONAL_DIR}/process"),
            "malformed-json": "{not json",
            "duplicate-keys": '{"schema_version":2,"methodology_dir":"a","methodology_dir":"b","operational_dir":".cdad-execution"}',
            "not-object": "[1]",
        }
        # 020-001 (INVERTIDO): la declaración schema 1 (sin operational_dir)
        # ya no es «versión inválida» sino proyecto no migrado: guía.
        old_schema = self.tmp / "old-schema-declaration"
        old_schema.mkdir()
        write_locator(old_schema, {"schema_version": 1, "methodology_dir": "cdad"})
        put(old_schema, "docs/.cdad-state.json", "{}")
        before_old = snapshot(old_schema)
        for flags in ((), ("--for-bootstrap",)):
            assert_migration_guidance(run_layout(old_schema, *flags), "schema 1")
        self.assertEqual(snapshot(old_schema), before_old)
        # El localizador viejo `.cdad/project-layout.json` también es no migrado.
        old_locator = self.tmp / "old-locator"
        old_locator.mkdir()
        put(old_locator, str(OLD_LOCATOR),
            json.dumps({"schema_version": 1, "methodology_dir": "cdad"}))
        before_old = snapshot(old_locator)
        for flags in ((), ("--for-bootstrap",)):
            assert_migration_guidance(run_layout(old_locator, *flags), ".cdad locator")
        self.assertEqual(snapshot(old_locator), before_old)
        for name, doc in bad.items():
            for flags in ((), ("--for-bootstrap",)):
                with self.subTest(case=name, flags=flags):
                    root = self.tmp / f"bad-{name}{'-b' if flags else ''}"
                    root.mkdir()
                    write_locator(root, doc)
                    put(root, "docs/.cdad-state.json", "{}")  # tempting legacy fallback
                    before = snapshot(root)
                    proc = run_layout(root, *flags)
                    assert_failure(self, proc)
                    self.assertEqual(snapshot(root), before)

        # Filesystem-dependent invalidities.
        fs_cases = {}
        link_root = self.tmp / "bad-symlink-escape"
        link_root.mkdir()
        os.symlink(outside, link_root / "escape")
        write_locator(link_root, decl("escape/cdad"))
        fs_cases["symlink-escape"] = link_root
        file_root = self.tmp / "bad-target-file"
        file_root.mkdir()
        put(file_root, "process", "i am a file")
        write_locator(file_root, decl("process"))
        fs_cases["target-is-file"] = file_root
        ops_link_root = self.tmp / "bad-symlink-into-ops"
        ops_link_root.mkdir()
        (ops_link_root / OPERATIONAL_DIR / "inner").mkdir(parents=True)
        os.symlink(ops_link_root / OPERATIONAL_DIR / "inner", ops_link_root / "alias")
        write_locator(ops_link_root, decl("alias"))
        fs_cases["symlink-into-cdad-ops"] = ops_link_root
        for name, root in fs_cases.items():
            with self.subTest(case=name):
                before = snapshot(root)
                assert_failure(self, run_layout(root))
                self.assertEqual(snapshot(root), before)
        self.assertEqual(list(outside.iterdir()), [], "nothing written outside the root")

    # PC-08 / PC-09 (resolution)
    def test_resolution_depends_only_on_explicit_root(self):
        results = []
        for basename in ("repo", "docs", "cdad", "my project", "x.y"):
            root = self.tmp / "roots" / basename
            root.mkdir(parents=True)
            write_locator(root, decl("process/cdad"))
            parent = root.parent
            unrelated = self.tmp / "elsewhere"
            unrelated.mkdir(exist_ok=True)
            relative_from_parent = os.path.relpath(root, parent)
            variants = [
                run_layout(root, cwd=root),
                run_layout(root, cwd=parent),
                run_layout(root, cwd=unrelated),
                run_layout(None, cwd=parent, root_arg=relative_from_parent),
            ]
            link = self.tmp / f"link-{basename.replace(' ', '_')}"
            os.symlink(root, link)
            variants.append(run_layout(link, cwd=unrelated))
            expected = self.expect(root, "registered", "process/cdad")
            for proc in variants:
                self.assertEqual(parse_success(self, proc), expected)
            results.append({k: v for k, v in expected.items() if k != "project_root"})
        self.assertTrue(all(r == results[0] for r in results), "basename must not matter")

        # The working directory is never a substitute for the root.
        cwd_project = self.tmp / "cwd-project"
        put(cwd_project, "docs/.cdad-state.json", "{}")
        bare = self.tmp / "bare"
        bare.mkdir()
        assert_failure(self, run_layout(None, cwd=cwd_project, root_arg=None))  # root required
        assert_failure(self, run_layout(bare, cwd=cwd_project))                 # cwd marker ignored
        assert_failure(self, run_layout(self.tmp / "does-not-exist", cwd=cwd_project))
        # No parent search: a nested directory inside a legacy project is not legacy.
        nested = cwd_project / "sub" / "pkg"
        nested.mkdir(parents=True)
        proc = run_layout(nested)
        assert_failure(self, proc)
        self.assertNotIn("legacy", proc.stdout)

    # §4.3 placement != operational validation
    def test_placement_success_is_not_operational_validation(self):
        # Registered directory that does not exist yet and has no state/policy.
        write_locator(self.root, decl("process/cdad"))
        before = snapshot(self.root)
        got = parse_success(self, run_layout(self.root))
        self.assertEqual(got, self.expect(self.root, "registered", "process/cdad"))
        self.assertFalse((self.root / "process").exists(), "must not create the directory")
        self.assertEqual(snapshot(self.root), before)
        # Legacy marker with unusable content and no counterpart still resolves.
        legacy = self.tmp / "legacy-garbage"
        legacy.mkdir()
        put(legacy, "docs/cdad-policy.json", "\x00garbage")
        before = snapshot(legacy)
        got = parse_success(self, run_layout(legacy))
        self.assertEqual(got, self.expect(legacy, "legacy", "docs"))
        self.assertEqual(snapshot(legacy), before)


if __name__ == "__main__":
    unittest.main()
