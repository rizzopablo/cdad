#!/usr/bin/env python3
"""005-002 T4 — ACEPTACIÓN: reproducción de las muestras 1 y 2 sobre
fixtures fieles, determinismo/solo-lectura sobre los fixtures, integración
sobre la BASE REAL (omitida por defecto) y S-BOOT-04 opcional
(criterios §4; PD-14 declarado).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (§4 criterios de
  aceptación; §6 muestras y valores verificados; PD-5, PD-6, PD-7, PD-14,
  PD-11, PD-15 — la superficie ya cubierta por T1/T2 se re-aplica aquí solo
  como ORÁCULO de la reproducción, no se re-testea por stuffed).
- docs/specs/005-002-session-context-meter/plan.md (ficha T4 y su gate de
  integración: reproducción de las DOS muestras sobre la base real en solo
  lectura; S-BOOT-04 opcional por variable de entorno; fixtures del
  test-writer omitidos por defecto; GREEN es de T1/T2/T3 — aquí no hay
  producto nuevo).
- Forma del esquema de los fixtures: discovery.md §1.2–§1.6 (NO se repite;
  NO se cree la base real NUNCA aquí).

ORÁCULO: la SALIDA del WRAPPER fino `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable) — NUNCA importando el
módulo. El contrato observable es el JSON por stdout, el rc y el diagnóstico
por stderr. Sin aserciones sobre nombres internos de funciones/clases/
módulos; sin mocks sobre plumbing.

Fixtures 100% SINTÉTICOS, construidos por este test en un directorio
temporal con SQLite, contenido inventado; la base real del runtime JAMÁS se
abre en los tests de fixture y JAMÁS se copia. Las cantidades reproducen
EXACTAMENTE las cifras pinneadas de las muestras (spec §4 y §6):

- MUESTRA 1 (primera sesión de 005-001): primer tramo contiguo de 101
  llamadas (desglose fiel del real: 25 `read`, 72 `shell`, 1 `execute`,
  2 `edit`, 1 `write`), ventana 12,5471 min (12,55), distribución de
  salidas FIEL (100 de 101 llamadas con salida; la MAYOR salida del
  tramo 51.243 car. Unicode — eso es lo que pinea la spec PD-5/§6; el
  TOTAL del tramo NO está pinneado: es la suma de las salidas del
  propio fixture, calculada por el constructor), proxy del ÚLTIMO paso
  203.276 tok (input 1.164 + cache.read 202.112 + cache.write 0). El
  borde ALTERNATIVO (último mensaje CON llamada de herramienta →
  12,40 min / 202.222 tok) se hace VISIBLE y se declara NO USADO (PD-5).
  El tramo cierra en el
  mensaje `assistant` SIN llamada de herramienta propia, seguido del
  `idle` `succeeded` previo a la brecha (~66,4 h = 3.984 min > umbral
  default 60). La sesión completa tiene 121 llamadas y queda visible
  SEPARADA del tramo (sin promediar). Sin resume real → hito AUSENTE con
  causa (no inventado).
- SONDA 2 (003-007): 29 llamadas; primer resume REAL en la llamada #19
  (el `resume --help` de la #10 NO cuenta y la `write` cuyo contenido
  menciona «resume» NO cuenta); 18 llamadas antes: 8 `read` + 2 `glob`
  + 8 `shell` (desglose expuesto); el total de `read` de la SESIÓN es 9
  (la novena, #24, es POSTERIOR al hito) — ambos números etiquetados
  (PD-6/PD-7; discrepancia 8 vs 9 visible).
- S-BOOT-04 (opcional, por variable de entorno): primer despacho de
  trabajo de rol = la herramienta `subagent` (en la muestra real: tool-call
  #73 con 72 previas). El oráculo del despacho en el registro es su
  `position` (criterio §4 «PD-6 (entrada adicional opcional)»).

Determinismo y solo lectura sobre los FP fixtures (criterio PD-11): dos
corridas producen salida byte-idéntica y el store y sus -wal/-shm no
cambian (tamaño y mtime); no se crean archivos nuevos.

INTEGRACIÓN SOBRE LA BASE REAL — OMITIDA POR DEFECTO (criterio §4 PD-5/
PD-6/PD-7 vía gate T4): corre SOLO si existen las variables de entorno que
la habilitan; sin ellas el test se OMITE con un diagnóstico explícito que
nombra lo que falta y cómo habilitar (NO es un verde fabricado). Con las
variables, reproduce las DOS muestras sobre la base real en SOLO LECTURA
(acotado por --session del medidor) aplicando LAS MISMAS aserciones de las
cifras pinneadas. D11-3 (005-003, corrección de evidencia): sobre la base
VIVA se comprueba SOLO la lectura y sus resultados (rc/documento); NO se
exige que la base quede inmóvil — la aserción previa de `(tamaño, mtime)`
era inestable con otro proceso escribiendo (debt.md D11). La ausencia de
escrituras se verifica sobre una base temporal CONTROLADA, en el focal de
T3 (`tests/test_005_003_t3_set_summary.py`), y la concurrencia con un
escritor controlado en el mismo focal; la base real JAMÁS se abre en modo
escritura (ni para demostrar que está prohibido).

VARIABLES DE ENTORNO (sin identificadores reales DENTRO de este archivo):
- `CDAD_CONTEXT_METER_REAL_STORE` — ruta del store real de sesiones del
  runtime (SQLite). NO se abre directo por el test: el medidor la abre por
  el flag `--store` de la superficie declarada (PD-15).
- `CDAD_005_002_M1_SESSION_ID` — identificador real de la MUESTRA 1 (la
  primera sesión de 005-001: 101 llamadas / 12,55 min / mayor salida
  51.243 car. / proxy del último paso 203.276 tok). El TOTAL de salida
  del tramo NO está pinneado por el contrato; sobre la base real se
  afirma SOLO la consistencia total >= max_output.
- `CDAD_005_002_S2_SESSION_ID` — identificador real de la SONDA 2 (la
  sesión de 003-007: primer resume real = llamada #19; 18 previas =
  8 read + 2 glob + 8 shell; 9 read en toda la sesión).
- `CDAD_005_002_SBOOT04_SESSION_ID` — (opcional) identificador real de la
  sesión S-BOOT-04 (primer despacho de trabajo de rol: herramienta
  `subagent`, tool-call #73 con 72 previas). Usa el mismo store.
Para habilitar la integración: exportar las tres primeras variables
(ruta del store + los dos identificadores) y correr este archivo.

PD-14 — sesión de cierre de 005-001 (V6): su criterio y su resolución se
verifican en el CIERRE y en la REVIEW (prosa del reference/context-meter.md;
spec §4 criterio PD-14). El contrato NO da un oráculo observable en la
salida del registro para ese punto (el medidor no declara sesiones por
histórico de feature en su contrato): NO se convierte en un test de unidad
ni vacío — declarado aquí como punto cubierto por review/cierre.

RED honesto: ficha T4 — «RED: sin la base/variable la prueba de integración
se omite; los fixtures aún no reproducen los valores; GREEN es de T1/T2/T3
(aquí no hay producto nuevo)». Los tests de fixture de este archivo son la
reproducción de ACEPTACIÓN de las cifras pinneadas y sirven como guardas de
aceptación del contrato; si el GREEN acumulado de T1/T2/T3 ya las satisface
el RED NO se fabrica (precedente honesto T3). Las corridas reales
(integración y S-BOOT-04) se omiten por defecto y NO cuentan como fallas.
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
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"  # fuga del entorno del host
CLI_TIMEOUT_S = 120        # fixtures chicos
REAL_CLI_TIMEOUT_S = 600   # base real (acotada por --session) — holgado

REAL_STORE_ENV = "CDAD_CONTEXT_METER_REAL_STORE"
M1_SESSION_ENV = "CDAD_005_002_M1_SESSION_ID"
S2_SESSION_ENV = "CDAD_005_002_S2_SESSION_ID"
SB_SESSION_ENV = "CDAD_005_002_SBOOT04_SESSION_ID"

DEFAULT_THRESHOLD_MIN = 60  # umbral default declarado (PD-15/§2)
MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")

# ----------------------------------------------------- cifras pinneadas
# (spec §4 y §6; identicas a las de la ficha T4 del paquete)

# --- MUESTRA 1 (PD-5, §4 criterio 1) ---
M1_TRAMO_WINDOW_MIN = 12.5471     # 12,55 min (espec): ventana del tramo
M1_ALT_WINDOW_MIN = 12.40         # borde alternativo: NO usado
M1_TRAMO_CALLS = 101              # llamadas del primer tramo contiguo
M1_SESSION_CALLS = 121            # toda la extensión (101 + 20 post-gap)
# Salidas del tramo: la spec pinea SOLO la MAYOR salida individual
# (51.243 car., PD-5/§6). El TOTAL NO está pinneado por el contrato: se
# deriva del PROPIO fixture con la distribución FIEL (100 de 101 llamadas
# con salida; la mayor 51.243 y las demás tamaños INVENTADOS menores →
# total claramente mayor que el máximo). Sobre la BASE REAL el total se
# afirma SOLO como consistencia interna (total >= max_output), jamás
# pineado a una medición real.
M1_MAX_OUTPUT = 51_243            # car. Unicode: MAYOR salida individual


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
M1_PROXY_LAST_STEP = 203_276      # último paso: 1164 + 202112 (+w 0)
M1_ALT_PROXY_LAST_STEP = 202_222  # proxy del paso #101 (borde NO usado)
M1_GAP_MIN = 3_984.0              # ~66,4 h entre el tramo 1 y la continuaci
M1_STEP_MS = 7_440                # cadencia sintética: ventana exacta
M1_TOTAL_MS = 752_826             # t0 → cierre del tramo = 12,5471 min
M1_ALT_TOTAL_MS = 744_000         # 12,40 min (última llamada con herramienta)
M1_NOGAP_PAUSE_MS = 300_000       # 5 min < umbral → sin brecha
M1_POST_GAP_STEP_MS = 30_000
M1_POST_GAP_MAX = 61_000          # trampa de mezcla (mayor que 51.243)
# ventana sin brecha: tramo único = sesión completa (752826 + 300000 +
# 20*30000 ms = 1.652.826 ms); derivada del PROPIO fixture
M1_NOGAP_WINDOW_MIN = (M1_TOTAL_MS + M1_NOGAP_PAUSE_MS
                       + 20 * M1_POST_GAP_STEP_MS) / 60_000
# desglose FIEL del tramo real (spec §6); declarado por el fixture:
M1_TRAMO_BY_TOOL = {"read": 25, "shell": 72, "execute": 1,
                    "edit": 2, "write": 1}

# --- SONDA 2 (PD-6/PD-7, §4 criterio 2) ---
S2_SESSION_CALLS = 29             # 8 read + 2 glob + 8 shell + #19 + 10 más
S2_RESUME_INDEX = 19              # primer resume REAL (llamada #19)
S2_RESUME_SEQ = 20                # seq del mensaje que porta la #19
S2_PREV_CALLS = 18                # llamadas antes del hito
S2_PREV_READS = 8                 # read antes del hito (PD-7)
S2_SESSION_READS = 9              # total read de la sesión (#24 posterior)
S2_PREV_BY_TOOL = {"read": 8, "glob": 2, "shell": 8}
S2_STEP_MS = 30_000

# --- S-BOOT-04 (opcional; criterio §4 «PD-6 entrada adicional») ---
SB_DISPATCH_CALL_INDEX = 73       # tool-call #73 del despacho (72 previas)

# --- identificadores/texto 100% SINTÉTICOS (inventados) ---
ROLE_SYNTH = "cdad-orchestrator"
MODEL_SYNTH = '{"id":"model-alpha","providerID":"prov-a"}'
CONTINUITY_CLI_STEM = "python3 skills/cdad-cycle/scripts/cdad_continuity.py"
RESUME_HELP_CMD = CONTINUITY_CLI_STEM + " resume --help"      # NO cuenta
RESUME_REAL_CMD = CONTINUITY_CLI_STEM + " resume --project-root ."

BASE_MS = 1_760_000_000_000  # epoch ms SINTÉTICO fijo (determinismo)

# ------------------------------------------------------------- fixtures

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


def _user_data(ms: int, text: str) -> str:
    """Forma `user` (discovery §1.3): {time, text}."""
    return json.dumps({"time": ms, "text": text}, sort_keys=True)


def _idle_data(ms: int, outcome: str) -> str:
    """Forma `idle` (discovery §1.3): {time, outcome}."""
    return json.dumps({"time": ms, "outcome": outcome}, sort_keys=True)


def _tool_part(name: str, text: str, ms: int, *, input_args: dict,
               part_id: str) -> dict:
    """Parte `tool` (discovery §1.4): state.content = [{type:text,text}] →
    el tamaño de salida = suma de len(text)."""
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


def _assistant_data(agent: str, model: str, ms: int, parts: list,
                    tokens: tuple, cost: float | None) -> str:
    """Forma `assistant` (discovery §1.3). En TODOS los fixtures
    time_created == time_updated por mensaje (sin ambigüedad de brecha)."""
    tin, tout, treason, tread, twrite = tokens
    return json.dumps({
        "time": {"created": ms, "streamed": ms, "completed": ms},
        "agent": agent, "model": model, "content": parts,
        "tokens": {"input": tin, "output": tout, "reasoning": treason,
                   "cache": {"read": tread, "write": twrite}},
        "cost": cost,
    }, sort_keys=True)


def _insert_msg(conn: sqlite3.Connection, sid: str, seq: int, mtype: str,
                data: str, ms: int) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, mtype, seq, ms, ms, data))


def _insert_session(conn: sqlite3.Connection, sid: str, agent: str,
                    model: str, t0: int, t_end: int, sums: tuple,
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


def _build_store(path: Path, populate) -> None:
    """Store SQLite sintético con el ESQUEMA observado (discovery §1.2–§1.6);
    escritura atómica tmp + os.replace (cierre limpio sin -wal/-shm
    remanentes, para el check de solo-lectura)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + ".tmp")
    try:
        tmp.unlink()
    except OSError:
        pass
    conn = sqlite3.connect(str(tmp))
    try:
        conn.execute(SESSION_V2_DDL)
        conn.execute(SESSION_MESSAGE_DDL)
        populate(conn)
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp, path)


