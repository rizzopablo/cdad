# Operating design — 019-001 discovery dialogue

**Status: documentary proposal. It is not an activation.** Current role powers,
role sources, packet instructions and executable behaviour stay in force until the
separately approved activation delivered by feature `019-002-effective-discovery-instructions`.

Not yet recorded here: the independent semantic review (PC-12), the authorized
approver's acceptance of this design, and the decisions D1–D5 of the approved
specification. Those are pending by design (see `verification.md`).

## Revisions and inputs

| Item | Identity |
|---|---|
| Repository revision examined for every locator in this product | `64aa4670` (HEAD at examination; locators written `path:Lx-Ly`, all at this revision) |
| Revision examined by discovery | `265174993b4213be9a96545578016657bc8b09ba` |
| Surfaces cited by discovery vs HEAD | `git diff --stat 265174993b…64aa4670` over the surfaces cited by discovery (the role, reference, packet, script, generator, skill, test and README paths it names) shows no change to them. Discovery's line numbers were re-read at `64aa4670` before use. That diff does not cover two surfaces this product relies on, which were re-read at HEAD independently of it: `skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md` and `docs/epics/epic-019-discovery-dialogue/execution.md`. |
| Approved amended specification | `docs/specs/019-001-discovery-dialogue-contract/spec.md`, SHA-256 `1e50141c91b84a309be92d115c8df025a1fb5e138dc0ba35b2c13f74bd864853` (amendment commit `e8b824b3`) |
| Admitted discovery | `docs/specs/019-001-discovery-dialogue-contract/discovery.md`, SHA-256 `6d77f4ba7c342bdf7c99f5b8b8a506eed71a021ebc035456be302a090357bb43` (recomputed; matches the spec) |
| Protected review checklist (PC-1..PC-12) | `docs/specs/019-001-discovery-dialogue-contract/review-checklist.md`, SHA-256 `41161a34802e0a4945de042f03b2e65f146c827342d0433079924f3d94a9a83f`; materialization record outside this product: `docs/epics/epic-019-discovery-dialogue/checklist-001-materialize.json` |

The approved amended specification says that for this documentary unit
independent semantic review is the verification. No automated test, RED/GREEN
phase or test-writer participation applies. The older `verification-blocker.md`
predates that amendment and is superseded by it. The owner decision that fixes
this documentary-only unit is recorded at `docs/epics/epic-019-discovery-dialogue/execution.md:16-28`.

## Index: each postcondition to its section

The index gives the reviewer locators. It is not a result. No PC is marked as
satisfied here.

| PC | Subject | Section |
|---|---|---|
| PC-1 | Named responsibilities and mediated round trip | `roles-and-dialogue.md` §1–§2 |
| PC-2 | Role-boundary changes needed for activation | `roles-and-dialogue.md` §3 |
| PC-3 | Meaning preserved in handoffs; corrections | `handoff-fidelity.md` §1–§5 |
| PC-4 | Fresh-session recovery worked example | `handoff-fidelity.md` §6 |
| PC-5 | Readiness without invented agreement | `readiness-and-approval.md` §1–§2 |
| PC-6 | Draft, independent review and approval are separate | `readiness-and-approval.md` §3 |
| PC-7 | Proportionate lightweight paths | `lightweight-paths.md` |
| PC-8 | Canonical owners and effective consumers | `activation-map.md` |
| PC-9 | Bounded activation handoff to 019-002 | `activation-handoff-019-002.md` |
| PC-10 | Illustrative examples for every committed behaviour | `examples.md` |
| PC-11 | Observed 019-002 acceptance protocol | `acceptance-protocol-019-002.md` |
| PC-12 | Independent semantic verification and closure | `verification.md` |

## Proposed decisions

D1–D5 of the specification are **proposals**. They need explicit acceptance by the
authorized approver; this product does not treat them as approved. Where a section
describes a rule, it describes the proposed rule.

- D1 one functional interlocutor (orchestrator), bounded technical delegation to the architect.
- D2 reuse an attributed dialogue-context section; no new dialogue subsystem.
- D3 readiness is checked, not inferred from conversation length.
- D4 shared fidelity rules, proportionate ceremony for lightweight paths.
- D5 keep architect brainstorm as a targeted technical-consultation path, with its delivery incompatibility explicitly handed to 019-002.

## Files

- `roles-and-dialogue.md` — roles, round trip, boundary deltas.
- `handoff-fidelity.md` — handoff classes, format, corrections, fresh-session example.
- `readiness-and-approval.md` — readiness checks, signal routing, distinct events.
- `lightweight-paths.md` — the three lightweight surfaces and their resolved applicability.
- `activation-map.md` — rule → canonical owner → consumers → incompatibility → reconciliation.
- `activation-handoff-019-002.md` — the four executable corrections, the canonical text deltas (item 5), and their regression obligations.
- `examples.md` — illustrative examples. They are **not** transcripts or evidence of agent compliance.
- `acceptance-protocol-019-002.md` — the observed-use protocol that 019-002 must run.
- `verification.md` — closure: protected checklist, independent review, approval.

## Non-claims

- No runtime was exercised. No activation is claimed. No deployment, distribution or global installation is claimed.
- No test was run. The only checks performed for this documentary unit are the packet validations (`validate-request`, `validate-packet`, `validate-state`, `validate-policy`, and `render --route C`, all against `64aa4670`).
- The design adds no role, state, gate, communication service, packet field or `current_decisions` vocabulary. Documentary distinctions are conventions inside existing artifacts.
- The design does not repair the workspace state of `docs/.cdad-state.json`. That is outside 019-001.


## Prospective recovery supersession

Historical acceptance is preserved. Conflicting activation details are superseded for 019-002 by its approved `recovery-spec.md` and `recovery-plan.md`, following the owner-selected 019-003 baseline restoration.
