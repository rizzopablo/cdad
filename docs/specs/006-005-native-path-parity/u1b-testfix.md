Everything is verified. Here is my role report.

## Role report — test-writer, RED substage (TESTFIX), 006-005-native-path-parity U1b

**Intake path:** validated canonical packet `006-005-native-path-parity-test-writer-red-003`. No full cycle/spec skill was loaded. **No implementation code was read** (`skills/cdad-cycle/scripts/**` never opened): the coupling and the lookup key below were established **by behaviour only**, through the suite's own fixtures and throwaway probes (in `/tmp/opencode`, **not committed**). `tests/.sensitive-patterns.local` was never read; no host value was written into any test.

**Decision honoured:** the fix is the **isolation**, never the assertion. PD-6's assertion (`model_configured` null without delegation config, A-1 of 006-003 U4/D3) is untouched.

### 1. Files changed (commit `8bbbdd4`, 2 files, +42/−6)

| File | Change |
|---|---|
| `tests/test_005_009_t2_opencode_adapter.py` | `AdapterCase.empty_user_home()` (**new**): returns a temp dir **inside the test's own `_tmp`**, with an **empty** `.config` (no `cdad/`, no `delegation.json`, no `runtimes.json`). `AdapterCase.run_opencode()` gains the keyword-only `user_home: Path | None = None`: with it, the child env is `HOME=<home>` + `XDG_CONFIG_HOME=<home>/.config`. Backward compatible: with `user_home=None` and `cwd=None`, `env` stays `None` (identical inherited env as before). |
| `tests/test_005_010_t1_durable_signal.py` | `TestPd6WorkerI8FromDurableRow::test_pd6_worker_i8_session_and_model_from_durable_row`: the dispatch is now `self.run_opencode(fake, user_home=self.empty_user_home())` + a comment declaring the isolation (precedent `delegation_home()`), and the method docstring declares the TESTFIX. **Assertions unchanged.** |

### 2. Step 1 — evidence of the coupling (probe, throwaway, behaviour only)

```
$ python3 /tmp/opencode/probe_u1b_testfix.py            # NOT committed
[host-env] host HOME=<home> XDG_CONFIG_HOME=None
   termination='completed'
   record delegate-opencode-…: model_configured='mofgw/deepseek-v4.1-flash' runtime='opencode'
        provenance_configured='delegation config (delegation.json): models.opencode.test-writer'
   record opencode-…:          model_configured='mofgw/deepseek-v4.1-flash' … model_reported='fixture-durable-row-model'
[redirected-empty] HOME=/tmp/cdad-005-009-t2-…/probe-home XDG_CONFIG_HOME=…/probe-home/.config (EMPTY)
   record delegate-opencode-…: model_configured=None
   record opencode-…:          model_configured=None
```
Coupling proven: the value that the PD-6 assertion requires (`None`) is produced **only** when `HOME`/`XDG_CONFIG_HOME` are redirected.

**After the fix** (same test, HOST env, not redirected by the caller, `user_home=` supplied by the fixture):
```
$ python3 /tmp/opencode/probe_u1b_testfix3.py           # NOT committed
host HOME=<home> XDG_CONFIG_HOME=None (NOT redirected by the caller)
termination='completed' attempt='delegate-opencode-7334e1dae39d'
record delegate-opencode-…: model_configured=None runtime='opencode' model_reported=None
record opencode-…:          model_configured=None runtime='opencode' model_reported='fixture-durable-row-model'
```
→ the PD-6 assertion is now **satisfiable** once the A-1/U1b-RED ledger assertion passes (GREEN).

### 3. Step 2 — search for other tests coupled to the user config

