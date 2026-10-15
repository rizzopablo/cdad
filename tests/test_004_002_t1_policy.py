#!/usr/bin/env python3
"""004-002 T1 RED — Política y clasificación (PD-1, PD-2, PD-9) sobre la interfaz I1.

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-1, PD-2,
PD-9) + docs/specs/004-002-project-execution-bootstrap/plan.md (decisión I1 del
orquestador, retiro T1).

Superficie observable bajo prueba (solo escrituras en el proyecto sintético,
ninguna en este repo):
    python3 scripts/cdad_packet.py validate-policy --project-root <raíz> [--classify <ruta>...]
    python3 scripts/cdad_packet.py prepare --project-root <raíz> --propose-policy

La forma del esquema de política en los fixtures deriva del paquete canónico
v1 (path_policy: raíces/archivos por clase + convenciones co-ubicadas), no de
la implementación. RED hoy: el subcomando/opción no existe (rc≠0
'invalid choice'/'unrecognized'); cada aserción expresa el comportamiento de
la postcondición, no la mecánica del CLI.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"

POLICY_FILE = "docs/cdad-policy.json"


# ---------------------------------------------------------------- helpers


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )


def run_validate(root: Path) -> subprocess.CompletedProcess:
    return run_cli(["validate-policy", "--project-root", str(root)])


def run_propose(root: Path) -> subprocess.CompletedProcess:
    return run_cli(["prepare", "--project-root", str(root), "--propose-policy"])


def run_classify(root: Path, relpath: str) -> subprocess.CompletedProcess:
    # Una invocación por ruta: robusto tanto si argparse implementa la
    # opción como nargs='+', como de acciones 'append' o plurales.
    return run_cli(["validate-policy", "--project-root", str(root),
                    "--classify", relpath])


def parse_classify(stdout: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].strip():
            out[parts[0].strip()] = parts[1].strip()
    return out


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        if p.is_symlink():
            h.update(b"symlink->" + os.readlink(p).encode("utf-8"))
        elif p.is_file():
            h.update(p.read_bytes())
        h.update(b"\1")
    return h.hexdigest()


def write_policy(root: Path, *, schema_version=1, path_policy=None,
                 temporary_roots=None, extra=None,
                 drop_schema_version=False,
                 omit_path_policy=False,
                 omit_temporary_roots=False) -> dict:
    """Materializa docs/cdad-policy.json con la forma del esquema canónico."""
    doc: dict = {}
    if not drop_schema_version:
        doc["schema_version"] = schema_version
    if not omit_path_policy:
        doc["path_policy"] = dict(path_policy or {})
    if not omit_temporary_roots:
        doc["temporary_roots"] = list(temporary_roots or [])
    if extra:
        doc.update(extra)
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / POLICY_FILE).write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return doc


class ProjectCase(unittest.TestCase):
    """Base: proyecto sintético en tempdir propio por test."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t1-red-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True)


# ---------------------------------------------------------------- PD-1


