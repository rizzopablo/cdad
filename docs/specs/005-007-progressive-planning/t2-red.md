# RED — 005-007 T2 (test-writer, substage red)

**Packet:** `005-007-progressive-planning-test-writer-red-002`
**Contrato:** `docs/specs/005-007-progressive-planning/spec.md` (PD-1, PD-2; sha256 `54877103…` — leído, no verificado re-hash en esta sesión)
**Postcondiciones de la tarea (ficha T2):** PD-2 (base PD-1), focal `tests/test_005_007_t2_progressive_plan_validator.py`.

## Archivos modificados

- `tests/test_005_007_t2_progressive_plan_validator.py` — **nuevo** (único archivo tocado; commit `git show --stat`: 1 file changed, 416 insertions).
- Nada fuera de `tests/`. La modificación observada en `docs/.cdad-state.json` en el worktree (`active_packet` → `005-007-progressive-planning-test-writer-red-002`, status `dispatched`) es la escritura de **preparación/despacho del orquestador**, previa a esta sesión; no la toqué (fuera de mi write scope) y **no** está en mi commit.

## Comando exacto (el declarado en la ficha T2 para RED)

```
python3 -m pytest tests/test_005_007_t2_progressive_plan_validator.py -q
```

(cwd: raíz del repo, rama `codex/epic-005-real-operation`)

## Salida (resumen final — la prueba del RED)

```
FAILED tests/test_005_007_t2_progressive_plan_validator.py::TestPd2ProgressivePlannedIsAccepted::test_pd2_planned_task_without_validation_plan_is_accepted
FAILED tests/test_005_007_t2_progressive_plan_validator.py::TestPd1PlannedFieldNegativesAreRejected::test_pd2_planned_missing_progressive_field_is_rejected
FAILED tests/test_005_007_t2_progressive_plan_validator.py::TestPd2UnknownDetailFailsClosed::test_pd2_detail_outside_closed_set_is_rejected
FAILED tests/test_005_007_t2_progressive_plan_validator.py::TestPd2MechanicalChecksApplyToPlanned::test_pd2_mechanical_checks_apply_to_planned_tasks
4 failed, 2 passed in 4.47s
```

## Caso → postcondición → estado HOY (fallo y salida)

Antes de escribir el RED hice un sondeo black-box del CLI (subprocess sobre fixtures temporales; **nunca leí `skills/cdad-cycle/scripts/cdad_packet.py` ni ningún archivo de implementación**) para fijar honestamente las aserciones. Estado por caso:

1. **POSITIVO (PD-1/PD-2 + AC-1):** tarea `detail: "planned"` con `objective` + `depends_on` + `uncertainty` + `owner` + `resolves_when`, SIN plan de validación por tarea → `prepare` debe aceptar (rc=0, paquete publicado). **FALLA HOY**: `AssertionError: 2 != 0 : the honest progressive plan was rejected: ERROR: plan task 't1' is missing its per-task validation plan: a non-empty focal_tests (code task) or observable_checks (code-less task) is required (PD-8)`. El validador de hoy exige el plan a TODAS las tareas.
2. **NEGATIVOS por campo (PD-1):** `planned` sin `objective` / `uncertainty` / `owner` / `resolves_when` (un subTest por campo) → rc≠0 con diagnóstico que nombra la tarea y el campo. **FALLA HOY**: el diagnóstico de hoy no nombra el campo PD-1; pytest detiene en el primer subTest: `AssertionError: 'objective' not found in "ERROR: plan task 't1' is missing its per-task validation plan: a non-empty focal_tests (code task) or observable_checks (code-less task) is required (PD-8)"`. El sondeo confirmó el mismo fallo de token para `uncertainty`/`owner`/`resolves_when`.
3. **`detail` fuera del conjunto cerrado (PD-2/INV-4):** `detail: "later"` → rc≠0 nombrando la tarea y el valor. **FALLA HOY**: `AssertionError: 'later' not found in "ERROR: plan task 't1' is missing its per-task validation plan: …"` — hoy el valor desconocido no se nombra (el rechazo es por el plan de validación faltante).
4. **CHECKS MECÁNICOS sobre `planned` (PD-2):** (a) `planned` + consumidor de productor inexistente `t9` → rc≠0 nombrando `t9` y `contract-b`; (b) ciclo `depends_on` que incluye la `planned` → rc≠0 nombrando los miembros. **FALLA HOY por el control honesto embebido**: `AssertionError: 2 != 0 : the honest progressive plan was rejected` — el plan progresivo mixto (productor `planned` + consumidor `next`, contratos matched) es rechazado hoy, así que el rechazo por el defecto mecánico no puede atribuirse al defecto; los diagnósticos mecánicos de hoy ya nombran `t9`/`contract-b` y `t1 -> t2 -> t1` (verificado por sondeo: corren antes que el check de validación por tarea), y quedarán como conservación al GREEN.
5. **REGRESIÓN sin marcador (PD-2):** bloque sin `detail`, tarea con código sin `focal_tests`/`observable_checks` → rc≠0 nombrando `t1` y `focal_tests`. **PASA HOY** (verde por diseño): su postcondición es "se comporta exactamente como hoy"; es un control que congela el comportamiento actual para impedir cambios al aterrizar el tratamiento progresivo.
6. **REGRESIÓN positiva (PD-1/PD-2):** todas las tareas `"next"` (explícito) o sin marcador con plan de validación completo → sigue aceptándose (rc=0, paquete publicado), dos subTests. **PASA HOY** (verde por diseño, misma razón: "sigue aceptandose igual que hoy").

**Declaración explícita para el orquestador:** la regla del packet «cada caso debe fallar HOY por AssertionError» se cumple en los casos 1–4 (firma del RED: `4 failed`, todos `AssertionError`, ninguno por `ImportError`/sintaxis/fixture, sin skips). Los casos 5 y 6 son controles de regresión cuyo postcondicionado declarado es **precisamente** el comportamiento de hoy («como hoy», «igual que hoy»): no puede existir una aserción honesta que los haga fallar hoy; se entregan verdes por diseño y así se declara. Si el orquestador requiere que todo el archivo sea rojo, es un conflicto de contrato a resolver ahí — no se fabricó.

## Aserciones de los negativos (estilo congelado 004-003)

Cada negativo verifica: rc≠0, `^ERROR: ` en stderr, tokens nombrados (solo ids de tarea, nombres de campo, ids de productor, artefactos, el valor ofensivo — nunca wording exacto), stdout vacío, out-dir sin entradas, state sin cambios, árbol del proyecto sin cambios. Control honesto primero en cada test (plan sin marcador válido renderiza).

## Procedencia y aislamiento

- Fixtures: patrón reutilizado de `tests/conftest.py`, `tests/test_004_003_t1_draft_contract.py` (`DRAFT_PLAN_BYTES`/`DRAFT_PLAN_RELPATH`/`DRAFT_PLAN_VERSION`), `tests/test_004_003_t3_plan_checks.py` y `tests/test_004_003_t4_validation_fields.py` (todos en read scope). Proyecto temporal autocontenido por test (`tempfile.TemporaryDirectory`), policy y state v2 coherentes vía `PrepareProject`; sin dependencia del estado real del repo ni rutas absolutas del host (INV-6).
- No se leyó implementación; no se cargó `cdad-cycle` (el packet es el contrato de ejecución); no se corrió la suite completa (política de suite: la corre quien cierra); sin skips, sin `--no-verify`.

## Commit

```
07abeb20697b046d66a405b2edbf9093c7c913a2 test: RED 005-007 T2 — validador plan-tasks con detalle progresivo (PD-1/PD-2)
```
Rama: `codex/epic-005-real-operation` · 1 file changed, 416 insertions(+) — solo `tests/test_005_007_t2_progressive_plan_validator.py`.
