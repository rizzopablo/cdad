"""Tests for PhaseManager - detects project phase and validates transitions."""

from cdad.project.model import ProjectModel
from cdad.orchestrator.phase_manager import PhaseManager


class TestPhaseManager:
    """Test PhaseManager detects phases and manages state machine."""

    def test_detects_none_phase(self, temp_generic_project):
        """PhaseManager detects 'none' phase when no specs exist."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "none"

    def test_detects_discovery_phase(self, temp_discovery_project):
        """PhaseManager detects 'discovery' phase when discovery.md exists."""
        project = ProjectModel(temp_discovery_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "discovery"

    def test_detects_spec_phase(self, temp_spec_project):
        """PhaseManager detects 'spec' phase when spec files exist."""
        project = ProjectModel(temp_spec_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "spec"

    def test_detects_red_phase(self, temp_red_project):
        """PhaseManager detects 'red' phase when tests fail."""
        project = ProjectModel(temp_red_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "red"

    def test_detects_green_phase(self, temp_green_project):
        """PhaseManager detects 'green' phase when tests pass."""
        project = ProjectModel(temp_green_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "green"

    def test_detects_review_phase(self, temp_review_project):
        """PhaseManager detects 'review' phase when review report exists."""
        project = ProjectModel(temp_review_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "review"

    def test_detects_merge_phase(self, temp_merge_project):
        """PhaseManager detects 'merge' phase when merged flag exists."""
        project = ProjectModel(temp_merge_project)
        manager = PhaseManager(project)

        assert manager.current_phase == "merge"

    def test_suggest_next_command_from_none(self, temp_generic_project):
        """PhaseManager suggests 'discover' command from 'none' phase."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "discover"

    def test_suggest_next_command_from_discovery(self, temp_discovery_project):
        """PhaseManager suggests 'spec' command from 'discovery' phase."""
        project = ProjectModel(temp_discovery_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "spec"

    def test_suggest_next_command_from_spec(self, temp_spec_project):
        """PhaseManager suggests 'red' command from 'spec' phase."""
        project = ProjectModel(temp_spec_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "red"

    def test_suggest_next_command_from_red(self, temp_red_project):
        """PhaseManager suggests 'green' command from 'red' phase."""
        project = ProjectModel(temp_red_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "green"

    def test_suggest_next_command_from_green(self, temp_green_project):
        """PhaseManager suggests 'review' command from 'green' phase."""
        project = ProjectModel(temp_green_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "review"

    def test_suggest_next_command_from_review(self, temp_review_project):
        """PhaseManager suggests 'merge' command from 'review' phase."""
        project = ProjectModel(temp_review_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd == "merge"

    def test_suggest_next_command_from_merge(self, temp_merge_project):
        """PhaseManager returns None for next command from 'merge' phase."""
        project = ProjectModel(temp_merge_project)
        manager = PhaseManager(project)

        next_cmd = manager.suggest_next_command()
        assert next_cmd is None

    def test_validate_valid_transition(self, temp_generic_project):
        """PhaseManager validates valid phase transitions."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        # Valid transition: none -> discovery
        is_valid = manager.validate_transition("none", "discovery")
        assert is_valid is True

    def test_reject_invalid_transition(self, temp_generic_project):
        """PhaseManager rejects invalid phase transitions."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        # Invalid transition: spec -> merge (must go through red, green, review)
        is_valid = manager.validate_transition("spec", "merge")
        assert is_valid is False

    def test_get_phase_info(self, temp_generic_project):
        """PhaseManager returns metadata about a phase."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        info = manager.get_phase_info("none")
        assert isinstance(info, dict)
        assert "next" in info
        assert "command" in info
        assert info["command"] == "discover"

    def test_phase_manager_attributes(self, temp_generic_project):
        """PhaseManager has expected attributes."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        assert hasattr(manager, "project")
        assert hasattr(manager, "current_phase")
        assert manager.project is project

    def test_phase_transitions_form_valid_path(self, temp_generic_project):
        """PhaseManager allows valid path through all phases."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        valid_path = ["none", "discovery", "spec", "red", "green", "review", "merge"]
        for i in range(len(valid_path) - 1):
            is_valid = manager.validate_transition(valid_path[i], valid_path[i + 1])
            assert (
                is_valid is True
            ), f"Transition {valid_path[i]} -> {valid_path[i + 1]} should be valid"

    def test_cannot_skip_phases(self, temp_generic_project):
        """PhaseManager prevents skipping phases in workflow."""
        project = ProjectModel(temp_generic_project)
        manager = PhaseManager(project)

        # Cannot skip from discovery directly to red
        is_valid = manager.validate_transition("discovery", "red")
        assert is_valid is False
