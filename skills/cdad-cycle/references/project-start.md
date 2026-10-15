# Project start — from rest to the first useful delegation

Short procedure for when a **brief instruction** must start a project from rest
(no prepared execution yet). It is a single short reading that **composes, by
reference — never by copying —** the primitives that already exist:

- `state-detection.md` — feature/Memory-Bank recognition (Steps 1-2).
- `project-execution.md` — prepared-execution path, policy and authority.
- `continuity.md` — the optional continuity CLI.
- `bootstrap.md` — Memory Bank initialization.
- `cdad-epic/references/state-detection.md` — epic-stage recognition.

This procedure does not redefine any of them (INV-1): it only says in which order
to use them and how to chain them to a first commission. If an execution is
already active, this is not the entry point — that path resumes an active
execution.

## 1. Recognize the root

The session directory is a **hint, not a norm**: the project may be a **nested**
repository inside a **container** (parent) directory, so the open directory must
not rule the recognition. Find the root **without imposing a layout** — no
particular directory structure is required — and **without a global search**: use
the nearest enclosing repository as the anchor instead of a massive filesystem
walk.

## 2. Classify the state

Distinguish three cases **using the primitives by reference** (never repeating the
algorithm, which belongs to `state-detection.md` and `project-execution.md`):

- **new** — no Memory Bank yet. Follow `state-detection.md` §Step 2 and `bootstrap.md`.
- **partially initialized** — a Memory Bank with `active_epic`/`active_feature`
  whose feature/epic records are incomplete. Follow `project-execution.md` §1-§3.
- **incomplete configuration** — state present but the policy
  (`docs/cdad-policy.json`) or the authority missing. Follow `project-execution.md`.

## 3. Preserve what exists

Never overwrite or clobber **existing** documentation, plans, conventions or
naming: **preserve the project's own conventions and naming** — keep its
existing epics, features and identifiers intact. CDAD's own naming convention
is `<epic-num>-<feat-num>-<slug>`; use it only when the project does not
already have a convention of its own (for example, a project may use its own
scheme such as `E001`/`F001-001`). The anti-patterns live in `bootstrap.md`;
the no-clobber rule of the first preparation lives in `project-execution.md`.

## 4. Record restrictions in their canonical place

Create only what is missing; if the place already exists, record or point to it —
never overwrite. Each discovered restriction goes to its canonical place:

| Restriction | Canonical place | How it is obtained |
|---|---|---|
| `stack` | `state.stack` | auto-detected by the `*-architect` convention (`bootstrap.md` §2b); ambiguity → ask or record the doubt |
| privacidad (privacy) | `docs/cdad-policy.json` → `path_policy.private_paths` | reserved edit (`project-execution.md`): infer and **propose**, never write without the user's decision |
| entorno de pruebas (test environment) | `test_roots` of the policy + the commands the project declares | the methodology defines the evidence (INV-6, `systemPatterns.md`) |
| límites operativos (operational limits) | `temporary_roots` of the policy + ADR-011 | `project-execution.md` |
| autoridad (authority) | `state.hitl_delegation`/`approver` + `docs/epics/<epic>/execution.md` | the **user** decides (non-delegable) |
| organización/convenciones (organization/conventions) | Memory Bank `projectbrief.md`/`systemPatterns.md` | bootstrap asks the minimum |

## 5. Inferable vs user decision

Mark each restriction **inferable** (auto-detectable with objective evidence) or a
**decision of the user**:

- `stack` is **automatic** (`bootstrap.md` §2b) — do not ask.
- privacidad and autoridad are a **decision of the user** (non-delegable).

Ask only the second kind, and keep it bounded: **three or four concrete questions**
at most (`bootstrap.md`). Without a user present, **record the doubt** in
`docs/activeContext.md` instead of asking — never invent an answer.

## 6. Chain to the first commission

Recognition is not the end. The start **chains** recognition → registering the
restrictions → preparing the **first commission**, using the prepared-execution
path (`project-execution.md`). The terminal state is a **prepared and dispatchable**
package — a **first useful delegation** — not merely having recognized the project.

