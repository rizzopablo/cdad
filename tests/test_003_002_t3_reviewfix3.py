#!/usr/bin/env python3
"""003-002 T3 RED review-fix ronda 3 — R-F1a/R-F1b residuales de re-review r2.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (P5 y §8: «Sólo se admiten argv
  cuyo prefijo sea exactamente `python3 -m unittest`», los argumentos
  posteriores son argv; «Las selecciones son roots/paths explícitos; si no
  puede demostrarse que cubren lo relevante, la equivalencia es unknown»;
  Limitaciones: «una selección incompleta o desconocida degrada a stale/
  unknown, no a verde»).
- Re-review T3 ronda 2 (dictamen reviewer, estado `review-3-t3`,
  `changes-required`): persisten 2 residuales de F1 con escape de CLASE —
  el binding dotted→path de r2 sólo cubre los argv que empiezan con el
  módulo; cualquier forma donde la opción precede al módulo o donde el
  módulo es un paquete de un segmento sigue produciendo `valid-current`
  falso con test_selection sesgada y mutación del test ejecutado.

Mapa hallazgo → test (cada test nombra su hallazgo y su postcondición P5):

- R-F1a (BLOCKING) — `python3 -m unittest -v <modulo>` (la opcion ANTES
  del modulo) escapa al binding de r2: hoy devuelve valid-current con
  test_selection sesgada (docs/) y mutación del test ejecutado.
  Remedio exigido (FAIL-CLOSED): la forma no plenamente ligable a
  test_selection degrada a unknown.
  - `test_rf1a_option_before_module_degrades_with_executed_mutation` —
    argv `-v tests.test_fixture` + test_selection=["docs"] + mutar el
    archivo test EJECUTADO ⇒ nunca `valid-current`.
  - `test_rf1a_option_before_module_degrades_without_mutation` — mismo
    argv con selecciones sesgadas SIN mutación ⇒ también degrada (la
    regla es de CLASE: el binding no demostrable basta).

- R-F1b (BLOCKING) — `python3 -m unittest <paquete-de-un-segmento>`
  (`tests` con hook `load_tests` en `__init__.py`: corre 1 test verde)
  idem R-F1a: valid-current falso con selecciones sesgadas.
  - `test_rf1b_one_segment_package_degrades_with_executed_mutation` —
    argv `tests` + test_selection=["docs"] + mutación de `tests/__init__.py`
    (el hook ejecutado) ⇒ nunca `valid-current`.
  - `test_rf1b_one_segment_package_degrades_without_mutation` — idem sin
    mutación ⇒ degrada igualmente.

- FAIL-CLOSED por defecto (remedio de CLASE, no por variante): una forma
  de argv que NO es de la whitelist explícita de opciones invariantes a
  la selección degrada. `-k <patrón>` (una opción estándar de unittest
  conocida — no exótica) CAMBIA qué tests se ejecutan: no es invariante
  a la selección y jamás puede aprobarse como gate verde.
  - `test_rf1c_unknown_option_form_never_green_gate` — argv
    `discover -s tests -k green_ok` AUN con la selección correcta
    `test_selection=["tests"]` ⇒ degrada (el caso general: fail-closed
    no por enumeración; `-k` cambia qué tests corren).

- LOCK del caso bueno (la regla no rompe la config canónica §8):
  - `test_rf1d_discover_with_correct_selection_still_green` —
    `discover -s tests` con `test_selection=["tests"]` sigue aprobando
    `valid-current` (control de la batería T3, repetido aquí como lock
    explícito de la regla fail-closed).

Los locks previos (63 verdes: batteries RED, review-fix r1 y r2) NO se
repiten uno a uno: cada test negativo de esta batería corre primero el
control positivo `green_cycle()` del MISMO proyecto (corrida discover
con selecciones correctas ⇒ `valid-current`), que es por sí el lock de
que la regla fail-closed nueva no rompe el caso bueno.

Superficie observable: CLI de §2 (`run-python-unittest`,
`validate-run-evidence`), evidencia JSON por stdout y su revalidación.
Corridas del CLI con cwd en la raíz del repo; fixtures son tempdirs;
nunca se lee implementación. RED hoy: cada vector fracasa por aserción
del comportamiento ausente (los experimentos terminan `valid-current`,
verificado como baseline por el test-writer), no por ImportError.
"""
from __future__ import annotations

