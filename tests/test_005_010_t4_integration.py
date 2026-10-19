#!/usr/bin/env python3
"""005-010 T4 RED — Prueba de integración OPCIONAL contra el binario REAL de
OpenCode (PD-8 enmendada al aprobar; INV-8, INV-9, INV-10).

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-8 §2, §11
enmienda) + plan.md §T4. Consume `senal-durable-sqlite` (T1, GREEN) y
`modo-carga-invocacion` (T2, GREEN): la señal durable es el store SQLite real
del runtime, la identidad se verifica desde la fila y la invocación usa
--standalone/--auto por defecto del adaptador.

REFORMULACIÓN DECLARADA (006-003 U4/PD-3b, D3 — el modelo configurado ya NO
sale de la exec-config): el oráculo `model_configured` del registro I8 se
reemplaza — donde antes se verificaba contra la clave `model` de la exec-config
temporal, ahora se verifica contra el modelo declarado en `delegation.json`
(la única fuente del modelo de la delegación externa, spec 006-003 §2.2/D3).
La exec-config temporal deja de declarar `model` (PD-3a retiró la clave del
ejemplo instalable) y el documento de delegación se escribe en el TEMPORAL del
test, con `XDG_CONFIG_HOME` redirigido: el HOME y la config del dueño no se
leen ni se pisan. La variable `CDAD_OPENCODE_MODEL` conserva su significado
como VALOR del modelo, ahora aportado a `delegation.json`. Nada más de esta
prueba se relaja: sigue omitida por defecto y no se activa aquí.

A-1 (006-005 U1b, REEMPLAZO DECLARADO en el RED de esa unidad): donde esta
prueba distinguía el registro I8 del WORKER «además del de la interfaz»
(`:480-486`) y asertaba el registro de la INTERFAZ (`:540-557`), ahora exige
UN SOLO registro por despacho: la interfaz RELAYA el `attempt` del módulo y no
registra (D-14/PD-1), así que el registro del despacho ES el del intento que el
sobre declara. Se conservan íntegras las aserciones sobre
`session`/`model_reported`/`provenance` que salían del registro del worker.

OMISIÓN POR DEFECTO (PD-8, verificable sin entorno): esta prueba está
MARCADA y OMITIDA por defecto; se HABILITA por variable de entorno
`CDAD_OPENCODE_INTEGRATION=1`. Sin la variable NO corre NADA de runtime:
la corrida focal registra el skip con diagnóstico (no se fabrica un verde).
Cuando está habilitada, toma TODOS los valores del ENTORNO, SIN valores por
defecto del host; si falta alguno, se OMITE con diagnóstico que NOMBRA la
variable:

  CDAD_OPENCODE_INTEGRATION=1     habilita la prueba (única variable de control)
  CDAD_OPENCODE_BINARY            ruta del binario REAL de OpenCode
  CDAD_OPENCODE_SESSIONS_DB       base de sesiones REAL del runtime (SQLite)
  CDAD_OPENCODE_MODEL             modelo de la config de DELEGACIÓN
                                  (delegation.json; 006-003 U4/PD-3b)

FRONTERA DECLARADA — lo AISLADO es CDAD, el runtime es el REAL del dueño:
- proyecto TEMPORAL (sintético, build_project) + instalación aislada: la
  interfaz común se STAGEA (copia byte a byte del árbol canónico de la skill,
  `staged_interface` de T1) y el subprocess recibe `CDAD_INSTALL_ROOT` del
  tempdir — NADA toca el HOME ni la configuración del dueño;
- agente derivado de PRUEBA `cdad-test-writer` publicado por `prepare` bajo
  `.opencode/agents/` (mínimo: responde un TOKEN FIJO y nada más — no es el
  rol completo del repo);
- paquete canónico publicado por `prepare` y llamado por la INTERFAZ COMÚN
  con destino `opencode` y una exec-config TEMPORAL (los valores del runtime
  llegan de las variables de entorno de arriba);
- el runtime corre con `--standalone` (por defecto del adaptador, PD-4):
  servidor privado; esta prueba NUNCA opera el servicio de fondo del dueño
  y el adaptador lee su base en SOLO LECTURA (lectura del oráculo con
  `mode=ro`, INV-3). Las sesiones que el runtime registra en su base son el
  EFECTO DECLARADO de una corrida real (las credenciales viven en esa base,
  discovery §3): un store vacío no autentica.

NO SE CORRE AQUÍ la prueba habilitada: la corre el ORQUESTADOR (gate de
integración real, plan §T4 — "Owner: test-writer (módulo omitido por
defecto); orquestador + dueño (recorrido real)"). Este RED entrega el
módulo con su omisión demostrada por la corrida focal; la habilitada queda
como evidencia del orquestador junto con la aceptación PD-9 en dos pasos.

RED (plan §T4): «sin la variable la prueba se omite; con entorno aislado, la
correlación durable se comprueba → GREEN es de T1/T2 (aquí no hay producto
nuevo)». El RED observable de ESTA sesión es la corrida focal: 1 skipped
con el diagnóstico que nombra CDAD_OPENCODE_INTEGRATION (omisión declarada,
no verde fabricado). Si estuviera habilitada y el recorrido roto, la unidad
falla por AssertionError de COMPORTAMIENTO (terminación distinta de
completed, fila durable ausente/desidentificada, token ausente, recibo
distinto de pending, I8 sin fila) — no por import/sintaxis.

Mapa test → postcondición (spec 005-010; PD-8 enmendada al aprobar):

  1  TestPd8RealOpenCodeIntegration::test_pd8_real_runtime_delegation_…
       PD-8 (recorrido completo habilitado) — los PUNTOS de la postcondición
       en una sola caminata observable:
       (a) terminación `completed` del envelope;
       (b) la sesión del envelope EXISTE en la base real (lectura mode=ro)
           con `agent == cdad-test-writer` e `idle_outcome == succeeded`
           (identidad desde la fila, PD-3/PD-5; correlación PD-1);
       (c) el TEXTO FINAL contiene el token fijo (delivery del rol);
       (d) recibo durable `semantic_status: "pending"` (INV-5);
       (e) registro I8 del WORKER con `session`/`model_reported` de la
           fila durable y provenance que lo declara (PD-6); `model_reported`
           aplica la regla R2 del review-fix (objeto {id, providerID} →
           'providerID/id'; texto plano intacto); `runtime` de la
           configuración y `model_configured` del `delegation.json`
           (reformulación declarada arriba: 006-003 D3/U4, ya NO de la
           exec-config).
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import (
    AdapterCase,
    durable_last_assistant_text,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Variables de entorno de la integración (declaradas arriba; SIN valores por
# defecto del host — PD-8).
ENABLE_VAR = "CDAD_OPENCODE_INTEGRATION"
BINARY_VAR = "CDAD_OPENCODE_BINARY"
SESSIONS_DB_VAR = "CDAD_OPENCODE_SESSIONS_DB"
MODEL_VAR = "CDAD_OPENCODE_MODEL"

# Agente derivado de PRUEBA del fixture (mínimo: el token fijo como única
# respuesta) y el token que la entrega final debe CONTENER.
EXPECTED_ROLE_AGENT = "cdad-test-writer"
FIXED_TOKEN = "CDAD-T4-TOKEN-b7e04a2c"

# 006-003 §2.2/D3 (reformulación declarada arriba): el rol del paquete es la
# clave del modelo en `delegation.json` — el mismo `--role` con que el fixture
# publica el paquete (`prepare`, EXPECTED_ROLE_AGENT = `cdad-<rol>`), y el id
# de destino es el identificador del runtime (A-2).
DELEGATION_ROLE = "test-writer"
DELEGATION_DIR_NAME = "cdad"
DELEGATION_FILE_NAME = "delegation.json"

RUNTIME = "opencode"          # id del destino (convención del adaptador)
WAIT_TIMEOUT_SECONDS = 600    # espera ACOTADA de la corrida real (PD-1/INV-4)
DELEGATE_SUBPROCESS_TIMEOUT = 900  # margen del subproceso > espera acotada


# Agente derivado MÍNIMO del fixture: frontmatter de agente OpenCode en el
# modo REAL de los roles (`mode: subagent`, fuente canónica de los roles) y
# una tarea única: responder el token fijo (nada de trabajo real del rol).
MINIMAL_TEST_AGENT_SOURCE = """---
description: Agente derivado de PRUEBA del fixture T4 de 005-010: responde un token fijo y nada más.
mode: subagent
---

