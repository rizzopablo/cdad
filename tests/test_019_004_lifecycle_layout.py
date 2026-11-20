#!/usr/bin/env python3
"""019-004 T2 RED — el layout seleccionado gobierna el ciclo de vida, la
continuación ligada a la ejecución y la compatibilidad de política.

Contract: docs/specs/019-004-project-layout-and-dispatch-intake/spec.md
(sha256 29f7c39b…b21be1), §4.4, §4.5, §5, PC-05..PC-09, más
docs/specs/019-004-project-layout-and-dispatch-intake/decisions.md
(locator que resuelve a la raíz del repositorio: no soportado, rechazado sin
escrituras).

Método: caja negra, solo subprocess sobre los CLI públicos
(`cdad_packet.py`, `cdad_result.py`); ningún fuente de producto se lee. Los
proyectos se construyen con las fixtures públicas ya existentes
(tests/test_005_012_t1_register_transition_base.py y
tests/test_019_002_resting_orientation.py) EN EL LAYOUT LEGADO y luego se
RELOCALIZAN por copia de sus artefactos de control (estado y política) a un
directorio registrado en `.cdad/project-layout.json`. El directorio
personalizado cuelga de `docs/` (clasificado como documentación por la
política de la fixture), de modo que es compatible sin reescribir la política;
los casos de incompatibilidad usan directorios `src/…`, `tests/…` o no
clasificados.

Señuelo (`decoy`): en los casos de rechazo se conserva en `docs/` un estado y
una política VÁLIDOS. Hoy los consumidores leen las rutas fijas `docs/…`, por
lo que aceptan el señuelo y las aserciones de rechazo fallan por
AssertionError de comportamiento pendiente (no por import/sintaxis/fixture).

Mapeo test -> postcondición (una promesa observable por test, R2):

  test_registered_layout_is_read_by_validate_state_and_status
      -> PC-05 (acceso de estado/orientación). Sin este test, un proyecto con
         layout propio sería leído como inexistente en docs/ y el usuario no
         podría ni validar ni orientarse.
  test_registered_layout_receives_lifecycle_writes_and_reaches_rest
      -> PC-05, PC-07(g del encargo f). Sin este test, el cierre y la
         apertura de unidad escribirían estado en docs/ y dejarían dos
         verdades o un ciclo que no llega a reposo coherente.
  test_prepare_binds_state_and_policy_path_in_selected_directory
      -> PC-05 (preparación). Sin este test, `prepare` publicaría el binding
         y el contexto apuntando a docs/ aunque el proyecto esté en otro lado.
  test_materialization_writes_under_selected_directory
  test_materialization_refuses_legacy_destination_when_layout_is_registered
      -> PC-05 (receipt/materialización). Sin estos tests, el artefacto
         aprobado caería bajo docs/specs en vez de la metodología elegida, o
         se aceptaría el destino histórico contra el layout seleccionado.
  test_legacy_project_without_locator_keeps_working_unchanged
      -> PC-02 + PC-05 (regresión legado; CONTROL: pasa hoy, no es RED).
         Sin este test, la nueva resolución podría romper o registrar un
         locator en un proyecto histórico.
  test_continuation_rejects_designated_execution_absent_from_selected_state
  test_continuation_rejects_alternative_state_with_a_different_execution
  test_continuation_rejects_when_locator_disappears_and_legacy_is_selected
      -> PC-07 (§4.5). Sin estos tests, un estado alternativo o el cambio de
         selección sustituiría silenciosamente a la ejecución designada.
  test_policy_path_recorded_in_execution_must_match_selected_layout
      -> PC-07 (§4.5.3). Sin este test, una ejecución ligada a otra ruta de
         política seguiría adelante con el layout seleccionado.
  test_incompatible_methodology_directory_is_rejected_without_changes
  test_open_unit_refuses_incompatible_layout_before_any_write
      -> PC-06 (§4.4). Sin estos tests, una metodología dentro de src/ o
         tests/ (o sin clasificar) se usaría operativamente, o el rechazo
         reescribiría la política/ampliaría permisos en silencio.
  test_locator_resolving_to_repository_root_is_rejected_without_writes
      -> decisions.md (2026-11-16) + PC-04/PC-05. Sin este test, un locator
         hacia la raíz volvería indistinguibles estado, política y `.cdad/`.

Enmienda 020-001 (docs/specs/020-001-versioned-layout-local-execution/):
la declaración vive en la ruta fija `cdad/project-layout.json` (schema 2:
schema_version, methodology_dir, operational_dir) y los registros
operacionales nuevos van bajo el `operational_dir` declarado (por defecto
`.cdad-execution`). `relocate()` REESCRIBE esa declaración con el
methodology_dir elegido. Un `.cdad/` poblado, el localizador viejo
`.cdad/project-layout.json` o una declaración sin `operational_dir` es un
proyecto NO MIGRADO: guía a `layout-migration.md`, sin escribir (inversión
deliberada de la fila `cdad_records` y del caso nuevo de migración al final).

No cubierto aquí (declarado): variante de `policy.snapshot` alterado en
contexto (§4.5.4), porque el rechazo del snapshot ya es comportamiento
vigente independiente del layout y no es RED; PC-08/PC-09 de `intake` es T3.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from test_005_012_t1_register_transition_base import (
    AUTHORITY_REF,
    FEATURE_ID,
    PACKET_CLI,
    RESULT_CLI,
    _Fixture,
)
from _layout_support import (
    DECLARATION_REL, OPERATIONAL_DIR, declaration_document, write_declaration,
)
from test_004_002_t2_bootstrap import (
    build_project, prepare_args, read_state, write_state,
)
from test_019_004_layout import assert_migration_guidance
from test_019_002_resting_orientation import (
    CLOSURE_REL,
    CLOSURE_STAGE,
    NEXT_FEATURE,
    _RestFixture,
)

APPROVER = "Demo Approver"
CUSTOM = "docs/custom-method"
LOCATOR_REL = DECLARATION_REL  # 020-001: ruta fija de la declaración
LEGACY_STATE = "docs/.cdad-state.json"
LEGACY_POLICY = "docs/cdad-policy.json"
CLI_TIMEOUT_S = 90


# ------------------------------------------------------------------ helpers


def snapshot(root: Path) -> dict:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            out[rel] = ("link", os.readlink(p))
        elif p.is_dir():
            out[rel] = ("dir", None)
        else:
            out[rel] = ("file", p.read_bytes())
    return out


def exec_context_path(fx) -> Path:
    return fx.root / OPERATIONAL_DIR / "executions" / fx.execution_id / "execution.json"


def relocate(fx, rel: str = CUSTOM, *, decoy: bool = False,
             register: bool = True, policy_path: str | None = None) -> Path:
    """Mueve (o copia, con `decoy`) el estado y la política legados a `rel`,
    registra el locator y reescribe el `policy.path` del/los contexto(s) v2
    publicados (la identidad queda ligada a la política del layout)."""
    root = fx.root
    dest = root / rel
    dest.mkdir(parents=True, exist_ok=True)
    for src_rel, name in ((LEGACY_STATE, ".cdad-state.json"),
                          (LEGACY_POLICY, "cdad-policy.json")):
        src = root / src_rel
        if src.exists():
            shutil.copy2(src, dest / name)
            if not decoy:
                src.unlink()
    if not decoy:
        # el contrato y su pin de aprobación viven bajo la metodología
        # declarada (<methodology_dir>/specs/<f>/spec.md); otros documentos
        # citados por ruta explícita (p. ej. closure.md) no se mueven.
        moved = False
        for spec in sorted((root / "docs" / "specs").glob("*/spec.md")):
            target = dest / "specs" / spec.parent.name / "spec.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(spec), str(target))
            moved = True
        state_file = dest / ".cdad-state.json"
        if moved and state_file.exists():
            state_file.write_text(state_file.read_text(encoding="utf-8").replace(
                "docs/specs/", f"{rel}/specs/"), encoding="utf-8")
    if register:
        loc = root / LOCATOR_REL
        loc.parent.mkdir(parents=True, exist_ok=True)
        loc.write_text(json.dumps(declaration_document(rel, OPERATIONAL_DIR)),
                       encoding="utf-8")
    new_path = policy_path or f"{rel}/cdad-policy.json"
    for ctx in (root / OPERATIONAL_DIR / "executions").glob("*/execution.json"):
        doc = json.loads(ctx.read_text(encoding="utf-8"))
        doc["policy"]["path"] = new_path
        ctx.write_text(json.dumps(doc), encoding="utf-8")
    return dest


def custom_state(fx, rel: str = CUSTOM) -> dict:
    return json.loads(
        (fx.root / rel / ".cdad-state.json").read_text(encoding="utf-8"))


def write_custom_state(fx, doc: dict, rel: str = CUSTOM) -> None:
    (fx.root / rel / ".cdad-state.json").write_text(
        json.dumps(doc), encoding="utf-8")


def validate_with_context(fx) -> subprocess.CompletedProcess:
    return fx.run_packet(
        "validate-state", "--project-root", str(fx.root),
        "--execution-context", str(exec_context_path(fx)))


def assert_rejected(proc, label: str, *, mention: tuple = ()) -> None:
    assert proc.returncode != 0, (
        f"{label}: debe rechazarse (rc!=0); rc={proc.returncode} "
        f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    assert proc.stderr.strip(), f"{label}: el rechazo debe explicarse en stderr"
    low = proc.stderr.lower()
    for word in mention:
        assert word.lower() in low, (
            f"{label}: el diagnóstico debe mencionar {word!r}: "
            f"{proc.stderr!r}")


def status_doc(fx) -> dict:
    proc = fx.run_packet("status", "--project-root", str(fx.root))
    assert proc.returncode == 0, (
        f"`status` debe responder rc=0: rc={proc.returncode} "
        f"{proc.stdout!r} {proc.stderr!r}")
    return json.loads(proc.stdout)


class _LazyRest:
    """Construye `_RestFixture` en el primer acceso, DENTRO del cuerpo del test:
    si la capa declarada (PC-1) aún no funciona, el fallo es un
    AssertionError de comportamiento del test y no un ERROR de setup."""

    def __init__(self, base: Path) -> None:
        self.__dict__["_base"] = base
        self.__dict__["_fx"] = None

    def _build(self) -> _RestFixture:
        if self.__dict__["_fx"] is None:
            try:
                self.__dict__["_fx"] = _RestFixture(self.__dict__["_base"])
            except AssertionError as exc:
                raise AssertionError(
                    "PC-1 (precondición): un proyecto declarado en "
                    f"{DECLARATION_REL} (schema 2) debe preparar, despachar y "
                    f"recibir bajo {OPERATIONAL_DIR}/: {exc}") from exc
        return self.__dict__["_fx"]

    def __getattr__(self, name: str):
        return getattr(self._build(), name)


@pytest.fixture
def rest(tmp_path: Path) -> _LazyRest:
    return _LazyRest(tmp_path)


class _Bare(_Fixture):
    """Proyecto con estado sin ejecución (previo a `prepare`)."""

    def __init__(self, base: Path) -> None:
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        self._build_project()


# ------------------------------------------------------------- PC-05 lectura


def test_registered_layout_is_read_by_validate_state_and_status(rest) -> None:
    """PC-05: con locator registrado, validate-state y status leen el estado
    del directorio elegido, no docs/."""
    relocate(rest)
    assert not (rest.root / LEGACY_STATE).exists()
    proc = rest.run_packet(
        "validate-state", "--project-root", str(rest.root))
    assert proc.returncode == 0, (
        f"validate-state debe leer {CUSTOM}/.cdad-state.json: "
        f"{proc.stdout!r} {proc.stderr!r}")
    with_ctx = validate_with_context(rest)
    assert with_ctx.returncode == 0, (
        "validate-state con el contexto ligado a la política del layout "
        f"debe pasar: {with_ctx.stdout!r} {with_ctx.stderr!r}")
    before = snapshot(rest.root)
    doc = status_doc(rest)
    assert doc, "status debe emitir la vista compacta del layout seleccionado"
    assert snapshot(rest.root) == before, "status es de solo lectura"


def test_registered_layout_receives_lifecycle_writes_and_reaches_rest(
        rest) -> None:
    """PC-05 (+ encargo f): cierre y apertura escriben el estado del layout y
    llegan a reposo coherente sin tocar docs/."""
    relocate(rest)
    closed = rest.close()
    assert closed.returncode == 0, (
        f"el cierre legítimo debe aplicarse al estado del layout: "
        f"{closed.stdout!r} {closed.stderr!r}")
    st = custom_state(rest)
    assert st["current_stage"] == "idle" and st["active_feature"] is None, (
        f"el cierre debe dejar reposo en {CUSTOM}: "
        f"{st['current_stage']!r}/{st['active_feature']!r}")
    assert "open-unit" in json.dumps(status_doc(rest)), (
        "status debe recomendar open-unit sobre el layout seleccionado")
    opened = rest.open_unit()
    assert opened.returncode == 0, (
        f"open-unit debe abrir la unidad en cola: {opened.stdout!r} "
        f"{opened.stderr!r}")
    assert custom_state(rest)["active_feature"] == NEXT_FEATURE, (
        "la apertura debe escribirse en el estado del layout")
    assert not (rest.root / LEGACY_STATE).exists(), (
        "ningún estado debe aparecer en docs/ cuando el layout es otro")
    assert not (rest.root / LEGACY_POLICY).exists()


def _adopt_cdad_methodology(fx) -> None:
    """Proyecto cuya metodología declarada es `cdad` (default de proyectos
    nuevos): estado, política, specs y épicas viven bajo `cdad/`."""
    relocate(fx, "cdad")
    root = fx.root
    policy_path = root / "cdad" / "cdad-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    policy["path_policy"]["documentation_roots"] = ["cdad"]
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    shutil.move(str(root / "docs" / "epics"), str(root / "cdad" / "epics"))
    state_path = root / "cdad" / ".cdad-state.json"
    doc = json.loads(state_path.read_text(encoding="utf-8").replace(
        "docs/epics/", "cdad/epics/"))
    epic = doc["active_epic"]
    doc["epic_history"] = [
        {"epic": epic, "stage": "epic-plan", "approved_by": "<owner>"}]
    state_path.write_text(json.dumps(doc), encoding="utf-8")
    plan = root / "cdad" / "epics" / epic / "plan.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(
        "# Epic plan fixture\n\n| Unit | Title |\n|---|---|\n"
        f"| {doc['active_feature']} | fixture unit |\n", encoding="utf-8")


def text_state(fx) -> str:
    return (fx.root / "cdad" / ".cdad-state.json").read_text(encoding="utf-8")


def test_prepare_binds_state_and_policy_path_in_selected_directory(
        tmp_path: Path) -> None:
    """PC-05: prepare registra binding y paquete en el estado del layout y
    liga el contexto a la política del layout; con metodología `cdad` el
    contrato aprobado y el plan de épica se derivan de `cdad/`, no de docs/."""
    fx = _Bare(tmp_path)
    _adopt_cdad_methodology(fx)
    proc = fx.run_packet(*prepare_args(
        fx.root, role="test-writer", substage="red",
        objective="prepare en layout registrado"))
    assert proc.returncode == 0, (
        f"prepare debe operar sobre cdad/ y derivar el contrato de la "
        f"metodología declarada: {proc.stdout!r} {proc.stderr!r}")
    st = json.loads(
        (fx.root / "cdad" / ".cdad-state.json").read_text(encoding="utf-8"))
    assert st["execution"] and st["active_packet"], (
        "prepare debe escribir execution y active_packet en el estado del "
        "layout")
    ctxs = list((fx.root / OPERATIONAL_DIR / "executions").glob("*/execution.json"))
    assert ctxs, "prepare debe publicar el contexto de ejecución"
    recorded = json.loads(ctxs[-1].read_text(encoding="utf-8"))["policy"]["path"]
    assert recorded == "cdad/cdad-policy.json", (
        f"el contexto debe registrar la política del layout, no {recorded!r}")
    request = json.loads(next(
        (fx.root / OPERATIONAL_DIR / "packets").glob("*/REQUEST.json")
    ).read_text(encoding="utf-8"))
    assert request["contract"]["path"] == f"cdad/specs/{FEATURE_ID}/spec.md", (
        f"el contrato debe derivarse de la metodología declarada: "
        f"{request['contract']!r}")
    assert {"class": "contract", "root": f"cdad/specs/{FEATURE_ID}"} in (
        request["read_scope"]), request["read_scope"]
    other = _Bare(tmp_path / "architect")
    _adopt_cdad_methodology(other)
    arch = other.run_packet(*prepare_args(
        other.root, role="architect", substage="draft",
        objective="plan de épica en layout registrado"))
    assert arch.returncode == 0, (
        f"prepare del architect debe derivar el plan de cdad/epics: "
        f"{arch.stdout!r} {arch.stderr!r}")
    packet = next((other.root / OPERATIONAL_DIR / "packets").glob("*/REQUEST.json"))
    plan_request = json.loads(packet.read_text(encoding="utf-8"))
    epic = json.loads(text_state(other))["active_epic"]
    projection = (packet.parent / "UNIT-CONTRACT.md").read_text(encoding="utf-8")
    assert plan_request["contract"]["kind"] == "approved-unit-contract", (
        plan_request["contract"])
    assert f"cdad/epics/{epic}/plan.md" in projection, (
        "la proyección debe derivarse del plan bajo la metodología declarada")
    assert "docs/epics" not in projection
    assert not (fx.root / LEGACY_STATE).exists()
    assert not (fx.root / LEGACY_POLICY).exists()
    assert not list((fx.root / "docs" / "specs").glob("*/spec.md"))


# ------------------------------------------------------- PC-05 materialización


def _materialize(fx, target: str):
    receipt = fx.receipt_path()
    auth = {
        "schema_version": 1,
        "execution_id": fx.execution_id,
        "packet_id": fx.packet_id,
        "receipt_sha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
        "authorized_by": "<owner> (HITL delegada)",
        "authority_ref": AUTHORITY_REF,
        "approval_effect": False,
        "copies": [{"part": "role-report", "target": target,
                    "expected_previous_sha256": None}],
    }
    path = fx.root / OPERATIONAL_DIR / "inbox" / "MATERIALIZE.json"
    path.write_text(json.dumps(auth, sort_keys=True) + "\n", encoding="utf-8")
    return fx.run_result(
        "materialize", "--project-root", str(fx.root),
        "--receipt", str(receipt), "--authorization", str(path))


def test_materialization_writes_under_selected_directory(
        tmp_path: Path) -> None:
    """PC-05: la raíz permitida del artefacto es <methodology_dir>/specs/<f>/."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx)
    target = f"{CUSTOM}/specs/{FEATURE_ID}/test-writer-role-report.md"
    proc = _materialize(fx, target)
    assert proc.returncode == 0, (
        f"materialize debe aceptar el destino bajo el layout: "
        f"{proc.stdout!r} {proc.stderr!r}")
    assert (fx.root / target).is_file(), "el artefacto debe quedar en el layout"


