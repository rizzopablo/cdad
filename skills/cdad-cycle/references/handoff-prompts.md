# Handoff Prompts — Templates per role

## Prepared packet contract

Every new preparation runs on a v2 execution: produce the packet
with `skills/cdad-cycle/scripts/cdad_packet.py prepare --role <role> --substage
<substage> --objective "<atomic task>"`. It derives contract, inputs, scopes,
invariants and evidence from the role, writes `.cdad-execution/packets/<packet_id>/`
(REQUEST.json, PACKET.md) and the state binding (`execution`, `active_packet`),
and prints the packet. Capture the complete stdout bytes and use them unchanged
as either the Task prompt or the copyable new-chat body. A role receiving that
valid packet follows its static instructions and declared inputs directly; it
does not reload this skill. `render` re-emits the same bytes from the written files.

Two dispatch vehicles exist, and the packet is never re-typed by hand:

- **Route C — explicit file backup** (preferred for new native dispatches). Emit
  the identification with `skills/cdad-cycle/scripts/cdad_packet.py render
  --route C` on the published request (`--request
  .cdad-execution/packets/<packet_id>/REQUEST.json`, inside the project root) and transfer
  that stdout ALONE: the identification travels without an inline body, and it is
  never recomposed, retranscribed or accompanied by the packet body. A transport may
  add inert preamble or trailing text around that stdout; the receiver's `intake`
  admits it and that text grants no authority. The dispatch MUST name the
  installed packet CLI the receiver runs (`<cli>` of its `intake` rule) and the
  product root as explicit locator lines outside the identification (see
  "Self-contained dispatch" below); those lines grant no authority, do not alter
  the identification, and replace no validation. The sender never adds a second
  identification, a packet fragment or a rewritten copy.
- **Route A — the complete render.** Where the transport requires the full
  packet, transfer the complete render unaltered; it keeps its force. C
  authorizes no mix with an inline body — A+C is rejected even when the inline
  coincides — and a divergent inline is never rescued by switching to C. Invent
  no route, marker or fallback and remove none: a rejection is reported.

When the packet must carry the decisions that govern the role, repeat the
optional flag `--current-decision '<row JSON>'` — once per row, in the declared
order — in the same `prepare` invocation; the package then carries the rows it
declares. The flag is optional: without it the package is byte-identical.

The execution context is the canonical v2 document the first `prepare` writes
at `.cdad-execution/executions/<execution_id>/execution.json`, declared by the request as
`execution_context` (keep the operational directory, `.cdad-execution/` by default, out of git). A v1 `.cdad/execution.json` is
historical: it is not a universal preparation entry and it is never adopted
forward. The bootstrap that creates the v2 context, and that boundary with the
legacy document, are owned by `project-execution.md` §3 and are not restated here.

Architect packets need `docs/epics/<epic_id>/plan.md`; a feature without an
epic plan delegates the architect through the legacy template.

If the prepared inputs are absent or invalid, do not invent authority or send a
partial packet. Continue with the legacy templates below.

### Self-contained dispatch (owner of the sender and receiver rule)

A role never has to discover, inherit or guess a resource its unit requires. This
section is the single statement of that rule; the orchestrator source, the
shared intake block and the packet instructions point here and do not restate it.

**Sender (orchestrator).** Every dispatch, on either route and on the legacy
path:

- names every external executable the unit requires — always at least the
  installed packet CLI (`<skill-dir>/scripts/cdad_packet.py`, as an existing
  absolute path) — on an explicit locator line, together with the product root
  the role passes as `--project-root`; a role uses the named path and never
  resolves it from installation metadata. A dispatch without that line is
  incomplete and is not sent;
- keeps every required read and write inside the declared `read_scope` and
  `write_scope`; a resource the unit needs that lies outside them is added by a
  re-prepared packet or the unit is re-planned, never left for the role to find;
- never relies on instructions a runtime loads automatically from a directory
  (project instruction files such as `AGENTS.md`/`CLAUDE.md`, local skill
  folders): anything required from them travels in the packet or in a reference
  the packet names inside the scopes;
- when the role session runs in a different directory from the orchestrator,
  states in the dispatch the context that is not available there (loaded
  instructions, session history, workspace files) instead of letting the role
  assume it.

**Receiver (role).** Use the named locator and product root. When a required
resource is missing, unnamed or outside the declared scopes, report the gap to
the orchestrator and stop that part: no search of the checkout or the
filesystem, no out-of-scope read, no improvised substitute.

The locator lines are inert: they grant no authority, are not part of the
packet or its identification, and replace no validation.

How the orchestrator generates the prompt the user pastes into a new chat (or a native sub-agent) to start a specific role.

## Invocation with native sub-agents

If the environment has `cdad-*` sub-agents installed, invoke the role through
**the native mechanism that the orchestrator agent of your runtime declares**
(its `delegation` section: the dispatch tool, the role→sub-agent mapping and how
the packet is passed). For a prepared execution, the Task prompt is the renderer
stdout unchanged. The adaptations below apply only to the legacy flow:

