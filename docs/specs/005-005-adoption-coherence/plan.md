> Plan **aprobado** (2026-10-09) junto con la spec. Texto del **architect** (subetapa `draft`,
> stage 2), materializado con el flujo (receive + materialize CAS) por el orquestador
> (ADR-003); aprobado por el orquestador OpenCode bajo la delegación HITL de epic-005.
> Decisiones D1–D8 aprobadas en `spec.md` §7. Construcción según CDAD stages 3–5 (TDD con
> test-writer/implementer por paquete, una sola review formal al final y Memory Bank al cierre).

## Plan — 005-005-adoption-coherence

**Feature ID:** `005-005-adoption-coherence` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-09, orquestador OpenCode, HITL delegada epic-005). Insumo: `docs/specs/005-005-adoption-coherence/discovery.md`.

### Restricciones globales

- Rama `codex/epic-005-real-operation`; **sin push**; **sin `--no-verify`**.
- **No** instalar CDAD en HOME ni activar versiones (reservado al dueño). **No** ejecutar el
  CLI del repo para **operar** este ciclo (el repo se **desarrolla**; el ciclo corre con la
  instalación vigente).
- No leer `tests/.sensitive-patterns.local`.
- Para comprobar un RED sin el arreglo: **worktree**, nunca `git stash` en el árbol compartido.
- No volcar salidas enormes al contexto.
- **Gate de tests.** Durante el trabajo: **focales + módulos tocados**. **Suite completa al
  cierre de la feature** (la feature toca el renderer/CLI `cdad_packet.py`, el instalador y
  docs), más `make validate` al cierre. La feature **fija** esta misma política en la
  metodología (T2), sin duplicarla.
- Ante un obstáculo fuera del ámbito: entregar el diagnóstico, no fabricar registros.

### Tareas

#### T1 — El reemplazo valida el encargo conservado · PD-1..PD-7, INV-1..INV-5
- **Files**: `skills/cdad-cycle/scripts/cdad_packet.py` (Modify: `_validate_corrections` —
  validar el **encargo resultante completo** (conservado + corregido); extraer el chequeo de
  existencia de `inputs` (`:1858`) para aplicarlo a **todo** `inputs`; reusar los textos
  campo/motivo/opción para los campos conservados; call site en `_replace_packet` `:2022-2025`).
  **Tests (New)**: `tests/test_005_005_t1_replace_conserved.py`.
- **Produce**: `reemplazo-valida-conservado` (`spec-005-005-PD1-PD7`).
- **Consume**: contrato verificado; sub-modo `--replace-packet` de 005-001.
- **Depends_on**: —.
- **TDD steps**: RED (focal: **input conservado inexistente → `rc=2`** con campo/motivo/opción;
  alcance conservado fuera de política → `rc=2` con campo/opción; **recuperación** con la
  corrección → `rc=0`; **camino normal sin restricción nueva** → `rc=0`; `inputs` vacío →
  válido; pisos del rol intactos; todos `AssertionError` de comportamiento, caja negra por
  subprocess en tempdir) → GREEN (mínimo) → focales + módulos tocados.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T2 — Una sola política de tests · PD-8..PD-11, INV-6 · *doc-only*
- **Files**: `skills/cdad-cycle/references/stage-3-tdd.md` (Modify: nueva §«Test evidence
  policy» — dueño canónico de la política; alinear `:153` y menciones `:31`/`:57`/`:123`/
  `:137`/`:150`/`:169`/`:217`); `references/re-entry.md` (Modify: checklist «Implementer —
  GREEN» referencia la política; **§«Equivalence of a registered run» sigue siendo el dueño
  único** de la reutilización); `packets/substages/implementer-green.md`,
  `implementer-refactor.md`, `implementer-review-fix.md`, `packets/roles/implementer.md`
  (Modify: remitir a la política, sin «the required full regression suite» indefinido);
  `skills/cdad-cycle/SKILL.md` (Modify: gates); `references/handoff-prompts.md`,
  `stage-4-review.md`, `stage-5-merge.md`, `sub-agent-strategies.md` (Modify si afirman
  frecuencia por GREEN); `docs/specs/005-001-idle-and-v7-bootstrap/spec.md` (Modify: enmienda
  de **PD-17** con fecha + decisión sobre el pin). Sin código de producto.
- **Produce**: `politica-unica-de-tests` (`spec-005-005-PD8-PD10`); `enmienda-pd17`
  (`spec-005-005-PD11`).
- **Consume**: —.
- **Depends_on**: —.
- **TDD steps**: verificación **documental** por barrido + test de consistencia
  (`tests/test_005_005_t2_docs_policy.py`): asserta que existe la sección única de política y
  que los consumidores **no** afirman «once per GREEN»/«required full regression suite».
  Focales = el test de consistencia + el barrido `grep` de la evidencia.
