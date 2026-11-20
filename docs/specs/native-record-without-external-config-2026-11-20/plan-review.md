# Plan review — native record without external configuration

**Result:** One blocking finding. This is a review of the draft, not approval. No implementation or tests were changed or run.

## Required — Keep observation runtime-neutral

- **Verdict:** BLOCKING
- **Bucket:** m
- **Rationale:** PC-3 makes a configured `sessions_db` the condition for invoking observation. That is an OpenCode-specific store setting, not the runtime-neutral observation contract. Another runtime module may provide `--observe` without that key. Skipping it could miss a contradictory identity and stage native bytes with reduced assurance instead of rejecting them.
- **Provenance:** Draft `spec.md:28–38, 62–64`; existing contract `docs/specs/006-005-native-path-parity/spec.md:59, 93–96, 106, 205`; current delegation to the module in `skills/cdad-cycle/scripts/cdad_dispatch.py:1129–1137`.
- **Smallest correction:** Require the existing single bounded module observation whenever there is a motive, passing the available runtime section, including an empty one. Let the module report whether its observation surface is unavailable; OpenCode may report missing `sessions_db`. Preserve the existing no-motive rule and contradiction handling. Adapt the existing observation control to demonstrate that the entry does not gate another module’s observation on OpenCode’s key.

## Other assessed boundaries

The draft explicitly distinguishes absent configuration from invalid JSON and a present non-object runtime section, without requiring a broader schema redesign. Its identity and no-native-result rules preserve the relevant fail-closed distinction. The named existing tests are plausible adaptation candidates, but their eventual changes and defect sensitivity remain to be demonstrated; preserving node IDs alone is not evidence of preserved coverage.

## Abstentions

- I did not verify every current-decision table entry against `docs/adr/`; no conclusion on complete decision-table consistency.
- Test adaptation feasibility is assessed from the existing cases and draft only; no tests were executed. Model-family independence from the draft author is not established.
