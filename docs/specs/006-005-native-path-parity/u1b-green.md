I've completed the implementation. Here is the role report.

---

# Role report — implementer, GREEN, `006-005-native-path-parity` / U1b

**Intake path:** validated canonical packet (`006-005-native-path-parity-implementer-green-002`). No full cycle/spec skill was loaded. Read: the approved spec (`docs/specs/006-005-native-path-parity/spec.md`, sha256 `3a824be3…` — matches the packet), `plan.md` §3 U1b, the RED report `u1b-red.md`, the four reformulated A-1 tests and the focal test (as the contract I implement — **never edited**).

**Definition of done: BLOCKED on three test-side oracles** (details in §4). The implementation is complete; the focal gate is 11/13 and 3/4 A-1 because those three oracles cannot pass for *any* implementation. I did not edit any test.

---

## 1. Modified files (commit `3af53f1`, no `--no-verify`, no stash, no push)

| File | Change |
|---|---|
| `skills/cdad-cycle/scripts/cdad_dispatch.py` | `+761/−…` — the verb zone: `dispatch` (external transport through the ONE implementation, relay of the module envelope, derived transient internal config, no registration, no staging), `record` (single body of observation + correlation with the §2.3 threshold + registration through the existing command + byte-exact staging with the derived kind), `capabilities` (the five keys of §2.2, fail-closed without the surface) |
| `skills/cdad-cycle/scripts/cdad_delegate.py` | `+…/−128` — its registration removed (`_observation`, `_register_dispatch`, its invocation, the now-dead `_now`/`delegation_model_provenance`/`uuid`/`datetime`); it **relays** the destination's `attempt`; CLI, internal `--exec-config` and the legacy-`model` deprecation notice preserved |
| `skills/cdad-cycle/scripts/cdad_delegate_opencode.py` | `+35/−…` — **only** the minimum for the module to declare in its envelope the `attempt` it registered (`_envelope(attempt=…)` + a local `envelope()` wrapper injecting the attempt); nothing of U2 |

```
$ git show --stat --format='' HEAD
 skills/cdad-cycle/scripts/cdad_delegate.py         | 128 +---
 .../cdad-cycle/scripts/cdad_delegate_opencode.py   |  35 +-
 skills/cdad-cycle/scripts/cdad_dispatch.py         | 761 ++++++++++++++++++++-
 3 files changed, 770 insertions(+), 154 deletions(-)
$ git status --short
?? docs/planning/
?? findings/incremental-construction-and-reproducible-validation-2026-10-17.md   # not mine, untouched
```

Nothing under `tests/**` was read-modified; `tests/.sensitive-patterns.local` and the user's real config/store were never touched; the real runtime was never launched (only fixture modules/stores in tempdirs).

**Contract points implemented:** §2.1 (surface, no `--exec-config`, envelope = `OUTPUT_KEYS`), §2.2 (module contract consumed; capability document; fail-closed window O-6), §2.3 (per-transport evidence; O-3 threshold; three outcomes, contradiction = rejection), §2.4 (per-path registration and `model_reported` source), §2.6 (derived transient internal config under `.cdad/`, deleted at the end, never model/credential), §2.8 (kind derived from role+subphase), PD-1/2/3/4/5/6/9(new verbs)/23(native), INV-1/2/5/8/10/14. `_allowed_kinds` untouched (U7).

## 2. Test → result

**Focal — `tests/test_006_005_u1b_dispatch_entry.py` (11 passed, 2 failed)**

| Test | Result |
|---|---|
| PD-1 external dispatch, one attempt relayed | ✅ |
| PD-2 record is not a second writer | ✅ |
| PD-3 byte-exact part + descriptor + `pending` receipt | ✅ |
| PD-4 no final text ⇒ no staging/descriptor/receipt | ✅ |
| PD-5 verified / O-3 `unknown` / contradiction rejection / outside-root rejection / packet without `agent` | ✅ (5) |
| PD-5 nested project by membership | ❌ **blocked oracle (1)** |
| PD-6 byte-exact result with unverifiable identity | ✅ |
| PD-9 `--exec-config` swept on `dispatch`/`record`/`capabilities` | ✅ (guard pre-satisfied by U1a) |
| PD-23 native kind derived | ❌ **blocked oracle (2)** (its test-writer/red half passes) |

**A-1 (the four reformulated tests)** — 3 green, 1 blocked:
`test_005_010_t1_durable_signal.py` ✅ · `test_005_010_reviewfix.py` ✅ · `test_005_010_t4_integration.py` ⏭ (owner-run, `CDAD_OPENCODE_INTEGRATION=1`) · `test_005_009_t1_interface.py` 3 passed / **1 blocked oracle (3)**.

