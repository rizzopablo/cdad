# Activation handoff to 019-002 (PC-9)

Locators are at revision `64aa4670`. Status: handoff. This is not an execution,
not a repair, and not a claim that any item is already supported.

**Scope boundary.** 019-001 is documentary. It does not change executable behaviour, does not
activate instructions, and does not repair the workspace state of `docs/.cdad-state.json`
(which is currently modified in the working tree; the earlier isolated repair committed
for the epic is a separate matter). Each item below is executable or instruction work owned
by 019-002, and each carries its focused regression obligation.

**Who writes the regression oracles.** The test-writer derives each oracle from the
approved specification and this handoff, under 019-002's own RED gate. This product does
not supply the test expectations; it names the surfaces and the behaviour they must show.

---

## Item 1 — Brainstorm single delivery incompatibility

- **Evidence:** `skills/cdad-cycle/scripts/cdad_result.py:826-840` admits `role-report` for architect `discovery` and `draft`, not `brainstorm`. `cdad_dispatch.py:999-1016` and `cdad_delegate_opencode.py:492-519` derive one delivery kind from that table and reject ambiguity (`discovery.md` §3.C).
- **Correction owned by 019-002:**
  - Admit `role-report` for architect `brainstorm`, and only there. The role axis stays closed for every other role and subphase.
  - Keep the single-delivery rule: the brainstorm delivery is the consultation report, not a draft.
  - Extend the substage prompt (`skills/cdad-cycle/packets/substages/architect-brainstorm.md`) with the mediated round trip (`roles-and-dialogue.md` §2) and the `READY FOR DRAFT` summary.
- **Focused regression obligation:**
  - A dispatch of architect `brainstorm` produces one `role-report` part and is accepted.
  - Architect `brainstorm` cannot deliver a spec draft, and the draft kinds stay rejected for it.
  - Test-writer, implementer, reviewer and the other closed roles remain rejected for `role-report` where they were rejected before.
- **Protected expectation to change deliberately:** `tests/test_006_005_u7_scribe_role_report.py:699-709`, whose case tuple includes `("architect", "brainstorm")` at `:708`. That case is the expectation this item changes. 019-002 must state the reason in the change record and must not change the other tuple entries.
- **Not allowed:** disguising the consultation as a draft, or silently switching the substage.

## Item 2 — Draft re-entry bypass of independent review

- **Evidence:** `skills/cdad-cycle/references/re-entry.md:251-253` sends a passing spec draft straight to the approver. The stage-2 sequence and the reviewer re-entry require the draft review first (`stage-2-specification.md:47-75`; `re-entry.md:266-278`) (`discovery.md` §3.D).
- **Correction owned by 019-002:** change the architect draft re-entry so that a passing draft is dispatched for independent review before the approval step, unless the owner's registered review exemption applies (`stage-2-specification.md:71-74`: `exempted_by`, `delegated`, `requested_by` and `reason`, in the same `stage_history` entry as the approval). Keep the review as it exists. Add no new gate. Under the exemption the review is not run, and the exemption is neither an approval nor a review verdict.
- **Focused regression obligation:** a check that the architect draft re-entry route reaches the draft review before the approval, across the canonical reference and the generated consumers (the stage-2 reference and the orchestrator agent). The check must exercise the route, not only the presence of words. It covers both routes: the reviewed route reaches E4 and E5 before E6; the exempted route reaches E6 only with the four exemption fields registered in the same `stage_history` entry, and records no verdict. A negative case: without the exemption, or with any of its four fields missing, the route cannot reach approval without the review.
- **Not allowed:** a route that permits approval before the verdict outside a registered exemption; treating a verdict as approval; treating an exemption as approval or as a verdict.

## Item 3 — Frozen packets and new publications

- **Evidence:** a published packet renders from its frozen instruction bytes (`skills/cdad-cycle/scripts/cdad_packet.py:1760-1774`, `:1849-1865`, `:1868-1879`). Editing a live instruction does not change a published packet.
- **Correction owned by 019-002:**
  - Instruction changes made by items 1–4 reach work only through **new publications**.
  - Record which in-flight packets were not updated. Do not rewrite any historical or frozen packet, including the packet of this unit.
- **Focused regression obligation:**
  - An already published packet renders byte-identically after the live instruction files change.
  - A new publication after a live change carries the new bytes, and its digests match them.
