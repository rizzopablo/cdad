# review.md: `native-record-without-external-config-2026-11-20`, result review (round 2 of 2)

**Verdict: no blocking findings.** The product commit `5be4ff93` meets PC-1 through PC-9. The three test commits keep every original check and the same 36 test IDs. Two optional findings and one nit are left for you to prioritise. I don't approve the spec, deploy or publish anything.

## Intake
- I ran `cdad_packet.py intake --project-root <repo> --received docs/specs/native-record-without-external-config-2026-11-20/review-dispatch-001.txt` on the capture file. It returned rc=0, route C, with the packet and execution IDs matching.
- The capture file is identical to the dispatch I received. `spec.md` sha256 is `cb0ded8a…b97109c`, matching the contract.
- That check confirms the structure only, not where the capture came from.

## Evidence I collected
- **Files modified:** none. **Commit:** none. This review is read-only.
- **Diffs read:**
  - `git show 5be4ff93`
  - `git diff a7849e04 2140c64a -- tests/test_006_005_u1b_dispatch_entry.py`
  - `git show 5cc18b23 -- '*suite-inventory.json'`
  - The unchanged `cdad_delegate_opencode.py` `_run_observe` and `_surface_config` functions, and `correlate`.
- **Focused tests:** `timeout 900 python3 -m pytest -q -p no:cacheprovider tests/test_006_005_{u1b_dispatch_entry,u1a_runtime_config,u4_single_entry,reviewfix,u6fix4_native_selection,u6fix6_model_parity}.py` → **63 passed in 129.08s, rc=0**. This includes the configured-observation checks and the reference-text pins.
- **Test IDs:** I collected the u1b and u1a test IDs with `pytest --collect-only` and compared them with the test-writer's pre-change file `collect-before-parent-2f7e1d7f.txt`: 36 and 36, **identical**. Separately, the u1b test function names match the audit-approval baseline `a7849e04` (17 and 17, same names).
- **Original checks kept:** the u1b test diff only adds code. It adds sub-cases and helpers, adds log fields to the fixture, and gives the fixture an explicit rc=3 "observation unavailable" exit. No original assertion was removed or weakened.
- **Not run:** the full test suite. Feature close recommends it, so I record it as not run. The evidence above covers only the focused selection.

## Contract check (PC → product → test → result)

| PC | Product (`cdad_dispatch.py`) | Test that exercises it | Result |
|---|---|---|---|
| PC-1 | `record` loads its config with `optional=True`. A missing file, `runtimes` map or section becomes `{}` | PD-6 partitions: no file, no `runtimes` key, no section, empty map, empty section | Met |
| PC-2 | The existing `correlate(row=None)` gives session and model null, the note explains why, and the bytes are staged | PD-6: completed and staged, envelope and record session null, model null, provenance non-empty, exact bytes, no receipt, one attempt | Met |
| PC-3 | Observation runs only with a motive (session, parent or no payload) and calls the module once with the section, even `{}`. No check for `sessions_db` | PD-5 with empty map: one observe call, config passed and `== {}`, with native bytes. PD-6 with only `--since`: zero observe calls | Met |
| PC-4 | The module's rc≠0 answer becomes the reason recorded and named in the diagnosis. Nothing is copied into the accredited identity | PD-6 partitions with no store (fixture exits 3) | Met. The test only asserts the diagnosis is non-empty; the code shows it names the module and its error output |
| PC-5 | Unchanged path: `DispatchError` → blocked + none + null, no registration, no staging | PD-5 contradiction with native bytes, with config full, absent and empty map: blocked + none + null, the key named, one observe call, nothing written | Met |
| PC-6 | No payload and observation unavailable → error before registering. A missing, empty or directory `--native-result` → error | PD-4: unavailable observation fails with nothing written. The missing, empty and directory cases are errors. The unreadable regular file runs only when the OS user is actually denied | Met, but see limit L1 |
| PC-7 | When optional, a present path is read: invalid JSON or a directory → error, a non-object section → error, a forbidden key → error | PD-9 native: invalid JSON, a directory, a list section, a text section, a `model` key (message names `delegation.json`) | Met for what the spec lists. See finding F1 |
| PC-8 | The runtime module is resolved before the config is read | PD-9: an invalid ID and a missing module both fail with nothing written | Met |
| PC-9 | `dispatch` and `capabilities` still load the section the strict way, and `module_capabilities` is unchanged | `u1a` Pd8 and Pd9 tests pass | Met |

**Invariants:**
- Packet, suspension and continuity checks still run before any observation or new effect.
- The config is now read before those checks, but reading it writes nothing.
- No new receipt or approval path, no launch, and no inferred store location.

## Findings

