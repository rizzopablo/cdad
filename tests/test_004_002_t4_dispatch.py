#!/usr/bin/env python3
"""004-002 T4 RED — Registro de intentos de despacho sin recepción (PD-6/I8).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-6, PD-5)
+ plan.md (decisión de interfaz I8 del orquestador).

Superficie observable bajo prueba (proyectos sintéticos T2 en tempdirs;
ninguna escritura en este repo):

    python3 scripts/cdad_packet.py prepare --project-root <raíz> \
        --record-dispatch <packet-id> --attempt-id <id> --input <obs.json>

El documento `--input` es JSON de claves cerradas (I8): runtime,
model_configured, model_reported, session, started_at (texto o null) y
provenance (objeto campo→fuente). Los modo de `prepare` son excluyentes: la
llamada de registro NO lleva --role/--substage/--objective; identity,
paquete, rol y subfase salen del paquete.

Mapa test → postcondición (PD-6/I8 salvo PD-5 en el último):

  1  two_roles_runtimes_separate_records  PD-6 para 1 / I8 ruta dispatches
  2  two_attempts_same_packet_separate          PD-6 para 1
  3  identical_record_idempotent                PD-6 para 1 / I8 idempotencia
  4  reused_attempt_id_conflicting_rejected     PD-6 para 1 / I8 sin sobrescribir
  5  all_fields_null_accepted                   PD-6 para 1 / I8 unknown null
  6  multi_runtime_rejected                     PD-6 para 1 / I8
  7  extra_keys_rejected_no_reception           PD-6 para 1 / I8 claves cerradas
  8  identity_fields_from_packet                PD-6 para 1 / I8 ids del paquete
  9  attempt_id_path_escapes_rejected           PD-6 para 1 / I8 nombre plano
 10  unknown_packet_id_rejected                 PD-6 para 1 / I8
 11  foreign_execution_packet_rejected          PD-6 para 1 / I8 otra ejecución
 12  prepared_to_dispatched_never_completed     PD-6 para 1 / I8 transición
 13  record_writes_only_dispatch_frontier       PD-6 para 1 (frontera 003-002)
 14  policy_unreconciled_change_blocks_record   PD-5 (bloqueo del registro)

RED hoy: la opción --record-dispatch no existe en el productor; cada aserción
positiva debe fallar por AssertionError ("opción ausente"), no por import ni
sintaxis. Nada de lectura de implementación.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    PACKET_BEGIN,
    POLICY_FILE,
    build_project,
    prepare_args,
    published_packets,
    read_state,
    run_cli,
    tree_snapshot,
    v2_execution_docs,
    write_state,
    state_document,
)

STATE_KEYS_FRONTIER = ("stage_history", "gates", "postconditions_status")
EXTRA_KEYS = ("result", "deliverable", "gate", "status")
IDENTITY_KEYS = ("execution_id", "packet_id", "role", "substage")
BAD_ATTEMPT_IDS = ("../escape", "sub/dir")


# ---------------------------------------------------------------- helpers


def iter_strings(obj) -> set:
    found: set = set()

    def walk(node) -> None:
        if isinstance(node, str):
            found.add(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(obj)
    return found


def observation_doc(**overrides) -> dict:
    doc = {
        "runtime": "opencode",
        "model_configured": "glm-5.3-flash",
        "model_reported": "glm-5.3-flash",
        "session": "ses-t4red-0001",
        "started_at": "2026-09-30T12:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }
    doc.update(overrides)
    return doc


def dispatch_path(root: Path, eid: str, attempt_id: str) -> Path:
    return (root / ".cdad" / "executions" / eid / "dispatches"
            / f"{attempt_id}.json")


def state_normalized(state) -> dict:
    """Copia comparable salvo el status del paquete activo (PD-6) y la
    marca temporal de auditoría del state."""
    doc = copy.deepcopy(state)
    doc.pop("last_updated", None)
    active = doc.get("active_packet")
    if isinstance(active, dict):
        active.pop("status", None)
    return doc


class DispatchCase(unittest.TestCase):
    """Base: proyecto sintético T2 con bootstrap v2 y paquete activo."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t4-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)

    # -- corridas CLI -----------------------------------------------------

    def run_prepare(self, root: Path, *extra: str, role: str = "test-writer",
                    substage: str = "red",
                    objective: str = "encargo T4") -> subprocess.CompletedProcess:
        return run_cli(prepare_args(root, role=role, substage=substage,
                                    objective=objective, extra=extra))

    def run_record(self, root: Path, packet_id: str, attempt_id: str,
                   input_path: Path) -> subprocess.CompletedProcess:
        return run_cli([
            "prepare", "--project-root", str(root),
            "--record-dispatch", packet_id,
            "--attempt-id", attempt_id,
            "--input", str(input_path),
        ])

    def out(self, proc: subprocess.CompletedProcess) -> str:
        return proc.stdout + proc.stderr

    # -- fixtures ---------------------------------------------------------

    def write_observation(self, name: str, doc: dict) -> Path:
        path = self.root / "docs" / name
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def bootstrap_ready(self) -> tuple[str, str]:
        """Precondición: bootstrap T2 + paquete activo (contexto único v2)."""
        proc = self.run_prepare(self.root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): el bootstrap debe tener éxito: "
                f"{self.out(proc)}")
        docs = v2_execution_docs(self.root)
        self.assertEqual(
            len(docs), 1,
            msg=f"precondición (fixture): un único contexto v2: {sorted(docs)}")
        execution_id = self.active_execution_id()
        packet_id = read_state(self.root)["active_packet"]["id"]
        self.assertTrue(
            published_packets(self.root).get(packet_id),
            msg="precondición (fixture): el paquete activo está publicado")
        return execution_id, packet_id

    def mark_completed(self) -> None:
        state = read_state(self.root)
        self.assertTrue(state.get("active_packet"),
                        msg="precondición (fixture): hay paquete activo")
        state["active_packet"]["status"] = "completed"
        write_state(self.root, state)

    def active_execution_id(self) -> str:
        state = read_state(self.root)
        eid = (state.get("execution") or {}).get("id")
        self.assertTrue(eid, msg="precondición (fixture): binding activo")
        return eid

    def read_dispatch(self, eid: str, attempt_id: str) -> bytes | None:
        path = dispatch_path(self.root, eid, attempt_id)
        return path.read_bytes() if path.is_file() else None

    def assert_no_traceback(self, proc: subprocess.CompletedProcess,
                            label: str) -> None:
        self.assertNotIn(
            "Traceback", proc.stderr, msg=f"{label}: fallo con traceback")

    def assert_option_exists(self, proc: subprocess.CompletedProcess) -> None:
        """Primera aserción de cada interacción con --record-dispatch: la
        opción debe existir (RED hoy = opción ausente, no otro motivo)."""
        self.assertNotIn(
            "unrecognized", self.out(proc),
            msg="--record-dispatch/--attempt-id/--input no existen aún "
                "(RED por opción ausente)")

    def assert_files_unchanged(self, before: dict, label: str) -> None:
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg=f"{label}: hubo escrituras en el árbol")


