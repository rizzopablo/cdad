#!/usr/bin/env python3
"""004-002 T3 review-fix RED — hallazgos F1–F6 de docs/specs/
004-002-project-execution-bootstrap/review-t3.md (disposición del orquestador)
+ interfaz I5b de docs/specs/004-002-project-execution-bootstrap/plan.md.

Superficie observable bajo prueba (proyectos sintéticos T2 en tempdirs;
ninguna escritura en este repo; NINGUNA lectura de implementación):

    python3 scripts/cdad_packet.py prepare --project-root <raíz> \
        --role <rol> --substage <subfase> --objective <encargo> [opciones]
    python3 scripts/cdad_packet.py validate-state --project-root <raíz>

Ganchos bajo prueba:
  - I5 (existente): CDAD_TEST_FAIL_AT=<punto> con puntos `reserved-id`,
    `context-written`, `packet-written`, `before-state`, `after-state`
    (código 97, sin paquete impreso).
  - I5b (nuevo, RED hoy): CDAD_TEST_PAUSE_AT=<punto> junto con
    CDAD_TEST_PAUSE_FILE=<ruta>: al llegar al punto el proceso crea
    `<ruta>.reached` y espera a que exista `<ruta>` (tope 30 s); inerte sin
    la variable. Con el remedio de F2, `reserved-id` queda después de tomar
    el lock y reservar.

Mapa test → postcondición (hallazgo):

  F1 lock_survives_success          PD-11 (remedio de F1: rendezvous
                                    permanente; solo se libera el flock)
  F2 pause_at_reserved_id_serializes PD-11/I5b + PD-4 (resolución y reserva
                                    dentro del lock; B rechazado con
                                    diagnóstico de ocupación y sin
                                    escrituras; A publica; nadie queda
                                    sobrescrito)
  F3 recovery_keeps_foreign_files_in_txn_dir PD-11 + invariante 7
  F4a reconcile_adopts_new_classification    PD-5 + PD-1/PD-7 (clasificación
                                    derivada de la revisión aceptada)
  F4b reconcile_invalid_policy_rejected      PD-5 + PD-1 (política inválida
                                    no se acepta por reconciliación)
  F5 validate_state_valid_immediately_after_reconcile PD-5 (binding
                                    coherente justo tras reconciliar)
  F6 packet_carries_verifiable_policy_snapshot PD-5 (snapshot en el paquete
                                    con digest que coincide con el hash
                                    declarado)

RED hoy (HEAD 860b60f): cada test debe fallar por AssertionError sobre el
comportamiento ausente (nunca por import/sintaxis/opciones inexistentes).
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (
    PACKET_BEGIN,
    POLICY_FILE,
    SCRIPT,
    build_project,
    prepare_args,
    published_packets,
    read_state,
    run_cli,
    run_validate_state,
    tree_snapshot,
    v2_execution_docs,
    write_state,
    STATE_FILE,
)

from test_004_002_t3_durable import (
    FAIL_AT_RC,
    FAIL_AT_VAR,
    snapshot_of_policy_recorded,
)

PAUSE_AT_VAR = "CDAD_TEST_PAUSE_AT"
PAUSE_FILE_VAR = "CDAD_TEST_PAUSE_FILE"
PAUSE_WAIT_SECONDS = 30


def policy_bytes(root: Path) -> bytes:
    return (root / POLICY_FILE).read_bytes()


def policy_sha(root: Path) -> str:
    return hashlib.sha256(policy_bytes(root)).hexdigest()


def state_bytes(root: Path) -> bytes:
    return (root / STATE_FILE).read_bytes()


def set_active_packet_status(root: Path, status: str) -> None:
    state = read_state(root)
    state["active_packet"]["status"] = status
    write_state(root, state)


def lock_path(root: Path) -> Path:
    return root / ".cdad" / ".lock"


def txn_root(root: Path) -> Path:
    return root / ".cdad" / ".txn"


def active_packet_bytes(root: Path) -> bytes:
    packet_id = read_state(root)["active_packet"]["id"]
    return published_packets(root)[packet_id]


def packet_json_doc(packet_text: str) -> dict:
    """El bloque JSON canónico del PACKET.md publicado."""
    start = packet_text.index("---cdad-packet-json\n") + len(
        "---cdad-packet-json\n")
    end = packet_text.index("---end-cdad-packet-json")
    return json.loads(packet_text[start:end])


class ReviewFixProjectCase(unittest.TestCase):
    """Base: proyecto sintético T2 en tempdir propio; corridas CLI."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t3-rf-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = self.new_project()

    def new_project(self) -> Path:
        tmp = tempfile.mkdtemp(prefix="cdad-t3-rf-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        root = Path(tmp) / "proj"
        build_project(root)
        return root

    def run_prepare(self, root: Path, *extra: str, role: str = "test-writer",
                    substage: str = "red", objective: str = "encargo T3 RF",
                    env_extra: dict | None = None,
                    timeout: float = 120) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(root, role=role, substage=substage,
                           objective=objective, extra=extra)],
            capture_output=True, text=True, cwd=SCRIPT.parents[1],
            env=env, timeout=timeout)

    def prepare_ok(self, root: Path, *extra: str, label: str,
                   **kwargs) -> subprocess.CompletedProcess:
        proc = self.run_prepare(root, *extra, **kwargs)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición {label}: {proc.stdout} {proc.stderr}")
        return proc


