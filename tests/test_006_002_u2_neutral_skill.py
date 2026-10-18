#!/usr/bin/env python3
"""006-002 U2 RED — §4 neutral de cdad-cycle y skill sin herramientas de runtime.

Contract:
- ``docs/specs/006-002-delegation-by-layer/spec.md`` §2 PD-1 (skill layer free
  of runtime tools and concrete models; oráculo de ausencia al inicio de §2),
  §2 PD-3 (§4 conserva el núcleo neutral de siete puntos, sin nombrar runtimes),
  §3 INV-1/INV-2.
- ``docs/specs/006-002-delegation-by-layer/plan.md`` ficha U2 (archivos y gate
  PD-1/PD-3) + enmienda A-1 (los asserts acoplados de esta superficie se
  reformulan en ESTE RED, nunca en el GREEN).

Oráculo de ausencia (spec §2, cabecera): el patrón de
``tests/test_005_010_t3_references.py`` (``CONCRETE_MODEL_ID_RE``,
``SPACED_MODEL_LINE_RE``, ``PROVIDER_RE`` — importados, una sola definición)
extendido con **formas de herramienta** de despacho: code-span ``task`` /
``delegate`` / ``Agent``, el token ``subagent_type``, ``opencode run``,
``sessions_spawn``, «Agent tool». NUNCA la palabra suelta *task* (prosa como
"atomic task": discovery §4 risk 6).

Exclusión declarada de esta unidad (con su dueño):
- ``references/context-meter.md`` — contrato de LECTOR/MEDICIÓN (INV-8): declara
  ``task``/``subagent`` como nombres de herramienta *reconocidos* (dato de
  medición, no instrucción de delegación).

Ya NO hay exclusiones temporales: el RED de **U3** (``test_006_002_u3_…``, PD-9/
PD-10) retiró las dos referencias por runtime del árbol instalable y la regla de
elección de transporte de ``cli-delegation.md``; el RED de **U4**
(``test_006_002_u4_skill_without_models.py``, PD-11) retiró la neutralización
TEMPORAL de §2 de ``SKILL.md`` (columna "Model family" + párrafo de perfiles)
que este módulo declaraba como deuda de esa unidad (enmienda A-1). El oráculo
corre ahora sobre el árbol instalable COMPLETO (``skills/cdad-cycle/**`` y
``skills/cdad-epic/**``) salvo ``context-meter.md`` (INV-8) — el contrato PD-1 no
distingue por unidad: ningún texto instalable de la skill nombra una herramienta
de despacho de un runtime ni un modelo concreto.

Mapa test → postcondición (un test por afirmación observable):
  1 ``TestPd1SkillWithoutRuntimeTools::test_pd1_no_dispatch_tool_form_in_installable_skill_text``   PD-1 / INV-1
  2 ``TestPd1SkillWithoutRuntimeTools::test_pd1_no_concrete_model_in_delegation_context``           PD-1 / INV-2
  3 ``TestPd3Section4NeutralCore::test_pd3_section4_keeps_the_seven_points_in_abstract_form``       PD-3
  4 ``TestPd3Section4NeutralCore::test_pd3_section4_names_no_runtime_tool_form``                    PD-3 / INV-1

RED esperado (árbol actual: U2 GREEN; el RED de U3 ya retiró las exclusiones
temporales de la superficie de PD-9/PD-10 y el de U4 la neutralización temporal
de §2 — superficie de PD-11):
- (1) PASA hoy (U3 ya en GREEN: las dos referencias por runtime salieron del
  árbol instalable y la regla de elección de transporte de ``cli-delegation.md``
  fue retirada): GUARD de conservación declarado — protege el GREEN contra la
  reaparición de una forma de herramienta de despacho en el texto instalable.
- (2) FALLA por AssertionError de CONTENIDO: el texto instalable fija modelos
  concretos — los de §2 de ``SKILL.md`` (columna "Model family", familia +
  versión: ``deepseek-v4-pro``/``deepseek-v4-flash``/``glm-5.2``, proveedor
  ``deepseek``) y el ejemplo de ``handoff-prompts.md:515``
  (``mofgw/qwen3.7-plus``) — exactamente la superficie de **PD-11 (U4)**, cuyo
  RED retiró la neutralización que este módulo declaraba; su ausencia la fija
  ``tests/test_006_002_u4_skill_without_models.py`` (enmienda A-1).
- (3)/(4): PASAN hoy (U2 GREEN); son los controles de conservación de §4.
Ningún fallo es ImportError/SyntaxError.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Reuso declarado (spec §2): los patrones de modelo/proveedor ya fijados por
# 005-010 T3 — una sola definición, sin copiarlos.
from tests.test_005_010_t3_references import (
    CONCRETE_MODEL_ID_RE,
    PROVIDER_RE,
    SPACED_MODEL_LINE_RE,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

SKILL_ROOTS = (
    REPO_ROOT / "skills" / "cdad-cycle",
    REPO_ROOT / "skills" / "cdad-epic",
)
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# --------------------------------------------------------------------------
# Exclusiones de esta unidad — cada una declara su dueño (spec §2 PD-1/PD-9,
# PD-10; INV-8).
# --------------------------------------------------------------------------

# INV-8 / PD-1: contrato de LECTOR (medición): reconoce `task`/`subagent` como
# nombres de herramienta observados, no instruye delegación.
READER_CONTRACT_EXCLUSIONS = (
    "skills/cdad-cycle/references/context-meter.md",
)
# Única exclusión vigente del oráculo de FORMAS DE HERRAMIENTA. Las exclusiones
# TEMPORALES de U3 (PD-9: las dos referencias por runtime; PD-10: la regla de
# elección de transporte de cli-delegation.md) se retiraron en el RED de U3
# (tests/test_006_002_u3_runtime_references.py): hoy el oráculo corre sobre el
# árbol instalable completo.
TOOL_FORM_EXCLUSIONS = READER_CONTRACT_EXCLUSIONS

# --------------------------------------------------------------------------
# Oráculo de ausencia — FORMAS DE HERRAMIENTA de despacho (spec §2, cabecera)
# --------------------------------------------------------------------------

TOOL_FORM_PATTERNS = (
    (re.compile(r"`\s*task\s*`"),
     "code-span `task` (forma de herramienta de despacho)"),
    (re.compile(r"`\s*delegate\s*`"),
     "code-span `delegate` (forma de herramienta de despacho)"),
    (re.compile(r"`\s*Agent\s*`"),
     "code-span `Agent` (forma de herramienta de despacho)"),
    (re.compile(r"(?i)\bsubagent_type\b"),
     "token `subagent_type` (parámetro de herramienta de despacho)"),
    (re.compile(r"(?i)\bopencode\s+run\b"),
     "invocación CLI `opencode run` (mecanismo de un runtime)"),
    (re.compile(r"(?i)\bsessions_spawn\b"),
     "token `sessions_spawn` (herramienta de un runtime)"),
    (re.compile(r"(?i)\bAgent\s+tool\b"),
     "«Agent tool» (herramienta de despacho de un runtime)"),
)

# --------------------------------------------------------------------------
# Oráculo de ausencia — MODELOS concretos (INV-2)
# --------------------------------------------------------------------------

# `claude-code` / `claude-code-*` son el nombre del RUNTIME (producto), no un
# modelo: ``CONCRETE_MODEL_ID_RE`` (familia + guion) los captura por prefijo
# `claude-`, así que el nombre del runtime se excluye explícitamente del
# oráculo de modelos.
RUNTIME_NAME_RE = re.compile(r"(?i)^claude-code[\w.\-]*$")


HEADING_RE = re.compile(r"^(#{1,6})[ \t]+\S")


def numbered_section_region(text: str, number: int) -> tuple[str, int, int] | None:
    """Región de la sección numerada `number` (el contrato la llama «§N»): del
    encabezado numerado N hasta el siguiente encabezado de nivel igual o
    superior. Devuelve (texto, primera línea, última línea) 1-based, o None si
    la sección no se puede delimitar. No captura subsecciones («4.1»)."""
    lines = text.splitlines()
    heading_re = re.compile(
        rf"^#{{1,6}}[ \t]*(?:§[ \t]*)?{number}(?!\d)(?!\.\d)[.)\s:—–-]?"
    )
    headings = [
        (index, len(match.group(1)))
        for index, line in enumerate(lines)
        if (match := HEADING_RE.match(line))
    ]
    for index, level in headings:
        if not heading_re.match(lines[index]):
            continue
        end = len(lines)
        for other, other_level in headings:
            if other > index and other_level <= level:
                end = other
                break
        return "\n".join(lines[index:end]), index + 1, end
    return None


def model_offences(text: str) -> list[str]:
    """Modelos/proveedores concretos presentes en `text` (INV-2), sin los
    nombres de runtime (`claude-code`)."""
    found: list[str] = []
    for pattern, label in (
        (CONCRETE_MODEL_ID_RE, "identificador de modelo concreto"),
        (SPACED_MODEL_LINE_RE, "nombre de modelo concreto espaciado"),
        (PROVIDER_RE, "nombre de proveedor concreto"),
    ):
        for match in pattern.finditer(text):
            token = match.group(0)
            if label == "identificador de modelo concreto" and RUNTIME_NAME_RE.match(token):
                continue
            found.append(f"{label}: {token!r}")
    return found


# --------------------------------------------------------------------------
# Recolección del texto instalable
# --------------------------------------------------------------------------


def relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def installable_text_documents() -> list[Path]:
    """Texto instalable de la SKILL: los documentos `.md` de
    ``skills/cdad-cycle/**`` y ``skills/cdad-epic/**`` (la prosa donde vive la
    regla de delegación; los ayudantes ejecutables y assets no son texto de
    delegación y quedan fuera del oráculo)."""
    documents: list[Path] = []
    for root in SKILL_ROOTS:
        documents.extend(sorted(path for path in root.rglob("*.md") if path.is_file()))
    return documents


def scanned_documents(exclusions: tuple[str, ...]) -> list[Path]:
    excluded = set(exclusions)
    return [path for path in installable_text_documents() if relative(path) not in excluded]


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def read(path: Path) -> str:
    assert path.is_file(), (
        "PD-1: el oráculo de ausencia apunta a un documento instalable "
        f"inexistente (drift de la superficie declarada): {relative(path)}"
    )
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Oráculo de AUSENCIA de A-5 (006-003 §9) — el requisito de familia/modelo del
# reviewer respecto del implementer se RETIRA del texto instalable (INV-5
# reformulada). DEFINICIÓN ÚNICA del oráculo: lo consumen
# ``tests/test_006_003_u3_texts_without_profiles.py`` (superficies acotadas),
# ``tests/test_006_003_u5p_no_family_requirement.py`` (focal) y
# ``tests/test_006_002_u4_skill_without_models.py`` / ``…_u1_delegation_section``
# (superficies de 006-002).
#
# Un ofensor es una línea que, junto a su ventana (±``FAMILY_WINDOW_LINES``
# líneas), usa «familia» en el sentido de A-5, nombra el rol reviewer/revisor y
# tiene mood de requisito/verificación/declaración (o su forma declarada
# «invariant not guaranteed» ligada a la familia).
#
# Usos NO relacionados excluidos por COLOCACIÓN (declarados, con su dueño):
# «failure family» / «failure-family» / «family of failures» / «familia de
# fallos» (clasificación de hallazgos: `stage-4-review.md`, `anti-patterns.md`)
# y «split-brain family» (`continuity.md`, familia de fallas de continuidad).
# --------------------------------------------------------------------------

FAMILY_RE = re.compile(r"(?i)\bfamil(?:y|ies|ia|ias)\b")
ROLE_ANCHOR_RE = re.compile(r"(?i)\b(reviewer|revisor)\b")

# La MOOD del requisito retirado: exigir/elegir/controlar/verificar/declarar la
# familia o comparar el modelo del reviewer con el del implementer.
FAMILY_REQUIREMENT_MOOD_RE = re.compile(
    r"(?i)\b(must|shall|should|require[sd]?|need(?:s|ed)?|"
    r"verif\w*|check\w*|checked|comprob\w*|compar\w*|control\w*|"
    r"declar\w*|guarantee\w*|garantiz\w*|ensure[sd]?|enforce[sd]?|"
    r"different|distinct|differ\w*|separate|separada|separado|"
    r"distinta|distinto|diferente|otra|otro)\b"
)

# La declaración de la rama retirada, ligada a la familia (A-5 §9: se retira).
FAMILY_NOT_GUARANTEED_RE = re.compile(
    r"(?i)invariant\s+not\s+guaranteed|invariante\s+no\s+garantizad\w*"
)

# Prefijo/sufijo inmediato que convierte «family» en un concepto ajeno a A-5.
UNRELATED_FAMILY_PREFIX_RE = re.compile(
    r"(?i)(failure|failures|fallo|fallos|split[-\s]?brain)[-\s]+$"
)
UNRELATED_FAMILY_SUFFIX_RE = re.compile(
    r"(?i)^[-\s]+(of\s+(a\s+|the\s+)?failures?|de\s+fall[oa]s?|de\s+fallas)\b"
)

# Ventana de co-ubicación: el requisito vive en su párrafo/ítem, no a distancia.
FAMILY_WINDOW_LINES = 3


def has_related_family(line: str) -> bool:
    """¿La línea usa «family» en el sentido de A-5 (no «failure family»)?

    Cada ocurrencia se juzga por su vecindad inmediata: los usos declarados como
    no relacionados (``failure famil…``, ``family of failures``, ``familia de
    fallos``, ``split-brain famil…``) quedan exentos; si un documento combina
    ambos sentidos, la ocurrencia relacionada sigue contando.
    """
    for match in FAMILY_RE.finditer(line):
        if UNRELATED_FAMILY_PREFIX_RE.search(line[:match.start()]):
            continue
        if UNRELATED_FAMILY_SUFFIX_RE.search(line[match.end():]):
            continue
        return True
    return False


def family_requirement_offenders(
    text: str, path: Path, first_line: int = 1
) -> list[str]:
    """El requisito retirado por A-5 (conceptos, no frases exactas).

    `first_line` permite reportar la línea del DOCUMENTO cuando `text` es una
    región (§2, un bloque ``delegation``).
    """
    lines = text.splitlines()
    offenders: list[str] = []
    for index, line in enumerate(lines):
        if not FAMILY_RE.search(line) or not has_related_family(line):
            continue
        lo = max(0, index - FAMILY_WINDOW_LINES)
        hi = min(len(lines), index + FAMILY_WINDOW_LINES + 1)
        chunk = "\n".join(lines[lo:hi])
        if not ROLE_ANCHOR_RE.search(chunk):
            continue
        if (
            FAMILY_REQUIREMENT_MOOD_RE.search(chunk)
            or FAMILY_NOT_GUARANTEED_RE.search(chunk)
        ):
            offenders.append(
                f"{relative(path)}:{first_line + index} — {line.strip()!r}"
            )
    return offenders


def family_not_guaranteed_offenders(
    text: str, path: Path, first_line: int = 1
) -> list[str]:
    """La declaración «invariant not guaranteed» ligada a la familia (A-5).

    El enunciado por sí solo no basta (puede describir otro invariante): sólo
    cuenta cuando la MISMA ventana usa «familia» en el sentido de A-5.
    """
    lines = text.splitlines()
    offenders: list[str] = []
    for index, line in enumerate(lines):
        if not FAMILY_NOT_GUARANTEED_RE.search(line):
            continue
        lo = max(0, index - FAMILY_WINDOW_LINES)
        hi = min(len(lines), index + FAMILY_WINDOW_LINES + 1)
        if not any(has_related_family(window_line) for window_line in lines[lo:hi]):
            continue
        offenders.append(f"{relative(path)}:{first_line + index} — {line.strip()!r}")
    return offenders


def all_offenders(text: str, path: Path, first_line: int = 1) -> list[str]:
    """Las dos formas del requisito retirado por A-5, en un solo oráculo."""
    return (
        family_requirement_offenders(text, path, first_line)
        + family_not_guaranteed_offenders(text, path, first_line)
    )


# --------------------------------------------------------------------------
# PD-1 / INV-1 — la skill no nombra herramientas de despacho de un runtime
# --------------------------------------------------------------------------


class TestPd1SkillWithoutRuntimeTools(unittest.TestCase):
    """PD-1: ningún texto instalable de ``skills/cdad-cycle/**`` y
    ``skills/cdad-epic/**`` nombra una herramienta de despacho de un runtime ni
    un modelo concreto en un contexto de delegación."""

    def test_pd1_no_dispatch_tool_form_in_installable_skill_text(self) -> None:
        """PD-1/INV-1: ausencia de FORMAS DE HERRAMIENTA de despacho en el texto
        instalable de la skill (code-span `task`/`delegate`/`Agent`,
        `subagent_type`, `opencode run`, `sessions_spawn`, «Agent tool»); la
        palabra suelta *task* NO cuenta."""
        documents = scanned_documents(TOOL_FORM_EXCLUSIONS)
        self.assertGreater(
            len(documents), 0,
            "drift del oráculo PD-1: no se recolectó ningún documento instalable "
            f"bajo {[relative(root) for root in SKILL_ROOTS]}"
        )
        self.assertIn(
            SKILL_MD, documents,
            "drift del oráculo PD-1: skills/cdad-cycle/SKILL.md no está en la "
            "superficie escaneada"
        )

        offenders: list[str] = []
        for path in documents:
            text = read(path)
            for pattern, label in TOOL_FORM_PATTERNS:
                for match in pattern.finditer(text):
                    offenders.append(
                        f"{relative(path)}:{line_of(text, match.start())} — {label}"
                    )

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1/INV-1: el texto instalable de la skill nombra formas de "
                "herramienta de despacho de un runtime (el mecanismo pertenece al "
                "orquestador de cada runtime, no a la skill): "
                f"{offenders[:20]!r}"
            ),
        )

    def test_pd1_no_concrete_model_in_delegation_context(self) -> None:
        """PD-1/INV-2: ausencia de modelos concretos y de proveedores en TODO el
        texto instalable de la skill — incluida §2 de ``SKILL.md`` (la familia de
        cada rol es la configurada en el runtime; la skill no nombra ninguna) —
        salvo la única exclusión con dueño (``context-meter.md``, INV-8)."""
        documents = scanned_documents(TOOL_FORM_EXCLUSIONS)
        self.assertGreater(len(documents), 0, "drift del oráculo PD-1 (modelos)")

        offenders: list[str] = []
        for path in documents:
            text = read(path)
            for offence in model_offences(text):
                offenders.append(f"{relative(path)} — {offence}")

        self.assertEqual(
            offenders, [],
            msg=(
                "PD-1/INV-2: el texto instalable de la skill fija modelos "
                "concretos o proveedores (el modelo de cada rol es el configurado "
                f"en el runtime): {offenders[:20]!r}"
            ),
        )


# --------------------------------------------------------------------------
# PD-3 — §4 conserva el núcleo neutral de siete puntos, sin nombrar runtimes
# --------------------------------------------------------------------------


def section4_region(text: str) -> tuple[str, int, int] | None:
    """Región de §4 (spec PD-3: ``SKILL.md`` §4)."""
    return numbered_section_region(text, 4)


def require_any(text: str, alternatives: tuple[str, ...], concept: str) -> str | None:
    """Concepto exigido con alternativas de idioma (patrón `require_any` de
    005-010 T3): devuelve None si el concepto está, o el detalle de su falta."""
    lowered = text.lower()
    if any(alternative.lower() in lowered for alternative in alternatives):
        return None
    return f"concepto ausente '{concept}' (alternativas buscadas {list(alternatives)!r})"


# Los SIETE puntos de §4 (spec §2 PD-3, en su orden) con alternativas de idioma.
SECTION4_CONCEPTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("1. principio de la delegación", ("principle", "principio")),
    ("2a. orden — mecanismo nativo", ("native", "nativo")),
    ("2b. orden — handoff", ("handoff",)),
    ("2c. orden — inline", ("inline",)),
    ("3. regla de adaptadores: dueño del ciclo de vida de la sesión",
     ("session lifecycle", "session's lifecycle", "lifecycle of the session",
      "ciclo de vida de la sesión", "ciclo de vida de la sesion")),
    ("4. invariantes de rol", ("invariant", "invariante")),
    ("5. spawn guard", ("spawn guard", "spawn")),
    ("6. recibo", ("receipt", "recibo")),
    ("7a. paquete / re-entry", ("re-entry", "reentry", "reentrada", "reingreso",
                                "packet", "paquete")),
    ("7b. independiente del transporte", ("transport", "transporte")),
)


class TestPd3Section4NeutralCore(unittest.TestCase):
    """PD-3: ``SKILL.md`` §4 conserva, en forma abstracta, los siete puntos —
    principio; orden nativo → handoff → inline; regla de adaptadores por dueño
    del ciclo de vida de la sesión; invariantes de rol; spawn guard; recibo;
    paquete y re-entry independientes del transporte — sin nombrar runtimes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = read(SKILL_MD)
        region = section4_region(cls.text)
        assert region is not None, (
            "drift del oráculo PD-3: SKILL.md no expone una sección §4 "
            "delimitable por su encabezado numerado"
        )
        cls.section, cls.first_line, cls.last_line = region

    def test_pd3_section4_keeps_the_seven_points_in_abstract_form(self) -> None:
        """PD-3: los siete puntos están presentes en §4 en forma abstracta
        (concepto con alternativas de idioma; la redacción es libre)."""
        missing = [
            detail
            for concept, alternatives in SECTION4_CONCEPTS
            if (detail := require_any(self.section, alternatives, concept))
        ]
        self.assertEqual(
            missing, [],
            msg=(
                "PD-3: §4 de SKILL.md no conserva el núcleo neutral completo "
                f"(líneas {self.first_line}-{self.last_line}). Ausentes: {missing}"
            ),
        )

    def test_pd3_section4_names_no_runtime_tool_form(self) -> None:
        """PD-3/INV-1: §4 (el núcleo neutral) no nombra ninguna forma de
        herramienta de despacho de un runtime — el mecanismo concreto vive en el
        orquestador de cada runtime."""
        offenders: list[str] = []
        for pattern, label in TOOL_FORM_PATTERNS:
            for match in pattern.finditer(self.section):
                offenders.append(
                    f"{relative(SKILL_MD)}:{self.first_line - 1 + line_of(self.section, match.start())}"
                    f" — {label}"
                )
        self.assertEqual(
            offenders, [],
            msg=(
                "PD-3/INV-1: §4 de SKILL.md nombra formas de herramienta de "
                "despacho de un runtime (debe ser abstracto: el mecanismo vive en "
                f"el orquestador generado): {offenders[:20]!r}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
