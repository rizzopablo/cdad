# Epic 019 — Delegated execution authority

Pablo expressly delegated HITL for this epic: “Te delego hitl, eres el dueño
del proceso, toma decisiones con criterio amplio pensando en el uso real del
sistema por el usuario final. Continúa orquestando proactivamente hasta completar
las correcciones pendientes y el epic completo.”

The orchestrator may decide and approve within `epic-019-discovery-dialogue`,
including its specifications, gates, reviews, evidence and closure, using the
same standards as the owner and recording the delegation. This mandate expires
at closure, cancellation or revocation. Publication and deployment remain outside
this mandate; a genuine scope expansion requires the owner's instruction. The
request to include the idle/done correction in the current plan is such an
explicit instruction. This delegation does not carry over from or to other epics.

## Owner decision — verification of purely documentary products (2026-11-15)

Decided directly by Pablo (not delegated): for a unit whose product is purely
documentary, with no executable behavior, no automated RED/GREEN test is
required. The independent semantic review, judged against the approved
contract, IS the verification ("the test is the review").

Scope: documentary-only units of this epic (019-001). Executable changes
(019-002 corrections to the CLI, status and tests) keep the normal TDD cycle.
This supersedes the structural-interface amendment proposed in
`spec-amendment-draft.md` (not applied) and resolves `verification-blocker.md`.
The general methodology wording is to be proposed in 019-002 as a requirement,
not changed here. Publication and deployment remain excluded.

## Renewed mandate — 019-004

Pablo renewed the epic HITL delegation and instructed proactive completion of
the remaining corrections and the whole epic. Existing projects retain their
registered methodology directories; new projects default to `cdad/`. A
per-project metadata value, resolved relative to the product repository root,
is the intended single source of the methodology directory. Publication and
deployment still require separate authorization.

## Recorded deviation — Memory Bank timing for 019-004

019-004 was closed with complete suite evidence before its Memory Bank entry was
drafted. The feature execution is closed, so a role packet cannot be prepared
against it. Decision by the orchestrator under delegated HITL: the scribe drafts
the 019-004 and 019-005 entries together at epic closure, and both are materialized
then. The deviation is recorded here rather than worked around with a mis-scoped
packet or an orchestrator-authored entry.

## Owner decision — suite selector maintenance (2026-11-17)

Pablo approved opening `019-007-suite-selector-maintenance` to repair the test
instrument that blocked the epic's closure gate ("Sí, ok A"). The change is
test-only, does not alter the product, and grants no deployment or publication
authority.
