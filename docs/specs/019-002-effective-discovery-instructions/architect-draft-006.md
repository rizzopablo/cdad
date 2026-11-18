## Role report

**Route C validated:** v2 execution context; identification matches; complete `PACKET.md` equals the canonical render: 7,191 bytes, SHA-256 `47cfc310916e22969bb4ac33bb738cd4462921acf0f2e5069e26962226ea1493`. Contract digest matches.

**Revision:** T1 now declares its exact paths in the canonical block, with separate role scopes preserved. Existing plan checks accept the complete corrected block, **rc=0**. The specification and substantive commitments remain unchanged. Candidate-runtime feasibility remains unresolved.

**Files edited:** none. **Commit created:** none. Both drafts remain unapproved.

---

# Draft `spec.md`

# Effective discovery instructions

**Feature:** `019-002-effective-discovery-instructions`  
**Status:** UNAPPROVED DRAFT

## Functional description

The owner describes a need to the orchestrator and resolves functional choices through that single interlocutor. The architect supplies targeted technical findings, challenges and alternatives through the orchestrator, then drafts from recoverable decisions. An independent reviewer examines the draft before approval, unless the existing registered exemption applies.

The first useful result is a faithful, reviewable draft—not an inferred agreement. After legitimate feature closure, operational guidance and status consistently support opening an eligible next unit.

**Global constraints:** No installation, deployment, public publication, live-state repair, new role, packet/state field or gate. Preserve role independence, protected acceptance inputs and historical evidence.

## Sources and technical baseline

Examined revision: `bc922c04a0cbd4e819df47f3d3d2b5e303fcc03a`. The existing modification to `docs/.cdad-state.json` is not part of this product.

Admitted sources:

- Approved epic plan and this unit’s validated contract.
- Accepted 019-001 operating design, including its activation map, handoff and acceptance protocol. Acceptance of D1–D5 is recorded separately in `docs/specs/019-001-discovery-dialogue-contract/acceptance-record.md:3–23`; the product’s historical “proposal” labels are not rewritten.
- Approved 019-003 specification and its existing verification instructions.
- Relevant repository code, canonical instructions, generated consumers, tests and distribution/inventory contracts.
- For observed acceptance: protected scenario inputs declared before execution, actual transcripts, delivered artifacts and recorded effective instruction versions.

Verified baseline:

- `cdad_result._allowed_kinds(role, substage)` currently admits draft kinds, but not `role-report`, for architect/brainstorm. Both dispatch derivation functions consequently reject it. See `skills/cdad-cycle/scripts/cdad_result.py:826–840`, `cdad_dispatch.py:999–1016`, and `cdad_delegate_opencode.py:492–519`.
- Architect draft re-entry currently sends a passing draft directly to approval: `skills/cdad-cycle/references/re-entry.md:240–266`. Stage 2 independently requires draft review or the registered exemption: `stage-2-specification.md:47–81`.
- That review gate is **supervised**, not a CLI check for the existence of a verdict. Preserve this distinction; see `tests/test_006_006_u3_review_route_and_gate.py:24–65`. Exemption registration currently records the supplied fields rather than deciding their procedural sufficiency: `cdad_packet.py:8990–9003`.
- Frozen instruction rendering and new-publication capture already exist: `cdad_packet.py:1760–1774,1849–1879`.
- Closure writes `idle`/`null`; opening applies `_validate_idle_coherence`. Status does not consistently apply that same precondition. See `cdad_packet.py:686–722,7293–7312,9195–9211,9495–9518,9990–10033`.
- Closing guidance instead says `done`/`null`: `stage-5-merge.md:187` and `skills/cdad-epic/references/feature-handoff.md:60–64`.

These findings bound the affected behavior; they do not establish compatibility for unexamined surfaces.

## Contract

### Promise A — The owner’s decisions survive dialogue and handoff faithfully

**PC-1 — Responsibilities.** Canonical role instructions and effective consumers assign functional dialogue to the orchestrator and targeted technical consultation to the architect. Findings and owner-facing questions return through the orchestrator. Consultation is triggered by consequential uncertainty or missing evidence, not every question. The architect remains read-only and returns an unapproved draft as final text.

