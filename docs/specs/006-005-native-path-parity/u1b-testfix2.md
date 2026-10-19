All three fixes are in, focal + A-1 + regressions green, and the commit is tests-only. Here is the role report.

---

# Role report — test-writer, RED (testfix), `006-005-native-path-parity` / U1b

**Intake path:** validated canonical packet `006-005-native-path-parity-test-writer-red-004` (first line `---cdad-packet-json`). No full cycle/spec skill was loaded — the packet is the execution contract. Read only the declared inputs: the approved spec (`docs/specs/006-005-native-path-parity/spec.md`, sha256 `3a824be3…` — matches the packet), the implementer report `u1b-green.md`, the tests under `tests/` and the fixture helpers they import (`test_004_002_t2_bootstrap.py`, `test_005_001_t4_decisive.py` precedent). **No implementation code was read** (nothing under `skills/`, `scripts/`, `agents/`, `sources/`, `build/`); the product CLIs were only *invoked as processes*, never inspected. `tests/.sensitive-patterns.local` was not read. No host values were added.

**Scope:** test-side correction of the three oracles the implementer reported blocked (`u1b-green.md` §4), without changing the postcondition each test verifies. The implementation commit `3af53f1` was not touched.

## 1. Modified files (commit `b28be34` — tests only, no `--no-verify`, no stash, no push)

| File | Change |
|---|---|
| `tests/test_006_005_u1b_dispatch_entry.py` | `+57/−…` — PD-5 membership oracle: per-iteration attempt; PD-23 fixture: approved epic plan (row + `epic_history` approval) |
| `tests/test_005_009_t1_interface.py` | `+44/−…` — PD-8 A-1 oracle: ledger snapshot before the second dispatch; the fixture stub declares a per-invocation attempt |

```
$ git show --stat --format='' HEAD
 tests/test_005_009_t1_interface.py       | 44 ++++++++++++++++++------
 tests/test_006_005_u1b_dispatch_entry.py | 57 +++++++++++++++++++++++++++++---
 2 files changed, 86 insertions(+), 15 deletions(-)
$ git status --short
?? docs/planning/                                              # not mine, untouched
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md   # not mine, untouched
```

## 2. Change per test (the postcondition each asserts is unchanged)

**(1) `TestPd5NativeCorrelation::test_pd5_native_nested_project_is_accepted_by_membership` (PD-5/INV-15).**
The `subTest` looped over two directories of the *same* project with the *same* `ATTEMPT_PD5`, then asserted `single_record(before)` ⇒ exactly one **new** record per iteration. Iteration 2 registers a *different* observation under an existing attempt, which the ledger refuses on purpose (a contract tested elsewhere: repeating an identical record is idempotent; different data is refused). So the second iteration could never yield a new record for *any* implementation.
Change: each iteration gets **its own attempt id** (`"%s-%02d" % (ATTEMPT_PD5, index)`), a real dispatch of its own. Added assertion `out["attempt"] == attempt` so the identity of *this* iteration's dispatch is pinned — an auto-disambiguated attempt id inside `record` would be caught instead of hiding the conflict. The nested-layout acceptance by membership (the postcondition) is untouched.

