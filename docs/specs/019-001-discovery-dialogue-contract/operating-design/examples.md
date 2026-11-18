# Illustrative examples (PC-10)

> **ILLUSTRATIVE.** Every example in this file is an invented scenario written to
> show what the intended rule means. None is a transcript, an observed agent
> response, or evidence that any agent complies. Observed behaviour belongs only to
> the protocol in `acceptance-protocol-019-002.md`.

Locators are at revision `64aa4670`.

Each committed fidelity behaviour below has an **intended** response and an
**unacceptable** response. The behaviours come from the design sections named in
each entry. The "Source" line points to the rule being illustrated; the reviewer
checks that the example matches its rule.

Owner messages, DC identifiers and dates are placeholders.

---

## B-01 — A partial answer is preserved; the remaining questions stay open

*Source: `handoff-fidelity.md` §1; `readiness-and-approval.md` §1 (partial answer).*

- **Owner:** "CSV, dates in UTC."
- **Intended:** "CSV and UTC are confirmed. The columns are still undecided. I suggest ID, date and total — do you want those?"
- **Unacceptable:** recording the suggested columns as agreed because the owner answered the format question.

## B-02 — An unaccepted default stays distinguishable from a decision

*Source: `handoff-fidelity.md` §1 (proposal); `readiness-and-approval.md` §1.*

- **Context:** the orchestrator proposed ID, date and total; the owner has said nothing about them.
- **Intended:** the entry is `proposal`, with "Authority: none (not accepted)", and the next question asks the owner to accept, amend or decline it.
- **Unacceptable:** the entry is `confirmed decision`, because the owner answered a different question.

## B-03 — Silence never accepts a proposal

*Source: `readiness-and-approval.md` §1 (silence); `docs/specs/019-001-discovery-dialogue-contract/spec.md` D3 ("silence never accepts a proposal").*

- **Context:** the owner answers the format question and does not reply to the column proposal.
- **Intended:** the proposal stays open; the orchestrator asks again, or records it as unresolved.
- **Unacceptable:** the orchestrator writes "owner agreed to the columns" because the owner did not object.

## B-04 — A correction replaces the superseded entry with its provenance

*Source: `handoff-fidelity.md` §5; spec representative example "Correction".*

- **Owner:** "Correction: include cancelled records, but identify their status."
- **Intended:** a correction entry DC-06 "Supersedes: DC-03" is recorded with its authority. DC-06 is therefore a current decision (`handoff-fidelity.md` §1). DC-03 is marked superseded and kept. The drafting input carries DC-06 only.
- **Unacceptable:** the architect's handoff keeps the exclusion, or describes inclusion and exclusion as simultaneous requirements.

## B-05 — An unresolved behavioural choice blocks readiness

*Source: `readiness-and-approval.md` §1–§2 (R1); spec representative example "Unresolved behaviour".*

- **Owner:** "I have not decided whether invalid rows should stop the export."
- **Intended:** DC-04 stays an unresolved item; the orchestrator asks about the trade-off; readiness is not recorded.
- **Unacceptable:** the orchestrator selects a conventional default and announces the brainstorm complete.

## B-06 — A technical uncertainty is routed to investigation

*Source: `readiness-and-approval.md` §1 (unverified technical assumption); spec representative example "Technical uncertainty".*

- **Owner:** "Use the existing export hook."
- **Intended:** the preference is recorded as the owner's preference; the orchestrator asks the architect to verify the hook; the architect returns verified evidence, or `VERIFY`, or a blocker. A consequential absence goes back to the owner.
- **Unacceptable:** the architect invents a hook, or the design claims the hook is available because the owner expects it.

## B-07 — An owner's preference is not evidence about the code

*Source: `readiness-and-approval.md` §1; spec representative example.*

- **Owner:** "It should work like the current report."
- **Intended:** the architect examines the current report's behaviour and records the examined version, or reports that no baseline was established.
- **Unacceptable:** the architect asserts the report's behaviour from memory or from the owner's sentence.

## B-08 — Existing and new behaviour are distinguished

*Source: spec representative example "Existing versus genuinely new behaviour".*

- **Intended (existing export):** the examined behaviour, the intended change and the preservation boundary are cited with the revision examined.
- **Intended (new export):** the design says that no existing baseline was established.
- **Unacceptable:** inventing prior behaviour, or promising compatibility on surfaces that were not examined.

## B-09 — A summary that extends an answer is not accepted; the orchestrator asks again

