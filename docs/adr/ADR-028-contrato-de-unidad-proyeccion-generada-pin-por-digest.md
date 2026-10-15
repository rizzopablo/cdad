# ADR-028: El contrato del architect es una proyección GENERADA de la unidad, pineada por digest, con fallback declarado al plan completo; el veredicto de consecuencias es por identidad y clase de parte y `status` sigue siendo de solo lectura

- **Status**: Proposed
- **Date**: 2026-10-14
- **Deciders**: orquestador OpenCode (HITL delegada epic-005) + architect (spec/plan) + orquestador Claude (review de la spec, cierre y suite de cierre)
- **Confidence**: Media
- **Aprobación**: orquestador OpenCode bajo la delegación HITL del epic-005
  (`docs/epics/epic-005-real-operation/execution.md`), el **2026-10-14**, a partir del borrador del scribe. Evidencia disponible: spec `4369822e…` y plan `89d5d8cf…` aprobados juntos; review formal **1 bloqueante / 5 opcionales / 1 abstención** con B1 **corregido ya**; gate T4 **aprobado** (prueba decisiva con el CLI real en tres formas de plan); suite de cierre **960 passed / 4 skipped** en `7ab16ba` y `make validate` **155 PASS / 1 FAIL** (F011 preexistente). **La confianza es Media** porque: (i) el comportamiento nuevo **no existe en la versión instalada** (el generador lee el activo co-ubicado con el script; las raíces instaladas **no** declaran las anclas — O3), así que hace falta **desplegar**; (ii) B1 fue un **defecto real** que la review **reprodujo y midió** (una proyección publicada reescrita, `2237d30d… → cec98be9…`, pin roto) — la corrección está verificada por 3 casos nuevos, pero muestra que el mecanismo tenía un hazard real; (iii) la **fila 13 (b)** quedó **acotada** (cambiar una restricción da `impact`, no `impeded`: el CLI no juzga la inmediatez sin una marca estructural); (iv) O2..O5 siguen abiertas.

## Contexto y problema

El pin que bloqueaba el trabajo en curso era el **del paquete**: `contract.sha256` del `REQUEST.json` y `active_packet.contract_sha256`, re-verificados contra los **bytes actuales** del archivo del contrato por `validate_request` — punto único de `prepare`, `render`, `validate-request`, `validate-packet`, `--resume-packet` y `receive`. Para el architect ese archivo era **el plan del epic completo**: cualquier edición del plan —incluida **agregar una unidad futura independiente**— cambiaba su sha y dejaba **irrecibible** una entrega correcta (medido: `receive` rc=2 «contract sha256 does not match exact content»). El pin **bloqueaba globalmente la planificación del proyecto**. La aprobación del architect no pinea hash (`epic_history` `epic-plan`, sin pin, D2) y `plan_sha256` de `epic_history` no tenía consumidores.

La pregunta de arquitectura: **¿qué debe identificar el hash de un contrato de unidad, de modo que la planificación del proyecto deje de bloquearse sin habilitar atajos (omitir gates, aprobar al recibir, declarar válido un contrato cambiado)?**

## Opciones consideradas

### Opción A: la proyección de unidad GENERADA, publicada una vez y pineada por digest; el sha del plan como procedencia (ADOPTADA)

- Pros: el hash depende **sólo de lo que la unidad recibe** (objetivo/alcance/aceptación + restricciones compartidas + aprobación y versión de origen); la planificación se desbloquea sin tocar el pin de la spec de los roles de construcción; se persisten los bytes (evita el hazard de byte-identidad: `_plan_task_sections` re-resuelve el plan en cada render y `_resume_packet` compara contra el render canónico); la ubicación junto al paquete la hace **inmutable** por construcción (INV-3 de 005-001).
- Contras: una pieza nueva (el generador, la declaración de anclas del producto, un kind nuevo, un bloque aditivo de la vista); exige **declarar** el fallback y la frontera.

### Opción B: re-generar la proyección en cada validación

- Contras: reintroduce el hazard de byte-identidad verificado en el discovery §3. **Rechazada.**

### Opción C: generar por unidad con ruta fija

- Contras: una segunda generación para la misma unidad (los paquetes de discovery y draft del architect) **sobrescribiría** la primera. **Rechazada.**

### Opción D: reusar `approved-epic-plan` con un path nuevo

- Contras: un `kind` que **miente** sobre su `path` (peor diagnóstico). **Rechazada** (se creó el kind `approved-unit-contract`).

### Opción E: fallar cerrado cuando la unidad no se localiza sin ambigüedad

