# FINAL TEXT — test-writer RED correction D1/D2 (017-001-suite-performance)

## Route C validation — PASS (before working)
- Identification block in the dispatch equals packet metadata: `packet_id` 017-001-suite-performance-test-writer-red-006, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e` — all match `REQUEST.json`.
- `scripts/cdad_packet.py render --request …` output byte-identical to `PACKET.md` (`diff` exit 0); contract sha256 matches spec on disk.
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture.
- Proceeded on Route C, substage `red`, inputs/scopes of the packet only. Full cycle skills not loaded.

## Pre-RED (authorized sources only)
- Read: spec §4.2 + PCs/INVs, `operation-scope-mapping.md` (§2 mechanism explicit-synchronous-markers, §4 scope draft), `red-T2-markers.md` (baseline: 4 failed on `operations: []`), `performance/operation-scope.json` (8 committed families, waits unknown), `tests/suite_operation_markers.py` (neutral seam, unchanged), `tests/test_017_001_suite_operations.py` (oracle to correct), T1 oracle as black-box `close` pattern reference.
- Confirmed both defects: (D1) P1-2nd-half/P2/P4 closed over a synthetic child that never imports the helper, then demanded non-empty `operations` — unsatisfiable by construction; (D2) P4 demanded non-empty `operations` while its promise is incomplete+diagnosis on zero capture. P3's close half had the same D1 shape (plain child demanding non-empty ops).
- Contribution: corrected oracle, 4 tests P1–P4 kept (one per promise, traced to PC-1 operations part, INV-1/INV-2/INV-6/INV-8); without the correction the user either calibrates on fiction or waits on an oracle GREEN can never satisfy.

## Corrección aplicada (solo `tests/`)
- `install_helper()` + `write_sample()`: the helper is copied into the synthetic workspace so the child imports marks locally and the child's observer can attach its sink on the same copy (D1 satisfiable path, no implementation API presumed).
- P1 2nd half: child emits nested marks (`u4.lookup` > `u4.copy` + `u4.initial-generate`) → demands `operations` non-empty + scope reference.
- P2 2nd half: child emits a mark and fails inside it → demands `rc != 0` (contractual failure preserved) + `operations` non-empty (error interval capturable via existing `finally`).
- P3: in-process neutrality kept; close half repurposed as integration-path control (rc 0, `operations` is a list — neither presence nor absence demanded, since post-GREEN the session observer captures whatever is emitted).
- P4 (D2 direction fix): (A) mark-less child + scope requiring ops → `status == "incomplete"` + non-empty string `diagnosis` + `operations` list (may be empty); (B) contrast with emitting child → `operations` non-empty + `status == "complete"` + falsy diagnosis.

## Resultado RED
Exact command:
`python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py`
→ **3 failed, 1 passed in ~3.6s**, all failures `AssertionError` de promesa ausente, **zero ImportError / collection errors** (`--collect-only`: 4 tests, 0 errors):
1. P1 FAILED (line 235) — profile brings `operations: []`, no identity intervals to calibrate on. Its `rc == 0` passes, proving the child imports the copied helper cleanly (D1 path viable).
2. P2 FAILED (line 284) — profile brings no operations; `rc != 0` passes, proving the failing emitting child collects and the contractual failure propagates (D1 path viable, failure is on pending capture).
3. P3 PASSED — control: helper neutral in-process, integration path viable (rc 0, `operations` shape kept). Honest note: P3 verifies a helper property needing no implementer, so it is green before GREEN by design; it guards the pattern P1/P2/P4B rely on.
4. P4 FAILED (line 349) — clean mark-less close measures `status complete` while scope commits 8 families and zero were captured; must be `incomplete` with diagnosis (D2 corrected direction).

No temporal thresholds used as oracle (presence/identity/diagnosis only).

## Evidencia del rol
- Implementation read: **none** (`scripts/cdad-suite.py`, observer, product code untouched; `close` used only as black-box CLI from authorized tests; phase isolation preserved).
- Modified files: **one** — `tests/test_017_001_suite_operations.py` (+131/−21). Helper unchanged. `docs/.cdad-state.json` was already modified before starting; untouched and uncommitted. `red-T2-markers.md` input untouched.
- Full suite **not run** (focal cycle; belongs to GREEN/review).
- Commit: `ede4e5af` (diff limited to `tests/`, 1 file).

## Delta de inventario vivo (texto, para materializar por el orquestador)
- Cambio propuesto con disposición **Extender** (no materializada en inventario por este rol): `tests/test_017_001_suite_operations.py` —
  - `::test_active_observer_captures_intervals_with_identity_context_and_nesting` | capacidad T2-check-1 | contrato operation-markers-v1 (spec §4.2, PC-1 parte operaciones, INV-1/INV-8) | RED T2 corregido D1 (hijo emite con helper copiado).
  - `::test_exceptional_exit_clo<session>_with_error_termination` | T2-check-2 | operation-markers-v1 (PC-1 parte, INV-2) | RED T2 corregido D1 (hijo emite y falla, rc != 0 + captura).
  - `::test_without_observer_helper_is_neutral_and_leaves_no_evidence` | T2-check-3 | operation-markers-v1 (PC-1 parte, INV-2) | RED T2 corregido D1 (control verde: neutralidad en proceso + viabilidad del camino).
  - `::test_missing_markers_capture_is_diagnosed_as_incomplete_measurement` | T2-check-4 | operation-markers-v1 (PC-1 parte, INV-6/INV-8) | RED T2 corregido D2 (incomplete+diagnosis en vacío; complete en contraste).
- Soporte (no verificador, sin cambios): `tests/suite_operation_markers.py`.
- Existentes sin cambios: T1 (`test_017_001_suite_profile.py`) **Mantener**; 0 Sustituir/Consolidar/Retirar.
- Nota para GREEN: el oráculo exige la regla simple «alcance con familias comprometidas + cero operaciones capturadas → incomplete con diagnosis; con marcas capturadas → complete»; el implementer debe materializar ese contraste de alcance en `profile.json`.
