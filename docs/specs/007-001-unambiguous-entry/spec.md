# spec.md — 007-001-unambiguous-entry

**Estado:** APROBADA el 2026-10-23 por el orquestador (HITL delegada del dueño), tras re-revisión independiente con dictamen APTO y sin hallazgos pendientes.
**Autoridad:** contrato de unidad y decisiones del orquestador al final del discovery de 007-001.
**Plan adicional:** no requerido; una única unidad de implementación y revisión.

## 1. Descripción funcional

El orquestador debe identificar desde `cdad_packet.py status`:

1. La situación operativa actual.
2. La siguiente operación, el script que la ejecuta y su procedimiento.
3. La referencia verificable a la aprobación aplicable al rol y objeto actuales.

La evolución es **aditiva**: conserva `entry`, los campos existentes y sus significados. Permite extender `unknowns` con las causas diagnósticas expresamente definidas en esta especificación, sin perder diagnósticos anteriores. No crea autoridad, gates, almacenamiento de continuidad ni registros de intentos.

La implementación canónica está en `skills/cdad-cycle/scripts/cdad_packet.py`; `scripts/cdad_packet.py` sigue siendo su wrapper.

## 2. Contrato de salida

Los nombres y valores siguientes son **interfaz nueva propuesta**, no interfaces actualmente disponibles. Tras aprobación constituyen el contrato para 002–004.

### 2.1 Situación

Agregar siempre el campo raíz `situation`, con uno de estos valores:

| Valor exacto | Condición |
|---|---|
| `diagnosis` | La selección existente devuelve `entry=diagnosis`. |
| `packet-dispatched` | Fuera de diagnóstico, existe paquete activo inequívoco y está `dispatched`. |
| `packet-prepared` | Fuera de diagnóstico, existe paquete activo inequívoco y está `prepared`. |
| `pending-work-unresolved` | Existe trabajo pendiente según el criterio existente, pero no hay paquete activo inequívoco preparado o despachado; o existe una inconsistencia comprobada en la pertenencia del paquete activo. |
| `execution-active` | Existe ejecución activa sin las condiciones anteriores. |
| `at-rest` | No existe ejecución activa ni las condiciones anteriores, **y el estado es legible**. |

**Precedencia por ilegibilidad:** si `docs/.cdad-state.json` no puede leerse o interpretarse, `situation=diagnosis`, `verb=diagnose`, `script=null`, `procedure=references/project-start.md`, `source=docs/.cdad-state.json`; se conservan `entry` y `next.route`. No se usa `pending-work-unresolved`: tampoco está probado que exista trabajo pendiente, y `at-rest` exige estado legible (INV-4).

La tabla establece precedencia de arriba abajo. Una inconsistencia de pertenencia se explica en `unknowns`; fuera de `diagnosis`, produce `pending-work-unresolved` y no habilita despacho.

La ejecución histórica dejada tras cerrar una feature no es ejecución activa. Se conserva el criterio existente de `_active_execution`.

#### Pertenencia y selección mínima

Esta proyección reutiliza los datos de `_active_execution`, `_pending_work`, `state.active_packet` y los bindings existentes de `REQUEST.json`. No ejecuta ni exige la validación integral del paquete.

Un **paquete activo inequívoco** requiere conjuntamente:

1. `_active_execution` devuelve una ejecución con `id` no vacío.
2. Existe `state.active_packet` con identificador no vacío y estado `prepared` o `dispatched`.
3. Su identificador permite localizar de forma segura `.cdad/packets/<id>/REQUEST.json` dentro del directorio de paquetes.
4. El request es un objeto JSON legible.
5. `request.execution_id` coincide con el `id` de la ejecución activa.
6. `request.packet_id` coincide con el identificador del paquete en el estado y con el nombre de su directorio.
7. `request.feature_id` coincide con la feature de la ejecución activa.
8. Los bindings `role` y `substage` coinciden entre request y `state.active_packet`; ambos son cadenas no vacías.

Estos controles establecen identidad y pertenencia, no autorización ni validez integral. No sustituyen comprobaciones de scopes, inputs, renderizado, contrato/versionado o gates propias de `validate-packet`.

La selección sigue estas reglas:

