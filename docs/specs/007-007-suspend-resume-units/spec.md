<!-- materializado de cdad-architect ses_e8adeb3e4ffexoEIxZycZVAit3 (excepción de arranque acotada, sin recibo) -->
# 007-007 — Suspender y reanudar unidades

**Estado:** aprobada por el orquestador (HITL delegada; alcance aprobado por el dueño el 2026-10-25) tras review NO APTO → ajustes A1–A5 aplicados en «Ajustes del orquestador».  
**Epic:** `epic-007-reliable-cycle-operation`.

## Descripción y alcance

Permitir interrumpir una unidad en un borde seguro, ejecutar otra y reanudar explícitamente la primera sin perder progreso, identidad ni trazabilidad.

**Una sola unidad en ejecución.** Las suspendidas no pueden despachar, recibir nuevas entregas ni avanzar transiciones. No hay pila ni reanudación automática.

Autorización y excepción de arranque: `docs/planning/handoff-2026-10-24-epic-007.md:63-66`. La excepción termina al desplegar esta feature: suspender 007-004 y abrir 007-006 por el ciclo; su borrador se reentrega mediante paquete.

**Incluido:** estado de suspendidas, operaciones CLI, continuidad, validación de reanudación, orientación y protección de consumidores existentes.

**Excluido:** paralelismo B3/B4, scheduler, cancelación de trabajadores, cambio de epic activo, worktrees automáticos, aprobación de evidencia nueva y reparación automática de contratos o cadenas.

### Descubrimiento

Referencias relativas al repositorio:

- `skills/cdad-cycle/scripts/cdad_packet.py:595-630`: `_validate_idle_coherence` exige equivalencia entre ausencia de feature e `idle`; rechaza paquetes activos en reposo.
- `cdad_packet.py:633-687,743-767`: validadores del estado y binding de ejecución.
- `cdad_packet.py:2035-2100`: vigencia de feature, epic y autoridad; la aprobación específica del contrato corresponde a la validación del request.
- `cdad_packet.py:5676-5725`: `open_unit` exige reposo y publica un nuevo binding.
- `cdad_packet.py:1683-1700`: lock por proyecto.
- `cdad_packet.py:7778-7818,7835-7970`: selección de situación y construcción de `compact-view-v1`.
- `skills/cdad-cycle/scripts/cdad_result.py:592-630`: `receive` permite convergencia de recibos durables antes de exigir paquete activo; esta feature debe proteger también esa ruta.
- `skills/cdad-cycle/assets/state-template.json:1-23`: campos actuales del estado.
- ADR-028:98 y ADR-029:258: exclusión histórica de paralelismo. Esta feature conserva ejecución serial.

## Decisiones

1. **Registro por id, no pila.** Se conserva el binding activo existente y se añade `suspended_units`. Es el incremento serial, no un mapa general de ejecuciones concurrentes.
2. **Estado de unidad separado del estado del proyecto.** La suspensión preserva íntegramente los campos específicos enumerados abajo; no restaura después una copia del estado global.
3. **Continuidad enlazada, no regenerada.** Una cadena existente recibe checkpoints de suspensión y reanudación. Sin cadena no se fabrica una.
4. **Suspensión no es retiro.** Un paquete `prepared` permanece preparado. No se usa `withdraw`, no se marca éxito ni se cierra la unidad.
5. **Recepción suspendida bloqueada.** No se admiten entregas nuevas ni finalizaciones de continuidad mientras la unidad está suspendida, incluso mediante replay o `--late`.
6. **Verificación conservadora.** Reanudar no vuelve vigente evidencia que cambió ni reinterpreta un contrato diferente como aprobado.

## Modelo de estado

Campo aditivo:

```json
"suspended_units": {
  "FEATURE_ID": {
    "feature_id": "FEATURE_ID",
    "epic_id": "EPIC_ID",
    "suspended_at": "ISO-8601",
    "reason": "Motivo",
    "unit_state": {},
    "resume_checks": {}
  }
}
```

Ausencia de `suspended_units` equivale a `{}`. Un valor presente mal formado es incoherencia, no ausencia.

### Estado preservado

`unit_state` conserva **valor y presencia/ausencia original** de:

- `active_feature`;
- `current_stage`;
- `tdd_substage`;
- `postconditions_status`;
- `audit_status`;
- `review_status`;
- `active_packet`;
- `execution`.

La presencia se representa mediante los miembros existentes de `unit_state`: no se convierte un campo ausente en `null`.

