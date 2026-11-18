# Specification draft

**Feature:** `019-005-bounded-review-cycles`  
**Version:** `draft-001`  
**Status:** Approved with amendment 001 (self-contained dispatch), independently reviewed.

## Functional description

A process owner wants CDAD to stop prolonged review-and-fix loops without concealing unfinished obligations. Starting with a unit ready for specification, the architect proposes a justified maximum. The orchestrator applies that maximum separately to draft review, test-audit corrections and result review.

The first useful result is a traceable decision: proceed within the allowance, stop for adjudication, or close with supported evidence and explicitly accepted optional residue. Re-dispatching the same work never grants a fresh allowance.

### Global constraints

- Instruction-only behavior: no new CLI operation, flag, schema field, counter file or parallel ledger.
- Preserve role separation, independent verification, existing approval authority and protected acceptance inputs.
- Resolve methodology paths through the existing layout contract; do not migrate historical records.
- Change canonical sources and regenerate affected derived agents; do not hand-edit generated agents.
- No installation, deployment or publication is authorized.

## Authority and admitted sources

The following constitute the design baseline:

- `discovery-notes.md:6–22`: owner’s requested per-unit bound, audit inclusion and epic-end accumulation.
- `architect-consultation-001.md:18–151`: technical alternatives and existing safeguards.
- Validated draft packet, **Current decisions**: separate family allowances; specification/planning configuration; provisional proposal and approval; evidence-backed exhaustion decisions; standalone debt; explicit accumulation amendment.
- `stage-2-specification.md:49–101`: draft review and verification per promise.
- `stage-4-review.md:5–54,207–214`: proportional review and closing verification.
- `re-entry.md:80–86,207–215,328–337`: registration, retry reconciliation and audit substitutions.
- `documentary-contracts.md:63–89,153–178`: pending classification and documentary acceptance.
- `planning-contract-draft.md`, §4.1: plan block.
- `Makefile:1–23`: declared regeneration and validation commands.

Paths above are relative to their existing repository locations. References describe the examined snapshot, not proof of future agent compliance. Recommendations in the consultation become requirements only where adopted by the validated packet or proposed explicitly in this draft.

## Review allowance for this unit

**Proposed maximum: 3 rounds per family.**

This is a proposal, not an approval. It provisionally bounds scheduling of this draft review; the competent approver adopts it with the specification. If provisional scheduling authority is unavailable, the orchestrator obtains that decision before starting the loop.

**Justification:** moderate difficulty, with meaningful semantic risk. There is no new execution machinery, but the change crosses three existing correction loops, effective role inputs, lightweight guidance and epic closure. The principal risks are hiding repeated corrections inside “verification,” resetting consumption and downgrading unmet promises. Three rounds provide a bounded opportunity for initial assessment, substantive correction and focused reconciliation without treating the owner’s example figures as mandatory quotas.

Each family receives its own allowance of three; unused rounds do not transfer between families.

## Operating contract

### 1. One round, three families

A round consists of:

1. An assessment.
2. Disposition of its findings.
3. One corrective batch, when needed.
4. The verification applicable to those corrections.

A clean assessment closes its round without a corrective batch. Interrupted or failed verification leaves the round unresolved; it does not erase consumption or supply closure evidence.

The three families are:

- **Draft:** independent review of specification and plan together, disposition, architect correction and applicable focused re-review. Specification and plan share one allowance.
- **Audit:** AUDIT assessment/dispositions, applicable approved POST-AUDIT changes and verification. Corrections to deficient audit outputs or substitutions remain in this family. Ordinary RED→GREEN work is not automatically an audit-correction round.
- **Result:** independent result review, disposition, corrections through the competent roles and applicable executable checks and closing contextual re-review.

The initial substantive assessment consumes round 1. Transport delivery alone does not.

A closing check belongs to verification of the current round. If it finds unresolved or new findings that continue the correction loop, it also supplies the assessment opening the next round; **that next round consumes the next allowance**. Do not commission another assessment merely to count it.

