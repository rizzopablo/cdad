# Specification — 019-004-project-layout-and-dispatch-intake

**Version:** draft-002  
**Status:** Draft for independent review and explicit approval.

## 1. Purpose and authority

Deliver three coordinated improvements:

1. Locate methodology artifacts through per-project configuration.
2. Resolve project declarations against the actual product repository root, independently of the coordinator’s working directory.
3. Validate a supplied received Route A/C dispatch with one command composing existing validation machinery.

Existing projects remain in place. `cdad/` becomes the default only when explicitly bootstrapping a genuinely new CDAD project.

### Confirmed decisions

- Existing projects must not be moved or rewritten. Use their configured location; retain `docs/` for recognizable unregistered legacy projects.
- Recognizable legacy markers are exactly `docs/.cdad-state.json` or `docs/cdad-policy.json`.
- Memory Bank files and `docs/epics/` or `docs/specs/` alone are insufficient: report an ambiguous layout rather than selecting legacy or new.
- Ordinary end-user documentation is not a CDAD marker.
- The methodology directory is project-local configuration resolved against the product repository root.
- `.cdad/` operational storage remains separate.
- Continuation is bound to the execution identity. The selected state must contain that execution and agree with its recorded policy path and snapshot.
- Before operational use, the effective policy must classify the methodology directory and intended methodology destinations as documentation. Incompatibility requires an actionable diagnostic and owner authorization for any policy change.
- Preserve existing CLI file-argument semantics.
- Validate the received dispatch, not merely valid files found on disk.
- Route C admits inert preamble and trailing text around exactly one declaration and its canonical identification block. Inline packet bodies, duplicate declarations or identifications and normalized mismatching values remain inadmissible.
- Structural validation does not establish semantic acceptance or filesystem isolation.

### Sources and proposal boundary

Admitted sources are the approved unit contract, recorded discovery and technical consultation, current specification and plan, independent draft review, the validated revision request and authorized repository implementation.

Source inventory for this revision:

- `.cdad/packets/019-004-project-layout-and-dispatch-intake-architect-draft-002/UNIT-CONTRACT.md`, especially “Owner-approved extension”.
- The validated packet’s Objective, containing the four owner-approved clarifications.
- `docs/specs/019-004-project-layout-and-dispatch-intake/discovery-notes.md`, “Owner decisions” and “Owner clarification”.
- `docs/specs/019-004-project-layout-and-dispatch-intake/architect-consultation-001.md`, technical mapping.
- `docs/specs/019-004-project-layout-and-dispatch-intake/plan-review-001.md`, findings 1–5.
- Repository implementation at revision `17a7283621d52a45f7488e5931448e5520fab0f1`.

**The locator schema, additional CLI surfaces and detailed transport grammar remain proposed design choices. Approval of this specification would approve them; the confirmed decisions above are not themselves approval of this complete draft.**

## 2. Global constraints

- Preserve existing project locations and historical artifacts; no migration or automatic registration.
- Keep `.cdad/` operational storage unchanged.
- Resolve project declarations against the explicit product repository root.
- Preserve existing CLI file-argument semantics and historical execution-context rules.
- Preserve role separation, approval gates, policy snapshots and independent verification.
- Never repair layout incompatibility by silently rewriting policy, widening permissions or changing projects.
- Do not claim semantic acceptance, delivery provenance or filesystem isolation from structural validation.
- No installation, deployment or publication is authorized by this feature’s approval.

## 3. Existing behavior and bounded delta

The inspected product currently:

- Hardcodes state and policy below `docs/`.
- Uses additional fixed methodology paths in lifecycle, continuity, guards, dispatch, result materialization, contract-link reporting and generation.
- Has no supported methodology-directory field in the inspected state or policy schemas.
- Canonicalizes an explicit product root and confines project declarations beneath it.
- Interprets existing CLI file arguments relative to the invocation directory.
- Already validates requests, execution contexts, published packets and canonical packet bytes.
- Does not offer a single command validating the actual received dispatch.
- Gives test and implementation classifications precedence over documentation classification.
- Validates execution identity against `state.execution` and records policy location, hash and snapshot in v2 execution contexts.

