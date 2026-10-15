> Plan **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). Se aprueba **junto con la spec** por el **orquestador OpenCode** bajo la
> HITL delegada del epic-005 (`docs/epics/epic-005-real-operation/execution.md`), o por el **dueño**; el
> architect **no** aprueba su propia propuesta (anti-sesgo). Contrato:
> `docs/epics/epic-005-real-operation/plan.md`, fila 11 (`:44`), sha256
> `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, más «Ajuste de los ciclos
> pendientes» (`:48-88`). Deriva de `docs/specs/005-011-common-entry/discovery.md` (§1-§10), que se
> resuelve **por referencia**. El bloque canónico `plan-tasks` de §4 sigue el formato de los planes
> vigentes (`docs/specs/005-007-progressive-planning/plan.md` §4 y
> `docs/specs/005-004-claude-code-roles/plan.md` §4) y se validó con las funciones del propio CLI en solo
> lectura. **Sin valores de este VPS; sin rutas absolutas del dueño ni ids crudos de sesión**
> (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`).

# Plan — 005-011-common-entry

## 1. Ficha de la feature

- **Feature ID:** `005-011-common-entry` · **Epic:** `epic-005-real-operation` · **Estado:** DRAFT (etapa 2).
- **Resultado buscado (fila 11, `plan.md:44`):** una sesión nueva entra al proceso por una **ruta breve y
  COMÚN** antes de leer el state o explorar: **(a)** todas las skills (`cdad-epic`, `cdad-cycle` y las de rol
  que orientan) empiezan por `status`; `state-detection.md` y la documentación extensa quedan como
  **ampliación ante una necesidad concreta**; **(b)** `status` acepta una **raíz relativa** igual que los
  demás CLI; **(c)** `status` informa **versión y siguiente acción claras**: un `DRIFT` legítimo dice **qué
  lo resuelve**, en vez de invitar a investigar.
- **Contrato y reglas reusadas:** spec §9. **Dependencias del epic:** `005-003` (vista compacta) y `005-007`
  (planificación progresiva). **Fronteras de contrato (no reescritura):** 005-003 (vista), 005-004
  (procedencia/versión, lado CC), 005-007 (planificación), 005-005 (procedencia): esta feature los
  **referencia** o los **extiende de forma aditiva y declarada** (spec INV-2/INV-4/PD-6).
- **Cambio autorizado:** la fila 11 **supersede** el comportamiento C4 de 005-003 (spec §2.2/PD-3); se
  declara y se nombran sus **dos** oráculos.
- **Convención de anonimización:** toda la salida usa `<home>`, `<repo>`, `<tmp>`, `<ses-…>`; el mapa real
  vive en `.cdad/local/` (fuera de git).

## 2. Ajuste de las unidades del discovery a tareas atómicas

Una tarea por **clase de producto y oráculo**; un **RED** cubre una clase y su **GREEN** va en **otra
sesión**, sin mezclar roles. El discovery (§6.3) propuso U1 (b), U2 (a) y U3 (c); esas unidades se
**reagrupan por clase** así:

| Unidad del discovery | Tarea | Por qué se agrupa así |
|---|---|---|
| **U1 — (b)** raíz relativa consistente + texto que quedaría falso + oráculos | **T1** | Clase **código del CLI + texto + oráculos de test**: un solo producto (la resolución unificada de `--project-root`), con focal nuevo y los dos oráculos declarados. Va **primero**: la entrada de (a) usa una raíz relativa en el recorrido real. |
| **U2 — (a)** entrada común de las skills | **T2** | Clase **documental** (dos `SKILL.md` + indexación de `orientation.md`); su oráculo son las guardas por ventana existentes + la review del texto (INV-5). No comparte archivos con T1/T3. |
| **U3 — (c)** versión y siguiente acción en la vista | **T3** | Clase **código del CLI** (`cdad_packet.py`) con focal de salida; **mismo archivo que T1** → se **serializa** (`depends_on: [T1]`). |
| Cierre/aceptación (§6.3) | **T4** | **Gate** (no RED/GREEN de producto): `observable_checks` + gate de integración; requiere T1/T2/T3. |