def _m1_tool_args(name: str, i: int, *, mention_resume: bool = False) -> dict:
    """Argumentos sintéticos NEUTRALES por herramienta (ninguno activa un
    hito; `mention_resume` solo se usa en la sonda 2 para el caso negativo
    de PD-6: la write cuyo CONTENIDO menciona «resume» NO es un hito)."""
    if name == "shell":
        return {"command": "echo fixture-step"}
    if name == "read":
        return {"path": "/fixture/dir/f%d.md" % i}
    if name == "glob":
        return {"pattern": "fixture-*"}
    if name == "execute":
        return {"command": "true"}
    if name == "edit":
        return {"path": "/fixture/dir/f%d.md" % i}
    if name == "write":
        content = ("notas del ciclo sinteticas" +
                   (" con la palabra resume en texto libre"
                    if mention_resume else ""))
        return {"path": "/fixture/dir/notes-%d.md" % i, "content": content}
    return {"path": "/fixture/dir/x%d.md" % i}


def _build_muestra1(path: Path, *, with_gap: bool = True) -> None:
    """MUESTRA 1 sintética FIEL (spec §4/§6): desglose del tramo real sin
    despacho (25 read + 72 shell + 1 execute + 2 edit + 1 write = 101);
    un solo `user` inicial; el tramo cierra en el mensaje `assistant` SIN
    llamada de herramienta propia (proxy 203.276) seguido del `idle`
    `succeeded`; brecha ~66,4 h (o pausa de 5 min en la variante sin
    brecha); luego la sesión continúa con 20 llamadas más (→ 121) con
    salidas distintas (max 61.000) para que mezclar tramo/sesión SEA
    visible. El paso #101 (última llamada CON herramienta) porta el proxy
    del borde alternativo NO usado (202.222). Distribución de salidas del
    tramo FIEL al recorrido (100 de 101 llamadas con salida; la mayor
    51.243 y las demás menores): `_m1_tramo_output_size`; el total es la
    suma de esas salidas."""
    sid = "sess-fixture-acceptance-m1"

    def populate(conn: sqlite3.Connection) -> None:
        tool_names = sum(([tool] * count for tool, count
                          in M1_TRAMO_BY_TOOL.items()), [])
        assert len(tool_names) == M1_TRAMO_CALLS, len(tool_names)
        sum_in = sum_out = sum_reason = sum_cread = 0
        t0 = BASE_MS + 10_000_000_000
        _insert_msg(conn, sid, 1, "user",
                    _user_data(t0, "arranque de la sesion sintetica"), t0)
        for i, name in enumerate(tool_names, start=1):
            seq = 1 + i                        # llamadas en seq 2..102
            ms = t0 + (i - 1) * M1_STEP_MS     # #101 en t0 + 744.000 ms
            if i == M1_TRAMO_CALLS:            # borde alternativo NO usado
                tin, tread = 1_160, 201_062
            else:
                tin, tread = 100, 100
            tout, treason = 40, 5
            text = "o" * _m1_tramo_output_size(i)  # distribución fiel
            sum_in += tin; sum_out += tout; sum_reason += treason
            sum_cread += tread
            data = _assistant_data(
                ROLE_SYNTH, MODEL_SYNTH, ms,
                [_tool_part(name, text, ms, input_args=_m1_tool_args(
                    name, i), part_id=f"p{seq}")],
                (tin, tout, treason, tread, 0), 0.0)
            _insert_msg(conn, sid, seq, "assistant", data, ms)
        # Mensaje `assistant` que CIERRA el tramo: SIN llamada propia;
        # proxy 1164 + 202112 + 0 = 203.276; ventana usada: t0 → aquí.
        close_ms = t0 + M1_TOTAL_MS
        assert close_ms > t0 + M1_ALT_TOTAL_MS
        _insert_msg(conn, sid, 103, "assistant",
                    _assistant_data(ROLE_SYNTH, MODEL_SYNTH, close_ms,
                                    [{"type": "text",
                                      "text": "cierre del tramo"}],
                                    (1164, 500, 0, 202_112, 0), 0.75),
                    close_ms)
        sum_in += 1164; sum_out += 500; sum_cread += 202_112
        # Cierre observable: `idle` con outcome succeeded (mismo instante).
        _insert_msg(conn, sid, 104, "idle",
                    _idle_data(close_ms, "succeeded"), close_ms)
        # Brecha ~66,4 h (> umbral 60) o pausa de 5 min (< umbral).
        gap_ms = (round(M1_GAP_MIN * 60_000) if with_gap
                  else M1_NOGAP_PAUSE_MS)
        t_gap_end = close_ms + gap_ms
        _insert_msg(conn, sid, 105, "user",
                    _user_data(t_gap_end, "continua la sesion"), t_gap_end)
        for i in range(1, 21):                 # 20 llamadas post-gap
            seq = 105 + i
            ms = t_gap_end + i * M1_POST_GAP_STEP_MS
            if i % 2 == 1:
                name, args = "read", {"path": "/fixture/dir/g%d.md" % i}
            elif i == M1_SESSION_CALLS - M1_TRAMO_CALLS - 1:  # la última
                name, args = "write", {"path": "/fixture/dir/notes-x.md",
                                       "content": "notas post brecha"}
            else:
                name, args = "shell", {"command": "echo mas"}
            tin, tread, tout, treason = 97, 93, 30, 5
            text = "q" * 100
            if i == 20:                        # max post-gap exacto
                text = "z" * M1_POST_GAP_MAX
            sum_in += tin; sum_out += tout; sum_reason += treason
            sum_cread += tread
            data = _assistant_data(
                ROLE_SYNTH, MODEL_SYNTH, ms,
                [_tool_part(name, text, ms, input_args=args,
                            part_id=f"p{seq}")],
                (tin, tout, treason, tread, 0), None)
            _insert_msg(conn, sid, seq, "assistant", data, ms)
        total_ms = t_gap_end + 20 * M1_POST_GAP_STEP_MS
        _insert_session(conn, sid, ROLE_SYNTH, MODEL_SYNTH, t0, total_ms,
                        (sum_in, sum_out, sum_reason, sum_cread, 0), 0.75)

    _build_store(path, populate)


