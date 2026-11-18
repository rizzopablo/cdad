# Recovery approval and execution decisions

Approved under Pablo's renewed explicit HITL delegation for epic 019.
The owner selected `bc922c04`; restoration of product and tests is complete.

## Independent review disposition

Review 001's kind/cardinality and corrected-presentation findings were resolved
by the architect and independently closed in review 002. No new cardinality
guard or materialization engine change is commissioned.

Review 002's candidate-execution finding is resolved as an explicit operational
precondition, not a waiver: the orchestrator owns execution feasibility and must
demonstrate effective candidate instruction loading before T8 begins. Existing
project-local `.opencode/agents` and `.opencode/skills` scratch-run evidence
establishes a candidate route worth reusing, not acceptance of the new candidate.
Use a fresh disposable workspace, preserve configured role model overlays, copy
candidate instructions locally, publish new packets, capture effective hashes
and complete session transcripts. Global installation and model settings must
remain unchanged. If local precedence or frozen packet provenance cannot be
demonstrated, T8 remains blocked; do not claim installed sessions are candidate
sessions. Installation is not authorized as a fallback.

This addresses the review's expressly offered resolution: an identified owner
and mandatory resolution condition before T8. No further architectural redesign
is required to proceed with independent tests and production.

## Prospective authority

Approve `recovery-spec.md` and `recovery-plan.md` as the replacement contract.
Old 019-002 promises and conflicting 019-001 activation details are superseded
prospectively only. Historical approvals, pins, failures and receipts remain.
019-003 verification-method routing remains accepted. No deployment, publication,
directory migration or model changes are authorized.

The necessary execution order remains independent RED, GREEN, semantic
production, independent contextual review, bounded real candidate exercise,
independent exercise assessment, complete `tests/` evidence and epic closure.
