#!/usr/bin/env python3
"""006-005 U6-4 RED — the native store's MOMENT (epoch milliseconds) and the
SELECTION of the candidate child under the declared parent.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved, sha256
3a824be3…): §2.2 (the module's bounded `--observe`), §2.3 (native correlation:
parent + agent + moment + project-by-membership, with the O-3 discrimination
threshold), PD-5, PD-6 (declared minor guarantee for a byte-exact native result
whose identity cannot be verified), O-3, INV-2 (never an invented session; a
contradiction is a rejection, `unknown` is not), INV-4 (closed/`unknown` with a
reason, never a silent fallback) and E1 (the native walk works even when the
coordinator was started from another folder / nested layout). Source of the
finding and of the decision corrected here: `docs/epics/epic-006-opencode-
concurrency/execution.md`, §«006-005 U6: recorrido real», finding U6-4, plus the
extended V-7 probe (same section): in the installed version's `session_v2`,
`time_created` is `INTEGER NOT NULL` in epoch MILLISECONDS, `parent_id` and
`agent` are `TEXT`, and `directory` is `TEXT NOT NULL`.

The defect this RED observes (two parts, as measured in the real walk):

  1. The store's instant is never interpretable: the entry only understands ISO
     instants, so the moment key stays `unknown` against the real store, and the
     degradation reuses the same words as the ancestor-directory case instead of
     naming the value as not interpretable (O-6/INV-4).
  2. The candidate under the parent is chosen arbitrarily (the first row): an
     earlier child of another role REJECTS a legitimate delivery, and two
     children of the packet's role after `--since` can be falsely accredited
     (INV-2).

Contract decision this RED pins (orchestrator, execution.md U6-4): candidates
are the rows under the declared parent whose agent is the packet's agent and
whose moment is AFTER `--since`. Exactly one ⇒ it is evaluated; none ⇒ there is
no row; more than one ⇒ nothing is accredited, the ambiguity is NAMED and it is
NEVER a rejection. A non-interpretable instant is named as such, and a
non-verified note also names the keys that DID match.

Oracle discipline (black box). The entry `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked AS A PROCESS from a staged copy of the skill tree,
so the REAL runtime module `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`
is the one resolved by the `opencode` section of `runtimes.json` under a
temporary `XDG_CONFIG_HOME` — no fake module replaces the candidate selection.
The store is a disposable SQLite database with the REAL shape above (epoch
milliseconds, not the invented `REAL` seconds of earlier fixtures). Nothing of
the implementation is read or imported: the observed surface is the exit code,
the declared envelope (stdout JSON), the I8 record the entry writes, the staged
inbox and the receipt's absence. The user's real config, store and binary are
neither read nor written; every fixture is a per-test temporary.

FIXTURE INTERFACE, DECLARED (the surface this RED pins):

  * runtime id `opencode` — its module is `cdad_delegate_opencode.py` next to the
    staged entry (the product's own module convention, §2.2);
  * `runtimes.json` section with a fake `binary` that reports `binary_version`
    (observed, never supposed), `mode: standalone`, the disposable
    `sessions_db` and a bounded wait;
  * the disposable store's `session_v2` carries the installed schema:
    `id, parent_id, agent, model, time_created (INTEGER ms), time_idle,
    idle_outcome, directory` (V-7 extended, execution.md);
  * `record --runtime opencode --parent <parent> --since <ISO UTC>` is the only
    invocation: the selection of the child is what is under test, so no
    `--session` is declared in the selection cases.

MAPPING (one test per contracted behavior of PD-5/E1, U6-4; every docstring
names the postcondition):

  PD-5/E1 (U6-4) — moment
    test_u64_verified_child_inside_the_root
    test_u64_ancestor_directory_is_verified_by_parent_and_moment
    test_u64_same_agent_child_before_since_is_not_a_candidate
  PD-5/E1 (U6-4) — candidate selection
    test_u64_earlier_child_of_another_role_is_not_a_candidate
    test_u64_two_candidates_are_ambiguous_and_never_accredited
    test_u64_no_candidate_earlier_child_is_not_a_rejection
    test_u64_no_candidate_other_agent_with_native_result_delivers_under_pd6
  PD-5/E1 (U6-4) — diagnostics
    test_u64_uninterpretable_instant_is_named_as_such
    test_u64_unverified_note_names_the_keys_that_matched

EXPECTED RED TODAY (declared, measured on this HEAD, never accidental): the
module's real store observation does not expose the moment, so the moment key is
`unknown`; the verification cases persist `session: null`; the earlier-child-of-
another-role and the only-child-of-another-role cases exit rc=1 with an `agent`
contradiction (a legitimate delivery rejected); the ambiguity and interpretable-
instant cases answer only «not evaluable: `moment`» without naming the ambiguity
or the uninterpretable value. Every focal failure is an AssertionError about
that missing behavior — never an ImportError, a SyntaxError or a fixture error.
The `no candidate, earlier child` case is a declared GUARD: it already answers
with no accredited session today (for the wrong reason: the moment is unknown),
and it becomes discriminating once the moment is interpreted (seconds vs
milliseconds).

A-1 (declared: no existing test is reformulated in this RED). The candidate
fixture named by the task, `tests/test_006_005_u2_opencode_module.py` (fixtures
`time_created REAL` = `time.time() - 5.0`, e.g. :1117-1123 and :1179-1186 in
`TestPd12Pd13ObserveSurface`), does NOT depend on the unit: the observation case
pins the row with `--session` and asserts the returned id (:1125-1143), and the
PD-13 case asserts the store's bytes and the `store_reads` counter
(:1177-1209); neither compares an instant against `--since`. No test of this
suite pins, as PRODUCT behavior, «take the first child under the parent»: the
U1b module is a fixture STUB of the module surface, not the selection under
test. Therefore the existing fixtures stay untouched.
"""