Relevant evidence:

- `skills/cdad-cycle/scripts/cdad_packet.py`, `classify_path`, `validate_state`, `_validate_v2_execution_document`, `_validate_v2_state`, `_select_execution` and `_resolve_active_execution`.
- `skills/cdad-cycle/scripts/cdad_result.py`, conventional state access and materialization.
- `skills/cdad-cycle/scripts/cdad_continuity.py`, state/policy access.
- `skills/cdad-cycle/scripts/cdad_guard.py`, state access.
- `scripts/claude-code-path-guard.sh`, state-path resolution.
- `scripts/cdad-generate.py`, operational detection and generation.

The change introduces shared location resolution and received-dispatch intake. It does not replace existing validation contracts.

## 4. Project-layout contract

### 4.1 Stable locator

Introduce the project-local control file:

```text
.cdad/project-layout.json
```

Its closed schema is:

```json
{
  "schema_version": 1,
  "methodology_dir": "cdad"
}
```

`methodology_dir` is a nonempty, normalized, repository-relative directory path. Nested directories are allowed.

Reject:

- Unknown fields, unsupported versions or malformed JSON, including duplicate keys.
- Absolute paths, backslashes, `.` or `..` components.
- Paths escaping the canonical repository root through symlinks.
- A directory equal to or beneath `.cdad/`.
- An existing target that is not a directory.

The locator identifies artifact placement. It does **not** classify paths or grant permissions.

Derive conventional children from the selected directory:

```text
<methodology_dir>/.cdad-state.json
<methodology_dir>/cdad-policy.json
<methodology_dir>/specs/
<methodology_dir>/epics/
<methodology_dir>/adr/
<methodology_dir>/projectbrief.md
<methodology_dir>/systemPatterns.md
<methodology_dir>/activeContext.md
<methodology_dir>/progress.md
<methodology_dir>/landscape.md
```

Other methodological children follow the same base. Explicit historical references remain literal repository-relative references; they are not rebased.

### 4.2 Resolution order and exact legacy signals

Apply this precedence:

1. **Locator present:** validate it and use its directory exclusively. Invalid metadata or missing artifacts required by the operation are errors. Never fall back to `docs/`.
2. **Locator absent, either fixed legacy marker present:** select `docs/`, without writing a locator.
3. **Locator absent, insufficient initialization evidence present:** report an ambiguous layout. Do not select legacy or propose a new initialization.
4. **Explicit new-project bootstrap with no recognized markers or insufficient initialization evidence, and affirmative confirmation that CDAD does not already exist elsewhere:** propose `cdad/`.

The only recognizable legacy markers are these exact paths:

```text
docs/.cdad-state.json
docs/cdad-policy.json
```

Either marker is sufficient to select the legacy location. This selection does not validate its contents or make an incomplete installation operational. A malformed marker, wrong filesystem type or absent counterpart produces the appropriate validation/configuration error when required; it does not make the project new.

The following fixed-location evidence is insufficient by itself and produces an explicit ambiguous-layout diagnostic when neither legacy marker nor locator exists. The list is closed, and it is checked by fixed location only, never by recursive discovery:

- Any conventional Memory Bank file listed in §4.1 under `docs/`.
- `docs/epics/` or `docs/specs/`.
- An unregistered `cdad/` methodology location.
- Any entry under `.cdad/packets/`.
- Any `.cdad/executions/<id>/` holding anything other than `continuity/` and `guards/`, checked one level deep: those two stores are operational bookkeeping of the continuity and guard layers, they record a session's own chain and decisions, they do not describe methodology placement, and they are written even before a layout is decided.
- Any entry under `.cdad/inbox/`.
- Any entry under `.cdad/runtime/results/`.
- Any entry under `.cdad/publication/`.

Locations under `.cdad/` that this list does not name — the locator itself, orchestration scratch space and any other operational file — are not examined and never make a project ambiguous. Dispatch records live under `.cdad/executions/<id>/dispatches/` and receipts under `.cdad/runtime/results/`, so both are covered by named entries.

