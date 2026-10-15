# Context measurement (optional) — `cdad_context_meter`

`<skill-dir>/scripts/cdad_context_meter.py` (`<skill-dir>` is the directory of the
loaded `cdad-cycle` skill, as the runtime reports it when the skill is loaded) is
an **optional** read-only CLI that emits a **runtime-agnostic measurement record**
(`context-meter-v1`, schema `assets/context-meter.schema.json`) from a runtime
session store. The record is the **contract**; the adapter **translates** and is
the only layer that knows the source table/column names — the record carries
none of them (neutrality).

**Nothing invokes it automatically.** The format and this procedure live in the
skill and are **not wired to any gate** (`prepare`, `validate-state`,
`validate-request`, review, merge). The cycle proceeds when the environment
does not expose tokens; run the meter by hand, only when it fits.

## Invocation surface

```sh
python3 "<skill-dir>/scripts/cdad_context_meter.py" \
  --store PATH [--session REF]... [--limit N] [--idle-threshold MINUTES] \
  [--steps] [--set-summary [--detail]] [--delegation-dispatch] \
  [--application-ref REF] [--application-limit {accepted,blocked,pending,unknown}] \
  [--json]
```

- **Store.** `--store PATH`, or the environment variable
  `CDAD_CONTEXT_METER_STORE`. With **neither**, it **fails closed**: `rc != 0`
  and a diagnostic on stderr that **names the missing input**. There is **no
  hardcoded path**.
- **Sessions.** `--session REF` is **repeatable** (one or several). Without it,
  `--limit N` bounds the selection (default `20`); `--limit 0` measures nothing
  and **fails closed**. The selection is always explicit and bounded — never an
  unbounded sweep.
- **Cut.** `--idle-threshold MINUTES` (default `60`) is the inactivity threshold
  of the stretch cut.
- **Detail vs. summary (output size).** `--steps` (boolean, no value) restores
  the **full ordered per-step detail** of `input_per_step` (one element per step
  of the stretch; `null` for a step whose proxy is not observable). **Without**
  it the measure carries a **fixed-size summary** and the published size limit
  holds (see *Output size*).
- **Application annotation (optional).** `--application-ref REF` and
  `--application-limit {accepted,blocked,pending,unknown}` transport an optional
  application annotation (see *Application annotation* below).
- **Delegation dispatch (005-007 PD-9).** `--delegation-dispatch` (boolean, no
  value) adds the **common delegation interface** to the recognized dispatch
  set: a `shell` call that **really invokes** `cdad_delegate.py` is a role work
  dispatch, and the record declares the recognized set with the **method** and
  **provenance** of each entry (see *Dispatch recognition* below). **Without**
  the flag the neutral record is emitted **byte-identical** to before (INV-5)
  and only the dispatch tool names are recognized.
- **Set summary (multi-session).** `--set-summary` (boolean, no value) emits the
  multi-session **set summary** as a separate additive document
  (`set-summary-v1`) instead of the neutral per-session record; `--detail`
  restores the per-session detail the summary declares in `detail_flag` (see
  *The multiplexed document and the set summary* below). Without `--set-summary`
  the neutral record is emitted byte-identical to before.
- **Output.** JSON on stdout; `--json` is an accepted no-op (JSON is the only
  output mode). `rc = 0` on success; `rc != 0` on a fail-closed condition, with
  the diagnostic on stderr.

## Bucket semantics

Every metric lives in **exactly one** of three explicit buckets. None is mixed;
none appears in two.

- **`observed`** — read **directly** from the record: reported tokens, reported
  cost, call counts, positions, times, output size.
- **`estimated`** — a **declared proxy**, never the real value. The proxy of
  *context loaded per step* is `input + cache.read + cache.write` of the step; it
  is **not** the context window, and it is **not** consumption.
- **`unknown`** — null/absent/not-reported, **with a cause**. It is **never**
  `0`.

### What is a proxy and what is not

The *context loaded per step* is a **proxy** (`estimated`): it says how much
context a step carried, not how much was consumed or billed. Do **not** read it
as the context window, as consumption, or as a hard limit. The *accumulated
processing* (sum of steps) and the *cost* are separate magnitudes and are never
conflated with the proxy.

### What is declared unknown, and why