def _build_sonda2(path: Path) -> None:
    """SONDA 2 sintética (spec §4/§6, PD-6/PD-7): 29 llamadas; el resume
    REAL es la #19 (shell con el subcomando `resume`, sin ayuda); el
    `resume --help` (#10) NO cuenta; 18 previas = 8 read + 2 glob +
    8 shell; la NOVENA read de la sesión es la #24 (posterior al hito); la
    `write` #29 cuyo CONTENIDO menciona «resume» NO cuenta como hito."""
    sid = "sess-fixture-acceptance-s2"

    def populate(conn: sqlite3.Connection) -> None:
        tools = (["read"] * 8                      # #1..#8
                 + ["glob"]                        # #9
                 + ["shell"]                       # #10: resume --help
                 + ["glob"]                        # #11
                 + ["shell"] * 7                   # #12..#18
                 + ["shell"]                       # #19: resume REAL
                 + ["shell"] * 4                   # #20..#23
                 + ["read"]                        # #24: NOVENA read
                 + ["shell"] * 4                   # #25..#28
                 + ["write"])                      # #29: menciona resume
        assert len(tools) == S2_SESSION_CALLS, len(tools)
        sum_in = sum_out = sum_reason = sum_cread = 0
        t0 = BASE_MS + 20_000_000_000
        _insert_msg(conn, sid, 1, "user",
                    _user_data(t0, "arranque de la sonda"), t0)
        for i, name in enumerate(tools, start=1):
            ms = t0 + i * S2_STEP_MS
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
            else:
                args = _m1_tool_args(name, i, mention_resume=True)
            tin, tread = 90, 80
            sum_in += tin; sum_out += 30; sum_reason += 5; sum_cread += tread
            data = _assistant_data(
                ROLE_SYNTH, MODEL_SYNTH, ms,
                [_tool_part(name, "o" * 30, ms, input_args=args,
                            part_id=f"p{seq}")],
                (tin, 30, 5, tread, 0), None)
            _insert_msg(conn, sid, seq, "assistant", data, ms)
        total_ms = t0 + len(tools) * S2_STEP_MS
        _insert_session(conn, sid, ROLE_SYNTH, MODEL_SYNTH, t0, total_ms,
                        (sum_in, sum_out, sum_reason, sum_cread, 0), None)

    _build_store(path, populate)


