#!/usr/bin/env python3
"""006-002 U4 RED — `SKILL.md` §2 sin modelos (PD-11; INV-2/INV-7).

Contract:
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-11**, §3
  **INV-2**/INV-7, §4 **D-6**;
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha **U4** (archivos:
  ``SKILL.md:67-77``, ``handoff-prompts.md:515``, F001 de
  ``tests/validate-consistency.sh``) + **enmienda A-1** (los asserts acoplados
  de esta superficie se reformulan en ESTE RED, nunca en el GREEN).

PD-11 — §2 pierde la columna "Model family" (``SKILL.md:67-75``) y el párrafo de
perfiles (``:77``); en su lugar queda UNA frase: el modelo de cada rol es **el
configurado en el runtime**, la skill **no nombra modelos**, y la familia
distinta del reviewer es una **invariante garantizada por configuración** cuando
el perfil fija modelos y **declarada** cuando no (nunca omitida en silencio:
INV-7). ``references/handoff-prompts.md:515`` pierde su ejemplo de modelo
concreto. F001 de ``tests/validate-consistency.sh`` se **reformula, no se
borra** (esa reformulación es parte de este mismo RED — enmienda A-1).

Oráculo de ausencia (spec §2, cabecera): el patrón ya fijado por
``tests/test_005_010_t3_references.py`` (``CONCRETE_MODEL_ID_RE``,
``SPACED_MODEL_LINE_RE``, ``PROVIDER_RE``), reusado por el helper
``model_offences`` de ``tests/test_006_002_u2_neutral_skill.py`` — una sola
definición, sin copiar patrones. Delimitación de §2 y ``require_any``: mismos
helpers de u2 (``numbered_section_region``, ``line_of``).

Mapa test → postcondición (un test por afirmación observable):
  1 ``TestPd11Section2WithoutModels::test_pd11_section2_drops_the_model_family_column``       PD-11 / D-6
  2 ``TestPd11Section2WithoutModels::test_pd11_section2_drops_the_profiles_paragraph``        PD-11 / D-6
  3 ``TestPd11Section2WithoutModels::test_pd11_section2_has_no_concrete_model_identifier``    PD-11 / INV-2
  4 ``TestPd11Section2WithoutModels::test_pd11_section2_declares_the_configured_model_sentence`` PD-11 / INV-7
  5 ``TestPd11HandoffPromptsWithoutModelExamples::test_pd11_handoff_prompts_has_no_concrete_model_example`` PD-11 / INV-2

RED esperado (árbol actual — U4 aún no implementada; estado OBSERVADO):
- (1)/(2)/(4): FALLAN por AssertionError de CONTENIDO sobre §2 (líneas 65-83):
  columna "Model family" presente; párrafo de perfiles presente (ofensor en
  ``:77``, exactamente la línea que el spec declara); la frase nueva ausente
  (faltan los conceptos 1 «modelo configurado en el runtime», 2 «la skill no
  nombra modelos», 6 «garantizada por configuración» y 7 «declarada»).
- (3): FALLA por AssertionError de CONTENIDO (12 identificadores de modelo/
  proveedor concretos en §2: ``deepseek-v4-pro``, ``deepseek-v4-flash``,
  ``glm-5.2``, proveedor ``deepseek``) — no es un guard pre-satisfecho.
- (5): FALLA por AssertionError de CONTENIDO: el ejemplo declarado por discovery
  §1 #18 (``mofgw/qwen3.7-plus``) sigue en ``handoff-prompts.md``. Forma que el
  oráculo compartido NO captura (``CONCRETE_MODEL_ID_RE`` exige el guion pegado
  a la familia y aquí la versión se interpone); se declara el patrón de esta
  unidad (``EMBEDDED_VERSION_MODEL_RE``) por el ejemplo que el propio contrato
  nombra.
Ningún fallo es ImportError/SyntaxError.

Acoplados reformulados en este RED (enmienda A-1, cada RED cubre su superficie):
- ``tests/test_006_002_u2_neutral_skill.py``: se retira la neutralización
  TEMPORAL de §2 del oráculo de modelos (PD-1/INV-2) — la ausencia de modelos
  concretos rige ahora sobre todo el texto instalable salvo ``context-meter.md``
  (INV-8); su mitad de modelos falla hoy por los ofensores de esta unidad.
- ``tests/validate-consistency.sh`` F001: la nota de perfiles (`--basic` + el
  caveat de la invariante) deja de exigirse en ``SKILL.md`` y pasa a exigir la
  frase nueva de §2 (SKILL.md) + el caveat de ``basic`` donde todavía
  corresponde (los orquestadores generados, cuya sección ``delegation`` ya
  declara la familia no garantizada — PD-4/D-3, U1).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Helper único del oráculo (una sola definición): §2 delimitada por su encabezado
# numerado, el oráculo de modelos y las utilidades de idioma — de u2.
from tests.test_006_002_u2_neutral_skill import (
    line_of,
    model_offences,
    numbered_section_region,
    relative,
    require_any,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"
HANDOFF_PROMPTS = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                   / "handoff-prompts.md")


def read(path: Path) -> str:
    """Artefacto de U4 (producto del movimiento de texto): existe y no está
    vacío; el oráculo jamás lee implementación de producto."""
    assert path.is_file(), (
        "PD-11: el oráculo apunta a un documento instalable inexistente (drift "
        f"de la superficie declarada): {relative(path)}"
    )
    text = path.read_text(encoding="utf-8")
    assert text.strip(), (
        f"PD-11: el documento instalable está vacío: {relative(path)}"
    )
    return text


# --------------------------------------------------------------------------
# PD-11 — el ejemplo de modelo concreto de `handoff-prompts.md:515`
# --------------------------------------------------------------------------

# discovery §1 #18 (``docs/specs/006-002-delegation-by-layer/discovery.md:47``)
# nombra el ejemplo que PD-11 retira: ``mofgw/qwen3.7-plus`` — familia + versión
# EMBEBIDA + sufijo. El oráculo compartido (``CONCRETE_MODEL_ID_RE``) NO lo
# captura: exige el guion inmediatamente después de la familia y aquí el dígito
# de versión se interpone (``qwen3.7-plus``), y ``\bqwen\b`` tampoco matchea
# (``3`` es carácter de palabra). Se declara el patrón de ESTA unidad, con el
# mismo espíritu (familia concreta, jamás la palabra suelta).
EMBEDDED_VERSION_MODEL_RE = re.compile(
    r"(?i)\b(?:claude|gpt|gemini|deepseek|glm|grok|kimi|qwen|mistral|llama)"
    r"\d[\w.\-]*-[\w.\-]+")


def model_offences_including_embedded_version(text: str) -> list[str]:
    """Oráculo de modelos de PD-11: el compartido (``model_offences``, una sola
    definición en u2) + la forma de versión embebida del ejemplo declarado."""
    found = list(model_offences(text))
    for match in EMBEDDED_VERSION_MODEL_RE.finditer(text):
        found.append(
            "identificador de modelo concreto con versión embebida: "
            f"{match.group(0)!r}"
        )
    return found


# --------------------------------------------------------------------------
# PD-11 — §2 sin modelos: marcadores de las DOS superficies que salen
# --------------------------------------------------------------------------

# "Model family": la cabecera de columna que la spec cita textualmente (§2
# PD-11, `SKILL.md:67-75`). Es la marca de la columna que §2 pierde.
MODEL_FAMILY_COLUMN_RE = re.compile(r"(?i)\bmodel famil")

# Párrafo de perfiles (`SKILL.md:77`): la nota que F001 fijaba por el flag
# `--basic` y el caveat de la invariante (familia no garantizada) bajo el perfil
# que la suspende. PD-11 la retira de §2; F001 (reformulado en este RED) repunta
# ese caveat a los orquestadores generados (PD-4/D-3, U1), donde la familia se
# declara no garantizada.
PROFILES_PARAGRAPH_PATTERNS = (
    (re.compile(r"--basic\b"),
     "flag `--basic` (marcador de la nota de perfiles de §2)"),
    (re.compile(
        r"(?i)\bbasic\b[^\n]{0,80}?"
        r"(?:[Nn][Oo][Tt] guaranteed|suspend|except)"),
     "caveat de la invariante bajo el perfil `basic` (nota de perfiles)"),
)

# La frase nueva (§2 PD-11) — concepto con alternativas de idioma; la redacción
# es libre, el concepto no. Conjunción: si falta UNO, la unidad falla.
PD11_SECTION2_CONCEPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("1. el modelo de cada rol es el configurado en el runtime",
     ("configured in the runtime", "configured in the environment",
      "configured by the runtime", "runtime configuration",
      "configuration of the runtime", "configurado en el runtime",
      "configurado en el entorno", "configuración del runtime")),
    ("2. la skill no nombra modelos",
     ("names no model", "does not name any model", "does not name a model",
      "name no model", "no model is named", "no model names",
      "no nombra", "sin nombrar", "no se nombra")),
    ("3. el rol reviewer",
     ("reviewer", "revisor")),
    ("4. la familia del reviewer difiere de la del implementer",
     ("different family", "different model family", "family differs",
      "distinct family", "not the same family", "differs from",
      "familia distinta", "familia diferente", "distinta de la del")),
    ("5. familia distinta = invariante",
     ("invariant", "invariante")),
    ("6. garantizada por configuración cuando el perfil fija modelos",
     ("guaranteed by configuration", "guaranteed by the configuration",
      "guaranteed by config", "garantizada por configuración",
      "garantizada por la configuración")),
    ("7. declarada cuando el perfil no fija modelos",
     ("declared when", "declared if", "declared as", "declared, not",
      "declarada cuando", "declarada si", "declarada,")),
    ("8. condición sobre el perfil de modelos",
     ("profile", "perfil")),
)


class TestPd11Section2WithoutModels(unittest.TestCase):
    """PD-11: ``SKILL.md`` §2 pierde la columna "Model family" y el párrafo de
    perfiles; ninguna de las dos se reemplaza por otro compromiso de modelos:
    §2 declara que el modelo de cada rol es el configurado en el runtime, que la
    skill no nombra modelos, y que la familia distinta del reviewer es una
    invariante garantizada por configuración o declarada (INV-7)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL_MD)
        region = numbered_section_region(cls.text, 2)
        assert region is not None, (
            "drift del oráculo PD-11: SKILL.md no expone una sección §2 "
            "delimitable por su encabezado numerado"
        )
        cls.section, cls.first_line, cls.last_line = region

    def _offenders(self, patterns: tuple[tuple[re.Pattern[str], str], ...]
                   ) -> list[str]:
        found: list[str] = []
        for pattern, label in patterns:
            for match in pattern.finditer(self.section):
                found.append(
                    f"{relative(SKILL_MD)}:"
                    f"{self.first_line - 1 + line_of(self.section, match.start())}"
                    f" — {label}"
                )
        return found

    def test_pd11_section2_drops_the_model_family_column(self) -> None:
        """PD-11/D-6: la columna "Model family" ya no está en §2 (el modelo de
        cada rol es el configurado en el runtime; la skill no fija familias)."""
        offenders = self._offenders(((MODEL_FAMILY_COLUMN_RE,
                                      "columna «Model family»"),))
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-11/D-6: §2 de SKILL.md conserva la columna «Model family» "
                "(el modelo de cada rol es el configurado en el runtime, la "
                f"skill no fija familias). Líneas §2 {self.first_line}-"
                f"{self.last_line}: {offenders[:20]!r}"
            ),
        )

    def test_pd11_section2_drops_the_profiles_paragraph(self) -> None:
        """PD-11/D-6: el párrafo de perfiles de §2 (la nota que fijaba el flag
        `--basic` y el caveat de la invariante bajo el perfil que la suspende)
        ya no está: ese caveat vive donde la familia se declara no garantizada
        (orquestadores generados — F001 reformulado)."""
        offenders = self._offenders(PROFILES_PARAGRAPH_PATTERNS)
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-11/D-6: §2 de SKILL.md conserva el párrafo de perfiles "
                "(`--basic` + caveat de la invariante): la nota sale de §2 y su "
                "caveat se repunta a los orquestadores (F001 reformulado). "
                f"Líneas §2 {self.first_line}-{self.last_line}: "
                f"{offenders[:20]!r}"
            ),
        )

    def test_pd11_section2_has_no_concrete_model_identifier(self) -> None:
        """PD-11/INV-2: §2 no fija un modelo concreto ni un proveedor concreto
        (la familia de cada rol es la configurada; la skill no nombra ninguna)."""
        offenders = model_offences_including_embedded_version(self.section)
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-11/INV-2: §2 de SKILL.md fija modelos o proveedores "
                "concretos (el modelo de cada rol es el configurado en el "
                f"runtime). Líneas §2 {self.first_line}-{self.last_line}: "
                f"{offenders[:20]!r}"
            ),
        )

    def test_pd11_section2_declares_the_configured_model_sentence(self) -> None:
        """PD-11/INV-7: §2 declara la frase nueva (concepto con alternativas):
        modelo configurado en el runtime; la skill no nombra modelos; la familia
        distinta del reviewer, invariante garantizada por configuración cuando
        el perfil fija modelos y declarada cuando no."""
        missing = [
            detail
            for concept, alternatives in PD11_SECTION2_CONCEPTS
            if (detail := require_any(self.section, alternatives, concept))
        ]
        self.assertEqual(
            missing, [],
            msg=(
                "PD-11/INV-7: §2 de SKILL.md no declara la frase nueva completa "
                f"(líneas {self.first_line}-{self.last_line}). Ausentes: {missing}"
            ),
        )


class TestPd11HandoffPromptsWithoutModelExamples(unittest.TestCase):
    """PD-11/INV-2: ``references/handoff-prompts.md`` pierde su ejemplo de
    modelo concreto (``:515``, discovery §1 #18: ``mofgw/qwen3.7-plus``): es
    plantilla de metodología, no fija modelos."""

    def test_pd11_handoff_prompts_has_no_concrete_model_example(self) -> None:
        """PD-11/INV-2: ausencia del ejemplo de modelo concreto (identificadores
        de modelo, variantes espaciadas, proveedores y la forma con versión
        embebida) en la plantilla."""
        text = read(HANDOFF_PROMPTS)
        offenders = model_offences_including_embedded_version(text)
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-11/INV-2: handoff-prompts.md fija modelos o proveedores "
                "concretos en su(s) ejemplo(s) (es plantilla de metodología: el "
                f"modelo de cada rol es el configurado en el runtime): "
                f"{offenders[:20]!r}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
