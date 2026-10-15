I have completed the adversarial review with my own probes. Cleaning up is done (worktree removed, repo untouched except the pre-existing orchestrator state edit). Here is the final artifact.

---

# review.md — Revisión formal (etapa 4) — `005-003-orientation-reduction`

Rol: **reviewer** (sesión independiente del autor; familia distinta a la del implementer). Read-only: no edité código ni tests, no desplegué, no toqué HOME, no hice push, no abrí `tests/.sensitive-patterns.local`, no escribí en la base real de sesiones. No corrí la suite completa (la corre quien cierra, una sola vez); corrí focales y sondas propias.

## 1. Objeto revisado

- **Contrato:** `docs/specs/005-003-orientation-reduction/spec.md`, sha256 `d630fdf9447b0296d558d682c5858432837272caaeec020b49b472665535118c` (verificado contra el declarado en el paquete). Plan: `docs/specs/005-003-orientation-reduction/plan.md`. Criterio de review vigente: `docs/epics/epic-005-real-operation/execution.md` (2026-10-12).
- **Rango de commits:** `009902b..HEAD` (`04feda6`). Commits de producto/test: `2bdf314` (T1 RED), `2bc159a` (T1 GREEN), `350aa58` (T2 RED), `5e628de2` (T2 testfix), `1810370` (T2 GREEN), `8b5673d` (T3 RED, incluye la corrección de D11-3 en `test_005_002_t4_acceptance.py`), `48d47f7` (T3 GREEN), `afd7fd4`/`b6e567b` (T4), `d805876`/`d45e627` (T6). Docs/state: `67514af`, `eda3299`, `6ea8065`, `bacb74b`, `ea9f94a`, `65e7caa`, `ddd6a62`, `5ad965d`, `8fba5de`, `86fe768`, `ff153cf`, `04feda6`.
- **Superficie de producto tocada:** `skills/cdad-cycle/scripts/cdad_packet.py`, `cdad_context_meter.py`, `cdad_result.py`; `assets/orientation-examples.json`, `assets/packet-request.schema.json`; `references/orientation.md`, `context-meter.md`, `project-start.md`, `capabilities.md`; `packets/common.md`, `packets/roles/implementer.md`, `packets/substages/implementer-green.md`; tests `test_005_003_t{1,2,3,4,6}_*.py` + corrección en `test_005_002_t4_acceptance.py`. `install.sh`, `agents/`, `sources/`, `build/` **no** fueron tocados.
- **Estado del árbol:** solo `docs/.cdad-state.json` aparece modificado (artefacto del orquestador, fuera del write scope de la feature). El producto está commiteado.
- **Evidencia propia ejecutada:** focales de la feature `43 passed` (T1..T4,T6); sondas adversariales propias (límite de la vista, byte-identidad del medidor, resumen del conjunto, conservación de `plan_task`, selección de entrada, render cross-versión con worktree en `009902b`).

## 2. Verificación por postcondición / invariante