**Declared regressions (15) — all green** (one file carries blocked oracle (3)):
`test_005_009_t2_opencode_adapter`, `test_005_009_t4_acceptance` (skipped: owner-run), `test_005_010_t2_load_mode_invocation`, `test_005_007_t5_delegation_dispatch`, `test_004_002_t4_dispatch`, `test_006_002_u5_transport_equivalence`, `test_006_001_t1_selection`, `test_006_003_u4_delegation_config`, `test_006_003_u6_server_credential`, `test_006_003_u8_acceptance`, `test_packet_prepare` → **97 passed, 1 skipped** (+4 flaky, §5) · `test_006_005_u1a_runtime_config.py` focals **19 passed**.
**Widened (shared interface, not in the declared list):** `test_006_001_t1b_service_mode`, `test_006_001_reviewfix`, `test_006_001_t2_wait_recovery`, `test_006_001_t3_concurrency`, `test_005_010_b1_last_assistant` → green (1 flaky, §5).

## 3. Commands and outputs (exact)

```
$ python3 -m pytest -q tests/test_006_005_u1b_dispatch_entry.py
2 failed, 11 passed in 30.74s
  FAILED …TestPd5NativeCorrelation::test_pd5_native_nested_project_is_accepted_by_membership
  FAILED …TestPd23NativeDescriptorKind::test_pd23_native_descriptor_kind_is_derived_from_role_and_substage

$ python3 -m pytest -q tests/test_005_009_t1_interface.py tests/test_005_010_t1_durable_signal.py \
      tests/test_005_010_reviewfix.py tests/test_005_010_t4_integration.py tests/test_006_005_u1a_runtime_config.py
1 failed, 37 passed, 1 skipped in 78.04s
  FAILED tests/test_005_009_t1_interface.py::TestPd8PortableExecConfigNotVpsValues::test_pd8_exec_config_portable_config_beats_product_no_host_values
  AssertionError: 0 != 1 : PD-1/D-14: el despacho dejó 0 registros I8 nuevos (se espera EXACTAMENTE uno…): []

$ python3 -m pytest -q <11 declared regression files + test_005_010_b1_last_assistant>   # batch A
4 failed, 97 passed, 1 skipped in 303.54s (0:05:03)     # the 4 are the known waiter flakiness, §5
$ python3 -m pytest -q tests/test_006_001_t2_wait_recovery.py tests/test_006_001_t3_concurrency.py
14 passed in 29.20s
$ make validate
Assert PASS: 168 · Assert FAIL: 1   → FAIL: F011
```

**F011 (environmental, pre-existing — same as U1a).** `make validate` fails only on `scripts/validate-subagents.sh (active profile)`: it compares the repo against the operator's **real HOME installs**; the direct run shows `❌ install.sh --check failed (rc=1)` (repo `skills/cdad-cycle` = 82 files vs installed 86). My change installs nothing in HOME and cannot cause it; U1a proved it pre-existing with a detached worktree at the base commit.

**Contract proof for the two blocked focal oracles (probes in `/tmp/opencode/u1b-probe/`, not committed):**
```
$ python3 /tmp/opencode/u1b-probe/probe_pd5_membership.py
directory: …/project                    rc: 0 | new records: ['att-x']
  stdout: {"attempt": "att-x", …, "diagnosis": "verified: the observable row of the module's single
          store read matches the declared evidence (project) — the session comes from the store…"}
directory: …/project/nested/deep        rc: 1 | new records: []
  stderr: cdad_dispatch: the attempt 'att-x' could not be registered: ERROR: attempt 'att-x' already
          exists with different observation data: refusing to overwrite a dispatch record …
# control: the SAME nested-directory case with a DISTINCT attempt id
control (nested directory, distinct attempt id) rc: 0
  persisted session: ses-native | provenance.session: verified: the observable row … (project)
```
```
$ python3 -c "…; d.derive_artifact_kind(role, substage) …"
test-writer/red -> test-writer-role-report   test-writer/audit -> test-audit
architect/draft -> role-report               architect/discovery -> role-report
implementer/green -> implementer-role-report reviewer/plan-review -> plan-review   reviewer/review -> review
scribe/memory -> DispatchError (needs U7/PD-26: declared dependency, table untouched)
```

## 4. The three blocked oracles (evidence + minimal correction) — I did not edit any test

