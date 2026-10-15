#!/usr/bin/env python3
"""005-002 T3 RED — informe de aplicación (anotación referenciada), privacidad
y salida compacta con referencias (PD-9, PD-10, PD-12).

Contract:
- docs/specs/005-002-session-context-meter/spec.md (§2; PD-9, PD-10, PD-12;
  INV-7, INV-8).
- docs/specs/005-002-session-context-meter/plan.md (T3: ficha de la tarea:
  «RED: no hay anotación; no existe la forma ref/limit/basis; ...»).
- docs/specs/005-002-session-context-meter/discovery.md §1.2–§1.6 (forma del
  esquema de los fixtures; el CONTENIDO es 100% sintético, inventado aquí,
  en un directorio temporal con SQLite: la base real del runtime JAMÁS se
  abre ni se copia).

BANDERAS de la anotación de aplicación DECLARADAS por este test (el orquestador
fija que la anotación llega como ENTRADA explícita del medidor: el lector NO
juzga y NUNCA aprueba nada; con estas banderas el GREEN puede satisfacer el
contrato leyendo este test):

- ``--application-ref REF`` — referencia durable (ruta/commit/recibo) que el
  medidor TRANSPORTA tal como se pasa. NO copia el contenido del archivo
  referenciado: el fixture crea un archivo con un marcador propio y el test
  afirma que ese marcador NO aparece en la salida.
- ``--application-limit {accepted,blocked,pending,unknown}`` — el límite
  declarado del informe de aplicación (conjunto fijado por la spec, PD-9).

Sin esas banderas: la anotación NO aparece, o bien queda ``unknown`` CON CAUSA
(ambas formas aceptadas; el lector nunca la inventa ni aprueba nada).

LÍMITE DE BYTES de PD-12: fijado por el ORQUESTADOR (número normativo): el
documento emitido para UNA sesión no puede superar 16384 bytes (16 KiB). El
implementer lo declara en el reference `skills/cdad-cycle/references/
context-meter.md`; este test verifica el número EN EL COMPORTAMIENTO.

Oracle observable: la SALIDA del WRAPPER FINO `scripts/cdad_context_meter.py`,
invocado SIEMPRE por subproceso (sys.executable), NUNCA importando el módulo.
Contrato observable = JSON por stdout + rc + diagnóstico por stderr. Sin
aserciones sobre nombres internos de funciones/clases/módulos ni plumbing;
sin mocks.

El campo `model` por sesión SI es contrato (la spec lo exige, parseado o
`unknown`): su presencia en la salida NO es una fuga. Lo que la salida NO
puede contener (PD-10): rutas absolutas del host, la ruta del store, el
identificador crudo de sesión, y el texto crudo de prompts o de salidas de
herramientas.

RED hoy: la implementación del GREEN de T1/T2 no transporta la anotación (las
banderas ni siquiera se aceptan: rc != 0), no declara sesiones incluidas ni
relaciones, y no declara `unknown` el enlace al padre ausente. Cada aserción
fracasa por AssertionError de CONTRATO, nunca por ImportError/sintaxis/setup:
el test NO importa el módulo del medidor.
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

# El fixture de la muestra 1 (101 llamadas en el tramo / 121 en la sesión y
# los helpers de forma del esquema) se toma del paquete T2: mismas cifras
# pinneadas, mismo esquema observado (conftest garantiza `tests.` importable).
from tests.test_005_002_t2_milestones import (
    BASE_MS,
    DISPATCH_TOOL,
    MODEL_SYNTH,
    RESUME_REAL_CMD,
    ROLE,
    _assistant_data,
    _build_muestra1,
    _insert_msg,
    _measure_leaves,
    _new_store,
    _tool_part,
    _user_data,
)

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
METER_WRAPPER = REPO_ROOT / "scripts" / "cdad_context_meter.py"  # wrapper fino

FEATURE_ID = "005-002-session-context-meter"
STORE_ENV_VAR = "CDAD_CONTEXT_METER_STORE"
CLI_TIMEOUT_S = 120

# --- anotación de aplicación (PD-9): BANDERAS DECLARADAS POR ESTE TEST ---
APP_REF_FLAG = "--application-ref"
APP_LIMIT_FLAG = "--application-limit"
APP_LIMIT_VALUES = ("accepted", "blocked", "pending", "unknown")
# forma fijada de la anotación (spec PD-9); included_sessions/relations
# declaradas por el documento del tramo que las combina.
APP_ON_REQUIRED_KEYS = ("ref", "limit", "basis")
APP_ON_ALLOWED_KEYS = {"ref", "limit", "basis", "included_sessions", "relations"}
APP_FORBIDDEN_KEY_WORD = "approv"  # el lector NUNCA aprueba (INV-9)

# --- límite de bytes de PD-12: fijado por el ORQUESTADOR (normativo) ---
PD12_BYTE_LIMIT = 16_384  # 16 KiB; NO lo elige ni lo relaja este test

# --- dispositivos sintéticos (100% inventados; nada de la base real) ---
SESSION_APP = "sess-fixture-app-single"
SESSION_PARENT = "sess-fixture-app-parent"
SESSION_CHILD = "sess-fixture-app-child"
SESSION_MISSING_PARENT = "sess-fixture-app-missing-parent"

ROLE_FIX = ROLE          # rol sintético del paquete T2
MODEL_FIX = MODEL_SYNTH  # modelo sintético del paquete T2
MODEL_ID_FIX = "model-alpha"  # id parseable dentro de MODEL_FIX

REF_MARKER = "APP-RECEIPT-MARKER RE7Q0F 005-002-T3"
PROMPT_MARKER = "PROMPT-MARKER-FX3D 005-002-T3 (inventado)"
TOOL_OUT_A = "TOOL-OUT-MARKER-KK81 005-002-T3 (inventado)\n"
TOOL_OUT_B = "TOOL-OUT-MARKER-ZZ42 005-002-T3 (inventado)\n"

# costos sintéticos del par padre/hijo (PD-9: sin doble conteo)
PARENT_COST = 0.80   # pasos 0.5 + 0.2 + 0.1
CHILD_COST = 0.30    # pasos 0.2 + 0.1
FAMILY_TOTAL_COST = PARENT_COST + CHILD_COST      # 1.10 — costo real
FAMILY_DOUBLE_COST = FAMILY_TOTAL_COST * 2        # 2.20 — doble conteo

ORPHAN_COST = 0.15  # (referencia de costo del fixture huérfano)
APP_SINGLE_COST = 0.40

M1_SESSION_ID = "sess-fixture-muestra1"  # id crudo del fixture T2


# ---------------------------------------------------------------- fixtures

def _orig_parent(conn: sqlite3.Connection, sid: str, agent: str, model: str,
                 t0: float, t_end: float, sums: tuple,
                 cost: float | None) -> None:
    """Fila completa `session_v2` (forma discovery §1.2; el contenido es
    sintético). Duplicado deliberado del insert del paquete T2: este test es
    un oráculo independiente y no comparte ESTADO con T2."""
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
         "slug-" + sid, "/fixture/dir", "/fixture/dir",
         "fixture " + sid, "fixture-version", None, 0, 0, 0, 0, None, cost,
         tin, tout, treason, tread, twrite, None, None, agent, model,
         t0, t_end, None, None, None, 0, None, None, None))


def _set_parent(conn, sid: str, parent_id: str | None) -> None:
    """Columna de relación del fixture (`parent_id`; discovery §1.2)."""
    conn.execute("UPDATE session_v2 SET parent_id=? WHERE id=?",
                 (parent_id, sid))


def _tool_call(conn, sid, seq, name, args, text, ms, *, cost=None) -> None:
    """Un paso del fixture: mensaje `assistant` con UNA parte tool
    (discovery §1.4). time_created == time_updated."""
    tin, tread = 210 + 10 * seq, 300 + 10 * seq
    _insert_msg(conn, sid, seq, "assistant",
                _assistant_data(ROLE_FIX, MODEL_FIX, ms,
                                [_tool_part(name, text, ms, input_args=args,
                                            part_id=f"p{seq}")],
                                (tin, 40, 10, tread, 0), cost),
                ms)


def _build_app_single(path: Path) -> None:
    """Fixture de UNA sesión con los marcadores de privacidad (PD-10): un
    prompt con cadena única, salidas de herramienta con cadenas únicas, un
    resume real (hito observado con posición) y un despacho (subagent)."""
    conn = _new_store(path)
    t0 = BASE_MS + 41_000_000_000
    _insert_msg(conn, SESSION_APP, 1, "user",
                _user_data(t0, PROMPT_MARKER + "\n"), t0)
    steps = (("read", {"path": "/fixture/dir/a.md"}, TOOL_OUT_A),
             ("shell", {"command": RESUME_REAL_CMD}, "resumen ok\n"),
             (DISPATCH_TOOL, {"path": "/fixture/dir/b.md"}, TOOL_OUT_B))
    sums = [0, 0, 0, 0, 0]
    for i, (name, args, text) in enumerate(steps, start=1):
        seq = 1 + i
        ms = t0 + i * 60_000
        _tool_call(conn, SESSION_APP, seq, name, args, text, ms,
                   cost=APP_SINGLE_COST)
        sums[0] += 210 + 10 * seq
        sums[1] += 40
        sums[2] += 10
        sums[3] += 300 + 10 * seq
    total_ms = t0 + (len(steps) + 1) * 60_000
    _orig_parent(conn, SESSION_APP, ROLE_FIX, MODEL_FIX, t0, total_ms,
                 tuple(sums), APP_SINGLE_COST)
    conn.commit()
    conn.close()


def _add_session(conn, sid, parent_id, tstart, steps_cost):
    """Sesión simple: user + llamadas con costos por paso; fila session_v2
    con `parent_id` (o None) y cost total = suma de pasos."""
    _insert_msg(conn, sid, 1, "user",
                _user_data(tstart, "arranque de " + sid + "\n"), tstart)
    sums = [0, 0, 0, 0, 0]
    for i, (name, cost) in enumerate(steps_cost, start=1):
        seq = 1 + i
        ms = tstart + i * 60_000
        if name == "shell":
            args = {"command": "echo fixture-fam"}
        elif name == DISPATCH_TOOL:
            args = {"path": "/fixture/dir/w.md"}
        else:
            args = {"path": "/fixture/dir/f.md"}
        _tool_call(conn, sid, seq, name, args, "salida\n", ms, cost=cost)
        sums[0] += 210 + 10 * seq
        sums[1] += 40
        sums[2] += 10
        sums[3] += 300 + 10 * seq
    total_ms = tstart + (len(steps_cost) + 1) * 60_000
    _orig_parent(conn, sid, ROLE_FIX, MODEL_FIX, tstart, total_ms,
                 tuple(sums), sum(c for _, c in steps_cost))
    _set_parent(conn, sid, parent_id)


def _build_app_family(path: Path) -> None:
    """Fixture padre/hijo (PD-9: sin doble conteo): `SESSION_CHILD` con
    parent_id = SESSION_PARENT; ambas sesiones del MISMO rol, costos 0.80 y
    0.30 → el agregado del rol debe ser 1.10 (una sola vez cada uno)."""
    conn = _new_store(path)
    t0 = BASE_MS + 52_000_000_000
    _add_session(conn, SESSION_PARENT, None, t0,
                 [("read", 0.5), ("shell", 0.2), (DISPATCH_TOOL, 0.1)])
    _add_session(conn, SESSION_CHILD, SESSION_PARENT, t0 + 600_000,
                 [("read", 0.2), ("shell", 0.1)])
    conn.commit()
    conn.close()


def _build_app_orphan(path: Path) -> None:
    """Fixture de enlace NO verificable (PD-9): una sola sesión cuyo
    parent_id apunta a una sesión que NO está en el store (no se inventa la
    sesión padre ni se completa el dato)."""
    conn = _new_store(path)
    t0 = BASE_MS + 63_000_000_000
    _add_session(conn, SESSION_APP, SESSION_MISSING_PARENT, t0,
                 [("read", 0.05), ("shell", 0.10)])
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- helpers

def _walk_strings(obj: object):
    """Cadenas a cualquier profundidad (números/bools/null aparte)."""
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _walk_strings(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_strings(item)
    elif isinstance(obj, str):
        yield obj


def _walk_dicts(obj: object):
    """Dicts a cualquier profundidad (para inspección de claves)."""
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _walk_dicts(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_dicts(item)


def _cost_leaf_numbers(value: object, out: list) -> None:
    """Números de costo de la hoja bajo una clave que CONTIENE `cost`: el
    número plano (forma previa) o el `value` de la entrada DECLARADA
    `{value, unit, bucket, sessions_reporting, sessions_total, cause}` (forma
    de R1). Un `value` null es un subtotal NO emitido: no se agrega."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        out.append(value)
    elif isinstance(value, dict):
        inner = value.get("value")
        if isinstance(inner, (int, float)) and not isinstance(inner, bool):
            out.append(inner)
        else:
            # estructura anidada intermedia: seguir buscando hojas de costo.
            _collect_cost_numbers(value, out)


