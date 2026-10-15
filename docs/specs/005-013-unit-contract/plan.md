> Plan **DRAFT (etapa 2, subetapa `draft`) — SIN APROBAR.** Texto del **architect**
> (`mofgw/deepseek-v4.1-flash`). **Corrección del plan** pedida por la review del orquestador Claude
> (`docs/specs/005-013-unit-contract/review-claude-spec-2026-10-14.md`, versionada en `2d3613a`) y por la
> **fila 13** del plan del epic (`plan.md:46`). **Esta entrega REEMPLAZA el plan aprobado por el orquestador
> OpenCode en `89165d7`:** esa aprobación queda **sustituida**; el contrato vuelve a estar **sin aprobar**
> hasta que el orquestador (HITL delegada del epic) o el dueño re-aprueben esta versión junto con la spec
> corregida. El architect **no** aprueba su propia propuesta (anti-sesgo). Contrato vigente:
> `docs/epics/epic-005-real-operation/plan.md`, fila 13 (`:46`), sha256
> `63dda3b83561a8763a6b3ab9613f2b26029796921cdede4dfd65e7ab3ad059a6`, más «Ajuste de los ciclos
> pendientes» (`:48-88`). Deriva de `docs/specs/005-013-unit-contract/discovery.md` (§1-§13) y de la spec
> corregida de la feature, que se resuelven **por referencia**. El bloque canónico `plan-tasks` de §4 sigue el
> formato de los planes vigentes (`docs/specs/005-011-common-entry/plan.md` §4 y
> `docs/specs/005-007-progressive-planning/plan.md` §4) y se valida con las funciones del propio CLI en
> solo lectura. **Sin valores de este VPS; sin rutas absolutas del dueño ni ids crudos de sesión; sin nombres
> de otros proyectos** (`<home>`, `<repo>`, `<tmp>`, `<ses-…>`, `<ID>`, `<otro-proyecto>`).

# Plan — 005-013-unit-contract

## 1. Ficha de la feature

- **Feature ID:** `005-013-unit-contract` · **Epic:** `epic-005-real-operation` · **Estado:** DRAFT (etapa 2,
  corrección del draft).
- **Resultado buscado (fila 13, `plan.md:46`):** el hash identifica el **contrato que recibió el agente** y
  deja de bloquear globalmente la planificación del proyecto. (a) el contrato de una unidad es una
  **proyección generada** del plan (objetivo/alcance/aceptación de la unidad + restricciones compartidas +
  aprobación y versión de origen), con la unidad localizada **estructuralmente** y **fallback** al contrato
  vigente si no se puede localizar sin ambigüedad; el hash se calcula sobre esa proyección. (b) las
  consecuencias dependen del **tipo de cambio** (sin efecto / registra impacto y decide el orquestador /
  impide las acciones afectadas por **autorización retirada**, con salida). (c) un paquete despachado se
  recibe contra el contrato que **efectivamente recibió** el agente; recibir no lo aprueba. **Fuera de
  alcance:** varias unidades a la vez sobre el mismo state (`active_packet` único). **Prueba decisiva:**
  despachar un architect, agregar una feature independiente al plan y recibir su entrega normalmente;
  después comprobar que un cambio relevante sí exige reconciliación — sobre **tres formas de plan** (este
  epic; uno de la plantilla del producto; un fixture sintético anónimo con la celda de la unidad como enlace
  y sin historia).
- **Contrato y reglas reusadas:** spec §9. **Dependencia del epic:** `005-011` (entrada común), cerrada.
- **Fronteras de contrato (no reescritura):** 005-001 (pin/reemplazo; **I2/PD-18 no se toca**), 005-003
  (vista compacta: **read-only** y límite de bytes), 005-005 (procedencia), 005-007
  (planificación/unidad), 005-011 (entrada común: extensión aditiva): esta feature los **referencia** o los
  **extiende de forma aditiva y declarada** (spec INV-4/INV-5/PD-13). La **operación de reconciliación** de
  un paquete `dispatched` es territorio de **005-012** y **no** se anticipa.
- **Oráculos: churn reducido por el fallback (spec §8 D-1).** Los tests que hardcodean el contrato del
  architect cambian **sólo** si su plan fixture declara una **tabla con la fila de la unidad**; **verificado**
  que hoy ninguno lo hace (los fixtures escriben `# Epic plan fixture …` /
  `# Contract fixture for <role>/<substage>`), así que caen en el **fallback** y conservan su
  comportamiento. Lista de **vigilancia** declarada en spec §8 D-1.
- **Convención de anonimización:** toda la salida usa `<home>`, `<repo>`, `<tmp>`, `<ses-…>`, `<ID>`,
  `<otro-proyecto>`; el mapa real vive en `.cdad/local/` (fuera de git). El fixture de la tercera forma de
  plan es **sintético y anónimo**.

