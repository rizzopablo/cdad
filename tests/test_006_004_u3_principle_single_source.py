#!/usr/bin/env python3
"""006-004 U3 RED — el principio: una casa, dos obligaciones, un límite.

Contrato:
- ``docs/specs/006-004-active-decisions-table/spec.md`` (aprobada 2026-10-20)
  §2.6 (la casa, las dos obligaciones y el límite), §3 **PD-8** (las dos
  responsabilidades donde se aplican), §3 **PD-10** (la fuente única, las dos
  obligaciones y el límite), §3 **PD-13** (las guardas vigentes siguen verdes:
  bloque estático bajo el techo, ``make staging`` determinista, agentes
  generados con el texto), §4 **INV-1** (una decisión, una casa), §4 **INV-12**
  (la regla de rol no se duplica), §6 **V-2** (``make staging`` determinista) y
  §6 **V-4** (el bloque estático bajo el techo).
- ``docs/specs/006-004-active-decisions-table/plan.md`` §3 **ficha U3** (archivos,
  RED, regresiones, A-1) y su bloque ``plan-tasks`` (los ``observable_checks`` de
  U3, que son el contrato operativo de este RED).

Superficie observable bajo prueba (caja negra: sólo TEXTO publicado y
PROCESOS REALES; la implementación NUNCA se lee, NUNCA se importa):

- ``skills/cdad-cycle/references/design-principles.md`` — la casa canónica
  (archivo NUEVO: hoy no existe ⇒ este RED falla por ausencia de
  comportamiento, no por error de sintaxis);
- ``sources/roles/architect.md`` y ``sources/roles/reviewer.md`` — las fuentes
  editables de cada rol;
- ``skills/cdad-cycle/packets/roles/architect.md`` y
  ``skills/cdad-cycle/packets/roles/reviewer.md`` — los bloques estáticos (la
  superficie que viaja en la ruta de paquete, donde el rol NO carga el skill:
  spec §2.6, D-2);
- ``skills/cdad-cycle/references/stage-4-review.md`` — el dueño canónico del
  deber del reviewer sobre la tabla;
- ``skills/cdad-cycle/SKILL.md`` — la tabla «How to read the references»;
- los agentes GENERADOS y los PROMOVIDOS del rol architect y del reviewer —
  salidas declaradas de ``scripts/cdad-generate.py`` (``Makefile``:15-18): se
  generan invocando el generador como PROCESO en una COPIA DESCARTABLE del
  repo (nunca en el árbol de trabajo, nunca en el HOME real);
- el bloque estático de los 14 pares rol/subfase — medido sobre las fuentes de
  instrucción públicas que el producto compone.

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
la spec §2.6 y la ficha U3 fijan el contrato y dejan la redacción dentro):

1. **La casa canónica** es ``skills/cdad-cycle/references/design-principles.md``
   y lleva una SECCIÓN que nombra el principio (general / specific) con el
   **texto del principio** y **su límite** (el límite del principio: mejora el
   juicio de diseño y NO aumenta las justificaciones que los agentes deben
   producir). Es la **única** casa del texto normativo.
2. **Un concepto, varias redacciones.** Los conceptos se derivan por
   **vocabulario** (con alternativas de idioma), NO por frase exacta: la
   redacción es libre; el concepto no. Sólo se exige **verbatim** lo que la
   ficha cita verbatim (los nombres de archivo: ``design-principles.md``,
   ``docs/adr/``).
3. **La unicidad** (INV-1) se mide sobre el **texto normativo derivado de la
   casa canónica**: las frases de la sección que enuncia el principio (y su
   límite) no pueden aparecer en NINGÚN otro archivo del árbol instalable
   (``skills/``, ``sources/``, ``agents/``). La comparación es insensible al
   ajuste de línea (se normalizan los espacios), de modo que una copia
   re-ajustada también se detecta.
4. **Las dos obligaciones** viven en la fuente de cada rol **y** en su bloque
   estático, y **apuntan** al dueño canónico (``design-principles.md``) sin
   copiar su texto:
   - **architect**: considera las alternativas generales y específicas y explica
     el criterio elegido (conceptos: alternativa · general · specific ·
     criterio; el puntero al archivo canónico);
   - **reviewer**: evalúa **consecuencias reales** (duplicación que puede
     divergir · complejidad innecesaria · pérdida de capacidades ·
     acoplamiento) y su **límite** (la falta de una abstracción, por sí sola, no
     es un defecto). El **límite** está en las **dos superficies** del reviewer
     (su fuente y su bloque estático); las cuatro consecuencias están en su
     **fuente** (el bloque estático lleva la obligación mínima: el límite y el
     puntero).
5. **El deber del reviewer sobre la tabla** (PD-8) vive en
   ``references/stage-4-review.md`` y nombra las **dos** comprobaciones:
   (a) **alineación** — cada fila apunta a un archivo que existe en
   ``docs/adr/``; (b) **respeto** — el cambio respeta las decisiones vigentes
   de su rol.
6. **``SKILL.md``** gana una **fila** en la tabla «How to read the references»
   para el archivo nuevo.
7. **Los agentes** (generados y promovidos) llevan el texto tras ``make
   agents``; ``make staging`` es **determinista** (dos corridas, mismos bytes).
8. **El techo del bloque estático** sigue siendo **12000 bytes** y los 14 pares
   rol/subfase se miden (V-4: la medición se repite y se registra).

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica):

- El RED **no** congela el texto literal del principio: lo DERIVA de la casa
  canónica (la casa canónica es la fuente de la verdad; el RED la usa como
  oráculo, no la dicta).
- El RED **no** exige ninguna redacción concreta de las obligaciones: exige los
  CONCEPTOS y el PUNTERO.
- El RED **no** exige que la casa canónica mentione el ADR-034 ni la tabla: eso
  es de U5/U7 (superficies distintas, plan §1.1).
- El RED **no** toca ``tests/validate-consistency.sh``: el bloque de texto del
  validador de esta feature lo escriben U4 (plantilla + procedimiento) y U7
  (siembra), y esta unidad lo verifica con su propio oráculo, más preciso
  (derivación por concepto y control de vacuidad). Queda declarado para el
  orquestador.

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** El conjunto cerrado del request se **extiende** con una propiedad
declarada; la forma de las secciones del paquete se comprueba **por
presencia**; ningún test fija un digest literal de una fuente de instrucción;
el exit gate de stage 5 no cambia; la subfase del reviewer no se toca; los
agentes son salidas declaradas y ``make agents`` los regenera. Este RED
**vuelve a comprobar** los controles negativos (la unicidad de la casa y la
ausencia de copia) y **sólo añade casos**: no modifica, no sustituye y no
invisibiliza ninguna prueba vigente. El RED de U3 no toca ningún archivo de
``tests/`` ajeno a este.

RED esperado contra el árbol vigente (OBSERVADO; declarado, no accidental):

- Fallan por ``AssertionError`` de CONTRATO las **trece** comprobaciones de
  contenido: la casa canónica no existe (y, por tanto, no hay texto normativo
  que derivar, ni unicidad que medir), las dos fuentes de rol no nombran su
  obligación ni apuntan al dueño canónico, sus bloques estáticos tampoco,
  ``stage-4-review.md`` no nombra las dos comprobaciones sobre la tabla y
  ``SKILL.md`` no tiene la fila del archivo nuevo. Los agentes generados y los
  promovidos no llevan el texto (la fuente no lo tiene).
- **Pasan hoy** los dos **controles**: ``make staging`` es determinista (V-2) y
  los 14 bloques estáticos están bajo el techo de 12000 bytes (V-4). No son la
  falla: son guardas que deben seguir verdes después del GREEN.
- Ningún fallo es ImportError, SyntaxError, NameError ni error de fixture: los
  artefactos requeridos que faltan se reportan con ``self.fail``/``assert`` y
  su mensaje contractual.

Mapeo test → postcondición (un test por aserción observable; las filas 2, 3 y 8
son controles declarados):

  1  ``TestPd10CanonicalHouse::test_pd10_the_canonical_file_exists_and_carries_the_principle_and_its_limit``   PD-10
  2  ``TestPd10CanonicalHouse::test_pd10_the_normative_text_of_the_principle_lives_in_exactly_one_installable_file``  PD-10 / INV-1
  3  ``TestPd10CanonicalHouse::test_pd10_no_installable_surface_copies_the_principle_text``   PD-10 / INV-12
  4  ``TestPd10ArchitectDuty::test_pd10_the_architect_source_names_its_duty_and_points_to_the_canonical_owner``  PD-10
  5  ``TestPd10ArchitectDuty::test_pd10_the_architect_static_block_carries_the_duty_and_the_pointer``   PD-10 / D-2
  6  ``TestPd10ReviewerCriterion::test_pd10_the_reviewer_source_names_its_duty_and_points_to_the_canonical_owner``  PD-10
  7  ``TestPd10ReviewerCriterion::test_pd10_the_reviewer_static_block_carries_the_limit_and_the_pointer``   PD-10 / D-2
  8  ``TestPd10ReviewerCriterion::test_pd10_the_reviewer_criterion_names_the_four_consequences_and_the_limit``   PD-10
  9  ``TestPd8ReviewerDutyOverTheTable::test_pd8_stage4_review_names_the_alignment_check_against_docs_adr``   PD-8
  10 ``TestPd8ReviewerDutyOverTheTable::test_pd8_stage4_review_names_the_respect_check_for_the_role_decisions``   PD-8
  11 ``TestPd10SkillReferenceRow::test_pd10_skill_md_references_table_has_the_row_of_the_new_file``   PD-10
  12 ``TestPd13GeneratedAgents::test_pd13_the_generated_agents_carry_the_duty_after_make_agents``   PD-13
  13 ``TestPd13GeneratedAgents::test_pd13_the_promoted_agents_of_the_repo_carry_the_duty``   PD-13
  14 ``TestPd13GeneratedAgents::test_pd13_make_staging_is_deterministic_across_two_runs``   PD-13 / V-2 (CONTROL)
  15 ``TestPd13StaticBlockCeiling::test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling``   PD-13 / V-4 (CONTROL)
"""

