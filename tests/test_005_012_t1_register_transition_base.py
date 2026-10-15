#!/usr/bin/env python3
"""005-012 T1 RED — superficie `register-transition` (forma mínima: `delivery`
y `advance`), clave de identidad, digests derivados y las postcondiciones del
registro (PD-1..PD-4, PD-7, PD-10..PD-12, PD-17, PD-18, PD-20).

Contract:
- docs/specs/005-012-transition-registration/spec.md §2.1 (superficie CLI y
  digests derivados/opcionales), §2.2 (forma aditiva del registro), §2.3
  (postcondiciones PD-1..PD-4, PD-7, PD-10..PD-12, PD-17, PD-18, PD-20),
  §2.4 (invariantes INV-1, INV-2, INV-3, INV-6, INV-7).
- docs/specs/005-012-transition-registration/plan.md §4 ficha T1 (test focal
  declarado `tests/test_005_012_t1_register_transition_base.py`).

Superficie observable bajo prueba (caja negra: SOLO subprocess sobre el CLI
del repo; el módulo de implementación NUNCA se importa y su código NUNCA se
lee):

    python3 skills/cdad-cycle/scripts/cdad_packet.py register-transition \
        --project-root <ABS> --transition <delivery|advance> --stage <token> \
        [--packet <packet-id>] [--receipt <sha256>] [--artifact <path>=<sha256>] \
        [--current-stage <stage>] [--substage <sub>]
    python3 skills/cdad-cycle/scripts/cdad_packet.py validate-state --project-root <ABS>
    python3 skills/cdad-cycle/scripts/cdad_packet.py prepare --project-root <ABS> ...
    python3 skills/cdad-cycle/scripts/cdad_result.py receive ...   (camino legítimo)

El subcomando `register-transition` NO existe todavía: HOY el CLI responde con
un error de uso (rc=2, «invalid choice: 'register-transition'») y ningún
efecto sobre el state. Por eso cada test falla en la ASERCIÓN sobre el
comportamiento del contrato (efecto sobre el state, digests derivados,
marcadores de rechazo, identidad de la transición), nunca en la invocación ni
en una precondición de fixture: los fallos RED son AssertionError de contrato,
jamás ImportError, SyntaxError, JSONDecodeError ni error de setup.

REVIEW-FIX B2 (paquete `005-012-transition-registration-test-writer-red-008`).
La spec vigente fue ENMENDADA (`review.md` §1 B2): PD-10 reescrita —el payload
canónico de la identidad incluye los INSUMOS CON EFECTO (`--postcondition`
resuelta con su `--outcome`, `--current-stage`, `--artifact` y los campos
propios de cada clase) y se escribe en la entrada como clave nueva y aditiva
`transition_key_payload`—, PD-11 (el no-op delata la anotación que no escribe)
y §2.2. El subcomando EXISTE desde el GREEN de T1; los casos de este bloque son
el RED de esa corrección: hoy la identidad ignora esos insumos, así que una
invocación DISTINTA se traga como no-op rc=0 «sin efectos» y su resultado queda
sin escribir. Los casos anteriores NO se tocan (ni se debilitan).

Fixture: proyecto descartable en un tempdir (política válida, contrato
pineado en `stage_history`, delegación HITL con `source` existente, ejecución
v2 y paquete reales) construido por el camino legítimo del CLI
(`prepare` → `prepare --record-dispatch` → `cdad_result.py receive`); HOME del
subproceso en un tempdir VACÍO (nunca el HOME real, nunca este repo). Los ids
del fixture son sintéticos y anónimos. Nada de mocks sobre el cableado
interno y ningún test de cobertura no derivado de un PD.

Mapeo test → postcondición:

  test_pd1_prepare_keeps_its_role_and_does_not_register_transitions
      -> PD-1/INV-1 (la superficie es el subcomando del CLI —todos los casos
         lo invocan como subproceso— y `prepare` conserva su rol: un `prepare`
         posterior a una transición registrada no agrega entradas de
         `stage_history`)
  test_pd2_pd20_delivery_derives_receipt_digest_and_completes_packet
      -> PD-2 + PD-20 (forma mínima `delivery`, SIN afirmar ningún digest:
         rc=0, `active_packet.status` «completed», una entrada nueva, el
         `receipt_sha256` DERIVADO de los bytes y escrito/imprimido,
         `validate-state` verde)
  test_pd3_delivery_without_durable_receipt_fails_closed
      -> PD-3(a) (sin recibo durable: rc=2 `evidence missing` nombrando el
         paquete y la evidencia faltante; state byte a byte idéntico)
  test_pd3_asserted_receipt_digest_divergent_fails_closed
      -> PD-3(b) (digest afirmado divergente: rc=2 `evidence missing`; state
         byte a byte idéntico)
  test_pd3_artifact_absent_or_divergent_digest_fails_closed
      -> PD-3(c) (`--artifact` ausente o con digest afirmado divergente:
         rc=2 `evidence missing`; state byte a byte idéntico)
  test_pd4_delivery_never_approves
      -> PD-4 (la entrada de `delivery` no lleva `approved_by` ni
         `contract_*`/`plan_*`; el recibo sigue `semantic_status: pending`; y
         el control: sin entrada `specification` pinneada, `prepare --role
         implementer --substage green` sigue bloqueado con `approval pending`)
  test_pd7_advance_moves_operational_fields
      -> PD-7 (positivo: `advance` fija `tdd_substage` con el vocabulario
         cerrado, deja `current_stage` como estaba y agrega una entrada)
  test_pd7_advance_rejects_out_of_vocabulary_values
      -> PD-7 (negativo: `--current-stage`/`--substage` fuera del vocabulario
         → rc=2 `state incoherent` nombrando los valores admitidos, sin
         efectos)
  test_pd10_entry_carries_transition_key_identity
      -> PD-10 (la entrada lleva `transition_key` —clave nueva y aditiva— con
         la forma derivada de un sha256)
  test_pd11_identical_repetition_is_noop_byte_identical
      -> PD-11 (repetición idéntica: rc=0, sin segunda entrada, state byte a
         byte idéntico y salida que nombra la entrada existente)
  test_pd12_distinct_transition_appends_new_entry
      -> PD-12 (transición distinta → entrada nueva; `stage_history` queda
         append-only: las entradas previas no cambian)
  test_pd12_delivery_of_not_dispatched_packet_fails_closed
      -> PD-12 (iii) (exclusión estructural: `delivery` de un paquete que no
         está `dispatched` → rc=2 `state incoherent`, sin efectos)
  test_pd17_validate_state_green_before_and_after_and_history_additive
      -> PD-17 (aditividad: `validate-state` rc=0 antes y después de la
         invocación; una entrada histórica sin `transition_key` no rompe nada
         ni es reescrita). Sin porcentajes ni conteos del state vivo.
  test_pd18_delivery_entry_has_no_judgement_fields
      -> PD-18 (la entrada de `delivery` no lleva `verdict`, `disposition`,
         `criterion`, `review_path` ni `review_sha256`)
  test_pd20_asserted_receipt_digest_that_matches_is_verified
      -> PD-20 (afirmar un digest que coincide se VERIFICA y se acepta: la
         aserción opcional no puede rechazar por defecto)

Review-fix B2 (spec enmendada: PD-10/PD-11/PD-12, §2.2, D-7):

  test_b2_pd10_pd12_two_postconditions_of_the_same_packet_are_two_entries
      -> PD-10 + PD-12 (dos `delivery` del MISMO paquete con la MISMA `--stage`
         y `--postcondition` distinta son DOS transiciones: dos entradas y las
         DOS postcondiciones escritas en `postconditions_status`)
  test_b2_pd10_pd12_two_advances_with_the_same_stage_are_two_entries
      -> PD-10 + PD-12 (dos `advance` con la MISMA etiqueta y distinto
         `--current-stage`: dos entradas, y el state refleja el último valor)
  test_pd11_pd10_noop_is_independent_of_the_head_after_later_appends
      -> PD-11/D-7 (control: repetir la invocación idéntica DESPUÉS de appends
         posteriores sigue siendo no-op: una sola entrada, state byte-idéntico
         y salida que nombra la entrada existente)
  test_pd10_entry_carries_a_recomputable_transition_key_payload
      -> PD-10/§2.2 (la entrada lleva `transition_key_payload` —clave nueva y
         aditiva— y el `transition_key` se RECOMPUTA desde él con la
         serialización canónica declarada: identidad verificable desde el state)
  test_pd10_payload_declares_the_identity_tuple_and_the_effect_inputs
      -> PD-10 (el payload declara la tupla y los insumos con efecto de la
         invocación: la postcondición RESUELTA con su outcome, y los digests
         resueltos que la entrada escribe)
  test_pd11_noop_names_the_entry_and_declares_the_annotation_not_written
      -> PD-11/B2 (el no-op no es mudo: nombra la entrada existente y declara
         que la anotación `--note`/`--by` de esta invocación no se escribió)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from test_004_002_t2_bootstrap import (
    prepare_args,
    read_state,
    write_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
# Superficie declarada por la spec §2.1/§4: el CLI del repo (subcomandos
# `register-transition`/`validate-state`/`prepare` y el helper de recibos).
PACKET_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_packet.py"
RESULT_CLI = REPO_ROOT / "skills" / "cdad-cycle" / "scripts" / "cdad_result.py"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"
CLI_TIMEOUT_S = 90

# Fixture sintético y anónimo (ids inventados; ningún proyecto real).
EPIC_ID = "epic-demo-100-fixture"
FEATURE_ID = "demo-100-transition-fixture"
AUTHORITY_REF = f"docs/epics/{EPIC_ID}/execution.md"
CONTRACT_FILE = f"docs/specs/{FEATURE_ID}/spec.md"
CONTRACT_BYTES = b"# Spec fixture (demo-100 transition registration)\n"
APPROVER = "Demo Approver"
ARTIFACT_REL = ".cdad/local/artifact-demo.md"
ARTIFACT_BYTES = b"# Artifact fixture (demo-100)\n"

# Tokens y valores declarados por el contrato.
STAGE_TOKEN = "tdd-green-t1"          # etiqueta histórica libre (token plano)
STAGE_TOKEN_ALT = "tdd-green-b1"      # segunda etiqueta → transition_key distinta
STAGE_VOCAB = ("discovery", "specification", "tdd", "review", "merge", "idle")
SUBSTAGE_VOCAB = ("red", "green")
OUT_OF_VOCAB_STAGE = "grooming"
OUT_OF_VOCAB_SUBSTAGE = "polish"

EVIDENCE_MISSING = "evidence missing"
STATE_INCOHERENT = "state incoherent"
APPROVAL_PENDING = "approval pending"
RECEIPT_NAME = "receipt.json"

# Review-fix B2: la clave aditiva del payload canónico de la identidad (§2.2),
# el campo del efecto de `delivery` (§2.2) y la anotación de la invocación
# (`--note`/`--by`, FUERA del payload: PD-10/PD-18).
PAYLOAD_KEY = "transition_key_payload"
POSTCONDITIONS_FIELD = "postconditions_status"
NOTE_TEXT = "nota-demo-b2-no-debe-escribirse"
NOTE_ROLE = "rol-demo-b2"

TRANSITION_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


# ---------------------------------------------------------------- helpers


def entries(state: dict) -> list[dict]:
    return list(state.get("stage_history") or [])


def last_entry(state: dict) -> dict:
    assert entries(state), "el state del fixture no tiene entradas de stage_history"
    return entries(state)[-1]


def last_entry_with(state: dict, **fields) -> dict | None:
    for entry in reversed(entries(state)):
        if all(entry.get(k) == v for k, v in fields.items()):
            return entry
    return None


class _Fixture:
    """Proyecto descartable en un tempdir, con el HOME del subproceso aislado.

    Modos:
      - `ready`: paquete `dispatched` + recibo durable real (PD-2/PD-3/PD-4/
        PD-10/PD-11/PD-17/PD-18/PD-20).
      - `dispatched_no_receipt`: paquete `dispatched` sin recibo (PD-3(a)).
      - `prepared`: paquete `prepared` (PD-7/PD-12).

    Toda la capa previa se produce por el camino legítimo del CLI
    (`prepare` → `prepare --record-dispatch` → `cdad_result.py receive`): son
    precondiciones de comportamiento EXISTENTE y se asertan como tales.
    """

    def __init__(self, base: Path, mode: str = "ready") -> None:
        assert mode in ("ready", "dispatched_no_receipt", "prepared"), mode
        self.base = base
        self.home = base / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.root = base / "proj"
        self._build_project()
        self._prepare()
        state = self.read_state()
        self.execution_id = state["execution"]["id"]
        self.packet_id = state["active_packet"]["id"]
        if mode in ("ready", "dispatched_no_receipt"):
            self._record_dispatch()
        if mode == "ready":
            self._receive()
        self.artifact = self.root / ARTIFACT_REL
        self.artifact.parent.mkdir(parents=True, exist_ok=True)
        self.artifact.write_bytes(ARTIFACT_BYTES)

    # -- construcción (interfaz pública del CLI, nunca implementación) ----

    def _build_project(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "docs").mkdir(exist_ok=True)
        (self.root / POLICY_REL).write_text(
            json.dumps({
                "schema_version": 1,
                "path_policy": {
                    "test_roots": ["tests"],
                    "implementation_roots": ["src", "lib"],
                    "documentation_roots": ["docs"],
                },
                "temporary_roots": [".cdad/tmp"],
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (self.root / CONTRACT_FILE).parent.mkdir(parents=True, exist_ok=True)
        (self.root / CONTRACT_FILE).write_bytes(CONTRACT_BYTES)
        authority = self.root / AUTHORITY_REF
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Authorized execution fixture (demo-100)\n",
                             encoding="utf-8")
        write_state(self.root, {
            "version": 1,
            "stack": None,
            "active_epic": EPIC_ID,
            "epic_stage": "features-loop",
            "epic_features": [{"id": FEATURE_ID, "status": "in-progress"}],
            "epic_history": [],
            "active_feature": FEATURE_ID,
            "current_stage": "tdd",
            "tdd_substage": "red",
            "audit_status": "approved",
            "postconditions_status": {},
            # Entrada histórica SIN `transition_key` (PD-10/PD-17: la clave es
            # nueva y aditiva; ninguna validación se la exige a lo histórico).
            "stage_history": [{
                "feature": FEATURE_ID,
                "stage": "specification",
                "approved_by": APPROVER,
                "approved_at": "2026-10-14T00:00:00Z",
                "contract_path": CONTRACT_FILE,
                "contract_sha256": hashlib.sha256(CONTRACT_BYTES).hexdigest(),
            }],
            "approver": APPROVER,
            "last_updated": "2026-10-14T00:00:00Z",
            "execution": None,
            "active_packet": None,
            "hitl_delegation": {
                "status": "active",
                "epic_id": EPIC_ID,
                "source": AUTHORITY_REF,
                "scope": EPIC_ID,
                "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
            },
        })

    def _prepare(self) -> None:
        proc = self.run_packet(*prepare_args(
            self.root, role="test-writer", substage="red",
            objective="fixture demo-100 (registro de transición)"))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente): `prepare` debe "
            f"publicar la ejecución v2 y el paquete (rc=0): "
            f"{proc.stdout!r} {proc.stderr!r}")

    def _record_dispatch(self) -> None:
        observation = self.root / "docs" / "observation-demo.json"
        observation.write_text(json.dumps({
            "runtime": "demo-runtime",
            "model_configured": "demo-model",
            "model_reported": "demo-model",
            "session": "ses-demo-0001",
            "started_at": "2026-10-14T00:00:00Z",
            "provenance": {
                "runtime": "reported by runtime",
                "model_reported": "orchestrator",
                "session": "orchestrator",
            },
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        proc = self.run_packet(
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", self.packet_id,
            "--attempt-id", "attempt-demo-001",
            "--input", str(observation))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente): "
            f"`--record-dispatch` debe registrar el intento (rc=0): "
            f"{proc.stdout!r} {proc.stderr!r}")
        assert (self.read_state()["active_packet"]["status"] == "dispatched"), (
            "precondición (fixture): el paquete activo debe quedar "
            "`dispatched`")

    def _receive(self) -> None:
        inbox = self.root / ".cdad" / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "role-report.md").write_bytes(
            b"# Role report (fixture demo-100)\nEvidencia mecanica del intento.\n")
        (inbox / "changes.json").write_text(json.dumps({
            "schema_version": 1,
            "observation_status": "trusted",
            "baseline_ref": "demo-baseline",
            "baseline_sha256": "0" * 64,
            "changes": [],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (inbox / "RESULT.json").write_text(json.dumps({
            "schema_version": 1,
            "execution_id": self.execution_id,
            "packet_id": self.packet_id,
            "feature_id": FEATURE_ID,
            "source": {"kind": "staged-file", "sdk_message_ref": None},
            "parts": [{
                "name": "role-report",
                "artifact_kind": "test-writer-role-report",
                "staged_path": ".cdad/inbox/role-report.md",
            }],
            "observed_changes": {
                "observation_status": "trusted",
                "baseline_ref": "demo-baseline",
                "baseline_sha256": "0" * 64,
                "manifest_path": ".cdad/inbox/changes.json",
            },
            "run_evidence_ref": None,
        }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        packet_dir = self.root / ".cdad" / "packets" / self.packet_id
        proc = self.run_result(
            "receive",
            "--project-root", str(self.root),
            "--execution-context",
            str(self.root / ".cdad" / "executions" / self.execution_id
                / "execution.json"),
            "--packet", str(packet_dir / "PACKET.md"),
            "--request", str(packet_dir / "REQUEST.json"),
            "--descriptor", str(inbox / "RESULT.json"))
        assert proc.returncode == 0, (
            "precondición (fixture, comportamiento existente): `receive` debe "
            f"persistir el recibo durable (rc=0): {proc.stdout!r} "
            f"{proc.stderr!r}")
        assert self.receipt_path().is_file(), (
            f"precondición (fixture): debe existir {RECEIPT_NAME} del paquete "
            f"en {self.receipt_path()}")

    # -- CLI (caja negra) -------------------------------------------------

    def env(self) -> dict:
        env = dict(os.environ)
        env["HOME"] = str(self.home)  # NUNCA el HOME real
        return env

    def _run(self, script: Path, args: list[str]
             ) -> subprocess.CompletedProcess:
        assert script.is_file(), f"CLI del repo ausente: {script}"
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=self.env(),
            stdin=subprocess.DEVNULL, timeout=CLI_TIMEOUT_S,
        )

    def run_packet(self, *args: str) -> subprocess.CompletedProcess:
        return self._run(PACKET_CLI, list(args))

    def run_result(self, *args: str) -> subprocess.CompletedProcess:
        return self._run(RESULT_CLI, list(args))

    def register_transition(self, *extra: str
                            ) -> subprocess.CompletedProcess:
        return self.run_packet(
            "register-transition", "--project-root", str(self.root), *extra)

    def delivery(self, *extra: str) -> subprocess.CompletedProcess:
        return self.register_transition(
            "--transition", "delivery", "--stage", STAGE_TOKEN,
            "--packet", self.packet_id, *extra)

    def validate_state(self) -> subprocess.CompletedProcess:
        return self.run_packet(
            "validate-state", "--project-root", str(self.root))

    # -- observación ------------------------------------------------------

    def read_state(self) -> dict:
        return read_state(self.root)

    def write_state(self, state: dict) -> None:
        write_state(self.root, state)

    def state_bytes(self) -> bytes:
        return (self.root / STATE_REL).read_bytes()

    def receipt_path(self) -> Path:
        return (self.root / ".cdad" / "runtime" / "results"
                / self.execution_id / self.packet_id / RECEIPT_NAME)


@pytest.fixture
def ready(tmp_path: Path) -> _Fixture:
    """Entregable listo: paquete `dispatched` + recibo durable real."""
    return _Fixture(tmp_path, mode="ready")


@pytest.fixture
def no_receipt(tmp_path: Path) -> _Fixture:
    """Paquete `dispatched` SIN recibo durable (PD-3(a))."""
    return _Fixture(tmp_path, mode="dispatched_no_receipt")


@pytest.fixture
def prepared(tmp_path: Path) -> _Fixture:
    """Paquete `prepared` (sin despacho): PD-7 (avance) y PD-12 (exclusión)."""
    return _Fixture(tmp_path, mode="prepared")


def assert_unchanged(fx: _Fixture, before: bytes, pd: str, label: str) -> None:
    """INV-7: todo rechazo deja el state byte a byte idéntico."""
    assert fx.state_bytes() == before, (
        f"{pd} violada ({label}): el rechazo modificó "
        f"`{STATE_REL}` (INV-7: fallo cerrado sin efectos)")


# Helpers del review-fix B2 (PD-10/PD-11/PD-12 enmendadas).


def entries_with(state: dict, **fields) -> list[dict]:
    """TODAS las entradas que declaran los campos dados (append-only)."""
    return [e for e in entries(state)
            if all(e.get(key) == value for key, value in fields.items())]


def outcome_for(state: dict, n: str | int) -> str | None:
    """El resultado escrito para la postcondición `n` (PD-10 normaliza
    `str(n)`, la misma forma con la que el efecto escribe el state)."""
    status = state.get(POSTCONDITIONS_FIELD) or {}
    for key, value in status.items():
        if str(key) == str(n):
            return value
    return None


def canonical_digest(payload: dict) -> str:
    """Serialización canónica DECLARADA por PD-10 (la del contrato, no la del
    state): `json.dumps(payload, ensure_ascii=False, sort_keys=True,
    separators=(",", ":"))` sobre bytes UTF-8, sha256 en hex."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- PD-1