Do not inspect repository-wide content to guess whether these shared names are methodological. Even a coinciding end-user `docs/specs/` name is not a legacy marker: it triggers clarification, not automatic CDAD recognition.

An ordinary `docs/` directory, ordinary end-user pages and `docs/adr/` alone are not CDAD markers or sufficient initialization evidence.

Detection uses fixed locations, not recursive discovery. Arbitrary custom locations cannot be discovered reliably without metadata. Bootstrap must ask whether CDAD already exists elsewhere; silence is not confirmation.

Recognizing a legacy location never overrides the execution-binding requirements in §4.5.

### 4.3 Read-only layout query

Add to the installed packet CLI:

```text
cdad_packet.py layout --project-root ROOT [--for-bootstrap]
```

Successful output is one JSON object:

```json
{
  "schema_version": 1,
  "project_root": "/canonical/product/root",
  "source": "registered",
  "methodology_dir": "process/cdad",
  "state": "process/cdad/.cdad-state.json",
  "policy": "process/cdad/cdad-policy.json"
}
```

`source` is `registered`, `legacy` or `new`.

- `new` is emitted only with `--for-bootstrap`, subject to §4.2.
- Uninitialized ordinary queries and ambiguous layouts fail explicitly.
- Exit 0 means placement was resolved, not that state, execution or policy passed operational validation.
- This command never creates directories, configuration, state or policy.

The query supports bootstrap and installed consumers without duplicating resolution logic. It does not authorize subsequent operations.

### 4.4 Bootstrap and policy compatibility

New-project bootstrap creates the selected methodology structure and locator using the existing bootstrap authorization. It does not overwrite existing metadata.

For newly proposed policies, classify the selected methodology directory as documentation while retaining applicable end-user documentation paths.

Before an operation uses the selected layout for execution, permissions or materialization:

1. Load and validate the effective policy through the existing applicable policy/context rules.
2. Require the selected methodology directory to be classified as documentation under the effective classifier.
3. Validate the operation’s conventional methodology destinations against that same classifier and existing artifact/role permissions.
4. Reject a destination classified as implementation, tests, private or otherwise incompatible/unclassified. A documentation classification does not override separate private-path protection.

Do not assume that adding a documentation root overrides a test or implementation root. Existing classifier precedence remains authoritative.

A compatibility failure must identify the selected directory or destination, the conflicting classification/policy rule and the corrective route: request owner-authorized policy reconciliation before retrying. It must not rewrite an accepted policy, grant an exception, select another layout or widen permissions.

A valid locator can therefore yield a successful placement query while operational use is blocked by policy incompatibility. The diagnostic must make that distinction clear.

### 4.5 Execution-bound continuation and control protection

Treat the locator as protected control metadata:

- Ordinary role edit permissions must not permit changing it.
- Invalid metadata must not cause a guard to choose a less restrictive fallback.
- No layout-repointing or migration operation is introduced.

For continuation, retain the execution identity already designated by the received request, packet, explicit admitted context or existing continuation binding. Do not replace that identity with one discovered in an alternative state.

For v2, load its canonical context by the designated execution identity under:

```text
.cdad/executions/<execution_id>/execution.json
```

Then require all of the following before continuing:

1. The state at the selected layout exists and validates.
2. Its `state.execution` binding contains the designated execution and satisfies the existing binding checks.
3. The selected conventional policy path agrees with the execution context’s recorded `policy.path`.
4. The effective policy passes the existing recorded snapshot/hash/history checks.
5. Layout-policy compatibility passes §4.4.

A missing selected state, missing execution binding, different execution, conflicting policy path or rejected snapshot fails closed.

In particular:

- If a custom locator disappears and legacy detection selects `docs/`, continuation of the previously designated custom-layout execution must still satisfy those checks.
- If a locator is altered to select another state, an unrelated active execution in that state cannot substitute for the designated execution.
- Never search other methodology directories, choose another execution, bootstrap a replacement context or switch product roots to make continuation pass.

