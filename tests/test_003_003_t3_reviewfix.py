#!/usr/bin/env python3
"""003-003 T3 review-fix RED — focales F1, F2, F3, O1, O2.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P4; P5; D4; D5; D7; D10;
  invariantes 1, 11; §3: rc≠0 con diagnóstico por stderr y sin salida
  parcial; V7: schemas de evento validados en RED)
- docs/specs/003-003-progress-guards/review-t3.md (hallazgos)
- docs/specs/003-003-progress-guards/review-t3-decision.md (remedio:
  F1 `_segment` de 002; F2 creación exclusiva sin overwrite; F3 focal
  contra el asset del schema; O1 buscar `receipt.json` por nombre; O2
  escalation-v1 lleva execution_id, packet_id y fingerprint)

Mapa focal ↔ postcondición (cada test mapea a UN punto del review):

- F1 → invariante 1/D4 (escritura SOLO bajo `.cdad/executions/<id>/guards/`):
  `execution_id` inseguro (`../x`, o absoluto) se RECHAZA (rc≠0,
  diagnóstico stderr, sin salida parcial) y NO escribe nada — ni dentro
  ni fuera de la raíz.
- F2 → P4/invariante 11 (la evidencia durable es append-only en
  identidad): `record` es CREACIÓN EXCLUSIVA — segundo record con la
  misma clave (packet, attempt, kind) ⇒ rc≠0 con diagnóstico de
  conflicto y los bytes originales intactos.
- F3 → §3/V7/D5 (schema de evento ejercitado en RED): el evento
  persistido por `record` satisface el asset declarado
  `skills/cdad-cycle/assets/guard-event.schema.json` (con las acciones
  de recuperación legítimas declaradas), y un evento con propiedad extra
  (additionalProperties:false) se rechaza con rc≠0 y cero escrituras.
- O1 → P5/D7 (fidelidad de la cita): `receipt_ref` cita el RECEIPT de
  002 por nombre (`…/receipt.json`), no otro artefacto del layout
  (`bundle.json`, `parts/…`).
- O2 → P7/D10/D11 (interfaz suficiente para dedup en T5):
  `escalation-v1` lleva `execution_id`, `packet_id` y el fingerprint de
  las llamadas que disparan la escalada — el `dedup_key` declarado se
  puede derivar de lo que el canal emite.
- Caso positivo → P4/invariante 11: dos record LEGÍTIMOS de intentos
  DISTINTOS (misma clave de packet/kind, attempt 1 y 2) siguen
  funcionando: rc 0 ambos, presupuesto acumulado, causas conservadas
  (guarda de regresión para el fix F2).

Fixtures: proyecto sintético en tmp, eventos y trazas PROPIOS y
etiquetados simulación (P6); los snapshots del árbol se toman DESPUÉS de
crear los fixtures (lección 5ee784e: el fixture no se le cuelga al
guard). No se provoca ningún incidente real. El test no importa el
módulo del guard (superficie observable = CLI subprocess).

RED hoy (contra 5604725): cada focal fracasa por AssertionError sobre el
comportamiento ausente — nunca por ImportError ni sintaxis.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (T1)

EVENT_SCHEMA_ASSET = (
    REPO_ROOT / "skills" / "cdad-cycle" / "assets" / "guard-event.schema.json")

# Tope duro: un guard determinista nunca puede colgarse (acotado).
GUARD_TIMEOUT_S = 120

EXEC_ID = "exec-003-003-t3-reviewfix-001"
PACKET_ID = "003-003-progress-guards-implementer-reviewfix-001"

RESULTS_DIR_REL = f".cdad/runtime/results/{EXEC_ID}/{PACKET_ID}"


# ---------------------------------------------------------------- fixtures


def guard_event(*, execution_id: str = EXEC_ID, packet_id: str = PACKET_ID,
                attempt: int = 1, kind: str = "recovery-attempt",
                cause: str = "session-died-without-result",
                session: str = "sess-A",
                action: str = "resume-same-session",
                at: str = "2026-10-06T00:00:00Z") -> dict:
    """Evento `guard-event-v1` (fixture determinista; forma del RED T3)."""
    return {
        "schema_version": 1,
        "event": "guard-event-v1",
        "execution_id": execution_id,
        "packet_id": packet_id,
        "attempt": attempt,
        "kind": kind,
        "cause": cause,
        "session": session,
        "action": action,
        "at": at,
    }


def unknown_signal_trace(**extra: object) -> dict:
    """Trazo `trace-v1` con contexto de ejecución (para O2) y UNA llamada
    de resultado no clasificable (`unknown`, count=1) → escalada P5.
    Etiquetada simulación (P6)."""
    doc = {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,
        "session_id": "sess-sim-reviewfix-o2",
        "execution_id": EXEC_ID,
        "packet_id": PACKET_ID,
        "entries": [
            {
                "i": 1,
                "kind": "tool_call",
                "tool": "bash",
                "args": ["python", "-m", "pytest", "-k", "opaque"],
                "result_class": "unknown",
                "progress_token": "p0",
                "at": "2026-10-06T00:00:00Z",
            }
        ],
    }
    doc.update(extra)
    return doc


# ------------------------------------------------- validador de schema (RED)


def validate_against_schema(instance: object, schema: dict,
                            path: str = "$") -> None:
    """Validador JSON-Schema mínimo (stdlib, casa sin dependencias).

    Soporta el subconjunto declarativo del asset: type/enum/const,
    required/properties/additionalProperties, items, y los asserts
    escalares básicos. FAIL-CLOSED: una keyword no soportada aborta con
    el nombre explícito (nunca se valida de menos en silencio).
    """
    def fail(msg: str) -> None:
        raise AssertionError(f"schema mismatch at {path}: {msg}")

    for key in schema:
        if key not in {
            "$schema", "title", "description", "type", "enum", "const",
            "required", "properties", "additionalProperties", "items",
            "minLength", "maxLength", "pattern", "minimum", "maximum",
        }:
            fail(f"validador mínimo no soporta la keyword {key!r} — "
                 "no se puede validar de menos en silencio (fail-closed)")

    types = schema.get("type")
    if types is not None:
        type_list = types if isinstance(types, list) else [types]
        ok = False
        for t in type_list:
            if t == "object":
                ok = ok or isinstance(instance, dict)
            elif t == "string":
                ok = ok or isinstance(instance, str)
            elif t == "integer":
                ok = ok or (isinstance(instance, int)
                            and not isinstance(instance, bool))
            elif t == "number":
                ok = ok or (isinstance(instance, (int, float))
                            and not isinstance(instance, bool))
            elif t == "boolean":
                ok = ok or isinstance(instance, bool)
            elif t == "array":
                ok = ok or isinstance(instance, list)
            elif t == "null":
                ok = ok or instance is None
            else:
                fail(f"tipo {t!r} no soportado por el validador mínimo")
        if not ok:
            fail(f"se esperaba type={type_list}; got "
                 f"{type(instance).__name__}")

    if "const" in schema and instance != schema["const"]:
        fail(f"const={schema['const']!r}; got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        fail(f"{instance!r} no pertenece al enum {schema['enum']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            fail(f"string más corto que minLength={schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            fail(f"string más largo que maxLength={schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            fail(f"string no coincide con el pattern {schema['pattern']!r}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            fail(f"número por debajo del minimum={schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            fail(f"número por encima del maximum={schema['maximum']}")

    if isinstance(instance, list):
        if "items" in schema:
            for i, item in enumerate(instance):
                validate_against_schema(item, schema["items"],
                                        path=f"{path}[{i}]")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                fail(f"falta la propiedad requerida {req!r}")
        props = schema.get("properties", {})
        for name, value in instance.items():
            if name in props:
                validate_against_schema(value, props[name],
                                        path=f"{path}.{name}")
            else:
                additional = schema.get("additionalProperties", True)
                if additional is False:
                    fail(f"propiedad extra {name!r} — el schema declara "
                         "additionalProperties:false")
                elif isinstance(additional, dict):
                    validate_against_schema(value, additional,
                                            path=f"{path}.{name}")


# ---------------------------------------------------------------- helpers


class ReviewFixProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con fixtures propios."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t3-reviewfix-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    # -- fixtures

    def write_event(self, **overrides: object) -> tuple[Path, dict]:
        event = guard_event(**overrides)  # type: ignore[arg-type]
        stem = f"event-{abs(hash(json.dumps(event, sort_keys=True)))}"
        path = self.root / "fixture" / f"{stem}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path, event

    def write_trace(self, **extra: object) -> Path:
        doc = unknown_signal_trace(**extra)
        path = self.root / "fixture" / "trace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(
            loaded.get("simulation") is True,
            msg="fixture (precondición): la traza de fallo provocado debe "
                "quedar etiquetada simulación (P6)")
        return path

    def seed_002_results_layout(self) -> None:
        """Layout real de publicación de 002 bajo
        `.cdad/runtime/results/<exec>/<packet>/`: `parts/<name>.utf8`,
        `bundle.json`, `receipt.json` (invariante 5: se REUTILIZA)."""
        res = self.root / RESULTS_DIR_REL
        (res / "parts").mkdir(parents=True, exist_ok=True)
        (res / "bundle.json").write_text(
            json.dumps({"schema_version": 1, "packet_id": PACKET_ID}) + "\n",
            encoding="utf-8")
        (res / "receipt.json").write_text(
            json.dumps({"schema_version": 1, "packet_id": PACKET_ID,
                        "semantic_status": "pending"}) + "\n",
            encoding="utf-8")
        (res / "parts" / "out.utf8").write_text("x", encoding="utf-8")

    # -- CLI

    def run_guard(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [sys.executable, str(GUARD_SCRIPT), *args,
                 "--project-root", str(self.root)],
                cwd=REPO_ROOT, capture_output=True, timeout=GUARD_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "acotado: el guard no terminó dentro de "
                f"{GUARD_TIMEOUT_S}s; got timeout={exc!r}")

    def run_record(self, event_path: Path) -> subprocess.CompletedProcess:
        return self.run_guard("record", "--event", str(event_path))

    def run_budget(self, packet_id: str = PACKET_ID
                   ) -> subprocess.CompletedProcess:
        exec_context = self.root / "fixture" / "exec.json"
        exec_context.parent.mkdir(parents=True, exist_ok=True)
        exec_context.write_text(
            json.dumps({"schema_version": 1, "execution_id": EXEC_ID,
                        "runtime": "opencode"}, indent=2, sort_keys=True)
            + "\n", encoding="utf-8")
        return self.run_guard("budget", "--execution-context",
                              str(exec_context), "--packet", packet_id)

    def run_classify(self, trace: Path) -> subprocess.CompletedProcess:
        return self.run_guard("classify", "--trace", str(trace))

    # -- aserciones compartidas

    def assert_schema_conforms(self, instance: object, schema: dict,
                               why: str) -> None:
        """Valida contra el asset y traduce el mismatch en AssertionError
        con el contexto del focal."""
        try:
            validate_against_schema(instance, schema)
        except AssertionError as exc:
            self.fail(f"{why}: {exc}")

    def assert_no_traceback(self, proc: subprocess.CompletedProcess,
                            which: str) -> None:
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "Traceback", err,
            msg="§3: la violación se diagnostica por stderr, no muere con "
                f"traceback; `{which}` stderr={err!r}")

    def assert_rejection(self, proc: subprocess.CompletedProcess,
                         which: str, why: str) -> None:
        """Violación declarada (§3): rc≠0, diagnóstico por stderr, sin
        salida parcial en stdout."""
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"{why}: la violación debe salir rc≠0; got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assert_no_traceback(proc, which)
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        self.assertTrue(
            err,
            msg=f"{why}: rc≠0 debe venir con diagnóstico por stderr (§3); "
                "stderr vacío")
        self.assertEqual(
            proc.stdout.decode("utf-8", errors="replace").strip(), "",
            msg=f"{why}: la violación no puede emitir salida parcial en "
                "stdout (§3); got stdout=" + repr(
                    proc.stdout.decode("utf-8", errors="replace")))


# ---------------------------------------------------------------- tests


class TestF1RecordRejectsUnsafeExecutionId(ReviewFixProjectCase):
    """F1 → invariante 1/D4: contención de `record`.

    `execution_id` es un segmento del path durable; un segmento inseguro
    (traversal `../x` o un path absoluto) no puede llegar sin validar al
    árbol durable: patrón `_segment` de 002 (cdad_result.py:198-213)."""


    def test_f01_execution_id_inseguro_se_rechaza_sin_escribir(self) -> None:
        """F1: `execution_id="../x"` → rc≠0 con diagnóstico stderr, sin
        salida parcial, y CERO escrituras nuevas en el árbol del proyecto
        (el envelope no puede mentir con un path que 'parece' contenida).
        Variante absoluta: CERO escrituras fuera de la raíz."""
        # (a) traversal: `..` no es un segmento seguro.
        ev_path, _ = self.write_event(execution_id="../x")
        # Snapshot DESPUÉS de los fixtures propios y ANTES de record
        # (lección 5ee784e): todo cambio restante es del guard.
        before = tree_snapshot(self.root)
        proc = self.run_record(ev_path)

        self.assert_rejection(
            proc, "record",
            "F1 (invariante 1/D4): un execution_id con traversal (`../x`) "
            "no es un segmento seguro — debe rechazarse ANTES de tocar "
            "disco, como `_segment` en 002")

        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="F1 (invariante 1/D4): cero escrituras nuevas en el árbol "
                "— el rechazo del segmento inseguro no puede dejar escritura "
                "alguna (ni dentro ni fuera de guards/)")

        # (b) absoluto: un execution_id absoluto descarta el prefijo de
        # joinpath y escribiría FUERA de la raíz; también debe rechazarse.
        outside = tempfile.mkdtemp(prefix="reviewfix-esc-abs-",
                                   dir=self._tmp)
        ev_abs_path, _ = self.write_event(execution_id=outside)
        proc_abs = self.run_record(ev_abs_path)

        self.assert_rejection(
            proc_abs, "record",
            "F1 (invariante 1/D4): un execution_id ABSOLUTO no es un "
            "segmento seguro — debe rechazarse rc≠0 antes de escribir")

        self.assertEqual(
            list(Path(outside).rglob("*")), [],
            msg="F1 (invariante 1/D4): CERO escrituras fuera de la raíz — "
                "un path absoluto en execution_id no puede descartar el "
                f"prefijo y escribir en {outside!r}")


class TestF2RecordIsCreateExclusive(ReviewFixProjectCase):
    """F2 → P4/invariante 11: el evento durable es creación exclusiva.

    El presupuesto durable no puede ser editado en silencio: un segundo
    `record` con la misma clave (packet, attempt, kind) y causa distinta
    NO sobrescribe — conflicto rc≠0 con los bytes originales intactos
    (convención 002: 'conflict: refusing to overwrite')."""

    def test_f02_misma_clave_distinto_payload_conflicto_y_bytes_intactos(
            self) -> None:
        ev1_path, ev1 = self.write_event(attempt=1, cause="original-cause")
        env1 = json.loads(self.run_record(ev1_path).stdout.decode())
        durable_rel = env1.get("durable")
        self.assertIsInstance(
            durable_rel, str,
            msg="F2 (precondición): el primer record declara su ruta durable")
        durable = self.root / durable_rel
        original_bytes = durable.read_bytes()

        ev2_path, ev2 = self.write_event(attempt=1,
                                         cause="corrected-cause-2")
        self.assertNotEqual(
            ev1["cause"], ev2["cause"],
            msg="F2 (precondición): los payloads difieren en la causa")
        proc2 = self.run_record(ev2_path)

        self.assert_rejection(
            proc2, "record",
            "F2 (P4/invariante 11): `record` es creación exclusiva — un "
            "segundo evento con la MISMA clave (packet, attempt, kind) es "
            "un conflicto y debe salir rc≠0, no sobrescribir la evidencia")

        self.assertEqual(
            durable.read_bytes(), original_bytes,
            msg="F2 (P4/invariante 11): los bytes del evento original "
                "quedan INTACTOS — la causa anterior se conserva; el "
                "overwrite silencioso destruye la evidencia del intento")


class TestF3RecordedEventSatisfiesDeclaredSchema(ReviewFixProjectCase):
    """F3 → §3/V7/D5: el schema de evento se ejercita en RED.

    El asset `guard-event.schema.json` (additionalProperties:false,
    `action` en la tabla cerrada D5 con las acciones de recuperación
    legítimas declaradas) es el contrato de la interfaz: el escritor
    (`record`) no puede divergir de él en silencio."""

    def test_f03_evento_valido_satisface_schema_y_extras_se_rechazan(
            self) -> None:
        # (a) Un evento LEGÍTIMO de recuperación (la forma que el propio
        # `record` persiste) debe satisfacer el asset declarado.
        ev_path, event = self.write_event(
            action="resume-same-session",
            cause="session-died-without-result")
        env = json.loads(self.run_record(ev_path).stdout.decode())
        durable_rel = env.get("durable")
        self.assertIsInstance(
            durable_rel, str,
            msg="F3 (precondición): record persiste el evento legítimo")
        persisted = json.loads((self.root / durable_rel).read_bytes())

        schema = json.loads(EVENT_SCHEMA_ASSET.read_text(encoding="utf-8"))
        self.assert_schema_conforms(
            persisted, schema,
            why="F3 (§3/V7): el evento durable que `record` persiste debe "
                "satisfacer el asset guard-event.schema.json — escritor y "
                "schema no pueden divergir (D5: acciones de recuperación "
                "legítimas como `resume-same-session` declaradas en la "
                "tabla cerrada)")

        # (b) Un evento con propiedad EXTRA (additionalProperties:false)
        # se rechaza en la frontera: rc≠0, diagnóstico, cero escrituras.
        invalid = dict(event)
        invalid["unexpected_field"] = "divergence-probe"
        invalid_path = self.root / "fixture" / "event-extra.json"
        invalid_path.write_text(
            json.dumps(invalid, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        before = tree_snapshot(self.root)
        proc = self.run_record(invalid_path)

        self.assert_rejection(
            proc, "record",
            "F3 (§3/V7): un evento con propiedad extra viola "
            "additionalProperties:false del schema declarado — `record` "
            "debe rechazarlo rc≠0 (validar_evento alineado con el schema)")

        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="F3 (§3/V7): el evento inválido no puede persistirse bajo "
                "guards/ — cero escrituras en el rechazo")


class TestO1ReceiptRefCitesReceiptJson(ReviewFixProjectCase):
    """O1 → P5/D7: fidelidad de la referencia de reconciliación.

    En el layout real de publicación de 002 conviven `parts/<name>.utf8`,
    `bundle.json` y `receipt.json`; 'citar el receipt' significa citar el
    RECEIPT — `receipt_ref` debe apuntar por nombre a `receipt.json`."""

    def test_o01_receipt_ref_apunta_al_receipt_json(self) -> None:
        self.seed_002_results_layout()

        ev_path, _ = self.write_event(attempt=1, action="retry",
                                      cause="silent-tool-failure")
        env = json.loads(self.run_record(ev_path).stdout.decode())

        self.assertIs(
            env.get("reconciled"), True,
            msg="O1/D7 (precondición): con el receipt de 002 presente, la "
                "corrida debe declararse reconciliada")
        receipt_ref = env.get("receipt_ref")
        self.assertIsInstance(
            receipt_ref, str,
            msg="O1/D7: la reconciliación debe citar evidencia por "
                "referencia")
        self.assertTrue(
            receipt_ref.endswith("receipt.json"),
            msg="O1/D7: `receipt_ref` debe citar el RECEIPT por nombre "
                f"(…/receipt.json), no otro artefacto del layout de 002 "
                f"(bundle.json, parts/…); got {receipt_ref!r}")


class TestO2EscalationCarriesDedupContext(ReviewFixProjectCase):
    """O2 → P7/D10/D11: interfaz de escalado suficiente para T5.

    El `dedup_key` declarado (canon(incident_kind, fingerprint,
    execution_id, packet_id)) debe poder derivarse de lo que el canal
    emite: `escalation-v1` lleva `execution_id`, `packet_id` y el
    fingerprint de las llamadas que disparan la escalada (D10: el
    contrato no se trunca)."""

    def test_o02_escalation_lleva_execution_id_packet_id_y_fingerprint(
            self) -> None:
        trace = self.write_trace()

        proc = self.run_classify(trace)
        self.assertEqual(
            proc.returncode, 0,
            msg="O2 (precondición): classify clasifica la traza con éxito "
                f"(rc 0); got rc={proc.returncode} stderr={proc.stderr!r}")
        env = json.loads(proc.stdout.decode())
        escalations = env.get("escalations") or []
        self.assertTrue(
            escalations,
            msg="O2 (precondición): la señal unknown debe producir la "
                "escalada honesta (P5/invariante 4)")
        esc = escalations[0]
        self.assertEqual(
            esc.get("contract"), "escalation-v1",
            msg="O2 (precondición): contrato escalation-v1")

        self.assertEqual(
            esc.get("execution_id"), EXEC_ID,
            msg="O2 (D10/D11): la escalada debe llevar `execution_id` — "
                "sin él el dedup_key declarado para T5 no puede derivarse "
                "de lo que el canal emite")
        self.assertEqual(
            esc.get("packet_id"), PACKET_ID,
            msg="O2 (D10/D11): la escalada debe llevar `packet_id` — "
                "el dedup es por execution_id+packet_id")
        fingerprint = esc.get("fingerprint")
        self.assertIsInstance(
            fingerprint, str,
            msg="O2 (D10/D11): la escalada debe llevar el fingerprint de "
                "las llamadas que la disparan (huella canónica: "
                "herramienta + argumentos + clase de resultado)")
        self.assertTrue(
            fingerprint and fingerprint.strip(),
            msg="O2 (D10/D11): el fingerprint debe ser no vacío — sin "
                "huella canónica no hay dedup del mismo incidente (P7)")


class TestPositiveDistinctAttemptsStillRecord(ReviewFixProjectCase):
    """Caso positivo → P4/invariante 11: dos record LEGÍTIMOS de intentos
    DISTINTOS siguen funcionando (guarda de regresión del fix F2: la
    creación exclusiva no puede bloquear intentos legítimos y distintos)."""

    def test_positivo_dos_intentos_distintos_acumulan_presupuesto(
            self) -> None:
        ev1_path, ev1 = self.write_event(
            attempt=1, cause="session-died-without-result", session="sess-A")
        proc1 = self.run_record(ev1_path)
        self.assertEqual(
            proc1.returncode, 0,
            msg="P4 (positivo): el primer record de un intento legítimo "
                f"debe salir rc 0; got rc={proc1.returncode} "
                f"stderr={proc1.stderr!r}")

        ev2_path, ev2 = self.write_event(
            attempt=2, cause="repetition-without-new-info", session="sess-B")
        proc2 = self.run_record(ev2_path)
        self.assertEqual(
            proc2.returncode, 0,
            msg="P4/invariante 11 (positivo): un record LEGÍTIMO de un "
                "intento DISTINTO (mismo packet/kind, attempt distinto) "
                "sigue funcionando tras la creación exclusiva — rc 0; got "
                f"rc={proc2.returncode} stderr={proc2.stderr!r}")

        benv = json.loads(self.run_budget().stdout.decode())
        self.assertEqual(
            benv.get("consumed"), 2,
            msg="P4 (positivo): dos intentos distintos ⇒ consumed=2 — el "
                "presupuesto acumula ambos (reanudar conserva intentos)")
        attempts = benv.get("attempts") or []
        by_attempt = {a.get("attempt"): a for a in attempts}
        self.assertEqual(
            by_attempt.get(1, {}).get("cause"), ev1["cause"],
            msg="P4/invariante 11 (positivo): la causa del intento 1 se "
                "conserva")
        self.assertEqual(
            by_attempt.get(2, {}).get("cause"), ev2["cause"],
            msg="P4/invariante 11 (positivo): la causa del intento 2 se "
                "conserva junto a la anterior")


if __name__ == "__main__":
    unittest.main()
