# spec.md — 007-003-continuity-at-edges

**Estado:** aprobada el 2026-10-24 por el orquestador (HITL delegada), tras resolver los dos VERIFY.
**Unidad:** fila 3 de `epic-007-reliable-cycle-operation`.
**Plan adicional:** no requerido.
**Materialización:** redactada por el rol architect (sesión `ses_e9339cdb6ffe…`); el orquestador materializa y resuelve los VERIFY de §7.

## 1. Descripción funcional

El recorrido de despacho y recepción conserva continuidad verificable en sus bordes:

- Antes de transportar un paquete existe un `begin` vigente, correspondiente a su ejecución, paquete e intento de continuidad.
- El registro canónico del despacho comprueba esa precondición; no sustituye la comprobación previa al transporte.
- La recepción durable deja un checkpoint idempotente, incluso desde el transporte externo o al recuperar una interrupción.
- Una reparación conserva la evidencia histórica y declara explícitamente qué evidencia dejó de acreditar el estado construido.

La continuidad no recibe resultados, no materializa, no registra disposiciones ni concede aprobaciones.

**Resultado verificable:** un recorrido serial puede interrumpirse y retomarse conservando objetivo, decisiones, cambios, evidencia aplicable y próxima acción, sin repetir transporte, recepción o transición ya realizados.

## 2. Contrato

### 2.1 Identidad y comprobación previa

```text
cdad_continuity.py verify-begin
  --project-root ROOT --execution-context EXEC.json
  --packet PACKET_ID --attempt N [--json]
```

`N` es el entero `attempt` de continuidad; **no** es el `--attempt-id` textual del registro de despacho. No se convierten uno en otro.

La comprobación exige: contexto y request legibles y coherentes; igualdad de `execution_id` entre contexto, request, cabeza y cuerpo; igualdad de `packet_id` entre argumento, request, cabeza y cuerpo; igualdad de `attempt` entre argumento, cabeza y cuerpo; cabeza vigente con `record="begin"`, cuerpo íntegro, encadenamiento verificable y ausencia de split-brain; autoridad vigente y referencias admisibles; paquete activo correspondiente al request.

No basta un `begin` histórico bajo esos identificadores: la cabeza vigente debe ser ese `begin`. Un checkpoint posterior o un `begin` de otro paquete o intento no habilita un transporte nuevo.

Salida exitosa: `{execution_id, packet_id, attempt, body_sha256, seq}`. El comando es de solo lectura; el rechazo termina con `rc≠0`, identifica la condición y no modifica nada. Los cuerpos históricos sin `record` siguen siendo legibles pero no prueban un `begin` previo.

### 2.2 Integración en los bordes ejecutables

Se añade `--continuity-attempt N` a `cdad_dispatch.py dispatch`, `cdad_dispatch.py record`, `cdad_packet.py prepare --record-dispatch` y las entradas de delegación externa que alcanzan al adaptador. Es **obligatorio** para un despacho o registro nuevo; las entradas externas propagan el mismo entero y no lo deducen del identificador textual.

**Transporte nativo.** El wiring canónico del orquestador ejecuta, en orden: validación del paquete → `begin` con `attempt=N` → `verify-begin` con los mismos identificadores → herramienta nativa de despacho → `record --continuity-attempt N`. La comprobación está inmediatamente antes de la herramienta nativa, no después de su retorno ni sólo dentro de `record`; entre comprobación y transporte no se ejecuta otra escritura de continuidad. Los cuerpos canónicos de los orquestadores y sus derivados generados declaran esta condición de despacho.

**Límite:** la herramienta nativa pertenece al runtime; esta feature no incorpora un interceptor universal que impida invocaciones manuales fuera del wiring CDAD.

**Transporte externo.** La entrada externa comprueba el mismo contrato antes de iniciar el transporte y el adaptador lo comprueba en su borde previo al lanzamiento del worker, de modo que invocarlo directamente no eluda la precondición. Sin transporte nuevo ni otro escritor de intentos.

**Registro canónico.** `prepare --record-dispatch` verifica la precondición antes de publicar un registro nuevo o completar la observación provisional; `record` no puede eludirlo. Ante fallo no publica observación, binding de estado ni entrega staged. Una repetición byte-idéntica de un registro ya durable conserva su idempotencia y no representa un transporte nuevo; esa excepción no sirve para introducir o modificar una observación.