def test_pd1_prepare_keeps_its_role_and_does_not_register_transitions(
        ready: _Fixture) -> None:
    """PD-1/INV-1: la superficie es un subcomando del CLI (todos los casos lo
    invocan como subproceso sobre el CLI real) y `prepare` CONSERVA su rol de
    productor de paquetes: un `prepare` posterior a una transición registrada
    no agrega entradas de `stage_history` (no hay segundo escritor).

    RED hoy: `register-transition` no existe (rc=2 «invalid choice») → falla
    la aserción del contrato, no la invocación.
    """
    delivered = ready.delivery()
    assert delivered.returncode == 0, (
        "PD-1 violada: `register-transition` debe ser un subcomando del CLI "
        f"del repo y aceptar la forma mínima (rc=0); hoy rc="
        f"{delivered.returncode}: {delivered.stdout!r} "
        f"{delivered.stderr!r}")
    after_delivery = len(entries(ready.read_state()))

    again = ready.run_packet(*prepare_args(
        ready.root, role="test-writer", substage="red",
        objective="segundo encargo del fixture demo-100"))
    assert again.returncode == 0, (
        "precondición (comportamiento existente): un `prepare` con el paquete "
        f"activo ya terminal debe publicar (rc=0): {again.stdout!r} "
        f"{again.stderr!r}")
    assert len(entries(ready.read_state())) == after_delivery, (
        "PD-1/INV-1 violada: `prepare` registró una transición en "
        "`stage_history` (el registro es de `register-transition`; `prepare` "
        "conserva su rol y no es un segundo escritor)"
    )


