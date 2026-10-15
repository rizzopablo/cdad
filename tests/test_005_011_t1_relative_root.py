#!/usr/bin/env python3
"""005-011 T1 RED — raíz relativa consistente en `cdad_packet.py` (PD-2, PD-3).

Contract:
- docs/specs/005-011-common-entry/spec.md §2.2 (`project-root-v1`), §3 PD-2/PD-3,
  §5 AC-2/AC-3.
- docs/specs/005-011-common-entry/plan.md §4 (T1) y la fila 11 del plan del
  epic-005, que **supersede** el comportamiento C4 de 005-003 (spec §2.2/PD-3).

Superficie observable bajo prueba (proyectos sintéticos en tempdirs; caja negra:
SOLO subprocess sobre el CLI del repo; el módulo NUNCA se importa y la
implementación NUNCA se lee al escribir este test):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root .
    python3 <skill-dir>/scripts/cdad_packet.py validate-state --project-root .
    python3 <skill-dir>/scripts/cdad_packet.py validate-policy --project-root .

Comportamiento VIGENTE (antes del GREEN): `cdad_packet.py` rechaza una raíz
relativa (`ERROR: --project-root must be an absolute existing directory: .`,
rc=2, sin proyección), mientras `cdad_continuity.py` la resuelve contra el cwd.
PD-2 **unifica** la resolución a «resolver contra el cwd y exigir `is_dir()`».
Por eso los oráculos del cambio fallan HOY en la ASERCIÓN sobre el rc / la
proyección / la consistencia entre subcomandos, nunca en la invocación: los
fallos RED son AssertionError de contrato, jamás ImportError, SyntaxError,
JSONDecodeError ni error de setup. Los fixtures son autocontenidos (tempdirs
armados por el test; sin datos de demo, sin la base real de sesiones, sin rutas
de este host) y el HOME del subproceso SIEMPRE es un tempdir vacío.

Mapeo test → postcondición/criterio (uno por afirmación observable):
  test_pd2_status_accepts_relative_root_with_projection
      -> PD-2 / AC-2: `status --project-root .` (cwd = fixture) → rc=0 CON
         proyección (hoy rc=2 sin proyección)
  test_pd2_relative_root_consistent_across_subcommands
      -> PD-2 / AC-2: los demás subcomandos aceptan la raíz relativa de forma
         consistente (`validate-state` y `validate-policy` con `.`)
  test_pd2_nonexistent_root_fails_closed_naming_cause
      -> PD-2 borde: una raíz que NO es un directorio existente sigue fallando
         cerrado, con un diagnóstico que nombra la causa (`existing directory`)
         y SIN proyección parcial
  test_pd2_status_without_flag_still_uses_cwd
      -> PD-2 borde / control de no-regresión: sin bandera se sigue usando el
         cwd (el default `:4297-4298` no cambia)
  test_pd2_other_validations_unchanged_with_relative_root
      -> PD-2 / AC-2 control: con la raíz relativa, la clasificación de la
         política, el hashing del contrato y la validación del paquete siguen
         funcionando — el veredicto es el mismo que con la raíz absoluta
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import build_project, read_state

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.2: `python3 <skill-dir>/scripts/cdad_packet.py`.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
CLI_TIMEOUT_S = 60

# Campos mínimos de la proyección (§2.1 de 005-003, referenciado por la spec
# §2.2): prueban que hay proyección real, no un documento vacío.
PROJECTION_FIELDS = (
    "project", "epic", "feature", "execution", "packet",
    "authority", "version", "next", "entry", "unknowns",
)


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

    def run(self, argv: list[str], cwd: Path | None = None
            ) -> subprocess.CompletedProcess:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        return subprocess.run(
            [sys.executable, str(CLI), *argv],
            capture_output=True, text=True,
            cwd=str(REPO_ROOT if cwd is None else cwd), env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def prepare(self) -> subprocess.CompletedProcess:
        return self.run([
            "prepare", "--project-root", str(self.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "005-011 T1 fixture",
        ])

    def packet_paths(self) -> tuple[Path, Path, Path]:
        """(REQUEST.json, PACKET.md, execution.json) del paquete activo."""
        state = read_state(self.root)
        packet_id = (state.get("active_packet") or {}).get("id")
        assert packet_id, "fixture: no hay paquete activo tras `prepare`"
        execution_id = (state.get("execution") or {}).get("id")
        assert execution_id, "fixture: no hay binding de ejecución tras `prepare`"
        packet_dir = self.root / ".cdad" / "packets" / packet_id
        request = packet_dir / "REQUEST.json"
        packet = packet_dir / "PACKET.md"
        context = (self.root / ".cdad" / "executions" / execution_id
                   / "execution.json")
        for path in (request, packet, context):
            assert path.is_file(), f"fixture: falta el artefacto {path}"
        return request, packet, context


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


def _projection(proc: subprocess.CompletedProcess) -> dict:
    """La proyección JSON de la vista, o AssertionError de contrato.

    Nunca deja escapar un JSONDecodeError (fallo de setup): si la vista no
    emitió la proyección del contrato, la aserción lo declara.
    """
    assert proc.returncode == 0, (
        "PD-2 violada: con raíz relativa la vista `status` debe aceptarla y "
        f"emitir la proyección (rc=0); hoy rc={proc.returncode}; "
        f"stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "PD-2 violada: con raíz relativa la vista no emitió el documento por "
        f"stdout; stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "PD-2 violada: stdout no es un ÚNICO documento JSON válido: "
            f"{proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"PD-2 violada: la proyección de la vista no es un objeto JSON: {doc!r}"
    )
    missing = [k for k in PROJECTION_FIELDS if k not in doc]
    assert not missing, (
        "PD-2 violada: con raíz relativa la proyección no trae los campos del "
        f"contrato: faltan {missing}; documento: {sorted(doc)}"
    )
    return doc


# ---------------------------------------------------------------- PD-2


def test_pd2_status_accepts_relative_root_with_projection(fx: _Fixture) -> None:
    """PD-2/AC-2: `status --project-root .` con cwd = el proyecto resuelve la
    raíz relativa contra el cwd y emite la proyección (rc=0). Hoy el CLI la
    rechaza (rc=2, sin proyección)."""
    proc = fx.run(["status", "--project-root", "."], cwd=fx.root)
    doc = _projection(proc)
    # La proyección es la del proyecto bajo el cwd, no la de otro árbol.
    assert doc["entry"] in {"continuity-reconcile", "next-unit", "diagnosis"}, (
        f"PD-2 violada: `entry` fuera del mapa declarado: {doc['entry']!r}"
    )


def test_pd2_relative_root_consistent_across_subcommands(fx: _Fixture) -> None:
    """PD-2/AC-2: los demás subcomandos aceptan la raíz relativa de forma
    consistente — `validate-state` y `validate-policy` con `.` sobre el fixture
    resuelven contra el cwd y su veredicto es EQUIVALENTE al de la raíz absoluta
    (antes del GREEN: rc=2 por el rechazo especial).

    Setup (no es la aserción): `validate-state` exige un binding de ejecución
    activo y el fixture `build_project` deja `execution: None`; el rechazo de un
    estado SIN binding es el oráculo preexistente
    `tests/test_005_001_t3_idle.py` y NO se toca. Se prepara el fixture con
    `prepare()` — el mismo setup que usa el control de PD-2 — para que la
    aserción dependa de la resolución de la RAÍZ, no del binding."""
    prepared = fx.prepare()
    assert prepared.returncode == 0, (
        "fixture: `prepare` del proyecto sintético debe tener éxito; "
        f"rc={prepared.returncode}; stderr={prepared.stderr.strip()!r}"
    )

    # Equivalencia relativa-vs-absoluta: la raíz absoluta es el control.
    absolute = fx.run(["validate-state", "--project-root", str(fx.root)])
    state = fx.run(["validate-state", "--project-root", "."], cwd=fx.root)
    assert absolute.returncode == 0, (
        "fixture/PD-2 control: `validate-state` con raíz absoluta debe ser "
        f"VÁLIDO; rc={absolute.returncode}; stderr={absolute.stderr.strip()!r}"
    )
    assert state.returncode == absolute.returncode, (
        "PD-2 violada: `validate-state --project-root .` debe resolver la raíz "
        "relativa contra el cwd y dar el MISMO veredicto que la raíz absoluta; "
        f"hoy rc={state.returncode} != {absolute.returncode}; "
        f"stderr={state.stderr.strip()!r}"
    )
    assert re.search(r"(?i)\bVALID\b", state.stdout + state.stderr), (
        "PD-2 violada: `validate-state` con raíz relativa no emitió su veredicto "
        f"VÁLIDO: stdout={state.stdout.strip()!r} stderr={state.stderr.strip()!r}"
    )

    policy = fx.run(["validate-policy", "--project-root", "."], cwd=fx.root)
    assert policy.returncode == 0, (
        "PD-2 violada: `validate-policy --project-root .` debe resolver la raíz "
        f"relativa contra el cwd (rc=0); hoy rc={policy.returncode}; "
        f"stderr={policy.stderr.strip()!r}"
    )
    assert re.search(r"(?i)\bVALID\b", policy.stdout + policy.stderr), (
        "PD-2 violada: `validate-policy` con raíz relativa no emitió su "
        f"veredicto VÁLIDO: stdout={policy.stdout.strip()!r} "
        f"stderr={policy.stderr.strip()!r}"
    )


def test_pd2_nonexistent_root_fails_closed_naming_cause(fx: _Fixture) -> None:
    """PD-2 borde: una raíz que NO es un directorio existente sigue fallando
    cerrado (rc≠0), con un diagnóstico que nombra la causa (`existing
    directory`) y SIN proyección parcial por stdout."""
    missing = fx.base / "missing-root"
    assert not missing.exists(), "fixture: la raíz inexistente no debe existir"

    for argv in (["status"], ["validate-state"], ["validate-policy"]):
        proc = fx.run([*argv, "--project-root", str(missing)])
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0, (
            "PD-2 violada: una raíz inexistente fue aceptada por "
            f"`{argv[0]}` (rc={proc.returncode})"
        )
        assert proc.stdout.strip() == "", (
            "PD-2 violada: una raíz inexistente falló cerrado pero emitió una "
            f"proyección parcial por stdout (`{argv[0]}`): "
            f"{proc.stdout[:200]!r}"
        )
        assert "Traceback" not in proc.stderr, (
            f"PD-2 violada: el fallo cerrado de `{argv[0]}` es un traceback: "
            f"{out.strip()!r}"
        )
        assert re.search(r"(?i)existing directory", out), (
            "PD-2 violada: el diagnóstico no nombra la causa (que la raíz debe "
            f"ser un directorio existente) en `{argv[0]}`: {out.strip()!r}"
        )


def test_pd2_status_without_flag_still_uses_cwd(fx: _Fixture) -> None:
    """PD-2 borde / control de no-regresión: sin `--project-root` la vista sigue
    usando el cwd (default `:4297-4298`) y emite la proyección (rc=0)."""
    proc = fx.run(["status"], cwd=fx.root)
    _projection(proc)


def test_pd2_other_validations_unchanged_with_relative_root(fx: _Fixture) -> None:
    """PD-2/AC-2 control: con la raíz relativa aceptada, NINGUNA otra validación
    cambia — la clasificación de la política, el hashing del contrato y la
    validación del paquete siguen funcionando y su veredicto es el MISMO que con
    la raíz absoluta (misma entrada lógica → mismo rc y misma salida)."""
    prepared = fx.prepare()
    assert prepared.returncode == 0, (
        "fixture: `prepare` del proyecto sintético debe tener éxito; "
        f"rc={prepared.returncode}; stderr={prepared.stderr.strip()!r}"
    )
    request, packet, context = fx.packet_paths()

    probes = {
        "validate-policy": ["validate-policy"],
        "validate-state": ["validate-state"],
        "validate-request": [
            "validate-request", "--execution-context", str(context),
            "--request", str(request),
        ],
        "validate-packet": [
            "validate-packet", "--execution-context", str(context),
            "--request", str(request), "--packet", str(packet),
        ],
    }
    for name, extra in probes.items():
        absolute = fx.run([*extra, "--project-root", str(fx.root)])
        relative = fx.run([*extra, "--project-root", "."], cwd=fx.root)
        assert absolute.returncode == 0, (
            f"fixture/PD-2 control: `{name}` con raíz absoluta debe ser VÁLIDO; "
            f"rc={absolute.returncode}; stderr={absolute.stderr.strip()!r}"
        )
        assert relative.returncode == absolute.returncode, (
            f"PD-2 violada: `{name}` con raíz relativa cambió su veredicto "
            f"respecto de la raíz absoluta (rc {relative.returncode} != "
            f"{absolute.returncode}); stderr={relative.stderr.strip()!r}"
        )
        assert relative.stdout == absolute.stdout, (
            f"PD-2 violada: `{name}` con raíz relativa emitió otra salida que "
            "con la raíz absoluta (la validación no debe cambiar): "
            f"{relative.stdout[:200]!r} != {absolute.stdout[:200]!r}"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
