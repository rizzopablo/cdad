#!/usr/bin/env python3
"""cdad_lifecycle — the ONE pure decision core of the lifecycle (008-003 §4).

Facts in, decision out. This module performs NO I/O: it never opens a file,
never writes, never reads the clock (every date arrives as an explicit
argument) and never imports a consumer (`cdad_packet`, `cdad_continuity`,
`cdad_result`). The consumers gather and verify the facts — execution context
and canonical registry, request/descriptor/receipt, state binding and
suspension registry, delegation and the existence of its source, durable
evidence, digests and the demonstrable chain — and the rules below decide.

Migrated rules (spec §4.2-§4.4, PC-01..PC-06):

* identity and owner (`resolve_execution_identity`, `resolve_owner`): the
  supplied identity selects WHAT is examined; it never accredits WHO owns it.
* authority (`classify_authority`, `require_authority`, `require_epic_binding`):
  ONE semantic criterion for equivalent authority facts.
* replay, conflict and new effect (`decide_continuity_write`,
  `decide_continuity_close`, `decide_transition`, `decide_receipt`): §4.4 order
  — a replay recognized inside its own domain wins over the eligibility of a
  new effect, and the domain rules (not the consumer) say which one it is.
* suspension (`require_owner_operable`): the suspension follows the accredited
  owner, never the supplied identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import re
from typing import Any, Iterable, Mapping, Sequence

# ------------------------------------------------------------------ vocabulary

ABSENT = "absent"
ACTIVE = "active"
EXPIRED = "expired"
REVOKED = "revoked"
UNKNOWN = "unknown"

#: Declared statuses that keep the delegation vigente (subject to its date).
ACTIVE_STATUSES = frozenset({"active", "current"})
#: Declared statuses that revoke the delegation by themselves.
REVOKED_STATUSES = frozenset({
    "revoked", "user-revoked", "revoked-by-user", "cancelled", "canceled"})

IDENTITY = "identity"
SUSPENSION = "suspension"
AUTHORITY = "authority"
CONFLICT = "conflict"

REPLAY = "replay"
NEW_EFFECT = "new-effect"
CONFLICT_OUTCOME = "conflict"


# -------------------------------------------------------------------- decision


@dataclass(frozen=True)
class Cause:
    """One refused promise: the machine code and the diagnostic that names it."""

    code: str
    detail: str


@dataclass(frozen=True)
class Decision:
    """The result of one pure decision: no cause means the operation may go on.

    `facts` carries what the consumer needs to continue (the accredited
    execution id, the owner, the outcome) without deciding again."""

    causes: tuple[Cause, ...] = ()
    facts: Mapping[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return not self.causes

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(cause.code for cause in self.causes))

    def message(self) -> str:
        return "; ".join(cause.detail for cause in self.causes)


def _deny(code: str, detail: str, **facts: Any) -> Decision:
    return Decision((Cause(code, detail),), facts)


def combine(*decisions: Decision) -> Decision:
    """Every cause of every decision, in the order they were evaluated.

    Nothing short-circuits: a rejection that hides *why else* the operation was
    illegitimate is not diagnostic (§5 PC-01/PC-02). An identical cause reported
    twice (the same owner checked as supplied and as accredited) appears once."""
    causes: list[Cause] = []
    seen: set[tuple[str, str]] = set()
    facts: dict[str, Any] = {}
    for decision in decisions:
        for cause in decision.causes:
            key = (cause.code, cause.detail)
            if key in seen:
                continue
            seen.add(key)
            causes.append(cause)
        facts.update(decision.facts)
    return Decision(tuple(causes), facts)


# ------------------------------------------------------------------- authority


@dataclass(frozen=True)
class Authority:
    """The classified authority of a delegation: the shared semantic result."""

    kind: str
    reason: str | None = None
    source: str | None = None
    expires_on: str | None = None

    @property
    def vigente(self) -> bool:
        """Absent is NOT a denial: without a delegation record the owner is the
        original authority and there is nothing to verify (PD-6/P2)."""
        return self.kind in (ABSENT, ACTIVE)


def declared_source(delegation: Mapping[str, Any]) -> str | None:
    source = delegation.get("source")
    if isinstance(source, str) and source.strip():
        return source
    reference = delegation.get("authority_ref")
    if isinstance(reference, str) and reference.strip():
        return reference
    return None


def classify_authority(delegation: Any, *, today: date) -> Authority:
    """§4.3: ONE semantic criterion of authority for equivalent facts.

    * a present revocation or an explicitly incompatible status: not vigente;
    * a structured invalid date is UNKNOWN, a past date is not vigente;
    * a delegation with a declared source and no date expires by events;
    * no delegation at all is `absent` (nothing to verify, never a denial)."""
    if not isinstance(delegation, Mapping) or not delegation:
        return Authority(ABSENT)
    source = declared_source(delegation)
    revoked_at = delegation.get("revoked_at")
    status = delegation.get("status")
    expires_on = delegation.get("expires_on")

    if revoked_at is not None:
        return Authority(
            REVOKED,
            f"revoked_at={revoked_at!r} is present, so no authority remains",
            source)
    # §4.3: `status` and the declared `state` are the SAME kind of fact — an
    # explicitly incompatible vigencia does not authorize; `active`/`current`
    # (or its absence) leaves the decision to the structured date.
    for field in ("status", "state"):
        declared = delegation.get(field)
        if declared is None or declared in ACTIVE_STATUSES:
            continue
        if declared in REVOKED_STATUSES:
            kind = REVOKED
        elif declared == EXPIRED:
            kind = EXPIRED
        else:
            kind = UNKNOWN
        detail = (f"the declared {field}={declared!r} is not one of "
                  f"{sorted(ACTIVE_STATUSES)}")
        # A normalized record carries the fact that produced its presentation
        # (`_state_authority`): naming it keeps the diagnostic diagnostic.
        reason = delegation.get("reason")
        if isinstance(reason, str) and reason.strip():
            detail = f"{detail} ({reason})"
        return Authority(kind, detail, source)
    if expires_on is not None:
        if isinstance(expires_on, (list, tuple)):
            # Expires by its declared events, never by a date.
            return Authority(ACTIVE, None, source)
        if isinstance(expires_on, str) and expires_on.strip():
            declared = expires_on.strip()
            try:
                expiry = date.fromisoformat(declared)
            except ValueError:
                return Authority(
                    UNKNOWN,
                    f"expires_on={expires_on!r} is not an ISO date, so its "
                    "vigencia is unknown",
                    source, declared)
            if expiry < today:
                return Authority(
                    EXPIRED, f"expires_on={expires_on!r} is in the past",
                    source, declared)
            return Authority(ACTIVE, None, source, declared)
        return Authority(
            UNKNOWN,
            f"expires_on={expires_on!r} is not a verifiable structured date",
            source)
    if source is not None:
        return Authority(ACTIVE, None, source)
    return Authority(
        UNKNOWN,
        "the delegation declares no source and no expiry, so its vigencia is "
        "unknown",
        None)


def require_authority(delegation: Any, *, today: date,
                      operation: str = "a managed effect") -> Decision:
    """§4.3: an authority that is not vigente never authorizes a NEW managed
    effect; the historical read and the accredited replays are decided by their
    own consumers and never ask this question."""
    authority = classify_authority(delegation, today=today)
    if authority.vigente:
        return Decision(facts={"authority": authority.kind})
    return _deny(
        AUTHORITY,
        f"HITL delegation is not vigente for {operation}: the authority is "
        f"{authority.kind} because {authority.reason}; a revoked, expired or "
        f"unknown authority never authorizes a managed effect that requires it "
        f"(§4.3)",
        authority=authority.kind)


def scope_names_epic(scope: Any, epic_id: str) -> bool:
    """An unambiguous reference to the epic: the exact identifier, or the exact
    identifier as a standalone token of a scope list/string. Never a substring
    or prefix of a different identifier (F2)."""
    if isinstance(scope, list):
        return epic_id in scope
    if isinstance(scope, str):
        if scope == epic_id:
            return True
        # ':' and parentheses are token separators too (the real scope is
        # "<epic-id>: ..."), so the identifier is matched as an exact token.
        parts = re.split(r"[,\s;/|:()]+", scope.strip())
        return epic_id in [token for token in parts if token]
    return False


def require_epic_binding(delegation: Mapping[str, Any], *,
                         epic_id: str) -> Decision:
    """§4.3: a managed operation that requires an epic delegation needs its epic
    and scope concordant and a declared source. The consumer verifies that the
    declared source EXISTS (a physical check); this rule decides the rest."""
    causes: list[Cause] = []
    declared_epic = delegation.get("epic_id")
    if declared_epic is not None and declared_epic != epic_id:
        causes.append(Cause(
            AUTHORITY,
            f"hitl_delegation epic mismatch: declared epic_id "
            f"{declared_epic!r} != the operation's epic {epic_id!r}"))
    if not scope_names_epic(delegation.get("scope"), epic_id):
        causes.append(Cause(
            AUTHORITY,
            f"hitl_delegation scope {delegation.get('scope')!r} does not name "
            f"the active epic {epic_id!r} exactly"))
    if declared_source(delegation) is None:
        causes.append(Cause(
            AUTHORITY,
            "hitl_delegation source missing: no authority reference to verify"))
    return Decision(tuple(causes))


# ---------------------------------------------------------- identity and owner


def _present(label: str, value: Any) -> tuple[str, str] | None:
    if isinstance(value, str) and value.strip():
        return label, value
    return None


def resolve_execution_identity(*, declared: Any = None, flat: Any = None,
                               located: Any = None) -> Decision:
    """§4.2: the identities present in applicable sources must agree.

    `declared` is the nested `execution.id`, `flat` the compatibility
    `execution_id` of the using fixture/context and `located` the identity
    implied by the canonical location of the document
    (`.cdad/executions/<id>/execution.json`). Contradiction or absence of the
    necessary evidence fails closed BEFORE any effect."""
    present = [item for item in (_present("execution.id", declared),
                                 _present("execution_id", flat)) if item]
    distinct = {value for _, value in present}
    if len(distinct) > 1:
        named = " and ".join(f"{label} {value!r}" for label, value in present)
        return _deny(
            IDENTITY,
            f"identity contradiction: the same context declares {named} — one "
            f"operation cannot name two executions (§4.2)")
    if not present:
        return _deny(
            IDENTITY,
            "identity missing: the context declares neither execution.id nor "
            "execution_id, so there is no execution to examine (§4.2)")
    identity = present[0][1]
    located_id = located if isinstance(located, str) and located.strip() else None
    if located_id is not None and located_id != identity:
        return _deny(
            IDENTITY,
            f"identity contradiction: the context declares the execution "
            f"{identity!r} but its canonical record is the one of "
            f"{located_id!r} (.cdad/executions/{located_id}/execution.json): a "
            f"copy of one execution cannot claim another identity (§4.2)")
    return Decision(facts={"execution_id": identity})


def resolve_owner(*, supplied: Any, execution_id: Any,
                  declared: Iterable[tuple[Any, Any]] = ()) -> Decision:
    """§4.2: the supplied identity selects the object; the OWNER is resolved
    from the evidence that declares that execution.

    `declared` yields `(execution_id, feature_id)` pairs from the accredited
    sources (state binding, suspension registry, canonical record). Only the
    pairs of THIS execution count: another active unit is not evidence about
    this one, and a historical/suspended unit keeps its own owner."""
    supplied_id = supplied if isinstance(supplied, str) and supplied.strip() else None
    accredited: list[str] = []
    if isinstance(execution_id, str) and execution_id:
        for declared_execution, feature in declared:
            if declared_execution != execution_id:
                continue
            if isinstance(feature, str) and feature.strip() \
                    and feature not in accredited:
                accredited.append(feature)
    if len(accredited) > 1:
        return Decision(
            (Cause(
                IDENTITY,
                f"identity contradiction: the accredited sources disagree on "
                f"the owner of the execution {execution_id!r}: "
                f"{sorted(accredited)} (§4.2)"),),
            {"accredited_candidates": tuple(sorted(accredited)),
             "owner": supplied_id})
    owner = accredited[0] if accredited else None
    if supplied_id is not None and owner is not None and supplied_id != owner:
        return Decision(
            (Cause(
                IDENTITY,
                f"identity contradiction: the supplied feature_id {supplied_id!r} "
                f"disagrees with the owner {owner!r} accredited by the evidence of "
                f"the execution {execution_id!r} (§4.2)"),),
            {"accredited_owner": owner, "accredited_candidates": (owner,),
             "owner": supplied_id})
    return Decision(facts={"owner": supplied_id or owner,
                           "accredited_owner": owner,
                           "accredited_candidates": tuple(accredited)})


def require_owner_operable(*, owner: Any,
                           suspended: Any = None) -> Decision:
    """§4.3: the suspension blocks NEW effects on the SUSPENDED OWNER and never
    on another unit just because some suspension exists."""
    registry = suspended if isinstance(suspended, Mapping) else {}
    if isinstance(owner, str) and owner and owner in registry:
        return _deny(
            SUSPENSION,
            f"unit {owner!r} is suspended: effects on it are blocked until it "
            f"is resumed — resume with resume-unit --feature {owner} (§4.3)",
            owner=owner)
    return Decision(facts={"owner": owner})


def require_concordant(pairs: Sequence[tuple[str, Any]], *,
                       subject: str) -> Decision:
    """§4.2 at a reception/close boundary: every source that declares the
    `subject` must declare the SAME value; an absent declaration is not a
    contradiction, and nothing is invented from the active state."""
    present = [item for item in (_present(label, value) for label, value in pairs)
               if item]
    if not present:
        return _deny(
            IDENTITY,
            f"identity missing: no source declares the {subject} of this "
            f"operation (§4.2)")
    distinct = {value for _, value in present}
    if len(distinct) > 1:
        named = "; ".join(f"{label}={value!r}" for label, value in present)
        return _deny(
            IDENTITY,
            f"identity contradiction: the sources disagree on the {subject} "
            f"({named}) — the same operation cannot name two (§4.2)")
    return Decision(facts={"value": present[0][1]})


# ----------------------------------------------------------- replay and effect
#
# §4.4 order, owned here and nowhere else: identity and the necessary evidence
# are gathered and verified by the consumer (§4.1); THEN the replay/conflict of
# the operation's own domain is decided from those verified facts; and ONLY a
# genuinely NEW effect has to satisfy the eligibility of its domain. Each
# domain keeps its own evidence, so each gets its own rule — and the rule, not
# the consumer, says which of the three outcomes the facts produce.

CONTINUITY_WRITE = "continuity-write"
CONTINUITY_CLOSE = "continuity-close"
TRANSITION = "transition"
RECEIPT = "receipt"

#: The decision that names its domain: what the consumer needs to render.
DOMAIN = "domain"


def _outcome(outcome: str, domain: str, **facts: Any) -> Decision:
    return Decision(facts={**facts, "outcome": outcome, DOMAIN: domain})


def new_effect(domain: str, **facts: Any) -> Decision:
    """The facts left a NEW effect: eligibility is required for it."""
    return _outcome(NEW_EFFECT, domain, **facts)


def is_resumed_unit_checkpoint(record: Any, decisions: Any) -> bool:
    """§2.3.1 (003-007 P5) continuity vocabulary: the `checkpoint` that RECORDS
    the resumption of a suspended unit — the one `begin` that may extend the
    same idempotency key instead of colliding with it."""
    if record != "checkpoint" or not isinstance(decisions, (list, tuple)):
        return False
    return any(
        isinstance(item, Mapping) and isinstance(item.get("decision"), str)
        and item["decision"].startswith("Resumed suspended unit ")
        for item in decisions)


def decide_continuity_write(*, command: str, published: bool,
                            head_key_matches: bool, head_record: Any,
                            head_decisions: Any, key: Mapping[str, Any],
                            head_sha256: Any, attempted_sha256: str) -> Decision:
    """§4.4 continuity-write domain — ejecución, paquete e intento.

    * `published`: the content (minus the single top-level `prev`) is ALREADY a
      link of the demonstrable chain ⇒ replay, whatever the active state says;
    * `head_key_matches` + `head_record`: the head carries the same idempotency
      key with a different content. A divergent `checkpoint` — and the `begin`
      of a resumed unit — APPENDS (a legitimately new link); a divergent `begin`
      (or any other command) under the key it cannot extend is a split-brain;
    * anything else is a new effect."""
    if published:
        return _outcome(REPLAY, CONTINUITY_WRITE)
    extends = is_resumed_unit_checkpoint(head_record, head_decisions)
    if head_key_matches and head_record != "reanchor" and command != "checkpoint" \
            and not (command == "begin" and extends):
        return _deny(
            CONFLICT,
            "split-brain: a "
            f"{command} with the same idempotency key (execution_id="
            f"{key.get('execution_id')!r}, packet_id={key.get('packet_id')!r}, "
            f"attempt={key.get('attempt')!r}) diverges from the head (head "
            f"body {head_sha256}, attempted body {attempted_sha256}); refusing "
            "to overwrite the head — escalate (O1/D7)",
            outcome=CONFLICT_OUTCOME, domain=CONTINUITY_WRITE)
    return new_effect(CONTINUITY_WRITE)


def decide_continuity_close(*, closes: Sequence[Mapping[str, Any]],
                            identical: bool, receipt_path: str,
                            receipt_digest: str) -> Decision:
    """§4.4 receipt/close domain: evidencia durable y cadena demostrable.

    `closes` are the closes of `(execution_id, packet, attempt)` that the
    demonstrable chain proves, each as `{sha256, path, digest}` (the facts); at
    most ONE exists, and it is the replay only when its normalized receipt path
    and digest are the same ones being received. Without a close the close is a
    new effect, subject to the preconditions of its own domain."""
    if len(closes) > 1:
        return _deny(
            CONFLICT,
            "violación de unicidad del cierre: hay "
            f"{len(closes)} cierres para el mismo (execution, packet, attempt): "
            f"{[str(entry.get('sha256'))[:12] for entry in closes]} — a lo sumo "
            "UNO por paquete e intento (§2.3.2)",
            outcome=CONFLICT_OUTCOME, domain=CONTINUITY_CLOSE)
    if closes:
        existing = closes[0]
        if identical:
            return _outcome(REPLAY, CONTINUITY_CLOSE,
                            close_sha256=existing.get("sha256"))
        return _deny(
            CONFLICT,
            f"el cierre ya existe con otro contenido: cierre existente "
            f"{existing.get('sha256')} (ruta {existing.get('path')!r}, digest "
            f"{existing.get('digest')!r}) frente a la recepción declarada "
            f"(ruta {receipt_path!r}, digest {receipt_digest!r}) — no se "
            f"sustituye ni se agrega un segundo cierre (§2.3.2)",
            outcome=CONFLICT_OUTCOME, domain=CONTINUITY_CLOSE)
    return new_effect(CONTINUITY_CLOSE)


def decide_transition(*, registered: bool, superseded_by_vigente: bool = False
                      ) -> Decision:
    """§4.4 transition domain: payload and key canónicos existentes.

    A registered transition key is a replay — the state is never written twice
    for the same decision. The ONE exception (006-006 PD-9/R-14/D-15): an
    invocation that collides with a HISTORICAL entry while a VIGENTE approval
    competes is not a repetition of the registered one; answering it with
    success would lose the requested change in silence, so it is a conflict."""
    if not registered:
        return new_effect(TRANSITION)
    if superseded_by_vigente:
        return _deny(
            CONFLICT,
            "conflict: this transition key collides with a historical entry "
            "while a DIFFERENT vigente approval competes for the same feature "
            "and contract; an identical repetition of the registered entry is a "
            "no-op, substituting the vigente one is not (D-15)",
            outcome=CONFLICT_OUTCOME, domain=TRANSITION)
    return _outcome(REPLAY, TRANSITION)


def decide_receipt(*, durable: bool, source_differs: bool = False,
                   part_set_differs: bool = False,
                   divergent_parts: Sequence[str] = ()) -> Decision:
    """§4.4 receipt domain: an existing durable receipt is the accredited replay
    only when its source and parts are the SAME; any difference is a conflict of
    this domain (the facts are the differences, the verdict is decided here)."""
    if not durable:
        return new_effect(RECEIPT)
    if source_differs:
        return _deny(
            CONFLICT,
            "conflict: the incoming source differs from the durable receipt; "
            "refusing to overwrite the existing finalization",
            outcome=CONFLICT_OUTCOME, domain=RECEIPT)
    if part_set_differs:
        return _deny(
            CONFLICT,
            "conflict: the incoming part set differs from the durable receipt; "
            "refusing to overwrite the existing finalization",
            outcome=CONFLICT_OUTCOME, domain=RECEIPT)
    if divergent_parts:
        return _deny(
            CONFLICT,
            "conflict: incoming part "
            f"{divergent_parts[0]!r} differs from the durable receipt "
            "(digest/bytes/kind); refusing to overwrite the existing "
            "finalization",
            outcome=CONFLICT_OUTCOME, domain=RECEIPT)
    return _outcome(REPLAY, RECEIPT)
