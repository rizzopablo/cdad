# Re-entry — validar resultado de un rol que terminó

Cuando el usuario vuelve al chat del orquestador con resultado de un rol (formato típico: *"Listo, acá el commit / diff / archivo"*), aplicás las validaciones del rol correspondiente antes de avanzar.

## Protocolo general de re-entry

1. **Identificá qué rol terminó** (por contexto del state file y de lo que el usuario te pasa).
2. **Aplicá las validaciones de ese rol** (secciones específicas más abajo).
3. **Si validación pasa**: actualizá state file, anunciá la transición o sub-fase nueva, generá el siguiente handoff packet (o cerrá la etapa).
4. **Si validación falla**: NO avances. Decile específicamente qué falta y proponé re-trabajo (típicamente: handoff de vuelta al mismo rol con instrucciones de fix).

---

## Validaciones por rol

### Architect — descubrimiento por feature

Verificá:
- [ ] El output cubre los archivos / hooks / métodos relevantes a la feature.
- [ ] Cada afirmación tiene referencia a archivo real (no inventos).
- [ ] Verificaciones pendientes están explícitamente listadas, no escondidas.

Si falla: pedile al usuario que vuelva al architect con el ítem específico que falta.

Si pasa: agregá el output al spec en la sección "Contexto técnico" (en el draft que va a Etapa 2). Avanzá a brainstorm socrático.

### Architect — brainstorm

Verificá:
- [ ] Hay decisiones explícitas en categorías clave (inputs, outputs, errores, casos de borde, out of scope).
- [ ] El usuario tomó las decisiones, no el architect (el architect preguntó).

Si falla (ej. queda categoría sin tocar): nuevo turno del architect con preguntas faltantes.

Si pasa: handoff a architect modo redacción de spec.

### Architect — draft de spec

Verificá:
- [ ] Existe `docs/specs/<NNN-feature-id>/spec.md`.
- [ ] Cuatro secciones obligatorias: Descripción funcional, Contrato (firma + postcondiciones numeradas), Invariantes verificables, Criterios de aceptación.
- [ ] Postcondiciones numeradas y verificables.
- [ ] Criterios medibles.
- [ ] Sin marca de aprobación (correcto: se aprueba después).

Si falla: handoff de vuelta al architect con la sección que falta.

Si pasa: pasás el spec al usuario (humano o agente autónomo de mayor jerarquía) para aprobación. **NO aprobás vos**. Decile:

> *"Spec en `docs/specs/<NNN>/spec.md`. Antes de avanzar a Etapa 3: revisalo y agregá la marca de aprobación al final (`Status: Approved by <vos> on <fecha>`) o en frontmatter (`approved_by` + `approved_at`). Cuando esté aprobado, avisame."*

Cuando el usuario confirma aprobación: actualizá state file con `current_stage: tdd`, registrá `approved_by` en stage_history, y emití handoff a test-writer (RED) para postcondición 1.

### Test-writer — RED

Verificá:
- [ ] Existe nuevo archivo o diff en `tests/`.
- [ ] El usuario pegó output del run mostrando el test falla.
- [ ] El test falla por **AssertionError u equivalente**, NO por ImportError, syntax error, o módulo no encontrado.
- [ ] Existe commit con prefijo `test:` (no mezclado con feat).

Si falla por razón equivocada (ImportError, etc.): handoff de vuelta al test-writer.

> *"El test falla con `<error específico>`, que NO es un assertion failure. Eso significa que el test no llega a ejercitar la postcondición. Posibles causas: módulo no existe todavía / firma mal escrita en el test / fixture mal armado. Volvé al test-writer con esta info."*

Si pasa: actualizá `postconditions_status: { "<N>": "red" }` y `tdd_substage: "green"`. Emití handoff a implementer.

### Implementer — GREEN

Verificá:
- [ ] El usuario pegó output de la suite **completa**, no solo el test nuevo.
- [ ] Toda la suite verde, incluyendo tests previos.
- [ ] Existe commit con prefijo `feat:`.
- [ ] El implementer NO modificó `tests/` (verificá con `git diff --stat <base>..HEAD -- tests/` si tenés acceso, o pidiéndolo al usuario).

Si modificó tests: AP-4 (implementer modifica tests). Decile:

> *"AP-4 detectado: el implementer tocó tests. Revertí los cambios en tests/. Si el test genuinamente estaba mal, eso es trabajo del test-writer, no del implementer. ¿Reverteamos y volvemos al test-writer con el problema, o el cambio del test era cosmético (ej. nombre)?"*

Si suite no está toda verde: handoff de vuelta al implementer con info del fallo.

Si pasa: actualizá `postconditions_status: { "<N>": "green" }`. Preguntá al usuario:

> *"Postcondición <N> verde. ¿Querés un REFACTOR ahora (si ves fricción evidente) o saltamos a la próxima postcondición / sub-fase?"*

Según respuesta: handoff a refactorer, o handoff a test-writer para postcondición N+1, o (si todas las postcondiciones están verdes) handoff a sub-fase properties / E2E si el spec lo pide.

### Refactorer

Verificá:
- [ ] Suite sigue verde tras el refactor.
- [ ] El refactorer NO modificó `tests/`.
- [ ] Commit con prefijo `refactor:`.

Si suite roja: AP-11. Pedí revertir.

> *"AP-11: refactor rompió tests. Refactor no cambia comportamiento observable. O el cambio era funcional (eso requiere actualizar spec primero), o los tests estaban mal (volver al test-writer). ¿Cuál de los dos?"*

Si pasa: state file no cambia (sigue green en la postcondición). Avanzás a próxima postcondición o sub-fase.

### Test-writer — Properties

Verificá:
- [ ] Property tests existen y corren con seed fijo.
- [ ] El usuario pegó output mostrando properties verdes con volumen razonable (≥100 inputs).
- [ ] Commit con prefijo `test:`.

Si una property falla con un input específico: ese input es un bug. Handoff a implementer con el input contraejemplo.

Si pasa: actualizá `tdd_substage: "integration"` (o `"review-pending"` si el spec no marca E2E). Avanzás.

### Test-writer — E2E

Verificá:
- [ ] Tests E2E existen, llaman vía API pública.
- [ ] Setup con fixtures completas.
- [ ] Asserts derivados de criterios de aceptación del spec.
- [ ] Estado: verde si modalidad B (cierre), rojo esperado si modalidad A (outside-in) hasta que las piezas se conecten.

Si modalidad B y E2E rojo: hay problema de ensamblaje. Handoff a implementer.

Si pasa: actualizá `tdd_substage: "review-pending"`. Anunciá al usuario que Etapa 3 cierra y proponé pasar a Review.

### Reviewer

Verificá:
- [ ] Existe `docs/specs/<feat>/review.md`.
- [ ] Estructura: secciones "Bloqueantes" y "Opcionales", cada hallazgo con ubicación + problema + sugerencia.
- [ ] Cada hallazgo tiene severidad explícita.

Si pasa: pasás el reporte al usuario para validar priorización.

> *"Reporte en docs/specs/<feat>/review.md: <X> bloqueantes, <Y> opcionales. Tu trabajo (capa 2): leé el reporte (no el diff completo) y validá si la priorización es correcta. Para cada bloqueante: ¿genuinamente bloqueante o hay contexto que el reviewer no tiene? Para cada opcional: ¿aplicar ahora o descartar?"*

Cuando el usuario vuelve con su priorización:
- Registrá las decisiones en el review.md (notas con motivo de cada desestimación).
- Si hay bloqueantes a aplicar: handoff a implementer con la lista de fixes.
- Si todos bloqueantes resueltos / desestimados: actualizá state file → `current_stage: merge` y emití handoff a scribe.

### Scribe

Verificá:
- [ ] Tres drafts presentes: activeContext entry, progress changes, ADR draft (o "sin ADR sugerido").
- [ ] Drafts NO están commiteados (correcto).
- [ ] El draft de ADR (si existe) tiene "Confianza" declarada.

Si pasa: pasás los drafts al usuario.

> *"Scribe terminó. Tres drafts para tu revisión:*
>
> *1. activeContext.md entry: <pegar>*
> *2. progress.md changes: <pegar>*
> *3. ADR: <pegar o "sin ADR sugerido", confianza <X>>*
>
> *Editá lo que el scribe entendió mal o no podía saber. Cuando estés conforme, commiteá vos con prefijo `docs(memory):`. Avisame cuando esté commiteado."*

Cuando el usuario confirma commit: validá CI completo (gate 5→done). Si CI verde y Memory Bank actualizado, cerrá feature.

---

## Cuándo NO avanzar

Si el output del rol no cumple el formato esperado, o falta info crítica (ej. test-writer no pegó output del run), pedí lo que falta antes de validar.

> *"Para validar el RED de la postcondición <N>, necesito el output del run que muestra el assertion error. ¿Podés pegármelo?"*

No asumís verde. No asumís correcto. La verificación es empírica.

---

## Actualización del state file

Cada validación exitosa lleva a una actualización del state file. Avisale al usuario en una línea:

> *"State actualizado: `postconditions_status: {"3": "green"}`, `tdd_substage: "refactor-or-next"`. <Próximo paso>."*

Esto da trazabilidad de cada transición.
