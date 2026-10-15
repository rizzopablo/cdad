#!/usr/bin/env python3
"""003-002 T1 RED review-fix — hallazgos R1, R2, R3 y R5 de review-t1.md.

Contract:
- docs/specs/003-002-artifact-tools/spec.md (§2 interfaz, §3 segmentos
  seguros, §4 scopes del manifest, §5 atomicidad/concurrencia/integridad,
  §6 receipt mecánico)
- docs/specs/003-002-artifact-tools/review-t1.md (dictamen: R1/R2/R3
  BLOCKING + R5 optional; ruta recomendada: RED (R1 negativo + R2/R3/R5
  locks) → review-fix GREEN → re-review focal)

Mapa hallazgo → test (cada test nombra su hallazgo y su postcondición):

- R1 (BLOCKING, RED hoy): `test_r1_forged_receipt_with_traversal_part_name_is_rejected`
  — un recibo forjado cuyo `parts[i].name` es traversal (§3: los nombres de
  part son segmentos seguros ASCII, sin separadores ni `..`) debe ser
  RECHAZADO por `validate-receipt` con diagnóstico por stderr, aunque el
  archivo fuera del project root coincida byte a byte con el digest
  declarado en el recibo (hoy la junction `parts/<name>.utf8` del §5
  resuelve y lee fuera del root). P3 (validación del recibo) + §3 + §5
  («Receipt o payload durable incompleto/tampered: error de integridad»).
- R2a (lock, pasa hoy): `test_r2a_kill_before_publish_retry_completes` —
  kill del subprocess `receive` en el límite observable antes de publicar
  (detección del directorio temporal hermano del §5): no existe resultado
  final y el retry completa. P2.
- R2b (lock, pasa hoy): `test_r2b_concurrent_identical_receives_converge`
  — dos receives concurrentes idénticos: ambos rc=0, un solo receipt
  durable y stdout byte a byte idéntico. P2.
- R3 (locks, pasan hoy): `test_r3_trusted_manifest_with_in_scope_change_scope_passed`
  y `test_r3_renamed_change_with_previous_path_scope_passed` — manifest
  trusted con cambio IN-SCOPE (`tests/…`, el write scope del paquete
  fixture) → rc=0 y `scope_validation="passed"`; variante `renamed` con
  `previous_path` también se valida. P6/§4.
- R5 (locks, pasan hoy): `test_r5_validate_receipt_accepts_valid_durable_receipt`
  (recibo durable válido → rc=0) y
  `test_r5_validate_receipt_rejects_tampered_store_part` (part del store
  mutada → rc≠0 con diagnóstico por stderr y sin stdout). P3/§5.

Los tests no leen implementación: la superficie observable es el CLI de §2
y el layout de §5; los fixtures reutilizan `EstablishedProjectCase` de la
batería T1 (`tests/test_003_002_t1_receive.py`).
"""

from __future__ import annotations

import copy
import json
import os
import signal
import subprocess
import sys
import time
import unittest

from tests.test_003_002_t1_receive import (
    IN_SCOPE_CHANGE,
    REPO_ROOT,
    RESULT_SCRIPT,
    STAGED_PARTS,
    EstablishedProjectCase,
    err_text,
    out_text,
    run_result_cli,
)

# Intentos para ganar la carrera de congelar el receive antes del rename
# de publicación (§5). Cada intento usa un proyecto sintético fresco.
KILL_ATTEMPTS = 5
KILL_DETECT_TIMEOUT_S = 20.0
RECEIVE_TIMEOUT_S = 120.0


def popen_result_cli(args: list[str]) -> subprocess.Popen:
    """Lanzamiento del CLI de 003-002 sin bloquear (bytes en pipes)."""
    return subprocess.Popen(
        [sys.executable, str(RESULT_SCRIPT), *args],
        cwd=REPO_ROOT, stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)


# ------------------------------------------------------------------- R1


