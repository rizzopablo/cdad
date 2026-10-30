#!/usr/bin/env python3
"""cdad_continuity — deterministic context-continuity CLI (003-004, T1/T2).

Three layers (D2): L2 = immutable checkpoint (authority of decisions/budget),
L1 = on-demand active projection (never persisted, O1), L3 = references to the
existing history. Implemented surface:

    begin      --project-root ROOT --execution-context EXEC.json \
               --update UPDATE.json [--max-bytes N] [--json]
    checkpoint --project-root ROOT --execution-context EXEC.json \
               --update UPDATE.json [--max-bytes N] [--json]
    reconcile  --project-root ROOT --execution-context EXEC.json \
               --packet PACKET_ID [--json]
    resume     --project-root ROOT --execution-context EXEC.json \
               [--role ROLE] [--max-bytes N] [--json]
    trigger    --project-root ROOT --execution-context EXEC.json \
               --packet PACKET_ID [--runtime opencode] [--json]

Contracts: `continuity-checkpoint-v1` (L2), `active-record-v1` (L1 render),
`reconcile-v1` and `trigger-v1` (§3, V6). `begin`/`checkpoint` are write-ahead
and write ONLY under `.cdad/executions/<execution_id>/continuity/**` (head +
content-addressed bodies); they never touch `docs/.cdad-state.json` (invariant
1/D3). `reconcile`, `resume` and `trigger` are read-only and deterministic.

`trigger` (P6/D5) is a SIGNAL, never a hard limit: it reads the runtime budget
snapshot frozen in the checkpoint body (`--update.budget`, D11) and only emits
`prepare`/`rotate` when BOTH `context_used_tokens` and `context_limit` are
integers; otherwise it stays `trigger: unknown` with `context_*: null` and an
explicit `unknowns[]`. Bytes are never converted into tokens and no limit is
fabricated (invariant 2). The durable attempt budget is REPORTED by reading
003's `.cdad/executions/<id>/guards/**` (invariant 5: reused, not redefined);
a new session never resets it (P4).

Content addressing: the canonical body is the frozen `--update` (D11) plus the
execution context's HITL authority; it carries NO absolute paths and NO
timestamps, so the same input in two different projects yields the same
`body_sha256` (portable, D8/O2). The body is stored under
`continuity/bodies/<body_sha256>.json`; `continuity/head.json` is the current
envelope. An identical write (same `(execution_id, packet_id, attempt)` key
and same body) is a successful no-op (rc 0) that writes nothing (P3). A
divergent `begin` under the same key is a conflict: the rejection is
all-or-nothing (RU-2) — nothing is written (no body, no head, no new
directory), the head is NOT overwritten and the command fails closed
(rc!=0) — one seq, no generation counter (D7). A divergent `checkpoint` under
the same key is NOT a conflict (003-007 P5): it appends a new link
(`seq+1`, `prev_checkpoint_sha256` = body of the head), preserving the
previous link as evidence.

003-007 (P6/D5): every body written by this CLI carries `record` — `begin`
or `checkpoint` — and so does the envelope (`head.json`). A body WITHOUT
`record` is legacy (pre-003-007); only there a reference without `class` is
resolved by comparison (D6/P7). A body WITH `record` whose reference lacks a
recognizable `class` falls closed to `contract` (P3/O-1).

`--max-bytes` (default 16 KiB) bounds the projection: exceeding it fails closed
with no truncation and no checkpoint persisted (P7). `--role` without the
project policy fails closed (review-t1 R-B2): classification is never
fail-open.

P5 (role isolation): `resume --role test-writer` never exposes implementation
material. A reference is implementation material when its path lies under the
project policy's `implementation_roots`/`implementation_files` — the policy
(`ROOT/docs/cdad-policy.json`) is the SINGLE source of truth for path
classification (review-t1 B2); the path name is never consulted.

JSON is the only output mode (N1): the CLI always renders JSON; `--json` is kept
as an accepted no-op flag for signature compatibility with §3 (V6).

Pure Python stdlib. No service, no permanent agent, no LLM controller.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# The canonical disposition verification lives in the packet CLI — the producer
# owns the transition identity (`_transition_identity_payload`/
# `_transition_key`), so importing it (never re-running it) gives `reconcile`
# and `prepare --replace-packet` the SAME reader of ONE decision (precedent:
# cdad_result.py:47-59).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_packet  # noqa: E402
import cdad_lifecycle  # noqa: E402

CHECKPOINT_CONTRACT = "continuity-checkpoint-v1"
RECORD_CONTRACT = "active-record-v1"
RECONCILE_CONTRACT = "reconcile-v1"
# 003's durable guard event contract — REUSED, never redefined (invariant 5).
GUARD_EVENT_CONTRACT = "guard-event-v1"
SCHEMA_VERSION = 1

DEFAULT_MAX_BYTES = 16 * 1024

# 003-007 (P3/D2): the reference class is DECLARED in the reference, never
# derived from the path. `contract` is the fail-closed default; only an
# explicit `living` yields a non-blocking reference (P2).
REFERENCE_CLASSES = ("contract", "living")

# 007-003 (§2.3.1): the additive historical link that lives ONLY in the body.
# The envelope is closed (`additionalProperties: false`) and is NOT extended.
PREV_FIELD = "prev"
PREV_LINK_KEYS = frozenset({"checkpoint_sha256", "seq"})
# 007-003 (§2.3): the durable receipt reference the common close freezes.
RECEIPT_CHECKPOINT_FIELD = "receipt_checkpoint"
RECEIPT_NAME = "receipt.json"
# 007-003 (§2.5): the closed applicability vocabulary of evidence.
EVIDENCE_STATUSES = ("vigente", "invalidada")
EVIDENCE_KEYS = frozenset({"id", "reference", "status", "reason", "antecedent"})
ANTECEDENT_KEYS = frozenset({"body_sha256", "evidence_id"})
REHABILITATED_MESSAGE = (
    "evidence {id!r} was invalidated and cannot return to `vigente` keeping its "
    "identity: declare a NEW id with its own reference and an antecedent that "
    "explains the substitution (§2.5 — no hash change, re-anchoring or byte "
    "equality rehabilitates evidence)")
_HEX64_RE = re.compile(r"[0-9a-f]{64}")

# Declared 200k context profile (plan T3: 200k/150k/120k). It is a SIGNAL, not
# a hard limit (D5): `trigger` only applies it when the runtime reported an
# integer counter AND an integer limit (P6); otherwise the state stays
# `unknown` and no number is fabricated (invariant 2). `rotate_at` is
# `limit - reserve` (200000 - 50000 = 150000).
PROFILE_RESERVE = 50_000
PROFILE_PREPARE_AT = 120_000

CONTINUITY_TREE = (".cdad", "executions")
RUNTIME_TREE = (".cdad", "runtime")
# 007-003 (§2.1): the published packet (request) the pre-transport proof reads.
PACKETS_TREE = (".cdad", "packets")
REQUEST_NAME = "REQUEST.json"

# Policy file read (never written) to classify references for `--role` (P5).
POLICY_REL_PATH = "docs/cdad-policy.json"

# State file READ (never written, D3) as the authority source when the real
# execution context (001) carries no `hitl_delegation` (D4/review-t4-ru1).
STATE_REL_PATH = "docs/.cdad-state.json"

# Roles that legitimately see implementation material; every other role gets the
# implementation-scoped references filtered out (fail-closed, P5).
IMPLEMENTATION_PRIVILEGED_ROLES = frozenset({
    "orchestrator", "implementer", "implementer-odoo",
})

# Declared convention (review-t1 B2): a reference's role classification comes
# ONLY from the project policy's `path_policy`; path names are never inspected.
_SEGMENT_UNSAFE = ("..",)

_FILENAME_SEGMENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


class ContinuityError(Exception):
    """A designed, deterministic failure: rc!=0 with a named diagnostic."""


# ------------------------------------------------------------------ JSON I/O


def _read_json(path: Path, label: str) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContinuityError(
            f"cannot read {label} {path}: {exc.strerror or exc}") from exc
    try:
        return json.loads(raw)
    except ValueError as exc:
        raise ContinuityError(f"invalid JSON in {label} {path}") from exc


def _canonical_bytes(document: Any) -> bytes:
    """Canonical serialization: sorted keys, compact separators, UTF-8."""
    return json.dumps(document, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_digest(value: Any) -> bool:
    """A lowercase sha256 hex digest (the only form the store addresses by)."""
    return isinstance(value, str) and _HEX64_RE.fullmatch(value) is not None


def _emit(document: Any) -> None:
    sys.stdout.write(json.dumps(document, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")


def _fsync_dir(path: Path) -> None:
    """Durability of a rename (D, review-t2): make the directory entry durable
    so a reported rc 0 head is not lost by a later crash (cdad_result.py
    standard). A filesystem that refuses fsync on a directory is tolerated."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _write_synced(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)
    _fsync_dir(path.parent)


# ------------------------------------------------------------------ paths


def _resolve(root: Path, raw: str) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else root / candidate


def _normalize_reference(raw: Any) -> str:
    """Root-relative POSIX path of a declared reference; fail closed otherwise."""
    if not isinstance(raw, str) or not raw.strip():
        raise ContinuityError("reference must be a non-empty string")
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ContinuityError(f"reference must be relative to project root: {raw!r}")
    text = posixpath.normpath(candidate.as_posix())
    if text == ".." or text.startswith("../"):
        raise ContinuityError(f"reference escapes project root: {raw!r}")
    return text


def _safe_segment(value: Any, label: str) -> str:
    if not isinstance(value, str) or _FILENAME_SEGMENT_RE.fullmatch(value) is None \
            or any(token in value for token in _SEGMENT_UNSAFE):
        raise ContinuityError(
            f"{label} must be a safe path segment "
            f"([A-Za-z0-9][A-Za-z0-9._-]{{0,127}}, no '..'): {value!r}")
    return value


def _continuity_dir(root: Path, execution_id: str) -> Path:
    return root.joinpath(*CONTINUITY_TREE, execution_id, "continuity")


def _head_path(root: Path, execution_id: str) -> Path:
    return _continuity_dir(root, execution_id) / "head.json"


def _body_path(root: Path, execution_id: str, body_sha256: str) -> Path:
    return _continuity_dir(root, execution_id) / "bodies" / f"{body_sha256}.json"


def _results_dir(root: Path, execution_id: str, packet_id: str) -> Path:
    return root.joinpath(*RUNTIME_TREE, "results", execution_id, packet_id)


def _dispatch_dir(root: Path, execution_id: str) -> Path:
    return root.joinpath(*CONTINUITY_TREE, execution_id, "dispatches")


def _materialization_dir(root: Path, execution_id: str, packet_id: str) -> Path:
    return root.joinpath(*RUNTIME_TREE, "materializations", execution_id,
                         packet_id)


# ------------------------------------------------------------------ body


def _state_delegation(root: Path) -> dict[str, Any]:
    """D4: when the context carries no `hitl_delegation`, the authority is read
    from `docs/.cdad-state.json` — structured fields ONLY (prose is never
    parsed). A missing/unreadable state yields no delegation (`unknown`)."""
    path = root / STATE_REL_PATH
    if not path.is_file():
        return {}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(document, dict):
        return {}
    delegation = document.get("hitl_delegation")
    return delegation if isinstance(delegation, dict) else {}


def _state_authority(root: Path) -> dict[str, Any]:
    """Normalize the state delegation into the authority vocabulary
    (`authority_ref` = `source`; `state` in active|expired|unknown).

    The CLASSIFICATION is not made here (008-003 §4.3/PC-06): the shared core
    `cdad_lifecycle.classify_authority` decides vigencia from the declared
    facts, and the normalized record keeps those facts (`status`, `revoked_at`,
    `source`, `expires_on`) so a later evaluation reaches the same verdict
    without deciding again here. `state` is the PRESENTATION of that verdict,
    not a second criterion."""
    delegation = _state_delegation(root)
    if not delegation:
        return {}
    authority = cdad_lifecycle.classify_authority(delegation, today=date.today())
    if authority.kind == cdad_lifecycle.ABSENT:
        return {}
    normalized: dict[str, Any] = {
        "authority_ref": authority.source,
        "state": _AUTHORITY_PRESENTATION[authority.kind],
    }
    for declared in ("status", "revoked_at", "source"):
        if declared in delegation:
            normalized[declared] = delegation[declared]
    expires_on = delegation.get("expires_on")
    if isinstance(expires_on, str):
        normalized["expires_on"] = expires_on
    if authority.reason is not None:
        normalized["reason"] = authority.reason
    return normalized


#: The public vocabulary of `authority.state` (§4.3: presentation only).
_AUTHORITY_PRESENTATION = {
    cdad_lifecycle.ACTIVE: "active",
    cdad_lifecycle.EXPIRED: "expired",
    cdad_lifecycle.REVOKED: "expired",
    cdad_lifecycle.UNKNOWN: "unknown",
}


def _located_execution_id(root: Path, path: Path) -> str | None:
    """The identity implied by the canonical location of a context
    (`.cdad/executions/<id>/execution.json`), or None when the document lives
    anywhere else (a copy, a fixture, the real 001 context)."""
    try:
        relative = path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    parts = relative.parts
    if len(parts) == 4 and parts[0] == CONTINUITY_TREE[0] and \
            parts[1] == CONTINUITY_TREE[1] and parts[3] == "execution.json":
        return parts[2]
    return None


def _load_execution_context(root: Path, path: Path) -> dict[str, Any]:
    document = _read_json(path, "execution context")
    if not isinstance(document, dict):
        raise ContinuityError("execution context must be a JSON object")
    execution = document.get("execution")
    nested = execution.get("id") if isinstance(execution, dict) else None
    # PC-01/§4.2: the supplied identity never accredits itself — the nested and
    # flat declarations and the canonical location must agree before any write.
    identity = cdad_lifecycle.resolve_execution_identity(
        declared=nested, flat=document.get("execution_id"),
        located=_located_execution_id(root, path))
    if not identity.allowed:
        raise ContinuityError(identity.message())
    execution_id = identity.facts["execution_id"]
    _safe_segment(execution_id, "execution_id")
    document["execution_id"] = execution_id
    if not isinstance(document.get("hitl_delegation"), dict):
        # D4/RU-1: the real context never carries the authority; it is read
        # from the structured state and normalized into `hitl_delegation`.
        document["hitl_delegation"] = _state_authority(root)
    return document


def _delegation(exec_context: dict[str, Any]) -> dict[str, Any]:
    delegation = exec_context.get("hitl_delegation")
    return delegation if isinstance(delegation, dict) else {}


def _authority(exec_context: dict[str, Any]) -> dict[str, Any]:
    """The frozen L2 authority (D2): the delegation reference and its declared
    `expires_on` only — the schema-bound shape written into the canonical body.
    The current vigencia (`state`) is evaluated at READ time, never frozen."""
    delegation = _delegation(exec_context)
    return {
        "authority_ref": delegation.get("authority_ref"),
        "expires_on": delegation.get("expires_on"),
    }


def _authority_view(exec_context: dict[str, Any]) -> dict[str, Any]:
    """Authority + current `state` for the read envelopes (`reconcile`,
    `resume`): vigencia is reconstructed on demand (D4), never from prose."""
    authority = dict(_authority(exec_context))
    authority["state"] = _authority_state(exec_context)
    return authority


def _authority_state(exec_context: dict[str, Any]) -> str:
    """D4/§4.3: validity is read from the structured facts, never from prose.

    The verdict is the shared one (`cdad_lifecycle.classify_authority`); this
    function only maps it to the PUBLIC vocabulary of the read envelopes —
    `current` for a dated delegation that is still vigente, `active` when the
    delegation already declares that presentation (state-sourced, expires by
    events), `expired` and `unknown` otherwise. Presentation only: the
    criterion is not decided here."""
    delegation = _delegation(exec_context)
    authority = cdad_lifecycle.classify_authority(
        delegation, today=date.today())
    if authority.kind == cdad_lifecycle.ACTIVE:
        # A delegation that expires by events already declares the presentation
        # `active`; a dated one is `current`. The verdict is the same.
        declared = delegation.get("state")
        return declared if declared in ("active", "current") else "current"
    if authority.kind == cdad_lifecycle.ABSENT:
        return "unknown"
    return _AUTHORITY_PRESENTATION[authority.kind]


