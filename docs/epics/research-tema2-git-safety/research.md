# Tema 2: Git safety al cierre — investigación (02 Sep 2026)

> Fase 1: qué hace Superpowers, qué hacen otros, qué tiene CDAD, gap real.
> Sin tocar código. Decisión cycle light (aprobada por Pablo 02 Sep).

## Fuentes revisadas

| Fuente | Qué aporta |
|---|---|
| obra/superpowers `finishing-a-development-branch/SKILL.md` (225 líneas, leído completo) | Core principle: Verify tests → Detect environment → Present options → Execute choice → Clean up. Detección de entorno (GIT_DIR vs GIT_COMMON, guard de submodule, detached HEAD), base branch confirmada (nunca asumir), menú fijo, discard con palabra literal, limpieza por provenance (solo worktrees bajo `.worktrees/`/`worktrees/`), nunca `--force` por iniciativa propia |
| obra/superpowers `using-git-worktrees/SKILL.md` (167 líneas, leído completo) | Contraparte al INICIO: detectar aislamiento existente antes de crear (guard submodule: `show-superproject-working-tree`), tool nativo > git fallback, `.worktrees/` verificada con `check-ignore`, baseline de tests en el workspace nuevo |
| CodingCossack/agent-skills-library (fork público del mismo skill) | Idéntico en lo esencial; añade `⊘ BLOCKED:TESTS/CONFLICTS` como estados de salida explícitos y detección de base branch por merge-base más cercano con ask si es ambiguo |
| Múltiples mirrors del mismo skill (skillstore, termo, aigearbase, codeape, eliteai) | El skill está masivamente adoptado/copiado; variante de eliteai añade "Rules That Have No Exceptions" y checklist de verificación; aigearbase conserva la versión más reciente (provenance check ampliado, `git worktree prune`) |

## Lo que CDAD YA tiene (verificado)

- `stage-5-merge.md` §5.1: CI/suite obligatoria antes de cerrar (equivalente
  al Step 1 "Verify Tests" — más estricto: linter+types+suite).
- §5.3: aprobación del usuario indelegable, ejecución de git del orquestador
  (AP-10). El principio usuario-decide/orquestador-ejecuta ya está.
- Cierre de feature ya define qué pasa DESPUÉS del merge (Memory Bank,
  activeContext, next feature).

## Gap real

- La mecánica de integración (merge/PR/keep/discard, base branch, entorno,
  limpieza) NO existe en CDAD: la variante de Superpowers y la de
  CodingCossack coinciden en que ese vacío es donde los agentes destruyen
  trabajo. En esta sesión ya vimos el patrón de riesgo en vivo (openchamber
  ejecutó `git reset` y deshizo trabajo — memory/MEMORY.md 05 Ago).
- El state file y la regla "si en etapa N falla algo volvé a N-1" asumen que
  el árbol sigue intacto; un discard/merge mal ejecutado lo rompe.

## Propuesta adaptada (borrador de síntesis)

Sección §5.4 "Cierre de la branch (git safety)" en stage-5-merge.md, DESPUÉS
del Memory Bank (el orden CDAD: CI → Memory Bank → decisión de integración):

1. **Precondición heredada**: la suite ya está verde (§5.1) — no se re-pide.
2. **Detectar entorno**: repo normal / worktree vinculado / detached HEAD
   (con guard de submodule). El menú se adapta (detached: sin merge local).
3. **Base branch**: confirmar con el usuario si no está registrada en el
   spec/state; nunca asumir (merge a base equivocada = caro de revertir).
4. **Menú fijo** (el usuario decide, el orquestador ejecuta — §5.3):
   merge local (con re-verificación de suite sobre el resultado mergeado,
   conflicto = STOP sin auto-resolver) / push+PR (worktree vive para iterar
   feedback) / dejar como está / descarte.
5. **Descarte**: solo a pedido explícito del usuario, listando QUÉ se borra
   (branch, commits, worktree) y esperando la palabra literal `discard` —
   un "sí, borralo" no alcanza.
6. **Limpieza por provenance**: solo worktrees que el propio ciclo creó
   (`.worktrees/`/`worktrees/`); worktree ajeno → intacto. Nunca `--force`
   por iniciativa propia; si `worktree remove` es rechazado, mostrar qué
   contiene y preguntar.
7. **Anti-racionalización** propia (del repo, no copiada) + "cuándo NO
   aplica" (proyectos sin branch de feature / squash por convención del
   proyecto: la decisión sigue siendo del usuario, cambia el comando).

## Decisión de forma

Cycle light: 1 feature (cdad-006-git-safety-close), 1 archivo tocado
(stage-5-merge.md) + quizá SKILL.md (tabla de lectura ya cubre stage-5).
No amerita epic: un solo contrato, un solo rol (orquestador).