| Id | Cubierto por test **ejecutable** | Cubierto por oráculo **documental** | **Sin cobertura** |
|---|---|---|---|
| PD-1 (vista acotada, sin `stage_history`, fail-closed, read-only, límite independiente del historial) | `test_005_003_t1_compact_view.py` (5 tests) + sondas propias | — | — |
| PD-2 (selección de entrada) | T1 (5 tests) | — | Borde «`active_packet` ausente + dirs de paquetes históricos» (ver **F2**) |
| PD-3 (ejemplos ejecutados, localizados por asset) | `test_005_003_t2_examples_execute.py` (5 tests) | — | — |
| PD-4 (ausencia ≠ incoherencia; medidor ausente) | — | T2 (`test_pd4_*`, 2 tests) | — |
| PD-5 (rc real; error accionable; asimetría diagnosticada en la salida) | T2 (`test_pd5_*`, repro `PIPESTATUS`) + T1 (`test_pd5_relative_root_*`) | T2 (parte documental de `orientation.md`) | — |
| PD-6 (resumen del conjunto + R4) | T3 (`test_pd6_*` ×4 + `test_r4_*` ×2) + sondas propias | R4 (reference) | — |
| PD-7 (no-regresión 005-002) | `test_005_002_t1_neutral_record.py` + sonda de byte-identidad propia | — | — |
| PD-8 (corridas redundantes declaradas) | — | `acceptance.md` §6 | — (proceso, sin oráculo ejecutable por diseño) |
| PD-9 (capacidades + fallback) | — | `test_005_003_t4_*` (6 tests, oráculo documental) | — |
| PD-10 (contrato aplicable del encargo) | `test_005_003_t6_packet_contract.py` (7 tests) | — | **§2.8-(iv)** conservación/re-resolución en `--replace-packet`: **sin oráculo** (verificado por sonda propia, funciona) |
| PD-11 (arranque con la vista primero) | — | T2 (`test_pd11_*`, 2 tests) | — |
| PD-12 (cierre de D11) | T3 (`test_d11_1_*`, `test_d11_2_*`, `test_d11_4_*`) + corrección D11-3 en `test_005_002_t4_acceptance.py` | T3 (regla en `context-meter.md`) | — |
| INV-1 (read-only) | T1 (`test_inv1_*`) | — | — |
| INV-2 (sin campo nuevo en el estado) | implícito (la vista no escribe) | — | — |
| INV-3 (sin otro bootstrap) | regresión `test_005_006_t1_start_procedure.py` | `project-start.md` §11 | — |
| INV-4 (frontera 005-007; aditivo) | T6 (`test_inv4_*`) + regresiones 005-001/005-005 | — | — |
| INV-5 (no reescribir 005-002) | regresiones + sonda byte-identidad propia | — | — |
| INV-6 (sin valores de este VPS) | — | T4 (`test_inv6_*`) | **Parcial:** el test escanea **solo `capabilities.md`**; ver **F4** |
| INV-7 (sin dashboard/fuente de estado) | — | T4 + `capabilities.md` §5 | — |
| INV-8 (condición de gate D11/R4) | T3 focales verdes | `acceptance.md` §1 | — |
| INV-9 (unknown con causa, nunca 0) | T1 (`test_inv9_*`) + T3 (resumen) | — | — |
| INV-10 (aceptación = sesión real) | — | `acceptance.md` §7 | Aceptación de uso real: **abstención** (requiere despliegue, del dueño) |

**Sondas propias (resultados):**
- **Límite de la vista:** con estado de **12,1 MB** (40.000 entradas de `stage_history`) la proyección es **byte-idéntica** (1.744 B) a la del estado chico → el límite **no crece con el historial**. En el borde exacto: `--max-bytes 1744` → `rc=0`; `--max-bytes 1743` → `rc=2`, **stdout vacío**, `ERROR: … exceeds the byte limit: 1744 bytes > 1743 bytes (--max-bytes, default 16384)…`. **Falla cerrado sin proyección parcial.** ✓
- **Byte-identidad del registro neutral (INV-5):** medidor de `009902b` vs `HEAD`, misma store sintética, **sin `--set-summary`** → salida **byte-idéntica** (`cmp` = igual). ✓
- **Resumen del conjunto:** con cobertura parcial (1 de 2 sesiones con tokens), `accumulated`/`cache.*`/`cost`/`max_output`/`total_output` → `bucket=unknown`, `value=null`, `cause` (nunca subtotal ni `0`); las magnitudes de cobertura total → `observed` con la suma. `sessions_included` hasheado (sin ids crudos). Detalle **no** emitido por defecto; restaurado con `--detail`. ✓
- **`--replace-packet` con tarea declarada:** conserva `plan_task` y **re-resuelve** el contenido desde el plan vigente (focal nuevo presente, viejo ausente). ✓ (sin oráculo de test).
- **Render cross-versión:** paquete publicado con el renderer previo a T6 → `validate-packet` en `HEAD` → `rc=2 ERROR: packet differs from canonical rendering`; el mismo paquete valida con el CLI previo (`rc=0`). (Ver **F3**.)