## 2. Ajuste de las unidades del discovery a tareas atómicas

Una tarea por **clase de producto y oráculo**; un **RED** cubre una clase y su **GREEN** va en **otra
sesión**, sin mezclar roles. El discovery (§10/§11) propuso U1 (proyección+publicación+origen), U2
(recepción/resume), U3 (tabla de consecuencias) y U4 (gate); se **reagrupan por clase** así:

| Unidad del discovery | Tarea | Por qué se agrupa así |
|---|---|---|
| **U1** proyección generada + publicación + pin + kind/path **con localizador estructural, fallback y anclas declaradas por el producto**; **U2** recepción/resume contra el contrato recibido | **T1** | Una sola **clase de producto**: el CLI (`cdad_packet.py`) que **genera** la proyección (y el activo del producto que **declara** las anclas) y la **pinea**; la recepción/resume contra los bytes registrados es **consecuencia** de que el `contract.path` apunte a la proyección (no toca `cdad_result.py`). Un focal por clase de oráculo: `prepare` genera/pinea o cae en el fallback; `receive`/`resume` contra el contrato recibido. |
| **U3** consecuencias por tipo de cambio **con línea base, journal idempotente y salida del impedimento** | **T2** | Clase **código del CLI** (`cdad_packet.py`) con focal propio (veredicto por parte + línea base + journal idempotente + falla cerrada + bloque `unit_contract` de `status` de sólo lectura). **Mismo archivo que T1** → se **serializa** (`depends_on: [T1]`). |
| Cierre documental (fuente única, frontera, origen, anclas por declaración del producto) | **T3** | Clase **documental** (referencias/declaraciones); su oráculo son **comprobaciones observables** + la review del texto (INV-8). No comparte archivos con T1/T2. |
| Gate de aceptación (§12 del discovery + tres formas de plan de B1.4 + focal de B2 + P1) | **T4** | **Gate** (no RED/GREEN de producto): `observable_checks` + gate de integración; requiere T1/T2/T3. |

**Qué NO se planifica** (fuera de alcance, spec §7): el registro de transiciones (005-012) y la
reconciliación de un paquete `dispatched`; la entrada común (005-011) y la vista compacta (005-003); el
adaptador Claude Code; **no** se reabren 005-001/005-003/005-005/005-007/005-011; sin CI, WebUI, sandbox,
plataforma de jobs, sin tocar HOME, sin desplegar, sin push. **No** se escriben listas de títulos por
proyecto ni tests que decidan el sentido de un párrafo.

**Nota de paralelismo.** T1 y T2 editan **el mismo archivo** (`skills/cdad-cycle/scripts/cdad_packet.py`)
→ **no** paralelas (`depends_on: [T1]`), consistente con el validador del producto. T3 (documental) podría
declararse paralela a T1/T2; se deja `parallel: []` (conservador, sin ganancia de integración).

## 3. Estrategia de validación (declarada una vez)

- **Dos niveles.** **Siempre:** procedencia, `git diff` contra el alcance del paquete, alcance declarado y
  **pruebas focales** (segundos). **Sólo con un motivo concreto:** la suite o la integración. Se **reutiliza
  evidencia equivalente** con procedencia verificada **por referencia** a
  `skills/cdad-cycle/references/re-entry.md` (*Equivalence of a registered run*).
- **Suite completa una vez, al cierre** (motivo: toca el CLI y los contratos de paquete; cierra la
  feature). No se corre dentro de cada tarea; **no se corre salvo que el paquete lo pida** (la corre quien
  cierra).
- **Comandos concretos por encargo** (fichas de §4), **tomados del bloque `plan-tasks`** y rendidos en el
  paquete (mecanismo de 005-003 T6). RED: el focal debe fallar por aserción (no por import/sintaxis).
  GREEN: focal verde + regresiones del área.
- **El sentido de los textos lo juzga la review** (INV-8): T3 se valida con **comprobaciones observables**
  y con la review; **no** con tests que decidan el significado de un párrafo por listas de palabras.
- **El cierre incluye el commit** y el reporte del rol lo declara; un rol que termina sin commitear es
  **bloqueo declarado**.
- **Sin `--no-verify`; sin push; sin desplegar; sin tocar HOME; sin leer `tests/.sensitive-patterns.local`.**

## 4. Fichas mínimas de tarea y bloque canónico

