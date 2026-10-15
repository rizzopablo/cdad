# Encargo al reviewer — borrador spec/plan 003-006-runtime-adoption

Rol: `cdad-reviewer`, solo lectura, adversarial. Revisa
`docs/specs/003-006-runtime-adoption/architect-draft-001.md` (discovery, D1–D10,
V1–V6, spec P1–P10, plan T1–T4) contra el encargo
`handoff-architect-001.md`. Sin `opencode run`/`claude`/`codex` anidados, sin instalar.

## Qué evaluar
1. ¿Cubre el objetivo (descubrimiento + `receive` + activación por runtime +
   recorrido real) **sin funcionalidad nueva**? Señala scope creep y proporcionalidad
   (MVP: hallazgos que no rompen el camino feliz → deuda).
2. ¿Las postcondiciones son verificables por test o por evidencia observable? ¿Alguna
   no se puede probar sin red/runtimes reales y está asignada a una tarea con RED?
3. ¿Respeta las restricciones del dueño (nunca HOME, no afectar la sesión orquestadora
   ni otros proyectos, nada de rutas locales commiteadas, no endurecer permisos)?
4. Riesgos no cubiertos.

## Observaciones del orquestador para verificar (no las des por ciertas: compruébalas)
- **O-A (mezcla de versiones de guard):** los agentes Claude Code generados escriben a
  mano `command: ~/.claude/cdad-scripts/path-guard.sh <rol>`
  (`scripts/cdad-generate.py:501` y los agentes en la raíz adoptada, `.claude/agents/cdad-implementer.md`).
  Copiar o enlazar esos agentes en `.claude/agents` del proyecto **seguiría ejecutando el
  guard global viejo**. El borrador (D4/P5) no dice cómo se resuelve la ruta del hook.
  ¿Hace falta parametrizar la ruta en la generación (p. ej., relativa al proyecto) o
  reescribirla en la activación? ¿Qué es lo mínimo?
- **O-B:** los hooks de Claude Code viven en el frontmatter de cada agente, no en
  `settings.json`. ¿Es necesario que la activación emita `.claude/settings.json`? Un
  `settings.json` de proyecto afecta a cualquier sesión abierta en ese directorio.
- **O-C:** V6 ya está resuelto (historial actualizado a v4 = `818f12a`, commit `b186329`).
- **O-D:** el recorrido de Claude Code y Codex en T4 lo ejecuta el orquestador; ¿el guion
  §1.4 es ejecutable con `claude -p` / `codex exec` en una raíz desechable sin tocar HOME?

## Entrega
Veredicto (aprobable / aprobable con cambios / no aprobable), bloqueantes (BL-n),
recomendaciones (R-n) con razón y archivo:línea, y qué pasaría a deuda.
