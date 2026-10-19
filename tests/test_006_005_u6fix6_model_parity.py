#!/usr/bin/env python3
"""006-005 U6-6 RED — `model_reported` parity between the two dispatch paths.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved, sha256
3a824be3…): §2.2 (the module's bounded `--observe`), §2.3 (native correlation:
parent + agent + moment + project-by-membership with the O-3 discrimination
threshold), §2.4 (`model_reported` comes from the observation of the module in
both paths), PD-5 and D-ADP-2 (the I8 record reports the store's observation).
Source of the finding: `docs/epics/epic-006-opencode-concurrency/execution.md`,
finding U6-6.

HECHO OBSERVADO (OpenCode v2.0.27): `session_v2.model` is TEXT carrying a JSON
document such as `{"id":"<model>","providerID":"<provider>","variant":
"default"}`. The EXTERNAL path's I8 record carries
`model_reported = "<provider>/<model>"` — the same normalized form the existing
D-ADP-2 tests pin: `tests/test_005_009_t2_opencode_adapter.py` (:346-357,
:803) and `tests/test_005_010_reviewfix.py` (R2, :503-536, object →
`providerID/id`, and :549-571, plain text preserved). The NATIVE path
(`cdad_dispatch.py record`, verified) carries the RAW JSON today.

This RED pins the parity: a verified native `record` (one child under the
declared parent, of the packet's agent, AFTER `--since`, in a directory inside
the authorized root — the §2.3 keys that reach the O-3 discrimination
threshold) must report `model_reported` in the SAME form as the external path,
never the raw store JSON.

Non-JSON model values are not invented: the external path already fixes the
declared rule with a test (plain text is preserved — `test_005_010_reviewfix.py
::TestR2ModelReportedFromDurableRow::test_r2_plain_text_row_model_is_preserved`),
so the native path is pinned to the same observable rule and to «never a
fabricated value».

Oracle discipline (black box). The entry `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked AS A PROCESS from a staged copy of the skill tree,
so the REAL runtime module `skills/cdad-cycle/scripts/cdad_delegate_opencode.py`
is the one resolved by the `opencode` section of `runtimes.json` under a
temporary `XDG_CONFIG_HOME`/`HOME`. The store is a disposable SQLite database
with the installed version's REAL shape: `time_created INTEGER NOT NULL` in
epoch MILLISECONDS and `model TEXT` carrying the JSON document above. Nothing
of the implementation is read or imported: the observed surface is the exit
code, the declared envelope (stdout JSON) and the I8 record the entry writes.
The user's real config, store and binary are neither read nor written; every
fixture is a per-test temporary.

MAPPING (one test per contracted behavior; every docstring names the
postcondition):

  PD-5/D-ADP-2 (U6-6) — model_reported parity
    test_u66_json_model_is_reported_as_provider_over_model
  PD-5/D-ADP-2 (U6-6) — no invented value
    test_u66_non_json_model_is_not_fabricated

EXPECTED RED TODAY (declared, never accidental): the JSON case fails with an
AssertionError — the verified native record carries the raw JSON document
instead of `<provider>/<model>`. The non-JSON case is a declared GUARD: today
it already reports the observed plain text (the raw copy happens to match the
declared rule) and it must stay green after the fix; it becomes discriminating
against any «parse and invent» implementation that would rewrite or fabricate
a value for a row that is not the declared JSON shape.

A-1 (declared: no existing test is reformulated in this RED). Verified: no
test of the suite pins the RAW JSON as PRODUCT behavior of the native path.
`tests/test_006_005_u1b_dispatch_entry.py` uses a fixture MODULE whose
observation is `model_reported: null` (the entry relays it; :387-400) and
`tests/test_006_005_u6fix4_native_selection.py` never asserts
`model_reported`. The external-path D-ADP-2 tests above fix the rule this RED
extends to the native path; they stay untouched.
"""

from __future__ import annotations

import datetime as dt
import json
import os
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

ENVELOPE_KEYS = OUTPUT_KEYS

PACKET_AGENT = "cdad-test-writer"
PARENT = "ses-parent-u6fix6-0001"

