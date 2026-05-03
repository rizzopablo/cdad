import random
import shutil
import string
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cdad.agents.implementer import ImplementerAgent
from cdad.llm.client import LLMClient
from cdad.project.model import ProjectModel
from tests.fakes.fake_acp_provider import FakeACPProvider


def random_string(length=10):
    """Generate a random string of fixed length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_response():
    """Generate a random LLM response with file blocks."""
    num_files = random.randint(1, 3)
    response = ""
    for _ in range(num_files):
        # 40% chance of attempting to write to tests/
        r = random.random()
        if r < 0.1:
            path = f"tests/{random_string()}.py"
        elif r < 0.2:
            path = f"tests/subfolder/{random_string()}.py"
        elif r < 0.4:
            # Tricky paths
            tricks = [
                f"src/../tests/{random_string()}.py",
                f"./tests/{random_string()}.py",
                f"tests// {random_string()}.py",
                "tests/conftest.py",
                f"src/../../tests/{random_string()}.py",
                f"src/./../tests/{random_string()}.py",
                f"/tests/{random_string()}.py",
                f"../tests/{random_string()}.py",
            ]
            path = random.choice(tricks)
        else:
            path = f"src/{random_string()}.py"

        content = f"# Random content: {random_string(50)}\n"
        response += f"### file: {path}\n{content}\n\n"
    return response


@pytest.mark.property
def test_implementer_invariant_never_modifies_tests(temp_generic_project):
    """Property test: ∀ execution, no file under tests/ is touched.

    Generates 100 random sequences of LLM responses and verifies tests/ integrity.
    """
    # 1. Setup project structure
    spec_dir = temp_generic_project / "docs" / "specs" / "prop-feat"
    spec_dir.mkdir(parents=True, exist_ok=True)
    spec_path = spec_dir / "spec.md"
    spec_path.write_text("## Postconditions\n### PC-1\nVerification: test\n")

    src_dir = temp_generic_project / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    tests_dir = temp_generic_project / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    # Create some initial test files to verify they are NOT modified/deleted
    (tests_dir / "test_initial.py").write_text("def test_ok(): pass\n")
    (tests_dir / "conftest.py").write_text("# Global config\n")

    # Create a failing test to force the agent into the loop
    (tests_dir / "test_fail.py").write_text("def test_f(): assert False\n")

    # Record initial state of tests/
    def get_tests_state():
        state = {}
        for p in tests_dir.rglob("*"):
            if p.is_file():
                state[str(p.relative_to(tests_dir))] = p.read_bytes()
        return state

    initial_state = get_tests_state()
    assert len(initial_state) == 3

    project = ProjectModel(temp_generic_project)

    # To make the test faster, we mock _run_tests because we are testing the
    # file-writing invariant, not the pytest integration itself.
    # However, we keep it as realistic as possible by letting it be called.

    for i in range(100):
        # Generate random responses for up to 3 iterations (to keep it reasonably fast)
        max_iter = 3
        responses = [generate_random_response() for _ in range(max_iter)]

        # We also need a "test result" mock because ImplementerAgent calls _run_tests
        # which returns a CompletedProcess.

        fake_provider = FakeACPProvider(responses)
        llm_client = LLMClient(provider=fake_provider)

        agent = ImplementerAgent(role="implementer", project=project, llm_client=llm_client)

        # We mock _run_tests to return a failing result (so it continues)
        # unless we hit GREEN (which we won't with random code)
        from subprocess import CompletedProcess

        agent._run_tests = MagicMock(
            return_value=CompletedProcess(
                args=[], returncode=1, stdout="1 passed, 1 failed", stderr=""
            )
        )

        # Run implementation
        agent.implement(spec_path=spec_path, max_iterations=max_iter)

        # 2. VERIFY INVARIANT: tests/ is untouched
        current_state = get_tests_state()

        if current_state != initial_state:
            # Find what changed for better error message
            added = set(current_state.keys()) - set(initial_state.keys())
            removed = set(initial_state.keys()) - set(current_state.keys())
            modified = [
                k
                for k in current_state.keys() & initial_state.keys()
                if current_state[k] != initial_state[k]
            ]

            error_msg = f"Iteration {i}: tests/ modified!\n"
            if added:
                error_msg += f"Added: {added}\n"
            if removed:
                error_msg += f"Removed: {removed}\n"
            if modified:
                error_msg += f"Modified: {modified}\n"

            pytest.fail(error_msg)

    # Final verification: no extra files in tests/
    assert get_tests_state() == initial_state
