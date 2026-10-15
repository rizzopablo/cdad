#!/usr/bin/env python3
"""cdad_guard — deterministic, read-only progress guard (003-003, T1 GREEN).

The guard is an analyzer, never an orchestrator: it reads already-existing
signals and emits structured incidents/decisions; the semantic judgement stays
in the orchestrator (D1/D5). Two slices are implemented:

    classify  --project-root ROOT --trace TRACE.json
    preflight --project-root ROOT --execution-context EXEC.json \
              --role ROLE --operation OP [--json]

`preflight` (T2, P3/D6/O2) reads `ROOT/docs/cdad-policy.json` plus a 001
execution context and prevalidates an operation against the policy (private
paths) and the role's declared scopes, BEFORE it is dispatched. It is
read-only: it never writes the policy nor grants/hardens permissions. A denial
returns rc!=0 with an actionable stderr diagnostic and the full `preflight-v1`
envelope on stdout; a legitimate operation returns rc 0. Same input always
yields the same bounded decision (no counter drift, no loop).

`preflight-v1` decision semantics (F1 review-fix, `review-t2-decision.md`):

- A target **outside the project root** (a `..` escape or an absolute path) is
  *not governed by the project policy*: the decision is `allow` with the honest
  reason "outside project root: not governed by project policy" — never the
  fabricated "within the declared scope" (owner amendment: leaving the root is
  enabled by default).
- A tool with **no resolvable target** (e.g. `bash` and every non-write tool
  without a target) is not evaluable: the decision is `unknown` with an honest
  reason, never a fabricated `allow`, `deny` or "within the declared scope"
  (P5, spec §2 "sin señal fiable"; invariant 4).
- `read_scope` is consulted for reads (and every non-write tool with a target):
  a read outside the role's `read_scope` denies with `denied_by="role-scope"`.
- A malformed policy shape (`path_policy` not an object, or a present
  `private_paths` not a list) fails loud: rc!=0 with a "policy invalid"
  diagnostic; **absent** keys are a declared-empty policy.
- `--role` contradicting `exec_context["role"]` is an identity inconsistency:
  rc!=0 with a diagnostic naming the role (identity is verified, not trusted).

**O-D limitation (declared, low debt):** `WRITE_TOOLS` is a single generic set
of mutation verbs, with no per-role tool map: the "role capability map" D6
mentions is only partially materialized. It is acceptable as an MVP while the
no-resolvable-target branch yields `unknown` instead of a fabricated `allow`.
Severity calibration is deferred to real usage (T5).

`classify` consumes a recorded `trace-v1` fixture (offline, deterministic,
labelled `simulation`) and emits one JSON envelope on stdout:

- `incidents`: repetition-without-progress (P1). A run of >= REPETITION_THRESHOLD
  consecutive `tool_call` entries sharing the same fingerprint (tool + args
  as recorded + result_class, D2) AND the same *observed* progress_token (no
  observable progress) yields a single incident with an explicit rule and
  evidence of why they are equivalent. **Argument canonicalization is the
  recorder's responsibility**, declared in the `trace-v1` contract
  (`skills/cdad-cycle/assets/guard-trace.schema.json`): the trace must be
  recorded with already-canonicalized args (stable fields only). The guard
  hashes args as recorded and does not canonicalize them (B3b). An absent or
  non-string `progress_token` is an *unobserved* signal: it never fabricates a
  frozen-progress incident (fail-closed to the non-alarm side, B1/P5/inv. 4).
- `polls`: one closed decision per `poll` entry (`wait` | `escalate` |
  `unknown`, D5). A justified poll (condition + deadline + cadence) continues
  (`wait`) before the deadline and escalates exactly once at it; later polls
  without a relevant change do not re-escalate (P2/P7). A poll without a valid
  justification signal is `unknown`, never a bare `wait` (O1/P5).
- `escalations`: the closed event->action channel extended by T3 (P5/D5/D10).
  An unreliable signal (`result_class == "unknown"`) is ambiguous: the guard
  does not fabricate success/blockage, it returns ONE `escalation-v1` package
  to the orchestrator (`unknown: true`, a declared observability limitation, and
  an action from the CLOSED table). The channel is always present, empty when
  nothing escalates. A lone `timeout` is NOT blockage (invariant 3) and a
  legitimate progressive run does not escalate (P7).

T3 (`record`/`budget`) writes durable recovery events/budget ONLY under
`.cdad/executions/<execution_id>/guards/**` (D4, never `docs/.cdad-state.json`).
`record` is create-exclusive: the durable path components are validated as safe
segments (002 `_segment`) and a repeated `(packet, attempt, kind)` key is a
conflict (rc!=0, original bytes untouched), so evidence is never overwritten.
`record` consults the 002 receipt/journal under
`.cdad/runtime/results/<execution_id>/<packet_id>/` before repeating and only
SIGNALS (`do_not_repeat`/`receipt_ref`), it never repeats an effect (D7,
invariant 5). `budget` is read-only and deterministic; exhausting the declared
attempts is a signal to reconsider (D3), not a violation.

Pure Python stdlib. `classify`/`budget` are read-only over the product; only
`record` writes, and only under `.cdad/executions/<id>/guards/**`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRACE_CONTRACT = "trace-v1"
PREFLIGHT_CONTRACT = "preflight-v1"
RECORD_CONTRACT = "record-v1"
BUDGET_CONTRACT = "budget-v1"
ESCALATION_CONTRACT = "escalation-v1"
GUARD_EVENT_CONTRACT = "guard-event-v1"
SCHEMA_VERSION = 1

# Durable trees (D4): recovery events/budget live under
# `.cdad/executions/<execution_id>/guards/`; the 002 receipts/journal live under
# `.cdad/runtime/results/<execution_id>/<packet_id>/`.
GUARDS_TREE = (".cdad", "executions")
RESULTS_TREE = (".cdad", "runtime", "results")

# Closed event->action table (D5): only reversible, proportional actions. The
# guard never invents a decision outside this set; ambiguity goes back to the
# orchestrator as an `escalation-v1` package. The recovery actions recorded by
# `record` (`resume-same-session`, `retry`) are declared here too so the event
# writer cannot diverge from the schema (T3 review-fix F3).
CLOSED_ACTIONS = frozenset({
    "backoff-poll",
    "retry-with-change",
    "repackage",
    "new-session-from-checkpoint",
    "escalate",
    "recommend-block",
    "resume-same-session",
    "retry",
})

# Durable `guard-event-v1` document keys (guard-event.schema.json). A persisted
# event must not carry any other property (`additionalProperties:false`, F3).
EVENT_KEYS = frozenset({
    "schema_version", "event", "execution_id", "packet_id", "attempt",
    "kind", "cause", "session", "action", "at",
})

# Safe path segment, mirroring 002 `_segment` (cdad_result.py): a durable
# filename component must never contain a separator or a `..` traversal.
SEGMENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")

# Policy file read (never written) by the pre-flight, relative to --project-root.
POLICY_REL_PATH = "docs/cdad-policy.json"

# Operations that mutate the product. Only these are checked against the role's
# write_scope; every other tool with a resolvable target is a read and is
# checked against the role's read_scope (F1-G'). A deny of a legitimate scope is
# a product defect (P3/P7), so the pre-flight stays conservative: an operation
# with no resolvable target is `unknown`, never a fabricated deny.
WRITE_TOOLS = frozenset({
    "edit", "write", "create", "unlink", "delete", "mkdir", "rmdir",
    "rename", "move", "chmod", "trash", "patch",
})

# Conservative explicit trigger for the 2.073-reintentos incident signal: a run
# of at least this many equivalent, non-progressing calls is unambiguous.
REPETITION_THRESHOLD = 3

REPETITION_RULE = (
    "repetition-without-progress: >=3 consecutive tool_call entries with the "
    "same fingerprint (tool + args as recorded + result_class) and a frozen "
    "observed progress_token (no observable progress)"
)

POLL_DECISIONS = ("wait", "escalate", "unknown")


# ------------------------------------------------------------------ fingerprint


def canonical_fingerprint(entry: dict[str, Any]) -> str:
    """Fingerprint = tool + args as recorded + result_class (D2).

    Only stable fields participate; the original evidence stays by reference
    (never a hash of the full output). Args are hashed exactly as recorded —
    canonicalization is the recorder's responsibility, declared in the
    `trace-v1` contract (B3b); the guard does not canonicalize them.
    """
    payload = {
        "tool": entry.get("tool"),
        "args": entry.get("args", []),
        "result_class": entry.get("result_class"),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ classify


def _repetition_incidents(entries: list[Any]) -> list[dict[str, Any]]:
    incidents: list[dict[str, Any]] = []
    run: list[dict[str, Any]] = []

    def flush() -> None:
        if len(run) >= REPETITION_THRESHOLD:
            head = run[0]
            incidents.append({
                "kind": "repetition-without-progress",
                "rule": REPETITION_RULE,
                "fingerprint": head["fingerprint"],
                "result_class": head["result_class"],
                "count": len(run),
                "evidence": {"progress": {"changed": False}},
            })

    for entry in entries:
        if not isinstance(entry, dict) or entry.get("kind") != "tool_call":
            flush()
            run = []
            continue
        fingerprint = canonical_fingerprint(entry)
        progress_token = entry.get("progress_token")
        if not isinstance(progress_token, str):
            # Unobserved progress signal: an absent/non-string token is not a
            # datum. Fail-closed to the non-alarm side — never fabricate a
            # frozen-progress incident from an unknown token (B1/P5/inv. 4).
            flush()
            run = []
            continue
        if run and run[0]["fingerprint"] == fingerprint \
                and run[0]["progress_token"] == progress_token:
            run.append({
                "fingerprint": fingerprint,
                "result_class": entry.get("result_class"),
                "progress_token": progress_token,
            })
        else:
            flush()
            run = [{
                "fingerprint": fingerprint,
                "result_class": entry.get("result_class"),
                "progress_token": progress_token,
            }]
    flush()
    return incidents


def _parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _poll_decisions(entries: list[Any]) -> list[dict[str, Any]]:
    decisions: list[dict[str, Any]] = []
    escalated: set[tuple[Any, Any]] = set()

    for entry in entries:
        if not isinstance(entry, dict) or entry.get("kind") != "poll":
            continue
        condition = entry.get("condition")
        deadline = _parse_ts(entry.get("deadline"))
        at = _parse_ts(entry.get("at"))
        cadence = entry.get("cadence_seconds")
        justified = (
            isinstance(condition, str) and condition.strip()
            and deadline is not None and at is not None
            and isinstance(cadence, int) and not isinstance(cadence, bool)
            and cadence > 0
        )
        if not justified:
            # No reliable justification signal: unknown, never a bare `wait`
            # that the orchestrator could read as a justified wait (O1/P5).
            decision = "unknown"
        elif at < deadline:
            decision = "wait"
        else:
            key = (condition, entry.get("deadline"))
            if key in escalated:
                decision = "wait"
            else:
                decision = "escalate"
                escalated.add(key)
        decisions.append({"i": entry.get("i"), "decision": decision})

    return decisions


def _escalations(entries: list[Any],
                 context: dict[str, Any]) -> list[dict[str, Any]]:
    """Closed event->action escalations for unreliable signals (P5/D5/inv. 4).

    A `tool_call` whose `result_class` is `unknown` is an ambiguous signal: the
    runtime does not expose a reliable outcome, so repetition, blockage and
    success cannot be distinguished. The guard must NOT fabricate a verdict
    (invariant 4): it emits ONE `escalation-v1` package for the orchestrator to
    decide, with an action from the CLOSED table (never `recommend-block` from
    an unreliable signal — that would fabricate failure). A lone `timeout`
    (invariant 3) and legitimate progressive runs are not escalated.

    The package carries `execution_id`, `packet_id` and the canonical
    `fingerprint` of the calls that trigger it, so the declared `dedup_key`
    (canon(incident_kind, fingerprint, execution_id, packet_id)) can be derived
    from what the channel emits (O2/D10/D11).
    """
    unreliable = [
        entry for entry in entries
        if isinstance(entry, dict)
        and entry.get("kind") == "tool_call"
        and entry.get("result_class") == "unknown"
    ]
    if not unreliable:
        return []
    count = len(unreliable)
    return [{
        "contract": ESCALATION_CONTRACT,
        "incident_kind": "unknown-signal",
        "execution_id": context.get("execution_id"),
        "packet_id": context.get("packet_id"),
        "fingerprint": canonical_fingerprint(unreliable[0]),
        "situation": (
            f"{count} tool_call(s) with an unreliable result_class 'unknown': "
            "the runtime exposes no reliable signal to classify them"
        ),
        "decision_needed": True,
        "unknown": True,
        "limitation": (
            "result_class 'unknown': the runtime does not expose the outcome of "
            "these tool_call(s), so repetition, blockage and success cannot be "
            "distinguished (invariant 4; no fabricated success/failure)"
        ),
        "action": "escalate",
        "package": {
            "summary": (
                "Ambiguous signal: classify the unknown tool_call(s) with the "
                "orchestrator before deciding on a recovery action"
            ),
            "evidence": (
                "trace entries with kind=='tool_call' and "
                f"result_class=='unknown' (count={count}); action confined to "
                "the closed event->action table (D5)"
            ),
        },
    }]


def classify_trace(trace: dict[str, Any]) -> dict[str, Any]:
    entries = trace.get("entries", [])
    if not isinstance(entries, list):
        entries = []
    return {
        "schema_version": SCHEMA_VERSION,
        "trace": trace.get("trace", TRACE_CONTRACT),
        "simulation": bool(trace.get("simulation", False)),
        "session_id": trace.get("session_id"),
        "incidents": _repetition_incidents(entries),
        "polls": _poll_decisions(entries),
        "escalations": _escalations(entries, trace),
    }


# ------------------------------------------------------------------ validation


def validate_trace(trace: Any) -> str | None:
    """Validate the `trace-v1` input contract; return a diagnostic or None.

    Fail-closed boundary (§3): a trace outside the contract must not be
    classified silently as an empty "valid" envelope (B2). Checks the three
    declared invariants: `trace=="trace-v1"`, `schema_version==1`, `entries`
    is a list.
    """
    if not isinstance(trace, dict):
        return "trace must be a JSON object"
    if trace.get("trace") != TRACE_CONTRACT:
        return f"trace must be {TRACE_CONTRACT!r}"
    if trace.get("schema_version") != SCHEMA_VERSION:
        return f"schema_version must be {SCHEMA_VERSION}"
    if not isinstance(trace.get("entries"), list):
        return "entries must be a list"
    return None


# ------------------------------------------------------------------ preflight


def _root_relative(root: Path, raw: Any) -> str | None:
    """Return the root-relative POSIX path of `raw`, or None when the target
    cannot be placed inside `root` (absolute outside root, or a `..` escape).

    Parsing at the boundary: every later scope/policy test works on this
    normalized value, so an ambiguous target fails closed to "outside".
    """
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(root)
        except ValueError:
            return None
    text = posixpath.normpath(candidate.as_posix())
    if text == ".." or text.startswith("../"):
        return None
    return text


def _is_under(path: str, target: str) -> bool:
    """True when `path` is `target` itself or lies inside it."""
    target = target.strip("/")
    if not target:
        return False
    return path == target or path.startswith(target + "/")


def validate_policy(policy: Any) -> str | None:
    """Validate the policy shape read by `preflight`; return a diagnostic or None.

    Fail-loud boundary (§3, F1-E): a malformed policy must not degrade to an
    implicit empty policy and silently allow the operation. `path_policy` must
    be an object when present, and `private_paths` must be a list when present;
    **absent** keys are a declared-empty policy, not an error.
    """
    if not isinstance(policy, dict):
        return "policy must be a JSON object"
    if "path_policy" in policy and not isinstance(policy["path_policy"], dict):
        return "path_policy must be an object"
    path_policy = policy.get("path_policy")
    if isinstance(path_policy, dict) and "private_paths" in path_policy \
            and not isinstance(path_policy["private_paths"], list):
        return "path_policy.private_paths must be a list"
    return None


def _private_paths(policy: Any) -> list[str]:
    if not isinstance(policy, dict):
        return []
    path_policy = policy.get("path_policy")
    if not isinstance(path_policy, dict):
        return []
    entries = path_policy.get("private_paths")
    if not isinstance(entries, list):
        return []
    return [entry.strip().strip("/") for entry in entries
            if isinstance(entry, str) and entry.strip()]


def _scope_targets(scope: Any) -> list[str]:
    """Extract root/path targets from a declared scope list (001 context)."""
    targets: list[str] = []
    if not isinstance(scope, list):
        return targets
    for entry in scope:
        if not isinstance(entry, dict):
            continue
        for key in ("root", "path"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                targets.append(value.strip().strip("/"))
    return targets


def evaluate_preflight(policy: Any, exec_context: Any, role: str,
                       operation: dict[str, Any], root: Path) -> dict[str, Any]:
    """Return the `preflight-v1` decision for one operation.

    Denial order: a policy `private_paths` match (only meaningful inside the
    root) denies with independence of role; then an operation with a resolvable
    target outside the role's declared scope denies by role-scope — the
    `write_scope` for mutating tools, the `read_scope` for reads (F1-G').

    A target that cannot be placed inside the root is *outside* it and therefore
    not governed by the project policy: `allow` with the honest reason (owner
    amendment). A tool with no resolvable target at all is not evaluable:
    `unknown`, never a fabricated decision (P5). The decision is a pure function
    of its inputs — no state, no counter, no drift.
    """
    tool = operation.get("tool")
    raw_path = operation.get("path")
    rel = _root_relative(root, raw_path)

    for private in _private_paths(policy):
        if rel is not None and _is_under(rel, private):
            return {
                "decision": "deny",
                "denied_by": "policy",
                "reason": (
                    f"operation {tool!r} on {raw_path!r} matches private_paths "
                    f"entry {private!r} declared in {POLICY_REL_PATH}; "
                    "refused before execution (read-only pre-flight)"),
            }

    if rel is None:
        if not (isinstance(raw_path, str) and raw_path.strip()):
            # No resolvable target: not evaluable against policy or role.
            # Fail to `unknown`, never fabricate an `allow`/`deny` (P5, inv. 4).
            return {
                "decision": "unknown",
                "reason": (
                    f"operation {tool!r} has no resolvable target path; "
                    "not evaluated against policy or role scope (unknown)"),
            }
        # Declared target outside the root: not governed by the project policy.
        return {
            "decision": "allow",
            "reason": (
                f"operation {tool!r} on {raw_path!r} is outside project root: "
                "not governed by project policy"),
        }

    scope_key = "write_scope" if tool in WRITE_TOOLS else "read_scope"
    scopes = exec_context if isinstance(exec_context, dict) else {}
    targets = _scope_targets(scopes.get(scope_key))
    if not any(_is_under(rel, target) for target in targets):
        return {
            "decision": "deny",
            "denied_by": "role-scope",
            "reason": (
                f"operation {tool!r} on {raw_path!r} is outside the "
                f"{scope_key} of role {role!r} "
                f"({targets or 'none declared'}); refused before "
                "execution (read-only pre-flight)"),
        }

    return {
        "decision": "allow",
        "reason": (
            f"operation {tool!r} on {raw_path!r} is within the declared "
            f"{scope_key} of role {role!r}; allowed"),
    }


# ------------------------------------------------------------------ record/budget
#
# T3 (P4/P5, D3/D4/D7). `record` persists one durable recovery event under
# `.cdad/executions/<execution_id>/guards/` and consults the 002 receipt/journal
# before repeating (it only SIGNALS). `budget` reports the durable, accumulated
# attempts for one `execution_id+packet_id`; it is read-only and deterministic
# and never resets on a restart/new session (invariant 11). Exhausting the
# declared limit is a signal to *reconsider* (D3), not a violation.


def validate_event(event: Any) -> str | None:
    """Validate the `guard-event-v1` input; return a diagnostic or None.

    Fail-loud boundary (§3): an out-of-contract event must not be persisted
    silently under `guards/`. Aligned with `guard-event.schema.json` (F3):
    `additionalProperties:false` (no unknown field is accepted) and `action`
    belongs to the closed event->action table (D5).
    """
    if not isinstance(event, dict):
        return "event must be a JSON object"
    unknown = sorted(set(event) - EVENT_KEYS)
    if unknown:
        return ("event has unknown fields (additionalProperties:false): "
                + ", ".join(unknown))
    if event.get("event") != GUARD_EVENT_CONTRACT:
        return f"event must be {GUARD_EVENT_CONTRACT!r}"
    if event.get("schema_version") != SCHEMA_VERSION:
        return f"schema_version must be {SCHEMA_VERSION}"
    for key in ("execution_id", "packet_id", "kind", "cause", "session",
                "action", "at"):
        if not isinstance(event.get(key), str) or not event[key].strip():
            return f"{key} must be a non-empty string"
    attempt = event.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
        return "attempt must be a positive integer"
    if event["action"] not in CLOSED_ACTIONS:
        return (f"action must belong to the closed event->action table "
                f"{sorted(CLOSED_ACTIONS)}: {event['action']!r}")
    return None


def _segment(value: Any) -> str | None:
    """Return `value` when it is a safe path segment, else None (002 `_segment`).

    Mirrors `cdad_result.py`'s `_segment`: `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`
    with no `..`. Used for the durable filename components so a traversal or an
    absolute path can never escape `.cdad/executions/<id>/guards/` (F1).
    """
    if not isinstance(value, str) or SEGMENT_RE.fullmatch(value) is None \
            or ".." in value:
        return None
    return value


def _guards_dir(root: Path, execution_id: str) -> Path:
    return root.joinpath(*GUARDS_TREE, execution_id, "guards")


def _find_receipt(root: Path, execution_id: str,
                  packet_id: str) -> str | None:
    """Relative path of the 002 receipt for (execution, packet), or None.

    Reuses 002's journal by REFERENCE (invariant 5); the guard never redefines
    it. The reconciliation cites the RECEIPT by name (`…/receipt.json`), not any
    other artifact of the 002 layout (`bundle.json`, `parts/…`) (O1/D7).
    Absent receipt -> None (never fabricate a reconciliation).
    """
    results_dir = root.joinpath(*RESULTS_TREE, execution_id, packet_id)
    if not results_dir.is_dir():
        return None
    candidate = results_dir / "receipt.json"
    if not candidate.is_file():
        found = sorted(p for p in results_dir.rglob("receipt.json")
                       if p.is_file())
        if not found:
            return None
        candidate = found[0]
    return candidate.relative_to(root).as_posix()


def _collect_attempts(root: Path, execution_id: str,
                      packet_id: str) -> list[dict[str, Any]]:
    """Durable recovery attempts for (execution, packet), sorted by attempt."""
    guards_dir = _guards_dir(root, execution_id)
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


def _max_attempts(exec_context: Any) -> int | None:
    """Declared `guard_budget.max_attempts` (D3), or None when not declared."""
    if not isinstance(exec_context, dict):
        return None
    guard_budget = exec_context.get("guard_budget")
    if not isinstance(guard_budget, dict):
        return None
    value = guard_budget.get("max_attempts")
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    return None


# ------------------------------------------------------------------ CLI


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cdad_guard")
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify", help="classify a recorded trace-v1")
    classify.add_argument("--project-root", required=True)
    classify.add_argument("--trace", required=True)

    preflight = sub.add_parser(
        "preflight", help="prevalidate an operation against policy + role")
    preflight.add_argument("--project-root", required=True)
    preflight.add_argument("--execution-context", required=True)
    preflight.add_argument("--role", required=True)
    preflight.add_argument("--operation", required=True)
    preflight.add_argument("--json", action="store_true")

    record = sub.add_parser(
        "record", help="persist a durable guard-event-v1 recovery event")
    record.add_argument("--project-root", required=True)
    record.add_argument("--event", required=True)

    budget = sub.add_parser(
        "budget", help="report the durable per-packet recovery budget")
    budget.add_argument("--project-root", required=True)
    budget.add_argument("--execution-context", required=True)
    budget.add_argument("--packet", required=True)

    return parser


def _cmd_classify(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    trace_path = Path(args.trace)
    if not trace_path.is_absolute():
        trace_path = root / trace_path
    try:
        raw = trace_path.read_text(encoding="utf-8")
    except OSError as exc:
        # Deterministic diagnostic, no raw traceback (§3: violation → rc≠0
        # with a designed stderr message and no partial output).
        sys.stderr.write(
            f"cdad_guard: cannot read trace {trace_path}: {exc.strerror or exc}\n")
        return 2
    try:
        trace = json.loads(raw)
    except ValueError:
        sys.stderr.write(
            f"cdad_guard: invalid JSON in trace {trace_path}\n")
        return 2
    error = validate_trace(trace)
    if error is not None:
        sys.stderr.write(
            f"cdad_guard: invalid {TRACE_CONTRACT} trace: {error}\n")
        return 2
    envelope = classify_trace(trace)
    sys.stdout.write(json.dumps(envelope, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")
    return 0


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _cmd_preflight(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    policy_path = root / POLICY_REL_PATH
    exec_path = Path(args.execution_context)
    if not exec_path.is_absolute():
        exec_path = root / exec_path

    # O2: the policy is READ here and never written. Fail loud on a missing or
    # malformed input instead of prevalidating against an implicit default.
    try:
        policy = _load_json(policy_path)
    except OSError as exc:
        sys.stderr.write(
            f"cdad_guard: cannot read policy {policy_path}: "
            f"{exc.strerror or exc}\n")
        return 2
    except ValueError:
        sys.stderr.write(f"cdad_guard: invalid JSON in policy {policy_path}\n")
        return 2

    # F1-E (fail-loud): a malformed policy shape fails explicitly instead of
    # degrading to an implicit empty policy that would allow the operation.
    policy_error = validate_policy(policy)
    if policy_error is not None:
        sys.stderr.write(f"cdad_guard: policy invalid: {policy_error}\n")
        return 2

    try:
        exec_context = _load_json(exec_path)
    except OSError as exc:
        sys.stderr.write(
            f"cdad_guard: cannot read execution context {exec_path}: "
            f"{exc.strerror or exc}\n")
        return 2
    except ValueError:
        sys.stderr.write(
            f"cdad_guard: invalid JSON in execution context {exec_path}\n")
        return 2

    # F1-C (identity): the evaluated role must be verifiable against the
    # execution context, not trusted blindly from the --role flag.
    context_role = exec_context.get("role") if isinstance(exec_context, dict) \
        else None
    if context_role != args.role:
        sys.stderr.write(
            f"cdad_guard: role inconsistency: --role {args.role!r} does not "
            f"match execution context role {context_role!r}\n")
        return 2

    try:
        operation = json.loads(args.operation)
    except ValueError:
        sys.stderr.write("cdad_guard: --operation must be a JSON object\n")
        return 2
    if not isinstance(operation, dict):
        sys.stderr.write("cdad_guard: --operation must be a JSON object\n")
        return 2

    result = evaluate_preflight(policy, exec_context, args.role, operation,
                                root)
    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "preflight": PREFLIGHT_CONTRACT,
        "role": args.role,
        "operation": operation,
        "decision": result["decision"],
        "reason": result["reason"],
    }
    if result["decision"] == "deny":
        envelope["denied_by"] = result["denied_by"]
    # Full envelope on stdout, no partial output; the diagnostic goes to
    # stderr (§3). Emit stdout before stderr so a deny is never mute.
    sys.stdout.write(json.dumps(envelope, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")
    if result["decision"] == "deny":
        sys.stderr.write(
            f"cdad_guard: deny ({result['denied_by']}): {result['reason']}\n")
        return 1
    return 0


def _cmd_record(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    event_path = Path(args.event)
    if not event_path.is_absolute():
        event_path = root / event_path
    try:
        event = _load_json(event_path)
    except OSError as exc:
        sys.stderr.write(
            f"cdad_guard: cannot read event {event_path}: "
            f"{exc.strerror or exc}\n")
        return 2
    except ValueError:
        sys.stderr.write(f"cdad_guard: invalid JSON in event {event_path}\n")
        return 2

    error = validate_event(event)
    if error is not None:
        sys.stderr.write(
            f"cdad_guard: invalid {GUARD_EVENT_CONTRACT} event: {error}\n")
        return 2

    execution_id = event["execution_id"]
    packet_id = event["packet_id"]
    attempt = event["attempt"]

    # F1 (invariant 1/D4): the durable path components must be safe segments
    # BEFORE any write; a traversal (`../x`) or an absolute path is refused with
    # zero writes (the envelope cannot lie with a path that "looks" contained).
    segments: dict[str, str] = {}
    for label in ("execution_id", "packet_id", "kind"):
        segment = _segment(event[label])
        if segment is None:
            sys.stderr.write(
                f"cdad_guard: {label} must be a safe path segment "
                f"([A-Za-z0-9][A-Za-z0-9._-]{{0,127}}, no '..'): "
                f"{event.get(label)!r}\n")
            return 2
        segments[label] = segment
    execution_id = segments["execution_id"]
    packet_id = segments["packet_id"]
    kind = segments["kind"]

    # D4: durable persistence ONLY under .cdad/executions/<id>/guards/**. The
    # key on disk is (packet, attempt, kind) — exact safe segments, no
    # `_slug` collapsing (F2: a slug collision must not overwrite evidence).
    guards_dir = _guards_dir(root, execution_id)
    filename = f"{packet_id}-attempt-{attempt:04d}-{kind}.json"
    durable_path = guards_dir / filename

    # F2 (P4/invariant 11): `record` is CREATE-EXCLUSIVE. A second event with
    # the same (packet, attempt, kind) key is a conflict: rc!=0 with the
    # original bytes untouched (002 convention: refusing to overwrite).
    if durable_path.exists():
        sys.stderr.write(
            f"cdad_guard: conflict: a {GUARD_EVENT_CONTRACT} for "
            f"(packet_id={packet_id!r}, attempt={attempt}, kind={kind!r}) "
            f"already exists at {durable_path.relative_to(root).as_posix()}; "
            "refusing to overwrite the durable evidence\n")
        return 2

    guards_dir.mkdir(parents=True, exist_ok=True)
    durable_path.write_text(
        json.dumps(event, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8")

    # D7/invariant 5: consult 002's receipt before repeating; only SIGNAL.
    receipt_ref = _find_receipt(root, execution_id, packet_id)
    reconciled = receipt_ref is not None

    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record": RECORD_CONTRACT,
        "event": event,
        "durable": durable_path.relative_to(root).as_posix(),
        "reconciled": reconciled,
        "receipt_ref": receipt_ref,
        "do_not_repeat": reconciled,
    }
    sys.stdout.write(json.dumps(envelope, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")
    return 0


def _cmd_budget(args: argparse.Namespace) -> int:
    root = Path(args.project_root)
    exec_path = Path(args.execution_context)
    if not exec_path.is_absolute():
        exec_path = root / exec_path
    try:
        exec_context = _load_json(exec_path)
    except OSError as exc:
        sys.stderr.write(
            f"cdad_guard: cannot read execution context {exec_path}: "
            f"{exc.strerror or exc}\n")
        return 2
    except ValueError:
        sys.stderr.write(
            f"cdad_guard: invalid JSON in execution context {exec_path}\n")
        return 2

    execution_id = exec_context.get("execution_id") \
        if isinstance(exec_context, dict) else None
    if not isinstance(execution_id, str) or not execution_id.strip():
        sys.stderr.write(
            "cdad_guard: execution context lacks a valid execution_id\n")
        return 2

    packet_id = args.packet
    attempts = _collect_attempts(root, execution_id, packet_id)
    consumed = len(attempts)
    max_attempts = _max_attempts(exec_context)
    # D3: reaching the declared limit is a signal to reconsider (escalate), not
    # a violation nor an automatic hard block.
    exhausted = max_attempts is not None and consumed >= max_attempts
    envelope: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "budget": BUDGET_CONTRACT,
        "execution_id": execution_id,
        "packet_id": packet_id,
        "attempts": attempts,
        "consumed": consumed,
        "exhausted": exhausted,
        "reconsider": exhausted,
    }
    sys.stdout.write(json.dumps(envelope, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "classify":
        return _cmd_classify(args)
    if args.command == "preflight":
        return _cmd_preflight(args)
    if args.command == "record":
        return _cmd_record(args)
    if args.command == "budget":
        return _cmd_budget(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
