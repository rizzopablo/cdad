# Revisión técnica y cumplimiento del objetivo: son dos actos distintos

Fecha: 2026-10-24. Origen: observación del orquestador del otro proyecto activo — «el revisor no dijo que el objetivo esté cumplido; dijo que el cambio que revisó no tiene errores bloqueantes».

## La distinción es correcta

La revisión de etapa 4 responde una pregunta acotada: **¿este diff cumple el contrato aprobado de esta unidad, sin defectos bloqueantes?** Su universo es el diff y la spec. No ve el entorno, no ejecuta el recorrido completo, no habla con el consumidor y no decide si el ciclo logró lo que se propuso.

La aceptación responde otra pregunta: **¿el objetivo del ciclo está cumplido, con qué evidencia y qué queda sin acreditar?** Su universo es el sistema en uso: criterios del epic, integración entre features, recepción real.

Confundirlas produce el error simétrico en dos direcciones:

- **Un diff conforme a una spec incompleta** se lee como objetivo logrado. La spec puede cumplirse al pie de la letra y no alcanzar el resultado: es el caso S-SYS-01 (decisiones implementadas sin la acción operativa necesaria).
- **Un objetivo logrado con defectos locales** se lee como fracaso. La revisión marca el defecto, y eso no dice nada sobre si el resultado se alcanzó.

También difieren en autoridad: la revisión la ejerce un rol read-only con independencia de familia; la aceptación la ejerce quien tiene el mandato (dueño u orquestador delegado), y no puede delegarse al revisor sin vaciar el gate.

## Lo que CDAD ya tiene

- Criterios de aceptación en la spec y en el plan del epic.
- `closure.md` por feature y `integration.md` por epic.
- Un gate de cierre y un Memory Bank que declara límites.
- Roles separados con autoridad explícita.

## La brecha concreta

**El vocabulario se solapa.** El revisor emite `APTO` / `NO APTO`, y ese mismo `APTO` se lee después como «está hecho». No existe un artefacto que responda, criterio por criterio, *acreditado / no acreditado / pendiente* con su evidencia. Cuando el cierre se escribe en prosa, la distinción se pierde.

Evidencia del propio repo: en 007-001 y 007-002 cerré con «review APTO + N passed» y una lista de deuda. Eso **no** es una tabla de aceptación: es una revisión más un recuento de tests.

## Propuesta (candidata al epic siguiente, no ejecutada)

1. **Vocabulario separado.** El revisor dictamina `conforme al contrato` / `no conforme` (o conserva `APTO` pero con el alcance declarado en el artefacto: «sobre este diff contra esta spec»). La aceptación usa `acreditado` / `no acreditado` / `pendiente`.
2. **Tabla de aceptación obligatoria en el cierre.** Una fila por criterio: `criterio → evidencia (ruta/hash/comando) → estado → quién acepta`. El estado **no se deriva** de la revisión; se declara con evidencia.
3. **Prohibición explícita.** Un cierre no puede presentar `APTO` del revisor como acreditación del objetivo. Si un criterio queda `pendiente`, el cierre lo dice y el epic no se declara cumplido.
4. **Aceptación del epic con evidencia de uso.** Los criterios del epic exigen integración y recepción reales; la revisión de cada feature no los sustituye.

## Coste

Bajo: es una tabla y una regla de vocabulario, no un mecanismo nuevo. No agrega gates ni roles.

## Dónde encaja

Es pariente de la línea A (planificación y evidencia) y del hallazgo S-SYS-01: la distinción entre decisión, ejecución, integración y uso. Se registra como candidato; no cambia ningún contrato vigente.
