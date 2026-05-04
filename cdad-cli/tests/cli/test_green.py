"""Tests for `cdad green` command — PC-003-13 exit codes.

RED phase: tests verify exit codes per spec:
- Exit code 0: success=True (suite GREEN)
- Exit code 1: success=False by max_iterations_reached or test_obsolescence_suspected
- Exit code 2: configuration errors (missing spec, no state file, unresolved provider)

NOTE: These tests invoke the actual CLI command and verify it doesn't meet
the spec requirements. No mocking of internal functions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

runner = CliRunner()

# Try to import the CLI module
try:
    from cdad.cli import main as cli_main
except ImportError:
    cli_main = None


@pytest.fixture(autouse=True)
def mock_valid_provider(monkeypatch):
    """Mock resolve_provider to return a valid provider instead of a MagicMock."""
    if cli_main is None:
        return

    class DummyProvider:
        name = "dummy"

        def send_message(self, *args, **kwargs):
            return "ok"

    monkeypatch.setattr(cli_main, "resolve_provider", lambda *args, **kwargs: DummyProvider())


@pytest.fixture
def temp_project_with_spec(tmp_path):
    """Create a temporary CDAD project with a valid spec and cdad.toml config."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create directory structure
    (project_root / "docs" / "specs").mkdir(parents=True)
    (project_root / "tests").mkdir()
    (project_root / "src").mkdir()

    # Create a valid spec file
    spec_file = project_root / "docs" / "specs" / "feature.md"
    spec_file.write_text("""---
title: Test Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Test passes
**Description**: Basic test should pass
**Verification**: test
""")

    # Create pyproject.toml
    (project_root / "pyproject.toml").write_text("""[project]
name = "test-project"
version = "0.1.0"
""")

    # Create cdad.toml with default config (required for provider-aware CLI)
    (project_root / "cdad.toml").write_text("""[agents]
default = "anthropic/claude-opus-4-7"
""")

    return project_root


