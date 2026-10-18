Now let me check a couple of constraints before editing:
Now I'll make the edits to both adapter sources.
Evidence gathering and commit:
## Report — implementer / GREEN (`006-002-delegation-by-layer-implementer-green-004`)

### 1. Root cause (measured, not inferred)
- **A2:** the `delegation` section named the CLI as `` `cdad_packet.py render` `` — no derived skill-dir route. In the composed agent this lands as a wiring line without `<skill-dir>` (`agents/cdad-orchestrator.md:183`, `agents/claude-code/cdad-orchestrator.md:188`).
- **P1:** the section's receipt bullet restated the receipt steps (`receive` → `validate-receipt` → `materialize` → transition). Because the composed section is a **single paragraph unit** for the test's `units()` (bullets are not blank-line separated), that unit matched the `receive-staging` / `receive-receipt` groups and diverged from `sources/roles/orchestrator.md` (extra unit, e.g. `Mechanism (native).** First, resolve…`).

### 2. Minimum production change
`sources/agents/adapters/{opencode,claude-code}.md` §`delegation` (declared outputs regenerated):
1. **A2:** every CLI invocation now carries the derived route: `` `<skill-dir>/scripts/cdad_packet.py render` ``. (The adapter mention `` `cdad_delegate*.py` `` in the intra-runtime prohibition is a **program-family mention inside a prohibition, not an invocation** — no `.py` file token for the oracle, and A2 does not flag it; left untouched to keep the diff minimal.)
2. **P1:** the receipt bullet **stops restating** the steps — it points to (a) the re-entry wiring the orchestrator source already composes (naming the command, `.cdad/inbox` + `RESULT.json`, the single state transition) and (b) the installed `<skill-dir>/references/re-entry.md` "**Orchestrator materialization protocol**" — while **keeping** the U1-required link phrase and the receipt `semantic_status: pending` (approving nothing).

Regenerated with `make agents` (no hand-editing of `agents/**`).

### 3. Modified files (4; `git add` of exactly these)
| file | change |
|---|---|
| `sources/agents/adapters/opencode.md` | delegation: `<skill-dir>` route + receipt bullet rewritten |
| `sources/agents/adapters/claude-code.md` | same |
| `agents/cdad-orchestrator.md` | regenerated |
| `agents/claude-code/cdad-orchestrator.md` | regenerated |

Untracked `docs/planning/` and `findings/incremental-construction-and-reproducible-validation-2026-10-17.md` were **not touched nor staged**. `install.sh`, `scripts/cdad-models.sh`, `skills/cdad-cycle/scripts/cdad_delegate*.py`, `docs/adr/ADR-007*` and `tests/**` untouched.

### 4. Test → result
| test | before | after |
|---|---|---|
| `test_005_006_t6_owner_reviewfix.py::test_hallazgo_a2_cli_invocations_derived_from_skill_dir` | FAIL (AssertionError: `cdad_packet.py render` in both agents) | **PASS** |
| `test_003_006_t3_receive_wiring.py::T3AgentRegenerationCoherence::test_p1_regenerated_agents_reflect_source` | FAIL (AssertionError: divergence in `receive-staging` + `receive-receipt`) | **PASS** |
| gates: `test_006_002_u{1,2,3}*.py` + `test_005_004_t1_dispatch_tool_name` + `test_005_004_t4_cc_guard_decisions` + `test_005_005_t3_provenance` + `test_005_009_t3_spawn_reconciliation` + `test_005_010_t3_references` (+ the two oracles) | 2 failed / 78 passed | **80 passed** |
| every test reading generated orchestrators (`grep -l "cdad-orchestrator" tests/*.py` → 22 files) | — | **191 passed, 2 skipped** |
| `make agents` idempotence | — | `git diff --stat` **identical** before/after 2nd run |
| `make validate` | — | `validate-consistency.sh` **159 PASS / 1 FAIL = F011** (DT-8, environmental HOME drift, pre-existing/declared); `validate-odoo-specialization.sh` **67 PASS / 0 FAIL** |

### 5. Exact commands + output (verbatim excerpts)
```
$ python3 -m pytest tests/test_005_006_t6_owner_reviewfix.py::test_hallazgo_a2_cli_invocations_derived_from_skill_dir \
    "tests/test_003_006_t3_receive_wiring.py::T3AgentRegenerationCoherence::test_p1_regenerated_agents_reflect_source" -v
tests/test_005_006_t6_owner_reviewfix.py::test_hallazgo_a2_cli_invocations_derived_from_skill_dir PASSED [ 50%]
tests/test_003_006_t3_receive_wiring.py::T3AgentRegenerationCoherence::test_p1_regenerated_agents_reflect_source PASSED [100%]
============================== 2 passed in 0.08s ===============================

$ python3 -m pytest <006-002 u1/u2/u3 + 5 coupled modules + t6 + t3_receive_wiring> -q
80 passed in 11.29s

$ grep -l "cdad-orchestrator" tests/*.py   # 22 files
$ python3 -m pytest <those 22 files> -q
191 passed, 2 skipped in 78.37s (0:01:18)

$ make agents   # 2nd run
rc=0 ; git diff --stat identical → "IDEMPOTENT: git diff identical after second make agents"

$ make validate
Assert PASS: 159 / Assert FAIL: 1   → FAIL: F011: scripts/validate-subagents.sh (active profile)
Assert PASS: 67  / Assert FAIL: 0   → PASS: all postconditions P1..P6 and the A3 criterion verified.
```
F011 detail (`bash scripts/validate-subagents.sh`): `install.sh --check failed — drift .claude/agents/*, .config/opencode/agents/*, skills …` i.e. HOME-installed copies stale vs. repo (DT-8) — unrelated to this diff and matching the declared baseline in `u1/u2/u3-green.md` (159 PASS / 1 FAIL).

### 6. Commit (`git log --oneline -1`)
```
7d13a6d fix: 006-002 U1 regresiones A2 y P1 (sección delegation de los adaptadores)
 agents/cdad-orchestrator.md             | 21 ++++++++++++---------
 agents/claude-code/cdad-orchestrator.md | 21 ++++++++++++---------
 sources/agents/adapters/claude-code.md  | 21 ++++++++++++---------
 sources/agents/adapters/opencode.md     | 21 ++++++++++++---------
 4 files changed, 48 insertions(+), 36 deletions(-)
```
No `--no-verify`, no `git stash`, no push.

### 7. Honest limits
- No full suite run (declared full-suite policy: the closer runs it once). Proportional regression = the 22 orchestrator-reading modules + the declared coupled modules.
- The P1 green is textual/coherence evidence (generated agent ↔ role source); it is not a behavioural run of the orchestrator.
- `make validate` remains 159/1 by design: F011 = DT-8 environmental, pre-existing, out of this write scope.
