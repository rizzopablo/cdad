"""Shared oracle helpers for the installer's always-deploy-with-backup contract.

Contract (owner decision 2026-11-19): `install.sh` always writes the current
staging bytes (plus the user's `model:` overlay on agents) to every managed
destination. When the existing destination differs from what is about to be
written, the current bytes are saved as a backup BEFORE overwriting; a
difference never stops the install. Symlinks / non-regular files at a
destination are still never written through.

The contract does not fix WHERE the backup lives or how it is named, so the
oracle is location-agnostic: a backup is any regular, non-symlink file under
the install root, other than the destination itself, whose bytes are exactly
the previous content. Black-box: only published effects are inspected.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path


def snapshot_tree(root: Path) -> dict[str, str]:
    """`{relative path: sha256 or 'symlink:<target>'}` for every entry under root."""
    out: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                out[rel] = f"symlink:{os.readlink(path)}"
            elif path.is_file():
                out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                out[rel] = "dir"
    return out


def backups_holding(root: Path, destination: Path, previous: bytes) -> list[Path]:
    """Backups of `destination`: other regular files whose bytes are `previous`."""
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            if path == destination or path.is_symlink() or not path.is_file():
                continue
            try:
                if path.read_bytes() == previous:
                    found.append(path)
            except OSError:
                continue
    return sorted(found)