**(1) `test_006_005_u1b_dispatch_entry.py::TestPd5NativeCorrelation::test_pd5_native_nested_project_is_accepted_by_membership` (PD-5/INV-15).**
The subTest loops over two directories **in the same project with the same `ATTEMPT_PD5`** and then asserts `single_record(before)` ⇒ *exactly one NEW record per iteration*. The project's ledger name is that attempt (PD-4 asserts the stem is it), and the ledger refuses to overwrite an attempt with different data — a contract tested elsewhere (`tests/test_004_002_t34_reviewfix3.py:186`: "repetir un registro idéntico es idempotente"; different data is refused). So iteration 2 can never yield a new record (probe above: `new records: []`, rc=1). The **contract** is satisfied — the control with a distinct attempt id accredits the session by membership (`§2.3/INV-15`). *Minimal correction:* give each iteration its own attempt id (or its own project) in the test.
**(2) `…::TestPd23NativeDescriptorKind::test_pd23_native_descriptor_kind_is_derived_from_role_and_substage` (PD-23/§2.8).**
Its second half builds an architect packet, but the fixture cannot publish it — a **fixture precondition**, independent of the implementation:
```
$ python3 /tmp/opencode/u1b-probe/probe_pd23.py     # exactly what the test's new_project does
rc: 2
stderr: CDAD prepare: unit contract fallback: no table row contains the feature id
  '004-002-project-execution-bootstrap' as a complete token in docs/epics/epic-004-single-source-planning/plan.md …
ERROR: approval pending: … epic_history has no entry with epic 'epic-004-single-source-planning', stage
  'epic-plan' and a non-empty approved_by (plan del epic) (PD-1/PD-2).
```
*Minimal correction:* inject the `epic-plan` approval into the fixture state (precedent `tests/test_005_001_t4_decisive.py:264`) and write the plan table row with the feature id.
**(3) `tests/test_005_009_t1_interface.py::TestPd8PortableExecConfigNotVpsValues::test_pd8_exec_config_portable_config_beats_product_no_host_values` (A-1).**
Two independent defects, both test-side: (a) `records_mid` is snapshotted **after** `proc_two`, the very invocation whose "exactly one new record" it then counts — the set is always empty (`0 != 1` for any implementation, before any further assertion); (b) the fixture stub declares a **constant** `_ATTEMPT` for both dispatches of the case, and the second one carries a different `runtime`, so the ledger refuses it (probe: `rc=2 … already exists with different observation data`), which also makes `assertNotEqual(record_two, record_one)` unreachable. *Minimal correction:* snapshot the ledger **before** `proc_two` **and** make the stub's attempt id per-invocation (e.g. derived from the config runtime), or use two projects.

**Not a contradiction of the spec, so I did not apply a workaround:** inventing an auto-disambiguated attempt id in `record` would satisfy (1) only by hiding a real ledger conflict ("fail loud"), and (2)+(3) are unreachable from the implementation side — a testfix round is required anyway. I stopped and reported instead, as my role requires.

## 5. Flakiness declared (not hidden)

Four tests failed once **under batch load** and pass in isolation — the waiter-margin flakiness already documented in the RED report (`u1b-red.md` §5) and in `test_005_009_t2_opencode_adapter.py`:
```
$ python3 -m pytest -q <the 4 failing tests>          # isolated
4 passed in 8.86s
$ python3 -m pytest -q "…t1b_service_mode…test_pd13_no_management_invocations_in_any_mode"
1 passed in 1.76s     # failed once in a 20-test batch with "did not answer within 2.0 seconds"
```
They are `'timeout' != 'completed'` on the fake runtime's wall-clock margin; my change touches neither the wait nor the timing.

## 6. Design decisions worth the reviewer's attention (outside the tests)

- **The transport is not reimplemented**: `dispatch` calls `cdad_delegate.delegate` (one implementation of launch/wait/collect/byte-identical transport), since a second one could diverge (§12).
- **The derived internal config carries `runtime=<id>`** in addition to the §2.6 section keys: it is the value of `--runtime`, never read from a project document, and the module's internal contract reads it for the observation's `runtime` (the `runtimes.json` *section* still has no `runtime` key).
- **`record` requires the runtime module and its section** (the store is the only correlation source, INV-12); a section-less invocation fails closed with the PD-9 diagnostic.
- **Store read motive (§2.1/PD-13):** one bounded read (`--observe`, timeout from the section's `wait`, default 30 s) only when the invocation declares correlation inputs (`--session`/`--parent`) or there is no byte-exact native result; the provenance says which case applies. Rejection (contradiction) and `unknown` are decided **before** any registration or staging.
- The report file was **not** written under `docs/` — the packet's `write_scope` declares only implementation roots + `install.sh`; the orchestrator materializes it (as with `u1a-green.md`).

## 7. Commit

```
3af53f1 feat: 006-005 U1b GREEN — entrada única y registro único
 3 files changed, 770 insertions(+), 154 deletions(-)
```
Message states the change and — honestly — the three blocked oracles with their evidence summary. No `--no-verify`, no stash, no push.

**Requested decision:** a **testfix** for (1), (2) and (3) by the test-writer (regenerate the RED/patch the same A-1 scope), after which the focal gate is expected to be 13/13 and A-1 4/4 with the implementation already committed; no production change should be needed for (1)–(3).