# ---------------------------------------------------------------- F1


class TestF1LockRendezvousIsPermanent(ReviewFixProjectCase):
    def test_f1_lock_file_survives_successful_prepare(self) -> None:
        """F1 (PD-11): tras un prepare exitoso `.cdad/.lock` SIGUE existiendo:
        el archivo de rendezvous es permanente y solo se libera el flock."""
        self.prepare_ok(self.root, label="bootstrap")
        self.assertTrue(
            lock_path(self.root).is_file(),
            msg="un prepare exitoso eliminó .cdad/.lock (el rendezvous debe "
                "ser permanente; solo se libera el flock)")
        # No es un caso especial del bootstrap: un prepare posterior tampoco
        # elimina el archivo ya existente.
        state = read_state(self.root)
        state["active_packet"]["status"] = "completed"
        write_state(self.root, state)
        self.prepare_ok(self.root, role="implementer", substage="green",
                        label="segundo prepare")
        self.assertTrue(
            lock_path(self.root).is_file(),
            msg="el segundo prepare eliminó .cdad/.lock preexistente")


# ---------------------------------------------------------------- F2


class TestF2PauseAtReservedId(ReviewFixProjectCase):
    """F2 (PD-11 + PD-4, I5b): con el gancho de pausa, A se detiene después
    de tomar el lock y reservar; mientras A está pausado, B es rechazado con
    diagnóstico de ocupación y sin escrituras; al soltar A, A publica y
    ningún paquete queda sobrescrito."""

    def test_f2_pause_at_reserved_id_blocks_b_and_a_publishes(self) -> None:
        root = self.root
        pause_file = Path(self._tmp) / "pause-rf.flag"
        reached_file = Path(str(pause_file) + ".reached")
        env_a = dict(os.environ)
        env_a[PAUSE_AT_VAR] = "reserved-id"
        env_a[PAUSE_FILE_VAR] = str(pause_file)
        proc_a = subprocess.Popen(
            [sys.executable, str(SCRIPT),
             *prepare_args(root, objective="encargo pausado A")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=SCRIPT.parents[1], env=env_a)
        self.addCleanup(self._drain_and_wait, proc_a)
        deadline = time.monotonic() + PAUSE_WAIT_SECONDS
        while (time.monotonic() < deadline and proc_a.poll() is None
               and not reached_file.exists()):
            time.sleep(0.05)

        if proc_a.poll() is not None:
            out, err = proc_a.communicate()
            self.fail(
                "I5b ausente/RED: el gancho CDAD_TEST_PAUSE_AT no pausó al "
                f"proceso A en reserved-id (A terminó rc={proc_a.returncode}; "
                f"¿terminó sin gancho? stdout: {out[:200]!r} stderr: "
                f"{err[:200]!r})")
        if not reached_file.exists():
            out, err = self._drain_and_wait(proc_a)
            self.fail(
                "I5b ausente/RED: el gancho no creó <ruta>.reached al llegar "
                f"al punto reserved-id; no hay pausa observable (stdout: "
                f"{out[:200]!r} stderr: {err[:200]!r})")

        # A está pausado DESPUÉS de tomar el lock y reservar: nadie más puede
        # publicar.
        self.assertTrue(
            lock_path(root).is_file(),
            msg="A pausado en reserved-id no dejó el rendezvous .cdad/.lock")

        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc_b = self.run_prepare(root, objective="concurrente B", timeout=30)
        out_b = proc_b.stdout + proc_b.stderr
        self.assertNotEqual(
            proc_b.returncode, 0,
            msg="B procedió pese a que A ocupa el lock (pausado después de "
                "tomar el lock y reservar)")
        self.assertFalse(
            proc_b.stdout.startswith(PACKET_BEGIN),
            msg="B bloqueado imprimió un paquete")
        self.assertTrue(
            re.search(r"bloqueo|lock|ocupad|en uso|busy", out_b, re.IGNORECASE),
            msg=f"el diagnóstico de B no informa la ocupación: {out_b!r}")
        self.assertEqual(
            tree_snapshot(root), before,
            msg="B bloqueado escribió el árbol (¿sobrescribió la reserva de A?)")
        self.assertEqual(
            state_bytes(root), state_before,
            msg="B bloqueado cambió el state")

        # Soltar A: publica su paquete.
        pause_file.touch(exist_ok=True)
        out_a, err_a = self._drain_and_wait(proc_a)
        self.assertEqual(
            proc_a.returncode, 0,
            msg=f"al soltar la pausa, A debe publicar: {out_a} {err_a}")
        self.assertTrue(
            out_a.startswith(PACKET_BEGIN),
            msg="A publicó sin imprimir el paquete canónico")
        packet_id = read_state(root)["active_packet"]["id"]
        packets = published_packets(root)
        self.assertIn(
            packet_id, packets,
            msg=f"el paquete activo {packet_id!r} no está publicado tras A")
        self.assertEqual(
            packets[packet_id].decode("utf-8"), out_a,
            msg="los bytes publicados difieren del stdout de A: el paquete "
                "quedó sobrescrito por otra publicación")

    @staticmethod
    def _drain_and_wait(proc: subprocess.Popen) -> tuple[str, str]:
        out, err = proc.communicate(timeout=60)
        return out, err


# ---------------------------------------------------------------- F3


class TestF3RecoveryKeepsForeignFiles(ReviewFixProjectCase):
    def test_f3_recovery_keeps_foreign_file_inside_existing_txn_dir(self) -> None:
        """F3 (PD-11 + invariante 7): interrumpir en `context-written`, meter
        un archivo ajeno dentro del directorio de transacción YA EXISTENTE,
        interrumpir otra vez y recuperar: el archivo ajeno sobrevive (la
        limpieza debe ser solo de los archivos propios de la transacción)."""
        root = self.root
        env_fail = dict(os.environ)
        env_fail[FAIL_AT_VAR] = "context-written"
        first = self.run_prepare(root, objective="primer intento",
                                 env_extra=env_fail)
        self.assertEqual(
            first.returncode, FAIL_AT_RC,
            msg=f"precondición: la interrupción 1 debe activarse: "
                f"{first.stdout} {first.stderr}")

        txn_dirs = [p for p in sorted(txn_root(root).iterdir())
                    if p.is_dir()] if txn_root(root).is_dir() else []
        self.assertTrue(
            txn_dirs,
            msg="precondición: la interrupción en context-written debe dejar "
                "un directorio de transacción en .cdad/.txn/")
        stage_dir = txn_dirs[0]
        foreign = stage_dir / "foreign.txt"
        foreign_payload = b"archivo ajeno del usuario; la recuperacion no lo toca\n"
        foreign.write_bytes(foreign_payload)

        second = self.run_prepare(root, objective="interrupcion repetida",
                                  env_extra=env_fail)
        self.assertEqual(
            second.returncode, FAIL_AT_RC,
            msg=f"precondición: la interrupción 2 debe activarse: "
                f"{second.stdout} {second.stderr}")

        recovery = self.run_prepare(root, objective="recuperacion normal")
        self.assertEqual(
            recovery.returncode, 0,
            msg=f"la recuperación normal debe terminar rc 0: "
                f"{recovery.stdout} {recovery.stderr}")
        self.assertTrue(
            foreign.is_file(),
            msg="la recuperación borró el archivo ajeno dentro del directorio "
                "de transacción existente (F3): debe limpiar solo los "
                "archivos propios de la transacción")
        self.assertEqual(
            foreign.read_bytes(), foreign_payload,
            msg="la recuperación modificó los bytes del archivo ajeno")


# ---------------------------------------------------------------- F4 / F5 / F6


class ReconcileScenarioCase(ReviewFixProjectCase):
    """Escenario común F4/F5/F6: bootstrap + paquete completado + revisión de
    política materializada con decisión del dueño."""

    def bootstrap_completed(self) -> str:
        self.prepare_ok(self.root, label="bootstrap")
        set_active_packet_status(self.root, "completed")

    def materialize_revision(self) -> tuple[str, str]:
        """Devuelve (sha, decision_ref) de los bytes ACTUALES de la política."""
        sha = policy_sha(self.root)
        decision_ref = "docs/decision-policy-revision-rf.md"
        (self.root / decision_ref).write_text(
            f"# Decisión del dueño\nsha256: {sha}\n", encoding="utf-8")
        return sha, decision_ref

    def run_reconcile(self, sha: str, decision_ref: str) -> subprocess.CompletedProcess:
        # A-2 (review-t3): argv PURO del modo reconciliación — sin las
        # opciones ordinarias --role/--substage/--objective de
        # run_prepare/prepare_args, que disparan el rechazo de modos
        # excluyentes (I5d) y no la reconciliación bajo prueba.
        args = ["prepare", "--project-root", str(self.root),
                "--reconcile-policy", sha, "--decision-ref", decision_ref]
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=SCRIPT.parents[1],
            env=dict(os.environ), timeout=120)

    def active_execution_doc(self) -> dict:
        docs = v2_execution_docs(self.root)
        self.assertTrue(docs, msg="no hay contexto v2 para examinar")
        eid = read_state(self.root)["execution"]["id"]
        return docs[eid]