- **`cache.write`** — the configured provider does **not** report it (it appears
  as `0` in every measured session). A reported `0` there means *not reported*,
  not *a real zero*: it is `unknown` with a cause, **never** `0`.
- **A null cost** — not reported: `unknown`, **never** `0` and never
  "free".
- **A session without token data** — a **valid** record is still emitted, with
  the token measures `unknown` (the measurement is optional).
- **A per-step proxy with a missing component** — the per-step context proxy is
  `input + cache.read + cache.write`; a step that does **not** report any of the
  three components has a **null** proxy for that step — never `0` and never a
  partial subtotal. The list keeps one element per step so the gap is visible.
- **An output magnitude without evidence** — when the stretch carries **no** tool
  call with output text, `total_output` and `max_output` are `unknown` with a
  cause, **never** `0` (there is no evidence of output). A tool call whose output
  **exists and measures 0 characters** is an **observed** `0` (present-with-zero
  is observable).
- **A milestone whose time is not observable** — when a milestone **position** is
  observable (the event exists and its `call_index`/`seq` are referenced) but its
  **time** is not (the record carries no numeric time for it), the milestone
  stays `observed` with its `position`, `time_relative` is **`null`** — never a
  fabricated `0.0` — and the milestone carries a **cause**. Its time-to measure
  (`time_to_first_resume` / `time_to_first_dispatch`) is `unknown` (value
  `null`), never `0`.

Reported input is **not** the same as billed consumption, and **not** the same as
the maximum context capacity.

### Aggregates: complete only with full coverage of the stretch

An aggregate that **sums a per-step component** over the stretch is a
**complete observation only if ALL steps of the stretch report that component**
(a reported `0` counts as reported):

- `accumulated` = Σ `tokens.input`.
- `cache.read` = Σ `cache.read`.
- `cost` = Σ `cost`.

With at least one step that does **not** report the component, the measure is
`unknown` (value `null`) — the **partial subtotal is never presented as
`observed`** — and `unknowns[]` carries **one aggregated cause per measure**
(never one per step) naming the component and the **coverage** of the stretch
(how many steps report it of how many, and how many do not).

`cache.write` keeps its own rule: because the configured provider does **not**
report it (a reported `0` means *not reported*), it is `unknown` with a cause,
**never** `0`; additionally, when some step of the stretch does not **carry** it,
the cause declares the **coverage** of the stretch (one aggregated entry).

### Per-role aggregate: the coverage is declared the same way

The **same principle** applies **one dimension up**, to the per-role aggregate
(`roles[]`). Each component **summed** in `roles[].sums` is a **declared entry**
`{value, unit, bucket, sessions_reporting, sessions_total, cause}` that carries
its **coverage**:

- the sum is a **complete observation** (`bucket: observed`, numeric `value`,
  `cause: null`) **only when EVERY session of the role reports the component**
  (`sessions_reporting == sessions_total`; a reported `0` counts as reported);
- with **at least one** session that does **not** report it, the entry is
  `unknown` with `value: null` — the **partial subtotal is never presented as the
  role total** — and `cause` declares the coverage (`k` of `n`);
- `sessions_reporting` / `sessions_total` are **always numbers**, never `null`;
- `sums.sessions` stays the **integer member count** (a count of members, not a
  sum of a measure: a real `0` is a count, not a fabricated zero).

The **same class** covers `roles[].distributions`: the observed values are
declared with their coverage `{values, sessions_reporting, sessions_total,
cause}`, so a **subset is never presented as the whole role**. When the coverage
is incomplete, `unknowns[]` carries **one aggregated cause per (role, component)**
naming the role, the component and the coverage (`k` of `n`) — **never one entry
per session**.

### Dispatch recognition: the recognized tools and the limit (D4)

The record declares, in the top-level **`reader`** key, the list
**`reader.dispatch_tools`** of tools this reader **recognizes** as a role work
dispatch (at least `subagent` and `task`). The dispatch milestone
(`first_dispatch`) is `observed` only for a call made with a **recognized**
tool.

When no such call is present, `first_dispatch` is `absent`, and its **cause
distinguishes "it did not happen" from "it was not recognized"**: it names the
**recognized set** and declares the **limit** — a dispatch made with a tool
**outside** the set is **not detected** by this reader. The consumer must
therefore not read the absence as proof that no dispatch occurred; a tool
outside the declared set is invisible to this reader.

