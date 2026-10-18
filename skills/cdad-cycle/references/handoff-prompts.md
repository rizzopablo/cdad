# Handoff Prompts — Templates per role

## Prepared packet contract

When `.cdad/execution.json` exists for the active feature, produce the packet
with `skills/cdad-cycle/scripts/cdad_packet.py prepare --role <role> --substage
<substage> --objective "<atomic task>"`. It derives contract, inputs, scopes,
invariants and evidence from the role, writes `.cdad/packets/<packet_id>/`
(REQUEST.json, PACKET.md) and the state binding (`execution`, `active_packet`),
and prints the packet. Capture the complete stdout bytes and use them unchanged
as either the Task prompt or the copyable new-chat body. A role receiving that
valid packet follows its static instructions and declared inputs directly; it
does not reload this skill. `render` re-emits the same bytes from the written files.

The execution context is written once per feature (keep `.cdad/` out of git):

```json
{"schema_version": 1,
 "execution": {"id": "exec-<feature_id>-001", "epic_id": "<epic_id or none>",
   "feature_id": "<feature_id>", "runtime": "claude-code", "scope": "local",
   "model_policy": "ordinary", "authority_ref": "docs/.cdad-state.json",
   "model": {"configured": null, "reported": null}},
 "path_policy": {"implementation_roots": ["src"], "test_roots": ["tests"],
   "colocated_test_roots": [], "documentation_roots": ["docs"],
   "colocated_test_suffixes": [], "colocated_test_prefixes": ["test_"]}}
```

Architect packets need `docs/epics/<epic_id>/plan.md`; a feature without an
epic plan delegates the architect through the legacy template.

If the prepared inputs are absent or invalid, do not invent authority or send a
partial packet. Continue with the legacy templates below.

How the orchestrator generates the prompt the user pastes into a new chat (or a native sub-agent) to start a specific role.

## Invocation with native sub-agents

If the environment has `cdad-*` sub-agents installed, invoke the role through
**the native mechanism that the orchestrator agent of your runtime declares**
(its `delegation` section: the dispatch tool, the role→sub-agent mapping and how
the packet is passed). For a prepared execution, the Task prompt is the renderer
stdout unchanged. The adaptations below apply only to the legacy flow:

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
- Re-read the spec with a critical eye: what old behavior changes?
- For each existing test that could be affected, determine:
  - Does it validate behavior that CHANGES? → Mark for modification
  - Does it validate behavior that STAYS? → Mark as untouched
  - Unrelated? → Ignore
- Every modified test MUST have explicit justification in the spec (line/section)
- List untouched tests EXPLICITLY (not implicitly)
- Identify regression risks: new behavior without test coverage

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

Task: help the user define the feature "<feature-name>" by asking questions that expose ambiguities. You do NOT propose design yet, you only ask.

Context:
1. Preliminary functional description: <one to three lines>
2. docs/landscape.md and the technical context of the discovery
3. docs/systemPatterns.md

Strict rules:
- Permissions: read-only.
- You do NOT write the spec in this turn.
- You ask Socratic questions in categories: inputs, outputs, errors, edge cases, non-functional, permissions, persistence, out of scope.
- One to three questions per turn. You wait for answers before continuing.
- You cut off when the remaining questions are implementation details, not behavior decisions.

Expected output: a round of questions. When you consider the brainstorm closed, respond:

"READY FOR DRAFT. Summary of the brainstorm: <bullets of decisions made>"
```

Draft:

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `architect` with the following task:

Task: produce the spec draft for "<feature-name>" based on the brainstorm.

Context:
1. Brainstorm summary: <paste summary>
2. Spec template: <paste the content of assets/spec-template/spec.md>
3. docs/systemPatterns.md

Strict rules:
- Four mandatory sections: Functional description, Contract (signature + numbered postconditions), Verifiable invariants, Acceptance criteria.
- Numbered and verifiable postconditions (a test can determine pass/fail).
- Measurable acceptance criteria (no vague adjectives).
- No approval mark: the user adds it later.

Expected output: the spec draft as complete FINAL TEXT (the orchestrator or the user writes `docs/specs/<NNN-feature-id>/spec.md` from that text — Roles contract §5; the canonical mechanism is the "Orchestrator materialization protocol" in `references/re-entry.md`). When you finish:

"DONE. Spec draft. Pending: user approval."
```

### Test-writer (Stage 3 — POST-AUDIT: Update existing suite)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: update the existing test suite according to the approved Test Audit Report. Then, write new tests in RED. This is a combined session of two sub-phases: POST-AUDIT + RED.

