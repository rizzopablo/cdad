#!/usr/bin/env python3
"""RED tests for 006-005 U2 — the OpenCode runtime module.

Contract: docs/specs/006-005-native-path-parity/spec.md (approved; §2.2, §2.3,
§2.5, §2.7, §2.8, PD-5 (external side), PD-10..PD-14, PD-23 (external side),
INV-4, INV-6, INV-11, INV-13, INV-15). Plan: the approved U2 sheet (§3) and its
`plan-tasks` block of docs/specs/006-005-native-path-parity/plan.md. Task
provenance: `exec-006-005-native-path-parity-001`.

Unit under test: `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`, invoked
AS A PROCESS (the interface's own argv contract for the module — the same one
`tests/test_006_005_u1b_dispatch_entry.py`'s fixture module honours):

    python3 cdad_delegate_opencode.py --project-root R --packet-id P \
        --exec-config C [ --capabilities | --observe --session S ]

with the published `PACKET.md` bytes on stdin (the module's declared transport,
probed black-box: without it the module answers `no packet was transported on
stdin`).

Oracle discipline (black-box, declared). Nothing is read from the
implementation: the module is executed as a process, its documented CLI surface
is probed (`--help`), and every fixture is disposable.
  - a FAKE runtime binary (`FAKE_BINARY_SOURCE`, declared protocol below):
    records each invocation (argv, PWD, whether `OPENCODE_PASSWORD` is present
    in its environment — a BOOLEAN, never the value) and writes the SQLite store
    declared by the fixture;
  - a disposable SQLite store, built either by the test (`write_store`, for the
    capability/observation surfaces) or by the fake binary (`store.json`, for
    the dispatch surfaces);
  - `HOME`/`XDG_CONFIG_HOME` redirected inside the test tempdir and the host's
    `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` STRIPPED from every child
    environment (never the host config, never a real runtime, INV-11);
  - the credential sentinel is invented by this file; no host value is used.

Mapping (one test per numbered postcondition; "RED" = fails today by
AssertionError about missing behaviour, "anchor" = passes today and is declared
as such, because the postcondition it fixes is already satisfied by the current
tree):

  PD-11  TestPd11CredentialReachesTheClientProcess
    test_pd11_server_mode_injects_the_resolved_credential_into_the_client_env
                                                                        RED
    test_pd11_standalone_injects_nothing                                 anchor
  PD-14  TestPd14AgentTravelsInThePacket
    test_pd14_run_argv_carries_the_agent_of_the_packet                  RED
    test_pd14_unpublished_packet_agent_fails_closed_before_dispatch     RED
    test_pd14_packet_without_agent_uses_the_role_agent_and_declares_it  RED
  PD-5   TestPd5ExternalCorrelationIsTheChosenSession
    test_pd5_external_association_is_the_session_the_module_chose       anchor
    test_pd5_external_accepts_a_directory_inside_the_project_and_elsewhere anchor
    test_pd5_foreign_agent_row_is_a_rejection_that_names_the_key        anchor
  PD-12  TestPd12ExternalDoesNotRequireParentNorDirectory
    test_pd12_external_accepts_a_store_without_parent_nor_directory     anchor
  PD-12/PD-13  TestPd12Pd13ObserveSurface
    test_pd12_observe_returns_the_correlated_row_of_the_installed_schema RED
    test_pd12_observe_fails_closed_naming_the_absent_column            RED
    test_pd13_observe_is_one_read_only_access_and_declares_its_counter RED
  PD-10  TestPd10Capabilities
    test_pd10_installed_schema_accredits_correlation_and_names_columns  RED
    test_pd10_only_agent_store_denies_correlation_naming_the_key       RED
    test_pd10_module_without_the_new_surface_does_not_accredit          anchor
  PD-23  TestPd23DerivedArtifactKind
    test_pd23_plan_review_kind_materializes_with_identical_sha         RED
    test_pd23_test_writer_kind_materializes_with_identical_sha         RED
    test_pd23_architect_draft_kind_stays_role_report                   anchor
    test_pd23_scribe_declares_role_report_and_its_row_is_u7            anchor

Expected RED today (measured on HEAD, declared, never accidental): the module
declares the constant `role-report` for every delivery (measured: the durable
`receipt.json` part of a test-writer/`red` dispatch carries
`artifact_kind: role-report` and `materialize` rejects it — "a kind of another
role fails in the closed §7 table"); it has no `--capabilities`/`--observe`
surface (its `--help` declares only `--project-root/--packet-id/--destination/
--exec-config`), so `capabilities` cannot accredit and `record` has no bounded
store observation; it resolves the agent as `cdad-<role>`, never from
`REQUEST.json.agent`; and it injects no credential into the client process
environment (the model of PD-11's D-ADP-1 is new). Measured on this HEAD: 11
tests fail by AssertionError about that missing behaviour (never an import,
syntax or fixture error) and the 8 declared anchors pass — they fix
postconditions the current tree already satisfies (the external association by
the chosen session id, the retired rigid `directory == root` equality, the
rejection of a contradicting agent, the external path without parent/directory
columns, the `standalone` non-injection, the architect/scribe kinds the
derivation must not change, and the module without the new surface).

A-1 (declared): the plan's A-1 row for U2 says "if the RED of U2 finds a test
that fixes the module's `role-report` constant, the replacement is declared here
before touching it". This file reformulates NO existing test's expectation: it
adds new oracles only and does not modify any other test file. An existing test
that fixes the constant was searched for and NOT found: the only files that
mention the module's constant are `tests/test_005_007_t4_architect_report_
materialization.py` (a hand-built receipt fixture: it never dispatches the
module) and this focal. Nothing is replaced.

Flakiness note (declared, from the same family): the waiter's margin under load
is a known debt. If a focal dispatch times out under load, it is reported with
its isolated run instead of loosening the oracle.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    build_project,
    read_state,
    run_cli,
)
from test_004_003_t1_draft_contract import (
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
    DRAFT_PLAN_WITH_TASKS,
)
from test_006_001_t1_selection import (
    FAST_WAIT,
    MATCHING_CLIENT_SEMVER,
    FakeInfoServer,
    basic_auth_header,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
SCRIPTS = SKILL_DIR / "scripts"
MODULE = SCRIPTS / "cdad_delegate_opencode.py"
ENTRY = SCRIPTS / "cdad_dispatch.py"
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

RUNTIME = "opencode"
FAKE_VERSION = "opencode-fake 1.0.0"          # semver == MATCHING_CLIENT_SEMVER
MODEL = "fixture-u2-model"
WAIT = {"timeout_seconds": 25}

# Fixture sentinels (invented here; never a host value, INV-11).
CREDENTIAL_SENTINEL = "cdad-006-005-u2-sentinel-credential"
FOREIGN_ROW_AGENT = "cdad-reviewer"           # an agent of ANOTHER role
UNPUBLISHED_AGENT = "cdad-006-005-u2-unpublished-agent"
STORE_SESSION = "ses-006-005-u2-fixture-0001"
FINAL_TEXT = "U2 fixture final text\n"

# §2.2/§2.3 config layout, under the redirected XDG_CONFIG_HOME.
CONFIG_DIR_NAME = "cdad"
CREDENTIAL_FILE_NAME = "opencode-server.env"
RUNTIMES_FILE_NAME = "runtimes.json"
OPENCODE_PASSWORD_ENV = "OPENCODE_PASSWORD"
OPENCODE_SERVER_PASSWORD_ENV = "OPENCODE_SERVER_PASSWORD"

# The store schema observed on the installed version (orchestrator's probe of
# the v2.0.27 store: `session_v2` exposes these columns). It carries the
# discriminating keys of §2.3 (`parent_id`, `time_created`, `directory`).
INSTALLED_COLUMNS = [
    "id", "parent_id", "directory", "agent", "model",
    "time_created", "time_idle", "idle_outcome",
]
# The store of a version that exposes ONLY the agent key: no discriminating key
# (§2.3/O-3) — the accreditation positive is unreachable with it.
AGENT_ONLY_COLUMNS = ["id", "agent", "idle_outcome"]
NO_PRODUCTIVE_KEY_COLUMNS = ["id", "idle_outcome"]   # `agent` absent

# §2.6/§2.8: the kind of the delivered part is derived from role + substage.
EXPECTED_KINDS = {
    ("test-writer", "red"): "test-writer-role-report",
    ("reviewer", "plan-review"): "plan-review",
    ("architect", "draft"): "role-report",
    ("scribe", "memory"): "role-report",
}


# ------------------------------------------------- fake runtime binary (fixture)


FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
# Fake OpenCode runtime binary — fixture of tests/test_006_005_u2_opencode_module.py.
# NOT the product: it simulates the destination CLI without a live runtime.
# Declared protocol (the whole surface the oracles observe):
#   1. `--version` (the preflight invocation) prints <fake>/version.txt and
#      exits 0 BEFORE writing the store or logging a dispatch.
#   2. EVERY invocation appends one JSON line to <fake>/calls.jsonl:
#      {"argv": [...], "pwd": <PWD env>, "credential_env_present": <bool>,
#       "session": <value of --session>, "agent": <value of --agent>}.
#      `credential_env_present` is a BOOLEAN derived from the presence of
#      OPENCODE_PASSWORD in this process environment: the value is NEVER read,
#      stored nor echoed (INV-11).
#   3. <fake>/store.json declares the durable store this client writes:
#      {"path": <sqlite path>, "columns": [<session_v2 columns>],
#       "final_text": <text of the last assistant message>}. The table is
#      created with EXACTLY those columns (a store without `agent` is a
#      declared fixture of PD-12) and the row carries the id received in
#      `--session`, the agent received in `--agent`, `$PWD` resolved in
#      `directory`, and `succeeded` in `idle_outcome` when those columns exist.
#   4. when <fake>/require-credential exists, the `run` invocation exits rc=9
#      with a stderr naming OPENCODE_PASSWORD if the variable is ABSENT from
#      this process environment (PD-11's oracle: the resolved credential must
#      reach the client process environment).
#   5. the final text is printed to stdout and stored as the last assistant
#      message (both are legitimate carriers of the role's final text).
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

_FAKE = Path(__file__).resolve().parent.parent


def _option(name):
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _log(entry):
    with (_FAKE / "calls.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


_argv = sys.argv[1:]

if "--version" in _argv:
    sys.stdout.write((_FAKE / "version.txt").read_text(encoding="utf-8").strip()
                     + "\n")
    sys.stdout.flush()
    sys.exit(0)

_session = _option("--session") or "ses-fake-default"
_agent = _option("--agent") or "cdad-test-writer"
_entry = {
    "argv": _argv,
    "pwd": os.environ.get("PWD"),
    "credential_env_present": "OPENCODE_PASSWORD" in os.environ,
    "session": _session,
    "agent": _agent,
    "is_run": "run" in _argv,
}

if ("run" in _argv and (_FAKE / "require-credential").is_file()
        and "OPENCODE_PASSWORD" not in os.environ):
    _entry["refused"] = "credential-absent"
    _log(_entry)
    sys.stderr.write("opencode-fake: OPENCODE_PASSWORD is not present in this "
                     "process environment\n")
    sys.stderr.flush()
    sys.exit(9)

_spec = json.loads((_FAKE / "store.json").read_text(encoding="utf-8"))
_store = Path(_spec["path"])
_store.parent.mkdir(parents=True, exist_ok=True)
_connection = sqlite3.connect(str(_store))
try:
    _connection.execute(
        "CREATE TABLE IF NOT EXISTS session_v2 (%s)"
        % ", ".join(_spec["columns"]))
    _connection.execute(
        "CREATE TABLE IF NOT EXISTS session_message ("
        "id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INTEGER,"
        " data TEXT)")
    _now = time.time()
    _values = {}
    for _declaration in _spec["columns"]:
        _column = _declaration.split()[0]
        if _column == "id":
            _values[_column] = _session
        elif _column == "agent":
            _values[_column] = _spec.get("row_agent") or _agent
        elif _column == "model":
            _values[_column] = _spec.get("model", "fixture-model")
        elif _column == "directory":
            _values[_column] = (_spec.get("directory")
                                or os.environ.get("PWD"))
        elif _column == "parent_id":
            _values[_column] = _spec.get("parent_id")
        elif _column in ("time_created", "time_updated"):
            _values[_column] = _now - 5.0
        elif _column == "time_idle":
            _values[_column] = _now
        elif _column == "idle_outcome":
            _values[_column] = _spec.get("outcome", "succeeded")
        else:
            _values[_column] = None
    _columns = list(_values)
    _connection.execute(
        "INSERT OR REPLACE INTO session_v2 (%s) VALUES (%s)"
        % (", ".join(_columns), ", ".join("?" * len(_columns))),
        [_values[_column] for _column in _columns])
    _connection.execute(
        "INSERT OR REPLACE INTO session_message VALUES (?,?,?,?,?)",
        (_session + "-final", _session, "assistant", 1,
         json.dumps({"content": [{"type": "text",
                                  "text": _spec["final_text"]}]})))
    _connection.commit()
finally:
    _connection.close()

_log(_entry)
sys.stdout.write(_spec["final_text"])
if not _spec["final_text"].endswith("\n"):
    sys.stdout.write("\n")
sys.stdout.flush()
sys.exit(0)
'''

# A module WITHOUT the new surface of §2.2 (the O-6 window fixture): it declares
# only the pre-feature CLI, so `capabilities` cannot accredit it. Written into a
# STAGED copy of the skill tree (the canonical tree is copied byte to byte,
# without inspection, and only this file is replaced).
LEGACY_MODULE_SOURCE = '''#!/usr/bin/env python3
"""Fixture module (006-005 U2): a runtime module without the §2.2 surface."""
import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--packet-id", required=True)
    parser.add_argument("--destination")
    parser.add_argument("--exec-config")
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


# ------------------------------------------------------------------ helpers


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tail(text: str, lines: int = 12) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


def strip_credentials(env: dict) -> dict:
    """Never inherit a host credential into a child (INV-11)."""
    cleaned = dict(env)
    cleaned.pop(OPENCODE_PASSWORD_ENV, None)
    cleaned.pop(OPENCODE_SERVER_PASSWORD_ENV, None)
    return cleaned


def out_text(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or b"").decode("utf-8", errors="replace")


def err_text(proc: subprocess.CompletedProcess) -> str:
    return (proc.stderr or b"").decode("utf-8", errors="replace")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, document: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


# ------------------------------------------------------------------ fixture


class U2ModuleCase(unittest.TestCase):
    """Disposable project + disposable store + fake runtime binary.

    `HOME` and `XDG_CONFIG_HOME` are redirected inside the test tempdir (never
    the host config), and both credential variables are stripped from every
    child environment. Nothing writes inside the repository.
    """

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-006-005-u2-")
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.xdg = self.base / "xdg"
        self.xdg.mkdir()
        self._projects = 0
        self._fakes = 0

    # -- project fixture -------------------------------------------------

    def new_project(self, *, role: str = "test-writer", substage: str = "red",
                    stack: str | None = None,
                    epic_plan_approved: bool = False,
                    draft_plan: bool = False) -> dict:
        """A published (v2) packet of the requested role/substage on a
        disposable project. Extra fixture state is declared by flag."""
        self._projects += 1
        root = self.base / ("proj-%d" % self._projects)
        build_project(root)
        state_path = root / "docs" / ".cdad-state.json"
        if stack is not None:
            state = read_json(state_path)
            state["stack"] = stack
            write_json(state_path, state)
        if epic_plan_approved:
            state = read_json(state_path)
            epic = state.get("active_epic")
            self.assertTrue(epic, "fixture: the state declares no active epic")
            plan = root / "docs" / "epics" / epic / "plan.md"
            plan.parent.mkdir(parents=True, exist_ok=True)
            plan.write_text("# Epic plan (fixture U2)\n", encoding="utf-8")
            authority = root / "docs" / "epics" / epic / "execution.md"
            if not authority.is_file():
                authority.write_text(
                    "# Authorized execution (fixture U2)\n", encoding="utf-8")
            history = list(state.get("epic_history") or [])
            history.append({
                "epic": epic,
                "stage": "epic-plan",
                "approved_by": "fixture-u2",
                "approved_at": "2026-10-19T00:00:00Z",
            })
            state["epic_history"] = history
            state["epic_stage"] = "features-loop"
            write_json(state_path, state)
        extra: list[str] = []
        if draft_plan:
            draft = root / DRAFT_PLAN_RELPATH
            draft.parent.mkdir(parents=True, exist_ok=True)
            draft.write_bytes(DRAFT_PLAN_WITH_TASKS)
            extra += [
                "--contract-kind", "draft-plan",
                "--contract-path", DRAFT_PLAN_RELPATH,
                "--plan-version", DRAFT_PLAN_VERSION,
            ]
        prepared = run_cli([
            "prepare", "--project-root", str(root),
            "--role", role, "--substage", substage,
            "--objective", "006-005 U2 RED fixture (%s/%s)" % (role, substage),
            *extra,
        ])
        self.assertEqual(
            prepared.returncode, 0,
            "fixture: `prepare` of %s/%s must publish the packet: %s"
            % (role, substage, tail(prepared.stdout + prepared.stderr)))
        state = read_state(root)
        packet_id = state["active_packet"]["id"]
        execution_id = state["execution"]["id"]
        packet_dir = root / ".cdad" / "packets" / packet_id
        return {
            "root": root,
            "role": role,
            "substage": substage,
            "packet_id": packet_id,
            "execution_id": execution_id,
            "request_path": packet_dir / "REQUEST.json",
            "packet_path": packet_dir / "PACKET.md",
            "execution_path": (root / ".cdad" / "executions" / execution_id
                               / "execution.json"),
            "request": read_json(packet_dir / "REQUEST.json"),
        }

    def rewrite_request(self, ctx: dict, mutate) -> dict:
        """Fixture device of this feature (precedent: U1c/U1b): rewrite the
        published `REQUEST.json` in place. The PACKET.md render is invariant to
        the `agent` field (PD-7), so the packet fed on stdin is unchanged."""
        request = read_json(ctx["request_path"])
        mutate(request)
        write_json(ctx["request_path"], request)
        ctx["request"] = request
        return request

    # -- fake runtime ----------------------------------------------------

    def fake_runtime(self, *, columns: list | None = None,
                     final_text: str = FINAL_TEXT,
                     outcome: str = "succeeded",
                     mode: str | None = "standalone",
                     server: str | None = None,
                     require_credential: bool = False,
                     store_directory: str | None = None,
                     row_agent: str | None = None) -> dict:
        self._fakes += 1
        fake = self.base / ("fake-%d" % self._fakes)
        (fake / "bin").mkdir(parents=True)
        binary = fake / "bin" / "opencode-fake"
        binary.write_text(FAKE_BINARY_SOURCE, encoding="utf-8")
        binary.chmod(0o755)
        (fake / "version.txt").write_text(FAKE_VERSION + "\n", encoding="utf-8")
        if require_credential:
            (fake / "require-credential").write_text("1\n", encoding="utf-8")
        store = fake / "sessions.db"
        spec = {
            "path": str(store),
            "columns": columns or list(INSTALLED_COLUMNS),
            "final_text": final_text,
            "outcome": outcome,
        }
        if store_directory is not None:
            spec["directory"] = store_directory
        if row_agent is not None:
            spec["row_agent"] = row_agent
        write_json(fake / "store.json", spec)
        config = {
            "runtime": RUNTIME,
            "binary": str(binary),
            "binary_version": FAKE_VERSION,
            "model": MODEL,
            "logs_dir": str(fake / "logs"),
            "sessions_db": str(store),
            "wait": dict(WAIT),
        }
        if mode:
            config["mode"] = mode
        if server:
            config["server"] = server
        config_path = write_json(fake / "exec-config.json", config)
        return {
            "dir": fake,
            "binary": binary,
            "config": config_path,
            "calls": fake / "calls.jsonl",
            "store": store,
            "server": server,
        }

    # -- config patching -------------------------------------------------

    def patch_config(self, fake: dict, patch: dict) -> dict:
        """Rewrite the module's execution configuration (the internal mechanism
        of §2.6) — `wait.*` is MERGED, never clobbered."""
        config = read_json(fake["config"])
        patch = dict(patch)
        wait_patch = patch.pop("wait", None)
        config.update(patch)
        if wait_patch:
            wait = dict(config.get("wait") or {})
            wait.update(wait_patch)
            config["wait"] = wait
        write_json(fake["config"], config)
        return config

    # -- child environment and invocations -------------------------------

    def child_env(self, *, pwd: Path, extra: dict | None = None) -> dict:
        env = strip_credentials(os.environ)
        env["HOME"] = str(self.home)
        env["XDG_CONFIG_HOME"] = str(self.xdg)
        env["PWD"] = str(pwd)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        if extra:
            env.update(extra)
        return env

    def credential_file(self, value: str, *, mode: int = 0o600) -> Path:
        """§2.5: the default credential file `<config-dir>/cdad/
        opencode-server.env`, with 0600 (006-003 U6 layout)."""
        path = self.xdg / CONFIG_DIR_NAME / CREDENTIAL_FILE_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "%s=%s\n" % (OPENCODE_PASSWORD_ENV, value), encoding="utf-8")
        os.chmod(path, mode)
        return path

    def run_module(self, ctx: dict, *args: str, stdin: bytes | None = None,
                   env_overrides: dict | None = None,
                   cwd: Path | None = None) -> subprocess.CompletedProcess:
        """The module, as a process, with the published packet on stdin."""
        payload = (stdin if stdin is not None
                   else ctx["packet_path"].read_bytes())
        return subprocess.run(
            [sys.executable, str(MODULE),
             "--project-root", str(ctx["root"]),
             "--packet-id", ctx["packet_id"],
             *args],
            input=payload, capture_output=True,
            env=self.child_env(pwd=cwd or ctx["root"], extra=env_overrides),
            cwd=str(cwd or ctx["root"]), timeout=300)

    def dispatch(self, ctx: dict, fake: dict, *,
                 env_overrides: dict | None = None,
                 cwd: Path | None = None) -> subprocess.CompletedProcess:
        return self.run_module(
            ctx, "--exec-config", str(fake["config"]),
            env_overrides=env_overrides, cwd=cwd)

    def envelope(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            "%s: the module did not end with rc=0: stdout=%s stderr=%s"
            % (label, tail(out_text(proc)), tail(err_text(proc))))
        try:
            out = json.loads(out_text(proc) or "null")
        except json.JSONDecodeError:
            self.fail("%s: stdout is not the module envelope JSON: %r"
                      % (label, out_text(proc)[:400]))
        self.assertIsInstance(out, dict, "%s: envelope is not an object" % label)
        for key in ("attempt", "session", "termination", "delivery_ref",
                    "diagnosis"):
            self.assertIn(key, out, "%s: envelope lacks %r" % (label, key))
        return out

    # -- fake observations -----------------------------------------------

    def calls(self, fake: dict) -> list:
        path = fake["calls"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def run_calls(self, fake: dict) -> list:
        return [call for call in self.calls(fake) if call.get("is_run")]

    def dispatch_call(self, fake: dict, label: str) -> dict:
        calls = self.run_calls(fake)
        self.assertEqual(
            len(calls), 1,
            "%s: the client must be invoked exactly once for the errand "
            "(without chaining sessions): %r"
            % (label, [call.get("argv") for call in calls][:4]))
        return calls[0]

    # -- store fixture ---------------------------------------------------

    def write_store(self, path: Path, columns: list, rows: list) -> Path:
        """A disposable SQLite store with EXACTLY the declared columns (the
        store of a version observed by the fixture, never a live store)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE session_v2 (%s)" % ", ".join(columns))
            for row in rows:
                ordered = [column.split()[0] for column in columns]
                connection.execute(
                    "INSERT INTO session_v2 (%s) VALUES (%s)"
                    % (", ".join(ordered), ", ".join("?" * len(ordered))),
                    [row.get(column) for column in ordered])
            connection.commit()
        finally:
            connection.close()
        return path

    def store_bytes(self, directory: Path) -> dict:
        return {
            path.name: path.read_bytes()
            for path in sorted(directory.glob("*"))
            if path.is_file()
        }

    # -- durable delivery and materialization ----------------------------

    def receipt_path(self, ctx: dict) -> Path:
        return (ctx["root"] / ".cdad" / "runtime" / "results"
                / ctx["execution_id"] / ctx["packet_id"] / "receipt.json")

    def receipt_doc(self, ctx: dict) -> dict:
        path = self.receipt_path(ctx)
        self.assertTrue(
            path.is_file(),
            "the durable delivery left no receipt at "
            + str(path.relative_to(ctx["root"])))
        return read_json(path)

    def materialize(self, ctx: dict, part_name: str, target_rel: str,
                    label: str) -> subprocess.CompletedProcess:
        """`materialize` with the durable receipt (003-002/§7 surface)."""
        receipt = self.receipt_path(ctx)
        self.assertTrue(receipt.is_file(), "%s: no durable receipt" % label)
        authorization = write_json(ctx["root"] / ".cdad" / "inbox" / "AUTH.json", {
            "schema_version": 1,
            "execution_id": ctx["execution_id"],
            "packet_id": ctx["packet_id"],
            "receipt_sha256": sha256_bytes(receipt.read_bytes()),
            "authorized_by": "fixture-u2",
            "authority_ref": read_json(ctx["execution_path"])["execution"]
                             ["authority_ref"],
            "approval_effect": False,
            "copies": [{
                "part": part_name,
                "target": target_rel,
                "expected_previous_sha256": None,
            }],
        })
        (ctx["root"] / target_rel).parent.mkdir(parents=True, exist_ok=True)
        return subprocess.run(
            [sys.executable, str(RESULT_CLI), "materialize",
             "--project-root", str(ctx["root"]),
             "--receipt", str(receipt),
             "--authorization", str(authorization)],
            capture_output=True, env=self.child_env(pwd=ctx["root"]),
            cwd=str(ctx["root"]), timeout=120)

    def assert_materializes_with_identical_sha(self, ctx: dict, kind: str,
                                               label: str) -> None:
        """§2.8/PD-23: the receipt's part carries the DERIVED kind and
        `materialize` copies its BYTES into the role's allowed root with an
        identical sha (no manual copy)."""
        receipt = self.receipt_doc(ctx)
        kinds = [part.get("artifact_kind") for part in receipt["parts"]]
        self.assertEqual(
            kinds, [kind],
            "%s: the delivered part must declare the kind derived from role and "
            "substage (§2.8/PD-23), got %r" % (label, kinds))
        part = receipt["parts"][0]
        target_rel = "docs/specs/%s/u2-report.md" % ctx["request"]["feature_id"]
        proc = self.materialize(ctx, part["name"], target_rel, label)
        self.assertEqual(
            proc.returncode, 0,
            "%s: `materialize` must accept the derived kind %r with an "
            "identical sha: rc=%s stderr=%s"
            % (label, kind, proc.returncode, tail(err_text(proc))))
        target = ctx["root"] / target_rel
        self.assertTrue(target.is_file(), "%s: no materialized target" % label)
        stored = (self.receipt_path(ctx).parent / "parts"
                  / (part["name"] + ".utf8"))
        self.assertTrue(stored.is_file(), "%s: no stored part" % label)
        self.assertEqual(
            sha256_bytes(target.read_bytes()),
            sha256_bytes(stored.read_bytes()),
            "%s: the materialized sha must be identical to the received part"
            % label)

    # -- ledger ----------------------------------------------------------

    def dispatch_records(self, ctx: dict) -> dict:
        directory = (ctx["root"] / ".cdad" / "executions"
                     / ctx["execution_id"] / "dispatches")
        if not directory.is_dir():
            return {}
        return {path.stem: path for path in sorted(directory.glob("*.json"))}

    def new_records(self, ctx: dict, before: dict) -> dict:
        after = self.dispatch_records(ctx)
        return {stem: path for stem, path in after.items() if stem not in before}

    def store_rows(self, path: Path) -> list:
        connection = sqlite3.connect("file:%s?mode=ro" % path, uri=True)
        try:
            cursor = connection.execute("SELECT * FROM session_v2")
            columns = [item[0] for item in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        finally:
            connection.close()


# --------------------------------------------------------------------- PD-11


class TestPd11CredentialReachesTheClientProcess(U2ModuleCase):
    """PD-11/D-ADP-1/INV-11: in `mode: server` the credential resolved with the
    precedence already in force (environment first, then the 0600 file) is
    injected ONLY into the environment of the client process the module
    launches, together with the `PWD` it already pins. Never in argv, stdout,
    stderr, the I8 record nor the receipt. In `standalone`/`service` nothing is
    injected."""

    def test_pd11_server_mode_injects_the_resolved_credential_into_the_client_env(
            self) -> None:
        """PD-11: a loopback server fixture requires Basic auth with the
        sentinel; the sentinel lives ONLY in the default 0600 credential file
        (the test environment carries no credential). The fake binary REQUIRES
        `OPENCODE_PASSWORD` in its own environment for the `run` errand and
        echoes only its presence → the dispatch must reach `completed` and the
        sentinel must appear nowhere else. RED today: the credential is
        resolved for the preflight but never injected into the client."""
        server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode(),
            expected_authorization=basic_auth_header(CREDENTIAL_SENTINEL))
        self.addCleanup(server.stop)
        ctx = self.new_project()
        fake = self.fake_runtime(mode="server", server=server.url,
                                 require_credential=True)
        credential_file = self.credential_file(CREDENTIAL_SENTINEL)
        before = self.dispatch_records(ctx)

        proc = self.dispatch(ctx, fake)
        out = self.envelope(proc, "PD-11 mode server")
        self.assertEqual(
            out["termination"], "completed",
            msg="PD-11/§2.5: the credential resolved from the 0600 file must "
                "reach the CLIENT process environment, so the client that "
                "requires `%s` completes the errand: termination=%r diagnosis=%r"
                % (OPENCODE_PASSWORD_ENV, out["termination"],
                   out.get("diagnosis")))

        call = self.dispatch_call(fake, "PD-11")
        self.assertTrue(
            call["credential_env_present"],
            msg="PD-11: the client invocation did not carry "
                "`%s` in its environment (injected only there, together with "
                "the pinned PWD): %r" % (OPENCODE_PASSWORD_ENV, call))

        # INV-11: the value never leaves the client environment.
        for label, text in (
                ("stdout", out_text(proc)),
                ("stderr", err_text(proc)),
                ("diagnosis", out.get("diagnosis") or "")):
            self.assertNotIn(
                CREDENTIAL_SENTINEL, text,
                msg="PD-11/INV-11: the credential appears in %s: %r"
                    % (label, text))
        for invocation in self.calls(fake):
            self.assertNotIn(
                CREDENTIAL_SENTINEL, " ".join(str(token)
                                              for token in invocation["argv"]),
                msg="PD-11/INV-11: the credential appears in the binary argv: "
                    "%r" % (invocation,))
        new_records = self.new_records(ctx, before)
        self.assertEqual(
            len(new_records), 1,
            msg="PD-11: the module registers exactly one attempt (its own): %r"
                % sorted(new_records))
        for record in new_records.values():
            self.assertNotIn(
                CREDENTIAL_SENTINEL, record.read_text(encoding="utf-8"),
                msg="PD-11/INV-11: the credential appears in the I8 record")
        self.assertNotIn(
            CREDENTIAL_SENTINEL,
            self.receipt_path(ctx).read_text(encoding="utf-8"),
            msg="PD-11/INV-11: the credential appears in the durable receipt")
        # The file that supplied it is the declared one (the oracle of §2.5).
        self.assertTrue(credential_file.is_file())

    def test_pd11_standalone_injects_nothing(self) -> None:
        """PD-11/§2.5 (anchor, declared): in `standalone` NOTHING is injected —
        even with the 0600 credential file present, the client environment does
        not carry the variable. Today the credential is never injected, so this
        test holds as the anchor that the new injection must stay limited to
        `mode: server`."""
        ctx = self.new_project()
        fake = self.fake_runtime(mode="standalone")
        self.credential_file(CREDENTIAL_SENTINEL)

        proc = self.dispatch(ctx, fake)
        out = self.envelope(proc, "PD-11 standalone")
        self.assertEqual(
            out["termination"], "completed",
            msg="PD-11: the standalone errand must complete: %r"
                % out.get("diagnosis"))
        call = self.dispatch_call(fake, "PD-11 standalone")
        self.assertFalse(
            call["credential_env_present"],
            msg="PD-11/§2.5: `standalone` must inject NOTHING (the credential "
                "file is present and must not be used): %r" % call)