# ---------------------------------------------------------------- helpers

def _snapshot_store_siblings(store: Path) -> dict:
    """Snapshot del store y sus -wal/-shm: nombre de archivo → (tamaño,
    mtime_ns). Sin leer contenido (solo stat); el dict NO cambia si no
    aparecen/desaparecen/alteran archivos junto al store."""
    snap: dict = {}
    for name in (store.name, store.name + "-wal", store.name + "-shm"):
        p = store.parent / name
        if p.exists() and p.is_file():
            st = p.stat()
            snap[name] = (st.st_size, st.st_mtime_ns)
    return snap


def _measure_leaf(measures: dict, key: str, ctx: str) -> dict:
    """Hoja de medida {value, unit, provenance, bucket}: las claves
    declaradas del contrato viven al nivel superior de `measures`
    (convención T1/T2)."""
    leaf = measures.get(key)
    if not isinstance(leaf, dict):
        raise AssertionError(
            f"{ctx}: la medida {key!r} NO existe en la salida (hojas: "
            f"{sorted(k for k in measures if isinstance(measures[k], dict))}"
            ") — RED/aceptación de contrato")
    for field in MEASURE_FIELDS:
        if field not in leaf:
            raise AssertionError(
                f"{ctx}: la medida {key!r} trae {field!r} declarado "
                f"(fue {leaf!r})")
    return leaf


def _measure_value(session: dict, key: str, ctx: str):
    return _measure_leaf(session["measures"], key, ctx)["value"]


def _milestone(session: dict, key: str, ctx: str) -> dict:
    milestones = session.get("milestones")
    if not isinstance(milestones, dict) or key not in milestones:
        raise AssertionError(
            f"{ctx}: milestones trae la clave presente {key!r} "
            f"(fue {milestones!r}) — contrato PD-16")
    return milestones[key]


def _assert_number(off: unittest.TestCase, value: object, expected: float,
                   ctx: str, msg: str, delta: float = 0.051) -> None:
    off.assertIsInstance(
        value, (int, float),
        msg=f"{ctx}: valor numérico esperado {expected!r} (fue {value!r}); "
            f"{msg}")
    off.assertLessEqual(
        abs(value - expected), delta,
        msg=f"{ctx}: valor esperado {expected!r}, con tolerancia ±{delta} "
            f"(fue {value!r}); {msg}")


# ---- aserciones de las cifras pinneadas: usadas TAMBIÉN sobre la base
# real por la prueba de integración (misma aserción, mismos números).

