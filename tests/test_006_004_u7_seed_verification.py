#!/usr/bin/env python3
"""006-004 U7 RED — la verificación de la siembra: el bloque del validador y su control negativo.

Contrato:
- ``docs/specs/006-004-active-decisions-table/spec.md`` (aprobada 2026-10-20)
  §3 **PD-11** (la siembra en dos capas: lo duradero se valida, el inventario se
  acredita), §4 **INV-15** (el inventario no es una restricción permanente) y
  **INV-16** (ninguna propiedad del validador depende de *qué* decisión es),
  §5 **DEC-15** (el validador lleva invariantes duraderas; el inventario sembrado
  es evidencia puntual) y **DEC-16** (el validador no lleva excepciones por
  identidad), §6 **V-7** (¿el comprobador admite el reemplazo sin editarlo?) y
  §3.1 **E4** (el reviewer detecta una tabla desalineada).
- ``docs/specs/006-004-active-decisions-table/plan.md`` §1.2 (qué NO es una
  invariante: ni el inventario ni la identidad de una decisión), §3 **ficha U7**
  (archivos, RED, regresiones, A-1, gate) y su bloque ``plan-tasks`` (los
  ``observable_checks`` de U7, que son el contrato operativo de este RED).

Superficie observable bajo prueba (caja negra: sólo el **texto publicado** del
validador y **PROCESOS REALES**; la implementación NUNCA se lee, NUNCA se
importa):

- ``tests/validate-consistency.sh`` — el **bloque de la siembra** de esta
  unidad (el bloque de U4 cubre plantilla y procedimiento; éste cubre la tabla
  viva), ejecutado como PROCESO REAL sobre el árbol del proyecto y sobre
  proyectos **DESCARTABLES** (nunca el HOME, nunca el árbol de trabajo).

INTERFAZ DECLARADA POR ESTE RED (la satisface quien cierra la unidad leyendo
el test; la spec §3 PD-11 y la ficha U7 fijan el contrato y dejan la
redacción del bloque dentro):

1. La sección de decisiones es el **primer H2** del documento de la tabla.
2. **Cada** línea de la tabla apunta a un archivo que **existe** y está
   **dentro de** ``docs/adr/`` — la dirección es **línea → archivo**, nunca
   archivo → línea: el estado de una decisión no es derivable (D-3).
3. **Toda** línea obsoleta nombra un reemplazo, y ese reemplazo **existe**.
4. **Todo** rol de **toda** línea pertenece al vocabulario cerrado.
5. **Ningún** archivo apuntado por una línea re-enuncia el texto normativo del
   principio (la casa única se extiende a las líneas).
6. La nota declara que **el estado lo declara quien mantiene la tabla** (D-3).
7. El propio bloque **no nombra ninguna decisión** (control negativo sobre el
   bloque: un ``grep`` acotado a sus líneas no encuentra un id de decisión).
8. El propio bloque **no fija ninguna figura del inventario** (ni el número de
   líneas, ni el de vigentes, ni el de obsoletas, ni el de excluidas).

CIERRE DEL COMPROBADOR (los tres casos de la ficha U7, con el **MISMO** bloque
y **sin editarlo** — el digest del bloque se mide antes y después):

- (i) una línea que apunta a un archivo **inexistente** ⇒ el bloque **detecta y
  reporta** la desalineación (el mismo hecho que E4 exige del reviewer);
- (ii) una tabla a la que se **agrega una decisión aprobada** (un archivo nuevo
  en ``docs/adr/`` + su línea vigente) ⇒ el bloque **pasa**;
- (iii) una tabla en la que se **reemplaza expresamente** una decisión (su
  línea pasa a obsoleta con su sucesor —**el archivo se conserva**— y la línea
  sucesora queda vigente con su archivo existente) ⇒ el bloque **pasa**.

LÍMITE DECLARADO DE ESTE RED (no sobre-especifica la mecánica):

- La derivación es **por CONCEPTO** (vocabulario con alternativas de idioma),
  **no por frase exacta**: la redacción de los documentos y del bloque es
  libre; el concepto no.
- El RED **no fija el inventario sembrado**: las figuras de la siembra y la
  ficha de cualquier decisión concreta se acreditan **una vez**, en la
  evidencia de U5 y U7 (spec §4 INV-15, §5 DEC-15/DEC-16) — **no** se
  comprueban aquí ni en el validador. Este RED comprueba lo contrario y es lo
  único que comprueba: que el validador **no** las fija.
- El RED **no** exige del validador ninguna redacción: exige su
  **comportamiento** sobre copias descartables.
- El RED **no** toca ningún archivo de ``tests/`` ajeno a este.

A-1 (declarada, plan §4): **esta feature NO reemplaza ningún oráculo
vigente.** El bloque que este RED añade al validador **crece**; no modifica ni
elimina ninguna aserción vigente. Los casos que este RED añade son **controles
negativos añadidos** (línea desalineada, línea fuera del directorio, reemplazo
inexistente, rol fuera del vocabulario, forma de línea rota, archivo que
re-enuncia el principio, nota que no declara el estado, sección que no es el
primer H2, decisión aprobada nueva y decisión reemplazada), **no oráculos
reemplazados**. Y el bloque que se añade **no fija ninguna figura del
inventario** ni **contiene ninguna comprobación por identidad** (B-3, DEC-15,
DEC-16).

Mapa de este RED → postcondiciones (un caso por comprobación observable):

  1  ``test_pd11_the_block_of_the_seeding_exists``                        PD-11
  2  ``test_pd11_the_block_names_no_decision``                             PD-11, DEC-16, INV-16
  3  ``test_pd11_the_block_fixes_no_figure_of_the_inventory``              PD-11, DEC-15, INV-15
  4  ``test_pd11_the_block_accepts_a_coherent_table``                      PD-11
  5  ``test_pd11_the_block_rejects_a_line_pointing_to_a_missing_file``     PD-11, E4
  6  ``test_pd11_the_block_rejects_a_line_pointing_outside_the_adr_dir``   PD-11
  7  ``test_pd11_the_block_rejects_an_obsolete_line_without_replacement``  PD-11
  8  ``test_pd11_the_block_rejects_an_obsolete_line_whose_replacement_is_missing``  PD-11
  9  ``test_pd11_the_block_rejects_a_role_outside_the_vocabulary``         PD-11
 10  ``test_pd11_the_block_rejects_a_line_whose_shape_is_broken``         PD-11
 11  ``test_pd11_the_block_rejects_a_file_that_re_enounces_principle``     PD-11, DEC-16
 12  ``test_pd11_the_block_rejects_a_note_without_the_state_declaration``  PD-11, D-3
 13  ``test_pd11_the_block_rejects_a_section_that_is_not_the_first_h2``    PD-11
 14  ``test_pd11_e4_v7_closure_of_the_checker``                            PD-11, E4, V-7
 15  ``test_pd11_the_block_passes_on_the_live_table``                      PD-11
"""

