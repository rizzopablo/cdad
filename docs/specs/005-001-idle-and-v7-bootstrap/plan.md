> Materializado por el orquestador desde `architect-draft-001.md` (architect,
> `mofgw/deepseek-v4.1-flash`), verbatim salvo encabezado. Aprobado por el
> orquestador OpenCode bajo la delegación HITL de epic-005 (`execution.md`),
> 2026-10-08. Decisiones D1–D6 resueltas en `spec.md` §7.
>
> **Enmienda 2026-10-09 (T-CORR).** Se agrega la tarea **T-CORR** (antes de T4)
> con las dos correcciones acotadas de T1/T2 instruidas por el dueño
> (`docs/epics/epic-005-real-operation/plan.md`, apartado «Cambios al plan»,
> 2026-10-09): C1 (ruta de la aprobación, PD-18) y C2 (conservación del reemplazo,
> PD-19..PD-24). T4 pasa a depender también de T-CORR. La enmienda fue
> **aprobada el 2026-10-09** por el orquestador OpenCode (HITL delegada epic-005)
> y el pin de `spec.md` se re-registró en `stage_history` con los bytes nuevos.

## Plan — 005-001-idle-and-v7-bootstrap

**Feature ID:** `005-001-idle-and-v7-bootstrap` · **Epic:** `epic-005-real-operation` ·
**Estado:** aprobado (2026-10-08, orquestador OpenCode, HITL delegada epic-005);
**enmienda T-CORR (2026-10-09) aprobada (orquestador OpenCode, HITL delegada epic-005)**.
Costrucción según CDAD stages 3–5 (TDD con test-writer/implementer por paquete,
review y Memory Bank al cierre).

### Restricciones globales

- Rama `codex/epic-005-real-operation`; sin push; sin `--no-verify`.
- v7 `ce09ed0`; no instalar/activar versiones (dueño). No leer `tests/.sensitive-patterns.local`.
- **Gate de tests.** Durante los ajustes de T-CORR: **focales + módulos tocados**. **Suite completa al cierre de la feature** (la feature toca el renderer/CLI `cdad_packet.py`: «suite completa al cierre de cada feature o si se toca instalador, staging o renderer»), más focales del área y `make validate` al cierre.

### Tareas

