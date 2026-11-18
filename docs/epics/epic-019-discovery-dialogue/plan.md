---
epic_id: epic-019-discovery-dialogue
epic_name: Effective discovery dialogue and agent instructions
created_at: 2026-11-15
approved_by: Pablo
approved_at: 2026-11-15
---

# Epic 019: Effective discovery dialogue and agent instructions

## Purpose and opening mandate

Pablo requested a new epic to design this sensitive change carefully, emphasizing
instructions that agents can understand and apply effectively. Opening the epic
authorized discovery and planning, not implementation. Pablo subsequently approved
this plan on 2026-11-15. Subsequently 019-001 was accepted and 019-002 opened
in discovery; the approved amendment below inserts 019-003 before its construction.

The target includes **both the normal five-stage CDAD cycle and the lightweight
workflow**. OpenSpec inspired the discussion; it is not a new dependency.

## Discovery baseline and proposed direction

The user converses with the orchestrator. Current guidance instead tells the
delegated architect to ask the user questions and wait for answers, without
explicitly connecting that conversation through the orchestrator. This is an
interaction-contract gap, not proof that every runtime forbids subagent questions.

Existing references:
- `skills/cdad-cycle/references/stage-1-discovery.md`: initial discovery already
  involves the user and orchestrator; per-feature technical discovery is delegated.
- `skills/cdad-cycle/references/handoff-prompts.md`, architect brainstorm:
  questions, waiting for answers and `READY FOR DRAFT` assume an interactive loop.
- `skills/cdad-cycle/references/stage-2-specification.md` and `re-entry.md`:
  dispatch and closure are described, but the mediated question loop is not explicit.
- `sources/roles/orchestrator.md` and `sources/roles/architect.md`: current role
  boundaries must be reconciled explicitly, not bypassed by informal practice.

Proposed division, subject to design review and owner approval:
- Orchestrator and user conduct functional discovery and brainstorming: problem,
  journey, expected result, boundaries and behavioral choices.
- Architect investigates existing behavior and technical feasibility, challenges
  assumptions, supplies questions and alternatives when useful, and drafts the spec
  from recorded decisions. Technical research is not moved wholesale to the orchestrator.
- Reviewer independently examines the draft; the owner approves it. Conversation,
  agreement on an answer and approval of the spec remain distinct.

Retain three useful improvements: establish the affected existing behavior with
evidence; distinguish confirmed decisions, proposals and unresolved questions;
state what changes and what is preserved in the affected observable behavior.
Prioritize decisions that condition others without imposing a fixed questionnaire,
one-question quota or scenario/test quota.

## Scope and exclusions

In scope: ownership and stopping conditions of the conversation; transfer of
decisions and technical findings; handling partial answers, corrections and
unknowns; coherent canonical instructions, effective role packets and legacy
handoffs; shared and domain-specific consumers where affected; semantic examples
and an observed end-to-end acceptance exercise.

Out of scope: OpenSpec installation, CLI or artifact graph; a capability catalog;
a new UI or runtime communication service; weakening independent test-writing or
review; automatic spec approval; unrelated documentation cleanup; publication or
deployment without a separate owner decision.

No new state, gate, role or document is presumed necessary. Any such need must be
justified during design, not introduced as an incidental implementation detail.

## Proposed decomposition — not yet scheduled

| Order | Feature | Independently reviewable result | Dependency |
|---|---|---|---|
| 1 | `019-001-discovery-dialogue-contract` | Reviewed documentary operating design: role boundaries, dialogue and handoff contracts, closure criteria, representative positive and negative examples | Owner-approved epic plan |
| 2 | `019-003-contract-verification-strategy` | Coherent verification instructions based on the promised property, with independent spec review, appropriate production routing and honest evidence evaluation | 019-001 accepted; amendment approved |
| 3 | `019-002-effective-discovery-instructions` | Implement the approved operating design coherently in canonical instructions and their effective consumers; verify distribution and observed use; correct the idle/done transition and orientation inconsistency | 019-001 and 019-003 accepted |
| 4 | `019-004-project-layout-and-dispatch-intake` | Default methodology documents to `cdad/`, make product-repository-relative paths explicit, and simplify role intake by composing the existing validators | Owner-approved extension below; close 019-002 before opening execution |
| 5 | `019-005-bounded-review-cycles` | A per-unit, architect-justified bound on consecutive review/audit+fix rounds, with a single epic-end accumulation cycle for accepted debt | Owner-approved extension; opens after 019-004 |

