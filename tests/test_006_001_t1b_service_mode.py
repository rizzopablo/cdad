#!/usr/bin/env python3
"""006-001 T1b RED — Modo `service` configurado (PD-13, PD-14) y las filas
`service` que la enmienda 001 agrega a PD-1, PD-2, PD-3, PD-4 y PD-5.

Contract: docs/specs/006-001-opencode-concurrency-reliability/spec.md v2
(§2.1, §2.2, §2.3b, §2.6; PD-13, PD-14; INV-2, INV-6, INV-10; D-9..D-13) +
plan v2, ficha T1b (docs/specs/006-001-opencode-concurrency-reliability/
plan.md). Plan provenance: plan.md (sha256 2726744566f58af88540f03b6bb1cec
6a73534c6adb43bfbf466206278a1ea72).

Superficie observable: la interfaz STAGEADA invocada como subproceso
(mismo contrato que el resto de la suite), destino `opencode`, proyecto
descartable, `exec-config` de fixture y un BINARIO FALSO PROPIO de este
focal como frontera del proceso. Base reutilizada: `Pd600T1Case`
(tests/test_006_001_t1_selection.py) — proyecto sintético + agentes
derivados publicados + staging de la skill + `dispatch()` con entorno
SIEMPRE explícito. El fake compartido y los focales de T1/T2 NO se
modifican (plan §3, oráculo 3: el focal T1b usa binario falso propio).

PIEZAS DE FIXTURE PROPIAS de este fichero:

1. Binario ENVOLTORIO propio (`T1B_WRAPPER_BINARY_SOURCE`, vía
   `T1bServiceCase.fake_runtime_service`): registra CADA invocación (argv,
   en orden) en su PROPIO log (`t1b-calls.jsonl`); responde ÉL MISMO al
   subcomando `service status` según el escenario de fixture
   (`service-scenario.json`: `stdout` + `rc` — URL, `stopped`, salida
   inesperada, rc≠0) SIN delegar, y delega TODO lo demás (el `--version`
   del preflight y el `run`) por `os.execv` al binario falso REAL
   COMPARTIDO (tests/test_005_009_t2_opencode_adapter.py), con el mismo
   argv/stdin/env (protocolo intacto). El conjunto de tokens prohibidos
   es el REFINADO del plan §3: `service status` está PERMITIDO (es la
   ÚNICA invocación de `service` admitida); `serve`,
   `service start|stop|restart|get|set|unset` y `reload` están PROHIBIDOS
   (INV-2/PD-13). Nunca reinicia, arranca ni reconfigura el servicio ni
   un servidor real.

2. Registro del servicio de fixture (D-11): documento JSON con el esquema
   observado `{id, version, url, pid, password}`, escrito en un directorio
   de ESTADO descartable del fixture (nunca HOME: el test fija
   `XDG_STATE_HOME` en el env del subproceso y el fixture escribe el
   registro en las DOS ubicaciones por defecto plausibles que la spec
   declara — `<state>/service.json` y `<state>/opencode/service.json` —
   con el MISMO contenido). La aserción es de COMPORTAMIENTO (el gate de
   versión proyecta SOLO la clave `version`, PD-14/D-11), no de la ruta
   interna que elija el adaptador (deuda DT-6: la ruta del registro no es
   contrato público). La contraseña centinela del registro
   (SERVICE_SENTINEL_PASSWORD) y la URL del servicio (un puerto CERRADO
   de loopback: nada escucha, así que un adaptador que abriera
   conexiones — PD-14 lo prohíbe — no podría completar el despacho feliz)
   NUNCA deben aparecer en ninguna salida (PD-5/INV-6).

Mapa test → postcondición:

  PD-13 (TestPd13ServiceModeDispatch, 6 métodos):
    test_pd13_running_compatible_dispatches_without_flags (también fija
      la fila `service` corre+compatible de PD-1/§2.2, el gate de versión
      IGUAL de PD-14, y el ORDEN de invocaciones de §2.3 enmienda:
      service status → --version → run)
    test_pd13_stopped_require_false_falls_back_standalone_countably
      (también fija los pares de procedencia del fallback — PD-3 — y que
      NO hay `--version` en el fallback, D-2)
    test_pd13_stopped_require_true_blocks_before_run (D-10)
    test_pd13_unexpected_output_blocks_never_standalone
    test_pd13_service_status_rc_nonzero_blocks
    test_pd13_no_management_invocations_in_any_mode (INV-2 refinada)

  PD-14 (TestPd14ServiceVersionGate, 4 métodos):
    test_pd14_service_version_mismatch_blocks_naming_both_versions
      (además PD-5: la URL del servicio no entra en el diagnóstico)
    test_pd14_service_registry_absent_blocks_never_standalone
    test_pd14_service_version_key_absent_blocks
    test_pd14_service_registry_unparseable_blocks

  PD-3 (TestPd3ServiceProvenance, 2 métodos):
    test_pd3_service_provenance_pairs_on_completed_service_dispatch
    test_pd3_service_status_not_checked_outside_service_mode

  PD-4 (TestPd4SameErrandInServiceMode, 1 método):
    test_pd4_same_errand_in_service_mode

  PD-5 (TestPd5ServiceSecrets, 1 método):
    test_pd5_service_registry_secret_never_in_outputs

  PD-1 (TestPd1ServiceRows, 2 métodos):
    test_pd1_service_ignores_configured_server (fila `service`: `server`
      se ignora y no se comprueba — cero requests a /api/info)
    test_pd1_invalid_service_require_type_blocks (§2.1: tipo inválido →
      blocked antes del despacho, diagnóstico que nombra la clave; la
      validación de TIPO se exige incondicional, el EFECTO de un valor
      VÁLIDO fuera del modo servicio es ignorarlo y registrarlo, D-10 —
      eso no se assertiona aquí)

  PD-2 (dif. enmienda: «`service status` no se invoca en modo servidor ni
  en standalone», SIN método propio): los oráculos de T1 ya lo vigilan —
  `test_pd2_preflight_success_version_then_run_only` exige EXACTAMENTE
  `--version` y `run` en modo servidor con `service` en su
  `NEVER_INVOKED_TOKENS`, y el standalone de T1 exige UNA sola
  invocación; ambos quedan como regresiones declaradas de esta ficha.

RED esperado (comportamiento ausente hoy; cada aserción citada es
AssertionError, nunca import/sintaxis — el adaptador existe desde T1
GREEN):
  - hoy `mode: service` NO pertenece al conjunto válido de T1
    (server|standalone): todo camino de servicio termina `blocked` con un
    diagnóstico que nombra `mode`, SIN invocar NADA (ni `service status`).
    Por eso: los caminos que deben despachar (corre+compatible, fallback
    standalone) fallan en la terminación (`blocked` != `completed`); los
    caminos que deben bloquear por causa del servicio (require true,
    inesperado, rc≠0, versiones) fallan en el CONTEO de invocaciones (hoy
    0 `service status`, se espera exactamente 1) o en el diagnóstico
    (hoy nombra `mode`, se espera la causa/acción del contrato).
  - hoy no existe lector del registro del servicio (D-11): los pares
    nuevos `dispatch_flags=`, `service_status=` y `fallback=` NO existen
    en la procedencia (el registro de worker de T1 lleva los cuatro pares
    de v1, sin los tres nuevos): PD-3 falla por el par ausente (en
    standalone el registro de worker de T1 SÍ existe y lleva
    `mode_requested=` — el marcador lo encuentra y la aserción del par
    nuevo falla).
  - PD-5 (secreto del registro) y PD-4 (encargo sin flags) fallan hoy en
    su precondición (el despacho feliz de modo servicio no existe:
    `blocked` != `completed`), no en las aserciones de secreto/encargo
    (declarado, no oculto).
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import published_packets
from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import durable_session_rows
from test_006_001_t1_selection import (
    EXPECTED_ROLE_AGENT,
    FAST_WAIT,
    MATCHING_CLIENT_SEMVER,
    Pd600T1Case,
    FakeInfoServer,
    closed_port_url,
)

# Versión del SERVICIO de fixture que NO coincide con la del cliente falso
# (semver válido pero distinto: PD-14 fila «distinta»).
SERVICE_MISMATCHED_VERSION = "9.9.9"

# PD-5/PD-14/INV-6: contraseña centinela que vive en el REGISTRO del
# servicio (clave `password` del esquema D-11). NUNCA debe aparecer en
# argv, diagnóstico, registros I8, stderr del adaptador ni recibo.
SERVICE_SENTINEL_PASSWORD = "cdad-006-001-service-registry-password"

SERVICE_STATUS_FORBIDDEN_SUBCOMMANDS = (
    "start", "stop", "restart", "get", "set", "unset")  # INV-2/PD-13


# ------------------------------------------------- binario envoltorio (T1b)


T1B_WRAPPER_BINARY_SOURCE = '''#!/usr/bin/env python3
# Binario ENVOLTORIO de fixture (tests/test_006_001_t1b_service_mode.py):
# registra CADA invocación (argv, en orden) en su PROPIO log
# (t1b-calls.jsonl); responde ÉL MISMO a `service status` según el
# escenario de fixture (<fake>/service-scenario.json: stdout + rc) SIN
# delegar — URL (corre), `stopped` (no corre), salida inesperada o rc≠0 —
# y delega TODO lo demás (el --version del preflight y el run) por
# os.execv al binario falso REAL compartido
# (tests/test_005_009_t2_opencode_adapter.py) con el MISMO argv/stdin/env
# (protocolo intacto). Nunca gestiona el servicio: no existe escenario de
# fixture para start/stop/restart/get/set/unset ni para reload.
import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent         # <fake>/bin
_FAKE = _HERE.parent                            # <fake>
_LOG = _FAKE / "t1b-calls.jsonl"
_SCENARIO = _FAKE / "service-scenario.json"
_REAL_BINARY = _HERE / "opencode-fake-real"

existing = 0
if _LOG.is_file():
    existing = sum(
        1 for line in _LOG.read_text(encoding="utf-8").splitlines()
        if line.strip())

_argv = sys.argv[1:]
with _LOG.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps({"index": existing, "argv": _argv},
                        sort_keys=True) + "\\n")

if _argv[:2] == ["service", "status"]:
    if not _SCENARIO.is_file():
        sys.stderr.write(
            "fixture t1b: invocacion service status sin escenario de "
            "fixture (ningun test debia invocarlo aca)\\n")
        sys.exit(3)
    scenario = json.loads(_SCENARIO.read_text(encoding="utf-8"))
    sys.stdout.write(scenario.get("stdout", ""))
    sys.stdout.flush()
    sys.exit(int(scenario.get("rc", 0)))

os.execv(str(_REAL_BINARY), [str(_REAL_BINARY)] + _argv)
'''


def _prov_get(provenance_text: str, key: str) -> str | None:
    """Valor del par `clave=valor` (pares `; `-separados de §2.6) en un
    texto de procedencia, o None si el par no está."""
    for part in provenance_text.split(";"):
        part = part.strip()
        if part.startswith(key + "="):
            return part[len(key) + 1:]
    return None


# ------------------------------------------------------- fixture base T1b


class T1bServiceCase(Pd600T1Case):
    """Base del focal T1b: añade el binario envoltorio PROPIO (con `service
    status` respondido por el propio envoltorio), el registro del servicio
    de fixture (D-11) en un directorio de estado descartable y el env
    `XDG_STATE_HOME` SIEMPRE explícito en el despacho."""

    def fake_runtime_service(self, name: str,
                             *, variant: str = "succeeded") -> dict:
        fake = self.fake_runtime(name, variant=variant)
        binary = fake["binary"]
        real_binary = binary.parent / "opencode-fake-real"
        binary.rename(real_binary)
        binary.write_text(T1B_WRAPPER_BINARY_SOURCE, encoding="utf-8")
        binary.chmod(0o755)
        fake["wrapper_calls"] = fake["dir"] / "t1b-calls.jsonl"
        fake["scenario"] = fake["dir"] / "service-scenario.json"
        state = fake["dir"] / "state-home"
        state.mkdir(parents=True, exist_ok=True)
        fake["state"] = state
        # URL del servicio: puerto CERRADO de loopback (nada escucha). Si
        # el adaptador abriera conexiones para observar la versión (PD-14
        # lo prohíbe: proyección de una sola clave, sin red), el despacho
        # feliz no podría completar: la prueba lo detecta.
        fake["service_url"] = closed_port_url()
        fake["registry"] = state / "opencode" / "service.json"
        return fake

    # -- escenarios de `service status` ------------------------------------

    def set_service_scenario(self, fake: dict, *, stdout: str,
                             rc: int = 0) -> None:
        fake["scenario"].write_text(
            json.dumps({"stdout": stdout, "rc": rc}, sort_keys=True) + "\n",
            encoding="utf-8")

    def scenario_running(self, fake: dict) -> None:
        self.set_service_scenario(fake, stdout=fake["service_url"] + "\n")

    def scenario_stopped(self, fake: dict) -> None:
        self.set_service_scenario(fake, stdout="stopped\n")

    # -- registro del servicio (D-11) --------------------------------------

    def write_service_registry(self, fake: dict, *, version=None,
                               omit_version: bool = False,
                               raw: bool = False,
                               with_password: bool = True) -> None:
        """Escribe el registro del servicio en las DOS ubicaciones
        plausibles del directorio de estado descartable (mismo contenido):
        la ruta interna no es contrato público (DT-6); lo observable es el
        COMPORTAMIENTO del gate (proyección solo de `version`)."""
        if raw:
            text = "opencode-fake-service-registry: no es JSON (fixture)\n"
        else:
            doc = {"id": "opencode-service-fixture", "pid": 4242,
                   "url": fake["service_url"]}
            if not omit_version:
                doc["version"] = version
            if with_password:
                doc["password"] = SERVICE_SENTINEL_PASSWORD
            text = json.dumps(doc, indent=2, sort_keys=True) + "\n"
        for rel in (("opencode", "service.json"), ("service.json",)):
            path = fake["state"].joinpath(*rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    # -- despacho y observación --------------------------------------------

    def dispatch_service(self, fake: dict, *,
                         env_overrides: dict | None = None,
                         cwd: Path | None = None) -> subprocess.CompletedProcess:
        overrides = {"XDG_STATE_HOME": str(fake["state"])}
        if env_overrides:
            overrides.update(env_overrides)
        return self.dispatch(fake, env_overrides=overrides, cwd=cwd)

    def service_status_calls(self, fake: dict) -> list[dict]:
        return [call for call in self.wrapper_calls(fake)
                if call["argv"][:2] == ["service", "status"]]

    def run_argv(self, fake: dict, label: str) -> list[str]:
        calls = [call for call in self.wrapper_calls(fake)
                 if call["argv"] and call["argv"][0] == "run"]
        self.assertEqual(
            len(calls), 1,
            msg=f"{label}: el número de invocaciones `run` no es UNA "
                f"(PD-9: como máximo una por invocación de la interfaz): "
                f"{[call['argv'] for call in calls]!r}")
        return calls[0]["argv"]

    def assert_exactly_one_service_status(self, fake: dict,
                                          label: str) -> None:
        calls = self.service_status_calls(fake)
        self.assertEqual(
            len(calls), 1,
            msg=f"{label}: `service status` no se invocó EXACTAMENTE una "
                f"vez antes del despacho (PD-13): "
                f"{[call['argv'] for call in calls]!r}; todas las "
                f"invocaciones: {[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assertEqual(
            calls[0]["argv"], ["service", "status"],
            msg=f"{label}: la invocación de `service` no es el subcomando "
                f"de SOLO-LECTURA `status` (INV-2/PD-13): "
                f"{calls[0]['argv']!r}")

    def assert_no_management_invocations(self, fake: dict,
                                         label: str) -> None:
        for call in self.wrapper_calls(fake):
            argv = call["argv"]
            for token in ("serve", "reload"):
                self.assertNotIn(
                    token, argv,
                    msg=f"{label}: una invocación lleva {token!r} (INV-2: "
                        f"CDAD no arranca, recarga ni gestiona servidores "
                        f"ni el servicio): {argv!r}")
            if argv and argv[0] == "service":
                self.assertEqual(
                    argv, ["service", "status"],
                    msg=f"{label}: la única invocación de `service` "
                        f"admitida es `service status`; jamás "
                        f"{SERVICE_STATUS_FORBIDDEN_SUBCOMMANDS} (INV-2/"
                        f"PD-13): {argv!r}")

    def assert_never_standalone(self, fake: dict, label: str) -> None:
        for call in self.wrapper_calls(fake):
            self.assertNotIn(
                "--standalone", call["argv"],
                msg=f"{label}: se abrió un standalone pese a que el "
                    f"servicio corre (INV-10: un servicio vivo no admite "
                    f"otro escritor por esta vía): {call['argv']!r}")


# ------------------------------------------------------------------ PD-13


class TestPd13ServiceModeDispatch(T1bServiceCase):
    """PD-13: con `mode: service`, `service status` exactamente una vez
    antes del despacho; corre+compatible → despacho SIN flags; no corre +
    require false → standalone con fallback declarado y contable; no corre
    + require true → blocked; respuesta inesperada → blocked, nunca
    standalone; ninguna invocación de gestión del servicio."""

    def test_pd13_running_compatible_dispatches_without_flags(self) -> None:
        """PD-13 (+ PD-1 fila corre+compatible, + PD-14 versión IGUAL):
        `service status` informa URL y la versión del registro coincide con
        la del cliente → despacho `completed` SIN `--server` ni
        `--standalone`; invocaciones EXACTAMENTE tres, en orden: `service
        status`, `--version`, `run` (§2.3 enmienda; D-2: `--version` solo
        si el servicio corre). RED hoy: `mode: service` es inválido para el
        adaptador vigente → `blocked` sin invocar nada."""
        fake = self.fake_runtime_service("pd13-running-compatible")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 corre y compatible")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"servicio corre y versión compatible: la terminación no "
                f"es `completed` con despacho SIN flags (PD-13/§2.2): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        calls = self.wrapper_calls(fake)
        self.assertEqual(
            len(calls), 3,
            msg=f"modo servicio compatible: las invocaciones del binario "
                f"no son EXACTAMENTE tres (service status, --version, run; "
                f"§2.3 enmienda): {[c['argv'] for c in calls]!r}")
        self.assertEqual(
            calls[0]["argv"], ["service", "status"],
            msg=f"la PRIMERA invocación no es `service status` (PD-13/§2.3b "
                f"punto 1): {calls[0]['argv']!r}")
        self.assertIn(
            "--version", calls[1]["argv"],
            msg=f"la SEGUNDA invocación no es `--version` (PD-14: versión "
                f"del cliente para la comparación de §2.3b punto 2): "
                f"{calls[1]['argv']!r}")
        self.assertEqual(
            calls[2]["argv"][0], "run",
            msg=f"la TERCERA invocación no es el despacho `run` (PD-13): "
                f"{calls[2]['argv']!r}")
        run_argv = calls[2]["argv"]
        self.assertNotIn(
            "--server", run_argv,
            msg=f"el despacho en modo servicio lleva --server (PD-13: sin "
                f"flags; el cliente usa el servicio como lo diseña el "
                f"runtime): {run_argv!r}")
        self.assertNotIn(
            "--standalone", run_argv,
            msg=f"el despacho en modo servicio lleva --standalone (PD-13: "
                f"sin flags): {run_argv!r}")

    def test_pd13_stopped_require_false_falls_back_standalone_countably(
            self) -> None:
        """PD-13 (+ PD-1 fila no corre+require false, + PD-3 pares del
        fallback, + D-2): `service status` informa `stopped` y
        `service.require: false` → despacho `--standalone` (sin `--server`)
        con el fallback DECLARADO y CONTABLE: `mode_requested=service;
        mode_effective=standalone; fallback=service-unavailable;
        service_status=stopped; dispatch_flags=--standalone`, y el
        diagnóstico nombra la causa («servicio no disponible»). Sin
        `--version` en el fallback (D-2: la versión del cliente solo se
        observa si el servicio corre). RED hoy: `mode: service` → blocked
        sin invocar nada."""
        fake = self.fake_runtime_service("pd13-stopped-fallback")
        self.scenario_stopped(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(
            fake, {"mode": "service", "service": {"require": False},
                   "wait": FAST_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 stopped + require false")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"servicio no corre con require false: la terminación no "
                f"es el despacho standalone del fallback declarado "
                f"(PD-13/§2.2): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        calls = self.wrapper_calls(fake)
        self.assertEqual(
            len(calls), 2,
            msg=f"fallback a standalone: las invocaciones no son "
                f"EXACTAMENTE dos (service status y run; SIN --version, "
                f"D-2): {[c['argv'] for c in calls]!r}")
        self.assertEqual(
            calls[0]["argv"], ["service", "status"],
            msg=f"la PRIMERA invocación no es `service status` (PD-13): "
                f"{calls[0]['argv']!r}")
        self.assertEqual(
            calls[1]["argv"][0], "run",
            msg=f"la SEGUNDA invocación no es el despacho `run` (PD-13): "
                f"{calls[1]['argv']!r}")
        run_argv = calls[1]["argv"]
        self.assertIn(
            "--standalone", run_argv,
            msg=f"el fallback no despacha standalone (PD-13:stopped + "
                f"require false → --standalone): {run_argv!r}")
        self.assertNotIn(
            "--server", run_argv,
            msg=f"el fallback lleva --server (PD-13: standalone con un "
                f"flag solo): {run_argv!r}")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="el fallback declarado no dejó registro de worker en el "
                "ledger (PD-3: fallback CONTABLE)")
        runtime_prov = str(
            worker_records[0].get("provenance", {}).get("runtime", ""))
        for pair, expected in (
                ("mode_requested", "service"),
                ("mode_effective", "standalone"),
                ("dispatch_flags", "--standalone"),
                ("service_status", "stopped"),
                ("fallback", "service-unavailable")):
            self.assertEqual(
                _prov_get(runtime_prov, pair), expected,
                msg=f"procedencia del fallback: el par {pair!r} no vale "
                    f"{expected!r} (PD-3/§2.6/§2.3b punto 3): "
                    f"{runtime_prov!r}")

        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "servicio no disponible", diagnosis.lower(),
            msg=f"el diagnóstico no nombra la causa del fallback "
                f"(«servicio no disponible», PD-13): {diagnosis!r}")

    def test_pd13_stopped_require_true_blocks_before_run(self) -> None:
        """PD-13 (D-10: variante estricta): `service status` informa
        `stopped` con `service.require: true` → `blocked` ANTES de invocar
        `run`, con la acción siguiente en el diagnóstico (arrancarlo lo
        decide el operador o el dueño, o declarar `mode: standalone`).
        RED hoy: `mode: service` → blocked por causa ajena (mode
        inválido) SIN invocar `service status` (0 != 1)."""
        fake = self.fake_runtime_service("pd13-stopped-strict")
        self.scenario_stopped(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.patch_config(
            fake, {"mode": "service", "service": {"require": True},
                   "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 stopped + require true")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"servicio no corre con require true: la terminación no "
                f"es `blocked` (PD-13/D-10): {out['termination']!r}")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"require true: se invocó `run` pese al servicio parado "
                f"(PD-13: blocked ANTES de invocar run): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assert_exactly_one_service_status(fake, "PD-13 require true")
        diagnosis = out.get("diagnosis") or ""
        for token in ("standalone", "servicio"):
            self.assertIn(
                token, diagnosis.lower(),
                msg=f"require true: el diagnóstico no nombra la acción "
                    f"siguiente (arrancar el servicio — del operador o del "
                    f"dueño — o declarar `mode: standalone`; PD-13/§2.3b "
                    f"punto 3): {diagnosis!r}")

    def test_pd13_unexpected_output_blocks_never_standalone(self) -> None:
        """PD-13: `service status` con salida NO reconocible (más de una
        línea, ninguna URL ni `stopped`) → `blocked`; NUNCA standalone
        («no se puede afirmar que el servicio no corre»). RED hoy:
        `mode: service` → blocked por causa ajena, sin invocar nada."""
        fake = self.fake_runtime_service("pd13-unexpected-output")
        self.set_service_scenario(
            fake, stdout="fixtura linea no reconocible\nsegunda linea\n")
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 salida inesperada")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"salida inesperada de `service status`: la terminación no "
                f"es `blocked` (PD-13/§2.3b: interpretación cerrada): "
                f"{out['termination']!r}")
        self.assert_exactly_one_service_status(fake, "PD-13 inesperado")
        self.assert_never_standalone(fake, "PD-13 inesperado")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"salida inesperada: se invocó `run` (PD-13: blocked sin "
                f"despachar): {[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertTrue(
            diagnosis.strip(),
            msg="salida inesperada: diagnóstico vacío (PD-13: diagnóstico "
                "accionable)")

    def test_pd13_service_status_rc_nonzero_blocks(self) -> None:
        """PD-13: `service status` con rc ≠ 0 → respuesta inesperada →
        `blocked`, nunca standalone (aunque la salida parezca una URL).
        RED hoy: `mode: service` → blocked por causa ajena, sin invocar
        nada."""
        fake = self.fake_runtime_service("pd13-rc-nonzero")
        self.set_service_scenario(fake, stdout=fake["service_url"] + "\n",
                                  rc=2)
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 rc != 0")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"rc != 0 de `service status`: la terminación no es "
                f"`blocked` (PD-13: respuesta inesperada): "
                f"{out['termination']!r}")
        self.assert_exactly_one_service_status(fake, "PD-13 rc != 0")
        self.assert_never_standalone(fake, "PD-13 rc != 0")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"rc != 0: se invocó `run` (PD-13: blocked sin despachar): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")

    def test_pd13_no_management_invocations_in_any_mode(self) -> None:
        """PD-13 (INV-2 refinada): en el camino feliz del modo servicio,
        NINGUNA invocación del binario lleva `serve`, `service
        start|stop|restart|get|set|unset` ni `reload`; la ÚNICA invocación
        de `service` es `service status`. RED hoy: no hay camino de modo
        servicio (precondición `completed` falla)."""
        fake = self.fake_runtime_service("pd13-no-management")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-13 sin gestión del servicio")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición: el despacho en modo servicio no llegó a "
                f"completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assert_no_management_invocations(
            fake, "PD-13 sin gestión del servicio")
        self.assert_exactly_one_service_status(
            fake, "PD-13 sin gestión del servicio")


# ------------------------------------------------------------------ PD-14


class TestPd14ServiceVersionGate(T1bServiceCase):
    """PD-14: con el servicio corriendo, la versión se observa por el
    mecanismo de D-11 (proyección de la sola clave `version` del registro,
    nunca la contraseña, nunca la URL, sin conexiones). Igual → despacha
    sin flags (fijado en PD-13); distinta o no verificable → `blocked`,
    NUNCA standalone (el servicio corre: un standalone al lado sería un
    escritor más, INV-10)."""

    def test_pd14_service_version_mismatch_blocks_naming_both_versions(
            self) -> None:
        """PD-14 (versión distinta): `blocked`; el diagnóstico nombra las
        DOS versiones y la acción siguiente (servicio compatible, o `mode`
        explícito); NUNCA standalone; sin `run`. Además PD-5: la URL del
        servicio no entra en el diagnóstico. RED hoy: `mode: service` →
        blocked por causa ajena (mode inválido), diagnóstico sin las
        versiones y sin invocar `service status` (0 != 1)."""
        fake = self.fake_runtime_service("pd14-version-mismatch")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=SERVICE_MISMATCHED_VERSION)
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-14 versión distinta")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"versión del servicio distinta de la del cliente: la "
                f"terminación no es `blocked` (PD-14/§2.3b punto 2): "
                f"{out['termination']!r}")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"versión distinta: se invocó `run` pese al gate (PD-14): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assert_exactly_one_service_status(fake, "PD-14 distinta")
        self.assert_never_standalone(fake, "PD-14 distinta")
        diagnosis = out.get("diagnosis") or ""
        for version in (MATCHING_CLIENT_SEMVER, SERVICE_MISMATCHED_VERSION):
            self.assertIn(
                version, diagnosis,
                msg=f"versión distinta: el diagnóstico no nombra la "
                    f"versión {version!r} (PD-14: nombra las dos "
                    f"versiones): {diagnosis!r}")
        self.assertIn(
            "standalone", diagnosis.lower(),
            msg=f"versión distinta: el diagnóstico no nombra la acción "
                f"siguiente (servicio compatible, o un `mode` explícito "
                f"como standalone; PD-14): {diagnosis!r}")
        self.assertNotIn(
            fake["service_url"], diagnosis,
            msg=f"la URL del servicio aparece en el diagnóstico (PD-5/"
                f"PD-14: la salida de `service status` se descarta salvo "
                f"el discriminante; la URL no entra en ninguna salida): "
                f"{diagnosis!r}")

    def test_pd14_service_registry_absent_blocks_never_standalone(
            self) -> None:
        """PD-14 (registro AUSENTE → versión no verificable): `blocked`
        («versión del servicio no verificable»), NUNCA standalone, sin
        `run`. Fail closed (D-11). RED hoy: blocked por causa ajena, sin
        invocar nada."""
        fake = self.fake_runtime_service("pd14-registry-absent")
        self.scenario_running(fake)
        # SIN write_service_registry: el directorio de estado descartable
        # queda sin registro (nunca el HOME real).
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-14 registro ausente")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"registro del servicio ausente: la terminación no es "
                f"`blocked` (PD-14/D-11: fail closed, nunca standalone): "
                f"{out['termination']!r}")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"registro ausente: se invocó `run` (PD-14: blocked sin "
                f"despachar): {[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assert_exactly_one_service_status(fake, "PD-14 sin registro")
        self.assert_never_standalone(fake, "PD-14 sin registro")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "no verificable", diagnosis.lower(),
            msg=f"registro ausente: el diagnóstico no declara la versión "
                f"del servicio como NO VERIFICABLE (PD-14/§2.3b): "
                f"{diagnosis!r}")

    def test_pd14_service_version_key_absent_blocks(self) -> None:
        """PD-14 (clave `version` AUSENTE del registro → no verificable):
        `blocked`, nunca standalone. RED hoy: blocked por causa ajena, sin
        invocar nada."""
        fake = self.fake_runtime_service("pd14-key-absent")
        self.scenario_running(fake)
        self.write_service_registry(fake, omit_version=True)
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-14 clave ausente")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"registro sin la clave `version`: la terminación no es "
                f"`blocked` (PD-14: no verificable, fail closed): "
                f"{out['termination']!r}")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"clave ausente: se invocó `run` (PD-14): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assert_never_standalone(fake, "PD-14 clave ausente")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "no verificable", diagnosis.lower(),
            msg=f"clave ausente: el diagnóstico no declara la versión del "
                f"servicio como NO VERIFICABLE (PD-14): {diagnosis!r}")

    def test_pd14_service_registry_unparseable_blocks(self) -> None:
        """PD-14 (registro NO PARSEABLE → no verificable): `blocked`,
        nunca standalone. RED hoy: blocked por causa ajena, sin invocar
        nada."""
        fake = self.fake_runtime_service("pd14-registry-unparseable")
        self.scenario_running(fake)
        self.write_service_registry(fake, raw=True)
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-14 registro no parseable")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"registro del servicio no parseable: la terminación no es "
                f"`blocked` (PD-14: no verificable, fail closed): "
                f"{out['termination']!r}")
        self.assertFalse(
            any(call["argv"] and call["argv"][0] == "run"
                for call in self.wrapper_calls(fake)),
            msg=f"registro no parseable: se invocó `run` (PD-14): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        self.assert_never_standalone(fake, "PD-14 no parseable")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "no verificable", diagnosis.lower(),
            msg=f"registro no parseable: el diagnóstico no declara la "
                f"versión del servicio como NO VERIFICABLE (PD-14): "
                f"{diagnosis!r}")


# ------------------------------------------------------------------- PD-3


class TestPd3ServiceProvenance(T1bServiceCase):
    """PD-3: la procedencia de §2.6 en el modo servicio — pares nuevos
    `dispatch_flags=`, `service_status=` y `fallback=` con los valores del
    camino, `service` en `mode_requested`/`mode_effective`,
    `server_version=` con la versión del servicio observada, y los pares
    de sesión intactos con `store_reads=`/`prior_check_reads=` AL FINAL."""

    def test_pd3_service_provenance_pairs_on_completed_service_dispatch(
            self) -> None:
        """PD-3 (camino completado en modo servicio): registro de worker
        con la forma I8 cerrada y los SIETE pares de `provenance.runtime`
        con los valores del modo servicio (`mode_requested=service;
        mode_effective=service; client_version=1.0.0;
        server_version=1.0.0; dispatch_flags=none; service_status=running;
        fallback=none`). RED hoy: el camino ni siquiera despacha (blocked
        por mode inválido) y ningún registro de worker nuevo existe."""
        fake = self.fake_runtime_service("pd3-service-completed")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-3 procedencia en modo servicio")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición: el despacho en modo servicio no llegó a "
                f"completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="camino `completed` en modo servicio: ningún registro "
                "NUEVO del ledger I8 lleva la procedencia de §2.6 "
                "(`mode_requested=`) (PD-3)")
        data = worker_records[0]
        self.assertEqual(
            set(data), I8_RECORD_KEYS,
            msg=f"la forma del registro de worker no es la cerrada I8 "
                f"(D-5: mismo esquema que la interfaz): {sorted(data)}")
        provenance = data["provenance"]
        runtime_prov = str(provenance.get("runtime", ""))
        session_prov = str(provenance.get("session", ""))
        for pair, expected in (
                ("mode_requested", "service"),
                ("mode_effective", "service"),
                ("client_version", MATCHING_CLIENT_SEMVER),
                ("server_version", MATCHING_CLIENT_SEMVER),
                ("dispatch_flags", "none"),
                ("service_status", "running"),
                ("fallback", "none")):
            self.assertEqual(
                _prov_get(runtime_prov, pair), expected,
                msg=f"provenance.runtime: el par {pair!r} no vale "
                    f"{expected!r} (PD-3/§2.6: valores del modo servicio, "
                    f"`server_version` = versión del servicio observada "
                    f"por D-11): {runtime_prov!r}")
        for pair in ("store=", "row=", "store_reads=",
                     "prior_check_reads="):
            self.assertIn(
                pair, session_prov,
                msg=f"provenance.session no lleva el par {pair!r} (§2.6: "
                    f"forma intacta): {session_prov!r}")
        last_pair = session_prov.rstrip().split(";")[-1].strip()
        self.assertTrue(
            last_pair.startswith("prior_check_reads="),
            msg=f"los pares de sesión no terminan en `prior_check_reads=` "
                f"(PD-3/§2.6: store_reads/prior_check_reads quedan AL "
                f"FINAL; el parseo por subcadena de T2 lo depende): "
                f"{session_prov!r}")

    def test_pd3_service_status_not_checked_outside_service_mode(
            self) -> None:
        """PD-3 (§2.6: `service_status` es `not-checked` fuera del modo
        servicio): en un despacho standalone el registro de worker lleva
        `service_status=not-checked`, `dispatch_flags=--standalone` y
        `fallback=none`. RED hoy: el registro de worker standalone de T1
        existe y lleva `mode_requested=`, pero SIN los pares nuevos de la
        enmienda."""
        fake = self.fake_runtime_service("pd3-standalone-not-checked")
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "standalone", "wait": FAST_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-3 not-checked fuera del modo servicio")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición (standalone, ya GREEN hoy): el despacho no "
                f"llegó a completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        worker_records = self.worker_records_with_marker(records_before)
        self.assertTrue(
            worker_records,
            msg="standalone: ningún registro de worker con la procedencia "
                "de §2.6 (PD-3)")
        runtime_prov = str(
            worker_records[0].get("provenance", {}).get("runtime", ""))
        for pair, expected in (
                ("mode_requested", "standalone"),
                ("dispatch_flags", "--standalone"),
                ("service_status", "not-checked"),
                ("fallback", "none")):
            self.assertEqual(
                _prov_get(runtime_prov, pair), expected,
                msg=f"provenance.runtime en standalone: el par {pair!r} no "
                    f"vale {expected!r} (PD-3/§2.6: pares nuevos de la "
                    f"enmienda, `not-checked` fuera del modo servicio): "
                    f"{runtime_prov!r}")
        self.assertEqual(
            self.service_status_calls(fake), [],
            msg="standalone: se invocó `service status` (§2.3 enmienda: "
                "solo en modo servicio; PD-2 dif. enmienda)")


# ------------------------------------------------------------------- PD-4


class TestPd4SameErrandInServiceMode(T1bServiceCase):
    """PD-4 (dif. enmienda): en modo servicio (despacho SIN flags) se
    cumple lo mismo que hoy se verifica en standalone: sha256 de stdin =
    PACKET.md, --agent/--session/--model/--auto, PWD = raíz del proyecto,
    identidad durable verificada, `completed` → receive `pending`."""

    def test_pd4_same_errand_in_service_mode(self) -> None:
        """PD-4: con el servicio corre+compatible, el despacho SIN flags
        transporta el MISMO encargo que standalone. RED hoy: el despacho en
        modo servicio no existe (`blocked` != `completed`): la
        precondición falla antes que las aserciones del encargo."""
        fake = self.fake_runtime_service("pd4-service-errand")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        config = self.patch_config(
            fake, {"mode": "service", "wait": FAST_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_service(fake, cwd=self.root)
        out = self.envelope(proc, "PD-4 encargo en modo servicio")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición de las aserciones del encargo: el despacho "
                f"en modo servicio no llegó a completed: "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        call = self.packet_call(fake, "PD-4 encargo en modo servicio")
        argv = call["argv"]

        # alternativas de modo: NINGUNA (despacho sin flags).
        self.assertNotIn(
            "--server", argv,
            msg=f"el despacho en modo servicio lleva --server (PD-4/PD-13): "
                f"{argv!r}")
        self.assertNotIn(
            "--standalone", argv,
            msg=f"el despacho en modo servicio lleva --standalone "
                f"(PD-4/PD-13): {argv!r}")

        # sha256 de stdin == PACKET.md publicado.
        published = published_packets(self.root)[self.packet_id]
        import hashlib
        expected_sha = hashlib.sha256(published).hexdigest()
        self.assertEqual(
            call["packet"]["sha256"], expected_sha,
            msg="el paquete transportado en modo servicio no es "
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
                "reportó haber escrito (PD-4)")
        self.assertEqual(
            out["session"], session_value,
            msg="la sesión declarada por el envelope no es la del argv "
                "(PD-4)")

        # --model, si está configurado.
        if config.get("model"):
            self.assertIn(
                "--model", argv,
                msg=f"hay `model` en la config pero el argv no lleva "
                    f"--model (PD-4): {argv!r}")
            self.assertEqual(
                argv[argv.index("--model") + 1], config["model"],
                msg=f"--model no lleva el valor configurado (PD-4): "
                    f"{argv!r}")

        # --auto según la config (por defecto activado).
        self.assertIn(
            "--auto", argv,
            msg=f"sin `auto: false` en la config, el argv no lleva --auto "
                f"(PD-4): {argv!r}")

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
                f"(PD-4): {[row.get('agent') for row in rows]!r}")

        # completed → receive con semantic_status pending.
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()
        self.assert_final_text_in_delivery()
        self.assert_attempt_is_in_ledger(out, records_before)


# ------------------------------------------------------------------- PD-5


class TestPd5ServiceSecrets(T1bServiceCase):
    """PD-5 (dif. enmienda): la salida de `service status` (que contiene la
    URL del servicio) se descarta salvo el discriminante; ni la URL del
    servicio ni la contraseña centinela del REGISTRO del servicio entran en
    argv, diagnóstico, registros I8, stderr del adaptador ni recibo. La
    contraseña nunca va en argv."""

    def test_pd5_service_registry_secret_never_in_outputs(self) -> None:
        """PD-5: en el despacho feliz de modo servicio, ni la contraseña
        centinela del registro (SERVICE_SENTINEL_PASSWORD) ni la URL del
        servicio aparecen en: stdout/stderr de la interfaz, diagnóstico,
        registros I8 nuevos, recibo, ni en NINGÚN argv (el despacho no lleva
        flags y la URL del servicio jamás es argumento). RED hoy: el camino
        feliz no existe (`blocked` != `completed`); las aserciones de
        secreto pasarían hoy trivialmente (nada se lee) — declarado, no
        oculto."""
        fake = self.fake_runtime_service("pd5-service-secrets")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER,
                                    with_password=True)
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "service", "wait": FAST_WAIT})
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-5 secretos del servicio")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición: el despacho en modo servicio no llegó a "
                f"completed: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        service_url = fake["service_url"]
        for output_name, text in (
                ("stdout", proc.stdout), ("stderr", proc.stderr),
                ("diagnosis", out.get("diagnosis") or "")):
            self.assertNotIn(
                SERVICE_SENTINEL_PASSWORD, text,
                msg=f"la contraseña centinela del registro del servicio "
                    f"aparece en {output_name} (PD-5/INV-6)")
            self.assertNotIn(
                service_url, text,
                msg=f"la URL del servicio aparece en {output_name} (PD-5: "
                    f"la salida de `service status` se descarta salvo el "
                    f"discriminante)")

        for _stem, path in self._new_dispatch_records(
                records_before).items():
            record_text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                SERVICE_SENTINEL_PASSWORD, record_text,
                msg=f"el registro I8 {path} contiene la contraseña del "
                    f"registro del servicio (PD-5: el lector de D-11 es "
                    f"una proyección de la sola clave `version`)")
            self.assertNotIn(
                service_url, record_text,
                msg=f"el registro I8 {path} contiene la URL del servicio "
                    f"(PD-5)")

        receipt_path = self.results_base() / "receipt.json"
        if receipt_path.is_file():
            receipt_text = receipt_path.read_text(encoding="utf-8")
            self.assertNotIn(
                SERVICE_SENTINEL_PASSWORD, receipt_text,
                msg="el recibo contiene la contraseña del registro del "
                    "servicio (PD-5)")
            self.assertNotIn(
                service_url, receipt_text,
                msg="el recibo contiene la URL del servicio (PD-5)")

        for call in self.wrapper_calls(fake):
            argv = call["argv"]
            self.assertNotIn(
                SERVICE_SENTINEL_PASSWORD, argv,
                msg=f"la contraseña del registro del servicio aparece en "
                    f"un argv (PD-5: nunca en argv): {argv!r}")
            self.assertNotIn(
                service_url, argv,
                msg=f"la URL del servicio aparece en un argv (PD-5: en "
                    f"modo servicio no hay flag de servidor): {argv!r}")


# ------------------------------------------------------------------- PD-1


class TestPd1ServiceRows(T1bServiceCase):
    """PD-1 (filas `service` de §2.2 y §2.1): el `server` declarado se
    ignora y no se comprueba en modo servicio; un `service.require` no
    booleano bloquea antes del despacho con diagnóstico que nombra la
    clave."""

    def test_pd1_service_ignores_configured_server(self) -> None:
        """PD-1 (fila `service` con `server` declarado): `server` se
        ignora — no se usa, no se comprueba (cero requests a /api/info) —
        y el despacho va SIN flags. RED hoy: `mode: service` → blocked sin
        invocar nada."""
        info_server = FakeInfoServer(
            body=json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode())
        self.addCleanup(info_server.stop)
        fake = self.fake_runtime_service("pd1-service-ignores-server")
        self.scenario_running(fake)
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(
            fake, {"mode": "service", "server": info_server.url,
                   "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-1 service ignora server")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"mode=service con `server` declarado: la terminación no "
                f"es el despacho sin flags (PD-1/§2.2: `server` se "
                f"ignora): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assertEqual(
            info_server.requests, [],
            msg=f"mode=service: se comprobó el `server` declarado (PD-1/"
                f"§2.2: se ignora, no se usa y no se comprueba): "
                f"{info_server.requests!r}")
        run_argv = self.run_argv(fake, "PD-1 service ignora server")
        self.assertNotIn(
            "--server", run_argv,
            msg=f"mode=service con `server` declarado: el argv lleva "
                f"--server (PD-1): {run_argv!r}")
        self.assertNotIn(
            "--standalone", run_argv,
            msg=f"mode=service compatible: el argv lleva --standalone "
                f"(PD-1): {run_argv!r}")

    def test_pd1_invalid_service_require_type_blocks(self) -> None:
        """PD-1 (§2.1: `service.require` no booleano → `blocked` antes del
        despacho, diagnóstico que nombra la clave; no se invoca nada). La
        validación de TIPO rige en todo modo (§2.1, lista incondicional);
        el EFECTO de un valor válido fuera del modo servicio es ignorarlo
        (D-10), no assertionado aquí. RED hoy: o la config inválida se
        tolera y despacha standalone a `completed`, o se bloquea por una
        causa ajena cuyo diagnóstico no nombra `service.require` — en
        ambos casos una aserción de este método falla."""
        fake = self.fake_runtime_service("pd1-invalid-require")
        self.patch_config(
            fake, {"mode": "standalone", "service": {"require": "yes"},
                   "wait": FAST_WAIT})

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PD-1 service.require inválido")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"`service.require` no booleano: la terminación no es "
                f"`blocked` antes del despacho (PD-1/§2.1): "
                f"{out['termination']!r}")
        self.assertEqual(
            self.wrapper_calls(fake), [],
            msg=f"`service.require` inválido: se invocó el binario (PD-1: "
                f"blocked SIN invocar nada): "
                f"{[c['argv'] for c in self.wrapper_calls(fake)]!r}")
        diagnosis = out.get("diagnosis") or ""
        self.assertIn(
            "service.require", diagnosis,
            msg=f"`service.require` inválido: el diagnóstico no nombra la "
                f"clave `service.require` (PD-1/§2.1): {diagnosis!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