# --------------------------------------------------------------------- PD-14


class TestPd14AgentTravelsInThePacket(U2ModuleCase):
    """PD-14/D-ADP-4/INV-13: the agent comes from `REQUEST.json.agent` (role +
    `stack`), it travels to the invocation as `--agent <agent>`, an agent that
    is not published fails closed BEFORE dispatching, and a packet without the
    field uses `cdad-<role>` and declares the absence."""

    def test_pd14_run_argv_carries_the_agent_of_the_packet(self) -> None:
        """PD-14: with `stack: odoo` the published packet declares
        `agent: cdad-test-writer-odoo`; the client invocation must carry THAT
        agent, never the bare role agent. RED today: the module resolves
        `cdad-<role>`."""
        ctx = self.new_project(stack="odoo")
        self.assertEqual(
            ctx["request"].get("agent"), "cdad-test-writer-odoo",
            msg="fixture precondition: `prepare` writes the agent of role+stack "
                "(PD-7): %r" % ctx["request"].get("agent"))
        fake = self.fake_runtime()
        out = self.envelope(self.dispatch(ctx, fake), "PD-14 agente del paquete")
        self.assertEqual(
            out["termination"], "completed",
            msg="PD-14: the errand of the declared agent must complete: %r"
                % out.get("diagnosis"))
        call = self.dispatch_call(fake, "PD-14")
        self.assertIn(
            "--agent", call["argv"],
            msg="PD-14: the invocation does not declare an agent: %r"
                % call["argv"])
        self.assertEqual(
            call["agent"], "cdad-test-writer-odoo",
            msg="PD-14: the invocation must carry the agent of the PACKET "
                "(role + stack), not the bare role agent: %r" % call)

    def test_pd14_unpublished_packet_agent_fails_closed_before_dispatch(
            self) -> None:
        """PD-14: a packet whose agent is not published fails closed BEFORE
        dispatching, naming that agent, with no client invocation and no
        delivery. RED today: the module uses `cdad-<role>` (which is published)
        and dispatches anyway."""
        ctx = self.new_project()
        self.rewrite_request(
            ctx, lambda request: request.__setitem__("agent", UNPUBLISHED_AGENT))
        self.assertFalse(
            (ctx["root"] / ".opencode" / "agents"
             / (UNPUBLISHED_AGENT + ".md")).exists(),
            msg="fixture precondition: %r must not be published"
                % UNPUBLISHED_AGENT)
        fake = self.fake_runtime()

        proc = self.dispatch(ctx, fake)
        out = self.envelope(proc, "PD-14 agente no publicado")
        self.assertEqual(
            out["termination"], "blocked",
            msg="PD-14: an unpublished agent must fail closed (never dispatch):"
                " termination=%r" % out["termination"])
        self.assertIn(
            UNPUBLISHED_AGENT, out_text(proc) + (out.get("diagnosis") or ""),
            msg="PD-14: the diagnosis must name the agent it refused: %r"
                % out.get("diagnosis"))
        self.assertEqual(
            self.run_calls(fake), [],
            msg="PD-14: the module must fail closed BEFORE dispatching the "
                "client: %r" % [call["argv"] for call in self.run_calls(fake)])
        self.assertFalse(
            self.receipt_path(ctx).exists(),
            msg="PD-14: a refused dispatch leaves no delivery")

    def test_pd14_packet_without_agent_uses_the_role_agent_and_declares_it(
            self) -> None:
        """PD-14 (compatibility): a packet published before the feature (no
        `agent` field) is still dispatchable with `cdad-<role>`, and the module
        DECLARES the absence of the field. RED today for the declaration half:
        the argv fallback already holds."""
        ctx = self.new_project()
        self.rewrite_request(ctx, lambda request: request.pop("agent", None))
        fake = self.fake_runtime()
        before = self.dispatch_records(ctx)

        proc = self.dispatch(ctx, fake)
        out = self.envelope(proc, "PD-14 sin campo agent")
        call = self.dispatch_call(fake, "PD-14 sin agent")
        self.assertEqual(
            call["agent"], "cdad-test-writer",
            msg="PD-14: without the field the module uses `cdad-<role>`: %r"
                % call)
        texts = [out_text(proc), out.get("diagnosis") or ""]
        for record in self.new_records(ctx, before).values():
            texts.append(record.read_text(encoding="utf-8"))
        joined = "\n".join(texts)
        self.assertRegex(
            joined, r"(?i)\bagent\b",
            msg="PD-14: the module must declare the absent `agent` field of the "
                "packet: %r" % tail(joined))
        self.assertRegex(
            joined,
            r"(?i)absent|missing|ausente|not declared|no declarad|without the"
            r" field|sin el campo|fallback",
            msg="PD-14: the module must DECLARE the absence of the field "
                "(never silence it): %r" % tail(joined))


