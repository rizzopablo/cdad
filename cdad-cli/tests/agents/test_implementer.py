"""Tests for ImplementerAgent — CICLO 2: PC-003-6.

Tests verify that ImplementerAgent.implement() raises SpecNotFoundError
or InvalidSpecError when spec_path is invalid.

RED phase: these tests fail because ImplementerAgent doesn't exist yet.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

# ===========================================================================
# STUBS: Minimal implementations for modules that don't exist yet.
# These allow tests to import and fail by AssertionError (correct RED).
# ===========================================================================

try:
    from cdad.agents.implementer import (
        ImplementerAgent,
        ImplementResult,
        InvalidSpecError,
        ObsolescenceSuspicion,
        SpecNotFoundError,
    )
except ImportError:

    class ImplementerAgent:
        """Stub for ImplementerAgent."""

        def __init__(self, role: str, project, llm_client):
            self.role = role
            self.project = project
            self.llm_client = llm_client

        def implement(
            self, spec_path: Path, max_iterations: int = 5, provider_override: str | None = None
        ):
            """Stub that always fails (correct RED behavior)."""
            raise NotImplementedError("ImplementerAgent.implement() not implemented yet")


# ===========================================================================
# Test helpers
# ===========================================================================


def _make_agent(project_root):
    """Create an ImplementerAgent with mocked LLM client."""
    from cdad.llm.client import LLMClient
    from cdad.project.model import ProjectModel

    project = ProjectModel(project_root)
    llm_client = MagicMock(spec=LLMClient)
    llm_client.send_message.return_value = "LLM response"
    agent = ImplementerAgent(role="implementer", project=project, llm_client=llm_client)
    return agent, llm_client


# ===========================================================================
# PC-003-6: Invalid spec handling
# ===========================================================================


class TestPC003_6_InvalidSpecHandling:
    """PC-003-6: Si el spec en spec_path no existe o no es válido (sin postcondiciones),
    el agente lanza SpecNotFoundError o InvalidSpecError. NO ejecuta tests ni invoca al provider.
    """

    def test_raises_spec_not_found_error_when_spec_path_does_not_exist(self, temp_generic_project):
        """Si spec_path no existe en filesystem, lanza SpecNotFoundError."""
        agent, llm = _make_agent(temp_generic_project)

        non_existent_path = temp_generic_project / "docs" / "specs" / "non_existent_spec.md"

        with pytest.raises(SpecNotFoundError):
            agent.implement(spec_path=non_existent_path)

        # Verificar que NO se invocó al provider
        llm.send_message.assert_not_called()

    def test_raises_invalid_spec_error_when_spec_has_no_postconditions(self, temp_generic_project):
        """Si spec existe pero no tiene postconditions, lanza InvalidSpecError."""
        agent, llm = _make_agent(temp_generic_project)

        # Crear un spec sin postconditions
        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        invalid_spec = spec_dir / "invalid_spec.md"
        invalid_spec.write_text("""---
title: Invalid Spec
---

# Spec

## Discovery
This feature does X, Y, Z.

# No hay sección ## Postconditions
""")

        with pytest.raises(InvalidSpecError):
            agent.implement(spec_path=invalid_spec)

        # Verificar que NO se invocó al provider
        llm.send_message.assert_not_called()

    def test_raises_spec_not_found_error_for_directory_path(self, temp_generic_project):
        """Si spec_path es un directorio (no un archivo), lanza SpecNotFoundError."""
        agent, llm = _make_agent(temp_generic_project)

        # Crear un directorio en lugar de un archivo
        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        dir_path = spec_dir / "a_directory"
        dir_path.mkdir()

        with pytest.raises(SpecNotFoundError):
            agent.implement(spec_path=dir_path)

        # Verificar que NO se invocó al provider
        llm.send_message.assert_not_called()

    def test_invalid_spec_error_mentions_missing_postconditions(self, temp_generic_project):
        """InvalidSpecError debe indicar que faltan postcondiciones."""
        agent, _ = _make_agent(temp_generic_project)

        # Crear un spec con ## Postconditions vacío
        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        empty_postconditions_spec = spec_dir / "empty_postconditions.md"
        empty_postconditions_spec.write_text("""---
title: Empty Postconditions
---

# Spec

## Postconditions

