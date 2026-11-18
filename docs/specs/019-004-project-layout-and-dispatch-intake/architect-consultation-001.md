# role-report

**Route C validated.** REQUEST validation passed; the complete published packet and received identification matched canonical renders. The execution context is v2. No specification drafted or approved.

## Findings

### 1. Existing metadata does not register a methodology directory

The inspected implementation has:

- Fixed state and policy locations: `docs/.cdad-state.json` and `docs/cdad-policy.json` (`skills/cdad-cycle/scripts/cdad_packet.py:223,243`).
- A state template without a methodology-location field (`skills/cdad-cycle/assets/state-template.json:1–20`).
- Policy metadata describing **path classifications**, not artifact locations. Its top-level schema currently rejects additional fields (`cdad_packet.py:554–573`).
- An execution snapshot carrying `policy.path`, but operational policy loading still uses the fixed location (`cdad_packet.py:1321–1328,2556–2583`).

Therefore, `documentation_roots[0]` must **not** be treated as the methodology directory: it describes admissible documentation paths and can represent unrelated documentation.

**VERIFY:** no supported machine-readable layout registry was found in the inspected product sources. The owner’s reference to “registered directories” needs a precise implementation contract; an existing registry must not be invented.

### 2. Changing the two constants would be insufficient

Affected executable surfaces include:

- **Packet lifecycle:** direct state reads/writes; spec/epic contract paths; plan validation; epic membership; status and orientation (`cdad_packet.py:913,1085,2034–2047,5662,6097,7133–7147,10036–10044,10894`).
- **Results and materialization:** state access and allowed output destinations (`skills/cdad-cycle/scripts/cdad_result.py:73,642,817–823,1011`; `assets/artifact-policy.json:4–15`).
- **Continuity and guards:** separate state/policy constants (`cdad_continuity.py:144–148`; `cdad_guard.py:141`).
- **Dispatch and contract-link reporting:** direct state/spec paths (`cdad_dispatch.py:1162`; `cdad_contract_links.py:1060,1297,1710`).
- **Runtime protection:** Claude Code checks only `$PROJECT_ROOT/docs/cdad-policy.json` before selecting its dynamic guard (`scripts/claude-code-path-guard.sh:50–56`). Missing this change could silently select legacy behavior.
- **Generation:** automatic stack selection reads the fixed state location (`scripts/cdad-generate.py:847–864`).

Effective instructions also require alignment: bootstrap, state detection, epic references, materialization guidance, lightweight guidance, role sources, generated agents and examples. For example, current bootstrap creates `docs/` explicitly (`references/bootstrap.md:66–82`).

Historical citations and CDAD’s own end-user documentation are different from operational paths. A global `docs/` replacement would damage that distinction.

### 3. Repository-relative declarations and CLI file arguments differ today

The product already canonicalizes an explicit repository root and confines declared project paths beneath it (`cdad_packet.py:279–310`).

However, existing `--request` and explicit `--execution-context` arguments retain **invocation-directory-relative** interpretation (`cdad_packet.py:10598–10610,10621,10888`).

Observed from the parent directory:

- Product-relative `--request .cdad/.../REQUEST.json`: **rc 2**, “packet request not found”.
- Absolute request path, with the same `--project-root cdad`: **rc 0**.

Consequently, an explicit root alone does not currently make every CLI input repository-relative. Preserve that distinction deliberately rather than silently changing established commands.

### 4. Most validation machinery already exists

Reusable functions include:

- `_canonical_block`: validates marker structure and extracts the untouched packet suffix (`cdad_packet.py:2223–2270`).
- `validate_request`: checks state, identities, instructions, contract paths and exact contract hashes (`1882–2057`).
- `verify_published_packet`: validates the request and compares the complete published suffix against canonical rendering (`2273–2331`).
- Route C helpers: enforce the published request location, canonical v2 context and verified packet (`10658–10775`).

The missing surface is **validation of the actual received dispatch**, including route selection and identification comparison. `render --route C` produces a valid identification; it does not establish that the received identification matches it.

One compatibility boundary is already tested: `validate-packet` compares the whole supplied file, whereas published-packet admission permits a preamble before its unique marker (`tests/test_010_004_t3_red.py:713–843`). Do not merge those semantics accidentally.

## Recommended design — proposals, not owner decisions

