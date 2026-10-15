# Encargo al architect — 003-006-runtime-adoption (discovery + spec/plan draft)

Rol: `cdad-architect`, solo lectura. Entregas en tu respuesta (el orquestador
materializa). Objetivo de tiempo: ~30-40 min. Sin `opencode run`/`claude`/`codex`
anidados, sin comandos en segundo plano, sin instalar nada.

## Objetivo
Que lo ya construido en 003-001..004 (`cdad_packet.py prepare`, `cdad_result.py
receive`, `cdad_guard.py`, `cdad_continuity.py`) **se descubra y se use** en el
ciclo normal, y que cada runtime (OpenCode, Claude Code, Codex) cargue **una misma
versión operativa** de skills, agentes y hooks. **No es funcionalidad nueva**:
cablear, activar y comprobar. MVP proporcional; endurecimiento a deuda.

## Hallazgos verificados (revisión externa + comprobación del orquestador en `a46497a`)
1. **Descubrimiento roto:** ni `skills/cdad-cycle/SKILL.md` ni
   `agents/cdad-orchestrator.md` mencionan `cdad_result`, `cdad_guard` ni
   `cdad_continuity`. `references/continuity.md` y `references/progress-guards.md`
   existen pero nada las enlaza desde la tabla de referencias del SKILL.
2. **Recepción sin usar:** el orquestador recibe salidas de roles sin pasar por
   `cdad_result receive`; por eso `cdad_continuity reconcile` queda en
   `dispatched-unknown` (deuda RU-2a de 003-004).
3. **Versión por runtime divergente:**
   - OpenCode en este proyecto: `.opencode/opencode.jsonc` (git-ignorado) apunta a la
     raíz aislada `818f12a` → correcto.
   - Claude Code: agentes/skills globales (`~/.claude`) anteriores; `~/.claude/cdad-scripts/path-guard.sh`
     difiere del de la versión adoptada. No hay configuración de proyecto que active la raíz aislada.
   - Codex: carga `~/.agents/skills` (copia vieja, sin las 3 herramientas) y
     `.agents/skills` del proyecto (VERIFY). CDAD no genera adaptador de agentes para Codex.
4. La raíz aislada adoptada ya contiene `.claude/`, `.agents/`, `.config/opencode/`,
   `cdad-scripts/` y el manifest (inspeccionar su estructura: está fuera del repo,
   ruta en `docs/runtime-adopted-version.md`).

## Restricciones del dueño (no negociables)
- **Nunca instalar ni modificar CDAD en el HOME real** (`~/.claude`, `~/.agents`,
  `~/.config/opencode`): rompe los agentes de otras sesiones. La activación debe ser
  **por proyecto** y apuntar a la raíz aislada adoptada.
- La activación **no debe afectar a la sesión orquestadora en curso ni a otros
  proyectos**. Diseñar con cuidado los hooks de Claude Code de proyecto (un hook
  roto bloquea herramientas): proponer cómo probarlo antes en un proyecto/raíz desechable.
- Rutas locales y configs de activación **no se commitean** (repo potencialmente
  público; anonimizar): el producto entrega el procedimiento/generador y tests; el
  archivo concreto de activación queda git-ignorado como `.opencode/`.
- No endurecer permisos. Sin push automático.
- Cada runtime usa su mecanismo nativo de subagentes; el despacho por shell es un
  artefacto del orquestador externo actual.

## Entradas (leer)
- `docs/epics/epic-003-context-efficiency/plan.md` (criterios de cierre), `execution.md`
- `docs/specs/003-004-context-continuity/{closure.md,debt.md,continuity-ledger.md}`
- `docs/specs/003-002-artifact-tools/closure.md`, `docs/specs/003-003-progress-guards/closure.md`
- `docs/specs/003-005-claude-code-packets/spec.md` (port previo a Claude Code)
- `docs/runtime-adopted-version.md`, `install.sh` (solo lectura: `--help`, `--dry-run` no lo corras), `Makefile` (staging)
- `skills/cdad-cycle/SKILL.md`, `skills/cdad-cycle/references/*.md`, `agents/cdad-orchestrator.md`, `sources/` (generación de agentes por runtime)
- Configuración OpenCode actual: `.opencode/opencode.jsonc`

## Discovery obligatorio
1. Inventario por runtime: qué carga hoy (skills, agentes, hooks/guards), desde dónde, y
   cómo se activaría por proyecto la raíz aislada (mecanismo nativo de cada uno; marcar VERIFY lo no comprobado).
2. Puntos de cableado mínimos en SKILL/orquestador/referencias para `receive`,
   `begin`/`checkpoint`, `reconcile`, `resume`, `trigger`, `classify`: dónde y en qué paso del ciclo.
3. Recorrido de aceptación breve por runtime (no un desarrollo entero): sesión nueva
   → reporta qué archivos/versión cargó → consume un paquete → `receive` del resultado →
   checkpoint → reconstrucción con `resume`. Qué es evidencia suficiente.
4. Riesgos: hook roto, mezcla de versiones (agentes nuevos + guard viejo), Codex sin
   adaptador de agentes (¿basta skills + prompt de rol con el paquete?).
5. Qué entra y qué va a deuda (lector de sesiones para `classify` y medición de
   contexto quedan fuera, explícitos).

## Entregables
- Discovery (puntos 1–5) con decisiones D1..Dn y VERIFY.
- Borrador `spec.md` (postcondiciones P1..Pn verificables) y `plan.md` (≤4 tareas,
  dependencias, RED esperado por tarea; la última tarea = recorrido real por runtime + enmienda de cierre del epic como borrador para el dueño).