- Contras: es la **regresión** de B1 de la review del orquestador Claude (rompe el uso previsto en cualquier plan con otra forma). **Rechazada** (se adoptó el **fallback declarado** al plan completo).

### Opción F: publicar una proyección del plan completo en el fallback

- Contras: mentiría sobre el `kind` y forzaría el churn de oráculos. **Rechazada.**

### Opción G: mantener listas de títulos por proyecto / localizar por el título de la sección / por igualdad exacta de la celda

- Contras: es la **fragilidad de B1**: la plantilla del producto usa «Decomposition into features»/«Feature ID»/«Plan changes» y los planes reales del repo usan títulos distintos («Entregas del MVP», «Descomposición candidata», «Feature ID»); otros proyectos usan la celda como enlace y no declaran historia. **Rechazada** (localizador **estructural** + anclas por **declaración del producto**).

### Opción H: una marca estructural declarada en cada plan para la «restricción de aplicación inmediata»

- Contras: exigiría **editar todos los planes existentes** (regresión). **Rechazada**; queda como deuda D-3 (la inmediatez la juzga la review/orquestador).

### Opción I: que `status` escriba el registro de impacto, o que lo escriba cualquiera de las operaciones

- Contras: viola el contrato de solo lectura de 005-003/005-011 y hace el veredicto no reproducible. **Rechazada** (el journal lo escribe **sólo** `validate-unit-contract` y es **idempotente**).

## Decision

1. **El contrato de una unidad con epic activo es una proyección GENERADA del plan**, publicada **una vez**, durable, en `.cdad/packets/<packet_id>/UNIT-CONTRACT.md`, y **pineada por su digest**: `contract = {kind: "approved-unit-contract", path, sha256, commit: null}` y `active_packet.contract_sha256` = ese digest. El **sha del plan** queda como **procedencia** (bloque de origen). La proyección contiene: el **bloque de origen** (unidad, plan, sha del plan al generar, `approved_by` de la entrada `epic_history` `epic-plan`, `policy_sha256`, la lista de partes con su clase y la traza del localizador y de las anclas) + la **parte `unit`** (encabezado de la tabla que localizó la unidad + la fila de la unidad, verbatim) + las **partes `shared`** (todas las secciones de nivel `##` verbatim, **excepto** las que la declaración del producto reconoce como **historia**, y con las líneas de la tabla localizada removidas de su sección).
2. **Localizador estructural:** la unidad es la **única** fila de cuerpo de una tabla del plan que contiene el id de la feature **como token completo** (delimitado por caracteres que no pueden ser parte de un id); la celda puede ser texto plano, un **enlace** o estar entre backticks. **No** se mira el título de la sección ni se exige igualdad exacta de la celda. **Ambigüedad → fallback declarado:** cero o más de una fila ⇒ **no** se publica proyección, el contrato vuelve al **vigente** (`approved-epic-plan`, el plan completo) y el motivo se informa en el **diagnóstico** (stderr) y en `status` (`mode: "fallback"`); `prepare` **rc=0** (no falla cerrado).
3. **Anclas por declaración del producto:** historia y autorización se reconocen contra la declaración **legible por máquina** del activo del producto (la plantilla del plan de epic), **nunca** contra listas por proyecto. Historia ⇒ excluida de la proyección; autorización ⇒ incluida como parte `shared` **etiquetada** en el origen y **sin efecto de veredicto** (la clase `authority` **no existe**). Declaración ausente/ilegible ⇒ ninguna ancla (conservador, sin falla cerrada nueva).
4. **Veredicto de consecuencias por identidad y clase de parte (`change-consequence-v1`):** la operación de lectura `validate-unit-contract` regenera la proyección **viva** y la compara con la **registrada** (la línea base = la proyección del **último paquete de la unidad**, publicación más reciente, empate → id mayor, el `active_packet` cuenta; sin paquete previo ⇒ `current`), **parte por parte** e **ignorando el origen**. Tres valores: **`current`** (ninguna parte difiere; cubre agregar una unidad futura independiente, modificar otra sin dependencias compartidas y editar la historia), **`impact`** (alguna parte `unit` o `shared` difiere: registra un **journal durable e idempotente** `.cdad/packets/<baseline_packet_id>/.impact.json` con `reason`/`contract_sha256_old`/`contract_sha256_new`/`changed_parts`; **decide el orquestador**, que registra la decisión en `stage_history.note`; **no** aprueba, **no** cambia `semantic_status`, **no** bloquea la recepción), **`impeded`** (rc=2, sin efectos, **sólo** cuando se **retiró la autorización** — sin entrada `epic_history` `epic-plan` con `approved_by` → `approval pending`, o `hitl_delegation` revocada/vencida → `state incoherent`; con la **salida** nombrada: registrar la aprobación `epic-plan` o restituir la delegación). **Ninguna sección del plan produce `impeded`.** El CLI **no** juzga el sentido de un texto (INV-8).
5. **Recepción y resume contra el contrato recibido:** con el `contract.path` apuntando a la proyección registrada, `render`/`validate-request`/`validate-packet`/`prepare --resume-packet`/`receive` validan los **bytes registrados**, no el plan vivo —**por la ubicación/pin**, sin cambiar la lógica de `receive`—. Recibir **no** aprueba (`semantic_status: pending`, `approval_effect: false`) y el **esquema del recibo no cambia**.
6. **`status` es de SOLO LECTURA y sólo informa:** el bloque **aditivo** `unit_contract` informa `mode`, la línea base, el digest vivo, el veredicto, las partes que difieren y el motivo, y **no escribe nada** (state byte-idéntico, sin proyección nueva, sin journal). El **journal de impacto lo escribe sólo `validate-unit-contract`** (y sólo en `impact`), **idempotente por par de digests**.

