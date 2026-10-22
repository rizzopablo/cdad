The RED is delivered and committed. Here is the role report.

---

# 006-004 B-1 — RED del test-writer (subfase `red`)

## 1. Qué se entregó

El RED del hallazgo **B-1** de la revisión de etapa 4 (`docs/specs/006-004-active-decisions-table/review.md`:9-28): la plantilla del Memory Bank trae una fila de ejemplo `vigente` que apunta a `docs/adr/ADR-NNN-<slug>.md`; el bootstrap la copia y un proyecto sin ADR nace declarando una decisión inexistente.

**Archivo nuevo (único):** `tests/test_006_004_b1_template_empty.py` (458 líneas, 3 casos). No toqué `tests/test_006_004_u4_decisions_table.py` ni `tests/test_006_004_u7_seed_verification.py` (el bloque permanente que se usa es el de U7, se **ejecuta**, no se modifica).

## 2. Mapa test → postcondición

| # | Test | PD | Estado hoy |
|---|---|---|---|
| 1 | `test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row` | **PD-7 / E5** | **FALLA** (fila de datos) |
| 2 | `test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker` | **PD-7 / E5 / PD-11** | **FALLA** (`PD-11-FILE`) |
| 3 | `test_b1_the_template_still_declares_the_row_shape_outside_the_data_rows` | PD-7 (**control declarado**) | pasa hoy y sigue verde tras el remedio |

- **Focal 1:** la tabla de la sección tiene encabezado + separador y **cero** filas de datos.
- **Focal 2:** la plantilla copiada **literalmente** a `docs/systemPatterns.md` de un proyecto descartable **sin `docs/adr/`** → el bloque permanente de la tabla (el de U7, invocado como lo invocan los tests de U7: encabezado real del validador + `ROOT` al árbol + `U7_STANDALONE=1`) **pasa** (rc=0, sin asserts fallados).
- **Control 3:** la forma de la fila (archivo · estado · resumen · roles · referencia, por concepto con alternativas de idioma) sigue declarada **fuera** de las filas de datos.

## 3. A-1 — reformulaciones

**Ninguna reformulación hizo falta: ningún test vigente fija la fila de ejemplo.** `rg "ADR-NNN" tests/` → **0 coincidencias**. El RED **añade** un archivo y no modifica, sustituye ni invisibiliza ninguna prueba vigente. El oráculo de U4 que exige la forma de la fila y la nota en la sección (`test_pd7_the_section_of_the_template_carries_the_row_shape_and_the_note`) **sigue verde** con el remedio (la forma se explica fuera de las filas; la nota no se toca), y el caso 3 de este RED lo fija explícitamente.

**Interfaz declarada al implementador (importante):** la explicación de la fila va en **prosa**. El comprobador lee **toda** línea que empieza por `|` de la sección como fila de datos ⇒ un ejemplo escrito como tabla (o en un bloque cercado con barras) se leería como una fila y fallaría por archivo inexistente.

## 4. Comandos y salida

```sh
cd <home>/clawd/projects/cdad/cdad
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_004_b1_template_empty.py -v
```
```
FAILED ...test_b1_the_table_of_the_template_has_a_header_a_separator_and_no_data_row
E  AssertionError: Lists differ: [] != ['| `docs/adr/ADR-NNN-<slug>.md` | `vigente` | one line: what the decision decides | `architect`, `reviewer` | `skills/cdad-cycle/references/<file>.md` |']
FAILED ...test_b1_the_template_copied_into_a_project_without_adrs_passes_the_permanent_checker
E  AssertionError: Lists differ: [] != ['PD-11-FILE']
E    FAIL: 006-004 U7 PD-11-FILE: the line points to a file that does not exist: docs/adr/ADR-NNN-<slug>.md
E    PASS: ... PD-11-SECTION / PD-11-REPLACEMENT / PD-11-ROLES / PD-11-PRINCIPLE / PD-11-NOTE / PD-11-NO-ID
2 failed, 1 passed in 0.24s
```

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider tests/test_006_004_*.py -q
→ 2 failed, 54 passed in 26.25s        # los 2 fallidos son los focales nuevos; los 53 preexistentes + 1 control, verdes
```
```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/opencode python3 -m pytest -p no:cacheprovider \
  tests/test_005_006_t2_intake.py tests/test_005_006_t5_acceptance.py tests/test_004_002_t1_policy.py \
  tests/test_003_002_t2_reviewfix.py tests/test_006_005_u7_scribe_role_report.py tests/test_role_packets.py -q
→ 54 passed in 57.71s                   # regresiones declaradas de la ficha: verdes
```
```sh
make validate
→ Assert PASS: 182 | Assert FAIL: 1
→ FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL   # PREEXISTENTE (la deriva árbol instalado vs repo, ya declarada en review.md:113-114)
```

**Satisfacibilidad del RED (verificada sin tocar la implementación):** con una plantilla sintética de tabla vacía + forma en prosa, el bloque permanente responde `rc=0, failed=[], passed=[PD-11-SECTION, PD-11-FILE, PD-11-REPLACEMENT, PD-11-ROLES, PD-11-PRINCIPLE, PD-11-NOTE, PD-11-NO-ID]` ⇒ el GREEN existe y es alcanzable. El arnés de esa comprobación quedó **fuera** del repo (`/tmp/opencode/b1-check/verify_green.py`).

## 5. Commit

```
4d71ccc5a7005e5729712ed16694e757efc90c1c
test: 006-004 B-1 RED — la plantilla nace sin decisiones
 tests/test_006_004_b1_template_empty.py | 458 ++++++++++++++++++++++++
```
`git status` tras el commit: sólo `M docs/.cdad-state.json` (del orquestador, no mío) y los sin trackear de `docs/planning/` y `findings/` (no míos). Sin `--no-verify`, sin `git stash`, sin `push`.

## 6. Límites declarados (honestidad)

- **No leí código de implementación.** Leí sólo: la spec, el review y el plan (raíz del contrato) y `tests/**`. La plantilla y el archivo canónico del principio aparecen en el test como **artefactos publicados** copiados en runtime (la misma superficie y el mismo patrón que los REDs de U4/U7 ya aceptados) — no como fuente de diseño. El diagnóstico del RED (la fila `ADR-NNN-<slug>.md`) ya estaba publicado en `review.md`:21.
- **No toqué** `tests/validate-consistency.sh` ni ningún archivo fuera de `tests/`.
- El `prepare` sin filas (la otra mitad del cierre de B-1) **ya está cubierto** por el RED de U2 (`test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section`); no lo dupliqué.
- El caso 3 es un **control** y hoy **pasa** (la forma ya está declarada en el encabezado): lo reporto como tal, no como focal.
- No se corrió la suite completa (política del paquete: la corre una vez quien cierra).