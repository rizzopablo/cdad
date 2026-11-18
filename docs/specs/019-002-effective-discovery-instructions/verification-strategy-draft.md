# Architect report — unapproved drafts

**Planning only.** No product, plan or state changes made. No approval or implementation authority is claimed.

## 1. Discovery findings

The current methodology already selects tests by observable promise and preserves independent roles. The gap is that several consumers still assume every promise must pass through executable RED/GREEN:

- `stage-3-tdd.md:21–40,136–156,318–328` defines behavioral verification and an unconditional RED/GREEN-oriented route.
- `packets/roles/implementer.md:1` and `substages/implementer-green.md:1` require current failing tests.
- `cdad-spec-and-test/SKILL.md:56–78` treats passing tests as sufficient to finish.
- `documentary-contracts.md:133–145,151–175` already distinguishes independent semantic review from structural control, but needs alignment with property-based method selection.
- `execution.md:16–28` records the owner’s narrower documentary decision for 019-001. Its acceptance remains historical evidence, not a general exemption to extend by analogy.

**Recommended design:** extend the existing specification, verification and review references; use existing contracts, role reports and approval records. No new schema, validator, gate, role or reader agent is justified by the requirements examined.

This is a prospective methodological change. It must not rewrite 019-001’s accepted contract or retrospectively change acceptance criteria.

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
> Strategy and acceptance criteria are fixed before construction. Verification details are concretized before production without changing the approved commitment; changes follow the applicable approval procedure. Criteria are never fitted retrospectively to an observed outcome.

### Add epic acceptance criterion 8

> The normal and lightweight instructions identify the appropriate verification method, responsible role, expected evidence and proof limits for each committed promise. Acceptance distinguishes satisfied obligations from failed checks, missing evidence, contradictory evidence and inability to verify. No method automatically certifies properties outside its reach. Effective consumers preserve role independence and do not require conflicting verification routes.

### Add a prospective history note

> **Plan change — 2026-11-15, pending approval:** propose 019-003 before 019-002 following the owner’s request for verification by contractual property. The earlier documentary decision and accepted 019-001 evidence remain unchanged. Once approved, the new strategy governs subsequent construction within its declared scope. Publication and deployment remain excluded.

Also correct the stale “no feature has been started” sentence to reflect that 019-001 is accepted and 019-002 is open in discovery. Do not erase the original approval history.

---

# 3. Additional-unit discovery/spec DRAFT

## 019-003 — Contract verification strategy

**Status:** Pending approval.

### Functional description and journey

An owner needs to know what evidence will justify accepting a promised result before its production begins.

Starting from a proposed contract, the architect identifies which properties need deterministic checks, semantic judgment or observed execution. The independent verification roles concretize that strategy. The owner approves the commitment, and the orchestrator later presents evidence against it without treating a green check or favorable reading as proof of everything.

**First useful result:** the owner can inspect an actionable, approved verification strategy and later see which promises are supported, unsupported or contradicted.

### Scope

Activate this strategy in the existing canonical instructions and their affected consumers, covering:

- The normal five-stage cycle.
- The lightweight workflow.
- Prepared packets and legacy handoffs.
- Generated generic and domain-specialized consumers where they inherit changed instructions.

This unit does **not** implement 019-002’s dialogue changes, CLI corrections or observed acceptance exercise.

### Admitted sources and protected inputs

Use:

- The approved epic amendment and this unit’s approved specification.
- Existing role sources, packet sources, stage references, spec template and lightweight instructions at the examined revision.
- Relevant existing tests, generator and distribution contracts.
- 019-001’s accepted operating design as dependency context.
- The epic execution record for authority and historical decisions.

The approved contract, acceptance inputs, independent review criteria and test verifiers remain outside the producer’s editable scope. Where an existing instruction becomes the product, identify its baseline revision separately from its proposed replacement.

Verification establishes the declared instructions’ fidelity, coherence and distribution. It does not establish universal agent compliance.

## Contract

### Promise A — The owner can approve verification appropriate to the promise

**PC-1.** The specification instructions require each promise to identify:

- The property being verified and applicable numbered postconditions.
- The selected method or combination of methods.
- Responsible verifier, authorized inputs and expected evidence.
- Acceptance criterion and limits of what the method establishes.

The commitment may use concise prose; no new machine-readable schema is required.

**PC-2.** Method selection follows the property, not “documentation versus code.” The instructions permit different methods within one product and neither require automation merely because it is feasible nor exempt executable behavior because its surrounding product is documentary.

**Verification strategy:** independent semantic review against the approved contract. The reviewer checks whether an owner can determine the evidence required and its limits. Textual presence alone is insufficient.

A compact explanatory example should distinguish:

- Distributed instruction bytes: deterministic comparison.
- Fidelity of those instructions to an approved decision: semantic review.
- An agent actually applying them: observed execution.

These are different claims, not three interchangeable ways to certify the same thing.

### Promise B — Independent roles establish verification without producer control

**PC-3.** The instructions assign responsibility unambiguously:

- **Architect:** proposes strategy in the specification.
- **Test-writer:** designs executable deterministic checks from the contract and authorized inputs, without implementation reads.
- **Reviewer:** designs and evaluates semantic verification, independently of the producer.
- **Orchestrator:** coordinates assignments, protects acceptance inputs and checks coverage.
- **Authorized owner:** approves the strategy with the contract.

The producer cannot modify protected acceptance criteria or verifiers.

**PC-4.** Strategy is approved before construction; detailed instruments and acceptance inputs are fixed before the relevant production begins. Concretization cannot change the approved promise, method sufficiency or acceptance criterion. Necessary changes stop the affected work and return through the applicable review and approval procedure.

**Verification strategy:** independent semantic review of role instructions, approval timing and change handling, including packet and legacy consumers. Existing scope/approval checks provide only their established mechanical evidence.

### Promise C — Comprehension evidence is useful without becoming an oracle

**PC-5.** Optional independent comprehension reading has a bounded procedure:

1. The reviewer determines its relevance and prepares the reading task and evaluation criteria before production.
2. The orchestrator dispatches a separate reader session; the reviewer does not spawn a subagent.
3. The reader receives the identified instructions and necessary ordinary context, but not expected answers, evaluation keys or conclusions.
4. The reader explains intended decisions, relevant passages and uncertainties without executing the skill.
5. The reviewer compares that response with the protected criteria and records findings and limits.

The reader task creates neither a new CDAD role nor an approval authority.

**PC-6.** The procedure states that comprehension evidence does not prove operational behavior. A reader error is a signal to investigate, not by itself proof of an instruction defect. Reports retain the actual inputs, versions, response and evaluation; they do not select only favorable attempts or claim a general comprehension benchmark.

**Verification strategy:** independent semantic review of the procedure and its information boundaries. A reader exercise is supporting evidence only when selected for a specific ambiguity risk; this unit does not mandate one as a universal ritual.

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

**Verification strategy:** independent semantic review of reporting and closure instructions. The reviewer traces each committed promise to the evidence required by its method, rather than counting tests or completed sections.

### Promise E — Effective instructions agree, prospectively

**PC-9.** Canonical references, role sources, affected packet instructions, legacy handoffs and generated consumers provide compatible routes:

- Executable pending behavior retains independent RED/GREEN verification where applicable.
- Approved semantic-only production does not require a fabricated failing test.
- Mixed commitments retain each applicable verification obligation.
- Non-executed RED/GREEN steps are not reported as executed or green.
- The lightweight route does not claim normal-cycle gates it did not perform.

**PC-10.** The change preserves 019-001’s acceptance and historical evidence. It establishes a prospective rule, leaves 019-002’s existing obligations intact and requires 019-002’s criteria to be fixed before its construction and observed exercise.

**Verification strategy:**

- **Mandatory semantic review:** compare the actual effective instructions with this contract and the historical decision.
- **Deterministic distribution verification:** reuse relevant generation, rendered-packet and isolated-distribution controls selected by the test-writer’s audit. These establish delivery/equality properties, not semantic sufficiency.
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
2. The independent reviewer finds no unresolved blocking contradiction or unsupported commitment.
3. Applicable deterministic controls have attributable results and recorded limits.
4. Effective consumers agree; untouched obligations remain preserved.
5. The authorized approver explicitly accepts the result.

Neither review nor passing checks constitutes approval.

## deferred-hardening

- **Universal comprehension scoring or benchmarks:** excluded because this unit establishes no calibrated general oracle.
- **Automated semantic interpretation:** excluded because deterministic textual checks cannot establish the committed semantic judgments.
- **Universal runtime compliance:** not promised; 019-002 supplies bounded observations.
- **New schema or mechanical enforcement service:** not required by the examined needs. Reconsider only if an approved commitment cannot be carried by existing artifacts and procedures.

No deferral postpones PC-1 through PC-10.

## Minimal implementation plan DRAFT

### T1 — Coherent activation of the verification strategy

**Consumes:** approved specification, protected verification instruments and authorized baseline.

**Produces:** compatible canonical instructions and effective consumers satisfying Promises A–E.

**Canonical allocation:**

