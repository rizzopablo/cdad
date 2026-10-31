<!-- CDAD canonical source — EDITABLE (not a deployed agent).
     kind=adapter id=claude-code
     generator: scripts/cdad-generate.py (004-001 T3)
     consumers: every generated Claude Code agent (11: 5 roles × base/odoo + orchestrator)
     Scope: DECLARED LEGITIMATE DELTAS ONLY — same semantic contract as OpenCode,
     different mechanism. Never duplicates the role contract. -->
<!-- cdad-source:adapter:claude-code -->

<!-- cdad-section:frontmatter -->
Agent layout: `~/.claude/agents/cdad-<role>[-odoo].md`.
Frontmatter shape (generated):
- `name: cdad-<role>[-odoo]`, `description:` (one-line, from the role source).
- `tools:` — Read, Grep, Glob, Bash, Skill (+ Edit, Write for writer roles; Agent
  for orchestrator).
- `model:` — NOT emitted any more (006-003 PD-1e/INV-3): the generator has no
  model map. The installer deploys the agents as a copy of the
  staged bytes, verbatim and untransformed (it `cp -p`s them); `install.sh
  --help` says it: "the deployed bytes are the staged bytes ... the installer
  transforms nothing". No CC agent carries a `model:` line, before or after any
  install; the model of a role is the one configured in the runtime (see the
  model-provenance bullet below).
- Model provenance (PD-5): there is no per-role model — the CC agents carry no
  `model:` line — so the model of a critical dispatch is declared per call on
  the dispatch tool (its `model` parameter), and the dispatch records
  `model_configured`/`model_reported` with `provenance` (`null`/`unknown` with
  cause when unobserved). Each role runs the model its runtime configures;
  CDAD does not choose it. Honest limit (PD-15): the installer
  guarantees nothing about which model a role runs. The anti-bias guard makes
  the exemption of a role with no declared model explicit and visible —
  declared, never silent — and its source is the single authority
  `scripts/validate-subagents.sh` (trade-off recorded in `ADR-007`); this
  adapter references it and does not restate the rule.
- `hooks:` — PreToolUse path-guard blocks per role class, timeout 5. This is
  the map, declared once here; the generator emits the frontmatter from
  `CC_GUARDS` (`scripts/cdad-generate.py`) and the generated agents carry it
  (the emission REFERENCES this map, it does not restate the guard's
  decisions, globs or classifier). Pairs (matcher → guard mode):
  | matcher | guard mode |
  |---|---|
  | `Read|Grep|Glob` | `test-writer-read` |
  | `Edit|Write` | `test-writer-write` |
  | `Read|Grep|Glob` | `test-writer-odoo-read` |
  | `Edit|Write` | `test-writer-odoo-write` |
  | `Edit|Write` | `implementer` |
  | `Edit|Write` | `implementer-odoo` |
  The command resolves a single root (`~/.claude/cdad-scripts/path-guard.sh`,
  installed; repo source `scripts/claude-code-path-guard.sh`). Roles without
  hooks: architect, reviewer, scribe (base and odoo) and orchestrator — no
  route barrier (they do not edit/read the product across the barrier).
  NO Bash hook — permissive operational policy (owner decision 2026-09-29,
  reversing 002-009): no operation filtering; the Bash content-guard is retired.
No YAML permission block: path-scoping is expressed by the guard script, not by
frontmatter permission keys.
<!-- /cdad-section -->

<!-- cdad-section:permissions -->
Mechanism: `scripts/claude-code-path-guard.sh` — matcher per role; guards the
retained methodological invariants (test-writer does not read implementation;
implementer does not edit tests, including colocated tests) via the
Read|Grep|Glob and Edit|Write path guards.
PERMISSIVE operational policy (owner decision 2026-09-29, reversing 002-009):
NO operation filtering — the Bash content-guard hooks (`<role>-bash`) are
RETIRED from the frontmatter; bash runs unfiltered in CC too. Honest limit
(PD-15): fail-open on unknown role; it does not guarantee protection against
deliberate evasion; it is prevention of accidents, not isolation, and the
bash layer is permissive by decision — bash content reads/writes are NOT
blocked. The systematic barriers are the path guards + the role contracts.
Semantic coherence (PD-14): the CC artifact must not mention models that
`cdad_model_claude` does not produce; byte-equality across runtimes is NOT a
requirement.
<!-- /cdad-section -->

