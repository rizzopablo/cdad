#!/usr/bin/env python3
"""005-002 T5 (REAPERTURA ACOTADA) — «desconocido NO es cero» y «ausencia
declarada»: los defectos de la CLASE D1, más el conjunto reconocido de
despacho (D4) y el casado parcial de `--session` (D5).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (PD-3, PD-4, PD-6,
  PD-10, PD-12, PD-15; INV-4, INV-7: un valor nulo/ausente/no observable se
  informa `unknown` CON causa, nunca `0`; una métrica vive en EXACTAMENTE un
  cubo y el value de un cubo `unknown` es null; privacidad = el id crudo
  nunca aparece en la salida).
- docs/specs/005-002-session-context-meter/plan.md (T1..T4; esta reapertura
  agrega la unidad T5, sin cambiar el contrato aprobado).
- docs/specs/005-002-session-context-meter/debt.md (condiciones de cierre de
  D1, D4 y D5).
- docs/epics/epic-005-real-operation/execution.md (criterio de review vigente
  que motiva la reapertura acotada).

ORÁCULO: la SALIDA del WRAPPER fino `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable) — NUNCA importando el
módulo. Sin aserciones sobre nombres internos de funciones/clases/módulos;
sin mocks sobre el plumbing. El test-writer NO lee la implementación.

Fixtures 100% SINTÉTICOS, construidos por este test en un directorio
temporal con SQLite, contenido inventado por este test (sesiones
`sess-fixture-*`, modelos `model-alpha`/`model-beta`, providers `prov-a`/
`prov-b`). La base real del runtime JAMÁS se abre ni se copia (PD-10/INV-7):
los tests no tocan ningún store real.

Invariante central (PD-4/INV-4) que esta unidad hace cumplir:
- un valor nulo, ausente o no observable se informa `unknown` CON causa,
  NUNCA `0`;
- una magnitud PARCIAL no se presenta como observada completa;
- una métrica vive en EXACTAMENTE un cubo (`observed`/`estimated`/`unknown`)
  y el `value` de un cubo `unknown` es `null`;
- presente-con-0 es observable (un `0` REPORTADO cuenta como reportado): la
  muestra 1 lo fija — proxy del último paso 203.276 = input 1.164 +
  cache.read 202.112 + cache.write 0.

Postcondiciones cubiertas (un test por postcondición, con el PD y el
hallazgo D1/D4/D5 nombrados en el docstring):

1. [D1] Hito OBSERVADO cuyo tiempo NO es observable.
2. [D1, la clase] Proxy por paso (`input + cache.read + cache.write`).
3. [D1, la clase] Salidas: sin evidencia → unknown; 0 observado → observado.
4. [D1, la clase] Barrido: ninguna medida en `observed` con value null ni
   un 0 fabricado.
5. [D4] Despachos reconocidos declarados (`reader.dispatch_tools`).
6. [D5] Casado parcial de `--session` declarado (y hasheado); la referencia
   PEDIDA y NO ENCONTRADA queda declarada (distinta de toda referencia
   medida) y el fallo cerrado cuando NINGUNA referencia casa se conserva.
7. [D1, la clase] Agregados por paso: una medida que SUMA un componente sobre
   los pasos del tramo (`accumulated` = Σ `tokens.input`, `cache.read` = Σ
   `cache.read`, `cost` = Σ `cost`) es una observación COMPLETA solo si TODOS
   los pasos del tramo reportan ese componente (un 0 REPORTADO cuenta como
   reportado); con al menos un paso que NO lo reporta → bucket `unknown`,
   value null (NUNCA el subtotal parcial presentado como `observed`) y UNA
   causa AGREGADA en `unknowns[]` (una por medida, nunca una por paso) que
   nombra la cobertura y el componente.
8. [D1 + PD-4] `cache.write` conserva su regla (un 0 reportado por el
   proveedor = «no reportado» → `unknown`, nunca `0`) y declara además la
   cobertura del tramo cuando algún paso no lo reporta.

Barrido corregido (unidad 1): `accumulated`, `cache.read` y `cost` pasan de
«no (0)» a **SÍ (subtotal parcial declarado como observado)** y quedan
cubiertos por el test 7 de este archivo.

RED hoy (probado con el wrapper, sin leer la implementación): `time_relative`
rinde `0.0` y la medida queda en `observed` con value null; el proxy por paso
rinde `0`/subtotal parcial; los agregados por paso (`accumulated`/`cache.read`/
`cost`) rinden el SUBTOTAL PARCIAL como `observed`; `cache.write` no declara la
cobertura del tramo; `total_output`/`max_output` rinden `0` sin evidencia; no
existe `reader.dispatch_tools`; la referencia `--session` que no casa no se
declara. Cada test falla por AssertionError de CONTRATO (comportamiento
ausente), nunca por ImportError/sintaxis/setup: el test NO importa el módulo
del medidor.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
METER_WRAPPER = REPO_ROOT / "scripts" / "cdad_context_meter.py"  # wrapper fino

FEATURE_ID = "005-002-session-context-meter"
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"
CLI_TIMEOUT_S = 120

# Bandera declarada por la unidad 2 de la reapertura acotada (interfaz
# fijada por `tests/test_005_002_t5_bounded_output.py`): el detalle por paso
# (lista ORDENADA de proxys) se obtiene con `--steps`; la corrida POR DEFECTO
# porta el resumen de tamaño fijo (PD-12/D2). Esta unidad 1 alinea su oráculo
# (solo la INVOCACIÓN, no el contrato) leyendo la lista de la corrida CON la
# bandera; las aserciones siguen probando EXACTAMENTE lo mismo.
DETAIL_FLAG = "--steps"

# Claves/tipos del registro neutral (spec §2; PD-16/C2).
MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")
BUCKET_VALUES = ("observed", "estimated", "unknown")
MILESTONE_STATUS_VALUES = ("observed", "absent", "unknown")

# Roles/modelos/ids/providers 100% SINTÉTICOS (inventados; nada de la base).
ROLE = "cdad-orchestrator"
MODEL = '{"id":"model-alpha","providerID":"prov-a"}'

SESSION_MILESTONE_RESUME = "sess-fixture-milestone-resume"
SESSION_MILESTONE_DISPATCH = "sess-fixture-milestone-dispatch"
SESSION_PROXY_PARTIAL = "sess-fixture-proxy-partial"
SESSION_NO_OUTPUTS = "sess-fixture-no-outputs"
SESSION_ZERO_OUTPUT = "sess-fixture-zero-output"
SESSION_POOR = "sess-fixture-poor"
SESSION_DISPATCH_TASK = "sess-fixture-dispatch-task"
SESSION_DISPATCH_UNKNOWN = "sess-fixture-dispatch-unknown"
SESSION_ALPHA = "sess-fixture-alpha-0001"
SESSION_MISSING = "sess-fixture-missing-ZZZ"
SESSION_AGG_PARTIAL = "sess-fixture-agg-partial"
SESSION_AGG_COMPLETE = "sess-fixture-agg-complete"

DISPATCH_TOOL_KNOWN = "subagent"
DISPATCH_TOOL_TASK = "task"
DISPATCH_TOOL_UNKNOWN = "dispatch_unknown"
RESUME_CMD = ("python3 skills/cdad-cycle/scripts/cdad_continuity.py "
              "resume --project-root .")

BASE_MS = 1_760_000_000_000       # epoch ms SINTÉTICO, fijo (determinismo)
STEP_MS = 30_000                  # paso entre llamadas sintéticas (ms)
NONNUMERIC = "not-a-number"       # marca de tiempo NO numérica (D1)

# Agregados por paso (D1, la clase). `SESSION_AGG_PARTIAL`: el tramo tiene 5
# pasos `assistant`, 3 reportan los componentes y 2 NO los reportan en
# absoluto (sin `tokens` ni `cost`) → la suma de los que reportan es un
# SUBTOTAL PARCIAL. `SESSION_AGG_COMPLETE`: 3 pasos y TODOS reportan → la
# suma es una observación completa (control positivo).
AGG_PARTIAL_TOTAL = 5
AGG_PARTIAL_MISSING = 2
AGG_PARTIAL_INPUT_SUM = 230       # subtotal parcial (NUNCA observado)
AGG_PARTIAL_READ_SUM = 120
AGG_PARTIAL_COST_SUM = 1.0
AGG_COMPLETE_INPUT_SUM = 24       # control positivo (observado)
AGG_COMPLETE_READ_SUM = 12
AGG_COMPLETE_COST_SUM = 0.875

AGG_COMPONENT_INPUT = "tokens.input"
AGG_COMPONENT_CACHE_READ = "cache.read"
AGG_COMPONENT_COST = "cost"
AGG_COMPONENT_CACHE_WRITE = "cache.write"

# Marcadores de «la suma NO es una observación completa» en la causa agregada.
AGG_INCOMPLETE_WORDS = ("not a complete", "incomplete", "no completa",
                        "no es una observacion completa", "partial", "parcial",
                        "subtotal", "no partial sum", "no se emite",
                        "not emitted", "no observad", "not observ")

# Palabras de causa «desconocido/ausencia» (any-match, minúsculas).
UNKNOWN_WORDS = ("unknown", "desconoc", "not observable", "no observable",
                 "no es observable", "not numeric", "no numerico",
                 "no numérico", "not reported", "no reportado")

SESSION_V2_DDL = """
CREATE TABLE session_v2 (
    id TEXT PRIMARY KEY,
    project_id TEXT, workspace_id TEXT, parent_id TEXT,
    fork_session_id TEXT, fork_boundary TEXT, slug TEXT,
    directory TEXT, path TEXT, title TEXT, version TEXT, share_url TEXT,
    summary_additions INTEGER, summary_deletions INTEGER,
    summary_files INTEGER, summary_diffs INTEGER,
    metadata TEXT, cost REAL,
    tokens_input INTEGER, tokens_output INTEGER, tokens_reasoning INTEGER,
    tokens_cache_read INTEGER, tokens_cache_write INTEGER,
    revert TEXT, permission TEXT, agent TEXT, model TEXT,
    time_created REAL, time_updated REAL, time_compacting REAL,
    time_archived REAL, time_suspended REAL,
    resume_attempts INTEGER, time_idle REAL, time_viewed REAL,
    idle_outcome TEXT)