def _collect_cost_numbers(node: object, out: list | None = None) -> list:
    """Números "de costo" del agregado por rol.

    Alineación de LECTURA (hallazgo R1, review-reopen-2026-10-12; la aserción
    NO cambia): el agregado por rol declara ahora la cobertura y cada
    componente sumado es `{value, unit, bucket, sessions_reporting,
    sessions_total, cause}` — el número observado vive en `value`. Solo se
    leen las claves que contienen `cost` (el `value` de una entrada declarada
    de OTRO componente no es un número de costo). La lectura acepta AMBAS
    formas (el número plano previo y la entrada declarada), de modo que el
    oráculo de doble conteo siga leyendo el costo declarado del rol sin
    depender de la forma fina."""
    if out is None:
        out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if "cost" in key.lower():
                _cost_leaf_numbers(value, out)
            else:
                _collect_cost_numbers(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_cost_numbers(item, out)
    return out


def _dump(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)


def _cause_text(d: dict) -> str:
    """Texto de causa/basis declarados (el contrato no fija el nombre de la
    clave de causa dentro de la anotación)."""
    for key in ("basis", "cause"):
        value = d.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


# ---------------------------------------------------------------- tests

class ApplicationPrivacyT3Test(unittest.TestCase):
    """T3 RED de 005-002: un test por postcondición (PD-9, PD-10, PD-12),
    contra la SALIDA del wrapper (JSON por stdout + rc). Fixtures 100%
    sintéticos en temporales; la base real JAMÁS se abre."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="cdad-005-002-t3-",
                                         dir="/tmp/opencode")
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name)
        self.base_dir = base
        self.store_app_single = base / "app-single" / "sessions.db"
        self.store_family = base / "app-family" / "sessions.db"
        self.store_orphan = base / "app-orphan" / "sessions.db"
        self.store_muestra1 = base / "muestra1" / "sessions.db"
        _build_app_single(self.store_app_single)
        _build_app_family(self.store_family)
        _build_app_orphan(self.store_orphan)
        _build_muestra1(self.store_muestra1)
        # archivo referenciado con marcador propio (PD-9: ref NO copia)
        self.receipt_path = base / "app-receipt-fixture.md"
        self.receipt_path.write_text(REF_MARKER + "\n", encoding="utf-8")

    # -- corrida del wrapper (SIEMPRE subproceso, nunca import) --

    def _run(self, *argv: str) -> subprocess.CompletedProcess:
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
                "ejecuta aún; el test NO importa el módulo del medidor")
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(f"PD-11 (acotado): el medidor no terminó dentro de "
                      f"{CLI_TIMEOUT_S}s; timeout={exc!r}")

    def _run_ok(self, *argv: str, label: str = "run") \
            -> subprocess.CompletedProcess:
        proc = self._run(*argv)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: rc=0 sobre el fixture (superficie PD-15/PD-9; "
                "las banderas declaradas DEBEN aceptarse) — "
                f"stdout={proc.stdout[:300]!r} stderr={proc.stderr[:300]!r}")
        return proc

    def _parse(self, proc: subprocess.CompletedProcess,
               label: str) -> dict:
        out = proc.stdout.decode("utf-8", errors="replace")
        try:
            doc = json.loads(out)
        except json.JSONDecodeError as exc:  # pragma: no cover
            self.fail(f"{label}: stdout no es JSON parseable ({exc}): "
                      f"{out[:400]!r}")
        run = doc.get("run", {})
        self.assertEqual(
            run.get("schema"), "recognized",
            msg=f"{label}: el fixture replica el esquema observado "
                "(discovery §1.2) y debe reconocerse; run=" + str(run))
        self.assertIsInstance(
            doc.get("sessions"), list, msg=f"{label}: sessions[] es lista")
        return doc

    def _run_ok_doc(self, *argv: str, n_sessions: int = 1,
                    label: str = "run") -> tuple[dict, bytes]:
        proc = self._run_ok(*argv, label=label)
        doc = self._parse(proc, label)
        self.assertEqual(
            len(doc["sessions"]), n_sessions,
            msg=f"{label}: el store tiene {n_sessions} sesiones y el "
                "modo acotado las mide (fixtures del test)")
        return doc, proc.stdout

    # -- PD-9 (a): anotación referenciada:transportada, no copia --

    def test_pd9_annotation_referenced_transport_no_copy(self):
        """PD-9: CON las banderas declaradas (--application-ref REF /
        --application-limit VALUE), el documento trae `application` con:
        `ref` == la referencia TAL COMO SE PASÓ (ruta durable; NO una copia
        del contenido del archivo referenciado: el marcador del archivo NO
        aparece en la salida), `limit` == el valor pasado (aquí `accepted`,
        miembro del conjunto fijado {accepted, blocked, pending, unknown})
        y `basis` no vacío con hechos observables del documento. La
        anotación es REFERENCIADA: no es una nueva clasificación semántica
        del lector ni una aprobación automática."""
        label = "PD-9(a) anotación referenciada"
        ref = str(self.receipt_path)
        proc = self._run_ok(
            "--store", str(self.store_app_single),
            APP_REF_FLAG, ref, APP_LIMIT_FLAG, "accepted", label=label)
        doc = self._parse(proc, label)
        stdout_text = proc.stdout.decode("utf-8", errors="replace")
        # (1) la anotación EXISTE con la forma fijada (ref/limit/basis):
        app = doc.get("application")
        self.assertIsNotNone(
            app,
            msg=f"{label}: la anotación `application` NO existe en el "
                "documento emitido — RED de contrato: con las banderas "
                f"declaradas ({APP_REF_FLAG}, {APP_LIMIT_FLAG}) el medidor "
                "debe transportarla (claves top del documento: "
                f"{sorted(doc.keys())})")
        self.assertIsInstance(app, dict, msg=f"{label}: application es objeto")
        for key in APP_ON_REQUIRED_KEYS:
            self.assertIn(
                key, app,
                msg=f"{label}: application trae {key!r} (forma fijada "
                    f"PD-9; app={app!r})")
        # (2) `ref`: la referencia durable TAL COMO SE PASÓ (transporte):
        self.assertEqual(
            app.get("ref"), ref,
            msg=f"{label}: application.ref es la referencia durable "
                f"tal como se pasó ({ref!r}; fue {app.get('ref')!r}) — "
                "el medidor la TRANSPORTA, no la fabrica ni la sustituye")
        # (3) NO es una copia del contenido del archivo referenciado:
        self.assertNotIn(
            REF_MARKER, stdout_text,
            msg=f"{label}: el marcador del archivo referenciado "
                f"({REF_MARKER!r}) NO aparece en la salida — ref es "
                "referencia (ruta/commit/recibo), NUNCA una copia del "
                "contenido (PD-9)")
        # (4) `limit` == el valor declarado; miembro del conjunto fijado:
        self.assertEqual(
            app.get("limit"), "accepted",
            msg=f"{label}: application.limit es el valor pasado "
                f"('accepted' ∈ {APP_LIMIT_VALUES}; fue "
                f"{app.get('limit')!r}) — el límite se DECLARA por "
                "entrada, no lo juzga el lector")
        # (5) `basis`: hechos observables, no vacío:
        basis = app.get("basis")
        self.assertIsInstance(
            basis, str, msg=f"{label}: basis es texto (fue {type(basis)})")
        self.assertTrue(
            basis.strip(),
            msg=f"{label}: basis NO vacío: los hechos observables que "
                f"sustentan el límite (fue {basis!r})")

    # -- PD-9 (b): anotación en el documento; el medidor no escribe nada --

    def test_pd9_annotation_lives_in_document_and_meter_writes_nothing(self):
        """PD-9: la anotación es un CAMPO del documento emitido (no una
        entrada de gate ni un estado del ciclo): vive dentro del JSON por
        stdout. El medidor NO escribe nada fuera de su stdout: el store
        queda intacto (tamaño/mtime y sin archivos nuevos junto a él) y el
        repo queda intacto (git status sin cambios). SIN las banderas, la
        anotación NO aparece, o bien queda `unknown` CON CAUSA (ambas formas
        aceptadas; el lector nunca la inventa ni aprueba nada)."""
        label = "PD-9(b) anotación en el documento; solo stdout"
        ref = str(self.receipt_path)
        argv = ("--store", str(self.store_app_single),
                APP_REF_FLAG, ref, APP_LIMIT_FLAG, "accepted")
        # (1) snapshot antes: store + directorio del store + repo.
        st_before = self.store_app_single.stat()
        dir_before = sorted(p.name for p in
                            self.store_app_single.parent.iterdir())
        git_before = self._git_porcelain()
        # (2) corrida CON banderas: la anotación vive EN el documento.
        proc = self._run_ok(*argv, label=label)
        doc = self._parse(proc, label)
        self.assertIn(
            "application", doc,
            msg=f"{label}: la anotación vive DENTRO del documento emitido "
                "(campo top-level `application`; no es un gate ni un "
                f"estado: doc={sorted(doc.keys())})")
        # (3) el medidor NO escribe nada fuera de su stdout: store intacto.
        st_after = self.store_app_single.stat()
        self.assertEqual(
            (st_after.st_size, st_after.st_mtime_ns),
            (st_before.st_size, st_before.st_mtime_ns),
            msg=f"{label}: el store queda INTACTO tras la lectura "
                "(tamaño/mtime sin cambios; INV-1: read-only)")
        dir_after = sorted(p.name for p in
                           self.store_app_single.parent.iterdir())
        self.assertEqual(
            dir_after, dir_before,
            msg=f"{label}: ningún archivo nuevo junto al store "
                f"(antes={dir_before!r}; después={dir_after!r})")
        self.assertEqual(
            self._git_porcelain(), git_before,
            msg=f"{label}: el REPO queda intacto (git status sin cambios "
                "por la corrida del medidor)")
        # (4) SIN las banderas: la anotación NO aparece, o queda `unknown`
        #     CON CAUSA (el lector nunca la inventa ni aprueba nada).
        proc_nof = self._run_ok("--store", str(self.store_app_single),
                                label=label + " sin banderas")
        doc_nof = self._parse(proc_nof, label + " sin banderas")
        app_nof = doc_nof.get("application")
        if app_nof is None:
            self.assertNotIn(
                "application", doc_nof,
                msg=f"{label}: sin banderas la anotación NO aparece "
                    "(corresponde: el lector no la inventa)")
        else:
            self.assertIsInstance(
                app_nof, dict,
                msg=f"{label}: sin banderas, una anotación presente debe "
                    f"ser objeto (fue {app_nof!r})")
            self.assertEqual(
                app_nof.get("limit"), "unknown",
                msg=f"{label}: sin banderas, la anotación queda limit="
                    "'unknown' con causa (fue "
                    f"{app_nof.get('limit')!r}) — nunca inventada ni "
                    "aprobada")
            self.assertTrue(
                _cause_text(app_nof),
                msg=f"{label}: sin banderas, `unknown` trae CAUSA "
                    f"(basis o cause no vacíos; app={app_nof!r})")

    # -- PD-9 (c): el lector nunca aprueba: rc invariante ante el límite --

    def test_pd9_reader_never_approves(self):
        """PD-9/INV-9: la anotación NO es un juez ni una aprobación: por
        CADA valor del conjunto fijado (accepted/blocked/pending/unknown),
        el documento transporta el límite declarado tal como se pasó, la
        forma de la anotación no abre claves de aprobación (ninguna clave
        tipo `approved` en TODO el documento) y el rc del proceso NO cambia
        según el limit (rc=0 en los cuatro; un gate cambiaría rc o
        escribiría estado)."""
        label = "PD-9(c) el lector nunca aprueba"
        ref = str(self.receipt_path)
        for limit in APP_LIMIT_VALUES:
            with self.subTest(limit=limit):
                proc = self._run_ok(
                    "--store", str(self.store_app_single),
                    APP_REF_FLAG, ref, APP_LIMIT_FLAG, limit, label=label)
                doc = self._parse(proc, f"{label}[{limit}]")
                app = doc.get("application")
                self.assertIsNotNone(
                    app,
                    msg=f"{label}[{limit}]: la anotación existe para el "
                        f"límite {limit!r} — RED si falta")
                self.assertEqual(
                    app.get("limit"), limit,
                    msg=f"{label}[{limit}]: el límite transportado es tal "
                        f"cual se pasó ({limit!r}; fue "
                        f"{app.get('limit')!r}) — el lector NO re-juzga")
                extra = set(app.keys()) - APP_ON_ALLOWED_KEYS
                self.assertEqual(
                    extra, set(),
                    msg=f"{label}[{limit}]: la anotación solo trae claves "
                        "de la forma fijada "
                        f"{sorted(APP_ON_ALLOWED_KEYS)} "
                        f"(sobrantes: {sorted(extra)})")
                # ninguna marca de aprobación en TODO el documento:
                approved_keys = sorted(
                    {key for d in _walk_dicts(doc) for key in d.keys()
                     if APP_FORBIDDEN_KEY_WORD in key.lower()})
                self.assertEqual(
                    approved_keys, [],
                    msg=f"{label}[{limit}]: el lector NUNCA aprueba "
                        "(INV-9/PD-9): ninguna clave de aprobación en el "
                        f"documento (encontradas: {approved_keys!r})")
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"{label}[{limit}]: el rc NO cambia según el "
                        "limit (la anotación no es un gate: rc=0 en los "
                        f"cuatro valores; limit={limit!r})")

    # -- PD-9 (d): padre/hijo sin doble conteo; declaraciones explícitas --

    def test_pd9_family_declares_sessions_relations_no_double_cost(self):
        """PD-9: al combinar coordinador (padre) y workers (hijo) el
        documento DECLARA qué sesiones están incluidas
        (`application.included_sessions`) y qué relaciones se observaron
        (`application.relations`, con el parent_ref de la hija), y el
        agregado por rol NO cuenta dos veces el mismo costo: el sumatorio
        del rol es la suma de los costos propios de las sesiones incluidas
        (0.80 + 0.30 = 1.10), una sola vez cada una (NUNCA 2.20)."""
        label = "PD-9(d) familia declarada sin doble conteo"
        doc, _ = self._run_ok_doc("--store", str(self.store_family),
                                  n_sessions=2, label=label)
        sessions = doc["sessions"]
        child = next((s for s in sessions if s.get("parent_ref")), None)
        self.assertIsNotNone(
            child,
            msg=f"{label}: la sesión hija con parent_id observable tiene "
                "su parent_ref hasheado en la salida (PD-10: referencia, "
                "no identificador crudo)")
        parent = next((s for s in sessions if s is not child), None)
        self.assertIsNotNone(parent, msg=f"{label}: el padre está incluido")
        child_ref = child.get("session_ref")
        parent_ref = child.get("parent_ref")
        parent_expected_ref = parent.get("session_ref")
        # (1) costos propios por sesión (una vez cada una):
        with self.subTest(punto="a-costos-propios-por-sesion"):
            for s, expected in ((parent, PARENT_COST), (child, CHILD_COST)):
                leaves = dict(_measure_leaves(s.get("measures", {})))
                leaf = leaves.get("cost")
                self.assertIsNotNone(
                    leaf,
                    msg=f"{label}: la sesión {s.get('session_ref')!r} "
                        "declara su medida `cost` con la forma "
                        "{value,unit,provenance,bucket}")
                self.assertAlmostEqual(
                    leaf.get("value"), expected, places=6,
                    msg=f"{label}: el costo PROPIO de la sesión incluida "
                        f"es {expected} (fue {leaf.get('value')!r})")
        # (2) el agregado por rol suma cada costo UNA sola vez (1.10, no
        #     2.20): el agregado es la suma de los costos propios de las
        #     sesiones incluidas.
        with self.subTest(punto="b-agregado-sin-doble-conteo"):
            role_entries = [r for r in doc.get("roles", [])
                            if isinstance(r, dict)]
            self.assertTrue(
                role_entries, msg=f"{label}: roles[] agrega por rol")
            entry = next((r for r in role_entries
                          if r.get("role") == ROLE_FIX), None)
            self.assertIsNotNone(
                entry, msg=f"{label}: el rol {ROLE_FIX!r} está agregado")
            totals = _collect_cost_numbers(entry.get("sums", {}))
            self.assertTrue(
                totals,
                msg=f"{label}: el agregado del rol declara su costo "
                    f"(sums={str(entry.get('sums'))!r})")
            matches = [v for v in totals
                       if abs(v - FAMILY_TOTAL_COST) < 1e-6]
            self.assertEqual(
                len(matches), 1,
                msg=f"{label}: el agregado del rol es la suma de los "
                    "costos PROPIOS de las sesiones incluidas, una sola "
                    f"vez cada una: {FAMILY_TOTAL_COST} "
                    f"(candidatos={totals!r}) — el doble conteo "
                    f"coordinador+workers daría {FAMILY_DOUBLE_COST}")
            self.assertEqual(
                [v for v in totals
                 if abs(v - FAMILY_DOUBLE_COST) < 1e-6], [],
                msg=f"{label}: NO se toma dos veces el mismo costo: no "
                    f"existe el total duplicado {FAMILY_DOUBLE_COST} en "
                    f"{totals!r}")
        # (3) el documento DECLARA qué sesiones están incluidas y qué
        #     relaciones observó (el parent_ref de la hija).
        with self.subTest(punto="c-included-sessions-y-relaciones"):
            app = doc.get("application")
            self.assertIsNotNone(
                app,
                msg=f"{label}: la anotación `application` existe en el "
                    "documento del tramo padre/hijo — RED de contrato "
                    f"(claves top: {sorted(doc.keys())})")
            included = app.get("included_sessions")
            if isinstance(included, int):
                self.assertEqual(
                    included, 2,
                    msg=f"{label}: included_sessions declara las 2 "
                        f"sesiones incluidas (fue {included!r})")
            elif isinstance(included, list):
                self.assertEqual(
                    len(included), 2,
                    msg=f"{label}: included_sessions lista las 2 sesiones "
                        f"incluidas (fue {len(included)})")
                missing = [r for r in (child_ref, parent_expected_ref)
                           if r not in included]
                self.assertEqual(
                    missing, [],
                    msg=f"{label}: included_sessions referencia las "
                        f"sesiones incluidas (faltan {missing!r}; "
                        f"included={included!r})")
            else:
                self.fail(
                    f"{label}: included_sessions declara las sesiones "
                    f"incluidas (int o lista; fue {included!r})")
            relations = app.get("relations")
            self.assertIsInstance(
                relations, list,
                msg=f"{label}: relations declara las relaciones observadas "
                    f"(fue {type(relations).__name__})")
            self.assertTrue(
                relations,
                msg=f"{label}: al menos la relación padre→hijo queda "
                    "declarada (relations vacía)")
            self.assertIn(
                parent_ref,
                _dump(relations),
                msg=f"{label}: la relación observada referencia el "
                    f"parent_ref de la hija ({parent_ref!r}); relations="
                    f"{relations!r}")

    # -- PD-9 (e): enlace no verificable → unknown con causa --

    def test_pd9_unverifiable_link_reports_unknown(self):
        """PD-9: un enlace NO verificable queda `unknown` con causa: con
        una sesión cuyo parent_id apunta a una sesión que NO está en el
        store, la relación se informa como desconocida — no se inventa la
        sesión padre (una sola sesión en la salida) ni se completa el dato
        (el identificador crudo del padre ausente NO aparece en la
        salida)."""
        label = "PD-9(e) enlace no verificable unknown"
        doc, stdout_raw = self._run_ok_doc("--store", str(self.store_orphan),
                                           n_sessions=1, label=label)
        stdout_text = stdout_raw.decode("utf-8", errors="replace")
        self.assertNotIn(
            SESSION_MISSING_PARENT, stdout_text,
            msg=f"{label}: el identificador crudo del padre AUSENTE no "
                "aparece (referencia hasheada u omisión; PD-10)")
        self.assertEqual(
            [s.get("role") for s in doc["sessions"]], [ROLE_FIX],
            msg=f"{label}: la sesión padre NO se inventa: la salida trae "
                "exactamente la sesión hija")
        unknowns = doc.get("unknowns", [])
        self.assertIsInstance(
            unknowns, list, msg=f"{label}: unknowns[] es lista")
        texts = [(_dump(entry) if not isinstance(entry, str) else entry)
                 .lower() for entry in unknowns]
        link_words = ("parent", "padre", "relacion", "relación")
        unknown_words = ("unknown", "desconoc", "no verific",
                         "not present", "not found", "missing", "ausent")
        hits = [t for t in texts
                if any(w in t for w in link_words)
                and any(w in t for w in unknown_words)]
        self.assertTrue(
            hits,
            msg=f"{label}: la relación con el padre NO verificable queda "
                "declarada como desconocida CON CAUSA en unknowns[] "
                f"(textos hoy: {texts!r}) — no se inventa ni se completa "
                "el dato")

    # -- PD-10: privacidad (omitir o hashear rutas e identificadores) --

    def test_pd10_output_omits_paths_ids_and_raw_texts(self):
        """PD-10: la salida omite o hashea rutas e identificadores: NO
        contiene la ruta del store del fixture, ninguna cadena que empiece
        con la barra raiz (ninguna ruta absoluta del host), el
        identificador crudo de sesión (la referencia hasheada EXISTE), ni
        el texto crudo del prompt ni de las salidas de herramienta del
        fixture (los marcadores inventados NO aparecen). La salida SI
        porta el modelo observado por sesión (parte del contrato) y las
        referencias (posición call_index/seq) a los eventos originales."""
        label = "PD-10 privacidad"
        proc = self._run_ok("--store", str(self.store_app_single),
                            label=label)
        stdout_text = proc.stdout.decode("utf-8", errors="replace")
        doc = self._parse(proc, label)
        session = doc["sessions"][0]
        # (a) identificadores/rutas crudos OMITIDOS O HASHEADOS:
        with self.subTest(punto="a-sin-identificadores-ni-rutas-crudos"):
            self.assertNotIn(
                SESSION_APP, stdout_text,
                msg=f"{label}: el identificador crudo de sesión del "
                    "fixture NO aparece (se usa una referencia hasheada)")
            store_path = str(self.store_app_single)
            self.assertNotIn(
                store_path, stdout_text,
                msg=f"{label}: la ruta del store del fixture NO aparece "
                    f"({store_path!r})")
            self.assertNotIn(
                str(self.base_dir), stdout_text,
                msg=f"{label}: ninguna ruta del host temporal aparece "
                    f"({str(self.base_dir)!r})")
            self.assertNotIn(
                REF_MARKER, stdout_text,
                msg=f"{label}: el contenido del archivo referenciado no "
                    "se embebe: esta corrida ni siquiera pasa la "
                    "bandera, así que el marcador NO pertenece a la "
                    "salida")
            # ninguna cadena que empiece con la barra raiz:
            slash_strings = sorted(
                {s for s in _walk_strings(doc) if s.startswith("/")})
            self.assertEqual(
                slash_strings, [],
                msg=f"{label}: ninguna cadena de la salida empieza con la "
                    "barra raiz (ninguna ruta absoluta del host; PD-10) "
                    f"— encontradas: {slash_strings[:5]!r}")
        # (b) los marcadores inventados del prompt y de las salidas:
        with self.subTest(punto="b-sin-textos-crudos"):
            for marker, origen in ((PROMPT_MARKER, "prompt"),
                                   (TOOL_OUT_A, "salida de herramienta"),
                                   (TOOL_OUT_B, "salida de herramienta")):
                self.assertNotIn(
                    marker, stdout_text,
                    msg=f"{label}: el texto crudo del {origen} del "
                        f"fixture NO aparece ({marker!r}; PD-10: el "
                        "adaptador nunca imprime prompts crudos ni "
                        "salidas de herramientas)")
        # (c) la REFERENCIA hasheada existe; el modelo es contrato:
        with self.subTest(punto="c-referencias-hasheadas-y-modelo"):
            self.assertTrue(
                session.get("session_ref"),
                msg=f"{label}: la referencia hasheada de sesión EXISTE "
                    f"(session_ref={session.get('session_ref')!r})")
            self.assertNotEqual(
                session.get("session_ref"), SESSION_APP,
                msg=f"{label}: la referencia NO es el identificador "
                    "crudo (hasheado)")
            model = session.get("model")
            self.assertTrue(
                model, msg=f"{label}: el modelo observado por sesión es "
                           "parte del contrato (parseado o unknown; fue "
                           f"{model!r})")
            model_text = str(model)
            self.assertTrue(
                model_text == "unknown" or MODEL_ID_FIX in model_text,
                msg=f"{label}: el modelo es `unknown` o el id del modelo "
                    f"observado del fixture ({MODEL_ID_FIX!r}; fue "
                    f"{model_text!r})")
            fd = session.get("milestones", {}).get("first_dispatch", {})
            if fd.get("status") == "observed":
                position = fd.get("position")
                self.assertIsInstance(
                    position, dict,
                    msg=f"{label}: la posición del hito observado trae "
                        "las referencias a los eventos originales")
                self.assertIn("call_index", position,
                              msg=f"{label}: la posición trae call_index")
                self.assertIn("seq", position,
                              msg=f"{label}: la posición trae seq")

    # -- PD-12: salida compacta con referencias, sin el transcript --

    def test_pd12_compact_output_with_references_no_transcript(self):
        """PD-12 (límite FIJADO por el orquestador: 16384 bytes): el
        documento emitido para el fixture de la muestra 1 (101 llamadas en
        el tramo, 121 en la sesión, como en T2) mide 16384 bytes o menos;
        porta referencias a la evidencia original (sesión referenciada de
        forma hasheada y posición con call_index/seq de los hitos) y NO
        embebe el transcript completo (los textos de las salidas de
        herramienta del fixture, incluida la de 51.243 caracteres, NO
        aparecen en la salida)."""
        label = "PD-12 salida compacta con referencias"
        proc = self._run_ok("--store", str(self.store_muestra1),
                            label=label)
        raw = proc.stdout  # bytes del documento emitido para UNA sesión
        self.assertLessEqual(
            len(raw), PD12_BYTE_LIMIT,
            msg=f"{label}: el documento para UNA sesión mide "
                f"{len(raw)} bytes y el límite normativo fijado por el "
                f"orquestador es {PD12_BYTE_LIMIT} (PD-12: salida "
                "compacta, acotada — 005-003 la consume sin inyectar "
                "toda la sesión)")
        doc = json.loads(raw.decode("utf-8"))
        raw_text = raw.decode("utf-8", "replace")
        session = doc["sessions"][0]
        # referencias a la evidencia original:
        self.assertTrue(
            session.get("session_ref")
            and session.get("session_ref") != M1_SESSION_ID,
            msg=f"{label}: la sesión se referencia de forma hasheada "
                f"(session_ref={session.get('session_ref')!r}; nunca el "
                f"id crudo {M1_SESSION_ID!r})")
        self.assertNotIn(
            M1_SESSION_ID, raw_text,
            msg=f"{label}: el identificador crudo de la sesión no "
                "aparece (referencia hasheada)")
        fd = session.get("milestones", {}).get("first_dispatch", {})
        self.assertEqual(
            fd.get("status"), "observed",
            msg=f"{label}: el hito de despacho se observa en la muestra 1 "
                "(subagent #1) — posición disponible como referencia")
        position = fd.get("position")
        self.assertIsInstance(
            position, dict,
            msg=f"{label}: la posición del hito es la referencia "
                "paso/seq a la evidencia original")
        self.assertIn(
            "call_index", position, msg=f"{label}: ref con call_index")
        self.assertIn("seq", position, msg=f"{label}: ref con seq")
        # NO embebe el transcript: los textos de las salidas no aparecen.
        for filler, origen in (("x" * 100, "salida de 51.243 car."),
                               ("z" * 100, "salida post-gap de 61.000"),
                               ("q" * 100, "salida corta"),
                               ("w" * 100, "salida write")):
            self.assertNotIn(
                filler, raw_text,
                msg=f"{label}: el transcript NO está embebido: la "
                    f"{origen} del fixture no aparece en la salida "
                    "(referencia primero, evidencia consultada aparte; "
                    "PD-12)")

    # -- utilidades --

    def _git_porcelain(self) -> list:
        """Estado del repo (solo observación): filtra artefactos de caché
        del entorno de tests."""
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
            capture_output=True, timeout=30, stdin=subprocess.DEVNULL)
        lines = proc.stdout.decode("utf-8", "replace").splitlines()
        return sorted(line for line in lines
                      if "__pycache__" not in line
                      and ".pytest_cache" not in line)


if __name__ == "__main__":
    unittest.main()
