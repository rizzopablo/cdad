# Etapa 4 — Review en dos capas

Capa 1: reviewer hace pasada exhaustiva con spec en contexto. Capa 2: humano valida priorización.

## Tu rol como orquestador

NO hacés review. Coordinás:

1. Emitís handoff a **reviewer** (capa 1) con diff + spec + boundaries + convenciones.
2. Validás reporte en re-entry.
3. Pasás reporte al **humano para validar priorización** (capa 2, indelegable).
4. Si hay bloqueantes a aplicar: handoff de vuelta a implementer.
5. Cierre de etapa cuando todos los bloqueantes resueltos o desestimados.

## Capa 1 — Handoff al reviewer

Cargá `references/handoff-prompts.md` sección "Reviewer (Etapa 4)".

Generá packet con:

- Diff completo de la feature (`git diff <base>..HEAD`).
- Spec aprobado (`docs/specs/<feat>/spec.md`).
- Interface / contrato.
- `.importlinter` o equivalente.
- Convenciones (`AGENTS.md`, `CONTRIBUTING.md`, `docs/systemPatterns.md`).

**Recomendación al usuario antes del packet**: *"Idealmente el reviewer corre con un modelo distinto al implementer. Si tu entorno te lo permite (cambiar modelo en chat nuevo), aprovechalo. Si no, igual sirve."*

Entregás packet, terminás turno.

### Re-entry

Cargá `re-entry.md` sección "Reviewer". Validá estructura del reporte.

Si pasa: pasás al humano para capa 2.

## Capa 2 — Validación humana (indelegable)

Decile al usuario:

> *"Reporte en `docs/specs/<feat>/review.md`: <X> bloqueantes, <Y> opcionales. Tu trabajo: leé el reporte (no el diff completo) y validá la priorización. Para cada bloqueante: ¿genuinamente bloqueante o hay contexto que el reviewer no tiene? Para cada opcional: ¿aplicar o descartar? Cuando termines, pasame las decisiones."*

### Cuando el humano vuelve con priorización

Aplicá la matriz de severidad por defecto para sanity-check:

| Tipo | Severidad por defecto | Excepción |
|------|----------------------|-----------|
| Divergencia del spec | Bloqueante | Solo si spec estaba desactualizado |
| Violación de boundary | Bloqueante | Solo si ADR autoriza |
| Riesgo de seguridad | Bloqueante | Sin excepciones |
| Bug funcional | Bloqueante | Sin excepciones |
| Inconsistencia de estilo | Opcional | Bloqueante si masiva |
| Simplificación | Opcional | Bloqueante si complejidad problemática |
| Feature adicional sugerida | Descartar | — |

Si el humano marcó como "no bloqueante" algo que la matriz dice bloqueante (ej. divergencia del spec), preguntale el motivo y registralo en `review.md` como nota.

Si detectás sesgo (humano queriendo cerrar rápido, marcando bloqueantes como opcionales sistemáticamente):

> *"Si dudás de si un bloqueante es genuino, errate del lado de tratarlo como bloqueante. El costo de una iteración extra es bajo; el costo de mergear un bug es alto."*

## Loop con Etapa 3

Si hay bloqueantes a aplicar (o opcionales aceptados):

1. Anotá la lista priorizada de fixes.
2. Emití handoff a implementer con la lista.
3. Suite debe seguir verde tras cada fix. Si un fix requiere cambio de comportamiento, eso significa que el **spec necesita actualizarse** → vuelta a Etapa 2.
4. Tras los fixes: idealmente otra pasada del reviewer. En features chicas con fixes mecánicos, podés saltar (criterio del usuario).

## 🛑 Gate de salida (Etapa 4 → Etapa 5)

- [ ] Existe `docs/specs/<feat>/review.md`.
- [ ] Bloqueantes resueltos o explícitamente desestimados con motivo escrito.
- [ ] Usuario aprobó priorización (no delegado al LLM).
- [ ] Suite sigue verde tras los fixes.

Cuando todos OK: actualizá state (`current_stage: merge`). Anunciá transición. Emití handoff a scribe (Etapa 5).

## Anti-patrón principal

**Skipear el review en features pequeñas.** Aunque sea review breve sobre 30 líneas, vale.
