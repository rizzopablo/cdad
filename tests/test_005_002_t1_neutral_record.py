#!/usr/bin/env python3
"""005-002 T1 RED — registro neutral, contrato de invocación, fallo cerrado,
determinismo/solo-lectura y medición opcional (PD-1, PD-2, PD-3, PD-4, PD-11,
PD-13, PD-15, PD-16).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (§2 contrato del registro
  neutral y de la superficie de invocación; PD-1, PD-2, PD-3, PD-4, PD-11,
  PD-13, PD-15, PD-16; INV-1..INV-6).
- docs/specs/005-002-session-context-meter/plan.md (T1: ficha de la tarea,
  focales declarados).
- Forma del esquema de los fixtures: discovery.md §1.2–§1.6 (tablas
  `session_v2` y `session_message` con sus columnas; formas de `data` de
  assistant/tool/user). El CONTENIDO de las filas es 100% SINTÉTICO,
  inventado por este test en un directorio temporal: ningún identificador de
  sesión, ruta, texto, proveedor ni modelo de la base real del runtime
  (el store real JAMÁS se abre aquí).

Superficie observable bajo prueba (PD-15/C1): el WRAPPER FINO
`scripts/cdad_context_meter.py`, invocado SIEMPRE por subproceso
(sys.executable) — NUNCA importando el módulo:

    python3 scripts/cdad_context_meter.py --store PATH \
        [--session REF]... [--limit N] [--idle-threshold MINUTES] [--json]

El contrato observable es la salida JSON por stdout, el rc y el diagnóstico
por stderr. `--session REF` recibe el identificador de sesión del store (la
referencia que el test puede observar del insumo; el registro hashea en su
SALIDA, no en la selección).

Decisión de fixture declarada para el GREEN (la discovery no fija el formato
de los tiempos): las columnas `time_*` de session_v2/session_message y los
campos `time` de `data` usan EPOCH EN MILISEGUNDOS (números). Sin brecha
mayor que el umbral → toda la sesión es UN tramo (PD-5); T1 verifica
ESTRUCTURA del contrato (claves, cubos, fallo cerrado, determinismo,
solo-lectura), NO los valores pinneados de la muestra (T2) ni el límite de
bytes de la salida (PD-12/T3 — no se fija ni se asume aquí).

RED hoy: `scripts/cdad_context_meter.py` no existe aún; cada aserción fracasa
por comportamiento ausente (AssertionError con el mensaje `el medidor no
existe aún`), nunca por ImportError ni sintaxis — el test no importa el
módulo del medidor ni toca implementación.

Fixtures (por store, todos en tmp):
- `valid`: 2 sesiones (roles distintos) con tokens POR PASO, `cache_write`
  0 en filas (el proveedor no lo reporta — V5), `cost` NULL/nulo, una parte
  tool `read` y salidas textuales de longitud conocida.
- `missing-table`: session_v2 SIN la tabla `session_message` (PD-2).
- `missing-column`: session_message SIN su columna `data` (PD-2).
- `no-token-data`: 1 sesión SIN datos de tokens en filas ni columnas
  (PD-13: registro válido con cubos unknown, no un fallo).
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

METER_ID = "context-meter-v1"

# Claves requeridas del registro neutral (spec §2; PD-16/C2).
REQUIRED_TOP_KEYS = (
    "schema_version", "meter", "run", "window",
    "sessions", "roles", "unknowns")
REQUIRED_RUN_KEYS = ("store_ref", "runtime_version", "schema")
REQUIRED_WINDOW_KEYS = ("criterion", "start_ref", "end_ref", "cutoff")
REQUIRED_SESSION_KEYS = (
    "session_ref", "role", "model", "parent_ref", "runtime_version",
    "window", "milestones", "measures", "buckets")
REQUIRED_MILESTONE_KEYS = ("first_resume", "first_dispatch")
REQUIRED_MEASURE_KEYS = (
    "time_to_first_resume", "time_to_first_dispatch", "previous_calls",
    "previous_reads", "total_output", "max_output", "input_per_step",
    "accumulated", "cache")
REQUIRED_BUCKET_KEYS = ("observed", "estimated", "unknown")
MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")
BUCKET_VALUES = ("observed", "estimated", "unknown")
MILESTONE_STATUS_VALUES = ("observed", "absent", "unknown")

# Neutralidad (PD-1/INV-3): el registro neutral NO porta nombres de
# tablas/columnas del runtime; el adaptador es el único traductor.
RUNTIME_NAMES = ("session_v2", "session_message")

# Roles/modelos/ids 100% SINTÉTICOS (inventados; nada de la base real).
ROLE_A = "cdad-orchestrator"
ROLE_B = "cdad-test-writer"
MODEL_A = '{"id":"model-alpha","providerID":"prov-a"}'
MODEL_B = '{"id":"model-beta","providerID":"prov-b"}'
SESSION_A = "sess-fixture-alpha-0001"
SESSION_A2 = "sess-fixture-alpha-0002"
SESSION_B = "sess-fixture-beta-0001"

BASE_MS = 1_760_000_000_000  # epoch ms SINTÉTICO, fijo (determinismo)

TOOL_READ_TEXT = "fixture-output-alpha-42\n"
TEXT_STEP_1 = "fixture respuesta alpha paso 1 (sintetica)\n"
TEXT_STEP_2 = "fixture respuesta alpha paso 2 (sintetica)\n"
TEXT_STEP_3 = "fixture respuesta beta unica (sintetica)\n"
USER_TEXT = "fixture prompt sintetico para el medidor\n"


# ---------------------------------------------------------------- fixtures

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

SESSION_MESSAGE_DDL_FULL = """
CREATE TABLE session_message (
    id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INTEGER,
    time_created REAL, time_updated REAL, data TEXT)
