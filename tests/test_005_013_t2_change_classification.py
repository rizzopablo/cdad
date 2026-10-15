#!/usr/bin/env python3
"""005-013 T2 RED — veredicto de consecuencias por tipo de cambio: línea base
declarada, `current` / `impact` / `impeded`, journal de impacto idempotente,
salida del impedimento y bloque aditivo `unit_contract` de `status` de sólo
lectura.

Contract:
- docs/specs/005-013-unit-contract/spec.md §2.4 (consecuencias por tipo de
  cambio `change-consequence-v1`), §2.5 (línea base del veredicto y salida del
  impedimento), §2.8 (superficie `validate-unit-contract` y bloque
  `unit_contract` de `status`), §3 PD-7..PD-11, §4 INV-1/INV-8/INV-9 y §5
  AC-5..AC-7.
- docs/specs/005-013-unit-contract/plan.md §4 ficha T2 (test focal declarado
  `tests/test_005_013_t2_change_classification.py`).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo NUNCA se importa y la implementación NUNCA se lee). La
proyección de unidad y su publicación/pin (T1) ya existen; el veredicto de
consecuencias (T2) NO:

    python3 <skill-dir>/scripts/cdad_packet.py validate-unit-contract \\
        --project-root <ABS>            # operación de lectura (PD-8/PD-9/PD-10)
    python3 <skill-dir>/scripts/cdad_packet.py status --project-root <ABS>
    python3 <skill-dir>/scripts/cdad_packet.py prepare --project-root <ABS> ...

Los proyectos son fixtures sintéticos en tempdirs, con el `HOME` del subproceso
SIEMPRE en un tempdir vacío (nunca el HOME real). Los ids, títulos y rutas del
fixture son inventados (`999-…`, `epic-999-fixture`): ningún proyecto real,
ninguna ruta absoluta del dueño, ningún id de sesión real. El arnés reutiliza
por referencia el fixture de T1 (`tests/test_005_013_t1_unit_projection.py`)
sin tocar ese archivo.

Mapa test → postcondición / criterio de aceptación:

  test_pd8_current_when_independent_unit_added_without_effect
      -> PD-8 (agregar una unidad futura INDEPENDIENTE + la edición de la
         historia → `current`, sin registro de impacto, sin impedir la
         recepción del paquete despachado) / AC-5.
  test_pd8_current_when_only_history_edited
      -> PD-8 (editar SOLO la historia → `current`) / AC-5.
  test_pd9_impact_when_unit_scope_changes_with_durable_record
      -> PD-9 (cambia la parte `unit` → `impact` con el registro durable en el
         directorio del paquete de la línea base: `reason`,
         `contract_sha256_old`, `contract_sha256_new`, `changed_parts`; el
         registro no aprueba ni cambia el state) / AC-5.
  test_pd9_impact_when_unit_dependency_changes
      -> PD-9 (una dependencia de la fila de la unidad → `impact`) / AC-5.
  test_pd9_impact_when_shared_part_changes
      -> PD-9 (una parte `shared` difiere → `impact`) / AC-5.
  test_pd9_impact_does_not_block_reception_of_dispatched_packet
      -> PD-9/PD-6 (el registro NO bloquea la recepción del paquete ya
         despachado) / AC-5.
  test_pd8_pd10_edited_authorization_section_is_impact_never_impeded
      -> PD-8/PD-10 (editar la sección de autorización → `impact`, NUNCA
         `impeded`) / AC-6.
  test_pd10_impeded_when_epic_plan_approval_retired_with_exit
      -> PD-10 (autorización retirada → `impeded` rc=2 con el marcador
         existente y la salida nombrada; registrar la aprobación `epic-plan` →
         `prepare` rc=0 y la proyección nueva pasa a ser la línea base) / AC-6.
  test_pd10_impeded_when_hitl_delegation_revoked_with_exit
      -> PD-10 (delegación revocada → `impeded` rc=2, marcador existente y
         salida nombrada) / AC-6.
  test_pd7_baseline_is_the_most_recent_packet_of_the_unit
      -> PD-7 (la línea base es la proyección registrada del ÚLTIMO paquete de
         la unidad; se declara en el veredicto) / AC-5.
  test_pd7_no_registered_projection_yields_current
      -> PD-7 (sin paquete con proyección registrada → `current`) / AC-5.
  test_pd11_status_informs_verdict_and_writes_nothing
      -> PD-11 (el bloque aditivo `unit_contract` informa `mode`, línea base,
         digest vivo, veredicto, partes que difieren y motivo; dos `status`
         consecutivos dejan el proyecto byte a byte idéntico, sin journal; la
         vista conserva sus campos) / AC-7.
  test_pd9_journal_is_idempotent_for_same_digest_pair
      -> PD-9 (mismo par de digests → journal byte a byte idéntico; un par
         distinto agrega un registro nuevo, no pisa el anterior) / AC-7.
  test_inv8_restrictive_prose_is_impact_never_impeded
      -> PD-10/INV-8 (el CLI no decide la inmediatez de una restricción por
         prosa: prosa restrictiva en una parte `shared` → `impact`, nunca
         `impeded`).
  test_inv1_inv9_verdict_does_not_write_state_nor_policy
      -> PD-11/INV-1/INV-9 (la operación de veredicto no escribe el state ni
         la política; la decisión del orquestador va a la nota de
         `stage_history`, que el CLI no toca).

RED hoy (hecho medido): `validate-unit-contract` NO existe (el parser responde
rc=2 «invalid choice: 'validate-unit-contract'», verificado por sonda) y el
bloque `unit_contract` de `status` informa `registered: null`, `live: null` y
`verdict: null`. Cada caso falla en la ASERCIÓN del comportamiento del contrato
(AssertionError), nunca en ImportError, SyntaxError, AttributeError, un error
de uso del CLI ni un fixture mal armado: las aserciones de rechazo de dominio
excluyen explícitamente el error de uso y los accesos al bloque de la vista
guían `null` con `or {}` (nunca un AttributeError).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest

from test_005_013_t1_unit_projection import (
    APPROVER,
    AUTHORITY_BODY,
    EPIC_ID,
    FEATURE_ID,
    HISTORY_BODY,
    OTHER_FEATURE_ID,
    PACKET_CLI,
    PLAN_REL,
    POLICY_REL,
    SHARED_PREVAILS_BODY,
    SHARED_PREVAILS_TITLE,
    STATE_REL,
    Fixture,
    plan_text,
    plain_cell,
    sha256_bytes,
    unit_row,
)

# ---------------------------------------------------------------- contrato
VERDICT_CURRENT = "current"
VERDICT_IMPACT = "impact"
VERDICT_IMPEDED = "impeded"

# Vocabulario de marcadores EXISTENTE reusado (spec §2.4; no se inventa uno
# nuevo para las causas ya cubiertas).
MARKER_APPROVAL_PENDING = "approval pending"
MARKER_STATE_INCOHERENT = "state incoherent"
USAGE_ERROR_TOKEN = "invalid choice"

JOURNAL_NAME = ".impact.json"
IMPACT_KEYS = ("reason", "contract_sha256_old", "contract_sha256_new",
               "changed_parts")

# Campos existentes de la vista compacta `compact-view-v1` (005-003) que NO se
# relajan: el bloque `unit_contract` es ADITIVO (spec §2.8; INV-4 de 005-011).
REQUIRED_TOP = (
    "project", "epic", "feature", "execution", "packet",
    "authority", "version", "next", "entry", "unknowns",
)

HEX64 = re.compile(r"[0-9a-f]{64}")


# ---------------------------------------------------------------- helpers


class T2Fixture(Fixture):
    """Fixture de T1 + las mutaciones declaradas y la superficie de T2.

    Hereda de `tests/test_005_013_t1_unit_projection.py::Fixture` (proyecto
    sintético autocontenido, HOME aislado, `prepare`/`dispatch`/`receive`
    reales) SIN tocar ese archivo.
    """

    # -- CLI de T2 ------------------------------------------------------

    def validate_unit_contract(self, *extra: str):
        """Operación de lectura del veredicto (spec §2.8)."""
        return self.run(PACKET_CLI, "validate-unit-contract",
                        "--project-root", str(self.root), *extra)

    def status_doc(self) -> dict:
        proc = self.status()
        assert proc.returncode == 0, (
            "precondición (fixture): la vista `status` debe emitir (rc=0): "
            f"{proc.stdout!r} {proc.stderr!r}")
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise AssertionError(
                "precondición (fixture): stdout de `status` no es JSON: "
                f"{proc.stdout[:200]!r}") from exc

    # -- mutaciones declaradas del fixture (lado orquestador) -----------

    def _write_state(self, state: dict) -> None:
        (self.root / STATE_REL).write_text(
            json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")

    def clear_active_packet(self) -> None:
        """Transición del orquestador entre subetapas: el paquete activo se
        completa y el state queda listo para la generación siguiente."""
        state = self.state()
        state["active_packet"] = None
        self._write_state(state)

    def second_packet_of_the_unit(self, substage: str = "draft") -> None:
        """Publica un SEGUNDO paquete de la MISMA unidad (otra subetapa del
        architect), dejando intactos los bytes del primero (INV-3). Es la
        precondición de PD-7 (línea base = el paquete más reciente)."""
        self.clear_active_packet()
        proc = self.prepare(substage=substage)
        assert proc.returncode == 0, (
            "precondición (fixture): el segundo `prepare` del architect debe "
            f"publicar el paquete (rc=0): {proc.stdout!r} {proc.stderr!r}")

    def _edit_plan(self, old: str, new: str) -> None:
        path = self.root / PLAN_REL
        text = path.read_text(encoding="utf-8")
        assert old in text, (
            f"precondición (fixture): el plan debe contener {old!r}")
        edited = text.replace(old, new, 1)
        assert edited != text, (
            "precondición (fixture): la edición debe cambiar los bytes del plan")
        path.write_text(edited, encoding="utf-8")

    def edit_unit_scope(self) -> None:
        """Edita el ALCANCE de la fila de la unidad activa (parte `unit`)."""
        self._edit_plan(
            unit_row(plain_cell()),
            unit_row(plain_cell() + " (alcance editado)"))

    def edit_unit_dependency(self) -> None:
        """Edita una DEPENDENCIA de la fila de la unidad activa (parte
        `unit`)."""
        self._edit_plan(
            unit_row(plain_cell()),
            f"| 1 | {plain_cell()} | in-progress | {OTHER_FEATURE_ID} |")

    def edit_shared_section(self, body: str = "Cuerpo compartido editado del fixture.") -> None:
        """Edita el cuerpo de una sección compartida (parte `shared`)."""
        self._edit_plan(SHARED_PREVAILS_BODY, body)

    def edit_authorization_section(
            self, body: str = "Autoridad editada del fixture.") -> None:
        """Edita la sección que el producto declara como AUTORIZACIÓN (parte
        `shared`, sin efecto de veredicto más allá de `impact`)."""
        self._edit_plan(AUTHORITY_BODY, body)

    def edit_history_only(self,
                          line: str = "- 2026-10-14: nota de historia (registro del fixture).") -> None:
        """Edita SOLO la sección de historia (excluida de la proyección)."""
        self._edit_plan(HISTORY_BODY, HISTORY_BODY + "\n" + line)

    def withdraw_authorization(self) -> None:
        """Retira la autorización: sin la entrada `epic_history` `epic-plan`
        con `approved_by` para el epic activo (marcador `approval pending`)."""
        state = self.state()
        state["epic_history"] = [
            entry for entry in state.get("epic_history", [])
            if entry.get("stage") != "epic-plan"]
        self._write_state(state)

    def restore_authorization(self) -> None:
        """Salida del impedimento (PD-10): el ORQUESTADOR registra una nueva
        aprobación `epic-plan` bajo la HITL (operación existente)."""
        state = self.state()
        state["epic_history"] = [{
            "epic": EPIC_ID,
            "stage": "epic-plan",
            "approved_by": APPROVER,
            "approved_at": "2026-10-14T00:00:00Z",
            "plan_path": PLAN_REL,
            "note": "aprobacion restituida (registro del fixture)",
        }]
        self._write_state(state)

    def revoke_delegation(self) -> None:
        """Revoca la delegación HITL (marcador `state incoherent`)."""
        state = self.state()
        state["hitl_delegation"]["status"] = "revoked"
        state["hitl_delegation"]["revoked_at"] = "2026-10-14T00:00:00Z"
        self._write_state(state)

    # -- oráculos de lectura --------------------------------------------

    def impact_path(self, packet_id: str | None = None) -> Path:
        return self.packet_dir(packet_id) / JOURNAL_NAME

    def impact_files(self) -> list[Path]:
        return sorted(self.root.glob(f".cdad/packets/*/{JOURNAL_NAME}"))

    def baseline_projection_digest(self, packet_id: str | None = None) -> str:
        return sha256_bytes(self.unit_contract_path(packet_id).read_bytes())

    def packets_with_projection(self) -> list[str]:
        base = self.root / ".cdad" / "packets"
        if not base.is_dir():
            return []
        return sorted(
            d.name for d in base.iterdir()
            if (d / "UNIT-CONTRACT.md").is_file())


def make_fixture(tmp_path: Path, plan: str | None = None,
                 name: str = "proj") -> T2Fixture:
    return T2Fixture(tmp_path / name, plan if plan is not None else plan_text())


@pytest.fixture
def fx(tmp_path: Path) -> T2Fixture:
    return T2Fixture(tmp_path, plan_text())


def _no_usage_error(label: str, proc) -> None:
    """El rechazo NO es un error de uso del CLI (subcomando desconocido): es el
    comportamiento del contrato (hoy `validate-unit-contract` no existe)."""
    out = proc.stdout + proc.stderr
    assert USAGE_ERROR_TOKEN not in out, (
        f"{label}: el resultado es un error de uso del CLI "
        f"({USAGE_ERROR_TOKEN!r}), no el comportamiento del contrato "
        f"(hoy el subcomando no existe): {out!r}")


def _out(proc) -> str:
    return proc.stdout + proc.stderr


def _registered(block: dict) -> dict:
    """La línea base declarada, guiando `null` (nunca AttributeError)."""
    return block.get("registered") or {}


def _live(block: dict) -> dict:
    return block.get("live") or {}


def impact_records(journal) -> list[dict]:
    """Todo dict del journal que lleva el par de digests (forma del registro:
    `reason` + `contract_sha256_old` + `contract_sha256_new` + `changed_parts`),
    sea el journal un registro o una colección de registros."""
    found: list[dict] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if "contract_sha256_old" in node and "contract_sha256_new" in node:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(journal)
    return found


def read_journal(fx: T2Fixture, packet_id: str | None = None) -> tuple[dict, bytes]:
    path = fx.impact_path(packet_id)
    assert path.is_file(), (
        "PD-9 violada: el veredicto `impact` debe escribir el registro durable "
        f"en el directorio del paquete de la línea base ({path.relative_to(fx.root)}); "
        "no existe")
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), raw


# ---------------------------------------------------------------- PD-8


def test_pd8_current_when_independent_unit_added_without_effect(fx: T2Fixture) -> None:
    """PD-8 (AC-5): con el paquete del architect DESPACHADO y su proyección
    registrada, AGREGAR una unidad futura INDEPENDIENTE al plan (y registrar la
    edición en la sección de historia) → veredicto `current`; NO se escribe
    ningún registro de impacto; y la recepción del paquete despachado sigue
    dando rc=0 (`semantic_status: pending`).

    RED hoy: `validate-unit-contract` no existe (rc=2 «invalid choice») → falla
    la aserción de rc=0/`current` (AssertionError del contrato).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.dispatch_ok(packet_id)
    fx.edit_plan_add_independent_unit()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-8 violada: agregar una unidad futura independiente NO tiene efecto "
        "(veredicto `current`, rc=0); hoy "
        f"rc={proc.returncode} (subcomando inexistente): {out!r}")
    assert VERDICT_CURRENT in out.lower(), (
        "PD-8 violada: el veredicto debe ser `current`: "
        f"{out!r}")
    assert not fx.impact_files(), (
        "PD-8 violada: `current` NO registra impacto; se encontró "
        f"{[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")

    recv = fx.receive(packet_id)
    assert recv.returncode == 0, (
        "PD-8 violada: `current` no impide nada; la recepción del paquete "
        f"despachado debe seguir dando rc=0: {recv.stdout!r} {recv.stderr!r}")
    receipt = json.loads(recv.stdout)
    assert receipt.get("semantic_status") == "pending", (
        f"PD-8 violada: el recibo conserva `semantic_status: pending`: {receipt!r}")


