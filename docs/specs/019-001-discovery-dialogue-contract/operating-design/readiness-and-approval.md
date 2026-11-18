# Readiness, draft review and approval (PC-5, PC-6)

Locators are at revision `64aa4670`. Status: proposal.

## 1. Signals and their routes (PC-5)

Each signal below must be treated as what it is. None of them is agreement by default.

| Signal | What it is | Not allowed | Route |
|---|---|---|---|
| **Partial answer** | The owner answered some consequential questions. | Inferring the answers to the others. | Record the answered part as confirmed (with authority). Ask the remaining questions, one batch at a time. |
| **Silence** | No answer to a question. | Reading silence as acceptance, of a proposal or of a summary. | Keep the item open. Ask again, or record it as unresolved. |
| **Proposed default** | An alternative offered by the orchestrator or architect. | Recording it as confirmed because the owner answered a different question. | Ask the owner to accept, amend or decline it. Declined → unresolved item. |
| **Unresolved behavioural choice** | A choice that changes the promised result, with no answer and no explicit exclusion. | Choosing a conventional default and calling the brainstorm complete. | Keep it visible. Ask the owner, or the authorized decision-maker. It may be resolved, or explicitly excluded from scope by the owner. |
| **Unverified technical assumption** | A claim about existing behaviour or feasibility that no evidence supports yet. | Asserting it as fact, or deriving it from the owner's preference (for example, "use the existing export hook"). | Route to a targeted architect investigation. The result is verified evidence, a bounded limitation stated explicitly, or a blocker if the item is consequential and absent. A detail may stay `VERIFY` only if an unambiguous, verifiable commitment remains possible. |

## 2. Readiness for drafting (D3)

The orchestrator checks all five conditions at brainstorm re-entry. Readiness is
recorded as an event of its own.

- **R1.** Every consequential behavioural choice has an explicit answer, or an explicit scope exclusion by the owner. No open conflict between entries (`handoff-fidelity.md` §1) stands on a fragment the draft would use: an open conflict blocks readiness for that fragment exactly as an unresolved item does.
- **R2.** The recorded summary does not extend the owner's answers. Where it introduces an interpretation, omits a qualification or conflicts with another instruction, the orchestrator asks again. An explicit answer does not need a redundant confirmation ritual.
- **R3.** Every correction whose authority is recorded is reflected in the current decisions (`handoff-fidelity.md` §1); the entries it supersedes are not used (`handoff-fidelity.md` §5). A correction without recorded authority does not count, and the entry it names stays current.
- **R4.** Relevant technical uncertainty has been investigated, bounded, or identified as blocking.
- **R5.** The drafting inputs are recoverable by a fresh architect session from the Dialogue context section of `discovery.md`, which exists before drafting (`handoff-fidelity.md` §2 and §6, including §6.1).

Readiness is not inferred from the length of the conversation, from the owner
being tired or from a summary being accepted. Readiness for drafting, agreement with
a summary, independent review and specification approval are four different
events (§3).

## 3. The route from dialogue to approval (PC-6)

The events happen in this order. Each one has its own record and its own authority.

| # | Event | Who | Authority it carries | Source |
|---|---|---|---|---|
| E1 | Owner answers | Owner | Answer only | Dialogue context (`handoff-fidelity.md`) |
| E2 | Readiness recorded (R1–R5 hold) | Orchestrator | Readiness only | `re-entry.md:230-238` |
| E3 | Spec draft returned as final text | Architect | Draft only; the architect never approves it | `stage-2-specification.md:31-45`; `sources/roles/architect.md:105` |
| E4 | Independent draft review dispatched | Orchestrator, to a reviewer in a separate session | None | `stage-2-specification.md:52-55` |
| E5 | Review verdict materialised as `plan-review.md`; blockers routed back; focused re-review if the design changed | Reviewer; orchestrator routes | A verdict. A verdict approves nothing | `stage-2-specification.md:56-64`; `re-entry.md:266-278` |
| E6 | Explicit approval | The authorized approver: the owner, or a higher-hierarchy autonomous owner. The orchestrator only under the sole delegation exception of `roles-and-dialogue.md` §1, cited in the record and within its limits | Approval; this is the only event that pins the contract | `stage-2-specification.md:14` and §2.3 (`:76-110`); `re-entry.md:255-263` |
| E7 | Stage 3 begins | Orchestrator | Follows E6 only | `re-entry.md:255-264` |

### The route that must change

The architect draft re-entry says: "If it passes: pass the spec to the user for
approval" (`skills/cdad-cycle/references/re-entry.md:251-253`, in
`Architect — spec draft`, `:240-264`). That skips E4 and E5, although the stage-2
sequence and the reviewer re-entry require them (`stage-2-specification.md:47-75`;
`re-entry.md:266-278`).

**Proposed route, in two forms.** *Reviewed route:* when the draft passes its
structural check, the orchestrator dispatches the draft review (E4). Only after every
blocker is closed (E5) does the draft go to the approver (E6). *Exempted route:* the
only other form is the owner's explicit, registered exemption of the review
(`stage-2-specification.md:71-74`). Under it, E4 and E5 are not run, and the draft goes
to the approver (E6) with the exemption recorded in the same `stage_history` entry as the
approval. Without that registered exemption, the reviewed route applies in every case.
An exemption is neither an approval nor a review verdict. The reconciliation belongs to
`activation-map.md` (rule R4) and to 019-002.

### What does not count as approval

- Answering a question (E1).
- Accepting a summary (part of E2 at most).
- Receiving a review verdict (E5).
- A review exemption: it waives E4 and E5 under its registered terms; it is neither an approval nor a verdict.
- Passing the draft to an approver.
- An approval that names no authority. An orchestrator's approval counts only when the record cites the explicit delegation of `roles-and-dialogue.md` §1 and the approval falls within its limits. For epic 019 that delegation is `docs/epics/epic-019-discovery-dialogue/execution.md:8-14`.

### Review exemption

The owner may exempt the draft review. The exemption must be explicit and be
registered in the same `stage_history` entry as the approval, with four fields:
`exempted_by`, `delegated`, `requested_by` and `reason` (`stage-2-specification.md:71-74`).
Without a declared exemption, E4 and E5 are mandatory.

## 4. Why the events stay separate

If the approver were asked to accept "the summary and the design" at once, the
approver could not tell whether the summary extended a decision, whether a
blocker was closed, or whether the design was reviewed. The separation keeps each
of those facts recoverable.
