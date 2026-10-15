# Deuda de 005-013-unit-contract

Deuda consolidada al cierre de la feature, con **condición de cierre** por ítem. Criterio vigente
(2026-10-12, `docs/epics/epic-005-real-operation/execution.md`): se bloquea y se corrige ya lo que
compromete el resultado, la evidencia o el uso previsto; va a deuda lo que es una mejora o variante sin
impacto material. **Nada de esta lista bloquea el cierre de la feature**; cada ítem dice qué lo cierra.

## De la review formal de la etapa 4 (`review.md`)

- **O2 (nit) — copia inerte de la declaración de anclas.** Cualquier plan generado desde la plantilla del
  producto lleva una copia **inerte** del comentario `cdad:plan-anchors`. El generador lee la declaración del
  **activo del producto** (co-ubicado con el script), **nunca** del plan, así que la copia no tiene efecto y
  **no** es una segunda copia de la regla (la fuente de verdad sigue siendo una). Lo que no está declarado es
  que los planes nuevos heredan la copia. *Cierre:* una frase en el propio comentario del template («copia
  inerte; el activo es la autoridad») o un caso de PD-3 que lo declare.
- **O3 (opcional, `m`) — lectura del activo INSTALADO.** El generador resuelve la declaración de anclas desde
  el activo co-ubicado con el script: el CLI del repo lee el activo del repo (que declara las anclas) y el CLI
  **instalado** lee el activo instalado. **Medido por la review:** las tres raíces instaladas tienen la
  plantilla byte-idéntica a base y **sin** la declaración (`grep "cdad:plan-anchors"` → 0), así que con el CLI
  instalado el efecto es el **conservador** que PD-3 declara (ninguna ancla ⇒ todas las secciones `shared` ⇒
  una edición da `impact`, **nunca** una falsa autorización). El drift silencioso requiere un redespliegue
  **parcial** (script nuevo + activo viejo). *Cierre (opcional, post-despliegue):* comprobar con un `grep` que
  el activo instalado declara las anclas, o agregar un `schema_version` dentro de la declaración para
  detectar el activo viejo.
- **O4 (nit) — límite de bytes de la vista.** El bloque aditivo `unit_contract` de `status` podría acercar la
  vista a su límite (`DEFAULT_VIEW_MAX_BYTES`, 16.384 B) si el plan es grande y **todos** los títulos cambian
  (`changed_parts` arrastra todos). La vista **falla cerrada** ante el límite (invariante de 005-003), sin
  truncamiento adaptativo dentro del bloque. *Cierre:* respetar `--max-bytes` truncando `changed_parts` y
  `reason` con un contador (`+N more`).
- **O5 (nit) — `mtime` como fecha de publicación.** La línea base usa `st_mtime` + desempate por id de
  paquete. La review lo juzgó **equivalente** a lo que declara PD-7/D-11 (**nominal**, sin impacto).
  *Cierre:* ninguno necesario; se cierra por declaración si el plan deja de publicar los paquetes en orden.

## De la spec §8 (deuda declarada por el contrato)

- **D-1 — oráculos vigilados.** El churn de oráculos se redujo por el fallback: los fixtures de plan de los
  tests existentes **no declaran tabla de unidades** (verificado) y caen en el fallback conservando su
  comportamiento. **Estado al cierre: cumplida** (focales de T1/T2 verdes y las regresiones declaradas
  corridas, sin debilitamiento silencioso). La **lista de vigilancia** queda declarada en la spec para
  cualquier cambio futuro del contrato del architect. *Cierre:* se mantiene como vigilancia; no requiere acción.
- **D-2 — reconciliación de un paquete `dispatched`.** Fuera de alcance (territorio de **005-012**): el
  veredicto `impact`/`impeded` la **nombra**, no la implementa. La **salida** del `impeded` (registrar la
  aprobación `epic-plan`) **sí** quedó dentro de esta feature. *Cierre:* la unidad **005-012**.
- **D-3 — juicio de «restricción de aplicación inmediata».** El CLI no juzga la inmediatez de una restricción
  (no parsea prosa) ni la clasifica por listas de títulos; la parte de autorización se reconoce por la
  **declaración del producto** y se etiqueta. *Cierre:* una **marca estructural declarada** en los planes (no
  se inventa acá; exigiría tocar los planes existentes).

## Acotamiento de la fila 13 (b) — declarado

La fila 13 pide que «cambiar una restricción de aplicación inmediata **impida** las acciones afectadas». La
implementación lo **acota**: cambiar una restricción del plan da **`impact`** (registro durable + decide el
**orquestador**), no `impeded`; lo único que produce `impeded` es **retirar la autorización**. Fundamento: el
CLI no puede juzgar la inmediatez de una restricción sin una marca estructural, y no se inventa una (D-3). Lo
aceptó la review del orquestador Claude en la segunda vuelta de la spec. Nada se aprueba solo y el orquestador
ve el impacto en `status`. *Cierre:* D-3 (marca estructural) si se quiere hacer mecánica la inmediatez.

## Datos para 005-012 (registro de transiciones)

- **Ejecución huérfana.** `open-unit` crea el contexto de ejecución de la unidad; `prepare --new-execution`
  inmediatamente después creó un **segundo** contexto (`exec-005-013-unit-contract-001` quedó sin referencias:
  no está versionado, no lo referencia ningún paquete ni recibo; el activo es `…-002`). Se dejó intacto (no se
  toca estado gestionado por el CLI). *Cierre (005-012):* tras `open-unit`, `prepare --new-execution` debería
  **rechazarse** con un diagnóstico que nombre el contexto ya abierto, en vez de crear un segundo.
- **Registros del state con scripts del orquestador.** Las transiciones de este ciclo (apertura/discovery,
  aprobación, RED/GREEN, review, T4, Memory Bank) se registraron con **scripts del orquestador** en
  `.cdad/local/`. El state queda bien y valida, pero el script que lo editó **no queda como evidencia
  durable**. Es otro caso del **registro manual de transiciones** que resuelve 005-012. *Cierre:* 005-012
  (la operación del CLI que registra la transición y conserva el juicio del orquestador).

## Despliegue pendiente (del dueño) — necesario para el uso previsto

El comportamiento de esta feature **no existe en la versión instalada**: el discovery verificó que el CLI del
repo era byte-idéntico al instalado en `7212ead`, y esa es la **procedencia citada, no la versión bajo
prueba**. Hasta que el dueño despliegue: (a) el generador del CLI instalado lee un activo **sin** la
declaración de anclas (⇒ comportamiento conservador, O3); (b) el pin de unidad no existe en producción.
*Cierre:* el despliegue (reservado al dueño) y, después, la comprobación de O3 en el activo instalado.
