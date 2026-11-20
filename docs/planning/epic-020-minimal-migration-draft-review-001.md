## Verdict

**Blocking findings remain.** This is draft-family review round 1/2; the findings continue the existing correction loop. This review is not approval.

### 1. Required — suspended-work handoff can overwrite another active unit and bypass changed-reference checks

**Verdict: BLOCKING · Bucket: h**

The draft instructs the operator to restore a selected suspended unit’s saved fields and remove its registry entry, but does not require the project to be at rest or explain which saved fields to replace (`epic-020-minimal-migration-draft.md:95`). The existing `resume-unit` refuses when another unit is active, replaces the complete set of unit-state fields, and verifies the recorded references and current authority before restoring (`cdad_packet.py:1091–1118`).

An operator following the draft while another feature is active could overwrite its live progress. The proposed bypass also omits a decision about changed policy, contract, or other pinned evidence: avoiding old-path replay is justified, but it does not establish that changes to those governing inputs are safe.

**Smallest correction:** Specify a rest/no-other-active-unit precondition; identify the saved fields and replacement procedure precisely; require the operator to inspect relevant recorded references and resolve changed governing inputs or revoked authority before preparing. Historical operational paths need not be rewritten or replayed. Missing genuine approval must still fail.

### 2. Required — outstanding effects are recorded, but not made a precondition for safe redispatch

**Verdict: BLOCKING · Bucket: m**

The handoff says to record unresolved deliveries/materializations, clear both bindings, and give the fresh assignment an objective accounting for prior effects (`draft.md:82–86, 97`). Current preparation normally blocks a published pending packet unless the prior dispatch has a verified durable receipt (`cdad_packet.py:6912–6934`); clearing the bindings deliberately removes that protection. A new objective that *asks* a worker to assess effects does not establish that assessment happened before the worker performs another effect.

**Consequence:** an unresolved partial delivery or materialization can be duplicated or incorrectly treated as complete.

**Smallest correction:** Require a documented, operator-verified disposition of outstanding effects **before authorizing any potentially overlapping effect**. If their state cannot be established, stop and escalate rather than treating a note or the new objective as resolution. Preserve old journals and evidence; do not require historical replay.

### 3. Required — configured operational stores are not covered by the migration’s ignore instruction

**Verdict: BLOCKING · Bucket: h**

The contract permits a declared `operational_dir` and promises that the operational store is ignored (`draft.md:21, 29`), but the guide only instructs adding `/.cdad-execution/` (`draft.md:74`). A project declaring a different directory would write operational records there without the promised ignore protection.

**Smallest correction:** Instruct operators to ignore the actual declared repository-relative operational directory, with `/.cdad-execution/` as the default example. No storage configuration framework is needed.

## Verification sufficiency and limits

- Clearing the execution binding does make `_open_unused_context` return no selection, and `--new-execution` skips `_find_prior_context` (`cdad_packet.py:3461–3479, 3331–3345`). This supports the proposed fresh-selection mechanism, **not** the safety of bypassing outstanding-effect and suspended-unit checks.
- The schema-2 direction is plausible, but the draft does not yet demonstrate executable behavior for all legacy/no-locator and standalone cases. The proposed adaptations and two-case ceiling are a plan, not evidence that the integrated regression will pass.
- The draft correctly limits the version-check claim to observed version-marker drift, not same-version edits (`draft.md:43–45`). Instruction-to-notice linkage remains to be verified in the produced change.
- No tests or migration commands were executed. No runtime success, installation, or publication is claimed.

## Abstentions

- I cannot establish from this draft alone that the proposed two new cases plus adapted existing tests will cover the integrated executable promises; that requires the baseline, audit, and subsequent test evidence.
- I did not perform a full repository audit or verify every consumer’s path conversion.