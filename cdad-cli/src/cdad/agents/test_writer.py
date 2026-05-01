"""TestWriterAgent - generates pytest tests from validated specs."""

from pathlib import Path
from typing import List

from cdad.agents.base import BaseAgent
from cdad.validators.spec_validator import (
    SpecValidationError,
    SpecValidator,
)


class TestWriterAgent(BaseAgent):
    """Agent responsible for generating tests from spec postconditions."""

    def get_accessible_files(self) -> List[Path]:
        """Test writer sees specs, existing tests, and pyproject.toml."""
        files: List[Path] = []
        files.extend(self.project.list_spec_files())
        files.extend(self.project.list_test_files())
        pyproject = self.project.root_path / "pyproject.toml"
        if pyproject.exists():
            files.append(pyproject)
        return sorted(set(files))

    def get_system_prompt(self) -> str:
        """Return system prompt for test writer role."""
        return """You are a senior test engineer writing pytest tests for a CDAD project.

Rules:
1. Generate ONE Python test module that maps each postcondition to at least one pytest test.
2. Test function names must reflect the postcondition Name (snake_case).
3. Use the postcondition Verification method to choose the test style:
   - test: pure unit test (assertion on return value or state)
   - query: assertion on a queried value (mock or fixture)
   - integration: integration-style test (may use fixtures)
   - visual: skipped placeholder marked with pytest.mark.skip("visual verification")
4. Forbid vague assertions like `assert result` without a concrete expected value.
5. Tests MUST initially fail (RED phase) — assert against expected behavior the implementation does not yet provide.
6. Output ONLY valid Python source code, no markdown fences, no commentary."""

    def write_tests(self, spec_path: Path) -> str:
        """Generate test source code from a validated spec.

        Args:
            spec_path: Path to a spec markdown file under docs/specs/.

        Returns:
            Python source code for a single test_*.py file.

        Raises:
            FileNotFoundError: If spec_path does not exist.
            SpecValidationError: If the spec fails validation.
        """
        spec_path = Path(spec_path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec not found: {spec_path}")

        validator = SpecValidator()
        result = validator.validate_file(spec_path)
        if not result.is_valid:
            raise SpecValidationError(
                f"Cannot generate tests from invalid spec: {'; '.join(result.errors)}"
            )

        spec_content = spec_path.read_text(encoding="utf-8")
        postcondition_summary = "\n".join(
            f"- {pc.name} [{pc.verification_method}]: {pc.description}"
            for pc in result.postconditions
        )

        prompt = f"""Spec: {spec_path.name}

Postconditions to cover:
{postcondition_summary}

Full spec:
{spec_content}

Project context:
{self.get_context()}

Generate a complete pytest module covering every postcondition above.
Output Python source only."""
        return self.invoke(prompt)