Éste es el inventario normativo del estado específico actual. Todo campo futuro específico de unidad debe incorporarse al mismo inventario canónico utilizado para preservar, limpiar y restaurar; no se mantienen listas divergentes por operación.

No se archivan ni restauran como estado privado de unidad: `stage_history`, `epic_history`, `epic_features`, autoridad, política, aprobador global, versión y metadatos del proyecto.

`resume_checks` conserva referencias relativas seguras y SHA-256 de:

- contexto de ejecución existente;
- request y paquete seleccionados, si existen;
- contrato que respalda ese paquete; sin paquete, contrato seleccionado por la ejecución;
- evidencias declaradas `vigente` en la cabeza de continuidad;
- recibo durable del paquete seleccionado, cuando exista.

Se reutilizan las formas de referencia y digest existentes. No se hashea indiscriminadamente el árbol git ni se introduce un segundo registro de evidencias.

### Coherencia

- Una feature no puede ser activa y suspendida.
- Cada clave coincide con `feature_id`, `unit_state.active_feature` y la identidad de ejecución.
- Cada suspendida pertenece al epic activo y figura exactamente una vez en `epic_features`, con `status: "suspended"`.
- Suspendidas distintas no comparten ejecución ni paquete seleccionado.
- Los bindings archivados pueden contener un paquete `prepared`; no se interpretan como paquete activo global.
- `active_feature: null` y `current_stage: "idle"` siguen siendo reposo legítimo aunque haya suspendidas.

Al suspender se limpian los campos específicos activos: feature, ejecución y paquete a `null`; etapa a `idle`; subfase, auditoría y review a `null`; postcondiciones a `{}`.

## Contrato CLI

Los verbos pertenecen a `scripts/cdad_packet.py`, ejecutado desde la instalación vigente.

```sh
python3 <packet> suspend-unit --project-root ROOT \
  --feature ID --reason "Motivo no vacío"

python3 <packet> resume-unit --project-root ROOT --feature ID
```

`--feature` es obligatorio en ambos verbos. No hay selección por directorio reciente, orden de suspensión ni única candidata.

**Códigos:** `0` éxito; `2` rechazo de entrada, coherencia, vigencia, seguridad o lock ocupado. Los diagnósticos nombran unidad, fuente del bloqueo y acción necesaria; no imprimen éxito ante un bloqueo.

### Suspender

Bajo el lock del proyecto:

1. Verificar que ID es la unidad activa, abierta, con contexto v2 y bindings coherentes.
2. Verificar el borde seguro.
3. Preservar estado y referencias de reanudación.
4. Añadir checkpoint cuando corresponda.
5. Cambiar `epic_features[ID].status` a `suspended`, añadir historial y publicar reposo.

**Borde seguro:**

- Sin paquete seleccionado: no hay trabajo pendiente irresuelto de esa ejecución.
- `prepared`: ausencia verificable de despacho, resultados, materializaciones y disposiciones incompatibles con ese estado.
- `dispatched`: rechazo; primero recibir o disponer por las rutas existentes.
- Terminal: su resolución es demostrable mediante recibo/disposición existente y no quedan intentos irresueltos.
- Señales ilegibles, discordantes o inconclusas: rechazo.

No basta con comprobar `active_packet.status`. El examen alcanza los intentos pendientes de la ejecución, para no esconder un trabajador anterior mediante otro paquete.

Suspender no exige suite verde: RED es un borde válido si su entrega está recibida y no hay despacho pendiente.

### Reanudar

Exige reposo legítimo, sin otra unidad activa ni trabajo activo irresuelto, y un registro suspendido de ID.

Construye una vista candidata restaurando `unit_state`, **sin publicarla**, y verifica:

- identidades y binding contra el contexto existente;
- epic y autoridad actualmente vigentes;
- política aceptada y coherencia de versión mediante los controles existentes;
- integridad de referencias y digests de `resume_checks`;
- validación y aprobación aplicables al paquete conservado, incluido el contrato pineado;
- cadena y evidencia vigente de continuidad.

La comparación del contrato vivo de unidad conserva las reglas existentes: un impacto de planificación no invalida retrospectivamente el contrato recibido; debe estar reconciliado mediante la decisión existente antes de reanudar. No se sustituye el digest del contrato publicado por uno nuevo.

Una referencia ausente o alterada bloquea sin efectos. Restaurar el antecedente o reconciliarlo requiere los procedimientos existentes; este verbo no aprueba sustituciones ni dispone de una opción de omisión.

