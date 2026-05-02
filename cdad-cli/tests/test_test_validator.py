"""Tests for TestValidator."""

from pathlib import Path
from unittest.mock import patch
import subprocess

from cdad.validators.test_validator import TestValidator, TestResult


class TestTestValidator:
    """Tests for the TestValidator class."""

    def test_returns_error_when_test_dir_missing(self, tmp_path: Path):
        validator = TestValidator()
        result = validator.validate(tmp_path / "does_not_exist")

        assert isinstance(result, TestResult)
        assert result.passed == 0
        assert result.failed == 0
        assert result.errors == ["Test directory not found"]

    def test_parses_passed_and_failed_counts(self, tmp_path: Path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        fake_completed = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout=" test_a PASSED\n test_b PASSED\n test_c FAILED\n",
            stderr="",
        )
        with patch("subprocess.run", return_value=fake_completed):
            result = TestValidator().validate(tests_dir)

        assert result.passed == 2
        assert result.failed == 1
        assert result.errors == []

    def test_returncode_nonzero_with_no_failed_yields_error(self, tmp_path: Path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        fake = subprocess.CompletedProcess(
            args=[], returncode=2, stdout="collection error", stderr=""
        )
        with patch("subprocess.run", return_value=fake):
            result = TestValidator().validate(tests_dir)

        assert result.passed == 0
        assert result.failed == 0
        assert result.errors == ["Tests failed to run properly"]

    def test_timeout_returns_timeout_error(self, tmp_path: Path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=30),
        ):
            result = TestValidator().validate(tests_dir)

        assert result.passed == 0
        assert result.failed == 0
        assert result.errors == ["Test run timed out"]

    def test_oserror_is_captured_with_message(self, tmp_path: Path):
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        with patch("subprocess.run", side_effect=FileNotFoundError("python missing")):
            result = TestValidator().validate(tests_dir)

        assert result.passed == 0
        assert result.failed == 0
        assert result.errors and "python missing" in result.errors[0]
