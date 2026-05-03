# Etapa 2 — Especificación

Convertir idea funcional en spec implementable sin ambigüedad.

## Tu rol como orquestador

NO escribís el spec. Coordinás:

1. Emitís handoff a **architect modo brainstorm** (preguntas socráticas).
2. Validás cierre del brainstorm en re-entry.
3. Emitís handoff a **architect modo redacción de spec**.
4. Validás draft del spec en re-entry.
5. Pasás el spec al **humano para aprobación** (indelegable).
6. Cuando humano aprueba, cerrás la etapa.

## Sub-fase 2.1 — Brainstorm socrático

Cargá `references/handoff-prompts.md` sección "Architect (Etapa 2 — Brainstorm socrático)". Generá el packet con:

- Descripción funcional preliminar (de Etapa 1).
- `docs/landscape.md` y output de descubrimiento por feature (sección "Contexto técnico" en draft).
- `docs/systemPatterns.md`.

Entregás packet y terminás turno.

### Re-entry

Cuando el architect cierra brainstorm con resumen de decisiones, validá (ver `re-entry.md` sección "Architect — brainstorm"). Si pasa, emití handoff a redacción.

## Sub-fase 2.2 — Redacción del spec

Handoff packet del architect modo redacción con:

- Resumen del brainstorm (del re-entry anterior).
- Contenido de `assets/spec-template/spec.md`.
- `docs/systemPatterns.md`.

Entregás packet, terminás turno.

### Re-entry

Validá draft del spec (ver `re-entry.md` sección "Architect — draft de spec").

Si pasa: pasás al humano para aprobación.

## Sub-fase 2.3 — Aprobación humana (indelegable)

Decile al usuario:

> *"Spec en `docs/specs/<NNN>/spec.md`. Revisalo: (a) cada postcondición es lo que querés, (b) criterios de aceptación medibles, (c) out of scope completo. Si está OK, agregá la marca de aprobación al final del archivo (`Status: Approved by <vos> on <fecha>`) o en frontmatter (`approved_by: <vos>`, `approved_at: <fecha>`). Avisame cuando esté."*

**Si el usuario te pide aprobar vos**: declinás amablemente.

> *"La aprobación del spec requiere tu juicio sobre dominio, cliente, y producto. Yo puedo proponerte cambios si querés, pero la marca de aprobado va con tu nombre."*

**Si el usuario quiere saltarse la aprobación**:

> *"La aprobación es lo que define si el spec captura lo que necesitás. Sin esa marca, en Etapa 4 no vamos a saber contra qué versión validar el código. Tres minutos de leer y aprobar te ahorran retrabajo en Etapa 3 o 4."*

## Variantes según tamaño

- **Trivial** (fix puntual): spec puede ser un párrafo + un test que falla. Igual brainstorm + aprobación, pero más cortos.
- **Mediana** (mayoría): formato estándar.
- **Compleja** (múltiples componentes): dividir en `spec.md`, `plan.md`, `tasks.md`.

Decidilo con el usuario al inicio de la etapa.

## 🛑 Gate de salida (Etapa 2 → Etapa 3)

- [ ] `docs/specs/<NNN-feature-id>/spec.md` existe.
- [ ] Cuatro secciones mínimas presentes y no son placeholders.
- [ ] Postcondiciones numeradas y verificables.
- [ ] Criterios de aceptación medibles.
- [ ] Marca de aprobación humana inequívoca.

Cuando todos OK: actualizá state file (`current_stage: tdd`, `tdd_substage: red`, `active_feature: <feat-id>`, registrá `approved_by` en `stage_history`). Anunciá transición. Emití handoff a test-writer (RED) para postcondición 1.

## Si surge algo no contemplado en spec durante implementación

Regla: NO se agrega silenciosamente al código. Volvés a Etapa 2: actualizar spec, commitear el cambio (`docs: update spec — add postcondition X`), reaprobar. Recién entonces el implementer puede tocar el caso.

## Anti-patrones

- **AP-5**: saltar el spec porque "es simple". Mínimo: un párrafo + test que falla, con aprobación.
- **AP-6**: spec aprobado en silencio sin marca explícita. Sin marca, no avanzás.
- **AP-10**: delegar la aprobación al LLM. Indelegable.