## Reasons

1. **El hash debe identificar el contrato que recibió el agente**, no la historia del plan: la proyección aísla lo que la unidad recibe; el sha del plan queda como procedencia. Es la dirección de la fila 13 (a) y del discovery §10.
2. **Persistir los bytes evita el hazard de byte-identidad** verificado en el discovery §3: re-generar en cada validación rompería `_resume_packet` (que compara contra el render canónico). Publicar junto al paquete lo hace **inmutable** (INV-3 de 005-001).
3. **La selección estructural + el fallback hacen la feature aditiva con churn de oráculos casi nulo:** los fixtures de plan de los tests existentes **no declaran tabla de unidades** (verificado), caen en el fallback y conservan su comportamiento. La sobre-inclusión de las partes `shared` es **conservadora y declarada**: una edición de una sección compartida da `impact`, nunca un bloqueo.
4. **Las anclas como declaración del producto** viven en **un solo lugar** (el activo que el producto manda cargar y completar), sin listas de títulos por proyecto ni fragilidad por plan.
5. **`impeded` sólo por autorización retirada** reusa causas y marcadores **ya existentes** (`approval pending`, `state incoherent`) y una salida que **ya existe** (registrar la aprobación `epic-plan`), sin depender de 005-012; así, editar legítimamente una sección del plan **nunca** deja la unidad bloqueada sin salida.
6. **El CLI no juzga prosa:** clasificar por identidad y clase de parte (no por listas de palabras ni por el sentido de un párrafo) es determinista y testeable; la inmediatez de una restricción queda en la review.
7. **`status` conserva su contrato de solo lectura** (005-003/005-011) y el journal idempotente hace el veredicto **reproducible sin efectos laterales**.

## Consequences

**Positivas (medidas):**

- **Tramo 1 (la planificación deja de bloquearse):** con el paquete despachado y tras **agregar una unidad futura independiente** al plan, `receive` → **rc=0** con `packet_validation`/`identity_validation` `passed` y `semantic_status: pending`; veredicto **`current`**. Es exactamente lo que hoy falla con el pin del plan completo (medido en el RED de T1: `receive` rc=2 «contract sha256 does not match exact content»).
- **Tramo 2 (el cambio relevante sí exige reconciliación):** editar el alcance o una dependencia de la unidad → **`impact`** con journal durable (los dos digests + las partes que difieren); editar la sección de autorización → **`impact`, nunca `impeded`**; retirar la autorización → **`impeded` rc=2** con el marcador y la **salida** nombrada; registrarla → `prepare` rc=0 y la proyección nueva como línea base.
- **Prueba decisiva (AC-9) cumplida en las tres formas de plan** con el **CLI real** sobre proyectos descartables; **AC-1..AC-9** verificados en las tres.
- **Suite de cierre:** **960 passed / 4 skipped, sin fallos** (worktree fijado a `7ab16ba`); `make validate` **155 PASS / 1 FAIL** (F011 preexistente).
- La planificación del proyecto deja de bloquearse globalmente por editar el plan del epic, sin habilitar atajos: no se omite ningún gate, recibir no aprueba y el pin de la spec de los roles de construcción queda intacto.

**Negativas / trade-offs:**

