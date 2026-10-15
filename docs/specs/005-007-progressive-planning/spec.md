# Spec draft — 005-007-progressive-planning

**Feature ID:** `005-007-progressive-planning` · **Epic:** `epic-005-real-operation` · **Etapa:** 2 (specification), subetapa `draft`. **Estado: DRAFT — SIN APROBAR.** Lo aprueba el orquestador/usuario (bajo la HITL delegada del epic), no este rol (anti-sesgo, `sources/roles/architect.md`; ADR-003: el architect entrega TEXTO FINAL y el orquestador lo materializa).

**Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md`, fila 9 (`:42`), sha256 `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`, más la sección «Ajuste de los ciclos pendientes» (`:70-76`, 005-007).

**Insumos:** el informe de discovery ya recibido y verificado (`docs/specs/005-007-progressive-planning/discovery.md`, sha `dee290cf…`) y el delta aprobado por el dueño (`docs/specs/005-007-progressive-planning/draft-inputs-2026-10-13.md`). El discovery de 004-003/005-002/005-003 **no se repite**: se resuelve por referencia.

---

## 1. Descripción funcional

La feature transforma un objetivo amplio (una fila del plan del epic) en **el próximo trabajo ejecutable con contexto suficiente**, sin inflar el contexto ni fragmentar el avance. Se parte del **recorrido de uso** del dueño/coordinador, no de una firma de función ni de un porcentaje de cobertura:

1. **Petición inicial (una frase):** «abrí la próxima unidad del plan y dejamela lista para despachar, sin perder el alcance global ni inflar el contexto».
2. El coordinador arranca de un **repo en reposo** con el epic aprobado y features en cola; **una sola operación del CLI** abre la feature/unidad siguiente y deja el state coherente (hoy lo hace leyendo y editando `docs/.cdad-state.json` a mano: 15 comandos, el mayor de ~55 KB — `docs/specs/005-003-orientation-reduction/acceptance.md:143,153-157`).
3. El plan de la feature declara **el objetivo y las dependencias de todas las unidades completos**, y **el detalle (contrato/pruebas) solo de la tanda próxima**; las unidades futuras declaran su **incertidumbre con dueño y condición de resolución** en vez de detalle falso (`docs/epics/epic-004-single-source-planning/planning-contract-draft.md:33,55-56`).
4. El **tamaño de unidad** se decide por **costo total** (planeación + sesión + revisión independiente + integración + retrabajo), no por número de tareas, archivos ni líneas; una unidad que no mueve un resultado verificable es fragmentación, y una que no cierra su propio ciclo es sobredimensionada.
5. El **informe del architect** (discovery/spec/plan) se **materializa por el camino legítimo** (recepción + materialización), no con un `cp` a mano.
6. El **medidor de contexto** reconoce como **despacho** una invocación de la interfaz común de delegación, para que la aceptación de esta feature sea medible.

El **resultado del primer uso**: un encargo despachable (una unidad con resultado, dependencias y aceptación) preparado tras **una operación del CLI** y **una consulta de orientación**, con el plan de detalle progresivo válido para el validador del producto.

---

## 2. Contrato (interfaces propuestas para implementar, no existentes)

| Superficie | Comportamiento |
|---|---|
| **Regla de detalle progresivo** (hogar canónico, una vez) | El bloque canónico `plan-tasks` admite una tarea **planificada-no-detallada** marcada por un campo cerrado `detail`; la tarea marcada completa **objetivo + dependencias** y declara **incertidumbre + dueño + condición de resolución**, sin el plan de validación por tarea. La regla vive **en un solo lugar** y los consumidores la referencian. |
| **Validador del plan** (`cdad_packet.py`, `_check_plan_validation_plan`) | Acepta el plan de detalle progresivo **sin** debilitar el fail-closed ni los checks mecánicos (productor/consumidor, ciclo, contrato incompatible, paralelismo inseguro), y sin cambiar el comportamiento de un bloque sin marcador. |
| **Operación `open-unit` del CLI** (subcomando nuevo en `cdad_packet.py`) | Abre la **feature/unidad siguiente** del epic activo: selecciona la primera `queued` de `epic_features` (o `--feature <ID>` si es `queued`) y escribe atómicamente `active_feature`, el estado `in-progress`+`opened_at` de la entrada y `current_stage`; reusa el bootstrap existente para la ejecución. Conserva validaciones, autoridad y escritor único. La entrada `next-unit` de `status` apunta a ella. |
| **Tabla cerrada de materialización** (`cdad_result.py` + `artifact-policy.json`) | Admite el **informe del role report del architect** y el **kind declarado de la interfaz de delegación** (`role-report`), para que una entrega del architect (informe de discovery incluido) pase por `receive` + `materialize` sin `cp`. |
| **Detección de despacho del medidor** (`cdad_context_meter.py`) | La invocación **real** de la interfaz común `cdad_delegate.py` (shell) es un **despacho de trabajo de rol**, detectado por **hechos materiales** (el propio tool-call que invoca el programa, no una mención), con la misma clase de evidencia que la regla de `resume`; el conjunto reconocido y su método se **declaran**. |
| **Plantillas** (`assets/spec-template/spec.md`, `assets/feature-plan-template.md`) | La plantilla de spec **parte del recorrido de uso** y su aceptación es el **comportamiento** (no un `%` de cobertura); existe una **plantilla de plan de feature** (ficha + bloque `plan-tasks`) como consumidor del formato ya declarado. |
| **Criterio de tamaño de unidad** y **vínculo de la regla de reintentos a la unidad** | Texto canónico en las fuentes que ya poseen cada regla (§6): `stage-2-specification.md` (tamaño) y `re-entry.md` (reintentos). La spec **no** los copia. |

---

## 3. Postcondiciones (numeradas y verificables)

**PD-1 (detalle progresivo: objetivo y dependencias completos; detalle solo de la tanda próxima).** El bloque canónico `plan-tasks` admite, por tarea, un campo cerrado `detail` con valores `"next"` (default) y `"planned"`. Toda tarea declara **siempre** un `objective` no vacío y sus `depends_on`. Una tarea con `detail == "planned"` declara además `uncertainty` (no vacía), `owner` (no vacío) y `resolves_when` (no vacía), y **no** está obligada a declarar `focal_tests`/`observable_checks`/`regressions`/`integration_gate`; una tarea `"next"` o sin marcador sigue declarando el plan de validación por tarea. La regla se enuncia **una sola vez** en su hogar canónico (§6/D1) y los consumidores la referencian. *(Hoy el validador exige el plan de validación por tarea para **todas** las tareas: `skills/cdad-cycle/scripts/cdad_packet.py:3063-3105`.)*

**PD-2 (el validador acepta el detalle progresivo sin debilitar el fail-closed).** `_check_plan_validation_plan` trata una tarea `detail == "planned"` por sus campos propios (PD-1) y exige el plan de validación por tarea solo a las `"next"`/sin marcador. Los checks mecánicos (`_check_plan_tasks`: entrada sin productor, ciclo, contrato incompatible, paralelismo inseguro) siguen aplicándose a **todas** las tareas declaradas, incluidas las `planned`. Un `detail` con valor fuera del conjunto cerrado **falla cerrado** nombrando la tarea y el valor; un bloque `plan-tasks` malformado o ausente sigue fallando cerrado, sin publicar paquete (`cdad_packet.py:2883-2942,2945-3060`). Un bloque sin el marcador se comporta **exactamente** como hoy. *(Resuelve VERIFY 1 y 2 del discovery §11.)*

**PD-3 (tamaño de unidad por costo total, cualitativo y verificable, sin números inventados).** La regla de tamaño declara condiciones **verificables** (no una puntuación opaca): una unidad es inválida si (a) un reviewer no podría rechazarla sin rechazar su vecina, (b) no cierra su propio resultado verificable con su **consumidor nombrado**, (c) sus **costos fijos** (planeación + apertura de sesión + revisión independiente + integración) superan el avance marginal que entrega, o (d) no mueve la feature hacia un resultado verificable (fragmentación). El criterio se enuncia **una vez** en su hogar canónico y reusa, por referencia, el criterio de «costo de coordinación» de `planning-contract-draft.md:155`. **Sin** umbrales numéricos, sin mínimo de tareas, sin límite universal de archivos ni líneas. *(Resuelve VERIFY 4.)*

**PD-4 (la regla de reintentos se vincula a la unidad, sin copiarla).** Un reintento que **no** aporta información nueva sobre una unidad dispara una **revisión de estrategia** que puede **replantear la unidad** (tamaño, frontera o detalle), reconciliada con la regla vigente de dos intentos; el número de intentos es una **señal**, no el criterio. La regla se edita **una vez** en su fuente canónica (`skills/cdad-cycle/references/re-entry.md:79`) y los consumidores la referencian; el plan aplica el disparador a nivel de unidad **por referencia**. *(Hoy la regla existe y es correcta; sólo falta el vínculo con la unidad a nivel de plan — `discovery.md:230-235`.)*

**PD-5 (la plantilla de spec parte del recorrido de uso; la aceptación es comportamiento, no cobertura).** `assets/spec-template/spec.md` abre con la **descripción funcional derivada de un recorrido de uso** (actor, objetivo, punto de partida legítimo, primer resultado útil) y sus criterios de aceptación son **comportamiento observable sobre ese recorrido**; el ítem de aceptación «Line coverage ≥ X%» **no** es criterio de contrato. *(Hoy la plantilla abre por `Signature` y su aceptación incluye cobertura: `skills/cdad-cycle/assets/spec-template/spec.md:17-21,41`; el patrón «spec desde el recorrido» ya se usó en `005-006/spec.md:36-60,plan.md:103-120` sin formalizarse.)*

**PD-6 (plantilla de plan de feature declarada una vez).** Existe una **plantilla de plan de feature** (`assets/feature-plan-template.md`) con la **ficha** y el **bloque canónico `plan-tasks`**; el **formato** del bloque sigue declarado una sola vez en `planning-contract-draft.md` §4.1 y la plantilla lo **referencia** (es un consumidor, no una segunda regla). *(Resuelve VERIFY 5; hoy no existe plantilla de plan de feature y los planes reales se escriben a mano — `discovery.md:176-179`.)*

**PD-7 (abrir la feature/unidad siguiente por el CLI, sin editar el state a mano).** Una operación del CLI (`cdad_packet.py open-unit`, subcomando nuevo) abre la próxima unidad del plan aprobado y deja el state coherente:
- **selección:** sin `--feature`, la **primera** entrada de `epic_features` con `status == "queued"` (el orden del plan es la autoridad); con `--feature <ID>`, esa entrada, que debe existir y estar `queued`;
- **efecto atómico:** `active_feature = <ID>`; en la entrada, `status = "in-progress"` y `opened_at = <fecha>`; `current_stage = discovery` (la etapa de entrada); `epic_stage` sin cambios;
- **conserva validaciones:** antes de publicar corre la **misma** validación de vigencia/coherencia del state (`_validate_v2_vigency`/`validate_state`); un estado incoherente o una unidad no abrible **falla cerrado** con diagnóstico accionable, sin escribir;
- **conserva autoridad:** **no** aprueba nada, **no** fabrica autoridad, **no** toca política, HITL ni versión;
- **escritor único:** escribe bajo el **mismo lock** del proyecto y con escritura atómica; el orquestador **no** edita el state;
- **precondición:** estado en reposo legítimo (`active_feature` nulo ⇔ `current_stage == idle`); con una unidad ya abierta, **rechaza** con diagnóstico (no cambia de unidad en silencio);
- la ruta de la entrada `next-unit` de `status` **nombra** esta operación; `project-start.md` §6 (dueño canónico del procedimiento de arranque) la documenta **por referencia**.
*(Delta 1; `draft-inputs-2026-10-13.md:17-21`; `acceptance.md:153-157`.)*

**PD-8 (el informe del architect se materializa por el camino legítimo).** La tabla cerrada de materialización admite el **informe del architect**: el `artifact_kind` del role report del architect queda en la política cerrada (`artifact-policy.json`) y en el eje rol/subfase (`_allowed_kinds`), y el **kind declarado de la interfaz común de delegación** (`role-report`, único valor que hoy emite el adaptador OpenCode) es materializable. Con eso, una entrega del architect (el **informe de discovery** incluido) recibida —directamente o por `cdad_delegate.py`— se materializa a `docs/specs/<feature>/discovery.md` vía `receive` + `materialize`, con **sha idéntico** a la parte recibida y **sin** `cp`. Se conservan: el destino dentro de `docs/specs/<feature>/`; el binding de autorización (`execution_id`/`packet_id`/`receipt_sha256`/`authority_ref`); `approval_effect == false`; y el rechazo de un **kind nombrado de otro rol** (`cdad_result.py:632-650,653-692,795-894`). *(Delta 2; el hecho medido del despacho anterior: la parte del informe llevó `artifact_kind: role-report` — `.cdad/runtime/results/exec-005-007-progressive-planning-001/005-007-progressive-planning-architect-discovery-001/receipt.json`.)*

**PD-9 (el medidor reconoce la interfaz común de delegación como despacho, por hechos materiales).** El medidor reconoce como despacho, además de `subagent`/`task`, una llamada de herramienta `shell` que **invoca realmente** el programa de la interfaz común de delegación (`cdad_delegate.py` con sus argumentos de delegación); es la **misma clase de evidencia** que ya usa la detección de `resume` (`cdad_context_meter.py:775-799`). **No** cuenta una llamada que sólo **menciona** el programa en sus argumentos o contenido (p. ej. el contenido de un `write` o un `grep`), ni una llamada de ayuda (`--help`/`-h`). El registro **declara** el conjunto reconocido y el **método** de cada entrada (con procedencia); una ausencia sigue siendo `absent`/`unknown` **con causa** que nombra el límite honesto; un despacho sigue siendo un **evento**, nunca prueba de utilidad ni de resultado aceptado (PD-6 de 005-002 preservado, `005-002/spec.md:271-280`). *(Delta 3; sin esto la aceptación de 005-007 no es medible — `acceptance.md:160-162`.)*

**PD-10 (aceptación de uso diferenciada; el despliegue queda del dueño).** La aceptación distingue tres capas con productor, actor evaluador y evidencia (contrato / integración / uso) y aplica la **receta mínima** (actor = agente en sesión fresca, objetivo, punto de partida legítimo, entorno/versión, evidencia de éxito; camino principal + un bloqueo/recuperación; separar comprobación repetible de observación exploratoria). La capa de **contrato** y la de **integración** se evidencian dentro de la feature; la **medición de uso con la versión desplegada** es la meta del delta (PD-11) y, mientras no haya despliegue, se declara **BLOQUEO con responsable (dueño)**, nunca verde por proximidad. *(`discovery-inputs.md:82-102`; `discovery.md:424-451`.)*

**PD-11 (meta de aceptación: orientación, no umbral).** Se repite la medición de `docs/specs/005-003-orientation-reduction/acceptance.md` §9 con una **sesión real nueva en reposo** y la **versión desplegada después de esta feature**: reducir las **llamadas** y la **salida** previas al primer despacho —en especial los **comandos sobre `docs/.cdad-state.json`**, que deben pasar a **una** operación del CLI— y que el **medidor detecte el despacho por sí solo** (`first_dispatch` observado). La meta numérica es **orientación derivada** de la línea base medida, **no** un umbral que acepte o rechace por sí solo; el **instrumento** (medidor del repo, 005-002, más el conteo propio sobre las partes `tool`) y su **procedencia** se declaran; lo **no observable** se conserva `unknown` con causa (nunca `0`).

**PD-12 (fuente única: la spec no agrega una segunda copia de una regla existente).** Cada regla que ya tiene dueño (equivalencia de evidencia, política de suite, reintentos, formato `plan-tasks`, unidad despachable, aprobación por rol) se **referencia**; ninguna se re-enuncia como texto normativo nuevo. *(Invariante de fuente única de 004-003: `docs/specs/004-003-planning-procedures/spec.md:55,84-91`.)*

**PD-13 (la replanificación mantiene trazabilidad y no reescribe contratos despachados).** Replanificar una unidad (PD-3/PD-4) conserva el objetivo y las razones, y **no** modifica un contrato ya despachado sin **reconciliación** declarada; el estado «planificada-no-detallada» (PD-1) es una representación de plan, **no** una autorización de construcción ni un cambio de un contrato en vuelo. *(Restricción dura: `discovery-inputs.md:137-138`.)*

---

## 4. Invariantes verificables

- **INV-1 (autoridad y anti-sesgo).** El architect **no** aprueba su propuesta (esta spec sale **sin** marca de aprobación); la aprobación y la revisión independiente se conservan; la familia del reviewer ≠ la del implementer; el test-writer nunca ve la implementación. `open-unit` y `materialize` **no** aprueban nada (`approval_effect` sigue `false`).
- **INV-2 (fuente única).** Una fuente editable por regla; consumidores por referencia; sin edición manual de salidas generadas (`agents/` es salida declarada de `scripts/cdad-generate.py` — `Makefile:1-6`).
- **INV-3 (escritor único y escritura atómica del state).** El state lo escriben **sólo** el CLI del producto (`prepare`, y `open-unit`); el orquestador no lo edita; toda escritura es atómica y bajo el lock del proyecto (patrón existente `_publish_generation`/`_atomic_write_bytes`).
- **INV-4 (fail-closed).** Un bloque `plan-tasks` malformado/ausente, un `detail` fuera del conjunto cerrado, una unidad no abrible, un kind fuera de la tabla cerrada y un destino fuera de la raíz permitida **fallan cerrado** (`rc≠0`, diagnóstico que nombra el campo/límite) sin dejar prefijo parcial.
- **INV-5 (compatibilidad byte a byte).** Sin el campo `detail`, el bloque `plan-tasks` y el render del paquete son idénticos a hoy; sin `plan_task`, el render es byte-idéntico (`005-003` T6); `receive`/`materialize` de los kinds existentes y el registro neutral del medidor sin las banderas nuevas no cambian.
- **INV-6 (sin valores ni efectos de este VPS).** Sin rutas de HOME, sin rutas absolutas del host, sin proveedor/modelo concretos en producto ni contratos; **sin desplegar**, **sin tocar HOME**, **sin push**, **sin escribir en la base real de sesiones**.
- **INV-7 (desconocido conservado).** Lo no observable queda `unknown` **con causa**, nunca `0` ni subtotal presentado como total (regla de `005-002`).
- **INV-8 (trazabilidad de la replanificación).** PD-13; el estado progresivo no borra objetivo, dependencias ni razones.
- **INV-9 (proporcionalidad de la validación).** Se reutiliza evidencia equivalente con procedencia verificada (regla canónica `re-entry.md:67-77`); la suite completa la corre **una vez** quien cierra; sin `--no-verify`.

---

## 5. Criterios de aceptación medibles

La aceptación de esta feature es **comportamiento observable sobre el recorrido de §1**, no un porcentaje de cobertura.

1. **AC-1 (detalle progresivo).** `prepare` valida un plan que declara una tarea `detail == "planned"` con objetivo + dependencias + incertidumbre + dueño + condición de resolución y **sin** plan de validación por tarea; rechaza (rc≠0) una tarea `planned` a la que le falta `uncertainty`/`owner`/`resolves_when` o `objective`, y una con un `detail` fuera del conjunto; los checks mecánicos se siguen aplicando a todas las tareas; un plan **sin** marcador pasa exactamente como hoy (regresión).
2. **AC-2 (apertura por CLI).** Desde un estado en reposo, **una** invocación de `open-unit` abre la primera feature `queued` y deja el state coherente (`validate-state` verde); **cero** ediciones manuales del state; la ruta `next-unit` de `status` nombra la operación; una segunda invocación (unidad ya abierta) y una feature no `queued` se rechazan con diagnóstico; el diff del repo sólo toca `docs/.cdad-state.json` (más los artefactos que el seguimiento del ciclo ya escribe).
3. **AC-3 (materialización legítima del informe).** El informe de discovery del architect (parte ya recibida, sha `dee290cf…`) se materializa a `docs/specs/005-007-progressive-planning/discovery.md` vía `receive` (idempotente, ya hay recibo) + `materialize`, con **sha idéntico** y **sin** `cp`; un kind **nombrado** de otro rol (p. ej. `implementer-role-report` para el architect) sigue rechazándose; el destino fuera de `docs/specs/<feature>/` sigue rechazándose.
4. **AC-4 (despacho por la interfaz de delegación).** Sobre una traza cuyo primer despacho es una invocación real de `cdad_delegate.py`, el medidor reporta `first_dispatch` **observado** en esa posición, con el método declarado; una traza que sólo **menciona** el programa (p. ej. un `write` o un `grep`) reporta `absent` con causa; el registro neutral sin las banderas nuevas es idéntico (regresión).
5. **AC-5 (plantillas).** La plantilla de spec abre por el recorrido de uso y su aceptación es comportamiento (sin «Line coverage ≥ X%»); existe la plantilla de plan de feature con ficha + bloque `plan-tasks` y su bloque valida con el validador del producto.
6. **AC-6 (tamaño y reintentos).** El criterio de tamaño por costo total y el disparador de replanteo por unidad están en sus fuentes canónicas, por referencia, **sin** umbrales numéricos inventados; un reintento sin información nueva sobre una unidad se declara como disparador de replanteo de la unidad.
7. **AC-7 (meta de aceptación; orientación).** La medición like-for-like (PD-11) con una **sesión real nueva en reposo** y la versión desplegada reporta: **una** operación del CLI sobre el state en lugar de 15 comandos; reducción de llamadas y salida previas al primer despacho frente a la línea base de `acceptance.md:136-143`; y `first_dispatch` **observado por el medidor**. Las bandas son **orientación** (no umbral); el instrumento y su procedencia se declaran; lo no observable queda `unknown` con causa. Mientras no haya despliegue (acción del dueño), se declara **BLOQUEO**, no verde.
8. **AC-8 (cierre).** Suite completa **una vez** por quien cierra, en un worktree fijado al commit de cierre; validadores sin fallos nuevos (`make validate`); commits de cada rol; sin `--no-verify`, sin push, sin desplegar.

---

## 6. Decisiones (con fundamento)

- **D1 — Hogar canónico de la regla de detalle progresivo: `skills/cdad-cycle/references/stage-2-specification.md`** (la skill instalada), con el **campo de formato** declarado una sola vez en `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1 (que ya es la declaración del bloque `plan-tasks` referenciada por los planes, `stage-2-specification.md:112`). *Fundamento:* hoy la regla vive **sólo** como borrador del epic-004 y **no** en la skill instalada (`discovery.md:139-162`); cada superficie posee una cosa (la regla vs el formato) y ninguna se duplica. *Alternativa declarada:* un asset `plan-tasks.schema.json` como formato único — más limpio pero más superficie; se difiere a deuda salvo que el owner lo prefiera.
- **D2 — Representación de «planificada-no-detallada»: un campo cerrado por tarea `detail` (`"next"` | `"planned"`).** *Fundamento:* es **aditivo**, **fail-closed** ante valor desconocido, compatible byte a byte cuando está ausente, y **no** crea ontología ni máquina de estados (VERIFY 1/2). Evita la alternativa de «alcance todo el bloque a la próxima tanda», que perdería la cobertura global (dependencias completas) que la fila 9 exige.
- **D3 — Criterio de tamaño por costo total: condiciones cualitativas declaradas, sin números.** *Fundamento:* el dueño rechazó la puntuación opaca con números inventados (`discovery-inputs.md:48`; VERIFY 4); las condiciones son verificables por el reviewer sin instrumento nuevo.
- **D4 — El vínculo reintentos↔unidad se edita en `re-entry.md`** (dueño único de la regla). *Fundamento:* invariante de fuente única (`004-003/spec.md:55`); los planes lo referencian.
- **D5 — Plantilla de plan de feature como asset nuevo** (`assets/feature-plan-template.md`), referenciada por `stage-2-specification.md`. *Fundamento:* VERIFY 5; hoy el formato se repite a mano en 4+ planes (`discovery.md:176-179`); los assets son la superficie instalada.
- **D6 — Delta 1 como subcomando nuevo `open-unit`** (no sobrecargar `prepare`). *Fundamento:* los sub-modos de `prepare` son mutuamente excluyentes y su trabajo es **renderizar** un paquete (`cdad_packet.py:4002-4103`); abrir es una operación de **estado**; el subcomando **reusa** `_bootstrap_v2_execution` para la ejecución, sin duplicar el camino de preparación.
- **D7 — Delta 2 extendiendo la tabla cerrada con el informe del architect y el kind de la interfaz (`role-report`), sin cambiar el adaptador.** *Fundamento:* cambiar el adaptador para emitir kinds por rol **duplicaría** el mapa rol→kind que ya posee `cdad_result.py` (violaría fuente única); el kind genérico lo declara la propia interfaz (`cdad_delegate_opencode.py:99`); así la mejora cubre **toda** entrega por la interfaz, no sólo al architect.
- **D8 — Delta 3 por la invocación real (misma clase que la regla de `resume`), sin acoplar el medidor a un ledger.** *Fundamento:* PD-6 prohíbe inferir por **texto que sólo menciona**; la invocación es un hecho material del tool-call y ya es la clase de evidencia usada para `resume`; el medidor sigue siendo lector de sesiones (no gana dependencia del proyecto). El refuerzo por el ledger durable se declara como deuda opcional (D-4).
- **D9 — Receta de aceptación de uso acotada:** una sección en `stage-2-specification.md` referenciada por la plantilla de spec; la **observación real** la hace el orquestador en el gate. *Fundamento:* `discovery-inputs.md:98-102,122-126` (no volverla evaluador de usabilidad general ni plataforma).
- **D10 — Los tres puntos del delta entran como alcance, no como deuda.** *Fundamento:* la aceptación de 005-007 **depende** de ellos (el state sin editar, la materialización del informe, el medidor que detecta el despacho); la deuda se reserva a lo que no cambia ese resultado (VERIFY 6/7, refuerzo por ledger, medición desplegada).

