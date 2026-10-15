#!/usr/bin/env python3
"""004-002 T3/T4 REVIEW-FIX 2 RED — hallazgos de la sección
"Re-review T3 + review T4 (suplente Opus...)" (A-1..A-4, B-1..B-5) de
docs/specs/004-002-project-execution-bootstrap/review-t3.md más la interfaz
I5d (y el contexto I5b/I5c/I8) de docs/specs/004-002-project-execution-bootstrap/plan.md.

Superficie observable: el CLI del productor invocado por argv PURO por caso
(sin helpers que inyecten opciones); proyectos sintéticos T2 en tempdirs;
ninguna lectura de implementación (skills/, scripts/, sources/, install.sh).
Las sondas del reviewer (p_loser_unlink.py, p_orphan_inode.py, p_t4.py,
p_modes.py, p_record_lock.py) son la referencia de reproducción (evidencia
de review, no implementación).

Mapa test → postcondición (hallazgo):

  A-1 rejected_loser_keeps_holders_lock_and_no_c_entry
        PD-11/I5b/I5d: quien pierde la adquisición (flock fallido) da
        rc≠0 "ocupado" y NUNCA retira el .cdad/.lock del tenedor; su
        inodo permanece; un tercero también queda fuera; al soltar A,
        A publica y queda un solo paquete despachable.
  A-2  mixed_reconcile_..._rejected (record / opciones ordinarias)
        PD-4: los modos de `prepare` son excluyentes; argv mixto da rc≠0
        sin escrituras (A-2; B-3 misma causa para --attempt-id).
        Nota: la variante --resume-packet + --reconcile-policy YA se
        rechaza en fc184c1 (rc=2, "resume acepta ninguna opción
        ordinaria", I7) — el T2 ya la cubre; no hay RED que escribir.
  B-3  ordinary_prepare_with_attempt_id_rejected
        PD-4/I8: --attempt-id fuera de --record-dispatch se rechaza.
  A-3  stale_inode_fd_is_rejected_on_acquire
        I5c/I5d: un descriptor sobre el inodo retirado de .lock no
        autoriza la entrada (fstat vs stat); C conserva su lock.
  A-4  recovery_preserves_foreign_txn_directory
        PD-11 + invariante 7: la recuperación limpia solo los archivos
        de transacción PROPIOS; un directorio ajeno dentro de
        .cdad/.txn conserva TODOS sus archivos.
  B-1  record_survives_state_write_failure_via_retry
        I8: el registro del intento y el state se publican en UNA
        transacción; si la escritura del state falla, no queda registro
        publicado y rc≠0; el reintento idéntico completa la transición
        (paquete dispatched).
  B-2  provenance_keys_outside_observed_fields_rejected
        I8: provenance admit solo claves dentro de los cinco campos
        observados; contrabando (result/gate/postconditions_status)
        da rc≠0 sin escrituras.
  B-4  record_rejects_ordinary_options / record_locked_out_by_prepare
        I8+PD-11: el registro también respeta la exclusividad de modos
        y el lock de sección crítica (busy, sin escrituras).
  B-5  multi_runtime_raises_rejected
        I8: la comparación del campo runtime no distingue mayúsculas
        ("Multi-Runtime" se rechaza igual que "multi-runtime").

RED hoy (HEAD fc184c1 + docs): cada test debe fallar por AssertionError
sobre el comportamiento ausente (nunca por import/sintaxis/opciones
inexistentes). Los pausados usan los ganchos I5b/I5d declarados en
plan.md; `before-lock-open` (I5d) hoy NO existe y es la causa declarada
de RED en A-1.
"""

from __future__ import annotations

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
    published_packets,
    read_state,
    tree_snapshot,
    write_state,
    STATE_FILE,
)

from test_004_002_t3_durable import FAIL_AT_RC, FAIL_AT_VAR

# Ganchos de pausa (I5b; I5d añade el punto before-lock-open).
PAUSE_AT_VAR = "CDAD_TEST_PAUSE_AT"
PAUSE_FILE_VAR = "CDAD_TEST_PAUSE_FILE"
PAUSE_WAIT_SECONDS = 35
PAUSE_MAX_INTERNAL = 30

