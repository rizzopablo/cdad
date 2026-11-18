# Recorded decisions — 019-004

## 2026-11-16 — reviewer optional finding on the root-resolving locator guard

The T1 reviewer noted that `cdad_layout.py` rejects a locator that resolves to the
repository root itself (`spec` §4.1 does not list that case) and offered two
remedies: remove the guard or declare repository-root placement unsupported.

Decision by the orchestrator under Pablo's renewed HITL delegation: keep the
guard and treat repository-root methodology placement as unsupported. Reasons:
`.cdad/` and the methodology directory share the repository root, so state,
policy and operational storage would become indistinguishable in scope; the
specification already forbids a locator at or beneath `.cdad/` and any escape,
and this is the same safety intent applied to the boundary case. The approval
pinned in stage `specification` remains valid because the guard only rejects a
previously unspecified pathological input and weakens no promise: it cannot make
a conforming promise fail.

Obligation carried into T2: a focused test asserting that a locator resolving to
the repository root is rejected without writes, citing this decision.

## 2026-11-16 — strictness boundaries after the T2 review fix

The strict resolver made three call sites fail in ways that approved legacy tests
forbid. Decision by the orchestrator under delegated HITL:

- **Continuity:** an unresolved layout is treated as absent state and policy; it is
  never replaced by `docs/`. `begin`, `checkpoint` and `reconcile` keep working on
  operational `.cdad/` records because their contracts are state-only and existing
  approved tests require that behavior. An invalid locator still errors.
- **Gap-report:** remains a read-only report over an explicit `--state`, so its
  legacy `docs/` lookup without a locator is retained; it selects no location for
  writes and its new focused tests pin both registered and legacy outcomes.
- **Propose-policy:** stays a read-only proposal and is not blocked by ambiguity;
  it must not invent a base root, and it reports none in that case.

None of the three selects `docs/` for an ambiguous project in an operational write
path; the tested operational commands (`validate-state`, `status`, `open-unit`,
`prepare`) fail with an ambiguity diagnostic and no writes.

## 2026-11-16 — continuity store is not initialization evidence

The test-writer asked whether the continuity store that `begin` itself creates
under `.cdad/executions/<id>/continuity` counts as insufficient initialization
evidence. If it counted, a first `begin` would make every later `begin` or
`checkpoint` fail for a project whose methodology layout is still being decided.

Decision by the orchestrator under delegated HITL: continuity checkpoints are
operational records of the continuity layer, not methodology artifacts, so they
do not by themselves constitute ambiguous initialization evidence. Packet,
execution, dispatch and receipt records under `.cdad/` do count, as the approved
tests require. A project with no admitted methodology layout and no such records
remains allowed to start a continuity chain; once state is required, resolution
still applies.

## 2026-11-16 — guard records are not initialization evidence

`trigger` was left out of the layout-checked commands because its approved fixture
`tests/test_003_004_t3_trigger.py::P4` seeds guard records under
`.cdad/executions/<id>/guards` without any methodology layout and expects the
command to work.

Decision by the orchestrator under delegated HITL: guard records belong to the
same operational layer as continuity checkpoints — they are written by the guard
hook about role sessions, not about methodology artifacts — so they do not
constitute initialization evidence. Packet, execution, dispatch and receipt
records still do. Consequently `trigger` joins the layout-checked commands, and
that fixture resolves as an uninitialized project rather than an ambiguous one.

## 2026-11-17 — a candidate identification is any JSON object with identification keys

The T3 implementation only counted a fenced block whose info string is exactly
`json` as a candidate, so a second identification delivered as a plain fence, an
uppercase `JSON` fence, a fence with trailing space, or raw JSON in the wrapper was
silently ignored instead of rejected. The fragment-heading set also missed
`## Contract` and `## Task validation plan`, which the rendered packet emits.

Decision by the orchestrator under delegated HITL: a candidate identification is
any JSON object, fenced in any form or unfenced in wrapper text, that carries at
least one identification-defining key (packet_id, execution_id, contract, request,
packet, project_root). More than one candidate is rejected in any order; a single
partial candidate is rejected as ambiguous; unrelated JSON without those keys stays
inert. The packet-section heading set covers every heading the published packet can
emit, so fragments beginning with any of them are rejected.

This refines the implementation of §6.4 without changing its promise: the wrapper
admission is unchanged and no candidate is ever normalized or preferred.

## 2026-11-17 — distinguishing evidence for a candidate identification

The previous rule counted any JSON object carrying `request`, `contract`, `packet`
or `project_root` as a candidate, so a legitimate wrapper such as
`{"note":"x","request":"coffee"}` was rejected as a second identification. Those
keys are ordinary JSON keys and do not identify a packet.

Decision by the orchestrator under delegated HITL: a candidate identification is a
JSON object — in any delivery form — that carries `packet_id` or `execution_id`,
the two distinctive identifiers of a published packet. An object carrying one of
them but not the full identification field set is a partial candidate and is
rejected as ambiguous, never merged or completed. Objects without either
identifier are inert wrapper content, whatever other keys they use.

Also decided: the renderer's instruction-block delimiters
(`<!-- cdad-instructions:start -->` and its end marker) are packet fragments and
are rejected in a Route C wrapper exactly like a section heading.

## 2026-11-17 — a wrapper line copied from the published packet is a fragment

Heading and delimiter matching alone cannot recognize packet body content: the
review reproduced acceptance of a published objective paragraph appended without
its heading.

Decision by the orchestrator under delegated HITL: once the named publication is
identified, a Route C wrapper is rejected as containing a packet fragment when any
of its lines, after stripping and ignoring empty ones, has at least 24 characters
and appears verbatim among the lines of that publication's packet body, excluding
the identification block itself. Shorter lines are exempt so that ordinary prose
and unavoidable coincidences stay inert. Heading and delimiter matching remains in
place. This closes the prohibition of section 6.4 for recognizable body content
without claiming that arbitrary paraphrases can be detected.
