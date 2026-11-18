# role-report — 019-005 bounded review cycles

**Result:** design recommendations only; no specification drafted or approved.

**Snapshot:** `c99b57b4eef2b4e73366df27a5a2b5a51495da3f`. Owner decisions below come from `docs/specs/019-005-bounded-review-cycles/discovery-notes.md:6–22`; recommendations are not additional consent.

## 1. Findings

The existing methodology already provides most of the required safeguards:

- Draft review covers the spec **and its plan**, binds their reviewed bytes, routes blockers to the architect, and requires focused re-review when corrections change the design (`stage-2-specification.md:49–83`).
- Result review already requires class-level fixes, evidence-backed blockers, focused closing re-review, and prevents optional improvements from prolonging closure (`stage-4-review.md:5–40`).
- POST-AUDIT preserves originals until substitutions have acceptable execution and sensitivity evidence. Missing evidence blocks substitution; it does not justify deleting protection (`re-entry.md:328–337`).
- Repeating without new information already triggers strategy review. Replanning preserves objective, dependencies and history (`re-entry.md:207–215`).

**Important tension:** draft guidance says focused re-review is “not a new full round” (`stage-2-specification.md:69–71`). The new definition must distinguish a *focused verification pass* from an *additional correction round*. Otherwise repeated corrections could remain indefinitely inside “round one.”

## 2. Recommended round definition

Use **one general definition with three concrete applications**, rather than three independent counting systems:

> A round consists of an assessment, disposition of its findings, the resulting correction batch when needed, and the applicable verification of those corrections.

A clean assessment closes its round without a correction. An unsuccessful or interrupted verification leaves the round unresolved; it does not reset it.

### Applications

- **Draft:** independent review of spec and plan → dispositions → architect corrections → required focused re-review. Spec and plan belong to the same round, not separate budgets.
- **Audit:** AUDIT findings/dispositions → approved test changes in POST-AUDIT where applicable → evidence and gate check. Corrections to deficient audit output or substitutions belong to this family; ordinary implementation RED→GREEN is not automatically an audit correction.
- **Result:** independent review → prioritization → fixes through the competent roles → executable checks and required contextual closing re-review.

### Latest-check findings

The closing check can establish that the correction succeeded **or** expose unresolved/new findings. In the latter case:

1. Record the check and its evidence as the outcome of the current round.
2. Any further correction batch consumes the **next** round.
3. At the limit, stop ordinary correction and adjudicate the remaining findings.

Thus a closing check is never permission for unlimited “finishing touches.” The final permitted correction still receives its required verification; the budget cannot remove that obligation.

Existing exemptions remain explicit exemptions, not executed checks. In particular, the mechanical-fix exception cannot waive corrected semantic verification (`stage-4-review.md:207–214`).

## 3. Budget and identity

**Recommendation requiring confirmation:** declare one unit-specific maximum, applied independently to each of the three families. Track consumption by **unit + family**, with spec and plan grouped together.

This avoids draft work consuming all permission to review the eventual result. However, the owner has not explicitly settled **three family allowances versus one shared unit-wide allowance**. Resolve this before drafting.

Prevent resets as follows:

- Packet IDs, execution IDs, transport routes and substage labels are provenance, not budget identities.
- Re-dispatch, suspension/resumption, a renamed stage, or a changed contract digest does not erase earlier consumption for the unit.
- An identical technical retry does not create a fresh correction opportunity. Without new information, apply the existing strategy-review trigger.
- A substantive replan records its predecessor, new evidence, changed scope or approach, remaining obligations and approval. Merely renaming the same work is not a replan.
- New evidence can justify reconsideration; it does **not automatically replenish** the budget.

## 4. Use existing records

### Declaration

Put the architect’s proposed limit and concise difficulty/risk justification in the existing unit specification. Include the initial proposal in the draft so draft review itself has a bound; the competent authority must adopt that provisional limit before the review loop begins.

The owner’s examples—two/three versus five/six—are guidance, not required values (`discovery-notes.md:8–13`). Justification should address actual uncertainty, coupling, correction difficulty and consequences of error, not merely attach a “high risk” label.

**Project configuration:** prefer project guidance in existing methodological planning material, with the unit spec carrying the actual applicable limit. Do not casually add a review setting to `cdad-policy.json`: its current top-level vocabulary is explicitly enumerated (`skills/cdad-cycle/scripts/cdad_packet.py:250`).

### Consumption

Reuse:

- Review/audit artifacts for findings and dispositions.
- `stage_history` for round identity, evidence references, consumed round and outcome.
- Existing `debt.md` where present for accepted residual items.
- Epic plan/decomposition and `epic_features` for the single accumulation unit.
- `epic_history` for the approved queue/plan decision.

Do not introduce a separate ledger or maintained counter file. Derive consumption from historical entries rather than keeping two independently editable totals.

### Minimal mechanical surface

Two alternatives are viable:

1. **Instruction-only:** record round summaries in existing transition notes and pinned artifacts. Lowest implementation cost, but enforcement remains procedural.
2. **Small additive extension:** structured round metadata on existing transitions, checked and summarized by the current CLI. Better protection against accidental resets without introducing another state machine.

**Recommendation:** choose the additive extension only if mechanical enforcement is an explicit promise. Do not parse free-text notes to enforce limits.

The current transition identity includes execution, stage, packet and evidence; notes are explicitly excluded (`cdad_packet.py:7539–7618`). Therefore its present idempotency is **not** already a round counter. Any structured extension must preserve historical identities and cover metadata in the identity of newly extended entries.