# V-7 extended probe (execution.md §«006-005: sonda V-7»): the INSTALLED
# version's `session_v2` and its real types/units. `time_created` is an
# INTEGER in epoch MILLISECONDS; `model` is TEXT.
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

# The real shape observed on OpenCode v2.0.27: `session_v2.model` is a JSON
# DOCUMENT, not a "provider/model" string. `variant` is part of the observed
# document (the external normalization only requires `id` and `providerID`).
MODEL_ID = "u66-fixture-model-id"
MODEL_PROVIDER = "u66-fixture-provider"
MODEL_JSON = json.dumps(
    {"id": MODEL_ID, "providerID": MODEL_PROVIDER, "variant": "default"})
# The SAME form the external path's D-ADP-2 tests pin (object {id, providerID}
# → 'providerID/id'): test_005_010_reviewfix.py:503-536 and
# test_005_009_t2_opencode_adapter.py:346-357.
MODEL_NORMALIZED = "%s/%s" % (MODEL_PROVIDER, MODEL_ID)

# A row model that is NOT the declared JSON shape: the external path preserves
# the observed value (test_005_010_reviewfix.py:549-571). Never fabricated.
MODEL_PLAIN = "u66-fixture-plain-model"

# An instant the fixture can always express as ISO UTC and as epoch ms.
MOMENT = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) - dt.timedelta(
    minutes=10)
SINCE = MOMENT.strftime("%Y-%m-%dT%H:%M:%SZ")

AFTER_MS = int((MOMENT + dt.timedelta(seconds=60)).timestamp() * 1000)

# ------------------------------------------------------- fixture: fake binary

FAKE_BINARY_SOURCE = '''#!/usr/bin/env python3
"""Fake runtime binary — fixture of
tests/test_006_005_u6fix6_model_parity.py. NOT the product: it only reports the
version the capability document must observe as OBSERVED, never supposed."""
import sys

if "--version" in sys.argv[1:]:
    sys.stdout.write(__VERSION__ + "\\n")
    sys.stdout.flush()
    sys.exit(0)

sys.stderr.write("u6fix6 fake binary: only --version is declared\\n")
sys.exit(2)
'''


def tail(text: str, lines: int = 25) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