from __future__ import annotations

import hashlib
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

VALIDATOR = REPO_ROOT / "tests" / "validate-consistency.sh"
LIVE_TABLE = REPO_ROOT / "docs" / "systemPatterns.md"
ADR_DIR = REPO_ROOT / "docs" / "adr"
CANONICAL_PRINCIPLE = (
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "design-principles.md"
)

# El bloque de la siembra de esta unidad dentro del validador (marcadores).
BLOCK_BEGIN = "# BEGIN 006-004 U7"
BLOCK_END = "# END 006-004 U7"

# El encabezado del validador: sus contadores y sus helpers.
HELPERS_END = 'echo "############################################"'

# Los códigos que el bloque declara (uno por invariante duradera).
CODES = (
    "PD-11-SECTION",
    "PD-11-FILE",
    "PD-11-REPLACEMENT",
    "PD-11-ROLES",
    "PD-11-PRINCIPLE",
    "PD-11-NOTE",
    "PD-11-NO-ID",
)

# --- El control negativo sobre el bloque (DEC-15, DEC-16, INV-15, INV-16) ---

# Un id de decisión (el bloque no puede nombrar ninguna).
DECISION_ID = re.compile(r"ADR-[0-9]{2,}")

# Una palabra que nombra una parte del inventario (el bloque no puede contarlas).
# La lista es deliberadamente gruesa: es un control complementario, no la
# prueba (la prueba de que el validador no fija el inventario es
# COMPORTAMENTAL: agregar una decisión y reemplazar una decisión siguen
# pasando el MISMO bloque).
INVENTORY_WORD = re.compile(
    r"\b(?:inventory|inventario|rows?|filas|entradas|count|counts|number"
    r"|n[uú]mero|total|figures?|vigentes?|obsolete|obsoletas?|excluded"
    r"|excluidas?|proposed|propuestas?)\b",
    re.IGNORECASE,
)

