"""RED 007-008 — acción canónica en el cierre de recibo.

Contrato: `docs/specs/007-008-receipt-next-action/spec.md` (PC-01..PC-06 con
los ajustes AJ1–AJ3, que prevalecen).

Caja negra: sólo CLIs públicos del repo sobre proyectos descartables. Los
fixtures se REUTILIZAN de los módulos aprobados (no se duplican):

- `_Project`, `_orphan_receipt` y aserciones de cadena de
  `test_007_003_continuity_at_edges.py` (recepción/replay, recibo externo,
  recuperación del cierre pendiente);
- `_RecoveryProject` y los verbos de suspensión de
  `test_007_007_suspend_resume_units.py` (PC-10: unidad RED recibida).

Archivo nuevo (justificación): los tests de 007-003 acumulan escenarios con
`_Cases` y sus nombres son estables por PC de 007-003; agregar aquí las
variantes parametrizadas de 007-008 mantiene la trazabilidad PC→test de
ambas unidades sin alterar los tests vecinos, que son el gate de
no-regresión.

Mapa de cobertura (AJ2):
- PC-01 → test_007_008_new_close_has_canonical_action (4 variantes, AJ1).
- PC-02 → test_007_008_new_close_preserves_context_and_link.
- PC-03 → test_007_008_entries_converge_without_approval (4 entradas).
- PC-04 → test_007_008_replay_preserves_history (3 variantes) y
          test_007_008_conflicting_valid_receipt_is_rejected (AJ3b).
- PC-05 → test_007_008_resume_unit_restores_canonical_action (2 variantes,
          AJ3a) y test_007_008_resume_unit_keeps_unreceived_action.
- PC-06 → test_007_008_reads_are_coherent_without_approval.

El literal esperado se declara aquí de forma independiente (§3.2); no se
importa del productor.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from test_007_003_continuity_at_edges import (
    CONTINUITY_CLI,
    PACKET_CLI,
    _Project,
    _orphan_receipt,
    assert_rc0,
    assert_rejected,
    json_doc,
    sha256_bytes,
)
from test_007_007_suspend_resume_units import (
    FEATURE_B,
    FEATURE_ID,
    _RecoveryProject,
    _assert_suspend_cli,
    _begin,
    _resume_cli,
    _suspend,
)

# §3.2 — declarado de forma independiente del productor.
CANONICAL_ACTION = (
    "recibo recibido mecánicamente; no repetir despacho/recepción; "
    "revisar el resultado sin presumir aprobación")

REDISPATCH_ACTION = "re-despachar el paquete al runtime y recibir su resultado"
OTHER_ACTION = "continuar el encargo"
OBSOLETE_ACTION = "despachar nuevamente el intento (acción histórica)"
_ABSENT = object()

PRESERVED_KEYS = ("goal", "authority", "uncertainties", "references",
                  "budget", "changes", "evidence", "execution_id",
                  "packet_id", "attempt")


# ---------------------------------------------------------------- helpers


def _begin_with_action(fx: _Project, action: object, *, attempt: int = 1):
    """`begin` público con la acción previa declarada; `_ABSENT` elimina la
    clave del input válido (AJ1), no la sustituye por `null`."""
    update = fx.write_update(attempt=attempt, label=f"begin-{attempt}")
    doc = json.loads(update.read_text(encoding="utf-8"))
    doc.pop("next_action")
    doc.update({} if action is _ABSENT else {"next_action": action})
    update.write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True)
                      + "\n", encoding="utf-8")
    return fx.run(CONTINUITY_CLI, "begin", "--project-root", str(fx.root),
                  "--execution-context", str(fx.ctx), "--update", str(update),
                  "--json")


def _head_body(fx: _Project, label: str) -> tuple[dict, dict]:
    head = fx.head(label)
    return head, fx.body(head["body_sha256"], label)


def _received_close(fx: _Project, label: str) -> tuple[dict, dict, dict]:
    """Recepción ordinaria del intento 1 tras `begin`; devuelve
    (cabeza previa, cuerpo previo, cuerpo del cierre)."""
    head_before, body_before = _head_body(fx, label)
    fx.mark_dispatched()
    assert_rc0(fx.receive(n=1), label, "`receive --continuity-attempt 1`")
    _, close_body = fx.assert_close(1, label)
    return head_before, body_before, close_body


def _reconcile(fx: _Project):
    return fx.run(CONTINUITY_CLI, "reconcile", "--project-root", str(fx.root),
                  "--execution-context", str(fx.ctx), "--packet",
                  fx.packet_id, "--json")


def _status(fx: _Project):
    return fx.run(PACKET_CLI, "status", "--project-root", str(fx.root))


def _rewrite_head_action(fx: _Project, action: str) -> str:
    """Cierre histórico con acción obsoleta y cadena ÍNTEGRA: el cuerpo se
    reescribe con su digest real (content-addressed) y la cabeza apunta a
    él con el mismo `seq`/`prev` (PC-04, oráculo de cadena demostrable)."""
    head, body = _head_body(fx, "PC-04 histórico obsoleto")
    body["next_action"] = action
    sha = fx.write_body(body)
    head["body_sha256"] = sha
    fx.write_head(head)
    return sha


# Entradas de PC-03: cada una deja el cierre del intento N y devuelve N.
# `snap` se invoca en cuanto el recibo es durable y ANTES de la entrada de
# cierre (validación externa / recuperación) para fijar sus bytes.
def _durable_snapshot(fx: _Project) -> dict[str, object]:
    return {"receipt": fx.receipt_bytes(), "parts": fx.parts_files()}


def _entry_ordinary(fx: _Project, snap) -> int:
    assert_rc0(fx.begin(attempt=1, next_action=REDISPATCH_ACTION),
               "PC-03 ordinaria", "`begin`")
    fx.mark_dispatched()
    assert_rc0(fx.receive(n=1), "PC-03 ordinaria", "`receive`")
    return 1


def _entry_external(fx: _Project, snap) -> int:
    _orphan_receipt(fx, close_attempt=2, label="PC-03 externa")
    snap(fx)
    assert_rc0(fx.validate_receipt(close=True, attempt=2), "PC-03 externa",
               "`validate-receipt --close-continuity`")
    return 2


def _entry_recovery(fx: _Project, snap) -> int:
    _orphan_receipt(fx, close_attempt=2, label="PC-03 recuperación")
    snap(fx)
    assert_rc0(fx.checkpoint_receipt(attempt=2), "PC-03 recuperación",
               "`checkpoint-receipt`")
    return 2


def _entry_recovery_after_transition(fx: _Project, snap) -> int:
    _orphan_receipt(fx, close_attempt=2, label="PC-03 tras transición")
    snap(fx)
    assert_rc0(fx.delivery(), "PC-03 tras transición",
               "la transición de entrega")
    assert_rc0(fx.checkpoint_receipt(attempt=2), "PC-03 tras transición",
               "`checkpoint-receipt`")
    return 2


# Variantes de replay de PC-04: preparan la historia tras el cierre.
def _replay_immediate(fx: _Project) -> str:
    return CANONICAL_ACTION


def _replay_after_links(fx: _Project) -> str:
    assert_rc0(fx.checkpoint(attempt=1, label="later-1"), "PC-04 enlaces",
               "checkpoint posterior 1")
    assert_rc0(fx.checkpoint(attempt=1, label="later-2"), "PC-04 enlaces",
               "checkpoint posterior 2")
    return CANONICAL_ACTION


def _replay_obsolete(fx: _Project) -> str:
    _rewrite_head_action(fx, OBSOLETE_ACTION)
    return OBSOLETE_ACTION


# PC-05: B se cierra o se suspende tras abrirse con A suspendida.
def _open_b(fx: _RecoveryProject) -> None:
    state = fx.read_state()
    state["epic_features"].append({"id": FEATURE_B, "status": "queued"})
    fx.write_state(state)
    contract_rel = f"docs/specs/{FEATURE_B}/spec.md"
    contract = fx.root / contract_rel
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_bytes(b"# Approved fixture contract for unit B\n")
    opened = fx.run_packet("open-unit", "--project-root", str(fx.root),
                           "--feature", FEATURE_B)
    assert opened.returncode == 0, (
        f"PC-05 fixture: abrir B: {opened.stdout!r} {opened.stderr!r}")
    gate = fx.run_packet(
        "register-transition", "--project-root", str(fx.root),
        "--transition", "gate", "--stage", "specification",
        "--approve-by", "Demo Approver", "--contract-path", contract_rel)
    assert gate.returncode == 0, (
        f"PC-05 fixture: gate B: {gate.stdout!r} {gate.stderr!r}")
    prep = fx.run_packet("prepare", "--project-root", str(fx.root), "--role",
                         "test-writer", "--substage", "red", "--objective",
                         "fixture B")
    assert prep.returncode == 0, (
        f"PC-05 fixture: prepare B: {prep.stdout!r} {prep.stderr!r}")


def _close_b(fx: _RecoveryProject) -> None:
    rel = f"docs/closures/{FEATURE_B}-closure.md"
    path = fx.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Fixture closure for unit B\n", encoding="utf-8")
    close = fx.run_packet(
        "register-transition", "--project-root", str(fx.root),
        "--transition", "closure", "--stage", "merge",
        "--approve-by", "Demo Approver", "--closure-path", rel)
    assert close.returncode == 0, (
        f"PC-05 fixture: cierre B: {close.stdout!r} {close.stderr!r}")


def _suspend_b(fx: _RecoveryProject) -> None:
    proc = _suspend(fx, feature_id=FEATURE_B)
    assert proc.returncode == 0, (
        f"PC-05 fixture: suspender B: {proc.stdout!r} {proc.stderr!r}")


def _recovery_resume(fx: _RecoveryProject):
    return fx._run(CONTINUITY_CLI, [
        "resume", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()), "--json"])


def _receive_a(fx: _RecoveryProject) -> None:
    dispatched = fx.run_packet(
        "prepare", "--project-root", str(fx.root), "--record-dispatch",
        fx.packet_id, "--attempt-id", "attempt-demo-700-001", "--input",
        str(fx._observation), "--continuity-attempt", "1")
    assert dispatched.returncode == 0, (
        f"PC-05 fixture: despacho A: {dispatched.stdout!r} "
        f"{dispatched.stderr!r}")
    received = fx.run_result(
        "receive", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--packet", str(fx.packet_dir() / "PACKET.md"),
        "--request", str(fx.packet_dir() / "REQUEST.json"),
        "--descriptor", str(fx._stage_result()), "--continuity-attempt", "1")
    assert received.returncode == 0, (
        f"PC-05 fixture: recepción A: {received.stdout!r} "
        f"{received.stderr!r}")


# ---------------------------------------------------------------- PC-01


@pytest.mark.parametrize("prior", [REDISPATCH_ACTION, OTHER_ACTION, None,
                                   _ABSENT],
                         ids=["redispatch", "other-text", "null", "absent"])
def test_007_008_new_close_has_canonical_action(tmp_path: Path,
                                                prior: object) -> None:
    """PC-01 (+AJ1): todo cierre nuevo por CLI lleva exactamente el literal
    de §3.2, independiente de la acción previa (texto, null o ausente)."""
    fx = _Project(tmp_path)
    assert_rc0(_begin_with_action(fx, prior), "PC-01", "`begin`")
    _, _, close_body = _received_close(fx, "PC-01")
    assert "next_action" in close_body, (
        "PC-01: el cuerpo durable del cierre declara `next_action`")
    assert close_body["next_action"] == CANONICAL_ACTION, (
        "PC-01: el cierre nuevo debe llevar la acción canónica de §3.2 "
        f"(no heredar la previa {prior!r}); visto "
        f"{close_body['next_action']!r}")


# ---------------------------------------------------------------- PC-02
# AJ4: declarado aquí de forma independiente (no se importa del productor).
RECEIPT_DECISION = {
    "decision": "recepción mecánica del recibo durable (checkpoint-receipt)",
    "rationale": (
        "el recibo existe y valida contra su payload durable: se registra la "
        "recepción MECÁNICA del efecto — no es aprobación semántica, no "
        "materializa, no dispone y no repite transporte ni recepción (§2.3)"),
}



def test_007_008_new_close_preserves_context_and_link(tmp_path: Path) -> None:
    """PC-02: el cierre nuevo sólo cambia `next_action`: conserva contexto,
    agrega una única decisión mecánica, enlaza la cabeza anterior y no
    reescribe cuerpos previos."""
    fx = _Project(tmp_path)
    assert_rc0(fx.begin(attempt=1, next_action=REDISPATCH_ACTION), "PC-02",
               "`begin`")
    bodies_before = fx.continuity_files()
    head_before, body_before, close_body = _received_close(fx, "PC-02")
    head_after = fx.head("PC-02")

    expected = {key: body_before.get(key, "<ausente>") for key in PRESERVED_KEYS}
    observed = {key: close_body.get(key, "<ausente>") for key in PRESERVED_KEYS}
    assert observed == expected, (
        "PC-02/§3.3: el cierre conserva valores y ausencias del contexto")
    assert close_body.get("record") == "checkpoint", (
        "PC-02/§3.3: el cierre conserva `record=checkpoint`")
    prior_decisions = body_before.get("decisions")
    decisions = close_body.get("decisions")
    assert decisions[:len(prior_decisions)] == prior_decisions, (
        "PC-02: las decisiones previas se conservan en orden")
    assert len(decisions) == len(prior_decisions) + 1, (
        "PC-02: se incorpora exactamente UNA decisión mecánica de recepción")
    assert list(decisions[-1].items()) == list(RECEIPT_DECISION.items()), (
        "PC-02/AJ4: la decisión incorporada es exactamente la decisión "
        f"mecánica contractual (valor y orden de claves): {decisions[-1]!r}")
    fx.assert_new_link_coherent(head_before, head_after, close_body, "PC-02")
    marker = close_body.get("receipt_checkpoint")
    assert marker.get("sha256") == sha256_bytes(fx.receipt_bytes()), (
        "PC-02: `receipt_checkpoint.sha256` es el SHA-256 del recibo durable")
    after = fx.continuity_files()
    assert {k: after.get(k) for k in bodies_before if "bodies/" in k} == {
        k: v for k, v in bodies_before.items() if "bodies/" in k}, (
        "PC-02: los cuerpos anteriores no cambian de bytes")
    assert close_body.get("next_action") == CANONICAL_ACTION, (
        "PC-02/§3.3: el único cambio funcional es la acción canónica; visto "
        f"{close_body.get('next_action')!r}")


# ---------------------------------------------------------------- PC-03


@pytest.mark.parametrize(
    "entry",
    [_entry_ordinary, _entry_external, _entry_recovery,
     _entry_recovery_after_transition],
    ids=["ordinary-receive", "external-validate", "checkpoint-receipt",
         "checkpoint-receipt-after-transition"])
def test_007_008_entries_converge_without_approval(tmp_path: Path,
                                                   entry) -> None:
    """PC-03: recepción ordinaria, recibo externo y recuperación producen el
    cierre con la misma regla de acción y preservación, sin aprobación y sin
    volver a recibir."""
    fx = _Project(tmp_path)
    snapshots: list[dict[str, object]] = []
    attempt = entry(fx, lambda f: snapshots.append(_durable_snapshot(f)))
    _, close_body = fx.assert_close(attempt, "PC-03")
    if entry is not _entry_ordinary:
        assert len(snapshots) == 1, "PC-03 fixture: snapshot previo tomado"
        assert _durable_snapshot(fx) == snapshots[0], (
            f"PC-03 [{entry.__name__}]: la entrada de cierre de un recibo ya "
            "durable no altera los bytes del recibo ni del payload (parts)")
    prev_sha = close_body["prev"]["checkpoint_sha256"]
    prev_body = fx.body(prev_sha, "PC-03 cabeza previa")
    assert fx.receipt().get("semantic_status") == "pending", (
        "PC-03: el recibo conserva `semantic_status=pending`")
    assert close_body.get("goal") == prev_body.get("goal"), (
        "PC-03: el cierre conserva el objetivo del contexto que cierra")
    assert close_body.get("decisions")[:-1] == prev_body.get("decisions"), (
        "PC-03: decisiones previas + una mecánica, en todas las entradas")
    assert close_body["receipt_checkpoint"]["sha256"] == sha256_bytes(
        fx.receipt_bytes()), (
        "PC-03: el recibo conserva los bytes que el cierre acredita")
    assert len(fx.parts_files()) == 1, (
        "PC-03: el recibo durable no se vuelve a recibir (una sola part)")
    assert close_body.get("next_action") == CANONICAL_ACTION, (
        f"PC-03 [{entry.__name__}]: la entrada converge en la acción "
        f"canónica; visto {close_body.get('next_action')!r}")


# ---------------------------------------------------------------- PC-04


@pytest.mark.parametrize(
    "variant", [_replay_immediate, _replay_after_links, _replay_obsolete],
    ids=["immediate", "historical-after-links", "historical-obsolete"])
def test_007_008_replay_preserves_history(tmp_path: Path, variant) -> None:
    """PC-04: el replay con igual identidad y recibo es no-op byte a byte,
    incluido un cierre histórico con acción obsoleta (no se migra)."""
    fx = _Project(tmp_path)
    assert_rc0(fx.begin(attempt=1, next_action=REDISPATCH_ACTION), "PC-04",
               "`begin`")
    _received_close(fx, "PC-04")
    expected_action = variant(fx)
    continuity_before = fx.continuity_files()
    receipt_before = fx.receipt_bytes()
    head_before = fx.head("PC-04")
    closes_before = len(fx.close_links(1))

    close_sha = fx.close(1, "PC-04")[0]
    replay = json_doc(fx.checkpoint_receipt(attempt=1), "PC-04",
                      "el replay del cierre")
    assert replay.get("no_op") is True, (
        f"PC-04: el replay reconoce no operación; visto {replay.get('no_op')!r}")
    identity = tuple(replay.get(k) for k in ("execution_id", "packet_id",
                                             "attempt", "body_sha256"))
    assert identity == (fx.execution_id, fx.packet_id, 1, close_sha), (
        "PC-04: el replay devuelve el cierre existente (clave y digest); "
        f"visto {identity!r}")
    assert fx.continuity_files() == continuity_before, (
        "PC-04: el replay no escribe cabeza ni cuerpos")
    assert fx.receipt_bytes() == receipt_before, (
        "PC-04: el replay mantiene el recibo byte a byte")
    assert fx.head("PC-04") == head_before, (
        "PC-04: digest y secuencia de la cabeza se conservan")
    assert len(fx.close_links(1)) == closes_before, (
        "PC-04: la cantidad de cierres no cambia")
    observed = fx.close(1, "PC-04")[1].get("next_action")
    assert observed == expected_action, (
        "PC-04: el cierre reconocido conserva su acción (nuevo: canónica; "
        f"histórico: la obsoleta, sin migrar); esperado {expected_action!r}, "
        f"visto {observed!r}")


def test_007_008_conflicting_valid_receipt_is_rejected(tmp_path: Path) -> None:
    """PC-04 (AJ3b): misma clave con un recibo ALTERNATIVO VÁLIDO de contenido
    distinto se rechaza sin escritura ni segundo cierre."""
    fx = _Project(tmp_path / "a")
    alt = _Project(tmp_path / "b")
    assert_rc0(fx.begin(attempt=1), "PC-04 conflicto", "`begin`")
    _received_close(fx, "PC-04 conflicto")
    assert_rc0(alt.begin(attempt=1), "PC-04 alternativo", "`begin`")
    alt.mark_dispatched()
    assert_rc0(alt.receive(n=1, part_content=b"# alternative report\n"),
               "PC-04 alternativo", "`receive` del recibo alternativo")
    assert (alt.execution_id, alt.packet_id) == (fx.execution_id,
                                                 fx.packet_id), (
        "PC-04 fixture: el recibo alternativo comparte la clave")
    assert alt.receipt_bytes() != fx.receipt_bytes(), (
        "PC-04 fixture: el recibo alternativo tiene contenido distinto")
    # El recibo alternativo (con sus parts) ocupa la ruta declarada de la
    # misma clave: es VÁLIDO (validate-receipt rc=0) y de contenido distinto.
    shutil.rmtree(fx.receipt_dir())
    shutil.copytree(alt.receipt_dir(), fx.receipt_dir())
    assert_rc0(fx.validate_receipt(), "PC-04 fixture",
               "el recibo alternativo valida (no es un recibo corrupto)")
    continuity_before = fx.continuity_files()

    proc = fx.checkpoint_receipt(attempt=1)
    assert_rejected(proc, "PC-04 conflicto",
                    "el cierre con un recibo alternativo de la misma clave")
    assert fx.continuity_files() == continuity_before, (
        "PC-04: el conflicto no escribe continuidad")
    assert len(fx.close_links(1)) == 1, (
        "PC-04: el conflicto no crea un segundo cierre")
    assert fx.close(1, "PC-04 conflicto")[1].get("next_action") == \
        CANONICAL_ACTION, (
        "PC-04: el cierre conservado es el cierre nuevo con acción canónica")


# ---------------------------------------------------------------- PC-05


@pytest.mark.parametrize("other", [_close_b, _suspend_b],
                         ids=["close-B", "suspend-B"])
def test_007_008_resume_unit_restores_canonical_action(tmp_path: Path,
                                                       other) -> None:
    """PC-05 (AJ3a): tras cierre nuevo de A, suspender A, trabajar en B y
    reanudar A restaura la acción canónica INMEDIATAMENTE después de
    `resume-unit`, sin repetir despacho ni recepción."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _begin(fx, "begin A", next_action=REDISPATCH_ACTION).returncode == 0, (
        "PC-05 fixture: begin A")
    _receive_a(fx)
    receipt_before = fx.receipt_path().read_bytes()
    dispatches_before = fx.dispatch_files()
    suspended = _suspend(fx)
    assert suspended.returncode == 0, (
        f"PC-05 fixture: suspender A: {suspended.stdout!r} "
        f"{suspended.stderr!r}")
    _open_b(fx)
    other(fx)
    resumed = _resume_cli(fx, "--feature", FEATURE_ID)
    assert resumed.returncode == 0, (
        f"PC-05: reanudar A: {resumed.stdout!r} {resumed.stderr!r}")

    projection = json_doc(_recovery_resume(fx), "PC-05",
                          "`resume` tras `resume-unit`")["projection"]
    assert fx.receipt_path().read_bytes() == receipt_before, (
        "PC-05: el recibo original permanece byte-idéntico")
    assert fx.dispatch_files() == dispatches_before, (
        "PC-05: no aparece otro despacho del intento recibido")
    assert projection.get("next_action") == CANONICAL_ACTION, (
        "PC-05: reanudar A restaura la acción canónica del cierre; visto "
        f"{projection.get('next_action')!r}")


