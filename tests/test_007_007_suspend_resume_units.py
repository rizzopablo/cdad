"""RED 007-007 — suspensión y reanudación serial de unidades.

Oráculo caja negra: CLIs públicos sobre proyectos descartables. El fixture
base importa únicamente constructores de pruebas ya aprobados (que preparan
el proyecto mediante CLIs); nunca módulos de producto.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_007_002_dispatch_recovery import (
    _RecoveryProject, EPIC_ID, FEATURE_ID, PACKET_CLI, CONTINUITY_CLI,
    RESULT_CLI, REPO_ROOT,
)

FEATURE_B = "demo-700-suspend-unit-b"
STATE_REL = "docs/.cdad-state.json"
TIMEOUT = 120


def _assert_suspend_cli(fx: _RecoveryProject) -> None:
    """Asegura que RED no sea un falso positivo por verbo argparse ausente."""
    proc = fx.run_packet("suspend-unit", "-h")
    assert proc.returncode == 0, (
        "PC-01..10: `suspend-unit -h` debe responder rc=0; sin el verbo, "
        f"argparse puede devolver rc=2 igual que un rechazo de dominio: "
        f"{proc.stdout!r} {proc.stderr!r}")


def _resume_cli(fx: _RecoveryProject, *args: str):
    return fx.run_packet("resume-unit", "--project-root", str(fx.root), *args)


def _begin(fx: _RecoveryProject, label: str = "suspend-resume fixture", *,
           packet_id: str | None = None, attempt: int = 1,
           next_action: str = "continue the assignment",
           references: list | None = None, evidence: list | None = None):
    """Create continuity through the public CLI with its required update."""
    update = fx.base / "begin-update.json"
    if evidence is None:
        evidence_path = fx.root / "docs" / "begin-evidence.md"
        evidence_bytes = b"begin evidence fixture\n"
        evidence_path.write_bytes(evidence_bytes)
        evidence = [{
            "id": "begin-evidence",
            "reference": {"path": "docs/begin-evidence.md",
                          "sha256": hashlib.sha256(evidence_bytes).hexdigest()},
            "status": "vigente", "reason": "evidencia vigente de begin",
            "antecedent": None,
        }]
    update.write_text(json.dumps({
        "packet_id": packet_id or fx.packet_id,
        "attempt": attempt,
        "goal": label,
        "decisions": [{"decision": "fixture decision", "rationale": "fixture rationale"}],
        "uncertainties": [],
        "next_action": next_action,
        "references": references or [],
        "evidence": evidence or [],
    }), encoding="utf-8")
    return fx._run(CONTINUITY_CLI, [
        "begin", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--update", str(update), "--json",
    ])


def _suspend(fx: _RecoveryProject, *args: str, feature_id: str = FEATURE_ID):
    return fx.run_packet("suspend-unit", "--project-root", str(fx.root),
                         "--feature", feature_id, "--reason", "pausa RED", *args)


def _state(fx: _RecoveryProject) -> dict:
    return fx.read_state()


def _assert_rejected_unchanged(fx: _RecoveryProject, proc, label: str,
                               expected_source: str | None = None) -> None:
    assert proc.returncode == 2, f"{label}: rechazo rc=2; {proc.stdout!r} {proc.stderr!r}"
    text = proc.stdout + proc.stderr
    assert FEATURE_ID in text or "--feature" in text, f"{label}: diagnóstico identifica unidad: {text!r}"
    if expected_source:
        assert expected_source in text, f"{label}: diagnóstico nombra bloqueo {expected_source!r}: {text!r}"


def test_007_007_state_and_restore_exactly_preserve_unit_state(tmp_path: Path) -> None:
    """PC-1: conservar los campos y ausencias de unidad; restaurarlos exactos,
    mientras la suspensión publica reposo y estado `suspended`."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    before = _state(fx)
    proc = _suspend(fx)
    assert proc.returncode == 0, f"PC-1: suspender unidad activa: {proc.stdout!r} {proc.stderr!r}"
    suspended = _state(fx)
    record = (suspended.get("suspended_units") or {}).get(FEATURE_ID)
    assert isinstance(record, dict), "PC-1: registro por feature debe existir"
    assert record.get("reason") == "pausa RED", "PC-1: motivo conservado"
    expected = {k: before[k] for k in ("active_feature", "current_stage", "tdd_substage",
                "postconditions_status", "audit_status", "review_status", "active_packet", "execution") if k in before}
    assert record.get("unit_state") == expected, "PC-1: valor y presencia original del estado específico se preservan"
    assert suspended.get("active_feature") is None and suspended.get("current_stage") == "idle", "PC-1: publicación queda en reposo"
    resumed = _resume_cli(fx, "--feature", FEATURE_ID)
    assert resumed.returncode == 0, f"PC-1: reanudar estado válido: {resumed.stdout!r} {resumed.stderr!r}"
    after = _state(fx)
    assert {k: after.get(k) for k in expected} == expected, "PC-1: reanudación restaura estado y ausencias exactamente"

    absent = _RecoveryProject(tmp_path / "absent-statuses")
    _assert_suspend_cli(absent)
    initial = absent.read_state()
    initial.pop("audit_status", None)
    initial.pop("review_status", None)
    absent.write_state(initial)
    assert _suspend(absent).returncode == 0, "PC-1/B4 fixture: suspender tras eliminar campos originalmente ausentes"
    absent_record = absent.read_state()["suspended_units"][FEATURE_ID]
    assert "audit_status" not in absent_record["unit_state"] and "review_status" not in absent_record["unit_state"], "PC-1/B4: ausencia se representa por omisión"
    assert _resume_cli(absent, "--feature", FEATURE_ID).returncode == 0, "PC-1/B4: reanudar unidad sin esos campos"
    restored_absent = absent.read_state()
    assert "audit_status" not in restored_absent and "review_status" not in restored_absent, "PC-1/B4: campos ausentes permanecen ausentes"


