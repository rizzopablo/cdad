# Stage E3 — Epic integration

Verify that the epic's features work **together**, not just each one on its own. Output: cross-feature E2E tests green + `integration.md` documenting what was integrated and what was learned.

## Why this stage exists

Each feature went through its own CDAD cycle with individual E2E tests. But individual E2E tests only cover the flow of ONE feature. Epic integration verifies that the composed features deliver the result promised in the epic's acceptance criteria.

Example: AFIP invoicing epic. Individual features have tests:
- 001 validates the CUIT.
- 002 generates the XML.
- 003 sends to the WS.
- 004 handles the retry queue.
- 005 parses responses.

But no individual test verifies the complete flow: invoice comes in → CUIT validated → XML generated → sent to the WS → response parsed → state persisted. That is E3's work.

## Your role

You coordinate. You identify the cross-feature flows that need to be tested (the ones in the epic's acceptance criteria), you issue the handoff to the **test-writer in E2E cross-feature mode**, you validate the result.

## Steps

### Step 1 — Identify flows to test

Re-read the **Epic acceptance criteria** from `plan.md`. Each criterion that requires a cross-feature flow is an epic E2E test.

Example:

| Criterion | Cross-feature E2E test |
|----------|------------------------|
| "Given a valid invoice, XML is generated, sent, and state is persisted" | Test that exercises 001 + 002 + 003 + 005 |
| "Given a failed submission, the queue retries until success or timeout" | Test that exercises 003 + 004 with a WS mock that fails N times |

### Step 2 — Handoff to the test-writer in E2E cross-feature mode

It is a variant of the E2E that `cdad-cycle` already has, but with an expanded scope: it covers multiple features.

Load `cdad-cycle/references/handoff-prompts.md` (yes, from the other skill — the pattern is the same) and adapt the section "Test-writer (Stage 3 — Integration / E2E)" for cross-feature:

```
You are a test-writer sub-agent in CDAD epic E2E cross-feature mode.

Task: translate ONE epic acceptance criterion into an E2E test that exercises 
multiple features together.

Context:
1. Epic plan: paste docs/epics/<id>/plan.md
2. Specific criterion to verify: <paste>
3. Specs of the involved features: paste docs/specs/<feat-i>/spec.md for each one
4. Public API of each feature (the interfaces used from the outside)
5. Project's E2E test conventions

Strict rules:
- Permissions: edit ONLY in tests/ (in a tests/integration/ or tests/epic/ folder)
- Calls via the features' public API. You do NOT access internals.
- Setup with realistic fixtures, no mocks that turn the test into a unit test.
- Mocks ONLY for external systems of the epic (third-party services, external APIs).
- Asserts derived from the epic criterion, one by one.

Expected output: E2E test file + commit "test(epic): add E2E for <criterion>".
When done:
"READY. E2E in <file>. Run output:
<paste output showing E2E green>
Commit: <hash>"
```

Generate the packet with all the context inline. Deliver to the user, end your turn.

### Step 3 — Re-entry

Validate:

- [ ] E2E test exists in `tests/integration/` or the project's equivalent.
- [ ] The run output pasted by the user shows green.
- [ ] Full suite still green (including previous tests of each feature).
- [ ] Commit with prefix `test(epic):` or a similar consistent one.

If it passes: mark that criterion as covered. If there are more cross-feature criteria left, issue the next handoff. If not, you move forward.

### Step 4 — Document `integration.md`

When all the cross-feature criteria have green E2Es, draft `docs/epics/<id>/integration.md`:

```markdown
# Epic <id> — Integration

## Cross-feature E2E tests

| Criterion | Test | Status |
|----------|------|--------|
| <criterion 1> | tests/integration/test_epic_<id>_flow.py::test_full_flow | ✅ green |
| <criterion 2> | tests/integration/test_epic_<id>_retry.py::test_retry_until_success | ✅ green |

## Findings during integration

<Anything learned during the integration phase: cross-feature bugs 
that emerged, adjustments to contracts, refactors made to already 
done features so they play well together, etc.>

## Technical debt detected

<If the integration revealed debt that was not resolved in this epic, document it 
for future epics or standalone features.>
```

Pass the draft to the user for final approval of the file (it is not non-delegable, but it is advisable that the user (human or a higher-hierarchy agent) review it before the orchestrator commits it).

## 🛑 Exit gate (E3 → E4)

- [ ] Each cross-feature acceptance criterion of the epic has its E2E test.
- [ ] All cross-feature E2Es pass.
- [ ] Full suite green (individual E2Es + cross-feature + unit + properties + linter + type checker).
- [ ] CI green on main / the epic's branch.
- [ ] `docs/epics/<id>/integration.md` exists and is committed.

When all OK: update the state (`epic_stage: epic-closure`). Announce the transition. Load `epic-closure.md`.

## Main anti-pattern (EAP-4)

**Skipping E3 because "each feature passed its E2Es"**. Individual tests do NOT substitute cross-feature tests. Typical bugs that only appear in integration:

- Feature A generates output that feature B expects in a slightly different format.
- Timing between features (race conditions).
- Shared resources (DB, files, locks) that work individually but clash together.
- Errors that in feature A are "handled" by throwing an exception that feature B does not account for.

If the user tries to skip it:

> *"The individual features passed their E2Es but none of them verifies the epic's complete flow. Cross-feature integration is precisely where the bugs that no individual test detects appear. How many cross-feature criteria do you have left? If few, we'll be done quickly."*

## If E3 fails — cross-feature bug

If a cross-feature test fails, identify which feature(s) have the bug. It is likely the bug is in a feature already `done`, which means:

1. The feature with the bug goes back to `in-progress` in the state.
2. The fix is applied with CDAD discipline (red test first, etc.) — yes, it requires another mini-cycle.
3. If the bug reveals that the feature's spec was incomplete, the spec is updated and re-approved.

You do NOT merge a cross-feature fix as "a patch in the E2E test" without going to the responsible feature. That dirties the specs and breaks them in the future.
