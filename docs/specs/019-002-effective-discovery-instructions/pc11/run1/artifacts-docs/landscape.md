# Landscape — notes-cli (discovery for 001-note-tags)

Revision examined: `68ba7b3`, working tree. Verified by reading the files; the CLI and tests were not executed.

## Code units the feature touches

- `notes/cli.py` `main(argv)` (lines 4-12): `add` branch (6-7), `rm` branch (8-9), default listing (10-12). Verified.
- `notes/storage.py`: `PATH` from `NOTES_FILE` at import (3); `load`/`save` (5-13); `add` (15-19) returns the new index; `delete` (21-24); `all_notes` (26-27). Verified.
- `notes/__init__.py` is empty; `python -m notes.cli` runs through the `__main__` guard (cli.py:14-15). Verified.

## Conventions that apply

- Standard library only; storage is the only module that touches disk.
- `snake_case`; plain-word commands.
- Tests: pytest in `tests/`, `NOTES_FILE` pointed at a temp path per test.

## Gotchas

1. No `list` branch: any unknown word, including `tag` and `untag` today, falls through to listing and exits 0 (cli.py:10-12). Tests must assert output or file effect.
2. `add` joins every remaining argument into the text (cli.py:7), so `--tag` must be extracted first.
3. Manual argument parsing; `rm` calls `int(argv[1])` (cli.py:9).
4. `rm -1` deletes the last note (storage.py:23). `tag`/`untag` must refuse negative ids.
5. Ids shift on delete (storage.py:23). Pre-existing; tags live inside the note object and move with it.
6. Errors are tracebacks today (systemPatterns.md:31). The refusal convention in the spec is new.
7. Whole-file rewrite, not atomic (storage.py:11-13). Pre-existing; refusals must happen before any write.
8. `add` with no words stores an empty text. Pre-existing, unchanged.

## Doubts (assumptions until confirmed)

- Old `notes.json` entries without a `tags` key read as untagged.
- Driving `python -m notes.cli` from a subprocess with `NOTES_FILE` set works as described.
- Python version on this machine: 3.13.5 (checked).
