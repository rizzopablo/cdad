#!/usr/bin/env python3
"""006-001 review-fix RED — los tres bloqueantes de la review formal
(docs/specs/006-001-opencode-concurrency-reliability/review.md, B1-B3),
contra la spec v2 aprobada (spec.md §2.3b, §2.4, §2.5, §2.7; PD-7, PD-9,
PD-11; INV-9, INV-10; D-3).

FAKE PROPIO de este focal: el binario falso de AQUÍ (`RF_FAKE_BINARY_SOURCE`,
vía `ReviewFixCase.fake_runtime_rf`) es autónomo — responde ÉL MISMO a
`--version` y a `service status` (según `service-scenario.json`, con
retardo opcional `service-delay.txt`) y ejecuta variantes de `run` propias
(`succeeded`, `exit-row-not-idle`, `hangs` con sleep largo e SIGTERM
ignorado). NINGÚN focal existente se modifica ni su fake se toca; se
reutiliza SOLO infraestructura de fixture YA PUBLICADA por import (el
mismo patrón que T2 y T1b usaron con T1): `patch_config`/`dispatch`/
`envelope`/`assert_no_receipt_fabricated` (Pd600T1Case),
`write_raw_session_row`/`fabricate_prior_dispatch_record`/
`kill_pid_if_alive`/`assert_adapter_in_product`/`assert_derived_agents_
published` (Pd600T2Case/AdapterCase) y `scenario_running`/
`write_service_registry`/`dispatch_service`/`service_status_calls`/
`run_argv` (T1bServiceCase). Sin valores del host: todo url/puerto/store/
contraseñas son de fixture en tempdir (INV-7).

Mapa test → bloqueante/postcondición:

  B1 (TestB1AdapterEnvelopeWithinCota):
    test_b1_medium_cota_slow_preflight_hangs_adapter_envelope_with_session
      (B1 / PD-11 / D-3 / §2.5: cota media ~10 s, preflight de servidor
      retardado 4 s > 25 % del presupuesto interno (B = 10 − 1 − g ≈ 8,8;
      25 % ≈ 2,2 s), cliente que se cuelga → el envelope proviene del
      ADAPTADOR (`timeout`, con la sesión elegida) dentro de la cota de la
      interfaz; NUNCA el `did not answer within` de la interfaz con
      `session: null` — que perdería la correlación de PD-8)

  B2 (TestB2PriorAttemptUnaffirmable):
    test_b2_prior_attempt_unaffirmable_store_blocks_before_dispatch
      (B2 / PD-9 / INV-9 / INV-10 / §2.7: registro previo del mismo
      paquete con sesión cuya fila NO PUEDE AFIRMARSE — un escritor del
      fixture mantiene `BEGIN EXCLUSIVE` de forma persistente sobre el
      store — → `blocked` ANTES del despacho, sin invocar `run`, con un
      diagnóstico que declara que no se puede afirmar el estado del
      intento previo, espejo de la interpretación cerrada de §2.3b.
      Fail-closed: lo no observable es `unknown`, no «ausente»)

  B3 (TestB3ServiceWaitAndPreflight):
    test_b3a_service_mode_row_not_idle_times_out_at_cota_ignoring_settle
      (B3 / PD-7 / §2.4 dif. enmienda: modo `service` (service status con
      URL y versión compatible), fila NO idle con `settle_seconds` chico
      → `timeout` al vencer la cota; el asentamiento NO decide; sin
      recibo; PD-8: la sesión elegida viaja en el envelope)
    test_b3b_service_preflight_bounded_responds_within_cota
      (B3 / PD-11 dif. enmienda: el preflight de MODO SERVICIO
      (`service status` retardado 1,2 s) queda acotado por el presupuesto
      restante y el despacho completo responde DENTRO de la cota de la
      interfaz, con envelope del adaptador)

RED esperado:
  - B1: FALLA hoy por AssertionError del contrato. Mecanismo (review B1):
    el piso proporcional sin tope superior (`CLIENT_MIN_BUDGET_SHARE`)
    reserva para el cliente 0,75·B ≈ 6,6 s pase lo que pase; con el
    preflight consumiendo 4 s, el adaptador responde ≈ 4 + 6,6 + 0,2 >
    10 s → la interfaz mata al adaptador y emite SU envelope
    (`did not answer within`, `session: null`). Las aserciones que fallan
    son sobre el comportamiento ausente (origen del envelope, sesión,
    terminación), nunca import/sintaxis/fixture.
  - B2: FALLA hoy por AssertionError del contrato. Mecanismo (review B2):
    el chequeo del intento previo falla ABIERTO ante store busy
    (`except _StoreBusy: continue`) → el despacho sigue → se invoca `run`
    → `completed`: exactamente el doble-escritor del mismo paquete que
    INV-10 prohíbe, en el rincón de mayor riesgo (worker vivo sosteniendo
    locks). La fila previa del fixture es IDLE: si el store fuera LEGIBLE,
    el despacho seguiría normal (PD-9 control), así que la ÚNICA razón del
    `blocked` exigido es la imposibilidad de AFIRMAR el estado — la
    aserción del diagnóstico protege contra un GREEN vacuo (blocked por
    otra causa).
  - B3a y B3b: PUEDEN PASAR hoy (la implementación comparte la rama
    `!standalone` de la espera y ya acota el preflight por
    `min(preflight_timeout, presupuesto restante)`): son COBERTURA de
    cláusulas nombradas por la enmienda que la review encontró sin focal —
    declarado, no oculto. Un refactor que cambie `!= "standalone"` por
    `== "server"` dejaría B3a en rojo.

Presupuesto de tiempos del focal: valores de espera chicos; el focal
completo corre en « 30 s (« 60 s exigidos). Riesgo de flake declarado (misma
naturaleza que la deuda de cota chica ya registrada en el epic): B1 depende
de que el overhead de arranque « 1 s (la reserva fija); bajo carga fuerte
del host, B1 podría llegar a la cota por el camino CORRECTO — en ese caso
el fallo sería de la banda de margen, no del contrato, y se reporta como
tal, no se debilite la aserción.
"""

