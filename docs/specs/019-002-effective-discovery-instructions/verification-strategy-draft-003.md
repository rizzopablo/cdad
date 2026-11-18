# Revised architect draft — UNAPPROVED

**Planning only.** This revision makes one bounded change to draft-002: the comprehension-reading reader and its orchestration in PC-5/PC-6 and T1. It adds no role, gate, field or validator. It authorizes neither implementation nor changes to the plan or state.

## 1. Discovery basis

The existing instructions preserve independent roles, but several consumers assume that every production task requires executable RED/GREEN:

- `skills/cdad-cycle/references/stage-3-tdd.md:21–40,136–156,318–328`.
- `skills/cdad-cycle/packets/roles/implementer.md:1`.
- `skills/cdad-cycle/packets/substages/implementer-green.md:1`.
- `skills/cdad-spec-and-test/SKILL.md:56–78`.

The documentary reference already distinguishes structural checks from semantic review (`documentary-contracts.md:133–175`). The epic execution record limits the owner’s earlier documentary decision to 019-001 (`docs/epics/epic-019-discovery-dialogue/execution.md`, “Owner decision”).

**Proposed design:** extend the existing specification, verification and review instructions, using existing contracts, assignments, reports and approval records. Prefer one property-based rule over separate documentary and executable methodologies, while retaining the verification obligations appropriate to each property.

This change is prospective. It does not rewrite 019-001’s accepted contract or retrospectively change acceptance criteria.

---

# 2. Epic-plan amendment DRAFT

**Target:** `docs/epics/epic-019-discovery-dialogue/plan.md`  
**Status:** Pending explicit applicable approval.

Preserve feature IDs and the existing decomposition heading/table anchors. Replace the decomposition table with:

```markdown
| Order | Feature | Independently reviewable result | Dependency |
|---|---|---|---|
| 1 | `019-001-discovery-dialogue-contract` | Accepted documentary operating design; retained without retrospective re-verification | Owner-approved epic plan |
| 2 | `019-003-contract-verification-strategy` | Activate verification strategy selected by contractual property, with explicit responsibilities, proof limits and approval rules across the normal and lightweight workflows | 019-001 accepted; this amendment approved |
| 3 | `019-002-effective-discovery-instructions` | Activate the accepted discovery-dialogue design; deliver its executable corrections and observed acceptance evidence using the approved verification strategy | 019-001 and 019-003 accepted |
```

Replace the paragraph immediately following the table with:

> 019-001 remains accepted. The additional unit establishes the verification strategy before 019-002 construction proceeds. 019-002 retains its discovery-dialogue activation, delivery correction, idle/done correction and observed-use obligations. It supplies a bounded application of the strategy and feedback about that application, not universal validation of the methodology.

### Add to “Cross-feature contract”

> Each specification proposes verification methods according to the properties promised, not the product’s file format. A single product may require deterministic checks, independent semantic review and observed execution for different promises.
>
> The architect proposes the strategy; the test-writer designs executable deterministic checks; the reviewer designs and evaluates semantic review, including any justified independent comprehension reading; the orchestrator coordinates the work and checks evidence coverage; the authorized owner approves the strategy with the contract. Producers cannot change acceptance criteria unilaterally.
>
> Strategy and acceptance criteria are fixed before construction. Verification details are concretized before relevant production without changing the approved commitment; changes follow the applicable approval procedure. Criteria are never fitted retrospectively to an observed outcome.

### Add epic acceptance criterion 8

> The normal and lightweight instructions identify the appropriate verification method, responsible role, expected evidence and proof limits for each committed promise. Acceptance distinguishes satisfied obligations from failed checks, missing evidence, contradictory evidence and inability to verify. No method automatically certifies properties outside its reach. Effective consumers preserve role independence and do not require conflicting verification routes.

### Add under “Plan changes”

> **Plan change — 2026-11-15, pending approval:** propose 019-003 before 019-002 following the owner’s request for verification by contractual property. The earlier documentary decision and accepted 019-001 evidence remain unchanged. Once approved, the new strategy governs subsequent construction within its declared scope. Publication and deployment remain excluded.

Also correct the stale “no feature has been started” sentence to reflect that 019-001 is accepted and 019-002 is open in discovery. Preserve the original approval history.

