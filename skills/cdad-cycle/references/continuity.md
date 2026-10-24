# Context continuity (optional) — `cdad_continuity`

`<skill-dir>/scripts/cdad_continuity.py` (`<skill-dir>` is the directory of the
loaded `cdad-cycle` skill, as the runtime reports it when the skill is loaded)
is an **optional** deterministic CLI that freezes a
small, tamper-evident checkpoint and reconstructs context on demand, so an
orchestrator can **rotate or resume a session** during long work without asking
the user to repeat the goal or the approvals, and without duplicating effects.
The semantic judgement and every write to `docs/.cdad-state.json` stay with the
**orchestrator** (single writer). **Nothing invokes it automatically** — no hook,
no service, no agent. Run it by hand, and only when it fits.

## Applies / does not apply

| Command | What it needs | Applies | Does not apply |
|---|---|---|---|
| `begin` | execution context + `--update` (goal/decisions/uncertainties/next_action + optional `budget`) | Any environment — write-ahead before dispatching, writes only under `.cdad/executions/<id>/continuity/**` | — |
| `checkpoint` | execution context + `--update` | Any environment — append a new link to the chain | — |
| `reconcile` | execution context + `--packet` | Any orchestrator that retries or resumes after a dispatch — reads 002 receipts/journal, does not repeat an effect | If the receipt is unreadable the result is `unknown` (never fabricated success/failure) |
| `resume` | execution context (+ optional `--role`, `--max-bytes`) | Any new session that must rebuild goal, decisions-with-rationale, authority, next action | Without a checkpoint it renders an empty `no-checkpoint` projection (rc 0); with `--role` it needs `docs/cdad-policy.json` |
| `trigger` | execution context + `--packet` (+ optional `--runtime`) | Any orchestrator that rotates a session or resumes long work | Almost always `unknown`: OpenCode does not report a context limit and Claude Code has no reader, so `context_*` stay `null`. Rotate at a **natural task boundary** instead |
| `verify-begin` | execution context + packet + the INTEGER continuity attempt | Immediately before a transport or a dispatch registration: proves the CURRENT head is the `begin` of that execution, packet and attempt (read-only; a rejection writes nothing) | A historical `begin` under those identifiers, a later `checkpoint` or a `begin` of another packet/attempt never authorizes a new transport |
| `checkpoint-receipt` | execution context + packet + the INTEGER continuity attempt + the durable receipt | The common close of a reception (`receive`, the external arrival and `validate-receipt --close-continuity` converge here): idempotent by `(execution_id, packet_id, attempt)` and by `(normalized receipt path, digest)` | Without a demonstrable chain to the `begin` of that attempt, or with the head advanced to another packet/attempt, it refuses and never rewinds |

`begin`/`checkpoint`/`reconcile`/`resume` are portable because they only read the
project files. `trigger` is only a **signal**: it never invents a limit, so in
today's runtimes it reports `unknown` and the decision to rotate is the
orchestrator's.

## Minimal orchestrator flow (verified surface)

```sh
# 1. before dispatching a role packet: freeze the write-ahead checkpoint
python3 "<skill-dir>/scripts/cdad_continuity.py" begin \
  --project-root ROOT --execution-context EXEC.json --update UPDATE.json --json

# 2. before any retry or resume: reconcile the dispatched work (no double effect)
python3 "<skill-dir>/scripts/cdad_continuity.py" reconcile \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID --json

# 3. in a NEW session: rebuild the context without re-asking the user
python3 "<skill-dir>/scripts/cdad_continuity.py" resume \
  --project-root ROOT --execution-context EXEC.json --json

# 4. optional: read the context signal (usually unknown) and the durable budget
python3 "<skill-dir>/scripts/cdad_continuity.py" trigger \
  --project-root ROOT --execution-context EXEC.json --packet PACKET_ID --json
```

A `begin` re-executed with the same `(execution_id, packet_id, attempt)` and the
same canonical body is a **successful no-op** (rc 0, returns the existing
checkpoint) **while that `begin` is still the head**; re-running it after an
append to its own key fails closed and writes nothing — recovering that no-op is
the `T2-R1` debt. The same holds for an identical `checkpoint` re-executed under
the same key: it is a **successful no-op** too (rc 0, P6). Under the same key, a
divergent `begin` fails closed (escalate, never overwrites), while a divergent
`checkpoint` **appends a new link** (`seq+1`, `prev_checkpoint_sha256` = body of
the head; P5) — the previous link stays as evidence. Every body written by this
CLI carries `record` (`begin`/`checkpoint`), mirrored in `head.json`; a body
**without** `record` is legacy (P6/D5/O-1).
`reconcile`/`resume`/`trigger` are read-only and deterministic; `--max-bytes`
(default 16 KiB) **fails closed without truncating**.

Every body written by `begin`/`checkpoint` also carries an additive historical
link `prev` (`null` in the genesis, `{checkpoint_sha256, seq}` afterwards). It
travels inside the body's physical digest but is **excluded** from the
repetition comparison (the compared content is the whole body minus that single
top-level field), so `prev` is never user input and never a no-op bypass. A body
without `prev` is legacy: it stays readable, but a chain that meets one does not
provide the demonstration a close requires. Bodies may also declare the additive
`changes` and `evidence` fields (`status` exactly `vigente|invalidada`, with
reason and antecedent); `resume` projects both, and an invalidated evidence is
never rehabilitated by byte equality, a changed hash or re-anchoring.

