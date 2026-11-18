"""Read-only project-layout resolution (019-004 §4).

Resolves where the CDAD methodology artifacts live in a product repository.
Placement only: a successful resolution never validates state, policy or
execution, never creates anything, and never grants permissions.

Precedence (§4.2):
1. A valid locator ``.cdad/project-layout.json`` is exclusive.
2. Otherwise an exact legacy marker (``docs/.cdad-state.json`` or
   ``docs/cdad-policy.json``) selects ``docs/`` without writing a locator.
3. Otherwise insufficient-but-present initialization evidence is ambiguous.
4. Otherwise, only with an explicit bootstrap request, propose ``cdad/``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

LOCATOR_RELPATH = Path(".cdad") / "project-layout.json"
OPERATIONAL_DIR = Path(".cdad")
LOCATOR_FIELDS = frozenset({"schema_version", "methodology_dir"})
LOCATOR_VERSION = 1
LEGACY_DIR = "docs"
LEGACY_MARKERS = (Path("docs") / ".cdad-state.json", Path("docs") / "cdad-policy.json")
BOOTSTRAP_DIR = "cdad"
MEMORY_BANK_FILES = ("projectbrief.md", "systemPatterns.md", "activeContext.md", "progress.md", "landscape.md")
CONTINUITY_STORE = "continuity"
GUARD_STORE = "guards"
# Operational record stores under an execution directory: written by the
# continuity and guard layers, never initialization evidence (decisions 019-004).
OPERATIONAL_RECORD_STORES = frozenset({CONTINUITY_STORE, GUARD_STORE})
# Named locations whose direct entries are initialization evidence (spec-amendment-001).
NAMED_ENTRY_LOCATIONS = (".cdad/packets", ".cdad/inbox", ".cdad/runtime/results", ".cdad/publication")


class LayoutError(ValueError):
    """A layout cannot be resolved; the message is the stderr cause."""


class AmbiguousLayoutError(LayoutError):
    """Initialization evidence is present without an admitted layout (§4.2, item 3)."""


def resolve_layout(project_root: str | os.PathLike[str], *, for_bootstrap: bool = False) -> dict[str, Any]:
    root = _canonical_root(project_root)
    locator = root / LOCATOR_RELPATH
    if os.path.lexists(locator):
        methodology_dir = _read_locator(root, locator)
        return _result(root, "registered", methodology_dir)
    if any(os.path.lexists(root / marker) for marker in LEGACY_MARKERS):
        return _result(root, "legacy", LEGACY_DIR)
    evidence = _ambiguity_evidence(root)
    if evidence:
        raise _ambiguous(evidence)
    if for_bootstrap:
        return _result(root, "new", BOOTSTRAP_DIR)
    raise LayoutError(
        "uninitialized: no locator, legacy marker or bootstrap request; "
        "run with --for-bootstrap only after confirming CDAD does not already exist elsewhere"
    )


def registered_methodology_dir(project_root: str | os.PathLike[str]) -> str | None:
    """Return the validated methodology directory of a REGISTERED layout, or None.

    None means no locator exists (legacy/uninitialized/ambiguous placement is
    decided by ``resolve_layout``). An invalid locator raises ``LayoutError``
    and never falls back to ``docs/`` (§4.2).
    """
    root = _canonical_root(project_root)
    locator = root / LOCATOR_RELPATH
    if not os.path.lexists(locator):
        return None
    return _read_locator(root, locator)


def methodology_base(project_root: str | os.PathLike[str]) -> str:
    """The repository-relative methodology base used by operational consumers.

    This is the single resolution shared by every operational consumer (019-004
    §4.2): a registered locator is exclusive, an exact legacy marker selects
    ``docs/``, and anything else raises ``LayoutError`` (ambiguous or
    uninitialized). It never returns ``docs/`` on insufficient evidence.
    """
    return resolve_layout(project_root)["methodology_dir"]


def optional_methodology_base(project_root: str | os.PathLike[str]) -> str | None:
    """The base for OPTIONAL reads (a project state or policy that may be absent).

    A registered layout is exclusive and an invalid locator still raises. An
    exact legacy marker selects ``docs/``. Insufficient initialization evidence
    is ambiguous and raises ``AmbiguousLayoutError`` (§4.2, item 3): it is never
    treated as absence and never selects ``docs/``. Only a genuinely
    uninitialized project (no locator, marker or evidence) returns None.
    """
    registered = registered_methodology_dir(project_root)
    if registered is not None:
        return registered
    root = _canonical_root(project_root)
    if any(os.path.lexists(root / marker) for marker in LEGACY_MARKERS):
        return LEGACY_DIR
    evidence = _ambiguity_evidence(root)
    if evidence:
        raise _ambiguous(evidence)
    return None


def state_relpath(project_root: str | os.PathLike[str]) -> str:
    return f"{methodology_base(project_root)}/.cdad-state.json"


def policy_relpath(project_root: str | os.PathLike[str]) -> str:
    return f"{methodology_base(project_root)}/cdad-policy.json"


def _canonical_root(project_root: str | os.PathLike[str]) -> Path:
    raw = os.fspath(project_root)
    if not raw:
        raise LayoutError("--project-root must be a non-empty path")
    root = Path(os.path.realpath(raw))
    if not root.is_dir():
        raise LayoutError(f"--project-root must be an existing directory: {raw}")
    return root


def _result(root: Path, source: str, methodology_dir: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project_root": str(root),
        "source": source,
        "methodology_dir": methodology_dir,
        "state": f"{methodology_dir}/.cdad-state.json",
        "policy": f"{methodology_dir}/cdad-policy.json",
    }


def _read_locator(root: Path, locator: Path) -> str:
    try:
        text = locator.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise LayoutError(f"cannot read locator {LOCATOR_RELPATH.as_posix()}: {exc}") from exc
    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except ValueError as exc:
        raise LayoutError(f"malformed locator {LOCATOR_RELPATH.as_posix()}: {exc}") from exc
    if not isinstance(document, dict):
        raise LayoutError("locator must be a JSON object")
    if set(document) != LOCATOR_FIELDS:
        raise LayoutError(
            f"locator fields must be exactly {sorted(LOCATOR_FIELDS)}; found {sorted(document)}"
        )
    version = document["schema_version"]
    if type(version) is not int or version != LOCATOR_VERSION:
        raise LayoutError(f"unsupported locator schema_version: {version!r}")
    methodology_dir = document["methodology_dir"]
    if not isinstance(methodology_dir, str):
        raise LayoutError("locator methodology_dir must be a string")
    _check_relative_path(methodology_dir)
    _check_target(root, methodology_dir)
    return methodology_dir


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _check_relative_path(methodology_dir: str) -> None:
    if not methodology_dir:
        raise LayoutError("locator methodology_dir must be non-empty")
    if "\\" in methodology_dir or "\x00" in methodology_dir:
        raise LayoutError(f"locator methodology_dir must not contain backslashes or NUL: {methodology_dir!r}")
    if methodology_dir.startswith("/"):
        raise LayoutError(f"locator methodology_dir must be repository-relative, not absolute: {methodology_dir!r}")
    parts = methodology_dir.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise LayoutError(
            f"locator methodology_dir must be normalized (no empty, '.' or '..' components): {methodology_dir!r}"
        )
    if parts[0] == OPERATIONAL_DIR.name:
        raise LayoutError(f"locator methodology_dir must not be or live beneath {OPERATIONAL_DIR.as_posix()}/")


def _check_target(root: Path, methodology_dir: str) -> None:
    target = Path(os.path.realpath(root / methodology_dir))
    operational = Path(os.path.realpath(root / OPERATIONAL_DIR))
    if not target.is_relative_to(root):
        raise LayoutError(f"locator methodology_dir escapes the repository root through a symlink: {methodology_dir!r}")
    if target == root:
        raise LayoutError(f"locator methodology_dir must not resolve to the repository root: {methodology_dir!r}")
    if target == operational or target.is_relative_to(operational):
        raise LayoutError(f"locator methodology_dir must not be or live beneath {OPERATIONAL_DIR.as_posix()}/: {methodology_dir!r}")
    if os.path.lexists(target) and not target.is_dir():
        raise LayoutError(f"locator methodology_dir exists and is not a directory: {methodology_dir!r}")


def _ambiguous(evidence: list[str]) -> AmbiguousLayoutError:
    return AmbiguousLayoutError(
        "ambiguous layout: no locator or legacy marker, but initialization evidence "
        f"is present ({', '.join(evidence)}); register the layout explicitly before use"
    )


def _ambiguity_evidence(root: Path) -> list[str]:
    """Insufficient-but-present initialization evidence (§4.2, item 3).

    The closed list (spec-amendment-001) is checked by fixed location only,
    never by recursive discovery:

    - Memory Bank files under ``docs/``, ``docs/specs``, ``docs/epics`` and
      an unregistered ``cdad/``.
    - Any direct entry under ``.cdad/packets`` (an empty directory is not
      evidence).
    - Any execution record under ``.cdad/executions/<id>/`` other than the
      continuity and guard stores (one level deep).
    - Any entry under ``.cdad/inbox``, ``.cdad/runtime/results`` and
      ``.cdad/publication``.

    Anything under ``.cdad/`` that the list does not name (the locator,
    orchestration scratch, other operational files) is never examined.
    """
    found = [f"docs/{name}" for name in MEMORY_BANK_FILES if os.path.lexists(root / LEGACY_DIR / name)]
    found += [rel for rel in ("docs/specs", "docs/epics") if os.path.lexists(root / rel)]
    found += _execution_record_evidence(root)
    for rel in NAMED_ENTRY_LOCATIONS:
        found += _named_location_evidence(root, rel)
    if os.path.lexists(root / BOOTSTRAP_DIR):
        found.append(f"{BOOTSTRAP_DIR}/")
    return found


def _named_location_evidence(root: Path, rel: str) -> list[str]:
    """Evidence from one named location: any direct entry, or a non-directory.

    An empty directory is not evidence (the runtime may pre-create it). A path
    that exists but is not a directory (file or dangling symlink) fails closed,
    as the executions branch does.
    """
    location = root / rel
    if not os.path.lexists(location):
        return []
    if not location.is_dir():
        return [rel]
    return [f"{rel}/{entry.name}" for entry in sorted(location.iterdir())]


def _execution_record_evidence(root: Path) -> list[str]:
    executions = root / OPERATIONAL_DIR / "executions"
    if not executions.is_dir():
        return [f"{OPERATIONAL_DIR.as_posix()}/executions"] if os.path.lexists(executions) else []
    found = []
    for entry in sorted(executions.iterdir()):
        rel = f"{OPERATIONAL_DIR.as_posix()}/executions/{entry.name}"
        if not entry.is_dir():
            found.append(rel)
        elif any(child.name not in OPERATIONAL_RECORD_STORES for child in entry.iterdir()):
            found.append(rel)
    return found


def _cli(argv: list[str] | None = None) -> int:
    """Print the effective methodology base for a shell consumer (fail closed).

    ``cdad_layout.py base --project-root ROOT``: exit 0 with the base on stdout,
    exit 2 with the cause on stderr when a registered layout is invalid. Never
    falls back to ``docs/`` on error.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="cdad_layout.py")
    sub = parser.add_subparsers(dest="command", required=True)
    base = sub.add_parser("base", help="print the effective methodology base")
    base.add_argument("--project-root", required=True)
    args = parser.parse_args(argv)
    try:
        print(methodology_base(args.project_root))
    except LayoutError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
