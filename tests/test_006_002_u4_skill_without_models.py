#!/usr/bin/env python3
"""006-002 U4 RED — `SKILL.md` §2 sin modelos (PD-11; INV-2/INV-7).

Contract:
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 **PD-11**, §3
  **INV-2**/INV-7, §4 **D-6**;
- ``docs/specs/006-003-installer-single-profile-delegation-config/spec.md`` §9
  (enmienda A-5 del dueño, 2026-10-18) — **INV-5 reformulada**: §2 no exige ni
  declara la familia o el modelo del reviewer respecto del implementer;
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha **U4** (archivos:
  ``SKILL.md``, ``handoff-prompts.md``, F001 de
  ``tests/validate-consistency.sh``) + **enmienda A-1** (los asserts acoplados
  de esta superficie se reformulan en ESTE RED, nunca en el GREEN).

PD-11 — §2 pierde la columna "Model family" y el párrafo de perfiles; en su
lugar queda: el modelo de cada rol es **el configurado en el runtime** y la
skill **no nombra modelos**. ``references/handoff-prompts.md`` pierde su ejemplo
de modelo concreto. F001 de ``tests/validate-consistency.sh`` se **reformula, no
se borra** (esa reformulación es parte de este mismo RED — enmienda A-1).
(Las dos mitades «cuando el perfil fija modelos / cuando no» quedaron
supersedidas por PD-7b de 006-003 y, luego, por **A-5**: ver *REFORMULADO por
006-003 U3 y por A-5* al final de esta cabecera. Los párrafos se conservan como
registro del contrato de 006-002.)

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
  5 ``TestPd11Section2WithoutModels::test_pd11_section2_has_no_family_requirement``          PD-7b / INV-5 (A-5)
  6 ``TestPd11HandoffPromptsWithoutModelExamples::test_pd11_handoff_prompts_has_no_concrete_model_example`` PD-11 / INV-2

RED esperado contra el árbol vigente (OBSERVADO; los guards ya están en verde):
- (1)/(3): PASAN (la columna y los modelos concretos ya salieron de §2 con el
  GREEN de U4) — GUARDs de PD-11/D-6 e INV-2.
- (2): PASA (el párrafo de perfiles salió con el GREEN de U3) — GUARD de
  PD-11/D-6.
- (4): PASA (la frase nueva de §2 —modelo configurado en el runtime + la skill
  no nombra modelos— está desde el GREEN de U4) — GUARD de INV-7 con los
  conceptos 1 y 2 (los conceptos de la rama de familia se retiraron).
- (5): FALLA por AssertionError de CONTENIDO: §2 todavía declara el requisito de
  familia del reviewer (A-5 lo retira). Es el RED de U5' en esta superficie.
- (6): PASA (el ejemplo con modelo concreto ya salió de ``handoff-prompts.md``).
Ningún fallo es ImportError/SyntaxError.

Acoplados reformulados (enmienda A-1 y A-5, cada RED cubre su superficie):
- ``tests/test_006_002_u2_neutral_skill.py``: se retiró la neutralización
  TEMPORAL de §2 del oráculo de modelos (PD-1/INV-2).
- ``tests/validate-consistency.sh`` F001: la nota de perfiles dejó de exigirse y
  pasó a exigir la frase nueva de §2; con A-5, la mitad de FAMILIA de F001 se
  invierte a ausencia (el requisito se retira, la declaración «invariant not
  guaranteed» ligada a familia con él).
- ``tests/test_006_003_u5p_no_family_requirement.py`` es el focal del retiro
  (A-5); aquí se conserva la mitad de esta unidad —§2 sin modelos, sin perfiles
  y sin el requisito de familia— para que ningún assert quede borrado sin
  declarar su reemplazo.

REFORMULADO por A-5 (006-003 §9; sobre la regla A-1): los conceptos 4, 5, 6',
7' y 8' de la versión anterior de esta unidad («la familia del reviewer difiere
del implementer», «familia distinta = invariante», «verificación de
configuración», «no verificable» y «se declara») EXIGÍAN el requisito que A-5
retira: se reemplazan —nunca se borran— por la AUSENCIA de ese requisito
(``test_pd11_section2_has_no_family_requirement``, oráculo único de u3:
``all_offenders``) y el concepto 3 («el rol reviewer») deja de exigirse porque
sólo existía para sostener esa declaración.
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

# Oráculo de ausencia del requisito de familia (A-5), definición única en u2
# (junto al resto de los oráculos de ausencia compartidos).
from tests.test_006_002_u2_neutral_skill import all_offenders

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
#
# REFORMULADO por 006-003 U3 (PD-7b/D7): el segundo patrón (el caveat «basic …
# NOT guaranteed/suspend») describía la rama por PERFIL que PD-7 retira
# completa; ya no puede describir nada porque `--basic` deja de existir en el
# texto instalable. Su reemplazo es la PROHIBICIÓN del vocabulario de perfiles
# en §2 (concepto 8 de esta unidad convertido en ausencia, declarado en la
# cabecera). El primer patrón (`--basic`) se conserva: sigue siendo el marcador
# mínimo de la nota de perfiles.
PROFILES_PARAGRAPH_PATTERNS = (
    (re.compile(r"--basic\b"),
     "flag `--basic` (marcador de la nota de perfiles de §2)"),
    (re.compile(r"(?i)\bperfil(?:es)?\b"),
     "vocabulario de perfiles en §2 (PD-7b: el perfil no es el lugar del modelo)"),
    (re.compile(r"(?i)\bprofile(?:s)?\b"),
     "vocabulario de perfiles en §2 (PD-7b: el perfil no es el lugar del modelo)"),
)

# La frase nueva (§2 PD-11) — concepto con alternativas de idioma; la redacción
# es libre, el concepto no. Conjunción: si falta UNO, la unidad falla.
# REFORMULADO por A-5 (006-003 §9): los conceptos 4, 5, 6', 7' y 8' anteriores
# exigían el requisito de familia/modelo del reviewer (diferencia de familia,
# «familia distinta = invariante», «verificación de configuración», «no
# verificable» y «se declara»), que A-5 RETIRA: se reemplazan por su AUSENCIA
# (test_pd11_section2_has_no_family_requirement, oráculo único de u3:
# ``all_offenders``). El concepto 3 («el rol reviewer») deja de exigirse porque
# sólo existía para sostener esa declaración. Se conservan los conceptos del
# contrato vigente: el modelo configurado en el runtime y la skill que no nombra
# modelos.
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
)


class TestPd11Section2WithoutModels(unittest.TestCase):
    """PD-11 + A-5: ``SKILL.md`` §2 pierde la columna "Model family" y el
    párrafo de perfiles; ninguna de las dos se reemplaza por otro compromiso de
    modelos: §2 declara que el modelo de cada rol es el configurado en el
    runtime y que la skill no nombra modelos, y **no** exige ni declara la
    familia o el modelo del reviewer respecto del implementer (INV-5
    reformulada por A-5)."""

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
        """PD-11/D-6 + PD-7b (006-003 U3): §2 no conserva la nota de perfiles.
        Reformulado: el patrón del caveat «basic … NOT guaranteed/suspend» se
        retira con la rama por perfil (PD-7) y su reemplazo es la prohibición del
        vocabulario de perfiles en §2 (concepto 8 convertido en ausencia)."""
        offenders = self._offenders(PROFILES_PARAGRAPH_PATTERNS)
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-11/D-6 + PD-7b: §2 de SKILL.md conserva el párrafo de "
                "perfiles (`--basic` / vocabulario de perfiles): la elección de "
                "modelo vive en la configuración de delegación, no en §2. "
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
        """PD-11/INV-7: §2 declara la frase vigente (concepto con alternativas):
        el modelo de cada rol es el configurado en el runtime y la skill no
        nombra modelos. Los conceptos de la familia del reviewer se retiraron
        con A-5 (su ausencia la fija el test siguiente).
        """
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

    def test_pd11_section2_has_no_family_requirement(self) -> None:
        """PD-7b/INV-5 REFORMULADA por A-5: §2 no exige, verifica ni declara la
        familia o el modelo del reviewer respecto del implementer (el modelo de
        cada rol es el que configura el runtime). Oráculo único: ``all_offenders``
        de ``tests/test_006_003_u3_texts_without_profiles.py``."""
        offenders = all_offenders(self.section, SKILL_MD, self.first_line)
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-7b/INV-5 (A-5): §2 de SKILL.md todavía exige o declara la "
                "familia/modelo del reviewer respecto del implementer "
                f"(líneas {self.first_line}-{self.last_line}): "
                f"{offenders[:20]!r}"
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
