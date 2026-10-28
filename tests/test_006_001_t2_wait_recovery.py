#!/usr/bin/env python3
"""006-001 T2 RED — Espera proporcional, clasificación tras la salida del
cliente, correlación, terminación ordenada e intento previo (PD-7, PD-8,
PD-9, PD-10, PD-11).

Contract: docs/specs/006-001-opencode-concurrency-reliability/spec.md
(§2.4, §2.5, §2.7, §3: PD-7..PD-11; INV-1, INV-3; D-3, D-4, D-6) + plan.md
T2 (skills/cdad-cycle/scripts/cdad_delegate_opencode.py). Plan provenance:
docs/specs/006-001-opencode-concurrency-reliability/plan.md (sha256
0d03d5fef32e79b6502748d75f43c494de1bad955da661d984c45d12b5397c8f). T1 ya
está en GREEN (tests/test_006_001_t1_selection.py verde): NO se modifica
ese fichero ni sus oráculos.

FAKE PROPIO de este focal (el plan §3 PROHÍBE tocar el fake compartido de
tests/test_005_009_t2_opencode_adapter.py en T2: «los files de T2 y T3 no
tocan test_005_009_t2_opencode_adapter.py»). Este fichero define su PROPIO
binario falso (`opencode-fake-t2`), reutilizando SOLO la infraestructura de
fixture YA PUBLICADA por import (sin editar esos ficheros): `AdapterCase`
(agentes derivados publicados + interfaz stageada) y `Pd600T1Case`
(`dispatch`, `patch_config`, `worker_records_with_marker`, `FakeInfoServer`)
de tests/test_006_001_t1_selection.py.

MECANISMO OBSERVABLE DE `store_reads` (PD-3/PD-10, §2.4): «un contador
instrumentado en el store de fixture O LA TRAZA DEL FOCAL» — se usa la
TRAZA: un `sitecustomize.py` propio, inyectado por `PYTHONPATH` SOLO en el
entorno de cada despacho (`install_read_trace` + `dispatch_traced`),
engancha `sys.addaudithook` sobre el evento `sqlite3.connect` y registra
{ts, pid, argv0, database} de CUALQUIER proceso que herede ese
`PYTHONPATH` (el intérprete que corre la interfaz/adaptador — en el mismo
proceso o en uno hijo, da igual: el entorno se hereda igual) — EXCLUYE
las conexiones del propio binario falso (`CDAD_T2_READ_TRACE_SELF`,
comparado contra `argv0`) para no contarse a sí mismo. Esto NO es leer
implementación: es observar, desde fuera del proceso, QUÉ conexiones
SQLite se abrieron y CUÁNDO — el mismo principio que medir con un reloj
cuánto tarda una caja negra. La traza es la ÚNICA fuente de verdad: el
`store_reads` que el propio adaptador declare en su registro I8 (PD-3) se
CONTRASTA contra ella (nunca se da por bueno el autorreporte solo).

Mapa test → postcondición:

  PD-7 (TestPd7FailureAndAbsence, tabla §2.4 tras la salida del cliente):
    test_pd7_failed_row_reports_durable_idle_error_blocked
      (fila idle 'failed' con mensaje `idle` de error durable → blocked
      con error.type/error.message acotados a 200 caracteres; también
      cubre PD-8: `session` presente en esta terminación post-Popen)
    test_pd7_no_row_rc0_is_unknown_after_settle
      (sin fila, rc=0 → unknown tras settle_seconds)
    test_pd7_row_not_idle_standalone_is_unknown_after_settle_bounded_reads
      (fila no idle en standalone → unknown tras settle_seconds, con el
      conteo store_reads contrastado contra la cota de §2.4 vía la traza)
    test_pd7_row_not_idle_server_is_timeout_at_cota_ignoring_settle
      (fila no idle en servidor → timeout al vencer LA COTA, el
      asentamiento NO decide — settle_seconds chico se demuestra
      irrelevante en modo servidor)

  PD-8 (TestPd8CorrelationAndOrderedTermination):
    test_pd8_timeout_with_live_client_standalone_kills_whole_process_group
      (hangs con un nieto cuyo pid queda registrado: tras la respuesta NO
      queda vivo ningún proceso del grupo propio — ni el cliente directo
      ni el nieto que el cliente lanzó)

  PD-9 (TestPd9PriorAttemptNoRetry, §2.7):
    test_pd9_prior_non_idle_blocks_without_invoking_binary
      (registro previo del mismo paquete con fila NO idle → blocked SIN
      invocar el binario; `session` sigue null, PD-8)
    test_pd9_prior_idle_dispatches_normally
      (control: fila previa IDLE no bloquea; como máximo una invocación
      `run`)

  PD-10 (TestPd10ProportionalWait, §2.4/§2.5):
    test_pd10_zero_store_reads_while_client_alive_and_bounded_after
      (cero lecturas mientras el cliente vive, vía traza; lecturas
      posteriores ≤ la cota de §2.4; store_reads del I8 == la traza)
    test_pd10_locked_store_retries_until_released_without_adapter_write
      (store bloqueado por un escritor del fixture en rollback journal,
      BEGIN EXCLUSIVE acotado → termina completed cuando se libera, SIN
      que el adaptador escriba el store — INV-1)

  PD-11 (TestPd11RespondsWithinBudget, §2.5/D-3):
    test_pd11_three_variants_respond_within_cota_and_total_budget
      (hangs, no-idle, transport-error — cota ≤ 2s cada una y techo de HOST
      del total 75 s (>= 10x ≈ 66 s de la conducta correcta, no «total
      ≤ 10 s»); el envelope nunca es el `did not answer
      within` de la interfaz)
    test_pd11_cota_at_reserve_blocks_before_dispatch
      (timeout_seconds == WAIT_RESERVE_SECONDS → blocked SIN despacho)
    test_pd11_completed_server_mode_with_preflight_stays_within_cota
      (REQUISITO ADICIONAL DEL ORQUESTADOR: el camino `completed` en modo
      servidor CON preflight también responde dentro de la cota — D-3
      resuelve la carrera de latencia extra que T1 introdujo; UNA sola
      corrida es evidencia débil contra un flake de ~1 de cada 3,
      declarado así en el reporte del rol, no oculto)

RED esperado (todo este comportamiento es NUEVO — T1-GREEN no toca espera,
clasificación tras salida, correlación post-Popen, terminación de grupo ni
intento previo): el adaptador vigente post-T1 sigue clasificando desde la
fila como hacía 005-010 (hoy YA distingue succeeded/failed/no-idle/sin fila
por rc, así que ALGUNAS aserciones de terminación de PD-7 pueden PASAR hoy
—declarado, no oculto—), pero: (a) el diagnóstico de `failed` HOY no lleva
el error.type/message del mensaje `idle` (PD-7 nuevo); (b) HOY no hay
backoff proporcional con las claves `wait.poll_initial_seconds` nuevas (el
vigente sondea con su propio intervalo fijo, no el `wait.*` de la config) —
el conteo store_reads y su cota de §2.4 fallan por comportamiento o por
ausencia del campo en la procedencia (que T1 solo exige con forma, no con
el conteo real, D-5/T2); (c) HOY se mata solo el hijo directo (discovery
`:287-299`): el nieto de `hangs` sigue vivo tras la respuesta (PD-8); (d)
HOY no existe la comprobación del intento previo (§2.7): PD-9 invoca el
binario pese al registro previo no idle; (e) PD-11 puede fallar por la
carrera D-3 (el margen interno vigente consume casi toda la cota, como ya
documenta `test_005_009_t2_opencode_adapter.py:241-255`) o por el defecto
de (c) en la variante `hangs`. Cada fallo esperado es AssertionError sobre
el comportamiento ausente, nunca import/sintaxis/fixture.

EXCLUIDO de este focal (alcance de T1 o T3): selección de modo, preflight
de versión/credencial, el FORMATO de la procedencia I8 (ya fijo por T1 —
aquí solo se usa, vía `worker_records_with_marker`, para LEER el
`store_reads` que el adaptador reporta y contrastarlo); concurrencia real
de PD-6 y la config de ejemplo de PD-12 (T3).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
import threading
import time
import unittest
from pathlib import Path

from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_dir, dispatch_records
from test_006_001_t1_selection import (
    FakeInfoServer, Pd600T1Case, pc8_preparatory_exhaustion)

# --------------------------------------------------------------- constantes

T2_FAKE_VERSION = "opencode-fake-t2 1.0.0"
T2_CLIENT_SEMVER = T2_FAKE_VERSION.rsplit(" ", 1)[-1]
DEFAULT_SESSION_T2 = "ses-fake-006-001-t2-0001"
PRIOR_SESSION_T2 = "ses-fake-006-001-t2-prior-0001"
T2_ROLE_AGENT = "cdad-test-writer"
T2_ROW_MODEL = "fixture-006-001-t2-model"
USER_TEXT_T2 = "Encargo canónico recibido por el binario opencode falso T2 (006-001)."
FINAL_TEXT_T2 = (
    "# Entrega del rol (binario opencode falso T2, 006-001)\n\n"
    "Texto final acordado por la fixture T2 de 006-001: espera "
    "proporcional, clasificación, correlación y terminación ordenada.\n")

# Mensaje de error durable LARGO (>200 caracteres) con un centinela de COLA
# después del carácter 200: prueba que el diagnóstico lo ACOTA a 200
# caracteres (spec PD-7), sin pretender fijar la prosa completa (plan §3:
# el sentido de los textos lo juzga la review).
IDLE_ERROR_TYPE = "unknown"
_IDLE_ERROR_HEAD = "Failed to execute statement (fixture 006-001 T2 PD-7)"
IDLE_ERROR_TAIL_SENTINEL = "COLA_MAS_ALLA_DE_200_CARACTERES_NUNCA_EN_DIAGNOSTICO"
IDLE_ERROR_MESSAGE = (
    _IDLE_ERROR_HEAD + " " + ("relleno " * 25) + IDLE_ERROR_TAIL_SENTINEL)
assert len(IDLE_ERROR_MESSAGE) > 220, "fixture: el mensaje debe superar 200 caracteres"

WAIT_RESERVE_SECONDS = 1.0  # spec §2.5 (constante FIJA del adaptador; no configurable)

# 008-005 PC-6 (T-A): separación del fixture agrandada para que el techo de
# la cota de duración (>= 10x la conducta correcta, ≈ 2,2-4,2 s) siga por
# DEBAJO del valor que produce el defecto (esperar a que el cliente salga
# solo). El cliente que cuelga ignora SIGTERM y duerme esto; el nieto
# duerme MÁS que el cliente (PD-8).
HANG_SLEEP_SECONDS = 60
GRANDCHILD_SLEEP_SECONDS = 90
SLOW_SECONDS = 1.0           # «slow-then-idle»: el cliente tarda esto antes de idle
LOCK_HOLD_SECONDS = 1.0      # ventana acotada del escritor que bloquea el store

# 008-005 PC-6 (T-A): cotas superiores de duración de este focal. Regla: el
# techo queda a >= 10x la conducta correcta (cota 2 s + gracia 0,2 s ≈
# 2,2 s; cota 4 s ≈ 4,2 s) y nunca igual al plazo que vigila.
# Pérdida declarada (PC-6, review F1): en los sitios cuya promesa es
# «responde/termina en la cota» (PD-7 y PD-11 ×2 aquí; B3a/B3b en
# test_006_001_reviewfix.py) el techo mide el HOST, no la cota: una espera
# acotada pero por ENCIMA de la cota (2x) hoy no es observable (el envelope
# del producto no expone duración) y queda registrada en deferred-hardening
# del spec 008-005 en vez de presentarse como guarda «en la cota».
# - PD-7 (sitios 10 y 11): techo 25 s >= 10x ≈ 22 s; el defecto "settle
#   usado" (0,1 s, más corto) lo separa la terminación, y el no
#   acotamiento queda por encima del techo.
# - PD-8 (sitio 12): cota 4 s; techo 50 s >= 10x ≈ 42-46 s y < el sleep
#   natural del cliente (HANG_SLEEP_SECONDS = 60 s).
# - PD-11 (sitios 13-17): techo 25 s >= 10x ≈ 22 s y < el defecto
#   (NO_IDLE_PD11_WAIT.settle_seconds = 30 s usado en vez de la cota /
#   sleep natural 60 s / no acotamiento); presupuesto total de las tres
#   variantes 75 s >= 10x ≈ 66 s y < 3 x defecto.
PD7_UPPER_SECONDS = 25.0
PD8_ACTIVE_TERMINATION_UPPER_SECONDS = 50.0
PD11_UPPER_SECONDS = 25.0
PD11_TOTAL_UPPER_SECONDS = 75.0

FAST_WAIT_T2 = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 0.3,
    "terminate_grace_seconds": 0.2,
    "preflight_timeout_seconds": 1,
}
SETTLE_WAIT_T2 = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 0.6,
    "terminate_grace_seconds": 0.3,
    "preflight_timeout_seconds": 1,
}
# PD-11 «no-idle»: settle_seconds por ENCIMA de la cota de 2s (30 s, la
# separación T-A de 008-005 PC-6), para que sea LA COTA (no el asentamiento)
# la que decida (D-3: la carrera real); si el adaptador usara el
# asentamiento, quedaría por encima del techo admisible (25 s).
NO_IDLE_PD11_WAIT = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 30,
    "terminate_grace_seconds": 0.2,
    "preflight_timeout_seconds": 1,
}
HANGS_WAIT = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 0.3,
    "terminate_grace_seconds": 0.2,
    "preflight_timeout_seconds": 1,
}


def _lit(text: str) -> str:
    return json.dumps(text)


def expected_read_bound(poll_initial: float, poll_max: float,
                         window_seconds: float) -> int:
    """Cota de lecturas de spec §2.4: R ≤ 2 + ceil(log2(pmax/pinit)) +
    ceil(W/pmax), para una ventana W posterior a la salida del cliente."""
    window_seconds = max(window_seconds, 0.0)
    return (2
            + math.ceil(math.log2(poll_max / poll_initial))
            + math.ceil(window_seconds / poll_max))


def _process_state(pid: int) -> str | None:
    """Estado `/proc/<pid>/stat` (3er campo tras el `)` de comm); None si
    el proceso ya no existe. 'Z' = zombie (ya no computa; se trata como
    MUERTO a efectos de PD-8 — un padre no reapeado no es «vivo»)."""
    try:
        text = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except (FileNotFoundError, ProcessLookupError, OSError):
        return None
    try:
        after_comm = text.rsplit(") ", 1)[1]
        return after_comm.split(" ", 1)[0]
    except IndexError:
        return None


# ------------------------------------------- traza de lecturas (sqlite3)

READ_TRACE_SITECUSTOMIZE = '''
import json
import os
import sys
import time

_LOG = os.environ.get("CDAD_T2_READ_TRACE")
_SELF = os.environ.get("CDAD_T2_READ_TRACE_SELF", "")


def _record(database):
    argv0 = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else ""
    if _SELF and argv0 == _SELF:
        return
    if not _LOG:
        return
    entry = {"ts": time.time(), "pid": os.getpid(), "argv0": argv0,
             "database": str(database)}
    try:
        with open(_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\\n")
    except OSError:
        pass


def _hook(event, args):
    if event == "sqlite3.connect":
        _record(args[0] if args else None)


if hasattr(sys, "addaudithook"):
    sys.addaudithook(_hook)
else:  # pragma: no cover (fallback de portabilidad, no esperado en CI)
    import sqlite3
    _orig_connect = sqlite3.connect

    def _patched_connect(*a, **kw):
        _record(a[0] if a else kw.get("database"))
        return _orig_connect(*a, **kw)

    sqlite3.connect = _patched_connect
'''


# ------------------------------------------------------- binario falso T2


T2_FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
# Binario OpenCode FALSO, PROPIO de tests/test_006_001_t2_wait_recovery.py
# (NO es el fake compartido de test_005_009_t2_opencode_adapter.py: el
# plan 006-001 S3 prohíbe tocarlo en T2). Protocolo:
#   1. --version: responde ANTES de tocar stdin/variant (mismo cuidado que
#      el oráculo 2 de T1: un --version del preflight no debe colgarse ni
#      contar como despacho).
#   2. localiza el paquete (argv-file / env PACKET|CDAD|DELIVER / stdin).
#   3. registra CADA invocación (incluido --version) en calls.jsonl — PD-9
#      exige poder comprobar «sin invocar NADA» desde este mismo log.
#   4. escribe client-start-ts.txt al comenzar el trabajo real y
#      client-exit-ts.txt justo antes de salir (en TODAS las ramas): la
#      ventana [start, exit] es «mientras el cliente vive» (PD-10).
#   5. variante leída de <fake>/variant, gobierna el store SQLite
#      (session_v2 + session_message, mismo esquema observado que el fake
#      compartido) y el rc.
import hashlib
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent        # <fake>/bin
_FAKE = _HERE.parent                           # <fake>
_MARKER = b"---cdad-packet-json"
_CALLS = _FAKE / "calls.jsonl"
_SENT = _FAKE / "sent-packet.md"
_GRANDCHILD_PID = _FAKE / "grandchild.pid"
_CLIENT_PID = _FAKE / "client.pid"
_START_TS = _FAKE / "client-start-ts.txt"
_EXIT_TS = _FAKE / "client-exit-ts.txt"


def _append(entry):
    with _CALLS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def _locate_packet():
    for token in sys.argv[1:]:
        candidate = Path(token)
        if candidate.is_file():
            data = candidate.read_bytes()
            if data.lstrip().startswith(_MARKER):
                return data, "argv-file"
    for key in sorted(os.environ):
        if any(part in key.upper() for part in ("PACKET", "CDAD", "DELIVER")):
            candidate = Path(os.environ[key])
            if candidate.is_file():
                data = candidate.read_bytes()
                if data.lstrip().startswith(_MARKER):
                    return data, "env:" + key
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.lstrip().startswith(_MARKER.decode("utf-8")):
                return data.encode("utf-8"), "stdin"
    except Exception:
        pass
    return None, "unfounded"


version_line = %VERSION_LINE%
if "--version" in sys.argv[1:]:
    _append({"argv": sys.argv[1:], "kind": "version"})
    sys.stdout.write(version_line + "\n")
    sys.stdout.flush()
    sys.exit(0)

_START_TS.write_text(repr(time.time()), encoding="utf-8")
_CLIENT_PID.write_text(str(os.getpid()), encoding="utf-8")

variant = (_FAKE / "variant").read_text(encoding="utf-8").strip() or "succeeded"
argv = sys.argv[1:]


def _argv_value(name):
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
    return None


session_id = _argv_value("--session") or %DEFAULT_SESSION%
agent_id = _argv_value("--agent") or "cdad-test-writer"
pwd_value = os.environ.get("PWD") or os.getcwd()


def _sessions_db_path():
    try:
        config = json.loads((_FAKE / "exec-config.json").read_text(encoding="utf-8"))
        value = config.get("sessions_db")
    except (OSError, ValueError):
        value = None
    return Path(value) if value else (_FAKE / "sessions.db")


store_path = _sessions_db_path()

packet, transport = _locate_packet()
if packet is not None:
    _SENT.write_bytes(packet)

entry = {
    "argv": argv,
    "kind": "dispatch",
    "variant": variant,
    "cwd": os.getcwd(),
    "pwd": pwd_value,
    "session_id_written": session_id,
    "agent_written": agent_id,
    "packet": None,
}
if packet is not None:
    entry["packet"] = {
        "transport": transport,
        "sha256": hashlib.sha256(packet).hexdigest(),
        "bytes": len(packet),
    }
    if transport == "stdin":
        entry["packet"]["stdin"] = packet.decode("utf-8")


def _write_store(idle_outcome, *, with_final_text, idle_message=None):
    store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = store_path.parent / (store_path.name + ".tmp")
    try:
        tmp_path.unlink()
    except OSError:
        pass
    conn = sqlite3.connect(str(tmp_path))
    try:
        conn.execute(
            "CREATE TABLE session_v2 (id TEXT PRIMARY KEY, agent TEXT,"
            " model TEXT, directory TEXT, time_created REAL,"
            " time_updated REAL, time_idle REAL, idle_outcome TEXT)")
        conn.execute(
            "CREATE TABLE session_message (id TEXT PRIMARY KEY,"
            " session_id TEXT, type TEXT, seq INTEGER, data TEXT)")
        now = time.time()
        idle = now if idle_outcome is not None else None
        conn.execute(
            "INSERT INTO session_v2 (id, agent, model, directory,"
            " time_created, time_updated, time_idle, idle_outcome)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (session_id, agent_id, %ROW_MODEL%, pwd_value, now - 1.0, now,
             idle, idle_outcome))
        seq = 1
        conn.execute(
            "INSERT INTO session_message (id, session_id, type, seq, data)"
            " VALUES (?, ?, ?, ?, ?)",
            (f"msg-{seq:04d}-{session_id}", session_id, "user", seq,
             json.dumps({"content": [{"type": "text", "text": %USER_TEXT%}]})))
        if with_final_text:
            seq += 1
            conn.execute(
                "INSERT INTO session_message (id, session_id, type, seq, data)"
                " VALUES (?, ?, ?, ?, ?)",
                (f"msg-{seq:04d}-{session_id}", session_id, "assistant", seq,
                 json.dumps({"content": [{"type": "text", "text": %FINAL_TEXT%}]})))
        if idle_message is not None:
            seq += 1
            conn.execute(
                "INSERT INTO session_message (id, session_id, type, seq, data)"
                " VALUES (?, ?, ?, ?, ?)",
                (f"msg-{seq:04d}-{session_id}", session_id, "idle", seq,
                 json.dumps(idle_message)))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp_path, store_path)


def _write_empty_store():
    """Store SQLite VÁLIDO (esquema creado) pero SIN ninguna fila — el
    store EXISTE (a diferencia de un path ausente, que el adaptador trata
    como fallo de configuración, no como hecho material de §2.4)."""
    store_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = store_path.parent / (store_path.name + ".tmp")
    try:
        tmp_path.unlink()
    except OSError:
        pass
    conn = sqlite3.connect(str(tmp_path))
    try:
        conn.execute(
            "CREATE TABLE session_v2 (id TEXT PRIMARY KEY, agent TEXT,"
            " model TEXT, directory TEXT, time_created REAL,"
            " time_updated REAL, time_idle REAL, idle_outcome TEXT)")
        conn.execute(
            "CREATE TABLE session_message (id TEXT PRIMARY KEY,"
            " session_id TEXT, type TEXT, seq INTEGER, data TEXT)")
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp_path, store_path)


if variant == "succeeded":
    _write_store("succeeded", with_final_text=True)
    _append(entry)
elif variant == "failed-with-idle-error":
    _write_store(
        "failed", with_final_text=False,
        idle_message={"outcome": "failed",
                      "error": {"type": %ERROR_TYPE%, "message": %ERROR_MESSAGE%}})
    _append(entry)
elif variant == "rc0-no-row":
    _write_empty_store()
    _append(entry)
elif variant == "exit-row-not-idle":
    _write_store(None, with_final_text=False)
    _append(entry)
elif variant == "transport-error":
    _write_empty_store()
    _append(entry)
    sys.stderr.write("opencode-fake-t2: transport error simulado (fixture)\n")
    _EXIT_TS.write_text(repr(time.time()), encoding="utf-8")
    sys.exit(2)
elif variant == "slow-then-idle":
    _append(entry)
    time.sleep(%SLOW_SECONDS%)
    _write_store("succeeded", with_final_text=True)
elif variant == "succeeded-after-lock-signal":
    # PD-10 (store bloqueado): escribe la fila normal con la SESIÓN REAL
    # elegida por el adaptador (session_id, de --session), avisa al test
    # vía un centinela (row-written.flag) y se queda un rato ACOTADO antes
    # de salir — tiempo para que el escritor del fixture (hilo del test)
    # tome BEGIN EXCLUSIVE ANTES de que el cliente salga (y por lo tanto
    # antes de que el adaptador intente su primera lectura).
    _write_store("succeeded", with_final_text=True)
    (_FAKE / "row-written.flag").write_text("1", encoding="utf-8")
    time.sleep(0.3)
    _append(entry)
elif variant == "hangs":
    grandchild = subprocess.Popen(
        [sys.executable, "-c",
         "import signal,time\n"
         "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
         f"time.sleep({%GRANDCHILD_SLEEP%})\n"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    _GRANDCHILD_PID.write_text(str(grandchild.pid), encoding="utf-8")
    _append(entry)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    sys.stdout.flush()
    time.sleep(%HANG_SLEEP%)
    _EXIT_TS.write_text(repr(time.time()), encoding="utf-8")
    sys.exit(0)
else:
    _append(entry)

_EXIT_TS.write_text(repr(time.time()), encoding="utf-8")
'''


# --------------------------------------------------------------- fixture


class Pd600T2Case(Pd600T1Case):
    """Fixture propia de T2: binario falso propio + traza de lecturas
    (sqlite3.connect vía sitecustomize) + helpers de fabricación directa
    de filas/registros I8 (PD-9) y verificación de liveness de procesos
    (PD-8). Reutiliza SOLO infraestructura ya publicada de T1/T2 005-009
    por import, sin editar esos ficheros."""

    def own_fake_runtime(self, name: str, *, variant: str = "succeeded") -> dict:
        fake = self.fake_runtime(name, variant="succeeded")  # reusa dir/config
        binary = fake["binary"]
        binary.write_text(
            T2_FAKE_BINARY_SOURCE
            .replace("%VERSION_LINE%", _lit(T2_FAKE_VERSION))
            .replace("%DEFAULT_SESSION%", _lit(DEFAULT_SESSION_T2))
            .replace("%USER_TEXT%", _lit(USER_TEXT_T2))
            .replace("%FINAL_TEXT%", _lit(FINAL_TEXT_T2))
            .replace("%ROW_MODEL%", _lit(T2_ROW_MODEL))
            .replace("%ERROR_TYPE%", _lit(IDLE_ERROR_TYPE))
            .replace("%ERROR_MESSAGE%", _lit(IDLE_ERROR_MESSAGE))
            .replace("%SLOW_SECONDS%", repr(SLOW_SECONDS))
            .replace("%HANG_SLEEP%", repr(HANG_SLEEP_SECONDS))
            .replace("%GRANDCHILD_SLEEP%", repr(GRANDCHILD_SLEEP_SECONDS)),
            encoding="utf-8")
        binary.chmod(0o755)
        (fake["dir"] / "variant").write_text(variant + "\n", encoding="utf-8")
        fake["grandchild_pid"] = fake["dir"] / "grandchild.pid"
        fake["client_pid"] = fake["dir"] / "client.pid"
        fake["client_start_ts"] = fake["dir"] / "client-start-ts.txt"
        fake["client_exit_ts"] = fake["dir"] / "client-exit-ts.txt"
        return fake

    # -- traza de lecturas (sqlite3.connect) --------------------------------

    def install_read_trace(self, fake: dict) -> dict:
        trace_dir = fake["dir"] / "pytrace"
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / "sitecustomize.py").write_text(
            READ_TRACE_SITECUSTOMIZE, encoding="utf-8")
        return {
            "pythonpath": str(trace_dir),
            "log_path": fake["dir"] / "store-reads-trace.jsonl",
            "self_name": fake["binary"].name,
        }

    def dispatch_traced(self, fake: dict, trace: dict, **kwargs):
        overrides = dict(kwargs.pop("env_overrides", None) or {})
        existing_pp = os.environ.get("PYTHONPATH")
        overrides["PYTHONPATH"] = (
            trace["pythonpath"] + (os.pathsep + existing_pp if existing_pp else ""))
        overrides["CDAD_T2_READ_TRACE"] = str(trace["log_path"])
        overrides["CDAD_T2_READ_TRACE_SELF"] = trace["self_name"]
        return self.dispatch(fake, env_overrides=overrides, **kwargs)

    def read_trace_entries(self, trace: dict) -> list[dict]:
        path = trace["log_path"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    # -- fabricación directa de filas / registros previos (PD-9, PD-10) ----

    def write_raw_session_row(self, store_path: Path, *, session_id: str,
                              agent_id: str = T2_ROLE_AGENT,
                              idle_outcome: str | None, pwd: str,
                              with_final_text: bool) -> None:
        store_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = store_path.parent / (store_path.name + ".rawtmp")
        if tmp.exists():
            tmp.unlink()
        conn = sqlite3.connect(str(tmp))
        try:
            conn.execute(
                "CREATE TABLE session_v2 (id TEXT PRIMARY KEY, agent TEXT,"
                " model TEXT, directory TEXT, time_created REAL,"
                " time_updated REAL, time_idle REAL, idle_outcome TEXT)")
            conn.execute(
                "CREATE TABLE session_message (id TEXT PRIMARY KEY,"
                " session_id TEXT, type TEXT, seq INTEGER, data TEXT)")
            now = time.time()
            idle = now if idle_outcome is not None else None
            conn.execute(
                "INSERT INTO session_v2 (id, agent, model, directory,"
                " time_created, time_updated, time_idle, idle_outcome)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, agent_id, T2_ROW_MODEL, pwd, now - 1.0, now,
                 idle, idle_outcome))
            if with_final_text:
                conn.execute(
                    "INSERT INTO session_message (id, session_id, type,"
                    " seq, data) VALUES (?, ?, ?, ?, ?)",
                    (f"msg-0001-{session_id}", session_id, "user", 1,
                     json.dumps({"content": [{"type": "text",
                                              "text": USER_TEXT_T2}]})))
                conn.execute(
                    "INSERT INTO session_message (id, session_id, type,"
                    " seq, data) VALUES (?, ?, ?, ?, ?)",
                    (f"msg-0002-{session_id}", session_id, "assistant", 2,
                     json.dumps({"content": [{"type": "text",
                                              "text": FINAL_TEXT_T2}]})))
            conn.commit()
        finally:
            conn.close()
        os.replace(tmp, store_path)

    def fabricate_prior_dispatch_record(self, *, session_id: str) -> Path:
        base = dispatch_dir(self.root, self.execution_id)
        base.mkdir(parents=True, exist_ok=True)
        record = {
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "role": "test-writer",
            "substage": "red",
            "runtime": "opencode",
            "model_configured": "unknown",
            "model_reported": "unknown",
            "session": session_id,
            "started_at": "2026-10-16T00:00:00Z",
            "provenance": {
                "runtime": ("execution config (--exec-config): runtime; "
                            "mode_requested=standalone; "
                            "mode_effective=standalone; "
                            "client_version=unknown; "
                            "server_version=same-binary(standalone)"),
                "session": (f"{session_id} | chosen by adapter; "
                            "store=configured sessions_db; row=present; "
                            "store_reads=unknown; prior_check_reads=unknown; "
                            "prior attempt fabricated by fixture (PD-9 "
                            "006-001 T2)"),
            },
        }
        self.assertEqual(
            set(record), I8_RECORD_KEYS,
            msg="fixture: el registro previo fabricado no respeta la "
                "forma cerrada I8 (precondición de PD-9 rota)")
        path = base / "fake-prior-006-001-t2-0001.json"
        path.write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    # -- liveness de procesos (PD-8) -----------------------------------------

    def assert_pid_not_alive(self, pid: int, label: str) -> None:
        deadline = time.monotonic() + 2.0
        state = _process_state(pid)
        while state not in (None, "Z") and time.monotonic() < deadline:
            time.sleep(0.05)
            state = _process_state(pid)
        self.assertIn(
            state, (None, "Z"),
            msg=f"{label}: el pid {pid} sigue vivo tras la respuesta del "
                f"adaptador (/proc estado {state!r}; PD-8: terminación "
                f"ordenada del grupo propio)")

    def kill_pid_if_alive(self, pid: int) -> None:
        try:
            os.kill(pid, 9)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def assert_t2_final_text_in_delivery(self) -> None:
        base = self.results_base()
        hits = [
            path for path in sorted(base.rglob("*"))
            if path.is_file()
            and FINAL_TEXT_T2.encode("utf-8") in path.read_bytes()
        ]
        self.assertTrue(
            hits,
            msg="ningún archivo de la entrega durable contiene el texto "
                "final acordado del fixture T2 (PD-7)")


# ----------------------------------------------------------------- PD-7


class TestPd7FailureAndAbsence(Pd600T2Case):
    """PD-7: tras la salida del cliente, la tabla §2.4 clasifica desde el
    hecho material (NUNCA el rc del cliente); también ejercita PD-8
    (`session` presente en toda terminación posterior al arranque de
    `run`)."""

    def test_pd7_failed_row_reports_durable_idle_error_blocked(self) -> None:
        """PD-7 (fila idle `failed`): `blocked` con `error.type`/
        `error.message` del ÚLTIMO `session_message` tipo `idle`
        (discovery `:64`), ACOTADOS a 200 caracteres (el centinela de
        cola del fixture, más allá del carácter 200, NUNCA debe aparecer
        en el diagnóstico). También PD-8: `session` viaja en el envelope
        (Popen fue exitoso). RED hoy: el diagnóstico vigente para `failed`
        no lee el mensaje `idle` del store (no hay error.type/message en
        el diagnóstico) — este mensaje `idle` es NUEVO (T2); el vigente
        solo conoce `idle_outcome` en `session_v2`."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd7-failed", variant="failed-with-idle-error")
        self.patch_config(
            fake, {"mode": "standalone", "wait": {**FAST_WAIT_T2,
                                                   "timeout_seconds": 5}})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-7 failed con error durable")

        self.assertEqual(
            out["termination"], "blocked",
            msg=f"fila idle 'failed': la terminación no es 'blocked' "
                f"(PD-7): {out['termination']!r}")
        # PD-8: la sesión del envelope debe ser la REALMENTE elegida por
        # el adaptador (la que de hecho viajó en --session, y con la que
        # el binario falso escribió la fila) — no un valor fijo del
        # fixture: el adaptador elige la sesión, el fixture solo la honra.
        chosen_session = self.packet_call(
            fake, "PD-7 failed con error durable").get("session_id_written")
        self.assertEqual(
            out.get("session"), chosen_session,
            msg=f"PD-8: 'blocked' posterior al arranque de run debe "
                f"llevar la sesión elegida ({chosen_session!r}): "
                f"{out.get('session')!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            IDLE_ERROR_TYPE, diagnosis,
            msg=f"el diagnóstico no nombra error.type del mensaje idle "
                f"(PD-7): {diagnosis!r}")
        self.assertIn(
            _IDLE_ERROR_HEAD, diagnosis,
            msg=f"el diagnóstico no lleva el INICIO de error.message "
                f"(PD-7): {diagnosis!r}")
        self.assertNotIn(
            IDLE_ERROR_TAIL_SENTINEL, diagnosis,
            msg=f"el diagnóstico lleva el centinela de COLA del mensaje "
                f"(más allá de 200 caracteres): no está acotado a 200 "
                f"caracteres (PD-7): {diagnosis!r}")
        self.assert_no_receipt_fabricated("PD-7 failed")

    def test_pd7_no_row_rc0_is_unknown_after_settle(self) -> None:
        """PD-7 (sin fila, rc=0): `unknown` al cumplirse `settle_seconds`
        (el cliente pudo imprimir lo que quiera por stdout; sin fila no
        hay hecho material hasta que el asentamiento se cumple)."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime("pd7-rc0-no-row", variant="rc0-no-row")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**SETTLE_WAIT_T2, "timeout_seconds": 5}})

        started = time.monotonic()
        proc = self.dispatch(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "PD-7 sin fila rc=0")

        self.assertEqual(
            out["termination"], "unknown",
            msg=f"sin fila, rc=0: la terminación no es 'unknown' tras "
                f"settle_seconds (PD-7): {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")
        self.assertGreaterEqual(
            elapsed, SETTLE_WAIT_T2["settle_seconds"],
            msg=f"terminó antes de cumplirse settle_seconds ({elapsed:.2f}s "
                f"< {SETTLE_WAIT_T2['settle_seconds']}s): el asentamiento "
                f"no se respetó (PD-7)")
        self.assert_no_receipt_fabricated("PD-7 sin fila rc=0")

    def test_pd7_row_not_idle_standalone_is_unknown_after_settle_bounded_reads(
            self) -> None:
        """PD-7 (fila no idle en standalone) + cota de lecturas de §2.4
        (asignada a T2): `unknown` tras `settle_seconds`; el número de
        lecturas posteriores a la salida del cliente (vía la TRAZA,
        mecanismo observable del fixture) no excede
        `2 + ceil(log2(pmax/pinit)) + ceil(W/pmax)`; el `store_reads` que
        el adaptador declara en su registro I8 (PD-3, T1) COINCIDE con la
        traza (no se da por bueno el autorreporte)."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd7-row-not-idle-standalone", variant="exit-row-not-idle")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**SETTLE_WAIT_T2, "timeout_seconds": 5}})
        trace = self.install_read_trace(fake)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_traced(fake, trace)
        out = self.envelope(proc, "PD-7 fila no idle standalone")

        self.assertEqual(
            out["termination"], "unknown",
            msg=f"fila no idle en standalone: la terminación no es "
                f"'unknown' tras settle_seconds (PD-7): "
                f"{out['termination']!r}")

        exit_ts = float(fake["client_exit_ts"].read_text(encoding="utf-8"))
        entries = self.read_trace_entries(trace)
        post_exit = [e for e in entries if e["ts"] > exit_ts]
        self.assertTrue(
            post_exit,
            msg="fixture: la traza no registró NINGUNA lectura posterior "
                "a la salida del cliente (¿PYTHONPATH no se propagó al "
                "proceso de la interfaz/adaptador? — fallo de fixture, "
                "no de comportamiento: detener y reportar, no debilitar "
                "la aserción)")
        window = max(e["ts"] for e in post_exit) - exit_ts
        bound = expected_read_bound(
            SETTLE_WAIT_T2["poll_initial_seconds"],
            SETTLE_WAIT_T2["poll_max_seconds"], window)
        self.assertLessEqual(
            len(post_exit), bound,
            msg=f"lecturas posteriores a la salida ({len(post_exit)}) "
                f"exceden la cota de §2.4 (R ≤ {bound} para W={window:.2f}s)")
        for e in post_exit:
            self.assertIn(
                "mode=ro", e["database"],
                msg=f"una lectura del adaptador NO usa mode=ro (INV-1): "
                    f"{e['database']!r}")
            self.assertNotIn(
                "immutable", e["database"].lower(),
                msg=f"una lectura del adaptador usa immutable (INV-1: "
                    f"solo mode=ro, nunca immutable): {e['database']!r}")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="no hay registro de worker con la procedencia nueva de "
                "§2.6 para esta terminación (PD-3, T1)")
        session_prov = str(worker_records[0]["provenance"].get("session", ""))
        reported = session_prov.split("store_reads=", 1)[1].split(";", 1)[0].strip()
        self.assertEqual(
            reported, str(len(post_exit)),
            msg=f"el store_reads declarado por el adaptador ({reported!r}) "
                f"no coincide con la traza del focal "
                f"({len(post_exit)}) (PD-3: el conteo se contrasta contra "
                f"la traza, no se da por bueno el autorreporte)")

    def test_pd7_row_not_idle_server_is_timeout_at_cota_ignoring_settle(
            self) -> None:
        """PD-7 (fila no idle en SERVIDOR): la espera sigue siendo durable
        hasta LA COTA (`timeout`), nunca `unknown` por asentamiento — el
        `settle_seconds` CHICO se demuestra irrelevante en modo servidor
        (tabla §2.4, última columna). Preflight exitoso (T1, GREEN) para
        llegar al camino de espera."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": T2_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd7-row-not-idle-server", variant="exit-row-not-idle")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": {"poll_initial_seconds": 0.05,
                            "poll_max_seconds": 0.2,
                            "settle_seconds": 0.1,  # CHICO: debe ser IGNORADO
                            "terminate_grace_seconds": 0.2,
                            "preflight_timeout_seconds": 1,
                            "timeout_seconds": 2}})

        started = time.monotonic()
        proc = self.dispatch(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "PD-7 fila no idle servidor")

        # PC-8: la cota (2s) es el sujeto y se conserva; si la preparación
        # la agotó, la clasificación válida es el no despacho — acotado.
        if pc8_preparatory_exhaustion(self, out, fake, "PD-7"):
            self.assertLess(elapsed, PD7_UPPER_SECONDS,
                            msg=f"PD-7 (008-005 T-A, sitio 10, PC-6): el "
                                f"no despacho quedó desacotado "
                                f"({elapsed:.2f}s >= {PD7_UPPER_SECONDS}s)")
            return

        self.assertEqual(
            out["termination"], "timeout",
            msg=f"fila no idle en SERVIDOR: la terminación no es "
                f"'timeout' (PD-7, la espera debe seguir hasta la cota, "
                f"no asentarse): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assertGreater(
            elapsed, 0.1 * 3,
            msg=f"terminó demasiado rápido ({elapsed:.2f}s): parece haber "
                f"usado settle_seconds=0.1s en vez de esperar la cota "
                f"(PD-7: en servidor, settle_seconds se ignora)")
        # 008-005 PC-6 (T-A, sitio 11, review F1): este techo mide el HOST
        # (25 s >= 10x ≈ 2,2 s de la conducta correcta), NO la cota de 2 s.
        # La discriminación «acotada por encima de la cota» (2x) no es
        # observable hoy (el envelope no expone duración) y queda como
        # pérdida declarada en deferred-hardening: no se presenta como
        # guarda «en la cota».
        self.assertLess(
            elapsed, PD7_UPPER_SECONDS,
            msg=f"PD-7 (008-005 T-A, sitio 11, PC-6): el host excedió el "
                f"techo de liveness ({elapsed:.2f}s >= "
                f"{PD7_UPPER_SECONDS}s; el techo mide el host, >= 10x la "
                f"conducta correcta ≈ 2,2 s, no la cota de 2 s); la "
                f"discriminación «acotada por encima de la cota» no es "
                f"observable hoy: pérdida declarada en deferred-hardening")
        self.assert_no_receipt_fabricated("PD-7 fila no idle servidor")


# ----------------------------------------------------------------- PD-8


class TestPd8CorrelationAndOrderedTermination(Pd600T2Case):
    """PD-8: correlación de sesión en toda terminación posterior al
    arranque de `run`, y terminación ORDENADA del grupo propio en
    `timeout` con el cliente vivo (SIGTERM, gracia, SIGKILL del GRUPO,
    no solo del hijo directo)."""

    def test_pd8_timeout_with_live_client_standalone_kills_whole_process_group(
            self) -> None:
        """PD-8 (`hangs` con un nieto cuyo pid queda registrado): tras la
        respuesta del adaptador, NINGÚN proceso del grupo propio sigue
        vivo — ni el cliente directo ni el nieto que el cliente lanzó
        (discovery: HOY solo se mata el hijo directo, `:287-299`). El
        cliente ignora SIGTERM (fuerza el camino SIGKILL, peor caso de
        D-3/PD-11) y el nieto duerme MÁS que el cliente (si nada lo
        matara explícitamente, seguiría vivo tras la respuesta aunque el
        cliente ya hubiera salido por su cuenta)."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime("pd8-hangs", variant="hangs")
        # Cota instrumental (PC-8): el sujeto es la terminación ordenada del
        # grupo; 4s deja presupuesto útil y sigue muy por debajo del sleep
        # natural del cliente (HANG_SLEEP_SECONDS) y del techo de 50 s de
        # 008-005 (evidencia de corte ACTIVO, aserción final intacta).
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**HANGS_WAIT, "timeout_seconds": 4}})

        started = time.monotonic()
        proc = self.dispatch(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "PD-8 hangs")

        self.assertEqual(
            out["termination"], "timeout",
            msg=f"cliente que cuelga: la terminación no es 'timeout': "
                f"{out['termination']!r}")
        chosen_session = self.packet_call(fake, "PD-8 hangs").get(
            "session_id_written")
        self.assertEqual(
            out.get("session"), chosen_session,
            msg=f"PD-8: 'timeout' posterior al arranque de run debe "
                f"llevar la sesión elegida ({chosen_session!r}; discovery: "
                f"HOY 'el timeout pierde el id de sesión'): "
                f"{out.get('session')!r}")

        self.assertTrue(
            fake["grandchild_pid"].is_file(),
            msg="fixture: el cliente no registró el pid del nieto "
                "(precondición de PD-8 rota)")
        grandchild_pid = int(
            fake["grandchild_pid"].read_text(encoding="utf-8").strip())
        self.addCleanup(self.kill_pid_if_alive, grandchild_pid)
        if fake["client_pid"].is_file():
            client_pid = int(
                fake["client_pid"].read_text(encoding="utf-8").strip())
            self.addCleanup(self.kill_pid_if_alive, client_pid)
            self.assert_pid_not_alive(
                client_pid, "PD-8 cliente directo")
        self.assert_pid_not_alive(grandchild_pid, "PD-8 nieto")

        self.assertLess(
            elapsed, PD8_ACTIVE_TERMINATION_UPPER_SECONDS,
            msg=f"PD-8 (008-005 T-A, sitio 12, PC-6): la respuesta tardó "
                f"{elapsed:.2f}s >= "
                f"{PD8_ACTIVE_TERMINATION_UPPER_SECONDS}s: no hay evidencia "
                f"de terminación ACTIVA por cota, solo de esperar a que el "
                f"proceso saliera solo ({HANG_SLEEP_SECONDS}s) "
                f"(PD-8/PD-11)")
        self.assert_no_receipt_fabricated("PD-8 hangs")


