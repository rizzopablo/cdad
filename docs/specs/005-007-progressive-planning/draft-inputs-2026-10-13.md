# Delta de entrada al draft — 005-007

Fecha: 2026-10-13. Aprobado por el dueño («si»), a partir de la aceptación real de 005-003
(`docs/specs/005-003-orientation-reduction/acceptance.md` §9). Complementa `discovery-inputs.md` y
el `discovery.md` ya recibido. No lo reemplaza ni pide repetir el discovery.

## Por qué entra en 005-007

La sesión de aceptación de 005-003 llegó sola al primer despacho, pero hizo 74 llamadas y leyó
399 mil caracteres antes. La causa medida no fue la orientación sino la preparación de la unidad.
Para abrir 005-007, el orquestador leyó y editó el state a mano: 15 comandos sobre ese archivo, el
mayor de 55 KB. Preparar encargos con contexto suficiente y sin costo de integración innecesario es
el problema de esta feature.

## Qué llevar al draft

1. **Abrir la siguiente unidad sin editar el state a mano.** Una operación del CLI, reutilizando
   `prepare` o con un subcomando, que abra la feature o la unidad siguiente del plan aprobado y deje
   el state coherente. Debe hacerlo sin que el orquestador lea ni reescriba el state entero, y
   conservar las validaciones, la autoridad y el escritor único. La entrada `next-unit` de `status`
   apunta a ella.
2. **Materializar el informe de discovery del architect.** Hoy `cdad_result.py` solo admite
   `architect-spec-draft` y `plan-draft`, así que el informe de discovery se copia a mano (en la
   aceptación, con `cp` y sha idéntico). Debe pasar por el camino legítimo de recepción y
   materialización.
3. **Reconocer como despacho la interfaz común de delegación.** El medidor reconoce solo
   `subagent` y `task`. Una invocación de `cdad_delegate.py` (shell) también es un despacho de
   trabajo de rol y debe detectarse, sin inferirlo del texto de un comando que solo lo mencione
   (PD-6 de 005-002). Sin esto, la aceptación de 005-007 no se puede medir con el medidor.

## Aceptación

Se repite la medición de `acceptance.md` §9 con una sesión real nueva en reposo y la versión
desplegada después de esta feature. La meta es orientación, no un umbral automático: reducir las
llamadas y la salida previas al primer despacho, en especial los comandos sobre el state. Además,
el medidor tiene que detectar el despacho por sí solo.