The orchestrator may record dialogue and materialize reports, but does not perform technical investigation, author or alter the architect’s report or specification content, write tests/code, or conduct independent review. Its existing other authorized materializations remain allowed. The approval prohibition retains only the existing delegation exception, defined once in stage-2 §2.3.

**PC-2 — Recoverable context.** Before drafting, `docs/specs/<feature>/discovery.md` contains an attributed **Dialogue context** section. If necessary, it exists before the technical report arrives; that report is later materialized unaltered in its own section.

Entries distinguish the six accepted classes: confirmed decision, proposal, unresolved item, conflicting statements, technical evidence and correction. Authority, provenance, affected fragment, supersession and next action are recoverable. An unauthorized correction supersedes nothing. Authorized corrections preserve the old entry but prevent its use as a current requirement; affected prior outputs are flagged for re-check.

A fresh architect receives current decisions, qualified evidence, proposals, unresolved items and conflicts without needing the owner’s conversation. The reviewer receives the complete attributed context, with superseded entries identified. `current_decisions` remains governing-project-decision transport, not the dialogue record.

**PC-3 — Readiness.** Brainstorm re-entry checks the accepted R1–R5 conditions: consequential choices answered or explicitly excluded; no unconfirmed extension of answers; authorized corrections reflected; technical uncertainty investigated, bounded or blocking; and recoverable drafting inputs.

Partial answers, silence and an unaccepted default do not supply missing consent. Open consequential choices and conflicts block readiness for the affected commitment. Technical assumptions remain visible and go to targeted investigation. `READY FOR DRAFT` is the consultation’s supported summary, not approval or a substitute for the orchestrator’s readiness check.

**Verification — contextual review with observed application.** An independent reviewer contrasts candidate instructions and relevant effective consumers with the accepted design and protected sources. PC-11 supplies observed fidelity evidence.

**Acceptance/evidence:** attributable findings establish actionable responsibilities, faithful records and correct stopping conditions, without unresolved blocking contradictions. Include source/product versions and transcript/artifact locators.

**Limits:** textual review cannot establish universal agent compliance; structural checks alone do not establish fidelity.

### Promise B — A passing draft cannot procedurally bypass independent review

**PC-4.** Architect draft re-entry routes a passing draft to independent review, materializes the verdict, routes blockers and obtains focused re-review when the design changes. Only then does it request approval.

The alternative remains the owner’s explicit exemption, registered with `exempted_by`, `delegated`, `requested_by` and `reason` in the approval’s same `stage_history` entry. An absent or incomplete exemption does not authorize bypass. Answers, readiness, verdict, exemption and approval remain distinct events. Approval authority and contract/plan pins retain existing requirements.

This is a correction to instructions and supervised routing—not a new automatic CLI review-enforcement mechanism.

**Verification — contextual review plus observed route exercises.** Exercise candidate canonical references and generated orchestrator instructions through:

- The reviewed route, including verdict and blocker handling before approval.
- The properly exempted route, with all four fields and no fabricated verdict.
- Attempted bypass without an exemption or with an incomplete exemption, including each required-field omission.

These are behavioral observations, not keyword assertions or a synthetic route engine. Existing executable exemption-recording and approval-pin regressions remain applicable.

**Acceptance/evidence:** an independent reviewer locates the actual actions and resulting records, establishes the required order, and finds no accepted unauthorized bypass.

**Limits:** compliant agent behavior does not prove the CLI rejects a manually invoked gate; that enforcement is not promised.

### Promise C — Targeted consultation is deliverable without weakening packet integrity

**PC-5 — Single consultation delivery.** Architect/brainstorm admits exactly `role-report`; draft kinds are rejected for that substage. Native dispatch and the OpenCode adapter derive the same single delivery kind, which the existing result/materialization path accepts. Other role/substage permissions remain unchanged.

The test-writer deliberately changes the obsolete rejection expectation in `tests/test_006_005_u7_scribe_role_report.py:699–709`, with its reason recorded; the other rejected role combinations remain protected.

