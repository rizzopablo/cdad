# Etapa 5 — Merge y Memory Bank

CI completo + actualización del Memory Bank con patrón Scribe.

## Tu rol como orquestador

NO actualizás el Memory Bank por tu cuenta. Coordinás:

1. Verificás CI completo (vos corrés si tenés bash, o pedís output al usuario).
2. Emitís handoff a **scribe** con spec + diff + review + Memory Bank actual.
3. Validás drafts en re-entry.
4. Pasás drafts al **usuario** para APROBACIÓN (indelegable); vos los commiteás tras la aprobación.
5. Cierre de feature cuando CI verde + Memory Bank commiteado.

## 5.1 — Verificación CI

**No es opcional.**

Verificaciones obligatorias:

- Linter completo sobre archivos modificados.
- Type checker (mypy / tsc / etc.).
- Import-linter o equivalente.
- Suite completa: unit + integration + contract + property.
- Verificaciones específicas del proyecto.

Si tenés bash: corré la suite. Si no: pedile al usuario el output.

> *"Corré la suite completa (`<comando del proyecto>`). Necesito ver: linter, type checker, import-linter, todos los tests. Si algo falla, volvemos a Etapa 3."*

Si CI falla: activá `stage-debugging` (`references/stage-debugging.md`) con el output del fallo — sin causa raíz verificada no hay fix. Con el diagnóstico y el loop rojo, volvé a Etapa 3. Sin excepciones.

## 5.2 — Handoff al Scribe

Cargá `references/handoff-prompts.md` sección "Scribe (Etapa 5)".

Generá packet con:

- Spec aprobado (`docs/specs/<feat>/spec.md`).
- Diff completo del PR.
- Reporte del reviewer (`docs/specs/<feat>/review.md`).
- Memory Bank actual (`projectbrief`, `activeContext`, `progress`, `systemPatterns`, `adr/`).

Entregás packet, terminás turno.

### Re-entry

Cargá `re-entry.md` sección "Scribe". Validá tres drafts presentes (activeContext entry, progress changes, ADR draft o "sin ADR").

## 5.3 — Validación del usuario (indelegable)

Pasás los drafts al usuario para aprobación:

> *"Scribe terminó. Tres drafts:*
>
> *1. activeContext.md entry: <pegar>*
> *2. progress.md changes: <pegar>*
> *3. ADR: <pegar | "sin ADR sugerido", confianza <X>>*
>
> *Editá lo que el scribe entendió mal. Cuando estés conforme, aprobá; el orquestador commitea con prefijo `docs(memory):`. Avisame cuando esté."*

**La aprobación es del usuario (indelegable); la ejecución del git es del
orquestador.** Si el usuario aprueba los drafts, vos los commiteás con `git add
docs/**` + `git commit` (prefijo `docs(memory):`).

## 5.4 — Decisión sobre ADR

Si el scribe propuso ADR:

- **Confianza Alta**: probablemente merece ADR. Pasalo al usuario para que lo expanda.
- **Confianza Media**: preguntale al usuario si la decisión amerita ADR.
- **Confianza Baja**: descartá por defecto, salvo que el usuario vea valor.

Heurística general: ¿alguien en 6 meses podría preguntar "por qué hicimos X así"? Si sí → ADR. Si no → descartá.

## 5.5 — Merge

Una vez CI verde + Memory Bank commiteado (+ ADR si corresponde):

Mergeás a main. Estrategia (squash, merge, rebase) según convención del proyecto, no del skill.

## 5.6 — Cierre de la branch (git safety)

**Precondición heredada**: suite ya verde (§5.1) y Memory Bank cerrado (§5.2-5.3). No se re-verifican acá; esta sección cubre lo que pasa con la branch y el worktree una vez que el trabajo está terminado y aprobado.

### Paso 1 — Detectar el entorno

Antes de tocar nada, determiná en qué tipo de repo estás:

```bash
git rev-parse --git-dir
git rev-parse --git-common-dir
git rev-parse --show-superproject-working-tree
```

- Si `--git-dir` y `--git-common-dir` coinciden → repo normal.
- Si `--git-common-dir` apunta a otro lugar → worktree vinculado.
- Guard de submodule: si `--show-superproject-working-tree` devuelve un path → estás dentro de un submodule; el repo real es el superprojecto (repo normal para efectos del cierre).

| Entorno detectado | Qué aplica |
|---|---|
| Repo normal | Menú completo, incluido merge local. |
| Worktree vinculado con branch propia | Menú completo. |
| Detached HEAD | Menú sin merge local (push + PR, keep o discard). |

### Paso 2 — Confirmar la base branch

Si la base no está registrada en el spec ni en el state file, **confirmá con el usuario**: *"Esta branch salió de `<mejor candidata>` — ¿correcto?"*. **Nunca** la asumas ni la infieras en silencio: un merge a base equivocada es caro de revertir.

