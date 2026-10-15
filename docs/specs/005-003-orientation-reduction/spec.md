> Spec **APROBADA (2026-10-12, ronda draft-003)**, texto del **architect** (subetapa `draft`,
> etapa 2), materializado por el orquestador (ADR-003) **sin cambios de contenido** y aprobado por el
> orquestador OpenCode bajo la delegación HITL del epic-005; el architect **no** aprobó su propia
> propuesta (anti-sesgo). Sustituye al texto del draft 002 (aprobado en
> `009902b`) **conservando íntegro todo lo demás** y aplicando **solo** los seis ajustes A1–A6
> pedidos por el dueño tras la revisión entre tramos del orquestador Claude
> (`review-claude-spec-2026-10-12.md`). El orquestador re-materializa con CAS y **re-aprueba**;
> el architect **no** aprueba su propia propuesta (anti-sesgo).
> **Contrato vigente:** `docs/epics/epic-005-real-operation/plan.md`, **fila 8 ENMENDADA Y
> APROBADA** (commit `5b912aa`; sha256 `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`;
> fila en `:41`, cambio en `:140-146`) **más** la sección «Ajuste de los ciclos pendientes —
> decisión del dueño, 2026-10-11» (`:45-85`), que **prevalece** sobre una lectura más estrecha de
> la fila. **La fila enmendada se cita como contrato vigente: no se propone otra enmienda.**
> Insumos obligatorios del dueño: `discovery-inputs.md` y el delta `discovery-inputs-2026-10-12.md`.
> Insumo verificado e **intacto**: `discovery.md` (aprobado por el gate de etapa 1) y su línea base
> medida `evidence/baseline-meter-2026-10-12.md`; **no se repiten ni se reescriben**. Dirección de
> fondo: `findings/agent-operation-strategy-2026-10-11.md`. **Sin valores de este VPS** en spec,
> plan ni producto: la prohibición cubre **rutas del host, ruta del store, nombres de proveedor y
> de modelo, servidor e identificadores crudos de sesión**; las magnitudes ya publicadas en la
> línea base y en el discovery se citan **por referencia**, sin agregar valores nuevos (INV-6).

# Spec — 005-003-orientation-reduction

**Feature ID:** `005-003-orientation-reduction` · **Epic:** `epic-005-real-operation` ·
**Estado:** borrador (2026-10-12; ronda acotada draft-003, pendiente de re-aprobación).

```yaml
feature_id: 005-003-orientation-reduction
feature_name: Orientación al retomar y arranque desde reposo con contexto acotado
created_at: 2026-10-12
status: approved
approved_by: orquestador OpenCode (HITL delegada epic-005)
approved_at: 2026-10-12
```

## 1. Descripción funcional

El resultado es una **orientación acotada al primer despacho legítimo**: el orquestador llega a la
próxima unidad de trabajo con **contexto chico** y **sin reconstruir preventivamente** ni la historia
del proyecto ni la implementación del CLI, conservando **autoridad, contratos, evidencia y capacidad
de orquestar durante horas**. La mejora se apoya en cuatro piezas, todas **generadas por código a
partir de fuentes existentes** y **sin otra memoria que sincronizar a mano**:

1. una **vista compacta del estado operativo** (proyección, no migración del formato del estado);
2. una **selección explícita de entrada** que **atiende un paquete pendiente** antes que cualquier
   inferencia de etapa;
3. una **interfaz operativa suficiente** para las operaciones frecuentes, con **ejemplos que se
   ejecutan** contra la versión correspondiente;
4. la **disposición de versión y del medidor** (incluido el caso «medidor no instalado») y el
   **resumen del conjunto** para corridas multi-sesión, con la evidencia mecánica capturada de forma
   fiable.

**Dos elementos más, declarados por la fila 8 enmendada** (no amplían el alcance de las cuatro
piezas anteriores; los asigna el contrato vigente a esta feature):

5. el **contrato aplicable del encargo**: cada paquete de una tarea **trae los comandos de
   validación de su tarea** tomados del bloque canónico `plan-tasks` del plan aprobado, **cuándo
   ampliarla** y las **postcondiciones, invariantes y decisiones aplicables** con referencias al
   contrato completo, de modo que **no sea obligatorio releer la spec entera** para ejecutar el
   encargo; el **cierre del encargo incluye el commit** y el reporte del rol lo declara (§2.8);
6. el **cierre dentro de la feature** de **D11** y **R4** (deuda de 005-002) **antes** de usar la
   integración real y las corridas multi-sesión como gate (§2.6, §3 PD-12, INV-8).

**Frontera de la mejora (no negociable).** Menos preparación **no** habilita: omitir gates, ocultar
bloqueos, declarar válido un contrato cambiado, ni delegar un encargo insuficientemente definido. Un
primer despacho más rápido es **señal**, no aceptación (la aceptación usa una próxima sesión real).

## 2. Contrato observable

### 2.1 Vista compacta del estado operativo (`compact-view-v1`)

Una **proyección generada por código** sobre las fuentes **ya existentes** (no una reescritura del
formato del estado ni una segunda memoria): `docs/.cdad-state.json` **solo en sus campos operativos**,
`.cdad/executions/<id>/execution.json`, `.cdad/packets/<id>/REQUEST.json` + `active_packet`,
`docs/cdad-policy.json`, el `cdad-version-check.py` **instalado** (versión) y la proyección de
continuidad para la ruta siguiente.

- **Forma elegida (D-4: la spec fija la superficie y elige la forma).** Un **subcomando read-only
  nuevo** de `cdad_packet.py` (el CLI de paquetes ya conoce el estado y las aprobaciones), de nombre
  fijado **`status`**:
  `python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>`.
- **Salida.** Un **único documento JSON** por stdout con, como mínimo, los campos:
  `project` (raíz reconocida; marcadores de feature/plan presentes/ausentes) · `epic`
  (`active_epic`, `epic_stage`) · `feature` (`active_feature`, `current_stage`, `tdd_substage`) ·
  `execution` (`id`, `authority_ref`, `model_policy`, `policy_sha256`) · `packet`
  (`{id, role, substage, status}` o `null`) · `authority` (`hitl_delegation.status`, `approver`, y la
  entrada de aprobación que habilita al rol, **por referencia**) · `version` (verdicto, §2.4) ·
  `next` (ruta operativa siguiente, con su **fuente declarada**) · `entry` (selección, §2.2) ·
  `unknowns[]` (causas de lo no proyectable, **nunca 0**).
- **Garantías.** (i) generada por código desde las fuentes existentes; (ii) **el historial
  (`stage_history`) NO se emite** — se consulta selectivamente ante una duda concreta; (iii)
  **acotada por un límite de bytes normativo** (ver *Límite declarado*); (iv) **read-only**: no
  escribe el estado ni ningún archivo; (v) determinista (misma entrada → mismos bytes).
- **Límite declarado (C1).** El documento de la vista **no supera 16.384 B (16 KiB)**: el mismo
  número ya normativo en el repo para el documento de **una sesión** (`context-meter.md:243`) y el
  default de `--max-bytes` de continuidad (`continuity.md:59-60`; `cdad_continuity.py:55,638-640`).
  **Al superarlo, la vista falla cerrado** (`rc != 0`) **sin emitir una proyección parcial**, con un
  diagnóstico que **nombra la causa** (el límite) y **el camino legítimo** para obtener más: la
  bandera `--max-bytes N` (default 16.384, como en continuidad, `cdad_continuity.py:1306,1323`) o
  **consultar la fuente concreta por referencia**. El límite **NO crece con el historial** (la vista
  no emite `stage_history`, garantía (ii)) y es **el mismo para cualquier tamaño de estado**: la
  proyección es función de los campos operativos declarados, no del tamaño del estado.
- **Dato de magnitud (citado por referencia, no re-medido).** La proyección de continuidad ya emite
  `goal / autoridad vigente / decisions / uncertainties / next_action` en **5.030 B** con
  `--max-bytes` de 16 KiB; el estado medido en la línea base es **320.880 B** y su `stage_history` el
  **94,8 %**. La reducción es de **dos órdenes de magnitud** y es **medible por inspección del
  artefacto** (la proyección no incluye el historial; el historial crece, la proyección no).

### 2.2 Selección explícita de entrada (mapa)

La selección es un **mapa explícito** sobre la proyección de §2.1 — **no** una inferencia por
`current_stage` ni por la palabra «inicializar». El campo `entry` de la vista emite una de
`continuity-reconcile` | `next-unit` | `diagnosis`:

| Condición observada | `entry` |
|---|---|
| `active_packet.status ∈ {prepared, dispatched}` **o** trabajo pendiente | `continuity-reconcile` (si el contrato cambió, `--replace-packet`; si está despachado, reconciliar antes de repetir) |
| Ejecución activa, sin paquete pendiente | `continuity-reconcile` (resume) y la siguiente unidad de esa ejecución |
| Reposo sin trabajo pendiente | `next-unit` (procedimiento existente, `project-start.md` §6-§7) |
| Configuración incompleta (sin `docs/cdad-policy.json`, autoridad sin pin) | `diagnosis` (marcadores `approval pending`/`state incoherent` **por referencia**, `project-start.md` §8) |

- **Caso real que prueba el riesgo.** Hoy `current_stage=discovery` **y** `active_packet.status=prepared`.
  Una inferencia ingenua («está en discovery, no hay nada activo») perdería un paquete ya preparado;
  la condición de la tabla lo evita **por construcción**.
- **«Trabajo pendiente» sin campo nuevo.** Se apoya en campos y directorios **existentes**
  (`active_packet.status`, `current_stage`, `postconditions_status`, `execution`; y, cuando
  `active_packet` está ausente, los sub-directorios `.cdad/packets/<id>/` con estado distinto de
  `completed`). **No se agrega un campo nuevo al estado** (INV-2).
- **Reposo e historia (enmienda F2, aprobada por el dueño el 2026-10-13).** Una ejecución es
  **activa** solo si `active_feature` no es nulo y `execution.feature_id` coincide con él; el bloque
  `execution` que queda en el state después de cerrar una feature es historia. Con
  `active_feature` nulo y `active_packet` ausente, los directorios de `.cdad/packets/` son historia y
  la vista emite `next-unit`. Un directorio cuenta como trabajo pendiente solo si su `REQUEST.json`
  pertenece a la ejecución activa y no tiene recibo en
  `.cdad/runtime/results/<execution_id>/<packet_id>/`.
- **`resume` no es la entrada desde reposo.** `resume` es para una ejecución activa
  (`project-start.md:134-138`); sin checkpoint devuelve una proyección vacía `no-checkpoint` con
  `rc=0`. Por eso la selección es **explícita y previa**, no delegada a `resume`.

### 2.3 Interfaz operativa suficiente

Una **referencia corta** (`skills/cdad-cycle/references/orientation.md`) que expone, para `prepare`
(y sus sub-modos), la validación (`validate-state`/`validate-request`/`validate-packet`), `begin`
(continuidad) y el **registro de despacho** (`--record-dispatch` + `docs/attempt.json`): cuándo
usarlos, **argumentos requeridos**, **defaults relevantes**, **efectos** y un **ejemplo mínimo válido
de sus archivos de entrada**. Reusa esquemas y constantes existentes (`packet-request.schema.json`,
`execution-context.schema.json`, `state-template.json`, el documento de observaciones del registro de
despacho, el `UPDATE` de continuidad). **Sin** otro manual extenso mantenido a mano y **sin**
generador de documentación.

- **Ejemplos ejecutables (C3).** Los ejemplos mínimos válidos viven en un **asset canónico declarado
  por la spec**: `skills/cdad-cycle/assets/orientation-examples.json` (JSON; un array `examples[]`
  con `id`, `kind`, `target` y el `input`/la `command` del ejemplo). El test los **localiza por el
  asset** (su ruta declarada), **nunca por prosa** de Markdown. La referencia `orientation.md`
  **cita** el asset (no duplica los ejemplos).
- **Conjunto mínimo exigido (C3)** — al menos: (1) el **archivo de entrada del registro de despacho**
  (`docs/attempt.json`, campos exactos `runtime, model_configured, model_reported, session, started_at`
  + `provenance`; `project-execution.md:113-116`); (2) el **`UPDATE` de continuidad**
  (`goal/decisions/uncertainties/next_action` + `budget` opcional; `continuity.md:17,33`); y (3) una
  **invocación válida de la vista de §2.1** (`cdad_packet.py status --project-root <ABS>`).
- **Qué afirma el test (PD-3).** Cada ejemplo se **EJECUTA** contra la **versión correspondiente** (el
  CLI de la versión cargada, no una copia del checkout) y **un ejemplo inválido falla con el
  diagnóstico que NOMBRA el campo** (p. ej. un `attempt.json` sin `runtime`). La utilidad **no** se
  verifica buscando frases en Markdown.

### 2.4 Disposición de versión y del medidor

- Reusar el **`cdad-version-check.py` instalado** (no el del checkout, que reporta `UNKNOWN`).
- **Distinguir AUSENCIA de INCOHERENCIA**: `UNKNOWN`(rc 3) y `NO-PROJECT-AGENTS`(rc 4) son *ausencia*
  (versión **no** verificada); `DRIFT`(rc 1) es *incoherencia*. Cualquier rc ≠ 0 se lee como «no
  verificado coherente», nunca como ok.
- **Republicar** por el camino legítimo (`prepare` y derivados) y **verificar después**; no duplicar
  inspecciones de manifiestos/marcadores sin una contradicción nueva.
- **Límite declarado:** la coincidencia de archivos **no** demuestra lo cargado por una sesión
  abierta.
- **Caso «medidor no instalado».** El medidor de 005-002 está **ausente** de las skills instaladas;
  se trata como **ausencia**, distinta de incoherencia, **no** como `DRIFT`. Mientras no esté
  instalado, la medición se hace con el **artefacto del repo en solo lectura**; **el despliegue es
  del dueño** y queda fuera de esta feature. Si el gate exige el medidor instalado, eso es un
  **bloqueo declarado**, no un atajo.

### 2.5 Evidencia mecánica fiable

- **Capturar el retorno REAL del CLI sin enmascararlo**: no leer el `rc` a través de una tubería
  (`head`/`tail`) que lo sustituye por el del último comando; usar `PIPESTATUS`/`set -o pipefail` o
  ejecutar sin tubería y acotar por separado.
- **Salida acotada para el contexto, evidencia completa disponible** por referencia.
- **Errores accionables** con el formato esperado (`ERROR: …`) y recuperación legítima; **no**
  ampliar alcances, fabricar aprobaciones ni borrar registros.
- **Dónde vive el patrón (C4).** El patrón de captura vive en la **referencia operativa de §2.3**
  (`skills/cdad-cycle/references/orientation.md`); la spec **exige** que la asimetría de raíz relativa
  se **DIAGNOSTIQUE en la salida de la vista** — un **campo o una causa** que **nombre la asimetría
  entre CLIs**, no solo en prosa. Es **comportamiento de producto** (la vista de §2.1 lo emite), por
  eso lo afirma el test de la vista (T1); **no** queda como comprobación observada.
- **Asimetría de raíz relativa (hecho verificado).** El rechazo de raíz relativa es **específico de
  `cdad_packet.py`** (`cdad_packet.py:663-666`, `_absolute_existing_directory`, invocado **antes** del
  dispatch del subcomando en `main`, `:3635-3636`; `ERROR: --project-root must be an absolute existing
  directory: .`, `rc=2`, en `validate-state` **y** `prepare`); `cdad_continuity.py resume --project-root
  .` da `rc=0` y `cdad_result.py` resuelve la raíz relativa contra el cwd. La vista y la interfaz
  **diagnostican** esa asimetría (la causa nombra ambos CLIs y el camino de recuperación: usar una raíz
  absoluta) en vez de ocultarla.
- **Qué afirma el test (C4).** Que el **`rc` capturado es el del CLI real** (no el de la tubería:
  `PIPESTATUS[0]`, no `$?`) y que el **error accionable nombra la causa y el camino de recuperación**.

### 2.6 Resumen del conjunto (multi-sesión) y regla del documento multiplexado

- **Resumen primero.** Para una corrida **multi-sesión**, el consumidor recibe **primero un resumen
  del conjunto**: **sesiones incluidas, cobertura, hitos, magnitudes relevantes y referencias al
  detalle**. El **detalle por sesión sale solo a pedido**. **No es un dashboard** ni una segunda
  memoria.
- **Transporte (V1, DECIDIDO por el orquestador).** El resumen va en un **DOCUMENTO ADITIVO
  SEPARADO** (contrato `set-summary-v1`), emitido para corridas multi-sesión. **No** reescribe el
  registro neutral **por sesión** de 005-002, ni su asset (`context-meter.schema.json`,
  `additionalProperties: false`, sin clave de resumen de corrida), ni su semántica, ni los flags
  existentes (INV-5): el registro por sesión queda **byte-congelado**.
