# External CLI delegation — common interface and one adapter per destination

005-009. This reference defines the **common delegation interface**
(`cdad_delegate.py`) and the contract its **destination adapters** follow, so
an authorized coordinator can hand a CDAD packet already prepared to a role
session in ANOTHER CLI and receive its delivery through the existing CDAD flow.

This document **references** the owners of the reused machinery; it does not
copy them:

- packets: `cdad_packet.py prepare` (see `references/project-execution.md`,
  `references/bootstrap.md`);
- dispatch observation (I8): `cdad_packet.py prepare --record-dispatch`
  (closed schema, single ledger);
- durable delivery / receipt: `cdad_result.py receive`
  (`references/receiving-feedback.md`);
- reconciliation / resume: `cdad_continuity.py reconcile` / `resume`
  (`references/continuity.md`);
- single writer of `docs/.cdad-state.json`: the orchestrator
  (`references/continuity.md`).

The interface is **destination-agnostic**: it is not a script per tool pair.
Adding a destination adds one adapter module and never edits the interface.

## Interface

```
python3 cdad_delegate.py --project-root <root> --packet <packet-id> \
    --destination <adapter-id> --exec-config <config.json>
```

| Flag | Meaning |
|---|---|
| `--project-root` | Project root, **explicit and independent of the coordinator's cwd** (PD-3). |
| `--packet` | Id of a **canonical packet already published by `prepare`** (PD-2). Not re-rendered. |
| `--destination` | Adapter id; resolves `cdad_delegate_<id>.py` next to the interface (PD-1/INV-2). |
| `--exec-config` | Execution configuration JSON (see *Configuration*). |

The role/substage and the execution identity are **never** passed as flags:
they are read from the **published packet** (PD-3).

### Output schema (single JSON object on stdout)

```json
{
  "attempt": "delegate-<destination>-<id>",
  "session": "ses-... | null",
  "termination": "completed | blocked | transport-error | timeout | cancelled | unknown",
  "delivery_ref": "<durable path or null>",
  "diagnosis": "<actionable text or null>"
}
```

- `attempt` is the identity of the dispatch attempt and matches the record
  `.cdad/executions/<execution-id>/dispatches/<attempt>.json`.
- `session` is the identity of the role session when the adapter reports one;
  otherwise `null` (honest unknown).
- `termination` is the cause of termination (vocabulary below).
- `delivery_ref` points at the durable final delivery when one exists.

Exit code is `0` when the interface produced the schema; a fail-closed
diagnostic (rc≠0, message on stderr) is returned when the destination has no
adapter or the invocation cannot be resolved.

## Termination vocabulary (PD-6/D4)

`completed`, `blocked`, `transport-error`, `timeout`, `cancelled`, `unknown`.

`completed` (the delivery exists) is **not** a gate approval: the receipt stays
`semantic_status: "pending"` and the responsible orchestrator decides the gate
at re-entry (INV-5). `timeout` does not prove absence of changes; after an
interruption the effects are reconciled (`cdad_continuity.py reconcile`) before
repeating.

## One adapter per destination (PD-1/INV-2)

The adapter for destination `<id>` is the module `cdad_delegate_<id>.py` in the
same directory as the interface. The interface resolves it by id; adding,
removing or changing a destination **does not touch the interface**.

### Adapter contract

Invoked by the interface as a subprocess:

- **stdin**: the published `PACKET.md` **byte-identical** (PD-2/INV-3).
- **argv**: `--project-root <root> --packet-id <id> --destination <id>
  [--exec-config <config.json>]`.
- **stdout**: one JSON envelope with the same keys as the output schema
  (`attempt` may be `null`; the interface fills it).
- **exit code**: `0` when the adapter ran; non-zero only for adapter-internal
  errors.

An adapter must:

1. verify the project's **published derived agent** for the role and **fail
   closed** with a named diagnostic when it is missing — the entry's declared
   load mode does **not** gate the dispatch; the identity is verified from the
   durable row (see the first adapter) — with **no silent fallback** to a
   generic agent (PD-3/D3);
2. wait on a **durable signal** (the destination's session store or durable
   receipt), never on the invocation client's rc, with no invented callback
   (PD-5/INV-4);
