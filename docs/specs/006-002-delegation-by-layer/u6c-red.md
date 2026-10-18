I'll start by reading the approved contract (spec) and the target test file.
Now I'll rewrite the module: replace the amendment-001 rule-4 tests with the amendment-002 versions (stable workspace paths + no `/tmp` in installable text).
RED observed. Now let me record the exact observed offenders in the module docstring.
RED complete and committed. Role report below.

## Role report — test-writer / RED (packet `006-002-delegation-by-layer-test-writer-red-009`)

### Files
| File | Change |
|---|---|
| `tests/test_006_002_u6_context_discipline.py` | modified (only file in the diff; 153+/271−) |

Commit: **`300a05c`** — `test: 006-002 enmienda 002 RED — regla 4: rutas estables del workspace y ausencia de /tmp en texto instalable`
Diff bounded to `tests/`: `git diff --name-only` → `tests/test_006_002_u6_context_discipline.py`. Untracked `docs/planning/` and `findings/…` left untouched (not mine).

### What changed (amendment 001 → amendment 002)
Read `docs/specs/006-002-delegation-by-layer/spec.md` (incl. **«Enmienda 002»**, approved 2026-10-17) and the test scope only. Assertions derive from the spec text, not from the tree.

- **Removed** the three amendment-001 rule-4 oracles and all their now-dead machinery (`TMP_PERMISSION_RE`, `EPHEMERAL_DRAFT_RE`, `SAME_PROCESS_RE`, `TMP_PROHIBITION_RE`, `PROHIBITIVE_RE`, `TMP_AS_PLACE_RE`, `CROSS_PROCESS_ROLE_RE`, `ARTIFACT_RECEIPT_EVIDENCE_RE`, `absolute_tmp_prohibitions()`, the `/tmp`-mention group of rule 4, the unused `require_any` import).
- **(a)** New `TestPd6Rule4StableWorkspacePaths::test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths` — in **both** generated orchestrators (staging `basic`): what must last / leave evidence / be read by another process or role → **stable workspace paths**, co-located with **`.cdad/inbox`** for the receipt. Concepts with alternatives; no `/tmp` group (amendment 002 removes it).
- **(b)** New `TestPd6NoTmpInInstallableText::test_pd6_no_installable_text_names_tmp` — no installable text (`skills/**`, generated `agents/**`, and the generated agents in staging `basic` `build/staging/agents/**`) names `/tmp`, neither to forbid nor to admit it (word-boundary token, so `.cdad/tmp`/`temporary` don't match).

### Test → postcondition map
| # | Test | PD |
|---|---|---|
| 1 | `TestPd6Rule1OrientationFirst::test_pd6_rule1_orient_first_with_the_compact_status_view_without_dumps` | PD-6(1) |
| 2 | `TestPd6Rule2SessionRotation::test_pd6_rule2_rotate_the_session_at_task_boundaries_not_mid_unit` | PD-6(2) |
| 3 | `TestPd6Rule3NoSelfRepair::test_pd6_rule3_no_self_repair_redispatch_the_role_naming_the_defect` | PD-6(3) |
| 4 | `TestPd6Rule4StableWorkspacePaths::test_pd6_rule4_durable_evidence_and_cross_role_reads_go_to_stable_workspace_paths` | PD-6(4)/INV-4 (enmienda 002, (a)) |
| 5 | `TestPd6OrientationOwnerCited::test_pd6_orchestrators_reference_the_view_first_owner` | PD-6 (cita, no duplica) |
| 6 | `TestPd6NoTmpInInstallableText::test_pd6_no_installable_text_names_tmp` | PD-6(4)/INV-4 (enmienda 002, (b) — oráculo de ausencia) |

Docstrings carry `PD-6 (enmienda 002)` as required.

### Commands and output
```
$ python3 -m unittest tests.test_006_002_u6_context_discipline -v      # rc=1
Ran 6 tests in 1.521s
FAILED (failures=1)

FAIL: test_pd6_no_installable_text_names_tmp
AssertionError: Lists differ: ["skills/cdad-cycle/SKILL.md:174 → **Conte…"] != []
First list contains 6 additional elements. : PD-6(4)/INV-4 (enmienda 002): texto
instalable que nombra `/tmp` …: [
  'skills/cdad-cycle/SKILL.md:174 → **Context discipline (pointer).** …',
  'skills/cdad-cycle/references/handoff-prompts.md:628 → - Run logs named under ~/tmp/ (never /tmp/) …',
  'agents/cdad-orchestrator.md:102 → - **`/tmp` only for ephemeral drafts of one same process.** …',
  'agents/claude-code/cdad-orchestrator.md:107 → - **`/tmp` only for ephemeral drafts of one same process.** …',
  'staging-basic/build/staging/agents/claude-code/cdad-orchestrator.md:106 → …',
  'staging-basic/build/staging/agents/opencode/cdad-orchestrator.md:102 → …']
```
Test 6 fails **by content assertion** (AssertionError), never ImportError/SyntaxError/fixture error. Tests 1–5 are pre-satisfied conservation guards (declared in the module docstring, same convention as U1–U5): rules 1–3 and the `.cdad/inbox`/stable-paths half already exist; amendment 002 only removes the `/tmp` mention from installable text.

```
$ grep -rn "/tmp" tests/*.py tests/*.sh        # requested by the packet
```
No other test requires a `/tmp` mention in installable text — the remaining hits are `temporary_roots`/tempdir fixtures, path-policy absolute paths, and docstrings of the tests themselves (`test_006_002_u5…:7`, `test_004_001_acceptance_matrix.py:32`, `test_005_007…:96`, `test_005_002…:348`). **Nothing else reformulated** (the packet's conditional is not triggered).

Regressions declared by the U6 ficha:
```
$ python3 -m pytest tests/test_005_009_t3_spawn_reconciliation.py -q   → 19 passed
$ bash tests/validate-consistency.sh                                   → Assert PASS: 161 / FAIL: 1
FAIL: F011: scripts/validate-subagents.sh (active profile) → FAIL
```
F011 is **pre-existing and out of my scope**: it validates `sources/agents` via a script, and my diff touches no `skills/`, `agents/`, `sources/` or `scripts/` file (`git diff --name-only` = the one test file). Not run as the full suite (full-suite policy: the closer runs it once at closure).

### Honest declarations (PD-15)
- **Phase isolation:** I did not read implementation code to derive any assertion. One declared deviation: I ran `grep -rln "/tmp" agents skills` (filename-only listing, no content) merely to know whether the new absence oracle would fail by assertion — it did not inform the oracle, which comes from the spec text.
- The `/tmp` occurrences inside the tests themselves (docstrings/comments) are not touched, per the packet.
- Honest limit recorded in the module: the oracle proves the rule **exists** and that `/tmp` is **not named**, not that the rule is obeyed (behavioural evidence is only the U8 acceptance transcript, a sample).
