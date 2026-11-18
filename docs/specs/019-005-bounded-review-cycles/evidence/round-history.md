# Ordinary round history (scenario evidence, not a product record)

review-round unit=unit-x; family=result; round=1/3; event=assessment; outcome=two findings; evidence=docs/reviews/r1.md; next=correction; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=result; round=1/3; event=correction; outcome=fixed both findings; evidence=commit-aaa; next=verify; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=result; round=2/3; event=verification; outcome=one finding persists, one optional residue accepted; evidence=docs/reviews/r2.md; next=correct the breach only; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=result; round=2/3; event=correction; outcome=breach corrected; evidence=commit-bbb; next=verify; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=result; round=3/3; event=verification; outcome=committed breach persists; optional residue unchanged; evidence=docs/reviews/r3.md; next=next round required; stopped; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=result; round=3/3; event=adjudication; outcome=breach blocked; residue recorded for the epic accumulation unit; evidence=docs/adjudication.md; next=stop ordinary correction; finite extension requires recorded unmet-promise decision; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=draft; round=1/3; event=assessment; outcome=no blockers; evidence=docs/reviews/d1.md; next=none; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=audit; round=1/3; event=assessment; outcome=one substitution admitted, one gap; evidence=docs/reviews/a1.md; next=post-audit correction; authority=orchestrator under delegated HITL
review-round unit=unit-x; family=audit; round=2/3; event=verification; outcome=substitution accepted with evidence; no further audit correction; evidence=docs/reviews/a2.md; next=none; authority=orchestrator under delegated HITL
