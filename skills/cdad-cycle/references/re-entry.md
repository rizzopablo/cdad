# Re-entry — validating a finished role's output

When the user comes back to the orchestrator's chat with a role's result (typical format: *"Done, here's the commit / diff / file"*), apply the validations of the corresponding role before advancing.

## General re-entry protocol

1. **Identify which role finished** (from the state file's context and from what the user hands you).
2. **Apply that role's validations** (specific sections below).
3. **If validation passes**: update the state file, announce the transition or new sub-phase, generate the next handoff packet (or close the stage).
4. **If validation fails**: do NOT advance. Tell them specifically what's missing and propose rework (typically: handoff back to the same role with fix instructions).

---

## Orchestrator materialization protocol (read-only roles)

Read-only roles (architect, reviewer, test-writer AUDIT, scribe) do not persist
their own output. When such a role finishes, the orchestrator integrates its
result with the product CLI instead of copying text by hand. The interface owner
is the CLI itself — `python3 scripts/cdad_result.py --help` (the installed
entrypoint under the skill behaves the same) — and the feature spec
(`docs/specs/003-002-artifact-tools/spec.md`, §2 and §6–§9). Do not duplicate the
full interface here: consult `--help` and the spec for the exact flags and
fields. The protocol has four steps:

1. **RECEIVE.** The role's output arrives either as FINAL TEXT or as staged parts
   under `.cdad/inbox` (with a `RESULT.json` descriptor). `receive` only accepts
   staged parts (`source.kind="staged-file"`, regular files under the fixed
   `.cdad/inbox` inbox), so a FINAL TEXT payload must first be **staged by the
   orchestrator** — a prior mechanical step, before invoking `receive`:
   - write the **exact bytes** of the role's FINAL TEXT under `.cdad/inbox`
     (one file per part), **without retyping, summarizing or regenerating** them;
   - write the `RESULT.json` descriptor that points to them (`source.kind`,
     `parts[].name` / `artifact_kind` / `staged_path` under the inbox,
     `observed_changes` with its baseline manifest). The **owner of those fields
     is the feature spec (§3/§4) and the CLI** — consult them; do not duplicate
     the interface here;
   - only then invoke `receive` with that descriptor.

   Staging is transport, not authority: it approves nothing and grants the role
   no write permission. The staged bytes **are** the original (identical) — what
   is persisted and received is exactly the role's FINAL TEXT. Run the product's
   `receive` command to persist those bytes and emit the receipt; do not retype,
   summarize or regenerate the payload. The receipt is mechanical and **never
   approves**: `semantic_status` is always `pending`. Approval remains the
   user/owner's decision, never the receipt's.
2. **RECONCILE.** Validate the durable receipt (`validate-receipt`) before acting
   on it. The receipt is durable and idempotent: on a retry, reconcile which
   external effects were already applied and do NOT repeat an effect already
   applied. An identical retry converges to the same receipt byte for byte, even
   if the orchestrator already advanced the packet.
3. **MATERIALIZE.** Copy the parts to their canonical targets with `materialize`
   and an explicit authorization. The **exact target is declared in the
   authorization** (create-only when `expected_previous_sha256` is null; CAS when
   it is a digest); never infer the target from the payload text. `approval_effect`
   is always `false` — materialization adds no approval mark, does not change
   `semantic_status` and does not update state.
4. **STATE TRANSITION.** The orchestrator — and only the orchestrator — registers
   the **single** transition in `docs/.cdad-state.json`: map
   `state_transition_requested` `received` to the valid packet state `completed`
   (vocabulary of 001) and add a small reference of the receipt/state in
   `stage_history` (existing form; the schema is unchanged). The orchestrator
   registers it with the `register-transition` subcommand of `cdad_packet.py`;
   the operation, its classes and its checks are declared in the feature spec
   (`docs/specs/005-012-transition-registration/spec.md`), which this protocol
   names and does not restate. Registering the transition approves nothing: the
   receipt binds the parts it received and `semantic_status` stays `pending`
   (receiving never approves a gate). On retry, reconcile first and do not
   repeat a change already reflected in state.

## Transport equivalence: one receipt route

Native delegation does not change the delivery contract: the role returns its
**FINAL TEXT** in the **orchestrator's session**, and the orchestrator stages
the **exact bytes** under `.cdad/inbox` with their `RESULT.json` descriptor,
**without retyping, summarizing or regenerating** them. The staged bytes are
the original ones, and receiving approves nothing — `semantic_status` stays
`pending`.

The transport equivalence holds for every transport: it is the same route —
`receive` → `validate-receipt` → `materialize` → the state transition — for
the handoff to a new chat and for the CLI adapter.

---

## Equivalence of a registered run (canonical rule)

A finished role's output may satisfy consecutive controls (implementer → orchestrator → reviewer) **without repeating the full suite three times**, when the same tree / policy / environment can be shown equivalent. This section is the **single canonical owner** of the equivalence rule; derived consumers (`stage-4-review.md`, `SKILL.md`) reference it and never copy it.

When the equivalence is shown, a **registered (recorded) run** may be **cited** instead of re-executed. The citation is evidence-based and must cover every dimension of the contract table: product version (versión del producto); test version, including uncommitted changes (sin commitear); the executed selection (selección); the command (comando); the result (resultado); the environment / config / dependencies (entorno, configuración, dependencias); and the availability of the original (disponibilidad del original). Record the citation with the path + line + commit of the recorded run.

The same commit alone is NOT proof of an equivalent environment: the same commit (mismo commit), by itself (por sí solo), does not imply an equivalent environment. When the equivalence cannot be shown, the uncertainty is declared (incertidumbre declarada), never assumed (no se asume): do not assume (asumir) an equivalence that was not demonstrated.

When the equivalence fails, a new run is forced (nueva corrida / re-ejecución): a materially changed tree (cambio de árbol), a diverged policy/snapshot, or an environment that cannot be shown equivalent re-executes the affected checks before the closure (cierre / final). The equivalence is declared, not fabricated.

Focal vs transversal are treated differently in the same decision frame: a local correction (corrección local) uses focal tests; a change to a shared contract (contrato compartido) or with uncertain impact is transversal and expands (amplía) the affected checks. The procedure never treats both cases as identical.

Two attempts are reconciled with new information: a retry (intento / reintento) responds to a new hypothesis or new information (hipótesis / información nueva). An identical repetition, an absence of progress (sin progreso / sin avance), a blocked or stalled environment, or a disproportionate cost triggers a strategy review (revisión de estrategia), reconciled with the standing two-attempt rule. There are no unlimited retries (sin reintentos ilimitados), and no limit authorizes skipping controls (saltar controles) or declaring success without evidence (evidencia).

---

## Retry without new information — replanning the unit (canonical link)

The two-attempt rule of the previous section is reconciled with this unit-level trigger: a retry that brings no new information about a unit does not repeat — it triggers a strategy review (revisión de estrategia) that may replan the unit (its size, its boundary or its detail). The number of attempts is a signal, not a criterion: the count alone never decides; the absence of new information is what triggers the review.

Replanning a unit preserves its objective, its dependencies and the reasons that justified it — the trail is kept, never erased or rewritten. It does not rewrite a contract already dispatched: changing an in-flight contract requires a declared reconciliation, not a silent edit.

---

## Validations by role

### Architect — per-feature discovery

Check:
- [ ] The output covers the files / hooks / methods relevant to the feature.
- [ ] Every claim has a reference to a real file (no inventions).
- [ ] Pending verifications are explicitly listed, not hidden.

If it fails: ask the user to go back to the architect with the specific missing item.

If it passes: add the output to the spec in the "Technical context" section (in the draft that goes to Stage 2). Advance to the Socratic brainstorm.

### Architect — brainstorm

Check:
- [ ] There are explicit decisions in the key categories (inputs, outputs, errors, edge cases, out of scope).
- [ ] The user made the decisions, not the architect (the architect asked).

If it fails (e.g. a category left untouched): new turn from the architect with the missing questions.

If it passes: handoff to the architect in spec-writing mode.

### Architect — spec draft

Check:
- [ ] `docs/specs/<NNN-feature-id>/spec.md` exists.
- [ ] Four mandatory sections: Functional description, Contract (signature + numbered postconditions), Verifiable invariants, Acceptance criteria.
- [ ] Numbered, verifiable postconditions.
- [ ] Measurable criteria.
- [ ] No approval mark (correct: it gets approved later).

If it fails: handoff back to the architect with the missing section.

If it passes: pass the spec to the user (human or higher-hierarchy autonomous agent) for approval. **You do NOT approve it**. Tell them:

> *"Spec is at `docs/specs/<NNN>/spec.md`. Before moving to Stage 3: review it and add the approval mark at the end (`Status: Approved by <you> on <date>`) or in frontmatter (`approved_by` + `approved_at`). When it's approved, let me know."*

When the user confirms approval: update the state file with `current_stage: tdd`
and register the **pinned** approval in `stage_history` — an entry with
`feature`, `stage: "specification"`, a non-empty `approved_by`, `contract_path`
(project-relative spec path) and `contract_sha256` (the `sha256` of the exact
approved bytes). The pin is mandatory: editing the spec afterwards invalidates
the authorization, so `prepare` fails for the construction roles with the
`approval pending` diagnostic. (The architect is authorized separately, by the
`epic_history` entry `stage: "epic-plan"` approved by the owner; it is not a
spec approval and carries no hash pin.) Then emit handoff to test-writer (RED)
for postcondition 1.

### Test-writer — RED

Check:
- [ ] A new file or diff exists in `tests/`.
- [ ] The user pasted the run output showing the test failing.
- [ ] The test fails with an **AssertionError or equivalent**, NOT with an ImportError, syntax error, or module-not-found.
- [ ] A commit with the `test:` prefix exists (not mixed with feat).

If it fails for the wrong reason (ImportError, etc.): handoff back to the test-writer.

> *"The test fails with `<specific error>`, which is NOT an assertion failure. That means the test doesn't get to exercise the postcondition. Possible causes: module doesn't exist yet / signature mistyped in the test / fixture misbuilt. Go back to the test-writer with this info."*

If it passes: update `postconditions_status: { "<N>": "red" }` and `tdd_substage: "green"`. Emit handoff to implementer.

### Implementer — GREEN

Check:
- [ ] The user pasted the evidence the change requires — focused tests plus the modules it touches — per the **Test evidence policy** (`stage-3-tdd.md` §"Test evidence policy"); the complete suite is the closure gate.
- [ ] The regression is green, including previous tests.
- [ ] A commit with the `feat:` prefix exists.
- [ ] The implementer did NOT modify `tests/` (check with `git diff --stat <base>..HEAD -- tests/` if you have access, or by asking the user).

If it modified tests: AP-4 (implementer modifies tests). Tell them:

> *"AP-4 detected: the implementer touched tests. Revert the changes in tests/. If the test is genuinely wrong, that is the test-writer's work, not the implementer's. Do we revert and go back to the test-writer with the problem, or was the test change cosmetic (e.g. a name)?"*

If the suite is not all green: handoff back to the implementer with the failure info.

If it passes: update `postconditions_status: { "<N>": "green" }`. Ask the user:

> *"Postcondition <N> green. Do you want a REFACTOR now (if you see evident friction) or do we move to the next postcondition / sub-phase?"*

Depending on the answer: handoff to refactorer, or handoff to test-writer for postcondition N+1, or (if all postconditions are green) handoff to the properties / E2E sub-phase if the spec asks for it.

### Refactorer

Check:
- [ ] The suite is still green after the refactor.
- [ ] The refactorer did NOT modify `tests/`.
- [ ] Commit with the `refactor:` prefix.

If the suite is red: AP-11. Ask to revert.

> *"AP-11: the refactor broke tests. Refactoring does not change observable behavior. Either the change was functional (that requires updating the spec first), or the tests were wrong (go back to the test-writer). Which of the two?"*

If it passes: the state file does not change (the postcondition stays green). You advance to the next postcondition or sub-phase.

### Test-writer — Properties

Check:
- [ ] Property tests exist and run with a fixed seed.
- [ ] The user pasted output showing the properties green with reasonable volume (≥100 inputs).
- [ ] Commit with the `test:` prefix.

If a property fails with a specific input: that input is a bug. Handoff to implementer with the counterexample input.

If it passes: update `tdd_substage: "integration"` (or `"review-pending"` if the spec does not mark E2E). Advance.

### Test-writer — E2E

Check:
- [ ] E2E tests exist and call through the public API.
- [ ] Setup with complete fixtures.
- [ ] Asserts derived from the spec's acceptance criteria.
- [ ] State: green if mode B (closure), expected red if mode A (outside-in) until the pieces connect.

If mode B and E2E red: there is an assembly problem. Handoff to implementer.

If it passes: update `tdd_substage: "review-pending"`. Announce to the user that Stage 3 closes and propose moving to Review.

### Reviewer

Check:
- [ ] `docs/specs/<feat>/review.md` exists.
- [ ] Structure: "Blockings" and "Optionals" sections, each finding with location + problem + suggestion; each blocking also states its consequence and a verifiable closure condition (calibration, rule 2).
- [ ] Every finding has an explicit severity.
- [ ] **Verdict contract (verdict-tuple.md):** every finding includes a `Bucket: <h|m|l>` derived by the rule of observables (not elicited confidence), and the review includes an "Abstentions" section (it may be empty) with the points the reviewer could not judge. Without bucket/provenance → request a correction, don't add it by hand.
- [ ] When passing to Layer 2, the summary includes the abstentions: *"<X> blockings, <Y> optionals, <Z> abstentions"*. The aggregator may apply κ-dedupe (findings from the same commit/block do not count as independent corroboration) — diagnostic, not veto: Layer 2 decides the prioritization.

If it passes: pass the report to the user to validate the prioritization.

> *"Report at docs/specs/<feat>/review.md: <X> blockings, <Y> optionals. Your job (layer 2): read the report (not the full diff) and validate whether the prioritization is correct. For each blocking: is it genuinely blocking, or is there context the reviewer doesn't have? For each optional: apply now or discard?"*

When the user comes back with their prioritization:
- Record the decisions in the review.md (notes with the reason for each dismissal).
- If there are blockings to apply: handoff to implementer with the list of fixes.
- If all blockings are resolved / dismissed: update the state file → `current_stage: merge` and emit handoff to scribe.

### Scribe

Check:
- [ ] Three drafts present: activeContext entry, progress changes, ADR draft (or "no ADR suggested").
- [ ] Drafts are NOT committed (correct).
- [ ] The ADR draft (if any) declares its "Confidence".

If it passes: pass the drafts to the user for approval.

> *"The scribe is done. Three drafts for your review:*
>
> *1. activeContext.md entry: <paste>*
> *2. progress.md changes: <paste>*
> *3. ADR: <paste or "no ADR suggested", confidence <X>>*
>
> *Edit whatever the scribe got wrong or couldn't know. When you're satisfied, approve; the orchestrator commits with the `docs(memory):` prefix. Let me know when it's committed."*

When the user approves and you commit: validate full CI (gate 5→done). If CI is green and the Memory Bank is updated, close the feature.

---

## When NOT to advance

If the role's output doesn't meet the expected format, or critical info is missing (e.g. the test-writer didn't paste the run output), ask for what's missing before validating.

> *"To validate the RED of postcondition <N>, I need the run output showing the assertion error. Can you paste it for me?"*

You don't assume green. You don't assume correct. Verification is empirical.

---

## State file update

Every successful validation leads to a state file update. Notify the user in one line:

> *"State updated: `postconditions_status: {"3": "green"}`, `tdd_substage: "refactor-or-next"`. <Next step>."*

This gives traceability of every transition.
