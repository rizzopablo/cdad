#!/usr/bin/env python3
"""003-003 T1 RED — clasificación de polling legítimo (P2) y su no-alarma.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P2, P7, Distinción "polling
  justificado" — T1)
- docs/specs/003-003-progress-guards/plan.md (T1; test focal declarado
  `tests/test_003_003_t1_polling.py`).

Superficie observable bajo prueba (V7: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_guard.py classify \
        --project-root ROOT \
        --trace TRACE.json          # traza grabada / fixture (trace-v1)

Envolvente de salida (JSON en stdout, contract `classify-v1` / `poll-v1`):

    {
      "schema_version": 1,
      "trace": "trace-v1",
      "simulation": true,
      "session_id": "...",
      "incidents": [],
      "polls": [
        {"i": <entrada de la traza>, "decision": "wait" | "escalate"}
      ]
    }

Entrada: la MISMA superficie `trace-v1` de T1, con entradas de polling:

    {"i": n, "kind": "poll", "condition": "<espera esperada, no vacía>",
     "deadline": "RFC3339 Z", "cadence_seconds": <seg>, "at": "RFC3339 Z"}

Vocabulario de decisiones cerrado (tabla cerrada evento→acción, D5):
- `wait`     : encuesta antes del vencimiento — se CONTINÚA, sin corte. Un
  polling justificado (condición + deadline + cadencia válidos) no se corta
  antes del vencimiento y las entradas pre-deadline NO generan incidentes.
- `escalate` : venció el deadline → escalar UNA SOLA VEZ. Las siguientes
  encuestas pasadas de vencimiento (sin cambio relevante) NO re-escalan
  (dedup de re-alarma, P7/O3).

Fixtures offline y deterministas, etiquetados **simulación** (P6); ninguna
escritura en este repo; no se provoca polling en instancias reales.

RED hoy: `scripts/cdad_guard.py` no existe aún; cada aserción positiva
fracasa por comportamiento ausente (rc≠0 con el mensaje que prima
`el comando classify no existe aún`), no por ImportError.
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
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (aún inexistente)

FEATURE_ID = "003-003-progress-guards"

POLL_CONDITION = "job-status==done"
POLL_DEADLINE = "2026-10-06T01:00:00Z"


# ---------------------------------------------------------------- fixtures


def poll_entry(i: int, at: str) -> dict:
    """Una encuesta de polling con condición, deadline y cadencia válidos."""
    return {
        "i": i,
        "kind": "poll",
        "condition": POLL_CONDITION,
        "deadline": POLL_DEADLINE,
        "cadence_seconds": 60,
        "at": at,
    }


def poll_trace(*, before: list[tuple[int, str]],
               after: list[tuple[int, str]]) -> dict:
    """Traza `trace-v1` de polling etiquetada **simulación**.

    `before` = encuestas ANTES del vencimiento; `after` = encuestas
    PAST el vencimiento. Cadencia respetada en todas (≥60s entre at).
    """
    entries = [poll_entry(i, at) for i, at in before + after]
    return {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,          # escenario de simulación (P6)
        "session_id": "sess-sim-poll-valid",
        "entries": entries,
    }


# ---------------------------------------------------------------- helpers


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con trazas grabadas como fixtures."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t1poll-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"

    def write_trace(self, doc: dict) -> Path:
        """Escribe la traza fixture bajo el proyecto y la devuelve."""
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "fixture" / "trace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        # Autochequeo del fixture: etiqueta simulación presente (P6).
        loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(loaded.get("simulation") is True,
                        msg="fixture (precondición): la traza de polling "
                            "simulado debe estar etiquetada simulación")
        return path

    def run_classify(self, trace: Path) -> subprocess.CompletedProcess:
        """Corrida del CLI classify (V7) con bytes."""
        return subprocess.run(
            [sys.executable, str(GUARD_SCRIPT), "classify",
             "--project-root", str(self.root), "--trace", str(trace)],
            cwd=REPO_ROOT, capture_output=True,
        )

    def classify_envelope(self, trace: Path) -> subprocess.CompletedProcess:
        """classify → (rc==0, sin traceback, stdout JSON parseable)."""
        proc = self.run_classify(trace)
        self.assertNotIn(
            "unrecognized", proc.stdout.decode("utf-8", errors="replace"),
            msg="P2: el comando `classify` no existe aún (RED por CLI "
                "ausente): el argv `classify --project-root --trace` "
                "declarado en §3 es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg="P2: el comando `classify` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="P2: classify terminó con traceback")
        self.env = json.loads(proc.stdout.decode("utf-8"))
        return proc

    def decisions_by_entry(self) -> dict[int, str]:
        """Mapa {i: decision} de la envolvente; cada entrada una decisión."""
        polls = self.env.get("polls")
        self.assertIsInstance(
            polls, list,
            msg="P2: la envolvente debe exponer `polls` con la decisión "
                "por encuesta (`poll-v1`)")
        mapping: dict[int, str] = {}
        for poll in polls:
            self.assertIsInstance(
                poll, dict, msg="P2: cada decisión de polling es un objeto")
            i = poll.get("i")
            decision = poll.get("decision")
            self.assertIn(
                i, (1, 2, 3, 4),
                msg=f"P2: la decisión debe referenciar una entrada de la "
                    f"traza; got i={i!r}")
            self.assertNotIn(
                i, mapping,
                msg=f"P2: la encuesta i={i} debe tener exactamente una "
                    f"decisión (distinta de encuestas duplicadas)")
            self.assertIsInstance(
                decision, str,
                msg=f"P2: cada decisión es una cadena; got {decision!r} "
                    f"para la encuesta i={i}")
            mapping[i] = decision
        return mapping


# ---------------------------------------------------------------- tests


class TestP2ValidPollNotCutBeforeDeadline(EstablishedProjectCase):
    """P2 — polling legítimo no se corta antes del vencimiento."""

    def test_p02_polling_valido_antes_del_vencimiento_continua_sin_alerta(
            self) -> None:
        """P2: encuestas ANTES del vencimiento con condición/cadencia
        válidas → decisión `wait` para cada una y CERO incidentes: un
        polling justificado no se corta y no genera alarma (Distinción
        "polling justificado"; P7)."""
        trace = self.write_trace(poll_trace(
            before=[(1, "2026-10-06T00:50:00Z"), (2, "2026-10-06T00:59:00Z")],
            after=[],
        ))

        self.classify_envelope(trace)
        env = self.env

        mapping = self.decisions_by_entry()
        self.assertEqual(
            {1: "wait", 2: "wait"}, mapping,
            msg=f"P2: antes del vencimiento la decisión es continuar "
                f"(`wait`), nunca cortar ni escalar; got={mapping!r}")
        self.assertEqual(
            env.get("incidents", []),
            [],
            msg="P2: polling justificado dentro del plazo no genera "
                "incidentes (no hay repetición improductiva que señalar)")
        self.assertFalse(
            any(p.get("decision") == "escalate" for p in env.get("polls", [])),
            msg="P2: antes del vencimiento no existe escalado")


class TestP2EscalatesExactlyOnceAfterDeadline(EstablishedProjectCase):
    """P2 — al vencer el plazo se escala una sola vez."""

    def test_p02_al_vencer_escala_una_sola_vez_y_no_repito_dictamen(
            self) -> None:
        """P2: con la traza extendida PASADA de vencimiento, la primera
        encuesta post-deadline decide `escalate` y las siguientes (sin
        cambio relevante) no re-escalan: exactamente UN `escalate` en
        toda la envolvente."""
        trace = self.write_trace(poll_trace(
            before=[(1, "2026-10-06T00:50:00Z")],
            after=[(2, "2026-10-06T01:02:00Z"), (3, "2026-10-06T01:03:00Z")],
        ))

        self.classify_envelope(trace)
        env = self.env

        mapping = self.decisions_by_entry()
        self.assertEqual(
            mapping.get(1), "wait",
            msg="P2 (precondición): la encuesta previa al vencimiento "
                "sigue sin cortar")
        escalations = [i for i, d in mapping.items() if d == "escalate"]
        self.assertEqual(
            escalations, [2],
            msg=f"P2: al vencer el deadline se escala UNA sola vez — la "
                f"primera encuesta post-deadline (i=2); got "
                f"escalamientos={escalations!r} decisiones={mapping!r}")
        self.assertNotEqual(
            mapping.get(3), "escalate",
            msg="P2: la segunda encuesta post-deadline (i=3, sin cambio "
                "relevante) no vuelve a escalar")


if __name__ == "__main__":
    unittest.main()