# Un número "desnudo": un entero que no es parte de un identificador (006-004,
# PD-11, U7, ADR-034, ... no lo son).
BARE_NUMBER = re.compile(r"(?<![\w$-])\d+(?![\w.-])")

# ---------------------------------------------------------------------------
# La tabla de referencia (un proyecto descartable, coherente)
# ---------------------------------------------------------------------------

ROW_ADR_002 = (
    "| `docs/adr/ADR-002-arquitectura-repo-fuente.md` | `vigente` |"
    " Repo fuente como única fuente de verdad. | `architect`, `orchestrator` |"
    " el propio ADR |"
)
ROW_ADR_007 = (
    "| `docs/adr/ADR-007-perfiles-de-modelos.md` |"
    " `obsoleto (reemplazado por ADR-033)` | Perfiles de modelos CDAD. |"
    " `orchestrator` | el propio ADR |"
)
ROW_ADR_033 = (
    "| `docs/adr/ADR-033-modelos-por-configuracion.md` | `vigente` |"
    " Los modelos se resuelven por configuración. | `orchestrator` |"
    " el propio ADR |"
)
ROW_ADR_034 = (
    "| `docs/adr/ADR-034-principio-general-antes-especifico.md` | `vigente` |"
    " Principio de general antes que específico. | `architect`, `reviewer` |"
    " `skills/cdad-cycle/references/design-principles.md` |"
)
ROW_ADR_034_OBSOLETE = (
    "| `docs/adr/ADR-034-principio-general-antes-especifico.md` |"
    " `obsoleto (reemplazado por ADR-035)` |"
    " Principio de general antes que específico. | `architect`, `reviewer` |"
    " `skills/cdad-cycle/references/design-principles.md` |"
)
ROW_ADR_035 = (
    "| `docs/adr/ADR-035-nueva-decision.md` | `vigente` |"
    " Una decisión aprobada nueva. | `orchestrator` | el propio ADR |"
)
ROW_MISSING_FILE = (
    "| `docs/adr/ADR-099-no-existe.md` | `vigente` |"
    " Una decisión sin archivo. | `orchestrator` | el propio ADR |"
)
ROW_OUTSIDE_ADR = (
    "| `docs/notas/ADR-100-fuera-del-directorio.md` | `vigente` |"
    " Una decisión fuera del directorio. | `orchestrator` | el propio ADR |"
)
ROW_OBSOLETE_WITHOUT_REPLACEMENT = (
    "| `docs/adr/ADR-007-perfiles-de-modelos.md` | `obsoleto` |"
    " Perfiles de modelos CDAD. | `orchestrator` | el propio ADR |"
)
ROW_OBSOLETE_MISSING_REPLACEMENT = (
    "| `docs/adr/ADR-007-perfiles-de-modelos.md` |"
    " `obsoleto (reemplazado por ADR-098)` | Perfiles de modelos CDAD. |"
    " `orchestrator` | el propio ADR |"
)
# La fila de la semilla real, con las barras sin escapar en el resumen: la
# celda de roles se lee desplazada y la fila no declara un conjunto de roles
# del vocabulario cerrado.
ROW_MALFORMED = (
    "| `docs/adr/ADR-007-perfiles-de-modelos.md` | `vigente` |"
    " Perfiles de modelos CDAD (economical | optimus | premium). |"
    " `orchestrator` | el propio ADR |"
)
ROW_RE_ENUNCIATES = (
    "| `docs/adr/ADR-036-re-enuncia-el-principio.md` | `vigente` |"
    " Una decisión que repite el texto del principio. | `orchestrator` |"
    " el propio ADR |"
)

