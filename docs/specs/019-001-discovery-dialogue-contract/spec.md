# Specification: CDAD discovery dialogue operating design

**Status: Approved by the CDAD orchestrator under <owner>'s delegated HITL on 2026-11-15; amended 2026-11-15 under the owner decision (review is the verification), after independent review.**

## Functional description

**Actor:** a process owner working through the CDAD orchestrator.

**Goal:** explain the desired outcome once, resolve consequential choices with appropriate technical help, and receive a faithful specification without managing conversations between agents.

**Legitimate starting point:** an authorized normal-cycle feature or deliberately bounded lightweight task. Existing role contracts remain effective until separately approved activation.

**First useful result:** a reviewed operating design that tells agents who converses, investigates, records, drafts, checks readiness and approves—and demonstrates the distinction with concrete examples.

This feature produces the documentary design. Feature `019-002-effective-discovery-instructions` owns coherent activation, executable delivery changes, the permanent idle/done correction and observed end-to-end acceptance against effective instructions.

## Scope

The design covers:

- Normal-cycle functional dialogue and targeted technical consultation.
- The normal cycle’s trivial-spec variant and the standalone lightweight entry point.
- Partial answers, proposed defaults, corrections, conflicting statements and technical unknowns.
- Recoverable context, handoff content and readiness for drafting.
- Independent draft review and explicit approval.
- Canonical ownership and affected consumers.
- Acceptance obligations passed to feature 019-002.

It does not change current role powers or executable behavior.

## Admitted sources and verification limits

Authorized backing:

1. The packet’s `UNIT-CONTRACT.md`, SHA-256 `8d927ba27df514d17bce66bea390ef5fbe67407e65b8988025b6c0342b1acfdd`.
2. `docs/specs/019-001-discovery-dialogue-contract/discovery.md`, SHA-256 `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43`.
3. `docs/epics/epic-019-discovery-dialogue/{plan,execution}.md`.
4. Relevant repository role sources, references, packet sources, generator, delivery code and existing tests at the examined revision.

Discovery’s citations describe its examined revision; later claims must identify the revision actually checked. External conversations, global installations and assumed runtime capabilities are not backing unless separately admitted and recoverable.

Verification establishes documentary fidelity, consistency and an actionable activation contract. It does not establish deployment, universal runtime compatibility, or successful agent execution of instructions that have not been activated.

## Documentary product and protected inputs

**Proposed documentary product scope:**

`docs/specs/019-001-discovery-dialogue-contract/operating-design/`

The directory contains the operating design and its worked examples. It is separate from this specification, discovery, approved epic sources, the protected review checklist and other acceptance inputs.

Before any product is produced, the orchestrator materializes the independent reviewer’s contract-derived checklist outside the product directory as a protected acceptance input. Independent review reports are also materialized outside that directory. The producer never edits the checklist, admitted sources or acceptance contract. A necessary checklist correction returns to the independent reviewer; a contract change requires the applicable explicit approval.

This declaration grants no write permission in the current architect session.

## Proposed design decisions

These choices require explicit acceptance; they are not previously approved decisions.

### D1 — One functional interlocutor, bounded technical delegation

The orchestrator conducts functional discovery: the problem, journey, expected result, boundaries and behavioral choices.

The architect investigates affected existing behavior and feasibility, challenges assumptions, supplies alternatives and questions, and drafts the specification. The orchestrator does not substitute for that technical work, write tests, implement, or perform independent review.

A technical consultation returns findings to the orchestrator. The orchestrator presents the consequential question to the owner and returns the attributed answer when further architect work is needed. No participant claims a direct architect–owner conversation that did not occur.

**Criterion:** prefer one shared interaction contract over separate runtime-specific conversational protocols. Runtime transport differences remain transport concerns, not permission grants.

### D2 — Reuse existing context rather than introduce a dialogue subsystem

In the normal cycle, keep a clearly attributed dialogue-context section in the existing per-feature discovery artifact. Preserve the technical report’s authorship; distinguish subsequently recorded owner answers and orchestration notes.

For standalone lightweight work, use the already authorized minimal specification or task artifact. Do not require a separate dialogue file merely to satisfy a template.

Recoverable context contains only what is relevant:

- The intended result and boundaries.
- Confirmed decisions and their recoverable authority.
- Interpretations and proposals that have not been accepted.
- Unanswered consequential choices.
- Technical findings and unresolved assumptions.
- Corrections identifying what they replace.
- The next action and who is responsible.

