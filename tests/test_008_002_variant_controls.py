#!/usr/bin/env python3
"""008-002 T2 — controles negativos de variante (PC-3, oráculo de variantes).

Contract: docs/specs/008-002-suite-by-capability/spec.md (PC-3, §4
«Controles de variante») + variant-controls.json de la feature.

Por cada variante candidata a retirar, el control introduce la DESVIACIÓN
CONTRACTUAL sobre una copia sintética aislada (el proyecto temporal del
caso, nunca el checkout) y comprueba que el test DESTINO falla por esa
causa: exactamente un fallo (AssertionError), ningún error, y el mensaje
del fallo nombra la obligación desviada. Una corrida sin desviación del
mismo destino debe pasar (línea base: un fallo ambiental no se confunde
con detección).

Límite declarado: la desviación se inyecta en el ARTEFACTO OBSERVADO (el
registro I8 durable que el destino lee), no en el producto — el
test-writer no lee implementación. Es equivalente para un oráculo que sólo
observa artefactos durables; no prueba cómo se produciría la desviación.

Mapa control → variante:

  1  test_baseline_pd6_destination_passes_without_deviation
  2  test_r2_plain_text_model_null_detected_by_pd6_destination
       005-010 PD-6 (R2 contracara): `model_reported` de una fila con
       modelo en texto plano no se conserva (null).
  3  test_r2_plain_text_model_prefixed_detected_by_pd6_destination
       005-010 PD-6 (R2 contracara): la normalización 'proveedor/id' se
       aplica también al texto plano.
  4  test_r2_closed_i8_schema_extra_key_detected_by_pd6_destination
       005-010 PD-6 (R2 contracara): el registro I8 deja de ser el esquema
       cerrado (clave extra).
"""

from __future__ import annotations

import json
import unittest

import test_005_010_t1_durable_signal as t1
from test_005_009_t1_interface import dispatch_records

DESTINATION = "test_pd6_worker_i8_session_and_model_from_durable_row"


def run_destination(mutate=None) -> unittest.TestResult:
    """Corre el test destino PD-6 en su proyecto sintético; si `mutate`
    se da, reescribe los registros I8 del despacho tras la invocación y
    antes de que el cuerpo del test los lea."""

    class Deviated(t1.TestPd6WorkerI8FromDurableRow):
        def run_opencode(self, fake, **kwargs):
            proc = super().run_opencode(fake, **kwargs)
            if mutate is not None:
                for path in dispatch_records(
                        self.root, self.execution_id).values():
                    record = json.loads(path.read_text(encoding="utf-8"))
                    mutate(record)
                    path.write_text(json.dumps(record), encoding="utf-8")
            return proc

    result = unittest.TestResult()
    Deviated(DESTINATION).run(result)
    return result


class TestR2PlainTextVariantControls(unittest.TestCase):
    """Variante R2 contracara (reviewfix::test_r2_plain_text_row_model_is_
    preserved) candidata a retirar con destino PD-6 del módulo T1."""

    def assert_detected(self, result: unittest.TestResult,
                        *needles: str) -> None:
        self.assertEqual(result.errors, [], msg="el destino ERRÓ (no es "
                         "detección por la causa declarada)")
        self.assertEqual(
            len(result.failures), 1,
            msg=f"el destino no detectó la desviación {needles!r}")
        for needle in needles or ("model_reported", "fila durable (PD-6)"):
            self.assertIn(needle, result.failures[0][1])

    def test_baseline_pd6_destination_passes_without_deviation(self) -> None:
        """Sin este test, el usuario podría confundir un fallo ambiental con una regresión real."""
        result = run_destination()
        self.assertTrue(
            result.wasSuccessful(),
            msg=f"línea base: el destino no pasa sin desviación "
                f"{result.failures + result.errors!r}")

    def test_r2_plain_text_model_null_detected_by_pd6_destination(self) -> None:
        """Sin este test, el usuario podría perder silenciosamente el modelo registrado del despacho."""
        self.assert_detected(run_destination(
            lambda record: record.update(model_reported=None)))

    def test_r2_plain_text_model_prefixed_detected_by_pd6_destination(self) -> None:
        """Sin este test, el usuario podría recibir un modelo registrado distinto del informado."""
        self.assert_detected(run_destination(
            lambda record: record.update(
                model_reported=f"fixture-provider/{record['model_reported']}")))

    def test_r2_closed_i8_schema_extra_key_detected_by_pd6_destination(self) -> None:
        """Sin este test, el usuario podría recibir registros durables fuera del esquema acordado."""
        self.assert_detected(
            run_destination(lambda record: record.update(extra_key="x")),
            "extra_key", "esquema se conserva")


if __name__ == "__main__":
    unittest.main(verbosity=2)
