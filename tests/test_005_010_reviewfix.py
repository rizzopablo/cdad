#!/usr/bin/env python3
"""005-010 RED review-fix — hallazgos R1/R2/R3/R4 del review formal
(docs/specs/005-010-real-opencode-delegation/review.md, decisión del
orquestador: R1/R2/R3/R4 se corrigen; R5-R7 deuda) sobre la SPEC aprobada.

Contract: docs/specs/005-010-real-opencode-delegation/spec.md (PD-1, PD-2,
PD-5, PD-6; INV-4, INV-5) + review.md (hallazgos R1..R4). Misma superficie
observable del oráculo T1 (proyecto sintético en tempdir, binario falso
como frontera de proceso: NINGUNA lectura de implementación, ningún
runtime vivo). Los tests observan SOLO artefactos durables:

  - el argv/registro del binario falso (`<fake>/calls.jsonl`);
  - la base SQLite del fixture (campo `sessions_db` de la config);
  - el registro I8 del intento del worker
    (`.cdad/executions/<id>/dispatches/<attempt>.json`, esquema cerrado);
  - el recibo durable (`.cdad/runtime/results/<exec>/<packet>/receipt.json`);
  - el envelope {attempt, session, termination, delivery_ref, diagnosis}.

Variantes NUEVAS del doble (fixture tests/test_005_009_t2_opencode_
adapter.py — review-fix: NINGUNA variante previa cambia de conducta):

  - `hangs` (R1): la invocación del DESTINO NO RETORNA dentro de la cota
    (duerme más que `wait.timeout_seconds`, nunca escribe fila): el hecho
    material (sin fila / sin idle / cliente sin terminar) es `timeout`,
    NO `transport-error` con un rc que no existe (PD-5: transport-error
    es UN CLIENTE QUE FALLA EN EL TRANSPORTE — hecho observado, no
    fabricado; PD-1/INV-4: sin señal dentro de la espera acotada es
    timeout); el diagnóstico no afirma un rc.
  - binario que NO ARRANCA (R1, contracara): sigue siendo
    `transport-error` (falla real de transporte, PD-5).
  - `succeeded-no-text` (R3): idle 'succeeded' SIN texto final →
    `blocked` con diagnóstico, sin entrega, sin recibo (PD-5: «si falta,
    blocked con diagnóstico»; R-C de §9).
  - `unknown-outcome` (R3): `idle_outcome` NO declarado → `unknown`, sin
    recibo (PD-5: el vocabulario incluye `unknown`).
  - configuración SIN `wait.timeout_seconds` o con valor NO positivo
    (R4): fallo CERRADO ANTES de despachar (blocked con diagnóstico que
    nombra la clave; el binario no se invoca; INV-4: la espera es
    acotada — sin cota positiva declarada no se despacha).
  - `model-object` (R2): la fila durable trae `model` serializado como
    OBJETO JSON {id, providerID}; el registro I8 del worker guarda
    `model_reported` como 'providerID/id' (PD-6: observación útil, no
    el objeto JSON verbatim); con texto plano se conserva tal cual.

Mapa test → postcondición (spec 005-010) y hallazgo:

  1  TestR1TimeoutVsTransportError::test_r1_hanging_invocation_ends_timeout_without_rc_claim
       PD-5/PD-1/INV-4 (R1) — invocación que no retorna en la cota →
       `timeout` (no transport-error); diagnóstico honesto (sin rc).
  2  TestR1TimeoutVsTransportError::test_r1_unstartable_binary_stays_transport_error
       PD-5 (R1 contracara) — binario que no arranca → `transport-error`.
  3  TestR4WaitConfigFailClosed::test_r4_exec_config_without_wait_object_fails_closed_before_dispatch
       PD-1/INV-4 (R4) — sin el objeto `wait` → fallo cerrado
       pre-despacho; el binario no se invoca.
  4  TestR4WaitConfigFailClosed::test_r4_exec_config_without_timeout_seconds_fails_closed_before_dispatch
       PD-1/INV-4 (R4) — sin la clave `timeout_seconds` → fallo cerrado
       pre-despacho; el binario no se invoca.
  5  TestR4WaitConfigFailClosed::test_r4_nonpositive_wait_timeout_fails_closed_before_dispatch
       PD-1/INV-4 (R4) — valor no positivo (0) → fallo cerrado
       pre-despacho; el binario no se invoca.
  6  TestR3IdleOutcomeEdgeVariants::test_r3_succeeded_without_final_text_is_blocked_without_receipt
       PD-5 (R3) — succeeded sin texto final → blocked, sin recibo.
  7  TestR3IdleOutcomeEdgeVariants::test_r3_undeclared_idle_outcome_is_unknown_without_receipt
       PD-5 (R3) — idle_outcome no declarado → unknown, sin recibo.
  8  TestR2ModelReportedFromDurableRow::test_r2_json_object_model_reported_as_provider_over_id
       PD-6 (R2) — objeto JSON de la fila → I8 'providerID/id'.
  9  TestR2ModelReportedFromDurableRow::test_r2_plain_text_row_model_is_preserved
       PD-6 (R2 contracara) — texto plano de la fila → se conserva.

RED esperado (estado vigente post GREEN de 005-010, según review.md):
  (1)  falla: el vigente clasifica TimeoutExpired del destino como
       `transport-error` con diagnóstico que afirma un rc inexistente;
  (3)  falla: sin la clave el vigente despacha SIN cota (despacho +
       completed); (4) falla: cota 0 vence el presupuesto de la
       invocación → `transport-error` en vez de fallo cerrado
       pre-despacho; (7) falla: `model_reported` guarda el objeto JSON
       verbatim de la fila;
  (2)/(5)/(6)/(8) fijan la contracara/ramas ya correctas del producto
       (el review las declara sin cobertura en el doble): pueden pasar
       en este RED — su estado observado se reporta.
Cada fallo RED debe ser AssertionError sobre el COMPORTAMIENTO ausente
(terminación/diagnóstico/provenancia), no import/sintaxis.

A-1 (006-005 U1b, REEMPLAZO DECLARADO en el RED de esa unidad): `:489-500`
(«el registro NUEVO que NO es el de la interfaz») pasa a «el ÚNICO registro
nuevo del despacho»: la interfaz RELAYA el `attempt` del módulo y no registra
(D-14/PD-1), así que el registro del intento ES el que el sobre declara. Las
aserciones sobre `model_reported` desde la fila durable no cambian.
"""

