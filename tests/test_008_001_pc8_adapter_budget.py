#!/usr/bin/env python3
"""008-001 PC-8 RED — el adaptador OpenCode no despacha sin presupuesto útil
(AJ5; PC-8a, PC-8b).

Contract: docs/specs/008-001-home-xdg-isolation/spec.md §AJ5 / PC-8.

Determinista: binario OpenCode FALSO (fixture compartida AdapterCase) y
servidor `/api/info` en loopback con retardo CONTROLADO (DelayedInfoServer);
`mode: server`, config temporal. Sin depender de la carga del host.

Mapa test → postcondición:
  1  test_pc8a_preparation_exhausts_budget_no_run
       PC-8a — `/api/info` tarda más que la cota total: no hay `run`, no hay
       sesión ni recibo, y el diagnóstico nombra el agotamiento preparatorio
       (no `bounded wait (0.0 seconds)`).
  2  test_pc8b_fast_preparation_dispatches_and_completes
       PC-8b — preparación rápida + fila durable `idle`: hay `run` y la
       delegación completa con sesión y entrega, dentro de la cota.
  4  test_pc8_edge_preparation_never_launches_with_zero_wait
       PC-8a/PC-8b (borde) — /api/info responde pero consume la reserva:
       o agotamiento preparatorio sin `run`, o despacho con espera positiva;
       nunca cliente lanzado con 0.0s.
  5  TestPc8ServiceMode::test_pc8_service_status_slow_cuts_preparation
       PC-8a en `mode: service` — `service status` lento: sin `run`, sin
       sesión/recibo/excepción, agotamiento preparatorio.
  6  TestPc8ServiceMode::test_pc8_service_status_fast_dispatches
       PC-8b en `mode: service` — `service status` rápido: despacha.
  3  test_pc8b_fast_preparation_hanging_client_times_out_with_session
       PC-8b (variante) — preparación rápida + cliente colgado: `timeout`
       con sesión; la espera del cliente fue positiva (no 0.0s).

RED esperado (adaptador vigente, medido):
  (4) con /api/info a 0.6s el preflight pasa y el adaptador lanza el cliente
      con `bounded wait (0.0 seconds)`: termination `timeout` con sesión →
      AssertionError (espera 0.0s).
  (1) con /api/info > cota el adaptador ya no lanza `run`, pero diagnostica
      "server not reachable" en vez de agotamiento preparatorio →
      AssertionError sobre el diagnóstico.
  (2)/(3) pasan hoy (comportamiento existente que no debe regresar).
"""

from __future__ import annotations

import json
import re
import time
import unittest

from test_005_009_t2_opencode_adapter import FAKE_BINARY_VERSION, AdapterCase
from test_006_001_reviewfix import DelayedInfoServer
from test_006_001_t1_selection import FAST_WAIT, MATCHING_CLIENT_SEMVER
from test_006_001_t1b_service_mode import (
    T1B_WRAPPER_BINARY_SOURCE, T1bServiceCase)

_SEMVER = FAKE_BINARY_VERSION.rsplit(" ", 1)[-1]
BUDGET_SECONDS = 2          # cota total del adaptador
SLOW_PREFLIGHT_SECONDS = 3
FAST_PREFLIGHT_SECONDS = 0  # preparación admisible (PC-8b)
# Preflight que RESPONDE pero consume la reserva: hoy el adaptador lanza el
# cliente con espera 0.0s (medido: ventana ~0.45-0.75s con cota 2s).
EDGE_PREFLIGHT_SECONDS = 0.6
ZERO_WAIT_MARKERS = ("0.0 second", "(0.0", "0.0s")
# Mínimo útil del cliente (review PC-8): proporcional a la cota total.
REQUIRED_MIN_WAIT = max(0.1, 0.2 * BUDGET_SECONDS)
# Marcadores DISTINTIVOS del agotamiento preparatorio (inglés o español),
# ambos componentes obligatorios: la causa y la ausencia de despacho.
EXHAUSTION_MARKERS = ("preparatory exhaustion", "agotamiento preparatorio")
NOT_DISPATCHED_MARKERS = ("not dispatched", "not launched", "no despachado",
                          "no se lanz", "sin despacho")
MIN_NAMING_MARKERS = ("required", "requerido", "minimum", "mínimo",
                      "remaining", "remanente")
