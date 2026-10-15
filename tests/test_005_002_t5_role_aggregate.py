#!/usr/bin/env python3
"""005-002 T5 (REAPERTURA ACOTADA — hallazgo **R1**, BLOCKING) — cobertura
DECLARADA en el agregado por ROL: un subtotal PARCIAL nunca se presenta como
el total completo del rol.

Contract:
- docs/specs/005-002-session-context-meter/spec.md (PD-1: «el agregado por rol
  existe»; §2 `roles[]` = `{ role, sums, distributions }`; PD-4/INV-4: un
  valor nulo/ausente/no reportado se informa `unknown` CON causa, NUNCA `0`;
  PD-16: forma del registro neutral).
- docs/specs/005-002-session-context-meter/review-reopen-2026-10-12.md
  (hallazgo **R1**, BLOCKING bajo el criterio de review vigente 2026-10-12:
  `roles[].sums` agrega los valores OBSERVADOS de las sesiones del rol y los
  presenta como el total del rol, SIN declarar cobertura — con dos sesiones
  del mismo rol, una que reporta tokens/costo y otra que no, el documento
  publica `accumulated`/`cache.read`/`cost` como números completos (p. ej.
  `cost = 0.75` con `sessions = 2`), sin cubo, sin cobertura y sin causa a
  nivel de rol. Es la MISMA CLASE de defecto que la reapertura corrige a
  nivel de sesión/tramo — un subtotal parcial presentado como completo —
  una dimensión arriba. El reference ya publica el principio para el tramo
  («complete only with full coverage of the stretch»): se aplica al agregado
  por rol).

ORÁCULO: la SALIDA del WRAPPER fino `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable) — NUNCA importando el
módulo. Sin aserciones sobre nombres internos de funciones/clases/módulos;
sin mocks sobre el plumbing. El test-writer NO lee la implementación; el
contrato observable es el JSON por stdout, el rc y el stderr.

INTERFAZ DECLARADA POR ESTE TEST (el implementer la satisface leyendo el
test; fijada por el orquestador para cerrar R1):

  1. Cada componente SUMADO en `roles[].sums` deja de ser un número plano y
     pasa a ser una entrada DECLARADA con las claves:
     `{ value, unit, bucket, sessions_reporting, sessions_total, cause }`.
       - Si TODAS las sesiones del rol reportan ese componente
         (`sessions_reporting == sessions_total`): `bucket == "observed"`,
         `value` = la suma, `cause` null.
       - Si ALGUNA no lo reporta (`sessions_reporting < sessions_total`):
         `bucket == "unknown"`, `value` null (NUNCA la suma parcial
         presentada como completa) y `cause` con el texto que declara la
         cobertura, p. ej. «roles[<rol>]: cost is reported by 1 of 2
         sessions; the sum would be a partial subtotal, so it is not
         emitted».
       - `sessions_reporting` y `sessions_total` son SIEMPRE números (pueden
         ser 0), nunca null.
  2. El conteo de sesiones agregadas `sums.sessions` sigue siendo un número
     entero: es un conteo de miembros, no una suma de medida (0 es un conteo
     real, no un cero fabricado).
  3. MISMA CLASE en `roles[].distributions`: si el rol publica una
     distribución (p. ej. `total_output_chars`), sus valores van declarados
     con su cobertura: `{ values: [...], sessions_reporting: k,
     sessions_total: n, cause: null|texto }`. Un subconjunto NUNCA se
     presenta como el conjunto del rol.
  4. UNA causa AGREGADA por rol y por componente en `unknowns[]` cuando la
     cobertura es incompleta: UNA entrada por (rol, componente), acotada,
     que nombre el rol, el componente y la cobertura (k de n). NUNCA una
     entrada por sesión (el límite de 16384 bytes sigue vigente).
  5. rc == 0 y el resto del documento no cambia: las sesiones, las medidas
     por sesión, los hitos, los cubos por sesión y los valores pinneados de
     las muestras siguen igual (esta unidad cambia SOLO la forma del
     agregado por rol).

Postcondiciones cubiertas (un test por postcondición, con el hallazgo R1
nombrado en el docstring):

  1. [R1] Caso COMPLETO: dos sesiones del MISMO rol, ambas reportan
     tokens/costo → las sumas quedan bucket `observed`, `value` = la suma,
     `sessions_reporting == sessions_total`, `cause` null; `sessions` sigue
     entero.
  2. [R1] Caso PARCIAL (el defecto): dos sesiones del mismo rol, UNA reporta
     tokens/costo y la otra NO → las sumas quedan bucket `unknown` con
     `value` null (NUNCA el subtotal 100/50/0.5), `sessions_reporting = 1`,
     `sessions_total = 2`, con `cause`; y hay UNA causa agregada en
     `unknowns[]` que nombra el rol y el componente con su cobertura
     (1 de 2) — nunca una por sesión.
  3. [R1] Caso TOTAL: si un componente no lo reporta NINGUNA sesión, su
     entrada queda bucket `unknown` con `value` null (NUNCA `0` como valor
     observado) y `sessions_reporting = 0`.
  4. [R1] DISTRIBUCIÓN con cobertura parcial: sus valores van declarados con
     su cobertura (`values`/`sessions_reporting`/`sessions_total`/`cause`);
     un subconjunto NUNCA se presenta como el conjunto del rol.

RED hoy (probado con el wrapper, sin leer la implementación): `roles[].sums`
publica números planos (`{"accumulated": 100, "cache.read": 50, "cost": 0.5,
"sessions": 2, ...}`) — el subtotal de la única sesión que reporta,
presentado como el total del rol, sin cubo ni cobertura ni causa; y
`roles[].distributions.total_output_chars` publica una lista plana. Cada test
falla por AssertionError de CONTRATO (comportamiento ausente), nunca por
ImportError/sintaxis/setup: el test NO importa el módulo del medidor.

Fixtures 100% SINTÉTICOS, construidos por este test en un directorio temporal
con SQLite, contenido inventado por este test (sesiones `sess-fixture-*`,
modelo `model-alpha`, provider `prov-a`). La base real del runtime JAMÁS se
abre ni se copia (PD-10/INV-7).
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

# Claves de una entrada DECLARADA del agregado por rol (interfaz fijada).
DECLARED_SUM_KEYS = ("value", "unit", "bucket", "sessions_reporting",
                     "sessions_total", "cause")
DECLARED_DIST_KEYS = ("values", "sessions_reporting", "sessions_total",
                      "cause")

DIST_KEY = "total_output_chars"

# Componentes SUMADOS del rol que cubre R1 (el ejemplo del hallazgo) y sus
# alias en las causas (el texto puede nombrar el componente por su clave del
# agregado o por su alias de la medida de sesión).
COMPONENTS = (
    ("accumulated", ("accumulated", "tokens.input")),
    ("cache.read", ("cache.read",)),
    ("cost", ("cost",)),
)

# Marcadores de «la suma NO es un total completo» en la causa agregada.
AGG_INCOMPLETE_WORDS = ("not a complete", "incomplete", "no completa",
                        "no es una observacion completa", "partial",
                        "parcial", "subtotal", "not emitted", "no emit",
                        "no se emite")

BUCKET_VALUES = ("observed", "estimated", "unknown")

# Roles/modelo/ids 100% SINTÉTICOS (inventados; nada de la base).
ROLE = "cdad-orchestrator"
MODEL = '{"id":"model-alpha","providerID":"prov-a"}'

SESSION_COMPLETE_A = "sess-fixture-role-complete-a"
SESSION_COMPLETE_B = "sess-fixture-role-complete-b"
SESSION_PARTIAL_A = "sess-fixture-role-partial-a"
SESSION_PARTIAL_B = "sess-fixture-role-partial-b"
SESSION_TOTAL_A = "sess-fixture-role-total-a"
SESSION_TOTAL_B = "sess-fixture-role-total-b"

BASE_MS = 1_760_000_000_000       # epoch ms SINTÉTICO, fijo (determinismo)
STEP_MS = 30_000                  # paso entre eventos sintéticos (ms)

# Caso COMPLETO: las DOS sesiones reportan tokens.input / cache.read / cost.
# La suma del rol es una observación completa de la cobertura.
COMPLETE_A_INPUT, COMPLETE_A_READ, COMPLETE_A_COST = 100, 50, 0.5
COMPLETE_B_INPUT, COMPLETE_B_READ, COMPLETE_B_COST = 20, 10, 0.25
COMPLETE_INPUT_SUM = COMPLETE_A_INPUT + COMPLETE_B_INPUT          # 120
COMPLETE_READ_SUM = COMPLETE_A_READ + COMPLETE_B_READ             # 60
COMPLETE_COST_SUM = COMPLETE_A_COST + COMPLETE_B_COST             # 0.75
COMPLETE_A_OUT, COMPLETE_B_OUT = 300, 120

# Caso PARCIAL (el defecto R1): A reporta tokens/costo; B NO reporta NADA
# (ni tokens, ni cost, ni salida). El agregado del rol cubre 1 de 2 sesiones:
# la suma de A (100 / 50 / 0.5) es un SUBTOTAL, nunca el total del rol.
PARTIAL_A_INPUT, PARTIAL_A_READ, PARTIAL_A_COST = 100, 50, 0.5
PARTIAL_A_OUT = 300

# Caso TOTAL: las dos sesiones reportan tokens (input/cache.read) pero
# NINGUNA reporta cost → la entrada del componente `cost` cubre 0 de 2
# sesiones (nunca el 0 como valor observado).
TOTAL_A_INPUT, TOTAL_A_READ = 10, 2
TOTAL_B_INPUT, TOTAL_B_READ = 20, 4
TOTAL_INPUT_SUM = TOTAL_A_INPUT + TOTAL_B_INPUT                   # 30
TOTAL_READ_SUM = TOTAL_A_READ + TOTAL_B_READ                      # 6

SESSIONS_PER_ROLE = 2

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
               ms) -> dict:
    """Parte `tool` (discovery §1.4): state.content = [{type:text, text}] →
    tamaño de salida = suma de len(text)."""
    return {
        "type": "tool", "id": part_id, "name": name, "executed": True,
        "state": {"status": "completed", "input": args,
                  "content": [{"type": "text", "text": text}]},
        "time": {"created": ms, "ran": ms, "completed": ms},
    }


def _assistant_data(parts: list, tokens, *, ms, cost=None) -> str:
    """Forma `assistant` (discovery §1.3). `tokens` None = AUSENTE
    (componente no reportado); `cost` None = costo no reportado."""
    doc: dict = {
        "time": _data_time(ms),
        "agent": ROLE, "model": MODEL, "content": parts,
    }
    if tokens is not None:
        doc["tokens"] = tokens
    doc["cost"] = cost
    return json.dumps(doc, sort_keys=True)


def _tokens_full(tin: int, tout: int, tread: int, twrite: int = 0) -> dict:
    """Tokens con los TRES componentes reportados; `twrite=0` REPORTADO
    cuenta como reportado (muestra 1)."""
    return {"input": tin, "output": tout, "reasoning": 0,
            "cache": {"read": tread, "write": twrite}}


def _user_data(ms) -> str:
    return json.dumps({"time": ms, "text": "fixture prompt sintetico"},
                      sort_keys=True)


def _insert_msg(conn: sqlite3.Connection, sid: str, seq: int, mtype: str,
                data: str, ms) -> None:
    conn.execute(
        "INSERT INTO session_message (id, session_id, type, seq,"
        " time_created, time_updated, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (f"msg-{seq:04d}-{sid}", sid, mtype, seq, ms, ms, data))


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


def _add_session(conn: sqlite3.Connection, sid: str, t0: float, *,
                 tokens, cost, output_len, sums) -> None:
    """Una sesión sintética con UN paso `assistant`: un mensaje `user` (seq 1)
    y el paso (seq 2). `tokens=None` = la sesión NO reporta tokens;
    `cost=None` = NO reporta costo; `output_len=None` = el paso NO porta una
    llamada de herramienta con salida (sin evidencia de salida)."""
    _insert_msg(conn, sid, 1, "user", _user_data(t0), t0)
    ms = t0 + STEP_MS
    parts: list = []
    if output_len is not None:
        parts = [_tool_part("read", "x" * output_len,
                            args={"path": "/fixture/dir/f"}, part_id="p2",
                            ms=ms)]
    _insert_msg(conn, sid, 2, "assistant",
                _assistant_data(parts, tokens, ms=ms, cost=cost), ms)
    _insert_session(conn, sid, t0, ms + STEP_MS, sums, cost)


def _build_complete(path: Path) -> None:
    """Caso COMPLETO: dos sesiones del MISMO rol, las DOS reportan tokens y
    costo (y salida) → la suma del rol es una observación COMPLETA."""
    conn = _new_store(path)
    t0 = BASE_MS + 10_000_000
    _add_session(conn, SESSION_COMPLETE_A, t0,
                 tokens=_tokens_full(COMPLETE_A_INPUT, 5, COMPLETE_A_READ),
                 cost=COMPLETE_A_COST, output_len=COMPLETE_A_OUT,
                 sums=(COMPLETE_A_INPUT, 5, 0, COMPLETE_A_READ, 0))
    _add_session(conn, SESSION_COMPLETE_B, t0 + 5_000_000,
                 tokens=_tokens_full(COMPLETE_B_INPUT, 5, COMPLETE_B_READ),
                 cost=COMPLETE_B_COST, output_len=COMPLETE_B_OUT,
                 sums=(COMPLETE_B_INPUT, 5, 0, COMPLETE_B_READ, 0))
    conn.commit()
    conn.close()


def _build_partial(path: Path) -> None:
    """Caso PARCIAL (el defecto R1): dos sesiones del MISMO rol; A reporta
    tokens/costo/salida, B NO reporta nada → el agregado del rol cubre 1 de 2
    sesiones y la suma de A es un SUBTOTAL, nunca el total del rol."""
    conn = _new_store(path)
    t0 = BASE_MS + 20_000_000
    _add_session(conn, SESSION_PARTIAL_A, t0,
                 tokens=_tokens_full(PARTIAL_A_INPUT, 5, PARTIAL_A_READ),
                 cost=PARTIAL_A_COST, output_len=PARTIAL_A_OUT,
                 sums=(PARTIAL_A_INPUT, 5, 0, PARTIAL_A_READ, 0))
    _add_session(conn, SESSION_PARTIAL_B, t0 + 5_000_000,
                 tokens=None, cost=None, output_len=None,
                 sums=(0, 0, 0, 0, 0))
    conn.commit()
    conn.close()


def _build_total(path: Path) -> None:
    """Caso TOTAL: dos sesiones del MISMO rol; las dos reportan tokens
    (input/cache.read) pero NINGUNA reporta costo → la entrada `cost` cubre
    0 de 2 sesiones (nunca un 0 presentado como valor observado)."""
    conn = _new_store(path)
    t0 = BASE_MS + 30_000_000
    _add_session(conn, SESSION_TOTAL_A, t0,
                 tokens=_tokens_full(TOTAL_A_INPUT, 1, TOTAL_A_READ),
                 cost=None, output_len=5,
                 sums=(TOTAL_A_INPUT, 1, 0, TOTAL_A_READ, 0))
    _add_session(conn, SESSION_TOTAL_B, t0 + 5_000_000,
                 tokens=_tokens_full(TOTAL_B_INPUT, 1, TOTAL_B_READ),
                 cost=None, output_len=7,
                 sums=(TOTAL_B_INPUT, 1, 0, TOTAL_B_READ, 0))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- helpers

def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _coverage_pattern(reporting: int, total: int) -> re.Pattern:
    """Cobertura «k de n» (acepta «k of n», «k de n», «k/n»)."""
    return re.compile(
        r"(?<!\d)%d(?!\d)[^\d]{0,40}(?:of|de|/)[^\d]{0,15}(?<!\d)%d(?!\d)"
        % (reporting, total))


class RoleAggregateT5Test(unittest.TestCase):
    """T5 RED de 005-002 (reapertura acotada, hallazgo R1): cobertura
    declarada en el agregado por rol, contra la SALIDA del wrapper."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-role-agg-")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.store_complete = base / "complete" / "sessions.db"
        self.store_partial = base / "partial" / "sessions.db"
        self.store_total = base / "total" / "sessions.db"
        _build_complete(self.store_complete)
        _build_partial(self.store_partial)
        _build_total(self.store_total)

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

    def run_ok(self, store: Path, label: str):
        proc = self.run_meter("--store", str(store))
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
        return doc

    def role_entry(self, doc: dict, label: str) -> dict:
        roles = doc.get("roles")
        self.assertIsInstance(
            roles, list,
            msg=f"{label}: roles[] existe (agregado por rol; PD-1)")
        entry = next((r for r in roles
                      if isinstance(r, dict) and r.get("role") == ROLE), None)
        self.assertIsNotNone(
            entry,
            msg=f"{label}: el rol {ROLE!r} está agregado en roles[] "
                f"(fue {[r.get('role') for r in roles if isinstance(r, dict)]!r})")
        return entry

    def declared_sum(self, sums: object, key: str, label: str) -> dict:
        """Entrada DECLARADA de `sums[key]` (R1): dict con las claves
        `value/unit/bucket/sessions_reporting/sessions_total/cause`; HOY es un
        número plano — RED de contrato."""
        self.assertIsInstance(sums, dict, msg=f"{label}: sums es objeto")
        self.assertIn(
            key, sums,
            msg=f"{label}: el componente `{key}` está declarado en "
                f"roles[].sums (hoy suma plano y no declara cobertura; claves "
                f"presentes: {sorted(sums)!r})")
        entry = sums[key]
        self.assertIsInstance(
            entry, dict,
            msg=f"{label}: `{key}` es una entrada DECLARADA "
                f"{{value, unit, bucket, sessions_reporting, sessions_total, "
                f"cause}} — NUNCA un número plano (fue {entry!r}; R1)")
        for field in DECLARED_SUM_KEYS:
            self.assertIn(
                field, entry,
                msg=f"{label}: la entrada declarada `{key}` trae {field!r} "
                    f"(fue {entry!r})")
        return entry

    def declared_dist(self, distributions: object, key: str,
                      label: str) -> dict:
        self.assertIsInstance(distributions, dict,
                              msg=f"{label}: distributions es objeto")
        self.assertIn(
            key, distributions,
            msg=f"{label}: el rol publica la distribución {key!r} (claves "
                f"presentes: {sorted(distributions)!r})")
        entry = distributions[key]
        self.assertIsInstance(
            entry, dict,
            msg=f"{label}: la distribución `{key}` va DECLARADA con su "
                "cobertura {{values, sessions_reporting, sessions_total, "
                f"cause}} — NUNCA una lista plana (fue {entry!r}; R1)")
        for field in DECLARED_DIST_KEYS:
            self.assertIn(
                field, entry,
                msg=f"{label}: la distribución declarada `{key}` trae "
                    f"{field!r} (fue {entry!r})")
        return entry

    def unknown_texts(self, doc: dict) -> list:
        unknowns = doc.get("unknowns", [])
        self.assertIsInstance(unknowns, list, msg="unknowns[] es lista")
        return [(entry if isinstance(entry, str)
                 else json.dumps(entry, sort_keys=True)).lower()
                for entry in unknowns]

    def role_coverage_hits(self, texts: list, component_aliases: tuple,
                           reporting: int, total: int) -> list:
        """Entradas de unknowns[] que son la CAUSA AGREGADA por (rol,
        componente): nombran el ROL, el componente (o su alias) y declaran la
        cobertura «k de n» del agregado por rol."""
        pat = _coverage_pattern(reporting, total)
        return [
            t for t in texts
            if ROLE.lower() in t
            and any(alias.lower() in t for alias in component_aliases)
            and pat.search(t)
        ]

    def assert_sessions_count_is_int(self, sums: dict, label: str) -> None:
        """Interfaz (2): `sums.sessions` es un conteo de miembros — entero,
        nunca una entrada declarada ni null."""
        self.assertIn("sessions", sums,
                      msg=f"{label}: sums.sessions (conteo de miembros) sigue "
                          f"presente (fue {sorted(sums)!r})")
        count = sums["sessions"]
        self.assertIsInstance(
            count, int,
            msg=f"{label}: sums.sessions es un ENTERO (conteo de miembros, no "
                f"una suma de medida; fue {count!r})")
        self.assertNotIsInstance(count, bool,
                                 msg=f"{label}: sessions no es bool")
        self.assertEqual(
            count, SESSIONS_PER_ROLE,
            msg=f"{label}: sessions cuenta las {SESSIONS_PER_ROLE} sesiones "
                f"del rol (fue {count!r})")

    # ------------------------------------------------- (1) [R1] completo

    def test_t5_role_1_r1_complete_sums_declared_observed(self):
        """[R1] Caso COMPLETO: dos sesiones del MISMO rol, AMBAS reportan
        tokens/costo/salida. Cada componente sumado del rol
        (`accumulated`/`cache.read`/`cost`) va DECLARADO con su cobertura:
        bucket `observed`, `value` = la suma completa, `sessions_reporting ==
        sessions_total == 2`, `cause` null; no hay causa agregada por rol. El
        conteo `sessions` sigue siendo un entero. PD-1 (el agregado por rol
        existe), PD-4/INV-4, PD-16; cierra la mitad «con cobertura completa»
        de R1 (review-reopen-2026-10-12)."""
        label = "R1(1) completo"
        doc = self.run_ok(self.store_complete, label)
        entry = self.role_entry(doc, label)
        sums = entry.get("sums")
        self.assert_sessions_count_is_int(sums, label)
        for key, want in (("accumulated", COMPLETE_INPUT_SUM),
                          ("cache.read", COMPLETE_READ_SUM),
                          ("cost", COMPLETE_COST_SUM)):
            leaf = self.declared_sum(sums, key, label)
            self.assertEqual(
                leaf.get("bucket"), "observed",
                msg=f"{label}: con TODAS las sesiones del rol reportando "
                    f"`{key}` la suma es una observación completa "
                    f"(`observed`); fue {leaf.get('bucket')!r}")
            value = leaf.get("value")
            self.assertTrue(_is_number(value),
                            msg=f"{label}: `{key}` value numérico observado "
                                f"(fue {value!r})")
            self.assertAlmostEqual(
                value, want, places=6,
                msg=f"{label}: la suma completa de `{key}` es {want} "
                    f"(fue {value!r})")
            self.assertEqual(
                leaf.get("sessions_reporting"), SESSIONS_PER_ROLE,
                msg=f"{label}: `{key}` declara cuántas sesiones lo reportan: "
                    f"{SESSIONS_PER_ROLE} (fue {leaf.get('sessions_reporting')!r})")
            self.assertEqual(
                leaf.get("sessions_total"), SESSIONS_PER_ROLE,
                msg=f"{label}: `{key}` declara el total de sesiones del rol: "
                    f"{SESSIONS_PER_ROLE} (fue {leaf.get('sessions_total')!r})")
            self.assertIsNone(
                leaf.get("cause"),
                msg=f"{label}: con cobertura completa `{key}` no tiene causa "
                    f"(fue {leaf.get('cause')!r})")
        # no hay causa agregada por rol para estos componentes (cobertura
        # completa): el conjunto de componentes con cobertura incompleta es
        # vacío a nivel de rol.
        texts = self.unknown_texts(doc)
        for key, aliases in COMPONENTS:
            hits = self.role_coverage_hits(
                texts, aliases, SESSIONS_PER_ROLE, SESSIONS_PER_ROLE)
            self.assertEqual(
                len(hits), 0,
                msg=f"{label}: con cobertura completa NO hay causa agregada "
                    f"por rol para `{key}` (hits={hits!r})")

    # -------------------------------------------------- (2) [R1] parcial

    def test_t5_role_2_r1_partial_sums_unknown_not_subtotal(self):
        """[R1 — el defecto] Caso PARCIAL: dos sesiones del MISMO rol, UNA
        reporta tokens/costo y la otra NO. Cada componente sumado del rol
        queda bucket `unknown` con `value` null (NUNCA el subtotal parcial
        100/50/0.5 presentado como completo), `sessions_reporting = 1`,
        `sessions_total = 2` y una `cause` que declara la cobertura; y hay UNA
        causa AGREGADA por (rol, componente) en `unknowns[]` que nombra el rol,
        el componente y la cobertura (1 de 2) — nunca una por sesión. PD-1,
        PD-4/INV-4, PD-16; es el hallazgo R1 (subtotal parcial presentado como
        el total del rol)."""
        label = "R1(2) parcial"
        doc = self.run_ok(self.store_partial, label)
        entry = self.role_entry(doc, label)
        sums = entry.get("sums")
        self.assert_sessions_count_is_int(sums, label)
        texts = self.unknown_texts(doc)
        for key, aliases, partial in (
                ("accumulated", ("accumulated", "tokens.input"),
                 PARTIAL_A_INPUT),
                ("cache.read", ("cache.read",), PARTIAL_A_READ),
                ("cost", ("cost",), PARTIAL_A_COST)):
            leaf = self.declared_sum(sums, key, label)
            self.assertIn(
                leaf.get("bucket"), BUCKET_VALUES,
                msg=f"{label}: `{key}` bucket declarado (fue "
                    f"{leaf.get('bucket')!r})")
            self.assertEqual(
                leaf.get("bucket"), "unknown",
                msg=f"{label}: `{key}` NO es una observación completa (solo 1 "
                    f"de {SESSIONS_PER_ROLE} sesiones lo reporta) → bucket "
                    f"`unknown` (fue {leaf.get('bucket')!r})")
            self.assertIsNone(
                leaf.get("value"),
                msg=f"{label}: `{key}` value null — NUNCA el subtotal parcial "
                    f"{partial} presentado como el total del rol (fue "
                    f"{leaf.get('value')!r}; R1)")
            self.assertEqual(
                leaf.get("sessions_reporting"), 1,
                msg=f"{label}: `{key}` declara que 1 de {SESSIONS_PER_ROLE} "
                    f"sesiones lo reporta (fue {leaf.get('sessions_reporting')!r})")
            self.assertEqual(
                leaf.get("sessions_total"), SESSIONS_PER_ROLE,
                msg=f"{label}: `{key}` declara el total de sesiones del rol "
                    f"(fue {leaf.get('sessions_total')!r})")
            cause = leaf.get("cause")
            self.assertIsInstance(
                cause, str,
                msg=f"{label}: `{key}` trae una CAUSA que declara la "
                    f"cobertura (fue {cause!r})")
            self.assertTrue(cause.strip(),
                            msg=f"{label}: la causa de `{key}` no es vacía")
            # UNA causa AGREGADA por (rol, componente) en unknowns[].
            hits = self.role_coverage_hits(texts, aliases, 1,
                                           SESSIONS_PER_ROLE)
            self.assertEqual(
                len(hits), 1,
                msg=f"{label}: `{key}` declara UNA causa AGREGADA por (rol, "
                    "componente) en unknowns[] (nunca una por sesión) que "
                    "nombra el rol, el componente y la cobertura (1 de 2) "
                    f"(hits={hits!r}; textos={texts!r})")
            low = hits[0]
            self.assertTrue(
                any(word in low for word in AGG_INCOMPLETE_WORDS),
                msg=f"{label}: la causa agregada de `{key}` declara que la "
                    f"suma NO es un total completo (fue {hits[0]!r})")

    # ---------------------------------------------------- (3) [R1] total

    def test_t5_role_3_r1_no_session_reports_component_zero_coverage(self):
        """[R1] Caso TOTAL: dos sesiones del MISMO rol; las dos reportan
        tokens (control: `accumulated`/`cache.read` quedan `observed` con
        cobertura completa) pero NINGUNA reporta costo → la entrada `cost`
        queda bucket `unknown` con `value` null (NUNCA `0` como valor
        observado) y `sessions_reporting = 0` sobre `sessions_total = 2`, con
        su causa agregada por rol (0 de 2). PD-1, PD-4/INV-4 («desconocido no
        es cero»), PD-16; cierra la mitad «ninguna sesión reporta» de R1."""
        label = "R1(3) total"
        doc = self.run_ok(self.store_total, label)
        entry = self.role_entry(doc, label)
        sums = entry.get("sums")
        self.assert_sessions_count_is_int(sums, label)
        # control: los componentes que SÍ reportan ambas sesiones quedan
        # observados con cobertura completa.
        for key, want in (("accumulated", TOTAL_INPUT_SUM),
                          ("cache.read", TOTAL_READ_SUM)):
            leaf = self.declared_sum(sums, key, label + " (control)")
            self.assertEqual(
                leaf.get("bucket"), "observed",
                msg=f"{label}: control — `{key}` con cobertura completa queda "
                    f"`observed` (fue {leaf.get('bucket')!r})")
            self.assertAlmostEqual(leaf.get("value"), want, places=6,
                                   msg=f"{label}: control — `{key}` = {want}")
            self.assertEqual(leaf.get("sessions_reporting"),
                             SESSIONS_PER_ROLE)
        # el caso TOTAL: NINGUNA sesión reporta `cost`.
        leaf = self.declared_sum(sums, "cost", label)
        self.assertEqual(
            leaf.get("bucket"), "unknown",
            msg=f"{label}: `cost` no lo reporta NINGUNA sesión → bucket "
                f"`unknown` (fue {leaf.get('bucket')!r})")
        self.assertIsNone(
            leaf.get("value"),
            msg=f"{label}: `cost` value null — NUNCA `0` presentado como "
                f"valor observado (fue {leaf.get('value')!r}; PD-4/INV-4)")
        self.assertEqual(
            leaf.get("sessions_reporting"), 0,
            msg=f"{label}: `cost` declara que 0 sesiones lo reportan (fue "
                f"{leaf.get('sessions_reporting')!r})")
        self.assertEqual(
            leaf.get("sessions_total"), SESSIONS_PER_ROLE,
            msg=f"{label}: `cost` declara el total de sesiones del rol (fue "
                f"{leaf.get('sessions_total')!r})")
        cause = leaf.get("cause")
        self.assertIsInstance(
            cause, str,
            msg=f"{label}: `cost` trae una CAUSA que declara la cobertura "
                f"(fue {cause!r})")
        self.assertTrue(cause.strip(),
                        msg=f"{label}: la causa de `cost` no es vacía")
        texts = self.unknown_texts(doc)
        hits = self.role_coverage_hits(texts, ("cost",), 0,
                                       SESSIONS_PER_ROLE)
        self.assertEqual(
            len(hits), 1,
            msg=f"{label}: `cost` declara UNA causa agregada por (rol, "
                "componente) con la cobertura (0 de 2) (hits="
                f"{hits!r}; textos={texts!r})")

    # --------------------------------------------- (4) [R1] distribución

    def test_t5_role_4_r1_distribution_declares_coverage(self):
        """[R1] MISMA CLASE en `distributions`: cuando el rol publica una
        distribución (`total_output_chars`), sus valores van DECLARADOS con su
        cobertura (`{values, sessions_reporting, sessions_total, cause}`). Con
        cobertura parcial (una de dos sesiones porta salida) `values` porta
        solo la evidencia observada (un subconjunto NUNCA se presenta como el
        conjunto del rol), `sessions_reporting = 1`, `sessions_total = 2` y hay
        causa; con cobertura completa (control positivo) `sessions_reporting ==
        sessions_total == 2` y `cause` null. PD-1, PD-4/INV-4, PD-16; cierra la
        mitad «distribución» de R1."""
        label = "R1(4) distribución"
        # cobertura PARCIAL: solo A porta salida.
        doc = self.run_ok(self.store_partial, label)
        entry = self.role_entry(doc, label)
        dist = self.declared_dist(entry.get("distributions"), DIST_KEY, label)
        values = dist.get("values")
        self.assertIsInstance(
            values, list,
            msg=f"{label}: `{DIST_KEY}` declara sus valores en `values` (fue "
                f"{values!r})")
        self.assertEqual(
            sorted(values), [PARTIAL_A_OUT],
            msg=f"{label}: `values` porta la evidencia de las sesiones que la "
                "reportan (una de dos: "
                f"{PARTIAL_A_OUT}) — un subconjunto NUNCA se presenta como el "
                f"conjunto del rol (fue {values!r})")
        self.assertEqual(
            dist.get("sessions_reporting"), 1,
            msg=f"{label}: la distribución declara que 1 de "
                f"{SESSIONS_PER_ROLE} sesiones la reporta (fue "
                f"{dist.get('sessions_reporting')!r})")
        self.assertEqual(
            dist.get("sessions_total"), SESSIONS_PER_ROLE,
            msg=f"{label}: la distribución declara el total de sesiones del "
                f"rol (fue {dist.get('sessions_total')!r})")
        self.assertIsInstance(
            dist.get("cause"), str,
            msg=f"{label}: con cobertura parcial la distribución trae causa "
                f"(fue {dist.get('cause')!r})")
        self.assertTrue(dist.get("cause").strip(),
                        msg=f"{label}: la causa de la distribución no es vacía")
        texts = self.unknown_texts(doc)
        hits = self.role_coverage_hits(texts, (DIST_KEY,), 1,
                                       SESSIONS_PER_ROLE)
        self.assertEqual(
            len(hits), 1,
            msg=f"{label}: la cobertura parcial de la distribución se declara "
                "en UNA causa agregada por (rol, componente) (hits="
                f"{hits!r}; textos={texts!r})")
        # control positivo: cobertura COMPLETA.
        control = label + " (control completo)"
        doc_c = self.run_ok(self.store_complete, control)
        entry_c = self.role_entry(doc_c, control)
        dist_c = self.declared_dist(entry_c.get("distributions"), DIST_KEY,
                                    control)
        self.assertEqual(
            sorted(dist_c.get("values")),
            sorted([COMPLETE_A_OUT, COMPLETE_B_OUT]),
            msg=f"{control}: con las dos sesiones reportando, `values` porta "
                f"las dos (fue {dist_c.get('values')!r})")
        self.assertEqual(
            dist_c.get("sessions_reporting"), SESSIONS_PER_ROLE,
            msg=f"{control}: cobertura completa (fue "
                f"{dist_c.get('sessions_reporting')!r})")
        self.assertEqual(
            dist_c.get("sessions_total"), SESSIONS_PER_ROLE,
            msg=f"{control}: total de sesiones del rol (fue "
                f"{dist_c.get('sessions_total')!r})")
        self.assertIsNone(
            dist_c.get("cause"),
            msg=f"{control}: con cobertura completa la distribución no tiene "
                f"causa (fue {dist_c.get('cause')!r})")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
