RED de U6-5 entregado. Reporte del rol:

## 1. Archivo modificado (único)

- **Nuevo:** `tests/test_006_005_u6fix5_write_ahead.py` (1771 líneas, 11 tests de proceso).
- Commit (solo `tests/`): `a0d96b52fee31a3c0da31b499128b11ec44e3cdc` — `test: 006-005 U6-5 RED — registro write-ahead del intento externo`.
- Sin cambios fuera de `tests/`: quedan sin trackear los preexistentes `docs/planning/` y `findings/…` (no son míos). Sin `--no-verify`, sin stash, sin push.

## 2. Mapa test → oráculo/PD

| Test | Oráculo | Postcondición / decisión |
|---|---|---|
| `test_u65_crash_midrun_recovers_through_disposition` | 1 | E4, PD-19 (a)-(d), PD-1, PD-22, D-U65-1/2/3, **O-4** |
| `test_u65_crash_before_launch_recovers_through_disposition` | 2 | E4, PD-19, D-U65-1/2, O-3(ii) |
| `test_u65_redispatch_with_live_session_is_blocked_without_run` | 3 | E4, PD-19 (d), PD-9 (006-001/INV-10), D-U65-3.4 |
| `test_u65_completed_leaves_one_final_record_with_pd3_pairs` | 4 | PD-1, 006-001 PD-3, D-U65-2, D-ADP-2 (cierre B-1) |
| `test_u65_binary_that_does_not_start_completes_with_null_session` | 5a | 006-001 PD-8, D-U65-2 (cierre B-3) |
| `test_u65_timeout_without_row_keeps_the_termination_provenance` | 5b | 006-001 PD-3/PD-8, D-U65-2 |
| `test_u65_write_ahead_failure_does_not_launch_the_client` | 6 | PD-19, D-U65-1 fail-closed (cierre B-2), PD-1 |
| `test_u65_second_completion_with_different_data_is_rejected` | 7a | ledger write-once + D-U65-2 |
| `test_u65_completion_over_an_unmarked_record_is_rejected` | 7b | D-U65-2 |
| `test_u65_completion_changing_the_identity_is_rejected` | 7c | D-U65-2 |
| `test_u65_termination_before_write_ahead_is_not_provisional` | 8 | D-U65-1 última viñeta, 006-001 PD-9, PD-1 |

El oráculo 1 asserta además la forma O-4: `provenance.session` empieza con `write-ahead:`, y termina en `row=unknown; store_reads=unknown; prior_check_reads=<n>`, con `model_reported: null` y `session` = la elegida.

## 3. RED: falla por la razón correcta

`python3 -m pytest tests/test_006_005_u6fix5_write_ahead.py -q` → **5 failed, 6 passed** (14–18 s, estable en dos corridas).

Fallos declarados, todos `AssertionError` de comportamiento ausente (nunca Import/Syntax/fixture):

1. **Oráculo 1:** `0 != 1` — «con el cliente VIVO debe existir el registro I8 write-ahead… se encontraron 0 registros».
2. **Oráculo 2:** «el cliente arrancó SIN el registro I8 write-ahead… no hay provisional en disco».
3. **Oráculo 3:** `0 != 1` — «el registro write-ahead debe existir con el cliente vivo; hay []».
4. **Oráculo 6:** `1 != 0` — «con el write-ahead fallido el cliente NO se lanza; invocaciones: [run --agent … --session …]». Hoy la falla de registro agrega la nota «worker record not written» y **lanza igual**.
5. **Oráculo 7a:** `2 != 0` — la primera compleción sobre un registro con la marca se rechaza hoy: «already exists with different observation data».

Guards declarados y **GREEN hoy** (deben seguir verdes tras el fix): 4, 5a, 5b, 7b, 7c, 8.

## 4. A-1: sin reformulaciones, con razón

No se reescribió ningún test existente:

- **`tests/test_006_001_t2_wait_recovery.py:865-871,1136-1141`** (store_reads exacto del registro final): **sigue valiendo**. El cierre B-1 de la re-review exige que la compleción reemplace todos los pares PD-3, así que el registro final queda byte-idéntico al de hoy. Es la regresión O-5 y pasa: **12 passed**.
- **Ledger «different observation data»** (`tests/test_004_002_t4_dispatch.py`, `test_pd6_i8_reused_attempt_id_with_conflicting_data_rejected` y el idempotente): usan registros **sin** la marca `write-ahead:`; la compleción única está condicionada a la marca, así que write-once queda igual.
- **D-5 «a registration failure never changes the termination»**: ningún test de la suite la fija (grep sobre `tests/` sin coincidencias); el fail-closed del oráculo 6 es comportamiento nuevo, no un reemplazo.
- Tests que cuentan un registro tras `completed` (`test_005_010_t1_durable_signal.py:435` y hermanos): válidos, la compleción **reemplaza** (PD-1).
- Nota declarada en el docstring: una repetición **byte-idéntica** de la compleción sigue siendo el no-op write-once existente (FYI de la re-review); el oráculo 7a aserta el rechazo de una segunda compleción **con datos distintos**, que es la regla declarada.

## 5. Regresiones ejecutadas

- `pytest tests/test_006_005_u1a_runtime_config.py tests/test_006_005_u1b_dispatch_entry.py tests/test_006_005_u1c_packet_agent.py -q` → **41 passed** (115 s).
- `pytest tests/test_006_005_u2_opencode_module.py tests/test_006_005_u3_temporary_scope.py tests/test_006_005_u3b_derived_temporary_permission.py -q` → **33 passed** (47 s).
- `pytest tests/test_006_005_u4_single_entry.py tests/test_006_005_u5_disposition_failed.py tests/test_006_005_u6fix1_capabilities_entry.py tests/test_006_005_u6fix4_native_selection.py tests/test_006_005_u7_scribe_role_report.py -q` → **31 passed** (75 s).
- `pytest tests/test_006_001_t2_wait_recovery.py -q` → **12 passed** (24 s).

No se corrió la suite completa (política de suite completa: la corre quien cierra).

## 6. Aislamiento y límites honestos

- No leí ni importé implementación (`skills/**/scripts/*.py`, módulo incluido). El módulo **real** se resuelve por la sección `opencode` de `runtimes.json` bajo `XDG_CONFIG_HOME`/`HOME` temporales; el binario es un fake que duerme/escribe fila/falla; el store es SQLite descartable con la forma real de V-7 (`time_created INTEGER` en ms). La caída se provoca con `SIGKILL` al grupo del coordinador; medí que el cliente del fake sobrevive en su propio grupo (premisa E4).
- Sin valores del host: nunca el store, la config ni el runtime reales.
- **Límite declarado (oráculo 2):** el instante exacto entre el write-ahead y `Popen` no se instrumenta sin leer implementación. El test mata al coordinador apenas aparece un registro provisional parseable y el cliente de esa variante no escribe fila ni efecto; el estado material asertado (registro presente, sin fila, sin efectos, mismo camino de recuperación) es el de la caída pre-lanzamiento. Está declarado en el docstring del test, sin afirmar un timestamp medido.