## 3. Hallazgos

### F1 — El plan declara un focal de T3 que no existe (`tests/test_005_003_t3_meter_no_write.py`) — Required · Bucket m
`Verdict: OPTIONAL` · `Bucket: m`

- **Qué:** la ficha T3 del plan (`plan.md:152`) y el **bloque canónico `plan-tasks`** (`plan.md:296`, `focal_tests` de T3) declaran `tests/test_005_003_t3_meter_no_write.py` como archivo **nuevo** para D11-(1)/(2). El archivo **no existe** ni existió nunca; las comprobaciones D11-(1)/(2) viven en `tests/test_005_003_t3_set_summary.py` (`test_d11_1_*`, `test_d11_2_*`). La desviación **fue declarada** por el GREEN de T3, y `acceptance.md` §1 la registra.
- **Reproducción propia:**
  ```
  $ ls tests/test_005_003_t3_meter_no_write.py
  ls: cannot access 'tests/test_005_003_t3_meter_no_write.py': No such file or directory
  $ git log --all --oneline -- tests/test_005_003_t3_meter_no_write.py
  (vacío — nunca se commiteó ni se borró)
  $ grep -rln "test_d11_1_" tests/
  tests/test_005_003_t3_set_summary.py
  ```
- **Por qué importa (no es cosmético):** el bloque `plan-tasks` es la **fuente canónica** que T6 renderiza en `## Task validation plan`. Un paquete de esta feature preparado con `--plan-task T3` emitiría un `focal_tests` **no ejecutable** (archivo inexistente): la promesa de T6 («no es obligatorio releer la spec entera para ejecutar el encargo») queda rota para esa tarea. Además el **plan aprobado contradice a la spec**: PD-12-(1)/(2) dice «vive en el test focal nuevo de T3» / «el mismo test focal» (singular) — la spec coincide con lo entregado; el plan no.
- **Por qué NO es BLOCKING:** la garantía (D11) **sí está entregada y verde** (los focales existen y pasan); el desvío fue declarado; y no hay paquete futuro de T3 previsto. Impacto material: exactitud de la superficie declarada del plan.
- **Disposición recomendada:** reconciliar el plan (quitar el archivo inexistente de la ficha `:152`/`:161` y del `focal_tests` de T3 en `:296`) **o** crear el archivo declarado. **Condición de cierre verificable:** `grep -c t3_meter_no_write docs/specs/005-003-orientation-reduction/plan.md == 0` **o** `test -f tests/test_005_003_t3_meter_no_write.py`. **Escalable a BLOCKING** si el dueño exige que la superficie declarada del plan coincida exactamente con los archivos entregados.

### F2 — La detección de «trabajo pendiente» ignora el calificador de la spec y produce una selección falsa en reposo — Required · Bucket m
`Verdict: OPTIONAL` · `Bucket: m`

- **Qué:** `_pending_work` (`cdad_packet.py:3670-3680`) cuenta como pendiente **cualquier** sub-directorio `.cdad/packets/<id>/` con `REQUEST.json`, **sin** aplicar el calificador de la spec §2.2 («sub-directorios … **con estado distinto de `completed`**»). Tampoco usa las fuentes declaradas `current_stage`/`postconditions_status`. Los directorios de paquete **no portan estado propio** (solo `REQUEST.json` + `PACKET.md`; no hay `state.json`), de modo que el calificador es **no implementable** con las fuentes declaradas: la implementación eligió una aproximación conservadora.
- **Reproducción propia** (proyecto fixture, `active_packet=null`, `execution=null`, un directorio de paquete histórico):
  ```
  entry = continuity-reconcile   (spec §2.2: «reposo sin trabajo pendiente» -> next-unit)
  next  = {'route': 'resume the active execution (continuity)',
           'source': 'docs/.cdad-state.json:execution'}   <- apunta a una ejecución que no existe
  ```
  El repo real acumula **372** directorios bajo `.cdad/packets/`; cuando `active_packet` es `null` la vista caería en `continuity-reconcile`.
