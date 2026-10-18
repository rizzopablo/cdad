#!/usr/bin/env python3
"""006-003 U3 RED — textos instalables sin perfiles, sin modelos y sin el
requisito de familia del reviewer.

Contract:
- ``docs/specs/006-003-installer-single-profile-delegation-config/spec.md``
  (approved 2026-10-18; **§9 — enmienda A-5 del dueño, 2026-10-18**) — §3
  **PD-7a** (``grep -rE 'deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/'
  skills/ agents/...`` sin salida), §3 **PD-7b REFORMULADA por A-5**: §2 de
  ``SKILL.md``, los invariantes de rol, las fuentes de rol y la sección
  ``delegation`` de los adaptadores **no contienen** el requisito de familia ni
  de modelo del reviewer respecto del implementer, y los restos de la redacción
  por perfiles (``basic``, «profile») se retiran; §4 **INV-3** (ningún texto
  instalable fija modelos), **INV-4** (ningún texto instalable nombra ``/tmp`` —
  no-regresión) e **INV-5 REFORMULADA por A-5** («ningún texto instalable exige
  al orquestador ni a ningún rol elegir, controlar, verificar ni declarar la
  familia o el modelo del reviewer respecto del implementer»).
- ``docs/specs/006-003-installer-single-profile-delegation-config/plan.md``
  ficha **U3** (archivos: ``skills/cdad-cycle/SKILL.md``,
  ``sources/agents/adapters/opencode.md``, ``claude-code.md`` y los
  orquestadores regenerados) + **regla A-1**.

Reformulación declarada por A-5 (regla A-1) — los conceptos que esta unidad
exigía como PRESENCIA («la familia del reviewer es una verificación de
configuración», «not verifiable», «declared») se INVIERTEN: pasan a ser un
oráculo de AUSENCIA. La definición única del oráculo de ausencia vive en ESTE
módulo (patrones + ``all_offenders``) y la consume el focal de U5'
(``tests/test_006_003_u5p_no_family_requirement.py``) sobre las superficies
amplias que A-5 nombra; aquí quedan las superficies acotadas de esta unidad (§2
de ``SKILL.md``, los bloques ``delegation`` de los adaptadores y los dos
orquestadores generados). Ninguna aserción se borra sin declarar su reemplazo.

Alcance declarado de esta unidad: el texto INSTALABLE (``skills/**`` y los dos
orquestadores generados) y la sección ``delegation`` de los adaptadores (dueña
del contenido por D-1). El ejecutable del instalador/generador (PD-1) y la
configuración de delegación (PD-2/PD-3) pertenecen a U1/U2/U4 y NO se asertan
aquí.

Oráculo (caja negra, artefacto publicado):
- PD-7a usa el conjunto de tokens EXACTO de la spec, con una sola definición
  (``MODEL_NAME_RE`` de ``tests/test_006_003_u1_generator_without_profiles.py``
  — U1 lo fijó para la mitad «agentes generados» del mismo postcondición). La
  superficie es ``grep -rE ... skills/``: TODOS los archivos regulares del árbol
  de skills (no sólo ``.md``), decodificados con reemplazo para que el barrido
  sea total como el ``grep`` del contrato, más los dos orquestadores generados
  que PD-7a nombra.
- Sin exclusión de ``references/context-meter.md`` para PD-7a: PD-7a no la
  declara y el contrato de lector (INV-8) no nombra ningún modelo en el árbol
  vigente, así que excluirlo debilitaría el oráculo sin necesidad. Si el
  contrato de lector llegara a nombrar uno, el fallo debe discutirse en la spec
  (no silenciarse aquí). El oráculo de AUSENCIA de familia (A-5) sí excluye
  ``context-meter.md`` (contrato de lector, INV-8) y ``references/verdict-tuple.md``
  (criterio de CONFIANZA del veredicto: el puntaje «+1 por familia distinta» no
  se fija en ningún sentido), ambas con su dueño declarado.
- PD-7b delimita §2 con el helper único ``numbered_section_region`` (misma
  delimitación que el oráculo focal de ``test_006_002_u4_skill_without_models``)
  y la sección ``delegation`` de cada adaptador con la gramática de secciones
  del generador (``<!-- cdad-section:delegation -->`` ... ``<!-- /cdad-section
  -->``, helpers de ``test_006_002_u1_delegation_section``). Los conceptos se
  exigen con alternativas de idioma (``require_any``, patrón 005-010 T3): la
  redacción es libre, el concepto no.
- «Por composición» (PD-7b): los dos orquestadores generados son artefactos
  compuestos, sin marcadores de sección; por eso el oráculo de ausencia los
  escanea como documento completo (no hay ancla de sección que delimite la
  declaración retirada).

Mapa test → postcondición (un test por afirmación observable; filas 4/6/8
reformuladas por A-5, de presencia a ausencia):

  1 ``TestPd7aInstallableTextWithoutModels::test_pd7a_installable_skill_tree_names_no_model``                    PD-7a / INV-3
  2 ``TestPd7aInstallableTextWithoutModels::test_pd7a_generated_orchestrators_name_no_model``                    PD-7a / INV-3
  3 ``TestPd7bSkillSection2WithoutProfiles::test_pd7b_skill_section2_has_no_profile_vocabulary``                 PD-7b / D7
  4 ``TestPd7bSkillSection2WithoutProfiles::test_pd7b_skill_section2_has_no_family_requirement``                 PD-7b / INV-5 (A-5)
  5 ``TestPd7bAdapterDelegationSections::test_pd7b_adapter_delegation_blocks_have_no_profile_vocabulary``         PD-7b / D7
  6 ``TestPd7bAdapterDelegationSections::test_pd7b_adapter_delegation_blocks_have_no_family_requirement``         PD-7b / INV-5 (A-5)
  7 ``TestPd7bGeneratedOrchestratorComposition::test_pd7b_generated_orchestrators_carry_no_profile_vocabulary``   PD-7b / D7 (composición)
  8 ``TestPd7bGeneratedOrchestratorComposition::test_pd7b_generated_orchestrators_carry_no_family_requirement``   PD-7b / INV-5 (A-5) (composición)
  9 ``TestRetiredModelMapNotReferenced::test_retired_model_map_is_unreferenced_by_role_sources_and_generated_agents`` PD-1c / PD-7 / INV-3
 10 ``TestInv4InstallableTextWithoutTmp::test_inv4_installable_skill_text_names_no_tmp``                          INV-4

RED esperado contra el árbol vigente (OBSERVADO; declarado, no accidental):

- (1) PASA hoy: U1 ya retiró los nombres de modelo de los agentes generados y
  ``skills/**`` no nombra ninguno (``grep -rE`` sin salida sobre el árbol). Es un
  GUARD de no-regresión de INV-3, no evidencia de que U3 esté hecha.
- (2) PASA hoy por la misma razón (los dos orquestadores comprometidos ya salen
  sin modelos de U1): GUARD declarado de PD-7a.
- (3) PASA hoy: §2 de ``SKILL.md`` ya no habla de perfiles (GREEN de U3). GUARD
  de PD-7b/D7: el retiro de U5' no debe reintroducirlos.
- (4) FALLA por AssertionError de CONTENIDO: §2 todavía declara el requisito de
  familia del reviewer (verificación de configuración / «no verificable» /
  declaración), que A-5 retira. Es el RED de U5'.
- (5) PASA hoy: los bloques ``delegation`` de los adaptadores ya perdieron el
  vocabulario de perfiles (GREEN de U3). GUARD de PD-7b/D7.
- (6) FALLA por AssertionError de CONTENIDO: los bloques ``delegation``
  conservan la declaración de familia del reviewer, que A-5 retira.
- (7) PASA hoy: cada orquestador generado ya salió sin ``--basic`` ni
  vocabulario de perfiles (GREEN de U3). GUARD de PD-7b/D7 (composición).
- (8) FALLA por AssertionError de CONTENIDO: los orquestadores generados
  conservan el requisito de familia heredado de la fuente, que A-5 retira.
- (9) PASA hoy: ni las fuentes de rol ni los agentes generados nombran
  ``cdad-models.sh`` (retirado en U1). GUARD declarado.
- (10) PASA hoy (INV-4 se cumple en ``skills/``): GUARD de no-regresión.

Ningún fallo es ImportError/SyntaxError: todos son aserciones sobre el contenido
publicado. Los reformulados acoplados del retiro de A-5
(``test_006_002_u4_…``, ``test_006_002_u1_…``, ``test_005_004_t2_…``,
``validate-consistency.sh`` F001 y ``validate-odoo-specialization.sh``) se
cambian en ESTE RED declarando su reemplazo (A-5, sobre la regla A-1); el focal
del retiro es ``tests/test_006_003_u5p_no_family_requirement.py``.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Helpers únicos (una sola definición): delimitación de secciones numeradas,
# líneas/etiquetas y conceptos con alternativas de idioma (006-002 U2, el mismo
# oráculo que usa el focal de §2 de 006-002 U4).
from tests.test_006_002_u2_neutral_skill import (
    all_offenders,
    line_of,
    numbered_section_region,
    relative,
)

# Gramática de secciones del generador (006-002 U1: dueña del bloque
# `delegation` de cada adaptador).
from tests.test_006_002_u1_delegation_section import (
    SECTION_CLOSE_RE,
    SECTION_OPEN_RE,
)

# PD-7a: una sola definición del conjunto de tokens de modelo de la spec — la
# que U1 fijó para la mitad «agentes generados» de la misma postcondición.
from tests.test_006_003_u1_generator_without_profiles import MODEL_NAME_RE

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILLS_ROOT = REPO_ROOT / "skills"
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# PD-7a nombra estos dos artefactos generados (son la composición del texto de
# delegación por runtime).
ORCHESTRATORS = (
    REPO_ROOT / "agents" / "cdad-orchestrator.md",
    REPO_ROOT / "agents" / "claude-code" / "cdad-orchestrator.md",
)

# PD-7b: fuentes dueñas de la sección `delegation` (D-1).
ADAPTERS = (
    REPO_ROOT / "sources" / "agents" / "adapters" / "opencode.md",
    REPO_ROOT / "sources" / "agents" / "adapters" / "claude-code.md",
)

# PD-1c/PD-7: el mapa de modelos retirado por U1 no debe reaparecer por nombre.
ROLE_SOURCES = REPO_ROOT / "sources" / "roles"
AGENTS_ROOT = REPO_ROOT / "agents"
RETIRED_MODEL_MAP = "cdad-models.sh"

# --------------------------------------------------------------------------
# PD-7b — vocabulario de PERFILES (prohibido en §2 y en la sección
# `delegation`). La palabra suelta se busca con límites de palabra: `profile`
# sólo cuenta como concepto de perfil, no dentro de otra palabra.
# --------------------------------------------------------------------------
PROFILES_VOCABULARY_PATTERNS = (
    (re.compile(r"(?i)\bperfil(?:es)?\b"),
     "vocabulario de perfiles («perfil/perfiles»)"),
    (re.compile(r"(?i)\bprofile(?:s)?\b"),
     "vocabulario de perfiles («profile/profiles»)"),
    (re.compile(r"--basic\b"),
     "flag `--basic` (alias del perfil retirado)"),
)

# --------------------------------------------------------------------------
# INV-5 REFORMULADA por A-5 — oráculo de AUSENCIA del requisito de familia/modelo
# del reviewer respecto del implementer: DEFINICIÓN ÚNICA en
# ``tests/test_006_002_u2_neutral_skill.py`` (``all_offenders`` y sus patrones,
# con los usos no relacionados de «familia» excluidos por colocación). Lo
# consumen esta unidad en sus superficies acotadas y el focal de U5'
# (``tests/test_006_003_u5p_no_family_requirement.py``) en las superficies
# amplias que A-5 nombra.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------- helpers


def read_document(path: Path, why: str) -> str:
    """Puerta del oráculo: el artefacto publicado existe y no está vacío."""
    assert path.is_file(), (
        f"{why}: el artefacto declarado por el contrato no existe "
        f"(drift de la superficie): {relative(path)}"
    )
    text = path.read_text(encoding="utf-8")
    assert text.strip(), (
        f"{why}: el artefacto declarado está vacío: {relative(path)}"
    )
    return text


def skill_text_files() -> list[Path]:
    """Todos los archivos regulares del árbol de skills (``grep -rE … skills/``).

    Se excluyen sólo los artefactos de caché de Python (``__pycache__``/``.pyc``),
    que no son texto instalable. La decodificación con reemplazo mantiene el
    barrido total, como el ``grep`` del contrato.
    """
    documents: list[Path] = []
    for path in sorted(SKILLS_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        documents.append(path)
    return documents


def text_of_any_file(path: Path) -> str:
    """Contenido del archivo como texto (reemplazo de bytes no decodificables)."""
    return path.read_text(encoding="utf-8", errors="replace")


def offenders_in(
    text: str,
    path: Path,
    patterns: tuple[tuple[re.Pattern[str], str], ...],
    first_line: int = 1,
) -> list[str]:
    """Ocurrencias de `patterns` en `text`, con archivo:línea y la etiqueta."""
    found: list[str] = []
    for pattern, label in patterns:
        for match in pattern.finditer(text):
            found.append(
                f"{relative(path)}:"
                f"{first_line - 1 + line_of(text, match.start())} — {label}: "
                f"{match.group(0)!r}"
            )
    return found


def model_offenders_in_file(path: Path) -> list[str]:
    """PD-7a: tokens de modelo de la spec presentes en un archivo publicado."""
    text = text_of_any_file(path)
    return [
        f"{relative(path)}:{line_of(text, match.start())} — "
        f"identificador de modelo concreto: {match.group(0)!r}"
        for match in MODEL_NAME_RE.finditer(text)
    ]


def delegation_block(path: Path, text: str) -> tuple[str, int]:
    """Bloque `<!-- cdad-section:delegation -->` de un adaptador fuente (D-1).

    Devuelve (texto del bloque, primera línea del bloque en el archivo) para que
    los ofensores se reporten con la línea del documento, no la del recorte.

    Su ausencia es drift del oráculo declarado (la sección existe hoy y es la
    dueña del contenido por PD-2(a)/(b) de 006-002); no se confunde con el fallo
    de contenido de esta unidad.
    """
    opening = SECTION_OPEN_RE.search(text)
    assert opening is not None, (
        "PD-7b: el adaptador fuente no expone el bloque "
        f"`<!-- cdad-section:delegation -->` declarado por el contrato "
        f"(drift del oráculo): {relative(path)}"
    )
    closing = SECTION_CLOSE_RE.search(text, opening.end())
    assert closing is not None, (
        f"PD-7b: el bloque `delegation` de {relative(path)} no tiene cierre "
        "`<!-- /cdad-section -->` (drift del oráculo)"
    )
    block = text[opening.end():closing.start()]
    assert block.strip(), (
        f"PD-7b: el bloque `delegation` de {relative(path)} está vacío"
    )
    return block, line_of(text, opening.end())


# (Los helpers `missing_concepts` / `missing_concepts_co_located` de la rama de
# PRESENCIA se retiran en este RED: su reemplazo declarado es `all_offenders`
# —oráculo de AUSENCIA—, que además consume el focal de U5'.)


# ------------------------------------------------------- PD-7a / INV-3 (textos)


class TestPd7aInstallableTextWithoutModels(unittest.TestCase):
    """PD-7a / INV-3: ningún texto instalable fija ni nombra un modelo concreto.

    Tokens del contrato: ``deepseek``, ``glm-``, ``qwen``, ``minimax``,
    ``sonnet``, ``haiku``, ``opus`` y el prefijo de gateway ``mofgw/``.
    """

    maxDiff = None

    def test_pd7a_installable_skill_tree_names_no_model(self) -> None:
        """PD-7a/INV-3: el árbol instalable de la skill (``skills/**``) no
        contiene ningún identificador de modelo concreto ni el prefijo de
        gateway (``grep -rE`` del contrato, sin salida)."""
        documents = skill_text_files()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo PD-7a: no se recolectó ningún archivo bajo "
            f"{relative(SKILLS_ROOT)}"
        )
        self.assertIn(
            SKILL_MD, documents,
            "drift del oráculo PD-7a: skills/cdad-cycle/SKILL.md no está en la "
            "superficie escaneada"
        )

        offenders: list[str] = []
        for path in documents:
            offenders.extend(model_offenders_in_file(path))

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-7a/INV-3: el texto instalable de la skill fija o nombra "
                "modelos concretos (el modelo de cada rol es el configurado en "
                f"la configuración de delegación): {offenders[:20]!r}"
            ),
        )

    def test_pd7a_generated_orchestrators_name_no_model(self) -> None:
        """PD-7a/INV-3: cada orquestador generado nombrado por el contrato
        (OpenCode y Claude Code) está libre de identificadores de modelo y del
        prefijo de gateway."""
        for path in ORCHESTRATORS:
            with self.subTest(orchestrator=relative(path)):
                self.assertTrue(
                    path.is_file(),
                    f"drift del oráculo PD-7a: falta el orquestador generado "
                    f"{relative(path)}",
                )
                offenders = model_offenders_in_file(path)
                self.assertEqual(
                    offenders, [],
                    msg=(
                        "PD-7a/INV-3: el orquestador generado fija o nombra "
                        "modelos concretos (ninguna superficie instalable fija "
                        f"ni nombra modelos): {offenders[:20]!r}"
                    ),
                )


# ------------------------------------------------- PD-7b / D7 — §2 de SKILL.md


class TestPd7bSkillSection2WithoutProfiles(unittest.TestCase):
    """PD-7b / D7 + INV-5 (A-5): §2 de ``SKILL.md`` no habla de perfiles y no
    exige ni declara la familia o el modelo del reviewer respecto del
    implementer."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read_document(SKILL_MD, "PD-7b")
        region = numbered_section_region(cls.text, 2)
        assert region is not None, (
            "drift del oráculo PD-7b: SKILL.md no expone una sección §2 "
            "delimitable por su encabezado numerado"
        )
        cls.section, cls.first_line, cls.last_line = region

    def test_pd7b_skill_section2_has_no_profile_vocabulary(self) -> None:
        """PD-7b/D7: §2 no nombra perfiles ni el flag ``--basic`` (la elección
        de modelo vive en la configuración de delegación, no en un perfil)."""
        offenders = offenders_in(
            self.section, SKILL_MD, PROFILES_VOCABULARY_PATTERNS,
            first_line=self.first_line,
        )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-7b/D7: §2 de SKILL.md conserva el vocabulario de perfiles "
                f"(líneas {self.first_line}-{self.last_line}): "
                f"{offenders[:20]!r}"
            ),
        )

    def test_pd7b_skill_section2_has_no_family_requirement(self) -> None:
        """PD-7b/INV-5 REFORMULADA por A-5: §2 no exige ni declara la familia o
        el modelo del reviewer respecto del implementer (el modelo de cada rol
        es el que configura el runtime; el de la delegación externa, la config
        de delegación)."""
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


# --------------------------------------- PD-7b / D7 — sección `delegation`


class TestPd7bAdapterDelegationSections(unittest.TestCase):
    """PD-7b / D7 + INV-5 (A-5): la sección ``delegation`` de cada adaptador
    fuente no habla de perfiles y no exige ni declara la familia o el modelo del
    reviewer respecto del implementer."""

    maxDiff = None

    def test_pd7b_adapter_delegation_blocks_have_no_profile_vocabulary(self) -> None:
        """PD-7b/D7: ningún bloque ``delegation`` menciona perfiles ni
        ``--basic`` (el desplazamiento de perfiles a la configuración de
        delegación vale también para las reglas de cada runtime)."""
        for path in ADAPTERS:
            with self.subTest(adapter=relative(path)):
                text = read_document(path, "PD-7b")
                block, first_line = delegation_block(path, text)
                offenders = offenders_in(
                    block, path, PROFILES_VOCABULARY_PATTERNS,
                    first_line=first_line,
                )
                self.assertEqual(
                    offenders, [],
                    msg=(
                        "PD-7b/D7: la sección `delegation` del adaptador "
                        f"conserva el vocabulario de perfiles: {offenders[:20]!r}"
                    ),
                )

    def test_pd7b_adapter_delegation_blocks_have_no_family_requirement(self) -> None:
        """PD-7b/INV-5 REFORMULADA por A-5: ningún bloque ``delegation`` exige
        ni declara la familia o el modelo del reviewer respecto del
        implementer."""
        for path in ADAPTERS:
            with self.subTest(adapter=relative(path)):
                text = read_document(path, "PD-7b")
                block, first_line = delegation_block(path, text)
                offenders = all_offenders(block, path, first_line)
                self.assertEqual(
                    offenders, [],
                    msg=(
                        "PD-7b/INV-5 (A-5): la sección `delegation` del "
                        "adaptador todavía exige o declara la familia/modelo del "
                        f"reviewer respecto del implementer: {offenders[:20]!r}"
                    ),
                )


# -------------------------- PD-7b / D7 — composición en los orquestadores


class TestPd7bGeneratedOrchestratorComposition(unittest.TestCase):
    """PD-7b / D7 + INV-5 (A-5): por composición, los dos orquestadores generados
    tampoco hablan de perfiles ni heredan el requisito de familia o modelo del
    reviewer respecto del implementer."""

    maxDiff = None

    def test_pd7b_generated_orchestrators_carry_no_profile_vocabulary(self) -> None:
        """PD-7b/D7: cada orquestador generado está libre del vocabulario de
        perfiles y del flag ``--basic`` (el caveat por perfil que F001 exigía
        hasta este RED se retira con el perfil mismo)."""
        for path in ORCHESTRATORS:
            with self.subTest(orchestrator=relative(path)):
                text = read_document(path, "PD-7b")
                offenders = offenders_in(text, path, PROFILES_VOCABULARY_PATTERNS)
                self.assertEqual(
                    offenders, [],
                    msg=(
                        "PD-7b/D7: el orquestador generado conserva el "
                        f"vocabulario de perfiles: {offenders[:20]!r}"
                    ),
                )

    def test_pd7b_generated_orchestrators_carry_no_family_requirement(self) -> None:
        """PD-7b/INV-5 REFORMULADA por A-5 (composición): ningún orquestador
        generado hereda el requisito de familia/modelo del reviewer respecto del
        implementer (por eso se escanea el documento completo: el artefacto
        compuesto no lleva marcadores de sección)."""
        for path in ORCHESTRATORS:
            with self.subTest(orchestrator=relative(path)):
                text = read_document(path, "PD-7b")
                offenders = all_offenders(text, path)
                self.assertEqual(
                    offenders, [],
                    msg=(
                        "PD-7b/INV-5 (A-5): el orquestador generado todavía "
                        "exige o declara la familia/modelo del reviewer respecto "
                        f"del implementer: {offenders[:20]!r}"
                    ),
                )


# ------------------------------- PD-1c / PD-7 — mapa de modelos retirado (U1)


class TestRetiredModelMapNotReferenced(unittest.TestCase):
    """PD-1c / PD-7 / INV-3: ``scripts/cdad-models.sh`` se retiró en U1 y ningún
    texto instalable vuelve a apoyarse en él — ni las fuentes de rol ni los
    agentes generados (que lo cargaban para resolver el modelo)."""

    maxDiff = None

    def test_retired_model_map_is_unreferenced_by_role_sources_and_generated_agents(
        self,
    ) -> None:
        """PD-1c/PD-7: las fuentes de rol y los agentes generados no nombran el
        mapa de modelos retirado (la delegación toma el modelo de la
        configuración, no de un mapa)."""
        sources = sorted(ROLE_SOURCES.glob("*.md"))
        agents = sorted(AGENTS_ROOT.glob("cdad-*.md")) + sorted(
            (AGENTS_ROOT / "claude-code").glob("*.md")
        )
        self.assertGreater(
            len(sources), 0,
            "drift del oráculo PD-7: no se recolectó ninguna fuente de rol bajo "
            f"{relative(ROLE_SOURCES)}"
        )
        self.assertGreater(
            len(agents), 0,
            "drift del oráculo PD-7: no se recolectó ningún agente generado "
            f"bajo {relative(AGENTS_ROOT)}"
        )

        offenders: list[str] = []
        for path in sources + agents:
            for number, line in enumerate(
                text_of_any_file(path).splitlines(), start=1
            ):
                if RETIRED_MODEL_MAP in line:
                    offenders.append(f"{relative(path)}:{number}")

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1c/PD-7/INV-3: el texto instalable sigue nombrando el mapa "
                f"de modelos retirado ({RETIRED_MODEL_MAP}): {offenders[:20]!r}"
            ),
        )


# --------------------------------------------------- INV-4 — sin `/tmp`


class TestInv4InstallableTextWithoutTmp(unittest.TestCase):
    """INV-4: ningún texto instalable nombra ``/tmp`` (invariante del plan §8
    punto 4; hoy se cumple en ``skills/`` y este test lo fija como
    no-regresión)."""

    TMP_RE = re.compile(r"/tmp\b")

    def test_inv4_installable_skill_text_names_no_tmp(self) -> None:
        """INV-4: el árbol instalable de la skill no nombra ``/tmp`` (una ruta
        temporal del host no puede filtrarse al texto que se distribuye)."""
        documents = skill_text_files()
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo INV-4: no se recolectó ningún archivo bajo "
            f"{relative(SKILLS_ROOT)}"
        )

        offenders: list[str] = []
        for path in documents:
            text = text_of_any_file(path)
            for match in self.TMP_RE.finditer(text):
                offenders.append(
                    f"{relative(path)}:{line_of(text, match.start())}"
                )

        self.assertEqual(
            offenders, [],
            msg=(
                "INV-4: el texto instalable nombra `/tmp` (ruta temporal del "
                f"host): {offenders[:20]!r}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