**(2) `TestPd23NativeDescriptorKind::test_pd23_native_descriptor_kind_is_derived_from_role_and_substage` (PD-23/§2.8).**
The second half builds an architect packet, but the fixture could not publish it: `prepare --role architect` requires the approved **plan of the active epic** (`epic_history` `epic-plan` with `approved_by`) and the plan table row that names the feature. This is a fixture precondition, independent of the implementation.
Change: the fixture authority (`new_project`) now writes the epic plan with the feature row (the product's template form, the id as a complete token) and injects the `epic-plan` approval into `epic_history`. Precedent: `tests/test_005_001_t4_decisive.py:262-284`, `tests/test_005_013_t1_unit_projection.py:266-305`. Probe (below) isolates the cause: without the approval `prepare` → `rc=2 ERROR: approval pending …`; with it → `rc=0`, packet `…-architect-draft-001`.

**(3) `TestPd8PortableExecConfigNotVpsValues::test_pd8_exec_config_portable_config_beats_product_no_host_values` (A-1, reformulation).**
Two independent test-side defects: (a) `records_mid` was snapshotted **after** `proc_two` — the very invocation whose “exactly one new record” it then counts — so the set was always empty (`0 != 1` before any further assertion); (b) the fixture stub declared a **constant** `_ATTEMPT` for both dispatches, the second carrying a different `runtime`, so the ledger refused it and `assertNotEqual(record_two, record_one)` was unreachable.
Change: the snapshot is taken **before** `proc_two`; the stub now derives its attempt **per invocation** (`_next_attempt()`: index = calls already logged + 1), so two dispatches with different data never share an attempt. The oracle (two distinct exec-configs ⇒ two distinct records; config beats product defaults; `model_configured` null) is unchanged.

## 3. Commands and outputs (exact)

```
$ python3 /tmp/opencode/u1b-testfix2/probe_architect.py      # not committed, fixture probe
=== stub plan, no approval (today's fixture) ===      rc: 2
  ERROR: approval pending: … epic_history has no entry with epic
  'epic-004-single-source-planning', stage 'epic-plan' and a non-empty approved_by
=== stub plan, approval injected ===                  rc: 0   packet 004-002-project-execution-bootstrap-architect-draft-001
=== plan with table row + approval injected ===       rc: 0   role/substage: architect draft

$ python3 -m pytest -q tests/test_006_005_u1b_dispatch_entry.py
13 passed in 14.79s                                   # was 11 passed / 2 failed (the two blocked focal oracles)

$ python3 -m pytest -q tests/test_005_009_t1_interface.py tests/test_005_010_t1_durable_signal.py \
      tests/test_005_010_reviewfix.py tests/test_005_010_t4_integration.py
19 passed, 1 skipped in 27.72s                        # the four A-1: was 1 failed (blocked oracle 3) / 3 green / 1 owner-run skipped

$ python3 -m pytest -q tests/test_005_009_t2_opencode_adapter.py tests/test_005_009_t4_acceptance.py \
      tests/test_005_010_t2_load_mode_invocation.py tests/test_005_007_t5_delegation_dispatch.py \
      tests/test_004_002_t4_dispatch.py tests/test_006_002_u5_transport_equivalence.py \
      tests/test_006_001_t1_selection.py tests/test_006_003_u4_delegation_config.py \
      tests/test_006_003_u6_server_credential.py tests/test_006_003_u8_acceptance.py tests/test_packet_prepare.py
99 passed, 1 skipped in 213.79s (0:03:33)             # the declared regressions of the ficha

$ make validate
Assert PASS: 168
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL — run it directly to see details
```

**F011 is environmental and pre-existing** (already declared by U1a/U1b GREEN): `scripts/validate-subagents.sh` compares the repo against the operator's **real HOME installs** (`install.sh --check`, repo 82 files vs installed 86). This change installs nothing in HOME and cannot cause it; `u1a-green.md` proved it at the base commit with a detached worktree.

## 4. Flakiness

None reproduced. The known waiter flakiness the implementer declared under batch load (`'timeout' != 'completed'`) did **not** appear in my runs: the 99-test regression batch and the focal/A-1 runs were clean. Had it appeared, I would report it with its isolated run.

## 5. Honest notes

- Only `tests/` was edited and committed; the untracked `docs/planning/` and `findings/…` files are not mine and are untouched. No `--no-verify`, no `git stash`, no push.
- The probe lives in `/tmp/opencode/u1b-testfix2/` (not committed).
- No assertion of contract was changed: (1) still asserts acceptance by membership, (2) still asserts the kind derived from role+substage (`test-writer-role-report` / `role-report`), (3) still asserts config-wins + one record per dispatch. The three changes are test-side (fixture preconditions and oracle baselines), as the implementer's report requested.
- **Result:** the focal gate of U1b is now **13/13**, the four A-1 are **4/4** (the owner-run integration case skips as designed), and the declared regressions are green with no production change.

**Commit:** `b28be34` — `test: 006-005 U1b testfix 2 — attempt por iteracion, aprobacion del epic en el fixture, snapshot del ledger`