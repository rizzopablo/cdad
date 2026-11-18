# Owner direction — reassess scope before further changes

The owner requested a retrospective review of the changes, not another
implementation iteration. This direction supersedes proceeding with the prepared
architect draft-007 assignment. No restoration, product edit, test edit or
deployment is authorized by this review assignment.

## Owner corrections

- The orchestrator was working well. The intended necessary change was the
  verification/review process for features whose properties cannot be tested
  deterministically. Investigate how the work expanded beyond that objective.
- Express the minimum necessary prohibitions, principally that the orchestrator
  must not write or correct the product or tests. Do not replace these with a
  catalogue of allowed activities.
- Trivial formal corrections to role deliverables have worked without problems;
  do not introduce a blanket prohibition. Distinguish presentation corrections
  from changes to substance, evidence or conclusions.
- Do not redesign owner-decision handling merely as an improvement. Determine
  whether a demonstrated defect belongs to the requested change, an older
  behavior, or an artificial acceptance scenario.
- Restrictions on the product under development are not restrictions on reading
  or using the installed methodology, even when the product is its next version.
- Consider separating CDAD work records into `cdad/` and user/external-agent
  documentation into `docs/`. This is a separate proposal, not authority to
  migrate directories during this review.
- Review everything done in the relevant initiative. If warranted, propose
  restoring the earlier orchestrator and reapplying only the necessary change.
  Present evidence and a proposal before any product modification.

## Required diagnostic

Trace the original request and its recorded evolution; distinguish actual owner
approvals from assumptions made during execution. Identify the pre-change
orchestrator baseline and examine cumulative changes across canonical sources,
generated agents, methodology references, executable behavior and tests.
Account separately for the installed deployment and the uninstalled candidate.
Recommend what to retain, revert, rework or defer, citing commits and paths.
Do not assume a blanket rollback is safer than a selective reversal.

This document records the owner's direction; it is not a new approved feature
specification and does not alter historical approval pins.
