# Review del orquestador Claude — spec y plan de 005-013 (2026-10-14)

Objeto: `spec.md` y `plan.md` aprobados por el orquestador OpenCode en `89165d7`. Criterio: se bloquea lo
que compromete el resultado, la evidencia o el uso previsto; el resto va a deuda.

La dirección es correcta y el discovery es sólido: el pin que bloquea es el del paquete del architect, la
proyección se publica una vez junto al paquete y se pinea por digest, la recepción valida los bytes que el
agente recibió y la clasificación es por identidad y clase de parte, sin juzgar prosa. Hay dos bloqueos y
una precisión.

## B1 (bloqueante, uso previsto) — la selección depende de los títulos de este plan

La spec ancla la proyección en «Entregas», «Cambios al plan» y «Autoridad», y localiza la unidad por
igualdad exacta de la celda `Feature`. Si no los encuentra, **falla cerrado** (PD-1). Esos títulos son los
del plan de epic-005. Los demás planes son distintos:

- **la plantilla del producto** (`skills/cdad-epic/assets/epic-plan-template.md`) usa «Decomposition into
  features», con la columna «Feature ID», y «Plan changes»;
- **los planes de otro proyecto real** que usa CDAD (siete epics) usan «Features y orden recomendado». La
  celda de la unidad es un enlace (`[F007-001 — …](../../specs/F007-001/spec.md)`) y no tienen sección de
  historia ni de autoridad.

Con la regla aprobada, después del próximo despliegue **todo `prepare` del architect fallaría** en ese
proyecto y en cualquiera creado desde la plantilla. Es una regresión que bloquea el uso previsto.

**Enmienda requerida (el mecanismo lo decide el architect):**

1. **La unidad se localiza estructuralmente en cualquier plan:** por ejemplo, la única fila de una tabla
   del plan que contiene el id de la feature como token completo, con el encabezado de esa tabla. No por
   el título de la sección ni por igualdad exacta de la celda.
2. **Si la unidad no se puede localizar sin ambigüedad (ninguna fila o más de una), no falla cerrado:**
   vuelve al contrato actual (`approved-epic-plan`, plan completo) y lo informa en el diagnóstico y en
   `status`. Se pierde el beneficio, pero no hay regresión.
3. **Las anclas de historia y de autoridad no son listas por proyecto.** Se reconocen por una declaración
   del propio producto, como el título de la plantilla o una marca estructural declarada en ella. Si un
   plan no las tiene, el contenido cuenta como `shared`, que es conservador: genera `impact` y no
   bloquea. No hay clase `authority`, y lo único que produce `impeded` es retirar la autorización.
4. **La aceptación cubre tres formas de plan:** el de epic-005, uno generado desde la plantilla y un
   fixture anonimizado con la forma de los planes del otro proyecto (celda con enlace, sin historia). En
   las tres, agregar una unidad independiente da `current` y `receive` rc=0, o el fallback declarado del
   punto 2.

## B2 (bloqueante, uso previsto) — `impeded` no tiene línea base ni salida

PD-7 impide «preparar un paquete nuevo» cuando cambió la parte `authority`, «hasta que el orquestador
reconcilie». Pero la reconciliación quedó fuera de alcance (V7, 005-012), y para un `prepare` nuevo no se
define contra qué proyección registrada se compara. Tal como está, editar legítimamente la sección de
autoridad deja la unidad bloqueada **sin salida dentro del producto**.

**Enmienda requerida:** declarar la línea base del veredicto (por ejemplo, la proyección registrada del
último paquete de la unidad) y una **salida con los mecanismos existentes**, sin depender de 005-012. Por
ejemplo: una nueva aprobación `epic-plan` en `epic_history` registrada después del cambio (HITL) levanta
el impedimento, y el siguiente paquete toma la proyección nueva como línea base. Un focal lo cubre:
autoridad editada → `impeded`; aprobación registrada → `prepare` rc=0.

## P1 (precisión, va en la misma enmienda) — `status` sigue siendo de solo lectura

D-8 agrega el veredicto a `status`, e INV-9 dice que, ante `impact`, la operación escribe un registro.
Hay que fijar que **`status` informa el veredicto y no escribe nada** (contrato de solo lectura de
005-003). El registro de impacto lo escribe solo `validate-unit-contract`, y es **idempotente**: si el
par de digests es el mismo, no se duplica el registro.

## Deuda / datos (no bloquean)

- **Ejecución huérfana `exec-005-013-unit-contract-001`** (desviación declarada): no está versionada ni
  referenciada, así que se deja. Es un dato para 005-012: después de `open-unit`, `prepare
  --new-execution` debería rechazarse con un diagnóstico, no crear un segundo contexto.
- **Registros del state hechos con scripts sueltos en un directorio temporal** (discovery y aprobación):
  el state queda bien y valida, pero el script que lo editó no queda como evidencia. Es otro caso del
  registro manual de transiciones que resuelve 005-012.
- **Entrada al proceso medida en esta sesión nueva de OpenCode (una sola observación, con 7212ead):**
  - **Orden de entrada:** la skill fue la llamada 1 y `status` la 2. El state completo **no se leyó
    entero**, solo con lecturas puntuales a partir de la llamada 15. Es la primera vez que se observa el
    orden de AC-6 de 005-011 en OpenCode.
  - **Primer despacho:** fue la llamada 73, con unos 314 mil caracteres de salida previa. No se compara
    con la línea base, porque esta corrida incluía abrir la unidad y una exploración del código del pin
    que el encargo hacía pertinente.

## Disposición

No se arranca TDD. El orquestador OpenCode despacha al architect una corrección del draft con esta review
como insumo, la verifica y vuelve a aprobar la spec y el plan. Después se detiene y reporta.

## Segunda vuelta (draft 002, `a67990f`) — APROBADA para TDD

- **B1:** está cubierto. La unidad se localiza como la única fila de una tabla que contiene el id como
  token completo. Si no se localiza sin ambigüedad, se usa el contrato del plan completo, declarado en
  `status`. Las anclas de historia y autorización las declara la plantilla del producto. Sin anclas, todo
  cuenta como `shared`. La aceptación se prueba con tres formas de plan.
- **B2:** está cubierto. La línea base es la proyección del último paquete de la unidad. `impeded` solo
  aparece cuando se retira la autorización, y una nueva aprobación `epic-plan` lo levanta, sin depender de
  005-012.
- **Tensión entre B2 y B1.3:** la acepto como la resolvió el rol. Editar la sección de autoridad da
  `impact` y no `impeded`. Esto acota la fila 13 (b): el CLI no puede saber si una restricción es de
  aplicación inmediata sin una marca estructural, así que el cambio de una restricción lo juzga el
  orquestador al ver el `impact`. Queda declarado como deuda D-3. No bloquea, porque nada se aprueba
  solo y el orquestador ve el impacto en `status`.
- **P1:** está cubierto. `status` no escribe, y el registro de impacto es idempotente por el par de
  digests.
- **El run del orquestador terminó con rc=1** por un corte del stream del proveedor, después de commitear
  y reportar. El árbol quedó limpio y `validate-state` da VALID.