These are documentary distinctions, not new state fields or packet schema values. Existing `current_decisions` transports governing decisions; it must not be overloaded with proposed defaults or unanswered questions.

**Criterion:** reuse minimizes context and maintenance cost while preserving provenance and corrections. A separate record would require evidence that existing artifacts cannot serve the handoff.

### D3 — Readiness is checked, not inferred from conversation length

The orchestrator checks readiness for drafting:

- Consequential behavioral choices have explicit answers or explicit scope exclusions.
- The recorded summary does not extend the owner’s answers.
- Corrections are reflected in the current understanding.
- Relevant technical uncertainty has been investigated, bounded, or identified as blocking.
- Drafting inputs are recoverable by a fresh architect session.

An explicit answer need not receive a redundant confirmation ritual. Ask again when the summary introduces an interpretation, omits a qualification, or conflicts with another instruction. Silence never accepts a proposal.

An unanswered behavioral choice that changes the promised result blocks a claim of readiness. A technical detail may remain `VERIFY` only when it does not prevent an unambiguous, verifiable commitment.

Readiness for drafting, agreement with a summary, independent review and specification approval remain distinct.

### D4 — Share fidelity rules, not identical ceremony

Supported lightweight surfaces are distinguished:

- **Trivial normal-cycle specification:** shorter artifact and dialogue; existing applicable brainstorm, review and approval obligations remain.
- **Standalone `cdad-spec-and-test`:** proportionate outcome, boundaries, verification and recoverable decisions; no automatic accreditation of normal-cycle gates it did not execute.

Neither path may invent consent, conceal uncertainty or label an unreviewed artifact independently reviewed. Lightweight instructions must name their applicable approval and verification steps rather than imply exemptions from another workflow.

Technical consultation is triggered by a consequential uncertainty or missing evidence, not by every question.

### D5 — Preserve brainstorm consultation explicitly

Retain architect `brainstorm` as a targeted technical-challenge and alternatives path, mediated through the orchestrator.

Feature 019-002 must reconcile its delivery contract so a consultation can return a single `role-report` through supported prepared dispatch. It must update the protecting regression expectations deliberately.

Until that implementation exists, instructions must not represent this delivery as already supported, disguise consultation as a draft, or silently switch substages.

**Criterion:** preserving the named path avoids an unnecessary replacement workflow, while explicitly addressing the verified delivery incompatibility.

## Contract

### Signature

This is a documentary transformation, not a new API:

> Approved unit contract + evidenced discovery + attributed decisions → operating design, worked examples and bounded activation/acceptance requirements.

### Promise A — The owner knows who acts

**PC-1.** The product assigns functional questioning, technical investigation, recording, challenge, drafting, readiness checking, independent review and approval to named existing roles or authorities. It explains the mediated round trip without attributing fictitious direct interaction.

**PC-2.** The product states the precise role-boundary changes required for activation and preserves prohibitions on technical substitution, implementation, test-writing and independent review by the orchestrator.

### Promise B — Answers retain their meaning across handoffs

**PC-3.** The handoff contract preserves confirmed answers, unaccepted proposals, consequential unknowns, technical evidence and corrections as distinguishable information. A correction identifies the earlier understanding it replaces without presenting both as current agreement.

**PC-4.** A fresh-session worked example recovers the current decision, its authority, a superseded statement and a remaining question from authorized durable inputs alone. The example does not rely on inaccessible conversation history.

### Promise C — Work does not advance on invented agreement

**PC-5.** Readiness instructions distinguish a partial answer, silence, a proposed default, an unresolved behavioral choice and an unverified technical assumption. Each leads to the appropriate clarification, investigation, explicit exclusion or blocked-readiness outcome.

**PC-6.** The route from completed dialogue to drafting, independent draft review and explicit approval is unambiguous. Answering a question, accepting a summary or receiving a review verdict does not approve the specification.

### Promise D — Small tasks remain proportionate

**PC-7.** The product identifies the supported lightweight surfaces and their applicable obligations. It shares decision-fidelity rules without requiring the full normal-cycle artifact set, a fixed questionnaire, per-question delegation or a scenario quota.

### Promise E — Activation has an actionable, bounded contract

**PC-8.** The design maps each affected rule to its canonical owner and effective consumers, including generic/domain role variants, prepared packets, legacy handoffs and lightweight guidance. It identifies incompatible current instructions and their intended reconciliation rather than treating a new explanatory document as activation.

