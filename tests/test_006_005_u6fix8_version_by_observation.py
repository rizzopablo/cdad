#!/usr/bin/env python3
"""006-005 U6-8 RED — the runtime version is OBSERVED, never read from the
configuration.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved, sha256
3a824be3…): PD-10 (`capabilities` answers the five keys of §2.2; `version` is
the OBSERVED one, never a supposed one), §2.2 (the declared version is
`binary_version`, with the preflight's existing gate), §2.3 + PD-12 (each path
requires the keys it evaluates and fails closed NAMING the absent ones),
E5/PD-25 (§2.6.1: the bounded migration step, verified by `capabilities`).
Source of the finding and of the decision corrected here:
`docs/epics/epic-006-opencode-concurrency/execution.md`, finding U6-8 — the
control compares the OBSERVED versions, CLIENT against SERVER, never against a
number written in the configuration; the compatibility of the store is verified
by CAPACITY (a missing column the correlation evaluates ⇒ fail-closed naming
it); and `binary_version` becomes OPTIONAL and informative: a difference is
DECLARED in the diagnostic and does NOT block, and `migrate` stops writing it.

OBSERVED DEFECT (the walk of U6-8): with a section whose `binary_version` does
not match the observed runtime, the dispatch ends `blocked` with «server
version '1.0.0' does not match the configured `binary_version` '0.9.0'» — the
gate binds a number written in the configuration instead of comparing the two
OBSERVED versions. This RED observes the REAL entry and the REAL runtime
module; the defect is in the product, not in a fixture.

Oracle discipline (black box). The entry `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked AS A PROCESS from a staged copy of the skill
tree, so the REAL runtime module `cdad_delegate_opencode.py` is the one
resolved by the `opencode` section of `runtimes.json` under a temporary
`XDG_CONFIG_HOME`/`HOME`. Nothing of the implementation is read or imported:
the observed surface is the exit code, the declared envelope (stdout JSON),
the I8 record the module writes, the fake binary's own call log and the
`runtimes.json` the migration writes. The user's real config, store, binary
and credential are never read nor written; every value is a per-test
temporary or an invented sentinel (no host value, INV-7/INV-11).

FIXTURE INTERFACE, DECLARED (the surface this RED pins):

  * runtime id `opencode` — its module is `cdad_delegate_opencode.py` next to
    the staged entry (the product's own module convention, §2.2);
  * a fake runtime binary that reports a CONFIGURABLE CLIENT version
    (`--version`) and records EVERY invocation (argv) in its own log; the
    observed SERVER version is what the fake `/api/info` server returns (the
    same surface the preflight already reads);
  * a disposable store with the REAL shape of the installed version (V-7
    probe): `id, parent_id, agent, model, time_created (INTEGER epoch ms),
    time_idle, idle_outcome, directory` plus the assistant-message table;
  * `runtimes.json` section with the fake binary, the disposable store, a
    bounded wait and — when the case declares it — a `binary_version` that
    DIFFERS from the observed one.

MAPPING (one test per contracted behaviour; every docstring names its
postcondition):

  PD-10/E5 (U6-8) test_u68_configured_version_difference_does_not_block_the_dispatch
  PD-10/E5 (U6-8) test_u68_dispatch_without_configured_version_proceeds_and_capabilities_report_the_observed_one
  PD-10/E5 (U6-8) + PD-12  test_u68_observed_client_and_server_versions_that_differ_fail_closed_naming_both
  PD-10/E5 (U6-8) + PD-12  test_u68_store_without_a_correlation_column_fails_closed_naming_the_column
  PD-10/E5 (U6-8) + PD-25/§2.6.1  test_u68_migrate_does_not_write_the_configured_version

EXPECTED RED TODAY (declared, measured on this HEAD, never accidental):

  * RED — the configured difference BLOCKS the dispatch (the defect):
    `test_u68_configured_version_difference_does_not_block_the_dispatch` fails
    on its FIRST behavioural assertion (the termination is `blocked`, not
    `completed`); the declared difference is never reached.
  * RED — the migration step still WRITES `binary_version`:
    `test_u68_migrate_does_not_write_the_configured_version` fails on the
    written section (the key is present in `runtimes.json`).
  * DECLARED GUARDS (green today, and the owner decision CONSERVES them — they
    protect the fix from over-correcting):
    `test_u68_dispatch_without_configured_version_proceeds_and_capabilities_
    report_the_observed_one` (the key is optional: without it the dispatch
    proceeds and `capabilities` reports the OBSERVED version),
    `test_u68_observed_client_and_server_versions_that_differ_fail_closed_
    naming_both` (the OBSERVED client against the OBSERVED server: fail-closed
    before launching the errand, naming both versions) and
    `test_u68_store_without_a_correlation_column_fails_closed_naming_the_
    column` (the store's compatibility is verified by CAPACITY).

A-1 (declared in this RED, with the replaced test, the amended postcondition
and the reason): the existing tests that fixed the OLD behaviour — the
migration step carrying `binary_version` into the section — are reformulated
in `tests/test_006_005_u1a_runtime_config.py` (the U1a focal):
`test_pd9_derived_section_is_inspected_key_by_key`,
`test_pd25_migrate_without_section_writes_the_section_key_by_key` and
`test_pd25_migrate_dry_run_does_not_write`. Amended postcondition: PD-25 /
§2.6.1 — the migration writes the section key by key EXCEPT `binary_version`,
which becomes optional and informative (owner decision U6-8: the version is
observed, a difference with the configured one is declared and does not block,
and `migrate` stops writing it). Reason: the decision of the owner recorded in
`docs/epics/epic-006-opencode-concurrency/execution.md` (finding U6-8); the
key stays part of the section's vocabulary and the missing-section diagnostic
keeps naming it in the key-by-key correspondence, so
`test_pd9_missing_section_diagnostic_names_file_section_and_correspondence` is
CONSERVED and untouched. The other occurrences of `binary_version` in the
suite (006-001, 006-003, 005-009, 005-010, U1b, U2 and the U6-fix focals) are
fixtures that declare the OBSERVED version or use a stub module: they fix no
blocked-by-configured-version behaviour and are CONSERVED untouched (searched
and measured, see the role report).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import build_project, read_state
from test_005_009_t1_interface import (
    OUTPUT_KEYS,
    TERMINATION_VOCABULARY,
    dispatch_records,
)
from test_006_001_t1_selection import FakeInfoServer

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
AGENTS_SOURCE = REPO_ROOT / "agents"
AGENTS_ENV = "CDAD_OPENCODE_AGENTS_DIR"

RUNTIME = "opencode"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

# §2.1: the envelope of the entry is exactly the declared key set, with
# `termination` in the closed vocabulary.
ENVELOPE_KEYS = OUTPUT_KEYS

# The OBSERVED versions (never host values): the fake binary reports the
# client version with `--version`; the fake `/api/info` server reports the
# server version. The control compares these two OBSERVED values.
CLIENT_VERSION = "opencode u6fix8 3.1.4"
CLIENT_SEMVER = CLIENT_VERSION.rsplit(" ", 1)[-1]        # "3.1.4"
SERVER_VERSION = CLIENT_SEMVER                          # the observed ones agree
SERVER_VERSION_OTHER = "9.9.9"                          # ... or they do not

# The CONFIGURED version: what the section of `runtimes.json` declares. It
# differs from the observed one — the case the owner decided (U6-8).
CONFIGURED_VERSION = "opencode u6fix8 2.0.0"
CONFIGURED_SEMVER = CONFIGURED_VERSION.rsplit(" ", 1)[-1]  # "2.0.0"

# A sentinel invented here; never a host credential (INV-11).
CREDENTIAL_SENTINEL = "cdad-006-005-u6fix8-sentinel-credential"

# V-7 probe (execution.md §«006-005: sonda V-7»): the INSTALLED version's
# `session_v2` and its real types/units. `time_created` is an INTEGER in
# epoch MILLISECONDS.
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
# The same store WITHOUT a column the correlation evaluates: the durable
# identity (`session_v2.agent`) is what the external path corroborates (§2.3).
STORE_COLUMNS_WITHOUT_AGENT = [
    column for column in STORE_COLUMNS if not column.startswith("agent ")
]

FINAL_TEXT = "006-005 U6-8 fixture final text\n"

# ------------------------------------------------------- fixture: fake binary

FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
"""Fake OpenCode runtime binary — fixture of
tests/test_006_005_u6fix8_version_by_observation.py. NOT the product.

