# Effective discovery instructions — implementation plan

**Status:** Approved together with the specification by the CDAD orchestrator (agent-delegated, explicit request from <owner> for epic 019 on 2026-11-15) on 2026-11-15. Approval provenance recovery: `approval-recovery-decision.md` and `approval-recovery-review.md`.

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


## Prospective recovery supersession

The owner selected restoration to closure of 019-003. For subsequent 019-002 work, `recovery-spec.md`, `recovery-plan.md` and `recovery-approval.md` replace this document’s prospective obligations. Historical approvals and failed or incomplete evidence remain unchanged; supersession is not acceptance of the old candidate.