def test_007_007_safe_boundary_prepared_unresolved_and_received_red(tmp_path: Path) -> None:
    """PC-2: prepared limpio y entrega RED recibida son bordes seguros;
    dispatch pendiente y señales inconclusas se rechazan sin cambios."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    # Un prepared legítimo no despachado se suspende sin alterar paquete/ancestros.
    packet_before = fx.packet_bytes(fx.packet_id, "REQUEST.json")
    proc = _suspend(fx)
    assert proc.returncode == 0, f"PC-2: prepared sin efectos es borde seguro: {proc.stdout!r} {proc.stderr!r}"
    assert fx.packet_bytes(fx.packet_id, "REQUEST.json") == packet_before, "PC-2: request conservado byte a byte"
    # El paquete preparado con una entrega staged ya no es borde seguro.
    staged = _RecoveryProject(tmp_path / "staged")
    _assert_suspend_cli(staged)
    descriptor = staged._stage_result()
    staged_result = staged.root / ".cdad" / "runtime" / "results" / staged.execution_id / staged.packet_id
    staged_result.mkdir(parents=True, exist_ok=True)
    (staged_result / "staged-result.json").write_bytes(descriptor.read_bytes())
    staged_before = staged.tree()
    staged_proc = _suspend(staged)
    assert staged_proc.returncode == 2, f"PC-2/B3: staged result bloquea suspensión: {staged_proc.stdout!r} {staged_proc.stderr!r}"
    assert staged.tree() == staged_before, "PC-2/B3: staged rechaza sin cambiar bytes ni inventario"
    # El caso RED recibido es el flujo integrado PC-10, donde la recepción se realiza por CLI.


def test_007_007_dispatch_without_active_packet_is_not_a_safe_boundary(tmp_path: Path) -> None:
    """PC-2/B3: la identidad del despacho registrado se verifica aunque
    `active_packet` sea null; el rechazo conserva el árbol byte a byte."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _begin(fx, "dispatch with detached active binding").returncode == 0, "fixture PC-2/B3: begin previo al despacho"
    dispatched = fx.run_packet(
        "prepare", "--project-root", str(fx.root), "--record-dispatch", fx.packet_id,
        "--attempt-id", "attempt-demo-700-001", "--input", str(fx._observation),
        "--continuity-attempt", "1",
    )
    assert dispatched.returncode == 0, f"fixture PC-2/B3: despacho público: {dispatched.stdout!r} {dispatched.stderr!r}"
    state = fx.read_state()
    state["active_packet"] = None
    fx.write_state(state)
    before = fx.tree()
    proc = _suspend(fx)
    assert proc.returncode == 2, f"PC-2/B3: despacho registrado sin active_packet bloquea: {proc.stdout!r} {proc.stderr!r}"
    text = proc.stdout + proc.stderr
    assert "dispatched" in text.lower() or "dispatch" in text.lower(), f"PC-2/B3: causa de bloqueo identifica despacho: {text!r}"
    assert fx.tree() == before, "PC-2/B3: rechazo no cambia bytes ni inventario"