# ------------------------------------------------------- PD-6 / I8


class TestPd6SeparateRecordsAndIdempotency(DispatchCase):
    """PD-6 para 1 / I8: registros separados, idempotencia y sin sobrescritura."""

    def test_pd6_i8_two_roles_runtimes_separate_records_same_execution(self) -> None:
        """PD-6/I8: dos roles en runtimes distintos (paquete test-writer +
        paquete implementer) registran intentos separados bajo el mismo
        execution_id, con cada runtime/rol visibles en su registro."""
        eid, pid = self.bootstrap_ready()
        first_path = self.write_observation(
            "obs-two-roles.json", observation_doc(runtime="opencode"))
        proc = self.run_record(self.root, pid, "attempt-a", first_path)
        self.assertNotIn("unrecognized", self.out(proc),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc.returncode, 0,
                         msg=f"registro 1 falló: {self.out(proc)}")

        self.mark_completed()
        proc2 = self.run_prepare(self.root, role="implementer", substage="green")
        self.assertEqual(proc2.returncode, 0,
                         msg=f"precondición: paquete 2: {self.out(proc2)}")
        pid2 = read_state(self.root)["active_packet"]["id"]
        second_path = self.write_observation(
            "obs-two-runtimes.json", observation_doc(runtime="codex"))
        proc3 = self.run_record(self.root, pid2, "attempt-b", second_path)
        self.assertNotIn("unrecognized", self.out(proc3))
        self.assertEqual(proc3.returncode, 0,
                         msg=f"registro 2 falló: {self.out(proc3)}")

        bytes_a = self.read_dispatch(eid, "attempt-a")
        bytes_b = self.read_dispatch(eid, "attempt-b")
        self.assertIsNotNone(bytes_a, msg="falta el registro attempt-a")
        self.assertIsNotNone(bytes_b, msg="falta el registro attempt-b")
        self.assertNotEqual(
            bytes_a, bytes_b, msg="los registros quedaron idénticos")
        strings_a = iter_strings(json.loads(bytes_a.decode("utf-8")))
        strings_b = iter_strings(json.loads(bytes_b.decode("utf-8")))
        self.assertIn("test-writer", strings_a,
                      msg="attempt-a no referencia el rol de su paquete")
        self.assertIn("opencode", strings_a, msg="attempt-a perdió su runtime")
        self.assertIn("implementer", strings_b,
                      msg="attempt-b no referencia el rol de su paquete")
        self.assertIn("codex", strings_b, msg="attempt-b perdió su runtime")
        self.assertIn(eid, strings_a | strings_b,
                      msg="los registros viven bajo la misma ejecución")
        self.assertIn(pid, strings_a | strings_b,
                      msg="los registros no referencian sus paquetes")
        self.assertIn(pid2, strings_b | strings_a,
                      msg="el segundo registro no referencia su paquete")

    def test_pd6_i8_two_attempts_same_packet_separate_records(self) -> None:
        """PD-6/I8: dos intentos del MISMO paquete con datos de observación
        distintos quedan como registros separados bajo una ejecución."""
        eid, pid = self.bootstrap_ready()
        path1 = self.write_observation(
            "obs-att-1.json", observation_doc(session="ses-uno"))
        path2 = self.write_observation(
            "obs-att-2.json", observation_doc(session="ses-dos"))
        proc1 = self.run_record(self.root, pid, "attempt-1", path1)
        self.assertNotIn("unrecognized", self.out(proc1),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc1.returncode, 0,
                         msg=f"registro 1 falló: {self.out(proc1)}")
        proc2 = self.run_record(self.root, pid, "attempt-2", path2)
        self.assertEqual(proc2.returncode, 0,
                         msg=f"registro 2 falló: {self.out(proc2)}")
        bytes1 = self.read_dispatch(eid, "attempt-1")
        bytes2 = self.read_dispatch(eid, "attempt-2")
        self.assertIsNotNone(bytes1, msg="falta attempt-1")
        self.assertIsNotNone(bytes2, msg="falta attempt-2")
        self.assertNotEqual(
            bytes1, bytes2,
            msg="los dos intentos del mismo paquete se sobrescribieron")

    def test_pd6_i8_identical_record_idempotent(self) -> None:
        """PD-6/I8: repetir un registro idéntico es idempotente: rc=0 en
        ambas llamadas y bytes iguales del registro."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-idem.json", observation_doc())
        proc1 = self.run_record(self.root, pid, "attempt-idem", doc)
        self.assertNotIn("unrecognized", self.out(proc1),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc1.returncode, 0,
                         msg=f"registro 1 falló: {self.out(proc1)}")
        bytes1 = self.read_dispatch(eid, "attempt-idem")
        self.assertIsNotNone(bytes1, msg="falta el registro del intento")
        proc2 = self.run_record(self.root, pid, "attempt-idem", doc)
        self.assertEqual(proc2.returncode, 0,
                         msg=f"el registro idéntico no fue idempotente: "
                             f"rc={proc2.returncode}: {self.out(proc2)}")
        self.assertEqual(
            self.read_dispatch(eid, "attempt-idem"), bytes1,
            msg="el registro idéntico cambió los bytes guardados")

    def test_pd6_i8_reused_attempt_id_with_conflicting_data_rejected(self) -> None:
        """PD-6/I8: reutilizar el attempt-id con datos contradictorios da
        rc≠0 sin sobrescribir el registro existente ni el árbol."""
        eid, pid = self.bootstrap_ready()
        doc1 = self.write_observation(
            "obs-conf-1.json", observation_doc(session="ses-original"))
        doc2 = self.write_observation(
            "obs-conf-2.json",
            observation_doc(runtime="codex", session="ses-otro"))
        proc1 = self.run_record(self.root, pid, "attempt-shared", doc1)
        self.assertNotIn("unrecognized", self.out(proc1),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc1.returncode, 0,
                         msg=f"registro inicial falló: {self.out(proc1)}")
        saved = self.read_dispatch(eid, "attempt-shared")
        self.assertIsNotNone(saved, msg="falta el registro inicial")
        before = tree_snapshot(self.root)

        proc2 = self.run_record(self.root, pid, "attempt-shared", doc2)
        self.assertNotEqual(
            proc2.returncode, 0,
            msg="reutilizar el attempt-id con datos contradictorios fue "
                "aceptado")
        self.assertEqual(
            self.read_dispatch(eid, "attempt-shared"), saved,
            msg="el registro contradictorio sobrescribió el intento")
        self.assert_files_unchanged(before, "registro contradictorio")


class TestPd6ObservationDocument(DispatchCase):
    """PD-6 para 1 / I8: documento de claves cerradas y unknown como null."""

    def test_pd6_i8_all_fields_null_accepted(self) -> None:
        """PD-6/I8: unknown explícito — cada campo en null acepta el registro
        (rc=0) y el intento queda guardado."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-null.json",
            observation_doc(runtime=None, model_configured=None,
                            model_reported=None, session=None,
                            started_at=None, provenance={}))
        proc = self.run_record(self.root, pid, "attempt-null", doc)
        self.assertNotIn("unrecognized", self.out(proc),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el documento con unknown null fue rechazado: "
                f"{self.out(proc)}")

    def test_pd6_i8_multi_runtime_not_an_observed_runtime(self) -> None:
        """PD-6/I8: `multi-runtime` no representa un runtime observado →
        rechazado sin registro ni escrituras."""
        eid, pid = self.bootstrap_ready()
        path = self.write_observation(
            "obs-multi.json", observation_doc(runtime="multi-runtime"))
        before = tree_snapshot(self.root)
        proc = self.run_record(self.root, pid, "attempt-multi", path)
        out = self.out(proc)
        self.assertNotIn("unrecognized", out,
                         msg="--record-dispatch no existe aún")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="`multi-runtime` fue aceptado como runtime")
        self.assert_files_unchanged(before, "multi-runtime")

    def test_pd6_i8_extra_keys_rejected_no_reception(self) -> None:
        """PD-6/I8: claves extra del documento (result, deliverable, gate,
        status) → rechazadas sin registro (el registro no recibe
        resultados ni decisiones de gates)."""
        eid, pid = self.bootstrap_ready()
        extraneous = {
            "result": {"green": True},
            "deliverable": "src/whatever.py",
            "gate": {"status": "approved"},
            "status": "completed",
        }
        for key, value in extraneous.items():
            with self.subTest(clave_extra=key):
                attempt = f"attempt-extra-{key}"
                path = self.write_observation(
                    f"obs-extra-{key}.json",
                    observation_doc(**{key: value}))
                before = tree_snapshot(self.root)
                proc = self.run_record(self.root, pid, attempt, path)
                out = self.out(proc)
                self.assertNotIn(
                    "unrecognized", out,
                    msg="--record-dispatch no existe aún")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"la clave extra {key!r} fue aceptada")
                self.assert_no_traceback(proc, f"clave extra {key!r}")
                self.assertIsNone(
                    self.read_dispatch(eid, attempt),
                    msg=f"la clave extra {key!r} dejó un registro")
                self.assert_files_unchanged(before, f"clave extra {key}")