At the maximum, record that another round is required but not ordinarily authorized. Finish the required verification of the last permitted corrective batch, then adjudicate; do not begin an unauthorized next correction.

A finding resolved by supported dismissal or accepted optional-debt disposition does not continue the correction loop. Calling a continuing correction a “verification touch-up” does not avoid the next round.

Existing explicit exemptions retain their existing scope. An exemption is not an executed verification, and the mechanical-fix exception does not cover corrected contextual promises.

### 2. Persistent identity and consumption

Consumption belongs to **unit + family**, not to a packet, execution, stage label, route or contract digest.

Re-dispatch, suspension/resumption, changed digests, renamed substages, identical technical retries and execution replacement retain the history. Spec and plan cannot receive separate draft allowances by changing their dispatch arrangement.

Reconcile a repeated receipt or registration with its original event. An identical retry is the same event, not a new opportunity or fictitious consumed round. An identical unproductive attempt invokes the existing strategy-review rule; a numerical allowance never overrides that trigger.

A revised maximum or authorized extension retains the consumed ordinal. It does not restart at round 1. Replanning preserves predecessor identity and outstanding obligations; merely renaming the same work cannot establish a fresh budget.

For work already underway when this guidance is adopted, reconcile recoverable assessments and correction batches before the next dispatch. Do not assume zero consumption because older notes lack the new pattern. Declare unresolved counting uncertainty and obtain its disposition before further corrective work.

### 3. Exhaustion decision

At exhaustion, the orchestrator stops ordinary corrections and disposes every remaining finding. A short disposition must identify:

- Originating unit, family, round and finding.
- Affected promise or the evidence that it is outside current commitments.
- Latest examined artifact/version and verification evidence.
- Concrete consequence and realistic exposure.
- Classification and its supporting reason.
- Resolution criterion, destination and responsible party.
- Decision-maker and authority.

Permitted outcomes:

- **Supported dismissal:** the evidence does not establish the alleged obligation or breach.
- **Accepted optional residue:** current promises remain established; consequence is understood and acceptable to the competent authority. Record the residue without withholding otherwise legitimate closure.
- **Blocked/replan:** a committed promise is unmet, required verification is missing, effect on an obligation remains unknown, or debt is unacceptable.

“Budget exhausted” is not evidence for dismissing a blocker. Neither elapsed effort nor a reviewer’s label alone establishes acceptable debt.

Only a recorded adjudication that a committed promise remains unmet may authorize further corrective work after exhaustion. It names the unmet promise, supporting evidence, competent authority, next corrective objective and a **finite further ceiling**, carrying the consumed ordinal forward. Reaching that ceiling requires another explicit decision; it never authorizes indefinite work.

An extension is not available merely to polish optional work. An unavailable verification remains a block unless a legitimate approved contract change resolves the obligation.

Scope or promise changes follow the existing contract-change and approval procedure. This feature grants no additional approval authority.

### 4. Existing records, one minimal note pattern

Use existing findings/disposition artifacts and existing `stage_history` entries. Where the ordinary transition is registered through `register-transition`, put the summary in its existing `--note`.

The fixed note pattern is:

```text
review-round unit=<id>; family=<draft|audit|result>; round=<n>/<ceiling>; event=<assessment|correction|verification|adjudication>; outcome=<brief outcome>; evidence=<recoverable references>; next=<action or stop>; authority=<actor and authority reference>
```

These are prose labels inside the existing note, not new JSON fields or CLI arguments. `round` identifies the cumulative ordinal; the ceiling identifies the currently applicable authorization.

- Record the summary with the ordinary event’s existing registration. Do not invent a transition class for round bookkeeping.
- The assessment reference identifies when an ordinal was first consumed. Subsequent correction/verification summaries carrying that ordinal are not additional consumption.
- If a closing check opens the next round, its note states the current verification outcome and the next consumed ordinal. At exhaustion it instead states “next round required; stopped,” with the adjudication reference.
- Full evidence and per-finding reasoning live in the existing review/audit/disposition artifacts; notes point to them.
- Before the next dispatch, reconcile historical entries and referenced artifacts. Do not maintain an independently editable total.
- A repeated transition may retain its existing note through idempotency. Do not claim that changing `--note` amends a registered event. Record subsequent substantive evidence with its legitimate subsequent event.