### 2.3 Cierre común de recepción

```text
cdad_continuity.py checkpoint-receipt
  --project-root ROOT --execution-context EXEC.json
  --packet PACKET_ID --attempt N --receipt RECEIPT.json [--json]
```

Reutiliza exclusivamente cabeza y cuerpos existentes. Antes de escribir: valida el recibo con los criterios de `validate-receipt`; comprueba coincidencia de ejecución y paquete; exige un `begin` verificable para `attempt=N`; verifica integridad y encadenamiento; exige autoridad vigente. **No exige** que el paquete siga activo o `dispatched`: una transición posterior no impide recuperar el cierre pendiente.

El checkpoint conserva objetivo, decisiones, incertidumbres, presupuesto y evidencia del contexto que cierra, y añade la referencia al recibo y una decisión fundada que expresa **recepción mecánica**, nunca aprobación semántica. Se incorpora al cuerpo, sólo para este cierre:

```json
{"receipt_checkpoint": {"path": "<ruta durable del recibo>", "sha256": "<digest>"}}
```

La ruta debe ser la que resuelva el productor existente; el ejemplo no autoriza almacenamiento nuevo. Identidad del cierre: `(execution_id, packet_id, attempt, receipt path, receipt sha256)`. Un cierre idéntico ya presente en la cadena vigente devuelve éxito sin escribir, aunque existan checkpoints posteriores. Un recibo diferente bajo el mismo cierre se rechaza; no se sustituye el antecedente.

**Puntos de integración:** `receive` ejecuta el cierre después de publicar o reconocer el recibo durable, también en su rama idempotente; la llegada externa con recibo durable ejecuta el mismo cierre sin volver a staged ni a `receive`; `validate-receipt` gana `--close-continuity --continuity-attempt N` para recuperar el cierre antes de continuar la reentrada (sin esas opciones conserva su comportamiento de solo validación). Las tres entradas de reentrada convergen en el mismo mecanismo.

### 2.4 Recuperación de interrupciones

No se promete atomicidad entre publicación del recibo, transición de estado y checkpoint. Si el proceso se interrumpe después del recibo durable y antes del cierre: se reconoce el recibo existente, se valida, se ejecuta `checkpoint-receipt` y se continúa sólo con los efectos pendientes. Si la transición ya ocurrió, el cierre sigue siendo recuperable por identidad histórica del paquete y recibo, sin reactivar el paquete ni repetir la transición.

Si la cabeza avanzó a otro paquete y el cierre falta, el comando rechaza la escritura con diagnóstico de continuidad adelantada: no rebobina ni reemplaza esa cabeza. La ruta canónica impide iniciar el siguiente transporte mientras quede pendiente el cierre del recibo anterior. Una falla del cierre posterior a la publicación no elimina ni altera el recibo, no presenta el recorrido como cerrado y devuelve un fallo que distingue «recibo durable existente» de «continuidad pendiente». `reconcile` y `resume` siguen siendo de solo lectura y no reparan automáticamente.

### 2.5 Evidencia y cambios: extensión aditiva

Los UPDATE y cuerpos admiten dos campos opcionales:

```json
{
  "changes": ["Descripción explícita del cambio construido o de la reparación."],
  "evidence": [{
    "id": "red-pc-1",
    "reference": {"path": "docs/evidence/red-pc-1.txt", "sha256": "<digest>"},
    "status": "vigente",
    "reason": "Verifica PC-1 para la base declarada.",
    "antecedent": null
  }]
}
```

Contrato: `changes` es lista de strings no vacíos (declaración del escritor, no productor automático de `observed_changes`); `evidence` es lista de objetos con `id` no vacío y único en el cuerpo, `reference` con ruta relativa segura y digest SHA-256, `status` exactamente `vigente|invalidada`, `reason` no vacío en ambos estados, y `antecedent` `null` o `{body_sha256, evidence_id}` que resuelva a una evidencia de la misma cadena.