from __future__ import annotations

import datetime as dt
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

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

RUNTIME = "opencode"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

# §2.1: the envelope of `record` is exactly the declared key set, with
# `termination` in the closed vocabulary.
ENVELOPE_KEYS = OUTPUT_KEYS

PACKET_AGENT = "cdad-test-writer"
OTHER_ROLE_AGENT = "cdad-architect"

PARENT = "ses-parent-u6fix4-0001"

# Byte-exact native payload with deliberately awkward bytes: a normalizer
# (retipeo, summary, added trailing newline, CRLF rewrite) would change them.
NATIVE_PAYLOAD = (
    "# Native role report (006-005 U6-4 fixture)\n"
    "\n"
    "line with trailing spaces:   \n"
    "CRLF line\r\n"
    "last line without a final newline (byte-exactness matters)"
).encode("utf-8")

# V-7 extended probe (execution.md §«006-005: sonda V-7»): the INSTALLED
# version's `session_v2` and its real types/units. `time_created` is an INTEGER
# in epoch MILLISECONDS (not the invented `REAL` seconds of older fixtures).
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

FAKE_VERSION = "opencode v2.0.27-fixture"

# An instant the fixture can always express as ISO UTC and as epoch ms. The
# assertions never depend on the wall clock: the rows are placed BEFORE or
# AFTER this declared instant.
MOMENT = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) - dt.timedelta(
    minutes=10)
SINCE = MOMENT.strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch_ms(delta_seconds: int) -> int:
    """Epoch MILLISECONDS of the declared instant ± `delta_seconds`."""
    return int((MOMENT + dt.timedelta(seconds=delta_seconds)).timestamp()
               * 1000)


BEFORE_MS = epoch_ms(-60)
AFTER_MS = epoch_ms(60)
LATER_MS = epoch_ms(120)

# ------------------------------------------------------- fixture: fake binary

FAKE_BINARY_SOURCE = '''#!/usr/bin/env python3
"""Fake runtime binary — fixture of
tests/test_006_005_u6fix4_native_selection.py. NOT the product: it only reports
the version the capability document must observe as OBSERVED, never supposed."""
import sys

if "--version" in sys.argv[1:]:
    sys.stdout.write(__VERSION__ + "\\n")
    sys.stdout.flush()
    sys.exit(0)

sys.stderr.write("u6fix4 fake binary: only --version is declared\\n")
sys.exit(2)
'''

# ------------------------------------------------------------- diagnostics

