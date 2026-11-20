# Specification amendment 001 — ambiguous initialization evidence

Status: proposed amendment to `spec.md` §4.2, prepared by the orchestrator under
<owner>'s delegated HITL for epic 019, revised after the first independent review of
this text. Independent review is required before it replaces anything.

## Problem

Approved §4.2 lists as insufficient initialization evidence: Memory Bank files,
`docs/epics/` or `docs/specs/`, an unregistered `cdad/` location, and "execution or
packet records under `.cdad/` without an admitted layout".

Taken literally, that includes `.cdad/executions/<id>/continuity/` and
`.cdad/executions/<id>/guards/`. Those stores are written by the runtime's own
session bookkeeping — continuity checkpoints for the current chain and guard
decisions about role sessions — not by methodology operations. A project that has
just started a continuity chain therefore becomes "ambiguous" and blocks the next
`begin`, and an approved trigger fixture that seeds only guard records fails.

The implementation excludes both stores and `decisions.md` records the exclusion,
while the approved text was never amended. That is the contradiction the third T2
review reported.

## Proposed replacement text for §4.2

Replace the paragraph that lists insufficient initialization evidence with:

> The following fixed-location evidence is insufficient by itself and produces an
> explicit ambiguous-layout diagnostic when neither legacy marker nor locator
> exists. The list is closed, and it is checked by fixed location only, never by
> recursive discovery:
>
> - Any conventional Memory Bank file listed in §4.1 under `docs/`.
> - `docs/epics/` or `docs/specs/`.
> - An unregistered `cdad/` methodology location.
> - Any entry under `.cdad/packets/`.
> - Any `.cdad/executions/<id>/` holding anything other than `continuity/` and
>   `guards/`, checked one level deep: those two stores are operational
>   bookkeeping of the continuity and guard layers, they record a session's own
>   chain and decisions, they do not describe methodology placement, and they are
>   written even before a layout is decided.
> - Any entry under `.cdad/inbox/`.
> - Any entry under `.cdad/runtime/results/`.
> - Any entry under `.cdad/publication/`.
>
> Locations under `.cdad/` that this list does not name — the locator itself,
> orchestration scratch space and any other operational file — are not examined
> and never make a project ambiguous.

## Consequences

- A project holding only continuity or guard records is uninitialized: continuity
  commands proceed, and `layout --for-bootstrap` may propose `cdad/`.
- A project holding a packet, a non-operational execution record, a staged inbox
  delivery, a receipt or a publication record, and no admitted layout, stays
  ambiguous. Dispatch records live under
  `.cdad/executions/<id>/dispatches/` and receipts under
  `.cdad/runtime/results/`, so both are covered by named entries.
- The two affected approved fixtures (`test_003_004_t3_trigger.py::P4` and the
  continuity-chain fixtures) remain valid without further test changes.
- Implementation must add detection for the three newly enumerated locations,
  which today are not examined.
- No other promise of §4 changes.

## Verification

Fixtures for each decided location, positive and negative: only `continuity/`, only
`guards/`, a packet, an execution with a non-operational record, an inbox entry, a
receipt, a publication entry, an unnamed operational file under `.cdad/`, plus a
valid legacy project, a registered layout and an empty project. Existing focal
selections for continuity, receipts, trigger and gap-report stay green.