def test_materialization_refuses_legacy_destination_when_layout_is_registered(
        tmp_path: Path) -> None:
    """PC-05: con layout registrado, el destino docs/specs/… se rechaza sin
    escribir."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, decoy=True)
    target = f"docs/specs/{FEATURE_ID}/test-writer-role-report.md"
    before = snapshot(fx.root)
    proc = _materialize(fx, target)
    assert_rejected(proc, "destino legado con layout registrado")
    assert not (fx.root / target).exists()
    after = snapshot(fx.root)
    changed = [k for k in after
               if before.get(k) != after[k]
               and k != f"{OPERATIONAL_DIR}/inbox/MATERIALIZE.json"
               and not k.startswith(f"{OPERATIONAL_DIR}/")]
    assert not changed, f"el rechazo no debe escribir destinos: {changed}"


# ------------------------------------------------------------- PC-02 control


def test_legacy_project_without_locator_keeps_working_unchanged(rest) -> None:
    """PC-02/PC-05 (CONTROL, pasa hoy): sin locator el ciclo usa docs/ y no se
    registra ningún locator. 020-001: la fixture nace declarada; aquí se
    retira la declaración para conservar el proyecto legado SIN declaración
    (sin `.cdad/` poblado, por tanto no es un proyecto no migrado)."""
    (rest.root / LOCATOR_REL).unlink()
    (rest.root / LOCATOR_REL).parent.rmdir()
    closed = rest.close()
    assert closed.returncode == 0, f"{closed.stdout!r} {closed.stderr!r}"
    assert "open-unit" in json.dumps(status_doc(rest))
    opened = rest.open_unit()
    assert opened.returncode == 0, f"{opened.stdout!r} {opened.stderr!r}"
    assert read_state(rest.root)["active_feature"] == NEXT_FEATURE
    assert not (rest.root / LOCATOR_REL).exists(), (
        "un proyecto legado no debe recibir locator")


# ----------------------------------------------------------------- PC-07 §4.5


def test_continuation_rejects_designated_execution_absent_from_selected_state(
        tmp_path: Path) -> None:
    """PC-07: el estado seleccionado sin la ejecución designada falla cerrado,
    aunque docs/ contenga un estado válido con ella."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, decoy=True)
    st = custom_state(fx)
    st["execution"] = None
    st["active_packet"] = None
    write_custom_state(fx, st)
    before = snapshot(fx.root)
    proc = validate_with_context(fx)
    assert_rejected(proc, "ejecución designada ausente del estado seleccionado",
                    mention=("execution",))
    assert snapshot(fx.root) == before, "el rechazo no modifica artefactos"