"""

# PD-2: la columna `data` (insumo de TODO el registro) es requerida.
SESSION_MESSAGE_DDL_NO_DATA = """
CREATE TABLE session_message (
    id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INTEGER,
    time_created REAL, time_updated REAL)
"""


def _data_time(ms: int) -> dict:
    return {"created": ms, "streamed": ms, "completed": ms}


def _tool_part(name: str, text: str, *, ms: int, path: str | None = None,
               part_id: str = "part-fixture-1") -> dict:
    """Parte `tool` (discovery §1.4): state.content = [{type:text, text}] →
    el tamaño de salida = suma de len(text)."""
    state: dict = {
        "status": "completed",
        "input": ({"path": path} if path else {}),
        "content": [{"type": "text", "text": text}],
    }
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": state, "time": {"created": ms, "ran": ms, "completed": ms},
    }


def _assistant_data(*, agent: str, model: str, ms: int, parts: list,
                    tokens: tuple | None = None, cost: float | None = None,
                    ) -> str:
    """Forma `assistant` (discovery §1.3): time/agent/model/content/cost/
    tokens {input, output, reasoning, cache:{read, write}}. `tokens=None`
    = datos de tokens AUSENTES (PD-13); `cost=None` = costo nulo (PD-4)."""
    doc: dict = {
        "time": _data_time(ms), "agent": agent, "model": model,
        "content": parts,
    }
    if tokens is not None:
        tin, tout, treason, tread, twrite = tokens
        doc["tokens"] = {
            "input": tin, "output": tout, "reasoning": treason,
            "cache": {"read": tread, "write": twrite},
        }
    doc["cost"] = cost  # None → JSON null en las filas
    return json.dumps(doc, sort_keys=True)


def _user_data(ms: int, text: str) -> str:
    """Forma `user` (discovery §1.3): {time, text}."""
    return json.dumps({"time": ms, "text": text}, sort_keys=True)


def _insert_session_row(conn: sqlite3.Connection, *, session_id: str,
                        agent: str, model: str, t_created: float,
                        t_updated: float, tokens: tuple | None = None,
                        cost: float | None = None, parent_id: str | None = None,
                        ) -> None:
    if tokens is None:
        tok = {"tokens_input": None, "tokens_output": None,
               "tokens_reasoning": None, "tokens_cache_read": None,
               "tokens_cache_write": None}
    else:
        tin, tout, treason, tread, twrite = tokens
        tok = {"tokens_input": tin, "tokens_output": tout,
               "tokens_reasoning": treason, "tokens_cache_read": tread,
               "tokens_cache_write": twrite}
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
        (session_id, "proj-fixture", "ws-fixture", parent_id, None, None,
         "fixture-slug", "/fixture/dir", "/fixture/dir", "fixture title",
         "fixture-version", None, 0, 0, 0, 0, None, cost,
         tok["tokens_input"], tok["tokens_output"], tok["tokens_reasoning"],
         tok["tokens_cache_read"], tok["tokens_cache_write"], None, None,
         agent, model, t_created, t_updated, None, None, None, 0, None,
         None, None))


def _insert_message(conn: sqlite3.Connection, *, session_id: str, seq: int,
                    mtype: str, data: str, ms: float) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{session_id}", session_id, mtype, seq, ms, ms,
         data))


def _build_store(path: Path, *, variant: str) -> None:
    """Fixture SQLite SINTÉTICO con el esquema observado (discovery §1.2–1.6).
    Variantes: `valid`, `no-token-data`, `missing-table`, `missing-column`.
    Escritura atómica tmp + os.replace; journal por defecto (cierre limpio
    sin -wal/-shm remanentes, para el check de solo-lectura de PD-11)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (path.name + ".tmp")
    try:
        tmp.unlink()
    except OSError:
        pass
    conn = sqlite3.connect(str(tmp))
    try:
        conn.execute(SESSION_V2_DDL)
        if variant != "missing-table":
            if variant == "missing-column":
                conn.execute(SESSION_MESSAGE_DDL_NO_DATA)
            else:
                conn.execute(SESSION_MESSAGE_DDL_FULL)

        if variant == "valid":
            # Sesión A: tokens por paso, cache_write 0 (no reportado — V5),
            # cost NULO (PD-4), tool read + salidas de longitud conocida.
            _insert_session_row(
                conn, session_id=SESSION_A, agent=ROLE_A, model=MODEL_A,
                t_created=BASE_MS, t_updated=BASE_MS + 4000,
                tokens=(250, 100, 10, 500, 0), cost=None)
            msgs_a = [
                (1, "user", _user_data(BASE_MS, USER_TEXT)),
                (2, "assistant", _assistant_data(
                    agent=ROLE_A, model=MODEL_A, ms=BASE_MS + 2000,
                    parts=[_tool_part("read", TOOL_READ_TEXT,
                                      ms=BASE_MS + 2000,
                                      path="/fixture/dir/a.md",
                                      part_id="part-fixture-a-1"),
                           {"type": "text", "text": TEXT_STEP_1}],
                    tokens=(100, 40, 10, 200, 0), cost=None)),
                (3, "assistant", _assistant_data(
                    agent=ROLE_A, model=MODEL_A, ms=BASE_MS + 4000,
                    parts=[{"type": "text", "text": TEXT_STEP_2}],
                    tokens=(150, 60, 0, 300, 0), cost=None)),
            ]
            for seq, mtype, data in msgs_a:
                _insert_message(conn, session_id=SESSION_A, seq=seq,
                                mtype=mtype, data=data, ms=BASE_MS + seq * 2000)
            # Sesión A2 (otro rol): mínimo, tokens presentes.
            _insert_session_row(
                conn, session_id=SESSION_A2, agent=ROLE_B, model=MODEL_B,
                t_created=BASE_MS + 10_000, t_updated=BASE_MS + 12_000,
                tokens=(30, 10, 0, 50, 0), cost=None)
            msgs_a2 = [
                (1, "user", _user_data(BASE_MS + 10_000, USER_TEXT)),
                (2, "assistant", _assistant_data(
                    agent=ROLE_B, model=MODEL_B, ms=BASE_MS + 12_000,
                    parts=[{"type": "text", "text": TEXT_STEP_3}],
                    tokens=(30, 10, 0, 50, 0), cost=None)),
            ]
            for seq, mtype, data in msgs_a2:
                _insert_message(conn, session_id=SESSION_A2, seq=seq,
                                mtype=mtype, data=data,
                                ms=BASE_MS + 10_000 + seq * 2000)

        elif variant == "no-token-data":
            # PD-13: SIN datos de tokens (columnas NULL y filas assistant
            # sin la clave `tokens`) → registro VÁLIDO con cubos unknown.
            _insert_session_row(
                conn, session_id=SESSION_B, agent=ROLE_B, model=MODEL_B,
                t_created=BASE_MS, t_updated=BASE_MS + 2000, tokens=None,
                cost=None)
            msgs_b = [
                (1, "user", _user_data(BASE_MS, USER_TEXT)),
                (2, "assistant", _assistant_data(
                    agent=ROLE_B, model=MODEL_B, ms=BASE_MS + 2000,
                    parts=[{"type": "text", "text": TEXT_STEP_3}],
                    tokens=None, cost=None)),
            ]
            for seq, mtype, data in msgs_b:
                _insert_message(conn, session_id=SESSION_B, seq=seq,
                                mtype=mtype, data=data, ms=BASE_MS + seq * 2000)

        elif variant == "missing-table":
            # PD-2: la tabla session_message ENTERA falta → el registro es
            # inconstruible → fallo cerrado que NOMBRA la tabla.
            _insert_session_row(
                conn, session_id=SESSION_A, agent=ROLE_A, model=MODEL_A,
                t_created=BASE_MS, t_updated=BASE_MS + 4000,
                tokens=(250, 100, 10, 500, 0), cost=None)

        elif variant == "missing-column":
            # PD-2: la columna `data` de session_message falta.
            _insert_session_row(
                conn, session_id=SESSION_A, agent=ROLE_A, model=MODEL_A,
                t_created=BASE_MS, t_updated=BASE_MS + 4000,
                tokens=(250, 100, 10, 500, 0), cost=None)
            conn.execute(
                "INSERT INTO session_message (id, session_id, type, seq,"
                " time_created, time_updated) VALUES (?, ?, ?, ?, ?, ?)",
                (f"msg-0001-{SESSION_A}", SESSION_A, "user", 1,
                 BASE_MS, BASE_MS))

        conn.commit()
    finally:
        conn.close()
    os.replace(tmp, path)