def test_pd8_current_when_only_history_edited(fx: T2Fixture) -> None:
    """PD-8 (AC-5): editar SOLO la sección de historia del plan (excluida de la
    proyección) → veredicto `current`, sin registro de impacto.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de
    rc=0/`current`.
    """
    fx.prepare_ok()
    fx.edit_history_only()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-8 violada: editar la historia no tiene efecto (veredicto "
        f"`current`, rc=0); hoy rc={proc.returncode}: {out!r}")
    assert VERDICT_CURRENT in out.lower(), (
        f"PD-8 violada: el veredicto debe ser `current`: {out!r}")
    assert not fx.impact_files(), (
        "PD-8 violada: `current` NO registra impacto: "
        f"{[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")


# ---------------------------------------------------------------- PD-9


def test_pd9_impact_when_unit_scope_changes_with_durable_record(fx: T2Fixture) -> None:
    """PD-9 (AC-5): al cambiar la parte `unit` (el ALCANCE de la fila de la
    unidad activa) el veredicto es `impact`: se escribe un registro durable en
    el directorio del paquete de la LÍNEA BASE con la forma del journal
    (`reason`, `contract_sha256_old`, `contract_sha256_new`, `changed_parts`),
    con el digest registrado como `old` y las partes que difieren nombradas. El
    registro NO aprueba, NO cambia el state (la decisión es del orquestador) y
    NO toca la política.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    baseline_digest = fx.baseline_projection_digest(packet_id)
    state_before = fx.state_bytes()
    policy_before = fx.policy_bytes()

    fx.edit_unit_scope()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-9 violada: un cambio de la parte `unit` da `impact` (rc=0); hoy "
        f"rc={proc.returncode} (subcomando inexistente): {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"PD-9 violada: el veredicto debe ser `impact`: {out!r}")

    journal, _ = read_journal(fx, packet_id)
    records = impact_records(journal)
    assert records, (
        "PD-9 violada: el registro durable debe llevar el par "
        f"`contract_sha256_old`/`contract_sha256_new`; journal={journal!r}")
    record = records[0]
    for key in IMPACT_KEYS:
        assert key in record, (
            f"PD-9 violada: el registro durable debe llevar {key!r}: {record!r}")
    assert record["contract_sha256_old"] == baseline_digest, (
        "PD-9 violada: `contract_sha256_old` debe ser el digest de la "
        f"proyección REGISTRADA (la línea base): {record['contract_sha256_old']!r} "
        f"!= {baseline_digest!r}")
    assert record["contract_sha256_new"] != baseline_digest, (
        "PD-9 violada: `contract_sha256_new` debe ser el digest de la "
        f"proyección VIVA (distinto): {record['contract_sha256_new']!r}")
    assert record["reason"], (
        f"PD-9 violada: el registro durable debe llevar `reason`: {record!r}")
    assert record["changed_parts"], (
        "PD-9 violada: `changed_parts` debe nombrar las partes que difieren: "
        f"{record!r}")
    assert "unit" in json.dumps(record["changed_parts"]).lower(), (
        "PD-9 violada: al cambiar la fila de la unidad, la parte que difiere es "
        f"la parte `unit`: {record['changed_parts']!r}")

    assert fx.state_bytes() == state_before, (
        "PD-9/INV-1 violada: el registro de impacto NO aprueba ni cambia el "
        "state (la decisión de reconciliación es del orquestador)")
    assert fx.policy_bytes() == policy_before, (
        "PD-9 violada: la operación de veredicto no toca la política")


def test_pd9_impact_when_unit_dependency_changes(fx: T2Fixture) -> None:
    """PD-9 (AC-5): al cambiar una DEPENDENCIA de la fila de la unidad activa
    (parte `unit`) el veredicto es `impact` con el registro durable (parte
    `unit` nombrada).

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.edit_unit_dependency()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-9 violada: un cambio de dependencia de la unidad da `impact` "
        f"(rc=0); hoy rc={proc.returncode}: {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"PD-9 violada: el veredicto debe ser `impact`: {out!r}")
    journal, _ = read_journal(fx, packet_id)
    records = impact_records(journal)
    assert records, f"PD-9 violada: registro durable ausente: {journal!r}"
    assert "unit" in json.dumps(records[0]["changed_parts"]).lower(), (
        "PD-9 violada: la parte `unit` debe nombrarse entre las que difieren: "
        f"{records[0]['changed_parts']!r}")