def test_continuation_rejects_alternative_state_with_a_different_execution(
        tmp_path: Path) -> None:
    """PC-07: un estado alternativo con OTRA ejecución no sustituye a la
    designada; no se busca en docs/."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, decoy=True)
    st = custom_state(fx)
    st["execution"] = dict(st["execution"], id="exec-otra-ejecucion-activa")
    write_custom_state(fx, st)
    before = snapshot(fx.root)
    proc = validate_with_context(fx)
    assert_rejected(proc, "estado alternativo con otra ejecución",
                    mention=("execution",))
    assert snapshot(fx.root) == before


def test_continuation_rejects_when_locator_disappears_and_legacy_is_selected(
        tmp_path: Path) -> None:
    """PC-07: si el locator desaparece y se elige docs/, la ejecución ligada
    al layout personalizado no continúa."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, decoy=True)
    (fx.root / LOCATOR_REL).unlink()
    before = snapshot(fx.root)
    proc = validate_with_context(fx)
    assert_rejected(proc, "locator desaparecido selecciona docs/",
                    mention=("polic",))
    assert snapshot(fx.root) == before


def test_policy_path_recorded_in_execution_must_match_selected_layout(
        tmp_path: Path) -> None:
    """PC-07 (§4.5.3): la política registrada en el contexto debe coincidir con
    la ruta convencional del layout seleccionado."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, decoy=True, policy_path=LEGACY_POLICY)
    before = snapshot(fx.root)
    proc = validate_with_context(fx)
    assert_rejected(proc, "policy.path del contexto discrepa del layout",
                    mention=("polic",))
    assert snapshot(fx.root) == before


# ----------------------------------------------------------------- PC-06 §4.4


@pytest.mark.parametrize("rel", ["src/method", "tests/method", "process/cdad"])
def test_incompatible_methodology_directory_is_rejected_without_changes(
        tmp_path: Path, rel: str) -> None:
    """PC-06: directorio clasificado como implementación/tests o sin
    clasificar → rechazo accionable, sin reescribir política ni cambios."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx, rel, decoy=True)
    before = snapshot(fx.root)
    policy_before = (fx.root / LEGACY_POLICY).read_bytes()
    proc = validate_with_context(fx)
    assert_rejected(proc, f"layout incompatible {rel}",
                    mention=(rel, "classif", "polic"))
    assert snapshot(fx.root) == before, "sin cambios de archivos"
    assert (fx.root / LEGACY_POLICY).read_bytes() == policy_before, (
        "la política no se reescribe ni se amplían permisos")


