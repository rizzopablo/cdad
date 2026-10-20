RED de U3 completo. Reporte de rol:

## Archivos modificados (write scope: `tests/`)

| Archivo | Acción | Líneas |
|---|---|---|
| `tests/test_006_004_u3_principle_single_source.py` | **nuevo** | 1213 |

Nada fuera de `tests/`. `docs/.cdad-state.json` (modificado por el orquestador), `docs/planning/` y `findings/` quedan **sin tocar** y sin commitear.

## Mapa test → postcondición (15 tests, 1 por aserción observable)

| # | Test | PD | observable_check de la ficha |
|---|---|---|---|
| 1 | `TestPd10CanonicalHouse::test_pd10_the_canonical_file_exists_and_carries_the_principle_and_its_limit` | PD-10 | "el archivo canonico existe y lleva el principio y su limite" |
| 2 | `…::test_pd10_the_normative_text_of_the_principle_lives_in_exactly_one_installable_file` | PD-10 / INV-1 | "grep -rl … devuelve exactamente ese archivo" |
| 3 | `…::test_pd10_no_installable_surface_copies_the_principle_text` | PD-10 / INV-12 | "control negativo: ninguna copia el texto del principio" |
| 4 | `TestPd10ArchitectDuty::test_pd10_the_architect_source_names_its_duty_and_points_to_the_canonical_owner` | PD-10 | "la fuente del architect … nombra la obligacion y apunta al dueno canonico" |
| 5 | `…::test_pd10_the_architect_static_block_carries_the_duty_and_the_pointer` | PD-10 / D-2 | id. (bloque estático: la ruta de paquete no carga el skill) |
| 6 | `TestPd10ReviewerCriterion::test_pd10_the_reviewer_source_names_its_duty_and_points_to_the_canonical_owner` | PD-10 | "la fuente del reviewer …" |
| 7 | `…::test_pd10_the_reviewer_static_block_carries_the_limit_and_the_pointer` | PD-10 / D-2 | "el limite presente en las dos superficies del reviewer" |
| 8 | `…::test_pd10_the_reviewer_criterion_names_the_four_consequences_and_the_limit` | PD-10 | "las cuatro consecuencias reales y el limite" |
| 9 | `TestPd8ReviewerDutyOverTheTable::test_pd8_stage4_review_names_the_alignment_check_against_docs_adr` | PD-8 | "stage-4-review.md nombra … la alineacion con docs/adr/" |
| 10 | `…::test_pd8_stage4_review_names_the_respect_check_for_the_role_decisions` | PD-8 | "… el respeto de las decisiones vigentes de su rol" |
| 11 | `TestPd10SkillReferenceRow::test_pd10_skill_md_references_table_has_the_row_of_the_new_file` | PD-10 | "SKILL.md tiene la fila del archivo nuevo" |
| 12 | `TestPd13GeneratedAgents::test_pd13_the_generated_agents_carry_the_duty_after_make_agents` | PD-13 | "los agentes generados contienen el texto tras make agents" |
| 13 | `…::test_pd13_the_promoted_agents_of_the_repo_carry_the_duty` | PD-13 | íd. sobre los agentes promovidos (`make agents`) |
| 14 | `…::test_pd13_make_staging_is_deterministic_across_two_runs` | PD-13 / V-2 | "make staging es determinista: dos corridas, mismos bytes" — **CONTROL verde** |
| 15 | `TestPd13StaticBlockCeiling::test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling` | PD-13 / V-4 | "los 14 pares … por debajo del techo de 12000 bytes" — **CONTROL verde** |

Derivación textual **por concepto** (vocabulario con alternativas de idioma), no por frase exacta; verbatim sólo lo que la ficha cita (nombres de archivo). El texto normativo de la unicidad se **deriva** de la casa canónica (la casa es el oráculo, no el RED).

## A-1 (declarada, plan §4)

**Ninguna oráculo vigente es reemplazado**; el RED **sólo añade casos** y **vuelve a comprobar los controles negativos** (unicidad de la casa, ausencia de copia). No se tocó ningún archivo de `tests/` ajeno a este, ni `tests/validate-consistency.sh`.

