"""ImplementerAgent — executes CDAD implementation cycles."""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
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

    def _parse_llm_response(self, response: str) -> dict[str, str]:
        """Parse LLM response into {filepath: code} dict.

        Expected format: ### file: src/<path>\n<code>
        """
        files = {}
        pattern = r"###\s+file:\s*(\S+)\s*\n(.*?)(?=###\s+file:|\Z)"
        for match in re.finditer(pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            code = match.group(2).strip()
            files[filepath] = code
        return files

    def _write_files(self, files: dict[str, str]) -> list[Path]:
        """Write files to project root. Create dirs if needed."""
        written = []
        for filepath, code in files.items():
            full_path = self.project.root_path / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code, encoding="utf-8")
            written.append(full_path)
        return written

    def _parse_pytest_output(self, output: str) -> tuple[int, int]:
        """Parse pytest -q output into (passed, failed) counts."""
        passed = 0
        failed = 0
        # Typical: "5 passed, 2 failed in 0.10s"
        passed_match = re.search(r"(\d+)\s+passed", output)
        failed_match = re.search(r"(\d+)\s+failed", output)
        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        return passed, failed

    def _count_iterations_from_log(self, log_path: Path) -> int:
        """Return number of iterations from log file."""
        if not log_path.exists():
            return 0
        count = 0
        for line in log_path.read_text().strip().split("\n"):
            if line.strip():
                count += 1
        return count

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

        # Determine log directory (same as spec file's directory)
        log_dir = spec_path.parent
        log_path = log_dir / "implement.log"

        # Clear any previous log
        if log_path.exists():
            log_path.unlink()

        # TDD iteration loop
        files_modified: list[Path] = []
        iterations_used = 0
        spec_content = spec_path.read_text(encoding="utf-8")

        for i in range(1, max_iterations + 1):
            iterations_used = i

            # a) Invoke LLM
            prompt = f"""Implement the following specification to pass the tests:

{spec_content}

Current test output:
{test_result.stdout}
{test_result.stderr}

Return your code changes using this format:
### file: src/path/to/file.py
<code here>
"""
            call_start = time.monotonic()
            llm_response = self.llm_client.send_message(prompt)
            call_duration = time.monotonic() - call_start

            # b) Parse response
            files_to_write = self._parse_llm_response(llm_response)

            # c) Write files
            written = self._write_files(files_to_write)
            files_modified.extend(written)

            # d) Run pytest
            test_result = self._run_tests()
            passed, failed = self._parse_pytest_output(test_result.stdout)

            # e) Check if green
            if test_result.returncode == 0:
                # Write final log entry
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "iteration": i,
                    "pytest_passed": passed,
                    "pytest_failed": failed,
                    "files_modified": [str(p) for p in written],
                    "provider_call_duration_s": round(call_duration, 3),
                    "notes": "Suite GREEN",
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                print(f"[Iteration {i}] Suite GREEN — {passed} passed, {failed} failed")
                print(f"Modified: {', '.join(str(p) for p in written)}")

                return ImplementResult(
                    success=True,
                    iterations_used=i,
                    files_modified=files_modified,
                    final_test_output=test_result.stdout,
                    obsolescence_suspicions=[],
                )

            # f) Log and continue
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "iteration": i,
                "pytest_passed": passed,
                "pytest_failed": failed,
                "files_modified": [str(p) for p in written],
                "provider_call_duration_s": round(call_duration, 3),
                "notes": f"Suite RED — {failed} test(s) failing",
            }
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            print(f"[Iteration {i}] Suite RED — {passed} passed, {failed} failed")
            print(f"Modified: {', '.join(str(p) for p in written)}")

        # Exhausted all iterations without going green
        return ImplementResult(
            success=False,
            iterations_used=iterations_used,
            files_modified=files_modified,
            final_test_output=test_result.stdout + test_result.stderr,
            error=f"Failed to reach GREEN after {max_iterations} iterations",
        )
