# Systematic debugging — diagnostic protocol

> **Sources:** obra/superpowers `systematic-debugging/SKILL.md` (Iron Law,
> 4 phases, rule 3+ fixes → architecture, red flags) and its auxiliaries
> `root-cause-tracing.md` (fix at the source, not where the symptom appears),
> `condition-based-waiting.md` (polling on a condition, never arbitrary sleep) and
> `defense-in-depth.md` (layered validation); Hermes Agent adaptation —
> "The Feedback Loop Rule": guessing without a red-capable loop IS the failure mode;
> arjenschwarz `systematic-debugger` — modified Fagan inspection + Five Whys
> for stubborn bugs (post-multiple-failures); epic research
> (`docs/epics/research-tema3-debugging/research.md`).
> Canonical search notation: `defense.?in.?depth` and
> `condition.?based.?waiting` — the terms match with or without dashes
> ("defense-in-depth", "defense in depth").
>
> **Invoked when:** a GREEN fails in Stage 3 and a diagnosis is needed before
> re-delegating (`stage-3-tdd.md` §3.2), or CI is broken in Stage 5
> (`stage-5-merge.md` §5.1).

**Core principle:** WITHOUT A VERIFIED ROOT CAUSE THERE IS NO FIX. The symptom is data,
not a diagnosis. A fix that does not come from a verified root cause is a bet
disguised as a correction — and stacked bets are thrashing (AP-18).

## The red loop IS the RED sub-phase

This is the central synthesis of the protocol in CDAD: debugging is not another
methodology, it is RED with diagnostic discipline. The *tight feedback loop* of
Superpowers/Hermes — one command that reproduces the bug — **is the RED sub-phase**
of `stage-3-tdd.md` applied to the bug:

- A **tight** command: fast, deterministic, agent-runnable, that goes **red with
  the exact symptom** and green **only with the fix**.
- The assert verifies the observed symptom, not "that it doesn't crash". A test
  that passes without the fix is not a red loop: it falsifies nothing.
- **Before reading code to build theories, the red loop has to exist.**
  Guessing without a red-capable loop is THE failure mode of debugging.
- If the bug is flaky: the first job is to **raise the repro rate** — run
  the test 100 times, parallelize, narrow the timing window. NEVER arbitrary
  sleep or "retry and see": `condition-based-waiting` — polling on
  the real condition (the resource is there, the event arrived, the state changed) instead of
  waiting an invented amount of time.

## Phase 1 — Diagnosis (collect evidence)

1. **Read the full error.** Entire stack traces, line numbers, first
   error in the output (not the last). Trimming the error is trimming the evidence.
2. **Build the red loop** (see above). Without a repro there is no diagnosis:
   there is guesswork.
3. **Recent changes:** `git diff` / `git log` of the affected area. Most
   bugs arrived with a recent commit.
4. **Multi-component systems:** instrument each boundary (what goes in, what
   comes out at each service/module/process frontier) **before** proposing
   anything. Evidence at boundaries replaces theories about "at what time the
   pipeline breaks".
5. Keep the accumulated evidence as a log (what you tried, what you observed).
   Under the 3+ rule, that evidence is what gets escalated.

## Phase 2 — Minimize + compare

- **Minimal repro (cut-one-thing):** remove one element at a time from the repro (data,
  steps, components). The done criterion: removing any of the remaining
  elements turns it green. Every element left over in the repro is noise that
  can point the hypothesis wrong.
- **Compare against code that does work** (same codebase, same mechanism
  elsewhere) **listing ALL the differences** — not only the one you already
  suspect. The difference you did not look at is the one causing the bug.

## Phase 3 — Ranked hypotheses

Don't pick a theory and defend it: generate **3-5 falsifiable hypotheses**,
ordered by likelihood × cheapness to falsify. Each one carries an explicit
prediction: "if X is the cause, Y should do Z".

- Test with the **smallest probe** (a log, a breakpoint, an extra assert) —
  never a big change "to see if it gets fixed".
- **ONE variable at a time.** Changing two things together destroys the information:
  even if it gets fixed, you don't know which one did it, and the other change may have
  introduced a new bug.
- **Verify before moving on.** If the prediction fails, the hypothesis
  is dead: write it down and move to the next one, don't twist it.
