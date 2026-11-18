# Project Brief

## Project purpose

`notes-cli` is a tiny command-line tool for keeping short text notes: add a note, list notes, remove a note. The owner is the only user for now.

## Technical stack

- **Language**: Python 3 (3.13 on the development machine); standard library only.
- **Main framework**: none.
- **Database**: none. Notes live in a JSON file (`notes.json` by default, or the path in the `NOTES_FILE` environment variable).
- **Test tooling**: pending (owner to choose between `unittest` and `pytest`). The `tests/` folder exists and is empty.
- **Lint / type check**: none configured.
- **CI**: none configured (recorded as debt, see `activeContext.md`).

## Stakeholders and roles

- **Spec approver**: pending. The owner has not yet said who approves specs (see `activeContext.md`).
- **Tech lead**: not applicable.
- **Others**: none.

## Known constraints

- Stdlib only, unless the owner decides otherwise.
- The CLI is run as a module (`python -m notes.cli ...`), because `notes/cli.py` uses a relative import.

## Overall scope

Covered: adding, listing and removing notes; tagging notes (a note can carry several tags); listing notes by tag.

Left out for now: editing note text, search by text, multi-user access, sync, and any UI beyond the terminal.

## External resources

None.

---

Last updated: 2026-11-15
