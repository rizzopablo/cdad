"""ArchitectAgent - discovers requirements and drafts specs."""

from typing import List
from pathlib import Path

from cdad.agents.base import BaseAgent


class ArchitectAgent(BaseAgent):
    """Agent responsible for discovery and spec generation."""

    def get_accessible_files(self) -> List[Path]:
        """Architect can see README, docs, and existing specs."""
        files = []

        # README
        readme = self.project.root_path / "README.md"
        if readme.exists():
            files.append(readme)

        # Docs directory
        docs_dir = self.project.root_path / "docs"
        if docs_dir.exists():
            files.extend(sorted(docs_dir.rglob("*.md")))

        # Existing specs
        files.extend(self.project.list_spec_files())

        return sorted(set(files))

    def get_system_prompt(self) -> str:
        """Return system prompt for architect role."""
        return """You are an expert software architect using Contract-Driven AI Development (CDAD).

Your role is to:
1. Understand project context and requirements
2. Identify testable postconditions for features
3. Draft detailed specifications

For each specification, include:
- ## Postconditions section
- Each postcondition must have:
  - **Name**: Short identifier
  - **Description**: Detailed, testable description
  - **Verification**: one of [test, query, visual, integration]

Be specific and avoid vague language like "works properly" or "is correct"."""

    def discover(self, feature_description: str) -> str:
        """Discover requirements for a feature.

        Args:
            feature_description: Description of feature to discover.

        Returns:
            Discovery output from Claude.
        """
        context = self.get_context()
        prompt = f"""Discover requirements for: {feature_description}

Project context:
{context}

Provide a structured discovery with:
1. Key requirements
2. User stories
3. Edge cases to consider
4. Suggested postconditions"""

        return self.invoke(prompt)

    def draft_spec(self, discovery: str) -> str:
        """Draft a specification from discovery output.

        Args:
            discovery: Discovery output to use as basis.

        Returns:
            Markdown spec with postconditions.
        """
        context = self.get_context()
        prompt = f"""Based on this discovery:
{discovery}

Project context:
{context}

Draft a complete CDAD specification with:
- Markdown format
- ## Postconditions section
- 3-5 specific, testable postconditions
- Each postcondition with Name, Description, and Verification method"""

        return self.invoke(prompt)
