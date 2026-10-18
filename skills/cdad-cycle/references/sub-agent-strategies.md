# Sub-agent strategies — how to materialize isolated sessions per environment

CDAD requires that test-writer, implementer, reviewer, refactorer and scribe run in sessions that **do not share context**. How this is materialized depends on the environment.

## Why it matters

If the same agent writes the test and the implementation in the same session, it will align both: it adjusts the code so the test passes, or mentally adjusts the test to what its code will satisfy. The separation guarantees that the test is an independent oracle.

## Strategy per environment

### OpenCode

**Full native support**. The CDAD agents live versioned in the repo in `agents/` (OpenCode format, the reference runtime) and are installed to `~/.config/opencode/agents/` via `install.sh` — the repo is the single source of truth and the installed copy is regenerated from there, not hand-edited. Example definition of a sub-agent:

```yaml
---
description: Strict test-writer in CDAD. Only writes tests.
mode: subagent
permission:
  edit:
    "*": deny
    "tests/**": allow
  read:
    "src/**": deny       # Does NOT see implementation code
    "docs/specs/**": allow
    "docs/systemPatterns.md": allow
---
You are a test-writer in CDAD. You write a test that verifies a specific postcondition of the spec...
```

Minimal sub-agents to create (one per file):

- `architect` — read-only, discovery and Socratic brainstorm.
- `test-writer` — edit in `tests/`, does NOT see `src/` or implementation code.
- `implementer` — edit in implementation code, NOT in tests.
- `refactorer` — edit in code, NOT in tests; the proportional regression the change requires must stay green (evidence policy: `stage-3-tdd.md` §"Test evidence policy").
- `reviewer` — read-only, model different from the implementer's if possible.
- `scribe` — read-only, drafts Memory Bank updates.

Different model per sub-agent with the `model: provider/model-id` key.

Invocation: through the runtime's native dispatch mechanism, declared in the `delegation` section of its generated orchestrator agent.

### Claude Code

**Native support via sub-agents** (since ADR-008, 2026-08-13). Define it in `.claude/agents/<name>.md` with Claude Code frontmatter (NOT OpenCode — the syntaxes are different).

**Key differences from OpenCode:**
- Claude Code frontmatter does NOT have `permission` with globs (e.g.: `edit: {"tests/**": deny}`). Instead, it uses `tools:` as a flat allowlist (tool names: `Read`, `Grep`, `Edit`, `Write`, `Bash`, `Skill`, etc.).
- Path-scoping is reconstructed via `hooks.PreToolUse` that runs a guard script (`~/.claude/cdad-scripts/path-guard.sh <role>`) before each `Edit`/`Write`/`Read`/`Grep`.
- Model: the model of each role is the one configured in the environment; the concrete syntax of the `model:` field is declared by this runtime's agent layer. This skill names no model alias, provider or deployment gateway.

Invocation from the orchestrator through the runtime's native dispatch mechanism (declared in its `delegation` section). The sub-session does NOT see the parent agent's context.

**Full detail:** the runtime detail lives in the `delegation` section of the runtime's generated orchestrator agent (its adapter source); the historical verification detail is preserved as non-installable evidence under `docs/` (006-002 PD-9).

### Zed

**Partial support via Agent Panel**. Zed has an Agent Panel that allows multiple threads and profiles. The strategy:

1. Create **profiles** (Profile) in Zed with specific instructions for each CDAD role.
2. For each phase, open a **new thread** with the corresponding profile.
3. Manually pass only the relevant context (spec + interface for test-writer; spec + test for implementer; etc.).

Zed does not enforce per-glob permissions like OpenCode/Claude Code, so the discipline is the operator's (you as orchestrator): you give the implementer only the files it has to see.

If Zed has evolved and already supports granular permissions when you read this, use the native version.

### Any LLM in chat (single-session fallback)

If the environment does not support sub-agents (plain web chat, pure terminal), **you simulate isolation with explicit discipline**:

#### Option 1 — Separate conversations

The user opens a new conversation for each phase. Each conversation starts with:

> *"You are `<role>` in CDAD. Your only task is `<task>`. I'm passing you the necessary context and nothing else:*
>
> *<context pasted by the user, curated>"*