def test_007_007_suspend_open_unit_without_packet_then_resume_prior_unit(tmp_path: Path) -> None:
    """PC-2: tras suspender A, puede abrirse B y suspenderla antes de
    `prepare`; luego la selección explícita permite reanudar A."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "PC-2 fixture: suspender A"
    state = fx.read_state()
    state["epic_features"].append({"id": FEATURE_B, "status": "queued"})
    fx.write_state(state)
    opened = fx.run_packet("open-unit", "--project-root", str(fx.root), "--feature", FEATURE_B)
    assert opened.returncode == 0, f"PC-2: open B desde reposo suspendido: {opened.stdout!r} {opened.stderr!r}"
    b_state = fx.read_state()
    assert b_state.get("active_feature") == FEATURE_B and b_state.get("active_packet") is None, "PC-2: B abierta sin paquete preparado"
    suspended_b = _suspend(fx, feature_id=FEATURE_B)
    assert suspended_b.returncode == 0, f"PC-2: suspender B sin prepare: {suspended_b.stdout!r} {suspended_b.stderr!r}"
    assert FEATURE_B in (fx.read_state().get("suspended_units") or {}), "PC-2: B queda registrada como suspendida"
    resumed_a = _resume_cli(fx, "--feature", FEATURE_ID)
    assert resumed_a.returncode == 0, f"PC-2: reanudar A tras suspender B sin paquete: {resumed_a.stdout!r} {resumed_a.stderr!r}"
    assert fx.read_state().get("active_feature") == FEATURE_ID, "PC-2: A vuelve a ser la unidad activa"


def test_007_007_continuity_checkpoints_link_without_fabricating_history(tmp_path: Path) -> None:
    """PC-3: checkpoints de suspensión/reanudación enlazados; sin recibos,
    begin ni ejecución nuevos. Sin cabeza no se fabrica continuidad y cadena
    ilegible bloquea sin escrituras."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    original_action = "continue from exact RED checkpoint"
    ref_path = fx.root / "docs" / "specs" / "demo-700-fixture.md"
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_bytes = b"identified continuity reference\n"
    ref_path.write_bytes(ref_bytes)
    original_refs = [{"path": "docs/specs/demo-700-fixture.md",
                      "sha256": hashlib.sha256(ref_bytes).hexdigest()}]
    assert _begin(fx, attempt=4, next_action=original_action,
                  references=original_refs).returncode == 0, "fixture PC-3: begin público, intento 4"
    before_execution = copy.deepcopy(_state(fx)["execution"])
    continuity = fx.root / ".cdad" / "executions" / fx.execution_id / "continuity"
    head_path = continuity / "head.json"
    assert head_path.is_file(), "fixture PC-3: begin publica cabeza en la ruta de continuidad de la ejecución"
    begin_head = json.loads(head_path.read_text(encoding="utf-8"))
    begin_sha = begin_head.get("body_sha256")
    assert isinstance(begin_sha, str) and begin_sha, "fixture PC-3: cabeza del begin tiene digest"
    begin_body_path = continuity / "bodies" / f"{begin_sha}.json"
    assert begin_body_path.is_file(), "fixture PC-3: cuerpo del begin existe"
    begin_body = json.loads(begin_body_path.read_text(encoding="utf-8"))
    assert begin_body.get("attempt") == 4 and begin_body.get("next_action") == original_action, "fixture PC-3: begin conserva los datos identificables"
    assert _suspend(fx).returncode == 0, "PC-3: suspender con cabeza de continuidad"
    suspend_head = json.loads(head_path.read_text(encoding="utf-8"))
    suspend_sha = suspend_head.get("body_sha256")
    assert isinstance(suspend_sha, str) and suspend_sha != begin_sha, "PC-3/B5: suspensión publica checkpoint nuevo"
    suspend_body = json.loads((continuity / "bodies" / f"{suspend_sha}.json").read_text(encoding="utf-8"))
    assert suspend_body.get("attempt") == 4, "PC-3/B5: checkpoint de suspensión conserva intento 4"
    assert suspend_body.get("prev", {}).get("checkpoint_sha256") == begin_sha, "PC-3/B5: suspensión enlaza prev al begin"
    assert any("suspend" in str(d).lower() for d in suspend_body.get("decisions", [])), "PC-3/B5: checkpoint declara decisión de suspensión"
    assert _resume_cli(fx, "--feature", FEATURE_ID).returncode == 0, "PC-3: reanudar con cadena íntegra"
    resume_head = json.loads(head_path.read_text(encoding="utf-8"))
    resume_sha = resume_head.get("body_sha256")
    resume_body = json.loads((continuity / "bodies" / f"{resume_sha}.json").read_text(encoding="utf-8"))
    assert resume_body.get("attempt") == 4, "PC-3/B5: reanudación conserva intento 4"
    assert resume_body.get("prev", {}).get("checkpoint_sha256") == suspend_sha, "PC-3/B5: reanudación enlaza al checkpoint de suspensión"
    assert resume_body.get("next_action") == original_action, "PC-3/B5: siguiente acción anterior se restaura"
    assert _state(fx)["execution"] == before_execution, "PC-3: no se crea ejecución nueva"
    transitions = [e for e in _state(fx).get("stage_history", []) if isinstance(e, dict)]
    assert any(e.get("transition") == "suspend" and e.get("feature") == FEATURE_ID for e in transitions), "PC-3/B5: historial registra suspensión"
    assert any(e.get("transition") == "resume" and e.get("feature") == FEATURE_ID for e in transitions), "PC-3/B5: historial registra reanudación"
    # Invalid chain is real on-disk corruption, not an internal mock.
    bad = _RecoveryProject(tmp_path / "bad")
    _assert_suspend_cli(bad)
    assert _begin(bad).returncode == 0, "fixture PC-3: begin para corrupción"
    bad_head = bad.root / ".cdad" / "executions" / bad.execution_id / "continuity" / "head.json"
    assert bad_head.is_file(), "fixture PC-3: cabeza de continuidad de corrupción existe"
    bad_head.write_text("{broken", encoding="utf-8")
    before = bad.tree()
    proc = _suspend(bad)
    assert proc.returncode == 2, f"PC-3: continuidad ilegible rechazada: {proc.stdout!r} {proc.stderr!r}"
    assert bad.tree() == before, "PC-3: fallo de continuidad sin efectos"


