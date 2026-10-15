#!/usr/bin/env python3
"""005-012 T6 RED — `prepare --new-execution` rechaza el contexto de ejecución
ya abierto y sin uso (PD-16).

Contract:
- docs/specs/005-012-transition-registration/spec.md §2.3 PD-16 (contexto de
  ejecución abierto y sin uso), §2.4 INV-7 (fallo cerrado sin efectos) y
  PD-17 (aditividad: `validate-state` rc=0 antes y después), §4 (instrumento:
  CLI real como subproceso, proyecto descartable, HOME vacío).
- docs/specs/005-012-transition-registration/plan.md §4 ficha T6 (test focal
  declarado `tests/test_005_012_t6_open_context_guard.py`), §5 D-9 (alcance
  acotado del rechazo) y §2 (T6 = cierre mecánico pedido a esta unidad).
- docs/specs/005-013-unit-contract/debt.md:60-64 (la ejecución huérfana que
  este cierre salda) y docs/specs/005-012-transition-registration/
  discovery.md §4.2 (la causa: `prepare --new-execution` ignora el contexto
  previo por construcción).

Superficie observable (caja negra: SOLO subprocess sobre el CLI del repo; el
módulo de implementación NUNCA se importa y su código NUNCA se lee):

    python3 <skill>/scripts/cdad_packet.py prepare --project-root <ABS> \\
        --role <rol> --substage <sub> --objective <texto> --new-execution
    python3 <skill>/scripts/cdad_packet.py prepare --project-root <ABS> ...   (reuso)
    python3 <skill>/scripts/cdad_packet.py open-unit --project-root <ABS>
    python3 <skill>/scripts/cdad_packet.py validate-state --project-root <ABS>

RED hoy (sonda declarada): `open-unit` existe y, desde reposo con cola, abre la
unidad acuñando su contexto v2 (`state.execution` = `exec-<feature>-001`, sin
paquetes publicados, sin despachos y con `active_packet` nulo). Un
`prepare --new-execution` inmediato NO se rechaza: da rc=0 y acuña un SEGUNDO
id (`…-002`) — exactamente el caso real de 005-013. Por eso el caso 1 falla en
la ASERCIÓN del contrato (rc=2 + marcador + diagnóstico), nunca en la
invocación ni en una precondición de fixture: los fallos RED son
AssertionError, jamás ImportError, SyntaxError, JSONDecodeError ni error de
setup.

Aislamiento de causas (caso 1, declarado). El fixture del rechazo monta el
contexto abierto SIN USO —`open-unit` no publica ningún paquete, no deja
`active_packet` y no crea despachos— y NINGUNA otra causa posible de rc≠0 en
`prepare`: política válida, feature activa `in-progress` con contrato
pineado en `stage_history`, `hitl_delegation` activa con `source` existente y
`active_packet` nulo. Hoy la MISMA invocación da rc=0 (sonda), así que el rc=2
del contrato es atribuible sólo al guard. Declarado, no inferido.

Casos NO cubiertos (declarado, no asertado). El contexto abierto CON uso (un
paquete ya publicado con su `execution_id`) queda fuera del alcance de T6
(ficha T6, «Excluido: … cubrir un contexto con paquetes … deuda D-5») y no
tiene caso observable limpio: con un paquete publicado la misma invocación
falla por OTRA causa (la precondición de paquete activo, PD-4 de 004-002), de
modo que el no-disparo del guard no es separable sin asertar comportamiento
que la spec no fija. Se declara en el informe; no se asevera acá.

Mapeo test → postcondición:

  test_pd16_new_execution_with_open_unused_context_is_rejected_naming_it
      -> PD-16 (caso RECHAZO): rc=2, marcador `state incoherent`, diagnóstico
         que nombra el contexto ya abierto y cómo seguir, sin acuñar un
         segundo id (el directorio de ejecuciones no crece, el state byte a
         byte idéntico); `validate-state` rc=0 antes y después (PD-17/INV-7).
  test_pd16_new_execution_without_prior_context_still_publishes
      -> PD-16 (CONTROL POSITIVO): sin contexto abierto previo, la invocación
         sigue funcionando (rc=0), acuña un id nuevo y publica el paquete.
  test_pd16_reuse_path_without_new_execution_keeps_working
      -> PD-16 (camino de REUSO intacto): tras `open-unit`, un `prepare` SIN
         `--new-execution` sigue rc=0 y reusa el contexto abierto.

El fixture es un proyecto descartable en un tempdir (política válida, state
sintético, contrato pineado, ejecución v2 y paquete reales por el camino
legítimo del CLI) y el HOME del subproceso es un tempdir VACÍO: nunca el repo
real, nunca HOME. Ids sintéticos y anónimos.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    build_project,
    prepare_args,
    published_packets,
    read_state,
    tree_snapshot,
    v2_execution_docs,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §4/§2.1: el CLI del repo.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
STATE_REL = "docs/.cdad-state.json"
CLI_TIMEOUT_S = 90

# Fixture sintético y anónimo (ids inventados; ningún proyecto real).
FEATURE_OPEN = "005-012-t6-open-context-fixture"
FEATURE_SECOND_QUEUED = "005-012-t6-second-queued-fixture"
APPROVER = "Demo Approver"

# Vocabulario del state (valores existentes, no inventados).
DONE = "done"
QUEUED = "queued"
IN_PROGRESS = "in-progress"
IDLE = "idle"
DISCOVERY = "discovery"

# Marcador declarado por PD-16.
STATE_INCOHERENT = "state incoherent"
PACKET_BEGIN = "---cdad-packet-json"


# ---------------------------------------------------------------- helpers


class _Fixture:
    """Proyecto descartable en un tempdir, con el HOME del subproceso aislado.

    Modos:
      - `fresh`: proyecto nuevo, SIN contexto de ejecución previo (control
        positivo de PD-16).
      - `rest`: reposo legítimo con cola `queued` (patrón de
        tests/test_005_007_t3_open_unit.py) más una ejecución real publicada
        por `prepare` que queda como historia.
      - `open`: `rest` + `open-unit`, que abre la unidad y acuña su contexto v2
        dejándolo SIN USO (sin paquetes con su `execution_id`, sin despachos).

    Toda la capa previa se produce por el camino legítimo del CLI (`prepare`,
    `open-unit`): son precondiciones de comportamiento EXISTENTE y se asertan
    como tales.
    """

    def __init__(self, base: Path, mode: str = "rest") -> None:
        assert mode in ("fresh", "rest", "open"), mode
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)
        if mode == "fresh":
            return
        self._prepare()
        self._to_rest()
        if mode == "open":
            self._open_unit()

    # -- construcción (interfaz pública del CLI, nunca implementación) ----

    def _prepare(self) -> None:
        assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
        proc = self.run(*prepare_args(
            self.root, objective="005-012 T6 fixture (historia)"))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente): `prepare` debe "
            f"publicar la ejecución (rc=0): {proc.stdout!r} {proc.stderr!r}")

    def _to_rest(self) -> None:
        """Mutación declarada del fixture a reposo legítimo con cola.

        Patrón de tests/test_005_007_t3_open_unit.py: la feature anterior queda
        `done`, la primera `queued` (la que abre `open-unit`) y una segunda
        `queued` (el orden del plan es la autoridad), y los contratos de las
        unidades en cola quedan pineados en `stage_history`.
        """
        state = read_state(self.root)
        history_feature = state["active_feature"]
        assert history_feature, (
            "precondición (fixture): `prepare` debe haber dejado una feature "
            "activa cuyo bloque `execution` quede como historia")
        for fid in (FEATURE_OPEN, FEATURE_SECOND_QUEUED):
            spec_rel = f"docs/specs/{fid}/spec.md"
            path = self.root / spec_rel
            path.parent.mkdir(parents=True, exist_ok=True)
            data = f"# Spec fixture ({fid})\n".encode()
            path.write_bytes(data)
            state.setdefault("stage_history", []).append({
                "feature": fid,
                "stage": "specification",
                "approved_by": APPROVER,
                "approved_at": "2026-10-14T00:00:00Z",
                "contract_path": spec_rel,
                "contract_sha256": hashlib.sha256(data).hexdigest(),
            })
        state["epic_features"] = [
            {"id": history_feature, "status": DONE},
            {"id": FEATURE_OPEN, "status": QUEUED},
            {"id": FEATURE_SECOND_QUEUED, "status": QUEUED},
        ]
        state["active_feature"] = None
        state["current_stage"] = IDLE
        state["tdd_substage"] = None
        state["active_packet"] = None
        self.write_state(state)
        # Precondición (fixture, comportamiento existente): el reposo con cola
        # es coherente hoy → validate-state verde.
        v = self.validate_state()
        assert v.returncode == 0 and IDLE in v.stdout, (
            "precondición (fixture): el reposo legítimo con cola `queued` debe "
            f"ser coherente hoy (validate-state rc=0): {v.stdout!r} "
            f"{v.stderr!r}")

    def _open_unit(self) -> None:
        """`open-unit` abre la unidad y acuña su contexto v2 (sin uso).

        Precondición del caso PD-16 (RECHAZO): el contexto abierto queda SIN
        USO —sin paquetes publicados con su `execution_id`, sin despachos y con
        `active_packet` nulo— y el state sigue siendo coherente.
        """
        self.packets_before_open: dict[str, bytes] = dict(
            published_packets(self.root))
        proc = self.run("open-unit", "--project-root", str(self.root))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente 005-007 PD-7): "
            f"`open-unit` debe abrir la unidad (rc=0): {proc.stdout!r} "
            f"{proc.stderr!r}")
        state = read_state(self.root)
        assert state["active_feature"] == FEATURE_OPEN, (
            "precondición (fixture): `open-unit` debe abrir la PRIMERA unidad "
            f"`queued` ({FEATURE_OPEN!r}): {state['active_feature']!r}")
        assert state.get("execution") and state["execution"].get("id"), (
            "precondición (fixture): `open-unit` debe dejar un contexto de "
            f"ejecución activo: {state.get('execution')!r}")
        assert state.get("active_packet") is None, (
            "precondición (fixture): el contexto abierto está SIN USO y no "
            f"deja paquete activo: {state.get('active_packet')!r}")
        assert published_packets(self.root) == self.packets_before_open, (
            "precondición (fixture): `open-unit` no debe publicar paquetes "
            "(sin uso del contexto abierto)")
        v = self.validate_state()
        assert v.returncode == 0, (
            "precondición (fixture): el state con el contexto abierto debe ser "
            f"coherente hoy: {v.stdout!r} {v.stderr!r}")

    # -- CLI (caja negra) -------------------------------------------------

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

    def prepare_new_execution(self) -> subprocess.CompletedProcess:
        """La superficie que PD-16 acota (ficha T6): `prepare --new-execution`."""
        return self.run(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="005-012 T6 fixture (nueva ejecución)",
            extra=("--new-execution",)))

    def prepare_reuse(self) -> subprocess.CompletedProcess:
        """El camino de REUSO del contexto (sin `--new-execution`)."""
        return self.run(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="005-012 T6 fixture (reuso del contexto abierto)"))

    def validate_state(self) -> subprocess.CompletedProcess:
        return self.run("validate-state", "--project-root", str(self.root))

    # -- observación ------------------------------------------------------

    def read_state(self) -> dict:
        return read_state(self.root)

    def write_state(self, state: dict) -> None:
        write_state(self.root, state)

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def snapshot(self) -> dict:
        return tree_snapshot(self.root)

    def contexts(self) -> dict[str, dict]:
        """Los contextos v2 publicados bajo `.cdad/executions` (oráculo de
        contenido: el directorio de ejecuciones no debe crecer)."""
        return v2_execution_docs(self.root)

    def packets(self) -> dict[str, bytes]:
        return published_packets(self.root)


@pytest.fixture
def fresh_project(tmp_path: Path) -> _Fixture:
    """Proyecto nuevo, SIN contexto de ejecución previo (control positivo)."""
    return _Fixture(tmp_path, mode="fresh")


@pytest.fixture
def open_context(tmp_path: Path) -> _Fixture:
    """Contexto v2 abierto por `open-unit` y SIN USO (caso PD-16)."""
    return _Fixture(tmp_path, mode="open")


# ---------------------------------------------------------------- PD-16


def test_pd16_new_execution_with_open_unused_context_is_rejected_naming_it(
        open_context: _Fixture) -> None:
    """PD-16 (caso RECHAZO): con un contexto v2 activo de la feature activa
    (el que creó `open-unit`) y SIN USO —sin paquetes publicados con su
    `execution_id` y sin registros de despacho—, `prepare --new-execution …`
    → rc=2, marcador `state incoherent`, diagnóstico que NOMBRA el contexto ya
    abierto (`.cdad/executions/<exec-id>/execution.json`) y CÓMO SEGUIR; y NO
    acuña un segundo id: el directorio `.cdad/executions/` no crece y el state
    (y el árbol, INV-7) quedan byte a byte idénticos. `validate-state` rc=0
    antes y después (PD-17).

    Aislamiento de causas: el fixture no tiene ninguna otra causa posible de
    rc≠0 (política válida, feature activa `in-progress` con contrato pineado,
    delegación activa con `source` existente, `active_packet` nulo) — hoy la
    misma invocación da rc=0 (sonda).

    RED hoy: rc=0 y acuña `…-NNN+1` (el defecto de 005-013) → falla la
    aserción del rechazo (AssertionError de contrato), no la invocación.
    """
    state = open_context.read_state()
    open_exec = state["execution"]["id"]
    context_rel = f".cdad/executions/{open_exec}/execution.json"

    # Precondiciones del fixture (comportamiento existente): contexto abierto…
    assert (open_context.root / context_rel).is_file(), (
        f"precondición (fixture): el contexto abierto debe existir en disco "
        f"({context_rel})")
    # …y SIN USO: sin despachos, sin paquete activo ni paquete publicado.
    assert not (open_context.root / ".cdad" / "executions" / open_exec
                / "dispatches").exists(), (
        "precondición (fixture): el contexto abierto está SIN USO (sin "
        "registros de despacho)")
    assert open_context.read_state().get("active_packet") is None, (
        "precondición (fixture): el contexto abierto no debe dejar paquete "
        "activo")
    assert open_context.packets() == open_context.packets_before_open, (
        "precondición (fixture): no debe haber paquetes publicados con el "
        "`execution_id` del contexto abierto")
    assert open_context.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 ANTES de la invocación")

    state_before = open_context.state_bytes()
    tree_before = open_context.snapshot()
    contexts_before = open_context.contexts()

    proc = open_context.prepare_new_execution()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-16 violada (RECHAZO): con un contexto abierto y sin uso, "
        "`prepare --new-execution` debe rechazarse (rc=2) en vez de acuñar un "
        f"segundo id; rc={proc.returncode}: {out!r}"
    )
    assert STATE_INCOHERENT in out.lower(), (
        "PD-16 violada (RECHAZO): el rechazo debe llevar el marcador "
        f"«{STATE_INCOHERENT}»: {out!r}"
    )
    assert context_rel in out, (
        "PD-16 violada (RECHAZO): el diagnóstico debe NOMBRAR el contexto ya "
        f"abierto ({context_rel!r}): {out!r}"
    )
    assert "--new-execution" in out, (
        "PD-16 violada (RECHAZO): el diagnóstico debe decir CÓMO SEGUIR (usar "
        "el contexto abierto, o preparar sin `--new-execution`): "
        f"{out!r}"
    )
    assert open_context.contexts() == contexts_before, (
        "PD-16 violada (RECHAZO): el rechazo NO debe acuñar un segundo id "
        f"(`.cdad/executions/` no debe crecer): antes "
        f"{sorted(contexts_before)}, después "
        f"{sorted(open_context.contexts())}"
    )
    assert open_context.state_bytes() == state_before, (
        "PD-16/INV-7 violada (RECHAZO): el rechazo debe dejar el state byte a "
        f"byte idéntico (`{STATE_REL}` cambió)"
    )
    assert open_context.snapshot() == tree_before, (
        "PD-16/INV-7 violada (RECHAZO): el rechazo debe dejar el árbol del "
        "proyecto byte a byte idéntico (sin efectos)"
    )
    assert open_context.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 DESPUÉS del rechazo "
        "(state y árbol intactos)"
    )


def test_pd16_new_execution_without_prior_context_still_publishes(
        fresh_project: _Fixture) -> None:
    """PD-16 (CONTROL POSITIVO): SIN contexto abierto previo (proyecto nuevo,
    sin `open-unit`), `prepare --new-execution …` sigue funcionando: rc=0,
    acuña un id nuevo (un contexto v2) y publica el paquete normalmente;
    `validate-state` queda verde.

    Hoy ya pasa: es el comportamiento EXISTENTE que el guard NO debe romper
    (ficha T6: «si el rechazo bloqueara un uso legítimo de `--new-execution`
    … detener»). Su valor es el GREEN y las regresiones, no el RED.
    """
    assert fresh_project.contexts() == {}, (
        "precondición (fixture): este caso NO debe tener contexto abierto "
        f"previo: {sorted(fresh_project.contexts())}")

    proc = fresh_project.prepare_new_execution()

    assert proc.returncode == 0, (
        "PD-16 violada (CONTROL POSITIVO): sin contexto abierto previo, "
        "`prepare --new-execution` debe seguir funcionando (rc=0); "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}"
    )
    contexts = fresh_project.contexts()
    assert len(contexts) == 1, (
        "PD-16 violada (CONTROL POSITIVO): la invocación debe acuñar UN id "
        f"nuevo (un contexto v2): {sorted(contexts)}"
    )
    new_exec = next(iter(contexts))
    assert fresh_project.read_state()["execution"]["id"] == new_exec, (
        "PD-16 violada (CONTROL POSITIVO): `state.execution` debe referenciar "
        f"el id nuevo ({new_exec!r}): "
        f"{fresh_project.read_state()['execution'].get('id')!r}"
    )
    assert proc.stdout.startswith(PACKET_BEGIN), (
        "PD-16 violada (CONTROL POSITIVO): la invocación debe PUBLICAR el "
        "paquete normalmente (stdout canónico): "
        f"{proc.stdout[:200]!r}"
    )
    assert len(fresh_project.packets()) == 1, (
        "PD-16 violada (CONTROL POSITIVO): debe quedar un paquete publicado: "
        f"{sorted(fresh_project.packets())}"
    )
    assert fresh_project.validate_state().returncode == 0, (
        "PD-16 violada (CONTROL POSITIVO): el state resultante debe quedar "
        "coherente (`validate-state` rc=0)"
    )


def test_pd16_reuse_path_without_new_execution_keeps_working(
        open_context: _Fixture) -> None:
    """PD-16 (camino de REUSO intacto): tras `open-unit`, un `prepare` SIN
    `--new-execution` sigue funcionando (rc=0): reusa el contexto abierto
    (ningún id nuevo, `state.execution` es el mismo), publica el paquete y
    `validate-state` queda verde. Es el camino que la feature usa en cada
    tramo; el guard sólo acota `--new-execution`.

    Hoy ya pasa: es el comportamiento EXISTENTE que el guard NO debe romper.
    """
    state = open_context.read_state()
    open_exec = state["execution"]["id"]
    contexts_before = open_context.contexts()
    packets_before = set(open_context.packets())

    proc = open_context.prepare_reuse()

    assert proc.returncode == 0, (
        "PD-16 violada (REUSO): tras `open-unit`, `prepare` SIN "
        "`--new-execution` debe seguir funcionando (rc=0); "
        f"rc={proc.returncode}: {proc.stdout!r} {proc.stderr!r}"
    )
    assert open_context.contexts() == contexts_before, (
        "PD-16 violada (REUSO): el reuso NO debe acuñar un contexto nuevo: "
        f"antes {sorted(contexts_before)}, después "
        f"{sorted(open_context.contexts())}"
    )
    assert open_context.read_state()["execution"]["id"] == open_exec, (
        "PD-16 violada (REUSO): `state.execution` debe seguir siendo el "
        f"contexto abierto ({open_exec!r}): "
        f"{open_context.read_state()['execution'].get('id')!r}"
    )
    assert len(set(open_context.packets()) - packets_before) == 1, (
        "PD-16 violada (REUSO): el `prepare` de reuso debe publicar su paquete "
        f"normalmente: {sorted(open_context.packets())}"
    )
    assert open_context.validate_state().returncode == 0, (
        "PD-16 violada (REUSO): el state resultante debe quedar coherente "
        "(`validate-state` rc=0)"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
