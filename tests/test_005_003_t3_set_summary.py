#!/usr/bin/env python3
"""005-003 T3 RED — resumen del conjunto (multi-sesión) + regla del documento
multiplexado (R4/V3) + cierre de D11 (PD-6, PD-12; INV-5, INV-8).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.6 (resumen del conjunto,
  contrato `set-summary-v1`, conjunto mínimo de claves C2, regla del documento
  multiplexado R4/V3), §3 PD-6/PD-12, §4 INV-5/INV-8, §10 D12.
- docs/specs/005-003-orientation-reduction/plan.md §3 (ficha T3) y §4 (T3).

ORÁCULOS (caja negra; el módulo del medidor NUNCA se importa y la
implementación NUNCA se lee):
- puntos 1 y D11 (1)/(2): la SALIDA del WRAPPER fino
  `scripts/cdad_context_meter.py`, invocado SIEMPRE por subproceso
  (sys.executable). El contrato observable es el JSON por stdout, el rc y el
  diagnóstico por stderr.
- puntos 2 y D11 (4): oráculo DOCUMENTAL sobre la ruta declarada
  `skills/cdad-cycle/references/context-meter.md` (el test lee el reference en
  runtime y afirma que el documento declara la regla con sus dos partes, nunca
  buscando una frase literal del prompt).

INTERFAZ DECLARADA POR ESTE TEST (el implementer la satisface leyendo el test;
el orquestador la fija en este paquete porque el test-writer no ve el código):

1. BANDERA NUEVA `--set-summary` (booleana, sin valor). Sobre una corrida
   multi-sesión emite el DOCUMENTO ADITIVO SEPARADO del resumen del conjunto
   (`meter == "set-summary-v1"`) por stdout, con el conjunto mínimo de claves de
   §2.6: `run` `{store_ref, runtime_version, schema}`, `sessions_included`
   (referencias HASHEADAS), `coverage` `{sessions_reporting, sessions_total,
   cause}`, `milestones` `{first_resume, first_dispatch}`, `magnitudes`
   (entradas `{value, unit, bucket, sessions_reporting, sessions_total, cause}`),
   `detail_ref`, `detail_flag` y `unknowns[]`. SIN la bandera la salida es la de
   hoy (registro neutral por sesión, `context-meter-v1`): la adición NO cambia
   el comportamiento existente (PD-7/INV-5, byte-congelado).
2. El detalle por sesión NO se emite por defecto en el resumen; se pide con la
   bandera declarada en `detail_flag` (fijada: `--detail`), que restaura el
   detalle por sesión (nodos `measures`).
3. Una magnitud sin cobertura total (en un fixture donde una sesión no reporta
   tokens) es `unknown` con `cause` y `value: null` — NUNCA un subtotal parcial
   presentado como total y NUNCA `0` (INV-9/§2.6-C2).

RED hoy: el resumen y la regla NO existen todavía. `--set-summary` es una
bandera DESCONOCIDA (el wrapper devuelve rc=2) y `context-meter.md` no declara
la regla del total (R4). Cada aserción falla por `AssertionError` de CONTRATO
(rc / documento / regla ausente), nunca por ImportError, sintaxis ni error de
E/S no capturado: el test NO importa el módulo del medidor.

Fixtures 100% SINTÉTICOS y autocontenidos: bases SQLite armadas por el test en
tempdirs (contenido inventado, ids `sess-fixture-*`, modelo `model-alpha`,
provider `prov-a`). La base real de sesiones del runtime JAMÁS se abre ni se
copia (INV-6/PD-10): el test NO usa rutas de este host.

Mapeo test → postcondición/borde:
  test_pd6_set_summary_minimal_keys_and_no_detail_by_default
      -> PD-6/C2 (documento aditivo `set-summary-v1` con el conjunto mínimo de
         claves; referencias hasheadas; el detalle por sesión NO se emite)
  test_pd6_set_summary_detail_flag_restores_per_session_detail
      -> PD-6 (la bandera declarada en `detail_flag` — `--detail` — restaura el
         detalle por sesión)
  test_pd6_partial_magnitude_is_unknown_not_partial_total
      -> PD-6 borde (magnitud sin cobertura total → unknown/null/causa; nunca un
         subtotal parcial como total; nunca 0)
  test_pd6_set_summary_is_additive_existing_records_unchanged
      -> PD-6/INV-5 (la adición es aditiva: el registro neutral por sesión no
         cambia de comportamiento)
  test_r4_reference_declares_total_bound_by_n_times_session_limit
      -> PD-6/R4/V3 elemento (a) (el total es ≤ N × el límite por sesión)
  test_r4_reference_declares_limit_is_per_session_document
      -> PD-6/R4/V3 elemento (b) (el límite normativo es POR DOCUMENTO DE SESIÓN)
  test_d11_1_controlled_temp_base_byte_identical_after_read
      -> PD-12/D11-(1) (ausencia de escrituras sobre base temporal controlada:
         el documento de esa base queda byte-idéntico)
  test_d11_2_read_completes_and_results_expected_with_concurrent_writer
      -> PD-12/D11-(2) (concurrencia: la lectura se completa y sus resultados son
         los esperados con otro escritor activo durante la lectura)
  test_d11_4_real_base_never_written_rule_declared_and_absent_in_tests
      -> PD-12/D11-(4) (regla declarada en `context-meter.md`: nunca se escribe en
         la base real para demostrar que está prohibido; ausencia verificable en
         las pruebas)
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
METER_WRAPPER = REPO_ROOT / "scripts" / "cdad_context_meter.py"  # wrapper fino
CONTEXT_METER_REF = (REPO_ROOT / "skills" / "cdad-cycle" / "references"
                     / "context-meter.md")
TESTS_DIR = REPO_ROOT / "tests"

FEATURE_ID = "005-003-orientation-reduction"
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"        # sin fuga del entorno del host
REAL_STORE_ENV = "CDAD_CONTEXT_METER_REAL_STORE"  # base real (JAMÁS se abre acá)
CLI_TIMEOUT_S = 120

SET_SUMMARY_CONTRACT = "set-summary-v1"
NEUTRAL_METER_ID = "context-meter-v1"
SET_SUMMARY_FLAG = "--set-summary"   # bandera declarada por este test (punto 1)
DETAIL_FLAG = "--detail"             # fijada por la spec §2.6 (detail_flag)

# Conjunto mínimo de claves del resumen (§2.6-C2).
SET_SUMMARY_KEYS = (
    "meter", "run", "sessions_included", "coverage", "milestones",
    "magnitudes", "detail_ref", "detail_flag", "unknowns",
)
RUN_KEYS = ("store_ref", "runtime_version", "schema")
COVERAGE_KEYS = ("sessions_reporting", "sessions_total", "cause")
MAGNITUDE_KEYS = ("value", "unit", "bucket", "sessions_reporting",
                  "sessions_total", "cause")
MILESTONE_KEYS = ("first_resume", "first_dispatch")
MILESTONE_STATUS = ("observed", "absent", "unknown")
BUCKET_VALUES = ("observed", "estimated", "unknown")

# --- dispositivos sintéticos (inventados; nada de la base real) ---
ROLE_SYNTH = "cdad-orchestrator"
MODEL_SYNTH = '{"id":"model-alpha","providerID":"prov-a"}'
S1_ID = "sess-fixture-t3-alpha"     # sesión con tokens y un resume
S2_ID = "sess-fixture-t3-beta"      # sesión SIN tokens (cobertura parcial)
STABLE_ID = "sess-fixture-t3-stable"  # sesión estable de la prueba de concurrencia
NOISE_ID = "sess-fixture-t3-noise"    # sesión de ruido del escritor concurrente

BASE_MS = 1_760_000_000_000  # epoch ms SINTÉTICO fijo (determinismo)
STEP_MS = 30_000             # 30 s < umbral default 60 min → un solo tramo
STABLE_CALLS = 3             # llamadas de herramienta de la sesión estable

CONTINUITY_CLI_STEM = "python3 skills/cdad-cycle/scripts/cdad_continuity.py"
RESUME_REAL_CMD = CONTINUITY_CLI_STEM + " resume --project-root ."


# ------------------------------------------------------------- DDL/fixtures

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
    return json.dumps({"time": ms, "text": text}, sort_keys=True)


def _tool_part(name: str, text: str, ms: int, *, input_args: dict,
               part_id: str) -> dict:
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": {
            "status": "completed",
            "input": input_args,
            "content": [{"type": "text", "text": text}],
            "metadata": {"status": "completed", "truncated": False, "exit": 0},
        },
        "time": {"created": ms, "ran": ms, "completed": ms},
    }


def _assistant_data(agent: str, model: str, ms: int, parts: list,
                    tokens, cost) -> str:
    doc = {
        "time": {"created": ms, "streamed": ms, "completed": ms},
        "agent": agent, "model": model, "content": parts, "cost": cost,
    }
    if tokens is not None:
        tin, tout, treason, tread, twrite = tokens
        doc["tokens"] = {"input": tin, "output": tout, "reasoning": treason,
                         "cache": {"read": tread, "write": twrite}}
    return json.dumps(doc, sort_keys=True)


def _insert_msg(conn, sid: str, seq: int, mtype: str, data: str, ms: int) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, mtype, seq, ms, ms, data))


def _insert_session(conn, sid: str, agent: str, model: str, t0: int, t_end: int,
                    sums, cost) -> None:
    if sums is None:
        tin = tout = treason = tread = twrite = None
    else:
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


def _build_store(path: Path, populate, *, wal: bool = False) -> None:
    """Store SQLite sintético con el ESQUEMA observado (discovery §1.2–§1.6)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if wal:
        conn = sqlite3.connect(str(path))
        try:
            conn.execute(SESSION_V2_DDL)
            conn.execute(SESSION_MESSAGE_DDL)
            populate(conn)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.commit()
        finally:
            conn.close()
        return
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