1. **Introduce one shared, repository-root-bound layout resolver.** Parameterize only the methodology directory and derive its conventional children. This covers the affected family without introducing a configurable path for every artifact.

2. **Use a stable project-local locator outside that movable directory.** A small optional registry under `.cdad/` is a reasonable proposal; its filename and field names remain **VERIFY/design choices**, not existing interfaces. Putting the only locator inside the directory it locates creates a discovery problem.

3. **Preserve old projects without rewriting them.**
   - Registered layout: use it exclusively.
   - Unregistered, recognizable legacy project: retain `docs/`, without writing configuration automatically.
   - Genuinely new bootstrap: default to `cdad/` and record its selected layout.
   - Conflicting or unrecognized existing layouts: diagnose and request explicit registration, not migration or filesystem-wide discovery.
   
   Existing policies, packets, hashes and historical references remain unchanged. `.cdad/` operational storage stays where it is.

4. **Add intake to the installed packet CLI**, rather than creating another validator or requiring checkout discovery. Proposed shape: an intake subcommand receiving an explicit product root and raw dispatch bytes through stdin or a file.

   Route A should validate the received suffix byte-for-byte. Route C should validate the received identification against its one designated publication and the complete canonical packet. Reject mixed routes, ambiguous identification and malformed packet claims without fallback.

   Keep success read-only and narrowly described: **structural dispatch validation**, not delivery provenance, semantic acceptance or filesystem isolation.

5. **Treat the layout locator as control metadata.** Define its protection and behavior during an active execution. Repointing it must not silently select another state or policy. Preserve existing policy snapshots and reserved-edit protections.

## Consequential questions before drafting

1. **Metadata contract:** approve a stable locator and legacy fallback rule, or identify the existing registry intended by “project metadata”. This blocks a precise compatibility contract.

2. **Received-input boundary:** how does the runtime provide the actual prompt to the intake command? A manually rebuilt canonical message cannot prove what was received. If raw-message export is unavailable, report that limitation explicitly.

3. **CLI compatibility:** is repository-relative behavior required for new intake declarations only, or also for existing CLI file arguments? I recommend preserving historical argument semantics and resolving dispatch-declared paths against the explicit product root.

4. **Route C grammar:** define identification comparison, permitted preamble and trailing content. Current role instructions require matching metadata; they do not justify inventing additional formatting restrictions.

## Verification strategy to carry into specification

- **Layout resolution — executable:** registered custom location, unchanged legacy project, and new `cdad/` bootstrap resolve consistently; invalid or ambiguous configuration fails without writes.
- **Lifecycle integration — executable:** preparation → intake → receipt/materialization → resting-state orientation uses the selected directory. Include policy classification and runtime guards, not just rendering.
- **Root independence — executable:** equivalent explicit roots work from a parent or unrelated invocation directory, using arbitrary repository basenames.
- **Dispatch integrity — executable:** valid A/C accepted; altered body under intact metadata, mismatched identification, duplicates, partial/mixed routes and C/v1 rejected. Retain historical locator behavior and comparator boundaries.
- **Effective instructions — combined:** installed-consumer execution plus independent contextual review establishes that agents can locate the command and follow the selected layout without contradictory guidance.

Expected evidence: exact commands, exit codes, relevant output and before/after file evidence. Existing focused protections include `test_010_004_t2_red.py`, `test_010_004_t3_red.py`, `test_010_004_t5_e2e.py`, `test_010_000_continuity_relative_root.py` and `test_019_002_resting_orientation.py`. No test quota is proposed.

## Execution evidence

- Executed `python3 scripts/cdad_packet.py validate-request`, `validate-packet` and `render --route C`, with the supplied request and explicit product root. All returned **rc 0**; validators produced no output.
- Executed in-memory canonical-byte comparisons: **PASS** for complete `PACKET.md` and received Route C identification.
- Executed the parent-directory comparison described above: **rc 2 / rc 0**, confirming current argument semantics. Exact command lines and outputs are retained in this session’s tool records.
- `git status --short` before and after: only pre-existing `M docs/.cdad-state.json`.
- **Files modified by this role:** none. **Commit created:** none.
- Examined revision: `bcc5329c0e5fe1c59e0fdd418bea29d125d142cf`.
- No test suite run; this was read-only consultation, not implementation acceptance.