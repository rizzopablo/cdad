#!/usr/bin/env python3
"""006-001 T1 RED — Selección de modo, preflight del modo servidor,
procedencia por intento y secretos (PD-1, PD-2, PD-3, PD-4, PD-5).

Contract: docs/specs/006-001-opencode-concurrency-reliability/spec.md
(PD-1..PD-5; INV-2, INV-4, INV-6, INV-9; D-1, D-2, D-5) + plan.md T1
(skills/cdad-cycle/scripts/cdad_delegate_opencode.py). Plan provenance:
docs/specs/006-001-opencode-concurrency-reliability/plan.md
(sha256 0d03d5fef32e79b6502748d75f43c494de1bad955da661d984c45d12b5397c8f).

Superficie observable (NINGUNA lectura de implementación, ningún runtime
real vivo): la interfaz STAGEADA invocada como subproceso (mismo contrato
que el resto de la suite 005-009/005-010), con destino `opencode`, un
proyecto descartable en tmp_path, un `exec-config` de fixture y un BINARIO
FALSO como frontera del proceso. Se reutiliza la base `AdapterCase`
(tests/test_005_009_t2_opencode_adapter.py): proyecto sintético + agentes
derivados publicados + staging de la skill + el binario falso compartido
(señal durable SQLite real chica).

DOS PIEZAS NUEVAS DE FIXTURE declaradas en este fichero (el plan autoriza
solo dos oráculos ajustados en OTROS ficheros, ver más abajo; esta pieza es
propia de este focal, no modifica ningún test existente):

1. `FakeInfoServer` — servidor HTTP de fixture en 127.0.0.1, puerto libre
   (`http.server.ThreadingHTTPServer`, hilo daemon), que sirve `/api/info`
   (spec §2.3): Basic auth opcional (`expected_authorization`) y cuerpo
   JSON con `version` configurable. Registra cada request (path +
   Authorization) para que los focales puedan comprobar si el preflight
   ocurrió. `closed_port_url()` da una URL de loopback sin nada escuchando
   (conexión rechazada, fila 1 de la tabla §2.3).

2. Binario ENVOLTORIO (`WRAPPER_BINARY_SOURCE`, vía
   `Pd600T1Case.fake_runtime_wrapped`) que se antepone al binario falso
   COMPARTIDO (sin tocarlo, salvo el oráculo 2 del plan, ver abajo):
   registra CADA invocación (argv, en orden) en su PROPIO log
   (`wrapper-calls.jsonl`) y delega por `os.execv` al binario falso REAL
   (mismo argv/stdin/env, protocolo intacto). Es necesario porque, tras el
   oráculo 2, el `--version` del preflight YA NO queda en el `calls.jsonl`
   del fake compartido (responde antes de registrar nada): el log del
   envoltorio es la ÚNICA fuente para contar/ordenar invocaciones (PD-2:
   únicas invocaciones `--version` y `run`) y para inyectar, SOLO en la
   invocación cuyo argv trae el subcomando `run` (nunca en el `--version`
   del preflight), un stderr de fixture con un valor sensible configurado
   (PD-5: redacción del stderr del cliente), sin tocar el fake compartido.

ORÁCULOS AJUSTADOS POR EL PLAN (§3, autorizados por el orquestador; se
ajustan en SUS PROPIOS ficheros, no aquí):

  1. tests/test_005_010_t2_load_mode_invocation.py
     (`test_pd4_server_config_uses_server_without_standalone`): sirve
     `/api/info` desde un `FakeInfoServer` de ESTE fichero (importado) en
     vez de `fixture.invalid` (D-1: el preflight rige el modo servidor
     también por compatibilidad; una URL inalcanzable ya no basta). Se
     conserva la aserción de argv.
  2. tests/test_005_009_t2_opencode_adapter.py (el fake compartido):
     `--version` responde ANTES de localizar el paquete, escribir el store
     o registrar la llamada (antes: después). Así un `--version` del
     preflight no crea fila ni cuenta como invocación del rol.

Mapa test → postcondición:

  PD-1 (TestPd1ModeSelectionMatrix, 5 métodos; una matriz, un dispatch por
  método — un segundo dispatch del mismo paquete cambiaría de `prepared` a
  `dispatched` y confundiría el fallo con un problema de fixture):
    test_pd1_mode_server_with_valid_url_dispatches_server_flag_only
    test_pd1_mode_standalone_ignores_configured_server
    test_pd1_mode_server_without_url_blocks_before_dispatch
    test_pd1_invalid_mode_value_blocks_before_dispatch
    test_pd1_invalid_wait_key_blocks_before_dispatch

  PD-2 (TestPd2ServerPreflight, 8 métodos; cada fila de la tabla §2.3 y el
  orden de contraseñas):
    test_pd2_preflight_success_version_then_run_only (también cubre la
      fila `undeclared + url válida -> servidor` de PD-1/§2.2, D-1)
    test_pd2_connection_refused_is_transport_error
    test_pd2_unauthorized_names_both_env_vars
    test_pd2_version_mismatch_names_both_versions
    test_pd2_missing_version_field_blocks
    test_pd2_unparseable_server_version_blocks
    test_pd2_password_order_prefers_first_env_var_when_valid
    test_pd2_password_order_prefers_first_env_var_when_invalid

  PD-3 (TestPd3ProvenanceEveryTermination, 2 métodos; el marcador
  `mode_requested=` en `provenance.runtime` identifica el registro de
  WORKER nuevo frente al registro de la INTERFAZ, que ya existe hoy y que
  `assert_attempt_is_in_ledger` tolera como «registro extra», D-5):
    test_pd3_worker_record_absent_today_on_blocked_standalone
    test_pd3_worker_record_provenance_pairs_on_completed_standalone

  PD-4 (TestPd4SameErrandInServerMode, 1 método: lo que hoy se verifica en
  standalone — sha256 de stdin, --agent/--session/--auto/--model, PWD,
  identidad durable, completed→receive pending — vale también en modo
  servidor):
    test_pd4_same_errand_in_server_mode

  PD-5 (TestPd5NoSecretsInOutputs, 2 métodos):
    test_pd5_no_secrets_in_successful_dispatch_outputs
    test_pd5_client_stderr_url_redacted_before_diagnosis

RED esperado (comportamiento ausente hoy; cada aserción citada es
AssertionError, nunca import/sintaxis — el adaptador YA EXISTE desde
005-009/005-010, que están en GREEN):
  - hoy el adaptador elige modo por la sola presencia de `server` en la
    config (regla vigente de 005-010) y NUNCA hace preflight: toda
    invocación con `server` configurado despacha DIRECTO a `completed`,
    sin ninguna llamada `--version` ni ninguna request a `/api/info`. Por
    eso: PD-1 #1 (mode=standalone con server configurado) falla en el
    argv (usa --server, no --standalone); PD-1 #3/#4/#5 (mode inválido,
    wait.* inválido, server ausente) fallan en la terminación (hoy
    `completed`, se espera `blocked`); TODO PD-2 salvo el camino feliz
    falla en la terminación (hoy `completed`, se espera
    transport-error/blocked) y en el conteo de invocaciones del
    envoltorio (hoy 1, se espera 2: --version y run); PD-2 éxito falla en
    el conteo/orden (hoy 1 invocación, se espera 2) aunque la terminación
    ya sea `completed` hoy.
  - hoy el registro de worker (I8, procedencia con los pares de §2.6:
    `mode_requested=`, `mode_effective=`, `client_version=`,
    `server_version=`, `store=`, `row=`, `store_reads=`,
    `prior_check_reads=`) está reservado a `completed` (D-5): PD-3 en un
    camino `blocked` no encuentra NINGÚN registro nuevo con el marcador
    (hoy cero registros de worker fuera de completed); en `completed` SÍ
    hay un registro de worker hoy, pero con el formato de procedencia
    VIEJO (sin los pares nuevos): ambos métodos fallan por la ausencia
    del marcador/los pares, no por `assert_attempt_is_in_ledger` (ESE
    helper YA tolera el registro extra hoy, D-5).
  - hoy el stderr del cliente que menciona la URL configurada NO se
    redacta (se copia verbatim en el diagnóstico, spec D-1/§2.3 nota
    `:870-876`): PD-5 (redacción) falla porque la URL aparece literal en
    el diagnóstico.
  - PD-4 (mismo encargo en modo servidor) y la mitad "válida" de PD-5
    (sin secretos en el despacho feliz) pueden PASAR hoy: el despacho en
    modo servidor sin preflight ya reutiliza el mismo camino de encargo
    que standalone (--agent/--session/--auto/PWD/identidad durable/
    receive pending) y, como nunca se lee ninguna contraseña, nunca se
    filtra ninguna (nada que leer, nada que filtrar). Declarado en el
    reporte del rol, no oculto.

EXCLUIDO de este focal (alcance de T2, no de T1): la comprobación del
intento previo (§2.7), `timeout` por cota vencida (PD-11), y el conteo
EXACTO de `store_reads`/`prior_check_reads` (el plan asigna «conteo
store_reads en la procedencia de T1» a la ficha de T2); aquí solo se
exige que, cuando el registro de worker exista, esas dos claves sean
texto no vacío con forma `<entero>` o `unknown` (INV-9: desconocido ≠
cero/vacío), nunca el valor exacto.
"""

