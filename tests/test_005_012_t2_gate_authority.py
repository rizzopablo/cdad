#!/usr/bin/env python3
"""005-012 T2 RED — la clase `gate` del subcomando `register-transition`:
el pin de contrato/plan verificado contra los bytes (digest DERIVADO cuando no
se afirma, PD-20) y la **autoridad** en sus **tres casos** (PD-6, la corrección
P2 de la review del orquestador).

Contract:
- docs/specs/005-012-transition-registration/spec.md §2.1 (superficie CLI y
  digests derivados/opcionales), §2.2 (forma aditiva del registro y campos
  derivados de la clase `gate`), §2.3 (postcondiciones PD-5, PD-6, PD-10,
  PD-20), §2.4 (invariantes INV-3, INV-7), §3 (frontera del juicio).
- docs/specs/005-012-transition-registration/plan.md §4 ficha T2 (test focal
  declarado `tests/test_005_012_t2_gate_authority.py`).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI del
repo; el módulo de implementación NUNCA se importa y su código NUNCA se lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
        --project-root <ABS> --transition gate --stage <token> \
        --approve-by <texto> [--contract-path <p>] [--contract-sha256 <hex>] \
        [--plan-path <p>] [--plan-sha256 <hex>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>

El subcomando `register-transition` existe (T1 GREEN: `delivery`/`advance`),
pero la clase `gate` NO: HOY el CLI responde con un error de uso (rc=2,
«invalid choice: 'gate'») y ningún efecto sobre el state. Por eso cada test
falla en la ASERCIÓN sobre el comportamiento del contrato (rc esperado, efecto
sobre el state, marcador de rechazo, digests derivados), nunca en la invocación
ni en una precondición de fixture: los fallos RED son AssertionError de
contrato, jamás ImportError, SyntaxError, JSONDecodeError ni error de setup.

Fixture: proyecto descartable en un tempdir (política válida, contrato pineado
en `stage_history`, delegación HITL con `source` existente, ejecución v2 y
paquete reales) construido por el camino legítimo del CLI (`prepare`), con el
`HOME` del subproceso en un tempdir VACÍO (nunca el HOME real, nunca este
repo). Los ids del fixture son sintéticos y anónimos. Las mutaciones de
delegación (revocada / vencida / ausente) que PD-6 declara se aplican sobre el
state del fixture con la forma ya usada por la suite
(`test_004_002_t2_bootstrap.py`, `test_003_004_t2_reviewfix.py`): ningún campo
inventado.

Mapeo test → postcondición:

  test_pd5_gate_registered_with_non_empty_approver
      -> PD-5 + forma §2.2 (+ PD-17): `gate` con `--approve-by` → rc=0, una
         entrada con `transition: "gate"` y `approved_by` NO vacío;
         `validate-state` rc=0 antes y después
  test_pd5_pd20_stage2_gate_derives_contract_and_plan_digests
      -> PD-5 + PD-20: gate de etapa 2 (`--stage specification`) con
         `--contract-path`/`--plan-path` y SIN afirmar digest → rc=0; el CLI
         DERIVA el sha256 de los bytes, lo escribe en la entrada y lo imprime
  test_pd20_asserted_contract_digest_that_matches_is_verified
      -> PD-20: afirmar un `--contract-sha256` que COINCIDE se verifica y se
         acepta (rc=0) y queda escrito
  test_pd5_asserted_contract_digest_divergent_fails_closed
      -> PD-5 / INV-7: `--contract-sha256` afirmado DIVERGENTE → rc=2
         `evidence missing`, sin efectos (state byte a byte idéntico)
  test_pd5_absent_contract_file_fails_closed
      -> PD-5 / INV-7: `--contract-path` con el archivo AUSENTE → rc=2
         `evidence missing`, sin efectos
  test_pd5_asserted_plan_digest_divergent_fails_closed
      -> PD-5 / INV-7: `--plan-sha256` afirmado DIVERGENTE → rc=2
         `evidence missing`, sin efectos
  test_pd5_absent_plan_file_fails_closed
      -> PD-5 / INV-7: `--plan-path` con el archivo AUSENTE → rc=2
         `evidence missing`, sin efectos
  test_pd6_case_a_gate_accepted_with_active_delegation
      -> PD-6 (caso A): con delegación registrada y VIGENTE el `gate` se
         acepta (rc=0) y escribe el aprobador declarado
  test_pd6_case_b_revoked_delegation_fails_closed_approval_pending
      -> PD-6 (caso B, revocada): rc=2 con el marcador `approval pending`,
         nombrando el registro, sin efectos
  test_pd6_case_b_expired_delegation_fails_closed_approval_pending
      -> PD-6 (caso B, vencida por `expires_on`): rc=2 `approval pending`,
         sin efectos
  test_pd6_case_c_without_delegation_registers_declared_approver
      -> PD-6 (caso C, P2): SIN delegación registrada el CLI NO bloquea al
         dueño → rc=0, `approved_by` = aprobador declarado, la salida declara
         que no hubo delegación que verificar
  test_pd6_case_c_active_epic_null_registers_declared_approver
      -> PD-6 (caso C, variante `active_epic: null`): mismo comportamiento
  test_pd10_gate_entry_carries_transition_key
      -> PD-10 (forma de la clase `gate`): la entrada lleva `transition_key`
  test_pd11_identical_gate_repetition_is_noop_byte_identical
      -> PD-11 (clase `gate`): repetir la invocación idéntica → rc=0, sin
         segunda entrada, state byte a byte idéntico y salida que nombra la
         entrada existente
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from test_005_012_t1_register_transition_base import (
    APPROVER,
    AUTHORITY_REF,
    EPIC_ID,
    FEATURE_ID,
    TRANSITION_DIGEST_RE,
    _Fixture as _BaseFixture,
    assert_unchanged,
    entries,
    last_entry_with,
)

# La clase `gate` es la DECISIÓN; `--stage` es la etiqueta (token plano libre).
GATE_STAGE = "tdd-review"
# El gate de etapa 2 pinnea el contrato y el plan (PD-5).
PIN_STAGE = "specification"

# Archivos del fixture para el pin del gate de etapa 2. La ruta es RELATIVA a
# la raíz del proyecto (misma convención que `--contract-path` en el CLI y que
# `stage_history[].contract_path`); se crean bajo `docs/` para no colisionar
# con la entrada `specification` que el fixture ya tiene pinneada.
GATE_CONTRACT_REL = f"docs/specs/{FEATURE_ID}/spec-t2-gate.md"
GATE_PLAN_REL = f"docs/specs/{FEATURE_ID}/plan-t2-gate.md"
GATE_CONTRACT_BYTES = b"# Gate contract fixture (demo-100 T2)\n"
GATE_PLAN_BYTES = b"# Gate plan fixture (demo-100 T2)\n"
ABSENT_CONTRACT_REL = f"docs/specs/{FEATURE_ID}/absent-t2-gate.md"
ABSENT_PLAN_REL = f"docs/specs/{FEATURE_ID}/absent-t2-plan.md"

EVIDENCE_MISSING = "evidence missing"
APPROVAL_PENDING = "approval pending"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _GateFixture(_BaseFixture):
    """Proyecto descartable (misma capa legítima del focal de T1) + las
    mutaciones de autoridad que PD-6 declara.

    La capa previa se produce por el camino legítimo del CLI
    (`prepare` → paquete `prepared`, ejecución v2, delegación activa) en un
    tempdir, con el `HOME` del subproceso aislado. Las mutaciones de
    delegación se aplican después, sobre el state del fixture.
    """

    def __init__(self, base: Path) -> None:
        super().__init__(base, mode="prepared")
        self.gate_contract = self.root / GATE_CONTRACT_REL
        self.gate_plan = self.root / GATE_PLAN_REL
        self.gate_contract.write_bytes(GATE_CONTRACT_BYTES)
        self.gate_plan.write_bytes(GATE_PLAN_BYTES)

    # -- invocación (caja negra) ------------------------------------------

    def gate(self, *extra: str, stage: str = GATE_STAGE,
             approve_by: str = APPROVER) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "gate", "--stage", stage,
            "--approve-by", approve_by, *extra)

    # -- mutaciones declaradas de la delegación (PD-6) --------------------

    def delegation(self) -> dict | None:
        return self.read_state().get("hitl_delegation")

    def revoke_delegation(self) -> None:
        """Delegación REVOCADA (forma de la suite: `status: revoked` +
        `revoked_at`)."""
        state = self.read_state()
        state["hitl_delegation"] = {
            "status": "revoked",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "revoked_at": "2026-10-14T12:00:00Z",
        }
        self.write_state(state)

    def expire_delegation(self) -> None:
        """Delegación VENCIDA por su `expires_on` (fecha en el pasado; forma
        ya usada por la suite: `test_003_004_t2_reviewfix.py`)."""
        state = self.read_state()
        state["hitl_delegation"] = {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "expires_on": "2020-01-01",
        }
        self.write_state(state)

    def remove_delegation(self, *, epic_null: bool = False) -> None:
        """SIN registro `hitl_delegation` (la corrección P2). Con
        `epic_null=True` además `active_epic: null` (la variante que PD-6
        declara idéntica)."""
        state = self.read_state()
        state["hitl_delegation"] = None
        if epic_null:
            state["active_epic"] = None
            state["epic_stage"] = None
        self.write_state(state)


@pytest.fixture
def gate_fx(tmp_path: Path) -> _GateFixture:
    return _GateFixture(tmp_path)


# ---------------------------------------------------------------- PD-5


def test_pd5_gate_registered_with_non_empty_approver(
        gate_fx: _GateFixture) -> None:
    """PD-5 (+ forma §2.2, + aditividad PD-17): `--transition gate --stage
    <token> --approve-by <texto>` → rc=0; se agrega UNA entrada de
    `stage_history` que declara `transition: "gate"` y `approved_by` NO vacío
    (el aprobador declarado); `validate-state` → rc=0 antes y después.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción del efecto
    (AssertionError de contrato).
    """
    assert gate_fx.validate_state().returncode == 0, (
        "precondición (fixture): el state del fixture debe ser coherente hoy "
        "(validate-state rc=0) ANTES de la operación")
    before = gate_fx.read_state()

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-5 violada: `gate` con `--approve-by` debe registrarse (rc=0); "
        f"hoy rc={proc.returncode}: {out!r}")
    state = gate_fx.read_state()
    assert len(entries(state)) == len(entries(before)) + 1, (
        "PD-5 violada: el gate debe dejar la traza como UNA entrada nueva "
        f"(antes {len(entries(before))}, después {len(entries(state))})")
    entry = last_entry_with(state, transition="gate")
    assert entry is not None, (
        "PD-5 violada: no hay entrada con `transition: \"gate\"` en "
        f"`stage_history`: {entries(state)!r}")
    assert entry.get("stage") == GATE_STAGE, (
        "PD-5/§2.2 violada: la entrada debe llevar la etiqueta declarada en "
        f"`--stage` ({GATE_STAGE!r}): {entry!r}")
    declared = entry.get("approved_by")
    assert isinstance(declared, str) and declared.strip(), (
        "PD-5 violada: la entrada de `gate` debe llevar `approved_by` NO "
        f"vacío (el aprobador declarado): {entry!r}")
    assert declared == APPROVER, (
        "PD-5 violada: `approved_by` debe ser el aprobador declarado en "
        f"`--approve-by` ({APPROVER!r}): {declared!r}")
    assert gate_fx.validate_state().returncode == 0, (
        "PD-5/PD-17 violada: `validate-state` debe quedar rc=0 sobre el state "
        "resultante")


def test_pd5_pd20_stage2_gate_derives_contract_and_plan_digests(
        gate_fx: _GateFixture) -> None:
    """PD-5 + PD-20: el gate de etapa 2 (`--stage specification`) con
    `--contract-path` y `--plan-path` y SIN afirmar ningún digest → rc=0; el
    CLI DERIVA el `sha256` de los bytes actuales de cada archivo, lo ESCRIBE
    en la entrada y lo IMPRIME en la salida.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción del efecto.
    """
    derived_contract = _sha256(GATE_CONTRACT_BYTES)
    derived_plan = _sha256(GATE_PLAN_BYTES)

    proc = gate_fx.gate(
        "--contract-path", GATE_CONTRACT_REL,
        "--plan-path", GATE_PLAN_REL,
        stage=PIN_STAGE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-5 violada: el gate de etapa 2 con el pin de contrato y plan sin "
        f"afirmar ningún digest debe aceptarse (rc=0); hoy rc="
        f"{proc.returncode}: {out!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-5 violada: no hay entrada con `transition: \"gate\"` en "
        "`stage_history`")
    assert entry.get("contract_path") == GATE_CONTRACT_REL, (
        "PD-5 violada: la entrada debe llevar el `contract_path` citado "
        f"({GATE_CONTRACT_REL!r}): {entry.get('contract_path')!r}")
    assert entry.get("contract_sha256") == derived_contract, (
        "PD-20 violada: sin `--contract-sha256`, el digest del contrato debe "
        "DERIVARSE de los bytes actuales y escribirse en la entrada; "
        f"esperado {derived_contract!r}, entrada "
        f"{entry.get('contract_sha256')!r}")
    assert entry.get("plan_path") == GATE_PLAN_REL, (
        "PD-5 violada: la entrada debe llevar el `plan_path` citado "
        f"({GATE_PLAN_REL!r}): {entry.get('plan_path')!r}")
    assert entry.get("plan_sha256") == derived_plan, (
        "PD-20 violada: sin `--plan-sha256`, el digest del plan debe "
        "DERIVARSE de los bytes actuales y escribirse en la entrada; "
        f"esperado {derived_plan!r}, entrada {entry.get('plan_sha256')!r}")
    assert derived_contract in out and derived_plan in out, (
        "PD-20 violada: la salida debe IMPRIMIR los digests usados "
        "(derivados) para que la entrada quede auditable; "
        f"contrato {derived_contract!r} en salida={derived_contract in out}, "
        f"plan {derived_plan!r} en salida={derived_plan in out}: {out!r}")
    assert gate_fx.validate_state().returncode == 0, (
        "PD-5 violada: `validate-state` debe quedar rc=0 sobre el state "
        "resultante")


def test_pd20_asserted_contract_digest_that_matches_is_verified(
        gate_fx: _GateFixture) -> None:
    """PD-20: afirmar un `--contract-sha256` que COINCIDE con los bytes
    actuales se VERIFICA y se acepta (rc=0), y el digest verificado queda
    escrito en la entrada. La aserción opcional no puede rechazar por defecto.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción del efecto.
    """
    derived = _sha256(GATE_CONTRACT_BYTES)

    proc = gate_fx.gate(
        "--contract-path", GATE_CONTRACT_REL,
        "--contract-sha256", derived,
        stage=PIN_STAGE)

    assert proc.returncode == 0, (
        "PD-20 violada: un `--contract-sha256` afirmado que coincide con los "
        f"bytes debe verificarse y aceptarse (rc=0); rc={proc.returncode}: "
        f"{proc.stdout!r} {proc.stderr!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-20 violada: no hay entrada con `transition: \"gate\"` en "
        "`stage_history`")
    assert entry.get("contract_sha256") == derived, (
        "PD-20 violada: el digest verificado debe quedar escrito en la "
        f"entrada: esperado {derived!r}, entrada "
        f"{entry.get('contract_sha256')!r}")


def test_pd5_asserted_contract_digest_divergent_fails_closed(
        gate_fx: _GateFixture) -> None:
    """PD-5 / INV-7: un `--contract-sha256` AFIRMADO distinto del digest de
    los bytes actuales → rc=2, marcador `evidence missing`, SIN efectos (state
    byte a byte idéntico).

    RED hoy: rc=2 por error de uso del CLI (no es el rechazo del contrato) →
    falla la aserción del marcador.
    """
    before = gate_fx.state_bytes()
    wrong = "f" * 64
    assert wrong != _sha256(GATE_CONTRACT_BYTES), (
        "precondición (fixture): el digest afirmado diverge de los bytes")

    proc = gate_fx.gate(
        "--contract-path", GATE_CONTRACT_REL,
        "--contract-sha256", wrong,
        stage=PIN_STAGE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-5 violada: un `--contract-sha256` afirmado divergente debe fallar "
        f"cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-5 violada: el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert_unchanged(gate_fx, before, "PD-5",
                     "digest de contrato afirmado divergente")


def test_pd5_absent_contract_file_fails_closed(gate_fx: _GateFixture) -> None:
    """PD-5 / INV-7: el gate de etapa 2 con un `--contract-path` cuyo archivo
    está AUSENTE → rc=2, marcador `evidence missing`, SIN efectos (state byte a
    byte idéntico).

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    before = gate_fx.state_bytes()
    assert not (gate_fx.root / ABSENT_CONTRACT_REL).exists(), (
        "precondición (fixture): el contrato citado NO debe existir")

    proc = gate_fx.gate("--contract-path", ABSENT_CONTRACT_REL,
                        stage=PIN_STAGE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-5 violada: un `--contract-path` ausente debe fallar cerrado "
        f"(rc=2); rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-5 violada: el archivo ausente debe fallar con el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert_unchanged(gate_fx, before, "PD-5", "contrato ausente")


def test_pd5_asserted_plan_digest_divergent_fails_closed(
        gate_fx: _GateFixture) -> None:
    """PD-5 / INV-7: un `--plan-sha256` AFIRMADO distinto del digest de los
    bytes actuales (con el contrato válido) → rc=2, marcador `evidence
    missing`, SIN efectos.

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    before = gate_fx.state_bytes()
    wrong = "0" * 64
    assert wrong != _sha256(GATE_PLAN_BYTES), (
        "precondición (fixture): el digest afirmado diverge de los bytes")

    proc = gate_fx.gate(
        "--contract-path", GATE_CONTRACT_REL,
        "--plan-path", GATE_PLAN_REL,
        "--plan-sha256", wrong,
        stage=PIN_STAGE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-5 violada: un `--plan-sha256` afirmado divergente debe fallar "
        f"cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-5 violada: el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert_unchanged(gate_fx, before, "PD-5", "digest de plan afirmado divergente")


def test_pd5_absent_plan_file_fails_closed(gate_fx: _GateFixture) -> None:
    """PD-5 / INV-7: el gate de etapa 2 con un `--plan-path` cuyo archivo está
    AUSENTE (con el contrato válido) → rc=2, marcador `evidence missing`, SIN
    efectos.

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    before = gate_fx.state_bytes()
    assert not (gate_fx.root / ABSENT_PLAN_REL).exists(), (
        "precondición (fixture): el plan citado NO debe existir")

    proc = gate_fx.gate(
        "--contract-path", GATE_CONTRACT_REL,
        "--plan-path", ABSENT_PLAN_REL,
        stage=PIN_STAGE)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-5 violada: un `--plan-path` ausente debe fallar cerrado (rc=2); "
        f"rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-5 violada: el plan ausente debe fallar con el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert_unchanged(gate_fx, before, "PD-5", "plan ausente")


# ---------------------------------------------------------------- PD-6


def test_pd6_case_a_gate_accepted_with_active_delegation(
        gate_fx: _GateFixture) -> None:
    """PD-6 (caso A): con una delegación registrada y VIGENTE (no revocada ni
    vencida, con `source` resoluble a un archivo existente) su vigencia se
    verifica y el `gate` se ACEPTA (rc=0), escribiendo el aprobador declarado.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción del efecto.
    """
    delegation = gate_fx.delegation()
    assert delegation is not None, (
        "precondición (fixture): el fixture debe tener una delegación "
        "registrada para el caso A")
    assert delegation.get("status") == "active", (
        "precondición (fixture): la delegación debe estar `active`: "
        f"{delegation!r}")
    assert (gate_fx.root / delegation["source"]).is_file(), (
        "precondición (fixture): el `source` de la delegación debe ser "
        f"resoluble a un archivo existente: {delegation.get('source')!r}")

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-6 violada (caso A): con la delegación vigente el `gate` debe "
        f"aceptarse (rc=0); rc={proc.returncode}: {out!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-6 violada (caso A): no hay entrada con `transition: \"gate\"`")
    assert entry.get("approved_by") == APPROVER, (
        "PD-6 violada (caso A): el aprobador declarado debe quedar escrito: "
        f"{entry.get('approved_by')!r}")


