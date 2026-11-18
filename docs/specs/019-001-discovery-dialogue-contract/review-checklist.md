# Protected independent-review checklist — 019-001

**Purpose:** Apply this checklist to the future `operating-design/` product. It is derived from the approved amended specification and admitted discovery, not from a produced design. It is not a review or approval of a product.

**Reference versions:** specification SHA-256 `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853`; discovery SHA-256 as recorded in the specification: `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43`. Discovery identifies its examined repository revision as `265174993b4213be9a96545578016657bc8b09ba`. Later source claims must identify the revision actually examined.

## How to apply

For **each PC**, record: result; product and source locators precise enough to recover the evidence; examined versions; findings; and any missing evidence, limitation or abstention. Contrast substance and examples against the contract and admitted sources, not just headings or labels. A missing or failed postcondition cannot establish acceptance.

### PC-1 — Named responsibilities and mediated dialogue

- **Must be true:** The design assigns functional questions, technical investigation, recording, challenge, drafting, readiness, independent review and approval to named existing roles or authorities. It explains architect findings → orchestrator question → owner answer → attributed return to the architect when needed, without inventing direct contact.
- **Evidence:** Product sections identifying each actor and the round trip; contrast with spec D1 and discovery §§2–3.B.
- **Failure:** An unassigned action, fictitious interaction, or handoff that leaves the reader unable to tell who acts.

### PC-2 — Boundaries required for activation

- **Must be true:** The design states the precise role-boundary changes needed to move functional dialogue to the orchestrator while retaining architect technical investigation, challenge and drafting. The orchestrator must not substitute for that work, implement, write tests or independently review.
- **Evidence:** Product boundary and activation mapping; spec D1 and PC-2; discovery §3.A.
- **Failure:** An explanatory document is treated as current authorization, or the proposed boundary permits technical substitution or erases the existing separations.

### PC-3 — Meaning preserved in handoffs

- **Must be true:** Confirmed answers and their authority, unaccepted proposals, consequential unknowns, technical evidence and corrections remain distinguishable. A correction identifies the superseded understanding; both are not represented as current agreement. The next action and responsible actor are recoverable.
- **Evidence:** Handoff/recording rules and correction treatment in the product; spec D2 and PC-3; discovery §3.E.
- **Failure:** A proposal or silence becomes agreement, a correction loses provenance, or the recipient cannot distinguish current from superseded information.

### PC-4 — Fresh-session recovery

- **Must be true:** A worked example lets a fresh session recover the current decision, its authority, the superseded statement and a remaining question from authorized durable inputs alone.
- **Evidence:** The example and the exact durable artifacts or sections it supplies to the fresh session; spec PC-4 and D2.
- **Failure:** Any of the four items requires inaccessible conversation history or is absent or ambiguous.

### PC-5 — Readiness without invented agreement

- **Must be true:** Instructions distinguish partial answers, silence, proposed defaults, unresolved consequential behavior and unverified technical assumptions. Each routes to appropriate clarification, investigation, authorized exclusion or blocked readiness. A technical detail remains `VERIFY` only if an unambiguous, verifiable commitment is still possible.
- **Evidence:** Readiness rules and corresponding examples; spec D3 and PC-5; discovery §§3.B, 3.E.
- **Failure:** Readiness is inferred from conversation length, silence accepts a default, an unresolved consequential choice is silently settled, or an unsupported technical assumption is asserted as fact.

### PC-6 — Draft, review and approval are separate

- **Must be true:** The route from completed dialogue through drafting, independent draft review and explicit authorized approval is unambiguous. Answering a question, accepting a summary or receiving a review verdict does not approve a spec.
- **Evidence:** Sequencing and re-entry instructions in the product; spec D3, PC-6 and acceptance criterion 6; discovery §3.D.
- **Failure:** A route permits approval before independent review, conflates readiness or review with approval, or omits the authorized approver.

### PC-7 — Proportionate lightweight paths

- **Must be true:** The design distinguishes the trivial normal-cycle spec from standalone `cdad-spec-and-test`, states each path’s applicable obligations, and applies shared fidelity rules proportionately. It does not require the full normal-cycle artifact set, a fixed questionnaire, delegation for every question or a scenario quota.
- **Evidence:** Lightweight applicability rules and examples; spec D4 and PC-7; discovery §2, lightweight paths.
- **Failure:** The paths are silently equated, one claims gates it did not execute, applicable normal-cycle obligations disappear, or unrelated ceremony is imposed.

### PC-8 — Canonical owners and effective consumers

- **Must be true:** Each affected rule is mapped to its canonical owner and effective consumers, including generic and domain role variants, prepared packets, legacy handoffs and lightweight guidance. Incompatible current instructions and intended reconciliation are identified; explanatory text alone is not activation.
- **Evidence:** Product mapping with recoverable source and consumer locators; spec PC-8 and technical context; discovery §§3.A–E and 4.
- **Failure:** A governing owner or required consumer chain is missing, an identified contradiction remains operative, or changing a non-authoritative explanation is claimed to activate the design.

