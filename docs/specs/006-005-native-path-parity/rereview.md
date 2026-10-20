# Re-review 006-005 — requiere cambios

Revisado hasta `42b34a9`, incluidos RED `056c0f1`, GREEN `3ca6597` y testfix `e99bc5a`. Hashes de contrato y política coincidentes con el paquete.

## Estado de los bloqueantes anteriores

| Hallazgo | Estado | Evidencia |
|---|---|---|
| **B-1** | **Cerrado** | `cdad_packet.py:3103-3112`: los allows de implementación preceden ahora a las prohibiciones convencionales; política, derivados y privados conservan precedencia. Los focales comprueban ambos implementers y código no-test escribible. |
| **B-2** | **Normalización cerrada; regresión nueva B-4** | `cdad_delegate_opencode.py:2135-2160,2233`: momento y modelo se normalizan después de seleccionar la fila, por cualquiera de las dos entradas. El momento contradictorio produce `blocked`, sin entrega (`cdad_dispatch.py:1003-1018`). |
| **B-3** | **Parcial; no cerrado** | Los agentes regenerados distinguen correctamente las salidas, pero remiten a un procedimiento que todavía ordena escenificar y recibir la entrega externa. Detalle abajo. |

## B — Bloqueantes

### B-3 — El procedimiento referenciado todavía contradice la ruta externa corregida

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicaciones:**
- `agents/cdad-orchestrator.md:234-249`
- `agents/claude-code/cdad-orchestrator.md:238-253`
- `skills/cdad-cycle/references/re-entry.md:25-49,76-87`

El generado corregido dice que `delivery_ref` es el recibo durable y prohíbe recibir otra vez. Sin embargo, el mismo cuerpo remite al **Orchestrator materialization protocol**, donde:

- `:42-43` conserva expresamente la escenificación manual para **external CLI dispatch**;
- `:47-49` ordena ejecutar `receive`;
- `:85-87` presenta esa secuencia completa como la ruta del adaptador CLI.

El recorrido real es:

```text
dispatch → módulo registra y recibe → sobre con delivery_ref=recibo
         → validate-receipt → materialize → register-transition
```

El módulo elimina sus archivos transitorios después de recibir (`cdad_delegate_opencode.py:2009-2016`). Por tanto, el procedimiento referenciado pide una operación que ya ocurrió y cuyo insumo no devuelve la entrada.

**Consecuencia:** quien consulte la referencia normativa para continuar recibe instrucciones incompatibles: reconstruir una escenificación o intentar una segunda recepción. Los nuevos tests comprueban el generado y la validez del recibo, pero no este siguiente tramo documental.

**Cierre verificable:** corregir la referencia común por estado de llegada: FINAL TEXT pendiente de escenificar, descriptor ya escenificado o recibo ya durable. La ruta externa debe entrar directamente por validación del recibo; la nativa debe conservar `record → receive`. Comprobar ambos recorridos incluyendo las referencias que el generado manda consultar.

### B-4 — Se elimina una llave no declarada y se acredita identidad donde el contrato exige `unknown`

**Required · Verdict: BLOCKING · Bucket: m**

**Ubicación:** `skills/cdad-cycle/scripts/cdad_dispatch.py:687-704,757-778`.

Además de normalizar B-2, el fix cambió la semántica de correlación: cuando la fila expone `parent_id` pero falta `--parent`, ahora **omite** la llave. Antes producía `parent: unknown`.

Esto contradice el resultado no verificable del contrato: falta una llave ⇒ `unknown`, con garantía menor PD-6 cuando existe resultado nativo (`spec.md:108-114`). La decisión registrada para B-2 sólo autoriza normalizar la observación (`execution.md:370`); no declara esta enmienda de identidad.

Reproducción sobre una fila sintética con padre observable, sin padre declarado:

```text
states: {'agent': 'match', 'moment': 'match', 'project': 'match'}
verified: True session: fixture-child
```

También lo observé por la entrada real con el fixture SQLite: `--session`, sin `--parent`, acredita la sesión y registra provenance `verified (moment, project)`.

**Consecuencia:** una declaración incompleta deja de conservar la incertidumbre exigida y pasa a acreditar sesión/modelo. Afecta al recorrido normal por `--session`, no a una variante hipotética.

**Cierre verificable:** conservar `unknown` para la llave expuesta sin declaración, ajustando el test positivo para aportar `--parent`; o registrar primero una enmienda explícita que autorice excluirla y delimite esa garantía. Cubrir padre ausente, coincidente y contradictorio; no mezclar la selección de fila con la suficiencia de evidencia.

## Re-trazado E1–E5 y V-11

