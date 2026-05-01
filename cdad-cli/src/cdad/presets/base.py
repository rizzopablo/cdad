"""Preset dataclass shared across framework presets."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class Preset:
    """A framework preset.

    Attributes:
        name: Framework identifier ("generic", "odoo", "django", ...).
        manifest_files: Files whose presence at the project root identifies the framework.
        source_dirs: Conventional source directories for this framework.
        test_dirs: Conventional test directories.
        spec_dirs: Where CDAD specs live (almost always docs/specs).
    """

    name: str
    manifest_files: List[str]
    source_dirs: List[str] = field(default_factory=lambda: ["src"])
    test_dirs: List[str] = field(default_factory=lambda: ["tests"])
    spec_dirs: List[str] = field(default_factory=lambda: ["docs/specs"])

    def matches(self, root_path: Path) -> bool:
        """Return True if this preset's manifest files exist at root_path."""
        return any((root_path / m).exists() for m in self.manifest_files)
