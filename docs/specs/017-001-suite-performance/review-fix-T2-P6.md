Route C review-fix complete. Role report:

## Route C validation — PASS (before working)
- Dispatch identification matches `REQUEST.json` (`packet_id` 017-001-suite-performance-implementer-review-fix-005, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`, `execution_context` path identical).
- Full canonical render `diff` vs `PACKET.md` → **identical** (`python3 scripts/cdad_packet.py render --request … --execution-context …` exit 0).
- Contract sha256 matches spec on disk (`sha256sum` → `472bab0c…192672e`).
- Execution context `schema_version=2` → v2, Route C admissible. No inline packet body → no route mixture. Full cycle skills not loaded.
- Proceeded on Route C, substage `review-fix`, packet inputs/scopes only.

## Finding verification (against original evidence)
- `red-T2-p6.md` RED: ambiguous child importing `tests.suite_operation_markers` closed rc=0 but profile had `operations: []` — capture loss, not collection failure. Confirmed in code: `_ensure_markers`/`_ensure_ops_attached` imported the **first** importable helper (`suite_operation_markers` bare) and attached the sink only there, while the child emitted via the distinct `tests.suite_operation_markers` module object. A second, subtler loss: `_phase_context` set ContextVars only on that same single instance, so nodeid/phase context would not reach marks emitted via the other instance (each module object owns its own ContextVars).

## Change applied (only `scripts/`, tests/ untouched)
- `scripts/cdad_suite_observer.py` (+99/−34, commit `cb8f2fe6`):
  - New `_discover_markers()` returning **all** distinct importable helper instances (bare + qualified, identity-deduped); `_ensure_markers()` kept as first-instance compat shim.
  - `_ensure_ops_attached()` now attaches **one shared `_TimedSink`** to every discovered instance, retrying each phase (late-importable instances get connected; already-connected ones are skipped, never re-attached).
  - `_phase_context()` now enters `use_context(...)` on **all** connected instances (ExitStack), so ambient nodeid/phase/owner_scope reaches the child regardless of which instance it imports.
  - `_build_operations()` silently dedupes byte-identical events (fingerprint via `json.dumps(sort_keys)`) arriving via two channels instead of converting them into `operation_errors` (any `operation_errors` forces `incomplete` in `build_profile`, so a duplicate-as-error would break P6-A's `complete`).
  - `pytest_sessionfinish()` detaches from **all** instances and clears the list; sink-absent neutrality, per-session close, and fail-loud stderr+`_OP_ERRORS` diagnostics preserved.

## Test evidence (exact commands, all with `-o addopts= -p no:cacheprovider`)
- `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs … tests/test_017_001_suite_operations.py::test_ambiguous_helper_import_still_captures_operations` → **1 passed in 1.87s** (P6 A+B green).
- `… tests/test_017_001_suite_operations.py` → **6 passed in 10.57s** (P1–P5 intact, P6 fixed).
- `… tests/test_017_001_suite_profile.py` → **17 passed in 22.60s** (all T1 green).
- Proportional regression `… tests/test_008_002_suite_evidence.py` → **5 passed in 5.22s** (close semantics preserved).
- `make validate` → **182 PASS / 1 FAIL**; the single FAIL is `F011: install.sh --check` drift on `skills/odoo-expert` in `~/.config` — verified **identical (182/1) on pristine HEAD** via `git stash push/pop`, i.e. preexisting/environmental and unrelated to this change.

## Role evidence
- Modified files: **one** — `scripts/cdad_suite_observer.py`. `tests/` and contract untouched. `docs/.cdad-state.json` was already modified before starting (per RED report); left uncommitted and un-staged.
- Full suite **not run** (focal cycle + proportional regression as routine; suite completa no realizada — selection: T2 focal file, T1 focal file, `test_008_002_suite_evidence.py` regression, `validate`; limits: no complete-suite run consumed).
- Commit: `cb8f2fe6` (`fix(017-001-T2): observer attaches sink to all helper instances with cross-channel dedup`, 1 file).

## FINAL TEXT
Review-fix T2 P6 aplicado en `scripts/cdad_suite_observer.py`: el sumidero compartido se adjunta a todas las instancias importables del helper (bare y `tests.` paquete) con reintento por fase, el contexto de fase se fija en todas, y las marcas duplicadas entre canales se conservan una sola vez sin error. P6 pasa en sus dos casos; P1–P5, las diecisiete de T1 y la regresión `008_002` siguen verdes. `validate` mantiene su único fallo preexistente ambiental (drift `install.sh --check`, idéntico en HEAD limpio). Commit `cb8f2fe6`.