Declared protocol (the whole surface the oracles observe):
  1. EVERY invocation appends one JSON line to `<fake>/calls.jsonl`:
     {"argv": [...], "agent": <--agent>, "session": <--session>}.
  2. `--version` prints `<fake>/version.txt` — the OBSERVED CLIENT version —
     and exits 0.
  3. Any other invocation writes the durable row into the store declared by
     `<fake>/store.json` (the real V-7 shape), writes the assistant message
     and prints the final text.
"""
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


_session = _option("--session") or "ses-fake-default"
_agent = _option("--agent") or "cdad-test-writer"
with (_FAKE / "calls.jsonl").open("a", encoding="utf-8") as handle:
    handle.write(json.dumps({"argv": sys.argv[1:], "agent": _agent,
                             "session": _session}, sort_keys=True) + "\n")

if "--version" in sys.argv[1:]:
    sys.stdout.write((_FAKE / "version.txt").read_text(encoding="utf-8").strip()
                     + "\n")
    sys.stdout.flush()
    sys.exit(0)

_spec = json.loads((_FAKE / "store.json").read_text(encoding="utf-8"))
_store = Path(_spec["path"])
_store.parent.mkdir(parents=True, exist_ok=True)
_connection = sqlite3.connect(str(_store))
try:
    _connection.execute("CREATE TABLE IF NOT EXISTS session_v2 (%s)"
                        % ", ".join(_spec["columns"]))
    _connection.execute("CREATE TABLE IF NOT EXISTS session_message ("
                        "id TEXT PRIMARY KEY, session_id TEXT, type TEXT,"
                        " seq INTEGER, data TEXT)")
    _now = time.time()
    _values = {}
    for _declaration in _spec["columns"]:
        _column = _declaration.split()[0]
        if _column == "id":
            _values[_column] = _session
        elif _column == "agent":
            _values[_column] = _agent
        elif _column == "model":
            _values[_column] = _spec.get("model", "fixture-model")
        elif _column == "directory":
            _values[_column] = (_spec.get("directory")
                                or os.environ.get("PWD"))
        elif _column == "parent_id":
            _values[_column] = _spec.get("parent_id")
        elif _column in ("time_created", "time_updated"):
            _values[_column] = int(_now * 1000)
        elif _column == "time_idle":
            _values[_column] = _now
        elif _column == "idle_outcome":
            _values[_column] = _spec.get("outcome", "succeeded")
        else:
            _values[_column] = None
    _columns = list(_values)
    _connection.execute("INSERT OR REPLACE INTO session_v2 (%s) VALUES (%s)"
                        % (", ".join(_columns), ", ".join("?" * len(_columns))),
                        [_values[column] for column in _columns])
    _connection.execute("INSERT OR REPLACE INTO session_message VALUES"
                        " (?,?,?,?,?)",
                        (_session + "-final", _session, "assistant", 1,
                         json.dumps({"content": [{"type": "text",
                                                  "text": _spec["final_text"]}]})))
    _connection.commit()
finally:
    _connection.close()

sys.stdout.write(_spec["final_text"])
if not _spec["final_text"].endswith("\n"):
    sys.stdout.write("\n")
sys.stdout.flush()
sys.exit(0)
'''


# -------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


def write_json(path: Path, document: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


# -------------------------------------------------------------------- fixture


class U6Fix8Case(unittest.TestCase):
    """Disposable project + staged skill tree with the REAL `opencode` module,
    a redirected `XDG_CONFIG_HOME`/`HOME`, a fake binary that reports a
    configurable client version and a disposable store with the installed
    version's real shape (V-7)."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u6fix8-")
        self.base = Path(self._tmp.name).resolve()
        self.config_home = self.base / "config-home"
        self.config_home.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.fixture_dir = self.base / "fixture"
        self.fixture_dir.mkdir()

        # The staged tree: the REAL runtime module is the one resolved next to
        # the entry (the product's own convention, §2.2). The copy is byte for
        # byte; nothing of it is read by this session.
        self.stage = self.base / "stage"
        shutil.copytree(SKILL_DIR, self.stage,
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.scripts = self.stage / "scripts"
        self.entry = self.scripts / "cdad_dispatch.py"
        self.assertTrue(
            self.entry.is_file(),
            msg="precondición (fixture): no existe la entrada en el producto "
                "(se espera %s por U1a del plan)"
                % ENTRY_PRODUCT.relative_to(REPO_ROOT))
        self.assertTrue(
            (self.scripts / MODULE_NAME).is_file(),
            msg="precondición (fixture): el módulo REAL del runtime (%s) no "
                "existe junto a la entrada; este RED no usa un módulo falso "
                "que reemplace la comparación de versiones (U6-8)" % MODULE_NAME)

        self.binary = self.write_fake_binary(CLIENT_VERSION)
        self.store_path = self.fixture_dir / "sessions.db"
        self.write_store(STORE_COLUMNS)
        self.write_runtimes(self.section())

        self.project = self.new_project()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- harness ------------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        # A sentinel invented here; the host's credential never reaches the
        # child (INV-11).
        env["OPENCODE_PASSWORD"] = CREDENTIAL_SENTINEL
        env.pop("OPENCODE_SERVER_PASSWORD", None)
        env.pop("CDAD_EXEC_CONFIG", None)
        return env

    def run_entry(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.entry), *args],
            cwd=str(self.project["root"]), env=self.env(), capture_output=True,
            text=True, check=False, timeout=300)

    @staticmethod
    def output(proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout or "") + (proc.stderr or "")

    # -- fixture data -------------------------------------------------------

    def write_fake_binary(self, version: str) -> Path:
        path = self.fixture_dir / "bin" / "opencode-u6fix8"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(FAKE_BINARY_SOURCE, encoding="utf-8")
        path.chmod(0o755)
        (self.fixture_dir / "version.txt").write_text(version + "\n",
                                                      encoding="utf-8")
        write_json(self.fixture_dir / "store.json", {
            "path": str(self.fixture_dir / "sessions.db"),
            "columns": list(STORE_COLUMNS),
            "final_text": FINAL_TEXT,
        })
        return path

    def write_store(self, columns: list) -> Path:
        """Disposable store with the REAL shape of the installed version (V-7):
        `time_created` INTEGER in epoch MILLISECONDS."""
        path = self.store_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        connection = sqlite3.connect(str(path))
        try:
            connection.execute("CREATE TABLE session_v2 (%s)"
                               % ", ".join(columns))
            connection.execute(
                "CREATE TABLE session_message (id TEXT PRIMARY KEY,"
                " session_id TEXT, type TEXT, seq INTEGER, data TEXT)")
            connection.commit()
        finally:
            connection.close()
        # The fake reads the declared columns when it writes the row.
        write_json(self.fixture_dir / "store.json", {
            "path": str(path),
            "columns": list(columns),
            "final_text": FINAL_TEXT,
        })
        return path

    def section(self, **overrides) -> dict:
        """§2.6: the runtime section of `runtimes.json`."""
        section = {
            "binary": str(self.binary),
            "binary_version": CONFIGURED_VERSION,
            "mode": "server",
            "auto": True,
            "sessions_db": str(self.store_path),
            "wait": {"timeout_seconds": 30},
        }
        section.update(overrides)
        return section

    def runtimes_path(self) -> Path:
        return self.config_home / "cdad" / "runtimes.json"

    def write_runtimes(self, section: dict) -> Path:
        return write_json(self.runtimes_path(), {
            "version": 1, "runtimes": {RUNTIME: section}})

    def start_server(self, version: str) -> FakeInfoServer:
        """The fake `/api/info` server: it reports the OBSERVED SERVER
        version (the surface the preflight already reads)."""
        server = FakeInfoServer(
            body=json.dumps({"version": version}).encode())
        self.addCleanup(server.stop)
        return server

    def new_project(self) -> dict:
        """A disposable project with a canonical packet published by
        `prepare` (with the derived agents adopted, I9)."""
        root = self.base / "project"
        root.mkdir(parents=True, exist_ok=True)
        build_project(root)
        env = self.env()
        env[AGENTS_ENV] = str(AGENTS_SOURCE)
        proc = subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "006-005 U6-8 fixture (test-writer/red)"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env)
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición (fixture): `prepare` no publicó el paquete "
                "(test-writer/red):\n%s" % tail(self.output(proc)))
        state = read_state(root)
        return {
            "root": root,
            "execution_id": state["execution"]["id"],
            "packet_id": state["active_packet"]["id"],
        }

    # -- invocations --------------------------------------------------------

    def dispatch(self) -> subprocess.CompletedProcess:
        return self.run_entry(
            "dispatch", "--project-root", str(self.project["root"]),
            "--packet", self.project["packet_id"], "--runtime", RUNTIME,
            "--json")

    def capabilities(self) -> subprocess.CompletedProcess:
        return self.run_entry("capabilities", "--runtime", RUNTIME, "--json")

    def migrate(self, legacy: Path, *extra: str
                ) -> subprocess.CompletedProcess:
        return self.run_entry(
            "migrate", "--runtime", RUNTIME,
            "--legacy-exec-config", str(legacy), "--json", *extra)

    def legacy_exec_config(self) -> Path:
        """A retired exec-config (§2.6): the section keys plus `runtime`,
        `model` and the credential route (the latter two never migrate)."""
        document = {
            "runtime": RUNTIME,
            "model": "fixture/u6fix8-model",
            "credential_env_file": "/fixture/credentials/opencode-server.env",
        }
        document.update(self.section())
        return write_json(self.fixture_dir / "legacy-exec-config.json",
                          document)

    # -- observations -------------------------------------------------------

    def envelope(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: la entrada no completó (rc=%s):\n%s"
                % (label, proc.returncode, tail(self.output(proc), 40)))
        try:
            out = json.loads(proc.stdout or "null")
        except json.JSONDecodeError:
            self.fail(msg="%s: stdout no es el sobre JSON declarado (§2.1):\n%s"
                          % (label, tail(proc.stdout, 40)))
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

    def records(self) -> dict:
        return dispatch_records(self.project["root"],
                                self.project["execution_id"])

    def single_record(self, before: dict) -> dict:
        """PD-1: exactly ONE attempt per dispatch."""
        new = {stem: path for stem, path in self.records().items()
               if stem not in set(before) and not stem.startswith(".")}
        self.assertEqual(
            len(new), 1,
            msg="PD-1: el despacho dejó %d registros I8 nuevos (se espera "
                "exactamente uno): %r" % (len(new), sorted(new)))
        return json.loads(next(iter(new.values())).read_text(encoding="utf-8"))

    def calls(self) -> list:
        path = self.fixture_dir / "calls.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def errand_invocations(self) -> list:
        """The invocations that actually LAUNCH the errand (`run`)."""
        return [call for call in self.calls() if "run" in call.get("argv", [])]

    def version_invocations(self) -> list:
        """The preflight's probes of the client's version."""
        return [call for call in self.calls()
                if "--version" in call.get("argv", [])]

    def declaration_text(self, out: dict, record: dict | None = None) -> str:
        """Only the DIAGNOSTIC the invocation declares (the envelope's
        `diagnosis` and the record's `provenance` values)."""
        parts: list = []
        if out.get("diagnosis"):
            parts.append(str(out["diagnosis"]))
        if record is not None:
            provenance = record.get("provenance")
            if isinstance(provenance, dict):
                parts.extend(str(value) for value in provenance.values())
        return "\n".join(parts)


