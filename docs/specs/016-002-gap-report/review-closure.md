## Closing review of 016-002: verdict

All six findings (B1, B3, B4, N2, N3, N4) are closed. The fix (`00319407`) opened no blocking issue. I edited nothing.

**Packet check (route C):** the identification block matches the canonical render. `validate-request` and `validate-packet` both give rc=0, `PACKET.md` is byte-identical to `render` (`cmp` SAME), and the spec's sha256 matches (`315fad2c…`).

### What I checked

1. **B1 is closed.** The fix counts exclusions by unit and promise before applying any (`cdad_contract_links.py:1655-1689`). When a pair appears more than once, every entry becomes a `bad_exclusion` and none is applied. The count ignores `reason`, so two entries with different reasons for the same unit and promise also block, and the gap stays in `gaps`. I confirmed the different-reasons case by reading the code, not by running it. The test checks identical duplicates: rc 1, PC-2 still in `gaps`, not in `excluded` (`tests/test_016_002_gap_report.py:464-489`).
2. **B4 is closed.** Rows not marked `done` now go to `out_of_universe` with their `unit`, `status` and `reason` (`:1007-1018`), and they never enter the universe. The `in-progress` case is checked in the test (`:281-290`).
3. **B3 is closed.** The reference (`contract-test-links.md`) now says the orchestrator materializes both the exclusions and the optional snapshot. It does not repeat the format, and it says GREEN does not write the exclusions file.
4. **N2, N3 and N4 are closed:**
   - N2: `_gap_display` shows paths relative to the project root, or `<fuera del proyecto>` for paths outside it.
   - N3: equivalent bindings now keep the smaller path in lexicographic order, so reordering them doesn't change the result.
   - N4: duplicated current rows are deduplicated when equivalent and reported as `ambiguous_closure` when they conflict.
   - `scope.current_rows` now counts the input rows (`len(current_lists)`), which is consistent.
5. **The RED-003 assertions really fail without the fix.** I ran the current test file against the commit just before the fix (`00319407~1`) in a temporary worktree. `R_A` failed on `'unit-c' not found in '[]'`, and the `R_C` duplicate-exclusion case failed too. With the fix, `tests/test_016_002_gap_report.py` gives 5 passed and `pytest -k 016` gives 16 passed.

### New findings

- **Nit (OPTIONAL, bucket m):** at `:956-976`, conflicting current rows are left out of `current`. If the same unit also has history rows, the loop at `:978` can then pick the history row. The result is still 1, because the unit is in `invalid_units`, but the report may show a history row the contract did not choose. A possible fix is to skip history for units with conflicting current rows. No test covers this case. The consequence is a misleading report for the user, not a hidden pass, so it doesn't block.
- **FYI:** the two-pass exclusion check (count first, then apply) is fine and simple.

### Evidence

**Commands run:** `cdad_packet.py validate-request|validate-packet|render [--route C]`, `git show 00319407 c69e25c5`, `pytest -q tests/test_016_002_gap_report.py`, `pytest -q tests/ -k 016`, plus the temporary worktree at `00319407~1` (removed afterwards).

**Modified files:** none. The only uncommitted change in the repo is `docs/.cdad-state.json`, which was already there and is not mine.

**Commit reviewed:** `00319407`, with tests at `c69e25c5`.

## Abstentions

- I did not run the full suite or `cdad-suite.py validate`, because the policy for this point in the cycle doesn't call for them. I took the reported `ok` for the materialized registry without checking it.
- I did not run the different-reasons duplicate case; that result comes from reading the code.
