#!/usr/bin/env python3
"""T5 evidence recorder: OpenCode DB -> CDAD guard `trace-v1`.

Read-only over the OpenCode SQLite database. Emits one `trace-v1` document
(matching `skills/cdad-cycle/assets/guard-trace.schema.json`) consumed by
`scripts/cdad_guard.py classify`.

Usage:
    python3 recorder.py --session <ses_...> --out <path.json>
                        [--db file:<home>/.local/share/opencode/opencode.db?mode=ro]

Argument canonicalization is this recorder's responsibility (the guard hashes
args as recorded): only stable fields are emitted, so identical repeated calls
produce byte-identical `args`.

Real-schema notes (probed live, see T5 report): in this DB version a tool part
carries its timing at the PART level (`part["time"] = {created, ran, completed}`)
and `state` exposes only `{status, input, content, metadata}` (no `state.error`,
no `state.time`). User/system prompts store their text in the top-level `text`
field (not `content[]` parts). The recorder accepts both the documented shape
and the observed shape rather than guessing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any

DEFAULT_DB = "file:<home>/.local/share/opencode/opencode.db?mode=ro"

# Tools whose target path(s) count as observable progress (cumulative set).
WRITE_TOOLS = frozenset({"write", "edit", "patch", "multiedit", "create"})

# Volatile input keys that must never participate in the fallback fingerprint.
VOLATILE_KEYS = frozenset({
    "id", "callID", "callId", "call_id", "time", "metadata", "output",
    "title", "tokens", "cost", "sessionID", "messageID",
})


# ------------------------------------------------------------------ extraction


def _rows_for_session(cur: sqlite3.Cursor, session_id: str) -> list[sqlite3.Row]:
    """Message rows for a session, ordered by seq (fallback time_created, id)."""
    return list(cur.execute(
        "SELECT id, session_id, type, seq, time_created, time_updated, data "
        "FROM session_message WHERE session_id = ? "
        "ORDER BY seq, time_created, id",
        (session_id,),
    ))


def _iter_tool_parts(message: dict[str, Any]):
    """Yield each `type=="tool"` content part of an assistant message."""
    content = message.get("content")
    if not isinstance(content, list):
        return
    for part in content:
        if isinstance(part, dict) and part.get("type") == "tool":
            yield part


def _tool_name(part: dict[str, Any]) -> str:
    name = part.get("name")
    if isinstance(name, str) and name:
        return name
    fallback = part.get("tool")
    if isinstance(fallback, str) and fallback:
        return fallback
    return "unknown"


def _state(part: dict[str, Any]) -> dict[str, Any]:
    state = part.get("state")
    return state if isinstance(state, dict) else {}


def _input(part: dict[str, Any]) -> dict[str, Any]:
    value = _state(part).get("input")
    return value if isinstance(value, dict) else {}


def _as_paths(value: Any) -> list[str]:
    """Normalize a path input (str or list of str) to a sorted, deduped list."""
    if isinstance(value, str) and value:
        return [value]
    if isinstance(value, list):
        paths = [v for v in value if isinstance(v, str) and v]
        return sorted(set(paths))
    return []


def _target_paths(tool: str, payload: dict[str, Any]) -> list[str]:
    """Deterministic file target(s) for a tool input, sorted and deduped."""
    if tool in ("read", "write", "edit", "patch", "multiedit", "create"):
        for key in ("filePath", "path", "file_path"):
            paths = _as_paths(payload.get(key))
            if paths:
                return paths
        return []
    if tool == "glob":
        return _as_paths(payload.get("path"))
    if tool == "grep":
        return _as_paths(payload.get("path"))
    return []


def canonical_args(tool: str, payload: dict[str, Any]) -> list[str]:
    """Canonicalized, stable `args` list for one tool call.

    Deterministic: identical repeated calls yield byte-identical lists.
    """
    if tool in ("shell", "bash"):
        command = payload.get("command")
        if isinstance(command, str) and command:
            return [command]
        description = payload.get("description")
        if isinstance(description, str) and description:
            return [description]
        return []

    if tool in ("read", "write", "edit", "patch", "multiedit", "create"):
        return _target_paths(tool, payload)

    if tool in ("glob", "grep"):
        args: list[str] = []
        pattern = payload.get("pattern")
        if isinstance(pattern, str) and pattern:
            args.append(pattern)
        path = payload.get("path")
        if isinstance(path, str) and path:
            args.append(path)
        return args

    if tool == "webfetch":
        url = payload.get("url")
        return [url] if isinstance(url, str) and url else []

    if tool == "task":
        description = payload.get("description")
        return [description] if isinstance(description, str) and description else []

    # Fallback: deterministic scalar fields only, sorted by key.
    args = []
    for key in sorted(payload):
        if key in VOLATILE_KEYS:
            continue
        value = payload[key]
        if isinstance(value, bool):
            args.append(f"{key}={value}")
        elif isinstance(value, (str, int, float)) and value is not None:
            args.append(f"{key}={value}")
        elif value is None:
            args.append(f"{key}=None")
    return args


def result_class(part: dict[str, Any]) -> str:
    """Closed mapping from `state.status` / `state.error`."""
    state = _state(part)
    status = state.get("status")
    if status == "completed":
        return "ok"
    if status == "error":
        error = state.get("error")
        etype = error
        if isinstance(error, dict):
            etype = error.get("type")
        if isinstance(etype, str) and "permission" in etype.lower():
            return "permission-rejected"
        return "tool-error"
    # pending / running / anything without a terminal outcome observed.
    return "unknown"


def _entry_time(part: dict[str, Any]) -> str | None:
    """ISO-8601 UTC from state.time (documented) or part.time (observed)."""
    state = _state(part)
    candidates = []
    state_time = state.get("time")
    if isinstance(state_time, dict):
        candidates.append(state_time)
    part_time = part.get("time")
    if isinstance(part_time, dict):
        candidates.append(part_time)
    for timing in candidates:
        for key in ("completed", "created"):
            ms = timing.get(key)
            if isinstance(ms, (int, float)) and not isinstance(ms, bool):
                return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
    return None


# ------------------------------------------------------------------ prompt ids


_ID_KEYS = ("execution_id", "packet_id", "packet-id", "packetid")


def _message_text(message: dict[str, Any]) -> str:
    """All prompt text of a user/system message.

    Handles both the documented `content[]` text parts and the observed
    top-level `text` field.
    """
    chunks: list[str] = []
    text = message.get("text")
    if isinstance(text, str) and text:
        chunks.append(text)
    content = message.get("content")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                value = part.get("text")
                if isinstance(value, str) and value:
                    chunks.append(value)
    return "\n".join(chunks)


def _id_patterns(key: str) -> list[re.Pattern[str]]:
    escaped = re.escape(key)
    return [
        # <execution_id>value</execution_id>
        re.compile(r"<" + escaped + r">\s*([^<\s]+)\s*</" + escaped + r">", re.I),
        # "execution_id": "value"  /  execution_id: value  /  \"packet-id\"=\"value\"
        re.compile(
            r'\\?"?' + escaped + r'\\?"?\s*[:=]\s*\\?["\']?\s*'
            r"([A-Za-z0-9][A-Za-z0-9._-]*)",
            re.I,
        ),
    ]


def _canonical_key(key: str) -> str:
    if key in ("packet-id", "packetid"):
        return "packet_id"
    return key


def extract_ids(messages: list[dict[str, Any]]) -> dict[str, str]:
    """execution_id / packet_id found in user+system prompt text (tolerant)."""
    text = "\n".join(
        _message_text(m) for m in messages
        if m.get("type") in ("user", "system")
    )
    found: dict[str, str] = {}
    for key in _ID_KEYS:
        canonical = _canonical_key(key)
        if canonical in found:
            continue
        for pattern in _id_patterns(key):
            match = pattern.search(text)
            if match:
                found[canonical] = match.group(1)
                break
    return found


# ------------------------------------------------------------------ trace build


def build_trace(session_id: str, raw_messages: list[dict[str, Any]]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    touched: set[str] = set()
    counter = 0

    for message in raw_messages:
        if message.get("type") != "assistant":
            continue
        for part in _iter_tool_parts(message):
            counter += 1
            tool = _tool_name(part)
            payload = _input(part)
            if tool in WRITE_TOOLS:
                touched.update(_target_paths(tool, payload))

            entry: dict[str, Any] = {
                "i": counter,
                "kind": "tool_call",
                "tool": tool,
                "args": canonical_args(tool, payload),
                "result_class": result_class(part),
            }
            if touched:
                digest = hashlib.sha256(
                    "\n".join(sorted(touched)).encode("utf-8")
                ).hexdigest()
                entry["progress_token"] = "sha256:" + digest
            at = _entry_time(part)
            if at is not None:
                entry["at"] = at
            entries.append(entry)

    trace: dict[str, Any] = {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": False,
        "session_id": session_id,
        "entries": entries,
    }
    ids = extract_ids(raw_messages)
    for key in ("execution_id", "packet_id"):
        if key in ids:
            trace[key] = ids[key]
    return trace


# ------------------------------------------------------------------ CLI


def build_trace_from_rows(session_id: str, rows: list[sqlite3.Row]) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    for row in rows:
        try:
            data = json.loads(row["data"])
        except ValueError:
            continue
        if not isinstance(data, dict):
            continue
        data["_column_type"] = row["type"]
        messages.append(data)

    # Reuse build_trace but with the column type authoritative.
    normalized = []
    for m in messages:
        m["type"] = m["_column_type"]
        normalized.append(m)
    return build_trace(session_id, normalized)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="recorder", description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args(argv)

    try:
        connection = sqlite3.connect(args.db, uri=True)
        connection.row_factory = sqlite3.Row
    except sqlite3.Error as exc:
        sys.stderr.write(f"recorder: cannot open db {args.db}: {exc}\n")
        return 2

    try:
        with connection:
            rows = _rows_for_session(connection.cursor(), args.session)
            trace = build_trace_from_rows(args.session, rows)
    except sqlite3.Error as exc:
        sys.stderr.write(f"recorder: query failed: {exc}\n")
        return 2
    finally:
        connection.close()

    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(trace, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