"""

SESSION_MESSAGE_DDL = """
CREATE TABLE session_message (
    id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INTEGER,
    time_created REAL, time_updated REAL, data TEXT)
"""


# ------------------------------------------------------------- fixtures

def _data_time(ms) -> dict:
    return {"created": ms, "streamed": ms, "completed": ms}


def _tool_part(name: str, text: str, *, args: dict, part_id: str,
               ms=None, nonnumeric_time: bool = False) -> dict:
    """Parte `tool` (discovery §1.4): state.content = [{type:text, text}] →
    tamaño de salida = suma de len(text). `nonnumeric_time=True` hace la
    marca de tiempo del paso NO numérica (D1)."""
    when = NONNUMERIC if nonnumeric_time else ms
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": {"status": "completed", "input": args,
                  "content": [{"type": "text", "text": text}]},
        "time": {"created": when, "ran": when, "completed": when},
    }


def _assistant_data(parts: list, tokens, *, ms=None, nonnumeric_time=False,
                    cost=None) -> str:
    """Forma `assistant` (discovery §1.3). `tokens` es el dict crudo de
    tokens (permite AUSENTE o con COMPONENTE FALTANTE, D1); `cost` es el
    costo por paso reportado (None o ausente = no reportado)."""
    doc: dict = {
        "time": _data_time(NONNUMERIC if nonnumeric_time else ms),
        "agent": ROLE, "model": MODEL, "content": parts,
    }
    if tokens is not None:
        doc["tokens"] = tokens
    doc["cost"] = cost
    return json.dumps(doc, sort_keys=True)


def _tokens_full(tin: int, tout: int, tread: int, twrite: int) -> dict:
    """Tokens con los TRES componentes reportados; `twrite=0` REPORTADO
    cuenta como reportado (muestra 1)."""
    return {"input": tin, "output": tout, "reasoning": 0,
            "cache": {"read": tread, "write": twrite}}


def _tokens_missing_write(tin: int, tout: int, tread: int) -> dict:
    """Tokens a los que les FALTA el componente `cache.write` (D1)."""
    return {"input": tin, "output": tout, "reasoning": 0,
            "cache": {"read": tread}}


def _user_data(ms) -> str:
    return json.dumps({"time": ms, "text": "fixture prompt sintetico"},
                      sort_keys=True)


def _insert_msg(conn: sqlite3.Connection, sid: str, seq: int, mtype: str,
                data: str, ms) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, mtype, seq, ms, ms, data))


def _insert_msg_nonnumeric_time(conn: sqlite3.Connection, sid: str, seq: int,
                                data: str) -> None:
    """Mensaje de hito cuyo tiempo (columna y `data.time`) NO es numérico:
    la POSICIÓN sigue observable pero el TIEMPO no (D1)."""
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, "assistant", seq,
         NONNUMERIC, NONNUMERIC, data))


def _insert_session(conn: sqlite3.Connection, sid: str, t0, t_end,
                    sums: tuple, cost=None) -> None:
    tin, tout, treason, tread, twrite = sums
    conn.execute(
        "INSERT INTO session_v2 (id, project_id, workspace_id, parent_id,"
        " fork_session_id, fork_boundary, slug, directory, path, title,"
        " version, share_url, summary_additions, summary_deletions,"
        " summary_files, summary_diffs, metadata, cost,"
        " tokens_input, tokens_output, tokens_reasoning, tokens_cache_read,"
        " tokens_cache_write, revert, permission, agent, model,"
        " time_created, time_updated, time_compacting, time_archived,"
        " time_suspended, resume_attempts, time_idle, time_viewed,"
        " idle_outcome)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
        " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (sid, "proj-fixture", "ws-fixture", None, None, None,
         f"fixture-{sid[-6:]}", "/fixture/dir", "/fixture/dir",
         f"fixture {sid}", "fixture-version", None, 0, 0, 0, 0, None, cost,
         tin, tout, treason, tread, twrite, None, None, ROLE, MODEL,
         t0, t_end, None, None, None, 0, None, None, None))


def _new_store(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(SESSION_V2_DDL)
    conn.execute(SESSION_MESSAGE_DDL)
    return conn


def _build_milestone_time(path: Path, *, hit_tool: str) -> None:
    """[D1] Fixture: el mensaje del hito EXISTE (posición observable) pero su
    marca de tiempo NO es numérica. `hit_tool="shell"` → el shell invoca el
    subcomando `resume` (hito `first_resume`); `hit_tool="subagent"` → hito
    `first_dispatch`."""
    sid = (SESSION_MILESTONE_RESUME if hit_tool == "shell"
           else SESSION_MILESTONE_DISPATCH)
    conn = _new_store(path)
    t0 = BASE_MS + 10_000_000
    _insert_msg(conn, sid, 1, "user", _user_data(t0), t0)
    tools = ["read", "glob", hit_tool, "edit"]
    for i, name in enumerate(tools, start=1):
        seq = 1 + i
        if i == 3:
            args = ({"command": RESUME_CMD} if name == "shell"
                    else {"path": "/fixture/worker", "description": "d"})
            parts = [_tool_part(name, "z" * 7, args=args, part_id=f"p{seq}",
                                nonnumeric_time=True)]
            data = _assistant_data(parts, _tokens_full(10, 2, 1, 0),
                                   nonnumeric_time=True)
            _insert_msg_nonnumeric_time(conn, sid, seq, data)
        else:
            ms = t0 + i * STEP_MS
            args = ({"command": "echo fixture"} if name == "shell"
                    else {"path": "/fixture/dir/f%d" % i})
            _insert_msg(conn, sid, seq, "assistant",
                        _assistant_data([_tool_part(name, "z" * 7, args=args,
                                                    part_id=f"p{seq}", ms=ms)],
                                        _tokens_full(10, 2, 1, 0), ms=ms),
                        ms)
    _insert_session(conn, sid, t0, t0 + len(tools) * STEP_MS,
                    (40, 8, 0, 4, 0))
    conn.commit()
    conn.close()


def _build_proxy_partial(path: Path) -> None:
    """[D1, la clase] Proxy por paso: el paso #1 trae los TRES componentes
    reportados (con cache.write=0 REPORTADO → proxy = suma); los pasos #2 y
    #3 les FALTA `cache.write` → su proxy es null (nunca 0 ni subtotal)."""
    conn = _new_store(path)
    t0 = BASE_MS + 20_000_000
    _insert_msg(conn, SESSION_PROXY_PARTIAL, 1, "user", _user_data(t0), t0)
    steps = [
        (2, _tokens_full(100, 10, 50, 0), 150),
        (3, _tokens_missing_write(70, 5, 40), None),
        (4, _tokens_missing_write(60, 4, 30), None),
    ]
    for seq, tokens, _expected in steps:
        ms = t0 + (seq - 1) * STEP_MS
        _insert_msg(conn, SESSION_PROXY_PARTIAL, seq, "assistant",
                    _assistant_data(
                        [_tool_part("read", "r" * 9,
                                    args={"path": "/fixture/dir/s%d" % seq},
                                    part_id=f"p{seq}", ms=ms)],
                        tokens, ms=ms), ms)
    _insert_session(conn, SESSION_PROXY_PARTIAL, t0, t0 + 3 * STEP_MS,
                    (230, 19, 0, 120, 0))
    conn.commit()
    conn.close()