class TestPd6IdentityFromPacket(DispatchCase):
    """PD-6 para 1 / I8: execution_id/packet_id/role/substage salen del
    paquete, nunca del documento."""

    def test_pd6_i8_record_identity_matches_packet(self) -> None:
        """PD-6/I8: el intento guardado referencia el execution_id, packet_id,
        rol y subfase del paquete (no del documento)."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-identity.json", observation_doc())
        proc = self.run_record(self.root, pid, "attempt-identity", doc)
        self.assertNotIn("unrecognized", self.out(proc),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc.returncode, 0,
                         msg=f"registro falló: {self.out(proc)}")
        data = self.read_dispatch(eid, "attempt-identity")
        self.assertIsNotNone(data, msg="no hay registro del intento")
        strings = iter_strings(json.loads(data.decode("utf-8")))
        self.assertIn(eid, strings,
                      msg="el registro no referencia la ejecución del paquete")
        self.assertIn(pid, strings,
                      msg="el registro no referencia el paquete activo")
        self.assertIn("test-writer", strings,
                      msg="el registro no lleva el rol del paquete")
        self.assertIn("red", strings,
                      msg="el registro no lleva la subfase del paquete")

    def test_pd6_i8_document_cannot_inject_identity_fields(self) -> None:
        """PD-6/I8: un documento que intente fijar execution_id, packet_id,
        role o substage se rechaza (claves cerradas)."""
        eid, pid = self.bootstrap_ready()
        for key, forged in (
            ("execution_id", "exec-forged"),
            ("packet_id", "packet-forged"),
            ("role", "implementer"),
            ("substage", "green"),
        ):
            with self.subTest(clave=key):
                attempt = f"attempt-forge-{key}"
                doc = self.write_observation(
                    f"obs-forge-{key}.json",
                    observation_doc(**{key: forged}))
                before = tree_snapshot(self.root)
                proc = self.run_record(self.root, pid, attempt, doc)
                out = self.out(proc)
                self.assertNotIn(
                    "unrecognized", out,
                    msg="--record-dispatch no existe aún")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"el documento fijó {key}={forged!r} en el registro")
                self.assertIsNone(
                    self.read_dispatch(eid, attempt),
                    msg=f"el intento huérfano con {key} falsificado existe")
                self.assert_files_unchanged(
                    before, f"inserción de {key} en el documento")


class TestPd6PacketAndAttemptIds(DispatchCase):
    """PD-6 para 1 / I8: attempt-id nombre plano; packet-id inexistente o de
    otra ejecución."""

    def test_pd6_i8_attempt_id_must_be_plain_name(self) -> None:
        """PD-6/I8: attempt-id con ../ o / es rechazado sin ningún registro
        fuera del directorio de dispatches."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-escape.json", observation_doc())
        before = tree_snapshot(self.root)
        for bad in BAD_ATTEMPT_IDS:
            with self.subTest(attempt_id=bad):
                proc = self.run_record(self.root, pid, bad, doc)
                out = self.out(proc)
                self.assertNotIn(
                    "unrecognized", out,
                    msg="--record-dispatch no existe aún")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"el attempt-id {bad!r} fue aceptado")
                self.assert_no_traceback(proc, f"attempt-id {bad!r}")
                self.assert_files_unchanged(
                    before,
                    f"el attempt-id {bad!r} escribió fuera de dispatches")

    def test_pd6_i8_unknown_packet_id_rejected(self) -> None:
        """PD-6/I8: packet-id inexistente → rechazado sin escrituras ni
        registro."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-unknown.json", observation_doc())
        before = tree_snapshot(self.root)
        proc = self.run_record(self.root, "packet-que-no-existe",
                               "attempt-unknown", doc)
        out = self.out(proc)
        self.assertNotIn("unrecognized", out,
                         msg="--record-dispatch no existe aún")
        self.assertNotEqual(
            proc.returncode, 0, msg="un packet-id inexistente fue aceptado")
        self.assert_files_unchanged(before, "packet-id inexistente")

    def test_pd6_i8_packet_from_other_execution_rejected(self) -> None:
        """PD-6/I8: un packet-id que no pertenece a la ejecución activa se
        rechaza sin registro. Fixture v2 (transformación trazada en
        v1-fixture-trace.md; el fixture v1 explícito de la versión anterior
        desaparece con el camino I4 en el GREEN de T6): un primer paquete de
        la ejecución 1 queda `completed`; `--new-execution` crea la ejecución
        2 activa; el paquete 1 ya no pertenece a la ejecución activa."""
        proc1 = self.run_prepare(self.root)
        self.assertEqual(
            proc1.returncode, 0,
            msg=f"precondición (fixture): primer paquete (exec 1): "
                f"{self.out(proc1)}")
        foreign_packet_id = read_state(self.root)["active_packet"]["id"]
        foreign_execution_id = self.active_execution_id()
        # La ejecución 1 se cierra (paquete completed) y el dueño inicia la
        # ejecución 2 explícitamente (I3: existe contexto previo v2 → se exige
        # --new-execution; precondición firmada por T2/PD-4).
        self.mark_completed()
        proc2 = self.run_prepare(self.root, "--new-execution")
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"precondición (fixture): --new-execution debe crear la "
                f"ejecución 2 activa: {self.out(proc2)}")
        active_eid = self.active_execution_id()
        active_pid = read_state(self.root)["active_packet"]["id"]
        self.assertNotEqual(
            active_eid, foreign_execution_id,
            msg="precondición: la ejecución activa no es la del paquete ajeno")
        self.assertNotEqual(
            active_pid, foreign_packet_id,
            msg="precondición: el paquete activo no es el de la otra ejecución")

        doc = self.write_observation(
            "obs-foreign.json", observation_doc())
        before = tree_snapshot(self.root)
        proc = self.run_record(self.root, foreign_packet_id,
                               "attempt-foreign", doc)
        out = self.out(proc)
        self.assertNotIn("unrecognized", out,
                         msg="--record-dispatch no existe aún")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="un packet-id de otra ejecución fue aceptado")
        self.assertIsNone(
            self.read_dispatch(active_eid, "attempt-foreign"),
            msg="hubo registro contra el paquete ajeno")
        self.assertIsNone(
            self.read_dispatch(foreign_execution_id, "attempt-foreign"),
            msg="hubo registro contra la ejecución anterior")
        self.assert_files_unchanged(before, "packet-id de otra ejecución")


class TestPd6StateStatusAndFrontier(DispatchCase):
    """PD-6 para 1: transición prepared→dispatched (nunca completed/failed),
    frontera de recepción con 003-002 y bloqueo PD-5."""

    def test_pd6_i8_active_packet_prepared_to_dispatched_never_completed(
            self) -> None:
        """PD-6/I8: registrar el despacho pasa el paquete activo de prepared
        a dispatched y NUNCA a completed o failed."""
        eid, pid = self.bootstrap_ready()
        state = read_state(self.root)
        state["active_packet"]["status"] = "prepared"
        write_state(self.root, state)
        doc = self.write_observation(
            "obs-status.json", observation_doc())
        proc = self.run_record(self.root, pid, "attempt-status", doc)
        self.assertNotIn("unrecognized", self.out(proc),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc.returncode, 0,
                         msg=f"registro falló: {self.out(proc)}")
        status = read_state(self.root)["active_packet"]["status"]
        self.assertEqual(
            status, "dispatched",
            msg=f"el paquete activo quedó en {status!r} (se esperaba "
                f"dispatched)")
        self.assertNotEqual(
            status, "completed", msg="el registro marcó completed")
        self.assertNotEqual(status, "failed", msg="el registro marcó failed")

    def test_pd6_i8_record_reception_free_frontier_with_003_002(self) -> None:
        """PD-6/I8 (frontera con 003-002): registrar no escribe entregables
        ni toca stage_history, gates ni postconditions_status: comparando el
        state antes/después solo cambia el status del paquete, y el árbol
        solo gana archivos de dispatches de la ejecución activa."""
        eid, pid = self.bootstrap_ready()
        doc = self.write_observation(
            "obs-frontier.json", observation_doc())
        # tree_before DESPUÉS de escribir el fixture de observaciones: el
        # documento --input es entrada del test, no escritura del registro
        # (enmienda de oráculo firmada, review-t3.md §T4).
        state_before = read_state(self.root)
        tree_before = tree_snapshot(self.root)
        proc = self.run_record(self.root, pid, "attempt-frontier", doc)
        self.assertNotIn("unrecognized", self.out(proc),
                         msg="--record-dispatch no existe aún")
        self.assertEqual(proc.returncode, 0,
                         msg=f"registro falló: {self.out(proc)}")

        state_after = read_state(self.root)
        self.assertEqual(
            state_normalized(state_after), state_normalized(state_before),
            msg="el registro tocó campos del state distintos del status del "
                "paquete (frontera 003-002): stage_history/gates/"
                "postconditions_status o binding alterados")
        for key in STATE_KEYS_FRONTIER:
            self.assertEqual(
                state_after.get(key), state_before.get(key),
                msg=f"el registro alteró {key}")
        self.assertIn(
            "dispatched",
            json.dumps(state_after.get("active_packet", {})),
            msg="el paquete activo no quedó en dispatched")

        changed = sorted(
            rel for rel in set(tree_before) | set(tree_snapshot(self.root))
            if tree_before.get(rel) != tree_snapshot(self.root).get(rel))
        unexpected = [
            rel for rel in changed
            if not (rel.startswith(
                        f".cdad/executions/{eid}/dispatches/")
                    or rel == ".cdad/.lock"
                    # la transición prepared→dispatched la exige el propio
                    # test (state arriba, comparación normalizada); el state
                    # publicado cambia por ese mismo motivo.
                    or rel == "docs/.cdad-state.json")
        ]
        self.assertEqual(
            unexpected, [],
            msg=f"el registro escribió fuera de dispatches: {unexpected}")

    def test_pd6_i8_record_blocked_when_policy_changed_unreconciled(self) -> None:
        """PD-6×PD-5: con la política cambiada sin reconciliar, record-dispatch
        se bloquea (rc≠0, diagnóstico que nombra la reconciliación, sin
        escrituras ni registro)."""
        eid, pid = self.bootstrap_ready()
        (self.root / "docs" / "obs-blocked.json").write_text(
            json.dumps(observation_doc(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        (self.root / POLICY_FILE).write_bytes(
            (self.root / POLICY_FILE).read_bytes() + b" \n")
        before = tree_snapshot(self.root)
        proc = self.run_record(self.root, pid, "attempt-blocked",
                               self.root / "docs" / "obs-blocked.json")
        out = self.out(proc)
        self.assertNotIn("unrecognized", out,
                         msg="--record-dispatch no existe aún")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="el registro operó con una revisión de política no "
                "reconciliada (PD-5)")
        self.assertTrue(
            re.search(r"reconcil|reconciliaci", out, re.IGNORECASE),
            msg=f"el diagnóstico no nombra la reconciliación: {out!r}")
        self.assert_no_traceback(proc, "registro bloqueado por PD-5")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el registro bloqueado imprimió un paquete")
        self.assert_files_unchanged(before, "registro bloqueado PD-5")


if __name__ == "__main__":
    unittest.main(verbosity=2)
