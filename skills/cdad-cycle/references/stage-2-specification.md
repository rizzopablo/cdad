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
- **Compleja** (múltiples componentes): el architect produce además `plan.md` siguiendo la sección "Planning de features complejas" (abajo).

Decidilo con el usuario al inicio de la etapa.

## Por qué la claridad del spec no es negociable

Etapa 3 usa tests de contrato, no cobertura exhaustiva (ver "Convención de tests" en `stage-3-tdd.md`). Eso significa que la precisión que normalmente aportaría una suite exhaustiva tiene que venir del spec. Una postcondición vaga ("el sistema debe manejar bien los errores") no se puede convertir en un test de contrato verificable — el test-writer termina interpretando, y esa interpretación puede no ser la que el usuario necesitaba (AP-13, Garbage Cascade). Cada postcondición tiene que poder responder: *¿qué efecto observable, exactamente, confirma que esto se cumplió?*

## Planning de features complejas

Disparador: el spec es complejo (múltiples componentes). El architect produce `plan.md` además del spec, antes de cerrar Etapa 2. El plan se aprueba con el spec — un solo acto del usuario — y el gate 2→3 incluye el plan aprobado cuando existe.

### Tamaño de tarea

La tarea es la unidad más chica que cierra en su propio mini-ciclo TDD (RED→GREEN propio) y que un reviewer podría rechazar sin rechazar la vecina. Setup, configuración y scaffolding se pliega en la tarea que los necesita — nunca una tarea "de setup" suelta. Ni tan chica que fragmente el review, ni tan grande que no se pueda rechazar una parte sin arrastrar el resto.

### Estructura de tarea

Cada tarea del plan declara:

- **Files**: paths exactos, marcados Create / Modify / Test.
- **Consumes / Produces**: el contrato público — firmas exactas de lo que esta tarea recibe de las anteriores y de lo que expone a las siguientes. El implementer de una tarea solo ve su tarea; por eso las firmas tienen que estar acá, y ser apto para test-writer (el contrato, no el cuerpo).
- **Pasos TDD**: el loop rojo→verde de la tarea, con el test primero.

### La regla central: el plan define el CONTRATO, no el código

*El plan define el CONTRATO — tests con aserciones reales, comandos exactos, comportamiento observable (3-5 bullets verificables contra el test) — y NUNCA código de implementación especulativo.* Escribir la implementación dos veces (en el plan y en la ejecución) revierte TDD y hornea supuestos que el planner adivina pero el implementer no verificó. El comportamiento específico de una tarea es el DELTA respecto al análogo existente en el repo: si hay que enumerar más de 3-5 bullets de comportamiento, ya se está re-derivando la implementación en markdown — cortar y dividir la tarea.

Consecuencia para el aislamiento del test-writer: como el plan no contiene implementación, el test-writer puede ver el plan entero sin violar su restricción. El plan es la interface, no el código.

### No placeholders

Estas frases en un plan son falla del plan:

- "TBD", "TODO", "implementar después".
- "manejar edge cases apropiadamente" (y toda variante de manejo vago).
- "similar a la Tarea N" — repetir el código de otra tarea; si es análogo, nombrá el análogo y describí el delta.
- Pasos que describen QUÉ hacer sin mostrar el CÓMO verificarlo.
- Referencias a tipos o firmas que no están definidas en ninguna tarea.

Matiz: una vagueza CON contrato de comportamiento no es placeholder. El patrón prohibido es vagueza sin contrato — si el bullet observable está, la impl puede decidir detalles internos.

### Auto-revisión (la corre el architect antes de cerrar Etapa 2)

1. **Cobertura del spec**: cada postcondición → al menos 1 tarea (≥1 tarea). Si una postcondición no tiene tarea, el plan está incompleto; si una tarea no mapea a ninguna postcondición, sobra.
2. **Escaneo de placeholders**: buscar las frases prohibidas de arriba en todo el plan.
3. **Consistencia de firmas entre tareas**: una función llamada `clearLayers` en la tarea 2 y `clearFullLayers` en la tarea 5 es un bug del plan — corregirlo acá, no en GREEN.

### Global constraints

Las restricciones proyecto-wide del spec (versiones, naming, plataforma, etc.) se copian verbatim en el header del plan. Toda tarea las incluye implícitamente — ninguna tarea puede contradecirlas ni re-interpretarlas.

## 🛑 Gate de salida (Etapa 2 → Etapa 3)

- [ ] `docs/specs/<NNN-feature-id>/spec.md` existe.
- [ ] Cuatro secciones mínimas presentes y no son placeholders.
- [ ] Postcondiciones numeradas y verificables.
- [ ] Criterios de aceptación medibles.
- [ ] Marca de aprobación del usuario inequívoca.
- [ ] Si el spec es complejo (múltiples componentes): `plan.md` existe, pasó la auto-revisión y está aprobado junto con el spec.

Cuando todos OK: actualizá state file (`current_stage: tdd`, `tdd_substage: red`, `active_feature: <feat-id>`, registrá `approved_by` en `stage_history`). Anunciá transición. Emití handoff a test-writer (RED) para postcondición 1.

## Si surge algo no contemplado en spec durante implementación

Regla: NO se agrega silenciosamente al código. Volvés a Etapa 2: actualizar spec, commitear el cambio (`docs: update spec — add postcondition X`), reaprobar. Recién entonces el implementer puede tocar el caso.

## Anti-patrones

- **AP-5**: saltar el spec porque "es simple". Mínimo: un párrafo + test que falla, con aprobación.
- **AP-6**: spec aprobado en silencio sin marca explícita. Sin marca, no avanzás.
- **AP-10**: delegar la aprobación al LLM. Indelegable.
