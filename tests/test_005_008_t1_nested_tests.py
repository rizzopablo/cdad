#!/usr/bin/env python3
"""005-008 T1 RED — Capacidades de ruta con RAÍZ DE TESTS ANIDADA (PD-1..PD-9).

Contract: docs/specs/005-008-project-path-capabilities/spec.md (PD-1..PD-9,
INV-1..INV-4) + docs/specs/005-008-project-path-capabilities/plan.md (T1) +
docs/specs/005-008-project-path-capabilities/discovery.md (defecto reproducido
§2; fixtures a reutilizar §4; guard B3).

Superficie observable (proyectos sintéticos en tempdirs; ninguna escritura
fuera de ellos; NINGUNA lectura de implementación — ni skills/** ni el
módulo del CLI por import):

  Subprocess sobre el CLI del ÁRBOL DE TRABAJO (mismo medio que las
  fixtures 004-002; el ciclo se desarrolla en el repo):
    CDAD_OPENCODE_AGENTS_DIR=<copia agents/cdad-*.md> \
      python3 scripts/cdad_packet.py prepare --project-root <raíz> ...
    → publica .opencode/agents/cdad-*.md; los mapas read/grep/glob/edit de
    cada derivado se evalúan con el ORÁCULO findLast ÚNICO
    (tests/pd10_permission_semantics.verdict, reutilizado por import; NO se
    reimplementa ningún evaluador).
  Guard CC forma-real (I10/C2) como control de paridad donde corresponde:
    echo '<hook json>' | CDAD_PACKET_CLI=<repo>/scripts/cdad_packet.py \
      bash scripts/claude-code-path-guard.sh <rol>   # cwd = proyecto fixture

Política del caso de uso (Perl/Webmin — CASO DE USO del plan, no política
confirmada del consumidor): implementation_roots=["webmin-module/module"],
test_roots=["webmin-module/module/t"] (ANIDADA dentro de la raíz de
implementación — política legal, discovery §1.1), y el CASO FOCAL
test_files=["webmin-module/module/t/standalone.t"] con test_roots vacía.
No hay colocados declarados (el caso Perl no los usa).

Mapa test → postcondición (UN test por PD):

  TestPd1NestedTestTreeReadable
    test_pd1_test_writer_reads_nested_test_tree        -> PD-1 (RED hoy: el
      defecto — el mapa read del test-writer no reabre el árbol de tests
      declarado; control de paridad: el guard CC YA lo permite)
  TestPd2ImplementationReadDenied
    test_pd2_test_writer_read_implementation_denied    -> PD-2 (control: la
      barrera mediada de lectura se conserva)
  TestPd3TestWriterEditsTestsNotImplementation
    test_pd3_test_writer_edit_maps                     -> PD-3 (control
      no-regresión: hoy ya es correcto)
  TestPd4ImplementerEditAndRead
    test_pd4_implementer_edit_impl_not_tests           -> PD-4 (control: edita
      implementación, no tests; su read NO deniega tests)
  TestPd5TestFilesUnderImplementation
    test_pd5_test_files_declared_under_impl            -> PD-5 (RED hoy: caso
      focal test_files — el declarado queda denegado a leer/editar al
      test-writer y el implementer lo deniega en edit HOY NO)
  TestPd6PrivateInsideTestTree
    test_pd6_private_inside_test_tree_never_reopened   -> PD-6 (precedencia
      findLast: privado gana; el control del hermano cae hoy por el MISMO
      defecto PD-1)
  TestPd7NoAmplification
    test_pd7_literal_tests_dir_under_impl_not_amplified -> PD-7/B3 (guard de
      regresión: un tests/ literal NO declarado sigue siendo implementación;
      sin convenciones globales **/t/** ni **/*.t)
  TestPd8ConventionalLayoutNoRegression
    test_pd8_conventional_layout_verdicts_unchanged    -> PD-8 (no-regresión
      del layout convencional)
  TestPd9NoSearchPathEntries
    test_pd9_no_grep_glob_path_entries                 -> PD-9/W-2 (ningún
      derivado gana entradas por ruta en grep/glob)

RED hoy (sin el arreglo; defecto reproducido en discovery §2/§6): PD-1 y PD-5
fallan por la postcondición faltante (allow ausente en los mapas derivados);
PD-6 falla SOLO en su control positivo (hermano no privado) por el mismo
defecto PD-1. TODA falla es AssertionError de comportamiento sobre veredictos
del oráculo único — no ImportError/SyntaxError/NameError/AttributeError, sin
nombres de funciones internas ni mocks.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest

from test_004_002_t1_policy import parse_classify, run_classify  # noqa: E402
from test_004_002_t2_bootstrap import POLICY_FILE  # noqa: E402
from test_004_002_t5_runtime import (  # noqa: E402
    AGENTS_ENV,
    CLI_ENV,
    LayoutProject,
    assert_no_search_path_entries,
    prepare_args,
    published_derived,
    require_derived,
    run_guard,
)
from pd10_permission_semantics import (  # noqa: E402
    perm_map,
    verdict,
)
from test_opencode_read_map_and_steps import glob_to_regex  # noqa: E402

TEST_WRITER = "cdad-test-writer.md"
IMPLEMENTER = "cdad-implementer.md"

IMPL = "webmin-module/module"
TEST_TREE = "webmin-module/module/t"
MAIN = f"{IMPL}/main.pl"
CGI = f"{IMPL}/index.cgi"
BASIC = f"{TEST_TREE}/basic.t"
HELPER = f"{TEST_TREE}/helper.pl"
DECLARED_FILE = f"{TEST_TREE}/standalone.t"
UNDECLARED_FILE = f"{TEST_TREE}/undeclared.t"
LITERAL_TESTS_DIR = f"{IMPL}/tests/x.py"

# Sondas NO declaradas con forma de test Perl: si existiera una convención
# global **/t/** o **/*.t, alguna regla de los derivados las matchearía
# (PD-7/INV-3). Ninguna está bajo raíces declaradas.
UNDECLARED_T_PROBES = ("other/t/basic.t", "other/t/helper.pl", "other/basic.t")


def undeclared_convention_rules(
        agent_text: str,
        probes: tuple[str, ...]) -> list[tuple[str, str, str]]:
    """Reglas NO catch-all de `read`/`edit` cuyo patrón matchea sondas NO
    declaradas por la política: serían convenciones globales **/t/** o
    **/*.t (B3/PD-7/INV-3 — amplificación de la política). El catch-all "*"
    se excluye: no es una convención por ruta (los mapas de edit lo llevan
    por diseño)."""
    flagged: list[tuple[str, str, str]] = []
    for tool in ("read", "edit"):
        for pattern, verb in perm_map(agent_text, tool):
            if pattern == "*":
                continue
            if any(re.fullmatch(glob_to_regex(pattern), probe)
                   for probe in probes):
                flagged.append((tool, pattern, verb))
    return flagged


class PerlLayoutProject(LayoutProject):
    """Proyecto sintético con política de tests anidados (caso Perl/Webmin).

    Reutiliza el arnés completo de T5 (build_project + agentes de origen en
    copia temporal + prepare subprocess con CDAD_OPENCODE_AGENTS_DIR). El
    layout por defecto del arnés NO se aplica: el fixture escribe su propia
    política de tests anidados por test (apply_perl).
    """

    def apply_layout(self, layout: str) -> None:
        # El fixture Perl define su política por test via apply_perl;
        # el layout convencional por defecto del arnés no corresponde aquí.
        return

    def apply_perl(self, *, test_roots: tuple[str, ...] = (TEST_TREE,),
                   test_files: tuple[str, ...] = (),
                   private: tuple[str, ...] = (),
                   extra_files: tuple[str, ...] = ()) -> None:
        """Política válida de tres campos del caso de uso (raíz de tests
        anidada) + sus archivos de fixture; campos opcionales (test_files,
        private_paths) solo cuando se declaran."""
        path_policy = {
            "implementation_roots": [IMPL],
            "test_roots": list(test_roots),
            "documentation_roots": ["docs"],
        }
        if test_files:
            path_policy["test_files"] = list(test_files)
        if private:
            path_policy["private_paths"] = list(private)
        doc = {"schema_version": 1, "path_policy": path_policy,
               "temporary_roots": [".cdad/tmp"]}
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        files = (MAIN, CGI, BASIC, HELPER, *test_files, *extra_files)
        for rel in files:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# fixture {rel}\n", encoding="utf-8")

    def prepare_perl(self, **apply_kwargs) -> subprocess.CompletedProcess:
        """Aplica la política del caso y corre el prepare del arnés (rc 0)."""
        self.apply_perl(**apply_kwargs)
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"prepare del fixture (precondición): "
                f"{proc.stdout} {proc.stderr}")
        return proc


# --------------------------------------------------------------- PD-1


class TestPd1NestedTestTreeReadable(PerlLayoutProject):
    """PD-1: el test-writer LEE su árbol de tests anidado (RED hoy: defecto)."""

    def test_pd1_test_writer_reads_nested_test_tree(self) -> None:
        """PD-1: con test_roots anidada en implementation_roots, el mapa
        `read` del derivado cdad-test-writer resuelve allow para los archivos
        del árbol de tests declarado — incluido un auxiliar no llamativo
        (t/helper.pl) — por findLast (el allow de tests va DESPUÉS del deny
        de implementación). Control de paridad (guard CC forma-real, I10):
        el clasificador/guard ya permite leer el árbol anidado; el mapa
        OpenCode es lo que falla hoy (discovery §1.3/§6)."""
        proc = self.prepare_perl()
        tw = require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]
        for probe in (BASIC, HELPER):
            with self.subTest(probe=probe):
                got = verdict(tw, "read", probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-1: el mapa `read` del derivado {TEST_WRITER} "
                        f"resuelve read({probe!r}) como {got!r} — el árbol "
                        f"de tests DECLARADO (test_roots anidada) debe quedar "
                        f"abierto a lectura para el test-writer (el deny de "
                        f"implementación no debe tragárselo)")
        with self.subTest(control="guard CC forma-real"):
            guard = run_guard(self.root, "test-writer-read", "Read",
                              {"file_path": HELPER})
            self.assertEqual(
                guard.returncode, 0,
                msg=f"PD-1 control: el guard CC denegó Read({HELPER!r}) al "
                    f"test-writer (rc={guard.returncode}: "
                    f"{guard.stderr.strip()}) — el clasificador ya da "
                    f"'tests' al árbol anidado; el mapa OpenCode debe "
                    f"quedar en paridad con el guard")


# --------------------------------------------------------------- PD-2


class TestPd2ImplementationReadDenied(PerlLayoutProject):
    """PD-2: el test-writer conserva el deny mediado de lectura de la
    implementación (control de la barrera)."""

    def test_pd2_test_writer_read_implementation_denied(self) -> None:
        """PD-2: en la misma política, el mapa `read` del test-writer resuelve
        deny para los archivos de implementación declarados (main.pl,
        index.cgi)."""
        self.prepare_perl()
        tw = require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]
        for probe in (MAIN, CGI):
            with self.subTest(probe=probe):
                got = verdict(tw, "read", probe)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-2: el mapa `read` del derivado {TEST_WRITER} "
                        f"resuelve read({probe!r}) como {got!r} — la "
                        f"barrera mediada de lectura de la implementación "
                        f"debe conservarse")


# --------------------------------------------------------------- PD-3


class TestPd3TestWriterEditsTestsNotImplementation(PerlLayoutProject):
    """PD-3: el test-writer edita su árbol de tests y NO la implementación
    (no-regresión: hoy ya es correcto)."""

    def test_pd3_test_writer_edit_maps(self) -> None:
        """PD-3: el mapa `edit` del test-writer resuelve allow para el árbol
        de tests declarado (basic.t, helper.pl) y deny para la
        implementación (main.pl, index.cgi)."""
        self.prepare_perl()
        tw = require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]
        for probe in (BASIC, HELPER):
            with self.subTest(edit=probe):
                got = verdict(tw, "edit", probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-3: el mapa `edit` de {TEST_WRITER} resolvió "
                        f"edit({probe!r}) como {got!r}, la política exige "
                        f"'allow' (árbol de tests declarado)")
        for probe in (MAIN, CGI):
            with self.subTest(edit=probe):
                got = verdict(tw, "edit", probe)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-3: el mapa `edit` de {TEST_WRITER} resolvió "
                        f"edit({probe!r}) como {got!r}, la política exige "
                        f"'deny' (implementación)")


# --------------------------------------------------------------- PD-4


class TestPd4ImplementerEditAndRead(PerlLayoutProject):
    """PD-4: el implementer edita implementación y no tests; su read NO
    deniega los tests (allow por defecto — sin entradas de tests en read)."""

    def test_pd4_implementer_edit_impl_not_tests(self) -> None:
        """PD-4: el mapa `edit` de cdad-implementer resuelve allow para
        main.pl y deny para los tests declarados (basic.t, helper.pl); su
        `read` no deniega los tests (veredicto allow por defecto)."""
        self.prepare_perl()
        imp = require_derived(
            self, self.root, (TEST_WRITER, IMPLEMENTER))[IMPLEMENTER]
        with self.subTest(edit=MAIN):
            got = verdict(imp, "edit", MAIN)
            self.assertEqual(
                got, "allow",
                msg=f"PD-4: el mapa `edit` de {IMPLEMENTER} resolvió "
                    f"edit({MAIN!r}) como {got!r}, la política exige 'allow'")
        for probe in (BASIC, HELPER):
            with self.subTest(edit=probe):
                got = verdict(imp, "edit", probe)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-4: el mapa `edit` de {IMPLEMENTER} resolvió "
                        f"edit({probe!r}) como {got!r}, la política exige "
                        f"'deny' (tests declarados)")
            with self.subTest(read=probe):
                got = verdict(imp, "read", probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-4: el mapa `read` de {IMPLEMENTER} resolvió "
                        f"read({probe!r}) como {got!r} — el implementer no "
                        f"deniega la lectura de tests (sin entradas de tests "
                        f"en su read)")


# --------------------------------------------------------------- PD-5


class TestPd5TestFilesUnderImplementation(PerlLayoutProject):
    """PD-5 (caso focal): test_files bajo implementación con test_roots
    vacía (RED hoy: defecto en test_files)."""

    def test_pd5_test_files_declared_under_impl(self) -> None:
        """PD-5: con test_files declarando un archivo BAJO la raíz de
        implementación (test_roots vacía), el test-writer resuelve allow
        para LEER y EDITAR el archivo declarado, el implementer lo DENIEGA
        en edit; y un archivo con forma de test NO declarado bajo la
        implementación sigue deny para el test-writer (no se corrige solo el
        ejemplo .t). Control de clasificación por CLI observable: el
        declarado clasifica 'tests' y el no declarado 'implementation' — la
        clasificación ya es correcta; el defecto está en los mapas."""
        proc = self.prepare_perl(
            test_roots=(), test_files=(DECLARED_FILE,),
            extra_files=(UNDECLARED_FILE,))
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        classes: dict[str, str | None] = {}
        for rel in (DECLARED_FILE, UNDECLARED_FILE):
            with self.subTest(control="classify", probe=rel):
                cls = run_classify(self.root, rel)
                self.assertEqual(
                    cls.returncode, 0,
                    msg=f"PD-5 control: validate-policy --classify falló "
                        f"(rc={cls.returncode}: {cls.stdout} {cls.stderr})")
                classes[rel] = parse_classify(cls.stdout).get(rel)
        self.assertEqual(
            classes.get(DECLARED_FILE), "test",
            msg=f"PD-5 control: el clasificador no da 'test' (vocabulario "
                f"observable del CLI) al archivo declarado en test_files "
                f"({classes!r})")
        self.assertEqual(
            classes.get(UNDECLARED_FILE), "implementation",
            msg=f"PD-5 control: el clasificador no da 'implementation' al "
                f"archivo con forma de test NO declarado ({classes!r})")
        with self.subTest(probe=DECLARED_FILE, tool="read", agent=TEST_WRITER):
            got = verdict(tw, "read", DECLARED_FILE)
            self.assertEqual(
                got, "allow",
                msg=f"PD-5 (focal): el mapa `read` de {TEST_WRITER} resolvió "
                    f"read({DECLARED_FILE!r}) como {got!r} — el archivo "
                    f"declarado en test_files (bajo implementación) debe "
                    f"quedar abierto a LECTURA para el test-writer")
        with self.subTest(probe=DECLARED_FILE, tool="edit", agent=TEST_WRITER):
            got = verdict(tw, "edit", DECLARED_FILE)
            self.assertEqual(
                got, "allow",
                msg=f"PD-5 (focal): el mapa `edit` de {TEST_WRITER} resolvió "
                    f"edit({DECLARED_FILE!r}) como {got!r} — el archivo "
                    f"declarado en test_files debe quedar editable por el "
                    f"test-writer")
        with self.subTest(probe=DECLARED_FILE, tool="edit", agent=IMPLEMENTER):
            got = verdict(imp, "edit", DECLARED_FILE)
            self.assertEqual(
                got, "deny",
                msg=f"PD-5 (focal): el mapa `edit` de {IMPLEMENTER} resolvió "
                    f"edit({DECLARED_FILE!r}) como {got!r} — test_files son "
                    f"tests declarados y el implementer no los edita")
        for tool in ("read", "edit"):
            with self.subTest(probe=UNDECLARED_FILE, tool=tool,
                              agent=TEST_WRITER):
                got = verdict(tw, tool, UNDECLARED_FILE)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-5: el mapa `{tool}` de {TEST_WRITER} resolvió "
                        f"{tool}({UNDECLARED_FILE!r}) como {got!r} — un "
                        f"archivo con forma de test NO declarado bajo la "
                        f"implementación sigue denegado (sin convenciones "
                        f"globales)")


# --------------------------------------------------------------- PD-6


class TestPd6PrivateInsideTestTree(PerlLayoutProject):
    """PD-6: una excepción de tests NUNCA reabre una ruta privada
    (precedencia findLast: private gana)."""

    def test_pd6_private_inside_test_tree_never_reopened(self) -> None:
        """PD-6: con una ruta privada ANIDADA dentro de la raíz de tests
        (webmin-module/module/t/secret.local), el mapa `read` Y `edit` de
        TODO derivado publicado resuelve deny para ella (el allow de tests va
        ANTES de private); el hermano no privado bajo el árbol de tests sigue
        allow para el test-writer (control positivo interno que cae HOY por
        el mismo defecto PD-1)."""
        secret = f"{TEST_TREE}/secret.local"
        self.prepare_perl(private=(secret,), extra_files=(secret,))
        pub = require_derived(
            self, self.root,
            tuple(sorted(published_derived(self.root))))
        for name, text in sorted(pub.items()):
            with self.subTest(agent=name, probe=secret, tool="read"):
                got = verdict(text, "read", secret)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-6: {name} resuelve read({secret!r}) como "
                        f"{got!r} — la ruta privada anidada en el árbol de "
                        f"tests debe quedar denegada para TODO rol")
            with self.subTest(agent=name, probe=secret, tool="edit"):
                got = verdict(text, "edit", secret)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-6: {name} resuelve edit({secret!r}) como "
                        f"{got!r} — la ruta privada anidada en el árbol de "
                        f"tests debe quedar denegada para TODO rol")
        with self.subTest(control="hermano no privado", tool="read"):
            got = verdict(pub[TEST_WRITER], "read", BASIC)
            self.assertEqual(
                got, "allow",
                msg=f"PD-6 control: el hermano no privado {BASIC!r} resolvió "
                    f"read como {got!r} para {TEST_WRITER} — la excepción de "
                    f"tests debe reabrir al hermano (hoy cae por el defecto "
                    f"PD-1)")
        with self.subTest(control="hermano no privado", tool="edit"):
            got = verdict(pub[TEST_WRITER], "edit", BASIC)
            self.assertEqual(
                got, "allow",
                msg=f"PD-6 control: el hermano no privado {BASIC!r} resolvió "
                    f"edit como {got!r} para {TEST_WRITER}")


# --------------------------------------------------------------- PD-7


class TestPd7NoAmplification(PerlLayoutProject):
    """PD-7/B3: sin amplificación — un tests/ literal NO declarado bajo la
    implementación sigue siendo implementación; sin convenciones globales."""

    def test_pd7_literal_tests_dir_under_impl_not_amplified(self) -> None:
        """PD-7: con un directorio literal tests/ anidado bajo la raíz de
        implementación (NO declarado en la política), el test-writer resuelve
        deny en read y edit, y el implementer allow en edit. Además, NO
        existe ninguna regla global **/t/** ni **/*.t en los derivados
        publicados: solo se reabren los árboles/archivos declarados
        (sondas no declaradas con forma de test Perl + barrido de reglas)."""
        proc = self.prepare_perl(extra_files=(LITERAL_TESTS_DIR,))
        with self.subTest(control="classify", probe=LITERAL_TESTS_DIR):
            cls = run_classify(self.root, LITERAL_TESTS_DIR)
            self.assertEqual(
                cls.returncode, 0,
                msg=f"PD-7 control: validate-policy --classify falló "
                    f"(rc={cls.returncode}: {cls.stdout} {cls.stderr})")
            self.assertEqual(
                parse_classify(cls.stdout).get(LITERAL_TESTS_DIR),
                "implementation",
                msg=f"PD-7 control: el clasificador no da 'implementation' "
                    f"al tests/ literal NO declarado ({LITERAL_TESTS_DIR!r})")
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        with self.subTest(agent=TEST_WRITER, tool="read",
                          probe=LITERAL_TESTS_DIR):
            got = verdict(tw, "read", LITERAL_TESTS_DIR)
            self.assertEqual(
                got, "deny",
                msg=f"PD-7: el mapa `read` de {TEST_WRITER} resolvió "
                    f"read({LITERAL_TESTS_DIR!r}) como {got!r} — un tests/ "
                    f"literal NO declarado es implementación (nunca "
                    f"amplificar)")
        with self.subTest(agent=TEST_WRITER, tool="edit",
                          probe=LITERAL_TESTS_DIR):
            got = verdict(tw, "edit", LITERAL_TESTS_DIR)
            self.assertEqual(
                got, "deny",
                msg=f"PD-7: el mapa `edit` de {TEST_WRITER} resolvió "
                    f"edit({LITERAL_TESTS_DIR!r}) como {got!r}")
        with self.subTest(agent=IMPLEMENTER, tool="edit",
                          probe=LITERAL_TESTS_DIR):
            got = verdict(imp, "edit", LITERAL_TESTS_DIR)
            self.assertEqual(
                got, "allow",
                msg=f"PD-7: el mapa `edit` de {IMPLEMENTER} resolvió "
                    f"edit({LITERAL_TESTS_DIR!r}) como {got!r} — "
                    f"sobre-restricción: es implementación")
        all_pub = require_derived(
            self, self.root,
            tuple(sorted(published_derived(self.root))))
        flagged: list[tuple[str, str, str, str]] = []
        for name, text in sorted(all_pub.items()):
            flagged.extend(
                (name, tool, pattern, verb)
                for tool, pattern, verb
                in undeclared_convention_rules(text, UNDECLARED_T_PROBES))
        self.assertEqual(
            flagged, [],
            msg=f"PD-7/INV-3: existen reglas de convención GLOBAL en los "
                f"derivados (matchean sondas NO declaradas con forma de test "
                f"Perl {UNDECLARED_T_PROBES!r}): {flagged!r} — solo se "
                f"reabren los árboles/archivos declarados")


# --------------------------------------------------------------- PD-8


class TestPd8ConventionalLayoutNoRegression(LayoutProject):
    """PD-8: un layout convencional funciona sin regresión (veredictos
    idénticos al comportamiento previo a la corrección)."""
    LAYOUT = "conventional"

    def test_pd8_conventional_layout_verdicts_unchanged(self) -> None:
        """PD-8: con implementación src/lib, test_roots ['tests'] y
        co-ubicados por prefijo/sufijo, los veredictos del test-writer y del
        implementer coinciden con los previos a la corrección: lectura de
        implementación denegada, tests y co-ubicados permitidos, implementer
        edita implementación y ningún test."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"prepare del fixture (precondición): "
                f"{proc.stdout} {proc.stderr}")
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        expectations = (
            (TEST_WRITER, tw, "read", "src/app.py", "deny"),
            (TEST_WRITER, tw, "read", "src/test_mod.py", "allow"),
            (TEST_WRITER, tw, "edit", "src/test_mod.py", "allow"),
            (TEST_WRITER, tw, "edit", "src/app.py", "deny"),
            (TEST_WRITER, tw, "read", "tests/test_a.py", "allow"),
            (TEST_WRITER, tw, "edit", "tests/test_a.py", "allow"),
            (IMPLEMENTER, imp, "edit", "src/app.py", "allow"),
            (IMPLEMENTER, imp, "edit", "src/test_mod.py", "deny"),
            (IMPLEMENTER, imp, "edit", "tests/test_a.py", "deny"),
        )
        for agent, text, tool, probe, expected in expectations:
            with self.subTest(agent=agent, tool=tool, probe=probe):
                got = verdict(text, tool, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"PD-8: {agent} — {tool}({probe!r}) resolvió "
                        f"{got!r}, el layout convencional exige "
                        f"{expected!r} (no-regresión)")


# --------------------------------------------------------------- PD-9


class TestPd9NoSearchPathEntries(PerlLayoutProject):
    """PD-9/W-2: ningún derivado gana entradas por ruta en grep/glob."""

    def test_pd9_no_grep_glob_path_entries(self) -> None:
        """PD-9: para TODOS los derivados publicados con la política de tests
        anidados, los mapas `grep` y `glob` NO contienen entradas por ruta de
        la política (helper reutilizado de T5; W-2: en OpenCode grep/glob se
        median por el patrón de búsqueda — declararlas sería una barrera
        inexistente)."""
        self.prepare_perl(private=(f"{TEST_TREE}/secret.local",),
                          extra_files=(f"{TEST_TREE}/secret.local",))
        pub = require_derived(
            self, self.root,
            tuple(sorted(published_derived(self.root))))
        probes = (
            IMPL, f"{IMPL}/w2_probe", TEST_TREE, f"{TEST_TREE}/w2_probe",
            MAIN, CGI, BASIC, HELPER, f"{TEST_TREE}/secret.local",
            "docs", "docs/w2_probe",
        )
        assert_no_search_path_entries(self, pub, probes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
