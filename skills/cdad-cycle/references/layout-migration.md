# Layout migration — operational-path separation (020-001)

This is the single canonical guide for moving a project from the legacy
operational layout (`.cdad/`) to the versioned layout: methodology state stays
versioned, and execution records live in a declared, ignored operational
directory. It is a **manual** procedure. No script converts, rewrites or
replaces anything for you, and no CLI verb performs the migration.

`<skill-dir>` is the directory of the loaded `cdad-cycle` skill. `<methodology>`
is the project's methodology directory: `docs` for a legacy project, `cdad` for a
new one, or the registered custom directory. `<operational>` is the operational
directory the declaration names (default `.cdad-execution`).

## When this guide applies

A project is **not migrated** when any of these holds:

- `.cdad/project-layout.json` exists (old locator);
- the declaration `cdad/project-layout.json` lacks `operational_dir` (schema 1);
- a populated `.cdad/` root remains (any file or symlink beneath it; empty
  directories do not count).

Until the project is migrated, every operational write is refused with a message
that names this guide. Nothing is written, converted or read as a fallback.

## Before you start

1. Tell the running agents that the layout is changing, and coordinate with
   them so that none writes under `.cdad/` while the moves run.
2. Keep every output already produced. Feature or epic completion is **not**
   required; the migration happens with open work.

## Migration steps

**Step 1 — Coordinate.** Done in *Before you start*: no conflicting filesystem
changes during the moves, and all outputs retained.

**Step 2 — Check destinations; never merge.** Before changing anything, check:

- If both `cdad/project-layout.json` and `.cdad/project-layout.json` exist, it is
  a collision: **stop** and report to the owner. Do not merge them and do not pick
  one.
- If the operational directory (default `.cdad-execution/`) exists and is not
  empty, it is a collision: **stop** and report to the owner.

Never merge the old `.cdad/` store into an existing one, and never choose between
the contents of two stores.

**Step 3 — Place and update the declaration.** The fixed declaration path is
`cdad/project-layout.json` for every project; it does not depend on the
methodology directory. Use the first case that applies:

- **(a) Already at the fixed path.** `cdad/project-layout.json` exists. If it is
  schema 2 with `methodology_dir` and `operational_dir`, it is current: do not move
  or overwrite it. If it is schema 1 (no `operational_dir`), update that same file
  in place: set `schema_version` to `2`, keep `methodology_dir` unchanged, and add
  `operational_dir` set to `.cdad-execution` (or the directory the owner chooses).
  Do not create a second declaration, and do not stop.
- **(b) Old locator only.** `.cdad/project-layout.json` exists and
  `cdad/project-layout.json` does not. Move it to `cdad/project-layout.json`, then
  apply case (a) to the moved file. For a legacy project whose methodology stays in
  `docs/`, this creates a `cdad/` directory that holds only the declaration.
  Methodology files do not move.
- **(c) No locator.** Neither file exists. Create `cdad/project-layout.json` with
  exactly three fields: `schema_version` `2`, `methodology_dir` set to the
  project's actual methodology placement, and `operational_dir` set to
  `.cdad-execution` (or the directory the owner chooses). A legacy project keeps its
  existing `docs/` where it is, so its `methodology_dir` is `"docs"` (or its
  registered custom directory). A new project uses `"cdad"`.

**Step 4 — Rename the remaining operational root.** If a populated `.cdad/` root
remains, rename `.cdad/` to the `operational_dir` declared in step 3 as a whole
(executions, packets, continuity records, and the rest). Move the entire tree; do
not select subsets and do not edit its contents. The declared `operational_dir`
must be a normalized repository-relative path that is neither `.cdad` nor inside
`<methodology>/`. If `.cdad/` is absent or empty, there is nothing to rename.

**Step 5 — Confirm the declaration.** The declaration you have now has exactly these
three fields, and it is the only declaration (no `.cdad/project-layout.json`
remains):

```json
{
  "schema_version": 2,
  "methodology_dir": "<the actual methodology placement>",
  "operational_dir": "<operational>"
}
```

The `operational_dir` here is the one step 4 used. The `cdad_layout.py base`
check at the end of this guide fails closed if the declaration is still invalid.

**Step 6 — Ignore the operational directory.** Add a **root-anchored** rule for
the actual declared directory to the project's ignore file. For the default:

```gitignore
/.cdad-execution/
```

