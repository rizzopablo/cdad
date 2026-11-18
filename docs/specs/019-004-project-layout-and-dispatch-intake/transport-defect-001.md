# Procedural defect — draft reception used a stale descriptor

On 2026-11-16 the orchestrator recorded and received
`019-004-project-layout-and-dispatch-intake-architect-draft-001` while
`.cdad/inbox/RESULT.json` still described the previous architect consultation.
The durable receipt therefore finalized a 590-byte role-report part
(`dd61b19b39450d4e7485d8b73d86f548d44c5ee25c227aa901d51ce8d69ab51b`) instead of
the architect's 38903-byte draft. `cdad_result.py receive` correctly refused to
overwrite the finalized receipt.

What was done instead, without fabricating a valid reception:

- The architect's actual final text was read from its native session
  `<session>` and preserved byte-identically as
  `.cdad/inbox/019-004-project-layout-and-dispatch-intake-architect-draft-001.md`
  (sha256 `51385269290e90d804a39a5d330a07e0733f176f2fbda5c230c74590a4e2ce90`).
- `spec.md` and `plan.md` were materialized from that text as declared in
  `architect-draft-provenance.json`: only each section's draft banner line was
  replaced by an equivalent H1; the body is otherwise unchanged.
- No validated receipt is claimed for this materialization. The defective
  receipt remains on disk unchanged as evidence.

Corrective practice: stage every native result to a packet-specific file and
pass that file, never a shared descriptor, to `record`.

This is a procedural defect, not a product failure; it does not by itself
invalidate the draft's content, which independent review will still assess.
