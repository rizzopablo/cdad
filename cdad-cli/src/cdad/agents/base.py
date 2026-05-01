"""BaseAgent - base class for all agents."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from cdad.project.model import ProjectModel
from cdad.llm.client import LLMClient


class BaseAgent(ABC):
    """Base class for all agents in the CDAD system."""

    def __init__(self, role: str, project: ProjectModel, llm_client: LLMClient):
        """Initialize BaseAgent.

        Args:
            role: Agent role (e.g., "architect", "test_writer").
            project: ProjectModel instance for the project.
            llm_client: LLMClient for communicating with Claude.
        """
        self.role = role
        self.project = project
        self.llm_client = llm_client

    @abstractmethod
    def get_accessible_files(self) -> List[Path]:
        """Return list of files accessible to this agent.

        Returns:
            List of file paths this agent can see.
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return system prompt for this agent.

        Returns:
            System prompt instructions for Claude.
        """
        pass

    def invoke(self, user_message: str) -> str:
        """Invoke the agent with a user message.

        Args:
            user_message: User message for the agent.

        Returns:
            Response from Claude.
        """
        system_prompt = self.get_system_prompt()
        return self.llm_client.send_message(user_message, system_prompt=system_prompt)

    def get_context(self) -> str:
        """Get context from accessible files.

        Returns:
            String containing contents of accessible files.
        """
        context_parts = []
        accessible_files = self.get_accessible_files()

        for file_path in accessible_files:
            if file_path.suffix in [".md", ".py", ".txt"]:
                try:
                    content = file_path.read_text(encoding="utf-8")
                    context_parts.append(f"## File: {file_path.name}\n{content}\n")
                except Exception:
                    pass

        return "\n".join(context_parts)