- **Por qué importa:** la **selección es el producto central** de la feature. En un estado que la propia spec declara válido («cuando `active_packet` está ausente»), el `entry` y el `next` son incorrectos.
- **Por qué NO es BLOCKING:** el error **erra del lado seguro** (nunca omite trabajo pendiente; solo lo inventa); es recuperable (la ruta `continuity-reconcile` sin paquete/ejecución lleva a `resume` → `no-checkpoint rc=0`, sin pérdida); y alcanzar `active_packet=null` + dirs publicados por el camino del CLI es poco frecuente (el único `state["active_packet"] = None` vive en la recuperación de publicación interrumpida, que exige que el dir **no** esté publicado).
- **Disposición recomendada:** declarar la aproximación en el reference **o** añadir la fuente de estado que distinga `completed` (p. ej. leer el estado por paquete). **Condición de cierre verificable:** un test que con `active_packet` ausente y un dir de paquete **completado** afirme `entry == next-unit`, o una declaración explícita del calificador no implementado.

### F3 — La corrección de los assets de instrucción invalida los paquetes publicados antes de T6 — Bucket m
`Verdict: OPTIONAL` · `Bucket: m`

- **Qué (hallazgo declarado del orquestador, juzgado):** T6 modifica `packets/common.md`, `roles/implementer.md` y `substages/implementer-green.md`. El paquete embebe `instruction_sources` (path + sha256) **y** el texto compuesto de la instrucción (`render_packet`, `:872-913`). Por eso, tras T6, **todo** paquete publicado con los assets previos deja de re-renderizarse byte-idéntico: `validate-packet` / `cdad_result.receive` fallan con `packet differs from its canonical rendering`.
- **Reproducción propia** (worktree en `009902b`, paquete preparado con el CLI previo, validado con `HEAD`):
  ```
  PRE  prepare          rc=0
  HEAD validate-packet  rc=2   ERROR: packet differs from canonical rendering
  PRE  validate-packet  rc=0
  ```
- **Juicio (respuesta a la pregunta del orquestador):** **no** compromete el **resultado** (las PD/INV de la feature se cumplen; el render sin `plan_task` es aditivo dado el mismo asset), ni la **evidencia** (los focales de T6 pasan; el orquestador declaró el recibo fallido y verificó por otra vía), ni el **uso previsto** (orientación con contexto acotado). Es una **consecuencia inherente** al contrato de paquete (los hashes de instrucción son parte del paquete) y **exigida** por PD-10-(iv) — la feature no puede evitar cambiar esos assets. El fallo es **ruidoso y recuperable** (re-preparar/reconciliar).
- **Disposición recomendada — deuda declarable:** declarar la consecuencia y el camino legítimo (re-preparar/reconciliar un paquete en vuelo) donde un orquestador la vea (`re-entry.md`/`orientation.md`). **Condición de cierre verificable:** la declaración existe en el reference y nombra que cambiar un asset de instrucción invalida los paquetes publicados antes del cambio. **No** requiere corregir el renderer.

### F4 — El artefacto de aceptación porta un identificador crudo de sesión — Nit · Bucket l
`Verdict: OPTIONAL` · `Bucket: l`

- **Qué:** `acceptance.md:75` cita un identificador crudo de sesión (`ses_…`) para la excepción del GREEN de T2. La spec §2.9 declara que «la sesión se registra por **referencia hasheada**», y el `test_inv6` de T4 define un patrón `RAW_SESSION_RX` — pero ese test escanea **solo `capabilities.md`**, así que la cobertura automática de INV-6 es **parcial** (no alcanza a `acceptance.md` ni al resto de los docs de la feature).
- **Reproducción propia:**
  ```
  $ grep -rEn "\bses_[A-Za-z0-9]{6,}\b" docs/specs/005-003-orientation-reduction/
  docs/specs/005-003-orientation-reduction/acceptance.md:75: … (`ses_…`): …
  $ grep -En "\bses_[A-Za-z0-9]{6,}\b" docs/specs/005-003-orientation-reduction/spec.md \
        docs/specs/005-003-orientation-reduction/plan.md        # (vacío)
  $ grep -rEn "\bses_[A-Za-z0-9]{6,}\b" skills/ scripts/         # (vacío)
  ```
