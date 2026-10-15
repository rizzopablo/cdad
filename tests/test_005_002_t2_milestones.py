#!/usr/bin/env python3
"""005-002 T2 RED — hitos, corte con el borde fijado, lecturas de orientación
y tres magnitudes (PD-5, PD-6, PD-7, PD-8).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (§2; PD-5, PD-6, PD-7,
  PD-8; INV-4, INV-9).
- docs/specs/005-002-session-context-meter/plan.md (T2: ficha de la tarea:
  «RED: el registro de T1 no expone hitos ni corte; el total y el conteo de
  `read` no se distinguen; la sesión completa se mezcla con el tramo; el
  fixture que toma el borde en el último mensaje con herramienta da
  12,40/202.222 y debe fallar»).
- docs/specs/005-002-session-context-meter/discovery.md §1.2–§1.7 y §2 (forma
  del esquema y de los recorridos; sonda 2; muestra 1).
- docs/epics/epic-005-real-operation/execution.md (delegación HITL vigente).

Oracle observable: la SALIDA del WRAPPER FINO `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable), NUNCA importando el módulo:

    python3 scripts/cdad_context_meter.py --store PATH \
        [--idle-threshold MINUTES] [--session REF] [--limit N] [--json]

El contrato observable es el JSON por stdout, el rc y el diagnóstico por
stderr. NO se aserte sobre nombres internos de funciones/clases/módulos ni
sobre plumbing; sin mocks sobre plumbing.

Fixtures 100% SINTÉTICOS: construidos por este test en un directorio temporal
con SQLite; los identificadores de sesión, rutas, textos, proveedor y modelo
son INVENTADOS; la base real del runtime JAMÁS se abre. Los tamaños y
cantidades reproducen EXACTAMENTE las cifras pinneadas de las muestras
(spec §2/§6, ficha T2 del plan):
- MUESTRA 1: primer tramo = 101 llamadas, FIEL a la forma del recorrido
  (100 de 101 llamadas CON salida); ventana 12,55 min (12,5471); la MAYOR
  salida del tramo es 51.243 car. (eso es lo que pinea la spec PD-5/§6);
  el TOTAL de salida del tramo NO está pinneado por el contrato: es la
  suma de las salidas del propio fixture, calculada por el constructor
  (claramente mayor que el máximo); proxy del último paso 203.276 tok
  (input 1.164 + cache.read 202.112 + cache.write 0); cierre en el mensaje
  `assistant` que cierra el tramo SIN llamada de herramienta propia, seguido
  de un evento `idle` con outcome `succeeded`; brecha ~66,4 h (66,4 h =
  3.984 min > umbral default 60); 20 llamadas más → 121 en el total.
  NUMERO ALTERNATIVO DECLARADO Y NO USADO: si el borde se tomara en el
  último mensaje CON llamada de herramienta la ventana sería 12,40 min y el
  proxy del último paso 202.222 tok — el test deja constancia de que la
  ventana reportada es 12,55/203.276 y NO 12,40/202.222 (spec PD-5: «la otra
  definición NO es la usada y se hace visible»).
- SONDA 2: 29 llamadas; el resume real es la llamada #19; 18 previas:
  8 read + 2 glob + 8 shell; el `resume --help` (#10) NO cuenta; la NOVENA
  read de la sesión es la #24, POSTERIOR al resume; una llamada `write` cuyo
  CONTENIDO menciona «resume» NO cuenta como hito.
- S-BOOT-04 (variante): primer despacho de trabajo de rol = llamada a la
  herramienta `subagent` → first_dispatch observado; el hito de resume
  queda independiente (ausente).

DECISIONES DECLARADAS PARA EL GREEN (el implementer lee este test como
oráculo; la spec pinnea los VALORES pero no fija nombre para las cifras del
tramo y de la sesión completa ni para los desgloses). Claves ADICIONALES de
measures introducidas por este test (snake_case, coherentes con las ya
declaradas en T1, todas bucket=`observed` con unit/provenance):

- `segment_duration` — duración (unit minutes) de la ventana del TRAMO
  usado = primer `time_created` → último `time_updated` del tramo (PD-5).
- `tool_calls` — llamadas de herramienta DEL TRAMO (unit calls).
- `session_tool_calls` — llamadas de herramienta de TODA la sesión
  (unit calls); se reporta SEPARADA de `tool_calls`: nunca se promedian
  tramo y sesión (PD-5), y la diferencia 101 vs 121 queda visible.
- `session_reads` — llamadas a la herramienta `read` de TODA la sesión
  (unit calls), etiquetada APARTE de `previous_reads` (que cuenta solo las
  previas al hito): ambos números aparecen etiquetados y NO se colapsan en
  uno (PD-7); para la sonda 2: 9 vs 8.
- `previous_calls_by_tool` — desglose por herramienta de las llamada
  anteriores al hito `first_resume` (PD-7): objeto {tool: conteo}; para la
  sonda 2: {"read": 8, "glob": 2, "shell": 8}.

Semántica declarada para claves del contrato ya existentes:

- `milestones.<hito>.position` = {call_index, seq}: `call_index` es el
  ORDINAL 1-based de la llamada de herramienta dentro de la sesión (se
  cuentan las partes type:"tool" de los mensajes `assistant` en orden de
  seq; cada una es una llamada; cada mensaje trae UNA parte tool en estos
  fixtures) y `seq` es el seq de la fila `session_message` que porta la
  llamada. `time_relative` y la medida `time_to_first_*` son MINUTOS
  relativos al inicio del tramo, medidos sobre los mensajes (en los
  fixtures time_created == time_updated por mensaje, sin ambigüedad).
- El detector de `resume` reconoce el SUBCOMANDO (la llamada shell cuyo
  comando ejecuta `resume` tras la ruta del CLI de continuidad), NO la ruta
  exacta (V3); excluye ayuda (`--help`/-h); un `write` cuyo contenido
  menciona «resume» NO es un hito (PD-6).
- El detector de `dispatch` reconoce la primera llamada a la herramienta
  `subagent` (la que abre sesión worker, p. ej. S-BOOT-04; PD-6/D5).
- Hito AUSENTE (no ocurrió en la traza): status `absent` con `cause`
  textual; las medidas asociadas (`time_to_first_resume`,
  `time_to_first_dispatch`, `previous_calls`, `previous_reads`) quedan
  value null + bucket `unknown` con causa — NUNCA 0 (PD-4/PD-8).
- Cada entrada de sesión reporta el PRIMER tramo contiguo como su
  ventana/measures/milestones (la línea base PD-5) yporta además en
  measures las cifras de TODA la sesión bajo las claves `session_*`,
  separadas de las del tramo (PD-5: sin promediar).
- `input_per_step.value` = lista ORDENADA de los proxys por paso
  (input + cache.read + cache.write reportado del PASO), un elemento por
  mensaje `assistant` del tramo EN ORDEN de seq — el mensaje `assistant`
  que cierra el tramo (sin llamada de herramienta propia) TAMBIÉN es un
  paso, y es el ÚLTIMO elemento (PD-5: el «último paso» es ese mensaje).
- `accumulated.value` = suma, sobre los pasos del tramo, de los tokens de
  ENTRADA reportados por paso (PD-8: «procesamiento acumulado = suma de
  pasos»); bucket `observed`.
- `cost.value` = suma del costo reportado por los pasos del tramo (PD-8);
  bucket `observed` cuando el costo está reportado, `unknown` si no.
- El proxy de contexto cargado por paso es `estimated` (spec PD-8: proxy
  declarado, NO la ventana real) aunque cache.write individual quede
  `unknown`/null (PD-4).

RED HOY: el GREEN de T1 dejó los hitos en `unknown` sin detección y sin el
corte con el borde fijado (las métricas del tramo se calculan sobre la
sesión completa: p. ej. max_output ≠ 51.243 — la sesión completa trae
además el máximo post-gap 61.000 — y total_output ≠ la suma de las
salidas del tramo según el fixture). Cada test de este archivo
falla HOY por AssertionError de CONTRATO (valor ausente o incorrecto en la
salida observable), nunca por ImportError/sintaxis/setup: el test no importa
el módulo del medidor.
"""

from __future__ import annotations

import json
import os
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

DEFAULT_THRESHOLD_MIN = 60  # default declarado PD-15(c)
TOOL_STATUS_VALUES = ("observed", "absent", "unknown")
BUCKET_VALUES = ("observed", "estimated", "unknown")
MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")

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

