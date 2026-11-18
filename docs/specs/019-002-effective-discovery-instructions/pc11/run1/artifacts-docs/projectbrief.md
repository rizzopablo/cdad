# Project Brief

## Project purpose

`notes-cli` is a tiny command-line tool to keep short text notes in a local JSON file. It lets a single user add, list and delete notes from a terminal.

## Technical stack

- **Language**: Python 3.13
- **Main framework**: none (standard library only)
- **Database**: none; notes are stored as a JSON list in the file named by `NOTES_FILE` (default `notes.json`)
- **Test tooling**: pytest 8.x (available locally; no tests exist yet)
- **Lint / type check**: none configured
- **CI**: pending (no CI configured; recorded as technical debt)

## Stakeholders and roles

- **Spec approver**: <TODO: owner name, to confirm in docs/activeContext.md>
- **Tech lead**: n/a
- **Others**: n/a

## Known constraints

- Single local user; no concurrency or locking in the storage layer.

## Overall scope

Covers: adding, listing and deleting notes from the command line.
Left out for now: search, editing, sync, a database, a GUI.

## External resources

- Repository README: `README.md`.

---

Last updated: 2026-11-15
