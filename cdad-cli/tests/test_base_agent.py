"""Tests for BaseAgent - base class for all agents."""

from unittest.mock import MagicMock
from cdad.agents.base import BaseAgent
from cdad.project.model import ProjectModel
from cdad.llm.client import LLMClient


class ConcreteTestAgent(BaseAgent):
    """Concrete agent for testing BaseAgent."""

    def get_accessible_files(self):
        """Return accessible files for test agent."""
        return self.project.list_spec_files()

    def get_system_prompt(self) -> str:
        """Return system prompt."""
        return "Test agent system prompt"


class TestBaseAgent:
    """Test BaseAgent base class."""

    def test_initializes_with_role_and_project(self, temp_generic_project):
        """BaseAgent initializes with role and project."""
        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)

        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)

        assert agent.role == "test"
        assert agent.project is project
        assert agent.llm_client is llm_client

    def test_get_accessible_files_returns_list(self, temp_generic_project):
        """BaseAgent returns accessible files for agent."""
        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)
        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)

        files = agent.get_accessible_files()
        assert isinstance(files, list)

    def test_get_system_prompt_returns_string(self, temp_generic_project):
        """BaseAgent returns system prompt."""
        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)
        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)

        prompt = agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert prompt == "Test agent system prompt"

    def test_invoke_sends_message_to_llm(self, temp_generic_project):
        """BaseAgent.invoke sends message to LLMClient."""
        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)
        llm_client.send_message.return_value = "Response from LLM"

        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)
        result = agent.invoke("Test message")

        llm_client.send_message.assert_called_once()
        assert result == "Response from LLM"

    def test_get_context_returns_file_contents(self, temp_generic_project):
        """BaseAgent.get_context returns file contents."""
        # Create a spec file
        (temp_generic_project / "docs" / "specs" / "test.md").write_text("# Test Spec")

        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)
        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)

        context = agent.get_context()
        assert isinstance(context, str)
        assert "test.md" in context or "Test Spec" in context

    def test_agent_has_required_methods(self, temp_generic_project):
        """BaseAgent subclass must implement required methods."""
        project = ProjectModel(temp_generic_project)
        llm_client = MagicMock(spec=LLMClient)
        agent = ConcreteTestAgent(role="test", project=project, llm_client=llm_client)

        assert hasattr(agent, "invoke")
        assert hasattr(agent, "get_context")
        assert hasattr(agent, "get_accessible_files")
        assert hasattr(agent, "get_system_prompt")
        assert callable(agent.invoke)
        assert callable(agent.get_context)