Los registros `invalidada` exigen antecedente no nulo y conservan la identidad de la evidencia invalidada: no recalculan su digest para presentarla como nueva. Una actualización que invalida evidencia conserva el cuerpo antecedente byte a byte, incluye la entrada invalidada con motivo y antecedente, no mantiene esa misma evidencia como vigente y conserva las demás entradas salvo actualización explícita que también preserve su antecedente. Omitir `evidence` al actualizar un cuerpo que ya la declara conserva su contenido; una lista vacía no puede retirar evidencia en silencio.

Una evidencia invalidada no vuelve a `vigente` conservando su identidad: una verificación nueva se declara con identificador nuevo, referencia a sus propios bytes y antecedente que explique la sustitución. Cambiar el hash, modificar la clase o reanclar **no** rehabilita evidencia; la igualdad de bytes tampoco acredita aplicabilidad. `contract`/`living` conservan exclusivamente su significado ante deriva y ninguna clase equivale a `vigente`/`invalidada`.

### 2.6 Proyección y compatibilidad

`resume.projection` añade `{changes: [], evidence: []}` con el contenido completo y estados explícitos; una entrada invalidada no se presenta como acreditación vigente ni pierde motivo o antecedente. Para cuerpos antiguos sin los campos: la lectura sigue siendo válida, la proyección emite listas vacías, no se infiere evidencia vigente desde `references`, decisiones o logs, y no se reescribe el cuerpo ni cambia su digest histórico. Los campos nuevos entran en la validación y límites de bytes existentes, y la proyección por rol aplica a las referencias de evidencia las mismas restricciones de visibilidad que a las existentes. La extensión no cambia versiones, nombres ni significados anteriores del envelope.

## 3. Invariantes

1. Almacenamiento único: sólo cabeza y cuerpos existentes; sin registro nuevo de intentos.
2. Escritor único del estado: continuidad nunca escribe `docs/.cdad-state.json`.
3. Write-ahead real: un registro posterior no sustituye la verificación inmediatamente anterior al transporte.
4. Identidad explícita: `execution_id`, `packet_id` y `attempt` coinciden; `attempt` entero y `attempt-id` textual no son equivalentes.
5. Cierre idempotente: recuperar un cierre no repite transporte, recepción, materialización ni transición.
6. Separación de autoridad: cerrar continuidad no recibe, materializa, dispone ni aprueba.
7. Historia conservada: invalidar evidencia agrega un antecedente trazable y no altera el cuerpo anterior.
8. Aplicabilidad independiente: deriva o igualdad de hashes no rehabilita evidencia.
9. Compatibilidad: cuerpos históricos legibles; interfaces de 007-001 y disposición de 007-002 intactas.
10. Observación sin reparación: `status`, `reconcile` y `resume` siguen sin efectos.

## 4. Postcondiciones y tests estables

Archivo propuesto: `tests/test_007_003_continuity_at_edges.py`.

| PC | Postcondición observable | Test estable |
|---|---|---|
| PC-01 | Sin `begin` vigente, o con ejecución, paquete, intento, cuerpo o cabeza discordantes, se rechaza el transporte externo antes de lanzar el worker; con prueba válida continúa el transporte existente. | `test_transport_requires_current_matching_begin` |
| PC-02 | El wiring nativo exige comprobar antes de invocar la herramienta; el registro canónico rechaza un intento nuevo sin la misma prueba, sin publicar estado, observación ni staging; un replay idéntico durable conserva su idempotencia. | `test_native_dispatch_and_registration_require_begin` |
| PC-03 | Una recepción ordinaria deja recibo durable y checkpoint correspondiente sin modificar `semantic_status=pending`; repetirla no añade enlaces ni repite otros efectos. | `test_receive_closes_continuity_idempotently` |
| PC-04 | Un recibo durable externo converge al mismo cierre común sin staged ni nueva recepción; repetir la validación con cierre no altera la cadena. | `test_external_durable_receipt_uses_common_continuity_close` |
| PC-05 | Interrupciones después del recibo y después de la transición se recuperan cerrando únicamente continuidad; recibo y transición permanecen idénticos; cabeza adelantada se rechaza sin rebobinar. | `test_interrupted_receipt_or_transition_recovers_only_missing_checkpoint` |
| PC-06 | Una reparación conserva el antecedente, proyecta evidencia invalidada con motivo y no la rehabilita por igualdad, cambio de hash o reanclaje; cuerpos antiguos siguen leyéndose. | `test_repair_preserves_history_and_invalidates_evidence_explicitly` |

