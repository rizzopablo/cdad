#!/usr/bin/env python3
"""Black-box contract tests for feature 003-001, Task 1 (P4/P5/P6).

004-002 T6 PRE-GREEN (PD-10, paquete
004-002-project-execution-bootstrap-test-writer-red-012): el portador del
contexto deja de ser el documento v1 artesanal (`schema_version: 1`, con
runtime/modelo en la identidad) y pasa a ser un portador v2 REAL obtenido por
la interfaz pública (`prepare --propose-policy` -> materialización del dueño ->
registros I2 -> bootstrap con `prepare`); traza:
docs/specs/004-002-project-execution-bootstrap/v1-fixture-trace.md (filas 3-9).
La identidad v2 no contiene runtime/modelo global (spec §2): las celdas de la
matriz que los afirmaban se retiran con trazabilidad; el resto se conserva.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "install.sh"
PACKET_CLI = REPO_ROOT / "scripts" / "cdad_packet.py"

EPIC_ID = "epic-003-context-efficiency"
FEATURE_ID = "003-001-role-packets"
AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"


from tests.product_staging import product_root


_V2_CARRIER: dict | None = None


def _bootstrap_v2_carrier() -> dict:
    """Obtiene un portador v2 REAL por la interfaz pública (PD-3/I2/I3).

    El proyecto sintético replica el layout del PacketFixture (src, lib,
    tests, docs, install.sh, README.md); ninguna lectura de implementación:
    solo se ejecuta el CLI en tempdir propio. La política la PROPONE prepare
    y la materializa el 'dueño' del fixture (PD-1); la autoridad son los
    registros I2 del plan (stage_history + hitl_delegation con scope); el
    bootstrap (prepare) publica el contexto v2, el binding y el paquete.
    """
    tmp = tempfile.mkdtemp(prefix="cdad-v2-carrier-")
    try:
        root = Path(tmp) / "carrier"
        for rel in ("src", "lib", "tests"):
            (root / rel).mkdir(parents=True)
        (root / "docs").mkdir(parents=True)
        (root / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
        (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (root / "tests" / "exact_test.py").write_text("# test\n", encoding="utf-8")

        def run(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(PACKET_CLI), *args],
                cwd=str(root),
                text=True,
                capture_output=True,
                check=False,
            )

        proposal = run("prepare", "--project-root", str(root), "--propose-policy")
        assert proposal.returncode == 0, (
            f"fixture: propose-policy falló: {proposal.stderr}"
        )
        policy_bytes = proposal.stdout
        (root / "docs" / "cdad-policy.json").write_text(policy_bytes, encoding="utf-8")

        authority = root / AUTHORITY_REF
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Authorized execution fixture\n", encoding="utf-8")
        contract_dir = root / "docs" / "specs" / FEATURE_ID
        contract_dir.mkdir(parents=True, exist_ok=True)
        (contract_dir / "spec.md").write_bytes(
            b"# Contract fixture for test-writer/red\n"
        )

        carrier_state = {
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
            "stage_history": [
                {
                    "feature": FEATURE_ID,
                    "stage": "specification",
                    "approved_by": "Pablo",
                    "approved_at": "2026-09-29T00:00:00Z",
                    # 005-001 T1 (D3): forma pineada — path + sha256 del
                    # contrato del fixture (migración mecánica del RED).
                    "contract_path": f"docs/specs/{FEATURE_ID}/spec.md",
                    "contract_sha256": hashlib.sha256(
                        b"# Contract fixture for test-writer/red\n"
                    ).hexdigest(),
                }
            ],
            "approver": "Pablo",
            "last_updated": "2026-09-29T00:00:00Z",
            "execution": None,
            "active_packet": None,
            "hitl_delegation": {
                "status": "active",
                "epic_id": EPIC_ID,
                "source": AUTHORITY_REF,
                "scope": EPIC_ID,
                "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
            },
        }
        (root / "docs" / ".cdad-state.json").write_text(
            json.dumps(carrier_state) + "\n", encoding="utf-8"
        )

        bootstrap = run(
            "prepare",
            "--project-root",
            str(root),
            "--role",
            "test-writer",
            "--substage",
            "red",
            "--objective",
            "v2 carrier fixture bootstrap",
        )
        assert bootstrap.returncode == 0, (
            f"fixture: bootstrap del portador v2 falló: {bootstrap.stderr}"
        )
        contexts = sorted((root / ".cdad" / "executions").glob("*/execution.json"))
        assert len(contexts) == 1, (
            f"fixture: el bootstrap publicó {len(contexts)} contextos, se "
            "esperaba exactamente uno"
        )
        document = json.loads(contexts[0].read_text(encoding="utf-8"))
        assert document.get("schema_version") == 2, (
            "fixture: el contexto publicado no es v2"
        )
        return {
            "document": document,
            "policy_bytes": policy_bytes,
            "execution_id": document["execution"]["id"],
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def v2_carrier() -> dict:
    """Portador v2 real, bootstrap una única vez por sesión de tests."""
    global _V2_CARRIER
    if _V2_CARRIER is None:
        _V2_CARRIER = _bootstrap_v2_carrier()
    return _V2_CARRIER


EXECUTION_ID = v2_carrier()["execution_id"]
MODEL_POLICY = v2_carrier()["document"]["execution"]["model_policy"]


def execution_document() -> dict:
    """Portador v2 real (identidad sin runtime/modelo global; spec v2 §2)."""
    return copy.deepcopy(v2_carrier()["document"])


def state_document(
    execution: dict, *, active_packet: object = None, contract_sha256: str | None = None
) -> dict:
    binding = copy.deepcopy(execution["execution"])
    spec_entry = {
        "feature": FEATURE_ID,
        "stage": "specification",
        "approved_by": "Pablo",
        "approved_at": "2026-09-29T00:00:00Z",
    }
    if contract_sha256 is not None:
        # 005-001 T1 (D3): forma pineada de la aprobación de spec (path +
        # sha256); la forma previa sin pin queda como fixture posible.
        spec_entry["contract_path"] = f"docs/specs/{FEATURE_ID}/spec.md"
        spec_entry["contract_sha256"] = contract_sha256
    entry: dict = spec_entry
    return {
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
        "postconditions_status": {"1": "pending", "2": "pending", "3": "pending"},
        # Registro I2 (plan 004-002): la aprobación del contrato se acredita
        # con stage_history (feature, stage "specification", approved_by).
        "stage_history": [entry],
        "approver": "Codex (agent-delegated)",
        "last_updated": "2026-09-17T00:00:00Z",
        "execution": binding,
        "active_packet": active_packet,
        "hitl_delegation": {
            "status": "active",
            "epic_id": EPIC_ID,
            "source": AUTHORITY_REF,
            "scope": EPIC_ID,
            "expires_on": ["epic-closed", "epic-cancelled", "user-revoked"],
        },
    }


def active_packet_document() -> dict:
    """Return the complete public active-packet snapshot from the P5 contract."""
    return {
        "id": "packet-003-001-t1",
        "role": "test-writer",
        "substage": "red",
        "status": "prepared",
        "packet_version": 1,
        "contract_kind": "approved-feature-spec",
        "contract_sha256": "a" * 64,
    }


class StateFixture:
    """Reusable on-disk fixture for the P4/P5 state-binding matrix."""

    def __init__(self, root: Path, execution: dict, state: dict, *, write_authority: bool = True) -> None:
        self.root = root
        self.execution = execution
        self.state = state
        self.write_authority = write_authority
        self.execution_path = root / "EXECUTION.json"

    def write(self) -> None:
        authority = self.root / AUTHORITY_REF
        if self.write_authority:
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Authorized execution fixture\n", encoding="utf-8")
        policy_path = self.root / "docs" / "cdad-policy.json"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        # La política es la misma que aceptó el bootstrap del portador (PD-1:
        # materialización del dueño; el binding lleva su sha256).
        policy_path.write_text(v2_carrier()["policy_bytes"], encoding="utf-8")
        state_path = self.root / "docs" / ".cdad-state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(self.state), encoding="utf-8")
        self.execution_path.write_text(json.dumps(self.execution), encoding="utf-8")


def invoke_validate_state(fixture: StateFixture) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(PACKET_CLI),
            "validate-state",
            "--project-root",
            str(fixture.root),
            "--execution-context",
            str(fixture.execution_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class TestInstallRootDryRun(unittest.TestCase):
    """P6 RED: dry-run destinations must be confined to CDAD_INSTALL_ROOT."""

    DESTINATION_PATTERNS = (
        re.compile(r"DRY-RUN COPY .+ -> (?P<path>/\S+)$"),
        re.compile(r"DRY-RUN MARKER (?P<path>/\S+) = "),
    )
    REQUIRED_PREFIXES = (
        ".config/opencode/agents",
        ".config/opencode/skills",
        ".agents/skills",
        ".claude/agents",
        ".claude/skills",
        ".claude/cdad-scripts",
    )

    def test_p6_dry_run_confines_every_destination_to_explicit_install_root(self) -> None:
        # Portabilidad (review-t1/T6): el dry-run consume el staging garantizado
        # (checkout real o copia temporal generada) y nunca escribe en él.
        install_product = product_root()
        with tempfile.TemporaryDirectory(prefix="cdad-install-root-") as install_dir:
            install_root = Path(install_dir).resolve()
            env = os.environ.copy()
            env["CDAD_INSTALL_ROOT"] = str(install_root)
            env["CDAD_SKILL_EXTRA_DIRS"] = ""

            result = subprocess.run(
                ["bash", str(install_product / "install.sh"), "--dry-run", "--basic"],
                cwd=install_product,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            destinations: list[Path] = []
            for line in result.stdout.splitlines():
                for pattern in self.DESTINATION_PATTERNS:
                    match = pattern.search(line)
                    if match:
                        destinations.append(Path(match.group("path")).resolve())
                        break

            self.assertTrue(destinations, "dry-run did not publish any install destinations")
            outside = [
                str(path)
                for path in destinations
                if os.path.commonpath((str(install_root), str(path))) != str(install_root)
            ]
            self.assertEqual(
                outside,
                [],
                "dry-run ignored CDAD_INSTALL_ROOT; destinations escaped it: "
                + ", ".join(outside),
            )

            relative_destinations = [path.relative_to(install_root) for path in destinations]
            for required in self.REQUIRED_PREFIXES:
                required_path = Path(required)
                self.assertTrue(
                    any(path == required_path or required_path in path.parents for path in relative_destinations),
                    f"dry-run omitted documented install layout prefix {required}",
                )


class TestStateBindingMatrixWhenCliAvailable(unittest.TestCase):
    """P4/P5 complete public state-binding matrix."""

    def test_p4_p5_state_binding_matrix_or_report_interface_blocked(self) -> None:
        self.assertTrue(PACKET_CLI.is_file(), f"public CLI unavailable at {PACKET_CLI}")

        # Celda válida (portador v2 real del bootstrap; la identidad v2 no
        # contiene runtime/modelo global — spec §2 —, de modo que la pareja
        # (runtime, scope) de la matriz v1 ya no es una celda de identidad).
        execution = execution_document()
        self._assert_state_result(execution, state_document(execution), expected_ok=True)

        invalid_mutations = {
            "execution id mismatch": lambda state: state["execution"].__setitem__("id", "other"),
            "epic mismatch": lambda state: state["execution"].__setitem__("epic_id", "other-epic"),
            "feature mismatch": lambda state: state["execution"].__setitem__("feature_id", "other-feature"),
            "scope mismatch": lambda state: state["execution"].__setitem__("scope", "codex-construction"),
            "authority mismatch": lambda state: state["execution"].__setitem__(
                "authority_ref", "docs/other-authority.md"
            ),
            "model policy mismatch": lambda state: state["execution"].__setitem__(
                "model_policy", "other-policy"
            ),
            "policy hash mismatch": lambda state: state["execution"].__setitem__(
                "policy_sha256", "0" * 64
            ),
            "active epic mismatch": lambda state: state.__setitem__("active_epic", "other-epic"),
            "active feature mismatch": lambda state: state.__setitem__("active_feature", "other-feature"),
            "epic closed": lambda state: state.__setitem__("epic_stage", "done"),
            "delegation revoked": lambda state: state["hitl_delegation"].__setitem__("status", "revoked"),
            "delegation expired": lambda state: state["hitl_delegation"].__setitem__("status", "expired"),
            "feature done": lambda state: state["epic_features"][0].__setitem__("status", "done"),
            "feature cancelled": lambda state: state["epic_features"][0].__setitem__("status", "cancelled"),
            "feature outside epic": lambda state: state.__setitem__("epic_features", []),
            "delegation source mismatch": lambda state: state["hitl_delegation"].__setitem__(
                "source", "docs/other-authority.md"
            ),
        }
        execution = execution_document()
        for label, mutate in invalid_mutations.items():
            with self.subTest(invalid_binding=label):
                state = state_document(execution)
                mutate(state)
                self._assert_state_result(execution, state, expected_ok=False)

        # Celdas retiradas con trazabilidad (v1-fixture-trace.md, fila 3):
        # - "runtime mismatch" de identidad y las parejas no autorizadas
        #   (runtime, scope): la identidad v2 no lleva runtime/modelo global
        #   (PD-6: son observaciones por intento), y el emparejamiento
        #   runtime/scope era mecánica de la excepción epic-003-single-model.
        #   Un campo extra en el binding v2 es rechazado por esquema
        #   ("state.execution fields do not match the v2 binding schema").
        # - "invalid exception rejected before basic compatibility" y
        #   "ordinary basic without exception": la rama de excepción por
        #   política de modelos (ADR-010, epic-003) caduca con la spec v2
        #   (§2: la autoridad se resuelve de los registros vigentes sin
        #   ramificar por política de modelos). Ningún portador público v2
        #   puede expresar esas celdas; el reemplazo vigente es la regla I2
        #   standalone (bootstrap sin epic), ya en verde en
        #   test_004_002_t6_landing::TestPd12InstalledConsumerFlow.

        execution = execution_document()
        with self.subTest(invalid_binding="authority file absent"):
            self._assert_state_result(execution, state_document(execution), expected_ok=False, write_authority=False)

        with self.subTest(invalid_binding="authority cannot be inherited from shared repository"):
            state = state_document(execution)
            state["hitl_delegation"] = copy.deepcopy(state["hitl_delegation"])
            state["hitl_delegation"]["epic_id"] = "other-epic"
            self._assert_state_result(execution, state, expected_ok=False)

        with self.subTest(p5="active_packet null is valid"):
            self._assert_state_result(execution, state_document(execution, active_packet=None), expected_ok=True)

        with self.subTest(p5="incomplete active_packet is invalid"):
            self._assert_state_result(
                execution,
                state_document(execution, active_packet={"id": "packet-003-001-t1"}),
                expected_ok=False,
            )

    def test_p5_active_packet_validates_every_field_enum_and_role_substage_pair(self) -> None:
        execution = execution_document()
        baseline = active_packet_document()

        for status in ("prepared", "dispatched", "completed", "failed"):
            with self.subTest(valid_status=status):
                packet = copy.deepcopy(baseline)
                packet["status"] = status
                self._assert_state_result(
                    execution,
                    state_document(execution, active_packet=packet),
                    expected_ok=True,
                )

        for field in baseline:
            with self.subTest(missing_field=field):
                packet = copy.deepcopy(baseline)
                del packet[field]
                self._assert_state_result(
                    execution,
                    state_document(execution, active_packet=packet),
                    expected_ok=False,
                )

        invalid_values = {
            "id type": ("id", 3),
            "unknown role": ("role", "operator"),
            "unknown substage": ("substage", "deploy"),
            "unknown status": ("status", "pending"),
            "unsupported packet version": ("packet_version", 2),
            "unknown contract kind": ("contract_kind", "working-draft"),
            "malformed contract hash": ("contract_sha256", "A" * 64),
        }
        for label, (field, value) in invalid_values.items():
            with self.subTest(invalid_field=label):
                packet = copy.deepcopy(baseline)
                packet[field] = value
                self._assert_state_result(
                    execution,
                    state_document(execution, active_packet=packet),
                    expected_ok=False,
                )

        with self.subTest(invalid_pair="reviewer/green"):
            packet = copy.deepcopy(baseline)
            packet["role"] = "reviewer"
            packet["substage"] = "green"
            self._assert_state_result(
                execution,
                state_document(execution, active_packet=packet),
                expected_ok=False,
            )

    def _assert_state_result(
        self, execution: dict, state: dict, *, expected_ok: bool, write_authority: bool = True
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="cdad-state-fixture-") as project_dir:
            fixture = StateFixture(
                Path(project_dir), copy.deepcopy(execution), copy.deepcopy(state), write_authority=write_authority
            )
            fixture.write()
            result = invoke_validate_state(fixture)
            if expected_ok:
                self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            else:
                self.assertNotEqual(result.returncode, 0, "invalid state binding was accepted")
                self.assertTrue(result.stderr.strip(), "invalid state binding lacked stderr diagnostic")


if __name__ == "__main__":
    unittest.main(verbosity=2)
