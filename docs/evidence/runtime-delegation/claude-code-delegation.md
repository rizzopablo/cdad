<!-- 006-002 PD-9 — non-installable evidence. NOT part of the skill tree:
     `install.sh` never ships `docs/**`. The rule in force lives in the
     `delegation` section of the generated runtime orchestrator agent. -->

# Historical evidence — Claude Code delegation reference (withdrawn from the skill)

**Status: non-installable historical evidence (006-002 PD-9).** This document
preserves, in full, the runtime reference `claude-code-delegation.md` that lived in the
installable skill tree (`skills/cdad-cycle/references/`) until 006-002
withdrew it. It is historical / verification material from 005-004 / 005-009 / 005-010; it is
**not installed** (nothing under `docs/**` is shipped by `install.sh`), and no
installable skill text points to it.

It also preserves the sub-agent → sub-agent (sub-subagent) spawn
prohibition (SPAWN GUARD) and the recorded incident that motivated it.

The delegation rule **in force today** is not here: each runtime's orchestrator
agent declares it in its `delegation` section (generated from
`sources/agents/adapters/*.md`) — the native dispatch mechanism, the
role→sub-agent mapping, the byte-identical packet pass, the intra-runtime
adapter prohibition, the model declaration (D-3) and the receipt. The
transport-equivalence receipt lives in the skill
(`references/re-entry.md`). What follows is the withdrawn detail, kept as
evidence.

---

# Claude Code Delegation — Role mapping to sub-agents

**Companion document to `SKILL.md` §4 (Delegation decision rule).**

When you run CDAD in Claude Code and have native `cdad-*` sub-agents installed in `~/.claude/agents/`, this document details how to delegate to them.

## Mechanism: the `Agent` tool

Claude Code exposes the `Agent` tool for spawning subagents. The orchestrator invokes it directly like any other tool call — there is no Python module to import; the invocation is a tool call with `subagent_type` and `prompt` as parameters (e.g. delegating test-writer RED with `subagent_type: cdad-test-writer` and the full handoff packet as `prompt`).

In markdown/prose, so that Claude Code interprets it:

```
Invoke the Agent tool with subagent_type: cdad-test-writer
```

## Role → subagent_type mapping

| Role | subagent_type | Tool | Model | Notes |
|-----|---|---|---|---|
| architect | `cdad-architect` | Agent | sonnet (optimus) | read-only; no hooks required |
| test-writer | `cdad-test-writer` | Agent | sonnet (optimus) | write-capable; path-scoping hooks |
| implementer | `cdad-implementer` | Agent | haiku (optimus) | write-capable; hook blocks `tests/**` |
| reviewer | `cdad-reviewer` | Agent | opus (optimus, different from implementer) | read-only; no hooks required |
| scribe | `cdad-scribe` | Agent | sonnet (optimus) | read-only; no hooks required |
| refactorer | `cdad-implementer` + `tdd_substage: refactor` | Agent | haiku (optimus) | Sub-mode of the implementer; same subagent_type with modified context |

## State-passing (fresh sessions)

Claude Code sub-agents start **without the orchestrator's context**, just like in OpenCode. The handoff packet must contain EVERYTHING needed:

- **Atomic task** (one postcondition, one test, one diff — don't group)
- **Spec inline or path** (`docs/specs/<id>/spec.md`)
- **Interface/signature** if applicable
- **Strict role rules** (§2 table of the Roles contract in SKILL.md)
- **Expected output and format**
- **`tdd_substage` field** of the state file if the role uses it (test-writer AUDIT/POST-AUDIT/RED, implementer GREEN/REFACTOR)

The subagent can read `docs/.cdad-state.json` and `docs/specs/<id>/` by itself; don't assume it remembers anything from the previous session.

## Path-scoping in Claude Code (important)

Claude Code has no declarative support for path restrictions (like OpenCode's `permission.edit: {"tests/**": deny}`). Instead, the `cdad-*` sub-agents carry **PreToolUse hooks** wired in their frontmatter. The **map** — which
role carries hooks, its `matcher`, the guard mode and the root the command
resolves — is declared **once** in its owners
(`sources/agents/adapters/claude-code.md` and `CC_GUARDS` in
`scripts/cdad-generate.py`); this document references that map and does not
restate it.

The current mechanism is the guard v2 (`scripts/claude-code-path-guard.sh`): it
**classifies** a path with the **project policy** (`docs/cdad-policy.json`) —
`cdad-policy` — instead of fixed globs, so which roots are "implementation" and
which are "tests" comes from the policy the project declares. `Grep`/`Glob` are
allowed only when **scoped** to a bounded `path` (a search with no `path` is
refused), and the guard is **fail-closed**: without a classifier it blocks with
no fallback (INV-3). The retired v1 globs (`src/**`, `lib/**`) are **superseded**
and are no longer the mechanism.

### cdad-implementer

- `PreToolUse` hook matcher `Edit|Write` → invokes `~/.claude/cdad-scripts/path-guard.sh implementer`
- Behavior: refuses `Edit`/`Write` to a path the project policy classifies as tests
- OpenCode equivalent: `permission.edit/write: {"tests/**": deny}`

### cdad-test-writer

- `PreToolUse` hook matcher `Read|Grep|Glob` → invokes `~/.claude/cdad-scripts/path-guard.sh test-writer-read`
- Behavior: refuses `Read`/`Grep`/`Glob` on a path the project policy classifies as implementation; an unscoped `Grep`/`Glob` is refused (a bounded `path` is required)
- `PreToolUse` hook matcher `Edit|Write` → invokes `~/.claude/cdad-scripts/path-guard.sh test-writer-write`
- Behavior: refuses `Edit`/`Write` outside the tests root of the project policy
- OpenCode equivalent: `permission.read/grep` denies the implementation roots and `permission.edit/write` denies everything except the tests root

**Scoped claim on the refusal code.** The guard signals a refusal with exit
code 2, and that refusal was observed in an **interactive** Claude Code session
(`findings/validation-cdad-002.md`). Whether Claude Code honors `exit 2` in
**non-interactive** (`-p` / print / headless) mode is **unknown** — not
verified — and is preserved as unknown with cause (PD-8, VERIFY 1): the claim
that the runtime honors `exit 2` is scoped to the interactive observation and is
not extended to `-p`.

**Caveat:** the PreToolUse hooks run BEFORE the tool call, but they are not as
strong as OpenCode's enforcement. A subagent that manages **to read the hook's
JSON before executing it** could theoretically guess the blocked path. In
practice, the guard script refuses the call itself; the guarantee is **behavioral**, not
**structural** (as in OpenCode with runtime-level `permission`).

**Implication:** the invariant "the test-writer never sees the implementation
root" is **critical** (AP-1/AP-2, anti-gaming: a session that sees test and
implementation at once aligns both instead of independently verifying the spec);
it is preserved via the hook, subject to the scoped claim above about the
non-interactive mode.

## Re-delegation (NOT allowed)

CDAD explicitly forbids a sub-agent from delegating to another sub-agent (SPAWN GUARD, SKILL.md §4, incident of Aug 5, 2026).

Claude Code reinforces this: the `Agent` tool has a **depth limit** (default 3 layers below the main session). A subagent spawned by the orchestrator that tries to spawn another subagent will find it rejected after ~3 layers.

**CDAD rule in Claude Code:** if a subagent needs to delegate to another, it returns control to the orchestrator with a handoff packet (open prose, no delegation tools) and the ORCHESTRATOR decides the spawn. The anti-spawn guard (SKILL.md) explains it; in Claude Code it is reinforced by the platform's depth limit.

### External delegation (authorized) vs sub-agent recursion

External delegation — a coordinator handing a prepared packet to a role session in ANOTHER CLI (coordinator → worker, between CLIs) — is authorized and is not recursion of subagents inside the same runtime. A delegation does not expand authority or scope, and the worker does not write the state (`docs/.cdad-state.json`). A separate session or CLI is not a sandbox: it does not guarantee isolation nor another model family.

## Handoff packet (fallback if there is no Agent tool)

If for some reason Claude Code does not expose the `Agent` tool (e.g. the user opted out of subagents), use the handoff packet (prose pasteable into a new chat):

- Copy the content of `references/handoff-prompts.md` for the role
- Paste it into a **new** chat (separate session, manual)
- The role starts in that chat with strict rules applied behaviorally (no hooks)

## Verification (ADR-008)

The end-to-end validation of this delegation lives in spike `cdad-002-validate-claude-code-subagents` (similar to `cdad-001` for OpenCode). Probes per role include:

1. **Creation and naming**: every agent installed in `~/.claude/agents/` exists and has the correct name.
2. **Frontmatter**: correct tools, correct model (by profile), hooks present (implementer/test-writer).
3. **Hook execution**: path-guard.sh runs and blocks as expected (probes with attempted tries against blocked paths).
4. **End-to-end**: a real mini-feature run with the 5 subagents, artifacts produced per stage, no illegal re-spawn.

Result documented in `findings/validation-cdad-002.md`.