Commands whose existing contract is state-only retain their current identity source; no new execution selector is introduced. Such a command cannot attest continuity with an earlier session identity that was never supplied or retained. This does not authorize it to rescue a known continuation conflict.

Preserve admitted historical v1 validation/context behavior without conversion. No new v1 preparation or Route C admission is introduced.

This does not claim detection of external replacement of an entire coherent project state, nor create a filesystem sandbox. Protection remains bounded by runtime mediation, role contracts and the identity actually available to the operation.

## 5. Repository-root contract

For new layout and intake commands, `--project-root` is required.

- Resolve that argument once to the canonical existing product root.
- Repository basenames have no special meaning.
- Methodology locations, packet declarations, execution locators and other project-declared references resolve against that root.
- Do not search parent directories or substitute the coordinator’s working directory.
- Preserve declared relative text in portable references and historical evidence.

Existing CLI file arguments—including `--request`, `--packet` and explicit `--execution-context`—retain their invocation-directory-relative behavior. Absolute arguments continue to work.

For intake:

- `--received FILE` names an invocation-directory-relative or absolute transport file.
- Paths declared **inside** the dispatch are product-root-relative.
- Explicit `--execution-context FILE` retains existing file-argument semantics and historical context-selection rules.

Help and effective instructions must explain this distinction.

## 6. Received-dispatch intake contract

### 6.1 Command and input boundary

Add:

```text
cdad_packet.py intake --project-root ROOT --received FILE|-
                     [--execution-context FILE]
```

`-` reads stdin as bytes. The command consumes one received dispatch, not a transcript containing several messages.

There is no route override: determine the route from the supplied input.

The caller must supply the actual received message representation. Do not substitute:

- `render` output,
- published `PACKET.md`,
- a reconstruction from metadata,
- or a transcript summary.

The command cannot prove input origin. It validates exactly the supplied representation.

If the runtime cannot expose the received message faithfully, report that limitation and use the existing manual intake procedure on the original message. Do not claim automated received-dispatch validation.

### 6.2 Route selection

Inspect the supplied message before product work:

- One Route A opening marker selects A unless the message also claims Route C.
- A Route C declaration and identification select C only without an inline packet.
- Duplicate markers, declarations or identification blocks, mixed routes and malformed packet claims fail.
- No packet claim produces the distinct “legacy consultation; not a CDAD dispatch” diagnostic. It accredits no commission.

Do not choose among candidates or search for another packet after rejection.

### 6.3 Route A

Compose the existing marker parser, request/context validation and canonical rendering.

1. Require exactly one opening and closing marker in the correct order.
2. Resolve the identified published `REQUEST.json` beneath `.cdad/packets/<packet_id>/`.
3. Apply existing request, contract, state and execution-context validation, including selected-layout continuation checks.
4. Compare supplied bytes from the opening marker through the message’s end against the **complete** canonical rendering.
5. Accept only exact equality.

A runtime preamble before the marker is inert. No trimming, line-ending conversion, reconstruction or normalization may make a divergent suffix pass.

An altered objective, instruction, scope or evidence requirement fails even with intact metadata.

Preserve admitted historical Route A context behavior. Do not silently supply a missing historical explicit context or upgrade v1.

Route A does not acquire a requirement to validate an unrelated on-disk packet body: its defining comparison is received body against the validated request’s rendering.

### 6.4 Route C

The owner-approved envelope admits:

- Optional inert preamble.
- Exactly one literal declaration line:

```text
Route C — explicit file backup
```

- One following fenced `json` identification object, with whitespace allowed between declaration and fence.
- Optional inert trailing text.
- No inline packet body or packet fragment.

“Inert” means outside the declaration/identification and grants no task authority. Wrapper text cannot override the validated request. It must not contain another declaration, candidate identification or inline packet claim; those are duplicate or mixed/partial input, not an inert wrapper.

The identification block has the complete field set and values generated by existing `render --route C` machinery:

- Reject duplicate JSON keys, unknown fields and malformed objects.
- JSON key order and insignificant JSON whitespace are not significant.
- Field values must agree without alteration. Do not normalize a mismatching path, identifier or root into agreement.
- Require the declared project root to equal the canonical explicitly selected root.

Then validate the one named published request, canonical v2 context and complete published packet using existing helpers and selected-layout continuation checks.

A v1 context produces the explicit Route-C-requires-v2 diagnostic. Do not convert it, select A or locate another context.

This explicitly replaces draft-001’s whitespace-only trailing restriction. Canonical identification with the ordinary runtime preamble and additional inert trailing text is admitted; wrappers do not become executable task instructions. `render --route C` output remains unchanged.

Compatibility evidence must include canonical output and a documented legitimate historical received representation with its provenance. If that representation cannot be recovered, record the missing evidence rather than inventing a historical fixture or declaring compatibility demonstrated.

### 6.5 Results and failures

Successful stdout contains one JSON object:

```json
{
  "schema_version": 1,
  "validation": "structural-dispatch",
  "route": "C",
  "packet_id": "example-packet",
  "execution_id": "example-execution",
  "project_root": "/canonical/product/root",
  "methodology_dir": "docs"
}
```

- Exit 0: structural dispatch validation passed.
- Exit 2: input, layout, identity, policy compatibility, context, contract or canonical comparison failed.
- No success object on failure.
- Stderr identifies the cause and safe corrective action without printing the dispatch body.

Success and rejection are read-only: no state transition, publication, receipt, ledger event, materialization, automatic registration or repair.

Retain existing comparator boundaries:

- `validate-packet --packet` compares the complete supplied file.
- Published-packet validation permits an inert preamble before its canonical marker.
- Route A intake permits that preamble in the received message.
- Route C wrapper tolerance never changes the complete canonical comparison of its named published packet.

## 7. Minimal design and affected surfaces

### Design choices

- **One methodology base rather than independent paths per artifact:** covers the actual family without a path-configuration framework.
- **Locator outside the selected directory:** avoids needing prior knowledge of the location being discovered.
- **Fixed legacy markers rather than content heuristics:** gives deterministic selection; insufficient shared names produce clarification rather than guessed recognition.
- **Shared resolver rather than scattered substitutions:** preserves lifecycle and guard consistency.
- **Execution-bound continuation rather than layout-only validation:** prevents a changed selection from substituting another state for a known execution.
- **Compatibility preflight rather than automatic policy adjustment:** keeps location configuration separate from authorization.
- **Intake composed from existing validators:** avoids a competing definition of a valid commission.
- **Metadata comparison for C; exact body comparison for A:** C identifies files while A carries the instruction body.
- **Inert C wrappers rather than whole-message equality:** preserves admitted transport wrappers without granting their text authority.
- **No repointing workflow:** preserves the no-migration boundary.

### Required operational integration

Use the selected layout in:

- Packet preparation, execution/state validation, unit transitions, status and orientation.
- Policy loading, proposal, classification and derived-agent protection.
- Continuity and guard state/policy access.
- Dispatch state access.
- Result receipt/materialization destinations.
- Contract-link and gap-report conventional specification lookup.
- Automatic stack selection.
- Bootstrap, Memory Bank, cycle, epic and lightweight guidance.

Relevant surfaces include:

```text
skills/cdad-cycle/scripts/cdad_packet.py
skills/cdad-cycle/scripts/cdad_result.py
skills/cdad-cycle/scripts/cdad_continuity.py
skills/cdad-cycle/scripts/cdad_guard.py
skills/cdad-cycle/scripts/cdad_dispatch.py
skills/cdad-cycle/scripts/cdad_contract_links.py
skills/cdad-cycle/assets/artifact-policy.json
scripts/cdad-generate.py
scripts/claude-code-path-guard.sh
```

Add a shared resolver module under `skills/cdad-cycle/scripts/`.

Materialization policy must express allowed destinations relative to the methodology base without expanding closed artifact-kind or role/substage permissions.

Update canonical instructions and regenerate affected distributions. Do not hand-edit generated agents. Update installable and domain-specific consumers where operational paths or intake instructions are affected.