---

# 3. Additional-unit specification DRAFT

## 019-003 — Contract verification strategy

**Status:** Pending approval.

### Functional description and journey

An owner needs to know what evidence will justify accepting a promised result before production begins.

Starting from a proposed contract, the architect identifies properties requiring deterministic checks, semantic judgment or observed execution. Independent verification roles concretize that strategy. The owner approves the commitment, and the orchestrator later presents evidence against it without treating a green check or favorable reading as proof of everything.

**First useful result:** the owner can inspect an actionable verification strategy before approving production and later distinguish supported, unsupported and contradicted promises.

### Scope

Activate this strategy in the existing canonical instructions and affected consumers, covering:

- The normal five-stage cycle.
- The lightweight workflow.
- Prepared packets and legacy handoffs.
- Generated generic and domain-specialized consumers where they inherit changed instructions.

This unit does **not** implement 019-002’s dialogue changes, CLI corrections or observed acceptance exercise.

### Admitted sources and protected inputs

Use:

- The approved epic amendment and this unit’s approved specification.
- Existing role sources, packet sources, stage references, specification template and lightweight instructions at the identified baseline revision.
- Relevant existing tests, generator and distribution contracts.
- 019-001’s accepted operating design as dependency context.
- The epic execution record for authority and historical decisions.

The approved contract, acceptance inputs, independent review criteria and test verifiers remain outside the producer’s editable scope. Where an existing instruction becomes the product, identify its baseline revision separately from its proposed replacement.

Verification establishes the declared instructions’ fidelity, coherence and distribution. It does not establish universal agent compliance.

## Contract

### Evidence mapping applicable to PC-1–PC-9

The following allocation makes delivery explicit without introducing another schema or mandatory document. Record the mapping in the existing verification and review reports.

For every affected instruction surface, identify the applicable PCs, the examined version, its semantic review and its deterministic delivery evidence:

- **Canonical references, specification template and lightweight instructions:** semantic review of the actual candidate files; deterministic comparison establishing that the corresponding distributed copies contain those candidate bytes.
- **Role sources and generated consumers:** semantic review of the source and actual composed consumer instructions; deterministic generation/source-manifest checks and output comparisons establishing the affected generic and inherited domain-specialized outputs.
- **Prepared packets:** semantic review of the actual rendered instructions; deterministic source-to-render comparison and complete canonical packet validation.
- **Legacy handoffs:** semantic review of the applicable handoff instructions and their referenced requirements; deterministic distribution checks for those files and their required referenced inputs.
- **Isolated installed consumers:** compare installed artifacts with the verified candidate distribution and demonstrate that the affected entrypoints resolve their required inputs without relying on an undeclared checkout.

Reuse applicable existing controls. Inspected candidates include `tests/test_cdad_generate.py`, `tests/test_role_packet_render.py`, `tests/test_install_ownership.py` and `tests/test_004_002_t6_landing.py`. Their existence is not evidence that they cover every changed surface or that they passed: the test-writer’s audit selects the relevant protection and identifies any gaps.

PC-9 owns the cross-surface delivery obligation. The PC-specific strategies below explicitly depend on the corresponding PC-9 delivery evidence. A PC promising effective instructions cannot be accredited by semantic review alone, nor by a passing unrelated distribution check.

A surface declared unaffected needs a supported explanation; absence from a selected test is not such an explanation. These checks establish delivery and equality, not semantic sufficiency or actual agent compliance.

### Promise A — The owner can approve verification appropriate to the promise

**PC-1.** The specification instructions require each promise to identify:

- The property being verified and applicable numbered postconditions.
- The selected method or combination of methods.
- Responsible verifier, authorized inputs and expected evidence.
- Acceptance criterion and limits of what the method establishes.

Concise prose is sufficient; no new machine-readable schema is required.

**PC-2.** Method selection follows the property, not “documentation versus code.” The instructions permit different methods within one product and neither require automation merely because it is feasible nor exempt executable behavior because its surrounding product is documentary.

**Verification strategy:**

- Independent semantic review of the specification instructions, template, lightweight route and affected consuming instructions. The reviewer determines whether an owner can identify the necessary evidence and its limits; textual presence alone is insufficient.
- Deterministic delivery evidence through PC-9: candidate-to-distribution comparisons for references/template/lightweight files, source-to-generated-consumer checks, and rendered-packet checks wherever those consumers carry PC-1 or PC-2.