# ---------------------------------------------------------------- PD-2 / PD-20


def test_pd2_pd20_delivery_derives_receipt_digest_and_completes_packet(
        ready: _Fixture) -> None:
    """PD-2 + PD-20 (forma mínima, SIN afirmar ningún digest): una invocación
    `--transition delivery --stage <token> --packet <id>` → rc=0; se agrega
    UNA entrada de `stage_history`; `active_packet.status` pasa a
    «completed»; el digest del recibo se DERIVA de los bytes actuales y queda
    escrito en la entrada e impreso en la salida; `validate-state` → rc=0.

    RED hoy: rc=2 «invalid choice» → falla la aserción del efecto
    (AssertionError de contrato).
    """
    before = ready.read_state()
    derived = hashlib.sha256(ready.receipt_path().read_bytes()).hexdigest()
    assert ready.validate_state().returncode == 0, (
        "precondición (fixture): el state con la entrega pendiente debe ser "
        "coherente hoy")

    proc = ready.delivery()

    assert proc.returncode == 0, (
        "PD-2 violada: `delivery` con recibo durable presente y sin afirmar "
        f"ningún digest debe aceptarse (rc=0); hoy rc={proc.returncode} "
        f"(subcomando inexistente): {proc.stdout!r} {proc.stderr!r}")
    state = ready.read_state()
    assert state["active_packet"] is not None and (
        state["active_packet"].get("status") == "completed"), (
        "PD-2 violada: `active_packet.status` debe pasar a «completed»: "
        f"{state.get('active_packet')!r}")
    assert len(entries(state)) == len(entries(before)) + 1, (
        "PD-2 violada: la recepción debe agregar UNA entrada de "
        f"`stage_history` (antes {len(entries(before))}, después "
        f"{len(entries(state))})")
    entry = last_entry(state)
    assert entry.get("transition") == "delivery", (
        f"PD-2 violada: la entrada debe declarar `transition: \"delivery\"` "
        f"(§2.2): {entry!r}")
    assert entry.get("packet_id") == ready.packet_id, (
        f"PD-2 violada: la entrada debe citar el paquete ({ready.packet_id!r}): "
        f"{entry.get('packet_id')!r}")
    assert entry.get("receipt_sha256") == derived, (
        "PD-20 violada: sin `--receipt`, el digest del recibo debe DERIVARSE "
        "de los bytes actuales del `receipt.json` y escribirse en la entrada; "
        f"esperado {derived!r}, entrada {entry.get('receipt_sha256')!r}")
    out = proc.stdout + proc.stderr
    assert derived in out, (
        "PD-20 violada: la salida debe IMPRIMIR el digest usado (derivado) "
        f"para que la entrada quede auditable: {derived!r} no aparece en "
        f"{out!r}")
    assert ready.validate_state().returncode == 0, (
        "PD-2 violada: `validate-state` debe quedar verde sobre el state "
        "resultante")


