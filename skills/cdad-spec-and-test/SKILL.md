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
verification: Checklist, one test per line
```

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
2. **Tests before code.** The verification is written BEFORE Build. If afterwards the tests pass, you are done.
3. **Tests are not just pytest.** It accepts:
   - `curl ... | grep ...` (integration)
   - `python3 -c "..."` (inline unittest)
   - File checks (`test -f`, `test -d`)
   - Manual steps with expected result (for UI)
4. **If a test fails, the task is not done.** Period. No excuses.

## How to close the cycle

```
[Build]  →  [Verify: run tests]
                 ↓
           Do all pass?
            /        \
          Yes         No
         /            \
    [Merge]       [Fix → Build again]
```

If after Verify all tests pass → Merge (commit, wiki, skill, whatever applies).
If any fails → go back to Build, do not move forward.

## Tests that are NOT useful

❌ "Manually verify that it works" — no objective criterion
❌ "The user should be able to see the screen" — how is it measured?
❌ "Test on staging" — without specifying what is tested
❌ Any test you cannot run in <30 seconds

## Tests that ARE useful

✅ `curl endpoint ; expect HTTP 200`
✅ `python3 -c "import module; module.function(); print('OK')"`
✅ `ssh server "command; test condition"`
✅ `test -f file`
✅ List of steps with an expected result per step

## Integration with CDAD

| Gate | Action |
|------|--------|
| 0→1 (Discovery→Spec) | Write spec.yaml with postcondition + verification |
| 1→2 (Spec→TDD) | Write tests (automated or checklist) |
| 2→3 (TDD→Review) | Run tests against the build |
| 3→4 (Review→Merge) | All tests pass → merge |
