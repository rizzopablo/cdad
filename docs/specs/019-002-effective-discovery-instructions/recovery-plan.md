## recovery-plan

**Status:** Approved under <owner>'s explicit HITL delegation for epic 019. Approval and mandatory pre-T8 execution-feasibility condition: `recovery-approval.md`.

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

### Canonical task block

T1–T9 correspond to steps 1–9 above. Postconditions and path-specific restrictions refer exclusively to the unchanged `recovery-spec.md`, not the superseded specification. File declarations describe task scope, not shared editing permission; dispatches retain role separation. Generated-output patterns retain the companion specification’s scope and regeneration restrictions.

```plan-tasks
{
  "validation_strategy": "Use the recovery-spec PC-1-PC-7 verification methods only. Independent RED precedes each executable GREEN; semantic promises use independent contextual review, supported by existing delivery checks and one bounded actual-use exercise. For documentary/evidence tasks, @validation_strategy in focal_tests refers to the task's observable_checks, not a fabricated executable test. Record commands, outputs, revisions and limits; retain separate mechanical and semantic evidence. Focused regression during construction; full tests/ suite and live-inventory validation at epic closure. No installation, publication or historical accreditation.",
  "tasks": [
    {
      "id": "T1",
      "objective": "Reconcile and approve the replacement contract before production, preserving historical evidence.",
      "produce": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "files": [
        "docs/specs/019-002-effective-discovery-instructions/recovery-spec.md",
        "docs/specs/019-002-effective-discovery-instructions/recovery-plan.md",
        "docs/specs/019-002-effective-discovery-instructions/spec.md",
        "docs/specs/019-002-effective-discovery-instructions/plan.md",
        "docs/specs/019-001-discovery-dialogue-contract/operating-design/README.md",
        "docs/epics/epic-019-discovery-dialogue/plan.md"
      ],
      "focal_tests": ["@validation_strategy"],
      "observable_checks": [
        "Independent sufficiency review and explicit approval are recorded through existing procedures before production; amendment and prospective notices preserve original text, pins, receipts and failed observations."
      ],
      "regressions": [],
      "integration_gate": "Independent sufficiency review without unresolved blockers and explicit authorized approval; no retroactive acceptance.",
      "owner": "orchestrator: materialization and records; independent reviewer: sufficiency; authorized approver: approval"
    },
    {
      "id": "T2",
      "objective": "Write independent RED tests for consultation delivery, PC-4 only.",
      "produce": [
        {
          "artifact": "consultation-delivery-red",
          "contract": "recovery-spec:PC-4"
        }
      ],
      "consume": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7",
          "producer": "T1"
        }
      ],
      "depends_on": ["T1"],
      "parallel": [],
      "files": [
        "tests/test_019_002_discovery_delivery.py",
        "tests/test_006_005_u7_scribe_role_report.py"
      ],
      "focal_tests": ["tests/test_019_002_discovery_delivery.py"],
      "regressions": ["tests/test_006_005_u7_scribe_role_report.py"],
      "integration_gate": "Independent PC-4 tests and focused intended failure evidence; replace only the named obsolete expectation and return inventory delta; no implementation read.",
      "owner": "independent test-writer"
    },
    {
      "id": "T3",
      "objective": "Satisfy protected PC-4 tests with the smallest consultation-delivery table change.",
      "produce": [
        {
          "artifact": "consultation-delivery-green",
          "contract": "recovery-spec:PC-4"
        }
      ],
      "consume": [
        {
          "artifact": "consultation-delivery-red",
          "contract": "recovery-spec:PC-4",
          "producer": "T2"
        }
      ],
      "depends_on": ["T2"],
      "parallel": [],
      "files": ["skills/cdad-cycle/scripts/cdad_result.py"],
      "focal_tests": ["tests/test_019_002_discovery_delivery.py"],
      "regressions": [
        "tests/test_006_005_u7_scribe_role_report.py",
        "tests/test_005_007_t4_architect_report_materialization.py"
      ],
      "integration_gate": "PC-4 GREEN and materialization regression evidence; preserve other role/substage controls and protected tests.",
      "owner": "implementer"
    },
    {
      "id": "T4",
      "objective": "Write independent RED tests for executable resting orientation, PC-5 only.",
      "produce": [
        {
          "artifact": "resting-orientation-red",
          "contract": "recovery-spec:PC-5"
        }
      ],
      "consume": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7",
          "producer": "T1"
        }
      ],
      "depends_on": ["T3"],
      "parallel": [],
      "files": ["tests/test_019_002_resting_orientation.py"],
      "focal_tests": ["tests/test_019_002_resting_orientation.py"],
      "regressions": [],
      "integration_gate": "Independent focused RED evidence for closure/status/opening and incoherent-state diagnosis on fixtures; no repair of live project state.",
      "owner": "independent test-writer"
    },
    {
      "id": "T5",
      "objective": "Correct resting orientation using the existing coherence criterion without unrelated projection changes.",
      "produce": [
        {
          "artifact": "resting-orientation-green",
          "contract": "recovery-spec:PC-5"
        }
      ],
      "consume": [
        {
          "artifact": "resting-orientation-red",
          "contract": "recovery-spec:PC-5",
          "producer": "T4"
        }
      ],
      "depends_on": ["T4"],
      "parallel": [],
      "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
      "focal_tests": ["tests/test_019_002_resting_orientation.py"],
      "regressions": [
        "tests/test_005_001_t3_idle.py",
        "tests/test_005_003_t1_compact_view.py",
        "tests/test_005_007_t3_open_unit.py",
        "tests/test_005_012_t3_closure_dispatch_resolution.py"
      ],
      "integration_gate": "PC-5 GREEN and relevant resting/closure regression evidence; status stays read-only and live state remains untouched.",
      "owner": "implementer"
    },
    {
      "id": "T6",
      "objective": "Produce minimal coherent instructions for PCs 1-3 and 6 plus PC-5 guidance, and regenerate affected outputs.",
      "produce": [
        {
          "artifact": "candidate-recovery-instructions",
          "contract": "recovery-spec:PC-1-PC-3-PC-5-PC-6"
        }
      ],
      "consume": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7",
          "producer": "T1"
        }
      ],
      "depends_on": ["T5"],
      "parallel": [],
      "files": [
        "sources/roles/orchestrator.md",
        "sources/roles/architect.md",
        "scripts/cdad-generate.py",
        "skills/cdad-cycle/SKILL.md",
        "skills/cdad-cycle/references/stage-1-discovery.md",
        "skills/cdad-cycle/references/stage-2-specification.md",
        "skills/cdad-cycle/references/re-entry.md",
        "skills/cdad-cycle/references/handoff-prompts.md",
        "skills/cdad-cycle/references/stage-5-merge.md",
        "skills/cdad-cycle/packets/roles/architect.md",
        "skills/cdad-cycle/packets/substages/architect-brainstorm.md",
        "skills/odoo-architect/SKILL.md",
        "skills/cdad-epic/references/feature-handoff.md",
        "CDAD_metodologia.md",
        "build/staging/**",
        "agents/**"
      ],
      "focal_tests": [
        "tests/test_cdad_generate.py",
        "tests/test_role_packet_render.py",
        "tests/test_role_packet_consumers.py"
      ],
      "observable_checks": [
        "Run make agents and inspect generated delta; independently review semantic fidelity in T7, without fabricated RED."
      ],
      "regressions": [
        "tests/test_015_001_frozen_reception.py",
        "tests/test_006_006_u3_review_route_and_gate.py",
        "tests/test_006_006_u5_exemption_record.py"
      ],
      "integration_gate": "Relevant generation/rendering checks pass and output delta is explained; semantic acceptance awaits T7. Preserve recovery-spec path-specific edit limits and frozen packets.",
      "owner": "implementer: production and mechanical checks; independent reviewer: semantic assessment in T7"
    },
    {
      "id": "T7",
      "objective": "Independently assess the candidate against owner sources, retained 019-003 and the approved recovery contract.",
      "produce": [
        {
          "artifact": "candidate-contextual-review",
          "contract": "recovery-spec:PC-1-PC-6"
        }
      ],
      "consume": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7",
          "producer": "T1"
        },
        {
          "artifact": "consultation-delivery-green",
          "contract": "recovery-spec:PC-4",
          "producer": "T3"
        },
        {
          "artifact": "resting-orientation-green",
          "contract": "recovery-spec:PC-5",
          "producer": "T5"
        },
        {
          "artifact": "candidate-recovery-instructions",
          "contract": "recovery-spec:PC-1-PC-3-PC-5-PC-6",
          "producer": "T6"
        }
      ],
      "depends_on": ["T1", "T3", "T5", "T6"],
      "parallel": [],
      "files": [],
      "observable_checks": [
        "Review effective packet, legacy, generated, lightweight and affected Odoo routes for fidelity and consistency; verify restrictions were removed, not relocated; return substantive corrections to the producer."
      ],
      "regressions": [],
      "integration_gate": "Independent contextual report with source locators, findings and limits; no unresolved blocking contradiction before actual-use acceptance.",
      "owner": "independent reviewer; orchestrator materializes unchanged report"
    },
    {
      "id": "T8",
      "objective": "Execute and independently assess one bounded PC-7 actual-use journey with candidate sessions and new packets.",
      "produce": [
        {
          "artifact": "actual-use-evidence-and-assessment",
          "contract": "recovery-spec:PC-7"
        }
      ],
      "consume": [
        {
          "artifact": "reconciled-recovery-contract",
          "contract": "recovery-spec:PC-1-PC-7",
          "producer": "T1"
        },
        {
          "artifact": "candidate-contextual-review",
          "contract": "recovery-spec:PC-1-PC-6",
          "producer": "T7"
        }
      ],
      "depends_on": ["T7"],
      "parallel": [],
      "files": [".cdad/orchestration/epic-019/recovery-exercise/"],
      "focal_tests": ["@validation_strategy"],
      "observable_checks": [
        "Declare protected exercise inputs before execution; recover candidate/effective instruction versions, packet identities, actual transcripts and artifacts for the PC-7 journey and decision conditions; independent reviewer assesses fidelity, preserves failures and declares limits."
      ],
      "regressions": [],
      "integration_gate": "One completed PC-7 journey independently assessed as faithful; missing evidence stays missing, demonstrated defects return to producers proportionally, and no installation authority is inferred.",
      "owner": "orchestrator: coordination and protected records; candidate roles: actual execution; independent reviewer: assessment"
    },
    {
      "id": "T9",
      "objective": "Close recovery evidence with live inventory/map deltas and separate mechanical and semantic records.",
      "produce": [
        {
          "artifact": "recovery-closure-evidence",
          "contract": "recovery-spec:acceptance-and-invariants"
        }
      ],
      "consume": [
        {
          "artifact": "candidate-contextual-review",
          "contract": "recovery-spec:PC-1-PC-6",
          "producer": "T7"
        },
        {
          "artifact": "actual-use-evidence-and-assessment",
          "contract": "recovery-spec:PC-7",
          "producer": "T8"
        }
      ],
      "depends_on": ["T8"],
      "parallel": [],
      "files": [
        "docs/specs/008-002-suite-by-capability/suite-inventory.json",
        "docs/specs/008-002-suite-by-capability/pc-map.json"
      ],
      "focal_tests": ["python3 scripts/cdad-suite.py validate"],
      "observable_checks": [
        "Materialize inventory/map deltas through existing ownership; record focal regression and independent semantic/exercise evidence separately, including missing and failed evidence."
      ],
      "regressions": [
        "At epic closure: PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests"
      ],
      "integration_gate": "Required PC-1-PC-7 evidence and independent review without unresolved blockers, plus explicit authorized acceptance; record full-suite output, exit status, candidate/test versions and environment at epic closure. No installation or publication.",
      "owner": "orchestrator: inventory/evidence integration and authorized suite run; independent reviewer: assessment; authorized approver: acceptance"
    }
  ]
}
```

