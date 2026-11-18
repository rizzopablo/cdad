T4 RED is written and committed: `tests/test_019_002_resting_orientation.py`, revision `62224ee71fde12ee62774b99ead8b9d82db4bdac`. The first test passes as a control. The second fails with the intended `AssertionError`.

**Intake (Route C).** I validated REQUEST.json and PACKET.md with `cdad_packet.py validate-request`, `render --request` and `validate-packet`. The render is byte-identical to PACKET.md, and `spec.md` has the pinned sha256 `cd61455c…`.

**What I did and didn't touch.**
- I read no implementation code. I drove the real CLIs (`register-transition --transition closure`, `status`, `open-unit`) as black-box subprocesses on tempdir fixtures.
- Fixtures are reused from `tests/test_005_012_t1_register_transition_base.py`.
- No live project state was repaired. The only files I changed are this test and its commit.
- `docs/.cdad-state.json` was already modified and `recovery-delivery-green.md` is untracked; neither is mine and neither was committed.

**Reuse.** I took both tests from the retired orientation test (`215b0b52`) and reassessed them against the replacement PC-5, not the old scenario obligations. I tightened one oracle. "No `open-unit` recommendation" is now checked on `entry` and `next` only, not on the whole status text. A good diagnosis may say that `open-unit` refuses `done`/`null`.

**Tests and why they protect the promise (R4).** A user who completes a feature should get next-step orientation that `open-unit` doesn't immediately refuse.
1. `test_pc7_closure_status_recommends_open_unit_and_it_succeeds` is PC-5 and preserves current behavior. A real closure leaves `idle`/`null`, `status` gives `entry=next-unit` and names `open-unit`, and `open-unit` then opens the queued unit. It passes today. Without it, a fix could break the legitimate path or the closure effect and go unnoticed.
2. `test_pc7_done_null_state_gets_diagnosis_not_open_unit_and_no_mutation` is the pending PC-5 behavior.
   - `done`/`null` must not produce `entry=next-unit`, an `open-unit` next step, or a claim of rest. It must carry a diagnosis, and `status` must leave the state bytes unchanged.
   - Without it, `status` sends the user to an `open-unit` that then refuses them.
   - The test also checks that `open-unit` does reject `done`/`null`.

**Focal command and result.**
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests/test_019_002_resting_orientation.py
```
It gives 1 failed, 1 passed. The failure is an `AssertionError`, not an import or setup error:
`PC-5 violada: done/null no debe producir recomendación open-unit (entry/next): {"entry": "next-unit", "next": {... "verb": "open-unit"} ...}`

**Inventory and map delta.** I didn't edit docs, as the packet says. `python3 scripts/cdad-suite.py validate` now reports insufficient integrity, as expected until the orchestrator adds the entries. It lists the unlisted module and the two unmapped nodeids. The orchestrator needs to add to `suite-inventory.json`:
- A module entry for `tests/test_019_002_resting_orientation.py` with kind `test`, `static_test_nodeids: 2`, and product surface `skills/cdad-cycle/scripts/cdad_packet.py`.
- A provenance such as "019-002 recovery T4 RED, independent test-writer, 62224ee7; PC-5; reuses retired 215b0b52".
- The capability and contract for both nodeids, resting-orientation / recovery PC-5. I did not check which capability name the inventory expects.

In `pc-map.json`, map the two nodeids to PC-5 (recovery-spec). I didn't read `pc-map.json`'s schema.

**Limits.** No full suite was run. The tests don't check semantic fidelity of instructions, as instructed. They also don't re-test the active, suspended and pending-work distinctions; existing tests (`test_007_001`, `test_007_007`, `test_005_003_f2`) cover those and are unchanged.