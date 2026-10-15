# Revisión del orquestador Claude — spec y plan de 005-011 (2026-10-13)

Criterio vigente del 2026-10-12.

**Bien:**
- D1–D4 atacan las cuatro causas medidas sin crear referencias nuevas ni una segunda copia de reglas.
- La autorización explícita de los dos oráculos de 005-003 que cambian es correcta y está declarada.
- T2 no usa oráculos de texto por listas de palabras: el sentido lo juzga la review.
- El bloque `plan-tasks` es válido (lo comprobé con las funciones del CLI).

**Corregido (bloqueante para el uso previsto):**
1. **AC-7 declaraba desconocido el lado Claude Code**, y lo medía solo «si el dueño corre una sesión».
   - Las skills que cambia T2 son comunes a los dos runtimes, así que el lado CC es parte del resultado.
   - El orquestador Claude puede lanzar la sesión nueva y contar su transcript, como en 005-004 T5.
   - Ahora AC-7 es obligatorio, con conteo propio declarado como otro instrumento.
2. **La aceptación de uso podía quedar en BLOQUEO por despliegue y la feature cerrarse igual.**
   - El resultado de 005-011 es el comportamiento de entrada en sesiones reales, así que cerrar sin
     medirlo compromete la evidencia.
   - Ahora: con T1–T3 en verde se pide el despliegue al dueño, y AC-6 y AC-7 corren antes del cierre.

**Corregido (ejecutabilidad):**
3. **T2 (las dos `SKILL.md`) tenía como responsable al test-writer,** que no edita fuera de `tests/`.
   Pasa al implementer, con la verificación del orquestador y la review por sentido.

Las enmiendas se aplicaron en un bloque al inicio de la spec que prevalece sobre el resto del texto,
y en AC-7, AC-8, D-1 y las fichas T2 y T4 del plan. Spec y plan se vuelven a aprobar con sus nuevos
sha256.
