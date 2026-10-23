# spec.md — 007-001-unambiguous-entry

**Estado:** borrador; pendiente de aprobación explícita.  
**Autoridad:** contrato de unidad y discovery aprobado de 007-001.  
**Plan adicional:** no requerido; una única unidad de implementación y revisión.

## 1. Descripción funcional

El orquestador debe identificar desde `cdad_packet.py status`:

1. La situación operativa actual.
2. La siguiente operación, el script que la ejecuta y su procedimiento.
3. La referencia verificable a la aprobación aplicable al rol y objeto actuales.

La evolución es **aditiva**: conserva `entry`, los campos existentes y sus significados. No crea autoridad, gates, almacenamiento de continuidad ni registros de intentos.

La implementación canónica está en `skills/cdad-cycle/scripts/cdad_packet.py`; `scripts/cdad_packet.py` sigue siendo su wrapper.

## 2. Contrato de salida

Los nombres y valores siguientes son **interfaz nueva propuesta**, no interfaces actualmente disponibles. Tras aprobación constituyen el contrato para 002–004.

### 2.1 Situación

Agregar siempre el campo raíz `situation`, con uno de estos valores:

| Valor exacto | Condición |
|---|---|
| `diagnosis` | La selección existente devuelve `entry=diagnosis`. |
| `packet-dispatched` | Fuera de diagnóstico, el paquete activo pertenece a la ejecución activa y está `dispatched`. |
| `packet-prepared` | Fuera de diagnóstico, el paquete activo pertenece a la ejecución activa y está `prepared`. |
| `pending-work-unresolved` | Existe trabajo pendiente, pero no hay un paquete activo inequívoco preparado o despachado. |
| `execution-active` | Existe ejecución activa sin trabajo pendiente. |
| `at-rest` | No existe ejecución activa ni trabajo pendiente. |

La tabla establece precedencia de arriba abajo. Una inconsistencia de pertenencia del paquete se clasifica como `pending-work-unresolved`, se explica en `unknowns` y no habilita despacho.

La ejecución histórica dejada tras cerrar una feature no es ejecución activa. Se conserva el criterio existente de `_active_execution`.

### 2.2 Siguiente operación

Conservar `next.route` y `next.source`. Agregar siempre `next.operation`:

```json
{
  "verb": "reconcile",
  "script": "scripts/cdad_continuity.py",
  "procedure": "references/continuity.md",
  "source": "docs/.cdad-state.json:active_packet.status"
}
```

Los cuatro campos son obligatorios. `script` es una ruta relativa al directorio del skill instalado; no es relativa al proyecto consumidor. `procedure` usa la misma base.

| `situation` | `verb` | `script` | `procedure` |
|---|---|---|---|
| `diagnosis` | `diagnose` | `null` | `references/project-start.md` |
| `packet-dispatched` | `reconcile` | `scripts/cdad_continuity.py` | `references/continuity.md` |
| `packet-prepared` | `validate-packet` | `scripts/cdad_packet.py` | `references/orientation.md` |
| `pending-work-unresolved` | `diagnose` | `null` | `references/project-execution.md` |
| `execution-active` | `resume` | `scripts/cdad_continuity.py` | `references/continuity.md` |
| `at-rest` | `open-unit` | `scripts/cdad_packet.py` | `references/project-start.md` |

`source` identifica el dato determinante:

- Diagnóstico de configuración: `next.source` existente.
- Paquete preparado o despachado: `docs/.cdad-state.json:active_packet.status`.
- Ejecución activa: `docs/.cdad-state.json:execution`.
- Reposo: `docs/.cdad-state.json:active_feature`.
- Pendiente irresuelto: `docs/.cdad-state.json:active_packet / .cdad/packets`.

`diagnose` es una indicación al operador, **no un subcomando nuevo**. Por ello lleva `script=null`.

La operación representa el **primer paso**, no una macro. Para un paquete preparado, el procedimiento sigue siendo validar → `begin` → transporte → registro, según la ruta existente. No sustituye ese protocolo ni autoriza repetir un despacho.

002–004 podrán alimentar esta proyección con evidencia adicional dentro de sus contratos. No cambiarán nombres, tipos o significados de estos campos. Una necesidad de valores adicionales exige una enmienda explícita; no se anticipan estados de entrega que todavía no producen esas features.