A compact explanatory example distinguishes:

- Distributed instruction bytes: deterministic comparison.
- Fidelity of those instructions to an approved decision: semantic review.
- An agent actually applying them: observed execution.

These are different claims, not interchangeable ways to certify the same thing.

### Promise B — Independent roles establish verification without producer control

**PC-3.** The instructions assign responsibility unambiguously:

- **Architect:** proposes the strategy in the specification.
- **Test-writer:** designs executable deterministic checks from the contract and authorized inputs, without implementation reads.
- **Reviewer:** designs and evaluates semantic verification independently of the producer.
- **Orchestrator:** coordinates assignments, protects acceptance inputs and checks coverage.
- **Authorized owner:** approves the strategy with the contract.

The producer cannot modify protected acceptance criteria or verifiers.

**PC-4.** Strategy is approved before construction; detailed instruments and acceptance inputs are fixed before relevant production begins. Concretization cannot change the approved promise, method sufficiency or acceptance criterion. Necessary changes stop the affected work and return through the applicable review and approval procedure.

**Verification strategy:**

- Independent semantic review of responsibility, approval timing and change handling in canonical instructions and actual affected role, packet, legacy and lightweight consumers.
- Deterministic delivery evidence through PC-9: role-source composition and generated-output comparisons, rendered-packet comparisons/validation, and distribution comparisons for referenced and legacy instructions.
- Existing scope and approval controls supply only their established mechanical evidence; they do not establish independence or adequate timing by themselves.

### Promise C — Comprehension evidence is useful without becoming an oracle

**PC-5.** Optional independent comprehension reading has an explicit handoff between the existing roles and a minimal-context auxiliary session:

1. Before relevant production begins, the **orchestrator dispatches an independent reviewer assignment** to determine whether comprehension reading is justified by a specific ambiguity risk and, if selected, to prepare the reading task and evaluation criteria from the approved contract and authorized baseline.
2. The reviewer returns that proposal read-only. The orchestrator preserves the selected task, criteria, source versions and selection rationale in the existing assignment/re-entry artifacts, versioned and outside the producer’s editable scope. Concretization remains within the approved commitment.
3. Before the exercise, the **orchestrator selects a minimal-context auxiliary session from the profiles the harness actually offers**. The reader is not a CDAD role, product reviewer or approval authority. It must not use the `cdad-reviewer` profile: loading adversarial-review instructions is incompatible with the intended minimal-context reading. A generic profile is not automatically suitable merely because it is shorter.
4. Before dispatching the reading task, the orchestrator records the selected profile’s actual text, the ambient instructions the session will load—including applicable user/project `AGENTS.md`—and its available tools and permissions. The record identifies the harness, recoverable versions of that context, and why the known context is acceptable for the bounded task. It also identifies relevant access and side-effect limits. Do not claim that a separate session guarantees file isolation or that a read-only assignment mechanically removes write capability.
5. **Only the orchestrator launches the reader; the reviewer never spawns it.** In the declared OpenCode/OpenChamber setup, the main session can launch first-level subagents, but a subagent cannot launch subagents. Other harness capabilities must be established rather than assumed. The reader receives the identified candidate instructions and necessary ordinary context, but not expected answers, evaluation keys or previous conclusions. Ambient instructions are part of this information-boundary assessment, not an invisible exception.
6. If the harness cannot provide a reader whose loaded context is known and acceptable, record the selected exercise as **BLOCKED / not performed**, with the reason. Never simulate the reader, invent its response or present the evaluating reviewer’s own reading as an independent exercise. A selected verification commitment remains unresolved under PC-7 until its blocker is resolved or the commitment is changed through the applicable approval procedure.
7. The reader explains intended decisions, relevant passages and uncertainties without executing the skill or approving the product. Before dispatch, the orchestrator accounts for profile-driven side effects. For example, the generic `general` profile described in the dispatch requires a project `logs/` file and carries no read-only restriction; it is not an acceptable default for an allegedly side-effect-free reading. Use it only if the actual harness configuration permits the required side effects to remain outside the product repository and the limitation is declared; otherwise select another suitable offered profile or report the exercise blocked. Auxiliary logs must not enter the project diff or be represented as product evidence.
8. The orchestrator preserves the actual delivered inputs, declared loaded context and complete response, then supplies them with the protected pre-production task, criteria and their versions to the **evaluating independent reviewer**. Any unexpected context, access or side effect remains visible; it is not silently discarded to manufacture an independent result. The evaluation cannot rely on a producer’s summary or on criteria reconstructed from memory.
9. The evaluating reviewer applies those criteria and records findings and the exercise’s declared limits. This may recover the earlier reviewer assignment’s protected output; it does not require the same session to remain alive.

