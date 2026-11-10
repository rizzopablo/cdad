# Decisiones del dueño sobre el Discovery — 2026-11-07

Registro de las cuatro decisiones que el Discovery de `017-001-suite-performance`
dejó abiertas (`discovery.md` §6). El dueño las aprobó con «ok» a la propuesta
del orquestador, el 2026-11-07.

| # | Pregunta | Decisión |
|---|---|---|
| 1 | ¿Autorizás la línea base completa instrumentada, tras calibración focal? | **Sí.** Corrida base y corrida final instrumentadas, sobre revisión y selección fijadas. |
| 2 | ¿Qué reducción consideramos éxito? | **Se fija después de la línea base**, con datos medidos; no se inventa un porcentaje ahora. |
| 3 | ¿Optimización serial primero y paralelismo condicionado? | **Sí.** Primero preparación en serie; paralelismo solo si el costo residual lo justifica y la seguridad se demuestra. |
| 4 | ¿Conciliación del total con residual explícito? | **Sí.** Partes + residual explícito; no se fuerza la igualdad entre XML y tiempo de pared. |

## Límites de esta autorización

- Autoriza las dos corridas completas instrumentadas (base y final) y las focales
  necesarias, conforme a la política de evidencia vigente.
- No autoriza poda de tests, cambios en contratos cerrados ni publicación o
  despliegue.
- No fija el objetivo de reducción: eso se decide con la línea base a la vista.
