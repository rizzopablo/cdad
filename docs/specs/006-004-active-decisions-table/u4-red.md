RED de U4 completo. Reporte de rol:

## Archivos modificados (write scope: `tests/`)

| Archivo | Acción | Líneas |
|---|---|---|
| `tests/test_006_004_u4_decisions_table.py` | **nuevo** | 701 |
| `tests/validate-consistency.sh` | **modificado** (bloque de texto de la unidad) | +123 |

Nada fuera de `tests/`. `docs/.cdad-state.json` (modificado por el orquestador), `docs/planning/` y `findings/` quedan **sin tocar** y sin commitear.

## Mapa test → postcondición (9 tests, 1 por aserción observable)

| # | Test | PD | observable_check de la ficha |
|---|---|---|---|
| 1 | `TestPd7TemplateSection::test_pd7_the_template_carries_the_decisions_section_as_its_first_h2` | PD-7 | "la plantilla contiene la seccion y esta en el lugar declarado" |
| 2 | `…::test_pd7_the_section_of_the_template_carries_the_row_shape_and_the_note` | PD-7 | íd. (la sección declara la **forma de la fila** y la **nota**: exclusiones + quién declara el estado — plan U4, archivos) |
| 3 | `TestPd7ExitGateControl::test_pd7_the_exit_gate_of_stage_5_did_not_gain_checkboxes` | PD-7 / PD-8 | "control negativo: el exit gate de stage 5 no ganan casillas" — **CONTROL verde** |
| 4 | `TestPd8Upkeep::test_pd8_stage5_merge_names_the_upkeep_of_the_table` | PD-8 | "stage-5-merge.md nombra el upkeep (agregar la fila al aprobar un ADR; marcar la anterior como obsoleta)" |
| 5 | `TestPd9CasRule::test_pd9_reentry_step3_declares_the_general_cas_by_base_rule` | PD-9 / DEC-13 | "re-entry.md, paso 3 MATERIALIZE, declara la regla general del CAS" (6 conceptos: digest base · nunca el actual · re-despacho con paquete nuevo · sobre la base nueva · sin fusión a mano · sin actualizar el digest esperado) |
| 6 | `…::test_pd9_reentry_scribe_section_declares_the_case_of_the_table` | PD-8 / PD-9 | "re-entry.md, seccion Scribe, declara el caso de la tabla: dos escritores, el orquestador escribe sus filas directamente en docs/ con su commit, el del scribe llega por materializacion" |
| 7 | `TestU4TextBlock::test_pd7_pd8_pd9_the_text_block_of_u4_passes_on_the_tree` | PD-7 / PD-8 / PD-9 | "el bloque de texto de la plantilla y de las dos referencias **pasa**" (proceso real: `bash` sobre el bloque, con el encabezado real del validador) |
| 8 | `…::test_pd7_pd8_pd9_the_text_block_of_u4_does_not_require_the_live_table_nor_adr_034` | B-1 | "el bloque NO exige la tabla viva ni el ADR-034" — **CONTROL verde** |
| 9 | `…::test_pd7_pd8_pd9_the_text_block_of_u4_behaves_the_same_without_the_seed` | B-1 | íd., **por proceso**: el bloque da el **mismo** resultado con y sin la semilla (dos árboles descartables) — **CONTROL verde** |

Derivación textual **por concepto** (vocabulario ES/EN, con ventana de vecindad y sin cruzar punto), **no por frase exacta**; verbatim sólo lo que la ficha cita (nombres de archivo). El exit gate se compara contra **7 casillas medidas** sobre el árbol previo a la feature.

## A-1 (declarada, plan §4)

**Ninguna oráculo vigente es reemplazado.** El RED **sólo añade casos** al validador (bloque nuevo, entre marcadores) y **vuelve a comprobar los controles negativos** (el exit gate intacto; el bloque no exige la semilla; el bloque no nombra ningún ADR). No se tocó ningún archivo de `tests/` ajeno a este ni al bloque propio de la unidad.

## Comandos y salida

```
$ python3 -m pytest tests/test_006_004_u4_decisions_table.py -q
6 failed, 3 passed in 1.70s
```
Fallas = **6 `AssertionError` de contrato** (plantilla sin sección / sin forma de fila / sin nota; §5.4 sin upkeep; paso 3 sin la regla del CAS; §Scribe sin el caso de la tabla; el bloque de texto falla). **Ningún** ImportError/SyntaxError/NameError ni error de fixture. Los 3 verdes son los controles declarados.

```
$ python3 -m pytest tests/test_005_006_t2_intake.py tests/test_005_006_t5_acceptance.py \
    tests/test_004_002_t1_policy.py tests/test_003_002_t2_reviewfix.py \
    tests/test_006_005_u7_scribe_role_report.py tests/test_role_packets.py -q
54 passed in 60.15s
```