### 2.3 Referencia de aprobación

Conservar intacto `authority.approval`. Agregar su hermano `authority.approval_reference`:

```json
{
  "role": "implementer",
  "object": "feature-spec",
  "status": "vigente",
  "record": {
    "path": "docs/.cdad-state.json",
    "pointer": "/stage_history/3",
    "transition_key": null,
    "approved_by": "aprobador registrado"
  },
  "contract": {
    "path": "docs/specs/example/spec.md",
    "declared_sha256": "...",
    "observed_sha256": "..."
  },
  "reason": null
}
```

Todos los campos mostrados son obligatorios; `record` y `contract` pueden ser `null`.

#### Vocabulario

- `role`: rol del request aplicable, o `null`.
- `object`: `epic-plan`, `feature-spec`, `draft-plan` o `null`.
- `status`:
  - `vigente`
  - `ausente`
  - `sustituida`
  - `contrato cambiado`
  - `no requerida`
  - `desconocida`

Los cuatro primeros expresan los resultados aprobados en discovery. Los dos últimos evitan inventar una aprobación para un borrador o un resultado cuando faltan datos.

`reason` es `null` para `vigente`; en los demás casos contiene una explicación no vacía. Su redacción no es API estable.

#### Fuentes y selección

1. Resolver el request del paquete activo en `.cdad/packets/<id>/REQUEST.json`, comprobando su pertenencia a la ejecución activa.
2. Obtener de ese request el rol y el contrato; no inferirlos de una aprobación histórica.
3. Para `draft-plan`: `object=draft-plan`, `status=no requerida`, `record=null`. No buscar una aprobación inexistente.
4. Para architect: `object=epic-plan`; usar el mandato que selecciona `_approved_epic_plan_entry`. Su aprobación no tiene pin de hash del plan.
5. Para los demás roles: `object=feature-spec`; aplicar los predicados de `_approved_spec_entries` y la comparación de ruta y digest de `_contract_approval_for`.

No modificar los criterios de autorización existentes para acomodar la vista.

Para la spec:

- `vigente`: hay un registro no sustituido que nombra la ruta y el digest declarados, y los bytes actuales del contrato coinciden con ese digest.
- `contrato cambiado`: existen registros no sustituidos para la feature, pero ninguno satisface la ruta/digest; o los bytes actuales contradicen el digest declarado.
- `sustituida`: no hay registros aplicables no sustituidos, pero sí registros de aprobación de esa feature excluidos por `supersedes`.
- `ausente`: no existe registro de aprobación de esa feature.

Cuando hay varios registros elegibles, `vigente` utiliza el primero coincidente en el orden del historial. Para explicar los otros resultados se utiliza el primer candidato de su clase en ese orden. Esta elección hace determinista el localizador sin cambiar qué registros autorizan.

`record.pointer` es un JSON Pointer con índice real del historial. `transition_key` puede ser `null` para registros históricos que no lo tengan. No se imprime el historial completo.

Para architect, `contract` describe el contrato del request cuando es verificable, pero **no se usa su digest como pin del mandato del epic**. Una contradicción comprobada de sus bytes se informa como `contrato cambiado`, conservando el localizador del mandato encontrado.

#### Ausencia de información

- Sin paquete activo aplicable: `role=null`, `object=null`, `status=desconocida`; no seleccionar una aprobación de una ejecución histórica.
- Request ausente, ilegible o inconsistente: `status=desconocida`, con causa en `reason` y `unknowns`.
- Contrato no legible cuando se necesita comprobar sus bytes: `status=desconocida`, nunca `vigente`.
- Falta de registro comprobada con fuentes legibles: `ausente`, no `desconocida`.

La vista es diagnóstico, no gate: un resultado distinto de `vigente` no modifica por sí solo `entry`, no registra transiciones y no altera el código de salida exitoso de una proyección válida.

## 3. Alineación del orquestador

`references/orientation.md` será propietario del mapa compacto verbo→script. `sources/roles/orchestrator.md` lo citará desde su árbol de entrada y su wiring, sin copiar interfaces completas.