# The value of the moment was read but cannot be interpreted as an instant:
# O-6/INV-4 requires NAMING it as such, never reusing the ancestor phrase of
# U6-3 («not evaluable: project (ancestro)»).
MOMENT_UNINTERPRETABLE_RE = re.compile(
    r"(?is)(?:moment|momento|time_created)[^.\n]{0,200}"
    r"(?:uninterpret|not interpretable|cannot be (?:read|interpret(?:ed)?)"
    r"|could not be (?:read|interpret(?:ed)?)|not readable|not a valid instant"
    r"|invalid instant|not an instant|not a timestamp|ilegible"
    r"|no se pudo (?:leer|interpretar))"
    r"|(?:uninterpret|not interpretable|cannot be (?:read|interpret(?:ed)?)"
    r"|could not be (?:read|interpret(?:ed)?)|not readable|not a valid instant"
    r"|invalid instant|not an instant|not a timestamp|ilegible"
    r"|no se pudo (?:leer|interpretar))[^.\n]{0,200}"
    r"(?:moment|momento|time_created)")

# U6-3 (unchanged): an ancestor session directory is NOT a contradiction; the
# project key is not evaluable and is NAMED as such.
PROJECT_NOT_EVALUABLE_RE = re.compile(
    r"(?is)(?:project|proyecto)[^.\n]{0,160}"
    r"(?:not evaluable|no evaluable|not evaluated|no evaluado|ancestor|ancestro"
    r"|unknown)"
    r"|(?:not evaluable|no evaluable|not evaluated|no evaluado|ancestor"
    r"|ancestro)[^.\n]{0,160}(?:project|proyecto)")

# U6-4: more than one candidate ⇒ the ambiguity is NAMED.
AMBIGUITY_RE = re.compile(
    r"(?i)ambigu|ambigü|more than one (?:row|candidate|session)"
    r"|multiple (?:rows|candidates|sessions)|not unique|no [uú]nic"
    r"|m[áa]s de un[ao]? (?:fila|candidat)")

# U6-4: a non-verified note names the keys that DID match (e.g. `parent`).
MATCHED_KEY_RE = re.compile(
    r"(?i)[^.\n]{0,120}"
    r"(?:match(?:ed|es|ing)?|coincid\w*|(?<!not )verified\s+by)"
    r"[^.\n]{0,120}(?:parent|padre)"
    r"|[^.\n]{0,120}(?:parent|padre)[^.\n]{0,120}"
    r"(?:match(?:ed|es|ing)?|coincid\w*)")

# ---------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


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
            "file", path.stat().st_size, path.read_bytes())
    return snapshot


def snapshot_diff(before: dict, after: dict) -> list:
    diff = ["created: %s" % key for key in sorted(set(after) - set(before))]
    diff += ["removed: %s" % key for key in sorted(set(before) - set(after))]
    diff += ["modified: %s" % key for key in sorted(set(before) & set(after))
             if before[key] != after[key]]
    return diff


# -------------------------------------------------------------------- fixture


