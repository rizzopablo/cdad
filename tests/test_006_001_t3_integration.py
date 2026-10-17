#!/usr/bin/env python3
"""006-001 T3 — Recorrido REAL en modo servidor (PD-6 pierna (b); D-7, D-8)
y complemento standalone.

Contract: docs/specs/006-001-opencode-concurrency-reliability/spec.md v2
(§5.1-§5.4 topología aislada, §3 PD-6 «Triple evidencia» pierna (b); D-7,
D-8) + plan v2, ficha T3 (observable_checks: «recorrido REAL en modo
servidor... lo corre el orquestador con la credencial del operador»). Plan
provenance: plan.md (sha256 2726744566f58af88540f03b6bb1cec6a73534c6adb43b
fbf466206278a1ea72).

OMISIÓN POR DEFECTO (misma convención que tests/test_005_010_t4_integration
.py): el test se OMITE salvo opt-in por entorno; la corre el ORQUESTADOR con
la credencial del operador. Sin la variable NO corre NADA de runtime y la
omisión se registra con diagnóstico (una omisión NO es un pase: PD-6 queda
en BLOQUEO declarado, D-8/plan §6). Variables (sin valores por defecto del
host; el test NUNCA lee el valor de la credencial, solo su NOMBRE):

  CDAD_OPENCODE_INTEGRATION=1     habilita la prueba (única variable de control)
  CDAD_OPENCODE_BINARY            ruta del binario REAL de OpenCode
  CDAD_OPENCODE_MODEL             modelo de la configuración de ejecución
  CDAD_OPENCODE_KEY_ENV           NOMBRE de la variable que lleva la clave
                                  del proveedor (el valor lo pone el
                                  operador en SU entorno; el test verifica
                                  PRESENCIA, jamás lee el valor)

TOPOLOGÍA (spec §5.1-§5.3, INV-2): servidor REAL descartable `opencode
serve --hostname 127.0.0.1 --port <libre>` lanzado y detenido POR EL TEST
(SIGTERM al grupo, gracia, SIGKILL); contraseña aleatoria por corrida en
`OPENCODE_SERVER_PASSWORD` (solo en el entorno de los procesos del test);
store aislado bajo `<ROOT>` (tempdir del test) con XDG_DATA/STATE/CACHE bajo
`<ROOT>`; GUARDA previa `opencode debug paths`: si `db`/`data`/`state`/`log`
no caen bajo `<ROOT>`, el test FALLA SIN DESPACHAR (plan, incertidumbre 1).
Credencial del proveedor por SUSTITUCIÓN de config (D-7, spec §5.3): el
entorno del servidor lleva
`OPENCODE_CONFIG_CONTENT={"provider":{"<provider>":{"options":{"apiKey":"{env:<VAR>}"}}}}`
con `<provider>` = prefijo de `CDAD_OPENCODE_MODEL` y `<VAR>` = valor de
`CDAD_OPENCODE_KEY_ENV`; el test NUNCA lee ni copia `auth.json` ni la base
viva. Dos delegaciones concurrentes desde DOS proyectos descartables en
modo servidor + el COMPLEMENTO standalone (tercer proyecto, spec §5.1). El
servicio de fondo del host NUNCA se arranca, reinicia ni reconfigura: el
recorrido contra el servicio VIVO (spec §5.5) es otra pierna que corre el
orquestador o el dueño aparte (PD-6 pierna (c)).

REUTILIZACIÓN (plan T3, contexto por rol): helpers de
tests/test_005_010_t4_integration.py:169-342 vía herencia de
`TestPd8RealOpenCodeIntegration` (proyecto sintético + staging de la skill
+ `CDAD_INSTALL_ROOT` aislado + lectura del store real en `mode=ro`); las
sobrescrituras locales son: agente derivado de PRUEBA genérico (el token
viaja en el OBJETIVO del paquete, uno distinto por proyecto), `prepare` con
ese objetivo, validación de entorno SIN `CDAD_OPENCODE_SESSIONS_DB` (el
store REAL aislado sale de la guarda `debug paths`, no de una variable) y
despacho con el entorno AISLADO del recorrido.

Mapa test → postcondición:

  1  test_pd6_real_server_two_concurrent_and_standalone_complement
       PD-6 (pierna (b), D-8): dos delegaciones REALES concurrentes en
       modo servidor terminan `completed` con sesión propia y no cruzada;
       cada fila durable (`session_v2`, leída mode=ro) declara la identidad
       cdad, idle succeeded y directory = su proyecto; el token de A solo
       en los resultados de A (y viceversa: sin cruce de encargos); el
       recibo queda `pending` (INV-5); complemento standalone completed.
       Observaciones VERIFY (spec §5.6) registradas por stdout con la marca
       `T3-VERIFY-OBSERVATIONS` (correr con `-s` para capturarlas en el
       informe del orquestador): forma de `version` en `/api/info`, valor
       de `session_v2.version` de las filas correlacionadas (VERIFY e), y
       modo de auth observado del servidor descartable.

RED: con la implementación de T1/T1b/T2 en GREEN (ddba831) este recorrido
puede pasar hoy; su valor es el ORÁCULO de aceptación de PD-6 en la
topología real (el fixture NO basta, D-8). Si el recorrido real rompe el
contrato (cruce de correlación, terminación distinta de completed, fila
desidentificada, guardas de aislamiento), falla por AssertionError de
COMPORTAMIENTO — nunca por import/sintaxis.
"""