# ---------------------------------------------------------------------- PD-5


class TestPd5ExternalCorrelationIsTheChosenSession(U2ModuleCase):
    """PD-5 (external side)/§2.3/INV-15: the association is the session id the
    MODULE chose (it creates the session and knows it by id), corroborated
    against the durable row's `agent`; there is no parent to compare and NO
    rigid `directory == root` equality; an evaluable contradiction is a
    rejection that names the key."""

    def test_pd5_external_association_is_the_session_the_module_chose(self) -> None:
        """PD-5 (anchor, declared): the envelope's session is the id the module
        passed in `--session`, which is exactly the id of the row it wrote."""
        ctx = self.new_project()
        fake = self.fake_runtime()
        out = self.envelope(self.dispatch(ctx, fake), "PD-5 asociación")
        self.assertEqual(out["termination"], "completed")
        call = self.dispatch_call(fake, "PD-5")
        self.assertTrue(
            call["session"],
            msg="PD-5: the module must declare the session id it chose on the "
                "invocation: %r" % call)
        self.assertEqual(
            out["session"], call["session"],
            msg="PD-5: the envelope's session is not the id of the transport: "
                "%r != %r" % (out["session"], call["session"]))
        rows = self.store_rows(fake["store"])
        self.assertEqual(len(rows), 1, msg="fixture: one durable row")
        self.assertEqual(
            rows[0]["id"], call["session"],
            msg="PD-5: the durable row is not the one of the chosen session")

    def test_pd5_external_accepts_a_directory_inside_the_project_and_elsewhere(
            self) -> None:
        """PD-5/§2.3/INV-15 (anchor, declared): the row's `directory` being a
        SUBDIRECTORY of the project, or a directory of a coordinator started in
        ANOTHER folder, is ACCEPTED — the rigid equality `directory == root` is
        retired (it would reject both legitimate routes)."""
        nested = self.base / "coordinator-elsewhere"
        nested.mkdir(parents=True, exist_ok=True)
        for label, directory in (
                ("subdirectorio del proyecto", None),
                ("coordinador en otra carpeta", str(nested))):
            with self.subTest(ruta=label):
                ctx = self.new_project()
                inside = ctx["root"] / "nested" / "deeper"
                inside.mkdir(parents=True, exist_ok=True)
                fake = self.fake_runtime(
                    store_directory=directory or str(inside))
                out = self.envelope(
                    self.dispatch(ctx, fake), "PD-5 %s" % label)
                self.assertEqual(
                    out["termination"], "completed",
                    msg="PD-5/INV-15 (%s): the legitimate route is rejected: "
                        "%r" % (label, out.get("diagnosis")))
                rows = self.store_rows(fake["store"])
                self.assertNotEqual(
                    rows[0]["directory"], str(ctx["root"]),
                    msg="fixture (%s): the row's directory must NOT be the root "
                        "(the oracle is about the retired equality)" % label)

    def test_pd5_foreign_agent_row_is_a_rejection_that_names_the_key(self) -> None:
        """PD-5 (anchor, declared): a durable row whose `agent` is another role
        CONTRADICTS the packet's agent → the dispatch is REJECTED naming the
        key, never `unknown`, never an accepted delivery (no receipt)."""
        ctx = self.new_project()
        fake = self.fake_runtime(row_agent=FOREIGN_ROW_AGENT)
        proc = self.dispatch(ctx, fake)
        out = self.envelope(proc, "PD-5 contradicción de agente")
        self.assertEqual(
            out["termination"], "blocked",
            msg="PD-5: an evaluable contradiction is a rejection: %r"
                % out["termination"])
        self.assertRegex(
            out_text(proc) + (out.get("diagnosis") or ""),
            r"(?i)agent|agente",
            msg="PD-5: the rejection must name the key that contradicts: %r"
                % out.get("diagnosis"))
        self.assertFalse(
            self.receipt_path(ctx).exists(),
            msg="PD-5: a rejected dispatch accepts no delivery")


