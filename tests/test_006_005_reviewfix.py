#!/usr/bin/env python3
"""006-005 review-fix RED — B-1, B-2 y B-3 de
`docs/specs/006-005-native-path-parity/review.md`.

Contrato y autoridad:

- `docs/specs/006-005-native-path-parity/spec.md` (aprobada, sha256
  `3a824be31e45cd8e6122b7d6f23d3f4d3e6af847ab73f7babef8aa90ce20df01`):
  §2.3 (correlación por transporte: los tres resultados — verificada, no
  verificable, verificada e incorrecta), §2.4 (`model_reported` sale de la
  observación del módulo), §2.6 (sección de runtime), §2.8, §3 (PD-5, PD-6,
  PD-7, PD-8, PD-9, PD-12, PD-14, PD-20, PD-22, PD-23, PD-24), §4 (INV-2,
  INV-13, INV-14, INV-16), §5 (D-3, D-6).
- `docs/specs/006-005-native-path-parity/review.md` (dictamen de etapa 4:
  3 B bloqueantes y 2 O opcionales).
- `docs/epics/epic-006-opencode-concurrency/execution.md`, §«006-005: review
  de etapa 4 (2026-10-20)» — decisiones del orquestador (HITL delegada):
  **B-1** «gana la barrera del rol» (el implementer nunca edita tests, ni
  convencionales ni co-ubicados, aunque estén dentro de una raíz de
  implementación; el derivado aplica la barrera del agente generado
  restringida por la política, nunca ampliada); **B-2** «la observación se
  normaliza en una frontera común (momento y modelo), cualquiera sea la forma
  de seleccionar la fila»; **B-3** «las instrucciones distinguen la vía
  externa (consumir el recibo de `delivery_ref`) de la nativa (`record`
  escenifica y luego `receive`)»; **O-1** se aplica al cierre; **O-2** deuda.

QUÉ SE ESCRIBE AQUÍ (un archivo nuevo) y QUÉ SE REFORMULA (A-1)

- Nuevo: `tests/test_006_005_reviewfix.py` (este archivo) — B-1, B-2, B-3.
- A-1 (reformulación DECLARADA): `tests/test_004_002_t5_reviewfix.py::
  test_reviewfix_b3_nested_tests_dir_not_amplified` exigía que el derivado del
  IMPLEMENTER permitiera editar `src/tests/x.py` («los mapas expresan
  exactamente al clasificador»: PD-7 de 004-002). Ese oráculo se REEMPLAZA
  por el de la barrera del rol (decisión B-1): el implementer NO edita tests
  convencionales ni co-ubicados, aunque la política los clasifique
  implementación. **PD enmendada:** PD-7 de `docs/specs/
  004-002-project-execution-bootstrap/spec.md` («los mapas expresan
  exactamente al clasificador, ni amplificación ni sobre-restricción») se
  ENMIENDA en su eje «ni sobre-restricción» para el implementer: la
  clasificación por ruta NO habilita la escritura de un test dentro de una
  raíz de implementación. **Razón:** el dictamen B-1 («los allows de
  implementación anulan la barrera de tests del implementer») — la barrera
  del rol (`sources/roles/implementer.md`: no editar tests, incluidos los
  co-ubicados) es una CONVENCIÓN DEL ROL, no una clasificación de ruta, y el
  derivado no puede ampliarla. La clasificación del POLICY NO cambia
  (`src/tests/x.py` sigue siendo `implementation`); lo que cambia es el
  permiso de escritura del derivado.
- Búsqueda de otros oráculos acoplados (declarada, ejecutada sobre `tests/`):
  ningún otro test fija `allow` de un test dentro de una raíz de
  implementación para el implementer (`tests/test_004_002_t5_runtime.py:526-531`
  fija `allow` para `src/app.py` —código que NO es test— y `deny` para
  `src/test_mod.py` y `tests/test_a.py`; `tests/test_004_002_t1_policy.py`
  fija la CLASIFICACIÓN, no el permiso), y ningún test fija la frase «FINAL
  TEXT» de la vía EXTERNA (`tests/test_003_006_t3_receive_wiring.py` y
  `tests/test_006_002_u5_transport_equivalence.py` hablan del FINAL TEXT
  NATIVO y de `references/re-entry.md`).

MAPA test → hallazgo (docstrings «review-fix B-n (006-005)»)

  B-1 (la barrera del rol gana) — `TestB1RoleBarrierWins`
    test_b1_derived_implementer_denies_tests_inside_implementation_roots
    test_b1_derived_implementer_never_more_permissive_than_the_generated_one
    test_b1_derived_implementer_keeps_non_test_implementation_code_writable
  B-2 (frontera común de normalización) — `TestB2SessionSelection`
    test_b2_session_selection_accredits_the_row_and_reports_the_model
    test_b2_session_selection_gives_the_same_result_as_parent_selection
    test_b2_session_selection_moment_contradiction_is_a_rejection
  B-3 (instrucciones + recorrido) — `TestB3GeneratedInstructions`,
  `TestB3ExternalWalk`
    test_b3_generated_orchestrator_describes_the_external_route_as_an_envelope
    test_b3_generated_orchestrator_describes_the_native_route_as_record_then_receive
    test_b3_external_dispatch_returns_a_delivery_ref_that_is_a_valid_receipt

SUPERFICIE OBSERVABLE (caja negra; NO se lee implementación)

- B-1: `scripts/cdad_packet.py prepare` publica en `.opencode/agents/` los
  agentes DERIVADOS (salida declarada del producto) con la política de layout
  CDAD; el veredicto EFECTIVO de escritura se evalúa con el evaluador ya
  declarado en `tests/test_006_005_u6fix7_write_lever.py` (`write_verdict`:
  las claves `edit` y `write` cuentan juntas y gana la última regla que
  coincide — findLast). Los agentes GENERADOS (fuente I9) son la salida
  declarada del generador (`agents/cdad-*.md`): artefactos legibles, no
  implementación.
- B-2: la entrada `skills/cdad-cycle/scripts/cdad_dispatch.py` se invoca COMO
  PROCESO desde una copia staged del árbol del skill, de modo que el módulo
  REAL del runtime (`cdad_delegate_opencode.py`) es el que se resuelve; el
  store es un SQLite descartable con la forma REAL de la versión instalada
  (`time_created INTEGER` en MILISEGUNDOS, `model` con el documento JSON
  observado). Se observan el sobre declarado (§2.1), el registro I8 que la
  entrada escribe y lo que queda bajo `.cdad/`. El config, el store y el
  binario del usuario no se leen ni se escriben: todo es temporal.
- B-3: los ORQUESTADORES GENERADOS (`agents/cdad-orchestrator.md` y
  `agents/claude-code/cdad-orchestrator.md`) son la salida declarada del
  generador; y el RECORRIDO se ejecuta de verdad (entry `dispatch` + módulo
  real + binario falso → sobre → `cdad_result.py validate-receipt`).

RED ESPERADO HOY (medido en este HEAD, declarado, nunca accidental)

Siete tests fallan por ASERCION de comportamiento ausente y dos son ANCLAS
(pasan hoy: fijan un comportamiento que el producto YA cumple y que las
instrucciones deben describir):

- B-1 (RED): el derivado del implementer RESUELVE `allow` para
  `skills/demo/test_example.py`, `sources/ui/widget.spec.ts` y
  `scripts/tests/test_example.py` (tests convencionales dentro de raíces de
  implementación): los allows de implementación reabren lo que la barrera
  del agente generado deniega (`generated=deny derived=allow`, medido en el
  dictamen). Falla por ASERCION de comportamiento ausente.
- B-2 (RED): por `--session` la entrada NO normaliza el instante: el
  diagnóstico dice «not verified: not evaluable: `parent`, `moment`», la
  sesión NO se acredita (`session: null`) y `model_reported` queda `null`,
  mientras que por `--parent` la MISMA fila se acredita (`session: <hijo>`,
  `model_reported: <provider>/<model>`). Y un momento que CONTRADICE
  `--since` se declara «not verified» con ENTREGA (PD-6) — terminación
  `completed` y el texto final escenificado — en vez de rechazo: lo que
  INV-2 prohíbe («una contradicción evaluable es rechazo, no `unknown`»).
- B-3 (RED): las instrucciones generadas AFIRMAN que `cdad_dispatch.py`
  devuelve el FINAL TEXT y que hay que recibirlo («then stage the returned
  FINAL TEXT through `receive`» / «and returns the FINAL TEXT»); no nombran
  `delivery_ref` en ninguna parte. (ANCLA) El RECORRIDO, en cambio, ya es el
  real: el sobre externo trae `delivery_ref` = el RECIBO DURABLE
  (`receipt.json`), el módulo ya recibió y `cdad_result.py validate-receipt`
  lo acepta — ese test fija el comportamiento real que las instrucciones
  deben describir.
- B-1 (ANCLA): el código de implementación que no es test sigue escribible
  por el derivado del implementer.

Ningún fallo es ImportError/SyntaxError/NameError ni error de fixture.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    POLICY_FILE,
    REPO_ROOT,
    SCRIPT,
    build_project,
    prepare_args,
    read_state,
)
from test_005_009_t1_interface import (
    OUTPUT_KEYS,
    TERMINATION_VOCABULARY,
    dispatch_records,
)
from test_006_005_u6fix7_write_lever import (
    materialize_layout,
    write_verdict,
)
from test_006_005_u6fix8_version_by_observation import (
    SERVER_VERSION,
    U6Fix8Case,
)

SKILL_DIR = REPO_ROOT / "skills" / "cdad-cycle"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"
RESULT_CLI = REPO_ROOT / "scripts" / "cdad_result.py"

RUNTIME = "opencode"
MODULE_NAME = "cdad_delegate_%s.py" % RUNTIME
ENTRY_PRODUCT = SKILL_DIR / "scripts" / "cdad_dispatch.py"

# §2.1: el sobre de la entrada es exactamente el conjunto de claves
# declarado, con `termination` en el vocabulario cerrado.
ENVELOPE_KEYS = OUTPUT_KEYS


# ===========================================================================
# B-1 — la barrera del rol gana sobre la clasificación de rutas
# ===========================================================================

# Los AGENTES GENERADOS (fuente I9) son la salida declarada del generador
# (`agents/cdad-*.md`): artefactos legibles, comparados con sus derivados.
GENERATED_AGENTS_DIR = REPO_ROOT / "agents"

# La política VIGENTE de layout CDAD (la que declara el paquete de esta
# ejecución: `docs/cdad-policy.json`, sha256 f508ab1e…). Se copia al proyecto
# descartable; sólo se sustituye `private_paths` por una ruta FICTICIA del
# fixture (nunca se lee `tests/.sensitive-patterns.local`).
PROJECT_POLICY_REL = "docs/cdad-policy.json"
FIXTURE_PRIVATE_PATH = "tests/.sensitive-patterns.fixture.local"

# Los roles Derivados cuya barrera se compara (implementer y su variante
# Odoo). El derivado se publica con la política de layout CDAD.
IMPLEMENTER_AGENTS = ("cdad-implementer.md", "cdad-implementer-odoo.md")

# Tests CONVENCIONALES dentro de raíces de implementación: son las tres
# sondas del dictamen B-1 («generated=deny derived=allow»).
CONVENTIONAL_TESTS_IN_IMPLEMENTATION = (
    "scripts/tests/test_example.py",
    "skills/demo/test_example.py",
    "sources/ui/widget.spec.ts",
)
# Los tests DECLARADOS por la política (raíz `tests`).
DECLARED_TESTS = ("tests/x.py",)
# La ruta PRIVADA declarada por la política del fixture.
PRIVATE_PATHS = (FIXTURE_PRIVATE_PATH,)
# El directorio de DERIVADOS (el manifiesto y los agentes publicados).
DERIVED_PATHS = (
    ".opencode/agents/cdad-implementer.md",
    ".opencode/agents/.cdad-derived.json",
)
# Código de implementación que NO es test: sigue escribible.
IMPLEMENTATION_CODE = (
    "scripts/x.py",
    "skills/demo/module.py",
    "sources/ui/widget.ts",
    "install.sh",
)

DENY_PROBES = (CONVENTIONAL_TESTS_IN_IMPLEMENTATION + DECLARED_TESTS
               + PRIVATE_PATHS + DERIVED_PATHS)
ALL_PROBES = DENY_PROBES + IMPLEMENTATION_CODE


class ReviewFixB1Case(unittest.TestCase):
    """Proyecto descartable con la política de layout CDAD; `prepare` publica
    los derivados y los agentes generados son su fuente I9."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-006-005-rf-b1-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        build_project(self.root)
        materialize_layout(self.root)
        self.write_policy()
        # Fuente I9: copia temporal de los agentes generados (salida declarada
        # del generador), copiada sin inspección.
        self.agents_src = Path(self._tmp.name) / "agents-src"
        self.agents_src.mkdir()
        for source in sorted(GENERATED_AGENTS_DIR.glob("cdad-*.md")):
            shutil.copy2(source, self.agents_src / source.name)
        env = dict(os.environ)
        env["CDAD_OPENCODE_AGENTS_DIR"] = str(self.agents_src)
        self.prepare = subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(self.root, role="test-writer", substage="red",
                           objective="006-005 review-fix B-1 (test-writer/red)")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env)
        self.generated: dict[str, str] = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(self.agents_src.glob("cdad-*.md"))
        }
        self.derived: dict[str, str] = {}
        base = self.root / ".opencode" / "agents"
        if base.is_dir():
            self.derived = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(base.glob("cdad-*.md"))
            }

    # -- fixture ---------------------------------------------------------

    def write_policy(self) -> None:
        """La política de layout CDAD vigente, con `private_paths` sustituida
        por una ruta FICTICIA del fixture (el archivo privado real no se lee
        ni se nombra)."""
        source = REPO_ROOT / PROJECT_POLICY_REL
        self.assertTrue(
            source.is_file(),
            msg="B-1 (precondición): la política del proyecto no existe: %s"
                % PROJECT_POLICY_REL)
        document = json.loads(source.read_text(encoding="utf-8"))
        path_policy = document["path_policy"]
        path_policy["private_paths"] = list(PRIVATE_PATHS)
        for root in ("scripts", "skills", "sources"):
            self.assertIn(
                root, path_policy["implementation_roots"],
                msg="B-1 (precondición): la política vigente no declara la "
                    "raíz de implementación %r; las sondas de esta unidad "
                    "dependen de ella" % root)
        self.assertIn(
            "tests", path_policy["test_roots"],
            msg="B-1 (precondición): la política vigente no declara la raíz "
                "de tests `tests`")
        (self.root / POLICY_FILE).parent.mkdir(parents=True, exist_ok=True)
        (self.root / POLICY_FILE).write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

    def require_derived(self) -> None:
        self.assertEqual(
            self.prepare.returncode, 0,
            msg="B-1 (precondición): `prepare` debe publicar los derivados; "
                "rc=%s stdout=%r stderr=%r"
                % (self.prepare.returncode, self.prepare.stdout[:300],
                   self.prepare.stderr[:400]))
        for name in IMPLEMENTER_AGENTS:
            self.assertIn(
                name, self.derived,
                msg="B-1 (precondición): falta el derivado %r en "
                    ".opencode/agents/; publicados: %r"
                    % (name, sorted(self.derived)))
            self.assertIn(
                name, self.generated,
                msg="B-1 (precondición): falta el agente GENERADO %r"
                    % name)