from __future__ import annotations

import base64
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import test_005_010_t4_integration as _t4_module
from test_005_010_t4_integration import (
    DELEGATE_SUBPROCESS_TIMEOUT,
    real_session_row,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Variables de entorno de la integración (declaradas arriba; SIN valores
# por defecto del host — INV-6/INV-7).
ENABLE_VAR = "CDAD_OPENCODE_INTEGRATION"
BINARY_VAR = "CDAD_OPENCODE_BINARY"
MODEL_VAR = "CDAD_OPENCODE_MODEL"
KEY_ENV_VAR = "CDAD_OPENCODE_KEY_ENV"

EXPECTED_ROLE_AGENT = "cdad-test-writer"

SERVER_WAIT_TIMEOUT_SECONDS = 60   # arranque del servidor descartable
REAL_WAIT_TIMEOUT_SECONDS = 600    # espera ACOTADA del recorrido real

# Llaves de la guarda `debug paths` (spec §5.2): deben caer bajo <ROOT>.
GUARD_REQUIRED_KEYS = ("db", "state", "log")
GUARD_CHECKED_KEYS = ("db", "data", "state", "log")


# ---------------------------------------------------------------- fixture


class _T3RealFixtureBase(_t4_module.TestPd8RealOpenCodeIntegration):
    """Base de fixture del recorrido real T3: hereda los HELPERS de la base
    T4 (reuso declarado por el plan T3, líneas 169-342) y ENMASCARA el test
    de esa base (no es de esta ficha; la base lo conserva en SU módulo).
    Sin métodos de test propios: pytest no la colecciona (misma convención
    que las bases de fixture del resto de la suite, p.ej. `T1bServiceCase`)."""

    test_pd8_real_runtime_delegation_completes_with_durable_correlation = None  # noqa: A003


class TestPd6RealServerIntegration(_T3RealFixtureBase):
    """PD-6 pierna (b): recorrido REAL en modo servidor con dos
    delegaciones concurrentes y el complemento standalone. OMITIDA por
    defecto; habilitada por entorno; la corre el ORQUESTADOR (la omisión
    por falta de credencial NO es un pase)."""

    def setUp(self) -> None:
        self.errand_token = "CDAD-T3-REAL-TOKEN-" + uuid.uuid4().hex[:12]
        super().setUp()  # valida entorno (skip si falta) + proyecto A

    # -- entorno requerido (override: SIN sessions_db; CON key_env) -------

    @staticmethod
    def _skip(message: str) -> None:
        raise unittest.SkipTest(message)

    def _require_integration_env(self) -> None:
        if os.environ.get(ENABLE_VAR, "") != "1":
            self._skip(
                "PD-6 pierna (b) omitida por defecto: el recorrido REAL "
                "en modo servidor se habilita con "
                f"{ENABLE_VAR}=1 y lo corre el ORQUESTADOR con la "
                "credencial del operador (sin la variable no se corre "
                "NINGÚN runtime; la omisión NO es un pase: PD-6 queda en "
                "BLOQUEO declarado).")
        binary = os.environ.get(BINARY_VAR, "").strip()
        if not binary:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{BINARY_VAR} (ruta del binario REAL de OpenCode): la "
                "prueba no toma valores por defecto del host.")
        if not (Path(binary).is_file() and os.access(binary, os.X_OK)):
            self._skip(
                f"la variable {BINARY_VAR} está definida pero su valor no "
                f"es un binario ejecutable existente: {binary!r} (el "
                "binario lo provee la configuración; se omite con "
                "diagnóstico, no se fabrica un verde).")
        model = os.environ.get(MODEL_VAR, "").strip()
        if not model:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{MODEL_VAR} (modelo de la configuración de ejecución): "
                "la prueba no toma valores por defecto del host.")
        key_env = os.environ.get(KEY_ENV_VAR, "").strip()
        if not key_env:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{KEY_ENV_VAR} (NOMBRE de la variable que lleva la clave "
                "del proveedor para la sustitución {env:<VAR>}, spec §5.3 "
                "D-7): la prueba no lee valores de credenciales, solo el "
                "nombre; sin nombre se omite con motivo y la omisión NO "
                "acredita PD-6 (BLOQUEO declarado).")
        if key_env not in os.environ:
            self._skip(
                f"la variable {KEY_ENV_VAR} nombra a <VAR>={key_env!r} y "
                "esa variable NO está definida en el entorno del "
                "operador: omisión por falta de credencial (spec §5.3). "
                "Una omisión NO es un pase: PD-6 queda en BLOQUEO "
                "declarado para el gate de cierre (plan §6).")

    # -- proyecto con token propio (override de los helpers T4) ------------

    def seed_agents(self) -> Path:
        """Agente derivado de PRUEBA mínimo GENÉRICO: la orden del token
        viaja en el OBJETIVO del paquete (el modelo sigue el paquete por
        encima del agente derivado — orden explícita de
        tests/test_005_010_t4_integration.py), así que cada proyecto
        concurrente puede llevar SU token sin tocar el fuente del agente."""
        agents_src = Path(self._tmp) / "agents-src"
        agents_src.mkdir(parents=True, exist_ok=True)
        (agents_src / f"{EXPECTED_ROLE_AGENT}.md").write_text(
            "---\n"
            "description: Agente derivado de PRUEBA del recorrido real T3 "
            "de 006-001: responde el token de su objetivo y nada más.\n"
            "mode: subagent\n"
            "---\n\n"
            "Agente derivado de PRUEBA del recorrido de integración real "
            "(tests/test_006_001_t3_integration.py; NO es un rol real del "
            "ciclo).\n\n"
            "Tu única tarea: responde EXACTAMENTE y ÚNICAMENTE con el "
            "token fijo que tu objetivo te indica, en tu mensaje final. "
            "No uses herramientas, no expliques, no agregues ningún otro "
            "texto: SOLO el token.\n",
            encoding="utf-8")
        return agents_src

    def prepare_ok(self, *extra: str) -> subprocess.CompletedProcess:
        """prepare del proyecto sintético con el TOKEN PROPIO de esta
        instancia en el objetivo (nonce del recorrido real: PD-6 exige
        encargo propio por delegación)."""
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "cdad_packet.py"),
             "prepare", "--project-root", str(self.root),
             "--role", "test-writer", "--substage", "red",
             "--objective",
             f"encargo T3 006-001 (recorrido real): responde EXACTAMENTE "
             f"y ÚNICAMENTE con el token fijo {self.errand_token} en tu "
             "mensaje final; no uses herramientas, no expliques, no "
             "agregues ningún otro texto.",
             *extra],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env={**dict(os.environ),
                 "CDAD_OPENCODE_AGENTS_DIR": str(self.agents_src)})
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): prepare no publicó el paquete "
                f"con el token propio: {proc.stdout + proc.stderr}")
        return proc

    def second_project(self) -> "TestPd6RealServerIntegration":
        """Otro proyecto descartable con la misma maquinaria (instancia
        aparte de esta clase; su limpieza viaja con los cleanups de ESTE
        test). Se usa para B (concurrente servidor) y C (standalone)."""
        other = TestPd6RealServerIntegration("runTest")
        other.setUp()
        self.addCleanup(other.doCleanups)
        return other

    # -- topología aislada (spec §5.1-§5.3) ---------------------------------

    def build_isolated_env(self, root: Path) -> dict:
        """Entorno AISLADO del recorrido: XDG_DATA/STATE/CACHE bajo
        `<ROOT>`, contraseña aleatoria por corrida en
        `OPENCODE_SERVER_PASSWORD` (solo en el entorno de los procesos del
        test) y la credencial del proveedor por SUSTITUCIÓN (D-7): el
        proveedor sale del prefijo de `CDAD_OPENCODE_MODEL` y la clave es
        `{env:<VAR>}` — el test NUNCA lee el valor de la variable."""
        provider = os.environ[MODEL_VAR].strip().split("/", 1)[0]
        key_env = os.environ[KEY_ENV_VAR].strip()
        return {
            "XDG_DATA_HOME": str(root / "xdg-data"),
            "XDG_STATE_HOME": str(root / "xdg-state"),
            "XDG_CACHE_HOME": str(root / "xdg-cache"),
            "OPENCODE_SERVER_PASSWORD": "cdad-t3-real-" + uuid.uuid4().hex,
            "OPENCODE_CONFIG_CONTENT": json.dumps(
                {"provider": {provider: {
                    "options": {"apiKey": "{env:" + key_env + "}"}}}},
                sort_keys=True),
        }

    def _auth_header(self, env: dict) -> str:
        token = base64.b64encode(
            f"opencode:{env['OPENCODE_SERVER_PASSWORD']}".encode("utf-8")
        ).decode("ascii")
        return f"Basic {token}"

    def _get_api_info(self, url: str, env: dict,
                      with_auth: bool) -> tuple[int, dict | None]:
        request = urllib.request.Request(url + "/api/info")
        if with_auth:
            request.add_header("Authorization", self._auth_header(env))
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                body = response.read()
                status = response.status
        except urllib.error.HTTPError as error:
            return error.code, None
        try:
            return status, json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return status, None

    def start_disposable_server(self, binary: str, env: dict,
                                root: Path) -> tuple[dict, str]:
        """Lanza `opencode serve` descartable en loopback (puerto libre),
        espera `/api/info`, y devuelve (observaciones, url). El grupo de
        procesos se detiene en el cleanup (SIGTERM, gracia, SIGKILL): lo
        lanza y lo detiene el TEST (spec §5.1). Nada toca el servicio de
        fondo del host (INV-2)."""
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()
        url = f"http://127.0.0.1:{port}"
        out_log = (root / "serve-out.log").open("wb")
        err_log = (root / "serve-err.log").open("wb")
        server = subprocess.Popen(
            [binary, "serve", "--hostname", "127.0.0.1",
             "--port", str(port)],
            env=env, stdout=out_log, stderr=err_log,
            start_new_session=True)
        out_log.close()
        err_log.close()
        self.addCleanup(self.stop_disposable_server, server)
        deadline = time.monotonic() + SERVER_WAIT_TIMEOUT_SECONDS
        observations = {"auth_mode": None, "api_info_version": None}
        last_status = None
        while time.monotonic() < deadline:
            if server.poll() is not None:
                self.fail(
                    msg=f"el servidor descartable salió antes de atender "
                        f"/api/info (rc={server.returncode}); logs del "
                        f"servidor bajo {root} (serve-out.log/"
                        "serve-err.log)")
            for with_auth in (True, False):
                status, info = self._get_api_info(url, env, with_auth)
                last_status = status
                if status == 200 and isinstance(info, dict):
                    observations["auth_mode"] = (
                        "basic" if with_auth else "none")
                    observations["api_info_version"] = info.get("version")
                    break
                time.sleep(0.25)
            if observations["api_info_version"] is not None:
                break
            time.sleep(0.25)
        if observations["api_info_version"] is None:
            self.fail(
                msg=f"el servidor descartable no atendió /api/info en "
                    f"{SERVER_WAIT_TIMEOUT_SECONDS} s (último status "
                    f"{last_status!r}; logs bajo {root})")
        return observations, url

    @staticmethod
    def stop_disposable_server(server: subprocess.Popen) -> None:
        """Detiene el servidor descartable del TEST: SIGTERM al grupo,
        gracia acotada, SIGKILL al grupo (spec §5.1). Solo el proceso del
        test: nunca el servicio de fondo del host (INV-2)."""
        if server.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(server.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(server.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            server.wait(timeout=10)

    def debug_paths(self, binary: str, env: dict) -> dict:
        """`opencode debug paths` con el MISMO entorno del recorrido
        (guarda previa, spec §5.2). Parseo tolerante (JSON o líneas
        `clave: valor` / `clave=valor` / `clave valor`); si no se puede
        parsear, devuelvo {} y la guarda falla cerrada (sin despachar)."""
        proc = subprocess.run(
            [binary, "debug", "paths"], env=env,
            capture_output=True, text=True, timeout=30,
            stdin=subprocess.DEVNULL)
        if proc.returncode != 0:
            return {}
        text = proc.stdout.strip()
        try:
            doc = json.loads(text)
            if isinstance(doc, dict):
                return {str(k): str(v) for k, v in doc.items()}
        except ValueError:
            pass
        mapping: dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for separator in (":", "="):
                if separator in line:
                    key, _, value = line.partition(separator)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        mapping[key] = value.split()[-1]
                    break
        return mapping

    def assert_paths_under_root(self, mapping: dict, root: Path) -> None:
        """GUARDA (spec §5.2): `db`, `data`, `state` y `log` deben caer
        bajo `<ROOT>`; si no, FALLA SIN DESPACHAR (plan, incertidumbre 1)."""
        root_resolved = root.resolve()
        for key in GUARD_REQUIRED_KEYS:
            self.assertIn(
                key, mapping,
                msg=f"guarda `debug paths`: el reporte no incluye la "
                    f"llave requerida {key!r} (no se puede afirmar el "
                    f"aislamiento del store; el test FALLA SIN DESPACHAR): "
                    f"{mapping!r}")
        for key in GUARD_CHECKED_KEYS:
            if key not in mapping:
                continue
            path = Path(mapping[key]).resolve()
            under = path == root_resolved or root_resolved in path.parents
            self.assertTrue(
                under,
                msg=f"guarda `debug paths`: {key!r} NO cae bajo <ROOT> "
                    f"({root_resolved}): {path} — el test FALLA SIN "
                    "DESPACHAR (aislamiento del store no afirmable, "
                    "spec §5.2)")

    # -- config y despacho con entorno aislado ------------------------------

    def real_exec_config(self, project, *, binary: str, model: str,
                         db_path: Path, server_url: str | None = None,
                         mode: str | None = None) -> Path:
        """Exec-config TEMPORAL del recorrido real: valores SOLO del
        entorno/`<ROOT>` (sin valores por defecto del host, INV-7); la
        espera es ACOTADA; `binary_version` de la sonda honesta
        `--version` o `unknown`."""
        try:
            probe = subprocess.run(
                [binary, "--version"], capture_output=True, text=True,
                timeout=30, stdin=subprocess.DEVNULL)
            version = (probe.stdout.strip().splitlines() or [""])[0].strip()
        except (OSError, subprocess.SubprocessError):
            version = ""
        config_dir = Path(project._tmp) / "real-runtime"
        logs_dir = config_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        config = {
            "runtime": "opencode",
            "binary": binary,
            "binary_version": version or "unknown",
            "model": model,
            "logs_dir": str(logs_dir),
            "sessions_db": str(db_path),
            "wait": {"timeout_seconds": REAL_WAIT_TIMEOUT_SECONDS},
        }
        if mode is not None:
            config["mode"] = mode
        if server_url is not None:
            config["server"] = server_url
        config_path = config_dir / "exec-config.json"
        config_path.write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return config_path

    def run_isolated_delegate(self, project, config: Path,
                              env: dict) -> subprocess.CompletedProcess:
        """La INTERFAZ COMÚN stageada del proyecto despacha al destino
        `opencode` con la exec-config del recorrido y el ENTORNO AISLADO
        (XDG bajo `<ROOT>` + contraseña del servidor): el cliente y el
        adaptador quedan confinados al `<ROOT>` del test; `CDAD_INSTALL_
        ROOT` apunta al tempdir del proyecto (nada instala ni escribe en
        el HOME del dueño)."""
        return subprocess.run(
            [sys.executable, str(project.staged),
             "--project-root", str(project.root),
             "--packet", project.packet_id,
             "--destination", "opencode",
             "--exec-config", str(config)],
            capture_output=True, text=True,
            env={**env, "CDAD_INSTALL_ROOT": str(project._tmp)},
            timeout=DELEGATE_SUBPROCESS_TIMEOUT)

    # -- aserciones ---------------------------------------------------------

    def assert_real_token_isolation(self, project, others, label: str) -> None:
        """PD-6: el token PROPIO aparece en los resultados del proyecto y
        NINGÚN token ajeno aparece en ellos (sin cruce de encargos)."""
        base = project.results_base()
        files = [path for path in sorted(base.rglob("*"))
                 if path.is_file()]
        self.assertTrue(
            files, msg=f"{label}: el proyecto no dejó resultados durables")
        hits = [path for path in files
                if project.errand_token.encode("utf-8")
                in path.read_bytes()]
        self.assertTrue(
            hits,
            msg=f"{label}: el token propio {project.errand_token!r} no "
                "aparece en los resultados del proyecto")
        for path in files:
            data = path.read_bytes()
            for other in others:
                self.assertNotIn(
                    other.errand_token.encode("utf-8"), data,
                    msg=f"{label}: el token de OTRO proyecto "
                        f"({other.errand_token!r}) aparece en "
                        f"{path.name} (cruce de resultados, PD-6)")

    # -- PD-6 pierna (b) ------------------------------------------------------

    def test_pd6_real_server_two_concurrent_and_standalone_complement(self) -> None:
        """PD-6 (recorrido REAL, spec §5): servidor descartable en
        loopback con contraseña aleatoria, store aislado bajo <ROOT>
        confirmado por la guarda `debug paths`, credencial por `{env:VAR}`
        sin copiar auth.json; DOS delegaciones concurrentes desde dos
        proyectos descartables terminan `completed` con sesión propia y
        nonces (tokens) separados; complemento standalone; observaciones
        VERIFY registradas por stdout (`T3-VERIFY-OBSERVATIONS`)."""
        binary = os.environ[BINARY_VAR].strip()
        model = os.environ[MODEL_VAR].strip()
        root = Path(self._tmp) / "real-root"
        root.mkdir(parents=True, exist_ok=True)
        env = self.build_isolated_env(root)

        # 1. Servidor REAL descartable (lo lanza y lo detiene el test).
        observations, url = self.start_disposable_server(binary, env, root)

        # 2. GUARDA `debug paths` (falla SIN despachar si no confina).
        paths = self.debug_paths(binary, env)
        self.assert_paths_under_root(paths, root)
        db_path = Path(paths["db"])

        # 3. Tres proyectos descartables: A y B concurrentes en modo
        #    servidor, C standalone (complemento, spec §5.1).
        project_b = self.second_project()
        project_c = self.second_project()
        config_server = self.real_exec_config(
            self, binary=binary, model=model, db_path=db_path,
            server_url=url, mode="server")
        config_standalone = self.real_exec_config(
            project_c, binary=binary, model=model, db_path=db_path,
            mode="standalone")

        # 4. Dos delegaciones REALES concurrentes (PD-6).
        with ThreadPoolExecutor(max_workers=2) as pool:
            procs = list(pool.map(
                lambda p: self.run_isolated_delegate(p, config_server, env),
                [self, project_b]))
        out_a = self.envelope(procs[0], "PD-6 real servidor: A")
        out_b = project_b.envelope(procs[1], "PD-6 real servidor: B")
        proc_c = self.run_isolated_delegate(project_c, config_standalone,
                                            env)
        out_c = project_c.envelope(proc_c, "PD-6 real standalone")

        # 5. Terminación y correlación sin cruces.
        for project, out, label in ((self, out_a, "A"),
                                    (project_b, out_b, "B"),
                                    (project_c, out_c, "standalone")):
            self.assertEqual(
                out["termination"], "completed",
                msg=f"PD-6 (recorrido real): la delegación {label} no "
                    f"terminó completed: {out['termination']!r}, "
                    f"diagnosis {out.get('diagnosis')!r}")
            self.assertTrue(
                out.get("session"),
                msg=f"PD-6 (recorrido real): delegación {label} sin "
                    "sesión en el envelope")
        self.assertEqual(
            len({out_a["session"], out_b["session"], out_c["session"]}), 3,
            msg="PD-6 (recorrido real): sesiones repetidas entre las tres "
                "delegaciones (cruce de correlación)")

        # 6. Fila durable REAL por sesión (mode=ro): identidad cdad, idle
        #    succeeded, directory = su proyecto; VERIFY (e) registrado.
        rows = {}
        for project, out, label in ((self, out_a, "A"),
                                    (project_b, out_b, "B"),
                                    (project_c, out_c, "standalone")):
            row = real_session_row(db_path, out["session"])
            self.assertIsNotNone(
                row,
                msg=f"PD-6 (recorrido real): la sesión del envelope de "
                    f"{label} ({out['session']!r}) NO existe en el store "
                    "aislado real (la correlación debe ser durable)")
            self.assertEqual(
                row.get("agent"), EXPECTED_ROLE_AGENT,
                msg=f"PD-6/PD-3 (recorrido real): la fila durable de "
                    f"{label} declara agent {row.get('agent')!r}, no el "
                    f"derivado cdad ({EXPECTED_ROLE_AGENT})")
            self.assertEqual(
                row.get("idle_outcome"), "succeeded",
                msg=f"PD-6 (recorrido real): la fila de {label} no quedó "
                    f"idle 'succeeded': {row.get('idle_outcome')!r}")
            self.assertTrue(
                row.get("time_idle"),
                msg=f"PD-6 (recorrido real): la fila de {label} no tiene "
                    "time_idle (señal durable material)")
            self.assertEqual(
                row.get("directory"), str(project.root),
                msg=f"PD-6 (recorrido real): session_v2.directory de "
                    f"{label} no es su proyecto: "
                    f"{row.get('directory')!r} != {str(project.root)!r}")
            rows[label] = row

        # 7. Token (nonce del recorrido real) solo en SUS resultados.
        self.assert_real_token_isolation(
            self, [project_b, project_c], "PD-6 real: A")
        self.assert_real_token_isolation(
            project_b, [self, project_c], "PD-6 real: B")
        self.assert_real_token_isolation(
            project_c, [self, project_b], "PD-6 real: standalone")

        # 8. Recibos durables pendientes (INV-5): entrega ≠ gate.
        for project, label in ((self, "A"), (project_b, "B"),
                               (project_c, "standalone")):
            receipt = project.receipt_doc()
            self.assertEqual(
                receipt.get("semantic_status"), "pending",
                msg=f"PD-6/INV-5 (recorrido real): el recibo de {label} "
                    f"no quedó pending: "
                    f"{receipt.get('semantic_status')!r}")

        # 9. Observaciones VERIFY (spec §5.6) registradas por stdout
        #    (correr con `-s` para capturarlas en el informe).
        verify_e = {
            label: row.get("version") for label, row in rows.items()
            if "version" in row
        }
        print("T3-VERIFY-OBSERVATIONS " + json.dumps({
            "api_info_version": observations["api_info_version"],
            "api_info_auth_mode": observations["auth_mode"],
            "session_v2_version": verify_e,
            "guard_paths": {key: paths[key]
                            for key in GUARD_CHECKED_KEYS
                            if key in paths},
            "standalone_termination": out_c["termination"],
        }, sort_keys=True))
