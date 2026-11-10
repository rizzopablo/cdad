# FINAL TEXT — implementer review-fix (Route C, 017-001 T1 corrección H1–H3)

## Route C validation — PASS (before working)

- Dispatch identification block names packet `017-001-suite-performance-implementer-review-fix-001`, execution `exec-017-001-suite-performance-001`, contract `docs/specs/017-001-suite-performance/spec.md` sha256 `472bab0c…192672e` — all equal `REQUEST.json`.
- `validate-request` → rc=0. `validate-packet` → rc=0.
- Contract sha256 matches `spec.md` on disk (`sha256sum` verified).
- Execution context `schema_version=2` → v2, Route C admissible. Zero `---cdad-packet-json` markers in dispatch → no route mixture.
- Worked on Route C, substage `review-fix`, declared inputs/scopes only. `tests/` read, never edited.

## Findings verified against original evidence (before changing code)

- **H1** (`cdad-suite.py:962-977`, observer `29-42`): observer swallowed capture exceptions to stderr only; `build_profile` checked only ≥1 phase per nodeid and ignored `read_xml_names`. Reproduced at unit level: empty-but-parseable XML + setup-only sink → `complete`. Confirmed.
- **H2** (`cdad-suite.py:1083-1090`): `build_profile` + `write_json_atomic(profile)` ran before `state=finished`/`rc` with no guard; a write error propagates, leaving the attempt `running`/`rc null`. Confirmed by reading the flow.
- **H3** (`cdad-suite.py:895-916, 1057-1066`): `child_argv`/`child_wall_s` assigned only on normal return; `KeyboardInterrupt` path wrote `pytest_argv: []`, `pytest_wall_s: null`. Confirmed.
- Phase-shape ground truth established empirically (real pytest run, not assumed): `pass` → setup/call/teardown; `skip` (mark) → setup(skipped)+teardown, **no call**; setup-error → setup(failed)+teardown, **no call**. The H1 rule exempts exactly these two legitimate absences, so clean runs stay `complete`.

## Modified files (commit `7b0b0b32`)

- `scripts/cdad_suite_observer.py` (+7): `_CAPTURE_ERRORS` list; capture exceptions appended as well as stderr-printed; `pytest_sessionfinish` payload gains `capture_errors`. Measuring still never breaks the measured run.
- `scripts/cdad-suite.py` (+153/−37):
  - **H1**: new `read_sink_payload` (phases + capture errors + diagnosis; missing key = zero declared errors, so the RED shadow without the key still works); new `read_xml_info` (names + skipped set; parseable-but-empty XML is an inconsistency issue); `build_profile` now forces `incomplete` on capture errors, XML issues, selection↔XML mismatch in **both** directions, per-nodeid missing phases, and per-phase loss for run tests (skipped nodeids exempt; failed setup exempts `call` only); never invents un-emitted phases. Profile gains additive `capture_errors` key.
  - **H2**: contractual finalization (`finished` + child rc) separated from profile build/write, wrapped in `except Exception`: measurement failure lands in `record["profile_diagnosis"]` + stderr warning (contains "profile"/"medición", no `Traceback`), stale temp cleaned best-effort, no `complete` substitute profile, rc preserved in output and attempt.
  - **H3**: new `pytest_argv_for` (deterministic argv builder reused by `run_pytest_to_logs`); `cmd_close` pre-computes `child_argv` and `child_start` before launch; both interrupt handlers recover `child_wall_s` when still `None`. Contractual interrupt treatment unchanged (`interrupted`, return 130).
- `tests/`: untouched. `docs/.cdad-state.json` modification is preexisting (present before this turn, not committed by this role).

## Exact commands + outputs

- Focal: `python3 -m pytest -v -rs -o addopts= -p no:cacheprovider tests/test_017_001_suite_profile.py` → **8 passed in 13.66s** (5 prior R1–R5 unmodified + 3 new H1–H3).
- Regression (packet-declared): `… tests/test_008_002_suite_evidence.py tests/test_008_002_suite_selection.py tests/test_008_005_ci_gate.py` → **49 passed in 53.80s**.
- `python3 scripts/cdad-suite.py validate` → **rc 0**, `status: "ok"`, 2002 nodeids collected, 239 modules, 31 map entries, `timing.status: "pending"`.
- Unit probe of `build_profile`: empty-XML+setup-only → `incomplete`; capture-errors-with-full-phases → `incomplete`; clean triple+matching XML → `complete`. **PROBE OK**.
- Suite completa **no realizada** (ciclo focal + regresión proporcional sin completa como rutina, por política declarada en el paquete; sin autorización para completa).

## Limits

- The fix covers T1 phase-profile integrity only; it does not deliver calibrated operation intervals or a base (T2+ tasks, per review abstentions).
- `cdad-ci-gate.py` not run (packet: not a routine T1 check).
- Full suite green claimed only for the executed selection (8 + 49); no complete-suite run performed or claimed.
