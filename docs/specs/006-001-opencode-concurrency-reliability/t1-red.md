Task complete. Final report:

## Summary

**Files modified** (all absolute paths, all under `tests/`, write-scope-compliant):
- `<repo>/tests/test_006_001_t1_selection.py` (new, 18 tests)
- `<repo>/tests/test_005_010_t2_load_mode_invocation.py` (oracle 1, authorized)
- `<repo>/tests/test_005_009_t2_opencode_adapter.py` (oracle 2, authorized — shared fake's `--version` now responds before locating the packet/writing the store/registering the call)

No implementation code was read or touched (`skills/`, `scripts/`, `agents/`, `sources/`, `build/`, `install.sh` were never opened).

**Test → PD map** (docstring in the new file has the full version):
- PD-1 (mode selection matrix): `TestPd1ModeSelectionMatrix` — 5 methods
- PD-2 (server preflight, §2.3 rows + password order): `TestPd2ServerPreflight` — 8 methods
- PD-3 (provenance on every termination, §2.6 pairs): `TestPd3ProvenanceEveryTermination` — 2 methods
- PD-4 (same errand in server mode): `TestPd4SameErrandInServerMode` — 1 method
- PD-5 (no secrets, stderr redaction): `TestPd5NoSecretsInOutputs` — 2 methods

**Exact commands and results:**

```
python3 -m pytest tests/test_006_001_t1_selection.py -q -p no:cacheprovider
→ 14 failed, 4 passed in 32.30s
```
All 14 failures are `AssertionError` on the documented contract behavior (never ImportError/SyntaxError/fixture errors) — e.g. `'completed' != 'blocked'`, `1 != 2` (preflight call count), `[] is not true` (no worker provenance record), URL literal found in diagnosis. 4 tests pass today and are declared as such in their docstrings (not hidden): `test_pd1_mode_server_with_valid_url_dispatches_server_flag_only`, `test_pd2_password_order_prefers_first_env_var_when_valid`, `test_pd4_same_errand_in_server_mode`, `test_pd5_no_secrets_in_successful_dispatch_outputs` — today's adapter already dispatches server mode "straight through" (no preflight), so these happy-path assertions already hold; the gap is specifically the *new* preflight/registration/redaction behavior.

```
python3 -m pytest tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider
→ 36 passed in 59.64s (clean rerun)
```
One earlier run showed `TestPd7` failing with `'timeout' != 'completed'`; reran `TestPd6`/`TestPd7` 3× in isolation and they passed every time — this matches the pre-existing, already-documented ~25% timing flake noted in `test_005_009_t2_opencode_adapter.py`'s own header (lines 241-255), unrelated to my oracle-2 edit (which only touches the `--version` early-exit branch, never the wait-margin race).

**Commit:** `91f7e98` — `test: 006-001 T1 RED selección de modo, preflight, procedencia y secretos`, containing exactly the 3 files above (`docs/.cdad-state.json`, pre-existing dirty, left untouched/unstaged). No `--no-verify`, no stash, no push.

**Declared scope limits** (per plan, not implemented here): §2.7 prior-attempt check, PD-11 timeout-at-cota, and exact `store_reads`/`prior_check_reads` counts are T2's card — this file only asserts those two keys are present and are digit-text or `unknown` (INV-9), never the exact value.