def _populate_multi(conn) -> None:
    """Dos sesiones: S1 con tokens y un resume; S2 SIN tokens (fuerza cobertura
    parcial de las magnitudes) y sin hitos."""
    # --- S1: 3 llamadas (read, shell, shell=resume), tokens por paso ---
    t0 = BASE_MS + 1_000_000
    _insert_msg(conn, S1_ID, 1, "user", _user_data(t0, "arranque s1"), t0)
    sum_in = sum_out = sum_reason = sum_cread = 0
    for i, (name, args) in enumerate((
            ("read", {"path": "/fixture/dir/a.md"}),
            ("shell", {"command": "echo fixture"}),
            ("shell", {"command": RESUME_REAL_CMD}),
    ), start=1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        tin, tout, treason, tread = 100, 40, 5, 200
        sum_in += tin; sum_out += tout; sum_reason += treason; sum_cread += tread
        _insert_msg(conn, S1_ID, seq, "assistant", _assistant_data(
            ROLE_SYNTH, MODEL_SYNTH, ms,
            [_tool_part(name, "o" * 50, ms, input_args=args,
                        part_id=f"p{seq}")],
            (tin, tout, treason, tread, 0), 0.0), ms)
    _insert_session(conn, S1_ID, ROLE_SYNTH, MODEL_SYNTH, t0,
                    t0 + 3 * STEP_MS,
                    (sum_in, sum_out, sum_reason, sum_cread, 0), 0.0)

    # --- S2: SIN tokens (columnas NULL, assistant sin la clave `tokens`) ---
    t0b = BASE_MS + 5_000_000
    _insert_msg(conn, S2_ID, 1, "user", _user_data(t0b, "arranque s2"), t0b)
    _insert_msg(conn, S2_ID, 2, "assistant", _assistant_data(
        ROLE_SYNTH, MODEL_SYNTH, t0b + STEP_MS,
        [{"type": "text", "text": "respuesta s2 sin tokens"}], None, None),
        t0b + STEP_MS)
    _insert_session(conn, S2_ID, ROLE_SYNTH, MODEL_SYNTH, t0b,
                    t0b + STEP_MS, None, None)


def _populate_single(conn) -> None:
    t0 = BASE_MS + 2_000_000
    _insert_msg(conn, S1_ID, 1, "user", _user_data(t0, "arranque s1"), t0)
    _insert_msg(conn, S1_ID, 2, "assistant", _assistant_data(
        ROLE_SYNTH, MODEL_SYNTH, t0 + STEP_MS,
        [{"type": "text", "text": "respuesta s1"}], (100, 40, 5, 200, 0), 0.0),
        t0 + STEP_MS)
    _insert_session(conn, S1_ID, ROLE_SYNTH, MODEL_SYNTH, t0, t0 + STEP_MS,
                    (100, 40, 5, 200, 0), 0.0)


def _populate_concurrency(conn) -> None:
    """Sesión estable (3 llamadas) + sesión de ruido (donde escribe el otro
    escritor). La lectura se acota con `--session` a la estable."""
    t0 = BASE_MS + 3_000_000
    _insert_msg(conn, STABLE_ID, 1, "user", _user_data(t0, "arranque estable"),
                t0)
    for i in range(1, STABLE_CALLS + 1):
        seq = 1 + i
        ms = t0 + i * STEP_MS
        _insert_msg(conn, STABLE_ID, seq, "assistant", _assistant_data(
            ROLE_SYNTH, MODEL_SYNTH, ms,
            [_tool_part("read", "o" * 30, ms,
                        input_args={"path": f"/fixture/dir/s{i}.md"},
                        part_id=f"sp{seq}")],
            (100, 40, 5, 200, 0), 0.0), ms)
    _insert_session(conn, STABLE_ID, ROLE_SYNTH, MODEL_SYNTH, t0,
                    t0 + STABLE_CALLS * STEP_MS, (300, 120, 15, 600, 0), 0.0)
    # Sesión de ruido (vacía de mensajes; el escritor le agrega filas).
    _insert_session(conn, NOISE_ID, ROLE_SYNTH, MODEL_SYNTH, t0, t0, None, None)


# ---------------------------------------------------------------- helpers

def _run_meter(*argv: str, timeout_s: int = CLI_TIMEOUT_S
               ) -> subprocess.CompletedProcess:
    """Corre el wrapper por subproceso (NUNCA import)."""
    assert METER_WRAPPER.is_file(), (
        f"{FEATURE_ID}: el medidor `{METER_WRAPPER.name}` no existe aún — RED "
        "por CLI ausente (comportamiento ausente), nunca por ImportError")
    cmd = [sys.executable, str(METER_WRAPPER), *argv]
    env = os.environ.copy()
    env.pop(STORE_ENV_VAR, None)
    env.pop(REAL_STORE_ENV, None)  # la base real JAMÁS se usa acá
    return subprocess.run(
        cmd, cwd=REPO_ROOT, env=env, capture_output=True, timeout=timeout_s,
        stdin=subprocess.DEVNULL)


def _parse_json(proc: subprocess.CompletedProcess, ctx: str) -> dict:
    out = proc.stdout.decode("utf-8", errors="replace")
    if not out.strip():
        raise AssertionError(
            f"{ctx}: stdout vacío (rc={proc.returncode}); "
            f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r}")
    try:
        doc = json.loads(out)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{ctx}: stdout no es JSON parseable ({exc}): {out[:400]!r}") from exc
    assert isinstance(doc, dict), f"{ctx}: el documento no es un objeto JSON"
    return doc


def _set_summary_doc(store: Path, *extra: str) -> dict:
    """Corrida multi-sesión con la bandera declarada `--set-summary`.

    RED: hoy la bandera no existe (rc=2) → AssertionError de CONTRATO que nombra
    el resumen ausente, nunca un error no capturado.
    """
    proc = _run_meter("--store", str(store), SET_SUMMARY_FLAG, *extra)
    assert proc.returncode == 0, (
        "PD-6 violada: la corrida multi-sesión con la bandera declarada "
        f"`{SET_SUMMARY_FLAG}` debe emitir el resumen del conjunto "
        f"(`{SET_SUMMARY_CONTRACT}`, rc=0); rc={proc.returncode}; "
        f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r} — "
        "el resumen y su bandera NO existen todavía")
    doc = _parse_json(proc, f"PD-6 {SET_SUMMARY_CONTRACT}")
    assert doc.get("meter") == SET_SUMMARY_CONTRACT, (
        f"PD-6 violada: el documento del resumen declara `meter` = "
        f"`{SET_SUMMARY_CONTRACT}` (fue {doc.get('meter')!r})")
    return doc