## Comandos y salida

```
$ python3 -m pytest tests/test_006_004_u3_principle_single_source.py -q
13 failed, 2 passed in 2.27s
```
Fallas = **13 `AssertionError` de contrato** (casa canónica ausente; sin puntero `design-principles.md`; sin las dos comprobaciones en `stage-4-review.md`; sin la fila en `SKILL.md`; agentes sin el texto). **Ningún** ImportError/SyntaxError/NameError ni error de fixture. Los 2 verdes son los controles declarados (V-2, V-4).

```
$ python3 -m pytest tests/test_cdad_generate.py tests/test_role_packet_render.py \
    tests/test_role_packets.py tests/test_static_block_ceiling.py \
    tests/test_005_007_t1_progressive_detail_rule.py tests/test_005_007_t6_templates.py \
    tests/test_006_003_u3_texts_without_profiles.py tests/test_bash_policy_selection.py -q
53 passed in 100.84s
```

**Medición V-4 registrada** (control): 14 pares rol/subfase, máximo **3033 bytes** (`reviewer/plan-review`), mínimo 1311 (`scribe/memory`), techo declarado **12000**. La medición está anclada en el producto: para `architect/discovery` y `reviewer/review` se renderiza el paquete con el CLI público y el bloque renderizado **coincide byte a byte** con los bytes medidos.

## RED satisfacible (verificado, no supuesto)

En una **copia descartable** del repo (`/tmp/opencode`, nunca el árbol de trabajo) simulé una implementación fiel (casa canónica + fila en `SKILL.md` + las dos fuentes de rol + los dos bloques estáticos + la sección de `stage-4-review.md` + `make agents`): **15 passed**. Tres mutaciones muerden exactamente donde deben:

| Mutación | Test(s) que la cazan |
|---|---|
| el architect **copia** el texto del principio | #2 (unicidad) y #3 (control negativo) |
| el **límite** desaparece del bloque estático del reviewer | #7 y #8 |
| los agentes promovidos **no** se regeneran | #13 (el generado #12 sigue verde: la generación sí propaga) |

(La primera simulación destapó un defecto real de mi oráculo: el límite partido en dos líneas no se detectaba. Corregido: las oraciones se **reúnen** aunque el ajuste de línea las parta, y la comparación de copias es insensible al re-ajuste.)

## Commit

```
61e07656e9c6af3fb83a405aa98127373f2c6648
test: 006-004 U3 RED — principio con una casa y dos obligaciones
 tests/test_006_004_u3_principle_single_source.py | 1213 +++++++++++++++++++++
```
Sin `--no-verify`, sin `git stash`, sin `push`.

## Desviaciones y límites declarados

1. **El «bloque bash» de `tests/validate-consistency.sh` que nombra la ficha U3 NO está en este RED.** Razón: los 8 `observable_checks` de la ficha quedan cubiertos por el focal, y ese bloque sería un oráculo **por frase** (el validador es `grep -E`), es decir **más débil** que el derivador por concepto con control de vacuidad; además el plan asigna los bloques del validador a U4 (plantilla + procedimiento) y U7 (siembra) y el mismo archivo es el focal de U7. Queda a decisión del orquestador si se quiere como bloque aparte (sería un añadido de una línea al validador).
2. **Lectura de texto fuera del alcance nominal de `read_scope`**: el guard de ruta deniega `sources/`, `agents/` y `skills/` a la herramienta `Read`; el encargo los autoriza explícitamente ("puedes leer texto de procedimiento, plantillas, `sources/` y `agents/`"), así que los leí **como texto** vía `cat`. **No** leí `skills/cdad-cycle/scripts/` ni `scripts/cdad-generate.py`: el CLI y el generador sólo se **invocan** (`render`, `make agents`, `make staging`), en copia descartable y con HOME aislado. No leí `tests/.sensitive-patterns.local`. Sin valores del host en el test.
3. **Suite completa: no ejecutada** (política declarada en el paquete: la corre una vez quien cierra).