class U6Fix4Case(unittest.TestCase):
    """Disposable project + staged skill tree with the REAL `opencode` module,
    a redirected `XDG_CONFIG_HOME`/`HOME`, a fake binary and a disposable store
    with the installed version's REAL shape (epoch milliseconds)."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u6fix4-")
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
                "existe junto a la entrada; este RED no usa un módulo falso "
                "que reemplace la selección (U6-4)" % MODULE_NAME)

        self.binary = self.write_fake_binary()
        self.store_path = self.fixture_dir / "sessions.db"
        self.write_store([])
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

    # -- fixture data -------------------------------------------------------

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "opencode-u6fix4"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            FAKE_BINARY_SOURCE.replace("__VERSION__", json.dumps(FAKE_VERSION)),
            encoding="utf-8")
        path.chmod(0o755)
        return path

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

    def row(self, session: str, *, agent: str = PACKET_AGENT,
            time_created: object = AFTER_MS, directory: str | None = None
            ) -> dict:
        """One `session_v2` row with the real shape. `directory` defaults to a
        directory INSIDE the authorized root (membership)."""
        return {
            "id": session,
            "parent_id": PARENT,
            "agent": agent,
            "model": "u6fix4-fixture-model",
            "time_created": time_created,
            "time_idle": None,
            "idle_outcome": "succeeded",
            "directory": directory if directory is not None
            else str(self.project["root"] / "nested"),
        }

    def write_runtimes(self) -> Path:
        """§2.6: the single source for the runtime configuration. The runtime
        id is `opencode`, so the REAL module next to the entry is resolved."""
        document = {
            "version": 1,
            "runtimes": {
                RUNTIME: {
                    "binary": str(self.binary),
                    "binary_version": FAKE_VERSION,
                    "mode": "standalone",
                    "auto": True,
                    "sessions_db": str(self.store_path),
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

    def new_project(self) -> dict:
        """Disposable project with a canonical packet published by `prepare`."""
        root = self.base / "project"
        root.mkdir(parents=True, exist_ok=True)
        build_project(root)
        proc = subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "006-005 U6-4 fixture (test-writer/red)"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env=self.env())
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

    def request_doc(self) -> dict:
        path = (self.project["root"] / ".cdad" / "packets"
                / self.project["packet_id"] / "REQUEST.json")
        return json.loads(path.read_text(encoding="utf-8"))

    # -- record invocations -------------------------------------------------

    def record(self, *, attempt: str, native_result: Path | None = None,
               parent: str | None = PARENT, since: str | None = SINCE
               ) -> subprocess.CompletedProcess:
        args = ["record", "--project-root", str(self.project["root"]),
                "--packet", self.project["packet_id"],
                "--attempt-id", attempt, "--runtime", RUNTIME, "--json"]
        if parent is not None:
            args += ["--parent", parent]
        if since is not None:
            args += ["--since", since]
        if native_result is not None:
            args += ["--native-result", str(native_result)]
        return self.run_entry(*args)

    def native_result_file(self, name: str = "native-result-u6fix4.md") -> Path:
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

    def assert_not_a_rejection(self, proc: subprocess.CompletedProcess,
                               out: dict, label: str) -> None:
        """U6-4: «more than one ⇒ never a rejection», «none ⇒ no rejection»,
        «uninterpretable ⇒ no rejection». `blocked` is the closed vocabulary's
        rejection termination."""
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: la vía nativa RECHAZÓ (rc=%s); U6-4 exige que un "
                "candidato ambiguo/ausente no sea un rechazo:\n%s"
                % (label, proc.returncode, tail(self.output(proc))))
        self.assertNotEqual(
            out.get("termination"), "blocked",
            msg="%s: la vía nativa RECHAZÓ (termination=blocked); U6-4 exige "
                "que un candidato ambiguo/ausente no sea un rechazo: %r"
                % (label, out))

    def records(self) -> dict:
        return dispatch_records(self.project["root"],
                                self.project["execution_id"])

    def record_doc(self, stem: str) -> dict:
        base = (self.project["root"] / ".cdad" / "executions"
                / self.project["execution_id"] / "dispatches")
        return json.loads((base / (stem + ".json")).read_text(encoding="utf-8"))

    def single_record(self, before: dict) -> dict:
        """PD-1: exactly ONE attempt per dispatch."""
        new = {stem: path for stem, path in self.records().items()
               if stem not in set(before) and not stem.startswith(".")}
        self.assertEqual(
            len(new), 1,
            msg="PD-1: el despacho dejó %d registros I8 nuevos (se espera "
                "exactamente uno): %r" % (len(new), sorted(new)))
        return self.record_doc(next(iter(new)))

    def note_text(self, out: dict | None = None,
                  record: dict | None = None) -> str:
        """Only the DIAGNOSTIC the invocation declares (the envelope's
        `diagnosis` and the record's `provenance` values), never the attempt or
        session ids: an id could contain a word the diagnostic must say."""
        parts: list = []
        if out is not None and out.get("diagnosis"):
            parts.append(str(out["diagnosis"]))
        if record is not None:
            provenance = record.get("provenance")
            if isinstance(provenance, dict):
                parts.extend(str(value) for value in provenance.values())
        return "\n".join(parts)

    def staged_payloads(self) -> list:
        inbox = self.project["root"] / ".cdad" / "inbox"
        return [path for path in sorted(inbox.rglob("*"))
                if path.is_file() and path.read_bytes() == NATIVE_PAYLOAD]

    def descriptor_path(self) -> Path:
        return self.project["root"] / ".cdad" / "inbox" / "RESULT.json"

    def receipt_path(self) -> Path:
        return (self.project["root"] / ".cdad" / "runtime" / "results"
                / self.project["execution_id"] / self.project["packet_id"]
                / "receipt.json")

    def assert_provenance_declares_unverified(self, record: dict,
                                              label: str) -> None:
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict,
            msg="%s/PD-6/INV-8: el `provenance` del intento no es un objeto: %r"
                % (label, provenance))
        source = provenance.get("session")
        self.assertIsInstance(
            source, str,
            msg="%s/PD-6: el `provenance` no declara que la identidad no se "
                "pudo verificar: %r" % (label, source))
        self.assertTrue(
            source.strip(),
            msg="%s/PD-6: la procedencia declarada de `session` está vacía"
                % label)


# ------------------------------------------------- PD-5/E1 (U6-4): moment


class TestU64MomentKey(U6Fix4Case):
    """PD-5/E1 (U6-4): the store's `time_created` is an epoch-MILLISECONDS
    INTEGER; after `--since` it matches, before it does not. The project key is
    corroborated by membership, and an ancestor directory is not evaluable
    (U6-3), never a contradiction."""

    def test_u64_verified_child_inside_the_root(self) -> None:
        """PD-5/E1 (U6-4): ONE child under the declared parent, of the packet's
        agent, with `time_created` (epoch ms) after `--since`, in a directory
        inside the authorized root ⇒ the attempt is VERIFIED with the session
        the STORE carries, and the byte-exact native delivery is staged."""
        request = self.request_doc()
        self.assertEqual(
            request.get("agent"), PACKET_AGENT,
            msg="precondición (fixture): el paquete declara el agente del rol "
                "(REQUEST.json.agent=%r)" % request.get("agent"))
        child = "ses-u64-inside-0001"
        self.write_store([self.row(child)])
        before = self.records()

        proc = self.record(attempt="att-u64-a1-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (a) hijo único dentro de la raíz")
        self.assert_not_a_rejection(proc, out, "U6-4 (a)")
        record = self.single_record(before)
        self.assertEqual(
            out.get("attempt"), "att-u64-a1-0001",
            msg="PD-5/E1 (U6-4): el sobre no declara el intento registrado: %r"
                % out.get("attempt"))
        self.assertEqual(
            record.get("session"), child,
            msg="PD-5/E1 (U6-4): con padre, agente, momento (ms posterior a "
                "`--since`) y proyecto por pertenencia coincidiendo, la sesión "
                "OBSERVADA se acredita; se persistió %r"
                % record.get("session"))
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4): la acreditación no escenificó la entrega "
                "byte-exacta del resultado nativo")

    def test_u64_ancestor_directory_is_verified_by_parent_and_moment(
            self) -> None:
        """PD-5/E1 (U6-4) + U6-3: the session directory is an ANCESTOR of the
        authorized root (the container where the coordinator was started) ⇒ the
        project key is NOT evaluable and is NAMED as such; the declared parent
        and the moment (ms after `--since`) — both discriminating keys — VERIFY
        the attempt, whose session is the store's child id."""
        root = self.project["root"]
        self.assertEqual(
            root.parent, self.base,
            msg="precondición (fixture): la raíz no cuelga del contenedor "
                "declarado (%r vs %r)" % (str(root.parent), str(self.base)))
        child = "ses-u64-ancestor-0001"
        self.write_store([self.row(child, directory=str(self.base))])
        before = self.records()

        proc = self.record(attempt="att-u64-a2-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (a) directorio ancestro")
        self.assert_not_a_rejection(proc, out, "U6-4 (a) ancestro")
        record = self.single_record(before)
        self.assertEqual(
            record.get("session"), child,
            msg="PD-5/E1 (U6-4): con el proyecto NO evaluable (ancestro) y "
                "padre + momento coincidentes, la sesión OBSERVADA se "
                "acredita; se persistió %r" % record.get("session"))
        note = self.note_text(out, record)
        self.assertRegex(
            note, PROJECT_NOT_EVALUABLE_RE,
            msg="PD-5/E1 (U6-4): el resultado no nombra el proyecto como NO "
                "EVALUABLE en el caso ancestro (U6-3: no es una "
                "contradicción):\n%s" % tail(note, 40))
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4): el caso ancestro no escenificó la entrega "
                "byte-exacta")

    def test_u64_same_agent_child_before_since_is_not_a_candidate(self) -> None:
        """PD-5/E1 (U6-4): TWO children of the packet's agent under the same
        parent, the first one with an epoch-ms `time_created` BEFORE `--since`
        and the second one after ⇒ the earlier child is not a candidate, so
        there is exactly ONE candidate and the attempt is verified on the AFTER
        child.

        This is the unit discriminator: reading the store's integer as seconds
        would place the BEFORE child in the future (two candidates ⇒ no
        accreditation), and treating it as uninterpretable would lose the
        timing filter (same outcome); only the real millisecond unit selects
        exactly one candidate."""
        earlier = "ses-u64-before-0001"
        later = "ses-u64-after-0001"
        self.write_store([
            self.row(earlier, time_created=BEFORE_MS),
            self.row(later, time_created=AFTER_MS),
        ])
        before = self.records()

        proc = self.record(attempt="att-u64-m1-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (momento ms: antes/después)")
        self.assert_not_a_rejection(proc, out, "U6-4 (antes/después)")
        record = self.single_record(before)
        self.assertEqual(
            record.get("session"), later,
            msg="PD-5/E1 (U6-4): con `time_created` en MILISEGUNDOS, el hijo "
                "anterior a `--since` no es candidato y el posterior sí: se "
                "acredita %r; se persistió %r (unidad en segundos ⇒ dos "
                "candidatos; instante no interpretable ⇒ ninguno)"
                % (later, record.get("session")))
        self.assertNotEqual(
            record.get("session"), earlier,
            msg="PD-5/E1 (U6-4): se acreditó el hijo ANTERIOR a `--since`")
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4): la selección por momento no escenificó la "
                "entrega byte-exacta")