def _assert_muestra1_pinned(off: unittest.TestCase, session: dict,
                            ctx: str, *,
                            expected_total_output: int | None = None,
                            steps_session: dict | None = None) -> None:
    """MUESTRA 1 (criterio §4 PD-5): ventana del tramo 12,55 min (NO
    12,40), 101 llamadas (NO 121: la sesión completa queda visible y
    separada), MÁXIMA salida 51.243 car. (la mayor salida individual:
    eso es lo que pinea la spec PD-5/§6), proxy del último paso 203.276
    tok (NO 202.222); sin resume real → hito ausente con causa.

    `steps_session`: la corrida CON la bandera declarada `--steps`
    (interfaz de la reapertura acotada). El detalle por paso exige la
    bandera (la corrida POR DEFECTO porta el resumen de tamaño fijo,
    PD-12/D2); sus assertions de proxy se leen de esa corrida.

    El TOTAL de salida del tramo NO está pinneado por el contrato:
    - sobre un FIXTURE fiel (expected_total_output dado): se afirma
      IGUAL a la suma de las salidas calculada por el propio constructor
      del fixture (no un número copiado);
    - sobre la BASE REAL (expected_total_output=None): se afirma SOLO la
      consistencia interna total_output >= max_output, JAMÁS pineado a
      una medición real."""
    measures = session["measures"]
    # (a) ventana del tramo: 12,55 min; el borde alternativo NO se usa.
    leaf = _measure_leaf(measures, "segment_duration", ctx)
    value = leaf["value"]
    _assert_number(
        off, value, M1_TRAMO_WINDOW_MIN, ctx + " (a) ventana del tramo",
        "la ventana del PRIMER TRAMO es 12,55 min (borde paidado: cierra "
        "en el mensaje assistant SIN llamada de herramienta propia, "
        "seguido del idle succeeded); el borde alternativo da 12,40")
    off.assertGreaterEqual(
        abs(value - M1_ALT_WINDOW_MIN), 0.05,
        msg=f"{ctx}: el borde alternativo NO se usa — la ventana NO es "
            f"{M1_ALT_WINDOW_MIN} min (último mensaje CON herramienta); "
            "criterio PD-5")
    # (b) llamadas del tramo 101 y de la sesión 121: separadas y visibles.
    tramo = _measure_value(session, "tool_calls", ctx)
    session_calls = _measure_value(session, "session_tool_calls", ctx)
    off.assertEqual(
        tramo, M1_TRAMO_CALLS,
        msg=f"{ctx}: (b) las llamadas del PRIMER TRAMO son "
            f"{M1_TRAMO_CALLS} con el corte en la brecha de "
            f"~{M1_GAP_MIN:.0f} min (fue {tramo!r})")
    off.assertEqual(
        session_calls, M1_SESSION_CALLS,
        msg=f"{ctx}: (b) la SESIÓN COMPLETA ({M1_SESSION_CALLS} llamadas, "
            "continuada tras la brecha) queda VISIBLE y separada del tramo "
            f"(fue {session_calls!r}) — sin promediar")
    # (c) salidas del tramo: la MAYOR salida es 51.243 (pinneada por la
    #     spec PD-5/§6). El TOTAL del tramo NO está pinneado por el
    #     contrato: se afirma como consistencia interna (total >= max) y,
    #     sobre un FIXTURE fiel, igual a la suma calculada por el propio
    #     fixture. Post-gap NO mezclado: su max es 61.000 > 51.243.
    max_out = _measure_value(session, "max_output", ctx)
    off.assertEqual(
        max_out, M1_MAX_OUTPUT,
        msg=f"{ctx}: (c) max_output del TRAMO = {M1_MAX_OUTPUT} car. — "
            "la MAYOR salida individual (pinneada por la spec PD-5/§6; "
            f"fue {max_out!r}); el max post-gap ({M1_POST_GAP_MAX}) NO "
            "entra al tramo")
    total_out = _measure_value(session, "total_output", ctx)
    off.assertIsInstance(
        total_out, (int, float),
        msg=f"{ctx}: (c) total_output del tramo es numérico (fue "
            f"{total_out!r})")
    if expected_total_output is not None:
        off.assertEqual(
            total_out, expected_total_output,
            msg=f"{ctx}: (c) total_output del TRAMO es la SUMA de las "
                "salidas del tramo según el PROPIO fixture "
                f"({expected_total_output} car.; fue {total_out!r}) — "
                "el total NO está pinneado por la spec y NO es la mayor "
                f"salida ({M1_MAX_OUTPUT})")
    off.assertGreaterEqual(
        total_out, max_out,
        msg=f"{ctx}: (c) consistencia interna — el total de las salidas "
            f"({total_out!r}) es >= la mayor salida individual "
            f"({max_out!r}) del tramo; sobre la base real el total NO "
            "se pinea (medicina: solo lo que el contrato pinnea)")
    # (d) proxy del ÚLTIMO paso = 203.276 (no 202.222): el último paso es
    #     el mensaje que CIERRA el tramo (sin herramienta propia). El detalle
    #     por paso exige la bandera declarada `--steps` (interfaz de la
    #     reapertura acotada: la corrida POR DEFECTO porta el resumen de
    #     tamaño fijo) — el detalle se lee de la corrida CON `--steps`.
    steps_measures = (steps_session or session)["measures"]
    steps_leaf = _measure_leaf(steps_measures, "input_per_step", ctx)
    steps = steps_leaf["value"]
    off.assertIsInstance(
        steps, list,
        msg=f"{ctx}: (d) con `--steps` input_per_step porta su lista de "
            f"pasos (fue {type(steps).__name__})")
    # Consistencia (D3): la spec pinea las 101 LLAMADAS de herramienta del
    # tramo, NO la cantidad de pasos `assistant`. El conteo exacto del
    # fixture fiel (101 llamadas + el assistant que cierra) queda como SONDA
    # DECLARADA; el assert de contrato es pasos >= llamadas.
    steps_probe = len(steps)
    off.assertGreaterEqual(
        steps_probe, M1_TRAMO_CALLS,
        msg=f"{ctx}: (d) los pasos del tramo ({steps_probe}) son >= las "
            f"llamadas de herramienta pinneadas ({M1_TRAMO_CALLS}) "
            "[sonda declarada del fixture: 102 = 101 llamadas + el mensaje "
            "que cierra; el contrato NO pinea la cantidad de pasos]")
    off.assertEqual(
        steps[-1], M1_PROXY_LAST_STEP,
        msg=f"{ctx}: (d) el proxy del ÚLTIMO paso es {M1_PROXY_LAST_STEP} "
            "tok (input 1164 + cache.read 202112 + cache.write 0); "
            f"fue {steps[-1]!r}")
    off.assertNotEqual(
        steps[-1], M1_ALT_PROXY_LAST_STEP,
        msg=f"{ctx}: el borde alternativo NO se usa — el último paso NO es "
            f"el último mensaje CON herramienta ({M1_ALT_PROXY_LAST_STEP} "
            "tok)")
    off.assertEqual(
        steps[-2], M1_ALT_PROXY_LAST_STEP,
        msg=f"{ctx}: el paso #{M1_TRAMO_CALLS} (último CON herramienta) "
            "porta el proxy del borde alternativo "
            f"{M1_ALT_PROXY_LAST_STEP} — VISIBLE y NO usado")
    # (e) sin resume real → hito AUSENTE con causa; no inventado, no 0.
    mt = _milestone(session, "first_resume", ctx)
    off.assertEqual(
        mt.get("status"), "absent",
        msg=f"{ctx}: (e) sin resume real, first_resume es `absent` "
            f"(no inventado; fue {mt.get('status')!r}) — PD-6")
    off.assertTrue(
        isinstance(mt.get("cause"), str) and mt["cause"].strip(),
        msg=f"{ctx}: (e) el hito ausente trae causa (fue "
            f"{mt.get('cause')!r})")
    rt_leaf = _measure_leaf(measures, "time_to_first_resume", ctx)
    off.assertIsNone(
        rt_leaf["value"],
        msg=f"{ctx}: (e) sin hito el tiempo NO se inventa y NO es 0 "
            f"(value={rt_leaf['value']!r}) — null en el cubo unknown")
    off.assertEqual(
        rt_leaf["bucket"], "unknown",
        msg=f"{ctx}: (e) sin hito, el tiempo queda en el cubo unknown "
            f"(fue {rt_leaf['bucket']!r})")