If comprehension reading was **not selected**, preserve the reason and record that no comprehension exercise was performed. Mandatory semantic review and applicable delivery checks still apply.

If a selected exercise’s task or criteria were **not fixed before relevant production**, stop the affected work and report the missing precondition. A retrospective exercise may be reported only as diagnostic evidence, not as satisfying the selected pre-production verification commitment. Resolve the affected commitment through the applicable approval procedure before continuing; neither a favorable response nor retroactively dated criteria repairs the omission.

**PC-6.** Comprehension evidence does not prove operational behavior. A reader error is a signal to investigate, not by itself proof of an instruction defect. Reports retain actual inputs, versions, loaded profile and ambient context, tools/permissions, responses and evaluations; they state what independence and minimal context were actually achieved. They do not select only favorable attempts, claim a general comprehension benchmark or present session separation as file isolation. A blocked or unperformed exercise supplies no comprehension result. Auxiliary side effects are not product changes or evidence of product correctness.

**Verification strategy:**

- Independent semantic review of the procedure, its selection/non-selection and blocked handling, pre-production handoff, protection and recovery of criteria, and actual information boundaries.
- Deterministic delivery evidence through PC-9 for the review procedure, orchestrator consequences, affected role/packet instructions and legacy references.
- Where an exercise is selected, inspect its actual assignment, preserved versions, pre-exercise context declaration, response and evaluation against PC-5–PC-6, or its explicit blocked/not-performed record. Check that auxiliary side effects did not enter the project diff or product evidence. This unit does not mandate an exercise as a universal ritual.

### Promise D — Acceptance reflects the evidence actually obtained

**PC-7.** Verification reports distinguish:

- Evidence supporting the specified property within stated limits.
- A failed check or unmet criterion.
- Missing required evidence.
- Contradictory evidence.
- Inability to verify, including environment or method limitations.

Failures and contradictions remain visible. Missing evidence or inability to verify a committed promise blocks its accreditation; declaring a limitation does not turn it into success.

**PC-8.** Existing gates check the approved strategy’s coverage and applicable evidence. Deterministic checks cannot substitute for semantic judgment; semantic review cannot substitute for promised runtime observations; observed success cannot establish unexamined scenarios or versions.

Only promise-relevant checks are required. No scenario quota, coverage target or automatic acceptance follows from choosing a method.

**Verification strategy:**

- Independent semantic review of reporting, re-entry and closure instructions, including the affected normal and lightweight consumers. Trace commitments to the evidence capable of establishing them rather than counting tests or completed sections.
- Deterministic delivery evidence through PC-9 for those references and lightweight files, generated role instructions and rendered packets where applicable.
- Neither byte equality nor structural validation establishes that a report’s semantic conclusions are warranted.

### Promise E — Effective instructions agree, prospectively

**PC-9.** Canonical references, role sources, affected packet instructions, legacy handoffs and generated consumers provide compatible routes:

- Executable pending behavior retains independent RED/GREEN verification where applicable.
- Approved semantic-only production does not require a fabricated failing test.
- Mixed commitments retain each applicable verification obligation.
- Non-executed RED/GREEN steps are not reported as executed or green.
- The lightweight route does not claim normal-cycle gates it did not perform.

For each affected surface carrying PC-1–PC-9, the evidence mapping identifies both its semantic examination and its applicable deterministic delivery result. Semantic success cannot conceal stale or missing distribution.

**PC-10.** The change preserves 019-001’s acceptance and historical evidence. It establishes a prospective rule, leaves 019-002’s existing obligations intact and requires 019-002’s criteria to be fixed before its construction and observed exercise.

**Verification strategy:**