# ------------------------------------------------- PD-10/E5 (U6-8): the version


class TestU68VersionByObservation(U6Fix8Case):
    """PD-10/E5 (U6-8): the control compares the OBSERVED versions (client
    against server); the CONFIGURED `binary_version` is optional and
    informative — a difference is DECLARED and does not block; and the
    migration step stops writing it."""

    def test_u68_configured_version_difference_does_not_block_the_dispatch(
            self) -> None:
        """PD-10/E5 (U6-8): the section declares a `binary_version` that
        DIFFERS from the observed one; the OBSERVED client and the OBSERVED
        server AGREE and the store exposes the columns the correlation
        evaluates ⇒ the dispatch is NOT blocked: the errand runs and the
        delivery happens. The difference is DECLARED (in the diagnostic or in
        the provenance) with the CONFIGURED value."""
        server = self.start_server(SERVER_VERSION)
        self.write_runtimes(self.section(server=server.url))
        before = self.records()

        proc = self.dispatch()
        out = self.envelope(proc, "PD-10/E5 (U6-8) diferencia de la "
                                 "versión configurada")
        self.assertEqual(
            out.get("termination"), "completed",
            msg="PD-10/E5 (U6-8): una `binary_version` CONFIGURADA distinta de "
                "la OBSERVADA no bloquea el despacho (cliente observado == "
                "servidor observado, store con las columnas): la "
                "terminación es %r (diagnóstico: %r). El control compara las "
                "versiones OBSERVADAS, no un número escrito en la config."
                % (out.get("termination"), out.get("diagnosis")))
        self.assertTrue(
            self.errand_invocations(),
            msg="PD-10/E5 (U6-8): el encargo no se lanzó (el binario no "
                "recibió `run`): el despacho quedó sin hacer el trabajo")
        self.assertTrue(
            out.get("delivery_ref"),
            msg="PD-10/E5 (U6-8): el despacho no deliversó entrega "
                "(`delivery_ref` vacío)")

        record = self.single_record(before)
        declaration = self.declaration_text(out, record)
        self.assertTrue(
            CONFIGURED_VERSION in declaration
            or CONFIGURED_SEMVER in declaration,
            msg="PD-10/E5 (U6-8): la diferencia entre la versión CONFIGURADA "
                "y la OBSERVADA no se declara (ni el diagnóstico ni la "
                "procedencia nombran el valor configurado %r):\n%s"
                % (CONFIGURED_VERSION, tail(declaration, 40)))

    def test_u68_dispatch_without_configured_version_proceeds_and_capabilities_report_the_observed_one(
            self) -> None:
        """PD-10/E5 (U6-8): a section WITHOUT `binary_version` (the key is
        OPTIONAL) ⇒ the dispatch proceeds normally and `capabilities` reports
        the OBSERVED version (never a supposed one)."""
        server = self.start_server(SERVER_VERSION)
        section = self.section(server=server.url)
        section.pop("binary_version")
        self.write_runtimes(section)

        proc = self.dispatch()
        out = self.envelope(proc, "PD-10/E5 (U6-8) sin versión configurada")
        self.assertEqual(
            out.get("termination"), "completed",
            msg="PD-10/E5 (U6-8): sin `binary_version` en la sección el "
                "despacho procede normalmente; la terminación es %r "
                "(diagnóstico: %r)"
                % (out.get("termination"), out.get("diagnosis")))

        capabilities = self.capabilities()
        self.assertEqual(
            capabilities.returncode, 0,
            msg="PD-10/E5 (U6-8): `capabilities --runtime %s` no completó "
                "(rc=%s):\n%s" % (RUNTIME, capabilities.returncode,
                                  tail(self.output(capabilities), 40)))
        try:
            document = json.loads(capabilities.stdout or "null")
        except json.JSONDecodeError:
            self.fail(msg="PD-10/E5 (U6-8): stdout de `capabilities` no es el "
                          "documento JSON declarado (§2.2):\n%s"
                          % tail(capabilities.stdout, 40))
        self.assertIsInstance(
            document, dict,
            msg="PD-10/E5 (U6-8): el documento de capacidades no es un "
                "objeto: %r" % (document,))
        self.assertIn(
            "version", document,
            msg="PD-10/E5 (U6-8): el documento de capacidades no responde la "
                "clave declarada `version` (§2.2): %r" % (document,))
        self.assertNotEqual(
            document["version"], "unknown",
            msg="PD-10/E5 (U6-8): la versión OBSERVADA es conocida (el binario "
                "de fixture la reporta): `version` no puede ser `unknown`: %r"
                % (document,))
        self.assertIn(
            CLIENT_SEMVER, str(document["version"]),
            msg="PD-10/E5 (U6-8): `version` no es la versión OBSERVADA "
                "(se espera %r): %r" % (CLIENT_VERSION, document["version"]))

    # -- the two fail-closed paths the decision conserves ------------------

    def test_u68_observed_client_and_server_versions_that_differ_fail_closed_naming_both(
            self) -> None:
        """PD-10/E5 (U6-8) + PD-12: the OBSERVED client version and the
        OBSERVED server version DIFFER ⇒ fail-closed BEFORE launching the
        errand, naming BOTH versions. The configured value is irrelevant here
        (it matches the observed client): the control compares the two
        OBSERVED versions."""
        server = self.start_server(SERVER_VERSION_OTHER)
        self.write_runtimes(self.section(server=server.url,
                                         binary_version=CLIENT_VERSION))

        proc = self.dispatch()
        out = self.envelope(proc, "PD-10/E5 (U6-8) cliente != servidor")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="PD-10/E5 (U6-8)/PD-12: el cliente OBSERVADO (%s) y el "
                "servidor OBSERVADO (%s) no coinciden ⇒ la terminación no es "
                "`blocked`: %r (diagnóstico: %r)"
                % (CLIENT_SEMVER, SERVER_VERSION_OTHER,
                   out.get("termination"), out.get("diagnosis")))
        diagnosis = str(out.get("diagnosis") or "")
        for version in (CLIENT_SEMVER, SERVER_VERSION_OTHER):
            self.assertIn(
                version, diagnosis,
                msg="PD-10/E5 (U6-8)/PD-12: el diagnóstico no nombra la "
                    "versión observada %r (debe nombrar LAS DOS): %r"
                    % (version, diagnosis))
        self.assertTrue(
            self.version_invocations(),
            msg="PD-10/E5 (U6-8)/PD-12: el cliente no se sondeó (`--version`): "
                "no hubo versión OBSERVADA que comparar")
        self.assertFalse(
            self.errand_invocations(),
            msg="PD-10/E5 (U6-8)/PD-12: el encargo se lanzó pese al "
                "desajuste de las versiones observadas (fail-closed ANTES de "
                "lanzar)")

    def test_u68_store_without_a_correlation_column_fails_closed_naming_the_column(
            self) -> None:
        """PD-10/E5 (U6-8) + PD-12: the store does NOT expose a column the
        correlation evaluates (the durable identity, `session_v2.agent`) and
        the observed versions MATCH ⇒ the compatibility of the store is
        verified by CAPACITY: fail-closed NAMING the absent column."""
        server = self.start_server(SERVER_VERSION)
        self.write_store(STORE_COLUMNS_WITHOUT_AGENT)
        self.write_runtimes(self.section(server=server.url,
                                         binary_version=CLIENT_VERSION))

        proc = self.dispatch()
        out = self.envelope(proc, "PD-10/E5 (U6-8) store sin columna")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="PD-10/E5 (U6-8)/PD-12: un store sin la columna que la "
                "correlación evalúa no puede entregar: la terminación no es "
                "`blocked`: %r (diagnóstico: %r)"
                % (out.get("termination"), out.get("diagnosis")))
        diagnosis = str(out.get("diagnosis") or "")
        self.assertRegex(
            diagnosis, re.compile(r"(?i)\bagent\b"),
            msg="PD-10/E5 (U6-8)/PD-12: el diagnóstico no nombra la columna "
                "ausente que la correlación evalúa (`agent`): %r" % diagnosis)
        self.assertRegex(
            diagnosis, re.compile(r"(?i)store|schema|sesión|session"),
            msg="PD-10/E5 (U6-8)/PD-12: el diagnóstico no declara que lo que "
                "falta es la capacidad del store: %r" % diagnosis)

    # -- the migration step (E5) -------------------------------------------

    def test_u68_migrate_does_not_write_the_configured_version(self) -> None:
        """PD-10/E5 (U6-8) + PD-25/§2.6.1: the bounded migration step writes
        the runtime section WITHOUT `binary_version` — the key becomes
        OPTIONAL and informative (the version is observed; a difference with
        the configured one is declared and does not block), so the migration
        stops carrying a version number that can drift."""
        legacy = self.legacy_exec_config()
        self.assertEqual(
            legacy.read_text(encoding="utf-8").count(CONFIGURED_VERSION), 1,
            msg="precondición (fixture): el exec-config heredado NO declara "
                "`binary_version` (%r)" % CONFIGURED_VERSION)
        # The migration writes the section ONLY when it does not exist
        # (PD-25/INV-7): the fixture starts with no section at all.
        self.runtimes_path().unlink()
        self.assertFalse(
            self.runtimes_path().exists(),
            msg="precondición (fixture): la sección del runtime sigue "
                "existiendo: la migración la encontraría y se negaría")

        proc = self.migrate(legacy)
        output = self.output(proc)
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: la migración debe escribir la "
                "sección y terminar rc=0 (rc=%s):\n%s"
                % (proc.returncode, tail(output, 40)))
        path = self.runtimes_path()
        self.assertTrue(
            path.is_file(),
            msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: la migración no creó "
                "`runtimes.json`")
        document = json.loads(path.read_text(encoding="utf-8"))
        section = document.get("runtimes", {}).get(RUNTIME)
        self.assertIsInstance(
            section, dict,
            msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: la sección migrada no existe "
                "en `runtimes.json`: %r" % (document,))
        self.assertNotIn(
            "binary_version", section,
            msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: la migración NO escribe "
                "`binary_version` (la versión se OBSERVA; una diferencia con "
                "la configurada se declara y no bloquea): la sección migrada "
                "lo contiene (%r)" % section.get("binary_version"))
        for key in ("binary", "mode", "auto", "sessions_db", "wait"):
            self.assertIn(
                key, section,
                msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: la sección migrada no trae "
                    "la clave %r (claves: %s)" % (key, sorted(section)))
        self.assertNotIn(
            CONFIGURED_VERSION, path.read_text(encoding="utf-8"),
            msg="PD-10/E5 (U6-8)/PD-25/§2.6.1: el valor de la versión "
                "configurada (%r) viaja al documento del dueño: la migración "
                "deja de escribirlo" % CONFIGURED_VERSION)


if __name__ == "__main__":
    unittest.main(verbosity=2)
