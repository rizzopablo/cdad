"""TestValidator - validates test status in projects."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class TestResult:
    """Result of test validation."""

    passed: int
    failed: int
    errors: list


class TestValidator:
    """Validates test status for a project."""

    def validate(self, test_dir: Path, project_root: Path = None) -> TestResult:
        """Run tests and return results.

        Args:
            test_dir: Directory containing tests.
            project_root: Project root directory (for cwd when running pytest).

        Returns:
            TestResult with pass/fail counts.
        """
        if not test_dir.exists():
            return TestResult(passed=0, failed=0, errors=["Test directory not found"])

        # Use project_root as cwd, or test_dir parent if not specified
        cwd = project_root or test_dir.parent
        if not cwd.exists():
            cwd = Path.cwd()

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_dir), "-v", "--tb=no"],
                capture_output=True,
                timeout=30,
                text=True,
                cwd=cwd,
            )

            # Parse output to count passes/failures
            output = result.stdout + result.stderr
            passed = output.count(" PASSED")
            failed = output.count(" FAILED")

            errors = []
            if result.returncode != 0 and failed == 0:
                errors = ["Tests failed to run properly"]

            return TestResult(passed=passed, failed=failed, errors=errors)
        except subprocess.TimeoutExpired:
            return TestResult(passed=0, failed=0, errors=["Test run timed out"])
        except (OSError, subprocess.SubprocessError) as e:
            return TestResult(passed=0, failed=0, errors=[str(e)])
