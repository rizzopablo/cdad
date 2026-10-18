# Cierre de 006-002-delegation-by-layer

**Feature:** 006-002-delegation-by-layer · **Epic:** `epic-006-opencode-concurrency` (segunda feature) · **Cerrada:** 2026-10-18 · **Contrato:** `spec.md` con enmiendas 001 y 002 · **Plan:** `plan.md` con A-1 y A-2 · **Aprobación:** orquestador Claude bajo la HITL delegada del epic-006; enmiendas y Memory Bank aprobados por Pablo.

## 1. Qué entrega

La delegación se resuelve por capa (ADR-032): cada orquestador generado declara su mecanismo nativo en una sección `delegation` compuesta desde `sources/agents/adapters/`; la skill queda neutral (sin herramientas ni modelos de un runtime); el adaptador CLI solo cruza runtimes; el recibo es el mismo para todo transporte; el orquestador tiene cuatro reglas de contexto.

## 2. Gates

| Etapa | Evidencia |
|---|---|
| Construcción U1–U6 | RED→GREEN por unidad (`u*-red.md`, `u*-green.md`), fix de U1 (`u1-fix.md`), testfix de U3 (`u3-testfix.md`), enmiendas 001/002 (`u6b-*`, `u6c-*`) |
| U8 aceptación real | orquestador OpenCode con los agentes generados en worktree aislado; despacho por `task` a `cdad-reviewer` (glm); 0 invocaciones del adaptador en 56 comandos (`execution.md`) |
| Review | 1 bloqueante, 4 opcionales, 4 abstenciones (`review.md`) |
| Review-fix B-1 | RED `5c85d68` → GREEN `a25fc20` (`rf-red.md`, `rf-green.md`) |
| Re-review | B-1 cerrado, 0 bloqueantes (`rereview.md`) |
| Suite de cierre | 1119 passed, 5 skipped, sin fallas |
| Memory Bank | `activeContext.md`, `progress.md`, `systemPatterns.md`, ADR-032 |

## 3. Abierto al cerrar

- **Redespliegue en HOME** de 006-002, a la orden del dueño (lo instalado es `6978709`).
- **Consumidor:** su handoff todavía prescribe el adaptador; lo actualiza su dueño.
- **Deuda:** O-1..O-4, NF-1, `sub-agent-strategies.md:49-50` (detalle de Claude Code en la skill), DT-8, registro de despacho sin recibo del intento detenido `at-006-002-u6b-red-001`, observaciones de U8 (el orquestador leyó código del CLI; notas de orquestación de `execution.md` tomadas como mandato; `opencode.json` de proyecto vació la lista de agentes; `prepare` publica agentes desde la versión instalada).
