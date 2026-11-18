# Acceptance record — 019-001 operating design

Date: 2026-11-15. Accepted by: the CDAD orchestrator, under Pablo's delegation
for epic 019 (`docs/epics/epic-019-discovery-dialogue/execution.md:8-14`),
inside the epic, without publication or deployment.

## What is accepted

- Design decisions D1-D5 of `spec.md`, as implemented in
  `operating-design/` at the commit recorded by the closing transition.
- The operating design as a documentary proposal. It is NOT an activation:
  no role instruction, packet, script or installed skill changes until 019-002.

## Evidence

- Verification is independent semantic review against the protected checklist
  (`review-checklist.md`, sha256 `41161a34…a83f`), per the owner decision in
  `execution.md` ("Owner decision — verification of purely documentary
  products"). No RED/GREEN applies to this unit.
- Four review rounds: `review-001.md`, `review-002.md`, `review-003.md`,
  `review-004.md`. The last found no blockers and PC-1..PC-12 satisfied as
  documentary proposals; PC-11 and the 019-002 handoff are protocols, not
  observed results.

## Honest procedural notes

- Construction started before this acceptance of D1-D5 was recorded; the spec
  says that acceptance authorizes construction. The orchestrator recorded it
  only after review. The defect is the orchestrator's, not the producer's.
- Round 1 of the fix added an unrequested "epic-level delegation" rule; the
  independent review rejected it as exceeding the approved scope and it was
  removed (`review-002.md`, finding 1).

## Carried forward (not blocking)

- Nit (review-004): mark E4/E5 in the events table of
  `readiness-and-approval.md` as "unless exempted", or introduce the table as
  the reviewed route.
- Canonical `stage-2-specification.md:47-50` omits the draft-review exemption
  that `:71-74` allows; to reconcile in 019-002.
- ADR-040 is missing from the `docs/systemPatterns.md` decision index.