Agente derivado de PRUEBA del fixture de integración
(tests/test_005_010_t4_integration.py; NO es un rol real del ciclo).

Tu única tarea: responde EXACTAMENTE y ÚNICAMENTE con el token fijo

CDAD-T4-TOKEN-b7e04a2c

en tu mensaje final. No uses herramientas, no expliques, no agregues
ningún otro texto: SOLO el token.
"""


def normalized_row_model(value):
    """Valor esperado de `model_reported` (I8 del worker) derivado de la
    fila durable con la MISMA regla declarada en el review-fix R2
    (review.md; tests/test_005_010_reviewfix.py
    ::TestR2ModelReportedFromDurableRow): si la fila trae `model`
    serializado como objeto JSON {id, providerID} (la forma que la propia
    base real de OpenCode reporta), la observación se guarda como
    'providerID/id' — observabilidad útil, no el objeto verbatim; el TEXTO
    PLANO se conserva tal cual (PD-6)."""
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            return value
        if (isinstance(parsed, dict)
                and isinstance(parsed.get("id"), str)
                and isinstance(parsed.get("providerID"), str)):
            return f"{parsed['providerID']}/{parsed['id']}"
    return value


def real_session_row(store_path: Path, session_id: str) -> dict | None:
    """La fila `session_v2` de UNA sesión correlacionada de la base REAL del
    runtime, abierta en SOLO LECTURA (`mode=ro`, INV-3/PD-8). Nada escribe
    el store del dueño. Devuelve None si el id no está en la base."""
    conn = sqlite3.connect(f"file:{store_path}?mode=ro", uri=True)
    try:
        cursor = conn.execute(
            "SELECT * FROM session_v2 WHERE id = ?", (session_id,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row is not None else None
    finally:
        conn.close()


# ------------------------------------------------------------- fixture T4


class TestPd8RealOpenCodeIntegration(AdapterCase):
    """PD-8 (enmendada al aprobar) — recorrido REAL opcional: interfaz común
    → adaptador OpenCode → runtime REAL (--standalone) → señal durable de la
    base real (mode=ro) → receive → recibo pending. OMITIDA por defecto;
    habilitada por entorno; sin valores por defecto del host."""

    # -- omisión por defecto y entorno requerido (PD-8) --------------------

    def setUp(self) -> None:
        # Las variables se verifican ANTES de construir la fixture: si falta
        # una, la prueba se OMITE con diagnóstico que NOMBRA la variable
        # (nunca un verde fabricado, PD-8).
        self._require_integration_env()
        super().setUp()

    @staticmethod
    def _skip(message: str) -> None:
        raise unittest.SkipTest(message)

    def _require_integration_env(self) -> None:
        if os.environ.get(ENABLE_VAR, "") != "1":
            self._skip(
                "PD-8 omitida por defecto: esta prueba de integración "
                f"contra el binario REAL de OpenCode se habilita con "
                f"{ENABLE_VAR}=1 (sin la variable no se corre NINGÚN "
                "runtime; no se fabrica un verde).")
        binary = os.environ.get(BINARY_VAR, "").strip()
        if not binary:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{BINARY_VAR} (ruta del binario REAL de OpenCode): la "
                "prueba no toma valores por defecto del host (PD-8).")
        if not (Path(binary).is_file() and os.access(binary, os.X_OK)):
            self._skip(
                f"la variable {BINARY_VAR} está definida pero su valor no "
                f"es un binario ejecutable existente: {binary!r} (PD-8: "
                "el binario lo provee la configuración; se omite con "
                "diagnóstico, no se fabrica un verde).")
        sessions_db = os.environ.get(SESSIONS_DB_VAR, "").strip()
        if not sessions_db:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{SESSIONS_DB_VAR} (base de sesiones REAL del runtime): "
                "la prueba no toma valores por defecto del host (PD-8).")
        if not Path(sessions_db).is_file():
            self._skip(
                f"la variable {SESSIONS_DB_VAR} está definida pero su "
                f"valor no es una base existente: {sessions_db!r} (PD-8: "
                "la base de sesiones la provee la configuración; se omite "
                "con diagnóstico).")
        model = os.environ.get(MODEL_VAR, "").strip()
        if not model:
            self._skip(
                "integración habilitada pero FALTA la variable "
                f"{MODEL_VAR} (modelo de la config de DELEGACIÓN: "
                "006-003 §2.2/D3 — la exec-config ya no declara `model`): "
                "la prueba no toma valores por defecto del host (PD-8).")

    # -- fixture ------------------------------------------------------------

    def seed_agents(self) -> Path:
        """Agente derivado de PRUEBA mínimo (cdad-test-writer, `mode:
        subagent`, responde el token fijo): la fuente de derivados del
        fixture es UN archivo mínimo escrito por este test — no los roles
        reales del repo (el recorrido de integración no ejecuta el rol
        completo; PD-8: lo aislado es CDAD, la respuesta observable es el
        token)."""
        agents_src = Path(self._tmp) / "agents-src"
        agents_src.mkdir(parents=True, exist_ok=True)
        (agents_src / f"{EXPECTED_ROLE_AGENT}.md").write_text(
            MINIMAL_TEST_AGENT_SOURCE, encoding="utf-8")
        return agents_src

    def prepare_ok(self, *extra: str) -> subprocess.CompletedProcess:
        """prepare del proyecto sintético con el derivado de PRUEBA (I9):
        publica el paquete canónico y `.opencode/agents/cdad-test-writer.md`
        (la entry que el adaptador exige, PD-3)."""
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "cdad_packet.py"),
             "prepare", "--project-root", str(self.root),
             "--role", "test-writer", "--substage", "red",
             "--objective",
            # ORDEN EXPLÍCITA EN EL ENCARGO (testfix determinista, corrida
            # del orquestador a 3e556a8): el modelo del runtime REAL sigue
            # el paquete canónico por arriba del agente derivado, así que
            # la orden de responder el token no puede vivir SOLO en el
            # agente derivado de prueba: viaja también en el objetivo del
            # paquete (~scripts/cdad_packet.py --objective) — misma orden,
            # mismo token, SIN debilitar la prueba (las afirmaciones de
            # identidad, directorio, idle_outcome, recibo pending, I8 y
            # presencia del token en la entrega se mantienen).
            f"encargo T4 005-010 (integración real OpenCode): responde "
            f"EXACTAMENTE y ÚNICAMENTE con el token fijo {FIXED_TOKEN} en "
            "tu mensaje final; no uses herramientas, no expliques, no "
            "agregues ningún otro texto.",
             *extra],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            env={**dict(os.environ),
                 "CDAD_OPENCODE_AGENTS_DIR": str(self.agents_src)})
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): prepare no publicó el paquete "
                f"canónico con el derivado de prueba: "
                f"{proc.stdout + proc.stderr}")
        return proc

    def integration_config(self) -> Path:
        """Exec-config TEMPORAL con valores EXCLUSIVAMENTE del entorno de la
        integración (sin valores por defecto del host, PD-8/INV-7): binario,
        base de sesiones real; la espera es ACOTADA (PD-1/INV-4).
        `binary_version` se declara desde la sonda honesta del binario
        (`--version`, no despacho) o `unknown` si la sonda no responde — jamás
        un valor inventado.

        Reformulación declarada (006-003 U4/PD-3a/D3): la exec-config ya NO
        declara la clave `model` — el modelo efectivo sale de `delegation.json`
        (`delegation_config()`), que es su única fuente."""
        binary = Path(os.environ[BINARY_VAR].strip())
        sessions_db = Path(os.environ[SESSIONS_DB_VAR].strip())
        try:
            probe = subprocess.run(
                [str(binary), "--version"], capture_output=True, text=True,
                timeout=30, stdin=subprocess.DEVNULL)
            version = (probe.stdout.strip().splitlines() or [""])[0].strip()
        except (OSError, subprocess.SubprocessError):
            version = ""
        fake_dir = Path(self._tmp) / "real-runtime"
        logs_dir = fake_dir / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        config_path = fake_dir / "exec-config.json"
        config_path.write_text(
            json.dumps({
                "runtime": RUNTIME,
                "binary": str(binary),
                "binary_version": version or "unknown",
                "logs_dir": str(logs_dir),
                "sessions_db": str(sessions_db),
                "wait": {"timeout_seconds": WAIT_TIMEOUT_SECONDS},
            }, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return config_path

    def delegation_home(self) -> Path:
        """`XDG_CONFIG_HOME` del fixture: el temporal del test (nunca el del
        dueño)."""
        config_home = Path(self._tmp) / "xdg-config"
        config_home.mkdir(parents=True, exist_ok=True)
        return config_home

    def delegation_config(self, config_home: Path) -> Path:
        """`delegation.json` TEMPORAL (006-003 §2.2/D3, destino=`opencode` por
        A-2) con el modelo de `CDAD_OPENCODE_MODEL` para el rol del paquete:
        la fuente ÚNICA del `model_configured` que observa el I8."""
        path = (config_home / DELEGATION_DIR_NAME / DELEGATION_FILE_NAME)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({
                "version": 1,
                "models": {
                    RUNTIME: {
                        DELEGATION_ROLE: os.environ[MODEL_VAR].strip(),
                    },
                },
            }, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def run_real_delegate(self, config: Path, *,
                          config_home: Path) -> subprocess.CompletedProcess:
        """La INTERFAZ COMÚN stageada (instalación aislada) despacha al
        destino `opencode` con la exec-config temporal y el `delegation.json`
        del test. El env se HEREDA (las credenciales del runtime viven en SU
        base — el runtime es el real del dueño, PD-8 enmendada) salvo
        `XDG_CONFIG_HOME`, que se redirige al temporal del test (006-003 D3:
        el modelo sale de ahí, nunca de la config del dueño) y
        `CDAD_INSTALL_ROOT`, que apunta al tempdir: ningún componente de CDAD
        instala o escribe en el HOME del dueño."""
        return subprocess.run(
            [sys.executable, str(self.staged),
             "--project-root", str(self.root),
             "--packet", self.packet_id,
             "--destination", "opencode",
             "--exec-config", str(config)],
            capture_output=True, text=True,
            env={**os.environ,
                 "CDAD_INSTALL_ROOT": str(self._tmp),
                 "XDG_CONFIG_HOME": str(config_home)},
            timeout=DELEGATE_SUBPROCESS_TIMEOUT)

    def assert_token_in_delivery(self) -> None:
        """El TOKEN FIJO del fixture está en la entrega durable (texto final
        del rol, PD-7)."""
        base = self.results_base()
        hits = [
            path for path in sorted(base.rglob("*"))
            if path.is_file() and FIXED_TOKEN.encode("utf-8")
            in path.read_bytes()
        ]
        self.assertTrue(
            hits,
            msg="ningún archivo de la entrega durable contiene el token "
                f"fijo {FIXED_TOKEN!r} (PD-8: el texto final del rol no "
                "llegó a la entrega)")

    # -- PD-8 ---------------------------------------------------------------

    def test_pd8_real_runtime_delegation_completes_with_durable_correlation(self) -> None:
        """PD-8 (habilitada con entorno): el recorrido REAL completo deja los
        hechos durables declarados: (a) terminación `completed`; (b) la
        sesión del envelope EXISTE en la base real del runtime (leída en
        mode=ro) con `agent == cdad-test-writer` e `idle_outcome ==
        succeeded`; (c) el texto final contiene el token fijo; (d) el recibo
        queda `semantic_status:"pending"` (entrega ≠ gate, INV-5); (e) el
        registro I8 del WORKER toma `session`/`model_reported` de la fila
        durable con provenance (PD-6); `runtime` viene de la configuración de
        ejecución y `model_configured` del `delegation.json` del test
        (006-003 D3/U4: reformulación declarada — la única fuente del modelo
        de la delegación externa)."""
        self.assert_derived_agents_published()
        config = self.integration_config()
        config_home = self.delegation_home()
        delegation = self.delegation_config(config_home)
        self.assertTrue(
            delegation.is_file(),
            msg="precondición (fixture, 006-003 D3/U4): no se escribió el "
                f"delegation.json del test en {delegation}")
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.run_real_delegate(config, config_home=config_home)
        out = self.envelope(proc, "PD-8 integración real")

        # (a) La corrida REAL termina completed (señal durable de la base
        # real; si el adaptador terminara en otra clase, la causa viaja en
        # diagnosis).
        self.assertEqual(
            out["termination"], "completed",
            msg=f"la delegación al runtime REAL no terminó completed "
                f"(PD-8: la señal durable real de {SESSIONS_DB_VAR} debe "
                f"otorgar completed): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        # (b) La sesión del envelope EXISTE en la base real (mode=ro) y la
        # fila declara la identidad cdad del rol + idle succeeded.
        sessions_db = Path(os.environ[SESSIONS_DB_VAR].strip())
        row = real_session_row(sessions_db, out["session"])
        self.assertIsNotNone(
            row,
            msg=f"la sesión del envelope ({out['session']!r}) NO existe en "
                f"la base real ({SESSIONS_DB_VAR}; PD-8: la correlación es "
                "durable sobre la base del runtime real)")
        self.assertEqual(
            row.get("agent"), EXPECTED_ROLE_AGENT,
            msg=f"la fila durable de la base real declara agent "
                f"{row.get('agent')!r}, no el derivado cdad del rol "
                f"({EXPECTED_ROLE_AGENT}; PD-3/PD-8: identidad desde la "
                "fila durable)")
        self.assertEqual(
            row.get("idle_outcome"), "succeeded",
            msg=f"la fila durable de la base real no quedó idle "
                f"'succeeded' (PD-8): idle_outcome "
                f"{row.get('idle_outcome')!r}")
        self.assertTrue(
            row.get("time_idle"),
            msg="la fila durable de la base real no tiene time_idle "
                "(la señal durable material de la corrida real)")

        # (c) El TEXTO FINAL de la sesión real contiene el token fijo.
        final_text = durable_last_assistant_text(sessions_db, out["session"])
        self.assertIsNotNone(
            final_text,
            msg=f"la sesión real no tiene texto final en el ÚLTIMO mensaje "
                f"assistant (PD-1/PD-8): la entrega no puede declararse "
                "sin texto")
        self.assertIn(
            FIXED_TOKEN, final_text,
            msg=f"el texto final de la sesión real no contiene el token "
                f"fijo {FIXED_TOKEN!r} (PD-8: la respuesta del derivado de "
                f"prueba no llegó): {final_text[:200]!r}")
        self.assert_token_in_delivery()

        # (d) ENTREGA ≠ GATE: el recibo durable queda pending (INV-5).
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()

        # (e) El registro I8 del WORKER: session/model_reported desde la
        # FILA DURABLE con provenance (PD-6); runtime de la configuración de
        # ejecución y model_configured del delegation.json del test
        # (006-003 D3/U4: reformulación declarada).
        #
        # A-1 (006-005 U1b, REEMPLAZO DECLARADO): UN SOLO registro por
        # despacho — la interfaz RELAYA el `attempt` del módulo y no registra
        # (D-14/PD-1), así que el registro del despacho ES el del intento que
        # el sobre declara; se conservan las aserciones del registro del
        # worker y se retira el bloque del registro de la interfaz.
        record = json.loads(
            self.assert_single_record_per_dispatch(
                out, records_before).read_text(encoding="utf-8"))
        self.assertEqual(
            set(record), I8_RECORD_KEYS,
            msg=f"el registro I8 del worker no conserva la forma cerrada "
                f"aprobada (PD-6): {sorted(record)}")
        self.assertEqual(
            record["session"], out["session"],
            msg=f"el registro I8 del worker no lleva la `session` de la "
                f"correlación durable (PD-6): {record['session']!r} != "
                f"{out['session']!r}")
        self.assertEqual(
            record["session"], row.get("id"),
            msg=f"el `session` del registro I8 del worker no es el id de "
                f"la fila durable (PD-6): {record['session']!r} != "
                f"{row.get('id')!r}")
        self.assertEqual(
            record["model_reported"], normalized_row_model(row.get("model")),
            msg=f"el `model_reported` del registro I8 del worker no viene "
                f"de la fila durable bajo la regla R2 (objeto JSON "
                f"{{id, providerID}} → 'providerID/id'; texto plano "
                f"intacto; review-fix R2/PD-6): "
                f"{record['model_reported']!r} != "
                f"{normalized_row_model(row.get('model'))!r}")
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict, msg="provenance del registro no es un objeto")
        for field in ("session", "model_reported"):
            source = provenance.get(field)
            self.assertIsInstance(
                source, str,
                msg=f"provenance[{field!r}] no declara la fuente (PD-6: "
                    "debe declarar que viene de la fila durable)")
            self.assertTrue(
                source.strip(), msg=f"provenance[{field!r}] vacío (PD-6)")
        self.assertEqual(
            record["runtime"], RUNTIME,
            msg=f"runtime del registro no es el de la configuración "
                f"(PD-6): {record['runtime']!r}")
        self.assertEqual(
            record["model_configured"], os.environ[MODEL_VAR].strip(),
            msg=f"model_configured del registro no es el declarado en el "
                f"delegation.json del test ({MODEL_VAR}; 006-003 §2.2/D3 — "
                f"única fuente del modelo de la delegación externa; "
                f"reformulación declarada, la exec-config ya no declara "
                f"`model`): {record['model_configured']!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