# ---------------------------------------------------------------- PD-3


def test_pd3_delivery_without_durable_receipt_fails_closed(
        no_receipt: _Fixture) -> None:
    """PD-3(a): `delivery` de un paquete SIN recibo durable → rc=2, marcador
    `evidence missing`, diagnóstico que nombra el paquete y la evidencia
    faltante; el state queda byte a byte idéntico (INV-7).

    RED hoy: rc=2 por error de uso del CLI (no es el rechazo del contrato) →
    falla la aserción del marcador y del diagnóstico.
    """
    before = no_receipt.state_bytes()
    assert not no_receipt.receipt_path().exists(), (
        "precondición (fixture): este caso NO debe tener recibo durable")
    state_before = no_receipt.read_state()
    assert state_before["active_packet"]["status"] == "dispatched", (
        "precondición (fixture): el paquete debe estar `dispatched`")

    proc = no_receipt.delivery()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-3 violada (a): la entrega sin recibo durable debe fallar cerrado "
        f"(rc=2); rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-3 violada (a): el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert no_receipt.packet_id in out, (
        "PD-3 violada (a): el diagnóstico debe nombrar el paquete "
        f"({no_receipt.packet_id!r}): {out!r}")
    assert RECEIPT_NAME in out, (
        "PD-3 violada (a): el diagnóstico debe nombrar la evidencia faltante "
        f"({RECEIPT_NAME}): {out!r}")
    assert_unchanged(no_receipt, before, "PD-3", "a")


