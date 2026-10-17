#!/usr/bin/env python3
"""006-001 T3 RED — Concurrencia útil con fixture (PD-6 pierna (a); INV-2,
INV-6, INV-7, INV-10; D-7, D-8).

Contract: docs/specs/006-001-opencode-concurrency-reliability/spec.md v2
(§2.1, §2.2, §2.3, §2.3b, §2.6, §3 PD-6; §5 pierna (a)) + plan v2, ficha T3
(docs/specs/006-001-opencode-concurrency-reliability/plan.md). Plan
provenance: plan.md (sha256 2726744566f58af88540f03b6bb1cec6a73534c6adb43b
fbf466206278a1ea72).

Superficie observable: DOS proyectos sintéticos descartables (cada uno con
su paquete preparado, su agents-src y su staging de la skill — el segundo se
construye con la misma maquinaria de fixture instanciada como objeto, sin
modificar los focales de T1/T1b/T2) despachando EN PARALELO contra el MISMO
store SQLite descartable y el MISMO servidor de fixture `/api/info`
(loopback, puerto libre). Binario FALSO PROPIO de este focal
(`T3_FAKE_BINARY_SOURCE`, el plan §3 oráculo 4 asigna un fake propio a T3):
responde `--version` antes que nada, responde `service status` según el
escenario de fixture, y en `run` localiza el paquete, EXTRAE el NONCE del
encargo, escribe una fila `session_v2` CON id único por nonce en el store
COMPARTIDO (CREATE TABLE IF NOT EXISTS + INSERT transaccional real: las dos
escrituras concurrentes se serializan por SQLite — PD-6 (a): escrituras
transaccionales reales como regresión permanente), registra la invocación
con PWD/nonce/sesión/hash-del-store-post-commit y emite el texto final con
el nonce. Valores de espera CHICOS (spec §2.1, fixture sugerido): el focal
entero corre en ≤ 30 s.

PIERNA REAL (no aquí): PD-6 exige además el recorrido REAL en modo servidor
(spec §5) y el recorrido REAL en modo servicio contra el servicio VIVO
(spec §5.5) — tests/test_006_001_t3_integration.py (opt-in por entorno; la
corre el orquestador con la credencial del operador). El fixture NO basta
para aceptar PD-6 (D-8): una omisión por falta de credencial no es un pase.

Mapa test → postcondición:

  1  test_pd6_two_concurrent_server_mode_dispatches_complete_
       without_cross_correlation
       PD-6 (topología servidor, pierna (a) fixture): dos delegaciones
       concurrentes desde dos proyectos descartables contra el mismo store
       y el mismo servidor de fixture; las dos terminan `completed`; el
       recibo de cada una lleva su propia sesión (sesiones distintas,
       correlación sin cruces); `session_v2.directory` de cada fila es su
       proyecto; cada encargo pide un nonce propio y el nonce de A aparece
       solo en los resultados de A (y viceversa), incluida la fila durable
       y los archivos cambiados de cada proyecto (dentro de su `.cdad/` y
       `docs/.cdad-state.json`); el adaptador NO escribe el store (el hash
       final del store es uno de los hashes post-commit registrados por el
       fake: cualquier escritura del adaptador crearía un estado no
       registrado); procedencia POR INTENTO (un registro de worker por
       proyecto con los pares de §2.6 y `store_reads`/`prior_check_reads`
       enteros). INV-6: la URL del servidor solo en el argv de `run
       --server` (nunca en envelope, diagnóstico, registros ni recibo).
       D-7/D-8: el encargo es idéntico al de los modos ya verificados; la
       topología servidor es la preferida.

  2  test_pd6_two_concurrent_service_mode_dispatches_complete_
       without_cross_correlation
       PD-6 (enmienda: modo `service`, despacho SIN flags): mismo
       escenario en modo servicio — fake de `service status` (URL) y
       registro del servicio de fixture (D-11) con versión compatible; las
       dos terminan `completed` con sesión y nonce propios, sin cruces; el
       argv de `run` no lleva `--server` ni `--standalone`; `service
       status` se invoca EXACTAMENTE una vez por despacho; la única
       invocación de `service` es `status` y NINGÚN argv lleva `serve` ni
       `reload` ni gestión (INV-2/INV-10); procedencia por intento con
       `mode_requested=service; mode_effective=service; dispatch_flags=
       none; service_status=running; fallback=none` y `server_version=` de
       la versión del servicio (D-11). INV-6: ni la contraseña centinela
       del registro del servicio ni la URL del servicio aparecen en
       envelope, diagnóstico, registros ni recibo.

RED — HONESTIDAD DECLARADA: T1, T1b y T2 están en GREEN (ddba831): los
comportamientos que este focal observationa (selección de modo, preflight,
procedencia, espera) ya existen. Por eso los DOS tests pueden PASAR hoy por
el GREEN previo; se declara explícitamente y queda registrado con la PD que
cada uno cubre. El valor del RED de T3 es el ORÁCULO de integración: si el
comportamiento concurrente faltara o se rompiera (cruce de correlación,
escritura del adaptador al store, fallback no contable, gestión del
servicio), la falla se manifiesta como AssertionError de CONTRATO
(terminación, sesiones, nonces, hashes del store, pares de procedencia) —
nunca por import/sintaxis/fixture: el fake, los proyectos y el store son
piezas de este fichero y su precondición se assertiona aparte.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path

from test_005_009_t1_interface import dispatch_records
from test_005_009_t2_opencode_adapter import (
    durable_last_assistant_text,
    durable_session_rows,
)
from test_006_001_t1_selection import (
    FAST_WAIT,
    FakeInfoServer,
    Pd600T1Case,
    closed_port_url,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Binario falso PROPIO de T3 (plan §3, oráculo 4): versión con semver
# conocido para el gate de /api/info y para el registro del servicio D-11.
T3_FAKE_VERSION = "opencode-t3-fake 1.0.0"
T3_CLIENT_SEMVER = T3_FAKE_VERSION.rsplit(" ", 1)[-1]
T3_MODEL = "fixture-opencode-t3-model"
EXPECTED_ROLE_AGENT = "cdad-test-writer"

# Espera chota pero real: cota > WAIT_RESERVE_SECONDS (1.0 s, spec §2.1) con
# margen para DOS despachos concurrentes bajo carga de suite (el flake de
# cota 2 s de T2 bajo carga quedó declarado como DT-7: aquí 4 s).
T3_WAIT_TIMEOUT_SECONDS = 4

# NONCE del encargo (formato cerrado que el fake extrae del paquete).
NONCE_PREFIX = "CDAD-T3-NONCE-"

# PD-5/INV-6: contraseña centinela que vive SOLO en el registro del
# servicio de fixture (clave `password` del esquema D-11). Nunca debe
# aparecer en argv, envelope, diagnóstico, registros I8, stderr ni recibo.
T3_SERVICE_SENTINEL_PASSWORD = "cdad-006-001-t3-service-registry-password"

# INV-2: tokens de gestión PROHIBIDOS en cualquier argv del binario.
T3_FORBIDDEN_ARGV_TOKENS = ("serve", "reload")


def _prov_value(provenance_text: str, key: str):
    """Valor del par `clave=valor` (pares `; `-separados, spec §2.6) en un
    texto de procedencia, o None si el par no está."""
    for part in str(provenance_text).split(";"):
        part = part.strip()
        if part.startswith(key + "="):
            return part[len(key) + 1:]
    return None


# ------------------------------------------------- binario falso propio T3


T3_FAKE_BINARY_SOURCE = r'''#!/usr/bin/env python3
# Binario FALSO de fixture (tests/test_006_001_t3_concurrency.py — fake
# PROPIO de T3, plan §3 oráculo 4). NO es producto. Protocolo:
#   --version       -> imprime la versión de fixture y sale 0 ANTES de
#                      localizar paquete, escribir store o registrar
#                      (oráculo 2 de 006-001 T1: el preflight no crea fila
#                      ni cuenta como invocación del rol).
#   service status  -> imprime el stdout del escenario de fixture
#                      (<fake>/service-scenario.json) y sale con su rc;
#                      nunca gestiona nada (solo lectura, INV-2).
#   run             -> localiza el paquete (argv-file/env/stdin), EXTRAe el
#                      nonce del encargo (CDAD-T3-NONCE-<12 hex>), escribe
#                      una fila session_v2 con id ÚNICO por nonce en el
#                      store COMPARTIDO (ruta `sessions_db` de
#                      <fake>/exec-config.json) con INSERT transaccional
#                      (CREATE TABLE IF NOT EXISTS + INSERT; las escrituras
#                      concurrentes se serializan por SQLite: PD-6 (a)),
#                      registra la invocación (argv, PWD, nonce, sesión,
#                      hash del store POST-commit) y emite el texto final
#                      con el nonce. La columna directory lleva la env PWD
#                      (como OpenCode real), no el cwd del proceso.
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent        # <fake>/bin
_FAKE = _HERE.parent                           # <fake>
_LOG = _FAKE / "t3-calls.jsonl"
_SCENARIO = _FAKE / "service-scenario.json"
_VERSION_LINE = (_FAKE / "version.txt").read_text(encoding="utf-8").strip()
_MARKER = b"---cdad-packet-json"
_NONCE_RE = re.compile(r"CDAD-T3-NONCE-[0-9a-f]{12}")

argv = sys.argv[1:]


def _append_call(entry):
    with _LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


if argv[:1] == ["--version"]:
    sys.stdout.write(_VERSION_LINE + "\n")
    sys.stdout.flush()
    sys.exit(0)

if argv[:2] == ["service", "status"]:
    _append_call({"argv": argv, "pwd": os.environ.get("PWD"),
                  "kind": "service-status"})
    if not _SCENARIO.is_file():
        sys.stderr.write("fixture t3: service status sin escenario\n")
        sys.exit(3)
    scenario = json.loads(_SCENARIO.read_text(encoding="utf-8"))
    sys.stdout.write(scenario.get("stdout", ""))
    sys.stdout.flush()
    sys.exit(int(scenario.get("rc", 0)))


def _locate_packet():
    for token in argv:
        candidate = Path(token)
        if candidate.is_file():
            data = candidate.read_bytes()
            if data.lstrip().startswith(_MARKER):
                return data
    for key in sorted(os.environ):
        if any(part in key.upper()
               for part in ("PACKET", "CDAD", "DELIVER")):
            candidate = Path(os.environ[key])
            if candidate.is_file():
                data = candidate.read_bytes()
                if data.lstrip().startswith(_MARKER):
                    return data
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read()
            if data.lstrip().startswith(_MARKER.decode("utf-8")):
                return data.encode("utf-8")
    except Exception:
        pass
    return None


def _argv_option(name):
    for index, token in enumerate(argv):
        if token == name and index + 1 < len(argv):
            return argv[index + 1]
        if token.startswith(name + "="):
            return token[len(name) + 1:]
    return None


def _store_path():
    try:
        config = json.loads(
            (_FAKE / "exec-config.json").read_text(encoding="utf-8"))
        value = config.get("sessions_db")
    except (OSError, ValueError):
        value = None
    return Path(value) if value else (_FAKE / "shared-sessions.db")


packet = _locate_packet()
if packet is None:
    _append_call({"argv": argv, "pwd": os.environ.get("PWD"),
                  "error": "packet-not-found"})
    sys.stderr.write("fixture t3: paquete no localizado\n")
    sys.exit(2)

match = _NONCE_RE.search(packet.decode("utf-8", errors="replace"))
if match is None:
    sys.stderr.write("fixture t3: el paquete no declara un nonce\n")
    sys.exit(2)
nonce = match.group(0)
# La SESIÓN la ELIGE el adaptador y viaja en --session (correlación,
# PD-8): la fila debe llevar ESA sesión. El id derivado del nonce es solo
# el fallback del fixture si la invocación no trae --session.
session_id = (_argv_option("--session")
              or "ses-t3-" + hashlib.sha256(
                  nonce.encode("utf-8")).hexdigest()[:12])
agent_id = _argv_option("--agent") or "cdad-test-writer"
model_id = _argv_option("--model") or ""
store_path = _store_path()
store_path.parent.mkdir(parents=True, exist_ok=True)
now = time.time()
final_text = nonce + " texto final fixture T3"

conn = sqlite3.connect(str(store_path), timeout=15)
try:
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS session_v2 ("
        " id TEXT PRIMARY KEY, agent TEXT, model TEXT,"
        " directory TEXT, time_created REAL, time_updated REAL,"
        " time_idle REAL, idle_outcome TEXT)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS session_message ("
        " id TEXT PRIMARY KEY, session_id TEXT, type TEXT,"
        " seq INTEGER, data TEXT)")
    conn.execute(
        "INSERT INTO session_v2 (id, agent, model, directory,"
        " time_created, time_updated, time_idle, idle_outcome)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, agent_id, model_id,
         os.environ.get("PWD") or os.getcwd(),
         now - 5.0, now, now, "succeeded"))
    user_data = json.dumps(
        {"content": [{"type": "text",
                      "text": "encargo con nonce " + nonce}]},
        sort_keys=True)
    assistant_data = json.dumps(
        {"content": [{"type": "text", "text": final_text}]},
        sort_keys=True)
    for msg_type, seq, data in (("user", 1, user_data),
                                ("assistant", 2, assistant_data)):
        conn.execute(
            "INSERT INTO session_message (id, session_id, type, seq, data)"
            " VALUES (?, ?, ?, ?, ?)",
            (f"msg-{seq:04d}-{session_id}", session_id, msg_type, seq, data))
    conn.commit()
finally:
    conn.close()

_append_call({
    "argv": argv,
    "pwd": os.environ.get("PWD"),
    "nonce": nonce,
    "session_id": session_id,
    "store_sha256_after": hashlib.sha256(
        store_path.read_bytes()).hexdigest(),
    "rc": 0,
})
sys.stdout.write(final_text + "\n")
sys.stdout.flush()
sys.exit(0)
'''


# ------------------------------------------------------------------ fixture


class T3ConcurrencyCase(Pd600T1Case):
    """Base del focal T3: proyecto descartable con NONCE PROPIO en el
    encargo (el fake lo extrae del paquete y lo firma en su fila, su texto
    final y su registro) más la fábrica del fake COMPARTIDO de T3 (un solo
    binario, un solo store, un solo escenario `service status` para todos
    los proyectos del test — PD-6: mismo store)."""

    def setUp(self) -> None:
        self.nonce = NONCE_PREFIX + uuid.uuid4().hex[:12]
        super().setUp()  # AdapterCase.setUp llama self.prepare_ok()
        self.records_before = dispatch_records(self.root, self.execution_id)

    def prepare_ok(self, *extra: str) -> subprocess.CompletedProcess:
        """prepare del proyecto con el nonce de ESTA instancia en el
        objetivo (el nonce viaja en el paquete: es el encargo propio que
        PD-6 exige por delegación)."""
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "cdad_packet.py"),
             "prepare", "--project-root", str(self.root),
             "--role", "test-writer", "--substage", "red",
             "--objective",
             f"encargo T3 006-001 (concurrencia): responde EXACTAMENTE y "
             f"ÚNICAMENTE con el nonce fijo {self.nonce} en tu mensaje "
             "final; no uses herramientas, no expliques, no agregues "
             "ningún otro texto.",
             *extra],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env={**dict(os.environ),
                 "CDAD_OPENCODE_AGENTS_DIR": str(self.agents_src)})
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): prepare no publicó el paquete "
                f"con el nonce propio: {proc.stdout + proc.stderr}")
        return proc

    # -- segundo proyecto (misma maquinaria, instancia aparte) -------------

    def second_project(self) -> "T3ConcurrencyCase":
        """Un SEGUNDO proyecto descartable, construido con la misma
        maquinaria de fixture (setUp propio sobre una instancia aparte de
        esta clase; su limpieza viaja con los cleanups de ESTE test). Sin
        tocar los focales de T1/T1b/T2 (plan §3, oráculo 4)."""
        other = T3ConcurrencyCase("runTest")
        other.setUp()
        self.addCleanup(other.doCleanups)
        return other

    # -- fake compartido ----------------------------------------------------

    def make_shared_fake(self, *, mode: str,
                         server_url: str | None = None) -> dict:
        """Escribe el binario falso PROPIO de T3 + su config con el store
        COMPARTIDO (un solo `sessions_db` para todos los proyectos del
        test — PD-6: mismo store descartable) y el escenario `service
        status` (URL en un puerto cerrado: nada escucha; si el adaptador
        conectara, no podría completar el despacho feliz)."""
        self.assert_adapter_in_product()
        fake_dir = Path(self._tmp) / "fake-t3-shared"
        bin_dir = fake_dir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        binary = bin_dir / "opencode-t3-fake"
        binary.write_text(T3_FAKE_BINARY_SOURCE, encoding="utf-8")
        binary.chmod(0o755)
        (fake_dir / "version.txt").write_text(
            T3_FAKE_VERSION + "\n", encoding="utf-8")
        logs_dir = fake_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "runtime": "opencode",
            "binary": str(binary),
            "binary_version": T3_FAKE_VERSION,
            "model": T3_MODEL,
            "logs_dir": str(logs_dir),
            "sessions_db": str(fake_dir / "shared-sessions.db"),
            "mode": mode,
            "wait": {"timeout_seconds": T3_WAIT_TIMEOUT_SECONDS,
                     **FAST_WAIT},
        }
        if mode == "server":
            config["server"] = server_url
        config_path = fake_dir / "exec-config.json"
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        # Escenario `service status`: corre (URL de puerto cerrado).
        service_url = closed_port_url()
        (fake_dir / "service-scenario.json").write_text(
            json.dumps({"stdout": service_url + "\n", "rc": 0},
                       sort_keys=True) + "\n", encoding="utf-8")
        # Registro del servicio de fixture (D-11): versión IGUAL a la del
        # cliente falso (despacho feliz) + contraseña centinela (INV-6).
        state = fake_dir / "state-home"
        registry_doc = {"id": "opencode-service-t3-fixture", "pid": 4242,
                        "url": service_url,
                        "version": T3_CLIENT_SEMVER,
                        "password": T3_SERVICE_SENTINEL_PASSWORD}
        for rel in (("opencode", "service.json"), ("service.json",)):
            path = state.joinpath(*rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(registry_doc, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
        return {
            "dir": fake_dir,
            "binary": binary,
            "config": config_path,
            "calls": fake_dir / "t3-calls.jsonl",
            "sessions_db": fake_dir / "shared-sessions.db",
            "state": state,
            "service_url": service_url,
            "scenario": fake_dir / "service-scenario.json",
        }

    # -- observación --------------------------------------------------------

    def fake_calls(self, fake: dict) -> list[dict]:
        path = fake["calls"]
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def fake_run_calls(self, fake: dict) -> list[dict]:
        """Invocaciones `run` registradas por el fake (las que transportan
        el encargo; `--version` y `service status` no escriben store)."""
        return [call for call in self.fake_calls(fake)
                if call.get("nonce")]

    def dispatch_pair(self, fake: dict, projects: list,
                      env_overrides: dict | None = None) -> list:
        """Despacha los proyectos EN PARALELO (dos subprocesos de la
        interfaz stageada corriendo a la vez: PD-6 exige concurrencia
        real, no secuencial)."""
        with ThreadPoolExecutor(max_workers=len(projects)) as pool:
            procs = list(pool.map(
                lambda p: p.dispatch(fake, env_overrides=env_overrides),
                projects))
        return [
            project.envelope(proc, "PD-6 despacho concurrente")
            for project, proc in zip(projects, procs)
        ]

    # -- aserciones compartidas de PD-6 --------------------------------------

    def assert_pair_completed_with_own_session(
            self, fake: dict, project_a, project_b, out_a: dict,
            out_b: dict) -> None:
        """PD-6: terminaciones completed; sesiones propias y distintas;
        fila durable por sesión con directory = su proyecto; correlación
        sin cruces (la entrada del fake con la PWD de cada proyecto
        declara SU nonce y SU sesión == la del envelope)."""
        for project, out in ((project_a, out_a), (project_b, out_b)):
            self.assertEqual(
                out["termination"], "completed",
                msg=f"PD-6: la delegación concurrente no terminó "
                    f"completed: {out['termination']!r}, diagnosis "
                    f"{out.get('diagnosis')!r}")
            self.assertTrue(out.get("session"),
                            msg="PD-6: envelope sin sesión")
        self.assertNotEqual(
            out_a["session"], out_b["session"],
            msg="PD-6: las dos delegaciones concurrentes comparten sesión "
                "(cruce de correlación: cada encargo debe tener su propia "
                "sesión)")
        rows = {row["id"]: row
                for row in durable_session_rows(fake["sessions_db"])}
        for project, out in ((project_a, out_a), (project_b, out_b)):
            row = rows.get(out["session"])
            self.assertIsNotNone(
                row,
                msg=f"PD-6: la sesión del envelope ({out['session']!r}) no "
                    "tiene fila durable en el store compartido")
            self.assertEqual(
                row.get("directory"), str(project.root),
                msg=f"PD-6: session_v2.directory de la fila NO es el "
                    f"proyecto de esa delegación: {row.get('directory')!r} "
                    f"!= {str(project.root)!r}")
            self.assertEqual(
                row.get("agent"), EXPECTED_ROLE_AGENT,
                msg="PD-6: la fila durable no declara el agente derivado "
                    f"cdad ({row.get('agent')!r})")
            self.assertEqual(
                row.get("idle_outcome"), "succeeded",
                msg="PD-6: la fila durable no quedó idle 'succeeded'")
            entries = [call for call in self.fake_run_calls(fake)
                       if call.get("pwd") == str(project.root)]
            self.assertEqual(
                len(entries), 1,
                msg=f"PD-6: la PWD del proyecto no tiene EXACTAMENTE una "
                    f"invocación run del fake (PWD declarada por el "
                    f"adaptador): {[c.get('pwd') for c in self.fake_run_calls(fake)]!r}")
            entry = entries[0]
            self.assertEqual(
                entry.get("nonce"), project.nonce,
                msg="PD-6: el fake recibió el nonce de OTRO proyecto "
                    "(cruce de encargos)")
            self.assertEqual(
                entry.get("session_id"), out["session"],
                msg="PD-6: la sesión que el fake escribió no es la que "
                    "declara el envelope (correlación rota)")

    def assert_nonce_isolation(self, fake: dict, project, out: dict,
                               other, label: str) -> None:
        """PD-6: el nonce del PROPIO proyecto aparece en SUS resultados y
        el del OTRO no aparece en NINGÚN archivo de resultados, en ningún
        archivo cambiado del árbol del proyecto, ni en el texto durable de
        la fila (los archivos cambiados quedan dentro de `.cdad/` y
        `docs/.cdad-state.json`)."""
        base = project.results_base()
        result_files = [path for path in sorted(base.rglob("*"))
                        if path.is_file()]
        self.assertTrue(
            result_files,
            msg=f"{label}: el proyecto no dejó resultados durables")
        hits = [path for path in result_files
                if project.nonce.encode("utf-8") in path.read_bytes()]
        self.assertTrue(
            hits,
            msg=f"{label}: el nonce propio {project.nonce!r} no aparece "
                "en los resultados del proyecto (entrega sin el encargo "
                "propio)")
        for path in result_files:
            self.assertNotIn(
                other.nonce.encode("utf-8"), path.read_bytes(),
                msg=f"{label}: el nonce del OTRO proyecto ({other.nonce!r}) "
                    f"aparece en {path.name} (cruce de resultados, PD-6)")
        for rel in project.tree_changed():
            path = project.root / rel
            if path.is_file():
                self.assertNotIn(
                    other.nonce.encode("utf-8"), path.read_bytes(),
                    msg=f"{label}: el nonce del OTRO proyecto aparece en "
                        f"el archivo cambiado {rel} (cruce de árboles, "
                        "PD-6)")
        unexpected = project.unexpected_touched(project.tree_changed())
        self.assertEqual(
            unexpected, [],
            msg=f"{label}: la delegación tocó archivos fuera de su "
                f"frontera (PD-6: `.cdad/` y docs/.cdad-state.json): "
                f"{unexpected!r}")
        final_text = durable_last_assistant_text(
            fake["sessions_db"], out["session"])
        self.assertIsNotNone(
            final_text,
            msg=f"{label}: la fila durable no tiene texto final")
        self.assertIn(
            project.nonce, final_text,
            msg=f"{label}: el texto durable no lleva el nonce propio")
        self.assertNotIn(
            other.nonce, final_text,
            msg=f"{label}: el texto durable lleva el nonce del OTRO "
                "proyecto (cruce en el store, PD-6)")

    def assert_no_adapter_store_write(self, fake: dict) -> None:
        """PD-6/INV-1: el store compartido no fue escrito por el
        adaptador. El fake registra el hash del store POST-commit de cada
        run; el hash FINAL del archivo debe ser uno de esos estados: una
        escritura del adaptador (después de que los fakes terminaron)
        crearía un estado no registrado."""
        recorded = {call.get("store_sha256_after")
                    for call in self.fake_run_calls(fake)}
        final_hash = sha256(fake["sessions_db"].read_bytes()).hexdigest()
        self.assertIn(
            final_hash, recorded,
            msg="PD-6/INV-1: el hash final del store compartido no "
                "coincide con NINGÚN estado post-commit registrado por el "
                "fake: hubo una escritura del store fuera de las filas del "
                "rol (el adaptador no debe escribir el store)")

    def assert_provenance_per_attempt(self, project, out: dict, *,
                                      expected: dict, label: str) -> dict:
        """PD-3/§2.6: UN registro de worker POR INTENTO con la procedencia
        nueva: los pares esperados + `store_reads`/`prior_check_reads`
        enteros (INV-9: medido, no vacío ni cero-forzado) y la sesión del
        envelope."""
        records = project.worker_records_with_marker(project.records_before)
        self.assertEqual(
            len(records), 1,
            msg=f"{label}: el número de registros de worker (procedencia "
                f"§2.6) no es UNO por intento: {len(records)}")
        provenance = records[0].get("provenance", {})
        runtime_prov = str(provenance.get("runtime", ""))
        session_prov = str(provenance.get("session", ""))
        for key, value in expected.items():
            self.assertEqual(
                _prov_value(runtime_prov, key), value,
                msg=f"{label}: el par `{key}=` de la procedencia no es "
                    f"{value!r}: {runtime_prov!r}")
        # PD-8: la correlación del intento viaja en la SESIÓN del envelope
        # (provenance.session identifica la fila durable, no repite el id:
        # forma de §2.6 fijada por T1 GREEN).
        self.assertIn(
            "durable session row", session_prov,
            msg=f"{label}: provenance.session no identifica la fila "
                f"durable del intento (§2.6): {session_prov!r}")
        for key in ("store_reads", "prior_check_reads"):
            value = _prov_value(session_prov, key)
            self.assertIsNotNone(
                value,
                msg=f"{label}: el par `{key}=` no está en la procedencia "
                    f"(INV-9): {session_prov!r}")
            self.assertTrue(
                (value or "") == "unknown" or (value or "").isdigit(),
                msg=f"{label}: `{key}=` no es un entero medido ni "
                    f"`unknown` (INV-9): {value!r}")
        return records[0]

    def assert_no_management_invocations(self, fake: dict,
                                         label: str) -> None:
        """INV-2/INV-10: ningún argv lleva `serve` ni `reload`, y la única
        invocación de `service` es el subcomando de solo lectura
        `status` (jamás start|stop|restart|get|set|unset)."""
        for call in self.fake_calls(fake):
            argv = call.get("argv", [])
            for token in T3_FORBIDDEN_ARGV_TOKENS:
                self.assertNotIn(
                    token, argv,
                    msg=f"{label}: una invocación lleva {token!r} (INV-2: "
                        "CDAD no arranca, recarga ni gestiona servidores "
                        f"ni el servicio): {argv!r}")
            if argv and argv[0] == "service":
                self.assertEqual(
                    argv, ["service", "status"],
                    msg=f"{label}: la única invocación de `service` "
                        "admitida es `service status` (INV-2/INV-10): "
                        f"{argv!r}")


# --------------------------------------------------------------------- PD-6


class TestPd6ConcurrencyFixture(T3ConcurrencyCase):
    """PD-6 con fixture: dos proyectos concurrentes, mismo store, mismo
    servidor de fixture (modo servidor) y mismo servicio de fixture (modo
    service). El RED de este fichero es el ORÁCULO: hoy puede pasar por el
    GREEN previo (declarado en el docstring del módulo); si el
    comportamiento concurrente falta, falla por AssertionError de
    contrato."""

    def test_pd6_two_concurrent_server_mode_dispatches_complete_without_cross_correlation(self) -> None:
        """PD-6 (pierna (a) fixture, topología servidor de D-8): dos
        delegaciones concurrentes desde dos proyectos descartables contra
        el MISMO store y el MISMO servidor de fixture `/api/info`; ambas
        `completed`, sesión y nonce propios sin cruces, sin escrituras del
        adaptador al store y con procedencia por intento (PD-3). INV-6: la
        URL del servidor solo en el argv de `run --server`."""
        server = FakeInfoServer(
            body=json.dumps({"version": T3_CLIENT_SEMVER}).encode("utf-8"))
        self.addCleanup(server.stop)
        fake = self.make_shared_fake(mode="server", server_url=server.url)
        project_b = self.second_project()
        self.assert_derived_agents_published()
        project_b.assert_derived_agents_published()

        out_a, out_b = self.dispatch_pair(fake, [self, project_b])

        self.assert_pair_completed_with_own_session(
            fake, self, project_b, out_a, out_b)
        self.assert_nonce_isolation(fake, self, out_a, project_b,
                                    "PD-6 servidor: A")
        self.assert_nonce_isolation(fake, project_b, out_b, self,
                                    "PD-6 servidor: B")
        self.assert_no_adapter_store_write(fake)
        for project, out in ((self, out_a), (project_b, out_b)):
            self.assert_provenance_per_attempt(
                project, out, label="PD-6 servidor",
                expected={
                    "mode_requested": "server",
                    "mode_effective": "server",
                    "dispatch_flags": "--server",
                    "client_version": T3_CLIENT_SEMVER,
                    "server_version": T3_CLIENT_SEMVER,
                    "service_status": "not-checked",
                    "fallback": "none",
                })
            project.assert_receipt_no_gate()
            # INV-6 (PD-5): la URL del servidor solo en el argv de `run
            # --server`; nunca en envelope, registros ni recibo.
            blob = (out.get("diagnosis") or "") + receipt_path_text(project)
            self.assertNotIn(
                server.url, blob,
                msg="PD-5/INV-6: la URL del servidor de fixture aparece "
                    "fuera del argv de `run --server` (envelope, registros "
                    "I8 o recibo)")
            argv_runs = [call.get("argv") for call in self.fake_run_calls(fake)
                         if call.get("pwd") == str(project.root)]
            self.assertEqual(
                len(argv_runs), 1, msg="precondición: una invocación run")
            self.assertIn(
                "--server", argv_runs[0],
                msg="PD-1 (fila server de §2.2): el argv de `run` debe "
                    "llevar `--server <url>` en modo servidor")
        self.assert_no_management_invocations(fake, "PD-6 servidor")

    def test_pd6_two_concurrent_service_mode_dispatches_complete_without_cross_correlation(self) -> None:
        """PD-6 (enmienda: modo `service`, despacho SIN flags): dos
        delegaciones concurrentes contra el MISMO store con fake de
        `service status` (corre) y registro del servicio compatible (D-11);
        ambas `completed`, sesión y nonce propios sin cruces; el argv de
        `run` no lleva `--server` ni `--standalone`; `service status`
        EXACTAMENTE una vez por despacho; sin gestión del servicio
        (INV-2/INV-10). INV-6: ni la contraseña centinela del registro ni
        la URL del servicio aparecen en las salidas."""
        fake = self.make_shared_fake(mode="service")
        project_b = self.second_project()
        self.assert_derived_agents_published()
        project_b.assert_derived_agents_published()

        out_a, out_b = self.dispatch_pair(
            fake, [self, project_b],
            env_overrides={"XDG_STATE_HOME": str(fake["state"])})

        self.assert_pair_completed_with_own_session(
            fake, self, project_b, out_a, out_b)
        self.assert_nonce_isolation(fake, self, out_a, project_b,
                                    "PD-6 service: A")
        self.assert_nonce_isolation(fake, project_b, out_b, self,
                                    "PD-6 service: B")
        self.assert_no_adapter_store_write(fake)

        status_calls = [call for call in self.fake_calls(fake)
                        if call.get("argv", [])[:2] == ["service", "status"]]
        self.assertEqual(
            len(status_calls), 2,
            msg="PD-13: `service status` no se invocó EXACTAMENTE una vez "
                f"por despacho (2 despachos): {len(status_calls)}")
        run_argvs = [call.get("argv") for call in self.fake_run_calls(fake)]
        self.assertEqual(len(run_argvs), 2, msg="precondición: 2 run")
        for argv in run_argvs:
            self.assertNotIn(
                "--server", argv,
                msg="PD-13: el despacho en modo service NO lleva "
                    f"--server: {argv!r}")
            self.assertNotIn(
                "--standalone", argv,
                msg="PD-13: el despacho en modo service NO lleva "
                    f"--standalone (despacho sin flags, enmienda 001): "
                    f"{argv!r}")
        for project, out in ((self, out_a), (project_b, out_b)):
            self.assert_provenance_per_attempt(
                project, out, label="PD-6 service",
                expected={
                    "mode_requested": "service",
                    "mode_effective": "service",
                    "dispatch_flags": "none",
                    "client_version": T3_CLIENT_SEMVER,
                    "server_version": T3_CLIENT_SEMVER,
                    "service_status": "running",
                    "fallback": "none",
                })
            project.assert_receipt_no_gate()
            blob = (out.get("diagnosis") or "") + receipt_path_text(project)
            self.assertNotIn(
                T3_SERVICE_SENTINEL_PASSWORD, blob,
                msg="PD-5/INV-6: la contraseña del registro del servicio "
                    "aparece en las salidas")
            self.assertNotIn(
                fake["service_url"], blob,
                msg="PD-5/INV-6: la URL del servicio aparece fuera del "
                    "argv (envelope, registros I8 o recibo)")
        self.assert_no_management_invocations(fake, "PD-6 service")


def receipt_path_text(project) -> str:
    """Los bytes del recibo durable del proyecto (para el barrido de
    secretos; el recibo puede no existir solo en caminos sin entrega — en
    completed siempre existe y la ausencia la assertiona
    assert_receipt_no_gate antes)."""
    path = project.results_base() / "receipt.json"
    return path.read_text(encoding="utf-8") if path.is_file() else ""
