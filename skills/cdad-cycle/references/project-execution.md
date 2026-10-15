# Project execution bootstrap (v2)

Reference for adopting the durable v2 execution model of `cdad_packet.py prepare`.
Everything below runs from the **installed product**: the CLI travels with this
skill (`scripts/cdad_packet.py`), so a consumer project never needs the checkout.

## 1. Policy configuration (owner-owned)

The single editable policy is `docs/cdad-policy.json`:

```json
{
  "schema_version": 1,
  "path_policy": { "...": "classification rules" },
  "temporary_roots": []
}
```

- Exactly these three fields; no models, authority or Bash rules.
- The CLI never writes it and no role scope may edit it.
- Optional `path_policy.private_paths` (project-relative exact paths or globs) is
  the single deliberately obvious barrier, for files no role needs. In OpenCode
  every entry is denied in `read` for every role, emitted after the allow rules
  so findLast wins; the `edit` entry is declared as well, but in this version it
  was not observed to be applied (W-3). In Claude Code the dynamic guard blocks the
  mediated tools over the path and its whole subtree (Read/Edit/Write/MultiEdit)
  and a `Grep`/`Glob` whose `path` points at it, plus a `Glob` whose `pattern`
  reaches into it from a bounded parent path. Without the field the behavior is
  unchanged; an invalid entry (absolute, with `..`, or empty) fails policy
  validation (rc≠0), like a root. Declared limitations — it is an obvious
  barrier, not a sandbox: the OpenCode `read` denial is verified live
  (t7-live-walk.md §6) while its `edit` entry is not applied in this version
  (W-3); in Claude Code the guard mediates only implementer and test-writer, so
  architect, reviewer and scribe rest on the role instruction and the audit
  (t7-live-walk.md §6); a `Grep` over a PARENT folder can still return private
  content, glob entries have best-effort semantics (simple paths are
  recommended), and Bash is not bounded. It replaces neither the role
  instruction nor the audit.
- Propose a deterministic, write-free starting point:

  ```sh
  python3 <skill>/scripts/cdad_packet.py prepare --project-root "$PWD" --propose-policy
  ```

  The owner reviews the proposal and materializes it byte-for-byte.

> Run every command in this reference from the **project root**: `--input` and
> `--decision-ref` resolve against the current directory, not against
> `--project-root` (which is resolved against the current working directory and
> must be an existing directory).

## 2. Authority (I2)

`prepare` verifies authorization from the project records, never from names or
defaults:

- **Role-aware contract approval** — the approval is specific to the role's own
  object and is verified against the contract bytes (the digest is the one
  `validate_request` already computed):
  - **architect** — an `epic_history` entry for the active epic with
    `stage: "epic-plan"` and a non-empty `approved_by` (no hash pin: the epic
    plan is the epic's live mandate, D2). The architect is enabled by the plan,
    never by a feature spec.
    - **Unit contract.** With an active epic, the contract pinned for the
      architect's unit is the **generated unit projection** of the epic plan,
      published beside its packet and pinned by its digest; when the unit cannot
      be located without ambiguity it is the **declared fallback** to the full
      approved plan (`approved-epic-plan`). The projection, its locator, its pin
      and its `kind`/`path` are defined in
      `docs/specs/005-013-unit-contract/spec.md` §2.1-§2.2 (PD-1..PD-5): this
      reference names that contract, it does not restate it.
    - **Origin; no re-approval per unit.** The projection records its origin
      (unit, plan, the plan's sha at generation, the approving `epic_history`
      `epic-plan` entry and `policy_sha256`). Authorization **remains** that
      `epic_history` `epic-plan` entry with `approved_by` — the architect is
      enabled by the epic plan, never by a feature spec — and is **not**
      re-approved per unit while the projection is unchanged; when the
      projection changes, the orchestrator decides (spec §2.7, PD-12).
    - **Leaving the `impeded` verdict.** An `impeded` verdict (authorization
      withdrawn) is lifted with the **existing** mechanisms: registering an
      `epic-plan` approval in `epic_history` under the HITL, or restoring the
      `hitl_delegation`; the next packet takes the new projection as its
      baseline. Reconciliation of a `dispatched` packet is **not** defined here
      (005-012). Defined in spec §2.5 (PD-10).
  - **every other role** — a `stage_history` entry with `feature`,
    `stage: "specification"`, a non-empty `approved_by` and the mandatory
    `contract_path` + `contract_sha256` pin (D3). The pin must NAME the contract
    verified for the role: `contract_path` equals that contract's path
    (C1/PD-18) and the digest equals `sha256(<contract_path>)`. A foreign or
    absent path, or editing the spec after approval, invalidates the
    authorization.
  - A declared `draft-plan` (reviewer/plan-review) is a first-class,
    non-approved review object: it carries no approval requirement.
  A missing, unpinned or drifted record fails with the `approval pending`
  diagnostic (rc=2, no effects).
- **Delegation** — with an active epic: `hitl_delegation` present, a `status`
  field that if present must be `"active"` (its absence does not invalidate), an
  `epic_id` field that if present must match the active epic (its absence leaves
  the decision to `scope`), `source` pointing to an existing file, `scope`
  naming the epic as an exact token (`:` and parentheses also separate tokens),
  `active_epic` matching and no `revoked_at`.
- **Standalone** — `active_epic: null`: only the role-aware contract approval
  is required; the execution is created with `epic_id: null` (no epic is
  fabricated).

## 3. First preparation (bootstrap)

```sh
python3 <skill>/scripts/cdad_packet.py prepare \
    --project-root <root> --role <role> --substage <substage> \
    --objective "<assignment>"
```

- Creates `.cdad/executions/<execution-id>/execution.json` (`schema_version: 2`),
  binds it in `state.execution`, and publishes `.cdad/packets/<id>/`.
- If any prior context exists (a v1 `.cdad/execution.json` or an active v2),
  add `--new-execution`; without it the call fails with a diagnostic.
- v1 contexts are never adopted forward: an explicit `--execution-context` to a
  v1 document fails with a diagnostic and rewrites nothing.

## 4. Resume

```sh
python3 <skill>/scripts/cdad_packet.py prepare --project-root <root> \
    --resume-packet <packet-id>
```

Re-emits the published packet byte-for-byte. It accepts no ordinary prepare
option (role, substage, objective, scopes, inputs, …).

## 5. Record a dispatch attempt

```sh
python3 <skill>/scripts/cdad_packet.py prepare --project-root <root> \
    --record-dispatch <packet-id> --attempt-id <id> --input docs/attempt.json
```

`docs/attempt.json` has exactly `runtime`, `model_configured`,
`model_reported`, `session`, `started_at` (each text or `null`) and
`provenance` (field → source). It records observations only: no results, no
gate decisions, no completion. Repeating identical data is idempotent.

## 6. Policy reconciliation

When `docs/cdad-policy.json` changes after an execution was created:

```sh
python3 <skill>/scripts/cdad_packet.py prepare --project-root <root> \
    --reconcile-policy <sha256> --decision-ref <owner-decision-file>
```

The owner edits the policy and records the decision; `prepare` accepts the
revision for the execution (no pending packet allowed), keeps the previous
revisions in `policy_history`, and changes no package. Until reconciliation,
new preparation, resume and dispatch registration are blocked.

Reconciliation does not make previous packets resumable (I11): a packet
rendered under a superseded revision fails `--resume-packet` with a diagnostic
naming the packet's revision and the now-accepted one, and asks for a new
packet to be prepared. Its bytes stay on disk; prepare a new packet under the
accepted revision instead of resuming the old one.

## 7. Runtime mechanisms

- **OpenCode** — `prepare` publishes project-local derived agents under
  `.opencode/agents/` from the installed agents
  (`$CDAD_OPENCODE_AGENTS_DIR` or `~/.config/opencode/agents`) and the project
  policy, with the `.cdad-derived.json` manifest.
  - **Mechanism limit (declared, PD-15).** The only path barrier verified live
    in OpenCode is `read` (reading and listing: a denied path stays denied
    across absolute, relative and `..` variants — t7-live-walk.md §2, §4). The
    derived agents also declare `edit` maps by path, but in OpenCode 2.0.16 the
    live probe did not observe them applied (W-3: `write` created files and
    `edit` modified `docs/cdad-policy.json` despite the deny): they are
    documentation of intent, not a guarantee. `grep`/`glob` are not scoped by
    path either (OpenCode matches the search PATTERN, W-2), just like the
    permissive Bash policy. Writing discipline therefore rests on the role
    instructions plus the orchestrator's audit: after a task, the orchestrator
    runs `git diff --name-only` over the commit range and the working tree and
    compares it against the packet's `write_scope`; a write outside scope
    invalidates the result.
- **Claude Code** — the installed guard (`~/.claude/cdad-scripts/path-guard.sh`)
  loads the project policy and classifies paths with the installed CLI
  (`$CDAD_PACKET_CLI`, or the skill copy under `$HOME/.claude/skills/cdad-cycle/`).

## 8. Reemplazo (`--replace-packet`)

Replace the active packet when it is **prepared and never dispatched** and its contract
(or accepted policy revision) has genuinely changed. The sub-mode re-resolves the
contract of the day and publishes a successor **only** with the still-valid role
authorization — it never invents authorization and never rewrites the superseded bytes.

```sh
python3 <skill>/scripts/cdad_packet.py prepare --project-root <root> \
    --replace-packet <packet-id> --reason "<texto>"
```

- **Precondition (PD-7/PD-10).** Only the **active** packet can be replaced, and only
  while its `active_packet.status` is `prepared`. A `dispatched` packet fails with the
  `packet obsolete` marker naming the required **reconciliation** (PD-10); a
  `completed`/`failed` packet is not replaceable either.
- **Verifiable obsolescence (PD-8).** Accepted only when the packet is genuinely
  obsolete: the contract `sha256` recorded in its `REQUEST.json` differs from the
  current file, **or** the packet's recorded policy revision differs from the accepted
  one (I11). Without either drift it fails with rc=2 and no effects — replacement is not
  a shortcut around the approval rule (PD-4).
- **Mandatory reason (PD-9).** `--reason` must be non-empty; `--reason` without
  `--replace-packet` is rejected.
- **Re-resolution and authorization (PD-11).** The contract and policy are re-resolved
  to the current ones, and the successor is published **only** if the still-valid
  role-aware approval enables it. With the C1/PD-18 pin, the `specification` entry must
  NAME the contract: `contract_path` equal to the verified contract's path **and**
  `contract_sha256` equal to its digest. If the current contract is not authorized the
  command fails with `approval pending`, publishes nothing and leaves the old packet
  intact.
- **Conservation of the previous assignment (PD-19/INV-7).** Without correction
  options, the new `REQUEST.json` conserves, field by field, the predecessor's
  `execution_id`, `role`, `substage`, `objective`, `inputs`, `read_scope`, `write_scope`,
  `invariants`, `expected_output` and `evidence_required` (the role defaults are no
  longer recomputed). The contract is re-resolved, never conserved.
- **Correction options (PD-20/D7).** Besides the selector and `--reason`, the sub-mode
  admits exactly `--input`, `--read-scope`, `--write-scope`, `--invariant`,
  `--expected-output`, `--evidence`. Each, **when given**, replaces that whole
  list/field (it is not appended to what was conserved). The sentinel `-` as the
  **only** value of a list field leaves it empty; `-` mixed with other values of the
  same field is an ambiguity (rc=2, no effects). `expected_output` is a scalar:
  `--expected-output -` empties it.
- **Mandatory role floors (PD-21/INV-7).** A correction never drops the role's
  mandatory floor: `DEFAULT_INVARIANTS` (test-writer, implementer) and `DEFAULT_EVIDENCE`
  are re-added, so `--invariant -` / `--evidence -` cannot remove them. A role without
  mandatory invariants (architect) may end with an empty `invariants`.
- **Same validations (PD-22).** A corrected packet passes the SAME validations as an
  ordinary `prepare`: role authorization, scopes against the policy, `inputs` inside the
  `read_scope` and closed fields. An invalid correction fails rc=2, publishes nothing
  and leaves the previous packet byte-for-byte intact; the diagnostic names the
  **field**, the **reason** and the correcting **option** (e.g. a `--read-scope` outside
  the policy names `read_scope` and `--read-scope`).
- **Mixed argv (PD-23).** `--replace-packet` does **not** accept `--role`, `--substage`,
  `--objective`, `--new-execution`, `--out-dir`, `--contract-kind`, `--contract-path`,
  `--plan-version`, `--resume-packet`, `--record-dispatch`, `--attempt-id`,
  `--reconcile-policy`, `--decision-ref` or `--propose-policy`; a mixed argv is rejected
  once (rc=2), before any lock or write.
- **Relation to resume (PD-16).** `--resume-packet <id>` on an obsolete packet fails with
  `packet obsolete`, naming the registered and current values; if the packet is
  `prepared` it points to `--replace-packet`, if `dispatched` it points to reconciliation.
- **Superseded record (PD-7/PD-24).** The previous packet's `REQUEST.json` and
  `PACKET.md` stay byte-for-byte identical; a durable record is written to
  `.cdad/packets/<id>/.superseded.json` with `superseded_by`, `reason`, `superseded_at`,
  `contract_sha256_old`, `contract_sha256_new`, plus the field trace `conserved_fields`
  and `changed_fields` — disjoint and covering the assignment universe
  `{execution_id, role, substage, objective, inputs, read_scope, write_scope, invariants,
  expected_output, evidence_required}`. Together with both `REQUEST.json` documents it
  shows what was conserved, what changed and why. No `stage_history`/`epic_history`
  entry is created or modified (INV-2).

The normative contract is the approved feature spec
(`docs/specs/005-001-idle-and-v7-bootstrap/spec.md`, PD-7..PD-11, PD-16, PD-19..PD-24);
this section is the operative reference.

## 9. Register a transition (`register-transition`)

`register-transition` records an explicit orchestrator decision over a transition
of the durable state: receiving a delivery (`delivery`), approving a gate
(`gate`), advancing a stage (`advance`), closing a feature (`closure`), the late
reception of a delivery for an already-closed feature (`late-delivery`) and the
disposition of a dispatched packet with no receipt (`disposition`, with
`--resolution <abandoned|superseded>` and `--replaced-by` when the resolution is
`superseded`).

```sh
python3 <skill>/scripts/cdad_packet.py register-transition --project-root <root> \
    --transition <class> [...]
```

The operation, its classes and their checks are the contract of the approved
feature spec (`docs/specs/005-012-transition-registration/spec.md` §2.1-§2.3);
this section names the operation, it does not restate the checks.