from __future__ import annotations

import atexit
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_role_packet_render import PacketFixture, static_instruction_bytes

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Superficies (rutas relativas al repo; ninguna ruta del host)
# ---------------------------------------------------------------------------

CANONICAL_RELPATH = "skills/cdad-cycle/references/design-principles.md"
CANONICAL = REPO_ROOT / CANONICAL_RELPATH

# El puntero al dueño canónico: el NOMBRE del archivo (verbatim de la ficha).
POINTER = "design-principles.md"

ARCHITECT_SOURCE = REPO_ROOT / "sources" / "roles" / "architect.md"
REVIEWER_SOURCE = REPO_ROOT / "sources" / "roles" / "reviewer.md"
ARCHITECT_BLOCK = REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "roles" / "architect.md"
REVIEWER_BLOCK = REPO_ROOT / "skills" / "cdad-cycle" / "packets" / "roles" / "reviewer.md"
STAGE4_REVIEW = REPO_ROOT / "skills" / "cdad-cycle" / "references" / "stage-4-review.md"
SKILL_MD = REPO_ROOT / "skills" / "cdad-cycle" / "SKILL.md"

# El árbol instalable donde el texto normativo debe vivir en UN solo archivo.
INSTALLABLE_ROOTS = ("skills", "sources", "agents")

# Los agentes de los dos roles que U3 toca: GENERADOS (en el staging) y
# PROMOVIDOS (en el repo, por `make agents`).
STAGED_AGENTS = (
    "agents/opencode/cdad-architect.md",
    "agents/opencode/cdad-architect-odoo.md",
    "agents/opencode/cdad-reviewer.md",
    "agents/opencode/cdad-reviewer-odoo.md",
    "agents/claude-code/cdad-architect.md",
    "agents/claude-code/cdad-architect-odoo.md",
    "agents/claude-code/cdad-reviewer.md",
    "agents/claude-code/cdad-reviewer-odoo.md",
)
PROMOTED_AGENTS = (
    "agents/cdad-architect.md",
    "agents/cdad-architect-odoo.md",
    "agents/claude-code/cdad-architect.md",
    "agents/claude-code/cdad-architect-odoo.md",
    "agents/cdad-reviewer.md",
    "agents/cdad-reviewer-odoo.md",
    "agents/claude-code/cdad-reviewer.md",
    "agents/claude-code/cdad-reviewer-odoo.md",
)

