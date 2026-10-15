#!/usr/bin/env python3
"""003-003 T4 — fixtures de trazas + generalidad + simulación declarada.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P6, P8 — generalidad; plan.md
  §4: trabajo legítimo progresivo sin intervención).
- docs/specs/003-003-progress-guards/plan.md (T4; test focal declarado
  `tests/test_003_003_t4_fixtures.py`; fixtures bajo
  `tests/fixtures/003_003/**`; regresión: `tests/validate-consistency.sh`).
- docs/specs/003-003-progress-guards/guards-incidents-observed.md
  (incuentes reales reconstruidos: C2 suite en segundo plano que muere con
  la sesión; C1 turno cerrado esperando ser retomado).

Postcondiciones bajo prueba:

- **P6 (fixtures de trazas).** Fixtures cubren bucle, progreso real,
  polling, flaky y crash; sin repetir un desarrollo completo; los
  escenarios de fallo provocado etiquetados **simulation**; los que
  reconstruyen incidentes reales observados llevan
  **reconstruction-of-real-incident** con su referencia a
  guards-incidents-observed.md — no son fallos provocados.
- **P8 (generalidad).** Proyecto Go con tests co-ubicados (fixture
  `go-project/`, test junto al código, convención Go) y ciclo sin código
  (documental) con progreso: la misma superficie `classify` los maneja sin
  casos especiales; un ciclo sin código CON progreso NO recibe
  intervención (P7 dentro del alcance de T4/plan §4).

Superficie observable (fijada en RED de T1–T3, §3/V7):

    python3 scripts/cdad_guard.py classify \
        --project-root ROOT --trace TRACE.json  # traza trace-v1 grabada

Envolvente `classify-v1`: `incidents`, `polls`, `escalations` (canal
estable, D10: siempre presente) + `simulation`/`session_id` eco de la
traza.

Comportamiento esperado por fixture (derivado del contrato, no del
código): bucle → 1 incidente con evidencia de equivalencia; progreso →
sin alerta; polling → wait pre-deadline, escala UNA VEZ vencido, sin
re-escalado; flaky → sin alerta (huella distingue clases de resultado,
D2); crash → unknown + escalada, sin fabricar resultado (invariante 4);
reconstrucciones C1/C2 → unknown + escalada al orquestador (límites de
observabilidad declarados; la ausencia de evidencia es débil).

Nota de honestidad RED (T4 tras T1–T3 en verde): este test verifica los
FIXTURES y el comportamiento del guard ya desplegado sobre ellos; si
todo pasa, se reporta tal cual (sin RED artificial); aserciones de
comportamiento ausente fracasarían por AssertionError, nunca por
ImportError.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (T1)
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "003_003"

FEATURE_ID = "003-003-progress-guards"

# Tope duro: un clasificador determinista nunca puede colgarse.
CLASSIFY_TIMEOUT_S = 120

# Tabla CERRADA evento→acción (D5, spec §8) — la misma de T3.
CLOSED_ACTION_TABLE = {
    "backoff-poll",
    "retry-with-change",
    "repackage",
    "new-session-from-checkpoint",
    "escalate",
    "recommend-block",
}

# P6 — escenarios obligatorios de fallo provocado (etiqueta simulation).
SIMULATED_SCENARIOS = ("loop", "progress", "polling", "flaky", "crash")

# P6 — reconstrucciones de incidentes reales (NO provocados): referencia
# obligatoria a guards-incidents-observed.md.
RECONSTRUCTIONS = {
    "background-suite-death": "C2",
    "closed-turn-awaiting-resume": "C1",
}

# P8 — fixtures de generalidad (Go co-ubicado + ciclo sin código).
GENERALITY_FIXTURES = ("go-project-trace", "doc-cycle")


# ---------------------------------------------------------------- helpers


class FixtureCase(unittest.TestCase):
    """Fixture grabado bajo tests/fixtures/003_003 corre sobre un
    proyecto sintético (tempdir): classify es read-only (invariante 1)."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t4-")
        self.addCleanup(
            lambda: shutil.rmtree(self._tmp, ignore_errors=True))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    def install_fixture(self, name: str) -> Path:
        """Copia el fixture grabado (verbatim) al proyecto sintético."""
        src = FIXTURES_DIR / f"{name}.json"
        self.assertTrue(
            src.is_file(),
            msg="precondición: el fixture " f"{name}.json debe existir "
                f"bajo tests/fixtures/003_003 (P6)")
        dst = self.root / "fixture" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        return dst

    def run_classify(self, trace: Path):
        """Corrida del CLI classify (V7) con tope de tiempo."""
        try:
            return subprocess.run(
                [sys.executable, str(GUARD_SCRIPT), "classify",
                 "--project-root", str(self.root), "--trace", str(trace)],
                cwd=REPO_ROOT, capture_output=True, timeout=CLASSIFY_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "T4: classify no terminó dentro de "
                f"{CLASSIFY_TIMEOUT_S}s; got timeout={exc!r}")

    def classify_envelope(self, trace: Path) -> tuple:
        """classify → (rc 0, sin traceback, envolvente completa)."""
        proc = self.run_classify(trace)
        self.assertNotIn(
            "unrecognized", proc.stdout.decode("utf-8", errors="replace"),
            msg="T4: el comando `classify --project-root --trace` de §3 "
                "es la superficie obligatoria de los fixtures")
        self.assertEqual(
            proc.returncode, 0,
            msg="T4: classify debe clasificar el fixture con éxito (rc 0);"
                f" rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", proc.stderr.decode("utf-8", errors="replace"),
            msg="T4: classify terminó con traceback sobre el fixture")
        env = json.loads(proc.stdout.decode("utf-8"))
        self.assertEqual(
            env.get("schema_version"), 1,
            msg="T4: la envolvente classify-v1 declara schema_version=1")
        # D10: los tres canales son parte del contrato estable — la
        # envolvente los expSIEMPRE (aunque vengan vacíos).
        for channel in ("incidents", "polls", "escalations"):
            self.assertIsInstance(
                env.get(channel), list,
                msg=f"T4 (D10): el canal `{channel}` debe estar siempre "
                    "presente en la envolvente classify-v1")
        return proc, env


