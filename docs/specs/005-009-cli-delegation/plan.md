> Plan **aprobado** (2026-10-10) junto con la spec. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado por el orquestador (receive + materialize create-only, ADR-003);
> aprobado por el **orquestador OpenCode** bajo la delegación HITL de epic-005 (`execution.md`).
> Construcción según CDAD stages 3–5 (TDD con test-writer/implementer por
> paquete, una única review formal al final y Memory Bank al cierre). Insumo:
> `docs/specs/005-009-cli-delegation/discovery.md`. Formato canónico de la ficha y del bloque
> `plan-tasks`: **por referencia**, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
> §4 y **§4.1** (NO se reproduce su formato aquí). Contrato:
> `docs/epics/epic-005-real-operation/plan.md` (fila de orden 5, `:38`).

## Plan — 005-009-cli-delegation

**Feature ID:** `005-009-cli-delegation` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-10, orquestador OpenCode, HITL delegada epic-005).

### Ajuste de las unidades propuestas al discovery

El plan de origen (`priority-perl-cli-plan-2026-10-10.md` §4) propone **T1 inventario y contrato**,
**T2 adaptador OpenCode**, **T3 recorrido real y procedimiento**. Ajuste al discovery:

- La parte de **inventario** de T1 **ya fue entregada por el discovery §3** (búsqueda acotada que
  documenta que **no existe un dispatcher previo como script** en el producto y que el mecanismo
  existe). Por eso T1 se concentra en el **contrato y la interfaz común**.
- La **reconciliación de la prohibición de spawn** (criterio del plan §4) es un cambio
  documental de **archivos disjuntos** del código de la interfaz: se separa como **T3** para
  permitir paralelismo seguro con T1.
- El **recorrido real y el procedimiento** pasan a **T4** (aceptación/integración), porque consumen
  la interfaz (T1), el adaptador (T2) y la reconciliación (T3).

Resultado: **T1 (interfaz común) ∥ T3 (reconciliación de spawn)**; **T2 (adaptador OpenCode)
depende de T1**; **T4 (aceptación) depende de T1, T2 y T3**.

### Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**.
- **No** instalar CDAD en HOME ni activar versiones, ni operar producción (reservado al dueño).
  **No** ejecutar el CLI del repo para **operar** este ciclo (el repo se **desarrolla**; el ciclo
  corre con la instalación vigente).
