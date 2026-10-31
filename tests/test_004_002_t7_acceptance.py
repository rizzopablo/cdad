#!/usr/bin/env python3
"""004-002 T7 — Matriz integral de aceptación (test-writer, primer paquete v2).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(criterios de aceptación 1–8, PD-1..PD-12) + plan.md (T7, I1–I11).

Objetivo: un mapa verificable de cada postcondición hacia los tests
existentes (suites T1–T6: tests/test_004_002_*.py) y tests nuevos SOLO para
los huecos reales confirmados con evidencia. El mapa es el docstring de este
módulo; los meta-tests anclan las citas a los suites (si un test citado
desaparece o cambia de nombre, T7 falla).

Superficie observable bajo prueba: los mismos CLI/guard black-box que T1–T6
(proyectos sintéticos en tempdirs; instalación aislada del producto — patrón
LandingInstall de test_004_002_t6_landing.py — para la matriz desde producto
instalado; ninguna escritura en este repo salvo este archivo).

## Tabla de trazabilidad PD/criterio → suite/test

| Contrato                                   | Cobertura (suite → tests clave)                                                                                  |
|--------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| PD-1 (política única, propuesta)           | T1: test_004_002_t1_policy.py TestPd1* (test_pd1_policy_found_only_at_docs_cdad_policy, test_pd1_exact_field_set_extra_fields_invalid, test_pd1_missing_schema_field_invalid, test_pd1_propose_policy_deterministic_and_no_writes, test_pd1_propose_without_policy_yields_validate_pass, test_pd1_policy_self_classified_as_policy); t1_reviewfix: test_b3_propose_policy_with_prepare_options_fails_without_writes, test_pvalid_propose_invalid_layout_fails_without_emitting. Citado. |
| PD-2 (clasificación inequívoca)            | T1: test_004_002_t1_policy.py TestPd2* (rejects_absolute_paths, rejects_dotdot_escape, rejects_symlink_escape, documentation_over_implementation_rejected, documentation_over_tests_rejected, redundant_same_class_overlap_valid, test_pd2_cdad_layout_classification, conventional_src, colocated, odoo, tests_inside_implementation_are_extracted, test_name_outside_declared_locations_is_not_test); t1_reviewfix: test_b1_* (×2), test_b2_policy_symlink_outside_rejected_*, test_o2_documentation_file_not_overlapping_implementation_root; t56_reviewfix: TestB6GuardTildePaths. Citado. |
| PD-3 (bootstrap autorizado)                | T2: test_004_002_t2_bootstrap.py TestPd3* (implicit_bootstrap_creates_v2_context_binding_and_packet, standalone_bootstrap_without_epic, negatives ×7); t2_reviewfix: test_f1_reuse_with_revoked_delegation_rejected, test_f1_reuse_with_done_feature_rejected, test_f2_terminal_epic_stage_rejected; w1_delegation: TestW1* (14 tests I2/W-1, W-1b, W-1c). Citado. |
| PD-4 (identidad y reanudación)             | T2: test_004_002_t2_bootstrap.py test_pd4_role_change_keeps_execution_id, test_pd4_active_packet_prepared_or_dispatched_blocks_replacement, test_pd4_resume_packet_returns_identical_bytes_without_changes, test_pd4_resume_packet_with_modifying_options_fails; t2_reviewfix: test_f3_resume_with_single_changed_objective_fails, test_f4_resume_packet_path_traversal_rejected, test_f4_resume_with_tampered_packet_md_rejected_without_bytes, test_i7_resume_with_any_ordinary_option_fails_with_prepared_packet; t56_reviewfix: TestB7ResumeAfterReconcile (I11). **Hueco G1 confirmado** → nuevo: test_pd4_resume_from_other_session_keeps_identity_and_bytes (este módulo). |
| PD-5 (snapshot y reconciliación)           | T3: test_004_002_t3_durable.py TestPd5* (context_and_packet_record_policy_hash_with_verifiable_snapshot, policy_bytes_change_blocks_prepare_resume_and_dispatch, reconcile_accepts_matching_sha_and_decision_ref, reconcile_negatives_rejected_without_writes, reconcile_rejected_with_pending_packet); t3_reviewfix: test_f4a_reconcile_adopts_new_implementation_roots, test_f4b_reconcile_with_invalid_policy_is_rejected, test_f5_validate_state_is_valid_immediately_after_reconcile, test_f6_published_packet_carries_verifiable_policy_snapshot; t34_reviewfix2: test_a2_reconcile_plus_record_rejected_no_writes, test_a2_reconcile_plus_ordinary_options_rejected_no_writes; t34_reviewfix3: test_r1_reconcile_plus_input_rejected_no_writes; t56_reviewfix: TestB7ResumeAfterReconcile (I11). Citado. |
| PD-6 (observaciones, sin recepción)        | T4: test_004_002_t4_dispatch.py (15 tests test_pd6_i8_*); t34_reviewfix2: test_b2_provenance_keys_outside_observed_fields_rejected, test_b4_record_rejects_ordinary_options, test_b5_multi_runtime_with_capitals_rejected, test_b4_record_locked_out_while_prepare_in_critical_section. Citado. |
| PD-7 (scopes derivados)                    | T5: test_004_002_t5_runtime.py TestPd7I9DerivedMaps (test_writer_cdad_layout_maps, maps_conventional_and_colocated_layouts, maps_odoo_layout, policy_edit_deny_for_every_derived_role); t5_reviewfix: test_reviewfix_b1_guard_blocks_policy_and_derived_edits, test_reviewfix_b3_nested_tests_dir_not_amplified, test_reviewfix_b1_derived_edit_deny_on_agents_dir. Citado. |
| PD-8 (mecanismo + activación)              | T5: test_004_002_t5_runtime.py TestPd8I9Publication (publica/manifest/ajenos/byte a byte), TestPd8I9DerivedLifecycle (a mano, regeneración), TestPd8I10CcGuard (denies_read, allows_tests, denies_scoped_grep_glob, blocks_unscoped, denies_implementer_edit, blocks_on_invalid_policy, blocks_when_cli_unfindable, legacy_smoke, guard_odoo); t5_reviewfix: test_reviewfix_b2_unscoped_paths_block_with_narrow_msg, test_reviewfix_b4_glob_pattern_escaping_blocked, test_reviewfix_b5_guard_uses_claude_project_dir, test_reviewfix_r1_sibling_prefix_collision_blocked, test_reviewfix_r6_multiedit_notebookedit_mediated, test_reviewfix_r2_removed_source_orphan_derived_retired, test_reviewfix_r3, test_reviewfix_r7, test_reviewfix_r9; t56_reviewfix: TestB6GuardTildePaths. Citado (activación OpenCode y CC reales: guard C2 de plan.md). |
| PD-9 (temporales/accion externas)          | T1: test_004_002_t1_policy.py TestPd9* (rejects_dotdot_in_temporary_roots, rejects_absolute_temporary_root, rejects_temporal_overlapping_product, empty_list_never_grants_temporary, declared_temporary_root_classifies_temporary); t1_reviewfix: test_o2_implementation_file_not_overlapping_temporary_root, test_o3_empty_list_classifies_scratch_anything_txt_unclassified, test_b1_temporary_root_over_declared_colocated_tests_rejected. Citado. |
| PD-10 (adopción hacia adelante)            | T2: test_004_002_t2_bootstrap.py TestPd10ForwardAdoption (v1_present_without_flag_fails_demanding_new_execution, new_execution_flag_creates_v2_leaving_v1_intact, migrate_execution_option_does_not_exist); T6: test_004_002_t6_landing.py TestPd10ExplicitV1Context; trazabilidad de fixtures v1: docs/specs/004-002-project-execution-bootstrap/v1-fixture-trace.md. Citado. |
| PD-11 (exclusión y recuperación)           | T3: test_004_002_t3_durable.py TestPd11InterruptAndRecover (fail_at_each_point_rc97, recovery_after_each_fail_point — los CINCO puntos), TestPd11ConcurrencyAndLock (concurrent_prepare_denied_without_writes_then_works, lock_not_orphaned_when_holder_process_dies); t34_reviewfix2: test_a1_rejected_b_keeps_a_lock_and_c_is_rejected, test_a3_fd_over_retired_lock_inode_is_rejected, test_a4_recovery_preserves_foreign_txn_dir_and_all_files, test_b1_state_write_failure_leaves_no_published_record; t34_reviewfix3: test_r2_retry_after_crash_between_renames_completes_transition; t3_reviewfix: test_f1_lock_file_survives_successful_prepare, test_f2_pause_at_reserved_id_blocks_b_and_a_publishes, test_f3_recovery_keeps_foreign_file_inside_existing_txn_dir. **Sin hueco de cobertura; anclado** → meta-test test_t7_t3_interruption_citation_is_resolvable (este módulo). |
| PD-12 (instalado, legacy/standalone)       | T6: test_004_002_t6_landing.py TestPd12InstallConsumesStaging, TestPd12InstalledConsumerFlow (flujo completo v2 desde instalación aislada + standalone), TestPd12RuntimeMechanismsFromInstall (I9/I10 desde install), TestPd12LegacyIntake; t56_reviewfix: test_reviewfix_opt4_architect_without_active_epic_diagnostic. **Hueco G2 confirmado** (matriz 4 layouts × 4 consumidores en UN recorrido parametrizado desde producto instalado) → nuevo: TestT7LayoutsConsumersMatrix (este módulo). |
| PD-13 (recorrido real 004-002)             | Evidencia documental del repo: docs/specs/004-002-project-execution-bootstrap/{cut-c.md, dispatch-ledger.md, supervision-record.md, evidence/}. No es suite automatizable por test-writer; disposada por el scribe/reviewer en el cierre. |
| Criterio 1 (PD-1..12 trazados, negativos)  | Esta tabla completa. Los casos negativos de publicación/conservación están citados arriba por PD. |
| Criterio 2 (matriz de layouts × consumidores) | T6 (standalone/legacy globales) + T5 (mapas por layout, sintético). **Hueco G2** → nuevo: TestT7LayoutsConsumersMatrix — CDAD, convencional, co-ubicado, Odoo × v2 nuevo, v2 reanudado, legacy sin contexto, standalone con spec aprobada, en un solo recorrido desde el producto instalado. No incluye migración v1 (fuera de alcance, PD-10). |
| Criterio 3 (derivación y activación real)  | T5 test_004_002_t5_runtime.py (mapas semánticos I9 + guard real C2 I10) + t5_reviewfix + t56 (B6). Evidencia usa la forma real de cada herramienta; servicio de fondo OpenCode y su disposición quedan en la evidencia del recorrido (cut-c/ledgers), no en este suite. |
| Criterio 4 (5 puntos + concurrente PD-11)  | Anclado por meta-test test_t7_t3_interruption_citation_is_resolvable → T3 pasan los cinco puntos y el caso concurrente. |
| Criterio 5 (validadores vigentes, fixtures v1 trazadas) | v1-fixture-trace.md + el conjunto T1–T6 en verde (corridas de este paquete). |
| Criterio 6 (corte C revisado y hashes)     | Evidencia documental: cut-c.md §1–6, evidence/cut-c-v1-packets.sha256. No es suite. |
| Criterio 7 (recorrido PD-13, fricción)     | Evidencia documental: supervision-record.md, cut-c.md §4–6 (W-1/W-1b/W-1c). No es suite. |
| Criterio 8 (guía reproducible desde instalado) | T6: TestPd12InstalledConsumerFlow — el flujo completo (propuesta→materialización→bootstrap→reanudación→registro) corre desde la instalación aislada sin el checkout en el camino de ejecución. Citado. |

Regla de este paquete (plan T7): "no repitas lo que ya cubren los suites
T1–T6; refiérelos". Toda aserción nueva deriva de la postcondición citada;
si un test nuevo falla contra el producto actual (T1–T6 cerrados), se
reporta como defecto de producto y NO se ajusta la aserción para que pase.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    PACKET_BEGIN,
    read_state,
    tree_snapshot,
)
import test_004_002_t3_durable as t3
from test_004_002_t6_landing import (
    CONSUMER_EPIC,
    LandingInstall,
    consumer_state,
    published_packets,
    v1_execution_document,
    v2_execution_docs,
    write_consumer_authority_and_contract,
    write_consumer_state,
    write_git_project,
)

# Los cinco puntos de interrupción exigidos por PD-11/plan I5 (texto de spec).
PD11_FIVE_POINTS = (
    "reserved-id",
    "context-written",
    "packet-written",
    "before-state",
    "after-state",
)


# ------------------------------------------------------- PD-11 (criterio 4): cita anclada


class TestT7Pd11InterruptionCitation(unittest.TestCase):
    """Criterio 4 / PD-11: la tabla de T7 cita los cinco puntos de
    interrupción y el caso concurrente; la cita debe poder resolvverse en
    test_004_002_t3_durable.py (si T3 renombra o retira, T7 falla)."""

    def test_t7_t3_interruption_citation_is_resolvable(self) -> None:
        """Criterio 4: FAIL_AT_POINTS de T3 == los cinco puntos de la spec
        (I5) y los tests de interrupción/recuperación/concurrencia existen
        tal como los cita la tabla de trazabilidad."""
        self.assertEqual(
            tuple(t3.FAIL_AT_POINTS), PD11_FIVE_POINTS,
            msg="PD-11/I5: la tabla cita CINCO puntos; T3 varió el gancho "
                f"CDAD_TEST_FAIL_AT: {t3.FAIL_AT_POINTS}")
        for cls, names in (
            (t3.TestPd11InterruptAndRecover, (
                "test_pd11_fail_at_each_point_rc97_without_packet_output",
                "test_pd11_recovery_after_each_fail_point_coherent_or_retained",
            )),
            (t3.TestPd11ConcurrencyAndLock, (
                "test_pd11_concurrent_prepare_denied_without_writes_then_works",
                "test_pd11_lock_not_orphaned_when_holder_process_dies",
            )),
        ):
            for name in names:
                with self.subTest(test=name):
                    self.assertTrue(
                        hasattr(cls, name),
                        msg=f"PD-11/criterio 4: la tabla cita {cls.__name__}"
                            f".{name} y el test no existe (T3 cambió o lo "
                            f"retiró sin trazabilidad)")


# --------------------------------------- PD-4 (hueco G1): reanudación entre sesiones


class TestT7Pd4ResumeAcrossSessions(LandingInstall):
    """PD-4 (hueco G1): reanudar un paquete v2 desde OTRA sesión/runtime
    (proceso nuevo, cwd ajeno al proyecto, sin ninguna variable CDAD_*)
    conserva execution_id, packet_id y bytes; no muta el árbol.

    Evidencia del hueco: T2 cubre resume en la MISMA invocación de entorno
    (cwd=repo) y el cambio de rol conservando execution_id
    (test_pd4_role_change_keeps_execution_id, test_pd4_resume_packet_returns_identical_bytes_without_changes);
    ninguna suite existente demuestra la invariancia de identidad entre
    sesiones/runtimes (la spec PD-4: "cambiar rol, runtime, modelo o sesión
    conservan execution_id"; "reanudar conserva packet_id y bytes").
    """

    def _run_other_session(self, root: Path, args: list[str]) -> subprocess.CompletedProcess:
        """Invocación del CLI instalado como OTRA sesión: cwd distinto del
        proyecto y del repo, entorno sin variables CDAD_* (simulación
        observable de otro runtime/sesión; el paquete v2 no lleva identidad
        de runtime — son observaciones, PD-4)."""
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_") or key in ("PYTHONPATH",):
                env.pop(key, None)
        return subprocess.run(
            [sys.executable, str(self.installed_cli()), *args],
            cwd=str(self._tmp.name),  # cwd AJENO al proyecto consumidor
            env=env, text=True, capture_output=True,
        )

    def test_pd4_resume_from_other_session_keeps_identity_and_bytes(self) -> None:
        """PD-4: bootstrap v2 → resume en otra sesión → bytes idénticos,
        packet_id activo intacto, execution_id único sin cambios, árbol íntegro."""
        temp = tempfile.mkdtemp(prefix="cdad-t7-pd4-")
        self.addCleanup(__import__("shutil").rmtree, temp, ignore_errors=True)
        root = Path(temp) / "consumer"
        write_git_project(root)
        write_consumer_authority_and_contract(root)

        # El dueño materializa la política EXACTAMENTE como la propuesta
        # (flujo T6: propuesta determinista verbatim).
        proposal = self.run_installed(root, "prepare", "--project-root",
                                      str(root), "--propose-policy")
        self.assertEqual(
            proposal.returncode, 0,
            msg=f"precondición: propuesta falló: {proposal.stderr}")
        (root / "docs" / "cdad-policy.json").write_text(
            proposal.stdout, encoding="utf-8")
        write_consumer_state(root, consumer_state())

        # Bootstrap v2 (sesión 1).
        boot = self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "T7 PD-4 bootstrap sesión 1")
        self.assertEqual(
            boot.returncode, 0,
            msg=f"precondición: bootstrap falló: {boot.stderr}")
        self.assertTrue(
            boot.stdout.startswith(PACKET_BEGIN),
            msg="precondición: el bootstrap no imprimió el paquete")
        packet_id = next(iter(published_packets(root)))
        packet_bytes = (root / ".cdad" / "packets" / packet_id
                        / "PACKET.md").read_bytes()
        execs_before = v2_execution_docs(root)
        self.assertEqual(
            len(execs_before), 1, msg=f"precondición: contextos {execs_before}")
        state_before = read_state(root)
        tree_before = tree_snapshot(root)

        # Reanudación desde OTRA sesión (hueco G1).
        resume = self._run_other_session(
            root, ["prepare", "--project-root", str(root),
                   "--resume-packet", packet_id])
        self.assertEqual(
            resume.returncode, 0,
            msg=f"PD-4: la reanudación desde otra sesión falló: "
                f"{resume.stderr}")
        self.assertEqual(
            resume.stdout, packet_bytes.decode("utf-8"),
            msg="PD-4: la reanudación entre sesiones no devolvió los bytes "
                "idénticos del paquete")
        # Identidad: mismo execution_id único, mismo packet_id activo.
        execs_after = v2_execution_docs(root)
        self.assertEqual(
            sorted(execs_after), sorted(execs_before),
            msg="PD-4: la reanudación entre sesiones cambió el execution_id")
        self.assertEqual(
            read_state(root).get("active_packet", {}).get("id"), packet_id,
            msg="PD-4: la reanudación entre sesiones cambió el packet_id activo")
        self.assertEqual(
            read_state(root).get("execution", {}).get("id"),
            state_before.get("execution", {}).get("id"),
            msg="PD-4: el binding del state cambió tras la reanudación")
        # Nada del árbol mutó (contexto, paquete, state: bytes preservados).
        self.assertEqual(
            tree_snapshot(root), tree_before,
            msg="PD-4: la reanudación entre sesiones modificó el árbol")


# ------------------------------------------ matriz (hueco G2): layouts × consumidores


# Política válida de tres campos para cada layout (clasificación T1/T5).
T7_LAYOUT_POLICIES: dict[str, dict] = {
    "cdad": {
        "test_roots": ["tests"],
        "implementation_roots": ["agents", "skills", "scripts",
                                 "sources", "build"],
        "implementation_files": ["install.sh"],
        "documentation_roots": ["docs"],
        "colocated_test_roots": ["scripts", "agents"],
        "colocated_test_prefixes": ["test_"],
        "colocated_test_suffixes": ["_test.py"],
    },
    "conventional": {
        "test_roots": ["tests"],
        "implementation_roots": ["src", "lib"],
        "documentation_roots": ["docs"],
        "colocated_test_roots": ["src", "lib"],
        "colocated_test_prefixes": ["test_"],
        "colocated_test_suffixes": ["_test.py"],
    },
    "colocated": {
        "test_roots": [],
        "implementation_roots": ["mypkg"],
        "documentation_roots": ["docs"],
        "colocated_test_roots": ["mypkg"],
        "colocated_test_prefixes": ["test_"],
        "colocated_test_suffixes": ["_test.py"],
    },
    "odoo": {
        "test_roots": ["addons/m/tests"],
        "implementation_roots": ["addons/m/models", "addons/m/views"],
        "documentation_roots": ["docs"],
        "colocated_test_prefixes": ["test_"],
        "colocated_test_suffixes": ["_test.py"],
    },
}

# Sonda PD-2 por layout: ruta relativa → clase esperada (semántica T1).
T7_LAYOUT_PROBES: dict[str, tuple[tuple[str, str], ...]] = {
    "cdad": (
        ("scripts/x.py", "implementation"),
        ("tests/test_a.py", "test"),
        ("scripts/test_h.py", "colocated-test"),
    ),
    "conventional": (
        ("src/app.py", "implementation"),
        ("tests/test_a.py", "test"),
        ("src/test_mod.py", "colocated-test"),
    ),
    "colocated": (
        ("mypkg/mod.py", "implementation"),
        ("mypkg/mod_test.py", "colocated-test"),
    ),
    "odoo": (
        ("addons/m/models/m.py", "implementation"),
        ("addons/m/tests/test_m.py", "test"),
    ),
}


class TestT7LayoutsConsumersMatrix(LandingInstall):
    """Criterio 2 (hueco G2): la matriz layouts × consumidores en UN solo
    recorrido parametrizado desde el producto instalado (patrón
    LandingInstall de T6). El checkout de este repo nunca es la ruta de
    ejecución del consumidor (PD-12).

    Celdas por layout (cdad, conventional, colocated, odoo):
      - v2-nuevo:      bootstrap implícito → contexto v2 (schema_version 2,
                       epic del proyecto), paquete publicado.
      - v2-reanudado:  resume desde otra sesión (cwd env ajenos) → bytes
                       idénticos, identidad intacta, árbol íntegro.
      - legacy:        PROYECTO SIN POLÍTICA + documento v1 con el
                       path_policy del layout → intake legacy conservado:
                       paquete publicado, NINGÚN contexto v2, v1 íntegro.
      - standalone:    spec aprobada, active_epic null → bootstrap sin
                       fabricar epic (epic_id null en el contexto v2).

    Clasificación PD-2 del layout desde el CLI instalado (validate-policy
    --classify) como sonda de derivación por celda v2 y standalone.
    """

    def _new_consumer(self, prefix: str) -> Path:
        temp = tempfile.mkdtemp(prefix=prefix)
        self.addCleanup(__import__("shutil").rmtree, temp, ignore_errors=True)
        root = Path(temp) / "consumer"
        write_git_project(root)
        write_consumer_authority_and_contract(root)
        return root

    def _write_layout_policy(self, root: Path, layout: str) -> Path:
        path = root / "docs" / "cdad-policy.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        doc = {"schema_version": 1, "path_policy": T7_LAYOUT_POLICIES[layout],
               "temporary_roots": [".cdad/tmp"]}
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def _classify(self, root: Path, relpath: str) -> str:
        """PD-2: una invocación por ruta (robusto ante nargs/append, T1)."""
        proc = self.run_installed(
            root, "validate-policy", "--project-root", str(root),
            "--classify", relpath)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"criterio 2/PD-2: classify {relpath} falló: {proc.stderr}")
        for line in proc.stdout.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2 and parts[0].strip() == relpath:
                return parts[1].strip()
        self.fail(
            msg=f"criterio 2/PD-2: la salida de classify no contuvo "
                f"{relpath!r}: {proc.stdout!r}")

    def _prepare(self, root: Path, objective: str) -> subprocess.CompletedProcess:
        return self.run_installed(
            root, "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", objective)

    # -- celdas ------------------------------------------------------------

    def _cell_v2_new_and_resumed(self, layout: str) -> None:
        root = self._new_consumer(prefix="cdad-t7-mtx-v2-")
        self._write_layout_policy(root, layout)
        write_consumer_state(root, consumer_state())
        # Sonda de clasificación del layout (derivación PD-2, CLI instalado).
        for relpath, want in T7_LAYOUT_PROBES[layout]:
            with self.subTest(cell="classify", layout=layout, ruta=relpath):
                self.assertEqual(
                    self._classify(root, relpath), want,
                    msg=f"criterio 2/PD-2 ({layout}): {relpath} no clasifica "
                        f"{want}")

        # v2-nuevo: bootstrap implícito desde la instalación aislada.
        with self.subTest(cell="v2-nuevo", layout=layout):
            proc = self._prepare(root, f"T7 matriz {layout} v2 nuevo")
            self.assertEqual(
                proc.returncode, 0,
                msg=f"criterio 2 ({layout}/v2-nuevo): bootstrap falló: "
                    f"{proc.stdout} {proc.stderr}")
            self.assertTrue(
                proc.stdout.startswith(PACKET_BEGIN),
                msg=f"criterio 2 ({layout}/v2-nuevo): sin paquete canónico")
            docs = v2_execution_docs(root)
            self.assertEqual(
                len(docs), 1,
                msg=f"criterio 2 ({layout}/v2-nuevo): contextos {sorted(docs)}")
            execution_id, doc = next(iter(docs.items()))
            self.assertEqual(
                doc.get("schema_version"), 2,
                msg=f"criterio 2 ({layout}/v2-nuevo): contexto no es v2")
            self.assertEqual(
                doc.get("execution", doc).get("epic_id"), CONSUMER_EPIC,
                msg=f"criterio 2 ({layout}/v2-nuevo): el consumidor v2 perdió "
                    f"su epic")
            self.assertEqual(
                json.loads(
                    (root / "docs" / ".cdad-state.json").read_text(
                        encoding="utf-8")).get("execution", {}).get("id"),
                execution_id,
                msg=f"criterio 2 ({layout}/v2-nuevo): state no referencia el "
                    f"contexto")
            self.assertEqual(
                len(published_packets(root)), 1,
                msg=f"criterio 2 ({layout}/v2-nuevo): sin paquete publicado")

        # v2-reanudado: resume desde OTRA sesión (cwd/env ajenos).
        with self.subTest(cell="v2-reanudado", layout=layout):
            packet_id = next(iter(published_packets(root)))
            packet_bytes = (root / ".cdad" / "packets" / packet_id
                            / "PACKET.md").read_bytes()
            env = os.environ.copy()
            for key in list(env):
                if key.startswith("CDAD_") or key == "PYTHONPATH":
                    env.pop(key, None)
            proc = subprocess.run(
                [sys.executable, str(self.installed_cli()), "prepare",
                 "--project-root", str(root), "--resume-packet", packet_id],
                cwd=str(self._tmp.name), env=env, text=True,
                capture_output=True)
            self.assertEqual(
                proc.returncode, 0,
                msg=f"criterio 2 ({layout}/v2-reanudado): resume falló: "
                    f"{proc.stderr}")
            self.assertEqual(
                proc.stdout, packet_bytes.decode("utf-8"),
                msg=f"criterio 2 ({layout}/v2-reanudado): bytes no idénticos "
                    f"(PD-4)")
            self.assertEqual(
                sorted(v2_execution_docs(root)),
                [execution_id],
                msg=f"criterio 2 ({layout}/v2-reanudado): identidad alterada")
            self.assertEqual(
                read_state(root).get("active_packet", {}).get("id"),
                packet_id,
                msg=f"criterio 2 ({layout}/v2-reanudado): packet_id activo "
                    f"alterado")
            self.assertEqual(
                published_packets(root)[packet_id], packet_bytes,
                msg=f"criterio 2 ({layout}/v2-reanudado): bytes en disco "
                    f"alterados")

    def _cell_legacy(self, layout: str) -> None:
        """Consumidor legacy SIN contexto (sin política): su documento v1
        lleva el path_policy del layout; la selección v1 implícita ya NO
        conserva el intake (sustitución N-3 de PD-12/I4-refinado, D2, por
        PC-04/010-004 §4.1/§7 + INV-11)."""
        with self.subTest(cell="legacy", layout=layout):
            root = self._new_consumer(prefix="cdad-t7-mtx-legacy-")
            cdad = root / ".cdad"
            cdad.mkdir()
            v1_path = cdad / "execution.json"
            doc = v1_execution_document()
            pp = dict(doc["path_policy"])
            pp["test_roots"] = T7_LAYOUT_POLICIES[layout]["test_roots"]
            pp["implementation_roots"] = (
                T7_LAYOUT_POLICIES[layout]["implementation_roots"])
            if "colocated_test_roots" in T7_LAYOUT_POLICIES[layout]:
                pp["colocated_test_roots"] = (
                    T7_LAYOUT_POLICIES[layout]["colocated_test_roots"])
            doc["path_policy"] = pp
            v1_path.write_text(
                json.dumps(doc, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            v1_bytes = v1_path.read_bytes()
            write_consumer_state(root, consumer_state())
            self.assertFalse(
                (root / "docs" / "cdad-policy.json").exists(),
                msg="estructura del fixture: el consumidor legacy no lleva "
                    "política")

            proc = self._prepare(root, f"T7 matriz {layout} legacy intake")
            # PC-04/INV-11: la selección v1 implícita sin policy (PD-12 de
            # 004-002:115) se SUSTITUYE (owner-decision-v2-new-assignments,
            # 010-004 §7 N-3): rechazo antes de publicar, sin paquete ni
            # efectos persistentes.
            self.assertNotEqual(
                proc.returncode, 0,
                msg=f"criterio 2 ({layout}/legacy): la selección v1 "
                    "implícita sin policy debe rechazarse antes de publicar "
                    "(PC-04, 010-004 §4.1/§7); prepare respondió exit 0 con "
                    f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
            self.assertEqual(
                proc.stdout, "",
                msg=f"criterio 2 ({layout}/legacy): el rechazo PC-04 no debe "
                    "publicar paquete (stdout vacío exigido)")
            self.assertEqual(
                published_packets(root), {},
                msg=f"criterio 2 ({layout}/legacy): el rechazo PC-04 publicó "
                    "un paquete (INV-11)")
            self.assertEqual(
                v1_path.read_bytes(), v1_bytes,
                msg=f"criterio 2 ({layout}/legacy): el documento v1 fue "
                    "modificado (PD-10)")
            self.assertEqual(
                v2_execution_docs(root), {},
                msg=f"criterio 2 ({layout}/legacy): el rechazo PC-04 "
                    "fabricó un contexto v2 (§4.1: no se copia, convierte "
                    "ni reubica el contexto para hacerla pasar)")
            post_state = read_state(root)
            self.assertIsNone(
                post_state["execution"],
                msg=f"criterio 2 ({layout}/legacy): el rechazo PC-04 dejó "
                    "binding v2 en state (INV-11)")
            self.assertIsNone(
                post_state["active_packet"],
                msg=f"criterio 2 ({layout}/legacy): el rechazo PC-04 dejó "
                    "paquete activo en state (INV-11)")

    def _cell_standalone(self, layout: str) -> None:
        """Consumidor standalone CON spec aprobada (active_epic null): el
        bootstrap no fabrica un epic (PD-12, T6 opt-4/standalone)."""
        with self.subTest(cell="standalone", layout=layout):
            root = self._new_consumer(prefix="cdad-t7-mtx-standalone-")
            self._write_layout_policy(root, layout)
            write_consumer_state(root, consumer_state(epic=None))
            proc = self._prepare(
                root, f"T7 matriz {layout} standalone")
            self.assertEqual(
                proc.returncode, 0,
                msg=f"criterio 2 ({layout}/standalone): bootstrap falló: "
                    f"{proc.stdout} {proc.stderr}")
            docs = v2_execution_docs(root)
            self.assertEqual(
                len(docs), 1,
                msg=f"criterio 2 ({layout}/standalone): contextos {sorted(docs)}")
            _, doc = next(iter(docs.items()))
            execution = doc.get("execution", doc)
            self.assertIsNone(
                execution.get("epic_id"),
                msg=f"criterio 2 ({layout}/standalone): fabricó el epic "
                    f"{execution.get('epic_id')!r}")
            self.assertTrue(
                proc.stdout.startswith(PACKET_BEGIN),
                msg=f"criterio 2 ({layout}/standalone): sin paquete canónico")
            self.assertEqual(
                len(published_packets(root)), 1,
                msg=f"criterio 2 ({layout}/standalone): sin paquete publicado")

    def test_criterio2_full_matrix_single_walk_from_install(self) -> None:
        """Criterio 2: UN solo recorrido parametrizado que cruza los 4
        layouts (CDAD, convencional, co-ubicado, Odoo) con los 4
        consumidores (v2 nuevo, v2 reanudado, legacy sin contexto,
        standalone con spec aprobada), todo desde el producto instalado."""
        for layout in ("cdad", "conventional", "colocated", "odoo"):
            self._cell_v2_new_and_resumed(layout)
            self._cell_legacy(layout)
            self._cell_standalone(layout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