def _assert_sonda2_pinned(off: unittest.TestCase, session: dict,
                          ctx: str, *, check_seq: bool) -> None:
    """SONDA 2 (criterio §4 PD-6/PD-7): primer resume real = llamada #19
    (el `resume --help` #10 y la `write` con «resume» NO cuentan); 18
    llamadas antes con desglose 8 read + 2 glob + 8 shell; el total de
    read de la SESIÓN es 9 (la #24 posterior): ambos números etiquetados."""
    measures = session["measures"]
    # (a) hito observado en la posición pinned.
    mt = _milestone(session, "first_resume", ctx)
    off.assertEqual(
        mt.get("status"), "observed",
        msg=f"{ctx}: (a) el primer resume REAL se OBSERVA en la llamada "
            f"#{S2_RESUME_INDEX} (fue {mt.get('status')!r}); la llamada "
            "`resume --help` (#10) y la `write` cuyo contenido menciona "
            "«resume» NO cuentan — PD-6")
    position = mt.get("position")
    off.assertIsInstance(
        position, dict, msg=f"{ctx}: (a) el hito observado trae position")
    off.assertEqual(
        position.get("call_index"), S2_RESUME_INDEX,
        msg=f"{ctx}: (a) la posición del hito es la llamada "
            f"#{S2_RESUME_INDEX} (fue {position.get('call_index')!r})")
    if check_seq:
        off.assertEqual(
            position.get("seq"), S2_RESUME_SEQ,
            msg=f"{ctx}: (a) la posición porta el seq del mensaje que "
                f"porta la #{S2_RESUME_INDEX} (fue "
                f"{position.get('seq')!r})")
    time_rel = mt.get("time_relative")
    off.assertIsInstance(
        time_rel, (int, float),
        msg=f"{ctx}: (a) time_relative del hito es numérico en minutos "
            f"(fue {time_rel!r})")
    # (b) previas al hito: 18 con desglose 8 read + 2 glob + 8 shell.
    prev_calls = _measure_value(session, "previous_calls", ctx)
    prev_reads = _measure_value(session, "previous_reads", ctx)
    off.assertEqual(
        prev_calls, S2_PREV_CALLS,
        msg=f"{ctx}: (b) las llamadas ANTES del hito son "
            f"{S2_PREV_CALLS} (fue {prev_calls!r})")
    off.assertEqual(
        prev_reads, S2_PREV_READS,
        msg=f"{ctx}: (b) definición cerrada V1: las lecturas de "
            "orientación = llamadas `read` ANTES del primer resume real: "
            f"{S2_PREV_READS} (fue {prev_reads!r}) — PD-7")
    off.assertNotEqual(
        prev_calls, prev_reads,
        msg=f"{ctx}: el total de previas y el conteo read NUNCA se "
            f"colapsan ({S2_PREV_CALLS} vs {S2_PREV_READS}) — PD-7")
    breakdown = _measure_value(session, "previous_calls_by_tool", ctx)
    off.assertIsInstance(
        breakdown, dict,
        msg=f"{ctx}: (b) el desglose por herramienta es un objeto "
            f"(fue {breakdown!r})")
    off.assertEqual(
        breakdown, S2_PREV_BY_TOOL,
        msg=f"{ctx}: (b) el desglose de las {S2_PREV_CALLS} previas expone "
            f"las herramientas (esperado {S2_PREV_BY_TOOL!r}; fue "
            f"{breakdown!r}) — glob y shell visibles, nada oculto")
    off.assertEqual(
        sum(breakdown.values()), S2_PREV_CALLS,
        msg=f"{ctx}: el desglose SUMA las {S2_PREV_CALLS} "
            "previas (sin promediar)")
    # (c) total de read de la sesión: 9 (la #24 posterior al hito).
    session_reads = _measure_value(session, "session_reads", ctx)
    off.assertEqual(
        session_reads, S2_SESSION_READS,
        msg=f"{ctx}: (c) el TOTAL de read de la SESIÓN es "
            f"{S2_SESSION_READS} (la novena es POSTERIOR al hito; fue "
            f"{session_reads!r}) — PD-7")
    off.assertNotEqual(
        session_reads, prev_reads,
        msg=f"{ctx}: discrepancia 8 vs 9 visible: el total de la sesión y "
            "el conteo previo al hito difieren y AMBOS quedan etiquetados "
            "con claves distintas (nunca promediados)")


# ---------------------------------------------------------------- tests


