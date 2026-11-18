T2 (PC-7) is implemented and committed as `c11825b4`, and the T2 tests plus the proportional regression pass. I did not run the full suite.

**Packet check:** I validated the packet by route C. The metadata and `contract.sha256` match, and the `PACKET.md` bytes are identical to `cdad_packet.py render`.

**Before the change:** `test_pc7_done_null_state_gets_diagnosis_not_open_unit_and_no_mutation` failed, because `status` answered `entry=next-unit`, `situation=at-rest` and named `open-unit` for a `done`/null state.

**Changes (all in `skills/`):**
- `skills/cdad-cycle/scripts/cdad_packet.py`: in `status_view`, when the entry is `next-unit`, `status` now runs `_validate_idle_coherence`, the same check `open-unit` uses. If that check raises, the entry becomes `diagnosis` and the error text goes into `unknowns`. `status` recommends no `open-unit`, makes no at-rest claim and writes no state. Active, suspended and pending-work states don't reach this branch, so their handling is unchanged.
- `skills/cdad-cycle/references/stage-5-merge.md`: closure now sets `current_stage: idle` instead of `done`, with `active_feature: null`.
- `skills/cdad-epic/references/feature-handoff.md`: the re-entry check now looks for `idle`/null.
- `skills/cdad-cycle/references/state-detection.md`: `done` is removed from the stage enum, the closure row now reads `idle` with `active_feature: null`, and the closure wording is updated.

**Commands and results:**
- `python3 -m pytest tests/test_019_002_resting_orientation.py tests/test_005_001_t3_idle.py tests/test_005_003_t1_compact_view.py tests/test_005_007_t3_open_unit.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_007_001_unambiguous_entry.py tests/test_007_007_suspend_resume_units.py tests/test_005_003_f2_idle_history.py -q` gave 105 passed in 179.57s. This is the T2 focal test, the four declared regressions, and the three active/suspended/pending protection tests named in the test header.
- I also ran the four tests that reference the edited reference docs (`tests/test_005_005_t2_docs_policy.py`, `tests/test_005_006_t1_start_procedure.py`, `tests/test_006_004_u4_decisions_table.py`, `tests/test_014_001_suite_evidence_defaults.py`). They gave 34 passed.

**Limitations:**
- Complete suite not run: this is a task-level close inside the feature, and I ran the focal tests plus the proportional regression.
- I did not edit any tests, and I did not install or deploy anything.
- `docs/.cdad-state.json` was already modified before I started and is outside my write scope. I left it untouched and uncommitted.