#### T1 — Modelo de autorización por rol (corrige I2 circular) · PD-1..PD-6, PD-12(aprobación)
- **Files**: `skills/cdad-cycle/scripts/cdad_packet.py` (Modify: `_validate_v2_vigency`, `_validate_v2_state`, nueva `_contract_approval_for(role, contract, state, execution, project_root)` invocada desde `validate_request`); `skills/cdad-cycle/references/project-execution.md` §2 (Modify); `skills/cdad-cycle/references/re-entry.md` (Modify: forma pineada del registro); `skills/cdad-cycle/references/stage-2-specification.md` (Modify si corresponde). **Tests (RED/New)**: `tests/test_005_001_t1_role_approval.py`. **Tests (migrados, consecuencia)**: `tests/test_role_packets.py`, `tests/test_packet_prepare.py`, `tests/test_004_002_t2_bootstrap.py`, `tests/test_004_002_t2_reviewfix.py`, `tests/test_004_002_t6_landing.py`, `tests/test_003_002_t1_receive.py`, `tests/test_003_002_t2_materialize.py`, `tests/test_003_002_t3_run_evidence.py`, `tests/test_003_002_t4_integration.py`.
- **Produce**: autorización role-aware; forma pineada del registro de spec; marcador `approval pending`.
- **Consume**: contrato verificado en `validate_request`.
- **Depends_on**: —.
- **TDD steps**: RED (PD-1..PD-6 + migración de fixtures, todos `AssertionError` de comportamiento) → GREEN (mínimo) → focales + **suite completa**.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T2 — Reemplazo de paquete preparado no despachado + diagnósticos de obsolescencia · PD-7..PD-11, PD-16, PD-12(paquete obsoleto)
- **Files**: `cdad_packet.py` (Modify: parser, `_reject_mode_mix`, `main`, nueva `_replace_packet`, ajuste de `_resume_packet` para emitir el marcador); `references/project-execution.md` (Modify: nueva sección "Reemplazo"). **Tests (New)**: `tests/test_005_001_t2_replace_packet.py`.
- **Produce**: sub-modo `--replace-packet`/`--reason`; registro `.superseded.json`; marcador `packet obsolete`.
- **Consume**: T1 (la autorización vigente gatea el contrato nuevo).
- **Depends_on**: T1.
- **TDD steps**: RED → GREEN → focales + suite completa.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T3 — Reposo legítimo + estado incoherente · PD-13..PD-15, PD-12(estado incoherente)
- **Files**: `cdad_packet.py` (Modify: rama `validate-state` en `main` `:2991-3010` + validación de coherencia de idle); `references/state-detection.md` (Modify: criterio de reposo). **Tests (New)**: `tests/test_005_001_t3_idle.py`.
- **Produce**: aceptación del reposo; marcador `state incoherent`.
- **Consume**: — (usa la coherencia v2 existente).
- **Depends_on**: T1 (no regresar la verificación de vigencia; misma rama de validación).
- **TDD steps**: RED (positivo idle + 2 negativos + en-vuelo) → GREEN → focales + suite completa.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T-CORR — Correcciones acotadas de T1/T2 (ruta de la aprobación y conservación del reemplazo) · PD-18..PD-24 · *enmienda 2026-10-09*
- **Files**: `skills/cdad-cycle/scripts/cdad_packet.py` (Modify: `_contract_approval_for` — exigir que el pin nombre el contrato (`contract_path` además de `contract_sha256`); `_replace_packet` — conservar el encargo anterior del `REQUEST.json` y aplicar las opciones de corrección + traza `conserved_fields`/`changed_fields` en `.superseded.json`; `build_parser` + `_reject_mode_mix` — admitir las opciones de corrección solo en el sub-modo replace y rechazar el argv mezclado); `skills/cdad-cycle/references/project-execution.md` (Modify: §2 authority — pin que nombra el contrato; §«Reemplazo» — conservación y corrección). **Tests (New)**: `tests/test_005_001_tcorr.py`.
- **Produce**: `correccion-ruta-aprobacion` (PD-18); `correccion-conservacion-reemplazo` (PD-19..PD-24).
- **Consume**: T1 (`_contract_approval_for`; autorización por rol), T2 (`--replace-packet`; `.superseded.json`).
- **Depends_on**: T1, T2.
- **TDD steps**: RED (6 focales: 5 de C2 + 1 de C1; todos `AssertionError` de comportamiento) → GREEN (mínimo) → focales + módulos tocados; **suite completa al cierre de la feature**.
- **Owner**: RED: test-writer; GREEN: implementer.

#### T4 — Prueba decisiva e integración · PD-17
- **Files**: `tests/test_005_001_t4_decisive.py` (New). Sin cambios de producto.
- **Consume**: T1, T2, T3, T-CORR.
- **Depends_on**: T1, T2, T3, T-CORR.
- **TDD steps**: el escenario secuencial de PD-17 (si algo falla, vuelve a la tarea correspondiente); verificación adicional de `make validate`.
- **Owner**: test-writer (RED del escenario completo); implementer solo si destapa un defecto.

### Bloque canónico `plan-tasks`

