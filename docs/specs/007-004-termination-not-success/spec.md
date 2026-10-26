# 007-004 — Terminación no equivale a éxito

**Estado:** aprobada por el orquestador (HITL delegada) el 2026-10-24, tras plan-review APTO CON AJUSTES (ajustes 1-4 aplicados: alcance de las pruebas, ruta FINAL TEXT, regresiones diferenciales, criterio de aceptación).  
**Epic:** `epic-007-reliable-cycle-operation`.  
**Contrato:** `.cdad/packets/007-004-termination-not-success-architect-draft-001/UNIT-CONTRACT.md`.  
**Decisiones de entrada:** `discovery.md`, sección «Decisiones del orquestador», 2026-10-24.

## 1. Descripción funcional

El consumidor distingue cinco hechos diferentes:

1. La interfaz procesó un comando y produjo un sobre.
2. El intento terminó, quedó bloqueado o no tiene desenlace concluyente.
3. Existe un resultado preparado para recepción.
4. Existe un recibo durable que debe validarse.
5. La autoridad correspondiente aprobó un gate.

El código de salida y `termination` no acreditan por sí solos recepción, cierre de continuidad ni aprobación.

La feature agrega al sobre existente el campo `delivery`, actualiza sus productores y establece una única regla de consumo documentada. Reutiliza descriptores, recibos, registros de intentos y comandos existentes.

## 2. Alcance

### Dentro

- Sobres de `cdad_dispatch.py dispatch` y `record`.
- Sobres de `cdad_delegate.py` y del adaptador `cdad_delegate_opencode.py`.
- Validación de combinaciones contradictorias.
- Compatibilidad de sobres históricos sin `delivery`.
- Consumo en el orquestador canónico, adaptadores y referencias de delegación y reentrada.
- Actualización de artefactos generados afectados mediante el mecanismo existente.
- Pruebas observables por CLI y verificaciones de las instrucciones distribuidas.

### Fuera

- Migración de códigos de salida o incorporación de `--strict-exit`.
- Nuevos recibos, registros de intentos o almacenes.
- Modificación del envoltorio privado `.cdad/local/deleg.sh`.
- Activación global, despliegue y adopción externa.
- Cambios de forma o vocabulario de `situation` y `next.operation`.
- Cambios en `provenance.continuity` o en el algoritmo de cierre de continuidad.
- Aprobación automática de gates.

El envoltorio local y los consumidores externos quedan como verificación de adopción de 007-005, no como implementación pendiente de esta feature.

## 3. Base verificada y criterio de diseño