from __future__ import annotations

import json
import re
import time
import unittest

from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import (
    ROW_MODEL,
    ROW_MODEL_NORMALIZED,
    ROW_MODEL_OBJECT,
    TEST_WAIT_TIMEOUT_SECONDS,
    UNKNOWN_OUTCOME,
    AdapterCase,
    durable_last_assistant_text,
    durable_session_rows,
)

# R1 (review): el diagnóstico del caso cuelga NO debe AFIRMAR un rc
# («failed in transport (rc=…)» con un rc que nunca se verificó: el
# cliente no retornó; el adaptador lo mató). Un diagnóstico honesto puede
# DECIR que no hubo rc; no puede aficionar uno con valor.
RC_CLAIM_RE = re.compile(r"rc\s*=\s*[-0-9]")
# Cota superior generosa para probar que la espera NO queda desacotada
# (INV-4): la corrida entera (interfaz + adaptador + cota del fixture) es
# de segundos; márgenes por la sobrecarga interna conocida del adaptador
# (hallazgo de flakiness registrado en la fixture). No fija un número
# interno del producto: la cota declarada es `wait.timeout_seconds`.
BOUNDED_WAIT_UPPER_SECONDS = 30


def assert_diag_actionable(case: unittest.TestCase, out: dict,
                           label: str) -> str:
    """Salida legítima ante bloqueo/terminación no completada: diagnóstico
    accionable no vacío (vocabulario de la spec §2)."""
    diagnosis = out.get("diagnosis")
    case.assertIsInstance(
        diagnosis, str, msg=f"{label}: el diagnóstico no es texto")
    case.assertTrue(
        diagnosis.strip(),
        msg=f"{label}: diagnóstico vacío (la salida legítima exige un "
            f"diagnóstico accionable)")
    return diagnosis