**The delegation lookup key is the DESTINATION id, not the runtime** (probe #2, `cdad_delegate.py --destination testdest`, host env):
```
[control-runtime-opencode]     runtime='opencode'          destination='testdest'
   record …: model_configured=None  provenance_configured='delegation config (delegation.json): models.testdest.test-writer'
[pd8-runtime-opencode-clone]   runtime='opencode-clone'    destination='testdest'
   record …: model_configured=None  provenance_configured='delegation config (delegation.json): models.testdest.test-writer'
```

The `delegation.json` observable reaches **three** surfaces: `model_configured` (I8), the `--model` token of the destination argv, and `provenance.model_configured`. I enumerated **every** assertion site of the three and checked its isolation:

| Site | Dispatches without redirect? | Coupled? |
|---|---|---|
| `test_005_010_t1_durable_signal.py::TestPd6` (`model_configured is None`, dest `opencode` = a destination the host config covers) | yes | **YES → fixed** |
| `test_005_009_t1_interface.py::TestPd8` (`model_configured is None` ×2) | yes | **no** — dest `testdest` (probe #2: `models.testdest` absent ⇒ null even with host config); `testdest`/`beta` are fixture-only destination ids a real user config never defines |
| `test_006_001_t1_selection.py` (`"--model" not in argv`) | redirects `XDG_CONFIG_HOME` in that same test (`:1016-1019`) | no |
| `test_006_001_t1b_service_mode.py` (`"--model" not in argv`) | redirects in that same test (`:907-911`) | no |
| `test_006_003_u4_delegation_config.py::TestPd3c` (no `--model`; `model_configured` null + provenance) | redirects (`DelegationAdapterCase`) | no |
| `test_006_003_rf_review_fixes.py::TestO2` (`--model == O2_MODEL`) | strips `XDG_CONFIG_HOME`, repoints `HOME`, `CDAD_INSTALL_ROOT` (its declared subject) | no (by design) |
| `test_006_003_u6_server_credential.py`, `test_006_003_u8_acceptance.py`, `test_006_005_u1a_runtime_config.py`, `test_006_005_u1b_dispatch_entry.py` | all redirect `HOME`/`XDG_CONFIG_HOME` | no |
| `test_005_010_t4_integration.py` (expects `model_configured == CDAD_OPENCODE_MODEL`) | redirects via `delegation_home()` and writes its own `delegation.json` | no |
| remaining dispatch sites of the family (`t2_opencode_adapter`, `t1_durable_signal` PD-1/2/5, `t2_load_mode_invocation` argv matrix, `reviewfix`, `b1_last_assistant`, `t4_acceptance`, `006_001_t1_selection` others, `006_001_t3_concurrency`, `006_001_t2_wait_recovery`) | yes | no — they assert no config-derived value (termination, receipts, store, argv `--standalone/--auto/--server`, schema keys, ledger count); `t2_wait_recovery`'s provenance string is a **fixture-fabricated** record |
| `test_005_007_t5_delegation_dispatch.py`, `test_004_002_t4_dispatch.py`, `test_006_002_u5_transport_equivalence.py`, `test_packet_prepare.py` | **do not dispatch** (synthetic traces / direct record writes / source-level equivalence / packet CLI) | no |

**Result: exactly one coupled test — the assigned one.** No other file was touched for this. Declared latent note (not applied): `TestPd8` of `t1_interface` and any future case asserting config-derived values would need the same isolation if a fixture ever used a destination id a user config can define; today `testdest`/`beta` are fixture-only ids, so its result does not depend on the user config.

### 4. Step 3 — runs with the host env (`XDG_CONFIG_HOME` unset, no redirect)

```
$ python3 -m pytest -q tests/test_005_010_t1_durable_signal.py
1 failed, 5 passed in 20.18s
FAILED …TestPd6WorkerI8FromDurableRow::test_pd6_worker_i8_session_and_model_from_durable_row
E   AssertionError: 2 != 1 : PD-1/D-14: el despacho dejó 2 registros I8 nuevos (se espera EXACTAMENTE uno: el del módulo; la interfaz relaya el `attempt` y no registra):
    ['delegate-opencode-a2170bc5c223', 'opencode-f3af82c9058d']
```
→ the remaining failure is **the already-declared U1b RED** (A-1 ledger, one record per dispatch), an `AssertionError` about missing behaviour — **not** the environment-dependent `model_configured` failure, and never an import/syntax error.

```
$ python3 -m pytest -q tests/test_005_009_t2_opencode_adapter.py
8 passed in 26.54s
```
→ the fixture change is behaviour-preserving for its 8 existing cases.

**Widened run** (my edit touches the shared `AdapterCase` imported by the whole family — declared regressions of the unit):
```
$ python3 -m pytest -q -rf <the 16 declared files: focal + regressions>
19 failed, 112 passed, 2 skipped in 251.26s (0:04:11)
```
The 19 failures are **exactly the declared set**: 12 focal U1b RED (`test_006_005_u1b_dispatch_entry.py`; `TestPd9` remains the pre-satisfied guard) + 4 `t1_interface` A-1 + 1 `t1_durable_signal` A-1 + 2 `reviewfix` A-1. 2 skipped = `t4_acceptance` (PD-10 owner gate) + `t4_integration` (`CDAD_OPENCODE_INTEGRATION=1`). **No new failure, none config-dependent.**

Also run: `make validate` → `Assert PASS: 168 / Assert FAIL: 1` (`F011: scripts/validate-subagents.sh`). **Pre-existing and unrelated**, declared honestly: it is `install.sh --check` **drift of the skills installed on this host** (`~/.claude/skills/cdad-cycle/references/cli-delegation.md` differs), i.e. host-install state read by `scripts/validate-subagents.sh`; nothing in my diff (tests-only, 2 files) is read by that check.

### 5. Commit

```
$ git add tests/test_005_009_t2_opencode_adapter.py tests/test_005_010_t1_durable_signal.py
$ git commit -m "test: 006-005 U1b testfix — aislamiento de la config de usuario en tests de despacho"
[main 8bbbdd4] test: 006-005 U1b testfix — aislamiento de la config de usuario en tests de despacho
 2 files changed, 42 insertions(+), 6 deletions(-)

$ git show --stat --format='%H%n%s' HEAD
8bbbdd40436a19a405a92a4864c1f93f052038c1
test: 006-005 U1b testfix — aislamiento de la config de usuario en tests de despacho
 tests/test_005_009_t2_opencode_adapter.py | 29 +++++++++++++++++++++++++----
 tests/test_005_010_t1_durable_signal.py   | 19 +++++++++++++++++--
```
No `--no-verify`, no stash, no push. Working tree after the commit: only the not-mine untracked paths remain and are **untouched**:
```
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md
```

### 6. Limits declared

- Probes are throwaway files under `/tmp/opencode/` (not committed); they only exercise the fixtures as processes.
- The isolation is in the **test fixture**; the product's contract is unchanged and `--exec-config` remains the common interface's internal mechanism (the new entry `cdad_dispatch.py` is U1b's product and is not referenced by this testfix).
- If U1b's GREEN makes the module read a user-level `runtimes.json` for this path, this test's premise (`empty_user_home()`) would have to be revisited — declared here, not silently assumed. Today the dispatch reaches `completed` under the empty home (probe #3), so the premise holds.