"""ImplementerAgent — executes CDAD implementation cycles."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from cdad.agents.base import BaseAgent


class SpecNotFoundError(FileNotFoundError):
    """Raised when spec_path does not exist on the filesystem."""

    pass


class InvalidSpecError(ValueError):
    """Raised when spec exists but is missing postconditions."""

    pass


@dataclass
class ObsolescenceSuspicion:
    """Represents a suspicion of test obsolescence."""

    test_path: Path
    reason: str
    evidence: str


@dataclass
class ImplementResult:
    """Result of the implement() method."""

    success: bool
    iterations_used: int
    files_modified: list[Path]
    final_test_output: str = ""
    error: str | None = None
    obsolescence_suspicions: list[ObsolescenceSuspicion] = field(default_factory=list)


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

    def _run_tests(self) -> subprocess.CompletedProcess:
        """Run pytest from project root."""
        return subprocess.run(
            ["python", "-m", "pytest", "tests/", "-q"],
            cwd=self.project.root_path,
            capture_output=True,
            text=True,
        )

    def implement(
        self,
        spec_path: Path,
        max_iterations: int = 5,
        provider_override: str | None = None,
    ) -> ImplementResult:
        """Implement a feature from a spec.

        Args:
            spec_path: Path to the specification file.
            max_iterations: Max TDD cycles.
            provider_override: Optional provider override.

        Returns:
            ImplementResult with success status and details.

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
        postconditions_match = re.search(
            r"(?:^|\n)## Postconditions\s*(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if postconditions_match is None:
            raise InvalidSpecError(f"Invalid spec: no postconditions section found in {spec_path}")

        section_content = postconditions_match.group(1).strip()
        if not section_content:
            raise InvalidSpecError(f"Invalid spec: postconditions section is empty in {spec_path}")

        # Run tests to check if suite is already green
        test_result = self._run_tests()

        if test_result.returncode == 0:
            # Suite already green — no iterations needed
            return ImplementResult(
                success=True,
                iterations_used=0,
                files_modified=[],
                final_test_output=test_result.stdout,
                obsolescence_suspicions=[],
            )

        # TODO: implement TDD loop for RED suites (future cycles)
        return ImplementResult(
            success=False,
            iterations_used=0,
            files_modified=[],
            final_test_output=test_result.stdout + test_result.stderr,
            error="Suite is RED, TDD loop not yet implemented",
        )
