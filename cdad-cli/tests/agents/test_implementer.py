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
