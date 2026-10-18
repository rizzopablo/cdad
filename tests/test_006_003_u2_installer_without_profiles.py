#!/usr/bin/env python3
"""RED tests for 006-003 U2: the installer has no profiles.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18) — §2.1 (installer CLI, decision D1), PD-1a (the retired
profile flags are rejected with a diagnostic pointing at the delegation config,
and the installer names none of them), PD-1g (control: `--check` PASSes on a
fresh redirected install), D1 (`--basic` accepted, deprecated, no effect, with a
one-line warning and no marker), the orchestrator amendment A-1
(`CDAD_MODEL_PROFILE` accepted and ignored with the same one-line warning), INV-6
(a redirected root is the only thing the install touches) and INV-7 (nothing
silent: every ignored surface says so).

Unit: U2 of the approved plan (ficha U2). The generator/Makefile surface
(PD-1b..PD-1f) belongs to U1 and is NOT asserted here. The `profile` key of the
ownership manifest (PD-1d) is asserted by the reformulated
`tests/test_install_ownership.py`; the delegation config files themselves
(PD-2a..d) belong to U4.

Oracle discipline (black-box): the installer runs as a subprocess against a
PRODUCT COPY whose staging is generated in the copy (never the repo, never
HOME — `CDAD_INSTALL_ROOT` points at a per-test temporary directory). What is
inspected is the published surface: exit codes, stdout/stderr, and the deployed
tree. Two exceptions are the postconditions' OWN subjects, asserted without
printing their content: the `install.sh` source lines that PD-1a bans (line
numbers only, mirroring `grep -nE`) and the `--help` text (pattern presence,
never dumped).

Mapping (one test per numbered postcondition / decision):

- test_pd_1a_*  -> PD-1a  (retired profile flags rejected: rc!=0, no deploy,
                            diagnostic naming `delegation.json`; the installer
                            source names none of the three flags)
- test_d1_*     -> D1 / §2.1 (`--basic` accepted + one-line deprecation warning
                            + no `.cdad-models-profile` marker)
- test_a_1_*    -> A-1 (D1b) (`CDAD_MODEL_PROFILE` accepted and ignored with the
                            same warning shape, no marker, installed agents with
                            no `model:` line)
- test_pd_1a_help_* -> PD-1a / §2.1 (`--help` names no retired profile flag and
                            no concrete model)
- test_pd_1g_*  -> PD-1g (`install.sh --check` on a fresh redirected install
                            -> PASS)
- test_inv_6_*  -> INV-6 (the redirected install creates/modifies nothing
                            outside the redirected root; the fake HOME of the
                            test is compared byte for byte)

Expected RED against the current tree (declared, not accidental): the three
profile flags install successfully (rc=0, 368 deployed files), `--basic` and
`CDAD_MODEL_PROFILE=optimus` publish the `.cdad-models-profile` marker with no
deprecation line, the installer source carries the three flag spellings (9
occurrences today) and `--help` names the flags and concrete models.

Expected GREEN controls today (declared, so a later failure is readable): PD-1g
(`--check` already exits 0 on a fresh install) and INV-6 (the redirected install
already leaves the fake HOME untouched, and it already installs agents without
`model:` because U1 retired the model map). Those controls guard the redirect
harness itself; they are not evidence that U2 is done.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"

# Public product entries the installer needs next to install.sh (same set the
# 004-001 acceptance matrix declares).
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"
STAGING_REL = Path("build") / "staging"

# PD-1a: the three retired profile flags.
RETIRED_PROFILE_FLAGS = ("--economical", "--optimus", "--premium")
RETIRED_PROFILE_FLAG_RE = re.compile(r"--(economical|optimus|premium)")
INSTALLER_REF = "install.sh"

# D1 / §2.1: the retired label surfaces.
PROFILE_MARKER_NAME = ".cdad-models-profile"
INSTALL_MANIFEST_NAME = ".cdad-install-manifest.json"
DELEGATION_CONFIG_NAME = "delegation.json"
MODEL_ENV_VAR = "CDAD_MODEL_PROFILE"

# §2.1: the rejection diagnostic names the delegation config as the place where
# the model is chosen (today the output only mentions `delegation.md`).
DELEGATION_POINTER_RE = re.compile(r"(?i)delegation\.json")

# A deprecation notice is one line carrying the deprecated surface (D1/A-1).
DEPRECATION_RE = re.compile(r"(?i)(deprecat|obsolet)")

# INV-3/PD-1e, reused from the U1 focal oracle: no installable text fixes a model.
MODEL_LINE_RE = re.compile(r"^model:")
MODEL_NAME_RE = re.compile(r"deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/")

# A-3: configuration files are user data, not a deployment.
CONFIG_PREFIX = ".config/"


# --------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def text_files(root: Path, name_glob: str) -> list[Path]:
    return sorted(p for p in root.rglob(name_glob) if p.is_file())


def deployed_non_config(root: Path) -> list[str]:
    """Install-root-relative paths of everything the install deployed.

    `A-3` declares the delegation config files user data (they live under
    `.config/` of the redirected root); PD-1a 'ningún despliegue ocurre' is
    asserted over everything else.
    """
    found: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            rel = str((Path(dirpath) / filename).relative_to(root))
            if rel.startswith(CONFIG_PREFIX):
                continue
            found.append(rel)
    return sorted(found)


def find_profile_markers(root: Path) -> list[str]:
    """Install-root-relative paths of the retired `.cdad-models-profile` marker."""
    found: list[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if PROFILE_MARKER_NAME in filenames:
            found.append(str((Path(dirpath) / PROFILE_MARKER_NAME).relative_to(root)))
    return sorted(found)


def deprecation_lines(output: str) -> list[str]:
    """Every line of `output` that carries a deprecation notice."""
    return [line for line in output.splitlines() if DEPRECATION_RE.search(line)]


def deprecation_notices(output: str, subject: str) -> list[str]:
    """Deprecation notice lines that refer to `subject` (or an adjacent line).

    The contract fixes the SHAPE («aviso de deprecación de una línea»), not the
    wording, so the notice is located by the deprecation lexicon and its
    adjacency to the deprecated surface.
    """
    lines = output.splitlines()
    notices: list[str] = []
    for index, line in enumerate(lines):
        if not DEPRECATION_RE.search(line):
            continue
        window = " ".join(lines[max(0, index - 1) : index + 2])
        if subject in window:
            notices.append(line)
    return notices


def snapshot_tree(root: Path) -> dict[str, tuple]:
    """Content-level snapshot of a tree (dirs, sizes, sha256 of every file)."""
    snapshot: dict[str, tuple] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        for name in dirnames:
            snapshot[str((base / name).relative_to(root)) + "/"] = ("dir",)
        for name in filenames:
            path = base / name
            try:
                data = path.read_bytes()
            except OSError as exc:  # a file the test cannot read is not a change
                snapshot[str(path.relative_to(root))] = ("unreadable", str(exc))
                continue
            snapshot[str(path.relative_to(root))] = (
                "file",
                len(data),
                hashlib.sha256(data).hexdigest(),
            )
    return snapshot


def snapshot_diff(before: dict[str, tuple], after: dict[str, tuple]) -> list[str]:
    """Human-sized description of a changed tree (keys only, never contents)."""
    diff: list[str] = []
    for key in sorted(set(after) - set(before)):
        diff.append("created: %s" % key)
    for key in sorted(set(before) - set(after)):
        diff.append("removed: %s" % key)
    for key in sorted(set(before) & set(after)):
        if before[key] != after[key]:
            diff.append("modified: %s" % key)
    return diff


# --------------------------------------------------------------------- fixture


class InstallerFixture(unittest.TestCase):
    """Product copy with staging generated in the copy + a redirected root.

    Nothing is installed into HOME or into the repository: every install root is
    a per-test temporary directory passed as `CDAD_INSTALL_ROOT`, and the fake
    HOME passed to the subprocess lives in the same temporary directory.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-u2-installer-")
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

        # Staging is generated in the COPY (U1: the generator has no profiles),
        # so the installer's declared input is fresh and never the repo's build/.
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

    # -- helpers ----------------------------------------------------------

    def assert_staging_ready(self) -> None:
        for runtime, result in self.generate_results.items():
            self.assertEqual(
                result.returncode,
                0,
                "precondición del fixture: el generador falló para runtime=%s "
                "(PD-1f, unidad U1):\n%s"
                % (runtime, tail(result.stderr or result.stdout)),
            )

    def new_root(self, name: str = "root") -> Path:
        root = self.base / name
        root.mkdir()
        return root

    def installer_env(self, root: Path, **overrides: str) -> dict:
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_"):
                env.pop(key)
        env["CDAD_INSTALL_ROOT"] = str(root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        # INV-6: the fake HOME of the test, never the real one; the config dir
        # stays undefined so §2.2 resolves it under the redirected root.
        env["HOME"] = str(self.fake_home)
        env.pop("XDG_CONFIG_HOME", None)
        env.pop(MODEL_ENV_VAR, None)
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

    def installer_help(self) -> subprocess.CompletedProcess[str]:
        """`--help` never installs; it only publishes the CLI surface."""
        return subprocess.run(
            ["bash", str(self.product / "install.sh"), "--help"],
            cwd=str(self.product),
            env=self.installer_env(self.base),
            text=True,
            capture_output=True,
            check=False,
        )

    # -- PD-1a: the retired profile flags -------------------------------

    def test_pd_1a_retired_profile_flags_are_rejected_without_deploying(self) -> None:
        """PD-1a/§2.1: each retired profile flag -> rc!=0, nothing deployed, and
        a diagnostic that names the delegation config as the place where the
        model is chosen. Control of non-vacuity: the redirected install is known
        to deploy when it accepts a flag (asserted by the D1 test)."""
        self.assert_staging_ready()
        for flag in RETIRED_PROFILE_FLAGS:
            with self.subTest(flag=flag):
                root = self.new_root("reject%s" % flag.lstrip("-"))
                result = self.run_installer(root, flag)
                output = result.stdout + result.stderr

                self.assertNotEqual(
                    result.returncode,
                    0,
                    "PD-1a: `install.sh %s` was accepted (rc=0); the installer "
                    "has no profiles and must refuse it with a diagnostic:\n%s"
                    % (flag, tail(output)),
                )
                deployed = deployed_non_config(root)
                self.assertEqual(
                    deployed,
                    [],
                    "PD-1a: `install.sh %s` refused with rc=%s but still deployed "
                    "files: %s"
                    % (flag, result.returncode, deployed[:10]),
                )
                self.assertRegex(
                    output,
                    DELEGATION_POINTER_RE,
                    "PD-1a/§2.1: the rejection of %s does not name the delegation "
                    "config (%s) as the place where the model is chosen:\n%s"
                    % (flag, DELEGATION_CONFIG_NAME, tail(output)),
                )

    def test_pd_1a_installer_source_names_no_retired_profile_flag(self) -> None:
        """PD-1a: the installer source carries none of the three retired flags.

        Only line NUMBERS are reported (never the matching lines), so the
        implementation stays unseen by the test-writer session. A rejection path
        that must recognize the flags cannot spell them literally.
        """
        self.assertTrue(
            (self.product / INSTALLER_REF).is_file(),
            "PD-1a: the declared installer %s is missing in the product copy"
            % INSTALLER_REF,
        )
        result = subprocess.run(
            [
                "grep",
                "-nE",
                "--",
                "--(economical|optimus|premium)",
                str(self.product / INSTALLER_REF),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        line_numbers = [
            line.split(":", 1)[0] for line in result.stdout.splitlines() if line
        ]
        self.assertEqual(
            line_numbers,
            [],
            "PD-1a: %s still contains the retired profile flags (matching line "
            "numbers: %s); only `--basic` survives as a deprecated alias (D1)"
            % (INSTALLER_REF, line_numbers),
        )

    def test_pd_1a_help_names_no_retired_profile_flag_nor_model(self) -> None:
        """PD-1a/§2.1: the published help names no retired profile flag and no
        concrete model. `--basic` may still be documented as the deprecated
        alias (D1) — the help is not dumped, only pattern hits are asserted."""
        self.assert_staging_ready()
        result = self.installer_help()
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            "PD-1a: `install.sh --help` exited with rc=%s:\n%s"
            % (result.returncode, tail(output)),
        )
        self.assertIsNone(
            RETIRED_PROFILE_FLAG_RE.search(output),
            "PD-1a/§2.1: `--help` still names retired profile flags: %s"
            % sorted(set(RETIRED_PROFILE_FLAG_RE.findall(output))),
        )
        self.assertIsNone(
            MODEL_NAME_RE.search(output),
            "PD-1a/§2.1: `--help` still names concrete models: %s"
            % sorted(set(MODEL_NAME_RE.findall(output))),
        )

    # -- D1: `--basic` is a deprecated, effect-free alias ----------------

    def test_d1_basic_is_a_deprecated_no_op_with_one_line_warning_and_no_marker(self) -> None:
        """D1/§2.1: `install.sh --basic` is accepted (rc=0), warns once, and does
        not write the retired `.cdad-models-profile` marker."""
        self.assert_staging_ready()
        root = self.new_root("basic")
        result = self.run_installer(root, "--basic")
        output = result.stdout + result.stderr

        self.assertEqual(
            result.returncode,
            0,
            "D1/§2.1: `install.sh --basic` must stay accepted (deprecated alias) "
            "so the existing recipes keep working (rc=%s):\n%s"
            % (result.returncode, tail(output)),
        )

        notices = deprecation_notices(output, "--basic")
        self.assertEqual(
            len(notices),
            1,
            "D1/§2.1: `--basic` must produce exactly one one-line deprecation "
            "notice (found %d):\n%s" % (len(notices), tail(output)),
        )
        self.assertEqual(
            len(deprecation_lines(output)),
            1,
            "D1/§2.1 (INV-7, nothing silent): the deprecation notice must be a "
            "single line and no other deprecation line may appear in the same "
            "run (found %d)" % len(deprecation_lines(output)),
        )

        markers = find_profile_markers(root)
        self.assertEqual(
            markers,
            [],
            "D1/§2.1: the install still wrote the retired profile marker: %s"
            % markers,
        )

    # -- A-1: `CDAD_MODEL_PROFILE` accepted and ignored ------------------

    def test_a_1_cdad_model_profile_is_ignored_with_the_same_warning_and_no_marker(self) -> None:
        """A-1 (D1b resolvable) / §2.1: `CDAD_MODEL_PROFILE=optimus install.sh`
        is accepted (rc=0), warns once like `--basic`, writes no marker, and
        installs agents with no `model:` line (INV-3/PD-1e: the surface is gone,
        the env var changes nothing)."""
        self.assert_staging_ready()
        root = self.new_root("model-profile-env")
        result = self.run_installer(
            root, env_extra={MODEL_ENV_VAR: "optimus"}
        )
        output = result.stdout + result.stderr

        self.assertEqual(
            result.returncode,
            0,
            "A-1/§2.1: `%s=optimus install.sh` must be accepted and ignored "
            "(rc=%s):\n%s" % (MODEL_ENV_VAR, result.returncode, tail(output)),
        )

        notices = deprecation_notices(output, MODEL_ENV_VAR)
        self.assertEqual(
            len(notices),
            1,
            "A-1/§2.1 (INV-7): `%s` must be ignored WITH a one-line deprecation "
            "notice — the same shape as `--basic` (found %d notices):\n%s"
            % (MODEL_ENV_VAR, len(notices), tail(output)),
        )

        markers = find_profile_markers(root)
        self.assertEqual(
            markers,
            [],
            "A-1/§2.1: `%s` still resolved a profile and wrote the marker: %s"
            % (MODEL_ENV_VAR, markers),
        )

        agents = text_files(root, "cdad-*.md")
        self.assertTrue(
            agents,
            "A-1/§2.1: the accepted install deployed no agent at all — the "
            "absence of `model:` cannot be observed",
        )
        offenders = [
            str(path.relative_to(root))
            for path in agents
            if any(MODEL_LINE_RE.match(line) for line in path.read_text(encoding="utf-8").splitlines())
        ]
        self.assertEqual(
            offenders,
            [],
            "A-1/INV-3/PD-1e: `%s` still produced agents carrying a `model:` "
            "line: %s" % (MODEL_ENV_VAR, offenders),
        )

    # -- PD-1g: the negative control -------------------------------------

    def test_pd_1g_check_passes_on_a_fresh_redirected_install(self) -> None:
        """PD-1g: after installing on a redirected root, `install.sh --check` on
        that root PASSes (the retired profile surface leaves no drift behind).

        PASS is observed as rc=0 plus the published PASS line and no drift
        report, the same oracle the 004-001 acceptance matrix uses for `--check`.
        """
        self.assert_staging_ready()
        root = self.new_root("check")
        install = self.run_installer(root, "--basic")
        self.assertEqual(
            install.returncode,
            0,
            "PD-1g precondición: la instalación redirigida falló (rc=%s):\n%s"
            % (install.returncode, tail(install.stdout + install.stderr)),
        )

        check = self.run_installer(root, "--check")
        output = check.stdout + check.stderr
        self.assertEqual(
            check.returncode,
            0,
            "PD-1g: `install.sh --check` must PASS on a freshly installed "
            "redirected root (rc=%s):\n%s" % (check.returncode, tail(output)),
        )
        self.assertRegex(
            output,
            r"(?i)\bpass\b",
            "PD-1g: `--check` exited 0 but published no PASS report:\n%s"
            % tail(output),
        )
        self.assertIsNone(
            re.search(r"(?i)conflict|drift|pending.?removal|mismatch", output),
            "PD-1g: `--check` reported drift/conflict on a fresh install:\n%s"
            % tail(output),
        )

    # -- INV-6: nothing outside the redirected root ----------------------

    def test_inv_6_redirected_install_touches_nothing_outside_the_root(self) -> None:
        """INV-6: with `CDAD_INSTALL_ROOT` set, the install creates or modifies
        nothing outside that root — verified by comparing the fake HOME of the
        test byte for byte, and by the absence of new siblings next to the
        root/home temporary directories.

        Non-vacuity: the same run must have actually installed into the root.
        """
        self.assert_staging_ready()
        root = self.new_root("inv6-root")
        before_home = snapshot_tree(self.fake_home)
        before_base = sorted(entry.name for entry in self.base.iterdir())

        result = self.run_installer(root, "--basic")
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            "INV-6 precondición: la instalación redirigida falló (rc=%s):\n%s"
            % (result.returncode, tail(output)),
        )

        installed = deployed_non_config(root)
        self.assertTrue(
            installed or (root / INSTALL_MANIFEST_NAME).is_file(),
            "INV-6: the redirected install deployed nothing into %s — the "
            "isolation check would be vacuous" % root,
        )

        after_home = snapshot_tree(self.fake_home)
        self.assertEqual(
            snapshot_diff(before_home, after_home),
            [],
            "INV-6: the redirected install touched the fake HOME "
            "(CDAD_INSTALL_ROOT must confine every write):\n%s"
            % "\n".join(snapshot_diff(before_home, after_home)[:10]),
        )

        after_base = sorted(entry.name for entry in self.base.iterdir())
        self.assertEqual(
            after_base,
            before_base,
            "INV-6: the redirected install created new entries outside the "
            "install root (base dir before=%s after=%s)"
            % (before_base, after_base),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
