#!/usr/bin/env python3
"""006-004 B-1 RED — la plantilla del Memory Bank nace SIN decisiones.

Hallazgo **B-1** de la revisión de etapa 4 de 006-004
(``docs/specs/006-004-active-decisions-table/review.md``:9-28):

    la plantilla del Memory Bank trae una fila de datos de ejemplo ``vigente``
    que apunta a ``docs/adr/ADR-NNN-<slug>.md``; el bootstrap la copia y un
    proyecto **sin decisiones** nace declarando una decisión **inexistente**.

    Remedio (review.md:26): «dejar únicamente encabezado y separador; explicar
    el ejemplo fuera de las filas de datos».

Contrato:
- ``docs/specs/006-004-active-decisions-table/spec.md`` §3 **PD-7** (la
  plantilla trae la sección y **un proyecto sin ADR no queda bloqueado**),
  §3.1 **E5** (un proyecto sin ADR no queda bloqueado: «la sección vacía **no**
  es una fila») y §3 **PD-11** (la siembra, en dos capas: lo duradero se
  valida).
- ``docs/specs/006-004-active-decisions-table/review.md`` **B-1** (el defecto
  y su cierre verificable: «copiar literalmente la plantilla a un proyecto sin
  ADR, comprobar que no contiene decisiones declaradas y que el comprobador
  acepta esa tabla vacía»).
- ``docs/specs/006-004-active-decisions-table/plan.md`` §3 fichas **U4** (la
  plantilla del Memory Bank) y **U7** (el bloque permanente de la tabla).

Superficie observable bajo prueba (caja negra: sólo el TEXTO publicado de la
plantilla y PROCESOS REALES; la implementación NUNCA se lee, NUNCA se
importa):

- ``skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md`` — la
  plantilla que el bootstrap copia al proyecto nuevo;
- ``tests/validate-consistency.sh`` — el **bloque permanente de la tabla**
  (el de U7), ejecutado como PROCESO REAL sobre un proyecto **DESCARTABLE**
  (nunca el HOME, nunca el árbol de trabajo).

INTERFAZ DECLARADA POR ESTE RED (la satisface el implementer leyendo el test;
el contrato queda en el hallazgo B-1 y en su remedio; la redacción es libre):

1. La tabla de la sección de la plantilla tiene **encabezado** y **separador**
   y **CERO filas de datos**: una plantilla que declara una decisión la
   declara para todos los proyectos que la copian.
2. Copiada **literalmente** a ``docs/systemPatterns.md`` de un proyecto
   **sin** ``docs/adr/``, la plantilla **pasa** el comprobador permanente de
   la tabla (el bloque de U7, invocado como lo invocan los tests de U7): la
   sección vacía no es una fila.
3. La plantilla **sigue explicando la forma de la fila** (archivo · estado ·
   resumen de una línea · roles · referencia) **fuera de las filas de datos**:
   el ejemplo se **explica**, no se **declara**.

   OJO (interfaz, no detalle): la explicación va en **prosa**. El comprobador
   lee **toda** línea que empieza por ``|`` de la sección como una fila de
   datos: un ejemplo escrito como tabla (o dentro de un bloque cercado con
   barras) sería leído como una fila y fallaría por un archivo inexistente.

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica):

- La derivación de la forma de la fila es **por CONCEPTO** (vocabulario con
  alternativas de idioma), como el RED de U4: la redacción es libre, el
  concepto no.
- Este RED **no** toca el validador: usa el bloque que ya existe (el de U7) y
  lo **ejecuta**; no añade, no modifica y no elimina ninguna aserción.
- Este RED **no** exige nada de la tabla viva del proyecto ni de su
  directorio de decisiones: eso es la superficie de U5/U7.
- Este RED **no** comprueba el ``prepare`` sin filas (ya lo comprueba el RED
  de U2: ``test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section``);
  su alcance es la **plantilla** y el **comprobador permanente**.

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** Ningún test vigente fija la fila de ejemplo (no hay ninguna
mención de ``ADR-NNN`` en ``tests/``): este RED **añade** un archivo de tests
y **no** modifica, no sustituye y no invisibiliza ninguna prueba vigente. El
oráculo de U4 que exige la forma de la fila y la nota en la sección de la
plantilla (``test_pd7_the_section_of_the_template_carries_the_row_shape_and_the_note``)
**sigue verde** con el remedio: la forma se explica fuera de las filas de
datos y la nota no se toca.

RED esperado contra el árbol vigente (OBSERVADO; declarado, no accidental):

- **Fallan por ``AssertionError`` de CONTRATO**: (1) la tabla de la plantilla
  trae una fila de datos; (2) la plantilla copiada a un proyecto sin ADR no
  pasa el comprobador permanente (la fila apunta a un archivo inexistente).
- **Pasa hoy** el control (3): la forma de la fila está declarada fuera de
  las filas de datos (en el encabezado), y sigue estándolo después del
  remedio.
- Ningún fallo es ImportError, SyntaxError ni error de fixture: los
  artefactos requeridos que faltan se reportan con ``assert`` y su mensaje
  contractual.

Mapeo test → postcondición (un test por aserción observable; el 3 es un
control declarado):

  1  ``TestB1TemplateIsBornEmpty::test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row``
     → PD-7 / E5
  2  ``TestB1TemplateIsBornEmpty::test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker``
     → PD-7 / E5 / PD-11
  3  ``TestB1TemplateIsBornEmpty::test_b1_the_template_still_declares_the_row_shape_outside_the_data_rows``
     → PD-7 (CONTROL declarado)
"""

