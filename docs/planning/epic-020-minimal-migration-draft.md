# Draft specification — operational-path separation

**Status: Draft; not approved.** Controlling decisions: `docs/planning/epic-020-restart.md:111–148`.

## Description

An operator upgrades CDAD, manually migrates its locator and operational directory, and continues unfinished work through a fresh assignment. Existing methodology placement and user-level progress remain unchanged. Historical assignments and evidence remain intact, without a replay guarantee.

### Proposed declaration

At `cdad/project-layout.json`:

```json
{
  "schema_version": 2,
  "methodology_dir": "docs",
  "operational_dir": ".cdad-execution"
}
```

`methodology_dir` retains the project’s actual value. Both directory values are normalized repository-relative paths; operational storage must remain disjoint from methodology. New-project default: `.cdad-execution`.

Recommend schema **2**, with exactly these three required fields: today’s parser rejects additional fields and unsupported versions (`cdad_layout.py:152–164`). An old declaration receives migration guidance, not silent conversion or fallback.

## Contract

### A. Versioned placement and local execution

**PC-1.** Layout resolution preserves methodology placement, while new operational records and new packet identities use the declared operational directory. The locator is versionable; the root operational store is ignored.

**Verification:** executable. Accept when adapted layout/lifecycle tests demonstrate declaration-driven access and tracking boundaries. Evidence: test output and reviewed ignore rules. Limit: no installation/publication claim.

### B. Manual upgrade without losing progress

**PC-2.** Encountering an unmigrated project produces brief actionable guidance before operational writes.

**PC-3.** Following the guide permits fresh preparation for unfinished work without loading historical packet/context identities. Historical evidence remains byte-identical; stage, postcondition outcomes, approvals and unfinished obligations are preserved, not falsely completed.

**Verification:** combined. Executable refusal/fresh-preparation checks plus independent contextual review of the manual handoff, suspended-unit procedure and outstanding-effect accounting. Accept only when both agree. Evidence: test output and review findings. Limit: operator coordination and truthful effect assessment are procedural, not runtime guarantees.

### C. Version-aware orchestration

**PC-4.** Startup instructions direct the orchestrator to read the canonical migration notice and prepare a new assignment after an observed methodology-version change, before dispatch.

**Verification:** combined: adapt version-check regression tests; contextually review instructions. Existing checking compares project `source_version` with installed `version.txt` markers and reports disagreement (`cdad-version-check.py:194–236`). It does **not** detect same-version edits or guarantee detecting a past change after every comparison leg has already advanced. Record observed versions through existing context notes; no new version-tracking subsystem.

## Invariants and acceptance

No aliases, content-based store selection, automatic migration, historical rewrites, fabricated approvals, automatic packet invalidation or session relocation. Existing cwd/explicit-root semantics remain.

Acceptance requires all four postconditions, integrated regression evidence, and independent review of migration sufficiency. Maximum **two correction rounds independently per draft/audit/result family**, provisional: consumers are coupled, but declaration and handoff changes are finite; remaining blockers require adjudication/replanning, not an expanded loop.

**Deferred-hardening:** historical replay, same-version edit detection and concurrent-upgrade synchronization—expressly outside this delivery.

# Draft migration guide content

Create one canonical `skills/cdad-cycle/references/layout-migration.md`.

### Physical migration

Coordinate running agents; retain their outputs and identify effects already performed. Do not require feature completion.

Preserve a byte-exact copy of mutable state before adjusting bindings:

```bash
# ROOT and METHOD identify the actual product root and methodology directory.
mkdir -p "$ROOT/cdad"
mv -n "$ROOT/.cdad/project-layout.json" "$ROOT/cdad/project-layout.json"
mv -n "$ROOT/.cdad" "$ROOT/.cdad-execution"
cp -n "$ROOT/$METHOD/.cdad-state.json" \
      "$ROOT/.cdad-execution/migration-state-before.json"
```

Check destinations beforehand; **stop on collisions**, never merge stores. Legacy projects without a locator manually create the schema-2 declaration using their actual methodology placement. Update the moved declaration and add `/.cdad-execution/` to root ignore rules. No methodology files move.

Reconcile declared temporary roots such as `.cdad/tmp` for future work, through an explicit policy decision—not historical snapshot edits.

### Smallest live-state handoff

**Proposed manual administrative exception requiring owner adoption with this spec:**

- Record the upgrade, prior bindings and unresolved deliveries/materializations in existing context/history.
- Clear only live `execution` and `active_packet` bindings; retain active feature, stage, outcomes, reviews and approvals.
- Prepare with `--new-execution`, appropriate existing role/substage and a new objective accounting for prior effects.

This is necessary: ordinary preparation can reuse historical contexts; pending packets block preparation. Clearing these live bindings lets `--new-execution` bypass prior selection, and preparation publishes fresh bindings before validation (`cdad_packet.py:3430–3479,6910–6937,7151–7166`). Fresh continuity begins under the new execution; do not reconcile/reanchor the historical chain as an upgrade shortcut.

Existing routes are **not universal migration substitutes**:

- `withdraw` applies only to never-dispatched prepared work (`7904–7916`).
- Replacement/recovery reads historical requests and contexts.
- Delivery/disposition registration resolves the old active context first (`8768–8774`).
- `open-unit` requires rest and starts discovery (`7411–7459`); do not use it to reset an open feature.

For a suspended unit, preserve its original registry entry. When selecting it for renewed work, manually restore its saved progress fields, remove that selected suspension entry, mark its feature in-progress, and clear restored packet/execution bindings before fresh preparation. Do not run historical `resume-unit`: its `resume_checks` verifies old paths/digests (`1095–1113`). Other suspensions remain untouched.

Outstanding old results/journals remain evidence. The fresh assignment explicitly verifies/reuses existing outputs and assesses partial effects before further action; it does not label them received or repeat effects merely because bindings changed.

# Ordered implementation plan

1. **Test-writer: baseline and audit.** Freeze the bounded selection below; map existing protections. Allocate at most two new cases: unmigrated refusal/no-write; manual active handoff followed by fresh preparation. Adapt existing cases—no hidden parameter expansion.

2. **RED, then implementer GREEN: declaration-driven storage.** Modify `cdad_layout.py`; packet/result/continuity/guard/dispatch/delegate/delegate_opencode/version-check siblings; `scripts/cdad-activate.py`, shell path guard, CI evidence default and suite canary paths; `.gitignore`. Consume project root/declaration; produce portable relative identities and correctly joined access paths. Preserve standalone eligibility. Run integrated regression immediately.

3. **Implementer: guide and instruction pointers.** Create the guide; modify `references/{bootstrap,project-start,orientation}.md`, `sources/roles/orchestrator.md`, relevant packet instructions/schema descriptions. Use the canonical generator for affected derivatives, never hand-edit them. Independent reviewer verifies PC-3/PC-4 and the administrative exception before approval.

Adapt existing `test_019_004_*.py`, `test_004_002_t2_bootstrap.py`, `test_007_007_suspend_resume_units.py`, `test_005_003_f2_idle_history.py`, continuity-relative-root, receipt/materialization and version-check modules.

Proposed baseline and repeated integrated regression:

```bash
python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py')

rg -n '\.cdad|OPERATIONAL_DIR|LOCATOR_RELPATH' \
  skills/cdad-cycle/scripts skills/cdad-cycle/assets scripts sources
```

Classify remaining literals as live paths, declaration references, filenames or history—not a zero-match gate. No tests or migration commands were executed.