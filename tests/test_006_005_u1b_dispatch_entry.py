#!/usr/bin/env python3
"""006-005 U1b RED — single entry (`cdad_dispatch.py`: dispatch/record/
capabilities) and single registration per dispatch.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved, sha256
3a824be3…): the surface of §2.1, the integration contract of §2.2, the
transport-evidence correlation of §2.3 (with the O-3 discrimination
threshold), the per-path registration table of §2.4, the derived kind of §2.8,
the new-verb `--exec-config` sweep of §2.6/PD-9 (O-10), and the postconditions
PD-1, PD-2, PD-3, PD-4, PD-5, PD-6, PD-9 (new verbs) and PD-23 (native side);
INV-1, INV-2, INV-5, INV-8, INV-10, INV-14. Plan: U1b sheet (`plan.md` §3), the
A-1 rule (§4) and its `plan-tasks` block.

Oracle discipline (black box). The entry `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked AS A PROCESS against a disposable project (built by
the suite's `build_project` fixture) with a temporary `XDG_CONFIG_HOME`/`HOME`;
the user's real config is neither read nor written. Nothing of the
implementation is read or imported by this session: the observed surface is
exit codes, stdout/stderr, the published ledger records, the staged inbox and
descriptor, the durable receipt (through the EXISTING `receive` command) and
the fixture module's own log.

FIXTURE INTERFACE, DECLARED (the surface this RED pins; the entry must satisfy
it for the external path, and `record` must consume it for the native one):

* The runtime id of the fixture is `u1bfix`; its module is
  `cdad_delegate_u1bfix.py`, placed next to the staged entry — the module
  convention the product itself declares ("expected cdad_delegate_<id>.py next
  to this entry"). The entry must invoke that module for the external path.
* The fixture module answers `--observe` with the observable `session_v2`
  columns of the correlated candidate row of a disposable SQLite store (the
  `sessions_db` of the configuration it receives) or `null`: those are the
  store facts §2.3 makes the entry evaluate (padre/agente/momento/proyecto).
  The fixture's "store version" is the set of columns of that store, so a store
  with only `(id, agent)` reproduces the version observed today
  (`SESSION_V2_COLUMNS`) that cannot discriminate (O-3).
* The fixture module registers its OWN attempt (PD-1: the module is the single
  writer of the external path) by invoking the existing ledger command
  (`cdad_packet.py prepare --record-dispatch`) — the only writer of the ledger
  and of the state transition (INV-5); its envelope declares that attempt, and
  the entry must RELAY it, never replace it.
* `--capabilities` answers the five declared keys.

MAPPING (one test per numbered postcondition; each docstring names its PD):

  PD-1  test_pd1_external_dispatch_registers_one_attempt_relayed_by_the_entry
  PD-2  test_pd2_record_writes_only_under_dot_cdad_and_never_the_store
  PD-3  test_pd3_native_result_part_is_byte_exact_and_the_receipt_stays_pending
  PD-4  test_pd4_without_final_text_no_staging_no_descriptor_no_receipt
  PD-5  test_pd5_native_verified_when_a_discriminating_key_matches
        test_pd5_native_only_agent_evaluable_is_unknown_o3
        test_pd5_native_contradiction_is_a_rejection_naming_the_key
        test_pd5_native_session_outside_the_authorized_root_is_a_rejection
        test_pd5_native_nested_project_is_accepted_by_membership
        test_pd5_native_packet_without_agent_never_invents_the_agent
  PD-6  test_pd6_byte_exact_result_with_unverifiable_identity_keeps_no_session
  PD-9  test_pd9_exec_config_token_is_rejected_on_dispatch_record_capabilities
  PD-23 test_pd23_native_descriptor_kind_is_derived_from_role_and_substage

DECLARED DEPENDENCIES (no failing test is written for them here):
* PD-23 / the scribe: `_allowed_kinds("scribe", "memory")` admits `role-report`
  only after U7 (PD-26). U1b does NOT touch that table, so no scribe case is
  asserted here; the native derivation is exercised with test-writer (whose
  kind is already in the table) and with the architect (whose row has admitted
  `role-report` since 005-007 T4).
* PD-5 / «agent of another role ⇒ rejection»: the agent key is compared against
  `REQUEST.json.agent`, which PD-7/U1c writes. The packet of this unit carries
  no `agent`, so the contracted observable of that key here is `unknown` (never
  `cdad-<rol>`), and the discriminator cases use the keys that do not need PD-7
  (padre, proyecto). When U1c lands, the agent-contradiction case belongs to
  that unit's surface (the request admits the field).

A-1 (tests coupled to the surface this unit changes; replacement declared here,
per `plan.md` §4 — the four tests are reformulated in THIS RED, never in GREEN):

1. `tests/test_005_009_t1_interface.py` — REPLACED: the assertions in which the
   INTERFACE is the writer of the I8 record. NEW POSTCONDITION: the interface
   RELAYS the attempt its destination declared and does NOT register; the
   fixture destination (`testdest`) registers its OWN attempt, and the single
   record of the dispatch is the destination's (PD-1/D-ADP-2). REASON: with one
   registration per dispatch (D-14) the interface/worker split inside the
   external path no longer exists; the rest of the interface contract
   (byte-identical transport, envelope, fail-closed) is unchanged.
2. `tests/test_005_010_t1_durable_signal.py` (`:431-449` counted a worker
   record IN ADDITION to the interface's; `:536-543` asserted a null
   `model_reported` in the interface's record) — REPLACED by: ONE record per
   dispatch, whose stem is the attempt the envelope relays and whose
   `session`/`model_reported` come from the module's observation (the durable
   row); the assertions of the worker record are preserved, the interface-record
   ones are retired (PD-1/§2.4).
3. `tests/test_005_010_t4_integration.py` (`:480-486`, `:540-557`) — same
   replacement, same coupling.
4. `tests/test_005_010_reviewfix.py` (`:489-500`: "the NEW record that is NOT
   the interface's") — the localization of the I8 record becomes "the single
   new record of the dispatch"; the assertions about `model_reported` from the
   durable row do not change.

EXPECTED RED TODAY (declared, not accidental): the entry carries U1a (config +
migration) only. `dispatch` ends "the external transport is not available in
this build" (rc=1), `record`/`capabilities` are unavailable and `--attempt-id`
is not even a known flag, so every focal test fails on its FIRST behavioral
assertion (the missing record/staged part/receipt or the missing envelope), with
the declared message. `make --help`/the `--exec-config` sweep belong to U1a and
are already green (a guard, reported as such). No failure is an ImportError,
SyntaxError or fixture error.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    build_project,
    read_state,
    tree_snapshot,
)
from test_005_009_t1_interface import (
    OUTPUT_KEYS,
    STATE_FILE_REL,
    TERMINATION_VOCABULARY,
    dispatch_records,
    state_normalized,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

RUNTIME = "u1bfix"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

# §2.1: the envelope of `dispatch`/`record` is exactly the declared key set,
# with `termination` in the closed vocabulary (same source as the suite).
ENVELOPE_KEYS = OUTPUT_KEYS

# A byte-exact native result with deliberately awkward bytes: a normalizer
# (retipeo, summary, added trailing newline, CRLF rewrite) would change them.
NATIVE_PAYLOAD = (
    "# Native role report (006-005 U1b fixture)\n"
    "\n"
    "line with trailing spaces:   \n"
    "CRLF line\r\n"
    "last line without a final newline (byte-exactness matters)"
).encode("utf-8")

ATTEMPT_PD2 = "att-u1b-native-pd2-0001"
ATTEMPT_PD3 = "att-u1b-native-pd3-0001"
ATTEMPT_PD4 = "att-u1b-native-pd4-0001"
ATTEMPT_PD5 = "att-u1b-native-pd5-0001"
ATTEMPT_PD6 = "att-u1b-native-pd6-0001"
ATTEMPT_PD23_TW = "att-u1b-native-pd23-tw-0001"
ATTEMPT_PD23_ARCH = "att-u1b-native-pd23-ar-0001"
ATTEMPT_PD9 = "att-u1b-native-pd9-0001"

NATIVE_SESSION = "ses-native-u1b-0001"
NATIVE_PARENT = "ses-parent-u1b-0001"

EPIC_FIXTURE = "epic-004-single-source-planning"

# ------------------------------------------------------- fixture module source


U1B_MODULE_SOURCE = r'''#!/usr/bin/env python3
"""FIXTURE runtime module of tests/test_006_005_u1b_dispatch_entry.py.

