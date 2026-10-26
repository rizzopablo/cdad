<!-- materializado de cdad-architect ses_e8ae0b6bdffeE9lKjTd2y8drpv (excepción de arranque, sin recibo) -->
# 007-006 — Withdraw de paquetes preparados y republicación independiente

**Estado:** aprobada por el orquestador (HITL delegada; alcance aprobado por el dueño el 2026-10-25) tras review APTO CON AJUSTES; ajustes AJ1–AJ4 aplicados al final del documento.

## Descripción

Resolver dos bloqueos independientes:

1. Retirar explícitamente un paquete activo `prepared` cuya ausencia de despacho y efectos sea verificable.
2. Actualizar los agentes derivados del proyecto sin generar otro paquete.

La autorización y excepción de arranque constan en `docs/planning/handoff-2026-10-24-epic-007.md:58-61`.

### Descubrimiento breve

Referencias relativas al repositorio:

- `skills/cdad-cycle/scripts/cdad_packet.py:7010-7028`: `disposition` ya utiliza `failed` como estado terminal que libera `prepare`, sin declarar éxito.
- `skills/cdad-cycle/scripts/cdad_continuity.py:2127-2166`: el reanclaje comprueba `prepared`, despachos, archivos de resultados, materializaciones y disposiciones; rechaza señales inconclusas.
- `skills/cdad-cycle/scripts/cdad_packet.py:5080-5125`: `prepare` calcula los derivados mediante `_build_derived_payloads` antes de publicar la generación.
- `skills/cdad-cycle/scripts/cdad_packet.py:3936-3986`: esa función deriva desde la instalación resuelta, conserva procedencia y construye el manifiesto.
- `skills/cdad-cycle/scripts/cdad_packet.py:7178-7185`: la resolución actual del DRIFT exclusivo de proyecto depende de otro `prepare`.
- `skills/cdad-cycle/scripts/cdad_packet.py:187-200,7778-7818`: un paquete coherente preparado produce `packet-prepared`, con `validate-packet` como primera operación.
- `skills/cdad-cycle/scripts/cdad_packet.py:3800-3870`: la transformación modifica permisos, no el campo `model:`. **Actualmente la derivación conserva el modelo de la fuente instalada**, no el modelo anterior del derivado local.

El caso 105 es un reporte del orquestador; no se inspeccionó el proyecto externo.

## Alcance

**Incluido:** transición `withdraw`, cierre de continuidad asociado, republicación independiente, resolución de DRIFT y documentación operativa.

**Excluido:** cancelar trabajadores, retirar paquetes despachados, fabricar recibos, aprobar resultados, cerrar features, modificar política, instalar agentes globales, elegir modelos o reparar otras patas de versión.

## Decisiones

1. **Estado terminal existente:** `active_packet.status = "failed"`. La distinción semántica queda en una entrada `transition: "withdraw"`, `resolution: "withdrawn"`. No se introduce otro estado terminal ni se presenta el retiro como fallo de ejecución.
2. **Separar retiro y disposición:** `withdraw` declara que el encargo no llegó a despacharse; `disposition` resuelve un despacho. No se amplía esta última para significados contradictorios.
3. **Ausencia verificable compartida:** extraer o reutilizar el criterio conservador de reanclaje, sin copiar detectores divergentes ni utilizar solamente `_has_dispatch`, que omite JSON ilegible (`cdad_continuity.py:2113-2124`).
4. **Continuidad:** si la cabeza vigente corresponde al paquete retirado, anexar un checkpoint de retiro en la misma operación; nunca borrar ni reescribir el `begin`.
5. **Republicación independiente:** reutilizar el constructor de derivados y las garantías de publicación existentes; no invocar `prepare` ni fabricar un paquete auxiliar.
6. **Orientación sin inferir intención:** mantener `packet-prepared → validate-packet`. Estar preparado no demuestra que el dueño quiera retirar el encargo. El retiro es una alternativa explícita documentada, no una nueva situación.

## Contrato CLI

`<packet>` designa el script instalado `scripts/cdad_packet.py`.

### Retirar

```sh
python3 <packet> register-transition \
  --project-root ROOT \
  --transition withdraw \
  --packet PACKET_ID \
  --note "Motivo no vacío"
```

