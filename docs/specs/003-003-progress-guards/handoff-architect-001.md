# Encargo al architect — 003-003-progress-guards (discovery + spec/plan draft)

Rol: `cdad-architect`, solo lectura. Entregas: borradores de `spec.md` y `plan.md`
en tu respuesta (el orquestador materializa). Objetivo de tiempo: ~30 min. Sin
`opencode run` anidados ni sondas que provoquen incidentes reales.

## Objetivo
Detectar y resolver interrupciones y repeticiones improductivas en desarrollos
reales, preservando autonomía y utilidad. No reconstruir restricciones rígidas ni
crear un supervisor que consuma más que el trabajo que evita.

## Entradas (leer)
- `docs/epics/epic-003-context-efficiency/remaining-features-handoff.md` (contratos y discovery obligatorio de 003-003)
- `docs/epics/epic-003-context-efficiency/plan.md`, `execution.md`
- `docs/epics/epic-003-context-efficiency/friction-intake-004-001.md`
- `docs/epics/epic-003-context-efficiency/evidence-utility-2026-10-05.md`
- `docs/specs/003-002-artifact-tools/closure.md` (evidencia reutilizable; 003-002 cerrada, no reabrir)
- `skills/cdad-cycle/references/re-entry.md` (regla de equivalencia de una ejecución registrada)
- Ledgers como fuente de incidentes reales: `docs/specs/*/dispatch-ledger.md`

## Casos prioritarios (contrastar con el alcance del epic)
1. Un agente termina sin entregar resultado utilizable.
2. Una ejecución iniciada por el agente muere al terminar su sesión.
3. Se repiten llamadas, errores o intentos sin información nueva.
4. Un obstáculo de capacidades/permisos impide trabajo legítimo y provoca rodeos.

Distinguirlos de: ejecución larga pero saludable, polling justificado, nueva
iteración por una hipótesis distinta. Para cada caso, brevemente: señal disponible,
limitaciones de observación, decisión que necesita el orquestador, recuperación
mínima. No hacer relevamiento exhaustivo de sesiones; no inventar señales que el
runtime no expone (si dudas de que exista, márcalo VERIFY).

## Criterios de diseño del MVP
- Deterministas para observar hechos cuando alcancen; el juicio queda en el orquestador.
- Sin agente permanente ni servicio nuevo salvo justificación concreta.
- Falta de progreso ≠ contar herramientas o tokens.
- Un límite de intentos es señal para reconsiderar la estrategia, no prueba de incumplimiento.
- Un rechazo de permisos no implica mala conducta del agente.
- Un timeout solo no prueba bloqueo.
- Conservar resultado parcial y evidencia antes de recuperar/reintentar.
- Comprobar si una acción terminó antes de repetirla; evitar efectos duplicados.
- Una reanudación conserva intentos y causas anteriores.
- Estado desconocido permanece desconocido: no fabricar éxito ni fracaso.
- Intervenciones automáticas con condiciones claras y proporcionadas; lo ambiguo vuelve al orquestador con información útil.
- Sin alertas repetidas del mismo incidente sin cambios relevantes.
- Definir qué recibe el orquestador para decidir y qué pasa sin señal fiable.
- No implementar la renovación de contexto de 003-004; declarar solo las interfaces que no la obstaculicen.
- Generalidad: proyectos Go (tests junto al código) y ciclos sin código.

## Plan
Unidades pequeñas y coherentes (no una feature por comprobación), cada una con su
plan de validación (contrato `planning-contract-draft.md` §4/§4.1): tests focales,
escenarios controlados de fallo identificados como simulación, y prueba de que un
trabajo legítimo y progresivo puede continuar. Incluir cómo se adopta la capacidad
en un límite de tarea y cómo se registra su uso real (situación, evidencia,
decisión, falsas alarmas, costo, pendiente).

## Formato de respuesta
1. Tabla de casos (señal / límite de observación / decisión / recuperación).
2. Decisiones abiertas para el dueño (numeradas, con recomendación).
3. Borrador de `spec.md`. 4. Borrador de `plan.md`.