3. capture the role's final text and its referenced evidence, and persist the
   delivery through the existing `receive` (PD-7);
4. report `runtime`, `model_configured`, `model_reported`, `session` honestly —
   `null`/`unknown` when not observed (PD-8).

The **first adapter** is `cdad_delegate_opencode.py` (destination OpenCode);
the first real journey is coordinator (Claude) → worker (OpenCode) → CDAD
reception. Other CLIs and the reverse direction are later increments.

### First adapter — OpenCode: the durable signal contract (PD-1/PD-2/PD-5)

The OpenCode adapter is the reference implementation of the adapter contract
above. Its durable signal is the runtime's **own session store**: a **SQLite**
base whose path is declared by `sessions_db` in the execution configuration (a
**configurable** path, never hardcoded), opened **read-only** (URI `mode=ro`;
never written — INV-3).

- **Correlation (PD-1).** The adapter **chooses** the session id and passes it
  in `--session <id>` to the destination invocation; the correlated **durable
  row** (`session_v2`, the durable row of that id) carries that id and its
  `agent`. The correlation is unambiguous: no other signal is invented.
- **End-of-run fact (PD-5).** The adapter waits, within the bounded wait
  (`wait.timeout_seconds`), for the correlated row's idle material
  (`idle_outcome`), never for the client `rc`: `succeeded → completed`,
  `failed → blocked`, `interrupted → cancelled`; no correlated row or no idle
  within the bound → `timeout`. Only `completed` persists the delivery.
- **Final text.** The role's final text is the last `assistant` message of the
  correlated session (`session_message.data.content[].text`); a `succeeded`
  row without final text is `blocked`, never `completed`.
- **Fail closed (PD-2).** A store that does not exist, is not readable, is not
  SQLite, or lacks the expected schema (an **unknown schema**) fails closed
  with an actionable diagnosis that names what is missing, termination
  `blocked`, without fabricating a delivery and without degrading the known
  fact into a `timeout`.

### First adapter — OpenCode: server and permissions (PD-4/INV-8)

The destination invocation mode is taken from the execution **configuration**,
never hardcoded: `--standalone` by default (a private server; never the owner's
background service), `--server <url>` when the configuration declares it (the
alternative to `--standalone`, never both), and `--auto` (enabled by default)
for non-interactive permissions. `--auto` auto-approves non-denied permissions
and is **not** a sandbox: the path deny-maps remain the barrier (INV-8).

## Configuration (PD-8/INV-7)

Runtime, model, binary/version, logs, servers and timeouts live in the
**execution configuration** (`--exec-config`, local and git-ignored) or in
flags — never hardcoded in the product nor in public contracts. The
configuration also carries the durable signal surface: the `sessions_db` path
of the destination's session store, and the server/permission selectors
(`server` as the alternative to the default private server, and `auto` for
non-interactive permissions). No value of the operating host (absolute paths,
provider, concrete model, server, times) may appear in the product. The
interface records **configured / observed or `unknown`**, with a `provenance`
map field → source.

## Procedure for another coordinator

1. `prepare` publishes the canonical packet (`PACKET.md` + `REQUEST.json`).
2. `cdad_delegate.py --project-root <root> --packet <id> --destination <id>
   --exec-config <config.json>` resolves the adapter, transports the packet
   byte-identical and registers the attempt in the same I8 ledger.
3. The adapter runs the role session in the destination CLI.
4. The delivery is persisted with `cdad_result.py receive`
   (`semantic_status: "pending"`).
5. The responsible orchestrator reconciles (`cdad_continuity.py reconcile`) and
   decides the gate at re-entry; it is the **single writer** of the state.

## Honest limits

- A **separate process/session is not a sandbox**: it neither prevents new reads
  nor isolates information; changing CLI does not guarantee another model
  family (INV-8).
- The interface **never** writes `docs/.cdad-state.json` and **never** creates
  another ledger or state; the only state change is the reused
  `prepared → dispatched` transition (INV-1).
- `rc=0` does not approve a gate; a delegation does not widen authority nor
  scope, and the worker never writes the state (INV-4/INV-5).
- No scheduler, no automatic CLI installation, no sandbox; not every
  destination is implemented (INV-9).