- Exige identidad coherente entre estado, request publicado y ejecución.
- Exige que el paquete citado sea el activo y esté `prepared`.
- `--note` contiene el motivo obligatorio.
- Etiqueta canónica: `stage: "packet-withdrawal"`.
- Resolución implícita: `resolution: "withdrawn"`; no requiere `--resolution`.
- Rechaza `--stage`, `--resolution`, `--replaced-by`, campos de aprobación, recibo, artefactos, resultado, avance operacional, cierre o supersesión: no pertenecen a este acto.
- Conserva `REQUEST.json`, `PACKET.md`, contexto y demás archivos previos.
- Añade a `stage_history` una entrada con la identidad y clave verificable habituales, paquete, ejecución, feature, motivo y resolución.
- Sólo cambia en el estado: `active_packet.status`, la entrada añadida y `last_updated`.
- No exige coherencia de versión de agentes: precisamente debe funcionar durante DRIFT.
- Repetición idéntica: éxito sin escrituras ni nueva entrada. Un motivo distinto para un retiro ya registrado es conflicto, no otra decisión.

### Continuidad del retiro

Si existe cabeza vigente del mismo paquete:

- La cadena debe ser legible, íntegra y demostrable, sin split-brain.
- Anexar `record: "checkpoint"` conservando paquete, intento, autoridad y contexto previo.
- Incorporar una decisión de retiro que cite la clave de transición y el motivo.
- `next_action` declara que el paquete no debe despacharse y que corresponde preparar un nuevo encargo.
- Conservar el vínculo `prev` y avanzar la secuencia normal.
- No crear recibo ni `receipt_checkpoint`: no hubo entrega.
- Estado y checkpoint se publican con rollback conjunto ante error.

Si no hay cabeza, no crear continuidad ficticia. Si la cabeza vigente pertenece a otro paquete, conservarla; el historial del retiro basta y el estado impide despachar el paquete retirado. Una cabeza existente ilegible o incoherente bloquea el retiro: no se presume que pertenece a otro paquete.

### Republicar

```sh
python3 <packet> republish-agents --project-root ROOT
```

- Utiliza la ejecución v2 vinculada y su política aceptada, verificando su coherencia.
- Admite un paquete activo `prepared`, `dispatched` o terminal: no opera sobre él.
- Resuelve las fuentes mediante la precedencia existente: variable de entorno, registro de instalación y fuente predeterminada (`cdad_packet.py:3540-3546`).
- Reutiliza `_build_derived_payloads`: permisos, temporales aceptados, procedencia, manifiesto, detección de modificaciones locales y retiro de nombres previamente administrados.
- Publica únicamente derivados administrados y manifiesto; conserva archivos ajenos.
- No modifica estado de ciclo, paquetes, política, contexto de ejecución ni continuidad.
- Si los bytes ya coinciden, éxito sin reescritura.
- Sin fuentes instaladas: rechazo explícito; este verbo no debe afirmar republicación cuando no publicó nada.
- Sin contexto v2/política aceptada verificables: rechazo explícito, sin crear contexto ni aceptar política por efecto lateral.
- Conserva exactamente el `model:` instalado, incluida su ausencia. Nunca toma una elección de modelo del manifiesto viejo ni añade una propia.

### Orientación y versión

Sin modificar la forma de `compact-view-v1`:

- Paquete coherente `prepared`, incluso con `begin` vigente y DRIFT: `situation = "packet-prepared"` y `next.operation.verb = "validate-packet"`.
- En DRIFT cuya única pata divergente sea `project`, `resolution` indica `republish-agents --project-root ROOT`, ejecutado mediante el script instalado.
- Otras divergencias no reciben la promesa de quedar reparadas con este verbo.
- Tras retirar, no se selecciona el paquete terminal como pendiente ni se lo propone para despacho. Con ejecución activa y sin otros pendientes, corresponde `execution-active → resume`.

## Rechazos

Toda señal positiva o inconclusa impide `withdraw`, nombrando fuente y causa:

- Despacho registrado del paquete.
- Registro de despacho ilegible, identidad ausente o discordante en el ámbito examinado.
- Cualquier archivo de resultado del paquete, aunque no exista recibo válido.
- Materialización registrada, incluso un registro ilegible.
- Disposición registrada o cuya selección no sea verificable.
- Paquete incorrecto, no activo, identidad discordante o estado distinto de `prepared`.
- Continuidad existente no verificable.
- Motivo ausente o vacío.

Un rechazo no modifica ningún archivo persistente. Los errores de republicación tampoco dejan un conjunto parcial de derivados.

## Invariantes

- **I1:** retiro no equivale a despacho, entrega, aprobación ni cierre.
- **I2:** evidencia histórica y archivos publicados permanecen conservados.
- **I3:** inconcluso nunca se interpreta como ausente.
- **I4:** repetición idéntica no añade efectos.
- **I5:** republicación no cambia ciclo ni paquetes.
- **I6:** el proyecto hereda el modelo instalado; CDAD no lo elige.
- **I7:** no se amplían autoridad ni permisos fuera de la derivación existente.

No se exige una subfase de propiedades adicional; las invariantes tienen verificaciones conductuales directas.

