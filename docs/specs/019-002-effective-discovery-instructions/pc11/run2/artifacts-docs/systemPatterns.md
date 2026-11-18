# System Patterns

Technical conventions, patterns, and structural rules of the project. This file is loaded at the start of every agent session.

## Current decisions

The decisions that govern this project, one row per decision. This section is the
index of the project's ADRs: it says which ones are in force, and it is the only
place where that is written down.

The table starts **empty**: a project with no decisions yet has no rows. A row is
added when a decision is approved; the row of a replaced decision is kept and
marked obsolete.

| File | State | Summary | Roles | Reference |
|---|---|---|---|---|

- **File** — the path of the decision's file, relative to the project root (for
  example `docs/adr/ADR-NNN-<slug>.md`).
- **State** — `vigente` (in force) or `obsoleto` (replaced; the row is kept, with its
  replacement, so the history stays in the table).
- **Summary** — one line: what the decision decides.
- **Roles** — the roles that must consume the decision (the delegated roles and/or
  the orchestrator).
- **Reference** — where the rule that the decision materializes lives (it may point
  into the installed skill tree).

**Note.**

- The state of a row is declared by whoever maintains the table: it is written in
  the row itself, never re-derived from the ADR's own text.
- The rows that are excluded are the decisions that are not in force yet (the
  `Proposed` ones): they get a row when they are approved, and the list is updated
  then. The excluded ones are not listed here.

## Layers and boundaries

- `notes/cli.py` — command dispatch (`add`, `rm`, default list). Imports `storage`.
- `notes/storage.py` — persistence: load and save the JSON list, add, delete, enumerate. Knows nothing about the CLI.

## Code conventions

### Naming

- Functions and modules in `snake_case`.
- Note ids are list indices. Deleting a note shifts the ids of the notes after it (`storage.py`, `delete`). This is existing behaviour, not a bug to fix silently.

### File organization

- Package `notes/` at the project root; tests in `tests/`.

### Errors and exceptions

No error handling yet. A bad id in `rm` raises the Python exception as it is.

## Framework patterns

Not applicable: no framework.

## Test conventions

- **Framework**: pending (owner to choose `unittest` or `pytest`).
- **Structure**: `tests/` at the project root.
- **Fixtures**: pending. Note that storage reads `NOTES_FILE` at import time, so tests should set it before importing `notes.storage` or use a temporary path.
- **Property tests**: not planned.

## Tooling enforcement

None configured yet.

## Project anti-patterns

- Do not run `python notes/cli.py`: the relative import fails. Use `python -m notes.cli`.

---

Last updated: 2026-11-15
