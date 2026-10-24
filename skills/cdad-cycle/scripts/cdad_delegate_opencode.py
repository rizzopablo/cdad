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
   (`binary`, `binary_version`, `wait.timeout_seconds`): nothing about the CLI,
   the binary or the times is hardcoded here (PD-8/INV-7). The delegated MODEL
   comes only from the delegation config (`delegation.json`, 006-003 D3); a
   `model` left in the execution configuration is ignored. `runtime`/`model`
   also feed the I8 observation.
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
5. 006-001 T1b (PD-13/PD-14): the `mode: service` selection checks the
   background service with the read-only `service status` (the ONLY invocation
   of `service`, never management: never `serve`, `service
   start|stop|restart|get|set|unset` or `reload`), dispatches WITHOUT
   `--server`/`--standalone` when the service runs with a compatible version
   (the version is projected from the single `version` key of the service
   registry, D-11: never the document, never its password, never the URL and
   with no network), declares and counts the `service` -> `standalone` fallback
   when the service does not run (`service.require: false`), and blocks -- never
   a standalone next to a running service (INV-10) -- when the status is
   unexpected, the strict variant requires the service, or the version differs
   or is unverifiable.
6. 006-003 U6 (PD-5a..e/INV-1): in `server` mode the credential comes from the
   ENVIRONMENT first (`OPENCODE_PASSWORD`, then `OPENCODE_SERVER_PASSWORD`) and,
   only when neither is present, from the credential file of the delegation
   config (`credential_env_file`, default `<config-dir>/cdad/opencode-server.env`,
   §2.2 location): `KEY=value` with `#` comments, an empty value meaning
   absent, permissions verified on the OPEN fd (any bit of `077` is refused).
   The 401/403 diagnosis is self-sufficient (both variables, the resolved
   path, the provenance of the value -- the password of the `opencode serve`
   in use, in the environment of the dispatching process -- and, when
   refused, the path and the mode found). The value never leaves the Basic
   header: never stdout/stderr/argv/ledger.
7. 006-005 U2 (PD-11/PD-14/PD-5/PD-10/PD-12/PD-13/PD-23): the module also (a)
   INJECTS the resolved server credential into the CLIENT PROCESS ENVIRONMENT
   (`OPENCODE_PASSWORD`) in `mode: server` only, next to the pinned `PWD`, and
   never into argv, stdout/stderr, the I8 record nor the receipt; (b) takes the
   AGENT from `REQUEST.json.agent` (role + `stack`, PD-7), falling back to the
   role agent `cdad-<role>` while DECLARING the absent field, and verifies THAT
   agent is published before dispatching; (c) corroborates the durable row's
   `agent` against the agent of the packet (`unknown` when either side is not
   evaluable, a REJECTION naming the key when they contradict); (d) DERIVES the
   delivered part's `artifact_kind` from role/subphase (§2.8/PD-23), never a
   fixed constant; and (e) declares `--capabilities` (the five §2.2 keys, the
   observed store columns and whether the §2.3 discrimination threshold is
   reached) and `--observe` (ONE bounded read-only access returning the
   correlated row plus the `store_reads` counter, failing closed naming the
   absent column) for the native path.
8. 006-005 U6-5 (D-U65-1/D-U65-2): the I8 attempt record is written
   WRITE-AHEAD -- a PROVISIONAL record (the declared `write-ahead:` mark in
   `provenance.session`, `model_reported: null`, the chosen session) is
   persisted AFTER the preflight, the prior-attempt check and the session
   choice and BEFORE the client is launched, so a coordinator that dies with
   the client alive still leaves the attempt visible to `reconcile`,
   `disposition` and the prior-attempt check. A failure to write it is
   fail-closed (the client is never launched; the termination is `blocked`),
   and EVERY later termination completes the SAME record exactly once with the
   observation that termination writes today (session per PD-8,
   `model_reported` from the store, and all PD-3 pairs). Terminations BEFORE
   the write-ahead register as before.

Honest limits: a separate process/session is not a sandbox (INV-8); the durable
signal surface implemented here is the session store the execution
configuration points at, read only; no scheduler, CLI installation or sandbox is
built (INV-9).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# The canonical CLIs live next to this adapter; importing them (never
# re-running) reuses the reception flow and the packet validators.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import cdad_delegate  # noqa: E402
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
FINAL_TEXT_PART = "final-text"
# 006-005 §2.8/PD-23: the kind of the delivered part is DERIVED from the
# packet's role and subphase (`_derived_artifact_kind`); this literal is the
# common single role report the derivation returns where the closed table
# admits it (never written as a fixed constant for every delivery).
ROLE_REPORT_KIND = "role-report"
RECEIPT_NAME = "receipt.json"

# 006-001 T1 (PD-1/PD-2): execution-mode selection and the server preflight.
OPENCODE_PASSWORD_ENV = "OPENCODE_PASSWORD"
OPENCODE_SERVER_PASSWORD_ENV = "OPENCODE_SERVER_PASSWORD"
VALID_MODE_VALUES = ("server", "service", "standalone")
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

# 006-001 T1b (PD-13/PD-14, §2.3b): the background-service preflight. The ONLY
# invocation of `service` CDAD ever makes is the read-only `service status`
# (INV-2: never `serve`, `service start|stop|restart|get|set|unset` or
# `reload`). Its output is a single line -- the service URL or `stopped` -- and
# is discarded to a discriminant: the URL never leaves the interpreter.
SERVICE_STATUS_ARGV = ("service", "status")
SERVICE_STATUS_STOPPED_LITERAL = "stopped"
# The service registry (D-11) is an OBSERVED fact, not a public contract (debt
# DT-6); it lives under the state directory. The fixture writes both candidates
# so the gate is asserted by BEHAVIOUR, not by the internal path the adapter
# picks.
SERVICE_REGISTRY_RELPATHS = (("opencode", "service.json"), ("service.json",))
# Provenance literals (spec §2.6).
DISPATCH_FLAG_SERVER = "--server"
DISPATCH_FLAG_STANDALONE = "--standalone"
DISPATCH_FLAG_NONE = "none"
SERVICE_STATUS_RUNNING = "running"
SERVICE_STATUS_STOPPED = "stopped"
SERVICE_STATUS_UNEXPECTED = "unexpected"
SERVICE_STATUS_NOT_CHECKED = "not-checked"
FALLBACK_NONE = "none"
FALLBACK_SERVICE_UNAVAILABLE = "service-unavailable"
# 006-005 U6-5 (D-U65-1/D-U65-2): the DECLARED mark of the PROVISIONAL I8
# record this adapter writes BEFORE launching the runtime client.
# `provenance.session` of that record starts with it; every termination after it
# completes the SAME record ONCE (an unmarked observation with the fixed
# identity, admitted by the ledger), and the final record is the one today's
# termination writes. A failure to write it is fail-closed: the client is never
# launched.
WRITE_AHEAD_MARK = "write-ahead:"

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

# 006-005 §2.2/§2.3 (PD-10/PD-12/PD-13): the declared capability keys, the
# column the observation surface requires (the identity key this path
# evaluates) and the DISCRIMINATING keys of the §2.3 native association (at
# least one of them must be observable for the positive accreditation, O-3).
CAPABILITY_KEYS = ("native_observation", "external_transport",
                   "session_correlation", "version", "reason")
VERSION_UNKNOWN = "unknown"
SESSION_CORRELATION_AGENT_COLUMN = "agent"
SESSION_OBSERVATION_KEY_COLUMNS = ("id", SESSION_CORRELATION_AGENT_COLUMN)
SESSION_CORRELATION_DISCRIMINATING_COLUMNS = ("parent_id", "directory",
                                              "time_created")
STORE_READS_KEY = "store_reads"

# 006-005 U6-4 (V-7 extended, execution.md): the installed version's
# `session_v2.time_created` is an INTEGER in epoch MILLISECONDS. The unit is a
# fact of the runtime's store, so THIS module (which knows its store) converts it
# into an ISO instant before handing the row to the entry: the entry never
# guesses units. A value that cannot be read as an instant is NAMED as not
# interpretable, never silently degraded into the ancestor-directory wording.
STORE_MOMENT_COLUMN = "time_created"
STORE_MOMENT_EPOCH_MILLISECONDS = 1000

# 006-005 U6-6 (D-ADP-2): the store's `model` is TEXT carrying either a JSON
# document (the installed version's shape) or plain text. The useful form of the
# I8 observation is the one the EXTERNAL path already declares
# (`_model_reported_from_row`): the module renders it in the observation it hands
# to the entry, so the native path reports the SAME `model_reported` and never
# the raw document.
STORE_MODEL_COLUMN = "model"

# 006-001 T2 (PD-7..PD-11, §2.4/§2.5/§2.7): the wait after the client exits,
# the classification of the durable row, the ordered termination of the
# adapter's OWN process group and the prior attempt check.
IDLE_MESSAGE_TYPE = "idle"            # the durable `idle` message (PD-7)
IDLE_ERROR_MESSAGE_LIMIT = 200        # PD-7: error.message bounded to 200 chars
DISPATCHES_RELPATH = Path(".cdad") / "executions"
# §2.5 (D-3): the effective grace is bounded by the reserve-relative fraction.
TERMINATE_GRACE_FRACTION = 0.25
# §2.5 (D-3) latency guarantee (PD-11): the share of the internal budget that
# the CLIENT's dispatch always keeps for itself. The preflight legitimately
# consumes part of the budget (two invocations in the service mode); without a
# floor a slow preflight would leave the client a near-zero bound and a
# HEALTHY client would be killed and reported as a FALSE `timeout` (PD-7/PD-8).
# The floor comes out of the adapter's own reserve and is CAPPED by it (see
# `COMPLETION_MARGIN_SECONDS` below): PD-11 wins over the floor.
CLIENT_MIN_BUDGET_SHARE = 0.75
# 006-001 §2.5 (D-3, PD-11; review B1): the completion margin the client's
# floor must always leave inside the interface's own bound. The adapter answers
# with ITS OWN envelope (with the chosen session), so the invariant is
#   consumed + client bound + grace + COMPLETION_MARGIN <= timeout_seconds
# SIEMPRE. The margin covers the adapter's own pre-invoke offset (module import
# -> the bound), the ordered kill of the client's group and the emission of the
# envelope under host load, all of which come out of the same 1.0s
# `WAIT_RESERVE_SECONDS`. The floor may only spend the reserve slack the
# effective grace and this margin leave free
# (`WAIT_RESERVE_SECONDS - grace - margin`, clamped at zero): a large grace
# consumes the whole reserve and the floor adds nothing, while a small grace
# still defends a HEALTHY client from a slow preflight.
COMPLETION_MARGIN_SECONDS = 0.8


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


def _packet_agent(request: dict[str, Any], role: str) -> tuple[str, str | None]:
    """The agent of the PACKET (PD-14/§2.7) and the note declaring its absence.

    Returns `(agent, absence_note)`. The agent comes from `REQUEST.json.agent`
    (role + `stack`, written by `prepare`, PD-7); a packet published before the
    feature (no `agent` field) is still dispatchable with the role agent
    `cdad-<role>`, and the absence of the declared field is NEVER silenced (the
    caller states it in its envelope's diagnosis).
    """
    declared = _as_text(request.get("agent"))
    if declared is not None:
        return declared, None
    agent = _entry_agent_name(role)
    return agent, (
        f"the packet request declares no `agent` field (a packet published "
        f"before this feature): the role agent {agent!r} is the declared "
        f"fallback and the `agent` key of the correlation stays `unknown`, "
        f"never an inferred value (§2.7/PD-14)")