class TestGreenExitCode0:
    """Exit code 0: success=True (suite GREEN)."""

    def test_exit_code_0_when_suite_passes(self, temp_project_with_spec, monkeypatch):
        """PC-003-13: Exit code 0 cuando la suite pasa (GREEN)."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        # Create a passing test (GREEN suite)
        test_file = temp_project_with_spec / "tests" / "test_feature.py"
        test_file.write_text("def test_pass(): pass\n")

        result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0, which matches spec
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"
        )
        # Verify output indicates GREEN
        assert "GREEN" in result.output, f"Expected GREEN in output, got: {result.output}"
        # Verify it's using ImplementerAgent (should show iterations_used)
        assert "iterations" in result.output.lower() or "0 iterations" in result.output.lower(), (
            f"Should show iterations_used from ImplementResult. Got: {result.output}"
        )


class TestGreenExitCode1:
    """Exit code 1: success=False by max_iterations_reached or test_obsolescence_suspected."""

    def test_exit_code_1_when_max_iterations_reached(self, temp_project_with_spec, monkeypatch):
        """PC-003-13: Exit code 1 cuando max_iterations alcanzado."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        # Create a failing test
        test_file = temp_project_with_spec / "tests" / "test_feature.py"
        test_file.write_text("def test_fails(): assert False\n")

        result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0 (doesn't implement spec exit codes)
        # Should be 1 per spec
        assert result.exit_code == 1, (
            f"Expected exit code 1 for max_iterations_reached, got {result.exit_code}. Output: {result.output}"
        )

    def test_exit_code_1_when_test_obsolescence_suspected(
        self, temp_project_with_spec, monkeypatch
    ):
        """PC-003-13: Exit code 1 cuando se detecta obsolescencia."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        # Create test with obsolete reference (simulated)
        test_file = temp_project_with_spec / "tests" / "test_legacy.py"
        test_file.write_text("def test_pc_001_old(): pass\n")

        result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0 (doesn't implement spec exit codes)
        # Should be 1 per spec
        assert result.exit_code == 1, (
            f"Expected exit code 1 for test_obsolescence_suspected, got {result.exit_code}. Output: {result.output}"
        )


class TestGreenExitCode2:
    """Exit code 2: configuration errors (missing spec, no state file, unresolved provider)."""

    def test_exit_code_2_when_spec_not_found(self, temp_project_with_spec, monkeypatch):
        """PC-003-13: Exit code 2 cuando el spec no existe (with --spec flag)."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        non_existent_spec = temp_project_with_spec / "docs" / "specs" / "non_existent.md"

        result = runner.invoke(cli_main.app, ["green", "--spec", str(non_existent_spec)])

        # Current CLI doesn't accept --spec flag - Typer returns error
        # Should return 2 per spec for spec-not-found
        assert result.exit_code == 2, (
            f"Expected exit code 2 for spec-not-found, got {result.exit_code}. Output: {result.output}"
        )
        # Verify it's the expected error message, not CLI parsing error
        assert "no such option" not in result.output.lower(), (
            f"Got CLI parsing error instead of spec-not-found. Output: {result.output}"
        )

    def test_exit_code_2_when_no_active_feature_and_no_spec_flag(
        self, temp_project_with_spec, monkeypatch
    ):
        """PC-003-13: Exit code 2 cuando no hay --spec y .cdad-state.json no existe."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        # No --spec provided, no .cdad-state.json exists
        result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0 (ignores state file logic)
        # Should be 2 per spec
        assert result.exit_code == 2, (
            f"Expected exit code 2 when no spec or state file, got {result.exit_code}. Output: {result.output}"
        )
        # Verify it mentions missing configuration
        assert (
            "active feature" in result.output.lower()
            or "no active feature" in result.output.lower()
        ), f"Expected message about missing active feature, got: {result.output}"

    def test_exit_code_2_when_state_file_missing_active_feature(
        self, temp_project_with_spec, monkeypatch
    ):
        """PC-003-13: Exit code 2 cuando .cdad-state.json existe pero no tiene active_feature."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        # Create state file without active_feature
        state_file = temp_project_with_spec / "docs" / ".cdad-state.json"
        state_file.write_text(json.dumps({"other_field": "value"}))

        result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0 (doesn't check state file)
        # Should be 2 per spec
        assert result.exit_code == 2, (
            f"Expected exit code 2 when state file missing active_feature, got {result.exit_code}. Output: {result.output}"
        )

    def test_exit_code_2_when_provider_unresolvable(self, temp_project_with_spec, monkeypatch):
        """PC-003-13: Exit code 2 cuando provider no se puede resolver."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        from unittest.mock import patch

        from cdad.llm.registry import ConfigurationError

        monkeypatch.chdir(temp_project_with_spec)

        test_file = temp_project_with_spec / "tests" / "test_feature.py"
        test_file.write_text("def test_pass(): pass\n")

        # Mock resolve_provider to raise ConfigurationError (provider unresolvable)
        with patch.object(cli_main, "resolve_provider") as mock_resolve:
            mock_resolve.side_effect = ConfigurationError("Provider not found")

            result = runner.invoke(cli_main.app, ["green"])

        # Current CLI returns 0 (doesn't handle provider errors)
        # Should be 2 per spec for provider error
        assert result.exit_code == 2, (
            f"Expected exit code 2 for provider error, got {result.exit_code}. Output: {result.output}"
        )


class TestGreenOutput:
    """Output printed to stdout."""

    def test_implement_result_printed_to_stdout(self, temp_project_with_spec, monkeypatch):
        """PC-003-13: El comando imprime ImplementResult a stdout."""
        if cli_main is None:
            pytest.skip("CLI module not available")

        monkeypatch.chdir(temp_project_with_spec)

        test_file = temp_project_with_spec / "tests" / "test_feature.py"
        test_file.write_text("def test_pass(): pass\n")

        result = runner.invoke(cli_main.app, ["green"])

        assert len(result.output) > 0, "Expected output to stdout"
        # Current CLI prints test results, not ImplementResult details
        # Should include: success, iterations_used, files_modified, error
        # Test that ALL ImplementResult fields are in the output
        assert "success" in result.output.lower(), (
            f"Missing 'success' in output. Got: {result.output}"
        )
        assert "iterations" in result.output.lower(), (
            f"Missing 'iterations' in output. Got: {result.output}"
        )
        assert "files_modified" in result.output.lower() or "modified" in result.output.lower(), (
            f"Missing files_modified info in output. Got: {result.output}"
        )