class TestF4ReconcileClassification(ReconcileScenarioCase):
    def test_f4a_reconcile_adopts_new_implementation_roots(self) -> None:
        """F4 (PD-5 + PD-1/PD-7): reconciliar tras cambiar
        implementation_roots (["src","lib"] → ["app"]) hace que el contexto y
        los paquetes posteriores usen la clasificación nueva."""
        self.bootstrap_completed()
        policy = json.loads(policy_bytes(self.root).decode("utf-8"))
        policy["path_policy"]["implementation_roots"] = ["app"]
        new_bytes = (json.dumps(policy, indent=2, sort_keys=True)
                     + "\n").encode("utf-8")
        (self.root / POLICY_FILE).write_bytes(new_bytes)
        sha, decision_ref = self.materialize_revision()

        proc = self.run_reconcile(sha, decision_ref)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out, msg="las opciones de reconciliación no existen")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"la reconciliación debe aceptarse: {out!r}")

        doc = self.active_execution_doc()
        self.assertIn(
            sha, json.dumps(doc),
            msg="el contexto no registra la revisión reconciliada")
        self.assertEqual(
            (doc.get("path_policy") or {}).get("implementation_roots"),
            ["app"],
            msg="el contexto conservó la clasificación anterior tras "
                f"reconciliar: {(doc.get('path_policy') or {}).get('implementation_roots')!r} (F4)")

        next_proc = self.prepare_ok(self.root, role="implementer",
                                    substage="green", label="paquete posterior")
        packet_text = active_packet_bytes(self.root).decode("utf-8")
        self.assertIn(
            sha, packet_text,
            msg="el paquete posterior no registra la revisión reconciliada")
        roots_matches = re.findall(
            r'"implementation_roots":\[[^\]]*\]', packet_text)
        self.assertTrue(
            roots_matches,
            msg="el paquete posterior no expone la clasificación")
        self.assertIn(
            '"implementation_roots":["app"]', packet_text,
            msg=f"el paquete posterior conserva la clasificación anterior: "
                f"{roots_matches}")
        self.assertNotIn(
            '"implementation_roots":["src","lib"]', packet_text,
            msg="el paquete posterior sigue publicando la clasificación "
                "anterior (F4)")

    def test_f4b_reconcile_with_invalid_policy_is_rejected(self) -> None:
        """F4 (PD-5 + PD-1): reconciliar contra una política inválida ({})
        debe fallar: no se valida el contexto anterior sino los bytes
        aceptados."""
        self.bootstrap_completed()
        (self.root / POLICY_FILE).write_text("{}\n", encoding="utf-8")
        sha, decision_ref = self.materialize_revision()
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)

        proc = self.run_reconcile(sha, decision_ref)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="la reconciliación aceptó una política inválida ({})")
        self.assertNotIn("Traceback", proc.stderr, msg="fallo con traceback")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la reconciliación rechazada escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la reconciliación rechazada cambió el state")
        self.assertTrue(
            re.search(r"pol[íi]tica|policy|inv[áa]lid", out, re.IGNORECASE),
            msg=f"el diagnóstico no nombra la política inválida: {out!r}")