- **Not allowed:** claiming that frozen packets update automatically, or editing a frozen packet to match the new text.

## Item 4 — Idle closure, status and opening eligibility

- **Evidence:**
  - Closure guidance says `current_stage: done`, `active_feature: null` (`skills/cdad-cycle/references/stage-5-merge.md:187`). The epic handoff checks `done` (`skills/cdad-epic/references/feature-handoff.md:60-64`).
  - Closure registration writes `idle` and clears `active_feature` (`skills/cdad-cycle/scripts/cdad_packet.py:9195-9211`). Opening requires the coherent resting state (`:7293-7312`, `:686-722`).
  - The status projection recommends `open-unit` without the same coherence check (`:9495-9518`, `:9990-10033`) (`discovery.md` §3.F).
- **Correction owned by 019-002:**
  - Align the closing guidance and the epic check with the real transition (`idle`, `null`).
  - Make the status projection apply the same coherence precondition as `open_unit` before it selects the next route.
- **Focused regression obligation:**
  - After a correct closure, the status shows a route that opens the next unit, and opening succeeds without an incoherence error.
  - A state that is `done` with `active_feature: null` is reported as not at rest, with a diagnosis, and is not offered `open-unit` as a route.
- **Not allowed:** repairing the workspace state as part of this item. The repair of an existing state is separate from the permanent correction.

---

## Item 5 — Canonical role and reference text deltas (dialogue, recording, approval, pre-draft record)

- **Evidence:** `sources/roles/orchestrator.md:128-131` prohibits "do NOT approve specs" with no exception, and no allowance for owner dialogue in stage 2 (`activation-map.md` R1, R11). `skills/cdad-cycle/references/stage-1-discovery.md:63` sends the per-feature output to the draft's Technical context, which exists only after drafting (`activation-map.md` R5). `stage-2-specification.md` §2.3 (`:92-110`) defines the exception per feature or stage.
- **Correction owned by 019-002:**
  - Apply the three deltas of `roles-and-dialogue.md` §3 to `sources/roles/orchestrator.md`: a dialogue allowance; a recording allowance, explicit and bounded: materialize the architect's report unaltered in its own section, and write owner answers, corrections and notes, attributed, only in the Dialogue context section of `docs/specs/<feature>/discovery.md` (the orchestrator's power already exists in `orchestrator.md:302`); and the approval exception added to the existing prohibition. The write limit of that allowance covers only the authorship and location of the dialogue record and of the architect's report; every other write or materialization the cycle already authorizes stays allowed.
  - The orchestrator text points to §2.3. Change `stage-1-discovery.md:63` so the per-feature report is materialized unaltered in its own section of `discovery.md`. Align the architect's consultation wording (`activation-map.md` R2) and the stage-2 §2.1 routing.
- **Focused regression obligation:**
  - A check that the generated orchestrator text keeps every R11 prohibition, points to the approval exception stated once in `stage-2-specification.md` §2.3, and does not permit the orchestrator to write tests or code, or to author or alter the spec's content or the architect's report. It also checks that the report is materialized unaltered in its own section and that owner answers and notes are written only in the Dialogue context section. It checks, positively, that the generated orchestrator text still permits the other writes the cycle authorizes (materializing `plan-review.md`, the independent report, the spec draft and the approval records), so the narrowed limit is not read as a general prohibition.
- **Not allowed:** a general approval permission for the orchestrator; a recording allowance wider than materializing the report unaltered in its own section and writing notes and answers only in the Dialogue context section; a write limit that forbids writes or materializations the cycle already authorizes; a Stage-1 route that still points dialogue to the draft.

## Observed acceptance is not in this handoff

Real-agent use (the end-to-end journey and the five PC-11 cases) belongs to 019-002. Its
protocol is `acceptance-protocol-019-002.md`. Passing the regression obligations above does not
count as observed acceptance, and this product does not count as such.

## Preconditions 019-002 must check before it claims any item

1. The five items are delivered as executable or instruction changes in their canonical owners (`activation-map.md`).
2. Consumers are regenerated or republished as the map requires (R2 and R9).
3. The protected expectation changed in item 1 is named, with its reason.
4. No item is claimed to be active before its consumers have been regenerated and republished.
