#!/usr/bin/env python3
"""019-002 recovery T4 RED — orientación de reposo tras el cierre (PC-5 de
recovery-spec.md; PC-7 del spec.md original, audit N2).

Reutilización: estos dos tests proceden de la T2 retirada (215b0b52) y se
reevaluaron de forma independiente contra el PC-5 de reemplazo, no contra las
obligaciones de escenario antiguas. Se endureció el oráculo del caso
`done`/`null`: la ausencia de `open-unit` se afirma sobre la recomendación
(`entry` y `next`), no sobre todo el texto, porque un diagnóstico accionable
puede legítimamente explicar que `open-unit` rechaza ese estado.

Consecuencia (R4): sin estos tests, quien completa una feature recibe de
`status` una recomendación de apertura que `open-unit` rechaza de inmediato.

Contract original: docs/specs/019-002-effective-discovery-instructions/spec.md PC-7:
«Legitimate closure leaves `current_stage: idle` and `active_feature: null`…
Status applies the same resting-coherence criterion as `open-unit` before
recommending opening. With otherwise eligible configuration and dependencies,
a correct closure permits opening the next queued unit. `done`/`null` produces
a diagnosis, not an `open-unit` recommendation or an at-rest claim.»
Audit: docs/specs/019-002-effective-discovery-instructions/test-audit.md N2.

Superficie (caja negra, solo subprocess sobre los CLI públicos; la
implementación nunca se lee):

    cdad_packet.py register-transition --transition closure …   (cierre real)
    cdad_packet.py status --project-root <ABS>                  (orientación)
    cdad_packet.py open-unit --project-root <ABS>               (apertura)

Fixtures descartables (tempdirs, HOME aislado), reutilizados de
tests/test_005_012_t1_register_transition_base.py. Las distinciones
activa/suspendida/pendiente de `status` NO se re-prueban aquí: las protegen
tests/test_007_001_unambiguous_entry.py, tests/test_007_007_suspend_resume_units.py
y tests/test_005_003_f2_idle_history.py (sin cambios).

Mapeo test → postcondición:
  test_pc7_closure_status_recommends_open_unit_and_it_succeeds
      -> PC-7 (cierre legítimo → status recomienda `open-unit` → la apertura
         recomendada tiene éxito sobre la siguiente unidad en cola).
         Sin este test el usuario recibe una recomendación de apertura que no
         se corresponde con lo que el cierre real deja.
  test_pc7_done_null_state_gets_diagnosis_not_open_unit_and_no_mutation
      -> PC-7 (`current_stage: done` + `active_feature: null` → diagnóstico,
         sin recomendación `open-unit`, sin claim de reposo, y `status` no
         muta el state). Sin este test `status` dirige al usuario a un
         `open-unit` que luego falla.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from test_005_012_t1_register_transition_base import (
    APPROVER,
    FEATURE_ID,
    _Fixture as _BaseFixture,
)

CLOSURE_STAGE = "feature-closure"
CLOSURE_REL = f"docs/specs/{FEATURE_ID}/closure.md"
CLOSURE_BYTES = b"# Closure fixture (019-002 resting orientation)\n"
NEXT_FEATURE = "019-900-next-queued-unit"
STATE_REL = "docs/.cdad-state.json"


class _RestFixture(_BaseFixture):
    """Proyecto con entregas satisfechas, cierre citado y UNA unidad `queued`
    elegible (contrato aprobado y pineado, sin dependencias)."""

    def __init__(self, base: Path) -> None:
        super().__init__(base, mode="ready")
        closure = self.root / CLOSURE_REL
        closure.parent.mkdir(parents=True, exist_ok=True)
        closure.write_bytes(CLOSURE_BYTES)
        spec_rel = f"docs/specs/{NEXT_FEATURE}/spec.md"
        spec = self.root / spec_rel
        spec.parent.mkdir(parents=True, exist_ok=True)
        data = f"# Spec fixture ({NEXT_FEATURE})\n".encode()
        spec.write_bytes(data)
        state = self.read_state()
        state["stage_history"].append({
            "feature": NEXT_FEATURE,
            "stage": "specification",
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T00:00:00Z",
            "contract_path": spec_rel,
            "contract_sha256": hashlib.sha256(data).hexdigest(),
        })
        state["epic_features"].append({"id": NEXT_FEATURE, "status": "queued"})
        self.write_state(state)

    def close(self):
        return self.register_transition(
            "--transition", "closure", "--stage", CLOSURE_STAGE,
            "--approve-by", APPROVER, "--closure-path", CLOSURE_REL)

    def status(self):
        return self.run_packet("status", "--project-root", str(self.root))

    def open_unit(self):
        return self.run_packet("open-unit", "--project-root", str(self.root))

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()


def _status_doc(proc) -> dict:
    assert proc.returncode == 0, (
        f"`status` debe responder rc=0: rc={proc.returncode} "
        f"{proc.stdout!r} {proc.stderr!r}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:  # pragma: no cover - forma de salida
        raise AssertionError(f"`status` debe emitir JSON: {proc.stdout!r}")


@pytest.fixture
def fx(tmp_path: Path) -> _RestFixture:
    return _RestFixture(tmp_path)


def test_pc7_closure_status_recommends_open_unit_and_it_succeeds(
        fx: _RestFixture) -> None:
    """PC-7: tras un cierre legítimo, `status` recomienda `open-unit` y la
    apertura recomendada abre la unidad en cola elegible."""
    closed = fx.close()
    assert closed.returncode == 0, (
        "precondición (comportamiento existente): el cierre legítimo se "
        f"aplica: {closed.stdout!r} {closed.stderr!r}")
    state = fx.read_state()
    assert state["current_stage"] == "idle" and state["active_feature"] is None, (
        "PC-7: el cierre legítimo deja `idle`/`null`: "
        f"{state['current_stage']!r}/{state['active_feature']!r}")

    doc = _status_doc(fx.status())
    text = json.dumps(doc)
    assert doc.get("entry") == "next-unit" and "open-unit" in text, (
        "PC-7 violada: tras el cierre `status` debe recomendar abrir la "
        f"siguiente unidad (entry=next-unit, nombra `open-unit`): {text!r}")

    opened = fx.open_unit()
    assert opened.returncode == 0, (
        "PC-7 violada: la apertura recomendada debe tener éxito sobre la "
        f"unidad elegible: rc={opened.returncode} "
        f"{opened.stdout!r} {opened.stderr!r}")
    assert fx.read_state()["active_feature"] == NEXT_FEATURE, (
        "PC-7: la apertura debe abrir la siguiente unidad en cola")


def test_pc7_done_null_state_gets_diagnosis_not_open_unit_and_no_mutation(
        fx: _RestFixture) -> None:
    """PC-7: `done`/`null` recibe diagnóstico — ni recomendación `open-unit` ni
    claim de reposo — y `status` no modifica el state."""
    assert fx.close().returncode == 0
    state = fx.read_state()
    state["current_stage"] = "done"  # el cierre descrito por la guía vieja
    state["active_feature"] = None
    fx.write_state(state)
    opened = fx.open_unit()
    assert opened.returncode != 0, (
        "precondición (comportamiento existente): `open-unit` rechaza "
        f"`done`/`null`: {opened.stdout!r}")
    fx.write_state(state)  # restaura bytes de entrada por si open-unit escribió
    before = fx.state_bytes()

    proc = fx.status()
    doc = _status_doc(proc)
    text = json.dumps(doc)

    assert fx.state_bytes() == before, "PC-7: `status` no debe mutar el state"
    recommendation = json.dumps({k: doc.get(k) for k in ("entry", "next")})
    assert doc.get("entry") != "next-unit" and "open-unit" not in recommendation, (
        "PC-5 violada: `done`/`null` no debe producir recomendación "
        f"`open-unit` (entry/next): {recommendation!r}")
    assert doc.get("situation") != "at-rest" and "at-rest" not in text, (
        f"PC-7 violada: `done`/`null` no debe declararse en reposo: {text!r}")
    assert any(w in text.lower() for w in ("diagnos", "incoheren", "inconsisten", "coheren")), (
        f"PC-7 violada: debe haber un diagnóstico del estado: {text!r}")