class TestF5BindingValidAfterReconcile(ReconcileScenarioCase):
    def test_f5_validate_state_is_valid_immediately_after_reconcile(self) -> None:
        """F5 (PD-5): inmediatamente después de reconciliar, validate-state
        da VALID (binding coherente; contexto y state.execution publicados
        juntos)."""
        self.bootstrap_completed()
        (self.root / POLICY_FILE).write_bytes(
            policy_bytes(self.root) + b"\n")
        sha, decision_ref = self.materialize_revision()
        proc = self.run_reconcile(sha, decision_ref)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out, msg="las opciones de reconciliación no existen")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: la reconciliación debe aceptarse: {out!r}")
        validated = run_validate_state(self.root)
        self.assertEqual(
            validated.returncode, 0,
            msg=f"inmediatamente tras reconciliar, validate-state debe dar "
                f"VALID (binding coherente): {validated.stdout} "
                f"{validated.stderr}")


class TestF6PacketPolicySnapshot(ReviewFixProjectCase):
    def test_f6_published_packet_carries_verifiable_policy_snapshot(self) -> None:
        """F6 (PD-5): el PACKET.md publicado contiene el snapshot verificable
        de la política (sus bytes exactos, literal o base64) y su digest
        coincide con el hash declarado en el paquete."""
        self.prepare_ok(self.root, label="bootstrap")
        packet_text = active_packet_bytes(self.root).decode("utf-8")
        raw = policy_bytes(self.root)
        declared = packet_json_doc(packet_text)["execution"]["policy_sha256"]

        self.assertIn(
            declared, packet_text,
            msg="el paquete no registra el hash de la política vigente")
        literal = raw.decode("utf-8")
        encoded = base64.b64encode(raw).decode("ascii")
        if literal in packet_text:
            snapshot_bytes = raw
        elif encoded in packet_text:
            snapshot_bytes = base64.b64decode(encoded, validate=True)
        else:
            self.fail(
                "el paquete publicado no contiene el snapshot de los bytes "
                "de la política (literal o base64); solo lleva el hash (F6)")
        self.assertEqual(
            hashlib.sha256(snapshot_bytes).hexdigest(), declared,
            msg="el digest del snapshot no coincide con el hash declarado")


if __name__ == "__main__":
    unittest.main(verbosity=2)
