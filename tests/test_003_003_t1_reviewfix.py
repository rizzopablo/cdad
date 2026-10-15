#!/usr/bin/env python3
"""003-003 T1 review-fix RED — focales B1, B2, B3(b), O1.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P1/P2/P5/P7, invariante 4,
  §3: "Éxito → 0; violación → rc≠0 con diagnóstico por stderr y sin
  salida parcial").
- docs/specs/003-003-progress-guards/review-t1.md (hallazgos B1/B2/B3/O1).
- docs/specs/003-003-progress-guards/review-t1-decision.md (remedio de
  clase: el guard trata «no observado» como dato; una sola ronda).

Un test focal por cierre (nota del orquestador):

- **B1** (→ P5, P7, invariante 4): token de progreso ausente o no-string
  ⇒ señal desconocida ⇒ el guard NO fabrica un incidente afirmando
  progreso congelado (`changed: false` nunca observado). Fail-closed al
  lado no-alarma (D3); el remedio marcador exige `unknown` explícito.
- **B2** (→ §3 del spec): `classify` valida el contrato de entrada
  (`trace=="trace-v1"`, `schema_version==1`, `entries` lista); en desvío
  rc≠0 + diagnóstico por stderr, sin salida parcial. Archivo inexistente
  o JSON ilegible ⇒ rc≠0 con diagnóstico determinista (sin traceback
  crudo).
- **B3(b)** (→ P1/D2, honestidad de la evidencia): la regla emitida en
  cada incidente de repetición NO afirma canonicalizar argumentos; la
  canonicalización es responsabilidad del grabador y vive declarada en
  el contrato `trace-v1`, no en la regla que ejecuta el guard.
- **O1** (→ P5): una encuesta de polling sin condición/deadline válidos
  NO produce un `wait` sin marca: la decisión debe ser `unknown` o llevar
  `justified: false` (el orquestador distingue espera justificada de
  señal desconocida).

Entrada: trazas `trace-v1` offline, deterministas, etiquetadas
**simulación** (P6). Superficie observable: el CLI
`scripts/cdad_guard.py classify` (V7) — ninguna implementación leída;
cada aserción fracasa por comportamiento observable ausente
(AssertionError), no por ImportError.
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
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"

FEATURE_ID = "003-003-progress-guards"

LOOP_CALLS = 5
RESULT_CLASS_LOOP = "tool-error"


# ---------------------------------------------------------------- fixtures


def loop_entries(*, with_token: bool = True,
                 token_value: object = "p0") -> list[dict]:
    """Entradas de bucle equivalente (misma herramienta + args + clase).

    Con `with_token=False` las entradas OMITEN la clave `progress_token`
    (el schema trace-v1 no la exige — B1). Con `token_value` no-string
    (B1: señal malformada) el valor entra tal cual.
    """
    entries = []
    for i in range(LOOP_CALLS):
        entry = {
            "i": i + 1,
            "kind": "tool_call",
            "tool": "bash",
            "args": ["python", "-m", "pytest"],
            "result_class": RESULT_CLASS_LOOP,
            "at": f"2026-10-06T00:0{i}:00Z",
        }
        if with_token:
            entry["progress_token"] = token_value
        entries.append(entry)
    return entries


def trace_doc(entries: list[dict], session_id: str = "sess-sim-reviewfix") -> dict:
    """Envolvente trace-v1 etiquetada **simulación** (P6)."""
    return {
        "schema_version": 1,
        "trace": "trace-v1",
        "simulation": True,
        "session_id": session_id,
        "entries": entries,
    }


def bad_contract_traces() -> list[tuple[str, dict]]:
    """B2 — desvíos de contrato de entrada, uno por validación declarada:
    trace≠trace-v1, schema_version≠1, entries no-lista."""
    base = trace_doc([])
    out = []
    d1 = dict(base); d1["trace"] = "trace-v9"
    out.append(("trace!=trace-v1", d1))
    d2 = dict(base); d2["schema_version"] = 9
    out.append(("schema_version!=1", d2))
    d3 = dict(base); d3["entries"] = "oops"
    out.append(("entries no-lista", d3))
    return out


# ---------------------------------------------------------------- helpers


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con trazas grabadas como fixtures."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t1fix-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    def write_trace(self, doc: dict, name: str = "trace.json") -> Path:
        """Escribe la traza fixture bajo el proyecto y la devuelve."""
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "fixture" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(
            loaded.get("simulation") is True,
            msg="fixture (precondición): la traza de fallo provocado debe "
                "quedar etiquetada simulación")
        return path

    def run_classify(self, trace_arg: str) -> subprocess.CompletedProcess:
        """Corrida del CLI classify (V7) con bytes; trace_arg es una ruta."""
        return subprocess.run(
            [sys.executable, str(GUARD_SCRIPT), "classify",
             "--project-root", str(self.root), "--trace", trace_arg],
            cwd=REPO_ROOT, capture_output=True,
        )

    def classify_ok(self, trace: Path) -> dict:
        """classify → rc==0, sin traceback, envolvente JSON en stdout."""
        proc = self.run_classify(str(trace))
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición: la traza dentro de contrato debe clasificarse "
                f"(rc==0); rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="precondición: classify terminó con traceback")
        return json.loads(proc.stdout.decode("utf-8"))

    def assert_closed_failure(self, proc: subprocess.CompletedProcess,
                              context: str) -> None:
        """B2 — violación de contrato: rc≠0 + diagnóstico stderr + sin
        salida parcial + sin traceback crudo (§3 del spec)."""
        stderr = proc.stderr.decode("utf-8", errors="replace")
        stdout = proc.stdout.decode("utf-8", errors="replace")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"{context}: violación del contrato de entrada debe fallar "
                f"rc≠0 (§3: éxito→0, violación→rc≠0); rc=0 con "
                f"stdout={stdout!r} — un veredicto silenciosamente vacío "
                f"'válido' es evidencia inválida consumida como válida")
        self.assertNotIn(
            "Traceback", stderr,
            msg=f"{context}: el diagnóstico debe ser determinista y "
                "diseñado, no un traceback crudo de la excepción")
        self.assertTrue(
            stderr.strip(),
            msg=f"{context}: la violación debe reportar diagnóstico por "
                "stderr")
        self.assertEqual(
            stdout, "",
            msg=f"{context}: sin salida parcial en stdout al violar el "
                "contrato (§3)")

    def assert_unknown_not_frozen(self, env: dict, context: str) -> None:
        """B1 — remedio: cero incidentes (fail-closed no-alarma) o, si
        existe, evidencia que declare la señal `unknown` y NUNCA
        `progress.changed: false` fabricado."""
        incidents = env.get("incidents", [])
        if not incidents:
            return  # remedio primario: sin incidente desde señal desconocida
        progress = (incidents[0].get("evidence") or {}).get("progress") or {}
        changed = progress.get("changed")
        self.assertIsNone(
            changed,
            msg=f"{context}: el guard afirmó progress.changed={changed!r} "
                "sin haber observado nunca el token de progreso — "
                "señal desconocida no es dato (P5; invariante 4: "
                "desconocido permanece desconocido)")
        self.assertIn(
            "unknown", json.dumps(progress, sort_keys=True),
            msg=f"{context}: si se emite incidente, la evidencia debe "
                "llevar el marcador explícito `unknown` de señal de "
                "progreso no observada (decisión B1)")


# ---------------------------------------------------------------- tests


class TestB1UnobservedProgressTokenIsUnknown(EstablishedProjectCase):
    """B1 → P5/P7/invariante 4: token de progreso ausente o no-string es
    señal desconocida; el guard no fabrica incidente de progreso
    congelado."""

    def test_b1_token_de_progreso_no_observado_no_fabrica_incidente(
            self) -> None:
        """B1: ≥3 llamadas equivalentes SIN `progress_token` (y variante
        con token no-string) → cero incidentes, o incidente con marcador
        `unknown` explícito y sin `changed: false` fabricado.

        RED hoy: `None == None` agrupa las entradas y dispara el
        incidente afirmando `changed: false` que nunca fue observado."""
        cases = [
            ("token ausente", loop_entries(with_token=False)),
            ("token no-string", loop_entries(token_value=42)),
        ]
        for context, entries in cases:
            with self.subTest(caso=context):
                trace = self.write_trace(trace_doc(entries))
                env = self.classify_ok(trace)
                self.assert_unknown_not_frozen(env, f"B1 ({context})")


class TestB2ClassifyValidatesInputContract(EstablishedProjectCase):
    """B2 → §3: entrada fuera de contrato falla cerrada (rc≠0, stderr,
    sin salida parcial, sin traceback)."""

    def test_b2_entrada_fuera_de_contrato_o_ilegible_falla_cerrada(
            self) -> None:
        """B2: (a) tres desvíos de contrato declarados (trace≠trace-v1,
        schema_version≠1, entries no-lista) → rc≠0; (b) archivo
        inexistente y (c) JSON ilegible → rc≠0 con diagnóstico
        determinista. En todos: stderr con mensaje, stdout vacío, sin
        traceback crudo.

        RED hoy: los desvíos se clasifican en silencio con rc=0; los
        errores de archivo/JSON salen con traceback crudo (rc=1 pero
        diagnóstico no diseñado)."""
        for context, doc in bad_contract_traces():
            with self.subTest(caso=f"contrato: {context}"):
                trace = self.write_trace(doc, name="bad-contract.json")
                proc = self.run_classify(str(trace))
                self.assert_closed_failure(proc, f"B2 ({context})")

        # Archivo inexistente (ilegible).
        missing = self.root / "fixture" / "no-existe.json"
        with self.subTest(caso="archivo inexistente"):
            proc = self.run_classify(str(missing))
            self.assert_closed_failure(proc, "B2 (archivo inexistente)")

        # JSON ilegible.
        garbage = self.write_trace_json_garbage()
        with self.subTest(caso="JSON ilegible"):
            proc = self.run_classify(str(garbage))
            self.assert_closed_failure(proc, "B2 (JSON ilegible)")

    def write_trace_json_garbage(self) -> Path:
        """Fixture de JSON ilegible (no parseable)."""
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "fixture" / "garbage.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{no es json]]", encoding="utf-8")
        return path


class TestB3bEmittedRuleDoesNotClaimCanonicalization(EstablishedProjectCase):
    """B3(b) → P1/D2: la regla emitida declara solo lo que el guard
    ejecuta; la canonicalización es del grabador (contrato trace-v1)."""

    def test_b3b_la_regla_emitida_no_afirma_canonicalizar_args(self) -> None:
        """B3(b): sobre el incidente de repetición estándar (fixture
        pre-canonicalizado de la suite T1), el texto de la regla emitida
        NO debe afirmar canonicalización de argumentos.

        RED hoy: la regla emitida declara "tool + canonicalized args +
        result_class", pero el guard no canonicaliza nada — la evidencia
        es infiel (D2). Decisión: opción (b), la canonicalización queda
        declarada en el contrato trace-v1 y la regla deja de afirmarlo."""
        trace = self.write_trace(trace_doc(loop_entries()))
        env = self.classify_ok(trace)

        incidents = env.get("incidents", [])
        self.assertTrue(
            incidents,
            msg="precondición (suite T1 GREEN en 4933ed0): el bucle "
                "equivalente debe producir un incidente para poder "
                "examinar el texto de su regla")
        rule = incidents[0].get("rule")
        self.assertIsInstance(
            rule, str,
            msg="precondición: el incidente debe traer la regla explícita")
        self.assertTrue(
            rule and rule.strip(),
            msg="precondición: la regla debe ser no vacía (P1)")

        self.assertNotIn(
            "canonical", rule.lower(),
            msg=f"B3(b): la regla emitida no debe afirmar canonicalización "
                f"de argumentos que el guard no ejecuta — regla={rule!r}; "
                "la canonicalización es responsabilidad del grabador, "
                "declarada en el contrato trace-v1 (decisión B3b)")


class TestO1UnjustifiedPollIsMarkedUnknown(EstablishedProjectCase):
    """O1 → P5: encuesta sin condición/deadline válidos ⇒ decisión
    marcada (`unknown` o `justified: false`), no un `wait` sin marca."""

    def test_o1_poll_sin_condicion_valida_marca_señal_desconocida(
            self) -> None:
        """O1: una encuesta de polling sin condition/deadline (señal de
        justificación ausente) NO debe decidir `wait` sin marca: el
        orquestador debe poder distinguir espera justificada de señal
        desconocida. Decisión esperada: `unknown` o `justified: false`
        en la decisión de esa encuesta.

        RED hoy: la encuesta injustificada decide `wait` sin ninguna
        marca (sonda E: rc=0, `wait`)."""
        entry = {
            "i": 1,
            "kind": "poll",
            "at": "2026-10-06T00:50:00Z",
            # sin condition, deadline ni cadence_seconds
        }
        trace = self.write_trace(trace_doc([entry], "sess-sim-poll-unjust"))

        proc = self.run_classify(str(trace))
        self.assertEqual(
            proc.returncode, 0,
            msg="precondición: la traza dentro de contrato debe "
                f"classificarse; rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        env = json.loads(proc.stdout.decode("utf-8"))

        polls = env.get("polls", [])
        self.assertTrue(
            polls,
            msg="precondición: la encuesta debe recibir una decisión en "
                "`polls`")
        poll = next((p for p in polls if p.get("i") == 1), None)
        self.assertIsNotNone(
            poll, msg="precondición: la decisión debe referenciar la "
                      "entrada i=1")
        decision = poll.get("decision")
        marked = (decision == "unknown") or (poll.get("justified") is False)
        self.assertTrue(
            marked,
            msg=f"O1: la encuesta sin condición/deadline no puede decidir "
                f"`wait` sin marca (P5: el orquestador debe distinguir "
                f"espera justificada de señal desconocida); got "
                f"decision={decision!r} poll={poll!r}")


if __name__ == "__main__":
    unittest.main()