<!-- cdad-section:tool-loading -->
Skills are loaded with the `Skill` tool (capital S). The composed body's legacy
sentences use "Skill tool". Delegation: read-only and write-capable roles alike
via the `Agent` tool (`subagent_type: cdad-<role>`); path-scoping of writer roles
comes from the PreToolUse hook, not from the invocation mechanism.
<!-- /cdad-section -->

<!-- cdad-section:delegation -->
Delegation in Claude Code — the native mechanism, not the CLI adapter:

- **Mechanism (native).** First, resolve the stack suffix
  (`docs/.cdad-state.json.stack`), then dispatch with the `Agent` tool and
  `subagent_type: cdad-<role>` (role→subagent mapping: `cdad-architect`,
  `cdad-test-writer`, `cdad-implementer`, `cdad-reviewer`, `cdad-scribe`;
  use `cdad-<role>-<stack>` when the variant exists, else the generic
  `cdad-<role>`).
- **Byte-identical packet.** Dispatch the exact bytes that the installed
  `<skill-dir>/scripts/cdad_packet.py render` emits (`prepare`'s stdout or
  `render`'s re-emission) — the packet is passed byte-identical, never padded
  with extra instructions.
- **Dispatch vehicle (route C — explicit file backup).** A dispatch that carries
  no inline body emits the identification with
  `<skill-dir>/scripts/cdad_packet.py render --route C` on the published request
  (`--request .cdad/packets/<packet_id>/REQUEST.json`, inside the project root),
  and passes that stdout ALONE, unchanged: the identification is never
  recomposed, retranscribed or accompanied by the packet body. The complete
  render (route A) stays valid for the transport that requires it; C authorizes
  no mix with an inline body (A+C is rejected even when the inline coincides)
  and a divergent inline is never rescued by switching to C. Invent no route,
  marker or fallback and delete none: a rejection is reported, never repaired by
  changing the route.
- **Intra-runtime prohibition.** The CLI adapter (`cdad_delegate*.py` /
  `cli-delegation`) MUST NOT dispatch inside the same runtime
  (intra-runtime): it is only for another runtime or one without native
  delegation of its own. Same-runtime dispatch is the native `Agent` tool.
- **Model provenance (I8).** CDAD does not choose, invent or select a model:
  each role runs the model its runtime configures, and external
  delegation takes it from the delegation configuration (per destination and
  role). The orchestrator passes a model only if it comes from the environment
  configuration; a destination or role without an entry runs the destination's
  own default and the model is reported as not verifiable. Register the attempt
  with its fields (`runtime`, `model_configured`, `model_reported`, `session`;
  `null` or `unknown` when unobserved). The legitimate exit is the new-chat
  handoff where the user picks the model.
- **Receipt.** The native dispatch returns FINAL TEXT in this session, and the
  native route stages that FINAL TEXT the same way; the external route does not
  return a FINAL TEXT — its receipt comes from the runtime module. This bullet
  does not restate the steps: the re-entry wiring composed in this same body
  (from `sources/roles/orchestrator.md`) already names the command that stages
  those exact bytes under `.cdad/inbox` + `RESULT.json` and the single state
  transition, and the installed `<skill-dir>/references/re-entry.md` owns the
  Orchestrator materialization protocol; the receipt stays
  `semantic_status: pending` (approving nothing).
- **Entry of the coordinator (the other runtime).** For a destination that is
  NOT this runtime, dispatch through the entry
  `<skill-dir>/scripts/cdad_dispatch.py --project-root R --runtime X`: it reads
  the execution configuration of that runtime from its section of `runtimes.json`
  and returns an ENVELOPE. Consume that envelope by its `delivery`, with the
  procedure of `<skill-dir>/references/re-entry.md`, whose shape, vocabulary,
  combinations and historical rule are owned by
  `<skill-dir>/references/cli-delegation.md`; neither `rc` nor `termination`
  alone authorizes advancing, and the orchestrator never receives that delivery
  a second time. The retired `--exec-config` is NOT an option of the entry (a
  usage error that names `runtimes.json`).
- **Agent travels in the packet (D-ADP-4).** `prepare` resolves the agent and
  writes it as the `agent` field of `REQUEST.json`; the dispatch carries the
  packet byte-identical and the invocation resolves that agent, failing closed
  before dispatching when the derived agent is not published.
- **Server credential (D-ADP-1).** In `mode: server` the runtime module resolves
  the credential and injects it only into the environment of the client process
  it launches; it never reaches argv, the logs or the records.
<!-- /cdad-section -->

<!-- /cdad-source -->
