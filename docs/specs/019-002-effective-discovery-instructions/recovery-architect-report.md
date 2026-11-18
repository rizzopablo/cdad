## recovery-spec

**Feature:** `019-002-effective-discovery-instructions`  
**Status:** Draft — not approved. Proposed materialization: `docs/specs/019-002-effective-discovery-instructions/recovery-spec.md`.

### Purpose and baseline

Restore useful discovery dialogue with minimal instructions: the user talks to the orchestrator; the architect provides consequential technical consultation and drafts the specification. Decisions survive handoff without invented agreement or procedural machinery disproportionate to the work.

Examined revision: `c29ef97cea79ebd603491f62dae99bed0bcf05f9`. Product and tests currently equal `bc922c04` across `sources`, `agents`, `skills`, `scripts`, `tests`, `install.sh` and `build`; `git diff --quiet` returned **0**. Restoration is complete, not pending implementation. The pre-existing state-file modification is outside this assignment.

Controlling sources:

- `recovery-direction.md:3–6,19–37`: selected baseline, minimal recovery and exclusions.
- `owner-decision-orchestrator-scope.md:3–20` and `owner-direction-scope-reassessment.md:8–29`: practical orchestrator autonomy and product/test boundary.
- Approved epic contract: single interlocutor, faithful decisions and separately requested closure correction.
- Retained `019-003-contract-verification-strategy/spec.md:32–79`: verification by promise.
- Historical 019-001 activation handoff, items 1 and 4: consultation delivery and resting-state correction.
- Independent retrospective: diagnostic evidence, **not** authorization or proof of candidate acceptance.

### Supersession

Upon explicit approval, this specification replaces the prospective obligations of the old 019-002 specification and plan.

In particular, it replaces the rigid dialogue-record requirements and old PC-4/PC-11 scenario commitments. Their failed, incomplete or unverified observations remain historical evidence; they are **not** marked achieved under the replacement contract.

019-001 remains historically accepted. Its conflicting activation details—including mandatory record structure, blanket investigation restrictions and prescribed scenario coverage—no longer govern this recovery. Retain 019-003’s verification strategy; its references to preserving earlier 019-002 obligations do not reinstate obligations explicitly superseded here.

### Contract and verification

#### Promise A — Faithful dialogue without unnecessary restrictions

**PC-1. Responsibilities.** The orchestrator conducts user-facing dialogue and may investigate, read code and run the product. It consults the architect when consequential uncertainty or independent technical judgment warrants it, and delegates specification drafting. Consultation is not required for every question and cannot depend on readiness already being established.

**PC-2. Recoverable decisions and readiness.** Existing discovery notes and handoffs preserve current confirmed choices, proposals, unresolved consequential questions, relevant technical evidence and corrections with recoverable provenance. Use ordinary prose; require neither a new schema nor recording every message.

Partial answers do not answer omitted questions. Silence and unaccepted defaults are not consent. Corrections govern subsequent work without erasing the displaced decision. Before drafting, consequential choices must be resolved, explicitly excluded, or declared blocking; unsupported technical assumptions remain qualified. Readiness is not approval.

**PC-3. Role boundaries.** The orchestrator must not author or correct product or tests. It may make trivial formal corrections when materializing role deliverables, without changing substance, evidence, conclusions or attributed decisions. Substantive defects return to the responsible role. Preserve original receipts and reports; this permission does not authorize altering frozen packet bytes.

The installed methodology is a tool in use, not automatically the product under development. Existing approval authority, independent review and test-writer separation remain unchanged.

**Method:** Contextual independent review against the controlling sources, supported by the actual-use exercise below.

**Acceptance/evidence:** The reviewer identifies actionable, consistent responsibilities and faithful treatment of decisions across the affected effective instructions, with no unresolved blocking contradiction.

**Limits:** Textual consistency and one observed exercise do not establish universal agent compliance.

#### Promise B — A targeted architect consultation can actually return

**PC-4. Consultation delivery.** Architect/brainstorm accepts exactly one `role-report`, not specification or plan drafts. Native dispatch, the OpenCode adapter and result materialization agree on that delivery. Other role/substage combinations retain their existing behavior.

This correction is justified by the approved dialogue route: consultation needs a deliverable report. The baseline still excludes `role-report` for brainstorm in `cdad_result.py:826–840`; both adapters already derive from that canonical table. Change the table, not the adapters unless demonstrated necessary.

Deliberately replace the obsolete architect/brainstorm rejection expectation in `tests/test_006_005_u7_scribe_role_report.py:699–709`; retain the other closed-role controls.

