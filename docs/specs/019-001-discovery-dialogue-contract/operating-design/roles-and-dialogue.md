# Roles and the mediated dialogue (PC-1, PC-2)

Locators are at revision `64aa4670`. Status: proposal. Current role contracts remain effective until activation.

## 1. Who does what in the normal cycle (proposed)

| Activity | Proposed owner | Today (evidence) |
|---|---|---|
| Functional questions: problem, journey, expected result, boundaries, behavioural choices | **Orchestrator**, to the authorized owner (the process owner) | Stage 2 hands this to the architect in brainstorm mode: `skills/cdad-cycle/references/stage-2-specification.md:9,17-29`; the legacy brainstorm prompt tells the architect to ask questions and wait: `skills/cdad-cycle/references/handoff-prompts.md:242-258` |
| Technical investigation of existing behaviour and feasibility | **Architect** (read-only) | `sources/roles/architect.md:105` |
| Challenge, alternatives, questions for the owner | **Architect**, returned to the orchestrator as findings | `sources/roles/architect.md:73` ("first you ask") |
| Recording of owner answers and orchestration notes | **Orchestrator**, attributed | No dialogue record exists; decision transport is partial: `current_decisions` and brainstorm summaries (see `handoff-fidelity.md` §2) |
| Readiness check before drafting | **Orchestrator**, at brainstorm re-entry | `skills/cdad-cycle/references/re-entry.md:230-238` |
| Spec draft (returned as final text, not written into the product) | **Architect** | `sources/roles/architect.md:105`; `skills/cdad-cycle/references/stage-2-specification.md:31-39` |
| Independent draft review | **Reviewer**, in a session separate from the author | `stage-2-specification.md:47-75`; `re-entry.md:266-278` |
| Approval of the spec | **Authorized approver**: the owner, or a higher-hierarchy autonomous owner. The orchestrator approves only under the sole exception below | `stage-2-specification.md:14`, §2.3 (`:76-110`); `re-entry.md:251-253` |
| Tests (stage 3) | **Test-writer** — unchanged | `sources/roles/orchestrator.md:298-307` (anti-bias invariants) |
| Implementation (stage 3) | **Implementer** — unchanged | same |

The "authorized approver" is a role of the cycle, not a person named in this design.

### The single approval boundary

This rule applies to every section of this design, and to the activation map. Other sections
point here and do not restate it.

1. **Ordinary rule.** The orchestrator never approves a specification by default. Approval belongs to the owner, or to a higher-hierarchy autonomous owner (`stage-2-specification.md` §2.3, `:76-90`).
2. **Sole exception: explicit recorded delegation.** The orchestrator, or another agent with delegated judgment, approves only when all of the following hold:
   - The owner explicitly requested it, for this feature or a specific stage (`stage-2-specification.md:92-94`). It is never inferred from another feature or stage, and the orchestrator never activates it on its own initiative.
   - The request is recorded in a durable artifact that the approval cites, with its file, section and quoted words. For epic 019 that artifact is `docs/epics/epic-019-discovery-dialogue/execution.md:8-14`.
   - The delegation is limited to the scope and terms of the recorded request. It never covers publication, deployment or scope expansion, which need the owner's instruction. Epic 019's grant, in that artifact, is limited to that epic and ends at its closure, cancellation or revocation.
   - The three self-assessment questions of `stage-2-specification.md` (`:96-102`) are answered for the spec. Any doubt means no approval.
   - The approval is registered as agent-delegated, not as the owner's. The Status line names the agent, `agent-delegated`, the requester and the date. The state's `stage_history` entry records `approved_by`, `delegated: true` and `requested_by` (`stage-2-specification.md:103-110`).
3. **Anything else is not approval.** Without the exception, the orchestrator reports readiness, dispatches the review and passes the draft to the approver. It does not mark the draft approved.

A concrete grant, such as epic 019's in `docs/epics/epic-019-discovery-dialogue/execution.md:8-14`, is applied as that grant, within its recorded terms, and never generalizes. This design does not extend any delegation.

## 2. The mediated round trip

No participant talks directly to another participant. The loop is:

1. **Owner → orchestrator.** The owner states the need, the outcome and the boundaries.
2. **Orchestrator asks.** It asks the functional questions it can ask. It does not answer technical questions itself.
3. **Orchestrator → architect (only when needed).** A consequential uncertainty or missing evidence triggers a targeted technical consultation: investigate, challenge, propose alternatives. A consultation is not triggered by every question (`lightweight-paths.md` §3, rule D4).
4. **Architect → orchestrator.** Findings come back with the architect's authorship preserved. They are technical evidence or proposals, not owner decisions.
5. **Orchestrator → owner.** The orchestrator presents the consequential question to the owner, in its own words, citing the architect's finding by reference.
6. **Owner → orchestrator.** The owner answers. The orchestrator records the answer, attributed to the owner's message.
7. **Orchestrator → architect (when further technical work depends on the answer).** The attributed answer goes to the architect in a new turn. The architect never receives the owner's conversation.
8. The loop repeats until the readiness check passes (`readiness-and-approval.md` §2).