def _walk_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_dicts(item)


def _measure_value(session: dict, key: str) -> object:
    leaf = (session.get("measures") or {}).get(key)
    assert isinstance(leaf, dict), (
        f"la medida {key!r} no existe en la salida (fue {leaf!r})")
    return leaf.get("value")


def _snapshot_bytes(store: Path) -> dict:
    """Bytes del documento de la base y sus -wal/-shm (sin leer la real)."""
    snap = {}
    for name in (store.name, store.name + "-wal", store.name + "-shm"):
        p = store.parent / name
        if p.exists() and p.is_file():
            snap[name] = p.read_bytes()
    return snap


# ===================================================================== PD-6

def test_pd6_set_summary_minimal_keys_and_no_detail_by_default() -> None:
    """PD-6/C2: una corrida multi-sesión con `--set-summary` emite el documento
    aditivo separado (`set-summary-v1`) con el conjunto mínimo de claves; las
    referencias están hasheadas (ni el id crudo ni la ruta del store); el
    detalle por sesión NO se emite por defecto."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        store = Path(tmp) / "multi" / "sessions.db"
        _build_store(store, _populate_multi)
        proc = _run_meter("--store", str(store), SET_SUMMARY_FLAG)
        assert proc.returncode == 0, (
            "PD-6 violada: la corrida multi-sesión con `--set-summary` debe "
            f"emitir el resumen (rc=0); rc={proc.returncode}; "
            f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r} — "
            "el resumen NO existe todavía")
        doc = _parse_json(proc, "PD-6 set-summary")

    assert doc["meter"] == SET_SUMMARY_CONTRACT, (
        f"PD-6 violada: `meter` = `{SET_SUMMARY_CONTRACT}` (fue "
        f"{doc['meter']!r})")
    missing = [k for k in SET_SUMMARY_KEYS if k not in doc]
    assert not missing, (
        f"PD-6/C2 violada: faltan claves del conjunto mínimo de §2.6: {missing}")

    # run: referencia HASHEADA del store (nunca ruta absoluta), versión y schema.
    run = doc["run"]
    assert isinstance(run, dict), f"PD-6: `run` es un objeto (fue {run!r})"
    for key in RUN_KEYS:
        assert key in run, f"PD-6: `run` trae {key!r}"
    assert isinstance(run["store_ref"], str) and run["store_ref"].strip(), (
        f"PD-6: `run.store_ref` es una referencia no vacía (fue "
        f"{run['store_ref']!r})")
    assert str(store) not in run["store_ref"], (
        "PD-6/INV-6 violada: `run.store_ref` porta la ruta absoluta del store "
        f"(debe ser una referencia hasheada): {run['store_ref']!r}")
    assert run["schema"] in ("recognized", "unknown"), (
        f"PD-6: `run.schema` ∈ {{recognized, unknown}} (fue {run['schema']!r})")

    # sessions_included: referencias hasheadas (ni el id crudo).
    inc = doc["sessions_included"]
    assert isinstance(inc, list) and inc, (
        f"PD-6: `sessions_included` es una lista no vacía (fue {inc!r})")
    for ref in inc:
        assert isinstance(ref, str) and ref.strip(), (
            f"PD-6: cada `sessions_included` es una referencia (fue {ref!r})")
    stdout_text = proc.stdout.decode("utf-8", errors="replace")
    for raw_id in (S1_ID, S2_ID):
        assert raw_id not in stdout_text, (
            "PD-6/INV-6 violada: el resumen porta un identificador crudo de "
            f"sesión ({raw_id!r}); las referencias deben estar hasheadas")

    # coverage declarada: un subconjunto nunca se presenta como el conjunto.
    cov = doc["coverage"]
    assert isinstance(cov, dict), f"PD-6: `coverage` es un objeto (fue {cov!r})"
    for key in COVERAGE_KEYS:
        assert key in cov, f"PD-6: `coverage` trae {key!r}"
    assert cov["sessions_total"] == 2, (
        f"PD-6: `coverage.sessions_total` = 2 (el fixture tiene 2 sesiones; "
        f"fue {cov['sessions_total']!r})")
    assert isinstance(cov["sessions_reporting"], int), (
        f"PD-6: `coverage.sessions_reporting` es entero (fue "
        f"{cov['sessions_reporting']!r})")
    assert 0 <= cov["sessions_reporting"] <= cov["sessions_total"], (
        f"PD-6: la cobertura declarada no excede el total (fue {cov!r})")

    # milestones del conjunto: misma forma que el registro neutral.
    ms = doc["milestones"]
    assert isinstance(ms, dict), f"PD-6: `milestones` es un objeto (fue {ms!r})"
    for key in MILESTONE_KEYS:
        assert key in ms, f"PD-6: `milestones` trae {key!r}"
        mt = ms[key]
        assert isinstance(mt, dict), f"PD-6: {key} es un objeto (fue {mt!r})"
        assert mt.get("status") in MILESTONE_STATUS, (
            f"PD-6: {key}.status ∈ {MILESTONE_STATUS} (fue {mt.get('status')!r})")
        if mt.get("status") == "observed":
            assert "position" in mt and "time_relative" in mt, (
                f"PD-6: {key} observado trae position y time_relative (fue {mt!r})")
        else:
            assert "cause" in mt, (
                f"PD-6/INV-9: {key} ausente/desconocido trae causa (fue {mt!r})")

    # magnitudes: entradas declaradas con cubo y cobertura.
    mags = doc["magnitudes"]
    assert isinstance(mags, dict) and mags, (
        f"PD-6: `magnitudes` es un objeto no vacío (fue {mags!r})")
    for name, entry in mags.items():
        assert isinstance(entry, dict), (
            f"PD-6: la magnitud {name!r} es un objeto (fue {entry!r})")
        missing_e = [k for k in MAGNITUDE_KEYS if k not in entry]
        assert not missing_e, (
            f"PD-6/C2 violada: la magnitud {name!r} trae {missing_e}")
        assert entry["bucket"] in BUCKET_VALUES, (
            f"PD-6: la magnitud {name!r} declara un cubo válido "
            f"({BUCKET_VALUES}; fue {entry['bucket']!r})")

    # detail_ref (referencias, no el detalle) y detail_flag.
    assert doc["detail_ref"], (
        f"PD-6: `detail_ref` trae referencias al detalle (fue {doc['detail_ref']!r})")
    assert doc["detail_flag"] == DETAIL_FLAG, (
        f"PD-6 violada: `detail_flag` = {DETAIL_FLAG!r} (fue "
        f"{doc['detail_flag']!r})")

    # unknowns[] declarado.
    assert isinstance(doc["unknowns"], list), (
        f"PD-6: `unknowns` es una lista (fue {doc['unknowns']!r})")

    # El detalle por sesión NO se emite por defecto: ningún nodo `measures`.
    detail_nodes = [n for n in _walk_dicts(doc) if "measures" in n]
    assert not detail_nodes, (
        "PD-6 violada: el resumen emite el detalle por sesión por defecto "
        f"(nodos `measures`: {len(detail_nodes)}); se pide con "
        f"`{DETAIL_FLAG}`")


def test_pd6_set_summary_detail_flag_restores_per_session_detail() -> None:
    """PD-6: el detalle por sesión se pide con la bandera declarada en
    `detail_flag` (`--detail`), que restaura el detalle (nodos `measures`)."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        store = Path(tmp) / "multi" / "sessions.db"
        _build_store(store, _populate_multi)
        proc = _run_meter("--store", str(store), SET_SUMMARY_FLAG, DETAIL_FLAG)
        assert proc.returncode == 0, (
            "PD-6 violada: `--set-summary --detail` debe restaurar el detalle "
            f"por sesión (rc=0); rc={proc.returncode}; "
            f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r}")
        doc = _parse_json(proc, "PD-6 --detail")

    detail_nodes = [n for n in _walk_dicts(doc) if "measures" in n]
    assert detail_nodes, (
        f"PD-6 violada: con `{DETAIL_FLAG}` el detalle por sesión (nodos "
        "`measures`) debe estar presente (fue ausente)")