def _build_no_outputs(path: Path) -> None:
    """[D1] Tramo SIN ninguna llamada de herramienta con salida: no hay
    evidencia de salida → total/max_output unknown, nunca 0."""
    conn = _new_store(path)
    t0 = BASE_MS + 30_000_000
    _insert_msg(conn, SESSION_NO_OUTPUTS, 1, "user", _user_data(t0), t0)
    for seq in (2, 3):
        ms = t0 + (seq - 1) * STEP_MS
        _insert_msg(conn, SESSION_NO_OUTPUTS, seq, "assistant",
                    _assistant_data([{"type": "text", "text": "solo texto"}],
                                    _tokens_full(10, 5, 1, 0), ms=ms), ms)
    _insert_session(conn, SESSION_NO_OUTPUTS, t0, t0 + 2 * STEP_MS,
                    (20, 10, 0, 2, 0))
    conn.commit()
    conn.close()


def _build_zero_output(path: Path) -> None:
    """[D1] Control positivo: el tramo SÍ porta una llamada cuya salida
    existe y mide 0 caracteres → ese 0 es OBSERVADO (no se vuelve unknown)."""
    conn = _new_store(path)
    t0 = BASE_MS + 40_000_000
    _insert_msg(conn, SESSION_ZERO_OUTPUT, 1, "user", _user_data(t0), t0)
    ms = t0 + STEP_MS
    _insert_msg(conn, SESSION_ZERO_OUTPUT, 2, "assistant",
                _assistant_data(
                    [_tool_part("read", "", args={"path": "/fixture/dir/e.md"},
                                part_id="p2", ms=ms)],
                    _tokens_full(10, 5, 1, 0), ms=ms), ms)
    _insert_session(conn, SESSION_ZERO_OUTPUT, t0, ms + STEP_MS,
                    (10, 5, 0, 1, 0))
    conn.commit()
    conn.close()


def _build_poor(path: Path) -> None:
    """[D1, la clase] Fixture «pobre» para el barrido: hito resume con tiempo
    NO observable (#3) y pasos con componente faltante → combina las dos
    fabricaciones (tiempo observado con value null y proxy 0/parcial)."""
    conn = _new_store(path)
    t0 = BASE_MS + 50_000_000
    _insert_msg(conn, SESSION_POOR, 1, "user", _user_data(t0), t0)
    # paso #1 (read, tokens completos) y #2 (read, falta cache.write)
    ms = t0 + STEP_MS
    _insert_msg(conn, SESSION_POOR, 2, "assistant",
                _assistant_data(
                    [_tool_part("read", "a" * 9,
                                args={"path": "/fixture/dir/p2"},
                                part_id="p2", ms=ms)],
                    _tokens_full(100, 10, 50, 0), ms=ms), ms)
    ms = t0 + 2 * STEP_MS
    _insert_msg(conn, SESSION_POOR, 3, "assistant",
                _assistant_data(
                    [_tool_part("read", "b" * 9,
                                args={"path": "/fixture/dir/p3"},
                                part_id="p3", ms=ms)],
                    _tokens_missing_write(70, 5, 40), ms=ms), ms)
    # hito resume #3 con tiempo NO observable
    _insert_msg_nonnumeric_time(
        conn, SESSION_POOR, 4,
        _assistant_data(
            [_tool_part("shell", "c" * 9, args={"command": RESUME_CMD},
                        part_id="p4", nonnumeric_time=True)],
            _tokens_full(60, 4, 30, 0), nonnumeric_time=True))
    _insert_session(conn, SESSION_POOR, t0, t0 + 3 * STEP_MS,
                    (230, 19, 0, 120, 0))
    conn.commit()
    conn.close()


def _build_dispatch(path: Path, *, tool: str) -> None:
    """[D4] Fixture de despacho: una llamada a `tool` (reconocida `task` o
    NO reconocida `dispatch_unknown`) tras un `read`."""
    sid = (SESSION_DISPATCH_TASK if tool == DISPATCH_TOOL_TASK
           else SESSION_DISPATCH_UNKNOWN)
    conn = _new_store(path)
    t0 = BASE_MS + 60_000_000
    _insert_msg(conn, sid, 1, "user", _user_data(t0), t0)
    for i, name in enumerate(["read", tool], start=1):
        ms = t0 + i * STEP_MS
        seq = 1 + i
        args = ({"path": "/fixture/dir/w%d" % i, "description": "d"}
                if name == tool else {"path": "/fixture/dir/r%d" % i})
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(
                        [_tool_part(name, "d" * 6, args=args,
                                    part_id=f"p{seq}", ms=ms)],
                        _tokens_full(10, 5, 1, 0), ms=ms), ms)
    _insert_session(conn, sid, t0, t0 + 2 * STEP_MS, (20, 10, 0, 2, 0))
    conn.commit()
    conn.close()


def _build_alpha(path: Path) -> None:
    """[D5] Una única sesión existente (`SESSION_ALPHA`)."""
    conn = _new_store(path)
    t0 = BASE_MS + 70_000_000
    _insert_msg(conn, SESSION_ALPHA, 1, "user", _user_data(t0), t0)
    ms = t0 + STEP_MS
    _insert_msg(conn, SESSION_ALPHA, 2, "assistant",
                _assistant_data(
                    [_tool_part("read", "q" * 6, args={"path": "/fixture/dir"},
                                part_id="p2", ms=ms)],
                    _tokens_full(10, 5, 1, 0), ms=ms), ms)
    _insert_session(conn, SESSION_ALPHA, t0, t0 + STEP_MS, (10, 5, 0, 1, 0))
    conn.commit()
    conn.close()


def _build_aggregate_partial(path: Path) -> None:
    """[D1, la clase] Agregados por paso: el tramo tiene 5 pasos `assistant`;
    3 reportan los componentes (`tokens.input`/`cache.read`/`cache.write` con
    cache.write=0 REPORTADO, y `cost`) y 2 NO reportan ni `tokens` ni `cost`.
    La suma de los que reportan (230 tok / 120 tok / 1.0) es un SUBTOTAL
    PARCIAL: no puede presentarse como observación completa."""
    conn = _new_store(path)
    t0 = BASE_MS + 80_000_000
    _insert_msg(conn, SESSION_AGG_PARTIAL, 1, "user", _user_data(t0), t0)
    steps = [
        (2, _tokens_full(100, 10, 50, 0), 0.25),
        (3, None, None),
        (4, _tokens_full(70, 5, 40, 0), 0.25),
        (5, None, None),
        (6, _tokens_full(60, 4, 30, 0), 0.5),
    ]
    for seq, tokens, cost in steps:
        ms = t0 + (seq - 1) * STEP_MS
        _insert_msg(conn, SESSION_AGG_PARTIAL, seq, "assistant",
                    _assistant_data(
                        [_tool_part("read", "r" * 9,
                                    args={"path": "/fixture/dir/a%d" % seq},
                                    part_id=f"p{seq}", ms=ms)],
                        tokens, ms=ms, cost=cost), ms)
    _insert_session(conn, SESSION_AGG_PARTIAL, t0, t0 + 5 * STEP_MS,
                    (230, 19, 0, 120, 0))
    conn.commit()
    conn.close()