# ----------------------------------------------------------------- PD-9


class TestPd9PriorAttemptNoRetry(Pd600T2Case):
    """PD-9 (§2.7): un registro previo del MISMO paquete cuya fila existe
    SIN idle bloquea sin invocar el binario; una fila previa IDLE o
    AUSENTE no bloquea; sin reintentos automáticos (INV-3)."""

    def test_pd9_prior_non_idle_blocks_without_invoking_binary(self) -> None:
        """PD-9: con un registro previo del mismo paquete cuya fila NO
        está idle, `blocked` SIN invocar el binario (registro de
        llamadas vacío); `session` sigue `null` (PD-8: pre-Popen, sin
        invocación); el diagnóstico nombra la sesión previa. RED hoy: la
        comprobación del intento previo (§2.7) no existe — el adaptador
        vigente invoca el binario normalmente."""
        fake = self.own_fake_runtime("pd9-blocked", variant="succeeded")
        self.patch_config(
            fake, {"mode": "standalone", "wait": {**FAST_WAIT_T2,
                                                   "timeout_seconds": 5}})
        self.write_raw_session_row(
            fake["sessions_db"], session_id=PRIOR_SESSION_T2,
            idle_outcome=None, pwd=str(self.root), with_final_text=False)
        self.fabricate_prior_dispatch_record(session_id=PRIOR_SESSION_T2)

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-9 fila previa no idle")

        self.assertEqual(
            out["termination"], "blocked",
            msg=f"registro previo con fila NO idle: la terminación no es "
                f"'blocked' (PD-9): {out['termination']!r}")
        self.assertFalse(
            out.get("session"),
            msg=f"PD-9/PD-8: bloqueado ANTES de invocar (sin Popen): "
                f"'session' debe seguir null: {out.get('session')!r}")
        self.assertEqual(
            self.binary_calls(fake), [],
            msg=f"registro previo con fila NO idle: el binario FUE "
                f"invocado (PD-9: blocked SIN invocar nada): "
                f"{self.binary_calls(fake)!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            PRIOR_SESSION_T2, diagnosis,
            msg=f"el diagnóstico no nombra la sesión previa no idle "
                f"(PD-9): {diagnosis!r}")
        self.assert_no_receipt_fabricated("PD-9 fila previa no idle")

    def test_pd9_prior_idle_dispatches_normally(self) -> None:
        """PD-9 (control, INV-3): con la fila previa IDLE, el despacho
        sigue normal — `completed`, y como MÁXIMO una invocación `run`.
        RED: puede PASAR hoy — sin la comprobación de §2.7, el vigente ya
        despacha sin mirar nada previo (declarado, no oculto): este
        método existe para probar que, cuando IMPLEMENTADA, la
        comprobación de §2.7 no bloquea de más (una fila previa idle no
        es intento vivo)."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime("pd9-idle-control", variant="succeeded")
        self.patch_config(
            fake, {"mode": "standalone", "wait": {**FAST_WAIT_T2,
                                                   "timeout_seconds": 5}})
        self.write_raw_session_row(
            fake["sessions_db"], session_id=PRIOR_SESSION_T2,
            idle_outcome="succeeded", pwd=str(self.root),
            with_final_text=True)
        self.fabricate_prior_dispatch_record(session_id=PRIOR_SESSION_T2)

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-9 fila previa idle (control)")

        self.assertEqual(
            out["termination"], "completed",
            msg=f"fila previa IDLE: no debería bloquear el despacho "
                f"(PD-9): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assertEqual(
            len(self.binary_calls(fake)), 1,
            msg=f"más de UNA invocación del binario (PD-9: como máximo "
                f"una invocación run por invocación de la interfaz): "
                f"{self.binary_calls(fake)!r}")


# ---------------------------------------------------------------- PD-10


class TestPd10ProportionalWait(Pd600T2Case):
    """PD-10: cero lecturas mientras el cliente vive; lecturas
    posteriores acotadas por §2.4; el store bloqueado por un escritor
    externo no detiene el despacho (reintenta según el calendario) y el
    adaptador JAMÁS escribe el store (INV-1)."""

    def test_pd10_zero_store_reads_while_client_alive_and_bounded_after(
            self) -> None:
        """PD-10: con un cliente que TARDA (`slow-then-idle`) y luego
        deja la fila idle, la traza NO registra NINGUNA conexión del
        adaptador dentro de la ventana [inicio, salida] del cliente
        (cero lecturas mientras vive); las lecturas posteriores a la
        salida están acotadas por §2.4 y el `store_reads` del registro
        I8 (PD-3) coincide con la traza."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd10-slow-then-idle", variant="slow-then-idle")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**SETTLE_WAIT_T2, "timeout_seconds": 5}})
        trace = self.install_read_trace(fake)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_traced(fake, trace)
        out = self.envelope(proc, "PD-10 slow-then-idle")

        self.assertEqual(
            out["termination"], "completed",
            msg=f"cliente lento que termina idle 'succeeded': la "
                f"terminación no es 'completed': {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")

        start_ts = float(fake["client_start_ts"].read_text(encoding="utf-8"))
        exit_ts = float(fake["client_exit_ts"].read_text(encoding="utf-8"))
        self.assertGreater(
            exit_ts - start_ts, SLOW_SECONDS * 0.8,
            msg="fixture: el cliente no vivió el tiempo esperado "
                "(precondición de 'mientras el cliente vive' rota)")

        entries = self.read_trace_entries(trace)
        alive_window = [e for e in entries if start_ts <= e["ts"] <= exit_ts]
        self.assertEqual(
            alive_window, [],
            msg=f"el adaptador leyó el store MIENTRAS el cliente vivía "
                f"(PD-10: cero lecturas con el cliente vivo): "
                f"{alive_window!r}")

        post_exit = [e for e in entries if e["ts"] > exit_ts]
        self.assertTrue(
            post_exit,
            msg="fixture: la traza no registró ninguna lectura posterior "
                "a la salida (¿PYTHONPATH no se propagó? — fallo de "
                "fixture, detener y reportar)")
        window = max(e["ts"] for e in post_exit) - exit_ts
        bound = expected_read_bound(
            SETTLE_WAIT_T2["poll_initial_seconds"],
            SETTLE_WAIT_T2["poll_max_seconds"], window)
        self.assertLessEqual(
            len(post_exit), bound,
            msg=f"lecturas posteriores a la salida ({len(post_exit)}) "
                f"exceden la cota de §2.4 (R ≤ {bound} para W={window:.2f}s)")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="no hay registro de worker con la procedencia nueva de "
                "§2.6 para esta terminación completed (PD-3, T1)")
        session_prov = str(worker_records[0]["provenance"].get("session", ""))
        reported = session_prov.split("store_reads=", 1)[1].split(";", 1)[0].strip()
        self.assertEqual(
            reported, str(len(post_exit)),
            msg=f"store_reads declarado ({reported!r}) no coincide con "
                f"la traza ({len(post_exit)}) (PD-3)")
        self.assert_t2_final_text_in_delivery()
        self.assert_receipt_no_gate()

    def test_pd10_locked_store_retries_until_released_without_adapter_write(
            self) -> None:
        """PD-10: con el store bloqueado por un escritor del fixture
        (`BEGIN EXCLUSIVE` en rollback journal, ventana acotada de
        {LOCK_HOLD_SECONDS}s), el adaptador reintenta según el
        calendario y TERMINA `completed` cuando se libera — SIN escribir
        el store: su mtime y contenido solo cambian por el escritor del
        fixture (INV-1: el adaptador abre el store SOLO mode=ro)."""
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd10-locked", variant="succeeded-after-lock-signal")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {"poll_initial_seconds": 0.05,
                            "poll_max_seconds": 0.2,
                            "settle_seconds": 3,
                            "terminate_grace_seconds": 0.3,
                            "preflight_timeout_seconds": 1,
                            "timeout_seconds": 5}})

        store_path = fake["sessions_db"]
        flag_path = fake["dir"] / "row-written.flag"
        baseline: dict = {}

        def _lock_after_signal() -> None:
            # Espera a que EL CLIENTE escriba la fila (con la sesión REAL
            # que el adaptador eligió, desconocida de antemano) y avise
            # por el centinela; el cliente se queda vivo 0.3s después de
            # avisar — margen de sobra para tomar el lock ANTES de que
            # salga (y por lo tanto antes de la primera lectura posible
            # del adaptador).
            deadline = time.monotonic() + 5.0
            while not flag_path.is_file() and time.monotonic() < deadline:
                time.sleep(0.01)
            if not flag_path.is_file():
                return  # fixture rota; el assert de abajo lo declara
            baseline["bytes"] = store_path.read_bytes()
            baseline["sha"] = hashlib.sha256(baseline["bytes"]).hexdigest()
            baseline["mtime"] = store_path.stat().st_mtime
            conn = sqlite3.connect(str(store_path), isolation_level=None)
            try:
                conn.execute("BEGIN EXCLUSIVE")
                time.sleep(LOCK_HOLD_SECONDS)
                conn.execute("ROLLBACK")
            finally:
                conn.close()

        locker = threading.Thread(target=_lock_after_signal, daemon=True)
        locker.start()

        trace = self.install_read_trace(fake)
        proc = self.dispatch_traced(fake, trace)
        locker.join(timeout=5)
        out = self.envelope(proc, "PD-10 store bloqueado")

        self.assertIn(
            "sha", baseline,
            msg="fixture: el escritor del lock nunca vio el centinela "
                "row-written.flag (el cliente no llegó a escribir la "
                "fila, o lo hizo fuera de la ventana esperada) — fallo "
                "de fixture, detener y reportar, no debilitar la "
                "aserción")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"store bloqueado y luego liberado: la terminación no es "
                f"'completed' (PD-10: reintenta y termina al liberarse): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        final_bytes = store_path.read_bytes()
        self.assertEqual(
            hashlib.sha256(final_bytes).hexdigest(), baseline["sha"],
            msg="el contenido del store cambió (PD-10/INV-1: el "
                "adaptador NUNCA escribe el store; el único escritor "
                "legítimo es el propio fixture, que no modificó nada — "
                "BEGIN EXCLUSIVE + ROLLBACK sin escritura)")
        self.assertEqual(
            store_path.stat().st_mtime, baseline["mtime"],
            msg="el mtime del store cambió (PD-10: solo debe cambiar "
                "por el escritor del fixture)")

        entries = self.read_trace_entries(trace)
        self.assertTrue(
            entries,
            msg="fixture: la traza no registró ninguna lectura (¿el "
                "PYTHONPATH no se propagó? — fallo de fixture, detener "
                "y reportar)")
        self.assertGreater(
            len(entries), 1,
            msg=f"solo UNA lectura pese al store bloqueado durante "
                f"{LOCK_HOLD_SECONDS}s: no hay evidencia de reintento "
                f"(PD-10: locked/busy cuenta como lectura y reintenta): "
                f"{entries!r}")
        self.assertLessEqual(
            len(entries), 10,
            msg=f"demasiadas lecturas ({len(entries)}) para un bloqueo "
                f"de {LOCK_HOLD_SECONDS}s con backoff que duplica hasta "
                f"0.2s (un sondeo fijo de 50ms habría dado ~20; esto "
                f"sugiere que NO se está usando el calendario de §2.4): "
                f"{entries!r}")

        self.assert_t2_final_text_in_delivery()
        self.assert_receipt_no_gate()


