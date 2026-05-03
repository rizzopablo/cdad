"""ImplementerAgent — executes CDAD implementation cycles."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

from cdad.agents.base import BaseAgent


class SpecNotFoundError(FileNotFoundError):
    """Raised when spec_path does not exist on the filesystem."""

    pass


class InvalidSpecError(ValueError):
    """Raised when spec exists but is missing postconditions."""

    pass


class ImplementerAgent(BaseAgent):
    """Agent responsible for code implementation from specs."""

    def get_accessible_files(self) -> List[Path]:
        """Implementer can see specs, common docs, and source files."""
        files = list(self.project.list_spec_files())
        files.extend(self.project.list_test_files())
        files.extend(self.project.root_path.rglob("*.md"))
        return sorted(set(files))

    def get_system_prompt(self) -> str:
        """Return system prompt for implementer role."""
        return """You are an expert software developer implementing features following CDAD.

Your role is to:
1. Read the specification
2. Run tests
3. Implement code to pass all postconditions"""

    def implement(
        self,
        spec_path: Path,
        max_iterations: int = 5,
        provider_override: str | None = None,
    ) -> str:
        """Implement a feature from a spec.

        Args:
            spec_path: Path to the specification file.
            max_iterations: Max TDD cycles (unused in this cycle).
            provider_override: Optional provider override (unused in this cycle).

        Returns:
            Implementation result.

        Raises:
            SpecNotFoundError: If spec_path does not exist.
            InvalidSpecError: If spec has no postconditions section.
        """
        spec_path = Path(spec_path)

        # Validate: path must exist and be a file
        if not spec_path.exists() or spec_path.is_dir():
            raise SpecNotFoundError(f"Spec file not found: {spec_path}")

        # Validate: spec must contain ## Postconditions as a real heading
        content = spec_path.read_text(encoding="utf-8")
        # Match ## Postconditions as markdown heading, not as inline text
        postconditions_match = re.search(
            r"(?:^|\n)## Postconditions\s*(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if postconditions_match is None:
            raise InvalidSpecError(f"Invalid spec: no postconditions section found in {spec_path}")

        section_content = postconditions_match.group(1).strip()
        if not section_content:
            raise InvalidSpecError(f"Invalid spec: postconditions section is empty in {spec_path}")

        # TODO: implement TDD loop (future cycles)
        return "ImplementerAgent.implement() — postconditions validated, implementation pending"
