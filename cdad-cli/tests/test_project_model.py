"""Tests for ProjectModel - reads project structure and detects frameworks."""

import pytest
from pathlib import Path
from cdad.project.model import ProjectModel


class TestProjectModel:
    """Test ProjectModel detects frameworks and navigates project."""

    def test_detects_generic_python_project(self, temp_generic_project):
        """ProjectModel detects generic Python project with pyproject.toml."""
        model = ProjectModel(temp_generic_project)
        assert model.framework == "generic"

    def test_detects_odoo_addon_project(self, temp_odoo_project):
        """ProjectModel detects Odoo addon with __manifest__.py."""
        model = ProjectModel(temp_odoo_project)
        assert model.framework == "odoo"

    def test_detects_django_project(self, temp_django_project):
        """ProjectModel detects Django project with manage.py."""
        model = ProjectModel(temp_django_project)
        assert model.framework == "django"

    def test_returns_unknown_for_unrecognized_framework(self, tmp_path):
        """ProjectModel returns 'unknown' for unrecognized framework."""
        (tmp_path / "docs").mkdir()
        model = ProjectModel(tmp_path)
        assert model.framework == "unknown"

    def test_lists_spec_files(self, temp_generic_project):
        """ProjectModel lists spec files from docs/specs/."""
        # Create some spec files
        (temp_generic_project / "docs" / "specs" / "auth.md").write_text("# Auth spec")
        (temp_generic_project / "docs" / "specs" / "storage.md").write_text("# Storage spec")

        model = ProjectModel(temp_generic_project)
        specs = model.list_spec_files()

        assert len(specs) == 2
        spec_names = {p.name for p in specs}
        assert spec_names == {"auth.md", "storage.md"}

    def test_lists_no_spec_files_when_none_exist(self, temp_generic_project):
        """ProjectModel returns empty list when no spec files exist."""
        model = ProjectModel(temp_generic_project)
        specs = model.list_spec_files()
        assert specs == []

    def test_lists_test_files(self, temp_generic_project):
        """ProjectModel lists test files from tests/."""
        # Create some test files
        (temp_generic_project / "tests" / "test_auth.py").write_text("# Test auth")
        (temp_generic_project / "tests" / "test_models.py").write_text("# Test models")

        model = ProjectModel(temp_generic_project)
        tests = model.list_test_files()

        assert len(tests) == 2
        test_names = {p.name for p in tests}
        assert test_names == {"test_auth.py", "test_models.py"}

    def test_lists_no_test_files_when_none_exist(self, temp_generic_project):
        """ProjectModel returns empty list when no test files exist."""
        model = ProjectModel(temp_generic_project)
        tests = model.list_test_files()
        assert tests == []

    def test_reads_spec_file_content(self, temp_generic_project):
        """ProjectModel reads content of specific spec file."""
        spec_content = "# Auth Spec\nTest content"
        (temp_generic_project / "docs" / "specs" / "auth.md").write_text(spec_content)

        model = ProjectModel(temp_generic_project)
        content = model.read_spec("auth.md")

        assert content == spec_content

    def test_reads_memory_bank(self, temp_generic_project):
        """ProjectModel reads AGENTS.md memory bank."""
        memory_content = "# Project Memory Bank\nPhase: 0"
        (temp_generic_project / "AGENTS.md").write_text(memory_content)

        model = ProjectModel(temp_generic_project)
        content = model.read_memory_bank()

        assert content == memory_content

    def test_returns_none_for_missing_memory_bank(self, temp_generic_project):
        """ProjectModel returns None when AGENTS.md doesn't exist."""
        model = ProjectModel(temp_generic_project)
        content = model.read_memory_bank()

        assert content is None

    def test_reads_project_metadata(self, temp_generic_project):
        """ProjectModel reads project metadata from pyproject.toml."""
        model = ProjectModel(temp_generic_project)

        assert model.name == "test-project"
        assert model.root_path == temp_generic_project

    def test_get_accessible_files_for_architect(self, temp_generic_project):
        """ProjectModel returns accessible files for architect agent."""
        # Create some files
        (temp_generic_project / "README.md").write_text("# README")
        (temp_generic_project / "docs" / "architecture.md").write_text("# Architecture")
        (temp_generic_project / "docs" / "specs" / "auth.md").write_text("# Auth spec")

        model = ProjectModel(temp_generic_project)
        accessible = model.get_accessible_files("architect")

        # Architect should see README, docs/, and existing specs
        filenames = {p.name for p in accessible}
        assert "README.md" in filenames or any("README" in str(p) for p in accessible)

    def test_get_accessible_files_for_test_writer(self, temp_generic_project):
        """ProjectModel returns accessible files for test-writer agent."""
        model = ProjectModel(temp_generic_project)
        accessible = model.get_accessible_files("test_writer")

        # Test writer should see the spec
        assert isinstance(accessible, list)

    def test_test_writer_cannot_see_src_files(self, temp_generic_project):
        """CDAD Principle 3: test_writer must NOT see implementation source."""
        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        impl_file = src_dir / "implementation.py"
        impl_file.write_text("def add(a, b): return a + b\n")

        model = ProjectModel(temp_generic_project)
        accessible = model.get_accessible_files("test_writer")

        assert impl_file not in accessible
        assert not any(p.is_relative_to(src_dir) for p in accessible)

    def test_implementer_can_see_src_files(self, temp_generic_project):
        """Implementer must see src/ to write code."""
        src_dir = temp_generic_project / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        impl_file = src_dir / "implementation.py"
        impl_file.write_text("# impl\n")

        model = ProjectModel(temp_generic_project)
        accessible = model.get_accessible_files("implementer")

        assert impl_file in accessible

    def test_unknown_agent_type_returns_only_common_files(self, temp_generic_project):
        """Unknown agent_type falls back to README + docs only."""
        (temp_generic_project / "src").mkdir(exist_ok=True)
        (temp_generic_project / "src" / "secret.py").write_text("x = 1")

        model = ProjectModel(temp_generic_project)
        accessible = model.get_accessible_files("nonexistent_role")

        assert all("src" not in p.parts for p in accessible)

    def test_initialize_with_nonexistent_path(self, tmp_path):
        """ProjectModel raises error when initialized with nonexistent path."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(FileNotFoundError):
            ProjectModel(nonexistent)

    def test_project_model_attributes(self, temp_generic_project):
        """ProjectModel has expected attributes."""
        model = ProjectModel(temp_generic_project)

        assert hasattr(model, "root_path")
        assert hasattr(model, "framework")
        assert hasattr(model, "name")
        assert isinstance(model.root_path, Path)
        assert isinstance(model.framework, str)
        assert isinstance(model.name, str)