An unavailable or ambiguous historical record blocks the decision that depends on it; it is not silently repaired by inventing prior consumption.

### 5. One non-recursive accumulation unit

When accepted optional residue exists in an epic, place it in **one ordinary accumulation unit**, queued after the other planned units and before epic integration/closure. Represent it in the existing epic plan and normal unit records, not a new phase.

Each admitted item retains:

- Originating unit, family, round and finding.
- Accepted consequence and disposition authority.
- Resolution criterion and responsible party.

Consolidating duplicates preserves their origins.

Before opening the accumulation unit, approve its bounded membership and contract, and declare its own architect-justified maximum. New items after approval require explicit amendment; they do not enter silently.

The accumulation unit follows normal verification and approvals. It cannot create another accumulation unit. Its optional residual work may remain explicitly accepted debt; unresolved committed obligations block closure or require a legitimate approved change.

Without an epic, accepted residue goes to the existing methodological `debt.md`; this does not create an epic. If no residue is admitted, record that result rather than opening an empty accumulation unit.

### 6. Minimal instruction surface and ownership

Create one canonical reference:

`skills/cdad-cycle/references/bounded-review-cycles.md`

It owns the general round definition, family identity, exhaustion rules and accumulation semantics. Existing consumers supply only the operational action needed at their boundary and point to that owner.

- **Stage 2 reference and spec template:** architect’s maximum, difficulty/risk reason, provisional/adopted status and counting identity; reconcile “not a new full round” with the distinction between focused verification and another corrective round.
- **Stage 3 and POST-AUDIT re-entry:** audit-family application; retain substitution safeguards.
- **Stage 4 reference:** final permitted verification and exhaustion disposition, without redefining review calibration.
- **Re-entry reference:** note pattern, reconciliation and existing retry interaction.
- **Epic skill and plan/closure templates:** project planning guidance and the single accumulation unit.
- **Architect/orchestrator role sources:** declaration, scheduling and stopping duties.
- **Affected role packet blocks and legacy handoffs:** sufficient operational instructions for the receiver to report the current family/round, required verification and stop/escalation.
- **Lightweight product guidance:** replace the unconditional Fix→Build-again loop with the same bounded rule; absent audit work does not imply a fabricated audit round.
- **Generated agents:** derive affected runtime/base/domain consumers through the declared generator.

Every new unit specification declares its maximum, concrete difficulty/risk justification, independent family allowances and adoption status. Handoffs preserve current consumption, evidence and next authorization; roles do not independently authorize extra rounds.

An inventory must identify affected consumers and justified exclusions. A pointer is insufficient when the receiver’s actual inputs do not make the required action recoverable.

## Observable promises and postconditions

### Promise A — Corrections stop at a known, persistent boundary

**Property:** the operator can identify the next permitted action without obtaining a fresh allowance by relabeling work.

- **PC-1:** instructions and the specification template require a positive integer unit maximum with difficulty/risk justification and provisional/adopted status; that maximum applies independently to the three named families.
- **PC-2:** instructions distinguish one corrective round from its closing verification, group specification and plan, include audit corrections and preserve required final verification.
- **PC-3:** a closing check continuing the correction loop consumes the next round when available; exhaustion stops ordinary correction. Identity changes and identical retries do not reset consumption.

**Method:** contextual review, including the bounded observed-use exercise below.

**Acceptance:** the independent reviewer finds no contradictory actionable instruction among inventoried consumers; the observed trace correctly identifies consumption and stopping.

**Evidence:** source/consumer inventory, contextual report with citations, actual exercise inputs/outputs and consumption decisions.

**Limits:** no automatic threshold enforcement; a bounded trace does not prove universal agent compliance.

### Promise B — Stopping never masquerades as success

**Property:** the owner sees why work may close, remain blocked or receive finite further authorization.

