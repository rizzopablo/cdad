#!/usr/bin/env python3
"""006-005 U6-5 RED — registro write-ahead del intento externo (E4/PD-19).

Contract (approved): `docs/specs/006-005-native-path-parity/spec.md` (sha256
3a824be3…df01) §3.1 E4 («un intento que no vuelve se lleva a `failed` por
comando … sin repetir efectos»), PD-19 (a)-(d), PD-1, PD-22; and 006-001
PD-3, PD-8, PD-9 and D-5 as amended by the U6-5 decision
(`docs/specs/006-005-native-path-parity/u6-5-decision.md`, revision 2,
reviews `u6-5-decision-review.md` / `u6-5-decision-rereview.md`). Evidence of
the real walk: `docs/epics/epic-006-opencode-concurrency/execution.md` E4 and
U6-5.

The defect this RED observes (measured in the real walk): the external module
writes its I8 attempt ONLY when it terminates. If the coordinator dies with
the runtime client alive (SIGKILL, shell-tool timeout, OOM): no record, the
packet stays `prepared`, `reconcile` says `not-started` / `repeat_effect:
false`, `disposition` is refused («only a dispatched packet can be
dispositioned»), the next `prepare` is refused («complete or fail it»), the
orphan commits with no state recording it, and the prior-attempt check has no
record to see, so a re-dispatch would open a second writer.

Contract decision pinned here (orchestrator, U6-5 decision D-U65-1..5):

  * the provisional I8 record is written BEFORE the runtime client is
    launched (after REQUEST, the prior-attempt check and the session id
    choice), with `session` = the chosen id, `model_reported: null` and the
    declared mark `write-ahead:` at the start of `provenance.session`;
  * the provisional record keeps the §2.6/006-001 shape: the mark comes
    before the first literal and the pairs go at the end — `row=unknown;
    store_reads=unknown; prior_check_reads=<n>` (O-4 of the re-review);
  * if the write-ahead record fails, the client is NEVER launched and the
    termination is `blocked` with the failure diagnosis (fail-closed;
    replaces 006-001 D-5 «a registration failure never changes the
    termination» only for this step);
  * every termination after the write-ahead completes the SAME record ONCE,
    replacing `session` (PD-8), `model_reported` from the store row and all
    PD-3 termination pairs (`row`, `store_reads`, `prior_check_reads`,
    `provenance.runtime`), so the final record is byte-identical to today's;
  * terminations BEFORE the write-ahead (preflight, live prior attempt,
    invalid request) register as today, final and not provisional.

Oracle discipline (black box, process level). The entry
`skills/cdad-cycle/scripts/cdad_dispatch.py` is invoked AS A PROCESS from a
staged copy of the skill tree, so the REAL runtime module
`skills/cdad-cycle/scripts/cdad_delegate_opencode.py` is the one resolved by
the `opencode` section of `runtimes.json` under a temporary
`XDG_CONFIG_HOME`/`HOME` — no fake module replaces the code under test. The
runtime binary is a fixture that sleeps, writes a disposable store row, exits
or refuses to start, and logs every invocation; the store is a disposable
SQLite database with the installed version's REAL shape (V-7 extended,
`execution.md`: `time_created INTEGER NOT NULL` in epoch MILLISECONDS,
`parent_id`/`agent` TEXT, `directory` TEXT NOT NULL). The crash is a SIGKILL
to the process group of the entry and the module while the fixture client
stays alive in its own group (measured: the client survives the group kill),
exactly the E4 premise. The oracles are observable behavior: exit code, the
stdout envelope, the I8 record on disk, `reconcile`'s classification, the
packet state, the staged inbox and whether the binary was invoked.

Nothing of the implementation is read or imported. The user's real config,
store and binary are never touched: every fixture is a per-test temporary.

MAPPING (one test per contracted oracle; every docstring starts with
`E4/PD-19 (U6-5)`):

  Oracle 1 — crash mid-run, client alive
    test_u65_crash_midrun_recovers_through_disposition
      -> E4, PD-19 (a)-(d), PD-1, PD-22; D-U65-1/2/3; O-4 (provisional shape)
  Oracle 2 — crash in the launch window (record present, no row ever)
    test_u65_crash_before_launch_recovers_through_disposition
      -> E4, PD-19; D-U65-1/2; O-3(ii)
  Oracle 3 — re-dispatch with the live session row
    test_u65_redispatch_with_live_session_is_blocked_without_run
      -> E4, PD-19 (d), PD-9 (006-001, INV-10); D-U65-3.4
  Oracle 4 — `completed` termination
    test_u65_completed_leaves_one_final_record_with_pd3_pairs
      -> PD-1, 006-001 PD-3, D-U65-2, D-ADP-2 (B-1 closure)
  Oracle 5 — binary that does not start / timeout without a complete row
    test_u65_binary_that_does_not_start_completes_with_null_session
      -> 006-001 PD-8 (amended for the provisional record), D-U65-2 (B-3)
    test_u65_timeout_without_row_keeps_the_termination_provenance
      -> 006-001 PD-3/PD-8, D-U65-2
  Oracle 6 — write-ahead failure
    test_u65_write_ahead_failure_does_not_launch_the_client
      -> PD-19, D-U65-1 fail-closed (B-2), PD-1
  Oracle 7 — ledger: one completion, identity fixed
    test_u65_second_completion_with_different_data_is_rejected
    test_u65_completion_over_an_unmarked_record_is_rejected
    test_u65_completion_changing_the_identity_is_rejected
      -> ledger write-once + D-U65-2
  Oracle 8 — termination before the write-ahead
    test_u65_termination_before_write_ahead_is_not_provisional
      -> D-U65-1 last bullet, 006-001 PD-9, PD-1

EXPECTED RED TODAY (declared, measured on this HEAD; every failure is an
AssertionError about missing behavior, never Import/Syntax/fixture):
  * oracle 1: no I8 record exists while the client is alive (the record is
    written only at termination) — the first assertion fails;
  * oracle 2: the client starts with no provisional record (same cause);
  * oracle 3: no provisional record exists and a re-dispatch invokes `run`
    again (a second writer);
  * oracle 6: a write-ahead failure does not stop the client (`run` is
    invoked) and the termination is not `blocked` — it carries the bounded
    note «worker record not written»;
  * oracle 7a: the first completion over a `write-ahead:` record is rejected
    as «different observation data».
  Oracles 4, 5a, 5b, 7b, 7c and 8 are declared GUARDS: they already answer
  with the contracted behavior today (final record with PD-3 pairs, session
  null for a binary that does not start, a final timeout record, the
  write-once rejections) and become discriminating once the one-time
  completion exists; they must stay GREEN after the fix.

A-1 (declared: NO existing test is reformulated in this RED). Reasons,
checked one by one:
  * `tests/test_006_001_t2_wait_recovery.py:865-871,1136-1141` asserts the
    FINAL `store_reads` equals the wait trace. The re-review B-1 closure
    requires the completion to replace all PD-3 termination pairs, so the
    final record stays byte-identical and the assertion remains valid; this
    file's oracle 4 re-asserts it through the new entry. The test is run as
    the declared U6-5 regression (O-5), not rewritten.
  * The ledger tests `tests/test_004_002_t4_dispatch.py`
    (`test_pd6_i8_reused_attempt_id_with_conflicting_data_rejected`, and the
    identical/idempotent case) use records WITHOUT the `write-ahead:` mark;
    the one-time completion is gated on the mark, so the write-once rule
    those tests pin is unchanged.
  * No test of the suite pins 006-001 D-5 «a registration failure never
    changes the termination»: a grep over `tests/` finds no such assertion,
    so the new fail-closed rule is new behavior, not a reformulation.
  * Tests that count exactly one record after a completed dispatch
    (`tests/test_005_010_t1_durable_signal.py:435` and siblings) remain valid
    because the completion REPLACES the same record (PD-1), it does not add
    a second one.

HONEST LIMIT (declared): the instant between the write-ahead and `Popen` is
not instrumented without reading implementation. Oracle 2 kills the
coordinator as soon as a parseable provisional record appears, with a client
variant that performs NO store write and no effect; the asserted material
state (record present, no row, no effects, same recovery path) is exactly the
pre-launch crash state. The docstrings do not claim a measured pre-launch
timestamp.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import build_project, read_state
from test_005_009_t1_interface import (
    I8_RECORD_KEYS,
    OUTPUT_KEYS,
    TERMINATION_VOCABULARY,
    dispatch_dir,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = REPO_ROOT / "scripts" / "cdad_continuity.py"

RUNTIME = "opencode"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

ENVELOPE_KEYS = OUTPUT_KEYS

FAKE_VERSION = "opencode v2.0.27-u65fix5"
ROW_MODEL = "u65fix5-fixture-model"
USER_TEXT = "U6-5 fixture: dispatch envelope received by the fake runtime."
FINAL_TEXT = (
    "# U6-5 fixture final text\n"
    "\n"
    "Byte-exact text used to exercise the completed termination.\n")

MARK = "write-ahead:"

# V-7 extended probe (execution.md): the INSTALLED version's `session_v2`
# types and units. `time_created` is an INTEGER in epoch MILLISECONDS (never
# the invented `REAL` seconds of older fixtures).
STORE_COLUMNS = [
    "id TEXT PRIMARY KEY",
    "parent_id TEXT",
    "agent TEXT",
    "model TEXT",
    "time_created INTEGER NOT NULL",
    "time_idle INTEGER",
    "idle_outcome TEXT",
    "directory TEXT NOT NULL",
]

STARTED_AT = "2026-10-19T00:00:00Z"

# O-4: the provisional record keeps §2.6's form — the pairs at the END.
PROVISIONAL_PAIRS_RE = re.compile(
    r"row=unknown[;\s].*store_reads=unknown[;\s].*prior_check_reads=\d+\s*$",
    re.S)

FINAL_PAIRS_RE = re.compile(
    r"row=(?:present|absent|unknown)[;\s].*store_reads=\S+[;\s].*"
    r"prior_check_reads=\d+\s*$", re.S)

# Measured literals of the bounded D-5 note / the write-once rejection. A
# completion over a provisional record must NOT leave one of these in the
# termination (B-3: no noisy rejection, no second row).
REJECTION_NOTE_LITERALS = (
    "worker record not written",
    "registration failed",
    "already exists with different observation data",
    "refusing to overwrite a dispatch record",
)

# ------------------------------------------------------- fixture: fake binary

FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
"""Fake runtime binary — fixture of
tests/test_006_005_u6fix5_write_ahead.py. NOT the product: it only materializes
the observed client surface the external path needs (a durable row, an exit, a
bounded sleep) and logs every invocation so the test can assert whether `run`
was invoked."""
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_FAKE = _HERE.parent
_CALLS = _FAKE / "calls.jsonl"
_STARTED = _FAKE / "started.flag"
_CLIENT_PID = _FAKE / "client.pid"
_EXIT_TS = _FAKE / "client-exit-ts.txt"
_VERSION = %VERSION%
_STORE = Path(%STORE%)
_MODEL = %MODEL%
_USER_TEXT = %USER_TEXT%
_FINAL_TEXT = %FINAL_TEXT%
_SLEEP_SECONDS = %SLEEP%


def _append(entry):
    with _CALLS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def _option(name):
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _message(text):
    return json.dumps({"content": [{"type": "text", "text": text}]},
                      sort_keys=True)


def _write_row(session_id, agent_id, *, idle, with_final_text):
    connection = sqlite3.connect(str(_STORE))
    try:
        now_ms = int(time.time() * 1000)
        directory = os.environ.get("PWD") or os.getcwd()
        connection.execute(
            "INSERT INTO session_v2 (id, parent_id, agent, model,"
            " time_created, time_idle, idle_outcome, directory)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, None, agent_id, _MODEL, now_ms - 1000,
             now_ms if idle else None, "succeeded" if idle else None,
             directory))
        connection.execute(
            "INSERT INTO session_message (id, session_id, type, seq, data)"
            " VALUES (?, ?, ?, ?, ?)",
            ("msg-u65-0001-" + session_id, session_id, "user", 1,
             _message(_USER_TEXT)))
        if with_final_text:
            connection.execute(
                "INSERT INTO session_message (id, session_id, type, seq, data)"
                " VALUES (?, ?, ?, ?, ?)",
                ("msg-u65-0002-" + session_id, session_id, "assistant", 2,
                 _message(_FINAL_TEXT)))
        connection.commit()
    finally:
        connection.close()


variant = (_FAKE / "variant").read_text(encoding="utf-8").strip()

if "--version" in sys.argv[1:]:
    _append({"kind": "version", "argv": sys.argv[1:]})
    sys.stdout.write(_VERSION + "\n")
    sys.stdout.flush()
    sys.exit(0)

_CLIENT_PID.write_text(str(os.getpid()), encoding="utf-8")
_STARTED.write_text("1", encoding="utf-8")
_append({"kind": "run", "argv": sys.argv[1:], "cwd": os.getcwd(),
         "pwd": os.environ.get("PWD")})

session_id = _option("--session") or ""
agent_id = _option("--agent") or "cdad-test-writer"

if variant == "row-not-idle-then-sleep":
    _write_row(session_id, agent_id, idle=False, with_final_text=False)
    time.sleep(_SLEEP_SECONDS)
elif variant == "sleep-no-store":
    time.sleep(_SLEEP_SECONDS)
elif variant == "succeeded":
    _write_row(session_id, agent_id, idle=True, with_final_text=True)
    _EXIT_TS.write_text(repr(time.time()), encoding="utf-8")
    sys.exit(0)
else:
    sys.stderr.write("u65fix5 fake binary: unknown variant %r\n" % variant)
    sys.exit(2)
'''

# sqlite3.connect audit hook: observes, from outside the process, WHICH
# connections were opened and WHEN (same principle as 006-001 T2's trace).
READ_TRACE_SITECUSTOMIZE = '''
import json
import os
import sys
import time

_LOG = os.environ.get("CDAD_U65_READ_TRACE")
_SELF = os.environ.get("CDAD_U65_READ_TRACE_SELF", "")


def _record(database):
    argv0 = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else ""
    if _SELF and argv0 == _SELF:
        return
    if not _LOG:
        return
    entry = {"ts": time.time(), "pid": os.getpid(), "argv0": argv0,
             "database": str(database)}
    try:
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\\n")
    except OSError:
        pass


def _hook(event, args):
    if event == "sqlite3.connect":
        _record(args[0] if args else None)


if hasattr(sys, "addaudithook"):
    sys.addaudithook(_hook)
'''


def tail(text: str, lines: int = 30) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


def snapshot_under(base: Path) -> dict:
    snapshot: dict = {}
    if not base.exists():
        return snapshot
    for path in sorted(base.rglob("*")):
        rel = path.relative_to(base).as_posix()
        if "__pycache__" in path.parts:
            continue
        snapshot[rel] = ("dir",) if path.is_dir() else (
            "file", path.stat().st_size, path.read_bytes())
    return snapshot


def snapshot_diff(before: dict, after: dict) -> list:
    diff = ["created: %s" % key for key in sorted(set(after) - set(before))]
    diff += ["removed: %s" % key for key in sorted(set(before) - set(after))]
    diff += ["modified: %s" % key for key in sorted(set(before) & set(after))
             if before[key] != after[key]]
    return diff


# -------------------------------------------------------------------- fixture


class U65WriteAheadCase(unittest.TestCase):
    """Disposable project + staged skill tree with the REAL `opencode` module,
    a redirected `XDG_CONFIG_HOME`/`HOME`, a fake binary, a disposable store
    with the installed version's REAL shape and a canonical packet published
    by `prepare`."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u65fix5-")
        self.base = Path(self._tmp.name).resolve()
        self.config_home = self.base / "config-home"
        self.config_home.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.fixture_dir = self.base / "fixture"
        self.fixture_dir.mkdir()

        self.stage = self.base / "stage"
        shutil.copytree(
            SKILL_DIR, self.stage,
            ignore=shutil.ignore_patterns("__pycache__"))
        self.scripts = self.stage / "scripts"
        self.entry = self.scripts / "cdad_dispatch.py"
        self.assertTrue(
            self.entry.is_file(),
            msg="precondición (fixture): no existe la entrada en el producto "
                "(se espera %s por U1a)"
                % ENTRY_PRODUCT.relative_to(REPO_ROOT))
        self.assertTrue(
            (self.scripts / MODULE_NAME).is_file(),
            msg="precondición (fixture): el módulo REAL del runtime (%s) no "
                "existe junto a la entrada; este RED no usa un módulo falso"
                % MODULE_NAME)

        self.agents_src = self.seed_agents()
        self.started_flag = self.fixture_dir / "started.flag"
        self.client_pid = self.fixture_dir / "client.pid"
        self.exit_ts_path = self.fixture_dir / "client-exit-ts.txt"
        self.calls_path = self.fixture_dir / "calls.jsonl"
        self.store_path = self.fixture_dir / "sessions.db"
        self.write_store([])
        self.fake_binary = self.write_fake_binary()
        self.write_runtimes()
        self.project = self.new_project()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- harness ------------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for name in ("OPENCODE_PASSWORD", "OPENCODE_SERVER_PASSWORD",
                     "CDAD_EXEC_CONFIG"):
            env.pop(name, None)
        return env

    def prepare_env(self) -> dict:
        env = self.env()
        env["CDAD_OPENCODE_AGENTS_DIR"] = str(self.agents_src)
        return env

    @staticmethod
    def output(proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout or "") + (proc.stderr or "")

    def run_cli(self, script: Path, args: list, *, env: dict | None = None,
                timeout: int = 180) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=str(REPO_ROOT), env=env or self.env(),
            capture_output=True, text=True, check=False, timeout=timeout)

    # -- fixture data -------------------------------------------------------

    def seed_agents(self) -> Path:
        """Copy of the repo's generated agents (`agents/cdad-*.md`) into a
        temporary source directory, copied without inspection (the same
        recipe as 005-009 T2 / 006-001 T1). It is what makes `prepare`
        publish the project-local derived agent the module checks."""
        source = self.base / "agents-src"
        source.mkdir(parents=True, exist_ok=True)
        for agent in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            shutil.copy(str(agent), str(source / agent.name))
        self.assertTrue(
            (source / "cdad-test-writer.md").is_file(),
            msg="precondición (fixture): no se pudo sembrar el agente del rol "
                "desde agents/cdad-*.md")
        return source

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "opencode-u65fake"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            FAKE_BINARY_SOURCE
            .replace("%VERSION%", json.dumps(FAKE_VERSION))
            .replace("%STORE%", json.dumps(str(self.store_path)))
            .replace("%MODEL%", json.dumps(ROW_MODEL))
            .replace("%USER_TEXT%", json.dumps(USER_TEXT))
            .replace("%FINAL_TEXT%", json.dumps(FINAL_TEXT))
            .replace("%SLEEP%", "60"),
            encoding="utf-8")
        path.chmod(0o755)
        return path

    def non_executable_binary(self) -> Path:
        """A file that exists but cannot be executed: the launch fails AFTER
        the write-ahead, so the termination must complete with `session:
        null` (PD-8) and no ledger rejection note (B-3)."""
        path = self.fixture_dir / "bin" / "opencode-u65-nox"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
        path.chmod(0o644)
        return path

    def set_variant(self, variant: str) -> None:
        (self.fixture_dir / "variant").write_text(
            variant + "\n", encoding="utf-8")

    def write_store(self, rows: list) -> Path:
        """Disposable store with the INSTALLED version's real schema (V-7
        extended): `time_created INTEGER NOT NULL` in epoch MILLISECONDS."""
        path = self.store_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        connection = sqlite3.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE session_v2 (%s)" % ", ".join(STORE_COLUMNS))
            connection.execute(
                "CREATE TABLE session_message (id TEXT PRIMARY KEY,"
                " session_id TEXT, type TEXT, seq INTEGER, data TEXT)")
            for row in rows:
                names = list(row)
                connection.execute(
                    "INSERT INTO session_v2 (%s) VALUES (%s)"
                    % (", ".join(names), ", ".join("?" * len(names))),
                    [row[name] for name in names])
            connection.commit()
        finally:
            connection.close()
        return path

    def write_store_row(self, session: str, *, idle: bool) -> None:
        now_ms = int(time.time() * 1000)
        connection = sqlite3.connect(str(self.store_path))
        try:
            connection.execute(
                "INSERT INTO session_v2 (id, parent_id, agent, model,"
                " time_created, time_idle, idle_outcome, directory)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (session, None, "cdad-test-writer", ROW_MODEL,
                 now_ms - 1000, now_ms if idle else None,
                 "succeeded" if idle else None, str(self.project["root"])))
            connection.commit()
        finally:
            connection.close()

    def store_row(self, session: str) -> dict | None:
        try:
            connection = sqlite3.connect(str(self.store_path))
            connection.row_factory = sqlite3.Row
            try:
                row = connection.execute(
                    "SELECT * FROM session_v2 WHERE id = ?", (session,)
                ).fetchone()
            finally:
                connection.close()
        except sqlite3.Error:
            return None
        return dict(row) if row is not None else None

    def store_rows(self) -> int:
        try:
            connection = sqlite3.connect(str(self.store_path))
            try:
                count = connection.execute(
                    "SELECT COUNT(*) FROM session_v2").fetchone()[0]
            finally:
                connection.close()
        except sqlite3.Error:
            return -1
        return int(count)

    def write_runtimes(self, *, binary: Path | None = None,
                       wait_timeout: int = 30) -> Path:
        """§2.6: the single source for the external path. The runtime id is
        `opencode`, so the REAL module next to the entry is resolved."""
        document = {
            "version": 1,
            "runtimes": {
                RUNTIME: {
                    "binary": str(binary or self.fake_binary),
                    "binary_version": FAKE_VERSION,
                    "mode": "standalone",
                    "auto": True,
                    "sessions_db": str(self.store_path),
                    "wait": {"timeout_seconds": wait_timeout},
                },
            },
        }
        path = self.config_home / "cdad" / "runtimes.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def new_project(self) -> dict:
        """Disposable project with a canonical packet published by `prepare`
        (and the derived agents published from the seeded source)."""
        root = self.base / "project"
        root.mkdir(parents=True, exist_ok=True)
        build_project(root)
        proc = subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "006-005 U6-5 fixture (test-writer/red)"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env=self.prepare_env())
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición (fixture): `prepare` no publicó el paquete "
                "(test-writer/red):\n%s" % tail(self.output(proc)))
        derived = root / ".opencode" / "agents" / "cdad-test-writer.md"
        self.assertTrue(
            derived.is_file(),
            msg="precondición (fixture): `prepare` no publicó el agente "
                "derivado del paquete (%s)" % derived)
        state = read_state(root)
        return {
            "root": root,
            "execution_id": state["execution"]["id"],
            "packet_id": state["active_packet"]["id"],
        }

    # -- invocations --------------------------------------------------------

    def dispatch_args(self) -> list:
        return [
            "dispatch",
            "--project-root", str(self.project["root"]),
            "--packet", self.project["packet_id"],
            "--runtime", RUNTIME,
            "--json",
        ]

    def run_dispatch(self, *, env_extra: dict | None = None
                     ) -> subprocess.CompletedProcess:
        env = self.env()
        env.update(env_extra or {})
        return subprocess.run(
            [sys.executable, str(self.entry), *self.dispatch_args()],
            cwd=str(self.project["root"]), env=env,
            capture_output=True, text=True, check=False, timeout=180)

    def start_dispatch(self, *, env_extra: dict | None = None
                       ) -> subprocess.Popen:
        """Start the entry in its OWN process group so the SIGKILL of the
        coordinator group leaves the fixture client alive (E4 premise)."""
        env = self.env()
        env.update(env_extra or {})
        return subprocess.Popen(
            [sys.executable, str(self.entry), *self.dispatch_args()],
            cwd=str(self.project["root"]), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True)

    def record_dispatch(self, attempt: str, doc: dict
                        ) -> subprocess.CompletedProcess:
        """The existing ledger command, used as the ONLY writer surface."""
        path = self.base / ("observation-%s.json" % attempt)
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return self.run_cli(PACKET_CLI, [
            "prepare",
            "--project-root", str(self.project["root"]),
            "--record-dispatch", self.project["packet_id"],
            "--attempt-id", attempt,
            "--input", str(path),
        ])

    def reconcile(self) -> subprocess.CompletedProcess:
        execution = (self.project["root"] / ".cdad" / "executions"
                     / self.project["execution_id"] / "execution.json")
        return self.run_cli(CONTINUITY_CLI, [
            "reconcile",
            "--project-root", str(self.project["root"]),
            "--execution-context", str(execution),
            "--packet", self.project["packet_id"],
            "--json",
        ])

    def disposition(self, resolution: str = "abandoned"
                    ) -> subprocess.CompletedProcess:
        return self.run_cli(PACKET_CLI, [
            "register-transition",
            "--project-root", str(self.project["root"]),
            "--transition", "disposition",
            "--packet", self.project["packet_id"],
            "--resolution", resolution,
        ])

    def validate_state(self) -> subprocess.CompletedProcess:
        return self.run_cli(PACKET_CLI, [
            "validate-state",
            "--project-root", str(self.project["root"]),
        ])

    def prepare_next(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(self.project["root"]),
             "--role", "test-writer", "--substage", "red",
             "--objective", "006-005 U6-5: next packet after the failed try"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env=self.prepare_env(), timeout=180)

    # -- process control ----------------------------------------------------

    def wait_for(self, predicate, *, timeout: float, interval: float = 0.01):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(interval)
        return None

    def crash_coordinator(self, proc: subprocess.Popen) -> None:
        """SIGKILL to the entry+module process group; the fixture client is in
        its own group and survives (measured)."""
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    def kill_client(self) -> None:
        """Kill the fixture client IF it is still the fixture client (guards
        against a reused pid after a normal exit)."""
        try:
            pid = int(self.client_pid.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return
        try:
            cmdline = Path("/proc/%d/cmdline" % pid).read_bytes()
        except OSError:
            return
        if self.fake_binary.name.encode() not in cmdline:
            return
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def track_client(self) -> None:
        self.addCleanup(self.kill_client)

    # -- observations -------------------------------------------------------

    def calls(self) -> list:
        if not self.calls_path.is_file():
            return []
        return [
            json.loads(line)
            for line in self.calls_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def run_calls(self) -> list:
        return [entry for entry in self.calls() if entry.get("kind") == "run"]

    def chosen_session(self) -> str:
        runs = self.run_calls()
        self.assertTrue(
            runs, msg="fixture: the fake client was never invoked with `run`")
        argv = runs[-1].get("argv") or []
        for index, token in enumerate(argv):
            if token == "--session" and index + 1 < len(argv):
                return argv[index + 1]
            if token.startswith("--session="):
                return token.split("=", 1)[1]
        self.fail(msg="fixture: the client invocation did not carry --session")

    def records(self) -> dict:
        base = dispatch_dir(self.project["root"], self.project["execution_id"])
        found: dict = {}
        if not base.is_dir():
            return found
        for path in sorted(base.glob("*.json")):
            if path.stem.startswith("."):
                continue
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if isinstance(doc, dict):
                found[path.stem] = doc
        return found

    def record_paths(self) -> dict:
        base = dispatch_dir(self.project["root"], self.project["execution_id"])
        return {path.stem: path for path in sorted(base.glob("*.json"))
                if not path.stem.startswith(".")}

    def provisional_records(self) -> dict:
        found = {}
        for stem, doc in self.records().items():
            provenance = doc.get("provenance")
            if isinstance(provenance, dict) and str(
                    provenance.get("session") or "").startswith(MARK):
                found[stem] = doc
        return found

    def single_record(self) -> tuple[str, dict]:
        records = self.records()
        self.assertEqual(
            len(records), 1,
            msg="PD-1: el despacho dejó %d registros I8 (se espera "
                "exactamente uno): %r" % (len(records), sorted(records)))
        stem = next(iter(records))
        return stem, records[stem]

    def envelope(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: la entrada no completó (rc=%s):\n%s"
                % (label, proc.returncode, tail(self.output(proc))))
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(msg="%s: stdout no es el sobre JSON declarado (§2.1):\n%s"
                          % (label, tail(proc.stdout)))
        self.assertIsInstance(
            out, dict, msg="%s: el sobre no es un objeto: %r" % (label, out))
        self.assertEqual(
            set(out), ENVELOPE_KEYS,
            msg="%s: el sobre no es exactamente el conjunto de claves "
                "declarado (§2.1): %s" % (label, sorted(out)))
        self.assertIn(
            out["termination"], TERMINATION_VOCABULARY,
            msg="%s: terminación fuera del vocabulario cerrado: %r"
                % (label, out["termination"]))
        return out

    def assert_record_identity(self, doc: dict, label: str) -> None:
        self.assertEqual(
            set(doc), I8_RECORD_KEYS,
            msg="%s/INV-8: la forma del registro I8 no es la cerrada "
                "aprobada: %s" % (label, sorted(doc)))
        self.assertEqual(doc.get("execution_id"),
                         self.project["execution_id"], msg=label)
        self.assertEqual(doc.get("packet_id"),
                         self.project["packet_id"], msg=label)
        self.assertEqual(doc.get("role"), "test-writer", msg=label)
        self.assertEqual(doc.get("substage"), "red", msg=label)
        self.assertEqual(doc.get("runtime"), RUNTIME, msg=label)
        self.assertTrue(
            str(doc.get("started_at") or "").strip(),
            msg="%s: el registro no declara `started_at`" % label)

    def assert_provisional_shape(self, doc: dict, label: str) -> None:
        """O-4: mark `write-ahead:` in front, pairs at the END
        (`row=unknown; store_reads=unknown; prior_check_reads=<n>`)."""
        self.assert_record_identity(doc, label)
        provenance = doc.get("provenance")
        self.assertIsInstance(
            provenance, dict,
            msg="%s: `provenance` no es un objeto: %r" % (label, provenance))
        source = str(provenance.get("session") or "")
        self.assertTrue(
            source.startswith(MARK),
            msg="%s/E4/PD-19 (U6-5): el registro provisional no empieza con "
                "la marca declarada %r: %r" % (label, MARK, source))
        self.assertTrue(
            source[len(MARK):].strip(),
            msg="%s: la marca provisional no nombra la observación: %r"
                % (label, source))
        self.assertRegex(
            source, PROVISIONAL_PAIRS_RE,
            msg="%s/O-4: el registro provisional no conserva la forma de "
                "§2.6 (marca delante y pares al final: row=unknown; "
                "store_reads=unknown; prior_check_reads=<n>): %r"
                % (label, source))
        self.assertIsNone(
            doc.get("model_reported"),
            msg="%s/E4/PD-19 (U6-5): el registro provisional debe dejar "
                "`model_reported` null (la fila aún no se observó): %r"
                % (label, doc.get("model_reported")))

    def assert_final_record(self, doc: dict, label: str) -> str:
        """The record is final (no mark) and carries the PD-3 termination
        pairs. Returns the `provenance.session` text."""
        self.assert_record_identity(doc, label)
        source = str((doc.get("provenance") or {}).get("session") or "")
        self.assertFalse(
            source.startswith(MARK),
            msg="%s/E4/PD-19 (U6-5): la terminación no completó el registro "
                "(sigue provisional, marca %r): %r" % (label, MARK, source))
        self.assertRegex(
            source, FINAL_PAIRS_RE,
            msg="%s/006-001 PD-3: el registro final no lleva todos los pares "
                "de procedencia de terminación (row, store_reads, "
                "prior_check_reads al final): %r" % (label, source))
        return source

    def assert_no_rejection_note(self, out: dict, doc: dict, label: str
                                 ) -> None:
        text = str(out.get("diagnosis") or "")
        provenance = doc.get("provenance")
        if isinstance(provenance, dict):
            text += "\n" + "\n".join(str(value) for value in provenance.values())
        lowered = text.lower()
        for literal in REJECTION_NOTE_LITERALS:
            self.assertNotIn(
                literal.lower(), lowered,
                msg="%s/E4/PD-19 (U6-5): la terminación lleva una nota de "
                    "rechazo del ledger (%r); la compleción única debe "
                    "reemplazar el registro sin una segunda escritura:\n%s"
                    % (label, literal, tail(text, 40)))

    # -- crash recovery (oracles 1 and 2) -----------------------------------

    def assert_recovers_after_crash(self, label: str) -> tuple[str, dict]:
        """E4/PD-19 (a)-(d): a provisional record exists; `reconcile` says
        `dispatched-unknown` (repeating is not authorized); `disposition`
        leaves the packet `failed` with `validate-state` VALID and the record
        STILL provisional; the next `prepare` proceeds."""
        provisional = self.provisional_records()
        self.assertEqual(
            len(self.records()), 1,
            msg="%s/PD-1: tras la caída hay %d registros I8 (se espera "
                "exactamente el provisional): %r"
                % (label, len(self.records()), sorted(self.records())))
        self.assertEqual(
            len(provisional), 1,
            msg="%s/E4/PD-19 (U6-5): el registro I8 no quedó provisional "
                "con la marca %r: %r"
                % (label, MARK,
                   {stem: (doc.get("provenance") or {}).get("session")
                    for stem, doc in self.records().items()}))
        stem = next(iter(provisional))
        doc = provisional[stem]
        self.assert_provisional_shape(doc, label)
        self.assertTrue(
            str(doc.get("session") or "").strip(),
            msg="%s/E4/PD-19 (U6-5): el registro provisional no lleva la "
                "sesión elegida (el chequeo de intento previo no la vería)"
                % label)

        reconciled = self.reconcile()
        self.assertEqual(
            reconciled.returncode, 0,
            msg="%s: `reconcile` falló (rc=%s):\n%s"
                % (label, reconciled.returncode,
                   tail(self.output(reconciled))))
        try:
            envelope = json.loads(reconciled.stdout)
        except json.JSONDecodeError:
            self.fail(msg="%s: `reconcile` no emitió el sobre JSON:\n%s"
                          % (label, tail(reconciled.stdout)))
        self.assertEqual(
            envelope.get("classification"), "dispatched-unknown",
            msg="%s/E4/PD-19 (d): con el registro write-ahead, `reconcile` "
                "debe clasificar `dispatched-unknown` (no autoriza repetir); "
                "vio %r" % (label, envelope.get("classification")))
        self.assertIs(
            envelope.get("repeat_effect"), False,
            msg="%s/E4/PD-19 (d): `repeat_effect` debe ser false; vio %r"
                % (label, envelope.get("repeat_effect")))

        disposed = self.disposition()
        self.assertEqual(
            disposed.returncode, 0,
            msg="%s/PD-19: la disposición del despacho sin recibo debe "
                "registrarse (rc=0); rc=%s:\n%s"
                % (label, disposed.returncode, tail(self.output(disposed))))
        state = read_state(self.project["root"])
        active = state.get("active_packet") or {}
        self.assertEqual(
            active.get("id"), self.project["packet_id"],
            msg="%s/PD-19 (a): la disposición no debe cambiar el paquete "
                "identificado: %r" % (label, active))
        self.assertEqual(
            active.get("status"), "failed",
            msg="%s/PD-19: el efecto del `disposition` es `status: failed`; "
                "vio %r" % (label, active.get("status")))

        validated = self.validate_state()
        self.assertEqual(
            validated.returncode, 0,
            msg="%s/PD-19: `validate-state` debe dar rc=0:\n%s"
                % (label, tail(self.output(validated))))
        self.assertIn(
            "VALID", self.output(validated),
            msg="%s/PD-19: `validate-state` no declaró VALID:\n%s"
                % (label, tail(self.output(validated))))

        after_disposition = self.provisional_records()
        self.assertEqual(
            len(after_disposition), 1,
            msg="%s/PD-19: la disposición no debe completar ni borrar el "
                "registro provisional del intento que no volvió: %r"
                % (label, sorted(self.records())))
        still = after_disposition[stem]
        self.assert_provisional_shape(still, label + " tras disposition")
        self.assertIsNone(
            still.get("model_reported"),
            msg="%s/E4/PD-19 (U6-5): el registro provisional no debe adquirir "
                "`model_reported` por la disposición: %r"
                % (label, still.get("model_reported")))

        prepared = self.prepare_next()
        self.assertEqual(
            prepared.returncode, 0,
            msg="%s/PD-19: tras `failed` el siguiente `prepare` debe "
                "proceder (rc=0); rc=%s:\n%s"
                % (label, prepared.returncode, tail(self.output(prepared))))
        new_state = read_state(self.project["root"])
        new_packet = new_state.get("active_packet") or {}
        self.assertNotEqual(
            new_packet.get("id"), self.project["packet_id"],
            msg="%s/PD-19: el `prepare` desbloqueado publica un paquete "
                "NUEVO: %r" % (label, new_packet))
        self.assertEqual(
            new_packet.get("status"), "prepared",
            msg="%s/PD-19: el paquete nuevo queda `prepared`: %r"
                % (label, new_packet))
        return stem, still

    # -- ledger observation documents --------------------------------------

    def observation(self, *, provisional: bool, session: str,
                    model_reported: str | None,
                    started_at: str = STARTED_AT) -> dict:
        if provisional:
            session_source = (
                MARK + " provisional; chosen by adapter; "
                "store=configured sessions_db; row=unknown; "
                "store_reads=unknown; prior_check_reads=1")
        else:
            session_source = (
                "chosen by adapter; store=configured sessions_db; "
                "row=present; store_reads=2; prior_check_reads=1")
        provenance = {
            "runtime": ("execution config (fixture): runtime; "
                        "mode_requested=standalone; "
                        "mode_effective=standalone"),
            "session": session_source,
        }
        if model_reported is not None:
            provenance["model_reported"] = "durable session row"
        return {
            "runtime": RUNTIME,
            "model_configured": None,
            "model_reported": model_reported,
            "session": session,
            "started_at": started_at,
            "provenance": provenance,
        }

    def record_bytes(self, attempt: str) -> bytes:
        return (dispatch_dir(self.project["root"],
                             self.project["execution_id"])
                / (attempt + ".json")).read_bytes()

    # -- sqlite3 connection trace (oracle 4) --------------------------------

    def install_read_trace(self) -> dict:
        trace_dir = self.fixture_dir / "pytrace"
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / "sitecustomize.py").write_text(
            READ_TRACE_SITECUSTOMIZE, encoding="utf-8")
        return {
            "pythonpath": str(trace_dir),
            "log_path": self.fixture_dir / "store-reads-trace.jsonl",
            "self_name": self.fake_binary.name,
        }

    def trace_env(self, trace: dict) -> dict:
        existing = os.environ.get("PYTHONPATH")
        pythonpath = trace["pythonpath"] + (
            os.pathsep + existing if existing else "")
        return {
            "PYTHONPATH": pythonpath,
            "CDAD_U65_READ_TRACE": str(trace["log_path"]),
            "CDAD_U65_READ_TRACE_SELF": trace["self_name"],
        }

    def read_trace_entries(self, trace: dict) -> list:
        path = trace["log_path"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


# --------------------------------------------------------- oracle 1 (E4/PD-19)


class TestU65CrashMidRun(U65WriteAheadCase):
    """E4/PD-19 (U6-5): the coordinator dies with the client alive; the
    provisional write-ahead record is the only way the consumers can see the
    attempt and recover without repeating effects."""

    def test_u65_crash_midrun_recovers_through_disposition(self) -> None:
        """E4/PD-19 (U6-5) — oracle 1 / D-U65-1, D-U65-2, D-U65-3, O-4: with
        the fixture client alive, the I8 record ALREADY exists, provisional
        (mark `write-ahead:` + pairs `row=unknown; store_reads=unknown;
        prior_check_reads=<n>` at the end), with the chosen session and
        `model_reported: null`. After SIGKILL to the coordinator group the
        record survives; `reconcile` ⇒ `dispatched-unknown` with
        `repeat_effect: false`; `disposition` ⇒ `failed` with `validate-state`
        VALID and the record STILL provisional; the next `prepare` proceeds.

        RED today: the record is written only at termination, so no I8 record
        exists while the client is alive (E4's defect)."""
        self.set_variant("row-not-idle-then-sleep")
        self.track_client()
        proc = self.start_dispatch()
        self.addCleanup(self.crash_coordinator, proc)

        started = self.wait_for(
            lambda: self.started_flag.is_file(), timeout=20)
        self.assertTrue(
            started,
            msg="fixture: el cliente falso no arrancó; no se puede observar "
                "la ventana de E4")
        session = self.chosen_session()

        records = self.records()
        self.assertEqual(
            len(records), 1,
            msg="E4/PD-19 (U6-5): con el cliente VIVO debe existir el "
                "registro I8 write-ahead (escrito antes de lanzarlo); se "
                "encontraron %d registros: %r"
                % (len(records), sorted(records)))
        provisional = self.provisional_records()
        self.assertEqual(
            len(provisional), 1,
            msg="E4/PD-19 (U6-5): el registro del intento no es provisional "
                "(no empieza con la marca %r): %r"
                % (MARK, {stem: (doc.get("provenance") or {}).get("session")
                          for stem, doc in records.items()}))
        doc = next(iter(provisional.values()))
        self.assert_provisional_shape(doc, "oráculo 1 (antes de la caída)")
        self.assertEqual(
            doc.get("session"), session,
            msg="E4/PD-19 (U6-5): el registro provisional debe llevar la "
                "sesión ELEGIDA (%r); persistió %r"
                % (session, doc.get("session")))

        row = self.store_row(session)
        self.assertIsNotNone(
            row, msg="fixture: el cliente falso no escribió su fila durable")
        self.assertIsNone(
            row.get("time_idle"),
            msg="fixture: la fila del cliente vivo no debe estar idle")

        self.crash_coordinator(proc)

        sessions = self.provisional_records()
        self.assertEqual(
            len(sessions), 1,
            msg="E4/PD-19 (U6-5): la caída del grupo del coordinador debe "
                "dejar el registro provisional en disco: %r"
                % sorted(self.records()))
        self.assert_recovers_after_crash("oráculo 1")


# ------------------------------------------------- oracle 2 (launch window)


class TestU65CrashBeforeLaunch(U65WriteAheadCase):
    """E4/PD-19 (U6-5): the same recovery path when the write-ahead record
    exists but the session row will NEVER exist (the pre-launch crash)."""

    def test_u65_crash_before_launch_recovers_through_disposition(self) -> None:
        """E4/PD-19 (U6-5) — oracle 2 / D-U65-1, D-U65-2, O-3(ii): the
        coordinator is killed as soon as a parseable provisional record
        appears; the fixture client variant performs NO store write and no
        effect, so the material state is the pre-launch crash state (record
        present, no row, no effects). The recovery is the oracle-1 sequence.

        Honest limit: the pre-launch instant itself is not instrumented (no
        implementation read); if the client happens to start in the gap it is
        killed before any effect, and the asserted state is the same.
        RED today: the client starts with no provisional record."""
        self.set_variant("sleep-no-store")
        self.track_client()
        inbox = self.project["root"] / ".cdad" / "inbox"
        inbox_before = snapshot_under(inbox)
        proc = self.start_dispatch()
        self.addCleanup(self.crash_coordinator, proc)

        deadline = time.monotonic() + 20
        record: dict | None = None
        while time.monotonic() < deadline:
            records = self.provisional_records()
            status = (read_state(self.project["root"]).get(
                "active_packet") or {}).get("status")
            if records and status == "dispatched":
                record = next(iter(records.values()))
                break
            if self.started_flag.is_file() and not records:
                self.fail(
                    msg="E4/PD-19 (U6-5): el cliente arrancó SIN el registro "
                        "I8 write-ahead (la marca debe escribirse antes de "
                        "lanzarlo); no hay provisional en disco")
            time.sleep(0.005)
        self.assertIsNotNone(
            record,
            msg="E4/PD-19 (U6-5): no apareció el registro I8 provisional "
                "antes de la caída (hoy se escribe recién al terminar)")
        self.assert_provisional_shape(record, "oráculo 2")

        self.crash_coordinator(proc)

        sessions = self.provisional_records()
        self.assertEqual(
            len(sessions), 1,
            msg="E4/PD-19 (U6-5): la caída en la ventana de lanzamiento "
                "debe dejar el provisional: %r" % sorted(self.records()))
        chosen = next(iter(sessions.values())).get("session")
        self.assertTrue(str(chosen or "").strip())
        self.assertIsNone(
            self.store_row(chosen),
            msg="fixture: la variante sin store no debe dejar fila; el "
                "oráculo 2 aserta el camino con una sesión cuya fila nunca "
                "existirá")
        self.assertEqual(
            self.store_rows(), 0,
            msg="fixture: el store descartable debe seguir sin filas")
        self.assertEqual(
            snapshot_diff(inbox_before, snapshot_under(inbox)), [],
            msg="E4/PD-19: una caída antes de cualquier efecto no debe "
                "escenificar nada bajo `.cdad/inbox`")
        self.assertFalse(
            (self.project["root"] / ".cdad" / "inbox" / "RESULT.json").is_file(),
            msg="E4/PD-19: no debe existir descriptor RESULT.json")

        self.assert_recovers_after_crash("oráculo 2")


# --------------------------------------------------------- oracle 3 (PD-9)


class TestU65ReDispatchLiveSession(U65WriteAheadCase):
    """E4/PD-19 (d)/PD-9 (006-001, INV-10): a re-dispatch must see the
    provisional record and the live row and block WITHOUT invoking `run`."""

    def test_u65_redispatch_with_live_session_is_blocked_without_run(
            self) -> None:
        """E4/PD-19 (U6-5) — oracle 3 / D-U65-3.4: after the crash, the
        provisional record names the chosen session and its row is live (no
        `time_idle`); re-dispatching the same packet terminates `blocked`
        with `session: null` and does NOT invoke the runtime binary again (no
        second writer).

        testfix: oraculo 3 alineado con D-U65-1 y el oraculo 8. El
        re-despacho bloqueado es OTRO despacho, y termina ANTES de su propio
        write-ahead (el intento previo vivo lo bloquea), así que aplica la
        última viñeta de D-U65-1: registra COMO HOY un registro final. PD-1
        es un registro POR DESPACHO, así que tras el re-despacho quedan DOS:
        (i) el provisional del primer despacho queda INTACTO (mismos bytes,
        marca `write-ahead:` y la sesión elegida); (ii) el registro nuevo es
        final (sin marca, `session: null`, procedencia de no despachado de
        §2.6). Es exactamente lo que asserta el oráculo 8.

        RED today: no provisional record exists and the re-dispatch invokes
        `run` again."""
        self.set_variant("row-not-idle-then-sleep")
        self.track_client()
        proc = self.start_dispatch()
        self.addCleanup(self.crash_coordinator, proc)
        started = self.wait_for(
            lambda: self.started_flag.is_file(), timeout=20)
        self.assertTrue(started, msg="fixture: el cliente falso no arrancó")

        provisional = self.provisional_records()
        self.assertEqual(
            len(provisional), 1,
            msg="E4/PD-19 (U6-5): el registro write-ahead debe existir con el "
                "cliente vivo; hay %r" % sorted(self.records()))
        chosen = next(iter(provisional.values())).get("session")
        self.assertTrue(
            str(chosen or "").strip(),
            msg="E4/PD-19 (U6-5): el provisional no lleva la sesión elegida")

        row = self.wait_for(
            lambda: self.store_row(chosen), timeout=10)
        self.assertIsNotNone(
            row, msg="fixture: el cliente no escribió su fila durable")
        self.assertIsNone(
            row.get("time_idle"),
            msg="fixture: la fila debe seguir viva (time_idle NULL)")

        self.crash_coordinator(proc)
        self.assertEqual(
            len(self.records()), 1,
            msg="E4/PD-19 (U6-5): la caída debe dejar UN registro: %r"
                % sorted(self.records()))
        provisional_before = self.provisional_records()
        self.assertEqual(
            len(provisional_before), 1,
            msg="E4/PD-19 (U6-5): la caída debe dejar UN provisional: %r"
                % sorted(self.records()))
        provisional_stem = next(iter(provisional_before))
        provisional_bytes = self.record_bytes(provisional_stem)
        runs_before = len(self.run_calls())
        self.assertEqual(runs_before, 1, msg="fixture: una sola invocación run")

        again = self.run_dispatch()
        out = self.envelope(again, "oráculo 3 (re-despacho con sesión viva)")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="E4/PD-19 (d)/PD-9: con la fila de la sesión viva, el "
                "re-despacho debe quedar `blocked` sin abrir un segundo "
                "escritor; vio %r" % out.get("termination"))
        self.assertIsNone(
            out.get("session"),
            msg="PD-8: la terminación previa al despacho mantiene `session` "
                "null; vio %r" % out.get("session"))
        self.assertEqual(
            len(self.run_calls()), runs_before,
            msg="E4/PD-19 (d)/PD-9: el re-despacho INVOCÓ el binario del "
                "runtime (`run`) pese al intento previo vivo; invocaciones: "
                "%r" % [entry.get("argv") for entry in self.run_calls()])
        after = self.records()
        self.assertEqual(
            len(after), 2,
            msg="D-U65-1/PD-1: el re-despacho bloqueado es OTRO despacho y "
                "termina ANTES de su write-ahead: registra COMO HOY un "
                "registro final propio junto al provisional del primer "
                "despacho; hay %r" % sorted(after))
        self.assertIn(
            provisional_stem, after,
            msg="E4/PD-19 (U6-5): el provisional del primer despacho debe "
                "seguir en disco; hay %r" % sorted(after))
        self.assertEqual(
            self.record_bytes(provisional_stem), provisional_bytes,
            msg="E4/PD-19 (U6-5): el registro provisional del primer "
                "despacho debe quedar INTACTO (mismos bytes) tras el "
                "re-despacho bloqueado")
        still = after[provisional_stem]
        self.assert_provisional_shape(
            still, "oráculo 3 (provisional del primer despacho)")
        self.assertEqual(
            still.get("session"), chosen,
            msg="E4/PD-19 (U6-5): el provisional intacto conserva la sesión "
                "elegida por el primer despacho (%r); persistió %r"
                % (chosen, still.get("session")))
        new_stems = [stem for stem in after if stem != provisional_stem]
        self.assertEqual(
            len(new_stems), 1,
            msg="D-U65-1: la terminación bloqueada debe dejar UN registro "
                "nuevo junto al provisional: %r" % sorted(after))
        terminal = after[new_stems[0]]
        source = self.assert_final_record(
            terminal, "oráculo 3 (terminación previa al write-ahead)")
        self.assertIsNone(
            terminal.get("session"),
            msg="006-001 PD-8: una terminación anterior al despacho declara "
                "`session: null`; vio %r" % terminal.get("session"))
        self.assertIn(
            "not dispatched", source,
            msg="006-001 §2.6: la terminación anterior al write-ahead "
                "declara la procedencia de no despachado (`not dispatched`): "
                "%r" % source)
        self.assertEqual(
            len(self.provisional_records()), 1,
            msg="E4/PD-19 (U6-5): solo el primer despacho queda provisional; "
                "la terminación nueva es final: %r"
                % {stem: (doc.get("provenance") or {}).get("session")
                   for stem, doc in self.provisional_records().items()})


# ---------------------------------------------------------- oracle 4 (PD-3)


class TestU65CompletedCompletion(U65WriteAheadCase):
    """PD-1/006-001 PD-3/D-ADP-2: a `completed` termination completes the
    SAME record once, with the observed model and the wait's exact reads."""

    def test_u65_completed_leaves_one_final_record_with_pd3_pairs(self) -> None:
        """E4/PD-19 (U6-5) — oracle 4 / D-U65-2 (B-1 closure): exactly ONE
        record, final (no `write-ahead:` mark), `model_reported` from the
        store row, `row=present`, and `store_reads` EQUAL to the traced reads
        after the client exited (006-001 PD-3, the assertion that must keep
        holding after the completion).

        Declared GUARD: GREEN today (the record is written at termination
        with those pairs); it must stay GREEN with the one-time completion."""
        self.set_variant("succeeded")
        self.write_runtimes(wait_timeout=5)
        trace = self.install_read_trace()

        proc = self.run_dispatch(env_extra=self.trace_env(trace))
        out = self.envelope(proc, "oráculo 4 (completed)")
        self.assertEqual(
            out.get("termination"), "completed",
            msg="precondición/oráculo 4: la corrida con fila idle y texto "
                "final debe terminar `completed`; vio %r"
                % out.get("termination"))
        stem, doc = self.single_record()
        source = self.assert_final_record(doc, "oráculo 4")
        session = self.chosen_session()
        self.assertEqual(
            doc.get("session"), session,
            msg="E4/PD-19 (U6-5)/PD-8: el registro final lleva la sesión "
                "elegida %r; persistió %r" % (session, doc.get("session")))
        self.assertEqual(
            doc.get("model_reported"), ROW_MODEL,
            msg="D-ADP-2: `model_reported` sale de `session_v2.model` de la "
                "fila (%r); persistió %r" % (ROW_MODEL,
                                             doc.get("model_reported")))
        self.assertRegex(
            source, r"row=present",
            msg="006-001 PD-3: el registro final de `completed` declara "
                "`row=present`: %r" % source)

        exit_ts = float(self.exit_ts_path.read_text(encoding="utf-8"))
        entries = self.read_trace_entries(trace)
        post_exit = [entry for entry in entries if entry["ts"] > exit_ts]
        self.assertTrue(
            post_exit,
            msg="fixture: la traza no registró lecturas posteriores a la "
                "salida del cliente (¿PYTHONPATH no se propagó? — fallo de "
                "fixture, no de comportamiento)")
        reported = int(re.search(r"store_reads=(\d+)", source).group(1))
        self.assertEqual(
            reported, len(post_exit),
            msg="006-001 PD-3/B-1: el `store_reads` del registro final (%d) "
                "debe coincidir con la traza de la espera (%d); la "
                "compleción no puede congelar los unknowns del write-ahead"
                % (reported, len(post_exit)))
        self.assertEqual(
            len(self.records()), 1,
            msg="PD-1: la compleción no agrega un segundo registro: %r"
                % sorted(self.records()))


# ----------------------------------------------------- oracle 5 (PD-8, PD-3)


class TestU65BinaryDoesNotStart(U65WriteAheadCase):
    """006-001 PD-8 (amended for the provisional record) / B-3: a client that
    cannot start completes the record with `session: null` and no rejection."""

    def test_u65_binary_that_does_not_start_completes_with_null_session(
            self) -> None:
        """E4/PD-19 (U6-5) — oracle 5a / D-U65-2 (B-3): the configured binary
        exists but cannot be executed ⇒ Popen fails AFTER the write-ahead; the
        termination completes the SAME record once: final (no mark),
        `session: null` (PD-8), `model_reported: null`, `row=absent`, and NO
        ledger rejection note (`worker record not written`, write-once, …),
        without invoking `run`.

        Declared GUARD: GREEN today (the final record already has session
        null and no rejection); it must stay GREEN with the completion."""
        self.write_runtimes(binary=self.non_executable_binary(), wait_timeout=5)
        proc = self.run_dispatch()
        out = self.envelope(proc, "oráculo 5a (binario que no arranca)")
        self.assertNotEqual(
            out.get("termination"), "completed",
            msg="E4/PD-19: un binario que no arranca no puede declarar "
                "entrega: %r" % out.get("termination"))
        self.assertIsNone(
            out.get("session"),
            msg="006-001 PD-8: si el binario no arranca, `session` sigue "
                "null; vio %r" % out.get("session"))
        self.assertEqual(
            len(self.run_calls()), 0,
            msg="E4/PD-19 (U6-5): el cliente no pudo arrancar; no debe "
                "haber una invocación `run` registrada: %r"
                % [entry.get("argv") for entry in self.run_calls()])
        _, doc = self.single_record()
        source = self.assert_final_record(doc, "oráculo 5a")
        self.assertIsNone(
            doc.get("session"),
            msg="PD-8 (enmendada para el registro provisional): el registro "
                "final declara `session: null` si el cliente no arrancó; "
                "persistió %r" % doc.get("session"))
        self.assertIsNone(
            doc.get("model_reported"),
            msg="sin fila no hay `model_reported` observado: %r"
                % doc.get("model_reported"))
        self.assertRegex(
            source, r"row=absent",
            msg="006-001 PD-3: el registro final declara `row=absent` "
                "cuando el cliente no arrancó: %r" % source)
        self.assertRegex(
            source, r"store_reads=unknown",
            msg="INV-9: lo no observado es `unknown`, nunca 0: %r" % source)
        self.assert_no_rejection_note(out, doc, "oráculo 5a")


class TestU65TimeoutWithoutRow(U65WriteAheadCase):
    """006-001 PD-3/PD-8: a wait timeout without a complete row keeps its
    termination provenance, and the record is final, not provisional."""

    def test_u65_timeout_without_row_keeps_the_termination_provenance(
            self) -> None:
        """E4/PD-19 (U6-5) — oracle 5b / D-U65-2: the client starts and
        writes NO row within the bounded wait ⇒ `timeout`; the SAME record is
        completed once (final, no mark), with the chosen session,
        `model_reported: null`, `row=absent|unknown` and
        `store_reads=<n>|unknown` — never the frozen `write-ahead:` mark
        (INV-9: unobserved is unknown, never 0).

        Declared GUARD: GREEN today; it must stay GREEN after the completion."""
        self.set_variant("sleep-no-store")
        # 008-001 PC-8: 5s deja presupuesto útil; el sujeto es la procedencia
        # del timeout, no el valor de la cota (el cliente duerme 60s).
        self.write_runtimes(wait_timeout=5)
        proc = self.run_dispatch()
        out = self.envelope(proc, "oráculo 5b (timeout sin fila)")
        self.assertEqual(
            out.get("termination"), "timeout",
            msg="precondición/oráculo 5b: sin fila completa la espera acotada "
                "termina `timeout`; vio %r" % out.get("termination"))
        _, doc = self.single_record()
        source = self.assert_final_record(doc, "oráculo 5b")
        self.assertIsNotNone(
            doc.get("session"),
            msg="PD-8: el cliente arrancó; el registro final lleva la sesión "
                "elegida (no null): %r" % doc.get("session"))
        self.assertEqual(
            doc.get("session"), out.get("session"),
            msg="PD-8: el registro y el sobre deben declarar la misma sesión: "
                "%r vs %r" % (doc.get("session"), out.get("session")))
        self.assertIsNone(
            doc.get("model_reported"),
            msg="sin fila idle no hay `model_reported` observado: %r"
                % doc.get("model_reported"))
        self.assertRegex(
            source, r"row=(?:absent|unknown)",
            msg="006-001 PD-3: el timeout sin fila completa declara "
                "`row=absent|unknown`: %r" % source)
        self.assertRegex(
            source, r"store_reads=(?:\d+|unknown)",
            msg="006-001 PD-3: el timeout declara el conteo real de lecturas "
                "o `unknown` si la espera no llegó a leer: %r" % source)
        self.assertNotRegex(
            source, r"store_reads=0(?:[;\s]|$)",
            msg="INV-9: lo no observado es `unknown`, nunca 0: %r" % source)
        self.assertEqual(
            len(self.run_calls()), 1,
            msg="fixture: una única invocación `run`")


# --------------------------------------------------------- oracle 6 (B-2)


class TestU65WriteAheadFailure(U65WriteAheadCase):
    """D-U65-1 fail-closed (B-2): if the write-ahead record fails, the client
    is never launched and the termination is `blocked` with the diagnosis."""

    def test_u65_write_ahead_failure_does_not_launch_the_client(self) -> None:
        """E4/PD-19 (U6-5) — oracle 6 / D-U65-1: the dispatch directory is
        read-only, so the write-ahead record cannot be written ⇒ NO client
        invocation, termination `blocked` with a diagnosis that names the
        failure, no record and no effects (the packet stays `prepared`).

        RED today: the registration failure adds a bounded note and the client
        IS launched (`run` invoked); the termination is not `blocked`."""
        self.set_variant("succeeded")
        dispatches = dispatch_dir(self.project["root"],
                                  self.project["execution_id"])
        dispatches.mkdir(parents=True, exist_ok=True)
        inbox = self.project["root"] / ".cdad" / "inbox"
        inbox_before = snapshot_under(inbox)
        os.chmod(dispatches, 0o500)
        try:
            proc = self.run_dispatch()
        finally:
            os.chmod(dispatches, 0o700)
        out = self.envelope(proc, "oráculo 6 (falla del write-ahead)")
        diagnosis = str(out.get("diagnosis") or "")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="D-U65-1 (B-2): si el registro write-ahead falla, la "
                "terminación es `blocked`; vio %r (%r)"
                % (out.get("termination"), diagnosis))
        self.assertTrue(
            diagnosis.strip(),
            msg="D-U65-1 (B-2): la terminación declara el diagnóstico de la "
                "falla (diagnóstico vacío)")
        self.assertRegex(
            diagnosis,
            r"(?i)(registr|record|write[- ]ahead|ledger|dispatch record)",
            msg="D-U65-1 (B-2): el diagnóstico no nombra la escritura del "
                "registro:\n%s" % tail(diagnosis, 40))
        self.assertRegex(
            diagnosis,
            r"(?i)(fail|error|cannot|could not|denied|permission|no se pudo"
            r"|fall[oa])",
            msg="D-U65-1 (B-2): el diagnóstico no nombra la falla:\n%s"
                % tail(diagnosis, 40))
        self.assertEqual(
            len(self.run_calls()), 0,
            msg="D-U65-1 (B-2): con el write-ahead fallido el cliente NO se "
                "lanza; invocaciones: %r"
                % [entry.get("argv") for entry in self.run_calls()])
        self.assertEqual(
            self.records(), {},
            msg="D-U65-1: no puede quedar un registro publicado por una "
                "escritura que falló: %r" % sorted(self.records()))
        state = read_state(self.project["root"])
        active = state.get("active_packet") or {}
        self.assertEqual(
            active.get("status"), "prepared",
            msg="D-U65-1: el paquete queda sin efectos (`prepared`), no "
                "`dispatched`: %r" % active.get("status"))
        self.assertEqual(
            snapshot_diff(inbox_before, snapshot_under(inbox)), [],
            msg="D-U65-1: la falla del write-ahead no produce efectos del rol")
        self.assertFalse(
            (self.project["root"] / ".cdad" / "inbox" / "RESULT.json").is_file(),
            msg="D-U65-1: no debe existir descriptor RESULT.json")


