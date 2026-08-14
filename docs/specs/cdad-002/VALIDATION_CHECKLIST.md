# CDAD-002 Validation Spike — Execution Checklist

**Reference:** Comprehensive checklist + probe script for running the CDAD-002 validation spike.

This document is for **manual execution after Phase 5 (install.sh) completes**. It guides you through the 5 stages of the validation spike and captures evidence.

---

## Pre-Flight

### 1. Install Agents & Guard Script

Run the installer **for real** (not dry-run) — this makes the agents available:

```bash
cd /path/to/project
bash install.sh --optimus   # or --economical, --premium
```

Verify installation:

```bash
# OpenCode agents
ls -la ~/.config/opencode/agents/cdad-*.md | wc -l     # expect 6

# Claude Code agents
ls -la ~/.claude/agents/cdad-*.md | wc -l              # expect 5

# Guard script
test -x ~/.claude/cdad-scripts/path-guard.sh && echo "Guard script OK"

# Skills
ls -la ~/.claude/skills/cdad-cycle && echo "Skills OK"
```

### 2. Start a Claude Code Session

Launch Claude Code CLI or open the Claude Code UI:

```bash
claude --agent cdad-orchestrator    # Optional: use orchestrator as primary agent
# or just start a fresh session
```

### 3. Bootstrap State File

In your Claude Code session, run the `cdad-cycle` skill to create the state file:

```
(in Claude Code chat)
Load the cdad-cycle skill and initialize CDAD-002.
```

The skill will create `docs/.cdad-state.json` with:

```json
{
  "feature_id": "cdad-002-validate-claude-code-subagents",
  "stage": 1,
  "substage": null,
  "tdd_substage": null
}
```

---

## Stages 1-5: Execute by Role

For EACH stage, use the patterns below.

### Stage 1: Discovery

**In Claude Code (Orchestrator):**

Invoke the skill to check state:

```
Run cdad-cycle skill to check current state (should say Stage 1: Discovery).
```

**Delegate to Architect:**

```
Use Agent tool to spawn cdad-architect subagent.

Prompt: 
---
You are the architect in CDAD. Spike CDAD-002 is a validation of Claude Code sub-agents.

Feature: "Calculator add function" — a new public func Add(a int, b int) -> int in src/calc.

Discovery task:
1. Audit the repo landscape: does src/calc/ exist? Any existing Add-related tests?
2. Brainstorm implementation options (trivial: just return a + b).
3. Draft the spec with postconditions P1-P4 (defined in spec.md).

Spec location (for reference if needed): docs/specs/cdad-002/spec.md
State file: docs/.cdad-state.json (you can read it)
Repo root: current directory

Output format: LISTO. Brainstorm + spec draft for CDAD-002...
---
```

**Capture architect's output.**

**In Claude Code (Orchestrator):**

Update state:

```
docs/.cdad-state.json:
{
  "feature_id": "cdad-002-validate-claude-code-subagents",
  "stage": 2,
  "substage": "refine"
}
```

### Stage 2: Specification (optional)

If architect's spec is good, skip this or quickly review. The spec.md already defines the postconditions.

### Stage 3.0: TDD AUDIT

**Delegate to Test-Writer:**

```
Use Agent tool to spawn cdad-test-writer subagent.

Prompt:
---
You are the test-writer in CDAD. Stage 3.0 (AUDIT).

Feature: "Calculator add function" in src/calc (new package).

Audit task: Read the existing test suite (if any) for src/calc/.
- List any existing tests related to Add.
- For each: mark as "to modify" or "untouched".
- Identify new tests needed for spec postconditions P1-P4.

Spec reference: docs/specs/cdad-002/spec.md
Repository: Go project, Makefile with "make test"
Existing test location: tests/calc/calc_test.go (create if missing)

Output: Produce a Test Audit Report (see cdad-cycle skill for format).
---
```

**Capture audit output.**

Update state:

```
docs/.cdad-state.json:
{
  "feature_id": "cdad-002-validate-claude-code-subagents",
  "stage": 3,
  "substage": 0,
  "tdd_substage": "red"
}
```

### Stage 3.1: TDD RED

**Delegate to Test-Writer:**

```
Use Agent tool to spawn cdad-test-writer subagent.

Prompt:
---
You are the test-writer in CDAD. Stage 3.1 (RED).

Feature: "Calculator add function" in src/calc.

Red task: Write tests that verify spec postconditions P1-P4.
- TestAdd_basic: Add(2, 3) == 5
- TestAdd_no_panic: no panic on valid inputs

Each test MUST fail initially (we haven't implemented Add yet).
Failure reason: undefined reference to Add, or assertion failure.

Spec: docs/specs/cdad-002/spec.md
Test location: tests/calc/calc_test.go
Run: make test

After writing, run the suite and paste the FAIL output.

Output: LISTO. Tests RED...
```

**Verify tests FAIL with correct reason (not import error).**

Update state:

```
tdd_substage: "green"
```

### Stage 3.2: TDD GREEN

**Delegate to Implementer:**

```
Use Agent tool to spawn cdad-implementer subagent.

Prompt:
---
You are the implementer in CDAD. Stage 3.2 (GREEN).

Feature: "Calculator add function" in src/calc.

Green task: Write the simplest code that makes the RED tests pass.
- Implement func Add(a, b int) int { return a + b }
- Location: src/calc/calc.go (create if missing)

Tests must pass. Run the full suite:
  make test

Output: LISTO. Implementation in src/calc/calc.go. Suite: GREEN. Commit: <hash>
```

**Verify suite is ALL GREEN.**