**Qué NO se planifica** (fuera de alcance, spec §7): el registro de transiciones (005-012), el contrato por
unidad (005-013), el adaptador Claude Code y la medición del lado CC (D-4 de 005-004); **no** se reabren
005-003/005-004/005-007; sin CI, WebUI, sandbox, plataforma de jobs, sin tocar HOME, sin desplegar, sin push.

**Nota de paralelismo.** T1 y T2 editan **archivos distintos** y podrían declararse paralelas; se deja
`parallel: []` (conservador, sin ganancia de integración). T1 y T3 editan **el mismo archivo**
(`skills/cdad-cycle/scripts/cdad_packet.py`) → **no** paralelas (`depends_on: [T1]`), consistente con el
validador del producto.

## 3. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre:** procedencia, `git diff` contra el alcance del paquete, alcance declarado y
  **pruebas focales** (segundos). **Sólo con un motivo concreto:** la suite o la integración. Se **reutiliza
  evidencia equivalente** con procedencia verificada **por referencia** a
  `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*).
- **Suite completa una vez, al cierre** (motivo: toca el CLI, las skills y el texto de orientación; cierra
  la feature). No se corre dentro de cada tarea; **no se corre salvo que el paquete lo pida** (la corre quien
  cierra).
- **Comandos concretos por encargo** (fichas de §4), **tomados del bloque `plan-tasks`** y rendidos en el
  paquete (mecanismo de 005-003 T6). RED: el focal debe fallar por aserción (no por import/sintaxis).
  GREEN: focal verde + regresiones del área.
- **El sentido de los textos lo juzga la review** (INV-5): T2 se valida con **comprobaciones observables**
  (estructura + guardas verdes) y con la review; **no** con tests que decidan el significado de un párrafo
  por listas de palabras.
- **El cierre incluye el commit** y el reporte del rol lo declara; un rol que termina sin commitear es
  **bloqueo declarado**.
- **Metas numéricas = orientación** (spec AC-6): derivadas de las líneas base medidas, **no** umbral.
- **Sin `--no-verify`; sin push; sin desplegar; sin tocar HOME; sin leer `tests/.sensitive-patterns.local`.**

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — (b) Raíz relativa consistente en `cdad_packet.py` + texto que quedaría falso + los dos oráculos declarados
- **Resultado observable / PD cubiertas:** PD-2, PD-3.
- **Alcance incluido:** unificar la resolución de `--project-root` en `cdad_packet.py` a «resolver contra el
  cwd + `is_dir()`» (sustituir `_absolute_existing_directory`, `:673-677`; **retirar** `_status_project_root`,
  `:3776-3791`, y su rama en `main`, `:4302`); corregir el texto que quedaría falso
  (`orientation.md:68-75`, `project-execution.md:49`); actualizar los **dos** oráculos declarados
  (`tests/test_005_003_t1_compact_view.py:414-441` al comportamiento nuevo; `tests/test_005_003_t2_examples_execute.py:545-656`
  con el fixture de fallo corregido y su oráculo de captura conservado). **Excluido:** tocar la política, el
  hashing, la publicación de derivados o el default cwd; crear una bandera nueva.
- **Consume:** — . **Produce:** `project-root-resolution` (`project-root-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`,
  `skills/cdad-cycle/references/orientation.md`, `skills/cdad-cycle/references/project-execution.md`,
  `tests/test_005_003_t1_compact_view.py`, `tests/test_005_003_t2_examples_execute.py`; *Test*
  `tests/test_005_011_t1_relative_root.py`.
- **Contexto por rol:** RED — spec §2.2/§3 (PD-2/PD-3), `cdad_packet.py:673-677,3776-3791,4294-4304`,
  `cdad_result.py:1508-1511`, `cdad_continuity.py:623`; GREEN — ídem.
- **Evidencia al re-entry:** focal rojo→verde (hoy `status --project-root .` rc=2 sin proyección; después
  rc=0 con proyección) + los dos oráculos declarados actualizados + `git diff` acotado; **sin** cambios en
  política/hashing/publicación (regresión).
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_011_t1_relative_root.py -q`; regresiones
  `tests/test_005_003_t1_compact_view.py`, `tests/test_005_003_t2_examples_execute.py`,
  `tests/test_packet_prepare.py`, `tests/test_005_003_f2_idle_history.py`,
  `tests/test_005_005_t1_replace_conserved.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si la unificación exigiera cambiar una validación **distinta** de la
  resolución de la raíz, **detener** (fuera de alcance); si el dueño/orquestador **no** autoriza el segundo
  oráculo, **detener** y declararlo (el paquete autorizó el C4; el segundo se **declara**, spec PD-3/V4).

### T2 — (a) Entrada común de las skills (Step 1 de las dos `SKILL.md`, filas de tabla, indexar `orientation.md`)
- **Resultado observable / PD cubiertas:** PD-1.
- **Alcance incluido:** reescribir el **Step 1** de `cdad-cycle` (`:249-251`) y `cdad-epic` (`:56-58`) para
  que la **primera acción** sea la vista `status`; pasar `state-detection.md` a **ampliación condicional**
  con gatillo en la tabla de referencias; **indexar `orientation.md`** en la tabla de `cdad-cycle`
  (`:447-469`); **referenciar** la regla (`orientation.md` §1 + `project-start.md` §11), **sin** copiarla.
  **Conservar** la rama `resume` (`SKILL.md:251`) y la fila `project-start.md`. **Excluido:** crear una
  referencia «common entry» nueva; duplicar la regla; tocar el agente `cdad-orchestrator` (no es el texto
  común entre runtimes).
- **Consume:** — . **Produce:** `common-entry` (`common-entry-v1`).
- **Dependencias:** — .
- **Archivos:** *docs-only* → `files: []` (convención de 005-003 T4 / 005-007 T6); los paths viven en esta
  ficha: `skills/cdad-cycle/SKILL.md`, `skills/cdad-epic/SKILL.md`. *Test* — (ciclo sin código; guardas
  existentes como regresión).
- **Contexto por rol:** test-writer — spec §2.1/§3 (PD-1), `SKILL.md:249-251,447-469`,
  `cdad-epic/SKILL.md:56-58,200-209`, `state-detection.md:16-18`, `project-start.md:223-240`; reviewer — el
  texto **por sentido** (INV-5).
- **Evidencia al re-entry:** comprobación observable roja→verde (el Step 1 manda leer el state → la primera
  acción es la vista; `orientation.md` ausente de la tabla → presente; `state-detection.md` primer paso →
  ampliación condicional); las **guardas por ventana verdes**; `git diff` acotado a las dos `SKILL.md`.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** `@validation_strategy`; implementer (edita las dos `SKILL.md`; el test-writer
  no edita fuera de `tests/`); verificación por el orquestador y, por sentido, la review.
- **Incertidumbres / detención:** si conservar la guarda exigiera **copiar** la estructura de los dueños,
  **detener** (INV-3); si el texto se leyera como «prohibido leer el state», **detener** y reformular (R3).

### T2b — Entrada común también en el prompt del agente orquestador (ampliación tras AC-6)
- **Resultado observable / PD cubiertas:** PD-1 (ampliado; spec, enmienda 4).
- **Alcance incluido:**
  - en `sources/roles/orchestrator.md`, la primera acción de toda sesión pasa a ser cargar la skill
    `cdad-cycle` y consultar su vista `status`, por referencia a `orientation.md` §1;
  - `resume` queda como paso siguiente, solo con una ejecución activa (se conserva la rama «start from
    rest»), y el state completo como ampliación ante una necesidad concreta;
  - regenerar los agentes con `make agents`.
- **Excluido:** copiar la regla, y cambiar otros roles o el mecanismo de despacho.
- **Consume:** `common-entry` (`common-entry-v1`) de T2. **Produce:** `orchestrator-entry` (`orchestrator-entry-v1`).
- **Dependencias:** T2.
- **Archivos:** *Modify* `sources/roles/orchestrator.md` y los derivados `agents/**` regenerados. *Test*: ninguno
  nuevo (es texto; el sentido lo juzga la review). Regresiones: las guardas de texto existentes del rol
  orquestador y de la paridad del generador.
- **Verificación:** `observable_checks` + regresiones; la prueba real es AC-6 repetida con la versión
  redesplegada.
- **Integración / responsable:** `@validation_strategy`; implementer; verificación del orquestador.
- **Incertidumbres / detención:** si las guardas existentes (005-006 PD-9, 005-010, INV-8 de 005-009) exigen
  conservar una frase literal, se conserva y la frase nueva se agrega antes, sin duplicar la regla.

### T3 — (c) Versión y siguiente acción en la vista (`DRIFT` legítimo con su resolución; ruta de `prepared` con la acción natural)
- **Resultado observable / PD cubiertas:** PD-4, PD-5.
- **Alcance incluido:** en `status_view`/`_version_verdict` (`cdad_packet.py:3815-3842,3965-4087`), **leer**
  las patas del chequeo (`project`/`agents`/`CLI`/`claude-code`, `cdad-version-check.py:214-236`) y, ante
  `DRIFT`, emitir la **pata que diverge** y la **resolución** **sólo** si la pata es `project` (el próximo
  `prepare` republica los derivados del proyecto); **no** confundir ausencia con incoherencia; cambiar el
  **texto** de `_next_route` (`:3930-3949`) para `prepared` (acción natural = **despacharlo**;
  `--replace-packet` condicional); `entry` **sin cambios**. Documentar en `orientation.md` §1/§4 **por
  referencia**. **Excluido:** cambiar el mapa de `entry`; cambiar la ruta de `dispatched`; introducir un
  veredicto nuevo; tocar `cdad-version-check.py`.
- **Consume:** — . **Produce:** `view-action` (`view-action-v1`).
- **Dependencias:** T1 (mismo archivo `cdad_packet.py` → **serializada**).
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`,
  `skills/cdad-cycle/references/orientation.md`; *Test* `tests/test_005_011_t3_view_action.py`.
- **Contexto por rol:** RED — spec §2.3/§3 (PD-4/PD-5), `cdad_packet.py:3815-3842,3930-3949,4049-4052`,
  `cdad-version-check.py:211-236`, `project-execution.md:164-182`; GREEN — ídem + `cdad_packet.py:2874`.
- **Evidencia al re-entry:** focal rojo→verde sobre **fixtures** (una pata `project` divergiendo; un paquete
  `prepared`; un caso de ausencia): la vista **nombra la pata leída** del chequeo, la **resolución** aparece
  sólo con la pata `project`, y la ruta de `prepared` nombra la acción natural; `git diff` acotado.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_011_t3_view_action.py -q`; regresiones
  `tests/test_005_003_t1_compact_view.py`, `tests/test_005_003_t2_examples_execute.py`,
  `tests/test_005_003_f2_idle_history.py`, `tests/test_005_007_t3_open_unit.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si la proyección de la pata exigiera un **veredicto nuevo** o tocar el
  chequeo, **detener** (INV-4); si el texto prometiera la resolución para una pata **no verificada**,
  **detener** (R2).

### T4 — Gate: aceptación de uso (OpenCode con el medidor; Claude Code con conteo propio)
- **Resultado observable / PD cubiertas:** PD-1..PD-6; AC-1..AC-8.
- **Alcance incluido:** verificar AC-1..AC-5 sobre los productos de T1..T3; correr **AC-6** con una **sesión
  nueva real** de OpenCode en reposo y la **versión desplegada**, midiendo con el **medidor de 005-002**
  (`--delegation-dispatch`) sobre el store de OpenCode, con **instrumento y procedencia**; conteo propio de la
  primera acción sobre el transcript; correr **AC-7** con una sesión nueva de Claude Code lanzada por el
  orquestador Claude, con conteo propio sobre su transcript; comparar **like-for-like** con cada línea base
  como **orientación**. **Secuencia:** con T1..T3 verdes se pide el despliegue al dueño; T4 corre después
  (enmienda de la revisión, spec AC-8). **Excluido:** desplegar;
  repetir la línea base; tratar la meta como umbral; presentar el lado CC como medido.
- **Consume:** `project-root-resolution` (`project-root-v1`) de **T1**, `common-entry` (`common-entry-v1`)
  de **T2**, `view-action` (`view-action-v1`) de **T3**. **Produce:** `acceptance-report`
  (`acceptance-report-v1`).
- **Dependencias:** T1, T2, T3. **Gate:** cubre T1/T2/T3 por la estrategia de validación (sus
  focales/comprobaciones) y su cierre es el **gate de la feature**.
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable); *Test* — (gate, sin código).
- **Contexto por rol:** orchestrator — spec §5 (AC-1..AC-8) + líneas base por referencia; architect — lectura.
- **Evidencia al re-entry:** informe con comparación **like-for-like**, medido vs derivado, bandas
  **orientación**, `unknown` con causa; **BLOQUEO** por despliegue si no está autorizado.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** **gate de aceptación de la feature 005-011**; orquestador OpenCode (AC-6) y
  orquestador Claude (AC-7, sesión nueva de Claude Code); architect (lectura).
- **Incertidumbres / detención:** si falta el despliegue → **BLOQUEO declarado**, nunca verde por proximidad;
  si falta evidencia de T1/T2/T3 → **BLOQUEO**, no atajo.

### Bloque canónico `plan-tasks`

```plan-tasks
{
 "validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + alcance declarado + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite. El sentido de los textos de (a) lo juzga la review (INV-5): no se piden tests que decidan el significado de un parrafo por listas de palabras.",
 "tasks": [
  {
   "id": "T1",
   "objective": "Unificar la resolucion de --project-root en cdad_packet.py a resolver contra el cwd y exigir is_dir() (como cdad_result.py), retirando el rechazo especial de status y el diagnostico C4, corrigiendo el texto que quedaria falso y actualizando los dos oraculos declarados.",
   "produce": [
    {
     "artifact": "project-root-resolution",
     "contract": "project-root-v1"
    }
   ],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "skills/cdad-cycle/references/orientation.md",
    "skills/cdad-cycle/references/project-execution.md",
    "tests/test_005_003_t1_compact_view.py",
    "tests/test_005_003_t2_examples_execute.py"
   ],
   "focal_tests": [
    "tests/test_005_011_t1_relative_root.py"
   ],
   "regressions": [
    "tests/test_005_003_t1_compact_view.py",
    "tests/test_005_003_t2_examples_execute.py",
    "tests/test_packet_prepare.py",
    "tests/test_005_003_f2_idle_history.py",
    "tests/test_005_005_t1_replace_conserved.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T2",
   "objective": "Hacer que el Step 1 de cdad-cycle y cdad-epic consulte primero la vista status, que state-detection.md pase a ampliacion condicional con gatillo, y que orientation.md quede indexado en la tabla, referenciando la regla sin copiarla y conservando la rama resume y la fila project-start.md.",
   "produce": [
    {
     "artifact": "common-entry",
     "contract": "common-entry-v1"
    }
   ],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [],
   "observable_checks": [
    "la primera accion prescripta del Step 1 de skills/cdad-cycle/SKILL.md y de skills/cdad-epic/SKILL.md es la vista compacta status (referencia a orientation.md seccion 1); state-detection.md deja de ser el primer paso y pasa a ampliacion condicional con gatillo declarado en la tabla de referencias (una necesidad concreta, con motivo registrado); orientation.md aparece como fila en la tabla de referencias de cdad-cycle; la regla se referencia (orientation.md seccion 1 + project-start.md seccion 11) y no se reescribe; no se crea documento nuevo; la rama resume y la fila project-start.md se conservan y las guardas por ventana de 005-006/005-010 quedan verdes; el sentido de los textos lo juzga la review, no una lista de palabras"
   ],
   "regressions": [
    "tests/test_005_006_t1_start_procedure.py",
    "tests/test_005_006_t6_owner_reviewfix.py",
    "tests/test_005_005_t2_docs_policy.py",
    "tests/test_005_003_t2_examples_execute.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "implementer (docs-only; verificacion por el orquestador y por sentido en la review)"
  },
  {
   "id": "T2b",
   "objective": "Que el prompt del agente orquestador (sources/roles/orchestrator.md y sus derivados) indique como primera accion la vista status de la skill cdad-cycle, por referencia a orientation.md seccion 1; resume como paso siguiente solo con una ejecucion activa y el state completo como ampliacion condicional.",
   "produce": [
    {
     "artifact": "orchestrator-entry",
     "contract": "orchestrator-entry-v1"
    }
   ],
   "consume": [
    {
     "artifact": "common-entry",
     "contract": "common-entry-v1",
     "producer": "T2"
    }
   ],
   "depends_on": [
    "T2"
   ],
   "parallel": [],
   "files": [],
   "observable_checks": [
    "el prompt generado del orquestador (OpenCode y Claude Code) nombra la vista status como primera accion y conserva la rama sin ejecucion activa no resume; make agents idempotente; las guardas de texto existentes siguen verdes"
   ],
   "regressions": [
    "tests/test_005_006_t1_start_procedure.py",
    "tests/test_005_009_t3_spawn_reconciliation.py",
    "tests/test_005_010_t3_references.py",
    "tests/test_cdad_generate.py",
    "tests/test_packet_prepare.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "implementer (docs-only; verificacion por el orquestador)"
  },
  {
   "id": "T3",
   "objective": "Que la vista, ante un DRIFT, nombre la pata que diverge leida del chequeo y diga que lo resuelve solo cuando la pata es project (el proximo prepare republica los derivados), sin confundir ausencia con incoherencia; y que la ruta de un paquete prepared nombre la accion natural (despacharlo) con --replace-packet como rama condicional, sin cambiar entry.",
   "produce": [
    {
     "artifact": "view-action",
     "contract": "view-action-v1"
    }
   ],
   "consume": [],
   "depends_on": [
    "T1"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "skills/cdad-cycle/references/orientation.md"
   ],
   "focal_tests": [
    "tests/test_005_011_t3_view_action.py"
   ],
   "regressions": [
    "tests/test_005_003_t1_compact_view.py",
    "tests/test_005_003_t2_examples_execute.py",
    "tests/test_005_003_f2_idle_history.py",
    "tests/test_005_007_t3_open_unit.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T4",
   "objective": "Gate de aceptacion de la feature: verificar AC-1..AC-5 y correr AC-6 con una sesion nueva real de OpenCode en reposo y la version desplegada (o BLOQUEO), medida con el medidor de 005-002 con --delegation-dispatch sobre el store de OpenCode, declarando instrumento y procedencia, el lado Claude Code como unknown con causa, y las lineas base como orientacion.",
   "produce": [
    {
     "artifact": "acceptance-report",
     "contract": "acceptance-report-v1"
    }
   ],
   "consume": [
    {
     "artifact": "project-root-resolution",
     "contract": "project-root-v1",
     "producer": "T1"
    },
    {
     "artifact": "common-entry",
     "contract": "common-entry-v1",
     "producer": "T2"
    },
    {
     "artifact": "view-action",
     "contract": "view-action-v1",
     "producer": "T3"
    },
    {
     "artifact": "orchestrator-entry",
     "contract": "orchestrator-entry-v1",
     "producer": "T2b"
    }
   ],
   "depends_on": [
    "T1",
    "T2",
    "T3",
    "T2b"
   ],
   "parallel": [],
   "files": [],
   "observable_checks": [
    "una sesion nueva real de OpenCode, sin contexto previo y en reposo, consulta status antes de leer el state completo y llega al primer despacho sin explorar versiones, manifiestos ni el codigo del CLI, medido con el medidor de 005-002 sobre el store de OpenCode con --delegation-dispatch, per sesion y per rol, con instrumento y procedencia declarados; la primera accion de orientacion se observa con conteo propio sobre el transcript porque el medidor no tiene ese hito; los valores se comparan like-for-like con la linea base (70 llamadas, 304.054 caracteres) como orientacion, no como umbral; el lado Claude Code se declara unknown con causa (sin adaptador CC); si el despliegue no esta autorizado se declara BLOQUEO con responsable, nunca verde por proximidad"
   ],
   "regressions": [],
   "integration_gate": "gate de aceptacion de la feature 005-011: AC-1..AC-5 verificados sobre los productos de T1..T3 (focales rojo-a-verde + git diff acotado; T2 por comprobaciones observables y review) y AC-6 con una sesion nueva real medida con el artefacto del repo; el despliegue es del dueno y su ausencia es un BLOQUEO declarado",
   "owner": "orquestador OpenCode (AC-6) y orquestador Claude (AC-7); architect (lectura)"
  }
 ]
}
```

## 5. Trazabilidad PD/AC → tarea

PD-1 → T2; PD-2 → T1; PD-3 → T1; PD-4 → T3; PD-5 → T3; PD-6 → T1/T2/T3 (referencias).
AC-1 → T2; AC-2 → T1; AC-3 → T1; AC-4 → T3; AC-5 → T3; AC-6/AC-7/AC-8 → T4.

## 6. Gate de aceptación de la feature

- **La feature cierra cuando** AC-1..AC-5 tienen evidencia (los focales de T1/T3 rojo→verde con su
  `git diff` acotado; las comprobaciones observables de T2 con las guardas verdes y la review del texto) y
  **AC-6** tiene su medición.
- **El gate de la feature es el de T4.** Con la **versión desplegada** y una **sesión real nueva en reposo**:
  se mide con el medidor de 005-002 (`--delegation-dispatch`) y se declaran las bandas como **orientación**.
  **Mientras el despliegue no esté autorizado (acción del dueño), T4 devuelve BLOQUEO declarado**, nunca
  verde. El **lado CC** se declara **unknown con causa** (sin adaptador CC).
- **Suite completa una vez**, por quien cierra, en un worktree fijado al commit de cierre; `make validate`
  sin fallos nuevos.

## 7. Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**; **sin desplegar**; **sin tocar
  HOME**; **sin leer** `tests/.sensitive-patterns.local`.
- **Sin valores de este VPS** en spec, plan ni producto (INV-6): sin rutas de HOME, sin rutas absolutas del
  dueño, sin ids crudos de sesión.
- **No** reescribir los contratos de 005-003/005-004/005-007/005-005: extensión **aditiva y declarada** o
  referencia. El cambio del comportamiento C4 es **autorizado por la fila 11** y **declarado**, con sus
  **dos** oráculos.
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia. Para comprobar un RED sin
  el arreglo: **worktree**, **nunca `git stash`** en el árbol compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**

## 8. Estado

**Estado: APROBADO.** Se aprobó **junto con la spec** (una sola acción) por el **orquestador OpenCode** el **2026-10-13**, bajo la **HITL delegada del epic-005** (`docs/epics/epic-005-real-operation/execution.md`). El **architect** no aprobó su propia propuesta (entregó este plan como DRAFT). La cabecera DRAFT del rol se conserva como registro de la entrega; el estado vigente es el de esta sección. Rige el **criterio de review vigente del 2026-10-12**. Este plan **no arranca TDD**: el **orquestador Claude revisa** antes de la etapa 3. El bloque canónico `plan-tasks` de §4 fue validado por el rol y **revalidado por el orquestador** con las funciones del propio CLI (`_plan_tasks_from_contract`, `_check_plan_tasks`, `_check_plan_validation_plan` y el render de las cuatro fichas): **OK**, tareas T1..T4, estrategia declarada. La **autorización explícita** de los dos oráculos que cambian (PD-3) está registrada en la spec §12. La firma y los hashes están en `docs/.cdad-state.json` (`stage_history`, `stage: specification`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-13
