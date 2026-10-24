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


def _execution_identity(document: dict[str, Any]) -> Any:
    """RU-1: the REAL 001 context publishes its identity nested as
    `execution.id`; the flat `execution_id` of the synthetic fixtures is kept
    for compatibility. Anything else (both absent) falls through to fail
    closed in `_safe_segment`, naming `execution_id`."""
    execution = document.get("execution")
    if isinstance(execution, dict):
        nested = execution.get("id")
        if isinstance(nested, str) and nested.strip():
            return nested
    return document.get("execution_id")


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
    (`authority_ref` = `source`; `state` in active|expired|unknown), reading
    only structured fields (D4/review-t4-ru1): `revoked_at` present or
    `status` != `active` → expired; an ISO `expires_on` in the past → expired;
    a delegation with a `source` and no date expires by events (active); no
    delegation → unknown."""
    delegation = _state_delegation(root)
    if not delegation:
        return {}
    source = delegation.get("source")
    revoked_at = delegation.get("revoked_at")
    status = delegation.get("status")
    expires_on = delegation.get("expires_on")
    reason: str | None = None
    if revoked_at is not None:
        state = "expired"
        reason = f"revoked_at={revoked_at!r}"
    elif isinstance(status, str) and status and status != "active":
        state = "expired"
        reason = f"status={status!r}"
    elif isinstance(expires_on, str) and expires_on.strip():
        try:
            expiry = date.fromisoformat(expires_on.strip())
        except ValueError:
            state = "unknown"
            reason = f"expires_on={expires_on!r} is not an ISO date"
        else:
            state = "expired" if expiry < date.today() else "active"
            if state == "expired":
                reason = f"expires_on={expires_on!r} is in the past"
    elif isinstance(source, str) and source.strip():
        # Expires by events; 001 validates vigencia in `prepare` (D4).
        state = "active"
    else:
        state = "unknown"
    normalized: dict[str, Any] = {"authority_ref": source, "state": state}
    if isinstance(expires_on, str):
        normalized["expires_on"] = expires_on
    if reason is not None:
        normalized["reason"] = reason
    return normalized


def _load_execution_context(root: Path, path: Path) -> dict[str, Any]:
    document = _read_json(path, "execution context")
    if not isinstance(document, dict):
        raise ContinuityError("execution context must be a JSON object")
    execution_id = _execution_identity(document)
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
    """D4: validity is read from the structured state, never from prose.

    A state-sourced delegation declares its vigencia explicitly (`active` =
    expires by events); it is returned as-is and its prose `expires` is never
    parsed. Otherwise a missing/unparseable `expires_on` stays `unknown` (never
    fabricated as current); an `expires_on` in the past is `expired`.
    """
    delegation = _delegation(exec_context)
    explicit = delegation.get("state")
    if isinstance(explicit, str) and explicit:
        return explicit
    expires_on = delegation.get("expires_on")
    if not isinstance(expires_on, str) or not expires_on.strip():
        return "unknown"
    try:
        expiry = date.fromisoformat(expires_on.strip())
    except ValueError:
        return "unknown"
    return "expired" if expiry < date.today() else "current"


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
    """D4/D6 + plan T2: an expired HITL delegation may reconstruct context but
    never writes a checkpoint (no dispatch/materialize authorization)."""
    if _authority_state(exec_context) != "expired":
        return
    delegation = _delegation(exec_context)
    detail = delegation.get("reason") or (
        f"expires_on={delegation.get('expires_on')!r}")
    raise ContinuityError(
        f"HITL delegation is expired ({detail}): refusing to write a "
        "checkpoint — expired authority reconstructs context but never "
        "authorizes effects (D4)")


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
    """The declared evidence of the walkable chain, OLDEST first.

    Returns the latest declared status per id, the latest entry per id and the
    `(body_sha256, evidence_id)` declarations an antecedent may resolve to —
    the entries themselves, so a transition can be checked against the identity
    it claims to supersede (§2.5/INV-7)."""
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
    """
    declared = update.get("evidence")
    if declared is None:
        inherited = head_body.get("evidence")
        return list(inherited) if isinstance(inherited, list) else []
    if not isinstance(declared, list) or not declared:
        raise ContinuityError(
            "update.evidence must be a non-empty list of evidence entries: an "
            f"empty list cannot retire evidence in silence; got {declared!r}")
    chain = chain if chain is not None else {"links": []}
    history = _evidence_history(chain)
    status = history["status"]
    known = history["declared"]
    latest = history["latest"]
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
            antecedent_entry = known.get(key)
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


