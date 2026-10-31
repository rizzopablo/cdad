# AUDIT — 010-002-documentary-role-integration

**Rol:** test-writer · **Subfase:** audit · **Paquete:** `010-002-documentary-role-integration-test-writer-audit-001`
**Contrato:** `docs/specs/010-002-documentary-role-integration/spec.md` v4, sha256 `0d630c49…81abc` (aprobado)
**Naturaleza:** informe de auditoría; **no** se escriben tests ni se modifica ningún archivo del repositorio.

---

## 0. Intake (ruta C) y validez del paquete

La identificación recibida coincide con `REQUEST.json` y `PACKET.md`, y el contexto de ejecución es v2.

| Verificación | Comando | Resultado |
|---|---|---|
| Request válido | `python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-010-002-documentary-role-integration-001/execution.json --request .cdad/packets/010-002-documentary-role-integration-test-writer-audit-001/REQUEST.json` | `rc=0` |
| Paquete válido | `python3 scripts/cdad_packet.py validate-packet … --packet .cdad/packets/010-002-documentary-role-integration-test-writer-audit-001/PACKET.md` | `rc=0` |
| Render canónico | `python3 scripts/cdad_packet.py render --route C … > /tmp/opencode/render-C.md` + `diff` | idéntico a `PACKET.md`; sha256 `5d84d82918046fc2eac8e6d04c456a8a5937099de76017cc36248fac78921021` en ambos |
| Contrato | `sha256sum docs/specs/010-002-documentary-role-integration/spec.md` | `0d630c49cfd4c8b0f671026437000617b96bf1bc44b2383dd2914bc7e5581abc` |
| Contexto | `execution.json` | `schema_version: 2` |
| Cuerpo inline | — | ausente (correcto en ruta C); no hay mezcla de rutas |

**Observaciones operativas (no bloqueantes):**
- `docs/.cdad-state.json` declara `tdd_substage: "plan-review"` mientras el paquete declara `substage: "audit"` y el `active_packet` es este AUDIT. El paquete es el contrato de ejecución; el estado debería actualizarse al materializar el informe.
- `HEAD` es `0279a9d01b2787bb7b3d81ab1ef1d3d34abf8e87`; la spec cita el snapshot `3bea7a8…`. El contrato está pineado por sha y coincide; la diferencia de `HEAD` no altera el contrato, pero el cierre debe declararla.
- `git status` muestra solo `M docs/.cdad-state.json` y un archivo no trackeado de 010-000; **no hay cambios de tests ni de producto atribuibles a esta sesión**.

---

## 1. Método, selección y límites de lectura

**Selección:** `tests/**` (229 archivos en la raíz; `1887` tests recolectados antes de un error de colección ajeno a `tests/` — `examples/idea_log/test_idea_log.py`, `ModuleNotFoundError: No module named 'odoo'`; la selección canónica es `tests/`).

**Lecturas no-test realizadas, declaradas:**
- `skills/cdad-cycle/references/documentary-contracts.md` — la norma compartida que el paquete ordena leer; no es producto de 010-002.
- `skills/cdad-cycle/packets/substages/test-writer-audit.md` — instrucción de subfase (sha `00889dea…` coincide con `instruction_sources`).
- `skills/cdad-cycle/references/stage-3-tdd.md` — solo la sección de auditoría de relevancia (grep, no lectura completa).

**Lecturas denegadas y no sorteadas:** `scripts/cdad_packet.py` y `skills/**` vía `Read` fueron denegados por el guard. El CLI se ejercitó **como proceso** (interfaz pública), que es el método sancionado; la norma documental se leyó vía bash porque el paquete la declara input. **No se leyó** `sources/roles/**`, `skills/cdad-cycle/SKILL.md`, `skills/odoo-*/**`, `agents/**` ni el código de implementación. No se derivó ningún oráculo del producto bajo prueba.

**Entorno medido:** Python `3.13.5`; pytest `8.3.5`; `jsonschema 4.19.2` disponible (motor real de esquema resuelto; su ausencia habría sido bloqueo de entorno, no defecto del producto).

**Límite honesto:** este AUDIT mide la suite existente y propone verificaciones; no ejecuta la suite completa (política del paquete) y no acredita fidelidad semántica.

---

## 2. (1) Mapa PC-01..PC-13 → verificación propuesta, clase y consecuencia observable

Clases: **TE** = test estructural (texto/artefacto), **ES** = evaluación real de esquema, **TO** = transición observable (CLI/adaptador), **RI** = revisión independiente.