# El techo DECLARADO del bloque estático (V-4): `CDAD_STATIC_BLOCK_LIMIT`,
# default 12000.
STATIC_CEILING = 12000
PACKETS_ROOT = REPO_ROOT / "skills" / "cdad-cycle" / "packets"
ROLE_SUBSTAGE_PAIRS = (
    ("architect", "discovery"),
    ("architect", "brainstorm"),
    ("architect", "draft"),
    ("test-writer", "audit"),
    ("test-writer", "post-audit"),
    ("test-writer", "red"),
    ("test-writer", "properties"),
    ("test-writer", "e2e"),
    ("implementer", "green"),
    ("implementer", "refactor"),
    ("implementer", "review-fix"),
    ("reviewer", "review"),
    ("reviewer", "plan-review"),
    ("scribe", "memory"),
)

# ---------------------------------------------------------------------------
# Conceptos (derivación textual por CONCEPTO; la redacción es libre)
# ---------------------------------------------------------------------------

# «general» / «generalmente» / «universally» (el eje del principio).
GENERAL = re.compile(r"(?i)\bgenera\w*|\buniversal\w*")
# «specific» / «específica» / «concreto» / «particular» (el otro eje).
# NO se acepta «spec»/«specification»: es el nombre del documento, no el
# concepto (evita un falso positivo en las fuentes que nombran la spec).
SPECIFIC = re.compile(
    r"(?i)\bspecific\w*|\bespec[ií]fic\w*|\bconcretely\b|\bconcreto\w*|\bparticul\w*"
)
# «alternativa» / «option» / «posibilidad».
ALTERNATIVE = re.compile(
    r"(?i)\balternativ\w*|\boption\w*|\bopci[oó]n\w*|\bposibilidad\w*|\bpossibilit\w*"
)
# «criterio» / «criterion».
CRITERION = re.compile(r"(?i)\bcriteri\w*")

# Las cuatro consecuencias reales del criterio del reviewer.
DUPLICATION = re.compile(r"(?i)\bduplicat\w*|\bduplic\w*")
DIVERGENCE = re.compile(r"(?i)\bdiverg\w*")
COMPLEXITY = re.compile(r"(?i)\bcomplej\w*|\bcomplex\w*")
UNNECESSARY = re.compile(
    r"(?i)\bnecesari\w*|\bunnecessar\w*|\bexcesiv\w*|\bavoidab\w*|\bunneeded\w*"
)
CAPABILITY = re.compile(r"(?i)\bcapabilit\w*|\bcapacidad\w*")
LOSS = re.compile(r"(?i)\bp[ée]rdida\b|\bperder\b|\bperdi[oó]\b|\bloss\b|\blose\b|\bdegrad\w*")
COUPLING = re.compile(r"(?i)\bacoplam\w*|\bacoplad\w*|\bcoupling\b|\bcoupled\b")

# El LÍMITE del criterio del reviewer: la falta de una abstracción, por sí
# sola, no es un defecto.
ABSTRACTION = re.compile(r"(?i)\babstrac\w*")
DEFECT = re.compile(r"(?i)\bdefect\w*|\bdefecto\w*")
NEGATION = re.compile(r"(?i)\bnot\b|\bnever\b|\bno\b|\bnunca\b|\bsin\b")

# El LÍMITE del PRINCIPIO (la casa canónica): mejora el juicio de diseño y NO
# aumenta las justificaciones que los agentes deben producir.
JUSTIFICATION = re.compile(r"(?i)\bjustific\w*")
INCREASE_NEGATION = re.compile(
    r"(?i)\b(?:does not|do not|doesn't|not)\s+"
    r"(?:increase|add|create|require|produce|multiply|generate)\b"
    r"|\bno\s+(?:aumenta|incrementa|multiplica|agrega|añade|crea|exige|produce|genera)\b"
)

# El deber del reviewer sobre la tabla (PD-8).
DOCS_ADR = re.compile(r"docs/adr/")
ROW = re.compile(r"(?i)\bfila|\brow\b")
ALIGNMENT = re.compile(r"(?i)\balinea\w*|\balign\w*|\bcontrast\w*|\bcompar\w*|\bcoincid\w*")
DECISION = re.compile(r"(?i)\bdecisi\w*|\bdecid\w*")
CURRENT = re.compile(r"(?i)\bvigent\w*|\bcurrent\b|\bin force\b|\ben vigor\b")
RESPECT = re.compile(r"(?i)\brespet\w*|\brespect\w*")

# Ventana de vecindad (caracteres) para las parejas de conceptos que la
# ficha declara en UNA línea.
NEAR = 2000
NEAR_TIGHT = 800


# ---------------------------------------------------------------------------
# Helpers (caja negra; un artefacto que falta = estado conductual)
# ---------------------------------------------------------------------------


