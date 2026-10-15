#!/usr/bin/env python3
"""003-002 T3 RED — evidencia de suite Python unittest (P5).

Contract:
- docs/specs/003-002-artifact-tools/spec.md (§2, §8 y P5).
- docs/specs/003-002-artifact-tools/plan.md (T3; test focal declarado
  `tests/test_003_002_t3_run_evidence.py`).

Superficie observable bajo prueba (§2 del contrato; nada de plomería):

    python3 scripts/cdad_result.py run-python-unittest \
        --project-root ROOT \
        --execution-context EXECUTION.json \
        --packet PACKET.md \
        --request REQUEST.json \
        --run-request RUN.json

    python3 scripts/cdad_result.py validate-run-evidence \
        --project-root ROOT \
        --execution-context EXECUTION.json \
        --packet PACKET.md \
        --request REQUEST.json \
        --run-request RUN.json \
        --evidence EVIDENCE.json

Requisitos del contrato que cada test verifica (P5 / §8):

1. argv admitido sólo con prefijo exacto `python3 -m unittest`; los
   argumentos posteriores son argv, sin shell, redirecciones ni
   operadores. Fuera de ese prefijo: rechazo, sin gate verde.
2. La herramienta calcula los snapshots before/after ella misma (§8:
   descubre archivos, ordena paths project-relative, hash por archivo,
   snapshot hash = SHA-256 de los entries canónicos) y NO acepta digests
   suministrados por el caller dentro de RUN.json.
3. `valid-current` exige conjuntamente: exit 0, tests_run > 0, al menos
   un test no skipped, failures = errors = runner_exceptions = 0,
   snapshots before/after iguales (árbol no mutado durante la corrida) y
   contract vigente.
4. NO reutilizables como gate verde: cero tests, exit != 0, suite sólo
   skipped, runner exception, mutación de source o de tests (drift
   current vs. registro), contract drift, selección incompleta o
   desconocida, evidence con digests desconocidos/tamperados. Estados:
   `valid-current` | `invalid` | `stale` | `unknown`.

Convenciones de la batería RED (decisiones del test-writer, derivadas del
contrato aprobado, no de la implementación):

- `run-python-unittest` entrega la evidencia canónica por stdout como
  bytes JSON (misma convención de familia que `receive` → receipt por
  stdout, §2); el test la persiste en scratch para
  `validate-run-evidence --evidence`.
- La evidencia expone `argv` capturado == RUN.json argv; los conteos con
  los nombres de §8 (`tests_run`, `failures`, `errors`, `skipped`,
  `runner_exceptions`) como enteros; un log combinado no vacío; y el
  snapshot hash before/after (bajo claves `before`/`after`, valor hex64
  directo o bajo `sha256`/`digest`/`hash` anidado).
- `validate-run-evidence` aprueba como gate verde exactamente con rc 0 y
  `valid-current` en su salida; cualquier otro resultado (incluyendo
  `invalid`/`stale`/`unknown` o rc != 0) no reutiliza la evidencia.
- Los tests negativos llevan un control positivo interno (corrida verde
  `valid-current` en el MISMO proyecto) antes del caso inválido, de modo
  que hoy fracasen por la ausencia del comando y no por un vacío
  trivial: el primer assert de cada test declara el comportamiento
  ausente.

Fixtures offline: proyecto sintético v2 (política válida, state con
aprobación de contrato I2 y delegación HITL activa), paquete publicado y
observado como dispatched (`--record-dispatch`, I8). Suite unittest local
mínima en `tests/` y source mínimo en `src/`; el `.gitignore` del
proyecto excluye `__pycache__/` y `*.pyc` para que los pyc generados por
la corrida no contaminen los snapshots de selección (§8: se descubren
archivos tracked y untracked NO ignorados). Los proyectos son tempdirs;
este repo nunca se escribe. Sin red.

RED hoy: los subcomandos `run-python-unittest`/`validate-run-evidence`
aún no existen en `scripts/cdad_result.py` (T3 GREEN pendiente); cada
test fracasa por comportamiento ausente (rc != 0 del CLI en el control
positivo), no por ImportError.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"   # runtime v2 de 001
RESULT_SCRIPT = REPO_ROOT / "scripts" / "cdad_result.py"   # helper de 003-002

POLICY_FILE = "docs/cdad-policy.json"
STATE_FILE = "docs/.cdad-state.json"
FEATURE_ID = "003-002-artifact-tools"
EPIC_ID = "epic-003-context-efficiency"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture 003-002 (T3 RED)\n"
CONTRACT_SHA256 = hashlib.sha256(CONTRACT_BYTES).hexdigest()

ROLE = "test-writer"
SUBSTAGE = "red"
ATTEMPT_ID = "attempt-t3-red-001"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
FAKE_DIGEST = "f" * 64          # digest caller-supplied (§8: no se acepta)
TAMPERED_DIGEST = "e" * 64      # digest tamperado en evidence (desconocido)

# argv de la suite del fixture (§8: prefijo exacto `python3 -m unittest`;
# los argumentos posteriores son argv, sin shell).
RUN_ARGV = ["python3", "-m", "unittest", "discover", "-s", "tests"]

SRC_FILES: dict[str, bytes] = {
    "src/app.py": b"APP_VALUE = 1\n",
}

GREEN_MODULE = b"""import unittest


