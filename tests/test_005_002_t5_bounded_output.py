#!/usr/bin/env python3
"""005-002 T5b (REAPERTURA ACOTADA, unidad 2 de 2) — SALIDA ACOTADA A ESCALA
(D2) y confinamiento del oráculo de aceptación (D3).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (PD-8 `input_per_step`;
  PD-12 «salida lo bastante chica»: la salida POR DEFECTO es compacta,
  acotada y con referencias, suficiente para que 005-003 consulte la evidencia
  original SIN inyectar toda la sesión; PD-3/PD-4/PD-6/PD-15 e INV-4: un valor
  no observable es null/`unknown`, NUNCA `0`).
- docs/specs/005-002-session-context-meter/debt.md (D2 y D3: condiciones de
  cierre de esta unidad).
- docs/epics/epic-005-real-operation/execution.md (criterio de review vigente
  que motiva la reapertura acotada).
- El contrato APROBADO no cambia (PD-3, PD-4, PD-6, PD-12, PD-15): esta
  unidad hace CUMPLIR lo ya publicado (el reference declara como normativo un
  límite de 16384 bytes por documento de sesión) y confina el oráculo de
  aceptación a lo que la spec pinea.

ORÁCULO: la SALIDA del WRAPPER fino `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable) — NUNCA importando el
módulo. El test-writer NO lee la implementación; el contrato observable es el
JSON por stdout, el rc y el diagnóstico por stderr.

Fixtures 100% SINTÉTICOS, construidos por este test en un directorio
temporal con SQLite, contenido inventado (`sess-fixture-*`, modelo
`model-alpha`, provider `prov-a`). La base real del runtime JAMÁS se abre ni
se copia (PD-10/INV-7).

INTERFAZ DECLARADA POR ESTE TEST (el implementer la satisface leyendo el test;
el orquestador la fija en este paquete porque el test-writer no ve el código):

1. BANDERA EXPLÍCITA NUEVA `--steps` (booleana, sin valor). CON `--steps` la
   medida `input_per_step` porta su lista ORDENADA completa de proxys por paso
   (un elemento por paso del tramo; `null` para el paso cuyo proxy no es
   observable) y el límite de bytes NO aplica.
2. POR DEFECTO (sin `--steps`) `input_per_step.value` es un RESUMEN DE TAMAÑO
   FIJO: objeto con las claves `count` (cantidad de pasos del tramo), `last`
   (proxy del ÚLTIMO paso), `previous` (proxy del PENÚLTIMO paso), `min` y
   `max` (sobre los proxys observables) y `unobserved` (cantidad de pasos cuyo
   proxy no es observable). Un valor no observable es `null`, NUNCA `0`;
   `min`/`max` son `null` si no hay ningún proxy observable.
3. INDICADOR DE TRUNCACIÓN Y SU CAUSA, declarado en la hoja de la medida: la
   clave `truncated` es un objeto con `truncated` (bool), `cause` (texto que
   declara POR QUÉ se omite el detalle y que el detalle se obtiene con
   `--steps`, citando el límite publicado de 16384 bytes por documento de
   sesión), `omitted_steps` (cuántos pasos no se detallan) y `detail_flag` (el
   nombre de la bandera: `"--steps"`). Por defecto `truncated=true` y
   `omitted_steps = count`; con `--steps`, `truncated=false` y
   `omitted_steps=0`.
4. EL LÍMITE SE CUMPLE CON CUALQUIER TAMAÑO DE SESIÓN: el documento POR
   DEFECTO de UNA sesión mide 16384 bytes o menos sea cual sea la cantidad de
   pasos del tramo (fixture sintético grande, 1000 y 4000 pasos). El resumen
   es de tamaño FIJO: el tamaño del documento no crece con la cantidad de
   pasos (comparación 1000 vs 4000 con una diferencia ACOTADA).
5. El resumen sigue portando lo que el contrato pinea: `last` y `previous`
   del tramo de 102 pasos del fixture de la muestra 1 (203.276 y 202.222)
   siguen siendo legibles en el documento POR DEFECTO.

RED HOY (se declara MIXTO porque el test declara una bandera nueva), probado
con el wrapper SIN leer la implementación:
- (a) las aserciones del modo POR DEFECTO fallan por AssertionError de
  CONTRATO: hoy el documento del fixture grande supera los 16384 bytes, y no
  existen el resumen de tamaño fijo ni el indicador de truncado;
- (b) las aserciones del modo `--steps` y los tests alineados de t2/t4 fallan
  porque la bandera declarada TODAVÍA NO EXISTE (el wrapper devuelve rc=2 por
  argumento desconocido). Es el estado RED de una INTERFAZ DECLARADA por el
  test y NO cuenta como falla de comportamiento.
Ninguna aserción falla por ImportError/sintaxis/setup: el test NO importa el
módulo del medidor.
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
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"  # sin fuga del entorno del host
CLI_TIMEOUT_S = 120
BIG_CLI_TIMEOUT_S = 300     # el fixture grande (4000 pasos) es más lento

MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")

# --- interfaz declarada por este test (puntos 1-4 del paquete) ---
DETAIL_FLAG = "--steps"                  # el nombre de la bandera (punto 1)
BYTE_LIMIT = 16_384                      # límite publicado POR DOCUMENTO de
                                         # UNA sesión (punto 4; PD-12)
SUMMARY_KEYS = ("count", "last", "previous", "min", "max", "unobserved")
TRUNCATED_KEYS = ("truncated", "cause", "omitted_steps", "detail_flag")

# margen ACOTADO de crecimiento del tamaño default entre dos tamaños de
# sesión: el resumen es de forma FIJA (seis escalares), de modo que el único
# crecimiento legítimo observado entre 1000 y 4000 pasos es el ancho en
# dígitos de los contadores y del resto del registro (constante). El DEFECTO
# D2, en cambio, emite el detalle por paso (~6-8 bytes por paso): 3000 pasos
# extra sumarían ≳18.000 bytes, dos órdenes de magnitud por encima de este
# margen. 512 bytes es < 4% del límite de 16.384 y NO admite crecimiento
# proporcional a los pasos.
SIZE_GROWTH_MARGIN_BYTES = 512
BIG_STEPS_SMALL = 1_000                  # fixture grande chico (1000-5000)
BIG_STEPS_LARGE = 4_000                  # fixture grande grande (1000-5000)

# --- cifras pinneadas de la MUESTRA 1 (spec §4/§6; PD-5/PD-8) ---
EDGE_TOOL_CALLS = 101                    # llamadas de herramienta del tramo
EDGE_STEPS = 102                         # 101 llamadas + el assistant que
                                         # cierra el tramo (sonda del fixture)
EDGE_PROXY_DEFAULT = 200                 # input 100 + cache.read 100 + w 0
EDGE_PROXY_LAST_CALL = 202_222           # paso #101 (borde alternativo)
EDGE_PROXY_CLOSING = 203_276             # último paso (1164 + 202112 + w 0)

# --- proxies por paso de los fixtures sintéticos pequeños ---
PARTIAL_STEPS = 3
PARTIAL_PROXY_FIRST = 150                # 100 + 50 + 0 (tres componentes)
PARTIAL_PROXY_LAST = 15                  # 10 + 5 + 0
PARTIAL_UNOBSERVED = 1                   # un paso sin cache.write → proxy null
NONE_STEPS = 2                           # ningún proxy observable
NONE_UNOBSERVED = 2

# --- dispositivos sintéticos (inventados; nada de la base real) ---
ROLE = "cdad-orchestrator"
MODEL = '{"id":"model-alpha","providerID":"prov-a"}'

EDGE_SESSION = "sess-fixture-bounded-m1"
PARTIAL_SESSION = "sess-fixture-bounded-partial"
NONE_SESSION = "sess-fixture-bounded-none"
BIG_SMALL_SESSION = "sess-fixture-bounded-1000"
BIG_LARGE_SESSION = "sess-fixture-bounded-4000"

BASE_MS = 1_760_000_000_000              # epoch ms SINTÉTICO (determinismo)
STEP_MS = 30_000                         # 30 s < umbral default 60 min → un
                                         # solo tramo = la sesión entera

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

def _user_data(ms: int) -> str:
    return json.dumps({"time": ms, "text": "fixture prompt sintetico"},
                      sort_keys=True)


def _tool_part(name: str, text: str, ms: int, *, args: dict,
               part_id: str) -> dict:
    """Parte `tool` (discovery §1.4): state.content = [{type:text,text}] →
    tamaño de salida = suma de len(text)."""
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": {"status": "completed", "input": args,
                  "content": [{"type": "text", "text": text}]},
        "time": {"created": ms, "ran": ms, "completed": ms},
    }


def _tokens_full(tin: int, tout: int, tread: int, twrite: int = 0) -> dict:
    """Tokens con los TRES componentes reportados; `twrite=0` REPORTADO
    cuenta como reportado → el proxy del paso es la suma."""
    return {"input": tin, "output": tout, "reasoning": 0,
            "cache": {"read": tread, "write": twrite}}


def _tokens_missing_write(tin: int, tout: int, tread: int) -> dict:
    """Tokens a los que les FALTA `cache.write` → proxy no observable."""
    return {"input": tin, "output": tout, "reasoning": 0,
            "cache": {"read": tread}}


def _assistant_data(ms: int, parts: list, tokens: dict,
                    cost: float | None) -> str:
    """Forma `assistant` (discovery §1.3). En TODOS los fixtures
    time_created == time_updated por mensaje (sin ambigüedad de brecha)."""
    return json.dumps({
        "time": {"created": ms, "streamed": ms, "completed": ms},
        "agent": ROLE, "model": MODEL, "content": parts,
        "tokens": tokens, "cost": cost,
    }, sort_keys=True)


def _insert_msg(conn: sqlite3.Connection, sid: str, seq: int, mtype: str,
                data: str, ms: int) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:05d}-{sid}", sid, mtype, seq, ms, ms, data))


def _insert_session(conn: sqlite3.Connection, sid: str, t0: int, t_end: int,
                    sums: tuple, cost: float | None) -> None:
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


def _build_edge(path: Path) -> None:
    """MUESTRA 1 sintética (102 pasos, sin brecha): 101 pasos con llamada de
    herramienta (proxy default 200; el #101 porta el borde alternativo
    202.222) + el mensaje `assistant` que CIERRA el tramo SIN llamada propia
    (proxy 203.276). El proxy del PENÚLTIMO paso es 202.222 y el del ÚLTIMO
    203.276: las dos cifras que pinea el contrato (PD-5/PD-8)."""
    conn = _new_store(path)
    t0 = BASE_MS + 10_000_000
    _insert_msg(conn, EDGE_SESSION, 1, "user", _user_data(t0), t0)
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i in range(1, EDGE_TOOL_CALLS + 1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        if i == EDGE_TOOL_CALLS:
            tin, tread = 1_160, 201_062      # proxy 202.222 (borde alternativo)
        else:
            tin, tread = 100, 100            # proxy 200
        sum_in += tin
        sum_cread += tread
        sum_out += 40
        sum_reason += 5
        _insert_msg(conn, EDGE_SESSION, seq, "assistant",
                    _assistant_data(
                        ms,
                        [_tool_part("read", "r" * 8, ms,
                                    args={"path": "/fixture/dir/f%d" % i},
                                    part_id=f"p{seq}")],
                        _tokens_full(tin, 40, tread), 0.0),
                    ms)
    close_ms = t0 + (EDGE_TOOL_CALLS + 1) * STEP_MS
    _insert_msg(conn, EDGE_SESSION, EDGE_TOOL_CALLS + 2, "assistant",
                _assistant_data(
                    close_ms,
                    [{"type": "text", "text": "cierre del tramo"}],
                    _tokens_full(1_164, 500, 202_112), 0.75),
                close_ms)
    sum_in += 1_164
    sum_cread += 202_112
    sum_out += 500
    _insert_session(conn, EDGE_SESSION, t0, close_ms,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), 0.75)
    conn.commit()
    conn.close()


def _build_partial(path: Path) -> None:
    """3 pasos: el #1 con los TRES componentes (proxy 150), el #2 sin
    `cache.write` (proxy NO observable) y el #3 con los tres (proxy 15) →
    `unobserved=1`; el proxy del penúltimo paso es `null`, NUNCA 0."""
    conn = _new_store(path)
    t0 = BASE_MS + 20_000_000
    _insert_msg(conn, PARTIAL_SESSION, 1, "user", _user_data(t0), t0)
    tokens = [_tokens_full(100, 10, 50),
              _tokens_missing_write(70, 5, 40),
              _tokens_full(10, 5, 5)]
    for i, tk in enumerate(tokens, start=1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        _insert_msg(conn, PARTIAL_SESSION, seq, "assistant",
                    _assistant_data(
                        ms,
                        [_tool_part("read", "r" * 8, ms,
                                    args={"path": "/fixture/dir/p%d" % i},
                                    part_id=f"p{seq}")],
                        tk, None),
                    ms)
    _insert_session(conn, PARTIAL_SESSION, t0, t0 + 3 * STEP_MS,
                    (180, 20, 0, 95, 0), None)
    conn.commit()
    conn.close()


def _build_none_observable(path: Path) -> None:
    """2 pasos, AMBOS sin `cache.write` → ningún proxy observable:
    `min`/`max`/`last`/`previous` deben ser `null`, NUNCA `0`."""
    conn = _new_store(path)
    t0 = BASE_MS + 30_000_000
    _insert_msg(conn, NONE_SESSION, 1, "user", _user_data(t0), t0)
    for i, tk in enumerate([_tokens_missing_write(70, 5, 40),
                            _tokens_missing_write(60, 4, 30)], start=1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        _insert_msg(conn, NONE_SESSION, seq, "assistant",
                    _assistant_data(
                        ms,
                        [_tool_part("read", "r" * 8, ms,
                                    args={"path": "/fixture/dir/n%d" % i},
                                    part_id=f"p{seq}")],
                        tk, None),
                    ms)
    _insert_session(conn, NONE_SESSION, t0, t0 + 2 * STEP_MS,
                    (130, 9, 0, 70, 0), None)
    conn.commit()
    conn.close()


def _build_big(path: Path, n_steps: int, sid: str) -> None:
    """Fixture grande SINTÉTICO: `n_steps` pasos `assistant` (cada uno con su
    llamada de herramienta y proxy observable 200), sin brecha → un solo
    tramo = la sesión. Sirve para medir el tamaño del documento POR DEFECTO
    a distintas escalas (1000 vs 4000 pasos)."""
    conn = _new_store(path)
    t0 = BASE_MS + 40_000_000
    _insert_msg(conn, sid, 1, "user", _user_data(t0), t0)
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i in range(1, n_steps + 1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        sum_in += 100
        sum_cread += 100
        sum_out += 40
        sum_reason += 5
        _insert_msg(conn, sid, seq, "assistant",
                    _assistant_data(
                        ms,
                        [_tool_part("read", "s" * 8, ms,
                                    args={"path": "/fixture/dir/b%d" % i},
                                    part_id=f"p{seq}")],
                        _tokens_full(100, 40, 100), 0.0),
                    ms)
    _insert_session(conn, sid, t0, t0 + n_steps * STEP_MS,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), 0.0)
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


class BoundedOutputT5bTest(unittest.TestCase):
    """T5b RED de 005-002 (reapertura acotada, unidad 2 de 2): un test por
    postcondición de la interfaz declarada, contra la SALIDA del wrapper
    (stdout JSON + rc + stderr)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t5b-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_edge = base / "edge" / "sessions.db"
        self.store_partial = base / "partial" / "sessions.db"
        self.store_none = base / "none" / "sessions.db"
        self.store_big_small = base / "big-small" / "sessions.db"
        self.store_big_large = base / "big-large" / "sessions.db"
        _build_edge(self.store_edge)
        _build_partial(self.store_partial)
        _build_none_observable(self.store_none)
        _build_big(self.store_big_small, BIG_STEPS_SMALL, BIG_SMALL_SESSION)
        _build_big(self.store_big_large, BIG_STEPS_LARGE, BIG_LARGE_SESSION)

    # -- corrida del wrapper (SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str, timeout_s: int = CLI_TIMEOUT_S
                  ) -> subprocess.CompletedProcess:
        if not METER_WRAPPER.is_file():
            self.fail(
                f"{FEATURE_ID}: el medidor `{METER_WRAPPER.name}` no existe "
                "aún — RED por CLI ausente (comportamiento ausente), nunca "
                "por ImportError: el test NO importa el módulo del medidor")
        cmd = [sys.executable, str(METER_WRAPPER), *argv]
        env = os.environ.copy()
        env.pop(STORE_ENV_VAR, None)      # sin fuga del entorno del host
        try:
            return subprocess.run(
                cmd, cwd=REPO_ROOT, env=env, capture_output=True,
                timeout=timeout_s, stdin=subprocess.DEVNULL)
        except FileNotFoundError:  # pragma: no cover
            self.fail(
                f"{FEATURE_ID}: el medidor `{METER_WRAPPER.name}` no ejecuta "
                "aún (comportamiento ausente); el test NO importa el módulo "
                "del medidor")
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                f"PD-11 (acotado): el medidor no terminó dentro de "
                f"{timeout_s}s; timeout={exc!r}")

    def _parse_ok(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: rc=0 sobre un fixture válido (el esquema se "
                f"reconoce; no es fallo cerrado); "
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
            msg=f"{label}: el fixture replica el esquema observado y debe "
                f"reconocerse (run={run}) — si sale `unknown` el RED sería de "
                "rejilla equivocada")
        self.assertEqual(
            len(doc.get("sessions", [])), 1,
            msg=f"{label}: el fixture tiene UNA sesión (el límite publicado "
                "de bytes es POR DOCUMENTO de sesión)")
        return doc

    def session_default(self, store: Path, label: str,
                        timeout_s: int = CLI_TIMEOUT_S):
        """Corrida POR DEFECTO (sin `--steps`): la medición acotada."""
        proc = self.run_meter("--store", str(store), timeout_s=timeout_s)
        doc = self._parse_ok(proc, label)
        return proc, doc["sessions"][0]

    def session_with_steps(self, store: Path, label: str):
        """Corrida CON la bandera declarada `--steps`: el detalle por paso.

        Si la bandera todavía no existe, el wrapper falla cerrado por
        argumento desconocido (rc=2): se reporta como el estado RED de una
        INTERFAZ DECLARADA por el test, explícitamente distinguido de una
        falla de comportamiento del contrato."""
        proc = self.run_meter("--store", str(store), DETAIL_FLAG)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace")
            if proc.returncode == 2:
                self.fail(
                    f"{label}: la bandera `{DETAIL_FLAG}` declarada por este "
                    "test AÚN NO EXISTE (rc=2: argumento desconocido) — "
                    "estado RED de una INTERFAZ DECLARADA por el test, no una "
                    f"falla de comportamiento del contrato; stderr="
                    f"{err[:300]!r}")
            self.fail(
                f"{label}: con `{DETAIL_FLAG}` se espera rc=0 (fue "
                f"{proc.returncode}); stderr={err[:300]!r}")
        doc = self._parse_ok(proc, label)
        return proc, doc["sessions"][0]

    def measure_leaf(self, measures: object, key: str, ctx: str) -> dict:
        leaves = dict(_measure_leaves(measures))
        leaf = leaves.get(key)
        self.assertIsNotNone(
            leaf,
            msg=f"{ctx}: la medida {key!r} NO existe en el registro — RED de "
                f"contrato (hojas presentes: {sorted(leaves)})")
        self.assertIsInstance(leaf, dict, msg=f"{ctx}: {key} es una hoja")
        return leaf

    def input_per_step(self, session: dict, ctx: str) -> dict:
        return self.measure_leaf(session.get("measures", {}),
                                 "input_per_step", ctx)

    def summary_of(self, session: dict, ctx: str) -> dict:
        """`input_per_step.value` POR DEFECTO debe ser el resumen de tamaño
        fijo (objeto), no la lista detallada."""
        leaf = self.input_per_step(session, ctx)
        value = leaf.get("value")
        self.assertIsInstance(
            value, dict,
            msg=f"{ctx}: POR DEFECTO `input_per_step.value` porta el RESUMEN "
                "de tamaño fijo (objeto con "
                f"{SUMMARY_KEYS!r}), NO la lista por paso — el detalle exige "
                f"`{DETAIL_FLAG}` (fue {type(value).__name__}: "
                f"{str(value)[:200]!r}; D2/PD-12)")
        for key in SUMMARY_KEYS:
            self.assertIn(
                key, value,
                msg=f"{ctx}: el resumen declara la clave {key!r} (fue "
                    f"{sorted(value)!r})")
        return value

    def truncated_of(self, leaf: dict, ctx: str) -> dict:
        """Indicador de truncación y su causa declarado en la hoja de la
        medida."""
        tr = leaf.get("truncated")
        self.assertIsInstance(
            tr, dict,
            msg=f"{ctx}: la hoja de `input_per_step` declara el indicador de "
                f"truncado `truncated` (objeto con {TRUNCATED_KEYS!r}) — "
                f"`truncated` es una clave de la HOJA de la medida (fue "
                f"{tr!r})")
        for key in TRUNCATED_KEYS:
            self.assertIn(
                key, tr,
                msg=f"{ctx}: el indicador de truncado declara {key!r} (fue "
                    f"{sorted(tr)!r})")
        self.assertIsInstance(
            tr.get("truncated"), bool,
            msg=f"{ctx}: `truncated.truncated` es bool (fue "
                f"{tr.get('truncated')!r})")
        self.assertEqual(
            tr.get("detail_flag"), DETAIL_FLAG,
            msg=f"{ctx}: `truncated.detail_flag` nombra la bandera del "
                f"detalle ({DETAIL_FLAG}; fue {tr.get('detail_flag')!r})")
        self.assertIsInstance(
            tr.get("omitted_steps"), int,
            msg=f"{ctx}: `truncated.omitted_steps` es entero (fue "
                f"{tr.get('omitted_steps')!r})")
        return tr

    # ------------------- punto 2 + punto 3 + punto 5: resumen por defecto

    def test_t5b_1_default_summary_shape_and_pinned_last_previous(self):
        """POR DEFECTO (sin `--steps`): `input_per_step.value` es el RESUMEN
        de tamaño FIJO (objeto con count/last/previous/min/max/unobserved);
        el resumen porta lo que el contrato pinea: `last` = 203.276 y
        `previous` = 202.222 (las cifras del tramo de 102 pasos de la muestra
        1); `unobserved` es 0 en el fixture donde todos los pasos reportan;
        `min`/`max` se computan sobre los proxys observables; el indicador de
        truncado declara por defecto truncated=true, omitted_steps=count,
        detail_flag="--steps" y una causa que cita el límite publicado de
        16384 bytes POR DOCUMENTO de sesión y declara que el detalle se
        obtiene con `--steps` (PD-3, PD-4, PD-8, PD-12; INV-4)."""
        label = "T5b(1) resumen por defecto"
        _, session = self.session_default(self.store_edge, label)
        value = self.summary_of(session, label)
        # SONDA DECLARADA DEL FIXTURE (no del contrato): el fixture fiel
        # tiene 102 pasos (101 llamadas + el assistant que cierra). La spec
        # pinea 101 LLAMADAS de herramienta, no la cantidad de pasos: el
        # assert de contrato es `count >= llamadas`; el conteo exacto queda
        # como sonda informativa del fixture.
        steps_probe = value["count"]
        self.assertGreaterEqual(
            steps_probe, EDGE_TOOL_CALLS,
            msg=f"{label}: `count` es >= las llamadas de herramienta del "
                f"tramo ({EDGE_TOOL_CALLS}; fue {steps_probe!r})")
        self.assertEqual(
            steps_probe, EDGE_STEPS,
            msg=f"{label}: [sonda declarada del fixture] los pasos del tramo "
                f"del fixture fiel son {EDGE_STEPS} (101 llamadas + el "
                f"assistant que cierra) — fue {steps_probe!r}; el contrato "
                "solo pinea 101 llamadas de herramienta")
        self.assertEqual(
            value["last"], EDGE_PROXY_CLOSING,
            msg=f"{label}: `last` = proxy del ÚLTIMO paso = "
                f"{EDGE_PROXY_CLOSING} tok (input 1164 + cache.read 202112 + "
                f"cache.write 0), el mensaje que CIERRA el tramo; fue "
                f"{value['last']!r} (PD-5/PD-8)")
        self.assertNotEqual(
            value["last"], EDGE_PROXY_LAST_CALL,
            msg=f"{label}: el borde alternativo NO se usa — `last` NO es el "
                f"proxy del último paso CON herramienta "
                f"({EDGE_PROXY_LAST_CALL} tok)")
        self.assertEqual(
            value["previous"], EDGE_PROXY_LAST_CALL,
            msg=f"{label}: `previous` = proxy del PENÚLTIMO paso = "
                f"{EDGE_PROXY_LAST_CALL} tok (el paso #101, último CON "
                f"herramienta, borde alternativo visible y NO usado); fue "
                f"{value['previous']!r} (PD-5/PD-8)")
        self.assertEqual(
            value["max"], EDGE_PROXY_CLOSING,
            msg=f"{label}: `max` es el MAYOR proxy observable del tramo "
                f"({EDGE_PROXY_CLOSING}); fue {value['max']!r}")
        self.assertEqual(
            value["min"], EDGE_PROXY_DEFAULT,
            msg=f"{label}: `min` es el MENOR proxy observable del tramo "
                f"({EDGE_PROXY_DEFAULT} = input 100 + cache.read 100 + w 0); "
                f"fue {value['min']!r}")
        self.assertEqual(
            value["unobserved"], 0,
            msg=f"{label}: ningún paso del fixture tiene proxy no observable "
                f"→ `unobserved` = 0; fue {value['unobserved']!r}")
        # indicador de truncado: por defecto TRUNCA y declara la causa.
        leaf = self.input_per_step(session, label)
        tr = self.truncated_of(leaf, label)
        self.assertTrue(
            tr["truncated"],
            msg=f"{label}: por defecto el detalle se OMITE → "
                f"truncated=true (fue {tr['truncated']!r}; punto 3)")
        self.assertEqual(
            tr["omitted_steps"], steps_probe,
            msg=f"{label}: por defecto `omitted_steps` = count = "
                f"{steps_probe} (cuántos pasos no se detallan); fue "
                f"{tr['omitted_steps']!r}")
        cause = tr.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"{label}: la causa del truncado es texto (fue {cause!r})")
        low = cause.lower()
        self.assertIn(
            "16384", low,
            msg=f"{label}: la causa cita el límite PUBLICADO de 16384 bytes "
                f"por documento de sesión (fue {cause!r})")
        self.assertIn(
            DETAIL_FLAG, low,
            msg=f"{label}: la causa declara que el detalle se obtiene con "
                f"`{DETAIL_FLAG}` (fue {cause!r})")
        self.assertTrue(
            any(w in low for w in ("byte", "bytes", "limit", "limite",
                                   "límite", "size", "tamano", "tamaño")),
            msg=f"{label}: la causa declara POR QUÉ se omite el detalle "
                f"(límite de tamaño/bytes) (fue {cause!r})")
        self.assertTrue(
            any(w in low for w in ("document", "documento", "session",
                                   "sesion", "sesión")),
            msg=f"{label}: la causa declara que el límite es por documento "
                f"de sesión (fue {cause!r})")

    # ------------------- punto 2: no observable es null, nunca 0

    def test_t5b_2_unobservable_proxy_null_and_min_max_null_when_none(self):
        """Un paso cuyo proxy no es observable cuenta en `unobserved` y su
        valor es `null`, NUNCA 0; `min`/`max` se computan solo sobre los
        proxys observables y son `null` cuando NO hay ningún proxy
        observable (`last`/`previous` también `null` en ese caso). PD-3,
        PD-4, PD-8, PD-12; INV-4."""
        label = "T5b(2) proxy no observable"
        _, session = self.session_default(self.store_partial, label)
        value = self.summary_of(session, label)
        self.assertEqual(
            value["count"], PARTIAL_STEPS,
            msg=f"{label}: el tramo tiene {PARTIAL_STEPS} pasos (fue "
                f"{value['count']!r})")
        self.assertEqual(
            value["last"], PARTIAL_PROXY_LAST,
            msg=f"{label}: `last` = proxy del último paso = "
                f"{PARTIAL_PROXY_LAST} (fue {value['last']!r})")
        self.assertIsNone(
            value["previous"],
            msg=f"{label}: el penúltimo paso NO tiene proxy observable → "
                f"`previous` es null, NUNCA 0 (fue {value['previous']!r}; "
                "PD-4/INV-4)")
        self.assertEqual(
            value["min"], PARTIAL_PROXY_LAST,
            msg=f"{label}: `min` sobre los proxys OBSERVABLES = "
                f"{PARTIAL_PROXY_LAST} (fue {value['min']!r})")
        self.assertEqual(
            value["max"], PARTIAL_PROXY_FIRST,
            msg=f"{label}: `max` sobre los proxys OBSERVABLES = "
                f"{PARTIAL_PROXY_FIRST} (fue {value['max']!r})")
        self.assertEqual(
            value["unobserved"], PARTIAL_UNOBSERVED,
            msg=f"{label}: `unobserved` cuenta los pasos sin proxy "
                f"observable ({PARTIAL_UNOBSERVED}); fue "
                f"{value['unobserved']!r}")
        # control negativo: ningún `null` se disfraza de 0 fabricado.
        for key in ("previous",):
            self.assertNotEqual(
                value[key], 0,
                msg=f"{label}: `{key}` null no se degrada a 0 fabricado "
                    f"(fue {value[key]!r})")
        # ningún proxy observable → min/max/last/previous null.
        label_none = label + " (ninguno observable)"
        _, session_none = self.session_default(self.store_none, label_none)
        none = self.summary_of(session_none, label_none)
        self.assertEqual(
            none["count"], NONE_STEPS,
            msg=f"{label_none}: el tramo tiene {NONE_STEPS} pasos (fue "
                f"{none['count']!r})")
        self.assertEqual(
            none["unobserved"], NONE_UNOBSERVED,
            msg=f"{label_none}: TODOS los proxies son no observables → "
                f"`unobserved` = {NONE_UNOBSERVED} (fue "
                f"{none['unobserved']!r})")
        for key in ("min", "max", "last", "previous"):
            self.assertIsNone(
                none[key],
                msg=f"{label_none}: sin NINGÚN proxy observable `{key}` es "
                    f"null, NUNCA 0 (fue {none[key]!r}; PD-4/INV-4)")

    # ------------------- puntos 1 + 3: la bandera `--steps`

    def test_t5b_3_steps_flag_restores_full_ordered_detail(self):
        """CON la bandera declarada `--steps`: `input_per_step.value` vuelve a
        portar la lista ORDENADA completa de proxys por paso (un elemento por
        paso del tramo; `null` para el paso cuyo proxy no es observable) y el
        indicador declara truncated=false con omitted_steps=0 (el detalle no
        se omite: el límite de bytes NO aplica cuando el usuario pidió el
        detalle). El último elemento es el proxy pinneado 203.276 y el
        penúltimo el borde alternativo 202.222 (misma muestra 1). PD-5, PD-8,
        PD-12."""

        # (a) el fixture con un paso no observable: lista ordenada completa.
        label = "T5b(3) --steps (paso no observable)"
        _, session = self.session_with_steps(self.store_partial, label)
        leaf = self.input_per_step(session, label)
        value = leaf.get("value")
        self.assertIsInstance(
            value, list,
            msg=f"{label}: con `{DETAIL_FLAG}` `input_per_step.value` es la "
                f"lista ORDENADA por paso (fue {type(value).__name__})")
        self.assertEqual(
            len(value), PARTIAL_STEPS,
            msg=f"{label}: un elemento por paso del tramo "
                f"({PARTIAL_STEPS}; fue {value!r})")
        self.assertEqual(
            value[0], PARTIAL_PROXY_FIRST,
            msg=f"{label}: el primer paso (los TRES componentes reportados) "
                f"porta su proxy {PARTIAL_PROXY_FIRST} (fue {value[0]!r})")
        self.assertIsNone(
            value[1],
            msg=f"{label}: el paso sin `cache.write` porta `null` (proxy no "
                f"observable, NUNCA 0; fue {value[1]!r})")
        self.assertEqual(
            value[2], PARTIAL_PROXY_LAST,
            msg=f"{label}: el último paso porta su proxy "
                f"{PARTIAL_PROXY_LAST} (fue {value[2]!r})")
        tr = self.truncated_of(leaf, label)
        self.assertFalse(
            tr["truncated"],
            msg=f"{label}: con `{DETAIL_FLAG}` el detalle NO se omite → "
                f"truncated=false (fue {tr['truncated']!r})")
        self.assertEqual(
            tr["omitted_steps"], 0,
            msg=f"{label}: con `{DETAIL_FLAG}` omitted_steps=0 (fue "
                f"{tr['omitted_steps']!r})")

        # (b) la muestra 1: la lista ordenada termina en los proxys pinneados.
        label_edge = "T5b(3) --steps (muestra 1)"
        _, session_edge = self.session_with_steps(self.store_edge, label_edge)
        leaf_edge = self.input_per_step(session_edge, label_edge)
        steps = leaf_edge.get("value")
        self.assertIsInstance(
            steps, list,
            msg=f"{label_edge}: `{DETAIL_FLAG}` restaura la lista por paso "
                f"(fue {type(steps).__name__})")
        self.assertEqual(
            steps[-1], EDGE_PROXY_CLOSING,
            msg=f"{label_edge}: el proxy del ÚLTIMO paso es "
                f"{EDGE_PROXY_CLOSING} (input 1164 + cache.read 202112 + "
                f"w 0); fue {steps[-1]!r}")
        self.assertEqual(
            steps[-2], EDGE_PROXY_LAST_CALL,
            msg=f"{label_edge}: el paso anterior (último CON herramienta) "
                f"porta el borde alternativo {EDGE_PROXY_LAST_CALL} (visible, "
                f"NO usado); fue {steps[-2]!r}")
        tr_edge = self.truncated_of(leaf_edge, label_edge)
        self.assertFalse(
            tr_edge["truncated"],
            msg=f"{label_edge}: con `{DETAIL_FLAG}` truncated=false (fue "
                f"{tr_edge['truncated']!r})")

    # ------------------- punto 4: el límite se cumple a escala

    def test_t5b_4_default_document_bounded_regardless_of_session_size(self):
        """PD-12 + D2: el documento POR DEFECTO de UNA sesión mide 16384 bytes
        o menos CUALQUIERA sea la cantidad de pasos del tramo (fixtures
        sintéticos de 1000 y 4000 pasos, ambos por debajo del límite), y el
        resumen es de tamaño FIJO: el tamaño del documento no crece con la
        cantidad de pasos — la diferencia entre 1000 y 4000 pasos queda dentro
        del margen acotado SIZE_GROWTH_MARGIN_BYTES (el resumen es un objeto
        de forma fija; el defecto D2, que emitía el detalle por paso, sumaría
        ≳18.000 bytes por 3000 pasos extra). El documento por defecto sigue
        portando el RESUMEN (objeto), no la lista. PD-3, PD-8, PD-12."""
        label_small = "T5b(4) fixture grande 1000"
        label_large = "T5b(4) fixture grande 4000"
        proc_small, session_small = self.session_default(
            self.store_big_small, label_small, timeout_s=BIG_CLI_TIMEOUT_S)
        proc_large, session_large = self.session_default(
            self.store_big_large, label_large, timeout_s=BIG_CLI_TIMEOUT_S)
        size_small = len(proc_small.stdout)
        size_large = len(proc_large.stdout)
        self.assertLessEqual(
            size_small, BYTE_LIMIT,
            msg=f"{label_small}: el documento POR DEFECTO de UNA sesión mide "
                f"{size_small} bytes y el límite publicado es {BYTE_LIMIT} "
                "bytes; el tamaño NO debe crecer con la cantidad de pasos "
                "(PD-12/D2)")
        self.assertLessEqual(
            size_large, BYTE_LIMIT,
            msg=f"{label_large}: el documento POR DEFECTO de UNA sesión mide "
                f"{size_large} bytes y el límite publicado es {BYTE_LIMIT} "
                "bytes; el tamaño NO debe crecer con la cantidad de pasos "
                "(PD-12/D2)")
        self.assertLessEqual(
            abs(size_large - size_small), SIZE_GROWTH_MARGIN_BYTES,
            msg=f"PD-12/D2: el resumen es de tamaño FIJO — entre 1000 y 4000 "
                f"pasos el tamaño cambia |{size_large} - {size_small}| = "
                f"{abs(size_large - size_small)} bytes, margen acotado "
                f"{SIZE_GROWTH_MARGIN_BYTES} (el detalle por paso sumaría "
                "≳18.000 bytes por los 3000 pasos extra)")
        # el documento por defecto sigue portando el RESUMEN, no la lista,
        # y declara el conteo de pasos del tramo a cada escala.
        small_summary = self.summary_of(session_small, label_small)
        large_summary = self.summary_of(session_large, label_large)
        self.assertGreaterEqual(
            small_summary["count"], BIG_STEPS_SMALL,
            msg=f"{label_small}: `count` es >= los pasos del tramo "
                f"({BIG_STEPS_SMALL}; fue {small_summary['count']!r})")
        self.assertGreaterEqual(
            large_summary["count"], BIG_STEPS_LARGE,
            msg=f"{label_large}: `count` es >= los pasos del tramo "
                f"({BIG_STEPS_LARGE}; fue {large_summary['count']!r})")
        tr = self.truncated_of(
            self.input_per_step(session_large, label_large), label_large)
        self.assertTrue(
            tr["truncated"],
            msg=f"{label_large}: con miles de pasos el detalle se OMITE por "
                f"defecto y se declara (truncated=true; fue {tr['truncated']!r})")
        self.assertEqual(
            tr["omitted_steps"], large_summary["count"],
            msg=f"{label_large}: `omitted_steps` = count = "
                f"{large_summary['count']} (cuántos pasos no se detallan; fue "
                f"{tr['omitted_steps']!r})")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
