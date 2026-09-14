# Receiving feedback — anti-sycophancy protocol

> **Sources:** obra/superpowers `receiving-code-review/SKILL.md` (the
> receiver's sequence, forbidden responses, push-back with evidence, YAGNI check) and
> research from epic topic 1 (`docs/epics/research-tema1-receiving-feedback/
> research.md`: Morricone "Sycophancy-Free Coding" — exit clauses and
> dilution in long sessions; Koushik "Your AI Code Reviewer Is a Liar" —
> steelman and reversal counting on the reviewer side; GitAuto — anti-sycophancy
> as a guardrail and persistence of learned rules).
> Applies to every role that RECEIVES feedback (implementer in the Stage 4
> fix loop, test-writer facing user feedback, refactorer) and complements
> the orchestrator's transmitter rule (`stage-4-review.md`,
> `handoff-prompts.md`).

Feedback from a review requires technical evaluation, not emotional
performance. RLHF compliance rewards agreement: answering "you're right!"
and thanking is the statistically reinforced pattern in training, not the
correct one. A performative agreement issued BEFORE verifying nullifies the
receiver's only real defense: verification against the code. And once the
finding is verified as correct, thanking adds nothing either — the corrected
code is the confirmation.

**Core principle:** verify before implementing; ask before
assuming. Technical rigor > social comfort.

## The receiver's sequence (4 steps, mandatory)

Apply it IN FULL before touching code, for each round of feedback:

1. **Read it all without reacting.** All the feedback, in one go. No
   starting to edit while you read the second finding: the immediate
   reaction is the channel of sycophancy (pleasing) and of defense (justifying yourself), and
   the correct implementation order is only known by reading everything.
2. **Restate the requirement in your own words.** For each item, state what
   it asks technically. If you can't restate it, you didn't understand it → ambiguous
   item (see below). Restating exposes cheap misunderstandings: correcting
   the reading is cheaper than correcting the code.
3. **Verify against the real code.** Open the cited files, run the
   test or the command if applicable, confirm the problem exists exactly as the
   feedback describes it. Never start from the assumption that "if the reviewer
   said it, it must be true".
4. **Implement one fix at a time with verification.** Order: blocking items (break
   functionality, security) → simple ones (typos, imports) → complex ones
   (refactors, logic). Suite green after each one — consistent with the
   fix loop of `stage-4-review.md`. Never batch without verifying in between.

## Forbidden responses and their factual replacements

| Forbidden | Why | Replacement |
|---|---|---|
| Thanking for the feedback ("thanks for pointing it out") | Thanking reinforces the performative pattern: it is social, not technical | "Fixed in `<file>:<line>`: <what changed>" |
| Generic "you're right" | Pre-verification agreement: it capitulates without evaluating | "Verified: <what you checked>. I'll fix it at <location>" |
| Agreement before verifying | Nullifies the receiver's defense; can freeze an error of the feedback itself | Verify first; if the finding is correct, the correction itself is the answer |
| Emotional defense ("that's how the whole repo does it") | Tone is not evidence | Cited evidence (push-back, below) or correction |

The replacement has a single form: **action + location + what changed**.
"Fixed in `skills/cdad-cycle/SKILL.md:410`: row added to the table".
No over-explanation, no long apology, no friendly paraphrase.

## Ambiguous items → stop EVERYTHING

If the feedback is multi-item and there are items you can't restate: stop
EVERYTHING and ask for clarification before implementing any of them. Items are usually
related — a misunderstanding in item 2 contaminates the fix of item 5 — and
implementing the understandable part produces badly made code with an air of
progress. Partial ≠ safe.

> "I understand items 1, 2, 3 and 6. I need clarification on 4 and 5 before
> implementing."

## Technical push-back

Push-back is evidence, not emotion. It is an obligation of the receiver when
the finding is incorrect, not a discourtesy: implementing a false finding
freezes the error inside the code.

**When it proceeds** (any of these):

