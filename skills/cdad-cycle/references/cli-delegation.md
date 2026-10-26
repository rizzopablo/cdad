# External CLI delegation — common interface and one adapter per destination

005-009 + 006-001. This reference defines the **common delegation interface**
(`cdad_delegate.py`) and the contract its **destination adapters** follow, so
an authorized coordinator can hand a CDAD packet already prepared to a role
session in ANOTHER CLI and receive its delivery through the existing CDAD flow.
006-001 adds the **explicit execution mode** (`server` | `service` |
`standalone`), the **service preflight** and the portable example configuration.

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

## The orchestrator's entry — `cdad_dispatch.py` (006-005)

The coordinator drives the cycle through ONE entry
(`skills/cdad-cycle/scripts/cdad_dispatch.py`, 006-005 §2.1) instead of carrying
a configuration, a model or a credential itself. Today it carries the
**execution configuration** and the **bounded migration**; the transport verbs
(`dispatch`/`record`) and `capabilities` are the rest of 006-005.

```
python3 cdad_dispatch.py [dispatch] --project-root <root> --packet <id> --runtime <X>
python3 cdad_dispatch.py migrate --runtime <X> --legacy-exec-config <file> [--dry-run]
```

- **`--runtime <X>` is mandatory in every verb and is the only runtime
  resolution** (006-005 PD-8): the entry never reads a `runtime` from a project
  document, not even from the flat v1 context that declares one. An id without a
  `cdad_delegate_<id>.py` module next to the entry is rejected naming the value.
- The **execution configuration** of the external path is the **runtime
  section** of `runtimes.json`, beside `delegation.json` and under the same
  location rule (`$XDG_CONFIG_HOME/cdad/`, else `<base>/.config/cdad/`; 006-005
  PD-9). One section per runtime id; its keys are the ones the adapter already
  reads (`binary`, `binary_version`, `mode`, `server`, `service`, `auto`,
  `sessions_db`, `wait`). Without a section the entry fails closed with a
  diagnostic that names the file, the section and the key-by-key
  correspondence.
- **`model` and the credential route never live in the section** — they are
  `delegation.json` and its `credential_env_file` (ADR-033 D3 / point 6); a
  section that carries either is rejected, naming where it lives (INV-12).
- The retired `--exec-config` is **not an option**: passing it (either form) is a
  usage error *before any effect*, with the migration diagnostic, in every verb —
  the sweep is over `argv`, by exact token, before the verb is parsed (006-005
  D-11).
- The installer writes the `runtimes.json` template only when missing: user
  data, never registered in the ownership manifest, never overwritten (INV-7).

### Migrating a retired exec-config (E5)

```
python3 cdad_dispatch.py migrate --runtime <X> --legacy-exec-config <file> [--dry-run]
```

- It moves the correspondence keys into the section of that runtime **only when
  it does not exist**; an existing section is refused without writing it
  (**never** overwritten — user data, 006-005 INV-7). `--dry-run` prints the
  section it would write and writes nothing.
- It never moves `model` nor a credential value: it reports where they live.
- **Verification is `capabilities --runtime X`** (006-005 PD-10); the migration
  step does not declare success by itself.