def test_pd6_case_b_revoked_delegation_fails_closed_approval_pending(
        gate_fx: _GateFixture) -> None:
    """PD-6 (caso B, REVOCADA): con la delegación revocada (`status:
    "revoked"` + `revoked_at`) el `gate` falla cerrado → rc=2, marcador
    `approval pending`, nombrando el registro, y SIN efectos (state byte a byte
    idéntico).

    RED hoy: rc=2 por error de uso (no es el rechazo del contrato) → falla la
    aserción del marcador.
    """
    gate_fx.revoke_delegation()
    assert gate_fx.delegation().get("status") == "revoked", (
        "precondición (fixture): la delegación debe quedar revocada")
    before = gate_fx.state_bytes()

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-6 violada (caso B, revocada): la delegación revocada debe fallar "
        f"cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert APPROVAL_PENDING in out.lower(), (
        "PD-6 violada (caso B, revocada): el fallo cerrado de la autoridad "
        f"debe llevar el marcador «{APPROVAL_PENDING}»: {out!r}")
    assert ("delegation" in out.lower()) or (EPIC_ID in out), (
        "PD-6 violada (caso B, revocada): el diagnóstico debe NOMBRAR el "
        f"registro de autoridad que no es vigente: {out!r}")
    assert_unchanged(gate_fx, before, "PD-6", "B (delegación revocada)")