class TestPd1PolicyLocationAndSchema(ProjectCase):
    """PD-1: única en docs/cdad-policy.json; esquema exacto de tres campos."""

    def test_pd1_policy_found_only_at_docs_cdad_policy(self) -> None:
        """PD-1: política válida en la única ruta admitida → rc=0;
        misma política en una ruta distinta → rc≠0 con diagnóstico."""
        doc = {
            "schema_version": 1,
            "path_policy": {"test_roots": ["tests"],
                            "implementation_roots": ["src"]},
            "temporary_roots": ["tmp"],
        }
        # (a) en la ruta canónica
        write_policy(self.root, path_policy=doc["path_policy"],
                     temporary_roots=doc["temporary_roots"])
        proc = run_validate(self.root)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)
        # (b) la misma política en otra ubicación NO se encuentra
        root2 = Path(tempfile.mkdtemp(prefix="cdad-t1-red-misplaced-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(root2)],
                                               check=False))
        root2.mkdir(parents=True, exist_ok=True)
        (root2 / "cdad-policy.json").write_text(
            json.dumps(doc), encoding="utf-8")
        proc2 = run_validate(root2)
        self.assertNotEqual(proc2.returncode, 0)
        self.assertNotIn("invalid choice", proc2.stdout + proc2.stderr)
        self.assertTrue((proc2.stdout + proc2.stderr).strip(),
                        msg="diagnóstico de política ausente vacío")

    def test_pd1_exact_field_set_extra_fields_invalid(self) -> None:
        """PD-1: solo schema_version+path_policy+temporary_roots; campo extra
        (modelos/autoridad/bash) torna la política inválida (rc≠0).
        Control: política exacta escrita en el proyecto → rc=0."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"]},
                     temporary_roots=["tmp"])
        for label, extra in (("modelos", {"models": {"policy": "cheap"}}),
                             ("autoridad", {"authority": "docs/auth.md"}),
                             ("bash", {"bash_policy": ["*"]})):
            with self.subTest(campo=label):
                root = Path(tempfile.mkdtemp(
                    prefix=f"cdad-t1-red-extra-{label}-"))
                self.addCleanup(lambda: subprocess.run(
                    ["rm", "-rf", str(root)], check=False))
                write_policy(root,
                             path_policy={"test_roots": ["tests"]},
                             temporary_roots=["tmp"], extra=extra)
                proc = run_validate(root)
                self.assertNotEqual(proc.returncode, 0, msg=label + ": política con campo extra fue aceptada")
                self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

        with self.subTest(campo="exacta"):
            proc = run_validate(self.root)
            self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)

    def test_pd1_missing_schema_field_invalid(self) -> None:
        """PD-1: faltar uno de los tres campos → inválida."""
        for label, kwargs in (("sin-schema_version",
                               {"drop_schema_version": True}),
                              ("sin-temporary_roots",
                               {"temporary_roots": None,
                                "omit_temporary_roots": True}),
                              ("sin-path_policy",
                               {"omit_path_policy": True,
                                "temporary_roots": None})):
            with self.subTest(campo=label):
                root = Path(tempfile.mkdtemp(
                    prefix=f"cdad-t1-red-missing-{label}-"))
                self.addCleanup(lambda: subprocess.run(
                    ["rm", "-rf", str(root)], check=False))
                write_policy(root,
                             path_policy={"test_roots": ["tests"]},
                             **kwargs)
                proc = run_validate(root)
                self.assertNotEqual(proc.returncode, 0, msg=label)
                self.assertNotIn("invalid choice", proc.stdout + proc.stderr)


class TestPd1ProposeDeterministicReadOnly(ProjectCase):
    """PD-1: propuesta determinista, sin escrituras ni aprobación."""

    def test_pd1_propose_policy_deterministic_and_no_writes(self) -> None:
        """PD-1: dos corridas sobre entradas iguales → mismos bytes por
        stdout, y el árbol del proyecto queda idéntico (ninguna escritura)."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"],
                                  "implementation_roots": ["src"]},
                     temporary_roots=["tmp"])
        before = tree_digest(self.root)
        out1 = run_propose(self.root)
        after1 = tree_digest(self.root)
        out2 = run_propose(self.root)
        self.assertEqual(after1, before,
                         msg="prepare --propose-policy escribió en el árbol")
        out2_after = tree_digest(self.root)
        self.assertEqual(out2_after, before,
                         msg="segunda propuesta escribió en el árbol")
        self.assertEqual(out1.returncode, 0,
                         msg=out1.stdout + out1.stderr)
        self.assertEqual(out2.returncode, 0,
                         msg=out2.stdout + out2.stderr)
        self.assertNotIn("invalid choice", out1.stdout + out1.stderr)
        self.assertNotIn("unrecognized", out1.stdout + out1.stderr)
        self.assertTrue(out1.stdout.strip(),
                        msg="propuesta vacía por stdout")
        # propuesta determinista: mismos bytes en dos corridas
        self.assertEqual(out1.stdout, out2.stdout,
                         msg="propuesta no determinista")

    def test_pd1_propose_without_policy_yields_validate_pass(self) -> None:
        """PD-1: caso principal de la propuesta. Sobre un proyecto SIN
        docs/cdad-policy.json, `prepare --propose-policy` da rc=0 con salida
        determinista y sin escrituras; materializar esa salida en una copia
        temporal como docs/cdad-policy.json pasa validate-policy rc=0."""
        self.assertFalse((self.root / POLICY_FILE).exists())
        (self.root / "src").mkdir()
        before = tree_digest(self.root)
        out1 = run_propose(self.root)
        out2 = run_propose(self.root)
        self.assertEqual(out1.returncode, 0,
                         msg=f"propuesta sin política falló: {out1.stdout} {out1.stderr}")
        self.assertNotIn("unrecognized", out1.stdout + out1.stderr)
        self.assertTrue(out1.stdout.strip(), msg="propuesta vacía")
        self.assertEqual(out1.stdout, out2.stdout,
                         msg="propuesta sin política no determinista")
        self.assertEqual(tree_digest(self.root), before,
                         msg="propuesta sin política escribió en el árbol")
        # La salida propuesta es una política válida: en una COPIA temporal,
        # materializada verbatim en docs/cdad-policy.json, valida rc=0.
        copy_root = Path(tempfile.mkdtemp(prefix="cdad-t1-red-mat-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(copy_root)],
                                               check=False))
        (copy_root / "docs").mkdir(parents=True)
        (copy_root / POLICY_FILE).write_text(out1.stdout, encoding="utf-8")
        proc = run_validate(copy_root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"propuesta materializada no valida: {proc.stdout} {proc.stderr}")

    def test_pd1_policy_self_classified_as_policy(self) -> None:
        """PD-1: la propia docs/cdad-policy.json se clasifica `policy`,
        nunca documentation/implementation, aunque caiga bajo una raíz de
        documentación u otra clase."""
        write_policy(self.root,
                     path_policy={
                         "documentation_roots": ["docs"],
                         "implementation_roots": ["pkg"],
                     },
                     temporary_roots=["var/tmp"])
        proc = run_classify(self.root, POLICY_FILE)
        classes = parse_classify(proc.stdout)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        self.assertEqual(classes.get(POLICY_FILE), "policy",
                         msg=f"clase de la política: {classes.get(POLICY_FILE)!r} (mapa: {classes})")