### Architect evidence

- **Intake:** Route C validated. Identification and contract digest matched; execution context is v2; all **7,425 bytes** of the published packet matched canonical render.
- **Correction:** Added machine-readable metadata for the existing nine steps. Their original prose was preserved byte-for-byte in the in-memory validation candidate. `recovery-spec.md` was not changed.
- **Format sources:** Existing `plan.md` §“Canonical task block”; planning contract §4.1; installed `cdad_packet.py:5416–5653`. Installed and repository validator files had identical SHA-256: `1f48f326f5f28dd1d82d377f0256808364e8d7f22274d999297ddcbba0923c7f`.
- **Commands:** Exact shell bodies and complete outputs are retained in this dispatch’s tool transcript. Intake used `validate-request`, `validate-packet`, `render --route C` and full-render byte comparison. The `python3 -B -` in-memory check invoked `_plan_tasks_from_contract`, `_check_plan_tasks` and `_check_plan_validation_plan` from both installed and repository validators.
- **Structural-check output:**
  ```text
  installed: original expected rejection: draft plan is missing the required plan-tasks block: the per-task validation plan is part of the plan (PD-8)
  installed: corrected block parse, dependency/artifact checks and per-task validation PASS (9 tasks)
  repository: original expected rejection: draft plan is missing the required plan-tasks block: the per-task validation plan is part of the plan (PD-8)
  repository: corrected block parse, dependency/artifact checks and per-task validation PASS (9 tasks)
  ```
- **Repository evidence:** `git rev-parse HEAD` returned `c29ef97cea79ebd603491f62dae99bed0bcf05f9`. `git diff --quiet bc922c04 -- sources agents skills scripts tests install.sh build` returned **0**. Initial and final status showed the same pre-existing state modification and three untracked recovery documents.
- **Unchanged companion SHA-256:** `b7195c04c27bcccad1249d7fd1c2d25b27845a82077dc6390068fbf87f21dc1f`.
- **Files modified / commits created / approvals issued:** None.
- **Limits:** Structural validation is not independent plan review, publication evidence or feature acceptance. No product tests, actual-use exercise or complete suite were run.