# --------------------------------------- PD-5/E1 (U6-4): candidate selection


class TestU64CandidateSelection(U6Fix4Case):
    """PD-5/E1 (U6-4): candidates are the rows under the declared parent with
    the packet's agent and a moment after `--since`; exactly one is evaluated,
    none means no row, more than one is NAMED ambiguity and never a rejection
    (INV-2)."""

    def test_u64_earlier_child_of_another_role_is_not_a_candidate(self) -> None:
        """PD-5/E1 (U6-4): under the same parent, an EARLIER child of ANOTHER
        role (inserted first) and the packet's child after `--since` ⇒ the
        attempt is verified on the packet's child. Never a rejection: the
        earlier foreign row is not a candidate, it does not contradict."""
        foreign = "ses-u64-foreign-role-0001"
        child = "ses-u64-role-child-0001"
        self.write_store([
            self.row(foreign, agent=OTHER_ROLE_AGENT, time_created=BEFORE_MS),
            self.row(child, agent=PACKET_AGENT, time_created=AFTER_MS),
        ])
        before = self.records()

        proc = self.record(attempt="att-u64-b-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (b) hijo anterior de otro rol")
        self.assert_not_a_rejection(proc, out, "U6-4 (b)")
        record = self.single_record(before)
        self.assertEqual(
            record.get("session"), child,
            msg="PD-5/E1 (U6-4): el hijo de OTRO rol no es candidato (no es "
                "una contradicción de `agent`): se acredita el hijo del "
                "paquete %r; se persistió %r" % (child, record.get("session")))
        self.assertNotEqual(
            record.get("session"), foreign,
            msg="PD-5/E1 (U6-4): se acreditó el hijo de otro rol")
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4): la selección por agente no escenificó la "
                "entrega byte-exacta")

    def test_u64_two_candidates_are_ambiguous_and_never_accredited(self) -> None:
        """PD-5/E1 (U6-4) + PD-6: TWO children of the packet's agent, both
        after `--since` ⇒ NOTHING is accredited (`session: null`), the
        ambiguity is NAMED, and it is NOT a rejection. With a byte-exact native
        result PD-6 applies: the delivery exists with `session: null` and a
        provenance that declares the identity could not be verified."""
        first = "ses-u64-ambiguous-a-0001"
        second = "ses-u64-ambiguous-b-0001"
        self.write_store([
            self.row(first, time_created=AFTER_MS),
            self.row(second, time_created=LATER_MS),
        ])
        before = self.records()

        proc = self.record(attempt="att-u64-c-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (c) dos candidatos")
        self.assert_not_a_rejection(proc, out, "U6-4 (c)")
        record = self.single_record(before)
        self.assertIsNone(
            record.get("session"),
            msg="PD-5/E1 (U6-4)/INV-2: dos hijos del mismo agente posteriores "
                "a `--since` son AMBIGUOS: no se acredita NINGUNA sesión "
                "(nunca una elección arbitraria); se persistió %r"
                % record.get("session"))
        self.assertNotIn(
            record.get("session"), (first, second),
            msg="PD-5/E1 (U6-4)/INV-2: se acreditó una de las dos sesiones "
                "ambiguas (%r)" % record.get("session"))
        note = self.note_text(out, record)
        self.assertRegex(
            note, AMBIGUITY_RE,
            msg="PD-5/E1 (U6-4): el diagnóstico no nombra la AMBIGÜEDAD de los "
                "candidatos:\n%s" % tail(note, 40))
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4)/PD-6: con resultado nativo byte-exacto y "
                "ambigüedad, la entrega se persiste igual (`session: null`)")
        self.assert_provenance_declares_unverified(record, "U6-4 (c)")

    def test_u64_no_candidate_earlier_child_is_not_a_rejection(self) -> None:
        """PD-5/E1 (U6-4), declared GUARD: the only child matches parent and
        agent but its epoch-ms moment is BEFORE `--since` ⇒ there is no
        candidate: nothing is accredited and it is NOT a rejection. Without a
        native result PD-4 decides the consequence: the attempt is registered,
        nothing is staged, no descriptor and no receipt are written.

        Today it answers no session for the wrong reason (the moment is not
        interpretable); it becomes discriminating once the unit is read: with
        seconds it would look like a future candidate."""
        child = "ses-u64-only-before-0001"
        self.write_store([self.row(child, time_created=BEFORE_MS)])
        root = self.project["root"]
        inbox_before = snapshot_under(root / ".cdad" / "inbox")
        before = self.records()

        proc = self.record(attempt="att-u64-d1-0001")
        out = self.envelope(proc, "U6-4 (d) único hijo anterior")
        self.assert_not_a_rejection(proc, out, "U6-4 (d) anterior")
        record = self.single_record(before)
        self.assertIsNone(
            record.get("session"),
            msg="PD-5/E1 (U6-4): el único hijo es anterior a `--since` ⇒ no hay "
                "candidato y no se acredita sesión; se persistió %r"
                % record.get("session"))
        self.assertNotEqual(
            out.get("termination"), "completed",
            msg="PD-5/E1 (U6-4)/PD-4: sin candidato ni texto final la "
                "terminación no puede declarar entrega: %r"
                % out.get("termination"))
        self.assertTrue(
            out.get("diagnosis"),
            msg="PD-5/E1 (U6-4)/PD-4: el sobre no declara el hecho (diagnóstico "
                "vacío)")
        self.assertFalse(
            self.descriptor_path().is_file(),
            msg="PD-5/E1 (U6-4)/PD-4: sin texto final se escribió un descriptor "
                "RESULT.json")
        self.assertEqual(
            snapshot_diff(inbox_before,
                          snapshot_under(root / ".cdad" / "inbox")),
            [],
            msg="PD-5/E1 (U6-4)/PD-4: sin texto final se escenificó algo bajo "
                "`.cdad/inbox`")
        self.assertFalse(
            self.receipt_path().is_file(),
            msg="PD-5/E1 (U6-4)/PD-4: sin texto final hay un recibo")

    def test_u64_no_candidate_other_agent_with_native_result_delivers_under_pd6(
            self) -> None:
        """PD-5/E1 (U6-4) + PD-6: the only child under the parent belongs to
        ANOTHER agent ⇒ it is not a candidate and its agent does NOT contradict
        the packet (no rejection). With a byte-exact native result PD-6
        applies: the delivery is persisted with `session: null` and a declared
        provenance."""
        foreign = "ses-u64-only-other-0001"
        self.write_store([self.row(foreign, agent=OTHER_ROLE_AGENT,
                                   time_created=AFTER_MS)])
        before = self.records()

        proc = self.record(attempt="att-u64-d2-0001",
                           native_result=self.native_result_file())
        out = self.envelope(proc, "U6-4 (d) único hijo de otro agente")
        self.assert_not_a_rejection(proc, out, "U6-4 (d) otro agente")
        record = self.single_record(before)
        self.assertIsNone(
            record.get("session"),
            msg="PD-5/E1 (U6-4): el hijo de otro agente no es candidato: no se "
                "acredita sesión (y no es una contradicción que rechace); se "
                "persistió %r" % record.get("session"))
        self.assert_provenance_declares_unverified(record, "U6-4 (d) otro agente")
        self.assertTrue(
            self.staged_payloads(),
            msg="PD-5/E1 (U6-4)/PD-6: con resultado nativo byte-exacto la "
                "entrega se persiste (`session: null`)")


