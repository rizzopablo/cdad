Done. Here is the role report.

---

# Role report — test-writer, RED (U6-7b TESTFIX), 006-005-native-path-parity

**Intake path:** validated packet (`packet_id: 006-005-native-path-parity-test-writer-red-021`, `substage: red`). No cycle/spec skill loaded. Inputs read: the approved contract (`docs/specs/006-005-native-path-parity/spec.md`), the implementer's GREEN report in the same contract folder (`u6fix7b-green.md` §5), the packet's execution authority (`docs/epics/epic-006-opencode-concurrency/execution.md` U6-7), and the test files inside the declared read scope (`tests/`).

**Phase isolation (declared):** no implementation code was read. Nothing under `skills/`, `scripts/`, `sources/`, `build/`, `install.sh` or `agents/*.md` was opened; the fixture copies `agents/cdad-*.md` mechanically (existing pattern of `test_004_002_t5_runtime.py`). The only product surface exercised is `prepare` as a black-box process, through the shared fixture helpers.

## 1. Modified files (write scope only)

| File | Change |
|---|---|
| `tests/test_006_005_u6fix7b_derived_strips_write.py` | The single wrong assertion corrected + second fixture (odoo policy) added. +122/−8. |

Nothing else was written. `docs/.cdad-state.json` was already dirty before this session and `docs/planning/` + `findings/*` are untracked and not mine — left untouched (verified: `git show --stat HEAD` = 1 file).

## 2. The correction (contract basis)

`test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary` demanded `cdad-test-writer-odoo.md` → `addons/m/tests/test_m.py` = **allow** under the **cdad** layout policy, where `addons/` is unclassified. That contradicts 004-002 PD-7 (scopes restrict the policy, never widen it) and 006-005 §2.9 (derived test-writer map = `deny *` + `tests/` + colocated + temporaries + barriers). The lever `write: ask` masked the contradiction in RED (everything resolved `ask`, so the subtest failed for the wrong reason).

- **cdad policy (existing fixture):** the derived odoo agent now resolves **whatever its own `edit` map resolves** — the odoo stack expectation is not demanded there.
- **odoo policy (new fixture `TestDerivedOdooAgentUnderOdooPolicy`, `LAYOUT = "odoo"`):** the concrete expectations hold, measured **by the write tool**: `addons/m/tests/test_m.py` = **allow**, `addons/m/models/m.py` = **deny** — the same pair `tests/test_004_002_t5_runtime.py::test_pd7_i9_maps_odoo_layout` already fixes for the `edit` map.
- Declared in the docstrings, verbatim: **«testfix: la expectativa odoo va con politica odoo (PD-7)»** (module docstring, A-1 bis; test docstring; new test docstring).
- The fixture was made layout-parameterized (`LAYOUT` class attribute; `materialize_layout(root, layout)`), so the cdad fixture is unchanged in behavior.

**Postcondition mapping:** the new test maps to **PD-24** (E2/PD-24, U6-7b) with **PD-7** as the policy discipline. No product change; no scope widening.

## 3. Exact commands and output

```
$ python3 -m pytest tests/test_006_005_u6fix7b_derived_strips_write.py -q --tb=short
......                                                                   [100%]
6 passed in 3.58s
```
```
$ python3 -m pytest tests/test_006_005_u6fix7b_derived_strips_write.py -v --tb=short   # post-commit
tests/…::TestDerivedAgentsIgnoreInstalledWriteLever::test_u6_7b_derived_implementer_and_readers_keep_their_maps PASSED [ 16%]
tests/…::TestDerivedAgentsIgnoreInstalledWriteLever::test_u6_7b_derived_orchestrator_control_stays_allow PASSED [ 33%]
tests/…::TestDerivedAgentsIgnoreInstalledWriteLever::test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary PASSED [ 50%]
tests/…::TestDerivedAgentsIgnoreInstalledWriteLever::test_u6_7b_every_derived_agent_ignores_the_installed_write_lever PASSED [ 66%]
tests/…::TestDerivedAgentsIgnoreInstalledWriteLeverDrift::test_u6_7b_second_prepare_does_not_claim_hand_edits PASSED [ 83%]
tests/…::TestDerivedOdooAgentUnderOdooPolicy::test_u6_7b_derived_odoo_test_writer_under_odoo_policy PASSED [100%]
============================== 6 passed in 2.04s ===============================
```
Focals + declared regressions (packet validation plan: the two U3 focals, the 13 declared regressions, plus the derived-map regressions the GREEN ran: `t7_l1_derived`, `t7_w2`):
```
$ python3 -m pytest -q --tb=short <focal + 2 focals + 15 regresiones>
181 passed in 157.24s (0:02:37)
```
The complete suite was **not** run (declared policy: it runs once, at closure, by whoever closes).

## 4. Falsification evidence (the new oracle is not vacuous)

Measured with the test module's own fixtures and evaluators (no implementation read), on the odoo fixture (`prepare` rc=0):

```
--- published derived (post-fix) ---
  addons/m/tests/test_m.py: edit='allow' write='allow'
  addons/m/models/m.py:     edit='deny'  write='deny'
--- installed copy (origin, lever live) ---
  addons/m/tests/test_m.py: write='ask'
  addons/m/models/m.py:     write='ask'
--- published derived WITH the lever re-inserted (pre-fix shape) ---
  addons/m/tests/test_m.py: edit='allow' write='ask'
  addons/m/models/m.py:     edit='deny'  write='ask'
```
So if the derivation had not retired the lever, the new test fails with `AssertionError('ask' != 'allow' / 'ask' != 'deny')` — an assertion about missing behavior, not an import/syntax/fixture error. The origin-level `'ask'` is asserted as an explicit precondition inside the new test (the lever is alive ⇒ the case proves something). Under the cdad policy the corrected assertion reads `edit='deny' write='deny'` for `addons/m/tests/test_m.py` — the derived odoo resolving exactly what its own `edit` map resolves.

## 5. Commit

`e58c0a8` — `test: 006-005 U6-7b testfix — expectativa odoo con politica odoo` (1 file, +122/−8). No `--no-verify`, no `git stash`, no push.

## 6. Declarations for the orchestrator

- **Path guard note (honest):** one attempt to write a scratch helper to `/tmp/opencode/` was **denied** by the write-scope guard (`write_scope: tests`); I did not work around it — the witness was re-run inline through `python3 -` (stdin), creating no file anywhere.
- No host values, session ids, credentials or endpoints entered the test file or the commit.
- The focal is now green against the committed product (`58af287`); the unit's single open assertion is closed by this testfix, and no product change is implied by it.