El mapa debe incluir:

| Verbo | Propietario ejecutable |
|---|---|
| `status`, `validate-packet`, `open-unit`, `prepare`, `render`, `prepare --record-dispatch` | `scripts/cdad_packet.py` |
| `begin`, `checkpoint`, `reconcile`, `resume`, `trigger` | `scripts/cdad_continuity.py` |
| `receive` | `scripts/cdad_result.py` |

La distinción entre `prepare --record-dispatch` y el verbo `record` de la entrada de transporte se conserva: no son alias intercambiables. Transporte nativo/externo mantiene sus referencias actuales y no se convierte en un subcomando ficticio de `cdad_packet.py`.

El árbol del orquestador leerá `situation` y `next.operation`, conservando `entry` como agrupador compatible. Declarará el caso pendiente irresuelto como diagnóstico sin despacho.

Los agentes derivados se regeneran mediante el generador existente; no se editan como propietarios independientes.

## 4. Postcondiciones y trazabilidad a tests

Tests propuestos en `tests/test_007_001_unambiguous_entry.py`, salvo la regresión existente indicada. Los nombres son requisitos para RED, no tests ya escritos.

| ID | Postcondición observable | Test |
|---|---|---|
| PC-01 | Los seis escenarios de §2.1 producen exactamente la situación y operación de las tablas, respetando precedencia. | `test_situation_operation_matrix` parametrizado |
| PC-02 | Paquete preparado indica `validate-packet`; despachado indica `reconcile`; sus scripts y referencias existen. | `test_prepared_and_dispatched_operations` |
| PC-03 | Ejecución histórica cerrada no produce `execution-active` ni una aprobación vigente histórica. | `test_closed_execution_is_history` |
| PC-04 | Pendiente sin paquete inequívoco o con pertenencia inconsistente produce diagnóstico sin script ejecutable; explica la causa. | `test_unresolved_pending_work_is_not_dispatchable` |
| PC-05 | Architect muestra el mandato real de `epic_history`, con pointer resoluble, sin exigir pin del plan. | `test_architect_approval_uses_epic_mandate` |
| PC-06 | Los cuatro resultados de aprobación de spec cumplen los predicados de §2.3; el pointer apunta al registro seleccionado. | `test_spec_approval_status_matrix` |
| PC-07 | Un hash coincidente con ruta ajena y un contrato cuyos bytes cambiaron nunca producen `vigente`. | `test_approval_checks_path_and_current_bytes` |
| PC-08 | `draft-plan` declara `no requerida` y no inventa registro. | `test_draft_plan_requires_no_approval` |
| PC-09 | Request/contrato ilegible, ausencia de paquete y falta de registro se distinguen conforme a §2.3. | `test_approval_unknown_vs_absent` |
| PC-10 | Selección entre varios registros y sustituciones es determinista y coherente con los selectores de autorización existentes. | `test_approval_selection_and_supersession` |
| PC-11 | La proyección conserva campos anteriores y sus valores para los mismos fixtures; `next.route` conserva la acción natural y su rama condicional. | `test_status_is_additive` y `tests/test_005_011_t3_view_action.py` |
| PC-12 | Ejecutar `status` no altera bytes del estado, requests, contratos, historiales ni checkpoints. | `test_status_is_read_only` |
| PC-13 | La salida sigue siendo un único JSON acotado; superar `--max-bytes` falla sin JSON parcial y con diagnóstico. Agregar historial no seleccionado no aumenta la salida. | `test_status_bound_and_history_independence` |
| PC-14 | El mapa documentado resuelve a scripts existentes y el cuerpo canónico del orquestador lo referencia; distingue ambos registros de despacho. | `test_orchestrator_references_operation_map` |

PC-06 incluye controles con `supersedes`, registros históricos sin `transition_key`, aprobación ausente y múltiples registros. PC-11 compara la proyección antigua eliminando exclusivamente las tres adiciones: `situation`, `next.operation` y `authority.approval_reference`.

## 5. Invariantes verificables