This is the closest to the ideal without native sub-agents. The friction is real (switching chats) but the quality justifies it.

#### Option 2 — Modes in a single conversation (last resort)

If the user insists on single-session, you declare explicit mode changes:

> *"Switching to **test-writer** mode. For this phase, I will NOT look at implementation code; I only work with the spec and the interface. If you ask me about the code, I'll remind you I'm in this mode."*

> *"Switching to **implementer** mode. Now I see the test and the interface. I will NOT modify the test."*

This is **less effective** than real isolated sessions because the LLM keeps memory of the previous context, but it at least formalizes the separation. The friction of the mode switch signals to the user that we are in an exception.

Tell the user:

> *"We are in single-session due to the environment. This is the mode with the least isolation guarantee. If at any point you can migrate to an environment with sub-agents (OpenCode, Claude Code), the process's performance improves noticeably."*

## Which strategy to recommend

| Environment | Recommended strategy |
|---------|------------------------|
| OpenCode | Native sub-agents `.opencode/agent/*.md` |
| Claude Code | Native sub-agents in `.claude/agents/` |
| Zed | Threads with profiles |
| ChatGPT, Claude.ai chat, etc. | Separate conversations (option 1) |
| Forced single-session | Explicit modes (option 2), with warning |

## How to start each isolated session

Generic template of the initial prompt for an isolated session:

```
You are a <role> sub-agent in CDAD. 

Your task is: <specific task of this phase>

Strict rules:
- <rule 1: e.g. do NOT look at implementation code>
- <rule 2: e.g. you only edit files in tests/>
- <rule 3>

Context you receive:
1. Approved spec: <content or path>
2. Interface: <content or path>
3. <other artifacts per role>

Expected output: <what you deliver when closing the session>
```

Adapt the rules and context per role. The rules are negotiable only if the project spec authorizes a specific exception.

## Permissions per role — cheatsheet

| Role | Edit | Read | Notes |
|-----|------|------|-------|
| architect | nothing (plan-only) | everything | discovery + Socratic brainstorm |
| test-writer | `tests/**` | spec, interface, systemPatterns | NOT `src/**` |
| implementer | implementation code | spec, tests, interface | NOT `tests/**` |
| refactorer | implementation code | full suite | NOT `tests/**`, suite always green |
| reviewer | nothing | everything | ideally model different from the implementer's |
| scribe | nothing | spec, diff, review, Memory Bank | drafts Memory Bank updates |

If the environment enforces these permissions per glob, great. If not, you as orchestrator respect these roles when directing each phase.

## Activation by stack — domain-specialized variants

Role delegation supports variants specialized by **stack**, activated by the
`stack` field of the state file `docs/.cdad-state.json`. With
`"stack": "odoo"`, the orchestrator delegates each role to its `*-odoo`
variant (`cdad-architect-odoo`, `cdad-test-writer-odoo`, `cdad-implementer-odoo`,
`cdad-reviewer-odoo`, `cdad-scribe-odoo`) instead of the generic agent. The
CDAD core (5-stage cycle, state machine, verdict tuple, model profile
contracts) **does not change** — the specialization is additive: the
variants are thin shells (frontmatter with paths scoped to Odoo modules and
a bash allowlist `make *`/`pre-commit *`/`pylint *`/`git *`, + loading the
role's Odoo skill) that preserve the generic role's directive.

- `stack` absent or with another value → delegation goes to the generic
  agents (`cdad-<role>`), default behavior unchanged.
- `stack: odoo` → `*-odoo` variants.
- The variants are installed with `install.sh` alongside the generic ones
  (`agents/cdad-*-odoo.md`) without touching existing agents.

Delegation decision rule: same as in §Roles contract §4 — if the
environment exposes sub-agents, delegation goes to the variant sub-agent
according to the active stack; session isolation and per-role model are
preserved.

### Parallel sessions of the same role

Parallel dispatch of several sessions of the same role **preserves
isolation**: each session still cannot see the others' work — the only thing
they share is the orchestrator's handoff, which dispatches, consolidates and
writes the state file (the sessions never touch it). Full protocol: decision
tree, owned/do-not-touch and final integration in `stage-3-tdd.md` §
"Parallel dispatch".