# ---------------------------------------------------------------- PD-2


class TestPd2Rejections(ProjectCase):
    """PD-2: rutas absolutas, escapes, symlinks y conflictos de clases."""

    def test_pd2_rejects_absolute_paths(self) -> None:
        """PD-2: raíz absoluta en path_policy → rc≠0 con diagnóstico."""
        write_policy(self.root,
                     path_policy={"test_roots": ["/tmp/not-relative"]})
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0, msg="ruta absoluta aceptada")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd2_rejects_dotdot_escape(self) -> None:
        """PD-2: escape por `..` → rc≠0 con diagnóstico."""
        write_policy(self.root,
                     path_policy={"implementation_roots": ["../outside"]})
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0, msg="escape `..` aceptado")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd2_rejects_symlink_escape(self) -> None:
        """PD-2: raíz-declarada cuyo symlink sale del proyecto → rc≠0."""
        outside = Path(tempfile.mkdtemp(prefix="cdad-t1-red-outside-"))
        self.addCleanup(lambda: subprocess.run(["rm", "-rf", str(outside)],
                                              check=False))
        write_policy(self.root,
                     path_policy={"implementation_roots": ["ext"]})
        (self.root / "ext").symlink_to(outside, target_is_directory=True)
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0, msg="symlink que sale del proyecto aceptado")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd2_documentation_over_implementation_rejected(self) -> None:
        """PD-2: documentación contra implementación es conflicto."""
        write_policy(self.root,
                     path_policy={"documentation_roots": ["docs"],
                                  "implementation_roots": ["docs"]})
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0,
                            msg="documentación solapada con implementación aceptada")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd2_documentation_over_tests_rejected(self) -> None:
        """PD-2: documentación contra tests es conflicto."""
        write_policy(self.root,
                     path_policy={"documentation_roots": ["docs"],
                                  "test_roots": ["docs/tests"]})
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0,
                            msg="documentación solapada con tests aceptada")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd2_redundant_same_class_overlap_valid(self) -> None:
        """PD-2: solapamiento de la misma clase es válido y espera única."""
        write_policy(self.root,
                     path_policy={
                         "test_roots": ["tests"],
                         "implementation_roots": ["src"],
                         "implementation_files": ["src/util.py"],
                     })
        proc = run_validate(self.root)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)