**PC-9.** The activation handoff includes:
- The architect-brainstorm delivery incompatibility.
- The draft re-entry route that currently bypasses independent review.
- Frozen-packet behavior and the need for new publications where instructions change.
- Idle closure and status/opening eligibility consistency.

It assigns these executable corrections and focused regression evidence to 019-002, without repairing current workspace state as part of this documentary product.

### Promise F — Acceptance distinguishes examples from observed success

**PC-10.** Worked examples show the intended response and an unacceptable alternative for every distinct committed fidelity behavior. Examples are labelled illustrative, not transcripts or proof of agent compliance.

**PC-11.** The acceptance protocol for 019-002 requires real agent use from need through dialogue, targeted architect input, recorded decisions, draft and independent draft review. It identifies protected scenario inputs, effective instruction versions, recoverable transcripts/artifacts, comparison criteria and reporting of failures or limitations.

The protocol must additionally require observed evidence for every epic case below:

- **Partial response:** the answered portion is preserved without inventing answers to the remaining consequential questions.
- **Unaccepted default:** the proposed default remains distinguishable from a confirmed decision; silence or an answer to another question does not accept it.
- **Corrected decision:** the correction replaces the superseded understanding in the current decision context and resulting handoff or draft, while retaining recoverable provenance.
- **Unresolved behavioral choice:** the consequential choice remains visible and prevents premature readiness until explicitly resolved or excluded by the authorized decision-maker.
- **Technical uncertainty:** an unverified assumption remains visible and is routed to targeted investigation. Its subsequent treatment reflects recovered evidence or an explicit limitation or blocker, not an assertion of fact without backing.

For each case, the acceptance record must identify the protected input that exercised it, the relevant actual agent response, the resulting decision record, handoff, readiness outcome or draft treatment, and the observed result against the criterion above. Citations must identify recoverable transcript turns or artifact sections and their examined versions. A response or artifact that cannot be recovered cannot establish observed coverage.

A single execution may cover several cases; additional observed executions may supply missing coverage. There is no fixed scenario count or quota of equivalent variants. The complete real-agent journey and the observed coverage of all five cases are both required.

Failures, missing coverage and limitations remain explicit. Reporting a limitation does not convert an unobserved or failed case into a successful result, and illustrative examples or structural checks cannot substitute for the required observations. A correctly observed blocked-readiness outcome can demonstrate the applicable case; the overall end-to-end obligation still requires its own evidence.

**PC-12.** Verification of 019-001 is independent semantic review against the approved contract. The reviewer uses a protected checklist derived from PC-1 through PC-12 and the admitted sources, fixed before any product is produced and never edited by the producer. Closure evidence identifies the checklist version used and records, for every PC, the verification result, cited evidence with recoverable locators and examined versions, and any findings, missing evidence, limitations or abstentions. Missing evidence or a failed postcondition cannot establish acceptance.

## Representative user-observable examples

These examples are illustrative acceptance inputs, not observations.

### Partial answer and unaccepted default

**Owner:** “CSV, dates in UTC.”

**Acceptable orchestrator response:** “CSV and UTC are confirmed. The columns remain undecided. I suggest ID, date and total; do you want those?”

**Unacceptable:** recording the suggested columns as agreed because the owner answered the format question.

### Correction

**Owner:** “Correction: include cancelled records, but identify their status.”

**Acceptable:** update the current decision, preserve the earlier exclusion as superseded, and pass the corrected requirement into drafting.

**Unacceptable:** retain the exclusion in the architect’s handoff or describe inclusion and exclusion as simultaneous requirements.

### Unresolved behavior

**Owner:** “I have not decided whether invalid rows should stop the export.”

**Acceptable:** keep the error policy pending and ask about the trade-off before declaring readiness.

**Unacceptable:** select a conventional default and announce the brainstorm complete.

### Technical uncertainty

**Owner:** “Use the existing export hook.”

**Acceptable:** record the preference, ask the architect to verify the hook and return evidence or `VERIFY`. Route any consequential absence back to the owner.

**Unacceptable:** invent a hook or claim availability from the owner’s preference alone.

### Existing versus genuinely new behavior

For an existing export, identify the examined behavior, intended change and preservation boundary with sources. For a genuinely new export, say no existing baseline was established.

**Unacceptable:** invent prior behavior or promise compatibility on unexamined surfaces.

### Lightweight work

For a bounded wording correction, record the requested replacement, its scope and verification in the authorized small-task artifact.