### PC-9 — Bounded activation handoff

- **Must be true:** The handoff assigns to 019-002 executable correction and focused regression evidence for: brainstorm single-delivery incompatibility; draft re-entry bypass of independent review; frozen packets and new publications; and idle closure/status/opening eligibility consistency. It does not repair workspace state as part of 019-001.
- **Evidence:** Explicit 019-002 handoff and affected surfaces; spec D5 and PC-9; discovery §§3.C–D, 3.F and 4.
- **Failure:** Any item or its regression obligation is omitted, brainstorm is disguised as drafting or silently switched, frozen packets are said to update automatically, or documentary work is represented as an executable repair.

### PC-10 — Meaningful illustrative examples

- **Must be true:** Worked examples show intended and unacceptable responses for **every distinct committed fidelity behavior**. They are labelled illustrative, not transcripts or evidence of compliance.
- **Evidence:** An explicit reviewer mapping from each committed behavior to both example outcomes and their locations; spec PC-10 and representative examples.
- **Failure:** A behavior lacks either outcome, an example contradicts the rule it purports to demonstrate, or illustrative material is presented as observed agent success.

### PC-11 — Observed 019-002 acceptance protocol

- **Must be true:** The protocol requires a real-agent journey from need through dialogue, targeted architect input, recorded decisions, draft and independent draft review. It identifies protected scenario inputs, effective instruction versions, recoverable transcripts/artifacts, comparison criteria, failures and limitations.
- **Case coverage:** Require observed evidence for all five: partial response; unaccepted default; corrected decision and provenance; unresolved behavioral choice blocking readiness until resolved or authorizedly excluded; and technical uncertainty routed to investigation and treated according to evidence or an explicit limitation/blocker.
- **Evidence:** For each case, the protocol requires a protected-input locator, actual response, resulting record/handoff/readiness or draft treatment, observed result, and recoverable transcript-turn or artifact-section locators with examined versions. One execution may cover several cases; additional executions may fill gaps, without a scenario quota.
- **Failure:** Either the complete journey or any case is missing; unrecoverable material is counted as coverage; or examples, structural checks, reported limitations or failed observations are accepted as success. A correctly observed blocked-readiness outcome can prove its case, not by itself the complete journey.
- **Sources:** Spec PC-11 and acceptance criterion 5; discovery §6.

### PC-12 — Independent semantic verification

- **Must be true:** The product’s verification/closure handoff preserves independent semantic review against the approved contract, using this protected, contract-derived checklist fixed before production and not edited by the producer. It requires a per-PC result, recoverable evidence and examined versions, findings, missing evidence, limitations and abstentions; failed or missing evidence cannot establish acceptance.
- **Evidence:** Product verification and closure instructions; protected checklist identity/version and its materialization record outside the product; eventual independent review report; spec documentary-product scope, PC-12 and acceptance criteria.
- **Failure:** Producer-controlled checklist, checklist derived from the finished design, structural matching substituted for semantic review, missing per-PC evidence, or acceptance despite an unmet postcondition.

## Cross-cutting checks

- **No new machinery:** The proposal requires no new role, state, gate, communication service or packet field. Documentary distinctions are not presented as schema additions; `current_decisions` is not overloaded with proposals or unanswered questions.
- **Durable context:** Normal-cycle dialogue context reuses the existing discovery artifact with attribution; standalone lightweight work uses its authorized minimal spec or task artifact. Technical authorship and later owner answers/orchestration notes remain distinguishable.
- **Source fidelity and contradictions:** Compare the product with the admitted sources and identify examined revisions. Resolve operative lightweight contradictions rather than merely marking them pending. Do not infer universal runtime capabilities from an instruction gap.
- **Activation boundary:** 019-001 is documentary; current powers and behavior remain effective until separately approved activation. Preserve 019-002’s PC-11 obligations and idle/status correction; do not claim deployment or observed compliance.
- **Acceptance:** No unresolved contradiction may prevent an unambiguous operating proposal. The authorized approver must explicitly accept the reviewed design, with delegated authority identified where applicable. Review is not approval.

## Checklist limits

This checklist provides criteria for a later independent review; it does not establish that a product exists or satisfies them. Documentary semantic review establishes fidelity, consistency and an actionable activation contract—not deployment, universal runtime compatibility or observed compliance. The real-agent exercise belongs to 019-002. For this documentary unit, the approved spec makes independent semantic review the verification; it does not require an automated test, RED/GREEN phase or test-writer participation.

## Abstentions

- No product, examples, closure evidence or 019-002 execution was reviewed; none was presented as existing.
- The discovery hash above is recorded from the approved specification, not independently recomputed in this session.

**Execution evidence:** Validated the named request and complete packet using `python3 scripts/cdad_packet.py validate-request` and `validate-packet`, with the named request, packet and execution-context paths; both exited successfully without output. `render --route C` returned the identification supplied in the dispatch. Read only the declared spec and discovery inputs. Files modified: none. Commit: none.