# Activation map — canonical owners and effective consumers (PC-8)

Locators are at revision `64aa4670`. Status: proposal. Nothing in this map is
active. The map says which source must change, which consumers must follow it,
and what currently contradicts it.

## How to read it

- **Canonical owner.** The one source that defines the rule. A consumer points to it or operationalises it; it never defines the rule again.
- **Effective consumers.** Everything that causes an agent to act on the rule: generated agents (generic and Odoo variants), packet sources and substages, legacy handoff templates, reference files that orchestrators load by path, and lightweight or explanatory surfaces.
- **Activation is not explanation.** Editing an explanatory text does not activate a rule. Activation means: owner changed, consumers regenerated or republished, executable behaviour delivered, and evidence recorded in 019-002.

**Generator path.** The generator composes role agents per stack and the orchestrator from the sources: `scripts/cdad-generate.py:915-946`. The generator also keeps role descriptions in `ROLE_META` (`:506-527`), which are consumer text and must be reconciled too.

**Republication.** A published packet renders from its frozen instruction bytes, not from live files (`skills/cdad-cycle/scripts/cdad_packet.py:1760-1774`, `:1849-1865`). A rule change reaches an in-flight packet only through a new publication (R9).

---

## R1 — Functional dialogue belongs to the orchestrator

- **Canonical owners:** `sources/roles/orchestrator.md` (operating rules `:128-137`; own-contract row `:298-302`) for the prohibitions and allowances; `skills/cdad-cycle/references/stage-2-specification.md` §2.3 (`:76-110`) for the text of the approval exception. The orchestrator text points to that text and does not restate it.
- **Consumers:** the generated orchestrator agent (`scripts/cdad-generate.py:937-946`); the stage-2 workflow (`skills/cdad-cycle/references/stage-2-specification.md:7-17`, which still assigns brainstorm to the architect).
- **Incompatibility:** the orchestrator's rules forbid role work inline and say "do NOT approve specs" with no allowance for owner dialogue in stage 2. The stage-2 reference hands brainstorming to the architect in brainstorm mode. The only existing dialogue allowance is for initial discovery (`skills/cdad-cycle/references/stage-1-discovery.md:14-30`), which is not general.
- **Reconciliation:** three deltas to this owner, as listed in `roles-and-dialogue.md` §3: (1) a bounded allowance for stage-2 functional dialogue; (2) a recording allowance, made explicit and bounded, to materialize the architect's per-feature report unaltered in its own section, and to write owner answers, corrections and notes, attributed, only in the Dialogue context section of `docs/specs/<feature>/discovery.md` (`handoff-fidelity.md` §2). That limit covers only the authorship and location of the dialogue record and of the architect's report; every other write the cycle already authorizes stays allowed. It is not a new power: `orchestrator.md:302` already allows materializing read-only artifacts and editing `docs/**`; (3) the sole approval exception of `roles-and-dialogue.md` §1, added to the existing prohibition, whose text is canonical in `stage-2-specification.md` §2.3. The prohibitions of R11 stay. Update stage-2 §2.1 to route the dialogue through the orchestrator.

## R2 — The architect performs technical consultation, not the owner interview

- **Canonical owner:** `sources/roles/architect.md` (contract row `:105`; "first you ask" `:73`; packet substages `:76`).
- **Consumers:**
  - Generated architect agents, generic and Odoo: `scripts/cdad-generate.py:506-510` (`ROLE_META["architect"]` description "Socratic brainstorm + spec draft" and the stage text), composed per stack at `:915-924`.
  - Odoo domain guidance: `skills/odoo-architect/SKILL.md:138-147` (asks configuration-versus-custom, OCA/core, SPoC and PL questions).
  - Packet role source: `skills/cdad-cycle/packets/roles/architect.md` (read-only, no approval, documentary duty; does not describe the consultation round trip).