def test_pd9_impact_when_shared_part_changes(fx: T2Fixture) -> None:
    """PD-9 (AC-5): al diferir una parte `shared` (el cuerpo de una sección
    compartida) el veredicto es `impact` con el registro durable que nombra la
    sección que difiere.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.edit_shared_section()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-9 violada: un cambio de una parte `shared` da `impact` (rc=0); "
        f"hoy rc={proc.returncode}: {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"PD-9 violada: el veredicto debe ser `impact`: {out!r}")
    journal, _ = read_journal(fx, packet_id)
    records = impact_records(journal)
    assert records, f"PD-9 violada: registro durable ausente: {journal!r}"
    token = SHARED_PREVAILS_TITLE.lstrip("# ").lower()
    assert token in json.dumps(records[0]["changed_parts"]).lower(), (
        "PD-9 violada: la parte `shared` que difiere debe nombrarse (su "
        f"título {token!r}): {records[0]['changed_parts']!r}")


def test_pd9_impact_does_not_block_reception_of_dispatched_packet(fx: T2Fixture) -> None:
    """PD-9/PD-6 (AC-5): el registro de impacto NO bloquea la recepción del
    paquete ya despachado: tras editar el alcance de la unidad (veredicto
    `impact`), `receive` sigue dando rc=0 con `packet_validation` /
    `identity_validation` `passed` y `semantic_status: pending`.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0 del
    veredicto (la recepción, T1, ya es rc=0).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.dispatch_ok(packet_id)
    fx.edit_unit_scope()

    proc = fx.validate_unit_contract()
    assert proc.returncode == 0, (
        "PD-9 violada: el cambio de alcance da `impact` (rc=0); hoy "
        f"rc={proc.returncode}: {_out(proc)!r}")
    assert VERDICT_IMPACT in _out(proc).lower(), (
        f"PD-9 violada: el veredicto debe ser `impact`: {_out(proc)!r}")

    recv = fx.receive(packet_id)
    assert recv.returncode == 0, (
        "PD-9 violada: el registro de impacto NO bloquea la recepción del "
        f"paquete ya despachado: {recv.stdout!r} {recv.stderr!r}")
    receipt = json.loads(recv.stdout)
    assert receipt.get("packet_validation") == "passed", (
        f"PD-9 violada: `packet_validation` debe ser `passed`: {receipt!r}")
    assert receipt.get("semantic_status") == "pending", (
        f"PD-9 violada: el recibo conserva `semantic_status: pending`: {receipt!r}")


