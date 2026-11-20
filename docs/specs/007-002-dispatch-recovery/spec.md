# spec.md — 007-002-dispatch-recovery

**Estado:** borrador para revisión y aprobación.
**Fecha:** 2026-10-24.
**Unidad:** fila 2 de `epic-007-reliable-cycle-operation`.
**Plan adicional:** no requerido; clasificación y reemplazo consumen una misma decisión canónica y cierran un único resultado operativo.
**Nota de materialización:** el texto proviene del rol architect (sesión `ses_e93df4769ffe…`). El orquestador resolvió aquí el VERIFY de §2.4 y extendió PC-7 (decisión del 2026-10-24, HITL delegada).

## 1. Descripción funcional

Una disposición registrada mediante `register-transition --transition disposition` resuelve explícitamente un despacho sin entrega. `reconcile` debe reconocerla y dejar de informar indefinidamente `dispatched-unknown`.

El orquestador puede preparar un sucesor mediante `prepare --replace-packet`, conservando el encargo anterior y aplicando las correcciones explícitas admitidas por ese comando. No necesita reconstruir el encargo ni provocar artificialmente una deriva del contrato.

«Resuelto» significa exclusivamente **dispuesto**. No incluye paquetes recibidos, materializados o completados.

La recuperación no vuelve a despachar el paquete anterior, no detiene al worker, no recibe resultados y no concede aprobación. La decisión sigue perteneciendo al orquestador; los comandos consumen su registro verificable.

**Resultado verificable:** disponer un despacho sin recibo permite reconocer la decisión y preparar un único sucesor trazable, sin repetir efectos ni alterar la autoridad existente.

## 2. Contrato

### 2.1 Fuente de la disposición

La única fuente es una entrada de `docs/.cdad-state.json:stage_history` producida por `register-transition --transition disposition`.

No bastan: `active_packet.status=failed`; una nota o explicación en prosa; la desaparición de una sesión; una terminación del transporte; un archivo `.superseded.json` sin disposición canónica; una entrada correspondiente a otro paquete, feature o ejecución.

Una **disposición canónica verificable** exige:

1. Estado JSON legible, con `stage_history` de tipo lista.
2. Entrada objeto con `transition="disposition"`.
3. `packet_id` y `feature` coincidentes con el request examinado.
4. `transition_key_payload` objeto con la **estructura completa** que produce el productor (`cdad_packet.py:5499-5558`): los bindings `execution_id`, `feature_id`, `packet_id`; `transition="disposition"`; `stage`, `substage`; `resolution` y `replaced_by` coincidentes con la entrada (ausente como `null`); `postcondition`, `current_stage`, `artifacts`, `approved_by`, `contract`, `plan` y `closure` presentes con la forma que el productor les da. Un payload reducido a un subconjunto, aun con hash recalculado correcto, **no** es canónico. No se exige autenticidad del autor.
5. `transition_key` no vacío e igual al SHA-256 de la serialización canónica del payload vigente: JSON UTF-8, `ensure_ascii=False`, claves ordenadas y separadores `(",", ":")`.
6. `resolution` perteneciente a `abandoned|superseded`.
7. Para `superseded`, `replaced_by` es un identificador de paquete no vacío, seguro y distinto del predecesor.
8. La entrada no está sustituida: su clave no aparece en `supersedes` de otra entrada, conforme al criterio existente del estado.
9. Las entradas candidatas no presentan decisiones vigentes contradictorias. Varias ocurrencias de la misma clave y contenido no constituyen decisiones distintas; decisiones vigentes diferentes impiden seleccionar una arbitrariamente.

La referencia certifica la correspondencia estructural con el registro, no la autenticidad del autor ni una aprobación. Los registros históricos sin payload verificable no habilitan esta recuperación: se diagnostican y no se migran.

### 2.2 Salida de `reconcile`

Se conserva el envelope existente, su versión y el marcador `reconcile-v1`.

Se agrega siempre `signals.disposition`, con uno de estos valores: `null` (no pudo seleccionarse una disposición canónica verificable) o el objeto siguiente:

```json
{
  "resolution": "abandoned",
  "replaced_by": null,
  "record": {
    "path": "docs/.cdad-state.json",
    "index": 7,
    "transition_key": "<sha256>"
  }
}
```