**Method:** Executable verification, independently written before implementation.

**Acceptance/evidence:** Focused tests demonstrate dispatch-kind derivation through both adapters, result acceptance/materialization and draft-kind rejection. Record RED and GREEN commands, outputs and tested revisions.

**Limits:** Successful delivery proves neither faithful dialogue nor comprehension.

#### Promise C — Closure and next-unit orientation agree

**PC-5. Resting-state consistency.** Preserve the existing legitimate closure effect, `current_stage: idle` and `active_feature: null`. Align closing guidance and epic handoff with it.

Status must apply the resting-coherence criterion already used by `open-unit` before recommending opening or claiming an at-rest situation. In an otherwise eligible fixture, closure → status → opening succeeds. `done`/`null` produces an actionable diagnosis, not an opening recommendation. Status remains read-only; preserve active, suspended and pending-work distinctions and output limits.

This is the separately approved user need recorded in the unit contract, acceptance criterion 7—not a new state model.

**Method:** Combined: executable regression plus contextual review of guidance.

**Acceptance/evidence:** Focused positive and incoherent-state regressions pass; reviewed instructions describe the actual transition.

**Limits:** Resting coherence does not establish unrelated dependency or authority eligibility. Repairing the live workspace state is excluded.

#### Promise D — The candidate is coherent and demonstrated, not merely described

**PC-6. Effective instructions.** Apply the minimal dialogue changes to canonical owners and affected packet, legacy, generated and Odoo consumers. Normal and lightweight guidance must not prescribe incompatible conduct. Correct draft re-entry with a pointer to the **existing** independent review-or-exemption procedure; do not redesign it.

Retain the baseline’s verification-method routing, frozen publication mechanism and applicable distribution protection. Existing frozen packets remain unchanged; candidate exercises use new publications carrying candidate instructions.

**PC-7. Representative actual use.** Run one bounded, representative exercise using actual candidate role sessions:

**need → dialogue → targeted consultation → recoverable decisions → readiness → unapproved draft → independent draft review.**

Within that coherent exchange, observe a partial answer, an unaccepted default and an authorized correction. Demonstrate that an unresolved consequential choice prevents readiness until resolved or explicitly excluded. No fabricated consent, approval or successful outcome is admissible.

Declare the exercise inputs before execution and keep them outside producer edit scope. Record candidate revision, effective instruction versions, packet identities, actual transcripts and resulting artifacts. An independent reviewer assesses those records against this contract and the owner sources. Preserve failures; missing required evidence remains missing.

**Method:** Combined: existing generation/rendering/inventory checks establish delivery; contextual independent review establishes semantic coherence and evaluates the actual exercise.

**Acceptance/evidence:** No unresolved blocking consumer contradiction; satisfactory relevant mechanical checks; one completed journey independently assessed as faithful.

**Limits:** This is bounded candidate evidence, not deployment evidence or a benchmark. There is no fixed scenario quota or obligation to exercise every unchanged approval variant.

### Exact implementation scope

**Executable product edits:**

- `skills/cdad-cycle/scripts/cdad_result.py`
- `skills/cdad-cycle/scripts/cdad_packet.py`

**Instruction production:**

- `sources/roles/{orchestrator,architect}.md`
- `scripts/cdad-generate.py` — architect descriptive metadata only
- `skills/cdad-cycle/SKILL.md` — affected role descriptions and pointers only
- `skills/cdad-cycle/references/{stage-1-discovery,stage-2-specification,re-entry,handoff-prompts,stage-5-merge}.md`
- `skills/cdad-cycle/packets/roles/architect.md`
- `skills/cdad-cycle/packets/substages/architect-brainstorm.md`
- `skills/odoo-architect/SKILL.md` — consultation/question routing only
- `skills/cdad-epic/references/feature-handoff.md`
- `CDAD_metodologia.md` — affected dialogue/lightweight explanations and pointers only

**Generated outputs:** `make agents` regenerates `build/staging/**` and promotes `agents/**`. Review the output delta; no hand-editing or unexplained unrelated changes.

**Test-writer edits:**

- `tests/test_019_002_discovery_delivery.py` — new
- `tests/test_019_002_resting_orientation.py` — new
- `tests/test_006_005_u7_scribe_role_report.py` — obsolete expectation only

Further verifier changes require a justified scope adjustment, not producer repair.

**Orchestration records:** Recovery artifacts under `docs/specs/019-002-effective-discovery-instructions/`; prospective supersession notices and epic-plan amendment; inventory/map updates at their existing declared paths; exercise evidence under `.cdad/orchestration/epic-019/recovery-exercise/`.

