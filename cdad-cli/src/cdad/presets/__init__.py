"""Framework presets for CDAD CLI.

Each preset describes how to detect and lay out a framework. The registry
defines detection order — first match wins.
"""

from cdad.presets.base import Preset
from cdad.presets.generic import GENERIC
from cdad.presets.django import DJANGO
from cdad.presets.odoo import ODOO

REGISTRY: list[Preset] = [ODOO, DJANGO, GENERIC]

__all__ = ["Preset", "REGISTRY", "GENERIC", "DJANGO", "ODOO"]
