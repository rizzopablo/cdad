# System Patterns

Technical conventions of the project. Loaded at the start of agent sessions.

## Current decisions

The table starts empty. A row is added when a decision is approved.

| File | State | Summary | Roles | Reference |
|---|---|---|---|---|

## Layers and boundaries

- `notes/cli.py` — argument parsing and printing; calls `storage`.
- `notes/storage.py` — reads and writes the JSON file; the only module that touches disk.
- The CLI entry point is `python -m notes.cli <command>`.

## Code conventions

### Naming

- Functions and variables in `snake_case`.
- Commands are plain words (`add`, `rm`, `list`).

### File organization

- Package code under `notes/`; tests under `tests/`.

### Errors and exceptions

- Current behaviour: no typed exceptions; invalid input surfaces as Python exceptions.

## Storage format

- A JSON list of objects. Each note is `{"text": "<string>"}`.
- A note's id is its index in the list. Deleting a note shifts the ids of later notes down by one.

## Test conventions

- **Framework**: pytest
- **Structure**: `tests/` at the project root
- **Fixtures**: point `NOTES_FILE` at a temporary path per test
- **Property tests**: none

## Tooling enforcement

None configured yet.

## Project anti-patterns

- None documented yet.

---

Last updated: 2026-11-15