Variaciones obligatorias: PC-01/02 con ausencia de cabeza, cuerpo alterado, `record` histórico ausente, cabeza de otro paquete o intento, checkpoint posterior al begin y autoridad expirada; PC-03/04 con recibo ilegible, identidad ajena y cierre idéntico histórico; PC-05 con fallo de cierre con recibo publicado y recuperación después de transición y antes del siguiente transporte; PC-06 con antecedente inexistente, id duplicado, invalidación sin razón, omisión accidental, identidad nueva, filtrado por rol y exceso de bytes.

Los tests verifican comandos, JSON, artefactos y efectos observables. La comprobación documental del wiring nativo no se presenta como interceptación empírica de una herramienta del runtime.

## 5. Base técnica verificada

| Base | Evidencia |
|---|---|
| Validación del contenido y construcción selectiva del cuerpo. | `cdad_continuity.py:496-581` |
| Clave existente y publicación idempotente/encadenada. | `cdad_continuity.py:627-689` |
| Verificación de cuerpo, cadena y referencias. | `cdad_continuity.py:752-886` |
| Detección de split-brain. | `cdad_continuity.py:890-920` |
| Proyección selectiva y reconstrucción. | `cdad_continuity.py:1337-1416` |
| Entrada externa anterior al transporte. | `cdad_dispatch.py:499-533` |
| Registro nativo mediante el productor canónico. | `cdad_dispatch.py:866-907,963-1043` |
| Delegación al adaptador sin segundo escritor. | `cdad_delegate.py:293-324` |
| Identificador textual del intento externo y registro previo al lanzamiento. | `cdad_delegate_opencode.py:2470-2477,2721-2742` |
| Registro canónico y replay del intento. | `cdad_packet.py:3259-3356` |
| Replay durable de recepción y publicación del recibo. | `cdad_result.py:528-638` |
| Tres entradas de reentrada. | `references/re-entry.md:25-89` |
| Envelope de continuidad. | `assets/continuity-checkpoint.schema.json:1-133` |
| Decisiones e invariantes aprobados. | `docs/specs/007-003-continuity-at-edges/discovery.md` |

Se elige un verificador y un cierre común para toda la familia de rutas, frente a parches independientes en `record` y `receive`. Las excepciones necesarias —herramienta nativa externa al CLI y recibo ya durable— se declaran, sin construir una fachada nueva de transporte.

## 6. Aceptación y límites

Aceptación: las seis PC verificadas; regresiones de continuidad, despacho, recepción, 007-001 y 007-002 verdes; documentación canónica y derivados generados consistentes.

Fuera de alcance: concurrencia, scheduler o atomicidad entre archivos; interceptar herramientas nativas fuera del wiring CDAD; redefinir disposición, reemplazo o resultados tardíos; producir automáticamente `observed_changes`; inferir validez semántica de evidencia; despliegue global, HOME, servicios o activación en consumidores; reescribir checkpoints históricos o cambiar la interfaz protegida de `status`.

## 7. Resolución de los VERIFY (orquestador, 2026-10-24)

1. **Propagación de `--continuity-attempt`:** se exige en **todas las entradas externas soportadas** —`cdad_dispatch.py` (ambos verbos) y los adaptadores presentes en el checkout— y en el registro canónico. Una entrada que no lo reciba **falla cerrado** con diagnóstico; no se deduce del `attempt-id` textual. Los adaptadores ausentes del checkout quedan explícitamente **no cubiertos** por esta feature y se declaran como límite.
2. **Recepción tardía de ejecuciones cerradas:** se permite el cierre de continuidad de una ejecución cerrada por la vía existente de recepción tardía (`cdad_result.py receive --late`), con la misma identidad de cierre y **sin** reescribir continuidad cerrada: el cierre se **agrega** como nuevo enlace si la cabeza lo admite, y si no, se rechaza con diagnóstico de continuidad adelantada. No se autoriza modificar retroactivamente la cadena.

**Deuda declarada:** el runtime conserva la capacidad de invocar su herramienta nativa directamente; la garantía previa al transporte nativo corresponde al wiring canónico y no es un sandbox. La aplicabilidad de evidencia la declara el escritor autorizado: el mecanismo verifica estructura, historia y conservación, no que la prueba siga siendo pertinente.
