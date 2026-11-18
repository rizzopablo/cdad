# Plan draft

**Feature:** `019-005-bounded-review-cycles`  
**Version:** `draft-001`  
**Status:** Pending independent review and approval.

## Feature record

**Result:** coherent bounded-correction instructions, effective consumers and a bounded observed application.

**Coverage:** promises A–E, PC-1–PC-15, including the self-contained dispatch rule added by amendment 001.

**Deferred work:** specification’s `deferred-hardening`, unchanged.

**Consumes:** the approved specification, admitted decisions and existing generation/verification contracts.

**Produces:** `bounded-review-instructions-v1`, consumed by architects, orchestrators, review/audit roles and epic planning; `bounded-round-trajectory-v1` evidence, consumed by independent review and approval.

### Global constraints

- Instruction-only behavior: no new CLI operation, flag, schema field, counter file or parallel ledger.
- Preserve role separation, independent verification, existing approval authority and protected acceptance inputs.
- Resolve methodology paths through the existing layout contract; do not migrate historical records.
- Change canonical sources and regenerate affected derived agents; do not hand-edit generated agents.
- No installation, deployment or publication is authorized.

## One implementation batch

The canonical rule and its actionable consumers form one batch. Separating them into sequentially accepted features would leave contradictory directions usable between changes and would add coordination without an independently useful result.

### Files

**Create**

- `skills/cdad-cycle/references/bounded-review-cycles.md`

**Modify — canonical references and templates**

- `skills/cdad-cycle/references/stage-2-specification.md`
- `skills/cdad-cycle/references/stage-3-tdd.md`
- `skills/cdad-cycle/references/stage-4-review.md`
- `skills/cdad-cycle/references/re-entry.md`
- `skills/cdad-cycle/references/handoff-prompts.md`
- `skills/cdad-cycle/assets/spec-template/spec.md`
- `skills/cdad-epic/SKILL.md`
- `skills/cdad-epic/assets/epic-plan-template.md`
- `skills/cdad-epic/assets/epic-closure-template.md`
- `skills/cdad-spec-and-test/SKILL.md`

**Modify — affected declaration and operational consumers**

- `sources/roles/architect.md`
- `sources/roles/orchestrator.md`
- `skills/cdad-cycle/packets/roles/architect.md`
- `skills/cdad-cycle/packets/substages/architect-draft.md`
- `skills/cdad-cycle/packets/substages/reviewer-plan-review.md`
- `skills/cdad-cycle/packets/substages/reviewer-review.md`
- `skills/cdad-cycle/packets/substages/test-writer-audit.md`
- `skills/cdad-cycle/packets/substages/test-writer-post-audit.md`
- `skills/cdad-cycle/packets/substages/implementer-review-fix.md`

**Regenerate**

- Affected `agents/cdad-*.md`
- Affected `agents/claude-code/cdad-*.md`
- Derived `build/staging` outputs and manifest, through the existing generator.

Regenerated output membership is determined by the declared generator, not by hand-selecting files. Unchanged consumers receive an explicit inventory exclusion where relevant.

**Protected acceptance material**

The approved specification, plan, scenario acceptance conditions and independent reports remain outside implementer write scope. The orchestrator materializes role reports and exercise evidence under this feature’s methodological evidence directory. The implementer does not produce its own acceptance verdict.

### Validation ownership

- **Implementer:** edits product instructions, runs declared regeneration and reports distribution-check results.
- **Test-writer:** assesses existing executable protection and any required updates under normal isolation; no test is manufactured to prove semantic fidelity. Any justified existing-test update stays in `tests/` and follows AUDIT/POST-AUDIT.
- **Orchestrator:** prepares and conducts the bounded exercise, registers ordinary decisions and preserves actual role inputs/outputs.
- **Independent reviewer:** evaluates all promises contextually, including actual effective inputs and exercise results; performs applicable closing re-review after corrections.
- **Competent approver:** adopts the specification/plan and makes authorized acceptance decisions.

```plan-tasks
{
  "validation_strategy": "Semantic-only feature. Independently review PC-1 through PC-15 against the approved contract, admitted sources, canonical owner and actual effective consumers. Execute bounded-round-trajectory-v1 with candidate instructions and preserve actual role inputs, outputs, ordinary history references, consumption and adjudication. Run make agents through the implementer; run existing packet/render/distribution regressions selected below, adapting existing guards only through the independent test-writer when approved audit dispositions require it. Follow skills/cdad-cycle/references/stage-3-tdd.md Test evidence policy; do not infer semantic success from executable checks or claim an unexecuted complete suite.",
  "tasks": [
    {
      "id": "T1",
      "objective": "Deliver and independently verify coherent bounded correction instructions and their effective normal, lightweight and epic consumers.",
      "produce": [
        {
          "artifact": "bounded-review-instructions",
          "contract": "bounded-review-instructions-v1"
        },
        {
          "artifact": "bounded-review-use-evidence",
          "contract": "bounded-round-trajectory-v1"
        }
      ],
      "consume": [],
      "depends_on": [],
      "parallel": [],
      "detail": "next",
      "observable_checks": [
        "Independent contextual review establishes promises A-E and PC-1 through PC-15, including the sender and receiver boundaries of the self-contained dispatch rule, including canonical ownership and no conflicting actionable consumers.",
        "bounded-round-trajectory-v1 preserves consumption through changed dispatch identity, stops after final verification at exhaustion and distinguishes a committed breach from acceptable optional residue.",
        "An independent receiving session reconstructs consumption and the next authorized action using only the ordinary records and candidate handoff.",
        "The accumulation disposition requires amendment for new membership and rejects a recursive successor unit.",
        "A bounded fresh-session check confirms a role resolves and uses the CLI named by the dispatch alone, and reports a gap instead of improvising when a required resource lies outside its scopes.",
        "The dispatch and handoff wording require the locator rather than merely recommending it.",
        "Diff inspection confirms no new CLI/schema/counter mechanism and no hand-edited derived agents."
      ],
      "regressions": [
        "Implementer: make agents",
        "Implementer or authorized test-writer: python3 -m pytest tests/test_role_packets.py tests/test_role_packet_render.py tests/test_role_packet_consumers.py tests/test_role_packet_review_regressions.py tests/test_packet_prepare.py -q",
        "Implementer: make validate; report installation-drift findings without deploying to eliminate them"
      ],
      "integration_gate": "@validation_strategy",
      "owner": "Product and regeneration: implementer; existing-test audit or corrections: independent test-writer; observed trajectory and ordinary records: orchestrator; contextual acceptance and closing re-review: independent reviewer; approval: competent authority"
    }
  ]
}
```

The `files` list identifies planned outputs across roles, not collective write permission. Each dispatch grants only that role’s actual scope. Conventional `docs/` evidence paths follow the existing layout resolver.
