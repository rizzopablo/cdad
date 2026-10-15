#!/usr/bin/env python3
"""004-002 T3 RED — Snapshot, reconciliación, exclusión y recuperación (PD-5, PD-11).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md (PD-5, PD-11)
+ plan.md (decisiones de interfaz I5, I6 del orquestador).

Superficie observable bajo prueba (los proyectos son fixtures sintéticos
tempdirs; ninguna escritura en este repo):

    python3 scripts/cdad_packet.py prepare --project-root <raíz> \
        --role <rol> --substage <subfase> --objective <encargo> [opciones]
    python3 scripts/cdad_packet.py validate-state --project-root <raíz>

NUEVO bajo T3:
  - I5: gancho inerte `CDAD_TEST_FAIL_AT=<punto>` con puntos
    `reserved-id`, `context-written`, `packet-written`, `before-state`,
    `after-state` (termina con código 97, sin limpieza ni paquete impreso);
    `fcntl.flock` sobre `.cdad/.lock` como escritor único; lock no huérfano.
  - I6: `prepare --reconcile-policy <sha256> --decision-ref <ruta>`.

Fixtures: mismos proyectos sintéticos que T2.GREEN (política válida de tres
campos, state con registros de autoridad I2, spec aprobada, source de
autoridad existente).

RED hoy (contra el GREEN de T2): sin snapshot/reconciliación ni gancho ni
lock; cada aserción expresa el comportamiento de la postcondición.
"""

from __future__ import annotations

import base64
import fcntl  # noqa: F401  (referencia a la interfaz I5 declarada)
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
    REPO_ROOT,
    SCRIPT,
    STATE_FILE,
    build_project,
    prepare_args,
    published_packets,
    read_state,
    run_validate_state,
    tree_snapshot,
    v2_execution_docs,
    write_state,
)

FAIL_AT_VAR = "CDAD_TEST_FAIL_AT"
FAIL_AT_POINTS = (
    "reserved-id",
    "context-written",
    "packet-written",
    "before-state",
    "after-state",
)
FAIL_AT_RC = 97
FOREIGN_FILE = ".cdad/ajeno.txt"


# ---------------------------------------------------------------- helpers


def curr_policy_bytes(root: Path) -> bytes:
    return (root / POLICY_FILE).read_bytes()


def curr_policy_sha(root: Path) -> str:
    return hashlib.sha256(curr_policy_bytes(root)).hexdigest()


def policy_texts(root: Path) -> tuple[str, bytes]:
    data = curr_policy_bytes(root)
    return data.decode("utf-8"), data


def state_bytes(root: Path) -> bytes:
    return (root / STATE_FILE).read_bytes()


def set_active_packet_status(root: Path, status: str) -> None:
    state = read_state(root)
    assert state.get("active_packet"), (
        "fixture: el prepare previo no dejó paquete activo en state")
    state["active_packet"]["status"] = status
    write_state(root, state)


def iter_strings(obj) -> "set[str]":
    found: set[str] = set()

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


def snapshot_of_policy_recorded(doc, policy_text: str, policy_bytes: bytes) -> bool:
    """PD-5: existe en el documento un snapshot verificable del contenido de
    la política (texto literal o base64 cuyo origen son los bytes exactos)."""
    for s in iter_strings(doc):
        if s == policy_text:
            return True
        try:
            if base64.b64decode(s, validate=True) == policy_bytes:
                return True
        except Exception:
            continue
    return False


def history_text(root: Path) -> str:
    """Dónde puede quedar el historial observable: contextos v2 + state."""
    parts: list[str] = []
    for doc in v2_execution_docs(root).values():
        parts.append(json.dumps(doc, ensure_ascii=False))
    parts.append(state_bytes(root).decode("utf-8", errors="replace"))
    return "\n".join(parts)


HOLDER_SOURCE = r"""
import fcntl, os, sys, time
lock_path, ready_path, release_path = sys.argv[1:4]
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
with open(ready_path, "w") as f:
    f.write("ready")
deadline = time.time() + 120
while not os.path.exists(release_path) and time.time() < deadline:
    time.sleep(0.05)
os.close(fd)
"""