- **Mandatory semantic review:** examine actual effective instructions against this contract and the historical decision, including compatibility across normal, lightweight, packet, legacy and generated routes.
- **Deterministic distribution verification:** use the surface-specific mapping above, relevant generation/rendering controls and isolated-distribution comparisons selected by the test-writer’s audit. Results must identify the candidate version and covered surfaces.
- **PC-10:** independently compare the amendment and candidate instructions with the accepted historical inputs. Any effective instruction carrying the prospective rule also requires its corresponding PC-9 delivery evidence. Historical records are not regenerated or retrospectively reverified under new criteria.
- **Observed application:** remains with 019-002. Its results cannot be retrofitted into this unit’s acceptance criteria.

## Verifiable invariants

- No producer controls its protected acceptance oracle.
- No committed promise is marked satisfied solely by evidence incapable of establishing its property.
- Test-writer implementation-read isolation and independent review remain intact.
- Historical failed or missing evidence is never rewritten into success.

These are review obligations here, not an automatic requirement for randomized property tests.

## Acceptance criteria

Accept only when:

1. PC-1 through PC-10 have recoverable evidence and an explicit result.
2. Every affected effective surface is traceable to its applicable PCs, semantic examination and deterministic delivery evidence.
3. The independent reviewer finds no unresolved blocking contradiction or unsupported commitment.
4. Applicable deterministic controls have attributable results and recorded limits.
5. Effective consumers agree; untouched obligations remain preserved.
6. The authorized approver explicitly accepts the result.

Neither review nor passing checks constitutes approval.

## deferred-hardening

- **Universal comprehension scoring or benchmarks:** excluded because this unit establishes no calibrated general oracle.
- **Automated semantic interpretation:** excluded because deterministic textual checks cannot establish the committed semantic judgments.
- **Universal runtime compliance:** not promised; 019-002 supplies bounded observations.
- **New schema or mechanical enforcement service:** not required by the examined needs. Reconsider only if an approved commitment cannot be carried by existing artifacts and procedures.

No deferral postpones PC-1 through PC-10.

---

# 4. Minimal implementation plan DRAFT

## T1 — Coherent activation of the verification strategy

**Consumes:** approved specification, protected verification instruments and authorized baseline.

**Produces:** compatible canonical instructions and effective consumers satisfying Promises A–E.

### Canonical allocation

- `stage-2-specification.md` and the specification template: strategy proposal, approval and required specification content.
- `stage-3-tdd.md`: method applicability, evidence sufficiency and construction/closure routing; preserve the existing test-evidence policy’s ownership.
- `stage-4-review.md`: semantic verification and optional comprehension-reading procedure, including the pre-production assignment, orchestrator-launched auxiliary reader, context declaration, blocked handling and later evaluation handoff.
- `documentary-contracts.md`: align conditional documentary obligations by reference without introducing a competing general rule.
- Role sources, packet blocks/substages, `handoff-prompts.md` and `re-entry.md`: role-specific consequences and pointers.
- Lightweight instructions: remove unconditional “tests pass, therefore done” implications.
- Generated agents: regenerate through the existing generator, never edit by hand.

### Before production

- The orchestrator dispatches the independent reviewer to concretize semantic criteria and determine whether a bounded comprehension exercise is selected.
- If selected, the reviewer returns its task and criteria before relevant production; the orchestrator preserves their versions outside producer control and later supplies them with the reader’s actual inputs, declared loaded context and response to the evaluating reviewer. The reviewer designs and evaluates the exercise but never launches the reader.
- Before the exercise, the orchestrator selects a minimal-context auxiliary session from profiles actually offered by the harness, excluding `cdad-reviewer`. It records the actual profile text, ambient instructions including user/project `AGENTS.md`, tools/permissions, recoverable versions and why that context is acceptable. A short generic profile is not presumed clean or read-only. Account for required logs and other side effects before dispatch; they must remain outside the project diff and must not be presented as product evidence.
- Only the orchestrator launches the reader. Do not depend on nested subagent dispatch: it is unavailable in the declared OpenCode/OpenChamber setup. Do not infer file isolation from a separate session. Where the harness cannot provide known, acceptable loaded context or cannot keep required auxiliary side effects outside the product repository, record the selected exercise **BLOCKED / not performed** under PC-5–PC-7, without simulation or substitution by the reviewer’s own reading.
- If not selected, preserve the reason. If selected but not fixed in time, apply PC-5’s stop-and-return procedure; do not invent retrospective compliance.
- The test-writer audits relevant deterministic protection and identifies the controls or changes needed for each affected delivery surface.
- The orchestrator materializes and protects those inputs, retaining the PC-to-surface mapping in existing reports.