All approved sources, historical publications and verifiers remain protected from production edits. The adapters, specification template and `cdad-spec-and-test` routing already provide relevant baseline behavior: no speculative rewrite is proposed.

### Acceptance and invariants

Acceptance requires every postcondition’s declared evidence, independent review without unresolved blockers and explicit acceptance by the authorized approver. Preserve independent role work, protected acceptance inputs and historical records. Never report unperformed verification as completed.

Use focused regression during construction. At **epic closure**, complete the full `tests/` suite and live-inventory validation. Run explicitly against `tests/`; exclude `examples/idea_log/tests/test_idea_log.py` because it is an Odoo addon example requiring Odoo’s test environment (`:3–10`), not this methodology suite.

No installation, deployment, public publication, directory migration, model change, new permission system, gate or runtime service is authorized.

### deferred-hardening

- Universal compliance and exhaustive runtime/scenario coverage: beyond the bounded promise.
- Automatic semantic or approval enforcement: no demonstrated need for a new mechanism.
- Installed `--check` diagnosis and deployment: separate operational work.
- Unrelated documentation and regression cleanup: outside this delta.

None postpones a committed postcondition.

---

## recovery-plan

**Status:** Draft — not approved. Proposed materialization: `docs/specs/019-002-effective-discovery-instructions/recovery-plan.md`.

1. **Reconcile the contract before production.**  
   Materialize this draft, obtain independent sufficiency review and explicit approval through existing procedures. Amend the epic plan to reference this replacement and its bounded evidence. Add prospective supersession notices to the old 019-002 specification/plan and 019-001 design entry point; preserve original text, approval pins, receipts and failed observations. Do not claim historical acceptance retroactively.

2. **Consultation delivery — RED dispatch.**  
   Independent test-writer: PC-4 only; the new delivery test file plus the named obsolete expectation. Provide the approved contract and necessary interfaces, not implementation code. Return focused failure evidence and inventory delta.

3. **Consultation delivery — GREEN dispatch.**  
   Implementer: `cdad_result.py` only. Satisfy the protected tests with the smallest closed-table change. Run focal delivery and existing materialization regression.

4. **Resting orientation — RED dispatch.**  
   Independent test-writer: executable PC-5 only, in the new orientation test file. Exercise real closure/status/opening and incoherent-state diagnosis without repairing this project’s live state.

5. **Resting orientation — GREEN dispatch.**  
   Implementer: `cdad_packet.py` only. Reuse the existing coherence criterion; preserve projection behavior outside the promised correction. Run focal orientation and relevant existing idle/closure regressions.

6. **Semantic production — separate dispatch.**  
   Implementer: only the instruction-production and generated-output scope above. Implement PCs 1–3 and 6 plus PC-5 guidance. Prefer concise canonical rules and operational pointers over duplicating a new protocol. Run `make agents` and relevant existing generation/rendering checks. No fabricated RED for semantic fidelity.

7. **Independent contextual review — separate dispatch.**  
   Review the actual candidate against owner sources, retained 019-003 and the approved replacement. Examine effective packet, legacy, generated, lightweight and affected Odoo routes. Check that simplification removed restrictions rather than redistributing them into other files. Route substantive corrections to their producer.

8. **Actual-use exercise and independent assessment.**  
   Execute PC-7 with candidate role sessions and new packets. Independently assess the recoverable transcript and artifacts. Address demonstrated defects proportionally; do not convert incidental observations into universal rules.

9. **Closure evidence.**  
   Materialize inventory/map deltas and run `python3 scripts/cdad-suite.py validate`. Record focal regression and semantic evidence separately. At epic closure run:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests
   ```
   Record complete output, exit status, candidate/test versions and environment. Missing or failed evidence prevents accreditation. No installation or publication follows from closure.

### Architect evidence

- **Intake:** Route C validated; identification matched; contract SHA-256 matched; execution context is v2; complete `PACKET.md` bytes equaled canonical `render` output.
- **Commands:** `validate-request`, `validate-packet` and `render --route C` using the named REQUEST; Python full-render byte comparison; `git rev-parse HEAD`; `git diff --quiet bc922c04 -- sources agents skills scripts tests install.sh build`; targeted repository reads/searches.
- **Results:** Packet checks succeeded; baseline equality returned **0**. Final tracked diff contained only the pre-existing `docs/.cdad-state.json` modification.
- **Files modified / commits created:** None.
- **Tests executed:** None. This is an unapproved architectural draft, not implementation or acceptance evidence.