- **Alcance honesto:** INV-6 nombra «spec, plan ni producto»; spec, plan y producto **cumplen** (verificado). El hallazgo es una inconsistencia con §2.9 en el artefacto de T5, y una **cobertura parcial** del oráculo INV-6.
- **Disposición recomendada:** reemplazar el id crudo por su referencia hasheada en `acceptance.md`. **Condición de cierre verificable:** `grep -rEn "\bses_[A-Za-z0-9]{6,}\b" docs/specs/005-003-orientation-reduction/` vacío.

### F5 — La comprobación de versión de la vista usa el `cdad-version-check.py` hermano del CLI en ejecución — FYI · Bucket l
`Verdict: OPTIONAL` · `Bucket: l`

- La spec §2.1/§2.4 pide reusar el `cdad-version-check.py` **instalado**; la vista usa `Path(__file__).resolve().parent / "cdad-version-check.py"` (el hermano del CLI que corre). Corriendo el CLI del repo, el verdicto es `UNKNOWN` (ausencia) — exactamente lo observado por la aceptación (`version.verdict=UNKNOWN` con causa). Es coherente con «la versión correspondiente al CLI cargado» y la aceptación lo declaró ausencia, no `DRIFT`; lo registro como nota, sin defecto material.

### F6 — La frase «the complete suite is the closure gate» persiste en references — FYI · Bucket l
`Verdict: OPTIONAL` · `Bucket: l`

- La política de la suite completa está declarada **una sola vez** en `packets/common.md` y `roles`/`substages` la referencian (el oráculo T6 lo verifica y no encuentra contradicción en `packets/roles/**` ni `packets/substages/**`). La frase «the complete suite is the closure gate» sigue en varios **references** (`stage-3-tdd.md:174`, `re-entry.md:149`, `handoff-prompts.md:377`, `anti-patterns.md:29`) — consistente con «la corre quien cierra, al cierre», y fuera del alcance declarado por la spec §2.8-(c). Nota, sin defecto.

## 4. Auditoría del debilitamiento de tests (commit por commit)

- **T1** (`2bdf314`): único commit del test → **sin ediciones posteriores**. Sin debilitamiento.
- **T2** (`350aa58` RED → `5e628de2` testfix → `1810370` GREEN): el testfix es una **enmienda de oráculo firmada** por el test-writer. Cambia **una** cosa: `CONTINUITY_ALLOWED` pasa de `{goal,decisions,uncertainties,next_action,budget}` a añadir `{packet_id, attempt}`. **No debilita:** la aserción de contenido mínimo (`CONTINUITY_REQUIRED <= cont_obj`) se **conserva**, y la cota de claves permitidas sigue existiendo (una clave arbitraria sigue rechazándose). La enmienda **corrige el oráculo, no el producto**: el CLI de continuidad exige `packet_id`/`attempt` como claves de idempotencia y falla cerrado sin ellas, así que el oráculo previo era **mutuamente insatisfacible** con `test_pd3_continuity_update_example_executes`. Correcto.
- **T3** (`8b5673d` RED, único commit): incluye la corrección de **D11-3** en `test_005_002_t4_acceptance.py` — se **retira** la aserción de `(tamaño, mtime)` de la base **viva** (inestable por escritores externos) y se conserva la comprobación de **lectura y resultados**. **No debilita la garantía:** la no-escritura se verifica sobre **base temporal controlada** (`test_d11_1_*`) y la concurrencia con **escritor activo** (`test_d11_2_*`), exactamente como exige PD-12-(1)/(2)/(3). Autorizado por el plan y la spec.
- **T4** (`afd7fd4`): único commit → sin ediciones. Sin debilitamiento.
- **T6** (`d805876`): único commit → sin ediciones (confirmado por el orquestador: `tests/` intacto entre RED y GREEN). Sin debilitamiento.
- **RED legítimo:** T1/T2/T3/T4/T6 fallaron por `AssertionError` de contrato (los reportes de rol lo evidencian: 6 `AssertionError` en T6, 0 excepciones no-aserción). T6 tiene un test ya satisfecho (`commit` ya en `DEFAULT_EVIDENCE`), declarado.