""")

        with pytest.raises(InvalidSpecError) as exc_info:
            agent.implement(spec_path=empty_postconditions_spec)

        # El mensaje de error debe mencionar postcondiciones
        error_msg = str(exc_info.value)
        assert "postcondition" in error_msg.lower() or "invalid" in error_msg.lower()


# ===========================================================================
# PC-003-1: Already GREEN suite handling (idempotencia)
# ===========================================================================


class TestPC003_1_AlreadyGreenSuite:
    """PC-003-1: Si la suite de tests está GREEN antes de cualquier iteración,
    retorna ImplementResult(success=True, iterations_used=0, files_modified=[],
    obsolescence_suspicions=[]).

    El implementer no debe iterar ni invocar al provider cuando ya está GREEN.
    """

    def test_returns_success_when_suite_already_green(self, temp_generic_project):
        """Si los tests ya pasan, retorna success=True sin iterar."""
        agent, llm = _make_agent(temp_generic_project)

        # Crear un spec válido
        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        valid_spec = spec_dir / "feature.md"
        valid_spec.write_text("""---
title: Test Feature
---

# Spec

## Postconditions

### Postcondition 1
**Name**: Test passes
**Description**: The test should pass
**Verification**: test
""")

        # Crear un test que YA pasa (GREEN suite)
        tests_dir = temp_generic_project / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_feature.py").write_text("""
def test_feature():
    assert True
""")

        result = agent.implement(spec_path=valid_spec)

        assert isinstance(result, ImplementResult), f"Expected ImplementResult, got {type(result)}"
        assert result.success is True, f"Expected success=True, got {result.success}"

    def test_returns_zero_iterations_when_already_green(self, temp_generic_project):
        """Cuando está GREEN, iterations_used debe ser 0."""
        agent, _ = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        valid_spec = spec_dir / "feature.md"
        valid_spec.write_text("""---
title: Test Feature
---

## Postconditions

### PC-1
**Name**: Test
**Description**: Test desc
**Verification**: test
""")

        tests_dir = temp_generic_project / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_feature.py").write_text("def test_pass(): pass")

        result = agent.implement(spec_path=valid_spec)

        assert result.iterations_used == 0, (
            f"Expected iterations_used=0, got {result.iterations_used}"
        )

    def test_returns_empty_files_modified_when_already_green(self, temp_generic_project):
        """Cuando está GREEN, no se modifican archivos (files_modified=[])."""
        agent, _ = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        valid_spec = spec_dir / "feature.md"
        valid_spec.write_text("""---
title: Test Feature
---

## Postconditions

### PC-1
**Name**: Test
**Description**: Test desc
**Verification**: test
""")

        tests_dir = temp_generic_project / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_feature.py").write_text("def test_pass(): pass")

        result = agent.implement(spec_path=valid_spec)

        assert result.files_modified == [], (
            f"Expected files_modified=[], got {result.files_modified}"
        )

    def test_returns_empty_obsolescence_suspicions_when_already_green(self, temp_generic_project):
        """Cuando está GREEN, no hay sospechas (obsolescence_suspicions=[])."""
        agent, _ = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        valid_spec = spec_dir / "feature.md"
        valid_spec.write_text("""---
title: Test Feature
---

## Postconditions

### PC-1
**Name**: Test
**Description**: Test desc
**Verification**: test
""")

        tests_dir = temp_generic_project / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_feature.py").write_text("def test_pass(): pass")

        result = agent.implement(spec_path=valid_spec)

        assert result.obsolescence_suspicions == [], (
            f"Expected obsolescence_suspicions=[], got {result.obsolescence_suspicions}"
        )

    def test_does_not_invoke_llm_when_already_green(self, temp_generic_project):
        """Cuando está GREEN, NO se debe invocar al provider LLM."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)
        valid_spec = spec_dir / "feature.md"
        valid_spec.write_text("""---
title: Test Feature
---

## Postconditions

### PC-1
**Name**: Test
**Description**: Test desc
**Verification**: test
""")

        tests_dir = temp_generic_project / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_feature.py").write_text("def test_pass(): pass")

        agent.implement(spec_path=valid_spec)

        llm.send_message.assert_not_called()


# ===========================================================================
# PC-003-2, PC-003-8, PC-003-9: Iterative loop with logging and stdout
# ===========================================================================