Los campos son obligatorios cuando el objeto existe: `resolution` (`abandoned|superseded`), `replaced_by` (identificador declarado o `null`), `record.path` (exactamente `docs/.cdad-state.json`), `record.index` (entero no negativo, base cero en `stage_history`), `record.transition_key` (clave verificada).

En ocurrencias idénticas de una misma decisión se referencia la primera por índice. El índice localiza en la instantánea observada; la clave comprueba identidad después.

Una clasificación dispuesta tiene la forma:

```json
{
  "classification": "disposed",
  "repeat_effect": false,
  "escalate": false,
  "signals": {
    "receipt": {"state": "absent", "effect": null, "semantic_status": null},
    "materialization": "open",
    "dispatch": "dispatched",
    "disposition": {
      "resolution": "abandoned",
      "replaced_by": null,
      "record": {"path": "docs/.cdad-state.json", "index": 7, "transition_key": "<sha256>"}
    }
  }
}
```

El ejemplo muestra el delta; no sustituye los demás campos obligatorios del envelope. El literal de ausencia del recibo se conserva según el contrato vigente del productor de esa señal.

#### Precedencia normativa

Después de los controles previos existentes —incluidos integridad de continuidad y split-brain—, clasificar en este orden:

| Orden | Condición | `classification` |
|---|---|---|
| 1 | Autoridad expirada. | `expired-authority` |
| 2 | Recibo presente pero ilegible o no fiable. | `unknown` |
| 3 | Recibo legible y materialización existente. | `already-closed` |
| 4 | Recibo legible sin materialización. | `received` |
| 5 | Despacho existente, sin recibo y con disposición canónica verificable. | `disposed` |
| 6 | No puede determinarse de forma fiable la disposición por ilegibilidad, inconsistencia o ambigüedad relevante. | `unknown` |
| 7 | Despacho existente sin recibo ni disposición verificable, con fuentes suficientes para afirmar su ausencia. | `dispatched-unknown` |
| 8 | Sin despacho ni recibo. | `not-started` |

Una disposición no convierte por sí sola un paquete sin evidencia de despacho en `disposed`: esa contradicción produce `unknown`.

Las señales comprobadas se conservan aun cuando una clasificación de mayor precedencia domine. En particular, una disposición verificable puede aparecer en `signals.disposition` junto con `expired-authority`, `received` o `already-closed`.

#### Campos que cambian

- `classification` admite `disposed`.
- `signals` incorpora `disposition`.
- `reasons` explica la clasificación y, para `disposed`, distingue decisión registrada de autorización para repetir.
- `unknowns` conserva diagnósticos existentes y agrega los de lectura o verificación de la disposición.

La redacción de los diagnósticos no es API estable; debe identificar fuente y causa.

#### Campos que no cambian

No cambian nombres, tipos ni significados de `schema_version`, `reconcile`, `execution_id`, `packet_id`, `authority`, `head`, `references`, `repeat_effect=false`, `escalate=false`, `signals.receipt`, `signals.materialization` ni `signals.dispatch`.

`disposed` es un resultado observado y conserva `rc=0`. Los errores previos que impiden emitir reconciliación siguen siendo errores.

`reconcile` no prepara sucesores ni introduce un campo de operación automática.

### 2.3 Elegibilidad de `prepare --replace-packet`

Se conserva la interfaz: `prepare --replace-packet <packet-id> --reason <razón no vacía>`.

Se admiten dos rutas:

| Ruta | Condiciones específicas |
|---|---|
| Reemplazo existente de preparado obsoleto | Paquete activo `prepared` y obsolescencia verificable de contrato, companion o política, conforme al comportamiento vigente. |
| Recuperación de dispuesto | Paquete activo `failed`, despacho existente, ausencia de recibo y disposición canónica verificable. No exige deriva. |

Para la ruta de recuperación se valida además:

1. El identificador pedido es el de `state.active_packet`.
2. El request pertenece a la ejecución activa y a su feature.
3. `request.packet_id` coincide con el identificador y su directorio.
4. Rol y substage coinciden entre request y paquete activo.
5. Las rutas están contenidas en el directorio de paquetes.
6. `REQUEST.json` y `PACKET.md` existen y son legibles.
7. La feature sigue abierta.
8. No existe directorio de recibo en la ruta durable del paquete, incluso si su contenido es ilegible.
9. La política está reconciliada y se satisfacen las validaciones vigentes de preparación, contrato, encargo, scopes y aprobación aplicable.

