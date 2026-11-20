"""Read-only project-layout resolution (019-004 §4, amended by 020-001).

Resolves where the CDAD methodology artifacts live in a product repository, and
which repository-relative directory holds the project's OPERATIONAL records.
Placement only: a successful resolution never validates state, policy or
execution, never creates anything, and never grants permissions.

Precedence (§4.2, 020-001 §Declaration):
1. A valid declaration ``cdad/project-layout.json`` (schema 2:
   ``schema_version``, ``methodology_dir``, ``operational_dir``) is exclusive.
2. Otherwise an exact legacy marker (``docs/.cdad-state.json`` or
   ``docs/cdad-policy.json``) selects ``docs/`` without writing a declaration.
3. Otherwise insufficient-but-present initialization evidence is ambiguous.
4. Otherwise, only with an explicit bootstrap request, propose ``cdad/``.

An UNMIGRATED project is refused before any operational write (020-001 PC-2):
the old locator ``.cdad/project-layout.json`` is still present, or the
declaration lacks ``operational_dir`` (schema 1), or a populated legacy
``.cdad/`` root remains. The rejection names the canonical migration guide and
never writes, converts or falls back silently.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# 020-001: fixed declaration path for every project, whatever its methodology
# placement, so discovery needs no prior knowledge of the methodology directory.
DECLARATION_RELPATH = Path("cdad") / "project-layout.json"
DECLARATION_FIELDS = frozenset({"schema_version", "methodology_dir", "operational_dir"})
DECLARATION_VERSION = 2
DEFAULT_OPERATIONAL_DIR = ".cdad-execution"
# The 019-004 locator and the operational root it registered: historical
# placements. They are MIGRATION signals here, never a registration source.
LEGACY_LOCATOR_RELPATH = Path(".cdad") / "project-layout.json"
LEGACY_OPERATIONAL_DIR = Path(".cdad")
MIGRATION_GUIDE_RELPATH = "skills/cdad-cycle/references/layout-migration.md"
LEGACY_DIR = "docs"
LEGACY_MARKERS = (Path("docs") / ".cdad-state.json", Path("docs") / "cdad-policy.json")
BOOTSTRAP_DIR = "cdad"
MEMORY_BANK_FILES = ("projectbrief.md", "systemPatterns.md", "activeContext.md", "progress.md", "landscape.md")


class LayoutError(ValueError):
    """A layout cannot be resolved; the message is the stderr cause."""


class AmbiguousLayoutError(LayoutError):
    """Initialization evidence is present without an admitted layout (§4.2, item 3)."""


class MigrationRequiredError(LayoutError):
    """The project still uses the legacy operational layout (020-001 PC-2)."""


def resolve_layout(project_root: str | os.PathLike[str], *, for_bootstrap: bool = False) -> dict[str, Any]:
    root = _canonical_root(project_root)
    _reject_unmigrated(root)
    declaration = root / DECLARATION_RELPATH
    if os.path.lexists(declaration):
        methodology_dir, _ = _read_declaration(root, declaration)
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

    None means no declaration exists (legacy/uninitialized/ambiguous placement is
    decided by ``resolve_layout``). An invalid declaration raises ``LayoutError``
    and never falls back to ``docs/`` (§4.2); an unmigrated project raises
    ``MigrationRequiredError`` (020-001 PC-2).
    """
    root = _canonical_root(project_root)
    _reject_unmigrated(root)
    declaration = root / DECLARATION_RELPATH
    if not os.path.lexists(declaration):
        return None
    return _read_declaration(root, declaration)[0]


def methodology_base(project_root: str | os.PathLike[str]) -> str:
    """The repository-relative methodology base used by operational consumers.

    This is the single resolution shared by every operational consumer (019-004
    §4.2): a registered declaration is exclusive, an exact legacy marker selects
    ``docs/``, and anything else raises ``LayoutError`` (ambiguous, unmigrated or
    uninitialized). It never returns ``docs/`` on insufficient evidence.
    """
    return resolve_layout(project_root)["methodology_dir"]