NOT product: the fixture declares, for the RED, the interface the entry must
consume (see the test module's docstring). Declared behavior:

  --capabilities  -> the five declared keys (§2.2), JSON on stdout.
  --observe       -> the observable `session_v2` columns of the correlated
                     candidate row of the fixture store (the `sessions_db` of
                     the configuration the module receives, or the store next
                     to itself), or `null`, JSON on stdout.
  (default)       -> the external dispatch: registers ITS OWN attempt through
                     the co-located product command (the only ledger writer),
                     declares it in its envelope and logs the invocation.
"""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "u1b-fixture"
STORE = FIXTURE / "store.db"
LOG = FIXTURE / "module-log.jsonl"
OBSERVATION = FIXTURE / "observation.json"
FINAL_TEXT = FIXTURE / "final-text.md"
ATTEMPT = "att-u1b-fixture-0001"
SESSION = "ses-u1b-fixture-0001"
PACKET_MARK = "---cdad-packet-json"
CAPABILITIES = {
    "native_observation": True,
    "external_transport": True,
    "session_correlation": True,
    "version": "u1b-fixture 1.0",
    "reason": None,
}


def _option(name):
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _is_direct():
    return Path(sys.argv[0] or "").resolve().name == Path(__file__).name


def _log(entry):
    FIXTURE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True, default=str) + "\n")


def _config():
    value = _option("--exec-config") or os.environ.get("CDAD_EXEC_CONFIG")
    if value and Path(value).is_file():
        try:
            return json.loads(Path(value).read_text(encoding="utf-8"))
        except ValueError:
            return {}
    return {}


def _store_path():
    value = _config().get("sessions_db")
    return Path(value) if value else STORE


def _columns(connection):
    cursor = connection.execute("PRAGMA table_info(session_v2)")
    return [row[1] for row in cursor.fetchall()]


def _observe():
    store = _store_path()
    if not store.is_file():
        return None, "no-store"
    connection = sqlite3.connect("file:%s?mode=ro" % store, uri=True)
    try:
        columns = _columns(connection)
        if not columns:
            return None, "no-schema"
        session = _option("--session") or os.environ.get("CDAD_SESSION")
        parent = _option("--parent") or os.environ.get("CDAD_PARENT")
        rows = []
        if session:
            rows = connection.execute(
                "SELECT * FROM session_v2 WHERE id = ?", (session,)).fetchall()
        if not rows and parent and "parent_id" in columns:
            rows = connection.execute(
                "SELECT * FROM session_v2 WHERE parent_id = ?",
                (parent,)).fetchall()
        if not rows and not session and not parent:
            rows = connection.execute("SELECT * FROM session_v2").fetchall()
            if len(rows) != 1:
                return None, "ambiguous"
        if not rows:
            return None, "no-candidate"
        return dict(zip(columns, rows[0])), "correlated"
    finally:
        connection.close()


def _packet_transport():
    for token in sys.argv[1:]:
        candidate = Path(token)
        if candidate.is_file():
            try:
                data = candidate.read_bytes()
            except OSError:
                continue
            if data.lstrip().startswith(PACKET_MARK.encode("utf-8")):
                return data, str(candidate), "argv-file"
    for key in sorted(os.environ):
        if any(part in key.upper() for part in ("PACKET", "CDAD", "DELIVER")):
            candidate = Path(os.environ[key])
            if candidate.is_file():
                try:
                    data = candidate.read_bytes()
                except OSError:
                    continue
                if data.lstrip().startswith(PACKET_MARK.encode("utf-8")):
                    return data, str(candidate), "env:" + key
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.lstrip().startswith(PACKET_MARK):
                return data.encode("utf-8"), None, "stdin"
    except Exception:
        pass
    return None, None, "unfounded"


def _dispatch():
    root = _option("--project-root") or os.environ.get("CDAD_PROJECT_ROOT")
    packet = (_option("--packet") or _option("--packet-id")
              or os.environ.get("CDAD_PACKET"))
    packet_bytes, packet_path, transport = _packet_transport()
    if packet_path and (not root or not packet):
        parts = Path(packet_path).parts
        if packet is None and len(parts) >= 2:
            packet = parts[-2]
        if root is None and len(parts) >= 4:
            root = str(Path(*parts[:-3]))
    registered = None
    registration = None
    if root and packet:
        FIXTURE.mkdir(parents=True, exist_ok=True)
        runtime = (_option("--destination") or _config().get("runtime")
                   or RUNTIME_LITERAL)
        OBSERVATION.write_text(json.dumps({
            "runtime": runtime,
            "model_configured": None,
            "model_reported": None,
            "session": SESSION,
            "started_at": "2026-10-19T00:00:00Z",
            "provenance": {
                "runtime": "execution configuration (fixture module)",
                "model_configured": "delegation config: no model for this "
                                    "destination (fixture)",
                "model_reported": "fixture module holds no durable store",
                "session": "fixture transport: the module chose it",
                "started_at": "fixture module",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(HERE / "cdad_packet.py"), "prepare",
             "--project-root", str(root), "--record-dispatch", str(packet),
             "--attempt-id", ATTEMPT, "--input", str(OBSERVATION)],
            capture_output=True, text=True)
        registered = completed.returncode == 0
        registration = None if registered else (completed.stderr
                                                or completed.stdout)[-500:]
    else:
        registration = ("the invocation carried no project root / packet id: "
                        + repr(sys.argv[1:]))
    FINAL_TEXT.write_text(
        "# Fixture module final text (006-005 U1b)\n", encoding="utf-8")
    envelope = {
        "attempt": ATTEMPT,
        "session": SESSION,
        "termination": "completed",
        "delivery_ref": str(FINAL_TEXT),
        "diagnosis": None,
    }
    _log({
        "mode": "dispatch",
        "argv": sys.argv[1:],
        "cwd": os.getcwd(),
        "pwd": os.environ.get("PWD"),
        "project_root": root,
        "packet": packet,
        "transport": transport,
        "packet_sha256": (hashlib.sha256(packet_bytes).hexdigest()
                          if packet_bytes else None),
        "registered": registered,
        "registration": registration,
        "envelope": envelope,
    })
    return envelope


RUNTIME_LITERAL = %RUNTIME%

if "--capabilities" in sys.argv[1:]:
    _log({"mode": "capabilities", "argv": sys.argv[1:]})
    if _is_direct():
        sys.stdout.write(json.dumps(CAPABILITIES, sort_keys=True) + "\n")
        sys.stdout.flush()
    sys.exit(0)

if "--observe" in sys.argv[1:]:
    row, reason = _observe()
    _log({"mode": "observe", "argv": sys.argv[1:], "reason": reason,
          "row": row})
    if _is_direct():
        sys.stdout.write(
            (json.dumps(row, sort_keys=True) if row is not None else "null")
            + "\n")
        sys.stdout.flush()
    sys.exit(0)

envelope = _dispatch()
if _is_direct():
    sys.stdout.write(json.dumps(envelope, sort_keys=True) + "\n")
    sys.stdout.flush()
sys.exit(0)
'''


# -------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot_under(base: Path) -> dict:
    """Content-level snapshot of a tree (sizes + sha256), for write checks."""
    snapshot: dict = {}
    if not base.exists():
        return snapshot
    for path in sorted(base.rglob("*")):
        rel = path.relative_to(base).as_posix()
        if "__pycache__" in path.parts:
            continue
        snapshot[rel] = ("dir",) if path.is_dir() else (
            "file", path.stat().st_size, sha256_bytes(path.read_bytes()))
    return snapshot


def snapshot_diff(before: dict, after: dict) -> list:
    diff = ["created: %s" % key for key in sorted(set(after) - set(before))]
    diff += ["removed: %s" % key for key in sorted(set(before) - set(after))]
    diff += ["modified: %s" % key for key in sorted(set(before) & set(after))
             if before[key] != after[key]]
    return diff


# --------------------------------------------------------------------- fixture


class U1bEntryCase(unittest.TestCase):
    """Disposable project + a staged copy of the skill tree with the fixture
    runtime module next to the entry; a redirected `XDG_CONFIG_HOME`/`HOME`."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u1b-entry-")
        self.base = Path(self._tmp.name).resolve()
        self.config_home = self.base / "config-home"
        self.config_home.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()

        self.stage = self.base / "stage"
        shutil.copytree(
            SKILL_DIR, self.stage,
            ignore=shutil.ignore_patterns("__pycache__"))
        self.scripts = self.stage / "scripts"
        self.fixture_dir = self.scripts / "u1b-fixture"
        self.fixture_dir.mkdir(parents=True, exist_ok=True)
        (self.scripts / MODULE_NAME).write_text(
            U1B_MODULE_SOURCE.replace("%RUNTIME%", json.dumps(RUNTIME)),
            encoding="utf-8")
        self.entry = self.scripts / "cdad_dispatch.py"
        self.assertTrue(
            self.entry.is_file(),
            msg="precondición (fixture): no existe la entrada en el producto "
                "(se espera %s por U1a/U1b del plan)"
                % ENTRY_PRODUCT.relative_to(REPO_ROOT))

        self.project = self.new_project(role="test-writer", substage="red")
        self.write_runtimes()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- harness ------------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def run_entry(self, *args: str, cwd: Path | None = None
                  ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.entry), *args],
            cwd=str(cwd) if cwd is not None else str(self.project["root"]),
            env=self.env(), capture_output=True, text=True, check=False,
            timeout=300)

    @staticmethod
    def output(proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout or "") + (proc.stderr or "")

    # -- projects -----------------------------------------------------------

    def new_project(self, *, role: str, substage: str) -> dict:
        """Disposable project with a canonical packet published by `prepare`."""
        root = self.base / ("project-%s-%s" % (role, substage))
        root.mkdir(parents=True, exist_ok=True)
        build_project(root)
        # the architect sheet of the fixture authority reads the epic plan.
        plan = root / "docs" / "epics" / EPIC_FIXTURE / "plan.md"
        plan.parent.mkdir(parents=True, exist_ok=True)
        plan.write_text("# Fixture epic plan (006-005 U1b)\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(root), "--role", role,
             "--substage", substage,
             "--objective", "006-005 U1b fixture (%s/%s)" % (role, substage)],
            capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición (fixture): `prepare` no publicó el paquete "
                "(%s/%s):\n%s" % (role, substage, tail(self.output(proc))))
        state = read_state(root)
        return {
            "root": root,
            "role": role,
            "substage": substage,
            "execution_id": state["execution"]["id"],
            "packet_id": state["active_packet"]["id"],
        }

    def store_path(self) -> Path:
        return self.fixture_dir / "store.db"

    def write_runtimes(self) -> Path:
        """§2.6: the single source for the external path — the runtime section
        of `runtimes.json` under the CDAD user config (redirected)."""
        document = {
            "version": 1,
            "runtimes": {
                RUNTIME: {
                    "binary": str(self.fixture_dir / "bin"),
                    "binary_version": "u1b-fixture 1.0",
                    "mode": "standalone",
                    "auto": True,
                    "sessions_db": str(self.store_path()),
                    "wait": {"timeout_seconds": 30},
                },
            },
        }
        path = self.config_home / "cdad" / "runtimes.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def write_store(self, columns: list, rows: list) -> Path:
        """Disposable SQLite store: its COLUMNS are the fixture's «store
        version» (the keys §2.3 lets the entry evaluate)."""
        path = self.store_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        connection = sqlite3.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE session_v2 (%s)" % ", ".join(columns))
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

    # -- record / dispatch invocations -------------------------------------

    def dispatch(self, ctx: dict | None = None) -> subprocess.CompletedProcess:
        ctx = ctx or self.project
        return self.run_entry(
            "dispatch", "--project-root", str(ctx["root"]),
            "--packet", ctx["packet_id"], "--runtime", RUNTIME, "--json")

    def record(self, ctx: dict | None = None, *, attempt: str = ATTEMPT_PD4,
               native_result: Path | None = None, session: str | None = None,
               parent: str | None = None, since: str | None = None
               ) -> subprocess.CompletedProcess:
        ctx = ctx or self.project
        args = ["record", "--project-root", str(ctx["root"]),
                "--packet", ctx["packet_id"], "--attempt-id", attempt,
                "--runtime", RUNTIME, "--json"]
        if native_result is not None:
            args += ["--native-result", str(native_result)]
        if session is not None:
            args += ["--session", session]
        if parent is not None:
            args += ["--parent", parent]
        if since is not None:
            args += ["--since", since]
        return self.run_entry(*args, cwd=ctx["root"])

    def native_result_file(self, name: str = "native-result-u1b.md") -> Path:
        path = self.base / name
        path.write_bytes(NATIVE_PAYLOAD)
        return path

    # -- observations -------------------------------------------------------

    def envelope(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: la entrada no completó (rc=%s):\n%s"
                % (label, proc.returncode, tail(self.output(proc))))
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(msg="%s: stdout no es el sobre JSON declarado:\n%s"
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

    def json_or_none(self, proc: subprocess.CompletedProcess) -> dict | None:
        try:
            out = json.loads(proc.stdout)
        except (json.JSONDecodeError, TypeError):
            return None
        return out if isinstance(out, dict) else None

    def assert_record_surface(self, proc: subprocess.CompletedProcess,
                              label: str) -> None:
        """Gate of the rejection cases: a rejection is only evidence of the
        contracted behavior when the `record` verb and its flags exist. An
        argparse "unrecognized arguments"/"not available" answer is a missing
        surface, not the rejection under test (same guard as the suite's
        `No such file or directory` checks)."""
        text = self.output(proc)
        for token in ("unrecognized arguments", "not available in this build",
                      "invalid choice"):
            self.assertNotIn(
                token, text,
                msg="%s: RED inválida — el verbo `record` y sus banderas "
                    "(`--attempt-id`, `--native-result`, `--session`, "
                    "`--parent`, `--since`) todavía no existen (U1b): la "
                    "«rechazo» observada es un error de uso del argparse, no "
                    "el comportamiento bajo prueba:\n%s" % (label, tail(text)))

    def records(self, ctx: dict | None = None) -> dict:
        ctx = ctx or self.project
        return dispatch_records(ctx["root"], ctx["execution_id"])

    def new_records(self, before: dict, ctx: dict | None = None) -> dict:
        after = self.records(ctx)
        return {stem: path for stem, path in after.items()
                if stem not in set(before) and not stem.startswith(".")}

    def record_doc(self, stem: str, ctx: dict | None = None) -> dict:
        ctx = ctx or self.project
        base = (ctx["root"] / ".cdad" / "executions" / ctx["execution_id"]
                / "dispatches")
        path = base / (stem + ".json")
        self.assertTrue(
            path.is_file(),
            msg="el registro I8 declarado no existe en el ledger: %s"
                % path.relative_to(ctx["root"]).as_posix())
        return json.loads(path.read_text(encoding="utf-8"))

    def single_record(self, before: dict, ctx: dict | None = None) -> dict:
        """PD-1: exactly ONE attempt per dispatch; returns its document."""
        new = self.new_records(before, ctx)
        self.assertEqual(
            len(new), 1,
            msg="PD-1: el despacho dejó %d registros I8 nuevos (se espera "
                "exactamente uno: un solo intento por despacho, escrito por "
                "una sola capa): %r" % (len(new), sorted(new)))
        return self.record_doc(next(iter(new)), ctx)

    def descriptor(self, ctx: dict | None = None) -> dict:
        ctx = ctx or self.project
        path = ctx["root"] / ".cdad" / "inbox" / "RESULT.json"
        self.assertTrue(
            path.is_file(),
            msg="PD-3: el descriptor RESULT.json de la escenificación no "
                "existe en %s" % path.relative_to(ctx["root"]).as_posix())
        return json.loads(path.read_text(encoding="utf-8"))

    def receipt_dir(self, ctx: dict | None = None) -> Path:
        ctx = ctx or self.project
        return (ctx["root"] / ".cdad" / "runtime" / "results"
                / ctx["execution_id"] / ctx["packet_id"])

    def receive(self, ctx: dict, descriptor: Path) -> dict:
        """The re-entry protocol's receive step, through the EXISTING command
        (the receipt is the protocol's, not `record`'s, §2.1)."""
        root = ctx["root"]
        proc = subprocess.run(
            [sys.executable, str(RESULT_CLI), "receive",
             "--project-root", str(root),
             "--execution-context", str(root / ".cdad" / "executions"
                                          / ctx["execution_id"]
                                          / "execution.json"),
             "--packet", str(root / ".cdad" / "packets" / ctx["packet_id"]
                             / "PACKET.md"),
             "--request", str(root / ".cdad" / "packets" / ctx["packet_id"]
                              / "REQUEST.json"),
             "--descriptor", str(descriptor)],
            capture_output=True, text=True, cwd=str(REPO_ROOT))
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-3: el paso de recibo del protocolo de re-entry falló "
                "sobre el descriptor escenificado (rc=%s):\n%s"
                % (proc.returncode, tail(self.output(proc))))
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            receipt = self.receipt_dir(ctx) / "receipt.json"
            self.assertTrue(
                receipt.is_file(),
                msg="PD-3: el recibo durable no existe en %s"
                    % receipt.relative_to(root).as_posix())
            return json.loads(receipt.read_text(encoding="utf-8"))

    def module_log(self) -> list:
        path = self.fixture_dir / "module-log.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text(
            encoding="utf-8").splitlines() if line.strip()]

    def request_doc(self, ctx: dict | None = None) -> dict:
        ctx = ctx or self.project
        path = (ctx["root"] / ".cdad" / "packets" / ctx["packet_id"]
                / "REQUEST.json")
        return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- PD-1