- **Conjunto mínimo de claves del resumen (C2).** El documento del resumen declara, como mínimo:
  - `meter` (const `set-summary-v1`): declara el contrato del resumen.
  - `run` (`{store_ref, runtime_version, schema}`): la corrida — referencia **hasheada** del store
    (nunca ruta absoluta), versión de runtime observada y si el esquema fue reconocido; misma forma
    que el `run` del registro neutral (`context-meter.schema.json:26-45`).
  - `sessions_included` (array de `session_ref` hasheadas): **qué sesiones incluye** el conjunto
    (referencias, no identificadores crudos).
  - `coverage` (`{sessions_reporting, sessions_total, cause}`): **cobertura declarada** del conjunto —
    un subconjunto **nunca** se presenta como el conjunto.
  - `milestones` (`{first_resume, first_dispatch}`, cada uno `{status, position?, time_relative?,
    cause?}`): **hitos del conjunto**; misma forma que `$defs/milestone` del registro neutral
    (`context-meter.schema.json:114-148`).
  - `magnitudes` (objeto de entradas declaradas `{value, unit, bucket, sessions_reporting,
    sessions_total, cause}`): **magnitudes relevantes del conjunto** con su **cubo** y su
    **cobertura**; una magnitud sin cobertura total es `unknown` con `cause` y `value: null` —
    **nunca un subtotal parcial presentado como total** y **nunca `0`** (misma forma que
    `$defs/role_aggregate_entry`, `context-meter.schema.json:352-402`).
  - `detail_ref` (referencias): **referencias al detalle por sesión** (referencias hasheadas /
    documento), no el detalle.
  - `detail_flag` (string): el nombre de la bandera que restaura el detalle por sesión.
  - `unknowns[]`: causas explícitas de lo no observable.
- **Detalle por sesión (C2).** El **detalle por sesión NO se emite por defecto**; se pide con la
  bandera declarada en `detail_flag` (fijada: `--detail`), siguiendo el patrón ya existente de
  `truncated.detail_flag` (`context-meter.schema.json:241-245`). **No es un dashboard** ni una segunda
  memoria.
- **Regla del documento multiplexado (R4/V3).** `context-meter.md` publica hoy el límite de
  **16.384 B POR DOCUMENTO DE SESIÓN** (`context-meter.md:243`) y **no** la regla del total. La regla
  se declara en el reference **en T3** (entregable de la feature, INV-8) **antes** de que esta feature
  consuma corridas multi-sesión, y contiene **dos elementos afirmables** (C5/V3): **(a)** **el total
  es ≤ N × el límite por sesión** y **(b)** **el límite normativo es POR DOCUMENTO DE SESIÓN**. La
  redacción exacta es del implementer de T3 (V3), pero ambos elementos son el contrato a afirmar
  (medición citada de la línea base: ~113 KB para 13 sesiones y ~135 KB para 14; media ~8,7 KB por
  sesión). **R4 se cierra dentro de la feature (T3)**, antes del consumo multi-sesión.

### 2.7 Capacidades efectivas y fallback portable

Un **inventario corto ligado a versión/configuración** de cómo el orquestador encuentra capacidades
**existentes** para presentar planes, archivos, previews y diffs, con **fallback portable por
archivos o enlaces** (mínimo ya posible). **OpenChamber** es un **consumidor verificado** en su
instalación y su mecanismo de acceso (CLI en PATH; servidor vivo y HTTP 200), pero su **contrato
estable agente↔superficie** para notas/previews/diffs **NO está verificado**: una integración
compleja de UI es **propuesta posterior** y **no** se compromete aquí. **No** se implementa
OpenChamber ni OnlyOffice; **no** se crea fuente de estado.

### 2.8 Contrato aplicable del encargo (A2 — fila 8 enmendada)

El **paquete de un encargo de una tarea** del plan aprobado **trae su propio contrato de ejecución**,
generado por código y **no** escrito a mano por el preparador. Fuente normativa: la fila 8 enmendada
(`plan.md:41`, «Cada encargo trae los comandos de validación de su tarea, cuándo ampliarla, y las
postcondiciones, invariantes y decisiones aplicables, con referencias al contrato completo»).

- **Alcance.** Aplica a los paquetes de un **encargo de tarea** (una unidad del plan de la feature).
  Para el contrato `approved-epic-plan` del **architect** no hay bloque de tareas: la extensión **no
  aplica y no debe fallar** (la derivación de contratos es la vigente, `cdad_packet.py:974-987`).
- **Selección explícita de la tarea (forma fijada).** El paquete **declara su tarea** con una opción
  **aditiva y declarada** de `prepare` (`--plan-task <TASK_ID>`) y el `REQUEST.json` lleva el campo
  **opcional** `plan_task`; sin él, el paquete se emite como hoy (byte-idéntico). La selección es
  **explícita**, nunca inferida de la prosa del objetivo.
- **(a) Comandos de validación de la tarea, tomados del bloque canónico.** Con la tarea declarada, el
  paquete emite una **sección declarada** (`## Task validation plan`) cuyos valores son **iguales** a
  los que el bloque canónico `plan-tasks` del plan aprobado declara para esa tarea:
  `focal_tests` / `observable_checks` / `regressions` / `integration_gate`, con el literal
  `@validation_strategy` **resuelto** contra el `validation_strategy` a nivel de plan. La sección
  **dice cuándo ampliar la validación**: el paquete emite la regla de ampliación derivada del
  `integration_gate`/`regressions` declarados y de la estrategia común (una corrección local usa
  focales; un contrato compartido o de impacto incierto amplía — `re-entry.md:77`), sin completar los
  valores a mano.
  - **Qué afirma el test (provenance).** Que los valores emitidos **coinciden exactamente** con los
    parseados del bloque canónico (mismo lector que usa el CLI, `cdad_packet.py:2856-2915`) y que
    **una tarea ausente del bloque falla cerrado nombrando el id**, de modo que la sección **no puede
    satisfacerse con texto escrito a mano**. El paquete declara además la **procedencia** del plan
    (path + `sha256`), como ya hace con sus instrucciones (`cdad_packet.py:888-891`).
- **(b) Postcondiciones, invariantes y decisiones aplicables, con referencias al contrato.** El
  paquete emite una **sección declarada** (`## Applicable contract`) con las **referencias al
  contrato completo** que el encargo declara para su unidad (ids de sección: PD/INV/D) más la
  referencia del contrato (path + `sha256`, ya presente en `## Contract`). Los **invariantes** del
  encargo siguen en el campo existente `invariants`. Con eso, **no es obligatorio releer la spec
  entera** para ejecutar el encargo.
  - **Qué afirma el test.** Que **cada id emitido resuelve a un encabezado del contrato** (pertenencia
    de conjunto, mecánica) y que la referencia del contrato (path + `sha256`) coincide con la del
    paquete. **Límite honesto:** la spec **no** afirma que el paquete derive la aplicabilidad
    automáticamente; el conjunto aplicable lo declara el encargo (su fuente humana es la ficha de la
    tarea en el plan) y el paquete lo **rinde por referencia**.
- **(c) La suite completa no se corre salvo que el paquete lo pida.** La **instrucción que el paquete
  emite** (bloque `<!-- cdad-instructions -->`, compuesto por `packets/common.md` +
  `packets/roles/<role>.md` + `packets/substages/<role>-<substage>.md`, `cdad_packet.py:850-857`)
  **declara**, en su parte común, que la **suite completa NO se corre salvo que el paquete lo pida**
  y que **la corre quien cierra**; y **ninguna** instrucción de rol o de subetapa afirma lo contrario
  (hoy `packets/roles/implementer.md:1` y `packets/substages/implementer-green.md:1` dicen «the
  complete suite is the closure gate» y se corrigen).
  - **Qué afirma el test.** Que el bloque de instrucción del paquete (sus **tres fuentes declaradas**
    en `instruction_sources`, con sus hashes) contiene la declaración y que ningún asset de
    `packets/roles/**` ni `packets/substages/**` la contradice. La declaración vive **una sola vez**
    (regla del repo: se referencia, no se copia).