class TestPC003_2_8_9_IterativeLoop:
    """CICLO 4: Tests for iterative TDD loop, NDJSON logging, and stdout progress.

    - PC-003-2: After one or more iterations reaching GREEN, returns success=True
      with iterations_used > 0 and files_modified listing paths under src/.
    - PC-003-8: implement.log in NDJSON format with required fields.
    - PC-003-9: Progress printed to stdout in real-time.
    """

    def _create_failing_test_and_mock_llm(
        self, project_root, spec_dir, llm_mock, passing_code: str
    ):
        """Helper: Create a spec with a failing test, mock LLM to return code that fixes it."""
        # Create valid spec
        spec_path = spec_dir / "feature.md"
        spec_path.write_text("""---
title: Calculator Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Add function works
**Description**: add(2, 3) returns 5
**Verification**: test
""")

        # Create a failing test
        tests_dir = project_root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_calculator.py").write_text("""
def test_add():
    from src.calculator import add
    assert add(2, 3) == 5
""")

        # Mock LLM to return code that makes test pass
        llm_mock.send_message.return_value = f"""### file: src/calculator.py
{passing_code}
"""

        return spec_path

    def test_returns_success_with_iterations_used_greater_than_zero(
        self, temp_generic_project, capsys
    ):
        """PC-003-2: Si alcanza GREEN tras iterar, success=True con iterations_used > 0."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        # Create src directory
        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        result = agent.implement(spec_path=spec_path, max_iterations=5)

        assert isinstance(result, ImplementResult)
        assert result.success is True, f"Expected success=True, got {result.success}"
        assert result.iterations_used > 0, (
            f"Expected iterations_used > 0, got {result.iterations_used}"
        )

    def test_returns_files_modified_under_src(self, temp_generic_project):
        """PC-003-2: files_modified lista paths bajo src/ creados/modificados."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        result = agent.implement(spec_path=spec_path)

        assert isinstance(result, ImplementResult)
        assert len(result.files_modified) > 0, "Expected at least one file modified"
        for path in result.files_modified:
            assert "src/" in str(path) or path.name == "calculator.py", (
                f"Expected path under src/, got {path}"
            )

    def test_implement_log_created_in_ndjson_format(self, temp_generic_project):
        """PC-003-8: implement.log se genera en docs/specs/<feature-id>/implement.log."""
        import json

        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs" / "calc-feature"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        agent.implement(spec_path=spec_path)

        log_path = spec_dir / "implement.log"
        assert log_path.exists(), f"Expected implement.log at {log_path}"

        # Verify NDJSON format: each line must be valid JSON
        lines = log_path.read_text().strip().split("\n")
        assert len(lines) > 0, "Log should have at least one line"
        for line in lines:
            entry = json.loads(line)  # NDJSON: each line is JSON
            # Required fields per spec
            assert "timestamp" in entry, "Missing timestamp field"
            assert "iteration" in entry, "Missing iteration field"
            assert "pytest_passed" in entry, "Missing pytest_passed field"
            assert "pytest_failed" in entry, "Missing pytest_failed field"
            assert "files_modified" in entry, "Missing files_modified field"
            assert "provider_call_duration_s" in entry, "Missing provider_call_duration_s field"
            assert "notes" in entry, "Missing notes field"

    def test_log_iteration_field_is_integer(self, temp_generic_project):
        """PC-003-8: El campo iteration es entero y comienza en 1."""
        import json

        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs" / "test-feature"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        agent.implement(spec_path=spec_path)

        log_path = spec_dir / "implement.log"
        lines = log_path.read_text().strip().split("\n")

        iterations = [json.loads(line)["iteration"] for line in lines]
        assert all(isinstance(i, int) for i in iterations), "iteration must be int"
        assert iterations[0] == 1, f"First iteration should be 1, got {iterations[0]}"

    def test_stdout_shows_iteration_start(self, temp_generic_project, capsys):
        """PC-003-9: Imprime inicio de iteración a stdout."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        agent.implement(spec_path=spec_path)

        captured = capsys.readouterr()
        stdout = captured.out
        assert "iterat" in stdout.lower() or "iteration" in stdout.lower(), (
            f"Expected 'iteration' in stdout, got: {stdout[:200]}"
        )

    def test_stdout_shows_pytest_result(self, temp_generic_project, capsys):
        """PC-003-9: Imprime resultado de pytest resumido a stdout."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        agent.implement(spec_path=spec_path)

        captured = capsys.readouterr()
        stdout = captured.out
        assert "pass" in stdout.lower() or "fail" in stdout.lower() or "pytest" in stdout.lower(), (
            f"Expected pytest result in stdout, got: {stdout[:200]}"
        )

    def test_stdout_shows_files_modified(self, temp_generic_project, capsys):
        """PC-003-9: Imprime archivos modificados a stdout."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_and_mock_llm(
            temp_generic_project, spec_dir, llm, passing_code="def add(a, b): return a + b"
        )

        agent.implement(spec_path=spec_path)

        captured = capsys.readouterr()
        stdout = captured.out
        assert (
            "file" in stdout.lower() or "src/" in stdout.lower() or "calculator" in stdout.lower()
        ), f"Expected files modified in stdout, got: {stdout[:200]}"