def _check_derived_agent_published(project_root: Path, agent: str) -> str | None:
    """Verify the derived agent of the packet is published (PD-3/PD-14).

    Returns `None` when the derived agent is published, or an actionable
    diagnosis that names the missing agent (fail closed BEFORE dispatching).

    PD-3: the derived entry's `mode:` NO LONGER conditions the dispatch (the
    installed runtime accepts `mode: subagent` as a non-interactive CLI entry);
    the barrier is the durable identity
    (`session_v2.agent == <agent of the packet>`), verified once the session is
    correlated. A missing derived agent is still a pre-dispatch fail-closed
    fact and NEVER falls back to a generic non-Cdad agent.
    """
    entry = project_root / DERIVED_AGENTS_RELPATH / f"{agent}.md"
    if entry.is_file():
        return None
    return (
        f"the derived agent {agent!r} is not published: expected {agent}.md "
        f"under {DERIVED_AGENTS_RELPATH.as_posix()}/ (published by prepare, "
        f"I9). Refusing to dispatch a non-interactive session and refusing "
        f"any fallback to a generic non-Cdad agent; publish the derived agent "
        f"before delegating.")


def _durable_identity_verdict(row: dict[str, Any],
                              packet_agent: str | None
                              ) -> tuple[str, str | None]:
    """Corroborate the durable row's `agent` against the packet's agent (§2.5).

    Returns `(verdict, diagnosis)`: `match` (the delivered role identity is the
    one the packet declared), `contradiction` (the row declares another agent:
    a REJECTION that names the `agent` key, never `unknown` and never an
    accepted delivery) or `unknown` (either side is not evaluable — a packet
    without the field, or a row without the column: the key is `unknown`,
    never compared against a supposed value).
    """
    declared = _as_text(row.get("agent"))
    if packet_agent is None or declared is None:
        return "unknown", (
            "the `agent` key of the correlation is not evaluable "
            f"(session_v2.agent={declared!r}, the agent of the packet="
            f"{packet_agent!r}): §2.5 resolves an unevaluable key as `unknown`, "
            "never by comparing against a supposed value, and no delivery is "
            "accepted on it (reconcile the session/agent before repeating)")
    if declared == packet_agent:
        return "match", None
    return "contradiction", (
        f"the correlated durable session row declares agent {declared!r}, not "
        f"the agent of the packet {packet_agent!r} (PD-3/§2.5: the role "
        f"identity is verified from the durable row, session_v2.agent). "
        f"Refusing to declare a delivery and refusing any fallback to a "
        f"generic non-Cdad agent; reconcile the session/agent before repeating "
        f"the delegation.")


def _derived_artifact_kind(role: str, substage: str) -> str:
    """§2.8/PD-23/INV-14: the kind of the delivered part comes from the closed
    role/subphase table (`cdad_result._allowed_kinds`, the single source the
    native path also derives from), never from a fixed constant.

    §2.8.1: a row that admits EXACTLY one kind determines the delivered part.
    §2.8.2: where the row admits `role-report` (the architect's report in
    `discovery`/`draft`, since 005-007 T4) the common single delivery of the
    interface is that role report. §2.8.3: the scribe's common single delivery
    is the same role report; its row admits `role-report` from U7/PD-26 and
    that row is NOT touched here (the materialization of the scribe's report is
    U7's oracle).
    """
    kinds = cdad_result._allowed_kinds(role, substage)
    if len(kinds) == 1:
        return next(iter(kinds))
    if ROLE_REPORT_KIND in kinds:
        return ROLE_REPORT_KIND
    # §2.8.3: the scribe's common single delivery is the same role report; its
    # row admits `role-report` from U7/PD-26 (declared dependency, the row is
    # NOT touched here and the materialization of that report is U7's oracle).
    if role == "scribe":
        return ROLE_REPORT_KIND
    raise AdapterError(
        f"the closed role/subphase table does not determine a single artifact "
        f"kind for role {role!r}/substage {substage!r}: "
        f"{sorted(kinds) or 'no kind admitted'} — the delivered part must "
        f"declare one kind (§2.8/PD-23)")


# ------------------------------------------------------- destination process


def _terminate_own_group(proc: subprocess.Popen, grace: float) -> None:
    """Ordered termination of the adapter's OWN process group (PD-8, §2.5).

    SIGTERM the group, wait the effective grace `g`, then SIGKILL the group:
    the direct client AND every process it spawned die before the adapter
    answers (a grandchild that ignores SIGTERM does not survive). The client
    runs in a session of its own (`start_new_session=True`), so the group
    killed here is ONLY the adapter's own -- the background service and any
    server are never touched (INV-2/PD-8).
    """
    try:
        pgid = os.getpgid(proc.pid)
    except OSError:
        pgid = proc.pid
    try:
        os.killpg(pgid, signal.SIGTERM)
    except OSError:
        pass
    deadline = time.monotonic() + max(0.0, grace)
    while time.monotonic() < deadline and proc.poll() is None:
        time.sleep(0.02)
    try:
        os.killpg(pgid, signal.SIGKILL)
    except OSError:
        pass
    try:
        proc.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        pass


def _invoke_destination(binary: str, agent: str, model: str | None,
                        packet_bytes: bytes, cwd: Path,
                        timeout: float | None,
                        session_id: str, *,
                        server: str | None,
                        auto: bool,
                        standalone: bool = True,
                        grace: float = 0.0,
                        credential_env: str | None = None) -> subprocess.CompletedProcess:
    """Invoke the configured binary, transporting the packet bytes on stdin.

    The adapter chooses the session id and passes `--session <id>` so the
    durable row is correlatable unambiguously (PD-1).

    PD-4: the server/permission mode comes from the execution configuration at
    the right level, never hardcoded -- `--server <url>` when the configuration
    declares it (alternative to `--standalone`, never both), `--standalone` by
    default (private server; never the owner's background service), and `--auto`
    (non-interactive permissions; auto-approval of non-denied permissions, NOT
    a sandbox -- INV-8) enabled by default.

    006-001 §2.3b point 4 (PD-13): in the SERVICE effective mode the dispatch
    carries NO flags (`server=None`, `standalone=False`): the client uses the
    background service as the runtime designs it. `--server`/`--standalone` are
    mutually exclusive and the service dispatch is neither.

    006-001 T2 (PD-8): the client runs in its OWN process group
    (`start_new_session=True`) so that, when it does not return within the
    bound, the adapter terminates the whole group in an ORDERED way (SIGTERM,
    the effective grace, SIGKILL) -- never just the direct child.

    006-005 U2 (PD-11/§2.5): `credential_env` is the credential the SERVER mode
    resolved (environment first, then the 0600 file) and is injected ONLY into
    the environment of THIS client process, next to the pinned `PWD`; it never
    reaches argv, stdout, stderr, the I8 record nor the receipt. `None`
    (standalone/service) injects nothing.
    """
    argv = [binary, "run", "--agent", agent, "--session", session_id]
    if server:
        argv += ["--server", server]
    elif standalone:
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
    if credential_env is not None:
        # PD-11: only the client process environment, only in server mode.
        env[OPENCODE_PASSWORD_ENV] = credential_env
    try:
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=str(cwd), env=env,
                                start_new_session=True)
    except OSError as exc:
        # R1 (contracara): the binary could not be STARTED -- a real
        # transport failure observed before any session row (PD-5). No
        # process was started, so the session stays `null` (PD-8).
        raise AdapterError(
            f"destination binary {binary!r} could not be started: {exc}") from exc
    try:
        stdout, stderr = proc.communicate(input=packet_bytes, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # R1: the invocation did NOT return within the bound; the client
        # never reported a return code. The adapter terminates its OWN
        # process group in an ordered way (PD-8) and raises the material
        # fact `timeout`, NOT a transport failure with a fabricated rc
        # (PD-5/PD-1).
        _terminate_own_group(proc, grace)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
        raise DestinationTimeoutError(
            f"destination binary {binary!r} did not return within the bounded "
            f"wait ({timeout} seconds); the client was terminated in an "
            f"ordered way at the bound (its whole process group) and no "
            f"return code was ever observed, so no rc is claimed; the "
            f"absence of a durable signal within the bound is a timeout (no "
            f"receipt is fabricated; reconcile before repeating)") from exc
    return subprocess.CompletedProcess(argv, proc.returncode, stdout, stderr)


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


def _store_instant(value: Any) -> datetime | None:
    """The store's `time_created` as an instant, or `None` when unreadable.

    U6-4: the unit (epoch MILLISECONDS) is a fact of the runtime's store, known
    here and nowhere else in the product. The entry receives the ISO instant;
    it never guesses seconds vs milliseconds. A value that is not a number is
    not an instant, and the caller NAMES it as such (O-6/INV-4).
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(
            value / STORE_MOMENT_EPOCH_MILLISECONDS, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None


def _declared_instant(value: str) -> datetime | None:
    """The declared `--since` instant (ISO), or `None` when uninterpretable."""
    text = _as_text(value)
    if text is None:
        return None
    try:
        instant = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if instant.tzinfo is None:
        return instant.replace(tzinfo=timezone.utc)
    return instant


def _native_candidate(conn: sqlite3.Connection, parent_id: str,
                      agent: str | None, since: str | None
                      ) -> tuple[dict[str, Any] | None, str | None]:
    """U6-4: the candidate row under the declared parent, or the named reason.

    Candidates are the rows under the declared parent whose `agent` is the
    packet's agent and whose moment is AFTER `--since`. Exactly one is handed to
    the entry (with its moment as an ISO instant); none is `(None, reason|None)`;
    more than one is NOT accredited and the ambiguity is NAMED (never a
    rejection, INV-2). ONE bounded read: a single `SELECT` filtered by parent.
    """
    cursor = _query(
        conn, f"SELECT * FROM {SESSION_V2_TABLE} WHERE parent_id = ?",
        (parent_id,))
    columns = [description[0] for description in cursor.description]
    rows = [dict(zip(columns, values)) for values in cursor.fetchall()]
    if not rows:
        return None, None
    declared = None
    if since is not None:
        declared = _declared_instant(since)
        if declared is None:
            raise AdapterError(
                f"the declared instant (`--since`) {since!r} is not "
                "interpretable as an ISO instant: the native selection cannot "
                "order the rows under the declared parent by moment")
    candidates: list[tuple[dict[str, Any], datetime | None]] = []
    uninterpretable = 0
    agent_matched = 0
    for row in rows:
        declared_agent = _as_text(row.get(SESSION_CORRELATION_AGENT_COLUMN))
        if agent is not None and declared_agent != agent:
            continue
        agent_matched += 1
        if STORE_MOMENT_COLUMN not in row:
            candidates.append((row, None))
            continue
        moment = _store_instant(row.get(STORE_MOMENT_COLUMN))
        if moment is None:
            uninterpretable += 1
            continue
        if declared is not None and not moment > declared:
            continue
        candidates.append((row, moment))
    if len(candidates) > 1:
        return None, (
            f"ambiguous: the durable store exposes {len(candidates)} candidate "
            f"rows under the declared parent {parent_id!r} for the packet's "
            f"agent {agent!r} after the declared instant: more than one "
            "candidate is not unique, so no session is accredited (INV-2)")
    if len(candidates) == 1:
        # B-2 (006-005 review-fix): the row is handed RAW; the instant is
        # normalized at the single boundary of the observation
        # (`_normalized_observation`), like the row selected by `--session`.
        return dict(candidates[0][0]), None
    if uninterpretable:
        return None, (
            f"the store's {STORE_MOMENT_COLUMN} value of {uninterpretable} "
            f"row(s) under the declared parent {parent_id!r} is not "
            "interpretable as an instant: the moment key cannot be evaluated "
            "and no session is accredited")
    if agent_matched:
        return None, (
            f"the row(s) under the declared parent {parent_id!r} match "
            f"`parent`"
            + (f" and `agent` {agent!r}" if agent is not None else "")
            + (", but no moment is after the declared instant"
               if declared is not None else "")
            + ": no session is accredited")
    return None, (
        f"the row(s) under the declared parent {parent_id!r} match `parent`, "
        f"but none declares the packet's agent {agent!r}: no session is "
        "accredited")


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


def _last_idle_message_error(conn: sqlite3.Connection,
                             session_id: str) -> tuple[str | None, str | None]:
    """The `error.type`/`error.message` of the LAST `idle` session_message.

    PD-7: a durable row whose `idle_outcome` is `failed` carries the failing
    fact in its LAST `idle` message (`data.error`). Returns
    `(error_type, error_message)`; `(None, None)` when there is no `idle`
    message or it carries no usable `error` object. The message is returned
    whole here and bounded to `IDLE_ERROR_MESSAGE_LIMIT` characters by the
    caller, so a very long durable error never floods the diagnosis.
    """
    cursor = _query(
        conn,
        f"SELECT data FROM {SESSION_MESSAGE_TABLE} "
        "WHERE session_id = ? AND type = ? ORDER BY seq DESC LIMIT 1",
        (session_id, IDLE_MESSAGE_TYPE))
    row = cursor.fetchone()
    if row is None:
        return None, None
    try:
        document = json.loads(row[0]) if isinstance(row[0], str) else row[0]
    except (TypeError, ValueError):
        return None, None
    if not isinstance(document, dict):
        return None, None
    error = document.get("error")
    if not isinstance(error, dict):
        return None, None
    error_type = error.get("type")
    error_message = error.get("message")
    return (error_type if isinstance(error_type, str) else None,
            error_message if isinstance(error_message, str) else None)


def _store_state(store_path: Path, session_id: str) -> dict[str, Any]:
    """Read the correlated session state from the store READ ONLY (PD-1/PD-2).

    Returns `{"kind": "idle"|"no-idle"|"no-row", "row": ..., "final_text": ...,
    "idle_error": ...}`.
    Raises `AdapterError` (fail closed, no waiting) when the store does not
    exist, is not readable SQLite or lacks the required schema; raises
    `_StoreBusy` on transient lock contention so the waiter can retry.

    The connection sets the SQLite busy timeout to 0: a locked store fails
    IMMEDIATELY as `_StoreBusy` instead of blocking inside SQLite's own
    (5 s) busy handler, so the proportional schedule of §2.4 -- not SQLite --
    decides when the store is retried (PD-10).
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
        conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True, timeout=0)
    except sqlite3.Error as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    try:
        _validate_store_schema(conn, store_path)
        row = _fetch_session_row(conn, session_id)
        if row is None:
            return {"kind": "no-row", "row": None, "final_text": None,
                    "idle_error": None}
        if row.get("idle_outcome") is None:
            return {"kind": "no-idle", "row": row, "final_text": None,
                    "idle_error": None}
        idle_error = None
        if row.get("idle_outcome") == IDLE_OUTCOME_FAILED:
            idle_error = _last_idle_message_error(conn, session_id)
        return {"kind": "idle", "row": row,
                "final_text": _last_assistant_text(conn, session_id),
                "idle_error": idle_error}
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


