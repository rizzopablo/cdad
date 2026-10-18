#!/usr/bin/env python3
"""006-003 U5' RED — retiro del requisito de familia/modelo del reviewer (A-5).

Contrato:
- ``docs/specs/006-003-installer-single-profile-delegation-config/spec.md``
  **§9 — Enmienda A-5 del dueño (2026-10-18)**: se retiran PD-4a..e, D4, §2.4 y
  el script ``cdad_model_family.py`` (no se construye); **INV-5 se reemplaza**
  por «ningún texto instalable exige al orquestador ni a ningún rol elegir,
  controlar, verificar ni declarar la familia o el modelo del reviewer respecto
  del implementer»; **PD-7b se reformula** en ese sentido: §2 de ``SKILL.md``,
  los invariantes de rol, las fuentes de rol (``sources/roles/*.md``) y la
  sección ``delegation`` de los adaptadores no contienen ese requisito, y los
  restos de la redacción por perfiles (``basic``, «profile») en los adaptadores
  también se retiran. Se CONSERVAN la observación I8 (``model_configured``/
  ``model_reported``) y los demás invariantes anti-sesgo (el test-writer no ve
  implementación, el implementer no edita tests, el reviewer es read-only y de
  sesión separada).

Este módulo es el oráculo FOCAL de U5'. RETIRA (declarado en el commit de este
RED) ``tests/test_006_003_u5_model_family.py``: PD-4a..e no rigen más, así que
el oráculo del script de familia se reemplaza por su inverso declarado, no se
borra en silencio (regla A-1).

Superficies de A-5 (oráculo de AUSENCIA por CONCEPTOS, nunca frases exactas):

  - ``skills/**`` — todo archivo regular (el ``grep -rE`` del contrato no
    distingue extensiones), decodificado con reemplazo;
  - ``sources/roles/*.md``;
  - ``sources/agents/adapters/*.md``;
  - ``agents/**`` — orquestadores y agentes generados (``.md``).

Exclusiones DECLARADAS (cada una con su dueño, ninguna silenciosa):

  - ``skills/cdad-cycle/references/context-meter.md`` — contrato de LECTOR/
    MEDICIÓN (INV-8): mide herramientas y modelos observados, no instruye
    delegación ni despacho (misma exclusión que ``test_006_002_u2_neutral_skill``
    y ``test_006_003_u3_texts_without_profiles``);
  - ``skills/cdad-cycle/references/verdict-tuple.md`` — criterio de CONFIANZA
    del veredicto, no requisito de despacho (A-5 §9): su puntaje «+1 por familia
    distinta» NO se fija en ningún sentido; este oráculo no lo mira.

Usos NO relacionados de la palabra «familia» excluidos por COLOCACIÓN (A-5 §9 /
encargo del packet), declarados uno por uno: ``failure family`` /
``failure-family`` (``stage-4-review.md``, ``anti-patterns.md``), ``family of
failures`` / ``familia de fallos`` y ``split-brain family`` (``continuity.md``).
El clasificador ``has_related_family`` de u3 es la definición única y su
auto-test (``TestU5pOracleDeclaredExclusions``) fija ambos lados: lo declarado
como ajeno NO cuenta y lo relacionado SÍ.

Mapa test → postcondición (un test por afirmación observable):

  1 ``TestU5pNoReviewerFamilyRequirement::test_u5p_skill_tree_has_no_reviewer_family_requirement``                      INV-5 (A-5) / PD-7b
  2 ``TestU5pNoReviewerFamilyRequirement::test_u5p_role_sources_have_no_reviewer_family_requirement``                   INV-5 (A-5) / PD-7b
  3 ``TestU5pNoReviewerFamilyRequirement::test_u5p_adapters_have_no_reviewer_family_requirement``                       INV-5 (A-5) / PD-7b
  4 ``TestU5pNoReviewerFamilyRequirement::test_u5p_generated_agents_have_no_reviewer_family_requirement``               INV-5 (A-5) / PD-7b
  5 ``TestU5pNoProfileWordingInAdapters::test_u5p_adapters_have_no_profile_wording``                                    PD-7b (A-5) / D7
  6 ``TestU5pConservedAntiBiasInvariants::test_u5p_section2_keeps_the_other_anti_bias_invariants``                       A-5 «se conservan»
  7 ``TestU5pOracleDeclaredExclusions::test_u5p_family_classifier_separates_declared_unrelated_uses``                     oráculo del oráculo (A-5 §9)

RED esperado contra el árbol actual (OBSERVADO y declarado, no accidental):

  - (1)…(4) FALLAN por AssertionError de CONTENIDO: el árbol vigente todavía
    declara el requisito (la familia del reviewer como verificación de
    configuración / «invariant not guaranteed»), que U5' GREEN retira;
  - (5) FALLA por AssertionError de CONTENIDO: los adaptadores conservan
    vocabulario de perfiles fuera de su bloque ``delegation`` (el bloque ya está
    limpio desde el GREEN de U3; A-5 retira también el resto);
  - (6) es el POSITIVO conservado por A-5: pasa hoy y debe seguir pasando
    después del GREEN (si el retiro de los textos de familia se llevara por
    delante un invariante anti-sesgo, este test lo detecta);
  - (7) pasa siempre: no lee producto, fija la precisión del oráculo.

Ningún fallo es ImportError/SyntaxError: todos son aserciones sobre el contenido
publicado. Sólo se LEE el artefacto publicado al ejecutarse; el test-writer no
leyó implementación (``skills/``, ``sources/``, ``agents/``, ``scripts/``).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Helper único (una sola definición): delimitación de la sección numerada §2 y el
# oráculo de AUSENCIA del requisito de familia (A-5), que vive en u2 junto al
# resto de los oráculos de ausencia compartidos.
from tests.test_006_002_u2_neutral_skill import (
    all_offenders,
    has_related_family,
    numbered_section_region,
    relative,
)

# Vocabulario de perfiles: una sola definición (la del oráculo de perfiles de
# U3, PD-7b).
from tests.test_006_003_u3_texts_without_profiles import (
    PROFILES_VOCABULARY_PATTERNS,
    offenders_in,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILLS_ROOT = REPO_ROOT / "skills"
ROLE_SOURCES_ROOT = REPO_ROOT / "sources" / "roles"
ADAPTERS_ROOT = REPO_ROOT / "sources" / "agents" / "adapters"
AGENTS_ROOT = REPO_ROOT / "agents"
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# --------------------------------------------------------------------------
# Exclusiones declaradas (dueño explícito; ninguna silenciosa)
# --------------------------------------------------------------------------

DECLARED_EXCLUSIONS: dict[str, str] = {
    "skills/cdad-cycle/references/context-meter.md":
        "contrato de LECTOR/MEDICIÓN (INV-8): mide, no delega",
    "skills/cdad-cycle/references/verdict-tuple.md":
        "criterio de CONFIANZA del veredicto (A-5 §9): +1 por familia distinta es "
        "puntaje, no requisito de despacho — no se fija en ningún sentido",
}

# --------------------------------------------------------------------------
# Recolección de superficies
# --------------------------------------------------------------------------


def _is_scannable(path: Path) -> bool:
    return (
        path.is_file()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and relative(path) not in DECLARED_EXCLUSIONS
    )


def skill_tree_documents() -> list[Path]:
    """``skills/**``: todos los archivos regulares (el ``grep -rE`` del contrato)."""
    return sorted(path for path in SKILLS_ROOT.rglob("*") if _is_scannable(path))


def role_source_documents() -> list[Path]:
    return sorted(
        path for path in ROLE_SOURCES_ROOT.glob("*.md") if _is_scannable(path)
    )


def adapter_documents() -> list[Path]:
    return sorted(
        path for path in ADAPTERS_ROOT.glob("*.md") if _is_scannable(path)
    )


def generated_agent_documents() -> list[Path]:
    return sorted(path for path in AGENTS_ROOT.rglob("*.md") if _is_scannable(path))


def read_artifact(path: Path, why: str) -> str:
    """Puerta del oráculo: el artefacto publicado existe y no está vacío."""
    assert path.is_file(), (
        f"{why}: el artefacto declarado por el contrato no existe "
        f"(drift de la superficie): {relative(path)}"
    )
    text = path.read_text(encoding="utf-8", errors="replace")
    assert text.strip(), (
        f"{why}: el artefacto declarado está vacío: {relative(path)}"
    )
    return text


def scan(documents: list[Path], why: str) -> list[str]:
    offenders: list[str] = []
    for path in documents:
        offenders.extend(all_offenders(read_artifact(path, why), path))
    return offenders


# ------------------------------------------- INV-5 (A-5) — ausencia por surface


class TestU5pNoReviewerFamilyRequirement(unittest.TestCase):
    """INV-5 reformulada por A-5 / PD-7b: ningún texto instalable exige elegir,
    controlar, verificar ni declarar la familia o el modelo del reviewer
    respecto del implementer."""

    maxDiff = None

    def test_u5p_skill_tree_has_no_reviewer_family_requirement(self) -> None:
        """A-5/PD-7b: el árbol ``skills/**`` (salvo las dos exclusiones
        declaradas) no contiene el requisito de familia del reviewer."""
        documents = skill_tree_documents()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo A-5: no se recolectó ningún archivo bajo "
            f"{relative(SKILLS_ROOT)}"
        )
        self.assertIn(
            SKILL_MD, documents,
            "drift del oráculo A-5: skills/cdad-cycle/SKILL.md no está en la "
            "superficie escaneada"
        )
        offenders = scan(documents, "A-5 (skills/**)")
        self.assertEqual(
            offenders, [],
            msg=(
                "A-5/PD-7b: el texto instalable de la skill todavía exige (o "
                "declara) la familia/modelo del reviewer respecto del "
                f"implementer: {offenders[:20]!r}"
            ),
        )

    def test_u5p_role_sources_have_no_reviewer_family_requirement(self) -> None:
        """A-5/PD-7b: las fuentes de rol ``sources/roles/*.md`` no contienen el
        requisito de familia del reviewer."""
        documents = role_source_documents()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo A-5: no se recolectó ninguna fuente de rol bajo "
            f"{relative(ROLE_SOURCES_ROOT)}"
        )
        offenders = scan(documents, "A-5 (sources/roles)")
        self.assertEqual(
            offenders, [],
            msg=(
                "A-5/PD-7b: una fuente de rol todavía exige (o declara) la "
                "familia/modelo del reviewer respecto del implementer: "
                f"{offenders[:20]!r}"
            ),
        )

    def test_u5p_adapters_have_no_reviewer_family_requirement(self) -> None:
        """A-5/PD-7b: los adaptadores fuente (``sources/agents/adapters/*.md``,
        dueños de la sección ``delegation``) no contienen el requisito."""
        documents = adapter_documents()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo A-5: no se recolectó ningún adaptador bajo "
            f"{relative(ADAPTERS_ROOT)}"
        )
        offenders = scan(documents, "A-5 (adapters)")
        self.assertEqual(
            offenders, [],
            msg=(
                "A-5/PD-7b: un adaptador fuente todavía exige (o declara) la "
                "familia/modelo del reviewer respecto del implementer: "
                f"{offenders[:20]!r}"
            ),
        )

    def test_u5p_generated_agents_have_no_reviewer_family_requirement(self) -> None:
        """A-5/PD-7b (por composición): los agentes y orquestadores generados
        (``agents/**``) no heredan el requisito de familia del reviewer."""
        documents = generated_agent_documents()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo A-5: no se recolectó ningún agente generado bajo "
            f"{relative(AGENTS_ROOT)}"
        )
        offenders = scan(documents, "A-5 (agents/**)")
        self.assertEqual(
            offenders, [],
            msg=(
                "A-5/PD-7b: un artefacto generado todavía exige (o declara) la "
                "familia/modelo del reviewer respecto del implementer: "
                f"{offenders[:20]!r}"
            ),
        )


# --------------------------------------------- PD-7b (A-5) — sin perfiles


class TestU5pNoProfileWordingInAdapters(unittest.TestCase):
    """PD-7b (A-5): los restos de la redacción por perfiles (``basic``,
    «profile») también se retiran de los adaptadores fuente."""

    maxDiff = None

    def test_u5p_adapters_have_no_profile_wording(self) -> None:
        """A-5/PD-7b: ningún adaptador fuente conserva vocabulario de perfiles
        ni el flag retirado ``--basic`` (el modelo vive en la configuración de
        delegación, PD-3; el perfil no existe, PD-1)."""
        documents = adapter_documents()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo PD-7b: no se recolectó ningún adaptador bajo "
            f"{relative(ADAPTERS_ROOT)}"
        )
        offenders: list[str] = []
        for path in documents:
            text = read_artifact(path, "PD-7b (adapters)")
            offenders.extend(
                offenders_in(text, path, PROFILES_VOCABULARY_PATTERNS)
            )
        self.assertEqual(
            offenders, [],
            msg=(
                "A-5/PD-7b: un adaptador fuente conserva vocabulario de "
                "perfiles o el flag retirado `--basic`: "
                f"{offenders[:20]!r}"
            ),
        )


# --------------------------------- A-5 «se conservan» — invariantes anti-sesgo


# Cada grupo conservado por A-5: las etiquetas del rol y el SUJETO/PREDICADO del
# invariante que debe seguir declarado en su vecindad (conceptos, no frases: el
# sujeto y el marcador de separación admiten alternativas de idioma y de orden).
CONSERVED_ANTI_BIAS_GROUPS: tuple[
    tuple[str, tuple[str, ...], re.Pattern[str]], ...
] = (
    (
        "el test-writer no ve implementación",
        ("test-writer", "test writer", "test_writer"),
        re.compile(r"(?i)(implementation|implementaci[oó]n|\bsrc/|\blib/|sources/)"),
    ),
    (
        "el implementer no edita tests",
        ("implementer", "implementador"),
        re.compile(r"(?i)\b(test|tests|prueba|pruebas)\b"),
    ),
    (
        "el reviewer es read-only",
        ("reviewer", "revisor"),
        re.compile(r"(?i)(read[- ]?only|readonly|solo\s+lectura|sólo\s+lectura)"),
    ),
    (
        "el reviewer corre en sesión separada",
        ("reviewer", "revisor"),
        re.compile(
            r"(?i)(session|sesi[oó]n)[^\n]{0,70}"
            r"(separat|different|another|other|new|own|isolat|independent|"
            r"distint|propi|aislad|independient)"
            r"|"
            r"(separat|different|another|other|new|own|isolat|independent|"
            r"distint|propi|aislad|independient)[^\n]{0,70}(session|sesi[oó]n)"
        ),
    ),
)

# La negación que hace que el concepto sea una FRONTERA (sin ella, «lee la
# implementación» satisfaría el grupo por la sola presencia del sustantivo).
NEGATION_RE = re.compile(
    r"(?i)\b(not|never|no|without|sin|cannot|can't|doesn't|don't|neither|"
    r"nunca|jamás|fuera de)\b"
)

# Ventana alrededor de cada aparición del rol dentro de §2.
SECTION2_ROLE_WINDOW = 6


class TestU5pConservedAntiBiasInvariants(unittest.TestCase):
    """A-5 «se conservan»: §2 de ``SKILL.md`` mantiene los demás invariantes
    anti-sesgo (el test-writer no ve implementación, el implementer no edita
    tests, el reviewer es read-only y de sesión separada)."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_artifact(SKILL_MD, "A-5 (conservación)")
        region = numbered_section_region(cls.text, 2)
        assert region is not None, (
            "drift del oráculo A-5: SKILL.md no expone una sección §2 "
            "delimitable por su encabezado numerado"
        )
        cls.section, cls.first_line, cls.last_line = region
        cls.section_lines = cls.section.splitlines()

    def _role_windows(self, aliases: tuple[str, ...]) -> str:
        """El texto de las ventanas (±``SECTION2_ROLE_WINDOW``) de cada línea
        que nombra el rol (un invariante debe vivir junto a su rol)."""
        chunks: list[str] = []
        for index, line in enumerate(self.section_lines):
            lowered = line.lower()
            if not any(alias in lowered for alias in aliases):
                continue
            lo = max(0, index - SECTION2_ROLE_WINDOW)
            hi = min(len(self.section_lines), index + SECTION2_ROLE_WINDOW + 1)
            chunks.append("\n".join(self.section_lines[lo:hi]))
        return "\n".join(chunks)

    def test_u5p_section2_keeps_the_other_anti_bias_invariants(self) -> None:
        """A-5: cada invariante conservado sigue declarado en §2, junto a su rol,
        con la negación que lo hace frontera (concepto con alternativas de
        idioma; la forma de la prosa la verifica el review de stage 4)."""
        problems: list[str] = []
        for concept, aliases, subject_re in CONSERVED_ANTI_BIAS_GROUPS:
            window = self._role_windows(aliases)
            if not window.strip():
                problems.append(
                    f"{concept}: drift del oráculo — §2 no nombra el rol "
                    f"{aliases!r} (líneas {self.first_line}-{self.last_line})"
                )
                continue
            if not subject_re.search(window):
                problems.append(
                    f"{concept}: sujeto ausente (alternativas buscadas "
                    f"{subject_re.pattern!r})"
                )
                continue
            if not NEGATION_RE.search(window):
                problems.append(
                    f"{concept}: falta la negación que lo hace frontera "
                    f"(alternativas buscadas {NEGATION_RE.pattern!r})"
                )
        self.assertEqual(
            problems, [],
            msg=(
                "A-5 («se conservan»): §2 de SKILL.md ya no declara los "
                "invariantes anti-sesgo conservados (líneas "
                f"{self.first_line}-{self.last_line}): {problems}"
            ),
        )


# ------------------------------------ precisión del oráculo (± usos ajenos)


class TestU5pOracleDeclaredExclusions(unittest.TestCase):
    """A-5 §9 / encargo del packet: los usos NO relacionados de la palabra
    «family» están excluidos por colocación (``failure family``,
    ``failure-family``, ``family of failures``, ``split-brain family``) y los
    usos relacionados se siguen detectando. Auto-test del oráculo sobre cadenas
    sintéticas: no lee producto."""

    UNRELATED_USES = (
        "el reviewer agrupa los hallazgos por failure family",
        "the reviewer must not merge findings into a different failure family",
        "the reviewer classifies a failure-family of the run",
        "the reviewer subdivides the failure families of the report",
        "continuity declares the split-brain family explicitly",
        "the reviewer detects a family of failures in the log",
        "el reviewer agrupa los hallazgos por familia de fallos",
    )

    RELATED_USES = (
        "the reviewer must be from a different model family than the implementer",
        "the reviewer's model family is a configuration verification",
        "invariant not guaranteed for the reviewer's model family",
        "la familia del reviewer debe diferir de la del implementer",
    )

    def test_u5p_family_classifier_separates_declared_unrelated_uses(self) -> None:
        """A-5 §9: lo declarado como ajeno no cuenta; lo relacionado sí."""
        wrongly_related = [
            line for line in self.UNRELATED_USES
            if has_related_family(line)
        ]
        self.assertEqual(
            wrongly_related, [],
            msg=(
                "oráculo A-5: un uso NO relacionado de «family» (declarado en "
                f"la cabecera) se clasificó como relacionado: {wrongly_related!r}"
            ),
        )
        wrongly_unrelated = [
            line for line in self.RELATED_USES
            if not has_related_family(line)
        ]
        self.assertEqual(
            wrongly_unrelated, [],
            msg=(
                "oráculo A-5: un uso RELACIONADO de «family» (familia de un "
                "modelo) se clasificó como ajeno: {wrongly_unrelated!r}"
            ),
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