The default is only an example. For any other name, use the same root-anchored
form with the directory's name. Escape Git-ignore metacharacters where they
occur (for example a leading `#` or `!`, a trailing space, `*`, `?`, `[`, `\`).
**Scripts never rewrite user ignore files**: you make this edit yourself. To
check it, run `git check-ignore -v <operational>/` (read-only) and confirm that
`git ls-files <operational>` is empty. Any older `.cdad/` entry is the owner's
decision; no script touches it.

**Step 7 — Temporary roots and methodology files.** No methodology file moves.
For temporary roots such as `.cdad/tmp`, take an explicit current-policy
decision and record it:

- either the root moves under `<operational>/` and the policy's
  `temporary_roots` names the new path (policy edits are a reserved owner edit,
  `project-execution.md`);
- or the owner explicitly removes it.

Never reconcile a temporary root by editing a historical snapshot (packets,
receipts, checkpoints, journals).

**Step 8 — Dispose of outstanding effects first.** Before authorizing any effect
that could overlap an earlier one, establish and record the disposition of:

- deliveries that were sent but not received;
- partially applied materializations;
- any other in-flight effect.

Use the existing route for each kind: receive or re-entry for a delivery,
`register-transition --transition withdraw` for a prepared package that will
never be dispatched, the owner's materialization route for a partial
materialization. An effect whose state is **unknown** requires investigation
first. A note, or a new objective, is **not** a disposition.

**Step 9 — Check governing inputs.** Inspect the current state of:

- the policy (`<methodology>/cdad-policy.json`);
- delegation and authority (`state.hitl_delegation`, `approver`);
- the applicable contracts;
- the approval pins (for example `docs/epics/<epic>/execution.md`).

Operational-path entries inside old packets or approvals are **historical
evidence**. Do not replay them and do not rewrite them. Revoked authority and
absent approvals **remain blocking**: stop until the owner resolves them.

**Verify.** Read-only checks:

```sh
python3 <skill-dir>/scripts/cdad_layout.py base --project-root "$PWD"   # exit 0, prints the methodology base
python3 <skill-dir>/scripts/cdad_packet.py status --project-root "$PWD" # compact view, writes nothing
```

## Live-state handoff (active unit, administrative exception)

Use this when a unit is active and has work in progress. It is the owner-approved
exception that lets the unit continue under the new layout without rebuilding
its history. Steps 8 and 9 must already be complete.

1. **Snapshot and record.** Save a byte-identical copy of the state file
   (`<methodology>/.cdad-state.json`; for legacy projects `docs/.cdad-state.json`)
   at a location you record. Record in the existing context
   (`docs/activeContext.md`) and history: the upgrade, the prior values of
   `execution` and `active_packet`, and the outstanding-effect dispositions from
   step 8.
2. **Clear only the two bindings.** In the live state, set `execution` and
   `active_packet` to `null`. Change nothing else. Feature, stage, outcomes
   (postconditions), reviews and approvals stay exactly as they are.
3. **Prepare a fresh assignment.** Use the role and substage that the current
   stage already requires:

   ```sh
   python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root "$PWD" \
       --role <ROLE> --substage <SUBSTAGE> --objective "<objective>" --new-execution
   ```

   Authorize write effects only after the disposition and governing-input
   checks above.
4. **Start continuity under the fresh execution.** Begin the continuity record
   with `cdad_continuity.py begin` against the new execution context. Do not
   reanchor or reconcile the historical chain.
5. Continue with the normal protocol (validate, `begin`, record the dispatch) as
   in `project-start.md` §6, using the new execution's paths under `<operational>/`.

## Suspended units (later, separate from migration)

Selecting a suspended unit is **not** a migration prerequisite. It requires that
**no other unit is active**, with no unresolved active work, and it is done by
hand only for the record described here:

1. Confirm that `suspended_units[<ID>]` exists and that `<ID>` is listed in
   `epic_features`.
2. Restore the saved fields from `suspended_units[<ID>].unit_state` **exactly**:
   `active_feature`, `current_stage`, `tdd_substage`, `postconditions_status`,
   `audit_status`, `review_status`. A member that is absent in `unit_state` stays
   absent; do not write it as `null`.
3. Set `execution` and `active_packet` to `null`.
4. Set `epic_features[<ID>].status` to `in-progress`, for the selected unit only.
   This is what the preparation and lifecycle expect, as `resume-unit` does today.
5. Remove **only** the `suspended_units[<ID>]` entry. Preserve every other
   suspension entry and every historical entry (an empty map remains `{}`).
6. Record the upgrade and migration note in the existing context
   (`docs/activeContext.md`) or in the existing stage history entry. Do not rewrite
   historical entries, and do not fabricate an approval.

The "no other active unit" precondition and the governing-input and effect checks
(steps 8 and 9 above) still apply before any write effect is authorized from the
restored unit.

Historical `resume-unit` is **not** a substitute for this procedure. Its
`resume_checks` record references and digests taken before the move, and the verb
blocks on any absent or altered reference, with no bypass.

## What stays historical, and what is not a substitute

- **Historical packets, receipts, checkpoints and journals stay byte-identical.**
  Their `.cdad/` paths are evidence. The migration does not replay them and does
  not promise that they validate under the new toolchain. Nothing is invalidated
  automatically.
- **Sessions are not relocated.** The existing cwd and explicit-root arguments keep
  their meaning.
- These actions are **not** universal migration substitutes. Each has its own
  narrower precondition:
  - `register-transition --transition withdraw`: only for a `prepared` packet that
    will never be dispatched. It closes that packet as failed.
  - `--replace-packet`: only when the contract of a prepared packet has changed
    (`project-execution.md` §8).
  - Receive or disposition of a delivery: only for that delivery's own outstanding
    effect (step 8).
  - `open-unit`: only at rest, to open the first eligible `queued` unit. It
    refuses when a unit is already open.
