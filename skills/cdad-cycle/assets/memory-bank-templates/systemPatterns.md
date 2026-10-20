# System Patterns

Technical conventions, patterns, and structural rules of the project. This file is loaded at the start of every agent session.

## Current decisions

The decisions that govern this project, one row per decision. This section is the
index of the project's ADRs: it says which ones are in force, and it is the only
place where that is written down.

| File | State | Summary | Roles | Reference |
|---|---|---|---|---|
| `docs/adr/ADR-NNN-<slug>.md` | `vigente` | one line: what the decision decides | `architect`, `reviewer` | `skills/cdad-cycle/references/<file>.md` |

- **File** — the path of the decision's file, relative to the project root.
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

<TODO: describe the project's architectural layers and what imports what. Example:

- `domain/` — pure business logic, does not import from adapters/ or framework/
- `adapters/` — integrations with external systems
- `framework/` — framework wiring, imports from domain and adapters
- `presentation/` — controllers/views, imports from framework
>

## Code conventions

### Naming

<TODO>

### File organization

<TODO>

### Errors and exceptions

<TODO: typed exceptions? result types? what gets logged?>

## Framework patterns

<TODO: how the main framework's extension mechanism is used — inheritance, hooks, signals, plugins. Which patterns are preferred and which are avoided.>

## Test conventions

- **Framework**: <TODO>
- **Structure**: <TODO: unit tests in X, integration in Y, E2E in Z>
- **Fixtures**: <TODO: how they are built, which pattern is used>
- **Property tests**: <TODO if applicable: library used, where they go>

## Tooling enforcement

<TODO: linters, type checkers, import-linter, pre-commit hooks. What runs in CI.>

## Project anti-patterns

<TODO: things this project historically avoids for good reasons. Document the reason.>

---

Last updated: <YYYY-MM-DD>
