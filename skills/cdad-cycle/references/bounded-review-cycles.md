# Bounded review cycles — single canonical owner

This file is the **single canonical owner** of how many correction rounds a unit
may consume, in which family, how consumption persists, how exhaustion is
adjudicated, how a round is noted in existing records and how accepted optional
residue is accumulated in an epic. Every consumer (stage references, templates,
role sources, packet blocks, handoffs, the epic skill) states only the
operational step it needs at its boundary and points here; none restates the
definitions.

Instruction-only. There is no CLI operation, flag, schema field, counter file or
parallel ledger for rounds: consumption is derived from existing findings and
disposition artifacts and from existing `stage_history` entries. Enforcement is
procedural, and a bounded trace does not prove universal agent compliance.

## 1. The round and the three families

A **round** consists of:

1. an assessment;
2. the disposition of its findings;
3. one corrective batch, when needed;
4. the verification applicable to those corrections.

A clean assessment closes its round without a corrective batch. An interrupted
or failed verification leaves the round unresolved; it neither erases
consumption nor supplies closure evidence.

Three **families**, each with its own allowance (unused rounds never transfer
between families):

- **Draft** — independent review of the specification and plan *together*,
  disposition, architect correction and the applicable focused re-review. Spec
  and plan share ONE allowance.
- **Audit** — AUDIT assessment and dispositions, applicable approved POST-AUDIT
  changes and their verification. Corrections to deficient audit outputs or
  substitutions stay in this family. Ordinary RED→GREEN work is not
  automatically an audit-correction round; a unit with no audit work has no audit
  round (never fabricate one).
- **Result** — independent result review, disposition, corrections through the
  competent roles, applicable executable checks and the closing contextual
  re-review.

The initial substantive assessment consumes round 1. Transport delivery alone
does not consume a round.

**The closing check.** A closing check belongs to the verification of the
current round. If it finds unresolved or new findings that continue the
correction loop, it also supplies the assessment that opens the next round, and
that next round consumes the next allowance. Do not commission another
assessment merely to count it. A focused re-review is *verification of the
current round*, not a free pass: if its findings continue the loop it is the
opening assessment of the next round.

**At the maximum**, record that another round is required but not ordinarily
authorized. Finish the required verification of the last permitted corrective
batch, then adjudicate (§3); begin no unauthorized next correction. A finding
resolved by supported dismissal or by an accepted optional-debt disposition does
not continue the loop. Calling a continuing correction a "verification
touch-up" does not avoid the next round.

Existing explicit exemptions keep their existing scope. An exemption is not an
executed verification, and the mechanical-fix exception never covers a corrected
contextual promise.

## 2. The maximum and persistent consumption

**Declaration.** The architect proposes, in the unit specification, a positive
integer **maximum** with a concrete difficulty/risk justification (uncertainty,
coupling, correction difficulty, consequence of error; not a bare "high risk"
label) and its status (**provisional** or **adopted**). That maximum applies
independently to each of the three families. The justification is the
architect's; scheduling and stopping are the orchestrator's.

**Provisional adoption.** The proposal in the draft provisionally bounds the
scheduling of the draft review; the competent approver adopts it with the
specification. If provisional scheduling authority is unavailable, the
orchestrator obtains that decision before starting the loop. The owner's example
figures are guidance, never mandatory quotas.

**Identity.** Consumption belongs to **unit + family** — never to a packet,
execution, stage label, route or contract digest. Re-dispatch,
suspension/resumption, changed digests, renamed substages, identical technical
retries and execution replacement retain the history. Spec and plan cannot get
separate draft allowances by changing their dispatch arrangement.

**Retries.** Reconcile a repeated receipt or registration with its original
event: an identical retry is the same event, not a new opportunity and not a
consumed round. An identical unproductive attempt triggers the existing strategy
review (`re-entry.md` §"Retry without new information — replanning the unit");
a numerical allowance never overrides that trigger.

**Revision.** A revised maximum or an authorized extension keeps the consumed
ordinal; it never restarts at round 1. Replanning preserves predecessor identity
and outstanding obligations; renaming the same work never establishes a fresh
budget.

**Work already underway** when this guidance is adopted: reconcile the
recoverable assessments and correction batches before the next dispatch. Do not
assume zero consumption because older notes lack the note pattern. Declare
unresolved counting uncertainty and obtain its disposition before further
corrective work.

## 3. Exhaustion decision

