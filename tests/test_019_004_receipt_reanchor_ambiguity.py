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
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

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
LOCATOR_REL = ".cdad/project-layout.json"
BASE = "process/cdad"


def drop_markers(root: Path) -> None:
    """Deja el proyecto SIN marcador legacy ni locator, conservando los
    registros `.cdad/` (evidencia insuficiente según §4.2)."""
    for rel in (STATE_REL, POLICY_REL):
        (root / rel).unlink()
    assert not (root / LOCATOR_REL).exists()


def ambiguity_failure(proc, label: str) -> None:
    out = (proc.stdout + proc.stderr).lower()
    assert proc.returncode != 0, (
        f"{label}: debe fallar ante layout ambiguo; stdout={proc.stdout!r}")
    assert "ambiguous" in out, (
        f"{label}: el diagnóstico debe nombrar la ambigüedad; "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}")


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


def test_checkpoint_receipt_refuses_ambiguous_layout_without_writes(
        tmp_path: Path) -> None:
    """PC-04 (§4.2): sin marcador ni locator y con registros `.cdad/`,
    `checkpoint-receipt` falla con diagnóstico de ambigüedad y no escribe."""
    fx = receipt_project(tmp_path)
    drop_markers(fx.root)
    before = fx.tree()
    proc = fx.checkpoint_receipt(attempt=2)
    ambiguity_failure(proc, "PC-04 checkpoint-receipt")
    assert fx.tree() == before, "PC-04: el rechazo no escribe nada"


@pytest.mark.parametrize("dry_run", [True, False])
def test_reanchor_refuses_ambiguous_layout_without_writes(
        tmp_path: Path, dry_run: bool) -> None:
    """PC-04 (§4.2): `reanchor` (real y `--dry-run`) con layout ambiguo falla
    con diagnóstico de ambigüedad y no escribe."""
    fx, head = reanchor_project(tmp_path)
    drop_markers(fx.root)
    before = fx.tree()
    if dry_run:
        proc = fx.run(CONTINUITY_CLI, "reanchor", "--project-root",
                      str(fx.root), "--execution-context", str(fx.ctx),
                      "--dry-run", "--json")
    else:
        proc = _reanchor(fx, head)
    ambiguity_failure(proc, f"PC-04 reanchor dry_run={dry_run}")
    assert fx.tree() == before, "PC-04: el rechazo no escribe nada"


def test_receipt_and_reanchor_keep_working_with_exact_legacy_marker(
        tmp_path: Path) -> None:
    """PC-02 (CONTROL): el marcador exacto `docs/.cdad-state.json` (sin
    `docs/cdad-policy.json`) admite docs/ aun con registros `.cdad/`; ambos
    comandos siguen operando. Solo se ejerce el marcador de estado: ambos
    comandos exigen además el estado de un `execution` administrado, de modo
    que el marcador de política solo no los habilita por una exigencia
    distinta de la resolución de layout."""
    fx = receipt_project(tmp_path / "receipt")
    (fx.root / POLICY_REL).rename(fx.root / (POLICY_REL + ".bak"))
    assert (fx.root / STATE_REL).is_file()
    proc = fx.checkpoint_receipt(attempt=2)
    assert_rc0(proc, "PC-02 checkpoint-receipt", "marcador exacto legacy")

    fx2, head = reanchor_project(tmp_path / "reanchor")
    (fx2.root / POLICY_REL).rename(fx2.root / (POLICY_REL + ".bak"))
    proc = _reanchor(fx2, head)
    assert_rc0(proc, "PC-02 reanchor", "marcador exacto legacy")


def test_receipt_and_reanchor_keep_working_with_registered_locator(
        tmp_path: Path) -> None:
    """PC-01 (CONTROL): un locator registrado admite el layout aunque existan
    registros `.cdad/` y ningún marcador en docs/."""

    def register(root: Path) -> None:
        for rel, name in ((STATE_REL, ".cdad-state.json"),
                          (POLICY_REL, "cdad-policy.json")):
            dst = root / BASE / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root / rel), str(dst))
        (root / LOCATOR_REL).write_text(
            json.dumps({"schema_version": 1, "methodology_dir": BASE}) + "\n",
            encoding="utf-8")

    fx = receipt_project(tmp_path / "receipt")
    register(fx.root)
    proc = fx.checkpoint_receipt(attempt=2)
    assert_rc0(proc, "PC-01 checkpoint-receipt", "locator registrado")

    fx2, head = reanchor_project(tmp_path / "reanchor")
    register(fx2.root)
    proc = _reanchor(fx2, head)
    assert_rc0(proc, "PC-01 reanchor", "locator registrado")