from __future__ import annotations

import base64
import http.server
import json
import os
import socket
import subprocess
import sys
import threading
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import published_packets
from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import (
    FAKE_BINARY_VERSION,
    AdapterCase,
    durable_session_rows,
)

# El derivado cdad-<rol> del paquete (mismo valor que
# tests/test_005_010_t2_load_mode_invocation.py EXPECTED_ROLE_AGENT; NO se
# importa de ahí para evitar un ciclo: ESE fichero importa `FakeInfoServer`
# de este módulo para su oráculo 1, 006-001 T1 plan §3).
EXPECTED_ROLE_AGENT = "cdad-test-writer"

OPENCODE_PASSWORD_ENV = "OPENCODE_PASSWORD"
OPENCODE_SERVER_PASSWORD_ENV = "OPENCODE_SERVER_PASSWORD"
SENTINEL_PASSWORD = "cdad-006-001-sentinel-password"  # PD-5: nunca debe salir
WRONG_PASSWORD = "cdad-006-001-wrong-password"

# Semver del cliente FALSO (FAKE_BINARY_VERSION = "opencode-fake 1.0.0"):
# el primer token semver (spec §2.3 punto 1) es su último espacio-separado.
MATCHING_CLIENT_SEMVER = FAKE_BINARY_VERSION.rsplit(" ", 1)[-1]
MISMATCHED_SERVER_SEMVER = "9.9.9"
UNPARSEABLE_SERVER_VERSION = "unknown-build"  # sin dígitos: no hay semver

# Valores de espera chicos (spec §2.1, fixture sugerido): cada focal nuevo
# termina en pocos segundos; portabilidad (INV-7): sin valores de host.
FAST_WAIT = {
    "poll_initial_seconds": 0.05,
    "poll_max_seconds": 0.2,
    "settle_seconds": 0.3,
    "terminate_grace_seconds": 0.2,
    "preflight_timeout_seconds": 1,
}

NEVER_INVOKED_TOKENS = ("serve", "service", "reload")  # INV-2

# 008-001 PC-8 (decisión del architect 2026-10-27): la reserva del
# adaptador NO cambia. Tests de CLASIFICACIÓN usan una cota instrumental
# holgada (la cota no es su sujeto); tests cuyo sujeto ES la cota la
# conservan y aceptan, además, la clasificación que PC-8 introduce cuando
# la preparación agota el presupuesto: no despacho con diagnóstico de
# agotamiento preparatorio (sin `run`, sin sesión, sin recibo).
INSTRUMENTAL_COTA_SECONDS = 10
INSTRUMENTAL_WAIT = {**FAST_WAIT, "timeout_seconds": INSTRUMENTAL_COTA_SECONDS}
PC8_EXHAUSTION_MARKERS = ("preparatory exhaustion", "agotamiento preparatorio")


def dispatch_calls(calls: list[dict]) -> list[dict]:
    """Invocaciones de DESPACHO (`run`), con o sin paquete registrado: un
    `run` cuyo paquete el fake no halló (`packet=None`) igual es despacho."""
    return [c for c in calls if "run" in (c.get("argv") or [])]


def pc8_preparatory_exhaustion(case, out: dict, fake: dict, label: str) -> bool:
    """True si el adaptador no despachó por agotamiento preparatorio (PC-8),
    tras verificar el oráculo estricto de ese camino; False si despachó."""
    diagnosis = (out.get("diagnosis") or "").lower()
    if not any(m in diagnosis for m in PC8_EXHAUSTION_MARKERS):
        return False
    case.assertTrue(
        "not launched" in diagnosis or "not dispatched" in diagnosis,
        msg=f"{label} (PC-8): agotamiento sin declarar el no despacho: "
            f"{diagnosis!r}")
    case.assertEqual(
        dispatch_calls(case.binary_calls(fake)), [],
        msg=f"{label} (PC-8): agotamiento preparatorio con `run`")
    case.assertIsNone(out.get("session"),
                      msg=f"{label} (PC-8): agotamiento con sesión: {out!r}")
    case.assertFalse(out.get("delivery_ref"),
                     msg=f"{label} (PC-8): agotamiento con entrega: {out!r}")
    case.assert_no_receipt_fabricated(f"{label} (PC-8)")
    return True