- **(d) El cierre del encargo incluye el commit.** El paquete exige la evidencia de cierre con el
  **commit** (el default ya lo incluye: `DEFAULT_EVIDENCE = [… "commit"]`, `cdad_packet.py:970`) y la
  instrucción de cierre **declara el commit** como parte de la entrega; el reporte del rol lo declara.
  **Límite honesto:** no hay gate automático que lo fuerce; la verificación sistemática es la
  **auditoría del orquestador** (diff contra `write_scope`) y la **observación de la aceptación**
  (§5 A8/A10): un rol que termina **sin commitear** es un **bloqueo declarado** registrado en el
  informe, nunca aceptado en silencio.
- **Frontera de la extensión (declarada).** La extensión es **aditiva**: (i) **no** cambia los campos
  obligatorios ni la semántica de los paquetes de 005-001/005-005; (ii) un paquete sin `plan_task`
  sigue emitiéndose **byte-idéntico**; (iii) el conjunto cerrado de campos del request
  (`cdad_packet.py:741-745`) y el del contrato (`:756-761`) se **extienden** con la propiedad
  opcional **declarada** (no se relaja el cierre: una clave desconocida sigue rechazándose); (iv) la
  **sustitución** (`--replace-packet`) **conserva** la tarea declarada y **re-resuelve** el contenido
  de validación desde el plan vigente (el contrato se re-resuelve, nunca se conserva). **No** se
  cambia el tamaño de unidad ni la preparación de encargos de 005-007 (INV-4).

### 2.9 Arranque y reentrada: la vista primero (A3 — fila 8 enmendada)

El **procedimiento canónico de arranque y reentrada del orquestador** (`project-start.md` y, si
corresponde, `project-execution.md`/`continuity.md`) **consulta primero la vista `status`** de §2.1 y
**amplía solo ante una necesidad concreta** (un bloqueo, una duda que afecte al siguiente despacho),
**sin reconstruir el estado ni el CLI por defecto**. Sigue siendo **el mismo procedimiento** de
005-006 (INV-3): se le agrega el paso de orientación por la vista, **por referencia** al dueño
canónico, sin copiar su estructura (la regresión de 005-006 lo prohíbe,
`tests/test_005_006_t1_start_procedure.py:58`).

- **Qué se observa (y cómo se registra).** La aceptación (§5) observa el **recorrido de una sesión
  nueva** y lo registra en el informe de T5: **(i)** si la **primera acción de orientación** de la
  sesión fue la vista `status`; **(ii)** las **ampliaciones** realizadas y su **motivo** (bloqueo o
  duda concreta); **(iii)** el **resultado** (primer despacho legítimo alcanzado, o bloqueo
  declarado). La sesión se registra por **referencia hasheada**; lo no observable queda `unknown` con
  causa.
- **Límite honesto (no es una garantía).** La spec **no** afirma que la vista se consulte siempre —
  eso depende de la voluntad del modelo y del recorrido real. Lo que fija es el **comportamiento del
  procedimiento** (la vista primero; ampliar con motivo) y **qué evidencia se observa y se registra**;
  la aceptación la juzga el orquestador con ese registro, sin convertirla en un umbral automático.

## 3. Postcondiciones (numeradas y verificables)

**PD-1 (vista compacta acotada por un límite normativo de bytes, generada por código).** La vista
(`status`) emite la proyección con los campos de §2.1, **generada por código desde las fuentes
existentes**, **sin emitir `stage_history`** y **acotada a 16.384 B (16 KiB)**; **al superarlo falla
cerrado** (`rc != 0`) **sin emitir una proyección parcial**, con un diagnóstico que **nombra el
límite** y la bandera/camino legítimo para obtener más; **read-only** (el estado queda byte-idéntico).
El límite **no crece con el historial** y es **el mismo para cualquier tamaño de estado**. Borde: un
proyecto fixture con historial grande sigue dando una vista ≤ el límite (el historial no se emite);
un fixture cuyo documento exceda el límite falla cerrado sin proyección parcial; la proyección
**surfacea** `active_packet.status`.

**PD-2 (la selección atiende el paquete pendiente; no depende de «inicializar»).** Con
`current_stage=discovery` **y** `active_packet.status=prepared`, `entry=continuity-reconcile` (no
`next-unit`); reposo sin pendiente → `next-unit`; configuración incompleta → `diagnosis`; la
selección **no** depende del literal «inicializar». Borde: `dispatched` → reconciliar antes de
repetir. **Reposo con historia (F2):** `active_feature` nulo, `active_packet` ausente, el bloque
`execution` de una feature cerrada y directorios de paquete históricos con y sin recibo →
`entry=next-unit`; el `next` no apunta a la ejecución cerrada.

**PD-3 (los ejemplos se EJECUTAN; localizados por el asset, nunca por prosa).** Los ejemplos mínimos
de la interfaz operativa viven en el **asset canónico**
`skills/cdad-cycle/assets/orientation-examples.json`; el test los **localiza por el asset** (su ruta
declarada), **nunca por prosa**. El **conjunto mínimo** (archivo de entrada del registro de despacho,
`UPDATE` de continuidad, invocación válida de la vista de §2.1) se **EJECUTA** contra la **versión
correspondiente** (no se verifica utilidad buscando frases en Markdown). Borde: un ejemplo inválido
falla con el diagnóstico que **nombra el campo**.

**PD-4 (versión: ausencia ≠ incoherencia; «medidor ausente» explícito).** El verdicto reusa el
`cdad-version-check.py` instalado; `UNKNOWN`/`NO-PROJECT-AGENTS` (ausencia) se distingue de `DRIFT`
(incoherencia); el caso «medidor no instalado» se declara **ausencia**, no `DRIFT`; republicar por el
camino legítimo y verificar después; se declara el límite «coincidencia de archivos ≠ sesión
abierta». Borde: sin marcador → ausencia; con versiones divergentes → `DRIFT`.

**PD-5 (retorno real capturado; error accionable; asimetría diagnosticada en la salida).** El patrón
de evidencia vive en la referencia operativa de §2.3 (`orientation.md`) y captura el `rc` real sin
tubería que lo enmascare (`PIPESTATUS[0]`, no `$?`); salida acotada con evidencia completa por
referencia; errores con formato `ERROR: …` y recuperación legítima. La **asimetría de raíz relativa**
entre CLIs se **diagnostica en la salida de la vista** (un campo o una causa que **nombra la
asimetría** y el camino de recuperación), **no solo en prosa**: es **comportamiento de producto**.
Borde: una reproducción muestra el `rc` real (2) pese a la tubería, y el error accionable **nombra la
causa y la recuperación**.

**PD-6 (resumen del conjunto + regla del documento multiplexado, cerrada en T3).** Para corridas
multi-sesión se emite **primero** el resumen en un **documento aditivo separado** (`set-summary-v1`,
V1 decidido) con el **conjunto mínimo de claves** de §2.6 (sesiones incluidas, cobertura, hitos,
magnitudes con cubo y cobertura, referencias al detalle); el **detalle por sesión NO se emite por
defecto** y se pide con la bandera declarada (`detail_flag`); el registro neutral por sesión de
005-002 queda **byte-congelado**. La regla del documento multiplexado está declarada en
`context-meter.md` **antes** del primer consumo multi-sesión — es un **entregable de T3** (INV-8) — y
contiene los **dos elementos** (total ≤ N × límite por sesión; límite normativo **por documento de
sesión**). Borde: si por cualquier motivo la regla no estuviera declarada, el consumo multi-sesión se
**bloquea** declarándolo; un resumen sin cobertura total no presenta un subtotal parcial como total.

**PD-7 (no-regresión de los contratos de 005-002).** El medidor, su superficie de invocación y su
registro neutral se **citan**; la **extensión del hito «primera acción del encargo»** queda como
**PROPUESTA al dueño**, no asumida ni plegada al alcance comprometido; el comportamiento existente
(registro neutral por sesión, flags, cubos, privacidad) **no** cambia. Borde: los tests de 005-002
siguen verdes.

**PD-8 (ejecuciones redundantes declaradas).** Las corridas de suite fuera del cierre y los gates
re-ejecutados se **declaran** en el ledger/evidencia del paquete; la **fidelidad** se verifica por
**procedencia + equivalencia** (regla canónica en `re-entry.md`, sección *Equivalence of a registered
run*); el cierre corre la suite **una vez**; el medidor **no** lee comandos (privacidad). Borde: el
cierre declara una sola corrida de suite.