class TestB1RoleBarrierWins(ReviewFixB1Case):
    """review-fix B-1 (006-005): la barrera del rol del implementer gana
    sobre los allows de las raíces de implementación."""

    def test_b1_derived_implementer_denies_tests_inside_implementation_roots(
            self) -> None:
        """review-fix B-1 (006-005): el derivado del implementer (y su
        variante Odoo) RESUELVE `deny` —veredicto efectivo de escritura—
        para los tests convencionales que están DENTRO de una raíz de
        implementación (`scripts/tests/test_example.py`,
        `skills/demo/test_example.py`, `sources/ui/widget.spec.ts`), para los
        tests declarados (`tests/x.py`), para la ruta privada de la política
        y para el directorio de derivados.

        El agente GENERADO deniega esas mismas rutas: el derivado no puede
        ser MÁS PERMISIVO que la barrera que hereda (decisión B-1)."""
        self.require_derived()
        for agent in IMPLEMENTER_AGENTS:
            derived_text = self.derived[agent]
            for probe in DENY_PROBES:
                with self.subTest(agent=agent, probe=probe):
                    got = write_verdict(derived_text, probe)
                    self.assertEqual(
                        got, "deny",
                        msg="review-fix B-1 (006-005): el derivado %s resuelve "
                            "%r para %r; la barrera del rol del implementer "
                            "deniega los tests (convencionales, co-ubicados o "
                            "declarados) y las rutas privadas y derivadas, "
                            "aunque estén dentro de una raíz de "
                            "implementación (decisión B-1: gana la barrera "
                            "del rol). El agente generado resuelve %r para esa "
                            "ruta."
                            % (agent, got, probe,
                               write_verdict(self.generated[agent], probe)))

    def test_b1_derived_implementer_never_more_permissive_than_the_generated_one(
            self) -> None:
        """review-fix B-1 (006-005): para CADA sonda, el veredicto efectivo
        de escritura del derivado coincide con el del agente generado o es
        MÁS RESTRICTIVO — nunca más permisivo. El derivado aplica la barrera
        del agente generado restringida por la política, nunca ampliada.

        La dirección «más restrictivo» se ejercita con las rutas privadas y
        las de derivados (el agente GENERADO no las deniega; el derivado sí)."""
        self.require_derived()
        for agent in IMPLEMENTER_AGENTS:
            for probe in ALL_PROBES:
                with self.subTest(agent=agent, probe=probe):
                    generated = write_verdict(self.generated[agent], probe)
                    derived = write_verdict(self.derived[agent], probe)
                    self.assertIn(
                        derived, ("allow", "deny"),
                        msg="review-fix B-1 (006-005): el derivado %s resuelve "
                            "%r para %r; el veredicto efectivo de escritura es "
                            "`allow` o `deny` (nunca `ask`)"
                            % (agent, derived, probe))
                    if generated == "deny":
                        self.assertEqual(
                            derived, "deny",
                            msg="review-fix B-1 (006-005): el derivado %s "
                                "resuelve %r para %r mientras el agente "
                                "generado deniega: el derivado NO puede ser "
                                "más permisivo que la barrera que hereda."
                                % (agent, derived, probe))

    def test_b1_derived_implementer_keeps_non_test_implementation_code_writable(
            self) -> None:
        """review-fix B-1 (006-005) — control positivo: el código de
        implementación que NO es test sigue escribible por el derivado del
        implementer (`scripts/x.py`, `skills/demo/module.py`,
        `sources/ui/widget.ts`, `install.sh`): la barrera del rol acota los
        TESTS, no el producto."""
        self.require_derived()
        for agent in IMPLEMENTER_AGENTS:
            for probe in IMPLEMENTATION_CODE:
                with self.subTest(agent=agent, probe=probe):
                    got = write_verdict(self.derived[agent], probe)
                    self.assertEqual(
                        got, "allow",
                        msg="review-fix B-1 (006-005): el derivado %s resuelve "
                            "%r para %r; el código de implementación que no es "
                            "test sigue escribible (la barrera del rol "
                            "acota los tests, no el producto)."
                            % (agent, got, probe))


