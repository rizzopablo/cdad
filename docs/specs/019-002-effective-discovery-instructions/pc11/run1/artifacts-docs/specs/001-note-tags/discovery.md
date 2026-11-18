# Discovery — 001-note-tags

## Architect report (materialized from the cdad-architect final text, section `## discovery`)

Examined revision `68ba7b3`, working tree (`docs/` untracked). Code and docs read only; the CLI and tests were not executed. Tags: **[verified]** = confirmed by reading file:line; **[assumption]** = reading to be confirmed by the owner or by tests.

**Units this feature touches**

- `notes/cli.py` `main(argv)` (lines 4-12): `add` branch (6-7), `rm` branch (8-9), and the `else` that lists notes (10-12). **[verified]**
- `notes/storage.py`: `PATH` read from `NOTES_FILE` at import (3); `load`/`save` (5-13); `add` (15-19) returns the new index; `delete` (21-24); `all_notes` (26-27). **[verified]**
- `notes/__init__.py` is empty; `python -m notes.cli` works through the `__main__` guard (cli.py:14-15). **[verified]**

**Conventions that apply**

- Standard library only; storage is the only module that touches disk (projectbrief.md:10; systemPatterns.md:15). **[verified]**
- `snake_case`; plain-word commands (systemPatterns.md:22-23). **[verified]**
- Tests: pytest, in `tests/`, `NOTES_FILE` pointed at a temp path per test (systemPatterns.md:38-43). **[verified]**

**Gotchas**

1. **No `list` branch.** Any unrecognised word, including `tag` and `untag` today, falls through to listing and exits 0 (cli.py:10-12). **[verified]**
2. **`add` swallows flags.** `add` joins every remaining argument into the text (cli.py:7). **[verified]**
3. **Manual argument parsing.** No argparse. `rm` calls `int(argv[1])` (cli.py:9). **[verified]**
4. **Negative ids.** `rm -1` reaches `del items[-1]` (storage.py:23) and deletes the last note. **[verified by reading; not executed]**
5. **Ids shift on delete.** Pre-existing (storage.py:23). Tags live inside the note object, so they move with it. **[verified]**
6. **Errors are tracebacks today** (systemPatterns.md:31). The refusal convention is new.
7. **Whole-file rewrite** (`open(PATH, "w")`, storage.py:11-13), not atomic. Pre-existing. **[verified]**
8. **`add` with no words** stores an empty text. Pre-existing, unchanged. **[verified by reading]**

**Doubts**

- Old `notes.json` entries have no `tags` key; reading them as untagged is an assumption. **[assumption]**
- Driving `python -m notes.cli` from a subprocess with `NOTES_FILE` set works as described. **[assumption, not executed]**
- Owner defaults: "lowercase" versus "invalid input is refused with no silent change". Read as: lowercasing is normalisation of valid input. **[assumption; owner]**
- Python version: 3.13.5 checked on this machine.

## Dialogue context

- Owner (2026-11-15): "A note can have several tags." — confirmed decision.
- Owner (2026-11-15): "I'll leave the other questions for later." — the remaining defaults are recorded as pending in `docs/activeContext.md` and in the spec's assumptions A2, A3, A6, A8, A9. Silence is not consent.