class TestPc8ExhaustionOracle(unittest.TestCase):
    """El oráculo de no despacho (PC-8) rechaza un `run` sin paquete."""

    class _Stub(unittest.TestCase):
        def __init__(self, calls):
            super().__init__()
            self._calls = calls

        def runTest(self):  # noqa: N802
            pass

        def binary_calls(self, fake):
            return self._calls

        def assert_no_receipt_fabricated(self, label):
            pass

    OUT = {"session": None, "delivery_ref": None,
           "diagnosis": "preparatory exhaustion: client was NOT launched"}

    def test_run_without_packet_is_not_accepted_as_no_dispatch(self) -> None:
        stub = self._Stub([{"argv": ["run", "--agent", "x"], "packet": None}])
        with self.assertRaises(AssertionError):
            pc8_preparatory_exhaustion(stub, self.OUT, {}, "oráculo")

    def test_no_run_is_accepted_as_no_dispatch(self) -> None:
        stub = self._Stub([{"argv": ["--version"], "packet": None}])
        self.assertTrue(pc8_preparatory_exhaustion(stub, self.OUT, {}, "oráculo"))


# --------------------------------------------------------- servidor /api/info


class _InfoHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format_: str, *args: object) -> None:  # noqa: D401
        pass  # silencia el log de acceso del fixture

    def do_GET(self) -> None:  # noqa: N802 (API de BaseHTTPRequestHandler)
        server = self.server
        server.requests.append({
            "path": self.path,
            "authorization": self.headers.get("Authorization"),
        })
        if self.path != "/api/info":
            self.send_response(404)
            self.end_headers()
            return
        expected = server.expected_authorization
        if (expected is not None
                and self.headers.get("Authorization") != expected):
            self.send_response(server.unauthorized_status)
            self.end_headers()
            return
        body = server.body_bytes
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class FakeInfoServer:
    """Fixture: servidor HTTP de `/api/info` (spec §2.3) en loopback, con
    puerto libre, Basic auth opcional y `version` configurable."""

    def __init__(self, *, body: bytes = b'{"version": "1.0.0"}',
                 expected_authorization: str | None = None,
                 unauthorized_status: int = 401) -> None:
        self._httpd = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), _InfoHandler)
        self._httpd.daemon_threads = True
        self._httpd.body_bytes = body
        self._httpd.expected_authorization = expected_authorization
        self._httpd.unauthorized_status = unauthorized_status
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