1. It breaks existing functionality (or security).
2. The sender lacks context (didn't see a file, a test, a decision).
3. YAGNI: it asks to "properly implement something" nobody uses. Check with a grep on the
   codebase: if the endpoint/module/flag has no real uses, the right push-back
   is to propose deleting, not building.
4. It is incorrect for the stack (a pattern that doesn't apply to the project's
   framework, an API that doesn't exist in the version in use).
5. Legacy/compatibility: the ugly code exists for a documented reason.
6. It contradicts a registered architectural decision (ADR, systemPatterns) —
   disagreement with an ADR is resolved through the ADR process, not in the fix.

**How:** cited evidence `file:line`, a test that fails or passes, command
output. No emotional defense, no "I think", no defensive tone.

**Destination depending on the source:**

- **To the reviewer (Stage 4):** the push-back asks for reconsideration; the reviewer
  evaluates it with steelman and re-issues the verdict with the same
  4-field tuple (`verdict-tuple.md`). It is a re-judging with new evidence, not
  a tone negotiation.
- **Persistent disagreement** (the reviewer maintains it, the receiver too): the
  user mediates. The orchestrator brings both positions with their evidence to the user,
  who decides with full context.

## Factual correction of one's own push-back

If you pushed back and were wrong — you verified and the finding was correct —,
correct it without over-explaining:

✅ "Factual correction: I verified `X` and it does `Y`. My initial reading erred
because <reason in one line>. Implementing."

❌ Long apology, defense of why the push-back was reasonable,
over-explanation. The reviewer's reversals count as a yellow flag; yours
do too: if your push-back was incorrect, factual correction and move on.

## Feedback source matrix

Not all feedback arrives with the same epistemic authority:

| Source | Attitude | Protocol |
|---|---|---|
| User | Trusted — execute after understanding | Except R4 (below): the strategic decision gets executed. If the requirement is ambiguous, it gets clarified; the decision is not discussed |
| Reviewer (Stage 4) | Verify against the code | Full 4-step sequence; push-back with evidence if applicable |
| External PR | Maximum skepticism | Does it break anything? Why does the current thing exist? Does it cover all cases? External feedback = suggestions to evaluate, not orders to follow; doubt the sender's context first, verify threefold |

## R4 — Approved strategic decisions: no post-hoc push-back

Against strategic decisions ALREADY approved by the user there is no post-hoc
push-back: they get executed or escalated through another channel. The technical objection lives
BEFORE the approval (Socratic brainstorm, stages 1-2 of the cycle). Reopening
the decision upon receiving feedback is appealing the rule after the play — the
right channel is proposing a new ADR or raising it in the next feature,
not blocking the current fix.

## Persistence — learned pattern goes to the scribe

If the feedback reveals a reusable project pattern (convention, recurring
trap, style rule), the receiver NEVER edits memory inline (neither
Memory Bank nor skills): write a **note to the orchestrator for the scribe**
(destination: `docs/systemPatterns.md`) and continue with the fixes. The Scribe
pattern exists so memory gets updated with the user's approval, not in the
heat of the fix.

## CDAD's structural advantage

Single-session skills fight sycophancy with rules inside the
same session that dilutes them. CDAD has two structural antidotes:

1. **The handoff packet re-invokes the protocol with fresh tokens.** The rule
   travels IN FULL with each task (intact transmission: `stage-4-review.md` and
   `handoff-prompts.md`) — a direct antidote to the dilution in long sessions
   that Morricone documented.
2. **The isolated session arrives fresh, without emotional investment.** The receiver
   didn't write the code in that session nor witness the review discussion:
   it arrives without the defended position that feeds the confirmation loop.
   Seeing one's own finding refuted costs less when nobody has a face to save.

Document this as a differentiating advantage when comparing CDAD with
prompt-only alternatives.

## No exit clauses (R2)

The rules of this protocol are NOT written with escapes like "if the user
insists, give in" or "unless it's really important". Native compliance
(RLHF) already caves at the first push: the exit clause is not a
valve of wisdom, it is the permission that accelerates capitulation (Morricone
finding, verified in its A/B). The protocol's rigidity is the valve: if
the real context demands an exception, the exception gets discussed with the user
explicitly — it doesn't slip in through a pre-written clause.

## Anti-rationalization table

| Typical excuse | Refutation |
|---|---|
| "It's a minor suggestion, I'll implement it right away" | Minor ≠ verified. The 4-step sequence has no fast mode: verify anyway |
| "The reviewer has more context than I do" | It may be true and even so the finding may be false. Verify against real code: that decides |
| "I thank them to be cordial" | Thanking reinforces the performative pattern. Technical cordiality is the well-placed correction: "Fixed at <location>: <what changed>" |
| "I'll implement what I understand and ask about the rest" | The items may be related; partial = badly implemented. Stop EVERYTHING and clarify before touching anything |
| "The push-back is confrontational" | It is evidence, not emotion: `file:line`, test, output. The real discourtesy would be letting a false finding slide |
| "I already pushed back once, I'll just insist" | The reviewer's reversals count, and so do yours: if your push-back was incorrect, factual correction and move on. If the disagreement persists, the user mediates |
| "The user told me, it's unappealable" | Trusted ≠ unread: it gets executed after understanding. R4 covers strategic decisions, not understanding the requirement |
| "The feedback is long, I'll start and finish reading later" | Reading it all without reacting is step 1: the order (blocking → simple → complex) comes from reading everything |

## When it does NOT apply

1. **Strategic decisions already approved** (R4): scope, priority,
   module choice, spec approval — they get executed or escalated through another
   channel; the technical objection goes before the approval.
2. **User feedback on scope and priority**: it is their decision by
   design (non-delegable approval). Understand the requirement and execute; the
   factual discussion belongs to stages 1-2, not to receiving.

Outside these two cases, the protocol applies in full: read it all without
reacting → restate → verify against the real code → implement one
fix at a time with verification.