import unittest

from tests.test_003_002_t3_reviewfix import T3ReviewFixCase
from tests.test_003_002_t3_run_evidence import (
    parse_json_or_none,
    decode,
)

# --------------------------------------------------------------- R-F1a/F1b

# R-F1a: opción ESTÁNDAR de unittest ANTES del módulo (lege form del
# escape; el binding dotted→path de r2 sólo dispara cuando el primer
# argumento post-`unittest` es el módulo).
RF1A_ARGV = ["python3", "-m", "unittest", "-v", "tests.test_fixture"]

# R-F1b: paquete de UN segmento. El fixture `tests/` lleva un
# `__init__.py` con hook `load_tests` que hace que esta forma ejecute
# exactamente 1 test verde (verificado contra unittest stdlib, rc 0).
RF1B_ARGV = ["python3", "-m", "unittest", "tests"]

# Selección irrelevante: declara docs/ y NO el árbol ejecutado.
SKEWED_SOURCE = ["src"]
SKEWED_TEST = ["docs"]

# R-F1c (fail-closed general): `-k` no es invariante a la selección
# (cambia qué tests corren: una corrida con `-k` puede NO ejercitar el
# árbol declarado aunque el discover cubra tests/). El argv NO puede
# ligarse COMPLETAMENTE a test_selection ⇒ degrada aunque la selección
# sea la correcta (fail-closed por defecto, no por enumeración).
RF1C_ARGV = ["python3", "-m", "unittest", "discover",
             "-s", "tests", "-k", "green_ok"]

# Mutación de R-F1b del archivo EJECUTADO por el hook (tests/__init__.py).
INIT_MODULE_MUTATED = b"""import unittest
from . import test_fixture


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromModule(test_fixture)


# rf1b mutation: one-segment package argv must bind tests/ tree
"""

INIT_MODULE_BASE = b"""import unittest
from . import test_fixture


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromModule(test_fixture)
"""

TEST_MODULE_MUTATED = b"""import unittest


class TestFixtureGreen(unittest.TestCase):
    def test_green_ok(self) -> None:
        self.assertTrue(True)


# rf1a mutation: option-before-module argv must bind the tests/ tree
"""


def one_segment_fixture(case: T3ReviewFixCase) -> None:
    """Fixture R-F1b: proyecto dispatched cuyo paquete `tests` tiene el
    hook `load_tests` (argv de un segmento corre 1 test verde)."""
    case.new_dispatched_project()
    (case.root / "tests" / "__init__.py").write_bytes(INIT_MODULE_BASE)


# ------------------------------------------------------------------- suite


