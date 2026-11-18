Both follow-up fixes are committed in the `cdad/` submodule. The four blocking findings of 019-001 are fixed, and the advisory refinements are in as well.

**Commits (`cdad/`, branch main)**
- `42b9af4e` fix: the four blocking findings of the operating design (the commit from the earlier round).
- `844a5d88` fix: epic-level delegation, bounded recording delta, B-25 readiness effect, B-26 cleanup.
- `b984222f` fix: restores the admissible `VERIFY` in B-26, places the epic-scope rule in its canonical owner, and removes stale "permission delta" wording.

**Files changed in this round (all under `docs/specs/019-001-discovery-dialogue-contract/operating-design/`)**
- `examples.md`: B-25 states the R1 effect both ways. B-26 has an admissible case with a visible `VERIFY` for a detail the promise does not depend on, and an inadmissible case with the baseline `VERIFY` and no verifiable commitment.
- `roles-and-dialogue.md`: §1 point 2 adds the epic-level clause (an explicit request naming the epic's specifications covers each of its features, and nothing wider). The sentence "it widens nothing" is added. §3 is reworded to "three deltas, nothing else", and the `Current:` cite is `:128-131`.
- `activation-map.md`: R1 names `stage-2-specification.md` §2.3 as the canonical owner of the approval-exception text. The recording allowance is described as not a new power, citing `orchestrator.md:302`.
- `activation-handoff-019-002.md`: item 5 lists the epic-scope rule as a correction and adds a regression check for it.

**Checks run**
- Grep for stale wording ("three explicit permission", "permission deltas", "stated once, in roles-and-dialogue", "states the approval exception once"): no hits.
- Code-fence balance on every product file: all balanced.
- Finding 4's closure criterion, re-read against B-25 and B-26: each example has its authority, its readiness effect and its unacceptable result, and B-26 shows an admissible `VERIFY`.
- Commit staging: only the four operating-design files in each commit. `docs/.cdad-state.json` (modified before this task) and `docs/epics/epic-019-discovery-dialogue/fix1-begin.json` (untracked) are not committed.

**Not run**
- No test suite. The unit is documentary, and `execution.md:16-28` makes the independent semantic review the verification.
- The Route C validation (`render`, `validate-request`, `validate-packet`, `validate-state`, all rc=0, render byte-identical to PACKET.md) was done at the start of the first round. I did not repeat it in this round.

**Decisions to check**
- I placed the canonical text of the epic-scope rule in `stage-2-specification.md` §2.3, not in the design document. The design now proposes changing that canonical reference. Nothing is activated; item 5 of the handoff carries the change to 019-002.
- The outer repo still shows `M cdad` (gitlink). I did not bump it, because that is outside my write scope.