# --------------------------------------------------------- cifras pinneadas

# --- muestra 1 (PD-5) ---
M1_TRAMO_WINDOW_MIN = 12.5471     # 12,55 min (espec); ventana del tramo
M1_ALT_WINDOW_MIN = 12.40         # borde alternativo: NO usado
M1_TRAMO_CALLS = 101              # llamadas del primer tramo contiguo
M1_SESSION_CALLS = 121            # toda la extensión (101 + 20 post-gap)
# Salidas del tramo: la spec pinea SOLO la MAYOR salida individual
# (51.243 car., PD-5/§6 y criterio §4); el TOTAL NO está pinneado por el
# contrato. El total se deriva del PROPIO fixture: distribución fiel a la
# forma del recorrido real (100 de las 101 llamadas con salida; la mayor
# 51.243 y las demás tamaños INVENTADOS menores → total claramente mayor
# que el máximo). NADA de mediciones de la base real acá.
M1_MAX_OUTPUT = 51_243            # car. Unicode; MAYOR salida individual


def _m1_tramo_output_size(i: int) -> int:
    """Tamaño de salida (car. Unicode) de la llamada #i del tramo de la
    MUESTRA 1. Fiel al recorrido real: 100 de 101 llamadas con salida;
    la MAYOR es 51.243 (pinneada por la spec) y las demás son tamaños
    inventados menores; la única llamada SIN salida es la #1."""
    if i == 1:
        return 0                 # la única llamada sin salida (100/101)
    if i == 2:
        return M1_MAX_OUTPUT     # 51.243: la mayor salida del tramo
    if i == 3:
        return 9_000
    if i == 4:
        return 6_000
    if i == 5:
        return 3_000
    if i == 6:
        return 1_500
    return 400                   # salidas menores, tamaño inventado


M1_TRAMO_TOTAL_OUTPUT = sum(_m1_tramo_output_size(i)
                            for i in range(1, M1_TRAMO_CALLS + 1))
assert M1_TRAMO_TOTAL_OUTPUT > M1_MAX_OUTPUT, (
    "consistencia del fixture: el total del tramo debe ser claramente "
    "mayor que el máximo (distribución fiel de salidas)")
M1_PROXY_LAST_STEP = 203_276      # input 1164 + cache.read 202112 (+w 0)
M1_ALT_PROXY_LAST_STEP = 202_222  # proxy del paso #101 (borde NO usado)
M1_ACCUMULATED_INPUT = 100 * 100 + 1_160 + 1_164
# suma de tokens.input de los 102 pasos del tramo (100 llamadas con
# input 100 + la llamada #101 con 1.160 + el cierre con 1.164); derivada
# del PROPIO fixture, no de la base real
M1_COST = 0.75                    # suma del costo reportado por los pasos
                                  # (los pasos portan 0.0; el cierre 0.75)
M1_POST_GAP_MAX = 61_000          # max_output POST al tramo (trampa de mezcla)
# salidas de las llamadas post-gap: 18*100 + 1.200 (la write) y el máximo
# post-gap 61.000 aparte; derivadas del propio fixture
M1_POST_GAP_OUTPUTS = M1_POST_GAP_MAX + 1_200 + 18 * 100
M1_GAP_MIN = 3_984.0              # ~66,4 h entre tramo 1 y tramo 2
M1_STEP_MS = 7_440                # paso entre llamadas del tramo 1 (ms)
M1_TOTAL_MS = 752_826             # ventana usada = 12,5471 min
M1_ALT_TOTAL_MS = 744_000         # 12,40 min (borde NO usado)
M1_NOGAP_PAUSE_MS = 300_000       # 5 min < umbral → sin brecha
# sin brecha: ventana = toda la sesión (752826 + 300000 + 20*30000 ms);
# derivada del PROPIO fixture (paso post-gap = 30.000 ms, el fixture usa
# el paso de la sonda 2)
M1_NOGAP_WINDOW_MIN = (M1_TOTAL_MS + M1_NOGAP_PAUSE_MS
                       + 20 * 30_000) / 60_000
# con --idle-threshold 5000 (> 3984): la brecha deja de cortar y la
# ventana es toda la sesión (752826 + 3984*60000 + 20*30000 ms)
M1_THRESHOLD_WINDOW_MIN = (M1_TOTAL_MS + M1_GAP_MIN * 60_000
                           + 20 * 30_000) / 60_000
M1_THRESHOLD_MIN = 5_000          # umbral > brecha → la brecha deja de cortar

# --- sonda 2 (PD-6/PD-7) ---
S2_SESSION_CALLS = 29             # 8 read + 2 glob + 8 shell + #19 + 10 más
S2_RESUME_INDEX = 19              # primer resume real (llamada #19)
S2_RESUME_SEQ = 20                # seq del mensaje que porta la llamada #19
# 19*30s = 9,5 min relativo (19 pasos × S2_STEP_MS = 30.000 ms, definido
# al pie de este bloque; derivado del PROPIO fixture)
S2_RESUME_TIME_MIN = S2_RESUME_INDEX * 30_000 / 60_000
S2_PREV_CALLS = 18                # llamadas antes del hito
S2_PREV_READS = 8                 # read antes del hito (PD-7: definición)
S2_SESSION_READS = 9              # total read de la sesión; la #24 posterior
S2_PREV_BY_TOOL = {"read": 8, "glob": 2, "shell": 8}
S2_STEP_MS = 30_000

# --- S-BOOT-04 (variante PD-6) ---
SB_DISPATCH_INDEX = 3             # subagent = llamada #3
SB_DISPATCH_SEQ = 4               # seq del mensaje que porta la llamada
# 3*60s = 3,0 min (3 pasos × SB_STEP_MS; derivado del PROPIO fixture)
SB_DISPATCH_TIME_MIN = SB_DISPATCH_INDEX * 60_000 / 60_000
SB_STEP_MS = 60_000

# --- dispositivos sintéticos ---
ROLE = "cdad-orchestrator"
MODEL_SYNTH = '{"id":"model-alpha","providerID":"prov-a"}'
DISPATCH_TOOL = "subagent"
CONTINUITY_CLI_STEM = "python3 skills/cdad-cycle/scripts/cdad_continuity.py"
RESUME_HELP_CMD = CONTINUITY_CLI_STEM + " resume --help"      # NO cuenta
RESUME_REAL_CMD = CONTINUITY_CLI_STEM + " resume --project-root ."

# ------------------------------------------------------------- fixtures

BASE_MS = 1_760_000_000_000  # epoch ms SINTÉTICO, fijo (determinismo)


def _user_data(ms: float, text: str) -> str:
    """Forma `user` (discovery §1.3): {time, text}."""
    return json.dumps({"time": ms, "text": text}, sort_keys=True)


def _idle_data(ms: float, outcome: str) -> str:
    """Forma `idle` (discovery §1.3): {time, outcome}."""
    return json.dumps({"time": ms, "outcome": outcome}, sort_keys=True)


def _tool_part(name: str, text: str, ms: float, *, input_args: dict,
               part_id: str) -> dict:
    """Parte `tool` (discovery §1.4): state.content=[{type:text,text}] → el
    tamaño de salida = suma de len(text); state.input = argumentos;
    state.metadata.{status, truncated, exit}."""
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": {
            "status": "completed",
            "input": input_args,
            "content": [{"type": "text", "text": text}],
            "metadata": {"status": "completed", "truncated": False,
                         "exit": 0},
        },
        "time": {"created": ms, "ran": ms, "completed": ms},
    }


def _assistant_data(agent: str, model: str, ms: float, parts: list,
                    tokens: tuple, cost: float | None) -> str:
    """Forma `assistant` (discovery §1.3): time/agent/model/content/cost/
    tokens {input, output, reasoning, cache:{read, write}}.
    En TODOS los fixtures time_created == time_updated por mensaje."""
    tin, tout, treason, tread, twrite = tokens
    return json.dumps({
        "time": {"created": ms, "streamed": ms, "completed": ms},
        "agent": agent, "model": model, "content": parts,
        "tokens": {"input": tin, "output": tout, "reasoning": treason,
                   "cache": {"read": tread, "write": twrite}},
        "cost": cost,
    }, sort_keys=True)


def _insert_msg(conn: sqlite3.Connection, sid: str, seq: int, mtype: str,
                data: str, ms: float) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, mtype, seq, ms, ms, data))


