#!/usr/bin/env python3
"""Portabilidad de staging (review-t1, hallazgo lateral para T6 / PD-12).

Los tests que instalan o leen el manifest de staging dependían de
`build/staging/manifest.json` presente en el checkout real (está ignorado por
git): en un checkout limpio, 6+ tests fallaban con
"ERROR: Staging manifest missing". El remedio acordado: cada fixture genera
el staging en SU propio temporal (o lo copia), nunca escribe en el repo.

Este helper expone `PRODUCT_ROOT`: una raíz de producto con staging listo.

- Si el checkout real ya tiene build/staging/manifest.json, PRODUCT_ROOT es el
  propio checkout (comportamiento idéntico al anterior; camino rápido).
- Si no, PRODUCT_ROOT es una COPIA temporal del checkout con build/staging
  generado por `make staging` dentro de la copia (una vez por proceso).

Los tests nunca leen la implementación: usan la raíz igual que antes
(cwd/instalador/manifest), sin escribir jamás en el checkout real.
"""

from __future__ import annotations

import atexit
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_MANIFEST = Path("build") / "staging" / "manifest.json"

_product_root: Path | None = None

# 008-001: las cachés de alcance de corrida (globales de módulo) no pueden vivir
# bajo el TMPDIR por test, que se retira al terminar cada test. La fixture de
# sesión `_cdad_session_tmp_root` publica aquí su raíz estable.
_RUN_SCOPED_BASE: Path | None = None


def _fallback_base() -> str:
    for candidate in ("/tmp", "/var/tmp", "/usr/tmp"):
        if os.path.isdir(candidate) and os.access(candidate, os.W_OK | os.X_OK):
            return candidate
    return os.getcwd()


def run_scoped_base() -> str:
    """Base estable para cachés de corrida: fuera del TMPDIR por test."""
    return str(_RUN_SCOPED_BASE) if _RUN_SCOPED_BASE is not None else _fallback_base()


def run_scoped_mkdtemp(prefix: str) -> str:
    return tempfile.mkdtemp(prefix=prefix, dir=run_scoped_base())


def _generate_staging_copy() -> Path:
    tmp = run_scoped_mkdtemp("cdad-staging-fixture-")
    atexit.register(shutil.rmtree, tmp, ignore_errors=True)
    copy = Path(tmp) / "product"
    shutil.copytree(
        REPO_ROOT,
        copy,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".pytest_cache", "__pycache__", "build"
        ),
    )
    run = subprocess.run(
        ["make", "staging"],
        cwd=str(copy),
        text=True,
        capture_output=True,
    )
    if not (copy / STAGING_MANIFEST).is_file():
        raise AssertionError(
            "portabilidad de staging: `make staging` no generó "
            f"build/staging/manifest.json en la copia del fixture "
            f"(rc={run.returncode}): {run.stdout!r} {run.stderr!r}"
        )
    return copy


def product_root() -> Path:
    """Raíz de producto con build/staging garantizado (repo o copia temporal)."""
    global _product_root
    if _product_root is None:
        if (REPO_ROOT / STAGING_MANIFEST).is_file():
            _product_root = REPO_ROOT
        else:
            _product_root = _generate_staging_copy()
    return _product_root
