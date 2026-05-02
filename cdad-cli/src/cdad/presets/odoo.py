"""Odoo addon preset."""

from cdad.presets.base import Preset

ODOO = Preset(
    name="odoo",
    manifest_files=["__manifest__.py", "__openerp__.py"],
    source_dirs=["models"],
    test_dirs=["tests"],
)
