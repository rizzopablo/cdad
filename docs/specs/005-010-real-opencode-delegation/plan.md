> Plan **aprobado** (2026-10-11) junto con la spec por el orquestador Claude. Texto del **architect** (subetapa `draft`,
> etapa 2), para su materialización por el orquestador (ADR-003); se aprueba **junto con la spec**
> (una sola acción) por el **orquestador Claude** bajo la excepción HITL de 005-010
> (`execution.md`). Construcción según CDAD stages 3–5 (TDD con test-writer/implementer por
> paquete, una única review formal al final y Memory Bank al cierre). Insumo:
> `docs/specs/005-010-real-opencode-delegation/discovery.md`. Formato canónico de la ficha y del
> bloque `plan-tasks`: **por referencia**,
> `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4 y §4.1 (NO se
> reproduce aquí). Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila de orden 6, `:39`).

## Plan — 005-010-real-opencode-delegation

**Feature ID:** `005-010-real-opencode-delegation` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-11).

### Ajuste de las unidades propuestas al discovery

El discovery §5 propone un doble fiel (§5.1) y una prueba de integración opcional (§5.2). Ajuste:

- El cambio de **señal durable** (PD-1/PD-2/PD-5/PD-6) y el **doble SQLite** (PD-7) son un solo
  átomo verificable con su propio RED→GREEN: **T1**.
- El **modo de carga** y la **invocación** (PD-3/PD-4) son un segundo átomo, en el **mismo
  archivo** de producto que T1 → **T2** (secuencial, `depends_on` T1), revisable por separado.
- La **documentación** (PD-10) toca **archivos disjuntos** → **T3**, paralela a T1/T2.
- La **prueba de integración opcional** (PD-8) y la **aceptación PD-10 en dos pasos** (PD-9)
  consumen T1/T2 → **T4**.

Resultado: **T1 → T2** (mismo archivo, secuencial); **T3 ∥ T1/T2** (disjuntos);
**T4 depende de T1 y T2**.

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
  (toca `skills/**` y `tests/**`), más `make validate` al cierre. Sin duplicar la regla.
- **Frontera:** **no** scheduler, **no** instalación automática de CLI, **no** sandbox; **no** se
  implementan todos los destinos (solo OpenCode); **no** se cambia `cdad-generate.py` ni la
  interfaz común. Ante un obstáculo fuera del ámbito: entregar el diagnóstico, no fabricar
  registros.

### Tareas

#### T1 — Señal durable real, correlación, clasificación y observación I8 · PD-1, PD-2, PD-5, PD-6, PD-7 · INV-3, INV-4, INV-5
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (**Modify**): el lector de la señal pasa
    de JSON a **SQLite en solo lectura** (`mode=ro`) sobre el `sessions_db` de la config; el
    adaptador **elige** el id y lo pasa en `--session <id>` a la invocación; espera la fila
    `session_v2` correlacionada con `time_idle`/`idle_outcome` dentro de `wait.timeout_seconds` y
    toma el texto del **último** `session_message` `assistant`; clasifica por `idle_outcome`
    (`succeeded/failed/interrupted/ninguno`); falla cerrado con diagnóstico ante store ilegible /
    esquema desconocido / JSON de `data` no parseable (el `UnicodeDecodeError` deja de ser no
    capturado); el registro I8 del worker toma `session`/`model_reported` de la fila durable con
    provenance. **No** cambia el envelope ni la persistencia por `receive`.
  - `tests/test_005_009_t2_opencode_adapter.py` (**Modify**): el doble (`FAKE_BINARY_SOURCE`) deja
    de escribir `<fake>/sessions.json` y escribe un **SQLite real chico** con el esquema observado
    (`session_v2` + `session_message`); migra las aserciones de señal/clasificación al store
    SQLite **conservando la semántica vigente de modo** (la inversión del modo es de T2).
  - `tests/test_005_010_t1_durable_signal.py` (**New**): variantes `succeeded`, `failed`,
    `interrupted`, `no-idle` (→ `timeout`), `unknown-schema` (falta `idle_outcome` → `blocked` con
    diagnóstico), `transport-error` (`rc≠0` sin señal); correlación por `--session`; `session`/
    `model_reported` del I8 desde la fila; recibo `pending` en `completed`.
- **Produce**: `senal-durable-sqlite` (`spec-005-010-PD1-PD2-PD5-PD6-PD7`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T3 (archivos disjuntos).
- **TDD steps**: RED (con el doble nuevo, el adaptador JSON no encuentra la señal → `timeout` en
  las variantes con fila idle; falta `--session`; `model_reported`/`session` no salen de la fila;
  el `unknown-schema` no falla cerrado) → GREEN (mínimo: lector SQLite + correlación +
  clasificación + observación) → focales + módulos tocados.
- **Evidencia**: salida de `pytest` focal; la base SQLite del fixture y sus variantes; el argv con
  `--session`; el registro I8 con `session`/`model_reported` de la fila; el recibo `pending`.

#### T2 — Modo de carga por la versión instalada + invocación configurable · PD-3, PD-4 · INV-2, INV-6, INV-7
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` (**Modify**): `SUPPORTED_LOAD_MODES`/`_check_load_mode`
    dejan de exigir `mode: all`; exigen el derivado `cdad-<rol>` publicado y verifican la identidad
    desde la fila durable (`session_v2.agent == cdad-<rol>`, sin fallback a agente genérico);
    `_invoke_destination` agrega `--standalone` por defecto o `--server <url>` por config
    (alternativa), y `--auto` configurable (activado por defecto). `cdad-generate.py` **no** se
    toca.
  - `tests/test_005_010_t2_load_mode_invocation.py` (**New**): con la entry `subagent` publicada
    **sí** despacha; si la fila durable reporta otro agente, **no** entrega; jamás un agente
    no-Cdad; argv por defecto (`--standalone` + `--auto`, sin `--server`); con `server` en config
    (`--server` sin `--standalone`); con `auto: false` sin `--auto`.
  - `tests/test_005_009_t2_opencode_adapter.py` (**Modify**): invierte la unidad de modo
    (`mode: subagent` deja de ser fallo cerrado; el fallo cerrado pasa a ser «derivado ausente» o
    «identidad durable distinta»).
- **Produce**: `modo-carga-invocacion` (`spec-005-010-PD3-PD4`).
- **Consume**: `senal-durable-sqlite` (`spec-005-010-PD1-PD2-PD5-PD6-PD7`, producer T1).
- **Depends_on**: T1. **Parallel**: T3 (archivos disjuntos).
- **TDD steps**: RED (con la entry `subagent` el adaptador vigente rechaza; el argv no lleva
  `--standalone`/`--auto`; no hay verificación de identidad desde la fila) → GREEN (mínimo: modo +
  invocación) → focales + módulos tocados.
- **Evidencia**: salida de `pytest` focal; el argv observado por el binario falso por variante de
  config; el diagnóstico del fallo cerrado por identidad durable; `make agents` sin cambios
  (paridad del generador).

#### T3 — Referencias de la delegación actualizadas · PD-10 · INV-7
- **Files**:
  - `skills/cdad-cycle/references/cli-delegation.md` (**Modify**): documenta el contrato de la
    **señal durable real** (store SQLite en solo lectura, correlación por `--session`, fallo
    cerrado por esquema) y la ubicación de `standalone`/`server`/`auto` en la configuración.
  - `skills/cdad-cycle/references/opencode-delegation.md` (**Modify**): actualiza la **sección de
    modo de carga** (`mode: subagent` = entry no interactiva en la versión instalada; identidad
    verificada desde la fila durable; sin fallback) y **reemplaza la tabla de modelos obsoleta**
    por un puntero a la **única** tabla (`scripts/cdad-models.sh` + perfil activo), sin nombres de
    modelo concretos.
  - `tests/test_005_010_t3_references.py` (**New**): consistencia estructural — las referencias
    contienen los marcadores del contrato durable y del modo de carga; **no** contienen rutas
    absolutas de host, proveedor concreto, modelo concreto ni servidor.
- **Produce**: `referencias-delegacion` (`spec-005-010-PD10`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T1, T2.
- **TDD steps**: RED (los marcadores del contrato durable y del modo actualizado no están; hay
  nombres de modelo concretos en la tabla) → GREEN (mínimo: editar las referencias) → focales.
- **Observable checks / criterio de prosa**: además del test estructural, la prosa se verifica por
  **review** (patrón 005-009: no se fijan frases del prompt ni nombres internos).

#### T4 — Prueba de integración opcional + aceptación PD-10 (dos pasos) · PD-8, PD-9 · INV-8, INV-9, INV-10
- **Files**:
  - `tests/test_005_010_t4_integration.py` (**New**): prueba **marcada y omitida por defecto**,
    habilitada por variable de entorno (p.ej. `CDAD_OPENCODE_INTEGRATION=1`), binario por config,
    instalación y proyecto **aislados** (`CDAD_INSTALL_ROOT`), runtime real con `--standalone` y
    base en solo lectura (spec PD-8, enmendada al aprobar); si faltan binario, base o credencial,
    **omite con diagnóstico** (no fabrica verde).
- **Produce**: `integracion-aceptacion` (`spec-005-010-PD8-PD9`).
- **Consume**: `senal-durable-sqlite` (T1), `modo-carga-invocacion` (T2).
- **Depends_on**: T1, T2. **Parallel**: —.
- **TDD steps**: RED (sin la variable la prueba se omite; con entorno aislado, la correlación
  durable se comprueba) → GREEN es de T1/T2 (aquí no hay producto nuevo) → focales.
  - **Gate de integración (real, no unitario):** **aceptación PD-10 en dos pasos** — (a)
    instalación aislada de la versión nueva + recorrido real Claude → `cdad_delegate.py` →
    OpenCode → `receive` → re-entry sobre un proyecto temporal, **corrido por el orquestador
    Claude**; (b) tras el despliegue del dueño, **confirmación corta** desde la instalación
    global. Registra la evidencia (I8 + recibo + re-entry) y confirma los VERIFY C/F/G.
- **Owner**: test-writer (módulo omitido por defecto); orquestador + dueño (recorrido real).

### Bloque canónico `plan-tasks`

Formato: **por referencia**, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
§4.1 (campos `tasks`/`validation_strategy`; por tarea `id`, `produce`, `consume`, `depends_on`,
`parallel`, `files`, `focal_tests`/`observable_checks`, `regressions`, `integration_gate`,
`owner`; estrategia común referenciada con `@validation_strategy`).

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el desarrollo; suite completa al cierre de la feature; regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "senal-durable-sqlite", "contract": "spec-005-010-PD1-PD2-PD5-PD6-PD7"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T3"],
   "files": ["skills/cdad-cycle/scripts/cdad_delegate_opencode.py",
             "tests/test_005_009_t2_opencode_adapter.py",
             "tests/test_005_010_t1_durable_signal.py"],
   "focal_tests": ["tests/test_005_010_t1_durable_signal.py",
                   "tests/test_005_009_t2_opencode_adapter.py"],
   "regressions": ["tests/test_005_009_t1_interface.py",
                   "tests/test_005_009_t3_spawn_reconciliation.py",
                   "tests/test_005_009_t4_acceptance.py",
                   "tests/test_004_002_t4_dispatch.py",
                   "tests/test_003_002_t1_receive.py",
                   "tests/test_003_004_t2_reconcile.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "modo-carga-invocacion", "contract": "spec-005-010-PD3-PD4"}],
   "consume": [{"artifact": "senal-durable-sqlite", "contract": "spec-005-010-PD1-PD2-PD5-PD6-PD7", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": ["T3"],
   "files": ["skills/cdad-cycle/scripts/cdad_delegate_opencode.py",
             "tests/test_005_010_t2_load_mode_invocation.py",
             "tests/test_005_009_t2_opencode_adapter.py"],
   "focal_tests": ["tests/test_005_010_t2_load_mode_invocation.py",
                   "tests/test_005_009_t2_opencode_adapter.py"],
   "regressions": ["tests/test_005_009_t1_interface.py",
                   "tests/test_cdad_generate.py",
                   "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "referencias-delegacion", "contract": "spec-005-010-PD10"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1", "T2"],
   "files": ["skills/cdad-cycle/references/cli-delegation.md",
             "skills/cdad-cycle/references/opencode-delegation.md",
             "tests/test_005_010_t3_references.py"],
   "focal_tests": ["tests/test_005_010_t3_references.py"],
   "observable_checks": ["review: la prosa documenta el contrato durable y el modo de carga y no fija frases ni nombres internos"],
   "regressions": ["tests/test_005_009_t1_interface.py",
                   "tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "integracion-aceptacion", "contract": "spec-005-010-PD8-PD9"}],
   "consume": [{"artifact": "senal-durable-sqlite", "contract": "spec-005-010-PD1-PD2-PD5-PD6-PD7", "producer": "T1"},
               {"artifact": "modo-carga-invocacion", "contract": "spec-005-010-PD3-PD4", "producer": "T2"}],
   "depends_on": ["T1", "T2"],
   "parallel": [],
   "files": ["tests/test_005_010_t4_integration.py"],
   "focal_tests": ["tests/test_005_010_t4_integration.py"],
   "regressions": [],
   "integration_gate": "aceptacion PD-10 en dos pasos: (a) instalacion aislada de la version nueva + recorrido real Claude -> cdad_delegate.py -> OpenCode -> receive -> re-entry sobre proyecto temporal (orquestador Claude); (b) confirmacion corta desde la instalacion global tras el despliegue del dueno; + suite completa + make validate",
   "owner": "test-writer (modulo omitido por defecto); orquestador + dueno (recorrido real)"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1/PD-2/PD-5/PD-6/PD-7 → T1; PD-3/PD-4 → T2; PD-10 → T3; PD-8/PD-9 → T4. Sin PD
  huérfano; sin tarea sin PD. INV-3/INV-4/INV-5 → T1; INV-2/INV-6/INV-7 → T2; INV-7 → T3;
  INV-8/INV-9/INV-10 → T4; INV-1 → declarado en la spec (§3/§10).
- **Grafo**: sin ciclos. T1 es raíz; T2 consume T1 (`depends_on` [`T1`], mismo archivo, secuencial);
  T3 es raíz **paralela** (archivos disjuntos de producto/tests); T4 consume T1 y T2.
- **Paralelismo seguro**: T3 solo edita referencias + su test (archivos que T1/T2 no tocan); el
  código y el doble de T1/T2 no son leídos por T3. T1→T2 es secuencial por compartir el archivo de
  producto y el módulo 005-009; la review puede rechazar T2 sin rechazar T1.
- **Aislamiento de roles**: los tests expresan la capacidad **observable** sobre artefactos
  durables (base SQLite, argv del binario falso, registro I8, recibo, terminación); el test-writer
  **no** lee la implementación ni fija nombres de funciones internas.
- **Contratos compatibles**: los nombres (`cdad_delegate_opencode.py`, `sessions_db`,
  `session_v2`, `session_message`, `idle_outcome`, `--session`, `--standalone`, `--server`,
  `--auto`, `semantic_status`, `@validation_strategy`) son idénticos a la spec y a lo verificado
  en el discovery.
- **Verificación independiente**: el **recibo durable** (`receive`) y la **clasificación de
  `reconcile`** son oráculos independientes; la **prueba de integración opcional** (T4) y el
  recorrido real son la evidencia de integración, no una comparación de dos productos del mismo
  error de generación.
- **Placeholders**: ninguno. **Una sola review formal** al cierre (stage 4).

### Riesgos registrados

- **R1 (alto) — señal durable inexistente/ilegible contra el runtime real.** Mitigación:
  PD-1/PD-2 (store SQLite en solo lectura, correlación por `--session`, fallo cerrado con
  diagnóstico) + D1/D2; el `unknown-schema`/ilegible se cubre en T1 y se confirma en T4.
- **R2 (alto) — fallback genérico / modo de carga.** Mitigación: PD-3 (identidad desde la fila
  durable, sin fallback) + D3; T2 + T4.
- **R3 (alto) — `rc=0` tomado como aprobación de gate.** Mitigación: PD-5/INV-5 (recibo `pending`;
  el gate lo decide el re-entry).
- **R4 (medio) — acoplar el servicio de fondo del dueño.** Mitigación: PD-4 (`--standalone` por
  defecto, `--server` opcional) + D4; T2 + T4. **No** se manipula el servicio en los tests.
- **R5 (medio) — texto final incompleto con herramientas (VERIFY-C).** Mitigación: R-C de la spec
  (último `assistant`; `blocked` si falta texto); T4.
- **R6 (medio) — esquema no público / versión (VERIFY-D).** Mitigación: D2 (validar columnas, fallar
  cerrado); T1 + T4.
- **R7 (medio) — lectura con el servicio vivo / WAL (VERIFY-G).** Mitigación: `mode=ro` + reintentos
  acotados, nunca `immutable=1` con servicio vivo, nunca escritura; T4.
- **R8 (bajo) — valores del VPS / nombres de modelo concretos en las referencias.** Mitigación:
  INV-7/PD-10 (config local; T3 estructural + review).
- **R9 (bajo) — el doble migrado del 005-009 arrastra aserciones contradictorias.** Mitigación: T1
  migra el doble **conservando** la semántica de modo; T2 invierte únicamente la unidad de modo.

### Aprobación

- **Estado: borrador (2026-10-11).** Pendiente de aprobación del **orquestador Claude** bajo la
  excepción HITL de 005-010 (`execution.md`), **junto con la spec** (una sola acción), con las
  decisiones D1–D10 de la spec §7 a resolver. El bloque `plan-tasks` se valida por el validador de
  `prepare` (4 tareas, productor/consumidor, sin ciclos, paralelismo T3 seguro, plan de validación
  por tarea). El architect **no** aprueba su propia propuesta (anti-sesgo).
