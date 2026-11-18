# Discovery report — 019-001

**Read-only discovery completed. This is not a specification, an approval, or activation of new role powers.**

## 1. Authority and verification limits

- Route C identification matched the canonical identification.
- `REQUEST.json` and the complete `PACKET.md` passed validation.
- Full canonical packet equality: **6,427 bytes**, SHA-256 `aeb1f5db2ec32ff691216d99cf9d7f3cb31dd45f9a10747031eb38701f843f23`.
- Execution context is v2.
- Repository revision examined: `265174993b4213be9a96545578016657bc8b09ba`.
- Authorized sources: repository files under the declared `repository-read` scope. No external conversations, global installations, or runtime capability claims were used.

The unit contract authorizes an operating-design result first and coherent activation separately. Its proposed role division must not be treated as already deployed behavior (`UNIT-CONTRACT.md:60–67,94–98`).

The epic’s recorded delegation permits the orchestrator to make and record applicable approvals within this epic; publication and deployment remain excluded (`docs/epics/epic-019-discovery-dialogue/execution.md:3–14`). This report grants no approval.

## 2. Existing behavior

### Normal cycle

**Initial discovery already has an orchestrator–user conversation.** The orchestrator asks structuring questions and assembles a landscape draft; the user confirms it. Per-feature technical discovery is delegated to the architect (`skills/cdad-cycle/references/stage-1-discovery.md:7–30,45–63`).

**Stage 2 currently assigns behavioral brainstorming to the architect.** The orchestrator dispatches brainstorming, validates closure, dispatches drafting, obtains independent draft review, then requests approval (`skills/cdad-cycle/references/stage-2-specification.md:5–45,47–75`).

The legacy brainstorm explicitly tells the architect to:

- help the user define behavior;
- ask questions and wait for answers;
- finish with `READY FOR DRAFT` and a decision summary.

Its stopping condition is that remaining questions concern implementation details rather than behavioral choices (`skills/cdad-cycle/references/handoff-prompts.md:235–259`).

Re-entry checks that key decisions exist and that the user—not the architect—made them. It does not specify how a delegated session receives the user’s answers or how corrections are preserved (`skills/cdad-cycle/references/re-entry.md:230–238`).

### Lightweight paths

There are several related surfaces, not one fully specified lightweight dialogue contract:

- `README.md:21–25` recommends `cdad-spec-and-test` for smaller, deliberately bounded work.
- `skills/cdad-spec-and-test/SKILL.md:16–25,54–78` defines a minimal outcome/checklist and build–verify loop. It contains no explicit ownership or closure procedure for a mediated brainstorm.
- Its integration section says the cycle owns gates and format; therefore this skill alone does not establish exemptions from the normal cycle (`:95–104`).
- Normal Stage 2 permits a trivial spec of one paragraph plus a failing test, **still with brainstorm and approval** (`skills/cdad-cycle/references/stage-2-specification.md:116–122`).
- The methodology separately describes “CDAD light” with isolated sessions for critical components and optional review (`CDAD_metodologia.md:114,2937`).

**Design implication:** specify which lightweight entry points are supported and their applicable obligations. Do not silently equate all these descriptions or import the full ceremony into every small task.

## 3. Verified conflicts and operational gaps

### A. Moving functional brainstorming changes an existing role boundary

The architect’s canonical contract owns “technical mapping + Socratic brainstorm + spec draft” (`sources/roles/architect.md:100–108`).

The orchestrator’s canonical contract prohibits role work inline and directs it to delegate requested role work (`sources/roles/orchestrator.md:128–147,298–307`). Initial discovery has a specific conversational allowance; it does not establish a general Stage 2 allowance.

**Consequence:** an explanatory dialogue reference alone cannot authorize the proposed division. Canonical role contracts and their effective consumers must be reconciled explicitly while retaining prohibitions on inline technical substitution, implementation, tests and independent review.

### B. The question loop is underspecified, not proven impossible

The legacy handoff assumes interactive questioning and waiting. The prepared brainstorm block merely instructs the architect to expose ambiguity and avoid premature design (`skills/cdad-cycle/packets/substages/architect-brainstorm.md:1`).

Neither defines the mediated round trip: architect findings → orchestrator question → owner answer → corrected decision context → architect continuation.

