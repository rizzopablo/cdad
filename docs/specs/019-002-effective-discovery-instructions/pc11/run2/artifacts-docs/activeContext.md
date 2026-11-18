# Active Context

Current state of the project. Each closed feature adds an entry. Most recent entries on top.

---

## 2026-11-15 — Project bootstrap

Memory Bank initialized from the CDAD templates. No feature is in progress; the first feature is queued (`queued` in `progress.md`).

Relevant decisions (owner):
- A note can carry several tags.
- Listing with several tags shows the notes that carry ANY of the given tags (OR), not only those carrying all of them.
- The plain `notes list` shows each note's tags next to it by default.

Defaults assumed by the orchestrator, NOT yet confirmed by the owner (to be confirmed before the spec is written; any one of them can be changed):
- Tags are written inline in the note text as `#tag`, e.g. `notes add "buy milk #errands #shop"`.
- Listing by tag: `notes list --tag <name>`. Plain `notes list` keeps showing all notes.
- Tag matching is case-insensitive.
- Existing notes (no tags) need no migration; they simply have no tags.
- Test runner: `unittest` (stdlib). Alternative: `pytest`.

Open questions for the owner (not decided):
- Confirm the tag syntax above (inline `#tag` vs a separate `--tag` flag on `add`, or both).
- Confirm the filter form (`--tag <name>`, repeatable for several tags, matching ANY).
- Spec approver: not named yet. The owner has said they will decide the spec approval.

Process blockers found on 2026-11-15 (checked with the CLI, nothing written):
- `prepare` refuses to start any execution: "no active feature in state". A feature must be opened first.
- The architect can only be enabled by an approved epic plan (`epic_history` entry with `stage: epic-plan` and an approver). A feature spec does not enable it. So the architect's discovery and draft need an epic plan that the owner approves.
- Policy: a write-free proposal exists (`prepare --propose-policy`: docs and tests roots, `.cdad/tmp` as temporary root). The owner has not accepted it, so `docs/cdad-policy.json` is not written.
- Confirm the test runner.
- Name the spec approver. Until then the state file has no approver and no spec can be approved.

Technical debt detected:
- No CI and no lint or type checker configured.
- No tests exist yet (`tests/` is empty).
- Note ids shift when a note is deleted (existing behaviour, `storage.py`).
- `notes/cli.py` must be run as `python -m notes.cli`.

Next feature in the queue: `001-note-tags` (tag notes and list notes by tag).

---

## Template for new entries (new ones go on top)

<!--
## <YYYY-MM-DD> — Feature: <short name>

Closed feature for <one-line description>.

Relevant decisions:
- <decision 1, with trade-off if applicable>

Technical debt detected:
- <item 1>

Next feature in the queue: <if you know it>.
-->