class TestR1ForgedReceiptTraversal(EstablishedProjectCase):
    """R1 (BLOCKING): junction de part con `name` controlado por el input."""

    def test_r1_forged_receipt_with_traversal_part_name_is_rejected(self) -> None:
        """R1: `validate-receipt` debe RECHAZAR (rc≠0, diagnóstico por
        stderr) un recibo forjado cuyo `parts[i].name` es traversal, aunque
        el archivo apuntado fuera del project root coincida byte a byte con
        el digest declarado. Nada fuera del project root debe leerse para
        «validar» el recibo (§3: los nombres de part son segmentos seguros;
        §5: la integridad se verifica contra el store del proyecto)."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)

        first = self.run_receive(descriptor)
        self.assertEqual(
            first.returncode, 0,
            msg=f"R1 (precondición): el receive inicial debe publicar el "
                f"recibo durable: rc={first.returncode} "
                f"stdout={out_text(first)!r} stderr={err_text(first)!r}")
        durable_receipt = json.loads(self.receipt_path().read_bytes())

        # Precondición de atribución: validate-receipt acepta el recibo
        # durable íntegro (R5 positivo); así un rechazo del recibo forjado
        # se atribuye al traversal y no a un validador roto.
        sane = run_result_cli(["validate-receipt",
                               "--project-root", str(self.root),
                               "--receipt", str(self.receipt_path())])
        self.assertEqual(
            sane.returncode, 0,
            msg=f"R1 (precondición): validate-receipt debe aceptar el "
                f"recibo durable íntegro: rc={sane.returncode} "
                f"stderr={err_text(sane)!r}")

        # Archivo de escape FUERA del project root (hermano del root en el
        # tmpdir del fixture) con los bytes exactos del part: si la
        # validación resuelve la junction `parts/<name>.utf8` del §5 con el
        # nombre forjado, encuentra ahí un contenido cuyo digest coincide
        # con el declarado — la única defensa posible es rechazar el nombre.
        report_name = "role-report"
        report_bytes = self.staged_report_data()
        escape_file = self.root.parent / "escape-target.utf8"
        escape_file.write_bytes(report_bytes)
        self.assertFalse(
            escape_file.resolve().is_relative_to(self.root.resolve()),
            msg="fixture: el target de escape debe quedar fuera del "
                "project root")

        traversal_name = "../" * 7 + "escape-target"
        # Sanidad del fixture (aritmética de paths del contrato §5, no de
        # la implementación): la junction `parts/<name>.utf8` con el nombre
        # forjado resuelve exactamente en el archivo de escape.
        resolved = (self.final_dir() / "parts"
                    / (traversal_name + ".utf8")).resolve()
        self.assertEqual(
            resolved, escape_file.resolve(),
            msg="fixture: la junction §5 con el nombre forjado debe "
                "resolver fuera del project root")

        forged = copy.deepcopy(durable_receipt)
        index = next(i for i, part in enumerate(forged["parts"])
                     if part["name"] == report_name)
        forged["parts"][index]["name"] = traversal_name
        forged_path = self.root.parent / "forged-receipt.json"
        forged_path.write_text(
            json.dumps(forged, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        escape_before = escape_file.read_bytes()

        proc = run_result_cli(["validate-receipt",
                               "--project-root", str(self.root),
                               "--receipt", str(forged_path)])
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"R1: un recibo forjado con parts[i].name de traversal "
                f"debe ser RECHAZADO con diagnóstico (hoy la junction "
                f"parts/<name>.utf8 resuelve y lee fuera del project "
                f"root): rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        self.assertTrue(
            err_text(proc).strip(),
            msg="R1: el rechazo debe proporcionar diagnóstico por stderr "
                "(§2: «diagnóstico por stderr»)")
        self.assertNotIn(
            "Traceback", err_text(proc),
            msg="R1: el rechazo debe ser un diagnóstico, no un traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="R1: en rechazo no se emite evidencia parcial por stdout")
        # Nada fuera del project root fue tocado por la validación.
        self.assertEqual(
            escape_file.read_bytes(), escape_before,
            msg="R1: validate-receipt no debe leer (ni tocar) nada fuera "
                "del project root")


# ------------------------------------------------------------------- R2


class TestR2KillAndConcurrency(EstablishedProjectCase):
    """R2 (BLOCKING): batería RED de T1 incompleta — kill antes del
    publish y receives concurrentes (§5; plan T1: «retry/interrupción/dos
    procesos»)."""

    def prepare_receive_fixture(self):
        """Proyecto dispatched + parts + manifest + descriptor listos."""
        self.new_dispatched_project()
        parts = self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=parts,
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        return parts, descriptor

    def kill_receive_before_publish(self, descriptor) -> bool:
        """Congela y mata un `receive` en el límite observable antes del
        rename de publicación (§5: «directorio temporal hermano» → rename
        exclusivo). Devuelve True sólo si el kill ocurrió antes de publicar
        (sin directorio final)."""
        exec_results_dir = (self.root / ".cdad" / "runtime" / "results"
                            / self.execution_id)
        proc = popen_result_cli(self.receive_args(descriptor))
        deadline = time.monotonic() + KILL_DETECT_TIMEOUT_S
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                # Terminó (publicó o falló) antes de poder congelar.
                return False
            tmp_siblings = []
            if exec_results_dir.is_dir():
                tmp_siblings = [
                    entry for entry in exec_results_dir.iterdir()
                    if entry.name != self.packet_id]
            if tmp_siblings:
                os.kill(proc.pid, signal.SIGSTOP)
                if self.final_dir().is_dir():
                    # Carrera: publicó entre la detección y el STOP; este
                    # intento se descarta (el llamante repite con proyecto
                    # fresco).
                    try:
                        os.kill(proc.pid, signal.SIGCONT)
                    except ProcessLookupError:
                        pass
                    proc.kill()
                    proc.wait()
                    return False
                # Congelado antes de publicar: kill definitivo.
                os.kill(proc.pid, signal.SIGKILL)
                proc.wait()
                return True
            # Detección continua (sin sleep apreciable): la ventana entre
            # la creación del directorio temporal y el rename de
            # publicación es de microsegundos en un filesystem rápido; un
            # sleep de milisegundos la pierde casi siempre.
            time.sleep(0)
        proc.kill()
        proc.wait()
        return False

    def test_r2a_kill_before_publish_retry_completes(self) -> None:
        """R2a: kill del subprocess receive antes del publish → no existe
        resultado final; el retry completa y publica el recibo durable
        (§5: «Interrupción antes de publicar: no existe resultado final; el
        retry puede completar»)."""
        parts = None
        for _ in range(KILL_ATTEMPTS):
            parts, descriptor = self.prepare_receive_fixture()
            if self.kill_receive_before_publish(descriptor):
                break
        else:
            self.fail(
                "R2a: no se logró congelar el receive en el límite "
                "observable antes del publish "
                f"(intentos={KILL_ATTEMPTS}); revisar el límite "
                "observable del §5 (directorio temporal hermano)")

        # Sin resultado final tras el kill (§5).
        self.assertFalse(
            self.final_dir().exists(),
            msg=f"R2a: el kill antes del publish dejó un resultado final "
                f"en {self.final_dir()} (§5: «no existe resultado "
                f"final»)")
        self.assertFalse(
            self.receipt_path().exists(),
            msg="R2a: el kill antes del publish dejó un receipt final")

        # El retry completa: rc=0, receipt durable en stdout byte a byte.
        retry = self.run_receive(descriptor)
        self.assertEqual(
            retry.returncode, 0,
            msg=f"R2a: el retry tras el kill debe completar la "
                f"finalización: rc={retry.returncode} "
                f"stdout={out_text(retry)!r} stderr={err_text(retry)!r}")
        self.assertNotIn(
            "Traceback", err_text(retry),
            msg="R2a: el retry terminó con traceback")
        self.assertTrue(
            self.receipt_path().is_file(),
            msg="R2a: el retry debe publicar receipt.json")
        self.assertEqual(
            retry.stdout, self.receipt_path().read_bytes(),
            msg="R2a: el retry debe devolver en stdout exactamente los "
                "bytes del receipt durable (§2)")
        # Los parts persistidos son los originales (una sola finalización).
        for name, data in parts.items():
            self.assert_part_file_matches(name, data)

    def test_r2b_concurrent_identical_receives_converge(self) -> None:
        """R2b: dos receives concurrentes idénticos → ambos rc=0, un solo
        receipt durable y stdout byte a byte idéntico (§5: «Dos receives
        concurrentes idénticos: uno publica; el otro compara identidad y
        digests y devuelve exactamente el receipt durable existente»)."""
        parts, descriptor = self.prepare_receive_fixture()
        argv = self.receive_args(descriptor)
        procs = [popen_result_cli(argv) for _ in range(2)]
        try:
            results = [proc.communicate(timeout=RECEIVE_TIMEOUT_S)
                       for proc in procs]
        except subprocess.TimeoutExpired:
            for proc in procs:
                proc.kill()
            for proc in procs:
                proc.wait()
            self.fail("R2b: un receive concurrente no terminó a tiempo")
        for i, proc in enumerate(procs):
            self.assertEqual(
                proc.returncode, 0,
                msg=f"R2b: el receive concurrente #{i + 1} debe converger "
                    f"al receipt durable con rc=0: rc={proc.returncode} "
                    f"stdout={results[i][0]!r} stderr={results[i][1]!r}")
        self.assertTrue(
            self.receipt_path().is_file(),
            msg="R2b: debe existir un único receipt durable")
        durable = self.receipt_path().read_bytes()
        self.assertEqual(
            results[0][0], results[1][0],
            msg="R2b: ambos receives concurrentes deben devolver el "
                "mismo stdout byte a byte (§5)")
        self.assertEqual(
            results[0][0], durable,
            msg="R2b: el stdout convergido debe ser exactamente el "
                "receipt durable (§5)")
        # Una sola finalización: los parts siguen siendo los originales.
        for name, data in parts.items():
            self.assert_part_file_matches(name, data)


# ------------------------------------------------------------------- R3


class TestR3ScopeValidationPositive(EstablishedProjectCase):
    """R3 (BLOCKING): scope-validation positivo con cambios in-scope
    nunca ejercitado (§4 paso 6; el write scope del paquete fixture es
    `tests`)."""

    def _receive_with_changes(self, changes: list[dict]):
        self.new_dispatched_project()
        self.write_staged_parts()
        self.write_manifest(changes=changes)
        doc = self.build_descriptor(parts=dict(STAGED_PARTS),
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        return self.run_receive(descriptor)

    def test_r3_trusted_manifest_with_in_scope_change_scope_passed(self) -> None:
        """R3: manifest trusted con un cambio IN-SCOPE (`tests/…`, bajo el
        write scope del paquete) → rc=0 y `scope_validation="passed"`
        (§4: «La comparación demuestra que los paths declarados están
        dentro del scope»)."""
        proc = self._receive_with_changes(
            [{"path": IN_SCOPE_CHANGE, "operation": "modified"}])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R3: un cambio in-scope debe aceptarse: "
                f"rc={proc.returncode} stdout={out_text(proc)!r} "
                f"stderr={err_text(proc)!r}")
        receipt = json.loads(proc.stdout)
        self.assertEqual(
            receipt["scope_validation"], "passed",
            msg=f"R3: scope_validation debe ser `passed` con un cambio "
                f"in-scope (la lógica de scope no puede quedar vacua): "
                f"{receipt.get('scope_validation')!r}")

    def test_r3_renamed_change_with_previous_path_scope_passed(self) -> None:
        """R3: la variante `renamed` con `previous_path` (§4: «rename
        incluye previous_path») también se valida como in-scope → rc=0 y
        `scope_validation="passed"`."""
        proc = self._receive_with_changes(
            [{"path": "tests/renamed_role_report.py",
              "operation": "renamed",
              "previous_path": "tests/previous_role_report.py"}])
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R3: un cambio `renamed` con previous_path in-scope debe "
                f"aceptarse: rc={proc.returncode} "
                f"stdout={out_text(proc)!r} stderr={err_text(proc)!r}")
        receipt = json.loads(proc.stdout)
        self.assertEqual(
            receipt["scope_validation"], "passed",
            msg=f"R3: scope_validation debe ser `passed` para la variante "
                f"renamed/previous_path: "
                f"{receipt.get('scope_validation')!r}")


# ------------------------------------------------------------------- R5


class TestR5ValidateReceipt(EstablishedProjectCase):
    """R5: `validate-receipt` declarado en el alcance T1 sin observables
    (positivo y negativo)."""

    def validate_receipt(self, receipt_path) -> subprocess.CompletedProcess:
        return run_result_cli(["validate-receipt",
                               "--project-root", str(self.root),
                               "--receipt", str(receipt_path)])

    def test_r5_validate_receipt_accepts_valid_durable_receipt(self) -> None:
        """R5 (positivo): un receipt durable íntegro → rc=0 (§2: éxito
        devuelve 0; §5: «Interrupción después de publicar: el retry lee y
        valida el receipt durable»)."""
        self.new_dispatched_project()
        self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=dict(STAGED_PARTS),
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        first = self.run_receive(descriptor)
        self.assertEqual(
            first.returncode, 0,
            msg=f"R5 (precondición): el receive debe publicar el recibo: "
                f"rc={first.returncode} stdout={out_text(first)!r} "
                f"stderr={err_text(first)!r}")

        proc = self.validate_receipt(self.receipt_path())
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R5: validate-receipt debe aceptar el receipt durable "
                f"íntegro (rc=0): rc={proc.returncode} "
                f"stderr={err_text(proc)!r}")
        self.assertNotIn(
            "Traceback", err_text(proc),
            msg="R5: validate-receipt positivo terminó con traceback")

    def test_r5_validate_receipt_rejects_tampered_store_part(self) -> None:
        """R5 (negativo): una part del store mutada tras la publicación →
        rc≠0 con diagnóstico por stderr y sin stdout (§5: «Receipt o
        payload durable incompleto/tampered: error de integridad; no se
        repara silenciosamente desde el input»)."""
        self.new_dispatched_project()
        self.write_staged_parts()
        self.write_manifest(changes=[])
        doc = self.build_descriptor(parts=dict(STAGED_PARTS),
                                    observed=self.observed_changes())
        descriptor = self.write_descriptor(doc)
        first = self.run_receive(descriptor)
        self.assertEqual(
            first.returncode, 0,
            msg=f"R5 (precondición): el receive debe publicar el recibo: "
                f"rc={first.returncode} stdout={out_text(first)!r} "
                f"stderr={err_text(first)!r}")

        stored = self.final_dir() / "parts" / "role-report.utf8"
        self.assertTrue(
            stored.is_file(),
            msg="R5 (precondición): la part durable debe existir (§5)")
        stored.write_bytes(stored.read_bytes() + b"\n")

        proc = self.validate_receipt(self.receipt_path())
        self.assertNotEqual(
            proc.returncode, 0,
            msg="R5: validate-receipt debe rechazar un store tampered "
                "(part mutada tras la publicación)")
        self.assertTrue(
            err_text(proc).strip(),
            msg="R5: el rechazo debe proporcionar diagnóstico por stderr")
        self.assertNotIn(
            "Traceback", err_text(proc),
            msg="R5: el rechazo debe ser un diagnóstico, no un traceback")
        self.assertEqual(
            proc.stdout, b"",
            msg="R5: en rechazo no se emite evidencia parcial por stdout")


if __name__ == "__main__":
    unittest.main(verbosity=2)