---

## 7. Alcance y fuera de alcance

**Dentro.**
1. Regla de detalle progresivo con hogar canónico + campo `detail` (D1/D2), consumidores por referencia.
2. Reconciliación del validador del `plan-tasks` con el detalle progresivo, preservando fail-closed y checks mecánicos (PD-2).
3. Criterio de tamaño de unidad por costo total (PD-3) y vínculo reintentos↔unidad (PD-4).
4. Plantilla de spec desde el recorrido de uso (PD-5) y plantilla de plan de feature (PD-6).
5. **Delta 1:** subcomando `open-unit` (PD-7) + ruta `next-unit` de `status` + `project-start.md` §6 por referencia.
6. **Delta 2:** tabla cerrada + `artifact-policy.json` admiten el informe del architect y el kind de la interfaz (PD-8).
7. **Delta 3:** el medidor reconoce la interfaz de delegación como despacho (PD-9) + la declaración de su método en el registro.
8. Receta mínima de aceptación de uso (PD-10) y la **meta de aceptación** del delta (PD-11).

**Fuera.**
- Agente/planner obligatorio; perfiles de modelo nuevos; aislamiento por repo para todos los agentes; servicios permanentes; UI nueva; scheduler; plataforma de usabilidad; evaluador de usabilidad general; CI (`plan.md:25-27`; `discovery-inputs.md:128-138`).
- Reescribir los contratos de 005-002 (medidor), 005-009/005-010 (interfaz de delegación), 005-001/005-005 (contratos de paquete) o 005-003 (orientación): esta feature los **extiende de forma aditiva y declarada** o los referencia.
- Desplegar la versión, tocar HOME, `git push`, escribir en la base real de sesiones, `--no-verify`.
- Un rediseño del ledger/state del ciclo, un segundo state, o un productor paralelo de paquetes.
- Migrar el formato del estado, separar el historial, o un dashboard.

