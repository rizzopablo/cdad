# Desviación declarada — 007-005 (2026-10-26)

## Qué ocurrió

El tramo se despachó **dos veces**:

1. **Primer transporte.** La sesión hija se creó desde la raíz del repositorio CDAD. `record`
   rechazó la identidad: `termination=blocked`, `delivery=none`, `delivery_ref=null`, `session=null`,
   y **no registró el intento**. El producto no acreditó ninguna entrega. La sesión rechazada, sin
   embargo, ejecutó el trabajo read-only.
2. **Segundo transporte.** Sesión con raíz en el consumidor; `record` verificó
   `parent`/`moment`/`project` contra el almacén, emitió `delivery=staged` y la recepción produjo un
   recibo válido.

No hubo duplicación de efectos: el primer intento no escribió estado, paquetes ni continuidad, y las
dos sesiones fueron read-only. Sí hubo **dos ejecuciones del mismo encargo**.

## Por qué

La identidad nativa exige que la sesión despachada pertenezca a la raíz del proyecto autorizado
(INV-2). El orquestador opera desde la raíz de CDAD; despachar a otro proyecto requiere una sesión
raíz en ese proyecto. El rechazo es el comportamiento contratado, no un defecto.

## Decisión de la autoridad delegada

Se acepta la desviación del presupuesto «un paquete, una sesión, un despacho» con estas condiciones:

- Sólo la recepción aceptada acredita entrega; el informe del intento rechazado no se usa como
  evidencia de la recepción.
- El rechazo se declara **fallo observado**, y el recorrido no se presenta como ejecución feliz sin
  fallos.
- No se repite el recorrido para fabricar cumplimiento.
- La inmediatez temporal de `verify-begin` respecto del despacho aceptado se declara no capturada;
  la cabeza no cambió entre la verificación y el despacho (cadena seq 16 → 17, sin escrituras
  intermedias).
- Si el dueño revoca esta aceptación, la feature no puede cerrarse con este expediente.

**Firmado:** Orquestador CDAD (HITL delegada del dueño), 2026-10-26.
