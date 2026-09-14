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

Claude Code has no declarative support for path restrictions (like OpenCode's `permission.edit: {"tests/**": deny}`). Instead, the `cdad-*` sub-agents use **PreToolUse hooks**:

### cdad-implementer

- `PreToolUse` hook matcher `Edit|Write` → invokes `~/.claude/cdad-scripts/path-guard.sh implementer`
- Behavior: blocks `Edit`/`Write` to `tests/**` (exit code 2)
- OpenCode equivalent: `permission.edit/write: {"tests/**": deny}`

### cdad-test-writer

- `PreToolUse` hook matcher `Read|Grep|Glob` → invokes `~/.claude/cdad-scripts/path-guard.sh test-writer-read`
- Behavior: blocks `Read`/`Grep`/`Glob` on `src/**` and `lib/**` (anti-gaming invariant, non-negotiable)
- `PreToolUse` hook matcher `Edit|Write` → invokes `~/.claude/cdad-scripts/path-guard.sh test-writer-write`
- Behavior: blocks `Edit`/`Write` everywhere except `tests/**`
- OpenCode equivalent: `permission.read/grep: {"src/**": deny, "lib/**": deny}` + `permission.edit/write: {"*": deny, "tests/**": allow}`

**Caveat:** the PreToolUse hooks are executed BEFORE the tool call, but they are not as strong as OpenCode's enforcement. A subagent that manages **to read the hook's JSON before executing it** could theoretically guess the blocked path. In practice, the guard script blocks the call itself (exit 2 prevents execution), but the guarantee is **behavioral**, not **structural** (as in OpenCode with runtime-level `permission`).

**Implication:** the invariant "the test-writer never sees `src/`" is **critical** (AP-1/AP-2, anti-gaming: a session that sees test and implementation at once aligns both instead of independently verifying the spec); it is preserved via the hook, but requires trust that the runtime honors exit code 2 (it does, verified empirically in validation-cdad-002.md).

## Re-delegation (NOT allowed)

CDAD explicitly forbids a sub-agent from delegating to another sub-agent (SPAWN GUARD, SKILL.md §4, incident of Aug 5, 2026).

Claude Code reinforces this: the `Agent` tool has a **depth limit** (default 3 layers below the main session). A subagent spawned by the orchestrator that tries to spawn another subagent will find it rejected after ~3 layers.

**CDAD rule in Claude Code:** if a subagent needs to delegate to another, it returns control to the orchestrator with a handoff packet (open prose, no delegation tools) and the ORCHESTRATOR decides the spawn. The anti-spawn guard (SKILL.md) explains it; in Claude Code it is reinforced by the platform's depth limit.

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