---

## 8. Deuda declarada (con condición de cierre)

- **D-1 — Medición de uso con la versión desplegada.** Requiere **desplegar** (acción reservada al dueño). *Cierre:* autorización de despliegue del dueño + una sesión real nueva en reposo medida **like-for-like** contra `acceptance.md` §9 (AC-7). Mientras tanto: **BLOQUEO declarado**, no verde.
- **D-2 — VERIFY 6 del discovery (sesión de cierre de 005-001 `unknown` en el medidor).** *Cierre:* n/a (no afecta a 005-007); se conserva citado como desconocido.
- **D-3 — VERIFY 7 (ruta del CLI en Claude Code para el ciclo real de 005-004).** Fuera de esta feature. *Cierre:* 005-004 (o el ciclo que lo resuelva).
- **D-4 — Refuerzo material de la detección de despacho (corroboración con el ledger durable `dispatches/<attempt>.json`).** Fuera de esta feature (mantiene al medidor como lector de sesiones). *Cierre:* sólo si se observa un **falso negativo real** (una invocación oculta por un wrapper que no expone el token del programa); entonces se abre el refuerzo con su test focal.
- **D-5 — Formato del bloque como asset `plan-tasks.schema.json` (alternativa de D1).** *Cierre:* si el owner prefiere el schema único sobre la declaración en `planning-contract-draft.md` §4.1.
- **D-6 — Deuda heredada de 005-003 (F2/_pending_work) y F3 (un asset de instrucción invalida paquetes publicados).** No se reabren aquí; se citan. *Cierre:* por su feature/owner. Nota: `open-unit` (PD-7) **no** depende de la cláusula en disputa de F2; se apoya en la coherencia de reposo que `_validate_idle_coherence` ya impone (`cdad_packet.py:501-536`).