TABLE_HEAD = """# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto.

## Decisiones vigentes

Las decisiones que gobiernan este proyecto, una fila por decisión.

| Archivo | Estado | Resumen | Roles | Referencia |
|---|---|---|---|---|
"""

TABLE_NOTE = """
**Nota.**

- El estado de una fila lo declara quien mantiene la tabla: se escribe en la
  propia fila y no se re-deriva del texto del ADR.
- La referencia es el lugar donde vive la regla que la decisión implanta: el
  propio ADR, o el archivo del skill instalable.
- Quedan fuera los ADR que todavía no están en vigor (`Proposed`): cada uno
  recibe su fila al aprobarse, y entonces esta lista se actualiza.

## Capas y boundaries

- `agents/*.md` — definición de roles.
"""

NOTE_WITHOUT_STATE_DECLARATION = """
**Nota.**

- La referencia es el lugar donde vive la regla que la decisión implanta: el
  propio ADR, o el archivo del skill instalable.

## Capas y boundaries

- `agents/*.md` — definición de roles.
"""


def table_text(rows, note: str = TABLE_NOTE, head: str = TABLE_HEAD) -> str:
    """El documento de la tabla con las filas dadas."""
    return head + "\n".join(rows) + "\n" + note


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


def block_text() -> str:
    """El bloque de la siembra dentro del validador (entre sus marcadores)."""
    text = read_document(VALIDATOR, "006-004 U7 (el bloque del validador)")
    lines = text.splitlines()
    try:
        begin = next(index for index, line in enumerate(lines) if line.startswith(BLOCK_BEGIN))
        end = next(
            index for index, line in enumerate(lines) if index > begin and line.startswith(BLOCK_END)
        )
    except StopIteration:
        return ""
    return "\n".join(lines[begin : end + 1])


def validator_helpers() -> str:
    """El encabezado del validador: sus contadores y sus helpers.

    Se USA el encabezado real (no una copia): un bloque que emplee un helper
    del validador se comporta igual aquí y en `make validate`.
    """
    text = read_document(VALIDATOR, "006-004 U7 (el validador)")
    index = text.find(HELPERS_END)
    if index < 0:
        return ""
    return text[:index]


def block_digest() -> str:
    """El digest del bloque: la prueba de que el comprobador NO se editó."""
    return hashlib.sha256(block_text().encode("utf-8")).hexdigest()


def run_block(tree: Path, tmp: Path) -> tuple[list[str], list[str], str, int]:
    """Ejecuta el bloque como PROCESO REAL sobre `tree`.

    Devuelve (códigos fallados, códigos pasados, salida completa, rc).
    """
    script = (
        validator_helpers()
        + f'\nROOT="{tree}"\ncd "$ROOT" || exit 2\n'
        + block_text()
    )
    script_file = tmp / "u7_block.sh"
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