class TestFixtureGreen(unittest.TestCase):
    def test_green_ok(self) -> None:
        self.assertTrue(True)
"""

FAILING_MODULE = b"""import unittest


class TestFixtureFailing(unittest.TestCase):
    def test_fails(self) -> None:
        self.assertEqual(1, 2)
"""

ALL_SKIPPED_MODULE = b"""import unittest


class TestAllSkipped(unittest.TestCase):
    @unittest.skip("fixture: suite solo skipped")
    def test_skipped_a(self) -> None:
        self.assertTrue(True)

    @unittest.skip("fixture: suite solo skipped")
    def test_skipped_b(self) -> None:
        self.assertTrue(True)
"""

# Runner exception: el módulo rompe al importarse (fuera de cualquier
# test); el loader/discovery registra el error.
BROKEN_MODULE = b"raise RuntimeError('fixture: runner exception al importar')\n"

ALL_SKIPPED_COUNT = 2  # tests del fixture ALL_SKIPPED_MODULE


# ---------------------------------------------------------------- fixtures


def fixture_state_document() -> dict:
    """State sintético con los registros I2 para `prepare` del fixture."""
    hitl = {
        "status": "active",
        "epic_id": EPIC_ID,
        "source": AUTHORITY_REF,
        "scope": EPIC_ID,
        "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
    }
    return {
        "version": 1,
        "stack": None,
        "active_epic": EPIC_ID,
        "epic_stage": "features-loop",
        "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
        "epic_history": [],
        "active_feature": FEATURE_ID,
        "current_stage": "tdd",
        "tdd_substage": SUBSTAGE,
        "audit_status": "approved",
        "postconditions_status": {},
        "stage_history": [{
            "feature": FEATURE_ID,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-10-05T00:00:00Z",
            # 005-001 T1 (D3): forma pineada — CONTRACT_BYTES es lo que
            # build_project escribe en CONTRACT_FILE (migración mecánica).
            "contract_path": CONTRACT_FILE,
            "contract_sha256": CONTRACT_SHA256,
        }],
        "approver": "Pablo",
        "last_updated": "2026-10-05T00:00:00Z",
        "execution": None,
        "active_packet": None,
        "hitl_delegation": hitl,
    }


def build_project(root: Path, *, test_module: bytes = GREEN_MODULE) -> Path:
    """Proyecto sintético válido para `prepare` (003-002) con suite local."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    (root / "src").mkdir(exist_ok=True)
    (root / "docs").mkdir(exist_ok=True)
    # Política válida de tres campos (soportada por el runtime v2).
    (root / POLICY_FILE).write_text(
        json.dumps({
            "schema_version": 1,
            "path_policy": {
                "test_roots": ["tests"],
                "implementation_roots": ["src"],
                "documentation_roots": ["docs"],
            },
            "temporary_roots": [".cdad/tmp"],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (root / CONTRACT_FILE).parent.mkdir(parents=True, exist_ok=True)
    (root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
    authority = root / AUTHORITY_REF
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Authorized execution fixture (epic-003)\n",
                         encoding="utf-8")
    (root / STATE_FILE).write_text(
        json.dumps(fixture_state_document(), ensure_ascii=False) + "\n",
        encoding="utf-8")
    for rel, data in SRC_FILES.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    # Higiene de snapshots: los pyc que genere la corrida de unittest dentro
    # del árbol del fixture quedan ignorados (§8: tracked y untracked NO
    # ignorados).
    (root / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
    (root / "tests" / "test_fixture.py").write_bytes(test_module)
    return root


def walk_nodes(node: object):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from walk_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk_nodes(item)


def decode(data: bytes | str) -> str:
    if isinstance(data, bytes):
        return data.decode("utf-8", errors="replace")
    return data


def run_packet_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Corrida del CLI de 001 (prepare/validate) con bytes de salida."""
    return subprocess.run(
        [sys.executable, str(PACKET_SCRIPT), *args],
        cwd=REPO_ROOT, capture_output=True,
    )


def parse_json_or_none(proc: subprocess.CompletedProcess) -> dict | None:
    """Evidencia JSON en stdout del CLI de 003-002, o None (rechazo)."""
    if proc.returncode != 0:
        return None
    try:
        return json.loads(decode(proc.stdout))
    except (json.JSONDecodeError, ValueError):
        return None


def validate_is_current(proc: subprocess.CompletedProcess) -> bool:
    """Gate verde exacto: rc 0 y `valid-current` en la salida (§8)."""
    return proc.returncode == 0 and "valid-current" in decode(proc.stdout)


def find_int(doc: object, keys: tuple[str, ...]) -> int | None:
    for node in walk_nodes(doc):
        if isinstance(node, dict):
            for key in keys:
                if key in node and isinstance(node[key], int) \
                        and not isinstance(node[key], bool):
                    return node[key]
    return None


def find_str_any(doc: object, keys: tuple[str, ...]) -> str | None:
    for node in walk_nodes(doc):
        if isinstance(node, dict):
            for key in keys:
                if key in node and isinstance(node[key], str) \
                        and node[key].strip():
                    return node[key]
    return None


def find_exact_list(doc: object, target: list) -> list | None:
    for node in walk_nodes(doc):
        if isinstance(node, dict):
            for value in node.values():
                if isinstance(value, list) and value == target:
                    return value
    return None


# ------------------------------------------------------------------- suite


class T3RunEvidenceCase(unittest.TestCase):
    """Base: proyecto dispatched + scratch para RUN.json/evidence."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-002-t3-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))

    # -- arranque del fixture ----------------------------------------------

    def new_dispatched_project(self) -> None:
        """Proyecto sintético nuevo (tempdir), paquete dispatched listo."""
        tmp = tempfile.mkdtemp(prefix="cdad-003-002-t3red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.root = build_project(Path(tmp) / "proj")
        self.establish_dispatched()
        self.run_counter = 0
        self._last: tuple[Path, Path] | None = None

    def establish_dispatched(self) -> None:
        """Prepara el paquete del fixture y lo observa como dispatched (I8)."""
        prep = run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--role", ROLE, "--substage", SUBSTAGE,
            "--objective", "T3 objective",
        ])
        self.assertEqual(
            prep.returncode, 0,
            msg=f"precondición (fixture): `prepare` debe tener éxito: "
                f"{decode(prep.stdout)} {decode(prep.stderr)}")
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
        self.packet_id = state["active_packet"]["id"]
        execution_id = (state.get("execution") or {}).get("id")
        self.assertTrue(
            execution_id,
            msg="precondición (fixture): state.execution debe referenciar "
                "el contexto v2 de 001")
        self.execution_id = execution_id
        self.execution_context_path = (
            self.root / ".cdad" / "executions" / execution_id
            / "execution.json")
        self.assertTrue(
            self.execution_context_path.is_file(),
            msg="precondición (fixture): el contexto v2 debe existir en "
                ".cdad/executions")
        self.packet_dir = self.root / ".cdad" / "packets" / self.packet_id
        self.packet_path = self.packet_dir / "PACKET.md"
        self.request_path = self.packet_dir / "REQUEST.json"
        for path in (self.packet_path, self.request_path):
            self.assertTrue(
                path.is_file(),
                msg=f"precondición (fixture): debe existir el paquete "
                    f"publicado en {path}")
        # Registro I8 del intento (claves cerradas del documento de despacho).
        observation_path = self.root / "docs" / "observations-t3.json"
        observation_path.write_text(json.dumps({
            "runtime": "opencode",
            "model_configured": "glm-5.3-flash",
            "model_reported": "glm-5.3-flash",
            "session": "ses-003-002-t3-red-0001",
            "started_at": "2026-10-05T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        record = run_packet_cli([
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", ATTEMPT_ID,
            "--input", str(observation_path),
        ])
        self.assertEqual(
            record.returncode, 0,
            msg=f"precondición (fixture): --record-dispatch debe registrar "
                f"el intento: {decode(record.stdout)} {decode(record.stderr)}")
        state = json.loads((self.root / STATE_FILE).read_text(encoding="utf-8"))
        self.assertEqual(
            state["active_packet"]["status"], "dispatched",
            msg="precondición (fixture): el paquete activo debe quedar "
                "dispatched (status I8)")

    # -- escrituras del fixture --------------------------------------------

    def write_test_module(self, module: bytes,
                          name: str = "test_fixture.py") -> None:
        tests_dir = self.root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / name).write_bytes(module)

    def clear_test_modules(self) -> None:
        tests_dir = self.root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        for path in tests_dir.glob("*.py"):
            path.unlink()

    def append_to(self, rel: str, extra: bytes) -> None:
        """Agrega bytes al final del archivo `rel` del proyecto fixture
        (mutación del árbol entre la corrida y la validación, sin cambiar
        la aserción que el test verifica)."""
        target = self.root / rel
        target.write_bytes(target.read_bytes() + extra)

    def run_request_document(self, *,
                             argv: list[str] | None = None,
                             source_selection: list[str] | None = None,
                             test_selection: list[str] | None = None,
                             drop: tuple[str, ...] = (),
                             demo: dict | None = None) -> dict:
        """RUN.json canónico (§8) del fixture."""
        doc = {
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "argv": list(RUN_ARGV if argv is None else argv),
            "source_selection": list(["src"] if source_selection is None
                                     else source_selection),
            "test_selection": list(["tests"] if test_selection is None
                                   else test_selection),
            "contract_sha256": CONTRACT_SHA256,
        }
        for key in drop:
            doc.pop(key, None)
        if demo is not None:
            doc.update(demo)
        return doc

    def run_request_path(self, **overrides) -> Path:
        """Escribe RUN.json en scratch (fuera del árbol del proyecto) y
        devuelve su path."""
        self.run_counter += 1
        path = Path(self._tmp) / f"run-request-{self.run_counter}.json"
        path.write_text(
            json.dumps(self.run_request_document(**overrides),
                       ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    # -- CLI ----------------------------------------------------------------

    def run_run_python_unittest(self, run_request: Path
                                ) -> subprocess.CompletedProcess:
        return self.result_cli([
            "run-python-unittest",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--run-request", str(run_request),
        ])

    def result_cli(self, args: list[str]) -> subprocess.CompletedProcess:
        """Corrida del CLI de 003-002 (`scripts/cdad_result.py`) con bytes."""
        return subprocess.run(
            [sys.executable, str(RESULT_SCRIPT), *args],
            cwd=REPO_ROOT, capture_output=True, timeout=300,
        )

    def validate_evidence(self, evidence_path: Path, run_request_path: Path
                          ) -> subprocess.CompletedProcess:
        return self.result_cli([
            "validate-run-evidence",
            "--project-root", str(self.root),
            "--execution-context", str(self.execution_context_path),
            "--packet", str(self.packet_path),
            "--request", str(self.request_path),
            "--run-request", str(run_request_path),
            "--evidence", str(evidence_path),
        ])

    # -- oráculos -----------------------------------------------------------

    def save_evidence(self, proc: subprocess.CompletedProcess,
                      run_request_path: Path) -> dict:
        """Persiste la evidencia canónica (§2, stdout JSON) y la liga al
        RUN.json empleado."""
        self.assertEqual(
            proc.returncode, 0,
            msg="P5 (T3 GREEN pendiente): `run-python-unittest` aún no "
                f"existe en {RESULT_SCRIPT.name} (rc={proc.returncode}): "
                f"{decode(proc.stdout)} {decode(proc.stderr)}")
        try:
            evid = json.loads(decode(proc.stdout))
        except (json.JSONDecodeError, ValueError) as exc:
            self.fail(
                "P5 (T3 GREEN pendiente): la evidencia canónica debe salir "
                f"por stdout como JSON; obtuve: {decode(proc.stdout)!r} "
                f"({exc})")
        self.run_counter += 1
        self.evidence_path = Path(self._tmp) / \
            f"evidence-{self.run_counter}.json"
        self.evidence_path.write_bytes(proc.stdout)
        self._last = (self.evidence_path, run_request_path)
        self.evidence_doc = evid
        return evid

    def validate_last(self) -> subprocess.CompletedProcess:
        assert self._last is not None, "precondición: save_evidence antes"
        return self.validate_evidence(*self._last)

    def must_be_current(self, validation: subprocess.CompletedProcess) -> None:
        self.assertTrue(
            validate_is_current(validation),
            msg="P5: la suite verde fixture (exit 0, 1 test no skipped, "
                "cero fallos, snapshots intactos, contract vigente) debe "
                f"aprobar valid-current; obtuve rc={validation.returncode} "
                f"{decode(validation.stdout)} {decode(validation.stderr)}")

    def never_gate(self, proc: subprocess.CompletedProcess,
                   run_request_path: Path) -> None:
        """El intento NO puede aprobarse como gate verde `valid-current`
        (modos aceptables: rechazo explícito rc!=0, o evidencia que otra
        cosa que no sea valid-current)."""
        evid = parse_json_or_none(proc)
        if proc.returncode == 0:
            self.assertIsNotNone(
                evid,
                msg="P5: rc==0 debe exponer la evidencia canónica JSON por "
                    "stdout (§2)")
        if evid is None:
            return  # rechazo explícito: no hay gate ni evidencia aprobable
        self.evidence_path = Path(self._tmp) / "evidence-rejected.json"
        self.evidence_path.write_bytes(proc.stdout)
        validation = self.validate_evidence(self.evidence_path,
                                            run_request_path)
        self.assertFalse(
            validate_is_current(validation),
            msg="P5: la evidencia debe RECHAZARSE como gate verde"
                f"; obtuve rc={validation.returncode} "
                f"{decode(validation.stdout)} {decode(validation.stderr)}")

    def assert_mechanical_evidence(self, evid: dict, argv: list[str]) -> None:
        """Hechos mecánicos capturados (§8): argv, exit, conteos, log y
        snapshots computados por la herramienta."""
        recorded = find_exact_list(evid, list(argv))
        self.assertIsNotNone(
            recorded,
            msg="P5: la evidencia debe capturar el argv de RUN.json")
        exit_code = find_int(evid, ("exit", "exit_code"))
        self.assertIsNotNone(
            exit_code, msg="P5: el exit code de la corrida debe registrarse")
        self.assertEqual(
            exit_code, 0,
            msg="P5 (corrida verde): exit 0 registrado")
        for key in ("tests_run", "failures", "errors", "skipped",
                    "runner_exceptions"):
            value = find_int(evid, (key,))
            self.assertIsNotNone(
                value,
                msg=f"P5: el conteo {key} (§8) debe registrarse como entero")
        self.assertEqual(
            find_int(evid, ("tests_run",)), 1,
            msg="P5: la suite fixture tiene exactamente 1 test")
        self.assertEqual(
            find_int(evid, ("skipped",)), 0,
            msg="P5: la corrida verde no tiene skips")
        self.assertEqual(
            find_int(evid, ("failures",)), 0, msg="P5: cero failures")
        self.assertEqual(
            find_int(evid, ("errors",)), 0, msg="P5: cero errors")
        self.assertEqual(
            find_int(evid, ("runner_exceptions",)), 0,
            msg="P5: cero runner exceptions")
        log_value = find_str_any(
            evid, ("log", "log_combined", "combined_log", "output"))
        self.assertIsNotNone(
            log_value,
            msg="P5: el log combinado de la corrida debe registrarse")
        hashes = self.snapshot_hashes(evid)
        self.assertEqual(
            hashes["before"], hashes["after"],
            msg="P5 (árbol no mutado): snapshot before/after deben "
                "coincidir (§8: snapshot hash = SHA-256 de los entries "
                "canónicos)")

    def snapshot_hashes(self, evid: dict) -> dict[str, set[str]]:
        """Snapshot hashes before/after expuestos por la evidencia (§8)."""
        values: dict[str, set[str]] = {}
        for side in ("before", "after"):
            found: set[str] = set()
            for node in walk_nodes(evid):
                if isinstance(node, dict) and node.get(side) is not None:
                    merged = node[side]
                    if isinstance(merged, str) and HEX64.match(merged):
                        found.add(merged)
                    elif isinstance(merged, dict) or isinstance(merged, list):
                        for item in walk_nodes(merged):
                            if isinstance(item, dict):
                                for key, value in item.items():
                                    if (key in ("sha256", "digest", "hash")
                                            and isinstance(value, str)
                                            and HEX64.match(value)):
                                        found.add(value)
                        if isinstance(merged, dict):
                            for key, value in merged.items():
                                if (key in ("sha256", "digest", "hash")
                                        and isinstance(value, str)
                                        and HEX64.match(value)):
                                    found.add(value)
            if not found:
                self.fail(
                    "P5: la evidencia debe exponer el snapshot hash "
                    f"'{side}' (hex64) computado por la herramienta")
            values[side] = found
        return values

    # -- composición del fixture --------------------------------------------

    def green_cycle(self) -> None:
        """Control positivo de la batería: suite verde del fixture →
        evidencia mecánica completa + `valid-current` en validate."""
        run_json = self.run_request_path()
        proc = self.run_run_python_unittest(run_json)
        evid = self.save_evidence(proc, run_json)
        self.assert_mechanical_evidence(evid, list(RUN_ARGV))
        self.must_be_current(self.validate_last())


# ---------------------------------------------------------------- T3 /  P5


class TestGreenSuite(T3RunEvidenceCase):
    """P5 — corrida verde: evidencia mecánica y gate vigente."""

    def test_p5_green_suite_records_evidence_and_validates_current(
            self) -> None:
        """P5 (3): exit 0 + tests_run > 0 + test no skipped + cero
        failures/errors/runner_exceptions + snapshots before/after
        iguales + contract vigente ⇒ `valid-current`; la evidencia
        registra argv capturado, exit code, conteos §8, log combinado y
        snapshots computados por la herramienta."""
        self.new_dispatched_project()
        self.green_cycle()


class TestArgvRestriction(T3RunEvidenceCase):
    """P5 — argv restringido a `python3 -m unittest` (sin shell ni ops)."""

    FORBIDDEN_ARGV: list[tuple[str, list[str]]] = [
        ("python (no python3)", ["python", "-m", "unittest",
                                 "discover", "-s", "tests"]),
        ("python3 -c", ["python3", "-c", "print('fixture-ok')"]),
        ("otro runner", ["python3", "-m", "pytest", "tests"]),
        ("shell wrapper bash -c",
         ["bash", "-c", "python3 -m unittest discover -s tests"]),
        ("shell wrapper sh -c",
         ["sh", "-c", "python3 -m unittest discover -s tests"]),
        ("operador &&", RUN_ARGV + ["&&", "true"]),
        ("redireccion >", RUN_ARGV + [">", str(Path(tempfile.gettempdir())
                                           / "cdad-t3-red-null")]),
    ]

    def test_p5_argv_outside_prefix_is_never_green_gate(self) -> None:
        """P5 (1): argv fuera del prefijo exacto `python3 -m unittest`
        (otros intérpretes, otros runners, shell wrappers, operadores,
        redirecciones) nunca produce un gate verde. El prefijo admitido
        con argv posterior (`discover -s tests`) sí es admisible (control
        positivo del mismo proyecto)."""
        self.new_dispatched_project()
        self.green_cycle()  # control positivo: prefijo admitido sí aprueba
        for label, argv in self.FORBIDDEN_ARGV:
            with self.subTest(label=label):
                run_json = self.run_request_path(argv=argv)
                proc = self.run_run_python_unittest(run_json)
                self.never_gate(proc, run_json)


class TestNonReusableRunOutcomes(T3RunEvidenceCase):
    """P5 — resultados de corrida y árbol: nunca reutilizables como gate."""

    def test_p5_failing_suite_not_valid_current(self) -> None:
        """P5 (3,4): exit != 0 con failures > 0 no es verde."""
        self.new_dispatched_project()
        self.green_cycle()
        self.clear_test_modules()
        self.write_test_module(FAILING_MODULE)
        run_json = self._last[1]  # mismo RUN.json; cambió el árbol de tests
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            # La corrida falló: si se graba evidencia, debe reflejarlo.
            exit_code = find_int(evid, ("exit", "exit_code"))
            self.assertIsNotNone(exit_code,
                                 msg="P5: exit de la corrida registrado")
            if exit_code == 0:
                self.assertNotEqual(
                    find_int(evid, ("failures",)), 0,
                    msg="P5: failures > 0 registrado pese a exit implícito")
        self.never_gate(proc, run_json)

    def test_p5_zero_tests_not_valid_current(self) -> None:
        """P5 (3,4): cero tests nunca es verde — trap de
        `unittest discover` que sale 0 con 'Ran 0 tests'."""
        self.new_dispatched_project()
        self.green_cycle()
        self.clear_test_modules()
        run_json = self._last[1]
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            tests_run = find_int(evid, ("tests_run",))
            self.assertIsNotNone(tests_run, msg="P5: tests_run registrado")
            self.assertEqual(
                tests_run, 0, msg="P5: fixture sin módulos ⇒ 0 tests")
        self.never_gate(proc, run_json)

    def test_p5_all_skipped_suite_not_valid_current(self) -> None:
        """P5 (3,4): suite sólo skipped (tests_run > 0, skipped ==
        tests_run, cero no-skipped) no es verde."""
        self.new_dispatched_project()
        self.green_cycle()
        self.clear_test_modules()
        self.write_test_module(ALL_SKIPPED_MODULE)
        run_json = self._last[1]
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            tests_run = find_int(evid, ("tests_run",))
            skipped = find_int(evid, ("skipped",))
            self.assertIsNotNone(tests_run, msg="P5: tests_run registrado")
            self.assertIsNotNone(skipped, msg="P5: skipped registrado")
            if tests_run and tests_run == skipped:
                self.assertEqual(
                    tests_run, ALL_SKIPPED_COUNT,
                    msg="P5: fixture de 2 tests ambos skipped")
        self.never_gate(proc, run_json)

    def test_p5_runner_exception_not_valid_current(self) -> None:
        """P5 (3,4): runner exception (módulo de test roto al importar) no
        es verde; errors/runner_exceptions los registran los counts §8."""
        self.new_dispatched_project()
        self.green_cycle()
        self.clear_test_modules()
        self.write_test_module(BROKEN_MODULE)
        run_json = self._last[1]
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            broken = (find_int(evid, ("errors",)) or 0) + \
                (find_int(evid, ("runner_exceptions",)) or 0)
            self.assertGreater(
                broken, 0,
                msg="P5: el error del loader debe reflejarse en counts §8")
        self.never_gate(proc, run_json)


class TestSnapshotIntegrity(T3RunEvidenceCase):
    """P5 — snapshots calculados por la herramienta; drift impide gate."""

    def test_p5_source_mutation_between_run_and_validate_not_current(
            self) -> None:
        """P5 (3,4): mutación de un archivo de source tras la corrida
        (drift current vs. snapshots registrados) ⇒ no `valid-current`
        (stale/unknown); las selecciones deben recalcularse actuales."""
        self.new_dispatched_project()
        self.green_cycle()
        self.append_to("src/app.py", b"APP_EXTRA = 2\n")
        self.never_gate_invalidated()

    def test_p5_test_mutation_between_run_and_validate_not_current(
            self) -> None:
        """P5 (3,4): mutación del árbol de tests tras la corrida ⇒ no
        `valid-current` (stale/unknown)."""
        self.new_dispatched_project()
        self.green_cycle()
        self.clear_test_modules()
        self.write_test_module(GREEN_MODULE + b"\n    def test_more(self) "
                                              b"-> None:\n        pass\n")
        self.never_gate_invalidated()

    def never_gate_invalidated(self) -> None:
        """Re-valida la evidencia vigente tras el drift del árbol."""
        validation = self.validate_last()
        self.assertFalse(
            validate_is_current(validation),
            msg="P5: evidence con árbol mutado no se reutiliza como gate "
                "verde (§8: diferencia ⇒ stale/unknown); obtuve "
                f"rc={validation.returncode} {decode(validation.stdout)} "
                f"{decode(validation.stderr)}")


class TestContractFreshness(T3RunEvidenceCase):
    """P5 — `valid-current` exige contract vigente."""

    def test_p5_contract_drift_not_valid_current(self) -> None:
        """P5 (3): cambiar el contrato del fixture tras la corrida ⇒
        contract ya no vigente ⇒ la evidencia no se reutiliza (stale)."""
        self.new_dispatched_project()
        self.green_cycle()
        contract_path = self.root / CONTRACT_FILE
        contract_path.write_bytes(
            b"# Spec fixture 003-002 (T3 RED) - drift\n")
        self.never_gate_invalidated()

    def never_gate_invalidated(self) -> None:
        validation = self.validate_last()
        self.assertFalse(
            validate_is_current(validation),
            msg="P5: evidence con contract drift no es valid-current "
                f"(stale); obtuve rc={validation.returncode} "
                f"{decode(validation.stdout)} {decode(validation.stderr)}")


class TestSelectionsAndCallerDigests(T3RunEvidenceCase):
    """P5 — selecciones explícitas; digests del caller nunca aceptados."""

    def test_p5_incomplete_selection_never_green_gate(self) -> None:
        """P5 (4): RUN.json incompleto (falta test_selection) no produce
        gate verde (campo ausente ⇒ rechazo o unknown — §8)."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(drop=("test_selection",))
        proc = self.run_run_python_unittest(run_json)
        self.never_gate(proc, run_json)

    def test_p5_unknown_selection_not_valid_current(self) -> None:
        """P5 (4): selección source que apunta a un path inexistente
        (equivalencia no demostrable ⇒ unknown) no es gate verde."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(source_selection=["missing-dir"])
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            # Si se grbó evidencia, track: no debe aprobarse como current.
            self.never_gate(proc, run_json)
        else:
            # No-evidencia aprobable con selección desconocida.
            self.assertFalse(
                "valid-current" in decode(proc.stdout),
                msg="P5: selección desconocida no respalda valid-current")

    def test_p5_caller_supplied_digests_not_accepted(self) -> None:
        """P5 (2): RUN.json que intenta fijar los snapshots con digests
        del caller (claims before/after) no sesga la evidencia: o se
        rechaza, o la evidencia queda calculada por la herramienta
        (nada del digest fake) y conserva el gate verde falso."""
        self.new_dispatched_project()
        self.green_cycle()
        run_json = self.run_request_path(demo={
            "snapshots": {
                "before": {"sha256": FAKE_DIGEST},
                "after": {"sha256": FAKE_DIGEST},
            },
        })
        proc = self.run_run_python_unittest(run_json)
        evid = parse_json_or_none(proc)
        if evid is not None:
            hashes = self.snapshot_hashes(evid)
            self.assertNotIn(
                FAKE_DIGEST, hashes["before"] | hashes["after"],
                msg="P5: los snapshots de la evidencia deben ser calculados "
                    "por la herramienta, jamás los digests del caller (§8)")
            self.must_be_current(self.validate_last())
        # rc != 0: rechazo cerrado del campo caller-supplied — aceptable.

    def test_p5_tampered_evidence_digests_not_current(self) -> None:
        """P5 (4): evidence tamperada (digests grabados reemplazados por
        un digest desconocido) no se reutiliza como gate verde: validate
        recalcula y compara contra las selecciones actuales de RUN.json
        (no acepta autocoincidencia).

        El control positivo (mismo evidence intacto) aprueba
        `valid-current` justo antes del tamper."""
        self.new_dispatched_project()
        self.green_cycle()
        evidence_path, run_request_path = self._last
        raw = evidence_path.read_bytes()
        tampered = re.sub(rb"[0-9a-f]{64}", TAMPERED_DIGEST.encode("ascii"),
                          raw)
        self.assertNotEqual(tampered, raw, msg="fixture: tamper aplicado")
        evidence_path.write_bytes(tampered)
        validation = self.validate_evidence(evidence_path, run_request_path)
        self.assertFalse(
            validate_is_current(validation),
            msg="P5: digests desconocidos/tamperados ⇒ stale/unknown, "
                "nunca gate verde (§8); obtuve "
                f"rc={validation.returncode} {decode(validation.stdout)} "
                f"{decode(validation.stderr)}")


if __name__ == "__main__":
    unittest.main()
