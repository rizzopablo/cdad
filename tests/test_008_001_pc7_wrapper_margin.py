"""008-001 AJ4 / PC-7 — el wrapper no preempta la cota del adaptador.

Contrato: docs/specs/008-001-home-xdg-isolation/spec.md (AJ4/PC-7). La cota
`wait.timeout_seconds` es del adaptador; el wrapper `cdad_delegate.py` espera
un margen declarado más (`cota + margen`). Determinista: adaptador falso que
duerme tiempos fijos, sin depender de carga.

1. El adaptador emite un sobre `timeout` válido a `cota + ε` → el wrapper
   devuelve ESE sobre (sesión conservada), no `did not answer within`.
2. El adaptador no responde dentro de `cota + margen` → timeout genérico del
   wrapper con `session=null`; el diagnóstico nombra el límite efectivo.
3. Control: el adaptador responde antes de la cota → sobre intacto.
"""

from __future__ import annotations

import json
import re
import time
import unittest
from pathlib import Path

from test_005_009_t1_interface import DelegateCase

COTA = 1
EPSILON = 0.5
SESSION = "ses-pc7-fixture-0001"

SLOW_ADAPTER_SOURCE = '''#!/usr/bin/env python3
"""FIXTURE de tests/test_008_001_pc7_wrapper_margin.py — NO es producto.
Duerme SLEEP segundos y emite un sobre JSON fijo por stdout."""
import json
import sys
import time

time.sleep(%(sleep)r)
sys.stdout.write(json.dumps(%(envelope)r) + "\\n")
sys.stdout.flush()
sys.exit(0)
'''


def adapter_source(sleep: float, envelope: dict) -> str:
    return SLOW_ADAPTER_SOURCE % {"sleep": sleep, "envelope": envelope}


TIMEOUT_ENVELOPE = {
    "attempt": None,
    "session": SESSION,
    "termination": "timeout",
    "delivery": "none",
    "delivery_ref": None,
    "diagnosis": "pc7-fixture: el adaptador agotó su cota",
}

COMPLETED_ENVELOPE = {
    "attempt": None,
    "session": SESSION,
    "termination": "blocked",
    "delivery": "none",
    "delivery_ref": None,
    "diagnosis": "pc7-fixture: respuesta antes de la cota",
}


class TestPc7WrapperWaitsAdapterEnvelope(DelegateCase):

    def stage_slow(self, name: str, sleep: float, envelope: dict) -> Path:
        staged, _ = self.staged_interface()
        (staged.parent / f"cdad_delegate_{name}.py").write_text(
            adapter_source(sleep, envelope), encoding="utf-8")
        return staged

    def config_with_cota(self, name: str) -> Path:
        path = self.exec_config(name, runtime="pc7rt", model="pc7-model")
        doc = json.loads(path.read_text(encoding="utf-8"))
        doc["wait"] = {"timeout_seconds": COTA}
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def output(self, proc) -> dict:
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(f"stdout no es JSON: {proc.stdout[:400]!r} "
                      f"stderr={proc.stderr[-400:]!r}")
        self.assertIsInstance(out, dict)
        return out

    def test_pc7_envelope_after_cota_within_margin_is_relayed(self) -> None:
        staged = self.stage_slow("pc7late", COTA + EPSILON, TIMEOUT_ENVELOPE)
        proc = self.run_delegate(
            staged, config=self.config_with_cota("pc7late"),
            destination="pc7late")
        out = self.output(proc)
        self.assertNotIn(
            "did not answer within", str(out.get("diagnosis")),
            msg="PC-7: el wrapper mató al adaptador a la cota y no esperó "
                f"cota + margen: {out}")
        self.assertEqual(out.get("termination"), "timeout", msg=str(out))
        self.assertEqual(
            out.get("session"), SESSION,
            msg=f"PC-7: la sesión del sobre del adaptador no se conservó: {out}")
        self.assertIsNone(out.get("delivery_ref"), msg=str(out))

    def test_pc7_adapter_silent_beyond_margin_gets_wrapper_timeout(
            self) -> None:
        staged = self.stage_slow("pc7mute", 60, COMPLETED_ENVELOPE)
        started = time.monotonic()
        proc = self.run_delegate(
            staged, config=self.config_with_cota("pc7mute"),
            destination="pc7mute")
        elapsed = time.monotonic() - started
        out = self.output(proc)
        self.assertEqual(out.get("termination"), "timeout", msg=str(out))
        self.assertIsNone(out.get("session"), msg=str(out))
        self.assertLess(elapsed, 50, msg="el wrapper no cortó al adaptador")
        diagnosis = str(out.get("diagnosis"))
        numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", diagnosis)]
        self.assertTrue(
            any(n > COTA for n in numbers),
            msg="PC-7: el diagnóstico del wrapper debe nombrar el límite "
                f"efectivo (cota + margen > {COTA}s): {diagnosis!r}")
        self.assertGreater(
            elapsed, COTA + EPSILON,
            msg="PC-7: el wrapper cortó a la cota, no a cota + margen "
                f"({elapsed:.2f}s)")

    def test_pc7_control_answer_before_cota_is_intact(self) -> None:
        staged = self.stage_slow("pc7fast", 0, COMPLETED_ENVELOPE)
        proc = self.run_delegate(
            staged, config=self.config_with_cota("pc7fast"),
            destination="pc7fast")
        out = self.output(proc)
        for key in ("session", "termination", "delivery_ref"):
            self.assertEqual(out.get(key), COMPLETED_ENVELOPE[key],
                             msg=f"control: sobre alterado en {key}: {out}")


if __name__ == "__main__":
    unittest.main()
