#!/usr/bin/env python3
"""004-002 T2 RED review-fix — hallazgos F1–F6 de review-t2 más las dos
mutaciones que sobrevivieron a la batería T2 (disposición del orquestador).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-1, PD-3, PD-4, PD-10) +
docs/specs/004-002-project-execution-bootstrap/review-t2.md.

Hallazgos (cada test nombra el suyo en la clase o el docstring):

- F1  reuse-omits-current-authority-checks (PD-3/PD-4)
- F2  authority-accepts-terminal-epic-and-prefix-scope (PD-3/I2)
- F3  resume-accepts-single-modifying-option (PD-4 / mutación sobreviviente 2)
- F4  resume-returns-unvalidated-bytes-traversal-and-tamper (PD-4)
- F5  publish-failures-leave-dirs-or-traceback (PD-3, contrato §2)
- F6  invalid-policy-location-falls-back-to-legacy (PD-1/PD-10)
- M1  mutación sobreviviente 1: hitl_delegation.source inexistente → rechazo.
      Excepción declarada: hoy el rechazo existe (test verde); es un test de
      regresión que debe romper si un cambio elimina la comprobación.
- M2  es la mutación sobreviviente 2, cubierta por el test de F3.

Micro-ciclo 2 (re-review T2, "Re-review (suplente...)" de review-t2.md):
- B1  autoridad source cambiado a OTRO archivo existente: reuse rechaza
      (verde), validate-state NO VALID (RED hoy) y resume puro rechazado
      (RED hoy).
- B2  F4 con argv puro (run_prepare inyectaba opciones ordinarias y I7
      rechazaba antes de llegar a la lógica de F4).
- B3  F3 e I7 con argv desde cero por opción y la lista completa de I7.
- O1  guard contra mutación M11: resume puro con delegación revocada →
      rc≠0 sin bytes (hoy pasa; debe romper si se elimina la verificación).

RED contra 91d0310: cada escenario de F1–F6 debe fallar hoy por
AssertionError que expresa la postcondición que falta (no un ImportError).
Fuentes de los escenarios: docs/specs/004-002-project-execution-bootstrap/
review-t2.md (sondas reproducibles del reviewer).

Superficie observable: `python3 scripts/cdad_packet.py prepare|validate-state
--project-root <raíz> ...` sobre proyectos sintéticos en tempdirs. No se lee
la implementación (skills/cdad-cycle/scripts/cdad_packet.py) y ningún
escenario escribe en este repositorio. Los reutilizables de fixture viven en
tests/test_004_002_t2_bootstrap.py (parte de tests/, no implementación).
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tests.test_004_002_t2_bootstrap as boot
REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "cdad_packet.py"

EPIC_ID = boot.EPIC_ID
FEATURE_ID = boot.FEATURE_ID
OTHER_FEATURE_ID = boot.OTHER_FEATURE_ID
AUTHORITY_REF = boot.AUTHORITY_REF
POLICY_FILE = boot.POLICY_FILE
STATE_FILE = boot.STATE_FILE
CONTRACT_FILE = boot.CONTRACT_FILE
PACKET_BEGIN = boot.PACKET_BEGIN
# 005-001 T1 (D3): los fixtures que agregan una entrada `specification` para
# OTHER_FEATURE_ID la insertan pineada y escriben el contrato correspondiente
# (migración mecánica del RED).
OTHER_CONTRACT_FILE = f"docs/specs/{OTHER_FEATURE_ID}/spec.md"
OTHER_CONTRACT_BYTES = b"# Spec fixture for 004-002 other active feature\n"
OTHER_CONTRACT_SHA256 = hashlib.sha256(OTHER_CONTRACT_BYTES).hexdigest()

v2_execution_docs = boot.v2_execution_docs
published_packets = boot.published_packets
tree_snapshot = boot.tree_snapshot
read_state = boot.read_state
write_state = boot.write_state
run_cli = boot.run_cli
prepare_args = boot.prepare_args
run_prepare = boot.run_prepare
run_validate_state = boot.run_validate_state
build_project = boot.build_project
state_document = boot.state_document


def pure_resume(root: Path, packet_id: str, *option: str) -> subprocess.CompletedProcess:
    """Reanudación con argv PURO, sin opciones ordinarias del modo ordinario
    (B2/B3 de la re-review T2: los helpers que inyectan --role/--substage/
    --objective hacen que I7 rechace antes de llegar a la lógica bajo
    prueba)."""
    return run_cli(["prepare", "--project-root", str(root),
                    "--resume-packet", packet_id, *option])


# ---------------------------------------------------------------- WS-F1


class RfCase(boot.ProjectTestCase):
    """Base: proyecto sintético válido; `first` opcionalmente bootstrap."""

    def prepare_ok(self, *extra: str, role: str = "test-writer",
                   substage: str = "red", objective: str = "T2 objective",
                   label: str) -> subprocess.CompletedProcess:
        args = prepare_args(self.root, role=role, substage=substage,
                            objective=objective, extra=extra)
        proc = run_cli(args)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: {proc.stdout} {proc.stderr}")
        return proc

    def require_bootstrap(self, objective: str = "T2 objective") -> str:
        """Precondición del escenario: primer prepare (bootstrap v2)."""
        proc = self.prepare_ok(label="primera preparación",
                               objective=objective)
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"primera preparación debe crear un único contexto v2: "
                f"{sorted(docs)}")
        return next(iter(docs))

    def require_bootstrap_completed(self, objective: str = "T2 objective") -> str:
        execution_id = self.require_bootstrap(objective=objective)
        state = read_state(self.root)
        state["active_packet"]["status"] = "completed"
        write_state(self.root, state)
        return execution_id


# ---------------------------------------------------------------- WS-F1


class TestF1ReuseValidatesCurrentState(RfCase):
    """WS-F1: reutilizar v2 omite comprobar autoridad y feature vigentes."""

    def _mutate_state(self, doc: dict) -> None:
        raise NotImplementedError

    def assert_reuse_rejected(self, label: str) -> None:
        execution_id = self.require_bootstrap_completed()
        state = read_state(self.root)
        self._mutate_state(state)
        write_state(self.root, state)
        snapshot = tree_snapshot(self.root)
        active_before = read_state(self.root)["active_packet"]
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0, msg=f"{label}: reutilización aceptada (rc=0)")
        self.assertEqual(
            proc.stdout, "", msg=f"{label}: stdout no vacío en fallo")
        self.assertNotIn("Traceback", proc.stderr, msg=f"{label}: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg=f"{label}: hubo publicación (árbol modificado)")
        self.assertEqual(
            read_state(self.root)["active_packet"], active_before,
            msg=f"{label}: active_packet cambió")
        self.assertEqual(
            sorted(v2_execution_docs(self.root)), [execution_id],
            msg=f"{label}: apareció otro execution_id")

    def test_f1_reuse_with_revoked_delegation_rejected(self) -> None:
        """WS-F1: completado el primer paquete, revocar hitl_delegation y
        reutilizar la v2 existente → rc≠0 sin publicación."""
        self._mutate_state = self._revoke
        self.assert_reuse_rejected("delegación revocada en reutilización")

    @staticmethod
    def _revoke(state: dict) -> None:
        state["hitl_delegation"]["status"] = "revoked"
        state["hitl_delegation"]["revoked_at"] = "2026-09-29T12:00:00Z"

    def test_f1_reuse_with_done_feature_rejected(self) -> None:
        """WS-F1: feature marcada done y reutilizar la v2 → rc≠0."""
        self._mutate_state = self._close_feature
        self.assert_reuse_rejected("feature done en reutilización")

    @staticmethod
    def _close_feature(state: dict) -> None:
        state["epic_features"][0]["status"] = "done"

    def test_f1_reuse_with_changed_active_feature_rejected_and_binding_kept(self) -> None:
        """WS-F1: active_feature sustituida y reutilizar la v2 → rc≠0; el
        binding (state.execution.feature_id) conserva la feature anterior."""
        execution_id = self.require_bootstrap_completed()
        state = read_state(self.root)
        state["active_feature"] = OTHER_FEATURE_ID
        state["epic_features"] = [{"id": OTHER_FEATURE_ID,
                                   "status": "in-progress"}]
        other_contract = self.root / OTHER_CONTRACT_FILE
        other_contract.parent.mkdir(parents=True, exist_ok=True)
        other_contract.write_bytes(OTHER_CONTRACT_BYTES)
        state["stage_history"].append({
            "feature": OTHER_FEATURE_ID,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-09-29T00:00:00Z",
            "contract_path": OTHER_CONTRACT_FILE,
            "contract_sha256": OTHER_CONTRACT_SHA256,
        })
        write_state(self.root, state)
        snapshot = tree_snapshot(self.root)
        binding_before = json.dumps(read_state(self.root)["execution"],
                                    sort_keys=True)
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="active_feature distinta: la reutilización v2 aceptó preparar")
        self.assertEqual(proc.stdout, "",
                         msg="reutilización fallida publicó stdout")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="reutilización fallida modificó el árbol")
        state_after = read_state(self.root)
        self.assertEqual(
            json.dumps(state_after["execution"], sort_keys=True),
            binding_before,
            msg="el binding state.execution cambió de feature")
        self.assertEqual(
            sorted(v2_execution_docs(self.root)), [execution_id],
            msg="active_feature distinta: creó otro execution_id")

    def test_f1_validate_state_not_valid_when_binding_contradicts_current_records(self) -> None:
        """WS-F1: con active_feature sustituida y el binding v2 de la feature
        anterior, validate-state NO responde VALID."""
        self.require_bootstrap_completed()
        state = read_state(self.root)
        state["active_feature"] = OTHER_FEATURE_ID
        state["epic_features"] = [{"id": OTHER_FEATURE_ID,
                                   "status": "in-progress"}]
        other_contract = self.root / OTHER_CONTRACT_FILE
        other_contract.parent.mkdir(parents=True, exist_ok=True)
        other_contract.write_bytes(OTHER_CONTRACT_BYTES)
        state["stage_history"].append({
            "feature": OTHER_FEATURE_ID,
            "stage": "specification",
            "approved_by": "Pablo",
            "approved_at": "2026-09-29T00:00:00Z",
            "contract_path": OTHER_CONTRACT_FILE,
            "contract_sha256": OTHER_CONTRACT_SHA256,
        })
        write_state(self.root, state)
        proc = run_validate_state(self.root)
        combined = proc.stdout + proc.stderr
        self.assertNotIn(
            "VALID", combined,
            msg=f"validate-state respondió VALID ante binding/active_feature "
                f"contradictorios: rc={proc.returncode}, out={combined!r}")


class TestF2AuthorityVigency(RfCase):
    """WS-F2: epic terminado y scope que comparte prefijo con el epic."""

    def test_f2_terminal_epic_stage_rejected(self) -> None:
        """WS-F2: epic_stage='epic-done' → rc≠0 sin publicación."""
        write_state(self.root, state_document())
        state = read_state(self.root)
        state["epic_stage"] = "epic-done"
        write_state(self.root, state)
        self.before = tree_snapshot(self.root)
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="epic_stage='epic-done' fue aceptado; el epic terminado no "
                "autoriza nueva preparación")
        self.assertEqual(
            proc.stdout, "", msg="epic terminado: stdout no vacío")
        self.assertNotIn("Traceback", proc.stderr, msg="epic terminado: traceback")
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg="epic terminado: hubo publicación (árbol modificado)")
        self.assert_state_unchanged()
        # Diagnóstico que menciona el estado del epic (específico, no genérico).
        self.assertIsNotNone(
            re.search(r"epic[-_ ]stage|epic[-_ ]done|epic", out, re.IGNORECASE),
            msg=f"diagnóstico no menciona el estado del epic: {out!r}")

    def test_f2_scope_with_prefix_only_of_authorised_epic_rejected(self) -> None:
        """WS-F2: scope='epic-004-single-source-planning-unrelated' (comparte
        prefijo con el epic activo) NO autoriza → rc≠0 sin publicación."""
        write_state(self.root, state_document())
        state = read_state(self.root)
        state["hitl_delegation"]["scope"] = EPIC_ID + "-unrelated"
        write_state(self.root, state)
        self.before = tree_snapshot(self.root)
        proc = run_prepare(self.root)
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"scope '{EPIC_ID}-unrelated' (sólo comparte prefijo con el "
                f"epic) fue aceptado como autoridad, I2/F2")
        self.assertEqual(proc.stdout, "", msg="scope-prefijo: stdout no vacío")
        self.assertNotIn("Traceback", proc.stderr,
                         msg="scope-prefijo: traceback")
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg="scope-prefijo: hubo publicación (árbol modificado)")
        self.assert_state_unchanged()


class TestF3ResumeSingleModifyingOption(RfCase):
    """WS-F3 y mutación sobreviviente 2 (misma garantía): una única opción
    modificadora en resume debe contrastarse con el encargo original del
    paquete almacenado, no detectarse por repetición."""

    def test_f3_resume_with_single_changed_objective_fails(self) -> None:
        """WS-F3: resume con UNA única opción `--objective` cuyo valor difiere
        del encargo original → rc≠0, sin bytes y con state intacto (mutación
        sobreviviente 2: hoy rc=0; el negativo previo sólo verificaba
        repetición, no incompatibilidad con el request)."""
        self.require_bootstrap_completed(objective="encargo original")
        packet_id = read_state(self.root)["active_packet"]["id"]
        snapshot = tree_snapshot(self.root)
        # B3 (re-review): argv desde cero; EXACTAMENTE una aparición de
        # --objective, con valor distinto del original (no un duplicado del
        # helper).
        proc = pure_resume(self.root, packet_id, "--objective", "CHANGED")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume con --objective único distinto del original fue "
                "aceptado (mutación sobreviviente: repetición ≠ incompatibilidad)")
        self.assertEqual(
            proc.stdout, "", msg="resume defectuoso publicó stdout")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="resume con valor cambiado modificó el árbol")
        self.assertEqual(
            read_state(self.root).get("active_packet", {}).get("id"),
            packet_id,
            msg="resume con valor cambiado cambió el packet_id activo")


class TestF4ResumeUnvalidatedBytes(RfCase):
    """WS-F4: resume devuelve contenido sin validar identidad ni
    confinamiento."""

    def test_f4_resume_packet_path_traversal_rejected(self) -> None:
        """WS-F4: `--resume-packet ../unrelated` → rc≠0 y sin bytes ajenos."""
        self.require_bootstrap_completed()
        packet_id = read_state(self.root)["active_packet"]["id"]
        self.assertTrue(packet_id, msg="precondición: sin packet_id activo")
        unrelated = self.root / ".cdad" / "unrelated"
        unrelated.mkdir(parents=True)
        (unrelated / "PACKET.md").write_text("UNRELATED BYTES\n",
                                             encoding="utf-8")
        snapshot = tree_snapshot(self.root)
        # B2 (re-review): argv puro; con las opciones del helper I7 rechazaría
        # antes de llegar a la validación de ruta de F4.
        proc = pure_resume(self.root, "../unrelated")
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume-packet resolvió '../unrelated' fuera del directorio "
                "de paquetes (sin validación de ruta, F4)")
        self.assertNotIn(
            "UNRELATED BYTES", proc.stdout,
            msg="resume-packet devolvió bytes de fuera de .cdad/packets")
        self.assertNotIn("Traceback", proc.stderr, msg="F4: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="resume con ruta de escape modificó el árbol")

    def test_f4_resume_with_tampered_packet_md_rejected_without_bytes(self) -> None:
        """WS-F4: PACKET.md adulterado → resume rc≠0 y NO devuelve bytes."""
        self.require_bootstrap_completed()
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_path = self.root / ".cdad" / "packets" / packet_id / "PACKET.md"
        packet_path.write_bytes(b"TAMPERED\n")
        state = read_state(self.root)
        snapshot = tree_snapshot(self.root)
        # B2 (re-review): argv puro; con las opciones del helper I7 rechazaría
        # antes de llegar a la verificación canónica de F4.
        proc = pure_resume(self.root, packet_id)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume devolvió un PACKET.md adulterado como si fuera "
                "canónico (F4)")
        self.assertEqual(
            proc.stdout, "",
            msg="resume de paquete adulterado devolvió bytes")
        self.assertNotIn("TAMPERED", proc.stdout,
                         msg="resume devolvió el contenido adulterado")
        self.assertNotIn("Traceback", proc.stderr, msg="F4: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="resume de paquete adulterado modificó el árbol")
        self.assertEqual(
            read_state(self.root).get("active_packet", {}).get("id"),
            packet_id,
            msg="resume del paquete adulterado cambió el packet_id activo")


class TestF5RollbackOfOrdinaryPublishingErrors(RfCase):
    """WS-F5: errores de publicación sin traceback ni directorios sobrantes
    creados por esta operación (rollback ordinario; la recuperación T3-11
    permanece fuera)."""

    def _assert_clean_failure(
        self, label: str, *, preexisting: tuple[str, ...] = (),
    ) -> None:
        """Fallo limpio: sin traceback, con diagnóstico, sin stdout y sin
        directorios creados por esta operación. Las rutas en `preexisting`
        existían antes del prepare: se respeta su contenido exacto (lo
        preexistente se preserva, PD-10/I7)."""
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0, msg=f"{label}: prepare aceptado")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg=f"{label}: fallo con traceback en lugar de diagnóstico")
        self.assertIsNotNone(
            re.search(r"error|denied|not a directory|in use|exist|failed", out,
                      re.IGNORECASE),
            msg=f"{label}: sin diagnóstico ({out!r})")
        self.assertEqual(
            proc.stdout, "", msg=f"{label}: stdout no vacío")
        for rel in (".cdad", ".cdad/executions", ".cdad/packets"):
            path = self.root / rel
            if rel in preexisting:
                self.assertTrue(
                    path.exists(),
                    msg=f"{label}: la operación retiró '{rel}' preexistente")
                continue
            self.assertFalse(
                path.exists(),
                msg=f"{label}: quedó '{rel}' creado por la operación fallida")
        state_after = read_state(self.root)
        self.assertIsNone(
            state_after.get("execution"), msg=f"{label}: state.execution ligado")
        self.assertIsNone(
            state_after.get("active_packet"),
            msg=f"{label}: state.active_packet ligado")

    def test_f5_packets_path_being_a_file_does_not_leave_dirs(self) -> None:
        """WS-F5: si `.cdad/packets` es un archivo PREEXISTENTE, prepare falla
        con diagnóstico (sin traceback), conserva los preexistentes (`.cdad` y
        `.cdad/packets` con sus bytes) y no deja `.cdad/executions` creado por
        la operación (F5)."""
        packets_path = self.root / ".cdad" / "packets"
        packets_path.parent.mkdir()
        packets_path.write_text("not a dir\n", encoding="utf-8")
        packets_bytes = packets_path.read_bytes()
        self._assert_clean_failure(
            ".cdad/packets es archivo", preexisting=(".cdad", ".cdad/packets"))
        self.assertEqual(
            packets_path.read_bytes(), packets_bytes,
            msg=".cdad/packets preexistente cambió su contenido")

    def test_f5_state_tmp_being_a_dir_fails_cleanly_without_new_dirs(self) -> None:
        """WS-F5: si `docs/.cdad-state.json.tmp` es un directorio, prepare
        falla sin traceback, con diagnóstico, y no deja `.cdad`,
        `.cdad/executions` ni `.cdad/packets` (creados por la operación)."""
        (self.root / "docs" / ".cdad-state.json.tmp").mkdir()
        self._assert_clean_failure(".cdad-state.json.tmp es directorio")


class TestF6NoLegacyFallbackOnInvalidPolicyLocation(RfCase):
    """WS-F6: ubicación de política existente pero no archivo → error sin
    fallback legacy (I4 refinado, PD-1/PD-10)."""

    def test_f6_policy_directory_with_v1_context_no_legacy_fallback(self) -> None:
        """WS-F6: docs/cdad-policy.json existente pero directorio (no archivo)
        con contexto v1 presente → rc≠0, sin paquete legacy y sin tocar el
        v1 (PD-1/PD-10)."""
        obj = boot.TestPd10ForwardAdoption(methodName="run")
        obj.root = self.root
        obj.write_v1_context()
        (self.root / POLICY_FILE).unlink()
        (self.root / POLICY_FILE).mkdir()
        self.assertEqual(
            (self.root / POLICY_FILE).is_dir(), True,
            msg="precondición: docs/cdad-policy.json debe ser un directorio")
        v1_bytes = (self.root / ".cdad" / "execution.json").read_bytes()
        self.before = tree_snapshot(self.root)
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="F6: ubicación de política no archivo activó el fallback "
                "legacy (rc=0) en contexto v1 (PD-1/PD-10)")
        self.assertNotIn("Traceback", proc.stderr, msg="F6: traceback")
        self.assertIsNotNone(
            re.search(r"policy|pol[íi]tica", out, re.IGNORECASE),
            msg=f"F6: diagnóstico no menciona la política: {out!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="F6: stdout no vacío (paquete legacy publicado)")
        self.assertEqual(
            (self.root / ".cdad" / "execution.json").read_bytes(), v1_bytes,
            msg="F6: el contexto v1 fue modificado")
        self.assertEqual(
            published_packets(self.root), {},
            msg="F6: se publicó un paquete legacy (fallback)")
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg="F6: hubo publicación parcial (árbol modificado)")


class TestB1AuthoritySourceMismatchAcrossProducers(RfCase):
    """B1 (re-review T2, BLOCKING): la comparación de autoridad
    (authority_ref == hitl_delegation.source) sólo se aplica en la selección
    de ejecución: con el `source` cambiado a OTRO archivo existente,
    reutilizar rechaza, pero validate-state da VALID y la reanudación pura
    reemite los bytes. Cada productor debe validar la vigencia de la
    autoridad contra los registros vigentes (PD-3/I2).
    """

    def _change_source_to_existing_file(self) -> None:
        """Apunta hitl_delegation.source a otro archivo existente del
        proyecto sintético (el contrato), no a uno inexistente."""
        state = read_state(self.root)
        self.assertTrue((self.root / CONTRACT_FILE).is_file(),
                        msg="precondición: el archivo source alternativo "
                            "debe existir")
        state["hitl_delegation"]["source"] = CONTRACT_FILE
        write_state(self.root, state)

    def test_b1_reuse_with_changed_source_is_rejected(self) -> None:
        """B1: reutilizar con hitl_delegation.source cambiado (archivo
        existente) → rc≠0 sin publicación (hoy ya se aplica en la selección)."""
        self.require_bootstrap_completed()
        self._change_source_to_existing_file()
        snapshot = tree_snapshot(self.root)
        active_before = read_state(self.root)["active_packet"]
        proc = run_prepare(self.root)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="reutilización con authority_ref != hitl_delegation.source "
                "fue aceptada (B1)")
        self.assertEqual(proc.stdout, "", msg="B1 reuse: stdout no vacío")
        self.assertNotIn("Traceback", proc.stderr, msg="B1 reuse: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="B1 reuse: hubo publicación (árbol modificado)")
        self.assertEqual(
            read_state(self.root)["active_packet"], active_before,
            msg="B1 reuse: active_packet cambió")

    def test_b1_validate_state_not_valid_with_changed_source(self) -> None:
        """B1: con el source cambiado, validate-state NO responde VALID
        (RED hoy: el binding y el source contradicen los registros)."""
        self.require_bootstrap_completed()
        self._change_source_to_existing_file()
        proc = run_validate_state(self.root)
        combined = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"validate-state aceptó authority_ref != hitl_delegation."
                f"source: rc={proc.returncode}, out={combined!r} (B1)")
        self.assertNotIn(
            "VALID", combined,
            msg=f"validate-state respondió VALID con el source cambiado: "
                f"{combined!r} (B1)")

    def test_b1_pure_resume_with_changed_source_rejected_without_bytes(self) -> None:
        """B1: resume puro (argv sin opciones ordinarias) con el source
        cambiado → rc≠0 y SIN devolver bytes (RED hoy: el resume reemite)."""
        self.require_bootstrap()  # activo en prepared: resume es el camino
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_bytes = published_packets(self.root)[packet_id]
        self._change_source_to_existing_file()
        snapshot = tree_snapshot(self.root)
        proc = pure_resume(self.root, packet_id)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume reemitió bytes con authority_ref != "
                "hitl_delegation.source (B1)")
        self.assertNotEqual(
            proc.stdout, packet_bytes.decode("utf-8"),
            msg="resume devolvió los bytes del paquete con el source "
                "cambiado (B1)")
        self.assertEqual(
            proc.stdout, "", msg="B1 resume: stdout con contenido")
        self.assertNotIn("Traceback", proc.stderr, msg="B1 resume: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="B1 resume: hubo escrituras en el árbol")


class TestO1PureResumeWithRevokedDelegation(RfCase):
    """O1 (re-review T2): guard contra la mutación M11 — resume puro con la
    delegación revocada debe rechazarse sin devolver bytes. Hoy el rechazo
    existe; el test debe romper si una edición elimina la verificación.
    """

    def test_o1_pure_resume_with_revoked_delegation_rejected_without_bytes(self) -> None:
        """O1: resume puro (argv sin opciones ordinarias) con
        hitl_delegation revocada → rc≠0 y sin bytes."""
        self.require_bootstrap()
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_bytes = published_packets(self.root)[packet_id]
        state = read_state(self.root)
        state["hitl_delegation"]["status"] = "revoked"
        state["hitl_delegation"]["revoked_at"] = "2026-09-29T12:00:00Z"
        write_state(self.root, state)
        snapshot = tree_snapshot(self.root)
        proc = pure_resume(self.root, packet_id)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="resume reemitió bytes con la delegación revocada (O1/M11)")
        self.assertNotEqual(
            proc.stdout, packet_bytes.decode("utf-8"),
            msg="resume devolvió los bytes del paquete con la delegación "
                "revocada (O1/M11)")
        self.assertEqual(
            proc.stdout, "", msg="O1: stdout con contenido")
        self.assertNotIn("Traceback", proc.stderr, msg="O1: traceback")
        self.assertEqual(
            tree_snapshot(self.root), snapshot,
            msg="O1: hubo escrituras en el árbol")


class TestMutation1SourceExistence(RfCase):
    """Mutación sobreviviente 1 (`missing-source-survivor`): si se elimina la
    comprobación de existencia del `source` de hitl_delegation, el test debe
    romper. Hoy, contra el productor actual, el rechazo existe y la aserción
    del test PASA (verde-on-propósito antes del RED del fix): es un test de
    regresión que mata la mutación."""

    def test_mutation1_nonexistent_delegation_source_is_rejected(self) -> None:
        """Mut-1: hitl_delegation activo cuyo `source` no existe en disco →
        prepare debe dar rc≠0 con diagnóstico y sin publicación; así, si una
        edición quita la comprobación de existencia del source, el test falla."""
        write_state(self.root, state_document())
        (self.root / AUTHORITY_REF).unlink()
        self.before = tree_snapshot(self.root)
        proc = run_prepare(self.root)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="hitl_delegation.source inexistente fue aceptado (mutación "
                "sobreviviente 1: si se elimina la comprobación, este test "
                "debe fallar)")
        self.assertEqual(
            proc.stdout, "", msg="source inexistente: stdout no vacío")
        self.assertNotIn("Traceback", proc.stderr, msg="mut-1: traceback")
        self.assertIsNotNone(
            re.search(r"authority|reference|source|hitl|delegaci", out,
                      re.IGNORECASE),
            msg=f"mut-1: sin diagnóstico nombrando la autoridad: {out!r}")
        self.assertEqual(
            tree_snapshot(self.root), self.before,
            msg="mut-1: hubo publicación parcial (árbol modificado)")
        self.assert_state_unchanged()


class TestI7ResumeAcceptsNoOrdinaryOptions(RfCase):
    """I7 (T2 review-fix, reanudación): `--resume-packet <id>` no acepta
    NINGUNA opción de preparación ordinaria; reanudar es reemitir los bytes
    verificados del paquete, no reconfigurarlo. Oráculo firmado en:
    docs/specs/004-002-project-execution-bootstrap/plan.md.

    B3 (re-review T2): cada subtest construye el argv desde cero con UNA sola
    opción ordinaria (las variantes con las tres opciones del helper no
    aíslan ninguna opción y las mutaciones M2b/M2c sobreviven), y cubre la
    lista completa de I7, incluidos valores idénticos al request almacenado.
    """

    # Lista completa de I7 (plan.md): role, substage, objective,
    # expected-output, out-dir, execution-context, new-execution, input,
    # read-scope, write-scope, invariant, evidence. Valores idénticos al
    # request del paquete activo cuando aplica (I7 rechaza igual). El marcador
    # {execution_context} se resuelve con el path real del contexto v2 para
    # que el único obstáculo sea el rechazo I7 (no un archivo inexistente).
    I7_CASES = (
        ("role-igual", ("--role", "test-writer")),
        ("substage-igual", ("--substage", "red")),
        ("objective-igual", ("--objective", "T2 objective")),
        ("objective-diferente", ("--objective", "encargo nuevo")),
        ("expected-output", ("--expected-output", "salida")),
        ("out-dir", ("--out-dir", "otros-paquetes")),
        ("execution-context", ("--execution-context", "{execution_context}")),
        ("new-execution", ("--new-execution",)),
        ("input", ("--input", "documento-observaciones.md")),
        ("read-scope", ("--read-scope", "src")),
        ("write-scope", ("--write-scope", "src")),
        ("invariant", ("--invariant", "PD-4")),
        ("evidence", ("--evidence", "evidencia.md")),
    )

    def test_i7_resume_with_any_ordinary_option_fails_with_prepared_packet(self) -> None:
        """I7: resume con cualquier opción ordinaria (incluso idéntica a la
        almacenada) → rc≠0, sin escrituras, con el paquete activo intacto en
        `prepared` (plan I7)."""
        execution_id = self.require_bootstrap()  # activo queda en prepared
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_bytes = published_packets(self.root)[packet_id]
        state_before = read_state(self.root)["active_packet"]
        self.assertEqual(
            state_before.get("status"), "prepared",
            msg=f"precondición: paquete activo no está prepared: "
                f"{state_before!r}")
        execution_context = str(self.root / ".cdad" / "executions" /
                                execution_id / "execution.json")
        for label, option in self.I7_CASES:
            option = tuple(v.replace("{execution_context}", execution_context)
                           for v in option)
            with self.subTest(opcion=label):
                snapshot = tree_snapshot(self.root)
                # argv desde cero: prepare --project-root X --resume-packet id
                # <opción> <valor>. Nada más (B3).
                proc = pure_resume(self.root, packet_id, *option)
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"I7 [{label}]: resume aceptó una opción ordinaria "
                        f"({option[0]}) con el paquete en prepared")
                self.assertNotIn(
                    "Traceback", proc.stderr,
                    msg=f"I7 [{label}]: fallo con traceback")
                self.assertEqual(
                    proc.stdout, "",
                    msg=f"I7 [{label}]: stdout no vacío en el rechazo")
                self.assertEqual(
                    tree_snapshot(self.root), snapshot,
                    msg=f"I7 [{label}]: hubo escrituras en el árbol")
                state_after = read_state(self.root)["active_packet"]
                self.assertEqual(
                    state_after, state_before,
                    msg=f"I7 [{label}]: active_packet cambió: "
                        f"{state_before!r} → {state_after!r}")
                self.assertEqual(
                    state_after.get("status"), "prepared",
                    msg=f"I7 [{label}]: el paquete no quedó en prepared")
                self.assertEqual(
                    published_packets(self.root).get(packet_id), packet_bytes,
                    msg=f"I7 [{label}]: los bytes del paquete cambiaron")
                self.assertEqual(
                    sorted(v2_execution_docs(self.root)), [execution_id],
                    msg=f"I7 [{label}]: cambió el execution_id")


if __name__ == "__main__":
    unittest.main(verbosity=2)