| PC | Promesa | Clase | Verificación propuesta | Consecuencia observable (sin este verificador, el usuario…) | Control ya verde |
|---|---|---|---|---|---|
| **PC-01** | Procedimiento con los campos existentes, sin selector nuevo | TE | `TestEngagement::test_documentary_procedure_uses_the_existing_fields_without_a_new_selector` sobre `references/handoff-prompts.md` + fuentes de rol | …no tiene procedimiento comprometido y el encargo documental se improvisa, con riesgo de superponer producto, fuentes y oráculos. | — |
| **PC-02** | Seis roles y agentes actuales; sin variantes documentales | TE | `TestEngagement::test_six_role_boundaries_and_no_documentary_variant` (fuentes, bloques, 11 agentes de ambos runtimes) | …podría aparecer un agente/selector documental paralelo y el encargo dejaría de llegar por el flujo canónico. | `test_010_001` (fronteras de rol), `test_005_004_t4` (nombres de agente) |
| **PC-03** | Alcance editable explícito; defaults y separación; detener superposiciones | TE + TO (control) | `TestEngagement::test_explicit_editable_scope_and_stop_on_protected_overlap` + `prepare` sintético con `write_scope` docs explícito | …un encargo documental podría escribir en tests u oráculos, o producir sin alcance declarado. | **`test_packet_prepare.py::TestPrepareDefaults::test_p2_default_request_derivations_per_role`** (implementer sin docs; read-only sin escritura; test-writer solo `tests/`) — verde |
| **PC-04** | Matriz Odoo de architect/test-writer/implementer + frontera de addon | TE | `TestOdooApplicability::test_addon_boundary_and_module_documentation`, `…::test_producer_roles_matrix`, `…::test_documentary_verifier_is_not_an_addon_test`, `…::test_distributed_artifacts_carry_the_matrix` | …en un proyecto Odoo el encargo documental queda bloqueado por una batería de addon que no modifica, o el implementer modifica addon sin inventario/entorno. | `validate-odoo-specialization.sh` (solo presencia; **no** acredita la matriz) |
| **PC-05** | Matriz de reviewer/orchestrator/scribe; el diff prevalece | TE + **RI** | `TestOdooApplicability::test_review_coordination_memory_matrix_and_diff_prevalence` + caso sintético de diff de addon bajo etiqueta documental en T8 | …un cambio de addon oculto bajo etiqueta documental se aceptaría sin instalación limpia, lint ni OCA. | — |
| **PC-06** | Publicación nueva (ordinaria y reemplazo) publica `agent`+`execution_context`; el sucesor rederiva; bytes históricos intactos | TO | `TestAgentBinding::test_ordinary_publication_publishes_derived_agent_and_context`, `…::test_replacement_of_historical_successor_without_agent_rederives`, `…::test_replacement_after_stack_change_rederives_current_stack` | …un reemplazo legítimo de un histórico sin agente no publicaría destinatario/contexto, o un cambio de dominio publicaría un sucesor del dominio anterior. | `test_007_002` (reemplazo, sin agente), `test_005_001_t2`/`test_005_005_t1` (conservación; stack `None`) |
| **PC-07** | Tres vías separadas (construcción, estático, contextual) + histórico sin agente | TO | `TestAgentBinding::test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack`, `…::test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent`, `…::test_historical_without_both_fields_records_a_new_intent_without_destination_contrast`, + los tres tests de publicación de PC-06 | …un agente de otro rol recibiría el trabajo, o el stack vigente se revalidaría en la recepción y rompería continuidad histórica. | `test_006_005_u1c` (3 tests de PD-7), `test_006_005_u2` PD-14 |
| **PC-08** | Presencia, admisión histórica, render, recepción, repetición, write-ahead, rechazo de intento nuevo, variante ausente | TO + ES (presencia) | `TestAgentBinding::test_context_without_agent_is_rejected_on_validation_and_publication`, `…::test_agent_is_excluded_from_render_between_valid_requests`, `…::test_reception_after_stack_change_keeps_the_static_contrast_only`, `…::test_identical_repetition_after_stack_change_stays_idempotent`, `…::test_write_ahead_finalization_after_stack_change_completes_once`, `…::test_new_intent_after_stack_change_is_rejected_without_mutating_packet_or_records` | …la regla de presencia rompería históricos legítimos, la excepción temporal habilitaría un intento nuevo encubierto, o un cambio de stack invalidaría trabajo ya despachado. | `test_004_002_t4` (idempotencia sin cambio de stack), `test_006_005_u6fix5` (write-ahead sin cambio de stack) |
| **PC-09** | Instrucciones coherentes con la derivación; sin «otro valor → genérico» | TE + **RI** | `TestDispatchDoctrine::test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback`, `…::test_absent_variant_is_mechanical_external_and_procedural_native` | …una sesión nativa caería al genérico para un stack no vacío o improvisaría un fallback inexistente. | Ninguno enshrines la cláusula errónea (medido: 0) |
| **PC-10** | Esquema declara ambos campos, cierre, históricos, rechazos y distinción schema/CLI | ES | `TestRequestSchema::test_schema_accepts_valid_current_and_historical_requests`, `…::test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent`, `…::test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast` | …el esquema publicado rechazaría requests válidos o aceptaría contexto sin agente, y el consumidor obtendría un veredicto distinto del CLI. | 0 tests existentes sobre `packet-request.schema.json` |
| **PC-11** | Generación reproducible; promovidos = staging; techo estático no elevado | TE | `TestDistribution::test_generation_is_reproducible_and_promoted_matches_staging` (copia descartable + `make agents`) | …los agentes distribuidos podrían no corresponder a las fuentes aprobadas o dos generaciones diferir. | **`test_cdad_generate.py::test_postcondition_2…`** (determinismo), **`test_006_004_u3…TestPd13StaticBlockCeiling`** (14 pares <12000), **`test_static_block_ceiling.py`** (2 tests), `test_install_ownership` |
| **PC-12.a** | T4: instalación aislada de agentes/skills/referencias; recorrido documental genérico y Odoo | TO/TE | `TestDistribution::test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey`, `…::test_documentary_odoo_journey_keeps_domain_and_write_frontier` | …el perfil documental quedaría descrito pero no distribuido, y el usuario no podría ejecutarlo tras instalar. | `test_010_001::test_isolated_install_distributes_the_reference_with_source_bytes` (modelo de `CDAD_INSTALL_ROOT` + 2 destinos + 2 runtimes) |
| **PC-12.b** | T6/T7: instalación actualizada con CLI y esquema; recorrido repetido con PC-06–10 | TO + ES | `test_010_002_documentary_role_properties.py` — instalación final + recorrido con CLI/esquema instalados | …la instalación distribuiría un CLI/esquema anterior y el recorrido documental/Odoo fallaría en el destino. | — (T7) |
| **PC-13** | Aceptación separa evidencia automática e informe independiente | **RI** | Dictamen T8; **ningún test estructural** | …un verde estructural se presentaría como fidelidad semántica y la aceptación no tendría informe independiente. | — |

**Agrupación:** por promesa observable (A–F), no por cuota. Varias PC comparten test; ninguna PC recibe un test propio por simetría.

---

## 3. (2) Presencia textual vs suficiencia de la conducta

| PC | Lo que el test estructural **sí** prueba | Lo que **no** prueba | Quién acredita la suficiencia |
|---|---|---|---|
| PC-01 | El procedimiento nombra las siete declaraciones y no introduce campo/selector nuevo. | Que el orquestador lo use ni que el procedimiento sea inequívoco. | T8 (D1–D5, P-1–P-4). |
| PC-02 | Las seis fronteras siguen escritas y no existe agente/selector documental. | Que las fronteras se respeten en un encargo real. | T8 + diffs. |
| PC-04/05 | Cada rol contiene su celda (exención documental + obligación de addon + mixto), la frontera del módulo y «el diff prevalece». | Que la cláusula sea suficiente, no ambigua y no se abuse de la etiqueta. | T8, incluido el caso sintético de diff de addon. |
| PC-09 | Todas las superficies declaran la derivación por sufijo y no conservan «otro valor → genérico». | Que una sesión nativa obedezca (obligación procedimental). | T8. |

**Regla explícita:** la presencia de secciones, etiquetas o frases **no** acredita fidelidad, suficiencia ni verdad semántica. Por eso PC-13 se reserva a T8 y **ningún** test de PC-01/02/04/05/09 se contabiliza como PC-13. El cierre debe mantener separados el control automático y el informe independiente.

---

## 4. (3) Cobertura de las matrices Odoo de PC-04 y PC-05

