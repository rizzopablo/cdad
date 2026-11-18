# T3 progress — observed acceptance remains open

The reviewed candidate includes the T1/T2 product and review fixes through
`db42e2e5`. Independent focused review `review-005.md` found the last reviewed
handoff issue resolved, but did not accredit the feature.

The real-agent route PC-4 and observed journey PC-11 have not been run. A
read-only OpenCode runtime probe of the configured orchestrator returned HTTP
429, provider weekly usage limit; it did not execute the scenario. Its session
and raw evidence are `.cdad/orchestration/epic-019/t3-runtime-probe.jsonl`;
`.cdad/orchestration/epic-019/t3-preflight-evidence.json` records candidate
file digests and notes that effective candidate activation is not demonstrated.
The installed and project-derived agents are not assumed to be the candidate.
No alternate model was selected: configured models remain user-owned.

## Newly detected process defects — unresolved

- The materialized `spec.md` and `plan.md` still say `UNAPPROVED DRAFT`, even
  though the orchestrator registered a specification gate at transition
  `6ed1e2ef60fe84754156a0a81506f8e170f8cf130b72364ad2acbc94a75f5573`.
  The prior gate identified delegated approval in `approved_by`, but omitted
  the separate provenance fields required by the installed stage-2 instructions.
  Recovery was independently reviewed and explicitly reapproved: the new gate
  `95739fe789ff1600747f63ff903c83ea8eab8de211f33ffba08f09503ff66c18` pins the
  corrected status labels with `delegated: true` and `requested_by: Pablo`,
  without an exemption. `approval-recovery-decision.md` and
  `approval-recovery-review.md` preserve the rationale and limits.
- The T1 implementer packet `...implementer-green-001/REQUEST.json` declares
  only implementation roots and `install.sh` in its `write_scope`, but commit
  `3322aaf3` also changed `README.md` and `CDAD_metodologia.md`, which are
  classified as documentation. The packet objective named the planned work,
  but that does not extend its declared write scope. Under the role contract,
  that out-of-scope result must be invalidated and redone under a properly
  scoped assignment; do not accept it retroactively. The review-001 scope check
  did not identify this discrepancy. A fresh exact-scope implementer restored
  the baseline and re-performed the change in commits `baf2874f` and
  `b38e3c26`; independent review identified and corrected a separate glossary contradiction;
  `review-007.md` confirms the scoped redo and corrected guidance within its
  stated limits.

Before acceptance, establish a candidate-only runtime without changing the
installed methodology, declare and protect scenario inputs, run J1–J7 and all
C1–C5 and the PC-4 routes, record actual sessions, packets and effective hashes,
and obtain an independent assessment. PC-6 frozen publications and affected
in-flight packets still need explicit evidence. Do not treat this diagnostic,
structural tests or a future declared limitation as observed use.

Installation check investigation: `install.sh --check` currently compares the
in-progress candidate with an older installation, so genuine candidate drift is
expected and is not evidence the installed version should be overwritten.
Separately, `count_tree_files` in `install.sh` uses `find "$dir" -type f` on
symlinked skill directories; for those paths this reports zero although `find
-L` reports the actual files. This explains the false zero-count diagnostics,
but does not establish that every other difference is benign. No local deployment
of 019-002 was authorized or performed.

## Native consultation delivery blocked

The native architect consultation for approval recovery was actually dispatched
and returned in session `<session>`. The installed
`cdad_dispatch.py record` rejected `architect/brainstorm` because the installed
role/substage table derives two draft kinds instead of the required single
`role-report`. No receipt or delivery transition exists. The continuity
reconciler reports `not-started` only because the native transport returned
before a dispatch could be recorded; that signal does not erase the observed
real session. Do not dispatch again, withdraw as never dispatched, or treat the
consultation as received. Recover through the authorized protocol without
changing the installed methodology or fabricating a receipt.

### Delivery recovery