def operational_dir(project_root: str | os.PathLike[str]) -> str:
    """The repository-relative OPERATIONAL directory (020-001 PC-1).

    One shared accessor for every operational consumer: the declared
    ``operational_dir`` when a schema-2 declaration exists, else the default
    ``.cdad-execution`` (a legacy project that never wrote operational records,
    or a genuinely new project). An unmigrated project raises
    ``MigrationRequiredError`` before any write; an invalid declaration raises
    ``LayoutError`` and never falls back.
    """
    root = _canonical_root(project_root)
    _reject_unmigrated(root)
    declaration = root / DECLARATION_RELPATH
    if os.path.lexists(declaration):
        return _read_declaration(root, declaration)[1]
    return DEFAULT_OPERATIONAL_DIR


def optional_methodology_base(project_root: str | os.PathLike[str]) -> str | None:
    """The base for OPTIONAL reads (a project state or policy that may be absent).

    A registered layout is exclusive and an invalid declaration still raises. An
    exact legacy marker selects ``docs/``. Insufficient initialization evidence
    is ambiguous and raises ``AmbiguousLayoutError`` (§4.2, item 3): it is never
    treated as absence and never selects ``docs/``. Only a genuinely
    uninitialized project (no declaration, marker or evidence) returns None.
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


def _unmigrated_cause(root: Path) -> str | None:
    """020-001 §Declaration: why the project still uses the legacy operational layout.

    The three signals are fixed and cheap, in this order: the old locator, a
    declaration without ``operational_dir`` (schema 1), and a populated legacy
    ``.cdad/`` root (any file or symlink beneath it; an empty directory subtree
    is not populated).
    """
    if os.path.lexists(root / LEGACY_LOCATOR_RELPATH):
        return f"the old locator {LEGACY_LOCATOR_RELPATH.as_posix()} is still present"
    declaration = root / DECLARATION_RELPATH
    if os.path.lexists(declaration):
        document = _try_read_object(declaration)
        if isinstance(document, dict) and "operational_dir" not in document:
            return "the layout declaration has no operational_dir (schema 1)"
    legacy_entry = _legacy_entry(root)
    if legacy_entry is not None:
        return f"the legacy operational root {LEGACY_OPERATIONAL_DIR.as_posix()}/ still has entries ({legacy_entry})"
    return None


def _reject_unmigrated(root: Path) -> None:
    cause = _unmigrated_cause(root)
    if cause is None:
        return
    raise MigrationRequiredError(
        f"project not migrated: {cause}. The legacy {LEGACY_OPERATIONAL_DIR.as_posix()}/ "
        "operational directory must be migrated before any operational write: move it to "
        "the declared operational directory, update the declaration and ignore the "
        f"destination. Follow the canonical guide {MIGRATION_GUIDE_RELPATH}"
    )


def _legacy_entry(root: Path) -> str | None:
    """One entry beneath the legacy ``.cdad/`` root, or None when it is empty/absent.

    Files and symlinks count, at any depth; an empty directory subtree does not
    (a leftover ``.cdad/packets/`` from a cleanup is not a legacy store).
    """
    legacy = root / LEGACY_OPERATIONAL_DIR
    if not os.path.lexists(legacy):
        return None
    if not legacy.is_dir():
        return LEGACY_OPERATIONAL_DIR.as_posix()
    for current, dirnames, filenames in os.walk(legacy, followlinks=False):
        dirnames.sort()
        for name in sorted(filenames):
            return (Path(current) / name).relative_to(root).as_posix()
        for name in dirnames:
            entry = Path(current) / name
            if entry.is_symlink():
                return entry.relative_to(root).as_posix()
    return None


def _try_read_object(path: Path) -> Any:
    try:
        return json.loads(path.read_bytes().decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, ValueError):
        return None


def _read_declaration(root: Path, declaration: Path) -> tuple[str, str]:
    try:
        text = declaration.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise LayoutError(
            f"cannot read declaration {DECLARATION_RELPATH.as_posix()}: {exc}") from exc
    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except ValueError as exc:
        raise LayoutError(
            f"malformed declaration {DECLARATION_RELPATH.as_posix()}: {exc}") from exc
    if not isinstance(document, dict):
        raise LayoutError("declaration must be a JSON object")
    if set(document) != DECLARATION_FIELDS:
        raise LayoutError(
            f"declaration fields must be exactly {sorted(DECLARATION_FIELDS)}; "
            f"found {sorted(document)}"
        )
    version = document["schema_version"]
    if type(version) is not int or version != DECLARATION_VERSION:
        raise LayoutError(f"unsupported declaration schema_version: {version!r}")
    methodology_dir = document["methodology_dir"]
    operational_dir = document["operational_dir"]
    if not isinstance(methodology_dir, str):
        raise LayoutError("declaration methodology_dir must be a string")
    if not isinstance(operational_dir, str):
        raise LayoutError("declaration operational_dir must be a string")
    _check_relative_path(methodology_dir, "methodology_dir")
    _check_relative_path(operational_dir, "operational_dir")
    _check_targets(root, methodology_dir, operational_dir)
    return methodology_dir, operational_dir


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _check_relative_path(value: str, label: str) -> None:
    if not value:
        raise LayoutError(f"declaration {label} must be non-empty")
    if "\\" in value or "\x00" in value:
        raise LayoutError(f"declaration {label} must not contain backslashes or NUL: {value!r}")
    if value.startswith("/"):
        raise LayoutError(f"declaration {label} must be repository-relative, not absolute: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise LayoutError(
            f"declaration {label} must be normalized (no empty, '.' or '..' components): {value!r}"
        )
    if parts[0] == LEGACY_OPERATIONAL_DIR.name:
        raise LayoutError(
            f"declaration {label} must not be or live beneath "
            f"{LEGACY_OPERATIONAL_DIR.as_posix()}/: {value!r}"
        )


def _check_targets(root: Path, methodology_dir: str, operational_dir: str) -> None:
    methodology = Path(os.path.realpath(root / methodology_dir))
    operational = Path(os.path.realpath(root / operational_dir))
    for value, target, label in ((methodology_dir, methodology, "methodology_dir"),
                                 (operational_dir, operational, "operational_dir")):
        if not target.is_relative_to(root):
            raise LayoutError(
                f"declaration {label} escapes the repository root through a symlink: "
                f"{value!r}")
        if target == root:
            raise LayoutError(
                f"declaration {label} must not resolve to the repository root: {value!r}")
        if os.path.lexists(target) and not target.is_dir():
            raise LayoutError(
                f"declaration {label} exists and is not a directory: {value!r}")
    if methodology == operational or methodology.is_relative_to(operational):
        raise LayoutError(
            f"declaration methodology_dir must not be or live beneath the operational "
            f"directory: {methodology_dir!r}")
    if operational.is_relative_to(methodology):
        raise LayoutError(
            f"declaration operational_dir must not be or live beneath the methodology "
            f"directory: {operational_dir!r}")



def _ambiguous(evidence: list[str]) -> AmbiguousLayoutError:
    return AmbiguousLayoutError(
        "ambiguous layout: no locator or legacy marker, but initialization evidence "
        f"is present ({', '.join(evidence)}); register the layout explicitly before use"
    )


def _ambiguity_evidence(root: Path) -> list[str]:
    """Insufficient-but-present initialization evidence (§4.2, item 3).

    The closed list (spec-amendment-001, 020-001) is checked by fixed location
    only, never by recursive discovery:

    - Memory Bank files under ``docs/``, ``docs/specs`` and ``docs/epics``.
    - An unregistered ``cdad/`` directory.

    A populated legacy ``.cdad/`` root is NOT ambiguity: it is an unmigrated
    project and is rejected earlier with the migration guide (020-001 PC-2).
    """
    found = [f"docs/{name}" for name in MEMORY_BANK_FILES if os.path.lexists(root / LEGACY_DIR / name)]
    found += [rel for rel in ("docs/specs", "docs/epics") if os.path.lexists(root / rel)]
    if os.path.lexists(root / BOOTSTRAP_DIR):
        found.append(f"{BOOTSTRAP_DIR}/")
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