At exhaustion the orchestrator stops ordinary corrections and disposes of every
remaining finding. A short disposition identifies:

- originating unit, family, round and finding;
- the affected promise, or the evidence that it is outside current commitments;
- the latest examined artifact/version and verification evidence;
- concrete consequence and realistic exposure;
- classification and its supporting reason;
- resolution criterion, destination and responsible party;
- decision-maker and authority.

Permitted outcomes:

- **Supported dismissal** — the evidence does not establish the alleged
  obligation or breach.
- **Accepted optional residue** — current promises remain established; the
  consequence is understood and acceptable to the competent authority. Record
  the residue (§5) without withholding otherwise legitimate closure.
- **Blocked / replan** — a committed promise is unmet, required verification is
  missing, the effect on an obligation is unknown, or the debt is unacceptable.

"Budget exhausted" is never evidence for dismissing a blocker; neither is
elapsed effort or a reviewer's label alone. Missing required verification, an
unmet promise or an unknown relevant impact cannot become success because the
allowance ended.

**Further corrective work after exhaustion** is authorized only by a recorded
adjudication that a committed promise remains unmet. It names the unmet promise,
the supporting evidence, the competent authority, the next corrective objective
and a **finite further ceiling**, carrying the consumed ordinal forward. Reaching
that ceiling requires another explicit decision. An extension is not available to
polish optional work. An unavailable verification remains a block unless a
legitimate approved contract change resolves the obligation. Scope or promise
changes follow the existing contract-change and approval procedure; this file
grants no approval authority.

Producer, independent verifier and competent approver remain distinct
responsibilities; no allowance, exemption or debt classification supplies absent
evidence.

## 4. Recording a round: the fixed note pattern

Use the existing findings/disposition artifacts and the existing `stage_history`
entries. When the ordinary transition is registered through
`register-transition`, put the summary in its existing `--note`. The fixed
pattern (prose labels inside the note, not JSON fields or CLI arguments):

```text
review-round unit=<id>; family=<draft|audit|result>; round=<n>/<ceiling>; event=<assessment|correction|verification|adjudication>; outcome=<brief outcome>; evidence=<recoverable references>; next=<action or stop>; authority=<actor and authority reference>
```

- `round` is the cumulative ordinal; the ceiling is the currently applicable
  authorization.
- Record the summary with the ordinary event's own registration; invent no
  transition class for round bookkeeping.
- The assessment note marks where an ordinal was first consumed. Later
  correction/verification notes carrying that ordinal are not further
  consumption.
- If a closing check opens the next round, its note states the current
  verification outcome and the next consumed ordinal. At exhaustion it states
  "next round required; stopped" with the adjudication reference.
- Full evidence and per-finding reasoning live in the existing review, audit or
  disposition artifacts; notes point to them.
- Before the next dispatch, reconcile historical entries and the artifacts they
  reference. Keep no independently editable total.
- A repeated transition may keep its existing note through idempotency; changing
  `--note` does not amend a registered event. Record later substantive evidence
  with its own legitimate event.

An unavailable or ambiguous historical record blocks the decision that depends
on it; it is never silently repaired by inventing prior consumption.

**Handoff content.** A handoff to a role (or a receiving session) carries, from
the ordinary records: the unit, the family, the cumulative ordinal and ceiling,
the evidence references, the verification still required and the stop/escalation
status. Roles report the current family and round, the verification they ran or
require, and any stop condition; a role never authorizes an extra round itself.

## 5. One non-recursive accumulation unit

When an epic holds accepted optional residue, place it in **one ordinary
accumulation unit**, queued after the other planned units and before epic
integration/closure, in the existing epic plan and normal unit records (not a new
phase). Each admitted item retains its originating unit, family, round and
finding; the accepted consequence and disposition authority; and its resolution
criterion and responsible party. Consolidating duplicates preserves every origin.

Before opening the accumulation unit, approve its bounded membership and
contract and declare its own architect-justified maximum (§2). New items after
approval enter only by explicit amendment, never silently. The unit follows
normal verification and approvals and **cannot create another accumulation
unit**; its optional residual work may remain explicitly accepted debt, while
unresolved committed obligations block closure or require a legitimate approved
change. Accumulation never replenishes correction opportunities.

Without an epic, accepted residue goes to the existing methodological `debt.md`
(layout resolved by `layout`), which does not create an epic. If no residue is
admitted, record that result instead of opening an empty unit. Accepted debt
never substitutes for an unmet current promise.
