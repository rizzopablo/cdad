I'll start by reading the approved contract spec and the RED tests.
Now let me look at the reformulated tests and the current source files.
Let me examine the RED commit diff and the reformulated tests.
Let me read the other reformulated test diffs and the current source files.
Now let me read the source files that need editing.
Let me read the shared test helpers and the full §2 region.
Let me run the focal test to capture the RED baseline.
Baseline confirmed (7 failures). Now implementing. First, SKILL.md §2:
Now the OpenCode adapter delegation bullet:
Now the generator's `model_note()`:
Now the role sources:
Now regenerate and check for any remaining profile vocabulary:
Focal green. Now the coupled/reformulated tests (fast ones first):
Now the staging-based coupled tests (slow):
Now the full gate test set (every test reading SKILL.md or generated orchestrators):
All 315 pass. Now verify `make agents` idempotence (two runs, no diff):
Now `tests/validate-consistency.sh`:
The legacy F001 check trips on a line starting with `model:`. Let me reword to avoid that:
Only the declared-environmental F011 remains. Let me confirm its nature:
Confirmed F011 is HOME-installation drift (environmental, declared). Now re-run the full gate set after the final regeneration:
All green. Idempotence check + final focused/coupled run for the evidence table:
Now inspect the diff scope before committing:
All within write scope, no tests touched. Let me check for pre-commit hooks, then commit:
Commit created. Final state verification:
## Role report — implementer / GREEN · 006-003 U3

**Contract:** `docs/specs/006-003-installer-single-profile-delegation-config/spec.md` (sha256 `32ed55c4…`) — PD-7a/PD-7b, INV-3/INV-4/INV-5. Packet `006-003-…-implementer-green-003`.

### Modified files (31, all in write scope; no `tests/**`, no `install.sh`, no delegation scripts)
| Area | File |
|---|---|
| Skill text | `skills/cdad-cycle/SKILL.md` (§2 "Models" paragraph) |
| Generator | `scripts/cdad-generate.py` (`model_note()`) |
| Adapters | `sources/agents/adapters/opencode.md`, `claude-code.md` (delegation §) |
| Role sources | `sources/roles/{architect,implementer,reviewer,scribe,test-writer}.md` |
| Regenerated | `agents/cdad-*.md` + `agents/claude-code/cdad-*.md` (22 files, via `make agents`) |

Change: the reviewer's different family is no longer profile-conditioned — it is a **configuration verification** ("the effective models are compared from the configuration") and, when not verifiable, is **declared** «invariant not guaranteed» at the review gate (never silent). `--basic`/profile vocabulary and the retired `scripts/cdad-models.sh` name are gone from the composed installable text. No verification-script path was named (U5).

### Test → result
| Test | Before (RED) | After (GREEN) |
|---|---|---|
| `test_006_003_u3_texts_without_profiles.py` | 7 failed, 3 passed | **10 passed** |
| `test_006_003_u1_generator_without_profiles.py` | — | passed |
| `test_006_003_u2_installer_without_profiles.py` | — | passed |
| `test_006_002_u1_delegation_section.py` | 2 failed | passed |
| `test_006_002_u2_neutral_skill.py` | — | passed |
| `test_006_002_u3_runtime_references.py` | — | passed |
| `test_006_002_u4_skill_without_models.py` | 2 failed | passed |
| `test_006_002_u5` / `u6` | — | passed / passed |
| `test_005_010_t3_references.py` | — | passed *(reformulated pointer assert inverted)* |
| `validate-consistency.sh` F001 / F008 | F001 failed | **passed** |

### Exact commands & outputs
```
$ python3 -m pytest tests/test_006_003_u3_texts_without_profiles.py -q
..........  [100%]   10 passed in 0.13s

$ python3 -m pytest <focal + coupled reformulated set> -v
============================= 65 passed in 43.64s ==============================

$ FILES=$(grep -l "SKILL.md\|cdad-orchestrator" tests/*.py)   # 39 files
$ python3 -m pytest $FILES -q
315 passed, 2 skipped in 384.52s (0:06:24)

$ make agents && make agents          # idempotence
IDEMPOTENT (run1==run2)               # sha256 snapshot of agents/ + build/staging: no diff

$ bash tests/validate-consistency.sh
Assert PASS: 166
Assert FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```
F011 confirmed environmental: `scripts/validate-subagents.sh` reports drift of the **HOME installation** (`<home>/.claude/…`, `<home>/.config/opencode/…`, `<home>/.agents/…`) — declared as the accepted HOME-drift failure in the packet gate. No other oracle requires profiles.

### Notes
- One legacy F001 assert (`extract_role_contract | grep '…|model:'`) tripped when the adapter bullet wrapped a line to start with `model:`; reworded to "…selects a model. It passes…" (behaviour unchanged, character-level only).
- Untracked `docs/planning/` and `findings/…md` were **not** touched/staged.

### Commit
```
2b1b597 feat: 006-003 U3 GREEN — installable texts without profiles or models (PD-7a/PD-7b, INV-3/4/5)
31 files changed, 111 insertions(+), 80 deletions(-)
```
No `--no-verify`, no `git stash`, no push. `git show --name-only HEAD` contains **no** `tests/` path.