class TestPd1ExternalDispatchSingleRegistration(U1bEntryCase):
    """PD-1/D-ADP-2: in the external path the MODULE registers its own attempt
    (one) and the entry relays it; the interface does not register."""

    def test_pd1_external_dispatch_registers_one_attempt_relayed_by_the_entry(
            self) -> None:
        """PD-1: `dispatch` leaves EXACTLY one new I8 record, produced by the
        runtime module (its own observation), and the envelope relays that
        attempt — the entry/delegate does not register a second one."""
        before = self.records()
        proc = self.dispatch()
        out = self.envelope(proc, "PD-1 vía externa")

        new = self.new_records(before)
        self.assertEqual(
            len(new), 1,
            msg="PD-1: el despacho externo dejó %d registros I8 nuevos (se "
                "espera UNO: el módulo registra su propio intento y la "
                "interfaz no registra): %r" % (len(new), sorted(new)))
        self.assertEqual(
            out["attempt"], next(iter(new)),
            msg="PD-1 (control negativo): el sobre no coincide con el registro "
                "del intento (sobre %r, registro %r) — la interfaz debe RELAYAR "
                "el attempt del módulo, no reemplazarlo"
                % (out["attempt"], sorted(new)))

        dispatch_log = [entry for entry in self.module_log()
                        if entry.get("mode") == "dispatch"]
        self.assertTrue(
            dispatch_log,
            msg="fixture/PD-1: el módulo del runtime nunca fue invocado por la "
                "vía externa (el planteamiento del transporte no ocurrió)")
        self.assertIs(
            dispatch_log[-1].get("registered"), True,
            msg="fixture/PD-1: el módulo del fixture no pudo registrar su "
                "propio intento (la entrada no le dio proyecto/paquete): "
                "registered=%r registration=%r"
                % (dispatch_log[-1].get("registered"),
                   dispatch_log[-1].get("registration")))