019-001 remains accepted. 019-003 establishes the verification instructions before
019-002 construction. 019-002 retains its existing obligations and provides a
bounded application and feedback opportunity, not universal validation of the
methodology. Additional mechanisms require observed deficiencies and a justified
subsequent decision.

## Cross-feature contract

Each promise receives verification appropriate to its property. The architect
specifies the method, acceptance criterion and expected evidence. Before approval,
the independent spec reviewer checks whether every promise and its proposed
verification are correct and sufficient. Preserve the existing explicitly
registered review exemption.

Approved acceptance criteria remain fixed before implementation. The orchestrator
routes applicable executable tests to the independent test-writer before
implementation and contextual independent review to the reviewer after
implementation. Producers cannot change their acceptance criteria or protected
verifiers.

Executable, semantic-only and mixed commitments retain their respective obligations.
Observed execution is required where explicitly committed, including 019-002's
existing real-agent exercise; it is not a universal additional workflow.

The design must identify, in plain actionable language: who asks, investigates,
records, challenges, drafts, checks closure and approves; what information each
handoff must preserve; and when to ask the user, consult the architect or proceed.
It must distinguish confirmed decisions from interpretations and proposals, avoid
unnecessary research and specify how a fresh session recovers the agreed context.

Instruction acceptance evaluates what an agent can do from its actual inputs,
not whether it has read an explanatory document elsewhere. Each rule has one
canonical owner; consumers use appropriate pointers or operational instructions
without introducing conflicting duplicate definitions.

## Epic acceptance criteria

1. The normal cycle supports a single user-facing interlocutor without pretending
   that the architect had a direct conversation with the user.
2. The operating design and its implementation receive independent review and
   owner approval at the applicable existing gates; the old role prohibitions
   are reconciled explicitly and their remaining boundaries stay clear.
3. Observed cases cover partial answers, an unaccepted default, a corrected
   decision and an unresolved behavioral choice: none becomes an invented
   agreement or premature closure. An unverified technical assumption remains
   visible and is routed to investigation rather than asserted as fact.
4. An existing-behavior change produces an evidenced, bounded delta; genuinely
   new functionality does not require an invented baseline. No compatibility
   guarantee is inferred for unexamined surfaces.
5. A real agent exercise follows need → dialogue → targeted architect input →
   recorded decisions → draft → independent draft review. Its transcript and
   artifacts show fidelity to the user's decisions and declare limitations;
   structural checks or keyword matches alone cannot establish semantic success.
6. Effective packets, generated agents where affected, references and legacy
   handoffs do not require incompatible conduct. Focused regression, inventory
   integrity and closure evidence follow the existing test evidence policy;
   neither a full-suite waiver nor semantic success is assumed in advance.
7. A correctly closed feature leaves a coherent resting state from which an
   eligible next unit can be opened; the status view does not recommend opening
   when the same state makes opening fail. Align closing guidance with the actual
   transition and protect the behavior with focused regression evidence. Repair
   of the previously inconsistent workspace state is separate from this permanent fix.

8. Normal and lightweight instructions support appropriate
verification without conflicting effective consumers. Acceptance identifies
supporting, failed, missing, contradictory and unverifiable evidence, with its
limits. Existing relevant distribution protection and proportionate regression
are retained; no separate new test is required for each postcondition.

## Risks and decisions to resolve during design

- Avoid making the orchestrator an unrestricted substitute for every role.
- Avoid per-question dispatch overhead and context growth from excessive research.
- Decide the minimum durable decision record and the closure check that catches
  lost nuance without repeating the whole conversation.
- Decide how existing architect brainstorm packets and specialized variants evolve;
  do not silently retire a supported path or broaden permissions.
- Use concise English public instructions with concrete triggers, actions and
  counterexamples. Review ambiguity, duplication and actual agent comprehension,
  not length or stylistic polish alone.

## Authority and next step

Plan approver: Pablo. Feature and gate authority: Pablo expressly delegated HITL
for this epic as recorded in `execution.md`. Users and operators: process owners
and agents running CDAD. No approval delegation from an earlier epic applies here.