class TestPd2Classification(ProjectCase):
    """PD-2: clases observables de I1 en los cuatro layouts."""

    def _classify_expect(self, expect: dict[str, str]) -> None:
        for relpath, want in expect.items():
            proc = run_classify(self.root, relpath)
            classes = parse_classify(proc.stdout)
            self.assertEqual(proc.returncode, 0,
                             msg=f"classify {relpath}: {proc.stderr or proc.stdout}")
            got = classes.get(relpath)
            self.assertEqual(got, want,
                             msg=f"classify {relpath}: esperado {want!r}, "
                                 f"obtenido {got!r} (mapa: {classes})")

    def test_pd2_cdad_layout_classification(self) -> None:
        """PD-2: layout CDAD (como este repo) — guiones y clases correctas."""
        write_policy(self.root, path_policy={
            "test_roots": ["tests"],
            "implementation_roots": ["agents", "skills", "scripts",
                                     "sources", "build"],
            "implementation_files": ["install.sh"],
            "documentation_roots": ["docs"],
            "documentation_files": ["docs/systemPatterns.md"],
        }, temporary_roots=[".cdad/tmp"])
        self._classify_expect({
            "scripts/foo.py": "implementation",
            "install.sh": "implementation",
            "docs/systemPatterns.md": "documentation",
            "tests/test_x.py": "test",
            "README": "unclassified",  # ruta sin clasificación necesaria
            ".cdad/tmp/work.json": "temporary",
        })

    def test_pd2_conventional_src_layout_classification(self) -> None:
        """PD-2: layout convencional src/tests."""
        write_policy(self.root, path_policy={
            "test_roots": ["tests"],
            "implementation_roots": ["src"],
        }, temporary_roots=[".cache"])
        self._classify_expect({
            "src/app.py": "implementation",
            "tests/test_app.py": "test",
            "notes.txt": "unclassified",
        })

    def test_pd2_colocated_layout_classification(self) -> None:
        """PD-2: tests co-ubicados — convención de sufijo dentro del paquete."""
        write_policy(self.root, path_policy={
            "test_roots": [],
            "implementation_roots": ["mypkg"],
            "colocated_test_roots": ["mypkg"],
            "colocated_test_suffixes": ["_test.py"],
            "colocated_test_prefixes": ["test_"],
        }, temporary_roots=[])
        self._classify_expect({
            "mypkg/mod.py": "implementation",
            "mypkg/mod_test.py": "colocated-test",
            "mypkg/test_mod.py": "colocated-test",
        })

    def test_pd2_odoo_layout_classification(self) -> None:
        """PD-2: layout Odoo addons/<m>/{models,views,tests}."""
        write_policy(self.root, path_policy={
            "test_roots": ["addons/m1/tests"],
            "implementation_roots": ["addons/m1/models",
                                     "addons/m1/views"],
        }, temporary_roots=["addons/.tmp"])
        self._classify_expect({
            "addons/m1/models/res_partner.py": "implementation",
            "addons/m1/tests/test_res_partner.py": "test",
        })

    def test_pd2_tests_inside_implementation_are_extracted(self) -> None:
        """PD-2: tests declarados dentro de implementación se sustraen de ella."""
        write_policy(self.root, path_policy={
            "test_roots": ["app/tests"],
            "implementation_roots": ["app"],
        }, temporary_roots=[])
        self._classify_expect({
            "app/core.py": "implementation",       # dentro de la raíz impl
            "app/tests/test_core.py": "test",      # sustraída: clase test
        })

    def test_pd2_test_name_outside_declared_locations_is_not_test(self) -> None:
        """PD-2: un nombre de test fuera de ubicaciones declaradas no conceda
        permisos → sin convención ni raíz de tests, NO es test."""
        write_policy(self.root, path_policy={
            "implementation_roots": ["lib"],
        }, temporary_roots=[])
        self._classify_expect({
            "lib/test_foo.py": "implementation",   # cayera en impl, no test
            "test_adhoc.py": "unclassified",       # nombre ≠ permiso
        })


