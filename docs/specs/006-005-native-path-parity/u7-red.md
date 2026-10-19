## Role report — test-writer / RED / U7 (006-005)

### Files modified
| File | Change |
|---|---|
| `tests/test_006_005_u7_scribe_role_report.py` | **new** (822 lines) — focal RED of U7 |
| anything else | none (`git status`: only the two pre-existing untracked paths `docs/planning/` and `findings/…` that are not mine) |

No implementation file was read. Black-box probing used only the CLI surfaces declared in the contract (`cdad_packet.py prepare`, `cdad_result.py receive/materialize`), run as processes.

### Test → PD map
| Test | PD | Kind |
|---|---|---|
| `test_pd26_scribe_role_report_materializes_into_the_spec_folder` | PD-26 (§2.8.3) positive: scribe/`memory` receipt with single part `role-report` ⇒ `materialize` rc=0 into `docs/specs/<feature>/`, sha identical to the received part, receipt `pending`, `approval_effect: false`, state+receipt untouched | **RED** |
| `test_pd26_memory_bank_targets_stay_rejected_naming_the_allowed_root` | PD-26 negative destination: each of the four Memory Bank files (`projectbrief`, `systemPatterns`, `activeContext`, `progress`) with `role-report` ⇒ rc≠0 **naming `docs/specs/<feature>/`**, no target written, no stdout, no traceback, state+receipt intact | **RED** |
| `test_pd26_role_axis_role_report_of_other_roles_stays_rejected` | PD-26/PD-23 role axis (D-17 rejects admitting it "for all roles"): `role-report` of test-writer/red, test-writer/audit, implementer/green, reviewer/review, architect/brainstorm stays rejected | anchor |
| `test_pd26_r3_crossings_stay_rejected` | PD-26/PD-23 R3: the four role↔kind crossings, including `("scribe","memory","test-audit")` | anchor |
| `test_pd26_r5_scribe_file_kinds_still_materialize` | PD-26 R5: the four `scribe-*` still materialize their file roots with identical bytes | anchor |
| `test_pd26_materialization_table_asset_is_unchanged` | PD-26/PD-23: `skills/cdad-cycle/assets/artifact-policy.json` unchanged (sha256 of bytes only; file not parsed) | anchor |

### Commands and output
```
$ python3 -m pytest tests/test_006_005_u7_scribe_role_report.py -q
2 failed, 4 passed in 13.40s

FAILED …TestPd26ScribeRoleReportMaterializes::test_pd26_scribe_role_report_materializes_into_the_spec_folder
FAILED …TestPd26MemoryBankTargetsStayRejected::test_pd26_memory_bank_targets_stay_rejected_naming_the_allowed_root
```
Both failures are `AssertionError` on missing behaviour — no ImportError/syntax/CLI-absent failure. Measured stderr at HEAD `4463969`:
```
ERROR: artifact_kind 'role-report' is not permitted for role 'scribe'/substage 'memory':
a kind of another role fails in the closed §7 table
```
The negative-destination case fails on the *second* assertion (`ALLOWED_ROOT in stderr`): today the rejection is by the role axis and does not name the allowed root, so the declared boundary "the Memory Bank is not reachable by this kind" is not yet established. Preconditions (`prepare`, `--record-dispatch`, `receive` rc=0 with `semantic_status: pending`) all pass, so the RED is not contaminated by a fixture error.

Declared regressions (ficha U7) — all green:
```
$ python3 -m pytest tests/test_003_002_t2_materialize.py tests/test_003_002_t2_reviewfix.py \
    tests/test_003_002_t1_receive.py tests/test_003_002_t1_reviewfix.py \
    tests/test_003_002_t4_integration.py tests/test_005_007_t4_architect_report_materialization.py -q
50 passed in 105.41s
```

`make validate`: **pre-existing, unrelated failure**, not caused by this change (it is a docs/test-only commit and the validator inspects installed skills):
```
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
$ bash scripts/validate-subagents.sh
DRIFT: differs <home>/.claude/skills/cdad-cycle/scripts/__pycache__/cdad_delegate_opencode.cpython-313.pyc
DRIFT: differs <home>/.claude/skills/cdad-cycle/references/cli-delegation.md
❌ install.sh --check failed (rc=1)
Assert PASS: 168 / Assert FAIL: 1
```
It is host-installed-skill drift from earlier units (pycache + `cli-delegation.md` in `~/.claude/skills`), outside `tests/` and outside my write scope. Flagging it to the orchestrator rather than fixing it.

### A-1 (rule declared)
**No replacement is needed.** A test fixing the scribe row *including the absence of `role-report`* was searched for and does not exist: R2 covers only the audit kinds, R3 crosses `("scribe","memory","test-audit")`, the R5 classes use the four `scribe-*`, and the U1b/U2 focals explicitly declare the scribe materialization as U7's oracle without asserting rejection. This file adds oracles only and modifies no other test.

### Commit
```
ba95af5 test: 006-005 U7 RED — fila del scribe en la tabla cerrada (PD-26)
 tests/test_006_005_u7_scribe_role_report.py | 822 ++++++++++++++++++++++++++++
 1 file changed, 822 insertions(+)
```
Tests-only commit, no `--no-verify`, no stash, no push.