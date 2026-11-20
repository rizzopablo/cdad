#!/usr/bin/env python3
"""019-004 T2 RED (packet 005) — layout ambiguo en continuity y gap-report.

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 29f7c39b…b21be1) §4.2 y PC-04/PC-05; hallazgos bloqueantes 1 y 2 de
review-t2-rereview.md. Caja negra: solo subprocess sobre `cdad_continuity.py`
y `cdad_contract_links.py`; ningún fuente de producto se lee.

Mapeo test -> postcondición (una promesa observable por test, R2):

  test_continuity_refuses_ambiguous_layout_without_writes
      -> PC-04 (§4.2, evidencia insuficiente = ambiguo, no se elige docs/ ni
         se opera). Sin este test, `begin`/`checkpoint`/`reconcile` seguirían
         escribiendo o clasificando sobre registros `.cdad/` de un proyecto
         cuya ubicación metodológica necesita aclaración.
  test_continuity_keeps_working_with_exact_legacy_marker (CONTROL)
      -> PC-02. Sin este test, el rechazo por ambigüedad podría alcanzar a un
         proyecto legacy con alguno de los dos marcadores exactos.
  test_continuity_keeps_working_with_registered_locator (CONTROL)
      -> PC-01. Sin este test, un layout registrado se confundiría con
         ambigüedad.
  test_gap_report_refuses_ambiguous_layout_instead_of_searching_docs
      -> PC-04/PC-05. Sin este test, el informe de huecos atribuiría contratos
         a docs/specs sin marcador legacy.
  test_gap_report_legacy_marker_admits_docs (CONTROL)
      -> PC-02/PC-05. Sin este test, un marcador exacto dejaría de admitir
         docs/ en la búsqueda convencional.

Enmienda 020-001 (docs/specs/020-001-versioned-layout-local-execution/):
la declaración vive en `cdad/project-layout.json` (schema 2) y los registros
operacionales nuevos van a `.cdad-execution/`. Un `.cdad/` poblado (aunque
exista marcador legado o declaración) es un proyecto NO MIGRADO: guía a
`layout-migration.md`, sin escribir. INVERSIONES deliberadas: las filas con
evidencia `.cdad/` de
`test_continuity_refuses_ambiguous_layout_without_writes` y del informe de
huecos pasan de «ambiguo» a «guía de migración»; el control del marcador
legado con `.cdad/` poblado pasa de «sigue operando» a «guía de migración»
(se renombra a `test_continuity_with_legacy_marker_and_cdad_records_requires_migration`).
Se conservan: ambigüedad por docs/specs / docs/epics y continuidad con
declaración registrada (ahora con registros bajo el directorio declarado).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from _layout_support import (
    DECLARATION_REL, OPERATIONAL_DIR, write_declaration,
)
from test_003_007_t2_checkpoint_vs_begin import (
    CONTINUITY_SCRIPT,
    EXEC_ID,
    PACKET_ID,
    POLICY_REL,
    STATE_REL,
    exec_context_fixture,
    policy_fixture,
    state_doc_fixture,
    update_fixture,
)

CONTRACT_LINKS_CLI = (Path(CONTINUITY_SCRIPT).parent.parent
                      / "skills" / "cdad-cycle" / "scripts"
                      / "cdad_contract_links.py")
LOCATOR_REL = DECLARATION_REL  # 020-001: ruta fija de la declaración
TIMEOUT_S = 120


def snapshot(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            out[rel] = ("link", os.readlink(p))
        elif p.is_dir():
            out[rel] = ("dir", None)
        else:
            out[rel] = ("file", p.read_bytes())
    return out


def write_json(root: Path, rel: str, doc: dict) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def cont(root: Path, command: str, ctx: Path, upd: Path | None = None):
    argv = [sys.executable, str(CONTINUITY_SCRIPT), command,
            "--project-root", str(root), "--execution-context", str(ctx)]
    if command == "reconcile":
        argv += ["--packet", PACKET_ID]
    else:
        argv += ["--update", str(upd)]
    argv.append("--json")
    return subprocess.run(argv, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=TIMEOUT_S)


def seed_marker(root: Path, which: str) -> None:
    if which == "state":
        write_json(root, STATE_REL, state_doc_fixture())
    else:
        write_json(root, POLICY_REL, policy_fixture())


def assert_migration_guidance_out(proc, label: str) -> None:
    """020-001 PC-2: no migrado => rechazo con guía a `layout-migration.md`
    que nombra `.cdad` (se revisa stdout+stderr: los comandos usan --json)."""
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, f"{label}: debe rechazar; stdout={proc.stdout!r}"
    assert "layout-migration.md" in out, (
        f"{label}: la guía debe apuntar a layout-migration.md; got {out!r}")
    assert re.search(r"\.cdad(?![-\w])", out), (
        f"{label}: la guía debe nombrar `.cdad`; got {out!r}")
    assert "ambiguous" not in out.lower(), (
        f"{label}: un proyecto no migrado no es «ambiguo»; got {out!r}")


def prime_then_drop_layout(root: Path, ctx: Path, upd: Path) -> None:
    """`begin` bajo un layout admitido (estado + declaración), que luego
    desaparece (estado y declaración) para que el resto del caso no tenga
    layout admitido."""
    seed_marker(root, "state")
    write_declaration(root)
    proc = cont(root, "begin", ctx, upd)
    assert proc.returncode == 0, f"precondición: {proc.stdout}{proc.stderr}"
    (root / STATE_REL).unlink()
    (root / LOCATOR_REL).unlink()
    (root / LOCATOR_REL).parent.rmdir()


def project(tmp_path: Path):
    root = tmp_path / "proj"
    root.mkdir()
    ctx = write_json(root, "fixture/exec.json", exec_context_fixture())
    upd = write_json(root, "fixture/update.json", update_fixture())
    return root, ctx, upd


def seed_evidence(root: Path, kind: str) -> None:
    if kind == "cdad-packet-record":
        write_json(root, ".cdad/packets/p1/REQUEST.json", {"packet_id": "p1"})
    elif kind == "cdad-execution-record":
        write_json(root, f".cdad/executions/{EXEC_ID}/execution.json",
                   exec_context_fixture())
    elif kind == "docs-specs":
        write_json(root, "docs/specs/u1/notes.json", {"x": 1})
    elif kind == "docs-epics":
        write_json(root, "docs/epics/e1/notes.json", {"x": 1})
    else:  # pragma: no cover
        raise AssertionError(kind)


EVIDENCE = ["cdad-packet-record", "cdad-execution-record",
            "docs-specs", "docs-epics"]


@pytest.mark.parametrize("command", ["begin", "checkpoint", "reconcile"])
@pytest.mark.parametrize("kind", EVIDENCE)
def test_continuity_refuses_ambiguous_layout_without_writes(
        tmp_path: Path, command: str, kind: str) -> None:
    """PC-04 (§4.2) + 020-001 PC-2: sin layout admitido, evidencia solo de
    docs/specs / docs/epics => diagnóstico explícito de ambigüedad; registros
    en un `.cdad/` poblado => proyecto no migrado con guía a
    `layout-migration.md`. En ambos casos los tres comandos fallan sin
    escribir."""
    root, ctx, upd = project(tmp_path)
    if command != "begin":
        # Cabeza válida creada bajo un layout admitido, que luego desaparece.
        prime_then_drop_layout(root, ctx, upd)
    seed_evidence(root, kind)
    before = snapshot(root)
    proc = cont(root, command, ctx, upd)
    out = (proc.stdout + proc.stderr).lower()
    assert proc.returncode != 0, (
        f"PC-04: `{command}` con evidencia `{kind}` debe fallar; "
        f"stdout={proc.stdout!r}")
    if kind.startswith("cdad-"):
        assert_migration_guidance_out(proc, f"{command} con `{kind}`")
    else:
        assert "ambiguous" in out, (
            f"PC-04: el diagnóstico debe nombrar la ambigüedad del layout; "
            f"got stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert snapshot(root) == before, "PC-04: el rechazo no escribe nada"


@pytest.mark.parametrize("command", ["begin", "checkpoint", "reconcile"])
@pytest.mark.parametrize("marker", ["state", "policy"])
def test_continuity_with_legacy_marker_and_cdad_records_requires_migration(
        tmp_path: Path, command: str, marker: str) -> None:
    """020-001 PC-2 (INVERTIDO; antes: el marcador exacto admitía docs/ aun
    con registros `.cdad/`): un marcador legado con registros en un `.cdad/`
    poblado es un proyecto no migrado: los tres comandos rechazan con guía a
    `layout-migration.md` y sin escribir. Sin este test, el usuario con un
    proyecto existente seguiría operando continuidad sobre el layout
    operacional viejo sin aviso."""
    root, ctx, upd = project(tmp_path)
    prime_then_drop_layout(root, ctx, upd)
    seed_marker(root, marker)
    seed_evidence(root, "cdad-packet-record")
    before = snapshot(root)
    proc = cont(root, command, ctx, upd)
    assert_migration_guidance_out(proc, f"{command} con marcador {marker}")
    assert snapshot(root) == before, "el rechazo no escribe nada"


@pytest.mark.parametrize("command", ["begin", "checkpoint", "reconcile"])
def test_continuity_keeps_working_with_registered_locator(
        tmp_path: Path, command: str) -> None:
    """PC-01 (CONTROL, 020-001): una declaración registrada admite el layout
    con registros operacionales bajo el directorio declarado (ya no bajo
    `.cdad/`) y ningún marcador en docs/."""
    root, ctx, upd = project(tmp_path)
    seed_marker(root, "state")
    write_declaration(root)
    assert cont(root, "begin", ctx, upd).returncode == 0
    (root / STATE_REL).unlink()
    base = "process/cdad"
    write_json(root, f"{base}/.cdad-state.json", state_doc_fixture())
    write_json(root, f"{base}/cdad-policy.json", policy_fixture())
    write_declaration(root, base, OPERATIONAL_DIR)
    write_json(root, f"{OPERATIONAL_DIR}/packets/p1/REQUEST.json",
               {"packet_id": "p1"})
    proc = cont(root, command, ctx, upd)
    assert proc.returncode == 0, f"{proc.stdout!r} {proc.stderr!r}"


# ------------------------------------------------------------- gap-report


def gap_unit(root: Path, base: str, unit: str) -> str:
    d = root / base / "specs" / unit
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(
        "# spec\n<!-- cdad:pc PC-1 promise=A -->\nTexto.\n", encoding="utf-8")
    (d / "closure.md").write_text(f"# cierre {unit}\n", encoding="utf-8")
    return hashlib.sha256((d / "closure.md").read_bytes()).hexdigest()


def gap_state(root: Path, unit: str, base: str, sha: str) -> Path:
    return write_json(root, "STATE.json", {
        "epic_features": [{"id": unit, "status": "done",
                           "closure_evidence": {
                               "path": f"{base}/specs/{unit}/closure.md",
                               "sha256": sha}}],
        "epic_history": []})


def gap_report(root: Path, state: Path):
    return subprocess.run(
        [sys.executable, str(CONTRACT_LINKS_CLI), "gap-report",
         "--project-root", str(root), "--state", str(state)],
        capture_output=True, text=True, cwd=str(root.parent),
        timeout=TIMEOUT_S)


@pytest.mark.parametrize("extra", ["none", "docs-epics", "memory-bank",
                                   "cdad-packet-record"])
def test_gap_report_refuses_ambiguous_layout_instead_of_searching_docs(
        tmp_path: Path, extra: str) -> None:
    """PC-04/PC-05 (§4.2) + 020-001 PC-2: sin locator ni marcador legacy,
    solo con docs/specs (u otra evidencia insuficiente) el informe falla con
    diagnóstico de ambigüedad; con registros en un `.cdad/` poblado, con guía
    de migración. Nunca universo atribuido a docs/ y sin escribir."""
    root = tmp_path / "proj"
    sha = gap_unit(root, "docs", "unit-a")
    if extra == "docs-epics":
        seed_evidence(root, "docs-epics")
    elif extra == "memory-bank":
        (root / "docs" / "projectbrief.md").write_text("# brief\n",
                                                       encoding="utf-8")
    elif extra == "cdad-packet-record":
        seed_evidence(root, "cdad-packet-record")
    state = gap_state(root, "unit-a", "docs", sha)
    before = snapshot(root)
    proc = gap_report(root, state)
    out = (proc.stdout + proc.stderr).lower()
    assert proc.returncode != 0, (
        "PC-04: layout ambiguo debe fallar, no buscar en docs/; "
        f"stdout={proc.stdout!r}")
    if extra == "cdad-packet-record":
        assert_migration_guidance_out(proc, "informe con `.cdad/` poblado")
    else:
        assert "ambiguous" in out, (
            f"PC-04: diagnóstico de ambigüedad esperado; got {proc.stdout!r} "
            f"{proc.stderr!r}")
    assert '"universe"' not in proc.stdout, "no se emite informe sobre docs/"
    assert snapshot(root) == before


@pytest.mark.parametrize("marker", [".cdad-state.json", "cdad-policy.json"])
def test_gap_report_legacy_marker_admits_docs(
        tmp_path: Path, marker: str) -> None:
    """PC-02/PC-05 (CONTROL): cualquiera de los dos marcadores exactos admite
    la búsqueda convencional en docs/specs."""
    root = tmp_path / "proj"
    sha = gap_unit(root, "docs", "unit-a")
    (root / "docs" / marker).write_text("{}\n", encoding="utf-8")
    proc = gap_report(root, gap_state(root, "unit-a", "docs", sha))
    assert proc.returncode == 0, f"{proc.stdout!r} {proc.stderr!r}"
    payload = json.loads(proc.stdout)
    assert [u.get("unit") for u in payload.get("universe", [])] == ["unit-a"]
    assert not (root / LOCATOR_REL).exists()