def test_007_007_resume_explicit_selection_and_active_exclusion(tmp_path: Path) -> None:
    """PC-4: selección --feature obligatoria, desconocidos y unidad activa
    rechazan con rc=2 y sin efectos."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "fixture PC-4: unidad suspendida"
    before = fx.tree()
    for args in ((), ("--feature", "missing-fixture-unit")):
        proc = _resume_cli(fx, *args)
        assert proc.returncode == 2, f"PC-4: selección inválida debe rc=2: {proc.stdout!r} {proc.stderr!r}"
        assert fx.tree() == before, "PC-4: selección inválida no escribe"
    active = _RecoveryProject(tmp_path / "active")
    _assert_suspend_cli(active)
    # En proyecto distinto la unidad activa impide resume aun si se pide su ID.
    proc = _resume_cli(active, "--feature", FEATURE_ID)
    assert proc.returncode == 2, f"PC-4: no reanudar sobre unidad activa: {proc.stdout!r} {proc.stderr!r}"


def test_007_007_resume_rejects_stale_authority_contract_policy_or_evidence(tmp_path: Path) -> None:
    """PC-5: autoridad, digests, política y evidencia dejan la unidad suspendida
    si cualquiera perdió vigencia."""
    for mutation in ("authority", "contract", "policy", "evidence"):
        fx = _RecoveryProject(tmp_path / mutation)
        _assert_suspend_cli(fx)
        evidence_path = fx.root / "docs" / "evidence-fixture.md"
        evidence_bytes = b"current evidence for resume check\n"
        evidence_path.write_bytes(evidence_bytes)
        if mutation == "evidence":
            assert _begin(fx, "vigent evidence", evidence=[{
                "id": "resume-evidence",
                "reference": {"path": "docs/evidence-fixture.md",
                              "sha256": hashlib.sha256(evidence_bytes).hexdigest()},
                "status": "vigente", "reason": "evidencia vigente de fixture",
                "antecedent": None,
            }]).returncode == 0, "fixture PC-5: begin publica evidencia vigente"
            head_path = fx.root / ".cdad" / "executions" / fx.execution_id / "continuity" / "head.json"
            assert head_path.is_file(), "fixture PC-5: cabeza de continuidad existe"
            head = json.loads(head_path.read_text(encoding="utf-8"))
            body_path = head_path.parent / "bodies" / f"{head['body_sha256']}.json"
            body = json.loads(body_path.read_text(encoding="utf-8"))
            assert any(item.get("id") == "resume-evidence" and item.get("status") == "vigente" for item in body.get("evidence", [])), "fixture PC-5: la cabeza enlaza evidencia vigente real"
        assert _suspend(fx).returncode == 0, f"fixture PC-5 ({mutation}): suspensión"
        if mutation == "authority":
            state = fx.read_state(); state["hitl_delegation"]["status"] = "revoked"; fx.write_state(state)
        elif mutation == "contract":
            request = fx.request_of(fx.packet_id)
            pinned_path = (request.get("contract") or {}).get("path")
            assert isinstance(pinned_path, str) and pinned_path, "fixture PC-5: paquete declara ruta contractual pineada"
            pinned_file = fx.root / pinned_path
            assert pinned_file.is_file(), f"fixture PC-5: contrato realmente pineado existe: {pinned_path}"
            pinned_file.write_bytes(pinned_file.read_bytes() + b"altered pinned contract\n")
        elif mutation == "policy":
            policy = fx.root / "docs/cdad-policy.json"; policy.write_bytes(policy.read_bytes() + b"\n")
        else:
            evidence_path.write_bytes(b"evidence changed after suspension\n")
        before = fx.tree()
        proc = _resume_cli(fx, "--feature", FEATURE_ID)
        assert proc.returncode == 2, f"PC-5 ({mutation}): evidencia vigente requerida: {proc.stdout!r} {proc.stderr!r}"
        assert fx.tree() == before, f"PC-5 ({mutation}): rechazo sin mutaciones"


@pytest.mark.parametrize("mutation", ["changed-evidence", "missing-evidence", "changed-pinned-contract"])
def test_007_007_suspend_rejects_stale_vigency_present_before_suspension(
        tmp_path: Path, mutation: str) -> None:
    """PC-5/B4: una referencia vigente ya alterada/ausente antes de suspender,
    o el contrato realmente pineado por el paquete ya alterado, bloquea la
    suspensión antes de publicar cualquier cambio."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    evidence_path = fx.root / "docs" / "evidence-before-suspend.md"
    evidence_bytes = b"declared-current-evidence\n"
    evidence_path.write_bytes(evidence_bytes)
    assert _begin(fx, "pre-suspend vigency", evidence=[{
        "id": "pre-suspend-evidence",
        "reference": {"path": "docs/evidence-before-suspend.md",
                      "sha256": hashlib.sha256(evidence_bytes).hexdigest()},
        "status": "vigente", "reason": "evidencia vigente declarada",
        "antecedent": None,
    }]).returncode == 0, "fixture PC-5/B4: begin con evidencia vigente"

    if mutation == "changed-evidence":
        evidence_path.write_bytes(b"changed before suspension\n")
        cause = "evidence-before-suspend.md"
    elif mutation == "missing-evidence":
        evidence_path.unlink()
        cause = "evidence-before-suspend.md"
    else:
        request = fx.request_of(fx.packet_id)
        pinned_path = (request.get("contract") or {}).get("path")
        assert isinstance(pinned_path, str) and pinned_path, "fixture PC-5/B4: paquete declara contrato pineado"
        pinned_contract = fx.root / pinned_path
        assert pinned_contract.is_file(), f"fixture PC-5/B4: contrato pineado existe: {pinned_path}"
        pinned_contract.write_bytes(pinned_contract.read_bytes() + b"changed before suspension\n")
        cause = pinned_path

    before = fx.tree()
    proc = _suspend(fx)
    assert proc.returncode == 2, f"PC-5/B4 ({mutation}): suspensión bloqueada antes de publicación: {proc.stdout!r} {proc.stderr!r}"
    text = proc.stdout + proc.stderr
    assert cause in text, f"PC-5/B4 ({mutation}): diagnóstico identifica referencia/contrato inválido {cause!r}: {text!r}"
    assert fx.tree() == before, f"PC-5/B4 ({mutation}): rechazo conserva estado, continuidad y artefactos byte a byte"