Tras validación, añade checkpoint cuando corresponda, restaura los campos específicos, elimina únicamente `suspended_units[ID]`, cambia su entrada a `in-progress` y añade historial. Conserva `opened_at`.

### Continuidad y publicación

Con cabeza existente:

- Verificar la cadena antes de modificarla.
- Anexar `checkpoint` enlazado con `prev`; conservar identidad, autoridad, paquete, intento y antecedentes.
- Suspensión: decisión con motivo y siguiente acción «no despachar; reanudar explícitamente ID».
- Reanudación: decisión de reanudación y siguiente acción conservada del progreso anterior a suspender.
- No crear `begin`, recibo, `receipt_checkpoint` ni una nueva ejecución.
- Una cadena ilegible, no demostrable o discordante bloquea.

Sin cabeza, no crear cadena ficticia.

Estado, historial y avance de cabeza forman una publicación transaccional bajo el lock existente: rollback ante fallo; recuperación de transacción interrumpida antes de aceptar otra mutación. Ningún estado recuperado puede mostrar simultáneamente unidad activa y suspendida.

Una repetición de `suspend-unit` sobre ID ya suspendida, o de `resume-unit` sobre ID ya activa, devuelve `2` sin escrituras. No genera nuevos checkpoints.

## Interacción con operaciones existentes

- `open-unit` admite reposo con suspendidas, conserva el registro y abre sólo una unidad `queued` elegible. No reabre una suspendida ni ignora dependencias incompletas.
- `prepare` sólo opera sobre la unidad activa; nunca selecciona una suspendida.
- `register-transition` rechaza transiciones dirigidas a unidades o paquetes suspendidos, incluidos replay, cierre, disposición y retiro.
- `receive` comprueba suspensión **antes** de cualquier finalización o actualización de continuidad. Rechaza nuevas entregas y replay durable, también con `--late`, indicando `resume-unit --feature ID`.
- Lectura y validación de recibos ya existentes siguen permitidas; rechazo de `receive` no invalida esos recibos.
- Despacho, `begin`, checkpoint operativo, materialización y mutaciones de ejecución deben aplicar la misma prohibición de avance sobre unidades suspendidas. Lecturas de diagnóstico y `resume` de continuidad pueden mostrar antecedentes, pero no habilitan ejecución.
- No se amplían autoridad ni criterios de aprobación.

## Vista compacta

Se conserva `compact-view-v1` y todos sus campos existentes. Extensión aditiva:

```json
"suspended_units": [
  {
    "feature_id": "ID",
    "suspended_at": "ISO-8601",
    "reason": "Motivo",
    "stage": "tdd",
    "substage": "red"
  }
]
```

Orden determinista por `feature_id`. Sin suspendidas: `[]`.

Con activa, la precedencia de situaciones y `next.operation` existente no cambia.

Sin activa y con suspendidas coherentes:

- `situation: "units-suspended"`;
- se conservan las claves existentes de `next.operation`;
- `verb: "select-unit"`, como instrucción de selección, **no como nuevo comando CLI**;
- `script` identifica `cdad_packet.py`;
- `procedure` referencia el procedimiento canónico;
- `source: "docs/.cdad-state.json:suspended_units"`;
- campo aditivo `next.alternatives`: `resume-unit` con selección obligatoria de ID y `open-unit` si existen unidades elegibles.

No elige una suspendida ni abre automáticamente otra unidad. Si no existen unidades elegibles, no ofrece apertura como acción disponible. Incoherencia conserva prioridad de diagnóstico.

Los directorios pendientes de una ejecución suspendida no convierten otra unidad activa ni el reposo en `pending-work-unresolved`.

## Invariantes

- **I1:** como máximo una unidad ejecutable.
- **I2:** suspensión no equivale a entrega, fallo, aprobación, retiro o cierre.
- **I3:** restauración íntegra del estado específico, sin restaurar estado global obsoleto.
- **I4:** ejecuciones, requests, paquetes, recibos y ancestros permanecen conservados.
- **I5:** inconcluso nunca significa ausencia ni evidencia vigente.
- **I6:** todas las mutaciones respetan escritor único y lock del proyecto.
- **I7:** ningún consumidor permite avanzar una suspendida.
- **I8:** selección explícita; ni pila ni selección temporal implícita.

No se requiere subfase adicional de propiedades: las invariantes tienen verificaciones conductuales directas.

## Postcondiciones y verificación