def build_project(
    root: Path,
    rows,
    note: str = TABLE_NOTE,
    head: str = TABLE_HEAD,
    adr_files: dict | None = None,
    without_adr: tuple = (),
) -> Path:
    """Un proyecto DESCARTABLE con la tabla dada y sus archivos de decisión.

    El proyecto lleva la casa canónica del principio (el árbol instalable del
    skill) porque el bloque compara los archivos apuntados contra ella.
    """
    project = root
    adr_dir = project / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)

    canonical = project / "skills" / "cdad-cycle" / "references" / "design-principles.md"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    read_document(CANONICAL_PRINCIPLE, "006-004 U7 (la casa canónica del principio)")
    shutil.copy2(CANONICAL_PRINCIPLE, canonical)

    files = {
        "ADR-002-arquitectura-repo-fuente.md": "# ADR-002\n\n**Status**: Accepted\n",
        "ADR-007-perfiles-de-modelos.md": "# ADR-007\n\n**Status**: Superseded\n",
        "ADR-033-modelos-por-configuracion.md": "# ADR-033\n\n**Status**: Accepted\n",
    }
    files.update(adr_files or {})
    for name, body in files.items():
        (adr_dir / name).write_text(body, encoding="utf-8")

    # El archivo de la decisión del principio: se copia el real (apunta a la
    # casa canónica y NO re-enuncia su texto).
    adr_034 = ADR_DIR / "ADR-034-principio-general-antes-especifico.md"
    if adr_034.is_file():
        shutil.copy2(adr_034, adr_dir / adr_034.name)

    for name in without_adr:
        target = adr_dir / name
        if target.exists():
            target.unlink()

    (project / "docs" / "systemPatterns.md").write_text(
        table_text(rows, note=note, head=head), encoding="utf-8"
    )
    return project


# ---------------------------------------------------------------------------
# La verificación de la siembra
# ---------------------------------------------------------------------------