Existing tests encoding superseded wording require deliberate dispositions; they are not deleted merely because they fail after the amendment.

### Verification and review

Run the selected deterministic controls and retain their outputs. Independently review the actual candidate instructions and effective consumers. Match both evidence families to every affected surface under PC-9; reuse evidence across PCs where it genuinely establishes the same delivery property.

For a selected comprehension exercise, retain its pre-exercise context declaration and actual result or explicit blocked/not-performed record. The evaluating reviewer uses the preserved task and criteria, reports actual context and access limits, and checks that auxiliary side effects did not become product changes or product evidence. This reading neither replaces semantic review nor acquires approval authority.

**Executable assessment:** no CLI or schema change is presently necessary. Existing transition registration can cite artifacts without recording a RED/GREEN outcome. Semantic results can remain in role reports and gate evidence; do not invent new `postconditions_status` values. If a concrete consumer prevents the approved route, report its reproducer and return for a bounded contract decision before adding executable scope.

**Self-application approval:** approval of this unit must explicitly authorize its stated verification strategy. Until then, this draft cannot use its proposed rule as permission to bypass current obligations.

---

# 5. Sequencing and pinned-input reconciliation DRAFT

## Inspected state

At the examined revision **retained from draft-002, not refreshed by this bounded revision**:

- 019-002 is active in `discovery`.
- The selected packet is `019-002-effective-discovery-instructions-architect-draft-002`, recorded as `prepared`.
- The execution context is schema v2.
- Continuity head sequence 5 belongs to this packet, attempt 1.
- Two earlier dispatch records exist; no durable receipt for this selected packet was present when inspected.

These are durable-record observations, not proof that this consultation was never transported. Re-entry must reconcile its actual delivery before any suspension decision.

## Exact current pin inventory and amendment impact

The relevant execution is `exec-019-002-effective-discovery-instructions-001`.

1. **Frozen selected contract:**  
   `.cdad/packets/019-002-effective-discovery-instructions-architect-draft-002/UNIT-CONTRACT.md`  
   SHA-256: `4c92d38e5a7953937daee4c781153e5ad7e4ec2945917129cbc0dd43310dff25`.

   The request and active-packet binding pin this projection—not the live epic-plan bytes. Its origin records the old plan SHA-256 as provenance. Do not update that origin or replace its digest after amending the plan.

2. **Live plan:**  
   `docs/epics/epic-019-discovery-dialogue/plan.md`  
   Current SHA-256: `a408980196c01d1f7ecf7f558fd8f81fa2fb3c781140dc9af6d98ec8fb5e98dc`.

   The amendment changes the active unit’s row/dependency and shared sections: Purpose, decomposition prose, Cross-feature contract and Epic acceptance criteria. Those changes require an `impact` decision; this is not merely adding an independent future row. The proposed history note belongs under the recognized “Plan changes” heading.

3. **Execution context:**  
   `.cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json`  
   SHA-256: `0372eeec07ab6e0683e76b786394cb4c51d781ad4834b82f370c916b8cbee315`.

   It binds execution identity, authority and accepted policy. It contains no direct epic-plan content pin. The proposed plan-only amendment does not require rewriting this file.

4. **Policy:**  
   `docs/cdad-policy.json`  
   SHA-256: `f508ab1eec67ce4575d0757bc8f9dde35113fff795b7d373bb456b1783ff2711`.

   Unaffected by the amendment. Do not invoke policy reconciliation for a plan change.

5. **Current continuity reference:**  
   `docs/epics/epic-019-discovery-dialogue/execution.md`, class `contract`  
   SHA-256: `91a7de2a0a54ca8940f0062c80dc2d943ed61a09b9246f30433014523d773512`.

   This is the current head’s sole reference. The head declares no `evidence` entries and no direct plan reference. The proposed amendment leaves this authority file unchanged, so this reference need not be replaced.