Un estado `failed` sin esas pruebas se rechaza con `rc≠0`, sin publicar sucesor. Un paquete `dispatched` sin disposición continúa rechazándose y remitiendo a reconciliación. Los estados `completed` y los paquetes con recibo quedan fuera.

`reconcile` observa la decisión histórica; `prepare` comprueba además la elegibilidad **actual** para crear trabajo.

### 2.4 Sucesor y trazabilidad

Cuando la disposición permite crear un sucesor:

- El sucesor tiene identificador nuevo, distinto del predecesor.
- Se conserva el encargo mediante el mecanismo existente de reemplazo, incluidas sus correcciones explícitas y pisos de rol.
- Se conservan `plan_task` y `current_decisions` cuando estaban declarados.
- Contrato y política se resuelven para la preparación actual; no se copian como autoridad histórica.
- Se ejecuta la misma validación de aprobación aplicable a una preparación ordinaria.
- El sucesor queda como paquete activo `prepared`; no se despacha automáticamente.
- Se publica `.superseded.json` en el directorio del predecesor con la forma existente: `superseded_by`, `reason`, `superseded_at`, digests anterior/nuevo y listas `conserved_fields`/`changed_fields`.
- No se cambian los bytes anteriores de `REQUEST.json` ni `PACKET.md`.
- No se modifica la disposición ni se agrega otra entrada a `stage_history`.

La creación, activación y trazabilidad usan la publicación transaccional existente. Un rechazo anterior a la publicación no deja sucesor parcial.

#### Sucesor declarado mediante `replaced_by`

1. **Sucesor existente y coherente:** no se asigna otro identificador ni se genera otro paquete; la operación termina con `rc≠0` y diagnóstico que cita al sucesor declarado; no reescribe ni activa ese sucesor.
2. **Sucesor existente pero ilegible o incoherente:** se informa la inconsistencia y tampoco se crea una alternativa.
3. **Sucesor declarado inexistente (decisión del 2026-10-24, corregida tras la revisión):** se rechaza con `rc≠0` y diagnóstico que nombra el sucesor declarado e indica la vía practicable: registrar la disposición corregida con `--supersedes <transition_key defectuosa>` **cambiando la resolución** (p. ej. de `superseded` a `abandoned`, que además deja `replaced_by=null`). `resolution` y `replaced_by` integran la identidad canónica del payload (`cdad_packet.py:5499-5558`), mientras que `supersedes` no (`6440`), de modo que la entrada nueva se registra y la defectuosa queda sustituida. Límite real: una corrección que conservara `resolution` y `replaced_by` idénticos colisionaría y sería un no-op (`6337-6359`); no se promete esa vía, y forzarla exigiría cambiar el escritor. No se crea otro identificador ni se publica nada.

Esta negativa explícita evita presentar como preparación nueva una operación que no publicó nada.

### 2.5 Compatibilidad con 007-001

Esta feature no agrega ni modifica valores de `situation`, `next.operation` ni `authority.approval_reference`. `status` sigue aplicando los predicados de 007-001. Un predecesor `failed` no se convierte en `packet-prepared` o `packet-dispatched`. Tras publicar correctamente un sucesor activo `prepared`, la vista lo presenta según el contrato ya aprobado de 007-001.

No se agrega un verbo de recuperación, un gate ni una aprobación implícita.

## 3. Invariantes

- **INV-1 — Decisión única.** `register-transition --transition disposition` sigue siendo el único registro de la decisión. `reconcile` y el reemplazo no crean registros alternativos.
- **INV-2 — Observación sin efectos.** `reconcile` y `status` son de solo lectura: no preparan, despachan, reciben, materializan, aprueban ni modifican estado o continuidad.
- **INV-3 — Escritor y publicación existentes.** El módulo de continuidad no escribe `docs/.cdad-state.json`; la activación del sucesor usa el mecanismo existente.
- **INV-4 — Separación de significados.** Disposición ≠ recibo ≠ aprobación ≠ terminación del worker. `disposed` nunca autoriza repetir el efecto del predecesor.
- **INV-5 — Identidad y conservación.** El sucesor no reutiliza el identificador del predecesor; el encargo se conserva salvo correcciones explícitas; contrato y autoridad se verifican para el sucesor.
- **INV-6 — Sin duplicación.** Un sucesor existente declarado en `replaced_by` impide generar otro; un paquete que dejó de ser activo no se reemplaza otra vez por esta ruta.
- **INV-7 — Fallo cerrado.** Una marca `failed`, una disposición no verificable o un recibo ilegible nunca bastan para publicar un sucesor.
- **INV-8 — Compatibilidad.** Se conserva la interfaz de 007-001 y el reemplazo de preparados obsoletos. Sin ampliación de autoridad ni gate nuevo.