class TestU7SeedVerification(unittest.TestCase):
    """PD-11: la siembra se verifica en dos capas — lo duradero se valida, el
    inventario se acredita (INV-15, INV-16, DEC-15, DEC-16, E4, V-7)."""

    # -- el bloque y su disciplina -------------------------------------------

    def test_pd11_the_block_of_the_seeding_exists(self) -> None:
        """PD-11: el validador permanente lleva el bloque de la siembra.

        Es el bloque que U4 NO podía llevar (B-1): su gate corre después de la
        materialización, así que no ata esta unidad a un documento pendiente.
        """
        block = block_text()
        self.assertTrue(
            block.strip(),
            msg="006-004 U7 PD-11: el validador no lleva el bloque de la "
            "siembra (marcadores %s / %s)" % (BLOCK_BEGIN, BLOCK_END),
        )
        for code in CODES:
            self.assertIn(
                code,
                block,
                msg="006-004 U7 PD-11: el bloque no declara la comprobación %s" % code,
            )

    def test_pd11_the_block_names_no_decision(self) -> None:
        """PD-11, DEC-16, INV-16: el validador no nombra ninguna decisión.

        Control negativo sobre el bloque: un ``grep`` acotado a sus líneas no
        encuentra un id de decisión. Un upkeep lícito (aprobar una decisión que
        reemplaza a otra) no puede obligar a tocar el validador.
        """
        block = block_text()
        self.assertTrue(block.strip(), msg="006-004 U7: el bloque no existe")
        found = DECISION_ID.findall(block)
        self.assertEqual(
            [],
            found,
            msg="006-004 U7 PD-11/DEC-16: el bloque nombra una decisión "
            "(%s): el validador no puede distinguir una decisión de otra"
            % ", ".join(sorted(set(found))),
        )

    def test_pd11_the_block_fixes_no_figure_of_the_inventory(self) -> None:
        """PD-11, DEC-15, INV-15: el validador no fija ninguna figura del inventario.

        Ni el número de líneas, ni el de vigentes, ni el de obsoletas, ni el de
        excluidas: la siembra se crece con cada decisión aprobada y se cambia
        con cada reemplazo, y un validador que las fijara obligaría a tocar
        los tests en cada upkeep legítimo.
        """
        block = block_text()
        self.assertTrue(block.strip(), msg="006-004 U7: el bloque no existe")
        offenders = []
        for number, line in enumerate(block.splitlines(), start=1):
            if not INVENTORY_WORD.search(line):
                continue
            bare = BARE_NUMBER.findall(line)
            if bare:
                offenders.append("línea %d: %s" % (number, line.strip()))
        self.assertEqual(
            [],
            offenders,
            msg="006-004 U7 PD-11/DEC-15: el bloque cuenta el inventario:\n%s"
            % "\n".join(offenders),
        )

    # -- el comportamiento del bloque sobre copias descartables --------------

    def test_pd11_the_block_accepts_a_coherent_table(self) -> None:
        """PD-11: el bloque pasa con una tabla coherente.

        Las siete comprobaciones duraderas se declaran (una por código) y
        ninguna falla: la tabla de referencia es coherente.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "coherent",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034],
            )
            failed, passed, output, rc = run_block(project, Path(tmp))
        self.assertEqual(
            [],
            failed,
            msg="006-004 U7 PD-11: el bloque falló con una tabla coherente:\n%s" % output,
        )
        self.assertEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque no pasó con una tabla coherente:\n%s" % output,
        )
        for code in CODES:
            self.assertIn(
                code,
                passed,
                msg="006-004 U7 PD-11: el bloque no declara %s sobre una tabla "
                "coherente (pasó: %s)" % (code, passed),
            )

    def test_pd11_the_block_rejects_a_line_pointing_to_a_missing_file(self) -> None:
        """PD-11, E4: una línea que apunta a un archivo inexistente falla.

        Es el mismo hecho que E4 exige del reviewer (la tabla desalineada): el
        comprobador lo detecta y lo nombra.
        """
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "misaligned",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034, ROW_MISSING_FILE],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-FILE",
            failed,
            msg="006-004 U7 PD-11/E4: el bloque NO detectó la línea desalineada:\n%s" % output,
        )
        self.assertIn(
            "ADR-099-no-existe.md",
            output,
            msg="006-004 U7 PD-11/E4: el bloque no nombró el archivo desalineado:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11/E4: el bloque pasó con una tabla desalineada:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_line_pointing_outside_the_adr_dir(self) -> None:
        """PD-11: una línea que apunta fuera de ``docs/adr/`` falla."""
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "outside",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034, ROW_OUTSIDE_ADR],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-FILE",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó la línea fuera de "
            "docs/adr/:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con una línea fuera de "
            "docs/adr/:\n%s" % output,
        )

    def test_pd11_the_block_rejects_an_obsolete_line_without_replacement(self) -> None:
        """PD-11: una línea obsoleta que no nombra reemplazo falla."""
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "no_replacement",
                [ROW_ADR_002, ROW_OBSOLETE_WITHOUT_REPLACEMENT, ROW_ADR_033, ROW_ADR_034],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-REPLACEMENT",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó la línea obsoleta sin "
            "reemplazo:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con una línea obsoleta sin "
            "reemplazo:\n%s" % output,
        )

    def test_pd11_the_block_rejects_an_obsolete_line_whose_replacement_is_missing(self) -> None:
        """PD-11: una línea obsoleta cuyo reemplazo NO existe falla."""
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "missing_replacement",
                [ROW_ADR_002, ROW_OBSOLETE_MISSING_REPLACEMENT, ROW_ADR_033, ROW_ADR_034],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-REPLACEMENT",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó el reemplazo "
            "inexistente:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con un reemplazo inexistente:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_role_outside_the_vocabulary(self) -> None:
        """PD-11: un rol fuera del vocabulario cerrado falla."""
        bad_role_row = ROW_ADR_002.replace("`orchestrator`", "`product-owner`")
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "bad_role",
                [bad_role_row, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-ROLES",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó el rol fuera del "
            "vocabulario:\n%s" % output,
        )
        self.assertIn(
            "product-owner",
            output,
            msg="006-004 U7 PD-11: el bloque no nombró el rol inválido:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con un rol inválido:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_line_whose_shape_is_broken(self) -> None:
        """PD-11: una línea que no respeta la forma declarada falla.

        Una fila cuyo resumen trae barras sin escapar desplaza la celda de
        roles: la fila ya no declara un conjunto de roles del vocabulario
        cerrado, y el comprobador lo reporta (no lo salta).
        """
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "broken_shape",
                [ROW_ADR_002, ROW_MALFORMED, ROW_ADR_033, ROW_ADR_034],
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-ROLES",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó la línea con la forma "
            "rota:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con una línea de forma rota:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_file_that_re_enounces_principle(self) -> None:
        """PD-11, DEC-16: un archivo apuntado que re-enuncia el principio falla.

        La casa única se extiende a las líneas: el bloque comprueba el texto
        normativo del principio contra cada archivo que una línea apunta.
        """
        canonical = read_document(
            CANONICAL_PRINCIPLE, "006-004 U7 (la casa canónica del principio)"
        )
        paragraphs = []
        for label in ("**The principle.**", "**The limit.**"):
            start = canonical.find(label)
            self.assertNotEqual(-1, start, msg="la casa canónica no declara %s" % label)
            rest = canonical[start + len(label) :]
            end = rest.find("\n**")
            paragraphs.append(rest[: end if end != -1 else len(rest)])
        reenunciation = "\n\n".join(paragraphs)

        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "re_enunciation",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034, ROW_RE_ENUNCIATES],
                adr_files={"ADR-036-re-enuncia-el-principio.md": reenunciation},
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-PRINCIPLE",
            failed,
            msg="006-004 U7 PD-11/DEC-16: el bloque NO detectó el archivo que "
            "re-enuncia el principio:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11/DEC-16: el bloque pasó con un archivo que "
            "re-enuncia el principio:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_note_without_the_state_declaration(self) -> None:
        """PD-11, D-3: una nota que no declara quién declara el estado falla."""
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "no_note",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034],
                note=NOTE_WITHOUT_STATE_DECLARATION,
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-NOTE",
            failed,
            msg="006-004 U7 PD-11/D-3: el bloque NO detectó la nota sin la "
            "declaración del estado:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11/D-3: el bloque pasó sin la nota que declara "
            "quién declara el estado:\n%s" % output,
        )

    def test_pd11_the_block_rejects_a_section_that_is_not_the_first_h2(self) -> None:
        """PD-11: la sección de decisiones tiene que ser el primer H2."""
        head = """# System Patterns