class U6Fix6Case(unittest.TestCase):
    """Disposable project + staged skill tree with the REAL `opencode` module,
    a redirected `XDG_CONFIG_HOME`/`HOME`, a fake binary and a disposable store
    with the installed version's REAL shape (epoch milliseconds, JSON model)."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u6fix6-")
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
                "que reemplace la observación (U6-6)" % MODULE_NAME)

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

    def run_entry(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.entry), *args],
            cwd=str(self.project["root"]), env=self.env(),
            capture_output=True, text=True, check=False, timeout=300)

    @staticmethod
    def output(proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout or "") + (proc.stderr or "")

    # -- fixture data -------------------------------------------------------

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "opencode-u6fix6"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            FAKE_BINARY_SOURCE.replace("__VERSION__", json.dumps(FAKE_VERSION)),
            encoding="utf-8")
        path.chmod(0o755)
        return path

    def write_store(self, rows: list) -> Path:
        """Disposable store with the INSTALLED version's real schema (V-7
        extended): `time_created INTEGER NOT NULL` in epoch MILLISECONDS and
        `model TEXT` carrying the observed JSON document."""
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

    def row(self, session: str, *, model: str) -> dict:
        """One `session_v2` row with the real shape: the packet's agent, under
        the declared parent, after `--since`, inside the authorized root."""
        return {
            "id": session,
            "parent_id": PARENT,
            "agent": PACKET_AGENT,
            "model": model,
            "time_created": AFTER_MS,
            "time_idle": None,
            "idle_outcome": "succeeded",
            "directory": str(self.project["root"] / "nested"),
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
             "--objective", "006-005 U6-6 fixture (test-writer/red)"],
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

    # -- record invocation --------------------------------------------------

    def record(self, *, attempt: str) -> subprocess.CompletedProcess:
        return self.run_entry(
            "record", "--project-root", str(self.project["root"]),
            "--packet", self.project["packet_id"],
            "--attempt-id", attempt, "--runtime", RUNTIME,
            "--parent", PARENT, "--since", SINCE, "--json")

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

    def verified_native_record(self, *, child: str, model: str,
                               attempt: str, label: str) -> dict:
        """Run a VERIFIED native `record` (the §2.3 keys reach the O-3
        threshold: parent + moment + project-by-membership) and return its
        single I8 record."""
        self.write_store([self.row(child, model=model)])
        before = self.records()
        proc = self.record(attempt=attempt)
        out = self.envelope(proc, label)
        record = self.single_record(before)
        # Precondition of the observation: the native path is VERIFIED, so the
        # row it reports IS the one the store carries (PD-5 §2.3).
        self.assertEqual(
            record.get("session"), child,
            msg="%s: precondición (PD-5 §2.3): la vía nativa no acreditó la "
                "sesión del store (%r != %r); el caso U6-6 exige un `record` "
                "VERIFICADO" % (label, record.get("session"), child))
        self.assertEqual(
            out.get("termination") != "blocked", True,
            msg="%s: la vía nativa rechazó un candidato legítimo: %r"
                % (label, out))
        return record


# --------------------------------------- PD-5/D-ADP-2 (U6-6): parity


class TestU66ModelReportedParity(U6Fix6Case):
    """PD-5/D-ADP-2 (U6-6): a verified native `record` reports
    `model_reported` in the SAME form as the external path — never the raw
    store JSON — and never fabricates a value for a row that is not the
    declared JSON shape."""

    def test_u66_json_model_is_reported_as_provider_over_model(self) -> None:
        """PD-5/D-ADP-2 (U6-6): the store's `session_v2.model` is the observed
        JSON document `{"id","providerID","variant"}`; the verified native
        record's `model_reported` is `<provider>/<model>` — the same normalized
        form the external path's D-ADP-2 tests pin — and NOT the raw JSON."""
        record = self.verified_native_record(
            child="ses-u66-json-0001", model=MODEL_JSON,
            attempt="att-u66-json-0001", label="U6-6 modelo JSON")

        self.assertEqual(
            record.get("model_reported"), MODEL_NORMALIZED,
            msg="el registro I8 de la vía nativa no reporta `model_reported` "
                "en la MISMA forma que la vía externa (D-ADP-2/U6-6): %r != %r"
                % (record.get("model_reported"), MODEL_NORMALIZED))
        self.assertNotEqual(
            record.get("model_reported"), MODEL_JSON,
            msg="el registro I8 de la vía nativa guardó el DOCUMENTO JSON "
                "crudo de `session_v2.model` (U6-6/§2.4: la observación se "
                "reporta como '<provider>/<model>'): %r"
                % (record.get("model_reported"),))

    def test_u66_non_json_model_is_not_fabricated(self) -> None:
        """PD-5/D-ADP-2 (U6-6), GUARD declarado: a row `model` that is NOT the
        declared JSON shape is not invented. The external path already fixes
        the rule — plain text is preserved verbatim (PD-6/R2) — so the native
        record reports the OBSERVED value, never a fabricated one."""
        record = self.verified_native_record(
            child="ses-u66-plain-0001", model=MODEL_PLAIN,
            attempt="att-u66-plain-0001", label="U6-6 modelo no-JSON")

        self.assertEqual(
            record.get("model_reported"), MODEL_PLAIN,
            msg="el registro I8 de la vía nativa no declara el valor "
                "OBSERVADO de `session_v2.model` para una fila que no es el "
                "JSON declarado (U6-6: nunca un valor fabricado): %r != %r"
                % (record.get("model_reported"), MODEL_PLAIN))
        self.assertNotIn(
            MODEL_PROVIDER, str(record.get("model_reported")),
            msg="el registro I8 fabricó un `model_reported` con datos que la "
                "fila no declara (U6-6): %r"
                % (record.get("model_reported"),))


if __name__ == "__main__":
    unittest.main(verbosity=2)