from __future__ import annotations

import os
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

# La plantilla que el bootstrap copia al proyecto nuevo.
TEMPLATE = REPO_ROOT / "skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md"

# El validador permanente: su bloque de la tabla (el de U7) es el comprobador
# que este RED ejecuta.
VALIDATOR = REPO_ROOT / "tests" / "validate-consistency.sh"

# La casa canónica del principio: el comprobador la compara contra los
# archivos apuntados por las filas (y falla cerrado si no existe).
CANONICAL_PRINCIPLE = (
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "design-principles.md"
)

# El bloque de la tabla dentro del validador (marcadores; los mismos que usa
# el RED de U7).
BLOCK_BEGIN = "# BEGIN 006-004 U7"
BLOCK_END = "# END 006-004 U7"

# El encabezado del validador: sus contadores y sus helpers.
HELPERS_END = 'echo "############################################"'

# ---------------------------------------------------------------------------
# Conceptos (derivación textual por CONCEPTO; la redacción es libre)
# ---------------------------------------------------------------------------

# El título de la sección: libre (spec §2.5, Q5); se aceptan las dos
# redacciones declaradas (inglés en la plantilla, español en la instancia
# viva del proyecto).
DECISIONS_SECTION = re.compile(r"current\s+decisions|decisiones\s+vigentes", re.IGNORECASE)

# Una fila de datos de una tabla markdown: la primera celda es la que apunta
# al archivo de la decisión.
DATA_ROW = re.compile(r"^\|")

# El separador de una tabla markdown.
SEPARATOR_ROW = re.compile(r"^\|[\s:\-|]+$")

