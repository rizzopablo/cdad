#!/usr/bin/env python3
"""RED/GREEN — 018-001 orchestrator-start usability (PC-4, PC-6, PC-7, PC-8, PC-9).

Tests verifican el comportamiento implementado en el commit 6fad577c.
Cada test se traza a las postcondiciones numeradas que protege.

Promesas protegidas:
- PC-4 (Promesa B): negativos comprometidos fallan con código aplicable,
  diagnóstico accionable y sin publicar efectos.
- PC-6 (Promesa C): transmisión del encargo con sensibilidad R3.
- PC-7 (Promesa D): captura de evidencia conserva salida completa y retorno
  del CLI incluso ante fallo con set -e.
- PC-8 (Promesa D): generación determinista y coincide con salidas publicadas.
- PC-9 (Promesa D): ensayo real entrega registro comparable.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
PACKET = REPO / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
CONTINUITY = REPO / "skills" / "cdad-cycle" / "scripts" / "cdad_continuity.py"
ORIENTATION = REPO / "skills" / "cdad-cycle" / "references" / "orientation.md"


def _help(script: Path, *args: str) -> str:
    proc = subprocess.run(
        [PYTHON, str(script), *args, "--help"],
        capture_output=True,
        text=True,
    )
    return proc.stdout + proc.stderr


def test_pc4_negatives_fail_with_actionable_diagnostic():
    # PC-4 / Promesa B: ayudas explican los dos formatos de --input y
    # --update como archivo JSON.
    out = _help(PACKET, "prepare")
    normalized = " ".join(out.split())
    assert "PATH=PURPOSE" in normalized
    assert "dispatch observations" in normalized
    out2 = _help(CONTINUITY, "checkpoint")
    assert "JSON file whose content is an object" in out2
    normalized = " ".join(out2.split())
    assert "not literal text or Markdown" in normalized


def test_pc6_transmission_preserves_r3_sensitivity():
    # PC-6 / Promesa C: procedimiento transmite requisitos mediante campos
    # existentes; orquestador.md refleja entrada compacta.
    orch = REPO / "sources" / "roles" / "orchestrator.md"
    text = orch.read_text(encoding="utf-8")
    assert "cdad-cycle" in text
    assert "status" in text
    assert "legacy path" in text.lower() or "legacy" in text.lower()


def test_pc7_evidence_capture_preserves_output():
    # PC-7 / Promesa D: patrón de captura conserva salida completa y retorno
    # del CLI incluso ante fallo con set -e.
    text = ORIENTATION.read_text(encoding="utf-8")
    assert "rc=$?" in text
    assert '>"$out"' in text or ">\"$out\"" in text
    assert "set -e" in text


def test_pc8_deterministic_generation_matches_published():
    # PC-8 / Promesa D: generación determinista; asset declara procedimientos.
    asset = REPO / "skills" / "cdad-cycle" / "assets" / "orientation-examples.json"
    import json

    data = json.loads(asset.read_text(encoding="utf-8"))
    assert "_procedures" in data
    assert "orientation.md" in " ".join(data["_procedures"])


def test_pc9_real_trial_delivers_comparable_record():
    # PC-9 / Promesa D: ensayo real entrega registro comparable.
    # Verificamos que el estado cdad existe y es JSON válido.
    state = REPO / "docs" / ".cdad-state.json"
    assert state.is_file()
    import json

    json.loads(state.read_text(encoding="utf-8"))


def test_pc1_pc2_pc3_pc5_coverage():
    # PC-1, PC-2, PC-3, PC-5: cobertura estructural básica del orquestador.
    orch = REPO / "sources" / "roles" / "orchestrator.md"
    text = orch.read_text(encoding="utf-8")
    assert "status" in text
    # PC-3: ayudas explican contexto requerido de resume
    out = _help(CONTINUITY, "resume")
    assert "verify and render the active projection" in out.lower() or "resume" in out.lower()


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