def test_open_unit_refuses_incompatible_layout_before_any_write(rest) -> None:
    """PC-06: una operación con efectos (open-unit) no actúa sobre un layout
    incompatible."""
    closed = rest.close()
    assert closed.returncode == 0, f"{closed.stdout!r} {closed.stderr!r}"
    relocate(rest, "src/method", decoy=True)
    before = snapshot(rest.root)
    proc = rest.open_unit()
    assert_rejected(proc, "open-unit en layout incompatible",
                    mention=("src/method", "classif"))
    assert snapshot(rest.root) == before


# --------------------------------------------------------------- decisions.md


def test_locator_resolving_to_repository_root_is_rejected_without_writes(
        tmp_path: Path) -> None:
    """decisions.md 2026-11-16: un locator que resuelve a la raíz del
    repositorio (aquí, por symlink) no está soportado y se rechaza sin
    escrituras, tanto en `layout` como en los consumidores operativos."""
    fx = _Fixture(tmp_path, mode="ready")
    (fx.root / "rootlink").symlink_to(".", target_is_directory=True)
    write_declaration(fx.root, "rootlink")
    before = snapshot(fx.root)
    layout = subprocess.run(
        [sys.executable, str(PACKET_CLI), "layout",
         "--project-root", str(fx.root)],
        capture_output=True, text=True, cwd=str(fx.root.parent),
        env=fx.env(), timeout=CLI_TIMEOUT_S)
    assert_rejected(layout, "layout con locator a la raíz",
                    mention=("root",))
    assert snapshot(fx.root) == before
    for args in (("validate-state", "--project-root", str(fx.root)),
                 ("status", "--project-root", str(fx.root))):
        proc = fx.run_packet(*args)
        assert_rejected(proc, f"{args[0]} con locator a la raíz")
    assert snapshot(fx.root) == before, "ningún rechazo escribe"