def _settle_decides(mode_effective: str, state: dict[str, Any] | None,
                    returncode: int) -> bool:
    """Does `settle_seconds`, not the cota, decide this non-idle outcome?

    006-001 §2.4 (PD-7): in STANDALONE a row that is not idle and a client
    that ended with rc=0 without a row resolve to `unknown` once
    `settle_seconds` elapses since the client exited; with the SERVER/SERVICE
    effective mode the durable wait keeps going up to the cota (`timeout`) and
    the settlement never decides. A store that is momentarily busy carries no
    new material fact: the LAST known state keeps deciding.
    """
    if state is None:
        return False
    if state["kind"] == "no-row":
        return returncode == 0
    if state["kind"] == "no-idle":
        return mode_effective == "standalone"
    return False


def _await_durable_outcome(store_path: Path, session_id: str,
                           returncode: int, *, deadline: float,
                           settle_seconds: float, mode_effective: str,
                           exit_ts: float, poll_initial: float,
                           poll_max: float) -> dict[str, Any]:
    """Wait on the DURABLE signal (never the client rc), proportionally.

    006-001 §2.4 (PD-10): zero reads while the client lives -- the durable
    wait only starts after the client exits; from then on the store is read
    with an exponential backoff (`poll_initial_seconds` doubled up to
    `poll_max_seconds`), so the number of reads over a window `W` stays within
    the §2.4 bound. A store/schema failure is a KNOWN fact that fails closed
    immediately (PD-2); a transient `locked`/`busy` store is retried on the
    same schedule (INV-1: only reads, never a write).

    Classification (PD-7): idle row -> its material outcome; no row with a
    non-zero rc -> `transport-error`; `unknown` once `settle_seconds` decides
    (standalone, or a rc=0 exit without a row); `timeout` when the cota is
    reached first. Returns the classification plus `reads`, the number of
    store reads this wait performed (PD-3: reported and contrasted).
    """
    interval = poll_initial
    reads = 0
    settle_deadline = exit_ts + settle_seconds
    settle_applies = False
    row_present = False
    while True:
        reads += 1
        try:
            state = _store_state(store_path, session_id)
        except _StoreBusy:
            state = None
        if state is not None:
            if state["kind"] == "idle":
                return {"kind": "idle", "row": state["row"],
                        "final_text": state["final_text"],
                        "idle_error": state.get("idle_error"), "reads": reads,
                        "row_present": True}
            if state["kind"] == "no-row" and returncode != 0:
                return {"kind": "transport-error", "row": None,
                        "final_text": None, "reads": reads,
                        "row_present": False}
            if _settle_decides(mode_effective, state, returncode):
                settle_applies = True
            row_present = state["kind"] == "no-idle"
        now = time.monotonic()
        if now >= deadline:
            return {"kind": "timeout", "row": None, "final_text": None,
                    "reads": reads, "row_present": row_present}
        if settle_applies:
            remaining_settle = settle_deadline - now
            if remaining_settle <= 0:
                return {"kind": "unknown", "row": None, "final_text": None,
                        "reads": reads, "row_present": row_present}
            sleep_for = min(interval, deadline - now, remaining_settle)
        else:
            sleep_for = min(interval, deadline - now)
        time.sleep(max(0.0, sleep_for))
        interval = min(interval * 2, poll_max)