**PC-6 — Frozen packets.** Editing live instructions does not change the canonical rendering of an existing frozen publication. A new publication captures the changed bytes with matching digests. Historical packets—including this assignment—are not rewritten. The orchestrator records affected in-flight packets left on older instructions and uses new publications for candidate work.

“Publication” here means operational task-packet publication, not authorization to publish or deploy the software.

**Verification — executable.** Independent test-writing before implementation for PC-5; reuse/extend existing frozen-reception tests for PC-6. Exercise real dispatch-kind derivation, result acceptance and old/new publication behavior in disposable project fixtures.

**Acceptance/evidence:** focused tests pass with exact commands, output, revision and relevant byte/digest comparisons; unchanged role-axis controls remain satisfactory.

**Limits:** transport acceptance and frozen-byte equality establish neither semantic correctness nor observed dialogue success.

### Promise D — Closure and next-unit orientation agree

**PC-7.** Legitimate closure leaves `current_stage: idle` and `active_feature: null`; closing guidance and epic handoff agree with that transition.

Status applies the same resting-coherence criterion as `open-unit` before recommending opening. With otherwise eligible configuration and dependencies, a correct closure permits opening the next queued unit. `done`/`null` produces a diagnosis, not an `open-unit` recommendation or an at-rest claim. Preserve existing active/suspended/pending-work distinctions and status output limits.

**Verification — combined.** Black-box executable closure → status → opening regression, plus the incoherent-state negative case; contextual review of closing and handoff guidance.

**Acceptance/evidence:** the recommended opening succeeds in the eligible fixture; the incoherent fixture receives consistent diagnosis without state mutation by status. Guidance matches those outcomes.

**Limits:** coherence is necessary, not a guarantee that unrelated authority, dependency or configuration requirements are satisfied. No repair of this workspace’s state is included.

### Promise E — Supported consumers tell the same, proportionate story

**PC-8 — Lightweight/domain applicability.** A trivial normal-cycle feature retains applicable dialogue, readiness, review-or-exemption, approval and role-separation requirements with shorter artifacts. Standalone bounded work records decisions and actual verification in its minimal artifact, without claiming cycle gates it did not execute. It does not evade verification required by its promised property.

“CDAD light” is explanatory, not a third protocol. Remove contradictory optional-review/partial-isolation wording for normal-cycle work and point to authoritative references. Odoo technical questions stay with the architect; owner-side SPoC/PL questions return through the orchestrator. No new Odoo addon or test environment is required.

**PC-9 — Effective delivery.** Reconcile canonical owners and affected consumers identified by the accepted activation map: role sources, stage references, re-entry, packet sources, legacy handoffs, generator metadata, generic/inherited domain agents, lightweight guidance and explanatory pointers. Generate declared outputs; do not hand-edit agents.

Candidate task packets use the changed sources. Record coverage, versions and unchanged historical publications. Retain relevant generation, rendering, materialization, inventory and distribution protection.

**PC-10 — Verification discipline.** Preserve 019-003: independent sufficiency review before approval unless validly exempted; approved acceptance fixed before production; independent tests before pending executable implementation; contextual independent review after semantic production; both for mixed commitments. No fabricated RED for semantic fidelity, new comprehension-reader role, pre-production checklist or test quota.

Acceptance distinguishes supporting, failed, missing, contradictory and unverifiable evidence. Producer-controlled changes to acceptance inputs or verifiers are prohibited.

**Verification — combined.** Contextual independent review establishes coherence and preserved duties; existing applicable generation/rendering/distribution and inventory checks establish mechanical delivery.

**Acceptance/evidence:** no unresolved blocking inconsistency across examined effective routes; recorded generated-output comparisons, selected regression results and live-inventory validation. Evidence may serve multiple postconditions.

**Limits:** delivery checks do not prove comprehension; this is bounded coverage, not certification of every consumer or runtime.

### Promise F — Acceptance includes actual use, not illustrative success

**PC-11.** After candidate activation and consumer generation/new packet publication, execute the accepted `operating-design/acceptance-protocol-019-002.md` without weakening it.