# ---------------------------------------------------------------- PD-9


class TestPd9TemporaryRoots(ProjectCase):
    """PD-9: temporary_roots relativos, sin escape ni solapamiento con
    producto; lista vacía no autoriza temporales."""

    def test_pd9_rejects_dotdot_in_temporary_roots(self) -> None:
        """PD-9: escape `..` en temporary_roots → rc≠0."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"]},
                     temporary_roots=["../leak"])
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0, msg="escape temporal aceptado")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd9_rejects_absolute_temporary_root(self) -> None:
        """PD-9: temporary_roots debe ser relativo (ruta absoluta → rc≠0)."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"]},
                     temporary_roots=["/tmp/abs-root"])
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0, msg="temporal absoluto aceptado")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)

    def test_pd9_rejects_temporal_overlapping_product(self) -> None:
        """PD-9: temporal solapado con producto (raíz impl) → rc≠0."""
        write_policy(self.root,
                     path_policy={"implementation_roots": ["src"]},
                     temporary_roots=["src/tmp"])
        proc = run_validate(self.root)
        self.assertNotEqual(proc.returncode, 0,
                            msg="temporal solapado con producto aceptado")
        self.assertNotIn("invalid choice", proc.stdout + proc.stderr)
        write_policy(self.root,
                     path_policy={"implementation_roots": ["src"]},
                     temporary_roots=["src"])
        proc2 = run_validate(self.root)
        self.assertNotEqual(proc2.returncode, 0,
                            msg="temporal igual a raíz de producto aceptado")
        self.assertNotIn("invalid choice", proc2.stdout + proc2.stderr)

    def test_pd9_empty_list_never_grants_temporary(self) -> None:
        """PD-9: lista vacía no autoriza temporales — valida rc=0 y nunca
        clasifica una ruta como `temporary`."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"]},
                     temporary_roots=[])
        proc = run_validate(self.root)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        proc2 = run_classify(self.root, "scratch/anything.txt")
        classes = parse_classify(proc2.stdout)
        self.assertEqual(proc2.returncode, 0, msg=proc2.stderr or proc2.stdout)
        self.assertNotIn("temporary", classes.values(),
                         msg=f"lista vacía clasificó temporary: {classes}")

    def test_pd9_declared_temporary_root_classifies_temporary(self) -> None:
        """PD-9: el temporal de un encargo es subconjunto explícito de la
        lista — una ruta bajo temporary_roots declarado se clasifica como
        `temporary`."""
        write_policy(self.root,
                     path_policy={"test_roots": ["tests"]},
                     temporary_roots=["work/tmp"])
        proc = run_classify(self.root, "work/tmp/output.bin")
        classes = parse_classify(proc.stdout)
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        self.assertEqual(classes.get("work/tmp/output.bin"), "temporary",
                         msg=f"obtenido {classes}")


if __name__ == "__main__":
    unittest.main()