- `stage-2-specification.md` and the spec template: strategy proposal, approval and required specification content.
- `stage-3-tdd.md`: method applicability, evidence sufficiency and construction/closure routing; preserve the existing test-evidence policy’s ownership.
- `stage-4-review.md`: semantic verification and optional comprehension-reading procedure.
- `documentary-contracts.md`: align conditional documentary obligations by reference without introducing a competing general rule.
- Role sources, packet blocks/substages, `handoff-prompts.md` and `re-entry.md`: role-specific operational consequences and pointers.
- Lightweight instructions: remove unconditional “tests pass, therefore done” implications.
- Generated agents: regenerate through the existing generator, never edit by hand.

**Before production:**

- Independent reviewer concretizes semantic criteria from the approved contract.
- Test-writer audits relevant existing deterministic protection and proposes necessary changes.
- Orchestrator materializes and protects those inputs.

Existing tests that encode superseded wording need deliberate dispositions; they are not deleted merely because they fail after the amendment.

**Executable assessment:** no CLI or schema change is presently necessary. Existing transition registration can cite artifacts without recording a RED/GREEN outcome. Semantic results can remain in role reports and gate evidence; do not invent new `postconditions_status` values. If a concrete consumer prevents the approved route, report the reproducer and return for a bounded contract decision before adding executable scope.

**Self-application approval:** approval of this unit must explicitly authorize its stated verification strategy. Until then, this draft cannot use the rule it proposes as permission to bypass current obligations.

---

# 4. Safe sequencing recommendation

The inspected state has 019-002 active in `discovery`, with this architect packet `prepared`; its execution dispatch directory is absent. That describes durable records, not proof that no consultation occurred.

1. **Complete this consultation’s re-entry first.** Preserve the report and reconcile its actual transport/result evidence. Do not withdraw a packet used for this consultation by falsely treating it as never dispatched.
2. Obtain explicit applicable approval for the epic amendment. Materialize approved changes and synchronize `epic_features` through the existing epic-planning procedure, preserving statuses, history and IDs. This is documented synchronization—not manual clearing of active bindings.
3. Reconcile the changed 019-002 unit projection and any affected continuity evidence. Keep frozen packets and their contracts unchanged.
4. At the verified safe boundary, the orchestrator invokes:
   ```sh
   python3 scripts/cdad_packet.py suspend-unit --project-root . \
     --feature 019-002-effective-discovery-instructions \
     --reason "Approved 019-003 verification strategy must precede 019-002 construction"
   ```
5. Open the newly registered eligible unit:
   ```sh
   python3 scripts/cdad_packet.py open-unit --project-root . \
     --feature 019-003-contract-verification-strategy
   ```
6. Complete 019-003 under its approved contract.
7. From coherent rest, explicitly resume:
   ```sh
   python3 scripts/cdad_packet.py resume-unit --project-root . \
     --feature 019-002-effective-discovery-instructions
   ```
8. Reassess 019-002’s next assignment and prepare fresh packets against the approved strategy. Resumption is not approval of its specification or permission to dispatch an obsolete assignment.

The suspension command checks unresolved dispatch/result effects and pinned inputs; resumption checks preserved references. If either rejects, stop and reconcile through the applicable existing procedure—never edit saved checks, clear bindings manually or relabel the unit.

Basis: `cdad_packet.py:791–837,907–1040,1075–1131,7293–7359`; epic-plan synchronization: `epic-planning.md:130–152`.

## Evidence and limits

- Route C request and packet validation succeeded. Identification matched the canonical Route C render.
- Complete `PACKET.md` bytes matched ordinary canonical rendering: **8,764 bytes**, SHA-256 `f5bbf483371ef3e4351e7c7770ac1613370031b05626d62e4e4852d0b4b011d9`.
- Contract SHA-256 matched: `4c92d38e5a7953937daee4c781153e5ad7e4ec2945917129cbc0dd43310dff25`.
- Executed validation commands:
  ```sh
  python3 scripts/cdad_packet.py validate-request --project-root . --execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-001/REQUEST.json
  python3 scripts/cdad_packet.py validate-packet --project-root . --execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-001/REQUEST.json --packet .cdad/packets/019-002-effective-discovery-instructions-architect-draft-001/PACKET.md
  python3 -B scripts/cdad_packet.py validate-state --project-root . --execution-context .cdad/executions/exec-019-002-effective-discovery-instructions-001/execution.json
  ```
  First two returned success without diagnostic output. State output:
  ```text
  VALID: execution=exec-019-002-effective-discovery-instructions-001 feature=019-002-effective-discovery-instructions model_policy=ordinary
  ```
- Measurement: Python **3.13.5**, complete byte comparison using `subprocess` renderer stdout and `pathlib.read_bytes()`.
- Examined HEAD: `b11031144766475744f16a2aef621b8092c7f9b2`.
- Modified files by this role: **none**. The pre-existing state diff remained; its measured digest was unchanged at exit.
- Commit created: **none**.
- Tests/full suite: **not run**; this assignment was read-only planning. No product acceptance or operational validation is claimed.