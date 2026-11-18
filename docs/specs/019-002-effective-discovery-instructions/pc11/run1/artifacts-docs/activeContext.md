# Active Context

Current state of the project. Most recent entries on top.

---

## 2026-11-15 — Feature 001-note-tags: draft ready for owner decision

Stage: Specification. `docs/specs/001-note-tags/spec.md` is `Status: Pending approval`. The owner has not approved it; approval is the owner's decision.

Owner decisions (confirmed):
- A note can carry several tags.
- Plain `list` shows each tagged note's tags next to its text (PC-7).
- `list --tag <name>` can be repeated; it shows notes that carry at least one of the names (ANY, A10).

Defaults in the spec, recommended by the orchestrator and NOT confirmed by the owner (each stays pending until the owner decides):
- A2 — `Home` is folded silently to `home` for every name argument (recommended: keep).
- A3 — `untag` of a name the note does not carry is a silent success (recommended: keep).
- A6 — `tag` and `untag` print nothing on success (recommended: keep).
- A8 — names with a space or tab, `,`, `[`, `]` or a leading `--` are refused, not normalised. This differs from the earlier default ("no spaces" read as normalisation).
- A9 — unknown commands and `--tag` used as a command: keep today's fall-through to `list` at cli.py:10-12, or refuse them (recommended: keep and decide later).
- A12 — arguments to `list` other than `--tag <name>` pairs (for example `list home`, or `list --tag home errands`). Today `list <anything>` lists everything with exit 0, so a misplaced second `--tag` silently shows every note. The spec reserves this (PC-10(e)) and commits nothing until the owner decides.
- Approver name (state field `approver` and the spec's `approved_by` are pending).

Verified facts (run on a scratch notes file, not on user data):
- Note numbers shift down after `rm` (`rm 0` makes the old note 1 become 0). Pinned by PC-13; a limit (ids shift) stays in deferred-hardening.
- An old-format notes file (`{"text": ...}`) lists correctly and is not modified by `list`. The first `add`, `rm` or `tag` rewrites the whole file in JSON format.

Technical debt detected:
- No tests exist yet.
- No CI configured.
- Note ids shift on delete (existing behaviour; not changed by this feature).

## 2026-11-15 — Project bootstrap

Memory Bank initialized (`docs/`). Test runner: pytest. CI: pending.
