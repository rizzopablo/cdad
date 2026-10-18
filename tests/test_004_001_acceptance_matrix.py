#!/usr/bin/env python3
r"""Acceptance criterion 1 of spec §4.1 (004-001 closure): the smoke matrix.

Matrix: runtime (opencode, claude-code) × role (11 agents per runtime =
5 roles × 2 stacks + orchestrator), verified from an ISOLATED installation
with synthetic data and zero provider calls.

Packet: 004-001-canonical-runtime-artifacts-test-writer-red-011 (substage
red). The T6 oracle (tests/test_004_001_t6.py) is FROZEN and is NOT modified
here; this file adds the two missing axes: (a) the full supported set of
roles per runtime, (b) the orchestrator (11 agents per runtime).

ORACLE REPLACEMENT (006-003 U1 — spec docs/specs/006-003-installer-single-
profile-delegation-config/spec.md, PD-1/PD-1c/PD-1d/PD-1e/INV-3). This matrix
was profile-coupled; what changed and why, so no assert is dropped silently:

- The PROFILE axis is RETIRED. The four `--<profile>` install flags
  (`--basic`, `--economical`, `--optimus`, `--premium`) no longer deploy
  distinct model sets: per D1/PD-1a `--economical|--optimus|--premium` are
  rejected and `--basic` survives only as a deprecated, no-effect alias
  (the >=6 test recipes that pass it keep working — D1). The matrix therefore
  runs ONE cell set with `--basic` and asserts the model axis is GONE rather
  than varying it. The flag-rejection surface (PD-1a) belongs to the installer
  unit of 006-003 and is not asserted here.
- `scripts/cdad-models.sh` is NO LONGER executed as a data contract: it is
  retired (PD-1c) and the generator has no model map. The former
  `cdad_models_expectations()` helper is therefore DELETED, and
  `test_acceptance_1_frontmatter_coherent_with_profile` is REPLACED by
  `test_acceptance_1_frontmatter_fixes_no_model`, which asserts the absence
  invariant INV-3/PD-1e: no installed agent of either runtime carries a
  `model:` line, for every role.

Black-box discipline: only public interfaces are used — the generator CLI
(`scripts/cdad-generate.py --runtime <r> --stack odoo --out`), install.sh
(`--basic`, `--basic --check`) and the OBSERVABLE deployed artifacts
(installed frontmatter, real destinations under CDAD_INSTALL_ROOT). The
generator/installer internals and sources/ composition are never read.

Behavioral probes recorded while building the original oracle (all logged
under /tmp/opencode/probe-matrix):
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

Test -> contract mapping (every test -> acceptance §4.1 of the 004-001 spec,
kept, plus the 006-003 U1 absence invariant):

- test_acceptance_1_all_cells_installed -> §4.1 (every cell of the
    runtime × 11-roles matrix exists at its real runtime destination after an
    isolated install)
- test_acceptance_1_frontmatter_fixes_no_model -> §4.1 as amended by
    006-003 PD-1e/INV-3 (no installed agent carries `model:` — replaces
    `..._coherent_with_profile`)
- test_acceptance_1_install_check_rc0 -> §4.1 (install.sh --check exits 0
    for the isolated install)
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
INSTALLER = REPO_ROOT / "install.sh"

# The 11 agents per runtime (T6 frozen role set + orchestrator; stack odoo
# produces base cells cdad-<role>.md and odoo cells cdad-<role>-odoo.md).
ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")
ROLE_NAMES = (
    ROLE_AGENTS
    + tuple(f"{role}-odoo" for role in ROLE_AGENTS)
    + ("orchestrator",)
)

RUNTIMES = ("opencode", "claude-code")

# D1: the only install flag that still runs is `--basic`, a deprecated alias
# with no effect on the deployed bytes (006-003 §2.1).
INSTALL_FLAG = "--basic"

# Real runtime destinations under the isolated install root (same frozen set
# T6 uses; orchestrator-confirmed):
AGENT_DESTINATIONS = {
    "opencode": ".config/opencode/agents",
    "claude-code": ".claude/agents",
}

# Product entries the public interfaces require next to install.sh.
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")

MODEL_LINE_RE = re.compile(r"^model:\s*(.*?)\s*$")


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


class TestAcceptanceMatrix(unittest.TestCase):
    """Fixture: product copy -> staging -> isolated install (no profiles).

    Everything happens under one temporary directory created by this fixture:
    a product copy (never the repo's build/) and a pre-created install root
    passed via CDAD_INSTALL_ROOT (never the real HOME).
    """

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
            ["bash", str(cls.product_copy / "install.sh"), INSTALL_FLAG],
            cwd=str(cls.product_copy),
            env=install_env,
            text=True,
            capture_output=True,
            check=False,
        )
        cls.check_result = subprocess.run(
            ["bash", str(cls.product_copy / "install.sh"), INSTALL_FLAG, "--check"],
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
                "el generador falló para runtime=%s (sin perfil, PD-1f):\n%s"
                % (
                    runtime,
                    tail(
                        self.generate_results[runtime].stderr
                        or self.generate_results[runtime].stdout
                    ),
                ),
            )
        self.assertEqual(
            self.install_result.returncode,
            0,
            "la instalación aislada falló (flag=%s):\n%s"
            % (
                INSTALL_FLAG,
                tail(self.install_result.stderr or self.install_result.stdout),
            ),
        )

    def agent_path(self, runtime: str, role: str) -> Path:
        destination = self.install_root / AGENT_DESTINATIONS[runtime]
        return destination / f"cdad-{role}.md"

    # --- tests (§4.1 of 004-001 as amended by 006-003 PD-1e/INV-3) ---------

    def test_acceptance_1_all_cells_installed(self) -> None:
        """§4.1: every runtime × 11-roles cell exists at its real destination."""
        self.assert_pipeline_succeeded()
        for runtime in RUNTIMES:
            for role in ROLE_NAMES:
                with self.subTest(runtime=runtime, rol=role):
                    cell = self.agent_path(runtime, role)
                    self.assertTrue(
                        cell.is_file(),
                        "celda de matriz ausente: runtime=%s rol=%s -> %s"
                        % (runtime, role, cell),
                    )

    def test_acceptance_1_frontmatter_fixes_no_model(self) -> None:
        """PD-1e/INV-3: no installed agent carries a `model:` line.

        ORACLE REPLACEMENT (006-003 U1): the former
        `..._coherent_with_profile` compared every installed cell against the
        model map executed from `scripts/cdad-models.sh`. The map is retired
        (PD-1c) and the generator has no profiles (PD-1f), so the new oracle
        asserts the stronger absence invariant: for BOTH runtimes and ALL 11
        roles the installed frontmatter has no `model:` at all.
        """
        self.assert_pipeline_succeeded()
        for runtime in RUNTIMES:
            for role in ROLE_NAMES:
                with self.subTest(runtime=runtime, rol=role):
                    cell = self.agent_path(runtime, role)
                    self.assertTrue(
                        cell.is_file(),
                        "celda de matriz ausente: runtime=%s rol=%s -> %s"
                        % (runtime, role, cell),
                    )
                    installed = frontmatter_model(cell.read_text(encoding="utf-8"))
                    self.assertIsNone(
                        installed,
                        "PD-1e/INV-3: el agente instalado %s/%s trae model: %r "
                        "y ningún texto instalable fija modelos"
                        % (runtime, cell.name, installed),
                    )

    def test_acceptance_1_install_check_rc0(self) -> None:
        """§4.1: install.sh --check exits 0 for the isolated install."""
        self.assert_pipeline_succeeded()
        self.assertEqual(
            self.check_result.returncode,
            0,
            "install.sh --check no está en rc=0:\n%s"
            % tail(self.check_result.stderr or self.check_result.stdout),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