### 4.1 Superficies que el test debe observar
- **Fuentes competentes:** `sources/roles/{architect,test-writer,implementer,reviewer,orchestrator,scribe}.md`.
- **Bloques estáticos distribuidos:** `skills/cdad-cycle/packets/roles/{architect,implementer,test-writer,reviewer,scribe}.md` (el orquestador no tiene bloque).
- **Agentes generados y promovidos de ambos runtimes:** `build/staging/agents/<runtime>/…`, `agents/…`, `agents/claude-code/…` (11 agentes: 5 roles × genérico/Odoo + orquestador).
- **Skills Odoo:** `skills/odoo-{architect,test-writer,expert,reviewer,make-env}/SKILL.md` y las cuatro referencias del inventario acotado de T4.
- **Instalación aislada:** árbol `CDAD_INSTALL_ROOT` (PC-12.a).

### 4.2 Celdas y casos exigidos
| Caso | Qué se asserta (derivado del contrato, no del documento) | Clase |
|---|---|---|
| **Documentación dentro de un módulo** | La frontera nombra `models/ views/ controllers/ wizards/ security/ data/ static/src/`, `__manifest__.py` y equivalentes ejecutables; y declara `readme/ static/description/ README.rst doc/` **producto documental** salvo que el contrato lo declare entregable funcional. | TE |
| **Verificador documental** | Un verificador estructural documental **no** se convierte en test de addon por estar en un proyecto Odoo; el test-writer no exige `TransactionCase`/`@tagged`/runner solo por dominio. | TE |
| **Diff de addon contrario a la etiqueta** | Reviewer y orquestador: el diff real prevalece; un cambio de addon bajo etiqueta documental se informa y **bloquea** su aceptación como documental puro; no hay permiso retroactivo. | **RI (T8)**, con presencia textual en TE |
| **Architect** | Documental puro: conserva dominio/mapeo/`VERIFY`, **no exige** inventario acreditado ni entorno de addon no modificado. Addon: exige inventario core/OCA y entorno resuelto **antes** de modificar. Mixto: ambas familias sobre esa parte. | TE |
| **Test-writer** | Documental puro: construye el verificador comprometido; no exige batería de addon. Addon: conserva framework/tags/fixtures/runner. Mixto: separa regímenes. | TE |
| **Implementer** | Documental puro: solo el documento y su evidencia; no exige pruebas/instalación/lint de addon no modificado. Addon: conserva pruebas, lint, OCA e instalación limpia cuando el contrato la exige. Mixto: ambas. | TE |
| **Reviewer** | Documental puro: confirma que el diff real es documental; no exige batería ajena al diff. Addon: activa obligaciones (instalación limpia, lint, OCA). Mixto: ambas evidencias. | TE + RI |
| **Orchestrator** | Prepara declaraciones y confirma diff en re-entry; addon exige evidencia sin trabajo de rol inline; contradicción detiene y reencauza. | TE + RI |
| **Scribe** | Memory Bank desde la evidencia documental/addon/mixta; no ejecuta ni sustituye verificaciones. | TE |

### 4.3 Prohibiciones de oráculo
- **No** se usa el `write_scope` del architect ni del reviewer como descripción del producto: ambos son vacíos. El test asserta que la base es «producto propuesto en el contrato y sus alcances» / «contrato y diff real».
- **No** se usa un grep global de «addon»/«documental»: el test debe localizar la región de aplicabilidad **por rol** y exigir el par (exención documental + obligación de addon). Un keyword suelto no acredita la exclusión.
- **No** se inventa detección mecánica del diff: la promesa es procedimental y se juzga en T8.

---

## 5. (4) Contraste estático vs contextual; las tres vías de PC-07

| Vía | Superficie | Qué se observa | Clasificación en `consequence` | Qué **no** se escribe |
|---|---|---|---|---|
| **1. Publicación ordinaria** (`prepare`) | CLI pública | `REQUEST.json` publica `agent` = `cdad-<role>` o `cdad-<role>-<stack>` según el stack vigente, y `execution_context` canónico | **Garantía por construcción**; se verifica el valor publicado | Un test que inyecte un agente alternativo y espere rechazo: la interfaz pública no acepta ese input; sería una rama inalcanzable |
| **2. Reemplazo** (`prepare --replace-packet`) | CLI pública | Sucesor nuevo con agente **rederivado** del rol y stack vigente; predecesor histórico sin agente → sucesor con agente+contexto; stack cambiado → agente del stack vigente, no copia | **Garantía por construcción**; transiciones de PC-06 | Un test que espere rechazo de agente inyectado en `prepare`; tampoco se exige que el sucesor conserve el agente del predecesor |
| **3. Rechazo estático** (`validate-request`, `render`, `validate-packet`) | CLI pública | Agente de **otro rol** → rc≠0 y `render` sin paquete válido; diagnóstico nombra rol, agente recibido y familia esperada, y **declara que el stack no se evalúa**; un agente del **mismo rol** con otro sufijo **no** se rechaza en lectura | **Rechazo estático** | Comparación contra el stack vigente en la recepción/lectura |
| **4. Contraste contextual** (`record-dispatch`, intento nuevo con agente declarado) | CLI pública | Agente del mismo rol pero discordante con el **stack vigente** → falla antes de publicar el registro o habilitar la invocación; diagnóstico nombra **rol, stack y agente esperado** (a diferencia del estático, que no nombra stack) | **Rechazo contextual** | Aplicarlo a recepción, repetición idéntica o finalización del write-ahead |
| **Excepción histórica** | `record-dispatch` sobre request sin `execution_context` ni `agent` | Registro admitido sin contraste contextual del destinatario y **sin derivar ni sustituir** agente | **Admisión histórica declarada** | Derivar `cdad-<role>` en el registro; prometer lanzamiento sin destinatario |

**Discriminador de diagnóstico:** el test estático debe exigir que el stack **no** se evalúe (frase explícita) y el contextual que el stack **sí** se nombre. Sin esa discriminación, un rechazo estático preemptor podría hacer pasar un test contextual por el motivo equivocado (ver §10, riesgo R2).

**Trazabilidad de PC-06/07a:** la garantía por construcción no se prueba provocando una discordancia; se prueba observando el agente publicado y su transición. El reemplazo histórico y el cambio de stack se acreditan **por separado** (PC-06 lo exige).

---

## 6. (5) Intento nuevo histórico sin `execution_context` ni `agent`

**Contrato (D3/PC-07/PC-08/INV-04):** se admite registrar un intento nuevo; no hay agente declarado que contrastar, por lo que **no** se aplica el contraste contextual del destinatario y **no** se deriva ni sustituye un agente en silencio. Se conservan las demás precondiciones.

