#!/usr/bin/env python3
"""RED 008-004 — exigencia de paquete verificable en las fronteras CDAD.

Contract:
- docs/specs/008-004-role-packet-enforcement/spec.md (PC-01, PC-03, PC-06,
  PC-07; §Referencias y nuevo begin; §Orden y efectos; §Errores).

Oráculo caja negra: CLIs públicos sobre proyectos descartables. Dos
constructores de pruebas ya aprobados preparan el proyecto por CLI:
- `_RecoveryProject` (007-002): paquete test-writer/red publicado con
  `prepare`; fronteras `prepare --record-dispatch`, `receive`, `begin`.
- `_Project` + `_Stage` (007-003): frontera de transporte
  `cdad_dispatch.py dispatch` con runtime de fixture que registra cada
  invocación (sin lanzar nada real).
Ningún módulo de producto se importa; ningún archivo de implementación se lee.

Cobertura (un bloque por postcondición; cada test declara su "sin este test"):

- PC-06: `begin` con referencia contract cubierta por write_scope se rechaza
  antes de persistir; controles (contract fuera de scope, living dentro)
  siguen aceptados.
- PC-03: un PACKET.md alterado (objetivo o línea de instrucciones), con
  encabezado JSON válido, no se acredita: no se registra el despacho, no se
  lanza el worker (`cdad_dispatch.py dispatch`) y no se recibe la entrega.
  Control: con el paquete intacto el worker se lanza una vez.
- PC-01: sin paquete verificable (PACKET.md ausente, sin marcador o con
  bloque sin cierre) la frontera rechaza sin publicar begin, despacho ni
  lanzamiento.
- PC-07: el rechazo no altera registros durables previos; un begin idéntico
  repetido y una recepción repetida siguen siendo replays sin efectos nuevos.

Rechazo de la frontera de transporte: el spec (§Errores) conserva la
semántica de cli-delegation.md; un rechazo válido es rc≠0 con diagnóstico, o
rc=0 con envoltura `termination=blocked`, `delivery=none`, `delivery_ref=null`.
Ambas formas se aceptan.

Frontera de registro: `prepare --record-dispatch` es el registro I8 de
`cdad_packet` (CLI directamente invocable). No figura en la superficie
técnica del spec: implementer y reviewer deben saber que obliga a tocar ese
CLI, no solo `cdad_dispatch`.

No cubierto por esta batería (declarado):
- PC-02, PC-04, PC-05, PC-08: se acreditan por lectura de intake de roles y
  adaptadores; los cubre el reviewer, sin tests de texto aquí.

Pruebas durables de admisión (post-review, docs/specs/008-004-role-packet-
enforcement/review.md, hallazgos 1-3): se escribieron DESPUÉS de la corrección
(commit 41b90d6), así que nacen verdes; su valor es impedir la regresión.
Cada una tiene un control del mismo montaje para que el rechazo no sea
universal:
- `cdad_delegate.py` directo con PACKET.md alterado: rc≠0 o envoltura
  `blocked`, cero invocaciones de worker; control intacto lanza una vez.
- `cdad_dispatch.py record` con PACKET.md alterado: sin sondeo `--observe`,
  sin worker, sin cambios en árbol ni estado; control intacto registra una
  entrada y sí produce sondeo `--observe` (prueba que el discriminador no es
  vacío). Límite declarado: el staging transitorio no es observable tras el
  hecho; se verifica la ausencia de residuos y de observación.
- `begin` con `REQUEST.json` ausente y PACKET.md publicado: rechazo sin
  efectos; control legacy (proyecto sin `.cdad/packets`, forma 003-007 T1)
  acepta `begin` y persiste la cabecera de continuidad.

Estado al RED (verificado por ejecución; ver el reporte del commit):
- Rojos por comportamiento (rc=0 o worker lanzado con el paquete alterado o
  sin verificar): PC-06 begin cubierto, PC-01 begin sin paquete, PC-03
  registro de despacho alterado, PC-03 y PC-01 dispatch que lanzan el worker,
  y PC-07(a) con la misma causa raíz que PC-06.
- Guardas verdes hoy: control PC-06, control PC-03 (paquete intacto lanza una
  vez), PC-03 receive alterado, PC-01 dispatch sin PACKET.md, replays PC-07.
  Los controles prueban que el montaje funciona; las guardas no son rojos.

RED (paquete): corre solo este archivo, en primer plano:
    env -u TMPDIR python3 -m pytest -q tests/test_008_004_packet_enforcement.py < /dev/null
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from test_003_007_t1_reference_classes import (
    HEAD_REL as LEGACY_HEAD_REL,
    POLICY_REL as LEGACY_POLICY_REL,
    STATE_REL as LEGACY_STATE_REL,
    exec_context_fixture,
    policy_fixture,
    state_doc_fixture,
    update_fixture,
)
from test_007_002_dispatch_recovery import (
    CLI_TIMEOUT_S,
    CONTINUITY_CLI,
    REPO_ROOT,
    _RecoveryProject,
    SPEC_BYTES,
    SPEC_REL,
)
from test_007_003_continuity_at_edges import (
    _Project as _DispatchProject,
    _Stage as _DispatchStage,
    _transport_accepted,
)

PACKET_END_LINE = "---end-cdad-packet-json"
INSTRUCTIONS_START = "<!-- cdad-instructions:start -->"
INSTRUCTIONS_END = "<!-- cdad-instructions:end -->"

ALTERED_SUFFIX = " (alterado en disco)"

# Con continuidad vigente el transporte exige el intento entero explícito
# (007-003 §2.2); el begin del fixture es el attempt 1.
CONTINUITY_ATTEMPT = ("--continuity-attempt", "1")

TEST_REL = "tests/exact_test_008.py"
TEST_BYTES = b"# fixture 008-004: referencia contract cubierta por write_scope\n"
LIVING_REL = "tests/nota-living-008.md"
LIVING_BYTES = b"nota living fixture 008-004 (dentro de write_scope)\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(root, rel: str, data: bytes) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _packet_md(fx):
    """PACKET.md publicado del paquete activo (ambos constructores)."""
    path = fx.root / ".cdad" / "packets" / fx.packet_id / "PACKET.md"
    assert path.is_file(), f"precondición (fixture): PACKET.md publicado en {path}"
    return path


def _objective_of(md) -> str:
    request = json.loads((md.parent / "REQUEST.json").read_text(encoding="utf-8"))
    return request["objective"]


def _assert_write_scope_cubre_tests(fx) -> None:
    """Precondición: el paquete test-writer publicado cubre `tests/`."""
    request = json.loads(
        (fx.root / ".cdad" / "packets" / fx.packet_id / "REQUEST.json")
        .read_text(encoding="utf-8"))
    scope = request.get("write_scope") or []
    assert any(sel.get("root") == "tests" for sel in scope), (
        f"precondición (fixture): el write_scope del paquete debe cubrir "
        f"tests/: {scope!r}")


def _begin(fx, references: list, *, attempt: int = 1,
           name: str = "begin-update.json"):
    """`begin` por el CLI público de continuidad, con referencias declaradas."""
    update = fx.base / name
    update.write_text(json.dumps({
        "packet_id": fx.packet_id,
        "attempt": attempt,
        "goal": "008-004 RED: begin con referencias",
        "decisions": [{"decision": "fixture decision",
                       "rationale": "fixture rationale"}],
        "uncertainties": [],
        "next_action": "continuar el encargo",
        "references": references,
    }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fx._run(CONTINUITY_CLI, [
        "begin", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--update", str(update), "--json",
    ])


# ----------------------------------------------- alteraciones de PACKET.md


def _alter_objective(md) -> None:
    """Altera una vez el objetivo; el encabezado JSON no cambia."""
    text = md.read_text(encoding="utf-8")
    objective = _objective_of(md)
    assert text.count(objective) == 1, (
        "precondición (fixture): el objetivo aparece una vez en PACKET.md")
    md.write_text(text.replace(objective, objective + ALTERED_SUFFIX),
                  encoding="utf-8")


def _alter_instruction_line(md) -> None:
    """Altera una línea única del bloque de instrucciones; el encabezado no cambia."""
    text = md.read_text(encoding="utf-8")
    block = text.split(INSTRUCTIONS_START, 1)[1].split(INSTRUCTIONS_END, 1)[0]
    candidates = [line for line in block.splitlines()
                  if len(line.strip()) >= 20 and text.count(line) == 1]
    assert candidates, (
        "precondición (fixture): hay una línea de instrucciones única en PACKET.md")
    line = candidates[0]
    md.write_text(text.replace(line, line + " (alterada)", 1), encoding="utf-8")


def _remove_packet_md(md) -> None:
    md.unlink()


def _replace_with_free_text(md) -> None:
    md.write_text("texto libre sin encomienda CDAD\n", encoding="utf-8")


def _drop_end_marker(md) -> None:
    lines = md.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if line.strip() != PACKET_END_LINE]
    assert len(kept) == len(lines) - 1, (
        "precondición (fixture): el marcador de cierre aparece una vez")
    md.write_text("".join(kept), encoding="utf-8")


def _assert_rechazo_limpio(proc, label: str) -> str:
    text = proc.stdout + proc.stderr
    assert proc.returncode != 0, (
        f"{label}: debe rechazarse (rc≠0); got rc={proc.returncode} "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert "Traceback" not in text, (
        f"{label}: el rechazo es diagnóstico, no un traceback: {text[:400]!r}")
    return text


def _receive(fx, descriptor):
    return fx.run_result(
        "receive", "--project-root", str(fx.root),
        "--execution-context", str(fx.execution_context_path()),
        "--packet", str(_packet_md(fx)),
        "--request", str(_packet_md(fx).parent / "REQUEST.json"),
        "--descriptor", str(descriptor),
    )


# ------------------------------------------------------------------ PC-06


def test_pc06_begin_con_contract_cubierta_por_write_scope_se_rechaza(tmp_path):
    """PC-06: un nuevo begin cuya referencia contract cae dentro del
    write_scope del paquete (`tests/`) se rechaza con diagnóstico antes de
    persistir.

    Sin este test, el usuario acabaría con un begin aceptado que solo falla
    después, al registrar (P1), con continuidad ya escrita: el store de la
    ejecución quedaría contaminado por una referencia que el propio paquete
    permite escribir.
    """
    fx = _RecoveryProject(tmp_path / "covered")
    _assert_write_scope_cubre_tests(fx)
    _write(fx.root, TEST_REL, TEST_BYTES)
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    proc = _begin(fx, [{"path": TEST_REL, "class": "contract",
                        "sha256": _sha(TEST_BYTES)}])

    text = _assert_rechazo_limpio(
        proc, "PC-06 (contract cubierta por write_scope)")
    assert TEST_REL in text, (
        f"PC-06: el diagnóstico nombra la referencia rechazada ({TEST_REL!r}); "
        f"got {text[:500]!r}")
    assert "scope" in text.lower(), (
        f"PC-06: el diagnóstico nombra el selector de write_scope incompatible; "
        f"got {text[:500]!r}")
    fx.assert_no_effects("PC-06 (rechazo antes de persistir)", before_tree,
                         before_state)


def test_pc06_controles_contract_fuera_de_scope_y_living_dentro_se_aceptan(tmp_path):
    """PC-06 (control): la regla no es un rechazo total. Un contract fuera de
    write_scope (la propia especificación) y una referencia living dentro de
    write_scope siguen siendo un begin válido.

    Sin este test, una implementación que rechace todo begin con referencias
    pasaría la PC-06 por accidente y el usuario perdería continuidad legítima.
    """
    fx = _RecoveryProject(tmp_path / "control")
    _assert_write_scope_cubre_tests(fx)
    _write(fx.root, LIVING_REL, LIVING_BYTES)

    proc = _begin(fx, [
        {"path": SPEC_REL, "class": "contract", "sha256": _sha(SPEC_BYTES)},
        {"path": LIVING_REL, "class": "living"},
    ])

    assert proc.returncode == 0, (
        "PC-06 (control): contract fuera de write_scope y living dentro se "
        f"aceptan; got rc={proc.returncode} stdout={proc.stdout!r} "
        f"stderr={proc.stderr!r}")


# ------------------------------------------------------------------ PC-01


@pytest.mark.parametrize(
    "degrade",
    [_remove_packet_md, _replace_with_free_text, _drop_end_marker],
    ids=["sin-paquete", "sin-marcador", "bloque-sin-cierre"])
def test_pc01_begin_sin_paquete_verificable_no_publica_continuidad(tmp_path, degrade):
    """PC-01: un begin asociado a un paquete sin PACKET.md verificable (ausente,
    sin marcador o con bloque sin cierre) se rechaza con diagnóstico, sin
    publicar continuidad.

    Sin este test, un begin podría quedar publicado para una encomienda que
    nadie puede verificar, y el resume posterior reanudaría sobre ella.
    """
    fx = _RecoveryProject(tmp_path / degrade.__name__)
    degrade(_packet_md(fx))
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    proc = _begin(fx, [])

    _assert_rechazo_limpio(proc, f"PC-01 (begin, {degrade.__name__})")
    fx.assert_no_effects(f"PC-01 (begin, {degrade.__name__})", before_tree,
                         before_state)


# ------------------------------------------------------------------ PC-03


@pytest.mark.parametrize("alter", [_alter_objective, _alter_instruction_line],
                         ids=["objetivo", "linea-de-instrucciones"])
def test_pc03_registro_de_despacho_rechaza_packet_md_alterado(tmp_path, alter):
    """PC-03: un PACKET.md alterado en el objetivo o en una línea de
    instrucciones, con encabezado JSON válido, no se registra como despacho.

    Sin este test, el usuario podría despachar una encomienda cuyo texto
    recibido por la sesión difiere del paquete validado: el registro
    acreditaría bytes que nadie validó contra el render canónico.
    """
    fx = _RecoveryProject(tmp_path / alter.__name__)
    alter(_packet_md(fx))
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    proc = fx.dispatch()

    text = _assert_rechazo_limpio(
        proc, f"PC-03 (registro de despacho, {alter.__name__})")
    assert fx.packet_id in text, (
        f"PC-03: el diagnóstico identifica el paquete ({fx.packet_id!r}); "
        f"got {text[:500]!r}")
    fx.assert_no_effects(
        f"PC-03 (registro, {alter.__name__})", before_tree, before_state)


def test_pc03_receive_rechaza_packet_md_alterado_tras_despacho_valido(tmp_path):
    """PC-03: tras un registro de despacho válido, un PACKET.md alterado en
    el objetivo impide recibir la entrega: no hay recibo nuevo y el árbol
    queda igual.

    Sin este test, una entrega podría acreditarse contra un paquete que ya no
    es el validado, y el recibo quedaría ligado a bytes alterados.
    """
    fx = _RecoveryProject(tmp_path / "receive")
    dispatched = fx.dispatch()
    assert dispatched.returncode == 0, (
        "precondición (fixture): el registro de despacho del paquete intacto "
        f"debe funcionar: {dispatched.stdout!r} {dispatched.stderr!r}")
    _alter_objective(_packet_md(fx))
    descriptor = fx._stage_result()
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    proc = _receive(fx, descriptor)

    _assert_rechazo_limpio(proc, "PC-03 (receive con PACKET.md alterado)")
    assert not fx.receipt_path().exists(), (
        "PC-03: no se publica recibo nuevo para un paquete alterado")
    fx.assert_no_effects("PC-03 (receive)", before_tree, before_state)


# -------------------------- PC-03 / PC-01 frontera de transporte (dispatch)


def _dispatch_fixture(tmp_path):
    """Proyecto con `begin` vigente (el transporte lo exige) y runtime de
    fixture: nada real se lanza; cada invocación queda registrada."""
    fx = _DispatchProject(tmp_path / "dispatch-proj")
    stage = _DispatchStage(tmp_path / "dispatch-stage")
    began = fx.begin()
    assert began.returncode == 0, (
        "precondición (fixture): el begin vigente debe acreditarse: "
        f"{began.stdout!r} {began.stderr!r}")
    return fx, stage


def _dispatch_effects(fx) -> dict:
    return {
        "state": fx.state_bytes(),
        "dispatch": fx.dispatch_files(),
        "inbox": fx.inbox_files(),
        "continuity": fx.continuity_files(),
    }


def _assert_worker_no_lanzado(stage, proc, label: str) -> None:
    """El rechazo ocurre antes de la herramienta de transporte: con rc≠0 o con
    la envoltura de bloqueo (rc=0, termination=blocked, delivery=none,
    delivery_ref=null) de cli-delegation.md."""
    calls = stage.transport_calls()
    assert calls == [], (
        f"{label}: el worker fue LANZADO pese al paquete no verificable "
        f"(invocaciones: {calls})")
    text = proc.stdout + proc.stderr
    assert "Traceback" not in text, (
        f"{label}: el rechazo es diagnóstico, no un traceback: {text[:400]!r}")
    if proc.returncode == 0:
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"{label}: rc=0 sin sobre JSON: {proc.stdout[:300]!r}") from exc
        assert (envelope.get("termination") == "blocked"
                and envelope.get("delivery") == "none"
                and envelope.get("delivery_ref") is None), (
            f"{label}: un rechazo con rc=0 es la envoltura de bloqueo "
            f"(termination=blocked, delivery=none, delivery_ref=null); "
            f"got {envelope!r}")
    else:
        assert text.strip(), f"{label}: rechazo sin diagnóstico observable"


def test_pc03_control_dispatch_con_paquete_intacto_lanza_worker_una_vez(tmp_path):
    """PC-03 (control): con el paquete intacto y el begin vigente, la frontera
    de transporte lanza el worker exactamente una vez y devuelve un sobre.

    Sin este test, un rechazo universal de la frontera pasaría los rechazos
    de PC-03 y el usuario no podría despachar nunca.
    """
    fx, stage = _dispatch_fixture(tmp_path)

    _transport_accepted(stage, fx, "PC-03 (control: paquete intacto)",
                        lambda: stage.dispatch(fx, *CONTINUITY_ATTEMPT))


@pytest.mark.parametrize("alter", [_alter_objective, _alter_instruction_line],
                         ids=["objetivo", "linea-de-instrucciones"])
def test_pc03_dispatch_rechaza_packet_md_alterado_antes_de_lanzar(tmp_path, alter):
    """PC-03: un PACKET.md alterado en el objetivo o en una línea de
    instrucciones, con encabezado JSON válido, se rechaza en la frontera de
    transporte ANTES de lanzar el worker, sin efectos.

    Sin este test, el worker recibiría un paquete distinto del validado y el
    usuario no sabría qué encomienda ejecutó la sesión.
    """
    fx, stage = _dispatch_fixture(tmp_path)
    alter(_packet_md(fx))
    before = _dispatch_effects(fx)
    stage.clear_calls()

    proc = stage.dispatch(fx, *CONTINUITY_ATTEMPT)

    _assert_worker_no_lanzado(stage, proc,
                              f"PC-03 (dispatch, {alter.__name__})")
    assert _dispatch_effects(fx) == before, (
        f"PC-03 (dispatch, {alter.__name__}): el rechazo no publica "
        "observación, entrega, staging ni cambio de estado")


@pytest.mark.parametrize(
    "degrade",
    [_remove_packet_md, _replace_with_free_text, _drop_end_marker],
    ids=["sin-paquete", "sin-marcador", "bloque-sin-cierre"])
def test_pc01_dispatch_sin_paquete_verificable_no_lanza_worker(tmp_path, degrade):
    """PC-01: un despacho sin PACKET.md verificable se rechaza en la frontera
    de transporte antes de lanzar el worker, sin efectos.

    Sin este test, una sesión podría ejecutar una encomienda sin paquete
    verificable: nadie podría demostrar después qué se le pidió.
    """
    fx, stage = _dispatch_fixture(tmp_path)
    degrade(_packet_md(fx))
    before = _dispatch_effects(fx)
    stage.clear_calls()

    proc = stage.dispatch(fx, *CONTINUITY_ATTEMPT)

    _assert_worker_no_lanzado(stage, proc, f"PC-01 (dispatch, {degrade.__name__})")
    assert _dispatch_effects(fx) == before, (
        f"PC-01 (dispatch, {degrade.__name__}): el rechazo no publica efectos")


# ------------------------------------------------------------------ PC-07


def test_pc07_rechazo_no_altera_registros_durables_previos(tmp_path):
    """PC-07: un begin rechazado (referencia contract cubierta, otro attempt)
    no modifica la cadena de continuidad ya persistida: head y bodies quedan
    byte a byte.

    Sin este test, un rechazo podría corromper o reescribir el registro
    durable de un begin válido anterior, y el usuario perdería la evidencia
    de lo que ya se acreditó.
    """
    fx = _RecoveryProject(tmp_path / "previos")
    _assert_write_scope_cubre_tests(fx)
    _write(fx.root, LIVING_REL, LIVING_BYTES)
    _write(fx.root, TEST_REL, TEST_BYTES)
    first = _begin(fx, [{"path": LIVING_REL, "class": "living"}], attempt=1,
                   name="begin-1.json")
    assert first.returncode == 0, (
        "precondición (fixture): el begin living válido se acredita: "
        f"{first.stdout!r} {first.stderr!r}")
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    rejected = _begin(fx, [{"path": TEST_REL, "class": "contract",
                            "sha256": _sha(TEST_BYTES)}],
                      attempt=2, name="begin-2.json")

    _assert_rechazo_limpio(rejected, "PC-07 (begin rechazado tras begin válido)")
    fx.assert_no_effects("PC-07 (preservación de registros)", before_tree,
                         before_state)


def test_pc07_begin_identico_repetido_es_replay_sin_efectos(tmp_path):
    """PC-07: repetir exactamente un begin válido es un replay: rc 0 y ningún
    eslabón, enlace ni recibo nuevo.

    Sin este test, un reintento del orquestador tras un fallo de transporte
    duplicaría continuidad y el usuario vería dos encargos donde hay uno.
    """
    fx = _RecoveryProject(tmp_path / "replay-begin")
    _write(fx.root, LIVING_REL, LIVING_BYTES)
    refs = [{"path": LIVING_REL, "class": "living"}]
    first = _begin(fx, refs, name="begin.json")
    assert first.returncode == 0, (
        "precondición (fixture): el begin válido se acredita: "
        f"{first.stdout!r} {first.stderr!r}")
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    replay = _begin(fx, refs, name="begin.json")

    assert replay.returncode == 0, (
        f"PC-07: el replay idéntico de begin se acepta (rc 0); got "
        f"rc={replay.returncode} stdout={replay.stdout!r} stderr={replay.stderr!r}")
    fx.assert_no_effects("PC-07 (replay de begin)", before_tree, before_state)


def test_pc07_recepcion_repetida_es_replay_sin_recibo_ni_enlace_nuevos(tmp_path):
    """PC-07: repetir la recepción de la misma entrega ya acreditada devuelve
    el replay y no crea recibo, enlace ni registro nuevos.

    Sin este test, un reintento de `receive` podría publicar un segundo
    recibo para la misma entrega y el usuario no sabría cuál es el válido.
    """
    fx = _RecoveryProject(tmp_path / "replay-receive")
    dispatched = fx.dispatch()
    assert dispatched.returncode == 0, (
        "precondición (fixture): el registro de despacho válido debe funcionar: "
        f"{dispatched.stdout!r} {dispatched.stderr!r}")
    first = _receive(fx, fx._stage_result())
    assert first.returncode == 0, (
        "precondición (fixture): la recepción válida se acredita: "
        f"{first.stdout!r} {first.stderr!r}")
    receipt_before = fx.receipt_path().read_bytes()
    descriptor = fx._stage_result()
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    replay = _receive(fx, descriptor)

    assert replay.returncode == 0, (
        f"PC-07: la repetición de la recepción es replay (rc 0); got "
        f"rc={replay.returncode} stdout={replay.stdout!r} stderr={replay.stderr!r}")
    assert fx.receipt_path().read_bytes() == receipt_before, (
        "PC-07: el recibo durable no cambia en la repetición")
    fx.assert_no_effects("PC-07 (replay de receive)", before_tree, before_state)


# ------------- admisión en delegate directo, record y begin sin REQUEST.json
# (pruebas durables del review 008-004: nacen verdes tras la corrección 41b90d6)


def _observation_calls(stage) -> list[dict]:
    """Sondeos `--observe` al runtime: la observación que `record` no debe
    hacer ante un paquete no verificable."""
    return [entry for entry in stage.calls()
            if "--observe" in (entry.get("argv") or [])]


@pytest.mark.parametrize("alter", [_alter_objective, _alter_instruction_line],
                         ids=["objetivo", "linea-de-instrucciones"])
def test_pc03_delegate_directo_rechaza_packet_md_alterado_antes_de_lanzar(
        tmp_path, alter):
    """PC-03: `cdad_delegate.py` invocado DIRECTAMENTE con un PACKET.md alterado
    en el objetivo o en una línea de instrucciones se rechaza antes de lanzar
    el worker, sin efectos.

    Sin este test, el usuario podría ver lanzado un worker con instrucciones
    distintas de las validadas, sin que ningún registro lo revele después: el
    delegate directo saltaría la admisión de `cdad_dispatch.py`.
    """
    fx, stage = _dispatch_fixture(tmp_path)
    alter(_packet_md(fx))
    before = _dispatch_effects(fx)
    stage.clear_calls()

    proc = stage.delegate(fx, *CONTINUITY_ATTEMPT)

    _assert_worker_no_lanzado(stage, proc,
                              f"PC-03 (delegate directo, {alter.__name__})")
    assert _dispatch_effects(fx) == before, (
        f"PC-03 (delegate directo, {alter.__name__}): el rechazo no publica "
        "observación, entrega, staging ni cambio de estado")


def test_pc03_delegate_directo_control_paquete_intacto_lanza_worker_una_vez(
        tmp_path):
    """PC-03 (control): `cdad_delegate.py` directo con el paquete intacto y el
    `begin` vigente lanza el worker exactamente una vez.

    Sin este test, un rechazo universal de la frontera directa pasaría el test
    anterior y el usuario no podría delegar nunca por esa vía.
    """
    fx, stage = _dispatch_fixture(tmp_path)

    _transport_accepted(stage, fx, "PC-03 (delegate directo, control)",
                        lambda: stage.delegate(fx, *CONTINUITY_ATTEMPT))


@pytest.mark.parametrize("alter", [_alter_objective, _alter_instruction_line],
                         ids=["objetivo", "linea-de-instrucciones"])
def test_pc03_record_rechaza_packet_md_alterado_sin_observar_ni_registrar(
        tmp_path, alter):
    """PC-03: `cdad_dispatch.py record` con un PACKET.md alterado se rechaza
    antes de observar al runtime y de registrar: sin sondeo `--observe`, sin
    worker, sin registro durable y con el árbol y el estado iguales.

    Sin este test, el usuario podría registrar una observación de sesión sobre
    un paquete cuyo texto no coincide con el validado, con el runtime ya
    consultado. El staging transitorio
    (`.observation.json`) no es observable después del hecho; aquí se verifica
    que no quede residuo ni registro.
    """
    fx, stage = _dispatch_fixture(tmp_path)
    alter(_packet_md(fx))
    before_tree = fx.tree()
    before_state = fx.state_bytes()
    stage.clear_calls()

    proc = stage.record(fx, *CONTINUITY_ATTEMPT)

    _assert_rechazo_limpio(proc, f"PC-03 (record, {alter.__name__})")
    assert _observation_calls(stage) == [], (
        f"PC-03 (record, {alter.__name__}): `record` observó al runtime pese al "
        f"paquete no verificable (sondeos: {_observation_calls(stage)})")
    assert stage.transport_calls() == [], (
        f"PC-03 (record, {alter.__name__}): `record` lanzó el worker")
    assert fx.dispatch_files() == [], (
        f"PC-03 (record, {alter.__name__}): hubo registro durable: "
        f"{fx.dispatch_files()}")
    assert fx.tree() == before_tree, (
        f"PC-03 (record, {alter.__name__}): el rechazo dejó escrituras o "
        "staging en el árbol del proyecto")
    assert fx.state_bytes() == before_state, (
        f"PC-03 (record, {alter.__name__}): el rechazo modificó el estado")


def test_pc03_record_control_paquete_intacto_registra_una_entrada(tmp_path):
    """PC-03 (control): con el paquete intacto y el `begin` vigente, `record`
    observa al runtime y publica exactamente un registro.

    Sin este test, un rechazo universal de `record` pasaría el test anterior y
    el usuario no podría registrar observaciones. El sondeo `--observe` debe
    verse aquí: si no aparece, la ausencia del test anterior no probaría nada.
    """
    fx, stage = _dispatch_fixture(tmp_path)
    stage.clear_calls()

    proc = stage.record(fx, *CONTINUITY_ATTEMPT)

    assert proc.returncode == 0, (
        "PC-03 (record, control): con el paquete intacto `record` acredita; "
        f"got rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert len(_observation_calls(stage)) >= 1, (
        "PC-03 (record, control): la observación debe pasar por el sondeo "
        f"`--observe` del runtime; calls={stage.calls()!r}")
    assert len(fx.dispatch_files()) == 1, (
        "PC-03 (record, control): con el paquete intacto se publica UN registro; "
        f"vistos {fx.dispatch_files()}")


def test_begin_con_request_ausente_y_rastro_de_publicacion_se_rechaza(tmp_path):
    """PC-01: un `begin` cuyo `REQUEST.json` falta, pero cuyo PACKET.md publicado
    permanece (rastro de publicación), se rechaza antes de persistir: la
    ausencia del request no cuenta como continuidad legacy.

    Sin este test, el usuario podría persistir un `begin` nuevo para una
    encomienda CDAD cuyo request se perdió, y el `resume` posterior reanudaría
    sobre una encomienda sin paquete verificable.
    """
    fx = _RecoveryProject(tmp_path / "request-ausente")
    packet_md = _packet_md(fx)
    request = packet_md.parent / "REQUEST.json"
    request.unlink()
    assert packet_md.is_file(), (
        "precondición (fixture): el rastro de publicación (PACKET.md) "
        "permanece sin REQUEST.json")
    before_tree = fx.tree()
    before_state = fx.state_bytes()

    proc = _begin(fx, [])

    _assert_rechazo_limpio(proc, "PC-01 (begin, REQUEST.json ausente)")
    fx.assert_no_effects("PC-01 (begin, REQUEST.json ausente)", before_tree,
                         before_state)


def test_begin_legado_sin_arbol_de_paquetes_se_acepta(tmp_path):
    """Control legacy: un proyecto sin árbol `.cdad/packets` (forma 003-007 T1:
    política, state y contexto de ejecución, sin paquete publicado) acepta
    `begin` con rc 0 y persiste la cabecera de continuidad.

    Sin este test, la admisión por paquete podría rechazar todo `begin` sin
    paquete publicado y el usuario perdería la continuidad de sus proyectos
    legados (003-004 y 003-007 intactos).
    """
    root = tmp_path / "legacy" / "proj"

    def write_json(rel: str, doc: dict) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    write_json(LEGACY_POLICY_REL, policy_fixture())
    write_json(LEGACY_STATE_REL, state_doc_fixture())
    exec_context = write_json("fixture/exec.json", exec_context_fixture())
    update = write_json("fixture/update.json",
                        update_fixture(references=[]))
    assert not (root / ".cdad" / "packets").exists(), (
        "precondición (fixture legado): no hay árbol .cdad/packets")
    env = dict(os.environ)
    env["HOME"] = str(tmp_path / "legacy" / "home")
    env["XDG_CONFIG_HOME"] = str(tmp_path / "legacy" / "config-home")
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    proc = subprocess.run(
        [sys.executable, str(CONTINUITY_CLI), "begin",
         "--project-root", str(root),
         "--execution-context", str(exec_context),
         "--update", str(update), "--json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)

    assert proc.returncode == 0, (
        "legado: sin árbol de paquetes, `begin` se acepta (rc 0); got "
        f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert (root / LEGACY_HEAD_REL).is_file(), (
        "legado: el `begin` aceptado persiste la cabecera de continuidad")
