# Tema 5: Despacho paralelo — investigación (02 Sep 2026)

## Fuentes revisadas

| Fuente | Qué aporta |
|---|---|
| obra/superpowers `dispatching-parallel-agents/SKILL.md` (167 líneas, leído completo) | Árbol de decisión (¿independientes? ¿sin estado compartido?), un prompt autocontenido por agente, integración final: revisar resúmenes → chequear conflictos → suite completa una vez |
| arittr/spectacular `executing-parallel-phase` | El más riguroso: **worktree por task SIEMPRE (incluso N=1)** — "los worktrees no son una optimización anti-conflicto, son la arquitectura que habilita el paralelismo"; `--detach` (git no permite la misma branch en 2 worktrees); **phase boundaries en el prompt** ("NO crees archivos de fases posteriores, ni stubs con TODO"); verificar branches ANTES de stack; stack ANTES de cleanup (los worktrees fallidos se preservan para debugging) |
| vasilyu1983/ai-agents-public `ai-agent-worktrees` | Reglas: un worktree por agente, una branch por worktree, **disjoint file ownership** (mismo archivo → wave dispatch secuencial), orquestador en main; merge: dependencia upstream primero + rebase + suite tras cada merge; **conflictos los resuelve el orquestador, no los subagentes**; detección pre-merge con `git diff --name-only` + `comm -12`; lock contention (`git gc`/`prune` prohibidos en paralelo) |
| SpillwaveSolutions `parallel-worktrees` | **One worktree per agent + non-overlapping file assignments + siempre escribir RESULTS.md + commit antes de señalar complete**; LLM non-determinism como ventaja (N agentes, mismo prompt, elegir el mejor) |
| TheAhmadOsman/parallel-agent-worktree-skill | Integración review-gated ("nunca mergear por el resumen del worker"); capturar `INTEGRATION_BRANCH` en preflight; changelog fragments para evitar colisión en el mismo archivo |
| enuno/claude-command-and-control | Rollback: si la integración falla, los worktrees se PRESERVAN para debugging |

## Lo que CDAD YA tiene (verificado)

- Aislamiento por sesión (sub-agent-strategies.md) — sesiones sin contexto compartido.
- Packet de postcondiciones ortogonales (stage-3:37,65) — para UN test-writer.
- Regla de state-passing §6 (prompt autocontenido) — ya es el estándar del handoff.
- Orquestador que consolida y escribe el state file (nadie más lo toca).
- §5.6 git safety (recién incorporado): provenance de worktrees, cleanup seguro.
- cdad-008: Consumes/Produces — el contrato de interfaz entre tareas paralelas ya existe.

## Gap real

1. Sin árbol de decisión de paralelismo (el default es secuencial sin análisis).
2. Sin reglas de despacho: scope disjunto, no-touch lists, integración final.
3. Sin ownership del state file bajo paralelismo (hoy implícito, no escrito).

## Propuesta adaptada (síntesis CDAD)

**Extensión de `stage-3-tdd.md`** (sección "Despacho paralelo" tras el packet
ortogonal) + **extensión de `sub-agent-strategies.md`**:

1. **Árbol de decisión**: ¿2+ tareas genuinamente independientes (sin estado
   compartido, sin archivos en común)? → paralelo. ¿Comparten archivos o
   estado? → secuencial o wave dispatch. El packet ortogonal (un test-writer,
   N postcondiciones) sigue siendo el default; paralelo cuando el packet es
   demasiado grande o las tareas son dominios disjuntos.
2. **Precondición**: los prompts paralelos solo existen si cdad-008 produjo
   plan con Consumes/Produces (el contrato de interfaz es lo que hace
   independientes las tareas — sin él, no hay paralelismo seguro).
3. **Reglas de despacho**: (a) prompt autocontenido por sesión (§6 ya lo
   exige — se explicita para paralelo: owned files + do-not-touch list),
   (b) scope disjunto verificado con `git diff --name-only` si duda,
   (c) mismo rol, sesiones distintas — el aislamiento se mantiene porque
   cada sesión sigue sin ver el trabajo de las otras.
4. **State file**: SOLO el orquestador lo escribe, siempre (las sesiones
   paralelas nunca lo tocan; el orquestador consolida al recibir cada
   re-entry). Hoy es implícito — se vuelve regla escrita.
5. **Integración final (el orquestador, nunca un rol)**: revisar cada
   resumen → chequear overlap de archivos → suite COMPLETA una sola vez al
   final → conflicto = los resuelve el orquestador, nunca los subagentes.
6. **Anti-racionalización**: "los archivos no se pisan, no necesito
   worktree" (el worktree habilita el paralelismo, no previene conflictos —
   pero CDAD con sesiones en el mismo árbol usa wave dispatch como default
   conservador y worktrees como opcional documentado); "es 1 sola tarea,
   básicamente secuencial" / "el resumen del agente dice que salió bien".

**Formato: cycle light** (cdad-009; toca stage-3-tdd.md + sub-agent-strategies.md).
