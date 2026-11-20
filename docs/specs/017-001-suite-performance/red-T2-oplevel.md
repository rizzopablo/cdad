# FINAL TEXT — test-writer RED P5 operation-level selection (017-001-suite-performance, T2 hallazgo 2)

## Route C validation — PASS (before working)
- Dispatch identification block equals the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-test-writer-red-008/REQUEST.json --route C` reproduces the prompt block exactly (`packet_id` 017-001-suite-performance-test-writer-red-008, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`).
- `validate-request` and `validate-packet` both exit 0.
- Contract sha256 matches spec on disk (`sha256sum` → `472bab0c…192672e`).
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `red`, packet inputs/scopes only.

## Pre-RED (authorized sources only)
- Read: spec §4.2 + PC-1/INVs + §4.4 (recorrido no ejercitado ≠ fallo de captura), `review-T2.md` hallazgo 2 (regla solo consulta `family["selection"]`, omite selecciones por operación; caso real `u3-disposable-product` sin selección de familia + operación `u3.contract-staging` con `selection: C-U3`), `performance/operation-scope.json` (familia sin `selection`, operación con `selection: C-U3` verificada), `red-T2-p4.md` (P4 existente y alcance sintético vía `--operation-scope`), `tests/test_017_001_suite_operations.py` (oráculo a extender).
- Contribution: P5 nueva y contract-grounded — (A) familia sin selección + operación con selección que incluye el nodeid ejecutado + cero operaciones capturadas → `incomplete` con diagnosis no vacía; (B) operación sin selección → `complete`; (C) selección de operación que no incluye el nodeid ejecutado → `complete`. El oráculo construye en su workspace alcances sintéticos explícitos y los pasa por el argumento declarado `--operation-scope` (existente, default al registro del repositorio). Sin esto, un nodeid de `C-U3` sin captura queda `complete` y la ausencia de captura se confunde con medición válida. P1/P2/P3/P4 intactas.

## Corrección aplicada (solo `tests/`)
- Nuevo `write_synthetic_op_scope(workspace, executed_nodeids, ...)`: JSON con `mechanisms.explicit-synchronous-markers.transport=dedicated-logging-channel`, familia `synthetic-op-selection` (`state=comprometida`, sin `selection`), operación `synthetic.op-prepare` con `selection` parametrizable; selección con los nodeids dados.
- Nueva P5 `test_operation_level_selection_is_diagnosed_as_incomplete_measurement`: verifica que el sintético declara familia sin selección + operación con selección incluyendo el nodeid ejecutado antes de los cierres; (A) hijo sin marcas → `incomplete`+diagnosis; (B) alcance sin selección de operación → `complete`; (C) alcance con selección ajena → `complete`. Docstring con consecuencia «sin este test…». Cero modificaciones a P1–P4.
- Sin umbrales temporales como oráculo (presencia/identidad/diagnóstico + rc contractual only).

## Resultado RED
Exact commands:
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **5 tests collected, 0 errors**.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py::test_operation_level_selection_is_diagnosed_as_incomplete_measurement` → **1 failed in 1.25s**, `AssertionError` en (A): `assert 'complete' == 'incomplete'` (hoy devuelve `complete`), `rc == 0` pasa (el CLI acepta `--operation-scope`; camino viable), **zero ImportError / collection errors**.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **1 failed, 4 passed in 5.70s**: P1/P2/P3/P4 pasan intactas; solo P5 falla por la aserción de promesa ausente. Tras GREEN, (A) debe dar `incomplete`+diagnosis y (B)/(C) `complete`.

## Evidencia del rol
- Implementation read: **none** (`scripts/`, observer, product code untouched; `close` usado solo como caja negra desde los tests autorizados).
- Modified files: **one** — `tests/test_017_001_suite_operations.py` (+162/−0, solo adición). `docs/.cdad-state.json` ya estaba modificado antes de empezar (transición del orquestador); intacto y sin commitear.
- Product diff outside `tests/`: **empty** (`git diff --name-only -- agents skills scripts sources build install.sh` → vacío).
- Full suite **not run** (focal cycle; belongs to GREEN/review).
- Commit: `1bea623e` (diff limitado a `tests/`, 1 file).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Cambio propuesto con disposición **Añadir** (no materializada en inventario por este rol): `tests/test_017_001_suite_operations.py` —
  - `::test_operation_level_selection_is_diagnosed_as_incomplete_measurement` | capacidad T2-check-5 | contrato operation-markers-v1 (spec §4.2, PC-1 parte operaciones, INV-6/INV-8 + §4.4 ejercitado-vs-capturado; review-T2 hallazgo 2) | RED T2 corrección hallazgo 2 (Añadir: familia sin selección + operación con selección aplicable → incomplete+diagnosis ante captura cero; contrastes sin selección o con selección ajena → complete).
  - Soporte nuevo (no verificador): `write_synthetic_op_scope` (constructor de alcances sintéticos con selección a nivel de operación).
- Existentes sin cambios: P1 `::test_active_observer_captures_intervals_with_identity_context_and_nesting` **Mantener**; P2 `::test_exceptional_exit_closes_interval_with_error_termination` **Mantener**; P3 `::test_without_observer_helper_is_neutral_and_leaves_no_evidence` **Mantener**; P4 `::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` **Mantener**; T1 (`test_017_001_suite_profile.py`, 17 protecciones) **Mantener**; 0 Sustituir/Consolidar/Retirar.
- Nota para GREEN: resolver las selecciones aplicables también a nivel de operación (respetando estados y la regla acotada «alcance aplicado con recorrido comprometido que incluye un nodeid ejecutado + cero operaciones → incomplete con diagnosis; con marcas → complete»); con el alcance por defecto y selección que no ejercita recorridos comprometidos, el perfil queda `complete` (T1 conservado).