# ===========================================================================
# B-2 — la observación se normaliza en una frontera común
# ===========================================================================

PACKET_AGENT = "cdad-test-writer"
PARENT = "ses-parent-rf-0001"
CHILD = "ses-rf-child-0001"

# La forma REAL de la versión instalada (sonda V-7): `time_created` es un
# INTEGER en MILISEGUNDOS y `model` es TEXT con el documento JSON observado.
STORE_COLUMNS = [
    "id TEXT PRIMARY KEY",
    "parent_id TEXT",
    "agent TEXT",
    "model TEXT",
    "time_created INTEGER NOT NULL",
    "time_idle INTEGER",
    "idle_outcome TEXT",
    "directory TEXT NOT NULL",
]

MODEL_ID = "rf-fixture-model-id"
MODEL_PROVIDER = "rf-fixture-provider"
MODEL_JSON = json.dumps({"id": MODEL_ID, "providerID": MODEL_PROVIDER,
                          "variant": "default"})
# La MISMA forma que la vía externa ya fija (D-ADP-2/U6-6): `<provider>/<model>`.
MODEL_NORMALIZED = "%s/%s" % (MODEL_PROVIDER, MODEL_ID)

FAKE_VERSION = "opencode v2.0.27-fixture"

# Un instante que el fixture expresa siempre como ISO UTC y como epoch ms.
MOMENT = dt.datetime.now(dt.timezone.utc).replace(microsecond=0) - dt.timedelta(
    minutes=10)