- **Adoption border.** The order is **migrate → `capabilities` → dispatch with
  `--runtime`**: `migrate` writes the runtime's section of `runtimes.json` from
  the retired document, `capabilities` verifies the section it wrote, and only
  then does the entry dispatch. From the moment the section exists the entry
  reads ONE source — that section of `runtimes.json` — and the retired
  exec-config, the local dispatch helper and the environment wrapper stop being
  used. The entry never reads a retired document outside this explicit step, and
  it never deletes that document (it is the owner's data).

## Interface

```
python3 cdad_delegate.py --project-root <root> --packet <packet-id> \
    --destination <adapter-id> --exec-config <config.json>   # internal flag
```

| Flag | Meaning |
|---|---|
| `--project-root` | Project root, **explicit and independent of the coordinator's cwd** (PD-3). |
| `--packet` | Id of a **canonical packet already published by `prepare`** (PD-2). Not re-rendered. |
| `--destination` | Adapter id; resolves `cdad_delegate_<id>.py` next to the interface (PD-1/INV-2). |
| `--exec-config` | Execution configuration JSON — an **internal** interface flag, never the orchestrator's path (006-005 D-11); its content is derived from the runtime's section of `runtimes.json`. |

The role/substage and the execution identity are **never** passed as flags:
they are read from the **published packet** (PD-3).

### Output schema (single JSON object on stdout)

```json
{
  "attempt": "delegate-<destination>-<id>",
  "session": "ses-... | null",
  "termination": "completed | blocked | transport-error | timeout | cancelled | unknown",
  "delivery": "none | staged | received",
  "delivery_ref": "<descriptor, durable receipt or null>",
  "diagnosis": "<actionable text or null>"
}
```

- `attempt` is the identity of the dispatch attempt and matches the record
  `.cdad/executions/<execution-id>/dispatches/<attempt>.json`.
- `session` is the identity of the role session when the adapter reports one;
  otherwise `null` (honest unknown).
- `termination` is the cause of termination (vocabulary below).
- `delivery` is the delivery state of the envelope (vocabulary below). It is
  **mandatory** in every envelope a producer of this interface emits.
- `delivery_ref` is the ONE reference of the delivery: the existing descriptor
  (`staged`) or the existing durable receipt (`received`); `null` when
  `delivery` is `none`. There is no second reference field.
- `diagnosis` explains a rejection, a block or a protocol failure.

Exit code is `0` when the interface produced the schema; a fail-closed
diagnostic (rc≠0, message on stderr) is returned when the destination has no
adapter or the invocation cannot be resolved.

**`rc` semantics (007-004 §7).** `rc=0` means that an envelope was produced, not
that the errand succeeded: a `blocked`, `timeout` or protocol rejection is also
`rc=0`. Errors that end without an envelope (unresolvable destination, invalid
flags) keep their non-zero `rc`. The destination's internal rc never replaces a
valid envelope, and `rc=0` without a usable envelope acredits no delivery.

## Delivery vocabulary and valid combinations (007-004 §4)

This section is the **owner** of the envelope shape, the vocabularies, the
combinations and the historical compatibility of the delivery. The consumption
procedure — which route a consumer follows for each `delivery` — is owned by
`references/re-entry.md`; roles and adapters point to both and never restate
them.

`delivery` is closed: `none | staged | received`.

| `delivery` | Contract |
|---|---|
| `none` | The envelope acredits no consumable delivery; `delivery_ref` is `null`. It does **not** prove the absence of changes or of durable effects that must be reconciled. |
| `staged` | The reference identifies the existing descriptor of prepared parts, still pending reception (native `record` path). |
| `received` | The reference identifies the existing durable receipt, pending validation by the consumer (external arrival). |

`R` below means a non-empty string that references the artifact of the declared
kind. Structural validity does not replace the validation of the artifact.

| `termination` | `delivery` | `delivery_ref` | Validity |
|---|---|---|---|
| `completed` | `staged` | R: descriptor | Valid for the native `record` producer. |
| `completed` | `received` | R: receipt | Valid for the external arrival. |
| `blocked` | `none` | `null` | Valid. |
| `transport-error` | `none` | `null` | Valid. |
| `timeout` | `none` | `null` | Valid. |
| `cancelled` | `none` | `null` | Valid. |
| `unknown` | `none` | `null` | Valid. |
| Any other combination | Any | Any | **Invalid.** |

In particular: `completed` with `none` is contradictory; a termination other
than `completed` with `staged` or `received` is contradictory; `none` with a
non-null reference is contradictory; `staged`/`received` without a reference,
with an empty reference or with a reference of the wrong type is invalid; an
unknown vocabulary value is invalid; a descriptor presented as a receipt (or the
reverse) is rejected when the artifact is validated; a structurally valid
combination that is incompatible with the route is also rejected.

### Producer rules

| Producer or route | Result | Required envelope |
|---|---|---|
| `cdad_dispatch.py record`, payload prepared correctly | Staged descriptor | `completed + staged` + reference to the descriptor. |
| `record`, registered attempt without payload | No delivery | `unknown + none + null`. |
| `record`, contradictory correlation | Rejection without registration or staging | `blocked + none + null` + diagnosis. |
| `cdad_delegate_opencode.py`, reception finished correctly | Durable receipt | `completed + received` + reference to the receipt. |
| OpenCode, non-completed termination | No acredited delivery | the corresponding termination `+ none + null`. |
| `cdad_delegate.py`, valid adapter answer | Relay | preserves identity, termination, delivery and reference; registers and receives nothing. |
| `cdad_delegate.py`, own timeout or transport without a usable envelope | Diagnostic | `timeout` or `transport-error`, `none`, `null`. |
| `cdad_dispatch.py dispatch` | External arrival | relays the validated envelope; prepares and receives no other delivery. |

On these EXTERNAL routes `completed + staged` is not an acceptable landing: the
external runtime module owns the existing reception, so `staged` belongs to the
native `record` path only. A producer of this interface therefore never emits
`completed + staged`; when an adapter does, the arrival is refused as a protocol
response (`transport-error + none + null`) and nothing is staged or received.

### Rejection of contradictions (§4.4)

A producer that follows this contract never emits an invalid combination. When
the interface receives a contradictory or wrongly typed envelope from an
adapter it (1) does not relay it as a valid delivery, (2) does not silently
correct it into a success, (3) registers no attempt, receives nothing and
materializes nothing, (4) emits a protocol diagnostic as
`transport-error + none + null`, and (5) keeps the usable identities of the
original envelope without inventing replacements. A consumer that meets an
invalid envelope directly stops and diagnoses; the process `rc` never
authorizes ignoring that condition.

### Historical compatibility (§5)

The **absence** of `delivery` is the only condition that activates the
historical interpretation: a key present with `null`, an unknown value or a
wrong type is not a valid historical envelope. The consumer uses the known
context of the operation — never the file name, never a `RESULT.json` suffix and
never a path that merely looks like a receipt:

| Historical context | Condition | Permitted interpretation |
|---|---|---|
| Native `record` | `completed` and a non-empty reference | Candidate to `staged`; validate the descriptor and its binding through the existing reception before receiving. |
| External arrival through `dispatch` or `cdad_delegate.py` | `completed` and a reference that IS the durable receipt of this errand and passes `validate-receipt` | Candidate to `received`; validate the receipt and its binding before continuing. |
| Any of the known routes | Non-completed termination and a `null` reference | `none`; do not advance. |
| Any of the known routes | Non-completed termination with a non-null reference, whether the artifact exists or not | Contradiction: stop and diagnose (`transport-error + none + null`). The reference is never removed to normalize the envelope into an acceptance. |
| Unknown context, a reference that is not this errand's receipt, a descriptor, a plain text, a contradictory combination | — | Stop and diagnose. |

Additional rules: a historical reference is not accepted because of its name nor
because the artifact it names exists; the reference must be **the** durable
receipt of this errand — the single receipt of its execution and packet, located
by the producer's own rule — and the producer's canonical verifier
(`cdad_result.py validate-receipt`, imported per ADR-036) must accept it, so a
descriptor, a plain text or another errand's receipt is refused instead of being
announced as `received`; an updated producer always emits `delivery`; historical
artifacts are never rewritten and no substitute receipt is created; validation
uses the existing machinery (the descriptor through the existing reception, the
receipt through `validate-receipt`).

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
  [--exec-config <config.json>]` (that last flag is internal to the interface;
  the orchestrator never passes it).
- **stdout**: one JSON envelope with the same keys as the output schema
  (`attempt` may be `null`; the interface fills it). The envelope declares
  `delivery` explicitly: `completed + received + <receipt>` when the adapter
  persisted the reception, and `<termination> + none + null` otherwise (007-004
  §4.3).
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
   delivery through the existing `receive` (PD-7) — the only delivery this
   route may acredit is `received` with that receipt (007-004 §4.3);
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

### First adapter — OpenCode: execution mode selection (PD-1/PD-13/PD-14)

The mode is taken from the execution **configuration** (`mode`), never inferred
from the mere presence of `server` and never hardcoded. Three modes:

| `mode` | Effective mode | Invocation of `run` |
|---|---|---|
| `server` | the declared server, after the server preflight (§ below) | `--server <url>` |
| `service` | the **background service**, after the service preflight (§ below) | **no** `--server`/`--standalone` (the client uses the background service as the runtime designs it) |
| `standalone` | a private server | `--standalone` |
| undeclared | **backward compatibility (D-9)**: server when a valid `server` is declared, otherwise standalone | as above |

- **Backward compatibility (D-9).** A configuration that declares no `mode`
  keeps the v1 rule (server if `server` is present and valid; standalone
  otherwise). `service` is **never** a default: moving to a shared background
  service is a consumer decision and must be explicit.
- **No mode change on failure (INV-2).** The **only** admissible transition is
  the declared and counted fallback `service` → `standalone` when
  `service status` reports that the service **does not run** (§ below).
- An invalid `mode`, or an invalid `service.*`/`wait.*` value, **blocks** before
  the dispatch: nothing is invoked. `--standalone` and `--server` are mutually
  exclusive and the service dispatch is neither.
- `--auto` (enabled by default, configurable) auto-approves non-denied
  permissions and is **not** a sandbox: the path deny-maps remain the barrier
  (INV-8).

#### Server preflight (mode `server`)

Before `run`, within the bound: the client version (`--version`) and a
`GET <server>/api/info` with the credential in the client's own order
(`OPENCODE_PASSWORD`, then `OPENCODE_SERVER_PASSWORD`; the value is never
recorded). Connection refused/timeout → `transport-error`; auth/JSON/version
mismatch → `blocked`. In this mode the only invocations of the binary are
`--version` and `run`; `service status` is **not** invoked.

#### Service preflight (mode `service`)

Before `run`, within the bound, `service status` (a **read-only** subcommand —
it starts nothing) is invoked **exactly once**:

- a URL → the service **runs**; the literal `stopped` → it **does not run**;
  any other output, empty, more than one line, rc ≠ 0 or a timeout →
  **unexpected** → `blocked` (never standalone).
- The URL that `service status` prints is **discarded to a discriminant**: it is
  never used, never stored and never enters any output (CDAD does not need it:
  the client finds the service itself).
- **Version gate (D-11).** When the service runs, the client `--version` is
  compared with the service's version, projected from the **single `version`
  key** of the service's registration record (an observed fact, not a public
  contract — debt DT-6; never the record, never its secret, never its URL, no
  network). **Equal** → dispatch **without flags**. **Different or
  unverifiable** → `blocked` (never standalone: a standalone next to a running
  service would be one more writer on the same store).
- **Service does not run.** With `service.require: true` → `blocked` (starting
  the service is the operator/owner's decision; CDAD never runs `service
  start`). With `service.require: false` → `standalone` with the **declared and
  countable** fallback `service-unavailable`.
- **`service.require`** is a boolean, default `false`. It only has effect in
  the service mode; elsewhere it is ignored and recorded as not applicable
  (D-10).
- **Declared race window (D-13).** The service can stop between
  `service status` and the dispatch, and the runtime's client would then start
  it (`run` without flags). The runtime offers no supported way to prevent that
  (no flag, no environment variable, and the service settings do not control
  it). This is a **residual risk**, not an action of CDAD.

> Measuring the versions in the service path is itself an act of reading a
> service registration, which also contains a secret; the projection returns
> only the `version` key and nothing else escapes — no key of that record
> reaches argv, diagnosis, the I8 records or the receipt (PD-5/INV-6).

## Limits — never manage the service, servers or the store (INV-2/INV-10)

- The product **never starts, restarts, stops or configures** the background
  service nor any server: no invocation carries `serve`, `service
  start|stop|restart|get|set|unset` or `reload`. The only `service` subcommand
  is `service status`.
- The product **never writes or maintains the session store**: it opens it
  read-only and its re-reads (including those retried against a lock) stay
  read-only — they add no write pressure.
- The **server and the background service are managed by the owner/operator**,
  never by CDAD. Neither the interface nor the adapter installs, schedules or
  sandboxes anything.

## Concurrency and the store (PD-6)

Two concurrent delegations from two disposable projects, against the same
disposable store (and, in the server topology, the same disposable server), both
finish `completed`; each receipt carries its own session; each durable row's
`directory` is its own project; each packet asks for its own nonce and that
nonce appears only in its own results. The permanent regression is the fixture
with real transactional SQLite writes; acceptance additionally requires the real
journeys in §*Isolation recipe* below.

- **The removal of the store's lock contention is NOT demonstrated.** A
  successful concurrent run is an **empirical observation**, not proof that
  contention disappeared; the read-only re-reads never add write pressure. This
  stays an observation of the reception (AC-7), not a proven property.

## Isolation recipe for tests (by the test, never the live host)

The real journey is launched by the **test**, never against the operating host:

1. Put `XDG_DATA_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` under a
   disposable `<ROOT>` (`mktemp -d`).
2. Guard first: run `debug paths` with that environment and abort, **without
   dispatching**, unless `db`, `data`, `state` and `log` fall under `<ROOT>`.
3. A disposable server on loopback, with a random password: the test launches
   it and stops it itself (SIGTERM, grace, SIGKILL to its group). Two disposable
   projects with their derived agents published and their packet prepared; the
   concurrent standalone journey is complementary.
4. **Credential by substitution, never by copying.** The provider credential is
   injected with a config layer that substitutes `{env:<VAR>}`; the test never
   reads nor copies the credential file. With no such variable defined the test
   is **skipped with a reason**, and a skip is **not** a pass (it leaves PD-6 as
   a declared BLOQUEO).
5. Record version, anonymized config, duration, terminations and `store_reads`.

The journey in the **service** topology uses the **live background service in
normal use**, without restarting or reconfiguring it, and is run by the
orchestrator or the owner. If it required something reserved to the owner, PD-6
stays a declared BLOQUEO. It records the termination, effective mode (no flags),
`mode_requested`, `service_status`, `server_version`, `fallback`, times, errors
and `store_reads`; the attribution to the service is verified by the durable
row's `version` and by the process inventory (no new private or service server
during the dispatch).

## Configuration (PD-8/INV-7)

Runtime, binary/version, logs, servers, timeouts and the execution mode live in
the **execution configuration** — the runtime's section of `runtimes.json`
(006-005 PD-9), which the entry reads and from which it derives the module's
internal configuration — or in flags — never hardcoded in the product nor in
public contracts. The configuration also carries the durable signal surface
(the `sessions_db` path of the destination's session store) and the
server/permission selectors (`server`
as the alternative to the default private server, and `auto` for
non-interactive permissions). No value of the operating host (absolute paths,
provider, concrete model, server, times) may appear in the product. The
interface records **configured / observed or `unknown`**, with a `provenance`
map field → source.

A model is NOT a key of the execution configuration (006-003 D3). Its only
source is the **delegation configuration**, which the installer creates as a
template and the user edits. Its location is ONE rule, the same for the
installer that writes it and the interface/adapter that read it (O-2):
`$XDG_CONFIG_HOME/cdad/delegation.json` when `XDG_CONFIG_HOME` is defined and
non-empty; otherwise `<base>/.config/cdad/delegation.json` with `<base>` =
`CDAD_INSTALL_ROOT` when that variable is defined and non-empty (a redirected
install root confines every write, INV-6), and the user's HOME otherwise:

```json
{
  "version": 1,
  "models": { "<destination-id>": { "<role>": "<provider>/<model>" } },
  "credential_env_file": "<path>"
}
```

`<destination-id>` is the id of the destination runtime (`opencode` for the
OpenCode adapter); `<role>` is one of `architect`, `test-writer`,
`implementer`, `reviewer`, `scribe`. A role without an entry has no model: the
destination argv carries no `--model` and the I8 record declares
`model_configured: null` with the delegation configuration as its provenance
(no fallback, INV-7). A `model` key left in an execution configuration is
ignored with a one-line deprecation notice that names the delegation
configuration and how to migrate.

The same document carries the optional **`credential_env_file`** (006-003 U6,
§2.3/D5): the `server` mode credential. It is read from the ENVIRONMENT of the
process that dispatches first — `OPENCODE_PASSWORD`, then
`OPENCODE_SERVER_PASSWORD` — and, only when neither is present with a
non-empty value (an empty value is **absent**, never an empty header), from
that file (the delegation config's `credential_env_file`, or the default
`<config-dir>/cdad/opencode-server.env`, i.e. the location rule of
`delegation.json`): `KEY=value` lines with `#` comments, an empty value meaning
**absent** (never an empty header). The file's permissions are verified on the
opened descriptor: `600`/`400` are accepted and any bit of `077` is refused.
The installer writes the sibling `opencode-server.env.example` with no value;
copy it to `opencode-server.env` with mode `600`. On a 401/403 the diagnosis
NAMES THE SOURCE actually used — the environment, or the resolved credential
file path (never `None`) — both variables, the provenance of the value (the
password of the `opencode serve` instance in use) and, when the file was
refused, the path and the mode found. The value is never printed, logged,
passed on argv nor recorded (INV-1).

Keys (all optional except the required wait bound):

| Key | Values | Default |
|---|---|---|
| `mode` | `"server"` \| `"service"` \| `"standalone"` | undeclared → the v1 compatibility rule (D-9) |
| `service.require` | boolean | `false` |
| `wait.timeout_seconds` | number > 0 | required |
| `wait.poll_initial_seconds` | number > 0 | `1` |
| `wait.poll_max_seconds` | number ≥ `poll_initial_seconds` | `15` |
| `wait.settle_seconds` | number > 0 | `30` |
| `wait.terminate_grace_seconds` | number > 0 | `5` |
| `wait.preflight_timeout_seconds` | number > 0 | `5` |

A portable example (only placeholders and defaults) lives in the skill's
assets: `skills/cdad-cycle/assets/opencode-exec-config.example.json`, with
`mode: "service"`.

## Procedure for another coordinator

1. `prepare` publishes the canonical packet (`PACKET.md` + `REQUEST.json`).
2. `cdad_dispatch.py --project-root <root> --packet <id> --runtime <X>`
   resolves the runtime, reads its section of `runtimes.json`, transports the
   packet byte-identical and leaves the attempt of the dispatch to the module
   (one record in the same I8 ledger). The interface's own
   `--exec-config` argument is an internal flag the entry derives — never a path
   the orchestrator passes.
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
- **The removal of the store's lock contention is not demonstrated**: a
  successful concurrent journey is an empirical observation, and the residual
  contention risk of the shared store stays declared.