The native result was subsequently recorded once, without repeating transport,
using the repository candidate `cdad_dispatch.py record` and candidate
`cdad_result.py receive`. The dispatch script and continuity script were
byte-identical to the installed copies; the candidate result module supplies
the already-reviewed PC-5 role-report mapping that the installed one lacks.
The same frozen packet and original native final text were used. The receipt
was validated and the delivery transition recorded; no installation changed.
This is a narrowly scoped recovery, not evidence of the PC-11 journey.

## Remaining execution constraints

The configured OpenCode orchestrator model returned a provider quota error
(`t3-runtime-probe.jsonl`). Its use is user-owned configuration; the probe did
not demonstrate the candidate agents or a protected scenario. The earlier
full-root pytest attempt stopped in collection because the separate Odoo example
requires the unavailable `odoo` Python module; that failure is preserved in
`.cdad/orchestration/epic-019/019-epic-complete-suite.log`. A separate run of
the project's `tests/` suite was started and its outcome must be read from the
result log, not inferred from this note.

## Interrupted epic suite and regressions

The separate `tests/` run was interrupted before completion and must not be
reported as green. Its preserved log
`.cdad/orchestration/epic-019/019-epic-tests-suite.log` reports 915 passed,
4 skipped and 5 failures before interruption. The failures concern existing
intake/readme protections: `test_005_006_t2_intake.py` (one failure),
`test_005_006_t4_readme.py` (two), and `test_005_006_t6_owner_reviewfix.py`
(two). Their applicability and baseline need independent test-writer audit;
route actual regressions to an appropriately scoped implementer, then rerun
the full epic suite. No exemption from epic-suite evidence has been granted.

### PD-10 regression

The PD-10 intake failure was corrected in `deda7786` by marking the
`re-entry.md` reference with `<skill-dir>` and regenerating affected agents.
`test_pd10_intake_wiring_u<session>_cli` and the eight declared
regressions passed. The four README failures remain a separate pre-existing
debt from `3b62d552`, not from 019-002; they are tracked in
`regression-audit.md`.

## Remaining work and honest limits

- `make validate` still reports `F011: scripts/validate-subagents.sh`, because
  `install.sh --check` compares this candidate with installed skills that are
  still symlinks to the older installed methodology. It is an installation-state
  mismatch, not evidence about the candidate product. No local deployment of
  019-002 was authorized or performed.
- The configured OpenCode orchestrator model returned a provider quota error
  (`t3-runtime-probe.jsonl`). No model was changed; configured models remain
  user-owned.
- PC-4, PC-11 and PC-6 frozen-publication evidence remain unobserved. The
  approval-recovery work corrects provenance, not observed use.
- The full `tests/` suite was interrupted and cannot be reported as green.
  The interrupted run's log and the final `test_pd10` result are preserved.
  Any future closure must either complete the full suite or record a dispensation
  expressly granted by the owner for that closure.

## Epic-level closure status

The 019-003 candidate was deployed locally under an explicit owner request
after its own closure. That deployment is unrelated to 019-002 acceptance and
does not certify it.

This feature's product-level work is preserved in the repository. Its acceptance
is not complete under the approved contract: PC-4, PC-6 and PC-11 require
observed evidence and the full epic suite still needs completion or an express
owner dispensation. The approval-provenance defect was recovered through
independently reviewed administrative correction. The out-of-scope T1 README
changes were invalidated and redone under an exact-scope packet, with the final
review accepted. The PD-10 intake regression was fixed and verified.

This document is a progress record, not closure. It does not close 019-002 or
epic 019.

## PC-11 run1 (2026-11-15) — FAILED observation, preserved

Run through a project-local candidate scratch (`.opencode/agents`, `.opencode/skills`), no
installation. Independent evaluation: `pc11-run1-review-009.md` (all of C1–C5 not met;
J3/J4/J5 failed; PC-4 only the reviewed route observed). Findings F1–F11 drive a
review-fix on the candidate instructions, then a new execution (run2) through the packet
route. run1 stays failed; it is never overwritten.