- **Incompatibility:** the architect's row and the generated description say "Socratic brainstorm", which is read as the architect conducting the owner interview. The Odoo guidance has the same effect.
- **Reconciliation:** rename the function to targeted technical consultation returned to the orchestrator. Keep "read-only", "never approves its own proposal" and "does not write the product". The Odoo questions for owner roles (SPoC, PL) are routed as owner questions by the orchestrator, while the architect keeps the technical questions.

## R3 — Brainstorm consultation has a supported delivery and a defined prompt

- **Canonical owners:**
  - Delivery: `skills/cdad-cycle/scripts/cdad_result.py:826-840` (`_allowed_kinds`). Packet substages for architect: `skills/cdad-cycle/scripts/cdad_packet.py:88` (`discovery`, `brainstorm`, `draft`).
  - Prompt: `skills/cdad-cycle/packets/substages/architect-brainstorm.md:1`.
- **Consumers:** packet dispatch `skills/cdad-cycle/scripts/cdad_dispatch.py:999-1016` (derives a single delivery kind from the table); the OpenCode delegation adapter `skills/cdad-cycle/scripts/cdad_delegate_opencode.py:492-519`; the legacy consultation prompt `skills/cdad-cycle/references/handoff-prompts.md:235-259`.
- **Incompatibility (verified):** the table admits `role-report` for architect `discovery` and `draft` but not `brainstorm`. Dispatch of `architect/brainstorm` therefore fails with "table does not determine a single artifact kind" (`discovery.md` §3.C). The existing test protects that rejection: `tests/test_006_005_u7_scribe_role_report.py:699-709` includes `("architect", "brainstorm")` in the cases that must stay rejected (line `:708`). The substage prompt is one sentence and does not state the round trip or the readiness summary.
- **Reconciliation:** keep the path (D5). 019-002 admits `role-report` for architect `brainstorm` only, keeps the other roles closed, updates the protected expectation deliberately, and extends the substage prompt with the round trip and the `READY FOR DRAFT` summary. See `activation-handoff-019-002.md` item 1.

## R4 — Draft re-entry goes through independent review before approval, unless the registered exemption applies

- **Canonical owner:** `skills/cdad-cycle/references/stage-2-specification.md:47-75` (draft review sub-phase: "The draft does not reach the approval without an independent review"; its only exception is the registered exemption, `stage-2-specification.md:71-74`).
- **Consumers:** the architect draft re-entry `skills/cdad-cycle/references/re-entry.md:240-264`; the reviewer re-entry `re-entry.md:266-278` (consistent); the orchestrator's stage-2 steps `stage-2-specification.md:13-14`; the orchestrator's reference-loading rule `sources/roles/orchestrator.md:59,227` (loads `re-entry.md`).
- **Incompatibility (verified):** `re-entry.md:251-253` says that when the spec draft passes, "pass the spec to the user for approval". A consumer that follows that subsection alone skips the review (`discovery.md` §3.D).
- **Reconciliation:** change the architect draft re-entry so that a passing draft is dispatched for review (`re-entry.md:266-278`) before the approval, as in stage 2 steps 5–6, unless the owner's registered exemption applies (`stage-2-specification.md:71-74`). Under the exemption the review is not run and the approval records it; the exemption is neither an approval nor a review verdict. No new gate is added; the existing one is respected (`readiness-and-approval.md` §3). Both routes, reviewed and exempted, belong to the regression obligation of 019-002 item 2.

## R5 — The dialogue context uses an attributed section; decision transport stays governing-only

