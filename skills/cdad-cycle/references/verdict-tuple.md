# Verdict Contract — 4-field Tuple (G2, Split the Labor 2608.14509)

> **Source:** https://arxiv.org/abs/2608.14509 (Wu, Atlassian — "Split the Labor:
> Separating Evidence Interpretation from Decision Aggregation", Prop 1-4 + §4.6).
> **Motivation:** the ad-hoc aggregation of review findings (counting BLOCKING
> items by hand, adding up fixed weights) inherits count-scale drift + misweighting
> that no threshold absorbs. This contract fixes the INTERFACE between the reviewer
> (layer 1, isolated interpretation) and the orchestrator (layer 2, aggregation +
> prioritization), without changing who decides: prioritization remains human or
> the process owner's (stage-4-review.md Layer 2).

## The tuple (per finding)

Each finding of a CDAD review emits exactly 4 fields:

| Field | Symbol | What it is | Hard rule |
|-------|--------|-----------|-----------|
| Verdict | Ŷ | `BLOCKING` \| `OPTIONAL` \| `ABSTAIN` | The reviewer NEVER emits "I don't know" as OPTIONAL. If it cannot judge (missing context, outside its reach), it emits `ABSTAIN`. Committed error costs more than not answering. |
| Reliability bucket | b | `h` \| `m` \| `l` estimated from OBSERVABLE properties of the reading | Eliciting it is forbidden ("my confidence is 0.8"). It is derived by deterministic rule (below). |
| Rationale | r | Concrete problem, causal mechanism | It must be verifiable against the code/spec, not opinion. |
| Provenance | a | Exact `file:lines` + ref to the violated postcondition or convention | Without provenance, the finding does not enter the aggregation (weight 0). |

## Bucket rule from observables (not elicited)

Accumulable points, bucket = sum:

| Observable property | +points |
|--------------------|---------|
| Model from a family DIFFERENT from the implementer's (declared at the start) | +1 |
| Full diff in context (no loose snippets) | +1 |
| Grounded rationale with exact verifiable citation `file:lines` | +1 |
| Spec + conventions in context | +1 |
| 0-1 points → `l` · 2 points → `m` · 3-4 points → `h` | |

The bucket does NOT measure the reviewer's quality: it measures the EXPECTED
CALIBRATION of the reading from session conditions — exactly the paper's design
(buckets from source properties, never elicited confidence).

## Aggregation (fixed arithmetic, diagnostic — not decision)

The orchestrator does NOT decide by arithmetic; it uses the aggregation as a
**drift diagnostic** and passes the report to Layer 2 (human prioritization)
intact.

1. **LLR pooling (Prop 4):** for each BLOCKING item, evidence
   ℓ = log(α_b / β_b) with α_b = expected hit rate of the bucket,
   β_b = expected false positive rate. Conservative defaults to be tuned by
   data (G3): h=(0.8, 0.1), m=(0.6, 0.3), l=(0.4, 0.5).
2. **κ-dedupe for dependent blocks (§4.6):** findings from the SAME commit,
   same session or same failure class do NOT accumulate as independent
   corroboration — count them as 1 block (κ = 1/(1+ρ(|B|−1)), implicit ρ = 1).
3. **ABSTAIN contributes no evidence** but is reported separately:
   N abstentions = a signal that the review touched zones out of reach
   (this IS information for Layer 2, not noise).
4. **Aggregator output:** `X blocking · Y optional · Z abstentions ·
   total LLR score (→ drift check: compare precision by number of sources,
   falsifiable prediction #1 of the paper)`.

Example of the drift this prevents (Prop 2): 2/3 sources asserting with
prior 0.2 → posterior 0.39; 2/6 → 0.001 — same count, a 300× difference.
A review with 12 BLOCKING items is not 6× more severe than one with 2 if they
come from the same commit block (κ) and the same bucket (identical ℓ).

## Current application

This contract applies to the `cdad-cycle` cycle: the Stage 4 reviewer (any
variant, generic or Odoo, on any runtime) emits the 4-field tuple per
finding; the orchestrator uses it as a drift diagnostic when passing the
report to the human Layer 2. It does not automatically extend to uses outside
the cycle (other review pipelines, other audit formats) — each new adoption
is evaluated separately against its own context.

## Anti-scope

- Does NOT change Layer 2 of stage-4-review.md: prioritization remains
  human or the process owner's. The arithmetic is diagnostic, not veto.
- Does NOT touch `cdad-epic` — only `cdad-cycle`; extending it to the epic
  level requires separate approval from the process owner.
- The α_b/β_b defaults are placeholders to be estimated from data (G3), not
  benchmark-calibrated.

## Reviewer behavior under push-back (reconsideration)

When the receiver issues push-back with evidence (see
`receiving-feedback.md`), the reviewer does **steelman BEFORE retracting** a
finding — "what is the strongest case that it still holds given this
context?" — and only reverts it with written justification. 2+ reversals in
the same review = yellow flag of capitulation → second pass in a fresh
session. The reconsideration re-emits the finding with the same 4-field
tuple: none of this changes the verdict format.

**Status:** minimal active descriptor in cdad-cycle (reviewer template +
re-entry). G3/G4 of the deep-read 2608.14509 remain open (rate estimation
from data; dependency blocks in DCPM cluster weights).
