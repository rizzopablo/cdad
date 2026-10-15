#!/usr/bin/env python3
"""Thin repository wrapper for the installable cdad-cycle context-meter CLI."""

from __future__ import annotations

from pathlib import Path
import runpy


CANONICAL = Path(__file__).resolve().parents[1] / "skills" / "cdad-cycle" / "scripts" / "cdad_context_meter.py"
runpy.run_path(str(CANONICAL), run_name="__main__")
