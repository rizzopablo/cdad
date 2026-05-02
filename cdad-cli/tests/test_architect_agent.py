"""Tests for ArchitectAgent."""

from unittest.mock import MagicMock

import pytest

from cdad.agents.architect import ArchitectAgent
from cdad.llm.client import LLMClient
from cdad.project.model import ProjectModel


def _make_agent(project_root):
    project = ProjectModel(project_root)
    llm_client = MagicMock(spec=LLMClient)
    llm_client.send_message.return_value = "LLM response"
    agent = ArchitectAgent(role="architect", project=project, llm_client=llm_client)
    return agent, llm_client


class TestArchitectAgentBasics:
    def test_get_accessible_files_includes_specs(self, temp_spec_project):
        agent, _ = _make_agent(temp_spec_project)
        files = agent.get_accessible_files()
        assert any(f.name == "feature.md" for f in files)

    def test_system_prompt_mentions_postconditions(self, temp_generic_project):
        agent, _ = _make_agent(temp_generic_project)
        assert "Postconditions" in agent.get_system_prompt()


class TestArchitectDiscoverAndDraft:
    def test_discover_calls_llm(self, temp_generic_project):
        agent, llm = _make_agent(temp_generic_project)
        result = agent.discover("user login")
        assert result == "LLM response"
        llm.send_message.assert_called_once()
        sent_msg = llm.send_message.call_args[0][0]
        assert "user login" in sent_msg

    def test_draft_spec_includes_discovery(self, temp_generic_project):
        agent, llm = _make_agent(temp_generic_project)
        agent.draft_spec("Discovery body XYZ")
        sent_msg = llm.send_message.call_args[0][0]
        assert "Discovery body XYZ" in sent_msg


class TestArchitectAnalyze:
    def test_analyze_raises_on_missing_path(self, temp_generic_project):
        agent, _ = _make_agent(temp_generic_project)
        with pytest.raises(FileNotFoundError):
            agent.analyze(temp_generic_project / "does-not-exist")

    def test_analyze_reads_file(self, temp_generic_project):
        target = temp_generic_project / "src" / "module.py"
        target.write_text("def hello():\n    return 'hi'\n")
        agent, llm = _make_agent(temp_generic_project)

        result = agent.analyze(target)

        assert result == "LLM response"
        sent_msg = llm.send_message.call_args[0][0]
        assert "module.py" in sent_msg
        assert "def hello" in sent_msg
        assert "## Summary" in sent_msg

    def test_analyze_reads_directory(self, temp_generic_project):
        src = temp_generic_project / "src"
        (src / "a.py").write_text("A = 1\n")
        (src / "b.py").write_text("B = 2\n")
        agent, llm = _make_agent(temp_generic_project)

        agent.analyze(src)
        sent_msg = llm.send_message.call_args[0][0]
        assert "a.py" in sent_msg
        assert "b.py" in sent_msg

    def test_analyze_truncates_large_files(self, temp_generic_project):
        big = temp_generic_project / "src" / "big.py"
        big.write_text("x = 0\n" * 5000)
        agent, llm = _make_agent(temp_generic_project)

        agent.analyze(big)
        sent_msg = llm.send_message.call_args[0][0]
        assert "[truncated]" in sent_msg


class TestArchitectRecommend:
    def test_recommend_includes_analysis(self, temp_generic_project):
        agent, llm = _make_agent(temp_generic_project)
        agent.recommend("## Summary\nLooks risky.")
        sent_msg = llm.send_message.call_args[0][0]
        assert "Looks risky" in sent_msg
        assert "High" in sent_msg

    def test_recommend_returns_llm_output(self, temp_generic_project):
        agent, _ = _make_agent(temp_generic_project)
        assert agent.recommend("analysis") == "LLM response"
