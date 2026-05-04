"""Tests for cdad CLI commands."""

import os
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from cdad.cli import main as cli_main
from cdad.llm.client import LLMClient


runner = CliRunner()


@pytest.fixture
def patched_llm(monkeypatch):
    """Replace resolve_provider to return mock provider for LLMClient."""
    fake_provider = MagicMock()
    fake_provider._model_id = "claude-opus-4-7"
    fake_provider.send_message.return_value = "stubbed LLM output"
    fake_provider.name = "anthropic"

    # Mock LLMClient to use our fake provider
    fake_client = MagicMock(spec=LLMClient)
    fake_client.send_message.return_value = "stubbed LLM output"

    # Patch resolve_provider to return fake provider
    monkeypatch.setattr(
        cli_main,
        "resolve_provider",
        lambda name, config=None, override=None: fake_provider,
    )
    monkeypatch.setattr(cli_main, "LLMClient", lambda **kw: fake_client)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    return fake_client


@pytest.fixture
def no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


class TestInit:
    def test_init_creates_structure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(cli_main.app, ["init", "--name", "demo"])
        assert result.exit_code == 0, result.output
        proj = tmp_path / "demo"
        assert (proj / "docs" / "specs").is_dir()
        assert (proj / "docs" / "architecture").is_dir()
        assert (proj / "tests").is_dir()
        assert (proj / "src").is_dir()
        assert (proj / "pyproject.toml").exists()
        assert (proj / "AGENTS.md").exists()
        assert "Initialized CDAD project" in result.output

    def test_init_does_not_overwrite_pyproject(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        proj = tmp_path / "demo"
        proj.mkdir()
        (proj / "pyproject.toml").write_text('[project]\nname = "preserved"\n')
        runner.invoke(cli_main.app, ["init", "--name", "demo"])
        assert "preserved" in (proj / "pyproject.toml").read_text()


class TestStatus:
    def test_status_on_non_project(self, tmp_path):
        result = runner.invoke(cli_main.app, ["status", "--path", str(tmp_path / "missing")])
        assert "Not a CDAD project" in result.output

    def test_status_reports_phase(self, temp_generic_project):
        result = runner.invoke(cli_main.app, ["status", "--path", str(temp_generic_project)])
        assert result.exit_code == 0
        assert "Phase:" in result.output


class TestArchitectCommand:
    def test_missing_target(self, temp_generic_project, patched_llm):
        result = runner.invoke(
            cli_main.app,
            ["architect", str(temp_generic_project / "nope"), "--path", str(temp_generic_project)],
        )
        assert "not found" in result.output.lower()

    def test_writes_recommendations(self, temp_generic_project, patched_llm):
        target = temp_generic_project / "src" / "foo.py"
        target.write_text("def foo(): return 1\n")
        result = runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(temp_generic_project)],
        )
        assert result.exit_code == 0, result.output
        out_dir = temp_generic_project / "docs" / "architecture"
        files = list(out_dir.glob("*.md"))
        assert files, "expected architecture file"
        body = files[0].read_text()
        assert "## Analysis" in body
        assert "## Recommendations" in body

    def test_requires_api_key(self, tmp_path, no_api_key):
        """Without cdad.toml, command aborts with exit code 2 and config help message."""
        # Create a project WITHOUT cdad.toml to test PC-004-06
        project = tmp_path / "no_config_project"
        project.mkdir()
        (project / "docs" / "specs").mkdir(parents=True)
        (project / "tests").mkdir(exist_ok=True)
        (project / "src").mkdir(exist_ok=True)
        (project / "pyproject.toml").write_text('[project]\nname = "test-project"\n')

        target = project / "src"
        target.mkdir(exist_ok=True)
        (target / "foo.py").write_text("x = 1\n")

        result = runner.invoke(
            cli_main.app,
            ["architect", str(target), "--path", str(project)],
        )
        # PC-004-06: Without config file, exit code 2 with config help
        assert result.exit_code == 2, (
            f"Expected exit code 2 without config, got {result.exit_code}. Output: {result.output}"
        )
        assert "cdad config auto" in result.output, (
            f"Expected 'cdad config auto' in output, got: {result.output}"
        )
        assert "cdad config set" in result.output, (
            f"Expected 'cdad config set' in output, got: {result.output}"
        )


class TestTestCommand:
    def test_missing_spec(self, temp_generic_project, patched_llm):
        result = runner.invoke(
            cli_main.app,
            ["test", "missing", "--path", str(temp_generic_project)],
        )
        assert "Spec not found" in result.output

    def test_generates_test_file(self, temp_spec_project, patched_llm):
        patched_llm.send_message.return_value = "def test_login():\n    assert False\n"
        result = runner.invoke(
            cli_main.app,
            ["test", "feature", "--path", str(temp_spec_project)],
        )
        assert result.exit_code == 0, result.output
        out = temp_spec_project / "tests" / "test_feature.py"
        assert out.exists()
        assert "def test_login" in out.read_text()

    def test_refuses_overwrite_without_force(self, temp_spec_project, patched_llm):
        out = temp_spec_project / "tests" / "test_feature.py"
        out.write_text("# existing\n")
        result = runner.invoke(
            cli_main.app,
            ["test", "feature", "--path", str(temp_spec_project)],
        )
        assert "already exists" in result.output
        assert out.read_text() == "# existing\n"

    def test_force_overwrites(self, temp_spec_project, patched_llm):
        patched_llm.send_message.return_value = "def test_new():\n    assert False\n"
        out = temp_spec_project / "tests" / "test_feature.py"
        out.write_text("# old\n")
        result = runner.invoke(
            cli_main.app,
            ["test", "feature", "--path", str(temp_spec_project), "--force"],
        )
        assert result.exit_code == 0
        assert "def test_new" in out.read_text()

    def test_invalid_spec_reports_error(self, temp_generic_project, patched_llm):
        bad = temp_generic_project / "docs" / "specs" / "bad.md"
        bad.write_text("# no postconditions\n")
        result = runner.invoke(
            cli_main.app,
            ["test", "bad", "--path", str(temp_generic_project)],
        )
        assert "Cannot generate tests" in result.output or "Postconditions" in result.output


class TestSpecCommand:
    VALID_SPEC = """# Generated

## Postconditions

### Postcondition 1
**Name**: Login works
**Description**: User can authenticate with valid credentials and receive a session token
**Verification**: test
"""

    def test_requires_discovery(self, temp_generic_project, patched_llm):
        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "auth", "--path", str(temp_generic_project)],
        )
        assert "No discovery found" in result.output

    def test_writes_valid_spec(self, temp_discovery_project, patched_llm):
        patched_llm.send_message.return_value = self.VALID_SPEC
        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "auth", "--path", str(temp_discovery_project)],
        )
        assert result.exit_code == 0, result.output
        spec_file = temp_discovery_project / "docs" / "specs" / "auth.md"
        assert spec_file.exists()
        assert "Spec is valid" in result.output

    def test_retries_on_invalid_spec(self, temp_discovery_project, patched_llm):
        patched_llm.send_message.side_effect = [
            "# bad spec without postconditions\n",
            self.VALID_SPEC,
        ]
        result = runner.invoke(
            cli_main.app,
            ["spec", "--name", "auth", "--path", str(temp_discovery_project), "--retry", "1"],
        )
        assert result.exit_code == 0
        assert "Validation failed" in result.output
        assert "Spec is valid" in result.output
