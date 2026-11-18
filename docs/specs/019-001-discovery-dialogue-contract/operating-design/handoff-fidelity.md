# Handoff fidelity (PC-3, PC-4)

Locators are at revision `64aa4670`. Status: proposal.

## 1. Six classes of entry

Every entry in the dialogue context belongs to exactly one class. The class is
written in the entry (§3). A reader must be able to tell the classes apart
without the conversation.

| Class | What it is | What it may do | What it may not do |
|---|---|---|---|
| **Confirmed decision** | An owner's answer, with its authority: the owner's message identifier in the authorized transcript, its date and the fragment at stake. | Govern drafting and readiness. | Be inferred from silence, from an answer to another question, or from the orchestrator's summary. |
| **Proposal** | An alternative offered by the orchestrator or the architect, not yet accepted. | Be presented to the owner for acceptance, amendment or decline. | Be recorded as a decision. A proposal becomes a decision only when a confirmed-decision entry cites the owner's acceptance. |
| **Unresolved item** | A consequential question with no answer and no explicit exclusion. | Block readiness when it changes the promised result. Name the decision-maker when known. | Be settled by a default, or be silently dropped. |
| **Conflicting statements** | Two entries, or an entry and an orchestrator summary, that disagree on the same fragment, with neither superseding the other. | Block drafting of that fragment until a correction or the owner's answer resolves it. Name each conflicting entry. | Be resolved by choosing the newer entry, the more specific one or the orchestrator's reading. |
| **Technical evidence** | An architect finding, with the architect as author, the examined revision and a status: *verified*, *VERIFY* (unverified), or *contradicted*. | Inform the decision and the draft. | Count as an owner decision. A *VERIFY* item stays visible. |
| **Correction** | A new entry, with its own authority, that replaces an identified earlier entry. | Become a current decision for its fragment once its authority is recorded, and supersede the entry it names. | Erase the replaced entry, or appear as current agreement together with it. A correction without recorded authority supersedes nothing. |

**Current decision.** This is a status that follows from the classes, not a seventh class. An entry is a *current decision* when it is a confirmed decision, or a correction whose authority is recorded, and no later entry supersedes it. Only current decisions govern drafting and readiness. A correction without recorded authority does not supersede anything: the entry it names stays current, and the orchestrator asks the owner again (`readiness-and-approval.md` §2, rule R3).

The orchestrator's own summary is not a class. Its statements are proposals until
the owner accepts them. When the summary introduces an interpretation, omits a
qualification or conflicts with another instruction, the orchestrator asks again
(`readiness-and-approval.md` §2, rule R2).

## 2. Where the context lives

- **Normal cycle:** a section titled **Dialogue context** inside the feature's per-feature discovery artifact, `docs/specs/<feature>/discovery.md` (discovery `discovery.md` §5.1 names this choice as open; this design resolves it in favour of reuse). That artifact already exists in the cycle: the architect's per-feature report is returned to the orchestrator and materialized there (precedent: commit `c1016fb5`, "docs(epic): materialize architect discovery report"). So the file is available before drafting. If the first owner answer is recorded before the report arrives, the orchestrator creates the file containing the Dialogue context section alone, and the report is materialized later, unaltered, in its own section.
  - The architect's report keeps its own section and authorship, and the orchestrator materializes it there unaltered. Owner answers and orchestrator notes are written only in the Dialogue context section, as attributed entries.
  - The orchestrator's authorship and location of the dialogue record and of the architect's report are limited to this file: it materializes the report unaltered in its own section, and writes owner answers, corrections and notes, attributed, only in the Dialogue context section. That limit covers only the dialogue record and the report. Every other write or materialization the cycle already authorizes stays allowed (`roles-and-dialogue.md` §3, item 2). The orchestrator never authors or alters the spec's content. The architect never writes the file (`roles-and-dialogue.md` §3).
  - The draft's "Technical context" section is written later, in Stage 2, as a copy of the report. It is not where dialogue is recorded. The Stage-1 reference that says otherwise (`skills/cdad-cycle/references/stage-1-discovery.md:63`) is reconciled in `activation-map.md` R5.