Context:
1. Approved Test Audit Report (paste the content of docs/specs/<feat>/test-audit.md)
2. Approved spec (paste docs/specs/<feat>/spec.md)
3. Current test suite (files or path)
4. Testing conventions: docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at implementation code.
- This session has THREE clearly separated parts (important so they don't get mixed):

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

#### PART 3: Write new tests (RED)

For EACH new postcondition of the spec (not touched by the previous ones):
- Write ONE test that verifies that postcondition.
- The test must FAIL when run (because the code is not implemented).
- Fail for the right reason: AssertionError, not ImportError.
- Descriptive name: test_postcondition_<N>_<description>.
- Commit it: `git commit -m "test: add failing test for postcondition <N>"`

#### Expected execution flow

1. Update tests → commit (they may be red, that is correct)
2. Verify untouched → all must pass
3. Write new tests → commit (they must be red)
4. Final run of the ENTIRE suite:
   - Updated tests: RED expected (new behavior, unimplemented code)
   - Untouched tests: GREEN expected (unchanged behavior)
   - New tests: RED expected (new postconditions, no implementation)

Expected output:

After finishing everything (3 parts), respond:

"DONE. Suite updated post-audit + new tests in RED.

**PART 1 — Audited tests updated:**
- <test-name-1>: [deleted | updated for <change>]
- <test-name-2>: [updated for <change>]

**PART 2 — Unchanged tests verified:**
- All passing (list with <N> tests)

**PART 3 — New tests in RED:**
- <test-name-new-1>
- <test-name-new-2>

Output of the final suite run:

<paste pytest/jest/etc output showing:
  - Red tests from new postconditions
  - Red tests from updated ones
  - Green tests from untouched ones
>

Commits:
<list hashes of:
  - Updated tests
  - New RED tests
>"
```

**Notes for the orchestrator**:
- Updated tests may be **red** post-session (that is correct, expected).
- Untouched tests must be **green** (regression gate).
- New tests must be **red** (standard RED).
- NEVER say "migrated tests must pass". It is incorrect.

---

### Test-writer (Stage 3 — RED)

#### Pre-RED: Test Audit Checklist (before any new test)

Before touching a test file, run through:

1. **Re-read the new spec in full** focusing on: what old behavior changes?
2. **Walk the codebase**: import the modules/models the feature touches. What existing tests touch that?
3. **Create `test-audit.md`** (template in assets) with:
   - What behavior changes (paragraph)
   - What tests get modified + justification for each
   - What new tests get written
   - What tests stay unchanged (STATE EXPLICITLY)
   - Regression risks
4. **The user approves the Test Audit** before RED starts.

If you can't confidently answer "every modified test is in the spec", **don't proceed**. Asking is cheaper than fixing afterwards.

**If you already completed the POST-AUDIT**: use the previous section (Test-writer POST-AUDIT), which combines updating audited tests + writing new tests in a single session. The section below is for cases where POST-AUDIT does not apply (a feature with no prior affected tests).

---

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `test-writer` with the following task:

Task: write ONE test that verifies a NEW postcondition (not touched by the audit) of the spec. The test must FAIL when run, because there is no implementation yet. It must fail for the right reason (assertion failure, not ImportError or syntax error).

IMPORTANT: This happens AFTER the POST-AUDIT. If you haven't completed the POST-AUDIT yet (update audited tests + verify untouched), do it first in that session or another one.

Context:
1. Approved spec (paste the full content of docs/specs/<feat>/spec.md)
2. Module interface / signature (paste)
3. Project testing conventions: docs/systemPatterns.md (tests section)

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at src/, lib/, or implementation code.
- If implementation code exists (feature-extension case), you do NOT read it. You work only from the spec.
- Test name: descriptive, references the postcondition. E.g.: test_postcondition_<N>_<description>.
- ONE test per session, unless postconditions are orthogonal (independent paths), in which case you may group.
- After the test, run the suite and verify it fails for the right reason.

Expected output: test file + commit with message "test: add failing test for postcondition <N>". When you finish:

"DONE. Test added in <file>. Run output confirming the expected failure:

<paste the pytest/jest/etc output showing the assertion error>

Commit: <hash>"
```

### Implementer (Stage 3 — GREEN)

```
Find and read the cdad-cycle skill (`skills/cdad-cycle/SKILL.md`) to understand the CDAD cycle and your specific role within it. Then, act as `implementer` with the following task:

Task: make the freshly written test pass with minimal code. NO extra features.

Context:
1. Approved spec (paste)
2. The test that has to pass (paste file)
3. Module interface / signature (paste)
4. docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY in implementation code. You do NOT touch tests/. If you think the test is wrong, do NOT change it; report to the orchestrator.
- MINIMAL code. The simplest implementation that makes the test pass.
- You do NOT add unrequested features "just in case".
- After implementing, run the evidence the change requires (focused tests + touched modules) per the **Test evidence policy** (`references/stage-3-tdd.md` §"Test evidence policy"); the complete suite is the closure gate.

Expected output: implementation code + commit "feat: implement <postcondition>". When you finish:

"DONE. Implementation in <file>. Output of the evidence run:

<paste output with all tests green>

Commit: <hash>"
```

#### Fix packet (review re-entry — Stage 4 loop)

The implementer template above is reused to apply review fixes (loop with Stage 3). The orchestrator adds TWO mandatory things to the packet:

1. **Complete feedback**: the reviewer's findings and the user's context travel pasted in full in the packet (original text, rationale and provenance included). No softening edits — no friendly tone, no cuts, no "summary". The receiver verifies against the original evidence, not your paraphrase.
2. **A line at the start of the instructions**: *"Apply the `skills/cdad-cycle/references/receiving-feedback.md` protocol before touching code"*.

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

Task: write property tests that verify the spec's invariants with random inputs.

Context:
1. Approved spec, "Verifiable invariants" section (paste)
2. Interface (paste)
3. Project's property-testing library: <Hypothesis / fast-check / QuickCheck / etc.>
4. docs/systemPatterns.md

Strict rules:
- Permissions: edit ONLY in tests/. You do NOT look at implementation code.
- One invariant per property test, clear and legible.
- Reasonable volume: 100-1000 inputs per property.
- FIXED seed in config for reproducibility in CI.

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

Expected output: the review as FINAL TEXT with this structure (the orchestrator materializes `docs/specs/<feat>/review.md` from that text — Roles contract §5; the canonical mechanism is the "Orchestrator materialization protocol" in `references/re-entry.md`):

# Review — <feature>

Reviewer model: <model declaration, e.g.: mofgw/qwen3.7-plus>

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

The same reviewer role reviews a **plan draft** (intention + restrictions + the
plan object), not a diff. Its procedure lives in the pinned substage source
`packets/substages/reviewer-plan-review.md` (composed by `prepare` as
`substages/reviewer-plan-review.md`); this template only shows how to invoke it.
Do NOT restate the procedure here — reference the source.

```
python3 skills/cdad-cycle/scripts/cdad_packet.py prepare \
  --project-root <repo> \
  --role reviewer --substage plan-review \
  --contract-kind draft-plan \
  --contract-path <path to the draft plan> \
  --plan-version <version of the draft> \
  --objective "<atomic review task>"
```

The **three contract flags are required** (`--contract-kind draft-plan`,
`--contract-path`, `--plan-version`): without them `prepare` falls back to the
role default (`approved-feature-spec`) and the pairing guard rejects
`plan-review` over an approved contract (rc=2). Pass the rendered stdout
unchanged as the Task prompt. The packet is the execution contract: review the
draft plan's intention, constraints and plan in a session independent from the
author, without marking it approved or authorizing implementation.
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
## RUN RULES (mandatory)
- Iterate ONLY with minimal runs against a warm environment
  (Odoo: make test-one against the warm DB). test-clean /
  make test FORBIDDEN during iteration (the full suite is for the
  gate, not for debugging).
- Cycle: read the full failure -> written hypothesis -> ONE change -> ONE
  run. Never re-run without a change. Max 2 runs per failure without
  convergence: STOP and report findings (it is a signal to escalate, not
  a "one more run").
- Gate: ONE single full run on a fresh environment (Odoo: make test-all;
  single-module: make test-clean). Task budget: max ~15 minimal
  runs and 1 full one (default; the project calibrates it in systemPatterns).
- Run logs named under ~/tmp/ (never /tmp/) so the evidence
  is referenceable.
- Gate evidence: the line "0 failed, 0 error(s) of N tests" + commit of the
  tree that was run (recorded in the state file or commit message).
```

For the reviewer's packet, the equivalent block:

```text
## RUN RULES (review: 0 budget by default)
- If git diff --stat <evidence-run-commit>..HEAD shows only
  [STATE]/docs commits, the tree is identical: CITE the log (path + line).
  You do NOT re-run the suite.
- Only if the tree changed: ONE full run as new evidence.
- Static analyzers (lint, import-linter) consume no budget.
```

---

## Notes for the orchestrator when generating the packet

- **Fill in ALL the context** before handing it to the user. Don't tell them "paste the spec here"; paste it yourself in the packet (if you have access to the file).
- **Atomic task**: one postcondition per test-writer, one test per implementer, one diff per reviewer. Do NOT group unless the spec marks explicitly orthogonal postconditions.
- **Attaching files**: when you can, give exact paths. When the content fits, paste it inline in the packet.
- **Final line of the packet**: your turn always ends with the packet and the instruction to the user to "come back when the role finishes, with the output". Nothing else.

---

## If the user is in mode B (specific role)

You do not emit a handoff packet. You apply the strict rules of the requested role to yourself:

1. Identify which role was requested.
2. Find the corresponding section above.
3. Work respecting the "Strict rules".
4. Output in the "Expected output" format.

If in the middle of the work you notice you need something outside the role's permissions (e.g. a test-writer wanting to see implementation code), stop and report:

> *"As a test-writer I should not see the implementation code. If I genuinely need it, this suggests the spec or the interface are incomplete. What do you prefer: completing the spec, or authorizing me to see the code (losing phase isolation)?"*