# ------------------------------------------------------------------- R1


class TestR1TimeoutVsTransportError(AdapterCase):
    """R1 (BLOCKING del review, decisión del orquestador: se corrige):
    distinguir el HECHO MATERIAL. Una invocación del destino que NO
    RETORNA dentro de la cota (`hangs`) es `timeout` — sin fila
    correlacionada, sin idle, sin rc —, jamás `transport-error` con un
    diagnóstico que aficione un rc inexistente; un binario que NO ARRANCA
    (falla real de transporte, PD-5) sigue siendo `transport-error`."""

    def test_r1_hanging_invocation_ends_timeout_without_rc_claim(self) -> None:
        """R1 (PD-5/PD-1/INV-4): el binario falso duerme MÁS que
        `wait.timeout_seconds` y NUNCA escribe fila; el adaptador mata la
        invocación al vencer la cota. El hecho material observable es la
        AUSENCIA de señal dentro de la espera acotada → terminación
        `timeout`; el diagnóstico no afirma un rc (el cliente no
        retornó); sin recibo; la espera es acotada (no queda desacotada)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("r1-hangs", variant="hangs")

        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "R1 invocación que cuelga")

        # Precondición del fixture: el binario FUE invocado (registró su
        # invocación ANTES de dormir; el paquete viajó en ese transporte)
        # y este cliente nunca retornó un rc (fue matado en la cota).
        call = self.packet_call(fake, "R1 invocación que cuelga")
        self.assertIsNone(
            call.get("rc"),
            msg="fixture: la invocación colgada registró un rc (no "
                "cuelga; precondición rota de R1)")
        # Hecho material: el store del fixture queda SIN filas (sin
        # señal durable possible dentro de la cota).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            rows, [],
            msg="fixture: la variante escribió fila (hecho material "
                "corrupto; R1 exige invocación sin fila): "
                f"{[dict(r) for r in rows]!r}")

        # Terminación desde el hecho material: timeout — NO
        # transport-error (RED hoy: el vigente clasifica TimeoutExpired
        # como transport-error con diagnóstico que afirma un rc).
        self.assertNotEqual(
            out["termination"], "transport-error",
            msg=f"invocación del destino sin retorno dentro de la cota: "
                f"terminación transport-error (R1: el hecho material es "
                f"ausencia-de-señal-en-la-cota = timeout; 'transport-"
                f"error' asevera una terminación de transporte con un rc "
                f"inexistente que NUNCA se verificó): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        self.assertEqual(
            out["termination"], "timeout",
            msg=f"invocación sin retorno dentro de la cota: la "
                f"terminación no es la clase del hecho material 'timeout' "
                f"(PD-5: sin fila correlacionada o sin idle dentro de la "
                f"espera acotada → timeout; PD-1: rc=0 temprano tampoco: "
                f"el hecho es tiempo vencido sin señal): "
                f"{out['termination']!r}")

        # Diagnóstico accionable que NO afirma un rc (hecho honesto).
        diagnosis = assert_diag_actionable(self, out, "R1 cuelga")
        self.assertIsNone(
            RC_CLAIM_RE.search(diagnosis),
            msg=f"el diagnóstico AFIRMA un rc («rc=<n>») en un caso donde "
                f"el cliente NO retornó (R1: hecho material falso): "
                f"{diagnosis!r}")

        # Sin recibo fabricado (sin entrega durable) y espera ACOTADA
        # (INV-4: la corrida entera es de segundos, no desacotada).
        self.assert_no_receipt_fabricated("R1 cuelga")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"la terminación timeout declaró entrega (PD-5: sólo "
                f"completed persiste entrega): {out.get('delivery_ref')!r}")
        self.assertLess(
            elapsed, BOUNDED_WAIT_UPPER_SECONDS,
            msg=f"la espera quedó DESACOTADA ({elapsed:.2f}s >= margen; "
                f"INV-4: la espera es acotada por wait.timeout_seconds)")

    def test_r1_unstartable_binary_stays_transport_error(self) -> None:
        """R1 (contracara, PD-5): un binario que NO ARRANCA (la ruta de
        `binary` no existe) es una FALLA REAL de transporte observada
        antes de cualquier fila → terminación `transport-error` con
        diagnóstico accionable; sin recibo; sin identidad de sesión (no
        hubo invocación que pudiera crearla)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("r1-no-start", variant="succeeded")
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        missing = fake["dir"] / "bin" / "opencode-falta"
        self.assertFalse(
            missing.exists(),
            msg="precondición (fixture): la ruta del binario ausente "
                "existe")
        config["binary"] = str(missing)
        fake["config"].write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "R1 binario que no arranca")
        assert_diag_actionable(self, out, "R1 binario ausente")

        self.assertEqual(
            out["termination"], "transport-error",
            msg=f"binario que no arranca: la terminación no es "
                f"transport-error (PD-5: el transporte falló ANTES de "
                f"cualquier fila — hecho observable del adaptador): "
                f"{out['termination']!r}")
        self.assert_no_receipt_fabricated("R1 binario ausente")
        self.assertFalse(
            out.get("session"),
            msg="el binario no arrancó: no se declara identidad de "
                "sesión")
        self.assertEqual(
            self.binary_calls(fake), [],
            msg="sin binario no hay registro de invocación posible "
                "(precondición del oracle)")