# --------------------------------------------------------------------- PD-12


class TestPd12ExternalDoesNotRequireParentNorDirectory(U2ModuleCase):
    """PD-12/§2.3: the external path correlates by the id it chose itself, so
    it requires NEITHER a parent column NOR a directory column (only the keys
    it actually evaluates)."""

    def test_pd12_external_accepts_a_store_without_parent_nor_directory(self) -> None:
        """PD-12 (anchor, declared): with a store exposing only
        `id, agent, idle_outcome` the external dispatch completes and leaves a
        `pending` receipt."""
        columns = ["id TEXT PRIMARY KEY", "agent TEXT", "model TEXT",
                   "time_idle REAL", "idle_outcome TEXT"]
        self.assertNotIn(
            "parent_id", " ".join(columns),
            msg="fixture: the store must not expose parent columns")
        self.assertNotIn(
            "directory", " ".join(columns),
            msg="fixture: the store must not expose a directory column")
        ctx = self.new_project()
        fake = self.fake_runtime(columns=columns)
        out = self.envelope(self.dispatch(ctx, fake), "PD-12 vía externa")
        self.assertEqual(
            out["termination"], "completed",
            msg="PD-12: the external path must not require parent/directory "
                "columns: %r" % out.get("diagnosis"))
        receipt = self.receipt_doc(ctx)
        self.assertEqual(
            receipt.get("semantic_status"), "pending",
            msg="PD-12: receiving does not approve anything (INV-1)")