def basic_auth_header(password: str) -> str:
    token = base64.b64encode(
        f"opencode:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def closed_port_url() -> str:
    """URL de loopback de un puerto libre SIN nada escuchando (conexión
    rechazada; fila 1 de la tabla §2.3)."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return f"http://127.0.0.1:{port}"


# ------------------------------------------------- binario envoltorio (argv)


WRAPPER_BINARY_SOURCE = '''#!/usr/bin/env python3
# Binario ENVOLTORIO de fixture (tests/test_006_001_t1_selection.py):
# registra CADA invocación (argv, en orden) en su PROPIO log
# (wrapper-calls.jsonl) y delega por os.execv al binario falso REAL
# compartido (tests/test_005_009_t2_opencode_adapter.py), con el MISMO argv
# (preserva stdin/env/protocolo de transporte intactos). Necesario porque,
# tras el oráculo 2 del plan (--version responde ANTES de localizar el
# paquete, escribir el store o registrar la llamada), el fake compartido
# deja de anotar las invocaciones --version en calls.jsonl: este log es la
# ÚNICA fuente fiable para contar/ordenar invocaciones (PD-2: únicas
# invocaciones --version y run) y, SOLO en la invocación cuyo argv trae el
# subcomando `run` (nunca en el --version del preflight), para inyectar un
# stderr de fixture con un valor sensible configurado (PD-5: redacción del
# stderr del cliente) antes de delegar.
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent         # <fake>/bin
_FAKE = _HERE.parent                            # <fake>
_LOG = _FAKE / "wrapper-calls.jsonl"
_STDERR_INJECT = _FAKE / "stderr-inject.txt"
_REAL_BINARY = _HERE / "opencode-fake-real"

existing = 0
if _LOG.is_file():
    existing = sum(
        1 for line in _LOG.read_text(encoding="utf-8").splitlines()
        if line.strip())

_argv = sys.argv[1:]
entry = {"index": existing, "argv": _argv}
with _LOG.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(entry, sort_keys=True) + "\\n")

if "run" in _argv and _STDERR_INJECT.is_file():
    sys.stderr.write(_STDERR_INJECT.read_text(encoding="utf-8"))
    sys.stderr.flush()
    _STDERR_INJECT.unlink()

os.execv(str(_REAL_BINARY), [str(_REAL_BINARY)] + _argv)
'''


# ---------------------------------------------------------------- fixture base


class Pd600T1Case(AdapterCase):
    """Base de este focal: añade el binario envoltorio, el parcheo de
    `exec-config` (incluida la fusión de `wait.*`) y un `dispatch()` con
    entorno SIEMPRE explícito (nunca hereda `OPENCODE_PASSWORD`/
    `OPENCODE_SERVER_PASSWORD` del host que corre la suite, PD-5)."""

    def fake_runtime_wrapped(self, name: str, *,
                             variant: str = "succeeded") -> dict:
        fake = self.fake_runtime(name, variant=variant)
        binary = fake["binary"]
        real_binary = binary.parent / "opencode-fake-real"
        binary.rename(real_binary)
        binary.write_text(WRAPPER_BINARY_SOURCE, encoding="utf-8")
        binary.chmod(0o755)
        fake["wrapper_calls"] = fake["dir"] / "wrapper-calls.jsonl"
        fake["stderr_inject"] = fake["dir"] / "stderr-inject.txt"
        return fake

    def patch_config(self, fake: dict, patch: dict) -> dict:
        """Reescribe `exec-config.json` (nivel correcto, PD-4): fusiona
        `wait.*` con lo vigente (`timeout_seconds`) en vez de pisarlo."""
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        patch = dict(patch)
        wait_patch = patch.pop("wait", None)
        config.update(patch)
        if wait_patch:
            wait = dict(config.get("wait") or {})
            wait.update(wait_patch)
            config["wait"] = wait
        fake["config"].write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return config

    def wrapper_calls(self, fake: dict) -> list[dict]:
        path = fake["wrapper_calls"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def dispatch(self, fake: dict, *, env_overrides: dict | None = None,
                cwd: Path | None = None) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.pop(OPENCODE_PASSWORD_ENV, None)
        env.pop(OPENCODE_SERVER_PASSWORD_ENV, None)
        if cwd is not None:
            env["PWD"] = str(cwd)
        if env_overrides:
            env.update(env_overrides)
        return subprocess.run(
            [sys.executable, str(self.staged),
             "--project-root", str(self.root),
             "--packet", self.packet_id,
             "--destination", "opencode",
             "--exec-config", str(fake["config"])],
            capture_output=True, text=True, env=env,
            cwd=str(cwd) if cwd is not None else None, timeout=300)

    def _new_dispatch_records(
            self, records_before: dict[str, Path]) -> dict[str, Path]:
        after = dispatch_records(self.root, self.execution_id)
        return {
            stem: path for stem, path in after.items()
            if stem not in records_before
        }

    def worker_records_with_marker(
            self, records_before: dict[str, Path],
            marker: str = "mode_requested=") -> list[dict]:
        """Registros NUEVOS del ledger I8 cuyo `provenance.runtime` lleva
        el marcador de la procedencia nueva de §2.6 (distingue el registro
        de WORKER del registro de la INTERFAZ, que ya existe hoy y que
        `assert_attempt_is_in_ledger` tolera como «registro extra», D-5)."""
        found = []
        for _stem, path in self._new_dispatch_records(records_before).items():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            provenance = data.get("provenance")
            if isinstance(provenance, dict) and marker in str(
                    provenance.get("runtime", "")):
                found.append(data)
        return found


# ----------------------------------------------------------------- PD-1


class TestPd1ModeSelectionMatrix(Pd600T1Case):
    """PD-1: el argv de `run` lleva EXACTAMENTE una de `--server <url>` o
    `--standalone` según la tabla §2.2; un `mode` inválido, `server`
    ausente con `mode: server`, o una clave `wait.*` inválida → `blocked`
    SIN invocar nada. Un dispatch por método (un segundo dispatch del
    mismo paquete pasaría de `prepared` a `dispatched` por razones ajenas
    al modo, confundiendo el fallo con un problema de fixture)."""

    def test_pd1_mode_server_with_valid_url_dispatches_server_flag_only(
            self) -> None:
        """PD-1 (fila `server` + URL válida): el argv lleva `--server
        <url>` y NO `--standalone`. RED hoy: la regla vigente (`server`
        presente ⇒ `--server`) ya produce este argv incluso sin preflight;
        este método puede PASAR hoy (declarado en el reporte, no oculto;
        el camino feliz completo con preflight lo fija PD-2)."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_wrapped("pd1-server-valid")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-1 mode=server url válida")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición de la observación del argv: el despacho no "
                f"llegó a completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        call = self.packet_call(fake, "PD-1 mode=server url válida")
        argv = call["argv"]
        self.assertIn(
            "--server", argv,
            msg=f"mode=server con URL válida: el argv no lleva --server "
                f"(PD-1/§2.2): {argv!r}")
        self.assertEqual(
            argv[argv.index("--server") + 1], info_server.url,
            msg=f"el valor de --server no es la URL declarada por la "
                f"config (PD-1): {argv!r}")
        self.assertNotIn(
            "--standalone", argv,
            msg=f"mode=server con URL válida: el argv lleva TAMBIÉN "
                f"--standalone (PD-1: alternativas excluyentes): {argv!r}")

    def test_pd1_mode_standalone_ignores_configured_server(self) -> None:
        """PD-1 (fila `standalone`): con `mode: standalone` Y `server`
        declarado a la vez, `server` se IGNORA: el argv lleva SOLO
        `--standalone`, nunca `--server`, y jamás se invoca `--version`
        (D-2: solo en modo servidor). RED hoy: la regla vigente elige modo
        por la sola presencia de `server` (ignora cualquier `mode`), así
        que hoy el argv lleva `--server` (y no `--standalone`): falla por
        comportamiento, no por fixture."""
        unused_url = closed_port_url()  # nunca debe marcarse (mode manda)
        fake = self.fake_runtime_wrapped("pd1-standalone-ignores-server")
        self.patch_config(
            fake, {"mode": "standalone", "server": unused_url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-1 mode=standalone con server ignorado")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición de la observación del argv: el despacho no "
                f"llegó a completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        call = self.packet_call(fake, "PD-1 mode=standalone")
        argv = call["argv"]
        self.assertIn(
            "--standalone", argv,
            msg=f"mode=standalone con `server` configurado: el argv NO "
                f"lleva --standalone (PD-1: el mode EXPLÍCITO manda, ya no "
                f"la sola presencia de `server`): {argv!r}")
        self.assertNotIn(
            "--server", argv,
            msg=f"mode=standalone: el argv lleva --server pese al `mode` "
                f"explícito (PD-1: alternativas excluyentes; `server` se "
                f"ignora y se registra, no se invoca): {argv!r}")
        wrapper_calls = self.wrapper_calls(fake)
        self.assertEqual(
            len(wrapper_calls), 1,
            msg=f"mode=standalone: hubo más de UNA invocación del binario "
                f"(D-2: --version solo en modo servidor): {wrapper_calls!r}")
        self.assertNotIn(
            "--version", wrapper_calls[0]["argv"],
            msg=f"mode=standalone: se invocó --version (D-2: solo en modo "
                f"servidor): {wrapper_calls[0]['argv']!r}")

    def test_pd1_mode_server_without_url_blocks_before_dispatch(self) -> None:
        """PD-1 (fila `server` sin `server` en la config): `blocked` SIN
        invocar nada. RED hoy: `mode` no existe en el adaptador vigente;
        sin `server` en la config la regla vigente despacha standalone
        normalmente a `completed` (falla en la terminación, no en la
        ausencia de invocación)."""
        fake = self.fake_runtime_wrapped("pd1-server-no-url")
        self.patch_config(fake, {"mode": "server", "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-1 mode=server sin url")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"mode=server sin `server` en la config: la terminación no "
                f"es `blocked` (PD-1: servidor declarado sin URL válida, "
                f"§2.2): {out['termination']!r}")
        self.assertEqual(
            self.wrapper_calls(fake), [],
            msg=f"mode=server sin URL: se invocó el binario (PD-1: blocked "
                f"SIN invocar nada): {self.wrapper_calls(fake)!r}")

    def test_pd1_invalid_mode_value_blocks_before_dispatch(self) -> None:
        """PD-1 (`mode` fuera del conjunto `server`/`standalone`):
        `blocked` SIN invocar nada, diagnóstico que nombra la clave
        `mode`. RED hoy: la clave `mode` es desconocida para el adaptador
        vigente (tolerancia a claves desconocidas) y, sin `server` en la
        config, despacha standalone a `completed`."""
        fake = self.fake_runtime_wrapped("pd1-invalid-mode")
        self.patch_config(
            fake, {"mode": "bogus-mode-value", "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-1 mode inválido")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"`mode` fuera del conjunto declarado: la terminación no "
                f"es `blocked` antes del despacho (PD-1/§2.1): "
                f"{out['termination']!r}")
        self.assertEqual(
            self.wrapper_calls(fake), [],
            msg=f"`mode` inválido: se invocó el binario (PD-1: blocked SIN "
                f"invocar nada): {self.wrapper_calls(fake)!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "mode", diagnosis.lower(),
            msg=f"`mode` inválido: el diagnóstico no nombra la clave "
                f"`mode` (PD-1/§2.1: diagnóstico que nombra la clave): "
                f"{diagnosis!r}")

    def test_pd1_invalid_wait_key_blocks_before_dispatch(self) -> None:
        """PD-1 (`wait.poll_max_seconds` < `wait.poll_initial_seconds`):
        `blocked` SIN invocar nada, diagnóstico que nombra la clave. RED
        hoy: estas claves `wait.*` no existen para el adaptador vigente
        (solo lee `wait.timeout_seconds`) y, sin `server` en la config,
        despacha standalone a `completed`."""
        fake = self.fake_runtime_wrapped("pd1-invalid-wait-key")
        self.patch_config(
            fake, {"wait": {**FAST_WAIT, "poll_initial_seconds": 0.5,
                            "poll_max_seconds": 0.1}})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-1 wait.* inválido")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"`wait.poll_max_seconds` < `wait.poll_initial_seconds`: la "
                f"terminación no es `blocked` antes del despacho "
                f"(PD-1/§2.1): {out['termination']!r}")
        self.assertEqual(
            self.wrapper_calls(fake), [],
            msg=f"`wait.*` inválido: se invocó el binario (PD-1: blocked "
                f"SIN invocar nada): {self.wrapper_calls(fake)!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "poll_max_seconds", diagnosis,
            msg=f"`wait.*` inválido: el diagnóstico no nombra la clave "
                f"`poll_max_seconds` (PD-1/§2.1): {diagnosis!r}")


# ----------------------------------------------------------------- PD-2


class TestPd2ServerPreflight(Pd600T1Case):
    """PD-2: cada fila de la tabla §2.3 produce la terminación indicada
    SIN invocar `run`; las únicas invocaciones del binario son `--version`
    y `run` (nunca `serve`/`service`/`reload`, INV-2); la contraseña se
    lee en el orden `OPENCODE_PASSWORD` → `OPENCODE_SERVER_PASSWORD`."""

    def test_pd2_preflight_success_version_then_run_only(self) -> None:
        """PD-2 (todo coincide → sigue a `run --server <url>`) + PD-1
        (fila `undeclared` + URL válida → servidor por compatibilidad,
        D-1): el envoltorio registra EXACTAMENTE dos invocaciones, en
        orden: `--version` (sin `run`) y luego `run` (sin `--version`);
        el servidor de fixture recibe EXACTAMENTE una request a
        `/api/info`; ningún argv lleva `serve`/`service`/`reload`
        (INV-2). RED hoy: sin preflight, el envoltorio solo registra UNA
        invocación (el `run` directo); el conteo/orden falla aunque la
        terminación ya sea `completed` hoy."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_wrapped("pd2-preflight-success")
        # `mode` SIN declarar (compatibilidad, D-1): con `server` válido el
        # modo efectivo es servidor y el preflight rige igual.
        self.patch_config(
            fake, {"server": info_server.url, "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-2 preflight éxito")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"preflight con todo coincidente: el despacho no llegó a "
                f"completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        calls = self.wrapper_calls(fake)
        self.assertEqual(
            len(calls), 2,
            msg=f"preflight con éxito: las invocaciones del binario no son "
                f"EXACTAMENTE dos (--version y run, PD-2): {calls!r}")
        self.assertIn(
            "--version", calls[0]["argv"],
            msg=f"la PRIMERA invocación no es --version (PD-2: versión del "
                f"cliente antes de GET /api/info, §2.3): {calls[0]!r}")
        self.assertNotIn(
            "run", calls[0]["argv"],
            msg=f"la invocación --version también porta `run` (PD-2: "
                f"--version NO es despacho): {calls[0]!r}")
        self.assertIn(
            "run", calls[1]["argv"],
            msg=f"la SEGUNDA invocación no es el despacho `run` (PD-2): "
                f"{calls[1]!r}")
        self.assertNotIn(
            "--version", calls[1]["argv"],
            msg=f"la invocación de despacho también lleva --version: "
                f"{calls[1]!r}")
        for call in calls:
            for token in NEVER_INVOKED_TOKENS:
                self.assertNotIn(
                    token, call["argv"],
                    msg=f"una invocación lleva {token!r} (INV-2: CDAD no "
                        f"arranca/recarga/detiene servidores): {call!r}")

        requests = info_server.requests
        self.assertEqual(
            len(requests), 1,
            msg=f"el preflight no hizo EXACTAMENTE una request a "
                f"/api/info: {requests!r}")
        self.assertEqual(requests[0]["path"], "/api/info")

    def test_pd2_connection_refused_is_transport_error(self) -> None:
        """PD-2 (fila 1: conexión rechazada): `transport-error`, SIN
        invocar `run`. RED hoy: sin preflight, la regla vigente despacha
        `run --server <url>` directo (el fake no comprueba
        alcanzabilidad): `completed`, no `transport-error`."""
        unreachable_url = closed_port_url()
        fake = self.fake_runtime_wrapped("pd2-connection-refused")
        self.patch_config(
            fake, {"mode": "server", "server": unreachable_url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-2 conexión rechazada")
        self.assertEqual(
            out["termination"], "transport-error",
            msg=f"servidor configurado inalcanzable: la terminación no es "
                f"`transport-error` (PD-2, fila 1 de §2.3): "
                f"{out['termination']!r}")
        self.assertFalse(
            any("run" in call["argv"] for call in self.wrapper_calls(fake)),
            msg=f"conexión rechazada: se invocó `run` pese al fallo del "
                f"preflight (PD-2: sin invocar run): "
                f"{self.wrapper_calls(fake)!r}")

    def test_pd2_unauthorized_names_both_env_vars(self) -> None:
        """PD-2 (fila 2: 401/403): `blocked`, diagnóstico que nombra las
        DOS variables de entorno (nunca su valor), SIN invocar `run`. RED
        hoy: sin preflight, `completed` directo."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode(),
            expected_authorization=basic_auth_header(SENTINEL_PASSWORD))
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped("pd2-unauthorized")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)  # sin ninguna contraseña en el entorno
        out = self.envelope(proc, "PD-2 401 sin credencial")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"servidor exige credencial y ninguna fue enviada: la "
                f"terminación no es `blocked` (PD-2, fila 2 de §2.3): "
                f"{out['termination']!r}")
        diagnosis = out.get("diagnosis") or ""
        for var in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
            self.assertIn(
                var, diagnosis,
                msg=f"401/403: el diagnóstico no nombra {var!r} (PD-2: "
                    f"nombra las dos variables de entorno): {diagnosis!r}")
        self.assertNotIn(
            SENTINEL_PASSWORD, diagnosis,
            msg="401/403: el diagnóstico menciona un valor de contraseña "
                "(PD-2/PD-5: nunca el valor)")
        self.assertFalse(
            any("run" in call["argv"] for call in self.wrapper_calls(fake)),
            msg="401 sin credencial: se invocó `run` pese al fallo del "
                "preflight")

    def test_pd2_version_mismatch_names_both_versions(self) -> None:
        """PD-2 (fila 4: `version` del servidor ≠ versión del cliente):
        `blocked`, diagnóstico que nombra AMBAS versiones, SIN invocar
        `run`. RED hoy: sin preflight, `completed` directo."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MISMATCHED_SERVER_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped("pd2-version-mismatch")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-2 version mismatch")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"version del servidor distinta de la del cliente: la "
                f"terminación no es `blocked` (PD-2, fila 4 de §2.3): "
                f"{out['termination']!r}")
        diagnosis = out.get("diagnosis") or ""
        for version in (MATCHING_CLIENT_SEMVER, MISMATCHED_SERVER_SEMVER):
            self.assertIn(
                version, diagnosis,
                msg=f"version mismatch: el diagnóstico no nombra la "
                    f"versión {version!r} (PD-2: nombra las dos "
                    f"versiones): {diagnosis!r}")
        self.assertFalse(
            any("run" in call["argv"] for call in self.wrapper_calls(fake)),
            msg="version mismatch: se invocó `run` pese al fallo del "
                "preflight")

    def test_pd2_missing_version_field_blocks(self) -> None:
        """PD-2 (fila 3: respuesta sin `version`): `blocked`, diagnóstico
        no vacío, SIN invocar `run`. RED hoy: sin preflight, `completed`
        directo."""
        info_server = FakeInfoServer(body=json.dumps({"ok": True}).encode())
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped("pd2-missing-version-field")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-2 sin version")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"respuesta de /api/info sin `version`: la terminación no "
                f"es `blocked` (PD-2, fila 3 de §2.3): "
                f"{out['termination']!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertTrue(
            diagnosis.strip(),
            msg="sin `version` en la respuesta: diagnóstico vacío (PD-2: "
                "diagnóstico accionable)")
        self.assertFalse(
            any("run" in call["argv"] for call in self.wrapper_calls(fake)),
            msg="sin `version`: se invocó `run` pese al fallo del "
                "preflight")

    def test_pd2_unparseable_server_version_blocks(self) -> None:
        """PD-2 (fila 5: versión del servidor no parseable): `blocked`,
        diagnóstico no vacío, SIN invocar `run`. RED hoy: sin preflight,
        `completed` directo."""
        info_server = FakeInfoServer(
            body=json.dumps(
                {"version": UNPARSEABLE_SERVER_VERSION}).encode())
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped("pd2-unparseable-version")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-2 version no parseable")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"version del servidor no parseable: la terminación no es "
                f"`blocked` (PD-2, fila 5 de §2.3): {out['termination']!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertTrue(
            diagnosis.strip(),
            msg="version no parseable: diagnóstico vacío (PD-2: "
                "diagnóstico accionable)")
        self.assertFalse(
            any("run" in call["argv"] for call in self.wrapper_calls(fake)),
            msg="version no parseable: se invocó `run` pese al fallo del "
                "preflight")

    def test_pd2_password_order_prefers_first_env_var_when_valid(
            self) -> None:
        """PD-2 (orden de contraseñas): con `OPENCODE_PASSWORD` CORRECTA y
        `OPENCODE_SERVER_PASSWORD` distinta (incorrecta), el preflight usa
        la PRIMERA y el despacho llega a `completed`. RED: puede PASAR
        hoy (sin preflight nunca se envía ninguna, y el despacho directo
        ya llega a completed; declarado, no oculto). El complemento
        (primera var incorrecta) es el método siguiente."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode(),
            expected_authorization=basic_auth_header(SENTINEL_PASSWORD))
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_wrapped("pd2-password-order-valid")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake, env_overrides={
            OPENCODE_PASSWORD_ENV: SENTINEL_PASSWORD,
            OPENCODE_SERVER_PASSWORD_ENV: WRONG_PASSWORD,
        })
        out = self.envelope(proc, "PD-2 orden de contraseñas (primera OK)")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"OPENCODE_PASSWORD correcta (primera en el orden): el "
                f"despacho no llegó a completed: {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")

    def test_pd2_password_order_prefers_first_env_var_when_invalid(
            self) -> None:
        """PD-2 (orden de contraseñas, complemento): con
        `OPENCODE_PASSWORD` INCORRECTA y `OPENCODE_SERVER_PASSWORD`
        correcta, el preflight usa la PRIMERA (incorrecta) y el servidor
        la rechaza: `blocked`, diagnóstico que nombra las dos variables.
        Junto con el método anterior prueba la precedencia (si el
        adaptador usara la segunda, este caso completaría en vez de
        bloquear). RED hoy: sin preflight, `completed` directo (nunca se
        envía ninguna contraseña)."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode(),
            expected_authorization=basic_auth_header(SENTINEL_PASSWORD))
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped("pd2-password-order-invalid")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})

        proc = self.dispatch(fake, env_overrides={
            OPENCODE_PASSWORD_ENV: WRONG_PASSWORD,
            OPENCODE_SERVER_PASSWORD_ENV: SENTINEL_PASSWORD,
        })
        out = self.envelope(
            proc, "PD-2 orden de contraseñas (primera incorrecta)")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"OPENCODE_PASSWORD incorrecta (debe ganar sobre "
                f"OPENCODE_SERVER_PASSWORD correcta, PD-2: orden "
                f"OPENCODE_PASSWORD → OPENCODE_SERVER_PASSWORD): la "
                f"terminación no es `blocked`: {out['termination']!r}")
        diagnosis = out.get("diagnosis") or ""
        for var in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
            self.assertIn(
                var, diagnosis,
                msg=f"orden de contraseñas: el diagnóstico no nombra "
                    f"{var!r}: {diagnosis!r}")


# ----------------------------------------------------------------- PD-3


class TestPd3ProvenanceEveryTermination(Pd600T1Case):
    """PD-3: cada camino deja un registro de WORKER con las claves I8
    cerradas y la procedencia de §2.6 (pares `clave=valor`). El marcador
    `mode_requested=` identifica el registro NUEVO frente al registro de
    la INTERFAZ (que ya existe hoy para TODO camino y que
    `assert_attempt_is_in_ledger` tolera como «registro extra», D-5)."""

    def test_pd3_worker_record_absent_today_on_blocked_standalone(
            self) -> None:
        """PD-3 (camino NO completado): con la variante `failed`
        (standalone; terminación `blocked` ya correcta HOY, GREEN de
        005-009/005-010 — aísla la aserción de procedencia de cualquier
        ruido de terminación), debe existir un registro de WORKER nuevo
        con la forma I8 cerrada y `provenance.runtime`/`provenance.session`
        con los pares de §2.6. RED hoy: el registro de worker está
        reservado a `completed` (D-5): CERO registros nuevos llevan el
        marcador `mode_requested=` en un camino `blocked`."""
        fake = self.fake_runtime_wrapped("pd3-blocked-standalone",
                                        variant="failed")
        self.patch_config(fake, {"mode": "standalone", "wait": INSTRUMENTAL_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-3 blocked standalone")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"precondición (fixture, ya GREEN hoy): variante `failed` "
                f"en standalone no fue `blocked`: {out['termination']!r}")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="camino `blocked` (posterior al despacho): ningún registro "
                "NUEVO del ledger I8 lleva la procedencia nueva de §2.6 "
                "(PD-3: registro de worker en TODA terminación, incluida "
                "`blocked`; D-5: hoy reservado a `completed`)")
        self._assert_worker_record_shape(worker_records[0])

    def test_pd3_worker_record_provenance_pairs_on_completed_standalone(
            self) -> None:
        """PD-3 (camino completado): con la variante `succeeded`
        (standalone), `assert_attempt_is_in_ledger` YA tolera hoy el
        registro extra de worker (D-5, verificado aquí: no es la
        aserción que falla). RED: el registro de worker existente hoy NO
        lleva el formato de procedencia nuevo (sin los pares de §2.6):
        ningún registro nuevo lleva el marcador `mode_requested=`."""
        fake = self.fake_runtime_wrapped("pd3-completed-standalone",
                                        variant="succeeded")
        self.patch_config(fake, {"mode": "standalone", "wait": INSTRUMENTAL_WAIT})
        self.assert_derived_agents_published()
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-3 completed standalone")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición (fixture, ya GREEN hoy): variante "
                f"`succeeded` en standalone no fue `completed`: "
                f"{out['termination']!r}")

        # D-5 (tolerancia a registros extra): YA pasa hoy; lo registramos
        # como evidencia, no como el punto RED de este método.
        self.assert_attempt_is_in_ledger(out, records_before)

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="camino `completed`: ningún registro NUEVO del ledger I8 "
                "lleva la procedencia nueva de §2.6 (`mode_requested=`): "
                "el registro de worker vigente usa el formato de "
                "procedencia VIEJO (PD-3: formato nuevo exigido)")
        self._assert_worker_record_shape(worker_records[0])

    def _assert_worker_record_shape(self, data: dict) -> None:
        self.assertEqual(
            set(data), I8_RECORD_KEYS,
            msg=f"la forma del registro de worker no es la cerrada I8 "
                f"(D-5: mismo esquema que la interfaz): {sorted(data)}")
        provenance = data["provenance"]
        runtime_prov = str(provenance.get("runtime", ""))
        session_prov = str(provenance.get("session", ""))
        for pair in ("mode_requested=", "mode_effective=",
                     "client_version=", "server_version="):
            self.assertIn(
                pair, runtime_prov,
                msg=f"provenance.runtime no lleva el par {pair!r} (§2.6): "
                    f"{runtime_prov!r}")
        for pair in ("store=", "row=", "store_reads=", "prior_check_reads="):
            self.assertIn(
                pair, session_prov,
                msg=f"provenance.session no lleva el par {pair!r} (§2.6): "
                    f"{session_prov!r}")
        # INV-9 (desconocido ≠ cero/vacío): si están, store_reads/
        # prior_check_reads son un entero en texto o el literal `unknown`
        # (el CONTEO exacto es alcance de T2, no se fija aquí).
        for key in ("store_reads", "prior_check_reads"):
            value = session_prov.split(f"{key}=", 1)[1].split(";")[0].strip()
            self.assertTrue(
                value == "unknown" or value.isdigit(),
                msg=f"{key} de provenance.session no es un entero ni "
                    f"`unknown` (INV-9): {value!r} (de {session_prov!r})")


# ----------------------------------------------------------------- PD-4


class TestPd4SameErrandInServerMode(Pd600T1Case):
    """PD-4: en modo servidor se cumple lo mismo que hoy se verifica en
    standalone (sha256 de stdin, --agent/--session/--model/--auto, PWD,
    identidad durable, `completed` → receive `pending`)."""

    def test_pd4_same_errand_in_server_mode(self) -> None:
        """PD-4: con preflight exitoso (versión coincidente), el despacho
        en modo servidor transporta el MISMO encargo que standalone. RED:
        la mayoría de estas aserciones pueden PASAR hoy (el despacho en
        modo servidor sin preflight ya reutiliza el mismo camino de
        encargo que standalone; declarado, no oculto); si el adaptador
        vigente no declara `--model` en el argv (ninguna prueba de la
        suite lo exige hoy), ESA aserción puntual falla por
        comportamiento ausente.

        A-1 (006-003 U4/D3, reemplazo declarado): el `model` de la
        exec-config dejó de ser la fuente del `--model` del argv; sin
        entrada en la config de delegación NO hay `--model` (sin
        fallback). El bloque que exigía `--model == config["model"]` se
        reemplaza por esa ausencia, con la config de delegación redirigida
        a un directorio vacío del tempdir (nunca la del host)."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_wrapped("pd4-server-errand")
        config = self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        xdg_home = Path(self._tmp) / "xdg-config-u4"
        xdg_home.mkdir(parents=True, exist_ok=True)
        proc = self.dispatch(
            fake, env_overrides={"XDG_CONFIG_HOME": str(xdg_home)})
        out = self.envelope(proc, "PD-4 encargo en modo servidor")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición de las aserciones del encargo: el despacho "
                f"no llegó a completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        call = self.packet_call(fake, "PD-4 encargo en modo servidor")
        argv = call["argv"]

        # sha256 de stdin == PACKET.md publicado.
        published = published_packets(self.root)[self.packet_id]
        import hashlib
        expected_sha = hashlib.sha256(published).hexdigest()
        self.assertEqual(
            call["packet"]["sha256"], expected_sha,
            msg="el paquete transportado en modo servidor no es "
                "byte-idéntico al PACKET.md publicado (PD-4)")

        # --agent cdad-<role>.
        self.assertIn("--agent", argv, msg=f"sin --agent en argv: {argv!r}")
        self.assertEqual(
            argv[argv.index("--agent") + 1], EXPECTED_ROLE_AGENT,
            msg=f"--agent no nombra {EXPECTED_ROLE_AGENT!r} (PD-4): "
                f"{argv!r}")

        # --session <elegida> == la que el binario falso reportó escrita.
        self.assertIn(
            "--session", argv, msg=f"sin --session en argv: {argv!r}")
        session_value = argv[argv.index("--session") + 1]
        self.assertEqual(
            session_value, call.get("session_id_written"),
            msg="la identidad de sesión del argv no es la que el cliente "
                "reportó haber escrito (PD-1/PD-4)")
        self.assertEqual(
            out["session"], session_value,
            msg="la sesión declarada por el envelope no es la del argv "
                "(PD-4/PD-8)")

        # A-1 (006-003 U4/D3, reemplazo declarado): el `model` de la
        # exec-config dejó de ser la fuente del `--model` del argv; sin
        # entrada en la config de delegación (redirigida a un directorio
        # vacío) NO hay `--model` (sin fallback). Antes este bloque exigía
        # `argv[--model] == config["model"]`.
        self.assertNotIn(
            "--model", argv,
            msg=f"el argv lleva `--model` pese a que U4/D3 retiró el `model` "
                f"de la exec-config como fuente y no hay entrada de "
                f"delegación: {argv!r}")

        # --auto según la config (por defecto activado).
        self.assertIn(
            "--auto", argv,
            msg=f"sin `auto: false` en la config, el argv no lleva --auto "
                f"(PD-4): {argv!r}")

        # alternativas de modo: exactamente --server, nunca --standalone.
        self.assertIn("--server", argv)
        self.assertNotIn("--standalone", argv)

        # PWD == raíz del proyecto.
        self.assertEqual(
            call.get("pwd"), str(self.root),
            msg=f"PWD de la invocación no es la raíz del proyecto (PD-4): "
                f"{call.get('pwd')!r} != {str(self.root)!r}")

        # Identidad durable verificada desde la fila.
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("agent") for row in rows], [EXPECTED_ROLE_AGENT],
            msg=f"la fila durable no declara la identidad cdad del rol "
                f"(PD-4/PD-3 de 005-010): "
                f"{[row.get('agent') for row in rows]!r}")

        # completed → receive con semantic_status pending.
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()
        self.assert_attempt_is_in_ledger(out, records_before)


