# Stage 2 — Specification

Turn a functional idea into an implementable spec with no ambiguity.

## Your role as orchestrator

You do NOT write the spec. You coordinate:

1. Emit handoff to **architect in brainstorm mode** (Socratic questions).
2. Validate brainstorm closure at re-entry.
3. Emit handoff to **architect in spec-writing mode**.
4. Validate the spec draft at re-entry.
5. Pass the spec to the **user (human or higher-hierarchy autonomous agent) for approval** (by default non-delegable; see the exception in 2.3 if the user explicitly requested delegating it to an agent for this feature).
6. When the approval arrives (from the user, or agent-delegated under an explicit request), close the stage.

## Sub-phase 2.1 — Socratic brainstorm

Load `references/handoff-prompts.md` section "Architect (Stage 2 — Socratic brainstorm)". Generate the packet with:

- Preliminary functional description (from Stage 1).
- `docs/landscape.md` and the per-feature discovery output ("Technical context" section in the draft).
- `docs/systemPatterns.md`.

Deliver the packet and end the turn.

### Re-entry

When the architect closes the brainstorm with a summary of decisions, validate it (see `re-entry.md` section "Architect — brainstorm"). If it passes, emit the handoff for spec writing.

## Sub-phase 2.2 — Spec writing

Handoff packet for the architect in spec-writing mode with:

- Brainstorm summary (from the previous re-entry).
- Content of `assets/spec-template/spec.md`.
- `docs/systemPatterns.md`.

Deliver the packet, end the turn.

### Re-entry

Validate the spec draft (see `re-entry.md` section "Architect — spec draft").

If it passes: pass it to the user for approval.

## Sub-phase 2.3 — Approval (by the user by default; delegable only under an explicit request)

**General rule: approval belongs to the user** (human or higher-hierarchy autonomous agent owning the process). Tell the user:

> *"Spec is at `docs/specs/<NNN>/spec.md`. Review it: (a) each postcondition is what you want, (b) measurable acceptance criteria, (c) complete out of scope. If it's OK, add the approval mark at the end of the file (`Status: Approved by <you> on <date>`) or in frontmatter (`approved_by: <you>`, `approved_at: <date>`). Let me know when it's done."*

**If the user asks you to approve it** without having explicitly requested it before for this feature/stage: decline politely.

> *"Spec approval requires your judgment about the domain, the client, and the product. I can propose changes if you want, but the approved mark goes with your name — unless you want to explicitly delegate it to an agent for this feature."*

**When the user IS a higher-hierarchy autonomous agent** (owner of the
process that orchestrates this cycle, e.g. from an external orchestrating
process), it approves directly — there is no explicit delegation ceremony
to fulfill: it is the owner. Apply the same criteria as a human: run the
self-assessment below before approving and do not lower the severity for being an agent.

### Exception: explicit delegation to an expert agent

If the user, **for this feature or specific stage**, explicitly requests that an agent (you as orchestrator, or another agent with delegated judgment) do the review and approve on their behalf — only then does this exception apply. It is not activated by default, is not assumed from a previous request in another feature, and you do not activate it on your own initiative. (When the user is a higher-hierarchy agent, this ceremony does not apply: it approves directly as the owner.)

With the explicit request in hand, before approving run the same self-assessment you would ask of the user — but applied to yourself:

1. Do you have sufficient context of the domain, the client, and the product to judge this spec, or are you missing information that only the user has?
2. Are the postconditions what the user needs, or just what the user wrote? (Real difference: repeating the spec is not approving it.)
3. Is there anything in this spec with hard-to-revert consequences (breaking changes, security, scope with a final client) where you would still prefer a second look from the user?

**If you have reasonable doubts on any of the three points: you do not approve.** Explain it to the user and ask for the user's approval, even if delegation is enabled for this feature — the explicit request gives you permission, it does not oblige you to use it.

If you approve: explicitly mark the source of the approval, never as if it came from the user:

```
Status: Approved by <your model/agent identifier> (agent-delegated, explicit request from <user> on <date>) on <date>
```