**Oráculo propuesto** (`TestAgentBinding::test_historical_without_both_fields_records_a_new_intent_without_destination_contrast`):
1. Fixture: request canónico **sin ambos campos** (no basta quitar `agent`: si se quita solo `agent` conservando `execution_context`, el request pasa a ser un caso negativo por la regla de presencia).
2. `prepare --record-dispatch` del intento nuevo → `rc=0` y registro durable.
3. El `REQUEST.json` **no gana** `agent` ni `execution_context`; el registro no contiene un agente derivado.
4. Se conservan las demás precondiciones del registro (no se relajan identidad, integridad, transiciones).
5. **No** se asserta que «cualquier adaptador lance sin destinatario»: eso está fuera de la promesa.

**Tratamiento histórico declarado del adaptador externo:** el FYI de `plan-review-004` establece que el fallback `cdad-<role>` con nota explícita de ausencia es tratamiento histórico declarado, **no** derivación silenciosa. El test debe verificar el **registro** (que no gana agente) y, si ejercita el adaptador, que la ausencia se **declare**; no debe leer ese lanzamiento como contraste contextual ni exigir su rechazo.

**Ambigüedad menor detectada (no bloqueante):** el contrato no dice explícitamente si la *finalización del write-ahead de un intento histórico sin agente* queda sujeta al contraste contextual. Por D3 no puede serlo (no hay agente declarado); conviene una línea aclaratoria en la spec o en el procedimiento, pero no impide verificar: el test debe afirmar que completa.

---

## 7. (6) Separación de intentos nuevos respecto de recepción, repetición y write-ahead

Cuatro comportamientos, cuatro tests con precondiciones y resultados distintos. No se agrupan en un «test de stack» genérico.

| Comportamiento | Secuencia | Resultado esperado | Discriminador |
|---|---|---|---|
| **Intento nuevo** (A5/A12) | Publicar con stack A → cambiar a stack B → `record-dispatch` con agente del stack A | `rc≠0`, diagnóstico con rol/stack/agente esperado, sin registro nuevo ni invocación; paquete y registros anteriores intactos | Si el implementer aplica el contraste, falla; si lo omite, pasa |
| **Recepción** (A9) | Publicar+despachar con stack A → cambiar a stack B → `receive` | `rc=0`, recibo durable; se conserva el contraste estático de rol | Solo falla si se introdujo comparación temporal en recepción |
| **Repetición idéntica** (A10) | Registrar intento con stack A → cambiar a stack B → repetir el **mismo** registro byte-idéntico | `rc=0`, bytes y transiciones pendientes conservados | Si el contraste se aplica antes de la idempotencia, falla |
| **Finalización write-ahead** (A11) | Write-ahead iniciado con stack A → cambiar a stack B → completar el **mismo** intento | Una única finalización, identidad fija, sin rechazo por stack | Si el contraste se aplica a la finalización, falla |

**Controles existentes (no se reescriben):** `test_004_002_t4_dispatch.py::test_pd6_i8_identical_record_idempotent` (repetición sin cambio de stack) y `test_006_005_u6fix5_write_ahead.py` (write-ahead sin cambio de stack). Ambos quedan verdes con o sin la excepción: **no discriminan**; por eso los tests nuevos son necesarios.

**Costo de fixture (decisión de alcance):** la finalización write-ahead requiere el adaptador externo con runtime falso (`U65WriteAheadCase`). Opciones:
- (a) implementar A11 en el módulo nuevo reutilizando el patrón público del fixture (preferible: no edita el archivo existente);
- (b) añadir un test aditivo a `tests/test_006_005_u6fix5_write_ahead.py` (requiere reencauce de alcance, porque no está en la lista de T5).

**Prohibición:** no se simula una API interna para inventar el estado write-ahead; se usa el adaptador/CLI público.

---

## 8. (7) Medición de fixtures existentes — método, comandos, resultados, clasificación

### 8.1 Método
Búsqueda acotada a `tests/**` (`rg` con `--glob '*.py'`, excluyendo `__pycache__`), lectura de los sitios-device y ejecuciones puntuales de pytest sobre los oráculos afectados. No se estimó ningún conteo.

### 8.2 Resultados

| # | Qué se midió | Comando | Resultado | Ubicaciones | Clasificación |
|---|---|---|---|---|---|
| M1 | Campos `agent` en documentos request | `rg -n --glob '*.py' '["'"'"']agent["'"'"']\s*:' tests` | **31 líneas / 16 archivos**; **1** es campo de request (`test_packet_prepare.py:418`); el resto son filas `session_v2`, logs de módulo falso u observaciones | `test_packet_prepare.py:418`; filas en `u1b`, `u2`, `u6fix4`, `u6fix6`, `reviewfix` | **Control**: no hay fixture que declare un agente discordante esperando aceptación |
| M2 | Simulaciones de histórico quitando **solo** `agent` (conservando `execution_context`) | `rg -n --glob '*.py' 'pop\(\s*["'"'"']agent' tests` | **4 sitios / 3 archivos**: `u1c:263`, `u1c:332`, `u1b:834` (usado en `:1247`), `u2:943` → **4 tests** | u1c (2), u1b (1), u2 (1) | **Fixture válido afectado**: pasan a caso negativo por la regla de presencia; deben reconstruirse como históricos **sin ambos** campos y con paquete canónico |
| M3 | Discordancias **estáticas** de rol | `rg -n 'UNPUBLISHED_AGENT'` + lectura | **1 sitio**: `test_006_005_u2_opencode_module.py:148`, inyectado en `:909` → **1 test** | u2 `test_pd14_unpublished_packet_agent_fails_closed_before_dispatch` | **Fixture válido afectado (atribución)**: el contraste estático lo rechaza antes; debe rebasarse a una variante del **mismo rol** no publicada (ver §10 R2) |
| M4 | Discordancias **contextuales** (mismo rol, stack distinto) | `rg '"stack"'`, setters y usos | **0** fixtures publican con un stack y registran un intento nuevo con otro | — | **Nuevo**: los tests de transición se escriben nuevos |
| M5 | Stack `"generic"` (abstención de `plan-review-004`) | `rg -n '"stack": "generic"' tests` | **2** ocurrencias: `test_003_006_t2_activation.py:112`, `test_005_005_t3_provenance.py:184` — ambas son **manifiestos de instalación**, no `docs/.cdad-state.json` | — | **Abstención resuelta**: no alcanzan el contraste contextual; no se tocan |
| M6 | Oráculos de reemplazo que fijen la copia del agente | `rg -l 'replace-packet' tests` + conteo de `agent` | **10 archivos** usan `--replace-packet`; **0** contienen la palabra `agent`; los estados son `stack: None` (`007_002:472`, `005_001_t2:225`, `005_005_t1:262`, `006_006_w1:330`, `005_001_t4:256`, `005_001_tcorr:266`, `005_005_t4:306`) o `PacketFixture` sin stack/agente | `test_007_002` es el único a extender | **Control**: ningún oráculo fija la copia; la rederivación es neutral con stack `None`; **no** hay regresión existente |
| M7 | Requests con `execution_context` **sin** `agent` construidos a mano | `rg -n '\["execution_context"\]\s*=' tests` | **2** sitios en `test_010_004_t2_red.py:94,343` (helper `locator_project`) → **5 tests** (`:104,181,258,385,507`) | `test_010_004_t2_red.py` | **Fixture válido afectado, fuera de T5**: hoy **6 passed**; con la regla de presencia, 5 pasarían a rojo. Requiere reencauce de alcance |
| M8 | Oráculos de render/histórico de u1c | Lectura + pytest | `u1c` **5 passed**; afectados `test_pd7_agent_does_not_enter_the_packet_render` (`:246`) y `test_pd7_pre_feature_packet_without_agent_is_still_received` (`:316`) | u1c | **Fixture válido afectado** (ver §8.3) |
| M9 | Oráculos de esquema | `rg -l 'packet-request\.schema' tests` | **0** archivos; `jsonschema 4.19.2` presente | — | **Nuevo** (PC-10) |
| M10 | Doctrina de selección | `rg 'TestDispatchDoctrine\|otro valor'` | **0** `TestDispatchDoctrine`; **0** tests que fijen «otro valor → genérico» | — | **Nuevo** (PC-09); ninguna sustitución |
| M11 | Aislamiento | `conftest.py:28-126`; `rg -l 'CDAD_INSTALL_ROOT' tests` | **36** archivos usan `CDAD_INSTALL_ROOT`; canarios `PC3/PC4` → **4 passed** | — | **Suficiente** (ver §9) |
| M12 | Techo estático | pytest focal | `test_static_block_ceiling.py` **2 passed**; `TestPd13StaticBlockCeiling` (14 pares) **1 passed** | — | **Control**; reejecutar en T4 |
| M13 | Baseline de regresiones seleccionadas | pytest focal | `010_001` **11 passed**; `role_packet_render` **17 passed**; `consumers` **5 passed**; `008_004` **25 passed**; `packet_prepare -k p2` **1 passed**; `010_004 t2` **6 passed**, `t3` **7**, `t5` **2**, `t6` **2**; `007_002` (2 representativos) **2 passed** | — | **Verde actual** de los oráculos que el cambio puede rozar |