- **PC-4:** exhaustion instructions require the listed evidence and distinguish dismissal, accepted optional residue and unmet/unknown obligations.
- **PC-5:** further corrective work after exhaustion requires a recorded unmet-promise adjudication with finite authorization and carried consumption; changing scope retains the existing approval procedure.
- **PC-6:** missing required verification, an unmet promise or unknown relevant impact cannot become success because the allowance ended.

**Method:** contextual review and observed exercise.

**Acceptance:** an unresolved committed finding at the limit remains blocked; an evidenced optional residue receives a separate supported disposition; neither is silently reclassified.

**Evidence:** latest check, finding-by-finding disposition, authority and subsequent-action record.

**Limits:** the exercise evaluates supplied evidence and reasoning, not infallible severity classification.

### Promise C — Consumption is recoverable without another ledger

**Property:** a fresh orchestrator can recover the allowance and next action from ordinary records.

- **PC-7:** re-entry instructions use the fixed note pattern in existing records, reconcile repeated events and distinguish consumption from multiple summaries of one round; no new CLI/schema/counter mechanism is introduced.
- **PC-8:** candidate handoffs preserve family, cumulative ordinal, ceiling, evidence and stop/escalation status; an independent receiving session recovers the same next action without hidden conversation.

**Method:** contextual review and bounded handoff observation.

**Acceptance:** the independent receiver reconstructs the correct current consumption and authorized next action from the supplied ordinary records.

**Evidence:** actual handoff, referenced ordinary records and receiver’s answer.

**Limits:** no free-text parser, automatic repair or historical completeness guarantee is promised.

### Promise D — Accepted residue has one bounded destination

**Property:** accepted optional work does not create an endless succession of cleanup cycles.

- **PC-9:** epic guidance provides one accumulation unit with provenance, consequence, resolution criteria, bounded membership, its own maximum and normal gates before epic closure.
- **PC-10:** membership amendments are explicit; recursive accumulation is prohibited; standalone residue goes to methodological debt and unresolved obligations do not disappear into that destination.

**Method:** contextual review plus the accumulation disposition in the exercise.

**Acceptance:** the reviewed plan/closure guidance and observed disposition preserve origins, forbid automatic admission and do not propose a successor accumulation cycle.

**Evidence:** cited candidate guidance and the exercise’s accumulation/standalone disposition.

**Limits:** this feature does not implement or complete the future accumulated fixes.

### Promise E — the dispatch carries everything the role needs

**Property:** a role never has to discover, inherit or guess a resource its unit
requires.

- **PC-11:** the dispatch names every external executable the unit requires, with an
  explicit locator line, together with the product root. A role uses the named path
  and does not resolve it from installation metadata.
- **PC-12:** every required read and write lies within the declared scopes. When a
  required resource falls outside them, the correct outcome is a reported gap, never
  a search, an out-of-scope read or an improvised substitute.
- **PC-13:** the dispatch does not depend on instructions that a runtime loads
  automatically from a directory. Anything required from such a file is carried in
  the packet or in a reference the packet names inside the scopes.
- **PC-14:** when the role session runs in a different directory from the
  orchestrator, the dispatch states the context that is not available, instead of
  letting the role assume it.
- **PC-15:** packaged instructions state the same rule at the sender and receiver
  boundaries: senders include the locator and the scope; receivers report a missing
  required resource and stop.

**Method:** combined. Contextual review of the sender and receiver instructions, plus
a bounded fresh-session check in which a role resolves and uses the required CLI from
the packet alone, with no access to the orchestrator's conversation and no out-of-scope
read.

**Acceptance:** the reviewer finds the rule stated once, consumed at the boundaries
and free of contradictory operational text; the bounded check shows the role invoking
the named CLI and reporting a gap, not improvising, when a required resource is placed
outside its scope.

**Evidence:** cited instruction locations, the dispatch under test, the role's actual
response and any failure preserved.

**Limits:** this does not make a runtime export information the packet omits, does not
create a sandbox and does not prove universal compliance across runtimes.

## Verifiable invariants