**PD-9 (capacidades efectivas + fallback portable).** El inventario declara cada capacidad como
observada/documentada/no disponible/desconocida, ligada a versión/configuración, con el fallback
portable demostrado y **sin** prometer el contrato agente↔OpenChamber. Borde: sin la UI, el camino
agente → artefacto → revisión por archivos/enlaces funciona.

**PD-10 (contrato aplicable del encargo — A2).** El paquete de un encargo de tarea: **(i)** declara su
tarea de forma explícita (opción aditiva `--plan-task <ID>`; campo opcional `plan_task`) y, sin ella,
se emite byte-idéntico; **(ii)** emite una sección declarada con los **comandos de validación de esa
tarea iguales a los del bloque canónico `plan-tasks`** del plan aprobado (`focal_tests` /
`observable_checks` / `regressions` / `integration_gate`, con `@validation_strategy` resuelto) y la
regla de **cuándo ampliarla**; una tarea **ausente** del bloque **falla cerrado nombrando el id**;
**(iii)** emite, por referencia, las **postcondiciones/invariantes/decisiones aplicables** a la unidad
(ids que resuelven a encabezados del contrato) con la referencia del contrato (path + `sha256`);
**(iv)** su **instrucción** declara que la **suite completa no se corre salvo que el paquete lo pida**
(la corre quien cierra) y **ningún** asset de rol/subetapa afirma lo contrario; **(v)** el cierre
exige el **commit** y el reporte lo declara. Borde: sin `plan_task` no hay sección ni fallo; con un id
inexistente, fallo cerrado con el id en el diagnóstico; la extensión es aditiva (el conjunto cerrado
de campos se extiende con una propiedad declarada, y una clave desconocida sigue rechazándose).

**PD-11 (arranque y reentrada: la vista primero — A3).** El procedimiento canónico de arranque y
reentrada **consulta primero la vista `status`** y **amplía solo ante una necesidad concreta**; la
aceptación **observa y registra** el recorrido de una sesión nueva (primera acción de orientación,
ampliaciones con su motivo, resultado) sin presentarlo como garantía. Borde: sin ampliación concreta,
el recorrido llega al primer despacho legítimo **sin** leer el estado completo; con un bloqueo, la
ampliación se registra con su motivo.

**PD-12 (cierre de D11 dentro de la feature — A1).** El cierre de D11 fija el comportamiento
observable de las **tres comprobaciones** y su lugar, según la condición causal de
`docs/specs/005-002-session-context-meter/debt.md` (§ «D11 — el chequeo de no escritura de la
integración real es inestable con la base viva»): **(1)** la **ausencia de escrituras** se verifica
sobre una **base temporal controlada** — afirma que tras la lectura el documento de la base
controlada queda byte-idéntico; vive en el **test focal nuevo de T3**;
**(2)** la **concurrencia** se cubre con una **prueba controlada con otro escritor activo** durante la
lectura — afirma que la lectura se completa y sus resultados son los esperados con un escritor
concurrente vivo; vive en el **mismo test focal**;
**(3)** en la **integración real** se comprueba **solo la lectura y los resultados**, **sin** exigir
que la base quede inmóvil — es la **corrección** de la aserción de `(tamaño, mtime)` de la base viva
en `tests/test_005_002_t4_acceptance.py` (método de D11, `debt.md:129-130`), que pasa a afirmar el
`rc`/el documento y no el estado del store;
**(4)** **nunca** se intenta escribir en la base real para demostrar que está prohibido — es una
**regla declarada** en `context-meter.md` y una ausencia verificable en las pruebas.
Borde: corridas verdes repetidas **no** sustituyen esta corrección (`debt.md:145-146`); si la prueba
controlada de concurrencia revela un defecto real del producto, es un **hallazgo nuevo declarado**,
no una corrección silenciosa dentro de esta ronda.

## 4. Invariantes (verificables)

- **INV-1 (read-only).** La vista, las referencias y la medición son **read-only**: no escriben el
  estado ni el store; la apertura del store sigue siendo `?mode=ro`; la vista deja el estado
  byte-idéntico.
- **INV-2 (sin campo nuevo en el estado).** La selección de entrada usa campos/directorios
  **existentes**; **no** se agrega un campo nuevo al estado.
- **INV-3 (sin otro bootstrap).** El arranque/arranque-desde-reposo-tras-enmienda **reusa** el
  procedimiento existente (`project-start.md`, que compone `state-detection.md`,
  `project-execution.md`, `continuity.md`); **no** se crea otro bootstrap. `state-detection.md`
  sigue siendo el owner canónico del reconocimiento feature/Memory-Bank. El paso de orientación por la
  vista se agrega **por referencia**, sin copiar la estructura de los dueños (A3).
- **INV-4 (frontera con 005-007).** El **tamaño de unidad** y la **preparación de encargos** son de
  005-007; 005-003 aporta el **contrato aplicable** y las **referencias del paquete**. La extensión de
  §2.8 es **aditiva y declarada**: **no** reescribe los contratos de paquete de 005-001/005-005 (los
  campos obligatorios y su semántica no cambian; un paquete sin `plan_task` se emite byte-idéntico).
- **INV-5 (no se reescriben los contratos de 005-002).** El medidor, su superficie de invocación y su
  registro neutral se citan; la extensión del hito «primera acción del encargo» es una **propuesta**,
  no se asume hecha. D11 y R4 se cierran **dentro de la feature** (T3) según su condición causal, sin
  reescribir el contrato del medidor.
- **INV-6 (sin valores de este VPS).** Ni rutas absolutas del host, ni ruta del store, ni proveedor,
  ni modelo concreto, ni servidor, ni identificadores crudos de sesión, en spec, plan ni producto;
  las magnitudes ya publicadas se citan **por referencia**.
- **INV-7 (sin dashboard/scheduler/fuente de estado nueva).** No se crea dashboard, scheduler,
  plataforma de usabilidad ni segunda fuente de estado.
- **INV-8 (condición de gate).** **D11 y R4** son **entregables de T3**, cerrados **dentro de la
  feature**, **antes** de usar la integración real y las corridas multi-sesión como gate; la medición
  se hace con el artefacto del repo **en solo lectura** mientras el medidor no esté instalado; el
  **despliegue** es del dueño. Si por cualquier motivo no estuvieran cerrados, el gate devuelve
  **bloqueo declarado**, no un atajo.
- **INV-9 (unknown con causa, nunca 0).** Lo no observable queda `unknown` con causa, **nunca 0**; la
  meta numérica distingue **medido** de **derivado**.
- **INV-10 (aceptación = próxima sesión real).** Un primer despacho más rápido es **señal**, no
  aceptación; la aceptación usa una **próxima sesión real** y registra ayudas extraordinarias,
  bloqueos y resultado.

## 5. Criterios de aceptación (medibles)

Base **citada por referencia** de la línea base medida; se distingue **medido** de **derivado**. La
comparación es **like-for-like** sobre la **próxima sesión real** de 005-003 (y, si está disponible,
el primer arranque real de 005-006), medida con el **artefacto del repo en solo lectura**, **mismos
cuts**. **Sin** límite universal de minutos ni de llamadas; **no** se afirma operar bajo 100k/200k.

**Las bandas de A1/A7/A9 y el proxy de A8 son ORIENTACIÓN derivada de la línea base medida (A6).**
**No** son una **demostración automática** ni un **umbral que acepte o rechace por sí solo**: la
aceptación la **juzga el orquestador** con el **registro de la sesión real** (ayudas extraordinarias,
bloqueos, resultado) y con lo **medido declarado como medido** y lo **derivado declarado como
derivado**. Una banda fuera de rango **no** rechaza por sí sola; una banda dentro de rango **no**
acepta por sí sola.

- [ ] **A1 — reposo → primer despacho legítimo.** Una sesión nueva en reposo llega al primer despacho
      legítimo **sin leer toda la historia del estado ni reconstruir el CLI desde su código** para el
      recorrido normal. Bandas (**orientación derivada de la línea base, no medidas y no umbrales**):
      llamadas antes del primer despacho **≈45–55** (base medida 72; quita las 21 consultas de código
      ≈70 KB); volumen de salida antes del primer despacho **≈120–180 KB** (base 418.841 car.).
      Lecturas antes del primer hito: **sin lectura del estado completo; ≤ decena** (base de la fila 18
      **no medida** en esta base; A:3, B:41 → **banda, no umbral**).
- [ ] **A2 — la reanudación preserva.** Una reanudación con trabajo activo **preserva autoridad,
      aprobaciones y efectos**; ante ausencia/incoherencia devuelve **BLOQUEO y cómo resolverlo**; un
      resumen corto **no** oculta un paquete pendiente ni declara válido un contrato cambiado.
