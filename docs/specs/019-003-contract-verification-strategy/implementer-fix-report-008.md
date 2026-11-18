Both review-008 blockers are fixed. The product commit is `f8719500`. The evidence files are on disk but not committed, because `.cdad` is gitignored.

**Intake:** the Route C packet validated (`validate-packet` rc=0, and the `render --route C` output matches the dispatch).

**Blocker 1 (property-test exclusion):** I changed the sentence in `skills/cdad-cycle/references/stage-3-tdd.md` (sub-phase 3.4). It said sub-phase 3.4 "does not apply to code with many side effects or UI". It now says property tests are usually a poor fit for such code, but that is guidance for choosing the strategy at contract review. When the approved contract selects them, the sub-phase and its gate remain required. If the selected verification proves infeasible, the work stops and returns to contract review and approval. It is never waived silently. I searched the agents, sources and skills for the same contradiction and found no other copy. `CDAD_metodologia.md:1395` is general guidance, not a prohibition, so I left it.

**Blocker 2 (distribution evidence):** `run.sh` ran after all edits, against candidate `f8719500` and base `0b11b5fb`.
- `make staging` returned rc=0.
- An isolated `install.sh`, with `CDAD_INSTALL_ROOT` set to a temporary root, returned rc=0.
- I compared every agent and skill file changed between base and candidate with `cmp`: 69 comparisons, 0 differences. Agents were checked in both opencode and Claude Code, and skills at all three destinations.
- Staging matches the `agents/` copies.
- Nothing was deployed and the real installation is untouched.

**Tests:** 38 passed across `tests/test_cdad_generate.py`, `tests/test_010_001_documentary_contracts.py` and `tests/test_role_packet_render.py`. I did not run the full suite or `make validate`. I did not edit any tests.

**Evidence:** it is in `.cdad/orchestration/epic-019/019-003-review-fix-008-evidence/` (`run.sh`, `run.log`, `tests.log`, `REPORT.md`). Reproduce it with `bash .cdad/orchestration/epic-019/019-003-review-fix-008-evidence/run.sh 0b11b5fb` from the repo root.