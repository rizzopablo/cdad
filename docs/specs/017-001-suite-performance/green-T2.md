# FINAL TEXT — implementer GREEN T2 (017-001-suite-performance): GREEN, all focals green

## 1. Route C validation — PASS (before working)

- Dispatch carries only the identification block (no inline packet body → no route mixture): `packet_id` 017-001-suite-performance-implementer-green-003, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- `validate-request` and `validate-packet` (with `--execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json`) both exit 0; contract sha256 matches `sha256sum` of the spec on disk; execution context `schema_version=2` → v2, Route C admissible.
- Proceeded on Route C, substage `green`, packet inputs/scopes only. Full cycle skills not loaded. `tests/` read-only; `scripts/` only write scope.

## 2. Implementation (only `scripts/`, minimal, contract-grounded)

**`scripts/cdad_suite_observer.py`** (extended, phases behavior unchanged):
- On `pytest_sessionstart` + each runtest phase hook, attaches a `_TimedSink` to the seam `suite_operation_markers` (lazy import: top-level, then `tests.*`; retry after collection since the child dir may not be on `sys.path` at session start). Without `CDAD_SUITE_PHASE_SINK` or without the importable seam, it stays inert — marks remain neutral, no evidence written.
- Phase hookwrappers (`setup`/`call`/`teardown`) wrap execution in the seam's `use_context(nodeid, phase, owner_scope="test")`, so collected begin/end carry identity + test/shared context + nesting (`parent_id` from the helper).
- Each event is stamped with `time.monotonic()` at arrival; `pytest_sessionfinish` pairs begin/end per `interval_id` into operations (`operation, interval_id, parent_id, process_id, nodeid, phase, owner_scope, branch, started, finished, duration_s, termination`), then detaches. Unpaired/duplicate events become `operation_errors` (fail-loud, never silent). One real bug caught by the focal: the first draft cleared the sink before building operations (always `[]`); fixed to build-then-detach, verified by the focal going 3F/1P → 4/4.

**`scripts/cdad-suite.py`** (additive, T1 semantics conserved):
- `close` accepts `--operation-scope PATH`, defaulting to the CLI repo registry (`docs/specs/<feature>/performance/operation-scope.json` resolved from the CLI location, not the cwd).
- `profile.json` now carries `operations` (observed intervals), `operation_errors`, and `operation_scope: {path, sha256, status}` — the unequivocal applied-scope reference. New keys only; no existing field renamed or reinterpreted.
- Bounded diagnostic rule (§4.4): zero captured operations → `incomplete` + non-empty diagnosis **only** when the applied scope declares a committed (`state`, default `comprometida`) family whose explicit selection nodeids include an executed nodeid. Selections without nodeid lists (`all-required-selections`) and families without selection never match — a non-exercised recorrido is not a capture failure, so T1's synthetic selections stay `complete`. With captured marks, the T1 phase-integrity rules decide alone. Unreadable scope → `incomplete` with diagnosis, rc always preserved.

## 3. Evidence (exact commands, outputs kept)

- T2 focal: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_operations.py` → **4 passed in 4.52s** (P1 identity/context/nesting + integration capture, P2 error-termination + rc≠0, P3 neutral control, P4A incomplete+diagnosis on exercised-committed zero-capture / P4B complete with operations).
- T1 focal (17 protections): same invocation over `tests/test_017_001_suite_profile.py` → **17 passed in 22.11s**.
- Proportional regression (shared `close` path: evidence, gate): `tests/test_008_002_suite_evidence.py tests/test_008_005_ci_gate.py` → **24 passed in 29.03s**.
- `python3 scripts/cdad-suite.py validate` → rc 0 (`status: ok`).
- **Suite completa no realizada** (focal cycle + proportional regression as routine; no authorization claimed for a complete run).

## 4. Role evidence summary

- Modified files: `scripts/cdad_suite_observer.py`, `scripts/cdad-suite.py`. Commit: `613b3722` (`feat: implement T2 operation markers capture and bounded capture diagnosis`, 2 files, +360/−19).
- `tests/` untouched (verified: `git diff --name-only -- tests/` empty); contract untouched; orchestrator's pre-existing `docs/.cdad-state.json` transition left uncommitted by me.
- Quality gates: guard clauses throughout; scope/operations validated at the boundary (`load_operation_scope`, shape-checked readers); atomic JSON writes unchanged; capture failures diagnose loud as `incomplete`, never zero-filled; rc contractual never substituted.