def test_007_008_resume_unit_keeps_unreceived_action(tmp_path: Path) -> None:
    """PC-05: no cambia la restauración de contextos todavía no recibidos."""
    fx = _RecoveryProject(tmp_path)
    _assert_suspend_cli(fx)
    assert _begin(fx, "begin A", next_action=OTHER_ACTION).returncode == 0, (
        "PC-05 fixture: begin A")
    assert _suspend(fx).returncode == 0, "PC-05 fixture: suspender A"
    resumed = _resume_cli(fx, "--feature", FEATURE_ID)
    assert resumed.returncode == 0, (
        f"PC-05: reanudar A: {resumed.stdout!r} {resumed.stderr!r}")
    projection = json_doc(_recovery_resume(fx), "PC-05 sin recibo",
                          "`resume` tras `resume-unit`")["projection"]
    assert projection.get("next_action") == OTHER_ACTION, (
        "PC-05: un contexto no recibido restaura su propia acción; visto "
        f"{projection.get('next_action')!r}")


# ---------------------------------------------------------------- PC-06


def test_007_008_reads_are_coherent_without_approval(tmp_path: Path) -> None:
    """PC-06: tras un cierre nuevo, `resume` proyecta la acción canónica,
    `reconcile` informa `received` sin repetir efecto, el recibo sigue
    pendiente, las lecturas no escriben y `status` conserva su forma."""
    fx = _Project(tmp_path)
    assert_rc0(fx.begin(attempt=1, next_action=REDISPATCH_ACTION), "PC-06",
               "`begin`")
    fx.mark_dispatched()
    status_before = json_doc(_status(fx), "PC-06", "`status` previo")
    assert_rc0(fx.receive(n=1), "PC-06", "`receive`")
    tree_before = fx.tree()

    reconcile = json_doc(_reconcile(fx), "PC-06", "`reconcile`")
    status_after = json_doc(_status(fx), "PC-06", "`status` posterior")
    projection = json_doc(fx.resume(), "PC-06", "`resume`")["projection"]
    assert reconcile.get("classification") == "received", (
        f"PC-06: `reconcile` informa received: {reconcile!r}")
    assert reconcile.get("repeat_effect") is False, (
        "PC-06: `reconcile` no ofrece repetir el efecto")
    assert fx.receipt().get("semantic_status") == "pending", (
        "PC-06: el recibo sigue con `semantic_status=pending`")
    assert fx.tree() == tree_before, (
        "PC-06: las lecturas no agregan aprobación, disposición ni "
        "materialización")
    assert sorted(status_after) == sorted(status_before), (
        "PC-06: `status` conserva su forma contractual")
    assert projection.get("next_action") == CANONICAL_ACTION, (
        "PC-06: `resume.projection.next_action` es exactamente la acción "
        f"canónica; visto {projection.get('next_action')!r}")
