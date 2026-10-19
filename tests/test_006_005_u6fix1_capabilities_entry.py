#!/usr/bin/env python3
"""006-005 U6-1 RED — `capabilities` invoked THROUGH THE ENTRY must observe
the runtime section it declares in `runtimes.json`.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved, sha256
3a824be3…): PD-10 (`capabilities` answers the five keys of §2.2; `version` is
the OBSERVED one or `unknown`, never supposed; a store with a discriminating
key accredits the correlation and names the columns), PD-25/§2.6.1 (the
declared verification of the migration step is `capabilities --runtime X`,
which observes the configured binary and version, or `unknown` with `reason`)
and PD-9/§2.6 (a missing section fails closed with the diagnostic that names
`runtimes.json`).

Observed defect (U6-1, `docs/epics/epic-006-opencode-concurrency/execution.md`
§«006-005 U6: recorrido real»): after `migrate`, with the `opencode` section
present in `runtimes.json` (`binary`, `binary_version`, `sessions_db`, …),
`cdad_dispatch.py capabilities --runtime opencode` answers `version: unknown`
and a `reason` saying «the execution configuration declares no durable session
store (`sessions_db`) … no destination binary (`binary`)». The U1b/U2 tests did
not see it because their fixture hands the configuration to the MODULE
directly; the ENTRY is what fails to deliver it. The RED therefore observes the
entry, never the module alone.

Oracle discipline (black box). The entry `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked AS A PROCESS against a staged copy of the skill
tree with a fixture runtime module next to it, and a temporary
`XDG_CONFIG_HOME`/`HOME`; nothing of the implementation is read or imported.
The user's real config is neither read nor written, and no host value is used:
the binary, the version and the store are per-test temporaries.

FIXTURE INTERFACE, DECLARED (the surface this RED pins):

* The runtime id is `u6fix`; its module is `cdad_delegate_u6fix.py` next to the
  entry (the product's own module convention).
* The fixture module's `--capabilities` answers §2.2's five keys and OBSERVES
  the configuration it receives on the channel the external dispatch already
  uses (`--exec-config FILE`, an equivalent internal carrier, or
  `CDAD_EXEC_CONFIG`). With the configuration it runs the configured `binary`
  `--version` (the version is OBSERVED, never supposed) and reads
  `PRAGMA table_info(session_v2)` from the configured `sessions_db`; it names
  those columns and declares `session_correlation` true when a discriminating
  key (§2.3: `parent_id`, `time_created` or `directory`) is present.
* WITHOUT the configuration the fixture reproduces the U6-1 answer: `version:
  unknown` and the reason that names the absent `sessions_db` and `binary`.
  That is what the entry relays today; the test fails on its assertion about
  the version/columns, never on an import or a missing verb.
* The disposable store carries the schema of the installed version (V-7 probe
  of `execution.md`): `id, parent_id, directory, agent, model, time_created,
  time_idle, idle_outcome`.

WHY THE U1b FIXTURE IS NOT REUSED: its `--capabilities` is a CONSTANT document
(it neither reads a configuration nor observes a binary/store), which is
exactly why U1b could not see U6-1. Reusing it would make the defect
invisible again; the declared configuration-dependent surface above is the
fixture this RED needs.

MAPPING (one test per numbered postcondition; each docstring names its PD):

  PD-10  test_pd10_entry_capabilities_observes_the_declared_runtime_section
  PD-25  test_pd25_migrated_section_is_verified_by_entry_capabilities
  PD-9   test_pd9_capabilities_without_section_names_the_single_source

EXPECTED RED TODAY (declared, not accidental): the entry's `capabilities`
invokes the runtime module without deriving the `runtimes.json` section, so the
fixture answers `version: unknown` and the missing-configuration reason. The
PD-10 and PD-25 tests fail on their FIRST behavioral assertion (the observed
version / the store columns); the PD-9 negative is a guard already green from
U1a and is reported as such.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

RUNTIME = "u6fix"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
FAKE_VERSION = "u6fix-runtime 7.7.7"

# V-7 probe (`execution.md` §«006-005: sonda V-7 antes del RED de U2»): the
# installed version's `session_v2` exposes parent_id, directory, time_created
# and agent, besides id, model, time_idle and idle_outcome.
INSTALLED_COLUMNS = [
    "id TEXT PRIMARY KEY",
    "parent_id TEXT",
    "directory TEXT",
    "agent TEXT",
    "model TEXT",
    "time_created REAL",
    "time_idle REAL",
    "idle_outcome TEXT",
]
DISCRIMINATING_COLUMNS = ("parent_id", "time_created", "directory")

# §2.2: the five keys of the capability document.
CAPABILITY_KEYS = (
    "native_observation",
    "external_transport",
    "session_correlation",
    "version",
    "reason",
)

# The U6-1 diagnosis the fix must remove from the answer of a configured
# runtime: it claims the configuration has no store and no binary.
MISSING_CONFIGURATION_RE = re.compile(
    r"(?i)declares no durable session store|no durable session store"
    r"|no destination binary"
)

# ------------------------------------------------------- fixture: fake binary

FAKE_BINARY_SOURCE = '''#!/usr/bin/env python3
"""Fake runtime binary — fixture of
tests/test_006_005_u6fix1_capabilities_entry.py. NOT the product: it only
declares a version, the datum the capability document must report as OBSERVED
(never supposed)."""
import sys

VERSION = __VERSION__

if "--version" in sys.argv[1:]:
    sys.stdout.write(VERSION + "\\n")
    sys.stdout.flush()
    sys.exit(0)

sys.stderr.write("u6fix fake binary: only --version is declared\\n")
sys.exit(2)
'''

# ---------------------------------------------- fixture: runtime module source

MODULE_SOURCE = r'''#!/usr/bin/env python3
"""FIXTURE runtime module of
tests/test_006_005_u6fix1_capabilities_entry.py (NOT product).