def test_007_007_open_unit_preserves_suspended_registry_and_dependencies(tmp_path: Path) -> None:
    """PC-6: open-unit desde reposo conserva suspendidas y solo abre unidad
    elegible, no una suspendida ni una dependiente incompleta."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "fixture PC-6: suspensión"
    state = fx.read_state()
    state["epic_features"].append({"id": FEATURE_B, "status": "queued", "depends_on": ["missing-dependency"]})
    fx.write_state(state)
    proc = fx.run_packet("open-unit", "--project-root", str(fx.root), "--feature", FEATURE_B)
    assert proc.returncode == 2, f"PC-6: dependencia incompleta rechazada: {proc.stdout!r} {proc.stderr!r}"
    current = fx.read_state()
    assert FEATURE_ID in current.get("suspended_units", {}), "PC-6: registro suspendido permanece"
    assert current.get("active_feature") is None, "PC-6: unidad inelegible no se abre"


def test_007_007_mutating_consumers_block_suspended_units(tmp_path: Path) -> None:
    """PC-7: consumidores mutantes resuelven identidad desde su propia entrada
    y bloquean el avance de suspendidas antes de publicar efectos."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _begin(fx, "mutating consumer fixture").returncode == 0, "fixture PC-7: contexto activo"
    packet = fx.packet_id
    assert _suspend(fx).returncode == 0, "fixture PC-7: suspensión"
    context = fx.execution_context_path()
    candidates = [
        (PACKET_CLI, ["prepare", "--project-root", str(fx.root), "--feature", FEATURE_ID]),
        (PACKET_CLI, ["register-transition", "--project-root", str(fx.root), "--transition", "closure", "--stage", "merge", "--approve-by", "Demo Approver"]),
        (CONTINUITY_CLI, ["begin", "--project-root", str(fx.root), "--execution-context", str(context)]),
        (CONTINUITY_CLI, ["checkpoint", "--project-root", str(fx.root), "--execution-context", str(context)]),
        (CONTINUITY_CLI, ["reanchor", "--project-root", str(fx.root), "--execution-context", str(context)]),
    ]
    before = fx.tree()
    for script, args in candidates:
        proc = fx._run(script, args)
        assert proc.returncode != 0, f"PC-7: mutación suspendida rechazada ({args[0]}): {proc.stdout!r} {proc.stderr!r}"
        text = proc.stdout + proc.stderr
        assert "resume-unit" in text or FEATURE_ID in text, f"PC-7: rechazo accionable ({args[0]}): {text!r}"
        assert fx.tree() == before, f"PC-7: {args[0]} no debe cambiar árbol suspendido"