**Limit:** this establishes an instruction-contract gap. It does **not** establish that every runtime prevents subagents from asking questions.

### C. Prepared brainstorm has a concrete single-delivery incompatibility

The result policy admits `role-report` for architect discovery and draft, but **not brainstorm** (`skills/cdad-cycle/scripts/cdad_result.py:826–840`).

The common dispatch path derives a single delivery kind from that table and rejects ambiguity (`skills/cdad-cycle/scripts/cdad_dispatch.py:999–1016`). The OpenCode adapter follows the same criterion (`skills/cdad-cycle/scripts/cdad_delegate_opencode.py:492–519`).

An in-memory invocation returned:

```text
architect/discovery → role-report
architect/brainstorm → diagnostic: table does not determine a single artifact kind
architect/draft → role-report
```

The existing test explicitly protects rejection of architect/brainstorm `role-report` (`tests/test_006_005_u7_scribe_role_report.py:694–723`).

**Consequence:** retaining brainstorm packets as a supported technical-consultation path requires an explicit delivery decision and focused regression changes. Do not disguise questions as a spec draft or silently substitute another substage.

### D. One draft re-entry instruction bypasses the independently required review

Stage 2 requires independent draft review before approval. The dedicated reviewer re-entry agrees (`skills/cdad-cycle/references/stage-2-specification.md:47–75`; `references/re-entry.md:266–278`).

However, architect draft re-entry directly says to pass the spec to the user for approval (`references/re-entry.md:240–264`).

**Consequence:** a consumer following that subsection alone can skip the review. Reconcile its next action with the existing review route rather than adding a new gate.

### E. Existing decision transport is useful but not a complete dialogue record

Existing facilities include:

- brainstorm summaries supplied to drafting;
- `docs/systemPatterns.md` as a durable decision index;
- optional packet `current_decisions`, supplied with repeatable `--current-decision`.

The packet field has a closed shape and vocabulary: file, state, summary, roles, reference, and conditional replacement. It transports governing decisions, not proposed defaults or unanswered questions (`skills/cdad-cycle/scripts/cdad_packet.py:94–111,1540–1616,5776–5795`).

The Memory Bank template explicitly excludes proposed decisions from its current-decision index (`skills/cdad-cycle/assets/memory-bank-templates/systemPatterns.md:5–34`).

**Consequence:** reuse these mechanisms where appropriate, but do not claim they already preserve partial answers, unaccepted proposals, corrections and unresolved choices as distinct dialogue states.

### F. Idle/done mismatch is verified

Closing guidance instructs:

```text
current_stage: done
active_feature: null
```

The epic handoff subsequently checks for that state (`skills/cdad-cycle/references/stage-5-merge.md:187`; `skills/cdad-epic/references/feature-handoff.md:60–64`).

Actual closure registration writes `current_stage=idle` and clears `active_feature`; opening requires that coherent resting state (`skills/cdad-cycle/scripts/cdad_packet.py:9195–9211,686–722,7293–7312`).

A pure in-memory probe showed:

```text
done/null → entry: next-unit
next route → open-unit
same state's opening precondition → state incoherent
idle/null → coherence True
```

The status projection does not apply the same idle-coherence check before recommending the next route (`:9476–9518,9990–10033,10145–10159`).

**Consequence:** align closing instructions and status eligibility with the real transition. Repairing an earlier workspace state is separate from this permanent correction.

## 4. Effective instruction consumers

The following chains are verified:

1. **Canonical roles → generated agents.**  
   `sources/roles/{architect,orchestrator}.md` feeds OpenCode and Claude Code agents. The orchestrator also receives the architect’s composed contract row. Generator metadata independently describes Socratic brainstorming (`scripts/cdad-generate.py:505–533,616–689,915–945`).

2. **Packet sources → frozen request → effective packet.**  
   New publications capture common, role and substage instruction bytes. Published frozen packets render from those snapshots, not subsequently edited source files (`skills/cdad-cycle/scripts/cdad_packet.py:1760–1774,1849–1879`). Editing live instructions does not update an already published packet.

3. **Legacy handoffs → cycle/stage references.**  
   Standalone architecture without an epic retains the legacy path; prepared architecture cannot simply replace it (`references/handoff-prompts.md:41–45`; `scripts/cdad_packet.py:2398–2410`).

