# Draft specification — operational-path separation

**Status: Draft; not approved.** Correction for draft-family closing check 2/2; no further round authorized. Controlling decisions: `docs/planning/epic-020-restart.md:111–182`.

## Description

An operator manually migrates CDAD’s locator and operational directory, then continues unfinished work through fresh assignments. Existing methodology placement and user-level progress remain unchanged. Historical assignments and evidence remain byte-identical, without replay support.

### Declaration

At `cdad/project-layout.json`:

```json
{
  "schema_version": 2,
  "methodology_dir": "docs",
  "operational_dir": ".cdad-execution"
}
```

Retain the project’s actual `methodology_dir`. Both directory values are normalized repository-relative paths; operational storage remains disjoint from methodology. New-project operational default: `.cdad-execution`.

Schema 2 has exactly these three required fields. The current parser rejects additional fields and unsupported versions (`cdad_layout.py:152–164`). Old declarations receive migration guidance, not conversion or fallback.

## Contract

### A. Versioned placement and local execution

**PC-1.** Layout resolution preserves methodology placement; new operational records and packet identities use the declared operational directory. The locator is versionable, and the actual root operational directory is ignored.

**Verification:** executable tests plus contextual review of ignore instructions. Acceptance: adapted layout/lifecycle tests establish declaration-driven access and tracking boundaries. Evidence: test output and review. Limit: no installation/publication claim.

### B. Manual upgrade preserving progress

**PC-2.** An unmigrated project receives brief actionable guidance before operational writes.

**PC-3.** The documented administrative handoff permits fresh preparation without loading historical packet/context identities. It preserves progress and evidence, prevents overwriting another active unit, and requires established outstanding-effect dispositions before authorizing overlapping effects.

**Verification:** combined refusal/fresh-preparation tests and independent review of the handoff, governing-reference assessment and effect dispositions. Both must pass. Evidence: test output and review findings. Limit: operator coordination and truthful assessment remain procedural.

### C. Version-aware orchestration

**PC-4.** Startup instructions direct the orchestrator to read the migration notice and generate a fresh assignment after an observed methodology-version change, before dispatch.

**Verification:** combined existing version-check regressions and contextual instruction review. The checker compares project `source_version` with installed `version.txt` markers (`cdad-version-check.py:194–236`). It detects disagreement—not same-version edits or a past change after every comparison leg advances. Record observed versions through existing context notes; no tracking subsystem.

## Invariants and acceptance

No aliases, store-content selection, automatic migration, historical rewriting, fabricated approval, automatic packet invalidation or session relocation. Existing cwd/explicit-root semantics remain.

Acceptance requires all postconditions, integrated regression evidence and independent migration-sufficiency review.

**Correction allowance:** two rounds independently per draft/audit/result family, provisional. Consumers are coupled, but declaration/handoff changes are finite. Remaining blockers require adjudication or replanning, not another automatic loop.

**Deferred-hardening:** historical replay, same-version edit detection and automated concurrent-upgrade synchronization are outside scope.

# Draft migration guide

Create `skills/cdad-cycle/references/layout-migration.md` as the single canonical guide.

## Physical migration

Migration may occur with active and suspended work. The upgrading user/operator must notify and coordinate running agents, retain outputs and prevent conflicting filesystem changes during the moves; feature/epic completion is unnecessary.

Check destinations first; stop on collisions, never merge stores. With `ROOT`, `METHOD` and normalized `OP` identifying the actual root, unchanged methodology placement and declared operational directory:

```bash
mkdir -p "$ROOT/cdad"
mv -n "$ROOT/.cdad/project-layout.json" "$ROOT/cdad/project-layout.json"
mv -n "$ROOT/.cdad" "$ROOT/$OP"
cp -n "$ROOT/$METHOD/.cdad-state.json" \
      "$ROOT/$OP/migration-state-before.json"
```