# ---------------------------------------------------------------- PD-8 / PD-10


def test_pd8_pd10_edited_authorization_section_is_impact_never_impeded(fx: T2Fixture) -> None:
    """PD-8/PD-10 (AC-6): editar la sección que el producto declara como
    AUTORIZACIÓN produce `impact` (rc=0) y NUNCA `impeded` (rc=2): ninguna
    sección del plan produce `impeded`; lo único que lo produce es retirar la
    autorización del state. El registro durable nombra la sección.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.edit_authorization_section()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-8/PD-10 violada: editar la sección de autorización da `impact` "
        f"(rc=0), nunca `impeded` (rc=2); hoy rc={proc.returncode}: {out!r}")
    assert proc.returncode != 2, (
        f"PD-10 violada: ninguna sección del plan produce `impeded`: {out!r}")
    assert VERDICT_IMPEDED not in out.lower(), (
        f"PD-10 violada: la edición de autorización NO produce `impeded`: {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"PD-8 violada: el veredicto debe ser `impact`: {out!r}")
    journal, _ = read_journal(fx, packet_id)
    records = impact_records(journal)
    assert records, f"PD-9 violada: registro durable ausente: {journal!r}"
    assert "autoridad" in json.dumps(records[0]["changed_parts"]).lower(), (
        "PD-9 violada: la parte de autorización que difiere debe nombrarse: "
        f"{records[0]['changed_parts']!r}")


# ---------------------------------------------------------------- PD-10


def test_pd10_impeded_when_epic_plan_approval_retired_with_exit(fx: T2Fixture) -> None:
    """PD-10 (AC-6): retirar la autorización (sin la entrada `epic_history`
    `epic-plan` con `approved_by`) → veredicto `impeded` con rc=2, el marcador
    existente `approval pending` y la SALIDA nombrada (registrar la aprobación
    `epic-plan`). La salida funciona con mecanismos existentes: registrar la
    aprobación → `prepare` rc=0 y el paquete nuevo publica la proyección nueva,
    que pasa a ser la LÍNEA BASE del veredicto siguiente.

    RED hoy: `validate-unit-contract` no existe → el rc=2 es el error de uso
    (no el rechazo de dominio) y no hay marcador ni salida → fallan las
    aserciones de contrato (AssertionError).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.withdraw_authorization()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 2, (
        "PD-10 violada: autorización retirada → `impeded` rc=2 (falla "
        f"cerrado); hoy rc={proc.returncode}: {out!r}")
    _no_usage_error("PD-10 (aprobación retirada)", proc)
    assert VERDICT_IMPEDED in out.lower(), (
        f"PD-10 violada: el veredicto debe ser `impeded`: {out!r}")
    assert MARKER_APPROVAL_PENDING in out.lower(), (
        "PD-10 violada: debe usarse el marcador EXISTENTE "
        f"({MARKER_APPROVAL_PENDING!r}): {out!r}")
    assert "epic-plan" in out, (
        "PD-10 violada: el diagnóstico debe nombrar la SALIDA (registrar la "
        f"aprobación `epic-plan`): {out!r}")
    assert not fx.impact_files(), (
        "PD-10 violada: `impeded` falla cerrado SIN efectos (no escribe el "
        f"journal): {[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")

    # La salida con mecanismos existentes: el orquestador registra la
    # aprobación `epic-plan` y completa el paquete entre subetapas.
    fx.restore_authorization()
    fx.clear_active_packet()
    new_prepare = fx.prepare(substage="draft")
    assert new_prepare.returncode == 0, (
        "PD-10 violada: con la autorización restituida, `prepare` debe dar "
        f"rc=0: {new_prepare.stdout!r} {new_prepare.stderr!r}")
    new_packet_id = fx.packet_id()
    assert new_packet_id != packet_id, (
        "PD-10 violada: el paquete nuevo debe ser un paquete NUEVO "
        f"(distinto de {packet_id!r}): {new_packet_id!r}")

    block = fx.status_block()
    registered = _registered(block)
    assert registered.get("packet_id") == new_packet_id, (
        "PD-7/PD-10 violada: el paquete nuevo publica la proyección nueva, que "
        "pasa a ser la LÍNEA BASE del veredicto siguiente "
        f"(registered.packet_id == {new_packet_id!r}): {block!r}")
    assert registered.get("sha256") == fx.baseline_projection_digest(new_packet_id), (
        "PD-7 violada: `registered.sha256` debe ser el digest de la proyección "
        f"registrada del paquete nuevo: {block!r}")