### F1 — Optional: a malformed `runtimes` map or top-level document is quietly treated as "no config"
- **Verdict:** OPTIONAL · **Bucket:** m
- **Where:** `skills/cdad-cycle/scripts/cdad_dispatch.py:302-304` (`load_runtime_section`, optional branch).
- **Evidence:**
  - In this branch, valid JSON whose top level isn't an object (`[]` or `"x"`), or whose `"runtimes"` value isn't an object (`"runtimes": 5`), returns `{}`.
  - So native recording goes ahead with no observation config.
  - Only a non-object *section* is rejected.
  - The reference text (`cli-delegation.md:51-55`) says "an absent file, `runtimes` map or section is the empty configuration". It doesn't mention that a malformed map is also treated as absent.
  - The test-audit planned to cover "a non-object `runtimes` or section". The PD-9 sub-cases only cover a non-object section.
- **Effect under the contract:**
  - PC-7 lists unreadable or invalid JSON and a present non-object section, and forbids "broader schema validation". So this is a gap in the spirit of Promise C ("invalid configuration is [not] ignored"), not a broken PC.
  - What the user would see: a corrupted `runtimes` map makes the motivated observation run without `sessions_db`. The identity is then declared unverified (lower assurance, explicitly stated). It is never falsely accredited, and a contradiction is never turned into a missing-evidence result.
  - That outcome is the same as having no config at all, which the spec approves.
- **Suggested fix:** in the optional branch, when the file exists, reject a non-object document or a present non-object `runtimes` value with the same "present but is not an object" message. Add one PD-9 native sub-case for it.
- **Closes when:** that input exits nonzero with nothing written, or you accept the current behaviour as debt.

### F2 — FYI / Consider: the observation config no longer carries the `"runtime"` key
- **Verdict:** OPTIONAL · **Bucket:** h
- **Where:** `cdad_dispatch.py:715` (`with_runtime=False`) and `:363-378`.
- **Evidence:**
  - The temporary config passed to `--observe` used to include `"runtime": <id>`. It now doesn't, for every native observation, including the configured ones.
  - The only caller of `observe_model` is `record`. `dispatch` (line 661) and `capabilities` (line 1251) are unchanged.
  - The OpenCode module's `_run_observe` reads only `sessions_db`. Its `delegate` reads `runtime`, but that path doesn't use `--observe`.
  - The configured-observation tests (reviewfix, u6fix4, u6fix6) pass.
- **Effect:** none today. The only consequence is that a third-party runtime module that read `runtime` during `--observe` would no longer get it.
- **Why it changed:** the PC-3 test asserts the module receives exactly `{}`. The spec says "passing the available runtime section, including an empty `{}`", so the change is defensible. I record it so it doesn't go unnoticed, not as a defect.

### N1 — Nit: indentation drift in `suite-inventory.json`
- **Verdict:** OPTIONAL · **Bucket:** h
- **Where:** `docs/specs/008-002-suite-by-capability/suite-inventory.json`, commit `5cc18b23`.
- **Evidence:** the re-indented `"path"` line of `pd10_permission_semantics.py` and the new helper entries, plus the re-indented `product_staging.py` block, use one extra space.
- **Effect:** cosmetic only. The JSON stays valid, and the orchestrator reported the inventory check at rc=0.
- **The two new helpers are labelled honestly.** `tests/install_backup_oracle.py` and `tests/install_harness.py` are recorded with contract `VERIFY`, confidence `baja` (low) and a rationale that says outright they are not semantic protection evidence. I don't treat them as accredited, and they aren't.

## Test-mapping audit (independent; I'm not the test author)
- Every PC-1 to PC-8 claim in `test-audit.md` is actually exercised by the final tests, with the two exceptions below.
- The "unavailable observation" partitions really are unavailable: `fresh_project` deletes the store, and the fixture exits 3 naming the missing store. They don't fall back to the fixture's own store, which was the risk the audit flagged.
- **Exception 1:** non-object `runtimes` map (see F1).
- **Exception 2:** an unreadable *regular* file for `runtimes.json`. The test uses a directory instead. Both reach the same `OSError` handling, so I see no gap in behaviour.

## Limits
- **L1:** the PC-6 unreadable-regular-file case is skipped when the OS user can still read a chmod-000 file (a privileged user). I didn't check which branch ran in this run.
- These are fixture-based tests. There is no live OpenCode store and no runtime-compatibility claim, as the spec states.
- Full suite not run.

## Rounds
- Result-correction round 2 of 2, so the ceiling is used up.
- Nothing I found is blocking, so nothing reopens the correction loop.
- If you want F1 or F2 acted on, that needs your explicit decision or replanning. I can't authorise another round.

## Abstentions
- I abstain on whether the upstream native capture is genuine (out of scope under PC-2's limits).
- I abstain on whether the two `VERIFY` helpers truly belong to their proposed capability (`generation-install-permissions`), since no recoverable contract was available.

**For you to prioritise:** F1 (medium; a small fix to close Promise C fully, or record it as debt). F2 and N1 can be accepted as they are.