| Evidencia | Consecuencia |
|---|---|
| `skills/cdad-cycle/scripts/cdad_dispatch.py:500-535` | `dispatch` retransmite el sobre externo; no registra otro intento ni prepara otra entrega. |
| `skills/cdad-cycle/scripts/cdad_dispatch.py:994-1027,1092-1124` | `record` prepara un descriptor, no un recibo; puede responder bloqueado sin registrar el intento rechazado. |
| `skills/cdad-cycle/scripts/cdad_delegate.py:219-287` | La interfaz interpreta y normaliza el sobre del adaptador; actualmente no conserva `delivery`. |
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:2945-2974` | OpenCode persiste la recepción antes de declarar `completed` con referencia. |
| `skills/cdad-cycle/references/cli-delegation.md:100-132` | El contrato publicado conserva rc 0 cuando se produjo un sobre. |
| `skills/cdad-cycle/references/re-entry.md:23-85` | Ya existen rutas distintas para descriptor preparado y recibo durable. |
| `sources/roles/orchestrator.md:51-54` | El consumidor describe la referencia externa como recibo, pero necesita consumir explícitamente el estado de entrega. |
| `docs/specs/007-003-continuity-at-edges/spec.md:119-135` | La recepción y el cierre de continuidad son hechos distintos; la recuperación reutiliza validación y cierre existentes. |

Se elige una distinción general de entrega, en lugar de corregir únicamente el caso `blocked`: también resuelve la ambigüedad entre resultado preparado y recibo durable.

Se conserva rc frente a la alternativa de modificarlo: preserva el contrato publicado y permite consumir diagnósticos sin introducir una migración shell. La protección depende de validar el sobre y seguir la ruta correcta, no de interpretar rc como éxito funcional.

No se incorpora otra autoridad persistente: `delivery` describe el artefacto existente; no reemplaza su validación.

## 4. Contrato del sobre

### 4.1 Forma nueva

Los sobres nuevos contienen los campos existentes y el campo obligatorio `delivery`:

```json
{
  "attempt": "identidad existente o null",
  "session": "identidad existente o null",
  "termination": "completed",
  "delivery": "staged",
  "delivery_ref": "referencia al artefacto existente",
  "diagnosis": null
}
```

Vocabularios cerrados:

- `termination`: `completed | blocked | transport-error | timeout | cancelled | unknown`.
- `delivery`: `none | staged | received`.

Significado:

| Campo | Contrato |
|---|---|
| `delivery=none` | El sobre no acredita una entrega consumible. `delivery_ref` es `null`. No prueba ausencia de cambios ni de efectos durables que deban reconciliarse. |
| `delivery=staged` | La referencia identifica el descriptor existente de partes preparadas, aún pendientes de recepción. |
| `delivery=received` | La referencia identifica el recibo durable existente, pendiente de validación por el consumidor. |
| `delivery_ref` | Una sola referencia, no vacía cuando hay entrega. No se introduce un segundo campo de referencia. |
| `attempt` | Conserva identidad y semántica anteriores. Su presencia no garantiza que exista un registro: un rechazo previo al registro puede declarar la identidad rechazada. |

Los ejemplos anteriores describen el contrato propuesto, no una interfaz ya implementada.

### 4.2 Tabla exhaustiva de combinaciones

`R` significa una cadena no vacía que referencia el tipo de artefacto indicado. La validez estructural no reemplaza la validación del artefacto.

| `termination` | `delivery` | `delivery_ref` | Validez |
|---|---|---|---|
| `completed` | `staged` | R: descriptor | Válida para `record` nativo. |
| `completed` | `received` | R: recibo | Válida para la llegada externa. |
| `blocked` | `none` | `null` | Válida. |
| `transport-error` | `none` | `null` | Válida. |
| `timeout` | `none` | `null` | Válida. |
| `cancelled` | `none` | `null` | Válida. |
| `unknown` | `none` | `null` | Válida. |
| Cualquier otra combinación | Cualquiera | Cualquiera | Inválida. |

En particular:

- `completed + none` es contradictorio.
- Una terminación distinta de `completed` con `staged` o `received` es contradictoria.
- `none` con referencia no nula es contradictorio.
- `staged` o `received` sin referencia, con referencia vacía o de tipo incorrecto es inválido.
- Un vocabulario desconocido es inválido.
- Un descriptor presentado como recibo, o viceversa, se rechaza al validar el artefacto.
- Una combinación estructuralmente válida pero incompatible con la ruta también se rechaza.

Si un fallo ocurre después de publicar un recibo, el productor no fabrica `blocked + received`: comunica fallo sin entrega acreditada y un diagnóstico que permita reconciliar los efectos existentes. No elimina el recibo ni presenta el recorrido como cerrado. Se conserva el tratamiento de recuperación definido por 007-003.

### 4.3 Reglas por productor y verbo

| Productor o ruta | Resultado | Sobre requerido |
|---|---|---|
| `cdad_dispatch.py record`, payload preparado correctamente | Descriptor staged | `completed + staged + referencia al descriptor`. |
| `record`, intento registrado sin payload | Sin entrega | `unknown + none + null`. |
| `record`, correlación contradictoria | Rechazo sin registro ni staging | `blocked + none + null`. |
| `cdad_delegate_opencode.py`, recepción concluida correctamente | Recibo durable | `completed + received + referencia al recibo`. |
| OpenCode, terminación no completada | Sin entrega acreditada | Terminación correspondiente `+ none + null`. |
| `cdad_delegate.py`, respuesta válida del adaptador | Retransmisión | Conserva identidad, terminación, entrega y referencia; no registra ni recibe otra vez. |
| `cdad_delegate.py`, timeout propio o transporte sin sobre utilizable | Diagnóstico | `timeout` o `transport-error`, `none`, `null`. |
| `cdad_dispatch.py dispatch` | Llegada externa | Retransmite el sobre validado; no prepara ni recibe otra entrega. |

En estas rutas externas, `completed + staged` no es una llegada aceptable: el adaptador externo tiene a su cargo la recepción existente.

Los errores de invocación que actualmente fallan antes de producir un sobre conservan ese comportamiento. No se exige convertir todos los errores CLI en sobres.

### 4.4 Rechazo de contradicciones

Un productor actualizado nunca emite una combinación inválida.

Cuando una interfaz recibe del adaptador un sobre contradictorio o mal tipado:

1. No lo retransmite como entrega válida.
2. No lo corrige silenciosamente hasta convertirlo en éxito.
3. No registra otro intento, recibe, materializa ni registra una transición por ese sobre.
4. Produce un diagnóstico de protocolo mediante un sobre `transport-error + none + null`.
5. Conserva las identidades utilizables del sobre original sin inventar reemplazos.

Un consumidor que encuentre directamente un sobre inválido se detiene y diagnostica. El rc del proceso no autoriza ignorar esta condición.

La clasificación como `transport-error` describe una respuesta de adaptador no utilizable; no prueba ausencia de efectos del intento original.

## 5. Compatibilidad histórica

La ausencia de `delivery` es la única condición que activa la interpretación histórica. Un campo presente con `null`, valor desconocido o tipo incorrecto no es un sobre histórico válido.

El consumidor usa contexto conocido de la operación, nunca el nombre del archivo:

| Contexto histórico | Condición | Interpretación permitida |
|---|---|---|
| `record` nativo | `completed` y referencia no vacía | Candidato a `staged`; validar descriptor y su vinculación antes de recibir. |
| Llegada externa por `dispatch` o `cdad_delegate.py` | `completed` y referencia no vacía | Candidato a `received`; validar recibo y su vinculación antes de continuar. |
| Cualquiera de las rutas conocidas | Terminación no completada y referencia `null` | `none`; no avanzar. |
| Contexto desconocido, referencia incompatible o combinación contradictoria | Cualquiera | Detenerse y diagnosticar. |

Reglas adicionales:

- Una referencia histórica no se acepta por terminar en `RESULT.json` ni por parecer una ruta de recibo.
- Si no puede demostrarse el contexto, no se prueban rutas alternativas hasta encontrar una que permita avanzar.
- Los productores actualizados siempre emiten `delivery`.
- La compatibilidad no reescribe artefactos históricos ni genera recibos sustitutivos.
- La validación usa los mecanismos existentes: el descriptor se somete a la recepción existente; el recibo se somete a `validate-receipt`.
- La interfaz externa que normalice un sobre histórico no anuncia `received` sin comprobar el recibo correspondiente.

## 6. Regla canónica de consumo

### 6.1 Dueños

- `skills/cdad-cycle/references/cli-delegation.md` es dueño de la forma del sobre, vocabularios, combinaciones, compatibilidad histórica y significado de rc.
- `skills/cdad-cycle/references/re-entry.md` es dueño del procedimiento de consumo y de la selección de ruta.
- `sources/roles/orchestrator.md` y los adaptadores de `sources/agents/adapters/` remiten a esos dueños y exigen su aplicación; no copian la tabla ni mantienen otro algoritmo.

Los agentes generados deben reflejar esas referencias y obligaciones mediante el proceso de generación existente.

### 6.2 Consumo de llegadas con sobre (procedimiento obligatorio)

Este procedimiento gobierna sólo las llegadas que traen sobre. La llegada como FINAL TEXT sin sobre (handoff a otro chat, respuesta textual del rol) conserva su ruta existente —staging bajo `.cdad/inbox` → recepción— definida en `references/re-entry.md`; esta feature no la vuelve dependiente de un sobre.

1. Leer y comprobar el sobre. Si es histórico, aplicar §5.
2. Rechazar contradicciones, contexto insuficiente y artefactos no verificables.
3. Consumir según `delivery`:

| Entrega | Acción |
|---|---|
| `none` | No avanzar a materialización, transición exitosa ni gate. Diagnosticar y consultar la orientación existente; reconciliar efectos cuando corresponda. |
| `staged` | Ejecutar la recepción existente sobre el descriptor; después validar el recibo y continuar la reentrada. No volver a preparar ni reescribir las partes. |
| `received` | Validar el recibo existente y continuar la reentrada. No ejecutar otra recepción ni volver a staging. |

4. Cumplir las obligaciones de continuidad de 007-003 antes de continuar con efectos posteriores.
5. Materializar y registrar sólo los efectos pendientes y autorizados según sus contratos existentes.
6. Aplicar por separado la decisión semántica del gate.

Cuando falta el cierre de continuidad después de una recepción durable, se utiliza la recuperación existente con `validate-receipt --close-continuity --continuity-attempt N`. El entero no se deduce de `attempt`.

`rc=0`, `termination=completed` y `delivery=received` no equivalen a aprobación. Un recibo mantiene `semantic_status: "pending"` y materializar no agrega aprobación.

## 7. Compatibilidad de códigos de salida

- Se conserva rc 0 cuando la interfaz produce un sobre, incluso si comunica bloqueo, timeout o fallo de protocolo.
- Se conservan los errores de resolución o invocación anteriores que terminan sin sobre y con rc no cero.
- El rc interno del adaptador no sustituye el contenido de un sobre válido.
- Un rc interno no cero con sobre válido no convierte automáticamente una entrega válida en fallo; la interfaz conserva el contrato de retransmisión y validación.
- Un rc interno cero sin sobre utilizable no acredita entrega.
- No se agrega ninguna opción de salida estricta.

## 8. Postcondiciones y trazabilidad de pruebas

Los nombres siguientes son identificadores estables propuestos para tests nuevos, no afirmaciones sobre tests ya existentes. Las pruebas funcionales invocan las CLI públicas en proyectos temporales autocontenidos y observan stdout, stderr, rc y artefactos. Los dobles de adaptador/runtime no requieren servicios reales.

| ID | Postcondición observable | Test estable |
|---|---|---|
| PC-01 | `record` con payload válido emite `completed/staged`, referencia un descriptor existente, conserva bytes y no crea recibo. | `test_007_004_record_payload_is_staged_not_received` |
| PC-02 | `record` con observación válida y sin payload emite `unknown/none/null`; registra sólo el intento y no prepara entrega. | `test_007_004_record_without_payload_has_no_delivery` |
| PC-03 | `record` con correlación contradictoria emite `blocked/none/null`, rc 0 y diagnóstico; no registra el intento rechazado ni prepara entrega. | `test_007_004_record_contradiction_blocks_without_effects` |
| PC-04 | La ruta externa OpenCode completada emite `completed/received` y su referencia supera `validate-receipt`. | `test_007_004_opencode_completed_has_valid_received_delivery` |
| PC-05 | Las terminaciones no completadas de OpenCode emiten `none/null`; ninguna declara recepción. | `test_007_004_opencode_noncompleted_never_claims_delivery` |
| PC-06 | `cdad_delegate.py` conserva los seis campos válidos del adaptador, incluida identidad y `delivery`, sin producir otro registro o recibo. | `test_007_004_delegate_relays_delivery_without_duplicate_effects` |
| PC-07 | `dispatch` conserva el sobre externo validado y no agrega staging, recepción ni otro intento. | `test_007_004_dispatch_relays_external_delivery` |
| PC-08 | La interfaz rechaza cada combinación inválida de §4.2 con `transport-error/none/null` y diagnóstico, sin efectos de aceptación. Incluye tipos incorrectos y vocabularios desconocidos. | `test_007_004_delegate_rejects_invalid_delivery_combinations` |
| PC-09 | La ruta externa rechaza `completed/staged` aunque sea una combinación válida para `record`. | `test_007_004_external_route_rejects_staged_delivery` |
| PC-10 | Un adaptador sin sobre, ilegible o que no arranca produce `transport-error/none/null`; un timeout propio produce `timeout/none/null`. | `test_007_004_transport_failures_have_no_delivery` |
| PC-11 | Un sobre histórico externo se admite como recibido sólo con contexto conocido y recibo válido; un descriptor disfrazado de recibo se rechaza. | `test_007_004_legacy_external_requires_valid_receipt` |
| PC-12 | Un descriptor histórico de `record` sigue la recepción existente; un recibo presentado como descriptor o un contexto ausente no autoriza avanzar. | `test_007_004_legacy_native_requires_context_and_descriptor` |
| PC-13 | La compatibilidad histórica acepta no entrega coherente, pero rechaza `completed` sin referencia, terminación no completada con referencia y `delivery` presente inválido. | `test_007_004_legacy_compatibility_is_fail_closed` |
| PC-14 | rc conserva la semántica de §7: bloqueo con sobre devuelve 0; error previo sin sobre conserva fallo; rc interno no sustituye un sobre válido. | `test_007_004_exit_codes_preserve_envelope_semantics` |
| PC-15 | La ruta staged seguida por las CLI existentes recibe y valida; la ruta received sólo valida. Repetir la reentrada no duplica recibo ni transición y no aprueba un gate. | `test_007_004_reentry_routes_preserve_receipt_and_gate_boundaries` |
| PC-16 | Recibo durable con cierre pendiente se recupera mediante validación y cierre existentes con N explícito, sin repetir recepción ni cambiar `provenance.continuity`. | `test_007_004_received_delivery_preserves_continuity_recovery` |
| PC-17 | Las fuentes e instrucciones generadas exigen consumir `delivery`, remiten a los dueños de §6.1 y no autorizan avanzar por rc o terminación solos. | `test_007_004_documented_consumers_reference_canonical_delivery_rule` |
| PC-18 | En bloqueo y recepción las CLI de orientación conservan forma y vocabulario de `situation/next.operation`; el sobre no introduce una situación de éxito ni transición automática. | `test_007_004_delivery_does_not_redefine_orientation` |

PC-05 y PC-08 son parametrizadas sobre vocabularios y combinaciones finitos. No se exige una campaña de propiedades, cobertura porcentual ni benchmark para esta feature.

**Qué verifica cada prueba.** (a) El comportamiento automático de las interfaces (`record`, `dispatch`, `cdad_delegate.py`, adaptador) se prueba por CLI. (b) El procedimiento del orquestador —incluida la selección de ruta histórica según contexto— es una instrucción verificada documentalmente en PC-17; ninguna PC atribuye al producto una selección automática que en realidad hace el test. (c) PC-12 y PC-15 son pruebas de integración de comandos existentes en las que **el escenario declara la ruta** (descriptor → `receive`; recibo → `validate-receipt`) y se observa que los comandos aceptan la correcta y rechazan la incorrecta.

PC-16 y PC-18 son regresiones diferenciales: pueden cumplirse reutilizando los tests existentes de 007-003 y 007-001 más un caso que demuestre que introducir `delivery` no cambia su comportamiento; no exigen duplicar esas suites. PC-15 puede reutilizar la evidencia existente de idempotencia de recepción.

PC-17 también comprueba que la referencia de reentrada conserva la ruta FINAL TEXT sin sobre.

PC-17 es una verificación de contrato documental ejecutable por CLI: verifica secciones y referencias canónicas, no sólo la aparición aislada de la palabra `delivery`. No acredita adopción de consumidores externos.

## 9. Invariantes verificables

1. **Una identidad de intento:** los envoltorios no crean otro registro para retransmitir un sobre.
2. **Una ruta de recepción:** `received` no vuelve a staging ni ejecuta otra recepción.
3. **Referencia única:** `delivery_ref` apunta al artefacto existente; no aparece otro recibo o ledger.
4. **Sin aprobación implícita:** ni sobre, recepción, validación ni materialización aprueban gates.
5. **Validación obligatoria:** entrega declarada y artefacto validado son hechos distintos.
6. **Fallo cerrado:** una contradicción no se normaliza a éxito ni permite efectos posteriores de aceptación.
7. **Efectos inciertos honestos:** `none`, timeout o fallo de transporte no prueban ausencia de cambios.
8. **Compatibilidad aditiva:** vocabulario de terminación y semántica de rc se mantienen.
9. **Orientación intacta:** se conserva el contrato de 007-001.
10. **Continuidad intacta:** se conserva el contrato de 007-003, incluyendo N explícito y recuperación sin repetir recepción.
11. **Una definición por responsabilidad:** esquema en delegación CLI; consumo en reentrada; fuentes y adaptadores remiten a ellos.

## 10. Criterios de aceptación

La implementación satisface la especificación cuando:

- PC-01 a PC-18 tienen evidencia reproducible y pasan.
- Todos los productores nuevos incluidos emiten `delivery`.
- Se rechazan las combinaciones inválidas y las incompatibilidades de ruta.
- Los sobres históricos tienen aceptación acotada por contexto y validación, sin heurísticas de nombre.
- Las instrucciones canónicas y generadas consumen el sobre sin usar rc o `termination` como aprobación.
- No aparecen recibos, registros de intentos ni almacenes adicionales.
- Se preservan los contratos de 007-001 y 007-003.
- El cierre aporta la evidencia de suite completa según la política común del paquete.
- El review contrasta implementación e instrucciones distribuidas con esta especificación.

La recepción real y la revisión del envoltorio local pertenecen a 007-005. Esta feature no declara demostrada esa adopción.

## 11. Evidencia del draft

**Archivos modificados:** ninguno.  
**Commit creado:** ninguno.  
**Tests ejecutados:** ninguno; tarea read-only de especificación.  
**HEAD observado:** `c614b2fc48646c320fc37461a6d9e3d491b1d77f`.

Comandos ejecutados desde `<repo>`:

```sh
cat .cdad/packets/007-004-termination-not-success-architect-draft-001/PACKET.md
cat .cdad/packets/007-004-termination-not-success-architect-draft-001/UNIT-CONTRACT.md
cat docs/specs/007-004-termination-not-success/discovery.md
cat skills/cdad-cycle/references/design-principles.md
git status --short

