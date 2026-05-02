"""PhaseManager - manages CDAD workflow phases and state machine."""

from typing import Dict, Optional
import subprocess

from cdad.config import PHASES, DISCOVERY_FILE, REVIEW_FILE, MERGED_FLAG_FILE
from cdad.project.model import ProjectModel


class PhaseTransitionError(Exception):
    """Raised when attempting invalid phase transition."""

    pass


class PhaseManager:
    """Manages project phase detection and phase transitions."""

    def __init__(self, project: ProjectModel):
        """Initialize PhaseManager.

        Args:
            project: ProjectModel instance representing the project.
        """
        self.project = project

    @property
    def current_phase(self) -> str:
        """Detect and return current project phase.

        Returns:
            Current phase: none, discovery, spec, red, green, review, or merge.
        """
        return self.detect_phase()

    def detect_phase(self) -> str:
        """Detect the current phase based on project state.

        Returns:
            Current phase name.
        """
        # Check for merge phase first (final state)
        if (self.project.root_path / MERGED_FLAG_FILE).exists():
            return "merge"

        # Check for review phase
        if (self.project.root_path / REVIEW_FILE).exists():
            return "review"

        # Check for green/red phase (tests exist)
        test_files = self.project.list_test_files()
        if test_files:
            if self._tests_pass():
                return "green"
            else:
                return "red"

        # Check for spec phase
        spec_files = self.project.list_spec_files()
        if spec_files:
            return "spec"

        # Check for discovery phase
        if (self.project.root_path / DISCOVERY_FILE).exists():
            return "discovery"

        # Default: no phase
        return "none"

    def suggest_next_command(self) -> Optional[str]:
        """Suggest the next command based on current phase.

        Returns:
            Next command to run, or None if workflow is complete.
        """
        phase = self.current_phase
        phase_info = PHASES.get(phase, {})
        return phase_info.get("command")

    def validate_transition(self, from_phase: str, to_phase: str) -> bool:
        """Validate if a phase transition is allowed.

        Args:
            from_phase: Source phase.
            to_phase: Destination phase.

        Returns:
            True if transition is valid, False otherwise.
        """
        if from_phase not in PHASES or to_phase not in PHASES:
            return False

        # Get the next allowed phase
        next_phase = PHASES[from_phase].get("next")
        return next_phase == to_phase

    def get_phase_info(self, phase: str) -> Dict:
        """Get metadata about a phase.

        Args:
            phase: Phase name.

        Returns:
            Dictionary with phase metadata (next, command).
        """
        return PHASES.get(phase, {})

    def _tests_pass(self) -> bool:
        """Check if all tests in the project pass.

        Returns:
            True if all tests pass, False if any fail or no tests exist.
        """
        test_files = self.project.list_test_files()
        if not test_files:
            return False

        try:
            # Run pytest with quiet mode
            result = subprocess.run(
                ["python", "-m", "pytest", str(self.project.root_path / "tests"), "-q"],
                cwd=self.project.root_path,
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            # If pytest fails to run, assume tests don't pass
            return False