# ------------------------------------------- PC-05 búsqueda convencional de spec
#
# Mapeo (una promesa observable por test, R2):
#   test_gap_report_resolves_spec_under_selected_methodology_dir
#       -> PC-05 (búsqueda convencional del contrato con layout registrado).
#          Sin este test, el usuario con layout propio vería sus unidades
#          cerradas como «sin spec» en el informe de huecos y perdería la
#          visibilidad de cobertura.
#   test_gap_report_missing_unit_names_selected_path_and_ignores_legacy_docs
#       -> PC-05. Sin este test, un spec histórico en docs/specs se aceptaría
#          en lugar del layout elegido, o la unidad ausente no tendría un
#          diagnóstico recuperable que nombre la ruta realmente buscada.
#   test_gap_report_legacy_layout_keeps_docs_specs_lookup (CONTROL: pasa hoy)
#       -> PC-02 + PC-05. Sin este test, la nueva resolución podría romper el
#          proyecto legado que sigue en docs/.

CONTRACT_LINKS_CLI = (Path(PACKET_CLI).parent / "cdad_contract_links.py")


def _gap_unit(root: Path, base: str, unit: str) -> str:
    """Crea <base>/specs/<unit>/{spec.md,closure.md}; devuelve sha del cierre."""
    d = root / base / "specs" / unit
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(
        "# spec\n<!-- cdad:pc PC-1 promise=A -->\nTexto.\n", encoding="utf-8")
    (d / "closure.md").write_text(f"# cierre {unit}\n", encoding="utf-8")
    return hashlib.sha256((d / "closure.md").read_bytes()).hexdigest()


def _gap_state(root: Path, rows: list[tuple[str, str, str]]) -> Path:
    feats = [{"id": u, "status": "done",
              "closure_evidence": {"path": f"{b}/specs/{u}/closure.md",
                                   "sha256": sha}} for u, b, sha in rows]
    path = root / "STATE.json"
    path.write_text(json.dumps({"epic_features": feats, "epic_history": []}),
                    encoding="utf-8")
    return path


def _register(root: Path, rel: str) -> None:
    write_declaration(root, rel)


def _gap_report(root: Path, state: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CONTRACT_LINKS_CLI), "gap-report",
         "--project-root", str(root), "--state", str(state)],
        capture_output=True, text=True, cwd=str(root.parent),
        timeout=CLI_TIMEOUT_S)


@pytest.mark.parametrize("rel", ["cdad", "process/cdad"])
def test_gap_report_resolves_spec_under_selected_methodology_dir(
        tmp_path: Path, rel: str) -> None:
    """PC-05: con layout registrado fuera de docs/, la unidad cerrada se
    resuelve en <methodology_dir>/specs/<unidad>/spec.md."""
    root = tmp_path / "proj"
    sha = _gap_unit(root, rel, "unit-a")
    _register(root, rel)
    state = _gap_state(root, [("unit-a", rel, sha)])
    proc = _gap_report(root, state)
    assert proc.returncode == 0, f"{proc.stdout!r} {proc.stderr!r}"
    payload = json.loads(proc.stdout)
    units = [u.get("unit") for u in payload.get("universe", [])]
    assert units == ["unit-a"], (
        f"unit-a debe estar en el universo vía {rel}/specs/unit-a/spec.md; "
        f"universe={units} out_of_universe={payload.get('out_of_universe')}")
    spec_path = payload["universe"][0]["spec"]["path"]
    assert spec_path == f"{rel}/specs/unit-a/spec.md", spec_path
    assert any(o.get("unit") == "unit-a" and o.get("id") == "PC-1"
               for o in payload.get("obligations", [])), (
        "las obligaciones deben derivarse del spec del layout")