- **Canonical owners:** the per-feature discovery artifact's **Dialogue context** section (a documentary convention, `handoff-fidelity.md` §2–§3); `current_decisions` for governing project decisions only (`skills/cdad-cycle/scripts/cdad_packet.py:94-111`, validation `:1538-1560`); the Memory Bank index (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:5-34`).
- **Consumers:** the stage-1 and stage-2 references that name the discovery artifact (`stage-1-discovery.md:63`; `stage-2-specification.md:21-22`); packet builders that accept `current_decisions`; the orchestrator's packet preparation and its recording allowance (R1).
- **Incompatibility:**
  - `stage-1-discovery.md:63` says the per-feature output "goes to the Technical context section of the spec in Stage 2". That section exists only after the draft, so dialogue recorded before drafting has no place to go. The fix is to materialize the report unaltered in `discovery.md` first, which the cycle already does (`handoff-fidelity.md` §2, commit `c1016fb5`).
  - `current_decisions` is the only existing structured transport, and it cannot carry proposals or open questions (`discovery.md` §3.E). A consumer might overload it.
- **Reconciliation:** change `stage-1-discovery.md:63` so the report is materialized unaltered in its own section of `discovery.md`, and the draft's Technical context is a later copy in Stage 2. Document the Dialogue context section in the stage references. State in the same place that `current_decisions` holds only governing decisions. No packet field, no state field, no schema value is added.

## R6 — Readiness is checked at brainstorm re-entry

- **Canonical owner:** `skills/cdad-cycle/references/re-entry.md:230-238` (brainstorm re-entry: explicit decisions in the key categories; the user made them).
- **Consumers:** the orchestrator's stage-2 re-entry (`stage-2-specification.md:27-29`).
- **Incompatibility:** the current check covers category coverage and who made the decisions. It does not check the five readiness conditions (R1–R5 of `readiness-and-approval.md` §2), nor the unaccepted-proposal and correction treatment.
- **Reconciliation:** extend the same check with R1–R5. The check is recorded as readiness, not as approval.

## R7 — Idle closure, status and opening agree

- **Canonical owners:**
  - Closure effect: `skills/cdad-cycle/scripts/cdad_packet.py:9195-9211` (closure writes `current_stage = idle`, `active_feature = null`).
  - Resting coherence: `skills/cdad-cycle/scripts/cdad_packet.py:686-722` (`_validate_idle_coherence`: `active_feature` null if and only if `current_stage` is idle).
  - Opening precondition: `skills/cdad-cycle/scripts/cdad_packet.py:7293-7312` (`open_unit` requires the coherent resting state).
- **Consumers:** closing guidance `skills/cdad-cycle/references/stage-5-merge.md:187` ("update state (`current_stage: done`, `active_feature: null`)"); the epic handoff check `skills/cdad-epic/references/feature-handoff.md:60-64`; the status projection `cdad_packet.py:9495-9518` (`_next_route`) and `:9990-10033` (`_situation_projection`).
- **Incompatibility (verified):**
  - The closing guidance says `done` with `active_feature: null`. The closure transition writes `idle`. The epic handoff checks `done`. This is a mismatch between instruction and transition.
  - The status projection recommends `open-unit` for a rest state without applying `_validate_idle_coherence`. `open_unit` then rejects the same state as incoherent (`discovery.md` §3.F). A correct closure can therefore block the next unit.
- **Reconciliation:** align the guidance and the epic check with `idle`/`null`. Make the status projection apply the same coherence check before it selects the next route. Repairing the earlier workspace state is **not** part of this map (`activation-handoff-019-002.md` item 4).

## R8 — Lightweight applicability

- **Canonical owners:** the trivial variant `skills/cdad-cycle/references/stage-2-specification.md:116-122`; the standalone skill `skills/cdad-spec-and-test/SKILL.md` (its integration section `:95-104` already defers gates to the cycle).
- **Consumers:** `README.md:21-25` (recommends the standalone skill for bounded work); `CDAD_metodologia.md:114` and `:195` (explanatory "CDAD light" tier).
- **Incompatibility:** the methodology describes "optional review" and "isolated sessions for the critical components only" for its light tier (`CDAD_metodologia.md:114`). The cycle makes the draft review mandatory (`stage-2-specification.md:47-50`) and keeps stage-3 separations.
- **Reconciliation:** resolved in `lightweight-paths.md` §2. The methodology gets a pointer to the cycle references. Its text does not change the cycle's rules.