# ===========================================================================
# PC-003-3: Max iterations reached without achieving GREEN
# ===========================================================================


class TestPC003_3_MaxIterationsReached:
    """PC-003-3: Si tras max_iterations iteraciones la suite sigue RED,
    retorna success=False con error != None y final_test_output contiene
    output del último pytest.
    """

    def _create_failing_test_with_broken_llm(self, project_root, spec_dir, llm_mock):
        """Helper: Create a spec with failing test, mock LLM returns code that doesn't fix it."""
        spec_path = spec_dir / "feature.md"
        spec_path.write_text("""---
title: Broken Feature
---

# Spec

## Postconditions

### PC-001
**Name**: Magic function works
**Description**: magic() returns 42
**Verification**: test
""")

        tests_dir = project_root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "test_broken.py").write_text("""
def test_magic():
    from src.magic import magic
    assert magic() == 42
""")

        # Mock LLM returns code that does NOT fix the test (wrong return value)
        llm_mock.send_message.return_value = """### file: src/magic.py
def magic():
    return 0  # Wrong! Should be 42
"""

        return spec_path

    def test_returns_success_false_when_max_iterations_reached(self, temp_generic_project):
        """PC-003-3: Cuando se agotan iteraciones sin alcanzar GREEN, success=False."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_with_broken_llm(temp_generic_project, spec_dir, llm)

        result = agent.implement(spec_path=spec_path, max_iterations=1)

        assert isinstance(result, ImplementResult)
        assert result.success is False, (
            f"Expected success=False when max_iterations reached, got {result.success}"
        )

    def test_error_is_not_none_when_max_iterations_reached(self, temp_generic_project):
        """PC-003-3: El campo error NO es None cuando se agotan iteraciones."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_with_broken_llm(temp_generic_project, spec_dir, llm)

        result = agent.implement(spec_path=spec_path, max_iterations=1)

        assert result.error is not None, "Expected error != None when max_iterations reached"
        assert len(result.error) > 0, "Expected non-empty error message"

    def test_iterations_used_equals_max_iterations(self, temp_generic_project):
        """PC-003-3: iterations_used debe ser igual a max_iterations cuando se agotan."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_with_broken_llm(temp_generic_project, spec_dir, llm)

        max_iter = 2
        result = agent.implement(spec_path=spec_path, max_iterations=max_iter)

        assert result.iterations_used == max_iter, (
            f"Expected iterations_used={max_iter}, got {result.iterations_used}"
        )

    def test_final_test_output_contains_pytest_output(self, temp_generic_project):
        """PC-003-3: final_test_output contiene output del último pytest."""
        agent, llm = _make_agent(temp_generic_project)

        spec_dir = temp_generic_project / "docs" / "specs"
        spec_dir.mkdir(parents=True, exist_ok=True)

        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "__init__.py").write_text("")

        spec_path = self._create_failing_test_with_broken_llm(temp_generic_project, spec_dir, llm)

        result = agent.implement(spec_path=spec_path, max_iterations=1)

        # final_test_output debe contener info de pytest (test name, assertion error, etc.)
        output = result.final_test_output
        assert len(output) > 0, "Expected non-empty final_test_output"
        assert (
            "test" in output.lower()
            or "assert" in output.lower()
            or "failed" in output.lower()
            or "error" in output.lower()
        ), f"Expected pytest output in final_test_output, got: {output[:200]}"
