#!/usr/bin/env python3
"""Black-box RED tests for 003-001 Task 3 (consumer and install parity)."""

from __future__ import annotations

import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.test_role_packet_render import PacketFixture
from tests.test_role_packets import INSTALLER, PACKET_CLI, REPO_ROOT
from tests.product_staging import product_root


ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")


def frontmatter(text: str) -> str:
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("installed agent does not have delimited frontmatter")
    return parts[1]


class InstalledFixture(unittest.TestCase):
    """Install once under an explicit temporary root; never alter HOME."""

    @classmethod
    def setUpClass(cls) -> None:
        # Portabilidad (review-t1/T6): staging garantizado (checkout real o
        # copia temporal generada); nunca se escribe en el checkout real.
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-t3-install-")
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
        cls.installed_cli = (
            cls.install_root
            / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py"
        )
        cls.installed_agents = cls.install_root / ".config/opencode/agents"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def assert_install_succeeded(self) -> None:
        self.assertEqual(
            self.install_result.returncode,
            0,
            self.install_result.stderr or self.install_result.stdout,
        )


class TestInstalledConsumerEntrypoint(InstalledFixture):
    def test_p6_installs_documented_consumer_entrypoint(self) -> None:
        """P6: the exact approved installed path is part of the public contract."""
        self.assert_install_succeeded()
        self.assertTrue(
            self.installed_cli.is_file(),
            f"installer omitted documented entrypoint {self.installed_cli}",
        )

    def test_p6_installed_cli_from_consumer_matches_source_bytes_and_results(self) -> None:
        """P6: a project without the repo wrapper gets byte/result parity."""
        self.assert_install_succeeded()
        self.assertTrue(
            self.installed_cli.is_file(),
            f"installer omitted documented entrypoint {self.installed_cli}",
        )
        with tempfile.TemporaryDirectory(prefix="cdad-t3-consumer-") as project_dir:
            consumer = Path(project_dir)
            self.assertFalse(
                (consumer / "scripts/cdad_packet.py").exists(),
                "consumer fixture unexpectedly contains the repository wrapper",
            )
            fixture = PacketFixture(consumer, "test-writer", "red")
            fixture.write()
            common_args = [
                "render",
                "--project-root",
                str(consumer),
                "--execution-context",
                str(consumer / "EXECUTION.json"),
                "--request",
                str(fixture.request_path),
            ]
            source = subprocess.run(
                [sys.executable, str(PACKET_CLI), *common_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            installed = subprocess.run(
                [sys.executable, str(self.installed_cli), *common_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            self.assertEqual(source.returncode, 0, source.stderr.decode())
            self.assertTrue(source.stdout.startswith(b"---cdad-packet-json\n"))
            self.assertEqual(installed.returncode, source.returncode)
            self.assertEqual(installed.stdout, source.stdout)
            self.assertEqual(installed.stderr, source.stderr)

            packet = consumer / "PACKET.md"
            packet.write_bytes(source.stdout)
            validate_args = [
                "validate-packet",
                "--project-root",
                str(consumer),
                "--execution-context",
                str(consumer / "EXECUTION.json"),
                "--request",
                str(fixture.request_path),
                "--packet",
                str(packet),
            ]
            source_validation = subprocess.run(
                [sys.executable, str(PACKET_CLI), *validate_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            installed_validation = subprocess.run(
                [sys.executable, str(self.installed_cli), *validate_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            self.assertEqual(source_validation.returncode, 0, source_validation.stderr.decode())
            self.assertEqual(installed_validation.returncode, source_validation.returncode)
            self.assertEqual(installed_validation.stdout, source_validation.stdout)
            self.assertEqual(installed_validation.stderr, source_validation.stderr)

            invalid_request = fixture.request.copy()
            invalid_request["execution_id"] = "wrong-execution"
            fixture.request_path.write_text(json.dumps(invalid_request), encoding="utf-8")
            invalid_source = subprocess.run(
                [sys.executable, str(PACKET_CLI), *common_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            invalid_installed = subprocess.run(
                [sys.executable, str(self.installed_cli), *common_args],
                cwd=consumer,
                text=False,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(invalid_source.returncode, 0)
            self.assertEqual(invalid_source.stdout, b"")
            self.assertTrue(invalid_source.stderr)
            self.assertEqual(invalid_installed.returncode, invalid_source.returncode)
            self.assertEqual(invalid_installed.stdout, invalid_source.stdout)
            self.assertEqual(invalid_installed.stderr, invalid_source.stderr)

    def test_p3_p6_base_consumers_use_rendered_packet_without_cycle_reload(self) -> None:
        """P3/P6: Task and chat receive render stdout unchanged as their prompt."""
        self.assert_install_succeeded()
        consumers = (
            self.installed_agents / "cdad-orchestrator.md",
            self.install_root
            / ".config/opencode/skills/cdad-cycle/references/handoff-prompts.md",
        )
        for consumer in consumers:
            with self.subTest(consumer=consumer.name):
                text = consumer.read_text(encoding="utf-8")
                self.assertIn("cdad_packet.py", text)
                self.assertRegex(text, r"(?i)render")
                self.assertRegex(text, r"(?is)stdout.{0,160}(unchanged|sin cambios|byte)")
                self.assertNotRegex(
                    text,
                    r"(?i)(busca|search for).{0,40}(y lee|and read).{0,80}cdad-cycle/SKILL\.md",
                )

    def test_p3_critical_opencode_permissions_survive_consumer_migration(self) -> None:
        """P3: migration preserves task classification and role edit barriers."""
        self.assert_install_succeeded()
        installed = {
            role: frontmatter(
                (self.installed_agents / f"cdad-{role}.md").read_text(encoding="utf-8")
            )
            for role in ROLE_AGENTS
        }
        for role, metadata in installed.items():
            with self.subTest(role=role, invariant="task-able"):
                self.assertRegex(metadata, r"(?m)^\s{2}write:\s*ask\s*$")
        for role in ("architect", "reviewer", "scribe"):
            with self.subTest(role=role, invariant="read-only"):
                self.assertRegex(installed[role], r"(?m)^\s{2}edit:\s*deny\s*$")
        self.assertRegex(installed["test-writer"], r'(?m)^\s{4}"src/\*\*":\s*deny\s*$')
        self.assertRegex(installed["test-writer"], r'(?m)^\s{4}"tests/\*\*":\s*allow\s*$')
        self.assertRegex(installed["implementer"], r'(?m)^\s{4}"tests/\*\*":\s*deny\s*$')


class TestPythonDependencyIsPublic(unittest.TestCase):
    def test_p6_readme_and_installer_help_publish_python3_dependency(self) -> None:
        """P6: consumers can discover the stdlib-only Python requirement."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        help_result = subprocess.run(
            ["bash", str(INSTALLER), "--help"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        for surface, text in (("README", readme), ("install --help", help_result.stdout)):
            with self.subTest(surface=surface):
                self.assertRegex(text, r"(?i)Python\s*3")
                self.assertRegex(text, r"(?i)(standard library|stdlib|sin dependencias de terceros)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