def test_gap_report_missing_unit_names_selected_path_and_ignores_legacy_docs(
        tmp_path: Path) -> None:
    """PC-05: unidad sin spec en el layout elegido → diagnóstico recuperable
    que nombra esa ruta; un spec en docs/specs no la sustituye."""
    root = tmp_path / "proj"
    sha_ok = _gap_unit(root, "cdad", "unit-a")
    sha_old = _gap_unit(root, "docs", "unit-b")  # solo en la ruta histórica
    _register(root, "cdad")
    state = _gap_state(root, [("unit-a", "cdad", sha_ok),
                              ("unit-b", "docs", sha_old)])
    proc = _gap_report(root, state)
    assert proc.returncode == 0, f"{proc.stdout!r} {proc.stderr!r}"
    payload = json.loads(proc.stdout)
    assert [u.get("unit") for u in payload.get("universe", [])] == ["unit-a"], (
        "unit-b no debe entrar al universo por un spec en docs/specs: "
        f"{payload.get('universe')}")
    entry = [o for o in payload.get("out_of_universe", [])
             if o.get("unit") == "unit-b"]
    assert entry, f"unit-b debe informarse fuera del universo: {payload}"
    reason = entry[0].get("reason", "")
    assert "cdad/specs/unit-b/spec.md" in reason, (
        f"el diagnóstico debe nombrar la ruta del layout elegido: {reason!r}")
    assert "docs/specs" not in reason, (
        f"el diagnóstico no debe citar la ruta fija histórica: {reason!r}")
    assert entry[0].get("status") == "done", "el estado debe ser recuperable"


def test_gap_report_legacy_layout_keeps_docs_specs_lookup(
        tmp_path: Path) -> None:
    """PC-02/PC-05 (CONTROL, pasa hoy): sin locator el spec se busca en
    docs/specs/<unidad>/spec.md y la unidad ausente cita esa ruta.

    Actualización 019-004 (T2 RED 005, §4.2): el fixture original solo
    escribía `docs/specs/**` — ni locator ni marcador legacy — lo que el
    contrato aprobado define como layout AMBIGUO (rechazado en
    tests/test_019_004_continuity_gap_ambiguity.py). Era por tanto
    genuinamente ambiguo; para conservar todas las aserciones del control
    legacy el fixture siembra ahora el marcador exacto
    `docs/.cdad-state.json`. Ninguna aserción cambia."""
    root = tmp_path / "proj"
    (root / "docs").mkdir(parents=True)
    (root / LEGACY_STATE).write_text("{}\n", encoding="utf-8")
    sha = _gap_unit(root, "docs", "unit-a")
    zdir = root / "docs" / "specs" / "unit-z"
    zdir.mkdir(parents=True)
    (zdir / "closure.md").write_text("# cierre unit-z\n", encoding="utf-8")
    sha_z = hashlib.sha256((zdir / "closure.md").read_bytes()).hexdigest()
    state = _gap_state(root, [("unit-a", "docs", sha), ("unit-z", "docs", sha_z)])
    proc = _gap_report(root, state)
    assert proc.returncode == 0, f"{proc.stdout!r} {proc.stderr!r}"
    payload = json.loads(proc.stdout)
    assert [u.get("unit") for u in payload.get("universe", [])] == ["unit-a"]
    assert payload["universe"][0]["spec"]["path"] == "docs/specs/unit-a/spec.md"
    reasons = [o.get("reason", "") for o in payload.get("out_of_universe", [])
               if o.get("unit") == "unit-z"]
    assert reasons and "docs/specs/unit-z/spec.md" in reasons[0], reasons
    assert not (root / LOCATOR_REL).exists()


# ------------------------------------------------ T2 review-fix: hallazgos 1-2
#
# Mapeo (una promesa observable por test, R2):
#   test_materialization_rejects_policy_private_destination_under_methodology_base
#       -> PC-06 (§4.4.3-4: el destino CONCRETO se clasifica con la política
#          efectiva y la protección privada se respeta; el padre doc no basta).
#          Sin este test, un artefacto aprobado se escribiría en una ruta que
#          la política declara privada, solo porque su padre es documentación.
#          Límite declarado: la política vigente rechaza raíces
#          tests/implementación anidadas bajo una raíz de documentación
#          («conflicts with»), por eso la clase privada es la única
#          alcanzable como descendiente incompatible vía política válida.
#   test_operational_commands_refuse_ambiguous_layout_without_selecting_docs
#       -> PC-04 (+ PC-05). Sin este test, con solo docs/specs o registros
#          .cdad sin layout admitido el usuario vería operar (o crear estado)
#          sobre docs/ sin marcador legado.
#   test_single_legacy_marker_is_not_diagnosed_as_ambiguous (CONTROL: pasa hoy)
#       -> PC-02. Sin este test, la corrección podría tratar como ambiguo un
#          proyecto con uno solo de los dos marcadores exactos.


