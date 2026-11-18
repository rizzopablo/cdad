# Closure — 019-007-suite-selector-maintenance

Approved by the CDAD orchestrator under Pablo's renewed HITL delegation for epic 019.
The unit repaired the verification instrument that blocked the epic's closure gate.

## Accepted contract

`spec.md` (sha256 `3ba4f69f…d14` after the approval mark) with four postconditions
under two promises, and `plan.md` (sha256 `d2e54daf…6c`) with a single task. Draft
review `plan-review.md` found no blockers within the examined aspects (draft family
round 1/2); the ceiling of two rounds per family was adopted as proposed.

## What changed

Commit `b08d1ad8`, confined to the three declared test files (+257/−22):

- Both `find_deployed` helpers now read `.cdad-install-manifest.json`, keep only the
  destinations whose `source` equals the staged origin exactly, require exactly one
  destination (or a declared runtime prefix when the origin is deployed to several
  runtimes) and check that the file exists. No basename fallback remains.
- Every caller passes its staged origin; the path-guard consumer in
  `tests/test_004_001_t6.py` was adapted.
- No product, installer, agent or policy file was touched.

## Evidence per postcondition

- **PC-1 — selection by exact registered source.** Each helper resolves by `source`
  and checks existence; the new `TestDeployedSelectorUsesRegisteredSource` (3 tests in
  each module) uses synthetic roots with two homonymous files of different bytes and
  asserts the runtime-specific file.
- **PC-2 — explicit failure, never a silent alternative.** The new tests cover a
  missing manifest, an unregistered origin, a missing file and an ambiguous selection;
  all fail with an explicit assertion, and the old basename selector was shown to fail
  them.
- **PC-3 — preserved assertions.** `test_t5_case8_install_deploys_staging_bytes_without_sources`
  keeps the staging mutation, the hash update, the inaccessible `sources/`, the
  successful install and the exact byte comparison; the independent review confirmed
  no other assertion was altered.
- **PC-4 — tests-only diff.** The commit names exactly the three test files, and the
  independent review confirmed the absence of product changes.

## Verification

- Test-writer: class `TestT5StagingIsSourceOfTruth` **4 passed** (42.55 s); three
  modules **32 passed** (299.28 s), rc 0.
- Sensitivity: with the previous `rglob`-and-take-first selector, the new tests fail
  (3 failures, in the homonym and unresolved-selection cases).
- Independent review (result family round 1/2): **no blocking findings**; focused
  verification of the six new tests **6 passed**. The reviewer declared its
  abstentions: it did not rerun the longer checks, did not reproduce the mutant, and
  did not perform automated intake.
- Complete suite: **exit 0 — 2201 passed, 5 skipped, 0 failed in 5215.49 s** on
  `56e667ee`, repository root, no concurrent work
  (`.cdad/orchestration/epic-019/final-suite-epic-6/`). This run feeds the epic
  closure gate.

## Rounds and residue

Draft family 1/2 and result family 1/2, both without corrections. No optional residue
was admitted and no accumulation unit is required for this unit.

## Limits

- The original suite failure depended on filesystem enumeration order and was not
  reproduced by the role before the change; the synthetic homonym fixture exercises
  the ambiguity directly instead.
- The mutant run was reported by the test-writer and not independently reproduced by
  the reviewer.
- Native capture of a received dispatch remains unverified in this runtime; the roles
  declared manual route C validation instead of claiming automated intake.
- A passing suite and an independent review do not prove the universal absence of
  regressions.
