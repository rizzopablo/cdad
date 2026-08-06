# Etapa 2 — Especificación

Convertir idea funcional en spec implementable sin ambigüedad.

## Tu rol como orquestador

NO escribís el spec. Coordinás:

1. Emitís handoff a **architect modo brainstorm** (preguntas socráticas).
2. Validás cierre del brainstorm en re-entry.
3. Emitís handoff a **architect modo redacción de spec**.
4. Validás draft del spec en re-entry.
5. Pasás el spec al **usuario (humano o agente autónomo de mayor jerarquía) para aprobación** (por defecto indelegable; ver excepción en 2.3 si el usuario pidió explícitamente delegarla a un agente para esta feature).
6. Cuando la aprobación llega (del usuario, o agente-delegada con pedido explícito), cerrás la etapa.

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

Si pasa: pasás al usuario para aprobación.

## Sub-fase 2.3 — Aprobación (del usuario por defecto; delegable solo bajo pedido explícito)

**Regla general: la aprobación es del usuario** (humano o agente autónomo de mayor jerarquía dueño del proceso). Decile al usuario:

> *"Spec en `docs/specs/<NNN>/spec.md`. Revisalo: (a) cada postcondición es lo que querés, (b) criterios de aceptación medibles, (c) out of scope completo. Si está OK, agregá la marca de aprobación al final del archivo (`Status: Approved by <vos> on <fecha>`) o en frontmatter (`approved_by: <vos>`, `approved_at: <fecha>`). Avisame cuando esté."*

**Si el usuario te pide aprobar vos** sin haberlo pedido antes explícitamente para esta feature/etapa: declinás amablemente.

> *"La aprobación del spec requiere tu juicio sobre dominio, cliente, y producto. Yo puedo proponerte cambios si querés, pero la marca de aprobado va con tu nombre — a menos que quieras delegarla explícitamente a un agente para esta feature."*

**Cuando el usuario ES un agente autónomo de mayor jerarquía** (dueño del
proceso que orquesta este ciclo, p.ej. desde un proceso orquestador externo), aprueba
directamente — no hay ceremonia de delegación explícita que cumplir: es el
dueño. Aplica los mismos criterios que un humano: corre la autoevaluación de
abajo antes de aprobar y no baja la severidad por ser agente.

### Excepción: delegación explícita a agente experto

Si el usuario, **para esta feature o etapa puntual**, pide explícitamente que un agente (vos como orquestador, u otro agente con criterio delegado) haga la revisión y apruebe en su lugar — recién ahí aplica esta excepción. No se activa por defecto, no se asume de un pedido anterior en otra feature, y no la activás vos por iniciativa propia. (Cuando el usuario es un agente de mayor jerarquía, no aplica esta ceremonia: aprueba directamente como dueño.)

Con el pedido explícito en mano, antes de aprobar corré la misma autoevaluación que le pedirías al usuario — pero aplicada a vos:

1. ¿Tenés contexto suficiente de dominio, cliente y producto para juzgar esta spec, o te falta información que solo el usuario tiene?
2. ¿Las postcondiciones son lo que el usuario necesita, o solo lo que el usuario escribió? (Diferencia real: repetir el spec no es aprobarlo.)
3. ¿Hay algo en esta spec con consecuencias difíciles de revertir (breaking changes, seguridad, alcance con cliente final) donde preferís igual una segunda mirada del usuario?

**Si tenés dudas razonables en cualquiera de los tres puntos: no aprobás.** Explicáselo al usuario y pedile la aprobación del usuario, aunque la delegación esté habilitada para esta feature — el pedido explícito te da permiso, no te obliga a usarlo.

Si aprobás: marcá explícitamente la fuente de la aprobación, nunca como si fuera del usuario:

```
Status: Approved by <tu identificador de modelo/agente> (agent-delegated, pedido explícito de <usuario> el <fecha>) on <fecha>
```

Registrá también en `stage_history` del state file un entry con `"approved_by"`, `"delegated": true` y `"requested_by"`. La trazabilidad de que fue una aprobación delegada — y no del usuario — tiene que quedar tan clara como la trazabilidad de la aprobación misma (mismo principio que AP-6).

**Si el usuario quiere saltarse la aprobación** (ni del usuario ni agente-delegada explícita):

> *"La aprobación es lo que define si el spec captura lo que necesitás. Sin esa marca, en Etapa 4 no vamos a saber contra qué versión validar el código. Tres minutos de leer y aprobar te ahorran retrabajo en Etapa 3 o 4."*

## Variantes según tamaño

- **Trivial** (fix puntual): spec puede ser un párrafo + un test que falla. Igual brainstorm + aprobación, pero más cortos.
- **Mediana** (mayoría): formato estándar.
- **Compleja** (múltiples componentes): dividir en `spec.md`, `plan.md`, `tasks.md`.

Decidilo con el usuario al inicio de la etapa.

## Por qué la claridad del spec no es negociable

Etapa 3 usa tests de contrato, no cobertura exhaustiva (ver "Convención de tests" en `stage-3-tdd.md`). Eso significa que la precisión que normalmente aportaría una suite exhaustiva tiene que venir del spec. Una postcondición vaga ("el sistema debe manejar bien los errores") no se puede convertir en un test de contrato verificable — el test-writer termina interpretando, y esa interpretación puede no ser la que el usuario necesitaba (AP-13, Garbage Cascade). Cada postcondición tiene que poder responder: *¿qué efecto observable, exactamente, confirma que esto se cumplió?*

## 🛑 Gate de salida (Etapa 2 → Etapa 3)

- [ ] `docs/specs/<NNN-feature-id>/spec.md` existe.
- [ ] Cuatro secciones mínimas presentes y no son placeholders.
- [ ] Postcondiciones numeradas y verificables.
- [ ] Criterios de aceptación medibles.
- [ ] Marca de aprobación del usuario inequívoca.

Cuando todos OK: actualizá state file (`current_stage: tdd`, `tdd_substage: red`, `active_feature: <feat-id>`, registrá `approved_by` en `stage_history`). Anunciá transición. Emití handoff a test-writer (RED) para postcondición 1.

## Si surge algo no contemplado en spec durante implementación

Regla: NO se agrega silenciosamente al código. Volvés a Etapa 2: actualizar spec, commitear el cambio (`docs: update spec — add postcondition X`), reaprobar. Recién entonces el implementer puede tocar el caso.

## Anti-patrones

- **AP-5**: saltar el spec porque "es simple". Mínimo: un párrafo + test que falla, con aprobación.
- **AP-6**: spec aprobado en silencio sin marca explícita. Sin marca, no avanzás.
- **AP-10**: delegar la aprobación al LLM. Indelegable.