# La forma de la fila (los mismos conceptos que deriva el RED de U4).
REQ_SHAPE = (
    ("the file of the decision", r"file|archivo|ruta|path"),
    ("the state of the decision", r"state|estado|vigente|obsoleto"),
    ("the one-line summary", r"summary|resumen"),
    ("the roles that must consume it", r"roles|consumers|consumidores|who consumes"),
    ("the reference where the rule lives", r"reference|referencia"),
)


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
    líneas es un texto corrido)."""
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


def table_of(section_text: str) -> tuple[str, str, list[str]]:
    """La tabla de la sección: ``(encabezado, separador, filas de datos)``.

    Una tabla markdown son líneas que empiezan por ``|``. La primera es el
    encabezado, la segunda es el separador y **el resto son filas de datos**:
    una fila de datos es una fila que DECLARA una decisión.
    """
    rows = [line.strip() for line in section_text.splitlines() if DATA_ROW.match(line.strip())]
    header = rows[0] if rows else ""
    separator = ""
    data: list[str] = []
    for index, row in enumerate(rows):
        if SEPARATOR_ROW.match(row):
            separator = row
            data = rows[index + 1 :]
            break
    if not separator:
        # Sin separador no hay tabla: lo que sigue del encabezado serían
        # filas de datos (o nada).
        data = rows[1:] if rows else []
    return header, separator, data


def block_text() -> str:
    """El bloque permanente de la tabla dentro del validador (el de U7)."""
    text = read_document(VALIDATOR, "006-004 B-1 (el validador permanente)")
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


def validator_helpers() -> str:
    """El encabezado del validador: sus contadores y sus helpers.

    Se USA el encabezado real (no una copia): un bloque que emplee un helper
    del validador se comporta igual aquí y en ``make validate``.
    """
    text = read_document(VALIDATOR, "006-004 B-1 (el validador permanente)")
    index = text.find(HELPERS_END)
    if index < 0:
        return ""
    return text[:index]


def run_block(tree: Path, tmp: Path) -> tuple[list[str], list[str], str, int]:
    """Ejecuta el bloque permanente de la tabla como PROCESO REAL sobre `tree`.

    La invocación es **la misma** que la del RED de U7: el encabezado real del
    validador (sus helpers), ``ROOT`` apuntando al árbol, el bloque tal cual y
    ``U7_STANDALONE=1`` para que el bloque conteste con su propio código de
    salida.

    Devuelve (códigos fallados, códigos pasados, salida completa, rc).
    """
    script = (
        validator_helpers()
        + f'\nROOT="{tree}"\ncd "$ROOT" || exit 2\n'
        + block_text()
    )
    script_file = tmp / "b1_block.sh"
    script_file.write_text(script, encoding="utf-8")
    env = os.environ.copy()
    env["U7_STANDALONE"] = "1"
    proc = subprocess.run(
        ["bash", str(script_file)],
        capture_output=True,
        text=True,
        cwd=str(tree),
        env=env,
    )
    output = proc.stdout + proc.stderr
    failed = re.findall(r"^FAIL:\s*006-004 U7 ([A-Z0-9-]+)", output, re.MULTILINE)
    passed = re.findall(r"^PASS:\s*006-004 U7 ([A-Z0-9-]+)", output, re.MULTILINE)
    return failed, passed, output, proc.returncode


def build_project_without_adrs(root: Path) -> Path:
    """Un proyecto DESCARTABLE **sin decisiones**: la plantilla copiada
    LITERALMENTE a ``docs/systemPatterns.md`` y ningún ``docs/adr/``.

    Es el caso del bootstrap (``references/bootstrap.md``: el bootstrap copia
    la plantilla): un proyecto nuevo nace con la sección recién instalada y
    **sin** ninguna decisión.

    El proyecto lleva la casa canónica del principio (el árbol instalable del
    skill) porque el comprobador la compara contra los archivos apuntados por
    las filas y **falla cerrado** si no la encuentra.
    """
    project = root / "fresh"
    (project / "docs").mkdir(parents=True, exist_ok=True)

    # La plantilla, LITERALMENTE (byte a byte): sin traducciones ni retoques.
    shutil.copy2(TEMPLATE, project / "docs" / "systemPatterns.md")

    canonical = project / "skills" / "cdad-cycle" / "references" / "design-principles.md"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    read_document(CANONICAL_PRINCIPLE, "006-004 B-1 (la casa canónica del principio)")
    shutil.copy2(CANONICAL_PRINCIPLE, canonical)

    # SIN docs/adr/: un proyecto sin decisiones.
    return project


# ---------------------------------------------------------------------------
# B-1 — la plantilla nace sin decisiones
# ---------------------------------------------------------------------------


class TestB1TemplateIsBornEmpty(unittest.TestCase):
    """B-1 (review.md): la plantilla no declara ninguna decisión.

    Un proyecto sin ADR nace copiando la plantilla: si la plantilla trae una
    fila de ejemplo, el proyecto nace declarando una decisión que no existe.
    """

    def test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row(
        self,
    ) -> None:
        """PD-7 / E5: la tabla de la sección de la plantilla está VACÍA.

        Encabezado y separador (la forma de la tabla) y **cero** filas de
        datos: la sección recién instalada no declara ninguna decisión.
        """
        text = read_document(TEMPLATE, "B-1 (la plantilla del Memory Bank)")
        body = section_body(text, 2, DECISIONS_SECTION)
        self.assertTrue(
            body.strip(),
            "B-1 (PD-7/E5): la plantilla del Memory Bank no tiene la sección de "
            "las decisiones: no se puede comprobar que nazca vacía",
        )
        header, separator, data = table_of(body)
        self.assertTrue(
            header,
            "B-1 (PD-7/E5): la sección de la plantilla no tiene el encabezado de "
            "la tabla",
        )
        self.assertTrue(
            separator,
            "B-1 (PD-7/E5): la sección de la plantilla no tiene el separador de "
            "la tabla (sólo el encabezado: %r)" % header,
        )
        self.assertEqual(
            [],
            data,
            "B-1 (PD-7/E5): la sección de la plantilla debe nacer con el "
            "encabezado y el separador y CERO filas de datos: una fila de "
            "ejemplo declara una decisión en todos los proyectos que copian "
            "la plantilla (el bootstrap la copia literal); filas de datos: %s"
            % " | ".join(row[:160] for row in data),
        )

    def test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker(
        self,
    ) -> None:
        """PD-7 / E5 / PD-11: la plantilla copiada pasa el comprobador permanente.

        El caso es el del bootstrap: la plantilla va **literalmente** a
        ``docs/systemPatterns.md`` de un proyecto **sin** ``docs/adr/``. El
        comprobador permanente de la tabla (el bloque de U7, invocado como lo
        invocan los tests de U7) tiene que **aceptar** esa tabla vacía: la
        sección vacía no es una fila.
        """
        block = block_text()
        self.assertTrue(
            block.strip(),
            "B-1: tests/validate-consistency.sh no tiene el bloque permanente de "
            "la tabla (marcadores %s / %s)" % (BLOCK_BEGIN, BLOCK_END),
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            project = build_project_without_adrs(tmp_path)
            self.assertFalse(
                (project / "docs" / "adr").exists(),
                "B-1: el caso descartable debe ser un proyecto SIN decisiones "
                "(docs/adr/ no existe)",
            )
            failed, passed, output, rc = run_block(project, tmp_path)
        self.assertEqual(
            [],
            failed,
            "B-1 (PD-7/E5/PD-11): el comprobador permanente de la tabla debe "
            "aceptar la plantilla copiada a un proyecto sin ADR (la sección "
            "vacía no es una fila); asserts fallados: %s\n%s"
            % (", ".join(failed) or "ninguno", output),
        )
        self.assertEqual(
            0,
            rc,
            "B-1 (PD-7/E5/PD-11): el comprobador permanente de la tabla no pasó "
            "con la plantilla copiada a un proyecto sin ADR:\n%s" % output,
        )
        self.assertTrue(
            passed,
            "B-1: el comprobador permanente no reportó ninguna comprobación "
            "pasada (no se ejecutó)\n%s" % output,
        )

    def test_b1_the_template_still_declares_the_row_shape_outside_the_data_rows(
        self,
    ) -> None:
        """PD-7 (CONTROL): la forma de la fila se sigue explicando.

        El remedio de B-1 vacía la tabla, **no** borra la forma de la fila:
        el ejemplo se **explica** fuera de las filas de datos (archivo ·
        estado · resumen de una línea · roles · referencia).
        """
        text = read_document(TEMPLATE, "B-1 (la plantilla del Memory Bank)")
        body = section_body(text, 2, DECISIONS_SECTION)
        self.assertTrue(
            body.strip(),
            "B-1 (PD-7): la plantilla del Memory Bank no tiene la sección de "
            "las decisiones",
        )
        _header, _separator, data = table_of(body)
        # El texto de la sección SIN las filas de datos: la forma de la fila
        # tiene que estar declarada ahí (en la prosa o en el encabezado).
        without_data = "\n".join(
            line for line in body.splitlines() if line.strip() not in data
        )
        declared = flat(without_data)
        missing = [
            label
            for label, pattern in REQ_SHAPE
            if not re.search(pattern, declared, re.IGNORECASE)
        ]
        self.assertEqual(
            [],
            missing,
            "B-1 (PD-7): la plantilla debe seguir explicando la forma de la "
            "fila (archivo, estado, resumen de una línea, roles, referencia) "
            "FUERA de las filas de datos; faltan: %s" % ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()
