# Etapa 5 — Merge y Memory Bank

CI completo + actualización del Memory Bank con patrón Scribe.

## Tu rol como orquestador

NO actualizás el Memory Bank por tu cuenta. Coordinás:

1. Verificás CI completo (vos corrés si tenés bash, o pedís output al usuario).
2. Emitís handoff a **scribe** con spec + diff + review + Memory Bank actual.
3. Validás drafts en re-entry.
4. Pasás drafts al **humano** que edita y commitea (indelegable).
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

Si CI falla: **volvés a Etapa 3** con el output del fallo. Sin excepciones.

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

## 5.3 — Validación humana (indelegable)

Pasás los drafts al humano:

> *"Scribe terminó. Tres drafts:*
>
> *1. activeContext.md entry: <pegar>*
> *2. progress.md changes: <pegar>*
> *3. ADR: <pegar | "sin ADR sugerido", confianza <X>>*
>
> *Editá lo que el scribe entendió mal. Cuando estés conforme, commiteá vos con prefijo `docs(memory):` y autoría humana. Avisame cuando esté."*

**Si el usuario te pide que commitees vos**: declinás.

> *"El commit del Memory Bank lleva tu autoría porque refleja tu juicio sobre el contexto del proyecto. Yo draftié, vos editás y commiteás. Es lo que mantiene el Memory Bank confiable a lo largo del tiempo."*

## 5.4 — Decisión sobre ADR

Si el scribe propuso ADR:

- **Confianza Alta**: probablemente merece ADR. Pasalo al humano para que lo expanda.
- **Confianza Media**: preguntale al humano si la decisión amerita ADR.
- **Confianza Baja**: descartá por defecto, salvo que el humano vea valor.

Heurística general: ¿alguien en 6 meses podría preguntar "por qué hicimos X así"? Si sí → ADR. Si no → descartá.

## 5.5 — Merge

Una vez CI verde + Memory Bank commiteado (+ ADR si corresponde):

Mergeás a main. Estrategia (squash, merge, rebase) según convención del proyecto, no del skill.

## 🛑 Gate de salida (Etapa 5 → done)

- [ ] CI verde completo.
- [ ] `docs/activeContext.md` con entry nueva.
- [ ] `docs/progress.md` movió feature a "done".
- [ ] Si decisión arquitectónica → ADR nuevo en `docs/adr/`.
- [ ] Commit con prefijo `docs(memory):` y autoría humana.
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
- **AP-10**: delegar commit del Memory Bank al LLM.