_BOUNDED_WAIT = re.compile(r"bounded wait \(([0-9]+(?:\.[0-9]+)?) second")
SLOW_SERVICE_STATUS_SECONDS = 3
SERVICE_FAST_BUDGET_SECONDS = 10
# Preparación admisible (PC-8b): cota holgada; medido, la preparación
# rápida cuesta ~0.65-0.80s, el presupuesto interno de una cota de 2s.
FAST_BUDGET_SECONDS = 10
# Envoltorio T1b con `service status` RETARDADO por el escenario (`delay`).
DELAYED_SERVICE_WRAPPER = T1B_WRAPPER_BINARY_SOURCE.replace(
    '    scenario = json.loads(_SCENARIO.read_text(encoding="utf-8"))\n',
    '    scenario = json.loads(_SCENARIO.read_text(encoding="utf-8"))\n'
    '    import time\n'
    '    time.sleep(float(scenario.get("delay", 0)))\n')
assert DELAYED_SERVICE_WRAPPER != T1B_WRAPPER_BINARY_SOURCE


class Pc8Oracles:
    """Oráculos estrictos compartidos (review PC-8)."""

    def assert_wait_not_below_minimum(self, text: str, label: str, *,
                                      required: float = REQUIRED_MIN_WAIT) -> None:
        for match in _BOUNDED_WAIT.finditer(text):
            self.assertGreaterEqual(
                float(match.group(1)), required,
                msg=f"{label}: el cliente recibió una espera menor al mínimo "
                    f"útil {required}s (timeout falso, PC-8): "
                    f"{text!r}")

    def assert_preparatory_exhaustion(self, diagnosis: str, label: str) -> None:
        low = diagnosis.lower()
        self.assertTrue(
            any(m in low for m in EXHAUSTION_MARKERS),
            msg=f"{label}: el diagnóstico no declara {EXHAUSTION_MARKERS}: "
                f"{diagnosis!r}")
        self.assertTrue(
            any(m in low for m in NOT_DISPATCHED_MARKERS),
            msg=f"{label}: el diagnóstico no declara la ausencia de despacho "
                f"{NOT_DISPATCHED_MARKERS}: {diagnosis!r}")
        self.assertTrue(
            any(m in low for m in MIN_NAMING_MARKERS),
            msg=f"{label}: el diagnóstico no nombra el mínimo/remanente: "
                f"{diagnosis!r}")