Before execution, the orchestrator declares and protects scenario inputs outside the producer’s scope, recording identifiers and digests. Record actual instruction versions, repository commit, effective-file hashes, packet identities/frozen digests, sessions and recoverable transcripts.

Observe the complete J1–J7 journey:

**need → functional dialogue → consequential targeted architect consultation → recorded decisions → readiness → unapproved draft → independent draft review.**

Additionally, obtain observed evidence for every required case:

- C1 partial answer without invented remainder.
- C2 unaccepted default remaining a proposal.
- C3 authorized correction governing the resulting handoff or draft, with superseded provenance retained.
- C4 unresolved consequential choice preventing premature readiness.
- C5 visible technical uncertainty routed to investigation and subsequently treated according to evidence, explicit limitation or blocker.

One execution may cover several cases; additional executions fill missing coverage. A blocked outcome can establish a case but cannot replace the complete journey. J8 approval is not simulated or required by this protocol.

**Verification — contextual independent review of real-agent observations.** The reviewer—not the producer—compares each case’s protected input, actual response and resulting treatment with the protocol.

**Acceptance/evidence:** J1–J7 and all C1–C5 have recoverable observed evidence and satisfactory independent assessment. Preserve failed runs; reruns receive new records. Separate observations/semantic review from structural test records.

**Limits:** no claim of deployment, universal compliance or unobserved-runtime compatibility. An unobserved, failed or unrecoverable required case blocks accreditation; declaring that limitation does not satisfy it.

## Verifiable invariants

- No role approves its own proposal or performs its independent review.
- Only attributed current decisions govern drafting; proposals, silence and superseded entries do not.
- Producers cannot edit protected contracts, acceptance inputs or verifiers.
- Historical packets and evidence remain intact.
- No test, review, observation or approval is reported as performed without its evidence.

These are verification constraints, not an automatic requirement for randomized property tests.

## Overall acceptance

Accept only after all PCs have their declared evidence, applicable checks are satisfactory, independent review leaves no unresolved blocker, PC-11 is observed, and the authorized approver explicitly accepts the result. Required missing evidence prevents acceptance.

Apply the existing test-evidence policy; this draft grants no suite waiver.

## deferred-hardening

- Universal agent-compliance/runtime benchmark: not established by bounded observations.
- Automatic semantic oracle or CLI review-gate enforcement: not justified; preserve supervised routing.
- Exhaustive unrelated regression/consumer cleanup: outside this bounded delta; retain relevant protection and existing closure policy.
- Installation/deployment and diagnosis of 019-003’s unresolved installed `--check` result: separately authorized operational work, not evidence that this candidate is effective.

None defers a committed postcondition.

---

# Draft `plan.md`

# Effective discovery instructions — implementation plan

**Status:** UNAPPROVED DRAFT; approve together with the specification.

**Global constraints:** No installation, deployment, public publication, live-state repair, new role, packet/state field or gate. Preserve role independence, protected acceptance inputs and historical evidence.

## Feature result and interfaces

Consumes the approved 019-001 operating design and 019-003 verification strategy. Produces coherent candidate instructions, supported consultation delivery, consistent resting-state orientation, and independently assessed observed-use evidence.

Acceptance-of-use recipe: spec Promises A–F and the accepted `acceptance-protocol-019-002.md`. Contract is drafted by the architect and independently reviewed; integration is delivered by the implementer and checked independently; use is coordinated by the orchestrator and evaluated by a separate reviewer.

Existing executable interfaces:

- `_allowed_kinds(role: str, substage: str) -> frozenset[str]`
- `derive_artifact_kind(role: Any, substage: Any) -> str`
- `_derived_artifact_kind(role: str, substage: str) -> str`
- `cdad_packet.py register-transition`, `status`, `open-unit`, `render`, `prepare`
- Existing `make agents` regeneration, declared in `Makefile:10–18`.

No new API or schema is proposed.

## T1 — Deliver the mediated discovery path

**Covers:** PC-1–6, PC-8–10.