def _build_aggregate_complete(path: Path) -> None:
    """[D1] Control positivo de los agregados: el tramo tiene 3 pasos y TODOS
    reportan los componentes (con cache.write=0 REPORTADO) → la suma ES una
    observación completa (24 tok / 12 tok / 0.875)."""
    conn = _new_store(path)
    t0 = BASE_MS + 90_000_000
    _insert_msg(conn, SESSION_AGG_COMPLETE, 1, "user", _user_data(t0), t0)
    steps = [
        (2, _tokens_full(11, 1, 5, 0), 0.5),
        (3, _tokens_full(7, 1, 4, 0), 0.25),
        (4, _tokens_full(6, 1, 3, 0), 0.125),
    ]
    for seq, tokens, cost in steps:
        ms = t0 + (seq - 1) * STEP_MS
        _insert_msg(conn, SESSION_AGG_COMPLETE, seq, "assistant",
                    _assistant_data(
                        [_tool_part("read", "r" * 9,
                                    args={"path": "/fixture/dir/c%d" % seq},
                                    part_id=f"p{seq}", ms=ms)],
                        tokens, ms=ms, cost=cost), ms)
    _insert_session(conn, SESSION_AGG_COMPLETE, t0, t0 + 3 * STEP_MS,
                    (24, 3, 0, 12, 0))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- helpers

def _measure_leaves(measures: object, prefix: str = ""):
    """Hojas de métrica: todo dict con (value, unit, provenance, bucket) a
    cualquier profundidad de anidamiento declarado."""
    if isinstance(measures, dict):
        if all(field in measures for field in MEASURE_FIELDS):
            yield prefix, measures
            return
        for key, value in measures.items():
            path = f"{prefix}.{key}" if prefix else key
            yield from _measure_leaves(value, path)


def _hashed_ref_pattern(session_ref: str) -> str:
    """Forma de la referencia hasheada derivada del PROPIO documento (mismo
    prefijo, mismo alfabeto y misma longitud; sin hardcodear el largo)."""
    if ":" in session_ref:
        prefix, digest = session_ref.split(":", 1)
        prefix += ":"
    else:
        prefix, digest = "", session_ref
    charset = "".join(sorted(set(digest)))
    return (re.escape(prefix) + "[" + re.escape(charset) + "]"
            + "{" + str(len(digest)) + "}")


def _hashed_refs_in(text: str, example_ref: str) -> list:
    """Tokens de `text` con la MISMA forma que `example_ref`: mismo prefijo y
    digest de la MISMA longitud, derivados del propio documento (no se
    hardcodea la función de hash ni el largo). El alfabeto es alfanumérico A
    PROPÓSITO: derivar el alfabeto de la referencia MEDIDA perdería un dígito
    que el digest de la referencia PEDIDA (no encontrada) sí puede usar, y el
    oráculo quedaría satisfecho por el eco de la referencia medida."""
    if ":" in example_ref:
        prefix, digest = example_ref.split(":", 1)
        prefix += ":"
    else:
        prefix, digest = "", example_ref
    return re.findall(re.escape(prefix) + r"[0-9A-Za-z]{%d}" % len(digest),
                      text)


