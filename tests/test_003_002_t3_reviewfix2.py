#!/usr/bin/env python3
"""003-002 T3 RED review-fix ronda 2 — hallazgos F1/F2 de re-review T3.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (P5 y §8: «Sólo se admiten argv
  cuyo prefijo sea exactamente `python3 -m unittest`», los argumentos
  posteriores son argv; «Las selecciones son roots/paths explícitos; si no
  puede demostrarse que cubren lo relevante, la equivalencia es unknown»;
  snapshots «descubre archivos tracked y untracked no ignorados, ordena
  paths project-relative, calcula SHA-256 por archivo»; Limitaciones: «una
  selección incompleta o desconocida degrada a stale/unknown, no a verde»).

Mapa hallazgo → test (cada test nombra su hallazgo y su postcondición P5):

- F1 (BLOCKING) — argv en la forma admitida por §8 `python3 -m unittest
  <modulo>` (SIN `discover`) escapa al binding argv↔selecciones: hoy sólo
  se manejan `-s`/`--start-directory`, así que con `test_selection`
  irrelevante y mutación del test ejecutado entre corrida y validación,
  `validate-run-evidence` da `valid-current` falso. §8 exige degradar a
  `unknown` salvo que el árbol del módulo ejecutado (dotted → path) esté
  declarado en `test_selection`:
  - `test_f1_module_argv_with_declared_tree_stays_green` (LOCK/F1) — argv
    módulo con `test_selection=["tests"]` (árbol del módulo ejecutado
    declarado) sigue aprobando `valid-current`; la regla nueva no rompe el
    caso bueno.
  - `test_f1_module_argv_undeclared_tree_degrades_without_mutation` —
    argv módulo con `test_selection=["docs"]` (irrelevante: no declara el
    árbol ejecutado) ⇒ degrade a unknown, jamás gate verde, AUNQUE no haya
    mutación.
  - `test_f1_module_argv_undeclared_tree_executed_mutation_caught` —
    mismo sesgo + MUTAR el archivo test EJECUTADO (`tests/test_fixture.py`)
    entre corrida y validación ⇒ no `valid-current`: la revalidación de
    las selecciones declaradas (docs/) no puede cazar la mutación; sólo el
    binding dotted→path del argv la revela.

- F2 (BLOCKING) — descubrimiento git con `ls-files` sin `-z`: un nombre
  con caracteres especiales/no-ASCII vuelve como C-string entrecomillado
  (core.quotepath) y DESAPARECE de la snapshot; su mutación es invisible y
  produce `valid-current` falso. Debe listar con `-z` y separar por NUL:
  - `test_f2_non_ascii_name_is_snapshot_scheduled` — repo git del fixture
    con `src/árbol-fixture.py` TRACKED; la snapshot de la selección `src/`
    debe programar el path REAL (no su C-string comillada). LOCK parcial:
    la validación inmediata sin mutación sigue `valid-current`.
  - `test_f2_non_ascii_name_mutation_invalidates` — mutar ese archivo
    entre corrida y validación ⇒ no `valid-current` (hoy: el archivo no
    está en la snapshot ⇒ mutación invisible ⇒ falso verde).

Los locks de la batería R1–R3 y RED original NO se repiten aquí (58/58
verdes); cada negative test lleva el control positivo interno
`green_cycle()` del MISMO proyecto, que es por sí el lock de que la regla
nueva no rompe el caso bueno.

Superficie observable: CLI de §2 (`run-python-unittest`,
`validate-run-evidence`), evidencia JSON por stdout y su revalidación.
Corridas del CLI con cwd en la raíz del repo; fixtures son tempdirs;
nunca se lee implementación. RED hoy: cada vector fracasa por aserción del
comportamiento ausente (los experimentos terminan `valid-current`), no por
ImportError.
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from tests.test_003_002_t3_reviewfix import T3ReviewFixCase
from tests.test_003_002_t3_run_evidence import (
    decode,
    parse_json_or_none,
    walk_nodes,
)

# F1: forma módulo admitida por §8 (prefijo exacto `python3 -m unittest`;
# el resto es argv, sin shell). The fixture package is `tests.test_fixture`
# (namespace package del proyecto sintético).
MODULE_ARGV = ["python3", "-m", "unittest", "tests.test_fixture"]

# Selección irrelevante: declara docs/ y NO el árbol del módulo ejecutado.
SKEWED_SOURCE = ["src"]
SKEWED_TEST = ["docs"]

# F1: mutación del test ejecutado entre corrida y validación (los bytes
# cambian; las selecciones declaradas docs/ siguen intactas).
F1_MUTATED_MODULE = b"""import unittest


