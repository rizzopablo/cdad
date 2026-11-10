# FINAL TEXT — test-writer RED (Route C, 017-001 T1 tercera vuelta, matriz de integridad de fases)

## Route C validation — PASS (before working)

- Identification block in the dispatch equals canonical `render --route C` output (byte-identical, verified).
- `validate-request` → rc=0. `validate-packet` → rc=0.
- `packet_id`, `execution_id`, contract `path`+`sha256` match `REQUEST.json`; contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk.
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Proceeded on Route C, substage `red`, inputs/scopes of the packet only.

## Objective executed

RED de corrección de T1, tercera vuelta tras `review-T1-003.md` (BLOCKING: call ejecutada y perdida se declara completa cuando setup pasó). Agregada a `tests/test_017_001_suite_profile.py` **una protección parametrizada (8 casos), sin modificar las nueve existentes** (R1–R5 + H1 + H2 + skip-rama + H3 intactas; diff `206+/0-` solo aditivo), trazada a review-T1-003 (+ review-T1-002) + spec §§4.2–4.3 / PC-2 / INV-6, por medio externo (sombra del observador que descarta una fase concreta, patrón reutilizado de los tests H1/skip-rama autorizados, no de implementación). Oráculo solo desde contrato/review/tests autorizados; no se leyó `scripts/cdad-suite.py` ni el observador.

## Modified files

- `tests/test_017_001_suite_profile.py` (+206/−0; ninguna de las 9 existentes tocada).
- Commit: `9d194644` — `017-001 T1 RED tercera vuelta: matriz de integridad de fases por origen de skip/fallo (call perdida falla por promesa ausente)` (1 file, 206 insertions).
- `docs/.cdad-state.json` aparece `M` preexistente al inicio del turno; no tocado ni commiteado por este rol (write_scope `tests`).

## Test added (promesa observable, con consecuencia)

- `test_matrix_phase_loss_is_incomplete_while_clean_stays_complete[8 casos]` (review-T1-003 → PC-2/INV-6, §§4.2–4.3). Regla observable: la exención de call depende del resultado de setup (setup skipped/failed no ejecutan call; setup passed sí), y toda fase esperable debe estar presente. Matriz: (1) skip en setup → drop teardown; (2) skip en call con setup passed → drop call; (3) skip en teardown → drop teardown; (4) fallo de setup → drop teardown; cada origen con su contrapeso limpio (complete + diagnosis vacía + rc intacto). *Sin este test, el usuario consume una medición parcial con una fase emitida perdida creyéndola íntegra; sin los contrapesos, una corrección futura podría marcar skips/fallos limpios como incompletos y bloquear la base.*

## Exact commands + outputs (RED)

- Focal RED: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **`1 failed, 16 passed in 20.57s`**. Las 9 existentes pasan sin modificación.
- Resumen por caso (matriz, 7 passed + 1 failed):
  - `setup-skip-clean` PASSED · `setup-skip-drop-teardown` PASSED (ya cerrada por la vuelta anterior)
  - `call-skip-clean` PASSED · **`call-skip-drop-call` FAILED** — `AssertionError: … se declaro 'complete'; debe ser incomplete` (`assert 'complete' == 'incomplete'`, línea 849; setup passed + teardown presentes, call perdida, XML con skip). Reproduce en ejecución el hallazgo BLOCKING de review-T1-003.
  - `teardown-skip-clean` PASSED · `teardown-skip-drop-teardown` PASSED (ya incompleta: la rama exige setup+teardown)
  - `setup-failed-clean` PASSED (setup failed + teardown → complete, rc≠0 intacto) · `setup-failed-drop-teardown` PASSED (ya incompleta)
- Hallazgo honesto: de las 4 pérdidas, solo la de call-con-setup-pasado falla hoy; las 3 pérdidas de teardown ya quedan `incomplete` por las correcciones previas y quedan como protección contra regresión. El fallo es de promesa ausente (`AssertionError`), nunca `ImportError` ni error de colección.
- Suite completa **no realizada** (ciclo focal; sin autorización para completa). Regresiones T1 no re-ejecutadas en RED (ningún archivo suyo tocado; corresponden al GREEN; no se ejecuta `cdad-ci-gate.py` como comprobación rutinaria de T1 por plan del paquete).

## Delta de inventario vivo (como texto, para materializar por el orquestador)

> En RED no hay altas materializadas; propuesta con disposición prevista **Añadir** (las 9 existentes quedan **Mantener** exactamente):
> - Añadir `tests/test_017_001_suite_profile.py::test_matrix_phase_loss_is_incomplete_while_clean_stays_complete` (8 casos; review-T1-003 → PC-2/INV-6, §§4.2–4.3).
> - Mantener las 9 existentes sin cambio (R1–R5 + H1 + H2 + skip-rama + H3). Incertidumbre: ninguna que obligue a conservar de más.

## Evidencia del rol / honestidad

- Implementación leída: **ninguna** (aislamiento preservado). Solo spec/review-T1-003/review-T1-002/red-T1-skip/tests. La sombra del observador reutiliza el patrón (nombre de archivo, variable `CDAD_SUITE_PHASE_SINK`, esquema del payload) de los tests H1/skip-rama autorizados.
- Diff limitado a `tests/` (1 archivo, +206/−0). Sin lecturas fuera de `docs/specs/017-001-suite-performance` + `tests/`. Sin edición fuera de `tests/`.