**Domain of this recipe (precondition).** It applies to a project that already has
an **active epic and a registered feature** (`state.active_epic` +
`state.active_feature`, with the feature listed in `epic_features`) and the
contract the role needs already approved (`project-execution.md` §2). A **truly
empty** project does not satisfy this yet: first register the feature and sync
`epic_features` with the approved plan (route to `cdad-epic`, PD-12) and obtain
the plan approval (PD-1) — those steps belong to the coordinator/owner, not to
this recipe. Once the precondition holds, the sequence below is concrete and
runnable from the project root (`<skill-dir>` is the directory of the loaded
`cdad-cycle` skill, as the runtime reports it when the skill is loaded):

```sh
# 1. open the new execution and prepare the first packet. Add --new-execution
#    when prior context exists (a v1 context or an active v2); omit it on a
#    truly empty project.
python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root "$PWD" \
    --role architect --substage discovery --objective "<first commission>" \
    --new-execution

# 2. bind the ids prepare produced; they live under `.cdad/`:
#      execution context: .cdad/executions/<EXEC_ID>/execution.json
#      published packet:  .cdad/packets/<PACKET_ID>/{REQUEST.json,PACKET.md}
#    (prepare prints the PACKET.md on stdout; its front matter carries both ids)
EXEC_ID=<execution-id>      # e.g. exec-<feature-id>-001
PACKET_ID=<packet-id>       # e.g. <feature-id>-architect-discovery-001

# 3. validate the binding, the request and the packet before dispatching.
#    --packet consumes a physical PATH to PACKET.md, never a bare packet id.
python3 <skill-dir>/scripts/cdad_packet.py validate-state --project-root "$PWD" \
    --execution-context ".cdad/executions/$EXEC_ID/execution.json"
python3 <skill-dir>/scripts/cdad_packet.py validate-request --project-root "$PWD" \
    --execution-context ".cdad/executions/$EXEC_ID/execution.json" \
    --request ".cdad/packets/$PACKET_ID/REQUEST.json"
python3 <skill-dir>/scripts/cdad_packet.py validate-packet --project-root "$PWD" \
    --execution-context ".cdad/executions/$EXEC_ID/execution.json" \
    --request ".cdad/packets/$PACKET_ID/REQUEST.json" \
    --packet ".cdad/packets/$PACKET_ID/PACKET.md"

# 4. freeze the write-ahead checkpoint before dispatching (UPDATE.json is the
#    continuity update you author: goal/decisions/uncertainties/next_action)
python3 <skill-dir>/scripts/cdad_continuity.py begin --project-root "$PWD" \
    --execution-context ".cdad/executions/$EXEC_ID/execution.json" \
    --update UPDATE.json --json

# 5. record the dispatch attempt (docs/attempt.json per project-execution.md §5)
python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root "$PWD" \
    --record-dispatch "$PACKET_ID" --attempt-id ATTEMPT_ID --input docs/attempt.json
```

When the role returns, receive its FINAL TEXT with the re-entry CLI
(`<skill-dir>/scripts/cdad_result.py receive`), validate the receipt and register
the state transition (`re-entry.md`).

### 6.1 Opening the next queued unit — the `open-unit` operation

When the project **rests** with a `queued` feature in `epic_features`, opening
the next unit is a state operation of the CLI, never a hand edit of
`docs/.cdad-state.json`:

```sh
python3 <skill-dir>/scripts/cdad_packet.py open-unit --project-root "$PWD"
```

It opens the **first** `queued` entry of `epic_features` (or `--feature <ID>`
when that entry exists and is `queued`), and atomically writes `active_feature`,
the entry's `in-progress`+`opened_at` and `current_stage=discovery`. It
**refuses** (without writing) when a unit is already open or when a declared
`depends_on` dependency is not `done`; when the entry declares no dependencies
it says so explicitly (the plan order is the authority). The rule lives in the
spec (`PD-7`), the executable invocation in the asset
`assets/orientation-examples.json` and its operating row in `orientation.md` —
this section **references** them and does not repeat the procedure.

## 7. Resume is only for an active execution