# --------------------------------------------------------- oracle 7 (ledger)


class TestU65LedgerCompletion(U65WriteAheadCase):
    """D-U65-2: the ONE completion is gated on the `write-ahead:` mark and the
    fixed identity; the write-once rule is otherwise unchanged."""

    def test_u65_second_completion_with_different_data_is_rejected(self) -> None:
        """E4/PD-19 (U6-5) — oracle 7a / D-U65-2: the first completion over a
        provisional record is accepted (the record becomes final with the
        observed data); a SECOND completion with different observation data
        is rejected and the final record's bytes do not change.

        Declared nuance (re-review FYI): a BYTE-IDENTICAL retry of the
        completion stays the ledger's existing idempotent no-op and is covered
        by `tests/test_004_002_t4_dispatch.py`; this test asserts the
        rejection of a *different* second completion, which is the declared
        rule.

        RED today: the first completion is rejected as «different observation
        data» because the mark has no meaning yet."""
        session = "ses-u65-ledger-0001"
        provisional = self.observation(
            provisional=True, session=session, model_reported=None)
        first = self.record_dispatch("att-u65-ledger", provisional)
        self.assertEqual(
            first.returncode, 0,
            msg="precondición: el ledger debe aceptar el registro "
                "provisional:\n%s" % tail(self.output(first)))

        completion = self.observation(
            provisional=False, session=session,
            model_reported="u65-ledger-model")
        accepted = self.record_dispatch("att-u65-ledger", completion)
        self.assertEqual(
            accepted.returncode, 0,
            msg="E4/PD-19 (U6-5)/D-U65-2: la PRIMERA compleción de un "
                "registro con la marca %r debe aceptarse (hoy se rechaza "
                "como «different observation data»):\n%s"
                % (MARK, tail(self.output(accepted))))
        final = self.records()["att-u65-ledger"]
        self.assert_final_record(final, "oráculo 7a")
        self.assertEqual(
            final.get("model_reported"), "u65-ledger-model",
            msg="D-U65-2: la compleción reemplaza la observación (model desde "
                "la fila): %r" % final.get("model_reported"))
        before = self.record_bytes("att-u65-ledger")

        second = self.observation(
            provisional=False, session=session,
            model_reported="u65-ledger-other")
        rejected = self.record_dispatch("att-u65-ledger", second)
        self.assertNotEqual(
            rejected.returncode, 0,
            msg="D-U65-2: una SEGUNDA compleción con datos distintos debe "
                "rechazarse (write-once):\n%s" % tail(self.output(rejected)))
        self.assertEqual(
            self.record_bytes("att-u65-ledger"), before,
            msg="D-U65-2: la segunda compleción rechazada no debe reescribir "
                "el registro final")

    def test_u65_completion_over_an_unmarked_record_is_rejected(self) -> None:
        """E4/PD-19 (U6-5) — oracle 7b / D-U65-2: a record WITHOUT the
        `write-ahead:` mark is already final; a completion payload over it is
        rejected and the record's bytes do not change. GREEN today (write-once)
        and must stay GREEN."""
        session = "ses-u65-final-0001"
        final = self.observation(
            provisional=False, session=session,
            model_reported="u65-final-model")
        recorded = self.record_dispatch("att-u65-final", final)
        self.assertEqual(
            recorded.returncode, 0,
            msg="precondición: el registro final debe aceptarse:\n%s"
                % tail(self.output(recorded)))
        before = self.record_bytes("att-u65-final")

        completion = self.observation(
            provisional=False, session=session,
            model_reported="u65-final-other")
        rejected = self.record_dispatch("att-u65-final", completion)
        self.assertNotEqual(
            rejected.returncode, 0,
            msg="D-U65-2: un registro SIN la marca %r es final y no admite "
                "compleción:\n%s" % (MARK, tail(self.output(rejected))))
        self.assertEqual(
            self.record_bytes("att-u65-final"), before,
            msg="D-U65-2: la compleción rechazada no debe reescribir el "
                "registro final")

    def test_u65_completion_changing_the_identity_is_rejected(self) -> None:
        """E4/PD-19 (U6-5) — oracle 7c / D-U65-2: identity (`execution_id`,
        `packet_id`, attempt, role, substage, runtime, `started_at`) is fixed;
        a completion whose `started_at` differs is rejected and the
        provisional record keeps its bytes. GREEN today (write-once) and must
        stay GREEN."""
        session = "ses-u65-identity-0001"
        provisional = self.observation(
            provisional=True, session=session, model_reported=None)
        recorded = self.record_dispatch("att-u65-identity", provisional)
        self.assertEqual(
            recorded.returncode, 0,
            msg="precondición: el registro provisional debe aceptarse:\n%s"
                % tail(self.output(recorded)))
        before = self.record_bytes("att-u65-identity")

        changed = self.observation(
            provisional=False, session=session,
            model_reported="u65-identity-model",
            started_at="2027-01-01T00:00:00Z")
        rejected = self.record_dispatch("att-u65-identity", changed)
        self.assertNotEqual(
            rejected.returncode, 0,
            msg="D-U65-2: una compleción que cambia la identidad "
                "(`started_at`) debe rechazarse:\n%s"
                % tail(self.output(rejected)))
        self.assertEqual(
            self.record_bytes("att-u65-identity"), before,
            msg="D-U65-2: la compleción con identidad distinta no debe "
                "reescribir el registro provisional")
        self.assertEqual(
            len(self.provisional_records()), 1,
            msg="D-U65-2: el registro provisional debe seguir provisional "
                "tras el rechazo")