- **Dos formas de contrato vivas** (proyección y plan): `validate_request` acepta dos pares y la vista distingue `mode`; a cambio, la feature es aditiva. El **fallback** pierde el beneficio de la proyección pero **no** regresiona.
- **Sobre-inclusión de las partes `shared`:** una edición de una sección compartida irrelevante registra `impact` (conservador, declarado).
- **La fila 13 (b) queda acotada:** «cambiar una restricción de aplicación inmediata impide las acciones afectadas» se implementa como **`impact`** (decide el orquestador), no como `impeded`: el CLI no puede juzgar la inmediatez sin una marca estructural (deuda D-3).
- **El comportamiento nuevo no existe en la versión instalada** (O3): el generador lee el activo co-ubicado con el script; las raíces instaladas **no** declaran las anclas, así que con el CLI instalado el efecto es el **conservador** (ninguna ancla ⇒ todo `shared` ⇒ una edición da `impact`, nunca una falsa autorización). Hace falta **desplegar** (del dueño).
- **B1 fue un defecto real** del mecanismo (una proyección publicada podía reescribirse por una colisión de `--out-dir`), corregido con **escritura create-only** que falla cerrada; el GREEN lo había declarado **incorrectamente** como «no-op» y la review lo reprodujo.
- **O2..O5 abiertas:** copia inerte de la declaración de anclas en cada plan; lectura del activo instalado; límite de bytes de la vista con el bloque `unit_contract`; `mtime` como aproximación de la fecha de publicación (nominal).
- **Datos para 005-012:** la ejecución huérfana `exec-005-013-unit-contract-001` y los registros del state hechos con scripts del orquestador.

**Neutrales:**

- **Fuente única:** la spec **referencia** las reglas existentes (005-003 vista compacta, 005-007 planificación/unidad, 005-005 procedencia, 005-001 pin/reemplazo); toda extensión (el kind `approved-unit-contract`, el bloque `unit_contract`, la declaración de anclas del producto, el journal de impacto) es **aditiva y declarada**; sin documento nuevo y sin bloque `plan-tasks` a mano.
- **Frontera declarada:** la proyección **nombra** las dependencias de la unidad pero **no** incluye las filas de las unidades de las que depende (serían filas ajenas); la reconciliación de un paquete `dispatched` es territorio de **005-012** y **no** se anticipa.
- **Sin paralelismo:** `active_packet` sigue siendo único (fuera de alcance de la fila 13).

## Notas

- **Contrato normativo:** `docs/specs/005-013-unit-contract/spec.md` (`4369822e…`; §2.1–§2.8, PD-1..PD-13, INV-1..INV-10, AC-1..AC-10) y `plan.md` (`89d5d8cf…`; fichas T1..T4); contrato de la **fila 13** del plan del epic (`docs/epics/epic-005-real-operation/plan.md:46`) y «Ajuste de los ciclos pendientes» (`:48-88`).
- **Evidencia:** `discovery.md` (diagnóstico y recorrido), `review-claude-spec-2026-10-14.md` (B1/B2/P1 y segunda vuelta aprobada para TDD), `review.md` (1 bloqueante / 5 opcionales / 1 abstención + addendum del orquestador), `acceptance.md` (T4, tres formas de plan), `closure-suite.md` (960 passed / 4 skipped en `7ab16ba`; `make validate` 155/1), informes de TDD `t1-red/t1-green/t2-red/t2-green/t3` y del review-fix `b1-red/b1-green`. Commits de producto: `021a491` (T1 GREEN), `da3ced5` (T2 GREEN), `b3cb88c` (T3), `f41025f` (review-fix de B1); RED `9785423`, `c61db34`, `4bf688c`; gate T4 `7ab16ba`.
- **Relación con otros ADR:** **extiende** la autorización por rol de 005-001 (el architect se sigue habilitando con la aprobación `epic_history` `epic-plan` **sin** pin — el pin nuevo es de la **unidad**, no de la autorización) y **no** toca el pin `specification` de los roles de construcción (I2/PD-18). Es análogo a **ADR-025** (la orientación es una proyección read-only) y **ADR-027** (la entrada por la vista), en el sentido de «proyectar, no duplicar»: aquí el contrato de la unidad es una **proyección generada** del plan, no una segunda copia mantenida a mano.
- **Límites honestos:** el informe del reviewer trae **segmentos corruptos por el modelo** (el addendum del orquestador resume lo sustantivo; el veredicto y su evidencia son legibles). Las cifras del cierre son de una **corrida única** de la suite. La atribución «la diferencia vs 005-011 (927) son los focales nuevos» está en `closure-suite.md` y es consistente con la aritmética (960−927 = 33 = 18 + 15), pero no se re-midió por separado.