def _walk_dicts(obj: object):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_dicts(item)


def _walk_kv(obj: object, prefix: str = ""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield f"{prefix}.{key}" if prefix else key, value
            yield from _walk_kv(value, f"{prefix}.{key}" if prefix else key)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            yield from _walk_kv(item, f"{prefix}[{index}]")


def _measure_leaves(measures: object, prefix: str = ""):
    """Hojas de métrica: todo dict con los campos (value, unit, provenance,
    bucket) — a cualquier profundidad de anidamiento declarado."""
    if isinstance(measures, dict):
        if all(field in measures for field in MEASURE_FIELDS):
            yield prefix, measures
            return
        for key, value in measures.items():
            path = f"{prefix}.{key}" if prefix else key
            yield from _measure_leaves(value, path)


# ---------------------------------------------------------------- tests


class NeutralRecordT1Test(unittest.TestCase):
    """T1 RED de 005-002: un test por postcondición, contra la salida del
    wrapper (stdout JSON + rc + diagnóstico por stderr)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t1-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_valid = base / "valid" / "sessions.db"
        self.store_no_msg_table = base / "missing-table" / "sessions.db"
        self.store_no_data_column = base / "missing-column" / "sessions.db"
        self.store_no_tokens = base / "no-token-data" / "sessions.db"
        _build_store(self.store_valid, variant="valid")
        _build_store(self.store_no_msg_table, variant="missing-table")
        _build_store(self.store_no_data_column, variant="missing-column")
        _build_store(self.store_no_tokens, variant="no-token-data")

    # -- corrida del wrapper (PD-15: SIEMPRE subproceso, nunca import) --

    def run_meter(self, *argv: str,
                  python_flags: tuple[str, ...] = (),
                  ) -> subprocess.CompletedProcess:
        if not METER_WRAPPER.is_file():
            self.fail(
                f"{FEATURE_ID} RED: el medidor `{METER_WRAPPER.name}` no "
                "existe aún — RED por CLI ausente (comportamiento "
                "ausente), nunca por ImportError: el test NO importa el "
                "módulo del medidor")
        cmd = [sys.executable, *python_flags, str(METER_WRAPPER), *argv]
        env = os.environ.copy()
        env.pop(STORE_ENV_VAR, None)  # sin fuga del entorno del host
        try:
            return subprocess.run(
                cmd, cwd=REPO_ROOT, env=env, capture_output=True,
                timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except FileNotFoundError:
            self.fail(
                f"{FEATURE_ID} RED: el medidor `{METER_WRAPPER.name}` no "
                "existe aún — RED por CLI ausente (comportamiento "
                "ausente), nunca por ImportError: el test NO importa el "
                "módulo del medidor")
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                f"PD-11 (acotado): el medidor no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — una medición acotada nunca puede "
                f"colgarse; timeout={exc!r}")

    def run_over_valid_store(self, *extra: str):
        proc = self.run_meter("--store", str(self.store_valid), *extra)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-15(a): con --store sobre el fixture válido el rc es 0; "
                f"stdout={proc.stdout[:300]!r} "
                f"stderr={proc.stderr[:300]!r}")
        doc = self.parse_stdout_json(proc, "PD-15(a)/(e)")
        return proc, doc

    def parse_stdout_json(self, proc: subprocess.CompletedProcess,
                          ctx: str) -> dict:
        out = proc.stdout.decode("utf-8", errors="replace")
        self.assertTrue(
            out.strip(),
            msg=f"{ctx}: la salida JSON por stdout está vacía "
                f"(stderr={proc.stderr[:200]!r})")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(
                f"{ctx}: la salida por stdout no es JSON parseable ({exc}); "
                f"stdout={out[:400]!r}")
        self.assertIsInstance(
            doc, dict,
            msg=f"{ctx}: el registro neutral es un documento JSON objeto")
        return doc

    def assert_no_metrics_in_stdout(self, proc: subprocess.CompletedProcess,
                                    ctx: str) -> None:
        """PD-2/PD-15(b): en fallo cerrado la salida NO trae NINGÚN número
        de métrica (ni 0 ni un objeto de métricas)."""
        out = proc.stdout.decode("utf-8", errors="replace").strip()
        if not out:
            return
        try:
            doc = json.loads(out)
        except json.JSONDecodeError:
            self.assertNotIn(
                METER_ID, out,
                msg=f"{ctx}: la salida de un fallo cerrado no porta el "
                    f"registro neutral; stdout={out[:400]!r}")
            return
        for key in ("meter", "measures", "buckets", "sessions"):
            self.assertNotIn(
                key, doc,
                msg=f"{ctx}: en fallo cerrado la salida no trae métricas "
                    f"(clave {key!r} presente); stdout={out[:400]!r}")

    def assert_fail_closed(self, proc: subprocess.CompletedProcess, ctx: str,
                           missing_name: str | None = None) -> None:
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"{ctx}: se esperaba rc != 0 (fallo cerrado); rc=0 con "
                f"stdout={proc.stdout[:300]!r}")
        self.assertTrue(
            err.strip(),
            msg=f"{ctx}: el diagnóstico del fallo cerrado va por stderr y "
                "está vacío")
        if missing_name is not None:
            self.assertIn(
                missing_name, err,
                msg=f"{ctx}: el diagnóstico por stderr debe NOMBRAR el "
                    f"elemento faltante {missing_name!r}; stderr={err!r}")
        self.assertNotIn(
            "Traceback", err,
            msg=f"{ctx}: fallo cerrado = diagnóstico, NO una excepción no "
                f"capturada; stderr={err!r}")
        self.assert_no_metrics_in_stdout(proc, ctx)

    # ------------------------------------------------------- PD-15 (C1)

    def test_pd15_invocation_contract(self):
        """PD-15: superficie de invocación mínima del wrapper — (a) --store
        → JSON por stdout con rc=0; (b) sin --store ni
        CDAD_CONTEXT_METER_STORE → rc!=0 y diagnóstico que NOMBRA el
        insumo faltante; (c) --json no-op aceptado; (d) --session y
        --limit aceptados, --limit 0 falla cerrado; (e) la salida es JSON
        parseable y va por stdout."""
        # (a) --store PATH → JSON por stdout, rc = 0.
        with self.subTest(punto="a-store-json-rc0"):
            proc, doc = self.run_over_valid_store()
            self.assertNotIn(
                "Traceback", proc.stderr.decode("utf-8", errors="replace"),
                msg="PD-15(a): éxito sin traceback en stderr")
        # (b) sin --store y sin la variable de entorno → fallo cerrado
        #     cuyo diagnóstico NOMBRA el insumo faltante (el store).
        with self.subTest(punto="b-sin-store-ni-env"):
            proc = self.run_meter()
            err = proc.stderr.decode("utf-8", errors="replace").lower()
            self.assert_fail_closed(proc, "PD-15(b)")
            self.assertIn(
                "store", err,
                msg="PD-15(b): el diagnóstico por stderr nombra el insumo "
                    f"faltante (el store, flag --store o variable "
                    f"{STORE_ENV_VAR}); stderr={proc.stderr!r}")
        # (c) --json se acepta como no-op: no cambia la salida.
        with self.subTest(punto="c-json-noop"):
            plain = self.run_meter("--store", str(self.store_valid))
            with_json = self.run_meter("--store", str(self.store_valid),
                                       "--json")
            self.assertEqual(
                plain.returncode, 0, msg="PD-15(c): corrida base rc=0")
            self.assertEqual(
                with_json.returncode, 0, msg="PD-15(c): --json aceptado")
            self.assertEqual(
                plain.stdout, with_json.stdout,
                msg="PD-15(c): --json es no-op — la salida es idéntica con "
                    "y sin el flag (JSON es el ÚNICO modo de salida)")
        # (d) --session (repetible) y --limit aceptados; --limit 0 →
        #     no mide ninguna y falla cerrado.
        with self.subTest(punto="d-session-repetible"):
            proc = self.run_meter("--store", str(self.store_valid),
                                  "--session", SESSION_A,
                                  "--session", SESSION_A2)
            self.assertEqual(
                proc.returncode, 0,
                msg=f"PD-15(d): --session es aceptado y repetible; "
                    f"stdout={proc.stdout[:200]!r} "
                    f"stderr={proc.stderr[:200]!r}")
            self.parse_stdout_json(proc, "PD-15(d) --session")
        with self.subTest(punto="d-limit-positivo"):
            proc = self.run_meter("--store", str(self.store_valid),
                                  "--limit", "1")
            self.assertEqual(
                proc.returncode, 0, msg="PD-15(d): --limit N aceptado")
            doc = self.parse_stdout_json(proc, "PD-15(d) --limit 1")
            self.assertLessEqual(
                len(doc.get("sessions", [])), 1,
                msg="PD-15(d): --limit 1 mide COMO MÁXIMO 1 sesión "
                    "(selección explícita y acotada, nunca un barrido)")
        with self.subTest(punto="d-limit-0-fallo-cerrado"):
            proc = self.run_meter("--store", str(self.store_valid),
                                  "--limit", "0")
            self.assert_fail_closed(proc, "PD-15(d) --limit 0")
        # (e) la salida es JSON parseable y va por stdout — cubierto por
        #     parse_stdout_json en (a)-(d) (json.loads sobre stdout).

    # --------------------------------------------- PD-1 + PD-16 (C1/C2)

    def test_pd1_pd16_neutral_record_keys_and_buckets(self):
        """PD-1/PD-16: el registro neutral trae las claves de nivel
        superior declaradas (schema_version, meter, run, window, sessions,
        roles, unknowns) y, por sesión, milestones/measures/buckets con
        sus claves requeridas; ninguna métrica aparece en dos cubos; el
        JSON NO contiene nombres de tablas ni de columnas del runtime."""
        proc, doc = self.run_over_valid_store()
        text = proc.stdout.decode("utf-8", errors="replace")
        for name in RUNTIME_NAMES:
            self.assertNotIn(
                name, text,
                msg=f"PD-1/INV-3: el registro neutral NO contiene el nombre "
                    f"de runtime {name!r} — el adaptador es el único "
                    "traductor")
        for key in REQUIRED_TOP_KEYS:
            self.assertIn(key, doc, msg=f"PD-16: clave requerida {key!r}")
        self.assertEqual(
            doc["meter"], METER_ID,
            msg="PD-16: meter declara el contrato del registro neutral")
        self.assertEqual(
            doc["schema_version"], 1,
            msg="PD-16: schema_version = 1 (versión del registro neutral)")
        run = doc["run"]
        for key in REQUIRED_RUN_KEYS:
            self.assertIn(
                key, run,
                msg=f"PD-16: run trae {key!r} (store_ref, runtime_version, "
                    "schema)")
        self.assertIn(
            run["schema"], ("recognized", "unknown"),
            msg="PD-16: run.schema ∈ {recognized, unknown}")
        self.assertEqual(
            run["schema"], "recognized",
            msg="PD-1: el fixture válido (esquema observado completo) se "
                "reconoce — un lector que no reconoce el esquema "
                "observado tampoco pasa PD-2 con stores reales")
        window = doc["window"]
        for key in REQUIRED_WINDOW_KEYS:
            self.assertIn(
                key, window,
                msg=f"PD-16: window trae {key!r} (ventana y corte "
                    "explícitos y reproducibles)")
        self.assertIsInstance(
            doc["sessions"], list, msg="PD-16: sessions[] es lista")
        self.assertTrue(
            doc["sessions"], msg="PD-16: al menos una sesión medida")
        self.assertIsInstance(doc["roles"], list,
                              msg="PD-1: roles[] existe (agregado por rol)")
        self.assertTrue(
            doc["roles"],
            msg="PD-1: el agregado por rol existe para el fixture válido")
        for entry in doc["roles"]:
            self.assertIsInstance(entry, dict, msg="PD-1: entrada de rol")
            for key in ("role", "sums", "distributions"):
                self.assertIn(
                    key, entry,
                    msg=f"PD-1: el agregado por rol trae {key!r}")
        self.assertIsInstance(
            doc["unknowns"], list, msg="PD-16: unknowns[] es lista")
        for session in doc["sessions"]:
            for key in REQUIRED_SESSION_KEYS:
                self.assertIn(
                    key, session,
                    msg=f"PD-16: la sesión trae la clave declarada {key!r}")
            milestones = session["milestones"]
            self.assertIsInstance(
                milestones, dict, msg="PD-16: milestones es objeto")
            for key in REQUIRED_MILESTONE_KEYS:
                self.assertIn(
                    key, milestones,
                    msg=f"PD-16: milestones trae {key!r} (ambos hitos como "
                        "clave presente, aunque queden ausentes)")
                milestone = milestones[key]
                status = milestone.get("status")
                self.assertIn(
                    status, MILESTONE_STATUS_VALUES,
                    msg=f"PD-16: {key}.status ∈ observed|absent|unknown")
                if status == "observed":
                    for sub in ("position", "time_relative"):
                        self.assertIn(
                            sub, milestone,
                            msg=f"PD-16: {key} observado trae {sub!r}")
                else:
                    self.assertIn(
                        "cause", milestone,
                        msg=f"PD-16: {key} ausente/desconocido trae causa")
            measures = session["measures"]
            self.assertIsInstance(measures, dict,
                                  msg="PD-16: measures es objeto")
            for key in REQUIRED_MEASURE_KEYS:
                self.assertIn(
                    key, measures,
                    msg=f"PD-16: measures trae la medida requerida {key!r}")
            leaves = dict(_measure_leaves(measures))
            self.assertTrue(
                leaves, msg="PD-16: hay métricas con bucket declarado")
            assignment: dict[str, set] = {}
            for name, leaf in leaves.items():
                for field in MEASURE_FIELDS:
                    self.assertIn(
                        field, leaf,
                        msg=f"PD-16: la medida {name!r} trae {field!r} "
                            "(unit y provenance obligatorias)")
                bucket = leaf["bucket"]
                self.assertIn(
                    bucket, BUCKET_VALUES,
                    msg=f"PD-16: la medida {name!r} declara un cubo válido")
                assignment.setdefault(name, set()).add(bucket)
            buckets = session["buckets"]
            self.assertIsInstance(buckets, dict,
                                  msg="PD-16: buckets es objeto")
            for key in REQUIRED_BUCKET_KEYS:
                self.assertIn(
                    key, buckets,
                    msg=f"PD-16: buckets trae {key!r} (observed, estimated, "
                        "unknown)")
            for name, assigned in assignment.items():
                self.assertEqual(
                    len(assigned), 1,
                    msg=f"PD-1/INV-4: NINGUNA métrica aparece en dos cubos "
                        f"({name!r} declara {sorted(assigned)})")
            for bucket_name, members in buckets.items():
                if isinstance(members, list):
                    for member in members:
                        if isinstance(member, str) and member in assignment:
                            self.assertEqual(
                                assignment[member], {bucket_name},
                                msg=f"PD-1: la métrica {member!r} aparece "
                                    f"en buckets[{bucket_name!r}] pero su "
                                    "cubo declarado es "
                                    f"{sorted(assignment[member])}")

    # --------------------------------------------- PD-2 (fallo cerrado)

    def test_pd2_fail_closed_unknown_schema(self):
        """PD-2: con un fixture al que le FALTA un elemento que hace
        inconstruible el registro (la tabla session_message entera, o su
        columna `data`) el proceso devuelve rc!=0, el diagnóstico por
        stderr NOMBRA el elemento faltante, y la salida no trae NINGÚN
        número de métrica; el error no es una excepción no capturada."""
        cases = (
            ("tabla-entera-session_message", self.store_no_msg_table,
             "session_message"),
            ("columna-data-de-session_message", self.store_no_data_column,
             "data"),
        )
        for label, store, missing in cases:
            with self.subTest(variante=label):
                proc = self.run_meter("--store", str(store))
                self.assert_fail_closed(
                    proc, f"PD-2 ({label})", missing_name=missing)

    # --------------------------------------- PD-3 (sin métricas fabricadas)

    def test_pd3_no_fabricated_metrics(self):
        """PD-3: el documento no trae un límite de contexto o ventana
        derivado del input (ni conversión bytes→tokens), y la lista
        unknowns nombra la causa de lo no observable."""
        proc, doc = self.run_over_valid_store()
        for key, value in _walk_kv(doc):
            self.assertNotEqual(
                key, "context_limit",
                msg="PD-3: el registro no porta un `context_limit` "
                    "derivado del input (ningún límite de contexto se "
                    "fabrica)")
            if "limit" in key.lower():
                self.assertNotIsInstance(
                    value, (int, float),
                    msg=f"PD-3: ningún límite FABRICADO con valor numérico "
                        f"(clave {key!r} = {value!r})")
        for key in ("total_output", "max_output"):
            leaf = dict(_measure_leaves(doc["sessions"][0]["measures"]))
            self.assertIn(
                key, leaf,
                msg=f"PD-3 (precondición PD-16): la medida {key!r} existe")
            unit = str(leaf[key].get("unit", "")).lower()
            self.assertNotIn(
                "token", unit,
                msg=f"PD-3/INV-2: {key} se mide en caracteres Unicode — "
                    "bytes/caracteres NUNCA se convierten a tokens "
                    f"(unit={unit!r})")
            self.assertNotIn(
                "byte", unit,
                msg=f"PD-3/INV-2: {key} no se reporta en bytes (unit="
                    f"{unit!r})")
        unknowns = doc["unknowns"]
        self.assertIsInstance(unknowns, list, msg="PD-3: unknowns[] lista")
        self.assertTrue(
            unknowns,
            msg="PD-3/PD-4: en el fixture válido (cache_write no reportado, "
                "cost nulo) unknowns[] nombra la causa de lo no observable")
        for entry in unknowns:
            if isinstance(entry, dict):
                self.assertTrue(
                    any(isinstance(v, str) and v.strip()
                        for v in entry.values()),
                    msg=f"PD-3: cada unknown nombra una causa textual; "
                        f"entry={entry!r}")
            else:
                self.assertIsInstance(
                    entry, str,
                    msg=f"PD-3: cada unknown nombra una causa textual; "
                        f"entry={entry!r}")

    # ------------------------------- PD-4 (desconocido, nunca cero)

    def test_pd4_unknown_never_zero(self):
        """PD-4: con un fixture donde el proveedor no reporta cache_write
        (valor 0 en las filas) el registro lo informa como unknown con
        causa, NUNCA como 0; un cost nulo es unknown."""
        proc, doc = self.run_over_valid_store()
        unknown_seen = False
        for node in _walk_dicts(doc):
            if "bucket" not in node or "value" not in node:
                continue
            bucket = node["bucket"]
            self.assertIn(
                bucket, BUCKET_VALUES,
                msg=f"PD-4: cubo válido declarado ({bucket!r})")
            value = node["value"]
            unit = str(node.get("unit", "")).lower()
            if value is None:
                unknown_seen = True
                self.assertEqual(
                    bucket, "unknown",
                    msg=f"PD-4: un valor nulo es unknown con causa, NUNCA "
                        f"observado ni estimado; nodo={node!r}")
            elif isinstance(value, (int, float)) and not isinstance(
                    value, bool):
                self.assertGreaterEqual(
                    value, 0, msg=f"PD-4: sin tokens negativos "
                    f"(nodo={node!r})")
                if bucket == "observed" and "token" in unit:
                    self.assertGreater(
                        value, 0,
                        msg="PD-4: en este fixture (cache_write=0 en filas "
                            "porque el proveedor NO lo reporta, "
                            "cache_read>0, cost nulo) NINGUNA métrica de "
                            "tokens observada puede ser 0 — lo no "
                            "reportado es unknown con causa, NUNCA 0; "
                            f"nodo={node!r}")
        self.assertTrue(
            unknown_seen,
            msg="PD-4: el registro porta al menos una métrica unknown "
                "(cache_write no reportado y/o cost nulo)")
        self.assertTrue(
            doc["unknowns"],
            msg="PD-4: la causa de lo no reportado queda en unknowns[]")

    # ---------------- PD-11 (solo lectura, determinismo, JSON, stdlib)

    def _snapshot_store_dir(self, store: Path) -> dict:
        return {
            p.name: (p.stat().st_size, p.stat().st_mtime_ns)
            for p in sorted(store.parent.iterdir()) if p.is_file()
        }

    def test_pd11_readonly_deterministic_single_json_stdlib(self):
        """PD-11: abrir el store no cambia tamaño ni mtime del fixture ni
        crea archivos nuevos en el directorio; dos corridas sobre el mismo
        fixture producen salida byte-idéntica; la salida es JSON; y no hay
        dependencias fuera de la biblioteca estándar."""
        before = self._snapshot_store_dir(self.store_valid)
        proc1 = self.run_meter("--store", str(self.store_valid))
        self.assertEqual(
            proc1.returncode, 0,
            msg=f"PD-11 (precondición): corrida exitosa; "
                f"stdout={proc1.stdout[:200]!r} stderr={proc1.stderr[:200]!r}")
        out1 = proc1.stdout
        self.parse_stdout_json(proc1, "PD-11: la salida es JSON")
        proc2 = self.run_meter("--store", str(self.store_valid))
        self.assertEqual(
            proc2.returncode, 0, msg="PD-11 (precondición): segunda corrida")
        self.assertEqual(
            out1, proc2.stdout,
            msg="PD-11: dos corridas sobre el mismo fixture producen "
                "salida byte-idéntica (determinismo)")
        after = self._snapshot_store_dir(self.store_valid)
        self.assertEqual(
            before, after,
            msg="PD-11/INV-1: abrir el store NO cambia el tamaño ni el "
                "mtime del fixture ni de sus archivos -wal/-shm y NO crea "
                f"archivos nuevos; antes={before} después={after}")
        # stdlib only (INV-6): run aislado (-I: sin env ni user-site;
        # -S: sin site-packages de terceros) produce la MISMA salida.
        proc3 = self.run_meter("--store", str(self.store_valid),
                               python_flags=("-I", "-S"))
        self.assertEqual(
            proc3.returncode, 0,
            msg="PD-11/INV-6: el medidor funciona SOLO con la biblioteca "
                f"estándar (run aislado -I -S); stdout={proc3.stdout[:200]!r} "
                f"stderr={proc3.stderr[:200]!r}")
        self.assertEqual(
            out1, proc3.stdout,
            msg="PD-11: en modo aislado la salida es la misma (sin "
                "dependencias fuera de stdlib)")

    # --------------------------- PD-13 (medición opcional, no en gates)

    def test_pd13_no_tokens_session_valid_record(self):
        """PD-13: una sesión sin datos de tokens produce un registro VÁLIDO
        con esos cubos en unknown, no un fallo (la medición es opcional)."""
        proc = self.run_meter("--store", str(self.store_no_tokens))
        self.assertEqual(
            proc.returncode, 0,
            msg="PD-13: una sesión sin datos de tokens produce un registro "
                "VÁLIDO (rc=0), NO un fallo cerrado; "
                f"stdout={proc.stdout[:300]!r} stderr={proc.stderr[:300]!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="PD-13: éxito sin traceback")
        doc = self.parse_stdout_json(proc, "PD-13")
        for key in REQUIRED_TOP_KEYS:
            self.assertIn(key, doc,
                          msg=f"PD-13: registro válido trae {key!r}")
        self.assertTrue(
            doc["sessions"], msg="PD-13: la sesión sin tokens es medida")
        for session in doc["sessions"]:
            for key in ("milestones", "measures", "buckets"):
                self.assertIn(
                    key, session,
                    msg=f"PD-13: la sesión sin tokens trae {key!r}")
            for key in REQUIRED_MEASURE_KEYS:
                self.assertIn(
                    key, session["measures"],
                    msg=f"PD-13: la medida requerida {key!r} existe "
                        "(valor unknown, no ausente)")
            for node in _walk_dicts(session["measures"]):
                if "bucket" not in node or "value" not in node:
                    continue
                unit = str(node.get("unit", "")).lower()
                if "token" in unit and isinstance(
                        node["value"], (int, float)):
                    self.assertEqual(
                        node["bucket"], "unknown",
                        msg="PD-13/INV-4: sin datos de tokens, NINGUNA "
                            "métrica de tokens es observada/estimada con "
                            f"número — el cubo es unknown; nodo={node!r}")
        self.assertTrue(
            doc["unknowns"],
            msg="PD-13: la ausencia de tokens queda como unknown con causa")


if __name__ == "__main__":
    unittest.main()