- **Standalone lightweight work:** a section inside the authorized minimal spec or task artifact (`lightweight-paths.md` §2). No separate dialogue file is required (D2).
- **`current_decisions` is not the dialogue record.** It transports governing project decisions, each marked `vigente` or `obsoleto` (`skills/cdad-cycle/scripts/cdad_packet.py:94-111`, `:1540-1560`). Proposals, unanswered questions and feature-level answers are not rows in it. The Memory Bank template states the same exclusion (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:5-34`).

## 3. Entry format

This is a documentary convention, not a schema. It adds no packet field and no state field.

```markdown
### DC-03 — Exclude cancelled records

- Class: confirmed decision
- Statement: <one line, in the owner's terms>
- Author: orchestrator (recording) · owner (answer)
- Authority: owner message <identifier>, <date>, fragment "<quoted words>"
- Supersedes: DC-01 | none
- Superseded by: DC-06 | none
- Next action: <role> — <action>
```

Technical evidence entries name the architect report section and the examined
revision in `Authority`. Their `Author` is always the architect.

## 4. Handoff rules by recipient

- **To the architect (consultation or draft).** Include the current decisions (§1), unresolved items, open conflicts and technical items. Each open conflict is named with both entries and marked as blocking for its fragment. Include each correction as *the current entry* plus one line naming the replaced entry as superseded. Proposals are labelled as proposals. Do not send superseded understanding as if it were a requirement.
- **To the reviewer (draft review).** Include the whole dialogue context with its authorship and the superseded entries marked as superseded. The reviewer checks the draft against the current decisions (§1), not against the conversation.
- **To the owner (questions).** Include only the question, the options or proposal being asked about, and the reference that justifies it. Do not ask about several decisions at once.

## 5. Correction procedure

1. The owner states a correction in their own words.
2. The orchestrator records a new Correction entry with its authority, and marks the replaced entry *superseded by* the new entry. The replaced entry stays in the record.
3. The current understanding is updated. Only current decisions (§1) feed drafting. Superseded entries do not, and neither does a correction whose authority is not recorded.
4. Any architect output or draft that relied on the replaced entry is flagged for re-check at re-entry (`re-entry.md` drafting route).

## 6. Worked example — fresh-session recovery (PC-4)

*Illustrative. This example shows what a fresh session must recover. It is not a transcript and not evidence that an agent performed it.*

**Durable input.** Only the file `docs/specs/<feature>/discovery.md`, section **Dialogue context**, is supplied to the fresh session. The chat history is not available.

```markdown
### DC-01 — Export format
- Class: confirmed decision · Authority: owner message M-12, fragment "CSV, dates in UTC"

### DC-02 — Export columns
- Class: proposal · Statement: ID, date, total · Authority: none (not accepted)

### DC-03 — Cancelled records
- Class: confirmed decision · Authority: owner message M-15, fragment "exclude cancelled records"
- Supersedes: none · Superseded by: DC-06

### DC-04 — Invalid rows
- Class: unresolved item · Statement: whether invalid rows stop the export · Next action: orchestrator asks the owner

### DC-06 — Cancelled records (correction)
- Class: correction · Statement: include cancelled records, identified by status
- Authority: owner message M-21, fragment "include cancelled records, but identify their status"
- Supersedes: DC-03
```

**What the fresh session must answer, and where each answer is found:**

| Question | Answer | Locator in the durable input |
|---|---|---|
| The current decision | Cancelled records are included and identified by status | `DC-06`: a correction whose authority is recorded, so it is a current decision (§1) |
| Its authority | Owner message M-21 | `DC-06`, `Authority` |
| The superseded statement | The exclusion of cancelled records, which must not be used | `DC-03`, `Superseded by: DC-06` |
| A remaining question | Whether invalid rows stop the export; the owner must decide before readiness | `DC-04` |

The fresh session must also not use `DC-02`, which is a proposal, as a column
decision. Failure would be: answering from "what was discussed" without these
entries, or treating `DC-02` as agreed.

### 6.1 Handoff to the fresh architect session, before any technical report exists (illustrative)

*Illustrative. This shows the handoff content for the pre-draft path in which the architect has not yet reported. It is not a transcript and not evidence that an agent performed it.*

The orchestrator sends a targeted consultation (`roles-and-dialogue.md` §2, step 3). The attached durable input is the `discovery.md` file of §6, with only its Dialogue context section, which the orchestrator created at the first owner answer.

```markdown
Targeted consultation — architect (fresh session)
Durable input: docs/specs/<feature>/discovery.md, section "Dialogue context" only.
Current decisions: DC-01 (owner message M-12); DC-06 (owner message M-21, supersedes DC-03).
Not current, do not use: DC-03 (superseded by DC-06); DC-02 (proposal, not accepted).
Open for the owner, not for you to decide: DC-04 (orchestrator asks the owner).
Task: examine the existing export behaviour that DC-01 and DC-06 affect. Return findings as
technical evidence: examined revision, status (verified / VERIFY / contradicted), and what is
still uncertain. Do not answer DC-04.
```

The fresh session recovers from this input alone: the two current decisions and their authority,
the superseded statement it must not use, the proposal it must not treat as agreed, and the open
question it must leave to the owner. Its report returns to the orchestrator, which materializes it unaltered
in its own section of the same file.

## 7. Anti-patterns this section rules out

- Recording an accepted-looking proposal without the owner's authority.
- Resolving a conflict between two entries by recency, by specificity or by the orchestrator's reading, instead of naming it and asking (B-24).
- Replacing an entry instead of adding a correction (provenance lost).
- Writing the superseded and the corrected statements in the same handoff as two current requirements.
- Using `current_decisions` to hold proposals or open questions.