- **Con `active_packet` explícito:** solo ese registro puede seleccionar el paquete actual. Otros directorios, incluso pendientes y pertenecientes a la misma ejecución, no lo sustituyen ni vuelven ambigua una selección que cumple los controles anteriores.
- **Con `active_packet` explícito inconsistente:** no buscar otro directorio como fallback. Informar la causa en `unknowns`.
- **Sin `active_packet`:** los directorios no seleccionan por sí solos un paquete preparado o despachado. El criterio existente de `_pending_work` determina si hay trabajo pendiente: request de la ejecución activa y ausencia de directorio de recibo en su ruta existente.
- Uno o varios directorios pendientes sin `active_packet` producen `pending-work-unresolved`; no se deduce de ellos un estado de despacho.
- Los directorios de otras ejecuciones y los ya recibidos no se convierten en trabajo pendiente por esta feature.
- Un request ilegible no prueba pertenencia a la ejecución activa. Se informa su ilegibilidad en `unknowns` cuando impide resolver el paquete explícito o cuando se observa al examinar los candidatos de pendientes, sin inventar pertenencia ni alterar el predicado existente de `_pending_work`.

Una inconsistencia de identidad o pertenencia es evidencia nueva para `situation` y `unknowns`; no cambia la selección histórica de `entry` ni `next.route`.

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

Si los controles nuevos detectan una inconsistencia, `next.operation` indica diagnóstico aunque la prosa histórica de `next.route` conserve su valor por compatibilidad. El orquestador utiliza `situation` y `next.operation` para decidir ese primer paso.

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
    "index": 3,
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

Todos los campos mostrados son obligatorios; `record` y `contract` pueden ser `null`. Cuando se conoce la declaración del contrato pero no pueden leerse sus bytes, `contract` conserva la ruta y el digest declarados, con `observed_sha256=null`. Si no se emite el objeto `contract`, no se inventa; si se emite sin haber comprobado bytes (caso `draft-plan`), `observed_sha256` es `null` explícito, nunca omitido.

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

#### Fuentes y predicados

1. Resolver el request del paquete seleccionado conforme a §2.1.
2. Obtener de ese request el rol y el contrato; no inferirlos de una aprobación histórica.
3. Si `contract.kind=draft-plan`, el objeto es `draft-plan`, con precedencia sobre el rol.
4. En otro caso, para architect el objeto es `epic-plan`; usar el mandato seleccionado por `_approved_epic_plan_entry`. Su aprobación no tiene pin de hash del plan.
5. Para los demás roles, el objeto es `feature-spec`; aplicar los predicados de `_approved_spec_entries` y la comparación de ruta y digest de `_contract_approval_for`.

No modificar los criterios de autorización existentes para acomodar la vista.

Para clasificar la spec:

- **Registros de aprobación:** entradas de `stage_history` para la feature de la ejecución, con `stage=specification` y `approved_by` no vacío, antes de excluir sustituidas.
- **Registros no sustituidos:** los que devuelve `_approved_spec_entries`, conservando exactamente su tratamiento de `supersedes`.
- **Pin coincidente:** igualdad conjunta de `contract_path` y `contract_sha256` con la ruta y el digest declarados en el request.
- **Bytes coincidentes:** SHA-256 observado del contrato igual al digest declarado en el request.

Para architect, el mandato es exactamente el que selecciona `_approved_epic_plan_entry`, incluidos sus criterios de epic, stage y aprobador. No se introduce filtrado por sustitución ni pin del plan que ese selector no tenga.

#### Clasificación ordenada

Las tablas son normativas: evaluar de arriba abajo y detenerse en la **primera** condición verdadera. Cada fixture tiene exactamente un resultado.

**Resolución común, anterior a las tablas por objeto:**

| Orden | Condición | Resultado |
|---|---|---|
| C1 | No existe paquete activo aplicable o no puede establecerse su pertenencia inequívoca. | `desconocida`; `role=null`, `object=null`, `record=null`. |
| C2 | El request o los datos necesarios para identificar rol y objeto son ausentes, ilegibles o inconsistentes. | `desconocida`; no inferir el objeto ni el rol desde el historial. |
| C3 | Request aplicable con rol y objeto identificables. | Continuar con la tabla del objeto correspondiente. |

