# Plan — operational-path separation

Approved by <owner> on 2026-11-19 together with `spec.md`.

## 0. Owner clarifications (2026-11-19, after the test audit)

- The declaration lives at the fixed path `cdad/project-layout.json` for every
  project; for a new project this is inside the methodology directory, and for
  a legacy project it holds only the declaration while state stays where it is.
- Automatic discovery of a custom methodology directory is explicitly not
  promised: the user identifies it or declares it in that file.
- "Not migrated" means: `.cdad/project-layout.json` exists, the declaration
  lacks `operational_dir`, or a populated `.cdad/` root remains.

## 1. Baseline and test audit (test-writer, read-only)

- Fix the candidate selection from the repository's actual test imports and
  the bounded searches below; do not impose a zero-literal gate.
- Measure the baseline of the integrated selection before any change.
- Map existing promises to the four postconditions; list which existing tests
  keep their meaning unchanged, which are adapted, and the exact files.
- Allocate at most two new cases: (a) unmigrated project refusal/no-write;
  (b) manual active handoff followed by fresh preparation. No parameter
  expansion to evade the ceiling.

```bash
python3 -m pytest -q $(rg -l \
  '\.cdad|test_004_002_t2_bootstrap|test_003_002_t1_receive|test_003_004_t1_checkpoint' \
  tests --glob 'test_*.py')

rg -n '\.cdad|OPERATIONAL_DIR|LOCATOR_RELPATH' \
  skills/cdad-cycle/scripts skills/cdad-cycle/assets scripts sources
```

## 2. Declaration and shared path (RED → GREEN)

- `cdad_layout.py`: schema 2 with `methodology_dir`, `operational_dir`; one
  shared repository-relative operational base; new-project default
  `.cdad-execution`; pre-write migration guidance for an unmigrated `.cdad/`
  and for an old declaration; never a store-content selector.
- Adapt consumers to derive from that base and the declared value: packet,
  result, continuity, guard, dispatch, delegate modules, activation and
  version check, shell path guard, CI evidence defaults and suite canary
  roots as actually required.
- `.gitignore`: root-anchored default operational entry.
- Preserve existing cwd/explicit-root semantics; do not move sessions.
- Run the integrated regression immediately after GREEN, not at the end.

## 3. Migration guide and instructions

- Create `skills/cdad-cycle/references/layout-migration.md` with the normative
  content fixed by the spec.
- Point startup/orchestration instructions at it; regenerate affected
  derivatives canonically instead of hand-editing generated files.

## 4. Review and closure

- Independent review of the actual diff, the declared/ignored boundary, the
  migration procedure and the two new cases.
- Full closure evidence per the test evidence policy; record any omission as
  debt, never as green.
- Memory Bank update drafts, owner approval, orchestrator commit.

## Risks kept explicit

- Coupled consumers: the declaration change touches every writer of
  operational paths, so the integrated regression runs before further work.
- Version detection covers published version markers, not same-version edits.
- Historical packages are evidence, not replay surface.

## Execution note (2026-11-19)

`prepare` cannot bootstrap the v2 execution: the state has no active feature or
epic, and the CLI refuses with `no active feature in state`. This feature is
therefore run through the documented legacy handoff route, with the owner's
direct approval recorded in `spec.md`; no delegated authority is claimed and no
state is edited by hand. A baseline of the affected test selection was measured
before any change.

