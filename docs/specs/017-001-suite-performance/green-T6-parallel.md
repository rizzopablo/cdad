Route C work complete. FINAL TEXT report below.

---

# FINAL TEXT — implementer GREEN T6 (017-001-suite-performance), packet `017-001-suite-performance-implementer-green-007`

## 1. Intake (Route C — explicit file backup): VALIDATED

- Identificación del dispatch (`packet_id …-green-007`, `execution_id exec-017-001-suite-performance-001`, contrato `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0…92672e`): **coincide** con `REQUEST.json` y `PACKET.md`.
- `python3 scripts/cdad_packet.py validate-request --request …/REQUEST.json --execution-context …/execution.json` → **EXIT 0**.
- `python3 scripts/cdad_packet.py validate-packet --request … --packet …/PACKET.md --execution-context …` → **EXIT 0**.
- Contexto de ejecución `schema_version: 2` → **v2 confirmado**, sin switch silencioso. Cero marcadores inline en el prompt → sin mezcla route A/C. **No se cargó `cdad-cycle` ni otro skill de ciclo**: el packet es el contrato.
- Solo leí insumos declarados (`spec.md`, `performance/parallelism.md`, `red-T6-parallel.md`, `tests/test_017_001_suite_parallel.py`, `scripts/cdad-suite.py`) y solo edité el write_scope (`scripts/`). **No toqué `tests/` ni el contrato.**

## 2. Implementación entregada

**Archivo modificado:** `scripts/cdad-suite.py` (+378/−1, puramente aditivo salvo una palabra del docstring).
**Commit:** `10dfae99` — `feat(017-001-T6): parallel subcommand with per-worker pytest isolation and wall/work/overlap aggregate` (solo ese archivo; `M docs/.cdad-state.json` del worktree es preexistente y no es mío, quedó fuera del commit).

Nuevo subcomando `parallel --workers N --evidence-root <dir> [--nodeids <f>|--capability|--all] [--balance-from <profile.json>]`, separado de `close` (código de `close` intacto, verificado por diff):

- `--workers` default **2**; validación `1 <= N <= nproc-1` (aquí nproc=8, máx 7); rechazo con **salida 2 y motivo con "workers" por stderr**.
- Partición **por archivo** (orden interno conservado, sin repetir nodeids): agrupación por archivo + asignación golosa al worker menos cargado (costo medido desde `--balance-from` si trae fases, si no conteo; determinista).
- Un proceso `pytest` hijo por worker lanzados en concurrente (`Popen` + `wait`), cada uno con `HOME`, `XDG_CONFIG_HOME/DATA/CACHE` y `TMPDIR` propios bajo `worker-<i>/`, mismo argv efectivo que el cierre serial (observador + junit), y evidencia `pytest.xml`, `phases-raw.json`, `stdout/stderr.log`, `profile.json` mínimo, `nodeids.txt`.
- Canary antes/después (`canary-before/after.txt` + `delta_lines`); hijos esperados y terminados (`children_terminated`, `orphans: 0`).
- Agregado `parallel.json` + `parallel.md`: pared por worker y pared total (reloj de pared), trabajo medido por worker (`work_measured_s` = Σ duraciones del XML, **rotulado como trabajo, nunca pared**), `overlap_s` = Σ pared − pared total declarado, resultado consolidado, equivalencia contra el serial.

## 3. Evidencia de comandos y salidas

- Focal nueva: `python3 -m pytest tests/test_017_001_suite_parallel.py -v` → **5 failed, 1 passed** (pasa solo `rejects_invalid_worker_counts`). **NO verde: bloqueado por defectos del oráculo, §5. Tests intactos.**
- Regresión proporcional: `python3 -m pytest tests/test_017_001_suite_profile.py tests/test_017_001_suite_operations.py tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_017_001_suite_reconcile.py tests/test_017_001_suite_external.py tests/test_008_002_suite_evidence.py -q` → **48 passed en 62.95 s**.
- `python3 scripts/cdad-suite.py validate` → `status: ok`, **rc=0**.
- Corrida real sobre selección sana (2 nodeids de `test_003_002_*` que sí pasan instrumentados): `parallel --workers 2` → **rc=0**, pared_total=3.10 s, trabajo=2.94 s, solapamiento=1.34 s, consolidado passed=2/failed=0/skipped=0, canary_delta=0; `close` de los mismos nodeids → **rc=0**, `pytest_summary` passed=2/failed=0/skipped=0. **Pared/trabajo/solapamiento informados y equivalencia exacta.**
- Rechazos: `--workers 0` y `--workers 8` → `… fuera de rango … workers … (nproc=8)` por stderr, **rc=2** en ambos.
- `python3 -m py_compile scripts/cdad-suite.py` → OK.

## 4. Límites

- **Suite completa no realizada**: sin autorización para corrida completa; selección ejecutada: focal T6 + 7 archivos focales T1/T2/T3/external/008-002 (48 tests) + `validate` + 1 selección sana comparada parallel/close. Cierre de epic con completa obligatoria queda pendiente con su autorización.
- Evidencia de corridas de prueba en `tmp_path`/`/tmp` (fuera del repo); temporales de demo en `/tmp/pdbg /tmp/pdemo /tmp/cdbg*`, sin restos en el repo.

## 5. VEREDICTO: BLOCKED — conflicto test-vs-contrato (no edité tests, reporto)

La implementación satisface el contrato sobre selecciones sanas, pero **los 6 tests publicados no pueden pasar** por dos defectos del lado verificador, fuera de mi write_scope:

- **D1 — nodeid inexistente en el oráculo** (`tests/test_017_001_suite_parallel.py:38-39`): pide `…tranche2…_emit_branch_and_stays_neutral`, pero el test real es `test_real_tranche2_lookups_emit_branch_and_stay_neutral` (`tests/test_017_001_suite_tranche2.py:64`, "stay" sin s). Evidencia: `close` con esos nodeids → `ERROR: not found … (no match in any of [<Module test_017_001_suite_tranche2.py>])`, rc=4. Todo test del archivo que corre la selección falla desde la colección.
- **D2 — `assert not is_active()` incompatible con corridas instrumentadas** (`tranche1.py:34`, `tranche2.py:68`): `scripts/cdad_suite_observer.py:107-140` conecta su sumidero en `pytest_runtest_setup` y lo retira recién en `pytest_sessionfinish`, así que `is_active()` es True durante `call` bajo `close` **y** bajo cualquier worker que cargue el observador. Evidencia: `close` con solo el nodeid correcto de tranche1 → `assert not is_active()` → **rc=1** (intento `attempt-20261108T014929…`); el test pasa solo en pytest plano sin observador. Como el packet exige `close` intacto, la aserción de equivalencia serial-del-agregado (`_serial_counts` exige rc=0 de `close`) es inalcanzable sin decisión del test-writer/arquitecto. Cambiar el ciclo de vida del observador en `scripts/` excede el cambio mínimo y arriesga regresión T1/T2.

**Se solicita al orquestador:** re-ruta al test-writer (corregir D1; resolver D2 por decisión de contrato) y luego re-emite GREEN/review-fix sobre esta implementación ya comiteada (`10dfae99`).