from __future__ import annotations

import http.server
import json
import sqlite3
import threading
import time
import unittest
from pathlib import Path

from test_005_009_t2_opencode_adapter import FAKE_MODEL, FAKE_RUNTIME
from test_006_001_t1_selection import (
    closed_port_url, pc8_preparatory_exhaustion)
from test_006_001_t1b_service_mode import T1bServiceCase
from test_006_001_t2_wait_recovery import Pd600T2Case

# --------------------------------------------------------------- constantes

RF_FAKE_VERSION = "opencode-fake-rf 1.0.0"
RF_CLIENT_SEMVER = RF_FAKE_VERSION.rsplit(" ", 1)[-1]  # "1.0.0"
RF_DEFAULT_SESSION = "ses-fake-006-001-rf-0001"
RF_PRIOR_SESSION = "ses-fake-006-001-rf-prior-0001"
RF_ROW_MODEL = "fixture-006-001-rf-model"
RF_USER_TEXT = (
    "Encargo canónico recibido por el binario opencode falso review-fix "
    "(006-001).")
RF_FINAL_TEXT = (
    "# Entrega del rol (binario opencode falso review-fix, 006-001)\n\n"
    "Texto final acordado por la fixture review-fix de 006-001: B1 (cota "
    "media), B2 (intento previo innegociable) y B3 (espera y preflight en "
    "modo servicio).")

WAIT_RESERVE_SECONDS = 1.0  # spec §2.5: reserva FIJA del adaptador

RF_HANG_SLEEP_SECONDS = 40        # el cliente colgado duerme más que todo
B1_COTA_SECONDS = 10.0            # B1: banda de cota media (~10 s)
B1_PREFLIGHT_DELAY_SECONDS = 4.0  # > 25 % del budget interno (≈ 2,2 s)
B3B_SERVICE_DELAY_SECONDS = 1.2   # retardo del `service status` (B3b)

# 008-005 PC-6 (T-A/T-B). Regla: el techo de una cota de duración queda a
# >= 10x el valor de la conducta correcta, nunca igual al plazo que vigila.
# - Sitio 6 (B1, T-B): correcto ≈ cota 10 s; el 10x (≈ 100 s) queda por
#   encima del defecto natural (RF_HANG_SLEEP_SECONDS = 40 s) → la
#   duración no discrimina; la decisión (origen del envelope, PD-11) ya
#   está assertada y el techo se declara liveness.
# - Sitios 7 y 8 (B3a, T-A): cota 2 s; correcto ≈ 2,2 s (cota + gracia);
#   techo 25 s >= 10x ≈ 22 s y < el no acotamiento (timeout del harness,
#   300 s). El defecto "settle usado" (más corto) lo separan la terminación
#   y la cota inferior.
# - Sitio 9 (B3b, T-A): correcto ≈ 1,7 s (preflight de 1,2 s + vuelta);
#   techo 25 s >= 10x ≈ 17 s y < el no acotamiento; el plazo vigilado es
#   la cota de 10 s (25 != 10).
# Pérdida declarada (PC-6, review F1): en los sitios 7-9 — como en PD-7 y
# PD-11 de test_006_001_t2_wait_recovery.py — el techo mide el HOST, no la
# cota: una espera acotada pero por ENCIMA de la cota (2x) hoy no es
# observable (el envelope del producto no expone duración) y queda
# registrada en deferred-hardening del spec 008-005 en vez de presentarse
# como guarda «en la cota».
LIVENESS_UPPER_SECONDS = 60
B3A_UPPER_SECONDS = 25.0
B3B_UPPER_SECONDS = 25.0