# ---------------------------------------------------------------- tests


class TestP6FixtureVocabulary(unittest.TestCase):
    """P6 — etiquetado y vocabulario de los fixtures grabados."""

    def test_p06_archivos_y_etiquetas_de_cada_fixture(self) -> None:
        """P6: todo fixture bajo tests/fixtures/003_003 es una traza
        `trace-v1` grabada (schema_version 1, simulation=true — nunca en
        vivo) con etiqueta cerrada: `simulation` (fallo provocado) o
        `reconstruction-of-real-incident` (reconstrucción de incidente
        real observado, con referencia obligatoria). Los 5 escenarios de
        fallo provocado + los 2 de generalidad existen."""
        files = sorted(FIXTURES_DIR.glob("*.json"))
        self.assertTrue(
            files, msg="P6: debe haber fixtures bajo tests/fixtures/003_003")
        labels = {}
        for path in files:
            doc = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                doc.get("schema_version"), 1,
                msg=f"P6 ({path.name}): traza trace-v1 con schema_version 1")
            self.assertEqual(
                doc.get("trace"), "trace-v1",
                msg=f"P6 ({path.name}): el fixture declara su contrato "
                    "trace-v1")
            self.assertIs(
                doc.get("simulation"), True,
                msg=f"P6 ({path.name}): el fixture es grabado/offline "
                    "(simulation=true) — nada corre en vivo")
            label = doc.get("label")
            self.assertIn(
                label, {"simulation", "reconstruction-of-real-incident"},
                msg=f"P6 ({path.name}): la etiqueta cerrada es `simulation` "
                    f"o `reconstruction-of-real-incident`; got={label!r}")
            if label == "reconstruction-of-real-incident":
                ref = doc.get("incident_ref")
                self.assertIsInstance(
                    ref, str,
                    msg=f"P6 ({path.name}): la reconstrucción de un "
                        "incidente real declara su referencia")
                self.assertIn(
                    "guards-incidents-observed", ref,
                    msg=f"P6 ({path.name}): la referencia debe anclar al "
                        "registro real guards-incidents-observed.md")
            labels[path.stem] = label

        for name in SIMULATED_SCENARIOS + GENERALITY_FIXTURES:
            self.assertEqual(
                labels.get(name), "simulation",
                msg=f"P6: el escenario provocado/de generalidad `{name}` "
                    "debe existir con etiqueta simulation")
        for name, caso in RECONSTRUCTIONS.items():
            self.assertEqual(
                labels.get(name), "reconstruction-of-real-incident",
                msg=f"P6: la reconstrucción del incidente real {caso} "
                    f"(`{name}`) debe existir con su etiqueta y referencia")

    def test_p06_reconstrucciones_citan_los_incidentes_reales(self) -> None:
        """P6: las DOS reconstrucciones de incidentes reales (suite en
        segundo plano que muere con la sesión = C2; turno cerrado
        esperando ser retomado = C1) citan su fila en
        guards-incidents-observed.md — correspondencia 1:1 con el
        registro real, nada inventado."""
        for name, caso in RECONSTRUCTIONS.items():
            doc = json.loads(
                (FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))
            ref = doc.get("incident_ref", "")
            self.assertIn(
                "guards-incidents-observed.md", ref,
                msg=f"P6 ({name}): la referencia cita el registro real")
            self.assertIn(
                f"{caso}", ref,
                msg=f"P6 ({name}): la referencia identifica el caso {caso} "
                    "del registro de incidentes")