# ---------------------------------------------- PD-5/E1 (U6-4): diagnostics


class TestU64Diagnostics(U6Fix4Case):
    """PD-5/E1 (U6-4)/INV-4: a value that cannot be read as an instant is NAMED
    as not interpretable (never the ancestor phrase), and a non-verified note
    names the keys that DID match."""

    def test_u64_uninterpretable_instant_is_named_as_such(self) -> None:
        """PD-5/E1 (U6-4)/O-6/INV-4: the store's `time_created` cannot be read
        as an instant (a non-numeric value in the INTEGER column) ⇒ nothing is
        accredited, no rejection, and the diagnosis NAMES the moment as NOT
        INTERPRETABLE — the ancestor-directory phrase of U6-3 does not satisfy
        this."""
        child = "ses-u64-unreadable-0001"
        self.write_store([self.row(child, time_created="not-an-instant")])
        before = self.records()

        proc = self.record(attempt="att-u64-e-0001")
        out = self.envelope(proc, "U6-4 (e) instante no interpretable")
        self.assert_not_a_rejection(proc, out, "U6-4 (e)")
        record = self.single_record(before)
        self.assertIsNone(
            record.get("session"),
            msg="PD-5/E1 (U6-4): un `time_created` que no se puede leer como "
                "instante no acredita sesión; se persistió %r"
                % record.get("session"))
        note = self.note_text(out, record)
        self.assertRegex(
            note, MOMENT_UNINTERPRETABLE_RE,
            msg="PD-5/E1 (U6-4)/INV-4: el diagnóstico NO nombra el instante del "
                "store como NO INTERPRETABLE (no vale la frase del caso "
                "ancestro):\n%s" % tail(note, 40))

    def test_u64_unverified_note_names_the_keys_that_matched(self) -> None:
        """PD-5/E1 (U6-4): in a NON-verified result, the note also names the
        keys that DID match. Here parent and agent match and the moment is
        before `--since`, so `parent` (a discriminating key) matched."""
        child = "ses-u64-note-parent-0001"
        self.write_store([self.row(child, time_created=BEFORE_MS)])
        before = self.records()

        proc = self.record(attempt="att-u64-f-0001")
        out = self.envelope(proc, "U6-4 (f) nota de llaves coincidentes")
        self.assert_not_a_rejection(proc, out, "U6-4 (f)")
        record = self.single_record(before)
        self.assertIsNone(
            record.get("session"),
            msg="PD-5/E1 (U6-4): sin candidato (momento anterior a `--since`) "
                "no se acredita sesión; se persistió %r" % record.get("session"))
        note = self.note_text(out, record)
        self.assertRegex(
            note, MATCHED_KEY_RE,
            msg="PD-5/E1 (U6-4): la nota no verificada no nombra las llaves que "
                "SÍ coincidieron (p. ej. `parent`):\n%s"
                % tail(note, 40))


if __name__ == "__main__":
    unittest.main(verbosity=2)
