> Plan **aprobado** (2026-10-10) junto con la spec. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado por el orquestador (receive + materialize create-only, ADR-003);
> aprobado por el **orquestador OpenCode** bajo la delegación HITL de epic-005 (`execution.md`).
> Construcción según CDAD
> stages 3–5 (TDD con test-writer/implementer por paquete, una única review formal al final y
> Memory Bank al cierre). Insumo: `docs/specs/005-008-project-path-capabilities/discovery.md`.
> Formato canónico de la ficha y del bloque `plan-tasks`: **por referencia**,
> `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4 y **§4.1** (NO se
> reproduce su formato aquí). Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila de orden
> 4, `:37`).

## Plan — 005-008-project-path-capabilities

**Feature ID:** `005-008-project-path-capabilities` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-10, orquestador OpenCode, HITL delegada epic-005).

### Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**.
- **No** instalar CDAD en HOME ni activar versiones, ni operar producción (reservado al dueño).
  **No** ejecutar el CLI del repo para **operar** este ciclo (el repo se **desarrolla**; el ciclo
  corre con la instalación vigente).
- **No** leer `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo: **worktree**, nunca `git stash` en el árbol compartido.
- No volcar salidas enormes al contexto.
- **Gate de tests (metodología común, dueño único `stage-3-tdd.md` §«Test evidence policy»).**
  Durante el trabajo: **focales + módulos tocados**. **Suite completa al cierre de la feature**
  (toca `skills/**` y `tests/**`), más `make validate` al cierre. Sin duplicar la regla.
- **Frontera:** **no** implementar el producto consumidor (Perl/Webmin), **no** crear agentes Perl
  manuales ni otro sistema de políticas; **no** cambiar HOME ni operar producción. **POLICY-CLASS,
  CI, sandbox y plataforma universal de jobs quedan FUERA.**
- Ante un obstáculo fuera del ámbito: entregar el diagnóstico, no fabricar registros.

### Tareas

#### T1 — Coherencia de política y derivados (cambio de producto) · PD-1..PD-9 · INV-1..INV-4, INV-8
- **Files**:
  - `skills/cdad-cycle/scripts/cdad_packet.py` (**Modify**)
    - rama `read` del `test-writer` en `_derived_maps` (`:2641-2651`): reabrir el **árbol de tests
      declarado** **después** del deny de implementación y **antes** de `private` (findLast);
    - `_test_patterns` (`:2587-2594`): **incluir `test_files`** (D1) — fuente única que consumen el
      `read`/`edit` del test-writer y el `edit` del implementer.
    - **No** se toca el clasificador, el guard CC, el esquema del manifiesto ni la publicación.
  - `tests/test_005_008_t1_nested_tests.py` (**New**): comportamiento observable sobre los
    derivados publicados, reutilizando por import `LayoutProject`/`policy_doc`
    (`tests/test_004_002_t5_runtime.py`), el guard CC forma-real y el oráculo findLast único
    (`tests/pd10_permission_semantics.py:verdict`); **no** invoca funciones internas.