RF_FAST_WAIT = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 0.3,
    "terminate_grace_seconds": 0.2,
    "preflight_timeout_seconds": 1,
}


def _lit(text: str) -> str:
    return json.dumps(text)


# ------------------------------------- servidor /api/info con retardo (B1)


class _DelayedInfoHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format_: str, *args: object) -> None:  # noqa: D401
        pass  # silencia el log de acceso del fixture

    def do_GET(self) -> None:  # noqa: N802 (API de BaseHTTPRequestHandler)
        server = self.server
        started = time.monotonic()
        server.requests.append({"path": self.path, "started_at": started})
        if self.path != "/api/info":
            self.send_response(404)
            self.end_headers()
            return
        time.sleep(server.delay_seconds)
        server.requests[-1]["served_after"] = time.monotonic() - started
        body = server.body_bytes
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class DelayedInfoServer:
    """Fixture propia (B1): servidor HTTP de `/api/info` en loopback que
    RESPONDE CON RETARDO fijo — el preflight de servidor queda retardado
    más allá de la fracción del presupuesto que el piso vigente asume."""

    def __init__(self, *, body: bytes, delay: float) -> None:
        self._httpd = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), _DelayedInfoHandler)
        self._httpd.daemon_threads = True
        self._httpd.body_bytes = body
        self._httpd.delay_seconds = delay
        self._httpd.requests = []
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    @property
    def url(self) -> str:
        host, port = self._httpd.server_address
        return f"http://{host}:{port}"

    @property
    def requests(self) -> list[dict]:
        return list(self._httpd.requests)

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=5)


# --------------------------------------------------- binario falso review-fix


RF_FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
# Binario OpenCode FALSO, PROPIO de tests/test_006_001_reviewfix.py
# (review-fix B1-B3: NO es el fake compartido de test_005_009_t2_opencode_
# adapter.py ni los fakes propios de T1/T1b/T2, que quedan intactos).
# Protocolo:
#   1. --version: responde ANTES de tocar stdin (preflight del cliente).
#   2. service status: responde según <fake>/service-scenario.json
#      (stdout + rc), tras un retardo opcional <fake>/service-delay.txt.
#   3. run (o cualquier otro argv): variante de <fake>/variant —
#      succeeded | exit-row-not-idle | hangs — escribe el store SQLite
#      (mismo esquema que el resto de los focales) y termina.
#   Toda invocación queda registrada en <fake>/rf-calls.jsonl.
import hashlib
import json
import os
import signal
import sqlite3
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent        # <fake>/bin
_FAKE = _HERE.parent                           # <fake>
_LOG = _FAKE / "rf-calls.jsonl"
_CLIENT_PID = _FAKE / "client.pid"
_PACKET_MARKER = b"---cdad-packet-json"


def _append(entry):
    with _LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


argv = sys.argv[1:]


def _argv_value(name):
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
    return None


if "--version" in argv:
    _append({"argv": argv, "kind": "version"})
    sys.stdout.write(@VERSION_LINE@ + "\n")
    sys.stdout.flush()
    sys.exit(0)

if argv[:2] == ["service", "status"]:
    delay_path = _FAKE / "service-delay.txt"
    if delay_path.is_file():
        time.sleep(float(delay_path.read_text(encoding="utf-8").strip()))
    scenario = json.loads(
        (_FAKE / "service-scenario.json").read_text(encoding="utf-8"))
    _append({"argv": argv, "kind": "service-status"})
    sys.stdout.write(scenario.get("stdout", ""))
    sys.stdout.flush()
    sys.exit(int(scenario.get("rc", 0)))

# ---- despacho (run) ----
variant = (_FAKE / "variant").read_text(encoding="utf-8").strip() or "succeeded"
session_id = _argv_value("--session") or @DEFAULT_SESSION@
agent_id = _argv_value("--agent") or "cdad-test-writer"
pwd_value = os.environ.get("PWD") or os.getcwd()


def _sessions_db_path():
    try:
        config = json.loads(
            (_FAKE / "exec-config.json").read_text(encoding="utf-8"))
        value = config.get("sessions_db")
    except (OSError, ValueError):
        value = None
    return Path(value) if value else (_FAKE / "sessions.db")


store_path = _sessions_db_path()

# transporte byte-idéntico por stdin (§2.8); argv-file como alternativa
packet = None
packet_transport = "unfounded"
try:
    if not sys.stdin.isatty():
        data = sys.stdin.buffer.read()
        if data.lstrip().startswith(_PACKET_MARKER):
            packet = data
            packet_transport = "stdin"
