# Documented Anti-patterns

Patterns to detect and correct when they appear at any stage of the cycle.

## AP-1 — Single session for everything

**Symptom**: the user says "it's done, I asked the LLM to write the test and the code in a single pass".

**Why it's bad**: the agent aligns test and implementation with each other. The test passes because it was written for the code the agent was going to write, not because it verifies the spec. You lose the independent oracle.

**Correction**: ask the user to let us restart. Even if the code "works", the tests are not reliable. Go back to Stage 3 with an isolated `test-writer` session and rewrite the tests without looking at the current code. Then run the tests against the existing code: if they pass, it's fine; if they fail, there is a bug the first tests didn't catch.

## AP-2 — Test written after the code

**Symptom**: the user implements first "to see if it works" and then writes the test.

**Why it's bad**: the test you write after the code tends to verify **what the code does**, not **what the spec asks for**. It is the subtlest trap.

**Correction**: if it already happened, you can't undo it, but you can mitigate it: ask the user to review the test against the spec, **without looking at the code**, and ask themselves "if the code were completely different, would this test still be valid?". If the answer is "I'm not sure", rewrite it from the spec.

For upcoming postconditions, reinforce the discipline: test first, no exceptions.

## AP-3 — "Green" test without empirical verification

**Symptom**: someone says "the test passes" but the suite was never run.

**Why it's bad**: confidence is not evidence. The test may have a bug that makes it always pass. The implementation may have side effects that break other tests.

**Correction**: run the suite. If your environment does not allow execution, ask the user for the exact output:

> *"I need the suite output. Paste the last 20 lines of the run, including the final summary line."*

Do not advance a phase with "I think it passes".

## AP-4 — Implementer modifies tests

**Symptom**: during GREEN, the implementer finds the test "is wrong" and changes it to make it pass.

**Why it's bad**: the implementer's rule is **make the test pass, don't change it**. If the test is wrong, you must go back to the test-writer in an isolated session to correct it, not allow the implementer to "adjust it".

**Correction**: revert the test change. If the test is genuinely wrong:

1. Close the implementer session.
2. Open a test-writer session.
3. Hand over: the spec, the problematic test, the reason it seems wrong.
4. The test-writer corrects it (or explains why it was right and the implementer was confused).
5. Go back to the implementer with the corrected test.

## AP-5 — Skipping the spec because "it's simple"

**Symptom**: "it's just adding a field, it doesn't need a spec".

**Why it's bad**: features that seem simple at the start are the ones that most frequently reveal ambiguities during implementation. And "simple" for you may not be simple for the LLM.

**Correction**: accept the **minimum spec variant**: one paragraph of description + one failing test. It is not overkill — it is the minimum that keeps the discipline.

> *"OK, we don't need the six blocks. But one paragraph describing what it does, one concrete assertion, and your approval. Three minutes."*

## AP-6 — Spec approved silently

**Symptom**: the spec exists but has no unequivocal approval mark; the user "assumes it's approved".

**Why it's bad**: in Stage 4, when the reviewer detects a divergence, we won't know whether the divergence is against the original approved spec or against a version that changed.

**Correction**: add the explicit mark now. Final line `Status: Approved by <X> on <date>` or frontmatter. Then we continue.

## AP-7 — Outdated Memory Bank

**Symptom**: the feature gets merged, but `activeContext.md` and `progress.md` were not touched.

**Why it's bad**: the next session starts without context of what was just done. The LLM doesn't know we already have a date parser, and proposes reimplementing it from scratch.

**Correction**: block the Stage 5 closure. Apply the Scribe pattern (you draft it, the user approves, and the orchestrator commits). 5 minutes, non-negotiable.

## AP-8 — Speculative or missing ADRs

**Two bad extremes**:

- **Speculative**: ADR-001 "We're going to use PostgreSQL at some point". There is no real decision, it's an expectation. Noise.
- **Missing**: a big architectural decision was made (e.g. DB change, new bounded context) and there is no ADR.

**Correction**: an ADR when there is a real decision with consequences and documentable trade-offs. If in doubt, ask: *"could someone in 6 months ask 'why did we do X this way'?"* If yes → ADR. If no → no.

## AP-9 — CI skipped

**Symptom**: "the linter fails but it's a minor thing, let's merge and fix it later".