def test_pd6_partial_magnitude_is_unknown_not_partial_total() -> None:
    """PD-6 borde (§2.6-C2/INV-9): una magnitud sin cobertura total es `unknown`
    con `cause` y `value: null` — NUNCA un subtotal parcial presentado como
    total y NUNCA `0`. El fixture fuerza cobertura parcial (S2 no reporta
    tokens)."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        store = Path(tmp) / "multi" / "sessions.db"
        _build_store(store, _populate_multi)
        doc = _set_summary_doc(store)

    mags = doc["magnitudes"]
    partial = {name: e for name, e in mags.items()
               if isinstance(e.get("sessions_reporting"), int)
               and isinstance(e.get("sessions_total"), int)
               and e["sessions_reporting"] < e["sessions_total"]}
    assert partial, (
        "PD-6 violada: el fixture fuerza cobertura parcial (S2 sin tokens) y "
        "ninguna magnitud la declara (sessions_reporting < sessions_total); el "
        "resumen no puede presentar solo magnitudes de cobertura total")
    for name, entry in partial.items():
        assert entry["bucket"] == "unknown", (
            "PD-6 violada: la magnitud sin cobertura total "
            f"{name!r} queda `unknown` (fue {entry['bucket']!r}); un subtotal "
            "parcial NUNCA se presenta como total")
        assert entry["value"] is None, (
            "PD-6 violada: la magnitud sin cobertura total "
            f"{name!r} tiene `value: null` (fue {entry['value']!r}); NUNCA un "
            "subtotal parcial ni `0`")
        assert isinstance(entry.get("cause"), str) and entry["cause"].strip(), (
            f"PD-6/INV-9 violada: la magnitud {name!r} sin cobertura total "
            f"declara una causa (fue {entry.get('cause')!r})")


def test_pd6_set_summary_is_additive_existing_records_unchanged() -> None:
    """PD-6/INV-5: la adición es aditiva — el registro neutral por sesión de
    005-002 NO cambia de comportamiento. Sin la bandera declarada, una corrida
    (de una o de varias sesiones) sigue emitiendo el registro neutral
    (`context-meter-v1` con `sessions[]`)."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        single = Path(tmp) / "single" / "sessions.db"
        multi = Path(tmp) / "multi" / "sessions.db"
        _build_store(single, _populate_single)
        _build_store(multi, _populate_multi)
        for label, store, expected in (("una-sesion", single, 1),
                                       ("multi-sesion", multi, 2)):
            proc = _run_meter("--store", str(store))
            assert proc.returncode == 0, (
                f"PD-6/INV-5 violada: la corrida por defecto ({label}) sigue "
                f"emitiendo el registro neutral (rc=0); rc={proc.returncode}")
            doc = _parse_json(proc, f"PD-6/INV-5 {label}")
            assert doc.get("meter") == NEUTRAL_METER_ID, (
                "PD-6/INV-5 violada: sin la bandera declarada la salida sigue "
                f"siendo el registro neutral `{NEUTRAL_METER_ID}` (fue "
                f"{doc.get('meter')!r}); la adición NO reescribe el registro "
                "por sesión")
            sessions = doc.get("sessions")
            assert isinstance(sessions, list) and len(sessions) == expected, (
                f"PD-6/INV-5 violada: el registro neutral ({label}) trae sus "
                f"{expected} sesión(es) (fue {sessions!r})")