### Paso 3 — Menú fijo de cierre

> *"Implementación completa. ¿Qué hacemos?"*
>
> 1. **Merge local** a `<base>`
> 2. **Push** y crear **PR**
> 3. **Keep**: dejar la branch como está
> 4. **Discard**: descartar el trabajo

El usuario elige; el orquestador ejecuta (§5.3). Nunca elijas por defecto.

**Ejecución por opción:**

1. **Merge local**: corré el merge y hacé re-verificación de la suite sobre el resultado mergeado (el gate valida el árbol a mergear, no el árbol que estaba cuando corriste la suite hace una hora). Si aparecieron conflictos: **STOP** — listá los archivos afectados, sin auto-resolver nada, y llevá la decisión al usuario. Si el merge falla, la branch y el worktree quedan en su lugar.
2. **Push + PR**: el worktree sigue vivo para iterar el feedback del PR.
3. **Keep**: reportá dónde quedó la branch y el worktree.
4. **Discard**: SOLO a pedido explícito del usuario. Mostrá qué se borra (branch, lista de commits, worktree) y esperá que el usuario tipee la palabra literal `discard` — *"sí, borralo"* no alcanza. Recién entonces: `git branch -D` + limpieza.

### Limpieza por provenance

Solo limpiás los worktrees que el propio ciclo creó (`.worktrees/` / `worktrees/`). Un worktree ajeno al ciclo queda intacto.

```bash
git worktree remove <path>   # desde la raíz del repo
git worktree prune
```

Si la remoción es rechazada (archivos sin commitear): mostrá el output de `git status --porcelain` y preguntale al usuario. **Sin `--force` por iniciativa propia** — el rechazo significa que hay archivos que existen solo ahí.

### ⚠️ Orden crítico

**Merge primero → worktree después → branch al final.** Borrar la branch con el worktree vivo referenciándola falla; y remover el worktree antes de confirmar el merge destruye trabajo si el merge falla.

### Anti-racionalización

| Racionalización | Corrección |
|---|---|
| "Ya corrimos la suite hace un rato" | El gate valida el árbol a mergear: re-corre sobre el resultado del merge. |
| "Es obvio que quiere mergear" | La decisión es del usuario (§5.3). Presentá el menú. |
| "Sí, borralo" alcanza como confirmación | Solo la palabra literal `discard` autoriza destrucción. |
| "Este otro worktree viejo lo limpio de paso" | Provenance: solo los que este ciclo creó. |
| "El rechazo del worktree remove es un tecnicismo, uso --force" | El rechazo significa archivos que existen solo ahí; forzar los destruye. |
| "El merge falló pero es flaky, reintento" | Un resultado mergeado rojo frena todo; branch y worktree quedan mientras se investiga. |
| "Detecto la base con git y listo" | Merge a base equivocada es caro de revertir; confirmá con el usuario. |

### Cuándo NO aplica

- **Proyectos con squash o rebase-merge por convención**: cambia el comando de integración, no la decisión del usuario ni el menú.
- **Repos sin branch de feature** (commiteo directo a main — común en proyectos solo o monorepo): el menú se reduce a push/PR, y la sección aplica solo a lo no destructivo.

## 🛑 Gate de salida (Etapa 5 → done)

- [ ] CI verde completo.
- [ ] `docs/activeContext.md` con entry nueva.
- [ ] `docs/progress.md` movió feature a "done".
- [ ] Si decisión arquitectónica → ADR nuevo en `docs/adr/`.
- [ ] Commit con prefijo `docs(memory):` — aprobado por el usuario, ejecutado por el orquestador.
- [ ] Feature mergeada.

Cuando todos OK: actualizá state (`current_stage: done`, `active_feature: null`).

**Si la feature pertenece a un epic** (`active_epic` no null en el state file), cerrá así:

> *"Feature `<X>` cerrada. Memory Bank actualizado. La feature pertenece al epic `<epic-id>`. Te recomiendo volver a `cdad-epic` (en chat nuevo) para coordinar la siguiente feature del epic. ¿O preferís arrancar feature standalone fuera del epic acá?"*

**Si la feature NO pertenece a un epic** (caso standalone), cerrá así:

> *"Feature `<X>` cerrada. Memory Bank actualizado. ¿Próxima feature, o cerramos por hoy?"*

Si próxima feature → vuelta a Etapa 1.

## Anti-patrones

- **AP-7**: Memory Bank desactualizado. Bloqueá cierre.
- **AP-8**: ADRs especulativos o ausentes.
- **AP-9**: CI skipeado.
- **AP-10**: delegar la APROBACIÓN del Memory Bank al LLM. La ejecución del commit es del orquestador; la decisión de aprobar es del usuario (indelegable).