class Pc8BudgetCase(Pc8Oracles, AdapterCase):

    def _server_fake(self, name: str, variant: str, delay: float,
                     budget: float = BUDGET_SECONDS) -> tuple[dict, DelayedInfoServer]:
        server = DelayedInfoServer(
            body=json.dumps({"version": _SEMVER}).encode(), delay=delay)
        self.addCleanup(server.stop)
        fake = self.fake_runtime(name, variant=variant)
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        config.update({
            "mode": "server", "server": server.url,
            "wait": {"poll_initial_seconds": 0.05, "poll_max_seconds": 0.2,
                     "settle_seconds": 0.3, "terminate_grace_seconds": 0.2,
                     "preflight_timeout_seconds": 5,
                     "timeout_seconds": budget}})
        fake["config"].write_text(json.dumps(config, indent=2) + "\n",
                                  encoding="utf-8")
        return fake, server

    def _run_calls(self, fake: dict) -> list[dict]:
        return [c for c in self.binary_calls(fake)
                if isinstance(c.get("packet"), dict)]

    def assert_not_zero_wait(self, text: str, label: str) -> None:
        for marker in ZERO_WAIT_MARKERS:
            self.assertNotIn(
                marker, text,
                msg=f"{label}: el diagnóstico reporta una espera de 0.0s "
                    f"(timeout falso, PC-8): {text!r}")

    def test_pc8a_preparation_exhausts_budget_no_run(self) -> None:
        """PC-8a: preparación que cruza la cota → sin `run`, sin sesión ni
        recibo, diagnóstico de agotamiento preparatorio."""
        self.assert_derived_agents_published()
        fake, server = self._server_fake(
            "pc8a", "succeeded", SLOW_PREFLIGHT_SECONDS)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PC-8a")

        self.assertTrue(server.requests,
                        msg="precondición: el preflight no consultó /api/info")
        self.assertEqual(
            self._run_calls(fake), [],
            msg=f"PC-8a: la preparación agotó la cota y el adaptador IGUAL "
                f"ejecutó el cliente (`run`): "
                f"{[c.get('argv') for c in self._run_calls(fake)]!r}; "
                f"envelope {out!r}")
        self.assertNotEqual(out["termination"], "completed",
                            msg=f"PC-8a: declaró completed: {out!r}")
        self.assertFalse(out.get("session"),
                         msg=f"PC-8a: fabricó sesión {out!r}")
        self.assertFalse(out.get("delivery_ref"),
                         msg=f"PC-8a: declaró entrega {out!r}")
        self.assert_no_receipt_fabricated("PC-8a")
        diagnosis = out.get("diagnosis") or ""
        self.assert_wait_not_below_minimum(diagnosis, "PC-8a")
        self.assert_preparatory_exhaustion(diagnosis, "PC-8a")

    def test_pc8b_fast_preparation_dispatches_and_completes(self) -> None:
        """PC-8b: preparación rápida + fila `idle` → `run` y completed con
        sesión y entrega, dentro de la cota."""
        self.assert_derived_agents_published()
        fake, _server = self._server_fake(
            "pc8b", "succeeded", FAST_PREFLIGHT_SECONDS,
            budget=FAST_BUDGET_SECONDS)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PC-8b")

        self.assertEqual(len(self._run_calls(fake)), 1,
                         msg=f"PC-8b: no hubo exactamente un `run`: {out!r}")
        self.assertEqual(out["termination"], "completed",
                         msg=f"PC-8b: no completó: {out!r}")
        self.assertTrue(out.get("session"), msg=f"PC-8b: sin sesión {out!r}")
        self.assert_durable_delivery_ref(out)
        self.assert_receipt_no_gate()

    def test_pc8b_fast_preparation_hanging_client_times_out_with_session(self) -> None:
        """PC-8b (variante): preparación rápida + cliente colgado →
        `timeout` con sesión, espera positiva (no 0.0s), sin recibo."""
        self.assert_derived_agents_published()
        fake, _server = self._server_fake(
            "pc8b-hangs", "hangs", FAST_PREFLIGHT_SECONDS,
            budget=FAST_BUDGET_SECONDS)

        started = time.monotonic()
        proc = self.run_opencode(fake)
        elapsed = time.monotonic() - started
        out = self.envelope(proc, "PC-8b hangs")

        self.assertEqual(len(self._run_calls(fake)), 1,
                         msg=f"PC-8b hangs: no hubo `run`: {out!r}")
        self.assertEqual(out["termination"], "timeout",
                         msg=f"PC-8b hangs: no es timeout: {out!r}")
        self.assertTrue(out.get("session"),
                        msg=f"PC-8b hangs: timeout sin sesión: {out!r}")
        self.assert_wait_not_below_minimum(
            out.get("diagnosis") or "", "PC-8b hangs",
            required=max(0.1, 0.2 * FAST_BUDGET_SECONDS))
        self.assert_no_receipt_fabricated("PC-8b hangs")
        self.assertLess(elapsed, 60,
                        msg=f"PC-8b hangs: espera no acotada ({elapsed:.1f}s)")

    def test_pc8_edge_preparation_never_launches_with_zero_wait(self) -> None:
        """PC-8a/PC-8b (borde): /api/info responde pero consume la reserva.
        Sólo dos salidas: (a) no despacho — sin `run`, `session=None`, sin
        recibo, diagnóstico de agotamiento preparatorio que nombra el
        mínimo; (b) despacho con `run` y espera >= mínimo requerido."""
        self.assert_derived_agents_published()
        fake, server = self._server_fake(
            "pc8-edge", "succeeded", EDGE_PREFLIGHT_SECONDS)

        proc = self.run_opencode(fake)
        out = self.envelope(proc, "PC-8 borde")
        diagnosis = out.get("diagnosis") or ""

        self.assertTrue(server.requests,
                        msg="precondición: el preflight no consultó /api/info")
        self.assert_wait_not_below_minimum(diagnosis, "PC-8 borde")
        runs = self._run_calls(fake)
        if runs:  # (b) despacho
            self.assertEqual(len(runs), 1,
                             msg=f"PC-8 borde: más de un `run`: {out!r}")
            self.assertTrue(out.get("session"),
                            msg=f"PC-8 borde: `run` sin sesión: {out!r}")
            self.assertEqual(out["termination"], "completed",
                             msg=f"PC-8 borde: despachó sin completar "
                                 f"(espera insuficiente): {out!r}")
        else:  # (a) no despacho
            self.assertIsNone(out.get("session"),
                              msg=f"PC-8 borde: sesión sin `run`: {out!r}")
            self.assertFalse(out.get("delivery_ref"),
                             msg=f"PC-8 borde: entrega sin `run`: {out!r}")
            self.assert_no_receipt_fabricated("PC-8 borde")
            self.assert_preparatory_exhaustion(diagnosis, "PC-8 borde")