class TestFixtureGreen(unittest.TestCase):
    def test_green_ok(self) -> None:
        self.assertTrue(True)


# f1 mutation: module-form argv must bind the tests/ tree
"""
F1_MUTATED_COUNT_WARNING = (
    "argv módulo con test_selection irrelevante (docs/) y MUTACIÓN del "
    "test ejecutado tests/test_fixture.py entre corrida y validación")

# F2: nombre con caracteres no-ASCII (git core.quotepath lo imprime como
# C-string entrecomillado si no se usa `-z`), TRACKED en el repo git del
# fixture, bajo la selección source `src/`.
UNICODE_SRC = "src/árbol-fixture.py"


# ------------------------------------------------------------------- suite


class T3ReviewFix2Case(T3ReviewFixCase):
    """Base ronda 2: reutiliza el fixture dispatched de la batería RED."""

    # -- oráculo ------------------------------------------------------------

    def assert_scheduled_path(self, evidence: dict, relpath: str) -> None:
        """El path REAL (sin C-string comillada) debe aparecer programado
        en los entries de snapshot expuestos por la evidencia (§8: paths
        project-relative)."""
        seen: list[str] = []
        for node in walk_nodes(evidence):
            if isinstance(node, dict):
                value = node.get("path")
                if isinstance(value, str):
                    seen.append(value)
                    if value == relpath:
                        return
        self.fail(
            "P5 (F2, §8 'tracked y untracked no ignorados'): la snapshot "
            "debe programar el path REAL " + repr(relpath) + "; con "
            "`ls-files` sin -z el nombre vuelve comillado como C-string y "
            "el archivo desaparece de la snapshot; paths observados: "
            + ", ".join(seen[:12]))


# ------------------------------------------------------- F1 (BLOCKING)


class TestF1ModuleArgvBinding(T3ReviewFix2Case):
    """F1 — binding del argv módulo (sin discover) a las selecciones."""

    def test_f1_module_argv_with_declared_tree_stays_green(self) -> None:
        """F1/P5 (LOCK): argv módulo con `test_selection=["tests"]` — el
        árbol del módulo ejecutado (`tests.test_fixture` → `tests/`) está
        declarado — aproba `valid-current` y registra evidencia mecánica
        completa. La regla de binding no rompe el caso bueno."""
        self.new_dispatched_project()
        run_json = self.run_request_path(argv=list(MODULE_ARGV))
        proc = self.run_run_python_unittest(run_json)
        evidence = self.save_evidence(proc, run_json)
        self.assert_mechanical_evidence(evidence, list(MODULE_ARGV))
        self.must_be_current(self.validate_last())

    def test_f1_module_argv_undeclared_tree_degrades_without_mutation(
            self) -> None:
        """F1/P5: argv módulo con `test_selection=["docs"]` (el árbol del
        módulo ejecutado NO está declarado) ⇒ binding argv↔selecciones no
        demostrable ⇒ degrade a unknown: nunca gate verde, aunque no haya
        mutación (§8: selección que no cubre lo relevante no es verde).
        Control positivo previo: el mismo proyecto con argv discover y
        selecciones correctas sí aprueba."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(MODULE_ARGV),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST),
        )
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    def test_f1_module_argv_undeclared_tree_executed_mutation_caught(
            self) -> None:
        """F1/P5 (vector central): argv módulo + test_selection irrelevante
        + MUTAR el archivo test EJECUTADO entre corrida y validación ⇒ la
        revalidación NO puede aprobar `valid-current`: las selecciones
        declaradas (docs/) siguen intactas; sólo el binding
        dotted→path (`tests.test_fixture` → `tests/`) detecta el drift.
        Si la corrida rechaza upfront, la regla ya se aplicó."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(MODULE_ARGV),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST),
        )
        proc = self.run_run_python_unittest(run_json)
        if proc.returncode != 0 or parse_json_or_none(proc) is None:
            return  # rechazo upfront por binding no demostrable: regla ok
        self.save_evidence(proc, run_json)
        self.write_test_module(F1_MUTATED_MODULE)
        self.must_not_be_current(
            self.validate_last(),
            "F1: " + F1_MUTATED_COUNT_WARNING)


# ------------------------------------------------------- F2 (BLOCKING)


class TestF2GitListingZ(T3ReviewFix2Case):
    """F2 — descubrimiento git con `-z` (NUL), sin citar paths."""

    def git_run(self, *args: str) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True)
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición (fixture): `git " + " ".join(args) +
                "` con código 0; " + decode(proc.stderr)[:300])
        return proc

    def git_init_commit(self) -> None:
        self.git_run("init", "-q")
        self.git_run("-c", "user.email=fixture@example.invalid",
                     "-c", "user.name=fixture", "add", "-A")
        self.git_run("-c", "user.email=fixture@example.invalid",
                     "-c", "user.name=fixture", "commit", "-q",
                     "-m", "fixture base")

    def setup_gitified_unicode_fixture(self) -> None:
        """Fixture git con un archivo TRACKED de nombre no-ASCII bajo la
        selección source `src/` (con core.quotepath por defecto, git sin
        -z imprime su path como C-string entrecomillada)."""
        self.new_dispatched_project()
        (self.root / UNICODE_SRC).write_bytes(b"fixture utf8 tracked\n")
        self.git_init_commit()
        listed = self.git_run("ls-files", "-z", UNICODE_SRC)
        self.assertIn(
            UNICODE_SRC, decode(listed.stdout),
            msg="precondición (fixture): git debe trackear " +
                repr(UNICODE_SRC))

    def test_f2_non_ascii_name_is_snapshot_scheduled(self) -> None:
        """F2/P5 (§8 'tracked y untracked no ignorados'): el archivo
        TRACKED de nombre no-ASCII debe aparecer en la snapshot de la
        selección `src/` con su path REAL; con `ls-files` sin -z su path
        vuelve comillado y merece desaparecer de la snapshot. LOCK
        parcial: la validación inmediata sin mutación sigue `valid-
        current`."""
        self.setup_gitified_unicode_fixture()
        self.green_cycle()
        self.assert_scheduled_path(self.evidence_doc, UNICODE_SRC)
        self.must_be_current(self.validate_last())

    def test_f2_non_ascii_name_mutation_invalidates(self) -> None:
        """F2/P5 (vector central): MUTAR el archivo TRACKED de nombre
        no-ASCII entre corrida y validación ⇒ no `valid-current`. Hoy el
        archivo no integra la snapshot (path comillado por core.quotepath
        sin -z), la mutación es invisible y la revalidación da falso
        verde; con `-z` + separación por NUL el path real queda
        programado y el drift invalida."""
        self.setup_gitified_unicode_fixture()
        self.green_cycle()
        target = self.root / UNICODE_SRC
        target.write_bytes(target.read_bytes() + b"mutated\n")
        self.must_not_be_current(
            self.validate_last(),
            "F2: mutación de un archivo TRACKED con nombre no-ASCII "
            "(snapshot via ls-files -z + NUL) debe invalidar la "
            "evidencia")


if __name__ == "__main__":
    unittest.main()
