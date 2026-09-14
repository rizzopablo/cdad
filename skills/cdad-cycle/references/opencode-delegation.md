# OpenCode delegation — materializing isolated sessions with native sub-agents

When the environment is OpenCode and the `cdad-*` sub-agents are installed
(`~/.config/opencode/agents/cdad-*.md`, installed via the repo's `install.sh`),
the orchestrator can delegate the role via the `task` tool with
`subagent_type: cdad-<role>` instead of handing a handoff packet to the user.

## Decision rule

1. Does the environment expose `cdad-*` sub-agents as `subagent_type`s available in `task`?
   - YES → delegate via Task (flow below).
   - NO / unsure → handoff packet (portable to any runtime).
2. Is the role a Stage 3 role with sub-phases (AUDIT / RED / properties / E2E)?
   - Every Task invocation is ONE atomic task (one postcondition, one test,
     one diff). Do NOT group sub-phases into a single invocation, unless the spec
     marks explicitly orthogonal postconditions.

## Role → subagent_type mapping

| CDAD role | subagent_type | Model (mofgw) | Stage |
|----------|---------------|-------------------|-------|
| architect | `cdad-architect` | deepseek-v4-pro | 1, 2 |
| test-writer (AUDIT/RED/properties/E2E) | `cdad-test-writer` | glm-5.2 | 3 |
| implementer (GREEN, refactor sub-mode) | `cdad-implementer` | deepseek-v4-flash | 3 |
| reviewer | `cdad-reviewer` | qwen3.7-plus | 4 |
| scribe | `cdad-scribe` | deepseek-v4-pro | 5 |

The `subagent_type` is the role. The model is defined by the sub-agent's config
(it is not passed as an argument). The reviewer uses a family different from the implementer's
(CDAD non-negotiable rule against confirmation bias).

The table shows the **optimus** profile (the repo's design). The deploy may use
another profile (`install.sh --economical|--premium`, see `scripts/cdad-models.sh`
and ADR-007): check the active profile before assuming the table's model
(marker `~/.config/opencode/agents/.cdad-models-profile`). The
reviewer-different-family rule holds across all 3 profiles.

## State-passing mechanism

Task sub-agents receive FRESH context (they don't see the
orchestrator's context). Therefore:

1. The orchestrator builds the Task prompt with the handoff
   packet's content: atomic task, relevant context (spec inline or path, interface,
   strict role rules, expected output).
2. The sub-agent also READS by itself `docs/.cdad-state.json` (for
   `tdd_substage` and state) and `docs/specs/<feature-id>/` depending on the role.
3. The orchestrator does NOT assume the sub-agent remembers anything from the previous
   session. All necessary context goes in the Task prompt.

## ⚠️ task vs delegate — classification by plugin permissions

opencode distinguishes TWO delegation tools, but the classification
**is NOT decided by the CDAD role**: it is decided by the **PLUGIN**, based on
the permissions of the sub-agent's frontmatter nested `permission:` block:

- The sub-agent is **task-able (write-capable)** when AT LEAST ONE of the
  `edit`, `write`, or `bash` permissions in the nested `permission:` block is NOT
  a catch-all deny (e.g. cdad-010's `write: ask` lever: `write` is not
  deny, so the agent does not collapse to read-only).
- The sub-agent is **read-only** only if `edit`, `write`, and `bash` in the nested
  block are ALL catch-all deny.

| Tool | For sub-agents | Detail |
|-------------|------------------|---------|
| `task` | task-ables (plugin: at least one nested permission not-deny) | The sub-agent can mutate files and returns a synchronous result |
| `delegate` | pure read-onlys (all three nested catch-all deny) | ASYNC background execution; the orchestrator must wait for the completion event |

**With the `write: ask` lever (cdad-010, 2026-09-12), all 10
`cdad-*` sub-agents are task-ables → ALL CDAD routing in OpenCode goes through `task`.**

### `delegate` — non-viable fallback in this deploy

**`delegate` is a non-viable fallback in this deploy (dead channel):** the
`session.prompt` the plugin uses to inject the task does NOT pass a model, the
delegated sub-agent falls to the global default (no credit) and dies with a timeout
and 0 messages. Evidence: `delegation-timeouts-2026-09-08` findings from the
workspace. Do NOT use `delegate` for CDAD routing.

**Historical reference of the channel (when it was alive) — MessageAbortedError risk.** The real risk of delegate was never persistence loss: async output IS fully persisted to disk
(`~/.local/share/opencode/delegations/<hash>/<session>/<id>.md`); the cause of
a truncated review was that the delegated sub-agent **ended the turn on a tool_call without emitting the final text** (verified 2026-08-24: the truncated
one exited the loop at step 4 after the last read vs. complete ones with 6+ steps). The
runtime then marked the message `MessageAbortedError` and only persisted the
trace (step-start + reasoning), not the report. The **closing rule** that mitigated it
— never end the turn on a tool_call, always dump the final text in
the same turn after the last tool — remains good prompt
practice for any read-only role, today via `task`.

Historical note on scoped write: any `deny` in edit/write/bash (even
one scoped to a path) makes opencode collapse the agent to "read-only" and
force `delegate` (verified NON-FUNCTIONAL as a mechanism to enable
`task` in opencode 1.18.18, 2026-08-24). Since cdad-010 the lever is
`write: ask`: it is not deny, does not collapse to read-only, and generates no prompts (the
runtime does not evaluate `write`; details and monitoring in `docs/systemPatterns.md`).

## Fallback on rate limit (429)

If the Task fails with a rate-limit (429) or provisioning error:

1. Retry 1 time with a short backoff.
2. If it persists, SURFACE to the user: tell them which role is blocked and why.
3. Offer to re-invoke the same Task pointing the sub-agent's model to the
   local gateway (proxy router) accepting the determinism trade-off
   (model rotation), or wait for the limit to reset.

## When Task vs handoff packet

| Criterion | Task (OpenCode) | Handoff packet |
|----------|-----------------|----------------|
| Session isolation | Yes (fresh sub-agent) | Yes (new chat) |
| Different model per role | Yes (per-agent config) | Manual (the user picks chat/model) |
| Automation | Total (no copy/paste) | Manual |
| Portability | OpenCode only | Any runtime |
| Context overhead | Low (bounded prompt) | High (manual paste) |
| Fallback | Local gateway (proxy router) | None needed |

Preference: Task when the environment supports it; handoff packet as the universal
fallback. The skill remains portable.
