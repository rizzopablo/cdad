#!/usr/bin/env python3
"""RED tests for 006-003 U4 — the delegation config is the single source of
the model (installer creates it; the external delegation reads only it).

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18), §2.2 (`delegation.json` v1, D3), the postconditions
PD-2a..d and PD-3a..d, the orchestrator amendments A-2 (`destination-id` is the
identifier of the destination runtime — `opencode` for the OpenCode adapter),
A-3 (the two config files are USER DATA: created only when missing, NOT
registered in the ownership manifest, never removed by `--uninstall` nor by the
PD-6 obsolete-retirement), A-4 (U4 creates BOTH config files), and INV-6
(a redirected root is the only thing the install touches) / INV-7 (nothing
silent). Plan: the approved U4 sheet of
docs/specs/006-003-installer-single-profile-delegation-config/plan.md.

Mapping (one test per numbered postcondition):

- test_pd_2a_*  -> PD-2a  (redirected install, no XDG_CONFIG_HOME: valid v1
                            `delegation.json` with the `opencode` destination
                            key + `opencode-server.env.example`, both under
                            `<root>/.config/cdad/`)
- test_pd_2b_*  -> PD-2b  (every non-comment line of the `.example` is `KEY=`
                            with an EMPTY value: no secret)
- test_pd_2c_*  -> PD-2c  (with XDG_CONFIG_HOME the two files move under
                            `$XDG_CONFIG_HOME/cdad/` and NOT under the root)
- test_pd_2d_a_3_* -> PD-2d + A-3 (a user-edited `delegation.json` survives a
                            second install byte for byte with a notice (no
                            CONFLICT); neither file is in the ownership
                            manifest; `--uninstall` leaves both in place)
- test_pd_3a_*  -> PD-3a  (`opencode-exec-config.example.json` has no `model`)
- test_pd_3b_*  -> PD-3b  (exec-config `model: X` + delegation
                            `opencode/<role> -> Y`: the destination argv
                            carries `--model Y`, and a one-line deprecation
                            notice names the `delegation.json` path)
- test_pd_3c_*  -> PD-3c  (role without a delegation entry: no `--model` in
                            argv; the I8 observation records
                            `model_configured: null` with provenance pointing
                            at the delegation config, not the exec-config)
- test_pd_3d_*  -> PD-3d  (`references/cli-delegation.md` § Configuration no
                            longer lists the model as an exec-config key)

Oracle discipline (black-box). The installer runs as a subprocess against a
PRODUCT COPY (staging regenerated in the copy, never the repo, never HOME: the
per-test `CDAD_INSTALL_ROOT` plus a fake HOME confine every write). The
external delegation runs through the SAME fake destination binary the adapter
suite already uses (`tests/test_005_009_t2_opencode_adapter.py::AdapterCase`,
reused by import — no implementation is read): the process frontier is the fake
binary that records its argv, never a live runtime, never the host config
(the delegation path is redirected with `XDG_CONFIG_HOME`/`HOME` to the test
tempdir). The two installable TEXT artifacts of PD-3a/PD-3d are asserted as the
postconditions' OWN subjects (existence + a JSON key / a section-key oracle),
never dumped.

Declared deviation (honest limit, PD-15): the `§ Configuration` region of
`references/cli-delegation.md` was sampled with a read-only `sed` (bash is
permissive for this writer role) to design the PD-3d key-listing oracle; only
that declared text artifact was looked at — no `scripts/` implementation was
read, and the EXPECTATION still comes from the spec ("deja de listar el modelo
como clave de la exec-config"), not from the current text.

Expected RED against the current tree (declared, not accidental): the installer
creates neither config file (PD-2a/2b/2c/2d fail on the missing file/notice),
the exec-config example still carries `model` (PD-3a), the adapter ignores any
`delegation.json` and keeps `--model` from the exec-config with no deprecation
notice (PD-3b), the I8 record's `model_configured` has no delegation provenance
(PD-3c), and the `§ Configuration` prose still lists the model among the
exec-config keys (PD-3d). Every failure is an AssertionError about missing
behavior, never an ImportError/syntax/fixture error.
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

# Reuse declared by import (single definition; fixture bases carry no test
# methods, so importing them imports no foreign tests).
from test_005_009_t1_interface import dispatch_records
from test_005_009_t2_opencode_adapter import AdapterCase

REPO_ROOT = Path(__file__).resolve().parents[1]

# ------------------------------------------------------------------ installer
# Same public product entries the 004-001 acceptance matrix and the U2 focal
# declare.
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"
STAGING_REL = Path("build") / "staging"

INSTALL_MANIFEST_NAME = ".cdad-install-manifest.json"
CONFIG_DIR_REL = Path(".config") / "cdad"
DELEGATION_REL = CONFIG_DIR_REL / "delegation.json"
ENV_EXAMPLE_REL = CONFIG_DIR_REL / "opencode-server.env.example"

# A-2: the destination id is the destination runtime identifier.
DESTINATION_ID = "opencode"
# The packet's role (the delegation entry is keyed by role, §2.2).
ROLE = "test-writer"

# PD-2b: a non-comment line is exactly `KEY=` with an empty value.
ENV_LINE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=$")

# A-3: a second install must NOTICE the pre-existing config (not CONFLICT).
EXISTING_RE = re.compile(
    r"(?i)already|exist|existe|present|preserv|conserv|kept|intact|"
    r"not overwrit|no se pisa|left (as|untouched)|unchanged")
CONFLICT_RE = re.compile(r"(?i)conflict")

# ------------------------------------------------------- installable text
EXEC_CONFIG_EXAMPLE = (
    REPO_ROOT / "skills" / "cdad-cycle" / "assets"
    / "opencode-exec-config.example.json")
CLI_DELEGATION_MD = (
    REPO_ROOT / "skills" / "cdad-cycle" / "references" / "cli-delegation.md")

# PD-3d: the exec-config contents/keys the § Configuration prose enumerates.
# Kept narrow on purpose so the unrelated "provider, concrete model, server,
# times" hygiene sentence does not trip the oracle.
EXEC_CONFIG_CONTENT_TOKENS = (
    "runtime", "binary", "logs", "servers", "timeouts", "sessions_db", "mode")
MODEL_TOKEN_RE = re.compile(r"(?i)\bmodel\b")
DELEGATION_WORD_RE = re.compile(r"(?i)delegation|delegaci")
# A `model` presented as a key (table first cell / definition line).
MODEL_AS_KEY_RE = re.compile(r"(?im)^\s*\|?\s*`?model`?\s*(\||:|=)")
HEADING_RE = re.compile(r"(?m)^(#{1,6})[ \t]+(.*?)[ \t]*$")

# -------------------------------------------------------------------- adapter
# Test-local placeholder models (no host value): X is the legacy exec-config
# model, Y the delegation-config model, Z another role's entry.
EXEC_CONFIG_MODEL = "fixture-exec-config-model-u4"
DELEGATION_MODEL = "fixture-delegation-model-u4"
OTHER_ROLE_MODEL = "fixture-delegation-other-role-u4"
DEPRECATION_RE = re.compile(r"(?i)deprecat|obsolet")


# --------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def manifest_artifact_keys(manifest_path: Path) -> list[str]:
    """Relative paths recorded by the ownership manifest (`artifacts`)."""
    doc = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = doc.get("artifacts", doc)
    return sorted(artifacts)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def existing_notices(output: str, subject: str) -> list[str]:
    """Lines that notice `subject` already exists / is preserved untouched."""
    return [
        line for line in output.splitlines()
        if EXISTING_RE.search(line) and subject in line
    ]


def conflict_lines(output: str, subject: str) -> list[str]:
    return [
        line for line in output.splitlines()
        if CONFLICT_RE.search(line) and subject in line
    ]


def configuration_section(text: str) -> str | None:
    """Body of the `Configuration` section (heading-level delimited)."""
    headings = list(HEADING_RE.finditer(text))
    for index, heading in enumerate(headings):
        if re.match(r"(?i)^configuration\b", heading.group(2).strip()):
            level = len(heading.group(1))
            end = len(text)
            for later in headings[index + 1:]:
                if len(later.group(1)) <= level:
                    end = later.start()
                    break
            return text[heading.end():end]
    return None


def model_listed_as_exec_config_key(section: str) -> list[str]:
    """Lines of `section` that list the model among the exec-config keys.

    Two detectors: (a) a content line that enumerates at least two exec-config
    keys AND names the model (unless it is the sentence that explicitly points
    the model AT the delegation config); (b) a `model` presented as a key.
    """
    hits: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if MODEL_AS_KEY_RE.match(line):
            hits.append(stripped)
            continue
        if not MODEL_TOKEN_RE.search(stripped):
            continue
        if DELEGATION_WORD_RE.search(stripped):
            continue
        tokens = sum(
            1 for token in EXEC_CONFIG_CONTENT_TOKENS
            if re.search(r"(?i)\b" + re.escape(token), stripped))
        if tokens >= 2:
            hits.append(stripped)
    return hits


# ------------------------------------------------------- installer fixture


class InstallerHarness(unittest.TestCase):
    """Product copy with staging generated in the copy + a redirected root.

    Nothing installs into HOME or the repository: every install root is a
    per-test temporary directory passed as `CDAD_INSTALL_ROOT`, and the fake
    HOME lives in the same temporary directory (INV-6).
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-u4-delegation-")
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
                    "--runtime",
                    runtime,
                    "--stack",
                    STACK,
                    "--out",
                    str(cls.product / STAGING_REL),
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
                result.returncode,
                0,
                "precondición del fixture: el generador falló para runtime=%s "
                "(PD-1f):\n%s" % (runtime, tail(result.stderr or result.stdout)),
            )

    def new_root(self, name: str) -> Path:
        root = self.base / name
        root.mkdir()
        return root

    def installer_env(self, root: Path, **overrides: str) -> dict:
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        # INV-6: the fake HOME of the test, never the real one; XDG_CONFIG_HOME
        # stays undefined unless the test overrides it (PD-2c).
        env["HOME"] = str(self.fake_home)
        env.pop("XDG_CONFIG_HOME", None)
        env.update({key: str(value) for key, value in overrides.items()})
        return env

    def run_installer(
        self, root: Path, *args: str, env_extra: dict | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.product / "install.sh"), *args],
            cwd=str(self.product),
            env=self.installer_env(root, **(env_extra or {})),
            text=True,
            capture_output=True,
            check=False,
        )

    def install_ok(self, root: Path, *args: str,
                   env_extra: dict | None = None) -> str:
        result = self.run_installer(root, *args, env_extra=env_extra)
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            "precondición: la instalación redirigida falló (rc=%s):\n%s"
            % (result.returncode, tail(output)),
        )
        return output