def test_007_007_managed_checkpoint_after_state_removal_is_blocked(tmp_path: Path) -> None:
    """PC-7/A2: checkpoint gestionado rechaza state ausente y conserva head."""
    managed = _RecoveryProject(tmp_path / "managed")
    _assert_suspend_cli(managed)
    assert _begin(managed, "managed checkpoint guard").returncode == 0, "fixture PC-7/A2: begin gestionado"
    assert _suspend(managed).returncode == 0, "fixture PC-7/A2: A suspendida"
    managed_head = managed.root / ".cdad" / "executions" / managed.execution_id / "continuity" / "head.json"
    assert managed_head.is_file(), "fixture PC-7/A2: head gestionado existe"
    head_before = managed_head.read_bytes()
    state_path = managed.root / STATE_REL
    state_path.unlink()
    update = managed.base / "managed-checkpoint-update.json"
    update.write_text(json.dumps({
        "packet_id": managed.packet_id, "attempt": 1, "goal": "checkpoint gestionado",
        "decisions": [{"decision": "avance", "rationale": "fixture"}],
        "uncertainties": [], "next_action": "continuar", "references": [],
        "evidence": [{
            "id": "begin-evidence",
            "reference": {"path": "docs/begin-evidence.md",
                          "sha256": hashlib.sha256((managed.root / "docs/begin-evidence.md").read_bytes()).hexdigest()},
            "status": "vigente", "reason": "evidencia vigente de begin", "antecedent": None,
        }],
    }), encoding="utf-8")
    rejected = managed._run(CONTINUITY_CLI, [
        "checkpoint", "--project-root", str(managed.root),
        "--execution-context", str(managed.execution_context_path()),
        "--update", str(update), "--json",
    ])
    assert rejected.returncode != 0, f"PC-7/A2: checkpoint gestionado sin state rechaza: {rejected.stdout!r} {rejected.stderr!r}"
    assert managed_head.read_bytes() == head_before, "PC-7/A2: checkpoint rechazado no cambia head gestionado"


def test_007_007_standalone_checkpoint_without_project_state_still_works(
        tmp_path: Path) -> None:
    """PC-7/A2 control: checkpoint standalone conserva compatibilidad sin
    `docs/.cdad-state.json`."""
    standalone = tmp_path / "standalone"
    root = standalone / "project"
    home = standalone / "home"
    root.mkdir(parents=True); home.mkdir(parents=True)
    execution_id = "exec-standalone-checkpoint-fixture"
    packet_id = "standalone-checkpoint-fixture-packet"
    context = root / "fixture" / "execution.json"
    context.parent.mkdir(parents=True)
    context.write_text(json.dumps({
        "schema_version": 1, "execution_id": execution_id, "runtime": "opencode",
        "hitl_delegation": {"authority_ref": "docs/epics/standalone/execution.md",
                            "expires_on": "2099-12-31"},
    }), encoding="utf-8")
    evidence_file = root / "fixture" / "evidence.md"
    evidence_file.write_bytes(b"standalone evidence\n")
    standalone_update = root / "fixture" / "update.json"
    standalone_update.write_text(json.dumps({
        "packet_id": packet_id, "attempt": 1, "goal": "standalone checkpoint",
        "decisions": [{"decision": "continue", "rationale": "standalone fixture"}],
        "uncertainties": [], "next_action": "continue standalone", "references": [],
        "evidence": [{
            "id": "standalone-evidence",
            "reference": {"path": "fixture/evidence.md",
                          "sha256": hashlib.sha256(evidence_file.read_bytes()).hexdigest()},
            "status": "vigente", "reason": "standalone evidence valid", "antecedent": None,
        }],
    }), encoding="utf-8")
    env = dict(os.environ); env["HOME"] = str(home)
    accepted = subprocess.run([
        sys.executable, str(CONTINUITY_CLI), "checkpoint", "--project-root", str(root),
        "--execution-context", str(context), "--update", str(standalone_update), "--json",
    ], capture_output=True, text=True, cwd=REPO_ROOT, env=env,
       stdin=subprocess.DEVNULL, timeout=TIMEOUT)
    assert accepted.returncode == 0, f"PC-7/A2 control: standalone checkpoint sigue permitido: {accepted.stdout!r} {accepted.stderr!r}"
    assert (root / ".cdad" / "executions" / execution_id / "continuity" / "head.json").is_file(), "PC-7/A2 control: head standalone publicado"
    assert not (root / STATE_REL).exists(), "PC-7/A2 control: standalone no crea state de proyecto"


