> Plan **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). Se aprueba **junto con la spec** por el **orquestador
> OpenCode** bajo la HITL delegada del epic-005, o por el **dueño**; el architect **no**
> aprueba su propia propuesta (anti-sesgo). Contrato: `docs/epics/epic-005-real-operation/plan.md`,
> fila 9 (`:42`), sha256 `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`,
> más el ajuste 005-007 (`:70-76`). Deriva de `docs/specs/005-007-progressive-planning/discovery.md`
> y del delta `docs/specs/005-007-progressive-planning/draft-inputs-2026-10-13.md`.
> El bloque canónico `plan-tasks` de §4 sigue el formato de
> `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1 (**se referencia, no
> se copia**) y se validó con las funciones del propio CLI en solo lectura. **Sin valores de este VPS.**

# Plan — 005-007-progressive-planning

## 1. Ficha de la feature

- **Feature ID:** `005-007-progressive-planning` · **Epic:** `epic-005-real-operation` · **Estado:** DRAFT (etapa 2).
- **Resultado buscado (fila 9):** contratos claros y tareas ejecutables con contexto suficiente, evitando la especificación excesiva y la fragmentación; **planificación progresiva** (objetivo y dependencias completos; detalle sólo de la próxima tanda); **tamaño de unidad** por costo total; **plantillas** que acompañen (spec desde el recorrido de uso; aceptación = comportamiento, no `%`); **regla de reintentos** con hipótesis nueva y replanteo ante repetición sin progreso.
- **Alcance obligatorio (delta):** (1) abrir la unidad siguiente **sin editar el state a mano**; (2) **materializar** el informe de discovery del architect por el camino legítimo; (3) que el **medidor** reconozca como despacho la interfaz común de delegación.
- **Contrato y reglas reusadas:** ver spec §9.
- **Dependencia del epic:** `005-006` (cerrada). **Frontera con 005-003:** 005-003 aporta el **contrato aplicable** y la **vista `status`**; esta feature aporta el **tamaño de unidad**, la **preparación progresiva** y la **operación de apertura** (INV-4 de 005-003).
- **Fronteras de contrato (no reescritura):** 005-002 (medidor), 005-009/005-010 (interfaz de delegación), 005-001/005-005 (contratos de paquete): esta feature los **extiende de forma aditiva y declarada** o los referencia.

## 2. Ajuste de las unidades a tareas atómicas

Una tarea por **clase de producto y oráculo**; un **RED** cubre una clase y su **GREEN** va en **otra sesión**, sin mezclar roles.

| Unidad (discovery §5 / delta) | Tarea | Por qué se agrupa así |
|---|---|---|
| Regla de detalle progresivo (hogar canónico) + campo del formato | **T1** | Un solo producto documental (la regla + su campo) verificable por comprobación observable; sin código. |
| Reconciliación del validador + regression test | **T2** | Clase distinta: **código** en `cdad_packet.py` con oráculo de test focal; depende de T1 (la regla declara el marcador). |
| Delta 1: apertura por CLI (`open-unit`) | **T3** | Clase distinta: **código** de estado + cableado (ruta `status` + procedimiento) con focal; comparte archivo con T2 → se serializa. |
| Delta 2: materialización legítima del informe | **T4** | Clase distinta: **código** de las tablas cerradas de `cdad_result.py` + asset, con focal. |
| Delta 3: despacho por la interfaz de delegación | **T5** | Clase distinta: **código** del medidor + su reference, con focal. |
| Plantillas (spec desde el recorrido + plan de feature) | **T6** | Documental; se separa de T7 porque su oráculo es la estructura/comportamiento de las plantillas, no el criterio de tamaño. |
| Tamaño por costo total + vínculo reintentos↔unidad | **T7** | Documental; misma fuente que T1 (`stage-2-specification.md`) → se serializa con T1/T6. |
| Meta de aceptación (delta c) | **T8** | **Gate** (no RED/GREEN de producto): `observable_checks` + gate de integración; requiere T3/T4/T5. |

**Qué NO se planifica:** agente planner, perfiles de modelo, aislamiento por repo, servicios, UI, scheduler, plataforma de usabilidad, CI (fuera de alcance, spec §7). El **despliegue** y la **medición desplegada** quedan como deuda con dueño (spec §8, D-1).

## 3. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre**: procedencia, `git diff` contra el alcance del paquete, alcance declarado y **pruebas focales** (segundos). **Sólo con un motivo concreto**: la suite o la integración. Se **reutiliza evidencia equivalente** con procedencia verificada **por referencia** a `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*).
- **Suite completa una vez, al cierre** (motivo: toca el CLI, la metodología y el medidor; cierra la feature). No se corre dentro de cada tarea; **no se corre salvo que el paquete lo pida** (la corre quien cierra).
- **Comandos concretos por encargo** (fichas de §4), **tomados del bloque `plan-tasks`** de este plan y rendidos en el paquete (mecanismo de `005-003` T6). RED: el focal debe fallar por aserción (no por import/sintaxis). GREEN: focal verde + regresiones del área.
- **El cierre incluye el commit** y el reporte del rol lo declara; un rol que termina sin commitear es **bloqueo declarado**, no aceptado en silencio.
- **Metas numéricas = orientación** (spec PD-11): derivadas de la línea base medida (`acceptance.md` §9), **no** umbral automático.
- **Sin `--no-verify`; sin push; sin desplegar; sin escribir la base real de sesiones.**

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Regla de detalle progresivo (hogar canónico) + campo del formato
- **Resultado observable / PD cubiertas:** PD-1, PD-12 (base de PD-2).
- **Alcance incluido:** enunciar **una vez** la regla (objetivo + dependencias completos; detalle sólo de la próxima tanda; marcador `detail` con `"next"`/`"planned"` y los campos exigidos a la tarea planificada) en `stage-2-specification.md`; declarar el **campo** en `planning-contract-draft.md` §4.1 (formato) **por referencia** a la regla; corregir `reviewer-plan-review.md` para que el reviewer consuma el marcador **por referencia**. **Excluido:** crear ontología/máquina de estados; duplicar la regla en el validador o en los paquetes (eso es T2 por comportamiento).
- **Consume:** — . **Produce:** `progressive-detail-rule` (`progressive-detail-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/references/stage-2-specification.md`, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`, `skills/cdad-cycle/packets/substages/reviewer-plan-review.md`; *Test* — (ciclo sin código).
- **Contexto por rol:** test-writer — spec §2/§6 (D1/D2), PD-1/PD-12 + `discovery.md` §1.3; reviewer — la subfase (referencia).
- **Evidencia al re-entry:** comprobación observable roja→verde (la regla no está → está, con el campo declarado una sola vez y la referencia desde el formato y el reviewer); `git diff` acotado a los tres archivos.
- **Verificación:** `observable_checks` (sin código).
- **Integración / responsable:** `@validation_strategy`; test-writer.
- **Incertidumbres / detención:** si el owner prefiere un asset `plan-tasks.schema.json` como formato único (D1 alterna / deuda D-5), **detener** y reconciliar antes de escribir; no introducir una segunda declaración del formato.

### T2 — Validator reconciliation + regression test (VERIFY 1/2)
- **Resultado observable / PD cubiertas:** PD-2 (base de PD-1).
- **Alcance incluido:** `_check_plan_validation_plan` trata `detail == "planned"` por sus campos propios (objetivo + incertidumbre + dueño + condición) y exige el plan de validación sólo a `"next"`/sin marcador; el `detail` fuera del conjunto cerrado **falla cerrado**; los checks mecánicos siguen aplicándose a **todas** las tareas. **Excluido:** relajar el parseo fail-closed del bloque; cambiar otros checks; tocar el render del paquete.
- **Consume:** `progressive-detail-rule` (`progressive-detail-v1`) de **T1**. **Produce:** `plan-validator` (`plan-validator-v1`).
- **Dependencias:** T1.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test* `tests/test_005_007_t2_progressive_plan_validator.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-1/PD-2), `planning-contract-draft.md` §4.1, `cdad_packet.py:2883-3105`; GREEN — ídem + los planes reales como fixtures. **El test-writer no ve la implementación** (oráculo desde el contrato).
- **Evidencia al re-entry:** focal rojo→verde; `git diff` acotado; la regresión de los dos planes reales (005-003, 004-003) sin cambios de comportamiento.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q`; regresiones `tests/test_004_003_t3_plan_checks.py`, `tests/test_004_003_t4_validation_fields.py`, `tests/test_005_003_t6_packet_contract.py`, `tests/test_packet_prepare.py`.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** si el marcador obliga a reescribir un plan ya despachado, **detener** (INV-8/PD-13: no se reescribe un contrato despachado sin reconciliación).

### T3 — Delta 1: operación `open-unit` (apertura sin editar el state) + ruta `status`
- **Resultado observable / PD cubiertas:** PD-7, PD-12.
- **Alcance incluido:** subcomando `open-unit` en `cdad_packet.py` (selección de la primera `queued` o `--feature`; escritura atómica de `active_feature` + `in-progress`+`opened_at` + `current_stage`; validación de vigencia/coherencia antes de publicar; rechazo de reposo inválido y de unidad ya abierta; **reuso** de `_bootstrap_v2_execution` para la ejecución); `_next_route` de la entrada `next-unit` **nombra** el subcomando; `project-start.md` §6 lo documenta **por referencia**; `orientation.md` + `assets/orientation-examples.json` con el ejemplo ejecutado. **Excluido:** abrir la próxima **tarea** de una feature (eso es `prepare --plan-task`, existente); un segundo productor del state; migrar el formato del estado.
- **Consume:** — . **Produce:** `open-unit-operation` (`open-unit-v1`).
- **Dependencias:** — . **Nota de paralelismo:** edita el **mismo archivo** que T2 (`cdad_packet.py`) → **no** se declaran paralelas (`parallel: []`).
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`, `skills/cdad-cycle/references/project-start.md`, `skills/cdad-cycle/references/orientation.md`, `skills/cdad-cycle/assets/orientation-examples.json`; *Test* `tests/test_005_007_t3_open_unit.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-7), `005-003/spec.md:109-138`, `project-start.md:74-138`, `orientation.md:29`; GREEN — ídem + `cdad_packet.py:3442-3588` (lock/publicación) y `:501-536` (coherencia de reposo).
- **Evidencia al re-entry:** focal rojo→verde sobre un **proyecto fixture** (no el repo real): reposo → una invocación abre la primera `queued`; `validate-state` verde; segunda invocación y unidad no `queued` fallan con diagnóstico; el ejemplo del asset **se ejecuta** (localizado por el asset, no por prosa).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_007_t3_open_unit.py -q`; regresiones `tests/test_005_003_t1_compact_view.py`, `tests/test_005_003_t2_examples_execute.py`, `tests/test_005_003_f2_idle_history.py`, `tests/test_005_001_t3_idle.py`.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** si la apertura exigiera tocar la autoridad, la política o el HITL, **detener** (fuera de alcance); si el fixture revela que la coherencia de reposo no alcanza (deuda F2 de 005-003), **declararlo**, no improvisar una fuente nueva.