## 4. Postcondiciones y tests estables

Los nombres siguientes son identificadores estables del RED. Los tests verifican comandos, JSON y archivos observables, no funciones internas ni orden de llamadas.

| PC | Postcondición | Test |
|---|---|---|
| PC-1 | Con despacho, ausencia de recibo y disposición canónica `abandoned`, `reconcile` devuelve `disposed`, referencia verificable y `repeat_effect=false`. | `test_reconcile_abandoned_dispatch_is_disposed` |
| PC-2 | Con disposición canónica `superseded`, la señal conserva exactamente `resolution`, `replaced_by` y la referencia a su entrada. | `test_reconcile_superseded_dispatch_preserves_declared_successor` |
| PC-3 | Un despacho sin recibo y sin disposición sigue siendo `dispatched-unknown`; una marca `failed` aislada no produce `disposed`. | `test_reconcile_failed_without_disposition_remains_unresolved` |
| PC-4 | Un paquete activo dispuesto y elegible puede reemplazarse aunque contrato, companion y política no hayan cambiado; se publica un sucesor nuevo `prepared`. | `test_replace_disposed_packet_without_drift_prepares_successor` |
| PC-5 | El sucesor conserva los campos del encargo y los bindings opcionales, excepto correcciones explícitas; el diff de `.superseded.json` coincide con las diferencias observables. | `test_replace_disposed_packet_preserves_assignment_and_explicit_corrections` |
| PC-6 | La publicación deja `.superseded.json` apuntando al sucesor, con razón no vacía y digests correctos; los bytes anteriores no cambian. | `test_replace_disposed_packet_publishes_trace_without_rewriting_predecessor` |
| PC-7 | Con `replaced_by` declarado: sucesor existente coherente → rechazo que lo cita; existente incoherente → rechazo con la inconsistencia; declarado inexistente → rechazo que nombra el sucesor y declara el límite, sin prometer una corrección que el productor no permite. En los tres casos no se publica ni se altera nada y el estado queda byte-idéntico. | `test_replace_disposed_packet_does_not_duplicate_existing_declared_successor` |
| PC-8 | Sin disposición canónica verificable, reemplazar un activo `failed` se rechaza sin publicación; un paquete recibido o `completed` tampoco entra. | `test_replace_failed_or_received_packet_requires_eligible_disposition` |
| PC-9 | Una disposición no desplaza autoridad expirada, recibo ilegible, recibo legible ni recibo con materialización; las señales y diagnósticos comprobados no se pierden. Disposición verificable **sin evidencia de despacho** → `unknown`. `signals.disposition` está **siempre presente** (`null` cuando no hay disposición admisible). | `test_reconcile_disposition_respects_authority_and_receipt_precedence` |
| PC-10 | Clave incorrecta, payload ausente, divergente o **incompleto con hash recalculado**, otro binding, resolución inválida, sustitución registrada o decisiones contradictorias no habilitan `disposed` ni reemplazo. La ausencia simple (fuentes legibles, sin entradas) se distingue del estado ilegible o del `stage_history` inválido: sólo el primero es `dispatched-unknown`; los otros son `unknown` con causa. Sólo cuenta la disposición **vigente**: una sustituida no compite frente a su sustituta válida. | `test_disposition_consumers_reject_unverifiable_or_conflicting_records` |
| PC-11 | El reemplazo rechaza paquete no activo, request ajeno o incoherente, feature cerrada y cualquier directorio de recibo durable; cada rechazo nombra la causa y no publica. | `test_replace_disposed_packet_checks_active_identity_open_feature_and_no_receipt` |
| PC-12 | La disposición no permite saltarse política reconciliada, validaciones de encargo ni aprobación aplicable. | `test_replace_disposed_packet_preserves_policy_and_approval_checks` |
| PC-13 | Dos reconciliaciones del mismo fixture producen el mismo JSON y dejan byte-idénticos estado, paquetes, recibos y continuidad; el envelope conserva campos y agrega `signals.disposition`. Con **duplicados idénticos** de una misma decisión se selecciona el **primer índice** del historial. | `test_reconcile_disposition_is_read_only_deterministic_and_additive` |
| PC-14 | Una preparación aceptada cambia únicamente artefactos de publicación y trazabilidad; no agrega disposiciones, recibos, despachos, aprobaciones ni checkpoints; una segunda invocación no crea otro sucesor. | `test_replace_disposed_packet_has_no_extra_effects_and_cannot_repeat` |
| PC-15 | El reemplazo de un activo `prepared` mantiene su requisito de deriva y sus validaciones; esta extensión no habilita reemplazar un preparado intacto. | `test_prepared_packet_replacement_still_requires_verifiable_drift` |
| PC-16 | Antes y después del reemplazo, `status` cumple 007-001 sin vocabulario, forma ni significado nuevos en los tres campos protegidos. | `test_dispatch_recovery_preserves_007_001_status_contract` |

