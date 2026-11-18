# Verification strategy — replacement DRAFT 004

**UNAPPROVED · Planning only**

This draft supersedes verification-strategy drafts 001–003 **as the proposal for future work**. Preserve those drafts, their reviews and all accepted historical evidence. Nothing here authorizes implementation, changes the active plan or approves this proposal.

## 1. Design decision and basis

**Each promise receives appropriate verification.** The architect specifies the promised property, verification method, acceptance criterion and expected evidence. The independent spec reviewer checks their correctness and sufficiency **before approval**. After approval, the orchestrator routes applicable executable tests to the test-writer before implementation and contextual independent review to the reviewer after implementation.

This general rule is preferable to separate “documentation” and “code” methodologies: one product can contain promises requiring different evidence. It neither mandates automation whenever possible nor exempts executable behavior because it accompanies documentation.

The proposal removes the comprehension-reading machinery introduced in earlier drafts. It creates no reader assignment, profile inventory, minimal-context exercise, pre-production reviewer checklist, role, gate, field or validator.

### Verified reconciliation needed

At examined HEAD `d61fb4876551ee947e04950b7c23676dbfe97298`:

- Stage 2 already requires independent draft review and records an explicit owner exemption (`stage-2-specification.md:47–74`). It needs an explicit review of verification sufficiency, not another review gate.
- Stage 2 still describes every task as RED/GREEN and always hands approved work to RED (`:134–150,206–224`).
- Stage 3’s acceptance wording and production routing assume behavioral tests and valid RED (`stage-3-tdd.md:21–40,136–156`).
- Implementer packet instructions require current failing tests (`packets/roles/implementer.md:1`; `packets/substages/implementer-green.md:1`).
- The lightweight workflow treats passing tests as completion (`skills/cdad-spec-and-test/SKILL.md:56–78`).
- Documentary guidance already distinguishes structural control from semantic review (`documentary-contracts.md:151–175`).
- The earlier owner decision applies specifically to 019-001; it is not an existing universal exemption (`docs/epics/epic-019-discovery-dialogue/execution.md:16–28`).

These are instruction inconsistencies to reconcile prospectively. They do not establish a need for CLI or schema changes.

## 2. Epic-plan amendment DRAFT

**Target:** `docs/epics/epic-019-discovery-dialogue/plan.md`

Preserve feature IDs, the decomposition heading, table anchors and original approval history.

### Decomposition changes

- Keep **019-001** first, with its accepted documentary result and historical evidence unchanged.
- Insert **019-003-contract-verification-strategy** second:
  - **Result:** coherent verification instructions based on the promised property, with independent spec review, appropriate production routing and honest evidence evaluation.
  - **Dependency:** 019-001 accepted; this amendment approved.
- Move **019-002-effective-discovery-instructions** to third:
  - Preserve its existing result, including effective distribution, observed use and the idle/done correction.
  - **Dependency:** 019-001 and 019-003 accepted.

Replace the decomposition’s following explanation with:

> 019-001 remains accepted. 019-003 establishes the verification instructions before 019-002 construction. 019-002 retains its existing obligations and provides a bounded application and feedback opportunity, not universal validation of the methodology. Additional mechanisms require observed deficiencies and a justified subsequent decision.

### Cross-feature contract addition

> Each promise receives verification appropriate to its property. The architect specifies the method, acceptance criterion and expected evidence. Before approval, the independent spec reviewer checks whether every promise and its proposed verification are correct and sufficient. Preserve the existing explicitly registered review exemption.
>
> Approved acceptance criteria remain fixed before implementation. The orchestrator routes applicable executable tests to the independent test-writer before implementation and contextual independent review to the reviewer after implementation. Producers cannot change their acceptance criteria or protected verifiers.
>
> Executable, semantic-only and mixed commitments retain their respective obligations. Observed execution is required where explicitly committed, including 019-002’s existing real-agent exercise; it is not a universal additional workflow.

### Epic acceptance criterion 8

> Normal and lightweight instructions support appropriate verification without conflicting effective consumers. Acceptance identifies supporting, failed, missing, contradictory and unverifiable evidence, with its limits. Existing relevant distribution protection and proportionate regression are retained; no separate new test is required for each postcondition.

Correct the stale “no feature has been started” sentence without erasing its historical context. Add a dated **Plan changes** entry recording the approved amendment and prospective sequence. Publication and deployment remain excluded.

## 3. Proposed specification: 019-003

### Functional description and journey

An owner considering a promised result can understand **what will establish acceptance before production begins**.

The architect drafts the contract and verification strategy. The independent reviewer assesses both before approval. Following approval, the orchestrator assigns applicable tests and production, then obtains contextual independent review. Closure presents what the evidence establishes and what remains unresolved.