SINCE = MOMENT.strftime("%Y-%m-%dT%H:%M:%SZ")
BEFORE_MS = int((MOMENT - dt.timedelta(seconds=60)).timestamp() * 1000)
AFTER_MS = int((MOMENT + dt.timedelta(seconds=60)).timestamp() * 1000)

# Texto final byte-exacto (el contenido no se transforma).
NATIVE_PAYLOAD = (
    "# Native role report (006-005 review-fix B-2 fixture)\n"
    "\n"
    "line with trailing spaces:   \n"
    "CRLF line\r\n"
    "last line without a final newline (byte-exactness matters)"
).encode("utf-8")

FAKE_BINARY_SOURCE = '''#!/usr/bin/env python3
"""Fake runtime binary — fixture of
tests/test_006_005_reviewfix.py. NOT the product: it only reports the
version the capability document must observe as OBSERVED, never supposed."""
import sys

if "--version" in sys.argv[1:]:
    sys.stdout.write(__VERSION__ + "\\n")
    sys.stdout.flush()
    sys.exit(0)

sys.stderr.write("006-005 review-fix fake binary: only --version is declared\\n")
sys.exit(2)
'''


class ReviewFixB2Case(unittest.TestCase):
    """Proyecto(s) descartable(s) + árbol del skill staged (módulo REAL del
    runtime) + store descartable con la forma real (epoch ms, model JSON)."""

    maxDiff = None

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="cdad-006-005-rf-b2-")
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.config_home = self.base / "config-home"
        self.config_home.mkdir()
        self.home = self.base / "home"
        self.home.mkdir()
        self.fixture_dir = self.base / "fixture"
        self.fixture_dir.mkdir()

        self.stage = self.base / "stage"
        shutil.copytree(SKILL_DIR, self.stage,
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.scripts = self.stage / "scripts"
        self.entry = self.scripts / "cdad_dispatch.py"
        self.assertTrue(
            self.entry.is_file(),
            msg="B-2 (precondición): no existe la entrada en el producto "
                "(se espera %s)" % ENTRY_PRODUCT.relative_to(REPO_ROOT))
        self.assertTrue(
            (self.scripts / MODULE_NAME).is_file(),
            msg="B-2 (precondición): el módulo REAL del runtime (%s) no existe "
                "junto a la entrada; este RED no usa un módulo falso que "
                "reemplace la observación" % MODULE_NAME)

        self.binary = self.write_fake_binary()
        self.store_path = self.fixture_dir / "sessions.db"
        self.write_store([])
        self.write_runtimes()
        self._projects = 0

    # -- harness ---------------------------------------------------------

    def env(self) -> dict:
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["HOME"] = str(self.home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for name in ("OPENCODE_PASSWORD", "OPENCODE_SERVER_PASSWORD",
                     "CDAD_EXEC_CONFIG"):
            env.pop(name, None)
        return env

    def run_entry(self, *args: str, cwd: Path
                  ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.entry), *args],
            cwd=str(cwd), env=self.env(), capture_output=True, text=True,
            check=False, timeout=300)

    # -- fixture data ----------------------------------------------------

    def write_fake_binary(self) -> Path:
        path = self.fixture_dir / "bin" / "opencode-reviewfix"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            FAKE_BINARY_SOURCE.replace("__VERSION__", json.dumps(FAKE_VERSION)),
            encoding="utf-8")
        path.chmod(0o755)
        return path

    def write_store(self, rows: list) -> Path:
        """Store descartable con la forma REAL de la versión instalada:
        `time_created INTEGER` en epoch MILISEGUNDOS y `model` con el
        documento JSON observado."""
        path = self.store_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.unlink()
        connection = sqlite3.connect(str(path))
        try:
            connection.execute(
                "CREATE TABLE session_v2 (%s)" % ", ".join(STORE_COLUMNS))
            for row in rows:
                names = list(row)
                connection.execute(
                    "INSERT INTO session_v2 (%s) VALUES (%s)"
                    % (", ".join(names), ", ".join("?" * len(names))),
                    [row[name] for name in names])
            connection.commit()
        finally:
            connection.close()
        return path

    def row(self, project: dict, *, session: str = CHILD,
            time_created: int = AFTER_MS) -> dict:
        """Una fila `session_v2` con la forma real: el agente del paquete, el
        instante en milisegundos y el directorio DENTRO de la raíz
        autorizada (pertenencia)."""
        return {
            "id": session,
            "parent_id": PARENT,
            "agent": PACKET_AGENT,
            "model": MODEL_JSON,
            "time_created": time_created,
            "time_idle": None,
            "idle_outcome": "succeeded",
            "directory": str(project["root"] / "nested"),
        }

    def write_runtimes(self) -> Path:
        """§2.6: la sección del runtime en `runtimes.json` (fuente única de la
        vía externa)."""
        document = {
            "version": 1,
            "runtimes": {
                RUNTIME: {
                    "binary": str(self.binary),
                    "binary_version": FAKE_VERSION,
                    "mode": "standalone",
                    "auto": True,
                    "sessions_db": str(self.store_path),
                    "wait": {"timeout_seconds": 30},
                },
            },
        }
        path = self.config_home / "cdad" / "runtimes.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def new_project(self) -> dict:
        """Proyecto descartable con un paquete publicado por `prepare`."""
        self._projects += 1
        root = self.base / ("project-%d" % self._projects)
        root.mkdir(parents=True, exist_ok=True)
        build_project(root)
        proc = subprocess.run(
            [sys.executable, str(PACKET_CLI), "prepare",
             "--project-root", str(root),
             "--role", "test-writer", "--substage", "red",
             "--objective", "006-005 review-fix B-2 fixture (test-writer/red)"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=self.env())
        self.assertEqual(
            proc.returncode, 0,
            msg="B-2 (precondición): `prepare` no publicó el paquete "
                "(test-writer/red):\n%s" % self.tail(proc.stdout + proc.stderr))
        state = read_state(root)
        return {
            "root": root,
            "execution_id": state["execution"]["id"],
            "packet_id": state["active_packet"]["id"],
        }

    @staticmethod
    def tail(text: str, lines: int = 25) -> str:
        return "\n".join((text or "").strip().splitlines()[-lines:])

    def native_result_file(self) -> Path:
        path = self.base / ("native-result-rf-%d.md" % self._projects)
        path.write_bytes(NATIVE_PAYLOAD)
        return path

    # -- invocación `record` --------------------------------------------

    def record(self, project: dict, *, attempt: str, session: str | None = None,
               parent: str | None = None, since: str | None = SINCE,
               native: bool = True) -> subprocess.CompletedProcess:
        args = ["record", "--project-root", str(project["root"]),
                "--packet", project["packet_id"],
                "--attempt-id", attempt, "--runtime", RUNTIME, "--json"]
        if session is not None:
            args += ["--session", session]
        if parent is not None:
            args += ["--parent", parent]
        if since is not None:
            args += ["--since", since]
        if native:
            args += ["--native-result", str(self.native_result_file())]
        return self.run_entry(*args, cwd=project["root"])

    # -- observaciones ----------------------------------------------------

    def envelope(self, proc: subprocess.CompletedProcess, label: str) -> dict:
        self.assertEqual(
            proc.returncode, 0,
            msg="%s: la entrada no completó (rc=%s):\n%s"
                % (label, proc.returncode, self.tail(proc.stdout + proc.stderr)))
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(msg="%s: stdout no es el sobre JSON declarado (§2.1):\n%s"
                          % (label, self.tail(proc.stdout)))
        self.assertIsInstance(out, dict,
                              msg="%s: el sobre no es un objeto: %r" % (label, out))
        self.assertEqual(
            set(out), ENVELOPE_KEYS,
            msg="%s: el sobre no es exactamente el conjunto de claves "
                "declarado (§2.1): %s" % (label, sorted(out)))
        self.assertIn(
            out["termination"], TERMINATION_VOCABULARY,
            msg="%s: terminación fuera del vocabulario cerrado: %r"
                % (label, out["termination"]))
        return out

    def records(self, project: dict) -> dict:
        return dispatch_records(project["root"], project["execution_id"])

    def record_doc(self, project: dict, stem: str) -> dict:
        base = (project["root"] / ".cdad" / "executions"
                / project["execution_id"] / "dispatches")
        return json.loads((base / (stem + ".json")).read_text(encoding="utf-8"))

    def single_record(self, project: dict, before: dict) -> dict:
        """PD-1: exactamente un intento por despacho."""
        new = {stem for stem in self.records(project)
               if stem not in set(before) and not stem.startswith(".")}
        self.assertEqual(
            len(new), 1,
            msg="PD-1: el despacho dejó %d registros I8 nuevos (se espera "
                "exactamente uno): %r" % (len(new), sorted(new)))
        return self.record_doc(project, next(iter(new)))

    def staged_payloads(self, project: dict) -> list:
        inbox = project["root"] / ".cdad" / "inbox"
        if not inbox.is_dir():
            return []
        return [path for path in sorted(inbox.rglob("*"))
                if path.is_file() and path.read_bytes() == NATIVE_PAYLOAD]

    def descriptor_path(self, project: dict) -> Path:
        return project["root"] / ".cdad" / "inbox" / "RESULT.json"

    def receipt_path(self, project: dict) -> Path:
        return (project["root"] / ".cdad" / "runtime" / "results"
                / project["execution_id"] / project["packet_id"] / "receipt.json")

    def diagnosis_text(self, out: dict) -> str:
        """Sólo el DIAGNÓSTICO que la invocación declara (nunca el intento ni
        la sesión: un id podría contener una palabra que el diagnóstico
        debe decir)."""
        return str(out.get("diagnosis") or "")


class TestB2SessionSelection(ReviewFixB2Case):
    """review-fix B-2 (006-005): la observación se normaliza en una frontera
    común, cualquiera sea la forma de seleccionar la fila."""

    def test_b2_session_selection_accredits_the_row_and_reports_the_model(
            self) -> None:
        """review-fix B-2 (006-005): la fila seleccionada con `--session`
        (instante en MILISEGUNDOS posterior a `--since`, agente del paquete y
        directorio dentro de la raíz) se ACREDITA: el registro I8 lleva la
        sesión observada y `model_reported` en la forma normalizada
        `<provider>/<model>` (la misma que fija la vía externa, D-ADP-2).

        Hoy la selección por `--session` no normaliza el instante: la
        observación es «not evaluable» y ni la sesión ni el modelo se
        acreditan."""
        project = self.new_project()
        self.write_store([self.row(project)])
        before = self.records(project)

        proc = self.record(project, attempt="att-rf-b2-s1-0001", session=CHILD)
        out = self.envelope(proc, "B-2 (--session, fila coincidente)")
        record = self.single_record(project, before)

        self.assertEqual(
            record.get("session"), CHILD,
            msg="review-fix B-2 (006-005): con la fila seleccionada por "
                "`--session` cuyo instante (epoch ms) es posterior a "
                "`--since`, el agente coincide y el directorio está dentro de "
                "la raíz, la sesión OBSERVADA se acredita; se persistió %r "
                "(la observación debe normalizarse en una frontera común, "
                "cualquiera sea la forma de seleccionar la fila)."
                % (record.get("session"),))
        self.assertEqual(
            record.get("model_reported"), MODEL_NORMALIZED,
            msg="review-fix B-2 (006-005): `model_reported` sale de la "
                "observación del módulo en las dos vías (§2.4) y se reporta "
                "como `<provider>/<model>` (D-ADP-2/U6-6); se persistió %r"
                % (record.get("model_reported"),))
        self.assertNotEqual(
            record.get("model_reported"), MODEL_JSON,
            msg="review-fix B-2 (006-005): el registro guardó el documento "
                "JSON crudo de `session_v2.model` en vez de la forma "
                "normalizada: %r" % (record.get("model_reported"),))
        self.assertNotEqual(
            out.get("termination"), "blocked",
            msg="review-fix B-2 (006-005): la vía nativa rechazó un "
                "candidato legítimo: %r" % (out,))

    def test_b2_session_selection_gives_the_same_result_as_parent_selection(
            self) -> None:
        """review-fix B-2 (006-005): la MISMA fila, seleccionada por
        `--session` y por `--parent`, produce el MISMO resultado: la sesión
        acreditada y el mismo `model_reported`. La normalización ocurre en
        una frontera común, no en un camino y sí en el otro."""
        by_session_project = self.new_project()
        self.write_store([self.row(by_session_project)])
        before_session = self.records(by_session_project)
        proc = self.record(by_session_project, attempt="att-rf-b2-s2-0001",
                           session=CHILD)
        self.envelope(proc, "B-2 (--session)")
        session_record = self.single_record(by_session_project, before_session)

        by_parent_project = self.new_project()
        self.write_store([self.row(by_parent_project)])
        before_parent = self.records(by_parent_project)
        proc = self.record(by_parent_project, attempt="att-rf-b2-s2-0002",
                           parent=PARENT)
        self.envelope(proc, "B-2 (--parent)")
        parent_record = self.single_record(by_parent_project, before_parent)

        self.assertEqual(
            session_record.get("session"), parent_record.get("session"),
            msg="review-fix B-2 (006-005): la misma fila seleccionada por "
                "`--session` acredita %r y por `--parent` acredita %r: la "
                "observación se normaliza en una frontera común, "
                "independientemente de cómo se seleccionó la fila."
                % (session_record.get("session"),
                   parent_record.get("session")))
        self.assertEqual(
            session_record.get("model_reported"),
            parent_record.get("model_reported"),
            msg="review-fix B-2 (006-005): `model_reported` por `--session` "
                "es %r y por `--parent` es %r: la normalización del modelo "
                "ocurre en la misma frontera que la del instante."
                % (session_record.get("model_reported"),
                   parent_record.get("model_reported")))
        self.assertEqual(
            session_record.get("model_reported"), MODEL_NORMALIZED,
            msg="review-fix B-2 (006-005): el resultado por `--session` no "
                "reporta el modelo observado en la forma declarada: %r"
                % (session_record.get("model_reported"),))

    def test_b2_session_selection_moment_contradiction_is_a_rejection(
            self) -> None:
        """review-fix B-2 (006-005): la fila seleccionada por `--session` cuyo
        instante (epoch ms) CONTRADICE `--since` es un RECHAZO sin entrega:
        la terminación lo declara, el diagnóstico nombra la llave y NADIE
        entrega (ni escenifica, ni descriptor, ni recibo). Nunca `unknown`:
        INV-2 — una contradicción evaluable es rechazo, no «no verificable».

        Hoy el instante no se normaliza, la contradicción se declara «not
        verified» y la entrega se persiste igual (PD-6)."""
        project = self.new_project()
        self.write_store([self.row(project, time_created=BEFORE_MS)])
        before = self.records(project)

        proc = self.record(project, attempt="att-rf-b2-s3-0001", session=CHILD)
        out = self.envelope(proc, "B-2 (--session, momento contradictorio)")

        self.assertNotEqual(
            out.get("termination"), "completed",
            msg="review-fix B-2 (006-005): una contradicción evaluable del "
                "momento es un RECHAZO sin entrega; la terminación observada "
                "es %r (INV-2: una contradicción no es «unknown» ni una "
                "entrega aceptada)" % (out.get("termination"),))
        self.assertNotEqual(
            out.get("termination"), "unknown",
            msg="review-fix B-2 (006-005): la contradicción del momento se "
                "declaró `unknown`; INV-2 exige RECHAZO, nunca `unknown`.")
        self.assertEqual(
            out.get("termination"), "blocked",
            msg="review-fix B-2 (006-005): la terminación del rechazo es "
                "`blocked` (el vocabulario cerrado); se observó %r"
                % (out.get("termination"),))
        diagnosis = self.diagnosis_text(out)
        self.assertRegex(
            diagnosis, r"(?i)(moment|momento|time_created)",
            msg="review-fix B-2 (006-005): el rechazo debe NOMBRAR la llave "
                "que contradice (§2.3, resultado 3):\n%s"
                % self.tail(diagnosis, 12))
        self.assertFalse(
            self.staged_payloads(project),
            msg="review-fix B-2 (006-005): se escenificó la entrega nativa "
                "pese a la contradicción del momento: un rechazo NO entrega "
                "(INV-2/PD-4).")
        self.assertFalse(
            self.descriptor_path(project).is_file(),
            msg="review-fix B-2 (006-005): se escribió el descriptor "
                "RESULT.json pese a la contradicción del momento: un rechazo "
                "no entrega (PD-4).")
        self.assertFalse(
            self.receipt_path(project).is_file(),
            msg="review-fix B-2 (006-005): se escribió un recibo pese a la "
                "contradicción del momento: un rechazo no entrega ni fabrica "
                "un recibo (INV-1).")
        for stem, document in ((stem, json.loads(path.read_text(encoding="utf-8")))
                               for stem, path in self.records(project).items()
                               if stem not in set(before)):
            self.assertNotEqual(
                document.get("session"), CHILD,
                msg="review-fix B-2 (006-005): el registro I8 acreditó la "
                    "sesión contradicha (%r): una contradicción evaluable "
                    "nunca se guarda como sesión verificada" % (stem,))


# ===========================================================================
# B-3 — las instrucciones generadas y el recorrido real
# ===========================================================================

# Los orquestadores GENERADOS: salida declarada del generador (artefactos
# legibles; nunca se editan a mano).
GENERATED_ORCHESTRATORS = (
    REPO_ROOT / "agents" / "cdad-orchestrator.md",
    REPO_ROOT / "agents" / "claude-code" / "cdad-orchestrator.md",
)

EXTERNAL_ENTRY_RE = re.compile(r"cdad_dispatch\.py")
FINAL_TEXT_RE = re.compile(r"(?i)final\s+text")
# La AFIRMACIÓN que B-3 prohíbe: la entrada devuelve un FINAL TEXT. Se
# reconoce por el FINAL TEXT junto a un verbo de entrega (no por la mera
# mención del texto final del rol).
DELIVER_VERB_RE = re.compile(
    r"(?i)\breturn(s|ed|ing)?\b|\bstag(e|es|ed|ing)\b"
    r"|\bdeliver(s|ed|ing)?\b|\bhand(s|ed)?\s+over\b"
    r"|\bproduc(e|es|ed)\b|\bemit(s|ed|ing)?\b|\bdevuelve\b")
DELIVERY_REF_RE = re.compile(r"(?i)delivery_ref")
RECEIPT_RE = re.compile(r"(?i)receipt|recibo")
DURABLE_RE = re.compile(r"(?i)durable|permanente|persistente")
# «el módulo YA recibió»: familia tolerante de la marca de hecho consumado.
ALREADY_DONE_RE = re.compile(
    r"(?i)\balready\b"
    r"|\b(has|have|had)\s+(already\s+)?(been\s+)?"
    r"(received|run|executed|performed|staged|registered|published)\b"
    r"|\b(received|ran|executed|performed|staged|registered|published)\b"
    r"[^.\n]{0,80}\bby the (module|adapter|entry)\b"
    r"|\b(ya|hecho|hecha|realizado|realizada|registrado|registrada|"
    r"escenificado|escenificada|recibido|recibida)\b")
# La palabra `receive` como VERBO (el comando), no como sustantivo.
RECEIVE_RE = re.compile(r"(?i)(?<!\w)receive(?!\w)")
RECORD_RE = re.compile(r"(?i)(?<!\w)record(?!\w)")
# «escenifica»: el verbo del staging de la entrega, NO «register».
STAGE_RE = re.compile(
    r"(?i)\bstag(e|es|ed|ing)\b|\bescenific\w*|\bmaterializ\w*|\bpersist\w*"
    r"|\bpublica\w*|\bguarda\w*|\bdeja\b|\bescribe\w*")
NEGATION_RE = re.compile(
    r"(?i)\b(not|no|never|nothing|nada|nunca|without|sin|instead|rather)\b")


def paragraphs(text: str) -> list:
    """Bloques de prosa (párrafos markdown). La segmentación por PÁRRAFO es
    la robusta: los nombres de archivo llevan punto (`cdad_dispatch.py`) y
    partir por puntuación los rompería."""
    return [block.strip() for block in re.split(r"\n\s*\n", text)
            if block.strip()]


def lines_of(block: str) -> list:
    return [line.strip() for line in block.splitlines() if line.strip()]


def sentences_of(block: str) -> list:
    """Oraciones de un párrafo: se acumulan líneas hasta que una CIERRA la
    frase (puntuación final). Las líneas envueltas de markdown no cortan la
    oración; los nombres de archivo (`cdad_dispatch.py`) tampoco la cortan
    (no terminan la línea con puntuación)."""
    buffer: list[str] = []
    out: list[str] = []
    for line in lines_of(block):
        buffer.append(line)
        if line[-1] in ".!?":
            out.append(" ".join(buffer))
            buffer = []
    if buffer:
        out.append(" ".join(buffer))
    return out


def clauses(sentence: str) -> list:
    """Cláusulas de una oración (comas, punto y coma, paréntesis, guiones)."""
    parts = re.split(r"[,;:()]|—|--", sentence)
    return [part.strip() for part in parts if part.strip()]


class TestB3GeneratedInstructions(unittest.TestCase):
    """review-fix B-3 (006-005): las instrucciones GENERADAS del
    orquestador describen la vía externa y la nativa como las hace el
    producto."""

    maxDiff = None

    def orchestrator_texts(self) -> list:
        texts = []
        for path in GENERATED_ORCHESTRATORS:
            self.assertTrue(
                path.is_file(),
                msg="B-3 (precondición): el orquestador generado no existe: %s"
                    % path.relative_to(REPO_ROOT))
            texts.append((path.relative_to(REPO_ROOT).as_posix(),
                          path.read_text(encoding="utf-8")))
        return texts

    def test_b3_generated_orchestrator_describes_the_external_route_as_an_envelope(
            self) -> None:
        """review-fix B-3 (006-005): en los orquestadores GENERADOS, la vía
        EXTERNA se describe como un SOBRE cuyo `delivery_ref` es el RECIBO
        DURABLE y cuyo módulo YA recibió la entrega — y en ningún caso se
        dice que `cdad_dispatch.py dispatch` devuelva un FINAL TEXT a
        recibir.

        Lo que el producto hace (medido, recorrido de esta unidad): la entrada
        devuelve el sobre §2.1, el módulo ya ejecutó `receive` y
        `delivery_ref` apunta al recibo durable."""
        for label, text in self.orchestrator_texts():
            with self.subTest(orchestrator=label):
                # (a) NEGATIVO: ninguna ORACIÓN que nombre la entrada externa
                #     afirma que devuelve un FINAL TEXT a recibir.
                offenders = []
                for block in paragraphs(text):
                    for sentence in sentences_of(block):
                        if not EXTERNAL_ENTRY_RE.search(sentence):
                            continue
                        for clause in clauses(sentence):
                            if not FINAL_TEXT_RE.search(clause):
                                continue
                            if not DELIVER_VERB_RE.search(clause):
                                continue
                            if NEGATION_RE.search(clause):
                                continue
                            offenders.append(clause)
                self.assertEqual(
                    offenders, [],
                    msg="review-fix B-3 (006-005): %s afirma que la entrada "
                        "externa devuelve un FINAL TEXT a recibir: %r. La "
                        "entrada devuelve un SOBRE (§2.1) cuyo `delivery_ref` "
                        "es el recibo durable; el módulo ya recibió."
                        % (label, offenders))

                # (b) POSITIVO: la vía externa se describe con el sobre, su
                #     `delivery_ref`, el recibo durable y el hecho consumado.
                blocks = paragraphs(text)
                self.assertTrue(
                    any(EXTERNAL_ENTRY_RE.search(block) for block in blocks),
                    msg="review-fix B-3 (006-005): %s no nombra la entrada "
                        "externa `cdad_dispatch.py`; la regla de transporte "
                        "debe estar declarada" % label)
                with_ref = [block for block in blocks
                            if DELIVERY_REF_RE.search(block)]
                self.assertTrue(
                    with_ref,
                    msg="review-fix B-3 (006-005): %s describe la vía externa "
                        "sin nombrar `delivery_ref`: el orquestador debe "
                        "consumir el RECIBO que la entrada declara en esa "
                        "clave (decisión B-3)" % label)
                receipt_blocks = [block for block in with_ref
                                  if RECEIPT_RE.search(block)
                                  and DURABLE_RE.search(block)]
                self.assertTrue(
                    receipt_blocks,
                    msg="review-fix B-3 (006-005): %s no dice que "
                        "`delivery_ref` sea el RECIBO DURABLE: %r"
                        % (label, with_ref))
                done_blocks = [block for block in with_ref
                               if ALREADY_DONE_RE.search(block)]
                self.assertTrue(
                    done_blocks,
                    msg="review-fix B-3 (006-005): %s no dice que el módulo YA "
                        "recibió la entrega (la entrada no devuelve un texto a "
                        "recibir): %r" % (label, with_ref))

    def test_b3_generated_orchestrator_describes_the_native_route_as_record_then_receive(
            self) -> None:
        """review-fix B-3 (006-005): en los orquestadores GENERADOS, la vía
        NATIVA se describe como «`record` escenifica, luego `receive`»: el
        verbo `record` de la entrada ESCENIFICA la entrega y el orquestador
        ejecuta después `receive` (la ruta de re-entry).

        Hoy las instrucciones describen la ruta nativa como «the native
        dispatch returns FINAL TEXT in this session» y el verbo `record` sólo
        como «register the attempt»: el orquestador no sabe que `record` ya
        dejó la entrega escenificada."""
        for label, text in self.orchestrator_texts():
            with self.subTest(orchestrator=label):
                found = []
                for block in paragraphs(text):
                    lines = lines_of(block)
                    for index, line in enumerate(lines):
                        if not RECORD_RE.search(line):
                            continue
                        if not STAGE_RE.search(line):
                            continue
                        following = " ".join(lines[index:index + 2])
                        if not RECEIVE_RE.search(following):
                            continue
                        found.append(following)
                self.assertTrue(
                    found,
                    msg="review-fix B-3 (006-005): %s no declara que el verbo "
                        "`record` ESCENIFICA la entrega nativa y que el "
                        "orquestador ejecuta después `receive` (decisión "
                        "B-3: la vía nativa es «record escenifica, luego "
                        "receive»). Líneas con `record`: %r"
                        % (label,
                           [line for block in paragraphs(text)
                            for line in lines_of(block)
                            if RECORD_RE.search(line)]))


class TestB3ExternalWalk(U6Fix8Case):
    """review-fix B-3 (006-005): el RECORRIDO que las instrucciones deben
    describir — la vía externa con el módulo REAL y un binario falso."""

    def test_b3_external_dispatch_returns_a_delivery_ref_that_is_a_valid_receipt(
            self) -> None:
        """review-fix B-3 (006-005) — ANCLA: el despacho EXTERNO (entry +
        módulo real del runtime + binario falso) devuelve un SOBRE §2.1 cuyo
        `delivery_ref` es el RECIBO DURABLE, y ese recibo es aceptado por
        `cdad_result.py validate-receipt`. El módulo ya recibió: el recibo y
        la parte persistida existen bajo `.cdad/runtime/results/`.

        Esta es la salida real que las instrucciones generadas deben
        describir (y la razón de que no puedan pedir un FINAL TEXT)."""
        server = self.start_server(SERVER_VERSION)
        self.write_runtimes(self.section(server=server.url))
        before = self.records()

        proc = self.dispatch()
        out = self.envelope(proc, "B-3 (recorrido externo)")

        ref = out.get("delivery_ref")
        self.assertIsInstance(
            ref, str,
            msg="review-fix B-3 (006-005): `delivery_ref` no es texto: %r"
                % (ref,))
        self.assertTrue(
            ref, msg="review-fix B-3 (006-005): `delivery_ref` vacío: sin "
                     "entrega declarada")
        receipt = Path(ref)
        self.assertTrue(
            receipt.is_file(),
            msg="review-fix B-3 (006-005): `delivery_ref` no apunta a un "
                "recibo durable existente: %r" % (ref,))
        self.assertTrue(
            str(receipt).endswith("receipt.json"),
            msg="review-fix B-3 (006-005): `delivery_ref` debe ser el RECIBO "
                "durable (`receipt.json`); apunta a %r" % (ref,))
        results = self.project["root"] / ".cdad" / "runtime" / "results"
        self.assertTrue(
            str(receipt).startswith(str(results)),
            msg="review-fix B-3 (006-005): el recibo quedó fuera del árbol "
                "canónico de resultados: %r" % (ref,))

        # El módulo YA recibió: la parte persistida acompaña al recibo.
        parts = receipt.parent / "parts"
        self.assertTrue(
            parts.is_dir() and any(parts.iterdir()),
            msg="review-fix B-3 (006-005): el recibo no tiene partes "
                "persistidas: el módulo no llegó a recibir la entrega: %r"
                % (ref,))

        # El recibo es válido para `cdad_result.py validate-receipt`.
        valid = subprocess.run(
            [sys.executable, str(RESULT_CLI), "validate-receipt",
             "--project-root", str(self.project["root"]),
             "--receipt", str(receipt)],
            capture_output=True, text=True, cwd=str(self.project["root"]),
            timeout=120)
        self.assertEqual(
            valid.returncode, 0,
            msg="review-fix B-3 (006-005): `validate-receipt` debe aceptar el "
                "recibo que declara `delivery_ref`; rc=%s stderr=%r"
                % (valid.returncode, (valid.stderr or "")[:400]))
        # Un solo intento I8 por despacho (PD-1) — el módulo registra el suyo.
        self.assertEqual(
            len(set(self.records()) - set(before)), 1,
            msg="review-fix B-3 (006-005)/PD-1: el despacho dejó %d registros "
                "I8 (se espera uno)" % len(set(self.records()) - set(before)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