Las causas de request ausente, ilegible o inconsistente se incluyen en `reason` y `unknowns`.

**Objeto `draft-plan`:**

| Orden | Condición | Resultado |
|---|---|---|
| D1 | Objeto identificado como `draft-plan`. | `no requerida`; `record=null`; no buscar aprobación. |

No es necesario comprobar los bytes del borrador para establecer que su aprobación no se requiere. `contract` puede describirlo cuando sea verificable; su ilegibilidad no transforma este resultado en una aprobación ausente o cambiada.

**Objeto `feature-spec`:**

| Orden | Condición | Resultado y registro |
|---|---|---|
| S1 | No pueden leerse o interpretarse las fuentes necesarias de aprobación, la declaración del contrato o los bytes actuales del contrato. | `desconocida`; no afirmar ausencia ni vigencia. |
| S2 | Con fuentes legibles, no hay registros de aprobación para la feature. | `ausente`; `record=null`, aunque los bytes contradigan el digest declarado. |
| S3 | Hay registros de aprobación, pero ninguno no sustituido. | `sustituida`; primer registro sustituido, aunque los bytes hayan cambiado. |
| S4 | Hay registros no sustituidos, pero ninguno tiene pin coincidente. | `contrato cambiado`; primer registro no sustituido. |
| S5 | Existe pin coincidente, pero los bytes actuales no coinciden con el digest declarado. | `contrato cambiado`; primer registro no sustituido con pin coincidente. |
| S6 | Existe pin coincidente y los bytes actuales coinciden. | `vigente`; primer registro no sustituido con pin coincidente. |

S1 precede a ausencia y sustitución: la clasificación requiere las fuentes legibles indicadas, aunque otra condición pudiera conocerse parcialmente.

**Alcance de S3:** «ninguno no sustituido» se evalúa con el selector vigente, que recoge `supersedes` de cualquier entrada (`_superseded_transition_keys`) y excluye las aprobaciones cuyas claves aparezcan allí. Es alcanzable con una entrada no aprobatoria posterior que sustituya la clave de la única aprobación; el fixture describe el estado observado por el selector, no una secuencia válida del protocolo.

S2 y S3 preceden a las discrepancias: no hay resultados simultáneos «ausente y contrato cambiado» ni «sustituida y contrato cambiado». Las discrepancias adicionales comprobadas pueden explicarse en `reason`, sin cambiar el resultado normativo ni su registro.

**Objeto `epic-plan` para architect:**

| Orden | Condición | Resultado y registro |
|---|---|---|
| A1 | No pueden leerse o interpretarse las fuentes necesarias para seleccionar el mandato o comprobar el contrato del request. | `desconocida`. |
| A2 | Con fuentes legibles, `_approved_epic_plan_entry` no selecciona mandato. | `ausente`; `record=null`, incluso si los bytes del contrato contradicen su digest declarado. |
| A3 | Hay mandato, pero los bytes del contrato del request contradicen su digest declarado. | `contrato cambiado`; conservar el mandato seleccionado. |
| A4 | Hay mandato y los bytes del contrato del request coinciden. | `vigente`; mandato seleccionado. |

Para architect, `contract` describe el contrato del request, **no un pin del mandato del epic**. La discrepancia de pin del plan y el resultado `sustituida` no se aplican: introducirlos cambiaría el predicado existente.

#### Localizadores y determinismo

«Primero» significa primero en el orden real del historial correspondiente.

`record.index` es el índice 0-based, en el historial que determina `object`, del registro seleccionado: `stage_history` para `feature-spec` y `epic_history` para `epic-plan`. No se emite el nombre del historial ni el historial completo: el localizador no contiene el token del historial, de modo que se conserva la garantía PD-1 vigente (`"stage_history" not in stdout`) sin enmendar tests aprobados. `transition_key` puede ser `null` para registros históricos que no lo tengan.

Para `desconocida`, `record` solo puede conservar un registro si su selección ya pudo comprobarse independientemente de la fuente ilegible; en otro caso es `null`. Nunca se fabrica un localizador.

La vista es diagnóstico, no gate: un resultado distinto de `vigente` no modifica por sí solo `entry`, no registra transiciones y no altera el código de salida exitoso de una proyección válida.