def test_pd10_impeded_when_hitl_delegation_revoked_with_exit(fx: T2Fixture) -> None:
    """PD-10 (AC-6): con la delegación HITL revocada → veredicto `impeded` con
    rc=2, el marcador existente `state incoherent` y la SALIDA nombrada
    (restituir la delegación / registrar la aprobación `epic-plan`), sin
    escribir el journal.

    RED hoy: `validate-unit-contract` no existe → el rc=2 es el error de uso y
    no hay marcador → fallan las aserciones de contrato (AssertionError).
    """
    fx.prepare_ok()
    fx.revoke_delegation()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 2, (
        "PD-10 violada: delegación revocada → `impeded` rc=2 (falla cerrado); "
        f"hoy rc={proc.returncode}: {out!r}")
    _no_usage_error("PD-10 (delegación revocada)", proc)
    assert VERDICT_IMPEDED in out.lower(), (
        f"PD-10 violada: el veredicto debe ser `impeded`: {out!r}")
    assert MARKER_STATE_INCOHERENT in out.lower(), (
        "PD-10 violada: debe usarse el marcador EXISTENTE "
        f"({MARKER_STATE_INCOHERENT!r}): {out!r}")
    assert ("delegation" in out.lower() or "delegacion" in out.lower()
            or "epic-plan" in out.lower()), (
        "PD-10 violada: el diagnóstico debe nombrar la SALIDA (restituir la "
        f"delegación / registrar la aprobación `epic-plan`): {out!r}")
    assert not fx.impact_files(), (
        "PD-10 violada: `impeded` falla cerrado SIN efectos (no escribe el "
        f"journal): {[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")