# ------------------------------------------------ oracle 8 (pre-write-ahead)


class TestU65BeforeWriteAhead(U65WriteAheadCase):
    """D-U65-1 (last bullet): terminations BEFORE the write-ahead register as
    today, final and not provisional, and do not launch the client."""

    def test_u65_termination_before_write_ahead_is_not_provisional(
            self) -> None:
        """E4/PD-19 (U6-5) — oracle 8 / D-U65-1 + 006-001 PD-9: a live prior
        attempt (final record + row without `time_idle`) blocks the dispatch
        BEFORE the write-ahead. Observable: `blocked`, the runtime binary is
        NOT invoked, the existing final record keeps its bytes, and the
        termination registers AS TODAY a final record (no `write-ahead:`
        mark, `session: null`); NO provisional record appears.

        Declared GUARD: GREEN today (the prior check blocks and the
        termination registers a final record); it pins the ordering the
        amendment must preserve."""
        session = "ses-u65-prior-live-0001"
        prior = self.observation(
            provisional=False, session=session,
            model_reported="u65-prior-model")
        recorded = self.record_dispatch("att-u65-prior", prior)
        self.assertEqual(
            recorded.returncode, 0,
            msg="precondición: el registro previo debe aceptarse:\n%s"
                % tail(self.output(recorded)))
        before = self.record_bytes("att-u65-prior")
        self.write_store_row(session, idle=False)
        self.set_variant("succeeded")

        proc = self.run_dispatch()
        out = self.envelope(proc, "oráculo 8 (intento previo vivo)")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="006-001 PD-9: un intento previo vivo bloquea el despacho; "
                "vio %r" % out.get("termination"))
        self.assertEqual(
            len(self.run_calls()), 0,
            msg="006-001 PD-9: el intento previo vivo bloquea ANTES de "
                "invocar el binario; invocaciones: %r"
                % [entry.get("argv") for entry in self.run_calls()])
        self.assertEqual(
            self.record_bytes("att-u65-prior"), before,
            msg="D-U65-1: el registro final previo no se modifica en la "
                "terminación anterior al write-ahead")
        self.assertEqual(
            self.provisional_records(), {},
            msg="D-U65-1: no debe existir un registro con la marca %r en una "
                "terminación anterior al write-ahead" % MARK)
        records = self.records()
        self.assertEqual(
            len(records), 2,
            msg="D-U65-1/006-001 D-5: la terminación anterior al write-ahead "
                "registra COMO HOY un registro final propio, junto al "
                "previo: %r" % sorted(records))
        new_stems = [stem for stem in records if stem != "att-u65-prior"]
        self.assertEqual(len(new_stems), 1)
        terminal = records[new_stems[0]]
        self.assert_final_record(terminal, "oráculo 8 (terminación previa)")
        self.assertIsNone(
            terminal.get("session"),
            msg="006-001 PD-8: una terminación anterior al despacho declara "
                "`session: null`; vio %r" % terminal.get("session"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