class TestPd12Pd13ObserveSurface(U2ModuleCase):
    """PD-12/PD-13/INV-6: the module's observation surface (`--observe`) returns
    the correlated row of the store, requires the keys it evaluates (failing
    closed and naming the absent one), performs exactly ONE read-only access
    (`mode=ro`, no polling) and declares its read counter."""

    def observation_store(self, ctx: dict, columns: list, rows: list) -> Path:
        store = self.base / "observation-store" / "sessions.db"
        if store.parent.exists():
            shutil.rmtree(store.parent)
        return self.write_store(store, columns, rows)

    def observe(self, ctx: dict, store: Path,
                *extra: str) -> subprocess.CompletedProcess:
        """`--observe` with the disposable store of the fixture wired through
        the module's execution configuration (never a live store)."""
        fake = self.fake_runtime()
        self.patch_config(fake, {"sessions_db": str(store)})
        return self.run_module(
            ctx, "--exec-config", str(fake["config"]), "--observe", *extra)

    def test_pd12_observe_returns_the_correlated_row_of_the_installed_schema(
            self) -> None:
        """PD-12: with the schema observed on the installed version (which
        carries the discriminating keys), `--observe --session S` returns the
        correlated row as its observation document. RED today: the module has no
        `--observe` surface (its `--help` declares only the pre-feature
        options)."""
        ctx = self.new_project()
        store = self.observation_store(
            ctx,
            ["id TEXT PRIMARY KEY", "parent_id TEXT", "directory TEXT",
             "agent TEXT", "model TEXT", "time_created REAL",
             "time_idle REAL", "idle_outcome TEXT"],
            [{"id": STORE_SESSION, "parent_id": "ses-parent-u2",
              "directory": str(ctx["root"]), "agent": "cdad-test-writer",
              "model": MODEL, "time_created": time.time() - 5.0,
              "time_idle": time.time(), "idle_outcome": "succeeded"}])

        proc = self.observe(ctx, store, "--session", STORE_SESSION)
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-12: `--observe` must return the observation of the "
                "correlated attempt (rc=%s): stdout=%s stderr=%s"
                % (proc.returncode, tail(out_text(proc)), tail(err_text(proc))))
        try:
            document = json.loads(out_text(proc) or "null")
        except json.JSONDecodeError:
            self.fail("PD-12: the observation is not JSON: %r"
                      % out_text(proc)[:400])
        self.assertIsInstance(
            document, dict,
            msg="PD-12: the observation must be the correlated row, not %r"
                % (document,))
        self.assertIn(
            STORE_SESSION, out_text(proc),
            msg="PD-12: the observation does not carry the correlated session "
                "id: %r" % out_text(proc)[:400])

    def test_pd12_observe_fails_closed_naming_the_absent_column(self) -> None:
        """PD-12: a store that lacks a column of the key set this path evaluates
        (`agent` here) fails closed NAMING the absent column, never degrading to
        `absent` nor fabricating a row. RED today: the failure is the missing
        surface, not the named column."""
        ctx = self.new_project()
        store = self.observation_store(
            ctx, list(NO_PRODUCTIVE_KEY_COLUMNS),
            [{"id": STORE_SESSION, "idle_outcome": "succeeded"}])

        proc = self.observe(ctx, store, "--session", STORE_SESSION)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="PD-12: a store without the `agent` key must fail closed: "
                "stdout=%s stderr=%s" % (tail(out_text(proc)), tail(err_text(proc))))
        self.assertRegex(
            out_text(proc) + err_text(proc), r"agent",
            msg="PD-12: the closed failure must NAME the absent column: %r"
                % (out_text(proc) + err_text(proc)))
        self.assertNotRegex(
            out_text(proc),
            r'"id"\s*:\s*"%s"' % re.escape(STORE_SESSION),
            msg="PD-12: no row may be fabricated from an unknown schema: %r"
                % out_text(proc)[:400])

    def test_pd13_observe_is_one_read_only_access_and_declares_its_counter(
            self) -> None:
        """PD-13/INV-6: the observation is ONE read-only access — the store's
        bytes and directory are untouched (no write, no window/journal file) —
        and the document declares its read counter (`store_reads` ≤ the declared
        ceiling of one read per invocation, no polling). RED today: no surface
        and no counter."""
        ctx = self.new_project()
        store = self.observation_store(
            ctx,
            ["id TEXT PRIMARY KEY", "parent_id TEXT", "directory TEXT",
             "agent TEXT", "model TEXT", "time_created REAL",
             "time_idle REAL", "idle_outcome TEXT"],
            [{"id": STORE_SESSION, "parent_id": "ses-parent-u2",
              "directory": str(ctx["root"]), "agent": "cdad-test-writer",
              "model": MODEL, "time_created": time.time() - 5.0,
              "time_idle": time.time(), "idle_outcome": "succeeded"}])
        before = self.store_bytes(store.parent)

        proc = self.observe(ctx, store, "--session", STORE_SESSION)
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-13: `--observe` must complete: stdout=%s stderr=%s"
                % (tail(out_text(proc)), tail(err_text(proc))))
        after = self.store_bytes(store.parent)
        self.assertEqual(
            after, before,
            msg="PD-13/INV-6: the observation WRITES the store (it must be a "
                "read-only access, `mode=ro`): %r"
                % sorted(set(after) ^ set(before)))

        match = re.search(r'"store_reads"\s*:\s*(\d+)', out_text(proc))
        self.assertIsNotNone(
            match,
            msg="PD-13: the observation must declare its store read counter "
                "(`store_reads`) — count of accesses of this invocation: %r"
                % out_text(proc)[:400])
        self.assertLessEqual(
            int(match.group(1)), 1,
            msg="PD-13/INV-6: one invocation performs a SINGLE bounded read of "
                "the store (no polling): declared %s" % match.group(1))


