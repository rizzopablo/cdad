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
from cdad.llm.provider import ProviderError


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
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
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

    def _has_tests_path(self, files: dict[str, str]) -> str | None:
        """Check if any file path resolves under tests/. Return the offending path or None.

        Uses filesystem-level resolution so tricks like ``src/../tests/foo.py``,
        ``./tests/foo.py``, or ``src/./../tests/foo.py`` are correctly caught.
        """
        tests_root = (self.project.root_path / "tests").resolve()
        for filepath in files:
            full_path = (self.project.root_path / filepath).resolve()
            try:
                full_path.relative_to(tests_root)
                return filepath
            except ValueError:
                pass  # not under tests/
        return None

    def _write_files(self, files: dict[str, str]) -> list[Path]:
        """Write files to project root. Create dirs if needed.

        Safety: refuses to write absolute paths or anything that resolves
        outside the project root or under ``tests/``.
        """
        project_root = self.project.root_path.resolve()
        tests_root = (project_root / "tests").resolve()
        written = []
        for filepath, code in files.items():
            # Reject absolute paths from the LLM
            if Path(filepath).is_absolute():
                continue
            full_path = (project_root / filepath).resolve()
            # Reject paths that escape the project root
            try:
                full_path.relative_to(project_root)
            except ValueError:
                continue
            # Reject paths under tests/ (defence-in-depth)
            try:
                full_path.relative_to(tests_root)
                continue
            except ValueError:
                pass
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

    def _extract_active_feature(self, spec_path: Path, content: str) -> str:
        """Extract the active feature ID from spec content or path.

        Priority: frontmatter ``feature_id`` → parent directory name → fallback "003".
        """
        # 1. Try frontmatter feature_id (e.g. "003-current-feature")
        fm_match = re.search(r"^feature_id:\s*(.+)$", content, re.MULTILINE)
        if fm_match:
            fid = fm_match.group(1).strip()
            num_match = re.search(r"(\d{3})", fid)
            if num_match:
                return num_match.group(1)

        # 2. Try parent directory name (e.g. "003-implementer-agent")
        parent_name = spec_path.parent.name
        num_match = re.search(r"(\d{3})", parent_name)
        if num_match:
            return num_match.group(1)

        return "003"  # fallback

    def _scan_for_obsolete_references(
        self, test_output: str, active_feature: str = "003"
    ) -> list[ObsolescenceSuspicion]:
        """Heuristic: scan pytest output for references to closed specs (PC-NNN where NNN != active).

        Looks for patterns like PC-NNN, pc_NNN in test output, test names, error messages.
        """
        suspicions = []
        # Find all PC-NNN or pc_NNN references
        pattern = r"(?:PC[-_]|pc[_-])(\d{3})"
        found = re.findall(pattern, test_output, re.IGNORECASE)

        # Also scan test file names that may have been in the output
        test_file_pattern = r"test.*pc[_-](\d{3})"
        found += re.findall(test_file_pattern, test_output, re.IGNORECASE)

        for nnn in found:
            if nnn != active_feature:
                # Try to find the test file path from output
                # pytest -q outputs like: tests/test_file.py::test_name - error
                test_path_match = re.search(r"(tests/\S+\.py)", test_output)
                test_path = (
                    Path(test_path_match.group(1)) if test_path_match else Path("tests/unknown.py")
                )

                evidence = f"PC-{nnn}"
                suspicions.append(
                    ObsolescenceSuspicion(
                        test_path=test_path,
                        reason="references_closed_spec",
                        evidence=evidence,
                    )
                )

        return suspicions

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
        active_feature = self._extract_active_feature(spec_path, content)
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
            # Suite already green — scan for obsolescence before returning
            combined_output = test_result.stdout + test_result.stderr
            suspicions = self._scan_for_obsolete_references(
                combined_output, active_feature=active_feature
            )
            if suspicions:
                return ImplementResult(
                    success=False,
                    iterations_used=0,
                    files_modified=[],
                    final_test_output=combined_output,
                    error="test_obsolescence_suspected",
                    obsolescence_suspicions=suspicions,
                )
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
            try:
                llm_response = self.llm_client.send_message(prompt)
            except ProviderError as exc:
                call_duration = time.monotonic() - call_start
                error_msg = f"provider_error: {exc}"
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "iteration": i,
                    "pytest_passed": 0,
                    "pytest_failed": 0,
                    "files_modified": [],
                    "provider_call_duration_s": round(call_duration, 3),
                    "notes": error_msg,
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                return ImplementResult(
                    success=False,
                    iterations_used=i - 1,
                    files_modified=files_modified,
                    final_test_output=test_result.stdout + test_result.stderr,
                    error=error_msg,
                    obsolescence_suspicions=[],
                )
            call_duration = time.monotonic() - call_start

            # b) Parse response
            files_to_write = self._parse_llm_response(llm_response)

            # c) Validate: reject ALL if any path is under tests/
            forbidden_path = self._has_tests_path(files_to_write)
            if forbidden_path is not None:
                error_msg = f"test_modification_forbidden:{forbidden_path}"
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "iteration": i,
                    "pytest_passed": 0,
                    "pytest_failed": 0,
                    "files_modified": [],
                    "provider_call_duration_s": round(call_duration, 3),
                    "notes": f"test_modification_forbidden:{forbidden_path}",
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                return ImplementResult(
                    success=False,
                    iterations_used=i,
                    files_modified=[],
                    final_test_output="",
                    error=error_msg,
                )

            # d) Write files
            written = self._write_files(files_to_write)
            files_modified.extend(written)

            # e) Run pytest
            test_result = self._run_tests()
            passed, failed = self._parse_pytest_output(test_result.stdout)

            # f) Check for obsolescence heuristic
            combined_output = test_result.stdout + test_result.stderr
            suspicions = self._scan_for_obsolete_references(
                combined_output, active_feature=active_feature
            )
            if suspicions:
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "iteration": i,
                    "pytest_passed": passed,
                    "pytest_failed": failed,
                    "files_modified": [str(p) for p in written],
                    "provider_call_duration_s": round(call_duration, 3),
                    "notes": f"test_obsolescence_suspected: {len(suspicions)} detection(s)",
                }
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

                print(f"[Iteration {i}] Obsolescence suspected — {len(suspicions)} detection(s)")

                return ImplementResult(
                    success=False,
                    iterations_used=i,
                    files_modified=files_modified,
                    final_test_output=combined_output,
                    error="test_obsolescence_suspected",
                    obsolescence_suspicions=suspicions,
                )

            # g) Check if green
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
            error="max_iterations_reached",
        )
