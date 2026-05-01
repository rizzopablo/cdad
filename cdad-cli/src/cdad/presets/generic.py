"""Generic Python preset."""

from cdad.presets.base import Preset

GENERIC = Preset(
    name="generic",
    manifest_files=["setup.py", "pyproject.toml"],
    source_dirs=["src"],
    test_dirs=["tests"],
)
