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

    def validate(self, test_dir: Path) -> TestResult:
        """Run tests and return results.

        Args:
            test_dir: Directory containing tests.

        Returns:
            TestResult with pass/fail counts.
        """
        if not test_dir.exists():
            return TestResult(passed=0, failed=0, errors=["Test directory not found"])

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_dir), "-v", "--tb=no"],
                capture_output=True,
                timeout=30,
                text=True,
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
        except Exception as e:
            return TestResult(passed=0, failed=0, errors=[str(e)])