### T1 — Proyección de unidad con localizador estructural, fallback declarado y anclas por declaración del producto; publicación, pin y kind/path; recepción/resume contra el contrato recibido
- **Resultado observable / PD cubiertas:** PD-1, PD-2, PD-3, PD-4, PD-5, PD-6 (y base de PD-7..PD-12).
- **Alcance incluido:**
  - **Localizador estructural** (PD-1): recorrer las **tablas** del plan y localizar la **única** fila de
    cuerpo que contiene `execution.feature_id` **como token completo** (delimitado por caracteres que no
    pueden ser parte de un id); la parte `unit` es el **encabezado de esa tabla** (fila de encabezado +
    separador) + esa fila, **verbatim**. La celda puede ser un **enlace**, llevar texto alrededor o estar
    entre backticks. **Sin** mirar el título de la sección y **sin** igualdad exacta de la celda.
  - **Fallback declarado** (PD-2): cero filas o más de una → **no** se genera ni publica proyección;
    `contract` = `approved-epic-plan` + `docs/epics/<epic_id>/plan.md` + sha del plan; **rc=0**; el motivo
    (cero/más de una, con la ruta del plan) va a **stderr** (stdout sigue siendo el `PACKET.md` byte a byte)
    y a `status` (`mode: "fallback"`).
  - **Anclas por declaración del producto** (PD-3): declaración **legible por máquina** en el activo del
    producto `skills/cdad-epic/assets/epic-plan-template.md` (historia y autorización; título inglés de la
    plantilla + la forma en español de los planes del producto); reconocimiento por título normalizado
    (igualdad o prefijo en frontera no alfanumérica); historia ⇒ **excluida** de la proyección; autorización
    ⇒ parte `shared` **etiquetada** en el origen, **sin** efecto de veredicto. Declaración ausente/ilegible
    ⇒ ninguna ancla (conservador, sin falla cerrada nueva).
  - **Generador determinista**: bloque de **origen** (`unit`, `plan`, `plan_sha256`, `approved_by`,
    `policy_sha256`, lista de partes con clase, traza del localizador y de las anclas) + parte `unit` +
    partes `shared` (todas las `##` menos las de historia, con las líneas de la tabla de unidades removidas
    de su sección).
  - **Publicación y pin** (PD-4/PD-5): `.cdad/packets/<packet_id>/UNIT-CONTRACT.md` en la misma generación;
    `contract` = `{kind: "approved-unit-contract", path, sha256, commit: null}`;
    `active_packet.contract_sha256` = el digest. `VALID_CONTRACT_KINDS` (`:52`) admite el kind;
    `_contract_for` (`:995-1008`) y `validate_request` (`:814-819`) aceptan **los dos** pares válidos
    (proyección y fallback) para el architect.
  - **Orden generación→validación** (VERIFY V6): publicar antes de validar (determinista e idempotente) o
    validar contra los bytes staged de la transacción; **sin** tocar la semántica de `validate_request`.
  - **Focales con las TRES formas de plan** (B1.4): (i) la de este epic; (ii) una generada desde la
    plantilla del producto; (iii) un **fixture sintético y anónimo** con la forma de los planes de otro
    proyecto (celda de unidad como **enlace**, **sin** historia ni autoridad; ids y títulos inventados).
  - **Excluido:** tocar `cdad_result.py` (el esquema del recibo **no** cambia), el pin `specification`
    (I2/PD-18), la política, el hashing de otros contratos, el render de otros roles.