Historical citations, this product’s end-user documentation and fixed historical test data are not operational paths to replace globally.

## 8. Observable promises and verification

### Promise A — Existing projects stay where they are; new projects receive the new default

**Property:** selection is explicit, deterministic and non-migrating.

- **PC-01:** A valid registered directory determines conventional methodology locations, without `docs/` fallback.
- **PC-02:** With no locator, either exact legacy marker selects `docs/` without registration, movement or rewriting. Selection does not bypass marker/content validation.
- **PC-03:** Explicit genuinely new bootstrap defaults to `cdad/`, records the chosen locator and leaves unrelated end-user documentation intact.
- **PC-04:** Invalid or ambiguous layouts fail without modification or implicit selection. Insufficient Memory Bank/spec/epic evidence is diagnosed as ambiguous; ordinary documentation alone does not establish legacy CDAD.

**Method:** combined.

**Acceptance:** black-box resolution checks establish the precedence and fixed signals; observed bootstrap following revised instructions produces the specified placement; independent contextual review finds no required migration or conflation of documentation and methodology.

**Evidence:** commands, outputs, exit codes, fixture-tree before/after evidence, bootstrap record and contextual review.

**Limits:** fixed-location detection cannot discover arbitrary unregistered custom directories. No automatic migration is promised.

### Promise B — The selected layout works through the lifecycle without weakening protection

**Property:** selection governs operational consumers and remains subordinate to execution identity and policy.

- **PC-05:** Preparation, dispatch/continuity access, receipt/materialization, conventional contract lookup and resting orientation consistently use the selected directory.
- **PC-06:** Policy classification, guards, derived permissions and stack detection use that layout. Operational use rejects policy-incompatible methodology locations/destinations before effects, with an actionable diagnostic and no automatic rewrite or permission widening.
- **PC-07:** Ordinary role edits cannot change the locator. Continuation requires the selected state to contain the designated execution and agree with its recorded policy path and snapshot checks. Missing/altered locator and alternative-state conflicts fail without searching, switching projects or modifying historical artifacts.

**Method:** executable.

**Acceptance:** a compatible configured-location lifecycle reaches coherent rest; policy/guard checks preserve role boundaries; a test/implementation-overlapped location is rejected without repair; designated continuation conflicts are rejected even when another state exists; legacy regressions pass.

**Evidence:** subprocess results, materialized destinations, state/status output, permission decisions, policy conflict diagnostics and unchanged-artifact comparisons.

**Limits:** no sandbox, live-repointing workflow or proof against coherent external metadata replacement. State-only operations cannot attest an earlier identity never supplied or retained.

### Promise C — The coordinator’s working directory does not redirect project declarations

**Property:** explicit product root governs declarations independently of invocation location.

- **PC-08:** Equivalent explicit product roots select the same project and give equivalent results from the root, its parent or an unrelated invocation directory, with arbitrary repository names.
- **PC-09:** Existing CLI file arguments retain their interpretation. Intake transport-file arguments remain distinct from product-relative dispatch declarations. Escaping declarations fail.

**Method:** executable.

**Acceptance:** black-box subprocess checks establish root independence and preserved argument semantics.

**Evidence:** exact working directories, arguments, exit codes and resolved identities.

**Limits:** runtime session relocation remains separate.

### Promise D — One command validates the supplied received A/C dispatch

**Property:** admission validates the supplied representation without weakening canonical or identity checks.

- **PC-10:** Valid A and C inputs succeed with the specified structural result, composing existing validators. C accepts inert preamble and trailing text around its one declaration/identification.
- **PC-11:** A rejects every divergent canonical suffix, including altered instructions beneath intact metadata.
- **PC-12:** C rejects mismatching identification, invalid publication/context and v1. Mixed, duplicate, incomplete and malformed claims fail without fallback. Wrapper tolerance does not admit duplicate identifications or inline packet fragments, nor normalize mismatching values.
- **PC-13:** Success and rejection leave project artifacts unchanged and retain comparator and historical-context boundaries.
- **PC-14:** Input absence, unreadable input and non-dispatch input produce explicit failure diagnostics, not accreditation.