**First useful result:** an approvable contract whose verification fits its promises, followed by acceptance grounded in that evidence.

### Scope and sources

Change canonical instructions and their affected consumers across:

- The normal five-stage cycle and lightweight workflow.
- Prepared packets and legacy handoffs.
- Generated generic and inherited domain-specific agents where affected.

Admitted sources are the approved amendment and specification, existing canonical instructions, accepted dependency context, relevant tests and distribution contracts, and authority records. Identify examined revisions in existing assignments and reports.

The approved contract and protected acceptance inputs remain outside the producer’s editable scope. Where instructions themselves become the product, preserve their examined baseline separately. Test-writer assignments retain implementation-read separation.

This unit does not implement 019-002’s dialogue activation, CLI corrections or real-agent exercise.

### Promise A — The owner can approve a sufficient verification strategy

**PC-1.** Specification instructions require each observable promise to identify its property, numbered postconditions, selected method—executable tests, contextual independent review or their combination—acceptance criterion, expected evidence and verification limits. Existing prose and artifacts suffice; no new schema is required.

**PC-2.** The existing independent spec review explicitly checks that every promise is correct and that its proposed verification can sufficiently establish acceptance. Insufficient or unverifiable commitments return for correction before approval. Preserve the existing owner exemption and its registered form; an exemption is not an executed review or a claim of verified sufficiency.

**Verification:** contextual independent review of the changed specification guidance, template and applicable review consumers.

**Acceptance/evidence:** the reviewer’s attributable report identifies whether those instructions enable an approval decision with sufficient verification and records any unresolved defects or abstentions. Merely finding the requested words is insufficient.

### Promise B — Production follows the approved commitment without producer-controlled acceptance

**PC-3.** Routing instructions distinguish:

- **Pending executable behavior:** independent test-writing before implementation, with applicable RED/GREEN and existing audit procedures.
- **Semantic-only production:** production followed by contextual independent review against the approved contract and sources, without manufacturing a failing executable test.
- **Mixed commitments:** both applicable verification families, with neither substituting for the other.

Existing distribution or structural checks remain applicable where relevant; their presence does not make semantic fidelity an executable property.

**PC-4.** Acceptance criteria are approved before implementation and cannot be changed by the producer. Necessary changes stop the affected work and return through the applicable review and approval procedure. The final reviewer uses the approved specification and relevant context; no separately commissioned pre-production checklist is required.

**Verification:** contextual independent review of production routing, role boundaries, packet instructions, legacy handoffs and lightweight guidance.

**Acceptance/evidence:** the report finds an actionable route for each commitment type without conflicting instructions, fabricated RED evidence, producer-edited acceptance criteria or weakened test-writer separation.

### Promise C — Acceptance reflects actual evidence and coherent delivery

**PC-5.** Reporting and closure instructions distinguish support within declared limits, failed criteria, missing evidence, contradictory evidence and inability to verify. Missing required evidence or an unmet commitment prevents accreditation; declaring a limitation does not turn it into success.

No method proves beyond its reach: byte equality does not establish semantic fidelity; favorable review does not replace promised runtime observations; observed success does not establish unexamined behavior.

**PC-6.** Affected canonical and effective instructions consistently carry PCs 1–5 across normal, lightweight, packet, legacy and generated routes. Existing applicable generation, rendering and distribution protection is reused with proportionate audit. Preserve 019-001’s acceptance and historical evidence, and leave 019-002’s executable and real-agent obligations intact.

**Verification:**

- Contextual independent review of the actual candidate instructions and relevant effective consumers.
- Existing relevant delivery checks and attributable candidate/output comparisons, selected according to the changed surfaces.
- Comparison with protected historical inputs for prospective scope and preserved obligations.

**Acceptance/evidence:** reports identify examined versions, covered surfaces, relevant delivery results and limits, with no unresolved blocking inconsistency. Reuse evidence across postconditions where it establishes the same property; require neither a new test nor a separate distribution exercise per PC.

### Invariants

- Producers do not modify protected acceptance criteria or verifiers.
- Test-writing and implementation remain independently assigned.
- Unperformed verification is never reported as executed or green.
- Historical evidence is not rewritten to satisfy prospective criteria.

These are reviewable constraints, not an automatic demand for randomized property tests.

### Overall acceptance

Accept only when PCs 1–6 have attributable evidence, required applicable checks have satisfactory results, independent review leaves no unresolved blocking defect, and the authorized approver explicitly accepts the result.

**Limits:** this verifies instruction fidelity, coherence and relevant delivery—not universal agent compliance. 019-002 supplies its separately committed bounded observations.

### deferred-hardening

