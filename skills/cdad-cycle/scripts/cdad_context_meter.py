#!/usr/bin/env python3
"""cdad_context_meter — neutral context-measurement record emitter (005-002 T1).

This is the canonical adapter. It reads a runtime session store in READ-ONLY
mode and emits a runtime-agnostic measurement record on stdout:

    context-meter-v1 (schema: assets/context-meter.schema.json)

Design rules (spec docs/specs/005-002-session-context-meter/spec.md):

- The record is the CONTRACT; this adapter only translates. The record carries
  NO runtime table/column names (neutrality, PD-1/INV-3). Only this adapter
  knows the source names.
- Buckets are explicit and never mixed: every metric lives in EXACTLY ONE of
  `observed` / `estimated` / `unknown` (PD-1/PD-16).
- A null/absent/not-reported value is `unknown` with a cause, NEVER `0`
  (PD-4). In particular `cache.write` — which the configured provider does not
  report — is `unknown`, never `0`.
- No bytes-to-tokens conversion and no fabricated context/limit (PD-3/INV-2).
- Read-only, bounded, stdlib only, JSON as the ONLY output mode, deterministic
  (PD-11/INV-6).
- Fail closed on an unrecognized schema: rc != 0, a diagnostic on stderr that
  NAMES the missing element, and NO metric number on stdout (PD-2). The source
  has no schema marker, so recognition is by required columns + row shapes.

Invocation surface (PD-15, observable contract):

    cdad_context_meter --store PATH [--session REF]... [--limit N]
                       [--idle-threshold MINUTES] [--steps]
                       [--set-summary [--detail]] [--delegation-dispatch]
                       [--json]

- `--store` or the environment variable `CDAD_CONTEXT_METER_STORE`; with
  NEITHER, it fails closed naming the missing input. No hardcoded path.
- `--session REF` is repeatable; `--limit N` bounds the selection when no
  `--session` is given (default 20; `--limit 0` fails closed).
- `--idle-threshold` (default 60 minutes) is the stretch-cut threshold.
- `--steps` (boolean, no value) restores the FULL ordered per-step detail of
  `input_per_step` (one element per step of the stretch; `null` for a step
  whose proxy is not observable). Without it the measure carries a FIXED-SIZE
  summary and the published 16384-byte limit holds for any session size
  (PD-12/D2).
- `--set-summary` (boolean, no value) emits the multi-session SET SUMMARY as a
  SEPARATE ADDITIVE document (`set-summary-v1`) instead of the neutral
  per-session record: sessions included (hashed), declared coverage, milestones,
  magnitudes with bucket and coverage, and references to the per-session detail.
  Without it the neutral record is emitted byte-identical to before (INV-5).
  `--detail` restores the per-session detail (the flag the summary declares in
  `detail_flag`); the detail is never emitted by default.
- `--delegation-dispatch` (boolean, no value, 005-007 PD-9) adds the common
  delegation interface to the recognized dispatch set: a `shell` call that
  REALLY invokes `cdad_delegate.py` is a role work dispatch, by the same class
  of material evidence as the `resume` rule (a mere MENTION of the program and
  a help call do NOT count). The record then declares the recognized set with
  the METHOD and PROVENANCE of each entry. WITHOUT the flag the neutral record
  is byte-identical to before (INV-5) and only the tool names are recognized.
- JSON on stdout; `--json` is an accepted no-op.

Measurement (PD-5..PD-8):

- The window is the FIRST contiguous stretch of the session, cut at the first
  inactivity gap greater than `--idle-threshold` (default 60 minutes). The
  stretch closes at the LAST message before the gap — the assistant message
  that closes it, which may carry no tool call of its own. Without a gap over
  the threshold the whole session is a single stretch. Metrics are reported
  PER STRETCH; whole-session figures are reported separately, never averaged.
- Two separate milestones: the first real `resume` (a shell call invoking the
  continuity CLI's `resume` subcommand, excluding help) and the first role
  work dispatch (a recognized dispatch tool that opens a worker session, e.g.
  `subagent` or `task`; the recognized set is DECLARED in
  `reader.dispatch_tools` and a dispatch by an unrecognized tool is NOT
  detected — the absence cause names the set and the limit, D4). Each is
  `observed` (position, and time when observable) or `absent`/`unknown` with a
  cause — never invented, never a zero. A milestone whose POSITION is
  observable but whose TIME is not stays `observed` with `time_relative: null`
  and a cause (D1).
- With `--delegation-dispatch` (005-007 PD-9) the recognized dispatch set also
  includes a `shell` call that REALLY invokes the common delegation interface
  (`cdad_delegate.py` with its delegation arguments) — the same class of
  material evidence as the `resume` rule below. A call that merely MENTIONS the
  program (the content of a `write`, the argument of a `grep`) and a HELP call
  (`--help`/`-h`) are NOT a dispatch, and the absence cause names the honest
  limit. The record declares the recognized set with the METHOD and PROVENANCE
  of each entry in `reader.dispatch_recognition`, and an observed milestone
  carries the METHOD of its entry. A dispatch is an EVENT: never proof of
  utility nor of an accepted result (PD-6 of 005-002).
- Orientation measures: previous calls/reads before the milestone, their
  per-tool breakdown, whole-session reads (labelled apart), outputs in Unicode
  characters, per-step input proxy (estimated: input + cache.read +
  cache.write, NOT the real window), accumulated (observed) and cost. An
  aggregate that SUMS a per-step component (`accumulated`, `cache.read`,
  `cost`) is a COMPLETE observation only if ALL steps of the stretch report it;
  otherwise it is `unknown` (never a partial subtotal presented as observed)
  with ONE aggregated cause naming the coverage. `total_output`/`max_output`
  are `unknown` (never 0) when the stretch carries no output text.

Application annotation (PD-9, optional):

- An OPTIONAL `application` field may carry a REFERENCED annotation. `ref` is a
  durable reference (path/commit/receipt) transported AS PASSED — never a copy
  of the referenced content. `limit` is declared by the caller and transported
  verbatim; the reader NEVER judges and NEVER approves anything (no approval
  marker, and `rc` does not change with the limit). Without the annotation
  input the field is absent, or it is `unknown` with a cause: the reader does
  not invent it.
- When a document combines a coordinator and its workers it DECLARES which
  sessions are included (`included_sessions`) and which relations were observed
  (`relations`, referencing each child's `parent_ref`). A `parent_id` pointing
  to a session that is NOT in the store is reported as an UNKNOWN relation in
  `unknowns[]` with a cause: the parent session is neither invented nor
  completed. The per-role aggregate sums each included session's own cost ONCE,
  never twice. Each SUMMED component of `roles[].sums` DECLARES its coverage
  (R1): a complete observation (`observed`, numeric value) only when EVERY
  session of the role reports it; otherwise `unknown` with value null — a
  partial subtotal is NEVER presented as the role total — and ONE aggregated
  cause per (role, component) declares the coverage. The same class covers
  `roles[].distributions`.

Pure Python stdlib. No service, no permanent agent, no LLM controller.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import sqlite3
import sys
from pathlib import Path
from typing import Any

METER_CONTRACT = "context-meter-v1"
SCHEMA_VERSION = 1

# Multi-session SET SUMMARY (005-003 T3): a SEPARATE ADDITIVE document
# (`set-summary-v1`) emitted with `--set-summary` for a multi-session run. It
# does NOT rewrite the neutral per-session record (INV-5): without the flag the
# output is byte-identical to before. The per-session detail is NOT emitted by
# default; it is restored with the flag declared in the summary's `detail_flag`.
SET_SUMMARY_CONTRACT = "set-summary-v1"
SET_DETAIL_FLAG = "--detail"

# The store comes from a flag or a declared environment variable — never a
# hardcoded path (PD-15(a)).
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"
DEFAULT_LIMIT = 20
DEFAULT_IDLE_THRESHOLD_MINUTES = 60

# Runtime source shape (schema detection, PD-2). The source has NO
# `schema_version` marker: recognition is by required columns + row shapes.
SESSION_TABLE = "session_v2"
MESSAGE_TABLE = "session_message"
REQUIRED_SESSION_COLUMNS = (
    "id", "agent", "model", "parent_id", "version",
    "time_created", "time_updated")
REQUIRED_MESSAGE_COLUMNS = ("session_id", "type", "seq", "data")

# Message/part types the adapter recognizes. Unknown types are opaque: they
# contribute no metric and never fabricate a number.
ASSISTANT_TYPE = "assistant"
TOOL_TYPE = "tool"

# Role work dispatch: the tools that open a worker session (PD-6/D5, D4). The
# recognized set is DECLARED in the record (`reader.dispatch_tools`) so the
# consumer knows the limit: a dispatch made with a tool outside the set is NOT
# detected by this reader (its cause names the set and the limit).
DISPATCH_TOOL_NAMES = frozenset({"subagent", "task"})

# Common delegation interface (005-007 PD-9). A `shell` call that REALLY
# invokes the delegation program is a role work dispatch, by the same class of
# material evidence as the `resume` rule (the tool call itself, never a
# mention). The detection is activated by the flag `--delegation-dispatch`:
# WITHOUT it the neutral record stays byte-identical (INV-5) and only the tool
# names above are recognized.
DELEGATION_DISPATCH_FLAG = "--delegation-dispatch"
DELEGATION_PROGRAM = "cdad_delegate.py"
DELEGATION_ENTRY = DELEGATION_PROGRAM
_DELEGATION_INTERPRETERS = frozenset({"python", "python2", "python3", "py"})
_HELP_FLAGS = ("--help", "-h")
_SHELL_SEPARATORS = ("&&", "||", ";;", ";", "|", "&", "\n")

# 005-007 review B2 (PD-9). A REAL invocation of the delegation program may be
# WRAPPED in a known prefix that is not the invoked program itself — the class
# of invocation that dominates the repo's real practice (`nohup bash -c "..."`).
# The resolver peels these wrappers (and a shell interpreter's `-c` argument,
# one pass) so a wrapped invocation is still recognized by the material fact:
# the program the shell segment REALLY runs.
_DELEGATION_WRAPPERS = frozenset({
    "time", "env", "nohup", "nice", "ionice", "stdbuf", "command",
    "timeout", "sudo",
})
# Wrapper flags that CONSUME the next token as their argument, so it is not
# mistaken for the program. `timeout`'s bare duration operand is handled apart.
_WRAPPER_ARGUMENT_FLAGS = {
    "nice": frozenset({"-n", "--adjustment"}),
    "ionice": frozenset({"-c", "-n", "--class", "--classdata"}),
    "stdbuf": frozenset({"-i", "-o", "-e", "--input", "--output", "--error"}),
    "timeout": frozenset({"-s", "-k", "--signal", "--kill-after"}),
    "sudo": frozenset({"-u", "-g", "-p", "-C", "-U", "-T",
                       "--user", "--group", "--prompt", "--chdir"}),
    "env": frozenset({"-u", "--unset", "-S", "--split-string",
                      "-C", "--chdir"}),
}
# Shell interpreters whose `-c "<command>"` argument carries the REAL command.
_SHELL_INTERPRETERS = frozenset({"sh", "bash", "dash", "zsh", "ksh"})

# METHOD and PROVENANCE declared per recognized entry (PD-9): the record states
# HOW each entry is recognized and WHERE the rule comes from. Two classes of
# evidence: the tool NAME of the call vs. the MATERIAL FACT that a shell call
# invokes the delegation program.
DISPATCH_TOOL_METHOD = "recognized dispatch tool name"
DISPATCH_TOOL_PROVENANCE = (
    "declared recognized dispatch tool names (005-002 PD-6/D5: the tool name "
    "of the call opens a worker session); 005-007 PD-9 extends the set without "
    "changing this class of evidence")
DELEGATION_DISPATCH_METHOD = (
    "material fact: the shell call invokes the program (unwrapping known "
    "prefixes: time/env/nohup/nice/ionice/stdbuf/command/timeout/sudo and a "
    "shell interpreter's -c argument)")
DELEGATION_DISPATCH_PROVENANCE = (
    "005-007 PD-9: the shell tool call REALLY invokes the delegation program "
    "'cdad_delegate.py' (with its delegation arguments), even when it is "
    "wrapped in a known prefix (time/env/nohup/nice/ionice/stdbuf/command/"
    "timeout/sudo, or a shell interpreter's -c argument) — same class of "
    "evidence as the resume rule (005-002 PD-6, cdad_context_meter.py); a mere "
    "mention of the program and a help call (--help/-h) are excluded")

# The cut criterion actually used (PD-5), declared verbatim in the record. The
# alternative edge (last message WITH a tool call) is NOT used.
CUT_CRITERION = (
    "first contiguous stretch: cut at the first inactivity gap greater than "
    "the idle threshold; the stretch closes at the last message before the "
    "gap (the assistant message that closes it, which may carry no tool call "
    "of its own); metrics are per stretch and whole-session figures are "
    "reported separately, never averaged")

# Bucket names and the declared assignment rule (PD-1/PD-16). The rule is
# declared in the schema asset; here it is applied:
#   observed  = read directly from the record (reported tokens, counts,
#               positions, times, output size)
#   estimated = declared proxy (never the real context window)
#   unknown   = null/absent/not-reported WITH a cause, never 0
BUCKET_OBSERVED = "observed"
BUCKET_ESTIMATED = "estimated"
BUCKET_UNKNOWN = "unknown"

# Causes for a milestone that did not occur in the evaluated trace (PD-6).
# The dispatch cause DISTINGUISHES "it did not happen" from "it was not
# recognized": it names the recognized set and declares the limit (D4).
_ABSENT_RESUME_CAUSE = (
    "no shell call in the first stretch invokes the resume subcommand of the "
    "continuity CLI (help calls such as --help are excluded)")
_ABSENT_DISPATCH_CAUSE = (
    "no role work dispatch tool call in the first stretch: this reader "
    "recognizes only the dispatch tools 'subagent' and 'task'; a dispatch made "
    "with any other tool is not detected by this reader, so the absence is "
    "unknown, never invented")
# With `--delegation-dispatch` the recognized set grows (005-007 PD-9) and the
# absence cause names, per trace, the HONEST limit: only a real invocation of
# the program counts (a mention does not; a help call is excluded). Every cause
# keeps the honest limit of PD-6 of 005-002: a dispatch is an EVENT, never proof
# of utility nor of an accepted result.
_ABSENT_DISPATCH_CAUSE_DELEGATION = (
    "no role work dispatch in the first stretch: with "
    f"`{DELEGATION_DISPATCH_FLAG}` this reader recognizes the dispatch tool "
    "names 'subagent'/'task' and a shell call that REALLY invokes the "
    f"delegation program '{DELEGATION_PROGRAM}'; a dispatch made with any "
    "other means is not detected by this reader, so the absence is unknown, "
    "never invented; a dispatch is an event, never proof of utility nor of an "
    "accepted result")
_ABSENT_DISPATCH_CAUSE_MENTION = (
    "no role work dispatch in the first stretch: a call whose content or "
    f"arguments only MENTION the delegation program '{DELEGATION_PROGRAM}' "
    "(the content of a `write`, the argument of a `grep`) is not a dispatch — "
    "only a shell call that really invokes the program counts, so the reader "
    "never infers a dispatch from text; a dispatch is an event, never proof of "
    "utility nor of an accepted result")
_ABSENT_DISPATCH_CAUSE_HELP = (
    "no role work dispatch in the first stretch: the only calls that invoke "
    f"the delegation program '{DELEGATION_PROGRAM}' are HELP calls "
    "(--help/-h), which are excluded (a help call dispatches no work) — only a "
    "real invocation of the program counts; a dispatch is an event, never "
    "proof of utility nor of an accepted result")
_NO_TRACE_CAUSE = "the session trace has no messages to evaluate"

# Causes for "unknown is not zero" (D1/PD-4): a magnitude that cannot be
# observed is `unknown` WITH a cause, never a fabricated `0` or a partial sum
# presented as a complete observation.
_OUTPUT_ABSENT_CAUSE = (
    "the stretch carries no tool call with output text: the output size "
    "(total_output/max_output) is unknown, never 0 (there is no evidence of "
    "output)")
_NO_STEPS_CAUSE = (
    "the stretch has no assistant step to observe: the measure is unknown, "
    "never 0")
_NO_TOKEN_DATA_CAUSE = (
    "the session reports no token data: token measures are unknown, never 0")

# Output size (PD-12/D2). The reference publishes a NORMATIVE limit of 16384
# bytes per single-session document; the DEFAULT document honors it by carrying
# a FIXED-SIZE summary of the per-step proxy instead of the full per-step
# detail. The full ordered detail is emitted ONLY when the caller explicitly
# asks for it with `--steps` (the published limit does not apply then: the
# detail was requested). The indicator and its cause travel in the measure's
# `truncated` key so the omission is never silent.
DETAIL_FLAG = "--steps"
PUBLISHED_BYTE_LIMIT = 16_384
_SUMMARY_PROVENANCE = (
    "fixed-size default summary of the declared per-step context proxy "
    "(reported input + cache.read + cache.write of each step, NOT the real "
    "context window): count of the stretch's steps, last/previous step proxy, "
    "min/max over the OBSERVABLE proxies and unobserved (steps whose proxy is "
    "not observable, never 0); the full ordered per-step detail is emitted "
    f"only with `{DETAIL_FLAG}` (see `truncated`)")
_DETAIL_PROVENANCE = (
    "declared proxy per step of the stretch: reported input + cache.read + "
    "cache.write (NOT the real context window); a null element means the proxy "
    "is not observable for that step (a missing component), never 0")
_TRUNCATED_CAUSE = (
    f"the per-step detail is omitted from the default document so that one "
    f"session's document stays at or below the published limit of "
    f"{PUBLISHED_BYTE_LIMIT} bytes (16 KiB) per single-session document; pass "
    f"`{DETAIL_FLAG}` to obtain the full ordered per-step detail and its count "
    "of omitted steps")
_DETAIL_CAUSE = (
    f"the full ordered per-step detail is emitted: the published limit of "
    f"{PUBLISHED_BYTE_LIMIT} bytes per single-session document does not apply "
    f"when the detail is requested with `{DETAIL_FLAG}` (no steps are omitted)")


def _milestone_time_cause(which: str) -> str:
    """Cause for a milestone whose POSITION is observable but whose TIME is
    not: the time is `unknown` (null), never a fabricated `0.0` (D1)."""
    return (
        f"the {which} milestone position is observable (its call_index/seq are "
        "referenced) but its time is not numeric in the record: the relative "
        "time is unknown, never 0")


# Application annotation (PD-9). The limit is a DECLARED input transported
# verbatim; the reader never judges and never approves. The set is fixed by the
# spec.
APPLICATION_LIMIT_VALUES = ("accepted", "blocked", "pending", "unknown")
APPLICATION_UNKNOWN_LIMIT = "unknown"
_APPLICATION_ABSENT_CAUSE = (
    "no application reference was provided: the limit is unknown and the "
    "reader does not invent it")
_DANGLING_PARENT_CAUSE = (
    "parent relation not verifiable: the referenced parent session is not "
    "present in the store (unknown; the parent is not invented and no datum "
    "is completed)")


class MeterError(Exception):
    """A designed, deterministic fail-closed condition: rc != 0, a diagnostic
    on stderr naming the missing element, and no metric number on stdout."""


# ------------------------------------------------------------------ helpers


def _hash_ref(value: Any) -> str | None:
    """Privacy (PD-10): identifiers are hashed, never emitted raw."""
    if not isinstance(value, str) or not value.strip():
        return None
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:32]}"


def _parse_model(raw: Any) -> str:
    """The session model is a JSON string; parse it, else keep the raw string,
    else `unknown` (spec §2)."""
    if not isinstance(raw, str) or not raw.strip():
        return "unknown"
    text = raw.strip()
    try:
        document = json.loads(text)
    except ValueError:
        return text
    if isinstance(document, dict):
        model_id = document.get("id")
        if isinstance(model_id, str) and model_id.strip():
            return model_id
    return text


def _parse_data(raw: Any) -> dict | None:
    if not isinstance(raw, str):
        return None
    try:
        document = json.loads(raw)
    except ValueError:
        return None
    return document if isinstance(document, dict) else None


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _measure(value: Any, unit: str, provenance: str, bucket: str) -> dict:
    return {
        "value": value,
        "unit": unit,
        "provenance": provenance,
        "bucket": bucket,
    }


def _measure_leaves(node: Any, prefix: str = ""):
    """Yield (name, leaf) for every metric leaf: a dict carrying the four
    metric fields, at any declared nesting depth (e.g. `cache.read`)."""
    if isinstance(node, dict):
        if all(field in node
               for field in ("value", "unit", "provenance", "bucket")):
            yield prefix, node
            return
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else key
            yield from _measure_leaves(value, path)


def _bucket_index(measures: dict) -> dict:
    """Group metric names by their declared bucket — one metric, one bucket."""
    index = {BUCKET_OBSERVED: [], BUCKET_ESTIMATED: [], BUCKET_UNKNOWN: []}
    for name, leaf in _measure_leaves(measures):
        index[leaf["bucket"]].append(name)
    for names in index.values():
        names.sort()
    return index


# ------------------------------------------------------------------ store


def _resolve_store(args: argparse.Namespace) -> Path:
    """Flag → environment variable → fail closed naming the missing input."""
    raw = args.store if args.store else os.environ.get(STORE_ENV_VAR)
    if not raw or not str(raw).strip():
        raise MeterError(
            "no session store given: pass --store PATH or set the "
            f"environment variable {STORE_ENV_VAR} (fail closed)")
    path = Path(str(raw))
    if not path.is_file():
        raise MeterError(f"session store not found: {path}")
    return path


def _connect_ro(path: Path) -> sqlite3.Connection:
    """READ-ONLY open (PD-11/INV-1): `?mode=ro`, no checkpoint, no writes."""
    uri = f"file:{path}?mode=ro"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise MeterError(
            f"cannot open the session store read-only: {exc}") from exc


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,)).fetchone()
    return row is not None


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def _require_column(conn: sqlite3.Connection, table: str, column: str) -> None:
    if column not in _table_columns(conn, table):
        raise MeterError(
            f"missing required column {column!r} of table {table!r} "
            "(unrecognized schema: fail closed, no metric emitted)")


def _require_schema(conn: sqlite3.Connection) -> None:
    """Fail closed by required table/column presence (PD-2). No version marker
    is trusted (the source has none)."""
    if not _table_exists(conn, SESSION_TABLE):
        raise MeterError(
            f"missing required table {SESSION_TABLE!r} (unrecognized schema: "
            "fail closed, no metric emitted)")
    for column in REQUIRED_SESSION_COLUMNS:
        _require_column(conn, SESSION_TABLE, column)
    if not _table_exists(conn, MESSAGE_TABLE):
        raise MeterError(
            f"missing required table {MESSAGE_TABLE!r} (unrecognized schema: "
            "fail closed, no metric emitted)")
    for column in REQUIRED_MESSAGE_COLUMNS:
        _require_column(conn, MESSAGE_TABLE, column)


def _load_session_rows(conn: sqlite3.Connection, refs: list[str] | None,
                       limit: int) -> list[tuple]:
    columns = ("id, agent, model, parent_id, version, time_created, "
               "time_updated")
    if refs:
        placeholders = ", ".join("?" for _ in refs)
        query = (f"SELECT {columns} FROM {SESSION_TABLE} WHERE id IN "
                 f"({placeholders}) ORDER BY id")
        return conn.execute(query, tuple(refs)).fetchall()
    query = (f"SELECT {columns} FROM {SESSION_TABLE} ORDER BY id LIMIT ?")
    return conn.execute(query, (limit,)).fetchall()


def _present_session_ids(conn: sqlite3.Connection,
                         ids: list[str]) -> set[str]:
    """The subset of `ids` that exists in the store. Bounded to the parent
    references of the measured sessions — never an unbounded sweep."""
    wanted = [i for i in ids if isinstance(i, str) and i.strip()]
    if not wanted:
        return set()
    placeholders = ", ".join("?" for _ in wanted)
    query = (f"SELECT id FROM {SESSION_TABLE} WHERE id IN ({placeholders})")
    return {row[0] for row in conn.execute(query, tuple(wanted)).fetchall()}


def _load_messages(conn: sqlite3.Connection, session_id: str) -> list[dict]:
    """Load a session's messages in seq order with their parsed data and
    bounds. Nothing is fabricated: a quantity that cannot be observed stays
    `None`."""
    query = (f"SELECT seq, type, data, time_created, time_updated FROM "
             f"{MESSAGE_TABLE} WHERE session_id = ? ORDER BY seq")
    messages: list[dict] = []
    for seq, mtype, data_raw, t_created, t_updated in conn.execute(
            query, (session_id,)).fetchall():
        messages.append({
            "seq": seq,
            "type": mtype,
            "data": _parse_data(data_raw) or {},
            "t_created": t_created if isinstance(t_created, (int, float))
            and not isinstance(t_created, bool) else None,
            "t_updated": t_updated if isinstance(t_updated, (int, float))
            and not isinstance(t_updated, bool) else None,
        })
    return messages


# ------------------------------------------------------------------ metrics


def _tool_output_lengths(part: dict) -> list[int]:
    """Output size = sum of len(text) over `state.content[]` text chunks
    (spec §6). Never converted to tokens or bytes."""
    state = part.get("state")
    if not isinstance(state, dict):
        return []
    content = state.get("content")
    if not isinstance(content, list):
        return []
    lengths: list[int] = []
    for chunk in content:
        if isinstance(chunk, dict) and chunk.get("type") == "text":
            text = chunk.get("text")
            if isinstance(text, str):
                lengths.append(len(text))
    return lengths


def _all_tool_calls(messages: list[dict]) -> list[dict]:
    """Every tool call of the session, in order: `call_index` is the 1-based
    ordinal of the tool part among assistant messages ordered by seq."""
    calls: list[dict] = []
    index = 0
    for msg_index, msg in enumerate(messages):
        if msg["type"] != ASSISTANT_TYPE:
            continue
        content = msg["data"].get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not (isinstance(part, dict) and part.get("type") == TOOL_TYPE):
                continue
            index += 1
            state = part.get("state")
            state = state if isinstance(state, dict) else {}
            calls.append({
                "call_index": index,
                "msg_index": msg_index,
                "seq": msg["seq"],
                "time": msg["t_created"],
                "name": part.get("name"),
                "input": state.get("input"),
                "output_lengths": _tool_output_lengths(part),
            })
    return calls


def _first_stretch(messages: list[dict], threshold_minutes: float):
    """Bounds of the FIRST contiguous stretch (PD-5): it starts at the first
    message and closes at the last message before the first inactivity gap
    greater than `threshold_minutes`. Inactivity between two consecutive
    messages = start of the next minus `time_updated` of the previous. Without
    a gap over the threshold, the whole session is one stretch."""
    if not messages:
        return None
    threshold_ms = threshold_minutes * 60_000.0
    end = len(messages) - 1
    for index in range(len(messages) - 1):
        start_next = messages[index + 1]["t_created"]
        end_previous = messages[index]["t_updated"]
        if start_next is None or end_previous is None:
            continue
        if start_next - end_previous > threshold_ms:
            end = index
            break
    return (0, end)


def _collect(messages: list[dict], stretch) -> dict:
    """Read the observable quantities of the first stretch and of the whole
    session. Nothing is fabricated: a quantity that cannot be observed stays
    `None`."""
    if stretch is None:
        start, end = 0, -1
    else:
        start, end = stretch
    calls = _all_tool_calls(messages)
    stretch_calls = [c for c in calls if start <= c["msg_index"] <= end]
    steps = [m for m in messages[start:end + 1]
             if m["type"] == ASSISTANT_TYPE]
    saw_tokens = any(isinstance(step["data"].get("tokens"), dict)
                     for step in steps)
    return {
        "has_trace": bool(messages),
        "start_time": messages[start]["t_created"] if messages else None,
        "end_time": messages[end]["t_updated"] if messages else None,
        "start_seq": messages[start]["seq"] if messages else None,
        "end_seq": messages[end]["seq"] if messages else None,
        "stretch_calls": stretch_calls,
        "session_calls": calls,
        "steps": steps,
        "session_reads": sum(1 for c in calls if c["name"] == "read"),
        "saw_tokens": saw_tokens,
    }


def _coverage_cause(component: str, reporting: int, total: int) -> str:
    """ONE AGGREGATED cause for an aggregate measure that SUMS a component over
    the steps of the stretch (D1). The sum is a COMPLETE observation only if
    ALL steps report the component (a reported 0 counts as reported); with at
    least one step that does NOT report it, the sum is a partial subtotal and
    the measure is `unknown` — never a partial sum presented as observed. One
    entry PER MEASURE, never one per step."""
    missing = total - reporting
    return (
        f"the stretch reports {component} in {reporting} of {total} messages: "
        f"{missing} messages do not report it, so the sum is not a complete "
        "observation of the stretch (unknown, never a partial sum presented as "
        "observed); no partial sum is emitted")


def _proxy_summary(step_proxies: list[Any], n_steps: int) -> dict:
    """FIXED-SIZE summary of the per-step proxy (PD-12/D2): its shape does not
    grow with the number of steps, so the default document stays bounded at any
    session size. A proxy that is not observable is `null` (in `last`,
    `previous`, `min`, `max`) and counted in `unobserved` — NEVER 0."""
    observable = [p for p in step_proxies if p is not None]
    return {
        "count": n_steps,
        "last": step_proxies[-1] if n_steps else None,
        "previous": step_proxies[-2] if n_steps >= 2 else None,
        "min": min(observable) if observable else None,
        "max": max(observable) if observable else None,
        "unobserved": n_steps - len(observable),
    }


def _input_per_step_measure(step_proxies: list[Any], n_steps: int,
                            detail: bool) -> dict:
    """The `input_per_step` measure. With `--steps` its value is the FULL
    ordered per-step list; by default it is the fixed-size summary. Either way
    the measure is the declared proxy (`estimated`) and carries the
    `truncated` indicator declaring the size policy and its cause (PD-8,
    PD-12/D2)."""
    if detail:
        leaf = _measure(list(step_proxies), "tokens", _DETAIL_PROVENANCE,
                        BUCKET_ESTIMATED)
    else:
        leaf = _measure(_proxy_summary(step_proxies, n_steps), "tokens",
                        _SUMMARY_PROVENANCE, BUCKET_ESTIMATED)
    leaf["truncated"] = {
        "truncated": not detail,
        "cause": _DETAIL_CAUSE if detail else _TRUNCATED_CAUSE,
        "omitted_steps": 0 if detail else n_steps,
        "detail_flag": DETAIL_FLAG,
    }
    return leaf


def _build_measures(collected: dict, detail: bool) -> tuple[dict, list[str]]:
    """Measures of the first stretch. Each metric lives in EXACTLY ONE bucket:
    the per-step context proxy is `estimated` (never the real window); counts,
    positions, times and output size are `observed`; a null/not-reported value
    is `unknown` with a cause, never 0. An aggregate that SUMS a per-step
    component is a COMPLETE observation only if ALL steps report it (D1)."""
    steps = collected["steps"]
    stretch_calls = collected["stretch_calls"]
    session_calls = collected["session_calls"]

    n_steps = len(steps)
    step_inputs: list[int] = []
    step_reads: list[int] = []
    step_writes: list[int] = []
    step_costs: list[float] = []
    step_proxies: list[Any] = []
    incomplete_components: set[str] = set()
    input_report = 0
    read_report = 0
    write_present = 0
    cost_report = 0
    for step in steps:
        data = step["data"]
        cost = data.get("cost")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool):
            step_costs.append(cost)
            cost_report += 1
        tokens = data.get("tokens")
        if not isinstance(tokens, dict):
            step_proxies.append(None)
            incomplete_components.update(
                ("input", "cache.read", "cache.write"))
            continue
        cache = tokens.get("cache")
        cache = cache if isinstance(cache, dict) else {}
        input_n = tokens.get("input") if _is_int(tokens.get("input")) else None
        read_n = cache.get("read") if _is_int(cache.get("read")) else None
        write_n = cache.get("write") if _is_int(cache.get("write")) else None
        if input_n is not None:
            step_inputs.append(input_n)
            input_report += 1
        if read_n is not None:
            step_reads.append(read_n)
            read_report += 1
        if write_n is not None:
            step_writes.append(write_n)
            write_present += 1
        # The per-step context proxy needs ALL THREE components: `input` +
        # `cache.read` + `cache.write` (a reported 0 counts). A step missing any
        # component has a NULL proxy, never 0 nor a partial subtotal (D1).
        if input_n is not None and read_n is not None and write_n is not None:
            step_proxies.append(input_n + read_n + write_n)
        else:
            step_proxies.append(None)
            if input_n is None:
                incomplete_components.add("input")
            if read_n is None:
                incomplete_components.add("cache.read")
            if write_n is None:
                incomplete_components.add("cache.write")
    incomplete_proxies = sum(1 for p in step_proxies if p is None)

    output_lengths: list[int] = []
    for call in stretch_calls:
        output_lengths.extend(call["output_lengths"])
    has_output_evidence = bool(output_lengths)
    total_output = sum(output_lengths) if has_output_evidence else None
    max_output = max(output_lengths) if has_output_evidence else None

    input_complete = n_steps > 0 and input_report == n_steps
    read_complete = n_steps > 0 and read_report == n_steps
    cost_complete = n_steps > 0 and cost_report == n_steps

    accumulated = sum(step_inputs) if input_complete else None
    cache_read = sum(step_reads) if read_complete else None
    cost = sum(step_costs) if cost_complete else None
    # `cache.write` is not reported by the configured provider (0 in every
    # measured session): a reported 0 is "not reported", so it is `unknown`
    # with a cause, NEVER 0 (PD-4). Only a positive reported value is observed.
    positive_writes = [w for w in step_writes if w > 0]
    cache_write = sum(positive_writes) if positive_writes else None

    start_time = collected["start_time"]
    end_time = collected["end_time"]
    duration = None
    if start_time is not None and end_time is not None:
        duration = (end_time - start_time) / 60_000.0

    measures: dict[str, Any] = {
        "segment_duration": _measure(
            duration, "minutes",
            "last time_updated minus first time_created of the stretch",
            BUCKET_OBSERVED if duration is not None else BUCKET_UNKNOWN),
        "tool_calls": _measure(
            len(stretch_calls), "calls",
            "tool calls of the first stretch",
            BUCKET_OBSERVED),
        "session_tool_calls": _measure(
            len(session_calls), "calls",
            "tool calls of the whole session (reported apart from the stretch)",
            BUCKET_OBSERVED),
        "session_reads": _measure(
            collected["session_reads"], "calls",
            "read tool calls of the whole session (reported apart from "
            "previous_reads)",
            BUCKET_OBSERVED),
        "total_output": _measure(
            total_output, "unicode_characters",
            "sum of len(text) over tool state.content[] text chunks of the "
            "stretch (unknown, never 0, when the stretch carries no output "
            "text)",
            BUCKET_OBSERVED if has_output_evidence else BUCKET_UNKNOWN),
        "max_output": _measure(
            max_output, "unicode_characters",
            "largest single tool output of the stretch (len(text)); unknown, "
            "never 0, when the stretch carries no output text",
            BUCKET_OBSERVED if has_output_evidence else BUCKET_UNKNOWN),
        "input_per_step": _input_per_step_measure(step_proxies, n_steps,
                                                   detail),
        "accumulated": _measure(
            accumulated, "tokens",
            "sum of per-step reported tokens.input over the stretch; complete "
            "only when every step reports tokens.input (otherwise unknown, "
            "never a partial subtotal)",
            BUCKET_OBSERVED if input_complete else BUCKET_UNKNOWN),
        "cache": {
            "read": _measure(
                cache_read, "tokens",
                "sum of per-step reported cache.read over the stretch; complete "
                "only when every step reports cache.read (otherwise unknown, "
                "never a partial subtotal)",
                BUCKET_OBSERVED if read_complete else BUCKET_UNKNOWN),
            "write": _measure(
                cache_write, "tokens",
                "cache.write not reported by the provider: a reported 0 means "
                "not reported (unknown, never 0)",
                BUCKET_OBSERVED if positive_writes else BUCKET_UNKNOWN),
        },
        "cost": _measure(
            cost, "currency_units",
            "sum of per-step reported cost over the stretch; complete only when "
            "every step reports cost (otherwise unknown, never a partial "
            "subtotal)",
            BUCKET_OBSERVED if cost_complete else BUCKET_UNKNOWN),
    }

    causes: list[str] = []
    if n_steps == 0:
        causes.append(_NO_STEPS_CAUSE)
    else:
        if not input_complete:
            causes.append(_coverage_cause(
                "tokens.input", input_report, n_steps))
        if not read_complete:
            causes.append(_coverage_cause("cache.read", read_report, n_steps))
        if not cost_complete:
            causes.append(_coverage_cause("cost", cost_report, n_steps))
    if not positive_writes:
        write_cause = (
            "cache.write is not reported by the provider (a reported 0 means "
            "not reported): unknown, never 0")
        if n_steps > 0 and write_present < n_steps:
            missing = n_steps - write_present
            write_cause += (
                f"; the stretch carries cache.write in {write_present} of "
                f"{n_steps} messages: {missing} messages do not carry it, so "
                "the stretch coverage of cache.write is not a complete "
                "observation; no partial sum is emitted")
        causes.append(write_cause)
    if incomplete_proxies:
        missing_names = ", ".join(sorted(incomplete_components))
        causes.append(
            f"the per-step context proxy is unknown for {incomplete_proxies} "
            "step(s) of the stretch: those steps do not report "
            f"{missing_names} (proxy = input + cache.read + cache.write; a null "
            "proxy means not observable for that step, never 0)")
    if not has_output_evidence:
        causes.append(_OUTPUT_ABSENT_CAUSE)
    if not collected["saw_tokens"]:
        causes.append(_NO_TOKEN_DATA_CAUSE)
    return measures, causes


def _is_resume_invocation(command: Any) -> bool:
    """A shell call invokes the continuity CLI's `resume` subcommand. Help
    calls (`--help`/`-h` and analogues) do NOT count (PD-6). A command that
    merely MENTIONS `resume` in its content is not a shell command and never
    reaches here."""
    if not isinstance(command, str) or not command.strip():
        return False
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    if not tokens:
        return False
    lowered = [token.lower() for token in tokens]
    if any(token in ("--help", "-h") for token in lowered):
        return False
    for index, token in enumerate(lowered):
        if token != "resume":
            continue
        if index == 0:
            return True
        previous = lowered[index - 1]
        if previous.endswith(".py") or "continuity" in previous:
            return True
    return False


def _find_resume(calls: list[dict]) -> dict | None:
    for call in calls:
        if call["name"] != "shell":
            continue
        state_input = call.get("input")
        command = (state_input.get("command")
                   if isinstance(state_input, dict) else None)
        if _is_resume_invocation(command):
            return call
    return None


def _find_dispatch(calls: list[dict]) -> dict | None:
    for call in calls:
        if call["name"] in DISPATCH_TOOL_NAMES:
            return call
    return None


# ---------------------------------------------- common delegation interface


def _program_basename(token: str) -> str:
    """The basename of a program token (a path to the program is accepted: the
    material fact is the PROGRAM, not its exact path — same class as the resume
    rule, which does not fix the CLI's path)."""
    return os.path.basename(token.replace("\\", "/"))


def _shell_segments(command: str) -> list[str]:
    """Split a shell command at the operators that START a new command, so the
    program of each segment can be told apart (`grep ... | head` runs two)."""
    segments = [command]
    for separator in _SHELL_SEPARATORS:
        expanded: list[str] = []
        for segment in segments:
            expanded.extend(segment.split(separator))
        segments = expanded
    return segments


def _skip_wrapper(tokens: list[str], index: int, base: str) -> int:
    """The index just past the wrapper at `tokens[index]` (005-007 review B2).

    The wrapper is not the invoked program: its flags (with their arguments) and
    `timeout`'s bare duration operand are dropped so the REAL program is told
    apart. Bounded by the token list, so it never loops.
    """
    argument_flags = _WRAPPER_ARGUMENT_FLAGS.get(base, frozenset())
    index += 1  # the wrapper word itself
    while (index < len(tokens) and tokens[index].startswith("-")
           and tokens[index] != "--"):
        flag = tokens[index]
        index += 1
        if flag in argument_flags and index < len(tokens):
            index += 1
    if index < len(tokens) and tokens[index] == "--":
        index += 1
    if base == "timeout" and index < len(tokens):
        index += 1  # the bare duration operand (`timeout 60 prog`)
    return index


def _shell_c_command(tokens: list[str], index: int) -> str | None:
    """The quoted command of a shell interpreter's `-c "<command>"` at
    `tokens[index]`, or None when the interpreter declares no `-c` argument."""
    for position in range(index + 1, len(tokens)):
        if tokens[position] != "-c":
            continue
        if position + 1 < len(tokens):
            return tokens[position + 1]
        return None
    return None


def _segment_resolution(tokens: list[str], depth: int = 0
                        ) -> tuple[str | None, list[str]]:
    """The program a shell segment INVOKES and the tokens of the invocation.

    Skips leading `NAME=value` assignments and the known WRAPPER prefixes
    (005-007 review B2: `time`, `env`, `nohup`, `nice`, `ionice`, `stdbuf`,
    `command`, `timeout` with its duration, `sudo`); an interpreter prefix
    (`python3 prog.py`) yields `prog.py`; a shell interpreter with
    `-c "<command>"` is resolved ONE pass deeper (bounded, never infinite) and
    the inner tokens join the invocation tokens, so help detection still works
    through the wrapper. The SECOND element lets the caller see every token that
    constitutes the invocation, never only the outer ones.
    """
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if "=" in token and not token.startswith("-"):
            index += 1
            continue
        base = _program_basename(token)
        if base in _DELEGATION_WRAPPERS:
            index = _skip_wrapper(tokens, index, base)
            continue
        if base in _SHELL_INTERPRETERS and depth < 1:
            inner = _shell_c_command(tokens, index)
            if inner is not None:
                try:
                    inner_tokens = shlex.split(inner)
                except ValueError:
                    inner_tokens = inner.split()
                if inner_tokens:
                    program, _ = _segment_resolution(inner_tokens, depth + 1)
                    return program, tokens + inner_tokens
            return token, tokens
        if base in _DELEGATION_INTERPRETERS:
            index += 1
            while index < len(tokens) and tokens[index].startswith("-"):
                index += 1
            if index >= len(tokens):
                return None, tokens
            return tokens[index], tokens
        return token, tokens
    return None, tokens


def _segment_program(tokens: list[str]) -> str | None:
    """The program a shell segment INVOKES (`_segment_resolution`, first item)."""
    return _segment_resolution(tokens)[0]


def _delegation_call_kind(command: Any) -> str | None:
    """Whether a shell command INVOKES the delegation program: `dispatch` (a
    real invocation), `help` (an invocation that only asks for help: excluded)
    or `None` (the program is NOT invoked — e.g. merely mentioned as the
    argument of another program such as `grep`)."""
    if not isinstance(command, str) or not command.strip():
        return None
    kinds: set[str] = set()
    for segment in _shell_segments(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if not tokens:
            continue
        program, invocation_tokens = _segment_resolution(tokens)
        if program is None or _program_basename(program) != DELEGATION_PROGRAM:
            continue
        lowered = [token.lower() for token in invocation_tokens]
        if any(flag in lowered for flag in _HELP_FLAGS):
            kinds.add("help")
        else:
            kinds.add("dispatch")
    if "dispatch" in kinds:
        return "dispatch"
    if "help" in kinds:
        return "help"
    return None


def _mentions_delegation(calls: list[dict]) -> bool:
    """Whether any call's arguments or content only MENTION the delegation
    program (a `write`'s content, a `grep`'s argument). A mention is NOT a
    dispatch: the reader never infers a dispatch from text (PD-9)."""
    for call in calls:
        if DELEGATION_PROGRAM in json.dumps(call.get("input"),
                                            ensure_ascii=False):
            return True
    return False


def _find_dispatch_delegation(
        calls: list[dict]) -> tuple[dict | None, str | None, str | None]:
    """With `--delegation-dispatch`: the FIRST dispatch of the stretch — a call
    made with a recognized dispatch tool NAME, or a shell call that REALLY
    invokes the delegation program. When there is none, returns the honest
    reason ('help' | 'mention' | None) instead of a fabricated dispatch."""
    help_seen = False
    for call in calls:
        if call["name"] in DISPATCH_TOOL_NAMES:
            return call, None, DISPATCH_TOOL_METHOD
        if call["name"] != "shell":
            continue
        input_args = call.get("input")
        command = (input_args.get("command")
                   if isinstance(input_args, dict) else None)
        kind = _delegation_call_kind(command)
        if kind == "dispatch":
            return call, None, DELEGATION_DISPATCH_METHOD
        if kind == "help":
            help_seen = True
    if help_seen:
        return None, "help", None
    if _mentions_delegation(calls):
        return None, "mention", None
    return None, None, None


_ABSENT_DISPATCH_CAUSE_BY_REASON = {
    "help": _ABSENT_DISPATCH_CAUSE_HELP,
    "mention": _ABSENT_DISPATCH_CAUSE_MENTION,
}


def _dispatch_recognition() -> dict:
    """The CLOSED recognized dispatch set with the METHOD and PROVENANCE of each
    entry (PD-9). Two classes of evidence: the tool NAME of the call vs. the
    MATERIAL FACT that a shell call really invokes the delegation program."""
    tool_entry = {"method": DISPATCH_TOOL_METHOD,
                  "provenance": DISPATCH_TOOL_PROVENANCE}
    return {
        "subagent": dict(tool_entry),
        "task": dict(tool_entry),
        DELEGATION_ENTRY: {"method": DELEGATION_DISPATCH_METHOD,
                           "provenance": DELEGATION_DISPATCH_PROVENANCE},
    }


def _relative_minutes(call: dict | None, start_time: Any) -> float | None:
    if call is None or start_time is None or call.get("time") is None:
        return None
    return (call["time"] - start_time) / 60_000.0


def _milestone(status: str, call: dict | None, time_relative: float | None,
               cause: str | None, which: str, method: str | None = None) -> dict:
    """One milestone. When it is `observed`, the POSITION is always emitted
    (it is observable). The relative TIME is emitted as a number when it is
    observable; when it is NOT (e.g. the milestone message carries no numeric
    time) it is `null` — NEVER a fabricated `0.0` — and the milestone carries a
    cause declaring the time not observable (D1/PD-4/INV-4). When the
    delegation flag declares the recognition METHODS (PD-9), the observed
    milestone carries the `method` of the entry that recognized it."""
    if status == "observed" and call is not None:
        block: dict[str, Any] = {
            "status": "observed",
            "position": {
                "call_index": call["call_index"],
                "seq": call["seq"],
            },
            "time_relative": time_relative,
        }
        if method is not None:
            block["method"] = method
        if time_relative is None:
            block["cause"] = _milestone_time_cause(which)
        return block
    return {"status": status, "cause": cause or _NO_TRACE_CAUSE}


def _milestone_block(collected: dict,
                     delegation_dispatch: bool = False
                     ) -> tuple[dict, dict, list[str]]:
    """The two SEPARATE milestones (PD-6) and their orientation measures.
    Absent → `absent` with a cause; with no trace → `unknown` with a cause.
    Never invented, never a zero (PD-4). A milestone whose position IS observed
    but whose time is NOT stays `observed` with `time_relative: null` and a
    cause, and its time-to measure is `unknown` (value null), never `0`. With
    `--delegation-dispatch` the recognized dispatch set also covers a shell
    call that REALLY invokes the delegation program, the milestone carries the
    declared METHOD of its entry (PD-9) and the absence cause names, per trace,
    the honest limit (mention / help)."""
    calls = collected["stretch_calls"]
    start_time = collected["start_time"]
    resume = _find_resume(calls)
    dispatch_method: str | None = None
    if delegation_dispatch:
        dispatch, dispatch_reason, dispatch_method = _find_dispatch_delegation(
            calls)
    else:
        dispatch, dispatch_reason = _find_dispatch(calls), None
    causes: list[str] = []

    if not collected["has_trace"]:
        resume_status = dispatch_status = "unknown"
        resume_cause = dispatch_cause = _NO_TRACE_CAUSE
    else:
        resume_status = "observed" if resume is not None else "absent"
        dispatch_status = "observed" if dispatch is not None else "absent"
        resume_cause = None if resume is not None else _ABSENT_RESUME_CAUSE
        if dispatch is not None:
            dispatch_cause = None
        elif delegation_dispatch:
            dispatch_cause = _ABSENT_DISPATCH_CAUSE_BY_REASON.get(
                dispatch_reason, _ABSENT_DISPATCH_CAUSE_DELEGATION)
        else:
            dispatch_cause = _ABSENT_DISPATCH_CAUSE

    resume_time = _relative_minutes(resume, start_time)
    dispatch_time = _relative_minutes(dispatch, start_time)

    milestones = {
        "first_resume": _milestone(
            resume_status, resume, resume_time, resume_cause, "first resume"),
        "first_dispatch": _milestone(
            dispatch_status, dispatch, dispatch_time, dispatch_cause,
            "first dispatch", dispatch_method),
    }
    if resume is not None and resume_time is None:
        causes.append(
            _milestone_time_cause("first resume"))
    if dispatch is not None and dispatch_time is None:
        causes.append(
            _milestone_time_cause("first dispatch"))

    if resume is not None:
        previous = [c for c in calls
                    if c["call_index"] < resume["call_index"]]
        previous_calls: int | None = len(previous)
        previous_reads: int | None = sum(
            1 for c in previous if c["name"] == "read")
        breakdown: dict | None = {}
        for call in previous:
            name = call["name"]
            breakdown[name] = breakdown.get(name, 0) + 1
    else:
        previous_calls = previous_reads = breakdown = None

    observed = resume is not None
    milestone_measures = {
        "time_to_first_resume": _measure(
            resume_time, "minutes",
            "time from the start of the stretch to the first resume milestone; "
            "unknown, never 0, when the milestone time is not observable",
            BUCKET_OBSERVED if resume_time is not None else BUCKET_UNKNOWN),
        "time_to_first_dispatch": _measure(
            dispatch_time, "minutes",
            "time from the start of the stretch to the first dispatch "
            "milestone; unknown, never 0, when the milestone time is not "
            "observable",
            BUCKET_OBSERVED if dispatch_time is not None else BUCKET_UNKNOWN),
        "previous_calls": _measure(
            previous_calls, "calls",
            "tool calls before the first resume milestone",
            BUCKET_OBSERVED if observed else BUCKET_UNKNOWN),
        "previous_reads": _measure(
            previous_reads, "calls",
            "read tool calls before the first resume milestone",
            BUCKET_OBSERVED if observed else BUCKET_UNKNOWN),
        "previous_calls_by_tool": _measure(
            breakdown, "calls",
            "tool calls before the first resume milestone, by tool name",
            BUCKET_OBSERVED if observed else BUCKET_UNKNOWN),
    }
    return milestones, milestone_measures, causes


def _window(cutoff: float, start_seq: Any = None,
            end_seq: Any = None) -> dict:
    return {
        "criterion": CUT_CRITERION,
        "start_ref": f"seq:{start_seq}" if start_seq is not None else None,
        "end_ref": f"seq:{end_seq}" if end_seq is not None else None,
        "cutoff": cutoff,
    }


def _measure_session(conn: sqlite3.Connection, row: tuple,
                     idle_threshold: float,
                     detail: bool,
                     delegation_dispatch: bool = False
                     ) -> tuple[dict, list[str]]:
    session_id, agent, model_raw, parent_id, version, _t_created, _t_updated = row
    messages = _load_messages(conn, session_id)
    stretch = _first_stretch(messages, idle_threshold)
    collected = _collect(messages, stretch)
    measures, causes = _build_measures(collected, detail)
    milestones, milestone_measures, milestone_causes = _milestone_block(
        collected, delegation_dispatch)
    measures.update(milestone_measures)
    causes.extend(milestone_causes)

    session = {
        "session_ref": _hash_ref(session_id),
        "role": agent if isinstance(agent, str) and agent.strip() else "unknown",
        "model": _parse_model(model_raw),
        "parent_ref": _hash_ref(parent_id),
        "runtime_version": version if isinstance(version, str) and version.strip()
        else None,
        "window": _window(idle_threshold, collected["start_seq"],
                          collected["end_seq"]),
        "milestones": milestones,
        "measures": measures,
        "buckets": _bucket_index(measures),
    }
    return session, causes


# ------------------------------------------------------------------ aggregate


# Components of `roles[].sums` that SUMS a per-session measure (R1). Each one is
# emitted as a DECLARED entry `{value, unit, bucket, sessions_reporting,
# sessions_total, cause}` that carries its COVERAGE: the sum is a COMPLETE
# observation of the role ONLY when EVERY session of the role reports the
# component (a reported 0 counts as reported); with at least one session that
# does NOT report it, the entry is `unknown` with `value` null — a partial
# subtotal is NEVER presented as the role total — and `cause` declares the
# coverage. `sums.sessions` stays the INTEGER member count (a count of members,
# not a sum of a measure).
ROLE_SUM_COMPONENTS = (
    "accumulated",
    "cache.read",
    "cache.write",
    "cost",
    "total_output",
    "max_output",
    "segment_duration",
    "tool_calls",
    "session_tool_calls",
    "session_reads",
    "time_to_first_resume",
    "time_to_first_dispatch",
    "previous_calls",
    "previous_reads",
)


def _role_coverage_cause(role: str, component: str, reporting: int, total: int,
                         kind: str = "sum") -> str:
    """ONE AGGREGATED cause for a per-role aggregate component whose coverage is
    incompleto (R1): a partial subtotal is NEVER presented as the role total.
    It names the ROLE, the COMPONENT and the coverage (`k` of `n`) — ONE entry
    per (role, component), never one per session (the same class as the stretch
    coverage, one dimension up)."""
    missing = total - reporting
    if kind == "sum":
        tail = (
            "the sum over the role is a partial subtotal, not a complete "
            "observation of the role; no partial sum is emitted (unknown, "
            "never a partial subtotal presented as the role total)")
    else:
        tail = (
            "the observed values cover a subset of the role, not the whole "
            "role; a subset is never presented as the whole role (unknown, "
            "never a partial distribution presented as the role total)")
    return (
        f"roles[{role}]: {component} is reported by {reporting} of {total} "
        f"sessions: {missing} session(s) do not report it, so {tail}")


def _role_sum_entry(value: Any, unit: str, bucket: str, reporting: int,
                    total: int, cause: str | None) -> dict:
    """One DECLARED summed component of `roles[].sums` (R1):
    `{value, unit, bucket, sessions_reporting, sessions_total, cause}`. The
    coverage is always a number pair, never null."""
    return {
        "value": value,
        "unit": unit,
        "bucket": bucket,
        "sessions_reporting": reporting,
        "sessions_total": total,
        "cause": cause,
    }


def _aggregate_roles(sessions: list[dict]) -> tuple[list[dict], list[str]]:
    """Aggregate per role. Every SUMMED component is a DECLARED entry carrying
    its COVERAGE (R1): a partial subtotal is NEVER presented as the role total.
    `sums.sessions` stays the integer member count. The same class covers
    `distributions`: the observed values carry their coverage. Returns the roles
    and ONE aggregated cause per (role, component) with incomplete coverage."""
    grouped: dict[str, list[dict]] = {}
    for session in sessions:
        grouped.setdefault(session["role"], []).append(session)
    roles: list[dict] = []
    causes: list[str] = []
    for role in sorted(grouped):
        members = grouped[role]
        total = len(members)
        leaves = [dict(_measure_leaves(session["measures"]))
                  for session in members]

        sums: dict[str, Any] = {"sessions": total}
        for component in ROLE_SUM_COMPONENTS:
            values: list[float] = []
            unit = ""
            for leaf_map in leaves:
                leaf = leaf_map.get(component)
                if leaf is None:
                    continue
                if not unit:
                    unit = leaf.get("unit") or ""
                value = leaf.get("value")
                if isinstance(value, (int, float)) and not isinstance(
                        value, bool):
                    values.append(value)
            reporting = len(values)
            if reporting == total:
                sums[component] = _role_sum_entry(
                    sum(values), unit, BUCKET_OBSERVED, reporting, total, None)
            else:
                cause = _role_coverage_cause(role, component, reporting, total)
                sums[component] = _role_sum_entry(
                    None, unit, BUCKET_UNKNOWN, reporting, total, cause)
                causes.append(cause)

        distributions: dict[str, Any] = {}
        output_chars: list[int] = []
        for leaf_map in leaves:
            leaf = leaf_map.get("total_output")
            value = leaf.get("value") if leaf else None
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                output_chars.append(int(value))
        if output_chars:
            reporting = len(output_chars)
            cause = None
            if reporting < total:
                cause = _role_coverage_cause(
                    role, "total_output_chars", reporting, total,
                    kind="distribution")
                causes.append(cause)
            distributions["total_output_chars"] = {
                "values": sorted(output_chars),
                "sessions_reporting": reporting,
                "sessions_total": total,
                "cause": cause,
            }

        roles.append({
            "role": role,
            "sums": sums,
            "distributions": distributions,
        })
    return roles, causes


# ---------------------------------------------------------------- set summary


# Magnitudes of the SET SUMMARY (C2). Each is a DECLARED entry carrying its
# bucket and its COVERAGE over the included sessions: a magnitude without full
# coverage is `unknown` with `value: null` and a cause — a partial subtotal is
# NEVER presented as the set total and NEVER `0` (INV-9).
SET_SUMMARY_MAGNITUDES = (
    "accumulated",
    "cache.read",
    "cache.write",
    "cost",
    "total_output",
    "max_output",
    "segment_duration",
    "tool_calls",
    "session_tool_calls",
    "session_reads",
)

_SET_MILESTONE_KEYS = ("first_resume", "first_dispatch")


def _set_magnitude_cause(component: str, reporting: int, total: int) -> str:
    """ONE aggregated cause for a set magnitude without full coverage: the
    aggregate is `unknown` (value null), never a partial subtotal presented as
    the set total and never `0`."""
    missing = total - reporting
    return (
        f"set summary: the magnitude {component!r} is reported by {reporting} "
        f"of {total} included session(s): {missing} do not report it, so the "
        "aggregate is not a complete observation of the set (unknown, value "
        "null; never a partial subtotal presented as the set total and never 0)")


def _set_magnitude(leaves: list[dict], component: str) -> dict:
    """One declared magnitude of the set summary (C2), same shape as
    `$defs/role_aggregate_entry`: `{value, unit, bucket, sessions_reporting,
    sessions_total, cause}`. Complete (numeric value, bucket observed) only when
    EVERY included session reports it; otherwise `unknown` with `value: null`
    and a coverage cause — a partial subtotal is never the set total."""
    values: list[float] = []
    unit = ""
    for leaf_map in leaves:
        leaf = leaf_map.get(component)
        if leaf is None:
            continue
        if not unit:
            unit = leaf.get("unit") or ""
        value = leaf.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(value)
    reporting = len(values)
    total = len(leaves)
    if total and reporting == total:
        return _role_sum_entry(sum(values), unit or component, BUCKET_OBSERVED,
                               reporting, total, None)
    return _role_sum_entry(None, unit or component, BUCKET_UNKNOWN, reporting,
                           total,
                           _set_magnitude_cause(component, reporting, total))


def _session_reports_tokens(measures: dict) -> bool:
    """Whether a session reports token data (used for the set coverage): a
    session is `reporting` when at least one token magnitude is a complete
    observation."""
    leaves = dict(_measure_leaves(measures))
    for name in ("accumulated", "cache.read", "cache.write"):
        leaf = leaves.get(name)
        value = leaf.get("value") if leaf else None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
    return False


def _set_coverage(sessions: list[dict]) -> dict:
    """The DECLARED coverage of the set (C2): a subset is never presented as the
    whole set."""
    total = len(sessions)
    reporting = sum(1 for s in sessions
                    if _session_reports_tokens(s.get("measures") or {}))
    cause = None
    if reporting < total:
        cause = (
            f"set coverage: {reporting} of {total} included session(s) report "
            "token data; the remaining session(s) do not, so the set is "
            "measured over a subset (declared, never presented as the whole)")
    return {
        "sessions_reporting": reporting,
        "sessions_total": total,
        "cause": cause,
    }


def _earliest_observed_milestone(observed: list[tuple[str, dict]]) -> dict:
    """The earliest observed milestone across the included sessions: by relative
    time when observable, otherwise by position."""
    def order(item):
        block = item[1]
        time_relative = block.get("time_relative")
        if isinstance(time_relative, (int, float)) and not isinstance(
                time_relative, bool):
            return (0, float(time_relative))
        call_index = (block.get("position") or {}).get("call_index")
        return (1, float(call_index) if isinstance(call_index, int) else 0.0)
    return min(observed, key=order)[1]


def _set_milestones(sessions: list[dict]) -> dict:
    """The milestones of the SET (C2), same shape as `$defs/milestone`: observed
    when at least one included session observed it (earliest, referenced to that
    session); absent with a cause otherwise. Never invented."""
    milestones: dict[str, Any] = {}
    for key in _SET_MILESTONE_KEYS:
        observed: list[tuple[str, dict]] = []
        for session in sessions:
            block = (session.get("milestones") or {}).get(key)
            if isinstance(block, dict) and block.get("status") == "observed":
                observed.append((session.get("session_ref"), block))
        if observed:
            chosen = _earliest_observed_milestone(observed)
            entry: dict[str, Any] = {
                "status": "observed",
                "session_ref": next(ref for ref, block in observed
                                    if block is chosen),
                "position": chosen.get("position"),
                "time_relative": chosen.get("time_relative"),
            }
            if entry["time_relative"] is None:
                entry["cause"] = _milestone_time_cause(key.replace("_", " "))
            milestones[key] = entry
        else:
            milestones[key] = {
                "status": "absent",
                "cause": (
                    f"no included session of the set observes the {key} "
                    "milestone in its first stretch (absent; the milestone is "
                    "not invented)"),
            }
    return milestones


def _build_set_summary(args: argparse.Namespace, sessions: list[dict],
                       store_ref: str | None, versions: list[str]) -> dict:
    """The multi-session SET SUMMARY as a SEPARATE ADDITIVE document
    (`set-summary-v1`, C2/V1). It carries the sessions included (hashed
    references), the declared coverage, the milestones, the magnitudes with
    their bucket and their coverage, and references to the per-session detail.
    The per-session detail is NOT emitted by default: it is restored only with
    the declared flag (`detail_flag`, `--detail`). The neutral per-session
    record is untouched (INV-5)."""
    leaves = [dict(_measure_leaves(s.get("measures") or {})) for s in sessions]
    magnitudes = {component: _set_magnitude(leaves, component)
                  for component in SET_SUMMARY_MAGNITUDES}
    milestones = _set_milestones(sessions)
    included = [s["session_ref"] for s in sessions if s.get("session_ref")]
    coverage = _set_coverage(sessions)

    unknowns: list[str] = []
    if coverage["cause"]:
        unknowns.append(coverage["cause"])
    for entry in magnitudes.values():
        if entry["cause"]:
            unknowns.append(entry["cause"])
    for entry in milestones.values():
        if entry.get("cause"):
            unknowns.append(entry["cause"])

    document: dict[str, Any] = {
        "meter": SET_SUMMARY_CONTRACT,
        "run": {
            "store_ref": store_ref,
            "runtime_version": versions[0] if versions else None,
            "schema": "recognized",
        },
        "sessions_included": included,
        "coverage": coverage,
        "milestones": milestones,
        "magnitudes": magnitudes,
        "detail_ref": {
            "sessions": included,
            "flag": SET_DETAIL_FLAG,
            "note": (
                "references to the per-session detail; the detail itself is "
                "emitted only with the flag declared in `detail_flag`"),
        },
        "detail_flag": SET_DETAIL_FLAG,
        "unknowns": sorted(set(unknowns)),
    }
    if getattr(args, "detail", False):
        document["detail"] = sessions
    return document


def _build_application(args: argparse.Namespace, sessions: list[dict],
                       relations: list[str], store_ref: str | None) -> dict | None:
    """The OPTIONAL referenced application annotation (PD-9). It is emitted
    when an application reference is declared, or when the document has an
    observed coordinator/worker relation to declare; otherwise it is absent
    (the reader never invents it). `ref` is transported AS PASSED (never a copy
    of the referenced content); when no application receipt is declared the
    annotation is anchored to the document's own durable, hashed store
    reference — the reader never invents an application receipt. `limit` is
    declared by the caller; the reader neither judges nor approves."""
    ref = args.application_ref
    has_ref = isinstance(ref, str) and bool(ref.strip())
    if not has_ref and not relations:
        return None

    included = [s["session_ref"] for s in sessions if s.get("session_ref")]
    if has_ref:
        limit = args.application_limit or APPLICATION_UNKNOWN_LIMIT
        basis = (
            f"limit declared as explicit input by the caller ({limit!r}); the "
            f"reader transports it verbatim and neither judges nor approves "
            f"it; {len(sessions)} session(s) included; "
            f"{len(relations)} observed parent/child relation(s)")
        annotation: dict[str, Any] = {"ref": ref, "limit": limit,
                                      "basis": basis}
    else:
        annotation = {
            "ref": store_ref,
            "limit": APPLICATION_UNKNOWN_LIMIT,
            "basis": (
                f"{_APPLICATION_ABSENT_CAUSE}; the annotation references the "
                f"measurement store by its hashed reference; "
                f"{len(sessions)} session(s) included; {len(relations)} "
                f"observed parent/child relation(s)"),
        }
    annotation["included_sessions"] = included
    annotation["relations"] = list(relations)
    return annotation


# ------------------------------------------------------------------ driver


def _hashed_list(values: list[str]) -> str:
    """Hashed references (privacy), comma-separated, deduplicated and sorted.
    A raw identifier is NEVER emitted (PD-10/INV-7)."""
    hashed = {_hash_ref(value) for value in values}
    return ", ".join(sorted(ref for ref in hashed if ref))


def _partial_session_match_cause(unmatched: list[str],
                                 measured: list[str]) -> str:
    """D5: with several `--session` references, one that does NOT exist is not
    silently dropped: it is DECLARED (unknown with a cause). PRIVACY: the
    requested references are named by their HASHED reference (same form as
    `session_ref`), never raw. The declaration states the coverage of the
    request (which references were measured and which were not)."""
    return (
        f"partial --session match: {len(unmatched)} of "
        f"{len(unmatched) + len(measured)} requested session reference(s) did "
        "not match any session in the store (not found); unmatched requested "
        f"reference(s), hashed: {_hashed_list(unmatched)}; measured "
        f"reference(s), hashed: {_hashed_list(measured)}; the reader neither "
        "invents the missing session nor silently drops it (unknown)")


def _build_document(args: argparse.Namespace) -> dict:
    store = _resolve_store(args)
    refs = args.session if args.session else None
    if not refs and args.limit == 0:
        raise MeterError(
            "--limit 0 selects no session: refusing to emit an empty "
            "measurement (fail closed)")
    delegation_dispatch = getattr(args, "delegation_dispatch", False)

    conn = _connect_ro(store)
    try:
        _require_schema(conn)
        rows = _load_session_rows(conn, refs, args.limit)
        if refs and not rows:
            raise MeterError(
                "no session matched the requested --session references "
                "(fail closed)")
        sessions: list[dict] = []
        unknowns: list[str] = []
        for row in rows:
            session, causes = _measure_session(conn, row, args.idle_threshold,
                                               args.steps, delegation_dispatch)
            sessions.append(session)
            unknowns.extend(causes)

        # R1: the per-role aggregate (roles[].sums/distributions) DECLARES its
        # coverage; a partial subtotal is NEVER presented as the role total.
        # ONE aggregated cause per (role, component) with incomplete coverage.
        roles, role_causes = _aggregate_roles(sessions)
        unknowns.extend(role_causes)

        # Coordinator/worker families (PD-9): declare the relations actually
        # observed. A parent_id pointing to a session NOT in the store is an
        # unknown relation with a cause — the parent is never invented.
        parent_ids = [row[3] for row in rows
                      if isinstance(row[3], str) and row[3].strip()]
        present = _present_session_ids(conn, parent_ids)
        relations: list[str] = []
        for row in rows:
            session_id, parent_raw = row[0], row[3]
            if not (isinstance(parent_raw, str) and parent_raw.strip()):
                continue
            parent_ref = _hash_ref(parent_raw)
            child_ref = _hash_ref(session_id)
            if parent_raw in present:
                relations.append(f"{parent_ref} -> {child_ref}")
            else:
                unknowns.append(_DANGLING_PARENT_CAUSE)

        # D5: a requested `--session` reference that does not exist among
        # several is DECLARED (unknown with a cause, hashed), never silently
        # dropped. If NONE matches, the fail-closed above already returned.
        if refs:
            matched_ids = {row[0] for row in rows}
            unmatched = [ref for ref in refs if ref not in matched_ids]
            if unmatched:
                unknowns.append(_partial_session_match_cause(
                    unmatched, [row[0] for row in rows]))
    finally:
        conn.close()

    versions = sorted({
        row[4] for row in rows
        if isinstance(row[4], str) and row[4].strip()})
    store_ref = _hash_ref(str(store))

    # 005-003 T3: the multi-session SET SUMMARY is a SEPARATE ADDITIVE document
    # (`set-summary-v1`), emitted only with `--set-summary`. Without the flag the
    # neutral per-session record below is emitted exactly as before (INV-5).
    if getattr(args, "set_summary", False):
        return _build_set_summary(args, sessions, store_ref, versions)

    document = {
        "schema_version": SCHEMA_VERSION,
        "meter": METER_CONTRACT,
        "run": {
            "store_ref": store_ref,
            "runtime_version": versions[0] if versions else None,
            "schema": "recognized",
        },
        "window": _window(args.idle_threshold),
        "reader": {
            "dispatch_tools": sorted(DISPATCH_TOOL_NAMES),
        },
        "sessions": sessions,
        "roles": roles,
        "unknowns": sorted(set(unknowns)),
    }
    # 005-007 PD-9: with the delegation flag the reader ALSO declares the
    # recognized set with the method and provenance of each entry. Without it
    # the reader is unchanged (INV-5: the neutral record stays byte-identical).
    if delegation_dispatch:
        document["reader"]["dispatch_recognition"] = _dispatch_recognition()
    application = _build_application(args, sessions, relations, store_ref)
    if application is not None:
        document["application"] = application
    return document


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cdad_context_meter")
    parser.add_argument("--store", default=None)
    parser.add_argument("--session", action="append", default=None)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--idle-threshold", type=float,
                        default=DEFAULT_IDLE_THRESHOLD_MINUTES)
    parser.add_argument("--steps", action="store_true",
                        help="emit the full ordered per-step detail "
                             "instead of the fixed-size default summary "
                             "(PD-12/D2)")
    parser.add_argument("--set-summary", action="store_true",
                        help="emit the multi-session SET SUMMARY as a separate "
                             "additive document (set-summary-v1) instead of the "
                             "neutral per-session record (005-003 T3)")
    parser.add_argument("--detail", action="store_true",
                        help="with --set-summary, restore the per-session "
                             "detail (the flag the summary declares in "
                             "detail_flag)")
    parser.add_argument("--delegation-dispatch", action="store_true",
                        help="also recognize as a role work dispatch a shell "
                             "call that REALLY invokes the common delegation "
                             "interface (cdad_delegate.py), declaring the "
                             "recognized set with the method and provenance of "
                             "each entry (005-007 PD-9); without it the "
                             "neutral record is byte-identical to before")
    parser.add_argument("--application-ref", default=None)
    parser.add_argument("--application-limit", default=None,
                        choices=APPLICATION_LIMIT_VALUES)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        document = _build_document(args)
    except MeterError as exc:
        sys.stderr.write(f"cdad_context_meter: {exc}\n")
        return 1
    except sqlite3.Error as exc:
        sys.stderr.write(
            f"cdad_context_meter: session store error: {exc}\n")
        return 1
    # JSON is the ONLY output mode; `--json` is an accepted no-op (PD-11).
    sys.stdout.write(json.dumps(document, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
