# Plan review — 001-note-tags (draft review, stage 2)

Reviewer: cdad-reviewer (read-only, separate session from the architect). Object reviewed: `docs/specs/001-note-tags/spec.md`.

## History of rounds

- Round 1: `needs revision before owner approval` — 4 blocking, 3 major, 8 minor. Architect revised all of them.
- Round 2: `needs revision before owner approval` — 2 new blocking (flag rule for `tag`/`untag`; false invariant on text), 4 minor. Architect revised all of them.
- Round 3 (final, below): `ready for owner approval`, 0 blocking.

## Final verdict (round 3, FINAL TEXT of the reviewer)

### verdict

**Ready for owner approval.** Open BLOCKING findings: **0**. Two minor wording items remain. The owner decisions are the only open items that affect approval.

### findings

1. **[minor] Deferred-hardening bullet is out of step with the refused set.** Touches: deferred-hardening, "Whitespace and case beyond ASCII". The bullet says "Only ASCII space and tab are refused"; PC-10(a) also refuses `,`, `[`, `]` and a leading `--`. Suggested change: "Only the ASCII names in PC-10(a) are checked; other Unicode whitespace is not checked, and non-ASCII case folding is not verified." — **OPEN (optional, not applied in this round).**
2. **[minor] Invariant overstates what is verified.** The invariant says every name is "lowercase", verified by PC-8, PC-9, PC-10; non-ASCII case folding is deferred. Suggested change: "lowercase (ASCII letters; non-ASCII case folding is deferred)". — **OPEN (optional, not applied in this round).**

All blocking findings of rounds 1 and 2 are resolved in the current text: rm and tags travel with the note (PC-13); re-tag order (PC-7); case folding for every name argument (PC-9); `--tag` parsing and refused names (PC-2, PC-10, A1); no-tag output after untagging all (PC-11); message content (PC-10); unknown commands kept pending (A9).

### owner decisions still open

1. A2 — silent case folding (recommended: keep).
2. A3 — `untag` of an absent name is a silent success (recommended: keep).
3. A6 — `tag` and `untag` print nothing on success (owner's choice).
4. A8 — refuse names with a space or tab, `,`, `[`, `]` or a leading `--`, instead of normalising (owner confirms; differs from the activeContext default read as normalisation).
5. A9 — unknown commands and `--tag` used as a command: keep the fall-through at cli.py:10-12, or refuse.
6. Approver name — needed for `approved_by`.

### abstentions (reviewer)

- No decisions table to compare (`docs/adr/` does not exist; systemPatterns.md table empty).
- Code behaviour checked by reading only; the CLI and pytest were not run.

## Round 4 — after the owner left plain-list display open (reviewer FINAL TEXT, summarized)

Verdict: **needs revision** — 1 blocking.

1. **[major, BLOCKING] Plain `list` output on tagged notes is not pinned.** PC-7 is reserved and commits nothing, so an implementation that shows tags in plain `list` and one that does not both pass every postcondition. Closure: (preferred) the owner decides the Open decision and the architect writes PC-7 with that output; (alternative) the owner approves with plain `list` explicitly unchanged and A11 restated as a closed rule.
2. [minor, open] Deferred-hardening "Whitespace and case beyond ASCII" says only ASCII space and tab are refused; PC-10(a) also refuses `,`, `[`, `]` and a leading `--`.
3. [minor, open] Invariant "lowercase" overclaims: non-ASCII case folding is deferred.

Checks passed in round 4: no postcondition or acceptance criterion depends on plain `list` showing tags; all examples hold under both options; no dangling reference to promise D or the old PC-7.

## Round 5 — full independent draft review after the owner's decisions (summarized from the reviewer's FINAL TEXT)

Verdict: needs revision — 1 blocking (`list` with extra arguments unspecified). Architect applied it.

## Round 6 — after PC-10(e) was made reserved (summarized from the reviewer's FINAL TEXT)

Verdict: needs revision — 1 blocking (PC-10(e) read as a commitment while A12 is open). Architect made PC-10(e) reserved, pending A12.

## Round 7 — final check (summarized from the reviewer's FINAL TEXT)

Verdict: **ready for owner approval** — 0 blocking.

Open optional items (not applied):
1. PC-10 intro lists (e) among "invalid input" although (e) is reserved; it should sit outside the list.
2. The message rule names `id`, `name` or the missing argument, but `add --tag home` (no text) has no named missing argument; PC-10(c) should name `text`.

Open owner decisions: A12 (extra `list` arguments), A2, A3, A6, A8, A9, approver name.
