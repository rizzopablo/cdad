# Progress guards (optional) — `cdad_guard`

`skills/cdad-cycle/scripts/cdad_guard.py` is an **optional** deterministic CLI that
reads already-existing signals and emits structured incidents/decisions; the
semantic judgement stays with the orchestrator. It is **read-only** over the
product, except `record`, which writes only under
`.cdad/executions/<execution_id>/guards/`. **Nothing invokes it automatically** —
no hook, no service, no agent. Run it by hand, and only when it fits.

## Applies / does not apply

| Command | What it needs | Applies | Does not apply |
|---|---|---|---|
| `preflight` | `docs/cdad-policy.json` + execution context + `--role` + `--operation` | Any environment — reads the policy/context, writes nothing | — |
| `record` | a `guard-event-v1` event JSON | Any environment — writes durable recovery events under `.cdad/` | — |
| `budget` | execution context + `--packet` | Any environment — reads one packet's durable events, writes nothing | — |
| `classify` | a recorded `trace-v1` document | Only if a **reader** converts the environment's session log to `trace-v1` | Today **no product reader exists** for any environment: OpenCode has only a disposable prototype (`docs/specs/003-003-progress-guards/evidence/t5/recorder.py`); Claude Code has none. Without a reader → **do not use `classify`** |

`preflight`, `record` and `budget` are portable because they only read the
project policy/context and write project files. `classify` is the only command
that depends on a runtime-specific recording layer; until a product reader
ships, its input must be produced by hand (T5 used a throwaway script), so it is
not worth wiring into the normal flow.

## When it is worth it

- You dispatch roles as **processes outside the runtime** (another CLI's
  non-interactive run) and want to
  **preserve attempts and causes across resumptions** — `record`/`budget` keep
  that durable, keyed by `execution_id` + `packet_id`.
- You want to **prevalidate an operation before dispatching it** — `preflight`
  checks it against the policy and the role's declared scope.

## When it adds nothing

- **Native runtime sub-agents** whose lifecycle the runtime already manages: the
  harness returns the result, so there is nothing to reconstruct — the guard is
  overhead.
- Note: with a non-interactive external CLI run, a shell command launched with
  `background: true` **dies with the turn** and never notifies. That is an
  artifact of this dispatch mode — **not** something the guard solves. Fix the
  dispatch mode; don't expect the guard to see a result that was never produced.

## Known limits

- **Coarse progress granularity:** the progress digest looks at the *set of
  paths*, not their content, so successive edits to the same file look like "no
  progress" → false alarms (observed in T5 real usage).
- **Advisory preflight:** a target **outside the project root is `allow`** (not
  governed by the project policy); `deny` only fires on an **explicit rule** (a
  `private_paths` match or a role-scope miss). No sandbox is promised.
- **Calibration pending:** severity and `read_scope` behaviour are uncalibrated
  against real usage.

## Commands (verified against `--help`)

```sh
# classify a recorded trace-v1 (offline, deterministic)
python3 skills/cdad-cycle/scripts/cdad_guard.py classify \
  --project-root ROOT --trace TRACE.json

# prevalidate an operation against policy + role before dispatching it
python3 skills/cdad-cycle/scripts/cdad_guard.py preflight \
  --project-root ROOT --execution-context EXEC.json \
  --role ROLE --operation '{"tool":"write","path":"src/a.py"}' [--json]

# persist one durable recovery event (writes under .cdad/executions/<id>/guards/)
python3 skills/cdad-cycle/scripts/cdad_guard.py record \
  --project-root ROOT --event EVENT.json

# report the durable per-packet recovery budget (read-only)
python3 skills/cdad-cycle/scripts/cdad_guard.py budget \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID
```