# ------------------------------------------------- PD-2: config created


class TestPd2InstallerDelegationConfig(InstallerHarness):
    """PD-2a..d / §2.2 / A-3 / A-4: the installer creates the delegation
    config and the server credential example as USER DATA under the redirected
    config dir, never touching HOME."""

    def test_pd_2a_installer_creates_delegation_config_and_env_example(self) -> None:
        """PD-2a/§2.2/A-2/A-4: with `CDAD_INSTALL_ROOT` and no
        `XDG_CONFIG_HOME`, the install creates
        `<root>/.config/cdad/delegation.json` (valid JSON, `version: 1`,
        `models` keyed by the destination id `opencode`) and
        `<root>/.config/cdad/opencode-server.env.example`."""
        self.assert_staging_ready()
        root = self.new_root("pd2a")
        self.install_ok(root)

        delegation = root / DELEGATION_REL
        example = root / ENV_EXAMPLE_REL
        self.assertTrue(
            delegation.is_file(),
            "PD-2a: el instalador no creó la config de delegación en "
            "%s" % DELEGATION_REL.as_posix(),
        )
        self.assertTrue(
            example.is_file(),
            "PD-2a: el instalador no creó el ejemplo de credencial del "
            "servidor en %s" % ENV_EXAMPLE_REL.as_posix(),
        )

        doc = json.loads(delegation.read_text(encoding="utf-8"))
        self.assertIsInstance(doc, dict, "PD-2a: delegation.json no es un objeto")
        self.assertEqual(
            doc.get("version"), 1,
            "PD-2a/§2.2: delegation.json no declara `version: 1` "
            "(encontrado %r)" % doc.get("version"),
        )
        models = doc.get("models")
        self.assertIsInstance(
            models, dict, "PD-2a/§2.2: `models` no es un objeto por destino")
        self.assertIn(
            DESTINATION_ID, models,
            "PD-2a/A-2: `models` no tiene la clave del destino de runtime "
            "`%s`: %s" % (DESTINATION_ID, sorted(models)),
        )
        self.assertIsInstance(
            models[DESTINATION_ID], dict,
            "PD-2a/§2.2: `models[%r]` no es un mapa rol→modelo" % DESTINATION_ID)

    def test_pd_2b_env_example_lines_are_empty_valued_keys(self) -> None:
        """PD-2b/§2.3: every non-comment line of the `.example` has the form
        `KEY=` with an EMPTY value; it carries no secret and declares at least
        one key."""
        self.assert_staging_ready()
        root = self.new_root("pd2b")
        self.install_ok(root)

        example = root / ENV_EXAMPLE_REL
        self.assertTrue(
            example.is_file(),
            "PD-2b: el `.example` no existe en %s (precondición de la "
            "forma)" % ENV_EXAMPLE_REL.as_posix(),
        )
        data_lines = [
            stripped
            for line in example.read_text(encoding="utf-8").splitlines()
            if (stripped := line.strip()) and not stripped.startswith("#")
        ]
        self.assertTrue(
            data_lines,
            "PD-2b: el `.example` no declara ninguna clave (todas las líneas "
            "son comentarios/vacías)",
        )
        bad = [line for line in data_lines if not ENV_LINE_RE.match(line)]
        self.assertEqual(
            bad, [],
            "PD-2b/§2.3: hay líneas del `.example` que no tienen la forma "
            "`KEY=` con valor vacío (¿secreto?): %r" % bad,
        )

    def test_pd_2c_config_home_redirects_both_files_out_of_the_root(self) -> None:
        """PD-2c/§2.2: with `XDG_CONFIG_HOME=C` both config files are created
        under `C/cdad/` and NOT under the redirected root."""
        self.assert_staging_ready()
        root = self.new_root("pd2c-root")
        config_home = self.base / "pd2c-xdg"
        config_home.mkdir()
        self.install_ok(root, env_extra={"XDG_CONFIG_HOME": str(config_home)})

        self.assertTrue(
            (config_home / "cdad" / "delegation.json").is_file(),
            "PD-2c/§2.2: con XDG_CONFIG_HOME definida, delegation.json no "
            "quedó bajo $XDG_CONFIG_HOME/cdad/",
        )
        self.assertTrue(
            (config_home / "cdad" / "opencode-server.env.example").is_file(),
            "PD-2c/§2.2: con XDG_CONFIG_HOME definida, el `.example` no quedó "
            "bajo $XDG_CONFIG_HOME/cdad/",
        )
        self.assertFalse(
            (root / DELEGATION_REL).exists(),
            "PD-2c/§2.2: con XDG_CONFIG_HOME definida, delegation.json NO debe "
            "crearse bajo la raíz (quedó en %s)" % DELEGATION_REL.as_posix(),
        )
        self.assertFalse(
            (root / ENV_EXAMPLE_REL).exists(),
            "PD-2c/§2.2: con XDG_CONFIG_HOME definida, el `.example` NO debe "
            "crearse bajo la raíz (quedó en %s)" % ENV_EXAMPLE_REL.as_posix(),
        )

    def test_pd_2d_a_3_config_files_are_user_data_surviving_reinstall_and_uninstall(
            self) -> None:
        """PD-2d + A-3: a user-edited `delegation.json` survives a second
        install byte for byte (with a notice, never a CONFLICT); neither file
        is registered in the ownership manifest; `--uninstall` leaves both in
        place."""
        self.assert_staging_ready()
        root = self.new_root("pd2d")
        self.install_ok(root)

        delegation = root / DELEGATION_REL
        example = root / ENV_EXAMPLE_REL
        self.assertTrue(
            delegation.is_file(),
            "PD-2d precondición: la primera instalación no creó delegation.json",
        )
        self.assertTrue(
            example.is_file(),
            "PD-2d precondición: la primera instalación no creó el `.example`",
        )

        # The user edits the config (a valid but different document).
        doc = json.loads(delegation.read_text(encoding="utf-8"))
        doc.setdefault("models", {}).setdefault(DESTINATION_ID, {})[ROLE] = (
            "user/edited-model")
        delegation.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        edited_sha = file_sha256(delegation)

        second_output = self.install_ok(root)
        self.assertEqual(
            file_sha256(delegation), edited_sha,
            "PD-2d: la segunda instalación PISÓ el delegation.json editado por "
            "el usuario (los bytes deben ser idénticos)",
        )
        notices = (existing_notices(second_output, "delegation.json")
                   + existing_notices(second_output, "opencode-server.env.example"))
        self.assertTrue(
            notices,
            "PD-2d/A-3: la segunda instalación no avisó que la config de "
            "usuario ya existe (INV-7: nada silencioso):\n%s"
            % tail(second_output),
        )
        self.assertEqual(
            conflict_lines(second_output, "delegation.json"), [],
            "PD-2d/A-3: la segunda instalación reportó la config del usuario "
            "como CONFLICT (A-3: no es CONFLICT):\n%s" % tail(second_output),
        )

        # A-3: neither file is recorded in the ownership manifest.
        manifest = root / INSTALL_MANIFEST_NAME
        self.assertTrue(
            manifest.is_file(),
            "A-3 precondición: falta el manifiesto de ownership %s"
            % INSTALL_MANIFEST_NAME,
        )
        keys = manifest_artifact_keys(manifest)
        for rel in (DELEGATION_REL, ENV_EXAMPLE_REL):
            self.assertNotIn(
                rel.as_posix(), keys,
                "A-3: %s NO debe figurar en el manifiesto de ownership "
                "(artefactos registrados: %s…)"
                % (rel.as_posix(), keys[:8]),
            )

        # A-3: `--uninstall` leaves the user data in place.
        uninstall = self.run_installer(root, "--uninstall", "--force")
        uninstall_output = uninstall.stdout + uninstall.stderr
        self.assertEqual(
            uninstall.returncode, 0,
            "A-3 precondición: `--uninstall` terminó con rc=%s:\n%s"
            % (uninstall.returncode, tail(uninstall_output)),
        )
        self.assertTrue(
            delegation.is_file(),
            "A-3: `--uninstall` borró el delegation.json del usuario (la "
            "config de usuario nunca se retira)",
        )
        self.assertTrue(
            example.is_file(),
            "A-3: `--uninstall` borró el `.example` del usuario (la config de "
            "usuario nunca se retira)",
        )