- **Consume:** — . **Produce:** `unit-projection` (`unit-projection-v1`).
- **Dependencias:** — .
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`,
  `skills/cdad-epic/assets/epic-plan-template.md` (la declaración de anclas); *Test*
  `tests/test_005_013_t1_unit_projection.py` (+ sus fixtures de plan, incluido el **anónimo**).
- **Contexto por rol:** RED — spec §2.1-§2.3/§3 (PD-1..PD-6),
  `cdad_packet.py:52,469-498,748-860,995-1008,1041-1045,1346-1360,3263-3345,3510-3600`;
  `skills/cdad-epic/assets/epic-plan-template.md:25-31,63-77`; las formas de plan reales del repo
  (spec §9); GREEN — ídem + `_publish_generation` (`:3263-3345`, `extra_writes`) y
  `cdad_result.py:493-589`.
- **Evidencia al re-entry:** focal rojo→verde (`prepare` produce `UNIT-CONTRACT.md`; digest coincide con
  `contract.sha256` y `active_packet.contract_sha256`; kind/path exactos; el localizador funciona con la
  celda como enlace; plan sin fila / con dos filas → **fallback** con `approved-epic-plan` y el motivo en
  stderr y en `status`; plan sin anclas → conservador, sin falla cerrada; `receive`/`resume` rc=0 tras
  **agregar una unidad futura independiente**) + `git diff` acotado; **sin** cambios en el esquema del
  recibo.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_013_t1_unit_projection.py -q`; regresiones
  `tests/test_packet_prepare.py`, `tests/test_role_packet_render.py`,
  `tests/test_005_001_t1_role_approval.py`, `tests/test_005_001_t4_decisive.py`,
  `tests/test_005_001_tcorr.py`, `tests/test_005_005_t1_replace_conserved.py`,
  `tests/test_005_005_t3_provenance.py`, `tests/test_005_006_t5_acceptance.py`,
  `tests/test_005_007_t4_architect_report_materialization.py`, `tests/test_004_002_t56_reviewfix.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si el generador exigiera un **bloque mantenido a mano** en el plan del
  epic, **detener** (viola fuente única, spec PD-13); si el localizador exigiera una **lista de títulos por
  proyecto** o el título de la sección, **detener** (viola PD-1/INV-10); si el orden generación→validación
  exigiera relajar `validate_request`, **detener** y declararlo.

### T2 — Veredicto de consecuencias: línea base, current/impact/impeded, journal idempotente, salida del impedimento y bloque `unit_contract` de sólo lectura
- **Resultado observable / PD cubiertas:** PD-7, PD-8, PD-9, PD-10, PD-11.
- **Alcance incluido:** operación **de lectura** `validate-unit-contract` que **regenera** la proyección viva
  y la compara con la **línea base** (la proyección registrada del **último paquete de la unidad**:
  publicación más reciente del `UNIT-CONTRACT.md`; empate → id de paquete mayor; el `active_packet` cuenta
  como candidato; sin paquete previo → `current`) **por parte** (ignorando el origen): veredicto `current`
  (sin efecto), `impact` (escribe el **registro durable de impacto** en
  `.cdad/packets/<baseline_packet_id>/.impact.json`, forma de `.superseded.json`: `reason`,
  `contract_sha256_old`, `contract_sha256_new`, `changed_parts`, **idempotente** por el par de digests) o
  `impeded` (rc=2: **autorización retirada** —`approval pending` / `state incoherent`— con la **salida**
  nombrada: registrar la aprobación `epic-plan` bajo la HITL; el paquete siguiente toma la proyección nueva
  como línea base). Bloque **aditivo** `unit_contract` en la vista compacta (`status`) que **informa** el
  veredicto (`mode`, línea base, digest vivo, veredicto, partes que difieren, motivo) y **no escribe nada**.
  **Excluido:** escribir el state (la decisión del orquestador va a `stage_history.note`), aprobar, cambiar
  `semantic_status`, parsear prosa, inventar el vocabulario de causas ya cubiertas, hacer que `status`
  escriba, y que **alguna sección del plan** produzca `impeded`.
- **Consume:** `unit-projection` (`unit-projection-v1`) de **T1**. **Produce:** `change-consequence`
  (`change-consequence-v1`).
- **Dependencias:** T1 (mismo archivo `cdad_packet.py` → **serializada**).
- **Archivos:** *Create/Modify* `skills/cdad-cycle/scripts/cdad_packet.py`; *Test*
  `tests/test_005_013_t2_change_classification.py`.
- **Contexto por rol:** RED — spec §2.4-§2.6/§2.8/§3 (PD-7..PD-11), `cdad_packet.py:2078-2086` y `:2103`
  (forma y publicación del journal), `:1406-1411` (`approval pending`), `:501-531` (`state incoherent`),
  `:1811-1836` (`packet obsolete`), `:3900-3995` (`_entry_selection`/`_next_route`), `:4042-4115` (vista
  `status`); GREEN — ídem.
- **Evidencia al re-entry:** focal rojo→verde sobre **fixtures** (una unidad independiente agregada →
  `current`; la fila de la unidad activa editada → `impact` con las partes nombradas y el journal durable;
  la sección de autorización editada → `impact` (nunca `impeded`); autorización retirada → `impeded` rc=2
  con la salida nombrada; aprobación registrada → `prepare` rc=0 y línea base nueva; **dos** `status`
  consecutivos byte-idénticos y **sin** `.impact.json`; **dos** `validate-unit-contract` con el mismo par →
  journal byte-idéntico); `git diff` acotado; la vista sigue siendo `compact-view-v1` con campos existentes
  conservados.
- **Verificación RED→GREEN:** `python3 -m pytest tests/test_005_013_t2_change_classification.py -q`;
  regresiones `tests/test_packet_prepare.py`, `tests/test_005_001_t1_role_approval.py`,
  `tests/test_005_003_t1_compact_view.py`, `tests/test_005_003_t2_examples_execute.py`,
  `tests/test_005_007_t3_open_unit.py`, `tests/test_005_005_t1_replace_conserved.py`.
- **Integración / responsable:** `@validation_strategy`; RED test-writer; GREEN implementer.
- **Incertidumbres / detención:** si clasificar exigiera decidir el significado de un párrafo por listas de
  palabras, **detener** (INV-8); si el registro durable exigiera escribir el state, **detener** (INV-1); si
  `impeded` exigiera una comparación de bytes o un juicio de prosa (en vez de la autorización retirada),
  **detener** y reportar (PD-10).

### T3 — Referencias y fronteras documentales (fuente única; origen; anclas por declaración del producto; pin de la spec intacto)
- **Resultado observable / PD cubiertas:** PD-12, PD-13 (INV-4/INV-5/INV-10).
- **Alcance incluido:** declarar **por referencia** (sin copiar la regla) en
  `skills/cdad-cycle/references/project-execution.md` (autoridad del architect) el contrato de unidad, su
  origen y su **salida del impedimento**, y en `docs/specs/005-013-unit-contract/` (spec/plan) las
  fronteras: **no** se crea un bloque `plan-tasks` mantenido a mano en el plan del epic; la proyección se
  **genera**; las anclas son una **declaración del producto** (no una lista por proyecto); el pin
  `specification` (I2/PD-18) **no** se toca. **Excluido:** crear una referencia «unit contract» nueva que
  duplique una regla; tocar los contratos de 005-001/005-003/005-005/005-007/005-011; mantener una lista de
  títulos por proyecto.
- **Consume:** `unit-projection` (`unit-projection-v1`) de **T1**, `change-consequence`
  (`change-consequence-v1`) de **T2** (referencia al comportamiento declarado). **Produce:**
  `unit-contract-references` (`unit-contract-references-v1`).
- **Dependencias:** T1, T2. docs-only → `files: []` (convención de 005-003 T4 / 005-007 T6); los paths
  viven en esta ficha: `skills/cdad-cycle/references/project-execution.md`.
- **Contexto por rol:** test-writer — spec §2.7/§7 (PD-12/PD-13), `project-execution.md:52-84,165-233`;
  reviewer — el texto **por sentido** (INV-8).
- **Evidencia al re-entry:** comprobación observable roja→verde (la autoridad del architect nombra el
  contrato de unidad, su origen y la salida del impedimento, por referencia, sin duplicar la regla; no hay
  bloque `plan-tasks` mantenido a mano en el plan del epic; no hay lista de títulos por proyecto); `git diff`
  acotado; las guardas de texto existentes verdes.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** `@validation_strategy`; implementer (docs-only); verificación del
  orquestador y, por sentido, la review.
- **Incertidumbres / detención:** si conservar una guarda exigiera **copiar** la regla, **detener**
  (INV-4); si el texto se leyera como «el architect deja de autorizarse por el plan», **detener** y
  reformular (PD-12).

### T4 — Gate: aceptación de la feature (prueba decisiva, CLI real, proyecto descartable, TRES formas de plan; focales de B2 y P1)
- **Resultado observable / PD cubiertas:** PD-1..PD-13; AC-1..AC-10.
- **Alcance incluido:** verificar AC-1..AC-8 sobre los productos de T1..T3; correr la **prueba decisiva**
  (AC-9) con el **CLI real** sobre un **proyecto descartable** (`<tmp>`; **nunca** este repo, **nunca**
  HOME; `HOME` del subproceso en un tempdir vacío) sobre **tres formas de plan**: **(i)** la de este epic;
  **(ii)** una generada desde la plantilla del producto; **(iii)** un **fixture sintético y anónimo** con la
  forma de los planes de otro proyecto (celda de unidad como **enlace**, **sin** historia ni autoridad).
  En las **tres**: **tramo 1** (despachar un architect → agregar una unidad futura independiente →
  `receive` rc=0; veredicto `current`) y **tramo 2** (un cambio relevante → `impact` con journal durable;
  la sección de autorización editada → `impact`, nunca `impeded`); más el **focal de B2** (autorización
  retirada → `impeded` rc=2; registrar la aprobación `epic-plan` → `prepare` rc=0 y línea base nueva) y el
  **focal de P1** (`status` byte-idéntico y sin journal; journal idempotente). Declarar instrumento y
  procedencia. **Excluido:** desplegar; repetir la línea base; tratar una meta como umbral; presentar un
  doble como CLI real; usar este repo o HOME; declarar verde por proximidad.
- **Consume:** `unit-projection` (`unit-projection-v1`) de **T1**, `change-consequence`
  (`change-consequence-v1`) de **T2**, `unit-contract-references` (`unit-contract-references-v1`) de **T3**.
  **Produce:** `acceptance-report` (`acceptance-report-v1`).
- **Dependencias:** T1, T2, T3. **Gate:** cubre T1/T2/T3 por la estrategia de validación (sus
  focales/comprobaciones) y su cierre es el **gate de la feature**.
- **Archivos:** *Create* evidencia del informe (fuera del árbol publicable); *Test* — (gate, sin código).
- **Contexto por rol:** orchestrator — spec §5 (AC-1..AC-10) + discovery §12 por referencia; architect —
  lectura.
- **Evidencia al re-entry:** informe con las salidas del CLI de los tramos y de las **tres** formas (rc y
  diagnósticos), el `REQUEST.json` y el recibo durables, el diff del plan de cada forma (con su medición de
  líneas/bytes), la comparación de digests, la salida de `status` antes y después (byte-identidad) y el
  journal de impacto repetido (idempotencia); **BLOQUEO** declarado si falta un insumo, nunca verde por
  proximidad.
- **Verificación:** `observable_checks`.
- **Integración / responsable:** **gate de aceptación de la feature 005-013**; orquestador OpenCode
  (prueba decisiva, HITL delegada del epic); architect (lectura).
- **Incertidumbres / detención:** si falta la evidencia de T1/T2/T3 → **BLOQUEO declarado**, no atajo; la
  reconciliación de un paquete `dispatched` **no** se inventa (005-012); si una de las tres formas no se
  puede correr (p. ej. falta el fixture anónimo), **BLOQUEO** con el insumo faltante nombrado.

### Bloque canónico `plan-tasks`

```plan-tasks
{
 "validation_strategy": "Verificacion en dos niveles: siempre procedencia + git diff contra el alcance + alcance declarado + pruebas focales (segundos); suite o integracion solo con un motivo concreto; la suite completa la corre una vez quien cierra; se reutiliza evidencia equivalente con procedencia verificada (regla canonica en skills/cdad-cycle/references/re-entry.md, seccion Equivalence of a registered run), sin repetir la suite. El sentido de los textos lo juzga la review (INV-8): no se piden tests que decidan el significado de un parrafo por listas de palabras.",
 "tasks": [
  {
   "id": "T1",
   "objective": "Generar deterministamente la proyeccion de unidad desde el plan del epic localizando la unidad de forma ESTRUCTURAL (la unica fila de una tabla del plan que contiene el id de la feature como token completo, con el encabezado de esa tabla), excluyendo las secciones de historia que declara el propio producto, publicarla una vez junto al paquete y pinear su digest como kind approved-unit-contract; si la unidad no se localiza sin ambiguedad, volver al contrato vigente (approved-epic-plan, plan completo) informandolo, de modo que la validacion, el resume y la recepcion se hagan contra los bytes registrados y no contra el plan vivo.",
   "produce": [
    {
     "artifact": "unit-projection",
     "contract": "unit-projection-v1"
    }
   ],
   "consume": [],
   "depends_on": [],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py",
    "skills/cdad-epic/assets/epic-plan-template.md"
   ],
   "focal_tests": [
    "tests/test_005_013_t1_unit_projection.py"
   ],
   "regressions": [
    "tests/test_packet_prepare.py",
    "tests/test_role_packet_render.py",
    "tests/test_005_001_t1_role_approval.py",
    "tests/test_005_001_t4_decisive.py",
    "tests/test_005_001_tcorr.py",
    "tests/test_005_005_t1_replace_conserved.py",
    "tests/test_005_005_t3_provenance.py",
    "tests/test_005_006_t5_acceptance.py",
    "tests/test_005_007_t4_architect_report_materialization.py",
    "tests/test_004_002_t56_reviewfix.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T2",
   "objective": "Clasificar el tipo de cambio comparando la proyeccion viva con la linea base registrada (la proyeccion del ultimo paquete de la unidad) por parte e ignorando el origen, en tres veredictos: current (sin efecto), impact (registro durable e idempotente con la forma del journal .superseded.json y decision del orquestador) e impeded (autorizacion retirada, con la salida existente nombrada: registrar la aprobacion epic-plan), reportando el veredicto de forma aditiva en la vista compacta sin escribir nada.",
   "produce": [
    {
     "artifact": "change-consequence",
     "contract": "change-consequence-v1"
    }
   ],
   "consume": [
    {
     "artifact": "unit-projection",
     "contract": "unit-projection-v1",
     "producer": "T1"
    }
   ],
   "depends_on": [
    "T1"
   ],
   "parallel": [],
   "files": [
    "skills/cdad-cycle/scripts/cdad_packet.py"
   ],
   "focal_tests": [
    "tests/test_005_013_t2_change_classification.py"
   ],
   "regressions": [
    "tests/test_packet_prepare.py",
    "tests/test_005_001_t1_role_approval.py",
    "tests/test_005_003_t1_compact_view.py",
    "tests/test_005_003_t2_examples_execute.py",
    "tests/test_005_007_t3_open_unit.py",
    "tests/test_005_005_t1_replace_conserved.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"
  },
  {
   "id": "T3",
   "objective": "Declarar por referencia, sin copiar la regla, el contrato de unidad, su origen y la salida del impedimento en la autoridad del architect, y fijar las fronteras documentales: la proyeccion se genera (no se mantiene un bloque plan-tasks a mano en el plan del epic), las anclas son una declaracion del producto y no una lista de titulos por proyecto, y el pin de la spec de los roles de construccion no se toca.",
   "produce": [
    {
     "artifact": "unit-contract-references",
     "contract": "unit-contract-references-v1"
    }
   ],
   "consume": [
    {
     "artifact": "unit-projection",
     "contract": "unit-projection-v1",
     "producer": "T1"
    },
    {
     "artifact": "change-consequence",
     "contract": "change-consequence-v1",
     "producer": "T2"
    }
   ],
   "depends_on": [
    "T1",
    "T2"
   ],
   "parallel": [],
   "files": [],
   "observable_checks": [
    "la autoridad del architect (skills/cdad-cycle/references/project-execution.md) nombra el contrato de unidad, su origen y la salida del impedimento por referencia a la regla, sin duplicarla; no existe un bloque plan-tasks mantenido a mano en el plan del epic; no hay una lista de titulos por proyecto (las anclas son una declaracion del producto); el pin specification (contract_path + contract_sha256, PD-18 de 005-001) queda intacto; no se crea documento nuevo que duplique una regla; las guardas de texto existentes quedan verdes y el sentido del texto lo juzga la review"
   ],
   "regressions": [
    "tests/test_005_005_t2_docs_policy.py",
    "tests/test_005_006_t1_start_procedure.py"
   ],
   "integration_gate": "@validation_strategy",
   "owner": "implementer (docs-only; verificacion por el orquestador y por sentido en la review)"
  },
  {
   "id": "T4",
   "objective": "Gate de aceptacion de la feature: verificar AC-1..AC-8 sobre los productos de T1..T3 y correr la prueba decisiva (AC-9) con el CLI real sobre un proyecto descartable en TRES formas de plan (la de este epic, una generada desde la plantilla del producto y un fixture sintetico anonimo con la celda de la unidad como enlace y sin historia): en las tres, despachar un architect, agregar una unidad futura independiente, receive rc=0 con veredicto current, y un cambio relevante que registra el impacto; mas el focal de la autorizacion retirada (impeded rc=2; registrar la aprobacion epic-plan -> prepare rc=0) y el focal de solo lectura e idempotencia de la vista y del journal, declarando instrumento y procedencia.",
   "produce": [
    {
     "artifact": "acceptance-report",
     "contract": "acceptance-report-v1"
    }
   ],
   "consume": [
    {
     "artifact": "unit-projection",
     "contract": "unit-projection-v1",
     "producer": "T1"
    },
    {
     "artifact": "change-consequence",
     "contract": "change-consequence-v1",
     "producer": "T2"
    },
    {
     "artifact": "unit-contract-references",
     "contract": "unit-contract-references-v1",
     "producer": "T3"
    }
   ],
   "depends_on": [
    "T1",
    "T2",
    "T3"
   ],
   "parallel": [],
   "files": [],
   "observable_checks": [
    "el CLI real (no un doble) sobre un proyecto descartable en <tmp>, nunca este repo ni HOME, con HOME del subproceso en un tempdir vacio, en TRES formas de plan (la de este epic; una generada desde la plantilla del producto; un fixture sintetico anonimo con la celda de la unidad como enlace y sin historia ni autoridad): en las tres, despachar un architect, agregar una unidad futura independiente al plan y receive devuelve rc=0 con packet_validation/identity_validation passed, semantic_status pending y veredicto current; un cambio en el alcance o una dependencia de la unidad activa deja el veredicto impact con el registro durable (los dos digests y las partes que difieren), y una seccion de autorizacion editada deja impact (nunca impeded); una autorizacion retirada deja impeded con rc=2 y registrar la aprobacion epic-plan deja prepare rc=0 con linea base nueva; dos status consecutivos dejan el proyecto byte a byte identico (sin journal) y dos validate-unit-contract con el mismo par de digests dejan el journal byte a byte identico; la evidencia incluye las salidas del CLI (rc y diagnosticos), el REQUEST.json y el recibo durables, el diff del plan de cada forma con su medicion de lineas/bytes y la comparacion de digests; si falta un insumo se declara BLOQUEO, nunca verde por proximidad; la reconciliacion de un paquete dispatched no se inventa (005-012)"
   ],
   "regressions": [],
   "integration_gate": "gate de aceptacion de la feature 005-013: AC-1..AC-8 verificados sobre los productos de T1..T3 (focales rojo-a-verde + git diff acotado; T3 por comprobaciones observables y review) y AC-9 con la prueba decisiva del CLI real sobre un proyecto descartable en las TRES formas de plan, con los focales de B2 (autorizacion retirada -> impeded; aprobacion registrada -> prepare rc=0) y de P1 (status de solo lectura; journal idempotente) y con instrumento y procedencia declarados; la suite completa la corre una vez quien cierra",
   "owner": "orquestador OpenCode (HITL delegada del epic); architect (lectura)"
  }
 ]
}
```

## 5. Trazabilidad PD/AC → tarea

PD-1 → T1; PD-2 → T1; PD-3 → T1; PD-4 → T1; PD-5 → T1; PD-6 → T1; PD-7 → T2; PD-8 → T2; PD-9 → T2;
PD-10 → T2; PD-11 → T2; PD-12 → T3; PD-13 → T3 (referencias) + T1/T2 (extensión aditiva).
AC-1 → T1; AC-2 → T1; AC-3 → T1; AC-4 → T1/T4; AC-5 → T2/T4; AC-6 → T2/T4; AC-7 → T2/T4; AC-8 → T3;
AC-9 → T4; AC-10 → T4 (cierre).

## 6. Gate de aceptación de la feature

- **La feature cierra cuando** AC-1..AC-8 tienen evidencia (los focales de T1/T2 rojo→verde con su
  `git diff` acotado; las comprobaciones observables de T3 con las guardas verdes y la review del texto) y
  **AC-9** tiene su **prueba decisiva**.
- **El gate de la feature es el de T4.** Con el **CLI real** y un **proyecto descartable** (`<tmp>`; nunca
  este repo, nunca HOME) y **tres formas de plan**: **tramo 1** (unidad independiente → `receive` rc=0,
  veredicto `current`), **tramo 2** (cambio relevante → `impact`; sección de autorización editada →
  `impact`, nunca `impeded`), **focal de B2** (autorización retirada → `impeded`; aprobación registrada →
  `prepare` rc=0) y **focal de P1** (`status` de sólo lectura; journal idempotente). **Mientras falte un
  insumo, T4 devuelve BLOQUEO declarado**, nunca verde. La **reconciliación** de un paquete `dispatched`
  **no** se inventa (005-012).
- **Suite completa una vez**, por quien cierra, en un worktree fijado al commit de cierre; `make validate`
  sin fallos nuevos.

## 7. Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**; **sin desplegar**; **sin tocar
  HOME**; **sin leer** `tests/.sensitive-patterns.local`.
- **Sin valores de este VPS** en spec, plan ni producto (INV-7): sin rutas de HOME, sin rutas absolutas del
  dueño, sin ids crudos de sesión, **sin nombres de otros proyectos** (el fixture de la tercera forma de
  plan es **sintético y anónimo**).
- **No** reescribir los contratos de 005-001/005-003/005-005/005-007/005-011: extensión **aditiva y
  declarada** o referencia. El cambio del contrato del architect (kind/path) es **autorizado por la fila
  13** y **declarado**; el **fallback** conserva el contrato vigente y evita el churn de oráculos (spec §8
  D-1).
- **Sin volcar salidas enormes** al contexto; evidencia completa por referencia. Para comprobar un RED sin
  el arreglo: **worktree**, **nunca `git stash`** en el árbol compartido.
- **Ante un obstáculo fuera de alcance: entregar el diagnóstico, no fabricar registros.**

## 8. Estado

**Estado: APROBADO.** Este plan **reemplaza** el aprobado por el **orquestador OpenCode** en `89165d7`
(aprobación **sustituida**). Se aprobó **junto con la spec, en una sola acción**, por el **orquestador
OpenCode** el **2026-10-14**, bajo la **HITL delegada del epic-005**
(`docs/epics/epic-005-real-operation/execution.md`). El **architect** no aprobó su propia propuesta
(entregó este plan como DRAFT; su cabecera DRAFT se conserva como registro de la entrega). El bloque
canónico `plan-tasks` de §4 fue validado por el rol y **revalidado por el orquestador** con las funciones
del propio CLI (`_plan_tasks_from_contract`, `_check_plan_tasks`, `_check_plan_validation_plan`): **OK**,
T1..T4, estrategia declarada. Rige el **criterio de review vigente del 2026-10-12** (`execution.md:48-59`).
Este plan **no arranca TDD**: el **orquestador Claude revisa** antes de la etapa 3. La firma y los hashes
están en `docs/.cdad-state.json` (`stage_history`, `stage: specification`, con `contract_path`/
`contract_sha256` y `plan_path`/`plan_sha256`).

Status: Approved by orchestrator OpenCode (epic-005 delegated HITL) on 2026-10-14
