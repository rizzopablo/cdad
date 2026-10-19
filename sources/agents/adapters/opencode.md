<!-- CDAD canonical source — EDITABLE (not a deployed agent).
     kind=adapter id=opencode
     generator: scripts/cdad-generate.py (004-001 T3)
     consumers: every generated OpenCode agent (11: 5 roles × base/odoo + orchestrator)
     Scope: DECLARED LEGITIMATE DELTAS ONLY. This file never duplicates the role
     contract (that lives in sources/roles/*.md) — it declares how the contract is
     mechanically expressed in OpenCode. -->
<!-- cdad-source:adapter:opencode -->

<!-- cdad-section:frontmatter -->
Agent layout: `~/.config/opencode/agents/cdad-<role>[-odoo].md`.
Frontmatter shape (generated):
- `description:` — one-line role summary (from the role source).
- `mode: subagent` (orchestrator: `mode: all` + `permission: allow`).
- `model:` — NOT emitted any more (006-003 PD-1e/INV-3): the generator has no
  model map, and the installer transforms no agent bytes. No
  OpenCode agent fixes a model; the model of each role is the one configured in
  the runtime, and external delegation takes it from the delegation
  configuration (per destination and role).
- `steps: 300` — per-agent step ceiling emitted on every role subagent (5 roles
  x base/odoo; the orchestrator, `mode: all`, gets none). Declared ONCE here:
  a runaway guard, not a work budget — it forces a text-only report after
  ~1.5x the highest legitimate session observed (203), far below the runaway
  loops (996, 2167). The generator READS this value; it is never hardcoded.
- `temperature: 0.1` (reviewer only).
- Optional top-level `edit: deny` mirror for read-only roles — INERT at runtime;
  it stays only as a marker of the role's read-only state (cdad-010 P2/A6).
- `permission:` block — see the `permissions` section.
Classification lever (cdad-010 P1): `write: ask` — the plugin's classifier reads
it; the runtime does NOT evaluate it today (the write tool requests "edit").
WATCH RULE: if a future OpenCode version evaluates `write` at runtime, this lever
starts generating prompts — revisit on version migration.
<!-- /cdad-section -->

<!-- cdad-section:permissions -->
Bash block: YAML under `permission:` — PERMISSIVE operational policy (owner
decision 2026-09-29, reversing 002-009): the composed block is the single
catch-all `"*": allow` derived from the role class's host source (reader:
architect.md; writer: test-writer.md — PD-1). No operation-level filtering is
generated; honest limit (PD-15): declared, NOT a sandbox — bash can read or
write anything; the systematic guards are the path maps below and the role
contracts.
Composition rules:
- Path globs for `read`/`edit`/`grep` keys come from the role source; the matcher
  escapes `{ }` — never emit braces. These maps are the retained barriers:
  read-only roles deny edit; the test-writer edits tests only and keeps the
  implementation invisible to read/grep; the implementer edits everything
  except tests (odoo included — models/views are its scope).
Mechanism limit (declared, not sold as sandbox): path matching on
Read/Edit/Write/Grep only; bash is permissive by owner decision 2026-09-29.
<!-- /cdad-section -->

<!-- cdad-section:tool-loading -->
Skills are loaded with the `skill` tool (lowercase). The composed body's legacy
sentences use "skill tool". Delegation: all cdad roles are task-able via the
`write: ask` lever (cdad-010/ADR-009); the `delegate` channel may be dead on
no-credit deploys — the orchestrator source decides the mechanism.
<!-- /cdad-section -->

<!-- cdad-section:delegation -->
Delegation in OpenCode — the native mechanism, not the CLI adapter:

- **Mechanism (native).** First, resolve the stack suffix
  (`docs/.cdad-state.json.stack`), then dispatch with the `task` tool and
  `subagent_type: cdad-<role>` (role→subagent mapping: `cdad-architect`,
  `cdad-test-writer`, `cdad-implementer`, `cdad-reviewer`, `cdad-scribe`;
  use `cdad-<role>-<stack>` when the variant exists, else the generic
  `cdad-<role>`).
- **Byte-identical packet.** Dispatch the exact bytes that the installed
  `<skill-dir>/scripts/cdad_packet.py render` emits (`prepare`'s stdout or
  `render`'s re-emission) — the packet is passed byte-identical, never padded
  with extra instructions.
- **Intra-runtime prohibition.** The CLI adapter (`cdad_delegate*.py` /
  `cli-delegation`) MUST NOT dispatch inside the same runtime
  (intra-runtime): it is only for another runtime or one without native
  delegation of its own. Same-runtime dispatch is the native `task` tool.
- **Model provenance (I8).** CDAD does not choose, invent or select a model:
  the model of each role is the one configured in the runtime, and external
  delegation takes it from the delegation configuration (per destination and
  role). The orchestrator passes a model only if it comes from the environment
  configuration; a destination or role without an entry runs the destination's
  own default and the model is reported as not verifiable. Register the attempt
  with its fields (`runtime`, `model_configured`, `model_reported`, `session`;
  `null` or `unknown` when unobserved). The legitimate exit is the new-chat
  handoff where the user picks the model.
- **Receipt.** The native dispatch returns FINAL TEXT in this session, and
  every route stages that FINAL TEXT the same way. This bullet does not
  restate the steps: the re-entry wiring composed in this same body (from
  `sources/roles/orchestrator.md`) already names the command that stages
  those exact bytes under `.cdad/inbox` + `RESULT.json` and the single state
  transition, and the installed `<skill-dir>/references/re-entry.md` owns the
  Orchestrator materialization protocol; the receipt stays
  `semantic_status: pending` (approving nothing).
- **Entry of the coordinator (the other runtime).** For a destination that is
  NOT this runtime, dispatch through the entry
  `<skill-dir>/scripts/cdad_dispatch.py --project-root R --runtime X`: it reads
  the execution configuration of that runtime from its section of `runtimes.json`
  and returns the FINAL TEXT, which is staged through the receipt route above.
  The retired `--exec-config` is NOT an option of the entry (a usage error that
  names `runtimes.json`).
- **Agent travels in the packet (D-ADP-4).** `prepare` resolves the agent and
  writes it as the `agent` field of `REQUEST.json`; the dispatch carries the
  packet byte-identical and the invocation resolves that agent, failing closed
  before dispatching when the derived agent is not published.
- **Server credential (D-ADP-1).** In `mode: server` the runtime module resolves
  the credential and injects it only into the environment of the client process
  it launches; it never reaches argv, the logs or the records.
<!-- /cdad-section -->

<!-- /cdad-source -->