### 2.4 Compatibilidad diagnóstica

Los diagnósticos anteriores de `unknowns` se conservan, con su contenido y orden relativo. Pueden añadirse causas concretas por:

- Pertenencia o identidad inconsistente del paquete.
- Request ausente, ilegible o inconsistente.
- Fuentes necesarias ilegibles que impiden resolver la referencia de aprobación.

No se exige texto estable para las causas nuevas. Sí se exige que identifiquen la fuente y la condición que impide resolverla. La extensión no habilita eliminar ni sustituir diagnósticos anteriores.

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
| PC-02 | Paquete preparado inequívoco indica `validate-packet`; despachado inequívoco indica `reconcile`; sus scripts y referencias existen. | `test_prepared_and_dispatched_operations` |
| PC-03 | Ejecución histórica cerrada no produce `execution-active` ni una aprobación vigente histórica. | `test_closed_execution_is_history` |
| PC-04 | La selección cumple todos los bindings mínimos de §2.1. Pendientes sin paquete inequívoco o con pertenencia inconsistente producen diagnóstico sin script ejecutable y explican su causa. Un paquete explícito válido no se vuelve ambiguo por otros directorios pendientes. | `test_unresolved_pending_work_is_not_dispatchable` parametrizado |
| PC-05 | Architect muestra el mandato real de `epic_history`, con `record.index` 0-based resoluble, sin exigir pin del plan; sin mandato y con fuentes legibles produce `ausente` conforme a la precedencia A1–A4. | `test_architect_approval_uses_epic_mandate` |
| PC-06 | Los resultados de aprobación de spec cumplen la tabla ordenada S1–S6 y cada fixture produce exactamente un resultado normativo; `record.index` apunta al registro seleccionado. | `test_spec_approval_status_matrix` |
| PC-07 | Un hash coincidente con ruta ajena y un contrato cuyos bytes cambiaron nunca producen `vigente`; ausencia o sustitución tienen la precedencia definida ante bytes cambiados. | `test_approval_checks_path_and_current_bytes` |
| PC-08 | `draft-plan` declara `no requerida` y no inventa registro, sin exigir comprobación de bytes para establecer la exención. | `test_draft_plan_requires_no_approval` |
| PC-09 | Request/contrato ilegible, ausencia de paquete y falta de registro se distinguen conforme a las tablas ordenadas de §2.3. | `test_approval_unknown_vs_absent` |
| PC-10 | Selección entre varios registros y sustituciones es determinista y coherente con los selectores de autorización existentes. | `test_approval_selection_and_supersession` |
| PC-11 | Se conservan campos y valores anteriores, excepto la extensión diagnóstica permitida de `unknowns`; `next.route` conserva la acción natural y su rama condicional. Se verifica por separado la compatibilidad estricta y la extensión diagnóstica. | `test_status_is_additive`, `test_status_preserves_and_extends_unknowns` y `tests/test_005_011_t3_view_action.py` |
| PC-12 | Ejecutar `status` no altera bytes del estado, requests, contratos, historiales ni checkpoints. | `test_status_is_read_only` |
| PC-13 | La salida sigue siendo un único JSON acotado; superar `--max-bytes` falla sin JSON parcial y con diagnóstico. Agregar historial no seleccionado no aumenta la salida. | `test_status_bound_and_history_independence` |
| PC-14 | El mapa documentado resuelve a scripts existentes y el cuerpo canónico del orquestador lo referencia; distingue ambos registros de despacho. | `test_orchestrator_references_operation_map` |

PC-04 incluye: `execution_id` ajeno, identidad del paquete discordante, feature discordante, rol/substage discordantes, request ilegible, ausencia de `active_packet` con uno o varios directorios pendientes, y selección explícita válida con otros directorios pendientes. Son variaciones de pertenencia y selección, no validación integral.

PC-06 incluye registros históricos sin `transition_key`, múltiples registros, `supersedes`, ausencia de aprobación, todos los registros sustituidos y discrepancias de pin o bytes. Debe incluir las combinaciones bytes cambiados + sin registros y bytes cambiados + todos sustituidos.

