"""Shared reader for generated OpenCode V2 permission frontmatter."""
from __future__ import annotations

from typing import Any

import re


def permissions(agent_text: str) -> list[dict[str, Any]]:
    """Return V2 permission entries in serialized order."""
    if not agent_text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    _, raw, _ = agent_text.split("---", 2)
    entries: list[dict[str, str]] = []
    active: dict[str, str] | None = None
    in_permissions = False
    for line in raw.splitlines():
        if line == "permissions:":
            in_permissions = True
            continue
        if in_permissions and line and not line.startswith(" ") and not line.startswith("#"):
            break
        if not in_permissions:
            continue
        if match := re.fullmatch(r"  - action: (.+)", line):
            active = {"action": match.group(1).strip(" '\""), "resource": "", "effect": ""}
            entries.append(active)
        elif active is not None:
            match = re.fullmatch(r"    (resource|effect): (.*)", line)
            if match:
                active[match.group(1)] = match.group(2).strip(" '\"")
    return entries