# --------------------------------------------------------------------- PD-10


class TestPd10Capabilities(U2ModuleCase):
    """PD-10/§2.2/§2.3/O-3: `capabilities` answers the five declared keys; with
    the schema of the installed version it accredits the correlation and names
    the columns it evaluates, with a store that exposes only `agent` it denies
    it naming the missing discriminating key, and a module without the new
    surface does not accredit (it declares what is missing)."""

    CAPABILITY_KEYS = (
        "native_observation", "external_transport", "session_correlation",
        "version", "reason",
    )

    def capabilities_document(self, ctx: dict, store: Path,
                              label: str) -> dict:
        fake = self.fake_runtime()
        self.patch_config(fake, {"sessions_db": str(store)})
        proc = self.run_module(
            ctx, "--exec-config", str(fake["config"]), "--capabilities")
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: `--capabilities` must answer: rc=%s stdout=%s stderr=%s"
                % (label, proc.returncode, tail(out_text(proc)),
                   tail(err_text(proc))))
        try:
            document = json.loads(out_text(proc) or "null")
        except json.JSONDecodeError:
            self.fail("%s: the capabilities document is not JSON: %r"
                      % (label, out_text(proc)[:400]))
        self.assertIsInstance(document, dict, "%s: not an object" % label)
        for key in self.CAPABILITY_KEYS:
            self.assertIn(key, document, "%s: the document lacks %r" % (label, key))
        return document

    def test_pd10_installed_schema_accredits_correlation_and_names_columns(
            self) -> None:
        """PD-10/§2.3: with the schema observed on the installed version
        (`parent_id`, `directory`, `time_created` included, so a discriminating
        key exists) `session_correlation` is TRUE, the document names the
        columns observed, and `version` is the observed one. RED today: the
        module has no `--capabilities` surface."""
        ctx = self.new_project()
        store = self.write_store(
            self.base / "cap-store" / "sessions.db",
            ["id TEXT PRIMARY KEY", "parent_id TEXT", "directory TEXT",
             "agent TEXT", "model TEXT", "time_created REAL",
             "time_idle REAL", "idle_outcome TEXT"],
            [])
        document = self.capabilities_document(ctx, store, "PD-10 instalado")
        self.assertTrue(
            document["session_correlation"],
            msg="PD-10/O-3: the installed schema exposes a discriminating key "
                "(parent_id/directory/time_created) and reaches the threshold: "
                "session_correlation must be true: %r" % document)
        self.assertRegex(
            json.dumps(document),
            "parent_id|directory|time_created",
            msg="PD-10: the document must declare the columns the observed "
                "version exposes: %r" % document)
        self.assertEqual(
            document["version"], FAKE_VERSION,
            msg="PD-10/§2.2: `version` is the version OBSERVED on the binary "
                "(never a supposed one): %r" % document["version"])
        self.assertTrue(
            document["external_transport"],
            msg="PD-10/§2.2: the module launches/waits/collects a process: "
                "external_transport must be true: %r" % document)

    def test_pd10_only_agent_store_denies_correlation_naming_the_key(
            self) -> None:
        """PD-10/O-3: a store that exposes ONLY `agent` (no discriminating key)
        denies `session_correlation` and its `reason` names the missing
        discriminating key. RED today: the reason names the absent surface, not
        the discriminating key."""
        ctx = self.new_project()
        store = self.write_store(
            self.base / "cap-store-agent" / "sessions.db",
            list(AGENT_ONLY_COLUMNS),
            [{"id": STORE_SESSION, "agent": "cdad-test-writer"}])
        document = self.capabilities_document(ctx, store, "PD-10 sólo agente")
        self.assertFalse(
            document["session_correlation"],
            msg="PD-10/O-3: with only `agent` evaluable there is no "
                "discriminating key (two concurrent dispatches of the same role "
                "share it): session_correlation must be false: %r" % document)
        self.assertTrue(
            document.get("reason"),
            msg="PD-10: a denied capability declares its `reason`: %r"
                % document)
        self.assertRegex(
            json.dumps(document),
            r"(?i)parent|padre|moment|momento|proyect|project|director|directory",
            msg="PD-10/O-3: the `reason` must NAME the missing discriminating "
                "key: %r" % document)

    def test_pd10_module_without_the_new_surface_does_not_accredit(self) -> None:
        """PD-10/§2.2 (O-6; anchor, declared): a module that does not implement
        the new surface cannot be accredited: the entry declares
        `native_observation: false` with a `reason` naming the missing surface
        — no silent degradation. The fixture STAGES a copy of the skill tree
        (byte copy, no inspection) and replaces only the module, so the oracle
        stays meaningful after U2 lands."""
        stage_root = self.base / "staged-skill" / "cdad-cycle"
        shutil.copytree(SKILL_DIR, stage_root,
                        ignore=shutil.ignore_patterns("__pycache__"))
        staged_module = stage_root / "scripts" / "cdad_delegate_opencode.py"
        staged_module.write_text(LEGACY_MODULE_SOURCE, encoding="utf-8")
        store = self.write_store(
            self.base / "stub-store" / "sessions.db",
            list(AGENT_ONLY_COLUMNS), [])
        write_json(self.xdg / CONFIG_DIR_NAME / RUNTIMES_FILE_NAME, {
            "version": 1,
            "runtimes": {
                RUNTIME: {
                    "binary": str(self.fake_runtime()["binary"]),
                    "binary_version": FAKE_VERSION,
                    "mode": "standalone",
                    "sessions_db": str(store),
                    "wait": dict(WAIT),
                },
            },
        })
        proc = subprocess.run(
            [sys.executable, str(stage_root / "scripts" / "cdad_dispatch.py"),
             "capabilities", "--project-root", str(self.base),
             "--runtime", RUNTIME, "--json"],
            capture_output=True, env=self.child_env(pwd=self.base),
            cwd=str(self.base), timeout=120)
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-10/§2.2: the entry must DECLARE the missing surface (rc=0, "
                "never a silent fallback): rc=%s stdout=%s stderr=%s"
                % (proc.returncode, tail(out_text(proc)), tail(err_text(proc))))
        document = json.loads(out_text(proc))
        self.assertFalse(
            document.get("native_observation"),
            msg="PD-10/§2.2: a module without the new surface cannot be "
                "accredited: %r" % document)
        self.assertRegex(
            out_text(proc),
            r"(?i)capabilit|surface|superficie|--observe",
            msg="PD-10/§2.2: the `reason` must name the missing surface: %r"
                % out_text(proc))