- [ ] **A3 — los ejemplos se ejecutan.** Los ejemplos operativos **se ejecutan** contra la versión
      correspondiente (localizados por el asset canónico, **nunca** por prosa de Markdown).
- [ ] **A4 — lo ausente queda `unknown` con causa.** Nunca `0`; las magnitudes distinguen **medido**
      de **derivado**.
- [ ] **A5 — no traslada trabajo al primer worker.** El encargo queda **completo**, sin
      bloqueos/retrabajo **por orientación**, con responsabilidades claras.
- [ ] **A6 — señal ≠ aceptación.** La aceptación usa una **próxima sesión real** y registra **ayudas
      extraordinarias, bloqueos y resultado**; un primer despacho más rápido **no** acepta por sí
      solo.
- [ ] **A7 — `time_to_first_dispatch`.** **≤ la banda de C, sin aumento** (base C 8,29–8,78 min;
      A/B 6,17–9,42 min, **trabajo legítimo distinto** → **no se promedian**). **Orientación, no
      umbral automático** (A6).
- [ ] **A8 — reorientación de rol (OBSERVACIÓN declarada del proxy de tramo completo, A5).** Las
      lecturas de **toda la sesión del rol** — el proxy de **tramo completo** (`session_reads`,
      `total_output`, `tool_calls`) — se **observan y se registran**, **sin** afirmar «sin aumento»;
      el proxy se declara como lo que es (**tramo completo, no un corte pre-acción**: `previous_*` y
      `time_to_first_*` salen `unknown` con causa en toda sesión de rol) y **lo ausente queda
      `unknown` con causa**. La **pregunta de aceptación** es si el rol **pudo empezar y completar su
      encargo con menos reconstrucción innecesaria**, **sin trasladarle trabajo** y **sin quitarle
      información necesaria**. La extensión acotada del medidor (hito nuevo) es **PROPUESTA** (§10),
      no asumida.
- [ ] **A9 — tiempo del orquestador entre despachos.** **Reducción, con criterio declarado** (base
      derivada 38,46 min); límites declarados (huecos **negativos** si dos roles se solapan; el
      tiempo del orquestador **dentro** de la ventana de un rol es **invisible**). **Orientación, no
      umbral automático** (A6).
- [ ] **A10 — redundancia (A4).** **Ninguna corrida completa innecesaria ni repetición de evidencia
      equivalente**; las **ampliaciones se justifican por el cambio o por un hallazgo**, y la
      fidelidad se verifica por **procedencia + equivalencia** canónica (`re-entry.md`); la suite
      completa la corre **una vez** quien cierra. La aceptación **registra las corridas observadas
      con su motivo** (no se fija un «0 corridas» rígido: el criterio es la justificación).
- [ ] **A11 — gate.** **D11 y R4** cerrados **en T3 (entregables de la feature)** antes de usar la
      integración real y las corridas multi-sesión; medición con el **artefacto del repo en solo
      lectura** mientras el medidor no esté instalado.

## 6. Las tres prácticas del delta (hipótesis y cómo se miden)

Son **hipótesis a medir**, no soluciones decididas; 005-003 aporta el **contrato aplicable** y las
**referencias del paquete** (§2.8), no el tamaño de unidad (INV-4).

- **(i) Validación concreta en cada encargo.** El paquete nombra los **comandos de validación
  aplicables** de su tarea (del bloque canónico `plan-tasks`, §2.8) y dice **cuándo ampliarla**; la
  suite completa la corre **una vez** quien cierra y **no se corre salvo que el paquete lo pida**.
  *Cómo se mide:* por **observación del paquete + ejecuciones reales** (no por grep de frases en
  Markdown) y por la **provenance** de los valores contra el bloque (§2.8-a).
- **(ii) Verificación en dos niveles.** **Siempre**: procedencia, diff, alcance y los focales
  (segundos). **Solo con un motivo concreto**: la suite o la integración. Se reutiliza la **evidencia
  equivalente con procedencia verificada**, por **referencia** a la regla canónica ya existente
  (`re-entry.md`), que **no se copia**. *Cómo se mide:* declaración en el ledger/evidencia + cierre
  con una sola corrida de suite + registro de las corridas observadas y su motivo (A10).
- **(iii) Agrupar defectos de una misma clase sin mezclar roles.** Un **RED** para varios defectos de
  una **misma clase** y **después** un **GREEN**, cada uno en **su sesión**, sin mezclar roles; el
  paquete lleva el **contrato aplicable** y **referencias para ampliar** (§2.8) sin obligar a releer
  la spec entera. *Cómo se mide:* por observación de los paquetes RED/GREEN y su aislamiento de roles.

## 7. Fronteras

- **005-006 (arranque guiado).** Se **reutiliza** el procedimiento de reconocimiento/arranque
  existente (`project-start.md`); **no** se crea otro bootstrap. El **arranque desde reposo tras una
  enmienda autorizada** pertenece a **esta** feature; el paso de orientación por la vista (§2.9) se
  agrega **por referencia**, sin copiar la estructura de los dueños.
- **005-007 (planificación progresiva).** El **tamaño de unidad** y la **preparación de encargos** son
  de 005-007; 005-003 aporta el contrato aplicable y las referencias (§2.8), de forma **aditiva**.
- **005-001/005-005 (contratos de paquete).** **No** se reescriben; la extensión de §2.8 es **aditiva
  y declarada** (campos obligatorios y semántica intactos; paquete sin `plan_task` byte-idéntico).
- **OpenChamber / OnlyOffice.** **No** se implementan; OpenChamber es consumidor verificado, no
  dependencia ni dashboard.
- **No** se crea dashboard, scheduler, plataforma de usabilidad ni otra fuente de estado.
- **005-002.** El medidor es **insumo**, no sustituto; su contrato **no** se reescribe; **D11 y R4 se
  cierran dentro de la feature (T3)**.

## 8. Prohibiciones y fuera de alcance

- **Sin valores de este VPS** (INV-6); **sin desplegar**; **sin tocar HOME**; **sin push**.
- **No** reescribir los contratos aprobados de 005-002; **no** asumir la extensión del hito.
- **No** reescribir los contratos de paquete de 005-001/005-005; la extensión es **aditiva y
  declarada** (§2.8).
- **No** proponer otra vez la enmienda de la fila 8 del plan del epic: está **aprobada** (`5b912aa`) y
  se cita como contrato vigente.
- **No** otro bootstrap; **no** dashboard/scheduler/fuente de estado nueva; **no** OpenChamber ni
  OnlyOffice.
- **No** aprobar la propia propuesta; **no** fabricar registros ni aprobaciones; **no** ampliar
  alcances para continuar; **no** repetir la medición de la línea base.
- **Fuera de alcance:** motor de evaluación de sesiones, dashboard, scheduler, plataforma de
  usabilidad, espera improductiva, cuotas/ETA, calidad semántica, comparaciones entre modelos, CI,
  sandbox, y repetir el discovery o desarrollos completos para comparar.

## 9. Contexto técnico (verificado)

- **Estado y bloat del historial** (citado por referencia del discovery/línea base): `stage_history`
  = **304.075 B = 94,8 %** del estado; 315 entradas (línea base). Claves de primer nivel y valores
  operativos verificados por lectura del archivo (proyección: `active_epic`, `active_feature`,
  `current_stage`, `active_packet.status`, `execution`, `hitl_delegation.status`, `approver`).
- **Superficie del CLI de paquetes:** subcomandos `validate-state`, `validate-policy`, `render`,
  `validate-request`, `validate-packet`, `prepare`, `validate-metric` (`cdad_packet.py:3454-3507`);
  `prepare` con sub-modos mutuamente excluyentes (`:3470-3510`, `:3529-3578`); error de argv →
  `ERROR: prog: msg` (`:3447-3449`); `PolicyError` → `ERROR: …` con `rc=2` (`:3720-3722`).
- **Límite de bytes (C1):** `cdad_continuity.py:55,638-640` (`--max-bytes`, default 16 KiB, **falla
  cerrado citando el límite**) y `:1306,1323` (bandera `--max-bytes` de `begin`/`checkpoint` y
  `resume`); `context-meter.md:243` (**16.384 B por documento de sesión**).
- **Rechazo de raíz relativa (C4):** `cdad_packet.py:663-666` (`_absolute_existing_directory`) y el
  chequeo **previo al dispatch del subcomando** en `main` (`:3635-3636`); `PolicyError` → `ERROR: …`
  con `rc=2` (`:3720-3722`).