## Postcondiciones y verificación

Tests estables mediante CLI en subprocesos, sin mocks de funciones internas:

| PC | Test | Resultado observable |
|---|---|---|
| PC-01 | `test_withdraw_prepared_packet_preserves_artifacts_and_frees_prepare` | Retiro válido devuelve éxito, conserva bytes del paquete, registra `withdraw/withdrawn`, marca `failed` y permite un nuevo `prepare` sin reemplazo. |
| PC-02 | `test_withdraw_requires_reason_and_matching_active_prepared_packet` | Motivo vacío, identidad discordante, otro paquete o estado no preparado: rechazo sin cambios. |
| PC-03 | `test_withdraw_rejects_effects_and_inconclusive_signals` | Casos parametrizados de despacho, resultado, materialización y disposición, tanto presentes como inconclusos: rechazo con fuente/causa y árbol persistente intacto. |
| PC-04 | `test_withdraw_closes_current_begin_without_fabricating_delivery` | Con `begin` vigente, agrega un checkpoint enlazado con decisión de retiro; preserva ancestros; `resume` muestra retiro y siguiente acción; no crea recibo ni aprobación. |
| PC-05 | `test_withdraw_handles_absent_foreign_and_invalid_continuity` | Sin cabeza no crea una; cabeza válida de otro paquete permanece idéntica; cadena ilegible/incoherente se rechaza sin cambios. |
| PC-06 | `test_withdraw_is_idempotent_and_rejects_conflicting_repetition` | Repetición idéntica no cambia bytes ni historial/cadena; motivo diferente se rechaza. |
| PC-07 | `test_withdraw_rejects_unrelated_transition_flags` | Los campos ajenos enumerados en la interfaz no son ignorados: producen rechazo sin cambios. |
| PC-08 | `test_republish_agents_repairs_project_drift_without_cycle_changes` | Con paquete activo, publica derivados/manifiesto actualizados; estado, paquetes, política y continuidad permanecen idénticos; el verificador deja de informar DRIFT de proyecto cuando las otras patas ya son coherentes. |
| PC-09 | `test_republish_agents_inherits_installed_model_and_is_idempotent` | Modelo instalado personalizado se conserva literalmente; ausencia de modelo permanece ausente; segunda ejecución no reescribe archivos. |
| PC-10 | `test_republish_agents_preserves_existing_derivation_guards` | Fuente/política/contexto inválidos y modificación local protegida producen rechazo sin publicación parcial; archivos ajenos se conservan y sólo se retiran nombres administrados obsoletos. |
| PC-11 | `test_status_preserves_prepared_situation_and_exposes_independent_drift_resolution` | Conserva forma y `packet-prepared/validate-packet`; sólo DRIFT exclusivo de proyecto ofrece `republish-agents`. Tras retiro no propone despachar el paquete. |
| PC-12 | `test_packet_105_prepared_begin_and_project_drift_recovery` | Fixture `F001-003-test-writer-red-105`, preparado + `begin` + DRIFT: republicar funciona sin retirar; retirar funciona con DRIFT; tras ambas operaciones, cadena trazable y nuevo `prepare` exitoso. |
| PC-13 | `test_withdraw_publication_failure_preserves_state_and_continuity` | Fallo de escritura provocado mediante condición real del filesystem devuelve error y conserva conjuntamente estado y cabeza anteriores. |

### Fixtures reales

Construir proyectos temporales con política aceptada, contexto v2, contrato aprobado, request/paquete publicados, manifiesto y agentes con frontmatter válido. Crear `begin` mediante la CLI de continuidad y despacho/materialización/disposición mediante sus rutas públicas cuando sean aplicables.

Las variantes ilegibles se producen alterando archivos de esas mismas formas reales, no mediante estructuras mínimas inventadas. Para DRIFT, utilizar marcadores/manifiestos de versiones distintas y ejecutar el verificador real. La prueba integrada admite ambos órdenes: republicar→retirar y retirar→republicar.

Comparar inventario y bytes antes/después; para idempotencia, verificar también ausencia de reescritura de los destinos.

## Documentación a alinear

- `skills/cdad-cycle/references/project-execution.md`: retiro versus disposición/reemplazo; verbo independiente.
- `skills/cdad-cycle/references/continuity.md`: checkpoint de retiro y ausencia de recibo.
- `skills/cdad-cycle/references/orientation.md`: situación preparada y resolución de DRIFT.
- `skills/cdad-cycle/references/re-entry.md`: retiro no es re-entry ni aprobación.
- `sources/roles/orchestrator.md`: enlazar esos procedimientos desde recuperación; sin duplicar sus reglas.
- Ayuda CLI y contratos de transición afectados.
- Especificaciones 007-001/007-002: registrar por referencia la extensión, sin reescribir retrospectivamente su alcance aprobado.
- Plan del epic y Memory Bank: actualización por el orquestador/scribe.

