# Recovery direction — owner-approved baseline

The owner selected the closure of 019-003, `bc922c04`, as the recovery baseline.
Restore the affected product surfaces to that revision before reimplementation.
Do not reset repository history, erase historical records, deploy, or change
model configuration. Restoration and reimplementation are separate assignments.

## Preserved evidence

- Original current revision: `6d32000b2424b982c4480253aaf413d04c2cb88f`.
- Verified complete Git bundle:
  `.cdad/orchestration/epic-019/recovery-backup/pre-restore.bundle`.
- Working-tree patch and status: in the same backup directory.
- Full and product-focused diffs:
  `.cdad/orchestration/epic-019/commit-boundary-audit/02-key-to-current.*.patch`.
- Independent retrospective report:
  `.cdad/inbox/019-002-scope-reassessment-role-report.md`.

## Lessons for reimplementation

Retain the baseline's verification-method routing. Subsequent work identified
potentially useful consultation delivery and resting-state corrections, but
these are not automatically retained or accepted: record them as candidates for
separate, explicit reapplication.

Do not repeat the blanket investigation prohibition, universal verbatim
presentation requirement, one-decision-per-question rule, or readiness check
before the very consultation needed to establish readiness. Do not turn
nonrepresentative failed exercises into general restrictions without establishing
cause. Keep failed observations and their limitations.

The orchestrator must not write or correct product or tests. Preserve its
practical autonomy, including trivial formal corrections to role deliverables.
Do not redesign owner authority or add gates absent a demonstrated need.
Installed methodology in use is distinct from the product under development.

Directory migration, deployment, and model changes are outside this recovery.

## Remaining work

Prepare an isolated restoration assignment covering the cumulative affected
product surfaces and corresponding test baseline, without rolling historical
state back. Verify exact content equality against `bc922c04`, then independently
check scope before commissioning any reimplementation. Retire obsolete pending
assignments and reconcile operational state without erasing their receipts.