**Unacceptable:** require unrelated domain research or claim that a short checklist proves completion of normal-cycle gates.

## Verifiable invariants

- A proposal or unanswered question never becomes a confirmed decision without recoverable authority.
- Corrections do not silently erase provenance.
- A readiness assessment, draft, review verdict and approval remain distinguishable.
- The architect does not write the product or approve its proposal.
- Test-writing and independent review retain their existing separation.
- No new role, state, gate, communication service or packet field is required by this design.
- Feature 019-001 does not activate instructions or correct executable state behavior.

## Acceptance criteria

Before accepting 019-001:

1. Every PC has an evidence locator and a verification result.
2. The independent reviewer contrasts the product with its admitted sources and examines the examples’ meaning—not merely their labels.
3. The reviewer can determine who acts, what each handoff preserves and what blocks readiness without inventing missing rules.
4. No unresolved contradiction prevents the design from being an unambiguous operating proposal.
5. The activation handoff preserves all epic obligations assigned to 019-002, including the real-agent end-to-end journey, observed evidence for each of the five PC-11 cases with recoverable locators and outcomes or limitations, and idle/status correction. The reviewer checks that the protocol requires both the complete journey and case coverage, permits executions to cover several cases without scenario quotas, and does not admit illustrative examples, structural checks or declared limitations as substitutes for missing or failed observations.
6. The authorized approver explicitly accepts the reviewed design. Delegated approval identifies its authority; this architect report supplies none.

For this purely documentary unit, independent semantic review IS the verification; no automated test, structural-interface verifier, RED/GREEN phase or test-writer participation is required. Before any product is produced, the independent reviewer derives the checklist from this approved contract’s PC-1 through PC-12 and its admitted sources, not from the produced design. The orchestrator materializes it as a protected acceptance input outside the product directory; the producer never edits it. The reviewer applies that fixed checklist and returns a per-PC result with cited product and source evidence, examined versions, findings and verification limits. Acceptance requires evidence satisfying every committed postcondition, no blocking contradiction or missing evidence, and explicit approval by the authorized approver. This verification establishes documentary fidelity, consistency and an actionable activation contract, not deployment or observed agent compliance. PC-11 and all acceptance obligations assigned to 019-002 remain unchanged.

## Technical context and activation ownership

The product must reconcile these evidenced surfaces:

- Role ownership: `sources/roles/{architect,orchestrator}.md`.
- Normal dialogue and sequencing: `skills/cdad-cycle/references/stage-1-discovery.md`, `stage-2-specification.md`, `handoff-prompts.md` and `re-entry.md`.
- Effective packet instructions and delivery: `skills/cdad-cycle/packets/` and the relevant result/dispatch adapters.
- Generated consumers: generator metadata, generic and Odoo agents for supported runtimes.
- Lightweight applicability: the smaller skill, trivial Stage 2 variant and methodology.
- Resting-state guidance and orientation: closure references, epic handoff and packet CLI status/opening behavior.

Canonical role sources own permissions; workflow references own sequencing; executable contracts own delivery and state behavior. Consumers must point to or operationalize those owners without creating conflicting definitions.

Historical frozen packets are not silently rewritten.

## Pending decisions and verification

- **D1–D5 acceptance:** proposed here; the authorized approver must accept or amend them. This blocks construction authorization, not circulation of the draft.
- **Semantic review and protected verification inputs:** not yet produced. Required before the respective acceptance claims.
- **Runtime execution and distribution:** not established by repository mapping. Required evidence belongs to 019-002.
- **Lightweight compatibility:** discovery identifies divergent descriptions. The operating design must resolve their applicability explicitly; it cannot preserve contradictory operative instructions under a “pending” label.

## deferred-hardening

- Exhaustive cross-runtime behavior certification: beyond the bounded observed exercise; additional runtimes require their own evidence.
- Statistical latency or context-cost benchmarks: no performance threshold is promised.
- Runtime prevention of every out-of-scope read or transient write: no sandbox mechanism is being introduced.
- Unrelated instruction cleanup and broader workflow redesign: excluded to preserve the approved boundary.

The observed exercise and executable corrections assigned to 019-002 are separate delivery obligations, not deferred hardening.

## Out of scope

OpenSpec installation; new UI or communication service; automatic approval; weakening test/review separation; global deployment; unrelated documentation cleanup; executable correction in 019-001.

**Status: Approved (amended 2026-11-15, owner decision) by the CDAD orchestrator under <owner>'s delegated HITL.**
