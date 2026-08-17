# Etapa 4 — Review en dos capas

Capa 1: reviewer hace pasada exhaustiva con spec en contexto. Capa 2: el usuario (humano o agente autónomo de mayor jerarquía) valida priorización.

## Tu rol como orquestador

NO hacés review. Coordinás:

1. Emitís handoff a **reviewer** (capa 1) con diff + spec + boundaries + convenciones.
2. Validás reporte en re-entry.
3. Pasás reporte al **usuario para validar priorización** (capa 2, por defecto indelegable; ver excepción más abajo si el usuario pidió explícitamente delegarla a un agente para esta feature).
4. Si hay bloqueantes a aplicar: handoff de vuelta a implementer.
5. Cierre de etapa cuando todos los bloqueantes resueltos o desestimados.

## Capa 1 — Handoff al reviewer

Cargá `references/handoff-prompts.md` sección "Reviewer (Etapa 4)".

Generá packet con:

- **Contrato de veredicto (verdict-tuple.md):** referenciá el tuple de 4 campos — cada hallazgo del reviewer emite Veredicto (BLOQUEANTE|OPCIONAL|ABSTENER) + Bucket h|m|l por observables + rationale + provenance. El bucket lo deriva el reviewer por regla determinística (familia de modelo, diff completo, rationale grounded, spec en contexto), nunca por confianza elicitada. La sección Abstenciones se reporta siempre (vacía si no aplica).
- Diff completo de la feature (`git diff <base>..HEAD`).
- Spec aprobado (`docs/specs/<feat>/spec.md`).
- Interface / contrato.
- `.importlinter` o equivalente.
- Convenciones (`AGENTS.md`, `CONTRIBUTING.md`, `docs/systemPatterns.md`).
- Pedido explícito de auditoría test↔postcondición: cada test del diff debe mapear a una postcondición del spec (marcar sobrantes) y ninguno debe depender de estructura interna (marcar mocks sobre plumbing, ver AP-14 en `anti-patterns.md`). Esta auditoría la hace el reviewer precisamente porque es una sesión distinta a la que escribió los tests — no delegar de vuelta al test-writer.

**Recomendación al usuario antes del packet**: *"Idealmente el reviewer corre con un modelo distinto al implementer. Si tu entorno te lo permite (cambiar modelo en chat nuevo), aprovechalo. Si no, igual sirve."*

Entregás packet, terminás turno.

### Re-entry

Cargá `re-entry.md` sección "Reviewer". Validá estructura del reporte.

Si pasa: pasás al usuario para capa 2.

## Capa 2 — Validación (del usuario por defecto; delegable solo bajo pedido explícito)

**Regla general: la priorización la valida el usuario** (humano o agente autónomo de mayor jerarquía dueño del proceso). Decile al usuario:

> *"Reporte en `docs/specs/<feat>/review.md`: <X> bloqueantes, <Y> opcionales. Tu trabajo: leé el reporte (no el diff completo) y validá la priorización. Para cada bloqueante: ¿genuinamente bloqueante o hay contexto que el reviewer no tiene? Para cada opcional: ¿aplicar o descartar? Cuando termines, pasame las decisiones."*

**Cuando el usuario ES un agente autónomo de mayor jerarquía** (dueño del
proceso que orquesta este ciclo, p.ej. desde un proceso orquestador externo), valida
directamente — no hay ceremonia de delegación explícita que cumplir: es el
dueño. PERO la matriz de severidad de abajo es innegociable: **riesgo de
seguridad y bug funcional son bloqueantes sin excepciones**, aunque el que
valida sea un agente — la delegación da autoridad para *priorizar*, no para
bajar la severidad de lo que la matriz marca como innegociable. Y ante la
duda, se pide al usuario igual (no se baja severidad por ser agente).

### Excepción: delegación explícita a agente experto

Igual que en Etapa 2 (ver `stage-2-specification.md`, "Excepción: delegación explícita a agente experto"), esto solo aplica si el usuario, **para esta feature o etapa puntual**, pidió explícitamente que un agente valide la priorización en su lugar. No se asume, no se activa por defecto, no la iniciás vos.

Con el pedido explícito, antes de validar corré la autoevaluación: ¿tenés contexto de cliente/producto que te falta para juzgar si un bloqueante es genuino? ¿hay algo en el reporte que preferís que vea el usuario (seguridad, breaking change, algo que afecta a un cliente final)? Notá que la matriz de severidad de abajo ya trata **riesgo de seguridad y bug funcional como bloqueante sin excepciones** — eso no lo cambia la delegación; la delegación te da autoridad para *priorizar*, no para bajar la severidad de algo que la matriz marca como innegociable.

Si tenés dudas: no validás vos, pedís al usuario igual. Si validás: marcá en `review.md` y en `stage_history` que la priorización fue agente-delegada, con quién la pidió y cuándo — mismo estándar de trazabilidad que en Etapa 2.

### Cuando el usuario vuelve con priorización

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

Si el usuario marcó como "no bloqueante" algo que la matriz dice bloqueante (ej. divergencia del spec), preguntale el motivo y registralo en `review.md` como nota.

Si detectás sesgo (usuario queriendo cerrar rápido, marcando bloqueantes como opcionales sistemáticamente):

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