## 5. Abstenciones declaradas

1. **Aceptación de uso real (A1/A2/A6/A8/A9).** Requiere **desplegar** la versión y observar una **sesión real nueva**; el despliegue es del dueño y está prohibido en este tramo. No puedo juzgar la aceptación like-for-like, las bandas ni la observación del proxy de rol. (`acceptance.md` §7 la declara como bloqueo, correctamente.)
2. **Suite completa.** No corrida por política (la corre quien cierra, una sola vez). No verifiqué el árbol completo; sí los focales de la feature y regresiones citadas.
3. **Base real de sesiones.** Nunca la abrí (ni en modo lectura): no puedo verificar afirmaciones sobre la base viva; el contrato prohíbe escribirla incluso para demostrarlo.
4. **Render de un paquete de T3 contra el repo real.** No lo ejecuté (habría escrito en `.cdad/` real); inferí el resultado leyendo el bloque `plan-tasks` del plan real y el renderer. La conclusión de F1 es de lectura, no de ejecución.
5. **Reachability real de F2 en el ciclo del orquestador.** No tracé exhaustivamente cuándo `active_packet` llega a `null` con directorios publicados; la consecuencia observable está reproducida, la frecuencia real queda **no verificada**.
6. **Comportamiento de la versión instalada.** No desplegué; la conducta de `_version_verdict` contra un árbol **instalado** (no el del checkout) no fue ejercida (F5).
7. **`--replace-packet` con `plan_task`** no tiene oráculo de test; lo verifiqué con **sonda propia** (funciona), pero no hay test que lo proteja de regresión.

## 6. Veredicto

**0 BLOCKING · 6 OPTIONAL (F1–F6; F5/F6 de severidad FYI) · 7 abstenciones declaradas.**

- No encontré ningún defecto que comprometa el **resultado**, la **evidencia** o el **uso previsto** de la feature: la vista falla cerrado sin proyección parcial y su límite no crece con el historial (sondas propias); el registro neutral del medidor es byte-idéntico sin `--set-summary` (sonda propia); el resumen del conjunto declara cobertura y deja lo no observado como `unknown`/`null` con causa (sonda propia); D11 (1)-(4) y R4 (dos elementos) están cerrados y verdes; la extensión de T6 es aditiva, la tarea ausente falla cerrado nombrando el id, y `--replace-packet` conserva y re-resuelve (sonda propia).
- Los hallazgos son de **deuda priorizada** con condición de cierre verificable. **F1** (focal declarado inexistente en el bloque canónico `plan-tasks`) y **F2** (calificador de «trabajo pendiente» no implementado → selección falsa en reposo) son los más accionables y quedan a decisión del orquestador/dueño; **F1** es escalable a BLOCKING si se exige que la superficie declarada del plan coincida con los archivos entregados. **F3** es una consecuencia inherente y declarable, no un defecto del renderer. **F4** es un nit de privacidad/consistencia con §2.9.
- **No suavizo:** F1 y F2 son defectos reales con reproducción propia; los reporto con su impacto material medido, que es lo que los deja fuera del bucket BLOCKING bajo el criterio vigente.

---

**Nota de cierre:** artefacto entregado como texto final (el orquestador lo materializa). No modifiqué código, tests ni el estado; el worktree de sondeo fue retirado y el árbol quedó como lo encontré (solo `docs/.cdad-state.json` modificado por el orquestador, fuera de mi write scope).