def relative(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_document(path: Path, label: str) -> str:
    """Artefacto requerido: si falta, es estado conductual (nunca ImportError)."""
    if not path.is_file():
        raise AssertionError(
            f"{label}: el artefacto declarado por el contrato no existe: "
            f"{relative(path)}"
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        raise AssertionError(f"{label}: el artefacto declarado está vacío: {relative(path)}")
    return text


def normalized(text: str) -> str:
    """Normalización de comparación: espacios colapsados y minúsculas.

    Hace la detección de copias insensible al ajuste de línea (una copia
    re-ajustada sigue siendo una copia).
    """
    return re.sub(r"\s+", " ", text).strip().lower()


def _strip_marker(line: str) -> str:
    """La línea sin su viñeta (`- `, `* `, `1. `) ni su encabezado (`## `)."""
    line = re.sub(r"^#+\s*", "", line)
    line = re.sub(r"^[-*+]\s+", "", line)
    line = re.sub(r"^\d+[.)]\s+", "", line)
    return line.strip()


def sentences(text: str) -> list[str]:
    """Unidades normativas de un texto: las oraciones, **reunidas aunque el
    ajuste de línea las parta**.

    Una línea que no cierra una oración se une con la siguiente (una prosa
    envuelta en varias líneas es UNA oración); un encabezado o una viñeta
    cortan la unidad. Se descartan los fragmentos demasiado cortos para
    enunciar una regla.
    """
    units: list[str] = []
    buffer = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if buffer:
                units.append(buffer)
                buffer = ""
            continue
        bullet = re.match(r"^([-*+]|\d+[.)])\s+", line)
        if bullet:
            if buffer:
                units.append(buffer)
                buffer = ""
            line = line[bullet.end() :]
        line = line.strip()
        if not line:
            continue
        buffer = f"{buffer} {line}" if buffer else line
        if re.search(r"[.!?][\"')\]]*$", buffer):
            units.append(buffer)
            buffer = ""
    if buffer:
        units.append(buffer)

    result: list[str] = []
    for unit in units:
        for part in re.split(r"(?<=[.!?])\s+", unit):
            part = part.strip()
            if len(part.split()) >= 6:
                result.append(part)
    return result


def line_units(text: str) -> list[str]:
    """Unidades por línea (la unidad más fina que se puede copiar): se usa
    como aguja FINO del control de copia, para que una copia de una sola línea
    también se detecte."""
    units: list[str] = []
    for raw in text.splitlines():
        line = _strip_marker(raw)
        if len(line.split()) >= 8:
            units.append(line)
    return units


def normative_units(text: str) -> list[str]:
    """Las unidades normativas del texto: oraciones (reunidas) + líneas.

    La unión es deliberada: la oración Reunida detecta la copia completa
    (aunque se re-ajuste) y la línea detecta la copia de un fragmento.
    """
    seen: set[str] = set()
    units: list[str] = []
    for unit in sentences(text) + line_units(text):
        key = normalized(unit)
        if key and key not in seen:
            seen.add(key)
            units.append(unit)
    return units


def canonical_section(text: str) -> tuple[str, str] | None:
    """(encabezado, cuerpo) de la sección que nombra el principio.

    La sección es la que la ficha declara: su encabezado nombra «general» y
    «specific». El cuerpo va hasta el siguiente encabezado de nivel igual o
    superior.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        if not (GENERAL.search(stripped) and SPECIFIC.search(stripped)):
            continue
        level = len(stripped) - len(stripped.lstrip("#"))
        body: list[str] = []
        for other in lines[index + 1 :]:
            candidate = other.strip()
            if candidate.startswith("#"):
                other_level = len(candidate) - len(candidate.lstrip("#"))
                if other_level <= level:
                    break
            body.append(other)
        return stripped, "\n".join(body)
    return None


def principle_units(text: str) -> list[str]:
    """Las frases de la casa canónica que ENUNCIAN el principio (o su límite).

    Se excluyen las frases que sólo son el LÍMITE DEL REVIEWER (la falta de
    una abstracción no es un defecto): ése vive por diseño en las dos
    superficies del reviewer (PD-10).
    """
    units: list[str] = []
    for unit in normative_units(text):
        if ABSTRACTION.search(unit) and DEFECT.search(unit):
            # Límite del reviewer: vive en dos superficies por contrato.
            continue
        if GENERAL.search(unit) and SPECIFIC.search(unit):
            units.append(unit)
        elif JUSTIFICATION.search(unit) and INCREASE_NEGATION.search(unit):
            units.append(unit)
    return units


def copies_of(needles: list[str], documents: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """(archivo, frase) donde una de las frases normativas aparece copiada.

    Oráculo de AUSENCIA de copia: se compara el texto normalizado de cada
    frase contra el texto normalizado de cada documento (así una copia
    re-ajustada se detecta igual).
    """
    offenders: list[tuple[str, str]] = []
    for relpath, text in documents:
        haystack = normalized(text)
        for needle in needles:
            probe = normalized(needle)
            if probe and probe in haystack:
                offenders.append((relpath, needle))
    return offenders


def installable_documents() -> list[tuple[str, str]]:
    """Todos los archivos regulares del árbol instalable (`skills/`, `sources/`,
    `agents/`), con su texto. El barrido es total (como el `grep -rl` del
    contrato): los archivos no decodificables se leen con reemplazo."""
    documents: list[tuple[str, str]] = []
    for root_name in INSTALLABLE_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            documents.append(
                (relative(path), path.read_text(encoding="utf-8", errors="replace"))
            )
    return documents


def _window(text: str, center: int, radius: int) -> tuple[int, int]:
    return max(0, center - radius), min(len(text), center + radius)


def _near(text: str, pattern: re.Pattern[str], center: int, radius: int = NEAR) -> bool:
    low, high = _window(text, center, radius)
    return bool(pattern.search(text, low, high))


def names_pointer(text: str) -> bool:
    """El texto apunta al dueño canónico (el nombre del archivo)."""
    return POINTER in text


def architect_duty_present(text: str) -> bool:
    """La obligación del architect: alternativas generales y específicas y el
    criterio elegido, con los cuatro conceptos en la misma zona."""
    for match in CRITERION.finditer(text):
        if (
            _near(text, GENERAL, match.start())
            and _near(text, SPECIFIC, match.start())
            and _near(text, ALTERNATIVE, match.start())
        ):
            return True
    return False


def architect_duty_minimum_present(text: str) -> bool:
    """La obligación MÍNIMA del architect (la que viaja en el bloque
    estático): general, specific y el criterio."""
    for match in CRITERION.finditer(text):
        if _near(text, GENERAL, match.start()) and _near(text, SPECIFIC, match.start()):
            return True
    return False


def four_consequences_present(text: str) -> bool:
    """Las cuatro consecuencias reales, nombradas en la misma zona del texto.

    La ancla es «duplicación que puede divergir»; las otras tres consecuencias
    tienen que aparecer en su vecindad (la ficha las declara en UNA línea).
    """
    for match in DUPLICATION.finditer(text):
        low, high = _window(text, match.start(), NEAR)
        if not DIVERGENCE.search(text, low, high):
            continue
        if not (COMPLEXITY.search(text, low, high) and UNNECESSARY.search(text, low, high)):
            continue
        if not (CAPABILITY.search(text, low, high) and LOSS.search(text, low, high)):
            continue
        if not COUPLING.search(text, low, high):
            continue
        return True
    return False


def reviewer_limit_present(text: str) -> bool:
    """El límite del reviewer: la falta de una abstracción, por sí sola, no es
    un defecto."""
    for match in ABSTRACTION.finditer(text):
        low, high = _window(text, match.start(), 400)
        if DEFECT.search(text, low, high) and NEGATION.search(text, low, high):
            return True
    return False


def principle_limit_present(text: str) -> bool:
    """El límite del PRINCIPIO: no aumenta las justificaciones que los agentes
    deben producir.

    Se mide sobre el texto NORMALIZADO (los espacios colapsados): el concepto
    se reconoce aunque la frase esté partida en varias líneas.
    """
    haystack = normalized(text)
    for match in JUSTIFICATION.finditer(haystack):
        low, high = _window(haystack, match.start(), 500)
        if INCREASE_NEGATION.search(haystack, low, high):
            return True
    return False


def alignment_check_present(text: str) -> bool:
    """(a) alineación: cada fila apunta a un archivo que existe en `docs/adr/`."""
    for match in DOCS_ADR.finditer(text):
        low, high = _window(text, match.start(), NEAR_TIGHT)
        if ROW.search(text, low, high) and ALIGNMENT.search(text, low, high):
            return True
    return False


def respect_check_present(text: str) -> bool:
    """(b) respeto: el cambio respeta las decisiones vigentes de su rol."""
    for match in DECISION.finditer(text):
        low, high = _window(text, match.start(), NEAR_TIGHT)
        if CURRENT.search(text, low, high) and RESPECT.search(text, low, high):
            return True
    return False


def skill_reference_row(text: str) -> bool:
    """La tabla «How to read the references» tiene una fila para el archivo
    nuevo (la primera celda de la fila lo nombra)."""
    lines = text.splitlines()
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            inside = "how to read the references" in stripped.lower()
            continue
        if not inside or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
        if not cells:
            continue
        if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
            continue
        if POINTER in cells[0]:
            return True
    return False


# ---------------------------------------------------------------------------
# La copia descartable del repo (nunca el árbol de trabajo, nunca el HOME)
# ---------------------------------------------------------------------------

_IGNORED_NAMES = frozenset(
    {
        ".git",
        ".cdad",
        "build",
        "__pycache__",
        ".pytest_cache",
        "logs",
        ".opencode",
        ".sensitive-patterns.local",
    }
)


def _ignore(_dirname: str, names: list[str]) -> set[str]:
    return {name for name in names if name in _IGNORED_NAMES}


def _temp_root() -> Path:
    preferred = Path("/tmp/opencode")
    if preferred.is_dir():
        return preferred
    return Path(tempfile.gettempdir())


_DISPOSABLE: dict[str, object] = {}


def disposable_product() -> dict[str, object]:
    """Copia descartable del repo + HOME descartable, con ``make agents``.

    La generación se invoca SIEMPRE dentro de la copia: el árbol de trabajo no
    se regenera nunca y el HOME real no se toca nunca.
    """
    if "product" in _DISPOSABLE:
        return _DISPOSABLE
    base = Path(tempfile.mkdtemp(prefix="cdad-006-004-u3-", dir=str(_temp_root())))
    atexit.register(shutil.rmtree, base, ignore_errors=True)
    product = base / "product"
    shutil.copytree(REPO_ROOT, product, symlinks=True, ignore=_ignore)
    home = base / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["XDG_CONFIG_HOME"] = str(home / ".config")
    run = subprocess.run(
        ["make", "agents"],
        cwd=str(product),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    _DISPOSABLE.update({"product": product, "home": home, "env": env, "run": run})
    return _DISPOSABLE


def staging_digests(product: Path, env: dict[str, str]) -> dict[str, str]:
    """Una corrida de `make staging` en la copia + el sha256 de los agentes
    generados de los dos roles que U3 toca."""
    run = subprocess.run(
        ["make", "staging"],
        cwd=str(product),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if run.returncode != 0:
        raise AssertionError(
            "`make staging` falló en la copia descartable (rc="
            f"{run.returncode}):\n{run.stdout}\n{run.stderr}"
        )
    staging = product / "build" / "staging"
    digests: dict[str, str] = {}
    for relpath in STAGED_AGENTS:
        path = staging / relpath
        if not path.is_file():
            raise AssertionError(
                f"`make staging` no publicó el agente declarado {relpath} en la "
                "copia descartable."
            )
        digests[relpath] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


# ---------------------------------------------------------------------------
# PD-10 / INV-1 / INV-12 — la casa canónica y la unicidad
# ---------------------------------------------------------------------------


class TestPd10CanonicalHouse(unittest.TestCase):
    """PD-10 / INV-1: el principio y su límite viven en UN archivo."""

    maxDiff = None

    def test_pd10_the_canonical_file_exists_and_carries_the_principle_and_its_limit(
        self,
    ) -> None:
        """PD-10: la casa canónica existe y lleva el principio **y** su límite.

        La casa es ``skills/cdad-cycle/references/design-principles.md`` (el
        archivo nuevo de la ficha U3): una sección que nombra el principio
        (general / specific), el texto normativo que lo enuncia y el LÍMITE del
        principio (mejora el juicio de diseño y NO aumenta las justificaciones
        que los agentes deben producir).
        """
        text = read_document(CANONICAL, "PD-10: la casa canónica del principio")
        section = canonical_section(text)
        self.assertIsNotNone(
            section,
            "PD-10: la casa canónica no tiene una sección que nombre el "
            "principio (general / specific): el archivo debe llevar una "
            "sección «General before specific» con el texto del principio y su "
            f"límite. Contenido:\n{text[:1200]!r}",
        )
        heading, body = section  # type: ignore[misc]
        self.assertTrue(
            GENERAL.search(heading) and SPECIFIC.search(heading),
            f"PD-10: el encabezado de la sección no nombra el principio: {heading!r}",
        )
        units = principle_units(body)
        self.assertTrue(
            units,
            "PD-10: la sección de la casa canónica no enuncia el principio de "
            "forma normativa (una frase que nombre general y specific) ni su "
            f"límite. Encabezado: {heading!r}. Cuerpo:\n{body[:1500]!r}",
        )
        self.assertTrue(
            principle_limit_present(body),
            "PD-10: la casa canónica no lleva el LÍMITE del principio (que no "
            "aumenta las justificaciones que los agentes deben producir). "
            f"Cuerpo:\n{body[:1500]!r}",
        )

    def test_pd10_the_normative_text_of_the_principle_lives_in_exactly_one_installable_file(
        self,
    ) -> None:
        """PD-10 / INV-1: el texto normativo aparece en UN único archivo.

        El texto normativo se DERIVA de la casa canónica (no lo dicta este
        RED) y después se busca, en todo el árbol instalable (``skills/``,
        ``sources/``, ``agents/``), como un ``grep -rl``: el resultado tiene que
        ser exactamente la casa canónica.
        """
        text = read_document(CANONICAL, "PD-10/INV-1: la casa canónica del principio")
        section = canonical_section(text)
        self.assertIsNotNone(
            section,
            "PD-10/INV-1: sin la casa canónica no hay texto normativo que "
            "derivar: falta la sección que nombra el principio.",
        )
        _heading, body = section  # type: ignore[misc]
        units = principle_units(body)
        self.assertTrue(
            units,
            "PD-10/INV-1: la casa canónica no enuncia el principio de forma "
            "normativa: no hay texto cuya unicidad se pueda medir.",
        )
        documents = installable_documents()
        self.assertGreater(
            len(documents),
            0,
            "drift del oráculo PD-10/INV-1: no se recolectó ningún archivo del "
            "árbol instalable.",
        )
        offenders = copies_of(units, documents)
        offending_files = sorted({relpath for relpath, _needle in offenders})
        self.assertEqual(
            offending_files,
            [CANONICAL_RELPATH],
            "PD-10/INV-1: el texto normativo del principio debe vivir en UN "
            "único archivo del árbol instalable (la casa canónica); lo "
            f"reproduce(n): {offenders[:10]!r}",
        )

    def test_pd10_no_installable_surface_copies_the_principle_text(self) -> None:
        """PD-10 / INV-12: ninguna superficie copia el texto del principio.

        Control NEGATIVO declarado: las fuentes de rol, sus bloques estáticos y
        los agentes generados **referencian** al dueño canónico; no **copian**
        su texto. El detector se autocomprueba (control de vacuidad): con una
        copia sintética debe marcar el.ofensor, y sin ella no.
        """
        text = read_document(CANONICAL, "PD-10/INV-12: la casa canónica del principio")
        section = canonical_section(text)
        self.assertIsNotNone(
            section,
            "PD-10/INV-12: el control negativo necesita el texto canónico: "
            "falta la casa del principio.",
        )
        _heading, body = section  # type: ignore[misc]
        units = principle_units(body)
        self.assertTrue(
            units,
            "PD-10/INV-12: el control negativo necesita el texto canónico: la "
            "casa no enuncia el principio de forma normativa.",
        )
        needle = units[0]
        probe = " ".join(needle.split()[: max(4, len(needle.split()) // 2)])
        self.assertTrue(
            copies_of([probe], [("sintetico.md", "otra cosa")]) == [],
            "control de vacuidad roto: el detector marca un texto que NO "
            "contiene la frase.",
        )
        self.assertTrue(
            copies_of([probe], [("sintetico.md", "prefijo " + probe + " sufijo")]),
            "control de vacuidad roto: el detector NO detecta una copia "
            "sintética del texto canónico (ni siquiera re-ajustada).",
        )
        documents = installable_documents()
        offenders = copies_of(units, documents)
        offending_files = sorted({relpath for relpath, _needle in offenders})
        self.assertEqual(
            offending_files,
            [CANONICAL_RELPATH],
            "PD-10/INV-12: una superficie del árbol instalable copia el texto "
            f"del principio: {offenders[:10]!r}",
        )


# ---------------------------------------------------------------------------
# PD-10 — las dos obligaciones (el architect y el reviewer)
# ---------------------------------------------------------------------------


class TestPd10ArchitectDuty(unittest.TestCase):
    """PD-10 / D-2: la obligación del architect vive en su fuente y en su
    bloque estático, y apunta al dueño canónico."""

    maxDiff = None

    def test_pd10_the_architect_source_names_its_duty_and_points_to_the_canonical_owner(
        self,
    ) -> None:
        """PD-10: la fuente del architect nombra su obligación y apunta al
        dueño canónico.

        La obligación: en las decisiones relevantes, considerar las
        alternativas generales y específicas y explicar el criterio elegido.
        El puntero: el nombre del archivo canónico.
        """
        text = read_document(ARCHITECT_SOURCE, "PD-10: sources/roles/architect.md")
        self.assertTrue(
            names_pointer(text),
            "PD-10: la fuente del architect no apunta al dueño canónico del "
            f"principio (falta `{POINTER}`).",
        )
        self.assertTrue(
            architect_duty_present(text),
            "PD-10: la fuente del architect no nombra su obligación (considerar "
            "las alternativas generales y específicas y explicar el criterio "
            "elegido): no se encontró la redacción de ese deber.",
        )

    def test_pd10_the_architect_static_block_carries_the_duty_and_the_pointer(
        self,
    ) -> None:
        """PD-10 / D-2: el bloque estático del architect lleva la obligación
        mínima y el puntero.

        En la ruta de paquete el rol NO carga el skill ⇒ el puntero solo no es
        resoluble: el bloque estático lleva la obligación operativa.
        """
        text = read_document(
            ARCHITECT_BLOCK, "PD-10/D-2: packets/roles/architect.md"
        )
        self.assertTrue(
            names_pointer(text),
            "PD-10/D-2: el bloque estático del architect no apunta al dueño "
            f"canónico del principio (falta `{POINTER}`).",
        )
        self.assertTrue(
            architect_duty_minimum_present(text),
            "PD-10/D-2: el bloque estático del architect no lleva la obligación "
            "mínima (general, specific y el criterio explicado).",
        )


class TestPd10ReviewerCriterion(unittest.TestCase):
    """PD-10 / D-2: el criterio del reviewer vive en su fuente y en su bloque
    estático (con el límite en las dos superficies), y apunta al dueño
    canónico."""

    maxDiff = None

    def test_pd10_the_reviewer_source_names_its_duty_and_points_to_the_canonical_owner(
        self,
    ) -> None:
        """PD-10: la fuente del reviewer nombra su deber y apunta al dueño
        canónico."""
        text = read_document(REVIEWER_SOURCE, "PD-10: sources/roles/reviewer.md")
        self.assertTrue(
            names_pointer(text),
            "PD-10: la fuente del reviewer no apunta al dueño canónico del "
            f"principio (falta `{POINTER}`).",
        )

    def test_pd10_the_reviewer_static_block_carries_the_limit_and_the_pointer(
        self,
    ) -> None:
        """PD-10 / D-2: el bloque estático del reviewer lleva el LÍMITE y el
        puntero.

        El límite (la falta de una abstracción, por sí sola, no es un defecto)
        está en las DOS superficies del reviewer (PD-10).
        """
        text = read_document(REVIEWER_BLOCK, "PD-10/D-2: packets/roles/reviewer.md")
        self.assertTrue(
            names_pointer(text),
            "PD-10/D-2: el bloque estático del reviewer no apunta al dueño "
            f"canónico del principio (falta `{POINTER}`).",
        )
        self.assertTrue(
            reviewer_limit_present(text),
            "PD-10/D-2: el bloque estático del reviewer no lleva el LÍMITE (la "
            "falta de una abstracción, por sí sola, no es un defecto).",
        )

    def test_pd10_the_reviewer_criterion_names_the_four_consequences_and_the_limit(
        self,
    ) -> None:
        """PD-10: el criterio del reviewer nombra las CUATRO consecuencias
        reales y su límite.

        Consecuencias: duplicación que puede divergir, complejidad
        innecesaria, pérdida de capacidades y acoplamiento. Límite: la falta de
        una abstracción, por sí sola, no es un defecto. El LÍMITE está en las
        dos superficies del reviewer; las cuatro consecuencias, en su fuente.
        """
        source = read_document(REVIEWER_SOURCE, "PD-10: sources/roles/reviewer.md")
        block = read_document(REVIEWER_BLOCK, "PD-10/D-2: packets/roles/reviewer.md")
        self.assertTrue(
            four_consequences_present(source),
            "PD-10: la fuente del reviewer no nombra las cuatro consecuencias "
            "reales del criterio (duplicación que puede divergir, complejidad "
            "innecesaria, pérdida de capacidades y acoplamiento).",
        )
        self.assertTrue(
            reviewer_limit_present(source),
            "PD-10: la fuente del reviewer no lleva el LÍMITE (la falta de una "
            "abstracción, por sí sola, no es un defecto).",
        )
        self.assertTrue(
            reviewer_limit_present(block),
            "PD-10: el bloque estático del reviewer no lleva el LÍMITE (la "
            "falta de una abstracción, por sí sola, no es un defecto): el límite "
            "está en las dos superficies del reviewer.",
        )


# ---------------------------------------------------------------------------
# PD-8 — el deber del reviewer sobre la tabla (dueño canónico)
# ---------------------------------------------------------------------------


class TestPd8ReviewerDutyOverTheTable(unittest.TestCase):
    """PD-8: ``references/stage-4-review.md`` nombra las dos comprobaciones
    del deber del reviewer sobre la tabla."""

    maxDiff = None

    def test_pd8_stage4_review_names_the_alignment_check_against_docs_adr(self) -> None:
        """PD-8 (a): la alineación — cada fila apunta a un archivo que existe
        en ``docs/adr/`` (y el contraste entre el conjunto de filas y el
        directorio)."""
        text = read_document(
            STAGE4_REVIEW, "PD-8: skills/cdad-cycle/references/stage-4-review.md"
        )
        self.assertTrue(
            alignment_check_present(text),
            "PD-8: `references/stage-4-review.md` no nombra la comprobación de "
            "ALINEACIÓN del deber del reviewer sobre la tabla (cada fila "
            "apunta a un archivo que existe en `docs/adr/`).",
        )

    def test_pd8_stage4_review_names_the_respect_check_for_the_role_decisions(
        self,
    ) -> None:
        """PD-8 (b): el respeto — el cambio respeta las decisiones vigentes de
        su rol."""
        text = read_document(
            STAGE4_REVIEW, "PD-8: skills/cdad-cycle/references/stage-4-review.md"
        )
        self.assertTrue(
            respect_check_present(text),
            "PD-8: `references/stage-4-review.md` no nombra la comprobación de "
            "RESPETO del deber del reviewer sobre la tabla (el cambio respeta "
            "las decisiones vigentes de su rol).",
        )


# ---------------------------------------------------------------------------
# PD-10 — la fila de referencias de SKILL.md
# ---------------------------------------------------------------------------


class TestPd10SkillReferenceRow(unittest.TestCase):
    """PD-10: ``SKILL.md`` tiene la fila del archivo nuevo en la tabla de
    referencias."""

    maxDiff = None

    def test_pd10_skill_md_references_table_has_the_row_of_the_new_file(self) -> None:
        """PD-10: la tabla «How to read the references» de ``SKILL.md`` tiene una
        fila para el archivo nuevo (la que dice cuándo cargarlo)."""
        text = read_document(SKILL_MD, "PD-10: skills/cdad-cycle/SKILL.md")
        self.assertTrue(
            skill_reference_row(text),
            "PD-10: `SKILL.md` no tiene la fila del archivo nuevo en la tabla "
            f"«How to read the references» (falta una fila que nombre `{POINTER}`).",
        )


# ---------------------------------------------------------------------------
# PD-13 / V-2 — los agentes generados y el determinismo
# ---------------------------------------------------------------------------


class TestPd13GeneratedAgents(unittest.TestCase):
    """PD-13: los agentes generados llevan el texto tras ``make agents`` y
    ``make staging`` es determinista."""

    maxDiff = None

    def test_pd13_the_generated_agents_carry_the_duty_after_make_agents(self) -> None:
        """PD-13: los agentes GENERADOS llevan la obligación y el puntero.

        El generador se invoca como PROCESO en la COPIA DESCARTABLE del repo
        (``make agents``: nunca el árbol de trabajo ni el HOME real).
        """
        disposable = disposable_product()
        run = disposable["run"]
        assert isinstance(run, subprocess.CompletedProcess)
        self.assertEqual(
            run.returncode,
            0,
            "`make agents` falló en la copia descartable (rc="
            f"{run.returncode}):\n{run.stdout}\n{run.stderr}",
        )
        product = disposable["product"]
        assert isinstance(product, Path)
        for relpath in STAGED_AGENTS:
            with self.subTest(agent=relpath):
                path = product / "build" / "staging" / relpath
                self.assertTrue(
                    path.is_file(),
                    f"PD-13: `make agents` no publicó el agente {relpath} en la "
                    "copia descartable.",
                )
                text = path.read_text(encoding="utf-8")
                label = f"PD-13: agente generado {relpath}"
                self.assertTrue(
                    names_pointer(text),
                    f"{label}: el agente no apunta al dueño canónico del "
                    f"principio (falta `{POINTER}`).",
                )
                if "architect" in relpath:
                    self.assertTrue(
                        architect_duty_minimum_present(text),
                        f"{label}: el agente no lleva la obligación del architect "
                        "(general, specific y el criterio explicado).",
                    )
                else:
                    self.assertTrue(
                        reviewer_limit_present(text),
                        f"{label}: el agente no lleva el LÍMITE del criterio del "
                        "reviewer (la falta de una abstracción, por sí sola, no "
                        "es un defecto).",
                    )

    def test_pd13_the_promoted_agents_of_the_repo_carry_the_duty(self) -> None:
        """PD-13: los agentes PROMOVIDOS en el repo llevan la obligación y el
        puntero.

        Son salidas declaradas de ``scripts/cdad-generate.py`` (se promovieron
        con ``make agents``): se leen, no se editan a mano.
        """
        for relpath in PROMOTED_AGENTS:
            with self.subTest(agent=relpath):
                path = REPO_ROOT / relpath
                self.assertTrue(
                    path.is_file(),
                    f"PD-13: falta el agente promovido {relpath}.",
                )
                text = path.read_text(encoding="utf-8")
                label = f"PD-13: agente promovido {relpath}"
                self.assertTrue(
                    names_pointer(text),
                    f"{label}: el agente no apunta al dueño canónico del "
                    f"principio (falta `{POINTER}`): hay que correr `make agents`.",
                )
                if "architect" in relpath:
                    self.assertTrue(
                        architect_duty_minimum_present(text),
                        f"{label}: el agente no lleva la obligación del architect.",
                    )
                else:
                    self.assertTrue(
                        reviewer_limit_present(text),
                        f"{label}: el agente no lleva el LÍMITE del criterio del "
                        "reviewer.",
                    )

    def test_pd13_make_staging_is_deterministic_across_two_runs(self) -> None:
        """PD-13 / V-2 (CONTROL): ``make staging`` es determinista.

        Dos corridas sobre las mismas fuentes producen los mismos bytes. Verde
        hoy: es la guarda de que el cambio de las fuentes de rol no rompe el
        determinismo del generador.
        """
        disposable = disposable_product()
        product = disposable["product"]
        env = disposable["env"]
        assert isinstance(product, Path)
        assert isinstance(env, dict)
        first = staging_digests(product, env)
        second = staging_digests(product, env)
        self.assertEqual(
            first,
            second,
            "PD-13/V-2: `make staging` no es determinista: dos corridas sobre "
            "las mismas fuentes produjeron bytes distintos.\n"
            f"primera: {first}\nsegunda: {second}",
        )


# ---------------------------------------------------------------------------
# PD-13 / V-4 — el techo del bloque estático
# ---------------------------------------------------------------------------


class TestPd13StaticBlockCeiling(unittest.TestCase):
    """PD-13 / V-4: el bloque estático de los 14 pares rol/subfase se mide y
    queda bajo el techo declarado de 12000 bytes."""

    maxDiff = None

    def _composed_static_block(self, role: str, substage: str) -> bytes:
        """El bloque estático que compone el producto: `common.md` + la fuente
        del rol + la de la subfase, unidos por un salto de línea."""
        parts = [
            (PACKETS_ROOT / "common.md").read_bytes(),
            (PACKETS_ROOT / "roles" / f"{role}.md").read_bytes(),
            (PACKETS_ROOT / "substages" / f"{role}-{substage}.md").read_bytes(),
        ]
        return b"\n".join(parts)

    def test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling(
        self,
    ) -> None:
        """PD-13 / V-4 (CONTROL): los 14 pares rol/subfase, medidos, bajo el
        techo de 12000 bytes.

        La medición se ancla en el PRODUCTO: para dos pares se renderiza el
        paquete con el CLI público y se comprueba que el bloque estático
        renderizado son EXACTAMENTE los bytes medidos aquí.
        """
        measured: dict[str, int] = {}
        for role, substage in ROLE_SUBSTAGE_PAIRS:
            measured[f"{role}/{substage}"] = len(self._composed_static_block(role, substage))
        self.assertEqual(
            len(measured),
            14,
            "drift del oráculo PD-13/V-4: se esperaban 14 pares rol/subfase y "
            f"se midieron {len(measured)}.",
        )

        for role, substage in (("architect", "discovery"), ("reviewer", "review")):
            with self.subTest(anchor=f"{role}/{substage}"):
                with tempfile.TemporaryDirectory(prefix="cdad-u3-anchor-") as tmp:
                    fixture = PacketFixture(Path(tmp), role, substage)
                    fixture.write()
                    rendered = fixture.render()
                    self.assertEqual(
                        rendered.returncode,
                        0,
                        f"PD-13/V-4: el render del par {role}/{substage} falló: "
                        f"{rendered.stderr}",
                    )
                    self.assertEqual(
                        static_instruction_bytes(rendered.stdout),
                        self._composed_static_block(role, substage),
                        f"PD-13/V-4: la medición del bloque estático de "
                        f"{role}/{substage} no es la del producto: el bloque "
                        "renderizado difiere de los bytes medidos.",
                    )

        worst = max(measured.values())
        worst_pair = max(measured, key=lambda key: measured[key])
        print(
            "PD-13/V-4: bloque estático de los 14 pares rol/subfase — máximo "
            f"{worst} bytes ({worst_pair}), techo declarado {STATIC_CEILING} bytes; "
            f"medición completa: {measured}"
        )
        for pair, size in sorted(measured.items(), key=lambda item: item[1], reverse=True):
            self.assertLessEqual(
                size,
                STATIC_CEILING,
                f"PD-13/V-4: el bloque estático del par {pair} mide {size} "
                f"bytes y supera el techo declarado de {STATIC_CEILING} bytes "
                "(la respuesta NO es subir el techo).",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