def _resolve_reference_declaration(raw: Any) -> dict[str, Any]:
    """003-007 (P3/D4): a reference is either a bare path (compat string,
    `class` = `contract`) or an object `{path, class?, fields?}`. The class is
    taken ONLY from the declaration; an absent or unrecognized class falls
    closed to `contract` (the path is never inspected, D2)."""
    if isinstance(raw, str):
        return {"path": _normalize_reference(raw), "class": "contract"}
    if not isinstance(raw, dict):
        raise ContinuityError(
            "reference must be a string (compat) or an object with a path")
    path = _normalize_reference(raw.get("path"))
    declared = raw.get("class")
    resolved: dict[str, Any] = {
        "path": path,
        "class": declared if declared in REFERENCE_CLASSES else "contract",
    }
    if "fields" in raw:
        fields = raw.get("fields")
        if not isinstance(fields, list) or not all(
                isinstance(field, str) and field.strip() for field in fields):
            raise ContinuityError(
                f"reference {path!r}: `fields` must be a list of non-empty "
                f"strings; got {fields!r}")
        resolved["fields"] = list(fields)
    return resolved


def _projection_digest(document: dict[str, Any], fields: list[str]) -> str:
    """V2 (S5, fixed in RED): the canonical projection of a top-level JSON
    object over `fields` — only the keys that resolve, sorted, compact UTF-8.
    Deterministic: the same projection always yields the same digest."""
    resolved = {key: document[key] for key in sorted(fields) if key in document}
    return _sha256(_canonical_bytes(resolved))


def _field_digest(root: Path, rel: str, fields: list[str]) -> str:
    """BL-3 (P4): `fields` over a non-JSON file is a WRITE-time failure, and a
    projection that resolves no key is never frozen — a constant digest would
    be zero integrity in silence."""
    target = root / rel
    try:
        document = json.loads(target.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ContinuityError(
            f"reference {rel!r}: `fields` requires a JSON object but the file "
            "is not valid JSON") from exc
    except OSError as exc:
        raise ContinuityError(
            f"cannot read reference {rel!r}: {exc.strerror or exc}") from exc
    if not isinstance(document, dict):
        raise ContinuityError(
            f"reference {rel!r}: `fields` requires a JSON object at the top "
            "level but the file is not a JSON object")
    if not any(field in document for field in fields):
        raise ContinuityError(
            f"reference {rel!r}: `fields` {fields!r} resolves no key — an "
            "empty `fields` projection is an integrity hole; refusing to "
            "freeze a constant digest (BL-3)")
    return _projection_digest(document, fields)


def _digest_references(root: Path, references: Any) -> list[dict[str, Any]]:
    """003-007 (P1-P4): stamp the resolved class (and the optional `fields`
    projection digest) into each reference before it is frozen."""
    if references is None:
        return []
    if not isinstance(references, list):
        raise ContinuityError(
            "update.references must be a list of paths or objects")
    digested: list[dict[str, Any]] = []
    for raw in references:
        entry = _resolve_reference_declaration(raw)
        rel = entry["path"]
        target = root / rel
        if not target.is_file():
            raise ContinuityError(f"reference does not exist: {rel}")
        if "fields" in entry:
            entry["sha256"] = _field_digest(root, rel, entry["fields"])
        else:
            entry["sha256"] = _sha256(target.read_bytes())
        digested.append(entry)
    return digested


def _require_key_fields(update: dict[str, Any]) -> None:
    """O2 (P1/P3): the idempotency key `(execution_id, packet_id, attempt)`
    must be well-typed BEFORE anything is persisted — fail closed with the
    violated field named, never persist a schema-invalid head (P1) nor lose
    the discriminating key (P3)."""
    packet_id = update.get("packet_id")
    if not isinstance(packet_id, str) or not packet_id.strip():
        raise ContinuityError(
            "update.packet_id must be a non-empty string (idempotency key "
            f"(execution_id, packet_id, attempt), P3); got {packet_id!r}")
    _safe_segment(packet_id, "update.packet_id")
    attempt = update.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool):
        raise ContinuityError(
            "update.attempt must be an integer (idempotency key "
            f"(execution_id, packet_id, attempt), P3); got {attempt!r}")


def _require_content_fields(update: dict[str, Any]) -> None:
    """R-B1 (review-t1 rereview): the D11 content that gets frozen in the
    checkpoint must satisfy `active-record-v1` BEFORE it is persisted — the
    render declares that contract, so a malformed body would otherwise travel
    unvalidated to T2's `reconcile` consumer. Fail closed, field named."""
    goal = update.get("goal")
    if goal is not None and not isinstance(goal, str):
        raise ContinuityError(
            f"update.goal must be a string or null; got {goal!r}")

    decisions = update.get("decisions", [])
    if not isinstance(decisions, list):
        raise ContinuityError(
            f"update.decisions must be a list; got {decisions!r}")
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            raise ContinuityError(
                f"update.decisions[{index}] must be an object with "
                f"decision+rationale; got {decision!r}")
        if not isinstance(decision.get("decision"), str) or \
                not decision["decision"].strip():
            raise ContinuityError(
                f"update.decisions[{index}].decision must be a non-empty "
                f"string (D11: each decision WITH its rationale); got "
                f"{decision.get('decision')!r}")
        rationale = decision.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ContinuityError(
                f"update.decisions[{index}].rationale must be a non-empty "
                f"string (D11: each decision WITH its rationale); got "
                f"{rationale!r}")

    uncertainties = update.get("uncertainties", [])
    if not isinstance(uncertainties, list):
        raise ContinuityError(
            f"update.uncertainties must be a list; got {uncertainties!r}")
    for index, item in enumerate(uncertainties):
        if not isinstance(item, str):
            raise ContinuityError(
                f"update.uncertainties[{index}] must be a string; got {item!r}")

    next_action = update.get("next_action")
    if next_action is not None and not isinstance(next_action, str):
        raise ContinuityError(
            f"update.next_action must be a string or null; got {next_action!r}")


def _require_current_authority(exec_context: dict[str, Any]) -> None:
    """D4/D6 + plan T2 + §4.3/PC-03: ONE criterion of authority — an expired,
    revoked or UNKNOWN HITL delegation may reconstruct context but never writes
    a checkpoint (no dispatch/materialize authorization). The verdict is the
    shared one; this border only refuses."""
    decision = cdad_lifecycle.require_authority(
        _delegation(exec_context), today=date.today(),
        operation="a continuity write")
    if not decision.allowed:
        raise ContinuityError(
            f"{decision.message()} — refusing to write a checkpoint "
            "(D4/§4.3)")


def _require_reanchor_authority(root: Path,
                               exec_context: dict[str, Any]) -> None:
    """§4.3/PC-06: the vigencia is decided by the shared core; this border adds
    the PHYSICAL check the core cannot make — the declared authority reference
    is a readable file inside the project."""
    delegation = _delegation(exec_context)
    if not delegation:
        return  # Direct owner approval is valid without a delegation record.
    decision = cdad_lifecycle.require_authority(
        delegation, today=date.today(), operation="a reanchor")
    if not decision.allowed:
        raise ContinuityError(
            f"registered delegation is not vigente: {decision.message()}")
    reference = delegation.get("authority_ref") or delegation.get("source")
    if not isinstance(reference, str) or not reference.strip():
        raise ContinuityError("registered delegation has no verifiable authority_ref")
    rel = _normalize_reference(reference)
    authority_path = (root / rel).resolve()
    if root not in authority_path.parents or not authority_path.is_file():
        raise ContinuityError("registered delegation authority_ref is not a readable project file")


def _canonical_body(exec_context: dict[str, Any], update: dict[str, Any],
                    references: list[dict[str, str]],
                    record: str, *,
                    changes: list[str] | None = None,
                    evidence: list[dict[str, Any]] | None = None,
                    receipt_checkpoint: dict[str, str] | None = None,
                    prev: dict[str, Any] | None = None,
                    include_prev: bool = False) -> dict[str, Any]:
    body = {
        "schema_version": SCHEMA_VERSION,
        "execution_id": exec_context["execution_id"],
        "packet_id": update.get("packet_id"),
        "attempt": update.get("attempt"),
        # 003-007 (P6/D5): the command that wrote this body. Legacy bodies
        # (pre-003-007) carry no `record`; it is the legacy discriminator (O-1).
        "record": record,
        "goal": update.get("goal"),
        "authority": _authority(exec_context),
        "decisions": update.get("decisions", []),
        "uncertainties": update.get("uncertainties", []),
        "next_action": update.get("next_action"),
        "references": references,
    }
    # D11 + plan T3: the runtime budget snapshot (`context_used_tokens` /
    # `context_limit` / `source`) travels in the frozen body; `trigger` reads
    # it from the checkpoint head. Included only when the update declares it,
    # so bodies without a snapshot keep their exact prior canonical form.
    if "budget" in update:
        body["budget"] = update.get("budget")
    # 007-003 (§2.5/§2.6): additive fields, absent when nothing declares them,
    # so a body with no `changes`/`evidence` keeps its exact prior form.
    if changes is not None:
        body["changes"] = changes
    if evidence is not None:
        body["evidence"] = evidence
    # 007-003 (§2.3): the reference to the durable receipt of the common close.
    if receipt_checkpoint is not None:
        body[RECEIPT_CHECKPOINT_FIELD] = receipt_checkpoint
    # 007-003 (§2.3.1): the historical link. It is added ONLY after the
    # repetition decision (it is physically digested but excluded from the
    # repetition comparison); `include_prev` keeps the two moments apart.
    if include_prev:
        body[PREV_FIELD] = prev
    return body


def _content_without_prev(body: dict[str, Any]) -> dict[str, Any]:
    """§2.3.1: the content compared to decide a repetition is the whole body
    minus the single top-level `prev` field. A legacy body (no `prev`) is NOT
    transformed into `prev: null`, and no other field is dropped (`record`
    included)."""
    return {key: value for key, value in body.items() if key != PREV_FIELD}


def _declared_changes(update: dict[str, Any]) -> list[str] | None:
    """§2.5: `changes` is a list of non-empty strings declared by the writer
    (never an automatic producer of `observed_changes`)."""
    if "changes" not in update:
        return None
    value = update.get("changes")
    if not isinstance(value, list) or not value:
        raise ContinuityError(
            "update.changes must be a non-empty list of non-empty strings: an "
            f"empty list cannot retire a declaration in silence; got {value!r}")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ContinuityError(
                f"update.changes[{index}] must be a non-empty string; got {item!r}")
    return list(value)


def _evidence_entry(raw: Any, index: int) -> dict[str, Any]:
    """§2.5: one `evidence` entry with its closed shape and applicability."""
    if not isinstance(raw, dict):
        raise ContinuityError(f"update.evidence[{index}] must be an object")
    if set(raw) != EVIDENCE_KEYS:
        raise ContinuityError(
            f"update.evidence[{index}] carries exactly "
            f"{sorted(EVIDENCE_KEYS)}; got {sorted(raw)}")
    evidence_id = raw.get("id")
    if not isinstance(evidence_id, str) or not evidence_id.strip():
        raise ContinuityError(
            f"update.evidence[{index}].id must be a non-empty string")
    reference = raw.get("reference")
    if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
        raise ContinuityError(
            f"update.evidence[{index}].reference must be an object with exactly "
            f"`path` and `sha256`; got {reference!r}")
    path = _normalize_reference(reference.get("path"))
    digest = reference.get("sha256")
    if not _is_digest(digest):
        raise ContinuityError(
            f"update.evidence[{index}].reference.sha256 must be 64 lowercase "
            f"hex; got {digest!r}")
    status = raw.get("status")
    if status not in EVIDENCE_STATUSES:
        raise ContinuityError(
            f"update.evidence[{index}].status must be one of "
            f"{list(EVIDENCE_STATUSES)}; got {status!r}")
    reason = raw.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ContinuityError(
            f"update.evidence[{index}].reason must be a non-empty string — it is "
            f"required in BOTH `vigente` and `invalidada`; got {reason!r}")
    antecedent = raw.get("antecedent")
    if antecedent is not None:
        if not isinstance(antecedent, dict) or set(antecedent) != ANTECEDENT_KEYS:
            raise ContinuityError(
                f"update.evidence[{index}].antecedent must be null or an object "
                f"with exactly {sorted(ANTECEDENT_KEYS)}; got {antecedent!r}")
        if not _is_digest(antecedent.get("body_sha256")):
            raise ContinuityError(
                f"update.evidence[{index}].antecedent.body_sha256 must be 64 "
                f"lowercase hex; got {antecedent.get('body_sha256')!r}")
        evidence_ref = antecedent.get("evidence_id")
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ContinuityError(
                f"update.evidence[{index}].antecedent.evidence_id must be a "
                f"non-empty string; got {evidence_ref!r}")
    elif status == "invalidada":
        raise ContinuityError(
            f"update.evidence[{index}] is `invalidada` without `antecedent`: an "
            f"invalidation must name the evidence it supersedes (§2.5)")
    return {
        "id": evidence_id,
        "reference": {"path": path, "sha256": digest},
        "status": status,
        "reason": reason,
        "antecedent": _copy_antecedent(antecedent),
    }


def _copy_antecedent(antecedent: Any) -> dict[str, str] | None:
    if antecedent is None:
        return None
    return {
        "body_sha256": antecedent.get("body_sha256"),
        "evidence_id": antecedent.get("evidence_id"),
    }


def _evidence_history(chain: dict[str, Any]) -> dict[str, Any]:
    """The HISTORICAL reading of the declared evidence, OLDEST first.

    Returns the latest declared status per id, the latest entry per id and the
    `(body_sha256, evidence_id)` declarations of every walkable body — the
    entries themselves, so a transition can be checked against the identity it
    claims to supersede (§2.5/INV-7).

    This reading is compatible with legacy bodies on purpose: they stay readable
    and their declared evidence still informs status and identity. Whether a
    declaration may be CREDITED as an antecedent is a different question,
    decided by the caller against `chain["demonstrable"]` (§2.3.1).
    """
    status: dict[str, str] = {}
    declared: dict[tuple[str, str], dict[str, Any]] = {}
    latest: dict[str, dict[str, Any]] = {}
    for sha, body in reversed(chain["links"]):
        evidence = body.get("evidence")
        if not isinstance(evidence, list):
            continue
        for entry in evidence:
            if not isinstance(entry, dict):
                continue
            evidence_id = entry.get("id")
            if not isinstance(evidence_id, str) or not evidence_id:
                continue
            declared[(sha, evidence_id)] = entry
            latest[evidence_id] = entry
            declared_status = entry.get("status")
            if declared_status in EVIDENCE_STATUSES:
                status[evidence_id] = declared_status
    return {"status": status, "declared": declared, "latest": latest}


def _reference_of(entry: dict[str, Any]) -> dict[str, Any] | None:
    """The identity (safe path + digest) an evidence entry references."""
    reference = entry.get("reference")
    if not isinstance(reference, dict):
        return None
    return {"path": reference.get("path"), "sha256": reference.get("sha256")}


