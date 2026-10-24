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

# Declared 200k context profile (plan T3: 200k/150k/120k). It is a SIGNAL, not
# a hard limit (D5): `trigger` only applies it when the runtime reported an
# integer counter AND an integer limit (P6); otherwise the state stays
# `unknown` and no number is fabricated (invariant 2). `rotate_at` is
# `limit - reserve` (200000 - 50000 = 150000).
PROFILE_RESERVE = 50_000
PROFILE_PREPARE_AT = 120_000

CONTINUITY_TREE = (".cdad", "executions")
RUNTIME_TREE = (".cdad", "runtime")

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
                    record: str) -> dict[str, Any]:
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
    return body


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

    max_bytes = args.max_bytes if args.max_bytes is not None else DEFAULT_MAX_BYTES
    references = _digest_references(root, update.get("references"))
    body = _canonical_body(exec_context, update, references,
                           "begin" if command == "begin" else "checkpoint")
    body_bytes = _canonical_bytes(body)
    if len(body_bytes) > max_bytes:
        raise ContinuityError(
            f"projection exceeds --max-bytes {max_bytes} "
            f"(canonical body is {len(body_bytes)} bytes); refusing to truncate")
    body_sha256 = _sha256(body_bytes)

    execution_id = exec_context["execution_id"]
    head = _load_head(root, execution_id)

    if head is not None and _same_key(head, body):
        # Same idempotency key: an identical canonical body is a successful
        # no-op (P3); a divergent `begin` is a conflict — the rejection is
        # all-or-nothing (RU-2): nothing is persisted, never overwrite the head,
        # never duplicate the chain (D7/O1).
        if head.get("body_sha256") == body_sha256:
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
                f"body {head.get('body_sha256')}, attempted body {body_sha256}); "
                "refusing to overwrite the head — escalate (O1/D7)")
        # P5 (003-007): a divergent `checkpoint` with the head's key is NOT a
        # split-brain — it appends a new link (seq+1, prev = body of the head),
        # preserving the previous link as evidence. Fall through to write.

    envelope = _checkpoint_envelope(exec_context, body, body_sha256, body_bytes,
                                    references, head, max_bytes)
    _write_synced(_body_path(root, execution_id, body_sha256), body_bytes)
    _write_synced(_head_path(root, execution_id),
                  (json.dumps(envelope, indent=2, sort_keys=True,
                              ensure_ascii=False) + "\n").encode("utf-8"))
    _emit(envelope)
    return 0


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


def _verify_body(root: Path, execution_id: str,
                 head: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    """P1: the stored body must digest to the digest named by the head. The
    file name IS the content digest (content-addressed), so any byte-level
    change is a tamper even when it is invisible to JSON canonicalization."""
    body_sha256 = head.get("body_sha256")
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
    return body, raw


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


def _projection(body: dict[str, Any],
                exec_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "goal": body.get("goal"),
        # D4/RU-1: the authority (with its CURRENT vigencia) is reconstructed
        # on demand from the state/context, never frozen stale in the body.
        "authority": _authority_view(exec_context),
        "decisions": body.get("decisions", []),
        "uncertainties": body.get("uncertainties", []),
        "next_action": body.get("next_action"),
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
        projection = _projection({}, exec_context)
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

    body, _ = _verify_body(root, execution_id, head)
    _verify_chain(root, execution_id, head)
    report_list = _reference_reports(root, body.get("references"), body)

    projection = _projection(body, exec_context)
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
