#!/usr/bin/env python3
"""005-007 T5 RED — el medidor reconoce la interfaz común de delegación como
despacho, por hechos materiales (PD-9, delta 3).

Contract:
- docs/specs/005-007-progressive-planning/spec.md (PD-9; AC-4; INV-5; D8;
  PD-6 de 005-002 preservado por referencia §9).
- docs/specs/005-007-progressive-planning/plan.md (ficha T5: alcance incluido
  — reconocer como despacho una llamada `shell` que invoca realmente
  `cdad_delegate.py`, misma clase que la regla de `resume`, excluye ayuda y
  meras menciones, declarar el método de cada entrada del conjunto reconocido
  y actualizar la causa de ausencia con el límite honesto; excluido acoplar
  el medidor a un ledger/root y inferir por texto que sólo menciona).
- docs/specs/005-002-session-context-meter/spec.md:271-280 (PD-6: el detector
  de `resume` reconoce la invocación real, excluye ayuda y menciones — la
  clase de evidencia que PD-9 extiende al despacho; PD-6 de 005-002: un
  despacho es un EVENTO, no prueba de utilidad ni de resultado aceptado).
- Forma del esquema de los fixtures: discovery.md de 005-002 §1.2–§1.6 (NO se
  repite; NO se crea ni se abre la base real NUNCA aquí — INV-6).

ORÁCULO: la SALIDA del wrapper fino `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable) — NUNCA importando el
módulo. El contrato observable es el JSON por stdout, el rc y el diagnóstico
por stderr. Sin aserciones sobre nombres internos de funciones/clases/
módulos; sin mocks sobre plumbing.

Fixtures 100% SINTÉTICOS, construidos por este test en un directorio temporal
con SQLite, contenido inventado (identificadores, rutas, comandos, textos,
proveedor y modelo); la base real del runtime JAMÁS se abre ni se copia
(INV-6); sin rutas absolutas del host. Patrón reusado de los tests del
medidor en este scope (test_005_002_t1/t2/t4): esquema observado
`session_v2` + `session_message`, una parte `tool` por mensaje `assistant`,
llamada #i en t0 + i*30 s (time_relative = i * 0.5 min, derivado del PROPIO
fixture).

CASOS EXIGIDOS (ficha T5 + PD-9; trazado 1:1 en el docstring de cada test):

1. POSITIVO (PD-9/AC-4): una traza cuyo PRIMER despacho es una llamada
   `shell` que INVOCA realmente el programa de la interfaz común de
   delegación (`cdad_delegate.py` con sus argumentos de delegación
   `--project-root`/`--packet`/`--destination`) reporta `first_dispatch`
   OBSERVADO en esa posición (call_index/seq/time_relative) y
   `time_to_first_dispatch` observed, con el MÉTODO declarado.
   Hoy: `absent` con la causa que declara reconocer sólo `subagent`/`task`
   → RED por AssertionError sobre la postcondición ausente.
2. NEGATIVO (mención, no invocación; PD-9 «no cuenta una llamada que sólo
   menciona el programa en sus argumentos o contenido»): una traza donde el
   texto sólo MENCIONA el programa (contenido de un `write`; y un `grep` cuyo
   ARGUMENTO lo menciona sin invocarlo) reporta `absent` — nunca un despacho
   — con la causa que NOMBRA el límite honesto (la mención no cuenta; sólo
   la invocación real). Hoy la causa de `absent` es la genérica que no
   distingue la mención → RED por AssertionError sobre la causa.
3. NEGATIVO (ayuda; PD-9 «ni una llamada de ayuda `--help`/`-h`»): las
   llamadas `cdad_delegate.py --help` y `-h` NO cuentan como despacho:
   `first_dispatch` `absent` con la causa que nombra la exclusión de ayuda.
   Hoy el estado ya es `absent` (comportamiento previo) pero la causa
   genérica no nombra la exclusión para la interfaz de delegación → RED por
   AssertionError sobre la causa.
4. REGRESIÓN (INV-5/AC-4, CONTROLES — pueden pasar hoy y se declaran):
   (a) el registro NEUTRAL sin la bandera nueva es IDÉNTICO al de hoy
       (byte-identidad: sha256 del registro canónico con `run.store_ref`
       normalizado — el registro no porta rutas del host, verificado en el
       RED; el sha se capturó del medidor VIGENTE sobre el fixture neutral,
       procedencia: observación black-box del RED 2026-10-13);
   (b) el registro neutral trae la declaración de HOY (`reader.
       dispatch_tools` = `subagent`+`task`) y las causas de HOY (pinneadas
       verbatim de la observación black-box);
   (c) las trazas con `subagent`/`task` siguen detectándose IGUAL: hito
       observado con la MISMA posición/time_relative de hoy (dicts exactos).
5. DECLARACIÓN (PD-9 «el registro declara el conjunto reconocido y el método
   de cada entrada, con procedencia»): CON la bandera nueva, el registro
   declara el conjunto reconocido COMPLETO (subagent + task + la invocación
   real de la interfaz de delegación) con el MÉTODO de cada entrada y su
   PROCEDENCIA; los hitos observados portan el método declarado de su
   entrada; la causa de ausencia conserva su límite honesto (un despacho es
   un EVENTO, no prueba de utilidad ni de resultado aceptado — PD-6 de
   005-002). Hoy la bandera no existe y no hay método/procedencia declarado
   → RED por AssertionError (comportamiento ausente).

DECISIONES DECLARADAS PARA EL GREEN (el implementer lee este test como
oráculo; la spec pinnea el COMPORTAMIENTO pero no fija los nombres nuevos):

- BANDERA NUEVA ÚNICA: `--delegation-dispatch` (booleana). La detección de la
  invocación real, la declaración del conjunto+método y la actualización de
  las causas de ausencia con el límite honesto se activan CON ella; SIN ella
  el registro es byte-idéntico al de hoy para CUALQUIER traza (INV-5: «el
  registro neutral del medidor sin las banderas nuevas no cambia»; la causa
  de HOY sigue siendo VERDADERA en el modo default, que sólo reconoce
  `subagent`/`task`). La detección flag-gated mantiene al medidor lector de
  sesiones (sin dependencia del proyecto; D8) y a la medición de AC-7 dentro
  de la corrida declarada con la bandera.
- DECLARACIÓN NUEVA EN EL REGISTRO (con la bandera): `reader` gana la clave
  `dispatch_recognition` — objeto con EXACTAMENTE tres entradas: `subagent`,
  `task` y UNA entrada cuyo nombre contiene `cdad_delegate.py`; cada entrada
  declara `method` (no vacío) y `provenance` (no vacío); el método de la
  entrada de la interfaz de delegación difiere del método por NOMBRE de
  herramienta de `subagent`/`task` (dos clases de evidencia: nombre de
  herramienta vs. hecho material de la invocación — PD-9).
- MÉTODO EN EL HITO: el hito `first_dispatch` observado porta `method`
  (string no vacío) igual al método declarado para su entrada en
  `reader.dispatch_recognition`.
- CAUSA DE AUSENCIA ACTUALIZADA (con la bandera, por traza): en una traza
  que sólo menciona, la causa nombra el límite «mención no cuenta» (contiene
  `mention`); en la ayuda, nombra la exclusión (contiene `help`); y en toda
  ausencia conserva el límite honesto de PD-6: un despacho es un `event`,
  no prueba de `utility`/resultado `accepted` — nunca inventa un despacho
  (los tiempos quedan null + cubo `unknown`, NUNCA 0).

RED HOY: el medidor existe y detecta `subagent`/`task` por NOMBRE; la
bandera `--delegation-dispatch` no existe aún y la invocación real de
`cdad_delegate.py` no se detecta. Los casos 1, 2, 3 y 5 fallan HOY por
AssertionError (comportamiento ausente: la guardia de la bandera declarada,
y tras GREEN las aserciones reales de contrato toman el relevo); el caso 4
es CONTROL y pasa hoy (así se declara). El test NO importa el módulo del
medidor: ningún fallo por ImportError ni sintaxis.
"""

