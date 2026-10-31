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
Frontmatter shape (generated, OpenCode V2 — 009-002):
- `description:` — one-line role summary (from the role source).
- `mode: subagent` (orchestrator: `mode: all`).
- `permissions:` — a LIST of `{action, resource, effect}` entries (V2). The V1
  `permission:` map made the runtime ignore the user's `model:`; the emitted
  rules keep the same globs, effects and order (PC-2). The orchestrator's
  permissive policy is the single catch-all entry
  `{action: "*", resource: "*", effect: allow}` (PC-4).
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
- `request: body: temperature: 0.1` (reviewer only). The request body is the
  reserved carrier; no top-level `temperature:` is emitted (PC-3).
- `permission:` block — RETIRED (V1): see the `permissions` section.
- `write` key — NOT emitted (006-005 U6-7). OpenCode v2.0.27 evaluates `write`
  for the write tool together with `edit` and the last matching rule wins, so a
  trailing entry would override the role's path policy. The cdad-010 P1
  classification lever is retired (its own watch rule was fulfilled).
<!-- /cdad-section -->

<!-- cdad-section:permissions -->
Bash block: entries with `action: shell` inside the V2 `permissions:` list —
PERMISSIVE operational policy (owner decision 2026-09-29, reversing 002-009):
the composed policy is the single catch-all `{resource: "*", effect: allow}`
derived from the role class's host source (reader: architect.md; writer:
test-writer.md — PD-1). No operation-level filtering is generated; honest limit
(PD-15): declared, NOT a sandbox — bash can read or write anything; the
systematic guards are the path maps below and the role contracts.
Composition rules:
- Path globs for the `read`/`edit`/`grep` actions come from the role source; the matcher
  escapes `{ }` — never emit braces. These maps are the retained barriers:
  read-only roles deny edit; the test-writer edits tests only and keeps the
  implementation invisible to read/grep; the implementer edits everything
  except tests (odoo included — models/views are its scope).
Mechanism limit (declared, not sold as sandbox): path matching on the
`read`/`edit`/`grep` actions only; shell is permissive by owner decision
2026-09-29.
<!-- /cdad-section -->

<!-- cdad-section:tool-loading -->
Skills are loaded with the `skill` tool (lowercase). The composed body's legacy
sentences use "skill tool". Delegation: all cdad roles are task-able with the
runtime's subagent tool (P3, 006-005 U6-7: the invocation does not need the
retired `write: ask` lever); the `delegate` channel may be dead on no-credit
deploys — the orchestrator source decides the mechanism.
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