### T4 — Delta 2: materialización legítima del informe del architect
- **Resultado observable / PD cubiertas:** PD-8.
- **Alcance incluido:** añadir a `artifact-policy.json` el **kind del informe del architect** y el **kind declarado de la interfaz** (`role-report`) con destino `docs/specs/<feature>/`; admitirlos en `_allowed_kinds` conservando el rechazo del **kind nombrado de otro rol** y el binding de autorización. **Excluido:** cambiar el adaptador OpenCode (evita duplicar el mapa rol→kind), reescribir `receive`/`materialize`, permitir un destino fuera de `docs/specs/<feature>/`.
- **Consume:** — . **Produce:** `architect-report-materialization` (`artifact-policy-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_result.py`, `skills/cdad-cycle/assets/artifact-policy.json`; *Test* `tests/test_005_007_t4_architect_report_materialization.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-8), `cdad_result.py:608-692,795-894`, el recibo real del discovery; GREEN — ídem + `test_003_002_t2_materialize.py`.
- **Evidencia al re-entry:** focal rojo→verde (hoy `role-report` del architect se rechaza; después materializa con sha idéntico); negativos: kind nombrado de otro rol y destino fuera de la raíz permitida siguen fallando.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_007_t4_architect_report_materialization.py -q`; regresiones `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t1_receive.py`.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** si admitir `role-report` requiriera relajar la **clausura del eje rol** (aceptar un kind que no corresponde al rol del recibo), **detener** y llevar la decisión al owner; no se relaja la tabla.

### T5 — Delta 3: el medidor reconoce la interfaz de delegación como despacho
- **Resultado observable / PD cubiertas:** PD-9.
- **Alcance incluido:** reconocer como despacho una llamada `shell` que **invoca realmente** `cdad_delegate.py` (misma clase que la regla de `resume`; excluye ayuda y meras menciones); declarar el **método** de cada entrada del conjunto reconocido y actualizar la **causa de ausencia** con el límite honesto; declararlo en `context-meter.md`. **Excluido:** acoplar el medidor a un ledger/root del proyecto; inferir el despacho por texto que sólo menciona; tocar el registro neutral sin las banderas nuevas.
- **Consume:** — . **Produce:** `delegation-dispatch-detection` (`dispatch-detection-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_context_meter.py`, `skills/cdad-cycle/references/context-meter.md`; *Test* `tests/test_005_007_t5_delegation_dispatch.py`.
- **Contexto por rol:** RED — spec §2/§3 (PD-9), `005-002/spec.md:271-280`, `cdad_context_meter.py:147-186,775-818`; GREEN — ídem + fixtures de traza (una invocación real, una mención).
- **Evidencia al re-entry:** focal rojo→verde sobre **trazas fixture** (no la base real): una traza con invocación real reporta `first_dispatch` observado con el método declarado; una que sólo menciona reporta `absent` con causa; el registro sin las banderas nuevas es idéntico (regresión de byte-identidad del neutral).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_007_t5_delegation_dispatch.py -q`; regresiones `tests/test_005_002_t2_milestones.py`, `tests/test_005_002_t4_acceptance.py`, `tests/test_005_002_t1_neutral_record.py`.
- **Integración / responsable:** `@validation_strategy`; GREEN implementer.
- **Incertidumbres / detención:** **no** se lee ni escribe la base real de sesiones en el test (INV-6); si la detección exigiera el ledger para no dar falsos positivos, **declararlo** como deuda D-4, no acoplar el medidor.

### T6 — Plantillas alineadas (spec desde el recorrido de uso + plan de feature)
- **Resultado observable / PD cubiertas:** PD-5, PD-6.
- **Alcance incluido:** reescribir el inicio de `assets/spec-template/spec.md` para partir del **recorrido de uso** y con aceptación de **comportamiento** (retirar «Line coverage ≥ X%» como criterio); **crear** `assets/feature-plan-template.md` (ficha + bloque `plan-tasks`) como **consumidor** del formato declarado; referenciar la plantilla y la **receta mínima de aceptación de uso** desde `stage-2-specification.md`. **Excluido:** un manual extenso, un generador de planes, convertir la receta en un evaluador de usabilidad general.
- **Consume:** — . **Produce:** `aligned-templates` (`templates-v1`).
- **Dependencias:** T1 (misma fuente `stage-2-specification.md`). **Nota:** docs-only → `files: []` (convención de `005-003` T4); los paths viven en esta ficha.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/assets/spec-template/spec.md`, `skills/cdad-cycle/assets/feature-plan-template.md` (nuevo), `skills/cdad-cycle/references/stage-2-specification.md`; *Test* — (ciclo sin código).
- **Contexto por rol:** test-writer — spec §2/§3 (PD-5/PD-6/PD-10) + `discovery.md` §1.4/§7.
- **Evidencia al re-entry:** comprobación observable roja→verde (plantilla anclada en `Signature`+cobertura → plantilla con recorrido de uso y sin `%`; plantilla de plan ausente → presente con ficha + bloque); el bloque de la plantilla de plan **valida** con el validador del producto.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** `@validation_strategy`; test-writer.
- **Incertidumbres / detención:** si la plantilla de plan arrastra un formato que difiere de los planes vigentes, **detener** y reconciliar con `005-003/plan.md` y `004-003/plan.md` (referencias de formato del encargo).

### T7 — Tamaño de unidad por costo total + vínculo reintentos↔unidad
- **Resultado observable / PD cubiertas:** PD-3, PD-4, PD-13.
- **Alcance incluido:** añadir a `stage-2-specification.md` («Task size») las **condiciones cualitativas** de tamaño por costo total (sin números) referenciando el criterio de «costo de coordinación»; añadir a `re-entry.md` (dueño único) la cláusula de **replanteo de la unidad** ante reintento sin información nueva, manteniendo el número de intentos como señal. **Excluido:** una segunda copia de la regla de reintentos; puntuaciones/umbrales numéricos; exigir alternativas para tareas obvias.
- **Consume:** — . **Produce:** `unit-size-criterion` (`unit-size-v1`).
- **Dependencias:** T1 (misma fuente `stage-2-specification.md`). docs-only → `files: []`.
- **Archivos:** *Create/Modify* `skills/cdad-cycle/references/stage-2-specification.md`, `skills/cdad-cycle/references/re-entry.md`; *Test* — (ciclo sin código).
- **Contexto por rol:** test-writer — spec §2/§3 (PD-3/PD-4) + `discovery-inputs.md:36-52` + `re-entry.md:79` + `planning-contract-draft.md:155`.
- **Evidencia al re-entry:** comprobación observable roja→verde (criterio ausente → presente con las condiciones declaradas; disparador de replanteo ausente a nivel de unidad → presente, **sin** duplicar la regla de reintentos: se verifica que `re-entry.md` sigue siendo la única fuente del número de intentos).
- **Verificación:** `observable_checks`.
- **Integración / responsable:** `@validation_strategy`; test-writer.
- **Incertidumbres / detención:** si el criterio no puede ser verificable sin números, **detener** y proponer al owner la forma declarada (bandas nombradas), sin inventar métricas.

### T8 — Gate de aceptación de la feature (medición; delta c)
- **Resultado observable / PD cubiertas:** PD-10, PD-11; criterios AC-1..AC-8.
- **Alcance incluido:** verificar AC-1..AC-6 sobre los productos de T1..T7; correr la **medición like-for-like** (AC-7) con el **medidor del repo** (005-002) + el conteo propio sobre las partes `tool`, sobre una **sesión real nueva en reposo** y la **versión desplegada después de esta feature**; declarar el **instrumento y su procedencia**; registrar el **BLOQUEO por despliegue** si no está autorizado; declarar las bandas como **orientación**. **Excluido:** desplegar; repetir la línea base; promediar cortes distintos; tratar las bandas como umbral; declarar verde por proximidad.
- **Consume:** `open-unit-operation` (`open-unit-v1`) de **T3**, `architect-report-materialization` (`artifact-policy-v1`) de **T4**, `delegation-dispatch-detection` (`dispatch-detection-v1`) de **T5**. **Produce:** `acceptance-report` (`acceptance-report-v1`).
- **Dependencias:** T3, T4, T5. **Gate:** cubre T1/T2/T6/T7 por la estrategia de validación (sus focales/comprobaciones), y su cierre es el gate de la feature.
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable); *Test* — (gate, sin código).
- **Contexto por rol:** orchestrator — spec §5 (AC-1..AC-8) + línea base por referencia (`acceptance.md` §9); architect — lectura.
- **Evidencia al re-entry:** informe con comparación **like-for-like**, medido vs derivado, bandas declaradas **orientación**, `unknown` con causa, y — si no hay despliegue — **BLOQUEO** con responsable.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** **gate de aceptación del epic-005** (ver §6); orchestrator (medición); architect (lectura).
- **Incertidumbres / detención:** si falta la evidencia de T3/T4/T5 → **BLOQUEO declarado**, no atajo; si el despliegue no está autorizado → **BLOQUEO**, no verde.

La **representación de detalle progresivo** (PD-1) se ejerce **en este mismo plan**: T1..T8 están **detalladas** porque son la **tanda próxima**; un plan futuro puede declarar sus unidades posteriores como `detail: "planned"` con objetivo + dependencias + incertidumbre + dueño + condición, sin plan de validación por tarea.

### Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "Verificacion en dos niveles: siempre procedencia + diff + alcance declarado + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite.",
 "tasks": [
  {"id": "T1",
   "objective": "Enunciar una sola vez la regla de detalle progresivo (objetivo y dependencias completos; detalle solo de la proxima tanda; marcador detail next/planned) y declarar su campo de formato, con los consumidores por referencia.",
   "produce": [{"artifact": "progressive-detail-rule", "contract": "progressive-detail-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [],
   "observable_checks": ["la regla vive en un solo lugar (skills/cdad-cycle/references/stage-2-specification.md) y el campo del bloque plan-tasks se declara una sola vez (planning-contract-draft.md seccion 4.1) por referencia a la regla; la subfase reviewer-plan-review consume el marcador por referencia; no hay una segunda copia de la regla en el validador ni en los paquetes"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "test-writer"},
  {"id": "T2",
   "objective": "Reconciliar el validador del plan-tasks con el detalle progresivo preservando el fail-closed y los checks mecanicos, con su test de regresion.",
   "produce": [{"artifact": "plan-validator", "contract": "plan-validator-v1"}],
   "consume": [{"artifact": "progressive-detail-rule", "contract": "progressive-detail-v1", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
   "focal_tests": ["tests/test_005_007_t2_progressive_plan_validator.py"],
   "regressions": ["tests/test_004_003_t3_plan_checks.py", "tests/test_004_003_t4_validation_fields.py", "tests/test_005_003_t6_packet_contract.py", "tests/test_packet_prepare.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "objective": "Abrir la feature/unidad siguiente del plan aprobado con una operacion del CLI (open-unit) que deje el state coherente, sin edicion manual del state.",
   "produce": [{"artifact": "open-unit-operation", "contract": "open-unit-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-start.md", "skills/cdad-cycle/references/orientation.md", "skills/cdad-cycle/assets/orientation-examples.json"],
   "focal_tests": ["tests/test_005_007_t3_open_unit.py"],
   "regressions": ["tests/test_005_003_t1_compact_view.py", "tests/test_005_003_t2_examples_execute.py", "tests/test_005_003_f2_idle_history.py", "tests/test_005_001_t3_idle.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "objective": "Materializar el informe del architect por el camino legitimo: la tabla cerrada admite su role report y el kind declarado de la interfaz de delegacion, conservando la clausura del eje rol y el binding de autorizacion.",
   "produce": [{"artifact": "architect-report-materialization", "contract": "artifact-policy-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_result.py", "skills/cdad-cycle/assets/artifact-policy.json"],
   "focal_tests": ["tests/test_005_007_t4_architect_report_materialization.py"],
   "regressions": ["tests/test_003_002_t2_materialize.py", "tests/test_003_002_t1_receive.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T5",
   "objective": "Reconocer como despacho la interfaz comun de delegacion por hechos materiales (invocacion real de cdad_delegate.py), sin inferirlo del texto de un comando que solo lo mencione.",
   "produce": [{"artifact": "delegation-dispatch-detection", "contract": "dispatch-detection-v1"}],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_context_meter.py", "skills/cdad-cycle/references/context-meter.md"],
   "focal_tests": ["tests/test_005_007_t5_delegation_dispatch.py"],
   "regressions": ["tests/test_005_002_t2_milestones.py", "tests/test_005_002_t4_acceptance.py", "tests/test_005_002_t1_neutral_record.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T6",
   "objective": "Alinear las plantillas con el resultado: la plantilla de spec parte del recorrido de uso y su aceptacion es comportamiento; existe la plantilla de plan de feature (ficha + plan-tasks) como consumidor del formato declarado.",
   "produce": [{"artifact": "aligned-templates", "contract": "templates-v1"}],
   "consume": [],
   "depends_on": ["T1"],
   "parallel": [],
   "files": [],
   "observable_checks": ["la plantilla de spec abre por el recorrido de uso (actor, objetivo, punto de partida legitimo, primer resultado util) y su aceptacion es comportamiento observable, sin el criterio de cobertura como requisito de contrato; existe skills/cdad-cycle/assets/feature-plan-template.md con la ficha y el bloque canonico plan-tasks, y ese bloque valida con el validador del producto"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "test-writer"},
  {"id": "T7",
   "objective": "Fijar el criterio de tamano de unidad por costo total (condiciones cualitativas, sin numeros) y vincular la regla de reintentos a la unidad sin duplicarla.",
   "produce": [{"artifact": "unit-size-criterion", "contract": "unit-size-v1"}],
   "consume": [],
   "depends_on": ["T1"],
   "parallel": [],
   "files": [],
   "observable_checks": ["el criterio de tamano declara condiciones verificables (reviewer no puede rechazar la unidad sin rechazar su vecina; no cierra su resultado con su consumidor nombrado; los costos fijos superan el avance marginal; fragmentacion) sin umbrales ni conteos inventados, referenciando el criterio de costo de coordinacion; re-entry.md (fuente unica) declara que un reintento sin informacion nueva dispara replanteo de la unidad, con el numero de intentos como senal y sin una segunda copia de la regla"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "test-writer"},
  {"id": "T8",
   "objective": "Gate de aceptacion de la feature: verificar AC-1..AC-6 y correr la medicion like-for-like (delta c) con el medidor y la sesion real nueva, declarando instrumento, procedencia y el bloqueo por despliegue si no esta autorizado.",
   "produce": [{"artifact": "acceptance-report", "contract": "acceptance-report-v1"}],
   "consume": [{"artifact": "open-unit-operation", "contract": "open-unit-v1", "producer": "T3"}, {"artifact": "architect-report-materialization", "contract": "artifact-policy-v1", "producer": "T4"}, {"artifact": "delegation-dispatch-detection", "contract": "dispatch-detection-v1", "producer": "T5"}],
   "depends_on": ["T3", "T4", "T5"],
   "parallel": [],
   "files": [],
   "observable_checks": ["el informe aplica las bandas como orientacion derivada de la linea base medida (no como umbral), con comparacion like-for-like sobre una sesion real nueva en reposo con la version desplegada; declara instrumento y procedencia; registra que los comandos sobre docs/.cdad-state.json pasan a una operacion del CLI y que el medidor observa el despacho por si solo; conserva lo no observable como unknown con causa; si el despliegue no esta autorizado declara BLOQUEO con responsable, nunca verde por proximidad"],
   "regressions": [],
   "integration_gate": "gate de aceptacion de la feature 005-007: AC-1..AC-6 verificados sobre los productos de T1..T7 y la medicion AC-7 con el artefacto del repo en solo lectura; el despliegue es del dueno y su ausencia es un BLOQUEO declarado",
   "owner": "orchestrator (medicion); architect (lectura)"}
 ]}
```

## 5. Trazabilidad PD/AC → tarea

PD-1 → T1, T2; PD-2 → T2; PD-3 → T7; PD-4 → T7; PD-5 → T6; PD-6 → T6; PD-7 → T3; PD-8 → T4; PD-9 → T5; PD-10 → T6 (receta) + T8 (gate); PD-11 → T8; PD-12 → T1, T3 (referencias); PD-13 → T2 (no reescribir despachados) + T7.
AC-1 → T2; AC-2 → T3; AC-3 → T4; AC-4 → T5; AC-5 → T6; AC-6 → T7; AC-7/AC-8 → T8.

## 6. Gate de aceptación de la feature

- **La feature cierra cuando** AC-1..AC-8 tienen evidencia: los focales de T2..T5 rojo→verde con su `git diff` acotado; las comprobaciones observables de T1/T6/T7 con la única fuente de cada regla; la **medición** de T8.
- **El gate de la feature es el de T8.** Con la **versión desplegada** y una **sesión real nueva en reposo**: se repite la medición de `acceptance.md` §9 y se declaran las bandas como **orientación**. **Mientras el despliegue no esté autorizado (acción del dueño), T8 devuelve BLOQUEO declarado**, nunca verde.
- **Mientras el medidor no esté instalado**, la medición se hace con el **artefacto del repo en solo lectura**; el despliegue queda fuera de esta feature.
- **Suite completa una vez**, por quien cierra, en un worktree fijado al commit de cierre; `make validate` sin fallos nuevos.

## 7. Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**; **sin desplegar**; **sin tocar HOME**; **sin leer** `tests/.sensitive-patterns.local`; **sin escribir en la base real de sesiones**.
- **Sin valores de este VPS** en spec, plan ni producto (INV-6).
- **No** reescribir los contratos de 005-002/005-009/005-010/005-001/005-005/005-003: extensión **aditiva y declarada** o referencia.
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia. Para comprobar un RED sin el arreglo: **worktree**, **nunca `git stash`** en el árbol compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**

## 8. Aprobación

**Estado: APROBADO.** Se aprobó **junto con la spec** (una sola acción) por el **orquestador OpenCode** el **2026-10-13**, bajo la HITL delegada del epic-005. El **architect** no aprobó su propia propuesta (entregó este plan como DRAFT). La firma y los hashes están registrados en `docs/.cdad-state.json` (`stage_history`, `stage: specification`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-13