class AcceptanceT4Test(unittest.TestCase):
    """T4 de 005-002: un test por criterio de aceptación (§4), contra la
    salida del wrapper. Los tests de integración real se OMITEN por
    defecto (unittest.skipTest con diagnóstico explícito)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t4-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_m1 = base / "muestra1" / "sessions.db"
        self.store_m1_nogap = base / "muestra1-nogap" / "sessions.db"
        self.store_s2 = base / "sonda2" / "sessions.db"
        _build_muestra1(self.store_m1, with_gap=True)
        _build_muestra1(self.store_m1_nogap, with_gap=False)
        _build_sonda2(self.store_s2)

    # -- corrida del wrapper (SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str, timeout_s: int = CLI_TIMEOUT_S
                  ) -> subprocess.CompletedProcess:
        if not METER_WRAPPER.is_file():
            self.fail(
                f"{FEATURE_ID}: el medidor `{METER_WRAPPER.name}` no existe "
                "aún — RED por CLI ausente (comportamiento ausente), "
                "nunca por ImportError: el test NO importa el módulo")
        cmd = [sys.executable, str(METER_WRAPPER), *argv]
        env = os.environ.copy()
        env.pop(STORE_ENV_VAR, None)      # sin fuga del entorno del host
        env.pop(REAL_STORE_ENV, None)     # ídem: la ruta SIEMPRE por flag
        try:
            return subprocess.run(
                cmd, cwd=REPO_ROOT, env=env, capture_output=True,
                timeout=timeout_s, stdin=subprocess.DEVNULL)
        except FileNotFoundError:
            self.fail(
                f"{FEATURE_ID}: el medidor `{METER_WRAPPER.name}` no "
                "ejecuta aún (comportamiento ausente); el test NO importa "
                "el módulo del medidor")
        except subprocess.TimeoutExpired as exc:
            self.fail(
                f"{FEATURE_ID}: el medidor no terminó dentro de "
                f"{timeout_s}s; timeout={exc!r}")

    def run_over_fixture(self, store: Path, label: str,
                         *extra: str) -> dict:
        proc = self.run_meter("--store", str(store), *extra)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición {label}: rc=0 sobre el fixture; "
                f"stdout={proc.stdout[:300]!r} stderr={proc.stderr[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        run = doc.get("run", {})
        self.assertEqual(
            run.get("schema"), "recognized",
            msg=f"precondición {label}: el fixture replica el esquema "
                "observado y debe reconocerse (si saliera `unknown`, el "
                "RED no sería del contrato sino de rejilla equivocada)")
        self.assertEqual(
            len(doc.get("sessions", [])), 1,
            msg=f"{label}: el fixture tiene UNA sesión")
        return doc["sessions"][0]

    def run_real_single(self, store: Path, session_id: str,
                        label: str, *extra: str) -> dict:
        """Corrida REAL en solo lectura y ACOTADA (criterio T4): el store
        llega POR FLAG (--store) y la selección POR --session (nada de
        barridos sin límite)."""
        proc = self.run_meter(
            "--store", str(store), "--session", str(session_id), *extra,
            timeout_s=REAL_CLI_TIMEOUT_S)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: la corrida real acotada por --session debe "
                f"salir bien (rc=0); stderr={proc.stderr[:300]!r}")
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        self.assertEqual(
            doc.get("run", {}).get("schema"), "recognized",
            msg=f"{label}: el esquema real se reconoce")
        self.assertEqual(
            len(doc.get("sessions", [])), 1,
            msg=f"{label}: con UN --session la salida mide UNA sesión "
                "(acotamiento observable)")
        return doc["sessions"][0]

    # --------------------------------------------------- §4 PD-5 (C3)

    def test_c1_muestra1_borde_fijado_y_valores_pinneados(self):
        """Criterio §4 PD-5 (fixture fiel): la MUESTRA 1 reproduce 12,55
        min / 101 llamadas / MÁXIMA salida 51.243 car. (la mayor salida,
        pinneada; el TOTAL del tramo es la suma de las salidas del propio
        fixture, no lo pinea la spec) / 203.276 tok (proxy del último
        paso); el borde alternativo (12,40 min / 202.222 tok) queda
        visible y NO usado; la sesión completa (121 llamadas) es visible
        y separada del tramo; sin resume real → ausente con causa.
        Además: sin brecha > umbral, TODA la sesión es un solo tramo
        (variante del criterio PD-5)."""
        # (a) la reproducción pinneada sobre el fixture fiel (cifras de las
        #     aserción comparte la MISMA función que la base real; aquí el
        #     total esperado lo calcula el PROPIO fixture).
        with self.subTest(punto="a-reproduccion-pinneada"):
            session = self.run_over_fixture(self.store_m1, "PD-5 (a)")
            steps_session = self.run_over_fixture(
                self.store_m1, "PD-5 (a) --steps", "--steps")
            _assert_muestra1_pinned(
                self, session, "PD-5 (a) fixture",
                expected_total_output=M1_TRAMO_TOTAL_OUTPUT,
                steps_session=steps_session)
        # (b) sin brecha > umbral: la sesión completa es UN solo tramo
        #     (criterio PD-5: «si no hay brecha, toda la sesión es un solo
        #     tramo») — el mismo fixture sin la brecha larga.
        with self.subTest(punto="b-sin-brecha-un-tramo"):
            session = self.run_over_fixture(
                self.store_m1_nogap, "PD-5 (b) sin brecha")
            tramo = _measure_value(session, "tool_calls",
                                   "PD-5 (b) [clave declarada]")
            session_calls = _measure_value(session, "session_tool_calls",
                                           "PD-5 (b) [clave declarada]")
            self.assertEqual(
                tramo, M1_SESSION_CALLS,
                msg=f"PD-5 (b): sin brecha > umbral, TODA la sesión es un "
                    f"tramo de {M1_SESSION_CALLS} llamadas (fue {tramo!r})")
            self.assertEqual(
                session_calls, tramo,
                msg="PD-5 (b): con un solo tramo, las llamadas del tramo y "
                    "de la sesión completa COINCIDEN, sin promediar")
            leaf = _measure_leaf(session["measures"], "segment_duration",
                                 "PD-5 (b)")
            _assert_number(
                self, leaf["value"], M1_NOGAP_WINDOW_MIN,
                "PD-5 (b) ventana sin brecha",
                "la ventana del único tramo es TODA la sesión (pausa de "
                "5 min < umbral)")

    # --------------------------------------------- §4 PD-6 / PD-7

    def test_c2_sonda2_primer_resume_y_previas(self):
        """Criterio §4 PD-6/PD-7 (fixture fiel): la SONDA 2 reproduce el
        primer resume REAL en la llamada #19 (el `resume --help` #10 y la
        `write` cuyo contenido menciona «resume» NO cuentan); 18 llamadas
        antes (8 `read` + 2 `glob` + 8 `shell` con desglose expuesto);
        total de `read` de la sesión = 9 (la #24 posterior al hito)."""
        session = self.run_over_fixture(self.store_s2, "PD-6/PD-7")
        _assert_sonda2_pinned(self, session, "PD-6/PD-7 fixture",
                              check_seq=True)

    # ------------------------------------------------- §4 PD-11 (C3)

    def test_c3_determinismo_y_solo_lectura_sobre_fixtures(self):
        """Criterio §4 PD-11 (fixture): dos ranuras sobre el MISMO fixture
        de aceptación producen salida byte-idéntica; el store y sus
        -wal/-shm no cambian (tamaño y mtime) y no se crean archivos
        nuevos; la apertura real queda acotada por --session/--store."""
        for label, store in (("muestra1", self.store_m1),
                             ("sonda2", self.store_s2)):
            with self.subTest(fixture=label):
                before = _snapshot_store_siblings(store)
                out1 = self.run_meter("--store", str(store),
                                      timeout_s=CLI_TIMEOUT_S).stdout
                self.run_meter("--store", str(store),
                               timeout_s=CLI_TIMEOUT_S)
                out2 = self.run_meter("--store", str(store),
                                      timeout_s=CLI_TIMEOUT_S).stdout
                self.assertEqual(
                    out1, out2,
                    msg=f"PD-11 ({label}): dos corridas sobre el mismo "
                        "fixture producen salida byte-idéntica "
                        "(determinismo)")
                after = _snapshot_store_siblings(store)
                self.assertEqual(
                    before, after,
                    msg=f"PD-11 ({label}): abrir el store NO cambia el "
                        "tamaño ni el mtime del store ni de sus "
                        f"-wal/-shm y NO crea archivos nuevos; "
                        f"antes={before} después={after}")

    # --------------------------- §4 PD-5/PD-6/PD-7 (gate T4): BASE REAL

    def test_c4_integracion_base_real_omitted_by_default(self):
        """Gate T4 (criterio §4 PD-5 + PD-6/PD-7) sobre la BASE REAL en
        SOLO LECTURA y ACOTADA — OMITIDA POR DEFECTO: corre SOLO con las
        variables CDAD_CONTEXT_METER_REAL_STORE + CDAD_005_002_M1_SESSION_ID
        + CDAD_005_002_S2_SESSION_ID. Sin ellas: skipTest con diagnóstico
        explícito (NO un verde fabricado). Con ellas: LAS MISMAS aserciones
        de las cifras pinneadas sobre las DOS muestras reales — SOLO lo
        que el contrato pinea (ventana 12,55 min, 101 llamadas del tramo,
        121 de la sesión, MÁXIMA salida 51.243, proxy del último paso
        203.276, primer resume de la sonda 2 y su desglose) MÁS la
        consistencia interna total_output >= max_output; el TOTAL de
        salida del tramo NO se pinea a un valor de la base real (sería
        copiar una medición real al contrato y la spec no lo pinea). D11-3
        (005-003): sobre la base VIVA se comprueba SOLO la lectura y sus
        resultados (rc/documento) — NO se exige que el store quede inmóvil
        (la aserción previa de `(tamaño, mtime)` era inestable con otro
        proceso escribiendo); la ausencia de escrituras se verifica sobre
        una base temporal CONTROLADA en el focal de T3."""
        required = (REAL_STORE_ENV, M1_SESSION_ENV, S2_SESSION_ENV)
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            self.skipTest(
                "INTEGRACIÓN REAL OMITIDA por falta de variables de "
                "entorno: " + ", ".join(missing) + ". Semántica: "
                f"{REAL_STORE_ENV} = ruta del store real de sesiones del "
                "runtime (SQLite, se abre SOLO por el medidor con el flag "
                "--store en modo read-only); "
                f"{M1_SESSION_ENV} = id real de la MUESTRA 1 (primera "
                "sesión de 005-001); "
                f"{S2_SESSION_ENV} = id real de la SONDA 2 (sesión de "
                "003-007). Habilitación: export los tres valores y correr "
                "python3 -m pytest tests/test_005_002_t4_acceptance.py -q "
                "-k c4. Ningún verde fabricado: los tests de "
                "fixture (test_c1/test_c2/test_c3) NO dependen de estas "
                "variables.")
        store = Path(os.environ[REAL_STORE_ENV]).expanduser().resolve()
        self.assertTrue(
            store.is_file(),
            msg=f"{REAL_STORE_ENV}={store!r} no es un archivo existente")
        m1_id = os.environ[M1_SESSION_ENV]
        s2_id = os.environ[S2_SESSION_ENV]
        # D11-3: NO se toma snapshot del store real — sobre la base viva se
        # comprueba SOLO la lectura y sus resultados (rc/documento), nunca que
        # la base quede inmóvil (la aserción de (tamaño, mtime) era inestable
        # con otro proceso escribiendo; debt.md D11).
        # (a) MUESTRA 1 real: mismas aserciones pinneadas.
        with self.subTest(muestra="1"):
            session = self.run_real_single(
                store, m1_id, "base real muestra 1")
            steps_session = self.run_real_single(
                store, m1_id, "base real muestra 1 --steps", "--steps")
            _assert_muestra1_pinned(
                self, session, "base real muestra 1",
                steps_session=steps_session)
        # (b) SONDA 2 real: mismas aserciones pinneadas.
        with self.subTest(muestra="2"):
            session = self.run_real_single(
                store, s2_id, "base real sonda 2")
            _assert_sonda2_pinned(self, session, "base real sonda 2",
                                  check_seq=False)
        # D11-3: NO se afirma que el store quede inmóvil — la corrección
        # reemplaza la aserción de (tamaño, mtime) de la base viva por SOLO la
        # lectura y sus resultados (ya asertados arriba por run_real_single y
        # las cifras pinneadas). La ausencia de escrituras se verifica sobre una
        # base temporal CONTROLADA en el focal de T3.

    # ------------------------- §4 PD-6 (entrada opcional): S-BOOT-04 REAL

    def test_c5_sboot04_primer_despacho_por_entorno(self):
        """Criterio §4 «PD-6 (entrada adicional opcional)» — S-BOOT-04:
        el primer despacho de trabajo de rol se verifica con la
        herramienta `subagent` sobre la MUESTRA REAL; la entrada es
        OPCIONAL y corre SOLO si están las variables del store y el id de
        la sesión; sin ellas se OMITE con diagnóstico."""
        required = (REAL_STORE_ENV, SB_SESSION_ENV)
        missing = [name for name in required if not os.environ.get(name)]
        if missing:
            self.skipTest(
                "S-BOOT-04 (opcional) OMITIDO por falta de variables de "
                "entorno: " + ", ".join(missing) + ". Semántica: "
                f"{REAL_STORE_ENV} = ruta del store real de sesiones; "
                f"{SB_SESSION_ENV} = id real de la sesión S-BOOT-04 "
                "(la muestra del PRIMER DESPACHO de trabajo de rol). "
                "Habilitación: export ambos valores y correr este test. "
                "Sin la entrada opcional el criterio §4 PD-6 principal ya "
                "está cubierto por test_c1 (resume ausente) y "
                "test_c2 (resume observado).")
        store = Path(os.environ[REAL_STORE_ENV]).expanduser().resolve()
        self.assertTrue(
            store.is_file(),
            msg=f"{REAL_STORE_ENV}={store!r} no es un archivo existente")
        sb_id = os.environ[SB_SESSION_ENV]
        # D11-3: sin snapshot del store real (sobre la base viva solo se
        # comprueban la lectura y sus resultados; nunca que quede inmóvil).
        session = self.run_real_single(store, sb_id, "base real S-BOOT-04")
        # El primer despacho de trabajo de rol = la llamada a `subagent`.
        fd = _milestone(session, "first_dispatch", "S-BOOT-04 real")
        self.assertEqual(
            fd.get("status"), "observed",
            msg="S-BOOT-04 real: el primer despacho de trabajo de rol se "
                f"OBSERVA (fue {fd.get('status')!r}) — criterio §4 PD-6 "
                "(opción)")
        position = fd.get("position")
        self.assertIsInstance(
            position, dict,
            msg="S-BOOT-04 real: el despacho observado trae position")
        self.assertEqual(
            position.get("call_index"), SB_DISPATCH_CALL_INDEX,
            msg=f"S-BOOT-04 real: el despacho es la tool-call "
                f"#{SB_DISPATCH_CALL_INDEX} (las "
                f"{SB_DISPATCH_CALL_INDEX - 1} previas no son despachos; "
                f"fue {position.get('call_index')!r})")
        time_rel = fd.get("time_relative")
        self.assertIsInstance(
            time_rel, (int, float),
            msg=f"S-BOOT-04 real: time_relative del despacho es numérico "
                f"en minutos (fue {time_rel!r})")
        # D11-3: NO se afirma que el store real quede inmóvil — sobre la base
        # viva se comprueba SOLO la lectura y sus resultados (ya asertados
        # arriba por run_real_single y el hito observado).


if __name__ == "__main__":
    unittest.main()
