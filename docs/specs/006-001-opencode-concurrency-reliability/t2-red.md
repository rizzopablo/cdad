Task complete. Final report:

## Summary

**File created** (absolute path, write-scope compliant, `tests/` only):
- `<repo>/tests/test_006_001_t2_wait_recovery.py` (new file, own fixture — never touched the shared fake `test_005_009_t2_opencode_adapter.py`, per plan §3 prohibition for T2)

No implementation code was read or touched (`skills/`, `scripts/`, `agents/`, `sources/`, `build/`, `install.sh` were never opened). `tests/test_006_001_t1_selection.py` (T1, GREEN) was only imported from (`FakeInfoServer`, `Pd600T1Case`), never edited.

## Test → postcondition map

- **PD-7** `TestPd7FailureAndAbsence` (4 methods): `failed-with-idle-error` (blocked + error.type/message from the durable `idle` message, truncated to 200 chars), `rc0-no-row` (unknown after settle), `exit-row-not-idle` standalone (unknown after settle, with §2.4 read-count bound verified via an independent sqlite3-audit-hook trace, cross-checked against the I8 `store_reads`), `exit-row-not-idle` server (timeout at cota, settle ignored).
- **PD-8** `TestPd8CorrelationAndOrderedTermination` (1 method): `hangs` with a registered grandchild pid — after the adapter responds, neither the direct client nor the grandchild remains alive (via `/proc/<pid>/stat`).
- **PD-9** `TestPd9PriorAttemptNoRetry` (2 methods): fabricated prior dispatch record (I8 schema) + non-idle row → blocked, binary never invoked; idle-row control → dispatches normally.
- **PD-10** `TestPd10ProportionalWait` (2 methods): `slow-then-idle` — zero reads in the client-alive window (sqlite3.connect audit trace) + bounded reads after exit; store locked via `BEGIN EXCLUSIVE` in rollback-journal mode — completes once released, store bytes/mtime unchanged (INV-1).
- **PD-11** `TestPd11RespondsWithinBudget` (3 methods): `hangs`/`no-idle`/`transport-error` each ≤2.5s, total ≤10s; cota == `WAIT_RESERVE_SECONDS` → blocked pre-dispatch; orchestrator's extra requirement — `completed` in server mode with preflight stays within cota (declared as weak evidence against the ~1-in-3 flake; a single run, not looped).

## Commands and results

Worktree verification (integration gate requirement, never `git stash`):
```
git worktree add <scratchpad>/wt-006-001-t2 HEAD
python3 -m pytest tests/test_006_001_t2_wait_recovery.py -v -p no:cacheprovider
→ 8 failed, 4 passed in 34.15s
```
All 8 failures are `AssertionError` on real contract gaps (never import/syntax/fixture): failed-row diagnosis lacks error.type/message; `rc0-no-row`/`exit-row-not-idle` standalone return `timeout` instead of `unknown` (settle_seconds not implemented yet); `hangs` loses `session` on timeout (matches discovery's documented bug "el timeout pierde el id de sesión"); PD-9 has no prior-attempt check yet (`completed` instead of `blocked`); the locked-store test shows only 1 read (today relies on sqlite's internal busy-timeout, not the configurable poll schedule); `store_reads` is reported as `unknown` (T1 only guarantees format, T2 owns the count); the reserve-boundary cota isn't enforced yet. The 4 passing tests were already correct today (declared, not hidden): server-mode `exit-row-not-idle` → timeout, PD-9 idle-row control, PD-11 three-variants (after fixing two fixture bugs below), and server-mode `completed` with preflight within cota.

Regressions (plan's T2 ficha list):
```
python3 -m pytest tests/test_006_001_t1_selection.py tests/test_005_009_t1_interface.py tests/test_005_009_t2_opencode_adapter.py tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_009_t4_acceptance.py tests/test_005_010_t1_durable_signal.py tests/test_005_010_t2_load_mode_invocation.py tests/test_005_010_reviewfix.py tests/test_005_010_b1_last_assistant.py -q -p no:cacheprovider
→ 77 passed, 1 skipped in 105.11s
```
No regression introduced; worktree removed afterward (`git worktree remove ... --force`); no stray processes left (`ps aux` checked clean after the hangs/grandchild tests).

Two fixture bugs found and fixed during verification (declared, not hidden): (1) `rc0-no-row`/`transport-error` variants didn't create the sessions_db file at all, so the adapter correctly fail-closed on "store doesn't exist" rather than exercising the intended behavior — fixed by writing an empty-schema store; (2) the PD-10 locked-store test originally pre-wrote the row under a fixed session id, but the adapter chooses its own session id dynamically — fixed by having the client itself write the row (with the real chosen session) and signal a sentinel the test's lock-holder thread waits for before acquiring `BEGIN EXCLUSIVE`.

**Commit:** `8447443` — `test: 006-001 T2 RED espera proporcional, clasificación, correlación, terminación ordenada e intento previo`, containing exactly `tests/test_006_001_t2_wait_recovery.py` (1379 insertions). `docs/.cdad-state.json` untouched. No `--no-verify`, no stash, no push.