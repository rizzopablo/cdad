# Review del orquestador Claude — spec y plan de 005-012 (2026-10-14)

Objeto: `spec.md` y `plan.md` aprobados por el orquestador OpenCode en `df597a7`. Criterio: se bloquea lo
que compromete el resultado, la evidencia o el uso previsto; el resto va a deuda.

La dirección es correcta. Es un subcomando aparte de `prepare`, con escritor único y vocabulario cerrado
para la decisión y etiqueta libre para la historia. Recibir no aprueba, la repetición se resuelve con una
clave por contenido, la vigencia de una aprobación se marca de forma estructural (`supersedes`) y el
cierre comprueba antes de aplicar. Hay un bloqueo y dos precisiones obligatorias.

## B1 (bloqueante, uso previsto) — el cierre no tiene salida para un despacho que nunca vuelve

PD-8(a) exige un recibo durable para **todo** paquete con registro de despacho en la ejecución activa. La
única salida que se ofrece es `receive --late` más `late-delivery`, pero PD-13 la limita a features
**cerradas**. D-9 declara como límite un despacho que el orquestador considera anulado.

Ese caso no es raro. En este mismo ciclo un run del orquestador terminó con «stream ended without
finish_reason» del proveedor. Si eso le pasa a un rol despachado, no hay entrega que recibir: el
orquestador vuelve a despachar en un paquete nuevo y el primero queda `dispatched` para siempre. Con la
regla aprobada, **la feature no se puede cerrar con la operación nueva** y se vuelve a editar el state a
mano, que es lo que la unidad viene a eliminar.

El registro del repo lo confirma como patrón: en ejecuciones anteriores hay muchos despachos sin recibo en
la ruta durable, por ejemplo los reintentos de GREEN y RED. En las de 005-010 y 005-013 no hay, y en la de
005-011 solo el del scribe.

**Enmienda requerida:** una **disposición explícita del orquestador** sobre un despacho sin recibo, con la
feature abierta. Por ejemplo, `--transition delivery` con una disposición `abandoned` o `superseded`, o
una clase propia, con referencia al paquete que lo reemplaza cuando existe. Tiene que cumplir cuatro
cosas:

- registra la decisión como dato estructural, sin aprobar nada y sin fabricar un `completed`;
- satisface PD-8(a) para ese paquete;
- es idempotente por `transition_key`;
- deja la traza en `stage_history`.

No es un control nuevo: es la decisión del orquestador que la fila 12 (d) manda conservar, con la
contabilidad a cargo del CLI. AC-4 suma el caso: despacho sin recibo → el cierre rechaza nombrándolo → la
disposición se registra → el cierre avanza.

## P1 (precisión obligatoria, resultado) — los digests los calcula el CLI

Hoy la superficie pide que el orquestador pase `--receipt <sha256>`, `--artifact <path>=<sha256>`,
`--contract-sha256` y `--plan-sha256`, que el CLI después verifica contra los mismos archivos. Calcular un
hash para que el CLI lo recalcule es trabajo y superficie de error sin protección adicional, y la fila 12
pide reducir trabajo operativo.

**Enmienda requerida:** que los digests sean **opcionales**. Si faltan, el CLI los calcula sobre los
bytes actuales, los escribe en la entrada y los imprime en la salida. Si se pasan, se verifican, y una
diferencia falla cerrado (`evidence missing`). Pasarlos sirve para un caso: aprobar exactamente los bytes
que se revisaron cuando el archivo pudo cambiar entre medio. Se declara así. AC-1 se corre en la forma
mínima, sin pasar ningún digest.

## P2 (precisión obligatoria, uso previsto) — aprobación del dueño sin delegación

PD-6 exige una `hitl_delegation` vigente siempre que haya un epic activo. Pero el dueño es la autoridad
original: un proyecto con epic y sin delegación, donde aprueba el dueño, no podría registrar sus gates
con la operación nueva y volvería a la edición manual.

**Enmienda requerida:**

- **Con una delegación registrada:** se verifica su vigencia, como dice PD-6.
- **Sin delegación:** se registra el aprobador declarado (`--approve-by`) y la salida dice que no hubo
  delegación que verificar, como ya hace PD-6 con `active_epic: null`. El CLI no puede verificar
  identidades (D-6), así que no puede bloquear al dueño.
- **Con una delegación revocada o vencida:** sigue fallando cerrado.

## Deuda / datos (no bloquean)

- **Datos medidos de PD-17:** el orquestador ya corrigió el porcentaje (90,8 %). Los tests no deben
  asertar porcentajes ni conteos del state vivo del repo: el state cambia con cada ciclo. Para PD-17
  alcanza con `validate-state` rc=0 antes y después.
- **Despachos sin recibo de ejecuciones cerradas:** no los toca esta unidad. El cierre mira solo la
  ejecución activa.
- **Tamaño:** son 8 tareas y una superficie grande. Va bien así siempre que T1 deje usable la forma
  mínima (`delivery` y `advance`) y las otras clases se agreguen sobre esa base.

## Disposición

No se arranca TDD. El orquestador OpenCode despacha al architect una corrección del draft con esta review
como insumo, la verifica y vuelve a aprobar la spec y el plan. La operación nueva todavía no existe, así que la
reaprobación se registra como hoy: una entrada nueva cuya nota declara que reemplaza a la anterior.
Después se detiene y reporta.

## Segunda vuelta (draft 002, `a18377e`) — APROBADA para TDD

- **B1:** está cubierto. Hay una clase propia, `disposition`, con `abandoned` o `superseded` y la feature
  abierta. Satisface PD-8(a), no fabrica un `completed`, es idempotente y rechaza si ya existe un recibo
  durable. El rechazo del cierre ahora ofrece recibir o disponer. AC-4 suma el caso.
- **P1:** está cubierto. PD-20 hace los digests opcionales: el CLI los deriva, los escribe y los imprime,
  y verifica los que se le pasan. AC-1 se corre en la forma mínima.
- **P2:** está cubierto en la operación. El límite que queda (D-10) es que `validate-state` ya exigía
  `hitl_delegation` con un epic activo. Es una regla de 005-001 que precede a esta unidad. Declarado y
  aceptado.
- **Reaprobación:** se registró con nota en prosa, porque `supersedes` todavía no existe. La aprobación
  anterior ya no habilita, porque su pin no coincide con los bytes actuales. Es correcto.