# ================================================================== R4/V3

def _paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text)
    return [re.sub(r"\s+", " ", b).strip() for b in blocks if b.strip()]


R4_LIMIT = re.compile(r"16[\s.,]?384|16\s*kib|16\s*kb", re.I)
R4_PER_SESSION_DOC = re.compile(
    r"documento\s+de\s+sesi[oó]n|session\s+document|per[- ]document|"
    r"por\s+(?:cada\s+)?sesi[oó]n|per\s+session|each\s+session|"
    r"por\s+documento|cada\s+documento", re.I)
R4_TOTAL = re.compile(
    r"\btotal\b|\bconjunto\b|\bset\b|\bagregado\b|\baggregate\b|\bsuma\b", re.I)
R4_N_TIMES = re.compile(
    r"n\s*[×x*]|[×x*]\s*n\b|\btimes\b|\bveces\b|multiplicad\w*\s+por|"
    r"producto\s+de|n[uú]mero\s+de\s+sesiones|cantidad\s+de\s+sesiones|"
    r"number\s+of\s+sessions",
    re.I)


def _load_reference() -> str:
    if not CONTEXT_METER_REF.is_file():
        pytest.fail(f"documento requerido no existe: {CONTEXT_METER_REF}")
    return CONTEXT_METER_REF.read_text(encoding="utf-8")