# ------------------------------------------- PD-3a: exec-config example


class TestPd3aExecConfigExampleWithoutModel(unittest.TestCase):
    """PD-3a/§2.2/D3: the installable exec-config example fixes no model."""

    def test_pd_3a_exec_config_example_declares_no_model_key(self) -> None:
        """PD-3a: `skills/cdad-cycle/assets/opencode-exec-config.example.json`
        does not contain the `model` key (the model is chosen in the delegation
        config, §2.2)."""
        self.assertTrue(
            EXEC_CONFIG_EXAMPLE.is_file(),
            "PD-3a: falta el ejemplo declarado por el contrato: %s"
            % EXEC_CONFIG_EXAMPLE.relative_to(REPO_ROOT).as_posix(),
        )
        doc = json.loads(EXEC_CONFIG_EXAMPLE.read_text(encoding="utf-8"))
        self.assertIsInstance(
            doc, dict, "PD-3a: el ejemplo no es un objeto JSON")
        self.assertNotIn(
            "model", doc,
            "PD-3a/§2.2/D3: el ejemplo de exec-config sigue declarando la "
            "clave `model` (%r); el modelo se elige en la config de delegación"
            % doc.get("model"),
        )


# ------------------------------------------- PD-3d: cli-delegation doc


class TestPd3dCliDelegationConfigurationSection(unittest.TestCase):
    """PD-3d/§2.2/D3: the `Configuration` section of the installable
    `cli-delegation.md` no longer lists the model as an exec-config key."""

    def test_pd_3d_configuration_section_lists_no_model_key(self) -> None:
        """PD-3d: the `§ Configuration` region of
        `references/cli-delegation.md` does not present the model as a key of
        the execution configuration."""
        self.assertTrue(
            CLI_DELEGATION_MD.is_file(),
            "PD-3d: falta el documento declarado por el contrato: %s"
            % CLI_DELEGATION_MD.relative_to(REPO_ROOT).as_posix(),
        )
        section = configuration_section(
            CLI_DELEGATION_MD.read_text(encoding="utf-8"))
        self.assertIsNotNone(
            section,
            "PD-3d: `cli-delegation.md` no expone una sección `Configuration` "
            "delimitable por su encabezado",
        )
        hits = model_listed_as_exec_config_key(section)
        self.assertEqual(
            hits, [],
            "PD-3d/§2.2/D3: la sección `Configuration` sigue listando el "
            "modelo como clave de la exec-config: %r" % hits,
        )


