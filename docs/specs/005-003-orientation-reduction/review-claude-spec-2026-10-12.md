# Revisión de la spec y el plan — 005-003 (orquestador Claude, entre tramos)

Fecha: 2026-10-12. Objeto: spec `0fcf78fe…`, plan `7eb9fe8f…` (commit `009902b`) y la línea base
`evidence/baseline-meter-2026-10-12.md`.

## Dictamen

**Conforme en lo sustancial.** El ancla en el primer despacho legítimo y no en el `resume` está
bien fundada. Son correctos la vista `status` como proyección sin migrar el state, la selección de
entrada que atiende un paquete pendiente, los ejemplos ejecutados localizados por asset, la
ausencia distinta de la incoherencia y el resumen del conjunto como documento aditivo. La línea
base reutiliza trabajo real y separa lo medido de lo derivado. Antes de abrir la etapa 3 hay que
resolver dos puntos.

## Puntos a resolver antes de la etapa 3

1. **D11 no tiene tarea que lo cierre.** El plan lo pone como condición del gate de T5 y hace lo
   mismo con R4, pero solo R4 tiene dueño (T3). Así, T5 termina en un bloqueo declarado. Propuesta:
   sumar a T3 el cierre de D11 con su condición causal (`docs/specs/005-002-session-context-meter/debt.md`).
   Es la misma clase de defecto: el consumo y la evidencia del medidor.
2. **Lo más caro de la línea base queda fuera del producto.** En la reapertura de 005-002 el
   desperdicio mayor fue:
   - el implementer corrió dos veces la suite completa en GREEN, unos 30 min en total;
   - los roles se re-orientaron sobre una spec de unos 50 KB;
   - el orquestador pasó unos 38 min entre despachos.

   La spec trata las tres prácticas como hipótesis aplicadas por el encargo y deja la preparación
   de encargos a 005-007 (INV-4). Pero A10 («0 corridas de suite fuera del cierre») es un criterio
   de 005-003, y sin un cambio de producto depende de lo que el orquestador escriba en cada
   paquete. Decisión del dueño: (a) sumar una unidad mínima a 005-003, en la que el paquete GREEN
   renderice los comandos de validación del bloque `plan-tasks` y la instrucción de la subetapa diga
   que la suite completa no se corre salvo que el paquete lo pida; o (b) dejarlo explícitamente
   para 005-007 y medir A10 como observación. Recomendación: (a). Es chica, apunta al costo medido
   más grande y no invade el tamaño de unidad de 005-007.

## Observaciones menores

- T4 (inventario de capacidades y OpenChamber) se mantiene chico y solo documental, como dice el
  plan.
- La enmienda de la fila 8 propuesta en `discovery.md` §3 es coherente con el delta aprobado.
  Recomiendo aprobarla, incluyendo el punto 1. La aprobación es del dueño.

## Verificación del cierre (orquestador Claude, 2026-10-12 23:55)

- `validate-state` da `VALID: idle`. Focales de 005-003 y 005-002: 81 passed / 2 skipped.
- D11 cerrado de verdad: la integración real del medidor pasó 5 de 5 corridas seguidas con la base
  activa (antes fallaba 7 de 8).
- `status` sobre este repo: 1.448 B, `rc=0`, sin `stage_history`, versión `UNKNOWN` con causa.
- Grep de privacidad del diff: limpio (la única coincidencia es una lista genérica de proveedores
  para el filtro).

### F2 compromete el uso previsto: corresponde reabrir

La review lo dejó como opcional con «frecuencia no verificada». En este repo ocurre siempre. Con
el state en reposo (`active_feature: null`, `current_stage: idle`, `active_packet: null`), la vista
emite `entry: continuity-reconcile` y «resume the active execution», que apunta a la ejecución de
una feature cerrada, en vez de `next-unit`. Cualquier proyecto real con historia tiene directorios
de paquete en `.cdad/packets/`, así que el recorrido principal de esta feature (reposo → primer
despacho legítimo, A1) siempre recibe una ruta equivocada. El orquestador tiene que descubrir
solo que no hay nada que retomar: la reorientación que la feature quería evitar. Con el criterio
vigente es material, no opcional.

Corrección propuesta. Es un cambio de contrato en §2.2 y la decide el dueño: en reposo sin feature
activa, los directorios de paquete son historia, no trabajo pendiente. Un directorio cuenta como
pendiente solo si pertenece a la ejecución vigente de una feature activa y no tiene recibo en
`.cdad/runtime/results/`. Se prueba con un fixture de reposo que tenga paquetes históricos y con
este repo.
