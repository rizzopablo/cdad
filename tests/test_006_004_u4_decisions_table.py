#!/usr/bin/env python3
"""006-004 U4 RED — la tabla de decisiones: la plantilla, su upkeep y la regla del CAS.

Contrato:
- ``docs/specs/006-004-active-decisions-table/spec.md`` (aprobada 2026-10-20)
  §2.5 (la tabla del proyecto: plantilla, upkeep y las dos responsabilidades),
  §3 **PD-7** (la plantilla trae la sección), §3 **PD-8** (las dos
  responsabilidades están escritas donde se aplican), §3 **PD-9** (el CAS se
  hace contra el digest base y la reconciliación es un re-despacho), §4
  **INV-13** (el CAS es contra la base y reconciliar es re-despachar), §5
  **DEC-13** (la regla general del CAS, dictada general antes que específica) y
  §5 **DEC-14** (U4 = plantilla y procedimiento; la siembra es de U5/U7).
- ``docs/specs/006-004-active-decisions-table/plan.md`` §3 **ficha U4** (archivos,
  RED, regresiones, A-1, gate) y su bloque ``plan-tasks`` (los
  ``observable_checks`` de U4, que son el contrato operativo de este RED).

Superficie observable bajo prueba (caja negra: sólo TEXTO publicado y
PROCESOS REALES; la implementación NUNCA se lee, NUNCA se importa):

- ``skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`` — la
  plantilla del Memory Bank (la sección que instala el bootstrap);
- ``skills/cdad-cycle/references/stage-5-merge.md`` — el procedimiento del
  orquestador en el cierre (§5.4: el upkeep) y el **exit gate** (que NO
  cambia);
- ``skills/cdad-cycle/references/re-entry.md`` — el protocolo de materialización
  (paso 3 MATERIALIZE: la regla general del CAS) y la sección ``### Scribe``
  (el caso particular de la tabla);
- ``tests/validate-consistency.sh`` — el **bloque de texto** de esta unidad (la
  plantilla y las dos referencias), ejecutado como PROCESO REAL sobre el árbol
  y sobre copias DESCARTABLES (nunca el HOME, nunca el árbol de trabajo).

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
la spec §2.5 y la ficha U4 fijan el contrato y dejan la redacción dentro):

1. **La plantilla** lleva la sección de las decisiones vigentes como **primer
   H2** (después de la introducción). El título concreto es libre (spec §2.5,
   Q5: el producto no parsea el documento); se aceptan las dos redacciones
   declaradas (``Current decisions`` / ``Decisiones vigentes``).
2. **La sección declara la forma de la fila** (archivo · estado · resumen de una
   línea · roles · referencia) y **la nota** que declara las exclusiones y que
   **el estado lo declara quien mantiene la tabla** (no se re-deriva).
3. **El upkeep** vive en **§5.4** de ``stage-5-merge.md``: al **aprobarse un
   ADR** el orquestador **agrega la fila** y **marca la anterior como
   obsoleta**.
4. **La regla general del CAS** vive en el **paso 3 (MATERIALIZE)** de
   ``re-entry.md``: el digest declarado es **siempre el digest base** (la
   versión del destino sobre la que se preparó la propuesta), **nunca** el
   actual; ante un conflicto, la vía es **re-despachar** al rol con un paquete
   nuevo **sobre la base nueva**; **no** se fusiona a mano ni se **actualiza el
   digest esperado** para forzar el paso.
5. **El caso de la tabla** vive en la sección ``### Scribe`` de la misma
   referencia: hay **dos escritores**; el **orquestador escribe sus propias
   filas directamente en ``docs/``** con su commit; la del scribe llega por
   **materialización**.
6. **El exit gate de stage 5 NO cambia** (control negativo): conserva el
   mismo número de casillas y ninguna se refiere a la tabla de decisiones.
7. **El bloque de texto** de esta unidad vive en ``tests/validate-consistency.sh``
   y **pasa**; y **NO exige** la tabla viva ni el ADR-034 (B-1): el gate de U4
   no puede depender de documentos de una unidad pendiente (DEC-14).

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica):

- La derivación es **por CONCEPTO** (vocabulario con alternativas de idioma),
  **no por frase exacta**: la redacción es libre; el concepto no. Sólo se exige
  **verbatim** lo que la ficha cita verbatim (los nombres de archivo).
- El RED **no** mira la tabla viva (``docs/systemPatterns.md``) ni el
  directorio de ADR: son la superficie de U5/U7 (plan §1.1, DEC-14). El único
  contacto con ellos es **negativo**: el bloque no debe exigirlos.
- El RED **no** exige el **exit gate** con casillas nuevas: lo exige **igual**
  (control negativo).
- El RED **no** congela el texto de la regla del CAS: deriva los **cinco**
  conceptos que la ficha nombra (digest base · nunca el actual · re-despacho
  con paquete nuevo sobre la base nueva · sin fusión a mano · sin actualizar el
  digest esperado).
- El RED **no** toca ningún archivo de ``tests/`` ajeno a este ni al bloque de
  texto de la unidad (que es suyo: vive en ``tests/``).

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** El conjunto cerrado del request se **extiende** con una propiedad
declarada; la forma de las secciones del paquete se comprueba **por
presencia**; ningún test fija un digest literal de una fuente de instrucción;
**el exit gate de stage 5 no cambia**; la subfase del reviewer no se toca; los
agentes son salidas declaradas y ``make agents`` los regenera. Este RED
**vuelve a comprobar** los controles negativos (el exit gate intacto, el bloque
que no exige la semilla) y **sólo añade casos**: no modifica, no sustituye y
no invisibiliza ninguna prueba vigente. El RED de U4 no toca ningún archivo de
``tests/`` ajeno a este.

RED esperado contra el árbol vigente (OBSERVADO; declarado, no accidental):

- Fallan por ``AssertionError`` de CONTRATO las comprobaciones de contenido:
  la plantilla no tiene la sección (ni la forma de la fila ni la nota),
  ``stage-5-merge.md`` §5.4 no nombra el upkeep, ``re-entry.md`` paso 3 no
  declara la regla general del CAS y su sección ``### Scribe`` no declara el
  caso de la tabla, y el bloque de texto de la unidad (que exige esas tres
  superficies) **falla**.
- **Pasan hoy** los tres **controles**: el exit gate conserva sus casillas, el
  bloque **no** exige la tabla viva ni el ADR-034, y el bloque se comporta
  **igual** con y sin la semilla (es decir: su resultado no depende de ella).
- Ningún fallo es ImportError, SyntaxError, NameError ni error de fixture: los
  artefactos requeridos que faltan se reportan con ``self.fail``/``assert`` y
  su mensaje contractual.

CONSECUENCIA DECLARADA DEL BLOQUE DE TEXTO (no oculta): el bloque de esta
unidad vive en ``tests/validate-consistency.sh`` (el plan §3 ficha U4 lo
declara como archivo de la unidad, y su RED lo incluye), de modo que
``make validate`` queda **rojo durante el RED** — seis asserts nuevos, los de
la unidad — y vuelve a verde cuando el GREEN escribe las tres superficies.
Efecto colateral **medido**: la prueba de puerta verde de una unidad cerrada
(``tests/test_006_003_u8_acceptance.py``, PD-8b: «``make validate`` pasa») queda
roja mientras falte la implementación; **no** se toca ni se sustituye esa
prueba, y su oráculo («el validador pasa») **no** cambia. En el entorno del
dueño el validador arrastra además un fallo **preexistente** y ajeno a esta
unidad (F011: la deriva entre el árbol instalado y el repositorio).

Mapeo test → postcondición (un test por aserción observable; las filas 3, 8 y 9
son controles declarados):

  1  ``TestPd7TemplateSection::test_pd7_the_template_carries_the_decisions_section_as_its_first_h2``   PD-7
  2  ``TestPd7TemplateSection::test_pd7_the_section_of_the_template_carries_the_row_shape_and_the_note``   PD-7
  3  ``TestPd7ExitGateControl::test_pd7_the_exit_gate_of_stage_5_did_not_gain_checkboxes``   PD-7 / PD-8 (CONTROL)
  4  ``TestPd8Upkeep::test_pd8_stage5_merge_names_the_upkeep_of_the_table``   PD-8
  5  ``TestPd9CasRule::test_pd9_reentry_step3_declares_the_general_cas_by_base_rule``   PD-9 / DEC-13
  6  ``TestPd9CasRule::test_pd9_reentry_scribe_section_declares_the_case_of_the_table``   PD-8 / PD-9
  7  ``TestU4TextBlock::test_pd7_pd8_pd9_the_text_block_of_u4_passes_on_the_tree``   PD-7 / PD-8 / PD-9
  8  ``TestU4TextBlock::test_pd7_pd8_pd9_the_text_block_of_u4_does_not_require_the_live_table_nor_adr_034``   B-1 (CONTROL)
  9  ``TestU4TextBlock::test_pd7_pd8_pd9_the_text_block_of_u4_behaves_the_same_without_the_seed``   B-1 (CONTROL)
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Superficies (rutas relativas al repo; ninguna ruta del host)
# ---------------------------------------------------------------------------

TEMPLATE = REPO_ROOT / "skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md"
STAGE5 = REPO_ROOT / "skills/cdad-cycle/references/stage-5-merge.md"
REENTRY = REPO_ROOT / "skills/cdad-cycle/references/re-entry.md"
VALIDATOR = REPO_ROOT / "tests/validate-consistency.sh"

# El bloque de texto de esta unidad dentro del validador (marcadores).
BLOCK_BEGIN = "# BEGIN 006-004 U4"
BLOCK_END = "# END 006-004 U4"

# El exit gate de stage 5 conserva el MISMO número de casillas (Q6): el número
# está MEDIDO hoy, sobre el árbol previo a la feature (7 casillas). El control
# negativo es "no ganó casillas", no "no cambió de texto".
EXIT_GATE_CHECKBOXES = 7

# Lo que el bloque copiado a los árboles descartables necesita del árbol
# instalable (nada del directorio de scripts: el RED no lo ve).
COPIED_SKILL_PATHS = (
    "skills/cdad-cycle/SKILL.md",
    "skills/cdad-cycle/assets",
    "skills/cdad-cycle/references",
    "skills/cdad-cycle/packets",
)

# ---------------------------------------------------------------------------
# Conceptos (derivación textual por CONCEPTO; la redacción es libre)
# ---------------------------------------------------------------------------

# El título de la sección: libre (Q5), pero el RED acepta las dos redacciones
# declaradas por la spec/plan (inglés en la plantilla, español en la instancia
# viva de este repo).
DECISIONS_SECTION = re.compile(r"current\s+decisions|decisiones\s+vigentes", re.IGNORECASE)

# El exit gate (encabezado de nivel 2 de stage-5-merge.md).
EXIT_GATE_HEADING = re.compile(r"exit gate", re.IGNORECASE)

# §5.4 — la decisión sobre el ADR (encabezado de nivel 2).
ADR_DECISION_HEADING = re.compile(r"^5\.4")

# La sección `### Scribe` de re-entry.md (encabezado de nivel 3).
SCRIBE_HEADING = re.compile(r"^scribe", re.IGNORECASE)

# --- PD-7: la forma de la fila y la nota -----------------------------------
REQ_PD7_SHAPE = (
    ("the file of the decision", r"file|archivo|ruta|path"),
    ("the state of the decision", r"state|estado|vigente|obsoleto"),
    ("the one-line summary", r"summary|resumen"),
    ("the roles that must consume it", r"roles|consumers|consumidores|who consumes"),
    ("the reference where the rule lives", r"reference|referencia"),
)

REQ_PD7_NOTE = (
    (
        "the exclusions of the table",
        r"exclud[a-z]*|excluid[a-z]*|proposed|propuesto|pending|not (?:yet )?in force|still pending",
    ),
    (
        "that the state is declared by whoever maintains the table",
        r"(?:declar[a-z]*[^.]{0,60}state|state[^.]{0,60}declar[a-z]*|declara(?:ndo)? el estado|estado[^.]{0,60}declar[a-z]*)"
        r"[^.]{0,300}(?:maintain[a-z]*|mantien[a-z]*|quien mantiene|who maintains)"
        r"|(?:maintain[a-z]*|mantien[a-z]*|quien mantiene|who maintains)"
        r"[^.]{0,300}(?:declar[a-z]*[^.]{0,60}state|state[^.]{0,60}declar[a-z]*|declara(?:ndo)? el estado|estado[^.]{0,60}declar[a-z]*)",
    ),
)

# --- PD-8: el upkeep, en §5.4 ----------------------------------------------
REQ_PD8_UPKEEP = (
    (
        "the approval of an ADR",
        r"(?:adr|decision record)[^.]{0,300}(?:approv[a-z]*|aprob[a-z]*)"
        r"|(?:approv[a-z]*|aprob[a-z]*)[^.]{0,300}(?:adr|decision record)",
    ),
    (
        "adding the row of the approved decision",
        r"(?:add[a-z]*|agrega[a-z]*|append[a-z]*|insert[a-z]*|añad[a-z]*|agreg[a-z]*)[^.]{0,200}(?:row|fila)"
        r"|(?:row|fila)[^.]{0,200}(?:add[a-z]*|agrega[a-z]*|append[a-z]*|insert[a-z]*|añad[a-z]*|agreg[a-z]*)",
    ),
    (
        "marking the previous row as obsolete",
        r"(?:mark[a-z]*|marc[a-z]*|set[a-z]*|pon[a-z]*|declara[a-z]*|pas[a-z]*)[^.]{0,250}"
        r"(?:obsolet[a-z]*|obsoleto|deprecat[a-z]*)"
        r"|(?:obsolet[a-z]*|obsoleto|deprecat[a-z]*)[^.]{0,250}"
        r"(?:mark[a-z]*|marc[a-z]*|set[a-z]*|pon[a-z]*|declara[a-z]*|pas[a-z]*)",
    ),
    (
        "the previous row (the one that is replaced)",
        r"\bprevious\b|\banterior\b|precedent|\bold\b|replaced|reemplaz[a-z]*|superseded",
    ),
)

# --- PD-9: la regla general del CAS, en el paso 3 (MATERIALIZE) ------------
REQ_PD9_CAS = (
    (
        "the BASE digest (the version the proposal was prepared on)",
        r"\bbase\b[^.]{0,250}(?:digest|sha256|version|target)"
        r"|(?:digest|sha256|version|target)[^.]{0,250}\bbase\b",
    ),
    (
        "never the CURRENT digest",
        r"(?:never|not|no|nunca|jamás|sin)\b[^.]{0,250}(?:current|actual)\b[^.]{0,250}(?:digest|sha256)"
        r"|(?:never|not|no|nunca|jamás|sin)\b[^.]{0,250}(?:digest|sha256)\b[^.]{0,250}(?:current|actual)\b",
    ),
    (
        "re-dispatch the role with a NEW packet",
        r"re-?dispatch[a-z]*|re-?despach[a-z]*|new (?:packet|package|dispatch)|paquete nuevo|nuevo paquete",
    ),
    (
        "on the NEW base",
        r"(?:new|nueva|nuevo)\b[^.]{0,120}\bbase\b|\bbase\b[^.]{0,120}(?:new|nueva|nuevo)",
    ),
    (
        "no manual merge",
        r"(?:never|not|no|nunca|jamás|sin)\b[^.]{0,250}(?:merg[a-z]*|fusi[oó]n|mergear)[^.]{0,250}"
        r"(?:by hand|a mano|manually|manual)"
        r"|(?:never|not|no|nunca|jamás|sin)\b[^.]{0,250}(?:by hand|a mano|manually|manual)[^.]{0,250}"
        r"(?:merg[a-z]*|fusi[oó]n|mergear)",
    ),
    (
        "no updating the expected digest to force the step",
        r"(?:never|not|no|nunca|jamás|sin)\b[^.]{0,200}"
        r"(?:updat[a-z]*|actualiz[a-z]*|bump[a-z]*|subid[a-z]*|rais[a-z]*|elev[a-z]*|touch[a-z]*|cambi[a-z]*)"
        r"[^.]{0,200}(?:expected|digest|sha256)"
        r"|(?:never|not|no|nunca|jamás|sin)\b[^.]{0,200}(?:expected|digest|sha256)[^.]{0,200}"
        r"(?:updat[a-z]*|actualiz[a-z]*|bump[a-z]*|subid[a-z]*|rais[a-z]*|elev[a-z]*|touch[a-z]*|cambi[a-z]*)",
    ),
)

# --- PD-8/PD-9: el caso de la tabla, en la sección `### Scribe` ------------
REQ_PD9_SCRIBE = (
    (
        "the two writers of the table",
        r"two writers|dos escritores|both writers|two authors|dos autores|two parties|dos partes",
    ),
    ("the orchestrator", r"orchestrator|orquestador"),
    (
        "the orchestrator writes its rows directly in docs/",
        r"(?:direct[a-z]*|escribe[a-z]*|write[a-z]*)[^.]{0,300}"
        r"(?:docs/|`docs`|docs (?:directory|directorio|tree|árbol))"
        r"|(?:docs/|`docs`|docs (?:directory|directorio|tree|árbol))[^.]{0,300}"
        r"(?:direct[a-z]*|escribe[a-z]*|write[a-z]*)",
    ),
    (
        "with its own commit",
        r"(?:orchestrator|orquestador)[^.]{0,400}commit|commit[^.]{0,400}(?:orchestrator|orquestador)",
    ),
    (
        "the scribe's proposal arrives by materialization",
        r"scribe[^.]{0,500}materializ[a-z]*|materializ[a-z]*[^.]{0,500}scribe",
    ),
)

# El bloque de texto NO puede exigir la semilla (B-1): ni la tabla viva del
# proyecto, ni el directorio de ADR, ni la identidad de un ADR. (Ojo: el
# NOMBRE del archivo de la PLANTILLA no es la semilla: la semilla es la
# instancia viva del proyecto, que se siembra en U5.)
SEED_MENTIONS = re.compile(r"docs\s*/\s*systempatterns|docs/adr|adr-0\d\d", re.IGNORECASE)


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
            f"{label}: el artefacto declarado por el contrato no existe: {relative(path)}"
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        raise AssertionError(f"{label}: el artefacto declarado está vacío: {relative(path)}")
    return text


def flat(text: str) -> str:
    """Normalización: los espacios colapsados (una prosa envuelta en varias
    líneas es un texto corrido; un concepto partido por el ajuste de línea
    sigue siendo un concepto)."""
    return re.sub(r"\s+", " ", text).strip()


def section_body(text: str, level: int, heading: re.Pattern[str]) -> str:
    """El cuerpo de la sección cuyo encabezado (de nivel `level`) casa con
    `heading`, hasta el próximo encabezado de nivel <= `level`."""
    lines = text.splitlines()
    body: list[str] = []
    inside = False
    for line in lines:
        match = re.match(r"^(#+)\s*(.*)$", line)
        if match:
            current = len(match.group(1))
            if not inside:
                if current == level and heading.search(match.group(2)):
                    inside = True
                    continue
            elif current <= level:
                break
        if inside:
            body.append(line)
    return "\n".join(body)


def first_h2(text: str) -> str:
    """El texto del primer H2 del documento (el lugar declarado)."""
    for line in text.splitlines():
        match = re.match(r"^##\s+(.*)$", line)
        if match:
            return match.group(1).strip()
    return ""


def materialization_step3(text: str) -> str:
    """El paso 3 (MATERIALIZE) del protocolo de materialización de re-entry.md."""
    body: list[str] = []
    inside = False
    for line in text.splitlines():
        if re.match(r"^\s*3\.\s+\*\*MATERIALIZE", line):
            inside = True
            continue
        if inside:
            if re.match(r"^\s*4\.\s", line):
                break
            body.append(line)
    return "\n".join(body)


def missing_concepts(text: str, requirements) -> list[str]:
    """Los conceptos que el texto NO declara (la redacción es libre: se deriva
    el concepto, no la frase)."""
    missing: list[str] = []
    for label, pattern in requirements:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(label)
    return missing


def block_text() -> str:
    """El bloque de texto de esta unidad dentro del validador."""
    text = read_document(VALIDATOR, "006-004 U4 (the text block of the validator)")
    lines = text.splitlines()
    try:
        begin = next(index for index, line in enumerate(lines) if line.startswith(BLOCK_BEGIN))
        end = next(
            index
            for index, line in enumerate(lines)
            if index > begin and line.startswith(BLOCK_END)
        )
    except StopIteration:
        return ""
    return "\n".join(lines[begin : end + 1])


# El arnés para ejecutar el bloque fuera del validador completo: el MISMO
# encabezado del validador (sus helpers: pass/fail, assert_file_has, ...), con
# el ROOT apuntando al árbol sobre el que se ejecuta, y nada más.
HELPERS_END = 'echo "############################################"'


def validator_helpers() -> str:
    """El encabezado del validador: sus contadores y sus helpers.

    Se USA el encabezado real (no una copia): un bloque que employe un helper
    del validador se comporta igual aquí y en `make validate`.
    """
    text = read_document(VALIDATOR, "006-004 U4 (the validator)")
    index = text.find(HELPERS_END)
    if index < 0:
        return ""
    return text[:index]


def run_block(tree: Path) -> tuple[list[str], list[str], str]:
    """Ejecuta el bloque de texto como PROCESO REAL sobre `tree`.

    Devuelve (códigos fallados, códigos pasados, salida completa).
    """
    script = (
        validator_helpers()
        + f'\nROOT="{tree}"\ncd "$ROOT" || exit 2\n'
        + block_text()
    )
    proc = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        cwd=str(tree),
    )
    output = proc.stdout + proc.stderr
    failed = re.findall(r"^FAIL:\s*006-004 U4 ([A-Z0-9-]+)", output, re.MULTILINE)
    passed = re.findall(r"^PASS:\s*006-004 U4 ([A-Z0-9-]+)", output, re.MULTILINE)
    return failed, passed, output


def build_trees(root: Path) -> tuple[Path, Path]:
    """Dos árboles DESCARTABLES: uno con la semilla (la tabla viva del
    proyecto y su directorio de ADR) y otro sin ella.

    El segundo es el control de B-1: si el bloque exigiera la semilla, su
    resultado en el segundo árbol diferiría del primero.

    La semilla del primer árbol es **simulada** (la siembra real es el producto
    de U5, que todavía no existe): una sección de decisiones vigentes en el
    archivo de patrones del proyecto y un ADR-034 con su archivo. Lo que se
    comprueba NO es el contenido de la semilla, sino que el bloque de texto de
    esta unidad **no dependa** de ella.
    """
    seedless = root / "seedless"
    seedless.mkdir(parents=True)
    for relative_path in COPIED_SKILL_PATHS:
        source = REPO_ROOT / relative_path
        target = seedless / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)

    seeded = root / "seeded"
    shutil.copytree(seedless, seeded)
    adr_dir = seeded / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    # La tabla viva del proyecto, con la semilla SIMULADA (la siembra real es
    # el producto de U5, que todavia no existe).
    (seeded / "docs" / "systemPatterns.md").write_text(
        read_document(REPO_ROOT / "docs/systemPatterns.md", "the live patterns")
        + "\n## Decisiones vigentes\n\n"
        + "| Decisión | Archivo | Estado | Roles | Referencia |\n"
        + "|---|---|---|---|---|\n"
        + "| ADR-034 | docs/adr/ADR-034-principio-general-antes-especifico.md |"
        + " vigente | architect, reviewer |"
        + " skills/cdad-cycle/references/design-principles.md |\n",
        encoding="utf-8",
    )
    for adr in sorted((REPO_ROOT / "docs" / "adr").glob("*.md")):
        shutil.copy2(adr, adr_dir / adr.name)
    (adr_dir / "ADR-034-principio-general-antes-especifico.md").write_text(
        "# ADR-034 - principio general antes que especifico\n\n"
        "**Status**: Accepted\n",
        encoding="utf-8",
    )
    return seeded, seedless


# ---------------------------------------------------------------------------
# PD-7 — la plantilla
# ---------------------------------------------------------------------------


class TestPd7TemplateSection(unittest.TestCase):
    def test_pd7_the_template_carries_the_decisions_section_as_its_first_h2(self):
        text = read_document(TEMPLATE, "PD-7 (the Memory Bank template)")
        heading = first_h2(text)
        self.assertTrue(
            heading,
            "PD-7: the Memory Bank template has no H2 at all (the section cannot be there)",
        )
        self.assertTrue(
            DECISIONS_SECTION.search(heading),
            "PD-7: the Memory Bank template must carry the decisions section as its "
            f"FIRST H2 (after the introduction); its first H2 is {heading!r}",
        )

    def test_pd7_the_section_of_the_template_carries_the_row_shape_and_the_note(self):
        text = read_document(TEMPLATE, "PD-7 (the Memory Bank template)")
        body = flat(section_body(text, 2, DECISIONS_SECTION))
        self.assertTrue(
            body,
            "PD-7: the Memory Bank template has no decisions section (the row shape "
            "and the note cannot be declared there)",
        )
        missing = missing_concepts(body, REQ_PD7_SHAPE + REQ_PD7_NOTE)
        self.assertEqual(
            [],
            missing,
            "PD-7: the decisions section of the Memory Bank template must declare the "
            "row shape (file, state, one-line summary, roles, reference) and the note "
            "(the exclusions, and that the state is declared by whoever maintains the "
            f"table); missing: {missing}",
        )


# ---------------------------------------------------------------------------
# PD-7/PD-8 — control negativo: el exit gate de stage 5 no cambia
# ---------------------------------------------------------------------------


class TestPd7ExitGateControl(unittest.TestCase):
    def test_pd7_the_exit_gate_of_stage_5_did_not_gain_checkboxes(self):
        text = read_document(STAGE5, "PD-7/PD-8 (the exit gate of stage 5)")
        body = section_body(text, 2, EXIT_GATE_HEADING)
        self.assertTrue(
            body.strip(),
            "PD-7/PD-8: the exit gate of stage 5 was not found in stage-5-merge.md",
        )
        boxes = [line for line in body.splitlines() if re.match(r"^\s*-\s*\[[ xX]\]", line)]
        self.assertEqual(
            EXIT_GATE_CHECKBOXES,
            len(boxes),
            "PD-7/PD-8: the exit gate of stage 5 must NOT gain checkboxes (Q6): it "
            f"keeps its {EXIT_GATE_CHECKBOXES} (measured before the feature) and now "
            f"has {len(boxes)}: {boxes}",
        )
        about_the_table = [
            line
            for line in boxes
            if re.search(r"current decisions|decisiones vigentes|systempatterns", line, re.I)
        ]
        self.assertEqual(
            [],
            about_the_table,
            "PD-7/PD-8: no checkbox of the exit gate of stage 5 may be about the "
            f"decisions table (the gate does not change): {about_the_table}",
        )


# ---------------------------------------------------------------------------
# PD-8 — el upkeep, en §5.4 de stage-5-merge.md
# ---------------------------------------------------------------------------


class TestPd8Upkeep(unittest.TestCase):
    def test_pd8_stage5_merge_names_the_upkeep_of_the_table(self):
        text = read_document(STAGE5, "PD-8 (the upkeep of the decisions table)")
        body = flat(section_body(text, 2, ADR_DECISION_HEADING))
        self.assertTrue(
            body,
            "PD-8: section 5.4 of stage-5-merge.md (the decision on the ADR) was not "
            "found: the upkeep of the table belongs there",
        )
        missing = missing_concepts(body, REQ_PD8_UPKEEP)
        self.assertEqual(
            [],
            missing,
            "PD-8: section 5.4 of stage-5-merge.md must name the upkeep of the "
            "decisions table (when an ADR is approved, the orchestrator adds its row; "
            f"the previous row is marked obsolete); missing: {missing}",
        )


# ---------------------------------------------------------------------------
# PD-9 — la regla general del CAS y el caso de la tabla
# ---------------------------------------------------------------------------


class TestPd9CasRule(unittest.TestCase):
    def test_pd9_reentry_step3_declares_the_general_cas_by_base_rule(self):
        text = read_document(REENTRY, "PD-9 (the CAS rule of the materialization protocol)")
        body = flat(materialization_step3(text))
        self.assertTrue(
            body,
            "PD-9: step 3 (MATERIALIZE) of the materialization protocol of re-entry.md "
            "was not found: the general CAS rule belongs there (DEC-13)",
        )
        missing = missing_concepts(body, REQ_PD9_CAS)
        self.assertEqual(
            [],
            missing,
            "PD-9: step 3 (MATERIALIZE) of re-entry.md must declare the general CAS "
            "rule: the declared digest is always the BASE digest (the version the "
            "proposal was prepared on), never the current one; on conflict, re-dispatch "
            "the role with a new packet on the new base; no manual merge and no "
            f"updating of the expected digest; missing: {missing}",
        )

    def test_pd9_reentry_scribe_section_declares_the_case_of_the_table(self):
        text = read_document(REENTRY, "PD-9 (the Scribe section of re-entry.md)")
        body = flat(section_body(text, 3, SCRIBE_HEADING))
        self.assertTrue(
            body,
            "PD-9: the `### Scribe` section of re-entry.md was not found: the case of "
            "the table (two writers) belongs there",
        )
        missing = missing_concepts(body, REQ_PD9_SCRIBE)
        self.assertEqual(
            [],
            missing,
            "PD-9: the `### Scribe` section of re-entry.md must declare the case of the "
            "table: two writers; the orchestrator writes its own rows directly in "
            "docs/ with its commit; the scribe's proposal arrives by materialization; "
            f"missing: {missing}",
        )


# ---------------------------------------------------------------------------
# El bloque de texto de la unidad (el oráculo durable del validador)
# ---------------------------------------------------------------------------


class TestU4TextBlock(unittest.TestCase):
    def test_pd7_pd8_pd9_the_text_block_of_u4_passes_on_the_tree(self):
        block = block_text()
        self.assertTrue(
            block.strip(),
            "006-004 U4: tests/validate-consistency.sh has no text block for this "
            "unit (the block of the template and the two references)",
        )
        failed, passed, output = run_block(REPO_ROOT)
        self.assertEqual(
            [],
            failed,
            "006-004 U4: the text block of the unit (the template and the two "
            "references) must pass; failed asserts: " + ", ".join(failed) + "\n" + output,
        )
        self.assertTrue(
            passed,
            "006-004 U4: the text block of the unit reported no passing assert "
            "(it did not run)\n" + output,
        )

    def test_pd7_pd8_pd9_the_text_block_of_u4_does_not_require_the_live_table_nor_adr_034(
        self,
    ):
        block = block_text()
        self.assertTrue(
            block.strip(),
            "006-004 U4: tests/validate-consistency.sh has no text block for this unit",
        )
        mentions = sorted({match.group(0) for match in SEED_MENTIONS.finditer(block)})
        self.assertEqual(
            [],
            mentions,
            "006-004 U4 (B-1): the text block of this unit must NOT require the live "
            "table of the project nor any ADR (the seed is U5's product and its gate "
            "runs later): it mentions " + ", ".join(mentions),
        )

    def test_pd7_pd8_pd9_the_text_block_of_u4_behaves_the_same_without_the_seed(self):
        block = block_text()
        self.assertTrue(
            block.strip(),
            "006-004 U4: tests/validate-consistency.sh has no text block for this unit",
        )
        with tempfile.TemporaryDirectory() as tmp:
            seeded, seedless = build_trees(Path(tmp))
            failed_seeded, _, output_seeded = run_block(seeded)
            failed_seedless, _, output_seedless = run_block(seedless)
        self.assertEqual(
            sorted(failed_seeded),
            sorted(failed_seedless),
            "006-004 U4 (B-1): the result of the text block must not depend on the "
            "seed (the live table and the ADR directory): with the seed it reports "
            f"{sorted(failed_seeded)} and without it {sorted(failed_seedless)}\n"
            + output_seeded
            + "\n"
            + output_seedless,
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