def _run_write(command: str, args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    exec_context = _load_execution_context(
        root, _resolve(root, args.execution_context))
    update = _read_json(_resolve(root, args.update), "update")
    if not isinstance(update, dict):
        raise ContinuityError("update must be a JSON object")
    _require_key_fields(update)
    _require_content_fields(update)
    _require_current_authority(exec_context)
    record = "begin" if command == "begin" else "checkpoint"
    declared_changes = _declared_changes(update)

    max_bytes = args.max_bytes if args.max_bytes is not None else DEFAULT_MAX_BYTES
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

    if head is not None and _same_key(head, body):
        # Same idempotency key. §2.3.1: the repetition comparison is the whole
        # content of the head body minus its single top-level `prev`; `prev`
        # itself is derived from the validated head, so it never reaches this
        # comparison and is never a no-op bypass.
        if _content_without_prev(head_body) == body:
            no_op = dict(head)
            no_op["no_op"] = True
            _emit(no_op)
            return 0
        if command != "checkpoint":
            raise ContinuityError(
                "split-brain: a "
                f"{command} with the same idempotency key (execution_id="
                f"{execution_id!r}, packet_id={body.get('packet_id')!r}, "
                f"attempt={body.get('attempt')!r}) diverges from the head (head "
                f"body {head.get('body_sha256')}, attempted body "
                f"{_sha256(_canonical_bytes(body))}); refusing to overwrite the "
                "head — escalate (O1/D7)")
        # P5 (003-007): a divergent `checkpoint` with the head's key is NOT a
        # split-brain — it appends a new link (seq+1, prev = body of the head),
        # preserving the previous link as evidence. Fall through to write.

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
    if len(body_bytes) > max_bytes:
        raise ContinuityError(
            f"projection exceeds --max-bytes {max_bytes} "
            f"(canonical body is {len(body_bytes)} bytes); refusing to truncate")
    body_sha256 = _sha256(body_bytes)

    envelope = _checkpoint_envelope(exec_context, body, body_sha256, body_bytes,
                                    references, head, max_bytes)
    _write_synced(_body_path(root, execution_id, body_sha256), body_bytes)
    _write_synced(_head_path(root, execution_id),
                  (json.dumps(envelope, indent=2, sort_keys=True,
                              ensure_ascii=False) + "\n").encode("utf-8"))
    _emit(envelope)
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
        "next_action": head_body.get("next_action"),
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

    existing = _chain_closes(chain, execution_id, packet_id, attempt)
    if len(existing) > 1:
        raise ContinuityError(
            "violación de unicidad del cierre: hay "
            f"{len(existing)} cierres para (execution_id={execution_id!r}, "
            f"packet_id={packet_id!r}, attempt={attempt!r}): "
            f"{[sha[:12] for sha, _ in existing]} — a lo sumo UNO por paquete e "
            f"intento (§2.3.2)")
    if existing:
        close_sha, close_body = existing[0]
        marker = close_body[RECEIPT_CHECKPOINT_FIELD]
        existing_path = _canonical_path(
            root, _resolve(root, str(marker.get("path"))))
        if existing_path == receipt_normalized_path \
                and marker.get("sha256") == receipt_digest:
            envelope = _close_envelope(
                close_body, close_sha,
                max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES)
            envelope["no_op"] = True
            return envelope
        raise ContinuityError(
            f"el cierre ya existe con otro contenido: cierre existente "
            f"{close_sha} (ruta {existing_path!r}, digest {marker.get('sha256')!r}) "
            f"frente a la recepción declarada (ruta {receipt_normalized_path!r}, "
            f"digest {receipt_digest!r}) — no se sustituye ni se agrega un "
            f"segundo cierre (§2.3.2)")

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
    _require_current_authority(exec_context)
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
            return {"links": links, "demonstrable": True, "unknowns": []}
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
    for path in sorted(bodies_dir.glob("*.json")):
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
    """The feature of the examined request: the execution context's binding
    (v2) or, for a flat legacy context, the state's active feature."""
    execution = exec_context.get("execution")
    if isinstance(execution, dict):
        feature = execution.get("feature_id")
        if isinstance(feature, str) and feature:
            return feature
    if isinstance(state, dict):
        feature = state.get("active_feature")
        if isinstance(feature, str) and feature:
            return feature
    return None


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
    packet_id = _safe_segment(args.packet, "packet")

    head = _load_head(root, execution_id)
    report_list: list[dict[str, Any]] = []
    if head is not None:
        body, _ = _verify_body(root, execution_id, head)
        _verify_chain(root, execution_id, head)
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
        command.add_argument("--update", required=True)
        command.add_argument("--max-bytes", type=int, default=None)
        command.add_argument("--json", action="store_true")

    add_write("begin", "write-ahead a checkpoint (idempotent on an identical head)")
    add_write("checkpoint", "append a new checkpoint link to the chain")

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
    reconcile.add_argument("--packet", required=True)
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


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command in ("begin", "checkpoint"):
            return _run_write(args.command, args)
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