```plan-tasks
{"validation_strategy": "focales + modulos tocados durante los ajustes de T-CORR; suite completa al cierre de la feature (renderer/CLI tocado); regresiones del area tocada; make validate al cierre",
 "tasks": [
  {"id": "T1",
   "produce": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6"}],
   "consume": [{"artifact": "contrato-verificado", "contract": "cdad_packet.validate_request"}],
   "depends_on": [],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-execution.md", "tests/test_005_001_t1_role_approval.py"],
   "focal_tests": ["tests/test_005_001_t1_role_approval.py"],
   "regressions": ["tests/test_role_packets.py", "tests/test_packet_prepare.py", "tests/test_004_002_t2_bootstrap.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T2",
   "produce": [{"artifact": "reemplazo-paquete-obsoleto", "contract": "spec-005-001-PD7-PD11-PD16"}],
   "consume": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6", "producer": "T1"}],
   "depends_on": ["T1"],
   "parallel": [],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-execution.md", "tests/test_005_001_t2_replace_packet.py"],
   "focal_tests": ["tests/test_005_001_t2_replace_packet.py"],
   "regressions": ["tests/test_packet_prepare.py", "tests/test_004_002_t56_reviewfix.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T3",
   "produce": [{"artifact": "reposo-legitimo", "contract": "spec-005-001-PD13-PD15"}],
   "consume": [],
   "depends_on": ["T1"],
   "parallel": ["T2"],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/state-detection.md", "tests/test_005_001_t3_idle.py"],
   "focal_tests": ["tests/test_005_001_t3_idle.py"],
   "regressions": ["tests/test_004_002_t2_reviewfix.py", "tests/test_004_002_w1_delegation.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T-CORR",
   "produce": [{"artifact": "correccion-ruta-aprobacion", "contract": "spec-005-001-PD18"},
               {"artifact": "correccion-conservacion-reemplazo", "contract": "spec-005-001-PD19-PD24"}],
   "consume": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6", "producer": "T1"},
               {"artifact": "reemplazo-paquete-obsoleto", "contract": "spec-005-001-PD7-PD11-PD16", "producer": "T2"}],
   "depends_on": ["T1", "T2"],
   "parallel": ["T3"],
   "files": ["skills/cdad-cycle/scripts/cdad_packet.py", "skills/cdad-cycle/references/project-execution.md", "tests/test_005_001_tcorr.py"],
   "focal_tests": ["tests/test_005_001_tcorr.py"],
   "regressions": ["tests/test_005_001_t1_role_approval.py", "tests/test_005_001_t2_replace_packet.py"],
   "integration_gate": "@validation_strategy",
   "owner": "RED: test-writer; GREEN: implementer"},
  {"id": "T4",
   "produce": [{"artifact": "prueba-decisiva", "contract": "spec-005-001-PD17"}],
   "consume": [{"artifact": "autorizacion-por-rol", "contract": "spec-005-001-PD1-PD6", "producer": "T1"},
               {"artifact": "reemplazo-paquete-obsoleto", "contract": "spec-005-001-PD7-PD11-PD16", "producer": "T2"},
               {"artifact": "reposo-legitimo", "contract": "spec-005-001-PD13-PD15", "producer": "T3"},
               {"artifact": "correccion-ruta-aprobacion", "contract": "spec-005-001-PD18", "producer": "T-CORR"},
               {"artifact": "correccion-conservacion-reemplazo", "contract": "spec-005-001-PD19-PD24", "producer": "T-CORR"}],
   "depends_on": ["T1", "T2", "T3", "T-CORR"],
   "parallel": [],
   "files": ["tests/test_005_001_t4_decisive.py"],
   "focal_tests": ["tests/test_005_001_t4_decisive.py"],
   "regressions": [],
   "integration_gate": "suite completa + make validate",
   "owner": "test-writer"}
 ]}
```

### Auto-revisión del plan

- **Cobertura**: PD-1..PD-6→T1; PD-7..PD-11/PD-16→T2; PD-13..PD-15→T3; PD-18..PD-24→T-CORR; PD-17→T4; PD-12→definido por marcadores en T1/T2/T3. Sin PD huérfano; sin tarea sin PD.
- **Placeholders**: ninguno.
- **Consistencia de firmas**: `--replace-packet`/`--reason`, las opciones de corrección `--input/--read-scope/--write-scope/--invariant/--expected-output/--evidence` (centinela `-`), `contract_path`/`contract_sha256`, marcadores `approval pending`/`packet obsolete`/`state incoherent` usados idénticos en spec y plan.
- **Consecuencia de alcance declarada**: T1 obliga a migrar fixtures (mismo patrón que 004-003 T4); las aserciones no se debilitan, solo se agrega el pin derivado del `spec.md` del fixture. T-CORR no cambia el alcance ni los criterios del epic.

### Riesgos registrados (R1–R5 del architect)

- **R1 — Radio de la migración de fixtures**: puede tocar 10 archivos; si crece, evaluar separar "T1-red-fixtures" (patrón 004-003).
- **R2 — Mensajes vs oráculos existentes**: los negativos actuales exigen tokens `stage_history|specification|approved`; el marcador nuevo debe conservarlos. Verificar en el RED.
- **R3 — Paridad del CLI instalado**: tocar `cdad_packet.py` obliga a que `test_packet_prepare.py::test_p5_installed_cli_prepare_matches_repo_prepare` siga verde; la suite completa al cierre lo cubre.
- **R4 — Sin CI**: el gate es la suite local + deuda registrada; `make validate` tiene 2 FAIL preexistentes conocidos (F011) que no deben atribuirse a este diff.
- **R5 — Enmienda sobre artefactos aprobados**: al editar `spec.md`, su `contract_sha256` deriva (PD-4) y la aprobación vigente (2026-10-08) deja de coincidir; el orquestador debe **re-registrar la aprobación pineada** de la enmienda antes de despachar T-CORR. El plan del epic también cambió de hash (apartado «Cambios al plan», 2026-10-09). La enmienda no se considera aprobada hasta ese re-registro.