## R9 — Frozen packets are not rewritten; a change needs a new publication

- **Canonical owners:** the publication capture `skills/cdad-cycle/scripts/cdad_packet.py:1849-1865` (reads live files once, stores bytes and digests) and the frozen render `:1760-1774`, `:1868-1879`.
- **Consumers:** every published packet (`.cdad/packets/<id>/PACKET.md` and `REQUEST.json`), including this unit's own packet.
- **Incompatibility:** a change to `skills/cdad-cycle/packets/**` or to a role source does not reach a published packet. Any consumer that assumes automatic update is wrong (`discovery.md` §4.2).
- **Reconciliation:** 019-002 makes the instruction changes, republishes the affected packets as new publications, and records which in-flight packets were not updated. Historical frozen packets are not rewritten.

## R10 — Documentary norm (kept as it is)

- **Canonical owner:** `skills/cdad-cycle/references/documentary-contracts.md` (sections 1–7).
- **Consumers:** `skills/cdad-cycle/packets/roles/architect.md:3` (documentary duty, points to the norm).
- **Incompatibility:** none found for this design.
- **Reconciliation:** none. This design only points to the norm; it does not restate it.

## R11 — The orchestrator does not substitute for technical, test, implementation or review work (kept)

- **Canonical owner:** `sources/roles/orchestrator.md:128-131` and `:298-307`.
- **Consumers:** the generated orchestrator agent; the R1 allowance must be drafted so that it does not widen these.
- **Incompatibility:** none if R1 is drafted narrowly. This is the main risk of R1. The approval exception is the second risk: a consumer could read "except under delegation" as a general permission.
- **Reconciliation:** the R1 allowance names the prohibitions explicitly in the same text. The approval exception is the only exception to "do NOT approve specs", and its text is stated once, canonically, in `stage-2-specification.md` §2.3 (R1); the orchestrator text points to it.

## R12 — Standalone architecture uses the legacy path

- **Canonical owners:** `skills/cdad-cycle/scripts/cdad_packet.py:2398-2410` (an architect packet requires an active epic; without one, the legacy path applies); `skills/cdad-cycle/references/handoff-prompts.md:41-45`.
- **Consumers:** the legacy architect templates `handoff-prompts.md:235-259`; the standalone architecture intake.
- **Incompatibility:** a standalone architect cannot be prepared as a packet. Changing only the prepared path leaves the standalone path on older text.
- **Reconciliation:** R1–R6 must be applied to the legacy templates as well as to the packet sources, so the two paths give the same rule.

---

## Summary of owners changed by activation

| Owner | Rules |
|---|---|
| `sources/roles/orchestrator.md` | R1 (dialogue allowance, recording allowance, approval exception), R11 (kept) |
| `sources/roles/architect.md` | R2 |
| `skills/cdad-cycle/references/stage-2-specification.md` | R1, R3, R4 |
| `skills/cdad-cycle/references/re-entry.md` | R4, R6 |
| `skills/cdad-cycle/references/stage-1-discovery.md`, `handoff-prompts.md` | R2, R5, R12 |
| `skills/cdad-cycle/packets/substages/architect-brainstorm.md` and `roles/architect.md` | R2, R3 |
| `skills/cdad-cycle/scripts/cdad_result.py` (executable) | R3 |
| `skills/cdad-cycle/references/stage-5-merge.md`, `skills/cdad-epic/references/feature-handoff.md`, `cdad_packet.py` status projection (executable) | R7 |
| `scripts/cdad-generate.py` (descriptions, regeneration) | R2 |
| `skills/odoo-architect/SKILL.md` | R2 |
| `CDAD_metodologia.md` and `README.md` (pointers only) | R8 |

Executable changes and their regression evidence belong to 019-002, not to this product.