def _insert_session(conn: sqlite3.Connection, sid: str, agent: str,
                    model: str, t0: float, t_end: float, sums: tuple,
                    cost: float | None) -> None:
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
         tin, tout, treason, tread, twrite, None, None, agent, model,
         t0, t_end, None, None, None, 0, None, None, None))


def _new_store(path: Path) -> sqlite3.Connection:
    """Store SQLite con el ESQUEMA observado (discovery §1.2–§1.6); columnas
    requeridas presentes, tipos de fila válidos (también los necesita el
    detector de esquema del GREEN T1, PD-2)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(SESSION_V2_DDL)
    conn.execute(SESSION_MESSAGE_DDL)
    return conn


def _build_muestra1(path: Path, *, with_gap: bool = True) -> None:
    """MUESTRA 1 sintética (forma del recorrido real; cifras pinneadas PD-5).
    Tramo 1: user + 101 llamadas (una por mensaje) + el mensaje `assistant`
    que CIERRA el tramo (SIN llamada de herramienta propia, proxy 203.276)
    + `idle` outcome succeeded; brecha ~66,4 h (o 5 min en la variante sin
    brecha); luego user + 20 llamadas más (salidas mayores y distintas al
    tramo: max 61.000 > 51.243, para que una mezcla tramo/sesión SEA visible).
    Distribución de salidas del tramo FIEL al recorrido (100 de 101
    llamadas con salida; la mayor 51.243 y las demás menores):
    `_m1_tramo_output_size`; el total es la suma de esas salidas.
    El paso #101 (último mensaje CON llamada de herramienta) porta el proxy
    del borde alternativo NO usado (202.222)."""
    sid = "sess-fixture-muestra1"
    conn = _new_store(path)
    t0 = BASE_MS + 10_000_000_000
    # 101 llamadas del tramo; #1 = subagent (primer despacho observado).
    tool_names = ([DISPATCH_TOOL]
                  + ["read"] * 25 + ["shell"] * 71
                  + ["execute"] + ["edit"] * 2 + ["write"])
    assert len(tool_names) == M1_TRAMO_CALLS, len(tool_names)
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i, name in enumerate(tool_names, start=1):
        seq = 1 + i                       # mensajes seq 2..102
        ms = t0 + (seq - 2) * M1_STEP_MS  # #101 (seq 102) en t0+744000
        if name == "shell":
            args = {"command": "echo fixture-step"}
        elif name == "read":
            args = {"path": "/fixture/dir/f%d.md" % i}
        elif name == "glob":
            args = {"pattern": "fixture-*"}
        elif name == "write":
            args = {"path": "/fixture/dir/notes-%d.md" % i,
                    "content": "notas del ciclo sinteticas"}
        elif name == "execute":
            args = {"command": "true"}
        else:  # subagent / edit
            args = {"path": "/fixture/dir/f%d.md" % i}
        if i == M1_TRAMO_CALLS:  # paso #101: proxy del borde alternativo
            tin, tread = 1_160, 201_062
        else:
            tin, tread = 100, 100
        tout, treason = 40, 5
        text = "o" * _m1_tramo_output_size(i)  # distribución fiel de salidas
        sum_in += tin; sum_cread += tread; sum_out += tout
        sum_reason += treason
        insert_ms = ms
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(ROLE, MODEL_SYNTH, insert_ms,
                                    [_tool_part(name, text, insert_ms,
                                                input_args=args,
                                                part_id=f"p{seq}")],
                                    (tin, tout, treason, tread, 0), 0.0),
                    insert_ms)
    # Mensaje `assistant` que CIERRA el tramo: SIN llamada de herramienta
    # propia; proxy 1164 + 202112 + 0 = 203.276; ventana usada: t0 → aquí.
    close_ms = t0 + M1_TOTAL_MS                      # 12,5471 min
    assert close_ms > t0 + M1_ALT_TOTAL_MS
    _insert_msg(conn, sid, 103, "assistant",
                _assistant_data(ROLE, MODEL_SYNTH, close_ms,
                                [{"type": "text", "text": "cierre"}],
                                (1164, 500, 0, 202_112, 0), M1_COST),
                close_ms)
    sum_in += 1164; sum_cread += 202_112; sum_out += 500
    # Cierre observable: `idle` con outcome succeeded (mismo instante).
    _insert_msg(conn, sid, 104, "idle", _idle_data(close_ms, "succeeded"),
                close_ms)
    # Brecha ~66,4 h (> umbral 60) o pausa 5 min (< umbral; sin brecha).
    gap_ms = (M1_GAP_MIN * 60_000) if with_gap else M1_NOGAP_PAUSE_MS
    t_gap_end = close_ms + gap_ms
    _insert_msg(conn, sid, 105, "user",
                _user_data(t_gap_end, "continua la sesion"), t_gap_end)
    for i in range(1, 21):
        seq = 105 + i                     # 20 llamadas post-gap: #102..#121
        ms = t_gap_end + i * S2_STEP_MS
        if i % 2 == 1:
            name, args = "read", {"path": "/fixture/dir/g%d.md" % i}
        elif i == 19:
            name = "write"
            args = {"path": "/fixture/dir/notes-x.md", "content": "notas"}
        else:
            name = "shell"
            args = {"command": "echo mas"}
        if i == 20:
            text = "z" * M1_POST_GAP_MAX          # 61.000 > max del tramo
        elif i == 19:
            text = "w" * 1_200
        else:
            text = "q" * 100
        tin, tread, tout, treason = 97, 93, 30, 5
        sum_in += tin; sum_cread += tread; sum_out += tout
        sum_reason += treason
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(ROLE, MODEL_SYNTH, ms,
                                    [_tool_part(name, text, ms,
                                                input_args=args,
                                                part_id=f"p{seq}")],
                                    (tin, tout, treason, tread, 0), None),
                    ms)
    total_ms = t_gap_end + 20 * S2_STEP_MS
    _insert_session(conn, sid, ROLE, MODEL_SYNTH, t0, total_ms,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), M1_COST)
    conn.commit()
    conn.close()


def _build_sonda2(path: Path) -> None:
    """SONDA 2 sintética (PD-6/PD-7): 29 llamadas; el resume real es la #19
    (shell con el subcomando `resume`, sin --help); el `resume --help` (#10)
    NO cuenta; 18 previas = 8 read + 2 glob + 8 shell; la NOVENA read es la
    #24 (posterior al hito); una `write` cuyo CONTENIDO menciona «resume»
    (#29) NO cuenta como hito. Sin brecha: un solo tramo = la sesión."""
    sid = "sess-fixture-sonda2"
    conn = _new_store(path)
    t0 = BASE_MS + 20_000_000_000
    _insert_msg(conn, sid, 1, "user", _user_data(t0, "arranque sonda"), t0)
    tools = (["read"] * 8                      # #1..#8
             + ["glob"]                        # #9
             + ["shell"]                       # #10: resume --help (excluido)
             + ["glob"]                        # #11
             + ["shell"] * 7                   # #12..#18
             + ["shell"]                       # #19: resume real
             + ["shell"] * 4                   # #20..#23
             + ["read"]                        # #24: NOVENA read (posterior)
             + ["shell"] * 4                   # #25..#28
             + ["write"])                      # #29: contenido menciona resume
    assert len(tools) == S2_SESSION_CALLS, len(tools)
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i, name in enumerate(tools, start=1):
        ms = t0 + i * S2_STEP_MS               # #k en t0 + k*30s
        seq = 1 + i
        if name == "shell":
            if i == 10:
                args = {"command": RESUME_HELP_CMD}
            elif i == S2_RESUME_INDEX:
                args = {"command": RESUME_REAL_CMD}
            else:
                args = {"command": "echo sonda"}
        elif name == "read":
            args = {"path": "/fixture/dir/s%d.md" % i}
        elif name == "glob":
            args = {"pattern": "sonda-*"}
        else:  # write: el CONTENIDO menciona resume — NO es un hito
            args = {"path": "/fixture/dir/notas.md",
                    "content": "el contenido menciona resume en texto libre"}
        tin, tread = 90, 80
        sum_in += tin; sum_cread += tread; sum_out += 30; sum_reason += 5
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(ROLE, MODEL_SYNTH, ms,
                                    [_tool_part(name, "out" * 15, ms,
                                                input_args=args,
                                                part_id=f"p{seq}")],
                                    (tin, 30, 5, tread, 0), None),
                    ms)
    total_ms = t0 + len(tools) * S2_STEP_MS    # 2,61 min lado real ≈ escala
    _insert_session(conn, sid, ROLE, MODEL_SYNTH, t0, total_ms,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), None)
    conn.commit()
    conn.close()