6. **Suspension snapshots:**  
   `_resume_digest_checks` records existing execution context, selected request/packet/contract, policy, any selected durable receipt and `vigente` continuity evidence. No suspension record exists yet.

   The selected request’s current SHA-256 is `178562c627d007e1de8fd37a9e5a0f86adf1a5a2313f970003efcd598ed5ab2e`; its packet SHA-256 is `941b3c117a227cb1c0f347f215c3d1aafc665758e7cca77e9b9195e345312f2b`. Preserve these frozen files.

The actual inventory must be refreshed after this consultation and its second review are received. Re-entry may add references, evidence or a receipt.

**Implementation basis:** `skills/cdad-cycle/scripts/cdad_packet.py:791–905,907–1040,1075–1131,1140–1215`; projection/classification at `:5987–6126,6187–6341,6442–6479`. The contractual reconciliation mechanism is `docs/specs/005-013-unit-contract/spec.md` §2.4–§2.8.

## Supported sequence

1. **Finish this consultation’s re-entry and second independent review.** Preserve actual transport/result evidence. Never withdraw a used packet by falsely treating it as undispatched.
2. Obtain applicable explicit approval for the amendment and record it. Preserve 019-001’s accepted contract and historical evidence.
3. Before materialization, refresh the pin inventory. For the inspected state, preserve the frozen projection, request, packet, execution context, policy and authority reference.
4. Materialize the approved amendment and synchronize `epic_features` through the existing epic-planning procedure, preserving IDs, statuses and history. The orchestrator remains the sole state writer (`skills/cdad-epic/references/epic-planning.md:130–152`).
5. Invoke the existing consequence operation:
   ```sh
   python3 scripts/cdad_packet.py validate-unit-contract --project-root .
   ```
   Examine its actual result. For `impact`, retain its durable impact record and record the orchestrator’s reconciliation decision in `stage_history.note`, citing the approved amendment and its effect on 019-002. Do not rewrite the received projection. `impeded` requires resolving its stated authority problem, not changing a digest.
6. At the verified safe boundary:
   ```sh
   python3 scripts/cdad_packet.py suspend-unit --project-root . \
     --feature 019-002-effective-discovery-instructions \
     --reason "Approved 019-003 verification strategy must precede 019-002 construction"
   ```
7. Open the registered eligible unit:
   ```sh
   python3 scripts/cdad_packet.py open-unit --project-root . \
     --feature 019-003-contract-verification-strategy
   ```
8. Complete 019-003 under its explicitly approved contract and strategy. Do not modify 019-002’s saved resumption inputs while it is suspended.
9. From coherent rest:
   ```sh
   python3 scripts/cdad_packet.py resume-unit --project-root . \
     --feature 019-002-effective-discovery-instructions
   ```
10. Reassess 019-002’s next assignment and prepare fresh packets. A new architect generation obtains the amended projection through existing `prepare`; the earlier projection remains historical. Resumption is neither specification approval nor permission to dispatch an obsolete assignment.

**Stop on rejection.** Suspension verifies frozen contract pins, current `vigente` evidence, continuity and unresolved effects; resumption compares saved digests and validates the restored binding. Do not clear bindings, edit `resume_checks`, rewrite saved contracts or weaken reference classes.

If refreshed inputs introduce an affected pin, reconcile it **before suspension** through its existing owning procedure. A live-plan `impact` decision does not authorize replacing a frozen digest. Where no existing procedure permits the needed substitution, stop and return the specific blocker for an authorized scope/routing decision.

---

# 6. Role evidence and limits

- **Route C:** the named request and published packet validated successfully; the canonical Route C identification matched the received identification.
- **Execution context:** schema v2.
- **Complete packet comparison:** ordinary canonical render equaled all published `PACKET.md` bytes: **8,108 bytes**, SHA-256 `74cf19f6bff92bd18f65f5217cf6f5a35b4f08f5c728700dd0a252531f40c01b`.
- **Contract digest:** `4c92d38e5a7953937daee4c781153e5ad7e4ec2945917129cbc0dd43310dff25`, matching the dispatch and validated request.
- **Measurement:** Python 3.13.5; renderer stdout bytes compared directly with `Path.read_bytes()`.
- **Examined HEAD:** `09f24968c1acef009651112bd290960e73e7206f`.