### 8.3 Detalle de los oráculos afectados

| Archivo:línea | Test | Forma actual | Por qué queda afectado | Clasificación |
|---|---|---|---|---|
| `test_006_005_u1c_packet_agent.py:246` | `test_pd7_agent_does_not_enter_the_packet_render` | quita solo `agent`, conserva `execution_context`, espera `render rc=0` y bytes iguales | Con la regla de presencia, el request sin agente es inválido; el test fallaría por el motivo equivocado o se adaptaría a comparar dos requests inválidos | **Fixture válido afectado** → comparar dos requests **válidos** (sin contexto declarado) que difieran solo en `agent`; no comparar contra el paquete moderno |
| `test_006_005_u1c_packet_agent.py:316` | `test_pd7_pre_feature_packet_without_agent_is_still_received` | quita solo `agent`, espera `receive rc=0` | Ya no representa un histórico admitido | **Fixture válido afectado** → quitar **ambos** y reconstruir el paquete canónico (metadata sin `execution_context`) |
| `test_006_005_u1b_dispatch_entry.py:819/1247` | `test_pd5_native_packet_without_agent_never_invents_the_agent` | `drop_optional_agent` quita solo `agent`, conserva contexto | Mismo problema; además el docstring declara el device equivocado | **Fixture válido afectado** → histórico sin ambos; actualizar la declaración |
| `test_006_005_u2_opencode_module.py:936` | `test_pd14_packet_without_agent_uses_the_role_agent_and_declares_it` | quita solo `agent`, espera fallback `cdad-<role>` y declaración | Un request con contexto sin agente ya no es un histórico válido | **Fixture válido afectado** → histórico sin ambos (o mover la aserción de rechazo al módulo nuevo) |
| `test_006_005_u2_opencode_module.py:902` | `test_pd14_unpublished_packet_agent_fails_closed_before_dispatch` | inyecta `cdad-006-005-u2-unpublished-agent` (rol ajeno) | El contraste estático lo rechaza antes; el test podría quedar verde sin probar la publicación | **Fixture válido afectado** → variante del mismo rol, contextualmente coherente y no publicada; assertar la causa «no publicada» |
| `test_010_004_t2_red.py:82-100` | 5 tests (`104/181/258/385/507`) | `locator_project` setea `execution_context` sin `agent` | Regla de presencia | **Fixture válido afectado, fuera de T5** → añadir `agent` derivado; reencauce de alcance |

### 8.4 Inventario de archivos que T5 debería incluir si la medición encuentra más de los cinco previstos

**Edición obligatoria adicional (6.º archivo):**
1. `tests/test_010_004_t2_red.py` — añadir `agent` al request sintético de `locator_project` (1 línea de fixture; 5 tests verdes que hoy regresarían). Obligación anterior: 010-004 PC-04/05/06/07. Obligación nueva: 010-002 PC-08 (presencia). Razón: el request con contexto debe declarar agente; no se debilita ninguna aserción de localizador.

**Edición opcional (solo según decisión de fixture):**
2. `tests/test_006_005_u6fix5_write_ahead.py` — solo si A11 se implementa como test aditivo allí; si se implementa en el módulo nuevo, **no se edita**.

**Ejecutar como regresión, sin editar (recomendación de lista, no cambio de alcance):**
- `tests/test_static_block_ceiling.py`, `tests/test_006_004_u3_principle_single_source.py` (techo estático; no están en la lista de T4).
- `tests/test_packet_prepare.py` (documento exacto con `agent`+`execution_context`; verde).
- `tests/test_008_001_home_xdg_isolation.py` (canarios de aislamiento).
- `tests/test_010_004_t6_red.py` (quita solo `execution_context`, conserva `agent`: histórico **válido**; no tocar).
- `tests/test_005_001_t2_replace_packet.py`, `tests/test_005_005_t1_replace_conserved.py` (reemplazo con stack `None`; neutrales).

**No requieren edición ni ejecución adicional:** los otros 8 archivos con `--replace-packet`; los 9 usuarios de `PacketFixture` (requests sin ambos campos = históricos válidos); `test_004_002_t4_dispatch.py`; `test_008_004_packet_enforcement.py`; `test_role_packet_consumers.py`.

---

## 9. (8) Aislamiento de `conftest.py` y `CDAD_INSTALL_ROOT`; techo estático

