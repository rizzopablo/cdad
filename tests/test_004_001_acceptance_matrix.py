#!/usr/bin/env python3
r"""Acceptance criterion 1 of spec §4.1 (004-001 closure): the smoke matrix.

Matrix: runtime (opencode, claude-code) × role (11 agents per runtime =
5 roles × 2 stacks + orchestrator) × supported profile (basic, economical,
optimus, premium), verified from an ISOLATED installation with synthetic
data and zero provider calls.

Packet: 004-001-canonical-runtime-artifacts-test-writer-red-011 (substage
red). The T6 oracle (tests/test_004_001_t6.py) is FROZEN and is NOT modified
here; this file adds the two missing axes: (a) all four supported profiles,
(b) the orchestrator (11 agents per runtime).

Black-box discipline: only public interfaces are used — the generator CLI
(`scripts/cdad-generate.py --runtime <r> --stack odoo --profile <p> --out`),
install.sh (`--<profile>`, `--<profile> --check`) and the OBSERVABLE deployed
artifacts (installed frontmatter, real destinations under CDAD_INSTALL_ROOT).
The generator/installer internals and sources/ composition are never read.
ONE declared data exception, authorized by the packet objective:
`scripts/cdad-models.sh` is EXECUTED as the data contract (the single source
of the model map) to compute the expected `model:` frontmatter per
profile × runtime × role — the test never hardcodes the map.

Interpretation registered (data contract governs): the objective's
"el orquestador sin model:" holds for OpenCode (cdad_model never fixes the
orchestrator). For Claude Code the data contract DOES fix the orchestrator
(`*\|orchestrator` → opus, cdad_model_claude), so the CC orchestrator cell
expects `model: opus` for every non-basic profile and no model line for
basic (basic returns before any case).

Behavioral probes recorded while building this oracle (all logged under
/tmp/opencode/probe-matrix):
- One staging accumulates BOTH runtimes (second generator run keeps the
  first runtime's artifacts; manifest lists 22 artifacts).
- install.sh refuses to run without an `agents/` directory next to
  install.sh ("Source agents directory missing") even though the deployed
  agent bytes come EXCLUSIVELY from staging (PD-18): discriminating probe —
  basic staging generated in a copy whose agents/ carry `model:` lines
  landed WITHOUT model lines. The copy therefore includes agents/ as a
  precondition of the public interface; deployed bytes stay staged bytes.
- install.sh requires CDAD_INSTALL_ROOT to be an EXISTING absolute
  directory (pre-created by the fixture).
- Profile flag must match the staging profile (PROFILE MISMATCH otherwise);
  this test always generates staging with the same profile as the flag.

Test -> contract mapping (every test -> acceptance §4.1 of the spec):

- test_acceptance_1_all_cells_installed            -> §4.1 (every cell of
    the runtime × 11-roles × profile matrix exists at its real runtime
    destination after an isolated install)
- test_acceptance_1_frontmatter_coherent_with_profile -> §4.1 (installed
    frontmatter is coherent with the profile per the data contract:
    model: present and equal where cdad-models.sh fixes it, absent where
    it returns empty — basic fixes nothing)
- test_acceptance_1_install_check_rc0              -> §4.1 (install.sh
    --check exits 0 for the isolated install of each profile)
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"
MODELS_SH = REPO_ROOT / "scripts" / "cdad-models.sh"
INSTALLER = REPO_ROOT / "install.sh"

# The 11 agents per runtime (T6 frozen role set + orchestrator; stack odoo
# produces base cells cdad-<role>.md and odoo cells cdad-<role>-odoo.md).
ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")
ROLE_NAMES = (
    ROLE_AGENTS
    + tuple(f"{role}-odoo" for role in ROLE_AGENTS)
    + ("orchestrator",)
)

PROFILES = (
    ("basic", "--basic"),
    ("economical", "--economical"),
    ("optimus", "--optimus"),
    ("premium", "--premium"),
)

RUNTIMES = ("opencode", "claude-code")

# Real runtime destinations under the isolated install root (same frozen set
# T6 uses; orchestrator-confirmed):
AGENT_DESTINATIONS = {
    "opencode": ".config/opencode/agents",
    "claude-code": ".claude/agents",
}

# Product entries the public interfaces require next to install.sh.
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")

MODEL_LINE_RE = re.compile(r"^model:\s*(.*?)\s*$")


def cdad_models_expectations(profile: str) -> dict[tuple[str, str], str]:
    """Execute the DATA contract (cdad-models.sh) and map (runtime, role) -> model.

    The map is never hardcoded: this function RUNS the declared single source
    (`scripts/cdad-models.sh`, authorized by the packet objective) and returns
    cdad_model / cdad_model_claude per role. Empty string means the contract
    fixes no model for that cell (installed agent must NOT carry model:).
    Premium env overrides are stripped for determinism (defaults expected).
    """
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("CDAD_PREMIUM_MODEL_"):
            env.pop(key)
    script = (
        "set -u; source %s\n"
        "for role in %s; do\n"
        "  printf 'opencode|%%s|%%s\\n' \"$role\" \"$(cdad_model %s \"$role\")\"\n"
        "  printf 'claude-code|%%s|%%s\\n' \"$role\" \"$(cdad_model_claude %s \"$role\")\"\n"
        "done\n"
        % (MODELS_SH, " ".join(ROLE_NAMES), profile, profile)
    )
    result = subprocess.run(
        ["bash", "-c", script],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "el contrato de datos scripts/cdad-models.sh falló al ejecutarse "
            f"para el perfil {profile}: {result.stderr.strip()}"
        )
    expectations: dict[tuple[str, str], str] = {}
    for line in result.stdout.splitlines():
        runtime, role, value = line.split("|", 2)
        expectations[(runtime, role)] = value.strip()
    missing = [
        (runtime, role)
        for runtime in RUNTIMES
        for role in ROLE_NAMES
        if (runtime, role) not in expectations
    ]
    if missing:
        raise AssertionError(
            f"cdad-models.sh no resolvió {len(missing)} celdas para el perfil "
            f"{profile}: {missing[:5]}"
        )
    return expectations


def frontmatter_model(agent_text: str) -> str | None:
    """Return the frontmatter `model:` value, or None when absent."""
    lines = agent_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = MODEL_LINE_RE.match(line)
        if match:
            return match.group(1)
    return None


def tail(text: str, lines: int = 30) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


class _AcceptanceMatrixProfile(unittest.TestCase):
    """Per-profile fixture: product copy -> staging -> isolated install.

    Everything happens under one temporary directory created by this fixture:
    a product copy (never the repo's build/) and a pre-created install root
    passed via CDAD_INSTALL_ROOT (never the real HOME).
    """

    PROFILE: str = ""
    FLAG: str = ""
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-acc-matrix-")
        base = Path(cls._tmp.name).resolve()
        cls.product_copy = base / "product"
        cls.product_copy.mkdir()
        for entry in PRODUCT_ENTRIES:
            source = REPO_ROOT / entry
            destination = cls.product_copy / entry
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)
        cls.staging = cls.product_copy / "build" / "staging"
        cls.generate_results: dict[str, subprocess.CompletedProcess] = {}
        for runtime in RUNTIMES:
            cls.generate_results[runtime] = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR),
                    "--runtime",
                    runtime,
                    "--stack",
                    "odoo",
                    "--profile",
                    cls.PROFILE,
                    "--out",
                    str(cls.staging),
                ],
                cwd=str(cls.product_copy),
                text=True,
                capture_output=True,
                check=False,
            )
        cls.install_root = base / "install-root"
        cls.install_root.mkdir()
        install_env = cls._installer_env()
        cls.install_result = subprocess.run(
            ["bash", str(cls.product_copy / "install.sh"), cls.FLAG],
            cwd=str(cls.product_copy),
            env=install_env,
            text=True,
            capture_output=True,
            check=False,
        )
        cls.check_result = subprocess.run(
            ["bash", str(cls.product_copy / "install.sh"), cls.FLAG, "--check"],
            cwd=str(cls.product_copy),
            env=install_env,
            text=True,
            capture_output=True,
            check=False,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    @classmethod
    def _installer_env(cls) -> dict:
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_"):
                env.pop(key)
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        return env

    def assert_pipeline_succeeded(self) -> None:
        """Generation + install must have succeeded (isolated, staged bytes)."""
        for runtime in RUNTIMES:
            self.assertEqual(
                self.generate_results[runtime].returncode,
                0,
                "el generador falló para runtime=%s perfil=%s:\n%s"
                % (
                    runtime,
                    self.PROFILE,
                    tail(
                        self.generate_results[runtime].stderr
                        or self.generate_results[runtime].stdout
                    ),
                ),
            )
        self.assertEqual(
            self.install_result.returncode,
            0,
            "la instalación aislada falló (perfil=%s, flag=%s):\n%s"
            % (
                self.PROFILE,
                self.FLAG,
                tail(self.install_result.stderr or self.install_result.stdout),
            ),
        )

    def agent_path(self, runtime: str, role: str) -> Path:
        destination = self.install_root / AGENT_DESTINATIONS[runtime]
        return destination / f"cdad-{role}.md"


class TestAcceptanceMatrixBasic(_AcceptanceMatrixProfile):
    PROFILE = "basic"
    FLAG = "--basic"


class TestAcceptanceMatrixEconomical(_AcceptanceMatrixProfile):
    PROFILE = "economical"
    FLAG = "--economical"


class TestAcceptanceMatrixOptimus(_AcceptanceMatrixProfile):
    PROFILE = "optimus"
    FLAG = "--optimus"


class TestAcceptanceMatrixPremium(_AcceptanceMatrixProfile):
    PROFILE = "premium"
    FLAG = "--premium"


# --- tests (defined once on the base; each profile subclass runs them) ------


def all_cells_installed(self: _AcceptanceMatrixProfile) -> None:
    """§4.1: every runtime × 11-roles cell exists at its real destination."""
    self.assert_pipeline_succeeded()
    for runtime in RUNTIMES:
        for role in ROLE_NAMES:
            with self.subTest(perfil=self.PROFILE, runtime=runtime, rol=role):
                cell = self.agent_path(runtime, role)
                self.assertTrue(
                    cell.is_file(),
                    "celda de matriz ausente: perfil=%s runtime=%s rol=%s -> %s"
                    % (self.PROFILE, runtime, role, cell),
                )


def frontmatter_coherent_with_profile(self: _AcceptanceMatrixProfile) -> None:
    """§4.1: installed frontmatter matches the cdad-models.sh data contract."""
    self.assert_pipeline_succeeded()
    expectations = cdad_models_expectations(self.PROFILE)
    for runtime in RUNTIMES:
        for role in ROLE_NAMES:
            with self.subTest(perfil=self.PROFILE, runtime=runtime, rol=role):
                cell = self.agent_path(runtime, role)
                self.assertTrue(
                    cell.is_file(),
                    "celda de matriz ausente: perfil=%s runtime=%s rol=%s -> %s"
                    % (self.PROFILE, runtime, role, cell),
                )
                installed = frontmatter_model(cell.read_text(encoding="utf-8"))
                expected = expectations[(runtime, role)]
                if expected == "":
                    self.assertIsNone(
                        installed,
                        "frontmatter incoherente con el perfil %s: %s trae "
                        "model: %r y el contrato de datos no fija modelo "
                        "(sin línea model:)" % (self.PROFILE, cell.name, installed),
                    )
                else:
                    self.assertIsNotNone(
                        installed,
                        "frontmatter incoherente con el perfil %s: %s no trae "
                        "model: y el contrato de datos fija %r"
                        % (self.PROFILE, cell.name, expected),
                    )
                    self.assertEqual(
                        installed,
                        expected,
                        "frontmatter incoherente con el perfil %s: %s trae "
                        "model: %r y el contrato de datos fija %r"
                        % (self.PROFILE, cell.name, installed, expected),
                    )


def install_check_rc0(self: _AcceptanceMatrixProfile) -> None:
    """§4.1: install.sh --check exits 0 for this profile's isolated install."""
    self.assert_pipeline_succeeded()
    self.assertEqual(
        self.check_result.returncode,
        0,
        "install.sh --check no está en rc=0 para el perfil %s:\n%s"
        % (self.PROFILE, tail(self.check_result.stderr or self.check_result.stdout)),
    )


for _cls in (
    TestAcceptanceMatrixBasic,
    TestAcceptanceMatrixEconomical,
    TestAcceptanceMatrixOptimus,
    TestAcceptanceMatrixPremium,
):
    _cls.test_acceptance_1_all_cells_installed = all_cells_installed
    _cls.test_acceptance_1_frontmatter_coherent_with_profile = (
        frontmatter_coherent_with_profile
    )
    _cls.test_acceptance_1_install_check_rc0 = install_check_rc0
del _cls


if __name__ == "__main__":
    unittest.main(verbosity=2)
