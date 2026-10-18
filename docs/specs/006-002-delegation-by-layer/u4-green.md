I'll start by reading the approved spec and the RED tests to understand the contract.
Now I'll make the edits to `SKILL.md` §2:
Now the concrete model example in `handoff-prompts.md`:
U4 GREEN complete. Report below.

## Changes (2 files, both in write scope)

| File | Change |
|---|---|
| `skills/cdad-cycle/SKILL.md` §2 (`:67-82`) | Dropped the **`Model family`** column from the roles-contract table (all 7 model cells) and the **profiles paragraph** (`:77`). Added one **`Models.`** paragraph: the model of each role is the one configured in the runtime; the skill names no model and fixes no family; the reviewer's different family from the implementer's is an **invariant**, guaranteed by configuration when the profile fixes models and **declared** when it does not; how it is declared belongs to the `delegation` section of each runtime's orchestrator. Reworded the anti-bias line so it no longer reads "model family" (it said *"the reviewer uses a model family different from the implementer's"*). |
| `skills/cdad-cycle/references/handoff-prompts.md:516` | `Reviewer model: <model declaration, e.g.: mofgw/qwen3.7-plus>` → `<model declaration — the model configured for the reviewer in the runtime>` |

Nothing else touched: `tests/**`, `install.sh`, `scripts/cdad-models.sh`, the profile map, ADR-007, `re-entry.md`, context rules, `docs/planning/`, `findings/` are all untouched (`git status` shows only the two files modified; the two untracked entries remain untracked and unstaged).

No approved oracle fixes models in `SKILL.md`: the generator composes the orchestrator §2 from `sources/roles/*.md` (`scripts/cdad-generate.py:799`) and **never reads SKILL.md** (`grep -n "SKILL.md" scripts/cdad-generate.py` → no match); the only tests carrying those model-name lists (`tests/test_cdad_generate.py:49-54`, `tests/test_004_001_t6.py:86-91`) are **absence** oracles over generated Claude Code artifacts, and F001's §2 asserts were reformulated in the RED.

## Test → result

| Test / gate | Before | After |
|---|---|---|
| `test_006_002_u4_skill_without_models.py` (5) | 5 FAIL | ✅ 5 pass |
| `test_006_002_u2_neutral_skill.py` (4) | 1 FAIL (models half) | ✅ 4 pass |
| `test_006_002_u1_delegation_section.py` (10) | pass | ✅ 10 pass |
| `test_006_002_u3_runtime_references.py` | pass | ✅ pass |
| `test_005_004_t1`, `t4`, `test_005_005_t3`, `test_005_009_t3`, `test_005_010_t3` | pass | ✅ pass (65 pass in the combined run) |
| every test reading SKILL.md (`grep -l "SKILL.md" tests/*.py` → 18 files) | pass | ✅ 102 + 5 + 65 pass (ran in 3 chunks; `test_install_review5_regressions.py` 5 pass) |
| F001 (reformulated) | FAIL (new sentence) | ✅ 4/4 new asserts pass + 9 conservation asserts pass |
| F011 (DT-8) | ⚠️ FAIL pre-existing | ⚠️ **still FAIL** — pre-existing environmental drift, not caused by U4 (proof below) |

## Exact commands and output