class TestRF1FailClosed(T3ReviewFixCase):
    """Ronda 3 — bind fail-closed: argv no plenamente ligable ⇒ degrada."""

    def green_cycle_locked(self) -> None:
        """Control positivo de la variante R-F1b: la forma de un segmento
        con `test_selection=["tests"]` correcta AUN aprueba si la
        implementación la soporta; si no, el control falla con mensaje
        explícito (lock del caso bueno, no assertion de RED)."""
        run_json = self.run_request_path(
            argv=list(RF1B_ARGV),
            source_selection=["src"],
            test_selection=["tests"])
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is None:
            self.fail(
                "P5 (precondición del vector R-F1b): el fixture con hook "
                "load_tests debe poder correr y exponer evidencia; obtuve "
                f"rc={proc.returncode} {decode(proc.stdout)} "
                f"{decode(proc.stderr)}")
        self.save_evidence(proc, run_json)
        self.must_be_current(self.validate_last())

    def skewed_cycle(self, argv: list[str]) -> dict:
        """Corrida del vector sesgado. Devuelve dict con proc/run_json y
        marca `rejected_upfront` si la corrida rechaza de entrada."""
        run_json = self.run_request_path(
            argv=list(argv),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST))
        proc = self.run_run_python_unittest(run_json)
        result = {"proc": proc, "run_json": run_json}
        if proc.returncode != 0 or parse_json_or_none(proc) is None:
            result["rejected_upfront"] = True
        return result

    # -- R-F1a --------------------------------------------------------------

    def test_rf1a_option_before_module_degrades_with_executed_mutation(
            self) -> None:
        """R-F1a/P5 (vector central): `-v <modulo>` con test_selection
        sesgada (docs/) y MUTACIÓN del test ejecutado entre corrida y
        validación ⇒ la forma no es plenamente ligable a test_selection ⇒
        FAIL-CLOSED: degrade a unknown; jamás gate verde."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(RF1A_ARGV),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST))
        proc = self.run_run_python_unittest(run_json)
        if proc.returncode != 0 or parse_json_or_none(proc) is None:
            return  # rechazo upfront por binding no demostrable: regla ok
        self.save_evidence(proc, run_json)
        self.write_test_module(TEST_MODULE_MUTATED)
        self.must_not_be_current(
            self.validate_last(),
            "R-F1a: 'python3 -m unittest -v tests.test_fixture' con "
            "test_selection sesgada (docs/) y mutación del test ejecutado "
            "tests/test_fixture.py debe degradar (fail-closed), no "
            "aprobar valid-current")

    def test_rf1a_degrades_even_without_mutated_executed_test(
            self) -> None:
        """R-F1a/P5: el binding no demostrable degrada POR LA FORMA del
        argv, no por la mutación: sin drift del árbol, `-v <modulo>` con
        test_selection irrelevante igual declina el gate (fail-closed de
        clase; nunca valid-current)."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(RF1A_ARGV),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST))
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    # -- R-F1b --------------------------------------------------------------

    def test_rf1b_one_segment_package_degrades_with_executed_mutation(
            self) -> None:
        """R-F1b/P5 (vector central): `<paquete-de-un-segmento>` (hook
        load_tests en tests/__init__.py: corre 1 test verde) con
        test_selection sesgada y mutación del hook ejecutado ⇒
        FAIL-CLOSED: degrada, jamás gate verde.
        Control: la MISMA forma con test_selection=["tests"] correcta
        sigue aprobando (lock del caso bueno de la regla)."""
        one_segment_fixture(self)
        self.green_cycle_locked()
        skewed = self.skewed_cycle(list(RF1B_ARGV))
        if skewed.get("rejected_upfront"):
            return  # rechazo upfront: regla fail-closed ya aplicada
        proc = skewed["proc"]
        self.save_evidence(proc, skewed["run_json"])
        (self.root / "tests" / "__init__.py").write_bytes(
            INIT_MODULE_MUTATED)
        self.must_not_be_current(
            self.validate_last(),
            "R-F1b: 'python3 -m unittest tests' (paquete con load_tests) "
            "con test_selection sesgada y mutación de tests/__init__.py "
            "(hook ejecutado) debe degradar, no aprobar valid-current")

    def test_rf1b_degrades_even_without_mutation(self) -> None:
        """R-F1b/P5: binding no demostrable ⇒ degrada sin necesidad de
        mutación (fail-closed de CLASE; control positivo previo con
        selecciones correctas del mismo proyecto)."""
        one_segment_fixture(self)
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(RF1B_ARGV),
            source_selection=list(SKEWED_SOURCE),
            test_selection=list(SKEWED_TEST))
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    # -- fail-closed general (whitelist de opciones invariantes) -------------

    def test_rf1c_unknown_option_form_never_green_gate(self) -> None:
        """R-F1b (clase)/P5: una forma con opción desconocida/ambigua
        (`-k <patron>`: NO invariante a la selección porque puede no
        ejercitar el árbol declarado) TAMBIÉN degrada AUN con la selección
        correcta `test_selection=["tests"]`: FAIL-CLOSED por defecto, no
        por enumeración de variantes. Cualquier argv que no pueda ligarse
        COMPLETAMENTE a test_selection jamás produce gate verde.
        Control positivo previo: la forma discover sin `-k` del MISMO
        proyecto sí aprueba (green_cycle)."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(
            argv=list(RF1C_ARGV),
            source_selection=["src"],
            test_selection=["tests"])
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    # -- LOCK del caso bueno -------------------------------------------------

    def test_rf1d_discover_with_correct_selection_still_green(self) -> None:
        """LOCK/P5 (remedio de CLASE no rompe el caso bueno §8):
        `discover -s tests` con `test_selection=["tests"]` sigue
        aprobando `valid-current` con la regla fail-closed activa.
        (Control canónico repetido como lock explícito de la ronda 3;
        los 63 locks previos no se duplican aquí.)"""
        self.new_dispatched_project()
        self.green_cycle()  # es la config canónica exacta del contrato §8


if __name__ == "__main__":
    unittest.main()