- **Universal observed workflow or agent-compliance benchmark:** not promised; observation is required only by explicit commitments.
- **Automated semantic oracle or new mechanical enforcement:** unjustified by the examined need; reconsider only after concrete deficiencies.
- **Unrelated consumer cleanup and exhaustive regression:** outside this bounded change; retain relevant distribution protection and the existing test-evidence policy.

No deferral postpones a committed promise.

## 4. Minimal implementation plan DRAFT

### T1 — Coherent instruction activation

**Consumes:** approved amendment, approved specification and protected baseline.

**Produces:** canonical instructions and affected consumers satisfying PCs 1–6.

Canonical allocation:

- **`stage-3-tdd.md`:** reconcile the foundational acceptance statement/R7 and method-dependent production routing. Preserve ownership of the existing test-evidence policy.
- **`stage-2-specification.md` and `assets/spec-template/spec.md`:** specify verification content and extend the existing pre-approval review to assess sufficiency; condition unconditional RED/GREEN planning language.
- **`stage-4-review.md`:** contextual post-production verification against the approved commitment, including evidence limits.
- **`documentary-contracts.md`:** align by reference without creating a competing general methodology.
- **Role sources and packet blocks/substages:** align architect, reviewer, orchestrator and implementer duties where affected; preserve test-writer boundaries.
- **`handoff-prompts.md`, `re-entry.md` and lightweight instructions:** remove contradictory unconditional routing and “tests pass, therefore done” implications.
- **Generated agents:** regenerate through the existing generator; do not hand-edit derived output.

The orchestrator first routes applicable executable verification to the test-writer. Its proportionate audit reuses existing protection, with candidates including `test_cdad_generate.py`, `test_role_packet_render.py`, `test_install_ownership.py` and `test_004_002_t6_landing.py`. Their existence does not establish coverage or a passing result. Tests encoding superseded requirements receive deliberate dispositions under existing rules.

After production, the independent reviewer evaluates the candidate in context against the approved criteria and applicable delivery evidence.

No executable change is presently specified. If an actual consumer prevents this route, report the concrete blocker for a bounded decision rather than adding speculative CLI scope.

**Self-application:** approval of 019-003 must explicitly authorize its proposed verification strategy. This draft cannot itself waive current obligations.

## 5. Sequence and reconciliation

Draft-003 §5 and review-002’s pin finding remain **historical analysis**, not current operational evidence. Refresh the actual packet, receipt, continuity, contract and suspension inputs after this consultation’s re-entry and independent review.

Proposed sequence:

1. Receive this result and obtain independent review of the replacement draft.
2. Obtain applicable explicit amendment/specification approvals.
3. Refresh affected pins; preserve frozen requests, packets, contracts and historical authority.
4. Materialize the approved plan amendment and synchronize epic sequencing through existing procedures.
5. Run existing `validate-unit-contract`; resolve its actual consequence. A live-plan impact decision never authorizes rewriting a frozen digest.
6. At a verified safe boundary, use existing `suspend-unit` for 019-002 and `open-unit` for registered, eligible 019-003.
7. Complete 019-003, then use existing `resume-unit` for 019-002 and prepare fresh applicable assignments.

Stop on rejection. Do not clear bindings, rewrite saved resumption checks or treat a used packet as undispatched. These operations are proposed, **not executed or certified successful**.

## 6. Role evidence

- **Intake:** Route C identification matched the canonical identification; request and published packet validated.
- **Complete comparison:** canonical render equaled all **8,776 published packet bytes**.
- **Execution context:** schema v2.
- **Contract SHA-256:** `4c92d38e5a7953937daee4c781153e5ad7e4ec2945917129cbc0dd43310dff25`.
- **Measurement:** Python 3.13.5, direct stdout-byte comparison against `Path.read_bytes()`.
- **Modified files by this role:** none. Initial and final status showed only the pre-existing `docs/.cdad-state.json` modification.
- **Commit created:** none.
- **Tests/full suite:** not run; read-only planning.
- **Operational transitions:** not run.

Exact validation commands:

```sh
P=.cdad/packets/019-002-effective-discovery-instructions-architect-draft-004
python3 scripts/cdad_packet.py validate-request --project-root . --request "$P/REQUEST.json"
python3 scripts/cdad_packet.py validate-packet --project-root . --request "$P/REQUEST.json" --packet "$P/PACKET.md"
```

Both succeeded without diagnostics. The exact byte-comparison script, source reads/searches and outputs are retained in this role’s tool transcript. An exploratory `validate --help` returned an unsupported-subcommand diagnostic; the supported validation commands above succeeded.

**Status: Unapproved replacement draft; independent review and explicit applicable approval pending.**