def test_pd6_case_b_expired_delegation_fails_closed_approval_pending(
        gate_fx: _GateFixture) -> None:
    """PD-6 (caso B, VENCIDA por su `expires_on`): con la delegación vencida el
    `gate` falla cerrado → rc=2, marcador `approval pending`, nombrando el
    registro, y SIN efectos (state byte a byte idéntico).

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    gate_fx.expire_delegation()
    assert gate_fx.delegation().get("expires_on") == "2020-01-01", (
        "precondición (fixture): la delegación debe quedar vencida")
    before = gate_fx.state_bytes()

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-6 violada (caso B, vencida): la delegación vencida debe fallar "
        f"cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert APPROVAL_PENDING in out.lower(), (
        "PD-6 violada (caso B, vencida): el fallo cerrado de la autoridad debe "
        f"llevar el marcador «{APPROVAL_PENDING}»: {out!r}")
    assert ("delegation" in out.lower()) or (EPIC_ID in out), (
        "PD-6 violada (caso B, vencida): el diagnóstico debe NOMBRAR el "
        f"registro de autoridad que no es vigente: {out!r}")
    assert_unchanged(gate_fx, before, "PD-6", "B (delegación vencida)")


def test_pd6_case_c_without_delegation_registers_declared_approver(
        gate_fx: _GateFixture) -> None:
    """PD-6 (caso C — corrección P2): SIN registro `hitl_delegation`, el CLI no
    inventa autoridad ni puede verificar identidades: NO bloquea al dueño (la
    autoridad original) → rc=0, registra el aprobador declarado (`--approve-by`)
    en la entrada y la salida DECLARA que no hubo delegación que verificar.

    (El límite del *estado* —con epic activo y sin delegación— sigue siendo la
    deuda D-10 que la spec declara; por eso este caso NO asertá `validate-state`
    sobre el state del fixture, sólo el comportamiento de la OPERACIÓN.)

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción de aceptación.
    """
    gate_fx.remove_delegation()
    assert gate_fx.delegation() is None, (
        "precondición (fixture): el state NO debe tener delegación registrada")

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-6 violada (caso C, sin delegación — P2): el dueño es la autoridad "
        "original y el `gate` NO debe bloquearse (rc=0); rc="
        f"{proc.returncode}: {out!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-6 violada (caso C): no hay entrada con `transition: \"gate\"`")
    assert entry.get("approved_by") == APPROVER, (
        "PD-6 violada (caso C): debe registrarse el aprobador declarado "
        f"({APPROVER!r}): {entry.get('approved_by')!r}")
    assert "delegation" in out.lower(), (
        "PD-6 violada (caso C): la salida debe DECLARAR que no hubo delegación "
        f"que verificar: {out!r}")


def test_pd6_case_c_active_epic_null_registers_declared_approver(
        gate_fx: _GateFixture) -> None:
    """PD-6 (caso C, variante `active_epic: null`): sin epic activo tampoco hay
    autoridad que verificar → mismo comportamiento: rc=0 y el aprobador
    declarado escrito en la entrada.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción de aceptación.
    """
    gate_fx.remove_delegation(epic_null=True)
    state = gate_fx.read_state()
    assert state.get("hitl_delegation") is None, (
        "precondición (fixture): sin delegación registrada")
    assert state.get("active_epic") is None, (
        "precondición (fixture): `active_epic: null`")

    proc = gate_fx.gate()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-6 violada (caso C — `active_epic: null`): sin autoridad que "
        f"verificar el `gate` no debe bloquearse (rc=0); rc="
        f"{proc.returncode}: {out!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-6 violada (caso C — `active_epic: null`): no hay entrada con "
        "`transition: \"gate\"`")
    assert entry.get("approved_by") == APPROVER, (
        "PD-6 violada (caso C — `active_epic: null`): debe registrarse el "
        f"aprobador declarado ({APPROVER!r}): {entry.get('approved_by')!r}")


# ---------------------------------------------------------------- PD-10


def test_pd10_gate_entry_carries_transition_key(gate_fx: _GateFixture) -> None:
    """PD-10 (forma de la clase `gate`): la operación computa y escribe
    `transition_key` —clave NUEVA y aditiva— en la entrada del gate.

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la aserción del efecto.
    """
    proc = gate_fx.gate()
    assert proc.returncode == 0, (
        "PD-10 violada: el `gate` debe registrarse (rc=0) para llevar su clave "
        f"de identidad; hoy rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    assert entry is not None, (
        "PD-10 violada: no hay entrada con `transition: \"gate\"`")
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        "PD-10 violada: la entrada de `gate` debe llevar `transition_key` "
        "(clave nueva y aditiva, derivada como sha256 canónico de la identidad "
        f"de la transición): {key!r}")


# ---------------------------------------------------------------- PD-11


def test_pd11_identical_gate_repetition_is_noop_byte_identical(
        gate_fx: _GateFixture) -> None:
    """PD-11 (clase `gate`): repetir la invocación idéntica (mismo
    `transition_key`) → rc=0, SIN segunda entrada de `stage_history`, con el
    state byte a byte idéntico al de la primera invocación, y salida que nombra
    la entrada existente (su `transition_key`).

    RED hoy: rc=2 «invalid choice: 'gate'» → falla la primera aserción.
    """
    first = gate_fx.gate()
    assert first.returncode == 0, (
        "PD-11 violada: la primera invocación del `gate` debe registrar la "
        f"transición (rc=0); hoy rc={first.returncode}: {first.stdout!r} "
        f"{first.stderr!r}")
    state_after_first = gate_fx.state_bytes()
    count_after_first = len(entries(gate_fx.read_state()))

    second = gate_fx.gate()

    assert second.returncode == 0, (
        "PD-11 violada: repetir la invocación idéntica del `gate` debe ser un "
        f"no-op exitoso (rc=0); rc={second.returncode}: {second.stdout!r} "
        f"{second.stderr!r}")
    assert len(entries(gate_fx.read_state())) == count_after_first, (
        "PD-11 violada: la repetición idéntica NO debe agregar una segunda "
        f"entrada de `stage_history` (sigue habiendo {count_after_first})")
    assert gate_fx.state_bytes() == state_after_first, (
        "PD-11 violada: el state tras la repetición idéntica debe ser byte a "
        "byte idéntico al de la primera invocación")
    entry = last_entry_with(gate_fx.read_state(), transition="gate")
    key = entry.get("transition_key") if entry else None
    assert key and key in (second.stdout + second.stderr), (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key!r}): {second.stdout!r} {second.stderr!r}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
