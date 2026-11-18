Work complete. FINAL TEXT report:

# Review-fix T3 — report (017-001-suite-performance, packet …-review-fix-007)

**Route C validation (before working):** packet_id, execution_id (`exec-017-001-suite-performance-001`) and contract sha256 from the dispatch match `.cdad/packets/…-007/REQUEST.json` and `PACKET.md`; `docs/specs/017-001-suite-performance/spec.md` hashes to `472bab0c…192672e` (matches); execution context is v2 (`schema_version: 2`). No inline packet body — admissible on route C. Proceeded.

**Blocking finding (review-T3-002, verified against original evidence):** `scripts/cdad-suite.py:2056-2057` — when `_t3_declared_selection_nodeids()` returned `None` (selection missing or unresolvable), the loop did `continue` with no failure reason, so `selection-coverage` could pass without binding map key → declared selection.

**Fix (commit `cce652f3`, only `scripts/cdad-suite.py`, 6+/1-):** `declared is None` now appends a named reason — `{key}: el intento no declara una seleccion verificable (selection ausente o irresoluble en attempt.json; sin inventarla)` — yielding `passed=false`, `satisfied=false`, exit 1. The `expected`-not-a-list skip is preserved unchanged (no register data to bind against → nothing invented). No test or contract file touched.

## Evidence — exact commands & output

- RED first: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -o addopts= -p no:cacheprovider tests/test_017_001_suite_reconcile.py::test_entry_check_missing_or_unresolvable_selection_fails_selection_coverage` → **1 failed** (line 743, missing-selection case rc 0).
- Focal T3: `… tests/test_017_001_suite_reconcile.py` → **12 passed in 4.29s**.
- Focal T1: `… tests/test_017_001_suite_profile.py` → **17 passed in 21.59s**.
- Focal T2: `… tests/test_017_001_suite_operations.py` → **9 passed in 9.88s**.
- Proportional regression (T2 tranches + T1 plan regressions, all exercise `scripts/cdad-suite.py`): `… tests/test_017_001_suite_tranche1.py tests/test_017_001_suite_tranche2.py tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **51 passed in 47.11s**.
- `python3 scripts/cdad-suite.py validate` → rc 0, `status: ok`.
- Real 8-selection map (`~/clawd/tmp/017-001-calibration-map.json` → out under `~/clawd/tmp/017-001-reviewfix-007/`, outside `/tmp/opencode`): correct map → **rc 0, satisfied=true**; C-R→C-E negative control → **rc 1, satisfied=false**, `selection-coverage` names C-R with both discrepant selections.
- Reviewer's exact repro on real evidence (copied C-R attempt, deleted only `selection`, repointed map): → **rc 1, satisfied=false**, `selection-coverage` = `["C-R: el intento no declara una seleccion verificable (selection ausente o irresoluble en attempt.json; sin inventarla)"]`. Original evidence untouched.

## Limits

- **Suite completa no realizada** (focal + regresión proporcional como rutina, sin autorización para la completa en este momento): executed selection = 12 T3 + 17 T1 + 9 T2 + 51 regression = 89 passed; `make validate` run separately (see below).
- `make validate`: **182 PASS / 1 FAIL (F011 `validate-subagents.sh`)** — verified **pre-existing** by re-running with my change stashed (identical 182/1 on the committed tree); unrelated to T3, out of write scope, left for the orchestrator.
- `git status` shows only the pre-existing `docs/.cdad-state.json` modification (already dirty before this task per review-T3-002; not mine, not committed). Committed: `cce652f3` touching solely `scripts/cdad-suite.py`.
