# Encargo al architect — 003-004-context-continuity (discovery + spec/plan draft)

Rol: `cdad-architect`, solo lectura. Entregas en tu respuesta (el orquestador
materializa). Objetivo de tiempo: ~30-40 min. Sin `opencode run` anidados, sin
sondas que provoquen incidentes reales, sin comandos en segundo plano.

## Objetivo
Que un orquestador pueda rotar/reanudar su sesión durante trabajo prolongado sin
pedir al usuario que repita objetivo ni autorizaciones, sin duplicar efectos y sin
cargar el historial completo: memoria activa pequeña + referencias íntegras.
Es la última feature del epic 003. MVP proporcional: lo mínimo determinista que
funcione en el camino feliz; endurecimiento a deuda priorizada.

## Entradas (leer)
- `docs/epics/epic-003-context-efficiency/remaining-features-handoff.md` §003-004 (resultado, discovery obligatorio, P1–P6, aceptación real)
- `docs/epics/epic-003-context-efficiency/plan.md`, `execution.md`
- `skills/cdad-cycle/references/re-entry.md`, `state-detection.md`, `progress-guards.md`
- Contratos ya entregados que debes reutilizar, no reescribir:
  - 001: identidad/paquete/state (`docs/specs/003-001-role-packets/`, `docs/.cdad-state.json`, `cdad_packet.py`)
  - 002: receipts/resultados originales (`docs/specs/003-002-artifact-tools/closure.md`, `cdad_result.py`)
  - 003: eventos, budget, record (`docs/specs/003-003-progress-guards/spec.md`, `closure.md`, `debt.md`, `cdad_guard.py`)
- Evidencia real de continuidad ya existente: `docs/epics/epic-003-context-efficiency/handoff*.md`, `docs/activeContext.md` (son el "active record" manual que hoy usamos)

## Hechos del entorno que el diseño debe respetar (decisiones del dueño)
- Cada entorno usa su mecanismo nativo de subagentes (OpenCode nativo: un solo nivel,
  sin subagentes anidados). El despacho por shell `opencode run` es un artefacto del
  orquestador externo actual, no el modelo de diseño.
- El guard de 003 es opcional y depende del entorno; no hay lector de sesiones por runtime.
  No asumir señales de runtime que no estén verificadas (márcalas VERIFY).
- Salir de la raíz del proyecto está habilitado por defecto; no endurecer permisos.
- No convertir bytes en tokens. Si el contador real de contexto no existe, `null` + margen conservador.
- "Habrá que calibrar con uso real": preferir mecanismos simples y ajustables.

## Discovery obligatorio (entregar antes de la spec)
1. Tres capas: active record pequeño, checkpoint inmutable, historia referenciable.
   Autoridad y checksum de cada una. ¿Cuánto de esto ya existe (state, Memory Bank, handoffs, ledgers)?
2. Schema mínimo del active record (objetivo, scope, autoridad/expiración, decisiones
   con razón, incertidumbres, tareas/gates, agentes en curso, receipts, presupuesto,
   siguiente acción).
3. Algoritmo de reconciliación write-ahead antes de dispatch y posterior via
   status + receipts. Sesión desaparecida ≠ fracaso ni autorización para repetir.
4. Trigger preventivo (perfil 200k/150k/120k) con unknowns explícitos por runtime.
5. Matriz crash/restart/split-brain/stale/autoridad vencida/tarea ya cerrada.

## Formato de respuesta
1. Tabla de lo que ya existe vs lo que falta (reutilización).
2. Schema del active record + algoritmo de reconciliación + triggers con unknowns + matriz.
3. Decisiones abiertas para el dueño (numeradas, con recomendación).
4. Borrador de `spec.md`. 5. Borrador de `plan.md` (tareas pequeñas con validación focal,
   incluida la adopción real en un límite de tarea natural según el brief).