- **No** leer `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo: **worktree**, nunca `git stash` en el árbol compartido.
- No volcar salidas enormes al contexto. **No** comunicar procesos por `/tmp`.
- **Sin valores de este VPS** (rutas absolutas, proveedor, modelo concreto, servidor, tiempos) en
  producto ni en contratos públicos (INV-7): la configuración llega por config de ejecución
  (local, git-ignorada) o flags.
- **Gate de tests (metodología común, dueño único `stage-3-tdd.md` §«Test evidence policy»).**
  Durante el trabajo: **focales + módulos tocados**. **Suite completa al cierre de la feature**
  (toca `skills/**`, `sources/**`, `agents/**` y `tests/**`), más `make validate` al cierre. Sin
  duplicar la regla.
- **Frontera:** **no** scheduler, **no** instalación automática de CLI, **no** sandbox; **no** se
  implementan todos los destinos (solo OpenCode); la dirección inversa y otros CLI quedan después.
  **POLICY-CLASS, CI y plataforma universal de jobs quedan FUERA.**
- Ante un obstáculo fuera del ámbito: entregar el diagnóstico, no fabricar registros.

### Tareas

#### T1 — Interfaz común de delegación (producto) · PD-1, PD-2, PD-3, PD-8 · INV-1..INV-3, INV-7
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_delegate.py` (**Create**): la CLI común de delegación,
    agnóstica del destino. Reutiliza `cdad_packet` (carga/render/validación del paquete publicado
    y registro I8 `prepare --record-dispatch`); resuelve el adaptador por **convención de módulo**
    (`cdad_delegate_<id>.py` en el mismo directorio); **transporta el `PACKET.md` byte-idéntico**;
    devuelve el esquema de salida `{attempt, session, termination, delivery_ref, diagnosis}`.
    **Nunca** escribe `docs/.cdad-state.json` ni crea otro ledger.
  - `scripts/cdad_delegate.py` (**Create**): wrapper `runpy` del canónico (patrón
    `scripts/cdad_packet.py`).
  - `skills/cdad-cycle/references/cli-delegation.md` (**Create**): el contrato de la interfaz
    (esquema de entrada/salida, vocabulario de terminación, ubicación de la configuración y
    portabilidad, regla «un adaptador por destino», procedimiento para otro coordinador, límites
    honestos). **Referencia** los dueños existentes; no los copia.
  - `tests/test_005_009_t1_interface.py` (**New**): comportamiento observable con un **destino de
    prueba** (módulo por convención): el paquete se transporta byte-idéntico; el registro I8 tiene
    la forma cerrada con `role`/`substage` del paquete y `provenance` campo→fuente; el vocabulario
    de terminación; el state **no** cambia; **no** hay valores de este VPS en producto.
- **Produce**: `interfaz-comun-delegacion` (`spec-005-009-PD1-PD2-PD3-PD8`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T3 (archivos disjuntos).
- **TDD steps**: RED (la CLI existe; con un destino de prueba transporta el paquete byte-idéntico;
  registra I8 con la forma cerrada; clasifica la terminación; no escribe el state; el barrido de
  portabilidad pasa) → GREEN (mínimo: la interfaz + el wrapper + la referencia) → focales +
  módulos tocados.
- **Evidencia**: bytes del paquete transportado; el registro I8 publicado; diff de state vacío;
  salida de `pytest` focal.

#### T2 — Adaptador OpenCode (producto) · PD-4, PD-5, PD-6, PD-7 · INV-4..INV-6
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (**Create**): el adaptador del destino
    OpenCode. Construye la invocación desde la **config de ejecución** (binario/versión, modelo,
    tiempos; **nunca** hardcodeados); **verifica el modo de carga soportado** contra los agentes
    derivados publicados del proyecto (**falla cerrado**, sin fallback a un agente genérico);
    invoca la sesión de rol; **espera sobre una señal durable** (no el rc del cliente); captura el
    texto final; produce la entrega durable por el `receive` existente; clasifica la terminación
    (`completed`/`blocked`/`transport-error`/`timeout`/`cancelled`).
  - `tests/test_005_009_t2_opencode_adapter.py` (**New**): comportamiento determinista con un
    **binario OpenCode falso** (script que emite un texto final acordado): con una entry
    `mode: subagent` el adaptador **rechaza** y **no** despacha sesión (sin fallback genérico); el
    binario/versión se registran desde la config; un cliente que retorna temprano **no** produce
    `completed`; el texto final se persiste vía `receive` con `semantic_status:"pending"`; el state
    no cambia.
- **Produce**: `adaptador-opencode` (`spec-005-009-PD4-PD5-PD6-PD7`).
- **Consume**: `interfaz-comun-delegacion` (`spec-005-009-PD1-PD2-PD3-PD8`, producer T1).
- **Depends_on**: T1. **Parallel**: —.
- **TDD steps**: RED (load-mode fail-closed; sin fallback genérico; binario/versión desde config;
  espera no basada en rc; clasificación de terminación; `receive` con `pending`) → GREEN (mínimo:
  el adaptador OpenCode) → focales + módulos tocados.
- **Evidencia**: salida de `pytest` focal; el recibo durable `pending`; el diagnóstico del
  fail-closed; la traza de la espera.

#### T3 — Reconciliación de la prohibición de spawn (fuentes + generados) · PD-9 · INV-1, INV-4, INV-8
- **Files**:
  - `skills/cdad-cycle/SKILL.md` (**Modify**): **conservar** el SPAWN GUARD (`:136-143`) y agregar
    la **distinción** de la delegación externa autorizada (coordinador→worker entre CLIs, que no es
    recursión de subagentes dentro del mismo runtime).
  - `sources/roles/orchestrator.md` (**Modify**): **conservar** la anti-recursión (`:74-76`) +
    la distinción + el orquestador como **escritor único** del state. Fuente canónica; regenerar.
  - `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md` (**Modify**:
    regenerados por `scripts/cdad-generate.py` / `make agents` — salidas declaradas, no se editan
    a mano).
  - `skills/cdad-cycle/references/claude-code-delegation.md` (**Modify**): la distinción
    (`:63-69`) entre delegación externa y recursión de subagentes.
  - `tests/test_005_009_t3_spawn_reconciliation.py` (**New**): consistencia estructural — el texto
    del SPAWN GUARD permanece; existe la distinción; paridad fuente↔generado; el orquestador sigue
    siendo el único escritor del state.
- **Produce**: `prohibicion-spawn-reconciliada` (`spec-005-009-PD9`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T1 (archivos disjuntos).
- **TDD steps**: RED (el SPAWN GUARD permanece; la distinción existe en fuentes y generados; la
  paridad fuente↔generado pasa; el escritor único del state se conserva) → GREEN (mínimo: editar
  las fuentes y regenerar) → focales + módulos tocados.
- **Evidencia**: salida de `pytest` focal; el diff de los generados (solo el orquestador);
  `test_cdad_generate.py` en verde.

#### T4 — Recorrido real + interrupción/recuperación (aceptación) · PD-6, PD-10 · INV-5, INV-6, INV-8, INV-9
- **Files**:
  - `tests/test_005_009_t4_acceptance.py` (**New**): comprobaciones **deterministas** de la
    distinción entrega/gate (`rc=0` → no gate; recibo `pending`; el state no cambia) y del **caso
    acotado de interrupción/recuperación** (`reconcile` clasifica sin repetir efectos ni fabricar
    entrega), agnósticas del proyecto y del entorno.
- **Produce**: `recorrido-real-reconciliacion` (`spec-005-009-PD6-PD10`).
- **Consume**: `interfaz-comun-delegacion` (T1), `adaptador-opencode` (T2),
  `prohibicion-spawn-reconciliada` (T3).
- **Depends_on**: T1, T2, T3. **Parallel**: —.
- **TDD steps**: RED (la terminación `rc=0` no cierra el gate; `reconcile` clasifica
  `dispatched-unknown` sin autorizar repetición; no se fabrica entrega) → GREEN es de T1/T2 (aquí no
  hay producto nuevo) → focales.
  - **Gate de integración (real, no unitario):** **recorrido real Claude → OpenCode → recepción
    CDAD** desde la **instalación elegida** para la aceptación, con **re-entry** del coordinador;
    lo corre el **orquestador con el dueño** y se registra como evidencia. Cierra/registra los
    VERIFY 2, 3, 4 y 8. Una prueba que solo llama al script desde un shell **no** demuestra por sí
    sola la orquestación desde Claude.
- **Owner**: test-writer (checks deterministas); orquestador + dueño (recorrido real).

### Bloque canónico `plan-tasks`

Formato: **por referencia**, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
§4.1 (campos `tasks`/`validation_strategy`; por tarea `id`, `produce`, `consume`, `depends_on`,
`parallel`, `files`, `focal_tests`/`observable_checks`, `regressions`, `integration_gate`,
`owner`; estrategia común referenciada con `@validation_strategy`).

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el desarrollo; suite completa al cierre de la feature; regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "interfaz-comun-delegacion", "contract": "spec-005-009-PD1-PD2-PD3-PD8"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T3"],
   "files": ["skills/cdad-cycle/scripts/cdad_delegate.py",
             "scripts/cdad_delegate.py",
             "skills/cdad-cycle/references/cli-delegation.md",
             "tests/test_005_009_t1_interface.py"],
   "focal_tests": ["tests/test_005_009_t1_interface.py"],
   "regressions": ["tests/test_004_002_t4_dispatch.py",
                   "tests/test_003_002_t1_receive.py",
                   "tests/test_003_004_t2_reconcile.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "adaptador-opencode", "contract": "spec-005-009-PD4-PD5-PD6-PD7"}],
   "consume": [{"artifact": "interfaz-comun-delegacion", "contract": "spec-005-009-PD1-PD2-PD3-PD8", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_delegate_opencode.py",
             "tests/test_005_009_t2_opencode_adapter.py"],
   "focal_tests": ["tests/test_005_009_t2_opencode_adapter.py"],
   "regressions": ["tests/test_004_002_t4_dispatch.py",
                   "tests/test_003_002_t1_receive.py",
                   "tests/test_003_004_t2_reconcile.py",
                   "tests/test_004_002_t3_durable.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "prohibicion-spawn-reconciliada", "contract": "spec-005-009-PD9"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1"],
   "files": ["skills/cdad-cycle/SKILL.md",
             "sources/roles/orchestrator.md",
             "agents/cdad-orchestrator.md",
             "agents/claude-code/cdad-orchestrator.md",
             "skills/cdad-cycle/references/claude-code-delegation.md",
             "tests/test_005_009_t3_spawn_reconciliation.py"],
   "focal_tests": ["tests/test_005_009_t3_spawn_reconciliation.py"],
   "regressions": ["tests/test_cdad_generate.py",
                   "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "recorrido-real-reconciliacion", "contract": "spec-005-009-PD6-PD10"}],
   "consume": [{"artifact": "interfaz-comun-delegacion", "contract": "spec-005-009-PD1-PD2-PD3-PD8", "producer": "T1"},
               {"artifact": "adaptador-opencode", "contract": "spec-005-009-PD4-PD5-PD6-PD7", "producer": "T2"},
               {"artifact": "prohibicion-spawn-reconciliada", "contract": "spec-005-009-PD9", "producer": "T3"}],
   "depends_on": ["T1", "T2", "T3"],
   "parallel": [],
   "files": ["tests/test_005_009_t4_acceptance.py"],
   "focal_tests": ["tests/test_005_009_t4_acceptance.py"],
   "regressions": [],
   "integration_gate": "recorrido real Claude -> OpenCode -> recepcion CDAD desde la instalacion elegida (orquestador + dueno) + suite completa + make validate",
   "owner": "test-writer (checks deterministas); orquestador + dueno (recorrido real)"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1/PD-2/PD-3/PD-8 → T1; PD-4/PD-5/PD-6/PD-7 → T2; PD-9 → T3; PD-6/PD-10 → T4.
  Sin PD huérfano; sin tarea sin PD. INV-1..INV-3, INV-7 → T1; INV-4..INV-6 → T2; INV-1/INV-4/INV-8
  → T3; INV-5/INV-6/INV-8/INV-9 → T4; INV-10 → declarado en la spec (§9).
- **Grafo**: sin ciclos. T1 y T3 son raíces **independientes y paralelas** (archivos disjuntos);
  T2 consume la interfaz de T1 (`depends_on` [`T1`]); T4 consume los tres artefactos
  (`depends_on` [`T1`,`T2`,`T3`]).
- **Paralelismo seguro**: T1 y T3 no comparten archivos ni state. T3 regenera agentes con
  `make agents`; la fuente de T1 (el CLI nuevo + la referencia) **no** es leída por el generador,
  y T1 **no** declara archivos de `agents/`, de modo que la regeneración de T3 no colisiona. La
  integración (T4) tiene un único responsable (`orquestador + dueño`), sin escritura de state
  compartida por workers.
- **Aislamiento de roles**: los tests de T1/T2 expresan la capacidad **observable** (bytes
  transportados, forma del registro I8, terminación, fail-closed del modo de carga) sobre
  artefactos durables; el test-writer **no** necesita leer la implementación (que **no** puede
  leer) ni fija nombres de funciones internas.
- **Contratos compatibles**: los nombres de archivo (`cdad_delegate.py`,
  `cdad_delegate_opencode.py`, `cli-delegation.md`, `SKILL.md`, `orchestrator.md`) y los marcadores
  (`semantic_status`, `dispatched`, `dispatched-unknown`, `@validation_strategy`) son idénticos a la
  spec y a lo verificado en el discovery.
- **Verificación independiente**: el **recibo durable** (`cdad_result.py receive`) y la
  **clasificación de `reconcile`** (`cdad_continuity.py`) son oráculos independientes del
  transporte; el **recorrido real** (T4) es la evidencia de integración, no un test que compare dos
  productos del mismo error de generación.
- **Placeholders**: ninguno. **Una sola review formal** al cierre (stage 4).

### Riesgos registrados

- **R1 (alto) — modo de carga silencioso / fallback genérico.** Una entry `mode: subagent` cuelga
  en silencio; existen agentes no-Cdad en el namespace. Mitigación: PD-4 (fail-closed, sin fallback)
  + D5; VERIFY-3 confirma la entry soportada contra la versión vigente.
- **R2 (alto) — esperar al cliente, no a la sesión.** `opencode run` puede volver antes de que el
  rol termine. Mitigación: PD-5 (señal durable, no rc) + D6.
- **R3 (alto) — `rc=0` tomado como aprobación de gate.** Mitigación: PD-6/INV-5 (recibo `pending`;
  el gate lo decide el re-entry) + T4.
- **R4 (medio) — crear otro state/ledger o reescribir las reglas del paquete.** Mitigación:
  PD-2/INV-1/INV-3 (reutilizar `prepare`/I8/ledger/`receive`/`reconcile`; transportar el paquete
  íntegro).
- **R5 (medio) — configuración efectiva no comprobada.** Mitigación: PD-3/PD-8 (registrar
  configurado/observado o `unknown`); VERIFY-2 no se cierra con un lector de sesión de producto.
- **R6 (medio) — valores del VPS en producto.** Mitigación: PD-8/INV-7 (config local; barrido de
  portabilidad en T1) + la regla de anonimización del proyecto.
- **R7 (medio) — doble binario de OpenCode.** Coexisten binarios con bases de sesión distintas.
  Mitigación: D7 (binario/versión desde la config, sin hardcodear rutas) + PD-3.
- **R8 (bajo) — `install.sh`/publicación.** El script viaja con el árbol `cdad-cycle`
  (`install.sh:1006-1020`); si `--check`/staging requiere algo más, se registra (VERIFY-6).

### Aprobación

- **Estado: aprobado (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL de
  epic-005 (`execution.md`), **junto con la spec** (una sola acción), con las decisiones D1–D10
  aprobadas (`spec.md` §7). El bloque `plan-tasks` fue validado por el propio validador de
  `prepare` (4 tareas, productor/consumidor, sin ciclos, paralelismo T1∥T3 seguro, plan de
  validación por tarea). El architect no aprobó su propia propuesta (anti-sesgo).
- **Condición de aprobación (orquestador, 2026-10-10).** Los tests de T1/T2/T3 son de
  **comportamiento observable** sobre artefactos durables (bytes del paquete transportado, forma
  cerrada del registro I8, clasificación de terminación, fail-closed del modo de carga) y de
  **consistencia estructural** (T3: el SPAWN GUARD permanece + paridad fuente↔generado), según el
  precedente de 005-005/005-006/005-008. **No** son suites que busquen frases del prompt ni que
  fijen nombres de funciones internas. La prosa se verifica por **review**.