sha256sum .cdad/packets/007-004-termination-not-success-architect-draft-001/UNIT-CONTRACT.md docs/cdad-policy.json
rg -n 'termination|delivery_ref|envelope|def .*dispatch|def .*record' skills/cdad-cycle/scripts/cdad_{dispatch,delegate,delegate_opencode}.py
sed -n '85,145p' skills/cdad-cycle/references/cli-delegation.md
sed -n '1,110p' skills/cdad-cycle/references/re-entry.md
sed -n '35,70p' sources/roles/orchestrator.md
sed -n '950,1140p' skills/cdad-cycle/scripts/cdad_dispatch.py

sed -n '219,290p' skills/cdad-cycle/scripts/cdad_delegate.py
sed -n '490,540p' skills/cdad-cycle/scripts/cdad_dispatch.py
sed -n '100,140p' docs/specs/007-003-continuity-at-edges/spec.md
rg -n 'delivery_ref|ENVELOPE' sources/agents/adapters/{opencode,claude-code}.md
ls tests/*{dispatch,delegate}*
git rev-parse HEAD
git diff --stat
git status --short
```

Resultados:

- SHA-256 del contrato: `9285fabe3b0da0b6ac8f62032698d841ff8e83c473d3d66943cb7496f494a15b`.
- SHA-256 de política: `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`.
- Ambos coinciden con el paquete.
- `git status --short` inicial y final, y `git diff --stat`: sin salida.
- La consulta de tests encontró `tests/test_006_005_u1b_dispatch_entry.py` y otros tests de dispatch. El patrón `tests/*delegate*` no encontró archivos; no se presenta como evidencia de ausencia de pruebas de delegación.
- Las lecturas confirmaron la diferencia actual entre descriptor staged y recibo durable, y la ausencia de `delivery` en la normalización existente.

**Aprobación:** pendiente; este draft no se autoaprueba.