except Exception:
    pass
if packet is None:
    for token in argv:
        candidate = Path(token)
        if candidate.is_file():
            blob = candidate.read_bytes()
            if blob.lstrip().startswith(_PACKET_MARKER):
                packet = blob
                packet_transport = "argv-file"
                break

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
        "transport": packet_transport,
        "sha256": hashlib.sha256(packet).hexdigest(),
        "bytes": len(packet),
    }


def _write_store(idle_outcome, *, with_final_text):
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
            (session_id, agent_id, @ROW_MODEL@, pwd_value, now - 1.0, now,
             idle, idle_outcome))
        conn.execute(
            "INSERT INTO session_message (id, session_id, type, seq, data)"
            " VALUES (?, ?, ?, ?, ?)",
            (f"msg-0001-{session_id}", session_id, "user", 1,
             json.dumps({"content": [{"type": "text", "text": @USER_TEXT@}]})))
        if with_final_text:
            conn.execute(
                "INSERT INTO session_message (id, session_id, type, seq,"
                " data) VALUES (?, ?, ?, ?, ?)",
                (f"msg-0002-{session_id}", session_id, "assistant", 2,
                 json.dumps({"content": [{"type": "text",
                                          "text": @FINAL_TEXT@}]})))
        conn.commit()
    finally:
        conn.close()
    os.replace(tmp_path, store_path)


if variant == "succeeded":
    _write_store("succeeded", with_final_text=True)
    _append(entry)
elif variant == "exit-row-not-idle":
    _write_store(None, with_final_text=False)
    _append(entry)
elif variant == "hangs":
    _CLIENT_PID.write_text(str(os.getpid()), encoding="utf-8")
    _append(entry)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    sys.stdout.flush()
    time.sleep(@HANG_SLEEP@)
    sys.exit(0)
else:
    _append(entry)