def test_007_007_status_and_validate_state_report_suspension_coherently(tmp_path: Path) -> None:
    """PC-8: validate-state distingue reposo suspendido y contexto suspendido;
    status agrega resumen determinista y selección explícita, conservando forma."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "fixture PC-8: suspensión"
    status = fx.status()
    assert status.returncode == 0, f"PC-8: status legible: {status.stdout!r} {status.stderr!r}"
    doc = json.loads(status.stdout)
    assert doc.get("situation") == "units-suspended", "PC-8: situación units-suspended"
    assert doc.get("suspended_units") == [{"feature_id": FEATURE_ID, "suspended_at": doc.get("suspended_units", [{}])[0].get("suspended_at"), "reason": "pausa RED", "stage": "tdd", "substage": "red"}], "PC-8: proyección compacta y motivo"
    next_block = doc.get("next") or {}
    assert (next_block.get("operation") or {}).get("verb") == "select-unit", "PC-8: instrucción requiere selección, no elige sola"
    validate = fx.validate_state()
    assert validate.returncode == 0, f"PC-8: coherencia global de suspendida en reposo: {validate.stdout!r} {validate.stderr!r}"
    contextual = fx.run_packet("validate-state", "--project-root", str(fx.root), "--execution-context", str(fx.execution_context_path()))
    assert contextual.returncode == 2 and "resume-unit" in contextual.stdout + contextual.stderr, "PC-8: validación contextual pide reanudar explícitamente"

    malformed = _RecoveryProject(tmp_path / "missing-reason")
    _assert_suspend_cli(malformed)
    assert _suspend(malformed).returncode == 0, "PC-8/I1 fixture: unidad suspendida"
    malformed_state = malformed.read_state()
    del malformed_state["suspended_units"][FEATURE_ID]["reason"]
    malformed.write_state(malformed_state)
    bad_status = malformed.status()
    assert bad_status.returncode == 0, f"PC-8/I1: status diagnostica incoherencia estructurada: {bad_status.stdout!r} {bad_status.stderr!r}"
    assert "Traceback" not in bad_status.stdout + bad_status.stderr, "PC-8/I1: incoherencia no filtra traceback"
    bad_doc = json.loads(bad_status.stdout)
    assert bad_doc.get("situation") == "diagnosis" and bad_doc.get("unknowns"), "PC-8/I1: registro sin reason da diagnóstico estructurado"

def test_007_007_status_does_not_offer_open_for_suspended_dependency(tmp_path: Path) -> None:
    """PC-8/I1: con una única queued dependiente de una unidad suspendida
    (no `done`), la orientación omite open-unit como alternativa."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "fixture PC-8/I1: unidad A suspendida"
    state = fx.read_state()
    state["epic_features"].append({"id": FEATURE_B, "status": "queued", "depends_on": [FEATURE_ID]})
    fx.write_state(state)
    proc = fx.status()
    assert proc.returncode == 0, f"PC-8/I1: status legible: {proc.stdout!r} {proc.stderr!r}"
    doc = json.loads(proc.stdout)
    alternatives = (doc.get("next") or {}).get("alternatives") or []
    assert not any(isinstance(item, dict) and item.get("verb") == "open-unit" for item in alternatives), "PC-8/I1: unidad dependiente no es elegible para open-unit"