Tests CLI en subprocesos, con fixtures reales; nombres estables:

| PC | Test | Resultado observable |
|---|---|---|
| PC-01 | `test_suspend_preserves_complete_unit_state_and_enters_idle` | Preserva valores y ausencias, registra motivo, limpia binding activo y marca `suspended`. |
| PC-02 | `test_suspend_prepared_packet_preserves_packet_and_execution` | Paquete preparado sin efectos permanece preparado; contexto, paquete y ancestros conservan bytes. |
| PC-03 | `test_suspend_rejects_unresolved_dispatch_and_inconclusive_effects` | Despacho pendiente o señales ilegibles/discordantes: rc 2, fuente indicada, sin cambios. |
| PC-04 | `test_suspend_received_red_unit_accepts_safe_boundary` | RED recibido permite suspensión sin exigir GREEN ni cierre. |
| PC-05 | `test_suspend_resume_append_linked_checkpoints_without_new_execution` | Checkpoints enlazados y decisiones verificables; identidad y antecedentes conservados; sin recibos nuevos. |
| PC-06 | `test_suspend_resume_handle_absent_and_invalid_continuity` | Sin cabeza no inventa cadena; cadena inválida bloquea sin cambios. |
| PC-07 | `test_resume_requires_explicit_selection_and_no_active_unit` | ID ausente, desconocido u otra unidad activa: rc 2 sin cambios. |
| PC-08 | `test_resume_restores_unit_state_without_rolling_back_project_history` | Restaura estado y presencias exactas; conserva avances globales y de otras unidades. |
| PC-09 | `test_resume_rejects_invalid_authority_contract_policy_or_evidence` | Autoridad revocada, digest alterado, política incoherente o evidencia ausente: rechazo íntegro. |
| PC-10 | `test_open_unit_preserves_suspended_registry_and_dependencies` | Apertura desde reposo con suspendidas conserva registros; no abre suspendidas ni dependencias incumplidas. |
| PC-11 | `test_suspended_units_cannot_advance_through_existing_consumers` | Prepare, transición, despacho, continuidad mutante y materialización no avanzan suspendidas. |
| PC-12 | `test_receive_rejects_suspended_unit_including_replay_and_late` | Recepción normal, durable y late rechazadas antes de escrituras; validación de recibo existente sigue disponible. |
| PC-13 | `test_status_adds_suspended_summary_and_requires_selection` | Forma previa conservada; resumen determinista; alternativa explícita sin selección automática; activa mantiene precedencia. |
| PC-14 | `test_suspension_registry_incoherence_is_diagnosed_without_fallback` | Duplicidad, identidad/binding discordante o estructura inválida producen diagnóstico, sin inferencias. |
| PC-15 | `test_suspend_resume_publication_failure_preserves_consistent_state` | Fallo real de filesystem e interrupción controlada no dejan estado/cabeza parcialmente publicados tras recuperación. |
| PC-16 | `test_suspend_resume_lock_and_repetition_have_no_extra_effects` | Lock ocupado y repetición rechazan sin entradas ni checkpoints extra. |
| PC-17 | `test_received_red_unit_can_suspend_open_another_and_resume_to_verified_begin` | Flujo 007-004-like completo, descrito abajo, sin pérdida ni repetición de efectos. |

### Fixtures y recorrido integrado

Construir política aceptada, contexto v2, epic y contratos aprobados, agentes derivados y paquetes mediante sus rutas públicas. Producir `begin`, despacho, recepción y disposiciones mediante las CLI correspondientes.

PC-17:

1. Unidad A en RED con entrega recibida, postcondiciones y estados de auditoría/review identificables.
2. Suspender A.
3. Abrir B y realizar trabajo trazable.
4. Variantes: cerrar B mediante cierre legítimo, o suspender B en borde seguro.
5. Reanudar explícitamente A.
6. Comprobar restauración, historial global conservado y mismos ids/contextos.
7. Continuar `prepare → begin → verify-begin` con contrato autorizado, sin repetir el despacho recibido.

Comparar inventario y bytes antes/después de rechazos. Provocar corrupción y fallos de escritura mediante condiciones reales, no mocks de funciones internas.

## Documentación a alinear

Por referencia, sin duplicar reglas:

- `assets/state-template.json` y esquemas afectados: registro y estado `suspended`.
- `references/state-detection.md`: reposo con suspendidas.
- `references/project-execution.md`: operaciones y prohibición de avance.
- `references/continuity.md`: checkpoints y verificación de reanudación.
- `references/orientation.md`: `units-suspended` y selección explícita.
- `references/re-entry.md`: recepción bloqueada mientras está suspendida.
- `sources/roles/orchestrator.md`: procedimiento canónico.
- `skills/cdad-epic/SKILL.md`: `epic_features`, dependencias y selección.
- Spec 007-001: extensión aditiva referenciada.
- Spec 007-006: suspensión distinta de retiro; no cambia su objetivo.
- Plan epic-007, handoff y Memory Bank: incorporación y fin de la excepción.

## Criterio de aceptación

PC-01…PC-17 verificadas; regresión proporcional y suite completa al cierre, distinguiendo RED ajeno preexistente; revisión independiente y aprobación del dueño.

Tras despliegue autorizado: suspender realmente 007-004, abrir 007-006 dentro del ciclo y demostrar posteriormente la reanudación de 007-004 sin perder identidad ni repetir efectos. La prueba controlada no sustituye esta evidencia de uso real.

## Ajustes del orquestador (review 2026-10-25)

**A1 — Prerrequisito de incorporación (bloqueante resuelto).** El plan del epic se enmendó (sección «Cambios al plan», 2026-10-25) con las altas de 007-006 y 007-007, y el orquestador sincronizó `epic_features` según `skills/cdad-epic/references/epic-planning.md` (coordinador propone, orquestador escribe): 007-006 `queued` con `depends_on: [007-007]`, 007-007 `queued`. `open-unit` no hace altas implícitas. Aceptación real: sobre el estado real, `suspend-unit 007-004 → open-unit --feature 007-006` sin edición reparadora.

**A2 — Matriz de entradas mutantes.** Antes del primer efecto, cada entrada resuelve la unidad desde su propia identidad (paquete/request/ejecución) y rechaza si pertenece a una unidad suspendida: `prepare`, `register-transition` (todas las transiciones), `cdad_dispatch.py dispatch` y `record` (con y sin continuidad), `cdad_continuity.py begin`, `checkpoint`, `checkpoint-receipt` (directo y desde `receive`), `reanchor` (prohibido mientras la unidad está suspendida), `cdad_result.py receive` (incluidos replay durable y `--late`, comprobado antes del retorno temprano) y la materialización por recibo/autorización. Lecturas (`status`, `verify-begin`, `reconcile`, `resume`, `validate-*`) siguen permitidas y no habilitan avance. Estas variantes se prueban parametrizadas dentro de la PC de prohibición de mutaciones.

**A3 — Tres niveles de validación.** (1) Coherencia global del reposo y del registro de suspendidas (`validate-state` sin contexto). (2) Validación contextual de la candidata restaurada dentro de `resume-unit`, sin publicarla. (3) Los consumidores mutantes nunca reciben la candidata como autorización. `validate-state --execution-context` de una unidad suspendida responde con rechazo explícito «unidad suspendida: reanudar con `resume-unit --feature ID`», sin relajar la comprobación de feature activa.

**A4 — Ampliación de dominio de compact-view.** Se amplían normativamente los dominios cerrados de 007-001: `situation` admite `units-suspended`; `next.operation.verb` admite `select-unit`. `procedure` = `references/orientation.md`. `next.alternatives` = lista de objetos `{verb, script, args_required}` con `verb ∈ {resume-unit, open-unit}`, `script` = `scripts/cdad_packet.py`, `args_required` = `["--feature"]` para `resume-unit` y `[]` u `["--feature"]` para `open-unit`. Sin suspendidas, la proyección es idéntica a la anterior más `suspended_units: []`; el test de compatibilidad de 007-001 descuenta sólo los campos nuevos.

**A5 — Postcondiciones consolidadas (10).** Normativas por contenido; los nombres de test son orientativos y las variantes van parametrizadas:
1. Estado y restauración íntegros (PC-01+08). 2. Bordes seguros (02+03+04). 3. Continuidad (05+06). 4. Selección explícita y exclusión de activa (07). 5. Vigencia (09). 6. Apertura y dependencias (10). 7. Prohibición de mutaciones, matriz A2 (11+12). 8. Orientación y coherencia del registro, A3/A4 (13+14). 9. Publicación, lock y repetición (15+16). 10. Recorrido integrado (17).

**Nota de aceptación real.** El estado actual de 007-004 tiene discrepancias previas (`current_stage: discovery` con entregas RED, `review_status` heredado de 005-014). Suspender/reanudar las conserva fielmente; no son su reparación.