# ------------------------------------------- PD-3b/3c: external delegation


class DelegationAdapterCase(AdapterCase):
    """Adapter fixture (reused black-box) plus the delegation config redirected
    by env to the test tempdir: the host's `~/.config/cdad` is never read."""

    def config_home(self, name: str = "xdg-config") -> Path:
        path = Path(self._tmp) / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_delegation(self, models: dict, *, config_home: Path) -> Path:
        cdad = config_home / "cdad"
        cdad.mkdir(parents=True, exist_ok=True)
        path = cdad / "delegation.json"
        path.write_text(
            json.dumps({"version": 1, "models": models},
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def set_config_model(self, fake: dict, model: str | None) -> dict:
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        if model is None:
            config.pop("model", None)
        else:
            config["model"] = model
        fake["config"].write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return config

    def run_delegated(self, fake: dict, *, config_home: Path,
                      destination: str = "opencode") -> subprocess.CompletedProcess:
        home = Path(self._tmp) / "home"
        home.mkdir(parents=True, exist_ok=True)
        env = {
            **os.environ,
            "XDG_CONFIG_HOME": str(config_home),
            "HOME": str(home),
            "PWD": str(self.root),
        }
        return subprocess.run(
            [sys.executable, str(self.staged),
             "--project-root", str(self.root),
             "--packet", self.packet_id,
             "--destination", destination,
             "--exec-config", str(fake["config"])],
            capture_output=True, text=True, env=env, timeout=300)

    def attempt_record(self, out: dict, records_before: dict) -> dict:
        path = self.assert_attempt_is_in_ledger(out, records_before)
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def deprecation_lines(output: str, subject: str = "delegation.json") -> list[str]:
        return [
            line for line in output.splitlines()
            if DEPRECATION_RE.search(line) and subject in line
        ]


class TestPd3bDelegationConfigIsTheModelSource(DelegationAdapterCase):
    """PD-3b/§2.2/D3: with an exec-config that declares `model: X` and a
    delegation config mapping the destination+role to `Y`, the destination argv
    carries `--model Y` (X is ignored) and a one-line deprecation notice names
    the `delegation.json` path."""

    def test_pd_3b_argv_uses_the_delegation_model_and_warns_about_the_legacy_key(
            self) -> None:
        """PD-3b/§2.2/D3/INV-7: the effective model comes ONLY from
        `delegation.json`; the legacy exec-config `model` is ignored with a
        one-line deprecation diagnosis that names the delegation config."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd3b", variant="succeeded")
        self.set_config_model(fake, EXEC_CONFIG_MODEL)
        config_home = self.config_home()
        self.write_delegation(
            {DESTINATION_ID: {ROLE: DELEGATION_MODEL}}, config_home=config_home)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_delegated(fake, config_home=config_home)
        out = self.envelope(proc, "PD-3b")
        self.assertEqual(
            out["termination"], "completed",
            "PD-3b precondición: la delegación no completó "
            "(termination=%r)" % out["termination"],
        )

        call = self.packet_call(fake, "PD-3b")
        argv = call["argv"]
        paired = (
            "--model" in argv
            and argv.index("--model") + 1 < len(argv)
            and argv[argv.index("--model") + 1] == DELEGATION_MODEL
        )
        self.assertTrue(
            paired or ("--model=" + DELEGATION_MODEL) in argv,
            "PD-3b/D3: el argv del destino no lleva `--model %s` — el modelo "
            "efectivo debe salir SOLO de la config de delegación: %r"
            % (DELEGATION_MODEL, argv),
        )
        self.assertNotIn(
            EXEC_CONFIG_MODEL, argv,
            "PD-3b/D3: el argv del destino lleva el `model` de la exec-config "
            "(%r); ese valor debe ignorarse: %r" % (EXEC_CONFIG_MODEL, argv),
        )

        output = proc.stdout + proc.stderr
        notices = self.deprecation_lines(output)
        self.assertEqual(
            len(notices), 1,
            "PD-3b/D3/INV-7: se espera EXACTAMENTE un diagnóstico de "
            "deprecación de una línea que nombre la ruta de `delegation.json` "
            "al ignorar el `model` de la exec-config (encontrados %d):\n%s"
            % (len(notices), tail(output)),
        )


class TestPd3cRoleWithoutDelegationEntry(DelegationAdapterCase):
    """PD-3c/§2.2/D3: a role without a delegation entry has NO model — the
    destination argv carries no `--model`, the I8 observation records
    `model_configured: null` and its provenance points at the delegation
    config (never at the exec-config)."""

    def test_pd_3c_role_without_entry_has_no_model_and_delegation_provenance(
            self) -> None:
        """PD-3c/§2.2/D3: without an entry for the packet's role, no `--model`
        in the destination argv; the I8 record's `model_configured` is null
        and `provenance.model_configured` names the delegation config."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("pd3c", variant="succeeded")
        # The new normal: the exec-config no longer carries a model.
        self.set_config_model(fake, None)
        config_home = self.config_home()
        self.write_delegation(
            {DESTINATION_ID: {"reviewer": OTHER_ROLE_MODEL}},
            config_home=config_home)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_delegated(fake, config_home=config_home)
        out = self.envelope(proc, "PD-3c")
        self.assertEqual(
            out["termination"], "completed",
            "PD-3c precondición: la delegación no completó "
            "(termination=%r)" % out["termination"],
        )

        call = self.packet_call(fake, "PD-3c")
        self.assertNotIn(
            "--model", call["argv"],
            "PD-3c/D3: un rol sin entrada en la config de delegación NO debe "
            "llevar `--model` en el argv (sin fallback): %r" % call["argv"],
        )

        record = self.attempt_record(out, records_before)
        self.assertIn(
            "model_configured", record,
            "PD-3c: el registro I8 no expone `model_configured`",
        )
        self.assertIsNone(
            record.get("model_configured"),
            "PD-3c/§2.2: `model_configured` debe ser null cuando el rol no "
            "tiene entrada en la config de delegación (encontrado %r)"
            % record.get("model_configured"),
        )
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict,
            "PD-3c: el registro I8 no trae un mapa `provenance` campo→fuente",
        )
        source = provenance.get("model_configured")
        self.assertIsInstance(
            source, str,
            "PD-3c/§2.2: `provenance.model_configured` debe declarar que el "
            "modelo se resuelve en la config de delegación (no en la "
            "exec-config): %r" % provenance,
        )
        self.assertRegex(
            source, r"(?i)delegation",
            "PD-3c/§2.2: `provenance.model_configured` (%r) no apunta a la "
            "config de delegación" % source,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