PC-11 se verifica en dos grupos:

1. **Compatibilidad estricta:** en fixtures sin las condiciones que añaden diagnósticos conforme a §2.4, eliminar exclusivamente `situation`, `next.operation` y `authority.approval_reference` debe recuperar la proyección antigua completa.
2. **Extensión diagnóstica:** en fixtures con esas condiciones, al eliminar las tres adiciones todos los campos anteriores salvo `unknowns` deben coincidir exactamente. `unknowns` debe conservar todos los diagnósticos anteriores y su orden relativo, y añadir las causas nuevas requeridas. Se comprueba la extensión por separado, sin exigir igualdad de la lista completa con la antigua.

## 5. Invariantes verificables

1. **Compatibilidad:** no eliminar, renombrar ni reinterpretar campos anteriores; `entry` conserva su mapa existente. `unknowns` admite únicamente la extensión diagnóstica descrita.
2. **Autoridad única:** la vista reutiliza los criterios de aprobación existentes; no escribe aprobaciones ni autoriza operaciones.
3. **Sin efectos:** ninguna orientación dispara preparación, continuidad, transporte o recepción.
4. **Evidencia honesta:** desconocido no equivale a ausente; disponer de un registro no prueba que los bytes actuales estén aprobados.
5. **Resultado único:** cada referencia de aprobación tiene un solo resultado, determinado por la primera fila aplicable de su tabla.
6. **Acotación:** límite predeterminado existente de 16.384 bytes; no volcar historiales o contratos.
7. **Sin mecanismos paralelos:** ningún almacenamiento o registro nuevo de intentos, disposición o continuidad.
8. **Propietario documental único:** mapa en orientación; orquestador y derivados por referencia/generación.

## 6. Decisiones de diseño

- **Localizador por índice frente a JSON Pointer (2026-10-23, post-GREEN):** el pointer exigido por §2.3 emitía el token `stage_history`, que la garantía PD-1 (vigente en `tests/test_005_003_t1_compact_view.py:228,325`) prohíbe en la salida. El índice 0-based con historial determinado por `object` localiza igual sin emitir el token, sin relajar ninguna garantía y sin enmendar tests aprobados.

- **Ampliación frente a reemplazo de `entry`:** se elige ampliación por compatibilidad con consumidores y pruebas existentes.
- **Una operación inicial frente a una fachada de despacho:** se proyecta el primer paso verificable y se referencia el protocolo; evita esconder varios efectos bajo un verbo nuevo.
- **Referencia común frente a una aprobación genérica:** una estructura común expresa objetos distintos, pero conserva las reglas específicas de mandato del architect y pin de spec.
- **Diagnóstico frente a inferencia de entregas:** ante pendientes ambiguos se informa el límite. 007-001 no interpreta señales de terminación cuya corrección pertenece a 002–004.
- **Bindings mínimos frente a validación integral:** se comprueba identidad y pertenencia para orientar sin convertir `status` en un gate duplicado.
- **Selección explícita frente a conteo global de directorios:** `active_packet` válido identifica el paquete actual; los demás directorios no anulan esa evidencia.
- **Decisión ordenada frente a etiquetas simultáneas:** la ilegibilidad precede al juicio de aprobación; ausencia y sustitución preceden a discrepancias. Así se obtiene un resultado único sin alterar los predicados de autorización.

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
- `…/cdad_packet.py:1200-1207`: bindings de identidad, rol y substage entre estado y request; comprobaciones adicionales de validación que esta vista no duplica integralmente.
- `…/cdad_packet.py:6643-6751`: ejecución activa, pertenencia por ejecución, recibos, pendientes, selección de entrada y rutas.
- `…/cdad_packet.py:6767-6891`: proyección, aprobación actual y límite.
- `sources/roles/orchestrator.md:28-48,137-176`: árbol de entrada y wiring.
- `skills/cdad-cycle/references/orientation.md:14-38,65-74`: orientación y operaciones.
- `tests/test_005_011_t3_view_action.py:452-525`: compatibilidad de preparados y despachados.
- `docs/specs/007-001-unambiguous-entry/discovery.md:45-50`: decisiones del orquestador que confirman evolución aditiva y referencia de aprobación por rol/objeto.
