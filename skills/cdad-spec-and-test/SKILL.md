---
name: "cdad-spec-and-test"
description: "CDAD spec/test workflow: postcondition, minimal format, tests before the build, real TDD with an acceptance criterion."
---

# Skill: CDAD Spec & Test

## Summary
Standardizes how specs and tests are written in the CDAD cycle. Minimalist spec (postcondition + acceptance criterion). Tests written before the build. Applies to code, documentation, infra setup, whatever.

## When to use it
- At the start of **any** task: code, doc, setup, research
- At the transition from **Discovery → Spec** (Gate 0→1)
- When the **Verify** gate is unclear because you have not defined what "done" means

## How to write a CDAD Spec

A spec is not a 50-page document. It is:

```yaml
context: Brief — what we are doing and why
resolution: What problem it solves / what need it covers
postcondition: How I know this is done (single sentence)
verification:                  # one entry per promise (rule 2)
  - property: what is promised, in the user's terms
    method: executable | contextual review | combined
    acceptance: the observable condition that accepts the promise
    evidence: the records that will exist (test output, review report)
    limits: what this method cannot establish
    checks: one test per line for the executable part (none for semantic-only)
```

The examples below show only the `checks` of each promise; the other fields are required for every promise.

### Example — Development instance setup:

```yaml
context: Configure development access to dev.example.com
resolution: Have SSH + app + GitHub access for R&D
postcondition: I can log in to the app and clone repos from the instance
verification:
  - ssh dev@localhost whoami → "dev"
  - curl http://localhost:PORT/xmlrpc/2/common → app version
  - ssh -T git@github.com 2>&1 | grep "Hi <user>"
  - test -d ~/src/<project> → exists
  - test -d ~/.<tool>/src/custom-dev → exists
```

### Example — App module:

```yaml
context: Health check module for the deploy's domain
resolution: The app reports its status (DB, workers, space) via API
postcondition: GET /health returns JSON with db_status, worker_count, disk_usage
verification:
  - curl /health → HTTP 200, JSON with the 3 fields
  - When the DB is down, db_status = "error"
  - When there are 0 workers, worker_count = 0
  - create_from_wizard=True creates the health check automatically
```

## Spec Rules

1. **Mandatory postcondition.** If you cannot write in one line what "done" means, you do not understand the task well.
2. **Verify before building, review before producing.** Each promise declares its property, method, acceptance criterion, expected evidence and limits, set BEFORE Build. Before the 1→2 transition, the draft's verification strategy gets the independent sufficiency review of `skills/cdad-cycle/references/stage-2-specification.md` §"Draft review sub-phase" (PC-2: the reviewer checks that each promise's verification can establish its acceptance; its depth is proportional), or the owner's exemption, registered in the approval's `stage_history` entry with `exempted_by`, `delegated`, `requested_by` and `reason` (`skills/cdad-cycle/references/stage-2-specification.md` §"The exemption's declared form"; the approval itself is §"Sub-phase 2.3 — Approval"). An exemption is not a review and does not claim sufficiency. Without one of the two, production does not start. Executable promises are verified by their tests; semantic-only promises by an independent contextual review of the result; mixed promises by both, each for its own part, neither substituting for the other. Passing tests alone do not close a promise's semantic part, and no test is invented for a semantic-only promise (routing: `skills/cdad-cycle/references/stage-3-tdd.md` §"Routing by verification method").
3. **Tests are not just pytest.** It accepts:
   - `curl ... | grep ...` (integration)
   - `python3 -c "..."` (inline unittest)
   - File checks (`test -f`, `test -d`)
   - Manual steps with expected result (for UI)
4. **If a test fails, or a blocking review finding stands, the task is not done.** Period. No excuses.

## How to close the cycle

```
[Build]  →  [Verify, each promise by its method]
                 ↓
   executable checks pass?              (executable and mixed promises)
   independent contextual review done?  (semantic-only and mixed promises)
            /        \
          Yes         No
         /            \
    [Merge]       [Fix → Build again, within the bounded rounds]
```

If after Verify every promise has its closure evidence (executable checks passing for its executable part, and an independent contextual review for its semantic part) → Merge (commit, wiki, skill, whatever applies).
If any fails → go back to Build, do not move forward — but not without limit: every correction loop (draft review, test audit, result review) is bounded by the maximum of rounds the spec declares, applied per family and kept across re-dispatches. A closing check that continues the loop consumes the next round; at the maximum, finish the verification of the last permitted fix, then adjudicate each remaining finding (supported dismissal, accepted optional residue, or blocked/replan). "Budget exhausted" never turns a missing verification or an unmet promise into success; accepted residue goes to the epic's single accumulation unit, or to `debt.md` without an epic. Absent audit work implies no audit round. Rules and the note pattern: `skills/cdad-cycle/references/bounded-review-cycles.md`.

## Tests that are NOT useful

❌ "Manually verify that it works" — no objective criterion
❌ "The user should be able to see the screen" — how is it measured?
❌ "Test on staging" — without specifying what is tested
❌ Any test without an objective criterion (duration alone never decides utility; no universal <30s rule — presupuesto y criterio contractual deciden)

## Tests that ARE useful

✅ `curl endpoint ; expect HTTP 200`
✅ `python3 -c "import module; module.function(); print('OK')"`
✅ `ssh server "command; test condition"`
✅ `test -f file`
✅ List of steps with an expected result per step

## Integration with CDAD

> `cdad-cycle` owns gates/format; this skill never replaces them — the table below applies them, it does not substitute the cycle.

| Gate | Action |
|------|--------|
| 0→1 (Discovery→Spec) | Write spec.yaml with postcondition + verification |
| 1→2 (Spec→TDD) | Before it: each promise's property, method, acceptance, evidence and limits declared, and the sufficiency review done or exempted (rule 2). Then write tests (automated or checklist) for the executable parts of promises; semantic-only promises get no test |
| 2→3 (TDD→Review) | Run the executable checks against the build; semantic-only parts go to independent contextual review |
| 3→4 (Review→Merge) | Every promise has its closure evidence (executable checks passing for executable parts, independent contextual review for semantic-only and mixed parts), per the cycle's evidence policy → merge |