class DurableProjectCase(unittest.TestCase):
    """Base: proyectos sintéticos T2 en tempdirs propios."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t3-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = self.new_project()

    def new_project(self, **state_kwargs) -> Path:
        tmp = tempfile.mkdtemp(prefix="cdad-t3-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        root = Path(tmp) / "proj"
        build_project(root, **state_kwargs)
        return root

    # -- corridas CLI -----------------------------------------------------

    def run_cli_env(self, args: list[str], *, env_extra: dict | None = None,
                    timeout: float = 120) -> tuple[subprocess.CompletedProcess, float]:
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        start = time.monotonic()
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True, cwd=REPO_ROOT,
            env=env, timeout=timeout)
        return proc, time.monotonic() - start

    def run_prepare(self, root: Path, *extra: str, role: str = "test-writer",
                    substage: str = "red", objective: str = "encargo T3",
                    env_extra: dict | None = None,
                    timeout: float = 120) -> tuple[subprocess.CompletedProcess, float]:
        args = prepare_args(root, role=role, substage=substage,
                            objective=objective, extra=extra)
        return self.run_cli_env(args, env_extra=env_extra, timeout=timeout)

    def run_resume(self, root: Path, packet_id: str) -> tuple[subprocess.CompletedProcess, float]:
        args = ["prepare", "--project-root", str(root),
                "--resume-packet", packet_id]
        return self.run_cli_env(args)

    def run_reconcile(self, root: Path, sha: str, decision_ref: str,
                      *extra: str) -> tuple[subprocess.CompletedProcess, float]:
        # A-2 (review-t3): reconciliar admite SOLO --decision-ref; argv
        # PURO del modo reconciliación — sin las opciones ordinarias
        # --role/--substage/--objective del helper prepare_args, que
        # disparan el rechazo de modos excluyentes (I5d) y no la
        # reconciliación bajo prueba.
        args = ["prepare", "--project-root", str(root),
                "--reconcile-policy", sha, "--decision-ref", decision_ref,
                *extra]
        return self.run_cli_env(args)

    def run_record_dispatch(self, root: Path, packet_id: str, attempt_id: str,
                            input_path: Path) -> tuple[subprocess.CompletedProcess, float]:
        # O1 (review-t3.md): argv PURO del modo registro I8 — sin las
        # opciones ordinarias --role/--substage/--objective del helper
        # prepare_args, que disparan el rechazo de modos excluyentes y no el
        # bloqueo de reconciliación bajo prueba.
        args = ["prepare", "--project-root", str(root),
                "--record-dispatch", packet_id,
                "--attempt-id", attempt_id,
                "--input", str(input_path)]
        return self.run_cli_env(args)

    # -- fixtures ---------------------------------------------------------

    def prepare_bootstrap(self, root: Path) -> subprocess.CompletedProcess:
        proc, _ = self.run_prepare(root)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: bootstrap de T2 debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        return proc

    def add_foreign_artifacts(self, root: Path) -> dict[str, bytes]:
        """PD-11: archivos ajenos dentro de .cdad que deben sobrevivir."""
        cdad = root / ".cdad"
        cdad.mkdir(exist_ok=True)
        (cdad / "keep").mkdir(exist_ok=True)
        foreign = {
            FOREIGN_FILE: b"recurso ajeno que prepare no debe borrar\n",
            ".cdad/keep/aux.bin": bytes(range(256)),
        }
        for rel, data in foreign.items():
            (root / rel).write_bytes(data)
        return foreign

    def assert_foreign_survives(self, foreign: dict[str, bytes]) -> None:
        for rel, data in foreign.items():
            path = self.root / rel
            self.assertTrue(
                path.is_file(),
                msg=f"PD-11/la recuperación borró el archivo ajeno {rel}")
            self.assertEqual(
                path.read_bytes(), data,
                msg=f"PD-11/la recuperación modificó el archivo ajeno {rel}")

    def assert_coherent_generation(self, recovery: subprocess.CompletedProcess) -> None:
        """PD-11: generación coherente tras la invocación de recuperación:
        binding resoluble, contexto v2 referenciado y (si hubo salida)
        stdout == bytes del paquete publicado."""
        root = self.root
        validated = run_validate_state(root)
        self.assertEqual(
            validated.returncode, 0,
            msg=f"tras la recuperación el binding no resuelve: "
                f"{validated.stdout} {validated.stderr}")
        state = read_state(root)
        self.assertTrue(state.get("execution"),
                        msg="state.execution sigue vacío tras la recuperación")
        execution_id = state["execution"].get("id")
        docs = v2_execution_docs(root)
        self.assertIn(
            execution_id, docs,
            msg=f"state.execution referencia {execution_id!r} sin contexto v2")
        packets = published_packets(root)
        self.assertTrue(
            packets, msg="no hay ningún paquete publicado tras la recuperación")
        if recovery.returncode == 0:
            self.assertTrue(
                recovery.stdout.startswith(PACKET_BEGIN),
                msg="recuperación ok no imprimió el paquete canónico")
            active_id = state.get("active_packet", {}).get("id")
            self.assertIn(
                active_id, packets,
                msg=f"el paquete activo {active_id!r} no está publicado")
            self.assertEqual(
                packets[active_id].decode("utf-8"), recovery.stdout,
                msg="stdout difiere de los bytes del paquete publicado")


# ---------------------------------------------------------------- PD-5


class TestPd5SnapshotAndReconciliation(DurableProjectCase):
    """PD-5 / I6: snapshot/hash de política, bloqueo y reconciliación."""

    def test_pd5_context_and_packet_record_policy_hash_with_verifiable_snapshot(self) -> None:
        """PD-5: la ejecución v2 y el paquete registran el hash (y un snapshot
        verificable) de docs/cdad-policy.json vigente al prepararlos."""
        proc = self.prepare_bootstrap(self.root)
        docs = v2_execution_docs(self.root)
        self.assertEqual(len(docs), 1, msg=f"contextos v2: {sorted(docs)}")
        _, doc = next(iter(docs.items()))
        sha = curr_policy_sha(self.root)
        packet_id = read_state(self.root)["active_packet"]["id"]
        packet_bytes = published_packets(self.root)[packet_id]

        self.assertIn(
            sha, json.dumps(doc),
            msg="el contexto v2 no registra el hash de la política vigente")
        self.assertIn(
            sha, packet_bytes.decode("utf-8"),
            msg="el paquete no registra el hash de la política vigente")
        policy_text, policy_bytes = policy_texts(self.root)
        self.assertTrue(
            snapshot_of_policy_recorded(doc, policy_text, policy_bytes),
            msg="el contexto no contiene un snapshot verificable de la política "
                "(contenido literal o base64)")

    def test_pd5_policy_bytes_change_blocks_prepare_resume_and_dispatch(self) -> None:
        """PD-5: cambiados los bytes de la política, un prepare nuevo,
        --resume-packet y el registro de despacho fallan (rc≠0) con
        diagnóstico que nombra la reconciliación y sin ninguna escritura."""
        self.prepare_bootstrap(self.root)
        packet_id = read_state(self.root)["active_packet"]["id"]
        set_active_packet_status(self.root, "completed")
        (self.root / "docs" / "observations.md").write_text(
            "documento de observaciones para el intento\n", encoding="utf-8")
        # Cambio de bytes (JSON sigue válido): un espacio extra al final.
        mutated = self.root / POLICY_FILE
        mutated.write_bytes(curr_policy_bytes(self.root) + b" \n")
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)

        proc, _ = self.run_prepare(self.root, role="implementer",
                                   substage="green",
                                   objective="post-cambio de política")
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="prepare aceptó operar con una política cuya revisión no coincide")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="prepare bloqueado publicó un paquete por stdout")
        self.assertTrue(
            re.search(r"reconcil|reconciliaci", out, re.IGNORECASE),
            msg=f"el diagnóstico no nombra la reconciliación: {out!r}")
        self.assertNotIn("Traceback", proc.stderr, msg="fallo con traceback")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el prepare bloqueado escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="el prepare bloqueado cambió el state")

        resumed, _ = self.run_resume(self.root, packet_id)
        out2 = resumed.stdout + resumed.stderr
        self.assertNotEqual(
            resumed.returncode, 0,
            msg="--resume-packet aceptó reanudar con revisión de política no reconciliada")
        self.assertTrue(
            re.search(r"reconcil|reconciliaci", out2, re.IGNORECASE),
            msg=f"resume bloqueado no nombra la reconciliación: {out2!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="--resume-packet bloqueado escribió el árbol")

        recorded, _ = self.run_record_dispatch(
            self.root, packet_id, "att-t3-block",
            self.root / "docs" / "observations.md")
        out3 = recorded.stdout + recorded.stderr
        self.assertNotEqual(
            recorded.returncode, 0,
            msg="el registro de despacho aceptó operar con revisión no reconciliada")
        # O1 (review-t3.md): el oráculo exige el diagnóstico de RECONCILIACIÓN,
        # no un rechazo genérico: con argv puro (sin opciones ordinarias) el
        # rechazo por modos excluyentes es imposible; el error de reconciliación
        # solo puede venir del bloqueo PD-5 en --record-dispatch.
        self.assertNotIn(
            "unrecognized", out3,
            msg=f"registro bloqueado: opciones inexistentes: {out3!r}")
        self.assertFalse(
            re.search(r"(?i)\bopciones\b|options", out3),
            msg=f"el rechazo fue por opciones/modos, no por reconciliación: {out3!r}")
        self.assertTrue(
            re.search(r"reconcil|reconciliaci", out3, re.IGNORECASE),
            msg=f"registro bloqueado no nombra la reconciliación: {out3!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el registro de despacho bloqueado escribió el árbol")

    def test_pd5_reconcile_accepts_matching_sha_and_decision_ref(self) -> None:
        """PD-5/I6: reconciliación correcta — sha actual + decision-ref dentro
        del proyecto con el sha literal, sin paquete pendiente → acepta; el
        historial conserva la revisión anterior; los paquetes existentes no
        cambian; luego se puede preparar de nuevo y la política no cambia."""
        self.prepare_bootstrap(self.root)
        first_packet_id = read_state(self.root)["active_packet"]["id"]
        first_packet_bytes = published_packets(self.root)[first_packet_id]
        set_active_packet_status(self.root, "completed")
        # La revisión a reconciliar son los bytes ACTUALES tras el cambio.
        old_sha = curr_policy_sha(self.root)
        policy_before = curr_policy_bytes(self.root)
        (self.root / POLICY_FILE).write_bytes(policy_before + b"\n")
        new_sha = curr_policy_sha(self.root)
        decision_path = "docs/decision-policy-revision.md"
        (self.root / decision_path).write_text(
            f"# Decisión del dueño — revisión de política aceptada\n"
            f"sha256: {new_sha}\n", encoding="utf-8")
        before = tree_snapshot(self.root)

        proc, _ = self.run_reconcile(self.root, new_sha, decision_path)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"--reconcile-policy/--decision-ref no existen aún: {out!r}")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"la reconciliación correcta debe aceptarse: {out!r}")
        # Tras aceptar se puede preparar de nuevo.
        proc2, _ = self.run_prepare(self.root)
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"tras reconciliar debe poder prepararse: {proc2.stdout} {proc2.stderr}")
        # La política no fue tocada por la reconciliación ni por el re-prepare.
        self.assertEqual(
            curr_policy_bytes(self.root), policy_before + b"\n",
            msg="la reconciliación o el re-prepare modificaron docs/cdad-policy.json")
        # Revisión previa en el historial de la ejecución + revisión aceptada.
        hist = history_text(self.root)
        self.assertIn(old_sha, hist,
                      msg="la revisión anterior de política no está en el historial")
        self.assertIn(new_sha, hist,
                      msg="la revisión aceptada no está registrada en el historial")
        # Paquetes existentes: bytes idénticos.
        packets_before = {
            pid: data for pid, data in published_packets(self.root).items()
            if pid != read_state(self.root)["active_packet"]["id"]
        }
        self.assertIn(
            first_packet_id, packets_before,
            msg="el paquete previo desapareció tras reconciliar")
        self.assertEqual(
            packets_before[first_packet_id], first_packet_bytes,
            msg="la reconciliación reescribió los bytes del paquete existente")
        self.assertGreater(
            len(published_packets(self.root)), 1,
            msg="tras reconciliar no se preparó el paquete nuevo")

    def test_pd5_reconcile_negatives_rejected_without_writes(self) -> None:
        """PD-5/I6 negativos: decision-ref inexistente, fuera del proyecto o
        sin el sha; sha distinto — todos rechazados sin escrituras ni
        reconciliación (control positivo primero: la opción existe)."""
        self.prepare_bootstrap(self.root)
        set_active_packet_status(self.root, "completed")
        sha = curr_policy_sha(self.root)
        decision_path = "docs/decision-policy-revision.md"
        (self.root / decision_path).write_text(
            f"sha256: {sha}\n", encoding="utf-8")
        proc, _ = self.run_reconcile(self.root, sha, decision_path)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"--reconcile-policy/--decision-ref no existen aún: {out!r}")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"control positivo de reconciliación falló: {out!r}")

        outside = Path(self._tmp) / "decision-outside.md"
        outside.write_text(f"sha256: {sha}\n", encoding="utf-8")
        wrong_sha = hashlib.sha256(b"bytes que no son la politica").hexdigest()
        (self.root / "docs" / "decision-without-sha.md").write_text(
            "decisión sin el hash\n", encoding="utf-8")
        (self.root / "docs" / "decision-wrong-sha.md").write_text(
            f"sha256: {wrong_sha}\n", encoding="utf-8")

        cases = {
            "decision-ref inexistente": (sha, "docs/no-existe.md"),
            "decision-ref fuera del proyecto": (sha, str(outside)),
            "decision-ref sin el sha": (sha, "docs/decision-without-sha.md"),
            "sha distinto del actual": (wrong_sha, "docs/decision-wrong-sha.md"),
        }
        for label, (csha, cref) in cases.items():
            with self.subTest(caso=label):
                self.before = tree_snapshot(self.root)
                self.state_before = state_bytes(self.root)
                proc, _ = self.run_reconcile(self.root, csha, cref)
                out = proc.stdout + proc.stderr
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"{label}: la reconciliación fue aceptada")
                self.assertNotIn("Traceback", proc.stderr,
                                 msg=f"{label}: fallo con traceback")
                self.assertEqual(
                    proc.stdout, "",
                    msg=f"{label}: había salida en stdout de un rechazo")
                self.assertEqual(
                    tree_snapshot(self.root), self.before,
                    msg=f"{label}: hubo escrituras en el árbol")
                self.assertEqual(
                    state_bytes(self.root), self.state_before,
                    msg=f"{label}: el state cambió")

    def test_pd5_reconcile_rejected_with_pending_packet(self) -> None:
        """PD-5/I6: con un paquete pendiente (`prepared`/`dispatched`) la
        reconciliación se rechaza sin escrituras."""
        self.prepare_bootstrap(self.root)
        # Marcar deliberadamente un paquete pendiente en el escenario.
        packet_id = read_state(self.root)["active_packet"]["id"]
        set_active_packet_status(self.root, "prepared")
        sha = curr_policy_sha(self.root)
        decision_path = "docs/decision-policy-revision.md"
        (self.root / decision_path).write_text(
            f"sha256: {sha}\n", encoding="utf-8")
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc, _ = self.run_reconcile(self.root, sha, decision_path)
        out = proc.stdout + proc.stderr
        self.assertNotIn(
            "unrecognized", out,
            msg=f"--reconcile-policy/--decision-ref no existen aún: {out!r}")
        self.assertNotEqual(
            proc.returncode, 0,
            msg="la reconciliación fue aceptada con paquete pendiente")
        self.assertTrue(
            re.search(r"prepared|dispatched|pendiente|pending", out,
                      re.IGNORECASE),
            msg=f"el diagnóstico no nombra el paquete pendiente: {out!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la reconciliación rechazada escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la reconciliación rechazada cambió el state")


# ---------------------------------------------------------------- PD-11


class TestPd11InterruptAndRecover(DurableProjectCase):
    """PD-11 / I5: inyección de interrupciones y recuperación coherente."""

    def test_pd11_fail_at_each_point_rc97_without_packet_output(self) -> None:
        """PD-11/I5: con `CDAD_TEST_FAIL_AT` en cada uno de los 5 puntos el
        prepare termina (código 97) y NO imprime el paquete ni lo publica."""
        for point in FAIL_AT_POINTS:
            with self.subTest(punto=point):
                root = self.new_project()
                self.add_foreign_artifacts(root)
                proc, _ = self.run_prepare(
                    root, env_extra={FAIL_AT_VAR: point},
                    objective=f"interrupción en {point}")
                self.assertEqual(
                    proc.returncode, FAIL_AT_RC,
                    msg=f"{point}: rc esperado {FAIL_AT_RC}, hubo "
                        f"{proc.returncode} (¿el gancho no existe?): "
                        f"{proc.stdout} {proc.stderr}")
                self.assertNotIn(
                    PACKET_BEGIN, proc.stdout,
                    msg=f"{point}: el paquete fue impreso antes de completar "
                        f"su publicación")
                if point != "after-state":
                    # after-state: la publicación ya completó; un paquete en
                    # disco es el resultado esperado, no una violación.
                    self.assertEqual(
                        published_packets(root), {},
                        msg=f"{point}: el fallo dejó un paquete "
                            f"despachable publicado por disco")

    def test_pd11_recovery_after_each_fail_point_coherent_or_retained(self) -> None:
        """PD-11/I5: tras la interrupción, la siguiente invocación sin la
        variable recupera una generación coherente (paquete publicado con
        state y binding coherentes) o conserva el estado anterior; sin borrar
        archivos ajenos de .cdad."""
        for point in FAIL_AT_POINTS:
            with self.subTest(punto=point):
                root = self.new_project()
                foreign = self.add_foreign_artifacts(root)
                proc, _ = self.run_prepare(
                    root, env_extra={FAIL_AT_VAR: point})
                self.assertEqual(
                    proc.returncode, FAIL_AT_RC,
                    msg=f"{point}: la inyección no se activó (rc="
                        f"{proc.returncode}): {proc.stdout} {proc.stderr}")
                crashed_contexts = v2_execution_docs(root)

                self.root_swap(root)
                recovery, _ = self.run_prepare(root)
                self.assert_coherent_generation(recovery)
                if recovery.returncode != 0:
                    # Conservada: los contextos alcanzados antes del fallo
                    # siguen presentes (nada se regeneró por encima del
                    # estado anterior) y hay diagnóstico.
                    self.assertTrue(
                        (recovery.stdout + recovery.stderr).strip(),
                        msg="recuperación fallida sin diagnóstico")
                docs_after = v2_execution_docs(root)
                for eid in crashed_contexts:
                    self.assertIn(
                        eid, docs_after,
                        msg=f"la recuperación perdió el contexto {eid} "
                            f"inyectado antes del fallo")
                self.assert_foreign_survives(foreign)

                # Sin restos que impidan continuar: a partir del estado
                # recuperado, un --resume-packet del paquete activo funciona
                # o un prepare adicional se resuelve de forma coherente.
                state = read_state(root)
                active = state.get("active_packet") or {}
                if active.get("id") and active.get("status") in ("prepared", "dispatched"):
                    resumed, _ = self.run_resume(root, active["id"])
                    self.assertEqual(
                        resumed.returncode, 0,
                        msg=f"{point}: el estado recuperado dejó un paquete "
                            f"pendiente no reanudable: {resumed.stdout} "
                            f"{resumed.stderr}")
                    self.assertTrue(
                        resumed.stdout.startswith(PACKET_BEGIN),
                        msg="resume de recuperación no devolvió el paquete")

    # -- utilidades de scope del test --------------------------------------

    def root_swap(self, root: Path) -> None:
        """El oráculo coherente lee `self.root`; apunta la aserción base."""
        self.root = root


class TestPd11ConcurrencyAndLock(DurableProjectCase):
    """PD-11 / I5: exclusión mediante `.cdad/.lock` y ciclo de vida del lock."""

    def setUp(self) -> None:
        super().setUp()
        self.cdad = self.root / ".cdad"
        self.cdad.mkdir(exist_ok=True)
        self.foreign = self.add_foreign_artifacts(self.root)

    def spawn_holder(self) -> tuple[subprocess.Popen, Path, Path]:
        ready = Path(self._tmp) / "holder-ready.flag"
        release = Path(self._tmp) / "holder-release.flag"
        proc = subprocess.Popen(
            [sys.executable, "-c", HOLDER_SOURCE,
             str(self.cdad / ".lock"), str(ready), str(release)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (release.touch()
                                 if not release.exists() else None,
                                 proc.wait(timeout=30)))
        deadline = time.monotonic() + 10
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not ready.exists():
            self.fail("el proceso titular no tomó el lock a tiempo")
        return proc, ready, release

    def test_pd11_concurrent_prepare_denied_without_writes_then_works(self) -> None:
        """PD-11/I5: con `.cdad/.lock` tomado por otro proceso, un prepare
        concurrente da rc≠0 inmediato con diagnóstico de ocupación y sin
        escrituras; soltado el lock, funciona."""
        holder, _ready, release = self.spawn_holder()
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc, elapsed = self.run_prepare(self.root, timeout=30)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg="prepare procedió pese a que otro proceso ocupa .cdad/.lock")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="prepare bloqueado imprimió un paquete")
        self.assertTrue(
            re.search(r"bloqueo|lock|ocupad|en uso|busy", out, re.IGNORECASE),
            msg=f"el diagnóstico no informa la ocupación del lock: {out!r}")
        self.assertLess(
            elapsed, 15,
            msg=f"prepare esperó al lock en vez de fallar de inmediato "
                f"({elapsed:.1f}s)")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el prepare bloqueado escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="el prepare bloqueado cambió el state")

        release.touch(exist_ok=True)
        holder.wait(timeout=30)
        proc2, _ = self.run_prepare(self.root)
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"tras soltar el lock, prepare debe funcionar: "
                f"{proc2.stdout} {proc2.stderr}")
        self.assertTrue(
            published_packets(self.root),
            msg="tras soltar el lock no quedó paquete publicado")

    def test_pd11_lock_not_orphaned_when_holder_process_dies(self) -> None:
        """PD-11/I5: si el proceso que tenía el lock muere, el lock no queda
        huérfano: el siguiente prepare funciona de inmediato."""
        holder, _ready, _release = self.spawn_holder()
        before = tree_snapshot(self.root)
        holder.kill()  # muere sin soltar el lock (el SO lo libera con el fd)
        holder.wait(timeout=30)
        proc, elapsed = self.run_prepare(self.root, timeout=30)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"el lock quedó huérfano tras morir su proceso: "
                f"{proc.stdout} {proc.stderr}")
        self.assertTrue(
            published_packets(self.root),
            msg="tras morir el lockholder no se publicó paquete")
        self.assert_foreign_survives(self.foreign)


if __name__ == "__main__":
    unittest.main(verbosity=2)