# ---------------------------------------------------------------- PD-2


class TestPd2NucleusIsNotASecondWriter(U1bEntryCase):
    """PD-2/INV-10: the core is not a second writer — the state only changes
    through the existing command's transaction, the store is never touched and
    every other write stays under `.cdad/`."""

    def test_pd2_record_writes_only_under_dot_cdad_and_never_the_store(
            self) -> None:
        """PD-2: `record` with a byte-exact native result writes only under
        `.cdad/` (plus the dispatch transaction of the existing command in
        `docs/.cdad-state.json`); the store's bytes are identical and no other
        state key changes."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer"}])
        store_before = self.store_path().read_bytes()
        root = self.project["root"]
        tree_before = tree_snapshot(root)
        state_before = read_state(root)

        proc = self.record(attempt=ATTEMPT_PD2,
                           native_result=self.native_result_file())
        self.envelope(proc, "PD-2")

        tree_after = tree_snapshot(root)
        changed = sorted(
            {rel for rel in set(tree_before) | set(tree_after)
             if tree_before.get(rel) != tree_after.get(rel)})
        unexpected = [rel for rel in changed
                      if not rel.startswith(".cdad/") and rel != STATE_FILE_REL]
        self.assertEqual(
            unexpected, [],
            msg="PD-2/INV-10: el núcleo escribió fuera de `.cdad/` (fuera de "
                "la transacción del comando en el estado): %r"
                % unexpected)
        self.assertEqual(
            self.store_path().read_bytes(), store_before,
            msg="PD-2/INV-5: el núcleo escribió el store (bytes distintos): la "
                "lectura del store es sólo del módulo y es sólo lectura")
        self.assertEqual(
            state_normalized(read_state(root)), state_normalized(state_before),
            msg="PD-2: el estado cambió más allá de la transacción del comando "
                "(status del paquete activo): %r -> %r"
                % (state_normalized(state_before), state_normalized(read_state(root))))


# ---------------------------------------------------------------- PD-3


class TestPd3NativeResultIsStagedByteExact(U1bEntryCase):
    """PD-3: with `--native-result` the staged part is byte-exact, the
    descriptor points at it and the receipt of the re-entry protocol stays
    `pending`."""

    def test_pd3_native_result_part_is_byte_exact_and_the_receipt_stays_pending(
            self) -> None:
        """PD-3: the staged part is byte-identical to the input (sha256 equal,
        no retipeo/summary/regeneration), the descriptor points at it and the
        receipt produced by the re-entry protocol is `semantic_status:
        pending` (receiving does not approve)."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer"}])
        source = self.native_result_file()
        proc = self.record(attempt=ATTEMPT_PD3,
                           native_result=source, session=NATIVE_SESSION)
        self.envelope(proc, "PD-3")

        root = self.project["root"]
        inbox = root / ".cdad" / "inbox"
        staged = [path for path in sorted(inbox.rglob("*"))
                  if path.is_file() and path.read_bytes() == NATIVE_PAYLOAD]
        self.assertTrue(
            staged,
            msg="PD-3: ninguna parte escenificada bajo `.cdad/inbox` conserva "
                "los bytes EXACTOS de la entrada (sha256 esperado %s): %r"
                % (sha256_bytes(NATIVE_PAYLOAD),
                   [path.name for path in sorted(inbox.rglob("*"))
                    if path.is_file()]))
        self.assertEqual(
            sha256_bytes(staged[0].read_bytes()), sha256_bytes(NATIVE_PAYLOAD),
            msg="PD-3: la parte escenificada no es byte-exacta")

        descriptor = self.descriptor()
        self.assertEqual(
            descriptor.get("packet_id"), self.project["packet_id"],
            msg="PD-3: el descriptor no liga el paquete despachado: %r"
                % descriptor.get("packet_id"))
        self.assertEqual(
            descriptor.get("execution_id"), self.project["execution_id"],
            msg="PD-3: el descriptor no liga la ejecución: %r"
                % descriptor.get("execution_id"))
        parts = descriptor.get("parts")
        self.assertIsInstance(
            parts, list,
            msg="PD-3: el descriptor no declara `parts`: %r" % (parts,))
        located = []
        for part in parts:
            rel = part.get("staged_path") or part.get("path")
            if not isinstance(rel, str):
                continue
            candidate = root / rel
            if candidate.is_file() and candidate.read_bytes() == NATIVE_PAYLOAD:
                located.append(candidate)
        self.assertTrue(
            located,
            msg="PD-3: el descriptor no apunta a la parte byte-exacta "
                "(parts=%r)" % (parts,))

        receipt = self.receive(self.project, inbox / "RESULT.json")
        self.assertEqual(
            receipt.get("semantic_status"), "pending",
            msg="PD-3/INV-5: el recibo de la entrega nativa no queda "
                "`pending` (recibir no aprueba): %r"
                % receipt.get("semantic_status"))