**Method:** executable.

**Acceptance:** positive controls and distinct negative behaviors pass black-box tests. Canonical Route C output, an identified legitimate historical representation and the admitted inert wrappers are contrasted with duplicate/mixed/partial failures. Metadata-only checks do not substitute for full-body comparison.

**Evidence:** received fixtures, provenance for the historical representation, command output, exit codes, file-tree comparisons and focused historical regressions.

**Limits:** the command does not establish faithful native capture, semantic validity, provenance or permissions.

### Promise E — Installed consumers can use the command without rediscovering it

**Property:** effective guidance makes the installed procedure usable and consistent.

- **PC-15:** Effective role instructions identify the installed CLI and received-input procedure, preserve A/C and legacy distinctions, and state the input-origin limitation.
- **PC-16:** Bootstrap, cycle, epic, lightweight, role and affected specialized instructions agree on resolution, execution binding, policy incompatibility and C wrapper handling while preserving role and approval boundaries.

**Method:** combined.

**Acceptance:** an isolated installed-consumer exercise invokes intake without depending on the checkout; independent contextual review finds no conflicting operational requirement in affected effective consumers.

**Evidence:** installed-consumer commands, generation/distribution checks, contextual findings and declared review scope.

**Limits:** keyword matches do not prove comprehension. No universal native-export capability or new real-agent dialogue exercise is claimed.

## 9. Acceptance-of-use recipe

- **Contract:** independent test-writer derives black-box tests from the approved specification; reviewer evaluates committed behavior coverage.
- **Integration:** implementer supplies compatible configured-location and legacy lifecycle evidence, execution-bound conflict rejection and incompatible-policy rejection without mutation.
- **Use:** an isolated installed consumer supplies a controlled received dispatch directly to intake, then an altered version. Record acceptance/rejection and unchanged files. Include admitted Route C wrappers and distinguish their inert text from task authority.
- **Context:** independent reviewer assesses revised effective instructions and bounded use evidence.

Use evidence is bounded to the exercised installation and supplied representation. It is not native delivery-provenance evidence.

## 10. Failure handling and pending evidence

Stop rather than repair, migrate or silently select another source when:

- Layout metadata is invalid or initialization is ambiguous.
- Required selected artifacts are absent.
- Selected state lacks or conflicts with the designated execution.
- Selected policy location or snapshot conflicts with that execution.
- Policy does not classify the methodology location/destinations compatibly.
- Received input cannot be obtained faithfully.
- Dispatch input is mixed, duplicated, incomplete or divergent.

**VERIFY — runtime input acquisition:** no universal native-message export API is established. The orchestrator must identify the capture mechanism for any native-integration claim. This does not block the bounded file/stdin contract; it blocks claims that native capture was demonstrated.

**Pending — historical Route C representation:** before T3 acceptance, recover and identify a legitimate historical received representation, or report missing compatibility evidence to the orchestrator. Synthetic wrappers may test the newly explicit grammar but must not be presented as historical observations.

**Approval still required:** locator schema, layout query, intake interface and full revised specification/plan. The four recorded owner clarifications resolve design ambiguities but do not approve these drafts.

## 11. deferred-hardening

- **Migration and live repointing:** excluded to preserve existing-project boundaries.
- **Automatic custom-directory discovery:** requires registration or clarification, not heuristics.
- **Authenticated native-message provenance:** not supplied by file/stdin validation.
- **New filesystem sandbox:** outside scope.
- **Universal runtime capture/relocation adapters:** outside scope; unsupported capabilities remain explicit.
- **Concurrent external replacement:** no new hostile-writer or cross-file atomicity guarantee.
- **ADR index reconciliation:** optional review finding 5; unrelated maintenance outside this feature. No ADR status is decided here.
- **Broad performance benchmarks, fuzzing and equivalent-scenario quotas:** no corresponding committed promise; use focused verification and proportional regression.

No deferral postpones a postcondition above.

---
