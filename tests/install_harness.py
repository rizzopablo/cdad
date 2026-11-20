"""Shared minimal installer harness (maintenance, tests-only).

Most installer tests assert something about ONE or TWO files (overlay of
`model:`, an ownership entry, a backup, a symlink guard, dry-run, prune,
uninstall) but used to install the whole product (~140 source files deployed
to 3 runtimes) or copy the whole repository per class to get a mutable
staging. This module gives those tests a MINIMAL product root instead:

- `install.sh` and `scripts/` (the installer's own tooling, as in the repo);
- a minimal `build/staging` (three real agents per runtime — the ones the installer tests name — in
  total per runtime) with a `manifest.json` of the SAME shape as the real one
  (sha256 recomputed from the staged bytes the harness copies);
- `skills/<name>/SKILL.md` for each skill directory the installer expects.

Built ONCE per process from the real staging and cached under
`tests.product_staging.run_scoped_base()`. `minimal_product_root()` is
read-only by convention; a test that mutates staging takes
`fresh_product(parent)`, a cheap private copy (a few hundred KB).

Tests whose promise IS the whole product (all agents deployed, full-tree
`--check`) keep using `tests.product_staging.product_root()`.
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from tests.product_staging import REPO_ROOT, product_root, run_scoped_mkdtemp
from tests.suite_operation_markers import operation

# Agents copied (per runtime) into the minimal staging.
MINIMAL_AGENTS = ("cdad-reviewer.md", "cdad-architect.md", "cdad-test-writer.md")
# Skill directories the installer expects (documented in `install.sh --help`).
MINIMAL_SKILLS = (
    "cdad-cycle",
    "cdad-epic",
    "cdad-spec-and-test",
    "odoo-architect",
    "odoo-expert",
    "odoo-make-env",
    "odoo-reviewer",
    "odoo-test-writer",
)

_minimal: Path | None = None


def _build_minimal() -> Path:
    real = product_root()
    base = Path(run_scoped_mkdtemp("cdad-minimal-product-"))
    atexit.register(shutil.rmtree, str(base), ignore_errors=True)
    product = base / "product"
    product.mkdir()
    shutil.copy2(real / "install.sh", product / "install.sh")
    shutil.copytree(real / "scripts", product / "scripts", symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    real_manifest = json.loads((real / "build/staging/manifest.json").read_text())
    kept = []
    for entry in real_manifest["artifacts"]:
        name = Path(entry["file"]).name
        if name not in MINIMAL_AGENTS:
            continue
        src = real / "build/staging" / entry["file"]
        dst = product / "build/staging" / entry["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        kept.append(dict(entry, sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
    manifest = dict(real_manifest, artifacts=kept)
    (product / "build/staging/manifest.json").write_text(
        json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    for skill in MINIMAL_SKILLS:
        d = product / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: minimal harness skill\n---\n",
            encoding="utf-8")
    # One nested asset under cdad-cycle: a multi-level own source whose
    # deployment is mirrored into every runtime (prune/obsolete oracles retire it).
    adr = product / "skills/cdad-cycle/assets/adr-template/ADR.md"
    adr.parent.mkdir(parents=True)
    adr.write_text("# ADR template (minimal harness)\n", encoding="utf-8")
    return product


def minimal_product_root() -> Path:
    """Cached minimal product root (read-only by convention)."""
    global _minimal
    if _minimal is None:
        _minimal = _build_minimal()
    return _minimal


def fresh_product(parent: Path) -> Path:
    """A private mutable copy of the minimal product under `parent`."""
    dest = Path(parent) / "product"
    shutil.copytree(minimal_product_root(), dest, symlinks=True)
    return dest


def make_install_root(prefix: str = "cdad-install-root-") -> tempfile.TemporaryDirectory:
    """A temp install root; the caller owns `.cleanup()` / the context."""
    return tempfile.TemporaryDirectory(prefix=prefix)


def _run(product: Path, root: Path, args: tuple[str, ...], env_extra: dict | None):
    env = os.environ.copy()
    env["CDAD_INSTALL_ROOT"] = str(root)
    env["CDAD_SKILL_EXTRA_DIRS"] = ""
    if env_extra:
        env.update(env_extra)
    with operation("external.install"):
        proc = subprocess.run(
            ["bash", str(Path(product) / "install.sh"), *args],
            cwd=str(product), env=env, text=True, capture_output=True, check=False,
        )
    return proc.returncode, proc.stdout, proc.stderr


def run_install(product: Path, root: Path, *args: str, env: dict | None = None):
    return _run(product, root, args, env)


def run_check(product: Path, root: Path, *args: str, env: dict | None = None):
    return _run(product, root, ("--check", *args), env)


def run_uninstall(product: Path, root: Path, *args: str, env: dict | None = None):
    return _run(product, root, ("--uninstall", *args), env)