def _merged_evidence(update: dict[str, Any], head_body: dict[str, Any],
                     chain: dict[str, Any] | None) -> list[dict[str, Any]]:
    """§2.5/INV-7: an update that invalidates evidence keeps the other entries;
    an omitted `evidence` keeps the declared content; an empty list cannot
    retire evidence in silence; an invalidated identity never returns to
    `vigente`.

    The transition is validated against the ANTECEDENT ENTRY, not merely its
    existence: an invalidation conserves the identity of the evidence it
    invalidates (the antecedent's reference, never another one), and replacing a
    `vigente` entry's reference needs a new id plus a traceable antecedent.

    Only the DEMONSTRABLE chain accredits an antecedent (§2.3.1): the historical
    reading stays compatible with legacy bodies, but a body of non-demonstrable
    history —one whose walk trips over a `prev`-less ancestor— serves no
    antecedent.
    """
    declared = update.get("evidence")
    if declared is None:
        inherited = head_body.get("evidence")
        return list(inherited) if isinstance(inherited, list) else []
    if not isinstance(declared, list) or not declared:
        raise ContinuityError(
            "update.evidence must be a non-empty list of evidence entries: an "
            f"empty list cannot retire evidence in silence; got {declared!r}")
    chain = chain if chain is not None else {"links": [],
                                             "demonstrable": False,
                                             "unknowns": []}
    history = _evidence_history(chain)
    status = history["status"]
    latest = history["latest"]
    # §2.3.1/§2.5: the reading above is historical; ACCREDITATION is not. An
    # antecedent resolves only inside the demonstrable chain.
    demonstrable = bool(chain.get("demonstrable"))
    creditable_antecedents = history["declared"] if demonstrable else {}
    inherited = head_body.get("evidence")
    inherited = inherited if isinstance(inherited, list) else []
    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for entry in inherited:
        if not isinstance(entry, dict):
            continue
        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not evidence_id:
            continue
        merged[evidence_id] = entry
        order.append(evidence_id)
    seen: set[str] = set()
    for index, raw in enumerate(declared):
        entry = _evidence_entry(raw, index)
        evidence_id = entry["id"]
        if evidence_id in seen:
            raise ContinuityError(
                f"update.evidence declares the id {evidence_id!r} twice: an "
                f"evidence id is unique in the body (§2.5)")
        seen.add(evidence_id)
        antecedent = entry.get("antecedent")
        antecedent_entry: dict[str, Any] | None = None
        if antecedent is not None:
            key = (antecedent["body_sha256"], antecedent["evidence_id"])
            if not demonstrable:
                # §2.3.1: history that does not reach the genesis through
                # `prev` is not demonstrable, so it accredits NO antecedent —
                # even when the body exists, is readable and is the one the
                # antecedent names.
                detail = "; ".join(chain.get("unknowns") or []) \
                    or "la cadena no alcanza el génesis con el enlace histórico"
                raise ContinuityError(
                    f"update.evidence[{index}].antecedent {key!r} resolves to "
                    f"historia no demostrable ({detail}): un cuerpo legado sin "
                    f"`prev` no sirve de antecedente de evidencia "
                    f"(§2.3.1/§2.5)")
            antecedent_entry = creditable_antecedents.get(key)
            if antecedent_entry is None:
                raise ContinuityError(
                    f"update.evidence[{index}].antecedent {key!r} resolves to no "
                    f"evidence of this chain: an unknown antecedent is history "
                    f"that cannot be demonstrated (§2.5/§2.3.1)")
        previous = latest.get(evidence_id)
        previous_reference = _reference_of(previous) if previous is not None \
            else None
        if entry["status"] == "invalidada":
            # §2.5/INV-7: the invalidation CONSERVES the identity of the
            # evidence it invalidates — the entry its antecedent names, with
            # THAT reference. Another identity or another reference is not an
            # invalidation but a substitution in disguise.
            if antecedent["evidence_id"] != evidence_id:
                raise ContinuityError(
                    f"update.evidence[{index}] invalidates {evidence_id!r} with "
                    f"the antecedent of another identity "
                    f"({antecedent['evidence_id']!r}): an invalidation "
                    f"conserves the identity of the evidence it invalidates "
                    f"(§2.5/INV-7)")
            antecedent_reference = (
                _reference_of(antecedent_entry)
                if antecedent_entry is not None else None)
            if antecedent_reference is None or \
                    entry["reference"] != antecedent_reference:
                raise ContinuityError(
                    f"update.evidence[{index}] invalidates {evidence_id!r} with a "
                    f"reference that is not the antecedent's "
                    f"({entry['reference']!r} != {antecedent_reference!r}): the "
                    f"identity of the invalidated evidence is conserved, never "
                    f"recalculated (§2.5/INV-7)")
        if status.get(evidence_id) == "invalidada" and entry["status"] == "vigente":
            raise ContinuityError(REHABILITATED_MESSAGE.format(id=evidence_id))
        if entry["status"] != "invalidada" and previous_reference is not None \
                and entry["reference"] != previous_reference:
            # §2.5/INV-7: replacing the reference of a declared identity is a
            # SUBSTITUTION, and a substitution needs a NEW id plus a traceable
            # antecedent; it is never done in place.
            raise ContinuityError(
                f"update.evidence[{index}] replaces the evidence {evidence_id!r} "
                f"with another reference ({entry['reference']!r} != "
                f"{previous_reference!r}) keeping its id: a substitution needs a "
                f"NEW id and an antecedent that explains it (§2.5/INV-7)")
        if evidence_id not in merged:
            order.append(evidence_id)
        merged[evidence_id] = entry
    return [merged[evidence_id] for evidence_id in order if evidence_id in merged]


# ------------------------------------------------------------------ checkpoint


def _load_head(root: Path, execution_id: str) -> dict[str, Any] | None:
    path = _head_path(root, execution_id)
    if not path.is_file():
        return None
    document = _read_json(path, "checkpoint head")
    if not isinstance(document, dict):
        raise ContinuityError("checkpoint head must be a JSON object")
    return document


def _checkpoint_envelope(exec_context: dict[str, Any], body: dict[str, Any],
                         body_sha256: str, body_bytes: bytes,
                         references: list[dict[str, str]],
                         head: dict[str, Any] | None,
                         max_bytes: int) -> dict[str, Any]:
    seq = 1
    prev: str | None = None
    if head is not None:
        previous_seq = head.get("seq")
        if isinstance(previous_seq, int) and not isinstance(previous_seq, bool):
            seq = previous_seq + 1
        prev = head.get("body_sha256")
    return {
        "schema_version": SCHEMA_VERSION,
        "checkpoint": CHECKPOINT_CONTRACT,
        "execution_id": exec_context["execution_id"],
        "packet_id": body.get("packet_id"),
        "attempt": body.get("attempt"),
        # 003-007 (P6/D5): `record` travels in the envelope too (P6).
        "record": body.get("record"),
        "seq": seq,
        "body_sha256": body_sha256,
        "prev_checkpoint_sha256": prev,
        "references": references,
        "bytes": len(body_bytes),
        "max_bytes": max_bytes,
        "no_op": False,
    }


def _same_key(head: dict[str, Any], body: dict[str, Any]) -> bool:
    return (head.get("execution_id") == body.get("execution_id")
            and head.get("packet_id") == body.get("packet_id")
            and head.get("attempt") == body.get("attempt"))


def _published_link(chain: dict[str, Any] | None,
                    body: dict[str, Any]) -> tuple[int, str, dict[str, Any]] | None:
    """§4.4/PC-04: the link of the demonstrable chain whose content — everything
    but the single top-level `prev` — IS this body, or None.

    Content equality already implies identity agreement (the key lives inside
    the body), so a hit means the write is ALREADY published: a replay, never a
    new effect."""
    if chain is None:
        return None
    for index, (sha, published) in enumerate(chain["links"]):
        if _content_without_prev(published) == body:
            return index, sha, published
    return None


def _replay_envelope(exec_context: dict[str, Any], head: dict[str, Any],
                     chain: dict[str, Any],
                     link: tuple[int, str, dict[str, Any]],
                     limit: int) -> dict[str, Any]:
    """The envelope of a replay: the identity of the PUBLISHED link it
    recognized (never a new write), with `no_op` set."""
    index, sha, published = link
    head_seq = head.get("seq")
    seq = head_seq - index if isinstance(head_seq, int) else None
    prev = published.get(PREV_FIELD)
    return {
        "schema_version": SCHEMA_VERSION,
        "checkpoint": CHECKPOINT_CONTRACT,
        "execution_id": exec_context["execution_id"],
        "packet_id": published.get("packet_id"),
        "attempt": published.get("attempt"),
        "record": published.get("record"),
        "seq": seq,
        "body_sha256": sha,
        "prev_checkpoint_sha256": (
            prev.get("checkpoint_sha256") if isinstance(prev, dict) else None),
        "references": published.get("references", []),
        "bytes": len(_canonical_bytes(published)),
        "max_bytes": (head.get("max_bytes") if index == 0
                      and isinstance(head.get("max_bytes"), int) else limit),
        "no_op": True,
    }