For an OpenCode coordinator in a parent directory, see the
[nested-project native child example](sub-agent-strategies.md#native-child-when-the-project-root-is-nested).
It relocates an initialization-only child before canonical packet delivery.

- Start the prompt with: "Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand your role within the cycle. Act as `<role>` with the following task:"
- Add the line: "Also, read `docs/.cdad-state.json` and `docs/specs/<feature-id>/` as applicable to your role."
- Do NOT include "paste into a new chat" instructions — the native dispatch already isolates the session.
- Keep the strict rules, the context and the expected output of the template.

The per-role templates below remain the content source; the
difference is ONLY the delivery mechanism (native dispatch vs new chat).

## Handoff packet format

You always hand the user **one copyable block** with a fixed structure:
Always include the skill reference so the sub-agent frames itself correctly in the methodology.


```
🛑 HANDOFF: <role> — <atomic task>

──────────────────────────────────────────
PROMPT FOR A NEW CHAT (copy and paste):
──────────────────────────────────────────

Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `<role>` with the following task:

Task: <specific task, a single one>

Context you receive (paste after this prompt):
1. <file 1>
2. <file 2>
3. <...>

Strict rules:
- <rule 1>
- <rule 2>

Expected output:
- <concrete file / commit / response format>

When you finish, respond to the user with:
"DONE. <expected specific output>"

──────────────────────────────────────────

Your job (user):
1. Open a new chat (Zed thread, OpenCode session, ChatGPT new chat, etc.).
2. Paste the prompt above.
3. Attach / paste the context files: <list>.
4. When the role finishes, come back here with the output (commit hash, diff, new file).

For alternatives with native sub-agents, see `references/sub-agent-strategies.md`.
```

The packet **is the last output** of the orchestrator in that turn. Then you wait for re-entry.

---

## Documentary engagement — operating procedure

An engagement whose product is a document (notes, process maps, user stories,
a module's readme) travels through the same canonical flow. The normative
criterion — the four categories, the locators, the pending classification and
the four declarations — lives in `documentary-contracts.md`; this section only
fixes the operating procedure and never restates that norm.

### The seven declarations, through the existing fields

Before preparing the packet, the orchestrator spells out each declaration of
the documentary engagement in the field that already carries it. The transport
is unchanged for a documentary engagement: no documentary selector, no
parallel selector, no documentary stack and no new field are introduced.

| Declaration of the documentary engagement | Existing field |
|---|---|
| Aim and promises | `objective` plus the approved `contract` |
| Expected product | `expected_output` |
| Authorized sources | `inputs` and `read_scope` |
| Editable product | `write_scope` |
| Protected verifiers and inputs | `invariants`, the contract and the scopes |
| Checks and limits | `evidence_required` |
| Evidence and pending items | `evidence_required` plus the contract's closure record |

### How the orchestrator prepares and accepts it

1. Fix the domain, the role and the substage; `stack` keeps meaning domain and
   gains no documentary value.
2. State the aim, the expected product and the recoverable sources.
3. Delimit the editable product as a scope of its own, separated from the
   contract, the sources and the oracles. An exact path is admitted only when
   the existing path policy admits it.
4. Name the verifiers and the protected inputs through the existing fields.
5. Settle Odoo applicability with each role's own basis and with the addon
   boundary held by the domain skills; a documentary label never exempts addon
   work, and the real diff prevails over the label.
6. Record the required evidence, the limits and the pending items.
7. Prepare and validate by the canonical route, and publish the coherent
   recipient; a replacement rederives the agent from the role and the current
   stack, it never copies the predecessor's.
8. Dispatch without rebuilding the packet, altering the intake route or
   swapping the recipient.
9. At re-entry, contrast the real diff and the evidence, keeping structural
   control, semantic review and acceptance as separate facts.

The six roles and their boundaries are preserved: no documentary variant, no
documentary agent and no documentary selector is created, and separation of
responsibilities is kept as the roles contract states it. The editable product
needs an explicit editable scope (`write_scope`); when that scope overlaps the
sources, the verifiers or protected oracles, or when it is unclear which part a
file plays, that part is stopped and the engagement is corrected before
continuing. A declared documentary engagement that would edit addon work is
stopped at that part and returned to the orchestrator.

---

## Templates per role

### Test-writer (Stage 3 — AUDIT)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: audit the existing test suite BEFORE writing new tests for the feature. Produce a Test Audit Report documenting which tests will be modified, which stay untouched, and which new tests will be written.

Context:
1. Approved spec (paste the full content of docs/specs/<feat>/spec.md)
2. Relevant existing tests (list the files in tests/ that touch the feature's module/aggregate)
3. test-audit.md template: assets/spec-template/test-audit.md

Strict rules:
- Permissions: read-only on the codebase. You do NOT edit anything yet.
- Selection and dispositions per R2 (`sources/roles/test-writer.md`, `cdad-shared:convention-rule`): the unit is the promise, never the postcondition; every test in the AUDIT receives exactly one disposition — Mantener, Extender, Sustituir, Consolidar, Añadir or Retirar (references between operations do not duplicate it; ante incertidumbre se conserva con Mantener).
- Re-read the spec with a critical eye: what old behavior changes? For each existing test, contrast via referencias recuperables which postconditions it protects and declare which protection is missing (PC-1–PC-3; «without this test, the user…» expresses the difference, never generic risk).
- AUDIT declares Añadir for pending protection (PC-2/PC-4; «without this test, the user…» expresses the faltante), RED writes those Añadir; only physically new Sustituir/Consolidar destinations of comportamiento vigente identified here are created in POST-AUDIT (verde + sensibilidad per R2 puntos 5-6, PC-6).
- Every Sustituir/Consolidar identifies origen y destino, committed obligations that stay vigente, initial states/actions/effects whose difference may matter, location of each check in the destination, and evidence/sensitivity/limits of the comparison (PC-5); Retirar requires explicit reference to the obligation removed in the approved spec.
- Every modified test MUST have explicit justification in the spec (line/section)
- List untouched tests EXPLICITLY (Mantener, including destinations by reference that stay intact)
- Identify regression risks: obligations without accredited protection, uncertainties and blocks (never certify sufficiency under uncertainty).
- Bounded rounds (`references/bounded-review-cycles.md`): this audit belongs to the unit's **audit family**. Report the family round and ceiling the packet gives you (the orchestrator carries them from the ordinary records), the verification still required, and any stop/escalation condition; you never authorize an extra round, and at the maximum you report the remaining findings for adjudication instead of continuing.

Expected output: the Test Audit Report as FINAL TEXT with this structure (the orchestrator materializes `docs/specs/<feat>/test-audit.md` from that text — Roles contract §5; the canonical mechanism is the "Orchestrator materialization protocol" in `references/re-entry.md`):
- Summary of changing behavior
- Modified tests (with justification and spec ref)
- New tests to write
- Untouched tests (explicit list)
- Regression risk assessment
- Test Audit gate checklist

When you finish:

"DONE. Test Audit Report. Summary:
- Tests to modify: N
- Untouched tests: M
- New tests: P
- Regression risks: [yes/no, detail]

Pending: user approval of the audit before moving to RED."
```

### Architect (Stage 1 — Per-feature discovery)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `architect` with the following task:

Task: map which APIs, hooks, methods and fields of the system the feature "<feature-name>" touches. Output goes to the "Technical context" section of the spec.

Context:
1. docs/landscape.md (project's initial discovery)
2. docs/projectbrief.md and docs/systemPatterns.md
3. List of repo files relevant to the feature: <files>
4. Preliminary functional description of the feature: <one sentence>

Strict rules:
- Permissions: read-only. You do NOT edit anything.
- You do NOT invent methods or fields. If you can't verify, mark it as "VERIFY".
- You work only from real repo files, not assumptions.

Expected output: a markdown block with sections "Models/entities touched", "Available hooks/extensions", "Conventions applicable to this feature", "Pending verifications". When you finish, respond:

"DONE. <markdown block>"
```

### Architect (Stage 2 — Socratic brainstorm and spec draft)

Brainstorm:

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `architect` with the following task:

Task: answer a targeted technical consultation on the feature "<feature-name>" so the orchestrator can hold the dialogue with the user: expose the consequential ambiguities as questions.

Context:
1. Preliminary functional description: <one to three lines>
2. docs/landscape.md and the technical context of the discovery
3. docs/systemPatterns.md

Strict rules:
- Permissions: read-only.
- You do NOT write the spec in this turn.
- You ask Socratic questions in categories: inputs, outputs, errors, edge cases, non-functional, permissions, persistence, out of scope.
- You never invent or assume the user's agreement; mark unsupported assumptions "VERIFY".
- You stop at behavior decisions; implementation details are not questions.

Expected output: one `role-report` with findings and evidence, and the consequential questions still open. When finished, respond:

"DONE. <role-report>"
```

Draft:

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `architect` with the following task:

Task: produce the spec draft for "<feature-name>" based on the owner's recoverable dialogue decisions and, only if one was consulted, the consultation summary.

Context:
1. Owner dialogue decisions (recoverable from the discovery dialogue): <paste decisions>; consultation summary (only if the architect was consulted): <paste summary or "none">; do not require a brainstorm summary that does not exist
2. Spec template: <paste the content of assets/spec-template/spec.md>
3. docs/systemPatterns.md

Strict rules:
- Four mandatory sections: Functional description, Contract (signature + numbered postconditions), Verifiable invariants, Acceptance criteria.
- For each observable promise, its verification per `references/stage-2-specification.md` §"Verification strategy per promise" (property, method, acceptance criterion, expected evidence, limits).
- Numbered and verifiable postconditions (a test can determine pass/fail, or, for a semantic-only promise, the contextual review can).
- Measurable acceptance criteria (no vague adjectives).
- Declare the unit's maximum of correction rounds (positive integer), a concrete difficulty/risk justification and its status (provisional until the approver adopts it), applied independently to the draft, audit and result families (`references/bounded-review-cycles.md`; you declare it, the orchestrator applies and records it).
- No approval mark: the user adds it later.

Expected output: the spec draft as complete FINAL TEXT (the orchestrator or the user writes `docs/specs/<NNN-feature-id>/spec.md` from that text — Roles contract §5; the canonical mechanism is the "Orchestrator materialization protocol" in `references/re-entry.md`). When you finish:

"DONE. Spec draft. Pending: user approval."
```

### Test-writer (Stage 3 — POST-AUDIT: Update existing suite)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: update the existing test suite according to the approved Test Audit Report, and stop there. This is ONE subphase: POST-AUDIT only. New tests for pending behavior are RED, a separate dispatch with its own packet and session; physically new Sustituir/Consolidar of comportamiento vigente identified in the approved AUDIT belong to this POST-AUDIT (verde + sensibilidad per R2, originales kept until evidence), never to RED.

Context:
1. Approved Test Audit Report (paste the content of docs/specs/<feat>/test-audit.md)
2. Approved spec (paste docs/specs/<feat>/spec.md)
3. Current test suite (files or path)
4. Testing conventions: docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at implementation code.
- This session has TWO clearly separated parts (important so they don't get mixed):

#### PART 1: Update audited tests

For EACH test listed in the "Tests modified" section of test-audit.md:
- Open the current test in the repo.
- Change the test to validate the NEW behavior according to the spec.
  - If the new postcondition is "this behavior no longer exists": **DELETE the test**.
  - If the behavior changed: update the test's logic to reflect the new expectation.
  - If only the interface/name changed: rename and update.
- Run ONLY that updated test.
  - Fails? **Correct.** The implementer hasn't touched the code yet. That is expected.
  - Passes unexpectedly? Rare, but possible if the change is cosmetic. Report it in the output.
- Commit the change: `git commit -m "test: update <test-name> for spec change <ref-in-spec>"`

#### PART 2: Verify unchanged tests

For EACH test listed in the "Tests untouched" section of test-audit.md:
- Run that test NOW, before touching anything else.
  - Passes? Perfect. Continue.
  - Fails? HALT. This means the spec/code change broke a test that should NOT have been affected. Report it as "Regression detected" and STOP.

#### STOP here — this subphase is over

- You do NOT write Añadir for pending behavior here: those are RED, a separate dispatch with its own packet and session; you DO create the approved physically new Sustituir/Consolidar destinations of vigente identified in the AUDIT (verde + sensibilidad per R2, PC-6).
- You do NOT run the full suite as routine — Durante el ciclo focal + proporcional per the **Test evidence policy** (`references/stage-3-tdd.md` §"Test evidence policy"); Cierre de feature con completa recomendada, Cierre de epic con completa obligatoria por defecto o dispensa expresa; without sufficient authorization for that run record suite completa no realizada.
- You do NOT implement anything, and you do not read implementation code.

Expected output:

After finishing both parts, respond:

"DONE. Existing suite updated post-audit.

**PART 1 — Audited tests updated:**
- <test-name-1>: [deleted | updated for <change>]
- <test-name-2>: [updated for <change>]

**PART 2 — Unchanged tests verified:**
- All passing (list with <N> tests)

Output of the two runs, kept separate:

<updated tests run — red expected: the new behavior is not implemented yet>

<untouched tests run — green expected: unchanged behavior>

Commits:
<list hash of the updated tests>"
```

**Notes for the orchestrator**:
- Updated tests may be **red** post-session (that is correct, expected).
- Untouched tests must be **green** (regression gate).
- POST-AUDIT executes the approved maintenance: existing audited tests plus approved sustitutos nuevos of comportamiento vigente (Sustituir/Consolidar with verde + sensibilidad, originales kept until evidence). RED is a separate dispatch only for pending behavior.
- Secuencia reconciliada: mantenimiento de vigente AUDIT → POST-AUDIT (incluidos sustitutos, sin GREEN si no hay implementación que cambiar); pendiente AUDIT → POST-AUDIT cuando corresponda → RED separado → GREEN separado.
- NEVER say "migrated tests must pass". It is incorrect.

---

### Test-writer (Stage 3 — RED)

#### Pre-RED: Test Audit Checklist (before any new test)

Before touching a test file, run through:

1. **Re-read the new spec in full** focusing on: what old behavior changes?
2. **Search authorized sources**: tests, contracts and authorized inputs. What existing tests touch that via referencias recuperables? Never import or inspect implementation code to discover what to verify.
3. **Create `test-audit.md`** (template in assets) with:
   - What behavior changes (paragraph)
   - What tests get modified + justification for each
   - What new tests get written
   - What tests stay unchanged (STATE EXPLICITLY)
   - Regression risks
4. **The user approves the Test Audit** before RED starts.

If you can't confidently answer "every modified test is in the spec", **don't proceed**. Asking is cheaper than fixing afterwards.

**The POST-AUDIT comes first, in its own dispatch**: the previous section (Test-writer POST-AUDIT) executes the approved maintenance — audited existing tests plus physically new Sustituir/Consolidar destinations of vigente identified in the approved AUDIT (PC-6) — and stops there. New Añadir declared in the AUDIT for pending behavior are written HERE in RED, in this separate session with its own packet. A feature with no prior affected tests has no POST-AUDIT dispatch, and RED is dispatched directly.

---

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: write the test that verifies a NEW observable promise of the spec (rule R2,
`sources/roles/test-writer.md`; a promise may carry several numbered
postconditions). The test must FAIL when run, because there is no implementation
yet. It must fail for the right reason (assertion failure, not ImportError or
syntax error).

IMPORTANT: This dispatch comes AFTER the POST-AUDIT. If the audited existing tests have not been updated yet (update audited tests + verify untouched), stop and report it: the POST-AUDIT is a separate dispatch with its own packet and session, never part of this one.

Context:
1. Approved spec (paste the full content of docs/specs/<feat>/spec.md)
2. Module interface / signature (paste)
3. Project testing conventions: docs/systemPatterns.md (tests section)

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at src/, lib/, or implementation code.
- If implementation code exists (feature-extension case), you do NOT read it. You work only from the spec.
- Test name: descriptive, names the promise and the postcondition(s) it protects. E.g.: test_postcondition_<N>_<description>.
- ONE test per session, unless the promises are orthogonal (independent paths), in which case you may group.
- Do not add a second test for an equivalent observable result; do declare "without this test, the user..." for each test.
- After the test, run the suite and verify it fails for the right reason.

Expected output: test file + commit with message "test: add failing test for postcondition <N>". When you finish:

"DONE. Test added in <file>. Run output confirming the expected failure:

<paste the pytest/jest/etc output showing the assertion error>

Commit: <hash>"
```

### Implementer (Stage 3 — GREEN)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `implementer` with the following task:

Task: for a promise with pending executable behavior, make the freshly written test pass with a simple implementation of the approved behavior. For a semantic-only promise, implement the approved behavior against the contract and acceptance criterion, without inventing a test (routing: `references/stage-3-tdd.md` §"Routing by verification method"). NO speculative features.

Context:
1. Approved spec (paste)
2. The test that has to pass (paste file) — only for a promise with pending executable behavior; for a semantic-only promise paste the approved acceptance criterion and the sources instead
3. Module interface / signature (paste)
4. docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY the implementation product: code, or the documentary deliverable the engagement expressly commissions. You do NOT touch tests/. If you think the test is wrong, do NOT change it; report to the orchestrator.
- Implement the approved behavior simply, with the robustness it needs (R5 — `sources/roles/implementer.md`): add the validation, guards and reasonable error handling the behavior needs even when no test demands them.
- You do NOT add unrequested features "just in case".
- After implementing, run the evidence the change requires (focused tests + touched modules) per the **Test evidence policy** (`references/stage-3-tdd.md` §"Test evidence policy"); Durante el ciclo sin completa como rutina, Cierre de feature con completa recomendada, Cierre de epic con completa obligatoria por defecto o dispensa expresa; otherwise suite completa no realizada with motive and limits.

Expected output: implementation code + commit "feat: implement <postcondition>". When you finish:

"DONE. Implementation in <file>. Evidence the change requires:

<executable parts: output of the applicable checks, all green, with exit status. Semantic parts: the produced product and the pertinent structural evidence; fidelity is NOT established by that evidence and is left to the independent contextual review at Stage 4. Mixed: both kinds, each on its own part>

Commit: <hash>"
```

#### Fix packet (review re-entry — Stage 4 loop)

The implementer template above is reused to apply review fixes (loop with Stage 3). The orchestrator adds THREE mandatory things to the packet:

1. **Complete feedback**: the reviewer's findings and the user's context travel pasted in full in the packet (original text, rationale and provenance included). No softening edits — no friendly tone, no cuts, no "summary". The receiver verifies against the original evidence, not your paraphrase.
2. **A line at the start of the instructions**: *"Apply the `skills/cdad-cycle/references/receiving-feedback.md` protocol before touching code"*.

3. **The bounded-round context** (`references/bounded-review-cycles.md`): the unit, the family (`result`), the cumulative round and its ceiling, the evidence references, the closing verification still required after the fixes, and the stop/escalation status. Apply only the grounded fixes of the packet; do not extend the loop yourself — report the verification you ran and any finding that continues the loop, and the orchestrator decides the next round or the adjudication.

Rationale: the packet re-invokes the protocol with fresh tokens (antidote to dilution in long sessions) and the isolated session arrives without emotional investment. Protocol detail: `references/receiving-feedback.md`.

### Refactorer (Stage 3 — REFACTOR optional)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `refactorer` with the following task:

Task: improve code readability/simplicity without changing observable behavior.

Context:
1. Current code (paste file or path)
2. Full test suite
3. docs/systemPatterns.md

Strict rules:
- Permissions: edit in implementation code. You do NOT touch tests/.
- The suite must stay green AT ALL TIMES. If a change breaks a test, you revert it.
- Observable behavior does NOT change. Only readability, naming, duplication, helper extraction.

Expected output: refactored code + commit "refactor: <what was improved>". When you finish:

"DONE. Refactor in <files>. Green suite confirmed:

<paste run output>

Commit: <hash>"
```

### Test-writer (Stage 3 — Properties)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: write property tests for the invariants for which the approved contract selects executable property tests (list them in the context; invariants kept as reviewable restrictions are NOT in scope and get no campaign), using random inputs.

Context:
1. Approved spec, the invariants for which the contract selects property tests (paste only those, with their declared verification)
2. Interface (paste)
3. Project's property-testing library: <Hypothesis / fast-check / QuickCheck / etc.>
4. docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at implementation code.
- One invariant per property test, clear and legible.
- Presupuesto finito y positivo declarado y justificado before each campaign (invariante, dominio y coste); no universal minima or maxima.
- FIXED semilla in config plus reproducible evidence: invariante, presupuesto declarado y cantidad realmente ejecutada, semilla, versión/config del generador, contraejemplo pertinente when it fails.

Expected output: property tests file + commit "test: add property tests for invariants". When you finish:

"DONE. Property tests in <file>. Run output:

<paste output showing green properties>

Commit: <hash>"
```

### Test-writer (Stage 3 — Integration / E2E)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: translate the spec's acceptance criteria into E2E tests that verify the cross-component flow.

Context:
1. Approved spec, "Acceptance criteria" section (paste)
2. System's public API (endpoints, external interfaces)
3. Project's E2E test conventions

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT read the feature's implementation.
- Setup with complete fixtures, no point mocks.
- Calls via the public API, not through internals.
- Asserts derived from the acceptance criteria, one by one.

Expected output: E2E tests file + commit "test: add E2E tests for <feature>". When you finish:

"DONE. E2E in <file>. Current run state: <green if mode B / expected red if mode A outside-in>.

<paste output>

Commit: <hash>"
```

### Reviewer (Stage 4)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, read `references/verdict-tuple.md` (verdict contract: 4-field tuple per finding) and act as `reviewer` with the following task:

Task: review the feature's full diff against the approved spec and produce a prioritized report.

Context:
1. Full diff: paste the output of `git diff <base>..HEAD`
2. Approved spec: paste docs/specs/<feat>/spec.md
3. Interface / contract (paste)
4. .importlinter or equivalent (paste)
5. Conventions: AGENTS.md / CONTRIBUTING.md / docs/systemPatterns.md

Strict rules:
- Permissions: read-only. You do NOT modify anything.
- Ideally you are a model different from the implementer's (declare it at the start).
- Mandatory categories: Spec divergences, Boundary violations, Security risks, Style inconsistencies, Simplification suggestions.
- **Verdict contract (4-field tuple, see `references/verdict-tuple.md`):**
  each finding emits `Verdict (BLOCKING|OPTIONAL|ABSTAIN)` + `Bucket (h|m|l)`
  derived by the observables rule (family different from implementer +1, full
  diff +1, grounded rationale file:lines +1, spec+conventions +1;
  0-1→l, 2→m, 3-4→h) + `Problem` (verifiable rationale) + `Location`
  (exact provenance). If you can't judge a point, emit `ABSTAIN` with
  a reason — never disguise it as Optional. Without provenance the finding
  does not count in the aggregation.
- **Calibration (single canonical owner: `references/stage-4-review.md`
  § "Review calibration"):** weigh each finding by its real effect under the
  contract; a **blocking** carries evidence + consequence + a **verifiable
  closure condition**; a failure family is fixed as a family (one proportionate
  general solution); optional improvements do not prolong the cycle. Search
  adversarially, report proportionally.
- **Bounded rounds (`references/bounded-review-cycles.md`):** this review is the
  assessment of the unit's **result family**; report the family round and
  ceiling the packet gives you. In a closing re-review, state whether any
  finding continues the correction loop (that opens the next round) and which
  required verification you ran or still require; at the maximum, report the
  remaining findings with their evidence for adjudication. You never authorize
  an extra round, and "budget exhausted" is never a reason to downgrade a
  blocker.

Expected output: the review as FINAL TEXT with this structure (the orchestrator materializes `docs/specs/<feat>/review.md` from that text — Roles contract §5; the canonical mechanism is the "Orchestrator materialization protocol" in `references/re-entry.md`):

# Review — <feature>

Reviewer model: <model declaration — the model configured for the reviewer in the runtime>

## Blocking
### 1. <title>
Location: <file:lines>
Bucket: <h|m|l>  ← per the observables rule (verdict-tuple.md)
Problem: <...>
Consequence: <what breaks, for whom, under which real use>
Closure condition: <observable check that confirms the fix>
Suggestion: <...>

## Optional
### N. <...>
Location: <file:lines>
Bucket: <h|m|l>
Problem: <...>
Suggestion: <...>

## Abstentions
### N. <point you couldn't judge>
Reason: <...>

When you finish:

"DONE. Summary: <X> blocking, <Y> optional, <Z> abstentions."
```

### Reviewer (subphase `plan-review` — draft plan, PD-2/PD-4)

The same reviewer role reviews a **draft** (the object the contract declares: a
spec, or a plan and its spec), not a diff. Its procedure lives in the pinned
substage source `packets/substages/reviewer-plan-review.md` (composed by
`prepare` as `substages/reviewer-plan-review.md`); this template only shows how
to invoke it. Do NOT restate the procedure here — reference the source.

```
python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \
  --project-root <repo> \
  --role reviewer --substage plan-review \
  --contract-kind draft-plan \
  --contract-path <path to the draft plan> \
  --plan-version <version of the draft> \
  --objective "<atomic review task>"
```

The review is the assessment of the unit's **draft family** (`references/bounded-review-cycles.md`): specification and plan share ONE allowance, so give the packet the current round and ceiling from the ordinary records. A focused re-review is the verification of the current round; report whether its findings continue the correction loop (that opens the next round) and, at the maximum, the remaining findings for adjudication. The reviewer never authorizes an extra round.

The **three contract flags are required** (`--contract-kind draft-plan`,
`--contract-path`, `--plan-version`): without them `prepare` falls back to the
role default (`approved-feature-spec`) and the pairing guard rejects
`plan-review` over an approved contract (rc=2). Add `--current-decision
'<row JSON>'` (repeatable, once per row, in the declared order) when the
packet must carry the decisions that govern the reviewer; the flag is
optional and the package carries the rows it declares. Pass the rendered stdout
unchanged as the Task prompt. The packet is the execution contract: review the
draft's intention, constraints and object in a session independent from the
author, without marking it approved or authorizing implementation.

**The form of the reviewed object and its double identity.** The contract
declares the form of the object under review: `--object-kind spec` when the
draft is a spec, `--object-kind plan` when it is a plan (without the flag the
form is `plan`). When the review covers a spec **and** its plan, the plan is
the main document and the spec is the companion, fixed by digest:
`--spec-path <path to the spec>` and `--spec-version <version of the spec>`.
```

### Scribe (Stage 5)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `scribe` with the following task:

Task: produce three drafts for the Memory Bank update after the feature closes.

Context:
1. Approved spec: docs/specs/<feat>/spec.md
2. Full PR diff: git diff <base>..HEAD
3. Reviewer's report: docs/specs/<feat>/review.md
4. Current state of the Memory Bank: docs/projectbrief.md, docs/activeContext.md, docs/progress.md, docs/systemPatterns.md, docs/adr/

Strict rules:
- Permissions: read-only. You do NOT commit. You generate drafts; the user APPROVES them; the orchestrator commits them.

Expected output, three blocks:

1. Draft entry for activeContext.md (format: ## YYYY-MM-DD — Feature: <name>, with sections "Key decisions", "Detected technical debt", "Next feature in the queue").

2. Draft changes for progress.md (move the feature from in-progress to done, update status).

3. If you detect a relevant architectural decision: draft ADR (MADR format), with a "Confidence" field stating how sure you are that it merits an ADR (High / Medium / Low).
   If you do NOT detect one → "No ADR suggested".

When you finish:

"DONE. Drafts:

[Draft 1: activeContext.md entry]
<...>

[Draft 2: progress.md changes]
<...>

[Draft 3: ADR | No ADR suggested]
<...>"
```

---

## "RUN RULES" block (inject into packets of roles that run tests)

When the project has an expensive test suite (in Odoo: `odoo-make-env/references/run-budget-protocol.md`), the orchestrator adds this block at the end of the "Strict rules" of the test-writer (RED), implementer (GREEN), refactorer and reviewer packets:

```text
## RUN RULES (mandatory, hogar `skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy")
- Iterate ONLY with minimal runs against a warm environment
  (Odoo: make test-one against the warm DB). test-clean /
  make test FORBIDDEN during iteration (Durante el ciclo: focal + proporcional,
  sin suite completa como rutina, not for debugging).
- Cycle: read the full failure -> written hypothesis -> ONE change -> ONE
  run. Never re-run without a change. Max 2 runs per failure without
  convergence: STOP and report findings (it is a signal to escalate, not
  a "one more run").
- Gate by moment: Cierre de feature con suite completa recomendada (Odoo: make test-all;
  single-module: make test-clean); Cierre de epic con suite completa obligatoria por defecto
  o dispensa expresa registrada para ese cierre. La aprobación de la política autoriza la corrida
  ordinaria de cierre de epic sin autorización adicional para esa corrida. Task budget: max ~15 minimal
  runs; completa solo cuando el momento la exige (default; the project calibrates it in systemPatterns).
- Run logs named under stable paths of the declared workspace so the
  evidence is referenceable.
- Gate evidence: the line "0 failed, 0 error(s) of N tests" + commit of the
  tree that was run (recorded in the state file or commit message).
```

For the reviewer's packet, the equivalent block:

```text
## RUN RULES (review: 0 budget by default, hogar `skills/cdad-cycle/references/stage-3-tdd.md` §"Test evidence policy")
- If git diff --stat <evidence-run-commit>..HEAD shows only
  [STATE]/docs commits, the tree is identical: CITE the log (path + line).
  You do NOT re-run the suite.
- If the tree changed: evidencia proporcional al cambio, no una nueva suite completa automática;
  completa solo cuando el momento lo exige (cierre) o con autorización suficiente para esa corrida.
- Static analyzers (lint, import-linter) consume no budget.
```

---

## Notes for the orchestrator when generating the packet

- **Fill in ALL the context** before handing it to the user. Don't tell them "paste the spec here"; paste it yourself in the packet (if you have access to the file).
- **Atomic task**: one promise per test-writer (R2: the unit of selection is the promise, never the postcondition), one test per implementer, one diff per reviewer. Do NOT group unless the spec marks explicitly orthogonal promises.
- **Attaching files**: when you can, give exact paths. When the content fits, paste it inline in the packet.
- **Final line of the packet**: your turn always ends with the packet and the instruction to the user to "come back when the role finishes, with the output". Nothing else.
- **Self-contained dispatch** (§"Self-contained dispatch"): every handoff, packet or legacy, names the packet CLI and the product root on explicit locator lines, keeps required reads and writes inside the declared scopes, carries what a directory-loaded instruction file would have supplied, and states the context a role running in another directory does not have. The receiver reports a missing or out-of-scope resource and stops; it never searches or substitutes.
- **Bounded rounds**: every handoff into a correction loop (draft, audit or result family) preserves, from the ordinary records, the unit, the family, the cumulative round and its ceiling, the evidence references, the verification still required and the stop/escalation status (`references/bounded-review-cycles.md`); the receiver reports these and never authorizes an extra round. Re-dispatch, a new packet or execution identity, or a changed digest never resets the count.

### Inventario vivo (013-002 PC-7) — regla para handoffs

La declaración vive en `docs/suite-maintenance.md` `## Inventario vivo`
(el comando de integridad declarado, inventario y mapa). El
orquestador la lee en los re-entries de cambios de tests y transmite la regla
en estos handoffs, por ruta legacy y por paquetes. Si no hay inventario vivo
declarado, registra `sin inventario vivo declarado` sin bloquear. El
test-writer entrega el delta de altas (nodeid, capacidad, contrato,
procedencia) como texto; el orquestador lo materializa al re-entry antes de la
siguiente transición. Los cambios de orígenes o destinos incorporan además el
delta del mapa de PC-6; POST-AUDIT devuelve los deltas documentales
pertinentes bajo la misma separación de responsabilidades. `validate` con rc=0
bloquea solo en entrada a Review y cierre, medido sobre la revisión que ya
contiene los deltas materializados y los últimos cambios de tests.

### Vínculos contrato↔test (016-001 PC-6) — regla para handoffs

El hogar canónico es `skills/cdad-cycle/references/contract-test-links.md`
(formato y uso; esta sección solo la cita). El orquestador transmite la regla
en estos handoffs, por ruta legacy y por paquetes: ruta del registro, contrato
(path + sha256), regla de delta (`CURRENT − BASE` del mismo ámbito) y
comprobación aplicable. El test-writer entrega el delta del registro como
texto; el orquestador lo materializa al re-entry antes de la siguiente
transición. En entrada a Review y cierre se exige comprobación sobre los
deltas y tests actuales; en los re-entries intermedios un resultado no cero se
registra sin convertirse en gate de RED («tests nuevos no comprobados» sin
baseline).

---

## If the user is in mode B (specific role)

You do not emit a handoff packet. You apply the strict rules of the requested role to yourself:

1. Identify which role was requested.
2. Find the corresponding section above.
3. Work respecting the "Strict rules".
4. Output in the "Expected output" format.

If in the middle of the work you notice you need something outside the role's permissions (e.g. a test-writer wanting to see implementation code), stop and report:

> *"As a test-writer I should not see the implementation code. If I genuinely need it, this suggests the spec or the interface are incomplete. What do you prefer: completing the spec, or authorizing me to see the code (losing phase isolation)?"*