BUSY_RE = re.compile(r"bloqueo|lock|ocupad|en uso|busy", re.IGNORECASE)

FOREIGN_TXN_DIR = "ajeno-no-transaccion-propia"
FOREIGN_TXN_FILES = {
    "execution.json": b'{"execution_id": "ajeno (no de esta invocacion)"}\n',
    "REQUEST.json": b'{"entrada ajena": true}\n',
    "PACKET.md": b"# PACKET ajeno en .cdad/.txn (no de esta ejecucion)\n",
    "state.json": b'{"ajeno": "ni se le borra el state ni el resto"}\n',
}


# ---------------------------------------------------------------- helpers


def policy_bytes(root: Path) -> bytes:
    return (root / POLICY_FILE).read_bytes()


def policy_sha(root: Path) -> str:
    import hashlib

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


def dispatch_path(root: Path, eid: str, attempt_id: str) -> Path:
    return (root / ".cdad" / "executions" / eid / "dispatches"
            / f"{attempt_id}.json")


def observation_doc(**overrides) -> dict:
    """Documento de observación I8 (claves cerradas, cinco campos + provenance)."""
    doc = {
        "runtime": "opencode",
        "model_configured": "glm-5.3-flash",
        "model_reported": "glm-5.3-flash",
        "session": "ses-reviewfix2-0001",
        "started_at": "2026-09-30T12:00:00Z",
        "provenance": {
            "runtime": "reported by runtime",
            "model_reported": "orchestrator",
            "session": "orchestrator",
        },
    }
    doc.update(overrides)
    return doc