**Modify:**  
`sources/roles/{architect,orchestrator}.md`;  
`scripts/cdad-generate.py`;  
`skills/cdad-cycle/scripts/cdad_result.py`;  
affected architect packet role/substage sources;  
`skills/cdad-cycle/references/{stage-1-discovery,stage-2-specification,re-entry,handoff-prompts}.md`;  
`skills/cdad-spec-and-test/SKILL.md`;  
`skills/odoo-architect/SKILL.md`;  
`README.md`; `CDAD_metodologia.md`.

Regenerate affected generic/domain agents and manifests through declared generation. Update live suite inventory/mapping for actual test changes.

**Test:** add `tests/test_019_002_discovery_delivery.py` for the executable consultation delta; deliberately update the obsolete architect/brainstorm expectation in `test_006_005_u7_scribe_role_report.py`. Test-writer owns test edits; implementer never edits tests.

**Contract:** deliver a consultation as one report without permitting brainstorm drafts or widening other role axes; deliver coherent instructions to normal, lightweight, packet and legacy consumers; retain frozen historical publication behavior.

**Validation:** independent RED/GREEN for delivery; contextual review for instruction fidelity. Existing relevant frozen-reception, role-report materialization, review/exemption, generation, packet-rendering and consumer regressions provide proportional protection. Observed route exercises belong to T3, not a word-matching substitute.

## T2 — Deliver coherent closure orientation

**Covers:** PC-7 and its PC-9–10 delivery obligations.

**Modify:**  
`skills/cdad-cycle/scripts/cdad_packet.py`;  
`skills/cdad-cycle/references/stage-5-merge.md`;  
`skills/cdad-epic/references/feature-handoff.md`.

**Test:** add `tests/test_019_002_resting_orientation.py`; update live inventory/mapping.

**Contract:** existing closure/status/opening interfaces agree on resting coherence without new state vocabulary or workspace repair.

**Validation:** independent black-box RED/GREEN over disposable fixtures; relevant idle, compact-status, closure and open-unit regressions; contextual review of guidance.

## T3 — Establish observed acceptance and close evidence

**Covers:** PC-4, PC-11 and integrated acceptance of PC-1–10.

Depends on T1 and T2. The orchestrator prepares protected inputs and coordinates actual candidate-agent execution; the independent reviewer evaluates the observations. The implementer does not own the scenario inputs or verdict.

Resolve before detailing execution: how the selected runtime consumes repository candidate agents, references and newly published packets **without an unauthorized installation**. No viable candidate-runtime path has yet been selected or demonstrated; execution feasibility remains unresolved. The orchestrator must establish that path and recover effective versions rather than assume installed instructions match. If it requires installation or deployment, stop and obtain separate owner authority; this plan grants none. Do not substitute hypothetical transcripts or waive PC-11.

## Canonical task block

