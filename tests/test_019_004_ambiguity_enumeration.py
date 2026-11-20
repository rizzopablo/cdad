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

Enmienda 020-001 (docs/specs/020-001-versioned-layout-local-execution/
spec.md, PC-1/PC-2; plan §0): el localizador versionable vive en la ruta
fija `cdad/project-layout.json` (schema 2: schema_version, methodology_dir,
operational_dir) y los registros operacionales nuevos viven bajo el
`operational_dir` declarado. Un proyecto NO MIGRADO (existe
`.cdad/project-layout.json`, o la declaración carece de `operational_dir`
(schema 1), o queda una raíz `.cdad/` poblada) recibe guía de migración
breve que apunta a `layout-migration.md`, SIN escribir. INVERSIONES
deliberadas (no son cosmética): toda fila cuya evidencia es un `.cdad/`
poblado (con o sin marcador legado, con o sin localizador viejo) pasa de
«ambiguo» / «resuelve» a «guía de migración, sin escribir». Se conservan
sin cambio de promesa: la evidencia AMBIGUA de docs/ y cdad/ sin registrar,
la resolución del marcador legado exacto sin `.cdad/` poblado, y la
resolución de la declaración schema 2 sola.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_019_004_layout import (
    SCRIPT, assert_migration_guidance, put, snapshot,
)
from _layout_support import DECLARATION_REL, OPERATIONAL_DIR, declaration_document

LOCATOR_REL = ".cdad/project-layout.json"  # localizador VIEJO (no migrado)
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


def assert_refusal_for(files: list[str], proc, label: str) -> None:
    """Evidencia solo de docs/ o cdad/ sin registrar sigue siendo AMBIGUA;
    evidencia en un `.cdad/` poblado es un proyecto no migrado (guía)."""
    if all(f.startswith(".cdad/") for f in files):
        assert_migration_guidance(proc, label)
    else:
        assert_ambiguous(proc, label)


def assert_not_ambiguous(proc, label: str) -> None:
    out = (proc.stdout + proc.stderr).lower()
    assert "ambiguous" not in out, f"{label}: no debe diagnosticarse ambiguo: {out!r}"


@pytest.mark.parametrize("name", sorted(NAMED))
def test_named_evidence_is_ambiguous_in_layout_and_operational_command(
        tmp_path: Path, name: str) -> None:
    """PC-04 (§4.2 lista cerrada) + 020-001 PC-2: cada ubicación nombrada,
    sola y sin declaración ni marcador legado, produce rechazo sin escribir en
    la consulta de layout (ordinaria y de bootstrap) y en un comando
    operativo: evidencia de docs/ => diagnóstico de ambigüedad; registro en un
    `.cdad/` poblado => proyecto no migrado, guía a `layout-migration.md`.
    Sin este test, el usuario con un proyecto existente vería operar (o crear
    estado nuevo) sin aviso, o un rechazo sin camino de salida."""
    root = make(tmp_path, NAMED[name])
    before = snapshot(root)
    for label, args in (
        ("layout", ["layout", "--project-root", str(root)]),
        ("layout --for-bootstrap",
         ["layout", "--project-root", str(root), "--for-bootstrap"]),
        ("validate-state", ["validate-state", "--project-root", str(root)]),
    ):
        proc = run_cli(root, *args)
        assert_refusal_for(NAMED[name], proc, f"{name}: {label}")
        assert snapshot(root) == before, f"{name}: {label} no debe escribir"
    assert not (root / LOCATOR_REL).exists()
    assert not (root / OPERATIONAL_DIR).exists(), f"{name}: sin escrituras nuevas"


@pytest.mark.parametrize("name", sorted(UNNAMED))
def test_unnamed_locations_never_make_a_project_ambiguous(
        tmp_path: Path, name: str) -> None:
    """PC-04 + 020-001 PC-2 (INVERTIDO): ubicaciones que la lista no nombra
    siguen sin volver AMBIGUO al proyecto, pero una raíz `.cdad/` poblada
    ya es proyecto no migrado: guía de migración (nunca «ambiguo») y sin
    escribir, en layout, bootstrap y un comando operativo. Sin este test, el
    scratch o un archivo operativo suelto dejaría al usuario operar sobre
    un layout operacional viejo sin aviso."""
    root = make(tmp_path, UNNAMED[name])
    before = snapshot(root)
    for label, args in (
        ("layout", ["layout", "--project-root", str(root)]),
        ("layout --for-bootstrap",
         ["layout", "--project-root", str(root), "--for-bootstrap"]),
        ("validate-state", ["validate-state", "--project-root", str(root)]),
    ):
        proc = run_cli(root, *args)
        assert_migration_guidance(proc, f"{name}: {label}")
        assert_not_ambiguous(proc, f"{name}: {label}")
        assert snapshot(root) == before, f"{name}: {label} no debe escribir"
    assert not (root / OPERATIONAL_DIR).exists()