---

## 9. Referencias (contrato y reglas reusadas)

- Contrato (fila 9): `docs/epics/epic-005-real-operation/plan.md:42`; ajuste 005-007: `:70-76`; alcance/fuera del epic: `:22,25-27`; criterios de aceptación del epic: `:87-108`.
- Delta aprobado (los tres puntos y la meta): `docs/specs/005-007-progressive-planning/draft-inputs-2026-10-13.md:17-29,31-36`.
- Discovery (insumo principal): `docs/specs/005-007-progressive-planning/discovery.md` §1.2 (`:107-137`), §1.3 (`:139-162`), §1.4 (`:164-192`), §7 (`:424-451`), §9 (`:497-507`), §11 (`:530-547`).
- Encargo y límites duros: `docs/specs/005-007-progressive-planning/discovery-inputs.md:36-48,61-102,128-138`.
- Formato `plan-tasks` y regla del borrador: `docs/epics/epic-004-single-source-planning/planning-contract-draft.md:30-39,43-60,87-138`; «detalle solo próxima tanda» `:33,55-56`; costo de coordinación `:155`.
- Validador del producto: `skills/cdad-cycle/scripts/cdad_packet.py:2883-2942` (parseo fail-closed), `:2945-3060` (checks mecánicos), `:3063-3105` (plan de validación por tarea), `:3114` (`PLAN_RELPATH_TEMPLATE`), `:3429-3588` (`prepare`), `:3914-3982` (subcomandos), `:4002-4103` (sub-modos exclusivos), `:501-536` (coherencia de reposo).
- Materialización: `skills/cdad-cycle/scripts/cdad_result.py:493-589` (`receive`), `:608-629` (política cerrada), `:632-650` (tabla rol/subfase), `:653-692` (autorización), `:795-894` (`materialize`); `skills/cdad-cycle/assets/artifact-policy.json:1-16`.
- Medidor: `skills/cdad-cycle/scripts/cdad_context_meter.py:147-151` (conjunto declarado), `:173-186` (causas de ausencia), `:775-799` (regla de invocación de `resume`), `:814-818` (`_find_dispatch`), `:1463-1484` (flags); contrato: `docs/specs/005-002-session-context-meter/spec.md:271-280` (PD-6), `:404-408` (INV-9).
- Reglas reusadas (por referencia): unidad despachable (`sources/roles/orchestrator.md:84-89`; `003-007/spec.md:140-150`); tamaño de unidad (`skills/cdad-cycle/references/stage-2-specification.md:102-113`); reintentos (`skills/cdad-cycle/references/re-entry.md:79`); equivalencia de evidencia (`re-entry.md:67-77`); política de suite (`skills/cdad-cycle/packets/common.md`); aprobación por rol (`005-001`, `005-005`); equivalencia/plan-review (`docs/specs/004-003-planning-procedures/spec.md:26-29,31-57,59-67`; `skills/cdad-cycle/packets/substages/reviewer-plan-review.md`).
- Plantillas actuales: `skills/cdad-cycle/assets/spec-template/spec.md:17-21,41`; ausencia de plantilla de plan de feature (`discovery.md:176-179`).
- Orientación (consumidor de PD-7): `docs/specs/005-003-orientation-reduction/spec.md:109-138` (§2.2), `:326-345`; `skills/cdad-cycle/references/project-start.md:74-138`; `skills/cdad-cycle/references/orientation.md:29`.