### Sources for this bounded revision

- `verification-strategy-draft-002.md`, particularly Promise C and T1; SHA-256 `b3a449ba935764b833adad14cce26607997b0a5a77d1bf7085497acfec9dcddb`.
- `verification-strategy-review-002.md`, particularly the comprehension-reading finding and pin-refresh limitation; SHA-256 `f46ca732ee3db62cc6bc6b806a486b07da7d65ab20527961ce4e707c9fca0d63`.
- The validated draft-003 packet’s objective for the supplied harness/profile observations. These were admitted dispatch facts, not independently remeasured profile sizes or a runtime capability test by this role.
- The packet’s frozen unit contract and the canonical `design-principles.md` and `documentary-contracts.md` references.

The design selects by actual loaded context rather than assuming that either a CDAD reviewer or a short generic profile supplies an uncontaminated reading. It introduces no new reader profile or role.

### Exact validation commands and results

Executed from `<repo>`:

```sh
python3 scripts/cdad_packet.py validate-request --project-root . --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root . --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/REQUEST.json --packet .cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/PACKET.md

python3 scripts/cdad_packet.py render --project-root . --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/REQUEST.json --route C
```

Request and packet validation succeeded without diagnostics. The Route C render reproduced the received identification.

The complete-byte comparison was executed as:

```sh
python3 - <<'PY'
import json,subprocess,hashlib
from pathlib import Path
r=Path('.cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/REQUEST.json')
j=json.loads(r.read_bytes()); e=json.loads(Path(j['execution_context']).read_bytes())
print('execution schema_version:',e.get('schema_version'))
p=subprocess.run(['python3','scripts/cdad_packet.py','render','--project-root','.','--request',str(r)],capture_output=True,check=True).stdout
b=(r.parent/'PACKET.md').read_bytes()
print('complete canonical render byte equality:',p==b,'bytes:',len(b))
assert p==b
print('contract sha256:',hashlib.sha256(Path(j['contract']['path']).read_bytes()).hexdigest())
PY
```

Output:

```text
execution schema_version: 2
complete canonical render byte equality: True bytes: 8108
contract sha256: 4c92d38e5a7953937daee4c781153e5ad7e4ec2945917129cbc0dd43310dff25
```

Repository and source measurements were executed as:

```sh
python3 - <<'PY'
import hashlib,platform,subprocess
from pathlib import Path
print('Python:',platform.python_version())
print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
print('git status --short:')
print(subprocess.check_output(['git','status','--short'],text=True),end='')
for f in ['.cdad/packets/019-002-effective-discovery-instructions-architect-draft-003/PACKET.md','docs/specs/019-002-effective-discovery-instructions/verification-strategy-draft-002.md','docs/specs/019-002-effective-discovery-instructions/verification-strategy-review-002.md','docs/.cdad-state.json']:
 b=Path(f).read_bytes(); print(f,len(b),'bytes',hashlib.sha256(b).hexdigest())
print('git diff --stat:')
print(subprocess.check_output(['git','diff','--stat'],text=True),end='')
PY
```

The repository observation showed:

```text
Python: 3.13.5
HEAD: 09f24968c1acef009651112bd290960e73e7206f
git status --short:
 M docs/.cdad-state.json
```

The state file measured 2,191,038 bytes, SHA-256 `55844129bce9afeccb9906137ca328fda4b5a000abfda11bbdab740e9a9e5246`. The diff summary showed only:

```text
 docs/.cdad-state.json | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
```

CLI discovery also used `--help`, `validate-request --help`, `validate-packet --help` and `render --help`. An initial `python3 scripts/cdad_packet.py validate --help` failed because `validate` is not a supported subcommand; the supported validation commands above subsequently succeeded.

- **Modified files by this role:** none. The observed state-file modification was external to this role’s read-only work.
- **Commit created:** none.
- **Tests/full suite:** not run; this was a read-only draft revision.
- **Reader exercise:** not performed or simulated.
- **Limits:** section 5 retains draft-002’s historical inspection, not current operational pins. This revision does not establish runtime reader suitability, successful suspension/resumption, complete consumer coverage or operational compliance. The complete draft remains **unapproved**, ready for focused independent re-review.