# ---------------------------------------------------------------- PD-4


class TestPd4WithoutFinalTextThereIsNoDelivery(U1bEntryCase):
    """PD-4/INV-1: without final text there is no delivery — nothing is
    staged, no `RESULT.json`, no `receive`; the attempt IS registered and the
    envelope declares the fact."""

    def test_pd4_without_final_text_no_staging_no_descriptor_no_receipt(
            self) -> None:
        """PD-4: `record` without `--native-result` registers the attempt
        (one) and the envelope declares it, but stages nothing under
        `.cdad/inbox`, writes no descriptor and leaves no receipt (nothing
        fabricates a delivery)."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer"}])
        root = self.project["root"]
        inbox_before = snapshot_under(root / ".cdad" / "inbox")
        self.assertFalse(
            (root / ".cdad" / "inbox" / "RESULT.json").is_file(),
            msg="precondición (fixture): el descriptor existe antes del caso")
        before = self.records()

        proc = self.record(attempt=ATTEMPT_PD4, session=NATIVE_SESSION)
        out = self.envelope(proc, "PD-4")

        self.assertEqual(
            out["attempt"], ATTEMPT_PD4,
            msg="PD-4: el sobre no declara el intento registrado: %r"
                % out.get("attempt"))
        self.assertIn(
            ATTEMPT_PD4, self.records(),
            msg="PD-4: el intento no quedó registrado en el ledger (el intento "
                "se registra aunque no haya entrega): %r"
                % sorted(set(self.records()) - set(before)))
        self.assertFalse(
            (root / ".cdad" / "inbox" / "RESULT.json").is_file(),
            msg="PD-4/INV-1: sin texto final se escribió un descriptor "
                "RESULT.json (no hay entrega que declarar)")
        self.assertEqual(
            snapshot_diff(inbox_before, snapshot_under(root / ".cdad" / "inbox")),
            [],
            msg="PD-4: sin texto final se escenificó algo bajo `.cdad/inbox` "
                "(nunca se fabrica una entrega)")
        receipt = self.receipt_dir() / "receipt.json"
        self.assertFalse(
            receipt.is_file(),
            msg="PD-4/INV-1: sin texto final hay un recibo (%s): `record` no "
                "invoca receive y nada fabrica la entrega"
                % receipt.relative_to(root).as_posix())
        self.assertNotEqual(
            out["termination"], "completed",
            msg="PD-4: sin texto final la terminación no puede declarar "
                "entrega: %r" % out["termination"])
        self.assertTrue(
            out.get("diagnosis"),
            msg="PD-4: el sobre no declara el hecho (diagnóstico vacío)")


# ---------------------------------------------------------------- PD-5


class TestPd5NativeCorrelation(U1bEntryCase):
    """PD-5/§2.3/INV-2: the native association is proven with the store's
    observable keys, with the O-3 discrimination threshold; `unknown` when no
    discriminating key is evaluable, rejection (never `unknown`, never an
    accepted delivery) when an evaluable key contradicts, and the project is
    corroborated by MEMBERSHIP (never a rigid equality)."""

    def test_pd5_native_verified_when_a_discriminating_key_matches(self) -> None:
        """PD-5 (verificada): with a discriminating key (padre) evaluated and
        matching, the attempt is persisted with the OBSERVED session — the id
        the STORE carries, which the invocation never declares."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "parent_id TEXT"],
            [{"id": NATIVE_SESSION, "parent_id": NATIVE_PARENT}])
        before = self.records()
        proc = self.record(attempt=ATTEMPT_PD5, parent=NATIVE_PARENT)
        out = self.envelope(proc, "PD-5 verificada")
        record = self.single_record(before)
        self.assertEqual(
            out["attempt"], ATTEMPT_PD5,
            msg="PD-5 (vía nativa): el sobre no declara el intento registrado")
        self.assertEqual(
            record["session"], NATIVE_SESSION,
            msg="PD-5 (verificada): el intento no se persiste con la sesión "
                "OBSERVADA (padre coincidente, llave discriminante evaluada; "
                "el id sale del store, la invocación no lo declara): "
                "%r != %r" % (record.get("session"), NATIVE_SESSION))

    def test_pd5_native_only_agent_evaluable_is_unknown_o3(self) -> None:
        """PD-5/O-3: with a store version that exposes only `agent` (the
        version observed today) two concurrent native dispatches of the same
        role cannot be told apart: neither session is accredited — the result
        is `unknown`, never «verificada», and the diagnosis names the missing
        discriminating key."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": "ses-conc-a", "agent": "cdad-test-writer"},
             {"id": "ses-conc-b", "agent": "cdad-test-writer"}])
        before = self.records()
        proc = self.record(attempt=ATTEMPT_PD5, session="ses-conc-a",
                           parent=NATIVE_PARENT)
        out = self.envelope(proc, "PD-5 O-3")
        record = self.single_record(before)
        self.assertIn(
            record["session"], (None, "unknown"),
            msg="PD-5/O-3: con sólo «agente» evaluable el resultado es "
                "`unknown` (nunca «verificada»): se persiste %r"
                % record.get("session"))
        self.assertNotIn(
            record["session"], ("ses-conc-a", "ses-conc-b"),
            msg="PD-5/O-3: dos despachos nativos concurrentes del mismo rol "
                "comparten agente: NINGUNA de las dos sesiones se acredita "
                "como la del intento, pero se acreditó %r"
                % record.get("session"))
        self.assertRegex(
            self.output(proc),
            r"(?i)parent|padre|momento|moment|proyect|proyecto|directory|directorio",
            msg="PD-5/O-3: el diagnóstico no nombra la llave discriminante que "
                "falta:\n%s" % tail(self.output(proc)))

    def test_pd5_native_contradiction_is_a_rejection_naming_the_key(self) -> None:
        """PD-5 (verificada e incorrecta): an evaluable key that contradicts
        (the row's `parent_id` is not the declared parent) is a REJECTION that
        names the key — never `unknown`, never an accepted delivery."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "parent_id TEXT"],
            [{"id": NATIVE_SESSION, "parent_id": "ses-otro-parent"}])
        proc = self.record(attempt=ATTEMPT_PD5, session=NATIVE_SESSION,
                           parent=NATIVE_PARENT)
        text = self.output(proc)
        self.assert_record_surface(proc, "PD-5 contradicción (padre)")
        self.assertRegex(
            text, r"(?i)parent|padre",
            msg="PD-5 (rechazo): el rechazo no nombra la llave contradictoria "
                "(parent):\n%s" % tail(text))
        out = self.json_or_none(proc)
        if out is not None:
            self.assertNotEqual(
                out.get("termination"), "unknown",
                msg="PD-5: una contradicción evaluable es RECHAZO, nunca "
                    "`unknown` (§2.3): %r" % out.get("termination"))
            self.assertNotEqual(
                out.get("termination"), "completed",
                msg="PD-5: una contradicción evaluable nunca acepta la entrega: "
                    "%r" % out.get("termination"))
        else:
            self.assertNotEqual(
                proc.returncode, 0,
                msg="PD-5: la contradicción evaluable no falló cerrado:\n%s"
                    % tail(text))
        for stem in self.records():
            self.assertNotEqual(
                self.record_doc(stem).get("session"), NATIVE_SESSION,
                msg="PD-5: el rechazo acreditó igual la sesión contradictoria "
                    "(%r) en el registro %r" % (NATIVE_SESSION, stem))

    def test_pd5_native_session_outside_the_authorized_root_is_a_rejection(
            self) -> None:
        """PD-5 (proyecto): a session whose directory is OUTSIDE the
        authorized root of the packet is a rejection that names the key —
        the project is corroborated, so a stranger directory can never be
        accredited."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "directory TEXT"],
            [{"id": NATIVE_SESSION,
              "directory": str(self.base / "otra-carpeta")}])
        proc = self.record(attempt=ATTEMPT_PD5, session=NATIVE_SESSION)
        text = self.output(proc)
        self.assert_record_surface(proc, "PD-5 rechazo (proyecto)")
        self.assertRegex(
            text,
            r"(?i)proyect|project|directory|directorio|ra[íi]z|root",
            msg="PD-5 (rechazo): el rechazo no nombra la llave contradictoria "
                "(proyecto/directorio):\n%s" % tail(text))
        out = self.json_or_none(proc)
        if out is not None:
            self.assertNotIn(
                out.get("termination"), ("unknown", "completed"),
                msg="PD-5: un directorio fuera de la raíz es RECHAZO, no "
                    "`unknown` ni entrega aceptada: %r" % out.get("termination"))
        else:
            self.assertNotEqual(
                proc.returncode, 0,
                msg="PD-5: el directorio fuera de la raíz no falló cerrado:\n%s"
                    % tail(text))
        for stem in self.records():
            self.assertNotEqual(
                self.record_doc(stem).get("session"), NATIVE_SESSION,
                msg="PD-5: se acreditó una sesión fuera de la raíz autorizada")

    def test_pd5_native_nested_project_is_accepted_by_membership(self) -> None:
        """PD-5/INV-15: the project is corroborated BY MEMBERSHIP — the
        authorized root is the session's directory or one of its ancestors —
        so a nested layout (and the coordinator started from another folder)
        is accepted; there is no rigid `directory == root`."""
        root = self.project["root"]
        for directory in (str(root), str(root / "nested" / "deep")):
            with self.subTest(directory=directory):
                self.write_store(
                    ["id TEXT PRIMARY KEY", "directory TEXT"],
                    [{"id": NATIVE_SESSION, "directory": directory}])
                before = self.records()
                proc = self.record(attempt=ATTEMPT_PD5)
                out = self.envelope(proc, "PD-5 pertenencia %s" % directory)
                record = self.single_record(before)
                self.assertEqual(
                    record["session"], NATIVE_SESSION,
                    msg="PD-5/INV-15: la raíz autorizada es la del directorio "
                        "de la sesión o su ancestro (pertenencia, nunca "
                        "igualdad rígida): con directory=%r se persistió %r"
                        % (directory, record.get("session")))

    def test_pd5_native_packet_without_agent_never_invents_the_agent(
            self) -> None:
        """PD-5/§2.3: a packet prepared before PD-7 carries no `agent`, so the
        agent key is `unknown` — never `cdad-<rol>`. The observable is
        `unknown` (no accredited session) and a diagnosis naming the key."""
        request = self.request_doc()
        self.assertNotIn(
            "agent", request,
            msg="precondición (declarada): esta unidad NO depende de PD-7; el "
                "paquete del fixture no declara `agent` (%r)" % sorted(request))
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT", "parent_id TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer",
              "parent_id": NATIVE_PARENT}])
        before = self.records()
        proc = self.record(attempt=ATTEMPT_PD5, parent=NATIVE_PARENT)
        out = self.envelope(proc, "PD-5 sin agente")
        record = self.single_record(before)
        self.assertIn(
            record["session"], (None, "unknown"),
            msg="PD-5: sin `agent` en el paquete la llave «agente» es "
                "`unknown` (nunca `cdad-<rol>`), aunque el padre coincida: se "
                "persiste %r" % record.get("session"))
        self.assertRegex(
            self.output(proc), r"(?i)agent|agente",
            msg="PD-5: el diagnóstico no nombra la llave no evaluable "
                "(«agente»):\n%s" % tail(self.output(proc)))
        self.assertNotEqual(
            record.get("session"), NATIVE_SESSION,
            msg="PD-5: sin la llave «agente» evaluable no hay acreditación "
                "positiva (la identidad del rol se detecta, no se supone)")


# ---------------------------------------------------------------- PD-6


class TestPd6UnverifiableIdentityKeepsNoSession(U1bEntryCase):
    """PD-6: with a byte-exact native result but an identity that cannot be
    verified, the delivery is persisted with `session: null` and a `provenance`
    that declares it — a session value is never invented."""

    def test_pd6_byte_exact_result_with_unverifiable_identity_keeps_no_session(
            self) -> None:
        """PD-6/INV-2: the store exposes only `agent` (no discriminating key
        ⇒ `unknown`), the native result is byte-exact: the delivery exists but
        the attempt carries `session: null` with the declared provenance, and
        the observed session id never appears as an accredited value."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer"}])
        before = self.records()
        proc = self.record(attempt=ATTEMPT_PD6, session=NATIVE_SESSION,
                           native_result=self.native_result_file())
        self.envelope(proc, "PD-6")
        record = self.single_record(before)

        self.assertIsNone(
            record.get("session"),
            msg="PD-6: la identidad no verificable se persiste con "
                "`session: null` (nunca un valor de sesión inventado): %r"
                % record.get("session"))
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict,
            msg="PD-6/INV-8: el `provenance` del intento no es un objeto: %r"
                % (provenance,))
        source = provenance.get("session")
        self.assertIsInstance(
            source, str,
            msg="PD-6: el `provenance` no declara la procedencia de `session` "
                "(que la identidad no se pudo verificar): %r" % (source,))
        self.assertTrue(
            source.strip(),
            msg="PD-6: la procedencia declarada de `session` está vacía")

        root = self.project["root"]
        staged = [path for path in sorted((root / ".cdad" / "inbox").rglob("*"))
                  if path.is_file() and path.read_bytes() == NATIVE_PAYLOAD]
        self.assertTrue(
            staged,
            msg="PD-6: la garantía menor exige la entrega byte-exacta del "
                "resultado nativo (no se escenificó ninguna parte)")


