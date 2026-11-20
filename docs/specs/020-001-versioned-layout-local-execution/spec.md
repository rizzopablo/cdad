# Spec — operational-path separation (versioned layout, local execution)

Feature: `020-001-versioned-layout-local-execution`
Status: Approved by <owner> on 2026-11-19.

## Description

Keep the project's versioned methodology state together with a versionable
placement declaration, while execution records remain local and ignored. A
clone recognizes the project without operational records. Existing projects
migrate manually by a documented procedure, including projects with unfinished
work. Historical packets and evidence stay byte-identical and are not made
replayable under the new toolchain.

## Declaration

`cdad/project-layout.json` (fixed path for every project) carries:

```json
{
  "schema_version": 2,
  "methodology_dir": "cdad",
  "operational_dir": ".cdad-execution"
}
```

- New projects default `methodology_dir` to `cdad/` (existing
  `cdad_layout.BOOTSTRAP_DIR`); existing projects retain their actual placement
  (`docs/` or a registered custom directory).
- `operational_dir` is a normalized repository-relative path; the default for a
  new project is `.cdad-execution/`.
- Exactly these three required fields. The current parser rejects additional
  fields and unsupported versions; an old declaration receives migration
  guidance, never silent conversion or fallback.
- The declaration path is fixed so that discovery needs no prior knowledge of
  the methodology directory. Automatic discovery of a custom methodology
  directory is **not** promised: when a project uses a custom directory, the
  user identifies it (for example in the project's agent instructions) or
  simply declares it in this file.
- Migration state: a project counts as **not migrated** when
  `.cdad/project-layout.json` exists, or when the declaration lacks
  `operational_dir` (schema 1), or when a populated `.cdad/` root remains.
  Any of those produces the migration guidance before operational writes.

## Contract

### PC-1 — Declared operational storage

Layout resolution preserves methodology placement, while new operational
records and new packet identities use the declared operational directory. The
locator is versionable and the actual declared root operational directory is
ignored.

Executable verification: adapted layout/lifecycle tests demonstrate
declaration-driven access and tracking boundaries. No installation,
deployment or publication claim.

### PC-2 — Actionable migration diagnosis

An unmigrated project receives brief actionable guidance, pointing at the
canonical migration guide, before any operational write.

Executable verification: refusal/no-write behavior on an unmigrated project.

### PC-3 — Continuation of unfinished work

The documented manual handoff permits preparing a fresh assignment without
loading historical packet or execution identities. It preserves feature,
stage, postcondition outcomes, reviews and approvals, never overwrites another
active unit, and requires established outstanding-effect dispositions and
genuine current approval/policy/authority before authorizing overlapping
effects.

Combined verification: executable fresh-preparation behavior plus independent
contextual review of the handoff, governing-reference assessment and effect
dispositions.

### PC-4 — Version-aware orchestration

Startup instructions direct the orchestrator to read the migration notice and
generate a fresh assignment after an observed methodology-version change,
before dispatch. The existing version checker compares the project's recorded
`source_version` with installed `version.txt` markers; it detects disagreement,
not same-version edits. No new tracking subsystem.

Combined verification: existing version-check regressions plus contextual
review of the instructions.

## Manual migration guide (normative content)

Create `skills/cdad-cycle/references/layout-migration.md` as the single
canonical guide:

1. Notify/coordinate running agents; retain outputs; prevent conflicting
   filesystem changes during the moves. Feature/epic completion is not
   required.
2. Check destinations; stop on collisions; never merge stores.
3. Move `.cdad/project-layout.json` to `<methodology>/project-layout.json`.
4. Rename the remaining `.cdad/` to the declared operational directory.
5. Update the moved declaration; legacy projects without a locator create
   schema 2 with their actual methodology placement.
6. Add a root-anchored ignore rule for the actual declared operational
   directory (escape Git-ignore metacharacters where needed); `/.cdad-execution/`
   is only the default example. Scripts never rewrite user ignore files.
7. No methodology files move. Reconcile temporary roots such as `.cdad/tmp`
   through an explicit current-policy decision, never by editing historical
   snapshots.
8. Before authorizing a potentially overlapping effect, establish and record
   the disposition of outstanding deliveries, partially applied
   materializations and other in-flight effects. Unknown effects require
   investigation; a note or a new objective is not resolution.
9. Inspect current policy, delegation/authority, applicable contracts and
   approval pins. Operational-path entries are historical evidence, not
   instructions to replay or rewrite them. Revoked authority and absent
   approvals remain blocking.

## Manual live-state handoff (administrative exception, approved)

- Preserve the original state snapshot; record the upgrade, prior bindings and
  outstanding-effect dispositions in existing context/history.
- For the active unit, clear only live `execution` and `active_packet`; preserve
  feature, stage, outcomes, reviews and approvals.
- Prepare a fresh assignment with `--new-execution` and the appropriate
  existing role/substage. Authorize write effects only after the disposition
  and governing-input checks.
- Start continuity under the fresh execution; do not reanchor or reconcile the
  historical chain.
- Later suspended-unit selection additionally requires no other active unit;
  restore exactly the saved unit-state fields, then null `execution` and
  `active_packet`; remove only the selected suspension entry and preserve the
  rest. This selection condition is not a migration prerequisite.
- Withdrawal, replacement, delivery/disposition and `open-unit` are not
  universal migration substitutes; each has narrower preconditions.

## Invariants

- No aliases, store-content selection, automatic migration, historical
  rewriting, fabricated approval, automatic packet invalidation or session
  relocation.
- Existing cwd/explicit-root argument semantics remain.
- Historical packets, receipts, checkpoints and journals remain
  byte-identical.
- Operational storage remains disjoint from the methodology directory.

## Acceptance criteria

- Every promise above carries its selected verification.
- Integrated regression evidence is produced from a baseline measured before
  the change.
- Independent review confirms migration sufficiency and the procedural
  handoff.
- At most two new test cases in total; existing tests are adapted as a
  coherent set.

## Correction allowance

Two rounds independently per draft/audit/result family (provisional, justified
by the coupled consumers and finite declaration/handoff surface). Remaining
blockers require adjudication or replanning, not an automatic extra loop.

## Deferred hardening

Historical replay, same-version edit detection and automated concurrent-upgrade
synchronization.

Status: Approved by <owner> on 2026-11-19.