1. **Compatibilidad:** no eliminar, renombrar ni reinterpretar campos anteriores; `entry` conserva su mapa existente.
2. **Autoridad única:** la vista reutiliza los criterios de aprobación existentes; no escribe aprobaciones ni autoriza operaciones.
3. **Sin efectos:** ninguna orientación dispara preparación, continuidad, transporte o recepción.
4. **Evidencia honesta:** desconocido no equivale a ausente; disponer de un registro no prueba que los bytes actuales estén aprobados.
5. **Acotación:** límite predeterminado existente de 16.384 bytes; no volcar historiales o contratos.
6. **Sin mecanismos paralelos:** ningún almacenamiento o registro nuevo de intentos, disposición o continuidad.
7. **Propietario documental único:** mapa en orientación; orquestador y derivados por referencia/generación.

## 6. Decisiones de diseño

- **Ampliación frente a reemplazo de `entry`:** se elige ampliación por compatibilidad con consumidores y pruebas existentes.
- **Una operación inicial frente a una fachada de despacho:** se proyecta el primer paso verificable y se referencia el protocolo; evita esconder varios efectos bajo un verbo nuevo.
- **Referencia común frente a una aprobación genérica:** una estructura común expresa objetos distintos, pero conserva las reglas específicas de mandato del architect y pin de spec.
- **Diagnóstico frente a inferencia de entregas:** ante pendientes ambiguos se informa el límite. 001 no interpreta señales de terminación cuya corrección pertenece a 002–004.

## 7. Aceptación y límites

Aceptación requiere:

- PC-01 a PC-14 verificadas y trazadas a resultados de tests.
- Regresión `tests/test_005_011_t3_view_action.py` sin modificaciones que relajen su contrato.
- Documentación y agentes generados consistentes.
- Evidencia de solo lectura y del límite de salida.
- Aprobación explícita de esta especificación antes de RED.

La suite completa se ejecuta únicamente conforme a la política de cierre del paquete.

Fuera de alcance: recuperación de intentos abandonados, sucesores, integración de checkpoints en los bordes, cambios de códigos de salida, reconocimiento nuevo de entrega/recepción, concurrencia, despliegue global y recepción en otro proyecto.

**Límite declarado:** `status` es una observación de archivos, no una transacción atómica entre todos ellos. La proyección no reemplaza la validación inmediatamente anterior a una operación.

## 8. Base técnica verificada

- `skills/cdad-cycle/scripts/cdad_packet.py:1772-1904`: selectores y autorización por rol/objeto.
- `…/cdad_packet.py:6643-6751`: ejecución activa, pendientes, selección de entrada y rutas.
- `…/cdad_packet.py:6767-6891`: proyección, aprobación actual y límite.
- `sources/roles/orchestrator.md:28-48,137-176`: árbol de entrada y wiring.
- `skills/cdad-cycle/references/orientation.md:14-38,65-74`: orientación y operaciones.
- `tests/test_005_011_t3_view_action.py:451-540`: compatibilidad de preparados y despachados.

---

## Informe de ejecución

- **Archivos modificados:** ninguno.
- **Commit observado:** `5f5fbc58ccd2a622f6f841c12860eea8e14a9786`.
- **Commit creado:** ninguno.
- **Tests ejecutados:** ninguno; tarea read-only de especificación.
- **Estado observado:** ` M docs/.cdad-state.json`; diferencia preexistente, no intervenida. `git diff --stat` informó `1 file changed, 1 insertion(+), 1 deletion(-)`.

Comprobaciones exactas y resultados:

```text
sha256sum .cdad/packets/007-001-unambiguous-entry-architect-draft-001/UNIT-CONTRACT.md
5ed7186f3e3006951c162d8eeabd0ba7a52a3109bf4b2705123d04f746035152

sha256sum docs/cdad-policy.json docs/epics/epic-007-reliable-cycle-operation/plan.md
f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711
713194aac03a1d077db3075d2062322e6ab61919de0a00dfb624146506042440

git status --short
 M docs/.cdad-state.json

git rev-parse HEAD
5f5fbc58ccd2a622f6f841c12860eea8e14a9786
```

Los comandos exactos de lectura (`cat`, `sed -n`, `rg -n`) y sus salidas están registrados en las llamadas de herramientas de esta sesión. No se materializó `spec.md` ni `plan.md`; corresponde al orquestador materializar este texto y solicitar la aprobación.