def test_r4_reference_declares_total_bound_by_n_times_session_limit() -> None:
    """PD-6/R4/V3 elemento (a): el reference declara que el total del conjunto
    es ≤ N × el límite por sesión (antes de consumir corridas multi-sesión)."""
    paras = _paragraphs(_load_reference())
    hit = [p for p in paras
           if R4_TOTAL.search(p) and R4_N_TIMES.search(p)
           and (R4_LIMIT.search(p) or R4_PER_SESSION_DOC.search(p))]
    assert hit, (
        "PD-6/R4 violada (elemento a): `context-meter.md` no declara que el "
        "total del conjunto es ≤ N × el límite por sesión (el total no puede "
        "presentarse sin acotar contra el número de sesiones)")


def test_r4_reference_declares_limit_is_per_session_document() -> None:
    """PD-6/R4/V3 elemento (b): el reference declara que el límite normativo es
    POR DOCUMENTO DE SESIÓN."""
    text = _load_reference()
    assert R4_LIMIT.search(text), (
        "PD-6/R4 violada (elemento b): `context-meter.md` no publica el límite "
        "normativo (16.384 B / 16 KiB)")
    assert R4_PER_SESSION_DOC.search(text), (
        "PD-6/R4 violada (elemento b): `context-meter.md` no declara que el "
        "límite normativo es POR DOCUMENTO DE SESIÓN")