- "I don't understand X" is a valid and useful answer — better than a
  convenient theory that was never falsified.

## Phase 4 — Fix

- **A single fix, on the root cause** — not on the symptom. Trace backwards
  through the call chain: the fix goes at the **source**, not where the
  symptom appears.
- **No "while I'm here":** no fixes bundled with a refactor or nearby cleanup.
  If the neighbor needs a refactor, that is another task (and another RED cycle).
- **Regression test first.** If the root cause is a new postcondition,
  the test-writer writes the regression test (RED); if the failing
  test itself was wrong (it verified something else), the fix belongs to the test. The code fix comes in
  afterwards, and that test is what keeps the bug from coming back.
- **Defense-in-depth AFTER the fix:** layered validation (data boundary,
  module entry, internal invariants) so the bug class becomes
  impossible, not just absent. Never in place of the root-cause fix.

## The 3+ rule → STOP → ADR

**3 or more failed fixes = STOP.** Don't attempt the fourth: a fourth attempt
on the same theory is not persistence, it is ignoring evidence.

1. Question the architecture, not your luck: 3+ fixes with no result is a sign that
   the design, not the detail, is at the root.
2. **Escalate to the user** with the accumulated evidence (red loop, hypotheses
   tested and their results, what you learned from each failure).
3. The outcome is an **ADR** (`docs/adr/`) that decides: a one-off bug within a
   reasonable design, or a wrong design → possible return to Discovery
   (the pre-existing exception of the cycle, "whole spec wrong → Stage 1").
4. Every fix that fixes here but breaks there **IS the signal**: the new problem
   elsewhere is the data showing the boundary of responsibilities is wrong.

## Roles in the CDAD cycle

- **Diagnosis = implementer.** It reads the suite and the code (it may read tests),
  but does NOT touch `tests/` (AP-4 still applies). The red loop can be the existing red
  test or a disposable repro command outside `tests/`.
- **Regression test = test-writer.** If the root cause implies a new
  postcondition, the test enters through RED (test-writer); the implementer does not write it.
- **Stubborn bugs (3+ accumulated failures):** modified **Fagan**
  inspection (clarify the problem → line-by-line reading of the code involved WITHOUT
  fixing anything along the way) + **Five Whys** (3-5 whys, writing down the
  assumptions of each jump) as techniques for phases 1-2. They are triggered WHEN
  there have already been 3+ failures, not before.

## Anti-rationalization table

| Typical excuse | Refutation |
|---|---|
| "It's simple, I'll fix it directly" | Simple ≠ diagnosed. Without a verified root cause there is no fix — not even for "obvious" bugs |
| "Let me just try one change and see" | Trying without a red loop is guessing with extra steps. First the command that goes red with the exact symptom |
| "I'll run 2 changes together to go faster" | Two variables at once destroy the information: if it gets fixed, you don't know which one; and one may introduce a new bug. ONE at a time |
| "I've already tried 3, one more won't hurt" | 3+ is STOP, not "another round": escalate to the user with evidence and an ADR. The fourth attempt burns context and trust |
| "It's flaky, I'll retry" | Retrying is praying. Raise the repro rate (run 100x, parallelize, narrow the window) and use condition-based-waiting, never arbitrary sleep |
| "There's no repro, I'll go by intuition" | Without a red loop no theory is worth anything: every theory without a repro is unfalsifiable. Invest in reproducing first |
| "While I'm at it, I'll refactor the thing next to it" | While-I'm-here stacks a design change on top of a fix without diagnosis: if something breaks, you don't know what. The fix is single and focused |
| "The ADR is bureaucracy, I'll try another fix" | The ADR is the only record of why the fourth fix would also fail. Without an ADR, the next cycle starts from zero again |

## When it does NOT apply

1. **Pure documented infrastructure:** an external provider outage, an exhausted quota,
   a platform incident — not code to fix: escalate to the user +
   monitoring, and wait for the provider. The protocol does not fabricate code fixes
   for problems that are not code problems.
2. **Chronic flaky with an explicit monitoring plan and registered debt:** if the
   instability is already documented as debt with a monitoring plan and a quota
   agreed with the user, it is not re-diagnosed in every session — consult
   the plan.

Outside these two cases, the protocol applies in full: red loop first →
diagnosis → minimize + compare → ranked hypotheses → single fix on
the root cause.
