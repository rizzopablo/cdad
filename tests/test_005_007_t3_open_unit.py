#!/usr/bin/env python3
"""005-007 T3 RED — abrir la unidad siguiente con una operación del CLI
(`open-unit`), sin editar el state a mano (PD-7), y la observación 2 de la
revisión de Claude (dependencias declaradas).

Contract:
- docs/specs/005-007-progressive-planning/spec.md §2 (operación `open-unit`
  del CLI), §3 PD-7 (selección, efecto atómico, validaciones conservadas,
  autoridad, escritor único, precondición de reposo, ruta `next-unit` y
  `project-start.md` §6 por referencia) y PD-12 (fuente única, por
  referencia); §5 AC-2.
- docs/specs/005-007-progressive-planning/plan.md §4 ficha T3 (test focal
  declarado `tests/test_005_007_t3_open_unit.py`).
- docs/specs/005-007-progressive-planning/review-claude-spec-2026-10-13.md
  observación 2: `open-unit` verifica las dependencias declaradas de la
  entrada o declara explícitamente que no las verifica (el orden del plan es
  la autoridad); no abre en silencio una unidad cuya dependencia no está
  `done`.

Superficie observable bajo prueba (caja negra, mismo modo de invocación que
tests/test_005_003_t1_compact_view.py: SOLO subprocess sobre el CLI del
repo; el módulo NUNCA se importa y la implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py open-unit --project-root <ABS>
    python3 <skill-dir>/scripts/cdad_packet.py open-unit --project-root <ABS> --feature <ID>
    python3 <skill-dir>/scripts/cdad_packet.py validate-state --project-root <ABS>
    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>

El subcomando `open-unit` NO existe todavía: HOY el CLI responde con un
error de uso (rc=2, stderr «invalid choice: 'open-unit'», verificado por
sonda). Por eso cada test falla en la ASERCIÓN sobre el comportamiento del
contrato (efecto sobre el state, diagnóstico accionable, declaración de
dependencias, ruta que nombra la operación), nunca en la invocación ni en
una precondición de fixture: los fallos RED son AssertionError de contrato,
jamás ImportError, SyntaxError, JSONDecodeError ni error de setup. Los
fixtures son autocontenidos (proyectos sintéticos en tempdirs, patrón ya
existente de tests/test_005_003_t1_compact_view.py,
tests/test_005_003_f2_idle_history.py y tests/test_005_001_t3_idle.py:
build_project + `prepare` real + mutación declarada a reposo legítimo con
`epic_features` en cola) y el HOME del subproceso SIEMPRE es un tempdir
vacío (nunca el HOME real).

Mapeo test → postcondición/observación (PD-7 salvo el último tramo; obs = la
observación 2 del review):

  test_pd7_open_unit_opens_first_queued_unit
      -> PD-7 (caso APERTURA): desde reposo, UNA invocación sin `--feature`
         abre la PRIMERA entrada `queued` de `epic_features` (el orden del
         plan es la autoridad): active_feature = esa id; la entrada queda
         `in-progress` con `opened_at`; `current_stage = "discovery"`;
         `epic_stage` sin cambios; las demás `queued` permanecen; y
         `validate-state` queda verde después.
  test_pd7_second_invocation_with_open_unit_rejected_without_writes
      -> PD-7 (caso IDEMPOTENCIA/REPOSO): con una unidad ya abierta, una
         segunda invocación se RECHAZA (rc≠0) con diagnóstico accionable que
         nombra la unidad abierta (no un error de uso del CLI), sin
         escribir el state ni el árbol.
  test_pd7_feature_target_rejects_non_queued_or_unknown_unit
      -> PD-7 (selección): `--feature <ID>` sobre una entrada NO `queued`
         (done) o inexistente se rechaza (rc≠0) con diagnóstico accionable
         que nombra la unidad, sin escribir el state.
  test_pd7_no_shortcuts_authority_blocks_byte_identical
      -> PD-7 («conserva autoridad: no aprueba nada, no fabrica autoridad,
         no toca política, HITL ni versión»): tras abrir, `stage_history`,
         `approver`, `hitl_delegation` y `version` del state quedan
         idénticos y `docs/cdad-policy.json` queda byte-idéntico.
  test_obs2_declared_dependencies_verified_or_declared
      -> observación 2 (dependencias declaradas; PD-7 conserva
         validaciones): (a) si la entrada a abrir declara `depends_on` y
         alguna dependencia no está `done`, RECHAZA con diagnóstico que la
         nombra, sin abrir ni escribir; (b) si la entrada NO declara
         dependencias, la operación DECLARA EXPLÍCITAMENTE en su salida que
         no las verifica (el orden del plan es la autoridad) y abre.
  test_pd7_discovery_status_next_route_names_open_unit_and_project_start_documents_it
      -> PD-7 (DESCUBRIMIENTO): la ruta `next-unit` de la vista `status`
         NOMBRA la operación (`open-unit`) y
         `skills/cdad-cycle/references/project-start.md` la documenta por
         referencia (una sección que la nombre).

RED hoy (sonda declarada en el encargo): `open-unit` no existe → rc=2
«invalid choice» y NINGÚN efecto sobre el state; la ruta `next-unit` de
`status` hoy apunta a `project-start.md §6-§7` sin nombrar la operación; y
`project-start.md` no tiene sección que nombre `open-unit`. Cada caso
declara su fallo esperado en su docstring; el resumen final de pytest es la
prueba.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
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
# Superficie declarada por la ficha T3: `cdad_packet.py` de la skill
# instalada (el mismo CLI que la vista `status` de 005-003).
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"
PROJECT_START_REL = "skills/cdad-cycle/references/project-start.md"
CLI_TIMEOUT_S = 60

APPROVER = "Pablo"
# Fixture: A cerrada (historia), B primera `queued` (la unidad a abrir), C
# segunda `queued` (el orden del plan es la autoridad), D unidad pendiente
# usada como dependencia NO `done` (observación 2, caso (a)).
FEATURE_DONE = "004-002-project-execution-bootstrap"
FEATURE_FIRST_QUEUED = "005-007-progressive-planning"
FEATURE_SECOND_QUEUED = "005-008-next-unit-b"
FEATURE_PENDING_DEP = "005-009-dependency-pending"

IDLE = "idle"
DISCOVERY = "discovery"
IN_PROGRESS = "in-progress"
QUEUED = "queued"
DONE = "done"
USAGE_ERROR_TOKEN = "invalid choice"


# ---------------------------------------------------------------- helpers


class _Fixture:
    """Proyecto sintético autocontenido en un tempdir, con HOME aislado.

    Patrón de tests/test_005_003_t1_compact_view.py (build_project +
    `prepare` real por interfaz pública) + mutación declarada a REPOSO
    legítimo con cola `queued` (patrón de
    tests/test_005_003_f2_idle_history.py y tests/test_005_001_t3_idle.py):
    `active_feature` nulo, `current_stage` "idle", `active_packet` ausente,
    feature anterior `done` (el bloque `execution` queda como historia) y
    contratos pineados para las unidades `queued`.
    """

    def __init__(self, base: Path, mode: str = "rest") -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)
        self._prepare()  # precondición: ejecución real publicada en disco
        if mode == "rest":
            self._to_rest()
        elif mode == "open":
            self._assert_open()
        else:
            raise AssertionError(f"fixture: modo desconocido: {mode!r}")

    def _assert_open(self) -> None:
        """Modo «unidad ya abierta» (PD-7 IDEMPOTENCIA/REPOSO): el state
        que `prepare` publicó (unidad activa en tdd/red, paquete
        `prepared`). Precondición: es coherente hoy (validate-state rc=0)."""
        state = self.read_state()
        assert state["active_feature"] == FEATURE_DONE, (
            "precondición (fixture): la unidad abierta por `prepare` debe "
            f"estar activa: {state['active_feature']!r}")
        v = self.validate_state()
        assert v.returncode == 0, (
            "precondición (fixture, comportamiento existente): el state con "
            f"unidad abierta debe ser coherente hoy (validate-state rc=0): "
            f"{v.stdout!r} {v.stderr!r}")

    # -- construcción (interfaz pública, nunca implementación) ----------

    def _prepare(self) -> None:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        proc = self.run(*prepare_args(
            self.root, objective="005-007 T3 fixture"))
        assert proc.returncode == 0, (
            "precondición (fixture): `prepare` debe publicar la ejecución "
            f"(rc=0): {proc.stdout!r} {proc.stderr!r}")

    def _to_rest(self) -> None:
        """Mutación declarada del fixture a reposo legítimo con cola."""
        state = read_state(self.root)
        for fid in (FEATURE_FIRST_QUEUED, FEATURE_SECOND_QUEUED,
                    FEATURE_PENDING_DEP):
            spec_rel = f"docs/specs/{fid}/spec.md"
            path = self.root / spec_rel
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"# Spec fixture ({fid})\n".encode()
            path.write_bytes(data)
            state.setdefault("stage_history", []).append({
                "feature": fid,
                "stage": "specification",
                "approved_by": APPROVER,
                "approved_at": "2026-10-13T00:00:00Z",
                "contract_path": spec_rel,
                "contract_sha256": hashlib.sha256(data).hexdigest(),
            })
        state["epic_features"] = [
            {"id": FEATURE_DONE, "status": DONE},
            {"id": FEATURE_FIRST_QUEUED, "status": QUEUED},
            {"id": FEATURE_SECOND_QUEUED, "status": QUEUED},
        ]
        state["active_feature"] = None
        state["current_stage"] = IDLE
        state["tdd_substage"] = None
        state["active_packet"] = None
        write_state(self.root, state)
        # Precondición (fixture, comportamiento existente PD-13 de 005-001):
        # el reposo con cola es coherente hoy → validate-state verde.
        v = self.validate_state()
        assert v.returncode == 0 and IDLE in v.stdout, (
            "precondición (fixture): el reposo legítimo con cola `queued` "
            f"debe ser coherente hoy (validate-state rc=0): "
            f"{v.stdout!r} {v.stderr!r}")

    # -- mutaciones declaradas por caso --------------------------------

    def set_first_queued_depends_on(self, depends_on: list[str]) -> None:
        """La PRIMERA entrada `queued` declara `depends_on` (obs 2)."""
        state = read_state(self.root)
        for entry in state["epic_features"]:
            if entry["id"] == FEATURE_FIRST_QUEUED:
                entry["depends_on"] = list(depends_on)
        write_state(self.root, state)
        v = self.validate_state()
        assert v.returncode == 0, (
            "precondición (fixture): el reposo con `depends_on` declarado "
            f"debe ser coherente hoy: {v.stdout!r} {v.stderr!r}")

    # -- CLI (caja negra) ----------------------------------------------

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return env

    def run(self, *args: str) -> subprocess.CompletedProcess:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def open_unit(self, *extra: str) -> subprocess.CompletedProcess:
        return self.run("open-unit", "--project-root", str(self.root), *extra)

    def validate_state(self) -> subprocess.CompletedProcess:
        return self.run("validate-state", "--project-root", str(self.root))

    def status(self) -> subprocess.CompletedProcess:
        return self.run("status", "--project-root", str(self.root))

    # -- observación ----------------------------------------------------

    def read_state(self) -> dict:
        return read_state(self.root)

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def policy_bytes(self) -> bytes:
        return (self.root / POLICY_REL).read_bytes()

    def snapshot(self) -> dict:
        return tree_snapshot(self.root)


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


@pytest.fixture
def fx_open(tmp_path: Path) -> _Fixture:
    """Proyecto con UNIDAD YA ABIERTA (capa real de `prepare`, coherente
    hoy): fixture del caso PD-7 IDEMPOTENCIA/REPOSO."""
    return _Fixture(tmp_path, mode="open")


def _no_usage_error(label: str, proc: subprocess.CompletedProcess) -> None:
    """El rechazo NO es un error de uso del CLI (subcomando/argumento
    desconocido): es un rechazo de dominio del contrato (PD-7)."""
    out = proc.stdout + proc.stderr
    assert USAGE_ERROR_TOKEN not in out, (
        f"{label}: el rechazo es un error de uso del CLI "
        f"({USAGE_ERROR_TOKEN!r}), no el comportamiento del contrato PD-7 "
        f"(hoy `open-unit` no existe): {out!r}"
    )


# ---------------------------------------------------------------- PD-7


def test_pd7_open_unit_opens_first_queued_unit(fx: _Fixture) -> None:
    """PD-7 (caso APERTURA): desde reposo legítimo, UNA invocación de
    `open-unit` (sin `--feature`) abre la PRIMERA entrada `queued` de
    `epic_features` (el orden del plan es la autoridad): `active_feature` =
    esa id; la entrada queda `in-progress` con `opened_at`;
    `current_stage = "discovery"`; `epic_stage` sin cambios; las demás
    `queued` permanecen; y `validate-state` queda verde después.

    RED hoy: rc=2 «invalid choice: 'open-unit'» y ningún efecto sobre el
    state → falla la aserción del efecto (AssertionError del contrato).
    """
    before = fx.read_state()
    epic_stage_before = before["epic_stage"]

    proc = fx.open_unit()

    assert proc.returncode == 0, (
        "PD-7 violada (APERTURA): UNA invocación de `open-unit` debe abrir "
        f"la primera unidad `queued` (rc=0); hoy rc={proc.returncode} "
        f"(subcomando inexistente): {proc.stdout!r} {proc.stderr!r}"
    )
    state = fx.read_state()
    assert state["active_feature"] == FEATURE_FIRST_QUEUED, (
        f"PD-7 violada (APERTURA): `active_feature` debe ser la primera "
        f"entrada `queued` ({FEATURE_FIRST_QUEUED!r}, el orden del plan es "
        f"la autoridad): {state['active_feature']!r}"
    )
    opened = next(
        (e for e in state["epic_features"]
         if e["id"] == FEATURE_FIRST_QUEUED), None)
    assert opened is not None, (
        f"PD-7 violada (APERTURA): la entrada de "
        f"{FEATURE_FIRST_QUEUED!r} desapareció de `epic_features`"
    )
    assert opened["status"] == IN_PROGRESS, (
        f"PD-7 violada (APERTURA): la entrada abierta debe quedar "
        f"{IN_PROGRESS!r}: {opened!r}"
    )
    assert opened.get("opened_at"), (
        f"PD-7 violada (APERTURA): la entrada abierta debe registrar "
        f"`opened_at`: {opened!r}"
    )
    assert state["current_stage"] == DISCOVERY, (
        f"PD-7 violada (APERTURA): `current_stage` debe ser "
        f"{DISCOVERY!r} (la etapa de entrada): {state['current_stage']!r}"
    )
    assert state["epic_stage"] == epic_stage_before, (
        f"PD-7 violada (APERTURA): `epic_stage` debe quedar sin cambios "
        f"({epic_stage_before!r}): {state['epic_stage']!r}"
    )
    still_queued = [e["id"] for e in state["epic_features"]
                    if e["status"] == QUEUED]
    assert still_queued == [FEATURE_SECOND_QUEUED], (
        f"PD-7 violada (APERTURA): sólo {FEATURE_SECOND_QUEUED!r} debe "
        f"seguir `queued` tras abrir {FEATURE_FIRST_QUEUED!r}: "
        f"{still_queued!r}"
    )
    v = fx.validate_state()
    assert v.returncode == 0, (
        f"PD-7 violada (APERTURA): `validate-state` debe quedar verde tras "
        f"abrir (rc=0): {v.stdout!r} {v.stderr!r}"
    )


def test_pd7_second_invocation_with_open_unit_rejected_without_writes(
        fx_open: _Fixture) -> None:
    """PD-7 (caso IDEMPOTENCIA/REPOSO): con una unidad ya abierta, una
    segunda invocación de `open-unit` se RECHAZA (rc≠0) con diagnóstico
    accionable que nombra la unidad abierta (no un error de uso del CLI),
    sin escribir el state ni el árbol.

    RED hoy: rc=2 por «invalid choice» (no es el rechazo del contrato)
    → fallan la aserción de rechazo de dominio y la del diagnóstico.
    """
    # Unidad ya abierta: ejecución activa real publicada por `prepare`
    # (precondición del fixture, comportamiento existente).
    assert fx_open.read_state()["active_feature"] == FEATURE_DONE, (
        "precondición (fixture): la unidad ya abierta debe estar activa")
    before = fx_open.snapshot()
    state_before = fx_open.state_bytes()

    proc = fx_open.open_unit()

    assert proc.returncode != 0, (
        "PD-7 violada (IDEMPOTENCIA/REPOSO): con una unidad ya abierta, "
        f"`open-unit` debe rechazar (rc≠0): {proc.stdout!r} {proc.stderr!r}"
    )
    _no_usage_error("PD-7 (IDEMPOTENCIA/REPOSO)", proc)
    out = proc.stdout + proc.stderr
    assert FEATURE_DONE in out, (
        "PD-7 violada (IDEMPOTENCIA/REPOSO): el diagnóstico debe ser "
        "accionable y nombrar la unidad ya abierta "
        f"({FEATURE_DONE!r}): {out!r}"
    )
    assert fx_open.state_bytes() == state_before, (
        "PD-7 violada (IDEMPOTENCIA/REPOSO): el rechazo debe ocurrir SIN "
        "escribir el state"
    )
    assert fx_open.snapshot() == before, (
        "PD-7 violada (IDEMPOTENCIA/REPOSO): el rechazo debe ocurrir sin "
        "efectos sobre el árbol del proyecto"
    )


def test_pd7_feature_target_rejects_non_queued_or_unknown_unit(
        fx: _Fixture) -> None:
    """PD-7 (selección): `--feature <ID>` sobre una entrada NO `queued`
    (aquí `done`) o inexistente se rechaza (rc≠0) con diagnóstico
    accionable que nombra la unidad (y la condición `queued`), sin escribir
    el state.

    RED hoy: rc=2 por «invalid choice» → fallan la aserción de rechazo de
    dominio y la del diagnóstico, para cada variante.
    """
    for label, target in (
        ("entrada no queued (done)", FEATURE_DONE),
        ("entrada inexistente", "005-007-nonexistent-unit"),
    ):
        state_before = fx.state_bytes()
        proc = fx.open_unit("--feature", target)
        assert proc.returncode != 0, (
            f"PD-7 violada ({label}): `--feature {target}` debe "
            f"rechazarse (rc≠0): {proc.stdout!r} {proc.stderr!r}"
        )
        _no_usage_error(f"PD-7 ({label})", proc)
        out = proc.stdout + proc.stderr
        assert target in out and QUEUED in out, (
            f"PD-7 violada ({label}): el diagnóstico debe ser accionable y "
            f"nombrar la unidad ({target!r}) y la condición {QUEUED!r}: "
            f"{out!r}"
        )
        assert fx.state_bytes() == state_before, (
            f"PD-7 violada ({label}): el rechazo debe ocurrir SIN escribir "
            f"el state"
        )


def test_pd7_no_shortcuts_authority_blocks_byte_identical(
        fx: _Fixture) -> None:
    """PD-7 («conserva autoridad: no aprueba nada, no fabrica autoridad, no
    toca política, HITL ni versión»): tras abrir, `stage_history` (sin
    aprobaciones nuevas), `approver`, `hitl_delegation` y `version` del
    state quedan idénticos, y `docs/cdad-policy.json` queda byte-idéntico.

    RED hoy: la aserción de apertura (rc=0) falla primero — es la del
    contrato; las de identidad se evalúan sobre el efecto esperado.
    """
    state_before = copy.deepcopy(fx.read_state())
    policy_before = fx.policy_bytes()

    proc = fx.open_unit()

    assert proc.returncode == 0, (
        "PD-7 violada (NO-ATAJOS): la apertura debe ocurrir (rc=0) para "
        f"evaluar la conservación de autoridad; hoy rc={proc.returncode} "
        f"(subcomando inexistente): {proc.stdout!r} {proc.stderr!r}"
    )
    state = fx.read_state()
    assert state["stage_history"] == state_before["stage_history"], (
        "PD-7 violada (NO-ATAJOS): `open-unit` NO debe aprobar nada "
        "(`stage_history` cambió)"
    )
    assert state["approver"] == state_before["approver"], (
        "PD-7 violada (NO-ATAJOS): `approver` cambió (no se fabrica "
        "autoridad)"
    )
    assert state["hitl_delegation"] == state_before["hitl_delegation"], (
        "PD-7 violada (NO-ATAJOS): `hitl_delegation` cambió"
    )
    assert state["version"] == state_before["version"], (
        "PD-7 violada (NO-ATAJOS): `version` cambió"
    )
    assert fx.policy_bytes() == policy_before, (
        "PD-7 violada (NO-ATAJOS): la política "
        f"({POLICY_REL}) no debe tocarse"
    )


def test_obs2_declared_dependencies_verified_or_declared(
        fx: _Fixture) -> None:
    """Observación 2 del review de Claude (dependencias declaradas; PD-7
    conserva validaciones):
    (a) si la entrada a abrir declara `depends_on` y alguna dependencia NO
        está `done`, `open-unit` RECHAZA con diagnóstico que la nombra, sin
        abrir ni escribir;
    (b) si la entrada NO declara dependencias, la operación DECLARA
        EXPLÍCITAMENTE en su salida que no las verifica (el orden del plan
        es la autoridad) y abre la unidad.

    RED hoy: rc=2 por «invalid choice» → (a) falla en el rechazo de dominio
    y el diagnóstico que nombra la dependencia; (b) falla en la declaración
    explícita (la salida de hoy no menciona dependencias).
    """
    # (a) dependencia declarada NO done → rechazo que la nombra, sin abrir.
    fx.set_first_queued_depends_on([FEATURE_PENDING_DEP])
    state_before = fx.state_bytes()
    proc = fx.open_unit()
    assert proc.returncode != 0, (
        "obs 2 (a) violada: con una dependencia declarada no `done`, "
        f"`open-unit` debe rechazar (rc≠0): {proc.stdout!r} {proc.stderr!r}"
    )
    _no_usage_error("obs 2 (a)", proc)
    out = proc.stdout + proc.stderr
    assert FEATURE_PENDING_DEP in out, (
        "obs 2 (a) violada: el diagnóstico debe nombrar la dependencia no "
        f"`done` ({FEATURE_PENDING_DEP!r}): {out!r}"
    )
    assert fx.state_bytes() == state_before, (
        "obs 2 (a) violada: el rechazo debe ocurrir sin abrir y sin "
        "escribir el state"
    )

    # (b) sin dependencias declaradas → abre y DECLARA que no las verifica.
    fx2 = _Fixture(fx.base.parent / "nodeps")
    proc2 = fx2.open_unit()
    assert proc2.returncode == 0, (
        "obs 2 (b) violada: sin dependencias declaradas, `open-unit` debe "
        f"abrir la unidad (rc=0): {proc2.stdout!r} {proc2.stderr!r}"
    )
    out2 = proc2.stdout + proc2.stderr
    assert "dependenc" in out2.lower(), (
        "obs 2 (b) violada: la salida debe DECLARAR EXPLÍCITAMENTE que no "
        "verifica dependencias (el orden del plan es la autoridad); la "
        f"salida no menciona dependencias: {out2!r}"
    )
    state2 = fx2.read_state()
    assert state2["active_feature"] == FEATURE_FIRST_QUEUED, (
        "obs 2 (b) violada: sin dependencias declaradas la unidad debe "
        f"abrirse (el orden del plan es la autoridad): "
        f"{state2['active_feature']!r}"
    )


def test_pd7_discovery_status_next_route_names_open_unit_and_project_start_documents_it(
        fx: _Fixture) -> None:
    """PD-7 (DESCUBRIMIENTO): la ruta `next-unit` de la vista `status`
    NOMBRA la operación (`open-unit`) y
    `skills/cdad-cycle/references/project-start.md` la documenta por
    referencia (una sección que la nombre).

    RED hoy: la ruta emite «next unit (project-start.md §6-§7)» sin nombrar
    la operación, y `project-start.md` no tiene sección que nombre
    `open-unit` → ambas aserciones del contrato fallan.
    """
    proc = fx.status()
    assert proc.returncode == 0, (
        "precondición (fixture, comportamiento existente 005-003): la vista "
        f"`status` debe emitir la proyección (rc=0): "
        f"{proc.stdout!r} {proc.stderr!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover
        raise AssertionError(
            "precondición (fixture): stdout de `status` no es un documento "
            f"JSON válido: {proc.stdout[:200]!r}"
        ) from exc
    assert doc.get("entry") == "next-unit", (
        "precondición (fixture, comportamiento existente F2): en reposo con "
        f"cola la vista debe emitir `entry=next-unit`: {doc.get('entry')!r}"
    )
    assert "open-unit" in json.dumps(doc.get("next")), (
        "PD-7 violada (DESCUBRIMIENTO): la ruta `next-unit` de `status` "
        "debe NOMBRAR la operación (`open-unit`): "
        f"{json.dumps(doc.get('next'), ensure_ascii=False)!r}"
    )

    # `project-start.md` la documenta por referencia: una SECCIÓN (bloque
    # bajo un encabezado) que nombre `open-unit`.
    project_start = REPO_ROOT / PROJECT_START_REL
    assert project_start.is_file(), (
        f"precondición (fixture): {PROJECT_START_REL} debe existir en el "
        f"repo")
    lines = project_start.read_text(encoding="utf-8").splitlines()
    sections: list[tuple[str, str]] = []
    heading = ""
    body: list[str] = []
    for line in lines:
        if line.startswith("#"):
            if heading:
                sections.append((heading, "\n".join(body)))
            heading, body = line, []
        else:
            body.append(line)
    if heading:
        sections.append((heading, "\n".join(body)))
    named = [h for h, b in sections if "open-unit" in f"{h}\n{b}"]
    assert named, (
        f"PD-7 violada (DESCUBRIMIENTO): {PROJECT_START_REL} debe "
        f"documentar `open-unit` por referencia (una sección que la "
        f"nombre); secciones: {[h for h, _ in sections]!r}"
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
