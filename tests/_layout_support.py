"""Shared 020-001 layout fixture support (not a test module).

One place for the declared-layout constants used by the project builders:

- the declaration lives at the fixed path ``cdad/project-layout.json``
  (schema 2: ``schema_version``, ``methodology_dir``, ``operational_dir``);
- operational records (packets, executions, inbox, runtime, locks, local
  files, temporary root) live under the declared repository-relative
  ``operational_dir``; the default for a project is ``.cdad-execution``.

Fixtures keep their state/policy under ``docs/`` (the methodology directory
the legacy fixtures always used), so the declaration registers ``docs``.
"""
from __future__ import annotations

import json
from pathlib import Path

OPERATIONAL_DIR = ".cdad-execution"
DECLARATION_REL = "cdad/project-layout.json"
OLD_OPERATIONAL_DIR = ".cdad"


def declaration_document(methodology_dir: str = "docs",
                         operational_dir: str = OPERATIONAL_DIR) -> dict:
    return {
        "schema_version": 2,
        "methodology_dir": methodology_dir,
        "operational_dir": operational_dir,
    }


def write_declaration(root, methodology_dir: str = "docs",
                      operational_dir: str = OPERATIONAL_DIR) -> Path:
    """Write the schema-2 declaration at the fixed path under ``root``."""
    path = Path(root) / DECLARATION_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(declaration_document(methodology_dir, operational_dir),
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return path


def operational_root(root, operational_dir: str = OPERATIONAL_DIR) -> Path:
    return Path(root) / operational_dir