class TestPc8ServiceMode(Pc8Oracles, T1bServiceCase):
    """PC-8 en `mode: service`: `service status` es parte de la preparación
    y queda bajo el mismo deadline agregado."""

    def _service_fake(self, name: str, delay: float,
                      budget: float = BUDGET_SECONDS) -> dict:
        fake = self.fake_runtime_service(name)
        fake["binary"].write_text(DELAYED_SERVICE_WRAPPER, encoding="utf-8")
        fake["scenario"].write_text(json.dumps(
            {"stdout": fake["service_url"] + "\n", "rc": 0,
             "delay": delay}) + "\n", encoding="utf-8")
        self.write_service_registry(fake, version=MATCHING_CLIENT_SEMVER)
        self.assert_derived_agents_published()
        self.patch_config(fake, {"mode": "service", "wait": {
            **FAST_WAIT, "timeout_seconds": budget}})
        return fake

    def _runs(self, fake: dict) -> list[dict]:
        return [c for c in self.wrapper_calls(fake)
                if c["argv"][:1] == ["run"]]

    def test_pc8_service_status_slow_cuts_preparation(self) -> None:
        """`service status` más lento que la cota → sin `run`,
        `session=None`, sin recibo, sin excepción; diagnóstico de
        agotamiento preparatorio."""
        fake = self._service_fake("pc8-svc-slow", SLOW_SERVICE_STATUS_SECONDS)

        started = time.monotonic()
        proc = self.dispatch_service(fake)
        elapsed = time.monotonic() - started
        for marker in ("Traceback", "KeyError"):
            self.assertNotIn(marker, proc.stderr + proc.stdout,
                             msg=f"PC-8 service lento: excepción: "
                                 f"{proc.stderr[-2000:]!r}")
        out = self.envelope(proc, "PC-8 service lento")

        self.assertTrue(self.service_status_calls(fake),
                        msg="precondición: no se invocó `service status`")
        self.assertEqual(self._runs(fake), [],
                         msg=f"PC-8 service lento: hubo `run`: {out!r}")
        self.assertIsNone(out.get("session"),
                          msg=f"PC-8 service lento: sesión: {out!r}")
        self.assertFalse(out.get("delivery_ref"),
                         msg=f"PC-8 service lento: entrega: {out!r}")
        self.assert_no_receipt_fabricated("PC-8 service lento")
        self.assert_preparatory_exhaustion(out.get("diagnosis") or "",
                                           "PC-8 service lento")
        self.assertLess(elapsed, BUDGET_SECONDS + SLOW_SERVICE_STATUS_SECONDS + 5,
                        msg=f"PC-8 service lento: sin corte ({elapsed:.1f}s)")

    def test_pc8_service_status_fast_dispatches(self) -> None:
        """`service status` rápido → despacha y completa. Cota holgada
        (medido: `service status` + `--version` + escritura previa cuestan
        ~0.66s, por encima del presupuesto interno de una cota de 2s)."""
        fake = self._service_fake("pc8-svc-fast", 0,
                                  budget=SERVICE_FAST_BUDGET_SECONDS)

        proc = self.dispatch_service(fake)
        out = self.envelope(proc, "PC-8 service rápido")

        self.assertEqual(len(self._runs(fake)), 1,
                         msg=f"PC-8 service rápido: sin `run`: {out!r}")
        self.assertEqual(out["termination"], "completed",
                         msg=f"PC-8 service rápido: no completó: {out!r}")
        self.assertTrue(out.get("session"),
                        msg=f"PC-8 service rápido: sin sesión: {out!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