from __future__ import annotations

import hashlib
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

FEATURE_ID = "005-007-progressive-planning"
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"  # fuga del entorno del host
CLI_TIMEOUT_S = 120        # fixtures chicos

METER_ID = "context-meter-v1"
DELEGATION_PROGRAM = "cdad_delegate.py"
DELEGATION_FLAG = "--delegation-dispatch"   # bandera nueva declarada (RED)
RUNTIME_NAMES = ("session_v2", "session_message")  # neutralidad PD-1/INV-3

# ------------------------------------- comportamiento de HOY (capturado del
# medidor VIGENTE por observación black-box en el RED 2026-10-13; sirve de
# base de la regresión de byte-identidad: INV-5 no lo deja cambiar sin la
# bandera nueva).

TODAY_DISPATCH_TOOLS = ["subagent", "task"]
TODAY_DISPATCH_ABSENT_CAUSE = (
    "no role work dispatch tool call in the first stretch: this reader "
    "recognizes only the dispatch tools 'subagent' and 'task'; a dispatch "
    "made with any other tool is not detected by this reader, so the absence "
    "is unknown, never invented")
TODAY_RESUME_ABSENT_CAUSE = (
    "no shell call in the first stretch invokes the resume subcommand of the "
    "continuity CLI (help calls such as --help are excluded)")
TODAY_NEUTRAL_MILESTONES = {
    "first_dispatch": {"status": "absent",
                       "cause": TODAY_DISPATCH_ABSENT_CAUSE},
    "first_resume": {"status": "absent", "cause": TODAY_RESUME_ABSENT_CAUSE},
}
# Observado hoy: subagent/task = despacho por NOMBRE de herramienta (llamada
# #2, seq 3, 1,0 min sobre el fixture de 3 llamadas con paso de 30 s).
TODAY_SUBAGENT_MILESTONE = {"position": {"call_index": 2, "seq": 3},
                            "status": "observed", "time_relative": 1.0}

# SHA del registro canónico de HOY sobre el fixture neutral (run.store_ref
# normalizado; see `_canonical_record`). Capturado del medidor vigente.
NEUTRAL_RECORD_GOLDEN_SHA256 = (
    "b43107dba90bbd7e2db1bfa5fd283c1f79b04d8192c7e9b5aecdf50ff3da2bcf")

# --------------------------------------------------- trazas fixture (PD-9)

DELEGATE_SKILLS_CMD = (
    "python3 skills/cdad-cycle/scripts/cdad_delegate.py --project-root . "
    "--packet fixture-packet-discovery-001 --destination "
    "cdad_delegate_fixture.py")
DELEGATE_WRAPPER_CMD = (
    "python3 scripts/cdad_delegate.py --project-root . "
    "--packet fixture-packet-plan-001 --destination "
    "cdad_delegate_fixture.py")
DELEGATE_HELP_CMD = (
    "python3 skills/cdad-cycle/scripts/cdad_delegate.py --help")
DELEGATE_HELP_SHORT_CMD = (
    "python3 skills/cdad-cycle/scripts/cdad_delegate.py -h")
# Mención NO invocadora: el contenido de una `write` y el ARGUMENTO de un
# `grep` mencionan el programa; NINGUNA llama al programa.
MENTION_WRITE_CONTENT = (
    "instrucciones del ciclo: para despachar, invocar cdad_delegate.py "
    "con --project-root, --packet y --destination")
MENTION_GREP_CMD = "grep -rn 'cdad_delegate.py' docs/ | head -3"

ROLE_SYNTH = "cdad-orchestrator"
MODEL_SYNTH = '{"id":"model-alpha","providerID":"prov-a"}'
BASE_MS = 1_760_000_000_000  # epoch ms SINTÉTICO, fijo (determinismo)
STEP_MS = 30_000             # llamada #i en t0 + i*30 s (→ i*0.5 min)