def test_locator_alone_is_not_ambiguity_evidence(tmp_path: Path) -> None:
    """PC-01/PC-04 (CONTROL, 020-001): la declaración schema 2 en
    `cdad/project-layout.json` como único contenido se resuelve como
    registrada, nunca como ambigua ni como no migrada."""
    root = tmp_path / "proj"
    root.mkdir()
    put(root, DECLARATION_REL, json.dumps(
        declaration_document("process/cdad", OPERATIONAL_DIR)))
    before = snapshot(root)
    proc = run_cli(root, "layout", "--project-root", str(root))
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["source"] == "registered"
    op = run_cli(root, "validate-state", "--project-root", str(root))
    assert_not_ambiguous(op, "locator solo: validate-state")
    assert "layout-migration.md" not in op.stderr, (
        "una declaración schema 2 sola no es un proyecto no migrado")
    assert snapshot(root) == before


@pytest.mark.parametrize("files", [
    [".cdad/executions/exec-1/continuity/head.json"],
    [".cdad/executions/exec-1/guards/decision-1.json"],
    [".cdad/executions/exec-1/continuity/head.json",
     ".cdad/executions/exec-1/guards/decision-1.json"],
], ids=["continuity-only", "guards-only", "continuity-and-guards"])
def test_continuity_and_guards_only_require_migration_guidance(
        tmp_path: Path, files: list[str]) -> None:
    """020-001 PC-2 (INVERTIDO; antes «sin inicializar, nunca ambiguo»): solo
    `continuity/` y/o `guards/` bajo un `.cdad/` poblado ya es un proyecto no
    migrado: guía a `layout-migration.md` (nunca ambiguo, nunca bootstrap
    silencioso) y sin escribir. Sin este test, un proyecto con una cadena de
    continuidad vieja sería tratado como nuevo y se le propondría un layout
    pisando su operación pendiente."""
    root = make(tmp_path, files)
    before = snapshot(root)
    for label, args in (
        ("layout", ["layout", "--project-root", str(root)]),
        ("layout --for-bootstrap",
         ["layout", "--project-root", str(root), "--for-bootstrap"]),
    ):
        proc = run_cli(root, *args)
        assert_migration_guidance(proc, label)
        assert_not_ambiguous(proc, label)
    assert snapshot(root) == before


@pytest.mark.parametrize("kind", ["legacy-state", "legacy-policy", "old-locator"])
@pytest.mark.parametrize("evidence", [".cdad/inbox/delivery-1.json",
                                      ".cdad/runtime/results/receipt-1.json",
                                      ".cdad/publication/pub-1.json",
                                      ".cdad/packets/p1/REQUEST.json"])
def test_legacy_marker_or_old_locator_with_named_evidence_requires_migration(
        tmp_path: Path, kind: str, evidence: str) -> None:
    """020-001 PC-2 (INVERTIDO; antes «el marcador o localizador ganaba»): un
    marcador legado exacto (`docs/…`) o el localizador viejo
    `.cdad/project-layout.json`, junto con registros operacionales en una
    raíz `.cdad/` poblada, es el proyecto típico NO MIGRADO: guía a
    `layout-migration.md`, nunca resolución silenciosa ni «ambiguo», sin
    escribir. Sin este test, el usuario con un proyecto existente seguiría
    operando sobre el layout operacional viejo sin aviso."""
    root = make(tmp_path, [evidence])
    if kind == "legacy-state":
        put(root, "docs/.cdad-state.json", "{}\n")
    elif kind == "legacy-policy":
        put(root, "docs/cdad-policy.json", "{}\n")
    else:
        put(root, LOCATOR_REL, json.dumps(
            {"schema_version": 1, "methodology_dir": "process/cdad"}))
    before = snapshot(root)
    proc = run_cli(root, "layout", "--project-root", str(root))
    assert_migration_guidance(proc, f"{kind}+{evidence}")
    assert_not_ambiguous(proc, f"{kind}+{evidence}")
    assert snapshot(root) == before
    assert not (root / OPERATIONAL_DIR).exists()


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


def test_single_entry_under_packets_requires_migration_guidance_without_writes(
        tmp_path: Path) -> None:
    """PC-04 (§4.2) + 020-001 PC-2: una sola entrada bajo `.cdad/packets/`
    basta para tratar el proyecto como no migrado (guía a
    `layout-migration.md`, sin escribir). Contraparte del caso vacío: sin
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
        assert_migration_guidance(run_cli(root, *args), f"packets 1 entrada: {label}")
        assert snapshot(root) == before, f"{label} no debe escribir"
    assert not (root / LOCATOR_REL).exists()