Nothing in this design claims a direct architect–owner conversation. A
transport difference between runtimes (for example, whether a subagent can ask
a question interactively) is a transport concern, not a permission. The
discovery reports that the question loop is underspecified, not proven
impossible (`discovery.md` §3.B). This design specifies the loop; it does not
assume runtime capability.

## 3. Boundary deltas required for activation (PC-2)

These are the changes that activation must make to canonical sources. Each row says
what the current text states, what changes, and what must not change.

### Orchestrator — `sources/roles/orchestrator.md`

- **Current:** "do NOT write tests, do NOT implement, do NOT refactor, do NOT review the full diff, do NOT approve specs" (`:128-131`, the rule opened by "Operating rules (strict):"). "If the user asks for role work → delegate" (`:135-137`). The own-contract row forbids "role work inline (tests, implementation, spec approval…)" (`:300-302`).
- **Change (three deltas, nothing else: a dialogue allowance, a recording allowance bounded to the architect's report section and the Dialogue context section, and the approval exception added to the prohibition):**
  1. A bounded allowance: during the stage-2 brainstorm sub-phase the orchestrator conducts the functional dialogue with the owner. This is the kind of allowance that stage 1 already gives for *initial* discovery (`skills/cdad-cycle/references/stage-1-discovery.md:14-30`). It does not extend to stage-2 technical work.
  2. A recording allowance, made explicit and bounded. `sources/roles/orchestrator.md:302` already lets the orchestrator materialize read-only artifacts and edit `docs/**`; this delta does not add that power. It states that, in stage 2, the orchestrator materializes the architect's per-feature report unaltered in its own section of `docs/specs/<feature>/discovery.md`, and writes owner answers, corrections and its own notes, attributed, only in the Dialogue context section of that file, creating the file if it does not exist. That limit covers only the authorship and location of the dialogue record and of the architect's report. Every other write or materialization the cycle already authorizes stays allowed, including `plan-review.md` (E5), the independent report (`verification.md:16-19`), the spec draft and the approval records (`readiness-and-approval.md` §3). The precedent is commit `c1016fb5`, where the orchestrator materialized the architect's discovery report there.
  3. The approval exception of §1, added to the existing prohibition "do NOT approve specs" (`sources/roles/orchestrator.md:128-131`). The prohibition stays the rule. The exception is the only way the orchestrator approves.
- **Must not change:** the orchestrator never answers technical questions itself; never authors or alters the spec's content (its writes to the spec are only those the cycle already authorizes); never authors or alters the architect's report, and only materializes it unaltered; never writes tests or code; never performs the independent review; never approves a spec outside the exception of §1.

### Architect — `sources/roles/architect.md`

- **Current:** the contract row says "technical mapping + Socratic brainstorm + spec draft" (`:105`). The brainstorm turn says "first you ask" (`:73`).
- **Change:** rename the brainstorm function to *targeted technical consultation*: investigate existing behaviour, challenge assumptions, offer alternatives, and return findings and questions **to the orchestrator**. The architect does not hold the functional interview with the owner. Questions for the owner are phrased by the architect and asked by the orchestrator.
- **Must not change:** read-only on product and repository; never writes the product; never approves its own proposal or spec (`:107-108`).

### Architect, Odoo variant — `sources/roles/architect.md:155-165`; `skills/odoo-architect/SKILL.md:138-147`

- **Current:** the Odoo brainstorm asks configuration-versus-custom, OCA/core reuse, and which SPoC and PL validate the logic.
- **Change:** the technical part (configuration versus custom, OCA/core reuse) stays in the architect's consultation. The questions about roles that belong to the owner side (which SPoC validates, which PL defines the scope) are routed through the orchestrator as owner questions. The domain guidance does not create a second interlocutor.

### Unchanged roles

Test-writer, implementer and reviewer keep their contracts. The reviewer's
independence from the author is preserved by the existing stage-2 draft review
(`stage-2-specification.md:47-50`).

## 4. What this section does not do

- It does not change any permission. The rows above are the **proposed** deltas. Activation happens only through the 019-002 handoff (`activation-handoff-019-002.md`).
- An explanatory dialogue document cannot make these deltas effective. `activation-map.md` lists the canonical owners that must change, and the consumers that must follow them.
