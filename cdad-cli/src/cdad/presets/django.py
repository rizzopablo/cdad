"""Django preset."""

from cdad.presets.base import Preset

DJANGO = Preset(
    name="django",
    manifest_files=["manage.py"],
    source_dirs=["."],
    test_dirs=["tests"],
)