# ------------------------------------------ posiciones esperadas (derivadas
# del PROPIO fixture: llamada #i → call_index i, seq i+1, i*0.5 min)

POS_DELEGATE_SKILLS = (3, 4, 1.5)   # read, glob, shell(delegate), read
POS_DELEGATE_WRAPPER = (2, 3, 1.0)  # read, shell(wrapper delegate), read

MEASURE_FIELDS = ("value", "unit", "provenance", "bucket")

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

SESSION_MESSAGE_DDL = """
CREATE TABLE session_message (
    id TEXT PRIMARY KEY, session_id TEXT, type TEXT, seq INTEGER,
    time_created REAL, time_updated REAL, data TEXT)
"""


def _user_data(ms: int, text: str) -> str:
    """Forma `user` (discovery §1.3): {time, text}."""
    return json.dumps({"time": ms, "text": text}, sort_keys=True)


def _tool_part(name: str, text: str, ms: int, *, input_args: dict,
               part_id: str) -> dict:
    """Parte `tool` (discovery §1.4): state.input = argumentos;
    state.content = [{type:text, text}] → salida = suma de len(text)."""
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
    """Forma `assistant` (discovery §1.3); time_created == time_updated."""
    tin, tout, treason, tread, twrite = tokens
    return json.dumps({
        "time": {"created": ms, "streamed": ms, "completed": ms},
        "agent": agent, "model": model, "content": parts,
        "tokens": {"input": tin, "output": tout, "reasoning": treason,
                   "cache": {"read": tread, "write": twrite}},
        "cost": cost,
    }, sort_keys=True)


def _build_trace_store(path: Path, *, sid: str,
                       calls: list[tuple[str, dict]]) -> None:
    """Fixture SQLite sintético con UNA sesión y UNA traza de llamadas (una
    parte `tool` por mensaje, llamada #i en t0 + i*STEP_MS, sin brechas →
    un solo tramo = la sesión). Contenido 100% inventado (INV-6)."""
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
        t0 = BASE_MS + 10_000_000_000
        sum_in = sum_out = sum_reason = sum_cread = 0
        conn.execute(
            "INSERT INTO session_message (id, session_id, type, seq,"
            " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (f"msg-0001-{sid}", sid, "user", 1, t0, t0,
             _user_data(t0, "arranque de la traza fixture t5")))
        for i, (name, args) in enumerate(calls, start=1):
            seq = 1 + i
            ms = t0 + i * STEP_MS
            tin, tread, tout, treason = 90, 80, 30, 5
            sum_in += tin
            sum_cread += tread
            sum_out += tout
            sum_reason += treason
            data = _assistant_data(
                ROLE_SYNTH, MODEL_SYNTH, ms,
                [_tool_part(name, "o" * 30, ms, input_args=args,
                            part_id=f"p{seq}")],
                (tin, tout, treason, tread, 0), None)
            conn.execute(
                "INSERT INTO session_message (id, session_id, type, seq,"
                " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?,"
                " ?, ?)",
                (f"msg-{seq:04d}-{sid}", sid, "assistant", seq, ms, ms,
                 data))
        total_ms = t0 + len(calls) * STEP_MS
        conn.execute(
            "INSERT INTO session_v2 (id, project_id, workspace_id,"
            " parent_id, fork_session_id, fork_boundary, slug, directory,"
            " path, title, version, share_url, summary_additions,"
            " summary_deletions, summary_files, summary_diffs, metadata,"
            " cost, tokens_input, tokens_output, tokens_reasoning,"
            " tokens_cache_read, tokens_cache_write, revert, permission,"
            " agent, model, time_created, time_updated, time_compacting,"
            " time_archived, time_suspended, resume_attempts, time_idle,"
            " time_viewed, idle_outcome)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
            " ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sid, "proj-fixture", "ws-fixture", None, None, None,
             f"fixture-{sid[-6:]}", "/fixture/dir", "/fixture/dir",
             f"fixture {sid}", "fixture-version", None, 0, 0, 0, 0, None,
             None, sum_in, sum_out, sum_reason, sum_cread, 0, None, None,
             ROLE_SYNTH, MODEL_SYNTH, t0, total_ms, None, None, None, 0,
             None, None, None))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp, path)