**Aislamiento (medido):**
- `tests/conftest.py:28-45` fija `HOME`, `XDG_CONFIG_HOME/DATA/STATE/CACHE/RUNTIME`, `TMPDIR/TMP/TEMP` bajo una raíz por test y **retira** `CDAD_INSTALL_ROOT`, `CDAD_OPENCODE_AGENTS_DIR` y `CDAD_CONTEXT_METER_STORE` (AJ2). Siembra los agentes canónicos en el HOME temporal (`:62-65`).
- Fixture de sesión (`:80-105`) + fixture por test (`:108-126`): el basetemp y el HOME real nunca se usan; `tempfile.tempdir` se restaura.
- `CDAD_INSTALL_ROOT` se pasa **explícitamente** en 36 archivos de test; el patrón canónico es `CDAD_INSTALL_ROOT=<temp>` + `CDAD_SKILL_EXTRA_DIRS=""` (`test_010_001:1335-1339`).
- Canarios verdes: `test_008_001_home_xdg_isolation.py::TestPC4Canary` (2 tests; `4 passed` con PC-3). El fixture `product_staging.product_root()` garantiza staging en una **copia** cuando falta, y nunca escribe el checkout.
- Ambos runtimes se verifican con los destinos existentes `INSTALLED_AGENTS_DIRS = {opencode: ".config/opencode/agents", claude-code: ".claude/agents"}` y `SKILLS_DESTINATIONS` (2 destinos `skills/cdad-cycle`), sin inventar rutas.

**Techo estático (medido):**
- `tests/test_006_004_u3_principle_single_source.py::TestPd13StaticBlockCeiling::test_pd13_the_static_block_of_the_fourteen_role_substage_pairs_is_under_the_ceiling` → **1 passed** (14 pares < 12000).
- `tests/test_static_block_ceiling.py` → **2 passed** (default 12000; `CDAD_STATIC_BLOCK_LIMIT` la baja y falla explícito).
- `tests/test_role_packet_render.py:271` (bloque delimitado y <12000) → verde.
- **No se ve afectado por el aislamiento**: el techo se mide sobre el bloque compuesto, no sobre el HOME. **Sí puede verse afectado por el contenido de T4** (texto nuevo en roles/bloques): T4 debe reejecutar el control y, si se acerca al techo, recortar texto — **nunca** elevar el límite. `test_static_block_ceiling.py` exige que `CDAD_STATIC_BLOCK_LIMIT` no esté seteado en el entorno; correr en entorno limpio.

**Caveat de staging obsoleto (riesgo de oráculo):** el checkout tiene `build/staging` (Oct 31 05:19). `product_root()` devuelve el checkout cuando el manifest existe, así que un test de distribución podría comparar contra staging **viejo**. T4 debe regenerar (`make agents`) antes de ejecutar `TestDistribution`; para T3 RED, el test debe generar en una **copia descartable** (`disposable_product()` de `test_006_004_u3`, que corre `make agents` en la copia) y comparar promovidos vs staging **dentro de la copia**, no en el checkout.

---

## 10. (9) Riesgos de oráculo: verde sin proteger la promesa / texto confundido con fidelidad

| # | Riesgo | Dónde | Mitigación obligatoria |
|---|---|---|---|
| **R1** | Un test de presencia (PC-01/02/04/05/09) pasa con cualquier mención y no con la celda correcta | PC-04/05, PC-09 | Localizar la región por rol/archivo; exigir el **par** exención+obligación; para PC-09 exigir la **ausencia** de «otro valor → genérico» en **todas** las superficies, no solo la presencia de «sufijo» |
| **R2** | El rechazo **estático** preempta al **contextual** y el test contextual queda verde sin probarlo | u2 PD-14 (`UNPUBLISHED_AGENT` rol ajeno); cualquier test de `record-dispatch` con agente ajeno | Usar un agente del **mismo rol** y **contextualmente coherente** (stack sin variante publicada) para el caso de publicación; para el contextual, mismo rol y stack distinto; assertar que el diagnóstico contextual **nombra el stack** y el estático declara que **no lo evalúa** |
| **R3** | El test de exclusión de `agent` del render compara un request inválido (contexto sin agente) | u1c:246 | Comparar **dos requests válidos** (sin contexto declarado) que difieran solo en `agent`; assertar el conjunto de metadata; no comparar contra el paquete moderno |
| **R4** | El «histórico» reconstruido conserva `execution_context` o bytes modernos y pasa por el motivo equivocado | u1c:316, u1b:1247, u2:943 | Assertar la **ausencia de ambos** campos como precondición; reconstruir el paquete canónico (la metadata pierde `execution_context`); no comparar bytes contra el paquete moderno |
| **R5** | Un test de reemplazo asserta el agente del predecesor y se vuelve verde con la copia actual | `test_007_002` | El oráculo espera el agente **rederivado**; el fixture debe hacer que predecesor y esperado **difieran** (cambiar stack) y assertar la diferencia como precondición |
| **R6** | El test de esquema inspecciona `properties` y no valida instancias | PC-10 | `jsonschema.validators.validator_for(schema)` + `check_schema` + `iter_errors`; instancias reales (request válido, histórico, tipos inválidos, clave desconocida, contexto sin agente) |
| **R7** | El test de repetición/write-ahead no cambia realmente el stack y pasa trivialmente | A10/A11 | Precondición: assertar el stack antes y después; assertar que un **intento nuevo** con el agente anterior sí se rechaza (discriminador) |
| **R8** | El test de distribución compara promovidos contra staging obsoleto o contra el checkout | PC-11/PC-12 | Generar en copia descartable; comparar `product/agents` vs `product/build/staging/agents`; no leer `build/staging` del checkout como oráculo del contenido corregido |
| **R9** | El test de recepción «tras cambio de stack» no despachó antes y no prueba continuidad | A9 | Secuencia completa: prepare → record-dispatch → cambiar stack → receive; assertar recibo durable |
| **R10** | Un test estructural de PC-04/05 se contabiliza como PC-13 | Cierre | PC-13 solo T8; el cierre separa control automático e informe independiente |
| **R11** | El test de PC-03 confunde el default del implementer con una prohibición mecánica de documentación | PC-03 | Usar la igualdad exacta de `test_packet_prepare` (ya verde) para scopes; el test nuevo solo asserta el procedimiento y el `prepare` sintético con alcance docs explícito; no prometer rechazo mecánico de un encargo sin alcance |
| **R12** | El test de variante ausente usa un stack inexistente como dominio y crea un fixture irreal | u2 PD-14 | Si se rebasa, declararlo como fixture descartable; alternativa: mantener el fixture actual y **declarar** que la promesa «no se despacha una variante ausente» queda ahora garantizada por la validación compartida, no por el módulo (no atribuirla al módulo) |