'''


# ------------------------------------------------------------------ fixture


class ReviewFixCase(T1bServiceCase, Pd600T2Case):
    """Base del focal review-fix: fixture PROPIA (binario falso autónomo)
    sobre la base publicada por import. NINGÚN foca existente se modifica.

    MRO (diamante estándar, sin conflictos de nombres):
    ReviewFixCase → T1bServiceCase → Pd600T2Case → Pd600T1Case →
    AdapterCase → DelegateCase."""

    def fake_runtime_rf(self, name: str, *,
                        variant: str = "succeeded") -> dict:
        """Runtime falso PROPIO: binario autónomo (version + service status
        con escenario/retardo + variantes de run), exec-config de fixture,
        escenario de `service status`, registro del servicio (D-11) en un
        directorio de ESTADO descartable y URL de servicio en un puerto
        CERRADO de loopback (nada escucha: si el adaptador abriera
        conexiones — PD-14 lo prohíbe — el despacho feliz no completaría)."""
        self.assert_adapter_in_product()
        fake_dir = Path(self._tmp) / "fake-runtime-rf" / name
        bin_dir = fake_dir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        binary = bin_dir / "opencode-fake-rf"
        binary.write_text(
            RF_FAKE_BINARY_SOURCE
            .replace("@VERSION_LINE@", _lit(RF_FAKE_VERSION))
            .replace("@DEFAULT_SESSION@", _lit(RF_DEFAULT_SESSION))
            .replace("@ROW_MODEL@", _lit(RF_ROW_MODEL))
            .replace("@USER_TEXT@", _lit(RF_USER_TEXT))
            .replace("@FINAL_TEXT@", _lit(RF_FINAL_TEXT))
            .replace("@HANG_SLEEP@", repr(RF_HANG_SLEEP_SECONDS)),
            encoding="utf-8")
        binary.chmod(0o755)
        (fake_dir / "variant").write_text(variant + "\n", encoding="utf-8")
        logs_dir = fake_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        config_path = fake_dir / "exec-config.json"
        config = {
            "runtime": FAKE_RUNTIME,
            "binary": str(binary),
            "binary_version": RF_FAKE_VERSION,
            "model": FAKE_MODEL,
            "logs_dir": str(logs_dir),
            "sessions_db": str(fake_dir / "sessions.db"),
            "wait": {"timeout_seconds": 5},
        }
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        state = fake_dir / "state-home"
        state.mkdir(parents=True, exist_ok=True)
        return {
            "dir": fake_dir,
            "binary": binary,
            "config": config_path,
            "calls": fake_dir / "rf-calls.jsonl",
            "sessions_db": fake_dir / "sessions.db",
            # el log propio es TAMBIÉN el log de invocaciones del envoltorio
            # (mi fake registra todo él mismo): service_status_calls/run_argv
            # de T1bServiceCase operan sobre wrapper_calls.
            "wrapper_calls": fake_dir / "rf-calls.jsonl",
            "scenario": fake_dir / "service-scenario.json",
            "state": state,
            "registry": state / "opencode" / "service.json",
            "service_url": closed_port_url(),
            "client_pid": fake_dir / "client.pid",
        }

    # -- observadores propios ----------------------------------------------

    def dispatch_calls(self, fake: dict) -> list[dict]:
        return [call for call in self.wrapper_calls(fake)
                if call.get("kind") == "dispatch"]

    def chosen_session(self, fake: dict, label: str) -> str:
        calls = self.dispatch_calls(fake)
        self.assertEqual(
            len(calls), 1,
            msg=f"{label}: el número de invocaciones `run` (con paquete) "
                f"no es UNA: {[c.get('argv') for c in calls]!r}")
        return calls[0]["session_id_written"]

    def assert_no_run_invoked(self, fake: dict, label: str) -> None:
        run_calls = [
            call for call in self.wrapper_calls(fake)
            if call.get("kind") == "dispatch"
            or (call.get("argv") and call["argv"][0] == "run")]
        self.assertEqual(
            run_calls, [],
            msg=f"{label}: se invocó `run` pese al bloqueo exigido antes "
                f"del despacho: "
                f"{[c.get('argv') for c in run_calls]!r}")


# -------------------------------------------------------------------- B1


class TestB1AdapterEnvelopeWithinCota(ReviewFixCase):
    """B1 (PD-11, D-3, §2.5): en la banda de cota media (~10 s) con un
    preflight de servidor retardado más allá del 25 % del presupuesto y un
    cliente que se cuelga, el envelope proviene del ADAPTADOR (`timeout`,
    con la sesión elegida) dentro de la cota de la interfaz — NUNCA el
    `did not answer within` de la interfaz (que pierde la sesión, PD-8)."""

    def test_b1_medium_cota_slow_preflight_hangs_adapter_envelope_with_session(
            self) -> None:
        """B1 / PD-11 / D-3: cota 10 s (banda media); el preflight de
        servidor (/api/info) tarda 4 s — por encima del 25 % del
        presupuesto interno (B = 10 − 1 − 0,2 = 8,8; 25 % ≈ 2,2 s) — y el
        cliente se cuelga. Exigido: el envelope es del ADAPTADOR —
        terminación `timeout` con la SESIÓN ELEGIDA — y llega dentro de la
        cota de la interfaz; jamás el `did not answer within` de la
        interfaz. RED hoy: el piso proporcional sin tope superior le da al
        cliente 0,75·B ≈ 6,6 s pase lo que pase → el adaptador responde
        ≈ 4 + 6,6 + 0,2 > 10 s → la interfaz lo mata y emite SU envelope."""
        info_server = DelayedInfoServer(
            body=json.dumps({"version": RF_CLIENT_SEMVER}).encode(),
            delay=B1_PREFLIGHT_DELAY_SECONDS)
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_rf("b1-cota-media", variant="hangs")
        self.patch_config(
            fake,
            {"mode": "server", "server": info_server.url,
             "wait": {"poll_initial_seconds": 0.05,
                      "poll_max_seconds": 0.2,
                      "settle_seconds": 0.3,
                      "terminate_grace_seconds": 0.2,
                      "preflight_timeout_seconds": 6,
                      "timeout_seconds": B1_COTA_SECONDS}})

        started = time.monotonic()
        proc = self.dispatch(fake)
        # limpieza temprana: si la interfaz mata al adaptador, el cliente
        # puede quedar huérfano (grupo propio sin padre que lo recoja)
        if fake["client_pid"].is_file():
            self.addCleanup(
                self.kill_pid_if_alive,
                int(fake["client_pid"].read_text(encoding="utf-8").strip()))
        elapsed = time.monotonic() - started
        out = self.envelope(
            proc, "B1 cota media con preflight lento y cliente colgado")

        # precondición del escenario: el retardo del preflight OCURRIÓ
        requests = info_server.requests
        self.assertEqual(
            len(requests), 1,
            msg=f"B1 precondición: el preflight no hizo EXACTAMENTE una "
                f"request a /api/info: {requests!r}")
        self.assertGreaterEqual(
            requests[0].get("served_after", 0),
            B1_PREFLIGHT_DELAY_SECONDS,
            msg=f"B1 precondición: el preflight no quedó retardado "
                f"({requests[0]!r}; se esperaba >= "
                f"{B1_PREFLIGHT_DELAY_SECONDS}s)")

        for text_name, text in (("diagnosis", out.get("diagnosis") or ""),
                                ("stdout", proc.stdout)):
            self.assertNotIn(
                "did not answer within", text.lower(),
                msg=f"B1 ({text_name}): el envelope es el de LA INTERFAZ "
                    f"(`did not answer within`: el adaptador no respondió "
                    f"dentro de la cota — exactamente el resultado que "
                    f"PD-11 prohíbe): {str(text)[:400]!r}")
        self.assertEqual(
            out["termination"], "timeout",
            msg=f"B1: cliente colgado con preflight lento en cota media: "
                f"la terminación no es 'timeout' del ADAPTADOR (PD-11/D-3): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        chosen = self.chosen_session(fake, "B1")
        self.assertEqual(
            out.get("session"), chosen,
            msg=f"B1/PD-8: el envelope debe llevar la sesión elegida "
                f"({chosen!r}) — un envelope de la INTERFAZ la pierde "
                f"(session null): {out.get('session')!r}")
        self.assertLess(
            elapsed, LIVENESS_UPPER_SECONDS,
            msg=f"liveness (008-005 T-B, sitio 6, PC-6): el despacho no "
                f"retornó ({elapsed:.2f}s >= guardia de liveness) — el "
                f"discriminador del contrato es el ORIGEN del envelope, "
                f"ya assertado arriba, no el reloj")
        self.assert_no_receipt_fabricated("B1")


# -------------------------------------------------------------------- B2


class TestB2PriorAttemptUnaffirmable(ReviewFixCase):
    """B2 (PD-9, INV-9, INV-10, §2.7): un registro previo del mismo paquete
    con sesión, cuya fila NO PUEDE AFIRMARSE (store bloqueado de forma
    persistente por un escritor del fixture), debe producir `blocked` ANTES
    del despacho — fail-closed, espejo de la interpretación cerrada de
    §2.3b («no se puede afirmar…» → blocked). Hoy el chequeo falla ABIERTO
    ante store busy: permitiría un segundo worker vivo del mismo paquete
    contra el mismo store/servicio — el doble-escritor que INV-10 prohíbe."""

    def test_b2_prior_attempt_unaffirmable_store_blocks_before_dispatch(
            self) -> None:
        """B2 / PD-9 / INV-9 / INV-10: registro previo del mismo paquete
        con sesión; la fila previa del store es INCOGNOSCIBLE porque un
        escritor del fixture mantiene `BEGIN EXCLUSIVE` de forma
        persistente (la fila, si fuera LEGIBLE, está IDLE: legible ⇒ el
        despacho seguiría normal, PD-9 control — así la única razón del
        `blocked` exigido es la imposibilidad de AFIRMAR el estado, INV-9:
        lo no observable es `unknown`, no «ausente»). Resultado exigido:
        `blocked` ANTES del despacho — sin invocar `run`, `session` null
        (PD-8) — con un diagnóstico que declare que NO SE PUEDE AFIRMAR el
        estado del intento previo. RED hoy: fail-open → despacha → run →
        completed."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime_rf("b2-prior-unaffirmable",
                                    variant="succeeded")
        self.patch_config(
            fake, {"mode": "standalone",
                   "wait": {**RF_FAST_WAIT, "timeout_seconds": 2}})
        # Fila previa IDLE (legible ⇒ no bloquearía, PD-9 control).
        self.write_raw_session_row(
            fake["sessions_db"], session_id=RF_PRIOR_SESSION,
            idle_outcome="succeeded", pwd=str(self.root),
            with_final_text=True)
        self.fabricate_prior_dispatch_record(session_id=RF_PRIOR_SESSION)

        acquired = threading.Event()
        release = threading.Event()

        def _hold_exclusive() -> None:
            # Escritor del fixture: toma el lock EXCLUSIVO y lo SOSTIENE de
            # forma persistente (nunca escribe nada: BEGIN + ROLLBACK).
            conn = sqlite3.connect(str(fake["sessions_db"]),
                                   isolation_level=None, timeout=5)
            try:
                conn.execute("BEGIN EXCLUSIVE")
                acquired.set()
                release.wait(60)
                conn.execute("ROLLBACK")
            finally:
                conn.close()

        locker = threading.Thread(target=_hold_exclusive, daemon=True)
        locker.start()
        self.assertTrue(
            acquired.wait(10),
            msg="fixture: el escritor del lock no tomó BEGIN EXCLUSIVE")
        self.addCleanup(release.set)
        self.addCleanup(locker.join, 10)

        # Precondición del escenario: una lectura fresca NO puede afirmar
        # la fila (store busy) — la misma condición que enfrentará el
        # chequeo del intento previo.
        probe = sqlite3.connect(str(fake["sessions_db"]), timeout=0)
        try:
            locked = False
            try:
                probe.execute("SELECT COUNT(*) FROM session_v2").fetchone()
            except sqlite3.OperationalError:
                locked = True
            self.assertTrue(
                locked,
                msg="fixture: la lectura de prueba pudo leer la fila pese "
                    "al escritor persistente — el escenario «no se puede "
                    "afirmar» no está montado (detener y reportar, no "
                    "debilitar la aserción)")
        finally:
            probe.close()

        proc = self.dispatch(fake)
        release.set()
        locker.join(timeout=10)
        out = self.envelope(proc, "B2 intento previo innegociable")

        self.assertEqual(
            out["termination"], "blocked",
            msg=f"B2: la fila del intento previo NO PUEDE AFIRMARSE "
                f"(store bloqueado de forma persistente): la terminación "
                f"debe ser 'blocked' ANTES del despacho (fail-closed, "
                f"PD-9/INV-9/INV-10; hoy el chequeo falla ABIERTO): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assert_no_run_invoked(
            fake, "B2 (fail-open permitiría un SEGUNDO worker vivo del "
                  "mismo paquete, INV-10)")
        self.assertFalse(
            out.get("session"),
            msg=f"B2/PD-8: bloqueado ANTES del despacho (sin Popen): "
                f"'session' debe seguir null: {out.get('session')!r}")
        diagnosis = (out.get("diagnosis") or "").lower()
        self.assertIn(
            "no se puede afirmar", diagnosis,
            msg=f"B2: el diagnóstico no declara que NO SE PUEDE AFIRMAR el "
                f"estado del intento previo (espejo de la interpretación "
                f"cerrada de §2.3b; PD-9): {out.get('diagnosis')!r}")
        self.assertIn(
            "intento previo", diagnosis,
            msg=f"B2: el diagnóstico no nombra el INTENTO PREVIO (PD-9): "
                f"{out.get('diagnosis')!r}")
        self.assert_no_receipt_fabricated("B2")


# -------------------------------------------------------------------- B3


class TestB3ServiceWaitAndPreflight(ReviewFixCase):
    """B3 (PD-7 y PD-11 en modo servicio): (a) fila no idle en modo
    servicio → `timeout` al vencer la cota (settle ignorado), sin recibo;
    (b) el preflight de servicio (`service status` retardado) queda acotado
    por el presupuesto restante y el despacho responde dentro de la cota.

    Ambos métodos PUEDEN PASAR hoy (la implementación comparte la rama
    `!standalone` de la espera y ya acota el preflight por
    `min(preflight_timeout, presupuesto restante)`): son COBERTURA de las
    cláusulas nombradas por la enmienda que la review encontró sin focal
    (declarado, no oculto) — un refactor que ponga `mode_effective ==
    "server"` donde hoy hay `!= "standalone"` dejaría (a) en rojo."""

    def test_b3a_service_mode_row_not_idle_times_out_at_cota_ignoring_settle(
            self) -> None:
        """B3 / PD-7: `mode: service` — `service status` informa URL y la
        versión del registro es compatible (§2.3b: despacho SIN flags) —
        con una fila NO idle y `settle_seconds` chico (0,3 s) → `timeout`
        AL VENCER LA COTA (2 s): la espera durable es IGUAL en los tres
        modos efectivos (§2.4) y el asentamiento NO decide en modo
        servicio; SIN recibo; PD-8: la sesión elegida viaja en el
        envelope."""
        fake = self.fake_runtime_rf("b3a-service-no-idle",
                                    variant="exit-row-not-idle")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=RF_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(
            fake, {"mode": "service",
                   "wait": {**RF_FAST_WAIT, "timeout_seconds": 2}})

        started = time.monotonic()
        proc = self.dispatch_service(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "B3a fila no idle en modo servicio")

        # PC-8: la cota (2s) es el sujeto y se conserva; si la preparación
        # la agotó, la clasificación válida es el no despacho — acotado.
        if pc8_preparatory_exhaustion(self, out, fake, "B3a"):
            self.assertLess(elapsed, B3A_UPPER_SECONDS,
                            msg=f"B3a (008-005 T-A, sitio 7, PC-6): el no "
                                f"despacho quedó desacotado "
                                f"({elapsed:.2f}s >= {B3A_UPPER_SECONDS}s)")
            return

        self.assertEqual(
            out["termination"], "timeout",
            msg=f"B3a: fila no idle en MODO SERVICIO: la terminación debe "
                f"ser 'timeout' al vencer la cota — nunca 'unknown' por "
                f"asentamiento (PD-7 dif. enmienda: «como servidor»): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        self.assertGreater(
            elapsed, RF_FAST_WAIT["settle_seconds"] * 3,
            msg=f"B3a: terminó demasiado rápido ({elapsed:.2f}s): parece "
                f"haber usado settle_seconds en modo servicio (PD-7: la "
                f"espera durable sigue hasta la cota, settle ignorado)")
        # 008-005 PC-6 (T-A, sitio 8, review F1): el techo mide el HOST
        # (25 s >= 10x ≈ 2,2 s de la conducta correcta), NO la cota de 2 s;
        # la espera acotada por encima de la cota no es observable hoy:
        # pérdida declarada en deferred-hardening.
        self.assertLess(
            elapsed, B3A_UPPER_SECONDS,
            msg=f"B3a (008-005 T-A, sitio 8, PC-6): el host excedió el "
                f"techo de liveness ({elapsed:.2f}s >= "
                f"{B3A_UPPER_SECONDS}s; el techo mide el host, >= 10x la "
                f"conducta correcta ≈ 2,2 s, no la cota de 2 s); la "
                f"discriminación «acotada por encima de la cota» no es "
                f"observable hoy: pérdida declarada en deferred-hardening")
        chosen = self.chosen_session(fake, "B3a")
        self.assertEqual(
            out.get("session"), chosen,
            msg=f"B3a/PD-8: 'timeout' posterior al arranque de run debe "
                f"llevar la sesión elegida ({chosen!r}): "
                f"{out.get('session')!r}")
        run_argv = self.run_argv(fake, "B3a")
        self.assertNotIn(
            "--server", run_argv,
            msg=f"B3a precondición: el despacho en modo servicio lleva "
                f"--server (§2.3b: sin flags): {run_argv!r}")
        self.assertNotIn(
            "--standalone", run_argv,
            msg=f"B3a precondición: el despacho en modo servicio lleva "
                f"--standalone (INV-10: el servicio corre; nunca "
                f"standalone): {run_argv!r}")
        self.assert_exactly_one_service_status(fake, "B3a")
        self.assert_no_receipt_fabricated("B3a")

    def test_b3b_service_preflight_bounded_responds_within_cota(self) -> None:
        """B3 / PD-11: el preflight de MODO SERVICIO (`service status`)
        retardado (1,2 s) queda acotado por el presupuesto restante
        (timeout = min(preflight_timeout_seconds, presupuesto restante) y
        el despacho completo responde DENTRO de la cota de la interfaz
        (10 s): envelope del adaptador (`completed`), jamás el
        `did not answer within` de la interfaz. Puede PASAR hoy: el
        preflight ya está acotado por min(...) — COBERTURA declarada."""
        fake = self.fake_runtime_rf("b3b-service-preflight-bounded",
                                    variant="succeeded")
        self.scenario_running(fake)
        (fake["dir"] / "service-delay.txt").write_text(
            repr(B3B_SERVICE_DELAY_SECONDS) + "\n", encoding="utf-8")
        self.write_service_registry(fake, version=RF_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(
            fake, {"mode": "service",
                   "wait": {"poll_initial_seconds": 0.05,
                            "poll_max_seconds": 0.2,
                            "settle_seconds": 0.3,
                            "terminate_grace_seconds": 0.2,
                            "preflight_timeout_seconds": 2,
                            "timeout_seconds": 10}})

        started = time.monotonic()
        proc = self.dispatch_service(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "B3b preflight de servicio acotado")

        self.assertEqual(
            out["termination"], "completed",
            msg=f"B3b: preflight de servicio retardado dentro de la cota: "
                f"el despacho no llegó a completed (PD-11 dif. enmienda): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assertGreaterEqual(
            elapsed, B3B_SERVICE_DELAY_SECONDS * 0.9,
            msg=f"B3b precondición: el retardo del preflight de servicio "
                f"no ocurrió ({elapsed:.2f}s < "
                f"{B3B_SERVICE_DELAY_SECONDS}s; fallo de fixture, detener "
                f"y reportar)")
        # 008-005 PC-6 (T-A, sitio 9, review F1): el techo mide el HOST
        # (25 s >= 10x ≈ 1,7 s de la conducta correcta), no la cota de
        # 10 s vigilada; la espera acotada por encima de la cota no es
        # observable hoy: pérdida declarada en deferred-hardening.
        self.assertLess(
            elapsed, B3B_UPPER_SECONDS,
            msg=f"B3b (008-005 T-A, sitio 9, PC-6): el host excedió el "
                f"techo de liveness: {elapsed:.2f}s >= "
                f"{B3B_UPPER_SECONDS}s (el techo mide el host, >= 10x la "
                f"conducta correcta ≈ 1,7 s, no la cota de 10 s; la "
                f"discriminación «acotada por encima de la cota» no es "
                f"observable hoy: pérdida declarada en deferred-hardening)")
        diagnosis = (out.get("diagnosis") or "").lower()
        self.assertNotIn(
            "did not answer within", diagnosis,
            msg=f"B3b: el envelope es el de la interfaz, no el del "
                f"adaptador (PD-11): {out!r}")
        self.assert_exactly_one_service_status(fake, "B3b")
        self.assert_receipt_no_gate()


if __name__ == "__main__":
    unittest.main(verbosity=2)