```
$ python3 -m pytest tests/test_006_002_u4_skill_without_models.py tests/test_006_002_u2_neutral_skill.py -q
.........                                                                [100%]
9 passed in 0.17s

$ python3 -m pytest tests/test_006_002_u1_*.py -q
..........                                                               [100%]
10 passed in 1.46s

$ python3 -m pytest tests/pd10_permission_semantics.py tests/test_003_006_t{1,2,3}_*.py \
    tests/test_004_003_t5_reentry_equivalence.py tests/test_005_005_t2_docs_policy.py \
    tests/test_005_006_t{1,2,6}_*.py tests/test_005_009_t{1,2}_*.py \
    tests/test_role_packet_review_regressions.py -q
102 passed in 70.46s

$ python3 -m pytest tests/test_install_review5_regressions.py -q
5 passed in 69.14s

$ python3 -m pytest tests/test_006_002_u{2,3,4}_*.py tests/test_005_004_t1_dispatch_tool_name.py \
    tests/test_005_004_t4_cc_guard_decisions.py tests/test_005_005_t3_provenance.py \
    tests/test_005_009_t3_spawn_reconciliation.py tests/test_005_010_t3_references.py -q
55 passed in 6.95s

$ bash tests/validate-consistency.sh   (log: /tmp/opencode/u4-validate.log)
PASS: F001 (006-002 PD-11): SKILL.md §2 declares the model of each role is the configured one
PASS: F001 (006-002 PD-11): SKILL.md §2 declares the skill names no models
PASS: F001 (006-002 PD-11): SKILL.md §2 declares the reviewer family invariant is guaranteed by configuration (when the profile fixes models)
PASS: F001 (006-002 PD-11): SKILL.md §2 declares the reviewer family invariant when the profile does not fix models
PASS: F001: agents/cdad-orchestrator.md caveats the anti-bias invariant for the basic profile
PASS: F001: agents/claude-code/cdad-orchestrator.md caveats the anti-bias invariant for the basic profile
PASS: F011: tests/validate-odoo-specialization.sh → PASS
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
Assert PASS: 161 / Assert FAIL: 1
```

## Commit

```
$ git show --stat --oneline HEAD
8c05755 feat: 006-002 U4 GREEN — SKILL.md §2 sin modelos (PD-11)
 skills/cdad-cycle/SKILL.md                      | 33 ++++++++++++++-----------
 skills/cdad-cycle/references/handoff-prompts.md |  2 +-
 2 files changed, 20 insertions(+), 15 deletions(-)
```
No `--no-verify`, no `git stash`, no push. `git status --short` after the commit: only the two untracked entries that are not mine.

## Blocks / honest findings (orchestrator decides)

1. **F011 cannot be met by any repo-only change — pre-existing, environmental.** `scripts/validate-subagents.sh` ends in `install.sh --check`, which compares the *installed* copies under `~/.claude`, `~/.config/opencode`, `~/.agents` against the working tree. It already failed at RED/HEAD for files U4 never touched — proof without reverting: `git show HEAD:skills/cdad-cycle/references/sub-agent-strategies.md | diff - ~/.claude/skills/cdad-cycle/references/sub-agent-strategies.md` is non-empty (and same for `~/.config/opencode/...`, and for `agents/cdad-orchestrator.md`), and the drift list also reports `cli-delegation.md`, `progress-guards.md`, `runtime-adoption.md` (U3 surfaces) plus `skills/cdad-cycle has 84 file(s), installed has 86` (the two withdrawn runtime references still installed). Those installs predate U1/U3 GREEN. Repair requires re-installing into HOME (outside my write scope) — I did not touch it. The SKILL.md content drift I introduced is additive to an already-failing check.
2. **Residue of INV-2 outside this unit's RED (not fixed, by design).** `skills/cdad-cycle/references/sub-agent-strategies.md:51` still names concrete Claude aliases and a gateway token: *"`model:` accepts aliases (`haiku`, `sonnet`, `opus`, `fable`) or a full model ID — there is no `mofgw` gateway"*. U2's shared oracle returns `[]` and U4's embedded-version oracle returns `[]` for it (`CONCRETE_MODEL_ID_RE` needs family+dash, `SPACED_MODEL_LINE_RE` needs a digit, `PROVIDER_RE` has no `mofgw`). Both gates are green, and the objective said to generalize only what U2's test finds — so I left it rather than silently expanding the diff. Flagging it as a possible INV-2 gap on the U2/U3 surface if a stricter oracle is ever written.
3. **`make agents` deliberately not run**: the packet requires `make validate`, not regeneration; running it would rewrite `agents/**` from `sources/**` (U5-U8 pending) and add diffs unrelated to U4. The generator does not read `SKILL.md`, so §2 edits cannot desynchronize the generated agents (F001's agent-side asserts pass unchanged).