class TestP6ProvokedScenarios(FixtureCase):
    """P6 — los escenarios provocados (simulation) ejercitan el bucle,
    progreso, polling, flaky y crash sobre la superficie classify."""

    def test_p06_bucle_simulado_detectado_con_evidencia(self) -> None:
        """P6/P1 (loop): 5 llamadas equivalentes sin progreso → UN
        incidente repetition-without-progress con huella, clase de
        resultado, regla explícita y progreso changed=false; dos corridas
        → stdout idéntico (invariante 1)."""
        trace = self.install_fixture("loop")
        before = tree_snapshot(self.root)

        proc, env = self.classify_envelope(trace)
        incidents = env.get("incidents")
        self.assertEqual(
            len(incidents), 1,
            msg=f"P6/P1: el bucle del fixture debe producir UN incidente; "
                f"got={incidents!r}")
        inc = incidents[0]
        self.assertEqual(
            inc.get("kind"), "repetition-without-progress",
            msg="P6/P1: clasificación de repetición sin progreso")
        self.assertEqual(
            inc.get("count"), 5,
            msg="P6/P1: el incidente atribuye las 5 ocurrencias del "
                "fixture")
        self.assertTrue(
            (inc.get("rule") or "").strip(),
            msg="P6/P1: regla explícita no vacía (sin regla no hay "
                "detección)")
        self.assertTrue(
            (inc.get("fingerprint") or "").strip(),
            msg="P6/P1: huella canónica no vacía (evidencia D2)")
        self.assertEqual(
            inc.get("result_class"), "tool-error",
            msg="P6/P1: la clase de resultado cerrada figura en la "
                "evidencia")
        self.assertIs(
            (inc.get("evidence") or {}).get("progress", {}).get("changed"),
            False, msg="P6/P1: el POR QUÉ incluye cero cambio de progreso")

        proc2 = self.run_classify(trace)
        self.assertEqual(
            proc2.stdout, proc.stdout,
            msg="P6 (invariante 1): classify determinista sobre el fixture")

        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P6 (invariante 1): classify read-only sobre el proyecto")

    def test_p06_progreso_real_simulado_sin_alerta(self) -> None:
        """P6/P7 (progress): trabajo equivalente pero progresivo (token
        avanza en cada tramo de 3) → cero incidentes y cero escaladas."""
        trace = self.install_fixture("progress")
        _, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg="P6/P7: ejecución larga saludable no se alerta")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P6/P7: sin intervención — la ejecución continúa")

    def test_p06_polling_simulado_no_se_corta_y_escala_una_vez(self) -> None:
        """P6/P2 (polling): condición/deadline/cadencia válidos — encuestas
        pre-deadline: `wait` (no se corta); al vencer: `escalate` UNA sola
        vez; encuestas posteriores sin cambio relevante: sin re-escalado
        (dedup, P7/O3) y sin paquete de escalada duplicado."""
        trace = self.install_fixture("polling")
        _, env = self.classify_envelope(trace)
        polls = env.get("polls")
        decisions = [p.get("decision") for p in polls]
        self.assertEqual(
            decisions, ["wait", "wait", "escalate", "wait"],
            msg=f"P6/P2: pre-deadline wait, vencido escala una vez, "
                f"posterior sin re-escalado; got decisions={decisions!r}")
        self.assertEqual(
            sum(1 for d in decisions if d == "escalate"), 1,
            msg="P2: al vencer se escala UNA SOLA VEZ")
        self.assertEqual(
            env.get("incidents"), [],
            msg="P2: un polling justificado no es incidente")

    def test_p06_flaky_simulado_no_alarma(self) -> None:
        """P6/C3 (flaky): mismo comando que alterna resultado
        (tool-error/ok) con progreso que avanza — la huella canónica
        incluye la clase de resultado (D2), NO es repetición equivalente:
        sin incidentes ni escaladas (distinción no-alarma C3)."""
        trace = self.install_fixture("flaky")
        _, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg="P6/C3: un test flaky que alterna y progresa no es "
                "repetición equivalente sin progreso")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P6/C3: la relectura justificada/go test intermitente no "
                "vuelve al orquestador")

    def test_p06_crash_simulado_unknown_sin_fabricar(self) -> None:
        """P6/invariante 4 (crash): la llamada in-flight que muere con la
        sesión deja resultado unobservable (`unknown`) ⇒ escalada única
        `unknown: true` con límite declarado y paquete accionable; SIN
        fabricar éxito ni fracaso (nada que declare 'pasó' la suite)."""
        trace = self.install_fixture("crash")
        _, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg="invariante 4: un crash con señal no fiable no se clasifica"
                " como bloqueo/repetición (no se fabrica fracaso)")
        escalations = env.get("escalations")
        self.assertEqual(
            len(escalations), 1,
            msg=f"P5: el crash vuelve al orquestador como UN paquete; "
                f"got={escalations!r}")
        esc = escalations[0]
        self.assertIs(
            esc.get("unknown"), True,
            msg="invariante 4: sin señal fiable ⇒ `unknown` explícito")
        self.assertIs(
            esc.get("decision_needed"), True,
            msg="P5: la decisión semántica vuelve al orquestador")
        self.assertIn(
            esc.get("action"), CLOSED_ACTION_TABLE,
            msg="P5/D5: la acción pertenece a la tabla cerrada")
        self.assertTrue(
            (esc.get("limitation") or "").strip(),
            msg="invariante 4/10: el límite de observabilidad se declara")
        package = esc.get("package") or {}
        self.assertTrue(
            (package.get("summary") or "").strip()
            and (package.get("evidence") or "").strip(),
            msg="P5: el paquete de escalada es breve y accionable")


