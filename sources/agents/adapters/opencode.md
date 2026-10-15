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
- `model:` — emitted from `scripts/cdad-models.sh` (the only map; optimus default
  by the generator); install.sh REWRITES this field at install time from the
  profile given as explicit parameter (profile = install input, not a hidden
  machine effect).
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

<!-- /cdad-source -->