# ---------------------------------------------------------------- PD-9


class TestPd9NewVerbsRejectTheRetiredToken(U1bEntryCase):
    """PD-9/§2.6/D-11 (O-10): the `--exec-config` token (both forms) is a
    usage error before any effect in EVERY verb, including the ones U1b adds;
    the sweep is of `argv`, by exact token, before the verb is parsed."""

    def test_pd9_exec_config_token_is_rejected_on_dispatch_record_capabilities(
            self) -> None:
        """PD-9/O-10: on the explicit `dispatch`, on `record` and on
        `capabilities`, both token forms ⇒ rc≠0 with the single migration
        diagnostic naming `runtimes.json`, before any write."""
        legacy = self.base / "legacy-exec-config-u1b.json"
        legacy.write_text(
            json.dumps({"binary": "/fixture/legacy-u1b"}, indent=2) + "\n",
            encoding="utf-8")
        legacy_bytes = legacy.read_bytes()
        for verb in ("dispatch", "record", "capabilities"):
            for form in (["--exec-config", str(legacy)],
                         ["--exec-config=%s" % legacy]):
                with self.subTest(verb=verb, form=form[0]):
                    args = [verb]
                    if verb in ("dispatch", "record"):
                        args += ["--project-root", str(self.project["root"]),
                                 "--packet", self.project["packet_id"],
                                 "--runtime", RUNTIME]
                    else:
                        args += ["--runtime", RUNTIME]
                    if verb == "record":
                        args += ["--attempt-id", ATTEMPT_PD9]
                    before = snapshot_under(self.base)
                    proc = self.run_entry(*args, *form)
                    text = self.output(proc)
                    self.assertNotEqual(
                        proc.returncode, 0,
                        msg="PD-9/D-11: `%s` en `%s` debe ser error de uso "
                            "(rc=%s):\n%s"
                            % (form[0], verb, proc.returncode, tail(text)))
                    self.assertIn(
                        "runtimes.json", text,
                        msg="PD-9/D-11: el rechazo de `%s` en `%s` no trae el "
                            "diagnóstico de migración que nombra "
                            "`runtimes.json`:\n%s" % (form[0], verb, tail(text)))
                    self.assertEqual(
                        snapshot_diff(before, snapshot_under(self.base)), [],
                        msg="PD-9/D-11: el rechazo de `%s` en `%s` escribió "
                            "antes de fallar" % (form[0], verb))
                    self.assertEqual(
                        legacy.read_bytes(), legacy_bytes,
                        msg="PD-9/D-11: el rechazo de `%s` en `%s` tocó el "
                            "documento heredado" % (form[0], verb))


