# Role report — test-writer RED (T4, 017-001-suite-performance)

## Intake (route C — explicit file backup): VALIDATED, executed
- Dispatch identification matches the canonical render byte-for-byte: `python3 scripts/cdad_packet.py render --project-root <repo> --execution-context .cdad/executions/exec-017-001-suite-performance-001/execution.json --request .cdad/packets/017-001-suite-performance-test-writer-red-018/REQUEST.json --route C` emits exactly the dispatched JSON.
- `validate-request` → exit 0; `validate-packet` → exit 0. Contract sha256 `472bab0c…192672e` matches `docs/specs/017-001-suite-performance/spec.md` on disk. Execution context `schema_version: 2` → v2 requirement satisfied (no silent route switch). Zero `---cdad-packet-json` markers in the dispatch → no route mixture. `docs/.cdad-state.json` `tdd_substage: red` matches the packet substage.
- Scope respected: read only declared inputs (`spec.md`, `t3-aggregator-contract.md`, `performance/operation-scope.json`, `tests/test_017_001_suite_reconcile.py`); edited only `tests/**`. **No implementation code read** — the CLI was exercised black-box (`reconcile --help`, probe runs), never its source. No full-cycle/spec skills loaded; the packet was the execution contract.

## Pre-RED search (contribution of the new test)
- The 12 existing tests in `tests/test_017_001_suite_reconcile.py` cover T3 accounting (`expected` counts, `operation-without-register-entry`, incomplete status, determinism, rc codes) but none covers the §4.4 base-run scope contrast over a full selection.
- `t3-aggregator-contract.md` has no `all-selection` coverage status and no `expected_in_full_run` rule (coverage without register is `unavailable`).
- `performance/operation-scope.json` already declares per-operation `expected_in_full_run` + `expected_in_full_run_reason`, but black-box probes confirm `reconcile` ignores them today (coverage `available`, `missing: []` even for a `true` op with zero observations).
- **Traceability:** new test protects **PC-5** (base report contrasts capture vs committed scope; unexercised vs capture-failure) with **PC-6/INV-6**. **Without this test, the user could consume the baseline over broken capture: a committed operation missing from the full run passes silently because today's coverage cannot tell "not exercised" from "failed to capture".**

## Work done (append-only; the 12 existing tests untouched)
- Added to `tests/test_017_001_suite_reconcile.py` (+243 lines, no modifications): `test_full_selection_scope_contrast_distinguishes_unexercised_from_missing` + 4 small helpers. Synthetic full-selection attempts (`attempt.json` with `selection.kind == "all"`) and synthetic registers in the real register shape (`expected_in_full_run` + reason), all in disposable `tmp_path` dirs.
  - **Case A** (declared `false`, zero observations) → `coverage.status "all-selection"`, reported as not-exercised, no `missing-operation-vs-register`.
  - **Case B** (declared `true`, zero observations) → `missing-operation-vs-register` naming the op, measurement incomplete/blocked.
  - **Case C** (observed undeclared → `operation-without-register-entry` naming it; declared `false` but observed → no diagnostic).

## Evidence (RED — fails for the right reason)
- Focal: `python3 -m pytest tests/test_017_001_suite_reconcile.py::test_full_selection_scope_contrast_distinguishes_unexercised_from_missing -q` → **1 failed**, `AssertionError` (case A: `coverage.status` is `'available'`, expected `'all-selection'`), never `ImportError` nor collection error. rc==0 assertions pass, so the failure is purely the absent promise.
- Regression guard: `python3 -m pytest tests/test_017_001_suite_reconcile.py -q` → **12 passed, 1 failed** (only the new RED test).
- **Commit:** `867d537a` — `tests/test_017_001_suite_reconcile.py` only (1 file, +243). `git show --stat HEAD` confirms. (`docs/.cdad-state.json` shows as modified by the orchestrator's packet bookkeeping red-017→red-018, pre-existing, not mine, not committed by me.)

## Delta de inventario vivo (como texto, para que el orquestador lo materialice)
Propuesta de alta T4 (017-001): `tests/test_017_001_suite_reconcile.py::test_full_selection_scope_contrast_distinguishes_unexercised_from_missing` — protege spec §4.4/PC-5 (contraste de alcance declarado vs observado en la corrida base, selección completa, `coverage.status "all-selection"`; distingue no-ejercitado de fallo de captura) con PC-6/INV-6; estado RED (falla por AssertionError de promesa ausente, commit 867d537a); rationale: sin esta protección la base puede consumirse sobre captura rota porque la cobertura actual no evalúa `expected_in_full_run`.

## Honest declarations
- Phase isolation kept: no `src/`/`scripts/` reads; only black-box CLI executions and authorized inputs. Diff limited to `tests/`.
- No wall-clock bounds, no property campaign, no deferrals introduced; existing suite run recorded above is the focal-file selection, not a full-suite green claim.