- No allowance, exemption or debt classification supplies absent evidence.
- Producer, independent verifier and competent approver remain distinct responsibilities.
- A unit/family’s consumed ordinal never decreases through administrative identity changes.
- Required verification of the final authorized batch remains required.
- Accepted debt cannot substitute for an unmet current promise.
- Accumulation cannot recursively replenish correction opportunities.

These are documentary invariants, not a commitment to property-based tests.

## Acceptance-of-use recipe: bounded-round-trajectory-v1

Use actual candidate instructions in isolated agent sessions. This is a bounded methodological exercise, not a change to live product contracts.

**Contract layer**

The orchestrator prepares the scenario from this approved specification and its acceptance conditions before observing candidate behavior. An independent reviewer evaluates adequacy and later fidelity. Preserve scenario inputs, candidate revision and role inputs.

**Integration layer**

The implementer supplies candidate sources and regenerated consumers. Existing distribution/render checks run under their normal ownership. The reviewer contrasts the effective inputs with their canonical sources. Structural success alone is insufficient.

**Use layer**

The orchestrator conducts one bounded trajectory using a declared maximum of three:

1. Start a result-family assessment and corrective batch. Its closing check supplies evidence of an unresolved committed finding, opening the next round.
2. Resume through a changed dispatch identity with the same unit/family consumption. An identical delivery retry remains the same event.
3. Reach round three and complete its required verification. That check still identifies a committed breach and separately an optional, evidence-supported residue.
4. Observe the stop and adjudication: the breach remains blocked; the optional residue is recorded with its destination. Any proposed continuation requires the finite unmet-promise authorization described above, not a fresh round 1.
5. Give an independent receiving session only the ordinary records and candidate handoff; compare its reconstructed consumption and next action with the actual trace.
6. Ask that receiver to distinguish the corresponding draft spec+plan allowance and audit-correction allowance, using the same candidate rule.
7. Present the accumulation disposition, including a proposed late item and a proposed successor accumulation cycle. The response requires explicit amendment for the late item and rejects recursion.

The scenario may supply controlled findings; identify them as scenario evidence, not discoveries in the real product. Preserve actual responses, including failures. One trace may support several promises; no scenario quota is implied.

If candidate use cannot be observed with the available runtime, report the missing evidence and block that acceptance claim rather than substituting a written example.

## Acceptance criteria

- All PC-1–PC-10 receive the declared contextual assessment with recoverable evidence and no unresolved blocking finding.
- The bounded trajectory exhibits the specified consumption, stop, evidence-backed disposition and fresh-session recovery.
- Effective affected consumers do not direct incompatible conduct.
- Existing relevant distribution and regression checks have recorded outcomes and limitations under the current test evidence policy.
- Neither semantic success nor a complete-suite result is inferred from structural validation.

## deferred-hardening

- **Automatic enforcement and status projections:** deferred because the selected design is instructional. Promote only after observed procedural failures justify additional mechanics.
- **Free-text note parsing and counter repair:** deferred to avoid a second state mechanism and false confidence from prose parsing.
- **Retrospective normalization of closed units:** deferred; it is unnecessary for prospective operation and risks rewriting history.
- **Large-scale, cross-model compliance measurement:** deferred; this feature promises one bounded observed application, not a universal benchmark.
- **Resolving accumulated optional items:** outside this feature’s commitment; their later bounded contract determines their implementation and verification.

No deferral postpones any PC-1–PC-10 obligation.

## Out of scope

New roles, gates, policy settings, CLI behavior, automatic approvals, quantitative severity scoring, layout migration, installation and publication.

## Design rationale

Use one cross-family rule with three applications rather than independent definitions: the same reset and verification ambiguities recur across the loops. Separate allowances preserve the opportunity to review the eventual result after draft work.

Use instruction and ordinary-history semantics rather than structured CLI counters: mechanical enforcement was not selected, and existing transition identity is not a round counter. The explicit limitation is procedural enforcement.

Use one ordinary epic unit rather than a recursive cleanup phase: it retains normal approval and verification while making admitted scope finite.

**Open approval decisions:** adoption of this draft, its proposed maximum of three and the plan below. No additional owner agreement is inferred.

---