Do not confuse "start the next unit / start from rest" with resuming an active
execution. **Without an active execution, do not run `resume`** — `resume` is for
an active execution (005-003). Starting from rest is this procedure.

## 8. Blocked configuration: actionable diagnosis

When a non-inferable input is missing (a missing policy, an authority without a
pin), stop closed, name **what is missing** and **how to continue**, reusing the
existing markers (`approval pending`, `state incoherent`) by reference — never
re-implementing them. The procedure **never fabricates authority**, never invents
an approval, and **never changes the active version silently**: it changes no
version, and it never publishes an invalid package.

## 9. Drift between the approved plan and `epic_features`

When the project already has an active epic, recognition also checks for **drift**
between the approved plan (`docs/epics/<id>/plan.md`) and `epic_features` in the
state: the list may be **out of sync** with the plan — a **mismatch**. If so,
**name what is missing or leftover**: list the **missing** feature entries the plan
has but `epic_features` lacks, and the **leftover** (extra) entries `epic_features`
has but the plan no longer contains.

Do **not** invent features to close the gap, and do **not** block silently: the
procedure **routes the synchronization to `cdad-epic`** (back to the epic
coordinator, PD-12) instead of patching the state locally from `cdad-cycle`. It
reports the drift with the named gap and continues — never fabricating features,
never waiting in silence for a resolution.

## 10. One version check

Before trusting a session, run **one** command to learn whether the **project**,
the **agents** and the **CLI** are the same version:
`python3 <skill-dir>/scripts/cdad-version-check.py --project-root "$PWD"`.

It reads the version the project's derived agents recorded
(`.opencode/agents/.cdad-derived.json` → `source_version`) and compares it with
the version declared by the installed product (the `version.txt` marker at the
installation root of the tree that hosts each piece — the same bytes behind the
agents and the CLI). It prints exactly one of four verdicts, each with its own
exit code; **only `COHERENT` is "ok"**:

| Verdict | rc | Meaning |
|---|---|---|
| `COHERENT` | 0 | project, agents and CLI share the same version |
| `DRIFT` | 1 | the three are NOT the same version |
| `NO-PROJECT-AGENTS` | 4 | nothing loaded yet to compare (version NOT verified) |
| `UNKNOWN` | 3 | an installation marker is missing (version NOT verified) |

A consumer that checks `$?` must treat **any non-zero** code as "version not
verified as coherent", never as ok. The check is honest about its boundary: the
CLI marker is read only at the installation root of the tree that hosts this
script (never by walking up into an unrelated installation), so a **development
checkout reports `UNKNOWN`** instead of borrowing the global installation's
marker. It verifies version coherence only: it does not run the suite, does not
validate the policy, and does not re-read the skill text a running session
already loaded.

The check also carries a **declared Claude Code leg** (additive). It reports the
marker of the installation root behind the Claude Code agents — resolved from the
project's activation registry when present, otherwise from the runtime's global
Claude Code agents directory — takes part in the verdict **only when such an
installation is detectable**, and declares the absence otherwise (without
changing the four verdicts or their exit codes). It never crosses an installation
boundary and never reads the OpenCode derived manifest to infer that side. The
leg's rules and output are **owned by the 005-004 contract (PD-3)** and
**referenced** here, not restated.

## 11. Orient first — the compact view, then expand on a concrete need

Before classifying, **consult first the read-only compact view** of
`<skill-dir>/scripts/cdad_packet.py status` (`orientation.md` §1), the single bounded projection
generated by code (no `stage_history`, the state stays byte-identical):

```sh
python3 <skill-dir>/scripts/cdad_packet.py status --project-root "$PWD"
```

Its `entry` selects the next action and its `next` names the route with its
declared source. **Consult the view first** and **expand only on a concrete
need** — a blocker, or a doubt that affects the next dispatch (a reason): read
the state's history, a source file or a full document **only then**, and record
the motive. Do not rebuild the state or the CLI by default; this step **reuses**
the procedure above and does not replace the canonical owners
(`state-detection.md`, `project-execution.md`, `continuity.md`), which it
references — it never copies their structure (INV-3).