**Scope of the integer (§2.2, amendment 2026-10-24).** `--continuity-attempt N`
is an INTEGER and is never derived from a textual attempt id. It is mandatory —
and its absence fails closed — for an execution **with continuity** (a head for
that execution, or a context that declares `continuity`), which therefore
cannot transport nor register without it. An execution **without continuity**
proceeds: the attempt record declares `continuity: absent` in its provenance
channel, so the omission is visible and auditable, never silent. A reception
follows the same rule for its close: `receive --continuity-attempt N` is
mandatory when the execution has continuity.

## Reference classes (003-007)

`--update.references[]` accepts a bare path (compat string, `class` = `contract`)
or an object `{"path", "class"?, "fields"?}`. The class is **declared** — the CLI
never derives it from the path (D2). `class` ∈ {`contract`, `living`}; an absent
or unrecognized class falls closed to `contract` (P3). The resolved class is
stamped into the checkpoint references as `{"path","sha256","class"}` (plus
`"fields"` when declared), even for the string form.

- **`contract`** — authority/contract material. If it changes or disappears,
  `resume`/`reconcile`/`trigger` fail closed (rc≠0) citing the path and the
  expected/real digests (P1).
- **`living`** — living documents. If it changes or disappears the commands
  still succeed (rc 0) and report it as progress: `state: changed|missing` with
  the real `current_sha256` (P2).
- **`fields`** — optional list of top-level JSON keys: the frozen digest covers
  only their canonical projection, so progress elsewhere in the file does not
  block (P4). `fields` over a non-JSON file, or with a projection that resolves
  no key, fails closed at **write** time (BL-3).
- **Legacy bodies** (pre-003-007, **no `record` in the body**) are resolved
  **by comparison** on read: intact → verified `contract`; divergent/absent →
  reported with `legacy: true` and never blocked (P7/D6). A body **with**
  `record` whose reference lacks a recognizable `class` falls closed to
  `contract` (P3/O-1) — only a legacy body (no `record`) is exempt.

The legacy discriminator lives in the **body**: `record` is stamped into every
body this CLI writes (`begin`/`checkpoint`) and mirrored in `head.json`. A body
without `record` is pre-003-007 (O-1).

Example — declare what is living and what is contract:

```json
{
  "packet_id": "003-007-living-continuity-implementer-green-001",
  "attempt": 1,
  "goal": "…",
  "decisions": [{"decision": "…", "rationale": "…"}],
  "uncertainties": [],
  "next_action": "…",
  "references": [
    {"path": "docs/specs/003-007-living-continuity/spec.md", "class": "contract"},
    {"path": "docs/specs/003-007-living-continuity/plan.md", "class": "contract"},
    {"path": "docs/cdad-policy.json", "class": "contract"},
    {"path": "docs/.cdad-state.json", "class": "contract",
     "fields": ["hitl_delegation", "approver", "execution"]},
    {"path": "docs/specs/003-007-living-continuity/continuity-ledger.md", "class": "living"},
    {"path": "docs/specs/003-006-runtime-adoption/debt.md", "class": "living"}
  ]
}
```

`living`: ledgers, `debt.md`, the Memory Bank, and closing/amendment drafts.
`contract`: approved spec/plan, `docs/cdad-policy.json`, and the state projected
to its authority fields.

## Known limits

- **No rollback/replay of an old head:** restoring an older head plus its bodies
  passes the `resume` verification (`seq` is not contrasted against anything
  persisted) — that is the split-brain/divergent-heads family, and it is the
  orchestrator's call, not the CLI's.
- **Self-consistent tamper is undetectable:** there is **no signature**; the
  digest only proves internal consistency. Rewriting head + body + references in
  agreement is outside the model.
- **Split-brain is the orchestrator's responsibility:** two divergent
  **non-checkpoint** bodies (begins, legacy, orphans) under the same key
  escalate (rc≠0); a begin→checkpoint chain under one key is a legitimate chain,
  not a fork (P5/P6). The CLI never picks a winner, and only the orchestrator
  chains checkpoints.
- **Same-key checkpoint forks are NOT detected:** `_detect_split_brain` only
  counts bodies with `record != "checkpoint"`, so two divergent `checkpoint`
  links under the same key stay invisible to it — detecting them remains the
  orchestrator's responsibility (declared debt, spec §6).
- **Orphan bodies are not detected:** `_detect_split_brain` silently skips
  non-JSON or altered-key bodies; tamper of orphaned bodies stays undetected (P1
  covers head + chain + references, not orphans). This limit covers both the
  pre-RU-2 orphan bodies (bodies left by a rejected pre-003-007 write) **and the
  current writer's own orphans**: a crash between the two fsyncs can leave a body
  carrying `record: "checkpoint"` that no head references (O-1c; `CKPT-FORK`
  debt).
- **The CLI never writes state and never approves:** it never touches
  `docs/.cdad-state.json` and never authorizes dispatch/materialize; an expired
  HITL delegation can rebuild context but cannot write a checkpoint (D4).