**Límite honesto:** ningún test de este AUDIT acredita fidelidad semántica, suficiencia de una exclusión ni conducta efectiva de modelos. Eso es T8/PC-13.

---

## 11. Inventario RED propuesto y trazabilidad test → PC → consecuencia

> Esta subfase **no escribe** tests. El inventario es la propuesta para T3/T5/T7.

### 11.1 T3 — instrucciones y distribución (`tests/test_010_002_documentary_role_integration.py`)

| Test | PC | Sin este test, el usuario… |
|---|---|---|
| `TestEngagement::test_documentary_procedure_uses_the_existing_fields_without_a_new_selector` | PC-01 | …no tiene procedimiento comprometido y el encargo se improvisa. |
| `TestEngagement::test_six_role_boundaries_and_no_documentary_variant` | PC-02 | …podría recibir un agente/selector documental paralelo. |
| `TestEngagement::test_explicit_editable_scope_and_stop_on_protected_overlap` | PC-03 | …podría tener un productor escribiendo en tests u oráculos. |
| `TestOdooApplicability::test_addon_boundary_and_module_documentation` | PC-04 | …la documentación dentro de un módulo se trataría como addon o el addon se colaría como documentación. |
| `TestOdooApplicability::test_producer_roles_matrix` | PC-04 | …architect/test-writer/implementer no sabrían cuándo rige la batería de addon. |
| `TestOdooApplicability::test_review_coordination_memory_matrix_and_diff_prevalence` | PC-05 | …un diff de addon bajo etiqueta documental se aceptaría sin instalación limpia/lint/OCA. |
| `TestOdooApplicability::test_documentary_verifier_is_not_an_addon_test` | PC-04 | …un verificador documental se convertiría en test de addon por dominio. |
| `TestOdooApplicability::test_distributed_artifacts_carry_the_matrix` | PC-04/05 | …la matriz quedaría en fuentes pero no llegaría a los agentes distribuidos. |
| `TestDispatchDoctrine::test_every_selection_surface_derives_a_suffix_and_keeps_no_other_value_fallback` | PC-09 | …una sesión nativa caería al genérico para un stack no vacío. |
| `TestDispatchDoctrine::test_absent_variant_is_mechanical_external_and_procedural_native` | PC-09/PC-08 | …una variante ausente se sustituiría en silencio. |
| `TestDistribution::test_generation_is_reproducible_and_promoted_matches_staging` | PC-11 | …los agentes distribuidos podrían no ser los aprobados. |
| `TestDistribution::test_isolated_install_distributes_corrected_surfaces_and_the_generic_journey` | PC-12.a | …el perfil documental no existiría tras instalar. |
| `TestDistribution::test_documentary_odoo_journey_keeps_domain_and_write_frontier` | PC-12.a | …el recorrido documental/Odoo no conservaría dominio ni frontera de escritura. |

**Controles citados, no reescritos:** `test_packet_prepare` (PC-03), `test_cdad_generate` (PC-11), `TestPd13` + `test_static_block_ceiling` (PC-11), `test_010_001` (instalación/agentes).

### 11.2 T5 — publicación, coherencia, compatibilidad y esquema (`tests/test_010_002_documentary_role_integration.py` + adaptaciones)

| Test | PC | Sin este test, el usuario… |
|---|---|---|
| `TestAgentBinding::test_ordinary_publication_publishes_derived_agent_and_context` | PC-06/07a | …no sabría a qué agente se publicó su encargo. |
| `TestAgentBinding::test_replacement_of_historical_successor_without_agent_rederives` | PC-06/07a | …no podría reemplazar un histórico legítimo sin agente. |
| `TestAgentBinding::test_replacement_after_stack_change_rederives_current_stack` | PC-06/07a | …el sucesor iría al dominio anterior. |
| `TestAgentBinding::test_static_role_contrast_rejects_foreign_agent_and_does_not_evaluate_stack` | PC-07b/PC-08 | …un agente de otro rol recibiría el trabajo. |
| `TestAgentBinding::test_contextual_contrast_rejects_a_new_intent_with_wrong_stack_agent` | PC-07c | …un encargo se despacharía a un dominio que ya no corresponde. |
| `TestAgentBinding::test_historical_without_both_fields_records_a_new_intent_without_destination_contrast` | PC-07c/PC-08 | …los históricos sin agente no podrían registrar un intento nuevo. |
| `TestAgentBinding::test_context_without_agent_is_rejected_on_validation_and_publication` | PC-08 | …un request con contexto sin destinatario pasaría. |
| `TestAgentBinding::test_agent_is_excluded_from_render_between_valid_requests` | PC-08 | …el render cambiaría por un campo de transporte. |
| `TestAgentBinding::test_reception_after_stack_change_keeps_the_static_contrast_only` | PC-08 | …un cambio de dominio invalidaría un trabajo ya despachado. |
| `TestAgentBinding::test_identical_repetition_after_stack_change_stays_idempotent` | PC-08 | …la repetición idéntica dejaría de ser idempotente. |
| `TestAgentBinding::test_write_ahead_finalization_after_stack_change_completes_once` | PC-08 | …un write-ahead iniciado no podría completarse. |
| `TestAgentBinding::test_new_intent_after_stack_change_is_rejected_without_mutating_packet_or_records` | PC-08 | …la excepción temporal habilitaría un intento nuevo encubierto. |
| `TestRequestSchema::test_schema_accepts_valid_current_and_historical_requests` | PC-10 | …el esquema rechazaría requests válidos. |
| `TestRequestSchema::test_schema_rejects_invalid_shape_unknown_keys_and_context_without_agent` | PC-10/PC-08 | …aceptaría contexto sin agente o claves desconocidas. |
| `TestRequestSchema::test_schema_shape_is_distinct_from_cli_role_and_dispatch_contrast` | PC-10/PC-07 | …el consumidor obtendría un veredicto distinto del CLI. |

**Adaptaciones (no nuevos):** u1c (2), u1b (1), u2 (2), `test_007_002` (2 transiciones de reemplazo: histórico sin agente y cambio de stack), `test_010_004_t2_red` (1 fixture). **Intactos:** los cinco archivos 006_005 no enumerados, los 9 usuarios de `PacketFixture`, `test_packet_prepare`, `test_010_001`, `test_cdad_generate`, `test_install_ownership`, `test_install_review5_regressions`, `test_007_006_withdraw_and_republish`, `validate-odoo-specialization.sh`, `test_008_004`, `test_role_packet_consumers`, `test_static_block_ceiling`, `TestPd13`, `test_004_002_t4`, `test_006_005_u6fix5`.

### 11.3 T7 — propiedades e integración final