- **Owner**: RED: test-writer (test de consistencia); GREEN: implementer (edición de docs).

#### T3 — Procedencia de la instalación + documentación de 005-001 · PD-12..PD-17, INV-7
- **Files**: `skills/cdad-cycle/scripts/cdad_packet.py` (Modify: `_derived_source_dir`/`:2454`
  — resolver el origen desde `.cdad/activation.json` cuando exista; **diagnóstico de
  contradicción** que nombra registro + versiones; `_build_derived_payloads`/`:2680` y el
  manifiesto `:2706-2712` — declarar **versión/commit** de origen; `_publish_generation`
  `:2976-2985` — aviso que nombra registro y versión); `references/opencode-delegation.md`
  (Modify: recarga de sesión/agentes/skills + procedencia verificable); `references/runtime-adoption.md`
  (Modify: regla de procedencia); `docs/specs/005-001-idle-and-v7-bootstrap/review.md`
  (Modify: normalización, PD-27→PD-20); `docs/epics/epic-005-real-operation/handoff-opencode.md`,
  `handoff-opencode-2.md`, `execution.md` (Modify: rutas personales, según PD-17/D7);
  `.cdad/local/` (registro local, fuera de git — no es archivo del repo). **Tests (New)**:
  `tests/test_005_005_t3_provenance.py`.
- **Produce**: `procedencia-instalacion` (`spec-005-005-PD12-PD15`);
  `docs-005-001-normalizados` (`spec-005-005-PD16-PD17`).
- **Consume**: —.
- **Depends_on**: —.
- **TDD steps**: RED (focal: con `.cdad/activation.json` **sintético** presente y sin la
  variable, `source_dir` del manifiesto = raíz adoptada registrada, no HOME; contradicción →
  diagnóstico que nombra registro + versiones; el manifiesto/agente declara versión; todos
  `AssertionError` de comportamiento) → GREEN (mínimo) → focales + módulos tocados. La
  comprobación de `opencode reload` (PD-15) es **documental**: en aislamiento, o diagnóstico;
  **nunca** afirmarlo.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T4 — Integración desde una instalación aislada · PD-18, INV-8
- **Files**: `tests/test_005_005_t4_integration.py` (New). Sin cambios de producto.
- **Produce**: `integracion-instalacion-aislada` (`spec-005-005-PD18`).
- **Consume**: `reemplazo-valida-conservado` (T1), `politica-unica-de-tests` (T2),
  `procedencia-instalacion` (T3).
- **Depends_on**: T1, T2, T3.
- **TDD steps**: instalar la versión del repo en una **raíz aislada** (nunca HOME); con ese
  CLI, secuencia **prepare → `--replace-packet` (validación completa) → despacho con validación
  proporcional**, sin rodeos manuales. Si algo falla, volver a la tarea correspondiente.
  Verificación adicional de `make validate`.
- **Owner**: test-writer (test de integración); implementer solo si destapa un defecto.

### Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante el trabajo; suite completa al cierre de la feature (renderer/CLI, instalador y docs tocados); regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "reemplazo-valida-conservado", "contract": "spec-005-005-PD1-PD7"}],
   "consume": [{"artifact": "contrato-verificado", "contract": "cdad_packet.validate_request"},
               {"artifact": "submodo-replace", "contract": "spec-005-001-PD7-PD11-PD19-PD24"}],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "tests/test_005_005_t1_replace_conserved.py"],
   "focal_tests": ["tests/test_005_005_t1_replace_conserved.py"],
   "regressions": ["tests/test_005_001_tcorr.py", "tests/test_005_001_t2_replace_packet.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "politica-unica-de-tests", "contract": "spec-005-005-PD8-PD10"},
               {"artifact": "enmienda-pd17", "contract": "spec-005-005-PD11"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1", "T3"],
   "files": ["skills/cdad-cycle/references/stage-3-tdd.md", "skills/cdad-cycle/references/re-entry.md",
             "skills/cdad-cycle/packets/substages/implementer-green.md",
             "skills/cdad-cycle/packets/substages/implementer-refactor.md",
             "skills/cdad-cycle/packets/substages/implementer-review-fix.md",
             "skills/cdad-cycle/packets/roles/implementer.md", "skills/cdad-cycle/SKILL.md",
             "docs/specs/005-001-idle-and-v7-bootstrap/spec.md",
             "tests/test_005_005_t2_docs_policy.py"],
   "focal_tests": ["tests/test_005_005_t2_docs_policy.py"],
   "regressions": [],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "procedencia-instalacion", "contract": "spec-005-005-PD12-PD15"},
               {"artifact": "docs-005-001-normalizados", "contract": "spec-005-005-PD16-PD17"}],
   "consume": [],
   "depends_on": [],
   "parallel": ["T1", "T2"],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py",
             "skills/cdad-cycle/references/opencode-delegation.md",
             "skills/cdad-cycle/references/runtime-adoption.md",
             "docs/specs/005-001-idle-and-v7-bootstrap/review.md",
             "docs/epics/epic-005-real-operation/handoff-opencode.md",
             "docs/epics/epic-005-real-operation/handoff-opencode-2.md",
             "docs/epics/epic-005-real-operation/execution.md",
             "tests/test_005_005_t3_provenance.py"],
   "focal_tests": ["tests/test_005_005_t3_provenance.py"],
   "regressions": ["tests/test_004_002_t7_l1_derived.py", "tests/test_003_006_t2_activation.py",
                   "tests/test_role_packet_render.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "integracion-instalacion-aislada", "contract": "spec-005-005-PD18"}],
   "consume": [{"artifact": "reemplazo-valida-conservado", "contract": "spec-005-005-PD1-PD7", "producer": "T1"},
               {"artifact": "politica-unica-de-tests", "contract": "spec-005-005-PD8-PD10", "producer": "T2"},
               {"artifact": "procedencia-instalacion", "contract": "spec-005-005-PD12-PD15", "producer": "T3"}],
   "depends_on": ["T1", "T2", "T3"],
   "parallel": [],
   "files": ["tests/test_005_005_t4_integration.py"],
   "focal_tests": ["tests/test_005_005_t4_integration.py"],
   "regressions": [],
   "integration_gate": "suite completa + make validate",
   "owner": "test-writer"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1..PD-7 → T1; PD-8..PD-11 → T2; PD-12..PD-17 → T3; PD-18 → T4. Sin PD
  huérfano; sin tarea sin PD. INV-1..INV-5 → T1/T2; INV-6 → T2; INV-7 → T3; INV-8 → T4.
- **Placeholders**: ninguno.
- **Consistencia de firmas**: `--replace-packet`/`--reason` y las opciones de corrección
  (`--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence`, centinela
  `-`) son las de 005-001 PD-19..PD-24, idénticas en spec y plan; `CDAD_OPENCODE_AGENTS_DIR`,
  `.cdad/activation.json`, `<adopted_root>/.config/opencode/agents` y los marcadores de 005-001
  se usan con el mismo nombre.
- **Una sola review formal** al final (stage 4), que confirme que 005-005 **elimina
  contradicciones y trabajo manual sin sumar restricciones**, y que separe **principio de
  CDAD / decisión del proyecto / particularidad del entorno** (handoff §4).

### Riesgos registrados

- **R1 — Enmienda de un artefacto de una feature `done`.** Editar
  `docs/specs/005-001-idle-and-v7-bootstrap/spec.md` (PD-17) deriva su `contract_sha256` y la
  aprobación pineada de 005-001 deja de coincidir (PD-4 de 005-001). 005-001 está `done`: la
  edición es **documental**. Decidir al aprobar si se **re-registra** el pin o se declara el
  motivo por el que no aplica (D-a confirmar; ver spec §8).
- **R2 — Validación de listas vacías.** `_validate_corrections` reusada para el universo
  completo **no** debe rechazar listas vacías legítimas (`--input -`, PD-6/D7 de 005-001).
- **R3 — Derivación del layout del registro.** `activation.json` guarda `adopted_root`, **no**
  la ruta de agentes: `prepare` debe derivar `<adopted_root>/.config/opencode/agents`. Verificar
  que el layout es estable (usado en `dispatch-ledger.md:33`); **VERIFY** del discovery §T3.
- **R4 — `opencode reload` no comprobado.** El adaptador (PD-15) no debe afirmarlo sin la
  comprobación en aislamiento; si no es posible, diagnóstico.
- **R5 — Superficie tocada.** T1/T3 tocan `cdad_packet.py` (renderer/CLI): la suite completa al
  cierre es obligatoria; la paridad del CLI instalado (`test_packet_prepare.py::test_p5_…`)
  debe seguir verde.
- **R6 — Sin CI.** El gate es la suite local + deuda registrada; `make validate` tiene 2 FAIL
  F011 preexistentes (`install.sh --check` / A3) que **no** se atribuyen a este diff.
- **R7 — Sin activación real en este repo.** No hay `.cdad/activation.json` en el repo: el
  test focal de T3 (PD-12/PD-13) debe usar un **fixture sintético** (tempdir), no depender de
  una activación real ni tocar HOME.
- **R8 — Rutas personales: criterio vs enumeración.** El encargo enumera `handoff-opencode.md:63`
  y `execution.md:21`; el criterio (D7) los conserva por ser convención genérica. **VERIFY
  (dueño)** antes de fijar el texto final de PD-17.