Legacy projects without a locator manually create schema 2. Update the moved declaration. Manually add a root-anchored directory ignore rule for **the actual declared `operational_dir`**, escaping Git-ignore metacharacters where necessary; `/.cdad-execution/` is only the default example. Scripts do not rewrite user ignore files.

No methodology files move. Reconcile temporary roots such as `.cdad/tmp` through an explicit current-policy decision, never by editing historical snapshots.

## Outstanding effects and governing inputs

Before authorizing **any potentially overlapping effect**, the operator establishes and records the disposition of outstanding deliveries, partially applied materializations and other in-flight effects from available outputs, journals, target files and agent communication.

Unknown effects require investigation/resolution first—not assumed completion or permission to repeat. A fresh narrowly read-only assessment may help; it does not authorize subsequent writes. Preserve all evidence. This is procedural guidance, not a new CLI gate.

Inspect current policy, delegation/authority, applicable contracts and required approval pins. Use saved `resume_checks`, contract paths/digests and context metadata to identify affected governing references. Operational-path entries are historical evidence, not instructions to replay or rewrite them. Investigate missing/changed governing inputs; obtain necessary policy decisions or genuine approvals before renewed effects. Revoked authority and absent approvals remain blocking.

## Manual live-state handoff

**Proposed administrative exception requiring adoption with this specification:**

- Preserve the original state snapshot and record the upgrade, prior bindings and outstanding-effect dispositions in existing context/history.
- For the active unit, clear only live `execution` and `active_packet`; preserve its feature, stage, outcomes, reviews and approvals.
- Prepare a fresh assignment with `--new-execution` and the appropriate existing role/substage. Authorize write effects only after the preceding disposition and governing-input checks.

Clearing these bindings avoids historical selection; fresh preparation publishes new bindings before validation (`cdad_packet.py:3430–3479,6910–6937,7151–7166`). Start continuity under the fresh execution; do not reanchor/reconcile the historical chain.

**Later suspended-unit selection:** first require no other active unit and coherent idle selection, matching current selection safety (`1091–1094`). This is **not a migration prerequisite**.

Preserve the selected registry entry before changing state. Replace the complete unit-state field set:

`active_feature`, `current_stage`, `tdd_substage`, `postconditions_status`, `audit_status`, `review_status`, `active_packet`, `execution` (`731–733`).

Remove those fields from the current state, restore exactly the saved `unit_state` fields, then set `execution` and `active_packet` to null. Remove only the selected suspension entry and mark only its feature in-progress; preserve every other suspension. Apply the governing-input/effect checks above, then prepare fresh. Historical `resume-unit` cannot substitute: it checks old paths/digests (`1099–1118`).

Neither withdrawal, replacement nor delivery/disposition is universal here: withdrawal concerns never-dispatched packets; other routes load old contexts. `open-unit` requires rest and resets discovery, so it must not reset open progress.

# Ordered implementation plan

1. **Test-writer:** baseline/audit; adapt existing promises. At most two new cases: unmigrated refusal/no-write; manual active handoff/fresh preparation. No disguised parameter expansion.
2. **RED → implementer GREEN:** modify `cdad_layout.py`; packet/result/continuity/guard/dispatch/delegate/delegate_opencode/version-check siblings; activation, shell guard, CI evidence default, suite canary and `.gitignore`. Preserve standalone eligibility and existing path-argument semantics. Run integrated regression immediately.
3. **Implementer:** guide and pointers in bootstrap/project-start/orientation, orchestrator source and relevant packet/schema descriptions. Generate affected derivatives canonically. Independent review verifies the three corrected procedural findings and executable evidence.

Adapt `test_019_004_*.py`, bootstrap, suspend/resume, idle-history, relative-root, receipt/materialization and version-check modules.

```bash
python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py')

rg -n '\.cdad|OPERATIONAL_DIR|LOCATOR_RELPATH' \
  skills/cdad-cycle/scripts skills/cdad-cycle/assets scripts sources
```

Classify literals; do not demand zero historical/filename matches. No tests, migration commands or edits were performed.