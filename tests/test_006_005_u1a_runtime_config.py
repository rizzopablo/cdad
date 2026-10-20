#!/usr/bin/env python3
"""RED tests for 006-005 U1a — execution config per runtime, explicit runtime
resolution, the retired `--exec-config` as a usage error, the bounded migration
step and the installer template.

Contract: `docs/specs/006-005-native-path-parity/spec.md` (approved 2026-10-18,
sha256 3a824be3…), the postconditions PD-8, PD-9 and PD-25, the §2.1 surface,
§2.6 (single source + template), §2.6.1 (bounded migration), D-10/D-11,
INV-7/INV-12, and the approval errata O-7 (the `--exec-config`-on-`migrate` case
belongs to THIS RED). Plan: the U1a sheet (`plan.md` §3) and its `plan-tasks`
block (focal `tests/test_006_005_u1a_runtime_config.py`; regressions listed in
that sheet).

Oracle discipline (black-box). The NEW CLI `skills/cdad-cycle/scripts/
cdad_dispatch.py` is invoked as a SUBPROCESS, never imported and never read
(no implementation file is looked at by this session). Every invocation runs
against a disposable project and a temporary `XDG_CONFIG_HOME`/`HOME` inside
the per-test tempdir — the user's real config is never read nor written. For
the installer, a PRODUCT COPY has its staging regenerated in the copy and the
install goes to a redirected `CDAD_INSTALL_ROOT` (never HOME, never the repo).
Only published effects are observed: exit code, stdout/stderr, the config file
and the ownership manifest.

Mapping (one test per numbered postcondition; a test names the PD in its
docstring):

PD-8 — runtime resolution is explicit and unique:
- test_pd8_missing_runtime_names_the_flag_on_the_default_verb
- test_pd8_missing_runtime_names_the_flag_on_an_explicit_verb
- test_pd8_runtime_without_a_module_is_rejected_naming_the_value
- test_pd8_valid_runtime_proceeds_to_the_single_source_check
- test_pd8_flat_v1_context_runtime_is_never_read

PD-9 — one config source (`runtimes.json` section), no `--exec-config`:
- test_pd9_missing_section_diagnostic_names_file_section_and_correspondence
- test_pd9_section_with_model_is_rejected_naming_delegation_json
- test_pd9_derived_section_is_inspected_key_by_key
- test_pd9_exec_config_token_is_rejected_before_any_effect_default_verb
- test_pd9_exec_config_token_is_rejected_before_any_effect_on_migrate_o7
- test_pd9_help_never_declares_the_retired_option
- test_pd9_legacy_document_is_not_probed_outside_the_migration_step

PD-25 — bounded migration step:
- test_pd25_migrate_without_section_writes_the_section_key_by_key
- test_pd25_migrate_with_existing_section_refuses_and_keeps_bytes
- test_pd25_migrate_dry_run_does_not_write
- test_pd25_migrate_missing_legacy_file_fails_naming_the_path

PD-9 / §2.6 — installer template (same user-data discipline as
`delegation.json`, INV-7):
- test_pd9_installer_creates_the_runtimes_template_when_missing
- test_pd9_installer_does_not_register_the_template_in_the_manifest
- test_pd9_reinstall_does_not_overwrite_the_user_runtimes_section

Declared dependency (not a failing test here): the post-migration verification
is `capabilities --runtime X` (PD-10) and the transient module config handed to
the runtime by `dispatch` — both are U1b/U2 surface. The derived document
inspected in U1a is the section the migration writes (the same key-by-key
document §2.6 enumerates); the dispatch-time transient file is not observable
before U1b.

Declared limit of the "no legacy read outside migration" oracle: whether a
process opens a file is not observable black-box. The oracle pins the
interface instead: the retired token is rejected everywhere, `--help` does not
declare it, a legacy document placed at the plausible config locations is
neither adopted nor modified, and the only document migrated is the one passed
explicitly to `migrate --legacy-exec-config`.

Expected RED against the current tree (declared, not accidental):
`skills/cdad-cycle/scripts/cdad_dispatch.py` does not exist yet, so every CLI
test fails on its FIRST behavior assertion (the diagnostic does not name
`--runtime`/`runtimes.json`/the value/the path) and the installer tests fail on
the missing template. No failure is an ImportError, SyntaxError or fixture
error: the script is never imported and the fixture preconditions are asserted
with their own messages.

A-1 (U6-8 — REFORMULATED IN THE 006-005 U6-8 RED, with the replaced test,
the amended postcondition and the reason). The owner decision recorded in
`docs/epics/epic-006-opencode-concurrency/execution.md` (finding U6-8) makes
`binary_version` OPTIONAL and informative: the control compares the OBSERVED
versions (client against server), never a number written in the configuration,
so a difference with the configured one is DECLARED and does not block — and
the bounded migration step STOPS writing it. Three tests of this file fixed
the OLD behaviour (the migration carrying `binary_version` into the section)
and are REFORMULATED here. Amended postcondition: PD-25/§2.6.1 — the section
is written key by key for the keys the migration moves, and `binary_version`
is NOT one of them. Reason: the owner decision of the finding U6-8 (a number
written in the configuration can drift — it was 2.0.27 while the runtime had
already moved — and the version is observed at runtime):

  * `test_pd9_derived_section_is_inspected_key_by_key` (replaced),
  * `test_pd25_migrate_without_section_writes_the_section_key_by_key`
    (replaced),
  * `test_pd25_migrate_dry_run_does_not_write` (replaced: the section it
    announces is the one that WOULD be written, and it carries no version).

The key STAYS part of the section's vocabulary and the missing-section
diagnostic keeps naming it in the key-by-key correspondence, so
`test_pd9_missing_section_diagnostic_names_file_section_and_correspondence`
is CONSERVED and untouched.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DISPATCH = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_dispatch.py"

# §2.1: `opencode` has a runtime module (`cdad_delegate_opencode.py`); this id
# has none, so it is the "value without a module" case.
VALID_RUNTIME = "opencode"
UNKNOWN_RUNTIME = "no-such-runtime-u1a"
PACKET_ID = "006-005-u1a-fixture-packet"

# §2.6: the keys the section carries and the exact fixture values used to
# inspect the document key by key. The id of the section is the runtime.
#
# A-1 (U6-8 — owner decision, `docs/epics/epic-006-opencode-concurrency/
# execution.md` §hallazgo U6-8): `binary_version` becomes OPTIONAL and
# informative — the control compares the OBSERVED versions (client against
# server), never a number written in the configuration, so a difference with
# the configured one is DECLARED and does not block — and the bounded
# migration step STOPS writing it. The key stays part of the section's
# vocabulary (the owner may keep it as a note) and the missing-section
# diagnostic keeps naming it in the key-by-key correspondence
# (`test_pd9_missing_section_diagnostic_names_file_section_and_correspondence`
# is CONSERVED and untouched); what changes is that the migration does not
# CARRY the key. REFORMULATED IN THIS RED: the three tests that fixed the
# OLD behaviour — the migration step carrying `binary_version` into the
# section — are `test_pd9_derived_section_is_inspected_key_by_key`,
# `test_pd25_migrate_without_section_writes_the_section_key_by_key` and
# `test_pd25_migrate_dry_run_does_not_write`.
SECTION_KEYS: dict[str, object] = {
    "binary": "/fixture/bin/opencode",
    "binary_version": "9.9.9-fixture",
    "mode": "standalone",
    "server": "http://127.0.0.1:4096",
    "service": {"require": False},
    "auto": True,
    "sessions_db": "/fixture/store/sessions.db",
    "wait": {"timeout_seconds": 42},
}
# The keys the migration step WRITES (A-1 / U6-8: `binary_version` is not one
# of them — the version is observed at runtime, never carried from a
# document that can drift).
MIGRATED_SECTION_KEYS: dict[str, object] = {
    key: value for key, value in SECTION_KEYS.items() if key != "binary_version"
}
# §2.6 correspondence: these MUST NOT live in the section (the retired document
# carried them, the migration must not move them).
FORBIDDEN_SECTION_KEYS = ("runtime", "model", "credential_env_file")

LEGACY_MODEL = "fixture/legacy-exec-config-model-u1a"
LEGACY_CREDENTIAL_ENV_FILE = "/fixture/credentials/opencode-server.env"

# §2.6: the key-by-key correspondence the missing-section diagnostic names.
CORRESPONDENCE_KEYS = (
    "runtime", "binary", "binary_version", "mode", "server", "service",
    "auto", "sessions_db", "wait", "model",
)
CREDENTIAL_POINTER_RE = re.compile(
    r"(?i)credential|opencode-server\.env|credential_env_file")

# ------------------------------------------------------------------ installer
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"
STAGING_REL = Path("build") / "staging"
INSTALL_MANIFEST_NAME = ".cdad-install-manifest.json"
CONFIG_DIR_REL = Path(".config") / "cdad"
RUNTIMES_REL = CONFIG_DIR_REL / "runtimes.json"


# --------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, document: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def snapshot_tree(root: Path) -> dict[str, tuple]:
    """Content-level snapshot (dirs, sizes, sha256) — detects any write."""
    snapshot: dict[str, tuple] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        for name in dirnames:
            snapshot[str((base / name).relative_to(root)) + "/"] = ("dir",)
        for name in filenames:
            path = base / name
            try:
                data = path.read_bytes()
            except OSError as exc:  # an unreadable file is not a silent change
                snapshot[str(path.relative_to(root))] = ("unreadable", str(exc))
                continue
            snapshot[str(path.relative_to(root))] = (
                "file", len(data), sha256_bytes(data))
    return snapshot


def snapshot_diff(before: dict[str, tuple], after: dict[str, tuple]) -> list[str]:
    diff: list[str] = []
    for key in sorted(set(after) - set(before)):
        diff.append("created: %s" % key)
    for key in sorted(set(before) - set(after)):
        diff.append("removed: %s" % key)
    for key in sorted(set(before) & set(after)):
        if before[key] != after[key]:
            diff.append("modified: %s" % key)
    return diff


def legacy_exec_config() -> dict:
    """A retired exec-config (§2.6): the config keys plus `runtime`, `model`
    and the credential route. `model`/credential MUST NOT reach the section."""
    document = {
        "runtime": VALID_RUNTIME,
        "model": LEGACY_MODEL,
        "credential_env_file": LEGACY_CREDENTIAL_ENV_FILE,
    }
    document.update(SECTION_KEYS)
    return document


# ------------------------------------------------------------------- fixture


class DispatchCase(unittest.TestCase):
    """Disposable project + redirected config/HOME; the CLI runs as a process.

    Nothing touches the real `~/.config/cdad` nor the repository: the project
    is a per-test temporary directory, and both `XDG_CONFIG_HOME` and `HOME`
    are redirected inside it.
    """

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-u1a-runtime-")
        self.base = Path(self._tmp.name).resolve()
        self.config_home = self.base / "config-home"
        self.config_home.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.project = self.base / "project"
        self.project.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # -- harness ---------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        # Do not write bytecode into the repository's implementation tree.
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def run_dispatch(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(DISPATCH), *args],
            cwd=str(self.project),
            env=self.env(),
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )

    @staticmethod
    def output(result: subprocess.CompletedProcess) -> str:
        return (result.stdout or "") + (result.stderr or "")

    def default_args(self, runtime: str = VALID_RUNTIME) -> list[str]:
        """§2.1: `dispatch` is the default verb; `--runtime` is mandatory."""
        return [
            "--project-root", str(self.project),
            "--packet", PACKET_ID,
            "--runtime", runtime,
        ]

    def runtimes_path(self) -> Path:
        return self.config_home / "cdad" / "runtimes.json"

    def write_runtimes(self, document: object) -> Path:
        return write_json(self.runtimes_path(), document)

    def write_legacy(self, document: object | None = None,
                     name: str = "legacy-exec-config-u1a.json") -> Path:
        return write_json(
            self.base / name,
            legacy_exec_config() if document is None else document)

    def read_section(self) -> dict:
        document = json.loads(
            self.runtimes_path().read_text(encoding="utf-8"))
        runtimes = document.get("runtimes")
        self.assertIsInstance(
            runtimes, dict,
            "PD-9/§2.6: `runtimes.json` no trae un objeto `runtimes` por "
            "runtime: %r" % (runtimes,))
        self.assertIn(
            VALID_RUNTIME, runtimes,
            "PD-9/§2.6: falta la sección del runtime `%s` (secciones: %s)"
            % (VALID_RUNTIME, sorted(runtimes)))
        section = runtimes[VALID_RUNTIME]
        self.assertIsInstance(
            section, dict,
            "PD-9/§2.6: la sección de `%s` no es un objeto" % VALID_RUNTIME)
        return section

    def assert_section_key_by_key(self, section: dict) -> None:
        """§2.6: every key the migration moves keeps its value; nothing
        forbidden moved; and `binary_version` is NOT written (A-1 / U6-8)."""
        for key, expected in MIGRATED_SECTION_KEYS.items():
            self.assertIn(
                key, section,
                "PD-9/§2.6: la sección no tiene la clave `%s` (claves: %s)"
                % (key, sorted(section)))
            self.assertEqual(
                section[key], expected,
                "PD-9/§2.6: la sección no conserva el valor de `%s` "
                "(esperado %r, encontrado %r)" % (key, expected, section[key]))
        for forbidden in FORBIDDEN_SECTION_KEYS:
            self.assertNotIn(
                forbidden, section,
                "PD-9/§2.6: la sección NO debe contener `%s` (vive fuera de "
                "`runtimes.json`; encontrado %r)"
                % (forbidden, section.get(forbidden)))
        self.assertNotIn(
            "binary_version", section,
            "PD-25/§2.6.1 (A-1, U6-8): la migración NO escribe "
            "`binary_version` (la versión se OBSERVA; una diferencia con la "
            "configurada se declara y no bloquea): la sección migrada lo "
            "contiene (%r)" % section.get("binary_version"))


# ---------------------------------------------- PD-8: explicit runtime


class TestPd8ExplicitRuntimeResolution(DispatchCase):
    """PD-8/§2.1: `--runtime X` is mandatory in every verb, is the unique
    resolution (no document is read for it) and an id without a runtime module
    is rejected naming the value."""

    def test_pd8_missing_runtime_names_the_flag_on_the_default_verb(self) -> None:
        """PD-8: with no `--runtime` on the default verb, rc≠0 and the
        diagnostic names the flag (there is no project fallback)."""
        result = self.run_dispatch(
            "--project-root", str(self.project),
            "--packet", PACKET_ID)
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-8: sin `--runtime` la invocación debe fallar cerrado "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "--runtime", output,
            "PD-8: el diagnóstico no nombra el flag `--runtime`:\n%s"
            % tail(output))

    def test_pd8_missing_runtime_names_the_flag_on_an_explicit_verb(self) -> None:
        """PD-8: the same rejection on an explicit verb (`dispatch`)."""
        result = self.run_dispatch(
            "dispatch",
            "--project-root", str(self.project),
            "--packet", PACKET_ID)
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-8: sin `--runtime` el verbo explícito `dispatch` debe fallar "
            "cerrado (rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "--runtime", output,
            "PD-8: el diagnóstico del verbo explícito no nombra `--runtime`:\n%s"
            % tail(output))

    def test_pd8_runtime_without_a_module_is_rejected_naming_the_value(self) -> None:
        """PD-8: an id with no runtime module ⇒ rc≠0 naming the VALUE."""
        result = self.run_dispatch(*self.default_args(UNKNOWN_RUNTIME))
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-8: un runtime sin módulo debe fallar cerrado (rc=%s):\n%s"
            % (result.returncode, tail(output)))
        self.assertIn(
            UNKNOWN_RUNTIME, output,
            "PD-8: el diagnóstico no nombra el valor `%s` sin módulo:\n%s"
            % (UNKNOWN_RUNTIME, tail(output)))

    def test_pd8_valid_runtime_proceeds_to_the_single_source_check(self) -> None:
        """PD-8: a valid runtime passes resolution and reaches the NEXT check
        (the `runtimes.json` section, PD-9) — its diagnostic names the file."""
        result = self.run_dispatch(*self.default_args())
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-8 precondición: sin sección de config el despacho no puede "
            "completar (rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "runtimes.json", output,
            "PD-8: con un runtime válido la ejecución no llegó a la "
            "comprobación de la sección (el diagnóstico no nombra "
            "`runtimes.json`):\n%s" % tail(output))

    def test_pd8_flat_v1_context_runtime_is_never_read(self) -> None:
        """PD-8/V-9: a flat v1 context that DECLARES `runtime` is not a source:
        without the flag the invocation still fails naming `--runtime`."""
        write_json(
            self.project / ".cdad" / "execution.json",
            {
                "schema_version": 1,
                "execution_id": "exec-006-005-u1a-fixture-001",
                "runtime": VALID_RUNTIME,
                "hitl_delegation": {
                    "authority_ref": "docs/epics/epic-006-fixture/execution.md",
                    "expires_on": "2099-12-31",
                },
            })
        result = self.run_dispatch(
            "--project-root", str(self.project),
            "--packet", PACKET_ID)
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-8/V-9: el `runtime` de un contexto v1 plano NO debe resolver "
            "el destino; sin flag la invocación tiene que fallar (rc=%s):\n%s"
            % (result.returncode, tail(output)))
        self.assertIn(
            "--runtime", output,
            "PD-8/V-9: la entrada leyó el `runtime` del documento (o no nombró "
            "el flag obligatorio) — el diagnóstico no nombra `--runtime`:\n%s"
            % tail(output))


# ---------------------------------------------- PD-9: single config source


class TestPd9SingleConfigSource(DispatchCase):
    """PD-9/§2.6: the runtime section of `runtimes.json` is the only source;
    `model`/credential never live there; the retired `--exec-config` token is
    a usage error before any effect, in every verb, and is not declared."""

    def test_pd9_missing_section_diagnostic_names_file_section_and_correspondence(
            self) -> None:
        """PD-9/§2.6: with no section, rc≠0 and the diagnostic names
        `runtimes.json`, the runtime section and the key-by-key
        correspondence (including `model` → `delegation.json`)."""
        result = self.run_dispatch(*self.default_args())
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-9: sin sección la vía externa no tiene fuente y debe fallar "
            "cerrado (rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "runtimes.json", output,
            "PD-9/§2.6: el diagnóstico no nombra `runtimes.json`:\n%s"
            % tail(output))
        self.assertIn(
            VALID_RUNTIME, output,
            "PD-9/§2.6: el diagnóstico no nombra la sección del runtime `%s`:"
            "\n%s" % (VALID_RUNTIME, tail(output)))
        missing = [key for key in CORRESPONDENCE_KEYS if key not in output]
        self.assertEqual(
            missing, [],
            "PD-9/§2.6: el diagnóstico no nombra la correspondencia clave por "
            "clave; faltan %r en:\n%s" % (missing, tail(output, 40)))
        self.assertIn(
            "delegation.json", output,
            "PD-9/§2.6: la correspondencia no indica que `model` vive en "
            "`delegation.json`:\n%s" % tail(output))
        self.assertRegex(
            output, CREDENTIAL_POINTER_RE,
            "PD-9/§2.6: la correspondencia no indica dónde vive la credencial "
            "(`delegation.json`/`opencode-server.env`):\n%s" % tail(output))

    def test_pd9_section_with_model_is_rejected_naming_delegation_json(
            self) -> None:
        """PD-9/§2.6: a `model` key inside the runtime section is rejected
        naming `delegation.json`, without modifying the user's config file."""
        section = dict(SECTION_KEYS)
        section["model"] = LEGACY_MODEL
        path = self.write_runtimes(
            {"version": 1, "runtimes": {VALID_RUNTIME: section}})
        before = path.read_bytes()

        result = self.run_dispatch(*self.default_args())
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-9/§2.6: una sección con `model` debe rechazarse (rc=%s):\n%s"
            % (result.returncode, tail(output)))
        self.assertIn(
            "delegation.json", output,
            "PD-9/§2.6: el rechazo de `model` no nombra `delegation.json` "
            "(ADR-033 D3: el modelo se elige en un solo lugar):\n%s"
            % tail(output))
        self.assertEqual(
            path.read_bytes(), before,
            "PD-9/§2.6: el rechazo de `model` modificó el `runtimes.json` del "
            "usuario (es dato del dueño, INV-7)")

    def test_pd9_derived_section_is_inspected_key_by_key(self) -> None:
        """PD-9/§2.6: the document derived from the retired exec-config is the
        runtime section, inspected key by key; `runtime`, `model` and the
        credential do not move. Once it exists, the entry reads it as the
        single source (no further config diagnostic).

        A-1 (U6-8, owner decision): the section is inspected key by key for
        the keys the migration WRITES; `binary_version` is NOT one of them
        (the version is observed at runtime, a difference with the configured
        one is declared and does not block, and `migrate` stops writing it).
        """
        legacy = self.write_legacy()
        migrated = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(legacy), "--json")
        self.assertEqual(
            migrated.returncode, 0,
            "PD-9 precondición: la migración declarada falló (rc=%s):\n%s"
            % (migrated.returncode, tail(self.output(migrated))))

        section = self.read_section()
        self.assert_section_key_by_key(section)
        document_text = self.runtimes_path().read_text(encoding="utf-8")
        for forbidden_value in (LEGACY_MODEL, LEGACY_CREDENTIAL_ENV_FILE):
            self.assertNotIn(
                forbidden_value, document_text,
                "PD-9/§2.6/INV-12: el documento derivado transporta `%s`, que "
                "vive fuera de `runtimes.json`" % forbidden_value)

        result = self.run_dispatch(*self.default_args())
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-9 precondición: sin paquete la vía externa no completa "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        # The missing-section diagnostic carries the `model → delegation.json`
        # correspondence; with the section present that correspondence must be
        # gone (the failing check is now the packet, not the configuration).
        self.assertNotIn(
            "delegation.json", output,
            "PD-9/§2.6: con la sección presente la entrada sigue dando el "
            "diagnóstico de configuración de la sección ausente — la sección "
            "no es (o no es la única) fuente:\n%s" % tail(output))

    def test_pd9_exec_config_token_is_rejected_before_any_effect_default_verb(
            self) -> None:
        """PD-9/D-11: `--exec-config` in either form on the default verb is a
        usage error BEFORE any effect (no write), with the migration
        diagnostic."""
        legacy = self.write_legacy({"binary": "/fixture/legacy-not-read"})
        for form in (
            ["--exec-config", str(legacy)],
            ["--exec-config=%s" % legacy],
        ):
            with self.subTest(form=form[0]):
                before_project = snapshot_tree(self.project)
                before_config = snapshot_tree(self.base)
                before_legacy = legacy.read_bytes()
                result = self.run_dispatch(*self.default_args(), *form)
                output = self.output(result)
                self.assertNotEqual(
                    result.returncode, 0,
                    "PD-9/D-11: `%s` debe ser error de uso en el verbo por "
                    "defecto (rc=%s):\n%s"
                    % (form[0], result.returncode, tail(output)))
                self.assertIn(
                    "runtimes.json", output,
                    "PD-9/D-11: el rechazo de `%s` no trae el diagnóstico de "
                    "migración que nombra `runtimes.json`:\n%s"
                    % (form[0], tail(output)))
                changed = (
                    snapshot_diff(before_project, snapshot_tree(self.project))
                    + snapshot_diff(before_config, snapshot_tree(self.base)))
                self.assertEqual(
                    changed, [],
                    "PD-9/D-11: el rechazo de `%s` tuvo efectos de escritura "
                    "antes de fallar: %r" % (form[0], changed))
                self.assertEqual(
                    legacy.read_bytes(), before_legacy,
                    "PD-9/D-11: el rechazo de `%s` tocó el archivo heredado"
                    % form[0])

    def test_pd9_exec_config_token_is_rejected_before_any_effect_on_migrate_o7(
            self) -> None:
        """PD-9/O-7: the same usage error on `migrate`, both token forms,
        before any write (the migration only accepts its own
        `--legacy-exec-config` token)."""
        legacy = self.write_legacy()
        for form in (
            ["--exec-config", str(legacy)],
            ["--exec-config=%s" % legacy],
        ):
            with self.subTest(form=form[0]):
                before = snapshot_tree(self.base)
                result = self.run_dispatch(
                    "migrate", "--runtime", VALID_RUNTIME,
                    "--legacy-exec-config", str(legacy), *form)
                output = self.output(result)
                self.assertNotEqual(
                    result.returncode, 0,
                    "PD-9/O-7/D-11: `%s` debe ser error de uso también en "
                    "`migrate` (rc=%s):\n%s"
                    % (form[0], result.returncode, tail(output)))
                self.assertIn(
                    "runtimes.json", output,
                    "PD-9/O-7/D-11: el rechazo en `migrate` no trae el "
                    "diagnóstico de migración:\n%s" % tail(output))
                self.assertEqual(
                    snapshot_diff(before, snapshot_tree(self.base)), [],
                    "PD-9/O-7/D-11: el rechazo de `%s` en `migrate` escribió "
                    "antes de fallar" % form[0])
                self.assertFalse(
                    self.runtimes_path().exists(),
                    "PD-9/O-7/D-11: el rechazo de `%s` creó `runtimes.json`"
                    % form[0])

    def test_pd9_help_never_declares_the_retired_option(self) -> None:
        """PD-9/§2.1: negative control — `--help` succeeds and does NOT
        declare `--exec-config` (the retired token is not an option)."""
        result = self.run_dispatch("--help")
        output = self.output(result)
        self.assertEqual(
            result.returncode, 0,
            "PD-9/§2.1: `--help` no es una invocación válida de la entrada "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "--runtime", output,
            "PD-9/§2.1: `--help` no documenta el flag obligatorio `--runtime`"
            ":\n%s" % tail(output))
        self.assertNotIn(
            "--exec-config", output,
            "PD-9/§2.1: `--help` declara `--exec-config`, que la entrada NO "
            "tiene (la bandera de migración es `--legacy-exec-config`):\n%s"
            % tail(output))

    def test_pd9_legacy_document_is_not_probed_outside_the_migration_step(
            self) -> None:
        """PD-9/D-11: no conventional legacy location is probed — a legacy
        document placed at plausible config paths is neither adopted nor
        modified; the migrated values come only from the explicit file."""
        poison = legacy_exec_config()
        poison.update({
            "binary": "/fixture/poison-binary-u1a",
            "sessions_db": "/fixture/poison-store-u1a.db",
        })
        poison_paths = (
            self.config_home / "cdad" / "exec-config.json",
            self.config_home / "cdad" / "opencode-exec-config.json",
        )
        for path in poison_paths:
            write_json(path, poison)
        before = {path: path.read_bytes() for path in poison_paths}

        # (a) Without a section, the entry fails on the single source; it does
        # not adopt a legacy file found at a conventional path.
        result = self.run_dispatch(*self.default_args())
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-9/D-11 precondición: sin sección el despacho no completa "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "runtimes.json", output,
            "PD-9/D-11: la entrada no falló en la fuente única (¿adoptó un "
            "exec-config heredado por sondeo?):\n%s" % tail(output))
        self.assertFalse(
            self.runtimes_path().exists(),
            "PD-9/D-11: la entrada creó `runtimes.json` sin el paso de "
            "migración (¿sondeó una ubicación heredada?)")

        # (b) The migration reads the file it is given, not the poison files.
        explicit = self.write_legacy(name="explicit-legacy-u1a.json")
        migrated = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(explicit))
        self.assertEqual(
            migrated.returncode, 0,
            "PD-9/D-11 precondición: la migración explícita falló (rc=%s):\n%s"
            % (migrated.returncode, tail(self.output(migrated))))
        section = self.read_section()
        self.assertEqual(
            section.get("binary"), SECTION_KEYS["binary"],
            "PD-9/D-11: la sección migrada no salió del archivo explícito "
            "(encontrado binary=%r)" % section.get("binary"))
        self.assertNotIn(
            poison["binary"], json.dumps(section),
            "PD-9/D-11: la sección migrada adoptó el binario de un archivo "
            "heredado no pasado por el paso de migración")

        for path in poison_paths:
            self.assertEqual(
                path.read_bytes(), before[path],
                "PD-9/D-11/INV-7: la entrada modificó el documento heredado "
                "%s (es dato del dueño)" % path.name)


