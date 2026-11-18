Status: the change is made and committed. I'm sending the final evidence now.

**FINAL TEXT**

- **Packet check:** I read the Route C identification and the packet's REQUEST.json and PACKET.md. I did not run `cdad_packet.py render` to compare the packet against the canonical render. That validation step is not done.
- **Modified file:** `skills/cdad-cycle/scripts/cdad_packet.py`, 11 lines added and none removed. No tests, docs or instructions were touched.
- **Change:** `status_view` now runs `_validate_idle_coherence`, the same check `open-unit` uses, whenever the entry would be `next-unit`.
  - If it raises `PolicyError`, the entry becomes `diagnosis`. The route carries the error text, which says "state incoherent …" and names the repair. The same text is added to `unknowns`.
  - A `done`/`null` state therefore gets no `open-unit` recommendation and no `at-rest` claim.
  - `status` stays read-only, and I added no new state vocabulary.
  - A legitimate `idle`/`null` closure still gets `next-unit`.
- **Commands run:**
  - Focused run before the edit: `python3 -m pytest tests/test_019_002_resting_orientation.py -q` gave 1 failed, 1 passed.
  - Regression after the edit: `python3 -m pytest tests/test_019_002_resting_orientation.py tests/test_005_001_t3_idle.py tests/test_005_003_t1_compact_view.py tests/test_005_007_t3_open_unit.py tests/test_005_012_t3_closure_dispatch_resolution.py tests/test_007_001_unambiguous_entry.py tests/test_007_007_suspend_resume_units.py tests/test_005_003_f2_idle_history.py -q -p no:cacheprovider` gave **105 passed in 193.30s**. The first attempt hit the default 120s timeout, so I reran it with a longer one.
  - The last two files in that list are the active, suspended and idle-history status regressions.
- **Commit:** `02ff945a` — "feat: status applies resting-coherence before recommending open-unit (019-002 PC-5)". It contains only `packet.py`.
- **Full suite:** not run (suite completa no realizada). The executed selection is the eight test files above.