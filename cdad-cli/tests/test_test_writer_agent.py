"""Tests for TestWriterAgent."""

from unittest.mock import MagicMock

import pytest

from cdad.agents.test_writer import TestWriterAgent
from cdad.llm.client import LLMClient
from cdad.project.model import ProjectModel
from cdad.validators.spec_validator import SpecValidationError


def _make_agent(project_root, response="def test_x():\n    assert False\n"):
    project = ProjectModel(project_root)
    llm_client = MagicMock(spec=LLMClient)
    llm_client.send_message.return_value = response
    return TestWriterAgent(role="test_writer", project=project, llm_client=llm_client), llm_client


class TestTestWriterAgentBasics:
    def test_accessible_files_includes_specs(self, temp_spec_project):
        agent, _ = _make_agent(temp_spec_project)
        files = agent.get_accessible_files()
        assert any(f.name == "feature.md" for f in files)

    def test_system_prompt_mentions_pytest(self, temp_generic_project):
        agent, _ = _make_agent(temp_generic_project)
        assert "pytest" in agent.get_system_prompt()


class TestWriteTests:
    def test_raises_when_spec_missing(self, temp_generic_project):
        agent, _ = _make_agent(temp_generic_project)
        with pytest.raises(FileNotFoundError):
            agent.write_tests(temp_generic_project / "docs" / "specs" / "missing.md")

    def test_raises_on_invalid_spec(self, temp_generic_project):
        bad_spec = temp_generic_project / "docs" / "specs" / "bad.md"
        bad_spec.write_text("# No postconditions section\n")
        agent, _ = _make_agent(temp_generic_project)
        with pytest.raises(SpecValidationError):
            agent.write_tests(bad_spec)

    def test_generates_tests_for_valid_spec(self, temp_spec_project):
        agent, llm = _make_agent(temp_spec_project)
        spec = temp_spec_project / "docs" / "specs" / "feature.md"

        result = agent.write_tests(spec)

        assert "def test_x" in result
        sent_msg = llm.send_message.call_args[0][0]
        assert "feature.md" in sent_msg
        # Postcondition name appears in the summary fed to the LLM
        assert "Test" in sent_msg
        assert "[test]" in sent_msg