# --------------------------------------------------------------------- PD-23


class TestPd23DerivedArtifactKind(U2ModuleCase):
    """PD-23/§2.8/INV-14: the kind of the delivered part is DERIVED from the
    packet's role and substage (never the fixed constant) and the derived kind
    materializes with an identical sha into its role's allowed root."""

    def dispatch_and_receipt(self, ctx: dict, label: str) -> dict:
        fake = self.fake_runtime()
        out = self.envelope(self.dispatch(ctx, fake), label)
        self.assertEqual(
            out["termination"], "completed",
            msg="%s: the external dispatch must complete: %r"
                % (label, out.get("diagnosis")))
        return self.receipt_doc(ctx)

    def test_pd23_plan_review_kind_materializes_with_identical_sha(self) -> None:
        """PD-23/§2.8: a reviewer packet in `plan-review` delivers a part whose
        `artifact_kind` is `plan-review` and `materialize` accepts it with an
        identical sha inside `docs/specs/<feature>/`. RED today: the module
        declares the fixed `role-report`, which the closed table rejects for the
        reviewer ("a kind of another role fails in the closed §7 table")."""
        ctx = self.new_project(role="reviewer", substage="plan-review",
                               draft_plan=True)
        receipt = self.dispatch_and_receipt(ctx, "PD-23 plan-review")
        self.assertEqual(
            [part.get("artifact_kind") for part in receipt["parts"]],
            ["plan-review"],
            msg="PD-23: the reviewer's delivery in `plan-review` must declare "
                "`plan-review`: %r" % receipt["parts"])
        self.assert_materializes_with_identical_sha(
            ctx, "plan-review", "PD-23 plan-review")

    def test_pd23_test_writer_kind_materializes_with_identical_sha(self) -> None:
        """PD-23/§2.8: a test-writer packet outside `audit` delivers
        `test-writer-role-report` and `materialize` accepts it with an identical
        sha. RED today: the fixed `role-report` is rejected by the closed table
        (measured on this HEAD)."""
        ctx = self.new_project(role="test-writer", substage="red")
        receipt = self.dispatch_and_receipt(ctx, "PD-23 test-writer/red")
        self.assertEqual(
            [part.get("artifact_kind") for part in receipt["parts"]],
            [EXPECTED_KINDS[("test-writer", "red")]],
            msg="PD-23: the delivery of a test-writer packet in `red` must "
                "declare `test-writer-role-report`: %r" % receipt["parts"])
        self.assert_materializes_with_identical_sha(
            ctx, EXPECTED_KINDS[("test-writer", "red")], "PD-23 test-writer/red")

    def test_pd23_architect_draft_kind_stays_role_report(self) -> None:
        """PD-23/§2.8 (anchor, declared): the architect's report in `draft` is
        `role-report` (its row admits it) and keeps materializing with an
        identical sha — the derivation must not change it."""
        ctx = self.new_project(role="architect", substage="draft",
                               epic_plan_approved=True)
        receipt = self.dispatch_and_receipt(ctx, "PD-23 architect/draft")
        self.assertEqual(
            [part.get("artifact_kind") for part in receipt["parts"]],
            ["role-report"],
            msg="PD-23/§2.8: the architect's report in `draft` is the single "
                "part `role-report`: %r" % receipt["parts"])
        self.assert_materializes_with_identical_sha(
            ctx, "role-report", "PD-23 architect/draft")

    def test_pd23_scribe_declares_role_report_and_its_row_is_u7(self) -> None:
        """PD-23/§2.8.3/DEPENDENCY: the scribe's single part is `role-report`
        (declared by PD-23); the MATERIALIZATION of that row is U7's oracle
        (PD-26) and is deliberately NOT asserted here — this test only fixes the
        kind the delivery declares, so it does not fail for U7's absence."""
        ctx = self.new_project(role="scribe", substage="memory")
        receipt = self.dispatch_and_receipt(ctx, "PD-23 scribe/memory")
        self.assertEqual(
            [part.get("artifact_kind") for part in receipt["parts"]],
            ["role-report"],
            msg="PD-23/§2.8.3: the scribe's single part is the role report "
                "(`role-report`): %r" % receipt["parts"])


if __name__ == "__main__":
    unittest.main(verbosity=2)