| Recorrido | Resultado de esta revisión |
|---|---|
| **E1 — nativa** | Selección → normalización común → correlación → un registro I8 → descriptor. `record` devuelve el descriptor, no un recibo (`cdad_dispatch.py:1020-1038`). Ejecuté después `receive` y `validate-receipt`: ambos **rc=0**, un intento I8. Queda **B-4** para la identidad sin padre declarado. |
| **E2 — temporal y barreras** | Test-writer permite sólo tests declarados/co-ubicados y temporales autorizados; privados, política y derivados prevalecen (`cdad_packet.py:3070-3091`). B-1 queda cerrado. `scope_validation: passed` real sigue pendiente/deuda U6-2; no lo acredito mediante estos focales. |
| **E3 — externa** | Entrada relaya el sobre (`cdad_dispatch.py:499-536`); módulo deriva kind, recibe y devuelve el recibo durable (`cdad_delegate_opencode.py:1982-2016`). El focal ejecutó `validate-receipt` sobre esa salida. El siguiente comando mecánico funciona; la guía completa mantiene **B-3**. Scribe/materialización y rechazo del Memory Bank: focales verdes. |
| **E4 — interrupción** | El write-ahead externo y su compleción siguen en el módulo; `disposition`/`failed` y sus regresiones pasan. No cambió este diseño. Se mantienen el límite nativo sin write-ahead y la recuperación del huérfano declarados en `execution.md:317-334`; no equivalen a autorización para repetir efectos. |
| **E5 — migración** | Sección inexistente → traslado acotado; sección existente → rechazo sin sobrescribir (`cdad_dispatch.py:346-378,422`); capacidades consume la sección (`:1055-1074`). Focales verdes. |
| **V-11 — Odoo** | `prepare` resuelve el sufijo (`cdad_packet.py:4606-4619`); el módulo consume el agente publicado y contrasta la identidad durable (`cdad_delegate_opencode.py:371-435`). La observación real permanece documentada en `execution.md:335`; no repetí el despacho real. |

### ¿Algún rol gana escritura fuera de su mapa generado?

**El diff nuevo no introduce tal ampliación.** El implementer queda igual o más restringido; los roles lectores mantienen su prohibición. La excepción intencional sigue siendo el temporal autorizado del test-writer, expresamente permitido por PD-24 y acotado por las barreras finales.

Esto describe los mapas de herramientas, **no un sandbox**: la capacidad previa de Bash no constituye permiso contractual para eludirlos.

### Enmiendas A-1

Están declaradas y son coherentes con la decisión B-1:

- `tests/test_004_002_t5_reviewfix.py:38-55,389-451`;
- `tests/test_005_008_t1_nested_tests.py:73-97,479-528`.

Ambas sustituyen `allow` por `deny` **sólo para edición del implementer** y conservan el control de clasificación `implementation`. La declaración de 005-008 resuelve el conflicto literal con su PD-7 (`docs/specs/005-008-project-path-capabilities/spec.md:151-155`). La clasificación no se convierte en autorización para editar tests.

## O — Opcionales anteriores

- **O-1:** pendiente para el cierre, conforme a `execution.md:372`. El documento de aceptación todavía conserva estados obsoletos y `scope_validation: unknown`; no debe presentarse como satisfacción literal de PD-22.
- **O-2:** permanece como deuda aceptada (`execution.md:373`). No lo reabro como bloqueante.

## Evidencia ejecutada

Comandos principales:

```sh
git diff 056c0f1~1 HEAD --stat
git diff 056c0f1~1 HEAD -- skills/cdad-cycle/scripts sources/roles/orchestrator.md sources/agents/adapters
sha256sum docs/specs/006-005-native-path-parity/spec.md docs/cdad-policy.json
```

Con `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider`:

- `test_006_005_reviewfix.py`, `test_004_002_t5_reviewfix.py`, `test_005_008_t1_nested_tests.py`, `test_006_005_u6fix4_native_selection.py`, `test_006_005_u6fix6_model_parity.py`, `test_006_005_u3b_derived_temporary_permission.py`: **47 passed**.
- `test_006_005_u1a_runtime_config.py`, `test_006_005_u1b_dispatch_entry.py`, `test_006_005_u5_disposition_failed.py`, `test_006_005_u7_scribe_role_report.py`, `test_003_006_t3_receive_wiring.py`: **63 passed**.

Un intento inicial usó un nombre de archivo inexistente: **no tests ran**. Otra selección ampliada agotó **240 segundos**: no la contabilizo como corrida completa.

**Archivos modificados:** ninguno. **Commit creado:** ninguno.

## Abstentions

- No repetí despachos reales ni verifiqué los artefactos originales completos de aceptación/V-11; distingo esa evidencia documental de mis ejecuciones con fixtures.
- No ejecuté `make validate`: su cadena incluye lectura del archivo privado prohibido.
- No ejecuté la suite completa; corresponde al cierre según PD-21.
- No acredito independencia de familia de modelo respecto del implementer.

**Veredicto final: requiere cambios por B-3 y B-4.**