---

## 10. VERIFY: resueltos y conservados (discovery §11)

| # | Tema | Disposición en esta spec |
|---|---|---|
| 1 | Representación de «planificada-no-detallada» | **RESUELTO**: D2 (campo cerrado `detail`), PD-1/PD-2, AC-1. |
| 2 | Punto exacto de reconciliación del validador + test de regresión | **RESUELTO**: `_check_plan_validation_plan` (`cdad_packet.py:3063-3105`), PD-2, tarea T2 y su focal. |
| 3 | Alcance de la receta de aceptación de uso y su parte pendiente por despliegue | **RESUELTO**: PD-10 (receta mínima) + D-1 (BLOQUEO por despliegue). |
| 4 | Criterio de tamaño por costo total sin números inventados | **RESUELTO**: PD-3 (condiciones cualitativas declaradas). |
| 5 | Plantilla de plan de feature (asset vs formalizar el formato) | **RESUELTO**: D5/PD-6 (asset nuevo). |
| 6 | Sesión de cierre de 005-001 `unknown` en el medidor | **CONSERVADO**: D-2 (no afecta a 005-007). |
| 7 | Ruta del CLI en Claude Code (005-004) | **CONSERVADO**: D-3 (fuera de esta feature; 005-004). |

---

## 11. Aprobación

**Estado: APROBADA.** El **architect** no aprueba su propia propuesta (anti-sesgo: entregó esta spec como DRAFT). La **aprobó el orquestador OpenCode** el **2026-10-13** bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md`), junto con el `plan.md` en una sola acción. Rige el **criterio de review vigente del 2026-10-12** (`docs/epics/epic-005-real-operation/execution.md:48-56`); el **orquestador Claude revisa** antes de la etapa 3 (la spec de esta feature entra a TDD revisada por Claude). La firma de la aprobación y sus hashes están registrados en `docs/.cdad-state.json` (`stage_history`, `stage: specification`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-13