# ---------------------------------------------------------------- PD-23


class TestPd23NativeDescriptorKind(U1bEntryCase):
    """PD-23/§2.8/INV-14 (native side): the descriptor `record` stages declares
    the kind DERIVED from the packet's role and substage — never a hardcoded
    constant. `_allowed_kinds` is not touched by this unit."""

    def test_pd23_native_descriptor_kind_is_derived_from_role_and_substage(
            self) -> None:
        """PD-23 (lado nativo): test-writer/red ⇒ `test-writer-role-report`;
        architect/draft ⇒ `role-report` (the row the table has admitted since
        005-007 T4). Declared dependency: the scribe row (`role-report`) needs
        U7/PD-26, so no scribe case is asserted here (the table is not touched
        by U1b)."""
        self.write_store(
            ["id TEXT PRIMARY KEY", "agent TEXT"],
            [{"id": NATIVE_SESSION, "agent": "cdad-test-writer"}])
        proc = self.record(attempt=ATTEMPT_PD23_TW,
                           native_result=self.native_result_file())
        self.envelope(proc, "PD-23 test-writer/red")
        descriptor = self.descriptor()
        self.assertEqual(
            self.part_kinds(descriptor), ["test-writer-role-report"],
            msg="PD-23/§2.8: el descriptor de la vía nativa no declara el kind "
                "derivado de rol+subfase (test-writer/red ⇒ "
                "`test-writer-role-report`; nunca la constante fija): %r"
                % (descriptor.get("parts"),))

        architect = self.new_project(role="architect", substage="draft")
        arch_proc = self.record(
            ctx=architect, attempt=ATTEMPT_PD23_ARCH,
            native_result=self.native_result_file("native-result-arch-u1b.md"))
        self.envelope(arch_proc, "PD-23 architect/draft")
        descriptor = self.descriptor(architect)
        self.assertEqual(
            self.part_kinds(descriptor), ["role-report"],
            msg="PD-23/§2.8: architect/draft ⇒ `role-report` (la fila lo admite "
                "desde 005-007 T4): %r" % (descriptor.get("parts"),))

    def part_kinds(self, descriptor: dict) -> list:
        parts = descriptor.get("parts")
        if not isinstance(parts, list):
            return []
        return [part.get("artifact_kind") for part in parts
                if isinstance(part, dict)]


if __name__ == "__main__":
    unittest.main(verbosity=2)