**VERIFY:** exact proposed field names, flags and validation hooks do not yet exist.

## 5. Decision at the limit

The orchestrator needs a short, evidence-backed disposition—not an automatic success or automatic failure.

For every pending finding, record:

- Provenance and affected obligation.
- Latest examined artifact/version and check.
- Concrete consequence and realistic exposure.
- Why it is optional, acceptable debt, blocking, or still unknown.
- Resolution criterion and destination.
- Who made the disposition and under what authority.

**Acceptable debt:** current promises remain accredited, evidence supports the residual classification, and the competent authority accepts the consequence.

**Replan/block:** a committed promise is unmet, required verification is absent, relevant impact remains unknown, or residual debt is unacceptable.

A reviewer’s blocker may be rejected with a supported reason; “budget exhausted” is not that reason. Changing a promise requires the existing contract-change and approval procedure.

This follows the pending classification already expressed in `documentary-contracts.md:§3`; it does not create a new permission to downgrade obligations.

## 6. One epic-end accumulation cycle

Represent it as **one normal, bounded unit in the epic plan**, not an extra recurring phase.

Each accumulated item references its originating unit, review/round and finding; records consequence and accepted disposition; and states its resolution criterion. Preserve those links when consolidating duplicates.

Before that unit opens:

- Consolidate the admitted items into a bounded contract.
- Declare its own architect-justified limit.
- Retain normal independent verification and approvals.

While it runs, new findings follow its ordinary bounded process. **Do not create another accumulation cycle recursively.** Residual optional work can remain explicitly accepted debt; unresolved obligations block closure or require an expressly approved scope/plan change.

Existing epic integration gates require all planned units done and none blocked (`skills/cdad-epic/SKILL.md:110–124`). The accumulation unit therefore belongs before those gates, not after the epic has been declared complete.

## 7. Instruction owners and verification

### Affected owners

- Canonical cross-family counting rule: recommend one focused reference, consumed rather than copied.
- `stage-2-specification.md`: limit declaration, provisional draft budget and focused re-review wording.
- `stage-3-tdd.md` and POST-AUDIT re-entry: audit-family application.
- `stage-4-review.md`: calibration, final-check findings and limit disposition.
- `re-entry.md`: durable registration and reconciliation with existing retry rules.
- Architect/orchestrator role sources and effective packet instructions.
- Spec template; epic skill and plan/closure templates.
- Normal and lightweight consumers, plus affected generated agents.

A rule only in the orchestrator’s reference is insufficient if the dispatched role cannot determine what it must report.

### Verification strategy

**Executable, if mechanics are promised:** demonstrate persistent consumption across re-dispatch/execution changes; correct family/unit separation; idempotent repeats; threshold behavior; invalid-data rejection without state changes; historical compatibility; and existing layout resolution. Group equivalent cases by observable promise, not scenario quotas.

**Independent contextual review:** assess whether the instructions let an agent distinguish final verification from another correction, recognize an unmet obligation, justify debt, and stop accumulation recursion. Structural presence or keyword checks cannot establish these semantic properties.

**Combined acceptance:** a bounded worked trajectory using actual candidate instructions and, where implemented, the real CLI. Include a final-check blocker at the limit and an acceptable optional residue. Expected evidence is the decision trail, pinned assessments, consumption history and truthful final disposition—not merely a green command.

## 8. Consequential questions still open

1. **Budget scope:** separate family allowances using the unit’s maximum, or one shared total?
2. **Project setting:** planning guidance only, or a machine-readable default? Is an explicit unit limit always required?
3. **Draft bootstrap:** who adopts the provisional limit, and may it change during review without erasing consumption?
4. **Replanning:** what approval can authorize further work after exhaustion, and how is predecessor consumption carried forward?
5. **Standalone feature:** without an epic, where does accepted residual work go?
6. **Accumulation membership:** can newly accepted items enter after its contract is approved, or must they follow explicit amendment?

These require orchestrator/owner decisions; none is assumed here.

## Evidence and limitations

- **Modified by this role:** none. No commit created.
- **Initial/final status:** both showed pre-existing modifications to `docs/.cdad-state.json` and `docs/epics/epic-019-discovery-dialogue/execution.md`.
- **Primary validation:** installed CLI resolved through `~/.cdad-install-manifest.json`; `validate-request` and `validate-packet` completed successfully. Installed `render --route C` produced identification matching the received declaration. Execution context is v2.
- **Intake deviation:** initially used the checkout CLI and fed a manually reproduced dispatch to `intake`. Its structural success is **not accredited as native received-message validation**. Subsequent installed-CLI file validation and manual comparison establish the Route C checks, not transport origin.
- Exact successful installed commands, with `P=.cdad/packets/019-005-bounded-review-cycles-architect-brainstorm-001` and product root as working directory:
  ```sh
  python3 ~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py validate-request --project-root <repo> --request "$P/REQUEST.json"
  python3 ~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py validate-packet --project-root <repo> --request "$P/REQUEST.json" --packet "$P/PACKET.md"
  python3 ~/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py render --project-root <repo> --request "$P/REQUEST.json" --route C
  ```
- Repository inspection used `read`, `rg`, `sed`, `nl`, and `git status --short`, `git diff --stat`, `git rev-parse HEAD`. Some guessed file paths and an unsupported `validate` help invocation failed; no equivalent permission workaround occurred.
- No tests or full suite run. This is evidence-grounded design analysis, not proof of implementation or observed agent compliance.