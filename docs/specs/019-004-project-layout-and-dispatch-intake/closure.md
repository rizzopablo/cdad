# Closure — 019-004 project layout and dispatch intake

Approved by the CDAD orchestrator under <owner>'s renewed HITL delegation for epic
019, on his explicit instruction to keep improving the epic.

## Accepted contract

`spec.md` (sha256 `8ad2d594…b0b839`) governs Promises A–E and PC-01–PC-16, with
amendment 001 replacing the §4.2 evidence list. Three decisions refine behaviour
without changing a promise: repository-root placement unsupported, continuity and
guard stores are operational rather than initialization evidence, and a candidate
identification is any JSON object carrying `packet_id` or `execution_id` in any
delivery form.

## Evidence per promise

- **A — existing projects unchanged, new projects default to `cdad/`.** Covered by
  `tests/test_019_004_layout.py` (7 tests) and by the closed enumeration tests:
  registered locator wins, either exact legacy marker selects `docs/`, insufficient
  evidence is ambiguous, ordinary documentation is not a marker, invalid metadata is
  rejected without fallback or writes, empty named directories are not evidence.
- **B — the selected layout governs the lifecycle without weakening protection.**
  `tests/test_019_004_lifecycle_layout.py` (19 tests) and
  `tests/test_019_004_continuity_gap_ambiguity.py`, `_receipt_reanchor_ambiguity.py`,
  `_ambiguity_enumeration.py`: state and policy access, materialization destinations,
  conventional contract lookup, execution-bound continuation, policy-classification
  preflight and locator protection. Two independent review rounds found real defects
  (parent-only classification, silent `docs/` selection, empty directory evidence,
  over-broad candidate keys); each was corrected with RED first.
- **C — the coordinator directory does not redirect declarations.**
  `tests/test_019_004_layout.py` and the intake tests exercise equivalent roots from
  the root, its parent and unrelated directories with arbitrary repository names.
- **D — one command validates the supplied received A/C dispatch.**
  `tests/test_019_004_received_intake.py` (21 tests): Route A complete-body equality
  including CRLF and appended text, Route C identification comparison with inert
  wrappers, candidate and partial-candidate rejection in any delivery form, heading,
  delimiter and verbatim-body fragment rejection, mixed and malformed input, v1
  context, the distinct legacy-consultation diagnostic, explicit input failures and
  unchanged trees. Four review rounds; each finding reproduced first.
- **E — installed consumers can use it without rediscovery.** Instructions aligned in
  `sources/roles/architect.md`, `skills/cdad-cycle/references/bootstrap.md`,
  `handoff-prompts.md`, `sub-agent-strategies.md`, `project-start.md` and `SKILL.md`,
  with 20 generated agents rebuilt by the generator. `tests/test_019_004_installed_intake.py`
  installs into an isolated HOME, exercises `layout` and `intake` as a consumer, and
  leaves both the project tree and the real HOME unchanged. Independent contextual
  review found three instruction defects (unresolvable skill directory, missing manual
  alternative, ambiguous bootstrap question); all three were corrected and the closing
  review accepted the wording.

## Complete suite

Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider -q tests`
Started at revision `3a9d3b30`, completed at `64ff624d` with no product or test change
in between: **2195 passed, 5 skipped, 0 failed**, exit 0, 5063 seconds.
Evidence: `.cdad/orchestration/epic-019/final-suite-019-004/`.

Earlier runs in this feature are distinct and are not folded into this result: the
T2-era parallel batch was discarded by its own canary, and intermediate serial runs
were interrupted by method changes. Inventory integrity was checked after every test
addition; `python3 scripts/cdad-suite.py validate` returned 0 at closure.

## Limits and dispositions

- **Deployment is not performed.** The installed HOME copy predates this feature, so
  `intake` and `layout` are not available there until the owner authorizes a deploy.
  The isolated-HOME test proves the installed consumer path, not the deployed one.
- **Fresh-role journey after relocation is not demonstrated**, because it depends on
  that deployment. The resolution procedure itself was verified mechanically against
  the manifest for the three runtime prefixes.
- **Historical Route C provenance is missing.** No legitimate historical received
  representation was recovered; the grammar is exercised with synthetic wrappers and
  reported as such.
- **Native capture is unverified.** The command validates the supplied representation
  and cannot prove its origin; role instructions require the manual procedure and
  forbid claiming automated validation when capture is unavailable.
- **Arbitrary paraphrase is not detectable.** Verbatim packet lines of 24 characters
  or more, headings and delimiters are rejected; a reworded fragment is not claimed to
  be detected. This is a declared boundary, not a silent gap.
- **Installation drift (F011)** predates this feature and remains red because the HOME
  copies differ from the checkout; it is not reported as green.
- **ADR index reconciliation** from the draft review stays optional and out of scope.

No deferred item postpones a committed postcondition. The epic remains open for
019-005.
