#!/usr/bin/env python3
"""003-003 T1 RED — núcleo de traza + repetición equivalente sin progreso.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P1, P7 — T1)
- docs/specs/003-003-progress-guards/plan.md (T1; test focal declarado
  `tests/test_003_003_t1_repetition.py`).

Superficie observable bajo prueba (V7: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_guard.py classify \
        --project-root ROOT \
        --trace TRACE.json          # traza grabada / fixture (trace-v1)

Envolvente de salida (JSON en stdout, contract `classify-v1`):

    {
      "schema_version": 1,
      "trace": "trace-v1",
      "simulation": true,
      "session_id": "...",
      "incidents": [
        {
          "kind": "repetition-without-progress",
          "rule": "<regla explícita, no vacía>",
          "fingerprint": "<huella canónica no vacía>",
          "result_class": "<clase de resultado cerrada>",
          "count": <número de llamadas equivalentes>,
          "evidence": {
            "progress": {"changed": false}
          }
        }
      ],
      "polls": []
    }

Entrada: traza `trace-v1` grabada (fixture determinista, offline, etiquetada
**simulación** — P6); cada entrada lleva `kind`, `tool`, `args` (campos
estables), `result_class`, `progress_token` (digest de progreso en
git/artefacto/state) y `at` (RFC3339 UTC). La huella canónica es
herramienta + argumentos canonicalizados + clase de resultado (D2) y vive en
el guard, no en este test — el test solo exige que distinga llamadas
distintas y que sea determinista (invariante 1).

Escenarios cubiertos (incidente real 2.073 reintentos como referencia de
señal; aquí 5 réplicas → regla conservadora explicita el disparo):

- P1: N llamadas equivalentes (misma huella: herramienta + args + clase de
  resultado) con cero progreso observable (`progress_token` constante) →
  incidente único con evidencia de POR QUÉ son equivalentes (fingerprint +
  result_class + progreso sin cambio) y regla explícita no vacía.
- P1 (evidencia): la huella distingue llamadas con argumentos distintos
  (dos bucles de herramientas distintas → fingerprints distintos).
- P7: trabajo equivalente pero PROGRESIVO (el token de progreso avanza en
  cada tramo de 3 llamadas) → sin incidente, sin intervención.
- P7: nueva hipótesis (args distintos, regla de dos intentos) → sin
  incidente aunque no haya progreso aún.
- Invariante 1: `classify` es determinista (dos corridas → stdout idéntico)
  y read-only (el árbol del proyecto no cambia).

RED hoy: `scripts/cdad_guard.py` (y su cuerpo
`skills/cdad-cycle/scripts/cdad_guard.py`) no existen aún; cada aserción
positiva fracasa por comportamiento ausente (rc≠0 con el mensaje que prima
`el comando classify no existe aún`), no por ImportError.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (aún inexistente)
# Cuerpo real declarado en plan.md T1: skills/cdad-cycle/scripts/cdad_guard.py

FEATURE_ID = "003-003-progress-guards"

# Thr para la señal de bucle: 5 réplicas equivalentes sin progreso son
# inconfundibles para cualquier umbral conservador del intérvalo [2..5].
LOOP_CALLS = 5

# Clase de resultado cerrada del fixture (§ C3: error de herramienta).
RESULT_CLASS_LOOP = "tool-error"


# ---------------------------------------------------------------- fixtures


def loop_trace(*, progress_tokens: list[str] | None = None,
               tool: str = "bash", args: list[str] | None = None) -> dict:
    """Traza `trace-v1` etiquetada **simulación** (P6): bucle equivalente.

    `args` idénticas en todas las entradas → misma huella canónica (D2).
    Sin `progress_tokens`, el token es constante (LOOP_CALLS entradas) →
    cero progreso observable. Con `progress_tokens`, la traza tiene una
    entrada por token (`len(progress_tokens)` entradas, con o sin
    LOOP_CALLS) y cada token marca el progreso observable tras esa
    llamada.
    """
    args = args if args is not None else ["python", "-m", "pytest"]
    tokens = (progress_tokens if progress_tokens is not None
              else ["p0"] * LOOP_CALLS)
    return {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,          # fallo provocado: etiqueta obligatoria (P6)
        "session_id": "sess-sim-loop-2073",
        "entries": [
            {
                "i": i + 1,
                "kind": "tool_call",
                "tool": tool,
                "args": args,
                "result_class": RESULT_CLASS_LOOP,
                "progress_token": token,
                "at": f"2026-10-06T00:0{i}:00Z",
            }
            for i, token in enumerate(tokens)
        ],
    }


def hypothesis_trace() -> dict:
    """P7 — nueva hipótesis: dos llamadas con args distintos (huellas
    distintas), aún sin progreso observable; regla de dos intentos."""
    doc = loop_trace()
    doc["session_id"] = "sess-sim-new-hypothesis"
    doc["entries"] = [
        {
            "i": 1, "kind": "tool_call", "tool": "bash",
            "args": ["python", "-m", "pytest", "-k", "hypothesis_a"],
            "result_class": RESULT_CLASS_LOOP,
            "progress_token": "p0", "at": "2026-10-06T00:00:00Z",
        },
        {
            "i": 2, "kind": "tool_call", "tool": "bash",
            "args": ["python", "-m", "pytest", "-k", "hypothesis_b"],
            "result_class": RESULT_CLASS_LOOP,
            "progress_token": "p0", "at": "2026-10-06T00:01:00Z",
        },
    ]
    assert doc["entries"][0]["args"] != doc["entries"][1]["args"]
    return doc


# ---------------------------------------------------------------- helpers


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con trazas grabadas como fixtures."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t1-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    def write_trace(self, doc: dict) -> Path:
        """Escribe la traza fixture bajo el proyecto y la devuelve."""
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "fixture" / "trace.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        # Autochequeo del fixture: el escenario de fallo va etiquetado
        # simulación (P6) — la etiqueta se escribe, no se asume.
        loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(loaded.get("simulation") is True,
                        msg="fixture (precondición): la traza de fallo "
                            "provocado debe quedar etiquetada simulación")
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
            msg="P1: el comando `classify` no existe aún (RED por CLI "
                "ausente): el argv `classify --project-root --trace` "
                "declarado en §3 es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg="P1/P7: el comando `classify` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="P1/P7: classify terminó con traceback")
        self.env = json.loads(proc.stdout.decode("utf-8"))
        return proc


# ---------------------------------------------------------------- tests


class TestP1RepetitionWithoutProgress(EstablishedProjectCase):
    """P1 — repetición equivalente sin progreso detectada con regla
    explícita y evidencia de equivalencia."""

    def test_p01_bucle_equivalente_sin_progreso_genera_incidente_unico(self) -> None:
        """P1: 5 llamadas equivalentes (misma huella) con token de progreso
        constante → UN incidente `repetition-without-progress` que cubre las
        5 ocurrencias, con huella canónica no vacía, clase de resultado,
        regla explícita no vacía y evidencia de por qué son equivalentes
        (progreso `changed: false`).

        Invariante 1: dos corridas sobre la misma traza → stdout idéntico
        (determinista). `classify` es read-only (árbol intacto)."""
        trace = self.write_trace(loop_trace())
        before = tree_snapshot(self.root)

        proc = self.classify_envelope(trace)
        env = self.env

        incidents = env.get("incidents")
        self.assertIsInstance(
            incidents, list,
            msg="P1: la envolvente classify-v1 debe exponer `incidents`")
        self.assertEqual(
            len(incidents), 1,
            msg=f"P1: el bucle equivalente de {LOOP_CALLS} llamadas sin "
                f"progreso debe producir UN incidente; got={incidents!r}")
        inc = incidents[0]

        self.assertEqual(
            inc.get("kind"), "repetition-without-progress",
            msg="P1: el incidente debe clasificarse como "
                "repetición sin progreso")
        rule = inc.get("rule")
        self.assertIsInstance(
            rule, str,
            msg="P1: el incidente debe declarar la regla que lo disparó")
        self.assertTrue(
            rule and rule.strip(),
            msg="P1: sin regla explícita no hay detección — el incidente "
                "debe declarar la regla que disparó (no vacía)")
        fingerprint = inc.get("fingerprint")
        self.assertIsInstance(
            fingerprint, str,
            msg="P1: la evidencia de equivalencia exige la huella canónica")
        self.assertTrue(
            fingerprint and fingerprint.strip(),
            msg="P1: la evidencia de equivalencia exige huella canónica "
                "no vacía (D2)")
        self.assertEqual(
            inc.get("result_class"), RESULT_CLASS_LOOP,
            msg="P1: la clase de resultado cerrada debe figurar en la "
                "evidencia de por qué son equivalentes")
        self.assertEqual(
            inc.get("count"), LOOP_CALLS,
            msg=f"P1: el incidente debe atribuir las {LOOP_CALLS} "
                f"ocurrencias equivalentes; got count={inc.get('count')!r}")
        evidence = inc.get("evidence")
        self.assertIsInstance(
            evidence, dict,
            msg="P1: el incidente debe traer evidencia estructurada")
        progress = evidence.get("progress") if evidence else None
        self.assertIsInstance(
            progress, dict,
            msg="P1: la evidencia debe incluir el estado de progreso")
        self.assertIs(
            progress.get("changed"), False,
            msg="P1: el porqué del incidente incluye cero cambio observable "
                "de progreso (token constante)")

        # Invariante 1: determinismo — misma traza, misma salida completa.
        proc2 = self.run_classify(trace)
        self.assertEqual(
            proc2.stdout, proc.stdout,
            msg="P1 (invariante 1): classify es determinista — la segunda "
                "corrida sobre la misma traza debe producir salida idéntica")

        # Invariante 1: read-only — el árbol del proyecto no cambia.
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P1 (invariante 1): classify es read-only — el árbol del "
                "proyecto no debe alterarse")

    def test_p01_la_huella_distingue_llamadas_con_args_distintas(self) -> None:
        """P1 (evidencia de equivalencia): dos bucles con argumentos
        distintos (misma herramienta, misma clase de resultado, sin
        progreso) generan dos incidentes con huellas DISTINTAS — la huella
        captura los argumentos, no solo la herramienta."""
        trace_a = self.write_trace(
            loop_trace(args=["python", "-m", "pytest"]))
        env_a = json.loads(self.classify_envelope(trace_a).stdout.decode())
        fprints_a = [i["fingerprint"] for i in env_a["incidents"]]
        self.assertEqual(len(fprints_a), 1,
                         msg="P1 (precondición del oráculo): el bucle A "
                             "produce exactamente un incidente")

        trace_b = self.write_trace(
            loop_trace(tool="bash",
                       args=["python", "-m", "pytest", "-k", "different"]))
        env_b = json.loads(self.classify_envelope(trace_b).stdout.decode())
        fprints_b = [i["fingerprint"] for i in env_b["incidents"]]
        self.assertEqual(len(fprints_b), 1,
                         msg="P1 (precondición del oráculo): el bucle B "
                             "produce exactamente un incidente")

        self.assertNotEqual(
            fprints_a[0], fprints_b[0],
            msg="P1: la huella canónica debe distinguir llamadas con "
                "argumentos distintos (si no, la evidencia de 'por qué "
                "son equivalentes' es vacía y toda repetición colapsa "
                "en una sola alarma)")


class TestP7NoAlarmOnLegitimateProgress(EstablishedProjectCase):
    """P7 — el trabajo legítimo y progresivo puede continuar: sin
    incidentes, sin intervención."""

    def test_p07_progreso_real_no_genera_alerta(self) -> None:
        """P7: 6 llamadas de huella idéntica cuyo token de progreso avanza
        en CADA tramo de 3 (ninguna ventana de 3 consecutivas queda sin
        cambio observable) → cero incidentes. Ejecución larga pero
        saludable: artificios/state cambian → sin alerta."""
        # Cambio en las posiciones 3,5 → ninguna ventana de 3 sin progreso.
        tokens = ["p0", "p0", "p1", "p1", "p2", "p2"]
        trace = self.write_trace(loop_trace(progress_tokens=tokens))
        # Precondición (fixture coherente): una entrada por token, y en
        # CADA tramo de 3 llamadas consecutivas hay al menos un cambio
        # observable de progreso — así ningún intérvalo de la traza puede
        # leerse como "cero progreso" (la supresión P7 es genuina, no un
        # artefacto de un hueco sin progreso). Verificado aquí, no
        # asumido al guard.
        doc = json.loads(trace.read_text(encoding="utf-8"))
        self.assertEqual(
            len(doc["entries"]), len(tokens),
            msg="fixture (precondición): la traza de progreso debe tener "
                "una entrada por token")
        for a in range(len(tokens) - 2):
            window = tokens[a:a + 3]
            self.assertTrue(
                len(set(window)) > 1,
                msg=f"fixture (precondición): la ventana {a + 1}..{a + 3} "
                    f"{window!r} no debe quedar sin cambio de progreso")
        before = tree_snapshot(self.root)

        proc = self.classify_envelope(trace)
        env = self.env

        self.assertEqual(
            env.get("incidents", []),
            [],
            msg="P7: trabajo equivalente pero PROGRESIVO debe continuar sin "
                f"alerta ni intervención; got={env.get('incidents')!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P7 (invariante 1): sin intervención significa también "
                "que el guard no escribe sobre el proyecto")

    def test_p07_nueva_hipotesis_no_genera_alerta(self) -> None:
        """P7: nueva iteración con hipótesis distinta (args cambian →
        huellas distintas; regla de dos intentos) → cero incidentes aunque
        el progreso observable aún no haya cambiado."""
        trace = self.write_trace(hypothesis_trace())

        self.classify_envelope(trace)
        env = self.env

        self.assertEqual(
            env.get("incidents", []),
            [],
            msg="P7:una nueva iteración por hipótesis distinta (args "
                "diferentes) NO es repetición equivalente y no debe "
                f"alertarse; got={env.get('incidents')!r}")


if __name__ == "__main__":
    unittest.main()