```plan-tasks
{
  "validation_strategy": "Independent tests before executable implementation; contextual independent review for semantic promises; proportional affected regression and existing delivery/inventory protection. Final acceptance includes spec PC-11 and observed PC-4 routes. Apply the existing Test evidence policy; no waiver is granted.",
  "tasks": [
    {
      "id": "T1",
      "objective": "Deliver the mediated discovery path described in T1.",
      "produce": [
        {
          "artifact": "candidate-discovery-instructions-and-delivery",
          "contract": "019-002-spec-PC1-PC6-PC8-PC10"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": [
        "sources/roles/architect.md",
        "sources/roles/orchestrator.md",
        "scripts/cdad-generate.py",
        "skills/cdad-cycle/scripts/cdad_result.py",
        "skills/cdad-cycle/packets/roles/architect.md",
        "skills/cdad-cycle/packets/substages/architect-brainstorm.md",
        "skills/cdad-cycle/references/stage-1-discovery.md",
        "skills/cdad-cycle/references/stage-2-specification.md",
        "skills/cdad-cycle/references/re-entry.md",
        "skills/cdad-cycle/references/handoff-prompts.md",
        "skills/cdad-spec-and-test/SKILL.md",
        "skills/odoo-architect/SKILL.md",
        "README.md",
        "CDAD_metodologia.md",
        "agents/cdad-architect.md",
        "agents/cdad-architect-odoo.md",
        "agents/cdad-orchestrator.md",
        "agents/claude-code/cdad-architect.md",
        "agents/claude-code/cdad-architect-odoo.md",
        "agents/claude-code/cdad-orchestrator.md",
        "build/staging/agents/opencode/cdad-architect.md",
        "build/staging/agents/opencode/cdad-architect-odoo.md",
        "build/staging/agents/opencode/cdad-orchestrator.md",
        "build/staging/agents/claude-code/cdad-architect.md",
        "build/staging/agents/claude-code/cdad-architect-odoo.md",
        "build/staging/agents/claude-code/cdad-orchestrator.md",
        "build/staging/manifest.json",
        "docs/specs/008-002-suite-by-capability/suite-inventory.json",
        "docs/specs/008-002-suite-by-capability/pc-map.json",
        "tests/test_019_002_discovery_delivery.py",
        "tests/test_006_005_u7_scribe_role_report.py"
      ],
      "focal_tests": ["tests/test_019_002_discovery_delivery.py"],
      "regressions": [
        "tests/test_006_005_u7_scribe_role_report.py",
        "tests/test_005_007_t4_architect_report_materialization.py",
        "tests/test_015_001_frozen_reception.py",
        "tests/test_006_006_u3_review_route_and_gate.py",
        "tests/test_006_006_u5_exemption_record.py",
        "tests/test_cdad_generate.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packet_consumers.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "test-writer: executable oracles; implementer: candidate product; reviewer: contextual fidelity"
    },
    {
      "id": "T2",
      "objective": "Deliver coherent closure, status and opening orientation described in T2.",
      "produce": [
        {
          "artifact": "candidate-resting-orientation",
          "contract": "019-002-spec-PC7"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": [
        "skills/cdad-cycle/scripts/cdad_packet.py",
        "skills/cdad-cycle/references/stage-5-merge.md",
        "skills/cdad-epic/references/feature-handoff.md",
        "tests/test_019_002_resting_orientation.py"
      ],
      "focal_tests": ["tests/test_019_002_resting_orientation.py"],
      "regressions": [
        "tests/test_005_001_t3_idle.py",
        "tests/test_005_003_t1_compact_view.py",
        "tests/test_005_007_t3_open_unit.py",
        "tests/test_005_012_t3_closure_dispatch_resolution.py"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "test-writer: black-box oracles; implementer: product; reviewer: guidance and integration"
    },
    {
      "id": "T3",
      "detail": "planned",
      "objective": "Establish PC-4 route observations, PC-11 complete journey and all five cases, then integrate acceptance evidence.",
      "depends_on": ["T1", "T2"],
      "uncertainty": "Candidate-runtime loading and effective-version provenance without installation.",
      "owner": "orchestrator, with independent reviewer",
      "resolves_when": "The candidate invocation, protected inputs, scopes and evidence locations are declared before execution and the actual effective instruction versions can be recovered."
    }
  ]
}
```

T1’s canonical files list is the exact task-path declaration: source changes, affected declared generated outputs, live inventory/mapping and the two test paths. The list is not a shared write scope. Materialized assignments separate test-writer-owned tests from implementer-owned sources/generated outputs; inventory/mapping updates follow the existing live-inventory ownership contract. Regeneration does not authorize unrelated changes or hand-editing agents. Any necessary path outside this declaration returns for explicit re-scoping before editing.

## Open verification items

- **Execution-blocking until resolved:** candidate-runtime loading and provenance for T3.
- **Required future evidence:** reviewed/exempted/invalid-exemption route observations, complete J1–J7, and C1–C5. None has been performed by this draft.
- **Outside this commitment:** 019-003’s installed-check diagnosis. It cannot be used as evidence for or against unexecuted candidate delivery.

---

## Evidence and limitations

### Validation performed

The existing validator functions are defined in `skills/cdad-cycle/scripts/cdad_packet.py:5416–5653`. I reproduced the prior failure, then validated the revised full plan-form text in memory with:

- `_plan_tasks_from_contract`
- `_check_plan_tasks`
- `_check_plan_validation_plan`

Output:

```text
Prior plan: plan task 'T1' is missing its per-task validation plan: a non-empty focal_tests (code task) or observable_checks (code-less task) is required (PD-8)
Proposed full plan-form: _plan_tasks_from_contract PASS; _check_plan_tasks PASS; _check_plan_validation_plan PASS
T1: 31 unique exact paths; focal test included; existing source/inventory/generated-consumer/regression paths verified; new focal test intentionally pending
T2 and T3 canonical entries unchanged; all declared focal tests belong to their task files
No files written; validation rc=0
```

The exact focused recheck command, executed from `<repo>`, was:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'
import json, runpy
from pathlib import Path
api = runpy.run_path('skills/cdad-cycle/scripts/cdad_packet.py')
text = Path('docs/specs/019-002-effective-discovery-instructions/architect-draft-005.md').read_text()
plan = text.split('# Draft `plan.md`\n\n', 1)[1].split('\n---\n\n## Evidence and limitations', 1)[0]
files = ['sources/roles/architect.md', 'sources/roles/orchestrator.md', 'scripts/cdad-generate.py', 'skills/cdad-cycle/scripts/cdad_result.py', 'skills/cdad-cycle/packets/roles/architect.md', 'skills/cdad-cycle/packets/substages/architect-brainstorm.md']
files += [f'skills/cdad-cycle/references/{n}.md' for n in ['stage-1-discovery', 'stage-2-specification', 're-entry', 'handoff-prompts']]
files += ['skills/cdad-spec-and-test/SKILL.md', 'skills/odoo-architect/SKILL.md', 'README.md', 'CDAD_metodologia.md']
files += [f'{p}/{n}.md' for p in ['agents', 'agents/claude-code', 'build/staging/agents/opencode', 'build/staging/agents/claude-code'] for n in ['cdad-architect', 'cdad-architect-odoo', 'cdad-orchestrator']]
files += ['build/staging/manifest.json', 'docs/specs/008-002-suite-by-capability/suite-inventory.json', 'docs/specs/008-002-suite-by-capability/pc-map.json', 'tests/test_019_002_discovery_delivery.py', 'tests/test_006_005_u7_scribe_role_report.py']
assert plan.count('"files": []') == 1
plan = plan.replace('"files": []', '"files": ' + json.dumps(files, indent=2).replace('\n', '\n      '))
tasks, strategy = api['_plan_tasks_from_contract'](plan.encode())
api['_check_plan_tasks'](tasks)
api['_check_plan_validation_plan'](tasks, strategy)
print('PASS: complete proposed plan-tasks block; all three existing plan checks; T1 files=31; T1 focal_tests preserved')
PY
printf 'validation rc=%s\n' "$?"
git status --short
git diff --stat
git rev-parse HEAD
```

Output:

```text
PASS: complete proposed plan-tasks block; all three existing plan checks; T1 files=31; T1 focal_tests preserved
validation rc=0
 M docs/.cdad-state.json
 docs/.cdad-state.json | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
12e8111e9f53ac70c712f97d74a17ab20ad4f172
```

The state-file modification was present at intake. No product changes were made.

### Packet validation

Executed:

```sh
python3 scripts/cdad_packet.py validate-request --project-root <repo> --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-006/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root <repo> --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-006/REQUEST.json --packet .cdad/packets/019-002-effective-discovery-instructions-architect-draft-006/PACKET.md

python3 scripts/cdad_packet.py render --project-root <repo> --request .cdad/packets/019-002-effective-discovery-instructions-architect-draft-006/REQUEST.json --route C
```

Request and packet validation returned rc=0 without diagnostics. A subsequent in-memory comparison confirmed complete canonical packet equality and matching Route C metadata.

**Limits:** mechanical plan acceptance does not establish semantic sufficiency, candidate-runtime feasibility or implementation acceptance. No test suite, generation, real-agent exercise, installation or deployment was performed. Independent review and explicit approval remain pending.