# =================================================================== D11

def test_d11_1_controlled_temp_base_byte_identical_after_read() -> None:
    """PD-12/D11-(1): la ausencia de escrituras se verifica sobre una base
    temporal CONTROLADA — tras la lectura, el documento de esa base queda
    byte-idéntico (y no aparecen -wal/-shm)."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        store = Path(tmp) / "controlled" / "sessions.db"
        _build_store(store, _populate_single)
        before = _snapshot_bytes(store)
        assert store.name in before, "fixture: la base controlada no se creó"
        proc = _run_meter("--store", str(store))
        assert proc.returncode == 0, (
            "PD-12/D11-(1): la lectura de la base controlada debe completarse "
            f"(rc=0); rc={proc.returncode}; "
            f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r}")
        after = _snapshot_bytes(store)
        assert after == before, (
            "PD-12/D11-(1) violada: la lectura NO es de solo escritura sobre la "
            "base controlada — el documento (o sus -wal/-shm) cambió; la base "
            "debe quedar byte-idéntica. antes="
            f"{ {k: len(v) for k, v in before.items()} } después="
            f"{ {k: len(v) for k, v in after.items()} }")


def _noise_writer(store: Path, stop: threading.Event, errors: list,
                  writes: list) -> None:
    """Otro escritor activo: escribe filas en la sesión de ruido (no medida)
    durante toda la lectura. `writes[0]` cuenta los commits efectivos."""
    conn = None
    try:
        conn = sqlite3.connect(str(store), timeout=10.0)
        conn.execute("PRAGMA busy_timeout=10000")
        seq = 1000
        while not stop.is_set():
            try:
                conn.execute("BEGIN IMMEDIATE")
                ms = BASE_MS + seq * 1000
                data = _assistant_data(
                    ROLE_SYNTH, MODEL_SYNTH, ms,
                    [{"type": "text", "text": "ruido concurrente"}], None, None)
                conn.execute(
                    "INSERT INTO session_message (id, session_id, type, seq,"
                    " time_created, time_updated, data) VALUES (?,?,?,?,?,?,?)",
                    (f"noise-{seq:06d}", NOISE_ID, "assistant", seq, ms, ms,
                     data))
                conn.commit()
                writes[0] += 1
                seq += 1
            except sqlite3.OperationalError:
                try:
                    conn.rollback()
                except sqlite3.Error:
                    pass
            time.sleep(0.005)
    except Exception as exc:  # pragma: no cover - diagnóstico del escritor
        errors.append(repr(exc))
    finally:
        if conn is not None:
            conn.close()


def test_d11_2_read_completes_and_results_expected_with_concurrent_writer() -> None:
    """PD-12/D11-(2): con otro escritor activo durante la lectura, la lectura se
    completa y sus resultados son los esperados (la lectura acotada a la sesión
    estable reporta sus medidas correctas)."""
    with tempfile.TemporaryDirectory(prefix="cdad-005-003-t3-") as tmp:
        store = Path(tmp) / "concurrent" / "sessions.db"
        _build_store(store, _populate_concurrency, wal=True)
        stop = threading.Event()
        errors: list = []
        writes: list = [0]
        writer = threading.Thread(
            target=_noise_writer, args=(store, stop, errors, writes),
            daemon=True)
        writer.start()
        try:
            # El escritor corre en paralelo mientras el medidor lee la base.
            time.sleep(0.05)
            proc = _run_meter("--store", str(store), "--session", STABLE_ID)
        finally:
            stop.set()
            writer.join(timeout=10)

    assert not errors, (
        f"PD-12/D11-(2): el escritor concurrente falló (diagnóstico): {errors}")
    assert writes[0] > 0, (
        "PD-12/D11-(2): el escritor concurrente no llegó a escribir durante la "
        "lectura (prueba de concurrencia vacía)")
    assert proc.returncode == 0, (
        "PD-12/D11-(2) violada: con un escritor concurrente vivo la lectura "
        f"debe completarse (rc=0); rc={proc.returncode}; "
        f"stderr={proc.stderr.decode('utf-8', errors='replace')[:300]!r}")
    doc = _parse_json(proc, "PD-12/D11-(2)")
    sessions = doc.get("sessions")
    assert isinstance(sessions, list) and len(sessions) == 1, (
        "PD-12/D11-(2): la lectura acotada por --session reporta UNA sesión "
        f"(fue {sessions!r})")
    calls = _measure_value(sessions[0], "tool_calls")
    assert calls == STABLE_CALLS, (
        "PD-12/D11-(2) violada: los resultados de la lectura deben ser los "
        f"esperados con el escritor concurrente vivo (tool_calls="
        f"{STABLE_CALLS}; fue {calls!r})")


D11_4_REAL_BASE = re.compile(
    r"base\s+real|real\s+base|store\s+real|real\s+store|base\s+de\s+sesiones|"
    r"base\s+viva|live\s+(?:store|base)|real\s+session", re.I)
D11_4_WRITE = re.compile(r"escrib\w*|escritura|\bwrite|writing", re.I)
D11_4_NEG = re.compile(
    r"nunca|jam[aá]s|\bnever\b|prohibid\w*|prohibited|sin\s+escribir|"
    r"without\s+writing|no\s+se\s+escrib|not\s+written", re.I)
D11_4_READONLY = re.compile(r"solo\s+lectura|s[oó]lo\s+lectura|read[- ]only", re.I)
# Verbos de escritura (constante aparte: la línea del escaneo que combina el
# nombre de la variable de la base real con este patrón no debe contener los
# literales de escritura — evita que el escaneo se auto-flagee).
D11_4_WRITE_VERBS = re.compile(
    r"(?i)\b(?:insert|update|delete|drop|create|replace)\b")


def test_d11_4_real_base_never_written_rule_declared_and_absent_in_tests() -> None:
    """PD-12/D11-(4): NUNCA se escribe en la base real (ni para demostrar que
    está prohibido). (a) la regla está declarada en `context-meter.md`; (b) la
    ausencia es verificable en las pruebas: ningún test abre la base real en
    modo escritura."""
    # (a) regla declarada en el reference.
    paras = _paragraphs(_load_reference())
    hit = [p for p in paras
           if D11_4_REAL_BASE.search(p) and D11_4_WRITE.search(p)
           and (D11_4_NEG.search(p) or D11_4_READONLY.search(p))]
    assert hit, (
        "PD-12/D11-(4) violada: `context-meter.md` no declara la regla de que "
        "NUNCA se escribe en la base real (ni para demostrar que está "
        "prohibido)")

    # (b) ausencia verificable: ningún test escribe en la base real.
    offenders = []
    for path in sorted(TESTS_DIR.rglob("*.py")):
        src = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"sqlite3\.connect\s*\(([^)]*)\)", src, re.S):
            if REAL_STORE_ENV in match.group(1):
                offenders.append(f"{path.name}: sqlite3.connect({match.group(1).strip()})")
        for lineno, line in enumerate(src.splitlines(), start=1):
            if REAL_STORE_ENV in line and D11_4_WRITE_VERBS.search(line):
                offenders.append(f"{path.name}:{lineno}: {line.strip()}")
    assert not offenders, (
        "PD-12/D11-(4) violada: hay pruebas que intentan escribir en la base "
        f"real ({REAL_STORE_ENV}): {offenders}; la base real JAMÁS se abre en "
        "modo escritura, ni para demostrar la prohibición")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
