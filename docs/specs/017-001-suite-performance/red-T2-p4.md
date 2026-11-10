# FINAL TEXT — test-writer RED P4 contract-grounded (017-001-suite-performance, T2)

## Route C validation — PASS (before working)
- Dispatch identification block equals the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --project-root … --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json --request .cdad/packets/017-001-suite-performance-test-writer-red-007/REQUEST.json --route C` reproduces the prompt block exactly (`packet_id` 017-001-suite-performance-test-writer-red-007, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`).
- Full render byte-identical to `PACKET.md` (`diff` clean); `validate-request` and `validate-packet` both exit 0.
- Contract sha256 matches spec on disk (`sha256sum` → `472bab0c…192672e`).
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `red`, packet inputs/scopes only.

## Pre-RED (authorized sources only)
- Read: spec §4.2 + PC-1/INVs + §4.4 (recorrido no ejercitado ≠ fallo de captura), `operation-scope-mapping.md`, `green-T2-blocked.md` (6 protecciones T1 rotas por la regla P4 actual; dirección (a)+(b) recomendada), `performance/operation-scope.json` (registro real), `tests/test_017_001_suite_operations.py` (oráculo a corregir), `tests/suite_operation_markers.py` (costura neutra, sin cambios), T1 oracle pattern as black-box reference.
- Contribution: P4 revisada a forma contract-grounded y satisfacible — (A) alcance aplicado declara recorrido comprometido cuya selección incluye el nodeid ejecutado + cero operaciones capturadas → `incomplete` con diagnosis no vacía; (B) mismo hijo emitiendo marcas → operations no vacías + `complete`. El oráculo construye en su workspace un alcance sintético explícito (declara el nodeid sintético en recorrido comprometido `C-SYNTH`) y lo pasa por el argumento declarado `--operation-scope` (nuevo, default al registro del repositorio). Sin esto, P4 contradice spec §4.4 y las 6 protecciones T1 (R4-clean, skip-clean, 4× matrix-clean). P1/P2/P3 intactas.

## Corrección aplicada (solo `tests/`)
- `run_close()` gana parámetro `operation_scope`: cuando se da, agrega `--operation-scope <path>` al `close`. Sin el argumento en el CLI, el cierre falla con rc 2 (flag no reconocido) → AssertionError de promesa ausente, nunca ImportError/colección.
- Nuevo `write_synthetic_scope(workspace, nodeids)`: JSON con `mechanisms.explicit-synchronous-markers.transport=dedicated-logging-channel`, selección `C-SYNTH` con los nodeids ejecutados (`test_sample.py::test_pass`), familia `synthetic-committed-preparation` (`state=comprometida`, `classification=preparacion`, `context=test-call`, operación `synthetic.prepare`).
- P4 reescrita sobre el alcance sintético para (A) y (B); verifica que el sintético declara el recorrido comprometido e incluye el nodeid ejecutado antes de los cierres. Docstring D2 actualizado a D2-rev (spec §4.4). P1/P2/P3 sin modificar.

## Resultado RED
Exact command:
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py`
→ **3 failed, 1 passed**, all failures `AssertionError`, **zero ImportError / collection errors** (`--collect-only`: 4 tests, 0 errors):
1. P1 FAILED (`test_active_observer…`, line ~293) — perfil trae `operations: []`; `rc == 0` pasa (camino D1 viable).
2. P2 FAILED (`test_exceptional_exit…`, line ~342) — perfil sin operaciones; `rc != 0` pasa (fallo contractual se propaga).
3. P3 PASSED — control verde por diseño (neutralidad + viabilidad del camino).
4. P4 FAILED (`test_missing_markers…`, line ~421) — `assert rc == 0` con `assert 2 == 0`: el CLI rechaza `--operation-scope` (verificado: `close --help` no lista el flag; solo `--evidence-root/--capability/--nodeids/--all`). Es el fallo esperado de promesa ausente: el argumento y la regla no existen hoy. Tras GREEN, (A) debe dar `incomplete`+diagnosis y (B) `complete` con operations no vacías.

No temporal thresholds used as oracle (presencia/identidad/diagnóstico + rc contractual only).

## Evidencia del rol
- Implementation read: **none** (`scripts/`, observer, product code untouched; `close` usado solo como caja negra desde los tests autorizados; `close --help` como inspección de interfaz del CLI invocado por el oráculo, no lectura de implementación).
- Modified files: **one** — `tests/test_017_001_suite_operations.py` (+104/−25). Helper `tests/suite_operation_markers.py` sin cambios. `docs/.cdad-state.json` ya estaba modificado antes de empezar (transición del orquestador); intacto y sin commitear.
- Product diff outside `tests/`: **empty** (`git diff --name-only -- agents skills scripts sources build install.sh` → vacío).
- Full suite **not run** (focal cycle; belongs to GREEN/review).
- Commit: `eaeff429` (diff limitado a `tests/`, 1 file).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Cambio propuesto con disposición **Extender** (no materializada en inventario por este rol): `tests/test_017_001_suite_operations.py` —
  - `::test_active_observer_captures_intervals_with_identity_context_and_nesting` | capacidad T2-check-1 | contrato operation-markers-v1 (spec §4.2, PC-1 parte operaciones, INV-1/INV-8) | RED T2 corregido D1, sin cambios en este paquete (Mantener).
  - `::test_exceptional_exit_closes_interval_with_error_termination` | T2-check-2 | operation-markers-v1 (PC-1 parte, INV-2) | RED T2 corregido D1, sin cambios (Mantener).
  - `::test_without_observer_helper_is_neutral_and_leaves_no_evidence` | T2-check-3 | operation-markers-v1 (PC-1 parte, INV-2) | control verde, sin cambios (Mantener).
  - `::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` | T2-check-4 | operation-markers-v1 (PC-1 parte, INV-6/INV-8 + §4.4 ejercitado-vs-capturado) | RED T2 corregido D2-rev (Extender: alcance sintético explícito vía `--operation-scope`; (A) incomplete+diagnosis sobre recorrido ejercitado con captura cero; (B) complete con marcas).
- Soporte (no verificador, sin cambios): `tests/suite_operation_markers.py`.
- Existentes sin cambios: T1 (`test_017_001_suite_profile.py`, 17 protecciones) **Mantener**; 0 Sustituir/Consolidar/Retirar/Añadir.
- Nota para GREEN: implementar `--operation-scope` (default al registro del repositorio), referencia inequívoca al alcance aplicado en `profile.json`, y la regla acotada «alcance aplicado con recorrido comprometido que incluye un nodeid ejecutado + cero operaciones → incomplete con diagnosis; con marcas → complete»; con el alcance por defecto y selección que no ejercita recorridos comprometidos, el perfil queda `complete` (T1 conservado).