# ---------------------------------------------------------------- PD-7


def test_pd7_baseline_is_the_most_recent_packet_of_the_unit(fx: T2Fixture) -> None:
    """PD-7 (AC-5): la línea base es la proyección REGISTRADA del ÚLTIMO
    paquete de la unidad. Con dos paquetes sucesivos de la unidad (discovery y
    draft), tras editar la fila de la unidad el veredicto compara contra el
    paquete MÁS RECIENTE: el journal se escribe en su directorio y el veredicto
    lo declara (`registered.packet_id` / `registered.sha256`).

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    first_packet = fx.packet_id()
    fx.second_packet_of_the_unit("draft")
    second_packet = fx.packet_id()
    assert second_packet != first_packet, (
        "precondición (fixture): deben existir dos paquetes de la unidad")
    assert set(fx.packets_with_projection()) == {first_packet, second_packet}, (
        "precondición (fixture): los dos paquetes deben tener proyección "
        f"registrada: {fx.packets_with_projection()!r}")

    fx.edit_unit_scope()

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-7 violada: el veredicto debe emitirse (rc=0); hoy "
        f"rc={proc.returncode}: {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"PD-7 violada: el veredicto debe ser `impact`: {out!r}")
    assert fx.impact_path(second_packet).is_file(), (
        "PD-7 violada: la línea base es el paquete MÁS RECIENTE de la unidad; "
        "el journal debe escribirse en su directorio "
        f"({fx.impact_path(second_packet).relative_to(fx.root)}); no existe")
    assert not fx.impact_path(first_packet).exists(), (
        "PD-7 violada: el journal NO debe escribirse en el directorio del "
        f"paquete anterior ({fx.impact_path(first_packet).relative_to(fx.root)})")

    block = fx.status_block()
    registered = _registered(block)
    assert registered.get("packet_id") == second_packet, (
        "PD-7 violada: la línea base se declara y es el paquete más reciente "
        f"({second_packet!r}): {block!r}")
    assert registered.get("sha256") == fx.baseline_projection_digest(second_packet), (
        "PD-7 violada: `registered.sha256` debe ser el digest de la proyección "
        f"registrada del paquete más reciente: {block!r}")


def test_pd7_no_registered_projection_yields_current(fx: T2Fixture) -> None:
    """PD-7 (AC-5): si la unidad NO tiene ningún paquete con proyección
    registrada, no hay línea base y el veredicto es `current` (nada que
    comparar), sin registro de impacto.

    El fixture lleva el proyecto al estado PREVIO al primer paquete de la
    unidad (la ejecución queda publicada — `validate-state` sigue verde — y no
    hay ningún paquete): es una mutación declarada del fixture, no un state
    inválido.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    fx.clear_active_packet()
    shutil.rmtree(fx.root / ".cdad" / "packets")
    assert fx.packets_with_projection() == [], (
        "precondición (fixture): no debe haber paquetes con proyección")

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "PD-7 violada: sin línea base el veredicto es `current` (rc=0); hoy "
        f"rc={proc.returncode}: {out!r}")
    assert VERDICT_CURRENT in out.lower(), (
        f"PD-7 violada: sin paquete con proyección el veredicto es `current`: {out!r}")
    assert not fx.impact_files(), (
        "PD-7 violada: sin línea base no se registra impacto: "
        f"{[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")
    registered = _registered(fx.status_block())
    assert registered.get("packet_id") is None, (
        f"PD-7 violada: no hay línea base declarada: {fx.status_block()!r}")


