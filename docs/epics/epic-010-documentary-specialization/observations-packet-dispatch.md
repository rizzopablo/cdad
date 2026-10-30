# Observaciones para 010-004 — despacho de paquetes

Evidencia recogida por el orquestador durante `010-000` (2026-10-29). No es
Discovery ni un contrato: son incidentes verificables para que la unidad
`010-004-packet-dispatch-ergonomics` los convierta en postcondiciones.

## I-1 — Transporte manual y divergencia de bytes

El paquete se copia a mano en el prompt del subagente. En el primer review de
spec, dos pares de backticks se perdieron en la copia; el reviewer rechazó
correctamente el paquete. La ruta A exige comparación byte a byte; no existe un
paso mecánico de transporte ni una ruta C emitida por el renderer.

Consecuencia: cualquier transcripción —humana o de modelo— puede invalidar el
encargo sin que el trabajo haya empezado.

## I-2 — El cierre del bloque JSON se lee como fin del paquete

El render canónico abre `---cdad-packet-json`, lo cierra con
`---end-cdad-packet-json` y continúa con el cuerpo. Un test-writer interpretó
ese cierre como "paquete parcial" y se detuvo sin ejecutar la comparación
canónica.

Consecuencia: el formato no explicita que el bloque es una cabecera y que la
comparación cubre desde el marcador hasta el final.

## I-3 — El contexto de ejecución se infiere

La cabecera declara `execution_id`, pero no la ruta del contexto v2. Dos
subagentes usaron `docs/.cdad-state.json` y `.cdad/execution.json` como contexto
y fallaron con "execution context fields do not match schema". La ruta correcta
es `.cdad/executions/<execution_id>/execution.json`.

Consecuencia: el rol debe deducir una ruta que la cabecera puede declarar.

## Criterio de cierre sugerido para 010-004

- La cabecera del paquete declara el contexto de ejecución utilizable sin
  inferencia.
- Existe una forma de despacho que no dependa de retranscribir bytes.
- El intake distingue explícitamente cabecera y cuerpo.
- Regresión de los tres incidentes: paquete divergente rechazado con diagnóstico
  accionable; cabecera+y cuerpo aceptados; contexto declarado aceptado y
  contexto ajeno rechazado nombrando el esperado.

No fijar mecanismo (ruta C, archivo, otro) antes del Discovery de la unidad.

## I-4 — Verificación de entrega no observable y bloqueo desproporcionado

En el resultado de `scribe-memory-002`, el rol informó `cmp` entre render y
PACKET.md, pero describió el cotejo del prompt recibido como «campo por campo».
Eso no acredita igualdad byte a byte de la entrega; tampoco demuestra corrupción
del paquete ni invalida por sí solo el borrador. El orquestador lo convirtió en
bloqueo automático y luego rectificó ese criterio a petición del usuario.

Problema a investigar: el transporte nativo puede no exponer los bytes recibidos
como artefacto verificable. Exigir al modelo que los reconstruya y certifique
puede producir una declaración no comprobable, en lugar de garantía mecánica.
No se afirma todavía que todos los runtimes tengan esta limitación.

Separar en Discovery tres evidencias: integridad del paquete publicado, integridad
de la entrega y fidelidad del resultado al encargo. Un `cmp` de render contra
PACKET.md prueba solo la primera; una comparación semántica no prueba la segunda.
Investigar cómo acreditar la entrega sin retranscripción ni autoatestación del
modelo y cómo diagnosticar honestamente lo no observable.

Disposición acordada con el usuario: registrar la limitación y contrastar el
borrador con las fuentes, sin repetir automáticamente todo el trabajo ni tratar
una declaración insuficiente como prueba de corrupción. Esto no elimina las
reglas vigentes ni autoriza ignorar divergencias reales, autoridad inválida o
contenido infiel. La mejora del protocolo corresponde a 010-004; este registro
no modifica por sí solo su contrato ni aprueba el cierre de 010-000.