class TestP6RealIncidentReconstructions(FixtureCase):
    """P6 — reconstrucciones de incidentes reales (NO provocados):
    unknown + escalada al orquestador, sin fabricar resultado."""

    def _check_unknown_reconstruction(self, name: str, caso: str) -> None:
        trace = self.install_fixture(name)
        _, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg=f"P6 ({caso}): la ausencia de evidencia es DÉBIL (podría "
                "estar pendiente) — no se fabrica fracaso como incidente")
        escalations = env.get("escalations")
        self.assertEqual(
            len(escalations), 1,
            msg=f"P6 ({caso}): el incidente real vuelve al orquestador "
                f"como UN paquete breve; got={escalations!r}")
        esc = escalations[0]
        self.assertIs(
            esc.get("unknown"), True,
            msg=f"P6 ({caso}): límite declarado — el runtime no expone el "
                "exit del proceso hijo ni si la sesión entregó ⇒ unknown")
        self.assertIs(
            esc.get("decision_needed"), True,
            msg=f"P6 ({caso}): reanudar vs. redespachar/citar corrida "
                "equivale a decisión semántica del orquestador")
        self.assertIn(
            esc.get("action"), CLOSED_ACTION_TABLE,
            msg=f"P6 ({caso}): acción de la tabla cerrada (D5)")
        package = esc.get("package") or {}
        self.assertTrue(
            (package.get("evidence") or "").strip(),
            msg=f"P6 ({caso}): el paquete cita la evidencia (traza "
                "reconstruida con su referencia real)")

    def test_p06_c2_suite_en_segundo_plano_muere_con_la_sesion(self) -> None:
        """P6/C2 (reconstruction-of-real-incident): la suite lanzada en
        segundo plano no deja evidencia durable y muere con la sesión →
        unknown=true + decisión del orquestador (citar corrida equivale;
        si no, re-ejecutar una vez en primer plano). Nunca 'la suite
        pasó' fabricado."""
        self._check_unknown_reconstruction("background-suite-death", "C2")

    def test_p06_c1_turno_cerrado_esperando_ser_retomado(self) -> None:
        """P6/C1 (reconstruction-of-real-incident): el turno se cierra
        «esperando ser retomado automáticamente» sin entrega final →
        unknown=true + decisión del orquestador (reanudar la misma sesión
        con trabajo preservado). Nunca 'entregó por otra vía' fabricado."""
        self._check_unknown_reconstruction(
            "closed-turn-awaiting-resume", "C1")