def test_007_007_publication_lock_and_repetition_are_atomic(tmp_path: Path) -> None:
    """PC-9: lock/repetición no producen efectos ni checkpoints adicionales."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _suspend(fx).returncode == 0, "fixture PC-9: primera suspensión"
    before = fx.tree()
    proc = _suspend(fx)
    assert proc.returncode == 2, f"PC-9: repetir suspensión rechaza: {proc.stdout!r} {proc.stderr!r}"
    assert fx.tree() == before, "PC-9: repetición no crea checkpoints"
    # Lock ocupado de forma real: archivo lock existente y exclusivo.
    lock = fx.root / ".cdad" / ".lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        before = fx.tree()
        proc = _resume_cli(fx, "--feature", FEATURE_ID)
        assert proc.returncode == 2, f"PC-9: lock ocupado rechaza: {proc.stdout!r} {proc.stderr!r}"
        assert fx.tree() == before, "PC-9: lock ocupado sin efectos"
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    publication = _RecoveryProject(tmp_path / "state-publication-failure")
    _assert_suspend_cli(publication)
    assert _begin(publication, "publication failure fixture").returncode == 0, "PC-9/B2 fixture: continuidad previa"
    continuity = publication.root / ".cdad" / "executions" / publication.execution_id / "continuity" / "head.json"
    assert continuity.is_file(), "PC-9/B2 fixture: cabeza previa existe"
    state_path = publication.root / STATE_REL
    state_before = state_path.read_bytes()
    head_before = continuity.read_bytes()
    temp_path = publication.root / "docs" / f"{STATE_REL.rsplit('/', 1)[-1]}.tmp"
    temp_path.mkdir()
    failed = _suspend(publication)
    assert failed.returncode == 2, f"PC-9/B2: fallo real al publicar estado da rc=2: {failed.stdout!r} {failed.stderr!r}"
    assert state_path.read_bytes() == state_before, "PC-9/B2: rollback conserva estado byte a byte"
    assert continuity.read_bytes() == head_before, "PC-9/B2: rollback conserva cabeza byte a byte"


@pytest.mark.parametrize("close_b", [True, False], ids=["close-B", "suspend-B"])
def test_007_007_received_red_unit_can_suspend_open_other_and_resume_verified_begin(
        tmp_path: Path, close_b: bool) -> None:
    """PC-10: A en RED con recibo durable puede suspenderse; B se ejecuta y
    cierra o suspende; A se reanuda y prepara→begin→verify-begin sin repetir
    el despacho recibido."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _begin(fx, "begin A").returncode == 0, "fixture PC-10: begin A"
    dispatched = fx.run_packet(
        "prepare", "--project-root", str(fx.root), "--record-dispatch", fx.packet_id,
        "--attempt-id", "attempt-demo-700-001", "--input", str(fx._observation),
        "--continuity-attempt", "1",
    )
    assert dispatched.returncode == 0, f"fixture PC-10: despacho A: {dispatched.stdout!r} {dispatched.stderr!r}"
    descriptor = fx._stage_result()
    received = fx.run_result(
        "receive", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--packet", str(fx.packet_dir() / "PACKET.md"),
        "--request", str(fx.packet_dir() / "REQUEST.json"),
        "--descriptor", str(descriptor), "--continuity-attempt", "1",
    )
    assert received.returncode == 0, f"fixture PC-10: recepción durable de A: {received.stdout!r} {received.stderr!r}"
    prior_dispatches = fx.dispatch_files()
    before_state = fx.read_state()
    assert fx.receipt_path().is_file(), "fixture PC-10: A tiene recibo durable"
    proc = _suspend(fx)
    assert proc.returncode == 0, f"PC-10: RED recibido es borde seguro: {proc.stdout!r} {proc.stderr!r}"
    state = fx.read_state(); state["epic_features"].append({"id": FEATURE_B, "status": "queued"}); fx.write_state(state)
    b_contract_rel = f"docs/specs/{FEATURE_B}/spec.md"
    b_contract = b"# Approved fixture contract for unit B\n\nPC-10 fixture.\n"
    b_contract_path = fx.root / b_contract_rel
    b_contract_path.parent.mkdir(parents=True, exist_ok=True)
    b_contract_path.write_bytes(b_contract)
    opened = fx.run_packet("open-unit", "--project-root", str(fx.root), "--feature", FEATURE_B)
    assert opened.returncode == 0, f"PC-10: abrir B con A suspendida: {opened.stdout!r} {opened.stderr!r}"
    gate = fx.run_packet(
        "register-transition", "--project-root", str(fx.root),
        "--transition", "gate", "--stage", "specification",
        "--approve-by", "Demo Approver", "--contract-path", b_contract_rel,
    )
    assert gate.returncode == 0, f"PC-10 fixture: aprobar contrato B por gate público: {gate.stdout!r} {gate.stderr!r}"
    # B se prepara por la ruta pública (la fixture tiene la aprobación contractual de A; el CLI
    # debe consumir únicamente la unidad activa y su contrato publicado).
    bprep = fx.run_packet("prepare", "--project-root", str(fx.root), "--role", "test-writer", "--substage", "red", "--objective", "fixture B")
    assert bprep.returncode == 0, f"PC-10: trabajo trazable B: {bprep.stdout!r} {bprep.stderr!r}"
    if close_b:
        closure_rel = f"docs/closures/{FEATURE_B}-closure.md"
        closure = fx.root / closure_rel
        closure.parent.mkdir(parents=True, exist_ok=True)
        closure.write_text("# Fixture closure for unit B\n", encoding="utf-8")
        close = fx.run_packet("register-transition", "--project-root", str(fx.root), "--transition", "closure", "--stage", "merge", "--approve-by", "Demo Approver", "--closure-path", closure_rel)
        assert close.returncode == 0, f"PC-10: cierre legítimo B: {close.stdout!r} {close.stderr!r}"
    else:
        assert _suspend(fx, "--feature", FEATURE_B).returncode == 0, "PC-10: suspensión B"
    resumed = _resume_cli(fx, "--feature", FEATURE_ID)
    assert resumed.returncode == 0, f"PC-10: reanudar A explícitamente: {resumed.stdout!r} {resumed.stderr!r}"
    restored = fx.read_state()
    assert restored.get("active_feature") == FEATURE_ID, "PC-10: identidad A restaurada"
    assert restored.get("active_packet") == before_state.get("active_packet"), "PC-10: binding del paquete recibido conserva su estado exacto"
    assert fx.receipt_path().is_file(), "PC-10: recibo durable no se pierde al reanudar"
    prep = fx.run_packet("prepare", "--project-root", str(fx.root), "--role", "test-writer", "--substage", "red", "--objective", "reanudar A")
    assert prep.returncode == 0, f"PC-10: continuar prepare: {prep.stdout!r} {prep.stderr!r}"
    prepared_packet = (fx.read_state().get("active_packet") or {}).get("id")
    assert isinstance(prepared_packet, str) and prepared_packet, "PC-10: prepare publica el paquete a verificar"
    begun = _begin(fx, "reanudar A", packet_id=prepared_packet)
    assert begun.returncode == 0, f"PC-10: begin vuelve al contexto existente: {begun.stdout!r} {begun.stderr!r}"
    verify = fx._run(CONTINUITY_CLI, [
        "verify-begin", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--packet", prepared_packet, "--attempt", "1", "--json",
    ])
    assert verify.returncode == 0, f"PC-10: verify-begin: {verify.stdout!r} {verify.stderr!r}"
    assert fx.dispatch_files() == prior_dispatches, "PC-10: no se repite el despacho recibido"