def _build_fixture_stores(base: Path) -> dict[str, Path]:
    """Las trazas fixture del RED (nombres → stores). Cada una replica el
    recorrido declarado por su caso; ver docstrings de los tests."""
    stores: dict[str, Path] = {}

    def build(name: str, sid: str, calls: list[tuple[str, dict]]) -> Path:
        store = base / name / "sessions.db"
        _build_trace_store(store, sid=sid, calls=calls)
        stores[name] = store
        return store

    # Caso 1 POSITIVO: el PRIMER despacho es una shell que invoca REALMENTE
    # el programa de la interfaz común (args de delegación declarados).
    build("delegate-skills", "sess-fixture-t5-delegate-skills", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("glob", {"pattern": "fixture-*"}),
        ("shell", {"command": DELEGATE_SKILLS_CMD}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    # Caso 1 (variante de camino): la MISMA invocación por el wrapper del
    # repo — el hecho material es el PROGRAMA, no la ruta exacta (misma
    # clase que la regla de `resume`, que no fija la ruta del CLI).
    build("delegate-wrapper", "sess-fixture-t5-delegate-wrapper", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("shell", {"command": DELEGATE_WRAPPER_CMD}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    # Caso 2 NEGATIVO: menciones sin invocación (contenido de `write` y
    # argumento de `grep`).
    build("mention", "sess-fixture-t5-mention", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("write", {"path": "/fixture/dir/instrucciones.md",
                   "content": MENTION_WRITE_CONTENT}),
        ("shell", {"command": MENTION_GREP_CMD}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    # Caso 3 NEGATIVO: llamadas de AYUDA (--help y -h).
    build("help", "sess-fixture-t5-help", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("shell", {"command": DELEGATE_HELP_CMD}),
        ("shell", {"command": DELEGATE_HELP_SHORT_CMD}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    # Caso 4 CONTROLES: traza NEUTRAL (sin despacho ni mención) para la
    # byte-identidad del registro; y trazas subagent/task de HOY.
    build("neutral", "sess-fixture-t5-neutral", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("glob", {"pattern": "fixture-*"}),
        ("shell", {"command": "echo fixture-step"}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    build("subagent", "sess-fixture-t5-subagent", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("subagent", {"path": "/fixture/dir/w2.md"}),
        ("read", {"path": "/fixture/dir/f3.md"}),
    ])
    build("task", "sess-fixture-t5-task", [
        ("read", {"path": "/fixture/dir/f1.md"}),
        ("task", {"path": "/fixture/dir/w2.md"}),
        ("glob", {"pattern": "fixture-*"}),
    ])
    return stores


# ---------------------------------------------------------------- helpers

def _canonical_record(doc: dict) -> str:
    """Registro canónico para la regresión de byte-identidad (INV-5): JSON
    determinista con `run.store_ref` NORMALIZADO — store_ref es el hash de
    la RUTA del store (varía por tmpdir/máquina; el resto del registro no
    porta rutas del host, verificado en el RED: 0 ocurrencias del tmpdir).
    La normalización NO debilita la regresión: cualquier otro byte del
    registro cambia el sha."""
    doc = json.loads(json.dumps(doc, ensure_ascii=False))
    doc["run"]["store_ref"] = "sha256:NORMALIZED-STORE-PATH"
    return json.dumps(doc, ensure_ascii=False, sort_keys=True)


def _golden_recipe() -> str:
    return ("regenerar la base de la comparación: construir el fixture "
            "neutral con `_build_fixture_stores` en un tmpdir, correr "
            "`python3 scripts/cdad_context_meter.py --store <store>`, "
            "aplicar `_canonical_record` y hashear con sha256")


class DelegationDispatchT5Test(unittest.TestCase):
    """T5 RED de 005-007: un test por caso exigido (ficha T5/PD-9), contra
    la SALIDA del wrapper (stdout JSON + rc + stderr)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-007-t5-")
        self.addCleanup(tmp.cleanup)
        self.stores = _build_fixture_stores(Path(tmp.name))

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
        env.pop(STORE_ENV_VAR, None)      # sin fuga del entorno del host
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
                f"{FEATURE_ID}: el medidor no terminó dentro de "
                f"{CLI_TIMEOUT_S}s; timeout={exc!r}")

    def run_with_flag(self, store: Path, label: str) -> dict:
        """Corrida CON la bandera nueva declarada `--delegation-dispatch`.
        Guard de RED: si la bandera no es aceptada aún, el fallo es un
        AssertionError de comportamiento ausente (nunca ImportError), con
        el contrato en el mensaje — el RED de la postcondición PD-9.
        `self.fail` lanza AssertionError (failureException)."""
        proc = self.run_meter("--store", str(store), DELEGATION_FLAG)
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace")
            missing_flag = (DELEGATION_FLAG.lstrip("-") in err
                            or "unrecognized" in err)
            if missing_flag:
                self.fail(
                    f"RED {label}: la bandera nueva declarada "
                    f"`{DELEGATION_FLAG}` no es aceptada aún por el "
                    "medidor — comportamiento ausente (PD-9/AC-4): ni la "
                    "detección de la invocación real de la interfaz de "
                    "delegación, ni la declaración del conjunto+método, ni "
                    "las causas de ausencia actualizadas existen; "
                    "AssertionError de RED, nunca ImportError. "
                    f"stderr={err[:300]!r}")
            self.fail(
                f"{label}: precondición rota — la corrida con "
                f"`{DELEGATION_FLAG}` sobre el fixture debe salir rc=0; "
                f"rc={proc.returncode} stderr={err[:300]!r}")
        return self.parse_session(proc, label)

    def parse_session(self, proc: subprocess.CompletedProcess,
                      label: str) -> dict:
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        self.assertEqual(
            doc.get("run", {}).get("schema"), "recognized",
            msg=f"{label}: el fixture replica el esquema observado "
                "(discovery §1.2) y debe reconocerse — si saliera "
                "`unknown` el fallo sería de rejilla equivocada, no de "
                f"contrato; run={doc.get('run')}")
        sessions = doc.get("sessions")
        self.assertIsInstance(sessions, list, msg=f"{label}: sessions[]")
        self.assertEqual(
            len(sessions), 1,
            msg=f"{label}: el fixture tiene UNA sesión (fue "
                f"{len(sessions) if isinstance(sessions, list) else sessions!r})")
        return doc

    def milestone(self, session: dict, key: str, ctx: str) -> dict:
        milestones = session.get("milestones")
        self.assertIsInstance(
            milestones, dict, msg=f"{ctx}: milestones es objeto")
        self.assertIn(
            key, milestones,
            msg=f"{ctx}: milestones trae {key!r} (clave presente)")
        return milestones[key]

    def measure_leaf(self, session: dict, key: str, ctx: str) -> dict:
        measures = session["measures"]
        self.assertIn(
            key, measures,
            msg=f"{ctx}: la medida declarada {key!r} existe (fue "
                f"{sorted(measures)!r})")
        leaf = measures[key]
        for field in MEASURE_FIELDS:
            self.assertIn(
                field, leaf,
                msg=f"{ctx}: la medida {key!r} trae {field!r}")
        return leaf


# ------------------------------------------------------------------ tests


class TestRealInvocationObserved(DelegationDispatchT5Test):
    """Caso 1 POSITIVO (PD-9/AC-4): la invocación REAL de la interfaz común
    de delegación es un despacho observado, con el método declarado."""

    def test_pd9_real_delegation_invocation_reports_observed_dispatch(self):
        """PD-9/AC-4 (caso 1): una traza cuyo PRIMER despacho es una llamada
        `shell` que invoca realmente `cdad_delegate.py` (con sus argumentos
        de delegación `--project-root`/`--packet`/`--destination`) reporta
        `first_dispatch` OBSERVADO en esa posición (call_index/seq/
        time_relative derivados del propio fixture), `time_to_first_dispatch`
        observed en minutos, y el MÉTODO declarado (string no vacío); el
        hito de `resume` queda independiente (ausente). Variantes: (a) por
        la ruta canónica del programa (skills/…), (b) por el wrapper del
        repo — el hecho material es el PROGRAMA, no la ruta exacta (misma
        clase que la regla de `resume`, 005-002 PD-6)."""
        # (a) invocación por la ruta canónica del programa.
        with self.subTest(punto="a-invocacion-real-ruta-canonica"):
            doc_a = self.run_with_flag(
                self.stores["delegate-skills"], "PD-9 caso 1 (a)")
            # EXTRACCIÓN (testfix 007): run_with_flag → parse_session
            # devuelve el DOCUMENTO; los casos verifican hitos/medidas de la
            # ENTRADA DE SESIÓN, que parse_session ya validó única y
            # existente.
            session = doc_a["sessions"][0]
            fd = self.milestone(session, "first_dispatch", "PD-9 caso 1 (a)")
            self.assertEqual(
                fd.get("status"), "observed",
                msg=f"PD-9 (caso 1): la invocación REAL de "
                    f"`{DELEGATION_PROGRAM}` (shell con "
                    "--project-root/--packet/--destination) es un despacho "
                    "de trabajo de rol OBSERVADO (fue "
                    f"{fd.get('status')!r}; hoy el medidor sólo reconoce "
                    "los NOMBRES subagent/task y no ve la invocación "
                    "real)")
            position = fd.get("position")
            self.assertIsInstance(
                position, dict,
                msg="PD-9 (caso 1): el hito observado trae position")
            self.assertEqual(
                position.get("call_index"), POS_DELEGATE_SKILLS[0],
                msg=f"PD-9 (caso 1): la posición del despacho es la "
                    f"llamada #{POS_DELEGATE_SKILLS[0]} (la shell que "
                    f"invoca `{DELEGATION_PROGRAM}`; fue "
                    f"{position.get('call_index')!r})")
            self.assertEqual(
                position.get("seq"), POS_DELEGATE_SKILLS[1],
                msg=f"PD-9 (caso 1): la posición porta el seq del mensaje "
                    f"({POS_DELEGATE_SKILLS[1]}; fue "
                    f"{position.get('seq')!r})")
            time_rel = fd.get("time_relative")
            self.assertIsInstance(
                time_rel, (int, float),
                msg=f"PD-9 (caso 1): time_relative numérico en minutos "
                    f"(fue {time_rel!r})")
            self.assertLessEqual(
                abs(time_rel - POS_DELEGATE_SKILLS[2]), 0.01,
                msg=f"PD-9 (caso 1): time_relative = "
                    f"{POS_DELEGATE_SKILLS[2]} min (derivado del propio "
                    f"fixture; fue {time_rel!r})")
            method = fd.get("method")
            self.assertIsInstance(
                method, str,
                msg="PD-9 (caso 1): el hito observado declara su MÉTODO "
                    f"(fue {method!r}) — con procedencia declarada en el "
                    "registro (caso 5)")
            self.assertTrue(
                method.strip(),
                msg="PD-9 (caso 1): el método declarado no es vacío")
            leaf = self.measure_leaf(session, "time_to_first_dispatch",
                                     "PD-9 caso 1 (a)")
            self.assertEqual(
                str(leaf.get("bucket")), "observed",
                msg="PD-9 (caso 1): el tiempo hasta el despacho observado "
                    f"es observed (fue {leaf.get('bucket')!r})")
            value = leaf.get("value")
            self.assertIsInstance(
                value, (int, float),
                msg=f"PD-9 (caso 1): time_to_first_dispatch numérico (fue "
                    f"{value!r})")
            self.assertLessEqual(
                abs(value - POS_DELEGATE_SKILLS[2]), 0.01,
                msg=f"PD-9 (caso 1): time_to_first_dispatch = "
                    f"{POS_DELEGATE_SKILLS[2]} min (fue {value!r})")
            fr = self.milestone(session, "first_resume", "PD-9 caso 1 (a)")
            self.assertEqual(
                fr.get("status"), "absent",
                msg="PD-9 (caso 1): el hito de resume queda INDEPENDIENTE "
                    f"(sin resume real → absent; fue {fr.get('status')!r})")
        # (b) la MISMA invocación por el wrapper del repo: mismo hecho
        #     material (el PROGRAMA), otra ruta — misma clase que `resume`,
        #     que no fija la ruta exacta del CLI.
        with self.subTest(punto="b-invocacion-real-por-el-wrapper"):
            doc_b = self.run_with_flag(
                self.stores["delegate-wrapper"], "PD-9 caso 1 (b)")
            session = doc_b["sessions"][0]   # misma extracción (testfix 007)
            fd = self.milestone(session, "first_dispatch", "PD-9 caso 1 (b)")
            self.assertEqual(
                fd.get("status"), "observed",
                msg=f"PD-9 (caso 1b): invocar `{DELEGATION_PROGRAM}` por el "
                    "wrapper del repo TAMBIÉN es un despacho observado — "
                    "el hecho material es el PROGRAMA invocado, no la ruta "
                    f"exacta (fue {fd.get('status')!r})")
            position = fd.get("position")
            self.assertEqual(
                (position or {}).get("call_index"), POS_DELEGATE_WRAPPER[0],
                msg=f"PD-9 (caso 1b): la posición es la llamada "
                    f"#{POS_DELEGATE_WRAPPER[0]} (fue {position!r})")


class TestMentionIsNotDispatch(DelegationDispatchT5Test):
    """Caso 2 NEGATIVO (PD-9): una mención del programa NO es un despacho;
    la ausencia se declara con la causa que nombra el límite honesto."""

    def test_pd9_mention_only_reports_absent_with_honest_cause(self):
        """PD-9 (caso 2): una traza donde el texto sólo MENCIONA el programa
        — el CONTENIDO de un `write` que instruye invocar
        `cdad_delegate.py`, y un `grep` cuyo ARGUMENTO lo menciona sin
        invocarlo — reporta `first_dispatch` `absent` (NUNCA un despacho
        inferido del texto: PD-6 de 005-002), con la causa que NOMBRA el
        límite honesto (la mención no cuenta; sólo la invocación real) y el
        tiempo null + cubo `unknown` (nunca 0). Hoy la causa de `absent` es
        la genérica que no distingue la mención → RED."""
        doc_mention = self.run_with_flag(self.stores["mention"],
                                         "PD-9 caso 2")
        session = doc_mention["sessions"][0]   # extracción (testfix 007)
        fd = self.milestone(session, "first_dispatch", "PD-9 caso 2")
        self.assertEqual(
            fd.get("status"), "absent",
            msg=f"PD-9 (caso 2): la traza con SOLO menciones (write + grep) "
                f"NO despacha → status `absent`, nunca `observed` (fue "
                f"{fd.get('status')!r}) — el despacho no se infiere de "
                "texto que sólo menciona")
        cause = fd.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"PD-9 (caso 2): la ausencia trae causa declarada (fue "
                f"{cause!r})")
        self.assertTrue(
            cause.strip(),
            msg="PD-9 (caso 2): la causa de la ausencia no es vacía")
        self.assertIn(
            "mention", cause.lower(),
            msg="PD-9 (caso 2): la causa NOMBRA el límite honesto — la "
                "MENCIÓN del programa no cuenta como despacho (hoy la "
                f"causa es la genérica de subagent/task: {cause!r})")
        leaf = self.measure_leaf(session, "time_to_first_dispatch",
                                 "PD-9 caso 2")
        self.assertIsNone(
            leaf.get("value"),
            msg="PD-9 (caso 2): sin despacho el tiempo NO se inventa y NO "
                f"es 0 (value={leaf.get('value')!r}) — null + cubo "
                "unknown (PD-4 de 005-002)")
        self.assertEqual(
            str(leaf.get("bucket")), "unknown",
            msg=f"PD-9 (caso 2): el tiempo queda en el cubo unknown (fue "
                f"{leaf.get('bucket')!r})")


class TestHelpCallIsNotDispatch(DelegationDispatchT5Test):
    """Caso 3 NEGATIVO (PD-9): una llamada de ayuda (`--help`/`-h`) NO es un
    despacho; la causa declara la exclusión."""

    def test_pd9_help_calls_report_absent_with_honest_cause(self):
        """PD-9 (caso 3): las llamadas `cdad_delegate.py --help` y `-h` NO
        cuentan como despacho — `first_dispatch` `absent`, con la causa que
        NOMBRA la exclusión de ayuda (el límite honesto, igual que la regla
        de `resume` que excluye `--help`), y el tiempo null + cubo
        `unknown`. Hoy el estado ya es `absent` (exclusión previa) pero la
        causa genérica no nombra la exclusión de ayuda para la interfaz de
        delegación → RED sobre la causa."""
        doc_help = self.run_with_flag(self.stores["help"], "PD-9 caso 3")
        session = doc_help["sessions"][0]     # extracción (testfix 007)
        fd = self.milestone(session, "first_dispatch", "PD-9 caso 3")
        self.assertEqual(
            fd.get("status"), "absent",
            msg=f"PD-9 (caso 3): las llamadas de ayuda (--help y -h de "
                f"`{DELEGATION_PROGRAM}`) NO son un despacho → status "
                f"`absent` (fue {fd.get('status')!r})")
        cause = fd.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"PD-9 (caso 3): la ausencia trae causa declarada (fue "
                f"{cause!r})")
        self.assertTrue(
            cause.strip(),
            msg="PD-9 (caso 3): la causa de la ausencia no es vacía")
        self.assertIn(
            "help", cause.lower(),
            msg="PD-9 (caso 3): la causa NOMBRA la exclusión de ayuda "
                "(hoy la causa genérica no distingue el caso de ayuda de "
                f"la interfaz de delegación: {cause!r})")
        leaf = self.measure_leaf(session, "time_to_first_dispatch",
                                 "PD-9 caso 3")
        self.assertIsNone(
            leaf.get("value"),
            msg="PD-9 (caso 3): sin despacho el tiempo NO se inventa y NO "
                f"es 0 (value={leaf.get('value')!r})")
        self.assertEqual(
            str(leaf.get("bucket")), "unknown",
            msg=f"PD-9 (caso 3): el tiempo queda en el cubo unknown (fue "
                f"{leaf.get('bucket')!r})")


class TestNeutralRecordByteIdentity(DelegationDispatchT5Test):
    """Caso 4 REGRESIÓN (INV-5/AC-4) — CONTROLES: el registro neutral sin
    la bandera nueva es idéntico al de hoy; subagent/task siguen
    detectándose igual. Este test PASA HOY (controles declarados) y debe
    seguir pasando en GREEN."""

    def test_pd9_inv5_neutral_record_identical_and_subagent_task_unchanged(
            self):
        """INV-5/AC-4 (caso 4, controles): (a) el registro NEUTRAL sin la
        bandera nueva es IDÉNTICO al de hoy — sha256 del registro canónico
        (`run.store_ref` normalizado) capturado del medidor VIGENTE sobre
        el fixture neutral (procedencia: observación black-box del RED
        2026-10-13; el registro no porta rutas del host); (b) el registro
        neutral trae la declaración y las causas de HOY (pinneadas
        verbatim); (c) las trazas `subagent`/`task` siguen detectándose
        IGUAL (hitos observados con los dicts exactos de hoy); (d) las
        trazas de mención y de ayuda SIN la bandera también siguen en
        `absent` (el modo default no cambia)."""
        # (a) byte-identidad del registro neutral (sha del registro
        #     canónico).
        with self.subTest(punto="a-neutral-byte-identico"):
            proc = self.run_meter("--store", str(self.stores["neutral"]))
            self.assertEqual(
                proc.returncode, 0,
                msg="INV-5 (a): la corrida default sobre el fixture "
                    f"neutral sale rc=0; stderr="
                    f"{proc.stderr[:300]!r}")
            doc = self.parse_session(proc, "INV-5 (a)")
            canonical = _canonical_record(doc)
            digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            self.assertEqual(
                digest, NEUTRAL_RECORD_GOLDEN_SHA256,
                msg="INV-5 (a): el registro neutral SIN la bandera nueva "
                    "es IDÉNTICO al de hoy (sha256 del registro canónico "
                    f"con run.store_ref normalizado; calculado "
                    f"{digest}, esperado {NEUTRAL_RECORD_GOLDEN_SHA256}) "
                    "— INV-5 prohíbe tocar el registro neutral; "
                    + _golden_recipe())
        # (b) la declaración y las causas de HOY, pinneadas verbatim.
        with self.subTest(punto="b-declaracion-y-causas-de-hoy"):
            proc = self.run_meter("--store", str(self.stores["neutral"]))
            doc = self.parse_session(proc, "INV-5 (b)")
            self.assertEqual(
                doc.get("meter"), METER_ID,
                msg=f"INV-5 (b): el registro neutral sigue siendo "
                    f"`{METER_ID}` (fue {doc.get('meter')!r})")
            self.assertEqual(
                doc.get("reader", {}).get("dispatch_tools"),
                TODAY_DISPATCH_TOOLS,
                msg=f"INV-5 (b): el conjunto declarado de HOY es "
                    f"{TODAY_DISPATCH_TOOLS!r} (fue "
                    f"{doc.get('reader', {}).get('dispatch_tools')!r})")
            session = doc["sessions"][0]
            self.assertEqual(
                session.get("milestones"), TODAY_NEUTRAL_MILESTONES,
                msg="INV-5 (b): los hitos de la traza neutral son los de "
                    f"HOY (fue {session.get('milestones')!r}) — la causa "
                    "de ausencia conserva el texto vigente en el modo "
                    "default")
        # (c) subagent/task siguen detectándose igual (dicts exactos).
        with self.subTest(punto="c-subagent-y-task-igual"):
            for name, sid_label in (("subagent", "subagent"),
                                    ("task", "task")):
                proc = self.run_meter("--store", str(self.stores[name]))
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"INV-5 (c) {sid_label}: corrida default rc=0")
                session = self.parse_session(
                    proc, f"INV-5 (c) {sid_label}")["sessions"][0]
                fd = self.milestone(session, "first_dispatch",
                                    f"INV-5 (c) {sid_label}")
                self.assertEqual(
                    fd, TODAY_SUBAGENT_MILESTONE,
                    msg=f"INV-5 (c) {sid_label}: el despacho por NOMBRE de "
                        "herramienta sigue detectándose IGUAL a hoy "
                        f"(esperado {TODAY_SUBAGENT_MILESTONE!r}; fue "
                        f"{fd!r})")
        # (d) mención y ayuda SIN la bandera: siguen `absent` en default.
        with self.subTest(punto="d-mencion-y-ayuda-sin-bandera-absent"):
            for name in ("mention", "help"):
                proc = self.run_meter("--store", str(self.stores[name]))
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"INV-5 (d) {name}: corrida default rc=0")
                session = self.parse_session(
                    proc, f"INV-5 (d) {name}")["sessions"][0]
                fd = self.milestone(session, "first_dispatch",
                                    f"INV-5 (d) {name}")
                self.assertEqual(
                    fd.get("status"), "absent",
                    msg=f"INV-5 (d) {name}: sin la bandera, la traza sigue "
                        f"en `absent` (fue {fd.get('status')!r})")


class TestRecordDeclaresSetAndMethod(DelegationDispatchT5Test):
    """Caso 5 DECLARACIÓN (PD-9): el registro declara el conjunto reconocido
    y el método de cada entrada, con procedencia, y la causa de ausencia
    conserva su límite honesto."""

    def test_pd9_record_declares_recognized_set_method_and_provenance(self):
        """PD-9 (caso 5): CON la bandera nueva, el registro declara el
        conjunto reconocido COMPLETO y el MÉTODO de cada entrada con
        PROCEDENCIA: `reader.dispatch_recognition` con EXACTAMENTE tres
        entradas — `subagent`, `task` y una que nombra
        `cdad_delegate.py` —, cada una con `method` y `provenance` no
        vacíos; el método de la entrada de la interfaz de delegación difiere
        del método por NOMBRE de herramienta (dos clases de evidencia —
        PD-9: el hecho material de la invocación, misma clase que la regla
        de `resume`); los hitos observados portan el método declarado de su
        entrada (subagent sigue detectándose igual CON la bandera); y la
        causa de ausencia conserva su límite honesto: un despacho es un
        EVENTO, no prueba de utilidad ni de resultado aceptado (PD-6 de
        005-002, por referencia)."""
        # (a) la declaración del conjunto + método por entrada + procedencia.
        with self.subTest(punto="a-conjunto-metodo-procedencia"):
            doc = self.run_with_flag(self.stores["delegate-skills"],
                                     "PD-9 caso 5 (a)")
            reader = doc.get("reader")
            self.assertIsInstance(
                reader, dict, msg="PD-9 (caso 5): reader es objeto")
            recognition = reader.get("dispatch_recognition")
            self.assertIsInstance(
                recognition, dict,
                msg="PD-9 (caso 5): el registro declara el CONJUNTO "
                    "reconocido y el método de cada entrada — "
                    "`reader.dispatch_recognition` no existe (fue "
                    f"{reader!r})")
            self.assertEqual(
                len(recognition), 3,
                msg=f"PD-9 (caso 5): el conjunto reconocido declarado es "
                    f"CERRADO con tres entradas (subagent, task y la "
                    f"invocación real de `{DELEGATION_PROGRAM}`; fue "
                    f"{sorted(recognition)!r})")
            self.assertIn(
                "subagent", recognition,
                msg="PD-9 (caso 5): `subagent` sigue en el conjunto")
            self.assertIn(
                "task", recognition,
                msg="PD-9 (caso 5): `task` sigue en el conjunto")
            delegation_entries = [
                name for name in recognition
                if DELEGATION_PROGRAM in str(name)]
            self.assertEqual(
                len(delegation_entries), 1,
                msg=f"PD-9 (caso 5): EXACTAMENTE una entrada del conjunto "
                    f"declara la interfaz de delegación (contiene "
                    f"`{DELEGATION_PROGRAM}`; fue "
                    f"{sorted(recognition)!r})")
            for name, entry in recognition.items():
                self.assertIsInstance(
                    entry, dict,
                    msg=f"PD-9 (caso 5): la entrada {name!r} es objeto")
                for field in ("method", "provenance"):
                    value = entry.get(field)
                    self.assertIsInstance(
                        value, str,
                        msg=f"PD-9 (caso 5): la entrada {name!r} declara "
                            f"{field!r} como texto (fue {value!r})")
                    self.assertTrue(
                        value.strip(),
                        msg=f"PD-9 (caso 5): la entrada {name!r} declara "
                            f"{field!r} no vacío (fue {value!r})")
            delegate_name = delegation_entries[0]
            subagent_method = recognition["subagent"]["method"]
            delegate_method = recognition[delegate_name]["method"]
            self.assertNotEqual(
                delegate_method, subagent_method,
                msg="PD-9 (caso 5): el MÉTODO de la entrada de la interfaz "
                    "de delegación difiere del método por NOMBRE de "
                    "herramienta — dos clases de evidencia (hecho material "
                    "de la invocación vs. nombre de herramienta)")
        # (b) los hitos observados portan el método declarado de su entrada;
        #     subagent sigue detectándose IGUAL con la bandera (posición).
        with self.subTest(punto="b-metodos-de-los-hitos-observados"):
            doc = self.run_with_flag(self.stores["delegate-skills"],
                                     "PD-9 caso 5 (b)")
            fd = self.milestone(doc["sessions"][0], "first_dispatch",
                                "PD-9 caso 5 (b)")
            recognition = doc["reader"]["dispatch_recognition"]
            delegate_name = next(
                name for name in recognition
                if DELEGATION_PROGRAM in str(name))
            self.assertEqual(
                fd.get("method"), recognition[delegate_name]["method"],
                msg="PD-9 (caso 5): el método del hito observado "
                    f"({fd.get('method')!r}) es el método declarado para "
                    f"la entrada {delegate_name!r} "
                    f"({recognition[delegate_name]['method']!r})")
            doc_sub = self.run_with_flag(self.stores["subagent"],
                                         "PD-9 caso 5 (b) subagent")
            session_sub = doc_sub["sessions"][0]
            fd_sub = self.milestone(session_sub, "first_dispatch",
                                    "PD-9 caso 5 (b) subagent")
            self.assertEqual(
                fd_sub.get("status"), "observed",
                msg=f"PD-9 (caso 5): CON la bandera, el despacho por "
                    f"`subagent` sigue OBSERVADO (fue "
                    f"{fd_sub.get('status')!r})")
            self.assertEqual(
                fd_sub.get("position"),
                TODAY_SUBAGENT_MILESTONE["position"],
                msg=f"PD-9 (caso 5): la posición del despacho `subagent` "
                    "con la bandera es la MISMA de hoy "
                    f"({TODAY_SUBAGENT_MILESTONE['position']!r}; fue "
                    f"{fd_sub.get('position')!r}) — la detección previa no "
                    "cambia")
            self.assertEqual(
                fd_sub.get("method"),
                recognition["subagent"]["method"],
                msg="PD-9 (caso 5): el método del hito `subagent` es el "
                    "declarado para su entrada "
                    f"({recognition['subagent']['method']!r}; fue "
                    f"{fd_sub.get('method')!r})")
        # (c) la causa de ausencia conserva su límite honesto: un despacho
        #     es un EVENTO, no prueba de utilidad ni de resultado aceptado.
        with self.subTest(punto="c-causa-de-ausencia-limite-honesto"):
            doc = self.run_with_flag(self.stores["neutral"],
                                     "PD-9 caso 5 (c)")
            fd = self.milestone(doc["sessions"][0], "first_dispatch",
                                "PD-9 caso 5 (c)")
            self.assertEqual(
                fd.get("status"), "absent",
                msg="PD-9 (caso 5): la traza neutral sigue sin despacho "
                    f"(fue {fd.get('status')!r}) — nunca se inventa uno")
            cause = str(fd.get("cause") or "")
            self.assertTrue(
                cause.strip(),
                msg="PD-9 (caso 5): la causa de ausencia no es vacía")
            self.assertIn(
                "event", cause.lower(),
                msg="PD-9 (caso 5): la causa conserva el límite honesto — "
                    "un despacho es un EVENTO (fue "
                    f"{fd.get('cause')!r})")
            self.assertTrue(
                ("utility" in cause.lower()
                 or "accepted" in cause.lower()),
                msg="PD-9 (caso 5): la causa conserva el límite honesto — "
                    "el despacho NO es prueba de utilidad ni de resultado "
                    f"aceptado (fue {fd.get('cause')!r})")


if __name__ == "__main__":
    unittest.main()
