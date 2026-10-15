#!/usr/bin/env python3
"""cdad-version-check.py — ONE version check for a CDAD project.

Answers a single question: are the **project**, the **agents** and the **CLI**
the same version? It composes the pieces the product already offers (005-005
PD-14/INV-7) into one thing to run:

- **project** — the version recorded by the project's derived agents
  (`<project-root>/.opencode/agents/.cdad-derived.json` → `source_version`),
  i.e. the version of the agents the project loaded.
- **agents** — the `version.txt` marker at the installation root behind those
  derived agents (`source_dir` of the same manifest).
- **CLI** — the `version.txt` marker at the installation root of the skill that
  hosts this script (the CLI travels with the `cdad-cycle` skill tree).
- **Claude Code** (declared, additive) — the `version.txt` marker at the
  installation root behind the **Claude Code** agents (`<root>/.claude/agents`),
  resolved from the project's activation registry when it exists and otherwise
  from the runtime's global Claude Code agents directory. It takes part in the
  verdict **only when a Claude Code installation is detectable**; when none is,
  it declares the absence and the four verdicts/`rc` are unchanged. It never
  crosses an installation boundary (F2) and never reads the OpenCode derived
  manifest to infer this side.

Every marker is read **at the installation root of its own tree, and only
there**: the search never walks up across an installation boundary (F2). So a
**development checkout** — whose tree declares no `version.txt` — reports
`UNKNOWN` instead of borrowing an unrelated (e.g. global) installation's marker.

It prints exactly one of four verdicts, each with its own exit code; **only
`COHERENT` is "ok"**:

| verdict | rc | meaning |
|---|---|---|
| `COHERENT` | 0 | project, agents and CLI share the same version |
| `DRIFT` | 1 | the three are NOT the same version |
| `NO-PROJECT-AGENTS` | 4 | nothing loaded yet to compare (version NOT verified) |
| `UNKNOWN` | 3 | an installation version marker is missing (version NOT verified) |

A consumer that inspects `$?` must treat **any non-zero** code as "version not
verified as coherent" (F6).

What it verifies: version coherence across project / agents / CLI.
What it does NOT verify: it does not run the suite, does not validate the
policy, and does not re-read the skill text a running session already loaded.
Read-only: it writes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DERIVED_MANIFEST_REL = Path(".opencode") / "agents" / ".cdad-derived.json"
VERSION_MARKER = "version.txt"

# Installation layouts of the installer (install.sh): the agents land at
# `<root>/.config/opencode/agents`; the skill tree at
# `<root>/.config/opencode/skills/cdad-cycle/`, `<root>/.agents/skills/cdad-cycle/`
# or `<root>/.claude/skills/cdad-cycle/`. The root is the boundary the marker
# search must not cross (mirrors `cdad_packet.py _installation_root`).
OPENCODE_AGENTS_SUBDIR = (".config", "opencode", "agents")
SKILL_TREE_SUFFIX = ("cdad-cycle", "scripts")

# The Claude Code leg (PD-3, additive): the agents land at `<root>/.claude/agents`
# (install.sh) and the project may declare the adopted root in the activation
# registry that `cdad-activate.py` writes.
CLAUDE_AGENTS_SUBDIR = (".claude", "agents")
ACTIVATION_REGISTRY_REL = Path(".cdad") / "activation.json"

EXIT_COHERENT = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2
EXIT_UNKNOWN = 3
EXIT_NO_PROJECT_AGENTS = 4


def _read_version_marker(directory: Path) -> str | None:
    marker = directory / VERSION_MARKER
    try:
        text = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _agents_installation_root(source_dir: Path) -> Path:
    """Installation root behind an OpenCode agents directory (PD-14).

    The installer lays the agents out at `<root>/.config/opencode/agents`, so
    the root is `parents[2]`; any other layout has no boundary to cross and the
    marker, if any, sits next to it. Mirrors `cdad_packet.py _installation_root`.
    """
    parts = source_dir.parts
    if len(parts) >= 3 and parts[-3:] == OPENCODE_AGENTS_SUBDIR:
        return source_dir.parents[2]
    return source_dir


def _skill_installation_root(script: Path) -> Path | None:
    """Installation root of the tree that hosts this script, or None when the
    script does not live in a recognizable `skills/cdad-cycle/scripts` layout.

    The installer places the skill at `<root>/.config/opencode/skills/cdad-cycle/`,
    `<root>/.agents/skills/cdad-cycle/` or `<root>/.claude/skills/cdad-cycle/`.
    The root is the directory that CONTAINS the skills container — the boundary
    the marker search must not cross. A development checkout maps to its repo
    root, which declares no `version.txt`, so the CLI version is `UNKNOWN`
    there, never the global installation's marker (F2).
    """
    resolved = script.resolve()
    if resolved.parent.parts[-2:] != SKILL_TREE_SUFFIX:
        return None
    skills_dir = resolved.parents[2]  # file -> scripts -> cdad-cycle -> skills
    container = skills_dir.parent
    if container.name == "opencode" and container.parent.name == ".config":
        return skills_dir.parents[2]  # <root>/.config/opencode/skills -> <root>
    if container.name in {".agents", ".claude"}:
        return skills_dir.parents[1]  # <root>/.agents|.claude/skills -> <root>
    return container  # dev checkout / extra dir: the dir that contains `skills`


def _claude_code_installation_root(project_root: Path) -> Path | None:
    """Installation root behind the Claude Code agents, or None when no Claude
    Code installation is detectable (PD-3).

    The root is resolved from the project's activation registry when it exists
    and declares a Claude Code installation (`.cdad/activation.json` →
    `adopted_root`, the registry `cdad-activate.py` writes) and otherwise from
    the runtime's global Claude Code agents directory (`<home>/.claude/agents`,
    the layout install.sh deploys). A Claude Code installation is "detectable"
    when its agents directory (`<root>/.claude/agents`) exists. It reads only the
    marker of that root: it never walks up across an installation boundary (F2)
    and never reads the OpenCode derived manifest to infer this side.
    """
    registry = project_root / ACTIVATION_REGISTRY_REL
    try:
        document = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        document = None
    if isinstance(document, dict):
        adopted = document.get("adopted_root")
        if isinstance(adopted, str) and adopted.strip():
            root = Path(adopted).expanduser()
            if root.joinpath(*CLAUDE_AGENTS_SUBDIR).is_dir():
                return root
    agents_dir = Path.home().joinpath(*CLAUDE_AGENTS_SUBDIR)
    if not agents_dir.is_dir():
        return None
    return agents_dir.parents[1]  # <root>/.claude/agents -> <root>


def _claude_code_version(root: Path) -> str | None:
    """Marker of a Claude Code installation root (PD-3).

    Reads the marker at the installation root; if absent, the copy next to the
    agents directory (`<root>/.claude/agents/version.txt`).
    """
    return (_read_version_marker(root)
            or _read_version_marker(root.joinpath(*CLAUDE_AGENTS_SUBDIR)))


def _project_version(project_root: Path) -> tuple[str | None, Path | None]:
    manifest_path = project_root / DERIVED_MANIFEST_REL
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(document, dict):
        return None, None
    version = document.get("source_version")
    source_dir = document.get("source_dir")
    version = version.strip() if isinstance(version, str) and version.strip() else None
    origin = Path(source_dir) if isinstance(source_dir, str) and source_dir.strip() else None
    return version, origin


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cdad-version-check.py", description=__doc__.splitlines()[0])
    parser.add_argument("--project-root", default=".", help="project root (default: current directory)")
    parser.add_argument(
        "--install-root",
        default=None,
        help="installation root to compare against (default: derived from the project manifest and this skill)",
    )
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser()
    if not project_root.is_dir():
        print(f"ERROR: --project-root is not an existing directory: {project_root}", file=sys.stderr)
        return EXIT_USAGE

    project_version, source_dir = _project_version(project_root)

    cc_root = _claude_code_installation_root(project_root)
    cc_version = _claude_code_version(cc_root) if cc_root is not None else None

    if args.install_root:
        override = Path(args.install_root).expanduser()
        marker = (_read_version_marker(_agents_installation_root(override))
                  if override.is_dir() else None)
        agents_version = marker
        cli_version = marker
    else:
        agents_version = (_read_version_marker(_agents_installation_root(source_dir))
                          if source_dir else None)
        cli_root = _skill_installation_root(Path(__file__))
        cli_version = _read_version_marker(cli_root) if cli_root else None

    print("CDAD version check — project / agents / CLI / Claude Code")
    print(f"  project: {project_version or '(none: no derived agents recorded yet)'}")
    print(f"  agents:  {agents_version or '(no version.txt found)'}")
    print(f"  CLI:     {cli_version or '(no version.txt found)'}")
    if cc_root is None:
        print("  claude-code: (not detected: no Claude Code agents installation)")
    else:
        print(f"  claude-code: {cc_version or '(no version.txt found)'}")

    if project_version is None:
        print("verdict: NO-PROJECT-AGENTS (nothing loaded yet to compare; version NOT verified)")
        return EXIT_NO_PROJECT_AGENTS
    if agents_version is None or cli_version is None:
        print("verdict: UNKNOWN (an installation version marker is missing; version NOT verified)")
        return EXIT_UNKNOWN
    if cc_root is not None and cc_version is None:
        print("verdict: UNKNOWN (the Claude Code installation version marker is missing; version NOT verified)")
        return EXIT_UNKNOWN
    compared = {project_version, agents_version, cli_version}
    if cc_root is not None:
        compared.add(cc_version)
    if len(compared) == 1:
        print("verdict: COHERENT (project, agents, CLI and Claude Code are the same version)")
        return EXIT_COHERENT
    print("verdict: DRIFT (project, agents, CLI and Claude Code are NOT the same version)")
    return EXIT_DRIFT


if __name__ == "__main__":
    raise SystemExit(main())