class ReviewFix2Case(unittest.TestCase):
    """Base: proyecto sintético T2 en tempdir propio; CLI por argv puro."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-t34rf2-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        self._parked: list[tuple[subprocess.Popen, Path]] = []

    # -- corridas CLI (argv puro se construye por caso) -------------------

    def cli(self, argv: list[str], *, env_extra: dict | None = None,
            timeout: float = 120) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *argv],
            capture_output=True, text=True, cwd=SCRIPT.parents[1],
            env=env, timeout=timeout)

    def out(self, proc) -> str:
        return proc.stdout + proc.stderr

    # -- pausas deterministas (ganchos I5b/I5d) ---------------------------

    def spawn_parked(self, argv: list[str], *, pause_at: str,
                     pause_file: Path,
                     env_extra: dict | None = None) -> subprocess.Popen:
        env = dict(os.environ)
        env[PAUSE_AT_VAR] = pause_at
        env[PAUSE_FILE_VAR] = str(pause_file)
        env.update(env_extra or {})
        proc = subprocess.Popen(
            [sys.executable, str(SCRIPT), *argv],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=SCRIPT.parents[1], env=env)
        self._parked.append((proc, pause_file))
        self.addCleanup(self.reap, proc, pause_file)
        return proc

    @staticmethod
    def reached_file(flag: Path) -> Path:
        return Path(str(flag) + ".reached")

    def wait_parked(self, proc: subprocess.Popen, flag: Path,
                    label: str, timeout: float = 40) -> None:
        """Espera a <flag>.reached (pausa alcanzada); Assertion error
        explícito cuando el gancho de pausa no existe/RED."""
        reached = self.reached_file(flag)
        deadline = time.monotonic() + timeout
        while (time.monotonic() < deadline and proc.poll() is None
               and not reached.exists()):
            time.sleep(0.05)
        if not reached.exists():
            if proc.poll() is not None:
                out, err = proc.communicate(timeout=30)
                detail = (f"rc={proc.returncode} stdout={out[:200]!r} "
                          f"stderr={err[:200]!r}")
            else:
                detail = "el proceso sigue vivo sin crear <ruta>.reached"
            self.fail(
                f"{label}: el punto de pausa no es alcanzable ( hoy es RED "
                f"si el gancho no existe, p. ej. before-lock-open de I5d): "
                f"{detail}")

    def release(self, proc: subprocess.Popen, flag: Path,
                timeout: float = 90) -> tuple[str, str]:
        flag.touch(exist_ok=True)
        return proc.communicate(timeout=timeout)

    def reap(self, proc: subprocess.Popen, flag: Path) -> None:
        if proc.poll() is None:
            try:
                flag.touch(exist_ok=True)
                proc.communicate(timeout=45)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate(timeout=15)

    def tearDown(self) -> None:
        # Liberar todo proceso pausado antes de que pytest cierre pipes.
        for proc, flag in list(self._parked):
            self.reap(proc, flag)


# ---------------------------------------------------------------- A-1


class TestA1LoserNeverRemovesHoldersLock(ReviewFix2Case):
    def test_a1_rejected_b_keeps_a_lock_and_c_is_rejected(self) -> None:
        """A-1 (PD-11, I5d): con .cdad existente y sin .lock, A adquiere
        (creando el archivo) y se pausa en reserved-id (I5b); B se pausa en
        before-lock-open (I5d). Soltar B: rc≠0 "ocupado" y .lock SIGUE
        existiendo con el MISMO inodo de A; un C lanzado entonces también
        da rc≠0; al soltar A, A publica bien y queda un solo paquete
        despachable. RED hoy: el punto before-lock-open no existe (I5d)."""
        root = self.root
        # Precondición: .cdad existe y .lock NO (p. ej. tras un rechazo I5c).
        (root / ".cdad").mkdir(exist_ok=True)

        flag_a = Path(self._tmp) / "pause-a.flag"
        flag_b = Path(self._tmp) / "pause-b.flag"
        argv_a = [
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "encargo A (tenedor)",
        ]
        argv_b = [
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "encargo B (perdedor)",
        ]

        proc_a = self.spawn_parked(argv_a, pause_at="reserved-id",
                                   pause_file=flag_a)
        self.wait_parked(
            proc_a, flag_a,
            "A en reserved-id (I5b) — precondición de reproducción")
        self.assertTrue(
            lock_path(root).is_file(),
            msg="A pausado en reserved-id no dejó el rendezvous .cdad/.lock")
        ino_a = os.stat(lock_path(root)).st_ino

        proc_b = self.spawn_parked(argv_b, pause_at="before-lock-open",
                                   pause_file=flag_b)
        self.wait_parked(
            proc_b, flag_b,
            "B en before-lock-open (I5d; hoy ese punto no existe: RED)",
            timeout=PAUSE_MAX_INTERNAL)

        # Soltar B: la adquisición debe perder limpio.
        out_b, err_b = self.release(proc_b, flag_b)
        outb_all = out_b + err_b
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        proc_c = self.cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "encargo C (observador)",
        ], timeout=60)
        out_c_all = proc_c.stdout + proc_c.stderr

        # Postcondiciones A-1.
        self.assertNotEqual(
            proc_b.returncode, 0,
            msg="B (perdedor) no debe terminar con éxito: el lock de A "
                "está ocupado")
        self.assertFalse(
            out_b.startswith(PACKET_BEGIN),
            msg="B perdedor imprimió un paquete despachable")
        self.assertTrue(
            BUSY_RE.search(outb_all),
            msg=f"B no informa la ocupación: {outb_all!r}")
        self.assertTrue(
            lock_path(root).is_file(),
            msg="el perdedor B retiró el .cdad/.lock del tenedor A "
                "(A-1/F1): el único que retira es __exit__ de una "
                "adquisición verificada")
        self.assertEqual(
            os.stat(lock_path(root)).st_ino, ino_a,
            msg="el inodo de .lock cambió con A todavía dentro: "
                "alguien no autorizado lo reemplazó")
        self.assertEqual(
            tree_snapshot(root), before,
            msg="alguno de B/C escribió el árbol con A aún en la "
                "sección crítica")
        self.assertEqual(
            state_bytes(root), state_before,
            msg="alguno de B/C cambió el state")
        self.assertNotEqual(
            proc_c.returncode, 0,
            msg="C entró pese a que A sigue dentro de la sección "
                "crítica (sus primeros 5 argv son irrelevantes; la "
                "exclusión debe rechazarlo): " + out_c_all[:200])
        self.assertFalse(
            proc_c.stdout.startswith(PACKET_BEGIN),
            msg="C imprimió un paquete con A dentro (dos tenedores "
                "simultáneos, F2 reintroducido)")

        # Soltar A: publica bien; un solo paquete despachable.
        out_a, err_a = self.release(proc_a, flag_a)
        self.assertEqual(
            proc_a.returncode, 0,
            msg=f"al soltar la pausa, A publica bien: {out_a[:200]} "
                f"{err_a[:200]}")
        self.assertTrue(
            out_a.startswith(PACKET_BEGIN),
            msg="A publicó sin imprimir el paquete canónico")
        packets = published_packets(root)
        self.assertEqual(
            len(packets), 1,
            msg=f"quedaron {sorted(packets)} paquetes publicados: la "
                "exclusión permitió publicar de más")
        active = read_state(root)["active_packet"]
        self.assertIn(
            active["status"], ("prepared", "dispatched"),
            msg=f"el paquete activo no quedó despachable: {active['status']!r}")
        self.assertEqual(
            packets.get(active["id"]),
            out_a.encode(),
            msg="los bytes del paquete activo no coinciden con el stdout "
                "de A: la publicación de A quedó sobrescrita")


# ---------------------------------------------------------------- A-2 / B-3


class MixedArgvCase(ReviewFix2Case):
    """Base común: bootstrap + paquete completado + decisión del dueño
    materializada, de modo que cada operación POR SEPARADO se aceptaría
    (el rechazo mixto solo puede deberse a la exclusividad de modos)."""

    def bootstrap_completed(self) -> tuple[str, str, str]:
        proc = self.cli([
            "prepare", "--project-root", str(self.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "bootstrap rf2",
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): bootstrap falló: "
                f"{proc.stdout} {proc.stderr}")
        set_active_packet_status(self.root, "completed")
        sha = policy_sha(self.root)
        decision_ref = "docs/dec-rf2.md"
        (self.root / decision_ref).write_text(
            f"# Decisión del dueño\nsha256: {sha}\n", encoding="utf-8")
        packet_id = read_state(self.root)["active_packet"]["id"]
        return packet_id, sha, decision_ref


class TestA2MixedReconcileArgvIsRejected(MixedArgvCase):
    def test_a2_reconcile_plus_record_rejected_no_writes(self) -> None:
        """A-2 (PD-4): --reconcile-policy combinado con --record-dispatch
        da rc≠0 sin ninguna escritura (hoy: rc=0 y descarta en silencio
        una de las operaciones)."""
        packet_id, sha, decision_ref = self.bootstrap_completed()
        obs = Path(self._tmp) / "obs-mix.json"
        obs.write_text(json.dumps(observation_doc()), encoding="utf-8")
        argv = [
            "prepare", "--project-root", str(self.root),
            "--reconcile-policy", sha, "--decision-ref", decision_ref,
            "--record-dispatch", packet_id, "--attempt-id", "a-mix",
            "--input", str(obs),
        ]
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(argv)
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="el modo mixto cayó en getopt en vez del rechazo de "
                "exclusividad de modos")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"argv mixto (--reconcile-policy + --record-dispatch) fue "
                f"aceptado (A-2): {proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="la invocación mixta imprimió un paquete")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la invocación mixta escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la invocación mixta cambió el state")

    def test_a2_reconcile_plus_ordinary_options_rejected_no_writes(
            self) -> None:
        """A-2 (PD-4): --reconcile-policy con opciones ordinarias
        (--role/--objective) da rc≠0 sin escrituras (hoy: rc=0,
        reconcilia y descarta las ordinarias)."""
        packet_id, sha, decision_ref = self.bootstrap_completed()
        argv = [
            "prepare", "--project-root", str(self.root),
            "--reconcile-policy", sha, "--decision-ref", decision_ref,
            "--role", "implementer",
            "--substage", "green",
            "--objective", "ordinario mezclado",
        ]
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(argv)
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="las opciones de reconciliación no existen")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"--reconcile-policy aceptó opciones ordinarias (A-2): "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="la invocación mixta imprimió un paquete")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la invocación mixta escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la invocación mixta cambió el state")

class TestB3OrdinaryPrepareAttemptIdRejected(MixedArgvCase):
    def test_b3_ordinary_prepare_with_attempt_id_rejected(self) -> None:
        """B-3 (PD-4/I8, misma causa que A-2): un prepare ordinario con
        --attempt-id da rc≠0 sin escrituras (hoy: prepare ignora la
        opción y publica)."""
        packet_id, sha, decision_ref = self.bootstrap_completed()
        argv = [
            "prepare", "--project-root", str(self.root),
            "--role", "implementer", "--substage", "green",
            "--objective", "ordinario con attempt-id",
            "--attempt-id", "a-ordinaria",
        ]
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(argv)
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--attempt-id no existe como opción")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"el prepare ordinario aceptó --attempt-id (B-3): "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="la invocación rechazada imprimió un paquete")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la invocación mixta escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la invocación mixta cambió el state")


# ---------------------------------------------------------------- A-3

HARNESS_OPEN = Path(__file__).resolve().parent / "_rf2_open_pause.py"


class TestA3StaleInodeFdRejectedOnAcquire(ReviewFix2Case):
    def _spawn_b_harness(self, argv: list[str], flag: Path) -> subprocess.Popen:
        """B: el CLI real corrido bajo pruebas con el `os.open` pausado
        tras abrir .cdad/.lock y antes del flock (instrumentación de la
        sonda p_orphan_inode/harness_b del reviewer; argv puro intacto)."""
        env = dict(os.environ)
        env.pop(PAUSE_AT_VAR, None)
        env.pop(PAUSE_FILE_VAR, None)
        proc = subprocess.Popen(
            [sys.executable, str(HARNESS_OPEN), str(SCRIPT),
             "after-open", str(flag), *argv],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=SCRIPT.parents[1], env=env)
        self._parked.append((proc, flag))
        self.addCleanup(self.reap, proc, flag)
        return proc

    def test_a3_fd_over_retired_lock_inode_is_rejected(self) -> None:
        """A-3 (I5c/I5d): un proceso con descriptor sobre un inodo de
        .lock YA RETIRADO (reemplazado por otro) no entra: rc≠0. Forma
        del reviewer: A falla por PD-5 y retira .lock y .cdad; B conserva
        el descriptor viejo; C toma el nuevo."""
        root = self.root
        flag_a = Path(self._tmp) / "a3-a.flag"
        flag_b = Path(self._tmp) / "a3-b.flag"
        flag_c = Path(self._tmp) / "a3-c.flag"
        argv = [
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "encargo {tag}",
        ]

        # A: crea .lock, toma el flock y se pausa en reserved-id.
        proc_a = self.spawn_parked(
            [a.replace("{tag}", "A") for a in argv],
            pause_at="reserved-id", pause_file=flag_a)
        self.wait_parked(
            proc_a, flag_a, "A en reserved-id — precondición de A-3")
        ino_a = os.stat(lock_path(root)).st_ino

        # B se pausa CON el descriptor de A's inode (tras open, pre-flock).
        proc_b = self._spawn_b_harness(
            [a.replace("{tag}", "B") for a in argv], flag_b)
        self.wait_parked(
            proc_b, flag_b, "B tras open de .lock (sonda p_orphan_inode)",
            timeout=PAUSE_MAX_INTERNAL)

        # A falla por PD-5 (política alterada) y retira .lock y .cdad.
        pol = root / POLICY_FILE
        orig = pol.read_bytes()
        pol.write_bytes(orig + b" ")
        out_a, err_a = self.release(proc_a, flag_a)
        self.assertNotEqual(
            proc_a.returncode, 0,
            msg=f"precondición: A debe fallar por PD-5: {out_a!r} {err_a!r}")
        self.assertFalse(
            lock_path(root).exists(),
            msg="precondición: el camino de fallo (I5c) debe retirar el "
                ".lock que la propia invocación creó")

        # C arranca de cero: crea .cdad/.lock con inodo NUEVO y se pausa.
        pol.write_bytes(orig)
        proc_c = self.spawn_parked(
            [a.replace("{tag}", "C") for a in argv],
            pause_at="reserved-id", pause_file=flag_c)
        self.wait_parked(
            proc_c, flag_c, "C en reserved-id — precondición de A-3")
        ino_c = os.stat(lock_path(root)).st_ino
        self.assertNotEqual(
            ino_c, ino_a,
            msg="precondición: C debe tener un inodo distinto del "
                "retirado")

        # B libera su flock sobre el INODO RETIRADO: debe ser rechazado
        # (comprobación de inodo fstat-vs-stat), no entrar.
        before = tree_snapshot(root)
        state_before = state_bytes(root)
        out_b, err_b = self.release(proc_b, flag_b)
        outb_all = out_b + err_b
        self.assertNotEqual(
            proc_b.returncode, 0,
            msg=f"B entró con un descriptor sobre el inodo retirado "
                f"{ino_a} (A-3/I5c: la adquisición debe verificar "
                f"fstat(fd) == stat(ruta)): {outb_all[:200]!r}")
        self.assertFalse(
            out_b.startswith(PACKET_BEGIN),
            msg="B (inodo huérfano) imprimió un paquete despachable")
        self.assertTrue(
            lock_path(root).is_file(),
            msg="B retiró el .lock de C al salir")
        self.assertEqual(
            os.stat(lock_path(root)).st_ino, ino_c,
            msg="el inodo del lock de C cambió con B huérfano dentro")
        self.assertEqual(
            tree_snapshot(root), before,
            msg="B (inodo retirado) escribió el árbol")
        self.assertEqual(
            state_bytes(root), state_before,
            msg="B (inodo retirado) cambió el state")

        # C publica limpio.
        out_c, err_c = self.release(proc_c, flag_c)
        self.assertEqual(
            proc_c.returncode, 0,
            msg=f"C debe publicar: {out_c[:200]} {err_c[:200]}")
        self.assertTrue(
            out_c.startswith(PACKET_BEGIN),
            msg="C publicó sin imprimir el paquete canónico")
        validated = self.cli([
            "validate-state", "--project-root", str(root)])
        self.assertEqual(
            validated.returncode, 0,
            msg=f"postcondición: state válido tras C: "
                f"{validated.stdout} {validated.stderr}")


# ---------------------------------------------------------------- A-4


class TestA4RecoveryPreservesForeignTxnDirectory(ReviewFix2Case):
    def test_a4_recovery_preserves_foreign_txn_dir_and_all_files(
            self) -> None:
        """A-4 (PD-11 + invariante 7): la recuperación limpia solo las
        transacciones PROPIAS. Un directorio AJENO dentro de .cdad/.txn
        (nombre que no es el de una transacción propia) conserva TODOS
        sus archivos —execution.json, REQUEST.json, PACKET.md y
        state.json incluidos— tras una recuperación. RED hoy: la
        limpieza elige por nombre de archivo y borra el state.json (y
        el resto) del directorio ajeno."""
        root = self.root
        env_fail = {FAIL_AT_VAR: "context-written"}
        first = self.cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "interrupcion para .txn",
        ], env_extra=env_fail)
        self.assertEqual(
            first.returncode, FAIL_AT_RC,
            msg=f"precondición: interrupción 1 debe activarse: "
                f"{first.stdout} {first.stderr}")
        second = self.cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "interrupcion repetida",
        ], env_extra=env_fail)
        self.assertEqual(
            second.returncode, FAIL_AT_RC,
            msg=f"precondición: interrupción 2 debe activarse: "
                f"{second.stdout} {second.stderr}")

        if not txn_root(root).is_dir():
            self.fail(
                "precondición: la interrupción debe dejar un directorio de "
                "transacción en .cdad/.txn")
        own_dirs = {p.name for p in txn_root(root).iterdir() if p.is_dir()}
        foreign = txn_root(root) / FOREIGN_TXN_DIR
        foreign.mkdir(parents=True, exist_ok=True)
        for name, payload in FOREIGN_TXN_FILES.items():
            (foreign / name).write_bytes(payload)

        recovery = self.cli([
            "prepare", "--project-root", str(root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "recuperacion normal",
        ])
        self.assertEqual(
            recovery.returncode, 0,
            msg=f"precondición: la recuperación debe terminar rc 0: "
                f"{recovery.stdout} {recovery.stderr}")

        if not txn_root(root).is_dir():
            self.fail(
                "la recuperación eliminó .cdad/.txn por completo, "
                f"incluido el directorio ajeno {FOREIGN_TXN_DIR} "
                "(A-4: la limpieza debe tocar solo transacciones propias)")
        still_there = {p.name for p in txn_root(root).iterdir()
                       if p.is_dir()}
        self.assertTrue(
            own_dirs <= still_there,
            msg=f"la recuperación borró una transacción propia: "
                f"{sorted(own_dirs - still_there)}")
        for name, payload in FOREIGN_TXN_FILES.items():
            target = foreign / name
            self.assertTrue(
                target.is_file(),
                msg=f"la recuperación borró {name} del directorio ajeno "
                    f"{FOREIGN_TXN_DIR} dentro de .cdad/.txn (A-4: la "
                    f"limpieza debe tocar solo transacciones propias)")
            self.assertEqual(
                target.read_bytes(), payload,
                msg=f"la recuperación modificó los bytes de {name} del "
                    f"directorio ajeno (A-4)")


# ---------------------------------------------------------------- B-1 / B-2 / B-4 / B-5


class RecordCase(ReviewFix2Case):
    """Base: proyecto T2 con bootstrap v2 y paquete activo; observación
    I8 escrita FUERA de root (p. ej. docs/ puede quedar no escribible)."""

    def bootstrap_ready(self) -> tuple[str, str]:
        proc = self.cli([
            "prepare", "--project-root", str(self.root),
            "--role", "test-writer", "--substage", "red",
            "--objective", "bootstrap record",
        ])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición (fixture): {proc.stdout} {proc.stderr}")
        eid = read_state(self.root)["execution"]["id"]
        pid = read_state(self.root)["active_packet"]["id"]
        return eid, pid

    def write_obs(self, name: str, doc: dict) -> Path:
        path = Path(self._tmp) / name
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def record_argv(self, packet_id: str, attempt_id: str, obs: Path,
                    *extra: str) -> list[str]:
        return [
            "prepare", "--project-root", str(self.root),
            "--record-dispatch", packet_id, "--attempt-id", attempt_id,
            "--input", str(obs), *extra,
        ]


class TestB1RecordAtomicWithState(RecordCase):
    def test_b1_state_write_failure_leaves_no_published_record(self) -> None:
        """B-1 (I8): el registro del intento y el state se publican en UNA
        transacción. Si la escritura del state falla durante
        --record-dispatch (docs/ no escribible), no queda registro
        publicado y rc≠0; un reintento idéntico, ya con permisos, deja el
        paquete en dispatched. RED hoy: el registro queda publicado con
        rc≠0 y el reintento sale antes de la transición."""
        root = self.root
        eid, pid = self.bootstrap_ready()
        obs = self.write_obs("obs-b1.json", observation_doc())
        argv = self.record_argv(pid, "a-b1", obs)

        os.chmod(root / "docs", 0o555)
        self.addCleanup(os.chmod, root / "docs", 0o755)
        proc = self.cli(argv)
        os.chmod(root / "docs", 0o755)  # ya con permisos para el resto

        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--record-dispatch/--attempt-id/--input no existen")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"el registro no reportó el fallo de la escritura del "
                f"state: {proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            dispatch_path(root, eid, "a-b1").is_file(),
            msg="quedó el registro publicado pese a que la escritura del "
                "state falló (B-1): deben publicarse en UNA transacción")
        self.assertEqual(
            read_state(root)["active_packet"]["status"], "prepared",
            msg="el status del paquete cambió en un registro que falló")

        # Reintento idéntico (mismo argv, mismo documento): completa la
        # transición pendiente.
        proc2 = self.cli(argv)
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"el reintento idéntico debe completar la transición "
                f"pendiente (B-1): {proc2.stdout!r} {proc2.stderr!r}")
        self.assertEqual(
            read_state(root)["active_packet"]["status"], "dispatched",
            msg="el reintento idéntico no dejó el paquete en dispatched")


class TestB2ProvenanceKeysClosed(RecordCase):
    def test_b2_provenance_keys_outside_observed_fields_rejected(
            self) -> None:
        """B-2 (I8): provenance admite solo claves dentro de los cinco
        campos observados (runtime, model_configured, model_reported,
        session, started_at). Contrabando vía result/gate/
        postconditions_status da rc≠0 sin escrituras. RED hoy: se
        acepta (vía para colar recepción)."""
        eid, pid = self.bootstrap_ready()
        obs = self.write_obs("obs-b2.json", observation_doc(provenance={
            "result": "PASS",
            "gate": "approved",
            "postconditions_status": "green",
        }))
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(self.record_argv(pid, "a-b2", obs))
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--record-dispatch no existe")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"provenance con claves de contrabando (result/gate/"
                f"postconditions_status) fue aceptado (B-2): "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            dispatch_path(self.root, eid, "a-b2").is_file(),
            msg="el registro de contrabando quedó publicado (B-2)")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el registro rechazado escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="el registro rechazado cambió el state")


class TestB4RecordExclusivityAndLock(RecordCase):
    def test_b4_record_rejects_ordinary_options(self) -> None:
        """B-4 (I8, exclusividad — mata M21): record-dispatch con
        --role/--objective da rc≠0 sin escrituras."""
        eid, pid = self.bootstrap_ready()
        obs = self.write_obs("obs-b4.json", observation_doc())
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(self.record_argv(pid, "a-b4", obs,
                                         "--role", "implementer",
                                         "--objective", "mezclado"))
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--record-dispatch/--attempt-id/--input no existen")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"record-dispatch aceptó --role/--objective (B-4/M21): "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            dispatch_path(self.root, eid, "a-b4").is_file(),
            msg="la invocación mixta publicó el registro")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la invocación mixta escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la invocación mixta cambió el state")

    def test_b4_record_locked_out_while_prepare_in_critical_section(
            self) -> None:
        """B-4 (PD-11, lock del registro — mata M22): con un prepare
        dentro de la sección crítica (pausado en reserved-id, I5b), el
        registro da rc≠0 busy sin escrituras."""
        eid, pid = self.bootstrap_ready()
        set_active_packet_status(self.root, "completed")
        obs = self.write_obs("obs-b4b.json", observation_doc())
        flag_a = Path(self._tmp) / "b4-a.flag"
        proc_a = self.spawn_parked([
            "prepare", "--project-root", str(self.root),
            "--role", "implementer", "--substage", "green",
            "--objective", "prepare pausado (tenedor)",
        ], pause_at="reserved-id", pause_file=flag_a)
        self.wait_parked(
            proc_a, flag_a, "A en reserved-id — precondición de B-4b")
        ino_a = os.stat(lock_path(self.root)).st_ino

        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(self.record_argv(pid, "a-b4b", obs))
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--record-dispatch no existe")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"el registro entró pese a que un prepare ocupa la "
                f"sección crítica (B-4/M22): {proc.stdout!r} "
                f"{proc.stderr!r}")
        self.assertFalse(
            proc.stdout.startswith(PACKET_BEGIN),
            msg="el registro bloqueado imprimió un paquete")
        self.assertTrue(
            lock_path(self.root).is_file(),
            msg="el registro bloqueado retiró el .lock del tenedor")
        self.assertEqual(
            os.stat(lock_path(self.root)).st_ino, ino_a,
            msg="el inodo del lock del tenedor cambió")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el registro bloqueado escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="el registro bloqueado cambió el state")

        out_a, err_a = self.release(proc_a, flag_a)
        self.assertEqual(
            proc_a.returncode, 0,
            msg=f"el tenedor debe poder publicar tras el bloqueo: "
                f"{out_a[:200]} {err_a[:200]}")


class TestB5RuntimeCaseInsensitive(RecordCase):
    def test_b5_multi_runtime_with_capitals_rejected(self) -> None:
        """B-5 (I8, nit): la comparación del campo runtime no distingue
        mayúsculas: "Multi-Runtime" se rechaza igual que
        "multi-runtime" (RED hoy: se acepta)."""
        eid, pid = self.bootstrap_ready()
        obs = self.write_obs(
            "obs-b5.json", observation_doc(runtime="Multi-Runtime"))
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        proc = self.cli(self.record_argv(pid, "a-b5", obs))
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="--record-dispatch no existe")
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"runtime {obs.name} 'Multi-Runtime' fue aceptado "
                f"(B-5, comparación case-sensitive): "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertFalse(
            dispatch_path(self.root, eid, "a-b5").is_file(),
            msg="el registro con runtime mayúsculo quedó publicado")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="el registro rechazado escribió el árbol")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="el registro rechazado cambió el state")


if __name__ == "__main__":
    unittest.main(verbosity=2)