### Delegation interface as a dispatch: the real invocation (005-007 PD-9)

With **`--delegation-dispatch`** the recognized dispatch set also includes the
**common delegation interface**. The evidence is the **same class** as the
`resume` rule: the **material fact** of the tool call, never a mention of the
program.

- **Recognized as a dispatch:** a `shell` call that **really invokes** the
  program `cdad_delegate.py` (by its canonical path or by a repository
  wrapper — the material fact is the **program**, not its exact path; same
  class as `resume`, which does not fix the CLI's path). The delegation
  arguments (`--project-root` / `--packet` / `--destination`) accompany the
  invocation.
- **NOT recognized:** a call that only **mentions** the program — the content
  of a `write`, the argument of a `grep`/`rg`, or any argument that does not
  invoke it — and a **help** call (`--help` / `-h`). The program has to be the
  **invoked** program of the shell segment, not a token handed to another
  program.

With the flag the record declares the **closed recognized set** with the
**method** and **provenance** of each entry in **`reader.dispatch_recognition`**
— exactly three entries in this version:

| Entry | `method` | Class of evidence |
| --- | --- | --- |
| `subagent` | recognized dispatch tool name | the **tool name** of the call opens a worker session |
| `task` | recognized dispatch tool name | the **tool name** of the call opens a worker session |
| `cdad_delegate.py` | material fact: the shell call invokes the program | the **shell call really invokes** the delegation program |

Each entry carries its **`provenance`** (the rule it comes from), so the
consumer knows **how** a dispatch was recognized. An `observed` dispatch
milestone carries the **`method`** of the entry that recognized it; the
milestone of a dispatch by tool **name** and the milestone of a dispatch by
**material invocation** are told apart.

**Honest limit of an absence.** With the flag, an absence cause **names the
honest limit** of the trace: in a trace that only **mentions** the program the
cause names the mention (a mention never dispatches); in a help call the cause
names the **help** exclusion; and every absence keeps the limit of PD-6 of
005-002 — **a dispatch is an `event`, never proof of `utility` nor of an
accepted result** — so the times stay `null` and the bucket `unknown`, never
`0`.

Without the flag the neutral record, its `reader.dispatch_tools` and its
absence causes are **byte-identical** to before (INV-5); the meter remains a
**session reader** (no coupling to a dispatch ledger or to the project root,
D8).

### Partial `--session` match (D5)

With several `--session` references, if **some** match and some do **not**, the
run still succeeds (`rc = 0`), measures the sessions that match, and **declares**
the unmatched requested reference(s) in `unknowns[]` **with a cause**: a subset
is **never** a silent measurement. The declaration names the requested
references by their **hashed** reference (the same form as `session_ref`) and
the measured references, so the **coverage of the request** is explicit. The
raw identifier never appears. When **none** of the requested references matches,
the run **fails closed** (`rc != 0`) as before.

## Application annotation (optional)

The record may carry an **optional** `application` field: a **referenced
annotation** that links the measurement to the **application** of a deliverable.
It has a **fixed shape** `{ ref, limit, basis }` (plus the optional
`included_sessions` / `relations`):

- **`ref`** — a **durable reference** (path / commit / receipt) to the
  application evidence. It is **transported exactly as passed** on the command
  line: it is a **reference**, **never a copy** of the referenced content. The
  meter does **not** read or embed the referenced file.
- **`limit`** — the **declared** limit, one of `accepted`, `blocked`, `pending`,
  `unknown`. It is **declared by the caller** and transported verbatim.
- **`basis`** — the **observable facts** of the document that support the limit.

**The reader never judges and never approves anything.** The annotation is **not
a new semantic classification** of the reader and **not an automatic approval**:
it is not a gate input, it does not write state, and it does **not** change the
process `rc` (the same `rc = 0` is returned for every value of `limit`). No
approval marker is ever emitted. Without the annotation input, the field is
**absent** when there is nothing to declare, or it is `unknown` **with a cause**
when a relation must be declared — the reader does **not** invent it.

**Coordinator and workers.** When the document combines a coordinator session and
its workers, it **declares which sessions are included** (`included_sessions`,
hashed references) and **which relations were observed** (`relations`,
referencing each child's `parent_ref`). The per-role aggregate sums **each
included session's own cost once** — the same cost is **never** counted twice.
A `parent_id` that points to a session **not present** in the store is reported
as an **unknown** relation in `unknowns[]` **with a cause**: the parent session
is **neither invented nor completed**. When such a declaration must be emitted
but no application reference was provided, the annotation carries `limit:
unknown` with a cause and is **anchored to the document's own durable, hashed
store reference** — an application receipt is **never invented**.

## No fabricated numbers

No field converts bytes or characters into tokens, and **no context/window limit
is fabricated**. Where a magnitude cannot be observed, it stays `unknown` with a
cause and `unknowns[]` names it. Output size is measured in **Unicode
characters** (`len(text)` over tool output text), never in tokens or bytes.

## Privacy

The record **hashes** the store reference and the session references, so the
absolute store path and the raw session identifiers never reach the output, and
the adapter never prints raw prompts or tool outputs.

Output privacy rules (the record is meant to be shareable and to be consumed by
the next feature without leaking the host):

- **Absolute host paths are omitted or hashed.** No string in the output starts
  with the root slash; the store reference and the session references are
  hashed, never raw.
- **The store path never appears.** Only its hashed reference (`run.store_ref`)
  is emitted.
- **Raw session identifiers never appear.** Each session is referenced by a
  hashed `session_ref` (and a hashed `parent_ref`); the raw id is used only to
  select and to read.
- **Raw prompts and tool outputs are never printed.** The adapter emits neither
  the text of user prompts nor the text of tool outputs; it emits only counts,
  positions, sizes and references.
- **The transcript is never embedded.** The record carries **references**
  (session reference + step/`seq`) to the original evidence, not the evidence
  itself; the original is consulted separately.
- **The observed `model` per session is contract**, not a leak: it is the parsed
  model id, or `unknown`.

## Output size

The output is **compact and bounded**: it is meant to let the consumer tell
orientation from execution and to consult the original evidence by reference,
**without injecting the whole session** into its context.

The normative limit is **16384 bytes (16 KiB) per single-session document**.
This number is **fixed by the orchestrator**; it is not chosen or relaxed by the
adapter. The document for one session stays at or below it, and it carries
**references** (the hashed session reference and the step/`seq` positions) to the
original events rather than the transcript.

### Fixing the limit: the per-step summary, and the `truncated` indicator

The per-step detail of `input_per_step` would grow with the number of steps, so
it is **not** emitted by default. **By default** `input_per_step.value` is a
**fixed-size summary** — its shape does not grow with the stretch, so the
16384-byte limit holds for **any** session size (a session of thousands of steps
emits the same-size summary):

- `count` — how many steps the stretch has.
- `last` — the proxy of the **last** step of the stretch.
- `previous` — the proxy of the step **before** the last (or `null` when there is
  none).
- `min` / `max` — the smallest / largest proxy over the **observable** proxies.
- `unobserved` — how many steps have **no observable** proxy.

A proxy that cannot be observed is `null` in `last` / `previous` / `min` /
`max`, **never** `0`; `min`/`max` are `null` when there is **no** observable
proxy. The summary **keeps** the pinned figures: for the first 005-001 session
its `last` is `203276` and its `previous` is `202222`.

The measure carries the **truncation indicator** `truncated`, whose omission is
therefore **never silent**:

- `truncated` — `true` by default (the detail is omitted), `false` with
  `--steps`.
- `cause` — the text declaring **why** the detail is omitted (or that it was
  emitted in full), **citing the published limit of 16384 bytes per
  single-session document** and the flag that restores the detail.
- `omitted_steps` — how many steps are not detailed: `count` by default, `0`
  with `--steps`.
- `detail_flag` — the name of the flag that restores the detail: `"--steps"`.

With `--steps` the limit **does not apply**: the caller explicitly asked for the
detail, and `input_per_step.value` is the **full ordered per-step list** (one
element per step, `null` where the proxy is not observable).

## The multiplexed document and the set summary (R4)

The published limit above applies **per document of session**, not to a
multi-session run. For a run over several sessions the meter emits, **first**, a
**set summary** in a **separate additive document** (`set-summary-v1`, emitted
with `--set-summary`) that carries the sessions included (hashed references),
the declared coverage, the milestones, the relevant magnitudes **with their
bucket and their coverage**, and references to the per-session detail. The
per-session detail is **not** emitted by default: it is requested with the flag
the summary declares in `detail_flag` (`--detail`). The summary is **not** a
dashboard and **not** a second memory. A magnitude without full coverage stays
`unknown` with a cause and `value: null` — a partial subtotal is **never**
presented as the set total, and **never** `0`. The neutral per-session record is
**byte-frozen**: without `--set-summary` the output is exactly as before.

**The total of the set is ≤ N × the per-session limit.** The document of a
**set** that includes N sessions is **not** bounded by the single-session number
above, but by **N × the per-session limit** (N × 16384 B): the total of the
**conjunto** grows with the **number of sessions** (N) and must be declared as
such. Reading the total without bounding it against the number of sessions
(N) — or presenting a partial subtotal as the total — is a wrong reading; that
is why the set summary is a separate document and the per-session detail is
requested apart.

**The normative limit is per document of session.** The number 16384 B
(16 KiB) bounds **one document of session**; it does **not** bound the aggregate
of the set and is **not** relaxed per session: each session document stays at or
below the limit, and the set is bounded as **N × the per-session limit**.

## Read-only and deterministic

The store is opened **read-only** (`?mode=ro`) and is never checkpointed or
written; the meter uses only the Python standard library, and the same input
produces the same bytes.

**The real session base is NEVER written.** The absence of writes is verified on
**controlled temporary bases** built by the tests (and on the store read-only):
**never** is a write attempted on the **real session base** — not even to prove
that it is prohibited. The prohibition is a **declared rule** and a
**verifiable absence** in the tests, not a destructive check against the live
base.

## Samples and the 005-001 closing session (PD-14)

The feature is exercised against **declared samples**: the **first session of
005-001**, the **closing session of 005-001** (declared by the epic/plan as
«≈4 h, 13 sub-agents, max ≈310k input»), and the **sonda 2 of 003-007**. The
first session and sonda 2 are reproduced from fixtures by the acceptance tests.
The **identity** of the closing session is a separate, evidence-bound question,
answered below.

### Criterion to identify the closing session (reproducible)

The criterion is applied to the runtime session store **alone** (read-only and
bounded). A session qualifies as the closing session of 005-001 when **all** of
these observable facts hold:

1. **Same session/directory provenance** — the candidate belongs to the same
   project/session directory as the other 005-001 samples (same store, same
   recorded working directory).
2. **Inside the 005-001 window** — the candidate's work falls inside the work
   window declared for 005-001 by the epic/plan (the window is **cited by
   reference**, not restated here).
3. **Declared child-session count** — the candidate has **exactly the number of
   child sessions declared for the sample (13)** — sessions whose parent is the
   candidate.
4. **Declared active work duration** — the candidate's active work spans the
   **declared duration (≈4 h)**.

A candidate satisfying all four is the closing session; if several do, the one
matching the declared child-session count and duration is selected. The
criterion is **re-runnable**: list the sessions in the window, compute each
one's child-session count and active span, and match against the declared
sample. The numbers the criterion compares against are the **declared** sample
values, not values re-measured and copied.

### Resolution — the identity cannot be established (PD-14: unknown with cause)

Applying the criterion to the available store **does not yield a session**. In
the 005-001 window the candidate sessions (ordered by child sessions) carry
**7, 22 and 30 child sessions** — **none carries 13**. Therefore:

- The closing session of 005-001 is declared **`unknown` with a cause**: the
  declared criterion (child-session count = 13) is **not satisfied by any
  observed session**, so its identity **cannot be established by evidence**.
- It is recorded as an **open item / debt** of the feature, as PD-14 permits.
  The sample is **never fabricated**, and **no** observed session is presented
  as the closing session: the record simply does not claim an identity it
  cannot support.

This is a **documentation-level** resolution. It does not change the meter, the
neutral record or its contract: the record has no field that names a session by
a feature's history, so PD-14 is verified by this reference (and by review),
**not** by a unit assertion on the meter's output.