def test_materialization_rejects_policy_private_destination_under_methodology_base(
        tmp_path: Path) -> None:
    """PC-06: destino bajo <methodology_dir>/specs/<f>/ que la política efectiva
    declara privado → rechazo accionable antes de escribir; un destino
    compatible vecino sigue materializando."""
    fx = _Fixture(tmp_path, mode="ready")
    relocate(fx)
    pol = fx.root / CUSTOM / "cdad-policy.json"
    doc = json.loads(pol.read_text(encoding="utf-8"))
    private_dir = f"{CUSTOM}/specs/{FEATURE_ID}/private"
    doc["path_policy"]["private_paths"] = [private_dir]
    pol.write_text(json.dumps(doc), encoding="utf-8")
    cls = fx.run_packet("validate-policy", "--project-root", str(fx.root),
                        "--classify", f"{private_dir}/x.md")
    assert cls.returncode == 0 and "private" in cls.stdout, (
        f"precondición: la política debe clasificar el destino como privado: "
        f"{cls.stdout!r} {cls.stderr!r}")
    bad = f"{private_dir}/test-writer-role-report.md"
    before = snapshot(fx.root)
    proc = _materialize(fx, bad)
    assert_rejected(proc, "destino privado bajo la base metodológica",
                    mention=(bad, "private"))
    assert not (fx.root / bad).exists(), "no debe escribirse el destino privado"
    after = snapshot(fx.root)
    changed = sorted(k for k in set(before) | set(after)
                     if before.get(k) != after.get(k)
                     and k != f"{OPERATIONAL_DIR}/inbox/MATERIALIZE.json")
    assert not changed, f"el rechazo no debe cambiar archivos: {changed}"
    ok = f"{CUSTOM}/specs/{FEATURE_ID}/test-writer-role-report.md"
    good = _materialize(fx, ok)
    assert good.returncode == 0, (
        f"un destino compatible debe seguir materializando: "
        f"{good.stdout!r} {good.stderr!r}")
    assert (fx.root / ok).is_file()


AMBIGUOUS_EVIDENCE = {
    "docs_specs": ("docs/specs/unit-a/spec.md", "# spec\n"),
    "docs_epics": ("docs/epics/e1/plan.md", "# plan\n"),
    # 020-001 (INVERTIDO): un `.cdad/` poblado sin declaración ya no es
    # «ambiguo» sino proyecto no migrado (guía a layout-migration.md).
    "cdad_records": (".cdad/executions/exec-x/execution.json", "{}\n"),
}


def _ambiguous_project(base: Path, kind: str) -> tuple[Path, dict]:
    root = base / "proj"
    rel, text = AMBIGUOUS_EVIDENCE[kind]
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")
    home = base / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["HOME"] = str(home)
    return root, env


def _run_in(root: Path, env: dict, *args: str):
    return subprocess.run(
        [sys.executable, str(PACKET_CLI), *args],
        capture_output=True, text=True, cwd=str(root.parent), env=env,
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)


@pytest.mark.parametrize("kind", sorted(AMBIGUOUS_EVIDENCE))
@pytest.mark.parametrize("command", ["validate-state", "status", "open-unit",
                                     "prepare"])
def test_operational_commands_refuse_ambiguous_layout_without_selecting_docs(
        tmp_path: Path, kind: str, command: str) -> None:
    """PC-04 + 020-001 PC-2: con solo señales insuficientes y sin locator ni
    marcador legado, el comando operativo falla sin escribir: evidencia de
    docs/ => ambigüedad; registros en un `.cdad/` poblado => proyecto no
    migrado con guía a `layout-migration.md`."""
    root, env = _ambiguous_project(tmp_path, kind)
    args = {
        "prepare": prepare_args(root, objective="layout ambiguo"),
    }.get(command, [command, "--project-root", str(root)])
    before = snapshot(root)
    proc = _run_in(root, env, *args)
    if kind == "cdad_records":
        assert_migration_guidance(proc, f"{command} con proyecto no migrado")
    else:
        assert_rejected(proc, f"{command} con layout ambiguo ({kind})",
                        mention=("ambiguous",))
    assert snapshot(root) == before, (
        f"{command} no debe escribir con layout ambiguo")
    assert not (root / LOCATOR_REL).exists()


@pytest.mark.parametrize("marker", ["docs/cdad-policy.json",
                                    "docs/.cdad-state.json"])
def test_single_legacy_marker_is_not_diagnosed_as_ambiguous(
        tmp_path: Path, marker: str) -> None:
    """PC-02 (CONTROL, pasa hoy): cualquiera de los dos marcadores exactos
    selecciona docs/; el error posible es de validación, no de ambigüedad."""
    root, env = _ambiguous_project(tmp_path, "docs_specs")
    (root / marker).write_text("{}\n", encoding="utf-8")
    before = snapshot(root)
    proc = _run_in(root, env, "validate-state", "--project-root", str(root))
    assert "ambiguous" not in (proc.stderr + proc.stdout).lower(), (
        f"un marcador legado exacto no es ambiguo: {proc.stderr!r}")
    assert snapshot(root) == before
    assert not (root / LOCATOR_REL).exists()


# ------------------------------------------------------------------- 020-001
#
# Mapeo (una promesa observable por test; techo de 2 casos nuevos):
#   test_unmigrated_project_is_refused_with_migration_guidance_before_any_write
#       -> 020-001 PC-2 (y PC-1: nada se escribe en una ubicación nueva). Sin
#          este test, el usuario con un proyecto existente vería una operación
#          que escribe en una ubicación operacional nueva sin avisarle, o un
#          rechazo sin camino de salida.
#   test_manual_handoff_then_new_execution_preserves_progress_and_history
#       -> 020-001 PC-3 (continuación; con PC-1 para el almacenamiento
#          declarado). Sin este test, el usuario con trabajo sin terminar no
#          tendría evidencia de que el traspaso manual documentado produce
#          una asignación fresca que conserva su progreso, ni de que la
#          historia vieja queda intacta.


def _files_under(path: Path) -> dict:
    if not path.exists():
        return {}
    return {p.relative_to(path).as_posix(): p.read_bytes()
            for p in sorted(path.rglob("*")) if p.is_file()}


