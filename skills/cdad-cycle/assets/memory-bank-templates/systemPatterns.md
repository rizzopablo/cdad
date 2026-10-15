# System Patterns

Technical conventions, patterns, and structural rules of the project. This file is loaded at the start of every agent session.

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
