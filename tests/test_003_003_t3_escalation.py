#!/usr/bin/env python3
"""003-003 T3 RED — tabla cerrada evento→acción y paquete de escalado (P5).

Contract:
- docs/specs/003-003-progress-guards/spec.md (P5; D5; invariantes 3, 4)
- docs/specs/003-003-progress-guards/plan.md (T3; test focal declarado
  `tests/test_003_003_t3_escalation.py`).

Superficie observable bajo prueba (V7: forma del CLI fijada en RED; §3;
la tabla cerrada y el paquete de escalado extienden `classify`, comando
ya declarado en §3):

    python3 scripts/cdad_guard.py classify \
        --project-root ROOT \
        --trace TRACE.json          # traza grabada / fixture (trace-v1)

Envolvente `classify-v1` EXTENDIDA por T3 (canal de escalado top-level):

    {
      "schema_version": 1,
      "trace": "trace-v1",
      "simulation": true,
      "session_id": "…",
      "incidents": [ … T1 … ],
      "polls": [],
      "escalations": [              # NUEVO en T3
        {
          "contract": "escalation-v1",
          "incident_kind": "<clase del evento que escala>",
          "situation": "<breve, no vacía>",
          "decision_needed": true,      # vuelve al orquestador
          "unknown": <bool>,            # señal no fiable ⇒ true
          "limitation": "<límite de observabilidad declarado>",
          "action": "<∈ tabla cerrada D5>",
          "package": {"summary": "<no vacía>",
                      "evidence": "<no vacía>"}
        }
      ]
    }

Semántica fijada por este RED:

- P5: la ambigüedad o la necesidad de decisión semántica vuelve al
  orquestador con un paquete breve y accionable (escalation-v1), sin
  decisión autónoma encubierta.
- P5 (D5, tabla cerrada): la acción de toda escalada pertenece SOLO a la
  tabla cerrada {backoff-poll, retry-with-change, repackage,
  new-session-from-checkpoint, escalate, recommend-block}.
- P5 (invariante 4): sin señal fiable ⇒ `unknown: true` explícito con el
  límite declarado; NUNCA se fabrica éxito ni fracaso (p. ej. sin
  clasificar `unknown` como repetición/bloqueo).
- P5 (invariante 3): un timeout SOLO no prueba bloqueo — sin incidente,
  sin escalada.
- P5/P7 (nota del orquestador): un trabajo legítimo y progresivo NO
  escala y NO recibe intervención.

Fixtures: trazas `trace-v1` grabadas, deterministas, etiquetadas
**simulación** (P6); no se provoca ningún incidente real. El canal
`escalations` es parte del contrato estable (D10): la envolvente lo
expone SIEMPRE (aunque venga vacío) — las interfaces no obstaculizan
003-004.

RED hoy: el canal `escalations` no existe aún en la envolvente
classify-v1; cada aserción positiva fracasa por comportamiento ausente
(AssertionError), nunca por ImportError — el test no importa el módulo
del guard.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (T1)

FEATURE_ID = "003-003-progress-guards"

# Tope duro: un clasificador determinista nunca puede colgarse.
CLASSIFY_TIMEOUT_S = 120

# Tabla CERRADA evento→acción (D5, spec): solo acciones reversibles y
# proporcionadas. Ninguna acción fuera de este conjunto.
CLOSED_ACTION_TABLE = {
    "backoff-poll",
    "retry-with-change",
    "repackage",
    "new-session-from-checkpoint",
    "escalate",
    "recommend-block",
}


# ---------------------------------------------------------------- fixtures


def unknown_signal_trace() -> dict:
    """P5 — sin señal fiable: UNA llamada cuyo resultado el runtime no
    puede clasificar (`result_class: "unknown"`).

    count=1 ⇒ NO puede ser repetición equivalente (umbral conservador ≥2)
    ni progreso medible: la decisión es semántica ⇒ vuelve al
    orquestador. Etiquetada **simulación** (P6)."""
    return {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,
        "session_id": "sess-sim-unknown-signal",
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


def lone_timeout_trace() -> dict:
    """Invariante 3 — un timeout SOLO no prueba bloqueo: una llamada con
    `result_class: "timeout"` no puede alarmar ni escalar por sí sola."""
    doc = unknown_signal_trace()
    doc["session_id"] = "sess-sim-lone-timeout"
    doc["entries"] = [
        {
            "i": 1,
            "kind": "tool_call",
            "tool": "bash",
            "args": ["python", "-m", "pytest", "-k", "slow-but-fine"],
            "result_class": "timeout",
            "progress_token": "p0",
            "at": "2026-10-06T00:00:00Z",
        }
    ]
    return doc


def progressive_trace() -> dict:
    """P5/P7 — trabajo legítimo y progresivo: huella estable pero el
    token de progreso avanza en cada tramo de 3 llamadas (ejecución
    larga pero saludable → sin alerta, sin escalada)."""
    tokens = ["p0", "p0", "p1", "p1", "p2", "p2"]
    return {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,
        "session_id": "sess-sim-progressive",
        "entries": [
            {
                "i": i + 1,
                "kind": "tool_call",
                "tool": "bash",
                "args": ["python", "-m", "pytest"],
                "result_class": "ok",
                "progress_token": token,
                "at": f"2026-10-06T00:0{i}:00Z",
            }
            for i, token in enumerate(tokens)
        ],
    }


# ---------------------------------------------------------------- helpers


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con trazas grabadas como fixtures."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t3-red-esc-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    def write_trace(self, doc: dict) -> Path:
        """Escribe la traza fixture bajo el proyecto y la devuelve."""
        path = self.root / "fixture" / "trace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        # Autochequeo del fixture: el escenario de fallo va etiquetado
        # simulación (P6) — la etiqueta se escribe, no se asume.
        loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(
            loaded.get("simulation") is True,
            msg="fixture (precondición): la traza de fallo provocado debe "
                "quedar etiquetada simulación")
        return path

    def run_classify(self, trace: Path) -> subprocess.CompletedProcess:
        """Corrida del CLI classify (V7) con tope de tiempo."""
        try:
            return subprocess.run(
                [sys.executable, str(GUARD_SCRIPT), "classify",
                 "--project-root", str(self.root), "--trace", str(trace)],
                cwd=REPO_ROOT, capture_output=True, timeout=CLASSIFY_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P5 (acotado): classify no terminó dentro de "
                f"{CLASSIFY_TIMEOUT_S}s; got timeout={exc!r}")

    def classify_envelope(self, trace: Path) -> dict:
        """classify → (rc 0, sin traceback, stdout JSON parseable)."""
        proc = self.run_classify(trace)
        self.assertNotIn(
            "unrecognized", proc.stdout.decode("utf-8", errors="replace"),
            msg="P5: el comando `classify` no existe aún (RED por CLI "
                "ausente): el argv `classify --project-root --trace` "
                "declarado en §3 es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg="P5: classify debe clasificar la traza con éxito (rc 0); "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="P5: classify terminó con traceback")
        env = json.loads(proc.stdout.decode("utf-8"))
        self.assertEqual(
            env.get("schema_version"), 1,
            msg="P5: la envolvente classify-v1 debe declarar "
                "schema_version=1")
        return env


# ---------------------------------------------------------------- tests


class TestP5AmbiguityEscalatesToOrchestrator(EstablishedProjectCase):
    """P5 — la ambigüedad vuelve al orquestador con un paquete breve y
    accionable, sin decisión autónoma encubierta."""

    def test_p05_caso_ambiguo_emite_paquete_breve_y_accionable(self) -> None:
        """P5: una llamada con señal no fiable (result_class `unknown`,
        count=1 — ni repetición clasificable ni progreso) es AMBIGUA ⇒
        UNA escalada `escalation-v1` al orquestador: situación breve,
        `decision_needed: true`, acción de la tabla cerrada y paquete
        con summary y evidencia no vacíos."""
        trace = self.write_trace(unknown_signal_trace())

        env = self.classify_envelope(trace)

        escalations = env.get("escalations")
        self.assertIsInstance(
            escalations, list,
            msg="P5: la envolvente classify-v1 debe exponer el canal "
                "`escalations` (T3: paquete de escalado al orquestador)")
        self.assertEqual(
            len(escalations), 1,
            msg="P5: el caso ambiguo debe volver al orquestador como UN "
                f"paquete de escalado; got={escalations!r}")
        esc = escalations[0]

        self.assertEqual(
            esc.get("contract"), "escalation-v1",
            msg="P5: la escalada debe declarar el contrato escalation-v1 "
                "(T3); got=" + repr(esc.get("contract")))
        situation = esc.get("situation")
        self.assertIsInstance(
            situation, str,
            msg="P5: el paquete de escalado debe llevar una situación")
        self.assertTrue(
            situation and situation.strip(),
            msg="P5: la situación del paquete debe ser BREVE pero no "
                "vacía — sin ella el orquestador no puede decidir")
        self.assertIs(
            esc.get("decision_needed"), True,
            msg="P5: la decisión es semántica ⇒ `decision_needed: true` — "
                "vuelve al orquestador, sin decisión autónoma encubierta")
        self.assertIsInstance(
            esc.get("incident_kind"), str,
            msg="P5: la escalada debe declarar la clase del evento que "
                "la dispara")
        self.assertTrue(
            esc.get("incident_kind") and esc["incident_kind"].strip(),
            msg="P5: incident_kind no vacío (trazabilidad evento→acción)")

        package = esc.get("package")
        self.assertIsInstance(
            package, dict,
            msg="P5: la escalada debe incluir el paquete breve y "
                "accionable (objeto `package`)")
        summary = package.get("summary") if package else None
        self.assertIsInstance(
            summary, str,
            msg="P5: el paquete debe resumir la situación (`summary`)")
        self.assertTrue(
            summary and summary.strip(),
            msg="P5: `package.summary` no vacío — el paquete es breve y "
                "accionable, no un puntero mudo")
        evidence = package.get("evidence") if package else None
        self.assertIsInstance(
            evidence, str,
            msg="P5: el paquete debe traer la evidencia que sustenta la "
                "escalada (`evidence`)")
        self.assertTrue(
            evidence and evidence.strip(),
            msg="P5: `package.evidence` no vacío — el paquete accionable "
                "cita evidencia, no juicios")


class TestP5UnknownStaysUnknown(EstablishedProjectCase):
    """P5 + invariante 4 — sin señal fiable ⇒ `unknown` explícito, sin
    fabricar éxito ni fracaso."""

    def test_p05_unknown_permanece_unknown_sin_fabricar(self) -> None:
        """P5: la señal `unknown` permanece unknown — la escalada la
        declara (`unknown: true` + límite de observabilidad explícito) y
        el guard NO fabrica resultado: no la clasifica como repetición
        (count=1) ni como bloqueo/mala conducta."""
        trace = self.write_trace(unknown_signal_trace())

        env = self.classify_envelope(trace)

        escalations = env.get("escalations")
        self.assertIsInstance(
            escalations, list,
            msg="P5: canal `escalations` obligatorio en classify-v1")
        self.assertTrue(
            escalations,
            msg="P5: sin señal fiable debe haber una escalada declarando "
                "la limitación (la ambigüedad no se calla)")
        for esc in escalations:
            self.assertIs(
                esc.get("unknown"), True,
                msg="P5 (invariante 4): el estado debe permanecer "
                    "`unknown` EXPLÍCITO — sin fabricar éxito ni fracaso")
            limitation = esc.get("limitation")
            self.assertIsInstance(
                limitation, str,
                msg="P5: la escalada debe declarar el límite de "
                    "observabilidad que impide decidir")
            self.assertTrue(
                limitation and limitation.strip(),
                msg="P5 (invariante 4): la limitación se DECLARA "
                    "explícitamente, no se asume ni se oculta")
            self.assertNotEqual(
                esc.get("action"), "recommend-block",
                msg="P5 (invariante 4): una señal `unknown` NO puede "
                    "fabricarse como fracaso — recomendar bloqueo por una "
                    "señal no fiable es fabricar un veredicto")

        incidents = env.get("incidents") or []
        self.assertFalse(
            any(i.get("kind") == "repetition-without-progress"
                for i in incidents),
            msg="P5 (invariante 4): una llamada `unknown` count=1 NO "
                "puede fabricarse como repetición equivalente — "
                f"got incidents={incidents!r}")


class TestP5ClosedActionTable(EstablishedProjectCase):
    """P5 + D5 — toda acción de escalada pertenece a la tabla cerrada."""

    def test_p05_toda_accion_pertenece_a_la_tabla_cerrada(self) -> None:
        """P5/D5: la acción de cada escalada es miembro de la tabla
        cerrada evento→acción (solo acciones reversibles y
        proporcionadas); ninguna decisión fuera de la tabla."""
        trace = self.write_trace(unknown_signal_trace())

        env = self.classify_envelope(trace)

        escalations = env.get("escalations")
        self.assertIsInstance(
            escalations, list, msg="P5: canal `escalations` obligatorio")
        self.assertTrue(
            escalations,
            msg="P5 (precondición del oráculo): el caso ambiguo debe "
                "producir una escalada para poder auditar su acción")
        for esc in escalations:
            action = esc.get("action")
            self.assertIsInstance(
                action, str,
                msg="P5/D5: la escalada debe declarar una acción "
                    "concreta")
            self.assertIn(
                action, CLOSED_ACTION_TABLE,
                msg="P5/D5: la acción debe pertenecer a la TABLA CERRADA "
                    f"evento→acción {sorted(CLOSED_ACTION_TABLE)}; got "
                    f"{action!r} — cualquier otra acción es una decisión "
                    "autónoma encubierta")


class TestP5LegitimateProgressDoesNotEscalate(EstablishedProjectCase):
    """P5/P7 — el trabajo legítimo y progresivo no escala ni recibe
    intervención (nota del orquestador)."""

    def test_p05_trabajo_legitimo_progresivo_no_escala(self) -> None:
        """P5/P7: 6 llamadas equivalentes con progreso real en cada tramo
        de 3 → cero escaladas y cero incidentes: la intervención solo
        ocurre bajo condiciones claras y proporcionadas."""
        trace = self.write_trace(progressive_trace())

        env = self.classify_envelope(trace)

        self.assertIn(
            "escalations", env,
            msg="P5/D10: el canal `escalations` es parte del contrato "
                "estable classify-v1 y debe exponerse siempre (aunque "
                "venga vacío)")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P5/P7: trabajo legítimo y PROGRESIVO no debe escalar; "
                f"got={env.get('escalations')!r}")
        self.assertEqual(
            env.get("incidents"), [],
            msg="P5/P7: trabajo legítimo y progresivo no debe recibir "
                "intervención (sin incidentes); "
                f"got={env.get('incidents')!r}")


class TestP5LoneTimeoutIsNotBlockage(EstablishedProjectCase):
    """P5 + invariante 3 — un timeout SOLO no prueba bloqueo."""

    def test_p05_timeout_solo_no_prueba_bloqueo_ni_escala(self) -> None:
        """P5/invariante 3: una única llamada con resultado `timeout` no
        puede alarmar, escalar ni declarar bloqueo — la lentitud aislada
        no es evidencia de bloqueo (sin fabricar fracaso)."""
        trace = self.write_trace(lone_timeout_trace())

        env = self.classify_envelope(trace)

        self.assertIn(
            "escalations", env,
            msg="P5/D10: el canal `escalations` debe exponerse siempre")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P5/invariante 3: un timeout SOLO no prueba bloqueo — no "
                f"debe escalar; got={env.get('escalations')!r}")
        self.assertEqual(
            env.get("incidents"), [],
            msg="P5/invariante 3: un timeout aislado no debe producir "
                f"incidente alguno; got={env.get('incidents')!r}")


if __name__ == "__main__":
    unittest.main()
