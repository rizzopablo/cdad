#!/usr/bin/env python3
"""005-003 T1 RED — vista compacta del estado operativo + selección de entrada
(PD-1, PD-2, PD-5; INV-1, INV-9).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.1 (`compact-view-v1`),
  §2.2 (mapa de entrada), §2.5 (asimetría de raíz relativa diagnosticada en la
  SALIDA de la vista), §3 PD-1/PD-2, §4 INV-1/INV-9.
- docs/specs/005-003-orientation-reduction/plan.md §3 (ficha T1) y §4 (T1).

Superficie observable bajo prueba (proyectos sintéticos en tempdirs; caja
negra: SOLO subprocess sobre el CLI del repo, el módulo NUNCA se importa y la
implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>

El subcomando `status` NO existe todavía: HOY el CLI responde con un error de
uso (rc=2, stderr «invalid choice: 'status'»). Por eso cada test falla en la
ASERCIÓN sobre la salida observable del contrato (rc / documento / límite /
diagnóstico), nunca en la invocación: los fallos RED son AssertionError de
contrato, jamás ImportError, SyntaxError, JSONDecodeError ni error de setup.
Los fixtures son autocontenidos (tempdirs armados por el test; sin datos de
demo, sin la base real de sesiones, sin rutas de este host) y el HOME del
subproceso SIEMPRE es un tempdir vacío (nunca el HOME real).

Mapeo test → postcondición/borde:
  test_pd1_compact_view_emits_single_bounded_document
      -> PD-1 (forma, campos mínimos de §2.1, sin `stage_history`, ≤16.384 B,
         determinista) + borde «surfacea active_packet.status»
  test_inv1_status_is_read_only_state_byte_identical
      -> INV-1 (read-only: el estado queda byte-idéntico)
  test_pd1_limit_fails_closed_without_partial_projection
      -> PD-1 borde C1 (límite: fallo cerrado sin proyección parcial, el
         diagnóstico nombra el límite y la bandera `--max-bytes`)
  test_pd1_limit_does_not_grow_with_history
      -> PD-1 borde (el historial NO se emite; la proyección es función de los
         campos operativos, no del tamaño del estado)
  test_pd2_entry_continuity_reconcile_for_prepared_packet
      -> PD-2 (caso real: etapa en curso + paquete `prepared` -> reconciliar)
  test_pd2_entry_continuity_reconcile_for_dispatched_packet
      -> PD-2 borde (`dispatched` -> reconciliar antes de repetir)
  test_pd2_entry_next_unit_at_rest
      -> PD-2 (reposo sin trabajo pendiente -> next-unit)
  test_pd2_entry_diagnosis_on_incomplete_config
      -> PD-2 (configuración incompleta: sin `docs/cdad-policy.json` -> diagnosis)
  test_pd2_entry_does_not_depend_on_literal_inicializar
      -> PD-2 borde (la selección NO depende del literal «inicializar»)
  test_pd5_relative_root_accepted_projects_view
      -> PD-5 borde C4 **SUPERSEDED** por la fila 11 del plan de epic-005
         (005-011 PD-2/PD-3): el comportamiento NUEVO es «raíz relativa
         aceptada → hay proyección» (rc=0), no el diagnóstico de la asimetría
  test_inv9_unknowns_declare_causes_not_fabricated_zero
      -> INV-9 (`unknowns[]` declara causas, nunca un `0` fabricado)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    build_project,
    prepare_args,
    read_state,
    tree_snapshot,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.1: `python3 <skill-dir>/scripts/cdad_packet.py status`.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"
MAX_BYTES = 16_384
CLI_TIMEOUT_S = 60

# Campos mínimos exigidos por §2.1.
REQUIRED_TOP = (
    "project", "epic", "feature", "execution", "packet",
    "authority", "version", "next", "entry", "unknowns",
)
ENTRY_VALUES = {"continuity-reconcile", "next-unit", "diagnosis"}


# ---------------------------------------------------------------- helpers


class _Fixture:
    """Proyecto sintético autocontenido en un tempdir, con HOME aislado."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return env

    def prepare(self, *, objective: str = "005-003 T1 fixture",
                role: str = "test-writer", substage: str = "red"
                ) -> subprocess.CompletedProcess:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        return subprocess.run(
            [sys.executable, str(CLI),
             *prepare_args(self.root, role=role, substage=substage,
                           objective=objective)],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def status(self, *extra: str, project_root=None, cwd=None
               ) -> subprocess.CompletedProcess:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        argv = [
            sys.executable, str(CLI), "status",
            "--project-root",
            str(self.root if project_root is None else project_root),
            *extra,
        ]
        return subprocess.run(
            argv, capture_output=True, text=True,
            cwd=str(REPO_ROOT if cwd is None else cwd), env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def read_state(self) -> dict:
        return read_state(self.root)

    def write_state(self, state: dict) -> None:
        write_state(self.root, state)

    def snapshot(self) -> dict:
        return tree_snapshot(self.root)

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


def _status_document(proc: subprocess.CompletedProcess) -> dict:
    """El único documento JSON de la vista, o AssertionError de contrato.

    Nunca deja escapar un JSONDecodeError (fallo de setup): si la vista no
    emitió el documento del contrato, la aserción lo declara.
    """
    assert proc.returncode == 0, (
        "PD-1 violada: la vista `status` debe emitir la proyección (rc=0); "
        f"hoy rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "PD-1 violada: la vista no emitió el documento por stdout; "
        f"stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "PD-1 violada: stdout no es un ÚNICO documento JSON válido: "
            f"{proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"PD-1 violada: el documento de la vista no es un objeto JSON: {doc!r}"
    )
    return doc


def _doc_bytes(proc: subprocess.CompletedProcess) -> int:
    return len(proc.stdout.encode("utf-8"))


# ---------------------------------------------------------------- PD-1


def test_pd1_compact_view_emits_single_bounded_document(fx: _Fixture) -> None:
    """PD-1: `status` emite un único documento JSON con los campos de §2.1,
    sin `stage_history`, ≤16.384 B por defecto, determinista (misma entrada →
    mismos bytes) y surfaceando `active_packet.status`."""
    fx.prepare()  # ejecución v2 activa + paquete activo `prepared`
    proc = fx.status()
    doc = _status_document(proc)

    missing = [k for k in REQUIRED_TOP if k not in doc]
    assert not missing, (
        f"PD-1 violada: faltan campos obligatorios de §2.1: {missing}; "
        f"documento: {sorted(doc)}"
    )

    # Sub-campos nombrados por §2.1 (mínimo del contrato de la salida).
    assert {"active_epic", "epic_stage"} <= set(doc["epic"] or {}), (
        f"PD-1 violada: `epic` no trae active_epic/epic_stage: {doc['epic']!r}"
    )
    assert {"active_feature", "current_stage", "tdd_substage"} <= set(
        doc["feature"] or {}
    ), f"PD-1 violada: `feature` incompleto: {doc['feature']!r}"
    assert {"id", "authority_ref", "model_policy", "policy_sha256"} <= set(
        doc["execution"] or {}
    ), f"PD-1 violada: `execution` incompleto: {doc['execution']!r}"
    assert doc["packet"] and {"id", "role", "substage", "status"} <= set(
        doc["packet"]
    ), f"PD-1 violada: `packet` incompleto: {doc['packet']!r}"
    assert doc["packet"]["status"] == "prepared", (
        "PD-1 violada: la proyección no surfacea active_packet.status "
        f"(`prepared`): {doc['packet']['status']!r}"
    )
    assert doc["entry"] in ENTRY_VALUES, (
        f"PD-2 violada: `entry` fuera del mapa declarado: {doc['entry']!r}"
    )
    assert doc["next"] not in (None, "", {}), (
        f"PD-1 violada: `next` vacío (ruta siguiente sin fuente declarada): "
        f"{doc['next']!r}"
    )

    # El historial NO se emite (garantía (ii) de §2.1).
    assert "stage_history" not in proc.stdout, (
        "PD-1 violada: la vista emite `stage_history` (el historial NO se "
        "proyecta)"
    )

    # Acotada por el límite normativo por defecto.
    assert _doc_bytes(proc) <= MAX_BYTES, (
        f"PD-1/C1 violada: el documento supera {MAX_BYTES} B por defecto "
        f"({_doc_bytes(proc)} B)"
    )

    # Determinista: misma entrada → mismos bytes.
    again = fx.status()
    assert again.stdout == proc.stdout, (
        "PD-1 violada: la vista no es determinista (misma entrada, distintos "
        "bytes)"
    )


# ---------------------------------------------------------------- INV-1


def test_inv1_status_is_read_only_state_byte_identical(fx: _Fixture) -> None:
    """INV-1: la vista es read-only — el estado (y el árbol) quedan
    byte-idénticos tras invocarla."""
    fx.prepare()
    state_before = fx.state_bytes()
    tree_before = fx.snapshot()

    proc = fx.status()
    _status_document(proc)  # la vista debe emitir (hoy rc≠0)

    assert fx.state_bytes() == state_before, (
        "INV-1 violada: la vista modificó docs/.cdad-state.json (debe ser "
        "read-only)"
    )
    assert fx.snapshot() == tree_before, (
        "INV-1 violada: la vista escribió en el proyecto (debe ser read-only)"
    )


# ---------------------------------------------------------------- PD-1 / C1


def test_pd1_limit_fails_closed_without_partial_projection(fx: _Fixture) -> None:
    """PD-1 borde C1: por encima del límite la vista falla cerrado (rc≠0),
    SIN emitir una proyección parcial, con un diagnóstico que nombra el límite
    y el camino legítimo para obtener más (`--max-bytes N`). Se fuerza de
    forma determinista con un `--max-bytes` chico sobre el fixture."""
    fx.prepare()
    proc = fx.status("--max-bytes", "64")
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0, (
        "PD-1/C1 violada: con --max-bytes 64 la vista no falló cerrado "
        f"(rc={proc.returncode})"
    )
    assert proc.stdout.strip() == "", (
        "PD-1/C1 violada: falló cerrado pero emitió una proyección parcial "
        f"por stdout: {proc.stdout[:200]!r}"
    )
    assert re.search(r"--max-bytes", out), (
        "PD-1/C1 violada: el diagnóstico no nombra el camino legítimo para "
        f"obtener más (--max-bytes N): {out.strip()!r}"
    )
    assert re.search(r"(?i)\bbytes\b|\bl[ií]mite\b|\blimit\b", out), (
        "PD-1/C1 violada: el diagnóstico no nombra la causa (el límite): "
        f"{out.strip()!r}"
    )


def test_pd1_limit_does_not_grow_with_history(fx: _Fixture) -> None:
    """PD-1 borde: el historial NO se emite, así que el límite no crece con él
    y la proyección es la MISMA para cualquier tamaño de estado (función de
    los campos operativos, no del tamaño)."""
    fx.prepare()
    small = fx.status()
    small_doc = _status_document(small)
    assert _doc_bytes(small) <= MAX_BYTES

    # Historia grande sintética: el estado se agranda mucho, la proyección no.
    state = fx.read_state()
    entries = list(state.get("stage_history") or [])
    assert entries, "fixture: el estado base no trae stage_history"
    state["stage_history"] = [dict(entries[0]) for _ in range(800)]
    fx.write_state(state)
    assert (fx.root / STATE_REL).stat().st_size > MAX_BYTES, (
        "fixture: la historia sintética no agrandó el estado"
    )

    big = fx.status()
    big_doc = _status_document(big)
    assert _doc_bytes(big) <= MAX_BYTES, (
        f"PD-1/C1 violada: con historial grande el documento supera "
        f"{MAX_BYTES} B ({_doc_bytes(big)} B) — el límite creció con el "
        "historial"
    )
    assert "stage_history" not in big.stdout, (
        "PD-1 violada: con historial grande la vista emite `stage_history`"
    )
    assert big_doc == small_doc, (
        "PD-1 violada: la proyección cambió al agrandar SOLO el historial "
        "(debe ser función de los campos operativos, no del tamaño del estado)"
    )


# ---------------------------------------------------------------- PD-2


def test_pd2_entry_continuity_reconcile_for_prepared_packet(fx: _Fixture) -> None:
    """PD-2 (caso real): con la etapa en curso y `active_packet.status=prepared`
    la selección es `continuity-reconcile`, nunca `next-unit`."""
    fx.prepare()
    doc = _status_document(fx.status())
    assert doc["packet"]["status"] == "prepared", (
        f"fixture: el paquete activo no quedó `prepared`: {doc['packet']!r}"
    )
    assert doc["entry"] == "continuity-reconcile", (
        "PD-2 violada: con un paquete `prepared` la entrada debe atender el "
        f"paquete pendiente (continuity-reconcile), no {doc['entry']!r}"
    )


def test_pd2_entry_continuity_reconcile_for_dispatched_packet(fx: _Fixture) -> None:
    """PD-2 borde: con `active_packet.status=dispatched` la selección es
    `continuity-reconcile` (reconciliar antes de repetir)."""
    fx.prepare()
    state = fx.read_state()
    state["active_packet"]["status"] = "dispatched"
    fx.write_state(state)
    doc = _status_document(fx.status())
    assert doc["packet"]["status"] == "dispatched", (
        f"fixture: el paquete activo no quedó `dispatched`: {doc['packet']!r}"
    )
    assert doc["entry"] == "continuity-reconcile", (
        "PD-2 violada: con un paquete `dispatched` la entrada debe reconciliar "
        f"antes de repetir (continuity-reconcile), no {doc['entry']!r}"
    )


def test_pd2_entry_next_unit_at_rest(fx: _Fixture) -> None:
    """PD-2: reposo sin trabajo pendiente (sin ejecución activa y sin paquete
    pendiente) → `next-unit` (procedimiento existente, project-start §6-§7)."""
    # Sin `prepare`: no hay ejecución activa ni paquete activo ni pendientes.
    doc = _status_document(fx.status())
    assert doc["entry"] == "next-unit", (
        "PD-2 violada: en reposo sin trabajo pendiente la entrada debe ser "
        f"next-unit, no {doc['entry']!r}"
    )


def test_pd2_entry_diagnosis_on_incomplete_config(fx: _Fixture) -> None:
    """PD-2: configuración incompleta (sin `docs/cdad-policy.json`) → la
    selección es `diagnosis`."""
    (fx.root / POLICY_REL).unlink()
    doc = _status_document(fx.status())
    assert doc["entry"] == "diagnosis", (
        "PD-2 violada: con configuración incompleta (sin la política del "
        f"proyecto) la entrada debe ser diagnosis, no {doc['entry']!r}"
    )


def test_pd2_entry_does_not_depend_on_literal_inicializar(fx: _Fixture) -> None:
    """PD-2 borde: la selección es un mapa explícito y NO depende del literal
    «inicializar» — un objetivo que contiene esa palabra no cambia la
    selección (con paquete pendiente sigue `continuity-reconcile`)."""
    fx.prepare(objective="inicializar el proyecto desde reposo")
    # El literal queda en una fuente declarada de la vista
    # (.cdad/packets/<id>/REQUEST.json, campo `objective`).
    request = next((fx.root / ".cdad" / "packets").glob("*/REQUEST.json"))
    assert "inicializar" in request.read_text(encoding="utf-8"), (
        "fixture: el literal «inicializar» no quedó en el REQUEST del paquete"
    )
    doc = _status_document(fx.status())
    assert doc["entry"] == "continuity-reconcile", (
        "PD-2 violada: el literal «inicializar» cambió la selección "
        f"({doc['entry']!r}); la selección no debe depender de esa palabra"
    )
    assert doc["entry"] != "next-unit", (
        "PD-2 violada: con paquete pendiente la selección cayó en next-unit "
        "(inferencia ingenua por el literal «inicializar»)"
    )


# ---------------------------------------------------------------- PD-5 / C4


def test_pd5_relative_root_accepted_projects_view(fx: _Fixture) -> None:
    """PD-5 — oráculo del comportamiento NUEVO que **supersede C4** por la
    fila 11 del plan de epic-005 (005-011 PD-2/PD-3): el comportamiento C4
    («la asimetría de raíz relativa se diagnostica en la salida de la vista»)
    queda superseded. Bajo la resolución unificada, `cdad_packet.py` resuelve
    una raíz relativa contra el cwd como los demás CLIs, así que
    `status --project-root .` con cwd = el proyecto ACEPTA la raíz y emite la
    proyección (rc=0)."""
    proc = fx.status(project_root=".", cwd=fx.root)
    doc = _status_document(proc)
    assert doc["entry"] in ENTRY_VALUES, (
        "PD-5/PD-2 violada: con raíz relativa la proyección no trae un `entry` "
        f"del mapa declarado: {doc['entry']!r}"
    )


# ---------------------------------------------------------------- INV-9


def test_inv9_unknowns_declare_causes_not_fabricated_zero(fx: _Fixture) -> None:
    """INV-9: `unknowns[]` declara causas de lo no proyectable y NUNCA un `0`
    fabricado; la ausencia se surfacea como tal (null), no como un valor
    inventado."""
    fx.prepare()
    doc = _status_document(fx.status())
    unknowns = doc["unknowns"]
    assert isinstance(unknowns, list), (
        f"INV-9 violada: `unknowns` no es una lista: {unknowns!r}"
    )
    for entry in unknowns:
        assert isinstance(entry, str) and entry.strip(), (
            f"INV-9 violada: entrada de `unknowns` sin causa: {entry!r}"
        )
        assert entry.strip() not in {"0", "0.0"}, (
            "INV-9 violada: `unknowns` declara un `0` fabricado en vez de una "
            f"causa: {entry!r}"
        )

    # En reposo no hay ejecución ni paquete: la ausencia se surfacea como null
    # (no como un objeto/valor inventado).
    rest = _status_document(_Fixture(fx.base / "rest").status())
    assert rest["execution"] is None, (
        f"INV-9/PD-1 violada: sin ejecución activa `execution` debe ser null, "
        f"no {rest['execution']!r}"
    )
    assert rest["packet"] is None, (
        f"INV-9/PD-1 violada: sin paquete activo `packet` debe ser null, no "
        f"{rest['packet']!r}"
    )
    assert isinstance(rest["unknowns"], list), (
        f"INV-9 violada: `unknowns` no es una lista en reposo: "
        f"{rest['unknowns']!r}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