Declared behavior: `--capabilities` answers §2.2's five keys by OBSERVING the
configuration it receives on the channel the external dispatch already uses
(`--exec-config FILE`, another internal carrier, or `CDAD_EXEC_CONFIG`):

  * `version` is the output of `<binary> --version` (observed, never supposed);
  * `session_correlation` declares, besides whether the threshold is reached,
    the columns of `session_v2` observed in `<sessions_db>` (§2.2/§2.3); it is
    `false` with a `reason` when no discriminating key (§2.3: parent_id /
    time_created / directory) is present.

Without the configuration it answers `version: unknown` and the U6-1 reason
that names the absent `sessions_db` and `binary` (the defect this RED
observes through the entry).
"""
import json
import os
import sqlite3
import subprocess
import sys

DISCRIMINATING = ("parent_id", "time_created", "directory")


def _option(name):
    argv = sys.argv[1:]
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _configuration():
    candidates = []
    for name in ("--exec-config", "--config", "--runtime-config"):
        value = _option(name)
        if value:
            candidates.append(value)
    environment = os.environ.get("CDAD_EXEC_CONFIG")
    if environment:
        candidates.append(environment)
    candidates.extend(sys.argv[1:])
    for candidate in candidates:
        if not candidate or not os.path.isfile(candidate):
            continue
        try:
            with open(candidate, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and ("sessions_db" in data or "binary" in data):
            return data
    return {}


def _observed_version(binary):
    if not binary:
        return "unknown", None
    try:
        completed = subprocess.run(
            [binary, "--version"], capture_output=True, text=True, timeout=60)
    except OSError:
        return "unknown", ("the configured binary (`binary`) could not be "
                           "executed")
    observed = (completed.stdout or "").strip()
    if completed.returncode != 0 or not observed:
        return "unknown", ("the configured binary (`binary`) reported no "
                           "version")
    return observed, None


def _columns(store):
    if not store or not os.path.isfile(store):
        return []
    connection = sqlite3.connect("file:%s?mode=ro" % store, uri=True)
    try:
        return [row[1] for row in
                connection.execute("PRAGMA table_info(session_v2)")]
    finally:
        connection.close()


def _capabilities():
    configuration = _configuration()
    binary = configuration.get("binary")
    store = configuration.get("sessions_db")
    version, version_reason = _observed_version(binary)
    columns = _columns(store)
    discriminating = [name for name in DISCRIMINATING if name in columns]

    reason_parts = []
    if not binary and not store:
        reason_parts.append("the execution configuration declares no durable "
                            "session store (`sessions_db`) and no destination "
                            "binary (`binary`)")
    else:
        if not binary:
            reason_parts.append("no destination binary (`binary`)")
        elif version_reason:
            reason_parts.append(version_reason)
        if not store:
            reason_parts.append("no durable session store (`sessions_db`)")
        elif not columns:
            reason_parts.append("the store (`sessions_db`) exposes no "
                                "`session_v2` schema")
        if columns and not discriminating:
            reason_parts.append("no discriminating key (parent_id / "
                                "time_created / directory) in `session_v2`")

    return {
        "native_observation": bool(binary) and bool(columns),
        "external_transport": True,
        "session_correlation": ({
            "accredited": True,
            "columns": columns,
            "threshold": True,
            "discriminating": discriminating,
        } if discriminating else False),
        "version": version,
        "reason": "; ".join(reason_parts) if reason_parts else None,
    }


if "--capabilities" in sys.argv[1:]:
    sys.stdout.write(json.dumps(_capabilities(), sort_keys=True) + "\n")
    sys.stdout.flush()
    sys.exit(0)

sys.stderr.write("u6fix fixture module: only --capabilities is declared\n")
sys.exit(2)
'''


# -------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join((text or "").strip().splitlines()[-lines:])


# -------------------------------------------------------------------- fixture


class U6Fix1EntryCase(unittest.TestCase):
    """Disposable config/HOME + a staged skill tree whose entry has the fixture
    runtime module next to it. The entry runs AS A PROCESS; no product module is
    read or imported."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u6fix1-")
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
        self.module = self.scripts / MODULE_NAME
        self.module.write_text(MODULE_SOURCE, encoding="utf-8")
        self.entry = self.scripts / "cdad_dispatch.py"
        self.assertTrue(
            self.entry.is_file(),
            msg="precondición (fixture): no existe la entrada en el producto "
                "(se espera %s por U1a del plan)"
                % ENTRY_PRODUCT.relative_to(REPO_ROOT))

        self.binary = self.write_fake_binary()
        self.store = self.write_store()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- harness ------------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("CDAD_EXEC_CONFIG", None)
        return env

    def run_entry(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.entry), *args],
            cwd=str(self.base), env=self.env(), capture_output=True,
            text=True, check=False, timeout=300)

    @staticmethod
    def output(proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout or "") + (proc.stderr or "")

    # -- fixture data -------------------------------------------------------

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "u6fix-runtime"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            FAKE_BINARY_SOURCE.replace("__VERSION__", json.dumps(FAKE_VERSION)),
            encoding="utf-8")
        path.chmod(0o755)
        return path

    def write_store(self) -> Path:
        """Disposable SQLite store with the INSTALLED version's schema (V-7)."""
        path = self.fixture_dir / "sessions.db"
        connection = sqlite3.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE session_v2 (%s)"
                % ", ".join(INSTALLED_COLUMNS))
            connection.commit()
        finally:
            connection.close()
        return path

    def runtime_section(self) -> dict:
        return {
            "binary": str(self.binary),
            "binary_version": FAKE_VERSION,
            "mode": "standalone",
            "auto": True,
            "sessions_db": str(self.store),
            "wait": {"timeout_seconds": 30},
        }

    def runtimes_path(self) -> Path:
        return self.config_home / "cdad" / "runtimes.json"

    def write_runtimes(self, section: dict | None) -> Path:
        document = {"version": 1, "runtimes": {}}
        if section is not None:
            document["runtimes"][RUNTIME] = section
        path = self.runtimes_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def legacy_exec_config(self) -> Path:
        """A retired exec-config (§2.6): the section keys plus `runtime`,
        `model` and the credential route (the latter two never migrate)."""
        document = {
            "runtime": RUNTIME,
            "model": "fixture/model-u6fix1",
            "credential_env_file": "/fixture/credentials/opencode-server.env",
        }
        document.update(self.runtime_section())
        path = self.fixture_dir / "legacy-exec-config.json"
        path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    # -- the entry's capability surface ------------------------------------

    def capabilities(self) -> subprocess.CompletedProcess:
        return self.run_entry("capabilities", "--runtime", RUNTIME, "--json")

    def capabilities_document(self, proc: subprocess.CompletedProcess,
                              label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: `capabilities --runtime %s` no completó (rc=%s):\n%s"
                % (label, RUNTIME, proc.returncode,
                   tail(self.output(proc), 40)))
        try:
            document = json.loads(proc.stdout or "null")
        except json.JSONDecodeError:
            self.fail(msg="%s: stdout no es el documento JSON declarado "
                          "(§2.2):\n%s" % (label, tail(proc.stdout, 40)))
        self.assertIsInstance(
            document, dict,
            msg="%s: el documento de capacidades no es un objeto: %r"
                % (label, document))
        for key in CAPABILITY_KEYS:
            self.assertIn(
                key, document,
                msg="%s: el documento de capacidades no responde la clave "
                    "declarada %r (§2.2): %r" % (label, key, document))
        return document

    def assert_observes_the_section(self, document: dict, label: str) -> None:
        """PD-10/PD-25 (U6-1): the entry delivers the section to the module, so
        the document reports the OBSERVED binary version and the store's
        columns, and carries no missing-configuration reason."""
        self.assertEqual(
            document["version"], FAKE_VERSION,
            msg="%s: `version` no es la versión OBSERVADA del binario "
                "configurado (se espera %r; `unknown` es el defecto U6-1): %r"
                % (label, FAKE_VERSION, document.get("version")))
        self.assertTrue(
            document["session_correlation"],
            msg="%s: la versión observada expone una llave discriminante "
                "(parent_id / time_created / directory) y alcanza el umbral "
                "de §2.3: `session_correlation` debe ser true: %r"
                % (label, document))
        blob = json.dumps(document, sort_keys=True)
        self.assertRegex(
            blob, "parent_id|time_created|directory",
            msg="%s: el documento no declara las columnas del store observado "
                "(V-7: parent_id / directory / time_created): %r"
                % (label, document))
        self.assertNotRegex(
            blob, MISSING_CONFIGURATION_RE,
            msg="%s: el documento conserva el diagnóstico de configuración "
                "ausente con la sección presente (U6-1): %r"
                % (label, document))