*Source: `handoff-fidelity.md` §1 (orchestrator's summary); `readiness-and-approval.md` §2 (R2).*

- **Owner's answer:** "Cancelled records are exported, but not the ones older than a year."
- **Orchestrator's summary:** "Cancelled records are exported."
- **Intended:** the orchestrator sees that the summary omits the qualification and asks again before recording the decision.
- **Unacceptable:** the summary is recorded as the owner's decision, with the qualification lost.

## B-10 — An explicit answer does not need a redundant ritual

*Source: `readiness-and-approval.md` §2 (the last paragraph).*

- **Owner:** "CSV, dates in UTC."
- **Intended:** the answer is recorded as confirmed in one step, without a second question that repeats it.
- **Unacceptable:** asking the owner to confirm the same answer again, with no new interpretation or qualification to check.

## B-11 — No fictitious architect–owner contact

*Source: `roles-and-dialogue.md` §2 (round trip); spec D1.*

- **Intended:** "The architect's finding is that the hook exists in version X (report §2). I will ask you whether that version is in scope."
- **Unacceptable:** "The architect confirmed with you directly that the hook is in scope." (No such conversation occurred.)

## B-12 — The technical question is not answered by the orchestrator

*Source: `roles-and-dialogue.md` §3 (orchestrator, must not change); `activation-map.md` R11.*

- **Owner's question to the orchestrator:** "Does the export hook fire before validation?"
- **Intended:** the orchestrator says the question is technical and dispatches a consultation to the architect.
- **Unacceptable:** the orchestrator answers from its own reading of the code, or "as far as I know".

## B-13 — Readiness, summary agreement, draft, review and approval stay distinct

*Source: `readiness-and-approval.md` §3–§4; spec invariant "A readiness assessment, draft, review verdict and approval remain distinguishable".*

- **Intended:** the record shows E2 "readiness recorded", E3 "draft returned", E4 "review dispatched", E5 "verdict", E6 "approval by the authorized approver", each with its own authority line.
- **Unacceptable:** a single line "spec agreed" that merges readiness, the summary and the approval.

## B-14 — A review verdict does not approve the spec

*Source: `readiness-and-approval.md` §3 (what does not count as approval); `stage-2-specification.md:56-58`.*

- **Intended:** the verdict is materialised; the blockers are routed to the architect; the spec waits for the explicit approval.
- **Unacceptable:** the orchestrator reads "no blocking findings" and moves to stage 3.

## B-15 — The architect does not approve its own proposal

*Source: spec invariant "The architect does not write the product or approve its proposal"; `sources/roles/architect.md:107-108`.*

- **Intended:** the architect's draft is returned as final text, marked unapproved; the approver is named as the next actor.
- **Unacceptable:** the draft is labelled "Approved" by the architect, or the architect says "this is approved".

## B-16 — The draft re-entry route includes the independent review

*Source: `readiness-and-approval.md` §3 (the route that must change); `re-entry.md:266-278`.*

- **Intended:** a passing draft is dispatched for the draft review, and then goes to the approver.
- **Unacceptable:** the draft goes directly to the approver, because the architect draft re-entry says so (the current text, `re-entry.md:251-253`).

## B-17 — Brainstorm consultation is not disguised as a draft

*Source: spec D5 ("disguise consultation as a draft" is forbidden); `activation-handoff-019-002.md` item 1.*

- **Intended:** the consultation returns findings and questions as a consultation report; the draft is produced later, in its own step.
- **Unacceptable:** the consultation's output is labelled "spec draft" so that it reaches the draft kinds.

## B-18 — Frozen packets are not claimed to update

*Source: `activation-handoff-019-002.md` item 3; `activation-map.md` R9.*

- **Intended:** "The live instruction changed. The published packet still carries the earlier bytes. A new publication is required to carry the change; the in-flight packet is recorded as not updated."
- **Unacceptable:** "The packet now reflects the change," with no new publication.

## B-19 — A lightweight path does not claim gates it did not execute

*Source: `lightweight-paths.md` §2 (surface B); spec D4.*

- **Intended:** the minimal task artifact says "not independently reviewed; not approved under the cycle", and lists the checks that were run.
- **Unacceptable:** "Reviewed and approved under the cycle," written in the standalone artifact by its author.

## B-20 — A lightweight path does not impose ceremony

*Source: `lightweight-paths.md` §3 (proportion); spec D4 and the lightweight example.*

- **Intended:** a bounded wording correction records the requested replacement, its scope and its verification in the authorized minimal artifact.
- **Unacceptable:** requiring unrelated domain research, a fixed questionnaire, or delegation of every question.

## B-21 — Consultation is triggered by consequential uncertainty, not by every question

*Source: `lightweight-paths.md` §3; spec D4 ("triggered by a consequential uncertainty or missing evidence, not by every question").*

- **Intended:** a question about the wording of an error message is answered by the owner; a question whether an existing hook can be reused triggers the architect.
- **Unacceptable:** every owner question is sent to a subagent, including a question about naming.

## B-22 — `current_decisions` carries only governing decisions

*Source: `handoff-fidelity.md` §2; `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:5-34`.*

- **Intended:** `current_decisions` holds a project decision marked `vigente` or `obsoleto`. The open question about invalid rows is in the dialogue context.
- **Unacceptable:** a row such as "invalid rows: undecided" added to `current_decisions`, with state `vigente`.

## B-23 — A fresh session recovers the decision from durable inputs alone

*Source: `handoff-fidelity.md` §6 (PC-4).*

- **Intended:** the fresh session answers the four questions (current decision, authority, superseded statement, remaining question) from the Dialogue context section only.
- **Unacceptable:** the fresh session can only answer by reference to a conversation it cannot access.

---

## B-24 — A conflict between two entries is named, not resolved by preference

*Source: `handoff-fidelity.md` §1 (conflicting statements); `handoff-fidelity.md` §7.*

- **Context:** DC-03 says "exclude cancelled records" (confirmed, M-15); DC-05 says "cancelled records appear in a separate tab" (confirmed, M-18). Neither supersedes the other.
- **Intended:** the orchestrator records the two entries as conflicting, names both, and asks the owner which statement governs (or whether a correction is meant). Drafting of that fragment waits.
- **Unacceptable:** the orchestrator picks the later message (DC-05) and drops DC-03 silently, or the architect drafts both behaviours as simultaneous requirements.

---

## B-25 — An authorized exclusion removes a choice from readiness; a silent exclusion does not

*Illustrative. Source: `readiness-and-approval.md` §1 (unresolved behavioural choice: "explicitly excluded from scope by the owner"); `handoff-fidelity.md` §1; spec D3.*

- **Owner:** "Invalid rows are out of scope for this export. We will not handle them."
- **Intended:** the orchestrator records DC-07 as a confirmed decision: a scope exclusion, with its authority (owner message identifier, date, quoted words). Readiness R1 is satisfied for that choice, and the draft lists invalid rows as out of scope.
- **Readiness effect under R1, both ways:** a written exclusion by the owner lets readiness be recorded for that choice. A dropped or silent question stays an unresolved item, and readiness is not recorded for that choice.
- **Unacceptable:** the question about invalid rows is dropped without the owner's words, because the owner "did not mention them", or the architect or orchestrator moves it out of scope on its own judgment. Silence and a dropped question are not an exclusion. A proposal to exclude is a proposal until the owner accepts it.

## B-26 — VERIFY is admissible only when a verifiable commitment remains possible

*Illustrative. Source: `readiness-and-approval.md` §1 (unverified technical assumption: "A detail may stay `VERIFY` only if an unambiguous, verifiable commitment remains possible"); spec D3.*

Two contrasted cases share one owner statement: "The export keeps the existing column order."

- **Intended (admissible):** the architect locates the current report's column order at the examined revision and verifies it. It cannot verify the name of the internal helper that builds the rows, so that detail stays `VERIFY`, and stays visible. The promised result does not depend on it: "the CSV header lists the columns in the order of the current report". That is an unambiguous commitment that an independent check can verify, so readiness may be recorded.
- **Unacceptable (not admissible):** the architect searches the report at every examined revision and locates no baseline for the column order. The baseline stays `VERIFY`, and the draft still promises "the export keeps the existing column order", which depends on that unverified baseline. No verifiable commitment exists. The item is a blocker: readiness is not recorded, and it goes back to the architect or the owner. The dependent promise is not written into the spec as `VERIFY`.

---

## Coverage index (producer index, not a review)

| Behaviour | Intended example | Unacceptable example |
|---|---|---|
| B-01 partial answer | B-01 | B-01 |
| B-02 unaccepted default | B-02 | B-02 |
| B-03 silence | B-03 | B-03 |
| B-04 correction | B-04 | B-04 |
| B-05 unresolved choice | B-05 | B-05 |
| B-06 technical uncertainty | B-06 | B-06 |
| B-07 owner preference is not evidence | B-07 | B-07 |
| B-08 existing vs new | B-08 | B-08 |
| B-09 summary extends answer | B-09 | B-09 |
| B-10 no redundant confirmation | B-10 | B-10 |
| B-11 no fictitious contact | B-11 | B-11 |
| B-12 no technical substitution | B-12 | B-12 |
| B-13 distinct events | B-13 | B-13 |
| B-14 verdict does not approve | B-14 | B-14 |
| B-15 architect does not approve | B-15 | B-15 |
| B-16 draft route includes review | B-16 | B-16 |
| B-17 brainstorm not a draft | B-17 | B-17 |
| B-18 frozen packets | B-18 | B-18 |
| B-19 lightweight claims | B-19 | B-19 |
| B-20 lightweight ceremony | B-20 | B-20 |
| B-21 consultation trigger | B-21 | B-21 |
| B-22 `current_decisions` scope | B-22 | B-22 |
| B-23 fresh-session recovery | B-23 | B-23 |
| B-24 conflicting statements | B-24 | B-24 |
| B-25 authorized vs silent exclusion | B-25 | B-25 |
| B-26 admissible vs inadmissible VERIFY | B-26 | B-26 |

The index lists each behaviour with its own intended and unacceptable entries. It is
the producer's pointer to those entries. The reviewer maps the behaviours
independently in `verification.md`.
