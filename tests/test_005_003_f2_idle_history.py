#!/usr/bin/env python3
"""005-003 F2 RED — reposo con historia: `next-unit`, no `resume` de la
ejecución cerrada (PD-2 «Reposo con historia», enmienda F2).

Contract:
- docs/specs/005-003-orientation-reduction/spec.md §2.2 «Reposo e historia
  (enmienda F2)» y §3 PD-2 «Reposo con historia (F2)»: una ejecución es activa
  SOLO si `active_feature` no es nulo y `execution.feature_id` coincide con él;
  el bloque `execution` que queda tras cerrar una feature es historia; con
  `active_feature` nulo y `active_packet` ausente los directorios de
  `.cdad/packets/` son historia y la vista emite `next-unit`; un directorio
  cuenta como trabajo pendiente SOLO si su `REQUEST.json` pertenece a la
  ejecución activa y NO tiene recibo en
  `.cdad/runtime/results/<execution_id>/<packet_id>/`.
- docs/specs/005-003-orientation-reduction/review-claude-spec-2026-10-12.md
  § «F2 compromete el uso previsto»: el defecto reproducido — reposo con
  historia → `entry: continuity-reconcile` apuntando a la ejecución cerrada.

Superficie observable bajo prueba (caja negra, mismo modo de invocación que
tests/test_005_003_t1_compact_view.py: subproceso sobre el subcomando `status`
del CLI; el módulo NUNCA se importa y la implementación NUNCA se lee):

    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>

El subcomando `status` ya existe (T1 GREEN); el defecto F2 es del CONTENIDO de
la proyección: en reposo con historia emite `continuity-reconcile` y una ruta
de `resume` hacia la ejecución cerrada. Cada test falla (o pasa) en la
ASERCIÓN sobre la salida observable del contrato, nunca en la invocación: los
fallos RED son AssertionError de contrato, jamás ImportError, SyntaxError ni
error de setup. Fixtures sintéticos autocontenidos (tempdirs armados por el
test; sin datos de demo, sin rutas de este host) y el HOME del subproceso
SIEMPRE es un tempdir vacío (nunca el HOME real).

Mapeo test → postcondición/borde (PD-2 F2):
  test_pd2_f2_idle_with_history_next_unit_and_next_not_closed_execution
      -> PD-2 F2 (reposo con historia: `active_feature` nulo, `active_packet`
         ausente, bloque `execution` de una feature cerrada y directorios de
         paquete históricos con y sin recibo → `entry=next-unit`; el `next`
         NO apunta a la ejecución cerrada). Este es el caso RED focal.
  test_pd2_f2_pending_dir_of_active_execution_without_receipt_reconciles
      -> PD-2 F2 (regresión: ejecución ACTIVA — `execution.feature_id`
         coincidente con `active_feature` — con `active_packet` ausente y un
         directorio de paquete de ESA ejecución sin recibo → el trabajo
         pendiente se atiende: `entry=continuity-reconcile`).
  test_pd2_f2_receipted_dir_of_active_execution_not_pending
      -> PD-2 F2 (regresión: el MISMO directorio con recibo en
         `.cdad/runtime/results/<execution_id>/<packet_id>/` NO cuenta como
         pendiente: la proyección es indistinguible de la del mismo proyecto
         sin directorios de paquete).

El caso (4) del encargo — los casos de PD-2 existentes siguen como están —
no añade un test nuevo: lo cubre la corrida de
tests/test_005_003_t1_compact_view.py EN LA MISMA invocación de validación
(comando del encargo), sin modificar ese archivo.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    AUTHORITY_REF,
    EPIC_ID,
    FEATURE_ID,
    build_project,
    policy_hash,
    read_state,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.1: `python3 <skill-dir>/scripts/cdad_packet.py status`.
CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
CLI_TIMEOUT_S = 60

# Ejecución CERRADA (historia): el bloque `execution` que quedó en el state
# después de cerrar la feature.
CLOSED_EXECUTION_ID = "exec-004-002-project-execution-bootstrap-001"
PACKET_STUCK_ID = "004-002-project-execution-bootstrap-implementer-green-900"
PACKET_RECEIVED_ID = "004-002-project-execution-bootstrap-red-901"


# ---------------------------------------------------------------- helpers


def _packet_dir(root: Path, packet_id: str, *, execution_id: str,
                feature_id: str, receipt: bool) -> None:
    """Directorio de paquete sintético `.cdad/packets/<id>/` (forma real
    observada del artefacto publicado por `prepare`) + recibo opcional en
    `.cdad/runtime/results/<execution_id>/<packet_id>/receipt.json`."""
    d = root / ".cdad" / "packets" / packet_id
    d.mkdir(parents=True, exist_ok=True)
    request = {
        "schema_version": 1,
        "packet_id": packet_id,
        "execution_id": execution_id,
        "feature_id": feature_id,
        "role": "test-writer",
        "substage": "red",
        "objective": "F2 fixture packet",
    }
    (d / "REQUEST.json").write_text(json.dumps(request), encoding="utf-8")
    (d / "PACKET.md").write_text(
        f"---cdad-packet-json\n{{}}\n---end-cdad-packet-json\n{packet_id}\n",
        encoding="utf-8",
    )
    if receipt:
        results = (root / ".cdad" / "runtime" / "results" / execution_id
                   / packet_id)
        results.mkdir(parents=True, exist_ok=True)
        (results / "receipt.json").write_text(
            json.dumps({"runtime": "opencode", "rc": 0}), encoding="utf-8"
        )


def _build_root(base: Path) -> Path:
    root = base / "proj"
    build_project(root)
    return root


def _state_closed_feature(root: Path) -> None:
    """Reposo con historia (F2): `active_feature` nulo, `current_stage=idle`,
    `active_packet` ausente, feature cerrada en `epic_features`, y el bloque
    `execution` VIEJO de la feature cerrada (historia, no ejecución activa)."""
    state = read_state(root)
    state["epic_features"] = [{"id": FEATURE_ID, "status": "done"}]
    state["active_feature"] = None
    state["current_stage"] = "idle"
    state["tdd_substage"] = None
    state["active_packet"] = None
    state["execution"] = {
        "id": CLOSED_EXECUTION_ID,
        "epic_id": EPIC_ID,
        "feature_id": FEATURE_ID,
        "scope": EPIC_ID,
        "authority_ref": AUTHORITY_REF,
        "model_policy": "ordinary",
        "policy_sha256": policy_hash(root),
    }
    write_state(root, state)


def _state_active_execution(root: Path) -> None:
    """Ejecución ACTIVA (regresión F2): `execution.feature_id` coincidente con
    `active_feature`, `active_packet` ausente."""
    state = read_state(root)
    state["active_feature"] = FEATURE_ID
    state["current_stage"] = "tdd"
    state["tdd_substage"] = "red"
    state["active_packet"] = None
    state["execution"] = {
        "id": CLOSED_EXECUTION_ID,
        "epic_id": EPIC_ID,
        "feature_id": FEATURE_ID,
        "scope": EPIC_ID,
        "authority_ref": AUTHORITY_REF,
        "model_policy": "ordinary",
        "policy_sha256": policy_hash(root),
    }
    write_state(root, state)


def _status(root: Path, home: Path) -> subprocess.CompletedProcess:
    assert CLI.is_file(), f"CLI del repo ausente: {CLI}"
    env = dict(os.environ)
    env["HOME"] = str(home)  # NUNCA el HOME real
    return subprocess.run(
        [sys.executable, str(CLI), "status", "--project-root", str(root)],
        capture_output=True, text=True, env=env,
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
    )


def _status_document(proc: subprocess.CompletedProcess) -> dict:
    """El único documento JSON de la vista, o AssertionError de contrato
    (nunca JSONDecodeError): si la vista no emitió el documento, la aserción
    lo declara."""
    assert proc.returncode == 0, (
        "F2: la vista `status` debe emitir la proyección (rc=0); "
        f"hoy rc={proc.returncode}; stderr={proc.stderr.strip()!r}"
    )
    assert proc.stdout.strip(), (
        "F2: la vista no emitió el documento por stdout; "
        f"stderr={proc.stderr.strip()!r}"
    )
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            "F2: stdout no es un único documento JSON válido: "
            f"{proc.stdout[:200]!r}"
        ) from exc
    assert isinstance(doc, dict), (
        f"F2: el documento de la vista no es un objeto JSON: {doc!r}"
    )
    return doc


# ---------------------------------------------------------------- PD-2 / F2


def test_pd2_f2_idle_with_history_next_unit_and_next_not_closed_execution(
        tmp_path: Path) -> None:
    """PD-2 F2 (RED focal): reposo con historia — `active_feature` nulo,
    `active_packet` ausente, bloque `execution` de una feature cerrada y
    directorios de paquete históricos (uno sin recibo y uno con recibo) —
    la vista emite `entry=next-unit` y el `next` NO apunta a la ejecución
    cerrada (ni a resumirla)."""
    root = _build_root(tmp_path)
    _state_closed_feature(root)
    # Historia: directorios de paquete de la ejecución cerrada, con y sin
    # recibo; según la enmienda TODOS son historia en reposo.
    _packet_dir(root, PACKET_STUCK_ID, execution_id=CLOSED_EXECUTION_ID,
                feature_id=FEATURE_ID, receipt=False)
    _packet_dir(root, PACKET_RECEIVED_ID, execution_id=CLOSED_EXECUTION_ID,
                feature_id=FEATURE_ID, receipt=True)

    proc = _status(root, tmp_path / "home")
    doc = _status_document(proc)

    assert doc["entry"] == "next-unit", (
        "PD-2/F2 violada: en reposo con historia (active_feature nulo, "
        "active_packet ausente, bloque execution de una feature cerrada y "
        "directorios de paquete históricos) la entrada debe ser next-unit; "
        f"hoy {doc['entry']!r} — los directorios de paquete se leyeron como "
        "trabajo pendiente y/o el bloque execution se leyó como ejecución "
        f"activa. Documento: {json.dumps(doc, sort_keys=True)[:400]}"
    )
    next_text = json.dumps(doc.get("next"), ensure_ascii=False)
    assert CLOSED_EXECUTION_ID not in next_text, (
        "PD-2/F2 violada: el `next` apunta a la ejecución cerrada "
        f"({CLOSED_EXECUTION_ID}): {doc['next']!r}"
    )
    assert "resume the active execution" not in next_text, (
        "PD-2/F2 violada: el `next` ordena resumir la ejecución activa "
        "(no la hay: la ejecución del bloque es historia de una feature "
        f"cerrada): {doc['next']!r}"
    )


def test_pd2_f2_pending_dir_of_active_execution_without_receipt_reconciles(
        tmp_path: Path) -> None:
    """PD-2 F2 (regresión): con ejecución ACTIVA (`execution.feature_id`
    coincidente con `active_feature`), `active_packet` ausente y un
    directorio de paquete de ESA ejecución SIN recibo, el trabajo pendiente
    se atiende: `entry=continuity-reconcile` (nunca next-unit)."""
    root = _build_root(tmp_path)
    _state_active_execution(root)
    _packet_dir(root, PACKET_STUCK_ID, execution_id=CLOSED_EXECUTION_ID,
                feature_id=FEATURE_ID, receipt=False)

    proc = _status(root, tmp_path / "home")
    doc = _status_document(proc)

    assert doc["entry"] == "continuity-reconcile", (
        "PD-2/F2 violada: un directorio de paquete de la ejecución activa "
        "sin recibo ES trabajo pendiente y la entrada debe atenderlo "
        f"(continuity-reconcile), no {doc['entry']!r}"
    )


def test_pd2_f2_receipted_dir_of_active_execution_not_pending(
        tmp_path: Path) -> None:
    """PD-2 F2 (regresión): el MISMO directorio de paquete de la ejecución
    activa CON recibo en `.cdad/runtime/results/<execution_id>/<packet_id>/`
    NO cuenta como pendiente: la proyección es indistinguible de la del mismo
    proyecto SIN directorios de paquete (el `entry`/`next`/`packet` no se ven
    afectados por el directorio con recibo)."""
    root_with = _build_root(tmp_path)
    _state_active_execution(root_with)
    _packet_dir(root_with, PACKET_STUCK_ID, execution_id=CLOSED_EXECUTION_ID,
                feature_id=FEATURE_ID, receipt=True)

    root_without = _build_root(tmp_path / "baseline")
    _state_active_execution(root_without)

    doc_with = _status_document(_status(root_with, tmp_path / "home"))
    doc_without = _status_document(_status(root_without, tmp_path / "home"))

    def _summary(doc: dict) -> str:
        return json.dumps({k: doc.get(k) for k in ("entry", "next", "packet")},
                          ensure_ascii=False)

    affected = [
        key for key in ("entry", "next", "packet")
        if doc_with.get(key) != doc_without.get(key)
    ]
    assert not affected, (
        "PD-2/F2 violada: el directorio de paquete CON recibo "
        f"(.cdad/runtime/results/{CLOSED_EXECUTION_ID}/{PACKET_STUCK_ID}/) "
        "cuenta como pendiente — las claves de la proyección que el trabajo "
        f"pendiente podría mover difieren del baseline sin directorios: "
        f"{affected}; con recibo: {_summary(doc_with)}; sin directorios: "
        f"{_summary(doc_without)}"
    )
    next_text = json.dumps(doc_with.get("next"), ensure_ascii=False)
    assert PACKET_STUCK_ID not in next_text, (
        "PD-2/F2 violada: el `next` apunta al directorio de paquete con "
        f"recibo ({PACKET_STUCK_ID}): {doc_with['next']!r}"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