# ---------------------------------------------- PD-25: bounded migration


class TestPd25MigrationStep(DispatchCase):
    """PD-25/§2.6.1: `migrate --runtime X --legacy-exec-config FILE` writes the
    runtime section only if it does not exist, never overwrites it, does not
    write on `--dry-run`, and fails naming a missing legacy path."""

    def test_pd25_migrate_without_section_writes_the_section_key_by_key(
            self) -> None:
        """PD-25/§2.6.1: no section ⇒ rc=0, the section is written key by key,
        with no `model`, no credential value, and the output says where they
        live.

        A-1 (U6-8, owner decision): the section is written key by key for the
        keys the migration moves; `binary_version` is NOT written (the version
        is OBSERVED at runtime — a difference with the configured one is
        declared and does not block — so the migration stops carrying a
        version number that can drift).
        """
        legacy = self.write_legacy()
        result = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(legacy), "--json")
        output = self.output(result)
        self.assertEqual(
            result.returncode, 0,
            "PD-25/§2.6.1: la migración sin sección debe escribirla y "
            "terminar rc=0 (rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertTrue(
            self.runtimes_path().is_file(),
            "PD-25/§2.6.1: la migración no creó `%s`"
            % self.runtimes_path().name)

        document = json.loads(
            self.runtimes_path().read_text(encoding="utf-8"))
        self.assertEqual(
            document.get("version"), 1,
            "PD-25/§2.6.1: `runtimes.json` no declara `version: 1` "
            "(encontrado %r)" % document.get("version"))
        section = self.read_section()
        self.assert_section_key_by_key(section)

        document_text = self.runtimes_path().read_text(encoding="utf-8")
        for forbidden_value in (LEGACY_MODEL, LEGACY_CREDENTIAL_ENV_FILE):
            self.assertNotIn(
                forbidden_value, document_text,
                "PD-25/§2.6.1: la sección migrada transporta `%s` (el "
                "`model` y la credencial viven en `delegation.json`)"
                % forbidden_value)
        self.assertIn(
            "delegation.json", output,
            "PD-25/§2.6.1: la migración no informa que el `model` vive en "
            "`delegation.json`:\n%s" % tail(output))
        self.assertRegex(
            output, CREDENTIAL_POINTER_RE,
            "PD-25/§2.6.1: la migración no informa dónde vive la credencial:"
            "\n%s" % tail(output))

    def test_pd25_migrate_with_existing_section_refuses_and_keeps_bytes(
            self) -> None:
        """PD-25/INV-7: an existing section is never overwritten: rc≠0 and
        `runtimes.json` keeps its bytes."""
        existing_section = dict(SECTION_KEYS)
        existing_section["binary"] = "/fixture/user-owned-binary"
        path = self.write_runtimes(
            {"version": 1, "runtimes": {VALID_RUNTIME: existing_section}})
        before = path.read_bytes()

        legacy = self.write_legacy()
        result = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(legacy), "--json")
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-25/INV-7: migrar sobre una sección existente debe rechazarse "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            "runtimes.json", output,
            "PD-25/INV-7: el rechazo no nombra `runtimes.json`:\n%s"
            % tail(output))
        self.assertIn(
            VALID_RUNTIME, output,
            "PD-25/INV-7: el rechazo no nombra la sección `%s`:\n%s"
            % (VALID_RUNTIME, tail(output)))
        self.assertEqual(
            path.read_bytes(), before,
            "PD-25/INV-7: la migración PISÓ la sección existente (los bytes "
            "deben ser idénticos)")

    def test_pd25_migrate_dry_run_does_not_write(self) -> None:
        """PD-25/§2.6.1: `--dry-run` writes nothing and prints the section it
        would write, key and value by key and value.

        A-1 (U6-8, owner decision): the section it announces is the one the
        migration WOULD write — and `binary_version` is not part of it (the
        version is OBSERVED at runtime and the migration stops writing it).
        """
        legacy = self.write_legacy()
        before = snapshot_tree(self.base)

        result = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(legacy), "--dry-run", "--json")
        output = self.output(result)
        self.assertEqual(
            result.returncode, 0,
            "PD-25/§2.6.1: `--dry-run` debe terminar rc=0 (rc=%s):\n%s"
            % (result.returncode, tail(output)))
        changed = snapshot_diff(before, snapshot_tree(self.base))
        self.assertEqual(
            changed, [],
            "PD-25/§2.6.1: `--dry-run` escribió: %r" % changed)
        self.assertFalse(
            self.runtimes_path().exists(),
            "PD-25/§2.6.1: `--dry-run` creó `runtimes.json`")
        missing_keys = [key for key in MIGRATED_SECTION_KEYS if key not in output]
        self.assertEqual(
            missing_keys, [],
            "PD-25/§2.6.1: `--dry-run` no imprime la sección que escribiría; "
            "faltan las claves %r:\n%s" % (missing_keys, tail(output, 40)))
        missing_values = [
            str(value) for value in MIGRATED_SECTION_KEYS.values()
            if str(value) not in output
        ]
        self.assertEqual(
            missing_values, [],
            "PD-25/§2.6.1: `--dry-run` no imprime los valores de la sección "
            "que escribiría; faltan %r:\n%s"
            % (missing_values, tail(output, 40)))
        self.assertNotIn(
            str(SECTION_KEYS["binary_version"]), output,
            "PD-25/§2.6.1 (A-1, U6-8): `--dry-run` no anuncia una versión que "
            "la migración no escribe (`binary_version`=%r):\n%s"
            % (SECTION_KEYS["binary_version"], tail(output, 40)))

    def test_pd25_migrate_missing_legacy_file_fails_naming_the_path(
            self) -> None:
        """PD-25/§2.6.1: a missing legacy file ⇒ rc≠0 naming its path, with no
        write."""
        missing = self.base / "missing-legacy-exec-config-u1a.json"
        before = snapshot_tree(self.base)

        result = self.run_dispatch(
            "migrate", "--runtime", VALID_RUNTIME,
            "--legacy-exec-config", str(missing), "--json")
        output = self.output(result)
        self.assertNotEqual(
            result.returncode, 0,
            "PD-25/§2.6.1: un archivo heredado ausente debe fallar cerrado "
            "(rc=%s):\n%s" % (result.returncode, tail(output)))
        self.assertIn(
            str(missing), output,
            "PD-25/§2.6.1: el diagnóstico no nombra la ruta ausente `%s`:\n%s"
            % (missing, tail(output)))
        self.assertEqual(
            snapshot_diff(before, snapshot_tree(self.base)), [],
            "PD-25/§2.6.1: el fallo por archivo ausente escribió algo")
        self.assertFalse(
            self.runtimes_path().exists(),
            "PD-25/§2.6.1: el fallo por archivo ausente creó `runtimes.json`")