4. **Domain variants.**  
   Generic and Odoo architect agents share the role boundary. Odoo additionally loads domain guidance whose brainstorm section asks configuration/custom, module-reuse and business-validation questions (`sources/roles/architect.md:155–165`; `skills/odoo-architect/SKILL.md:138–147`). Preserve that technical/domain contribution without implying a second user-facing interlocutor.

5. **Lightweight consumers.**  
   The smaller skill, trivial Stage 2 variant and public methodology need explicit applicability alignment.

In-memory generation matched the repository architect, Odoo architect and orchestrator agents byte-for-byte for both runtimes. The three corresponding project-local `.opencode/agents` files matched their recorded derived hashes.

**Limit:** these checks establish composition and local-file integrity—not global deployment, runtime loading precedence or behavioral success.

## 5. Decisions still needed before drafting

These are design questions for the orchestrator/authorized owner, not requests to reopen the approved epic direction.

1. **Where does the minimum recoverable dialogue context live?**  
   Compare a compact section in an existing authorized artifact with a separate record. Prefer reuse unless the observed handoff cannot preserve provenance, corrections and unresolved choices without a separate artifact.

2. **What is the precise closure check?**  
   Decide who confirms that consequential behavioral choices are resolved or explicitly excluded, the architect’s relevant uncertainties are routed, and the summary preserves the owner’s intent. An answer, agreement with a summary and spec approval must remain separate events.

3. **How do existing brainstorm packets evolve?**  
   Preserve a supported path for targeted technical challenge and alternatives, or explicitly reconcile its replacement. Include the delivery-kind conflict above; wording changes alone are insufficient.

4. **What is shared across lightweight and normal dialogue?**  
   A common fidelity rule with proportionate recording appears preferable to two independently maintained dialogue protocols. The amount of ceremony should follow risk and the applicable workflow—not a questionnaire or scenario quota.

These questions do not block this discovery report. They block a claim that the operating design is already unambiguous and ready for approval.

## 6. Verification and handoff

### Required later evidence

The approved contract requires observed agent use, not merely matching headings or keywords (`UNIT-CONTRACT.md:113–139`). The future exercise must show that partial answers, rejected defaults, corrected decisions and unresolved behavioral choices do not become invented agreements. Technical uncertainty must remain distinguishable from verified behavior.

Structural checks, semantic review and owner acceptance remain separate. No semantic exercise or independent review was performed in this discovery session.

### Commands and observed results

Executed from `<repo>`:

```sh
python3 scripts/cdad_packet.py validate-request --project-root "$PWD" --request .cdad/packets/019-001-discovery-dialogue-contract-architect-discovery-001/REQUEST.json

python3 scripts/cdad_packet.py validate-packet --project-root "$PWD" --request .cdad/packets/019-001-discovery-dialogue-contract-architect-discovery-001/REQUEST.json --packet .cdad/packets/019-001-discovery-dialogue-contract-architect-discovery-001/PACKET.md

python3 scripts/cdad_packet.py render --project-root "$PWD" --request .cdad/packets/019-001-discovery-dialogue-contract-architect-discovery-001/REQUEST.json --route C

git status --short
git diff --stat
git diff --cached --stat
git rev-parse HEAD
```

Validation commands succeeded. Additional Python probes used **Python 3.13.5**, `PYTHONDONTWRITEBYTECODE=1`, no temporary files, and these exact repository functions:

- generator `build('odoo', runtime)`, comparing returned bytes without publishing;
- packet `_entry_selection`, `_next_route`, `_validate_idle_coherence`, using an in-memory state;
- result `_allowed_kinds` and dispatch `derive_artifact_kind`, for architect discovery/brainstorm/draft.

**Files modified by this role:** none.  
**Commit created:** none.  
**Test suite:** not run; this was discovery, not implementation or closure.

Initial and final git observations showed the same pre-existing changes:

```text
 M docs/.cdad-state.json
?? docs/epics/epic-019-discovery-dialogue/discovery-begin.json
```

No product diff was observed.

**Next step:** mediated design discussion resolving the four questions above, followed by a separately commissioned specification draft and independent draft review.