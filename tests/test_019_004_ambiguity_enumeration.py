#!/usr/bin/env python3
"""019-004 T2 RED (packet 007) — enumeración cerrada de evidencia ambigua.

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 8ad2d594…b0b839) §4.2 tal como lo enmienda
spec-amendment-001.md; PC-02, PC-04. Caja negra: solo subprocess sobre
`cdad_packet.py` (`layout` y `validate-state` como comando operativo
representativo); ningún fuente de producto se lee.

Mapeo test -> postcondición (una promesa observable por test, R2):

  test_named_evidence_is_ambiguous_in_layout_and_operational_command
      -> PC-04 (§4.2, lista cerrada). Sin este test, un proyecto con una
         entrega en inbox, un recibo o una publicación sin layout admitido
         seguiría resolviéndose como "sin inicializar" y se le propondría un
         `cdad/` nuevo (o se operaría) pisando metodología existente.
         RED hoy: inbox, runtime/results y publication (la detección solo
         cubre packets y executions).
  test_unnamed_locations_never_make_a_project_ambiguous
      -> PC-04 (§4.2, "no se examinan"). CONTROL: pasa hoy. Sin este test,
         el scratch de orquestación o un archivo operativo ajeno bloquearía
         un proyecto que sí es nuevo.
  test_continuity_and_guards_only_resolve_as_uninitialized
      -> PC-04 (enmienda: bookkeeping operativo). CONTROL: pasa hoy. Sin este
         test, abrir una cadena de continuidad impediría decidir el layout.
  test_exact_marker_and_registered_layout_win_over_named_evidence
      -> PC-01/PC-02. CONTROL: pasa hoy salvo donde la detección nueva
         degrade la precedencia. Sin este test, la nueva evidencia nombrada
         haría ambiguo a un proyecto legado o registrado que ya funcionaba.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_019_004_layout import SCRIPT, put, snapshot

LOCATOR_REL = ".cdad/project-layout.json"
TIMEOUT_S = 90

# Ubicación nombrada -> archivos que la pueblan (una sola señal por caso).
NAMED = {
    "memory-bank-file": ["docs/projectbrief.md"],
    "docs-specs": ["docs/specs/u1/spec.md"],
    "docs-epics": ["docs/epics/e1/plan.md"],
    "packets": [".cdad/packets/p1/REQUEST.json"],
    "execution-non-operational-record": [".cdad/executions/exec-1/execution.json"],
    "execution-dispatch-record": [".cdad/executions/exec-1/dispatches/d1.json"],
    "execution-with-continuity-plus-record": [
        ".cdad/executions/exec-1/continuity/head.json",
        ".cdad/executions/exec-1/execution.json",
    ],
    "inbox-entry": [".cdad/inbox/delivery-1.json"],
    "runtime-results-entry": [".cdad/runtime/results/receipt-1.json"],
    "publication-entry": [".cdad/publication/pub-1.json"],
}

# No nombradas por la lista: nunca vuelven ambiguo al proyecto.
UNNAMED = {
    "orchestration-scratch": [".cdad/orchestration/scratch.md"],
    "unrelated-operational-file": [".cdad/runtime/state.lock"],
    "unrelated-operational-file-2": [".cdad/notes.json"],
}


def run_cli(root: Path, *args: str):
    home = root.parent / "home"
    home.mkdir(exist_ok=True)
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=str(root.parent), env=env,
        stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)


def make(tmp_path: Path, files: list[str]) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    for f in files:
        put(root, f, "{}\n")
    return root


def assert_ambiguous(proc, label: str) -> None:
    assert proc.returncode != 0, f"{label}: debe fallar; stdout={proc.stdout!r}"
    assert "schema_version" not in proc.stdout, f"{label}: objeto de éxito en fallo"
    assert "ambiguous" in proc.stderr.lower(), (
        f"{label}: el diagnóstico debe indicar ambigüedad; stderr={proc.stderr!r}")


def assert_not_ambiguous(proc, label: str) -> None:
    out = (proc.stdout + proc.stderr).lower()
    assert "ambiguous" not in out, f"{label}: no debe diagnosticarse ambiguo: {out!r}"


@pytest.mark.parametrize("name", sorted(NAMED))
def test_named_evidence_is_ambiguous_in_layout_and_operational_command(
        tmp_path: Path, name: str) -> None:
    """PC-04 (§4.2 lista cerrada): cada ubicación nombrada, sola y sin locator
    ni marcador legado, produce diagnóstico de ambigüedad en la consulta de
    layout (ordinaria y de bootstrap) y en un comando operativo, sin escribir."""
    root = make(tmp_path, NAMED[name])
    before = snapshot(root)
    for label, args in (
        ("layout", ["layout", "--project-root", str(root)]),
        ("layout --for-bootstrap",
         ["layout", "--project-root", str(root), "--for-bootstrap"]),
        ("validate-state", ["validate-state", "--project-root", str(root)]),
    ):
        proc = run_cli(root, *args)
        assert_ambiguous(proc, f"{name}: {label}")
        assert snapshot(root) == before, f"{name}: {label} no debe escribir"
    assert not (root / LOCATOR_REL).exists()


@pytest.mark.parametrize("name", sorted(UNNAMED))
def test_unnamed_locations_never_make_a_project_ambiguous(
        tmp_path: Path, name: str) -> None:
    """PC-04 (CONTROL): ubicaciones que la lista no nombra no se examinan; el
    proyecto sigue sin inicializar (nuevo en bootstrap), no ambiguo."""
    root = make(tmp_path, UNNAMED[name])
    before = snapshot(root)
    plain = run_cli(root, "layout", "--project-root", str(root))
    assert plain.returncode != 0, "sin layout admitido la consulta ordinaria falla"
    assert_not_ambiguous(plain, f"{name}: layout")
    boot = run_cli(root, "layout", "--project-root", str(root), "--for-bootstrap")
    assert boot.returncode == 0, f"{name}: bootstrap debe proponer cdad/: {boot.stderr!r}"
    got = json.loads(boot.stdout)
    assert got["source"] == "new" and got["methodology_dir"] == "cdad"
    op = run_cli(root, "validate-state", "--project-root", str(root))
    assert_not_ambiguous(op, f"{name}: validate-state")
    assert snapshot(root) == before


def test_locator_alone_is_not_ambiguity_evidence(tmp_path: Path) -> None:
    """PC-01/PC-04 (CONTROL): el locator como único contenido de `.cdad/` se
    resuelve como registrado, nunca como ambiguo."""
    root = tmp_path / "proj"
    root.mkdir()
    put(root, LOCATOR_REL, json.dumps(
        {"schema_version": 1, "methodology_dir": "process/cdad"}))
    before = snapshot(root)
    proc = run_cli(root, "layout", "--project-root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["source"] == "registered"
    assert_not_ambiguous(
        run_cli(root, "validate-state", "--project-root", str(root)),
        "locator solo: validate-state")
    assert snapshot(root) == before


@pytest.mark.parametrize("files", [
    [".cdad/executions/exec-1/continuity/head.json"],
    [".cdad/executions/exec-1/guards/decision-1.json"],
    [".cdad/executions/exec-1/continuity/head.json",
     ".cdad/executions/exec-1/guards/decision-1.json"],
], ids=["continuity-only", "guards-only", "continuity-and-guards"])
def test_continuity_and_guards_only_resolve_as_uninitialized(
        tmp_path: Path, files: list[str]) -> None:
    """PC-04 (CONTROL, enmienda): solo `continuity/` y/o `guards/` es
    bookkeeping operativo: sin inicializar, nunca ambiguo."""
    root = make(tmp_path, files)
    before = snapshot(root)
    plain = run_cli(root, "layout", "--project-root", str(root))
    assert plain.returncode != 0
    assert_not_ambiguous(plain, "layout")
    boot = run_cli(root, "layout", "--project-root", str(root), "--for-bootstrap")
    assert boot.returncode == 0, boot.stderr
    assert json.loads(boot.stdout)["source"] == "new"
    assert snapshot(root) == before


@pytest.mark.parametrize("kind", ["legacy-state", "legacy-policy", "registered"])
@pytest.mark.parametrize("evidence", [".cdad/inbox/delivery-1.json",
                                      ".cdad/runtime/results/receipt-1.json",
                                      ".cdad/publication/pub-1.json",
                                      ".cdad/packets/p1/REQUEST.json"])
def test_exact_marker_and_registered_layout_win_over_named_evidence(
        tmp_path: Path, kind: str, evidence: str) -> None:
    """PC-01/PC-02: un marcador legado exacto o un locator válido siguen
    resolviendo su layout aunque exista evidencia nombrada; no es ambiguo."""
    root = make(tmp_path, [evidence])
    if kind == "legacy-state":
        put(root, "docs/.cdad-state.json", "{}\n")
        want = ("legacy", "docs")
    elif kind == "legacy-policy":
        put(root, "docs/cdad-policy.json", "{}\n")
        want = ("legacy", "docs")
    else:
        put(root, LOCATOR_REL, json.dumps(
            {"schema_version": 1, "methodology_dir": "process/cdad"}))
        want = ("registered", "process/cdad")
    before = snapshot(root)
    proc = run_cli(root, "layout", "--project-root", str(root))
    assert proc.returncode == 0, f"{kind}+{evidence}: {proc.stderr!r}"
    got = json.loads(proc.stdout)
    assert (got["source"], got["methodology_dir"]) == want
    assert snapshot(root) == before


# --- T2 final review (packet 008): entradas, no el directorio contenedor ----

def test_empty_packets_directory_is_uninitialized_not_ambiguous(
        tmp_path: Path) -> None:
    """PC-04 (§4.2: «cualquier entrada bajo `.cdad/packets/`»): un proyecto
    cuyo único contenido `.cdad` es un `.cdad/packets/` vacío no tiene
    ninguna entrada; se resuelve sin inicializar y bootstrap propone el
    default nuevo. Sin este test, el usuario con un directorio vacío
    heredado de una limpieza vería rechazado su proyecto como ambiguo y no
    recibiría la propuesta de inicialización."""
    root = tmp_path / "proj"
    (root / ".cdad" / "packets").mkdir(parents=True)
    before = snapshot(root)
    plain = run_cli(root, "layout", "--project-root", str(root))
    assert plain.returncode != 0, "sin layout admitido la consulta ordinaria falla"
    assert_not_ambiguous(plain, "packets vacío: layout")
    boot = run_cli(root, "layout", "--project-root", str(root), "--for-bootstrap")
    assert boot.returncode == 0, f"bootstrap debe proponer cdad/: {boot.stderr!r}"
    got = json.loads(boot.stdout)
    assert got["source"] == "new" and got["methodology_dir"] == "cdad"
    assert_not_ambiguous(
        run_cli(root, "validate-state", "--project-root", str(root)),
        "packets vacío: validate-state")
    assert snapshot(root) == before
    assert (root / ".cdad" / "packets").is_dir()
    assert not (root / LOCATOR_REL).exists()


def test_single_entry_under_packets_is_ambiguous_without_writes(
        tmp_path: Path) -> None:
    """PC-04 (§4.2): una sola entrada bajo `.cdad/packets/` basta para el
    diagnóstico de ambigüedad, sin escribir. Contraparte del caso vacío: sin
    este test, relajar la comprobación a «ignorar packets» dejaría pasar un
    proyecto con paquetes reales y se le propondría un `cdad/` nuevo."""
    root = make(tmp_path, [".cdad/packets/p1.json"])
    before = snapshot(root)
    for label, args in (
        ("layout", ["layout", "--project-root", str(root)]),
        ("layout --for-bootstrap",
         ["layout", "--project-root", str(root), "--for-bootstrap"]),
        ("validate-state", ["validate-state", "--project-root", str(root)]),
    ):
        assert_ambiguous(run_cli(root, *args), f"packets 1 entrada: {label}")
        assert snapshot(root) == before, f"{label} no debe escribir"
    assert not (root / LOCATOR_REL).exists()