class TestP8Generalidad(FixtureCase):
    """P8 (generalidad) — proyecto Go con tests co-ubicados y ciclo sin
    código: la misma superficie classify los maneja sin intervención."""

    def _fixture(self, name: str) -> dict:
        return json.loads(
            (FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))

    def test_p08_proyecto_go_con_tests_co_ubicados(self) -> None:
        """P8 (generalidad): el fixture Go tiene el test CO-UBICADO junto
        al código (misma carpeta/package) y el proyecto compila con su
        suite en verde — la generalidad se prueba contra un proyecto Go
        real, no contra la palabra 'go' en una traza."""
        kata = FIXTURES_DIR / "go-project" / "kata"
        code = kata / "kata.go"
        colocated = kata / "kata_test.go"
        self.assertTrue(
            code.is_file() and colocated.is_file(),
            msg="P8: el fixture Go debe tener código y test co-ubicados "
                "(mismo directorio de package)")
        go = shutil.which("go")
        if not go:  # pragma: no cover — entorno sin toolchain
            self.skipTest("toolchain Go no disponible en este entorno")
        proc = subprocess.run(
            [go, "test", "./..."], cwd=FIXTURES_DIR / "go-project",
            capture_output=True, timeout=200)
        self.assertEqual(
            proc.returncode, 0,
            msg="P8: el proyecto Go co-ubicado del fixture compila y su "
                f"test pasa; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

    def test_p08_traza_go_progresiva_sin_intervencion_y_determinista(
            self) -> None:
        """P8/P7: la traza del proyecto Go (test co-ubicado, ciclo
        rojo→verde, progreso avanzando) → cero incidentes/escaladas
        (sin intervención) y salida determinista entre corridas."""
        trace = self.install_fixture("go-project-trace")
        before = tree_snapshot(self.root)
        proc, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg="P8/P7: el desarrollo Go legítimo y progresivo continúa "
                "sin alerta")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P8/P7: sin intervención ni paquete al orquestador")
        proc2 = self.run_classify(trace)
        self.assertEqual(
            proc2.stdout, proc.stdout,
            msg="P8 (invariante 1): classify determinista también sobre "
                "la traza Go")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P8 (invariante 1): read-only sobre el proyecto Go")

    def test_p08_ciclo_documental_progresivo_sin_intervencion(self) -> None:
        """P8 (D9 observable_check): ciclo SIN CÓDIGO (solo documentación)
        con progreso que avanza → cero incidentes/escaladas — el guard no
        asume un proyecto de software y NO recibe intervención (P7), con
        classify read-only (invariante 1)."""
        doc = self._fixture("doc-cycle")
        self.assertEqual(
            [e["tool"] for e in doc["entries"]],
            ["edit", "edit", "edit", "edit"],
            msg="precondición (fixture): el ciclo documental solo edita "
                "documentación — sin código")
        trace = self.install_fixture("doc-cycle")
        before = tree_snapshot(self.root)
        _, env = self.classify_envelope(trace)
        self.assertEqual(
            env.get("incidents"), [],
            msg="P8/P7: el ciclo documental con progreso no recibe "
                "intervención")
        self.assertEqual(
            env.get("escalations"), [],
            msg="P8/P7: sin escalada — sigue su curso")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P8 (invariante 1): read-only también sobre el ciclo "
                "documental")


if __name__ == "__main__":
    unittest.main()
