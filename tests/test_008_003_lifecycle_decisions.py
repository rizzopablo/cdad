#!/usr/bin/env python3
"""RED 008-003 — decisor compartido de ciclo de vida (PC-01..PC-05).

Contract: `docs/specs/008-003-lifecycle-decision-model/spec.md` (aprobada;
sha256 3c2aa400fe7e1cec52b7412ef4c7c546bca09f61e1571cedc6eafbfd3df52031).
PC-06 es estructural y la acredita el reviewer; este módulo cubre sólo las
promesas behaviorales PC-01..PC-05 (§5).

Método (idéntico a los focales 007-003/007-004): caja negra sobre los CLI
públicos en proyectos sintéticos descartables; ningún módulo de producto se
importa ni se lee. Los fixtures y helpers se reutilizan por import de
`test_007_003_continuity_at_edges` (`_Project`, `_orphan_receipt`, snapshots,
`_Cases`) y `test_004_002_t2_bootstrap` (`build_project`); este módulo agrega
SOLO los constructores propios del decisor (proyecto sin paquete para el borde
`prepare`, mutaciones de identidad/autoridad y la unidad B).

Mapeo test → postcondición (una promesa observable por test, AJ6/R2):

  test_pc01_contradictory_identity_is_rejected_without_effects
      -> PC-01 (§4.2, §4.4): contradicción `execution.id`/`execution_id`,
         contexto/registro y contexto/registro de feature → rechazo
         diagnosticable y artefactos byte-idénticos; una repetición durable con
         un argumento contradictorio (`--contract-sha256`) tampoco publica.
  test_pc02_suspension_follows_the_accredited_owner
      -> PC-02 (§4.2, §4.3): la identidad suministrada (feature del contexto)
         no elude la suspensión del propietario real; omitir la identidad no
         convierte una ejecución gestionada en standalone; una unidad no
         suspendida sigue operando (open-unit, gate, prepare, begin) aunque A
         esté suspendida.
  test_pc03_authority_is_one_criterion_across_consumers
      -> PC-03 (§4.3): los mismos hechos de autoridad (revocada, fecha vencida,
         fecha estructurada inválida = desconocida) producen la misma decisión
         en C (`begin`), P (`prepare`) y R (`receive`), sin efectos; la lectura
         histórica (`resume`) y el replay acreditado (`checkpoint-receipt`)
         siguen disponibles.
  test_pc03_accredited_replay_precedes_eligibility
      -> PC-03 y §4.4 (GUARDA DE REGRESIÓN, no RED): una repetición íntegramente
         acreditada (checkpoint o recepción) tras revocar la autoridad o suspender
         la unidad retorna sin efectos; una variante divergente sigue sujeta a la
         elegibilidad y se rechaza sin efectos.
  test_pc04_replay_converges_after_the_active_state_advances
      -> PC-04 (§4.4): transición, escritura de continuidad y cierre
         reconocidos por evidencia existente retornan sin duplicar efectos
         aunque el estado activo haya avanzado; el conflicto sigue rechazándose;
         un recibo con cierre pendiente no acredita el cierre (agregarlo es un
         efecto nuevo).
  test_pc05_routes_and_legacy_history_are_conserved
      -> PC-05 (§4.5): la ruta normal exige unidad abierta + paquete despachado;
         la tardía conserva su excepción de destino cerrado y escribe un recibo
         `pending`; leer historia legacy (cuerpo sin `prev`, entrada sin clave)
         no recalcula claves ni altera bytes históricos.

Guardas de entrada directa (§3 «funciones invocables directamente», PC-06
«entradas programáticas»; GUARDA, no RED: pasan en el estado actual o es un
defecto real del fix). Cargan `cdad_continuity` en proceso, sólo para la
interfaz de `plan_write` y `close_durable_receipt`; cada una tiene un control
positivo previo, así un rechazo no puede deberse a una entrada inválida.

  test_pc01_direct_plan_write_rejects_contradictory_owner
      -> PC-01 (§4.2): `plan_write` con un contexto cuyo propietario contradice
         el estado → ContinuityError diagnosticable; artefactos byte-idénticos.
  test_pc02_direct_plan_write_respects_suspension
      -> PC-02 (§4.3): `plan_write` sobre la unidad suspendida → ContinuityError;
         artefactos byte-idénticos.
  test_pc02_direct_close_durable_receipt_respects_suspension
      -> PC-02 (§4.4): `close_durable_receipt` sobre un recibo cuya unidad está
         suspendida → ContinuityError; sin cierre publicado ni cadena tocada.

RED medido (HEAD d9810ea; sondas de CLI en tempdirs y luego esta misma
fixture). La causa declarada por caso es la observable hoy:

- PC-01: (a) `execution_id` plano discordante con `execution.id` → `checkpoint`
  rc=0 y escribe la continuidad; (b) contexto con `execution.id` ajeno al
  registro → rc=0 y escribe bajo `executions/<ajeno>/continuity/`; (c)
  contexto con `feature_id` ajeno al registro → rc=0 y escribe. Las tres
  contradicciones se aceptan con efectos (falla rc y falla el snapshot). La
  repetición durable con digest contradictorio ya rechaza (guarda).
- PC-02: con A suspendida, un `checkpoint` cuyo contexto declara la feature B
  → rc=0 y anexa enlace (seq 3); el mismo `checkpoint` con `feature_id`
  omitido en el contexto → rc=0 y anexa enlace. La unidad B no suspendida ya
  opera hoy con A suspendida (guarda de no-regresión).
- PC-03: con `expires_on: "2020-01-01"` (fecha vencida) C rechaza y P publica
  el paquete (rc=0): divergencia de criterio. Con `expires_on:
  "no-es-una-fecha"` (fecha estructurada inválida = desconocida) C, P y R
  aceptan y producen efectos (continuidad, paquete y recibo). Revocada ya
  rechaza en los tres bordes; `resume` y el replay del cierre ya siguen
  disponibles (guardas).
- PC-04: un `checkpoint` idéntico repetido después de un `begin` posterior
  → rc=0 con `no_op: false` y un enlace nuevo (seq 4): duplica la escritura.
  El replay del cierre de A con la unidad B activa → rc=2 (PD-24) en vez del
  no-op acreditado. El replay de transición (`gate`) y el conflicto de cierre
  ya convergen/rechazan hoy (guardas); el recibo con cierre pendiente agrega
  su enlace y su repetición no duplica (guarda).
- PC-05: guarda de conservación; hoy las dos rutas funcionan con sus
  precondiciones y la lectura legacy no reescribe bytes ni claves. No se le
  inventa un oráculo rojo.

Ningún fallo RED es ImportError, SyntaxError, JSONDecodeError ni error de
fixture: las precondiciones se asertan con mensaje propio.
"""
from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_007_003_continuity_at_edges import (
    _assert_receipt_state_unchanged,
    _Cases,
    _Project,
    _orphan_receipt,
    _snapshot_receipt_state,
    changed_paths,
    tree_snapshot,
)
from test_004_002_t2_bootstrap import build_project

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
CONTINUITY_CLI = (
    REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_continuity.py")
RESULT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"
SKILL_SCRIPTS = REPO_ROOT / "skills" / "cdad-cycle" / "scripts"

STATE_REL = "docs/.cdad-state.json"
APPROVER = "Demo Approver"
CLOSURE_REL = "docs/closures/demo-700-closure.md"
OTHER_FEATURE = "008-003-otra-unidad-fixture"
FOREIGN_EXECUTION = "exec-008-003-otra-unidad"
GATE_CONTRACT_REL = "docs/specs/demo-008-003-gate/spec.md"

# Hechos de autoridad estructurada (§4.3).
EXPIRED_ON = "2020-01-01"
INVALID_ON = "no-es-una-fecha"

# Diagnósticos: la causa observable que el rechazo debe nombrar.
IDENTITY_CAUSE = re.compile(
    r"(?i)identit|contradic|discord|mismatch|incoher|execution|ejecuci|feature")
REPLAY_ARGS_CAUSE = re.compile(
    r"(?i)digest|sha256|contract|contrato|evidenc|evidencia|assert")
SUSPENSION_CAUSE = re.compile(r"(?i)suspend|resume-unit")
OWNER_CAUSE = re.compile(
    r"(?i)owner|propiet|identit|contradic|discord|mismatch|incoher")
AUTHORITY_CAUSE = re.compile(
    r"(?i)authority|autoridad|delegation|delegaci|hitl|revoked|expired|"
    r"unknown|fecha|date|source|fuente")
CONFLICT_CAUSE = re.compile(
    r"(?i)already|registrad|no-op|conflict|conflicto|closure|cierre|"
    r"incoher|state")

CLI_TIMEOUT_S = 120


# ---------------------------------------------------------------- lectura


def output(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or "") + (proc.stderr or "")


def assert_rc0(proc: subprocess.CompletedProcess, label: str) -> None:
    text = output(proc)
    assert proc.returncode == 0, (
        f"precondición ({label}): debía completar (rc=0); "
        f"rc={proc.returncode}: {text[-900:]!r}")


def json_doc(proc: subprocess.CompletedProcess, label: str) -> dict:
    assert_rc0(proc, label)
    assert proc.stdout.strip(), f"{label}: no emitió un documento JSON"
    try:
        doc = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{label}: stdout no es JSON válido: {proc.stdout[:300]!r}") from exc
    assert isinstance(doc, dict), f"{label}: el documento no es un objeto: {doc!r}"
    return doc


def assert_rejected(proc: subprocess.CompletedProcess, label: str,
                    pattern: re.Pattern | None = None) -> str:
    text = output(proc)
    assert proc.returncode != 0, (
        f"{label}: la contradicción/falta de precondición debe rechazarse "
        f"(rc≠0); rc={proc.returncode}: {text[-900:]!r}")
    assert text.strip(), f"{label}: el rechazo debe ser diagnosticable"
    if pattern is not None:
        assert pattern.search(text), (
            f"{label}: el rechazo debe nombrar la causa "
            f"({pattern.pattern!r}); visto: {text[-900:]!r}")
    return text


def assert_rejected_without_effects(project, proc, before, label: str,
                                    pattern: re.Pattern | None = None) -> str:
    text = assert_rejected(proc, label, pattern)
    changed = changed_paths(before, project.tree())
    assert not changed, (
        f"{label}: el rechazo no debe modificar ningún artefacto; cambiaron: "
        f"{sorted(changed)}")
    return text


def read_state(project) -> dict:
    return json.loads((project.root / STATE_REL).read_text(encoding="utf-8"))


def write_state(project, state: dict) -> None:
    (project.root / STATE_REL).write_text(
        json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")


def entries(state: dict) -> list[dict]:
    history = state.get("stage_history") or []
    assert isinstance(history, list), (
        f"fixture: `stage_history` debe ser lista: {type(history).__name__}")
    return [entry for entry in history if isinstance(entry, dict)]


def set_delegation(project, **facts: object) -> None:
    """Muta el hecho de autoridad declarado por el estado del fixture."""
    state = read_state(project)
    delegation = dict(state.get("hitl_delegation") or {})
    delegation.update(facts)
    state["hitl_delegation"] = delegation
    write_state(project, state)


def gate(project, *, contract: str = GATE_CONTRACT_REL,
         stage: str = "specification",
         extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    return project.run(
        PACKET_CLI, "register-transition", "--project-root", str(project.root),
        "--transition", "gate", "--stage", stage, "--approve-by", APPROVER,
        "--contract-path", contract, *extra)


def closure(project, *, stage: str = "merge",
            closure_rel: str = CLOSURE_REL,
            feature: str | None = None) -> subprocess.CompletedProcess:
    cited = project.root / closure_rel
    if not cited.exists():
        cited.parent.mkdir(parents=True, exist_ok=True)
        cited.write_bytes(
            f"# Closure fixture (008-003) {closure_rel}\n".encode())
    args = [
        "register-transition", "--project-root", str(project.root),
        "--transition", "closure", "--stage", stage,
        "--approve-by", APPROVER, "--closure-path", closure_rel,
    ]
    if feature is not None:
        args += ["--feature", feature]
    return project.run(PACKET_CLI, *args)


def write_contract(project, feature: str) -> str:
    rel = f"docs/specs/{feature}/spec.md"
    path = project.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"# Approved fixture contract for {feature}\n".encode())
    return rel


def add_queued_unit(project, feature: str) -> None:
    state = read_state(project)
    state["epic_features"] = list(state.get("epic_features") or []) + [
        {"id": feature, "status": "queued"}]
    write_state(project, state)


def open_unit(project, feature: str) -> subprocess.CompletedProcess:
    return project.run(
        PACKET_CLI, "open-unit", "--project-root", str(project.root),
        "--feature", feature)


def begin_context(project, context: Path, packet_id: str, label: str
                  ) -> subprocess.CompletedProcess:
    update = project.base / f"update-{label}.json"
    update.write_text(json.dumps({
        "packet_id": packet_id,
        "attempt": 1,
        "goal": f"begin fixture {label}",
        "decisions": [],
        "uncertainties": [],
        "next_action": "continuar",
        "references": [],
    }, ensure_ascii=False), encoding="utf-8")
    return project.run(
        CONTINUITY_CLI, "begin", "--project-root", str(project.root),
        "--execution-context", str(context), "--update", str(update), "--json")


def suspend(project, feature: str) -> subprocess.CompletedProcess:
    return project.run(
        PACKET_CLI, "suspend-unit", "--project-root", str(project.root),
        "--feature", feature, "--reason", "pausa fixture 008-003")


class _BareProject:
    """Proyecto sintético SIN paquete preparado (borde `prepare` limpio).

    `build_project` (004-002) publica política, contrato aprobado, autoridad y
    el estado I2; el test muta sólo el hecho de autoridad y ejerce `prepare`
    como primera operación.
    """

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.config_home = base / "config-home"
        self.config_home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        build_project(self.root)

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)
        env["XDG_CONFIG_HOME"] = str(self.config_home)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def run(self, cli: Path, *args: str) -> subprocess.CompletedProcess:
        assert cli.is_file(), f"CLI del repo ausente: {cli}"
        return subprocess.run(
            [sys.executable, str(cli), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)

    def prepare(self) -> subprocess.CompletedProcess:
        return self.run(
            PACKET_CLI, "prepare", "--project-root", str(self.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "fixture 008-003 authority")

    def tree(self) -> dict[str, bytes | None]:
        return tree_snapshot(self.root)


# ================================================================ PC-01


def test_pc01_contradictory_identity_is_rejected_without_effects(
        tmp_path: Path) -> None:
    """PC-01 (+§4.2, §4.4): una contradicción entre fuentes aplicables
    (`execution.id` vs `execution_id` planos, contexto vs registro de
    ejecución, contexto vs registro de feature) y un argumento contradictorio
    en una repetición durable se rechazan sin modificar estado, continuidad,
    recibos ni artefactos administrados.

    Sin este test, el usuario puede ver su continuidad escrita bajo otra
    ejecución o su trabajo atribuido a otra unidad sin ningún error.
    """
    cases = _Cases()

    def flat_and_nested_execution_ids_disagree() -> None:
        fx = _Project(tmp_path / "id-plano")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        assert context["execution"]["id"] != FOREIGN_EXECUTION, (
            "fixture: el id ajeno debe ser distinto del real")
        context["execution_id"] = FOREIGN_EXECUTION
        fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
        before = fx.tree()
        proc = fx.checkpoint(attempt=1, label="identidad plana discordante")
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-01 (execution.id vs execution_id)", IDENTITY_CAUSE)

    def context_and_registry_execution_ids_disagree() -> None:
        fx = _Project(tmp_path / "id-contexto-registro")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        context["execution"]["id"] = FOREIGN_EXECUTION
        fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
        before = fx.tree()
        proc = fx.checkpoint(attempt=1, label="ejecución discordante")
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-01 (contexto vs registro de ejecución)", IDENTITY_CAUSE)
        assert not (fx.root / ".cdad/executions" / FOREIGN_EXECUTION).exists(), (
            "PC-01: la ejecución ajena no debe recibir continuidad")

    def context_and_registry_features_disagree() -> None:
        fx = _Project(tmp_path / "id-feature")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        assert context["execution"]["feature_id"] != OTHER_FEATURE
        context["execution"]["feature_id"] = OTHER_FEATURE
        fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
        before = fx.tree()
        proc = fx.checkpoint(attempt=1, label="feature discordante")
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-01 (contexto vs registro de feature)", IDENTITY_CAUSE)

    def durable_repetition_with_contradictory_arguments() -> None:
        fx = _Project(tmp_path / "repeticion-dura")
        assert_rc0(fx.begin(), "PC-01 repetición/begin")
        contract_rel = write_contract(fx, "demo-008-003-gate")
        assert_rc0(gate(fx, contract=contract_rel), "PC-01 repetición/gate")
        state = read_state(fx)
        gates_before = [e for e in entries(state) if e.get("transition") == "gate"]
        assert len(gates_before) == 1, (
            f"fixture PC-01: un gate registrado; hay {len(gates_before)}")
        before = fx.tree()
        proc = gate(fx, extra=("--contract-sha256", "0" * 64))
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-01 (repetición durable con argumento contradictorio)",
            REPLAY_ARGS_CAUSE)
        gates_after = [e for e in entries(read_state(fx))
                       if e.get("transition") == "gate"]
        assert len(gates_after) == 1, (
            "PC-01: la repetición contradictoria no agrega otra entrada; "
            f"hay {len(gates_after)}")

    for case in (flat_and_nested_execution_ids_disagree,
                 context_and_registry_execution_ids_disagree,
                 context_and_registry_features_disagree,
                 durable_repetition_with_contradictory_arguments):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-01")


# ================================================================ PC-02


def test_pc02_suspension_follows_the_accredited_owner(tmp_path: Path) -> None:
    """PC-02 (+§4.2, §4.3): una identidad suministrada que señala otra unidad
    no elude la suspensión del propietario real; omitir la identidad no
    reclasifica como standalone una ejecución gestionada; una unidad no
    suspendida conserva su operación aunque exista otra suspendida.

    Sin este test, el usuario puede seguir trabajando sobre una unidad que
    suspendió (o perder el trabajo de la unidad que sí puede operar).
    """
    cases = _Cases()

    def supplied_feature_of_another_unit() -> None:
        fx = _Project(tmp_path / "feature-ajena")
        assert_rc0(fx.begin(), "PC-02 begin A")
        assert_rc0(suspend(fx, fx.feature_id), "PC-02 suspender A")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        context["execution"]["feature_id"] = OTHER_FEATURE
        fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
        before = fx.tree()
        proc = fx.checkpoint(attempt=1, label="eludir suspensión")
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-02 (identidad suministrada de otra unidad)", SUSPENSION_CAUSE)

    def omitted_feature_does_not_become_standalone() -> None:
        fx = _Project(tmp_path / "identidad-omitida")
        assert_rc0(fx.begin(), "PC-02 begin A")
        assert_rc0(suspend(fx, fx.feature_id), "PC-02 suspender A")
        context = json.loads(fx.ctx.read_text(encoding="utf-8"))
        context["execution"].pop("feature_id", None)
        fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
        state = read_state(fx)
        assert state.get("suspended_units"), (
            "fixture PC-02: la evidencia gestionada conserva la suspensión")
        before = fx.tree()
        proc = fx.checkpoint(attempt=1, label="identidad omitida")
        assert_rejected_without_effects(
            fx, proc, before,
            "PC-02 (identidad omitida en contexto gestionado)", SUSPENSION_CAUSE)

    def other_unit_keeps_operating() -> None:
        fx = _Project(tmp_path / "unidad-b")
        assert_rc0(fx.begin(), "PC-02 begin A")
        assert_rc0(suspend(fx, fx.feature_id), "PC-02 suspender A")
        add_queued_unit(fx, OTHER_FEATURE)
        assert_rc0(open_unit(fx, OTHER_FEATURE), "PC-02 abrir B")
        contract_rel = write_contract(fx, OTHER_FEATURE)
        assert_rc0(gate(fx, contract=contract_rel), "PC-02 gate B")
        prepared = fx.run(
            PACKET_CLI, "prepare", "--project-root", str(fx.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "fixture unidad B")
        assert_rc0(prepared, "PC-02 prepare B")
        state = read_state(fx)
        assert state.get("active_feature") == OTHER_FEATURE
        assert fx.feature_id in (state.get("suspended_units") or {}), (
            "PC-02: A sigue registrada como suspendida")
        execution_id = (state.get("execution") or {}).get("id")
        packet_id = (state.get("active_packet") or {}).get("id")
        assert execution_id and packet_id, (
            f"fixture PC-02: ejecución y paquete de B: {state!r}")
        b_context = (fx.root / ".cdad" / "executions" / execution_id
                     / "execution.json")
        assert b_context.is_file(), (
            f"fixture PC-02: contexto de B publicado: {b_context}")
        assert_rc0(begin_context(fx, b_context, packet_id, "unidad-b"),
                   "PC-02 begin B")
        assert fx.feature_id in (read_state(fx).get("suspended_units") or {}), (
            "PC-02: operar B no reanuda ni borra la suspensión de A")

    for case in (supplied_feature_of_another_unit,
                 omitted_feature_does_not_become_standalone,
                 other_unit_keeps_operating):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-02")


# ================================================================ PC-03


def test_pc03_authority_is_one_criterion_across_consumers(tmp_path: Path) -> None:
    """PC-03 (+§4.3): para los mismos hechos de autoridad, C (`begin`), P
    (`prepare`) y R (`receive`) deciden igual; revocada, vencida, desconocida
    o incompatible no autoriza efectos gestionados, mientras la lectura
    histórica y el replay acreditado siguen disponibles.

    Sin este test, el usuario puede publicar paquetes o recibos con una
    autoridad vencida o desconocida que otro borde ya rechaza.
    """
    cases = _Cases()
    revoked = {"status": "revoked", "revoked_at": "2026-10-01T00:00:00Z"}

    def revoked_blocks_continuity() -> None:
        fx = _Project(tmp_path / "revocada-continuidad")
        set_delegation(fx, **revoked)
        before = fx.tree()
        proc = fx.begin()
        assert_rejected_without_effects(
            fx, proc, before, "PC-03 (revocada/C begin)", AUTHORITY_CAUSE)

    def revoked_blocks_packet() -> None:
        bare = _BareProject(tmp_path / "revocada-packet")
        set_delegation(bare, **revoked)
        before = bare.tree()
        proc = bare.prepare()
        assert_rejected_without_effects(
            bare, proc, before, "PC-03 (revocada/P prepare)", AUTHORITY_CAUSE)
        assert not (bare.root / ".cdad/packets").exists(), (
            "PC-03: la autoridad revocada no publica paquete")

    def revoked_blocks_result() -> None:
        fx = _Project(tmp_path / "revocada-result")
        assert_rc0(fx.begin(), "PC-03 revocada R begin")
        assert_rc0(fx.record_dispatch(), "PC-03 revocada R dispatch")
        fx.mark_dispatched()
        set_delegation(fx, **revoked)
        continuity_before = fx.continuity_files()
        state_before = fx.state_bytes()
        proc = fx.receive(n=1)
        assert_rejected(proc, "PC-03 (revocada/R receive)", AUTHORITY_CAUSE)
        assert not fx.receipt_path().exists(), (
            "PC-03: la autoridad revocada no publica recibo")
        assert fx.continuity_files() == continuity_before, (
            "PC-03: la autoridad revocada no escribe continuidad")
        assert fx.state_bytes() == state_before, (
            "PC-03: la autoridad revocada no escribe estado")

    def expired_date_blocks_continuity() -> None:
        # Guarda: hoy ya rechaza, y debe seguir rechazando.
        fx = _Project(tmp_path / "vencida-continuidad")
        set_delegation(fx, expires_on=EXPIRED_ON)
        before = fx.tree()
        proc = fx.begin()
        assert_rejected_without_effects(
            fx, proc, before, "PC-03 (vencida/C begin)", AUTHORITY_CAUSE)

    def expired_date_blocks_packet() -> None:
        # Mismo hecho que C; hoy P publica el paquete (RED).
        bare = _BareProject(tmp_path / "vencida-packet")
        set_delegation(bare, expires_on=EXPIRED_ON)
        before = bare.tree()
        proc = bare.prepare()
        assert_rejected_without_effects(
            bare, proc, before, "PC-03 (vencida/P prepare)", AUTHORITY_CAUSE)

    def invalid_date_blocks_continuity() -> None:
        # Una fecha estructurada inválida es `desconocida` (§4.3) y no
        # autoriza el efecto; hoy rc=0 y escribe (RED).
        fx = _Project(tmp_path / "invalida-continuidad")
        set_delegation(fx, expires_on=INVALID_ON)
        before = fx.tree()
        proc = fx.begin()
        assert_rejected_without_effects(
            fx, proc, before, "PC-03 (inválida/C begin)", AUTHORITY_CAUSE)

    def invalid_date_blocks_packet() -> None:
        # Mismo hecho que C; hoy rc=0 y publica (RED).
        bare = _BareProject(tmp_path / "invalida-packet")
        set_delegation(bare, expires_on=INVALID_ON)
        before = bare.tree()
        proc = bare.prepare()
        assert_rejected_without_effects(
            bare, proc, before, "PC-03 (inválida/P prepare)", AUTHORITY_CAUSE)

    def invalid_date_blocks_result() -> None:
        # Mismo hecho que C y P; hoy rc=0 y publica recibo (RED).
        fx = _Project(tmp_path / "invalida-result")
        assert_rc0(fx.begin(), "PC-03 inválida R begin")
        assert_rc0(fx.record_dispatch(), "PC-03 inválida R dispatch")
        fx.mark_dispatched()
        set_delegation(fx, expires_on=INVALID_ON)
        continuity_before = fx.continuity_files()
        state_before = fx.state_bytes()
        proc = fx.receive(n=1)
        assert_rejected(proc, "PC-03 (inválida/R receive)", AUTHORITY_CAUSE)
        assert not fx.receipt_path().exists(), (
            "PC-03: la autoridad desconocida no publica recibo")
        assert fx.continuity_files() == continuity_before, (
            "PC-03: la autoridad desconocida no escribe continuidad")
        assert fx.state_bytes() == state_before, (
            "PC-03: la autoridad desconocida no escribe estado")

    def historical_read_and_accredited_replay_remain_available() -> None:
        fx = _Project(tmp_path / "lectura-replay")
        assert_rc0(fx.begin(), "PC-03 lectura begin")
        assert_rc0(fx.record_dispatch(), "PC-03 lectura dispatch")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 lectura receive")
        set_delegation(fx, **revoked)
        resumed = fx.resume()
        assert_rc0(resumed, "PC-03 lectura resume")
        assert json.loads(resumed.stdout).get("projection"), (
            "PC-03: la lectura histórica sigue disponible con autoridad "
            "revocada")
        before = fx.continuity_files()
        replay = fx.checkpoint_receipt(attempt=1)
        doc = json_doc(replay, "PC-03 replay checkpoint-receipt")
        assert doc.get("no_op") is True, (
            "PC-03: el replay acreditado del cierre no publica otro cierre: "
            f"{doc!r}")
        assert fx.continuity_files() == before, (
            "PC-03: el replay acreditado no altera la cadena")

    for case in (revoked_blocks_continuity, revoked_blocks_packet,
                 revoked_blocks_result, expired_date_blocks_continuity,
                 expired_date_blocks_packet, invalid_date_blocks_continuity,
                 invalid_date_blocks_packet, invalid_date_blocks_result,
                 historical_read_and_accredited_replay_remain_available):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-03")


# ================================================= PC-03 / §4.4 (replay primero)


def test_pc03_accredited_replay_precedes_eligibility(tmp_path: Path) -> None:
    """Guarda de regresión (no RED) de PC-03 y §4.4: una repetición íntegramente
    acreditada (checkpoint o recepción) se reconoce ANTES de comprobar la
    autoridad o la suspensión y retorna sin efectos; una variante divergente
    sigue sujeta a la elegibilidad y se rechaza sin efectos.

    Sin este test, el usuario no puede reintentar una escritura o recepción ya
    registrada tras revocar la autoridad o suspender la unidad; y si la
    elegibilidad desapareciera del todo, la repetición y un efecto nuevo no
    serían distinguibles.
    """
    cases = _Cases()
    revoked = {"status": "revoked", "revoked_at": "2026-10-01T00:00:00Z"}

    def checkpoint_replay_after_revocation() -> None:
        fx = _Project(tmp_path / "replay-cp-revocada")
        assert_rc0(fx.begin(), "PC-03 replay cp revocada begin")
        assert_rc0(fx.checkpoint(attempt=1, label="checkpoint acreditado"),
                   "PC-03 replay cp revocada checkpoint")
        set_delegation(fx, **revoked)
        before = fx.tree()
        replay = fx.checkpoint(attempt=1, label="checkpoint acreditado")
        doc = json_doc(replay, "PC-03 replay cp tras revocación")
        assert doc.get("no_op") is True, (
            "PC-03/§4.4: la repetición acreditada tras revocación es replay "
            f"(`no_op: true`); visto {doc!r}")
        assert fx.tree() == before, (
            "PC-03/§4.4: el replay tras revocación no altera ningún artefacto; "
            f"cambiaron: {sorted(changed_paths(before, fx.tree()))}")
        before = fx.tree()
        divergent = fx.checkpoint(attempt=1, label="checkpoint divergente")
        assert_rejected_without_effects(
            fx, divergent, before,
            "PC-03/§4.4 (checkpoint divergente tras revocación)", AUTHORITY_CAUSE)

    def checkpoint_replay_after_suspension() -> None:
        fx = _Project(tmp_path / "replay-cp-suspendida")
        assert_rc0(fx.begin(), "PC-03 replay cp suspendida begin")
        assert_rc0(fx.checkpoint(attempt=1, label="checkpoint acreditado"),
                   "PC-03 replay cp suspendida checkpoint")
        assert_rc0(suspend(fx, fx.feature_id), "PC-03 replay cp suspender")
        before = fx.tree()
        replay = fx.checkpoint(attempt=1, label="checkpoint acreditado")
        doc = json_doc(replay, "PC-03 replay cp tras suspensión")
        assert doc.get("no_op") is True, (
            "PC-03/§4.4: la repetición acreditada tras suspensión es replay "
            f"(`no_op: true`); visto {doc!r}")
        assert fx.tree() == before, (
            "PC-03/§4.4: el replay tras suspensión no altera ningún artefacto; "
            f"cambiaron: {sorted(changed_paths(before, fx.tree()))}")
        before = fx.tree()
        divergent = fx.checkpoint(attempt=1, label="checkpoint divergente")
        assert_rejected_without_effects(
            fx, divergent, before,
            "PC-03/§4.4 (checkpoint divergente tras suspensión)",
            SUSPENSION_CAUSE)

    def receive_replay_after_revocation() -> None:
        fx = _Project(tmp_path / "replay-recepcion-revocada")
        assert_rc0(fx.begin(), "PC-03 replay recepción revocada begin")
        assert_rc0(fx.record_dispatch(), "PC-03 replay recepción revocada dispatch")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 replay recepción revocada receive")
        set_delegation(fx, **revoked)
        before = _snapshot_receipt_state(fx)
        assert_rc0(fx.receive(n=1), "PC-03 replay recepción tras revocación")
        _assert_receipt_state_unchanged(
            fx, before, "PC-03/§4.4 (recepción repetida tras revocación)")

    def receive_replay_after_suspension() -> None:
        fx = _Project(tmp_path / "replay-recepcion-suspendida")
        assert_rc0(fx.begin(), "PC-03 replay recepción suspendida begin")
        assert_rc0(fx.record_dispatch(),
                   "PC-03 replay recepción suspendida dispatch")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-03 replay recepción suspendida receive")
        assert_rc0(suspend(fx, fx.feature_id),
                   "PC-03 replay recepción suspender")
        before = _snapshot_receipt_state(fx)
        assert_rc0(fx.receive(n=1), "PC-03 replay recepción tras suspensión")
        _assert_receipt_state_unchanged(
            fx, before, "PC-03/§4.4 (recepción repetida tras suspensión)")

    for case in (checkpoint_replay_after_revocation,
                 checkpoint_replay_after_suspension,
                 receive_replay_after_revocation,
                 receive_replay_after_suspension):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-03 (§4.4 replay antes de elegibilidad)")


# ================================================================ PC-04


def test_pc04_replay_converges_after_the_active_state_advances(
        tmp_path: Path) -> None:
    """PC-04 (+§4.4): una transición, una escritura de continuidad y un cierre
    reconocidos como replay por su evidencia existente retornan sin duplicar
    efectos aunque el estado activo haya avanzado; los conflictos siguen
    rechazándose y un cierre pendiente no se presenta como ya realizado.

    Sin este test, el usuario puede duplicar enlaces de continuidad o cerrar
    la unidad equivocada al repetir una operación ya registrada.
    """
    cases = _Cases()

    def transition_replay_after_active_advance() -> None:
        fx = _Project(tmp_path / "replay-transicion")
        assert_rc0(fx.begin(), "PC-04 transición begin")
        contract_rel = write_contract(fx, "demo-008-003-gate")
        assert_rc0(gate(fx, contract=contract_rel), "PC-04 transición gate")
        assert_rc0(fx.begin(attempt=2, label="avance-transicion"),
                   "PC-04 transición avance")
        tree_before = fx.tree()
        state_before = fx.state_bytes()
        replay = gate(fx, contract=contract_rel)
        assert_rc0(replay, "PC-04 replay de transición")
        assert fx.state_bytes() == state_before, (
            "PC-04: el replay de la transición no agrega entradas ni reescribe "
            "el estado; cambiaron: "
            f"{sorted(changed_paths(tree_before, fx.tree()))}")
        gates = [e for e in entries(read_state(fx))
                 if e.get("transition") == "gate"]
        assert len(gates) == 1, (
            f"PC-04: una sola entrada del gate; hay {len(gates)}")

    def continuity_write_replay_after_active_advance() -> None:
        fx = _Project(tmp_path / "replay-continuidad")
        assert_rc0(fx.begin(), "PC-04 escritura begin")
        assert_rc0(fx.checkpoint(attempt=1, label="checkpoint fijo"),
                   "PC-04 escritura checkpoint")
        assert_rc0(fx.begin(attempt=2, label="avance-escritura"),
                   "PC-04 escritura avance")
        bodies_before = set(fx.bodies())
        continuity_before = fx.continuity_files()
        replay = fx.checkpoint(attempt=1, label="checkpoint fijo")
        doc = json_doc(replay, "PC-04 replay de escritura")
        assert doc.get("no_op") is True, (
            "PC-04: la escritura idéntica ya acreditada es replay (`no_op: "
            f"true`); visto {doc!r}")
        assert fx.continuity_files() == continuity_before, (
            "PC-04: el replay no agrega cuerpo, cabeza ni enlace; cambiaron: "
            f"{sorted(changed_paths(continuity_before, fx.continuity_files()))}")
        assert set(fx.bodies()) == bodies_before, (
            "PC-04: el replay no agrega un cuerpo nuevo; cuerpos: "
            f"{sorted(set(fx.bodies()) - bodies_before)}")

    def closure_replay_with_another_unit_active() -> None:
        fx = _Project(tmp_path / "replay-cierre")
        assert_rc0(fx.begin(), "PC-04 cierre begin")
        assert_rc0(fx.record_dispatch(), "PC-04 cierre dispatch")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-04 cierre receive")
        assert_rc0(closure(fx), "PC-04 cierre A")
        add_queued_unit(fx, OTHER_FEATURE)
        assert_rc0(open_unit(fx, OTHER_FEATURE), "PC-04 abrir B")
        state_before = fx.state_bytes()
        replay = closure(fx, feature=fx.feature_id)
        text = output(replay)
        assert replay.returncode == 0, (
            "PC-04 violada: el cierre ya registrado es un replay acreditado "
            "por su evidencia y no requiere unidad activa (§4.4); rc="
            f"{replay.returncode}: {text[-900:]!r}")
        assert fx.state_bytes() == state_before, (
            "PC-04: el replay del cierre no publica otra vez ni reescribe el "
            "estado")
        closed = [e for e in entries(read_state(fx))
                  if e.get("transition") == "closure"
                  and e.get("feature") == fx.feature_id]
        assert len(closed) == 1, (
            f"PC-04: un solo cierre de A; hay {len(closed)}")

    def conflict_is_still_rejected() -> None:
        fx = _Project(tmp_path / "conflicto")
        assert_rc0(fx.begin(), "PC-04 conflicto begin")
        assert_rc0(fx.record_dispatch(), "PC-04 conflicto dispatch")
        fx.mark_dispatched()
        assert_rc0(fx.receive(n=1), "PC-04 conflicto receive")
        assert_rc0(closure(fx), "PC-04 conflicto cierre")
        state_before = fx.state_bytes()
        proc = closure(fx, stage="feature-closure-alternativa")
        assert_rejected(proc, "PC-04 conflicto de cierre", CONFLICT_CAUSE)
        assert fx.state_bytes() == state_before, (
            "PC-04: el conflicto no escribe estado")
        closed = [e for e in entries(read_state(fx))
                  if e.get("transition") == "closure"]
        assert len(closed) == 1, (
            f"PC-04: el conflicto no agrega otro cierre; hay {len(closed)}")

    def pending_close_is_a_new_effect() -> None:
        fx = _Project(tmp_path / "cierre-pendiente")
        _orphan_receipt(fx, close_attempt=2)
        assert fx.receipt_path().is_file(), (
            "fixture PC-04: el recibo durable existe con el cierre pendiente")
        assert fx.close_links(2) == [], (
            "fixture PC-04: el cierre del intento 2 todavía no existe")
        before = fx.continuity_files()
        first = fx.checkpoint_receipt(attempt=2)
        assert_rc0(first, "PC-04 cierre pendiente: agregar")
        assert fx.continuity_files() != before, (
            "PC-04: agregar el cierre pendiente es un efecto NUEVO (agrega "
            "enlace), no un replay")
        assert len(fx.close_links(2)) == 1, (
            "PC-04: el cierre agregado es uno; hay "
            f"{len(fx.close_links(2))}")
        after = fx.continuity_files()
        replay = fx.checkpoint_receipt(attempt=2)
        doc = json_doc(replay, "PC-04 cierre pendiente: replay")
        assert doc.get("no_op") is True, (
            f"PC-04: repetir el cierre ya agregado es no-op; visto {doc!r}")
        assert fx.continuity_files() == after, (
            "PC-04: repetir el cierre no agrega otro enlace")

    for case in (transition_replay_after_active_advance,
                 continuity_write_replay_after_active_advance,
                 closure_replay_with_another_unit_active,
                 conflict_is_still_rejected,
                 pending_close_is_a_new_effect):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-04")


# ================================================================ PC-05


def test_pc05_routes_and_legacy_history_are_conserved(tmp_path: Path) -> None:
    """PC-05 (+§4.5): la recepción normal conserva la exigencia de unidad
    abierta y paquete despachado; la tardía conserva su excepción de destino
    cerrado y publica un recibo `pending`; leer y repetir historia legacy no
    recalcula claves ni altera bytes históricos.

    Sin este test, el usuario puede perder la recepción legítima o ver
    reescrita (y por tanto invalidada) su historia anterior.
    """
    cases = _Cases()

    def normal_route_keeps_its_preconditions() -> None:
        without = _Project(tmp_path / "normal-sin-despacho")
        assert_rc0(without.begin(), "PC-05 normal begin")
        proc = without.receive(n=1)
        assert_rejected(proc, "PC-05 normal sin despacho")
        assert not without.receipt_path().exists(), (
            "PC-05: sin despacho no hay recibo durable")

        ok = _Project(tmp_path / "normal-ok")
        assert_rc0(ok.begin(), "PC-05 normal-ok begin")
        assert_rc0(ok.record_dispatch(), "PC-05 normal-ok dispatch")
        assert_rc0(ok.receive(n=1), "PC-05 normal-ok receive")
        assert ok.receipt_path().is_file(), (
            "PC-05: la ruta normal publica el recibo durable")
        ok.assert_close(1, "PC-05 normal-ok")

    def late_route_keeps_its_exception() -> None:
        fx = _Project(tmp_path / "tardia")
        assert_rc0(fx.begin(), "PC-05 tardía begin")
        assert_rc0(fx.record_dispatch(), "PC-05 tardía dispatch")
        assert_rc0(fx.transition("disposition", resolution="abandoned",
                                 packet=fx.packet_id),
                   "PC-05 tardía disposición")
        assert_rc0(closure(fx), "PC-05 tardía cierre")
        state = read_state(fx)
        assert state.get("active_feature") is None, (
            "fixture PC-05: el destino queda cerrado")
        state_before = fx.state_bytes()
        proc = fx.receive(late=True, n=1,
                          part_content=b"# late role report (008-003)\n")
        assert_rc0(proc, "PC-05 tardía receive")
        assert fx.receipt_path().is_file(), (
            "PC-05: la ruta tardía publica el recibo durable")
        assert fx.receipt().get("semantic_status") == "pending", (
            "PC-05: el recibo tardío no aprueba ningún gate")
        assert fx.state_bytes() == state_before, (
            "PC-05: el recibo tardío no reabre ni reescribe el estado")
        assert (read_state(fx).get("active_feature")) is None, (
            "PC-05: la unidad cerrada sigue cerrada")

        missing = _Project(tmp_path / "tardia-sin-intento")
        assert_rc0(missing.begin(), "PC-05 tardía-sin-intento begin")
        assert_rc0(missing.record_dispatch(), "PC-05 tardía-sin-intento dispatch")
        assert_rc0(missing.transition("disposition", resolution="abandoned",
                                      packet=missing.packet_id),
                   "PC-05 tardía-sin-intento disposición")
        assert_rc0(closure(missing), "PC-05 tardía-sin-intento cierre")
        proc = missing.receive(late=True, with_flag=False)
        assert_rejected(proc, "PC-05 tardía sin intento")
        assert not missing.receipt_path().exists(), (
            "PC-05: la tardía sin intento no publica recibo")

    def legacy_history_is_read_without_recalculating_keys() -> None:
        fx = _Project(tmp_path / "legacy")
        assert_rc0(fx.begin(), "PC-05 legacy begin")
        # Una transición REAL con clave verificable convive con la historia
        # legacy: la lectura no debe recalcular ninguna de las dos.
        contract_rel = write_contract(fx, "demo-008-003-gate")
        assert_rc0(gate(fx, contract=contract_rel), "PC-05 legacy gate")
        head = fx.head("PC-05 legacy")
        body = fx.body(head["body_sha256"], "PC-05 legacy")
        body.pop("prev", None)  # cuerpo legado: sin enlace histórico
        legacy_sha = fx.write_body(body)
        fx.body_path(head["body_sha256"]).unlink()
        head["body_sha256"] = legacy_sha
        head["prev_checkpoint_sha256"] = None
        head["seq"] = 1
        fx.write_head(head)
        state = read_state(fx)
        state["stage_history"].append({
            "feature": fx.feature_id,
            "stage": "tdd",
            "transition": "gate",
            "approved_by": APPROVER,
            "at": "2025-01-01T00:00:00Z",
        })
        write_state(fx, state)
        before_tree = fx.tree()
        keys_before = [entry.get("transition_key")
                       for entry in entries(state)]
        assert any(key for key in keys_before), (
            "fixture PC-05: la historia mixta conserva al menos una clave real")
        assert None in keys_before, (
            "fixture PC-05: la entrada legacy no declara clave")
        assert_rc0(fx.resume(), "PC-05 legacy resume")
        assert_rc0(fx.run(PACKET_CLI, "status", "--project-root",
                          str(fx.root)), "PC-05 legacy status")
        assert_rc0(fx.run(PACKET_CLI, "validate-state", "--project-root",
                          str(fx.root)), "PC-05 legacy validate-state")
        rejected = fx.verify_begin(attempt=1)
        assert rejected.returncode != 0, (
            "PC-05: la historia no demostrable no acredita un `begin` vigente")
        assert fx.tree() == before_tree, (
            "PC-05: leer/repetir historia legacy no altera bytes históricos; "
            f"cambiaron: {sorted(changed_paths(before_tree, fx.tree()))}")
        keys_after = [entry.get("transition_key")
                      for entry in entries(read_state(fx))]
        assert keys_after == keys_before, (
            "PC-05: la lectura legacy no recalcula claves de transición; "
            f"antes {keys_before!r}, después {keys_after!r}")
        real_keys = [key for key in keys_after if key]
        assert real_keys and all(
            len(key) == 64 for key in real_keys), (
            f"PC-05: las claves reales se conservan íntegras: {real_keys!r}")

    for case in (normal_route_keeps_its_preconditions,
                 late_route_keeps_its_exception,
                 legacy_history_is_read_without_recalculating_keys):
        cases.run(case.__name__, case)
    cases.raise_if_any("PC-05")


# ================================================ guardas de entrada directa
#
# GUARDAS (no RED): `plan_write` y `close_durable_receipt` se invocan en
# proceso, como lo haría un consumidor programático. Cada rechazo se compara
# con un control positivo de la misma entrada sin la mutación.


def _continuity_module():
    """Carga `cdad_continuity` en proceso (interfaz directa del decisor).

    Import perezoso: un fallo de carga no impide colectar los tests CLI. No
    deja `__pycache__` bajo `skills/` (raíz de implementación).
    """
    scripts = str(SKILL_SCRIPTS)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        return importlib.import_module("cdad_continuity")
    finally:
        sys.dont_write_bytecode = previous


def _isolate_home(monkeypatch: pytest.MonkeyPatch, fx: _Project) -> None:
    """La llamada directa corre en el proceso de pytest: HOME y XDG se redirigen
    al proyecto descartable, como lo hace `_Project` en sus CLI."""
    monkeypatch.setenv("HOME", str(fx.home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(fx.config_home))


def _checkpoint_update(fx: _Project, label: str) -> dict:
    return {
        "packet_id": fx.packet_id,
        "attempt": 1,
        "goal": f"objetivo fixture 008-003 ({label})",
        "decisions": [{"decision": "decisión fixture",
                       "rationale": "razón fixture"}],
        "uncertainties": [],
        "next_action": "continuar el encargo",
        "references": [],
    }


def _expect_plan(mod, call, label: str) -> dict:
    """Control positivo: la entrada válida debe planear escrituras (dict)."""
    try:
        plan = call(mod)
    except mod.ContinuityError as exc:
        raise AssertionError(
            f"precondición ({label}): la entrada válida fue rechazada: {exc}"
        ) from exc
    except Exception as exc:
        raise AssertionError(
            f"precondición ({label}): fallo no contractual "
            f"{type(exc).__name__}: {exc}") from exc
    assert isinstance(plan, dict), (
        f"precondición ({label}): el plan debe ser un dict; "
        f"visto {type(plan).__name__}")
    return plan


def _expect_rejection(mod, call, label: str, pattern: re.Pattern) -> str:
    """La entrada contradictoria debe fallar con ContinuityError diagnosticable."""
    try:
        plan = call(mod)
    except mod.ContinuityError as exc:
        text = str(exc)
    except Exception as exc:
        raise AssertionError(
            f"{label}: debe fallar con ContinuityError; fue "
            f"{type(exc).__name__}: {exc}") from exc
    else:
        raise AssertionError(
            f"{label}: debía rechazarse con ContinuityError; devolvió un plan: "
            f"{str(plan)[:300]!r}")
    assert text.strip(), f"{label}: el rechazo debe ser diagnosticable"
    assert pattern.search(text), (
        f"{label}: el rechazo debe nombrar la causa ({pattern.pattern!r}); "
        f"visto: {text[-900:]!r}")
    return text


def test_pc01_direct_plan_write_rejects_contradictory_owner(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PC-01 (§4.2, §3): `plan_write` invocado directamente rechaza un contexto
    cuyo propietario contradice el estado, sin efectos. Es la entrada que el
    CLI no ejerce como función: sin este test, un consumidor programático podría
    planear una escritura de continuidad sobre una ejecución ajena.
    """
    fx = _Project(tmp_path / "plan-propietario")
    assert_rc0(fx.begin(), "PC-01 directo begin")
    _isolate_home(monkeypatch, fx)
    mod = _continuity_module()

    before = fx.tree()
    _expect_plan(
        mod,
        lambda m: m.plan_write(fx.root, fx.ctx,
                               _checkpoint_update(fx, "control")),
        "PC-01 directo control (contexto legítimo)")
    assert not changed_paths(before, fx.tree()), (
        "PC-01 directo: `plan_write` sólo planea; no debe publicar en el control")

    context = json.loads(fx.ctx.read_text(encoding="utf-8"))
    context["execution"]["feature_id"] = OTHER_FEATURE
    fx.ctx.write_text(json.dumps(context, indent=1), encoding="utf-8")
    before = fx.tree()
    _expect_rejection(
        mod,
        lambda m: m.plan_write(fx.root, fx.ctx,
                               _checkpoint_update(fx, "contradiccion")),
        "PC-01 plan_write directo (propietario contradictorio)", IDENTITY_CAUSE)
    changed = changed_paths(before, fx.tree())
    assert not changed, (
        "PC-01 plan_write directo: el rechazo no debe modificar artefactos; "
        f"cambiaron: {sorted(changed)}")


def test_pc02_direct_plan_write_respects_suspension(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PC-02 (§4.3, §3): `plan_write` invocado directamente no planea efectos
    nuevos sobre la unidad suspendida. Sin este test, una entrada programática
    podría escribir continuidad de una unidad que el usuario suspendió.
    """
    fx = _Project(tmp_path / "plan-suspendida")
    assert_rc0(fx.begin(), "PC-02 directo begin")
    _isolate_home(monkeypatch, fx)
    mod = _continuity_module()

    before = fx.tree()
    _expect_plan(
        mod,
        lambda m: m.plan_write(fx.root, fx.ctx,
                               _checkpoint_update(fx, "control")),
        "PC-02 directo control (unidad activa)")
    assert not changed_paths(before, fx.tree()), (
        "PC-02 directo: `plan_write` sólo planea; no debe publicar en el control")

    assert_rc0(suspend(fx, fx.feature_id), "PC-02 directo suspender A")
    assert fx.feature_id in (read_state(fx).get("suspended_units") or {}), (
        "fixture PC-02: la unidad A debe quedar registrada como suspendida")
    before = fx.tree()
    _expect_rejection(
        mod,
        lambda m: m.plan_write(fx.root, fx.ctx,
                               _checkpoint_update(fx, "suspendida")),
        "PC-02 plan_write directo (unidad suspendida)", SUSPENSION_CAUSE)
    changed = changed_paths(before, fx.tree())
    assert not changed, (
        "PC-02 plan_write directo: el rechazo no debe modificar artefactos; "
        f"cambiaron: {sorted(changed)}")


def _expect_accepted(mod, call, label: str):
    """Control positivo: la entrada válida debe ejecutarse sin ContinuityError."""
    try:
        return call(mod)
    except mod.ContinuityError as exc:
        raise AssertionError(
            f"precondición ({label}): la entrada válida fue rechazada: {exc}"
        ) from exc
    except Exception as exc:
        raise AssertionError(
            f"precondición ({label}): fallo no contractual "
            f"{type(exc).__name__}: {exc}") from exc


def _close_call_for(fx: _Project):
    def close_call(m):
        return m.close_durable_receipt(
            fx.root, fx.receipt_path(), 2,
            execution_context=fx.ctx, packet=fx.packet_id)
    return close_call


def test_pc02_direct_close_durable_receipt_respects_suspension(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PC-02 (§4.4, §3): `close_durable_receipt` invocado directamente publica el
    cierre común de un recibo de la unidad activa (lo agrega a la cadena) y, sobre
    la unidad suspendida, no publica cierre ni toca su cadena. Sin este test, un
    recibo de una unidad suspendida podría cerrarse sin que el usuario la haya
    reanudado.
    """
    # Control positivo (unidad activa): el cierre válido SÍ se publica.
    ctl = _Project(tmp_path / "cierre-activo")
    _orphan_receipt(ctl, close_attempt=2, label="PC-02 directo control")
    _isolate_home(monkeypatch, ctl)
    mod = _continuity_module()

    chain_before = ctl.chain("PC-02 directo control antes")
    bodies_before = set(ctl.bodies())
    _expect_accepted(mod, _close_call_for(ctl),
                     "PC-02 directo control (unidad activa)")
    chain_after = ctl.chain("PC-02 directo control después")
    close_sha, _ = ctl.close(2, "PC-02 directo control")
    assert chain_after[0][0] == close_sha, (
        "PC-02 directo control: el cierre publicado debe ser la nueva cabeza "
        f"de la cadena; cabeza {chain_after[0][0][:12]}…, cierre "
        f"{close_sha[:12]}…")
    assert len(chain_after) > len(chain_before), (
        "PC-02 directo control: el cierre válido debe agregar un enlace a la "
        f"cadena ({len(chain_before)} -> {len(chain_after)})")
    assert close_sha in set(ctl.bodies()) - bodies_before, (
        "PC-02 directo control: el cierre debe ser un cuerpo nuevo en la "
        "continuidad, no uno preexistente")

    # Mitad que importa (unidad suspendida): rechazo sin efectos.
    fx = _Project(tmp_path / "cierre-suspendido")
    _orphan_receipt(fx, close_attempt=2, label="PC-02 directo cierre")
    _isolate_home(monkeypatch, fx)

    assert_rc0(suspend(fx, fx.feature_id), "PC-02 directo suspender A")
    assert fx.feature_id in (read_state(fx).get("suspended_units") or {}), (
        "fixture PC-02: la unidad A debe quedar registrada como suspendida")
    before = fx.tree()
    _expect_rejection(
        mod, _close_call_for(fx),
        "PC-02 close_durable_receipt directo (unidad suspendida)",
        SUSPENSION_CAUSE)
    changed = changed_paths(before, fx.tree())
    assert not changed, (
        "PC-02 close_durable_receipt directo: el rechazo no debe publicar cierre "
        f"ni tocar la cadena; cambiaron: {sorted(changed)}")
    assert fx.close_links(2) == [], (
        "PC-02 close_durable_receipt directo: no debe existir cierre publicado")
