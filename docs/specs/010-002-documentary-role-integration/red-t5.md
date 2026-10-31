# RED T5 — 010-002-documentary-role-integration

## 0. Intake (ruta C) y validez del paquete

Identificación recibida contrastada con `REQUEST.json`, `PACKET.md` y `execution.json`:

| Verificación | Comando | Resultado |
|---|---|---|
| Contrato | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49…81abc` (coincide) |
| Request válido | `python3 -B scripts/cdad_packet.py validate-request …` | `rc=0` |
| Render canónico | `python3 -B scripts/cdad_packet.py render … > /tmp/opencode/render-010-002-red-002.md` | idéntico a `PACKET.md` (16535 bytes, `diff` rc=0) |
| Contexto | `execution.json` | `schema_version: 2` |
| Cuerpo inline | — | ausente (ruta C correcta); sin mezcla de rutas |

**Observación operativa (no bloqueante):** `docs/.cdad-state.json` declara `tdd_substage: "green"` mientras el paquete declara `substage: "red"`. El paquete es el contrato de ejecución; el state ya venía modificado (`M`) antes de esta sesión y **no lo toqué**.

## 1. Revisión medida, entorno y commit

- **Producto medido:** `HEAD` `1f3e1416` (sin cambios de producto en esta sesión).
- **Commit de los tests:** `32a9531e` — `test(010-002): RED de T5 con destinatario, transiciones y esquema`.
- **Entorno:** Python `3.13.5`, pytest `8.3.5`, `jsonschema 4.19.2` (motor real resuelto).
- **Selección focal:** `-k 'TestAgentBinding or TestRequestSchema'`.
- **Salidas completas:** `/tmp/opencode/red-010-002-t5/{focal,u1c,u1b,u2,recovery,t2}.log` (fuera del repositorio).

## 2. Archivos modificados (solo `tests/`)

| Archivo | Cambio |
|---|---|
| `tests/test_010_002_documentary_role_integration.py` | Nuevos grupos `TestAgentBinding`, `TestAgentBindingReception`, `TestAgentBindingWriteAheadFinalization`, `TestRequestSchema` (14 tests) |
| `tests/test_006_005_u1c_packet_agent.py` | 2 fixtures adaptados (render entre requests válidos; histórico sin ambos campos + paquete canónico reconstruido) |
| `tests/test_006_005_u1b_dispatch_entry.py` | 1 fixture adaptado (histórico sin ambos campos + paquete canónico) |
| `tests/test_006_005_u2_opencode_module.py` | 2 fixtures adaptados (variante no publicada del mismo rol; histórico sin ambos campos + paquete canónico) |
| `tests/test_010_004_t2_red.py` | A1: el request sintético con `execution_context` declara el `agent` derivado |

`docs/.cdad-state.json` (`M`) y `docs/specs/010-000-continuity-relative-root/discovery.md` (`??`) son preexistentes y **no** forman parte del commit.

## 3. Inventario nuevo y trazabilidad

| Grupo / test | PC | Sin este test, el usuario… |
|---|---|---|
| `TestAgentBinding::test_ordinary_publication_publishes_derived_agent_and_context` | PC-06/07(a) | …no sabría a qué destinatario se publicó su encargo (garantía por construcción) |
| `::test_replacement_of_historical_successor_without_agent_rederives` | PC-06/07(a) | …un reemplazo de histórico legítimo quedaría sin destinatario |
| `::test_replacement_after_stack_change_rederives_current_stack` | PC-06/07(a) | …el sucesor iría al dominio anterior |
| `::test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack` | PC-07(b)/PC-08 | …un agente de otro rol recibiría el trabajo |
| `::test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent` | PC-07(c)/PC-08 | …un encargo se despacharía a un dominio que ya no rige |
| `::test_historical_without_both_fields_records_a_new_intent_without_destination_contrast` | PC-08/P-3 | …los históricos legítimos no podrían registrar un intento nuevo |
| `::test_context_without_agent_is_rejected_on_validation_and_publication` | PC-08/O2 | …un request con contexto quedaría sin destinatario |
| `::test_agent_is_excluded_from_render_between_valid_requests` | PC-08 | …un campo de transporte rompería los bytes del render |
| `::test_identical_repetition_after_stack_change_stays_idempotent` | PC-08/P-2 | …la repetición dejaría de ser idempotente o el ledger se relajaría |
| `TestAgentBindingReception::test_reception_after_stack_change_keeps_the_static_contrast_only` | PC-08/R9 | …un cambio de dominio invalidaría la recepción de un trabajo ya despachado |
| `TestAgentBindingWriteAheadFinalization::test_write_ahead_finalization_after_stack_change_completes_once` | PC-08/P-2/N2 | …un write-ahead iniciado no podría completarse tras cambiar el stack |
| `TestRequestSchema::test_schema_accepts_valid_current_and_historical_requests` | PC-10 | …el esquema rechazaría requests válidos |
| `…::test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent` | PC-10/PC-08 | …aceptaría tipos inválidos, claves desconocidas o contexto sin agente |
| `…::test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast` | PC-10/PC-07 | …el consumidor obtendría un veredicto distinto del CLI |

## 4. Causa de cada fallo (8 RED, todos `AssertionError`)

| Test | Salida / causa |
|---|---|
| `test_context_without_agent_is_rejected_on_validation_and_publication` | `0 == 0 : PC-08/O2 violada: un request con execution_context y sin agent fue aceptado por validate-request` — **falta la regla de presencia** |
| `test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent` | `0 == 0 : PC-07(c) violada (R2): un intento nuevo con agente declarado del stack anterior fue aceptado tras cambiar solo el stack` — **falta el contraste contextual** |
| `test_replacement_after_stack_change_rederives_current_stack` | `'cdad-test-writer-odoo' != 'cdad-test-writer' : PC-06 violada (R5/P-4): el sucesor debe publicar el agente del stack VIGENTE, no una copia del anterior` — **el reemplazo copia el agente** |
| `test_replacement_of_historical_successor_without_agent_rederives` | `None != 'cdad-test-writer-odoo' : PC-06 violada (P-4/B1): el sucesor debe REDERIVAR el agente… vio None` — **copia la ausencia del predecesor** |
| `test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack` | `0 == 0 : PC-07(b) violada: validate-request aceptó un agente de otro rol (el contraste estático agente↔rol no existe o no se aplica)` |
| `test_schema_accepts_valid_current_and_historical_requests` | `Lists differ: ["Additional properties are not allowed ('agent', 'execution_context' were unexpected)"] != []` — **el asset no declara los campos** |
| `test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent` | `PC-10 violada: agent no textual no se rechazó por su TIPO…` — el rechazo observado es `additionalProperties`, no la forma corregida |
| `test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast` | `'agent' not found in {…}` — **propiedades no declaradas** |

Ningún fallo es `ImportError`, `SyntaxError`, error de fixture ni ruta inexistente.

## 5. Controles ya verdes (6, declarados como tales)

1. Publicación ordinaria genérica (`stack` null/vacío/ausente) y `odoo`: agente derivado, contexto canónico, render sin `agent`.
2. Exclusión de `agent` del render entre dos requests válidos sin contexto.
3. Intento nuevo sobre histórico sin ambos campos tras cambiar el stack (sin contraste ni derivación silenciosa).
4. Repetición idéntica tras cambiar solo el stack (bytes/estado conservados) + rechazo del identificador reutilizado con datos distintos.
5. Finalización del write-ahead del mismo intento tras cambiar solo el stack (un único registro final, identidad fija).
6. Recepción de un paquete ya despachado tras cambiar solo el stack (recibo durable; se conserva el contraste estático).

## 6. Ejecución obligatoria por archivo

| Archivo | Esperado | Observado | rc | Causa |
|---|---|---|---|---|
| `tests/test_010_002_documentary_role_integration.py -k 'TestAgentBinding or TestRequestSchema'` | 8 RED de obligaciones ausentes + 6 controles verdes | `8 failed, 6 passed, 13 deselected in 24.57s` | `1` | Contraste estático/contextual, presencia, rederivación del sucesor y esquema ausentes |
| `tests/test_006_005_u1c_packet_agent.py` | 5 verdes (2 fixtures adaptados) | `5 passed in 7.22s` | `0` | Adaptación de conservación |
| `tests/test_006_005_u1b_dispatch_entry.py` | 17 verdes (1 fixture adaptado) | `17 passed in 28.04s` | `0` | Adaptación de conservación |
| `tests/test_006_005_u2_opencode_module.py` | 19 verdes (2 fixtures adaptados) | `19 passed in 30.14s` | `0` | Adaptación de conservación (A2 incluida) |
| `tests/test_007_002_dispatch_recovery.py` | 18 verdes; **sin edición** | `18 passed in 69.35s` | `0` | M6: ningún oráculo fija la copia del agente; los fixtures de reemplazo usan `stack: None` |
| `tests/test_010_004_t2_red.py` | 6 verdes (A1) | `6 passed in 9.00s` | `0` | Adaptación de fixture A1 |

## 7. Adaptaciones de fixture (obligación anterior → nueva → razón)

- **A1 — `test_010_004_t2_red.py`:** request con `execution_context` sin `agent` → agrega `agent = cdad-test-writer` (rol + stack `None`). Razón: PC-08 exige agente cuando hay contexto; no se debilita ninguna aserción de 010-004.
- **A2 — `test_006_005_u2_opencode_module.py` (variante no publicada):** agente de rol ajeno → `cdad-test-writer-odoo` (mismo rol, coherente con `stack=odoo`) cuyo archivo publicado se retira; el diagnóstico debe atribuir el rechazo a la variante no publicada. Razón: evitar que el contraste estático preempte el rechazo. Se declara la vía nativa como obligación procedimental.
- **A3 — write-ahead:** el test vive en el módulo nuevo (`TestAgentBindingWriteAheadFinalization`); `tests/test_006_005_u6fix5_write_ahead.py` **no se editó**.
- **u1c (2 fixtures):** el render compara dos requests válidos sin contexto (R3); el histórico de recepción quita ambos campos y reconstruye `PACKET.md` con `render` (metadata sin `execution_context`).
- **u1b (1 fixture):** el histórico quita ambos campos y reconstruye el paquete canónico; el oráculo de la llave «agente» `unknown` se conserva.
- **u2 (histórico sin ambos):** quita ambos campos, reconstruye el paquete y conserva el fallback declarado/atribución histórica (P-3).
- **No apareció ningún fixture afectado no previsto.** La medición del AUDIT (M2/M3/M7) cubrió los sitios; no fue necesario detenerse por alcance.

## 8. Discrepancias declaradas (importante para el orquestador)

1. **Objetivo del paquete, ítem 9, contra el contrato aprobado.** El ítem lista «uno con solo `execution_context`» entre los **admitidos**. Eso contradice:
   - `spec.md` PC-10 («Rechaza … contexto presente sin agente») y D5 («presencia de `execution_context` exige `agent`»),
   - `plan.md` T5 («`execution_context` presente sin `agent`: rechazo»),
   - el AUDIT §11.2 (`…_rejects_…_context_without_agent`) y el propio ítem 7 del paquete.

   **Resolución aplicada:** prevalece el contrato aprobado. El test de aceptación admite los tres casos válidos (actual con ambos; histórico solo con `agent`; histórico sin ambos) y el de rechazos exige rechazar contexto sin agente. La contradicción queda registrada en el docstring del test. **Si el orquestador quisiera la lectura literal del ítem 9, requiere una corrección del contrato, no del test.**

2. **Ítem 4, «al publicar un request nuevo». ** La interfaz pública de `prepare` no acepta un agente del llamador (`spec.md` §2 D3: no se promete una rama de rechazo de agente inyectado; AUDIT §5: publicación = garantía por construcción). La coherencia contextual de la publicación se verifica por el **valor derivado** (tests 1/2); la rama observable de rechazo se verifica en `record-dispatch`. No se escribió una rama inalcanzable.

3. **`test_007_002_dispatch_recovery.py`:** se ejecutó verde y **no se editó**. M6 midió 0 oráculos de reemplazo que fijen la copia del agente; sus fixtures usan `stack: None`. Las transiciones de reemplazo de PC-06 se cubren en el módulo nuevo (lista de T5).

## 9. Límites honestos

- No se leyó código de implementación (`skills/cdad-cycle/scripts/**`); el CLI, el adaptador y el esquema se ejercieron como superficies públicas. El asset del esquema se cargó con `jsonschema` para evaluarlo, no para derivar el oráculo (el oráculo viene de PC-10/D5).
- El test de write-ahead usa el patrón público del adaptador con runtime falso; no instrumenta el instante exacto del cambio de stack más allá de esperar el registro provisional.
- Este RED no acredita fidelidad semántica ni conducta de modelos; la suite completa no se ejecutó (política del paquete: la corre el cierre).
- El commit `32a9531e` contiene solo los cinco archivos de tests; el state y el archivo no trackeado de 010-000 quedaron fuera.

## 10. Evidencia de comandos (resumen)

```
$ python3 -B -m pytest -q tests/test_010_002_documentary_role_integration.py -k 'TestAgentBinding or TestRequestSchema'
8 failed, 6 passed, 13 deselected in 24.57s   (rc=1; los 8 fallos son las aserciones del §4)

$ python3 -B -m pytest -q tests/test_006_005_u1c_packet_agent.py        → 5 passed   (rc=0)
$ python3 -B -m pytest -q tests/test_006_005_u1b_dispatch_entry.py     → 17 passed  (rc=0)
$ python3 -B -m pytest -q tests/test_006_005_u2_opencode_module.py     → 19 passed  (rc=0)
$ python3 -B -m pytest -q tests/test_007_002_dispatch_recovery.py      → 18 passed  (rc=0)
$ python3 -B -m pytest -q tests/test_010_004_t2_red.py                 → 6 passed   (rc=0)

$ git commit -m "test(010-002): RED de T5 con destinatario, transiciones y esquema"
32a9531e
```

**Estado del gate RED:** los cinco archivos previstos (más A1) fueron ejecutados; hay RED por las obligaciones comprometidas (no por fixtures rotos); las garantías por construcción y los controles de conservación están declarados verdes; reemplazo histórico, reemplazo tras cambio de stack e intento nuevo histórico están cubiertos; las adaptaciones aprobadas (A1/A2/A3 y los históricos de u1c/u1b/u2) quedaron protegidas antes de GREEN. La única discrepancia que requiere decisión del orquestador es el ítem 9 del objetivo frente a PC-10/D5 (§8.1).
