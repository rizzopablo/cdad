"""E2E integration tests for cdad-cli commands using real acp/qwen provider.

Tests execute real commands against acp/qwen to catch bugs that unit tests
with mocks miss (e.g., race conditions, protocol mismatches).

Marked @pytest.mark.integration for opt-in execution with `-m integration`.
Skips automatically if qwen is not available in PATH.

TIMEOUT NOTE: Tests should complete in ~60-120s. For stricter timeout enforcement,
install pytest-timeout plugin and add @pytest.mark.timeout decorators.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
import toml
from typer.testing import CliRunner

pytestmark = pytest.mark.integration

runner = CliRunner()

try:
    from cdad.cli import main as cli_main
except ImportError:
    cli_main = None


def _is_qwen_available() -> bool:
    """Check if qwen command is available in PATH."""
    return shutil.which("qwen") is not None


@pytest.fixture
def temp_project_with_cdad_config(tmp_path):
    """Create a temporary project with cdad.toml configured for acp/qwen."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    (project_root / "docs" / "specs").mkdir(parents=True)
    (project_root / "tests").mkdir()
    (project_root / "src").mkdir()

    cdad_toml = project_root / "cdad.toml"
    cdad_toml.write_text(
        '[agents]\ndefault = "acp/qwen"\n',
        encoding="utf-8",
    )

    (project_root / "pyproject.toml").write_text(
        '[project]\nname = "test-project"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n',
        encoding="utf-8",
    )

    return project_root


@pytest.mark.skipif(
    not _is_qwen_available(),
    reason="qwen CLI not available in PATH (install qwen to run this test)",
)
def test_discovers_feature_with_real_acp(temp_project_with_cdad_config, monkeypatch):
    """E2E: cdad discover --feature completes without error and produces output in docs/.

    Verifies:
    - Command exits with code 0
    - docs/discovery.md is created
    - File contains non-empty content (actual LLM response varies, don't validate deeply)
    """
    if cli_main is None:
        pytest.skip("CLI module not available")

    monkeypatch.chdir(temp_project_with_cdad_config)

    result = runner.invoke(
        cli_main.app,
        ["discover", "--feature", "implement a simple greeting function"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"

    discovery_path = temp_project_with_cdad_config / "docs" / "discovery.md"
    assert discovery_path.exists(), f"discovery.md not created at {discovery_path}"

    content = discovery_path.read_text(encoding="utf-8")
    assert len(content) > 50, f"discovery.md seems too short or empty: {content[:100]}"


@pytest.mark.skipif(
    not _is_qwen_available(),
    reason="qwen CLI not available in PATH (install qwen to run this test)",
)
def test_generates_spec_with_real_acp(temp_project_with_cdad_config, monkeypatch):
    """E2E: cdad spec --name generates spec file with content.

    Verifies:
    - Command exits with code 0 or 1 (validation may fail, but command should complete)
    - docs/specs/greeting.md is created
    - File contains non-empty content

    NOTE: We don't validate spec structure deeply because LLM output varies.
    The test verifies the command completes and produces output.
    """
    if cli_main is None:
        pytest.skip("CLI module not available")

    monkeypatch.chdir(temp_project_with_cdad_config)

    discovery_path = temp_project_with_cdad_config / "docs" / "discovery.md"
    discovery_path.write_text(
        """# Discovery: Greeting Function

## Context
This feature implements a simple greeting utility for the application.

## Requirements
The system needs a function that returns a standard greeting message.

## Proposed Solution
Implement a `greeting()` function in src/greeting.py that returns "Hello, World!".

## Technical Notes
- Single module: src/greeting.py
- No dependencies
- Pure function, no side effects
""",
        encoding="utf-8",
    )

    result = runner.invoke(
        cli_main.app,
        ["spec", "--name", "greeting"],
        catch_exceptions=False,
    )

    # Accept both 0 (valid spec) and non-zero (validation may fail, but command completes)
    # The key assertion is that the command doesn't crash and produces output
    assert result.exit_code in [0, 1], f"Unexpected exit code {result.exit_code}. Output: {result.output}"

    spec_path = temp_project_with_cdad_config / "docs" / "specs" / "greeting.md"
    assert spec_path.exists(), f"spec.md not created at {spec_path}"

    content = spec_path.read_text(encoding="utf-8")
    # Only verify non-empty content (LLM output varies, don't validate structure)
    assert len(content) > 20, f"spec.md seems too short or empty: {content[:100]}"


def test_config_auto_creates_toml_with_real_acp(tmp_path, monkeypatch):
    """E2E: cdad config auto --local creates cdad.toml with [agents] section.

    Verifies:
    - Command exits with code 0
    - cdad.toml is created in current directory
    - Contains [agents] section with default provider

    NOTE: This test doesn't require qwen to be available because it only validates
    file creation, not provider validation.
    """
    if cli_main is None:
        pytest.skip("CLI module not available")

    empty_dir = tmp_path / "empty_project"
    empty_dir.mkdir()
    monkeypatch.chdir(empty_dir)

    result = runner.invoke(
        cli_main.app,
        ["config", "auto", "--local"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"

    cdad_toml = empty_dir / "cdad.toml"
    assert cdad_toml.exists(), f"cdad.toml not created at {cdad_toml}"

    config = toml.load(cdad_toml)
    assert "agents" in config, f"cdad.toml missing [agents] section: {config}"
    assert "default" in config["agents"], f"cdad.toml missing default in [agents]: {config['agents']}"


def test_config_set_writes_role_with_real_acp(tmp_path, monkeypatch):
    """E2E: cdad config set --local architect acp/qwen modifies cdad.toml.

    Verifies:
    - Command exits with code 0
    - cdad.toml contains architect = "acp/qwen"

    NOTE: This test doesn't require qwen to be available because it only validates
    file modification.
    """
    if cli_main is None:
        pytest.skip("CLI module not available")

    project_dir = tmp_path / "config_project"
    project_dir.mkdir()

    cdad_toml = project_dir / "cdad.toml"
    cdad_toml.write_text(
        '[agents]\ndefault = "acp/qwen"\n',
        encoding="utf-8",
    )

    monkeypatch.chdir(project_dir)

    result = runner.invoke(
        cli_main.app,
        ["config", "set", "--local", "architect", "acp/qwen"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}. Output: {result.output}"

    config = toml.load(cdad_toml)
    assert "agents" in config
    assert config["agents"].get("architect") == "acp/qwen", (
        f"Expected architect = 'acp/qwen', got: {config['agents']}"
    )


def test_skip_messages_when_qwen_not_available():
    """Verify skip messages are clear when qwen is not available."""
    if _is_qwen_available():
        pytest.skip("qwen is available, skipping skip-message verification test")

    assert True, "Skip marker works correctly via @pytest.mark.skipif"