class UnknownDeclaredT5Test(unittest.TestCase):
    """T5 RED de 005-002 (reapertura acotada): un test por postcondición,
    contra la SALIDA del wrapper (stdout JSON + rc + stderr)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t5-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_milestone_resume = base / "milestone-resume" / "sessions.db"
        self.store_milestone_dispatch = base / "milestone-dispatch" / "sessions.db"
        self.store_proxy_partial = base / "proxy-partial" / "sessions.db"
        self.store_no_outputs = base / "no-outputs" / "sessions.db"
        self.store_zero_output = base / "zero-output" / "sessions.db"
        self.store_poor = base / "poor" / "sessions.db"
        self.store_dispatch_task = base / "dispatch-task" / "sessions.db"
        self.store_dispatch_unknown = base / "dispatch-unknown" / "sessions.db"
        self.store_alpha = base / "alpha" / "sessions.db"
        self.store_agg_partial = base / "agg-partial" / "sessions.db"
        self.store_agg_complete = base / "agg-complete" / "sessions.db"
        _build_milestone_time(self.store_milestone_resume, hit_tool="shell")
        _build_milestone_time(self.store_milestone_dispatch,
                              hit_tool=DISPATCH_TOOL_KNOWN)
        _build_proxy_partial(self.store_proxy_partial)
        _build_no_outputs(self.store_no_outputs)
        _build_zero_output(self.store_zero_output)
        _build_poor(self.store_poor)
        _build_dispatch(self.store_dispatch_task, tool=DISPATCH_TOOL_TASK)
        _build_dispatch(self.store_dispatch_unknown,
                        tool=DISPATCH_TOOL_UNKNOWN)
        _build_alpha(self.store_alpha)
        _build_aggregate_partial(self.store_agg_partial)
        _build_aggregate_complete(self.store_agg_complete)

    # -- corrida del wrapper (SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str) -> subprocess.CompletedProcess:
        if not METER_WRAPPER.is_file():
            self.fail(
                f"{FEATURE_ID} RED: el medidor `{METER_WRAPPER.name}` no "
                "existe aún — RED por CLI ausente (comportamiento ausente), "
                "nunca por ImportError: el test NO importa el módulo del "
                "medidor")
        cmd = [sys.executable, str(METER_WRAPPER), *argv]
        env = os.environ.copy()
        env.pop(STORE_ENV_VAR, None)  # sin fuga del entorno del host
        try:
            return subprocess.run(
                cmd, cwd=REPO_ROOT, env=env, capture_output=True,
                timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except FileNotFoundError:  # pragma: no cover
            self.fail(
                f"{FEATURE_ID} RED: el medidor `{METER_WRAPPER.name}` no "
                "ejecuta aún (comportamiento ausente); el test NO importa el "
                "módulo del medidor")
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                f"PD-11 (acotado): el medidor no terminó dentro de "
                f"{CLI_TIMEOUT_S}s; timeout={exc!r}")

    def run_ok(self, store: Path, label: str, *extra: str):
        proc = self.run_meter("--store", str(store), *extra)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: rc=0 (no es fallo cerrado: el store y el esquema "
                f"son válidos); stdout={proc.stdout[:300]!r} "
                f"stderr={proc.stderr[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        run = doc.get("run", {})
        self.assertEqual(
            run.get("schema"), "recognized",
            msg=f"{label}: el fixture replica el esquema observado y debe "
                f"reconocerse (run={run}) — si sale unknown el RED sería de "
                "rejilla equivocada")
        return proc, doc

    def session0(self, doc: dict, label: str) -> dict:
        sessions = doc.get("sessions")
        self.assertIsInstance(sessions, list, msg=f"{label}: sessions[] lista")
        self.assertTrue(
            sessions, msg=f"{label}: la sesión se mide (sessions[] no vacío)")
        return sessions[0]

    def session_of(self, store: Path, label: str, *extra: str) -> dict:
        _, doc = self.run_ok(store, label, *extra)
        return doc, self.session0(doc, label)

    def session_with_steps(self, store: Path, label: str):
        """Corrida CON la bandera declarada `--steps` (interfaz de la unidad
        2 de la reapertura acotada): el detalle por paso (lista ORDENADA de
        proxys) se lee de esta corrida; la corrida POR DEFECTO porta el
        resumen de tamaño fijo (PD-12/D2). Solo cambia la INVOCACIÓN: las
        aserciones de contrato no se relajan ni se agregan.

        Si la bandera todavía no existe, el wrapper falla cerrado por
        argumento desconocido (rc=2): se reporta como el estado RED de una
        INTERFAZ DECLARADA por el test, explícitamente distinguido de una
        falla de comportamiento del contrato."""
        proc = self.run_meter("--store", str(store), DETAIL_FLAG)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace")
            if proc.returncode == 2:
                self.fail(
                    f"{label}: la bandera `{DETAIL_FLAG}` declarada por la "
                    "unidad 2 de la reapertura AÚN NO EXISTE (rc=2: argumento "
                    "desconocido) — estado RED de una INTERFAZ DECLARADA por "
                    "el test, no una falla de comportamiento del contrato; "
                    f"stderr={err[:300]!r}")
            self.fail(
                f"{label}: con `{DETAIL_FLAG}` se espera rc=0 (fue "
                f"{proc.returncode}); stderr={err[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        run = doc.get("run", {})
        self.assertEqual(
            run.get("schema"), "recognized",
            msg=f"{label}: el fixture replica el esquema observado y debe "
                f"reconocerse (run={run}) — si sale unknown el RED sería de "
                "rejilla equivocada")
        return proc, self.session0(doc, label)

    def measure_leaf(self, measures: object, key: str, ctx: str) -> dict:
        leaves = dict(_measure_leaves(measures))
        leaf = leaves.get(key)
        self.assertIsNotNone(
            leaf,
            msg=f"{ctx}: la medida {key!r} NO existe en el registro — RED de "
                f"contrato: el implementer debe emitirla (hojas presentes: "
                f"{sorted(leaves)})")
        self.assertIsInstance(leaf, dict, msg=f"{ctx}: {key} es una hoja")
        return leaf

    def milestone(self, milestones: object, key: str, ctx: str) -> dict:
        self.assertIsInstance(milestones, dict, msg=f"{ctx}: milestones es "
                                                    "objeto")
        self.assertIn(
            key, milestones,
            msg=f"{ctx}: milestones trae {key!r} (clave presente, PD-16)")
        return milestones[key]

    def unknown_texts(self, doc: dict) -> list:
        unknowns = doc.get("unknowns", [])
        self.assertIsInstance(unknowns, list, msg="unknowns[] es lista")
        return [(entry if isinstance(entry, str) else json.dumps(entry,
                                                                 sort_keys=True)
                 ).lower() for entry in unknowns]

    def assert_time_words(self, text: str, ctx: str) -> None:
        self.assertTrue(
            any(word in text for word in ("time", "tiempo")),
            msg=f"{ctx}: la causa declara el TIEMPO (texto={text!r})")

    def assert_unknown_words(self, text: str, ctx: str) -> None:
        self.assertTrue(
            any(word in text for word in UNKNOWN_WORDS),
            msg=f"{ctx}: la causa declara «unknown/no observable» "
                f"(texto={text!r})")

    def coverage_hits(self, texts: list, component: str, *, total: int,
                      missing: int) -> list:
        """Entradas de `unknowns[]` que nombran el COMPONENTE y declaran la
        COBERTURA del tramo: cuántos pasos lo reportan (`reporting of total`,
        p. ej. «3 of 5 steps») y cuántos no (`missing`). Una entrada AGREGADA
        por medida (nunca una por paso)."""
        reporting = total - missing
        frac = re.compile(
            r"(?<!\d)%d(?!\d)[^\d]{0,40}(?:of|de|/)[^\d]{0,15}(?<!\d)%d(?!\d)"
            % (reporting, total))
        miss = re.compile(r"(?<!\d)%d(?!\d)" % missing)
        return [t for t in texts
                if component in t and frac.search(t) and miss.search(t)]

    # --------------------------------------------------- (1) [D1] hito

    def _assert_milestone_time_not_observable(self, store: Path, hit_key: str,
                                              measure_key: str, label: str,
                                              ):
        doc, session = self.session_of(store, label)
        milestone = self.milestone(session.get("milestones", {}), hit_key,
                                   label)
        # la POSICIÓN SI se observa: no se degrada ni se pierde
        self.assertEqual(
            milestone.get("status"), "observed",
            msg=f"{label}: el hito está OBSERVADO — su posición es "
                "observable (no se degrada a absent/unknown; PD-6)")
        position = milestone.get("position")
        self.assertIsInstance(
            position, dict,
            msg=f"{label}: la POSICIÓN del hito observado está presente y "
                f"es la referencia a los eventos originales (fue {position!r})")
        self.assertIn("call_index", position,
                      msg=f"{label}: la posición trae call_index")
        self.assertIn("seq", position, msg=f"{label}: la posición trae seq")
        # el TIEMPO no es observable → null, NUNCA 0.0
        self.assertIsNone(
            milestone.get("time_relative"),
            msg=f"{label}: el tiempo del hito NO es observable → "
                f"time_relative null, NUNCA 0.0 (fue "
                f"{milestone.get('time_relative')!r}; D1/PD-4/INV-4)")
        # el hito trae una CAUSA que declara el tiempo no observable
        cause = milestone.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"{label}: el hito trae una CAUSA que declara el tiempo no "
                f"observable (fue {cause!r})")
        low = cause.lower()
        self.assert_time_words(low, f"{label} causa del hito")
        self.assert_unknown_words(low, f"{label} causa del hito")
        # la medida hermana: bucket unknown + value null + causa en unknowns
        leaf = self.measure_leaf(session.get("measures", {}), measure_key,
                                 label)
        self.assertEqual(
            leaf.get("bucket"), "unknown",
            msg=f"{label}: {measure_key} queda bucket `unknown` (hoy "
                f"`observed` con value null = cubo mentiroso; fue "
                f"{leaf.get('bucket')!r})")
        self.assertIsNone(
            leaf.get("value"),
            msg=f"{label}: {measure_key} value null (NUNCA 0)"
                f"; fue {leaf.get('value')!r}")
        texts = self.unknown_texts(doc)
        hits = [t for t in texts
                if any(w in t for w in ("time", "tiempo"))
                and any(w in t for w in UNKNOWN_WORDS)]
        self.assertTrue(
            hits,
            msg=f"{label}: {measure_key} declara su causa en unknowns[] "
                f"(textos hoy: {texts!r})")

    def test_t5_1_d1_observed_milestone_without_observable_time(self):
        """[D1] Hito OBSERVADO cuyo tiempo NO es observable: la posición
        sigue observada; `time_relative` es null (NUNCA 0.0); el hito trae la
        causa; la medida hermana queda bucket `unknown`, value null, con
        causa en unknowns[]; rc=0 (no es fallo cerrado). Cubre resume y
        despacho (PD-3, PD-4, PD-6, PD-16; INV-4)."""
        with self.subTest(hito="first_resume"):
            self._assert_milestone_time_not_observable(
                self.store_milestone_resume, "first_resume",
                "time_to_first_resume", "T5(1) resume")
        with self.subTest(hito="first_dispatch"):
            self._assert_milestone_time_not_observable(
                self.store_milestone_dispatch, "first_dispatch",
                "time_to_first_dispatch", "T5(1) dispatch")

    # ------------------------------------------- (2) [D1] proxy por paso

    def test_t5_2_d1_proxy_per_step_partial_not_zero_aggregated_cause(self):
        """[D1, la clase] Proxy por paso (`input + cache.read + cache.write`):
        un paso con los TRES componentes reportados (cache.write=0 REPORTADO)
        tiene proxy = suma; un paso con un componente faltante tiene proxy
        null (nunca 0 ni subtotal parcial presentado como completo); la causa
        va AGREGADA en unknowns[] (UNA entrada con el conteo de pasos
        incompletos y los componentes faltantes, nunca una por paso); la
        medida conserva bucket `estimated` y su provenance declara que null =
        no observable para ese paso (PD-4, PD-8, PD-12; INV-4)."""
        label = "T5(2) proxy por paso"
        _, session = self.session_with_steps(self.store_proxy_partial, label)
        leaf = self.measure_leaf(session.get("measures", {}), "input_per_step",
                                 label)
        self.assertEqual(
            leaf.get("bucket"), "estimated",
            msg=f"{label}: input_per_step conserva su bucket `estimated` "
                f"(fue {leaf.get('bucket')!r})")
        value = leaf.get("value")
        self.assertIsInstance(
            value, list,
            msg=f"{label}: input_per_step porta la lista por paso (fue "
                f"{type(value).__name__})")
        self.assertEqual(
            len(value), 3,
            msg=f"{label}: un elemento por paso `assistant` del tramo (fue "
                f"{value!r})")
        self.assertEqual(
            value[0], 150,
            msg=f"{label}: el paso con los TRES componentes reportados "
                f"(input 100 + cache.read 50 + cache.write 0) tiene proxy 150 "
                f"(fue {value[0]!r})")
        self.assertIsNone(
            value[1],
            msg=f"{label}: el paso al que le falta `cache.write` tiene proxy "
                f"null (NUNCA 0 ni subtotal; fue {value[1]!r})")
        self.assertIsNone(
            value[2],
            msg=f"{label}: el segundo paso incompleto también tiene proxy "
                f"null (fue {value[2]!r})")
        prov = str(leaf.get("provenance", "")).lower()
        self.assertTrue(
            any(w in prov for w in ("null", "unknown", "not observable",
                                    "no observable", "desconoc")),
            msg=f"{label}: la provenance declara que null = no observable "
                f"para ese paso, nunca 0 (fue {prov!r})")
        self.assertTrue(
            any(w in prov for w in ("step", "paso")),
            msg=f"{label}: la provenance habla del paso (fue {prov!r})")
        texts = self.unknown_texts(
            self.run_ok(self.store_proxy_partial, label)[1])
        topic = ("step", "paso", "proxy", "input_per_step")
        incomplete = ("missing", "faltante", "incomplete", "incompleto",
                      "unknown", "desconoc", "null", "not observable",
                      "no observable", "no reportado", "not reported")
        hits = [t for t in texts
                if any(k in t for k in topic) and any(k in t for k in incomplete)]
        self.assertEqual(
            len(hits), 1,
            msg=f"{label}: UNA entrada AGREGADA acotada (nunca una por paso; "
                f"hits={hits!r}; todas={texts!r})")
        self.assertIn(
            "cache.write", hits[0],
            msg=f"{label}: la causa agregada nombra el componente faltante "
                f"`cache.write` (fue {hits[0]!r})")
        self.assertRegex(
            hits[0], r"(?<!\d)2(?!\d)",
            msg=f"{label}: la causa agregada declara el CONTEO de pasos "
                f"incompletos (2) del tramo (fue {hits[0]!r})")

    # --------------------------------------------------- (3) [D1] salidas

    def test_t5_3_d1_outputs_absent_unknown_zero_observed_control(self):
        """[D1, la clase] Salidas: si el tramo NO porta ninguna llamada de
        herramienta con salida (no hay evidencia de salida), `total_output` y
        `max_output` quedan bucket `unknown`, value null y con causa, nunca 0;
        control positivo: si el tramo SÍ porta una llamada cuya salida existe
        y mide 0 caracteres, ese 0 es OBSERVADO (bucket `observed`) y NO se
        convierte en unknown (PD-3, PD-4, PD-8; INV-4)."""
        label = "T5(3) salidas"
        doc, session = self.session_of(self.store_no_outputs, label)
        for key in ("total_output", "max_output"):
            leaf = self.measure_leaf(session.get("measures", {}), key, label)
            self.assertEqual(
                leaf.get("bucket"), "unknown",
                msg=f"{label}: {key} sin evidencia de salida queda bucket "
                    f"`unknown` (nunca `observed` con 0 fabricado; fue "
                    f"{leaf.get('bucket')!r})")
            self.assertIsNone(
                leaf.get("value"),
                msg=f"{label}: {key} value null (nunca 0); fue "
                    f"{leaf.get('value')!r}")
        texts = self.unknown_texts(doc)
        hits = [t for t in texts
                if any(w in t for w in ("output", "salida"))
                and any(w in t for w in UNKNOWN_WORDS)]
        self.assertTrue(
            hits,
            msg=f"{label}: la ausencia de evidencia de salida se declara CON "
                f"CAUSA en unknowns[] (textos hoy: {texts!r})")
        # control positivo: salida presente que mide 0 → 0 OBSERVADO
        _, session_zero = self.session_of(self.store_zero_output,
                                          label + " (control positivo)")
        for key in ("total_output", "max_output"):
            leaf = self.measure_leaf(session_zero.get("measures", {}), key,
                                     label + " (control positivo)")
            self.assertEqual(
                leaf.get("bucket"), "observed",
                msg=f"{label}: la salida presente que mide 0 caracteres es "
                    f"OBSERVADA — {key} bucket `observed` (fue "
                    f"{leaf.get('bucket')!r})")
            self.assertEqual(
                leaf.get("value"), 0,
                msg=f"{label}: el 0 observado de {key} es un 0 real (fue "
                    f"{leaf.get('value')!r})")

    # ------------------------------------------- (4) [D1] barrido completo

    def test_t5_4_d1_sweep_no_observed_null_no_fabricated_zero(self):
        """[D1, la clase] Barrido de las medidas del registro: NINGUNA puede
        quedar en el cubo `observed` con value null, ni emitir 0 cuando la
        magnitud no es observable (el value de un cubo `unknown` es null); se
        agrega la regresión por cada medida donde un 0 sería fabricado
        (input_per_step, total_output, max_output, time_to_first_*). PD-4,
        PD-8, PD-16; INV-4)."""
        label = "T5(4) barrido"
        doc_poor, session_poor = self.session_of(self.store_poor,
                                                 label + " (pobre)")
        doc_noout, session_noout = self.session_of(self.store_no_outputs,
                                                   label + " (sin salidas)")
        # invariante genérico, medida por medida
        for doc, tag in ((doc_poor, "pobre"), (doc_noout, "sin-salidas")):
            session = self.session0(doc, label)
            for path, leaf in _measure_leaves(session.get("measures", {})):
                bucket = leaf.get("bucket")
                value = leaf.get("value")
                self.assertIn(
                    bucket, BUCKET_VALUES,
                    msg=f"{label} [{tag}] {path}: bucket declarado ∈ "
                        f"{BUCKET_VALUES} (fue {bucket!r})")
                if bucket == "observed":
                    self.assertIsNotNone(
                        value,
                        msg=f"{label} [{tag}] {path}: ninguna medida queda en "
                            "`observed` con value null (cubo mentiroso; "
                            "D1/PD-4/INV-4)")
                if bucket == "unknown":
                    self.assertIsNone(
                        value,
                        msg=f"{label} [{tag}] {path}: el value de un cubo "
                            f"`unknown` es null (fue {value!r})")
        # regresión por cada medida donde un 0 sería fabricado
        leaf = self.measure_leaf(session_poor.get("measures", {}),
                                 "time_to_first_resume",
                                 label + " time_to_first_resume")
        self.assertEqual(
            leaf.get("bucket"), "unknown",
            msg=f"{label}: time_to_first_resume (tiempo no observable) NO "
                f"puede quedar `observed` con value null (fue "
                f"{leaf.get('bucket')!r})")
        self.assertIsNone(leaf.get("value"),
                          msg=f"{label}: time_to_first_resume value null")
        _, session_poor_steps = self.session_with_steps(
            self.store_poor, label + " input_per_step")
        leaf = self.measure_leaf(session_poor_steps.get("measures", {}),
                                 "input_per_step", label + " input_per_step")
        value = leaf.get("value")
        self.assertIsInstance(value, list,
                              msg=f"{label}: input_per_step lista")
        self.assertIn(
            None, value,
            msg=f"{label}: el paso con componente faltante tiene proxy null "
                f"(nunca 0/subtotal; fue {value!r})")
        for key in ("total_output", "max_output"):
            leaf = self.measure_leaf(session_noout.get("measures", {}), key,
                                     f"{label} {key}")
            self.assertEqual(
                leaf.get("bucket"), "unknown",
                msg=f"{label}: {key} sin evidencia de salida NO puede ser "
                    f"`observed` con 0 fabricado (fue {leaf.get('bucket')!r})")
            self.assertIsNone(leaf.get("value"),
                              msg=f"{label}: {key} value null (nunca 0)")

    # --------------------------------------- (5) [D4] despacho declarado

    def test_t5_5_d4_reader_declares_recognized_dispatch_tools(self):
        """[D4] El documento declara en la clave de nivel superior `reader` la
        lista `dispatch_tools` de herramientas de despacho reconocidas (al
        menos `subagent` y `task`); una llamada a una herramienta NO
        reconocida (`dispatch_unknown`) NO produce despacho observado
        (`first_dispatch.status == "absent"`) y su causa DISTINGUE «no
        ocurrió» de «no reconocido»: nombra el conjunto reconocido y declara
        el límite (un despacho fuera del conjunto NO es detectado); una
        llamada a `task` SÍ produce `first_dispatch` observado con su posición
        (PD-6, PD-16; INV-9)."""
        label = "T5(5) despacho"
        doc, session = self.session_of(self.store_dispatch_task, label)
        reader = doc.get("reader")
        self.assertIsInstance(
            reader, dict,
            msg=f"{label}: el documento declara la clave de nivel superior "
                f"`reader` (fue {reader!r})")
        tools = reader.get("dispatch_tools")
        self.assertIsInstance(
            tools, list,
            msg=f"{label}: reader.dispatch_tools es la lista de herramientas "
                f"de despacho reconocidas (fue {tools!r})")
        for known in (DISPATCH_TOOL_KNOWN, DISPATCH_TOOL_TASK):
            self.assertIn(
                known, tools,
                msg=f"{label}: reader.dispatch_tools contiene {known!r} (fue "
                    f"{tools!r})")
        fd = self.milestone(session.get("milestones", {}), "first_dispatch",
                            label)
        self.assertEqual(
            fd.get("status"), "observed",
            msg=f"{label}: una llamada a `task` produce first_dispatch "
                f"OBSERVADO (fue {fd.get('status')!r})")
        position = fd.get("position")
        self.assertIsInstance(
            position, dict,
            msg=f"{label}: el despacho observado trae su posición "
                f"({position!r})")
        self.assertIn("call_index", position,
                      msg=f"{label}: la posición trae call_index")
        self.assertIn("seq", position, msg=f"{label}: la posición trae seq")
        # herramienta NO reconocida → absent, con causa que distingue
        _, session_unknown = self.session_of(self.store_dispatch_unknown,
                                             label + " (no reconocida)")
        fd_unknown = self.milestone(session_unknown.get("milestones", {}),
                                    "first_dispatch",
                                    label + " (no reconocida)")
        self.assertEqual(
            fd_unknown.get("status"), "absent",
            msg=f"{label}: una llamada a una herramienta de despacho NO "
                f"reconocida (`{DISPATCH_TOOL_UNKNOWN}`) NO produce despacho "
                f"observado (fue {fd_unknown.get('status')!r})")
        cause = fd_unknown.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"{label}: el absent trae su causa que distingue «no ocurrió» "
                f"de «no reconocido» (fue {cause!r})")
        low = cause.lower()
        self.assertIn(
            DISPATCH_TOOL_KNOWN, low,
            msg=f"{label}: la causa nombra el conjunto reconocido "
                f"(`{DISPATCH_TOOL_KNOWN}`); fue {cause!r}")
        self.assertIn(
            DISPATCH_TOOL_TASK, low,
            msg=f"{label}: la causa nombra el conjunto reconocido "
                f"(`{DISPATCH_TOOL_TASK}`); fue {cause!r}")
        self.assertTrue(
            any(w in low for w in ("only", "solo", "recogni", "reconoc",
                                   "not detected", "no detect", "no se "
                                   "detecta", "outside", "fuera del "
                                   "conjunto", "not recognized",
                                   "no reconocid")),
            msg=f"{label}: la causa declara el LÍMITE (un despacho hecho con "
                f"una herramienta fuera del conjunto NO es detectado); fue "
                f"{cause!r}")

    # ---------------------------------- (6) [D5] casado parcial --session

    def test_t5_6_d5_partial_session_match_declared_hashed(self):
        """[D5] Con dos referencias `--session`, una existente y una
        inexistente: rc=0 (no es fallo cerrado), la sesión existente se mide
        (aparece en `sessions[]`) y la referencia pedida que NO se encuentra
        se declara en `unknowns[]` con causa; PRIVACIDAD (PD-10/INV-7): el id
        crudo no aparece en NINGUNA parte de la salida y la causa porta una
        referencia de la MISMA forma hasheada que `session_ref` (derivada del
        propio documento).

        Refuerzo del oráculo (esta reapertura): la causa debe nombrar una
        referencia hasheada que NO sea la de NINGUNA sesión medida — la
        referencia PEDIDA y NO ENCONTRADA queda declarada; NO alcanza con que
        la causa nombre (o devuelva el eco de) las referencias MEDIDAS. El
        assert discrimina: un texto de causa que solo nombre la referencia
        medida no lo satisface (comprobación negativa interna).

        El fallo cerrado cuando NINGUNA referencia casa se conserva y se
        verifica acá: con todas las referencias sin casar, `rc != 0` con
        diagnóstico por stderr (nunca un subconjunto vacío medido con rc=0)."""
        label = "T5(6) casado parcial"
        proc = self.run_meter("--store", str(self.store_alpha),
                              "--session", SESSION_ALPHA,
                              "--session", SESSION_MISSING)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: rc=0 (una referencia inexistente entre varias no "
                f"es fallo cerrado); stderr={proc.stderr[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        # privacidad: ningún id crudo en la salida (PD-10/INV-7)
        self.assertNotIn(
            SESSION_MISSING, out,
            msg=f"{label}: el id crudo pedido NO aparece en NINGUNA parte de "
                "la salida (se declara de forma hasheada; PD-10/INV-7)")
        self.assertNotIn(
            SESSION_ALPHA, out,
            msg=f"{label}: el id crudo de la sesión medida tampoco aparece "
                "(referencia hasheada)")
        # la sesión existente se mide
        sessions = doc.get("sessions")
        self.assertIsInstance(sessions, list, msg=f"{label}: sessions[] lista")
        self.assertEqual(
            len(sessions), 1,
            msg=f"{label}: la sesión existente se mide (un subconjunto "
                f"silencioso no: se mide la que casa y se declara la que no; "
                f"fue {len(sessions)})")
        session_ref = sessions[0].get("session_ref")
        self.assertIsInstance(
            session_ref, str,
            msg=f"{label}: la sesión medida trae su session_ref hasheado "
                f"(fue {session_ref!r})")
        # la referencia pedida que NO se encuentra se declara con causa
        pattern = _hashed_ref_pattern(session_ref)
        texts = self.unknown_texts(doc)
        hits = [t for t in texts if re.search(pattern, t)]
        self.assertTrue(
            hits,
            msg=f"{label}: la referencia pedida que NO se encuentra se "
                "declara en unknowns[] con causa, portando una referencia de "
                f"la MISMA forma hasheada que session_ref (patrón={pattern!r}; "
                f"textos hoy: {texts!r})")
        self.assertTrue(
            any(any(w in t for w in ("not found", "no encontrad", "missing",
                                     "ausent", "unknown", "desconoc"))
                for t in hits),
            msg=f"{label}: la entrada es una CAUSA de ausencia "
                f"(hits={hits!r})")
        # [refuerzo D5] la causa nombra la referencia PEDIDA y NO ENCONTRADA:
        # se extraen de los textos de la causa los tokens hashed de la MISMA
        # forma que session_ref (mismo prefijo + digest de la misma longitud,
        # derivados del propio documento) y se exige que AL MENOS UNO sea
        # DISTINTO de toda sesión medida (session_ref y parent_ref si existe).
        measured_refs = {
            ref.lower()
            for session in sessions
            for ref in (session.get("session_ref"), session.get("parent_ref"))
            if isinstance(ref, str)
        }
        cause_tokens = set()
        for text in hits:
            cause_tokens.update(_hashed_refs_in(text, session_ref))
        undeclared = [ref for ref in cause_tokens
                      if ref.lower() not in measured_refs]
        self.assertTrue(
            undeclared,
            msg=f"{label}: la causa debe nombrar una referencia hasheada que "
                "NO es la de NINGUNA sesión medida — la referencia PEDIDA y "
                "NO ENCONTRADA queda declarada; no basta con que la causa "
                "nombre las referencias MEDIDAS. Tokens hashed de la causa: "
                f"{sorted(cause_tokens)!r}; referencias medidas: "
                f"{sorted(measured_refs)!r}. Un oráculo satisfecho por el eco "
                "del hash de una sesión medida no prueba D5")
        # el assert DISCRIMINA: un texto de causa que SOLO nombre la
        # referencia MEDIDA no lo satisface (comprobación negativa interna,
        # sin tocar el producto).
        measured_only = (f"{label} synthetic: measured reference(s), hashed: "
                         f"{session_ref}")
        self.assertTrue(
            _hashed_refs_in(measured_only, session_ref),
            msg=f"{label}: sonda interna — el texto sintético porta la "
                "referencia medida")
        self.assertFalse(
            [ref for ref in _hashed_refs_in(measured_only, session_ref)
             if ref.lower() not in measured_refs],
            msg=f"{label}: DISCRIMINACIÓN — un texto de causa que SOLO "
                "nombre la referencia MEDIDA (sin la pedida-no-encontrada) NO "
                "satisface el assert: el hash de una referencia medida "
                "presente en la causa no es prueba de que la referencia "
                "pedida quede declarada")
        # [invariante D5 conservado] el fallo cerrado cuando NINGUNA
        # referencia casa sigue vigente (el casado parcial no lo degrada):
        # nunca un conjunto vacío medido con rc=0.
        none_proc = self.run_meter("--store", str(self.store_alpha),
                                   "--session", SESSION_MISSING)
        self.assertNotEqual(
            none_proc.returncode, 0,
            msg=f"{label}: con NINGUNA referencia casando el medidor sigue "
                "fallando cerrado (rc != 0), nunca mide un conjunto vacío con "
                f"rc=0 (D5/PD-2/PD-15); stdout="
                f"{none_proc.stdout[:200]!r}")
        self.assertTrue(
            none_proc.stderr.strip(),
            msg=f"{label}: el fallo cerrado trae DIAGNÓSTICO por stderr "
                "(PD-15)")
        none_out = none_proc.stdout.decode("utf-8", errors="replace")
        none_err = none_proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            SESSION_MISSING, none_out + none_err,
            msg=f"{label}: en el fallo cerrado el id crudo pedido tampoco "
                "aparece (privacidad; PD-10/INV-7)")

    # --------------------------- (7) [D1] agregados por paso: suma completa

    def test_t5_7_d1_aggregated_sum_partial_not_observed(self):
        """[D1, la clase — agregados por paso] Una medida que SUMA un
        componente sobre los pasos del tramo (`accumulated` = Σ
        `tokens.input`, `cache.read` = Σ `cache.read`, `cost` = Σ `cost`) es
        una observación COMPLETA solo si TODOS los pasos del tramo reportan
        ese componente (un 0 REPORTADO cuenta como reportado). Control
        positivo (`SESSION_AGG_COMPLETE`, 3 pasos, todos reportan): la suma
        queda bucket `observed` con su valor (24 / 12 / 0.875). Subclase que
        cierra esta unidad (`SESSION_AGG_PARTIAL`, 5 pasos, 3 reportan y 2
        no): la medida NO es una observación completa → bucket `unknown`,
        value null (NUNCA el subtotal parcial 230 / 120 / 1.0 presentado como
        `observed`) y UNA causa AGREGADA en `unknowns[]` (una por medida,
        nunca una por paso) que nombra la cobertura y el componente, p. ej.
        «the stretch reports tokens.input in 3 of 5 steps: 2 steps do not
        report it, so the sum is not a complete observation of the stretch;
        no partial sum is emitted». PD-4, PD-8, PD-12; INV-4)."""
        label = "T5(7) agregados por paso"
        # -- control positivo: TODOS los pasos reportan el componente --
        control = label + " (control completo)"
        _, session_complete = self.session_of(self.store_agg_complete, control)
        for key, want in (("accumulated", AGG_COMPLETE_INPUT_SUM),
                          ("cache.read", AGG_COMPLETE_READ_SUM),
                          ("cost", AGG_COMPLETE_COST_SUM)):
            leaf = self.measure_leaf(session_complete.get("measures", {}), key,
                                     control)
            self.assertEqual(
                leaf.get("bucket"), "observed",
                msg=f"{control}: con TODOS los pasos reportando `{key}` la "
                    f"suma SÍ es una observación completa (`observed`); fue "
                    f"{leaf.get('bucket')!r}")
            self.assertEqual(
                leaf.get("value"), want,
                msg=f"{control}: la suma completa de {key} es {want} (fue "
                    f"{leaf.get('value')!r})")
        # -- subclase: un paso parcial NO se presenta como observado completo --
        doc, session = self.session_of(self.store_agg_partial, label)
        cases = (
            ("accumulated", AGG_COMPONENT_INPUT, AGG_PARTIAL_INPUT_SUM),
            ("cache.read", AGG_COMPONENT_CACHE_READ, AGG_PARTIAL_READ_SUM),
            ("cost", AGG_COMPONENT_COST, AGG_PARTIAL_COST_SUM),
        )
        texts = self.unknown_texts(doc)
        for key, component, partial in cases:
            leaf = self.measure_leaf(session.get("measures", {}), key, label)
            self.assertEqual(
                leaf.get("bucket"), "unknown",
                msg=f"{label}: `{key}` suma `{component}` y al menos un paso "
                    f"del tramo NO lo reporta → NO es una observación "
                    f"completa → bucket `unknown` (fue {leaf.get('bucket')!r}; "
                    "D1/PD-4/INV-4: un subtotal parcial nunca se presenta como "
                    "observado)")
            self.assertIsNone(
                leaf.get("value"),
                msg=f"{label}: `{key}` value null — NUNCA el subtotal parcial "
                    f"{partial} presentado como observado (fue "
                    f"{leaf.get('value')!r})")
            hits = self.coverage_hits(texts, component,
                                      total=AGG_PARTIAL_TOTAL,
                                      missing=AGG_PARTIAL_MISSING)
            self.assertEqual(
                len(hits), 1,
                msg=f"{label}: `{key}` declara UNA causa AGREGADA (nunca una "
                    f"por paso) en unknowns[] que nombra `{component}` y la "
                    f"cobertura del tramo ("
                    f"{AGG_PARTIAL_TOTAL - AGG_PARTIAL_MISSING} de "
                    f"{AGG_PARTIAL_TOTAL} pasos lo reportan; "
                    f"{AGG_PARTIAL_MISSING} no) (hits={hits!r}; textos="
                    f"{texts!r})")
            low = hits[0]
            self.assertTrue(
                any(w in low for w in AGG_INCOMPLETE_WORDS),
                msg=f"{label}: la causa agregada de `{key}` declara que la "
                    f"suma NO es una observación completa (fue {hits[0]!r})")

    # ---------------------- (8) [D1 + PD-4] cache.write y cobertura

    def test_t5_8_d1_cache_write_pd4_and_stretch_coverage(self):
        """[D1 + PD-4] `cache.write` conserva su regla: un 0 REPORTADO por el
        proveedor es «no reportado» → bucket `unknown`, value null, con causa,
        NUNCA `0` (tanto si TODOS los pasos lo reportan — muestra 1 — como si
        alguno no). Además, cuando al menos un paso del tramo NO reporta
        `cache.write`, la causa declara la COBERTURA del tramo (una entrada
        agregada, p. ej. «the stretch reports cache.write in 3 of 5 steps: 2
        steps do not report it ...»; nunca una por paso). PD-4, PD-8, PD-12;
        INV-4)."""
        label = "T5(8) cache.write"
        control = label + " (todos reportan)"
        _, session_complete = self.session_of(self.store_agg_complete, control)
        leaf = self.measure_leaf(session_complete.get("measures", {}),
                                 AGG_COMPONENT_CACHE_WRITE, control)
        self.assertEqual(
            leaf.get("bucket"), "unknown",
            msg=f"{control}: el 0 que reporta el proveedor para cache.write es "
                f"«no reportado» → `unknown`, nunca `observed` (fue "
                f"{leaf.get('bucket')!r}; PD-4/INV-4)")
        self.assertIsNone(
            leaf.get("value"),
            msg=f"{control}: cache.write value null (nunca 0); fue "
                f"{leaf.get('value')!r}")
        doc, session = self.session_of(self.store_agg_partial, label)
        leaf = self.measure_leaf(session.get("measures", {}),
                                 AGG_COMPONENT_CACHE_WRITE, label)
        self.assertEqual(
            leaf.get("bucket"), "unknown",
            msg=f"{label}: cache.write sigue `unknown` (PD-4); fue "
                f"{leaf.get('bucket')!r}")
        self.assertIsNone(leaf.get("value"),
                          msg=f"{label}: cache.write value null (nunca 0); fue "
                              f"{leaf.get('value')!r}")
        texts = self.unknown_texts(doc)
        hits = self.coverage_hits(texts, AGG_COMPONENT_CACHE_WRITE,
                                  total=AGG_PARTIAL_TOTAL,
                                  missing=AGG_PARTIAL_MISSING)
        self.assertEqual(
            len(hits), 1,
            msg=f"{label}: cuando algún paso del tramo NO reporta cache.write, "
                f"la causa declara ADEMÁS la cobertura ("
                f"{AGG_PARTIAL_TOTAL - AGG_PARTIAL_MISSING} de "
                f"{AGG_PARTIAL_TOTAL} pasos lo reportan; "
                f"{AGG_PARTIAL_MISSING} no), en UNA entrada agregada "
                f"(hits={hits!r}; textos={texts!r})")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