def _build_sboot04(path: Path) -> None:
    """S-BOOT-04 sintética (variante PD-6): el primer despacho de trabajo de
    rol es una llamada a la herramienta `subagent` (#3); el hito de resume
    queda independiente (sin resume → absent)."""
    sid = "sess-fixture-sboot04"
    conn = _new_store(path)
    t0 = BASE_MS + 30_000_000_000
    _insert_msg(conn, sid, 1, "user", _user_data(t0, "boot"), t0)
    tools = ["read", "glob", DISPATCH_TOOL, "shell", "read", "shell"]
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i, name in enumerate(tools, start=1):
        ms = t0 + i * SB_STEP_MS               # subagent (#3) en t0+180s
        seq = 1 + i
        assert i != SB_DISPATCH_INDEX or seq == SB_DISPATCH_SEQ
        if name == "shell":
            args = {"command": "echo boot"}
        elif name == "read":
            args = {"path": "/fixture/dir/b%d.md" % i}
        elif name == "glob":
            args = {"pattern": "boot-*"}
        elif name == DISPATCH_TOOL:
            args = {"path": "/fixture/dir/w%d.md" % i}
        else:
            args = {"path": "/fixture/dir/a%d.md" % i}
        tin, tread = 120, 110
        sum_in += tin; sum_cread += tread; sum_out += 20; sum_reason += 3
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(ROLE, MODEL_SYNTH, ms,
                                    [_tool_part(name, "b" * 40, ms,
                                                input_args=args,
                                                part_id=f"p{seq}")],
                                    (tin, 20, 3, tread, 0), None),
                    ms)
    _insert_session(conn, sid, ROLE, MODEL_SYNTH, t0,
                    t0 + len(tools) * SB_STEP_MS,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), None)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- helpers

def _measure_leaves(measures: object, prefix: str = ""):
    """Hojas de métrica: dict con {value, unit, provenance, bucket} a
    cualquier profundidad declarada (convención T1)."""
    if isinstance(measures, dict):
        if all(field in measures for field in MEASURE_FIELDS):
            yield prefix, measures
            return
        for key, value in measures.items():
            path = f"{prefix}.{key}" if prefix else key
            yield from _measure_leaves(value, path)


def _walk_dicts(obj: object):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_dicts(item)


def _assert_unit_mentions(leaf: dict, ctx: str, good: tuple[str, ...],
                          forbidden: tuple[str, ...] = ()) -> None:
    """La unidad declara alguna de las palabras esperadas y NINGUNA
    prohibida (any-match sobre unit en minúsculas)."""
    unit = str(leaf.get("unit", "")).lower()
    if not any(word in unit for word in good):
        raise AssertionError(
            f"{ctx}: la unidad no declara ninguna de {good!r} "
            f"(unit={unit!r}; leaf={leaf!r})")
    for word in forbidden:
        if word in unit:
            raise AssertionError(
                f"{ctx}: la unidad prohibida {word!r} aparece "
                f"(unit={unit!r}; leaf={leaf!r})")


def _assert_number_in_minutes(leaf: dict, ctx: str, expected: float,
                              delta: float = 0.01) -> None:
    """Guard: número + unidad en minutos + valor numérico esperado."""
    value = leaf.get("value")
    assert isinstance(value, (int, float)) and not isinstance(value, bool), \
        f"{ctx}: tiempo numérico en minutos (fue {value!r})"
    assert abs(value - expected) <= delta, (
        f"{ctx}: tiempo de {expected} min (fue {value!r})")


# ---------------------------------------------------------------- tests