```
$ bash tests/validate-consistency.sh          # make validate
Assert PASS: 169
Assert FAIL: 7      → 6 de la unidad U4 + 1 PREEXISTENTE (F011: deriva árbol instalado vs repo)
```
Medido **antes** de mi cambio: `Assert PASS: 168 / Assert FAIL: 1` (el F011 ya fallaba; es deriva de despliegue, ajena a U4).

**Validación ampliada** (el validador es contrato compartido): `tests/test_006_002_u4_skill_without_models.py`, `test_006_003_u3_texts_without_profiles.py`, `test_006_002_u6_context_discipline.py`, `test_005_004_t4_cc_guard_decisions.py`, `test_003_003_t4_fixtures.py`, `test_003_004_t2_reconcile.py`, `test_006_003_u8_acceptance.py` → **51 passed, 1 failed** (ver la consecuencia declarada).

## RED satisfacible (verificado, no supuesto)

En una **copia descartable** (`/tmp/opencode/u4-green-sim`, nunca el árbol de trabajo) simulé un GREEN fiel (sección en la plantilla + upkeep en §5.4 + regla del CAS en el paso 3 + caso de la tabla en §Scribe): **9 passed**. La simulación destapó un defecto real de mi oráculo (el `awk` del bloque no quitaba el espacio tras los `#`, y las secciones `5.4`/`Scribe` no se encontraban): **corregido** antes de entregar.

Ocho mutaciones, **todas cazadas**:

| Mutación | Test(s) que la cazan |
|---|---|
| la sección de la plantilla no es el primer H2 | #1 (+#7) |
| la sección pierde la nota (quién declara el estado) | #2 (+#7) |
| el exit gate gana una casilla | #3 (+#7) |
| §5.4 deja de marcar la fila anterior como obsoleta | #4 (+#7) |
| el paso 3 usa el digest **actual** en vez del **base** | #5 (+#7) |
| §Scribe deja de declarar los dos escritores | #6 (+#7) |
| el bloque exige la tabla viva (la semilla) | #8, #9 (+#7) |
| el bloque nombra un ADR (identidad) | #8, #9 (+#7) |

## Consecuencia declarada (no oculta)

El bloque de texto vive en `tests/validate-consistency.sh` (el plan §3 ficha U4 lo declara archivo de la unidad y su RED lo incluye), de modo que **`make validate` queda rojo durante el RED** y vuelve a verde con el GREEN. Efecto colateral **medido**: la prueba de puerta verde de una unidad cerrada — `tests/test_006_003_u8_acceptance.py::TestPd8bMakeValidate::test_pd_8b_make_validate_passes_on_the_acceptance_install` — queda **roja** mientras falte la implementación; **medí que estaba verde antes de mi cambio** (con el validador de HEAD) y **no se toca ni se sustituye**: su oráculo («el validador pasa») no cambia.

## Commit

```
26b05ed7cecf2f96b3bcc86f948bf015285c0fb3
test: 006-004 U4 RED — tabla y upkeep en plantilla y procedimiento
 tests/test_006_004_u4_decisions_table.py | 701 +++++++++++++++++++++++
 tests/validate-consistency.sh            | 123 ++++++
```
Sin `--no-verify`, sin `git stash`, sin `push`.

## Desviaciones y límites declarados

1. **Suite completa: no ejecutada** (política del paquete: la corre una vez quien cierra).
2. **Lectura de texto fuera del alcance nominal de `read_scope`**: el encargo autoriza explícitamente leer texto de procedimiento y plantillas (`sources/`, `agents/`, `skills/…/references`, `assets/memory-bank-templates`); leí **sólo texto** de esas superficies. **No** leí `skills/cdad-cycle/scripts/` (ni lo copia el RED a los árboles descartables: `COPIED_SKILL_PATHS` excluye `scripts/`), no leí `tests/.sensitive-patterns.local`, y el test no contiene valores del host (todo es relativo al repo o a `tempfile`).
3. **La semilla de los árboles descartables es simulada** (U5 es su producto y todavía no existe): una sección de decisiones vigentes y un ADR-034 de ejemplo. Lo que se comprueba no es el contenido de la semilla, sino que **el bloque no dependa de ella**.
4. **Oráculos que no se tocan**: `make validate` conserva sus 168 asserts previos (el bloque **agrega** 7: 6 de contenido + 1 control del exit gate); el exit gate de stage 5 conserva sus 7 casillas; la subfase del reviewer no se toca; los agentes no se regeneran.
5. **Oráculo propio de la plantilla**: el *título* de la sección es libre (spec §2.5, Q5) → el RED acepta `Current decisions` o `Decisiones vigentes`; el *lugar* sí es exacto (primer H2).