def plan_write(root: Path, execution_context_path: Path, update: dict[str, Any],
               *, command: str = "checkpoint",
               max_bytes: int | None = None,
               state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compute — never publish — the atomic writes of ONE continuity write.

    007-006 (review-002) needs the checkpoint of a retirement to travel in the
    SAME transaction as the state: the caller asks for the plan and publishes
    `writes` together with its own artifacts, so a failure leaves the chain and
    the state untouched. `writes` is empty for an identical repetition (a
    no-op), and `envelope` is the document the CLI prints.

    Returns `{"writes": [(path, bytes), …], "envelope": {…}}`: the canonical
    body first and the head that chains it second.

    It is a PROGRAMMATIC border, not a presentation of the CLI: the §4.4 order
    is applied here too (§5 PC-01/PC-02/PC-06), because a caller that plans a
    write never passes through `main()`.

    `state` is the project state the operation is being decided against: the
    caller may pass the state it is about to publish, so a resume that removes
    the unit from the suspension registry is judged on the state it creates,
    not on the one it replaces (the same fact the CLI reads from disk)."""
    # 010-000 PC-02: the same project declared relatively, absolutely or through
    # a symlink is one root — the plan is computed against its resolution, so
    # every planned destination and every membership check agrees.
    root = cdad_packet._canonical_project_root(root)
    exec_context = _load_execution_context(root, execution_context_path)
    return _plan_write(root, exec_context, update, command=command,
                       max_bytes=max_bytes,
                       context_path=execution_context_path, state=state)


def _plan_write(root: Path, exec_context: dict[str, Any], update: dict[str, Any],
                *, command: str,
                max_bytes: int | None,
                context_path: Path | None = None,
                state: dict[str, Any] | None = None) -> dict[str, Any]:
    """`plan_write` over an already loaded execution context (the CLI reads it
    once, exactly as before)."""
    # §4.4 (1): identity, owner and the necessary evidence — always, before any
    # decision. The suspension is NOT checked here: it belongs to step (3).
    unit = _accredited_unit(root, context_path, exec_context, state=state)
    _require_unit_identity(unit)
    _require_key_fields(update)
    _require_content_fields(update)
    record = "begin" if command == "begin" else "checkpoint"
    declared_changes = _declared_changes(update)

    limit = max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES
    references = _digest_references(root, update.get("references"))
    execution_id = exec_context["execution_id"]
    head = _load_head(root, execution_id)
    chain = _chain_links(root, execution_id, head) if head is not None else None
    head_body = chain["links"][0][1] if chain is not None else {}

    # 007-003 (§2.5/§2.6): `evidence` is merged over the context being extended
    # (an omitted field keeps the declaration); `changes` is inherited only
    # when the update does not declare it.
    evidence = _merged_evidence(update, head_body, chain) \
        if "evidence" in update else (
            list(head_body["evidence"])
            if isinstance(head_body.get("evidence"), list) else None)
    changes = declared_changes if declared_changes is not None else (
        list(head_body["changes"])
        if isinstance(head_body.get("changes"), list) else None)

    body = _canonical_body(exec_context, update, references, record,
                           changes=changes, evidence=evidence)

    # §4.4/PC-04: the REPLAY is recognized by the evidence that already exists —
    # the same content (minus the single top-level `prev`) published anywhere in
    # the demonstrable chain. It is decided BEFORE any eligibility of a new
    # effect: an identical `checkpoint` repeated after the active state advanced
    # converges without adding a link, and the same write is never published
    # twice. The order (replay → conflict → new effect) and the three outcomes
    # are the shared core's (`decide_continuity_write`); this border only
    # GATHERS the facts: the published link, the head's key and content.
    replay = _published_link(chain, body)
    same_key = (replay is None and head is not None and _same_key(head, body))
    decision = cdad_lifecycle.decide_continuity_write(
        command=command, published=replay is not None,
        head_key_matches=same_key,
        head_record=head.get("record") if head is not None else None,
        head_decisions=head_body.get("decisions"),
        key={"execution_id": execution_id, "packet_id": body.get("packet_id"),
             "attempt": body.get("attempt")},
        head_sha256=head.get("body_sha256") if head is not None else None,
        attempted_sha256=_sha256(_canonical_bytes(body)))
    if decision.facts.get("outcome") == cdad_lifecycle.REPLAY:
        return {"writes": [],
                "envelope": _replay_envelope(exec_context, head, chain, replay,
                                             limit)}
    if not decision.allowed:
        raise ContinuityError(decision.message())

    # 008-004 PC-01/PC-06 (§Referencias y nuevo begin): the facts left a NEW
    # effect of a CDAD commission, so its packet must verify and no `contract`
    # reference may fall inside the packet's own write_scope. Both rules govern
    # new effects only: the replay recognized above already converged and never
    # reaches this point. Nothing has been written yet.
    if command == "begin":
        admission = _admit_packet(root, body.get("packet_id"), state)
        if admission is not None:
            _refuse_covered_contract_references(
                root, body.get("packet_id"), admission[0], admission[1],
                references)

    # §4.4 (3): the facts left a NEW effect, so its eligibility is required —
    # authority first, then the suspension of the ACCREDITED owner (§4.3): a
    # replay recognized above never reaches this point and therefore never asks
    # for an authority or a unit that the repetition does not need.
    _require_current_authority(exec_context)
    _require_owner_operable(unit)

    # §2.3.1: only AFTER deciding to publish is the link derived from the
    # validated head, the complete body serialized, the byte limit applied and
    # the physical digest computed. `body` (the compared content) is copied so
    # the published body differs from it in exactly one field: `prev`.
    if head is None:
        prev_link: dict[str, Any] | None = None
    else:
        prev_link = {
            "checkpoint_sha256": head.get("body_sha256"),
            "seq": head.get("seq"),
        }
    published = dict(body)
    published[PREV_FIELD] = prev_link
    body_bytes = _canonical_bytes(published)
    if len(body_bytes) > limit:
        raise ContinuityError(
            f"projection exceeds --max-bytes {limit} "
            f"(canonical body is {len(body_bytes)} bytes); refusing to truncate")
    body_sha256 = _sha256(body_bytes)

    envelope = _checkpoint_envelope(exec_context, body, body_sha256, body_bytes,
                                    references, head, limit)
    head_bytes = (json.dumps(envelope, indent=2, sort_keys=True,
                             ensure_ascii=False) + "\n").encode("utf-8")
    return {
        "writes": [(_body_path(root, execution_id, body_sha256), body_bytes),
                   (_head_path(root, execution_id), head_bytes)],
        "envelope": envelope,
    }


def _run_write(command: str, args: argparse.Namespace, *,
               state: dict[str, Any] | None = None) -> int:
    # 010-000 PC-01/PC-02: the handler works over the resolution of the root it
    # was given, exactly as the CLI border already decides its guards over it.
    root = cdad_packet._canonical_project_root(Path(args.project_root))
    context_path = _resolve(root, args.execution_context)
    exec_context = _load_execution_context(root, context_path)
    update = _read_json(_resolve(root, args.update), "update")
    if not isinstance(update, dict):
        raise ContinuityError("update must be a JSON object")
    plan = _plan_write(root, exec_context, update, command=command,
                       max_bytes=args.max_bytes, context_path=context_path,
                       state=state)
    for path, data in plan["writes"]:
        _write_synced(path, data)
    _emit(plan["envelope"])
    return 0



# ------------------------------------------------------- verify-begin (007-003)


def _published_request(root: Path, packet_id: str) -> dict[str, Any]:
    """The canonical request of a packet already published by `prepare`."""
    directory = root.joinpath(*PACKETS_TREE, packet_id)
    path = directory / REQUEST_NAME
    if not path.is_file():
        raise ContinuityError(
            f"unknown packet {packet_id!r}: no published request under "
            f"{directory} — the continuity precondition needs a packet "
            f"published by `prepare`")
    document = _read_json(path, "packet request")
    if not isinstance(document, dict):
        raise ContinuityError("the packet request must be a JSON object")
    return document


def _active_packet(root: Path, packet_id: str) -> None:
    """§2.1: the active packet must correspond to the request being checked."""
    path = root / STATE_REL_PATH
    if not path.is_file():
        raise ContinuityError(
            f"no active packet: the project state {STATE_REL_PATH} is missing "
            f"(continuidad)")
    state = _read_json(path, "project state")
    active = state.get("active_packet") if isinstance(state, dict) else None
    active_id = active.get("id") if isinstance(active, dict) else None
    if active_id != packet_id:
        raise ContinuityError(
            f"el paquete activo no corresponde al request: el estado declara "
            f"{active_id!r} y la comprobación de continuidad exige "
            f"{packet_id!r} (§2.1)")


def _published_commission_trace(directory: Path) -> bool:
    """008-004 PC-01 (review fix): the control-plane trace of a packet that
    `prepare` published.

    A legacy continuity write leaves no entry under the packets tree at all;
    a directory that `prepare` created (its request, its canonical text, or any
    other file of the transaction) is evidence that the id names a CDAD
    commission — a legacy operation never writes there.
    """
    try:
        return directory.is_dir() and any(directory.iterdir())
    except OSError:
        return True


def _admit_packet(root: Path, packet_id: Any,
                  state: dict[str, Any] | None = None
                  ) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """008-004 PC-01/PC-03 (§Orden y efectos): the packet a NEW begin cites must
    verify before the write is planned, when it is a published CDAD commission.

    An id with NO trace under the packets tree is not a CDAD commission — there
    is nothing to admit and the legacy continuity path (003-004/003-007) is
    untouched. A commission whose `REQUEST.json` is missing is NOT legacy: its
    published trace proves the id was meant to be a CDAD packet, so an
    INCOMPLETE commission is refused before persisting instead of being admitted
    through the legacy route. A published one whose `PACKET.md` is absent,
    marker-less, unclosed or altered is refused the same way, with the shared
    verifier's diagnostic, having written nothing.
    """
    if not isinstance(packet_id, str) or not packet_id:
        return None
    directory = root.joinpath(*PACKETS_TREE, packet_id)
    request_path = directory / REQUEST_NAME
    if not request_path.is_file():
        if not _published_commission_trace(directory):
            return None
        raise ContinuityError(
            f"the begin is refused: packet {packet_id!r} was published under "
            f"{directory} but its {REQUEST_NAME} is missing — an incomplete CDAD "
            f"commission has no validated request to compare the packet against, "
            f"so it authorizes nothing and is never resumed as legacy continuity "
            f"(008-004 PC-01)")
    try:
        return cdad_packet.verify_published_packet(root, packet_id, state=state)
    except cdad_packet.PolicyError as exc:
        raise ContinuityError(f"the begin is refused: {exc}") from exc


def _refuse_covered_contract_references(
        root: Path, packet_id: str, request: dict[str, Any],
        execution_document: dict[str, Any],
        references: list[dict[str, Any]]) -> None:
    """008-004 PC-06 (§Referencias y nuevo begin): a NEW begin whose `contract`
    reference is covered by the packet's write_scope is refused before
    persisting, naming the reference and the incompatible selector.

    Only `contract` references are compared: a `living` one keeps its meaning
    (its divergence never becomes a P1 by itself). The coverage is decided by
    `cdad_packet._scope_contains`, the existing owner of the classes, roots and
    policy — never by comparing path strings.
    """
    contract = request.get("contract")
    contract_path = contract.get("path") if isinstance(contract, dict) else None
    contract_dir = (Path(contract_path).parent.as_posix()
                    if isinstance(contract_path, str) and contract_path else ".")
    policy = execution_document.get("path_policy")
    policy = policy if isinstance(policy, dict) else {}
    scopes = request.get("write_scope")
    scopes = scopes if isinstance(scopes, list) else []
    for reference in references:
        if not isinstance(reference, dict):
            continue
        if reference.get("class") != "contract":
            continue
        rel = reference.get("path")
        if not isinstance(rel, str) or not rel:
            continue
        for selector in scopes:
            if not isinstance(selector, dict):
                continue
            try:
                covered = cdad_packet._scope_contains(
                    selector, rel, contract_dir, policy, root)
            except cdad_packet.PolicyError as exc:
                raise ContinuityError(
                    f"reference {rel!r} cannot be compared with the write_scope "
                    f"of packet {packet_id!r}: {exc}") from exc
            if covered:
                raise ContinuityError(
                    f"reference {rel!r} (class contract) is covered by the "
                    f"write_scope selector "
                    f"{json.dumps(selector, sort_keys=True)} of packet "
                    f"{packet_id!r}: a contract reference must not be writable by "
                    f"the packet that cites it, and it is not reclassified "
                    f"automatically — refusing the begin before persisting "
                    f"(008-004 PC-06)")


def verify_begin(project_root: Path, execution_context_path: Path,
                 packet: Any, attempt: Any) -> dict[str, Any]:
    """§2.1: the pre-transport proof that a `begin` of THIS execution, packet
    and continuity attempt is the current head. Read-only: it writes nothing
    and a rejection names the condition with rc≠0 (the CLI's concern).

    It proves identity between context, request, head and body; the head's
    `record` (`begin`), the body integrity and the walkable cadena; the absence
    of split-brain; a current authority with admissible references; and the
    active packet that corresponds to the request. A historical `begin` under
    those identifiers is NOT enough: the CURRENT head must be that `begin`, so
    a later checkpoint (or a begin of another packet/attempt) never authorizes
    a new transport.
    """
    root = Path(project_root)
    exec_context = _load_execution_context(root, execution_context_path)
    execution_id = exec_context["execution_id"]
    packet_id = _safe_segment(packet, "packet")
    if not _is_int(attempt) or attempt < 1:
        raise ContinuityError(
            f"--attempt must be a positive integer (the continuity attempt, NOT "
            f"the textual --attempt-id); got {attempt!r}")
    request = _published_request(root, packet_id)
    if request.get("execution_id") != execution_id:
        raise ContinuityError(
            f"ejecución discordante: el request del paquete declara "
            f"execution_id={request.get('execution_id')!r} y el contexto "
            f"{execution_id!r} (continuidad)")
    if request.get("packet_id") != packet_id:
        raise ContinuityError(
            f"paquete discordante: el request declara packet_id="
            f"{request.get('packet_id')!r} y la comprobación exige "
            f"{packet_id!r} (continuidad)")
    head = _load_head(root, execution_id)
    if head is None:
        raise ContinuityError(
            f"no hay `begin` vigente para la ejecución {execution_id!r}: la "
            f"cabeza de continuidad no existe — escriba `begin --attempt "
            f"{attempt}` antes de transportar el paquete {packet_id!r} "
            f"(continuidad)")
    chain = _chain_links(root, execution_id, head)
    if not chain["demonstrable"]:
        # §2.1/§2.3.1 (review-001 BLOCKING 1): a `begin` is credited only over a
        # history demonstrated from the head to the genesis. A legacy ancestor
        # without `prev` stays READABLE and may still receive new links, but it
        # cannot accredit a transport — the close rejects the same chain.
        detail = "; ".join(chain["unknowns"]) or "historia no demostrable"
        raise ContinuityError(
            f"cadena no demostrable: {detail} — el `begin` no se acredita sobre "
            f"historia que no alcanza el génesis con el enlace histórico; el "
            f"transporte se rechaza sin efectos (§2.1/§2.3.1)")
    body = chain["links"][0][1]
    if head.get("record") != "begin" or body.get("record") != "begin":
        raise ContinuityError(
            f"la cabeza vigente no es el `begin` de este transporte: record="
            f"{head.get('record')!r} en seq {head.get('seq')!r}; un checkpoint "
            f"posterior no habilita un transporte nuevo (continuidad)")
    if head.get("packet_id") != packet_id or body.get("packet_id") != packet_id:
        raise ContinuityError(
            f"la cabeza de continuidad es de otro paquete ("
            f"{head.get('packet_id')!r}), no de {packet_id!r}: el `begin` de "
            f"otro paquete no habilita este transporte (continuidad)")
    if head.get("attempt") != attempt or body.get("attempt") != attempt:
        raise ContinuityError(
            f"la cabeza de continuidad es de otro intento (attempt="
            f"{head.get('attempt')!r}), no de attempt={attempt!r}: el `begin` "
            f"histórico de otro intento no habilita este transporte "
            f"(continuidad)")
    _detect_split_brain(root, execution_id, packet_id)
    _require_current_authority(exec_context)
    _reference_reports(root, body.get("references"), body)
    _active_packet(root, packet_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "verify": "begin",
        "execution_id": execution_id,
        "packet_id": packet_id,
        "attempt": attempt,
        "body_sha256": head.get("body_sha256"),
        "seq": head.get("seq"),
    }


# --------------------------------------------------- checkpoint-receipt (007-003)


def execution_context_path(project_root: Path, execution_id: str) -> Path:
    """The published context of an execution (001's convention, reused)."""
    return Path(project_root).joinpath(
        *CONTINUITY_TREE, _safe_segment(execution_id, "execution_id"),
        "execution.json")


def continuity_state(project_root: Path, execution_id: str) -> str:
    """`present` when the execution ever wrote continuity, `absent` otherwise.

    Only the STATE is classified here, never an authorization: a reception in a
    project that never started a continuity chain has nothing to close (007-001
    and 007-002 stay usable), while an existing chain is always the authority
    the common close must respect.
    """
    directory = _continuity_dir(Path(project_root).resolve(), execution_id)
    return "present" if directory.is_dir() else "absent"


# 007-003 §2.2 (enmienda 2026-10-24): the SCOPE of the mandatory integer. An
# execution WITH continuity —a head for that `execution_id`, or a context that
# DECLARES continuity— may not transport nor register without it; an execution
# WITHOUT continuity proceeds and the omission is DECLARED, never silent.
CONTINUITY_PRESENT = "present"
CONTINUITY_ABSENT = "absent"
CONTINUITY_FIELD = "continuity"


def _declares_continuity(document: Any) -> bool:
    """Whether a context DOCUMENT declares continuity.

    Declared shape (an additive field, never inferred from a path): a
    `continuity` entry at the top level or under `execution`, worth an object,
    `true`, or a non-empty string other than the explicit `absent` family. A
    context that says nothing does NOT declare it.
    """
    if not isinstance(document, dict):
        return False
    for candidate in (document, document.get("execution")):
        if not isinstance(candidate, dict):
            continue
        value = candidate.get(CONTINUITY_FIELD)
        if isinstance(value, dict):
            return True
        if value is True:
            return True
        if isinstance(value, str) and value.strip():
            return value.strip().lower() not in {
                CONTINUITY_ABSENT, "none", "no", "false", "never"}
    return False


def continuity_presence(project_root: Path, execution_id: Any,
                        exec_context: dict[str, Any] | None = None) -> str:
    """§2.2 (enmienda): does THIS execution have continuity?

    `present` when a continuity head exists for the `execution_id` or the
    execution context declares continuity; `absent` otherwise. An identity that
    cannot even be located resolves `present` (fail closed: an unprovable
    absence never relaxes the obligation).
    """
    root = Path(project_root)
    try:
        segment = _safe_segment(execution_id, "execution_id")
    except ContinuityError:
        return CONTINUITY_PRESENT
    if _head_path(root, segment).is_file():
        return CONTINUITY_PRESENT
    context = exec_context
    if context is None:
        path = execution_context_path(root, segment)
        if path.is_file():
            try:
                context = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                context = None
    return CONTINUITY_PRESENT if _declares_continuity(context) \
        else CONTINUITY_ABSENT


def historical_continuity(payload: bytes | None) -> str | None:
    """§2.2 (review-001 BLOCKING 3): the `continuity` declaration a DURABLE
    attempt record carries, verbatim.

    It is historical evidence of the registration, never a value recomputed from
    the current presence: recognizing a byte-identical repetition must preserve
    the record and its bytes. `None` when the record declares nothing.
    """
    if not payload:
        return None
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    if not isinstance(document, dict):
        return None
    provenance = document.get("provenance")
    if not isinstance(provenance, dict):
        return None
    value = provenance.get(CONTINUITY_FIELD)
    return value if isinstance(value, str) and value else None


def _durable_receipt(project_root: Path,
                     receipt_path: Path) -> dict[str, Any]:
    """§2.3: validate the receipt with the SAME criteria as `validate-receipt`
    (reused, never re-implemented) before anything is written."""
    try:
        import cdad_result  # local: cdad_result imports this module
        receipt = cdad_result._load_json(receipt_path, "receipt")
        final_dir = cdad_result._final_dir(
            project_root, receipt.get("execution_id"),
            receipt.get("packet_id"))
        if not final_dir.is_dir():
            raise cdad_result.ResultError(
                f"durable result not found for the receipt: {final_dir}")
        cdad_result._verify_durable(final_dir, receipt)
    except (ValueError, OSError) as exc:
        raise ContinuityError(
            f"el recibo durable {receipt_path} no valida (el cierre de "
            f"continuidad no escribe): {exc}") from exc
    return receipt


def _canonical_path(project_root: Path, path: Path) -> str:
    """§2.3.2: the durable path RESOLVED and normalized (absolute canonical of
    the producer, symlinks resolved, project-relative when it lives inside)."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError:
        return resolved.as_posix()


def _receipt_reference(project_root: Path,
                       raw: Any) -> tuple[str, str]:
    """§2.3.2: `(normalized_receipt_path, receipt_sha256)` of a receipt
    argument; symlinks, `..` segments and the raw argument text are NOT the
    identity."""
    candidate = Path(str(raw))
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve()
    try:
        digest = _sha256(resolved.read_bytes())
    except OSError as exc:
        raise ContinuityError(
            f"no se puede leer el recibo {resolved}: {exc}") from exc
    return _canonical_path(project_root, resolved), digest


def _chain_closes(chain: dict[str, Any], execution_id: str, packet_id: str,
                  attempt: int) -> list[tuple[str, dict[str, Any]]]:
    """§2.3.2/§2.3.3: the closes of the key `(execution_id, packet, attempt)`
    that belong to the demonstrable cadena — nothing else counts."""
    found: list[tuple[str, dict[str, Any]]] = []
    for sha, body in chain["links"]:
        if not isinstance(body.get(RECEIPT_CHECKPOINT_FIELD), dict):
            continue
        if (body.get("execution_id"), body.get("packet_id"),
                body.get("attempt")) != (execution_id, packet_id, attempt):
            continue
        found.append((sha, body))
    return found


def _close_envelope(body: dict[str, Any], body_sha256: str,
                    max_bytes: int) -> dict[str, Any]:
    prev = body.get(PREV_FIELD)
    return {
        "schema_version": SCHEMA_VERSION,
        "checkpoint": CHECKPOINT_CONTRACT,
        "execution_id": body.get("execution_id"),
        "packet_id": body.get("packet_id"),
        "attempt": body.get("attempt"),
        "record": body.get("record"),
        "seq": prev.get("seq", 0) + 1 if isinstance(prev, dict) else 1,
        "body_sha256": body_sha256,
        "prev_checkpoint_sha256": (
            prev.get("checkpoint_sha256") if isinstance(prev, dict) else None),
        "references": body.get("references", []),
        "bytes": len(_canonical_bytes(body)),
        "max_bytes": max_bytes,
        "no_op": False,
    }


RECEIPT_DECISION = {
    "decision": (
        "recepción mecánica del recibo durable (checkpoint-receipt)"),
    "rationale": (
        "el recibo existe y valida contra su payload durable: se registra la "
        "recepción MECÁNICA del efecto — no es aprobación semántica, no "
        "materializa, no dispone y no repite transporte ni recepción (§2.3)"),
}


def _closing_body(exec_context: dict[str, Any], head_body: dict[str, Any],
                  head: dict[str, Any], packet_id: str, attempt: int,
                  receipt_reference: dict[str, str]) -> dict[str, Any]:
    """§2.3: the close preserves the goal, decisions, uncertainties, budget and
    evidence of the context it closes and adds the receipt reference plus the
    founded decision of MECHANICAL reception."""
    decisions = list(head_body.get("decisions") or [])
    decisions.append(dict(RECEIPT_DECISION))
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "execution_id": exec_context["execution_id"],
        "packet_id": packet_id,
        "attempt": attempt,
        # A close is a new link of the chain: `checkpoint` (never a divergent
        # head under the key, never a transport).
        "record": "checkpoint",
        "goal": head_body.get("goal"),
        "authority": head_body.get("authority", _authority(exec_context)),
        "decisions": decisions,
        "uncertainties": list(head_body.get("uncertainties") or []),
        "next_action": (
            "recibo recibido mecánicamente; no repetir despacho/recepción; "
            "revisar el resultado sin presumir aprobación"),
        "references": list(head_body.get("references") or []),
        RECEIPT_CHECKPOINT_FIELD: receipt_reference,
        PREV_FIELD: {
            "checkpoint_sha256": head.get("body_sha256"),
            "seq": head.get("seq"),
        },
    }
    if "budget" in head_body:
        body["budget"] = head_body.get("budget")
    for field in ("changes", "evidence"):
        if isinstance(head_body.get(field), list):
            body[field] = list(head_body[field])
    return body


def close_durable_receipt(project_root: Path, receipt_path: Path, attempt: Any,
                          *, execution_context: Path | None = None,
                          packet: str | None = None,
                          max_bytes: int | None = None) -> dict[str, Any]:
    """§2.3/§2.3.2/§2.3.3: the ONE common close of every re-entry.

    Normative order — recognize first, authorize after: validate the receipt,
    normalize its path and verify the execution/packet identity; verify the
    integrity of the head and of the cadena used as proof; and only THEN look
    for a close of `(execution_id, packet, attempt)` **exclusively in the
    demonstrable cadena**:

    * it exists and `(normalized path, digest)` is equal ⇒ success without
      writing (no `begin` head, active packet or current authority required);
    * it exists with a different content ⇒ rejection (the existing close is
      named and no second close is added); several closes for one key ⇒
      unicity violation;
    * it does not exist ⇒ the close may be added only when the head keeps that
      key and a complete `begin` with `record="begin"` and that key is
      reachable from the head without crossing a key change; a current
      authority is required. Another packet/attempt in the head is a rejection
      (advanced continuity), never a rewind. `verify-begin` does NOT apply here:
      it stays exclusive of the new transport (§2.1).
    """
    root = Path(project_root).resolve()
    if not _is_int(attempt) or attempt < 1:
        raise ContinuityError(
            f"--continuity-attempt must be a positive integer (the continuity "
            f"attempt is NEVER inferred from the textual --attempt-id); got "
            f"{attempt!r}")
    resolved_receipt = _resolve(root, str(receipt_path)).resolve()
    receipt = _durable_receipt(root, resolved_receipt)
    execution_id = _safe_segment(receipt.get("execution_id"),
                                 "receipt.execution_id")
    receipt_packet = _safe_segment(receipt.get("packet_id"),
                                   "receipt.packet_id")
    packet_id = _safe_segment(packet if packet is not None else receipt_packet,
                              "packet")
    if receipt_packet != packet_id:
        raise ContinuityError(
            f"el recibo pertenece a otro paquete ({receipt_packet!r}), no a "
            f"{packet_id!r}: la identidad del cierre no coincide (continuidad)")
    context_path = (Path(execution_context) if execution_context is not None
                    else execution_context_path(root, execution_id))
    exec_context = _load_execution_context(root, context_path)
    if exec_context["execution_id"] != execution_id:
        raise ContinuityError(
            f"el recibo pertenece a otra ejecución ({execution_id!r}); el "
            f"contexto es {exec_context['execution_id']!r} (continuidad)")
    receipt_normalized_path, receipt_digest = _receipt_reference(
        root, resolved_receipt)
    reference = {"path": receipt_normalized_path, "sha256": receipt_digest}

    head = _load_head(root, execution_id)
    if head is None:
        raise ContinuityError(
            f"no hay cadena de continuidad para cerrar en la ejecución "
            f"{execution_id!r}: falta el `begin` que acredita el cierre "
            f"(continuidad)")
    chain = _chain_links(root, execution_id, head)
    if not chain["demonstrable"]:
        detail = "; ".join(chain["unknowns"]) or "historia no demostrable"
        raise ContinuityError(
            f"cadena no demostrable: {detail} — el cierre no se acredita sobre "
            f"historia que no alcanza la cabeza (§2.3.1)")

    # §4.4 (1): identity, accredited owner and the necessary evidence — always,
    # before the close decides anything else (a contradiction is rejected even
    # when the receipt would be a replay).
    unit = _accredited_unit(root, context_path, exec_context)
    _require_unit_identity(unit)
    existing = _chain_closes(chain, execution_id, packet_id, attempt)
    # §4.4: the order replay → conflict → new effect, and the rule that says
    # which one these facts produce, belong to the shared core
    # (`decide_continuity_close`). This border GATHERS the facts of its domain:
    # the closes the demonstrable chain proves, each with its normalized receipt
    # path and digest.
    facts: list[dict[str, Any]] = []
    for close_sha, close_body in existing:
        marker = close_body[RECEIPT_CHECKPOINT_FIELD]
        close_path = _canonical_path(
            root, _resolve(root, str(marker.get("path"))))
        facts.append({"sha256": close_sha, "path": close_path,
                      "digest": marker.get("sha256")})
    identical = (len(facts) == 1
                 and facts[0]["path"] == receipt_normalized_path
                 and facts[0]["digest"] == receipt_digest)
    decision = cdad_lifecycle.decide_continuity_close(
        closes=facts, identical=identical,
        receipt_path=receipt_normalized_path, receipt_digest=receipt_digest)
    if decision.facts.get("outcome") == cdad_lifecycle.REPLAY:
        close_sha, close_body = existing[0]
        envelope = _close_envelope(
            close_body, close_sha,
            max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES)
        envelope["no_op"] = True
        return envelope
    if not decision.allowed:
        raise ContinuityError(decision.message())

    key = (execution_id, packet_id, attempt)
    if (head.get("execution_id"), head.get("packet_id"),
            head.get("attempt")) != key:
        raise ContinuityError(
            f"continuidad adelantada: la cabeza vigente es de "
            f"(execution_id={head.get('execution_id')!r}, "
            f"packet_id={head.get('packet_id')!r}, attempt="
            f"{head.get('attempt')!r}) y el cierre pendiente es de "
            f"(execution_id={execution_id!r}, packet_id={packet_id!r}, "
            f"attempt={attempt!r}); no se rebobina ni se reemplaza la cabeza "
            f"(§2.4)")
    begin_found = False
    for sha, body in chain["links"]:
        if (body.get("execution_id"), body.get("packet_id"),
                body.get("attempt")) != key:
            raise ContinuityError(
                f"continuidad adelantada: la cadena atraviesa un cambio de "
                f"clave en el cuerpo {sha[:12]}… (otro paquete o intento) antes "
                f"de alcanzar el `begin` de (packet_id={packet_id!r}, "
                f"attempt={attempt!r}); un `begin` histórico no autoriza "
                f"rebobinar ni cerrar sobre otro intento (§2.3.3)")
        if body.get("record") == "begin":
            begin_found = True
            break
    if not begin_found:
        raise ContinuityError(
            f"no hay `begin` íntegro (record=\"begin\") para "
            f"(packet_id={packet_id!r}, attempt={attempt!r}) alcanzable desde la "
            f"cabeza: sin esa prueba el cierre no se agrega (continuidad)")
    # §4.4 (3): the facts left a NEW close, so its eligibility is required —
    # the current authority AND the suspension of the ACCREDITED owner (§4.3).
    # A close recognized as a replay above never reaches this point.
    _require_current_authority(exec_context)
    _require_owner_operable(unit)
    _reference_reports(root, chain["links"][0][1].get("references"),
                       chain["links"][0][1])

    body = _closing_body(exec_context, chain["links"][0][1], head, packet_id,
                         attempt, reference)
    body_bytes = _canonical_bytes(body)
    limit = max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES
    if len(body_bytes) > limit:
        raise ContinuityError(
            f"el cierre excede --max-bytes {limit} "
            f"(el cuerpo canónico mide {len(body_bytes)} bytes); no se trunca")
    body_sha256 = _sha256(body_bytes)
    envelope = _close_envelope(body, body_sha256, limit)
    _write_synced(_body_path(root, execution_id, body_sha256), body_bytes)
    _write_synced(_head_path(root, execution_id),
                  (json.dumps(envelope, indent=2, sort_keys=True,
                              ensure_ascii=False) + "\n").encode("utf-8"))
    return envelope


# ------------------------------------------------------------------ references/role


def _load_policy(root: Path) -> dict[str, Any]:
    document = _read_json(root / POLICY_REL_PATH, "policy")
    if not isinstance(document, dict):
        raise ContinuityError("policy must be a JSON object")
    return document


def _require_policy_for_role(root: Path, role: str | None) -> dict[str, Any]:
    """R-B2: `--role` requires the project policy; without it classification
    would fail open and leak implementation material. Fail closed instead."""
    if role is None:
        return {}
    policy_path = root / POLICY_REL_PATH
    if not policy_path.is_file():
        raise ContinuityError(
            f"--role {role!r} requires the project policy {POLICY_REL_PATH} "
            f"(missing at {policy_path}); refusing to classify references "
            "fail-open (R-B2)")
    return _load_policy(root)


def _policy_entries(policy: dict[str, Any], *keys: str) -> list[str]:
    path_policy = policy.get("path_policy")
    path_policy = path_policy if isinstance(path_policy, dict) else {}
    entries: list[str] = []
    for key in keys:
        value = path_policy.get(key)
        if not isinstance(value, list):
            continue
        entries.extend(item.strip().strip("/") for item in value
                       if isinstance(item, str) and item.strip())
    return entries


def _is_under(path: str, target: str) -> bool:
    target = target.strip("/")
    if not target:
        return False
    return path == target or path.startswith(target + "/")


def _is_implementation_reference(path: str, policy: dict[str, Any]) -> bool:
    """P5/B2: classification comes ONLY from the policy's declared roots."""
    roots = _policy_entries(policy, "implementation_roots", "implementation_files")
    return any(_is_under(path, root) for root in roots)


def _visible_references(references: list[dict[str, Any]], role: str | None,
                        policy: dict[str, Any]) -> list[dict[str, Any]]:
    if role is None or role in IMPLEMENTATION_PRIVILEGED_ROLES:
        return references
    return [reference for reference in references
            if not _is_implementation_reference(str(reference.get("path", "")),
                                                policy)]


# ------------------------------------------------------------------ verification


def _load_body(root: Path, execution_id: str,
               body_sha256: Any) -> tuple[dict[str, Any], bytes]:
    """P1: a stored body must digest to the digest that names it. The file name
    IS the content digest (content-addressed), so any byte-level change is a
    tamper even when it is invisible to JSON canonicalization."""
    if not isinstance(body_sha256, str) or not body_sha256:
        raise ContinuityError("body_sha256 missing from the checkpoint head")
    body_file = _body_path(root, execution_id, body_sha256)
    if not body_file.is_file():
        raise ContinuityError(
            f"body_sha256 {body_sha256} does not match any stored canonical "
            "body (checkpoint body is missing or altered)")
    raw = body_file.read_bytes()
    actual = _sha256(raw)
    if actual != body_sha256:
        raise ContinuityError(
            f"checkpoint body tamper: {body_file.name} digests {actual} but "
            f"the head declares body_sha256 {body_sha256} (stale/altered "
            "store); refusing to continue (no --allow-stale, O3)")
    try:
        body = json.loads(raw.decode("utf-8"))
    except ValueError as exc:
        raise ContinuityError(
            f"invalid JSON in canonical body {body_file}") from exc
    if not isinstance(body, dict):
        raise ContinuityError(
            f"the canonical body {body_file} is not a JSON object")
    return body, raw


def _verify_body(root: Path, execution_id: str,
                 head: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    """P1: the stored body must digest to the digest named by the head."""
    return _load_body(root, execution_id, head.get("body_sha256"))



def _verify_chain(root: Path, execution_id: str, head: dict[str, Any]) -> None:
    prev = head.get("prev_checkpoint_sha256")
    if prev is None:
        return
    if not isinstance(prev, str) or not prev:
        raise ContinuityError("prev_checkpoint_sha256 is not a valid digest")
    prev_file = _body_path(root, execution_id, prev)
    if not prev_file.is_file():
        raise ContinuityError(
            f"prev_checkpoint_sha256 {prev} is broken: no preceding checkpoint "
            "with that body digest exists")
    actual = _sha256(prev_file.read_bytes())
    if actual != prev:
        raise ContinuityError(
            f"prev_checkpoint_sha256 {prev} does not match the preceding "
            f"checkpoint body (digests {actual})")


def _require_head_coherence(execution_id: str, head: dict[str, Any],
                            body: dict[str, Any]) -> None:
    """§2.3.1: the envelope describes ITS body — identity, position and link.
    A discrepancy is rejected and never repaired automatically."""
    if head.get("execution_id") != execution_id \
            or body.get("execution_id") != execution_id:
        raise ContinuityError(
            f"cadena incoherente: la cabeza o su cuerpo no pertenecen a la "
            f"ejecución {execution_id!r}")
    for field in ("packet_id", "attempt", "record"):
        if head.get(field) != body.get(field):
            raise ContinuityError(
                f"cadena incoherente: la cabeza declara {field}="
                f"{head.get(field)!r} y su cuerpo declara {field}="
                f"{body.get(field)!r}; la cabeza no describe ese cuerpo")
    if body.get("record") == "reanchor":
        if body.get(PREV_FIELD) is not None or head.get("seq") != 1 \
                or head.get("prev_checkpoint_sha256") is not None:
            raise ContinuityError("reanclaje incoherente: debe ser génesis seq 1")
        return
    if PREV_FIELD not in body:
        # Legacy body: its link cannot be proven. Readable, never demonstrable.
        return
    prev = body.get(PREV_FIELD)
    if prev is None:
        if head.get("seq") != 1 or head.get("prev_checkpoint_sha256") is not None:
            raise ContinuityError(
                "cadena incoherente: el génesis (cuerpo con `prev: null`) debe "
                f"ser seq 1 sin predecesor; la cabeza declara seq="
                f"{head.get('seq')!r} y prev_checkpoint_sha256="
                f"{head.get('prev_checkpoint_sha256')!r}")
        return
    if not isinstance(prev, dict) or set(prev) != PREV_LINK_KEYS:
        raise ContinuityError(
            f"cadena incoherente: `prev` del cuerpo debe ser null o un objeto "
            f"{sorted(PREV_LINK_KEYS)}; visto {prev!r}")
    if head.get("prev_checkpoint_sha256") != prev.get("checkpoint_sha256"):
        raise ContinuityError(
            "cadena incoherente: `head.prev_checkpoint_sha256` y "
            f"`body.prev.checkpoint_sha256` discrepan "
            f"({head.get('prev_checkpoint_sha256')!r} != "
            f"{prev.get('checkpoint_sha256')!r})")
    if head.get("seq") != prev.get("seq", 0) + 1:
        raise ContinuityError(
            "cadena incoherente: la cabeza declara seq="
            f"{head.get('seq')!r} y su cuerpo `prev.seq`={prev.get('seq')!r}; "
            "el enlace debe crecer en 1")


def _chain_links(root: Path, execution_id: str,
                 head: dict[str, Any]) -> dict[str, Any]:
    """§2.3.1: the walk from the head to the genesis through `prev`.

    Returns `{"links": [(sha, body)…] (head first), "demonstrable": bool,
    "unknowns": […]}`. A body that digests to its name but whose `prev` is
    missing (legacy) or whose link position disagrees stops the demonstration:
    legacy bodies stay READABLE, they simply do not prove the chain. A `prev`
    that is present and incoherent is a violation, not a missing proof."""
    _verify_chain(root, execution_id, head)
    body_sha256 = head.get("body_sha256")
    if not _is_digest(body_sha256):
        raise ContinuityError(
            "checkpoint head declares no valid body_sha256: the cadena is not "
            "verifiable")
    expected_seq = head.get("seq")
    if not _is_int(expected_seq) or expected_seq < 1:
        raise ContinuityError(
            f"checkpoint head declares an invalid `seq` {expected_seq!r}: the "
            "cadena position is not verifiable")
    links: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    sha: Any = body_sha256
    while True:
        if sha in seen:
            raise ContinuityError(
                f"cadena incoherente: la cadena se cicla en {str(sha)[:12]}…")
        seen.add(sha)
        body, _ = _load_body(root, execution_id, sha)
        if not links:
            _require_head_coherence(execution_id, head, body)
        links.append((sha, body))
        if PREV_FIELD not in body:
            return {
                "links": links,
                "demonstrable": False,
                "unknowns": [
                    f"historia no demostrable: el cuerpo {sha[:12]}… no declara "
                    f"`prev` (legado); no acredita un cierre ni sirve de "
                    f"antecedente (§2.3.1)"],
            }
        prev = body.get(PREV_FIELD)
        if prev is None:
            if expected_seq != 1:
                raise ContinuityError(
                    f"cadena incoherente: el cuerpo {sha[:12]}… declara "
                    f"`prev: null` (génesis) pero la cadena espera la posición "
                    f"{expected_seq}")
            if body.get("record") == "reanchor":
                _validate_reanchor_body(root, execution_id, body)
            return {"links": links, "demonstrable": True,
                    "unknowns": (["historia anterior conservada, no demostrable"]
                                 if body.get("record") == "reanchor" else [])}
        if not isinstance(prev, dict) or set(prev) != PREV_LINK_KEYS:
            raise ContinuityError(
                f"cadena incoherente: `prev` del cuerpo {sha[:12]}… debe ser "
                f"null o un objeto {sorted(PREV_LINK_KEYS)}; visto {prev!r}")
        previous_sha = prev.get("checkpoint_sha256")
        previous_seq = prev.get("seq")
        if not _is_digest(previous_sha):
            raise ContinuityError(
                f"cadena incoherente: `prev.checkpoint_sha256` del cuerpo "
                f"{sha[:12]}… no es un digest sha256")
        if not _is_int(previous_seq) or previous_seq != expected_seq - 1:
            raise ContinuityError(
                f"cadena incoherente: `prev.seq` del cuerpo {sha[:12]}… debe "
                f"decrecer en 1 (esperado {expected_seq - 1}, visto "
                f"{previous_seq!r})")
        sha, expected_seq = previous_sha, previous_seq


def _validate_reanchor_body(root: Path, execution_id: str,
                            body: dict[str, Any]) -> None:
    anchor = body.get("legacy_anchor")
    inventory = body.get("pre_anchor_bodies")
    if not isinstance(anchor, dict) or anchor.get("execution_id") != execution_id \
            or not _is_digest(anchor.get("head_sha256")) \
            or not _is_int(anchor.get("head_seq")) or anchor["head_seq"] < 1:
        raise ContinuityError("reanclaje inválido: legacy_anchor incoherente")
    if not isinstance(anchor.get("reason"), str) or not anchor["reason"].strip():
        raise ContinuityError("reanclaje inválido: motivo vacío")
    if not isinstance(inventory, list) or inventory != sorted(set(inventory)) \
            or any(not _is_digest(item) for item in inventory):
        raise ContinuityError("reanclaje inválido: inventario no canónico")
    for digest in inventory:
        raw = _body_path(root, execution_id, digest).read_bytes()
        if _sha256(raw) != digest:
            raise ContinuityError(f"cuerpo archivado corrupto: {digest}")
        try:
            archived = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError) as exc:
            raise ContinuityError(f"cuerpo archivado ilegible: {digest}") from exc
        if not isinstance(archived, dict) or archived.get("execution_id") != execution_id:
            raise ContinuityError(f"cuerpo archivado de otra ejecución: {digest}")


def _legacy_inventory(root: Path, execution_id: str) -> list[str]:
    directory = _continuity_dir(root, execution_id) / "bodies"
    result = []
    if directory.is_dir():
        for path in sorted(directory.glob("*.json")):
            digest = path.stem
            if not _is_digest(digest):
                continue
            raw = path.read_bytes()
            if _sha256(raw) != digest:
                raise ContinuityError(f"cuerpo de continuidad corrupto: {digest}")
            try:
                doc = json.loads(raw.decode("utf-8"))
            except (UnicodeError, ValueError) as exc:
                raise ContinuityError(
                    f"cuerpo de continuidad ilegible: {digest}") from exc
            if isinstance(doc, dict) and doc.get("execution_id") == execution_id:
                result.append(digest)
    return sorted(set(result))


def _approval_fields(path: Path) -> dict[str, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContinuityError(f"no se puede leer aprobación: {exc}") from exc
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not match:
        raise ContinuityError("aprobación sin frontmatter válido")
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            value = value.strip().strip('"\'')
            if key in fields:
                raise ContinuityError(f"campo duplicado en aprobación: {key}")
            fields[key.strip()] = value
    required = ("reanchor_execution_id", "reanchor_head_sha256",
                "reanchor_inventory_sha256", "approved_by", "approved_at")
    if any(not fields.get(key) for key in required):
        raise ContinuityError("aprobación incompleta")
    try:
        date.fromisoformat(fields["approved_at"])
    except ValueError as exc:
        raise ContinuityError("approved_at debe ser YYYY-MM-DD") from exc
    return fields


def _run_reanchor(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    context = _load_execution_context(root, _resolve(root, args.execution_context))
    execution_id = context["execution_id"]
    head = _load_head(root, execution_id)
    if head is None:
        raise ContinuityError("no existe cabeza de continuidad para reanclar")
    old_sha = head.get("body_sha256")
    chain = _chain_links(root, execution_id, head)
    if chain["links"][-1][1].get("record") == "reanchor":
        original = chain["links"][-1][1]
        if args.dry_run:
            raise ContinuityError("la historia ya está reanclada")
        saved_approval = original["legacy_anchor"]["approval_ref"]
        approval_rel = _normalize_reference(args.approval_ref)
        approval_path = (root / approval_rel).resolve()
        if root not in approval_path.parents or not approval_path.is_file():
            raise ContinuityError("approval-ref debe ser archivo regular dentro del proyecto")
        if args.expected_head != original["legacy_anchor"]["head_sha256"] \
                or args.reason != original["legacy_anchor"]["reason"] \
                or approval_rel != saved_approval.get("path") \
                or _sha256(approval_path.read_bytes()) != saved_approval.get("sha256"):
            raise ContinuityError("conflicto: el reanclaje vigente tiene otros parámetros")
        anchor_sha, anchor_body = chain["links"][-1]
        anchor_raw = _canonical_bytes(anchor_body)
        field_size = max(0, len(_canonical_bytes({
            "pre_anchor_bodies": anchor_body["pre_anchor_bodies"]})) - 2)
        env = {"schema_version": SCHEMA_VERSION, "checkpoint": CHECKPOINT_CONTRACT,
               "execution_id": execution_id, "packet_id": anchor_body.get("packet_id"),
               "attempt": anchor_body.get("attempt"), "record": "reanchor", "seq": 1,
               "body_sha256": anchor_sha, "prev_checkpoint_sha256": None,
               "references": [], "bytes": len(anchor_raw),
               "max_bytes": DEFAULT_MAX_BYTES + field_size, "no_op": True,
               "legacy_anchor": anchor_body["legacy_anchor"],
               "pre_anchor_bodies": anchor_body["pre_anchor_bodies"],
               "pre_anchor_inventory_sha256": _sha256(
                   _canonical_bytes(anchor_body["pre_anchor_bodies"])),
               "idempotent": True}
        _emit(env); return 0
    current = _legacy_inventory(root, execution_id)
    body, _ = _verify_body(root, execution_id, head)
    if chain["demonstrable"]:
        raise ContinuityError("la cadena ya es demostrable; no se puede reanclar")
    if args.expected_head and args.expected_head != old_sha:
        raise ContinuityError("expected-head no coincide con la cabeza vigente")
    _require_reanchor_effect_free(root, execution_id, head.get("packet_id"))
    _require_reanchor_authority(root, context)
    inventory_sha = _sha256(_canonical_bytes(current))
    if args.dry_run:
        _emit({"execution_id": execution_id, "head_sha256": old_sha,
               "head_seq": head.get("seq"), "body_count": len(current),
               "pre_anchor_inventory_sha256": inventory_sha})
        return 0
    approval_rel = _normalize_reference(args.approval_ref)
    approval_path = (root / approval_rel).resolve()
    if not approval_path.is_file() or root not in approval_path.parents:
        raise ContinuityError("approval-ref debe ser archivo regular dentro del proyecto")
    fields = _approval_fields(approval_path)
    approval_sha = _sha256(approval_path.read_bytes())
    if fields["reanchor_execution_id"] != execution_id \
            or fields["reanchor_head_sha256"] != old_sha \
            or fields["reanchor_inventory_sha256"] != inventory_sha:
        raise ContinuityError("la aprobación no coincide con ejecución/cabeza/inventario")
    approval = {"path": approval_rel, "sha256": approval_sha}
    published = {"schema_version": SCHEMA_VERSION, "execution_id": execution_id,
                 "packet_id": body.get("packet_id"), "attempt": body.get("attempt"),
                 "record": "reanchor", "goal": body.get("goal"),
                 "authority": _authority(context), "decisions": [],
                 "uncertainties": [], "next_action": None, "references": [],
                 "legacy_anchor": {"execution_id": execution_id,
                                   "head_sha256": old_sha, "head_seq": head.get("seq"),
                                   "reason": args.reason, "approval_ref": approval},
                 "pre_anchor_bodies": current, "prev": None}
    raw = _canonical_bytes(published); digest = _sha256(raw)
    ordinary_limit = args.max_bytes if getattr(args, "max_bytes", None) is not None \
        else DEFAULT_MAX_BYTES
    if ordinary_limit < 1:
        raise ContinuityError("--max-bytes must be positive")
    field_size = max(0, len(_canonical_bytes({"pre_anchor_bodies": current})) - 2)
    without_inventory = dict(published)
    without_inventory.pop("pre_anchor_bodies")
    if len(_canonical_bytes(without_inventory)) > ordinary_limit:
        raise ContinuityError(
            f"reanchor body excluding inventory exceeds ordinary limit {ordinary_limit}")
    effective_limit = ordinary_limit + field_size
    if len(raw) > effective_limit:
        raise ContinuityError(
            f"reanchor body exceeds effective --max-bytes {effective_limit} "
            f"(canonical body is {len(raw)} bytes)")
    if _load_head(root, execution_id) != head \
            or _legacy_inventory(root, execution_id) != current:
        raise ContinuityError("head or inventory changed before reanchor publication")
    env = {"schema_version": SCHEMA_VERSION, "checkpoint": CHECKPOINT_CONTRACT,
           "execution_id": execution_id, "packet_id": body.get("packet_id"),
           "attempt": body.get("attempt"), "record": "reanchor", "seq": 1,
           "body_sha256": digest, "prev_checkpoint_sha256": None,
           "references": [], "bytes": len(raw), "max_bytes": effective_limit,
           "no_op": False}
    _write_synced(_body_path(root, execution_id, digest), raw)
    _write_synced(_head_path(root, execution_id),
                  (json.dumps(env, indent=2, sort_keys=True) + "\n").encode())
    env.update({"legacy_anchor": published["legacy_anchor"],
                "pre_anchor_bodies": current,
                "pre_anchor_inventory_sha256": inventory_sha,
                "idempotent": False})
    _emit(env); return 0


def _reference_digest(root: Path, reference: dict[str, Any]) -> str | None:
    """Read-time digest of a reference, or None when the file is absent (no
    digest is ever fabricated — invariant 2). With `fields`, the digest covers
    the canonical projection (V2/S5); without it, the complete file bytes (P4).
    An unreadable/non-JSON file under `fields` yields no reliable digest."""
    rel = reference.get("path")
    target = root / str(rel)
    if not target.is_file():
        return None
    fields = reference.get("fields")
    if isinstance(fields, list) and fields:
        try:
            document = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(document, dict):
            return None
        return _projection_digest(document, fields)
    try:
        return _sha256(target.read_bytes())
    except OSError:
        return None


def _reference_report(root: Path, reference: dict[str, Any], *,
                      legacy_body: bool) -> dict[str, Any]:
    """003-007 §3/Envolturas + D6/O-1: the read envelope entry for one stored
    reference. A body WITHOUT `record` is legacy: its reference class is
    resolved BY COMPARISON (D6) — intact → verified `contract`;
    divergent/absent → reported with `legacy: true`. A body WITH `record`
    (written by this CLI) whose reference lacks a recognizable `class` falls
    closed to `contract` (P3/O-1), never legacy."""
    rel = reference.get("path")
    expected = reference.get("sha256")
    declared = reference.get("class")
    legacy = legacy_body and declared not in REFERENCE_CLASSES
    klass = declared if declared in REFERENCE_CLASSES else "contract"
    current = _reference_digest(root, reference)
    if current is None:
        state = "missing"
    elif current == expected:
        state = "unchanged"
    else:
        state = "changed"
    report: dict[str, Any] = {
        "path": rel,
        "class": klass,
        "sha256": expected,
        "current_sha256": current,
        "state": state,
    }
    if legacy:
        report["legacy"] = True
    return report


def _reference_reports(root: Path, references: Any,
                       body: dict[str, Any]) -> list[dict[str, Any]]:
    """P1/P2/P7: report every stored reference; a declared `contract`
    reference that changed or vanished fails closed (rc!=0) naming the path and
    both digests. Legacy bodies (no `record` in the body, D6/O-1) and `living`
    references never block."""
    if not isinstance(references, list):
        raise ContinuityError("canonical body references must be a list")
    legacy_body = "record" not in body
    reports: list[dict[str, Any]] = []
    for reference in references:
        if not isinstance(reference, dict):
            raise ContinuityError("canonical body reference must be an object")
        report = _reference_report(root, reference, legacy_body=legacy_body)
        reports.append(report)
        if report.get("legacy") or report["class"] != "contract":
            continue
        if report["state"] == "unchanged":
            continue
        rel = report["path"]
        expected = report["sha256"]
        if report["state"] == "missing":
            raise ContinuityError(
                f"reference {rel!r} (class contract) is missing since the "
                f"checkpoint: expected {expected}; refusing to resume a "
                "divergent contract reference (P1, fail closed)")
        raise ContinuityError(
            f"reference {rel!r} (class contract) changed since the checkpoint "
            f"(P1, fail closed): expected {expected}, got "
            f"{report['current_sha256']}")
    return reports


# ------------------------------------------------------------------ reconcile


def _detect_split_brain(root: Path, execution_id: str, packet_id: str) -> None:
    """D7 (003-007 P6): bodies under the SAME key `(execution_id, packet_id,
    attempt)` that are NOT checkpoints (`record != "checkpoint"`: begins,
    legacy and orphan bodies) are divergent heads → escalate. A legitimate
    chain begin→checkpoint under one key (P5 append) is not a fork; the CLI
    never picks a winner and never deletes evidence."""
    bodies_dir = _continuity_dir(root, execution_id) / "bodies"
    if not bodies_dir.is_dir():
        return
    by_key: dict[tuple[Any, Any, Any], list[str]] = {}
    head = _load_head(root, execution_id)
    archived: set[str] = set()
    if head is not None:
        chain = _chain_links(root, execution_id, head)
        genesis = chain["links"][-1][1]
        if genesis.get("record") == "reanchor":
            archived = set(genesis.get("pre_anchor_bodies", []))
    for path in sorted(bodies_dir.glob("*.json")):
        if path.stem in archived:
            if _sha256(path.read_bytes()) != path.stem:
                raise ContinuityError(f"cuerpo archivado corrupto: {path.stem}")
            continue
        try:
            document = json.loads(path.read_bytes().decode("utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(document, dict):
            continue
        if document.get("execution_id") != execution_id \
                or document.get("packet_id") != packet_id:
            continue
        # P6: a checkpoint link is not a divergent head; only non-checkpoint
        # bodies (begins/legacy/orphans) count under one key.
        if document.get("record") == "checkpoint":
            continue
        if document.get("record") == "reanchor":
            continue
        key = (document.get("execution_id"), document.get("packet_id"),
               document.get("attempt"))
        by_key.setdefault(key, []).append(path.name)
    for key, names in by_key.items():
        if len(names) > 1:
            raise ContinuityError(
                "split-brain: divergent checkpoint heads for key "
                f"(execution_id={key[0]!r}, packet_id={key[1]!r}, "
                f"attempt={key[2]!r}): {sorted(names)}; escalate — the CLI "
                "never chooses a winner (D7)")


def _has_dispatch(root: Path, execution_id: str, packet_id: str) -> bool:
    dispatches = _dispatch_dir(root, execution_id)
    if not dispatches.is_dir():
        return False
    for path in sorted(dispatches.glob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(document, dict) and document.get("packet_id") == packet_id:
            return True
    return False


def _require_reanchor_effect_free(root: Path, execution_id: str,
                                 packet_id: str) -> None:
    """The CONSERVATIVE «no effect yet» criterion of the reanchor, shared with
    the retirement of a prepared packet (007-006 §Rechazos: the packet CLI
    consumes this same function and never a divergent detector).

    A signal that cannot be interpreted is INCONCLUSIVE, never absent: an
    unreadable dispatch record, a missing/discordant identity (also when the
    named packet has no published request in the examined scope), any result
    file, a materialization record and a disposition all block the operation."""
    state_path = root / STATE_REL_PATH
    state = _read_json(state_path, "project state") if state_path.is_file() else {}
    active = state.get("active_packet") if isinstance(state, dict) else None
    if not isinstance(active, dict) or active.get("id") != packet_id \
            or active.get("status") != "prepared":
        raise ContinuityError("the packet is not in prepared status")

    dispatch_dir = _dispatch_dir(root, execution_id)
    if dispatch_dir.is_dir():
        for path in sorted(dispatch_dir.glob("*.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, ValueError) as exc:
                raise ContinuityError(
                    f"inconclusive dispatch signal at {path}: {exc}") from exc
            if not isinstance(doc, dict):
                raise ContinuityError(f"inconclusive dispatch signal at {path}")
            recorded_execution = doc.get("execution_id")
            recorded_packet = doc.get("packet_id")
            if recorded_execution != execution_id \
                    or not isinstance(recorded_packet, str) or not recorded_packet.strip():
                raise ContinuityError(
                    f"inconclusive dispatch signal at {path}: missing or discordant identity")
            if recorded_packet == packet_id:
                raise ContinuityError("a dispatch is already registered for the packet")
            # 007-006 §Rechazos: a dispatch record of this execution whose
            # packet has NO published request in the project has an identity
            # that cannot be established in the EXAMINED scope — a record that
            # was renamed to another packet, or a stale/foreign one. It is
            # inconclusive, never "another packet's dispatch", so it blocks the
            # operation instead of reading as an absent effect (I3).
            if not (root.joinpath(*PACKETS_TREE, recorded_packet)
                    / REQUEST_NAME).is_file():
                raise ContinuityError(
                    f"inconclusive dispatch signal at {path}: the record names the "
                    f"packet {recorded_packet!r}, which has no published request "
                    f"({'/'.join(PACKETS_TREE)}/{recorded_packet}/{REQUEST_NAME}); "
                    f"its identity cannot be established in the examined scope")

    # The STRONGEST effect is reported first: a materialization (copies already
    # landed in the project) is further than a receipt or a staged file, and the
    # diagnostic must name the concrete state that blocks the operation
    # (007-006 §Rechazos: source and cause). Both orders reject; this one names
    # what actually happened when both signals are present.
    if _has_materialization(root, execution_id, packet_id):
        raise ContinuityError("a materialization is already registered for the packet")
    result_dir = _results_dir(root, execution_id, packet_id)
    if result_dir.is_dir() and any(path.is_file() for path in result_dir.rglob("*")):
        raise ContinuityError("a receipt/effect file already exists for the packet")

    disposition, causes = _disposition_signal(
        root, {"execution_id": execution_id}, execution_id, packet_id)
    if causes:
        raise ContinuityError("disposition is inconclusive: " + "; ".join(causes))
    if disposition is not None:
        raise ContinuityError("a disposition is already registered for the packet")


def _receipt_signal(root: Path, execution_id: str, packet_id: str,
                    ) -> tuple[str, dict[str, Any] | None, list[str]]:
    """`absent` | `unreadable` | `readable`. An unreadable or mismatched
    receipt is NOT a reliable signal: it stays `unreadable` so the caller
    reports `unknown` instead of fabricating success or failure (§2)."""
    path = _results_dir(root, execution_id, packet_id) / "receipt.json"
    if not path.is_file():
        return "absent", None, []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return "unreadable", None, [
            f"receipt unreadable at {path}: {exc.strerror or exc}"]
    try:
        document = json.loads(raw)
    except ValueError:
        return "unreadable", None, [
            f"receipt unreadable at {path}: invalid JSON (no reliable signal)"]
    if not isinstance(document, dict):
        return "unreadable", None, [
            f"receipt at {path} is not a JSON object (no reliable signal)"]
    if document.get("execution_id") != execution_id \
            or document.get("packet_id") != packet_id:
        return "unreadable", None, [
            f"receipt at {path} does not match execution_id/packet_id "
            "(no reliable signal)"]
    return "readable", document, []


def _has_materialization(root: Path, execution_id: str, packet_id: str) -> bool:
    mat_dir = _materialization_dir(root, execution_id, packet_id)
    if not mat_dir.is_dir():
        return False
    return any(mat_dir.glob("*.json"))


def _disposition_state(root: Path) -> tuple[Any, list[str]]:
    """007-002 §2.1.1: the ONLY source of a disposition is
    `docs/.cdad-state.json:stage_history`.

    A project without that file has no disposition (absence, indistinguishable
    from "never registered" — and never a diagnostic); a PRESENT state that
    cannot be read or decoded is reported as a cause, so absence is never
    disguised as illegibility nor the other way round (review-001 B2: a
    `UnicodeDecodeError` is an unreadable source, not an abort)."""
    path = root / STATE_REL_PATH
    if not path.is_file():
        return None, []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [
            f"the project state {STATE_REL_PATH} cannot be read "
            f"({exc.strerror or exc}): the disposition cannot be verified"]
    except UnicodeError:
        # review-001 B2: undecodable bytes are an ILLEGIBLE source, not an
        # abort — the envelope is preserved and the cause is reported.
        return None, [
            f"the project state {STATE_REL_PATH} is not decodable as UTF-8: "
            f"the disposition cannot be verified (no reliable signal)"]
    try:
        document = json.loads(raw)
    except ValueError:
        return None, [
            f"the project state {STATE_REL_PATH} is not valid JSON: the "
            f"disposition cannot be verified (no reliable signal)"]
    return document, []


def _execution_feature(exec_context: dict[str, Any], state: Any) -> str | None:
    """§4.2: the feature of the examined request, resolved by the shared core.

    The supplied binding competes with the evidence the project recorded instead
    of overriding it, and the active feature never substitutes the owner of a
    historical or suspended execution. A flat legacy context — no `execution`
    object at all — keeps its declared fallback to `state.active_feature`,
    explicitly and only there."""
    execution = exec_context.get("execution")
    if isinstance(execution, dict):
        decision = cdad_lifecycle.resolve_owner(
            supplied=execution.get("feature_id"),
            execution_id=exec_context.get("execution_id"),
            declared=_accredited_owner_sources(exec_context, state))
        return decision.facts.get("owner") if decision.allowed else None
    active = state.get("active_feature") if isinstance(state, dict) else None
    return active if isinstance(active, str) and active else None


def _disposition_signal(root: Path, exec_context: dict[str, Any],
                        execution_id: str, packet_id: str,
                        ) -> tuple[dict[str, Any] | None, list[str]]:
    """§2.2: the canonical disposition that resolved this dispatch, or `None`
    (with the causes that prevented selecting one).

    The selection itself is the packet CLI's (one decision, two consumers);
    this function only locates the source and the feature of the request."""
    state, causes = _disposition_state(root)
    if state is None:
        return None, causes
    feature_id = _execution_feature(exec_context, state)
    if feature_id is None:
        return None, causes
    signal, selection_causes = cdad_packet.disposition_selection(
        state, execution_id=execution_id, feature_id=feature_id,
        packet_id=packet_id)
    return signal, causes + selection_causes


def _classify(authority_state: str, receipt_state: str, dispatch: bool,
              closed: bool, disposition: dict[str, Any] | None = None,
              disposition_causes: list[str] | None = None,
              ) -> tuple[str, list[str]]:
    if authority_state == "expired":
        return "expired-authority", [
            "the HITL delegation is expired (D4): context may be rebuilt but "
            "no dispatch/materialize is authorized"]
    if receipt_state == "unreadable":
        return "unknown", [
            "a receipt is present but unreadable: no reliable signal, so "
            "neither success nor failure is fabricated (§2)"]
    if receipt_state == "readable":
        if closed:
            return "already-closed", [
                "a valid receipt plus a materialization journal exist: the "
                "work is already closed, no retrabajo (D6)"]
        return "received", [
            "a valid receipt exists: the effect is already received and must "
            "not be duplicated (D10); a receipt is not semantic approval "
            "(invariant 4)"]
    # 007-002 §2.2 (row 5): a dispatch with no receipt resolved by a canonical
    # disposition is `disposed` — an OBSERVED result, never an authorization to
    # repeat the effect (invariant 4).
    if disposition is not None:
        if dispatch:
            resolution = disposition.get("resolution")
            replaced_by = disposition.get("replaced_by")
            successor = (f" and declares {replaced_by!r} as its successor"
                         if replaced_by is not None else "")
            return "disposed", [
                f"a canonical disposition is registered for this dispatch "
                f"({resolution}{successor}): the recorded DECISION resolves a "
                f"dispatch that will not come back, and it authorizes NO "
                f"repeat of the predecessor's effect (repeat_effect=false; "
                f"invariant 4)"]
        # §2.2: a disposition alone never turns a request with no dispatch
        # evidence into `disposed`; the contradiction is reported as `unknown`.
        return "unknown", [
            "a canonical disposition is registered but the request has no "
            "dispatch evidence: the decision contradicts the dispatch it "
            "resolves, so nothing is fabricated (`disposed` and `not-started` "
            "are both withheld; 007-002 §2.2)"]
    if disposition_causes:
        # §2.2 (row 6): an unreadable, inconsistent or ambiguous disposition
        # source prevents a reliable determination; the causes travel in
        # `unknowns`.
        return "unknown", [
            "the disposition of this request cannot be determined reliably "
            "(unreadable, inconsistent or ambiguous record); its causes are "
            "reported in `unknowns` (007-002 §2.2)"]
    if dispatch:
        return "dispatched-unknown", [
            "a dispatch is recorded with no receipt: the session is not "
            "classified as a failure and repeating is not authorized "
            "(invariant 3)"]
    return "not-started", [
        "no dispatch and no receipt: the write-ahead head precedes any "
        "dispatch (P3/D6)"]


def _run_reconcile(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    exec_context = _load_execution_context(
        root, _resolve(root, args.execution_context))
    execution_id = exec_context["execution_id"]
    head = _load_head(root, execution_id)
    packet_id = _safe_segment(args.packet or (head or {}).get("packet_id"), "packet")
    report_list: list[dict[str, Any]] = []
    chain = None
    if head is not None:
        chain = _chain_links(root, execution_id, head)
        body = chain["links"][0][1]
        report_list = _reference_reports(root, body.get("references"), body)

    _detect_split_brain(root, execution_id, packet_id)

    authority_state = _authority_state(exec_context)
    receipt_state, receipt_doc, unknowns = _receipt_signal(
        root, execution_id, packet_id)
    dispatch = _has_dispatch(root, execution_id, packet_id)
    closed = _has_materialization(root, execution_id, packet_id)
    # 007-002 §2.2: the disposition is verified ALWAYS, so a signal that could
    # be proved is never lost to a higher-precedence classification; an
    # inconclusive source is a diagnostic, never a fabricated decision.
    disposition, disposition_causes = _disposition_signal(
        root, exec_context, execution_id, packet_id)
    unknowns.extend(disposition_causes)
    if chain is not None:
        unknowns.extend(item for item in chain.get("unknowns", []) if item not in unknowns)

    classification, reasons = _classify(
        authority_state, receipt_state, dispatch, closed, disposition,
        disposition_causes)

    # A (review-t2): `expired-authority` stays dominant, but the receipt /
    # materialization / dispatch facts travel in `signals` so the orchestrator
    # can tell "expired and already closed" from "expired with no effect".
    signals = {
        "receipt": {
            "state": receipt_state,
            "effect": "received" if receipt_state == "readable" else None,
            "semantic_status": (
                receipt_doc.get("semantic_status")
                if isinstance(receipt_doc, dict) else None),
        },
        "materialization": "closed" if closed else "open",
        "dispatch": "dispatched" if dispatch else "none",
        # 007-002 §2.2: ALWAYS present — `null` when no disposition could be
        # selected, the §2.2 object when one was verified.
        "disposition": disposition,
    }

    head_summary = None
    if head is not None:
        head_summary = {
            "seq": head.get("seq"),
            "body_sha256": head.get("body_sha256"),
        }
    authority = _authority_view(exec_context)

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "reconcile": RECONCILE_CONTRACT,
        "execution_id": execution_id,
        "packet_id": packet_id,
        "classification": classification,
        "repeat_effect": False,
        "escalate": False,
        "authority": authority,
        "head": head_summary,
        "references": report_list,
        "signals": signals,
        "reasons": reasons,
        # A (review-t2): unknowns are preserved ALWAYS, whatever the dominant
        # classification — an inconclusive signal is never hidden.
        "unknowns": unknowns,
    }
    _emit(envelope)
    return 0


# ------------------------------------------------------------------ trigger


def _is_int(value: Any) -> bool:
    """P6: only integers signal — `bool` is not a token count."""
    return isinstance(value, int) and not isinstance(value, bool)


def _collect_guard_attempts(root: Path, execution_id: str,
                            packet_id: str) -> list[dict[str, Any]]:
    """Durable recovery attempts for (execution, packet) under 003's
    `.cdad/executions/<id>/guards/**`, sorted by attempt. Mirrors
    `cdad_guard.py::_collect_attempts` (invariant 5: the 003 budget is REUSED,
    never redefined). Unreadable/foreign files are skipped, never fabricated.
    """
    guards_dir = root.joinpath(*CONTINUITY_TREE, execution_id, "guards")
    if not guards_dir.is_dir():
        return []
    attempts: list[dict[str, Any]] = []
    for path in sorted(guards_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(event, dict):
            continue
        if event.get("event") != GUARD_EVENT_CONTRACT:
            continue
        if event.get("packet_id") != packet_id:
            continue
        attempts.append({
            "attempt": event.get("attempt"),
            "cause": event.get("cause"),
            "session": event.get("session"),
            "at": event.get("at"),
        })
    attempts.sort(
        key=lambda item: item["attempt"]
        if isinstance(item["attempt"], int) else 0)
    return attempts


def _durable_budget(root: Path, execution_id: str,
                    packet_id: str) -> dict[str, Any]:
    """The 003 durable attempt budget, reported WITH its `source` path (P4)."""
    attempts = _collect_guard_attempts(root, execution_id, packet_id)
    source = Path(*CONTINUITY_TREE, execution_id, "guards").as_posix()
    return {"source": source, "consumed": len(attempts), "attempts": attempts}


def _frozen_budget(root: Path,
                   execution_id: str) -> tuple[dict[str, Any] | None,
                                               list[dict[str, Any]]]:
    """Budget snapshot frozen in the checkpoint body (D11) plus the reference
    reports, or `(None, [])` when there is no head / the head carries no
    snapshot. The head is verified (P1) before it is read, like
    `resume`/`reconcile`."""
    head = _load_head(root, execution_id)
    if head is None:
        return None, []
    body, _ = _verify_body(root, execution_id, head)
    _verify_chain(root, execution_id, head)
    reports = _reference_reports(root, body.get("references"), body)
    snapshot = body.get("budget")
    return (snapshot if isinstance(snapshot, dict) else None), reports


def _trigger_unknowns(snapshot: dict[str, Any] | None) -> list[str]:
    """P6/criterios 6, 7, 11: name every field that lacks a reliable integer
    signal, so `unknown` is explicit and never fabricated."""
    if not isinstance(snapshot, dict):
        return [
            "context_used_tokens: no runtime counter (no budget snapshot in "
            "the checkpoint head)",
            "context_limit: no runtime limit (no budget snapshot in the "
            "checkpoint head)",
        ]
    missing: list[str] = []
    used = snapshot.get("context_used_tokens")
    if not _is_int(used):
        missing.append(
            f"context_used_tokens: no integer counter reported (got {used!r})")
    limit = snapshot.get("context_limit")
    if not _is_int(limit):
        missing.append(
            f"context_limit: no integer limit reported (got {limit!r})")
    return missing


def _run_trigger(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    exec_context = _load_execution_context(
        root, _resolve(root, args.execution_context))
    execution_id = exec_context["execution_id"]
    # Cierre C: the packet id is a safe path segment BEFORE any read (a
    # traversal must fail closed, naming the field, never fabricate a source).
    packet_id = _safe_segment(args.packet, "packet")

    snapshot, report_list = _frozen_budget(root, execution_id)
    used = snapshot.get("context_used_tokens") \
        if isinstance(snapshot, dict) else None
    limit = snapshot.get("context_limit") \
        if isinstance(snapshot, dict) else None

    signal: str
    profile: dict[str, Any] | None = None
    context_source: str | None = None
    unknowns = _trigger_unknowns(snapshot)

    if unknowns:
        # No reliable counter+limit: `unknown` with nulls (P6/criterio 7).
        signal = "unknown"
        used = None
        limit = None
    else:
        source = snapshot.get("source")
        context_source = source if isinstance(source, str) else None
        profile = {
            "limit": limit,
            "reserve": PROFILE_RESERVE,
            "prepare_at": PROFILE_PREPARE_AT,
            "rotate_at": limit - PROFILE_RESERVE,
        }
        # Fronteras `>=` fijadas en RED: rotate at/over `limit - reserve`,
        # prepare at/over `prepare_at`, else ok.
        if used >= profile["rotate_at"]:
            signal = "rotate"
        elif used >= profile["prepare_at"]:
            signal = "prepare"
        else:
            signal = "ok"

    envelope = {
        "schema_version": SCHEMA_VERSION,
        # P6 literal: the key `trigger` carries the SIGNAL itself.
        "trigger": signal,
        "context_used_tokens": used,
        "context_limit": limit,
        "context_source": context_source,
        "profile": profile,
        "unknowns": unknowns,
        "references": report_list,
        "budget": _durable_budget(root, execution_id, packet_id),
    }
    _emit(envelope)
    return 0


# ------------------------------------------------------------------ resume


def _visible_evidence(evidence: Any, role: str | None,
                      policy: dict[str, Any]) -> list[dict[str, Any]]:
    """§2.6: the role filter reaches the evidence references with the SAME
    visibility rules as the existing references (policy, never the path name)."""
    if not isinstance(evidence, list):
        return []
    entries = [entry for entry in evidence if isinstance(entry, dict)]
    if role is None or role in IMPLEMENTATION_PRIVILEGED_ROLES:
        return entries
    visible: list[dict[str, Any]] = []
    for entry in entries:
        reference = entry.get("reference")
        path = reference.get("path") if isinstance(reference, dict) else None
        if isinstance(path, str) and _is_implementation_reference(path, policy):
            continue
        visible.append(entry)
    return visible


def _projection(body: dict[str, Any],
                exec_context: dict[str, Any], *,
                role: str | None = None,
                policy: dict[str, Any] | None = None) -> dict[str, Any]:
    """007-003 (§2.6): the L1 projection also emits `changes`/`evidence` with
    their explicit states. A body without them projects empty lists; nothing is
    inferred from references, decisions or logs, and no body is rewritten."""
    changes = body.get("changes")
    return {
        "goal": body.get("goal"),
        # D4/RU-1: the authority (with its CURRENT vigencia) is reconstructed
        # on demand from the state/context, never frozen stale in the body.
        "authority": _authority_view(exec_context),
        "decisions": body.get("decisions", []),
        "uncertainties": body.get("uncertainties", []),
        "next_action": body.get("next_action"),
        "changes": list(changes) if isinstance(changes, list) else [],
        "evidence": _visible_evidence(body.get("evidence"), role,
                                      policy if policy is not None else {}),
    }


def _run_resume(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    exec_context = _load_execution_context(
        root, _resolve(root, args.execution_context))
    execution_id = exec_context["execution_id"]
    role = getattr(args, "role", None)
    policy = _require_policy_for_role(root, role)

    max_bytes = args.max_bytes if args.max_bytes is not None else DEFAULT_MAX_BYTES
    head = _load_head(root, execution_id)

    if head is None:
        # O1/criterio 4: no persisted active memory and no checkpoint yet is
        # not an error — nothing to resume is a valid, empty projection.
        projection = _projection({}, exec_context, role=role, policy=policy)
        projection_bytes = _canonical_bytes(projection)
        if len(projection_bytes) > max_bytes:
            raise ContinuityError(
                f"projection exceeds --max-bytes {max_bytes} "
                f"(is {len(projection_bytes)} bytes); refusing to truncate")
        envelope: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "record": RECORD_CONTRACT,
            "state": "no-checkpoint",
            "execution_id": execution_id,
            "projection": projection,
            "bytes": len(projection_bytes),
            "max_bytes": max_bytes,
        }
        if role is not None:
            envelope["role"] = role
        _emit(envelope)
        return 0

    # 007-003 (§2.3.1): `resume` verifies the whole walkable cadena, so a
    # `prev` altered without its digest, or a head/body link that disagrees,
    # fails closed without repair. Legacy bodies stay readable.
    chain = _chain_links(root, execution_id, head)
    body = chain["links"][0][1]
    _detect_split_brain(root, execution_id, body.get("packet_id"))
    report_list = _reference_reports(root, body.get("references"), body)

    projection = _projection(body, exec_context, role=role, policy=policy)
    projection_bytes = _canonical_bytes(projection)
    if len(projection_bytes) > max_bytes:
        raise ContinuityError(
            f"projection exceeds --max-bytes {max_bytes} "
            f"(is {len(projection_bytes)} bytes); refusing to truncate")

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "record": RECORD_CONTRACT,
        "execution_id": execution_id,
        "packet_id": head.get("packet_id"),
        "attempt": head.get("attempt"),
        "seq": head.get("seq"),
        "body_sha256": head.get("body_sha256"),
        "prev_checkpoint_sha256": head.get("prev_checkpoint_sha256"),
        "references": _visible_references(report_list, role, policy),
        "bytes": len(projection_bytes),
        "max_bytes": max_bytes,
        "projection": projection,
    }
    if role is not None:
        envelope["role"] = role
    _emit(envelope)
    return 0


# ------------------------------------------------------------------ CLI


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cdad_continuity")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_write(name: str, help_text: str) -> None:
        command = sub.add_parser(name, help=help_text)
        command.add_argument("--project-root", required=True)
        command.add_argument("--execution-context", required=True)
        command.add_argument("--update")
        command.add_argument("--max-bytes", type=int, default=None)
        command.add_argument("--json", action="store_true")

    add_write("begin", "write-ahead a checkpoint (idempotent on an identical head)")
    add_write("checkpoint", "append a new checkpoint link to the chain")

    reanchor = sub.add_parser("reanchor", help="explicitly re-anchor legacy history")
    reanchor.add_argument("--project-root", required=True)
    reanchor.add_argument("--execution-context", required=True)
    reanchor.add_argument("--expected-head")
    reanchor.add_argument("--approval-ref")
    reanchor.add_argument("--reason")
    reanchor.add_argument("--max-bytes", type=int, default=None)
    reanchor.add_argument("--dry-run", action="store_true")
    reanchor.add_argument("--json", action="store_true")

    verify = sub.add_parser(
        "verify-begin",
        help="read-only pre-transport proof of the current `begin` (007-003)")
    verify.add_argument("--project-root", required=True)
    verify.add_argument("--execution-context", required=True)
    verify.add_argument("--packet", required=True)
    verify.add_argument("--attempt", type=int, required=True,
                        help="the continuity attempt (an INTEGER; never the "
                             "textual --attempt-id of the dispatch ledger)")
    verify.add_argument("--json", action="store_true")

    close = sub.add_parser(
        "checkpoint-receipt",
        help="the common close of a durable receipt (007-003, idempotent)")
    close.add_argument("--project-root", required=True)
    close.add_argument("--execution-context", required=True)
    close.add_argument("--packet", required=True)
    close.add_argument("--attempt", type=int, required=True,
                       help="the continuity attempt (an INTEGER; never inferred "
                            "from the textual --attempt-id)")
    close.add_argument("--receipt", required=True)
    close.add_argument("--max-bytes", type=int, default=None)
    close.add_argument("--json", action="store_true")

    reconcile = sub.add_parser(
        "reconcile", help="reconcile the dispatched work (read-only)")
    reconcile.add_argument("--project-root", required=True)
    reconcile.add_argument("--execution-context", required=True)
    reconcile.add_argument("--packet", default=None)
    reconcile.add_argument("--json", action="store_true")

    resume = sub.add_parser("resume", help="verify and render the active projection")
    resume.add_argument("--project-root", required=True)
    resume.add_argument("--execution-context", required=True)
    resume.add_argument("--role", default=None)
    resume.add_argument("--max-bytes", type=int, default=None)
    resume.add_argument("--json", action="store_true")

    trigger = sub.add_parser(
        "trigger", help="read the context signal (read-only, P6/D5)")
    trigger.add_argument("--project-root", required=True)
    trigger.add_argument("--execution-context", required=True)
    trigger.add_argument("--packet", required=True)
    trigger.add_argument("--runtime", default="opencode")
    trigger.add_argument("--json", action="store_true")

    return parser


def _managed_context_without_state(root: Path, context_path: Path,
                                   context: dict[str, Any],
                                   identity) -> bool:
    """Classify managed contexts from their location or matching execution record.

    The identity is never read with a local precedence (008-003 §4.2): it is the
    one the shared core already resolved for this context."""
    executions_root = (root / ".cdad" / "executions").resolve()
    try:
        context_path.resolve().relative_to(executions_root)
        return True
    except ValueError:
        pass

    if not identity.allowed:
        return False
    execution_id = identity.facts["execution_id"]
    record_path = executions_root / execution_id / "execution.json"
    if not record_path.exists():
        return False
    if not record_path.is_file():
        raise ContinuityError(
            f"managed execution record is not a file: {record_path}")
    record = _read_json(record_path, "managed execution record")
    record_identity = cdad_lifecycle.resolve_execution_identity(
        declared=(record.get("execution") or {}).get("id")
        if isinstance(record, dict) and isinstance(record.get("execution"), dict)
        else None,
        flat=record.get("execution_id") if isinstance(record, dict) else None)
    if not record_identity.allowed \
            or record_identity.facts["execution_id"] != execution_id:
        raise ContinuityError(
            f"managed execution record identity is incoherent: {record_path}")
    return True


def _accredited_owner_sources(context: dict[str, Any],
                              state: Any) -> list[tuple[Any, Any]]:
    """The `(execution_id, feature_id)` pairs the ACCREDITED sources declare.

    The supplied context declares one (it is what the caller wants examined);
    the state binding and the suspension registry declare the ones the project
    recorded. §4.2: the supplied identity is not authority over the owner, so it
    competes with the recorded ones instead of overriding them."""
    pairs: list[tuple[Any, Any]] = []
    execution = context.get("execution")
    if isinstance(execution, dict):
        pairs.append((execution.get("id") or context.get("execution_id"),
                      execution.get("feature_id")))
    if not isinstance(state, dict):
        return pairs
    binding = state.get("execution")
    if isinstance(binding, dict):
        pairs.append((binding.get("id"), binding.get("feature_id")))
    registry = state.get("suspended_units")
    if isinstance(registry, dict):
        for record in registry.values():
            unit_state = record.get("unit_state") if isinstance(record, dict) else None
            if not isinstance(unit_state, dict):
                continue
            bound = unit_state.get("execution")
            bound_id = bound.get("id") if isinstance(bound, dict) else None
            if isinstance(bound, dict):
                pairs.append((bound_id, bound.get("feature_id")))
            if isinstance(unit_state.get("active_feature"), str):
                pairs.append((bound_id, unit_state["active_feature"]))
    return pairs


def _accredited_unit(root: Path, context_path: Path | None,
                     context: dict[str, Any],
                     *, state: dict[str, Any] | None = None) -> dict[str, Any]:
    """§4.2 + PC-01: the facts and the decision of the unit this context names.

    Gathers what this border owns — the supplied context, its canonical location
    and the project state (`state` when the caller is deciding a not-yet
    published state, the one on disk otherwise) — and asks the shared core for
    the concordant identity and the owner ACCREDITED by that evidence (never the
    supplied identity). The suspension is NOT decided here (§4.4 step 3):
    `_require_owner_operable` asks for it only once the operation is known to be
    a new effect."""
    identity = cdad_lifecycle.resolve_execution_identity(
        declared=(context.get("execution") or {}).get("id")
        if isinstance(context.get("execution"), dict) else None,
        flat=context.get("execution_id"),
        located=_located_execution_id(root, context_path)
        if context_path is not None else None)
    if state is not None:
        state_facts: Any = state
    else:
        state_path = root / STATE_REL_PATH
        state_facts = None
        if state_path.exists():
            state_facts = cdad_packet._load_json(state_path, "project state")
        elif context_path is not None and _managed_context_without_state(
                root, context_path, context, identity):
            raise ContinuityError(
                "project state is missing for managed execution "
                f"{identity.facts.get('execution_id')!r}; refusing continuity "
                f"write")
    execution = context.get("execution")
    supplied_feature = (execution.get("feature_id")
                        if isinstance(execution, dict) else None)
    owner = cdad_lifecycle.resolve_owner(
        supplied=supplied_feature,
        execution_id=identity.facts.get("execution_id"),
        declared=_accredited_owner_sources(context, state_facts))
    return {
        "decision": cdad_lifecycle.combine(identity, owner),
        "owner": owner,
        "supplied_feature": supplied_feature,
        "suspended": (state_facts.get("suspended_units")
                      if isinstance(state_facts, dict) else None),
    }


def _owner_decision(unit: dict[str, Any]) -> cdad_lifecycle.Decision:
    """§4.3/PC-02: the suspension decision of EVERY owner the evidence
    accredits for this execution — never of the supplied identity alone."""
    owner = unit["owner"]
    accredited_owner = owner.facts.get("accredited_owner")
    candidates = owner.facts.get("accredited_candidates") or ()
    return cdad_lifecycle.combine(
        *(cdad_lifecycle.require_owner_operable(owner=candidate,
                                                suspended=unit["suspended"])
          for candidate in tuple(candidates) + (accredited_owner,
                                                unit["supplied_feature"])))


def _require_unit_identity(unit: dict[str, Any]) -> None:
    """§4.4 (1)/PC-01: identity and the evidence of the unit — always, before
    the operation decides anything else (including a replay). An operation that
    is illegitimate for more than one reason names them all: a diagnostic that
    hides a cause is not diagnostic."""
    decision = unit["decision"]
    if decision.allowed:
        return
    raise ContinuityError(
        cdad_lifecycle.combine(decision, _owner_decision(unit)).message())


def _require_owner_operable(unit: dict[str, Any]) -> None:
    """§4.3/§4.4 (3)/PC-02: the suspension of the ACCREDITED owner blocks NEW
    effects. Naming another unit never turns a suspension into an escape route,
    and a unit that is not suspended keeps operating while another one is."""
    decision = _owner_decision(unit)
    if not decision.allowed:
        raise ContinuityError(decision.message())


def _require_unit_operable(root: Path, context_path: Path,
                           context: dict[str, Any]) -> None:
    """§4.2/§4.3 + PC-01/PC-02: the ONE eligibility of a continuity effect that
    is certainly NEW (identity, accredited owner and its suspension), for the
    borders whose operation never converges with a published one."""
    unit = _accredited_unit(root, context_path, context)
    _require_unit_identity(unit)
    _require_owner_operable(unit)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command in {"begin", "checkpoint", "checkpoint-receipt", "reanchor"}:
            root = Path(args.project_root).resolve()
            context_path = _resolve(root, args.execution_context)
            context = cdad_packet._load_json(context_path, "execution context")
            if not isinstance(context, dict):
                raise ContinuityError("execution context must be a JSON object")
            # §4.4: only the IDENTITY evidence is checked at the CLI border; the
            # suspension and the authority are asked by the operation itself,
            # AFTER it recognizes an accredited replay (§4.4 step 2). `reanchor`
            # never converges with a published effect, and an incomplete
            # `begin`/`checkpoint` (no `--update`) has no content to recognize as
            # a replay, so both keep the full guard here.
            if args.command == "reanchor" or (
                    args.command in ("begin", "checkpoint")
                    and not args.update):
                _require_unit_operable(root, context_path, context)
            else:
                _require_unit_identity(
                    _accredited_unit(root, context_path, context))
        if args.command in ("begin", "checkpoint"):
            if not args.update:
                raise ContinuityError(f"{args.command} requires --update JSON")
            return _run_write(args.command, args)
        if args.command == "reanchor":
            if not args.dry_run and (not args.expected_head or not args.approval_ref
                                     or not args.reason):
                sys.stderr.write("reanchor requires --expected-head, --approval-ref and --reason\n")
                return 2
            return _run_reanchor(args)
        if args.command == "verify-begin":
            _emit(verify_begin(Path(args.project_root),
                               _resolve(Path(args.project_root),
                                        args.execution_context),
                               args.packet, args.attempt))
            return 0
        if args.command == "checkpoint-receipt":
            root = Path(args.project_root)
            _emit(close_durable_receipt(
                root, _resolve(root, args.receipt), args.attempt,
                execution_context=_resolve(root, args.execution_context),
                packet=args.packet, max_bytes=args.max_bytes))
            return 0
        if args.command == "reconcile":
            return _run_reconcile(args)
        if args.command == "resume":
            return _run_resume(args)
        if args.command == "trigger":
            return _run_trigger(args)
    except ContinuityError as exc:
        sys.stderr.write(f"cdad_continuity: {exc}\n")
        return 1
    return 2



if __name__ == "__main__":
    raise SystemExit(main())