Plan approved by Pablo on 2026-11-15. Pablo subsequently requested adding the
idle/done correction to one of the two units and delegated HITL for this epic.
The specification of each feature still requires an explicit recorded approval.
Existing execution and receipt records belong to earlier work and confer no
authority for this epic. No role instructions have been changed or deployed.

Status: Approved by Pablo on 2026-11-15.

## Plan changes

2026-11-15 — Pablo requested and approved inserting 019-003 before 019-002,
then explicitly approved the simplified direction ("Ok, hagamos eso, continúa"):
each promise receives appropriate verification; the spec reviewer checks the
promises and their verification before approval; tests precede implementation
where applicable and contextual independent review follows it. No comprehension
reader, new agent or mandatory pre-production review checklist is included.
Replacement draft 004 supersedes drafts 001–003 prospectively and received
independent review without blockers in
`docs/specs/019-002-effective-discovery-instructions/verification-strategy-review-004.md`.
019-001 and its historical evidence remain unchanged. Publication and deployment
remain excluded. The unit specification requires its own recorded approval.


## Owner-directed recovery amendment

The owner selected closure of 019-003 (`bc922c04`) as the restored product/test baseline and renewed delegated HITL. Remaining 019-002 execution follows its approved recovery-spec.md and recovery-plan.md, with review dispositions and the mandatory pre-exercise runtime feasibility condition in recovery-approval.md. This prospectively replaces conflicting dialogue-record and historical scenario quotas, without changing historical acceptance or turning failed runs into success. Retain single interlocutor, faithful decisions, consultation delivery and closure orientation; require bounded actual candidate use, independent assessment, full tests/ suite, inventory and Memory Bank closure. No installation, deployment or publication is authorized.

## Owner-approved extension — project layout and dispatch intake (2026-11-16)

Pablo requested these improvements and explicitly instructed adding them as a new
cycle of this same epic: “Sumémoslo como nuevo ciclo de este epic, seguimos
haciendo mejoras.” The epic therefore remains open after 019-002; the new unit is
`019-004-project-layout-and-dispatch-intake`. This is approval of the scope
extension, not approval of an unwritten feature specification.

Confirmed objectives:

- Default methodology documents (state, policy, epics, cycle/specification
  artifacts and methodological memory) to `cdad/`, reserving `docs/` for
  end-user documentation.
- Make paths relative to the product repository root, which need not be the
  directory of the coordinator's local session. The nested directory can have
  any name; neither `src/` nor `cdad/` is a required repository basename.
- Reduce repetitive role-intake work, preferably to one command composing the
  existing validation machinery. Preserve validation of the actual received
  dispatch, not just the published files on disk, for both admitted routes.

Discovery evidence and design questions are recorded in
`docs/specs/019-004-project-layout-and-dispatch-intake/discovery-notes.md`.
Do not move historical records or alter active execution paths as an incidental
effect of this plan amendment. Compatibility, migration and the exact CLI remain
to be specified and reviewed. Existing `.cdad/` operational storage is not
automatically renamed by this objective. This amendment grants no new deployment
or publication authority.

## Scope amendment — self-contained dispatch (2026-11-17)

Pablo directed that a self-contained dispatch is not a separate cycle: this epic is
already a methodology cycle, so the correction is absorbed into 019-005 rather than
queued as 019-006. The approved 019-005 specification receives amendment 001 adding
the promise and its postconditions; implementation stays in the same batch, and the
amendment is independently reviewed before approval is re-pinned.


## Owner-approved extension — suite selector maintenance (2026-11-17)

The epic's closure suite failed twice, in the same node id, on a defect of the
verification instrument: `find_deployed()` returns the first filesystem match of
an agent filename, and the installer deploys that name to two runtime
destinations with different bytes (`.claude/agents/` and
`.config/opencode/agents/`). The owner approved repairing it before the gate
("Sí, ok A"). It is a separate minimal unit,
019-007-suite-selector-maintenance, because packets bind to a unit contract
and the defect belongs to a test of an earlier feature, not to 019-005.

Scope: test-only (the two copies of the helper and the assertions that use
them). No installer, agent, policy or product behavior changes. Verification:
the affected class and module, plus the complete suite that feeds the epic
closure gate. The unit closes before the epic, and the epic gate is the complete
suite run after the fix.
