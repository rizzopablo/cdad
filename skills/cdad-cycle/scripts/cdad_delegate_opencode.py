#!/usr/bin/env python3
"""CDAD OpenCode destination adapter (005-009 T2; PD-4, PD-5, PD-6, PD-7).

Destination adapter resolved by the common delegation interface by module
convention (`cdad_delegate_<id>.py` next to `cdad_delegate.py`, PD-1). The
interface runs this module as a subprocess with the published `PACKET.md` bytes
on stdin and `--project-root`, `--packet-id`, `--destination` and
`--exec-config` on argv, and reads ONE JSON envelope
`{attempt, session, termination, delivery_ref, diagnosis}` from stdout (see
`references/cli-delegation.md`).

What this adapter does, and why (contract decisions D5/D6):

1. It builds the destination invocation FROM THE EXECUTION CONFIGURATION
   (`binary`, `binary_version`, `model`, `logs_dir`, `wait.timeout_seconds`):
   nothing about the CLI, the binary, the model or the times is hardcoded here
   (PD-8/INV-7). `runtime`/`model` also feed the I8 observation.
2. It VERIFIES THE PUBLISHED DERIVED AGENT (PD-3) the project published under
   `.opencode/agents/` (I9): the derived `cdad-<role>.md` must be published. Its
   `mode:` NO LONGER conditions the dispatch (the installed runtime accepts
   `mode: subagent` as a non-interactive CLI entry); the role identity is
   verified from the durable row (`session_v2.agent == "cdad-<role>"`) once the
   session is correlated. A missing derived agent FAILS CLOSED before dispatch
   and a durable row declaring another agent FAILS CLOSED too; in both cases the
   adapter NEVER falls back to a generic non-Cdad agent.
3. It chooses the session id itself and passes it in `--session <id>` so the
   durable session gets correlated UNAMBIGUOUSLY (PD-1), then invokes the
   configured binary transporting the packet bytes byte-identical (stdin) with
   the server/permission mode at the right level (PD-4: `--server <url>` taken
   from the configuration as an alternative to the `--standalone` default, never
   both, and `--auto` enabled by default; `--auto` auto-approves non-denied
   permissions and is NOT a sandbox, INV-8) and WAITS ON THE DURABLE SIGNAL,
   NOT on the client rc (PD-5/D6), for a bounded time. The durable signal is
   the runtime's own session store (`sessions_db`,
   a configurable path) opened READ ONLY (SQLite URI `mode=ro`; never
   `immutable`, never written): the correlated `session_v2` row carries the
   chosen id and its `idle_outcome` is the material end-of-run fact. No
   invented completion signal and no promised callback.
4. It CLASSIFIES the termination from material facts (PD-5/D6): `completed`
   (`idle_outcome = succeeded` + the final text taken from the LAST `assistant`
   `session_message`), `blocked` (`failed`, or `succeeded` without final text),
   `cancelled` (`interrupted`), `transport-error` (client failed in transport
   before any session row) or `timeout` (no idle within the bounded wait). An
   unreadable/non-SQLite store or one missing the required schema FAILS CLOSED
   with a diagnosis that names what is missing (PD-2), without waiting longer.
   Only `completed` persists the durable delivery through the existing `receive`
   flow; the receipt stays `semantic_status: "pending"` (delivery is NOT a gate,
   INV-5) and no non-completed termination fabricates a receipt. The receive
   flow (its CLI and the packet instructions it renders from) is resolved from
   the CDAD skill tree the adapter ships in. The state is never written here
   beyond the reused dispatch mechanism.

Honest limits: a separate process/session is not a sandbox (INV-8); the durable
signal surface implemented here is the session store the execution
configuration points at, read only; no scheduler, CLI installation or sandbox is
built (INV-9).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# The canonical CLIs live next to this adapter; importing them (never
# re-running) reuses the reception flow and the packet validators.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_result  # noqa: E402

DESTINATION_ID = "opencode"
# The derived agents the project publishes under this relpath (I9): their
# presence gates dispatch (PD-3); their `mode:` no longer does.
DERIVED_AGENTS_RELPATH = Path(".opencode") / "agents"
PACKET_CLI_NAME = "cdad_packet.py"
RESULT_CLI_NAME = "cdad_result.py"
PACKET_INSTRUCTIONS_NAME = "common.md"
# The adapter must answer inside the interface's own bound on this process
# (the same `wait.timeout_seconds`): its startup, the destination invocation,
# the bounded wait AND the classification/persistence through the reused
# `receive` flow all fit inside that bound, so the interface is never the one
# that kills this adapter. This fixed reserve covers that overhead (measured
# ~0.7s: startup + the destination subprocess + the receive subprocesses) and
# leaves the remaining budget to bound the destination invocation and the wait
# (PD-5).
WAIT_RESERVE_SECONDS = 1.0
POLL_INTERVAL_SECONDS = 0.05
FINAL_TEXT_PART = "final-text"
FINAL_TEXT_ARTIFACT_KIND = "role-report"
RECEIPT_NAME = "receipt.json"

# 006-001 T1 (PD-1/PD-2): execution-mode selection and the server preflight.
OPENCODE_PASSWORD_ENV = "OPENCODE_PASSWORD"
OPENCODE_SERVER_PASSWORD_ENV = "OPENCODE_SERVER_PASSWORD"
VALID_MODE_VALUES = ("server", "standalone")
WAIT_NUMERIC_KEYS = (
    "poll_initial_seconds", "poll_max_seconds", "settle_seconds",
    "terminate_grace_seconds", "preflight_timeout_seconds",
)
DEFAULT_WAIT_VALUES = {
    "poll_initial_seconds": 1.0,
    "poll_max_seconds": 15.0,
    "settle_seconds": 30.0,
    "terminate_grace_seconds": 5.0,
    "preflight_timeout_seconds": 5.0,
}
# Spec §2.3 point 1: the first semver token in the (acotada) `--version` output.
SEMVER_RE = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")

# PD-1/PD-2: the durable signal is the runtime's OWN session store, opened
# READ ONLY (URI `mode=ro`, never `immutable`, never written). The adapter
# chooses the session id and correlates by it unambiguously; the store and its
# schema are observed facts (discovery §3.4), never a public contract, so an
# unknown/degraded store FAILS CLOSED with a diagnosis that names what is
# missing (PD-2). The observed OpenCode v2 schema:
#   session_v2(id, agent, model, ..., time_idle, idle_outcome)
#   session_message(id, session_id, type, seq, data JSON)
SESSION_ID_PREFIX = "ses_"
SESSION_V2_TABLE = "session_v2"
SESSION_MESSAGE_TABLE = "session_message"
SESSION_V2_COLUMNS = ("id", "agent", "model", "time_idle", "idle_outcome")
SESSION_MESSAGE_COLUMNS = ("id", "session_id", "type", "seq", "data")
IDLE_OUTCOME_SUCCEEDED = "succeeded"
IDLE_OUTCOME_FAILED = "failed"
IDLE_OUTCOME_INTERRUPTED = "interrupted"


class AdapterError(RuntimeError):
    """Fail-closed diagnostic of the OpenCode adapter."""


class DestinationTimeoutError(AdapterError):
    """The destination invocation did not return within the bounded wait.

    R1: this is the material fact ABSENCE-OF-SIGNAL-WITHIN-THE-BOUND, not a
    transport failure. The client never returned a return code (the adapter
    killed it at the bound), so the classification is `timeout` and the
    diagnosis must never claim an `rc` that was never observed (PD-5/PD-1).
    """


class _StoreBusy(Exception):
    """The session store was momentarily locked/busy: retry within the bound.

    Internal sentinel only (never leaves the adapter): a `locked`/`busy`
    SQLite result is NOT a fail-closed fact, it is transient contention with
    the live runtime (R-G), so the waiter retries until the bounded deadline.
    """


def _choose_session_id() -> str:
    """The session id the adapter chooses and correlates by (PD-1/R-F).

    A safe alphabet with the `ses_` prefix (the runtime accepts it in
    `--session`); the adapter, not the client, owns the correlation id.
    """
    return f"{SESSION_ID_PREFIX}{uuid.uuid4().hex}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _model_reported_from_row(model_value: Any) -> str | None:
    """Normalize the durable row's `model` into a useful I8 observation (R2).

    PD-6: `model_reported` is observability of the WORKER attempt. When the
    row serializes the model as a JSON object ``{"id": ..., "providerID":
    ...}`` (the shape the real runtime reports), the useful form is
    ``providerID/id`` -- never the verbatim JSON blob. A plain-text model is
    preserved as-is (the normalization only applies to the object shape).
    """
    text = _as_text(model_value)
    if text is None:
        return None
    try:
        document = json.loads(text)
    except (TypeError, ValueError):
        return text
    if isinstance(document, dict):
        provider = _as_text(document.get("providerID"))
        model_id = _as_text(document.get("id"))
        if provider is not None and model_id is not None:
            return f"{provider}/{model_id}"
    return text


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AdapterError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise AdapterError(f"{label} is not readable JSON: {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise AdapterError(f"{label} must be a JSON object: {path}")
    return document


# ------------------------------------------------------------ derived agents


def _entry_agent_name(role: str) -> str:
    return f"cdad-{role}"


def _check_derived_agent_published(project_root: Path, role: str) -> str | None:
    """Verify the derived `cdad-<role>` agent is published (PD-3).

    Returns `None` when the derived agent is published, or an actionable
    diagnosis that names the missing agent (fail closed BEFORE dispatching).

    PD-3: the derived entry's `mode:` NO LONGER conditions the dispatch (the
    installed runtime accepts `mode: subagent` as a non-interactive CLI entry);
    the barrier is the durable identity
    (`session_v2.agent == "cdad-<role>"`), verified once the session is
    correlated. A missing derived agent is still a pre-dispatch fail-closed
    fact and NEVER falls back to a generic non-Cdad agent.
    """
    agent = _entry_agent_name(role)
    entry = project_root / DERIVED_AGENTS_RELPATH / f"{agent}.md"
    if entry.is_file():
        return None
    return (
        f"the derived agent {agent!r} is not published: expected {agent}.md "
        f"under {DERIVED_AGENTS_RELPATH.as_posix()}/ (published by prepare, "
        f"I9). Refusing to dispatch a non-interactive session and refusing "
        f"any fallback to a generic non-Cdad agent; publish the derived agent "
        f"before delegating.")


def _check_durable_identity(row: dict[str, Any], role: str) -> str | None:
    """Verify the correlated durable row declares the role identity (PD-3).

    Returns `None` when `session_v2.agent == cdad-<role>`, or an actionable
    diagnosis that names BOTH agents (the row's and the expected `cdad-<role>`)
    when they differ. The identity is the barrier, not the CLI `mode`; there is
    never a fallback to a generic non-Cdad agent.
    """
    expected = _entry_agent_name(role)
    declared = _as_text(row.get("agent"))
    if declared == expected:
        return None
    return (
        f"the correlated durable session row declares agent {declared!r}, not "
        f"the expected {expected!r} (PD-3: the role identity is verified from "
        f"the durable row, session_v2.agent). Refusing to declare a delivery "
        f"and refusing any fallback to a generic non-Cdad agent; reconcile the "
        f"session/agent before repeating the delegation.")


# ------------------------------------------------------- destination process


def _invoke_destination(binary: str, agent: str, model: str | None,
                        packet_bytes: bytes, cwd: Path,
                        timeout: float | None,
                        session_id: str, *,
                        server: str | None,
                        auto: bool) -> subprocess.CompletedProcess:
    """Invoke the configured binary, transporting the packet bytes on stdin.

    The adapter chooses the session id and passes `--session <id>` so the
    durable row is correlatable unambiguously (PD-1).

    PD-4: the server/permission mode comes from the execution configuration at
    the right level, never hardcoded -- `--server <url>` when the configuration
    declares it (alternative to `--standalone`, never both), `--standalone` by
    default (private server; never the owner's background service), and `--auto`
    (non-interactive permissions; auto-approval of non-denied permissions, NOT
    a sandbox -- INV-8) enabled by default.
    """
    argv = [binary, "run", "--agent", agent, "--session", session_id]
    if server:
        argv += ["--server", server]
    else:
        argv += ["--standalone"]
    if auto:
        argv += ["--auto"]
    if model:
        argv += ["--model", model]
    # OpenCode v2.0.26 (verified fact) derives the PROJECT DIRECTORY from the
    # PWD environment variable, NOT from the process cwd: pin PWD to the
    # project root of this delegation so the destination session runs in the
    # EXPLICIT project (PD-3 of 005-009 / PD-4) regardless of the PWD the
    # coordinator inherited. Never a resource-resolution source: PWD is only
    # set for the destination process, never read (PD-3/PD-8).
    env = dict(os.environ)
    env["PWD"] = str(cwd)
    try:
        return subprocess.run(argv, input=packet_bytes, capture_output=True,
                              cwd=str(cwd), timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        # R1: the invocation did NOT return within the bound; the client
        # never reported a return code (the adapter killed it). This is the
        # material fact `timeout`, NOT a transport failure with a fabricated
        # rc (PD-5/PD-1).
        raise DestinationTimeoutError(
            f"destination binary {binary!r} did not return within the bounded "
            f"wait ({timeout} seconds); the client was killed at the bound and "
            f"no return code was ever observed, so no rc is claimed; the "
            f"absence of a durable signal within the bound is a timeout (no "
            f"receipt is fabricated; reconcile before repeating)") from exc
    except OSError as exc:
        # R1 (contracara): the binary could not be STARTED -- a real
        # transport failure observed before any session row (PD-5).
        raise AdapterError(
            f"destination binary {binary!r} could not be started: {exc}") from exc


# ----------------------------------------------------------- durable signal


def _query(conn: sqlite3.Connection, sql: str,
           params: tuple[Any, ...] = ()) -> sqlite3.Cursor:
    """Run one read query, mapping transient contention to `_StoreBusy`.

    A `locked`/`busy` SQLite result while the live runtime writes is transient
    (R-G): the waiter retries within the bounded deadline instead of failing
    closed. Every other error propagates to the fail-closed handler (PD-2).
    """
    try:
        return conn.execute(sql, params)
    except sqlite3.OperationalError as exc:
        message = str(exc).lower()
        if "locked" in message or "busy" in message:
            raise _StoreBusy(str(exc)) from exc
        raise


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cursor = _query(conn, f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def _validate_store_schema(conn: sqlite3.Connection, store_path: Path) -> None:
    """Fail closed (naming what is missing) when the store schema is unknown.

    The schema is an OBSERVED fact, not a public contract (PD-2/R-D): a store
    that lacks the required tables/columns gets an actionable diagnosis that
    NAMES them, and the adapter neither fabricates a delivery nor degrades the
    known fact into a timeout."""
    missing: list[str] = []
    for table, required in ((SESSION_V2_TABLE, SESSION_V2_COLUMNS),
                            (SESSION_MESSAGE_TABLE, SESSION_MESSAGE_COLUMNS)):
        columns = _table_columns(conn, table)
        if not columns:
            missing.append(f"table {table!r}")
            continue
        for column in required:
            if column not in columns:
                missing.append(f"{table}.{column}")
    if missing:
        raise AdapterError(
            f"the durable session store {store_path} lacks the required schema "
            "(observed OpenCode v2 session store; sessions_db from the "
            f"execution configuration): missing {', '.join(missing)}. Refusing "
            "to read an unknown schema, to fabricate a delivery or to degrade "
            "this known fact into a timeout.")


def _fetch_session_row(conn: sqlite3.Connection,
                       session_id: str) -> dict[str, Any] | None:
    cursor = _query(conn, f"SELECT * FROM {SESSION_V2_TABLE} WHERE id = ?",
                    (session_id,))
    columns = [description[0] for description in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row is not None else None


def _text_from_message_data(data: Any) -> str | None:
    """The `text` parts of a `session_message.data` JSON document (PD-1)."""
    try:
        document = json.loads(data) if isinstance(data, str) else data
    except (TypeError, ValueError) as exc:
        raise AdapterError(
            f"the durable session store carries a session_message whose data "
            f"is not parseable JSON: {exc}") from exc
    if not isinstance(document, dict):
        return None
    parts = document.get("content")
    if not isinstance(parts, list):
        return None
    texts = [
        part.get("text") for part in parts
        if isinstance(part, dict) and part.get("type") == "text"
        and isinstance(part.get("text"), str) and part.get("text")]
    return "\n".join(texts) if texts else None


def _last_assistant_text(conn: sqlite3.Connection,
                         session_id: str) -> str | None:
    """The text of the LAST `assistant` message of the correlated session.

    PD-1: the final text is the last `assistant` message's
    `data.content[].text` (type `text`); an earlier intermediate assistant
    decoy never travels. PD-5: if THAT last assistant carries no text part,
    the final text is absent (None) — an earlier assistant's text never
    substitutes the missing delivery.
    """
    cursor = _query(
        conn,
        f"SELECT data FROM {SESSION_MESSAGE_TABLE} "
        "WHERE session_id = ? AND type = 'assistant' "
        "ORDER BY seq DESC LIMIT 1",
        (session_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return _text_from_message_data(row[0])


def _store_state(store_path: Path, session_id: str) -> dict[str, Any]:
    """Read the correlated session state from the store READ ONLY (PD-1/PD-2).

    Returns `{"kind": "idle"|"no-idle"|"no-row", "row": ..., "final_text": ...}`.
    Raises `AdapterError` (fail closed, no waiting) when the store does not
    exist, is not readable SQLite or lacks the required schema; raises
    `_StoreBusy` on transient lock contention so the waiter can retry.
    """
    if not store_path.is_file():
        raise AdapterError(
            f"the durable session store {store_path} declared by the execution "
            "configuration (sessions_db) does not exist: cannot correlate a "
            "material signal (fail closed; no delivery is fabricated and this "
            "known fact is not degraded into a timeout)")
    try:
        # READ ONLY: URI `mode=ro`; NEVER `immutable` (it would mask the live
        # runtime's updates, R-G) and NEVER a writable connection (INV-3).
        conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    try:
        _validate_store_schema(conn, store_path)
        row = _fetch_session_row(conn, session_id)
        if row is None:
            return {"kind": "no-row", "row": None, "final_text": None}
        if row.get("idle_outcome") is None:
            return {"kind": "no-idle", "row": row, "final_text": None}
        return {"kind": "idle", "row": row,
                "final_text": _last_assistant_text(conn, session_id)}
    except (AdapterError, _StoreBusy):
        raise
    except sqlite3.OperationalError as exc:
        message = str(exc).lower()
        if "locked" in message or "busy" in message:
            raise _StoreBusy(str(exc)) from exc
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    except sqlite3.DatabaseError as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not a SQLite database "
            f"or is unreadable: {exc}") from exc
    finally:
        conn.close()


def _await_durable_outcome(store_path: Path, session_id: str,
                           returncode: int, deadline: float) -> dict[str, Any]:
    """Wait on the DURABLE signal (never the client rc) up to the bound.

    A store/schema failure is a KNOWN fact: it fails closed immediately, without
    exhausting the wait (PD-2). While the store is valid but the correlated row
    is not yet idle, the adapter waits up to the bounded deadline; a client
    that already ended with a non-zero rc and left no row is a material
    transport failure (PD-5).
    """
    while True:
        try:
            state = _store_state(store_path, session_id)
        except _StoreBusy:
            state = None
        if state is not None:
            kind = state["kind"]
            if kind == "idle":
                return {"kind": "idle", "row": state["row"],
                        "final_text": state["final_text"]}
            if kind == "no-row" and returncode != 0:
                return {"kind": "transport-error"}
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {"kind": "timeout"}
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))


def _wait_budget(timeout: float | None) -> float | None:
    if timeout is None:
        return None
    return max(0.0, timeout - WAIT_RESERVE_SECONDS)


# --------------------------------------------- 006-001 T1: mode selection


def _validate_wait_keys(wait: dict[str, Any]) -> str | None:
    """Validate the new `wait.*` keys (spec §2.1), if present.

    Returns an actionable diagnosis naming the offending key, or `None` when
    every declared key is a positive number and `poll_max_seconds >=
    poll_initial_seconds`. Called BEFORE the packet request is loaded: a
    malformed config never reaches the point where a worker attempt could be
    registered (nothing is invoked, nothing is dispatched).
    """
    values: dict[str, float] = {}
    for key in WAIT_NUMERIC_KEYS:
        if key not in wait:
            continue
        raw_value = wait[key]
        if (isinstance(raw_value, bool)
                or not isinstance(raw_value, (int, float))
                or raw_value <= 0):
            return (
                f"invalid `wait.{key}`: expected a positive number, got "
                f"{raw_value!r} (spec §2.1)")
        values[key] = float(raw_value)
    poll_initial = values.get(
        "poll_initial_seconds", DEFAULT_WAIT_VALUES["poll_initial_seconds"])
    poll_max = values.get(
        "poll_max_seconds", DEFAULT_WAIT_VALUES["poll_max_seconds"])
    if poll_max < poll_initial:
        return (
            f"invalid `wait.poll_max_seconds` ({poll_max!r}): must be >= "
            f"`wait.poll_initial_seconds` ({poll_initial!r}) (spec §2.1)")
    return None


def _validate_mode_value(raw_mode: Any) -> tuple[str, str | None]:
    """Validate the `mode` config key (spec §2.1/§2.2).

    Returns (`mode_requested`, diagnosis). `mode_requested` is one of
    `server`/`standalone`/`undeclared`; a non-`None` diagnosis means the
    declared value is outside the set and the caller must block before the
    packet request is loaded (no registration possible or needed).
    """
    if raw_mode is None:
        return "undeclared", None
    if raw_mode not in VALID_MODE_VALUES:
        return "undeclared", (
            f"invalid `mode` value {raw_mode!r}: expected one of "
            f"{VALID_MODE_VALUES!r} (spec §2.1)")
    return raw_mode, None


def _valid_server_url(value: str) -> bool:
    """URL válida (spec §2.2): http/https, con host, sin userinfo."""
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False
    return True


def _resolve_mode_effective(mode_requested: str, server_raw: str | None) -> str:
    """Spec §2.2 selection table. Returns `server`/`standalone`/`none`.

    `none` means `mode: server` (declared or by compatibility, since a
    `server` key present with `mode` undeclared is treated as an intended
    server mode, INV-2: no silent fallback to standalone on a bad URL) was
    requested without a valid URL: `blocked` before any invocation.
    """
    if mode_requested == "standalone":
        return "standalone"
    server_valid = server_raw is not None and _valid_server_url(server_raw)
    if mode_requested == "server":
        return "server" if server_valid else "none"
    # undeclared (compatibility, D-1): a declared (even if invalid) `server`
    # is treated as an intended server mode, never a silent standalone
    # fallback (INV-2); only its TRUE absence keeps the standalone default.
    if server_raw is None:
        return "standalone"
    return "server" if server_valid else "none"


def _parse_semver(text: str | None) -> str | None:
    """First semver token (spec §2.3 point 1), or `None` if unparseable."""
    if not text:
        return None
    match = SEMVER_RE.search(text)
    return match.group(0) if match else None


def _preflight_password() -> str | None:
    """Spec §2.3 point 2: `OPENCODE_PASSWORD`, then `OPENCODE_SERVER_PASSWORD`.

    The first one PRESENT in the environment wins, even if it later turns out
    to be wrong (never falls through to the second once the first is set).
    `None` means no credential is sent (no header), never an empty string.
    """
    value = os.environ.get(OPENCODE_PASSWORD_ENV)
    if value is not None:
        return value
    return os.environ.get(OPENCODE_SERVER_PASSWORD_ENV)


def _invoke_version(binary: str, timeout: float) -> tuple[str | None, str | None]:
    """`binary --version` (D-2: only in server mode), bounded.

    Returns (raw_output, diagnosis); a non-`None` diagnosis means the client
    version could not be observed (binary could not be started, or did not
    answer within the bound) -- a transport fact (PD-2 row 1).
    """
    try:
        proc = subprocess.run(
            [binary, "--version"], capture_output=True,
            stdin=subprocess.DEVNULL, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, (
            f"destination binary {binary!r} did not answer `--version` "
            f"within the preflight bound ({timeout} seconds)")
    except OSError as exc:
        return None, f"destination binary {binary!r} could not be started: {exc}"
    output = (proc.stdout or b"").decode("utf-8", errors="replace")
    output += "\n" + (proc.stderr or b"").decode("utf-8", errors="replace")
    return output, None


def _preflight_get_info(server_url: str, password: str | None,
                        timeout: float) -> dict[str, Any]:
    """`GET <server>/api/info` (spec §2.3 point 2), bounded, Basic auth.

    Never honors a host HTTP(S) proxy: a proxy would both break the loopback
    server and leak the Basic credential to a third party. Returns a `kind`
    discriminant: `transport-error`/`unauthorized`/`not-found`/`no-json`/
    `no-version`/`ok` (with `version_raw` when `ok`).
    """
    url = server_url.rstrip("/") + "/api/info"
    request = urllib.request.Request(url, method="GET")
    if password is not None:
        token = base64.b64encode(
            f"opencode:{password}".encode("utf-8")).decode("ascii")
        request.add_header("Authorization", f"Basic {token}")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            body = exc.read()
        except OSError:
            body = b""
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"kind": "transport-error", "detail": str(exc)}
    if status in (401, 403):
        return {"kind": "unauthorized"}
    if status != 200:
        return {"kind": "not-found"}
    try:
        document = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {"kind": "no-json"}
    if not isinstance(document, dict):
        return {"kind": "no-json"}
    version_value = document.get("version")
    if not isinstance(version_value, str) or not version_value:
        return {"kind": "no-version"}
    return {"kind": "ok", "version_raw": version_value}


def _preflight_server(binary: str, server_raw: str, timeout: float,
                      binary_version_configured: str | None) -> dict[str, Any]:
    """Spec §2.3: client version, then `GET /api/info`, within `timeout`.

    Returns {"ok", "termination", "diagnosis", "client_version",
    "server_version"}. `client_version` is always the OBSERVED `--version`
    fact (I8 provenance); the comparison against the server also considers
    `binary_version` when the config declares it and it is parseable (spec
    §2.3 row 4).
    """
    version_output, version_diag = _invoke_version(binary, timeout)
    if version_diag is not None:
        return {"ok": False, "termination": "transport-error",
                "diagnosis": version_diag, "client_version": None,
                "server_version": None}
    observed_client_version = _parse_semver(version_output)
    configured_client_version = _parse_semver(binary_version_configured)

    info = _preflight_get_info(server_raw, _preflight_password(), timeout)
    kind = info["kind"]
    if kind == "transport-error":
        return {"ok": False, "termination": "transport-error",
                "diagnosis": (
                    "the configured server is not reachable (servidor "
                    "configurado no alcanzable): prepare a compatible server "
                    "or declare `mode: standalone`"),
                "client_version": observed_client_version,
                "server_version": None}
    if kind == "unauthorized":
        return {"ok": False, "termination": "blocked",
                "diagnosis": (
                    "the server rejected or required a credential (401/403; "
                    "credencial ausente o rechazada): the password is read "
                    f"from {OPENCODE_PASSWORD_ENV}, then "
                    f"{OPENCODE_SERVER_PASSWORD_ENV} (never its value)"),
                "client_version": observed_client_version,
                "server_version": None}
    if kind in ("not-found", "no-json", "no-version"):
        return {"ok": False, "termination": "blocked",
                "diagnosis": (
                    "the configured server has no compatible V2 info "
                    "(servidor sin información V2 compatible, GET "
                    "/api/info)"),
                "client_version": observed_client_version,
                "server_version": None}
    server_version = _parse_semver(info["version_raw"])
    # Row 5 (§2.3): unparseable somewhere -- the PRIMARY comparands (the
    # observed client version and the server version) must each parse.
    # `binary_version` not parsing only means that extra check (below) is
    # skipped, never a block by itself (spec: "si ... es parseable").
    if observed_client_version is None or server_version is None:
        return {"ok": False, "termination": "blocked",
                "diagnosis": (
                    "versión no verificable: client version "
                    f"{observed_client_version!r}, server version "
                    f"{info['version_raw']!r} is not a parseable semver"),
                "client_version": observed_client_version,
                "server_version": server_version}
    if observed_client_version != server_version:
        return {"ok": False, "termination": "blocked",
                "diagnosis": (
                    f"server version {server_version!r} does not match the "
                    f"observed client version {observed_client_version!r}: "
                    "prepare a matching server or declare "
                    "`mode: standalone`"),
                "client_version": observed_client_version,
                "server_version": server_version}
    # Row 4 (§2.3, second clause): ALSO compared against `binary_version`
    # when the config declares it and it parses -- an inconsistent
    # configuration blocks even when the observed client matches the server.
    if (configured_client_version is not None
            and configured_client_version != server_version):
        return {"ok": False, "termination": "blocked",
                "diagnosis": (
                    f"server version {server_version!r} does not match the "
                    f"configured `binary_version` {configured_client_version!r}"
                    ": prepare a matching server, correct `binary_version` "
                    "or declare `mode: standalone`"),
                "client_version": observed_client_version,
                "server_version": server_version}
    return {"ok": True, "termination": None, "diagnosis": None,
            "client_version": observed_client_version,
            "server_version": server_version}


def _redact_server_url(text: str, server_url: str | None) -> str:
    """PD-5: a client stderr mentioning the configured URL is redacted to
    «servidor configurado» BEFORE entering any diagnosis (spec §2.3 note)."""
    if not text or not server_url:
        return text
    return text.replace(server_url, "servidor configurado")


def _append_note(diagnosis: str | None, note: str | None) -> str | None:
    if note is None:
        return diagnosis
    if diagnosis:
        return f"{diagnosis}; {note}"
    return note


# ------------------------------------------------------------ I8 dispatch


def _observation(runtime: str | None, model: str | None, binary_version: str | None,
                 session: str | None, started_at: str, *,
                 mode_requested: str, mode_effective: str,
                 client_version: str | None, server_version: str | None,
                 session_base: str, row_state: str,
                 model_reported: str | None = None,
                 store_reads: str = "unknown",
                 prior_check_reads: str = "unknown") -> dict[str, Any]:
    """Build the closed-key I8 observation document (PD-3/PD-8).

    PD-6: when the adapter wrote this record for the WORKER attempt, `session`
    and `model_reported` come from the correlated durable row
    (`session_v2.id` / `session_v2.model`) and the provenance declares it;
    `runtime` / `model_configured` keep coming from the execution config.

    006-001 §2.6 (PD-3): the provenance text carries the new pairs in free
    text (the I8 schema stays closed, INV-4). `session_base` is one of the
    three literal alternatives the spec names (`durable session row
    (exec-config: sessions_db): session_v2.id` | `chosen by adapter` | `not
    dispatched`); `row_state` is `present`/`absent`/`unknown` (INV-9: unknown
    is never 0 nor empty). `store_reads`/`prior_check_reads` stay `unknown`
    here: the exact count is T2 scope.
    """
    runtime_provenance = (
        "execution config (--exec-config): runtime; "
        f"mode_requested={mode_requested}; mode_effective={mode_effective}; "
        f"client_version={client_version or 'unknown'}; "
        f"server_version={server_version or 'unknown'}")
    session_provenance = (
        f"{session_base}; store=configured sessions_db; row={row_state}; "
        f"store_reads={store_reads}; prior_check_reads={prior_check_reads}")
    return {
        "runtime": runtime,
        "model_configured": model,
        "model_reported": _as_text(model_reported),
        "session": session,
        "started_at": started_at,
        "provenance": {
            "runtime": runtime_provenance,
            "model_configured": "execution config (--exec-config): model",
            "model_reported": (
                "durable session row (exec-config: sessions_db): "
                "session_v2.model"),
            "session": session_provenance,
            "started_at": (
                "destination adapter clock (UTC); "
                f"binary_version {binary_version or 'unknown'}"
            ),
        },
    }


def _register_dispatch(project_root: Path, packet_id: str, request: dict[str, Any],
                       attempt_id: str, observation: dict[str, Any]) -> None:
    """Register the attempt in the SAME I8 ledger (reused machinery, PD-2)."""
    execution_id = _as_text(request.get("execution_id"))
    if execution_id is None:
        raise AdapterError(f"packet {packet_id!r} request has no execution_id")
    observation_dir = project_root / ".cdad" / "executions" / execution_id
    observation_dir.mkdir(parents=True, exist_ok=True)
    observation_path = observation_dir / f".{attempt_id}.observation.json"
    payload = (json.dumps(observation, ensure_ascii=False, sort_keys=True, indent=2)
               + "\n").encode("utf-8")
    packet_cli = _SCRIPT_DIR / PACKET_CLI_NAME
    if not packet_cli.is_file():
        raise AdapterError(
            f"cannot register the dispatch: {PACKET_CLI_NAME} is not next to "
            "the OpenCode adapter")
    try:
        observation_path.write_bytes(payload)
    except OSError as exc:
        raise AdapterError(f"cannot stage the dispatch observation: {exc}") from exc
    try:
        proc = subprocess.run(
            [sys.executable, str(packet_cli), "prepare",
             "--project-root", str(project_root),
             "--record-dispatch", packet_id,
             "--attempt-id", attempt_id,
             "--input", str(observation_path)],
            capture_output=True, text=True, cwd=str(project_root))
    finally:
        observation_path.unlink(missing_ok=True)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise AdapterError(
            f"dispatch registration failed for attempt {attempt_id!r}: "
            f"{detail[:300]}")


# --------------------------------------------------------- durable delivery


def _is_complete_skill_tree(scripts_dir: Path) -> bool:
    """A skill tree that carries both the receive CLI and the packet instructions."""
    return ((scripts_dir / RESULT_CLI_NAME).is_file()
            and (scripts_dir.parent / "packets" / PACKET_INSTRUCTIONS_NAME).is_file())


def _skill_scripts_dir() -> Path | None:
    """Resolve the CDAD skill tree that carries the receive CLI and the packet
    instructions the reused `receive` flow renders from.

    The adapter ships inside that tree, so its own directory is the ONLY
    source: the installation places the complete skill (scripts/ + packets/ +
    references/ + assets/) co-located with the artifact. Resources are never
    resolved from the coordinator's working directory (PD-3/PD-8); if the
    co-located tree is incomplete the caller fails closed with a diagnosis.
    """
    scripts_dir = Path(__file__).resolve().parent
    if _is_complete_skill_tree(scripts_dir):
        return scripts_dir
    return None


def _run_receive(project_root: Path, execution_id: str, packet_id: str,
                 descriptor_path: Path) -> None:
    """Persist the delivery through the existing `receive` flow (PD-7).

    The receipt stays `semantic_status: "pending"`: the delivery is not a gate
    (INV-5)."""
    scripts_dir = _skill_scripts_dir()
    if scripts_dir is None:
        raise AdapterError(
            "the CDAD skill tree co-located with the OpenCode adapter is "
            f"incomplete: expected {RESULT_CLI_NAME} and "
            f"packets/{PACKET_INSTRUCTIONS_NAME} next to "
            f"{Path(__file__).resolve().parent} (the installation places the "
            "complete skill co-located with the adapter); the delivery cannot "
            "be persisted and no coordinator working directory is used as a "
            "fallback")
    packet_dir = project_root / ".cdad" / "packets" / packet_id
    try:
        proc = subprocess.run(
            [sys.executable, str(scripts_dir / RESULT_CLI_NAME), "receive",
             "--project-root", str(project_root),
             "--execution-context", str(project_root / ".cdad" / "executions"
                                       / execution_id / "execution.json"),
             "--packet", str(packet_dir / "PACKET.md"),
             "--request", str(packet_dir / "REQUEST.json"),
             "--descriptor", str(descriptor_path)],
            capture_output=True, text=True, cwd=str(project_root))
    except OSError as exc:
        raise AdapterError(f"cannot start the receive flow: {exc}") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise AdapterError(f"the receive flow failed: {detail[:300]}")


def _persist_delivery(project_root: Path, packet_id: str, request: dict[str, Any],
                      attempt_id: str, session: str | None,
                      runtime: str | None, model: str | None,
                      binary_version: str | None, started_at: str,
                      final_text: str, *,
                      mode_requested: str, mode_effective: str,
                      client_version: str | None, server_version: str | None,
                      model_reported: str | None = None) -> str:
    """Persist the final text through the existing `receive` flow (PD-7).

    The receipt stays `semantic_status: "pending"` (delivery is not a gate,
    INV-5). Returns the durable receipt path.
    """
    execution_id = _as_text(request.get("execution_id"))
    feature_id = _as_text(request.get("feature_id"))
    if execution_id is None or feature_id is None:
        raise AdapterError(
            f"packet {packet_id!r} request lacks execution_id/feature_id")

    # `receive` requires the packet to be dispatched (I8); the interface
    # registers its own attempt after this adapter returns, so the worker's
    # attempt is recorded here first (same ledger, reused machinery). PD-6:
    # `session`/`model_reported` come from the durable row, with provenance.
    # 006-001 §2.6: the row is present (the row we just classified from).
    observation = _observation(
        runtime, model, binary_version, session, started_at,
        mode_requested=mode_requested, mode_effective=mode_effective,
        client_version=client_version, server_version=server_version,
        session_base=(
            "durable session row (exec-config: sessions_db): session_v2.id"),
        row_state="present", model_reported=model_reported)
    _register_dispatch(project_root, packet_id, request, attempt_id, observation)

    inbox = project_root / ".cdad" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    part_name = f"{attempt_id}-{FINAL_TEXT_PART}"
    staged = inbox / f"{part_name}.md"
    staged.write_bytes(final_text.encode("utf-8"))

    descriptor = {
        "schema_version": 1,
        "execution_id": execution_id,
        "packet_id": packet_id,
        "feature_id": feature_id,
        "source": {"kind": "staged-file", "sdk_message_ref": None},
        "parts": [{
            "name": part_name,
            "artifact_kind": FINAL_TEXT_ARTIFACT_KIND,
            "staged_path": f"{cdad_result.INBOX_RELPATH.as_posix()}/{part_name}.md",
        }],
        "run_evidence_ref": None,
    }
    descriptor_path = (project_root / ".cdad" / "runtime"
                       / f".{attempt_id}.result.json")
    descriptor_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor_path.write_text(
        json.dumps(descriptor, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8")

    try:
        _run_receive(project_root, execution_id, packet_id, descriptor_path)
    finally:
        staged.unlink(missing_ok=True)
        descriptor_path.unlink(missing_ok=True)

    return str(project_root / cdad_result.RESULTS_RELPATH / execution_id
               / packet_id / RECEIPT_NAME)


# --------------------------------------------------------------- envelope


def _envelope(*, session: str | None, termination: str, delivery_ref: str | None,
              diagnosis: str | None) -> dict[str, Any]:
    return {
        "attempt": None,
        "session": _as_text(session),
        "termination": termination,
        "delivery_ref": _as_text(delivery_ref),
        "diagnosis": _as_text(diagnosis),
    }


def _classify(row: dict[str, Any],
              final_text: str | None) -> tuple[str, str | None, str | None, str | None]:
    """Classify the correlated durable row into the termination vocabulary.

    PD-5: the termination comes from the MATERIAL fact of the row's
    `idle_outcome` (never the client rc). Only `completed` carries a final text
    (delivery); every other termination never fabricates a receipt.
    """
    idle_outcome = row.get("idle_outcome")
    session = _as_text(row.get("id"))
    if idle_outcome == IDLE_OUTCOME_SUCCEEDED:
        if not _as_text(final_text):
            return "blocked", session, None, (
                "the correlated durable session row reports idle_outcome "
                "'succeeded' but the store carries no final assistant text "
                "(session_message.data.content[].text): cannot declare a "
                "sufficient delivery (reconcile before repeating)")
        return "completed", session, final_text, None
    if idle_outcome == IDLE_OUTCOME_FAILED:
        return "blocked", session, None, (
            "the correlated durable session row reports idle_outcome 'failed': "
            "the role session is blocked; obtain a re-entry with changed "
            "conditions before repeating the delegation")
    if idle_outcome == IDLE_OUTCOME_INTERRUPTED:
        return "cancelled", session, None, (
            "the correlated durable session row reports idle_outcome "
            "'interrupted': no delivery is declared and no receipt is "
            "fabricated (reconcile before repeating)")
    return "unknown", session, None, (
        f"the correlated durable session row reports an unknown idle_outcome "
        f"{idle_outcome!r}: no delivery is declared and no receipt is fabricated")


# ------------------------------------------------------------------- main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cdad_delegate_opencode.py",
        description="CDAD OpenCode destination adapter.")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--destination", default=DESTINATION_ID)
    parser.add_argument("--exec-config", default=None)
    return parser


def _read_packet_stdin() -> bytes:
    try:
        data = sys.stdin.buffer.read()
    except (OSError, ValueError) as exc:
        raise AdapterError(f"cannot read the transported packet from stdin: {exc}") from exc
    if not data:
        raise AdapterError("no packet was transported on stdin")
    return data


def delegate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project_root)
    if not project_root.is_dir():
        raise AdapterError(f"--project-root is not a directory: {args.project_root}")
    project_root = project_root.resolve()
    if args.destination != DESTINATION_ID:
        raise AdapterError(
            f"OpenCode adapter cannot serve destination {args.destination!r}")

    config = (_load_json(Path(args.exec_config), "execution config")
              if args.exec_config else {})
    runtime = _as_text(config.get("runtime"))
    model = _as_text(config.get("model"))
    binary_version = _as_text(config.get("binary_version"))
    sessions_db_raw = _as_text(config.get("sessions_db"))
    # PD-4/PD-1 (006-001): server/permission mode at the right level
    # (execution config); the profile decides. `server` (alternative to
    # `--standalone`) and `auto` (non-interactive permissions, enabled by
    # default) are never hardcoded.
    server_raw = _as_text(config.get("server"))
    auto = config.get("auto", True) is not False
    wait = config.get("wait")
    wait_dict = wait if isinstance(wait, dict) else {}
    timeout = (float(wait_dict["timeout_seconds"])
               if isinstance(wait_dict.get("timeout_seconds"), (int, float))
               and wait_dict["timeout_seconds"] > 0 else None)

    # 006-001 §2.1: a malformed `wait.*`/`mode` value blocks BEFORE the
    # packet request is even loaded -- nothing is invoked, nothing is
    # registered (there is no execution_id to register against yet).
    wait_keys_diagnosis = _validate_wait_keys(wait_dict)
    if wait_keys_diagnosis is not None:
        return _envelope(session=None, termination="blocked",
                         delivery_ref=None, diagnosis=wait_keys_diagnosis)
    mode_requested, mode_value_diagnosis = _validate_mode_value(config.get("mode"))
    if mode_value_diagnosis is not None:
        return _envelope(session=None, termination="blocked",
                         delivery_ref=None, diagnosis=mode_value_diagnosis)

    packet_dir = project_root / ".cdad" / "packets" / args.packet_id
    request = _load_json(packet_dir / "REQUEST.json", "packet request")
    role = _as_text(request.get("role"))
    if role is None:
        raise AdapterError(f"packet {args.packet_id!r} request has no role")

    packet_bytes = _read_packet_stdin()
    started_at = _now()
    attempt_id = f"opencode-{uuid.uuid4().hex[:12]}"
    mode_effective = _resolve_mode_effective(mode_requested, server_raw)

    def register_note(*, session: str | None, session_base: str,
                      row_state: str, client_version: str | None,
                      server_version: str | None) -> str | None:
        """006-001 §2.6 (PD-3): register the WORKER's own attempt in the
        SAME I8 ledger in EVERY termination posterior to loading
        REQUEST.json. A registration failure never changes the
        termination (D-5): it only adds a bounded note to the diagnosis."""
        observation = _observation(
            runtime, model, binary_version, session, started_at,
            mode_requested=mode_requested, mode_effective=mode_effective,
            client_version=client_version, server_version=server_version,
            session_base=session_base, row_state=row_state)
        try:
            _register_dispatch(project_root, args.packet_id, request,
                               attempt_id, observation)
        except AdapterError as exc:
            return f"worker record not written: {str(exc)[:200]}"
        return None

    def pre_dispatch_termination(termination: str, diagnosis: str | None, *,
                                 client_version: str | None,
                                 server_version: str | None) -> dict[str, Any]:
        """A termination before any session was chosen (PD-1/PD-2/PD-3 of
        005-009's own pre-dispatch checks): `session_base` is `not
        dispatched`, the row is (truthfully) `absent` -- no session was ever
        created, so no row could ever exist."""
        note = register_note(session=None, session_base="not dispatched",
                             row_state="absent", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination=termination,
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    def blocked_before_dispatch(diagnosis: str, *,
                                client_version: str | None = "unknown",
                                server_version: str | None = "unknown"
                                ) -> dict[str, Any]:
        return pre_dispatch_termination(
            "blocked", diagnosis, client_version=client_version,
            server_version=server_version)

    # PD-3: verify the derived agent is published BEFORE dispatching anything.
    # A missing derived agent fails closed here; the CLI `mode:` no longer
    # conditions the dispatch (the durable identity is the barrier instead).
    unpublished_diagnosis = _check_derived_agent_published(project_root, role)
    if unpublished_diagnosis is not None:
        return blocked_before_dispatch(unpublished_diagnosis)

    binary = _as_text(config.get("binary"))
    if binary is None:
        return blocked_before_dispatch(
            "execution configuration has no destination binary; cannot "
            "dispatch a session (no fallback to a generic non-Cdad agent)")
    if sessions_db_raw is None:
        return blocked_before_dispatch(
            "execution configuration has no durable signal surface "
            "(sessions_db); cannot wait on a material signal")
    sessions_db = Path(sessions_db_raw)

    # R4/INV-4: the wait on the durable signal MUST be bounded. A config that
    # does not declare a positive `wait.timeout_seconds` (missing object,
    # missing key, or a non-positive value) FAILS CLOSED before dispatching:
    # no invocation, no transport, no session, no receipt. Without a positive
    # bound the wait would be unbounded (fail-open) and the invocation could
    # never be killed at a declared bound.
    if timeout is None:
        return blocked_before_dispatch(
            "the execution configuration does not declare a positive "
            "`wait.timeout_seconds`; the wait on the durable signal must "
            "be bounded (INV-4). Refusing to dispatch without a positive "
            "bound declared in the `wait.timeout_seconds` key: no session "
            "is created, no bytes are transported and no receipt is "
            "fabricated (reconcile the execution configuration before "
            "repeating)")

    # 006-001 §2.2: `mode: server` (declared or by compatibility) without a
    # valid URL selects NO execution mode -- blocked before any invocation,
    # never a silent fallback (INV-2).
    if mode_effective == "none":
        return blocked_before_dispatch(
            "`mode: server` was requested without a valid `server` URL "
            "(http/https, with host, no userinfo -- spec §2.2): refusing to "
            "select an execution mode (no fallback to standalone, INV-2)")

    budget = _wait_budget(timeout)
    wait_deadline = time.monotonic() + (budget or 0.0)

    # 006-001 §2.3 (PD-2): the preflight only runs in the SERVER effective
    # mode (D-2); `--version` is the client's OWN observed fact, used for
    # the I8 provenance regardless of whether it gates the comparison.
    server_for_invoke: str | None = None
    if mode_effective == "server":
        preflight_timeout_configured = float(
            wait_dict.get("preflight_timeout_seconds",
                         DEFAULT_WAIT_VALUES["preflight_timeout_seconds"]))
        remaining = max(0.0, wait_deadline - time.monotonic())
        # §2.3: bounded by the REMAINING budget, never by the configured
        # value alone (an exhausted budget must not fall back to the
        # largest timeout).
        preflight_timeout = min(preflight_timeout_configured, remaining)
        preflight = _preflight_server(binary, server_raw, preflight_timeout,
                                      binary_version)
        client_version = preflight["client_version"]
        server_version = preflight["server_version"]
        if not preflight["ok"]:
            return pre_dispatch_termination(
                preflight["termination"], preflight["diagnosis"],
                client_version=client_version, server_version=server_version)
        server_for_invoke = server_raw
    else:
        # D-2 (standalone): never invokes `--version` (would break the
        # call-count oracles); registers the configured `binary_version` (or
        # `unknown`) and the literal `same-binary(standalone)`.
        client_version = binary_version
        server_version = "same-binary(standalone)"

    # PD-1: the adapter CHOOSES the session id and correlates by it.
    session_id = _choose_session_id()
    remaining_for_invoke = max(0.0, wait_deadline - time.monotonic())

    # PD-5/D6: invoke the configured binary (with `--session <id>`), then wait
    # on the DURABLE signal. The invocation is bounded by the remaining
    # budget, so a destination that never returns can never make the
    # interface the one that kills this adapter (the adapter always answers
    # within the bound it received).
    try:
        proc = _invoke_destination(binary, _entry_agent_name(role), model,
                                   packet_bytes, project_root,
                                   remaining_for_invoke, session_id,
                                   server=server_for_invoke, auto=auto)
    except DestinationTimeoutError as exc:
        # R1: the material fact is absence-of-signal within the bound ->
        # `timeout`, never `transport-error` with a fabricated rc.
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="unknown", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination="timeout",
                         delivery_ref=None,
                         diagnosis=_append_note(str(exc), note))
    except AdapterError as exc:
        # R1 (contracara): a binary that could not be STARTED is a real
        # transport failure (PD-5).
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="absent", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination="transport-error",
                         delivery_ref=None,
                         diagnosis=_append_note(str(exc), note))

    # PD-2: a missing/unreadable/unknown-schema store is a KNOWN fact and fails
    # closed with a diagnosis, without exhausting the wait. PD-5: otherwise the
    # termination comes from the correlated durable row's `idle_outcome`; a
    # client that already ended with a non-zero rc and left no row is a
    # material transport failure; no idle within the bounded wait is `timeout`.
    try:
        outcome = _await_durable_outcome(sessions_db, session_id,
                                         proc.returncode, wait_deadline)
    except AdapterError as exc:
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="unknown", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination="blocked",
                         delivery_ref=None,
                         diagnosis=_append_note(str(exc), note))

    kind = outcome["kind"]
    if kind == "transport-error":
        stderr = _redact_server_url(
            proc.stderr.decode("utf-8", errors="replace").strip(),
            server_for_invoke)
        diagnosis = (
            f"the destination client failed in transport (rc="
            f"{proc.returncode}) before any durable session row: "
            f"{stderr[:300] or 'no diagnostic'}")
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="absent", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination="transport-error",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))
    if kind == "timeout":
        diagnosis = (
            "no durable session row with an idle outcome for the chosen "
            f"session {session_id!r} within the bounded wait "
            f"({timeout if timeout is not None else 'configured'} seconds); "
            "the client rc does not prove the role finished and no receipt "
            "is fabricated (reconcile before repeating)")
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="unknown", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=None, termination="timeout",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    row = outcome["row"]
    durable_session_base = (
        "durable session row (exec-config: sessions_db): session_v2.id")
    # PD-3/INV-6: the role identity is the barrier. If the durable row declares
    # another agent, fail closed with a diagnosis naming BOTH agents -- never a
    # delivery and never a fallback to a generic non-Cdad agent.
    identity_diagnosis = _check_durable_identity(row, role)
    if identity_diagnosis is not None:
        note = register_note(session=_as_text(row.get("id")),
                             session_base=durable_session_base,
                             row_state="present", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=_as_text(row.get("id")), termination="blocked",
                         delivery_ref=None,
                         diagnosis=_append_note(identity_diagnosis, note))

    termination, session, final_text, diagnosis = _classify(
        row, outcome["final_text"])
    if termination != "completed":
        note = register_note(session=session, session_base=durable_session_base,
                             row_state="present", client_version=client_version,
                             server_version=server_version)
        return _envelope(session=session, termination=termination,
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    try:
        delivery_ref = _persist_delivery(
            project_root, args.packet_id, request, attempt_id, session, runtime,
            model, binary_version, started_at, final_text,
            mode_requested=mode_requested, mode_effective=mode_effective,
            client_version=client_version, server_version=server_version,
            model_reported=_model_reported_from_row(row.get("model")))
    except (AdapterError, cdad_result.ResultError) as exc:
        return _envelope(
            session=session, termination="blocked", delivery_ref=None,
            diagnosis=(
                f"the role completed but the durable delivery could not be "
                f"persisted through receive: {exc}"))
    return _envelope(session=session, termination="completed",
                     delivery_ref=delivery_ref, diagnosis=None)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        output = delegate(args)
    except AdapterError as exc:
        output = _envelope(session=None, termination="blocked",
                           delivery_ref=None, diagnosis=str(exc))
    sys.stdout.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