Also register in the state file's `stage_history` an entry with `"approved_by"`, `"delegated": true`, and `"requested_by"`. The traceability of it having been a delegated approval — and not the user's — must be as clear as the traceability of the approval itself (same principle as AP-6).

**If the user wants to skip approval** (neither the user's nor an explicit agent-delegated one):

> *"Approval is what defines whether the spec captures what you need. Without that mark, in Stage 4 we won't know which version to validate the code against. Three minutes of reading and approving saves you rework in Stage 3 or 4."*

## Variants by size

- **Trivial** (point fix): the spec can be one paragraph + one failing test. Still brainstorm + approval, but shorter.
- **Medium** (most cases): standard format.
- **Complex** (multiple components): the architect also produces `plan.md` following the "Planning for complex features" section (below).

Decide it with the user at the start of the stage.

## Why spec clarity is not negotiable

Stage 3 uses contract tests, not exhaustive coverage (see "Test convention" in `stage-3-tdd.md`). That means the precision that an exhaustive suite would normally provide has to come from the spec. A vague postcondition ("the system must handle errors well") cannot be turned into a verifiable contract test — the test-writer ends up interpreting, and that interpretation may not be what the user needed (AP-13, Garbage Cascade). Every postcondition must be able to answer: *what observable effect, exactly, confirms that this was satisfied?*

## Planning for complex features

Trigger: the spec is complex (multiple components). The architect produces `plan.md` in addition to the spec, before closing Stage 2. The plan is approved together with the spec — a single user action — and the 2→3 gate includes the approved plan when it exists.

### Task size

The task is the smallest unit that closes in its own mini TDD cycle (its own RED→GREEN). Its size is judged by **total cost**, not by a count: the unit is invalid when any of these four verifiable conditions holds, and the criterion reuses — by reference, never re-stated as a score or a number — the «coordination cost» criterion already declared in the planning contract (§5).

- **(a) Rejectable without its neighbor.** A reviewer could not reject the unit without also rejecting its neighbor: if the refusal necessarily drags the adjacent unit along, the boundary is wrong.
- **(b) Closes its own verifiable result with its named consumer.** The unit closes its own verifiable result with its named consumer; with no named consumer it is not a unit.
- **(c) Fixed costs exceed the marginal progress.** Its fixed costs — planning, session opening, independent review and integration — exceed the marginal progress it delivers: the handoffs, reloads and extra review it forces cost more than the small advance it produces.
- **(d) Fragmentation.** The unit does not move the feature toward a verifiable result: it fragments the work without advancing any observable outcome.

Setup, configuration, and scaffolding are folded into the unit that needs them — never a loose "setup" task. Neither so small that it fragments the review, nor so large that a part can't be rejected without dragging the rest along. Replanning a unit whose boundary turns out wrong follows the retry rule owned by `references/re-entry.md` (PD-4), consumed here by reference and never restated; that rule preserves the unit's objective, dependencies and reasons and never rewrites a dispatched contract without a declared reconciliation.

### Task structure

Each task in the plan declares:

- **Files**: exact paths, marked Create / Modify / Test.
- **Consumes / Produces**: the public contract — exact signatures of what this task receives from the previous ones and of what it exposes to the next ones. The implementer of a task only sees its own task; that is why the signatures must be here, and be usable by the test-writer (the contract, not the body).
- **Validation plan**: the focal tests, the affected regressions, the integration gate and who runs each check — or an observable check instead for a code-less task. The field names and the canonical `plan-tasks` block format live in one place and are only referenced, never copied: `docs/epics/epic-004-single-source-planning/planning-contract-draft.md` §4.1.
- **TDD steps**: the task's red→green loop, with the test first.

### Progressive detail (canonical rule)

The plan declares the **objective and dependencies of every unit in full**, and
the **detail (contract, signatures and tests) only of the next batch**: a unit
whose detail is not yet the next batch declares its uncertainty with an owner
and a resolution condition instead of false detail.

Per task, the canonical `plan-tasks` block admits a closed marker `detail` with
the values `"next"` (the default) and `"planned"`:

- `detail` `"next"`, or no marker at all: the task keeps declaring its per-task
  validation plan — `focal_tests` or `observable_checks`, `regressions` and
  `integration_gate`.
- `detail` `"planned"`: the task declares `objective`, `depends_on`,
  `uncertainty`, `owner` and `resolves_when`, and declares no per-task
  validation plan.

This rule is stated once, here; every consumer (the block's format declaration,
the plan review) references it and never copies it.

### The central rule: the plan defines the CONTRACT, not the code

*The plan defines the CONTRACT — tests with real assertions, exact commands, observable behavior (3-5 bullets verifiable against the test) — and NEVER speculative implementation code.* Writing the implementation twice (in the plan and in the execution) reverses TDD and bakes in assumptions that the planner guessed but the implementer never verified. The specific behavior of a task is the DELTA relative to the existing analog in the repo: if you have to enumerate more than 3-5 behavior bullets, the implementation is already being re-derived in markdown — cut and split the task.

Consequence for test-writer isolation: since the plan contains no implementation, the test-writer can see the whole plan without violating its restriction. The plan is the interface, not the code.

### No placeholders

These phrases in a plan are a plan failure:

- "TBD", "TODO", "implement later".
- "handle edge cases appropriately" (and every variant of vague handling).
- "similar to Task N" — repeating another task's code; if it is analogous, name the analog and describe the delta.
- Steps that describe WHAT to do without showing HOW to verify it.
- References to types or signatures not defined in any task.

Nuance: a vagueness WITH a behavior contract is not a placeholder. The forbidden pattern is vagueness without a contract — if the observable bullet is there, the impl can decide internal details.

### Self-review (run by the architect before closing Stage 2)

1. **Spec coverage**: every postcondition → at least 1 task (≥1 task). If a postcondition has no task, the plan is incomplete; if a task maps to no postcondition, it is superfluous.
2. **Placeholder scan**: search for the forbidden phrases above throughout the plan.
3. **Signature consistency across tasks**: a function called `clearLayers` in task 2 and `clearFullLayers` in task 5 is a plan bug — fix it here, not in GREEN.

### Global constraints

The project-wide constraints of the spec (versions, naming, platform, etc.) are copied verbatim into the plan header. Every task includes them implicitly — no task may contradict or re-interpret them.

### Feature plan template

The plan is drafted from `assets/feature-plan-template.md`: the feature's ficha plus the canonical `plan-tasks` block. The template is a consumer of the format declared once in the planning contract draft's §4.1 (referenced above); it references that declaration and never restates it.

The feature's **minimum acceptance-of-use recipe** — contract / integration / use, each layer with its producer, its evaluating actor and its evidence — is anchored to the same ficha by reference: the plan names the recipe and the Stage 4 gate uses it. Its detail lives with the feature's acceptance material and is neither copied nor expanded here.

## 🛑 Exit gate (Stage 2 → Stage 3)

- [ ] `docs/specs/<NNN-feature-id>/spec.md` exists.
- [ ] Four minimum sections present and not placeholders.
- [ ] Numbered, verifiable postconditions.
- [ ] Measurable acceptance criteria.
- [ ] Unequivocal user approval mark.
- [ ] If the spec is complex (multiple components): `plan.md` exists, passed the self-review, and is approved together with the spec.

When all OK: update the state file (`current_stage: tdd`, `tdd_substage: red`, `active_feature: <feat-id>`, register `approved_by` in `stage_history`). Announce the transition. Emit handoff to test-writer (RED) for postcondition 1.

## If something not contemplated in the spec comes up during implementation

Rule: it is NOT silently added to the code. You go back to Stage 2: update the spec, commit the change (`docs: update spec — add postcondition X`), re-approve. Only then may the implementer touch the case.

## Anti-patterns

- **AP-5**: skipping the spec because "it's simple". Minimum: one paragraph + failing test, with approval.
- **AP-6**: spec approved silently with no explicit mark. Without the mark, you don't advance.
- **AP-10**: delegating approval to the LLM WITHOUT a previous explicit request from the user for this feature/stage (default: non-delegable). With an explicit request, see "Exception: explicit delegation to an expert agent" above — the exception does not apply on its own initiative (AP-15).
