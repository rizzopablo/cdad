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

**PC-3. Role boundaries.** The orchestrator must not author or correct product or tests. It may make trivial formal corrections in an explicitly attributed corrected presentation of a role deliverable, separate from the durable original and its journaled canonical copy, without changing substance, evidence, conclusions or attributed decisions. Receive and materialize the original byte-identically through the existing route; leave its receipt, stored report and journaled canonical copy unchanged. Substantive defects return to the responsible role. This permission does not authorize altering frozen packet bytes or redesigning the materialization engine.

**Operational example (illustrative, not executed evidence):** An architect report contains the typo `recieve`. Receive it unchanged and, with the existing explicit authorization, materialize it as `consultation-original.md` in the allowed feature records. Leave the durable receipt, stored report and that journaled target untouched. A separately named `consultation-presentation.md` in those records may show `receive`, explicitly identifying the architect as the original author, referencing the original report and receipt, and attributing that spelling correction to the orchestrator. It is a corrected presentation, not a replacement receipt payload or journaled canonical target. A retry of the original materialization with the same otherwise-valid receipt and authorization still sees identical target bytes and skips rewriting; editing `consultation-original.md` instead would trigger the existing divergent-target conflict.

The installed methodology is a tool in use, not automatically the product under development. Existing approval authority, independent review and test-writer separation remain unchanged.

**Method:** Contextual independent review against the controlling sources, supported by the actual-use exercise below.

**Acceptance/evidence:** The reviewer identifies actionable, consistent responsibilities and faithful treatment of decisions across the affected effective instructions, with no unresolved blocking contradiction. Contextually check the PC-3 example against the existing receipt/materialization and retry behavior: originals remain byte-identical and the attributed correction is confined to the separate presentation. This uses the existing semantic review task; no additional task, implementation scope or product test is required.

**Limits:** Textual consistency and one observed exercise do not establish universal agent compliance.

#### Promise B — A targeted architect consultation can actually return

**PC-4. Consultation delivery.** Architect/brainstorm admits `role-report` as its artifact kind, not specification or plan drafts. Normal native dispatch and OpenCode adapter delivery each produce one report; both adapters and result materialization agree on that kind. This is a kind/normal-delivery promise, not a new global result part-cardinality constraint. Other role/substage combinations retain their existing behavior.

This correction is justified by the approved dialogue route: consultation needs a deliverable report. The baseline still excludes `role-report` for brainstorm in `cdad_result.py:826–840`; both adapters already derive from that canonical table. Change the table, not the adapters unless demonstrated necessary.

Deliberately replace the obsolete architect/brainstorm rejection expectation in `tests/test_006_005_u7_scribe_role_report.py:699–709`; retain the other closed-role controls.

**Method:** Executable verification, independently written before implementation.

**Acceptance/evidence:** Focused tests demonstrate dispatch-kind derivation and normal one-report delivery through both adapters, result acceptance/materialization of `role-report` and draft-kind rejection. No new rejection of multiple report parts is promised or required. Record RED and GREEN commands, outputs and tested revisions.

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

### Architect role report — outside the proposed specification

- **Intake:** Route C validated against the named request, complete canonical packet render and contract digest; execution context schema is **2**. No alternate packet selected.
- **Changes proposed:** Only PC-3 and PC-4 clarifications, their verification wording and the requested illustrative example. Four localized replacements were checked in memory; nothing was written.
- **Design choice:** Retain kind-based delivery and the existing immutable materialization route, rather than introducing general cardinality enforcement or an engine redesign. This follows the packet’s delegated decisions and resolves the two reviewed mismatches without new scope.
- **Grounding:** `skills/cdad-cycle/scripts/cdad_result.py:974–980` skips identical journaled targets and rejects divergent ones; `:1086–1094` takes canonical bytes from the durable original. Native and OpenCode one-part construction appears at `cdad_dispatch.py:1034–1044` and `cdad_delegate_opencode.py:2171–2181`.
- **Plan:** Unchanged. SHA-256 remains `7d4fcec1604d1d8f5dd7421dd93def4cd7b82ae253c0bff49f786245e6f46cc8`. Existing semantic production/review tasks cover the clarification.
- **Commands/output:** Exact shell bodies, including read-only Python byte comparisons and the in-memory draft diff, are retained in this dispatch’s tool transcript. The principal commands were:
  ```sh
  python3 scripts/cdad_packet.py validate-request --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-010/REQUEST.json
  python3 scripts/cdad_packet.py validate-packet --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-010/REQUEST.json --packet .cdad/packets/019-002-effective-discovery-instructions-architect-draft-010/PACKET.md
  python3 scripts/cdad_packet.py render --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-010/REQUEST.json --route C
  python3 scripts/cdad_packet.py render --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-010/REQUEST.json
  git diff --quiet bc922c04 -- sources agents skills scripts tests install.sh build
  git status --short
  git rev-parse HEAD
  ```
  Validators completed without error or output. Identification matched; full packet bytes matched canonical render. Baseline product diff returned **0**. Initial and final status were identical.
- **Files modified / commits created / approvals issued:** None. HEAD remains `c29ef97cea79ebd603491f62dae99bed0bcf05f9`.
- **Limits:** No product tests, receipt replay, actual-use exercise or complete suite executed. The example is illustrative and source-grounded, not observed execution evidence. Independent sufficiency review and authorized approval remain pending.