- **Esquema del medidor (C2/V3):** `context-meter.schema.json` — `run` (`:26-45`), `$defs/milestone`
  (`:114-148`), `$defs/truncated.detail_flag` (`:241-245`), `$defs/role_aggregate_entry` (`:352-402`);
  `additionalProperties: false` (`:7`) y **sin** clave de resumen de corrida.
- **Registro de despacho (C3):** `project-execution.md:113-116` (`prepare --record-dispatch … --input
  docs/attempt.json`; campos exactos `runtime, model_configured, model_reported, session, started_at`
  + `provenance`); `continuity.md:17,33` (`begin --update UPDATE.json`).
- **Esquemas reusados:** `packet-request.schema.json` (campos requeridos, `:6`; cierre
  `additionalProperties: false`, `:5`); `execution-context.schema.json` (`:6-11`);
  `state-template.json` (claves, `:2-18`).
- **Vista/versión:** `cdad-version-check.py` vive en `skills/cdad-cycle/scripts/` (única ubicación
  en el árbol); verdictos `COHERENT(0)/DRIFT(1)/UNKNOWN(3)/NO-PROJECT-AGENTS(4)`
  (`project-start.md` §10); lee el marcador solo en la raíz de su propio árbol.
- **Continuidad:** `resume` proyecta `goal / authority / decisions / uncertainties / next_action`;
  `--max-bytes` (default 16 KiB) **falla cerrado sin truncar** (`continuity.md:59-60`).
- **Medidor (005-002):** `context-meter.md:243` publica el límite de **16.384 B por documento de
  sesión**; `context-meter.schema.json:7` declara `additionalProperties: false` y **no** tiene clave
  de resumen de corrida; `debt.md:113-116` (R4) y `:128-146` (D11) con sus condiciones de cierre.
- **Regla de equivalencia (canónica):** `re-entry.md:67-79` (*Equivalence of a registered run*), con
  la regla de ampliación focal/transversal en `:77` — se referencia, no se copia.
- **`resume` solo con ejecución activa:** `project-start.md:134-138`.
- **Asimetría de raíz relativa:** verificada por el orquestador (`cdad_packet.py` rechaza raíz
  relativa; `cdad_continuity.py resume --project-root .` rc=0; `cdad_result.py` resuelve contra cwd).
- **Evidencia mecánica (reproducciones del discovery §1.3):** `PIPESTATUS=(2 0)` con tubería;
  `ERROR: --project-root must be an absolute existing directory: .` en `prepare` y `validate-state`.
- **Bloque canónico `plan-tasks` (A2):** formato único en
  `planning-contract-draft.md:87-138` (§4.1: `tasks`, `validation_strategy`, `@validation_strategy`);
  lector del CLI `cdad_packet.py:2856-2915` (`PLAN_TASKS_FENCE`/`_plan_tasks_from_contract`; el bloque
  es obligatorio y **exactamente uno**), chequeos estructurales `:2918-3033` y plan de validación por
  tarea `:3036-3078` (tarea con código ⇒ `focal_tests`; sin código ⇒ `observable_checks`;
  `regressions`/`integration_gate`/`owner` obligatorios). **Hoy** el bloque se parsea **solo** para un
  contrato `draft-plan` declarado (reviewer-only), antes de publicar (`:3386-3389`).
- **Derivación de contratos (A2):** `cdad_packet.py:974-987` — architect → `docs/epics/<epic>/plan.md`
  (sin bloque de tareas); demás roles → `docs/specs/<feature>/spec.md`; el plan de la feature es
  `docs/specs/<feature>/plan.md` (misma derivación por directorio).
- **Conjuntos de campos cerrados (A2):** `cdad_packet.py:741-745` (`set(document) != required` ⇒
  `request fields do not match schema`) y `:756-761` (cierre del campo `contract`, con
  `plan_version` opcional) — la extensión es **aditiva y declarada**.
- **Emisión del paquete (A2):** `cdad_packet.py:850-907` (`render_packet`) — bloque de instrucción
  compuesto por `packets/common.md` + `packets/roles/<role>.md` +
  `packets/substages/<role>-<substage>.md` (`:852-854`), techo declarado de la instrucción estática
  (default **12.000 B**, `:860-878`), `instruction_sources` con path+sha256 (`:888-891`) y secciones
  Objective/Contract/Inputs/Read scope/Write scope/Invariants/Expected output/Evidence required
  (`:894-906`). Tamaños medidos de los 14 pares rol+subetapa: **1.001–2.060 B** (muy por debajo del
  techo). `DEFAULT_EVIDENCE` ya incluye **`commit`** (`:970`).
- **Contradicción a corregir (A2-c):** `packets/roles/implementer.md:1` y
  `packets/substages/implementer-green.md:1` afirman «the complete suite is the closure gate»;
  `packets/common.md:1` es la parte común del bloque de instrucción.
- **D11 (A1):** la aserción inestable es la comparación de `(tamaño, mtime)` del store y sus
  `-wal`/`-shm` en `tests/test_005_002_t4_acceptance.py` (método `test_c5_sboot04_primer_despacho_por_entorno`),
  con su condición causal en `debt.md:128-146`.
- **Arranque/reentrada (A3):** `project-start.md` §1-§10 — §6 encadena reconocimiento → primer
  encargo con la secuencia concreta de comandos (`:74-132`), §7 `resume` solo con ejecución activa
  (`:134-138`), §8 bloqueo accionable, §10 una sola comprobación de versión (`:164-191`); **hoy no
  hay paso que consulte primero la vista**. Regresión estructural de 005-006 sobre ese archivo:
  `tests/test_005_006_t1_start_procedure.py:58` (`PSTART = REFS / "project-start.md"`), con INV-1
  (no copiar la estructura de los dueños).
- **Fila 8 enmendada (contrato vigente):** `docs/epics/epic-005-real-operation/plan.md:41` (fila) y
  `:140-146` (cambio registrado; commit `5b912aa`; sha256 `b22bc687…`).

## 10. Decisiones propuestas (a resolver al aprobar)

| Id | Propuesta del architect | Rationale |
|---|---|---|
| **D1** | Vista compacta = **proyección por código** sobre las fuentes existentes; **no** se migra el formato del estado ni se separa el historial. | discovery (a); el costo lo paga el agente, no el CLI; separar el historial rompería consumidores/pines. |
| **D2** | Forma: **subcomando read-only nuevo `status`** de `cdad_packet.py`, salida JSON acotada con los campos de §2.1. | D-4 (fijar superficie y elegir forma); el CLI de paquetes ya conoce estado y aprobaciones. |
| **D3** | Selección de entrada = **mapa explícito** que atiende `prepared`/`dispatched` y trabajo pendiente; **no** depende de «inicializar»; detección con campos/dirs existentes. | discovery (b); caso real `discovery` + `prepared`. |
| **D4** | Interfaz operativa = **referencia corta + ejemplos EJECUTADOS** (asset canónico, C3); reusa esquemas/constantes; **sin** manual extenso ni generador. | discovery (c); delta punto 1. |
| **D5** | Versión: reusar el **instalado**; **ausencia ≠ incoherencia**; «medidor ausente» = ausencia; republicar + verificar. | discovery (d); hecho 1. |
| **D6** | Evidencia mecánica: capturar el `rc` **sin enmascarar**; salida acotada + evidencia completa; asimetría de raíz relativa diagnosticada en la salida (C4). | discovery (e); hallazgos vivos. |
| **D7** | Resumen del conjunto en **documento aditivo separado** (V1 **decidido**) + regla del **documento multiplexado** en `context-meter.md` (R4) **antes** del consumo multi-sesión, **como entregable de T3**. | delta R4; INV-5 (no reescribir 005-002); fila 8 enmendada («D11 y R4 se cierran dentro de la feature»). |
| **D8** | Reorientación de rol = **proxy de tramo completo** observado y registrado; extensión del medidor (hito nuevo) = **PROPUESTA al dueño**, no asumida. | hecho 2; fila 8 enmendada (meta de orientación, no demostración); A5. |
| **D9** | Meta numérica = **bandas** de la línea base, con **medido vs derivado**, declaradas **orientación y no demostración automática**; sin límite universal. | discovery §4.2; delta Aceptación; A6. |
| **D10** | Límite de la vista = **16.384 B (16 KiB)**, **fail-closed sin proyección parcial** (C1); el número **reusa** los límites normativos ya existentes. | continuidad (`continuity.md:59-60`) y medidor (`context-meter.md:243`): consistencia y no invención de un número nuevo. |
| **D11b** | Contrato aplicable del encargo = **unidad nueva T6**: opción aditiva `--plan-task <ID>`, campo opcional `plan_task`, sección `## Task validation plan` (valores **iguales** al bloque `plan-tasks`) y sección `## Applicable contract` (referencias); la instrucción declara que la suite completa no se corre salvo que el paquete lo pida; el cierre exige el **commit**. | fila 8 enmendada (contrato vigente); A2; el sufijo evita confundir esta decisión con la **deuda D11** de 005-002, que esta ronda asigna a T3. |
| **D12** | Cierre de **D11** en **T3**: (1) no-escritura sobre **base temporal controlada**; (2) concurrencia con **otro escritor activo** (prueba controlada); (3) la integración real comprueba **solo lectura y resultados**; (4) **nunca** se escribe en la base real. Prueba focal nueva de T3 + corrección de la aserción de la base viva. | `debt.md:128-146` (condición causal corregida); fila 8 enmendada (D11 se cierra dentro de la feature); A1. |