def test_pd3_asserted_receipt_digest_divergent_fails_closed(
        ready: _Fixture) -> None:
    """PD-3(b): `--receipt <sha256>` AFIRMADO distinto del digest real → rc=2
    `evidence missing`, sin efectos (state byte a byte idéntico).

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    before = ready.state_bytes()
    wrong = "f" * 64
    real = hashlib.sha256(ready.receipt_path().read_bytes()).hexdigest()
    assert wrong != real, "precondición (fixture): el digest afirmado diverge"

    proc = ready.delivery("--receipt", wrong)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-3 violada (b): un digest afirmado divergente debe fallar cerrado "
        f"(rc=2); rc={proc.returncode}: {out!r}")
    assert EVIDENCE_MISSING in out.lower(), (
        "PD-3 violada (b): el rechazo debe llevar el marcador "
        f"«{EVIDENCE_MISSING}»: {out!r}")
    assert wrong in out, (
        "PD-3 violada (b): el diagnóstico debe nombrar el digest esperado "
        f"(el afirmado, {wrong!r}): {out!r}")
    assert_unchanged(ready, before, "PD-3", "b")


def test_pd3_artifact_absent_or_divergent_digest_fails_closed(
        ready: _Fixture) -> None:
    """PD-3(c): `--artifact <path>=<sha256>` cuya ruta no existe, o cuyo
    digest afirmado no coincide con los bytes → rc=2 `evidence missing`, sin
    efectos (state byte a byte idéntico).

    RED hoy: rc=2 por error de uso → fallan las aserciones del marcador, en
    cada variante.
    """
    absent = ready.root / ".cdad" / "local" / "absent-demo.md"
    divergent = f"{ready.artifact}={'0' * 64}"
    variants = (
        ("ruta ausente", str(absent)),
        ("digest afirmado divergente", divergent),
    )
    for label, artifact_arg in variants:
        before = ready.state_bytes()
        proc = ready.delivery("--artifact", artifact_arg)
        out = proc.stdout + proc.stderr
        assert proc.returncode == 2, (
            f"PD-3 violada (c, {label}): el artefacto ausente o con digest "
            f"divergente debe fallar cerrado (rc=2); rc={proc.returncode}: "
            f"{out!r}")
        assert EVIDENCE_MISSING in out.lower(), (
            f"PD-3 violada (c, {label}): el rechazo debe llevar el marcador "
            f"«{EVIDENCE_MISSING}»: {out!r}")
        assert_unchanged(ready, before, "PD-3", f"c, {label}")


# ---------------------------------------------------------------- PD-4


def test_pd4_delivery_never_approves(ready: _Fixture) -> None:
    """PD-4: la entrada escrita por `delivery` NO lleva `approved_by`,
    `contract_path`, `contract_sha256`, `plan_path` ni `plan_sha256`; el
    recibo sigue `semantic_status: pending`; y como control, sin entrada
    `specification` pinneada, `prepare --role implementer --substage green`
    sigue fallando con `approval pending` (rc=2).

    RED hoy: rc=2 «invalid choice» en la entrega → falla la primera aserción
    de contrato.
    """
    proc = ready.delivery()
    assert proc.returncode == 0, (
        "PD-4 violada: la entrega debe registrarse (rc=0) para evaluar que "
        f"recibir no aprueba; hoy rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")
    entry = last_entry_with(ready.read_state(), transition="delivery")
    assert entry is not None, (
        "PD-4 violada: no hay entrada de `delivery` en `stage_history`")
    for field in ("approved_by", "contract_path", "contract_sha256",
                  "plan_path", "plan_sha256"):
        assert field not in entry, (
            "PD-4 violada: recibir una entrega NUNCA aprueba; la entrada de "
            f"`delivery` no debe llevar {field!r}: {entry!r}")

    receipt = json.loads(ready.receipt_path().read_text(encoding="utf-8"))
    assert receipt.get("semantic_status") == "pending", (
        "PD-4 violada: el `semantic_status` del recibo debe seguir `pending` "
        f"(la operación no lo reescribe): {receipt.get('semantic_status')!r}")

    # Control: sin entrada `specification` pinneada la autorización no existe.
    state = ready.read_state()
    state["stage_history"] = [
        e for e in entries(state)
        if not (e.get("feature") == FEATURE_ID
                and e.get("stage") == "specification")
    ]
    ready.write_state(state)
    control = ready.run_packet(*prepare_args(
        ready.root, role="implementer", substage="green",
        objective="control PD-4 (sin aprobación pinneada)"))
    out = control.stdout + control.stderr
    assert control.returncode != 0, (
        "PD-4 violada (control): con la entrega registrada y SIN entrada "
        "`specification` pinneada, `prepare --role implementer --substage "
        f"green` debe seguir bloqueado: {out!r}")
    assert APPROVAL_PENDING in out.lower(), (
        "PD-4 violada (control): el bloqueo debe ser `approval pending` "
        "(la autorización depende sólo de la entrada `specification`): "
        f"{out!r}")


# ---------------------------------------------------------------- PD-7


def test_pd7_advance_moves_operational_fields(prepared: _Fixture) -> None:
    """PD-7 (positivo): `--transition advance --stage <token> --substage
    <sub>` → rc=0; fija el campo operativo `tdd_substage` (vocabulario
    cerrado), deja `current_stage` como estaba (no se declaró) y agrega una
    entrada de `stage_history`.

    RED hoy: rc=2 por error de uso → falla la aserción del avance.
    """
    before = prepared.read_state()

    proc = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--substage", "green")
    out = proc.stdout + proc.stderr

    assert proc.returncode == 0, (
        "PD-7 violada: `advance` con vocabulario válido debe aceptarse "
        f"(rc=0); hoy rc={proc.returncode}: {out!r}")
    state = prepared.read_state()
    assert state["tdd_substage"] == "green", (
        "PD-7 violada: `advance` debe fijar `tdd_substage` en el valor "
        f"declarado: {state.get('tdd_substage')!r}")
    assert state["current_stage"] == before["current_stage"], (
        "PD-7 violada: `advance` sólo fija los campos declarados; "
        f"`current_stage` cambió sin declararse: {state.get('current_stage')!r}")
    entries_after = entries(state)
    assert len(entries_after) == len(entries(before)) + 1, (
        "PD-7 violada: el avance debe dejar la traza como UNA entrada nueva "
        f"(antes {len(entries(before))}, después {len(entries_after)})")
    assert last_entry(state).get("transition") == "advance", (
        f"PD-7 violada: la entrada debe declarar `transition: \"advance\"`: "
        f"{last_entry(state)!r}")
    assert prepared.validate_state().returncode == 0, (
        "PD-7 violada: el state resultante debe seguir siendo coherente")


def test_pd7_advance_rejects_out_of_vocabulary_values(
        prepared: _Fixture) -> None:
    """PD-7 (negativo): `--current-stage` fuera de {discovery, specification,
    tdd, review, merge, idle} y `--substage` fuera de
    `VALID_SUBSTAGES`/`ROLE_SUBSTAGES` → rc=2 `state incoherent`, nombrando
    los valores admitidos, SIN efectos (state byte a byte idéntico).

    RED hoy: rc=2 por error de uso → fallan las aserciones del marcador, el
    vocabulario admitido y la ausencia de efectos.
    """
    variants = (
        ("--current-stage fuera del vocabulario",
         ("--current-stage", OUT_OF_VOCAB_STAGE), OUT_OF_VOCAB_STAGE,
         STAGE_VOCAB),
        ("--substage fuera del vocabulario",
         ("--substage", OUT_OF_VOCAB_SUBSTAGE), OUT_OF_VOCAB_SUBSTAGE,
         SUBSTAGE_VOCAB),
    )
    for label, extra, rejected, admitted in variants:
        before = prepared.state_bytes()
        proc = prepared.register_transition(
            "--transition", "advance", "--stage", STAGE_TOKEN, *extra)
        out = proc.stdout + proc.stderr
        assert proc.returncode == 2, (
            f"PD-7 violada ({label}): debe fallar cerrado (rc=2); "
            f"rc={proc.returncode}: {out!r}")
        assert STATE_INCOHERENT in out.lower(), (
            f"PD-7 violada ({label}): el rechazo debe llevar el marcador "
            f"«{STATE_INCOHERENT}»: {out!r}")
        assert rejected in out, (
            f"PD-7 violada ({label}): el diagnóstico debe nombrar el valor "
            f"rechazado ({rejected!r}): {out!r}")
        assert any(value in out for value in admitted), (
            f"PD-7 violada ({label}): el diagnóstico debe nombrar los valores "
            f"admitidos {admitted}: {out!r}")
        assert_unchanged(prepared, before, "PD-7", label)


# ---------------------------------------------------------------- PD-10


def test_pd10_entry_carries_transition_key_identity(ready: _Fixture) -> None:
    """PD-10: la operación computa y escribe `transition_key` —clave NUEVA y
    aditiva— en la entrada; la entrada histórica (sin la clave) no se
    invalida.

    RED hoy: rc=2 por error de uso → falla la aserción de la clave.
    """
    proc = ready.delivery()
    assert proc.returncode == 0, (
        "PD-10 violada: la transición debe registrarse (rc=0) para llevar su "
        f"clave de identidad; hoy rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")
    entry = last_entry(ready.read_state())
    key = entry.get("transition_key")
    assert isinstance(key, str) and TRANSITION_DIGEST_RE.match(key), (
        "PD-10 violada: la entrada debe llevar `transition_key` (clave nueva "
        "y aditiva, derivada como sha256 canónico de la identidad de la "
        f"transición): {key!r}")


# ---------------------------------------------------------------- PD-11


def test_pd11_identical_repetition_is_noop_byte_identical(
        ready: _Fixture) -> None:
    """PD-11: repetir la invocación idéntica (mismo `transition_key`) → rc=0,
    SIN segunda entrada de `stage_history`, con el state byte a byte idéntico
    al de la primera invocación, y salida que nombra la entrada existente.

    RED hoy: rc=2 por error de uso → falla la primera aserción de contrato.
    """
    first = ready.delivery()
    assert first.returncode == 0, (
        "PD-11 violada: la primera invocación debe registrar la transición "
        f"(rc=0); hoy rc={first.returncode}: {first.stdout!r} "
        f"{first.stderr!r}")
    state_after_first = ready.state_bytes()
    count_after_first = len(entries(ready.read_state()))

    second = ready.delivery()

    assert second.returncode == 0, (
        "PD-11 violada: repetir la invocación idéntica debe ser un no-op "
        f"exitoso (rc=0); rc={second.returncode}: {second.stdout!r} "
        f"{second.stderr!r}")
    assert len(entries(ready.read_state())) == count_after_first, (
        "PD-11 violada: la repetición idéntica NO debe agregar una segunda "
        f"entrada de `stage_history` (sigue habiendo {count_after_first})")
    assert ready.state_bytes() == state_after_first, (
        "PD-11 violada: el state tras la repetición idéntica debe ser byte a "
        "byte idéntico al de la primera invocación")
    key = last_entry(ready.read_state()).get("transition_key")
    assert key and key in (second.stdout + second.stderr), (
        "PD-11 violada: la salida del no-op debe nombrar la entrada "
        f"existente (su `transition_key` {key!r}): "
        f"{second.stdout!r} {second.stderr!r}")


# ---------------------------------------------------------------- PD-12


def test_pd12_distinct_transition_appends_new_entry(prepared: _Fixture) -> None:
    """PD-12: un `transition_key` distinto (otra `--stage`) se registra como
    entrada NUEVA (append); las entradas previas no cambian (`stage_history`
    es append-only).

    RED hoy: rc=2 por error de uso → falla la primera aserción de contrato.
    """
    before = prepared.read_state()
    first = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--substage", "green")
    assert first.returncode == 0, (
        "PD-12 violada: la primera transición debe registrarse (rc=0); hoy "
        f"rc={first.returncode}: {first.stdout!r} {first.stderr!r}")

    second = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN_ALT,
        "--substage", "red")
    assert second.returncode == 0, (
        "PD-12 violada: una transición con `transition_key` distinto debe "
        f"registrarse como entrada nueva (rc=0); rc={second.returncode}: "
        f"{second.stdout!r} {second.stderr!r}")

    entries_after = entries(prepared.read_state())
    assert len(entries_after) == len(entries(before)) + 2, (
        "PD-12 violada: dos transiciones distintas son DOS entradas nuevas "
        f"(antes {len(entries(before))}, después {len(entries_after)})")
    new_entries = entries_after[len(entries(before)):]
    keys = [e.get("transition_key") for e in new_entries]
    assert all(isinstance(k, str) and k for k in keys), (
        f"PD-12 violada: cada entrada nueva lleva su `transition_key`: {keys!r}")
    assert keys[0] != keys[1], (
        f"PD-12 violada: una transición distinta tiene una clave distinta: "
        f"{keys!r}")
    assert entries_after[:len(entries(before))] == entries(before), (
        "PD-12/INV-3 violada: las entradas previas no deben reescribirse "
        "(append-only)")
    assert prepared.validate_state().returncode == 0, (
        "PD-12 violada: el state con las dos entradas nuevas debe ser "
        "coherente")


def test_pd12_delivery_of_not_dispatched_packet_fails_closed(
        prepared: _Fixture) -> None:
    """PD-12 (iii) — exclusión estructural: `delivery` cuyo paquete citado NO
    está `dispatched` → rc=2, marcador `state incoherent`, sin efectos (state
    byte a byte idéntico).

    RED hoy: rc=2 por error de uso → falla la aserción del marcador.
    """
    before = prepared.state_bytes()
    assert prepared.read_state()["active_packet"]["status"] == "prepared", (
        "precondición (fixture): el paquete debe estar `prepared` (no "
        "`dispatched`)")

    proc = prepared.delivery()
    out = proc.stdout + proc.stderr

    assert proc.returncode == 2, (
        "PD-12 violada (iii): `delivery` de un paquete no `dispatched` debe "
        f"fallar cerrado (rc=2); rc={proc.returncode}: {out!r}")
    assert STATE_INCOHERENT in out.lower(), (
        "PD-12 violada (iii): el reparto de marcadores es por condición: "
        "paquete no `dispatched` → marcador "
        f"«{STATE_INCOHERENT}»: {out!r}")
    assert_unchanged(prepared, before, "PD-12", "iii")


# ---------------------------------------------------------------- PD-17


def test_pd17_validate_state_green_before_and_after_and_history_additive(
        ready: _Fixture) -> None:
    """PD-17: la operación y sus validaciones NO exigen ningún campo a las
    entradas existentes: `validate-state` → rc=0 antes y después de la
    invocación, y una entrada histórica SIN `transition_key` no rompe nada ni
    es reescrita. El oráculo es `validate-state rc=0` —sin porcentajes ni
    conteos del state vivo.

    RED hoy: rc=2 por error de uso → falla la aserción del efecto.
    """
    before_state = ready.read_state()
    historical = [e for e in entries(before_state) if "transition_key" not in e]
    assert historical, (
        "precondición (fixture): debe haber al menos una entrada histórica "
        "sin `transition_key`")
    assert ready.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 ANTES de la operación "
        "sobre el state con historia sin `transition_key`")

    proc = ready.delivery()
    assert proc.returncode == 0, (
        "PD-17 violada: la transición debe registrarse (rc=0) para evaluar la "
        f"aditividad; hoy rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")

    assert ready.validate_state().returncode == 0, (
        "PD-17 violada: `validate-state` debe dar rc=0 DESPUÉS de la "
        "operación (ninguna validación nueva se aplica a lo histórico)")
    after_state = ready.read_state()
    after_historical = [
        e for e in entries(after_state) if "transition_key" not in e]
    assert after_historical == historical, (
        "PD-17/INV-3 violada: las entradas históricas sin `transition_key` "
        "deben quedar intactas (no se reescriben ni se les exige la clave "
        f"nueva): {after_historical!r} != {historical!r}")


# ---------------------------------------------------------------- PD-18


def test_pd18_delivery_entry_has_no_judgement_fields(ready: _Fixture) -> None:
    """PD-18: la entrada de `delivery` no lleva `verdict`, `disposition`,
    `criterion`, `review_path` ni `review_sha256` — la operación no escribe
    juicio ni parsea prosa.

    RED hoy: rc=2 por error de uso → falla la aserción del efecto.
    """
    proc = ready.delivery()
    assert proc.returncode == 0, (
        "PD-18 violada: la entrega debe registrarse (rc=0) para evaluar que "
        f"no escribe juicio; hoy rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")
    entry = last_entry_with(ready.read_state(), transition="delivery")
    assert entry is not None, (
        "PD-18 violada: no hay entrada de `delivery` en `stage_history`")
    for field in ("verdict", "disposition", "criterion", "review_path",
                  "review_sha256"):
        assert field not in entry, (
            "PD-18 violada: la entrada de `delivery` no debe llevar el campo "
            f"de juicio {field!r}: {entry!r}")


# ---------------------------------------------------------------- PD-20


def test_pd20_asserted_receipt_digest_that_matches_is_verified(
        ready: _Fixture) -> None:
    """PD-20: afirmar un digest que COINCIDE con los bytes actuales se
    VERIFICA y se acepta (rc=0), y el digest verificado queda escrito en la
    entrada. La aserción opcional no puede rechazar por defecto.

    RED hoy: rc=2 por error de uso → falla la aserción del efecto.
    """
    derived = hashlib.sha256(ready.receipt_path().read_bytes()).hexdigest()

    proc = ready.delivery("--receipt", derived)

    assert proc.returncode == 0, (
        "PD-20 violada: un `--receipt` afirmado que coincide con los bytes "
        f"debe verificarse y aceptarse (rc=0); rc={proc.returncode}: "
        f"{proc.stdout!r} {proc.stderr!r}")
    entry = last_entry_with(ready.read_state(), transition="delivery")
    assert entry is not None, (
        "PD-20 violada: no hay entrada de `delivery` en `stage_history`")
    assert entry.get("receipt_sha256") == derived, (
        "PD-20 violada: el digest verificado debe quedar escrito en la "
        f"entrada: esperado {derived!r}, entrada "
        f"{entry.get('receipt_sha256')!r}")


# ---------------------------------------------------------------- review-fix B2
# PD-10/PD-11/PD-12 enmendadas (spec vigente) + §2.2 + D-7: la identidad de la
# transición incluye los INSUMOS CON EFECTO y se escribe en la entrada como
# `transition_key_payload`, de modo que dos invocaciones distintas del mismo
# paquete con la misma etiqueta NO se traguen como no-op.


def test_b2_pd10_pd12_two_postconditions_of_the_same_packet_are_two_entries(
        ready: _Fixture) -> None:
    """PD-10 + PD-12 (B2): registrar DOS postcondiciones del MISMO paquete con
    la MISMA etiqueta —`--postcondition 1 --outcome green` y después
    `--postcondition 2 --outcome green`— son DOS transiciones distintas (el
    insumo con efecto entra en el payload de PD-10 → `transition_key` distinto)
    ⇒ **DOS** entradas y ninguna de las dos es un no-op. El state termina con
    las **dos** entradas de esa etapa y `postconditions_status` con las **dos**
    postcondiciones escritas.

    RED hoy (defecto B2): la identidad ignora `--postcondition`/`--outcome`, la
    2ª invocación devuelve rc=0 «no-op, no effects» y el resultado queda sin
    escribir → falla por ASERCIÓN de contrato (el conteo de entradas), nunca por
    import, sintaxis o fixture.
    """
    before = ready.read_state()
    assert ready.validate_state().returncode == 0, (
        "precondición (fixture): el state con la entrega pendiente debe ser "
        "coherente")

    first = ready.delivery("--postcondition", "1", "--outcome", "green")
    assert first.returncode == 0, (
        "PD-10 violada: la 1ª `delivery --postcondition 1 --outcome green` del "
        f"paquete con recibo durable debe registrarse (rc=0); rc="
        f"{first.returncode}: {first.stdout!r} {first.stderr!r}")

    second = ready.delivery("--postcondition", "2", "--outcome", "green")
    assert second.returncode == 0, (
        "PD-10/PD-12 violada (B2): una `delivery` del mismo paquete y la misma "
        "`--stage` que difiere en un insumo con efecto (`--postcondition 2`) es "
        "una transición DISTINTA y debe registrarse (rc=0), nunca tragarse como "
        f"no-op; rc={second.returncode}: {second.stdout!r} {second.stderr!r}")

    state = ready.read_state()
    stage_entries = entries_with(
        state, transition="delivery", stage=STAGE_TOKEN)
    assert len(stage_entries) == 2, (
        "PD-10/PD-12 violada (B2): dos postcondiciones distintas del mismo "
        "paquete con la misma etiqueta son DOS entradas (el insumo con efecto "
        "entra en la identidad de PD-10 y una transición distinta se registra "
        f"como nueva); hay {len(stage_entries)} entrada(s) de esa etapa (antes "
        f"{len(entries(before))}, después {len(entries(state))}): el resultado "
        "de la 2ª quedó sin registrar")
    keys = [e.get("transition_key") for e in stage_entries]
    assert all(isinstance(k, str) and TRANSITION_DIGEST_RE.match(k)
               for k in keys) and keys[0] != keys[1], (
        "PD-10 violada (B2): cada postcondición registrada es una transición "
        "con su PROPIA clave (dos insumos con efecto distintos ⇒ dos claves): "
        f"{keys!r}")
    assert outcome_for(state, "1") == "green", (
        "PD-12 violada (B2): `postconditions_status` debe llevar la 1ª "
        f"postcondición escrita: {state.get(POSTCONDITIONS_FIELD)!r}")
    assert outcome_for(state, "2") == "green", (
        "PD-12 violada (B2): `postconditions_status` debe quedar con LAS DOS "
        "postcondiciones escritas (antes de la corrección la 2ª se perdía en un "
        f"no-op que afirmaba «no effects»): {state.get(POSTCONDITIONS_FIELD)!r}")
    assert ready.validate_state().returncode == 0, (
        "PD-12 violada: el state con las dos entradas debe seguir siendo "
        "coherente")


def test_b2_pd10_pd12_two_advances_with_the_same_stage_are_two_entries(
        prepared: _Fixture) -> None:
    """PD-10 + PD-12 (B2): dos `advance` con la MISMA etiqueta y distinto
    `--current-stage` (ambos en el vocabulario cerrado) son DOS transiciones
    distintas ⇒ **DOS** entradas, y el state refleja el **último** valor
    declarado. La 2ª no puede tragarse como no-op.

    RED hoy (defecto B2): `--current-stage` está fuera de la clave, así que la
    2ª invocación devuelve rc=0 «no-op, no effects», el avance no se registra y
    `current_stage` no refleja el último valor → falla por ASERCIÓN.
    """
    before = prepared.read_state()

    first = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--current-stage", "review")
    assert first.returncode == 0, (
        "PD-10 violada: el 1º `advance --current-stage review` debe registrarse "
        f"(rc=0); rc={first.returncode}: {first.stdout!r} {first.stderr!r}")

    second = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--current-stage", "merge")
    assert second.returncode == 0, (
        "PD-10/PD-12 violada (B2): un `advance` con la misma etiqueta y otro "
        "`--current-stage` es una transición DISTINTA y debe registrarse "
        f"(rc=0); rc={second.returncode}: {second.stdout!r} {second.stderr!r}")

    state = prepared.read_state()
    stage_entries = entries_with(
        state, transition="advance", stage=STAGE_TOKEN)
    assert len(stage_entries) == 2, (
        "PD-10/PD-12 violada (B2): dos `advance` con la misma etiqueta y "
        "distinto `--current-stage` son DOS entradas (el `current_stage` "
        f"declarado entra en la identidad); hay {len(stage_entries)} (antes "
        f"{len(entries(before))}, después {len(entries(state))})")
    keys = [e.get("transition_key") for e in stage_entries]
    assert all(isinstance(k, str) and k for k in keys) and keys[0] != keys[1], (
        "PD-10 violada (B2): cada `advance` registrado lleva su propia clave "
        f"(dos `current_stage` distintos ⇒ dos claves): {keys!r}")
    assert state.get("current_stage") == "merge", (
        "PD-12 violada (B2): el state debe reflejar el ÚLTIMO valor declarado "
        f"(`merge`): {state.get('current_stage')!r}")
    assert prepared.validate_state().returncode == 0, (
        "PD-12 violada: el state con los dos avances debe seguir siendo "
        "coherente")


def test_pd11_pd10_noop_is_independent_of_the_head_after_later_appends(
        prepared: _Fixture) -> None:
    """PD-11 / D-7 (B2): el no-op es INDEPENDIENTE de la cabeza. Con dos
    transiciones ya anexadas (la 2ª después de la 1ª), repetir la PRIMERA
    invocación de forma idéntica → rc=0, **sin** una tercera entrada, con el
    state **byte a byte idéntico** al que dejaron los appends, y salida que
    **nombra la entrada existente** (su `transition_key`).

    Control declarado: este caso corre HOY (la clave vieja ya distingue esas dos
    etiquetas) y el contrato enmendado no puede perderlo — la clave corregida
    debe seguir reconociendo una repetición idéntica aunque no sea la cabeza.
    """
    before = prepared.read_state()

    first = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--substage", "green")
    assert first.returncode == 0, (
        "PD-10 violada: la 1ª transición debe registrarse (rc=0); rc="
        f"{first.returncode}: {first.stdout!r} {first.stderr!r}")
    other = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN_ALT,
        "--substage", "red")
    assert other.returncode == 0, (
        "PD-12 violada: una etiqueta distinta es una entrada nueva (rc=0); rc="
        f"{other.returncode}: {other.stdout!r} {other.stderr!r}")

    after_appends = prepared.state_bytes()
    count_after_appends = len(entries(prepared.read_state()))
    first_entries = entries_with(
        prepared.read_state(), transition="advance", stage=STAGE_TOKEN)
    assert len(first_entries) == 1, (
        "precondición (fixture): debe haber UNA entrada de la primera "
        f"invocación: {len(first_entries)}")
    key = first_entries[0].get("transition_key")
    assert isinstance(key, str) and key, (
        f"PD-10 violada: la entrada anexada debe llevar su `transition_key`: {key!r}")
    assert count_after_appends == len(entries(before)) + 2, (
        "precondición (fixture): las dos invocaciones distintas anexan DOS "
        f"entradas (antes {len(entries(before))}, después {count_after_appends})")

    repeat = prepared.register_transition(
        "--transition", "advance", "--stage", STAGE_TOKEN,
        "--substage", "green")

    assert repeat.returncode == 0, (
        "PD-11 violada: repetir la composición idéntica de la primera "
        f"invocación debe ser un no-op exitoso (rc=0); rc={repeat.returncode}: "
        f"{repeat.stdout!r} {repeat.stderr!r}")
    assert len(entries(prepared.read_state())) == count_after_appends, (
        "PD-11 violada: la repetición idéntica NO debe anexar una tercera "
        f"entrada (siguen {count_after_appends})")
    assert prepared.state_bytes() == after_appends, (
        "PD-11 violada: el no-op debe dejar el state byte a byte idéntico al de "
        "los appends previos (no depende de la cabeza, D-7)")
    assert key in (repeat.stdout + repeat.stderr), (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key!r}): {repeat.stdout!r} {repeat.stderr!r}")


def test_pd10_entry_carries_a_recomputable_transition_key_payload(
        ready: _Fixture) -> None:
    """PD-10 / §2.2 (B2): la entrada lleva el **payload canónico** de la
    identidad como clave NUEVA y aditiva `transition_key_payload`, de modo que
    la identidad es **verificable desde el state**: recomputar el sha256 de esa
    serialización canónica declarada (`json.dumps(payload, ensure_ascii=False,
    sort_keys=True, separators=(",", ":"))` sobre UTF-8) devuelve el
    `transition_key` de la entrada.

    RED hoy (defecto B2): la entrada no lleva el payload (§2.2 lo declara
    aditivo) → falla por ASERCIÓN.
    """
    proc = ready.delivery("--postcondition", "1", "--outcome", "green")
    assert proc.returncode == 0, (
        "PD-10 violada: la transición debe registrarse (rc=0) para llevar el "
        f"payload de su identidad; rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")

    entry = last_entry(ready.read_state())
    payload = entry.get(PAYLOAD_KEY)
    assert isinstance(payload, dict) and payload, (
        "PD-10 violada (B2): la entrada debe llevar el payload canónico de la "
        "identidad como clave nueva y aditiva `transition_key_payload` (§2.2), "
        "para que la identidad sea comprobable desde el state: "
        f"{entry.get(PAYLOAD_KEY)!r}")
    recomputed = canonical_digest(payload)
    assert recomputed == entry.get("transition_key"), (
        "PD-10 violada (B2): el `transition_key` debe recomputarse desde el "
        "payload escrito con la serialización canónica declarada (sha256 sobre "
        f"bytes UTF-8): recomputado {recomputed!r}, entrada "
        f"{entry.get('transition_key')!r}, payload {payload!r}")


def test_pd10_payload_declares_the_identity_tuple_and_the_effect_inputs(
        ready: _Fixture) -> None:
    """PD-10 (B2): el payload escrito declara la **tupla** de la identidad y los
    **insumos con efecto** de ESTA invocación: la postcondición **resuelta** con
    su `outcome` (`{"n": <str>, "outcome": <red|green>}`), y los digests
    **resueltos** por el CLI (el valor que la entrada escribe, no el afirmado).
    Un delivery no declara `resolution` (sólo la clase `disposition`).

    RED hoy (defecto B2): no hay payload escrito → falla por ASERCIÓN.
    """
    proc = ready.delivery("--postcondition", "1", "--outcome", "green")
    assert proc.returncode == 0, (
        "PD-10 violada: la transición debe registrarse (rc=0) para declarar el "
        f"payload de su identidad; rc={proc.returncode}: {proc.stdout!r} "
        f"{proc.stderr!r}")

    state = ready.read_state()
    entry = last_entry(state)
    payload = entry.get(PAYLOAD_KEY)
    assert isinstance(payload, dict), (
        "PD-10 violada (B2): falta `transition_key_payload` en la entrada: "
        f"{payload!r}")

    for field, expected in (
        ("execution_id", state["execution"]["id"]),
        ("feature_id", FEATURE_ID),
        ("transition", "delivery"),
        ("stage", STAGE_TOKEN),
        ("packet_id", ready.packet_id),
        ("resolution", None),
    ):
        assert payload.get(field) == expected, (
            "PD-10 violada: el payload de la identidad debe declarar el campo "
            f"{field!r} con el valor resuelto {expected!r}: "
            f"{payload.get(field)!r} (payload {payload!r})")

    postcondition = payload.get("postcondition")
    assert isinstance(postcondition, dict), (
        "PD-10 violada (B2): el payload debe llevar la postcondición RESUELTA "
        f"de la invocación (`--postcondition 1 --outcome green`): {postcondition!r}")
    assert str(postcondition.get("n")) == "1", (
        "PD-10 violada: `postcondition.n` se normaliza como la clave del state "
        f"(`str(n)`): {postcondition.get('n')!r}")
    assert postcondition.get("outcome") == "green", (
        "PD-10 violada: la postcondición del payload lleva su `outcome` "
        f"resuelto: {postcondition.get('outcome')!r}")
    assert payload.get("receipt_sha256") == entry.get("receipt_sha256"), (
        "PD-10 violada: los digests del payload son los RESUELTOS (el valor que "
        f"la entrada escribe): payload {payload.get('receipt_sha256')!r}, "
        f"entrada {entry.get('receipt_sha256')!r}")


def test_pd11_noop_names_the_entry_and_declares_the_annotation_not_written(
        ready: _Fixture) -> None:
    """PD-11 (B2): el no-op **no es mudo**. Repetir los mismos insumos con
    efecto cambiando SÓLO la anotación (`--note`/`--by`, fuera del payload) →
    rc=0, sin segunda entrada y con el state byte a byte idéntico (la anotación
    NO se escribe), y la salida **nombra la entrada existente** y **declara**
    que la anotación de esta invocación no se escribió, en vez de afirmar un
    no-op sin más.

    RED hoy (defecto B2): la salida del no-op es «no-op, no effects» y no
    declara nada sobre la anotación → falla por ASERCIÓN (sobre la salida real
    del subproceso, sin decidir el significado de una prosa).
    """
    first = ready.delivery()
    assert first.returncode == 0, (
        "PD-11 violada: la primera invocación debe registrar la transición "
        f"(rc=0); rc={first.returncode}: {first.stdout!r} {first.stderr!r}")
    before_repeat = ready.state_bytes()
    count_before = len(entries(ready.read_state()))
    key = last_entry(ready.read_state()).get("transition_key")
    assert isinstance(key, str) and key, (
        f"PD-10 violada: la entrada existente debe llevar su clave: {key!r}")

    second = ready.delivery("--note", NOTE_TEXT, "--by", NOTE_ROLE)
    out = second.stdout + second.stderr

    assert second.returncode == 0, (
        "PD-11 violada: la anotación (`--note`/`--by`) queda FUERA del payload, "
        "así que la invocación sigue siendo idéntica y su repetición debe ser un "
        f"no-op exitoso (rc=0); rc={second.returncode}: {out!r}")
    assert ready.state_bytes() == before_repeat, (
        "PD-11 violada: la anotación de esta invocación NO se escribe; el state "
        "debe quedar byte a byte idéntico al de la primera invocación")
    assert len(entries(ready.read_state())) == count_before, (
        "PD-11 violada: el no-op no debe anexar una segunda entrada "
        f"(siguen {count_before})")
    assert key in out, (
        "PD-11 violada: la salida del no-op debe nombrar la entrada existente "
        f"(su `transition_key` {key!r}): {out!r}")
    declared = out.lower()
    assert "note" in declared or "annot" in declared, (
        "PD-11 violada (B2): el no-op debe DECLARAR que la anotación de esta "
        "invocación no se escribió (el contrato vigente lo fija: «la salida "
        "nombra la entrada existente y declara que la anotación … no se "
        "escribió»), en vez de afirmar un no-op sin más; la salida real fue "
        f"{out!r}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