def test_unmigrated_project_is_refused_with_migration_guidance_before_any_write(
        tmp_path: Path) -> None:
    """PC-2: un proyecto que conserva el layout operacional viejo (`.cdad/`
    poblado, sin declaración schema 2) recibe una guía breve que apunta a la
    guía canónica `layout-migration.md`, antes de cualquier escritura
    operacional: ni `.cdad/` ni `.cdad-execution/` se tocan."""
    root = build_project(tmp_path / "proj", declared=False)
    for rel, text in (
            (".cdad/executions/exec-1/execution.json", "{}\n"),
            (".cdad/packets/p1/REQUEST.json", "{}\n")):
        seed = root / rel
        seed.parent.mkdir(parents=True, exist_ok=True)
        seed.write_text(text, encoding="utf-8")
    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home))
    before = snapshot(root)
    proc = subprocess.run(
        [sys.executable, str(PACKET_CLI),
         *prepare_args(root, objective="proyecto no migrado")],
        capture_output=True, text=True, cwd=str(tmp_path), env=env,
        stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S)
    assert proc.returncode != 0, (
        "PC-2: `prepare` debe rechazar un proyecto no migrado antes de "
        f"escribir; rc={proc.returncode} stdout={proc.stdout!r} "
        f"stderr={proc.stderr!r}")
    assert "layout-migration.md" in proc.stderr, (
        "PC-2: la guía debe apuntar a layout-migration.md; "
        f"stderr={proc.stderr!r}")
    assert re.search(r"\.cdad(?![-\w])", proc.stderr), (
        "PC-2: la guía debe nombrar el layout viejo `.cdad`; "
        f"stderr={proc.stderr!r}")
    assert snapshot(root) == before, (
        "PC-2: el rechazo no debe escribir nada (ningún lock ni archivo "
        "nuevo, ni en `.cdad/` ni fuera)")
    assert not (root / OPERATIONAL_DIR).exists(), (
        f"PC-1/PC-2: no debe crearse {OPERATIONAL_DIR}/ en un proyecto no "
        "migrado")


def test_manual_handoff_then_new_execution_preserves_progress_and_history(
        tmp_path: Path) -> None:
    """PC-3: tras el traspaso manual (limpiar SOLO `execution` y
    `active_packet`), `prepare --new-execution` produce una asignación fresca
    bajo el directorio operacional declarado, sin cargar identidades
    históricas, y conserva feature, etapa, resultados, historia y
    delegación; los registros viejos quedan byte a byte intactos."""
    try:
        fx = _Fixture(tmp_path, mode="ready")
    except AssertionError as exc:
        raise AssertionError(
            "PC-1 (precondición): un proyecto declarado en "
            f"{DECLARATION_REL} (schema 2) debe preparar, despachar y "
            f"recibir bajo {OPERATIONAL_DIR}/: {exc}") from exc
    op = fx.root / OPERATIONAL_DIR
    old_exec, old_packet = fx.execution_id, fx.packet_id
    assert (op / "executions" / old_exec / "execution.json").is_file(), (
        f"PC-1: el contexto de ejecución debe publicarse bajo {OPERATIONAL_DIR}/")
    assert (op / "packets" / old_packet / "REQUEST.json").is_file(), (
        f"PC-1: el paquete debe publicarse bajo {OPERATIONAL_DIR}/")
    assert not (fx.root / ".cdad").exists(), (
        "PC-1: ningún registro nuevo debe ir a la raíz `.cdad/`")

    # Progreso sembrado (con {} la preservación sería vacía).
    state = fx.read_state()
    state["postconditions_status"] = {"1": "pending", "2": "pending", "3": "pending"}
    fx.write_state(state)
    keys = ("active_feature", "current_stage", "tdd_substage", "audit_status",
            "postconditions_status", "stage_history", "epic_features",
            "hitl_delegation")
    kept = {k: json.loads(json.dumps(state.get(k))) for k in keys}
    assert kept["postconditions_status"] and kept["stage_history"], (
        "precondición: progreso e historia no vacíos antes del traspaso")
    old_bytes = {
        "executions": _files_under(op / "executions" / old_exec),
        "packets": _files_under(op / "packets" / old_packet),
        "results": _files_under(op / "runtime" / "results" / old_exec),
        "inbox": _files_under(op / "inbox"),
    }
    assert all(old_bytes.values()), "precondición: registros viejos no vacíos"

    # Traspaso manual: limpiar solo la identidad viva.
    state["execution"] = None
    state["active_packet"] = None
    fx.write_state(state)

    proc = fx.run_packet(*prepare_args(
        fx.root, role="test-writer", substage="red",
        objective="asignación fresca tras traspaso manual",
        extra=("--new-execution",)))
    assert proc.returncode == 0, (
        "PC-3: `prepare --new-execution` debe preparar una asignación fresca: "
        f"{proc.stdout!r} {proc.stderr!r}")
    after = fx.read_state()
    new_exec = (after.get("execution") or {}).get("id")
    new_packet = (after.get("active_packet") or {}).get("id")
    assert new_exec and new_exec != old_exec, (
        f"PC-3: la ejecución nueva no debe reutilizar {old_exec!r}: {new_exec!r}")
    assert new_packet and new_packet != old_packet, (
        f"PC-3: el paquete nuevo no debe reutilizar {old_packet!r}: {new_packet!r}")
    for key in keys:
        assert after.get(key) == kept[key], (
            f"PC-3: `{key}` debe conservarse tras el traspaso: "
            f"{kept[key]!r} -> {after.get(key)!r}")
    assert {
        "executions": _files_under(op / "executions" / old_exec),
        "packets": _files_under(op / "packets" / old_packet),
        "results": _files_under(op / "runtime" / "results" / old_exec),
        "inbox": _files_under(op / "inbox"),
    } == old_bytes, "PC-3: los registros históricos deben quedar byte a byte intactos"
    new_ctx = op / "executions" / new_exec / "execution.json"
    assert new_ctx.is_file(), (
        f"PC-1: el contexto nuevo debe publicarse bajo {OPERATIONAL_DIR}/")
    assert (op / "packets" / new_packet / "REQUEST.json").is_file(), (
        f"PC-1: el paquete nuevo debe publicarse bajo {OPERATIONAL_DIR}/")
    assert old_exec not in new_ctx.read_text(encoding="utf-8"), (
        "PC-3: el contexto nuevo no debe cargar la identidad histórica")
    assert not (fx.root / ".cdad").exists(), (
        "PC-1: no debe aparecer una raíz `.cdad/` en el proyecto declarado")
    valid = fx.validate_state()
    assert valid.returncode == 0, (
        f"PC-3: validate-state debe pasar tras el traspaso: "
        f"{valid.stdout!r} {valid.stderr!r}")