- **Produce**: `coherencia-permisos-derivados` (`spec-005-008-PD1-PD9`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T2 (archivos disjuntos).
- **TDD steps**: RED (fixture de política con `test_roots` **anidada** en implementación y con
  `test_files` bajo implementación: el test-writer debe **leer y editar** sus tests y el
  implementer **no** editar tests; privada anidada sigue denegada; B3/W-2 sin amplificación) →
  GREEN (mínimo: editar `_derived_maps`/`_test_patterns`) → focales + módulos tocados.
- **Evidencia**: veredictos por oráculo sobre los derivados publicados + salida de `pytest`.

#### T2 — Procedimiento de uso Perl/Webmin (reusando 005-006, sin duplicar bootstrap) · PD-10 · INV-5, INV-7
- **Files**:
  - `tests/test_005_008_t2_language_commands.py` (**New**): fixture determinista que (i) verifica
    que el **esquema de política** sigue de **tres campos** y **rechaza** un campo `commands` con
    diagnóstico (PD-10b), y (ii) que un proyecto sintético puede declarar comandos de sintaxis/tests
    Perl en su **Makefile** sin tocar la política y sin afectar los mapas derivados.
  - (Condicional, **solo si el discovery lo justifica**, VERIFY 5/6) un **puntero corto** al lugar
    canónico de los comandos (**Makefile/systemPatterns**) en una referencia de `cdad-cycle`,
    **reusando 005-006**; **no** otra skill, **no** duplicar el bootstrap. Si 005-006 ya lo
    resuelve, T2 **verifica y no agrega** archivo de metodología.
- **Produce**: `convenciones-perl-registro-comandos` (`spec-005-008-PD10`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T1 (archivos disjuntos).
- **TDD steps**: RED (política con cuarto campo → rc≠0 con diagnóstico; fixture de proyecto con
  `make syntax`/`make test` declarados sin cambio de política) → GREEN (mínimo) → focales.
- **Evidencia**: salida de los tests focales + diagnóstico observado del rechazo del cuarto campo.

#### T3 — Recorrido instalado (aceptación) · PD-11 · INV-6
- **Files**:
  - `tests/test_005_008_t3_acceptance.py` (**New**): comprobaciones **deterministas** de las
    capacidades sobre los derivados publicados (positivas: test-writer lee/edita sus tests,
    implementer edita implementación y no tests; negativas: test-writer no lee implementación,
    privada denegada), agnósticas del proyecto.
- **Produce**: `aceptacion-capacidades-instaladas` (`spec-005-008-PD11`).
- **Consume**: `coherencia-permisos-derivados` (T1), `convenciones-perl-registro-comandos` (T2).
- **Depends_on**: T1, T2. **Parallel**: —.
- **TDD steps**: RED (capacidades positivas y negativas por oráculo sobre la política de tests
  anidados) → GREEN es de los cambios de T1 (aquí no hay producto nuevo) → focales.
- **Gate de integración (real, no unitario):** **recorrido del producto instalado** que demuestra
  las capacidades mediante **operaciones reales del runtime**, con los **límites honestos**
  declarados (grep/shell/sesión separada **no** son sandbox; **sin** allowlists por comando). Lo
  corre el **orquestador con el dueño** y se registra como evidencia. Cierra/registra los VERIFY
  1, 3, 5 y 6 (layout/política real del consumidor, mediación viva, dominio, comandos).
- **Owner**: test-writer (checks deterministas); orquestador + dueño (recorrido instalado).

### Bloque canónico `plan-tasks`

Formato: **por referencia**, `docs/epics/epic-004-single-source-planning/planning-contract-draft.md`
§4.1 (campos `tasks`/`validation_strategy`; por tarea `id`, `produce`, `consume`, `depends_on`,
`parallel`, `files`, `focal_tests`/`observable_checks`, `regressions`, `integration_gate`,
`owner`; estrategia común referenciada con `@validation_strategy`).

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el desarrollo; suite completa al cierre de la feature; regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "coherencia-permisos-derivados", "contract": "spec-005-008-PD1-PD9"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T2"],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py",
             "tests/test_005_008_t1_nested_tests.py"],
   "focal_tests": ["tests/test_005_008_t1_nested_tests.py"],
   "regressions": ["tests/test_004_002_t5_reviewfix.py",
                   "tests/test_004_002_t7_private_paths.py",
                   "tests/test_004_002_t7_w2.py",
                   "tests/test_004_002_t1_policy.py",
                   "tests/test_opencode_read_map_and_steps.py",
                   "tests/test_004_002_t5_runtime.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "convenciones-perl-registro-comandos", "contract": "spec-005-008-PD10"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1"],
   "files": ["tests/test_005_008_t2_language_commands.py"],
   "focal_tests": ["tests/test_005_008_t2_language_commands.py"],
   "regressions": ["tests/test_004_002_t1_policy.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "aceptacion-capacidades-instaladas", "contract": "spec-005-008-PD11"}],
   "consume": [{"artifact": "coherencia-permisos-derivados", "contract": "spec-005-008-PD1-PD9", "producer": "T1"},
               {"artifact": "convenciones-perl-registro-comandos", "contract": "spec-005-008-PD10", "producer": "T2"}],
   "depends_on": ["T1", "T2"],
   "parallel": [],
   "files": ["tests/test_005_008_t3_acceptance.py"],
   "focal_tests": ["tests/test_005_008_t3_acceptance.py"],
   "regressions": [],
   "integration_gate": "recorrido real del producto instalado (capacidades positivas y negativas) + suite completa + make validate",
   "owner": "test-writer (checks deterministas); orquestador + dueno (recorrido instalado)"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1..PD-9 → T1; PD-10 → T2; PD-11 → T3. Sin PD huérfano; sin tarea sin PD.
  INV-1..INV-4, INV-8 → T1; INV-5 → T2; INV-6 → T3; INV-7/INV-9 → declarados en la spec (§9).
- **Grafo**: sin ciclos. T1 y T2 son raíces independientes y **paralelas** (archivos disjuntos:
  `skills/.../cdad_packet.py` + fixture vs fixture + posible referencia de metodología); T3 consume
  los artefactos de T1 y T2 (`depends_on` [`T1`,`T2`]).
- **Paralelismo seguro**: T1 y T2 no colisionan archivos ni state; la integración (T3) tiene un
  único responsable (`orquestador + dueño`), sin escritura de state compartida por workers.
- **Aislamiento de roles**: el fixture de T1 expresa la capacidad **observable** (allow/deny por
  herramienta y ruta sobre los derivados publicados); no expone implementación al test-writer (que
  **no** puede leer `skills/**`) ni introduce nombres de funciones internas.
- **Contratos compatibles**: los nombres de archivo (`cdad_packet.py`, `stage-3-tdd.md`) y los
  marcadores (`@validation_strategy`) son idénticos a la spec y a lo verificado en el discovery.
- **Verificación independiente**: el oráculo findLast (`pd10_permission_semantics.py`) es la fuente
  única de veredictos; la aceptación añade el **recorrido real** del producto instalado como
  evidencia independiente de la sonda.
- **Placeholders**: ninguno. **Una sola review formal** al cierre (stage 4).

### Riesgos registrados

- **R1 (alto) — sobre-amplificación.** «Arreglar» con `**/tests/**` o `**/*.t` rompería B3
  (`test_reviewfix_b3_nested_tests_dir_not_amplified`) y el invariante PD-7. Mitigación: reabrir
  solo los **árboles/archivos declarados**; PD-7 fija el control.
- **R2 (alto) — reabrir una ruta privada.** Si el allow de tests se emite **después** de `private`,
  se anula la barrera (la política del repo tiene `tests/.sensitive-patterns.local` dentro de
  `tests/`). Mitigación: allow de tests **antes** de `private`; PD-6 lo fija.
- **R3 (medio) — caso focal `test_files` omitido.** Corregir solo `.t`/`test_roots` deja
  inconsistente `test_files` bajo implementación. Mitigación: D1 + PD-5.
- **R4 (medio) — `grep`/`glob`.** No agregar entradas por ruta; el canal vivo es `read`/`edit`.
  Mitigación: PD-9 + `assert_no_search_path_entries`.
- **R5 (medio) — mediación real.** La sonda prueba mapas generados, **no** la mediación de un
  proceso OpenCode real. Mitigación: T3 (recorrido instalado); los límites honestos se declaran.
- **R6 (bajo) — comandos Perl ausentes.** Declarar comandos no autoriza instalar intérprete/runner/
  dependencias en producción; la ausencia produce diagnóstico. Mitigación: PD-10d; consumidor fuera
  de alcance.
- **R7 (bajo) — duplicar 005-006 o crear agentes/sistema de políticas paralelo.** Mitigación: T2
  reusa y no agrega otra skill; INV-7.

### Aprobación

- **Estado: aprobado (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL de
  epic-005 (`execution.md`), **junto con la spec** (una sola acción), con las decisiones D1–D7
  aprobadas (`spec.md` §7). El bloque `plan-tasks` fue validado por el propio validador de
  `prepare` (productor/consumidor, sin ciclos, paralelismo seguro, plan de validación por tarea).
- **Condición de aprobación (orquestador, 2026-10-10).** Los tests de T1/T2 son de **comportamiento
  observable sobre los artefactos publicados** (veredictos allow/deny por herramienta y ruta sobre
  los agentes derivados, evaluados con el oráculo findLast único), según el precedente de 005-005
  T2 y 005-006. **No** son suites que busquen frases del prompt ni que fijen nombres de funciones
  internas. Los aspectos de pura prosa (PD-10c) se verifican por **review** (la única review formal
  de la feature).
