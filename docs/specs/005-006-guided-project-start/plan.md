> Plan **aprobado** (2026-10-10) junto con la spec. Texto del **architect** (subetapa `draft`,
> etapa 2), materializado con el flujo (receive + materialize create-only) por el orquestador
> (ADR-003); aprobado por el orquestador OpenCode bajo la delegación HITL de epic-005.
> Decisiones D1–D8 aprobadas en `spec.md` §7. Construcción según CDAD stages 3–5 (TDD con
> test-writer/implementer por paquete, una sola review formal al final y Memory Bank al cierre).
> Insumo: `docs/specs/005-006-guided-project-start/discovery.md`.
> Contrato: `docs/epics/epic-005-real-operation/plan.md` (fila 3, `:35`).

## Plan — 005-006-guided-project-start

**Feature ID:** `005-006-guided-project-start` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-10, orquestador OpenCode, HITL delegada epic-005).

### Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**.
- **No** instalar CDAD en HOME ni activar versiones (reservado al dueño). **No** ejecutar el
  CLI del repo para **operar** este ciclo (el repo se **desarrolla**; el ciclo corre con la
  instalación vigente, ver INV-5 de la spec).
- No leer `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo: **worktree**, nunca `git stash` en el árbol compartido.
- No volcar salidas enormes al contexto.
- **Gate de tests (metodología común).** Durante el trabajo: **focales + módulos tocados**.
  **Suite completa al cierre de la feature** (la feature toca `skills/**`, `sources/**`,
  `agents/**` generados, `README.md` y docs), más `make validate` al cierre. Sin duplicar la
  regla: es la política única que fijó 005-005 (`stage-3-tdd.md` §«Test evidence policy»).
- Ante un obstáculo fuera del ámbito: entregar el diagnóstico, no fabricar registros.

### Tareas

#### T1 — Procedimiento corto de arranque + cableado del ciclo · PD-1, PD-3..PD-9, PD-13, PD-15 · INV-1..INV-4
- **Files**:
  - `skills/cdad-cycle/references/project-start.md` (**Create**: el procedimiento corto; reconoce
    (sin imponer layout), clasifica (nuevo/parcial/incompleta) por **referencia**, registra
    restricciones en su lugar canónico, distingue inferible/decide-el-usuario, encadena al
    primer encargo; **referencia** `state-detection`, `project-execution`, `continuity`,
    `bootstrap`, `cdad-epic/state-detection`; **no** copia reglas).
  - `skills/cdad-cycle/SKILL.md` (**Modify**: fila de `project-start.md` en «How to read the
    references» `:443-460`; paso 1 del flujo `:242-244` — rama «sin ejecución activa → no
    `resume`» (PD-9); `:260-261` y `:451-452` — ruta del **CLI instalado** (PD-10)).
  - `skills/cdad-cycle/references/state-detection.md` (**Modify**: declarar dueño canónico y
    puntero al arranque; sin duplicar el algoritmo — PD-13).
  - `skills/cdad-cycle/references/continuity.md` (**Modify**: `:31-44` — ejemplo con ruta del
    CLI **instalado**, no relativa al proyecto — PD-10).
  - `tests/test_005_006_t1_start_procedure.py` (**New**: test de consistencia documental).
- **Produce**: `procedimiento-arranque-corto` (`spec-005-006-PD1-PD9-PD13-PD15`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T3, T4 (archivos disjuntos).
- **TDD steps**: RED (test de consistencia: existe `project-start.md`; la fila de la tabla
  existe; el procedimiento **referencia** los dueños y **no** reproduce el algoritmo de
  detección ni el texto de política/autoridad; enuncia la rama «no `resume` en reposo», la
  preservación, la tabla restricción→lugar canónico y el encadenado al primer encargo; no hay
  plantilla con el prompt largo bajo `assets/`) → GREEN (mínimo: crear/editar los textos) →
  focales + módulos tocados.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T2 — Intake del orquestador: arranque desde reposo + rutas instaladas · PD-2, PD-10, PD-14 · INV-4, INV-5
- **Files**:
  - `sources/roles/orchestrator.md` (**Modify**: intake `:19-43` — **entrada de arranque desde
    reposo** que ordena cargar la metodología primero y señala `references/project-start.md`
    (PD-2); cableado de continuidad/re-entry `:80-98` — ruta del **CLI instalado** (PD-10);
    salida legítima ante bloqueo (PD-14)). Fuente canónica; regenerar.
  - `agents/cdad-orchestrator.md`, `agents/claude-code/cdad-orchestrator.md` (**Modify**:
    regenerados por `scripts/cdad-generate.py`/`make agents` — salidas declaradas, no se editan
    a mano).
  - `tests/test_005_006_t2_intake.py` (**New**: consistencia fuente↔generado + barrido de rutas).
- **Produce**: `entrada-de-arranque-intake` (`spec-005-006-PD2-PD10-PD14`).
- **Consume**: `procedimiento-arranque-corto` (`spec-005-006-PD1-PD9-PD13-PD15`, producer T1).
- **Depends_on**: T1. **Parallel**: —.
- **TDD steps**: RED (la fuente tiene la entrada de arranque desde reposo; el cableado no usa
  rutas relativas al proyecto para el CLI instalado; el generado coincide con la fuente según
  el contrato del generador) → GREEN (mínimo: editar la fuente y regenerar) → focales +
  módulos tocados.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T3 — Responsable de sincronizar `epic_features` · PD-12 · INV-3
- **Files**:
  - `skills/cdad-epic/references/epic-planning.md` (**Modify**: §«If the plan needs to be
    updated during the feature loop» `:130-143` — asignar que aplicar un cambio de plan
    aprobado **incluye sincronizar `epic_features`**; responsable = **coordinador de epic**;
    el escritor único del state es el orquestador).
  - `tests/test_005_006_t3_epic_features.py` (**New**: consistencia documental).
- **Produce**: `responsable-epic-features` (`spec-005-006-PD12`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T1, T4.
- **TDD steps**: RED (la sección asigna el responsable y menciona `epic_features`; el
  enforcement de código `cdad_packet.py:549-554`/`:1459-1509` **no** cambia) → GREEN (edición
  de docs) → focales + módulos tocados.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T4 — README: arranque guiado · PD-11 · INV-6
- **Files**:
  - `README.md` (**Modify**: sección corta de arranque guiado que enuncia que una instrucción
    breve basta y **referencia** `references/project-start.md`; sin el prompt largo).
  - `tests/test_005_006_t4_readme.py` (**New**: consistencia documental).
- **Produce**: `readme-arranque-guiado` (`spec-005-006-PD11`).
- **Consume**: —.
- **Depends_on**: —. **Parallel**: T1, T3.
- **TDD steps**: RED (la sección existe, remite al procedimiento y no reproduce el prompt) →
  GREEN (edición de docs) → focales + módulos tocados.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T5 — Aceptación: recorridos R1/R2/R3 + comprobación empírica de `resume` · PD-16, PD-17
- **Files**:
  - `tests/test_005_006_t5_acceptance.py` (**New**: R1 y R3 con fixtures deterministas
    (tempdir, agnósticos de proyecto/entorno); `resume` sin checkpoint → `rc=0` + proyección
    vacía `no-checkpoint`, contra el CLI).
- **Produce**: `aceptacion-arranque` (`spec-005-006-PD16-PD17`).
- **Consume**: `procedimiento-arranque-corto` (T1), `entrada-de-arranque-intake` (T2),
  `responsable-epic-features` (T3), `readme-arranque-guiado` (T4).
- **Depends_on**: T1, T2, T3, T4. **Parallel**: —.
- **TDD steps**: RED (R1: proyecto nuevo → bootstrap → primer encargo preparado; R3: policy
  ausente → `rc≠0` cerrado con diagnóstico, autoridad sin pin → `approval pending` rc=2;
  `resume` sin checkpoint → `rc=0`/`no-checkpoint`) → GREEN es de los textos de T1..T4 (aquí no
  hay producto nuevo) → focales.
  - **Gate de integración (R2 real, no unitario):** el **arranque real** del proyecto de
    aceptación elegido por el dueño (identificado en el registro local `.cdad/local/`, fuera de
    git) hasta una primera delegación útil; lo corre el **orquestador con el dueño** y se
    registra como evidencia. Es el **VERIFY 5** el que se cierra o queda abierto aquí.
- **Owner**: test-writer (R1/R3/`resume`); orquestador + dueño (R2 real).

### Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el trabajo; suite completa al cierre de la feature; regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "procedimiento-arranque-corto", "contract": "spec-005-006-PD1-PD9-PD13-PD15"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T3", "T4"],
   "files": ["skills/cdad-cycle/references/project-start.md", "skills/cdad-cycle/SKILL.md",
             "skills/cdad-cycle/references/state-detection.md",
             "skills/cdad-cycle/references/continuity.md",
             "tests/test_005_006_t1_start_procedure.py"],
   "focal_tests": ["tests/test_005_006_t1_start_procedure.py"],
   "regressions": ["tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "entrada-de-arranque-intake", "contract": "spec-005-006-PD2-PD10-PD14"}],
   "consume": [{"artifact": "procedimiento-arranque-corto", "contract": "spec-005-006-PD1-PD9-PD13-PD15", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["sources/roles/orchestrator.md", "agents/cdad-orchestrator.md",
             "agents/claude-code/cdad-orchestrator.md",
             "tests/test_005_006_t2_intake.py"],
   "focal_tests": ["tests/test_005_006_t2_intake.py"],
   "regressions": ["tests/test_cdad_generate.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "responsable-epic-features", "contract": "spec-005-006-PD12"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1", "T4"],
   "files": ["skills/cdad-epic/references/epic-planning.md",
             "tests/test_005_006_t3_epic_features.py"],
   "focal_tests": ["tests/test_005_006_t3_epic_features.py"],
   "regressions": ["tests/validate-consistency.sh"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "readme-arranque-guiado", "contract": "spec-005-006-PD11"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1", "T3"],
   "files": ["README.md", "tests/test_005_006_t4_readme.py"],
   "focal_tests": ["tests/test_005_006_t4_readme.py"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T5",
   "produce": [{"artifact": "aceptacion-arranque", "contract": "spec-005-006-PD16-PD17"}],
   "consume": [{"artifact": "procedimiento-arranque-corto", "contract": "spec-005-006-PD1-PD9-PD13-PD15", "producer": "T1"},
               {"artifact": "entrada-de-arranque-intake", "contract": "spec-005-006-PD2-PD10-PD14", "producer": "T2"},
               {"artifact": "responsable-epic-features", "contract": "spec-005-006-PD12", "producer": "T3"},
               {"artifact": "readme-arranque-guiado", "contract": "spec-005-006-PD11", "producer": "T4"}],
   "depends_on": ["T1", "T2", "T3", "T4"],
   "parallel": [],
   "files": ["tests/test_005_006_t5_acceptance.py"],
   "focal_tests": ["tests/test_005_006_t5_acceptance.py"],
   "regressions": [],
   "integration_gate": "arranque real del proyecto de aceptacion (registro local) + suite completa + make validate",
   "owner": "test-writer (checks deterministas); orquestador + dueno (arranque real)"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1/PD-3..PD-9/PD-13/PD-15 → T1; PD-2/PD-10/PD-14 → T2; PD-12 → T3; PD-11 → T4;
  PD-16/PD-17 → T5. Sin PD huérfano; sin tarea sin PD. INV-1..INV-4 → T1/T2; INV-5 → T2;
  INV-6 → T4; INV-7/INV-8 → declarados en spec §9.
- **Placeholders**: ninguno.
- **Consistencia de firmas**: los nombres de archivo (`references/project-start.md`,
  `sources/roles/orchestrator.md`, `skills/cdad-epic/references/epic-planning.md`,
  `README.md`) y los marcadores (`approval pending`, `state incoherent`, `no-checkpoint`) son
  idénticos a los de la spec y a los verificados en el discovery. El CLI se nombra por la
  procedencia de 005-005, sin re-declarar precedencia.
- **Una sola review formal** al final (stage 4): confirma que 005-006 abre un arranque corto
  real **sin trasladar el prompt a una plantilla**, que respeta la frontera 005-003/005-002 y
  que no cambia el alcance del epic.

### Riesgos registrados

- **R1 — Copiar en vez de referenciar.** El procedimiento corto puede degenerar en una segunda
  definición de las reglas (INV-1). Mitigación: el test de consistencia de T1 verifica que
  **referencia** y no copia el algoritmo de detección ni el texto de política.
- **R2 — Orden de las tareas de intake.** T2 consume el procedimiento de T1 → `depends_on`.
  No paralelizar T2 con T1.
- **R3 — Regeneración de agentes.** T2 regenera `agents/cdad-orchestrator.md` y
  `agents/claude-code/cdad-orchestrator.md`; verificar que **solo** cambian esos archivos y que
  el generador coincide con la fuente (`tests/test_cdad_generate.py`).
- **R4 — `resume` sin checkpoint.** El claim de `continuity.md:19` se **fija empíricamente**
  (PD-17); si el CLI discrepa, es un defecto a reportar, no una suposición de la spec.
- **R5 — Proyecto de aceptación real (R2).** Depende de un proyecto externo (registro local);
  no verificable por fixture. El VERIFY 5 se cierra/queda abierto durante esa corrida real; el
  procedimiento **no** debe asumir activación/global/variable.
- **R6 — Frontera 005-003.** No reducir lecturas ni tocar la selección fina del camino de
  continuación; solo la rama «no `resume` en reposo» (PD-9).

### Aprobación

- **Estado: aprobado (2026-10-10)** por el **orquestador OpenCode** bajo la delegación HITL del
  epic-005 (`execution.md`), en la misma acción que la spec. Gate de etapa 3 habilitado.
- Regla original del borrador: el plan se aprueba junto con la spec (una sola acción),
  por el **orquestador OpenCode** bajo la delegación HITL del epic-005 (`execution.md`).
- **Condición de aprobación (orquestador, 2026-10-10).** Los tests de T1/T3/T4 son de
  **consistencia estructural de artefactos distribuidos** (existencia, referencia-en-vez-de-copia,
  cableado, paridad fuente↔generado), según el precedente de 005-005 T2. **No** son suites que
  busquen frases del prompt ni intentos de probar determinísticamente que un modelo seguirá
  instrucciones (requisitos de orquestación eficiente:
  `docs/specs/004-003-planning-procedures/efficient-orchestration-requirements.md:107`).
  Los aspectos de pura prosa se verifican por **review** (la única review formal de la feature).
  T5 aporta las comprobaciones de comportamiento (R1/R3 y `resume` sin checkpoint).
