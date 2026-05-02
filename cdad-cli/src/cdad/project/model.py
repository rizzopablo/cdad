"""ProjectModel reads project structure and detects frameworks."""

from pathlib import Path
from typing import List, Optional
import toml

from cdad.config import MEMORY_BANK_FILE
from cdad.presets import REGISTRY


class ProjectModel:
    """Model for project structure and framework detection."""

    def __init__(self, root_path: Path):
        """Initialize ProjectModel.

        Args:
            root_path: Root directory of the project.

        Raises:
            FileNotFoundError: If root_path doesn't exist.
        """
        root_path = Path(root_path)
        if not root_path.exists():
            raise FileNotFoundError(f"Project root not found: {root_path}")

        self.root_path = root_path
        self.framework = self.detect_framework()
        self.name = self._read_project_name()

    def detect_framework(self) -> str:
        """Detect the project framework via the preset registry.

        Returns:
            Framework type: "odoo", "django", "generic", or "unknown".
        """
        for preset in REGISTRY:
            if preset.matches(self.root_path):
                return preset.name
        return "unknown"

    def list_spec_files(self) -> List[Path]:
        """List all spec files in docs/specs/.

        Returns:
            List of Path objects for spec files.
        """
        specs_dir = self.root_path / "docs" / "specs"
        if not specs_dir.exists():
            return []

        return sorted([f for f in specs_dir.glob("*.md")])

    def list_test_files(self) -> List[Path]:
        """List all test files in tests/.

        Returns:
            List of Path objects for test files.
        """
        tests_dir = self.root_path / "tests"
        if not tests_dir.exists():
            return []

        return sorted([f for f in tests_dir.glob("test_*.py")])

    def read_spec(self, spec_name: str) -> str:
        """Read content of a specific spec file.

        Args:
            spec_name: Name of the spec file (e.g., "auth.md").

        Returns:
            Content of the spec file.

        Raises:
            FileNotFoundError: If spec file doesn't exist.
        """
        spec_path = self.root_path / "docs" / "specs" / spec_name
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        return spec_path.read_text(encoding="utf-8")

    def read_memory_bank(self) -> Optional[str]:
        """Read the memory bank (AGENTS.md).

        Returns:
            Content of AGENTS.md, or None if it doesn't exist.
        """
        memory_bank = self.root_path / MEMORY_BANK_FILE
        if not memory_bank.exists():
            return None

        return memory_bank.read_text(encoding="utf-8")

    # Per-agent file-access policy. Each entry declares whether that agent
    # may see specs, existing tests, and the implementation source tree.
    # CDAD Principle 3: the test_writer MUST NOT see implementation source —
    # otherwise it aligns tests to existing code instead of to the contract.
    _AGENT_ACCESS_POLICY = {
        "architect":   {"specs": True,  "tests": False, "src": False, "discovery": True},
        "test_writer": {"specs": True,  "tests": True,  "src": False, "discovery": False},
        "implementer": {"specs": True,  "tests": True,  "src": True,  "discovery": False},
        "reviewer":    {"specs": True,  "tests": True,  "src": True,  "discovery": False},
    }

    def get_accessible_files(self, agent_type: str) -> List[Path]:
        """Get list of files accessible to an agent.

        Note: each agent class owns its own ``get_accessible_files()``; this
        method is a thin façade used by the CLI and tests when only the agent
        type string is available. Policy lives in ``_AGENT_ACCESS_POLICY``.

        Args:
            agent_type: Type of agent (e.g., "architect", "test_writer").

        Returns:
            List of accessible file paths, deduplicated and sorted.
        """
        accessible: List[Path] = []

        # All agents see README and docs/
        if (self.root_path / "README.md").exists():
            accessible.append(self.root_path / "README.md")
        docs_dir = self.root_path / "docs"
        if docs_dir.exists():
            accessible.extend(sorted(docs_dir.rglob("*.md")))

        policy = self._AGENT_ACCESS_POLICY.get(agent_type, {})
        if policy.get("specs"):
            accessible.extend(self.list_spec_files())
        if policy.get("tests"):
            accessible.extend(self.list_test_files())
        if policy.get("src") and (self.root_path / "src").exists():
            accessible.extend(sorted((self.root_path / "src").rglob("*.py")))
        if policy.get("discovery"):
            discovery = self.root_path / "docs" / "discovery.md"
            if discovery.exists():
                accessible.append(discovery)

        return sorted(set(accessible))

    def _read_project_name(self) -> str:
        """Read project name from configuration.

        Returns:
            Project name from pyproject.toml or "unnamed-project".
        """
        pyproject = self.root_path / "pyproject.toml"
        if pyproject.exists():
            try:
                data = toml.load(pyproject)
                return data.get("project", {}).get("name", "unnamed-project")
            except Exception:
                pass

        # Fallback to directory name
        return self.root_path.name