def _prior_attempt_check(store_path: Path, project_root: Path,
                         execution_id: str | None,
                         packet_id: str) -> dict[str, Any]:
    """006-001 §2.7 (PD-9/D-6): a live prior attempt of the SAME packet blocks.

    Reads the dispatch records of this execution and, for every record of the
    SAME `packet_id` that declares a session, reads that session's durable row
    (read only): a row that EXISTS and is NOT idle is a live prior attempt ->
    `blocking_session`. A row that is idle, or absent, does not block.

    A store that cannot be read does NOT carry the material fact "the row is
    absent": what is not observed is `unknown`, never absent (INV-9). A prior
    record whose row cannot be AFFIRMED because the store EXISTS but is busy
    with a live writer or unreadable -> `unaffirmable_session`, and the caller
    FAILS CLOSED with `blocked` BEFORE dispatching, mirroring the closed
    interpretation of §2.3b ("no se puede afirmar" -> `blocked`): after a
    `timeout` the prior worker of the same packet may still be alive and
    writing, and a second one would be the double writer INV-10 forbids. Never
    fail open on that corner; the check never invents an attempt either.

    A store that does NOT exist is a different, determinate fact (§2.7: a row
    that is idle, or absent, does not block): no writer can be holding a store
    SQLite has not created yet, so there is no row to affirm and this is not
    the unaffirmable corner.

    No automatic retry is ever produced here (INV-3): the caller blocks, it
    never re-dispatches and never opens a standalone next to a live writer
    (INV-10). Returns `{"blocking_session": ..., "unaffirmable_session": ...,
    "reads": N}`.
    """
    if not isinstance(execution_id, str):
        return {"blocking_session": None, "unaffirmable_session": None,
                "reads": 0}
    base = project_root / DISPATCHES_RELPATH / execution_id / "dispatches"
    if not base.is_dir():
        return {"blocking_session": None, "unaffirmable_session": None,
                "reads": 0}
    reads = 0
    blocking: str | None = None
    unaffirmable: str | None = None
    for path in sorted(base.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(record, dict) or record.get("packet_id") != packet_id:
            continue
        prior_session = _as_text(record.get("session"))
        if prior_session is None:
            continue
        reads += 1
        if not store_path.is_file():
            # The durable surface ITSELF is absent: no writer can be holding
            # it (SQLite creates it on open) and the prior row is
            # determinately not in it -- §2.7: a row that is idle, or absent,
            # does not block. This is NOT the unaffirmable corner below.
            continue
        try:
            state = _store_state(store_path, prior_session)
        except (_StoreBusy, AdapterError):
            # The store EXISTS but its row cannot be affirmed right now (a
            # live writer holds the lock, or the store is unreadable/unknown
            # schema): fail closed -- `unknown` is not `absent` (INV-9/INV-10).
            if unaffirmable is None:
                unaffirmable = prior_session
            continue
        if state["kind"] == "no-idle" and blocking is None:
            blocking = prior_session
    return {"blocking_session": blocking, "unaffirmable_session": unaffirmable,
            "reads": reads}


def _wait_budget(timeout: float | None, grace: float) -> float | None:
    """§2.5: the internal budget is `timeout - WAIT_RESERVE - g`.

    `g` (the effective terminate grace) is taken out of the bound so the
    ordered termination of the client's group also fits INSIDE the interface's
    own bound (PD-11).
    """
    if timeout is None:
        return None
    return max(0.0, timeout - WAIT_RESERVE_SECONDS - grace)


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


def _validate_service_keys(service: Any) -> str | None:
    """Validate the `service.*` keys (spec §2.1), unconditionally.

    Returns an actionable diagnosis naming the offending key, or `None` when
    every declared key is well-typed. Called BEFORE the packet request is
    loaded: an invalid `service.require` type blocks before anything is invoked
    or registered. The TYPE is validated in every mode; the EFFECT of a valid
    value outside the service mode is to be ignored and recorded (D-10).
    """
    if service is None:
        return None
    if not isinstance(service, dict):
        return (f"invalid `service` key: expected an object, got "
                f"{type(service).__name__} (spec §2.1)")
    if "require" in service and not isinstance(service["require"], bool):
        return (f"invalid `service.require`: expected a boolean, got "
                f"{service['require']!r} (spec §2.1)")
    return None


def _resolve_mode_effective(mode_requested: str, server_raw: str | None) -> str:
    """Spec §2.2 selection table. Returns `server`/`service`/`standalone`/`none`.

    `none` means `mode: server` (declared or by compatibility, since a
    `server` key present with `mode` undeclared is treated as an intended
    server mode, INV-2: no silent fallback to standalone on a bad URL) was
    requested without a valid URL: `blocked` before any invocation.

    `service` is PROVISIONAL: the effective mode is decided by the service
    preflight (§2.3b), which can keep `service`, declare the counted
    `standalone` fallback or resolve to `none` (`blocked`). `service` ignores
    any declared `server` (like `standalone`): it is the client that finds the
    service, without a URL.
    """
    if mode_requested == "service":
        return "service"
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

    The first one PRESENT and NON-EMPTY in the environment wins, even if it
    later turns out to be wrong (never falls through to the second while the
    first carries a value). An empty value is ABSENT (§2.3, O-1): it is never
    sent as an empty header, so the next key -- and then the credential file
    -- still applies. `None` means the environment carries no credential at
    all; what happens next is 006-003 U6/§2.3 (the credential file).
    """
    for variable in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
        value = os.environ.get(variable)
        if value:
            return value
    return None


# ----------------------- 006-003 U6: the server credential file (§2.3/D5)


def _credential_file_path() -> Path:
    """The RESOLVED credential file (§2.2/§2.3/D5): `credential_env_file` of
    the delegation config when it declares one, the default
    `<config-dir>/cdad/opencode-server.env` otherwise.

    Resolved even when no credential is found: the 401/403 diagnosis must
    name it (PD-5a/PD-5b).
    """
    configured = cdad_delegate.delegation_credential_env_file()
    if configured:
        return Path(configured)
    return cdad_delegate.delegation_env_file_path()


def _credential_file_value(text: str) -> str | None:
    """`KEY=value` subset (§2.3/D5): the value of the accepted keys.

    Comments (`#`) and lines without `=` are ignored. An EMPTY value means
    ABSENT -- never an empty credential, so the other key still applies
    (PD-5e). Precedence inside the file is the environment's: the first
    non-empty `OPENCODE_PASSWORD` wins over `OPENCODE_SERVER_PASSWORD`.
    """
    declared: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if separator and value and key in (
                OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
            declared.setdefault(key, value)
    for key in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
        if key in declared:
            return declared[key]
    return None


def _read_credential_file(path: Path) -> dict[str, Any]:
    """Read the credential file, verifying the permissions of the OPEN fd.

    The mode comes from `os.fstat` of the descriptor actually opened (never
    `os.stat(path)`: the TOCTOU-safe pattern of `cdad_packet.py`'s project
    lock), and a group/world accessible mode (`S_IMODE(st_mode) & 0o077`) is
    REFUSED (0600 and 0400 are accepted). Returns a closed document:
    `value` (only when a non-empty credential was read), `mode`/`mode_text`
    (the found mode, when a file was opened), `problem`
    (`None`/`insecure`/`unreadable`) and `detail`. A missing file is the all
    `None` document. The value is never logged. (`stat` is imported here:
    only the `server` preflight needs it, PD-11/D-3.)
    """
    import stat

    try:
        descriptor = os.open(path, os.O_RDONLY)
    except FileNotFoundError:
        return {"value": None, "mode": None, "mode_text": None,
                "problem": None, "detail": None}
    except OSError as exc:
        return {"value": None, "mode": None, "mode_text": None,
                "problem": "unreadable", "detail": _os_error_text(exc)}
    try:
        raw_mode = os.fstat(descriptor).st_mode
        mode = stat.S_IMODE(raw_mode)
        if mode & 0o077:
            return {"value": None, "mode": mode,
                    "mode_text": stat.filemode(raw_mode), "problem": "insecure",
                    "detail": None}
        chunks = []
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            chunks.append(chunk)
    except OSError as exc:
        return {"value": None, "mode": None, "mode_text": None,
                "problem": "unreadable", "detail": _os_error_text(exc)}
    finally:
        os.close(descriptor)
    text = b"".join(chunks).decode("utf-8", errors="replace")
    return {"value": _credential_file_value(text), "mode": mode,
            "mode_text": stat.filemode(raw_mode), "problem": None, "detail": None}


def _os_error_text(exc: OSError) -> str:
    """Error text of an `OSError` without leaking anything else."""
    return f"{type(exc).__name__}: {exc.strerror or exc}"


def _preflight_credential() -> dict[str, Any]:
    """Resolve the server credential (§2.3/D5): environment first, file second.

    Only reached in `server` mode (the server preflight is the sole
    consumer). The environment wins when EITHER variable is present with a
    non-empty value (the order of `_preflight_password`); only when neither
    is present is the credential file consulted. Returns a closed document:
    `source` (`environment`/`file`/`absent`), `value` (the credential to send
    -- `None` means NO header, never an empty one), `path` (the resolved file
    path when the file was consulted, `None` for an environment value, O-4)
    plus the file document. The value never leaves the caller.
    """
    env_value = _preflight_password()
    if env_value is not None:
        return {"source": "environment", "value": env_value, "path": None,
                "mode": None, "mode_text": None, "problem": None,
                "detail": None}
    path = _credential_file_path()
    document = _read_credential_file(path)
    document["source"] = "file" if document["value"] is not None else "absent"
    document["path"] = path
    return document


def _unauthorized_diagnosis(credential: dict[str, Any]) -> str:
    """Self-sufficient 401/403 diagnosis (§2.3/D5, PD-5a/PD-5b), never the value.

    Names the accepted variables and their order, the provenance of the value
    (the password of the `opencode serve` instance in use, which must live in
    the ENVIRONMENT of the process that dispatches) and, when the value was
    read from the file, the RESOLVED path -- never an unresolvable one
    (`None`, O-4): the diagnosis names the source actually used. When the value
    came from the environment, the RESOLVED credential-file path is named TOO,
    as the documented alternative (OPT-1): a rejected environment value is
    migrated by moving it to that file. The value is never named.
    """
    path = credential["path"] or _credential_file_path()
    parts = [
        "the server rejected or required a credential (401/403; credencial "
        "ausente o rechazada). The credential is the password of the "
        "`opencode serve` instance in use (with OpenChamber, the password "
        "configured there), and it must be available to the PROCESS that "
        "dispatches: in its ENVIRONMENT under "
        f"{OPENCODE_PASSWORD_ENV} (first), then "
        f"{OPENCODE_SERVER_PASSWORD_ENV}",
    ]
    if credential["source"] == "environment":
        parts.append(
            "the value in use came FROM the ENVIRONMENT above (source: "
            "environment) and was rejected; no credential file was consulted "
            f"-- to move the credential there, the alternative is the "
            f"credential file {path} (the delegation config's "
            "`credential_env_file`, or this default) with mode 0600 or 0400")
    else:
        parts.append(
            f"or in the credential file {path} (the delegation config's "
            "`credential_env_file`, or this default) with mode 0600 or 0400")
    parts.append("The value is never shown here")
    if credential["problem"] == "insecure":
        parts.append(
            f"the credential file {path} is group/world accessible: found "
            f"mode {oct(credential['mode'])} ({credential['mode_text']}) — "
            f"refused, no credential was sent; restrict it with `chmod 600 "
            f"{path}`")
    elif credential["problem"] == "unreadable":
        parts.append(
            f"the credential file {path} could not be read "
            f"({credential['detail']}); no credential was sent")
    return " — ".join(parts) + "."


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

    The HTTP stack (`urllib.request`/`urllib.error` and `base64`, with the
    `http.client`/`ssl`/`email`/`tempfile` subtree they pull in) is imported
    HERE and not at module load: it is only needed by the SERVER preflight, and
    the adapter's own startup is on the critical path of the interface's cota
    (PD-11/D-3: measured ~0.07s of the ~0.24s module import cost, and a larger
    share of it under host load). The standalone/service dispatch -- and every
    pre-dispatch block -- must not pay it.
    """
    import base64
    import urllib.error
    import urllib.request

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

    Returns {"ok", "termination", "diagnosis", "note", "client_version",
    "server_version", "credential_value"}. `client_version` is always the
    OBSERVED `--version` fact (I8 provenance) and the ONLY control is the
    comparison between the two OBSERVED versions (client against server).

    U6-8 (owner decision, `execution.md` §hallazgo U6-8): `binary_version` is
    OPTIONAL and informative. A difference with the OBSERVED version is
    DECLARED in the returned `note` and does NOT block: a number written in the
    configuration is not an observed fact and must never gate the dispatch.
    `credential_value` is the credential this mode resolved (PD-11/§2.5) and is
    relayed to the caller so it can be injected into the CLIENT process
    environment (never into the preflight document that is emitted).
    """
    version_output, version_diag = _invoke_version(binary, timeout)
    if version_diag is not None:
        return {"ok": False, "termination": "transport-error",
                "diagnosis": version_diag, "client_version": None,
                "server_version": None}
    observed_client_version = _parse_semver(version_output)
    configured_client_version = _parse_semver(binary_version_configured)

    credential = _preflight_credential()
    info = _preflight_get_info(server_raw, credential["value"], timeout)
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
                "diagnosis": _unauthorized_diagnosis(credential),
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
    # U6-8 (owner decision): the configured `binary_version` is OPTIONAL and
    # informative -- the control compares the two OBSERVED versions, never a
    # number written in the configuration. A difference is DECLARED (it travels
    # in the note the caller attaches to the diagnosis) and does NOT block.
    note: str | None = None
    if (configured_client_version is not None
            and configured_client_version != server_version):
        note = (
            f"the configured `binary_version` {binary_version_configured!r} "
            f"differs from the observed runtime version {server_version!r}: "
            "the version is OBSERVED, never read from the configuration — the "
            "difference is declared and does not block (the compatibility of "
            "the store is verified by capacity, not by this number)")
    return {"ok": True, "termination": None, "diagnosis": None, "note": note,
            "client_version": observed_client_version,
            "server_version": server_version,
            "credential_value": credential["value"]}


# ------------------------------------------- 006-001 T1b: service preflight


def _invoke_service_status(binary: str, timeout: float
                           ) -> tuple[str | None, int, str | None]:
    """`binary service status` (spec §2.3b point 1), bounded and read-only.

    The ONLY invocation of `service` CDAD ever makes (INV-2): the subcommand
    prints the service URL or `stopped` and starts nothing (observed fact).
    Returns `(stdout, rc, diagnosis)`; a `None` stdout means the subcommand
    could not be observed (timeout, or the binary could not be started) -- a
    fail-closed `unexpected` answer, never a standalone.
    """
    try:
        proc = subprocess.run(
            [binary, *SERVICE_STATUS_ARGV], capture_output=True,
            stdin=subprocess.DEVNULL, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, -1, (
            f"`service status` did not answer within the preflight bound "
            f"({timeout} seconds)")
    except OSError as exc:
        return None, -1, f"destination binary {binary!r} could not be started: {exc}"
    output = (proc.stdout or b"").decode("utf-8", errors="replace")
    return output, proc.returncode, None


def _interpret_service_status(output: str | None, rc: int) -> str:
    """Closed interpretation of `service status` (spec §2.3b point 1).

    One line that is a valid `http`/`https` URL (host, no userinfo) -> the
    service RUNS; the literal `stopped` -> it does NOT run; anything else
    (empty output, several lines, unrecognized text, rc != 0 or a missing
    answer) -> `unexpected`: CDAD cannot affirm the service is stopped. The URL
    output is discarded here and never stored or emitted (PD-5/INV-6).
    """
    if output is None or rc != 0:
        return SERVICE_STATUS_UNEXPECTED
    text = output.strip()
    if not text or "\n" in text:
        return SERVICE_STATUS_UNEXPECTED
    if text == SERVICE_STATUS_STOPPED_LITERAL:
        return SERVICE_STATUS_STOPPED
    if _valid_server_url(text):
        return SERVICE_STATUS_RUNNING
    return SERVICE_STATUS_UNEXPECTED


def _service_state_dir() -> Path:
    """The state directory the service registry lives under (D-11).

    Resolved from `XDG_STATE_HOME` (the runtime's own XDG convention), falling
    back to the XDG default `~/.local/state`. The path is an OBSERVED fact, not
    a public contract (debt DT-6); the fixture fixes `XDG_STATE_HOME` to a
    disposable directory, so no real HOME registry is read in the suite.
    """
    xdg_state = os.environ.get("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state)
    return Path.home() / ".local" / "state"


def _service_registry_path() -> Path | None:
    """First existing service-registry candidate under the state dir, or None."""
    base = _service_state_dir()
    for rel in SERVICE_REGISTRY_RELPATHS:
        candidate = base.joinpath(*rel)
        if candidate.is_file():
            return candidate
    return None


def _read_service_version(registry_path: Path) -> str | None:
    """Project ONLY the `version` key of the service registry (D-11).

    A ONE-KEY projection: the document (with its password and URL) never leaves
    this function; the caller receives the version text or `None` (absent file,
    not parseable, or key absent/non-textual). Fail closed: an unverifiable
    version never degrades into opening a standalone next to a running service.
    """
    try:
        raw = registry_path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        document = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(document, dict):
        return None
    version = document.get("version")
    if not isinstance(version, str) or not version.strip():
        return None
    return version.strip()


def _preflight_service(binary: str, timeout: float, require: bool,
                       binary_version_configured: str | None) -> dict[str, Any]:
    """Spec §2.3b: `service status` once, then -- only if it RUNS -- the D-11
    version gate and the client `--version`.

    Returns a decision dict. `termination` is `None` when the caller must
    continue (service dispatch, or the counted `standalone` fallback); otherwise
    it is the pre-dispatch termination with its actionable diagnosis. The dict
    carries the provenance values (`mode_effective`, `dispatch_flags`,
    `service_status`, `fallback`, `client_version`, `server_version`).
    """
    output, rc, status_diag = _invoke_service_status(binary, timeout)
    status = _interpret_service_status(output, rc)
    if status == SERVICE_STATUS_UNEXPECTED:
        detail = status_diag or "salida no reconocible de `service status`"
        return {
            "termination": "blocked",
            "diagnosis": (
                "the background service status could not be asserted "
                f"({detail}): CDAD cannot affirm that the service is stopped "
                "and refuses to open a standalone next to it (INV-10). Check "
                "`opencode service status` manually; CDAD never starts, "
                "restarts or reconfigures the service"),
            "mode_effective": "none", "dispatch_flags": DISPATCH_FLAG_NONE,
            "service_status": SERVICE_STATUS_UNEXPECTED,
            "fallback": FALLBACK_NONE,
            "client_version": None, "server_version": None,
        }
    if status == SERVICE_STATUS_STOPPED:
        if require:
            return {
                "termination": "blocked",
                "diagnosis": (
                    "el servicio de fondo no corre (`service status` reports "
                    "stopped) and `service.require` is true: have the operator "
                    "or the owner start the service, or declare `mode: "
                    "standalone` explicitly (CDAD never runs `service start`)"),
                "mode_effective": "none", "dispatch_flags": DISPATCH_FLAG_NONE,
                "service_status": SERVICE_STATUS_STOPPED,
                "fallback": FALLBACK_NONE,
                "client_version": binary_version_configured,
                "server_version": None,
            }
        return {
            "termination": None,
            "diagnosis": (
                "servicio no disponible (`service status` reports stopped): "
                "declared fallback `service` -> `standalone` "
                f"({FALLBACK_SERVICE_UNAVAILABLE})"),
            "mode_effective": "standalone",
            "dispatch_flags": DISPATCH_FLAG_STANDALONE,
            "service_status": SERVICE_STATUS_STOPPED,
            "fallback": FALLBACK_SERVICE_UNAVAILABLE,
            "client_version": binary_version_configured,
            "server_version": "same-binary(standalone)",
        }
    # The service RUNS: observe the client version (D-2: `--version` only when
    # it runs) BEFORE the D-11 version gate.
    version_output, version_diag = _invoke_version(binary, timeout)
    if version_diag is not None:
        return {
            "termination": "blocked",
            "diagnosis": version_diag,
            "mode_effective": "none", "dispatch_flags": DISPATCH_FLAG_NONE,
            "service_status": SERVICE_STATUS_RUNNING,
            "fallback": FALLBACK_NONE,
            "client_version": None, "server_version": None,
        }
    client_version = _parse_semver(version_output)
    registry_path = _service_registry_path()
    service_version_raw = (
        _read_service_version(registry_path)
        if registry_path is not None else None)
    service_version = _parse_semver(service_version_raw)
    if client_version is None or service_version is None:
        return {
            "termination": "blocked",
            "diagnosis": (
                "versión del servicio no verificable: the running service "
                "registry carries no parseable `version` (D-11); prepare a "
                "compatible service, or declare `mode: standalone` or "
                "`mode: server` explicitly. Never a standalone next to a "
                "running service (INV-10)"),
            "mode_effective": "none", "dispatch_flags": DISPATCH_FLAG_NONE,
            "service_status": SERVICE_STATUS_RUNNING,
            "fallback": FALLBACK_NONE,
            "client_version": client_version,
            "server_version": service_version_raw,
        }
    if client_version != service_version:
        return {
            "termination": "blocked",
            "diagnosis": (
                f"service version {service_version!r} does not match the "
                f"observed client version {client_version!r}: prepare a "
                "compatible service, or declare `mode: standalone` or "
                "`mode: server` explicitly. Never a standalone next to a "
                "running service (INV-10)"),
            "mode_effective": "none", "dispatch_flags": DISPATCH_FLAG_NONE,
            "service_status": SERVICE_STATUS_RUNNING,
            "fallback": FALLBACK_NONE,
            "client_version": client_version, "server_version": service_version,
        }
    return {
        "termination": None,
        "diagnosis": None,
        "mode_effective": "service",
        "dispatch_flags": DISPATCH_FLAG_NONE,
        "service_status": SERVICE_STATUS_RUNNING,
        "fallback": FALLBACK_NONE,
        "client_version": client_version, "server_version": service_version,
    }


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
                 dispatch_flags: str = DISPATCH_FLAG_NONE,
                 service_status: str = SERVICE_STATUS_NOT_CHECKED,
                 fallback: str = FALLBACK_NONE,
                 store_reads: str = "unknown",
                 prior_check_reads: str = "unknown") -> dict[str, Any]:
    """Build the closed-key I8 observation document (PD-3/PD-8).

    PD-6: when the adapter wrote this record for the WORKER attempt, `session`
    and `model_reported` come from the correlated durable row
    (`session_v2.id` / `session_v2.model`) and the provenance declares it;
    `runtime` keeps coming from the execution config and `model_configured`
    from the delegation config (006-003 D3), never from the exec-config.

    006-001 §2.6 (PD-3, enmienda 001): the provenance text carries the new pairs
    in free text (the I8 schema stays closed, INV-4): `dispatch_flags=`,
    `service_status=` and `fallback=` are ADDED AT THE END of `provenance.runtime`
    (v1's four pairs keep their order); the service mode registers
    `mode_requested=service` / `mode_effective=service` and
    `service_status=not-checked` outside the service mode.
    `session_base` is one of the three literal alternatives the spec names
    (`durable session row (exec-config: sessions_db): session_v2.id` | `chosen by
    adapter` | `not dispatched`); `row_state` is `present`/`absent`/`unknown`
    (INV-9: unknown is never 0 nor empty). `store_reads`/`prior_check_reads` stay
    the LAST pairs of `provenance.session`: T2 parses them by substring.
    """
    runtime_provenance = (
        "execution config (--exec-config): runtime; "
        f"mode_requested={mode_requested}; mode_effective={mode_effective}; "
        f"client_version={client_version or 'unknown'}; "
        f"server_version={server_version or 'unknown'}; "
        f"dispatch_flags={dispatch_flags}; "
        f"service_status={service_status}; "
        f"fallback={fallback}")
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
            "model_configured": (
                "delegation config (delegation.json): "
                f"models.{DESTINATION_ID}"),
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
                       attempt_id: str, observation: dict[str, Any],
                       continuity_attempt: int | None = None) -> None:
    """Register the attempt in the SAME I8 ledger (reused machinery, PD-2).

    007-003 §2.2 (enmienda): the integer continuity attempt the entry
    propagated travels with the registration. When the execution has no
    continuity the flag is omitted and the record DECLARES `continuity:
    absent`; the adapter never infers the integer.
    """
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
             *(["--continuity-attempt", str(continuity_attempt)]
               if continuity_attempt is not None else []),
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
                 descriptor_path: Path,
                 continuity_attempt: int | None = None) -> None:
    """Persist the delivery through the existing `receive` flow (PD-7).

    The receipt stays `semantic_status: "pending"`: the delivery is not a gate
    (INV-5). 007-003 §2.3.3: the integer continuity attempt travels with the
    arrival, so the reception closes it; it is never inferred here."""
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
             "--descriptor", str(descriptor_path),
             *(["--continuity-attempt", str(continuity_attempt)]
               if continuity_attempt is not None else [])],
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
                      dispatch_flags: str = DISPATCH_FLAG_NONE,
                      service_status: str = SERVICE_STATUS_NOT_CHECKED,
                      fallback: str = FALLBACK_NONE,
                      model_reported: str | None = None,
                      store_reads: str = "unknown",
                      prior_check_reads: str = "unknown",
                      continuity_attempt: int | None = None) -> str:
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
    # 006-001 §2.6: the row is present (the row we just classified from), and
    # `store_reads`/`prior_check_reads` report the counts of THIS attempt
    # (PD-3: the I8 count is contrasted against the fixture trace, PD-10).
    observation = _observation(
        runtime, model, binary_version, session, started_at,
        mode_requested=mode_requested, mode_effective=mode_effective,
        client_version=client_version, server_version=server_version,
        session_base=(
            "durable session row (exec-config: sessions_db): session_v2.id"),
        row_state="present", model_reported=model_reported,
        dispatch_flags=dispatch_flags, service_status=service_status,
        fallback=fallback, store_reads=store_reads,
        prior_check_reads=prior_check_reads)
    _register_dispatch(project_root, packet_id, request, attempt_id, observation,
                       continuity_attempt)

    inbox = project_root / ".cdad" / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    part_name = f"{attempt_id}-{FINAL_TEXT_PART}"
    staged = inbox / f"{part_name}.md"
    staged.write_bytes(final_text.encode("utf-8"))

    # §2.8/PD-23/INV-14: the kind of the delivered part is DERIVED from the
    # packet's role and subphase (the closed table is the single source), never
    # the fixed constant that made another role's report impossible to
    # materialize.
    artifact_kind = _derived_artifact_kind(
        _as_text(request.get("role")) or "", _as_text(request.get("substage")) or "")

    descriptor = {
        "schema_version": 1,
        "execution_id": execution_id,
        "packet_id": packet_id,
        "feature_id": feature_id,
        "source": {"kind": "staged-file", "sdk_message_ref": None},
        "parts": [{
            "name": part_name,
            "artifact_kind": artifact_kind,
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
        _run_receive(project_root, execution_id, packet_id, descriptor_path,
                     continuity_attempt)
    finally:
        staged.unlink(missing_ok=True)
        descriptor_path.unlink(missing_ok=True)

    return str(project_root / cdad_result.RESULTS_RELPATH / execution_id
               / packet_id / RECEIPT_NAME)


# ------------------------------ 006-005 U2: capabilities and observation


def _read_store_columns(store_path: Path) -> list[str]:
    """The observable `session_v2` columns, through ONE read-only access.

    §2.2/PD-13: URI `mode=ro` (never `immutable`, never a writable connection);
    the schema is introspected inside the same single access. Fails closed when
    the store does not exist or is not readable SQLite -- an unknown store is
    never degraded into a supposed capability.
    """
    if not store_path.is_file():
        raise AdapterError(
            f"the durable session store {store_path} declared by the execution "
            "configuration (sessions_db) does not exist")
    try:
        conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True, timeout=0)
    except sqlite3.Error as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    try:
        return sorted(_table_columns(conn, SESSION_V2_TABLE))
    except _StoreBusy as exc:
        raise AdapterError(
            f"the durable session store {store_path} is momentarily locked by "
            f"a live writer ({exc}): the capability cannot be observed now and "
            "this surface performs ONE bounded read, never a poll") from exc
    except sqlite3.DatabaseError as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    finally:
        conn.close()


def _observed_binary_version(binary: str | None) -> tuple[str, str | None]:
    """The version OBSERVED on the binary (§2.2): never a supposed one."""
    if binary is None:
        return VERSION_UNKNOWN, (
            "the execution configuration declares no destination binary "
            "(`binary`): the version cannot be observed")
    output, diagnosis = _invoke_version(
        binary, DEFAULT_WAIT_VALUES["preflight_timeout_seconds"])
    if diagnosis is not None:
        return VERSION_UNKNOWN, diagnosis
    lines = [line.strip() for line in (output or "").splitlines()
             if line.strip()]
    if not lines:
        return VERSION_UNKNOWN, (
            f"the destination binary {binary!r} answered `--version` with no "
            "observable version")
    return lines[0], None


def _capabilities_document(config: dict[str, Any],
                          config_note: str | None = None) -> dict[str, Any]:
    """§2.2/PD-10/O-3: the declared capabilities of this runtime module.

    Exactly the five declared keys: `native_observation`, `external_transport`,
    `session_correlation`, `version` and `reason`. `session_correlation` is true
    only when the store of the version OBSERVED exposes the identity key this
    path evaluates (`agent`) **and reaches the §2.3 discrimination threshold**
    (at least one discriminating key -- parent, moment or project/directory);
    the `reason` DECLARES the observed columns and, when a capability is denied,
    names what is missing (never a silent degradation).
    """
    binary = _as_text(config.get("binary"))
    version, version_note = _observed_binary_version(binary)
    store_raw = _as_text(config.get("sessions_db"))
    remarks: list[str] = []
    if config_note is not None:
        remarks.append(config_note)
    columns: list[str] = []
    if store_raw is None:
        remarks.append(
            "the execution configuration declares no durable session store "
            "(`sessions_db`): the columns of the observed version cannot be "
            "declared")
    else:
        try:
            columns = _read_store_columns(Path(store_raw))
        except AdapterError as exc:
            remarks.append(str(exc))
    agent_observable = SESSION_CORRELATION_AGENT_COLUMN in columns
    discriminating = [column for column
                      in SESSION_CORRELATION_DISCRIMINATING_COLUMNS
                      if column in columns]
    session_correlation = agent_observable and bool(discriminating)
    if columns:
        remarks.append("the observed store exposes: " + ", ".join(columns))
        if not agent_observable:
            remarks.append(
                f"the `{SESSION_CORRELATION_AGENT_COLUMN}` column is absent: "
                "the identity key of the correlation is not observable")
        if not discriminating:
            remarks.append(
                "no discriminating key is evaluable (neither a parent column, "
                "nor the moment `time_created`, nor a project/directory "
                "column): the `agent` key alone does not discriminate (two "
                "concurrent dispatches of the same role share it), so this "
                "path does not reach the §2.3 threshold")
    if version_note is not None:
        remarks.append(version_note)
    if session_correlation:
        remarks.append(
            "the observed version reaches the §2.3 discrimination threshold")
    return {
        "native_observation": session_correlation,
        "external_transport": True,
        "session_correlation": session_correlation,
        "version": version,
        "reason": "; ".join(remarks),
    }


def _normalized_observation(row: dict[str, Any]) -> dict[str, Any]:
    """The ONE normalization boundary of the observed row (B-2, 006-005).

    The store's `time_created` is an epoch-MILLISECONDS integer and its `model`
    is the JSON document the runtime wrote; the entry understands an ISO
    instant and the `<provider>/<model>` form. Both are normalized HERE, so
    the row the entry consumes is the same document whichever way it was
    selected — by `--session` or by `--parent`.

    B-2: normalizing only the `--parent` selection made the SAME store read
    two different verdicts: the row selected by id kept the raw integer (the
    moment key stayed `unknown`, so the session was never accredited and a
    contradicting moment degraded to `unknown` instead of the rejection
    INV-2 demands). U6-6/D-ADP-2: the model is rendered with the external
    path's single normalization (`_model_reported_from_row`), never a
    fabricated value.
    """
    document = dict(row)
    if STORE_MOMENT_COLUMN in document:
        moment = _store_instant(document[STORE_MOMENT_COLUMN])
        if moment is not None:
            document[STORE_MOMENT_COLUMN] = moment.isoformat()
    if STORE_MODEL_COLUMN in document:
        document[STORE_MODEL_COLUMN] = _model_reported_from_row(
            document[STORE_MODEL_COLUMN])
    return document


def _observe_document(store_path: Path, session_id: str | None,
                      parent_id: str | None, agent: str | None = None,
                      since: str | None = None
                      ) -> tuple[dict[str, Any] | None, str | None]:
    """§2.2/PD-12/PD-13 + U6-4: the observable row of the correlated attempt.

    ONE bounded access to the store, READ ONLY (no polling, no write): the row
    the external path correlates by the session id the module itself chose, or
    the candidate row of the dispatching session (`parent_id`) the native path
    declares. The keys this path evaluates are REQUIRED: a store that does not
    expose them fails closed NAMING the absent column, never degrading to
    `absent` nor fabricating a row. The native selection is U6-4's: candidates
    are the rows under the declared parent with the packet's `agent` and a
    moment after `--since`; exactly one is returned, more than one is NAMED as
    an ambiguity and nothing is accredited (never a rejection). The returned
    document carries `store_reads`, the accesses of the correlated row performed
    by this invocation (exactly one). U6-6/D-ADP-2: its `model` is rendered with
    the external path's single normalization (`_model_reported_from_row`), so
    both dispatch paths report the same `model_reported`. The second element is a
    diagnostic that does not accredit a row (the entry declares it).
    """
    if session_id is None and parent_id is None:
        raise AdapterError(
            "`--observe` needs the correlation evidence of the attempt: the "
            "session id (`--session`) the external path chose, or the "
            "dispatching session (`--parent`) of the native path")
    if not store_path.is_file():
        raise AdapterError(
            f"the durable session store {store_path} declared by the execution "
            "configuration (sessions_db) does not exist")
    try:
        conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True, timeout=0)
    except sqlite3.Error as exc:
        raise AdapterError(
            f"the durable session store {store_path} is not readable as "
            f"SQLite: {exc}") from exc
    try:
        columns = sorted(_table_columns(conn, SESSION_V2_TABLE))
        if not columns:
            raise AdapterError(
                f"the durable session store {store_path} does not expose the "
                f"{SESSION_V2_TABLE} table: refusing to observe an unknown "
                "schema and refusing to fabricate a row")
        required = list(SESSION_OBSERVATION_KEY_COLUMNS)
        if session_id is None:
            required.append("parent_id")
            if since is not None:
                required.append(STORE_MOMENT_COLUMN)
        missing = [column for column in required if column not in columns]
        if missing:
            raise AdapterError(
                f"the durable session store {store_path} lacks the column(s) "
                f"this observation evaluates: missing {', '.join(missing)} "
                f"(session_v2.{SESSION_CORRELATION_AGENT_COLUMN} is the "
                "identity key of the correlation). Refusing to observe an "
                "unknown schema and refusing to fabricate a row")
        detail: str | None = None
        if session_id is not None:
            row = _fetch_session_row(conn, session_id)
        else:
            row, detail = _native_candidate(conn, parent_id, agent, since)
    except _StoreBusy as exc:
        raise AdapterError(
            f"the durable session store {store_path} is momentarily locked by "
            f"a live writer ({exc}): this observation performs ONE bounded "
            "read and never polls -- reconcile and repeat") from exc
    finally:
        conn.close()
    if row is None:
        return None, detail
    document = _normalized_observation(row)
    document[STORE_READS_KEY] = 1
    return document, detail


def _surface_config(args: argparse.Namespace) -> tuple[dict[str, Any], str | None]:
    """The internal execution configuration of a §2.2 surface and a note.

    These surfaces answer WITHOUT the transport of a packet: the configuration
    is optional and a config that cannot be read is DECLARED (the capability
    cannot be accredited), never a traceback and never a silent fallback.
    Returns `(config, note)`; `note` is not `None` when the configuration could
    not be read (the document stays the closed five-key one).
    """
    if not args.exec_config:
        return {}, None
    try:
        return _load_json(Path(args.exec_config), "execution config"), None
    except AdapterError as exc:
        return {}, (
            f"the execution configuration handed to the module is not readable "
            f"JSON ({exc}): no version and no store column can be observed")


def _run_capabilities(args: argparse.Namespace) -> int:
    """`--capabilities`: the five §2.2 keys on stdout (rc=0, never a fallback)."""
    config, config_note = _surface_config(args)
    document = _capabilities_document(config, config_note=config_note)
    sys.stdout.write(
        json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


def _run_observe(args: argparse.Namespace) -> int:
    """`--observe`: ONE bounded read-only access, the row or `null` on stdout.

    A store/schema that cannot be observed fails closed with rc≠0 and a
    diagnosis on stderr that names the absent column (never a fabricated row).
    """
    config, config_note = _surface_config(args)
    if config_note is not None:
        sys.stderr.write(config_note + "\n")
        return 2
    store_raw = _as_text(config.get("sessions_db"))
    if store_raw is None:
        sys.stderr.write(
            "`--observe` requires the durable session store (`sessions_db`) in "
            "the execution configuration\n")
        return 2
    try:
        document, detail = _observe_document(
            Path(store_raw), _as_text(args.session), _as_text(args.parent),
            _as_text(args.agent), _as_text(args.since))
    except AdapterError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    if detail:
        sys.stderr.write(detail + "\n")
    sys.stdout.write(
        json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


# --------------------------------------------------------------- envelope


def _envelope(*, attempt: str | None = None, session: str | None,
              termination: str, delivery_ref: str | None,
              diagnosis: str | None) -> dict[str, Any]:
    return {
        "attempt": _as_text(attempt),
        "session": _as_text(session),
        "termination": termination,
        "delivery_ref": _as_text(delivery_ref),
        "diagnosis": _as_text(diagnosis),
    }


def _classify(row: dict[str, Any],
              final_text: str | None,
              idle_error: tuple[str | None, str | None] | None = None
              ) -> tuple[str, str | None, str | None, str | None]:
    """Classify the correlated durable row into the termination vocabulary.

    PD-5: the termination comes from the MATERIAL fact of the row's
    `idle_outcome` (never the client rc). Only `completed` carries a final text
    (delivery); every other termination never fabricates a receipt.

    006-001 T2 (PD-7): a `failed` row carries the durable `error.type` /
    `error.message` of its LAST `idle` message -- the message is bounded to
    `IDLE_ERROR_MESSAGE_LIMIT` characters so a very long durable error never
    floods the diagnosis.
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
        detail = ""
        if idle_error is not None:
            error_type, error_message = idle_error
            parts = []
            if error_type is not None:
                parts.append(f"error.type={error_type}")
            if error_message is not None:
                parts.append(
                    f"error.message={error_message[:IDLE_ERROR_MESSAGE_LIMIT]}")
            if parts:
                detail = f" ({', '.join(parts)})"
        return "blocked", session, None, (
            f"the correlated durable session row reports idle_outcome 'failed'"
            f"{detail}: the role session is blocked; obtain a re-entry with "
            "changed conditions before repeating the delegation")
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
    # `--project-root`/`--packet-id` are required for the dispatch errand (the
    # transport of a published packet) but NOT for the §2.2 surfaces the
    # orchestrator's entry asks standalone (`--capabilities`).
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--packet-id", default=None)
    parser.add_argument("--destination", default=DESTINATION_ID)
    parser.add_argument("--exec-config", default=None)
    # 006-005 §2.2 (PD-10/PD-12/PD-13): the declared surfaces of the integration.
    parser.add_argument("--capabilities", action="store_true")
    parser.add_argument("--observe", action="store_true")
    parser.add_argument("--session", default=None)
    parser.add_argument("--parent", default=None)
    # 006-005 U6-4: the native selection's declared evidence. `--agent` is the
    # packet's agent (`REQUEST.json.agent`); `--since` is the ISO instant the
    # moment key is measured against. The store's unit is known HERE, not there.
    parser.add_argument("--agent", default=None)
    parser.add_argument("--since", default=None)
    # 007-003 §2.3.3: the integer continuity attempt of the arrival. The
    # external entry propagates it; the adapter never infers it and hands it to
    # the SAME common close the re-entry uses.
    parser.add_argument("--continuity-attempt", type=int, default=None,
                        metavar="N")
    return parser


def _read_packet_stdin() -> bytes:
    try:
        data = sys.stdin.buffer.read()
    except (OSError, ValueError) as exc:
        raise AdapterError(f"cannot read the transported packet from stdin: {exc}") from exc
    if not data:
        raise AdapterError("no packet was transported on stdin")
    return data


def _continuity_attempt(args: argparse.Namespace) -> int | None:
    """007-003 §2.3.3: the integer the entry propagated; never inferred."""
    value = getattr(args, "continuity_attempt", None)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise AdapterError(
            f"--continuity-attempt must be a positive integer; got {value!r}")
    return value


def delegate(args: argparse.Namespace) -> dict[str, Any]:
    if not args.project_root:
        raise AdapterError("--project-root is required for a dispatch")
    if not args.packet_id:
        raise AdapterError("--packet-id is required for a dispatch")
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
    service_keys_diagnosis = _validate_service_keys(config.get("service"))
    if service_keys_diagnosis is not None:
        return _envelope(session=None, termination="blocked",
                         delivery_ref=None, diagnosis=service_keys_diagnosis)

    # 006-001 §2.1: every `wait.*` value is validated above; the declared keys
    # (or their portable defaults) drive the proportional wait of §2.4.
    poll_initial = float(wait_dict.get(
        "poll_initial_seconds", DEFAULT_WAIT_VALUES["poll_initial_seconds"]))
    poll_max = float(wait_dict.get(
        "poll_max_seconds", DEFAULT_WAIT_VALUES["poll_max_seconds"]))
    settle_seconds = float(wait_dict.get(
        "settle_seconds", DEFAULT_WAIT_VALUES["settle_seconds"]))
    terminate_grace_seconds = float(wait_dict.get(
        "terminate_grace_seconds", DEFAULT_WAIT_VALUES["terminate_grace_seconds"]))

    packet_dir = project_root / ".cdad" / "packets" / args.packet_id
    request = _load_json(packet_dir / "REQUEST.json", "packet request")
    role = _as_text(request.get("role"))
    if role is None:
        raise AdapterError(f"packet {args.packet_id!r} request has no role")
    execution_id_value = _as_text(request.get("execution_id"))
    # 006-005 PD-14/§2.7 (D-ADP-4): the agent travels IN THE PACKET
    # (`REQUEST.json.agent`, role + `stack`); a packet published before the
    # feature uses the role agent and its absent field is DECLARED, never
    # silenced (the note travels in this attempt's diagnosis).
    agent, agent_note = _packet_agent(request, role)

    packet_bytes = _read_packet_stdin()
    started_at = _now()
    attempt_id = f"opencode-{uuid.uuid4().hex[:12]}"

    def envelope(**fields: Any) -> dict[str, Any]:
        """006-005 PD-1/§2.2: declare in THIS attempt's envelope the attempt the
        adapter registered, so whoever invokes the adapter RELAYS it instead of
        replacing it (the interface owns no attempt of its own). A termination
        before the attempt exists declares `None` (nothing was registered)."""
        return _envelope(attempt=attempt_id, **fields)

    mode_effective = _resolve_mode_effective(mode_requested, server_raw)
    # `service.require` (D-10) only has an EFFECT in the service mode; its TYPE
    # is validated above in every mode.
    service_config = config.get("service")
    service_require = (
        bool(service_config.get("require", False))
        if isinstance(service_config, dict) else False)
    # 006-001 §2.6 provenance defaults; the service preflight (§2.3b) overwrites
    # them (late-bound closure values read at register time) and a pre-dispatch
    # block in standalone already declares the flag it would have used.
    dispatch_flags = (
        DISPATCH_FLAG_SERVER if mode_effective == "server"
        else DISPATCH_FLAG_STANDALONE if mode_effective == "standalone"
        else DISPATCH_FLAG_NONE)
    service_status = SERVICE_STATUS_NOT_CHECKED
    fallback = FALLBACK_NONE
    # A note the service preflight attaches to a NON-blocking outcome (the
    # declared standalone fallback): it travels in the envelope's diagnosis so
    # the caller sees the cause and the declared transition (PD-13).
    dispatch_note: str | None = None
    # 006-001 T2 (PD-3): the counters THIS attempt reports in
    # `provenance.session`. `unknown` until the corresponding work runs
    # (INV-9: unknown is never 0 nor empty); the prior attempt check and the
    # durable wait (PD-10) set them to the reads they performed.
    store_reads_value: Any = "unknown"
    prior_check_reads_value: Any = "unknown"

    def register_note(*, session: str | None, session_base: str,
                      row_state: str, client_version: str | None,
                      server_version: str | None) -> str | None:
        """006-001 §2.6 (PD-3): register the WORKER's own attempt in the
        SAME I8 ledger in EVERY termination posterior to loading
        REQUEST.json. After the 006-005 U6-5 write-ahead this call is the ONE
        completion of the provisional record (D-U65-2); a registration failure
        never changes the termination (D-5): it only adds a bounded note to the
        diagnosis."""
        observation = _observation(
            runtime, model, binary_version, session, started_at,
            mode_requested=mode_requested, mode_effective=mode_effective,
            client_version=client_version, server_version=server_version,
            session_base=session_base, row_state=row_state,
            dispatch_flags=dispatch_flags, service_status=service_status,
            fallback=fallback, store_reads=store_reads_value,
            prior_check_reads=prior_check_reads_value)
        try:
            _register_dispatch(project_root, args.packet_id, request,
                               attempt_id, observation,
                               _continuity_attempt(args))
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
        return envelope(session=None, termination=termination,
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    def blocked_before_dispatch(diagnosis: str, *,
                                client_version: str | None = "unknown",
                                server_version: str | None = "unknown"
                                ) -> dict[str, Any]:
        return pre_dispatch_termination(
            "blocked", diagnosis, client_version=client_version,
            server_version=server_version)

    # 006-003 D3/§2.2: the model comes ONLY from the delegation config, by
    # destination and role (no fallback to the exec-config, which is now
    # ignored). A config that cannot be parsed fails closed before anything
    # is invoked.
    try:
        model = cdad_delegate.delegation_model(DESTINATION_ID, role)
    except cdad_delegate.DelegateError as exc:
        return blocked_before_dispatch(
            f"the delegation config is not usable: {exc}")

    # PD-3/PD-14: verify the derived agent of the PACKET is published BEFORE
    # dispatching anything. A missing derived agent fails closed here; the CLI
    # `mode:` no longer conditions the dispatch (the durable identity is the
    # barrier instead).
    unpublished_diagnosis = _check_derived_agent_published(project_root, agent)
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

    # 006-001 §2.1 cota mínima (PD-11): `wait.timeout_seconds` must exceed the
    # fixed reserve; at or below it there is no budget left for the
    # invocation/wait, so the adapter BLOCKS before dispatching anything.
    if timeout is not None and timeout <= WAIT_RESERVE_SECONDS:
        return blocked_before_dispatch(
            "`wait.timeout_seconds` "
            f"({timeout}) must be greater than the fixed reserve "
            f"WAIT_RESERVE_SECONDS ({WAIT_RESERVE_SECONDS}) (spec §2.1/PD-11): "
            "refusing to dispatch without a usable bound -- no session is "
            "created, no bytes are transported and no receipt is fabricated "
            "(reconcile the execution configuration before repeating)")

    # 006-001 §2.2: `mode: server` (declared or by compatibility) without a
    # valid URL selects NO execution mode -- blocked before any invocation,
    # never a silent fallback (INV-2).
    if mode_effective == "none":
        return blocked_before_dispatch(
            "`mode: server` was requested without a valid `server` URL "
            "(http/https, with host, no userinfo -- spec §2.2): refusing to "
            "select an execution mode (no fallback to standalone, INV-2)")

    # 006-001 §2.5 (D-3): the effective grace and the internal budget. The
    # grace is bounded by the reserve-relative fraction and the budget takes
    # it out, so the ordered termination of the client's group ALSO fits
    # inside the interface's own bound (PD-11).
    grace = min(terminate_grace_seconds,
                TERMINATE_GRACE_FRACTION * (timeout - WAIT_RESERVE_SECONDS))
    budget = _wait_budget(timeout, grace)
    wait_deadline = time.monotonic() + (budget or 0.0)

    # 006-001 §2.7 (PD-9/D-6): a LIVE prior attempt of the SAME packet blocks
    # BEFORE anything is invoked -- no re-dispatch, no standalone next to a
    # live writer (INV-10).
    prior = _prior_attempt_check(sessions_db, project_root, execution_id_value,
                                 args.packet_id)
    prior_check_reads_value = prior["reads"]
    if prior["blocking_session"] is not None:
        return blocked_before_dispatch(
            "a prior attempt of the same packet is still LIVE (PD-9/§2.7): the "
            f"durable session row {prior['blocking_session']!r} of a previous "
            "dispatch record exists without an idle outcome. No automatic "
            "retry is produced: reconcile or wait for the prior worker before "
            "repeating the delegation (CDAD never re-dispatches on its own and "
            "never opens a standalone next to a live writer, INV-3/INV-10)")
    if prior["unaffirmable_session"] is not None:
        # B2 (PD-9/INV-9/INV-10, mirror of §2.3b): the row of the prior attempt
        # could not be read (the store is busy with a live writer, or
        # unreadable). `unknown` is not `absent`: fail closed BEFORE dispatch.
        return blocked_before_dispatch(
            "no se puede afirmar el estado del intento previo (PD-9/INV-9): "
            f"la fila durable de la sesión {prior['unaffirmable_session']!r} "
            "de un registro de despacho previo del mismo paquete no pudo "
            "leerse (store ocupado por un escritor vivo o ilegible: no se "
            "puede afirmar si el intento previo sigue vivo). Lo no observado "
            "es `unknown`, nunca «ausente»: se bloquea ANTES del despacho en "
            "vez de arriesgar un segundo worker del mismo paquete (sin "
            "re-despacho automático, INV-3/INV-10). Reconciliá o esperá al "
            "worker previo antes de repetir la delegación.")

    preflight_timeout_configured = float(
        wait_dict.get("preflight_timeout_seconds",
                      DEFAULT_WAIT_VALUES["preflight_timeout_seconds"]))

    # 006-001 §2.3/§2.3b (PD-2/PD-13): the preflight runs in the SERVER
    # effective mode and in the SERVICE mode; `--version` is the client's OWN
    # observed fact (in the service mode, D-2: only when the service runs).
    server_for_invoke: str | None = None
    standalone_for_invoke = True
    # PD-11/§2.5 (D-ADP-1): the credential the SERVER mode resolved is injected
    # ONLY into the environment of the client process this module launches.
    # `None` in standalone/service: nothing is injected there.
    client_credential: str | None = None
    if mode_effective == "server":
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
        standalone_for_invoke = False
        client_credential = preflight.get("credential_value")
        # U6-8: a configured `binary_version` that differs from the OBSERVED
        # version is DECLARED (in the diagnosis of this attempt) and does not
        # block the dispatch.
        dispatch_note = preflight.get("note")
    elif mode_effective == "service":
        # 006-001 §2.3b (PD-13/PD-14): `service status` once, then the D-11
        # version gate; any declared `server` is ignored and never checked.
        remaining = max(0.0, wait_deadline - time.monotonic())
        preflight_timeout = min(preflight_timeout_configured, remaining)
        service = _preflight_service(binary, preflight_timeout, service_require,
                                     binary_version)
        mode_effective = service["mode_effective"]
        dispatch_flags = service["dispatch_flags"]
        service_status = service["service_status"]
        fallback = service["fallback"]
        client_version = service["client_version"]
        server_version = service["server_version"]
        if service["termination"] is not None:
            return pre_dispatch_termination(
                service["termination"], service["diagnosis"],
                client_version=client_version, server_version=server_version)
        dispatch_note = service["diagnosis"]
        standalone_for_invoke = mode_effective == "standalone"
    else:
        # D-2 (standalone): never invokes `--version` (would break the
        # call-count oracles); registers the configured `binary_version` (or
        # `unknown`) and the literal `same-binary(standalone)`.
        client_version = binary_version
        server_version = "same-binary(standalone)"

    # PD-1: the adapter CHOOSES the session id and correlates by it.
    session_id = _choose_session_id()

    # 006-005 U6-5 (D-U65-1): the PROVISIONAL I8 record is written BEFORE the
    # runtime client can produce any effect -- after the preflight, the
    # prior-attempt check and the session choice, and BEFORE the launch. It
    # carries the chosen session (so the prior-attempt check of a later dispatch
    # can see it), `model_reported: null` (the row is not observed yet) and the
    # declared `write-ahead:` mark, keeping §2.6's form with `unknown` for what
    # is not observed (O-4). A failure here is FAIL-CLOSED: the client is NEVER
    # launched (this replaces 006-001 D-5 only for this step). The registration
    # consumes part of the internal budget, so it runs BEFORE the client's
    # bound is computed: the adapter still answers inside the interface's own
    # bound (PD-11).
    write_ahead_observation = _observation(
        runtime, model, binary_version, session_id, started_at,
        mode_requested=mode_requested, mode_effective=mode_effective,
        client_version=client_version, server_version=server_version,
        session_base=(
            f"{WRITE_AHEAD_MARK} provisional: the observation is completed ONCE "
            "at termination"),
        row_state="unknown",
        dispatch_flags=dispatch_flags, service_status=service_status,
        fallback=fallback, store_reads="unknown",
        prior_check_reads=prior_check_reads_value)
    try:
        _register_dispatch(project_root, args.packet_id, request, attempt_id,
                           write_ahead_observation,
                           _continuity_attempt(args))
    except AdapterError as exc:
        return envelope(
            session=None, termination="blocked", delivery_ref=None,
            diagnosis=(
                "the write-ahead I8 record could not be written, so the "
                "dispatch is blocked and the runtime client was NOT launched "
                "(D-U65-1 fail-closed): "
                f"{str(exc)[:300]}"))

    # §2.5 (D-3, PD-11): the client dispatch gets whatever the preflight left
    # of the budget, but NEVER less than its declared share: a slow preflight
    # must not kill a healthy client at a near-zero bound and report a FALSE
    # `timeout`. The floor is CAPPED (review B1) so the adapter ALWAYS answers
    # with its own envelope inside the interface's bound: the consumed time is
    # already reflected in `remaining`, so the admissible ceiling is `remaining`
    # plus whatever reserve slack the effective grace and the completion margin
    # leave free (clamped at zero -- a large grace consumes the whole reserve).
    # Without the cap a proportional floor could push the answer past the cota
    # and let the INTERFACE kill the adapter, emitting its own envelope with
    # `session: null` (the very result PD-11/PD-8 forbid).
    client_floor = (budget or 0.0) * CLIENT_MIN_BUDGET_SHARE
    remaining = max(0.0, wait_deadline - time.monotonic())
    floor_ceiling = remaining + max(
        0.0, WAIT_RESERVE_SECONDS - grace - COMPLETION_MARGIN_SECONDS)
    remaining_for_invoke = max(remaining, min(client_floor, floor_ceiling))

    # PD-5/D6: invoke the configured binary (with `--session <id>`), then wait
    # on the DURABLE signal. The invocation is bounded by the remaining
    # budget, so a destination that never returns can never make the
    # interface the one that kills this adapter (the adapter always answers
    # within the bound it received). PD-8: the client runs in its OWN process
    # group and, when the bound expires, the WHOLE group is terminated in an
    # ordered way (SIGTERM, the effective grace, SIGKILL).
    try:
        proc = _invoke_destination(binary, agent, model,
                                   packet_bytes, project_root,
                                   remaining_for_invoke, session_id,
                                   server=server_for_invoke, auto=auto,
                                   standalone=standalone_for_invoke,
                                   grace=grace,
                                   credential_env=client_credential)
    except DestinationTimeoutError as exc:
        # R1: the material fact is absence-of-signal within the bound ->
        # `timeout`, never `transport-error` with a fabricated rc. PD-8: the
        # client WAS started, so the envelope carries the chosen session.
        diagnosis = str(exc)
        if mode_effective in ("server", "service"):
            diagnosis += (
                f"; the role worker may still be running in the "
                f"{mode_effective} (CDAD terminated ONLY its own client's "
                "process group and never touches the server or the background "
                "service)")
        note = register_note(session=session_id, session_base="chosen by adapter",
                             row_state="unknown", client_version=client_version,
                             server_version=server_version)
        return envelope(session=session_id, termination="timeout",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))
    except AdapterError as exc:
        # R1 (contracara): a binary that could not be STARTED is a real
        # transport failure (PD-5): no process was started, so the session
        # stays `null` (PD-8).
        note = register_note(session=None, session_base="chosen by adapter",
                             row_state="absent", client_version=client_version,
                             server_version=server_version)
        return envelope(session=None, termination="transport-error",
                         delivery_ref=None,
                         diagnosis=_append_note(str(exc), note))

    # PD-7/PD-10: the proportional wait only starts AFTER the client exits
    # (zero reads while it lives) and classifies from the material facts.
    exit_ts = time.monotonic()
    try:
        outcome = _await_durable_outcome(
            sessions_db, session_id, proc.returncode, deadline=wait_deadline,
            settle_seconds=settle_seconds, mode_effective=mode_effective,
            exit_ts=exit_ts, poll_initial=poll_initial, poll_max=poll_max)
    except AdapterError as exc:
        # PD-2: a missing/unreadable/unknown-schema store is a KNOWN fact and
        # fails closed with a diagnosis, without exhausting the wait. PD-8:
        # the client WAS started, so the chosen session travels.
        note = register_note(session=session_id, session_base="chosen by adapter",
                             row_state="unknown", client_version=client_version,
                             server_version=server_version)
        return envelope(session=session_id, termination="blocked",
                         delivery_ref=None,
                         diagnosis=_append_note(str(exc), note))
    store_reads_value = str(outcome["reads"])

    kind = outcome["kind"]
    if kind == "transport-error":
        stderr = _redact_server_url(
            proc.stderr.decode("utf-8", errors="replace").strip(),
            server_for_invoke)
        diagnosis = (
            f"the destination client failed in transport (rc="
            f"{proc.returncode}) before any durable session row: "
            f"{stderr[:300] or 'no diagnostic'}")
        note = register_note(session=session_id, session_base="chosen by adapter",
                             row_state="absent", client_version=client_version,
                             server_version=server_version)
        return envelope(session=session_id, termination="transport-error",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))
    if kind == "timeout":
        diagnosis = (
            "no durable session row with an idle outcome for the chosen "
            f"session {session_id!r} within the bounded wait "
            f"({timeout if timeout is not None else 'configured'} seconds); "
            "the client rc does not prove the role finished and no receipt "
            "is fabricated (reconcile before repeating)")
        if mode_effective in ("server", "service"):
            diagnosis += (
                f"; the role worker may still be running in the "
                f"{mode_effective}: CDAD does NOT open a standalone next to it "
                "and never touches the server or the background service "
                "(INV-10)")
        note = register_note(session=session_id, session_base="chosen by adapter",
                             row_state=("present" if outcome["row_present"]
                                        else "absent"),
                             client_version=client_version,
                             server_version=server_version)
        return envelope(session=session_id, termination="timeout",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))
    if kind == "unknown":
        # §2.4/PD-7: `settle_seconds` elapsed without a durable idle outcome.
        diagnosis = (
            "no durable idle outcome for the chosen session "
            f"{session_id!r} after the settlement window "
            f"({settle_seconds} seconds since the client exited, rc="
            f"{proc.returncode}): the store carries no material end-of-run "
            "fact and no receipt is fabricated (reconcile before repeating)")
        note = register_note(session=session_id, session_base="chosen by adapter",
                             row_state=("present" if outcome["row_present"]
                                        else "absent"),
                             client_version=client_version,
                             server_version=server_version)
        return envelope(session=session_id, termination="unknown",
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    row = outcome["row"]
    durable_session_base = (
        "durable session row (exec-config: sessions_db): session_v2.id")
    # PD-3/PD-5 (§2.5, INV-15): the durable row's `agent` is corroborated
    # against the AGENT OF THE PACKET. A contradiction is a REJECTION that names
    # the key; a key that is not evaluable (the packet declares no `agent`, or
    # the row exposes no column) resolves to `unknown` -- never `cdad-<rol>` and
    # never a delivery accepted on it. There is no parent to compare and no
    # `directory == root` equality here (§2.3).
    identity_verdict, identity_diagnosis = _durable_identity_verdict(
        row, _as_text(request.get("agent")))
    if identity_verdict != "match":
        identity_termination = ("blocked"
                                if identity_verdict == "contradiction"
                                else "unknown")
        note = register_note(session=_as_text(row.get("id")),
                             session_base=durable_session_base,
                             row_state="present", client_version=client_version,
                             server_version=server_version)
        return envelope(session=_as_text(row.get("id")),
                         termination=identity_termination,
                         delivery_ref=None,
                         diagnosis=_append_note(
                             _append_note(identity_diagnosis, agent_note), note))

    termination, session, final_text, diagnosis = _classify(
        row, outcome["final_text"], outcome.get("idle_error"))
    if termination != "completed":
        note = register_note(session=session, session_base=durable_session_base,
                             row_state="present", client_version=client_version,
                             server_version=server_version)
        return envelope(session=session, termination=termination,
                         delivery_ref=None,
                         diagnosis=_append_note(diagnosis, note))

    try:
        delivery_ref = _persist_delivery(
            project_root, args.packet_id, request, attempt_id, session, runtime,
            model, binary_version, started_at, final_text,
            mode_requested=mode_requested, mode_effective=mode_effective,
            client_version=client_version, server_version=server_version,
            dispatch_flags=dispatch_flags, service_status=service_status,
            fallback=fallback,
            model_reported=_model_reported_from_row(row.get("model")),
            store_reads=store_reads_value,
            prior_check_reads=prior_check_reads_value,
            continuity_attempt=_continuity_attempt(args))
    except (AdapterError, cdad_result.ResultError) as exc:
        return envelope(
            session=session, termination="blocked", delivery_ref=None,
            diagnosis=(
                f"the role completed but the durable delivery could not be "
                f"persisted through receive: {exc}"))
    return envelope(session=session, termination="completed",
                     delivery_ref=delivery_ref, diagnosis=dispatch_note)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # 006-005 §2.2: the declared surfaces of the integration answer on their own
    # (they are not the dispatch errand and never emit an envelope).
    if args.capabilities:
        return _run_capabilities(args)
    if args.observe:
        return _run_observe(args)
    try:
        output = delegate(args)
    except AdapterError as exc:
        output = _envelope(session=None, termination="blocked",
                           delivery_ref=None, diagnosis=str(exc))
    sys.stdout.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
