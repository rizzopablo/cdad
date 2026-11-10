# FINAL TEXT — implementer GREEN T4 (017-001-suite-performance): GREEN, focal + regresión + base real

## 1. Route C validation — PASS (before working)

- Dispatch carries only the identification block (no `---cdad-packet-json` markers → no route mixture): `packet_id` 017-001-suite-performance-implementer-green-005, `execution_id` exec-017-001-suite-performance-001, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e`.
- `python3 scripts/cdad_packet.py validate-request --project-root <repo> --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json --request .cdad/packets/017-001-suite-performance-implementer-green-005/REQUEST.json` → exit 0.
- `validate-packet` (same + `--packet …/PACKET.md`) → exit 0.
- `render --request … --route C` emits exactly the dispatched JSON (header + json block byte-for-byte).
- Contract sha256 matches `sha256sum` of spec on disk (`472bab0c942268956484d55edec8d24934105dab29a2c86effdcbf82e192672e`). Execution context `schema_version: 2` → v2, Route C admissible.
- Worked on Route C, substage `green`, only declared inputs/scopes. No `cdad-cycle`/spec skills loaded. `tests/` read-only; write scope `scripts/` only.

## 2. Implementation (only `scripts/cdad-suite.py`, +111/−1, commit `af28f9f1`)

Full-selection scope contrast inside `reconcile` (spec §4.4/PC-5, RED `red-T4-allcov.md`), focal behavior untouched:

- `_t4_is_full_selection(attempt)`: true only when `attempt.selection` is a dict with `kind == "all"`. Any other form (list, dict without kind) keeps the approved T3 focal path.
- `_t4_full_run_declarations(register)`: from committed families only (`state == comprometida`, T2 criterion): required (`expected_in_full_run is True` + reason), optional (`is False` + reason), declared (all ids, for `operation-without-register-entry`). No bool → declared but outside the scope contrast (no invented counts).
- `_t4_full_coverage(profile, register)`: required with zero observations → missing (`expected: 1, observed: 0`, names the op); optional with zero → `unexercised` with its reason, never missing; optional but observed → no diagnostic; observed undeclared → `without_entry`. `blocked = bool(missing)`.
- `_t3_build_reconciliation`: when full-selection AND register present → `coverage.status "all-selection"` (selection = inferred key or `"all"`), with `missing/unexpected/without_entry/unexercised/blocked/measurement ("blocked-incomplete"/"complete")`. Existing `missing → missing-operation-vs-register` and `without_entry → operation-without-register-entry` diagnostics reused, so the op is named and the blob carries `blocked`/`incomplete` when something required is absent. Register-absent still `unavailable` (honest scope); focal selections still `available` via `_t3_coverage`. `entry-check` untouched per packet.
- Quality gates: parse at the boundary (bool-checked flags, verified shapes), guards first, deterministic ordering (sorted ops), intentional names, atomic JSON writes reused.

## 3. Evidence (exact commands, outputs preserved)

- RED confirmed before the change: `python3 -m pytest tests/test_017_001_suite_reconcile.py::test_full_selection_scope_contrast_distinguishes_unexercised_from_missing -q` → 1 failed, `AssertionError` (`coverage.status` `'available'` vs `'all-selection'`).
- **Focal T3/T4 (13):** `python3 -m pytest -q -p no:cacheprovider tests/test_017_001_suite_reconcile.py` → **13 passed in 5.74s** (re-verified post-commit: 13 passed in 5.35s).
- **Focal T1:** `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **17 passed in 29.94s**.
- **Focal T2:** same invocation over `tests/test_017_001_suite_operations.py` → **9 passed in 11.23s**.
- **Proportional regression** (shared `close` path): `... tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 52.13s**.
- **`validate`:** `python3 scripts/cdad-suite.py validate` → rc 0 (`status: ok`).
- **Suite completa no realizada** (focal cycle + proportional regression as routine; no authorization for a complete run).

## 4. Real base attempt reconcile (new out dir, outside `/tmp/opencode`)

- Command: `python3 scripts/cdad-suite.py reconcile --attempt <repo-parent>/evidence/017-001-baseline2/attempt-20261107T171212569537Z-1474770-69bdbdcf --out <tmp>/017-001-T4-green/reconcile-base --register docs/specs/017-001-suite-performance/performance/operation-scope.json` → **rc 0** (`status=complete, diagnostics=none`).
- `coverage.status`: **all-selection** (selection `all`).
- Missing operations: **none** (`missing: []`) — every `expected_in_full_run=true` op has ≥1 observed occurrence.
- Unexercised (false + reason, no missing diagnostic): **product.copy** and **product.generate**, both `cold-branch-requires-manifest-less-source; base-checkout-has-build/staging/manifest.json`.
- `without_entry: []`, `blocked: False`, `measurement: complete`, `diagnostics: []`, payload `status: complete`.
- Note: `wait.*` (false, `declared-unknown`) live in the `desconocida` family and stay outside the committed-scope contrast per the T2 criterion — they remain unknown/remainder, not reclassified as unexercised.
- Out dir `<tmp>/017-001-T4-green/reconcile-base` (new, outside `/tmp/opencode`); the attempt dir is intact (read-only reconcile).

## 5. Limits and role

- `tests/` intact (`git diff --name-only -- tests/` empty); contract intact; `docs/.cdad-state.json` shows the orchestrator's packet bookkeeping (red-018→green-005 prepared), pre-existing, left uncommitted.
- Commit: `af28f9f1` (`feat: implement T4 full-selection scope contrast in reconcile (017-001)`, 1 file, only `scripts/cdad-suite.py`; `git show --stat HEAD` confirms).