## Criterio de aceptación

PC-01…PC-13 verificadas, regresión proporcional y suite completa al cierre; documentación consistente; revisión independiente y aprobación del dueño.

**Entrega read-only:** no se modificaron archivos. El checkout ya contenía una modificación en `tests/test_007_004_termination_not_success.py`, ajena a este trabajo.

## Ajustes del orquestador (review 2026-10-25)

**AJ1 — Convivencia con 007-007 (bloqueante resuelto).** `withdraw` aplica la guarda compartida de suspensión (007-007/A2) antes del replay idempotente; ni el retiro ni su replay operan sobre el paquete de una unidad suspendida. `withdraw` y `republish-agents` conservan íntegro `suspended_units`, no cambian la elegibilidad de `open-unit` ni la selección explícita, y no ofrecen abrir suspendidas. `republish-agents` exige la ejecución activa vinculada verificable: sin binding activo rechaza; nunca selecciona una ejecución suspendida. PC añadida (dentro de la PC consolidada 7): con 007-004 suspendida, retirar o repetir el retiro de su paquete → rc 1 sin cambios; `status` sigue mostrando sólo alternativas elegibles.

**AJ2 — Continuidad del retiro conserva evidencia (bloqueante resuelto).** El checkpoint de retiro reutiliza el escritor/verificador canónico de continuidad (el mismo de 007-003/007-007) y **conserva `evidence`, su clasificación y los antecedentes**; sólo agrega la decisión de retiro y cambia `next_action`. No crea `begin`, recibo ni `receipt_checkpoint`. PC con evidencia identificable creada por CLI: tras retirar, cadena íntegra, evidencia preservada y clasificación intacta.

**AJ3 — Postcondiciones consolidadas en 8** (los nombres de test son orientativos; las variantes van parametrizadas): (1) retiro válido y liberación de `prepare`; (2) elegibilidad, efectos inconclusos y flags ajenos; (3) continuidad (con y sin cabeza, con evidencia); (4) idempotencia y publicación fallida; (5) republicación, aislamiento y reparación de DRIFT; (6) modelo instalado y guardas de derivación; (7) orientación y convivencia con suspensión (AJ1); (8) recorrido integrado. El test-writer debe **extender los fixtures/tests existentes** de 007-007 y de continuidad antes de crear un módulo nuevo.

**AJ4 — Identidad genérica del caso reportado.** La fixture usa identidad genérica; se declaran dos rutas independientes: `prepared + begin + DRIFT → republish` (sin retiro) y `prepared + begin + DRIFT → withdraw` (con cierre de continuidad), y su composición en ambos órdenes. «Caso real resuelto» queda reservado a la evidencia que aporte el orquestador del otro proyecto.

## Notas registradas en la implementación (GREEN 2026-10-26)

Estas notas **registran** lo que el GREEN de esta unidad precisó y **no amplían el
alcance aprobado** ni sustituyen sus postcondiciones. Su lugar es este contrato
**vivo**: los contratos de las features cerradas son inmutables y no se reescriben
para alojar una extensión posterior.

1. **Criterio de efectos compartido (consumido, no copiado).** El retiro consume el
   criterio conservador del reanclaje
   (`cdad_continuity._require_reanchor_effect_free`) y no un detector propio. En el
   ámbito examinado —el directorio de despachos de la ejecución activa—, un registro
   cuyo `packet_id` **no tiene request publicado en el proyecto** tiene una identidad
   que no se puede establecer: es una señal **INCONCLUSA** (nunca «de otro paquete»,
   nunca ausencia) y bloquea la operación que lo examina (§Rechazos, «identidad
   ausente o discordante en el ámbito examinado»; PC-03
   `dispatch-identity-mismatch`). El mismo criterio rige el reanclaje sin cambiar su
   significado: el despacho legítimo de otro paquete de la ejecución —con su request
   publicado— se sigue ignorando.
2. **Diagnóstico del efecto más avanzado.** Cuando el paquete presenta varias
   señales, el rechazo nombra la más avanzada —materialización por delante de recibo
   o archivo de resultado—, porque es la que describe el estado real del encargo
   (§Rechazos, «nombrando fuente y causa»; PC-03 `materialization-*`).
3. **Registro por referencia de la extensión.** 007-006 extiende la orientación
   (007-001) y el borde de efectos del despacho (007-002) **por referencia a este
   documento**; los bytes aprobados de esas specs cerradas permanecen intactos y sus
   pins de `specification` siguen nombrando sus bytes vigentes.
