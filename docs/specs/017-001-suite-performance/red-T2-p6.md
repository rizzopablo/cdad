Route C RED complete. Role report:

## Route C validation — PASS (before working)
- Dispatch identification block equals the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --request .cdad/packets/017-001-suite-performance-test-writer-red-011/REQUEST.json --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json --route C` reproduces the prompt block exactly (`packet_id` 017-001-suite-performance-test-writer-red-011, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`).
- Full canonical render `diff` vs `PACKET.md` → identical (8937 bytes, exit 0); contract sha256 matches spec on disk (`sha256sum` → `472bab0c…192672e`).
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `red`, packet inputs/scopes only.

## Pre-RED (authorized sources only)
- Read: spec §4.2 + PC-1/INVs + §4.4, `red-T2-markers-fix.md` (D1/D2 correction, P1–P4), `red-T2-oplevel.md` (P5 op-level selection), `tests/test_017_001_suite_operations.py` (oracle to extend, 5 tests), `tests/suite_operation_markers.py` (seam, unchanged).
- Contribution: P6 is new and contract-grounded — synthetic workspace reproducing the real-calibration defect (helper at workspace root AND under `tests/` as package, child importing `tests.suite_operation_markers`) must yield non-empty `operations` on `close`; the mark-less contrast on the same layout must still diagnose `incomplete`+diagnosis. Traced to PC-1 (operations part), INV-1/INV-6/INV-8. Without it, the user consumes a phases-only profile over a run that did emit marks — loss by dual instance, not by missing marks — and no contrast separates lost marks from never-emitted ones. P1–P5 intact (zero deletions).
- Self-correction during work: my first edit landed mid-file replacing P5's header comment; I reverted (`git checkout -- tests/…`, back to 5 collected) and re-applied P6 as a pure end-of-file append. Final diff: +134/−0.

## Change applied (only `tests/`)
- New `AMBIGUOUS_SAMPLE` (emits `u4.lookup` > `u4.copy` via `tests.suite_operation_markers`) + `AMBIGUOUS_PLAIN` (clean body, same layout).
- New `install_ambiguous_layout` (root bare copy via untouched `install_helper` + `tests/__init__.py` + package copy) and `run_close_nodeids` (full-nodeid selection; `run_close` untouched).
- New P6 `test_ambiguous_helper_import_still_captures_operations`: (A) emitting ambiguous child + synthetic family scope covering `tests/test_ambiguous.py::test_amb` → `rc==0`, `operations` non-empty, `complete` without diagnosis; (B) same layout mark-less → `incomplete` + non-empty diagnosis + list-shaped `operations`.
- No temporal thresholds as oracle (presence/identity/diagnosis + contractual rc only).

## RED result
Exact commands:
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **6 tests collected, 0 errors**.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py::test_ambiguous_helper_import_still_captures_operations` → **1 failed in 1.39s**, `AssertionError` at line 724: `assert (True and [])` — profile brings `operations: []` though the child emitted marks. Its `rc == 0` passes, proving the ambiguous child imports `tests.suite_operation_markers` cleanly (path viable, defect is capture, not collection).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **1 failed, 5 passed in 10.27s**: P1/P2/P3/P4/P5 pass intact; only P6 fails on the missing-promise assertion. **Zero ImportError / collection errors** throughout.

## Role evidence
- Implementation read: **none** (`scripts/`, observer, product code untouched; `close` used only as black-box CLI from authorized tests; phase isolation preserved).
- Modified files: **one** — `tests/test_017_001_suite_operations.py` (+134/−0). Helper unchanged. `docs/.cdad-state.json` was already modified before starting; untouched and uncommitted.
- Product diff outside `tests/`: **empty**.
- Full suite **not run** (focal cycle; belongs to GREEN/review — suite completa no realizada, selection: focal file only).
- Commit: `ac3b7edf` (diff limited to `tests/`, 1 file).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Cambio propuesto con disposición **Añadir** (no materializada en inventario por este rol): `tests/test_017_001_suite_operations.py` —
  - `::test_ambiguous_helper_import_still_captures_operations` | capacidad T2-check-6 | contrato operation-markers-v1 (spec §4.2, PC-1 parte operaciones, INV-1/INV-6/INV-8) | RED T2 defecto calibración real dual-instancia (Añadir: layout ambiguo bare+paquete con hijo que importa tests.suite_operation_markers → operations no vacías + complete; contraste sin marcas → incomplete+diagnosis).
  - Soporte nuevo (no verificadores): `install_ambiguous_layout`, `run_close_nodeids`, `AMBIGUOUS_SAMPLE`, `AMBIGUOUS_PLAIN`.
- Existentes sin cambios: P1 `::test_active_observer_captures_intervals_with_identity_context_and_nesting` **Mantener**; P2 `::test_exceptional_exit_closes_interval_with_error_termination` **Mantener**; P3 `::test_without_observer_helper_is_neutral_and_leaves_no_evidence` **Mantener**; P4 `::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` **Mantener**; P5 `::test_operation_level_selection_is_diagnosed_as_incomplete_measurement` **Mantener**; T1 (`test_017_001_suite_profile.py`) **Mantener**; 0 Sustituir/Consolidar/Retirar.
- Nota para GREEN: una sola instancia compartida del helper entre observador e hijo ambiguo (el sumidero debe alcanzar las marcas emitidas vía `tests.suite_operation_markers`); el contraste sin marcas conserva la regla §4.4 ya verde (alcance aplicado con recorrido comprometido ejercitado + cero operaciones → incomplete con diagnosis).
