#!/usr/bin/env python3
"""T6 RED contract tests for 004-001 (Aterrizaje B: coherencia Claude Code).

Packet: 004-001-canonical-runtime-artifacts-test-writer-red-006 (substage red).
Contract: docs/specs/004-001-canonical-runtime-artifacts/spec.md (approved
2026-09-24) + plan.md row T6.

ORACLE FREEZE (review-6): the semantics below are the complete approved
definition for this package. Any later adjustment of these oracles requires
reviewer sign-off.

Mapping (every test -> contract item; behavior-level, black-box; the suite
never reads implementation code, install.sh, sources/ or the guard itself):

- test_pd9_default_install_deploys_only_real_runtime_destinations  -> PD-9
    (default install lands ONLY at real runtime destinations; the public
    layout install.sh:34-35,605,627-628 is not installed by default)
- test_pd9_real_runtime_destinations_are_installed_for_both_runtimes -> PD-9
    (frozen positive direction: the real destination set per runtime)
- test_pd9_opencode_cli_entrypoint_lives_at_real_destination        -> PD-9/D6
    (frozen anchor for the test_role_packet_consumers.py:46 fixture migration)
- test_pd14_installed_cc_and_opencode_agents_are_runtime_coherent    -> PD-14
    (same roles in both runtimes; CC copy is not a byte clone of the OpenCode
    copy; CC copy mentions no OpenCode design model)
- test_pd15_installed_cc_agents_make_no_unbacked_sandbox_promises    -> PD-15
    (same honesty oracle as the generator level, applied to the installed CC
    artifacts)
- test_pd16_installed_cc_task_agents_keep_packet_and_legacy_contract -> PD-16
    (installed CC Task agents keep the complete packet/legacy dual-path
    contract, including the R3-corrected legacy loads)
- test_t6_cc_path_guard_is_installed_and_coherent_with_cc_contract   -> T6 item 1
    (staging-driven install deploys .claude/cdad-scripts/path-guard.sh and the
    installed CC agents reference exactly that destination; the guard itself is
    only ever invoked black-box, never read)
- test_t6_smoke_matrix_base_and_odoo_cells_for_both_runtimes         -> T6 item 3
    (acceptance §4.1 matrix cells installed from the isolated install)
- test_t6_smoke_render_from_install_without_checkout                 -> T6 item 3
    (from-install render of synthetic data without the repo in the execution
    path, for both runtime CLIs)

T6 item 4 (PD-9 flag decision) is NOT a test: the consumption evidence that the
reviewer needs is recorded in the role report of the dispatching session.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.test_install_review5_regressions import find_deployed
from tests.test_role_packet_render import PacketFixture
from tests.test_role_packet_review_regressions import packet_and_legacy_contract_errors
from tests.test_role_packets import INSTALLER, PACKET_CLI, REPO_ROOT
from tests.product_staging import product_root

# Same role set the existing suite freezes for Task agents (003-001 §2).
ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")

# Real runtime destinations under an isolated install root (orchestrator-confirmed):
#   Claude Code:  .claude/agents/, .claude/skills/, .claude/cdad-scripts/path-guard.sh
#   OpenCode:     .config/opencode/agents|skills + ~agents|skills (root .agents/skills)
REQUIRED_REAL_DESTINATIONS = (
    ".config/opencode/agents",
    ".config/opencode/skills/cdad-cycle",
    ".agents/skills",
    ".claude/agents",
    ".claude/skills/cdad-cycle",
    ".claude/cdad-scripts",
)

# Legacy/public layout paths that PD-9 forbids installing by default.
PUBLIC_LAYOUT_ENTRIES = (
    "agents",
    "skills",
)

# PD-14 single source for OpenCode design models: scripts/cdad-models.sh
# (cdad_model). Values frozen from tests/test_cdad_generate.py — the tests are
# the declared consumers of the model map, never the implementation.
#
# 006-003 U1 (PD-1c/PD-1e/INV-3) — DECLARED REPLACEMENT of the oracle, asserts
# untouched: the model map `scripts/cdad-models.sh` is RETIRED and no installed
# agent carries a `model:` line any more, so this frozen tuple stops being "the
# values the map produces" and becomes a NEGATIVE oracle (these names must not
# appear in a Claude Code artifact). The `assertNotIn` direction of this test
# is unchanged and still holds; only its justification is restated here.
OC_DESIGN_MODELS = (
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "glm-5.2",
    "qwen3.7-plus",
    "qwen3.7-max",
    "minimax-m3",
)

# PD-15: negation cues that turn a 'sandbox' mention into an honest limitation;
# the Odoo environment skill legitimately carries 'sandbox' in its NAME.
SANDBOX_NEGATION_RE = re.compile(r"\b(no|not|never|sin|não)\b")
SANDBOX_SKILL_NAME = "odoo-sandbox-env"


class T6InstalledFixture(unittest.TestCase):
    """One staging-driven install under an explicit temporary root; never HOME."""

    @classmethod
    def setUpClass(cls) -> None:
        # Portabilidad (review-t1/T6): staging garantizado (checkout real o
        # copia temporal generada); nunca se escribe en el checkout real.
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-t6-install-")
        cls.install_root = Path(cls._install_tmp.name).resolve()
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        cls.install_result = subprocess.run(
            ["bash", str(cls.install_product / "install.sh"), "--basic"],
            cwd=cls.install_product,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def assert_install_succeeded(self) -> None:
        self.assertEqual(
            self.install_result.returncode,
            0,
            self.install_result.stderr or self.install_result.stdout,
        )


class TestPD9RealDestinationsOnly(T6InstalledFixture):
    """PD-9: default install lands only at real runtime destinations."""

    def test_pd9_default_install_deploys_only_real_runtime_destinations(self) -> None:
        """PD-9: the public layout must NOT be installed by default (RED first)."""
        self.assert_install_succeeded()
        for entry in PUBLIC_LAYOUT_ENTRIES:
            legacy_path = self.install_root / entry
            with self.subTest(public_layout=entry):
                self.assertFalse(
                    legacy_path.exists(),
                    f"default install deployed public-layout path {legacy_path}; "
                    "PD-9: installation must land only at real runtime destinations "
                    "and the public layout must not be installed by default",
                )

    def test_pd9_real_runtime_destinations_are_installed_for_both_runtimes(self) -> None:
        """PD-9 (frozen positive direction): each real destination per runtime."""
        self.assert_install_succeeded()
        for required in REQUIRED_REAL_DESTINATIONS:
            destination = self.install_root / required
            with self.subTest(destination=required):
                self.assertTrue(
                    destination.is_dir(),
                    f"default install omitted real runtime destination {required}",
                )

    def test_pd9_opencode_cli_entrypoint_lives_at_real_destination(self) -> None:
        """PD-9/D6 (frozen): the consumer entrypoint lives at the real destination.

        Freezes the migrated fixture of tests/test_role_packet_consumers.py:46:
        the installed CLI is consumed from
        .config/opencode/skills/cdad-cycle/scripts/cdad_packet.py, never from the
        legacy public-layout path.
        """
        self.assert_install_succeeded()
        real_cli = (
            self.install_root
            / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py"
        )
        self.assertTrue(
            real_cli.is_file(),
            f"installer omitted the documented consumer entrypoint {real_cli}",
        )


class TestPD14RuntimeCoherence(T6InstalledFixture):
    """PD-14: semantic coherence of the CC copy against the same contract."""

    def test_pd14_installed_cc_and_opencode_agents_are_runtime_coherent(self) -> None:
        """PD-14: same roles in both runtimes; CC copy is adapted, not cloned.

        The byte-for-byte §2 equality stops being a requirement: the CC copy
        must exist for every frozen role, differ in bytes from the OpenCode copy
        (runtime adaptation) and mention no OpenCode design model.
        """
        self.assert_install_succeeded()
        role_names = ROLE_AGENTS + ("orchestrator",)
        for role in role_names:
            with self.subTest(role=role):
                cc_agent = self.install_root / ".claude/agents" / f"cdad-{role}.md"
                oc_agent = (
                    self.install_root / ".config/opencode/agents" / f"cdad-{role}.md"
                )
                self.assertTrue(
                    cc_agent.is_file(),
                    f"CC install omitted role {role}: {cc_agent}",
                )
                self.assertTrue(
                    oc_agent.is_file(),
                    f"OpenCode install omitted role {role}: {oc_agent}",
                )
                cc_text = cc_agent.read_text(encoding="utf-8")
                self.assertNotEqual(
                    cc_agent.read_bytes(),
                    oc_agent.read_bytes(),
                    f"CC copy of {role} is a byte clone of the OpenCode copy; "
                    "PD-14 requires runtime coherence, not byte equality",
                )
                for model in OC_DESIGN_MODELS:
                    self.assertNotIn(
                        model,
                        cc_text,
                        f"PD-14: installed CC agent {cc_agent.name} mentions "
                        f"OpenCode design model {model}, which cdad_model_claude "
                        "does not produce",
                    )


class TestPD15Honesty(T6InstalledFixture):
    """PD-15: installed CC artifacts make no unbacked sandbox promises."""

    def test_pd15_installed_cc_agents_make_no_unbacked_sandbox_promises(self) -> None:
        """PD-15: same honesty oracle as generator level, on the installed bytes."""
        self.assert_install_succeeded()
        cc_agents = sorted((self.install_root / ".claude/agents").glob("cdad-*.md"))
        self.assertTrue(cc_agents, "CC install deployed no agents to check for PD-15")
        for agent_path in cc_agents:
            with self.subTest(agent=agent_path.name):
                for line in agent_path.read_text(encoding="utf-8").splitlines():
                    stripped = line.replace(SANDBOX_SKILL_NAME, "")
                    if "sandbox" not in stripped.lower():
                        continue
                    self.assertRegex(
                        stripped,
                        SANDBOX_NEGATION_RE,
                        f"PD-15: {agent_path.name} mentions 'sandbox' without an "
                        f"honest-limitation negation: {stripped!r}",
                    )


class TestPD16LegacyPath(T6InstalledFixture):
    """PD-16: the installed CC Task agents keep the complete packet/legacy contract."""

    def test_pd16_installed_cc_task_agents_keep_packet_and_legacy_contract(self) -> None:
        """PD-16: every installed CC Task agent branches packet/legacy correctly.

        Reuses the frozen semantic oracle of the 003-001 review regressions:
        packet_and_legacy_contract_errors() must be empty, which encodes the
        valid-packet branch (no cdad-cycle reload) AND the legacy branch
        (cdad-cycle load retained), including the R3-corrected intake loads.
        """
        self.assert_install_succeeded()
        cc_agents = self.install_root / ".claude/agents"
        for role in ROLE_AGENTS:
            with self.subTest(role=role):
                agent_text = (cc_agents / f"cdad-{role}.md").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(
                    packet_and_legacy_contract_errors(agent_text),
                    [],
                    f"PD-16: installed CC agent cdad-{role}.md lost a packet/legacy "
                    "contract branch",
                )


class TestT6PathGuard(T6InstalledFixture):
    """T6 item 1: CC path-guard deployed from staging, coherent with the CC contract.

    The guard implementation is never read; it is only observed as a deployed
    artifact and referenced destination of the installed CC agents.
    """

    def test_t6_cc_path_guard_is_installed_and_coherent_with_cc_contract(self) -> None:
        """T6: staging-driven install deploys the guard; CC agents reference it."""
        self.assert_install_succeeded()
        guard = find_deployed(self.install_root, "path-guard.sh")
        self.assertEqual(
            guard.name,
            "path-guard.sh",
            f"staging-driven install deployed no path-guard.sh under {self.install_root}",
        )
        self.assertTrue(
            os.access(guard, os.X_OK),
            f"installed CC path-guard is not executable: {guard}",
        )
        cc_agents = sorted((self.install_root / ".claude/agents").glob("cdad-*.md"))
        referencing = []
        for agent_path in cc_agents:
            text = agent_path.read_text(encoding="utf-8")
            if "path-guard.sh" in text:
                referencing.append(agent_path)
                with self.subTest(agent=agent_path.name):
                    self.assertRegex(
                        text,
                        r"(?m)\.claude/cdad-scripts/path-guard\.sh",
                        f"{agent_path.name} references a path-guard destination that "
                        "is not the documented one (.claude/cdad-scripts/path-guard.sh)",
                    )
        self.assertTrue(
            referencing,
            "no installed CC agent references the path-guard; the CC agent/contract "
            "coherence (T6/PD-16) requires at least one reference",
        )


class TestT6SmokeMatrix(T6InstalledFixture):
    """T6 item 3: smoke matrix base/odoo × runtimes from the isolated install."""

    def test_t6_smoke_matrix_base_and_odoo_cells_for_both_runtimes(self) -> None:
        """T6: every base/odoo × runtime cell is installed, no provider needed.

        Frozen layout (orchestrator-confirmed real destinations): the odoo stack
        cells are the odoo-specialized agents cdad-{role}-odoo.md deployed in
        each runtime's agents destination; base cells are cdad-{role}.md.
        """
        self.assert_install_succeeded()
        for runtime_agents_dir in (
            self.install_root / ".config/opencode/agents",
            self.install_root / ".claude/agents",
        ):
            runtime = (
                "opencode"
                if ".config/opencode" in runtime_agents_dir.parts
                else "claude-code"
            )
            for role in ROLE_AGENTS:
                for stack, expected_name in (
                    ("base", f"cdad-{role}.md"),
                    ("odoo", f"cdad-{role}-odoo.md"),
                ):
                    cell = runtime_agents_dir / expected_name
                    with self.subTest(
                        runtime=runtime, role=role, stack=stack, cell=cell.name
                    ):
                        self.assertTrue(
                            cell.is_file(),
                            f"smoke matrix cell missing: runtime={runtime} "
                            f"stack={stack} role={role} -> {cell}",
                        )

    def test_t6_smoke_render_from_install_without_checkout(self) -> None:
        """T6: from the install alone, both runtime CLIs render synthetic data.

        A consumer project without the repository renders a synthetic packet
        through EACH runtime's installed CLI; the installed result must equal
        the repository CLI result byte for byte, proving the checkout is not
        part of the execution path (PD-11/12 groundwork for T7).
        """
        self.assert_install_succeeded()
        installed_clis = (
            self.install_root
            / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py",
            self.install_root / ".claude/skills/cdad-cycle/scripts/cdad_packet.py",
        )
        for installed_cli in installed_clis:
            with self.subTest(cli=str(installed_cli.relative_to(self.install_root))):
                self.assertTrue(
                    installed_cli.is_file(),
                    f"installer omitted installed CLI {installed_cli}",
                )
                with tempfile.TemporaryDirectory(
                    prefix="cdad-t6-consumer-"
                ) as project_dir:
                    consumer = Path(project_dir)
                    fixture = PacketFixture(consumer, "test-writer", "red")
                    fixture.write()
                    args = [
                        "render",
                        "--project-root",
                        str(consumer),
                        "--execution-context",
                        str(consumer / "EXECUTION.json"),
                        "--request",
                        str(fixture.request_path),
                    ]
                    env = os.environ.copy()
                    env.pop("PYTHONPATH", None)
                    installed = subprocess.run(
                        [sys.executable, str(installed_cli), *args],
                        cwd=consumer,
                        env=env,
                        capture_output=True,
                        check=False,
                    )
                    source = subprocess.run(
                        [sys.executable, str(PACKET_CLI), *args],
                        cwd=consumer,
                        env=env,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(
                        source.returncode,
                        0,
                        source.stderr.decode(errors="replace"),
                    )
                    self.assertTrue(
                        source.stdout.startswith(b"---cdad-packet-json\n"),
                        "repo CLI did not render the synthetic packet",
                    )
                    self.assertEqual(
                        installed.returncode,
                        source.returncode,
                        installed.stderr.decode(errors="replace"),
                    )
                    self.assertEqual(
                        installed.stdout,
                        source.stdout,
                        f"installed CLI {installed_cli.name} diverged from the repo "
                        "CLI on synthetic data (install without checkout broken)",
                    )
                    self.assertEqual(installed.stderr, source.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