## 11. VERIFY

| # | VERIFY | Estado en el draft | Dueño / cuándo |
|---|---|---|---|
| **V1** | Transporte del resumen: **documento aditivo separado** (`set-summary-v1`), registro neutral por sesión byte-congelado. | **DECIDIDO por el orquestador** (ratificado en draft-002). | — (cerrado). |
| **V2** | Subcomando `status` de `cdad_packet.py` y **nombres de los campos de §2.1** (`project`, `epic`, `feature`, `execution`, `packet`, `authority`, `version`, `next`, `entry`, `unknowns`) = **contrato de la salida**. | **DECIDIDO por el orquestador** (ratificado en draft-002). | — (cerrado). |
| **V3** | Redacción exacta de la regla del documento multiplexado en `context-meter.md`. | **ABIERTO (implementer de T3)**: los **dos elementos** quedan fijados — (a) el total es **≤ N × el límite por sesión** y (b) el **límite normativo es POR DOCUMENTO DE SESIÓN**. | Implementer de T3; test que afirma ambos elementos. |

*(Los VERIFY que el orquestador ya cerró — (b) detección de trabajo pendiente, (c) frontera con
005-007, (e) asimetría de raíz relativa, (g) alcance de OpenChamber — se usan como **hechos** y no se
reabren. V1 y V2 pasan a **contrato decidido**. La forma de §2.8 (nombre de la opción, del campo y de
las secciones) se fija por **D11b**, como D2/D4 fijan la vista y la interfaz: no es un VERIFY abierto.
La redacción exacta de la declaración de §2.8-c y de la regla de §2.9 queda al implementer/test-writer
de su tarea, dentro del contrato fijado.)*

## 12. Riesgos con mitigación

- **R1 — el historial del estado sigue creciendo** (el estado medido en la línea base ~320 KB; crece
  con cada artefacto materializado). **Mitigación:** la vista **no** emite el historial (PD-1); la
  ventaja de la proyección **crece** con el historial.
- **R2 — la medición depende del medidor no instalado.** **Mitigación:** medir con el **artefacto del
  repo en solo lectura**; el despliegue es del dueño; **D11/R4 se cierran en T3** (INV-8) antes de
  usar la integración y las corridas multi-sesión como gate.
- **R3 — tocar 005-002 al añadir el resumen o al cerrar D11.** **Mitigación:** resumen **aditivo** y
  registro por sesión byte-congelado (PD-7); el cierre de D11 **no** reescribe el contrato del medidor
  (corrige evidencia y declara la regla; PD-12).
- **R4 — una sola sonda por variante → indicativa, no estadística** (riesgo del epic). **Mitigación:**
  bandas declaradas **orientación, no umbral** (A6) + criterio de comparación like-for-like; **no**
  promediar cuts distintos.
- **R5 — privacidad.** **Mitigación:** INV-6; citar magnitudes ya publicadas por referencia.
- **R6 — la extensión del paquete toca contratos de 005-001/005-005 y la corrección de D11 toca un
  test de 005-002.** **Mitigación:** extensión **aditiva y declarada** (INV-4, §2.8) con regresiones
  dedicadas (`test_005_001_t2_replace_packet.py`, `test_005_005_t1_replace_conserved.py`); la
  corrección de D11 se declara como corrección de **evidencia** (no de contrato) y su test focal
  nuevo lleva el oráculo real.

## 13. Aprobación

- **Estado de este texto: APROBADO (2026-10-12, ronda draft-003).** Aprobado por el **orquestador
  OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`; alcance: aprobar specs y planes de las features
  del epic), **junto con el plan** (una sola acción). El architect **no** aprobó su propia propuesta
  (anti-sesgo). **Decisiones adoptadas: D1–D10** del draft 002 (sin cambios) **más** las de esta
  ronda (D11/D12 según §10). **Sin enmiendas al re-aprobar**: la ronda acotada **draft-003** resolvió
  **A1–A6** en el propio draft y conservó íntegro el resto del draft 002.
- **Historial.** El texto del **draft 002** fue **aprobado (2026-10-12)** por el **orquestador
  OpenCode**, bajo la **delegación HITL del epic-005**
  (`docs/epics/epic-005-real-operation/execution.md`), **junto con el plan** (una sola acción), en el
  commit `009902b` (spec `0fcf78fe…`, plan `7eb9fe8f…`), con **D1–D10** adoptadas y **V3** abierto.
  Entre tramos, el **orquestador Claude** revisó spec y plan
  (`review-claude-spec-2026-10-12.md`): **conforme en lo sustancial**, con **dos puntos a resolver**
  (D11 sin tarea que lo cierre; A10 sin producto) y observaciones menores. El **dueño** decidió
  **seis ajustes (A1–A6)** que este draft-003 aplica **conservando íntegro todo lo demás**.
- **Contrato vigente (citado, no enmendado).** La **fila 8 del plan del epic está ENMENDADA Y
  APROBADA** por el dueño (commit `5b912aa`; sha256
  `b22bc687e327c8524ab55f44ae8df65b06076bcc628e373b5e274a54906bec16`; fila `plan.md:41`, cambio
  `:140-146`). Esta spec **la cita como contrato vigente**; **no** propone otra enmienda. El borrador
  anterior proponía esa enmienda: **queda cerrada y no se reabre**.
- **D11 y R4 (INV-8).** Se **cierran dentro de la feature**, como **entregables de T3** (§2.6,
  PD-12, D12), **antes** de usar la integración real y las corridas multi-sesión como gate. Dejan de
  ser condiciones sueltas del gate de T5: T5 **verifica** su cierre (con su evidencia) y, si faltara,
  devuelve **bloqueo declarado**.
- **Aceptación y meta numérica (A6).** Se adoptan los criterios **A1–A11** con las bandas derivadas de
  la línea base medida, declaradas **orientación derivada y NO demostración automática ni umbral**;
  la aceptación la juzga el orquestador con el **registro de la sesión real** (ayudas extraordinarias,
  bloqueos, resultado), con **medido vs derivado** explícito y sin límite universal de minutos ni de
  llamadas. **A8** es una **observación** registrada del proxy de tramo completo (sin afirmar «sin
  aumento») y **A10** exige **justificación** de las ampliaciones (no un «0 corridas» rígido).
- **Contratos de 005-002.** **No** se reescriben (INV-5); la **extensión del hito «primera acción del
  encargo»** sigue siendo **PROPUESTA al dueño**, no asumida ni plegada al alcance comprometido.
- **Contratos de paquete de 005-001/005-005.** **No** se reescriben; la extensión de §2.8 es
  **aditiva y declarada** (D11b).
- **Verificación del orquestador antes de re-aprobar** (proporcional, con evidencia propia): el bloque
  canónico `plan-tasks` del plan (con **T6** incorporada) se validó con las funciones del **propio
  CLI** en solo lectura (`_plan_tasks_from_contract` + `_check_plan_tasks` +
  `_check_plan_validation_plan`): `OK`, tareas `T1..T6`, estrategia declarada. **Sin suite ni
  integración**: motivo declarado — el paquete del architect no cambia código y no tiene
  postcondiciones ejecutables.
- Status: Approved by orquestador OpenCode (HITL delegada epic-005) on 2026-10-12 (ronda draft-003)