**Why it's bad**: "later" never arrives. Violations accumulate. Every PR that goes through with CI skipped erodes trust in CI.

**Correction**: fix it first. If it is genuinely trivial, it's 2 minutes. If it's real, there was a reason CI blocked it.

## AP-10 — "Pass it through me"

**Symptom**: the user starts delegating to the LLM, on the spot and without a previous explicit request, things that are non-delegable by default (spec approval, review prioritization, Memory Bank update content).

**Why it's bad**: it erodes the principle of user approval at key moments. Sustainable quality comes from the combination of process owner (human or higher-hierarchy agent) + LLM, not from the LLM alone.

**Correction**: point out the non-delegability politely.

> *"This requires your judgment about <domain/client/product>. I can draft it or give you options, but the decision is yours. Want me to give you a draft to edit?"*

**Exception — do not confuse with legitimate delegation**: spec approval (Stage 2) and review prioritization (Stage 4) allow delegation to an expert agent **only if the user explicitly requested it for that specific feature or stage**, not as a project default. See "Exception: explicit delegation to an expert agent" in `stage-2-specification.md` and `stage-4-review.md`. A casual request within the conversation ("you approve it, go ahead") without that previous context is still AP-10 — the difference is that the explicit request must precede the moment of approval, not coincide with it.

## AP-15 — Unsolicited self-approval

**Symptom**: the orchestrator (or another agent) assumes on its own that it can approve the spec or prioritize the review because "it feels it has enough context", without the user having explicitly requested it for that feature.

**Why it's bad**: approval delegation exists for cases where the user, with their own judgment, decides to trust their judgment to an agent. If the agent grants itself that authority, there is no user decision behind it — it is AP-10 with an extra step of justification.

**Correction**: if there was no previous explicit request, user approval by default, no exceptions. If the orchestrator is tempted to approve because "this is obvious" or "it's not worth bothering the user", that temptation is the signal to pass it to the user, not the justification for skipping them.

## AP-11 — Refactor that breaks tests

**Symptom**: the refactorer makes changes and "now three tests fail, but they're minor, we'll fix them".

**Why it's bad**: the rule of refactoring is "observable behavior does not change". If tests fail, behavior changed. It is not a refactor; it is a functional modification without a spec.

**Correction**: revert the refactor. If it was genuinely a refactor and the tests were wrong, that is a problem with the tests (go back to the test-writer). If it was a functional modification, that requires updating the spec first (go back to Stage 2).

## AP-12 — Property tests with a random seed

**Symptom**: property tests green locally, red in CI sometimes.

**Why it's bad**: non-deterministic tests break trust in the suite.

**Correction**: configure a fixed seed for property tests in CI. Hypothesis, fast-check, and similar libraries support it. The seed is committed together with the test.

## AP-13 — Garbage Cascade (ambiguous spec with non-exhaustive tests)

**Symptom**: the feature stage does not use exhaustive coverage (by design — see "Test convention" in `stage-3-tdd.md`), but the spec has vague or unnumbered postconditions.

**Why it's bad**: without test exhaustiveness, the entire burden of precision falls on the spec. An ambiguous spec produces contract tests that verify one possible interpretation but not the correct one, and an implementation that passes the suite without being what the user needed. The error cascades from Stage 2 with nothing in Stage 3 detecting it.

**Correction**: RED is not opened with unnumbered or untestable postconditions. If ambiguity appears during RED or GREEN, it is not resolved "at the discretion" of the test-writer or implementer — go back to Stage 2 to make the spec precise and re-approve it.

## AP-14 — Mock over plumbing

**Symptom**: the test-writer verifies middleware call order, internal function names, or mocks internal collaborators instead of verifying the observable effect.

**Why it's bad**: it fixes an implementation decision in the RED stage, before an implementation exists. It takes away from the implementer the design freedom GREEN needs, and couples the test to an internal structure that can change without the behavior changing — the test becomes fragile and stops being a reliable oracle of the contract.

**Correction**: revert the test. Rewrite it verifying the effect an external consumer of the system (another process, another service, the user) can observe — wire message, command result, event emitted outward, rejected auth. If the effect you want to verify is purely internal between modules, it probably does not correspond to a postcondition of the spec; check whether the spec needs precision.

## AP-16 — Performative response / blind implementation