# ----------------------------------------------------------------- PD-5


class TestPd5NoSecretsInOutputs(Pd600T1Case):
    """PD-5: con una contraseña centinela en el entorno, ni ella ni la
    URL configurada aparecen en envelope, diagnóstico, registros I8,
    stderr del adaptador ni recibo; la URL aparece SOLO en el argv de
    `run`; la contraseña NUNCA va en argv; un stderr del cliente que
    mencione la URL se redacta antes del diagnóstico."""

    def test_pd5_no_secrets_in_successful_dispatch_outputs(self) -> None:
        """PD-5 (despacho feliz): ni la contraseña centinela ni la URL
        configurada aparecen fuera del argv de `run` (donde la URL SÍ
        debe aparecer, exactamente una vez); ningún registro I8 nuevo ni
        el recibo las contienen. RED: puede PASAR hoy en su mayoría (sin
        preflight, la contraseña nunca se lee ni se envía: nada que
        filtrar); declarado, no oculto."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode(),
            expected_authorization=basic_auth_header(SENTINEL_PASSWORD))
        self.addCleanup(info_server.stop)
        self.assert_derived_agents_published()
        fake = self.fake_runtime_wrapped("pd5-no-secrets")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch(
            fake, env_overrides={OPENCODE_PASSWORD_ENV: SENTINEL_PASSWORD})
        out = self.envelope(proc, "PD-5 despacho feliz")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición: el despacho no llegó a completed: "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")

        self.assertNotIn(SENTINEL_PASSWORD, proc.stdout)
        self.assertNotIn(SENTINEL_PASSWORD, proc.stderr)
        self.assertNotIn(
            info_server.url, proc.stdout,
            msg="la URL configurada aparece en el stdout del envelope "
                "(PD-5: solo debe aparecer en el argv de run)")

        diagnosis = out.get("diagnosis") or ""
        self.assertNotIn(SENTINEL_PASSWORD, diagnosis)
        self.assertNotIn(info_server.url, diagnosis)

        for _stem, path in self._new_dispatch_records(
                records_before).items():
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                SENTINEL_PASSWORD, text,
                msg=f"el registro I8 {path} contiene la contraseña "
                    f"centinela (PD-5)")
            self.assertNotIn(
                info_server.url, text,
                msg=f"el registro I8 {path} contiene la URL configurada "
                    f"(PD-5)")

        receipt_path = self.results_base() / "receipt.json"
        if receipt_path.is_file():
            receipt_text = receipt_path.read_text(encoding="utf-8")
            self.assertNotIn(SENTINEL_PASSWORD, receipt_text)
            self.assertNotIn(info_server.url, receipt_text)

        call = self.packet_call(fake, "PD-5 despacho feliz")
        argv = call["argv"]
        self.assertNotIn(
            SENTINEL_PASSWORD, argv,
            msg=f"la contraseña aparece en el argv (PD-5: nunca en argv): "
                f"{argv!r}")
        url_occurrences = sum(1 for token in argv if token == info_server.url)
        self.assertEqual(
            url_occurrences, 1,
            msg=f"la URL no aparece EXACTAMENTE una vez en el argv (PD-5): "
                f"{argv!r}")

        for wrapper_call in self.wrapper_calls(fake):
            self.assertNotIn(
                SENTINEL_PASSWORD, wrapper_call["argv"],
                msg=f"la contraseña aparece en una invocación del binario: "
                    f"{wrapper_call!r}")

    def test_pd5_client_stderr_url_redacted_before_diagnosis(self) -> None:
        """PD-5 (redacción): un stderr del cliente que menciona la URL
        configurada (variante `transport-error`, tras un preflight
        exitoso) se redacta a «servidor configurado» ANTES de entrar al
        diagnóstico: la URL NUNCA aparece literal en `diagnosis`. RED
        hoy: el adaptador vigente copia el stderr del cliente verbatim
        (hasta 300 caracteres) en el diagnóstico, SIN redactar nada: la
        URL aparece literal."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_wrapped(
            "pd5-stderr-redaction", variant="transport-error")
        self.patch_config(
            fake, {"mode": "server", "server": info_server.url,
                   "wait": INSTRUMENTAL_WAIT})
        # Inyectado SOLO en la invocación de `run` (nunca en --version, el
        # envoltorio lo gatea por el argv): simula un cliente real que
        # imprime la URL configurada en su propio error de conexión.
        fake["stderr_inject"].write_text(
            f"opencode: connection to {info_server.url} refused "
            "(fixture inyectado)\n",
            encoding="utf-8")

        proc = self.dispatch(fake)
        out = self.envelope(proc, "PD-5 redacción de stderr")
        self.assertEqual(
            out["termination"], "transport-error",
            msg=f"precondición (variante transport-error): la terminación "
                f"no es transport-error: {out['termination']!r}")

        diagnosis = out.get("diagnosis") or ""
        self.assertNotIn(
            info_server.url, diagnosis,
            msg=f"la URL configurada aparece LITERAL en el diagnóstico "
                f"(PD-5: debe redactarse a «servidor configurado» antes "
                f"de entrar al diagnóstico): {diagnosis!r}")
        self.assertIn(
            "servidor configurado", diagnosis.lower(),
            msg=f"el diagnóstico no lleva la redacción «servidor "
                f"configurado» (PD-5): {diagnosis!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