# ---------------------------------------------------------------- PD-11


def test_pd11_status_informs_verdict_and_writes_nothing(fx: T2Fixture) -> None:
    """PD-11 (AC-7, P1): el bloque ADITIVO `unit_contract` de la vista INFORMA
    `mode`, la línea base, el digest vivo, el veredicto, las partes que
    difieren y el motivo, y NO escribe nada: dos `status` consecutivos dejan el
    proyecto BYTE A BYTE idéntico (state, paquetes y ausencia de `.impact.json`).
    La vista conserva sus campos existentes (ninguno se relaja).

    RED hoy: el bloque informa `registered: null`, `live: null` y
    `verdict: null` → fallan las aserciones de contenido (AssertionError); la
    byte-identidad ya se cumple (guardia).
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()
    fx.edit_unit_scope()

    before = fx.snapshot()
    first = fx.status()
    second = fx.status()
    assert first.returncode == 0 and second.returncode == 0, (
        "precondición (fixture): `status` debe emitir (rc=0): "
        f"{first.stderr!r} {second.stderr!r}")
    assert fx.snapshot() == before, (
        "PD-11 violada: `status` es de SOLO LECTURA; dos `status` consecutivos "
        "deben dejar el proyecto byte a byte idéntico (state, paquetes)")
    assert not fx.impact_files(), (
        "PD-11 violada: `status` nunca crea el journal de impacto: "
        f"{[str(p.relative_to(fx.root)) for p in fx.impact_files()]!r}")

    doc = fx.status_doc()
    for key in REQUIRED_TOP:
        assert key in doc, (
            f"PD-11 violada: la vista conserva el campo existente {key!r} "
            f"(el bloque `unit_contract` es aditivo): {sorted(doc)!r}")
    block = doc.get("unit_contract") or {}
    assert block.get("mode") == "projection", (
        f"PD-11 violada: `unit_contract.mode` debe informar `projection`: {block!r}")
    assert block.get("unit") == FEATURE_ID, (
        f"PD-11 violada: `unit_contract.unit` debe informar la unidad activa: {block!r}")
    registered = _registered(block)
    assert registered.get("packet_id") == packet_id, (
        f"PD-11 violada: el bloque debe informar la línea base: {block!r}")
    assert registered.get("sha256") == fx.baseline_projection_digest(packet_id), (
        f"PD-11 violada: el bloque debe informar el digest registrado: {block!r}")
    live = _live(block)
    assert HEX64.fullmatch(str(live.get("sha256") or "")), (
        f"PD-11 violada: el bloque debe informar el digest vivo: {block!r}")
    assert live["sha256"] != registered.get("sha256"), (
        "PD-11 violada: el digest vivo difiere del registrado (la fila de la "
        f"unidad cambió): {block!r}")
    assert block.get("verdict") == VERDICT_IMPACT, (
        f"PD-11 violada: el bloque debe informar el veredicto: {block!r}")
    assert block.get("changed_parts"), (
        f"PD-11 violada: el bloque debe informar las partes que difieren: {block!r}")
    assert "unit" in json.dumps(block["changed_parts"]).lower(), (
        f"PD-11 violada: la parte `unit` difiere: {block['changed_parts']!r}")
    assert block.get("reason"), (
        f"PD-11 violada: el bloque debe informar el motivo: {block!r}")


# ---------------------------------------------------------------- PD-9 / P1


def test_pd9_journal_is_idempotent_for_same_digest_pair(fx: T2Fixture) -> None:
    """PD-9 (AC-7, P1): el journal de impacto es IDEMPOTENTE. Dos corridas de
    la operación de veredicto con el MISMO par de digests dejan el journal
    BYTE A BYTE idéntico (sin registro duplicado); un par distinto agrega un
    registro nuevo sin pisar el anterior.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    packet_id = fx.packet_id()

    fx.edit_unit_scope()
    first = fx.validate_unit_contract()
    assert first.returncode == 0, (
        "PD-9 violada: el veredicto debe emitirse (rc=0); hoy "
        f"rc={first.returncode}: {_out(first)!r}")
    journal_1, bytes_1 = read_journal(fx, packet_id)

    second = fx.validate_unit_contract()
    assert second.returncode == 0, (
        f"PD-9 violada: la repetición debe emitirse (rc=0): {_out(second)!r}")
    _, bytes_2 = read_journal(fx, packet_id)
    assert bytes_2 == bytes_1, (
        "PD-9 violada: con el MISMO par de digests, correr la operación de "
        "nuevo NO duplica el registro (journal byte a byte idéntico)")

    # Un par distinto (otra edición) agrega un registro nuevo.
    records_1 = impact_records(journal_1)
    assert records_1, f"PD-9 violada: registro durable ausente: {journal_1!r}"
    first_new_digest = records_1[0]["contract_sha256_new"]

    fx.edit_shared_section()
    third = fx.validate_unit_contract()
    assert third.returncode == 0, (
        f"PD-9 violada: el segundo veredicto debe emitirse (rc=0): {_out(third)!r}")
    journal_3, bytes_3 = read_journal(fx, packet_id)
    assert bytes_3 != bytes_1, (
        "PD-9 violada: un par de digests distinto debe agregar un registro "
        "nuevo (journal distinto)")
    records_3 = impact_records(journal_3)
    assert len(records_3) >= 2, (
        "PD-9 violada: un par distinto agrega un registro nuevo (no pisa el "
        f"anterior): registros={records_3!r}")
    new_digests = {record.get("contract_sha256_new") for record in records_3}
    assert first_new_digest in new_digests, (
        "PD-9 violada: el registro anterior NO debe pisarse: "
        f"{first_new_digest!r} no está en {new_digests!r}")
    assert any(digest != first_new_digest for digest in new_digests), (
        f"PD-9 violada: falta el registro del par nuevo: {new_digests!r}")


