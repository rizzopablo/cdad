#!/usr/bin/env python3
"""004-002 T7 L-1 integración — la regla general de límites llega a los
DERIVADOS por proyecto (I9), no solo a la superficie canónica.

Contrato: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-7:
los scopes derivados llegan completos a los prompts; PD-8: los agentes
generados en .opencode/agents/ proceden de las fuentes canónicas) +
decisiones L-1 (owner 2026-10-02) en supervisión de T7.

Encargo del orquestador (paquete red-022): L-1 (717e6a7) inlineó la regla
general de límites en los agentes CANÓNICOS (marcador estable: el texto
"General write-scope rule"; verificado en la superficie canónica por
test_004_002_t7_limits_rule.py). Faltaba verificar que llega a los agentes
DERIVADOS por proyecto (I9: .opencode/agents/ que publica `prepare`).

Este test de INTEGRACIÓN es el camino del test canónico L-1 aplicado a la
superficie que consume un proyecto real: publications en tempdirs vía
prepare (fixtures T5 reutilizados: LayoutProject + helpers
require_derived / assert_no_search_path_entries) y los mismos marcadores
estables del test canónico (importados, no redefinidos): idea (b) y (c)
por párrafo, y el marcador textual de la regla.

SUPERFICIE OBSERVABLE (sin implementación): los derivados PUBLICADOS por
prepare (salidas declaradas del generador) en proyectos sintéticos y los
derivados de este repo regenerados por el prepare del orquestador (el
hermano canónico ya los lee bajo el mismo precedente). No se lee el CLI ni
agents/ (raíces de implementación). No se lee tests/.sensitive-patterns.local.

W-2 (t7-live-walk.md §3): en OpenCode grep/glob se median por el patrón de
búsqueda — los derivados siguen SIN entradas por ruta en `grep`/`glob`.

ORACLE STATUS (declarado en el encargo): si la integración ya funciona el
test pasa VERDE de entrada — esta es la verificación de integración del
plan (no hay implementación pendiente que produzca RED; L-1 ya integró la
regla en la fuente y prepare la propaga por derivación). Fallo si la
integración se rompe (regresión) con AssertionError sobre la postcondición.

Mapa test → postcondición:
  test_l1_derived_rule_b_and_c_and_marker
    -> PD-7/PD-8 + L-1 (integración): para los 3 layouts (cdad,
       conventional, odoo), CADA derivado publicado contiene las ideas
       (b) y (c) de L-1 en los mismos marcadores del test canónico, y el
       marcador textual "General write-scope rule" de L-1.
  test_w2_deriveds_still_no_path_search_entries (mismo test, subcontrol)
    -> W-2: los derivados publicados siguen SIN entradas por ruta en
       `grep`/`glob` (regla W-2 conservada; mismo marcador que
       test_004_002_t7_w2.py).
"""

from __future__ import annotations

import unittest

# Marcadores estables L-1 (canónicos): importados, no redefinidos.
from test_004_002_t7_limits_rule import (  # noqa: E402
    DENIED_RE,
    INVALID_RE,
    AUDIT_RE,
    NO_RETRY_NO_BYPASS_RE,
    OUT_OF_SCOPE_RE,
    STOP_REPORT_RE,
    find_paragraph,
)
from test_004_002_t5_runtime import (  # noqa: E402
    LayoutProject,
    assert_no_search_path_entries,
    policy_path_probes,
    published_derived,
    require_derived,
)

L1_MARKER = "General write-scope rule"


class TestL1DerivedIntegration(LayoutProject):
    """L-1 integración (PD-7/PD-8): la regla general de límites que L-1
    inlineó en los agentes canónicos llega a CADA derivado publicado por
    prepare, en los 3 layouts del contrato, con los mismos marcadores del
    oráculo canónico (test_004_002_t7_limits_rule.py) + W-2."""

    def test_l1_derived_rule_b_and_c_and_marker(self) -> None:
        """I9/PD-7/PD-8 + L-1 (integración): cada derivado publicado por
        prepare contiene, por párrafo, (b) invalid* + audit + fuera-de-
        scope/write_scope y (c) denied/deneg + stop/report +
        retry/reintent/bypass/sortear/rodeo, y el marcador textual
        "General write-scope rule". ESTADO DECLARADO: verificación de
        integración del plan — pasa verde de entrada si la integración
        funciona; falla como AssertionError de postcondición ante una
        regresión."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = published_derived(self.root)
        names = tuple(n for n in sorted(pub)
                      if n.startswith("cdad-") and n.endswith(".md"))
        self.assertTrue(
            names,
            msg="precondición: el prepare no publicó derivados cdad-*.md")
        for name in names:
            text = require_derived(self, self.root, (name,))[name]
            with self.subTest(agent=name):
                self.assertIn(
                    L1_MARKER, text,
                    msg=f"L-1 integración: {name} no contiene el marcador "
                        f"de la regla general de límites {L1_MARKER!r} "
                        "(regla L-1 en el bloque compartido del agente "
                        "canónico; PD-7: los scopes derivados llegan "
                        "completos a los prompts)")
                self.assertTrue(
                    find_paragraph(text, INVALID_RE, AUDIT_RE,
                                   OUT_OF_SCOPE_RE),
                    msg=f"L-1(b) integración: {name} no inlinea la idea "
                        "(b) — escribir fuera del alcance o sortear un "
                        "límite NO adelanta el trabajo: el orquestador lo "
                        "audita y el resultado se invalida (mismos "
                        "marcadores del oráculo canónico L-1)")
                self.assertTrue(
                    find_paragraph(text, DENIED_RE, STOP_REPORT_RE,
                                   NO_RETRY_NO_BYPASS_RE),
                    msg=f"L-1(c) integración: {name} no inlinea la idea "
                        "(c) — un bloqueo de trabajo legítimo exige "
                        "detenerse y reportar al orquestador con "
                        "evidencia, sin reintentos equivalentes ni rodeos "
                        "(mismos marcadores del oráculo canónico L-1)")

    def test_l1_w2_deriveds_still_no_path_search_entries(self) -> None:
        """W-2 (conservación, mismo layout sin sondear claude-code) y L-1
        — la integración L-1 no reintroduce entradas por ruta en
        `grep`/`glob` de los derivados (t7-live-walk.md §3)."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = require_derived(
            self, self.root,
            tuple(n for n in sorted(published_derived(self.root))))
        assert_no_search_path_entries(self, pub, policy_path_probes(self.LAYOUT))


class TestL1DerivedIntegrationCdad(TestL1DerivedIntegration):
    """L-1 integración, layout CDAD (el de este repo)."""
    LAYOUT = "cdad"


class TestL1DerivedIntegrationConventional(TestL1DerivedIntegration):
    """L-1 integración, layout convencional."""
    LAYOUT = "conventional"


class TestL1DerivedIntegrationOdoo(TestL1DerivedIntegration):
    """L-1 integración, layout Odoo."""
    LAYOUT = "odoo"


if __name__ == "__main__":
    unittest.main(verbosity=2)