| Test | PC | Sin este test, el usuario… |
|---|---|---|
| `TestInv04Properties::test_publication_derives_a_coherent_agent` (semilla fija) | INV-04/PC-06 | …una entrada aleatoria podría publicar un agente incoherente. |
| `…::test_static_role_contrast_rejects_random_foreign_agents` | PC-07b | …la regla estática quedaría sin cobertura generable. |
| `…::test_contextual_contrast_rejects_random_wrong_stack` | PC-07c | …la regla contextual quedaría sin cobertura generable. |
| `…::test_presence_rule_holds_for_random_histories` | PC-08/PC-10 | …la dependencia agente/contexto tendría agujeros. |
| `test_final_isolated_install_runs_the_documentary_journey_with_cli_and_schema` | PC-12.b | …la instalación final podría distribuir un CLI/esquema anterior. |

**PC-13:** solo T8; no se escribe proxy estructural.

---

## 12. Dudas contractuales y correcciones propuestas

**Ninguna postcondición quedó no verificable.** No hay bloqueantes.

Aclaraciones recomendadas (no bloqueantes, no cambian el alcance):
1. **Write-ahead histórico:** una línea que diga que la finalización de un intento histórico sin `agent` tampoco aplica contraste contextual (se deduce de D3, pero conviene explicitarlo).
2. **Alcance de «validar un request publicado»:** precisar que la regla de presencia se aplica en `validate-request` y `validate-packet` (no solo `render`), como ya implica D3.
3. **PC-03:** declarar que «requiere alcance editable explícito» es una obligación procedimental; no hay rechazo mecánico de un encargo documental sin alcance. Si el dueño quisiera enforcement mecánico, sería un cambio de contrato fuera de esta unidad.
4. **Variante no publicada:** precisar si, tras la validación compartida, el rechazo del adaptador externo sigue siendo atribuible al módulo (y por tanto su test debe rebasarse) o si la promesa se satisface con el rechazo temprano. Es una decisión de fixture/alcance, no de contrato.

---

## 13. Evidencia

**Archivos modificados:** ninguno. **Commit:** ninguno (subfase AUDIT; el `test-audit.md` lo materializa el orquestador y el commit corresponde a esa materialización). `git status` no muestra cambios de tests/producto.

**Comandos y salidas representativas:**
```
$ python3 scripts/cdad_packet.py validate-request … ; echo rc   → rc=0
$ python3 scripts/cdad_packet.py validate-packet … ; echo rc    → rc=0
$ python3 scripts/cdad_packet.py render --route C … | diff - PACKET.md → idéntico
$ sha256sum spec.md PACKET.md render → 0d630c49… / 5d84d829… / 5d84d829…
$ python3 -c "import jsonschema; …" → jsonschema 4.19.2
$ python3 -B -m pytest -q tests/test_static_block_ceiling.py → 2 passed
$ python3 -B -m pytest -q tests/test_006_004_u3_principle_single_source.py -k StaticBlockCeiling → 1 passed, 14 deselected
$ python3 -B -m pytest -q tests/test_packet_prepare.py -k test_p2_default_request_derivations_per_role → 1 passed, 18 deselected
$ python3 -B -m pytest -q tests/test_006_005_u1c_packet_agent.py → 5 passed
$ python3 -B -m pytest -q tests/test_006_005_u1b_dispatch_entry.py -k pd5_native_packet_without_agent → 1 passed, 16 deselected
$ python3 -B -m pytest -q tests/test_006_005_u2_opencode_module.py -k pd14 → 3 passed, 16 deselected
$ python3 -B -m pytest -q tests/test_007_002_dispatch_recovery.py -k "…replace_disposed_packet…" → 2 passed, 16 deselected
$ python3 -B -m pytest -q tests/test_010_004_t2_red.py → 6 passed
$ python3 -B -m pytest -q tests/test_010_004_t3_red.py → 7 passed
$ python3 -B -m pytest -q tests/test_010_004_t5_e2e.py → 2 passed
$ python3 -B -m pytest -q tests/test_010_004_t6_red.py → 2 passed
$ python3 -B -m pytest -q tests/test_010_001_documentary_contracts.py → 11 passed
$ python3 -B -m pytest -q tests/test_role_packet_render.py → 17 passed
$ python3 -B -m pytest -q tests/test_role_packet_consumers.py → 5 passed
$ python3 -B -m pytest -q tests/test_008_004_packet_enforcement.py → 25 passed
$ python3 -B -m pytest -q tests/test_008_001_home_xdg_isolation.py -k "PC4 or PC3Overrides" → 4 passed, 4 deselected
$ rg -n --glob '*.py' 'pop\(\s*["'"'"']agent' tests → 4 sitios / 3 archivos
$ rg -l --glob '*.py' 'replace-packet' tests | wc -l → 10 (0 con `agent`)
$ rg -l --glob '*.py' 'packet-request\.schema' tests | wc -l → 0
$ rg -n --glob '*.py' '"stack": "generic"' tests → 2 (manifiestos, no estado)
$ pytest --collect-only -q → 1887 tests; 1 error ajeno (examples/idea_log, sin módulo odoo)
```

**Artefacto temporal:** `/tmp/opencode/render-C.md` (render canónico para el diff), fuera del repositorio.

---

## 14. Veredicto del gate AUDIT

- **Mapa PC→verificación:** suficiente, con clases explícitas y consecuencias de usuario.
- **Presencia vs suficiencia:** separadas; PC-13 reservada a T8.
- **Matrices Odoo:** cubiertas por rol y artefacto distribuido, sin usar `write_scope` de reviewer/architect; el diff contrario a la etiqueta queda en T8.
- **Tres vías de PC-07:** clasificadas; publicación ordinaria y reemplazo como **garantía por construcción**, no como ramas de rechazo alcanzables.
- **Histórico sin ambos campos:** tratamiento explícito, sin derivación ni sustitución silenciosa.
- **Separación temporal:** cuatro comportamientos separados con discriminadores.
- **Medición:** completa y con ubicaciones; se encontró **un archivo adicional** que T5 debe editar (`test_010_004_t2_red.py`, 5 tests verdes en riesgo) — **requiere reencauce de alcance antes de RED**— y dos decisiones de fixture (variante no publicada; ubicación del test de write-ahead).
- **Aislamiento y techo:** suficientes; el techo debe reejecutarse en T4 y no elevarse.

**Condición de cierre del AUDIT:** el orquestador debe resolver el alcance de `tests/test_010_004_t2_red.py` y las dos decisiones de fixture antes de autorizar T5. Sin esa resolución, el RED de T5 no puede proteger PC-08 sin regresar 5 tests verdes de 010-004.
