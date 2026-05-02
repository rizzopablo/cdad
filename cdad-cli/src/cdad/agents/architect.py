"""ArchitectAgent - discovers requirements, drafts specs, analyzes code."""

from typing import List
from pathlib import Path

from cdad.agents.base import BaseAgent

CODE_SUFFIXES = {".py", ".md", ".txt", ".toml", ".cfg", ".ini"}
MAX_FILE_BYTES = 16_000
MAX_FILES = 40


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

    def analyze(self, code_path: Path) -> str:
        """Analyze an existing code path and produce a structured assessment.

        Args:
            code_path: File or directory to analyze.

        Returns:
            Markdown analysis covering responsibilities, coupling, gaps, risks.

        Raises:
            FileNotFoundError: If code_path does not exist.
        """
        code_path = Path(code_path)
        if not code_path.exists():
            raise FileNotFoundError(f"Code path not found: {code_path}")

        snippets = self._collect_code_snippets(code_path)
        prompt = f"""Analyze the code at: {code_path}

Project context:
{self.get_context()}

Code under review:
{snippets}

Produce a markdown analysis with these sections:
## Summary
## Responsibilities
## Coupling & Dependencies
## Test Coverage Gaps
## Risks
Be specific. Reference file names. Avoid vague language."""
        return self.invoke(prompt)

    def recommend(self, analysis: str) -> str:
        """Turn an analysis into prioritized, actionable recommendations.

        Args:
            analysis: Markdown analysis output from `analyze`.

        Returns:
            Markdown recommendations grouped by priority and category.
        """
        prompt = f"""Given this code analysis:
{analysis}

Produce prioritized, actionable recommendations as markdown.
Group by priority (## High, ## Medium, ## Low).
For each item include:
- **Category**: refactor | extract | add-test | contract-gap
- **Action**: concrete change to make
- **Rationale**: why it matters
Be specific and testable. No vague advice."""
        return self.invoke(prompt)

    def _collect_code_snippets(self, code_path: Path) -> str:
        """Read up to MAX_FILES files under code_path into a single context blob."""
        if code_path.is_file():
            files = [code_path]
        else:
            files = sorted(
                f for f in code_path.rglob("*") if f.is_file() and f.suffix in CODE_SUFFIXES
            )[:MAX_FILES]

        parts = []
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                continue
            if len(content) > MAX_FILE_BYTES:
                content = content[:MAX_FILE_BYTES] + "\n... [truncated]"
            rel = f.relative_to(code_path) if code_path.is_dir() else f.name
            parts.append(f"### File: {rel}\n```\n{content}\n```\n")
        return "\n".join(parts) if parts else "(no readable files found)"

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