# --------------------------------------------------------------------- PD-10


class TestPd10EntryCapabilities(U6Fix1EntryCase):
    """PD-10/§2.2/§2.3 (U6-1): `capabilities` through the ENTRY observes the
    runtime section of `runtimes.json` — the entry must derive it and deliver
    it to the runtime module, exactly as `dispatch` does."""

    def test_pd10_entry_capabilities_observes_the_declared_runtime_section(
            self) -> None:
        """PD-10/PD-25 (U6-1): with a section declaring a fake binary (with a
        version) and a disposable store with the installed-version schema, the
        answer declares the OBSERVED version and the store's columns, with no
        missing-configuration reason."""
        self.write_runtimes(self.runtime_section())
        proc = self.capabilities()
        document = self.capabilities_document(proc, "PD-10 (U6-1)")
        self.assert_observes_the_section(document, "PD-10 (U6-1)")
        self.assertTrue(
            document["native_observation"],
            msg="PD-10 (U6-1): con binario y store observables el documento "
                "debe acreditar `native_observation`: %r" % document)


# --------------------------------------------------------------------- PD-25


class TestPd25MigrationVerification(U6Fix1EntryCase):
    """PD-25/§2.6.1 (U6-1): the declared verification of the migration is
    `capabilities --runtime X`; the E5 walk (migrate → capabilities) must see
    what the migration wrote."""

    def test_pd25_migrated_section_is_verified_by_entry_capabilities(
            self) -> None:
        """PD-25/PD-10 (U6-1): `migrate` from a fixture exec-config writes the
        section; the subsequent `capabilities` through the entry verifies it —
        observed binary version and store columns, no missing-configuration
        reason."""
        legacy = self.legacy_exec_config()
        migrated = self.run_entry(
            "migrate", "--runtime", RUNTIME,
            "--legacy-exec-config", str(legacy), "--json")
        self.assertEqual(
            migrated.returncode, 0,
            msg="PD-25/§2.6.1: la migración desde un exec-config de fixture "
                "no escribió la sección (rc=%s):\n%s"
                % (migrated.returncode, tail(self.output(migrated), 40)))
        path = self.runtimes_path()
        self.assertTrue(
            path.is_file(),
            msg="PD-25/§2.6.1: la migración no creó `runtimes.json`")
        document = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(
            RUNTIME, document.get("runtimes", {}),
            msg="PD-25/§2.6.1: la sección migrada del runtime no existe en "
                "`runtimes.json`: %r" % document)

        capabilities = self.capabilities()
        verification = self.capabilities_document(
            capabilities, "PD-25 (U6-1, sección migrada)")
        self.assert_observes_the_section(
            verification, "PD-25 (U6-1, sección migrada)")