# ---------------------------------------------------------------- PD-11


class TestPd11RespondsWithinBudget(Pd600T2Case):
    """PD-11: el adaptador SIEMPRE responde dentro de la cota de la
    interfaz (incluida la gracia efectiva de §2.5); el envelope es del
    adaptador, NUNCA el `did not answer within` de la interfaz; una cota
    ≤ `WAIT_RESERVE_SECONDS` bloquea sin despacho."""

    def test_pd11_three_variants_respond_within_cota_and_total_budget(
            self) -> None:
        """PD-11: `hangs`, `no-idle` (fila no idle con settle por encima
        de la cota: es LA COTA la que decide, D-3) y `transport-error`,
        cada una con su PROPIO proyecto/store (TestPd6 precedent: un
        registro previo no idle de la variante anterior no debe
        PD-9-bloquear la siguiente), cota ≤ 2s cada una; el techo de HOST
        del total (las tres) es `PD11_TOTAL_UPPER_SECONDS` = 75 s
        (>= 10x ≈ 66 s de la conducta correcta), no «total ≤ 10 s»: la
        discriminación «acotada por encima de la cota» no es observable hoy
        y queda como pérdida declarada en deferred-hardening (008-005
        PC-6, review F1/F7)."""
        total_elapsed = 0.0
        cases = (
            ("hangs", "hangs", HANGS_WAIT, "timeout"),
            ("no-idle", "exit-row-not-idle", NO_IDLE_PD11_WAIT, "timeout"),
            ("transport-error", "transport-error", FAST_WAIT_T2,
             "transport-error"),
        )
        for label, variant, wait_cfg, expected in cases:
            with self.subTest(variant=label):
                self.assert_derived_agents_published()
                fake = self.own_fake_runtime(f"pd11-{label}", variant=variant)
                self.patch_config(
                    fake, {"mode": "standalone",
                           "wait": {**wait_cfg, "timeout_seconds": 2}})
                started = time.monotonic()
                proc = self.dispatch(fake)
                elapsed = time.monotonic() - started
                total_elapsed += elapsed
                out = self.envelope(proc, f"PD-11 {label}")
                # PC-8: la cota (2s) es el sujeto y se conserva; si la
                # preparación la agotó, el no despacho acotado es válido.
                if pc8_preparatory_exhaustion(self, out, fake,
                                              f"PD-11 {label}"):
                    self.assertLess(elapsed, PD11_UPPER_SECONDS,
                                    msg=f"[{label}] (008-005 T-A, sitio 13, "
                                        f"PC-6) desacotado ({elapsed:.2f}s "
                                        f">= {PD11_UPPER_SECONDS}s)")
                    continue

                diagnosis = (out.get("diagnosis") or "").lower()
                self.assertNotIn(
                    "did not answer within", diagnosis,
                    msg=f"[{label}] el envelope es el de LA INTERFAZ (no "
                        f"respondió a tiempo), no el del adaptador "
                        f"(PD-11): {out!r}")
                self.assertEqual(
                    out["termination"], expected,
                    msg=f"[{label}] terminación inesperada: "
                        f"{out['termination']!r} != {expected!r}, "
                        f"diagnosis {out.get('diagnosis')!r}")
                # 008-005 PC-6 (T-A, sitio 14, review F1): el techo mide el
                # HOST (25 s >= 10x ≈ 2,2 s de la conducta correcta), no la
                # cota de 2 s; la espera acotada por encima de la cota no
                # es observable hoy (pérdida declarada en
                # deferred-hardening).
                self.assertLess(
                    elapsed, PD11_UPPER_SECONDS,
                    msg=f"[{label}] (008-005 T-A, sitio 14, PC-6) el host "
                        f"excedió el techo de liveness: {elapsed:.2f}s >= "
                        f"{PD11_UPPER_SECONDS}s (el techo mide el host, "
                        f">= 10x la conducta correcta ≈ 2,2 s, no la cota "
                        f"de 2 s; la discriminación «acotada por encima de "
                        f"la cota» no es observable hoy: pérdida declarada "
                        f"en deferred-hardening)")
        self.assertLess(
            total_elapsed, PD11_TOTAL_UPPER_SECONDS,
            msg=f"PD-11 (008-005 T-A, sitio 15, PC-6): presupuesto total "
                f"del focal excedido: {total_elapsed:.2f}s >= "
                f"{PD11_TOTAL_UPPER_SECONDS}s (75 s >= 10x ≈ 66 s de la "
                f"conducta correcta y < 3 x el defecto; una ejecución por "
                f"variante)")

    def test_pd11_cota_at_reserve_blocks_before_dispatch(self) -> None:
        """PD-11 (cota mínima): `timeout_seconds` == `WAIT_RESERVE_SECONDS`
        (1,0s, el límite `≤` de la regla) → `blocked` SIN despacho; el
        binario nunca se invoca."""
        fake = self.own_fake_runtime("pd11-cota-reserva", variant="succeeded")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**FAST_WAIT_T2,
                            "timeout_seconds": WAIT_RESERVE_SECONDS}})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-11 cota == reserva")

        self.assertEqual(
            out["termination"], "blocked",
            msg=f"timeout_seconds == WAIT_RESERVE_SECONDS: la "
                f"terminación no es 'blocked' (PD-11): "
                f"{out['termination']!r}")
        self.assertEqual(
            self.binary_calls(fake), [],
            msg=f"cota == reserva: el binario FUE invocado (PD-11: "
                f"blocked sin despacho): {self.binary_calls(fake)!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "timeout_seconds", diagnosis,
            msg=f"el diagnóstico no nombra la clave timeout_seconds "
                f"(PD-11): {diagnosis!r}")

    def test_pd11_completed_server_mode_with_preflight_stays_within_cota(
            self) -> None:
        """REQUISITO ADICIONAL DEL ORQUESTADOR (evidencia de T1): el
        camino `completed` en modo SERVIDOR CON preflight también debe
        responder dentro de la cota (D-3 resuelve la latencia extra del
        preflight+registro de T1). UNA sola corrida es evidencia DÉBIL
        contra un flake de ~1 de cada 3 (declarado, no oculto — ver
        reporte del rol para la recomendación de repetición)."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": T2_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.own_fake_runtime(
            "pd11-server-completed", variant="succeeded")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": {**FAST_WAIT_T2, "timeout_seconds": 2}})

        started = time.monotonic()
        proc = self.dispatch(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "PD-11 completed servidor con preflight")

        # PC-8: la cota (2s) es el sujeto y se conserva; si la preparación
        # la agotó, la clasificación válida es el no despacho — acotado.
        if pc8_preparatory_exhaustion(self, out, fake, "PD-11"):
            self.assertLess(elapsed, PD11_UPPER_SECONDS,
                            msg=f"PD-11 (008-005 T-A, sitio 16, PC-6): el "
                                f"no despacho quedó desacotado "
                                f"({elapsed:.2f}s >= {PD11_UPPER_SECONDS}s)")
            return

        diagnosis = (out.get("diagnosis") or "").lower()
        self.assertNotIn(
            "did not answer within", diagnosis,
            msg=f"el envelope es el de la interfaz, no el del adaptador "
                f"(PD-11/D-3): {out!r}")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"camino completed en modo servidor con preflight: "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        # 008-005 PC-6 (T-A, sitio 17, review F1): el techo mide el HOST
        # (25 s >= 10x ≈ 2,2 s de la conducta correcta), no la cota de 2 s;
        # la discriminación «acotada por encima de la cota» no es
        # observable hoy: pérdida declarada en deferred-hardening.
        self.assertLess(
            elapsed, PD11_UPPER_SECONDS,
            msg=f"PD-11 (008-005 T-A, sitio 17, PC-6): el host excedió el "
                f"techo de liveness: {elapsed:.2f}s >= "
                f"{PD11_UPPER_SECONDS}s (el techo mide el host, >= 10x la "
                f"conducta correcta ≈ 2,2 s, no la cota de 2 s; la "
                f"discriminación «acotada por encima de la cota» no es "
                f"observable hoy: pérdida declarada en deferred-hardening)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