# ------------------------------------------- installer template (§2.6/PD-9)


class InstallerHarness(unittest.TestCase):
    """Product copy with staging regenerated in the copy; every install goes to
    a per-test `CDAD_INSTALL_ROOT` and a fake HOME inside the tempdir."""

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-u1a-template-")
        cls.base = Path(cls._tmp.name).resolve()
        cls.product = cls.base / "product"
        cls.product.mkdir()
        for entry in PRODUCT_ENTRIES:
            source = REPO_ROOT / entry
            target = cls.product / entry
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

        cls.generate_results: dict[str, subprocess.CompletedProcess[str]] = {}
        for runtime in RUNTIMES:
            cls.generate_results[runtime] = subprocess.run(
                [
                    sys.executable,
                    str(cls.product / "scripts" / "cdad-generate.py"),
                    "--runtime", runtime,
                    "--stack", STACK,
                    "--out", str(cls.product / STAGING_REL),
                ],
                cwd=str(cls.product),
                text=True,
                capture_output=True,
                check=False,
            )

        cls.fake_home = cls.base / "home"
        cls.fake_home.mkdir()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def assert_staging_ready(self) -> None:
        for runtime, result in self.generate_results.items():
            self.assertEqual(
                result.returncode, 0,
                "precondición del fixture: el generador falló para runtime=%s:"
                "\n%s" % (runtime, tail(result.stderr or result.stdout)))

    def new_root(self, name: str) -> Path:
        root = self.base / name
        root.mkdir()
        return root

    def installer_env(self, root: Path) -> dict:
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        env["HOME"] = str(self.fake_home)
        env.pop("XDG_CONFIG_HOME", None)
        return env

    def install_ok(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["bash", str(self.product / "install.sh"), *args],
            cwd=str(self.product),
            env=self.installer_env(root),
            text=True,
            capture_output=True,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        self.assertEqual(
            result.returncode, 0,
            "precondición: la instalación redirigida sobre %s falló (rc=%s):"
            "\n%s" % (root.name, result.returncode, tail(output)))
        return output


class TestInstallerRuntimeTemplate(InstallerHarness):
    """PD-9/§2.6 (plantilla) / INV-7: `install.sh` creates the `runtimes.json`
    template only when missing, never registers it in the ownership manifest
    and never overwrites the user's content."""

    def test_pd9_installer_creates_the_runtimes_template_when_missing(
            self) -> None:
        """PD-9/§2.6: a redirected install creates
        `<root>/.config/cdad/runtimes.json` as a valid v1 template."""
        self.assert_staging_ready()
        root = self.new_root("u1a-template")
        self.install_ok(root)

        template = root / RUNTIMES_REL
        self.assertTrue(
            template.is_file(),
            "PD-9/§2.6: el instalador no creó la plantilla de ejecución en %s"
            % RUNTIMES_REL.as_posix())
        document = json.loads(template.read_text(encoding="utf-8"))
        self.assertIsInstance(
            document, dict,
            "PD-9/§2.6: la plantilla de `runtimes.json` no es un objeto JSON")
        self.assertEqual(
            document.get("version"), 1,
            "PD-9/§2.6: la plantilla no declara `version: 1` (encontrado %r)"
            % document.get("version"))
        self.assertIsInstance(
            document.get("runtimes"), dict,
            "PD-9/§2.6: la plantilla no trae el mapa `runtimes` por runtime")

    def test_pd9_installer_does_not_register_the_template_in_the_manifest(
            self) -> None:
        """PD-9/§2.6/INV-7: the template is user data — absent from the
        ownership manifest."""
        self.assert_staging_ready()
        root = self.new_root("u1a-template-manifest")
        self.install_ok(root)
        self.assertTrue(
            (root / RUNTIMES_REL).is_file(),
            "PD-9/§2.6 precondición: el instalador no creó la plantilla, así "
            "que la ausencia en el manifiesto no probaría nada")

        manifest_path = root / INSTALL_MANIFEST_NAME
        self.assertTrue(
            manifest_path.is_file(),
            "PD-9 precondición: falta el manifiesto de ownership %s"
            % INSTALL_MANIFEST_NAME)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifacts = manifest.get("artifacts", manifest)
        registered = sorted(
            key for key in artifacts
            if str(key).endswith("runtimes.json")
            or str(key) == RUNTIMES_REL.as_posix())
        self.assertEqual(
            registered, [],
            "PD-9/§2.6/INV-7: la plantilla de `runtimes.json` figura en el "
            "manifiesto de ownership (es dato del usuario): %r"
            % registered)

    def test_pd9_reinstall_does_not_overwrite_the_user_runtimes_section(
            self) -> None:
        """PD-9/§2.6/INV-7: content written by the user in `runtimes.json`
        survives a second install byte for byte."""
        self.assert_staging_ready()
        root = self.new_root("u1a-template-user-data")
        self.install_ok(root)
        template = root / RUNTIMES_REL
        self.assertTrue(
            template.is_file(),
            "PD-9/§2.6 precondición: la primera instalación no creó la "
            "plantilla")

        user_document = {
            "version": 1,
            "runtimes": {
                "fixture-user-runtime": {"binary": "/fixture/user-binary"},
            },
        }
        write_json(template, user_document)
        user_bytes = template.read_bytes()
        digest = sha256_bytes(user_bytes)

        self.install_ok(root)
        self.assertEqual(
            sha256_bytes(template.read_bytes()), digest,
            "PD-9/§2.6/INV-7: la reinstalación PISÓ el `runtimes.json` del "
            "usuario (los bytes deben ser idénticos)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