# ---------------------------------------------------------------------- PD-9


class TestPd9MissingSection(U6Fix1EntryCase):
    """PD-9/§2.6 (guard, already green from U1a): without a section,
    `capabilities` fails closed with the single-source diagnostic."""

    def test_pd9_capabilities_without_section_names_the_single_source(
            self) -> None:
        """PD-9/§2.6: no section ⇒ rc≠0 and the diagnostic names
        `runtimes.json`, the runtime section and the key-by-key correspondence
        — the module is never asked to guess a configuration."""
        self.write_runtimes(None)
        proc = self.capabilities()
        text = self.output(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="PD-9/§2.6: sin sección del runtime, `capabilities` debe "
                "fallar cerrado (rc=%s):\n%s"
                % (proc.returncode, tail(text, 40)))
        self.assertIn(
            "runtimes.json", text,
            msg="PD-9/§2.6: el diagnóstico no nombra `runtimes.json`:\n%s"
                % tail(text, 40))
        self.assertIn(
            RUNTIME, text,
            msg="PD-9/§2.6: el diagnóstico no nombra la sección del runtime "
                "(%r):\n%s" % (RUNTIME, tail(text, 40)))
        for key in ("binary", "sessions_db"):
            self.assertIn(
                key, text,
                msg="PD-9/§2.6: el diagnóstico no trae la correspondencia "
                    "clave por clave (falta %r):\n%s"
                    % (key, tail(text, 40)))
        self.assertFalse(
            self.runtimes_path().read_text(encoding="utf-8").count(RUNTIME),
            msg="PD-9/INV-7: la negativa por sección ausente escribió la "
                "sección del runtime en `runtimes.json`")


if __name__ == "__main__":
    unittest.main()