class MilestonesT2Test(unittest.TestCase):
    """T2 RED de 005-002: un test por postcondición (PD-5, PD-6, PD-7,
    PD-8), contra la SALIDA del wrapper (stdout JSON + rc). Cada fixture es
    100% sintético; las cifras reproducen las pinneadas de la spec."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t2-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_muestra1 = base / "muestra1" / "sessions.db"
        self.store_muestra1_nogap = base / "muestra1-nogap" / "sessions.db"
        self.store_sonda2 = base / "sonda2" / "sessions.db"
        self.store_sboot04 = base / "sboot04" / "sessions.db"
        _build_muestra1(self.store_muestra1, with_gap=True)
        _build_muestra1(self.store_muestra1_nogap, with_gap=False)
        _build_sonda2(self.store_sonda2)
        _build_sboot04(self.store_sboot04)

    # -- corrida del wrapper (SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str) -> subprocess.CompletedProcess:
        if not METER_WRAPPER.is_file():
            self.fail(
                f"{FEATURE_ID} RED: el medidor `{METER_WRAPPER.name}` no "
                "existe aún — RED por CLI ausente (comportamiento "
                "ausente), nunca por ImportError: el test NO importa el "
                "módulo del medidor")
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
                "ejecuta aún (comportamiento ausente); el test NO importa "
                "el módulo del medidor")
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                f"PD-11 (acotado): el medidor no terminó dentro de "
                f"{CLI_TIMEOUT_S}s; timeout={exc!r}")

    def run_and_parse(self, store: Path, label: str, *extra: str) -> dict:
        proc = self.run_meter("--store", str(store), *extra)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición {label}: rc=0 sobre el fixture; "
                f"stdout={proc.stdout[:300]!r} stderr={proc.stderr[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:  # pragma: no cover
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        run = doc.get("run", {})
        self.assertEqual(
            run.get("schema"), "recognized",
            msg=f"precondición {label}: el fixture replica el esquema "
                "observado (discovery §1.2) y debe reconocerse — si sale "
                "unknown el RED sería de rejilla equivocada, no de "
                f"contrato; run={run}")
        self.assertIsInstance(
            doc.get("sessions"), list, msg=f"{label}: sessions[] es lista")
        self.assertEqual(
            len(doc["sessions"]), 1,
            msg=f"{label}: el fixture tiene UNA sesión y "
                "`--store` sin `--session/--limit` la mide entera")
        return doc

    def session_of(self, store: Path, label: str, *extra: str) -> dict:
        doc = self.run_and_parse(store, label, *extra)
        return doc["sessions"][0]

    # -- extractores con guard de RED (nunca KeyError/IndexError) --

    def measure_leaf(self, measures: object, key: str, ctx: str) -> dict:
        leaves = dict(_measure_leaves(measures))
        leaf = leaves.get(key)
        self.assertIsNotNone(
            leaf,
            msg=f"{ctx}: la medida declarada {key!r} NO existe en el "
                "registro — RED de contrato: el implementer debe emitirla "
                f"(hojas presentes: {sorted(leaves)})")
        self.assertIsInstance(leaf, dict, msg=f"{ctx}: {key} es una hoja")
        return leaf

    def measure_value(self, measures: object, key: str, ctx: str):
        return self.measure_leaf(measures, key, ctx).get("value")

    def measure_list(self, measures: object, key: str, ctx: str) -> list:
        value = self.measure_value(measures, key, ctx)
        self.assertIsInstance(
            value, list,
            msg=f"{ctx}: la medida {key!r} porta su lista declarada como "
                f"valor (fue {type(value).__name__}) — RED de contrato")
        return value

    def milestone(self, milestones: object, key: str, ctx: str) -> dict:
        self.assertIsInstance(
            milestones, dict, msg=f"{ctx}: milestones es objeto")
        self.assertIn(
            key, milestones,
            msg=f"{ctx}: milestones trae {key!r} (clave presente, PD-16)")
        mt = milestones[key]
        return mt

    # ------------------------------------------------------- PD-5 (C3)

    def test_pd5_cutoff_explicit_fixed_edge_and_session_separation(self):
        """PD-5: corte explícito y reproducible con el BORDE FIJADO sobre la
        muestra 1 (umbral default). El registro reporta la ventana y el
        corte usados (criterion/start_ref/end_ref/cutoff), la ventana del
        tramo es 12,55 min (NO 12,40), las llamadas del tramo son 101,
        max_output es 51.243 car. (la MAYOR salida, pinneada por la spec)
        y total_output es la SUMA de las salidas del propio fixture (el
        total NO está pinneado por el contrato y NO es el máximo), y el
        proxy del ÚLTIMO PASO es 203.276 tok (no 202.222); la sesión
        completa (121 llamadas) queda VISIBLE y SEPARADA del tramo, sin
        promediar. El borde alternativo (último mensaje CON herramienta →
        12,40 min / 202.222 tok) queda declarado en este módulo y NO se
        usa."""
        doc = self.run_and_parse(self.store_muestra1, "PD-5")
        session = doc["sessions"][0]
        measures = session["measures"]

        # (a) la ventana y el corte usados quedan explícitos y reproducibles:
        #     el corte (umbral) es observable en la VENTANA del tramo de la
        #     sesión, con sus refs de borde; el registro top-level declara
        #     criterion y cutoff usados.
        with self.subTest(punto="a-ventana-y-corte-explicitos"):
            session = doc["sessions"][0]
            t_win = session.get("window")
            self.assertIsInstance(
                t_win, dict, msg="PD-5(a): window de la sesión es objeto")
            for key in ("criterion", "start_ref", "end_ref", "cutoff"):
                self.assertIn(
                    key, t_win, msg=f"PD-5(a): window de sesión trae {key!r}")
            self.assertIsInstance(
                t_win["criterion"], str,
                msg="PD-5(a): criterion es texto que declara el método del "
                    "corte (primer tramo contiguo, borde fijado)")
            self.assertTrue(
                t_win["criterion"].strip(),
                msg="PD-5(a): criterion de la sesión no vacío")
            self.assertTrue(
                t_win["start_ref"] and t_win["end_ref"],
                msg="PD-5(a): la ventana del tramo usado porta sus refs de "
                    "borde (first time_created → último time_updated), "
                    "reproducibles desde el store")
            self.assertEqual(
                t_win["cutoff"], DEFAULT_THRESHOLD_MIN,
                msg=f"PD-5(a): el corte reportado es el umbral usado "
                    f"({DEFAULT_THRESHOLD_MIN} min, default declarado)")
            top_win = doc.get("window")
            self.assertIsInstance(
                top_win, dict, msg="PD-5(a): window top-level es objeto")
            for key in ("criterion", "start_ref", "end_ref", "cutoff"):
                self.assertIn(
                    key, top_win,
                    msg=f"PD-5(a): window top-level trae {key!r}")
            self.assertTrue(
                top_win["cutoff"] == DEFAULT_THRESHOLD_MIN,
                msg=f"PD-5(a): el corte top-level reporta el umbral usado "
                    f"({DEFAULT_THRESHOLD_MIN} min)")
        # (b) borde fijado: la ventana del tramo es 12,55 min, NO 12,40.
        with self.subTest(punto="b-ventana-tramo-12-55-no-12-40"):
            leaf = self.measure_leaf(measures, "segment_duration",
                                     "PD-5(b) [clave declarada]")
            self.assertEqual(
                str(leaf.get("bucket")), "observed",
                msg="PD-5(b): la duración del tramo se LEE de las marcas "
                    "de tiempo → observed")
            value = leaf.get("value")
            self.assertIsInstance(
                value, (int, float),
                msg=f"PD-5(b): segment_duration numérica (fue {value!r})")
            self.assertLessEqual(
                abs(value - M1_TRAMO_WINDOW_MIN), 0.051,
                msg=f"PD-5(b): la ventana del tramo es {M1_TRAMO_WINDOW_MIN}"
                    f" min (≈12,55; fue {value!r}) — borde FIJADO: el tramo "
                    "cierra en el mensaje `assistant` SIN llamada de "
                    "herramienta propia, seguido del `idle` succeeded")
            self.assertGreaterEqual(
                abs(value - M1_ALT_WINDOW_MIN), 0.05,
                msg=f"PD-5(b): el borde alternativo NO se usa — la ventana "
                    f"NO es {M1_ALT_WINDOW_MIN} min (borde en el último "
                    "mensaje CON llamada de herramienta)")
            _assert_unit_mentions(
                leaf, "PD-5(b)", ("min",))
        # (c) llamadas del tramo 101 vs sesión completa 121: separadas.
        with self.subTest(punto="c-tramo-101-vs-sesion-121"):
            tramo = self.measure_value(measures, "tool_calls",
                                       "PD-5(c) [clave declarada]")
            session_calls = self.measure_value(measures, "session_tool_calls",
                                               "PD-5(c) [clave declarada]")
            self.assertEqual(
                tramo, M1_TRAMO_CALLS,
                msg=f"PD-5(c): las llamadas del PRIMER TRAMO son "
                    f"{M1_TRAMO_CALLS} (fue {tramo!r}) — el corte en la "
                    f"brecha de ~{M1_GAP_MIN:.0f} min")
            self.assertEqual(
                session_calls, M1_SESSION_CALLS,
                msg=f"PD-5(c): la SESIÓN COMPLETA ({M1_SESSION_CALLS} "
                    f"llamadas, continuada tras la brecha) queda VISIBLE "
                    f"(fue {session_calls!r})")
            self.assertNotEqual(
                tramo, session_calls,
                msg="PD-5(c): tramo y sesión NUNCA se promedian — ambos "
                    "números separados y distintos (101 vs 121)")
        # (d) salidas del tramo: la MAYOR salida es 51.243 (pinneada por la
        #     spec PD-5/§6); el TOTAL es la suma de las salidas del tramo
        #     según el propio fixture (con consistencia total >= max; el
        #     total NO está pinneado por el contrato y NO es el máximo).
        #     La trampa de mezcla sigue: las llamadas post-gap suman
        #     (además del tramo) y su máximo es 61.000 > 51.243 — mezclar
        #     tramo/sesión ALTERNA total y máximo.
        with self.subTest(punto="d-salidas-tramo-total-suma-y-max"):
            total = self.measure_value(measures, "total_output", "PD-5(d)")
            max_out = self.measure_value(measures, "max_output", "PD-5(d)")
            self.assertEqual(
                max_out, M1_MAX_OUTPUT,
                msg=f"PD-5(d): max_output del TRAMO = {M1_MAX_OUTPUT} "
                    f"car. — la MAYOR salida individual (pinneada por la "
                    f"spec PD-5/§6; fue {max_out!r}); el máximo POST-gap "
                    f"({M1_POST_GAP_MAX}) no entra al tramo")
            self.assertEqual(
                total, M1_TRAMO_TOTAL_OUTPUT,
                msg=f"PD-5(d): total_output del TRAMO es la SUMA de las "
                    "salidas del tramo según el PROPIO fixture "
                    f"({M1_TRAMO_TOTAL_OUTPUT} car.; fue {total!r}) — el "
                    "total NO está pinneado por la spec y NO es la mayor "
                    f"salida ({M1_MAX_OUTPUT}); mezclar la sesión completa "
                    f"agregaría además {M1_POST_GAP_OUTPUTS} car. "
                    "de salidas post-gap al total")
            self.assertGreaterEqual(
                total, max_out,
                msg=f"PD-5(d): consistencia interna — total_output "
                    f"({total!r}) >= max_output ({max_out!r}) del tramo")
            for key, leaf in (("total_output",
                               self.measure_leaf(measures, "total_output",
                                                 "PD-5(d)")),
                              ("max_output",
                               self.measure_leaf(measures, "max_output",
                                                 "PD-5(d)"))):
                _assert_unit_mentions(
                    leaf, f"PD-5(d) {key}",
                    ("unicode", "car"),  # caracteres Unicode
                    forbidden=("token", "byte"))
        # (e) proxy del ÚLTIMO PASO = 203.276 (no 202.222): el último paso
        #     es el mensaje que CIERRA el tramo (sin herramienta propia). El
        #     detalle por paso exige la bandera declarada `--steps` (interfaz
        #     de la reapertura acotada): la corrida POR DEFECTO resume.
        with self.subTest(punto="e-proxy-ultimo-paso-203276"):
            steps_session = self.session_of(
                self.store_muestra1, "PD-5(e) --steps", "--steps")
            steps = self.measure_list(steps_session["measures"],
                                      "input_per_step", "PD-5(e)")
            self.assertEqual(
                len(steps), 102,
                msg="PD-5(e): el tramo porta 102 pasos (101 llamadas + "
                    f"el mensaje que cierra) — fueron {len(steps)}")
            self.assertEqual(
                steps[-1], M1_PROXY_LAST_STEP,
                msg=f"PD-5(e): el proxy del ÚLTIMO paso (el mensaje que "
                    f"cierra el tramo) es {M1_PROXY_LAST_STEP} tok "
                    "(input 1164 + cache.read 202112 + cache.write 0); "
                    f"fue {steps[-1]!r}")
            self.assertNotEqual(
                steps[-1], M1_ALT_PROXY_LAST_STEP,
                msg=f"PD-5(e): el borde alternativo NO se usa — el último "
                    "paso NO es el último mensaje CON herramienta "
                    f"({M1_ALT_PROXY_LAST_STEP} tok); ese valor es el paso "
                    "#101, visible como anterior:")
            self.assertEqual(
                steps[-2], M1_ALT_PROXY_LAST_STEP,
                msg="PD-5(e): el paso #101 (último CON herramienta) porta "
                    "el proxy del borde alternativo "
                    f"{M1_ALT_PROXY_LAST_STEP} (visible, NO usado)")

    def test_pd5_no_gap_single_segment_and_configurable_threshold(self):
        """PD-5: sin brecha mayor que el umbral la sesión completa es UN
        solo tramo; y el umbral es configurable: con --idle-threshold
        mayor que la brecha del fixture (~66,4 h), la brecha deja de cortar
        y el tramo pasa a ser la sesión completa (121 llamadas)."""
        # (a) SIN BRECHA: pausa de 5 min < umbral 60 → un tramo = la sesión.
        with self.subTest(punto="a-sin-brecha-un-tramo"):
            session = self.session_of(
                self.store_muestra1_nogap, "PD-5(a) sin brecha")
            measures = session["measures"]
            tramo = self.measure_value(measures, "tool_calls",
                                       "PD-5(a) [clave declarada]")
            session_calls = self.measure_value(
                measures, "session_tool_calls", "PD-5(a) [clave declarada]")
            self.assertEqual(
                tramo, M1_SESSION_CALLS,
                msg=f"PD-5(a): sin brecha > umbral, TODA la sesión es un "
                    f"tramo de {M1_SESSION_CALLS} llamadas (fue {tramo!r})")
            self.assertEqual(
                session_calls, tramo,
                msg="PD-5(a): con un solo tramo, las llamadas del tramo y "
                    "de la sesión completa COINCIDEN (121 == 121), sin "
                    "promediar")
            duration = self.measure_value(measures, "segment_duration",
                                          "PD-5(a)")
            self.assertIsInstance(
                duration, (int, float),
                msg=f"PD-5(a): segment_duration numérica (fue {duration!r})")
            self.assertLessEqual(
                abs(duration - M1_NOGAP_WINDOW_MIN), 0.051,
                msg=f"PD-5(a): la ventana del único tramo es la sesión "
                    f"completa: {M1_NOGAP_WINDOW_MIN} min (5 min de pausa "
                    f"< umbral; fue {duration!r})")
        # (b) umbral configurable: --idle-threshold 5000 min > brecha
        #     (3984 min) → la brecha deja de cortar; tramo = sesión.
        with self.subTest(punto="b-umbral-configurable"):
            session = self.session_of(
                self.store_muestra1, "PD-5(b) umbral",
                "--idle-threshold", str(M1_THRESHOLD_MIN))
            measures = session["measures"]
            self.assertEqual(
                session["window"]["cutoff"], M1_THRESHOLD_MIN,
                msg="PD-5(b): el corte reportado es el umbral pasado por "
                    f"flag ({M1_THRESHOLD_MIN} min), no el default")
            self.assertEqual(
                self.measure_value(measures, "tool_calls",
                                   "PD-5(b) [clave declarada]"),
                M1_SESSION_CALLS,
                msg=f"PD-5(b): con umbral {M1_THRESHOLD_MIN} > brecha "
                    f"({M1_GAP_MIN:.0f} min), el tramo pasa a ser la "
                    f"sesión completa ({M1_SESSION_CALLS} llamadas)")
            self.assertEqual(
                self.measure_value(measures, "session_tool_calls",
                                   "PD-5(b) [clave declarada]"),
                M1_SESSION_CALLS,
                msg="PD-5(b): tramo == sesión completa bajo el umbral "
                    "mayor (121 == 121), sin promediar")
            duration = self.measure_value(measures, "segment_duration",
                                          "PD-5(b)")
            self.assertIsInstance(
                duration, (int, float),
                msg=f"PD-5(b): segment_duration numérica (fue {duration!r})")
            self.assertLessEqual(
                abs(duration - M1_THRESHOLD_WINDOW_MIN), 0.051,
                msg=f"PD-5(b): la ventana del único tramo es toda la "
                    f"sesión: {M1_THRESHOLD_WINDOW_MIN} min "
                    f"(fue {duration!r})")

    # ------------------------------------------------------- PD-6

    def test_pd6_resume_and_dispatch_milestones_separate(self):
        """PD-6: dos hitos SEPARADOS — (a) sonda 2: primer `resume` real
        observado en la llamada #19 (el `resume --help` #10 NO cuenta y un
        `write` cuyo contenido menciona «resume» NO cuenta),
        time_relative presente, y first_dispatch ausente con causa;
        (b) muestra 1: sin `resume` real → first_resume ABSENT con causa
        (no se inventa un hito ni un cero) y first_dispatch es el primer
        despacho de trabajo de rol observado (subagent) — hitos separados;
        (c) S-BOOT-04: el primer despacho de trabajo de rol es la llamada a
        la herramienta `subagent` → first_dispatch observed con su
        posición, y el hito de resume queda independiente (absent).
        Con resume real → observed; sin resume real → absent (sesión
        nueva vs reanudada, expresada por el hito)."""
        # (a) sonda 2: resume real en #19; --help (#10) y write (#29) NO.
        with self.subTest(punto="a-sonda2-resume-19-help-y-write-excluidos"):
            session = self.session_of(self.store_sonda2, "PD-6(a)")
            mt = self.milestone(session["milestones"], "first_resume",
                                "PD-6(a)")
            self.assertEqual(
                mt.get("status"), "observed",
                msg=f"PD-6(a): el primer resume REAL se OBSERVA en la "
                    f"llamada #{S2_RESUME_INDEX} (fue "
                    f"{mt.get('status')!r})")
            position = mt.get("position")
            self.assertIsInstance(
                position, dict,
                msg="PD-6(a): el hito observado trae position")
            self.assertEqual(
                position.get("call_index"), S2_RESUME_INDEX,
                msg=f"PD-6(a): la posición del hito es la llamada "
                    f"#{S2_RESUME_INDEX} (contador de llamadas de "
                    f"herramienta; fue {position.get('call_index')!r}): el "
                    f"`resume --help` (#10) y la `write` cuyo contenido "
                    "menciona resume (#29) NO cuentan")
            self.assertEqual(
                position.get("seq"), S2_RESUME_SEQ,
                msg=f"PD-6(a): la posición porta el seq del mensaje que "
                    f"porta la llamada (fue {position.get('seq')!r})")
            time_rel = mt.get("time_relative")
            self.assertIsInstance(
                time_rel, (int, float),
                msg=f"PD-6(a): time_relative del hito es numérico en "
                    f"minutos (fue {time_rel!r})")
            self.assertLessEqual(
                abs(time_rel - S2_RESUME_TIME_MIN), 0.01,
                msg=f"PD-6(a): time_relative del hito es los minutos "
                    f"relativos al inicio del tramo ({S2_RESUME_TIME_MIN}; "
                    f"fue {time_rel!r})")
            leaf = self.measure_leaf(session["measures"],
                                     "time_to_first_resume", "PD-6(a)")
            self.assertEqual(
                str(leaf.get("bucket")), "observed",
                msg="PD-6(a): el tiempo hasta el hito observado es "
                    "observed (fue "
                    f"{leaf.get('bucket')!r})")
            _assert_number_in_minutes(
                leaf, "PD-6(a) time_to_first_resume", S2_RESUME_TIME_MIN)
            fd = self.milestone(session["milestones"], "first_dispatch",
                                "PD-6(a)")
            self.assertEqual(
                fd.get("status"), "absent",
                msg=f"PD-6(a): la sonda 2 NO despacha trabajo de rol "
                    f"(sin `{DISPATCH_TOOL}`) → first_dispatch absent "
                    f"(fue {fd.get('status')!r}); los hitos NUNCA se "
                    "confunden entre sí")
            self.assertTrue(
                isinstance(fd.get("cause"), str) and fd["cause"].strip(),
                msg=f"PD-6(a): el hito ausente trae causa (cause="
                    f"{fd.get('cause')!r})")
        # (b) muestra 1: sin resume → absent (no inventado); dispatch
        #     observado (subagent #1) y separado del resume.
        with self.subTest(punto="b-muestra1-resume-absent-dispatch-observado"):
            session = self.session_of(self.store_muestra1, "PD-6(b)")
            mt = self.milestone(session["milestones"], "first_resume",
                                "PD-6(b)")
            self.assertEqual(
                mt.get("status"), "absent",
                msg=f"PD-6(b): la muestra 1 NO invoca el subcomando resume → "
                    "status `absent` (no `unknown` dudoso y no inventado; "
                    f"fue {mt.get('status')!r})")
            self.assertTrue(
                isinstance(mt.get("cause"), str) and mt["cause"].strip(),
                msg=f"PD-6(b): el hito ausente trae causa (cause="
                    f"{mt.get('cause')!r})")
            leaf = self.measure_leaf(session["measures"],
                                     "time_to_first_resume", "PD-6(b)")
            self.assertIsNone(
                leaf.get("value"),
                msg=f"PD-6(b): sin hito, el tiempo NO se inventa y NO es 0 "
                    f"(value={leaf.get('value')!r}) — null + bucket "
                    "unknown; el hito se declara con su causa")
            self.assertEqual(
                str(leaf.get("bucket")), "unknown",
                msg="PD-6(b): sin hito, el tiempo queda en el cubo "
                    f"unknown (fue {leaf.get('bucket')!r})")
            fd = self.milestone(session["milestones"], "first_dispatch",
                                "PD-6(b)")
            self.assertEqual(
                fd.get("status"), "observed",
                msg=f"PD-6(b): el primer despacho de trabajo de rol es la "
                    f"llamada a `{DISPATCH_TOOL}` (llamada #1) → observed "
                    f"(fue {fd.get('status')!r}); los hitos NUNCA se "
                    "confunden: en la MUESTRA el dispatch es observado y "
                    "el resume está ausente")
            position = fd.get("position")
            self.assertIsInstance(
                position, dict,
                msg="PD-6(b): el despacho observado trae position")
            self.assertEqual(
                position.get("call_index"), 1,
                msg=f"PD-6(b): el despacho observado porta su posición "
                    f"(la llamada #1; fue {position!r})")
            fd_time = self.measure_leaf(
                session["measures"], "time_to_first_dispatch", "PD-6(b)")
            self.assertEqual(
                str(fd_time.get("bucket")), "observed",
                msg="PD-6(b): el despacho observado porta su tiempo "
                    "observed (fue "
                    f"{fd_time.get('bucket')!r})")
            _assert_number_in_minutes(
                fd_time, "PD-6(b) time_to_first_dispatch", 0.0)
        # (c) S-BOOT-04: despacho = subagent observado; resume independiente.
        with self.subTest(punto="c-sboot04-dispatch-subagent"):
            session = self.session_of(self.store_sboot04, "PD-6(c)")
            fd = self.milestone(session["milestones"], "first_dispatch",
                                "PD-6(c)")
            self.assertEqual(
                fd.get("status"), "observed",
                msg=f"PD-6(c): el primer despacho de trabajo de rol es la "
                    f"llamada a `{DISPATCH_TOOL}` → observed "
                    f"(fue {fd.get('status')!r})")
            position = fd.get("position")
            self.assertIsInstance(
                position, dict,
                msg="PD-6(c): el despacho observado trae position")
            self.assertEqual(
                position.get("call_index"), SB_DISPATCH_INDEX,
                msg=f"PD-6(c): la posición del despacho es la llamada "
                    f"#{SB_DISPATCH_INDEX} (fue {position!r})")
            self.assertEqual(
                position.get("seq"), SB_DISPATCH_SEQ,
                msg=f"PD-6(c): la posición porta el seq del mensaje "
                    f"(fue {position.get('seq')!r})")
            fd_time = fd.get("time_relative")
            self.assertIsInstance(
                fd_time, (int, float),
                msg=f"PD-6(c): time_relative del despacho es numérico en "
                    f"minutos (fue {fd_time!r})")
            self.assertLessEqual(
                abs(fd_time - SB_DISPATCH_TIME_MIN), 0.01,
                msg=f"PD-6(c): time_relative del despacho es los minutos "
                    f"({SB_DISPATCH_TIME_MIN}; fue {fd_time!r})")
            mt = self.milestone(session["milestones"], "first_resume",
                                "PD-6(c)")
            self.assertEqual(
                mt.get("status"), "absent",
                msg=f"PD-6(c): el resume queda INDEPENDIENTE del despacho "
                    f"(sin resume → absent, no confundido; fue "
                    f"{mt.get('status')!r})")
            self.assertTrue(
                isinstance(mt.get("cause"), str) and mt["cause"].strip(),
                msg=f"PD-6(c): el hito de resume ausente trae causa")
            status_pair = (
                fd.get("status"),
                self.milestone(session["milestones"], "first_resume",
                               "PD-6(c)").get("status"))
            self.assertNotEqual(
                status_pair[0], status_pair[1],
                msg="PD-6(c): los dos hitos NUNCA se confunden entre sí "
                    f"(statuses {status_pair!r})")

    # ------------------------------------------------------- PD-7

    def test_pd7_orientation_reads_closed_definition(self):
        """PD-7 (resuelve V1): definición cerrada de lecturas de orientación
        — sobre la sonda 2, la definición es «llamada read ANTES del primer
        resume real»: previous_reads = 8 y previous_calls = 18 con el
        desglose por herramienta (8 read + 2 glob + 8 shell) expuesto; el
        total de read de la SESIÓN = 9 (la novena, #24, es POSTERIOR al
        hito) aparece ETIQUETADO y SEPARADO del conteo previo al hito: los
        dos números existen, difieren y NUNCA se promedian ni colapsan."""
        session = self.session_of(self.store_sonda2, "PD-7")
        measures = session["measures"]
        prev_calls = self.measure_value(measures, "previous_calls", "PD-7")
        prev_reads = self.measure_value(measures, "previous_reads", "PD-7")
        self.assertEqual(
            prev_calls, S2_PREV_CALLS,
            msg=f"PD-7: las llamadas ANTES del hito (llamada "
                f"#{S2_RESUME_INDEX}) son las demás del tramo y "
                f"{S2_PREV_CALLS} (fue {prev_calls!r})")
        self.assertEqual(
            prev_reads, S2_PREV_READS,
            msg=f"PD-7 (definición cerrada V1): las lecturas de "
                f"orientación = llamadas `read` ANTES del primer resume "
                f"real: {S2_PREV_READS} (fue {prev_reads!r})")
        self.assertNotEqual(
            prev_calls, prev_reads,
            msg="PD-7: el total de llamadas previas y el conteo read NUNCA "
                "se colapsan en un mismo número: 18 vs 8")
        breakdown = self.measure_value(measures, "previous_calls_by_tool",
                                       "PD-7 [clave declarada]")
        self.assertIsInstance(
            breakdown, dict,
            msg=f"PD-7: el desglose por herramienta es objeto: {breakdown!r}")
        self.assertEqual(
            breakdown, S2_PREV_BY_TOOL,
            msg=f"PD-7: el desglose de las {S2_PREV_CALLS} previas expone "
                f"las herramientas (esperado {S2_PREV_BY_TOOL!r}; fue "
                f"{breakdown!r}) — glob y shell visibles, nada oculto")
        for tool, count in breakdown.items():
            self.assertIsInstance(
                count, (int, float),
                msg=f"PD-7: el conteo de {tool!r} en el desglose es "
                    f"numérico (fue {count!r})")
        self.assertEqual(
            sum(breakdown.values()), S2_PREV_CALLS,
            msg=f"PD-7: el desglose SOMA las {S2_PREV_CALLS} llamadas "
                "previas (sin promediar)")
        session_reads = self.measure_value(measures, "session_reads",
                                           "PD-7 [clave declarada]")
        self.assertEqual(
            session_reads, S2_SESSION_READS,
            msg=f"PD-7: el TOTAL de read de la sesión es "
                f"{S2_SESSION_READS} (la NOVENA es la #{S2_SESSION_READS}, "
                f"POSTERIOR al hito; fue {session_reads!r})")
        self.assertNotEqual(
            session_reads, prev_reads,
            msg="PD-7 (discrepancia 8 vs 9 visible): el total de la sesión "
                "y el conteo previo al hito difieren (9 vs 8) y AMBOS "
                "quedan etiquetados con claves distintas, nunca promediados")

    # ------------------------------------------------------- PD-8

    def test_pd8_measures_units_provenance_three_magnitudes(self):
        """PD-8: medidas de orientación y tres MAGNITUDES con unidad y
        procedencia — cada medida trae unit y provenance no vacíos y un
        bucket válido; las tres magnitudes quedan SEPARADAS: (i) el contexto
        cargado por paso es el proxy declarado (input + cache.read +
        cache.write) y su bucket es `estimated`, (ii) el procesamiento
        acumulado (suma de pasos) es `observed`, (iii) el costo es observed
        o unknown; NINGUNA métrica aparece en dos cubos; los tiempos están
        en minutos, los conteos en llamadas, las salidas en caracteres
        Unicode; con la muestra 1, el proxy del último paso = 203.276 y el
        acumulado y el costo aparecen separados de él."""
        session = self.session_of(self.store_muestra1, "PD-8")
        measures = session["measures"]
        leaves = dict(_measure_leaves(measures))
        # (a) cada medida trae unit y provenance no vacíos y bucket válido.
        with self.subTest(punto="a-cada-medida-con-unit-y-procedencia"):
            self.assertTrue(
                leaves, msg="PD-8(a): hay medidas con bucket declarado")
            for name, leaf in leaves.items():
                for field in MEASURE_FIELDS:
                    self.assertIn(
                        field, leaf,
                        msg=f"PD-8(a): la medida {name!r} trae {field!r}")
                unit = str(leaf.get("unit", "")).strip()
                provenance = str(leaf.get("provenance", "")).strip()
                self.assertTrue(
                    unit, msg=f"PD-8(a): la medida {name!r} trae unit no "
                              f"vacía (fue {unit!r})")
                self.assertTrue(
                    provenance,
                    msg=f"PD-8(a): la medida {name!r} trae provenance no "
                        f"vacía (fue {provenance!r})")
                self.assertIn(
                    leaf.get("bucket"), BUCKET_VALUES,
                    msg=f"PD-8(a): la medida {name!r} declara un cubo "
                        f"válido (fue {leaf.get('bucket')!r})")
        # (b) unidades: tiempos en minutos; conteos en llamadas; salidas en
        #     caracteres Unicode.
        with self.subTest(punto="b-unidades-minutos-llamadas-caracteres"):
            _assert_unit_mentions(
                self.measure_leaf(measures, "time_to_first_resume",
                                  "PD-8(b) minutos"), "PD-8(b)", ("min",))
            _assert_unit_mentions(
                self.measure_leaf(measures, "time_to_first_dispatch",
                                  "PD-8(b) minutos"),
                "PD-8(b) time_to_first_dispatch", ("min",))
            for key in ("previous_calls", "previous_reads", "tool_calls",
                        "session_tool_calls"):
                _assert_unit_mentions(
                    self.measure_leaf(measures, key,
                                      f"PD-8(b) {key} en llamadas"),
                    f"PD-8(b) {key}", ("call", "llamada"))
            for key in ("total_output", "max_output"):
                _assert_unit_mentions(
                    self.measure_leaf(measures, key,
                                      f"PD-8(b) {key} en caracteres"),
                    f"PD-8(b) {key}",
                    ("unicode", "car"), forbidden=("token", "byte"))
        # (i) CONTEXTO CARGADO POR PASO = proxy declarado → estimated.
        with self.subTest(punto="i-proxy-por-paso-estimated"):
            # el detalle por paso exige la bandera declarada `--steps`
            # (interfaz de la reapertura acotada): la corrida POR DEFECTO
            # resumen. Assertions sin cambios.
            steps_measures = self.session_of(
                self.store_muestra1, "PD-8(i) --steps",
                "--steps")["measures"]
            steps = self.measure_list(steps_measures, "input_per_step",
                                      "PD-8(i)")
            leaf = self.measure_leaf(steps_measures, "input_per_step",
                                     "PD-8(i)")
            self.assertEqual(
                str(leaf.get("bucket")), "estimated",
                msg="PD-8(i): el contexto cargado por paso es el PROXY "
                    "declarado (input + cache.read + cache.write del paso), "
                    "NO la ventana real → bucket estimated "
                    f"(fue {leaf.get('bucket')!r})")
            self.assertEqual(
                steps[-1], M1_PROXY_LAST_STEP,
                msg=f"PD-8(i): el proxy del último paso de la muestra 1 es "
                    f"{M1_PROXY_LAST_STEP} tok (input 1164 + cache.read "
                    f"202112 + cache.write 0; fue {steps[-1]!r})")
        # (ii) PROCESAMIENTO ACUMULADO (suma de pasos) → observed y
        #      SEPARADO del proxy del último paso.
        with self.subTest(punto="ii-acumulado-observed-separado"):
            leaf = self.measure_leaf(measures, "accumulated", "PD-8(ii)")
            self.assertEqual(
                str(leaf.get("bucket")), "observed",
                msg="PD-8(ii): el procesamiento acumulado (suma de pasos "
                    f"leída de los reportes) es observed "
                    f"(fue {leaf.get('bucket')!r})")
            value = leaf.get("value")
            self.assertEqual(
                value, M1_ACCUMULATED_INPUT,
                msg=f"PD-8(ii): el acumulado del tramo es la SUMA de los "
                    f"pasos: {M1_ACCUMULATED_INPUT} tok (suma de "
                    f"tokens.input de los 102 pasos: 100*100 + 1160 + "
                    f"1164; fue {value!r}) — separado del proxy de UN paso "
                    f"({M1_PROXY_LAST_STEP})")
            self.assertNotEqual(
                value, M1_PROXY_LAST_STEP,
                msg="PD-8(ii): el acumulado NO es el proxy del último paso "
                    "— las magnitudes quedan separadas")
        # (iii) COSTO: observed (con valores reportados) o unknown.
        with self.subTest(punto="iii-costo-separado"):
            cost_leaf = self.measure_leaf(measures, "cost", "PD-8(iii)")
            self.assertIn(
                str(cost_leaf.get("bucket")), ("observed", "unknown"),
                msg=f"PD-8(iii): el costo es observed o unknown "
                    f"(fue {cost_leaf.get('bucket')!r})")
            self.assertEqual(
                cost_leaf.get("value"), M1_COST,
                msg=f"PD-8(iii): el costo del tramo es la suma de los "
                    f"costos reportados por paso: {M1_COST} (el paso que "
                    "cierra porta 0.75; los otros 0.0; fue "
                    f"{cost_leaf.get('value')!r}) — separado del proxy y "
                    "del acumulado")
            self.assertNotEqual(
                cost_leaf.get("value"), M1_PROXY_LAST_STEP,
                msg="PD-8(iii): el costo NO se mezcla con los tokens")
        # (c) cubos: ninguna métrica en dos cubos; el cache.write NO
        #     reportado queda unknown (PD-4 en el fixture del adaptador).
        with self.subTest(punto="c-cubos-disjuntos-y-cache-write-unknown"):
            assignment: dict[str, set] = {}
            for name, leaf in leaves.items():
                assignment.setdefault(name, set()).add(leaf["bucket"])
            buckets = session["buckets"]
            self.assertIsInstance(buckets, dict,
                                  msg="PD-8(c): buckets es objeto")
            for bucket_name, members in buckets.items():
                if isinstance(members, list):
                    for member in members:
                        if isinstance(member, str):
                            assignment.setdefault(
                                member, set()).add(bucket_name)
            for name, placed in assignment.items():
                self.assertEqual(
                    len(placed), 1,
                    msg=f"PD-8(c)/INV-4: NINGUNA métrica aparece en dos "
                        f"cubos ({name!r} en {sorted(placed)})")
            write_leaf = self.measure_leaf(measures, "cache.write",
                                           "PD-8(c) cache.write")
            self.assertEqual(
                str(write_leaf.get("bucket")), "unknown",
                msg="PD-8(c): cache.write NO es un cero real si el "
                    f"proveedor no lo reporta → unknown "
                    f"(fue {write_leaf.get('bucket')!r})")
            read_leaf = self.measure_leaf(measures, "cache.read",
                                          "PD-8(c) cache.read")
            self.assertEqual(
                str(read_leaf.get("bucket")), "observed",
                msg="PD-8(c): cache.read sí está reportado → observed")
            # la sesión sin costo reportado (sonda 2): costo unknown.
            sonda = self.session_of(self.store_sonda2, "PD-8(c) sonda")
            sonda_cost = self.measure_leaf(sonda["measures"], "cost",
                                           "PD-8(c) sonda")
            self.assertEqual(
                str(sonda_cost.get("bucket")), "unknown",
                msg="PD-8(c): cost nulo/no reportado → unknown con causa, "
                    f"NUNCA 0 (fue {sonda_cost.get('bucket')!r})")


if __name__ == "__main__":
    unittest.main()