## 5. Criterio de aceptación

1. Todas las PC aprobadas tienen tests observables trazados y verdes.
2. Un recorrido controlado ejecuta preparación → despacho registrado → disposición → reconciliación `disposed` → reemplazo → validación del sucesor.
3. Ese recorrido conserva predecesor, decisión y autoridad, sin recibo o despacho adicional.
4. Las regresiones de continuidad, disposición, reemplazo y 007-001 permanecen verdes.
5. Sin VERIFY pendientes.

No se exige porcentaje de cobertura ni recepción real en otro proyecto: esa recepción pertenece a 007-005.

## 6. Base técnica verificada

| Evidencia | Base |
|---|---|
| Clasificación actual sin disposición; precedencia de autoridad y recibos. | `skills/cdad-cycle/scripts/cdad_continuity.py:965-991` |
| Obtención de señales y publicación del envelope. | `cdad_continuity.py:1010-1064` |
| Marcador actual `reconcile-v1`. | `cdad_continuity.py:87` |
| Reemplazo restringido al activo y rechazo de estados distintos de `prepared`. | `skills/cdad-cycle/scripts/cdad_packet.py:2564-2602` |
| Exigencia actual de deriva. | `cdad_packet.py:2603-2639` |
| Conservación del encargo, correcciones y bindings opcionales. | `cdad_packet.py:2672-2733` |
| Validación del sucesor, diff, `.superseded.json` y publicación. | `cdad_packet.py:2734-2774` |
| Resoluciones canónicas existentes. | `cdad_packet.py:5489` |
| Payload e identidad verificable de transición. | `cdad_packet.py:5499-5578` |
| Evidencia de despacho por ejecución y paquete. | `cdad_packet.py:5700-5722` |
| Validación existente de disposición. | `cdad_packet.py:6051-6100` |
| Entrada de historial y datos de disposición. | `cdad_packet.py:6430-6477` |
| Efecto existente de disposición: solo `status=failed`. | `cdad_packet.py:6513-6529` |
| Pertenencia del request y detección conservadora de recibo. | `cdad_packet.py:6719-6733` |
| Decisiones e invariantes aprobados para esta unidad. | `docs/specs/007-002-dispatch-recovery/discovery.md` |

Se reutiliza el mecanismo general de reemplazo y su publicación, con una nueva condición de elegibilidad respaldada por la decisión existente. No se crea una ruta paralela.

## 7. Límites declarados

- Sin concurrencia, scheduler ni coordinación de workers.
- Sin integración nueva de checkpoints: corresponde a 007-003.
- Sin despliegue global ni cambios de HOME, servicios o runtime.
- Sin tratamiento nuevo de resultados tardíos: las rutas existentes siguen aplicando.
- Sin recuperación de paquetes recibidos o completados.
- Sin migración de disposiciones históricas no verificables.
- Sin garantía de que el worker dispuesto haya terminado.
- Sin autenticación criptográfica del autor de una entrada de estado.
- Sin cambios a la identidad canónica de las transiciones existentes.
- Sin nueva abstracción de intentos, verbos, registros o gates.
- **Deuda declarada:** corregir una disposición conservando `resolution` y `replaced_by` idénticos (corrección «en el mismo sentido») requiere modificar el escritor: su identidad no incluye `supersedes`. No se hace en 007-002; la vía practicable es cambiar la resolución con `--supersedes`.
