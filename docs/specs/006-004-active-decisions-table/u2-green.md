GREEN de U2 de 006-004 cerrado. Informe de rol:

## Modified files (write scope: `skills/`, `scripts/`, `sources/`, `agents/`, `build/`)

| Archivo | Cambio |
|---|---|
| `skills/cdad-cycle/scripts/cdad_packet.py` | `render_packet` emite la sección aditiva `## Current decisions` (rama nueva, entre `## Contract` y el bloque de plan-task) + helper `_current_decisions_sections()` |
| `skills/cdad-cycle/references/handoff-prompts.md` | la invocación de `prepare` con la bandera `--current-decision` en la sección «Prepared packet contract» y en la plantilla del reviewer |

**No tocados:** `tests/**` (nada), `sources/**` (no aplica), `agents/**` (generados: verificado sin diff pendiente), `docs/.cdad-state.json` (del orquestador), `docs/planning/` y `findings/` (sin trackear, no míos).

## Tabla test → resultado

| Test | PD | Resultado |
|---|---|---|
| `test_pd5_the_section_is_emitted_after_contract_with_one_entry_per_row` | PD-5 | ✅ GREEN (era RED) |
| `test_pd5_without_rows_the_render_is_byte_identical_and_the_rows_add_only_the_section` | PD-5+PD-13 | ✅ GREEN (era RED) |
| `test_pd5_the_section_precedes_the_plan_task_block` | PD-5 (R-10) | ✅ GREEN (era RED) |
| `test_pd6_the_rows_travel_inside_the_package_and_the_scope_does_not_change` | PD-6 | ✅ GREEN (era RED) |
| `test_pd6_a_role_without_applicable_rows_carries_no_section` | PD-6 (control) | ✅ GREEN (ya verde) |
| `test_pd13_the_vigente_section_presence_oracles_stay_green_with_the_new_section` | PD-13 (control) | ✅ GREEN (ya verde) |
| 6 regresiones de la ficha (render/packets/plan-review/t6/reviewfix/prepare) | — | ✅ 53 passed |
| 8 archivos ampliados (la superficie `handoff-prompts.md` tiene oráculos vivos propios) | — | ✅ 59 passed |
| `tests/test_006_004_u1_decisions_field.py` (U1, dependencia) | — | ✅ green |
| `tests/test_static_block_ceiling.py` | PD-13 | ✅ 2 passed |
| `make validate` | gate | ⚠️ 168 PASS / 1 FAIL — **F011 ambiental** (declarado abajo) |

## Comandos y salida

```
$ python3 -m pytest tests/test_006_004_u2_decisions_section.py -v
6 passed in 3.26s
```
```
$ python3 -m pytest tests/test_role_packet_render.py tests/test_role_packets.py \
    tests/test_004_003_t2_plan_review.py tests/test_005_003_t6_packet_contract.py \
    tests/test_004_003_t1_reviewfix.py tests/test_packet_prepare.py -q
53 passed in 136.99s (0:02:16)
```
```
$ python3 -m pytest tests/test_006_006_u3_review_route_and_gate.py tests/test_006_002_u6_context_discipline.py \
    tests/test_006_002_u2_neutral_skill.py tests/test_006_002_u4_skill_without_models.py \
    tests/test_006_003_u5p_no_family_requirement.py tests/test_006_003_u3_texts_without_profiles.py \
    tests/test_005_005_t2_docs_policy.py tests/test_006_004_u1_decisions_field.py -q
59 passed in 17.17s
```
```
$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
PASS: F011: tests/validate-odoo-specialization.sh → PASS
```
```
$ bash scripts/validate-subagents.sh
DRIFT: differs <home>/.claude/skills/cdad-cycle/references/handoff-prompts.md
DRIFT: differs <home>/.claude/skills/cdad-cycle/assets/packet-request.schema.json
[... ] Check: FAIL — missing staged agents/opencode/cdad-orchestrator.md missing staged agents/opencode/cdad-reviewer.md
```

**F011 — declaro el origen ambiental (no lo introduzco).** Es el mismo 168/1 que ya registró el RED de U2 (`u2-red.md` §3). La causa es que el **producto instalado en HOME está atrasado respecto del repo**: el DRIFT nombra `assets/packet-request.schema.json` (de U1, que yo no toqué) y dos agentes opencode faltantes en el árbol instalado — la deriva es anterior a mi cambio y mi commit sólo suma dos archivos más a esa misma lista. Instalar en HOME está fuera de mi alcance de escritura (y el encargo prohíbe leer/escribir la instalación de HOME), así que lo reporto en vez de rodearlo. `tests/` no forma parte del árbol instalable: mi cambio no lo afecta.

**Bloque estático:** no lo pide la ficha de U2 (es gate de U3) y mi cambio no toca las fuentes del bloque; `test_static_block_ceiling.py` queda verde (2 passed).

**`make agents`:** la ficha de U2 no toca `sources/` ni el generador, así que no hay que regenerar. Verificado de todos modos: `make staging` produce `build/staging/agents/opencode/cdad-*.md` **byte-idéntico** a `agents/` (cero archivos `DIFF`) ⇒ no queda diff pendiente de agentes.

## Muestra de la sección emitida

```
## Current decisions

- Decision: docs/adr/ADR-001-decision-fixture.md
  - state: vigente
  - summary: Resumen de la decision que gobierna al rol.
  - roles: test-writer, reviewer
  - reference: skills/cdad-cycle/references/design-principles.md
```

## Commit

```
$ git commit -m "feat: 006-004 U2 — seccion aditiva del render"
[main bf2b69b] feat: 006-004 U2 — seccion aditiva del render
 2 files changed, 42 insertions(+), 1 deletion(-)

skills/cdad-cycle/references/handoff-prompts.md
skills/cdad-cycle/scripts/cdad_packet.py
```
Sin `--no-verify`, sin `git stash`, sin `push`. Tras el commit, el árbol sólo muestra `docs/.cdad-state.json` (del orquestador) y los sin-trackear ajenos.

## Notas de honestidad

- **A-1: ninguna.** No toqué ni sustituí ningún oráculo vigente: el RED sólo añadió casos, y la forma de las secciones se sigue comprobando por presencia. Los controles negativos del RED (lista vacía, rol sin filas) siguen verdes.
- **Aditividad (R-9/PD-5):** comprobada dentro de la misma revisión — sin el campo y con `[]` el render es byte-idéntico; con filas la sección es lo único que se añade. El RED no afirma nada entre revisiones.
- **Suite completa:** no la corrí. La política declarada en el paquete dice que la corre **quien cierra**, una vez; y la ficha de U2 no la pide. Anoto, sin extrapolar, que `references/stage-3-tdd.md` §"Test evidence policy" (2)催促 la suite completa cuando el cambio toca el renderer — este cambio lo toca —: quien cierre debe correrla.
- **Riesgo residual, sin medir:** `cdad_result.py` re-renderiza el paquete publicado en `receive` y en `_load_run_binding` y compara bytes; ambos chemins validan el request antes de renderizar, así que las filas llegan ya validadas. En el modo `late` (`cdad_result.py`:563) la validación se omite y el render consume las filas del `REQUEST.json` ya publicado; una fila malformada ahí produciría un `KeyError` en vez de un diagnóstico `rc=2`. No lo toqué porque el contrato declarado de U2 es el render y ese camino queda fuera de la ficha; lo dejo declarado por si el reviewer lo quiere acotado.