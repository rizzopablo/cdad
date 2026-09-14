# Stage 4 — Two-layer review

Layer 1: the reviewer does an exhaustive pass with the spec in context. Layer 2: the user (human or higher-hierarchy autonomous agent) validates the prioritization.

## Your role as orchestrator

You do NOT do the review. You coordinate:

1. Emit handoff to the **reviewer** (layer 1) with diff + spec + boundaries + conventions.
2. Validate the report at re-entry.
3. Pass the report to the **user to validate the prioritization** (layer 2, by default non-delegable; see the exception below if the user explicitly requested delegating it to an agent for this feature).
4. If there are blockings to apply: handoff back to implementer.
5. Stage closure when all blockings are resolved or dismissed.

## Layer 1 — Handoff to the reviewer

Load `references/handoff-prompts.md` section "Reviewer (Stage 4)".

Generate the packet with:

- **Verdict contract (verdict-tuple.md):** reference the 4-field tuple — every reviewer finding emits a Verdict (BLOCKING|OPTIONAL|ABSTAIN) + Bucket h|m|l by observables + rationale + provenance. The bucket is derived by the reviewer by deterministic rule (model family, full diff, grounded rationale, spec in context), never by elicited confidence. The Abstentions section is always reported (empty if not applicable).
- Full diff of the feature (`git diff <base>..HEAD`).
- Approved spec (`docs/specs/<feat>/spec.md`).
- Interface / contract.
- `.importlinter` or equivalent.
- Conventions (`AGENTS.md`, `CONTRIBUTING.md`, `docs/systemPatterns.md`).
- Explicit request for the test↔postcondition audit: every test in the diff must map to a postcondition of the spec (flag the superfluous ones) and none may depend on internal structure (flag mocks over plumbing, see AP-14 in `anti-patterns.md`). The reviewer does this audit precisely because it is a session other than the one that wrote the tests — do not delegate it back to the test-writer.

**Recommendation to the user before the packet**: *"Ideally the reviewer runs with a model different from the implementer's. If your environment allows it (changing the model in a new chat), take advantage of it. If not, it still works."*

Deliver the packet, end the turn.

### Re-entry

Load `re-entry.md` section "Reviewer". Validate the report structure.

If it passes: pass it to the user for layer 2.

## Layer 2 — Validation (by the user by default; delegable only under an explicit request)

**General rule: the user validates the prioritization** (human or higher-hierarchy autonomous agent owning the process). Tell the user:

> *"Report at `docs/specs/<feat>/review.md`: <X> blockings, <Y> optionals. Your job: read the report (not the full diff) and validate the prioritization. For each blocking: is it genuinely blocking, or is there context the reviewer doesn't have? For each optional: apply or discard? When you're done, send me the decisions."*

**When the user IS a higher-hierarchy autonomous agent** (owner of the
process that orchestrates this cycle, e.g. from an external orchestrating
process), it validates directly — there is no explicit delegation
ceremony to fulfill: it is the owner. BUT the severity matrix below is
non-negotiable: **security risk and functional bug are blockings without exceptions**,
even if the one validating is an agent — delegation grants authority to
*prioritize*, not to lower the severity of what the matrix marks as
non-negotiable. And when in doubt, the user is asked anyway (severity is not lowered for being an agent).

### Exception: explicit delegation to an expert agent

As in Stage 2 (see `stage-2-specification.md`, "Exception: explicit delegation to an expert agent"), this applies only if the user, **for this feature or specific stage**, explicitly requested that an agent validate the prioritization on their behalf. It is not assumed, not activated by default, and you do not initiate it.

With the explicit request, before validating run the self-assessment: do you lack client/product context to judge whether a blocking is genuine? is there anything in the report you would prefer the user to see (security, breaking change, something affecting a final client)? Note that the severity matrix below already treats **security risk and functional bug as blockings without exceptions** — delegation does not change that; delegation gives you authority to *prioritize*, not to lower the severity of something the matrix marks as non-negotiable.

If you have doubts: you don't validate, the user is asked anyway. If you validate: mark in `review.md` and in `stage_history` that the prioritization was agent-delegated, who requested it and when — the same traceability standard as in Stage 2.

### When the user comes back with the prioritization

Apply the default severity matrix as a sanity check:

| Type | Default severity | Exception |
|------|----------------------|-----------|
| Spec divergence | Blocking | Only if the spec was outdated |
| Boundary violation | Blocking | Only if an ADR authorizes it |
| Security risk | Blocking | No exceptions |
| Functional bug | Blocking | No exceptions |
| Style inconsistency | Optional | Blocking if massive |
| Simplification | Optional | Blocking if problematic complexity |
| Suggested additional feature | Discard | — |

If the user marked as "non-blocking" something the matrix says is blocking (e.g. spec divergence), ask for the reason and record it in `review.md` as a note.

If you detect bias (user wanting to close quickly, systematically marking blockings as optional):

> *"If you doubt whether a blocking is genuine, err on the side of treating it as blocking. The cost of an extra iteration is low; the cost of merging a bug is high."*

### Transmitting the feedback to the implementer (R1)

When the prioritization produces fixes, the orchestrator TRANSMITS the **full** feedback of the reviewer and of the user in the handoff packet: the findings travel attached exactly as they were written (with their rationale and provenance), **with no editing that softens** — paraphrasing in a friendly tone, trimming the evidence, or "summarizing" the finding softens exactly the signal the receiver needs in order to verify. The user's feedback (the context that motivated the prioritization) travels in the same packet.

The packet instructs the receiver to apply `references/receiving-feedback.md` **before touching code**: the sequence read it fully without reacting → restate the requirement → verify against the real code → implement one fix at a time (blockings → simple → complex, suite green after each). If the receiver issues technical push-back with evidence, the reviewer reconsiders it (`verdict-tuple.md`); persistent disagreement → the user mediates. The fix session arrives fresh — that is the structural advantage of the cycle: the packet re-invokes the protocol with fresh tokens and the receiver arrives without emotional investment.

## Evidence reuse (the reviewer's budget of 0 runs)

If the code tree is identical to the one from the gate's evidence run
(verifiable: `git diff --stat <commit-of-the-run>..HEAD` shows only
`[STATE]`/docs commits), the reviewer **cites the recorded log (path + line)
instead of re-running the suite** — run budget of 0. Only if the tree
changed does ONE new full run apply. Static analyzers
(lint, import-linter) do not consume budget. Requirement: every gate
run is recorded with its log and its commit (state file or commit
message). In Odoo, details in `odoo-make-env/references/run-budget-protocol.md`.

## Loop with Stage 3

If there are blockings to apply (or accepted optionals):

1. Note the prioritized list of fixes.
2. Emit handoff to implementer with the list.
3. The suite must stay green after every fix. If a fix requires a behavior change, that means the **spec needs updating** → back to Stage 2.
4. After the fixes: ideally another pass by the reviewer. In small features with mechanical fixes, you can skip it (the user's call).

## 🛑 Exit gate (Stage 4 → Stage 5)

- [ ] `docs/specs/<feat>/review.md` exists.
- [ ] Blockings resolved or explicitly dismissed with a written reason.
- [ ] Prioritization validated by the user, or agent-delegated with an explicit request registered in `stage_history` (see the exception in §2.3/Layer 2 — never self-granted, AP-15).
- [ ] Suite still green after the fixes.

When all OK: update state (`current_stage: merge`). Announce the transition. Emit handoff to scribe (Stage 5).

## Main anti-pattern

**Skipping the review on small features.** Even a brief review over 30 lines is worth it.