Update state:

```
tdd_substage: null
stage: 4
```

### Stage 4: Review

**Delegate to Reviewer:**

```
Use Agent tool to spawn cdad-reviewer subagent.

Prompt:
---
You are the reviewer in CDAD. Stage 4 (Review).

Feature: "Calculator add function" in src/calc.

Review task: Audit the diff (implementation + tests) against spec.
5 ejes: Correctness, Robustness, Maintainability, Testability, Performance.

Spec: docs/specs/cdad-002/spec.md
Diff: (tell reviewer to use `git diff main` or paste diff)

Expected: no CRITICAL or MAJOR findings (spike is intentionally trivial).

Output: LISTO. Review report. Severities: CRITICAL=0, MAJOR=0, MINOR=?, TRIVIAL=?.
```

**Capture review findings.**

Update state:

```
stage: 5
```

### Stage 5: Merge + Memory Bank

**Delegate to Scribe:**

```
Use Agent tool to spawn cdad-scribe subagent.

Prompt:
---
You are the scribe in CDAD. Stage 5 (Memory Bank).

Feature: "Calculator add function" validation spike CDAD-002.

Scribe task: Draft a Memory Bank update capturing:
1. Validation result: did all 5 stages complete? Any blockers?
2. Agents invoked: list which agents were spawned and their model/profile.
3. Findings: path-scoping hooks worked? State-passing OK? Any surprises?
4. Lessons learned: what this spike proved about Claude Code support.

Reference spec: docs/specs/cdad-002/spec.md
Diff: git diff main (post-merge diff if committed)
Review findings: (paste key findings above)

Output: LISTO. Draft Memory Bank entry for CDAD-002 validation...
```

**Approve and commit the Memory Bank entry** (simulate user approval).

---

## Post-Spike Evidence Capture

Create a validation findings file:

**File:** `findings/validation-cdad-002.md`

```markdown
# Validation: CDAD-002 — Claude Code Sub-agents

**Date:** 2026-08-13  
**Profile:** optimus  
**Result:** PASS / FAIL (fill in after spike completes)

## Stages Completed

- [x] Stage 1: Discovery (architect)
- [x] Stage 2: Specification
- [x] Stage 3.0: TDD AUDIT (test-writer)
- [x] Stage 3.1: TDD RED (test-writer)
- [x] Stage 3.2: TDD GREEN (implementer)
- [x] Stage 4: Review (reviewer)
- [x] Stage 5: Memory Bank (scribe)

## Agent Execution Summary

| Agent | Model | Invocation | Status | Notes |
|-------|-------|---|---|---|
| cdad-architect | sonnet | Agent tool ✓ | PASS | Produced spec draft |
| cdad-test-writer | sonnet | Agent tool ✓ | PASS | Audit + RED tests ✓ |
| cdad-implementer | haiku | Agent tool ✓ | PASS | Suite GREEN ✓ |
| cdad-reviewer | opus | Agent tool ✓ | PASS | No blockers ✓ |
| cdad-scribe | sonnet | Agent tool ✓ | PASS | Memory entry drafted ✓ |

## Path-Scoping Verification

### Test-Writer (Read/Grep/Glob Restrictions)

- [ ] Attempted to read `src/` — hook BLOCKED (exit 2) ✓
- [ ] Attempted to read `lib/` — hook BLOCKED (exit 2) ✓
- [ ] Allowed to read `tests/` and `spec.md` ✓

### Test-Writer (Edit/Write Restrictions)

- [ ] Attempted to write outside `tests/` — hook BLOCKED (exit 2) ✓
- [ ] Allowed to write to `tests/calc_test.go` ✓

### Implementer (Edit/Write Restrictions)

- [ ] Attempted to write to `tests/` — hook BLOCKED (exit 2) ✓
- [ ] Allowed to write to `src/calc/calc.go` ✓

## Model Routing Verification

- [ ] Architect: sonnet (expected: sonnet optimus) ✓
- [ ] Test-Writer: sonnet (expected: sonnet optimus) ✓
- [ ] Implementer: haiku (expected: haiku optimus) ✓
- [ ] Reviewer: opus (expected: opus optimus) ✓
- [ ] Scribe: sonnet (expected: sonnet optimus) ✓

## State-Passing Verification

- [ ] Architect received no parent session context ✓
- [ ] Test-writer received spec but NOT implementation ✓
- [ ] Implementer received spec + tests but NOT review ✓
- [ ] Reviewer received diff but NOT implementer's session (read-only) ✓
- [ ] Scribe received all prior outputs without implementer details ✓

## Blockers & Fricciones

(List any issues discovered during spike)

- None found (ideal case)
- OR:
  - Friction: [description]
  - Blocker: [description]

## Recommendations

(Capture any improvements for follow-up work)

- ...

## Overall Result

**PASS** — All 5 stages completed, path-scoping honored, models routed correctly, state-passing clean. Claude Code support for CDAD agents is verified and ready for production use.

(or FAIL with specific blockers if issues found)
```

---

## Cleanup

After validation completes:

### Option A: Keep the Feature (as permanent "hello-world" test)

```bash
git log --oneline | head -10   # show commits during spike
# Feature lives in repo; CI will run tests, etc.
```

### Option B: Revert Feature (keep validation findings)

```bash
git reset --hard HEAD~7        # example: 7 commits during spike
git push origin main --force   # force-push if needed

# Findings + Memory Bank entry persist in docs/findings/ and docs/memory-bank.md
```

Choose Option A if you want CDAD-002 as a permanent regression test; choose Option B for a cleaner final repo.
