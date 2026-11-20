#!/usr/bin/env python3
"""019-004 T2 RED (packet 006) — layout ambiguo en `checkpoint-receipt` y
`reanchor`.

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 29f7c39b…b21be1) §4.2 y PC-02/PC-04/PC-01; hallazgo bloqueante 1 de
review-t2-rereview.md (continuity no puede operar con layout ambiguo).
Caja negra: solo subprocess sobre `cdad_continuity.py`; ningún fuente de
producto se lee. Se reutilizan los fixtures de 007-003 (`_Project`,
`_orphan_receipt`, `_ready_legacy`), que construyen el proyecto por el camino
legítimo del CLI.

Mapeo test -> postcondición (una promesa observable por test, R2):

  test_checkpoint_receipt_refuses_ambiguous_layout_without_writes
      -> PC-04 (§4.2: registros `.cdad/` sin layout admitido = ambiguo; no se
         elige docs/ ni se opera). Sin este test, `checkpoint-receipt` cerraría
         continuidad (escribiría un cuerpo y la cabeza) en un proyecto cuya
         ubicación metodológica necesita aclaración.
  test_reanchor_refuses_ambiguous_layout_without_writes
      -> PC-04 (§4.2), `reanchor` con y sin `--dry-run`. Sin este test, un
         reanclaje (operación con efecto sobre la cadena) o su dry-run
         procederían sobre un layout ambiguo.
  test_receipt_and_reanchor_keep_working_with_exact_legacy_marker (CONTROL)
      -> PC-02. Sin este test, el rechazo por ambigüedad podría alcanzar a un
         proyecto legacy con alguno de los dos marcadores exactos.
  test_receipt_and_reanchor_keep_working_with_registered_locator (CONTROL)
      -> PC-01. Sin este test, un layout registrado se confundiría con
         ambigüedad.

Enmienda 020-001 (docs/specs/020-001-versioned-layout-local-execution/):
la declaración vive en `cdad/project-layout.json` (schema 2) y los registros
nuevos van a `.cdad-execution/`. Un proyecto con los registros operacionales
en el `.cdad/` VIEJO y sin declaración (o con marcador legado) es NO MIGRADO:
guía a `layout-migration.md`, sin escribir. INVERSIONES deliberadas (con
renombre): los dos rechazos «ambiguo» y el control del marcador legado
pasan a exigir la guía de migración; el proyecto no migrado se simula
renombrando el directorio operacional recién creado al `.cdad/` viejo.
Se conserva (con registros bajo el directorio declarado): el control del
locator registrado.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from _layout_support import (
    DECLARATION_REL, OLD_OPERATIONAL_DIR, OPERATIONAL_DIR, write_declaration,
)

from test_007_003_continuity_at_edges import (
    CONTINUITY_CLI,
    _Project,
    assert_rc0,
    tree_snapshot,
)
from test_007_003_legacy_reanchor import (
    _dry_run,
    _legacyize,
    _reanchor,
    _write_approval,
)
from test_007_003_continuity_at_edges import _orphan_receipt

STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"
LOCATOR_REL = DECLARATION_REL  # 020-001: ruta fija de la declaración
BASE = "process/cdad"


def to_old_operational_layout(root: Path, *, drop_markers_too: bool) -> None:
    """Simula un proyecto NO MIGRADO: sin declaración y con los registros
    operacionales en el `.cdad/` viejo (se renombra el directorio operacional
    que acaba de crear el fixture). Con `drop_markers_too` desaparecen
    también los marcadores legados."""
    (root / LOCATOR_REL).unlink()
    (root / LOCATOR_REL).parent.rmdir()
    (root / OPERATIONAL_DIR).rename(root / OLD_OPERATIONAL_DIR)
    if drop_markers_too:
        for rel in (STATE_REL, POLICY_REL):
            (root / rel).unlink()
        assert not (root / LOCATOR_REL).exists()


def migration_guidance_failure(proc, label: str) -> None:
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        f"{label}: debe rechazar un proyecto no migrado; stdout={proc.stdout!r}")
    assert "layout-migration.md" in out, (
        f"{label}: la guía debe apuntar a layout-migration.md; "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert re.search(r"\.cdad(?![-\w])", out), (
        f"{label}: la guía debe nombrar `.cdad`; got {out!r}")


def receipt_project(tmp_path: Path) -> _Project:
    fx = _Project(tmp_path)
    _orphan_receipt(fx, close_attempt=2)
    return fx


def reanchor_project(tmp_path: Path):
    fx = _Project(tmp_path)
    head, dry, approval = _ready_legacy_local(fx)
    return fx, head


def _ready_legacy_local(fx: _Project):
    _, head = _legacyize(fx, 5)
    dry = _dry_run(fx, "setup/dry-run")
    approval, _ = _write_approval(fx, dry)
    return head, dry, approval


def test_checkpoint_receipt_requires_migration_guidance_without_writes(
        tmp_path: Path) -> None:
    """020-001 PC-2 (INVERTIDO; antes «ambiguo»): sin marcador ni declaración
    y con registros en el `.cdad/` viejo, `checkpoint-receipt` rechaza con
    guía a `layout-migration.md` y no escribe."""
    fx = receipt_project(tmp_path)
    to_old_operational_layout(fx.root, drop_markers_too=True)
    before = fx.tree()
    proc = fx.checkpoint_receipt(attempt=2)
    migration_guidance_failure(proc, "PC-2 checkpoint-receipt")
    assert fx.tree() == before, "PC-04: el rechazo no escribe nada"


@pytest.mark.parametrize("dry_run", [True, False])
def test_reanchor_requires_migration_guidance_without_writes(
        tmp_path: Path, dry_run: bool) -> None:
    """020-001 PC-2 (INVERTIDO; antes «ambiguo»): `reanchor` (real y
    `--dry-run`) sobre un proyecto no migrado rechaza con guía a
    `layout-migration.md` y no escribe."""
    fx, head = reanchor_project(tmp_path)
    to_old_operational_layout(fx.root, drop_markers_too=True)
    before = fx.tree()
    if dry_run:
        proc = fx.run(CONTINUITY_CLI, "reanchor", "--project-root",
                      str(fx.root), "--execution-context", str(fx.ctx),
                      "--dry-run", "--json")
    else:
        proc = _reanchor(fx, head)
    migration_guidance_failure(proc, f"PC-2 reanchor dry_run={dry_run}")
    assert fx.tree() == before, "PC-04: el rechazo no escribe nada"


def test_receipt_and_reanchor_with_legacy_marker_and_old_cdad_require_migration(
        tmp_path: Path) -> None:
    """020-001 PC-2 (INVERTIDO; antes: el marcador exacto admitía docs/ aun
    con registros `.cdad/`): el marcador exacto `docs/.cdad-state.json` junto
    con registros en el `.cdad/` viejo es un proyecto no migrado; ambos
    comandos rechazan con guía a `layout-migration.md` y sin escribir. Sin
    este test, el usuario con un proyecto existente seguiría operando sobre
    el layout operacional viejo sin aviso."""
    fx = receipt_project(tmp_path / "receipt")
    to_old_operational_layout(fx.root, drop_markers_too=False)
    (fx.root / POLICY_REL).rename(fx.root / (POLICY_REL + ".bak"))
    assert (fx.root / STATE_REL).is_file()
    before = fx.tree()
    proc = fx.checkpoint_receipt(attempt=2)
    migration_guidance_failure(proc, "PC-2 checkpoint-receipt con marcador")
    assert fx.tree() == before, "el rechazo no escribe nada"

    fx2, head = reanchor_project(tmp_path / "reanchor")
    to_old_operational_layout(fx2.root, drop_markers_too=False)
    (fx2.root / POLICY_REL).rename(fx2.root / (POLICY_REL + ".bak"))
    before2 = fx2.tree()
    proc = _reanchor(fx2, head)
    migration_guidance_failure(proc, "PC-2 reanchor con marcador")
    assert fx2.tree() == before2, "el rechazo no escribe nada"


def test_receipt_and_reanchor_keep_working_with_registered_locator(
        tmp_path: Path) -> None:
    """PC-01 (CONTROL, 020-001): una declaración registrada admite el layout
    con registros bajo el directorio operacional declarado y ningún marcador
    en docs/."""

    def register(root: Path) -> None:
        for rel, name in ((STATE_REL, ".cdad-state.json"),
                          (POLICY_REL, "cdad-policy.json")):
            dst = root / BASE / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root / rel), str(dst))
        write_declaration(root, BASE, OPERATIONAL_DIR)

    fx = receipt_project(tmp_path / "receipt")
    register(fx.root)
    proc = fx.checkpoint_receipt(attempt=2)
    assert_rc0(proc, "PC-01 checkpoint-receipt", "locator registrado")

    fx2, head = reanchor_project(tmp_path / "reanchor")
    register(fx2.root)
    proc = _reanchor(fx2, head)
    assert_rc0(proc, "PC-01 reanchor", "locator registrado")