Convenciones técnicas, patrones, y reglas estructurales del proyecto.

## Convenciones de código

- Una convención.

## Decisiones vigentes

Las decisiones que gobiernan este proyecto, una fila por decisión.

| Archivo | Estado | Resumen | Roles | Referencia |
|---|---|---|---|---|
"""
        with tempfile.TemporaryDirectory() as tmp:
            project = build_project(
                Path(tmp) / "not_first",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034],
                head=head,
            )
            failed, _passed, output, rc = run_block(project, Path(tmp))
        self.assertIn(
            "PD-11-SECTION",
            failed,
            msg="006-004 U7 PD-11: el bloque NO detectó que la sección no es el "
            "primer H2:\n%s" % output,
        )
        self.assertNotEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque pasó con la sección fuera del "
            "primer H2:\n%s" % output,
        )

    # -- el cierre del comprobador (E4, V-7) ---------------------------------

    def test_pd11_e4_v7_closure_of_the_checker(self) -> None:
        """PD-11, E4, V-7: el cierre del comprobador, con el MISMO bloque.

        Tres casos sobre copias descartables, ejecutados con el mismo bloque y
        sin editarlo: (i) una línea desalineada ⇒ falla; (ii) una decisión
        aprobada nueva ⇒ pasa; (iii) una decisión reemplazada expresamente ⇒
        pasa. El digest del bloque se mide antes y después de los tres: es la
        prueba de que el comprobador no se editó para admitir el reemplazo.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            digest_before = block_digest()

            # (i) una línea que apunta a un archivo inexistente ⇒ falla
            misaligned = build_project(
                tmp_path / "case_i",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034, ROW_MISSING_FILE],
            )
            failed_i, _passed_i, output_i, rc_i = run_block(misaligned, tmp_path)

            # (ii) una decisión aprobada nueva (archivo + fila) ⇒ pasa
            added = build_project(
                tmp_path / "case_ii",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034, ROW_ADR_035],
                adr_files={"ADR-035-nueva-decision.md": "# ADR-035\n\n**Status**: Accepted\n"},
            )
            failed_ii, _passed_ii, output_ii, rc_ii = run_block(added, tmp_path)

            # (iii) una decisión reemplazada expresamente ⇒ pasa (el archivo
            # de la decisión reemplazada se conserva: el reemplazo cambia la
            # fila, no borra el documento)
            replaced = build_project(
                tmp_path / "case_iii",
                [ROW_ADR_002, ROW_ADR_007, ROW_ADR_033, ROW_ADR_034_OBSOLETE, ROW_ADR_035],
                adr_files={"ADR-035-nueva-decision.md": "# ADR-035\n\n**Status**: Accepted\n"},
            )
            failed_iii, _passed_iii, output_iii, rc_iii = run_block(replaced, tmp_path)

            digest_after = block_digest()

        self.assertIn(
            "PD-11-FILE",
            failed_i,
            msg="006-004 U7 E4: el bloque NO detectó la tabla desalineada:\n%s" % output_i,
        )
        self.assertNotEqual(0, rc_i, msg="006-004 U7 E4: el bloque pasó con la tabla desalineada")

        self.assertEqual(
            [],
            failed_ii,
            msg="006-004 U7 PD-11: el bloque falló al agregar una decisión "
            "aprobada (el validador no puede fijar el inventario):\n%s" % output_ii,
        )
        self.assertEqual(0, rc_ii, msg="006-004 U7 PD-11: el bloque no pasó al agregar una decisión aprobada")

        self.assertEqual(
            [],
            failed_iii,
            msg="006-004 U7 PD-11/DEC-16: el bloque falló al reemplazar "
            "expresamente una decisión (el validador no puede distinguir una "
            "decisión de otra):\n%s" % output_iii,
        )
        self.assertEqual(0, rc_iii, msg="006-004 U7 PD-11/DEC-16: el bloque no pasó al reemplazar una decisión")

        self.assertEqual(
            digest_before,
            digest_after,
            msg="006-004 U7 V-7: el bloque cambió entre los tres casos "
            "(digest antes: %s, después: %s): el comprobador no puede "
            "editarse para admitir el reemplazo" % (digest_before, digest_after),
        )

    # -- el gate de la unidad -------------------------------------------------

    def test_pd11_the_block_passes_on_the_live_table(self) -> None:
        """PD-11: el bloque pasa con la tabla viva ya materializada.

        Éste es el gate de la unidad (plan §3, ficha U7): el bloque de la
        siembra pasa sobre la tabla viva del proyecto y sobre su directorio de
        decisiones.
        """
        with tempfile.TemporaryDirectory() as tmp:
            failed, _passed, output, rc = run_block(REPO_ROOT, Path(tmp))
        self.assertEqual(
            [],
            failed,
            msg="006-004 U7 PD-11: el bloque de la siembra falló con la tabla "
            "viva:\n%s" % output,
        )
        self.assertEqual(
            0,
            rc,
            msg="006-004 U7 PD-11: el bloque de la siembra no pasó con la "
            "tabla viva:\n%s" % output,
        )


if __name__ == "__main__":
    unittest.main()