# ---------------------------------------------------------------- INV-8 / INV-1


def test_inv8_restrictive_prose_is_impact_never_impeded(fx: T2Fixture) -> None:
    """PD-10/INV-8: el CLI NO decide la inmediatez de una restricción por
    prosa (no hay listas de palabras). Una parte `shared` cuya prosa se lee
    como «de aplicación inmediata» da `impact` (registra el impacto y decide el
    orquestador), NUNCA `impeded` (lo único que produce `impeded` es retirar la
    autorización del state).

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    fx.edit_shared_section(
        "Restriccion del fixture: de aplicacion inmediata (registro del fixture).")

    proc = fx.validate_unit_contract()
    out = _out(proc)
    assert proc.returncode == 0, (
        "INV-8/PD-10 violada: la prosa restrictiva de una parte `shared` da "
        f"`impact` (rc=0), nunca `impeded`; hoy rc={proc.returncode}: {out!r}")
    assert VERDICT_IMPEDED not in out.lower(), (
        "INV-8/PD-10 violada: el CLI no clasifica la inmediatez por prosa "
        f"(sin listas de palabras): {out!r}")
    assert VERDICT_IMPACT in out.lower(), (
        f"INV-8 violada: el veredicto debe ser `impact`: {out!r}")


def test_inv1_inv9_verdict_does_not_write_state_nor_policy(fx: T2Fixture) -> None:
    """PD-11/INV-1/INV-9: la operación de veredicto NO escribe el state (la
    decisión del orquestador va a la nota de `stage_history`, que el CLI no
    toca) ni la política; su único efecto, en `impact`, es el registro durable.

    RED hoy: `validate-unit-contract` no existe → falla la aserción de rc=0.
    """
    fx.prepare_ok()
    fx.edit_unit_scope()
    state_before = fx.state_bytes()
    policy_before = fx.policy_bytes()
    stage_history_before = json.loads(state_before)["stage_history"]

    proc = fx.validate_unit_contract()
    assert proc.returncode == 0, (
        f"PD-11 violada: el veredicto debe emitirse (rc=0): {_out(proc)!r}")
    assert fx.state_bytes() == state_before, (
        "INV-1/INV-9 violada: la operación de veredicto NO escribe el state "
        "(la decisión del orquestador va a la nota de `stage_history`)")
    assert json.loads(fx.state_bytes())["stage_history"] == stage_history_before, (
        "INV-1 violada: el CLI no escribe `stage_history` (no aprueba nada)")
    assert fx.policy_bytes() == policy_before, (
        "PD-11 violada: la operación de veredicto no toca la política")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
