# Discovery — bounded review and fix cycles

Status: scope approved by Pablo on 2026-11-16; specification not drafted or
approved. Planned cycle of epic-019-discovery-dialogue after 019-004.

## Owner decisions

Pablo requested a maximum number of consecutive review+fix rounds per cycle,
configured per project together with the specifications. Low or medium
difficulty might need two or three rounds; high difficulty five or six. Those
figures are guidance, not fixed quotas: the architect specifies a reasonable
limit in each unit contract according to apparent difficulty and risk. The limit
is per unit, not for the whole epic.

When the limit is reached, the orchestrator must judge whether the work is
goldplating or whether pending findings prevent reaching the objective or leave
an unacceptable debt. Low or moderate remaining debt goes to one additional
exclusive cycle that accumulates pending items, queued at the end of the epic.

The owner confirmed that a test audit that generates correction rounds counts
like a review, and required precise specification to stop infinite loops without
fundamentally degrading product quality or overcomplicating the orchestrator.

## Attributed current observations

- Contract loop: independent draft review (`plan-review`), correction, and a
  focused re-review when the correction changed the design. Stage 2.
- Result loop: review against the approved contract, fixes, then a closing
  re-review verifying agreed findings and introduced regressions. A small
  mechanical fix may skip it by owner decision; a corrected semantic-only or
  mixed part requires contextual re-review. Stage 4.
- Test audit: AUDIT and POST-AUDIT establish dispositions and substitutes and can
  require corrections. These are the third family named by the owner.
- No current instruction expresses a per-unit bound on consecutive rounds or a
  uniform accumulation mechanism.

## Design questions for the specification

- Define one round precisely for each family, including when a round closes and
  what a finding raised by the latest check does.
- Reuse existing gate and history records rather than inventing a parallel
  bookkeeping system; keep the orchestrator's judgment short and traceable.
- Prevent resetting the counter by renaming a substage, switching route or
  re-dispatching without new evidence.
- Preserve independent review and semantic verification; a bound must never
  authorize declaring unmet promises complete.
- Distinguish goldplating from a real unmet obligation, and state what evidence
  justifies deferral versus re-planning.
- One accumulating cycle per epic, queued at the end, with per-item provenance,
  consequence and resolution criterion. It must not become an unbounded queue.
- Configure the limit with the specification. Determine where a per-project value
  belongs without conflicting with the methodology-layout work of 019-004.

## Next boundary

Close 019-004 before opening this execution. Then obtain architect analysis and a
reviewed specification. No product, tests or existing instructions change here.