# ------------------------------------------------------------------- R4


class TestR4WaitConfigFailClosed(AdapterCase):
    """R4 (review, decisión del orquestador: se corrige): la espera ES
    ACOTADA por `wait.timeout_seconds` (INV-4) — una config de ejecución
    sin la clave, o con valor no positivo, NO despacha: fallo CERRADO
    ANTES del despacho (blocked con diagnóstico que NOMBRA la clave); el
    binario no se invoca, sin transporte, sin sesión, sin recibo.

    Cada configuración declara SU PROPIA unidad de test (un proyecto
    sintético fresco por método — setUp por instancia): un despacho
    precedente que llegara a completed dejaría recibo/recepción en el
    mismo proyecto y contaminaría los hechos de la observación
    siguiente."""

    def _dispatch_without_bounded_wait(self, name: str, *,
                                       mutate) -> tuple[dict, dict]:
        """Fake runtime estándar con la config mutada por `mutate` (la
        config es el nivel correcto de la espera, PD-4/INV-4); devuelve
        (fake, envelope)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime(name, variant="succeeded")
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        mutate(config)
        fake["config"].write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        proc = self.run_opencode(fake)
        return fake, self.envelope(proc, name)

    def _assert_bounded_wait_fail_closed(self, label: str, fake: dict,
                                         out: dict) -> None:
        """El fallo cerrado pre-despacho de R4: blocked con diagnóstico
        que nombra la clave; SIN invocación, SIN transporte, SIN sesión,
        SIN recibo (INV-4: sin cota positiva declarada no se despacha)."""
        self.assertNotEqual(
            out["termination"], "completed",
            msg=f"[{label}] la config SIN espera acotada despachó a "
                f"completed (R4/INV-4: fail-open — la espera quedó "
                f"desacotada; la invocación del destino no puede quedar "
                f"sin cota)")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"[{label}] la config SIN espera acotada no falló cerrado "
                f"en 'blocked' ANTES de despachar (R4/INV-4): "
                f"{out['termination']!r}")
        diagnosis = assert_diag_actionable(self, out, label)
        self.assertIn(
            "timeout_seconds", diagnosis,
            msg=f"[{label}] el diagnóstico de la config sin espera "
                f"acotada no NOMBRA la clave faltante (R4: diagnóstico "
                f"accionable): {diagnosis!r}")
        self.assertFalse(
            out.get("session"),
            msg=f"[{label}] sin despacho no se declara identidad de "
                f"sesión")
        # Hechos durables (no invocación / no transporte / no recibo).
        self.assertEqual(
            self.binary_calls(fake), [],
            msg=f"[{label}] la config SIN espera acotada INVOCÓ el "
                f"binario destino (R4/INV-4: fallo cerrado ANTES del "
                f"despacho — sin cota positiva no se despacha): "
                f"{[c.get('argv') for c in self.binary_calls(fake)]!r}")
        self.assertFalse(
            fake["sent"].is_file(),
            msg=f"[{label}] hubo transporte de bytes sin cota declarada "
                f"(R4)")
        self.assert_no_receipt_fabricated(f"R4 [{label}]")

    def test_r4_exec_config_without_wait_object_fails_closed_before_dispatch(self) -> None:
        """R4 (INV-4): la config SIN el objeto `wait` completo NO
        despacha: `blocked` con diagnóstico que nombra `timeout_seconds`;
        el binario falso NUNCA se invoca, no hay transporte, sin sesión
        ni recibo (RED hoy: el vigente despacha SIN cota — INV-4
        fail-open)."""
        fake, out = self._dispatch_without_bounded_wait(
            "r4-wait-object-absent",
            mutate=lambda config: config.pop("wait", None))
        self._assert_bounded_wait_fail_closed("sin objeto wait", fake, out)

    def test_r4_exec_config_without_timeout_seconds_fails_closed_before_dispatch(self) -> None:
        """R4 (INV-4): el objeto `wait` presente pero SIN la clave
        `timeout_seconds` NO despacha (misma barrera pre-despacho)."""
        fake, out = self._dispatch_without_bounded_wait(
            "r4-timeout-seconds-absent",
            mutate=lambda config: config.update({"wait": {}}))
        self._assert_bounded_wait_fail_closed("sin timeout_seconds", fake,
                                              out)

    def test_r4_nonpositive_wait_timeout_fails_closed_before_dispatch(self) -> None:
        """R4 (INV-4): con `wait.timeout_seconds` = 0 (valor NO positivo),
        el adaptador NO despacha: `blocked` con diagnóstico que nombra la
        clave; sin invocación, sin transporte, sin recibo (RED hoy: la
        cota 0 vence el presupuesto de la invocación misma →
        `transport-error`, no un fallo cerrado pre-despacho)."""
        fake, out = self._dispatch_without_bounded_wait(
            "r4-zero-wait",
            mutate=lambda config: config.update(
                {"wait": {"timeout_seconds": 0}}))
        self.assertNotEqual(
            out["termination"], "completed",
            msg="cota 0 despachó a completed (R4/INV-4: una espera de 0 "
                "no es acotada en el sentido del contrato)")
        self.assertNotEqual(
            out["termination"], "transport-error",
            msg=f"cota no positiva cayó en transport-error (R1/R4: el "
                f"despacho mismo no debió ocurrir — fallo cerrado "
                f"PRE-despacho): {out['termination']!r}")
        self._assert_bounded_wait_fail_closed("cota 0", fake, out)


# ------------------------------------------------------------------- R3


class TestR3IdleOutcomeEdgeVariants(AdapterCase):
    """R3 (review, decisión del orquestador: se corrige): las ramas de
    PD-5 sin cobertura previa en el doble — `succeeded` SIN texto final →
    `blocked` con diagnóstico y sin recibo (R-C de §9: el rol que usa
    herramientas queda sin texto); `idle_outcome` NO declarado →
    `unknown`, sin recibo (el vocabulario incluye `unknown`)."""

    def test_r3_succeeded_without_final_text_is_blocked_without_receipt(self) -> None:
        """R3 (PD-5): fila idle 'succeeded' + time_idle pero SIN ningún
        texto final (`assistant`) → terminación `blocked` (NUNCA
        completed sin texto), con diagnóstico accionable; sin entrega ni
        recibo; sin esperar de más (el hecho ya conocido no se degrada a
        timeout)."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("r3-succeeded-no-text",
                                 variant="succeeded-no-text")
        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "R3 succeeded sin texto")

        # Precondición del fixture: la fila está idle 'succeeded' y NO
        # hay texto final de ningún assistant (hecho material R-C).
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows], ["succeeded"],
            msg="fixture: la fila no está idle 'succeeded' (precondición "
                "R3 rota)")
        self.assertIsNone(
            durable_last_assistant_text(fake["sessions_db"], rows[0]["id"]),
            msg="fixture: el store SÍ tiene texto final de assistant "
                "(precondición R3 'sin texto' rota)")

        self.assertNotEqual(
            out["termination"], "completed",
            msg="idle 'succeeded' SIN texto final terminó completed (PD-5: "
                "succeeded→completed SÓLO con texto final presente)")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"idle 'succeeded' sin texto final: la terminación no es "
                f"'blocked' (PD-5, rama R3: si falta el texto, blocked "
                f"con diagnóstico): {out['termination']!r}")
        assert_diag_actionable(self, out, "R3 sin texto")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"succeeded sin texto declaró entrega (PD-5: la entrega "
                f"exige el texto final): {out.get('delivery_ref')!r}")
        self.assert_no_receipt_fabricated("R3 sin texto")
        self.assertLess(
            elapsed, TEST_WAIT_TIMEOUT_SECONDS,
            msg=f"la rama 'succeeded sin texto' esperó de más "
                f"({elapsed:.2f}s >= cota; PD-5: el hecho ya conocido no "
                f"se degrada a timeout)")

    def test_r3_undeclared_idle_outcome_is_unknown_without_receipt(self) -> None:
        """R3 (PD-5): fila con `idle_outcome` NO declarado por el
        vocabulario observado (succeeded|failed|interrupted|NULL,
        discovery §3.4) → terminación `unknown` (hecho material no
        interpretable), NUNCA completed, con diagnóstico accionable; sin
        entrega, sin recibo."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime("r3-unknown-outcome",
                                 variant="unknown-outcome")
        proc = self.run_opencode(fake)
        out = self.envelope(proc, "R3 idle_outcome no declarado")

        # Precondición del fixture: la fila lleva el idle_outcome foráneo.
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("idle_outcome") for row in rows], [UNKNOWN_OUTCOME],
            msg=f"fixture: la fila no declara el idle_outcome no "
                f"declarado {UNKNOWN_OUTCOME!r} (precondición R3 rota)")

        self.assertNotEqual(
            out["termination"], "completed",
            msg="idle_outcome no declarado terminó completed (PD-5: el "
                "hecho no interpretable no autoriza un gate)")
        self.assertEqual(
            out["termination"], "unknown",
            msg=f"idle_outcome no declarado: la terminación no es "
                f"'unknown' (PD-5, rama R3: el vocabulario incluye "
                f"unknown para el hecho no interpretable): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        assert_diag_actionable(self, out, "R3 outcome foráneo")
        self.assertFalse(
            out.get("delivery_ref"),
            msg=f"idle_outcome no declarado declaró entrega (PD-5): "
                f"{out.get('delivery_ref')!r}")
        self.assert_no_receipt_fabricated("R3 outcome foráneo")


# ------------------------------------------------------------------- R2


class TestR2ModelReportedFromDurableRow(AdapterCase):
    """R2 (review, decisión del orquestador: se corrige): la observación
    I8 del worker (PD-6) es OBSERVABILIDAD útil: cuando la fila durable
    trae `model` serializado como OBJETO JSON {id, providerID} (la forma
    reportada por la propia evidencia de aceptación del runtime real),
    `model_reported` se guarda como 'providerID/id' — no el objeto JSON
    verbatim; si la fila trae TEXTO PLANO, se conserva tal cual."""

    def _worker_i8_record(self, label: str, *,
                          variant: str, name: str) -> dict:
        """Despacha al binario falso y devuelve el registro I8 del intento del
        despacho. A-1 (006-005 U1b, REEMPLAZO DECLARADO): la localización pasa
        de «el registro nuevo del ledger que NO es el de la interfaz» a «el
        ÚNICO registro nuevo del despacho» — la interfaz RELAYA el `attempt`
        del módulo y no registra (D-14/PD-1), así que el registro del intento
        ES el que el sobre declara. Las aserciones sobre `model_reported`
        (desde la fila durable) no cambian."""
        self.assert_derived_agents_published()
        fake = self.fake_runtime(name, variant=variant)
        records_before = dispatch_records(self.root, self.execution_id)
        proc = self.run_opencode(fake)
        out = self.envelope(proc, label)
        self.assertEqual(
            out["termination"], "completed",
            msg=f"{label}: la corrida con fila durable no terminó "
                f"completed (precondición de la observación I8): "
                f"{out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        record_path = self.assert_single_record_per_dispatch(
            out, records_before)
        return fake, json.loads(record_path.read_text(encoding="utf-8"))

    def test_r2_json_object_model_reported_as_provider_over_id(self) -> None:
        """R2 (PD-6): la fila durable trae `model` = objeto JSON
        serializado {id, providerID} → `model_reported` del registro I8
        del worker es 'providerID/id' (normalizado), NO el objeto JSON
        verbatim; el esquema cerrado I8 se conserva y la provenance
        sigue declarando la fuente."""
        fake, record = self._worker_i8_record(
            "R2 modelo objeto JSON", variant="model-object",
            name="r2-model-object")

        # Precondición del fixture: la fila trae el OBJETO JSON.
        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("model") for row in rows], [ROW_MODEL_OBJECT],
            msg="fixture: la fila no trae el modelo serializado como "
                f"objeto JSON {ROW_MODEL_OBJECT!r} (precondición R2 rota)")

        # Esquema cerrado conservado (PD-6) y valor NORMALIZADO.
        self.assertEqual(
            set(record), I8_RECORD_KEYS,
            msg=f"la forma del registro I8 no es la cerrada aprobada "
                f"(PD-6: el esquema se conserva): {sorted(record)}")
        self.assertEqual(
            record["model_reported"], ROW_MODEL_NORMALIZED,
            msg=f"`model_reported` del I8 del worker no es la forma "
                f"normalizada 'providerID/id' de la fila (R2/PD-6): "
                f"{record['model_reported']!r} != "
                f"{ROW_MODEL_NORMALIZED!r}")
        self.assertNotEqual(
            record["model_reported"], ROW_MODEL_OBJECT,
            msg=f"`model_reported` guardó el OBJETO JSON verbatim de la "
                f"fila (R2: baja utilidad de observabilidad — el registro "
                f"'configured / observed' queda ilegible): "
                f"{record['model_reported']!r}")

        # La provenance sigue declarando la fuente (PD-6).
        provenance = record.get("provenance")
        self.assertIsInstance(
            provenance, dict, msg="provenance del registro no es un objeto")
        source = provenance.get("model_reported")
        self.assertIsInstance(
            source, str,
            msg="provenance['model_reported'] no declara la fuente (PD-6)")
        self.assertTrue(
            source.strip(), msg="provenance['model_reported'] vacío")

    def test_r2_plain_text_row_model_is_preserved(self) -> None:
        """R2 (contracara, PD-6): si la fila trae el modelo como TEXTO
        PLANO, `model_reported` se conserva tal cual (la normalización
        sólo aplica a la forma objeto; la regla no cambia el caso
        vigente)."""
        fake, record = self._worker_i8_record(
            "R2 modelo texto plano", variant="succeeded",
            name="r2-model-plain")

        rows = durable_session_rows(fake["sessions_db"])
        self.assertEqual(
            [row.get("model") for row in rows], [ROW_MODEL],
            msg="fixture: la fila no trae el modelo como texto plano "
                f"{ROW_MODEL!r} (precondición rota)")
        self.assertEqual(
            set(record), I8_RECORD_KEYS,
            msg=f"la forma del registro I8 no es la cerrada aprobada "
                f"(PD-6): {sorted(record)}")
        self.assertEqual(
            record["model_reported"], ROW_MODEL,
            msg=f"`model_reported` alteró el modelo de TEXTO PLANO de la "
                f"fila (R2: sólo la forma objeto se normaliza; PD-6): "
                f"{record['model_reported']!r} != {ROW_MODEL!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
