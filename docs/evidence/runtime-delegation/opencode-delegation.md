<!-- 006-002 PD-9 — non-installable evidence. NOT part of the skill tree:
     `install.sh` never ships `docs/**`. The rule in force lives in the
     `delegation` section of the generated runtime orchestrator agent. -->

# Historical evidence — OpenCode delegation reference (withdrawn from the skill)

**Status: non-installable historical evidence (006-002 PD-9).** This document
preserves, in full, the runtime reference `opencode-delegation.md` that lived in the
installable skill tree (`skills/cdad-cycle/references/`) until 006-002
withdrew it. It is historical / verification material from 005-004 / 005-005 / 005-010; it is
**not installed** (nothing under `docs/**` is shipped by `install.sh`), and no
installable skill text points to it.

The delegation rule **in force today** is not here: each runtime's orchestrator
agent declares it in its `delegation` section (generated from
`sources/agents/adapters/*.md`) — the native dispatch mechanism, the
role→sub-agent mapping, the byte-identical packet pass, the intra-runtime
adapter prohibition, the model declaration (D-3) and the receipt. The
transport-equivalence receipt lives in the skill
(`references/re-entry.md`). What follows is the withdrawn detail, kept as
evidence.

---

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

| CDAD role | subagent_type | Stage |
|----------|---------------|-------|
| architect | `cdad-architect` | 1, 2 |
| test-writer (AUDIT/RED/properties/E2E) | `cdad-test-writer` | 3 |
| implementer (GREEN, refactor sub-mode) | `cdad-implementer` | 3 |
| reviewer | `cdad-reviewer` | 4 |
| scribe | `cdad-scribe` | 5 |

The `subagent_type` is the role. The **model** is NOT fixed in this reference:
the **single model table** lives in `scripts/cdad-models.sh`, and the model a
role resolves to is the one the **active profile** declares. Read the profile
selectors from `scripts/cdad-models.sh` (and the active-profile marker under the
agents dir) instead of assuming any concrete model; never hardcode a model here.
The reviewer uses a family different from the implementer's (CDAD
non-negotiable rule against confirmation bias), and that rule holds across every
profile.

## Load mode of the role agents (installed runtime)

The role agents are published with `mode: subagent` (`scripts/cdad-generate.py`
emits it; `sources/agents/adapters/opencode.md`). In the **installed runtime** a
`mode: subagent` agent is a valid **non-interactive** entry through the
delegation adapter (`opencode run --agent cdad-<role> ...`): it answers the
non-interactive invocation, and a non-existent agent errors explicitly instead
of hanging. The adapter therefore **no longer requires a `mode: all` entry**;
its barrier is:

- the derived `cdad-<role>` agent is **published** in the project
  (`.opencode/agents/cdad-<role>.md`, by `prepare`), and
- the role **identity** is verified from the **durable row** — the correlated
  `session_v2` row must declare `agent == "cdad-<role>"` — **without fallback**
  to a generic non-Cdad agent.

A missing derived agent, or a durable row declaring another agent, is a
fail-closed fact (the diagnosis names it), never a silent fallback.

## Invocation — the project directory travels in `PWD`

OpenCode v2.0.26 (verified) takes the **project directory** from the `PWD`
environment variable, not from the process cwd. The adapter therefore pins
`PWD` to the explicit project root of the delegation when it invokes the
destination, so a coordinator running from another cwd never leaks its own
directory into the delegated session; `PWD` is only *set* for the destination
process, never read as a resource-resolution source.

## State-passing mechanism

Task sub-agents receive FRESH context (they don't see the
orchestrator's context). Therefore:

1. For a prepared execution, the orchestrator runs
   `skills/cdad-cycle/scripts/cdad_packet.py render`, captures complete stdout,
   and passes those bytes unchanged as the Task prompt.
2. The sub-agent follows the packet instructions and declared inputs without
   reloading the full cycle skill.
3. Without a prepared execution/request, use the legacy handoff-template flow.
   Do not fabricate authority or an incomplete packet.

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

## Reload, version and provenance of the project agents

`prepare` publishes the project-local OpenCode agents under `.opencode/agents/`
(see `references/runtime-adoption.md`). Two questions matter when a delegated
session runs against them: whether an already-started OpenCode process picks up
a changed agent/skill, and which installation version a session loaded.

### Origin resolution (005-005 PD-12)

`prepare` resolves the OpenCode agents source in this order:

1. `CDAD_OPENCODE_AGENTS_DIR` (explicit).
2. The installation registered in the project activation registry
   `.cdad/activation.json` → `<adopted_root>/.config/opencode/agents`.
3. The runtime global default (`$HOME/.config/opencode/agents`).

When the resolved origin differs from the registry or from the `source_dir` of
the previous derived manifest (the real MIX-V6V7 case), `prepare` writes a
diagnostic to **stderr** that names `.cdad/activation.json` and every
version/commit in play, and continues with the resolved source: a version change
is never silent (PD-13/INV-7).

### Version a session loaded (005-005 PD-14)

The published manifest `.opencode/agents/.cdad-derived.json` declares
`source_dir` **and** `source_version` (the origin installation's `version.txt`),
so the version a session loaded is verifiable from the published artifact.

### Reload — what is verified and what is not (005-005 PD-15)

- **Owner fact (data, OpenCode 2.0.22):** a **new process** re-reads the agents;
  a project agent in `.opencode/agents/` **replaces** the global agent of the
  same name.
- **Verified in isolation (installed CLI `opencode` 1.18.32, temp `HOME`/`XDG`
  and a free port; the owner's HOME and server were never touched):** a project
  agent shadows the same-named global agent in a **new process** —
  `opencode debug agent <name>` resolved `"description": "PROJECT probe agent"`
  with `<proj>/.opencode/agents/cdad-probe.md` present next to a global
  `<home>/.config/opencode/agents/cdad-probe.md`.
- **NOT verified — `opencode reload` on an already-started server:** the owner
  declares it untested, and it could not be exercised in isolation. The installed
  1.18.32 exposes **no `reload` subcommand** (`opencode --help` lists none; the
  only `reload` strings in the binary belong to the desktop/webview), and the
  headless server (`opencode serve`) answers **401 Unauthorized**
  (`www-authenticate: Basic realm="Secure Area"`) with no token exposed, so its
  live reload behavior could not be observed. Do **not** affirm it: restart the
  server (a new process) or re-verify against 2.0.22 before claiming otherwise.