**Symptom**: the role responds to feedback with "you're so right!", thank-yous, or immediate agreement, and/or implements the suggestions without verifying against the code. Typical signal: the receiver starts editing while still reading the reviewer's report.

**Why it's bad**: sycophancy is a training artifact (RLHF) — compliance was rewarded, so the model produces it by default. The performative agreement emitted before verifying nullifies the receiver's only real defense (verification against the code), and implementing blindly freezes into the codebase the errors the feedback itself may have: neither the receiver nor the feedback is ground truth on its own.

**Correction**: apply `references/receiving-feedback.md` — a 4-step sequence (read fully without reacting → restate → verify against the real code → implement one fix at a time with verification), push-back with cited evidence when the finding is wrong. Proper push-back with evidence is the receiver's obligation, not rudeness: the rude thing (toward the codebase) is letting a false finding go through.

## AP-17 — Destructive integration

**Symptom**: the agent merges, deletes branches/worktrees, or discards work without presenting the options menu, without confirming the base branch, or with weak confirmation ("yes, delete it"). Typical signal: `git branch -D`, `git worktree remove`, `git reset` executed without the user having chosen an option from the closure menu or typed the literal word `discard`.

**Why it's bad**: it deletes irrecoverable work — a reset/discard without literal confirmation destroys commits with no safety net. A merge onto the wrong base contaminates the whole team's main. And the cycle's state file assumes an intact tree: silent destruction breaks the premise of "you go back to stage N-1" — the state the cycle believes exists no longer exists.

**Correction**: apply `stage-5-merge.md` §5.6 — environment detection, base branch confirmed, fixed menu of 4 options, discard only with the literal word `discard`, cleanup by provenance (only the cycle's own worktrees), and never `--force` on your own initiative. (Historical context note: a runtime with a web interface executed `git reset` over uncommitted work in this project — the reflog was the only trace left.)

## How to use this file

Load it when you detect signals of any of these patterns. Do not load it preventively; it is noise if everything is going well. When you intervene against an anti-pattern, cite the code (AP-N) in your message to the user so they can look it up:

> *"We are falling into AP-2 (test after code). We are going to correct before continuing."*

## AP-18 — Fix without diagnosis (thrashing)

**Symptom**: 2+ fixes in the same session with no stable repro or no written root cause. Typical signal: "let's try this change and see" — a delegated fix with no red loop, followed by another delegated fix on top of the first one's result.

**Why it's bad**: stacked fixes hide which one did what — by the time the suite goes green (or not), there is no way to attribute the effect. Every fix without a diagnosis can introduce a new bug on top of the one it was trying to fix. Thrashing burns the user's trust (why does nobody know what's going on?) and the context budget (every failed RED→GREEN cycle is a full turn). And 3+ failed fixes without a diagnosis is not bad luck: it is a signal that the problem is one of design, not of aim.

**Correction**: apply `references/stage-debugging.md` — red loop first (a tight command that goes red with the exact symptom and green only with the fix), falsifiable ranked hypotheses with one variable at a time, and a single fix on the verified root cause. At the 3rd failure: STOP → escalate to the user with the accumulated evidence → an ADR deciding one-off bug vs. wrong design.

## AP-19 — Placeholder plan

**Symptom**: a plan for a complex feature with tasks that don't close in their own mini TDD cycle; phrases like "TBD", "TODO", "handle edge cases appropriately", "similar to Task N"; or inconsistent signatures across tasks (task 2 produces `clearLayers`, task 5 consumes `clearFullLayers`). Signal: the plan could not be executed without re-deriving design decisions halfway through.

**Why it's bad**: the ambiguous plan delegates design decisions to the implementer with no contract — it is AP-13 (Garbage Cascade) at task level. The test-writer inherits an interface invented halfway through, and its tests point to a contract nobody approved; inconsistent signatures break the integration between tasks and are discovered in GREEN, the most expensive place to discover them. And a plan containing the speculated implementation reverses TDD: the implementer executes decisions the planner baked in without verifying.

**Correction**: follow "Planning for complex features" in `references/stage-2-specification.md` — task size with its own TDD cycle, observable behavior as contract (3-5 verifiable bullets), the list of forbidden placeholders = plan failure, and a self-review of spec coverage and signature consistency before closing Stage 2.
