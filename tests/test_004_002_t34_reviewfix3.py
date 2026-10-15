#!/usr/bin/env python3
"""004-002 T3/T4 REVIEW-FIX 3 RED — hallazgos R-1 y R-2 de
docs/specs/004-002-project-execution-bootstrap/review-t34-rf2.md
(disposición del orquestador en su sección final) + plan.md I5d/I8.

Superficie observable: el CLI del productor invocado por argv PURO por
caso (sin helpers que inyecten --role/--substage/--objective); proyectos
sintéticos T2 en tempdirs. Ninguna lectura de implementación
(skills/cdad-cycle/scripts/, scripts/, sources/, install.sh). Fixtures
reutilizados de test_004_002_t34_reviewfix2 (y t2/t3) sin tocar los
archivos existentes.

Mapa test → postcondición (hallazgo):

  R-1  reconcile_plus_input_option_rejected_no_writes
        PD-4/I5d (exclusividad de modos, variante --input): el modo
        `reconcile` admite SOLO --decision-ref; `--input` es una opción
        ordinaria allí, así que `--reconcile-policy <sha>
        --decision-ref <ruta> --input <archivo>` da rc=2 con stdout
        vacío y ninguna escritura (árbol .cdad+docs byte a byte,
        policy_history sin crecer). Control positivo: el mismo argv sin
        --input reconcilia con rc=0.
  R-2  record_retry_completes_pending_transition_after_crash_window
        PD-11/I8 (recuperación B-1): estado de "muerte entre los dos
        renames" — registro de despacho ya publicado en
        .cdad/executions/<eid>/dispatches/<attempt>.json y state con el
        paquete activo todavía `prepared` (siembra por interfaz
        pública: registrar una vez y restaurar los bytes previos del
        state). Un reintento idéntico de --record-dispatch da rc=0,
        deja el paquete `dispatched` y el registro con bytes idénticos.
        Mata la mutación M-B1b (`if already_recorded: return`): la
        mutación sale temprano cuando el registro ya existe y NO
        completa la transición prepared→dispatched, así que el status
        del paquete quedaría `prepared` y la aserción de status falla
        (la de bytes idénticos no basta sola: el registro no se toca).

RED esperado contra el código actual: R-1 falla (hoy el modo
`reconcile` exime a --input y acepta el argv con rc=0); R-2 PASA (la
implementación ya completa la transición; es un test de cobertura de la
garantía nombrada en review-t34-rf2).
"""

from __future__ import annotations

import json
from pathlib import Path

from test_004_002_t2_bootstrap import (
    STATE_FILE,
    read_state,
    tree_snapshot,
)
from test_004_002_t3_durable import history_text
from test_004_002_t34_reviewfix2 import (
    MixedArgvCase,
    RecordCase,
    dispatch_path,
    observation_doc,
    state_bytes,
)


# ---------------------------------------------------------------- R-1


class TestR1ReconcileRejectsInput(MixedArgvCase):
    def test_r1_reconcile_plus_input_rejected_no_writes(self) -> None:
        """R-1 (PD-4/I5d): `--reconcile-policy <sha> --decision-ref <ruta>
        --input <archivo>` da rc=2 con stdout vacío y ninguna escritura
        (árbol de .cdad y docs byte a byte; policy_history sin crecer).
        argv PURO: exactamente esas opciones más --project-root, sin
        helpers que inyecten --role/--substage/--objective. Control
        positivo: el mismo argv sin --input reconcilia con rc=0."""
        _packet_id, sha, decision_ref = self.bootstrap_completed()
        obs = Path(self._tmp) / "obs-r1.json"
        obs.write_text(
            json.dumps({"entrada": "ordinaria del encargo"}),
            encoding="utf-8")
        argv = [
            "prepare", "--project-root", str(self.root),
            "--reconcile-policy", sha, "--decision-ref", decision_ref,
            "--input", str(obs),
        ]
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        history_before = history_text(self.root)

        proc = self.cli(argv)
        self.assertNotIn(
            "unrecognized", proc.stdout + proc.stderr,
            msg="las opciones del argv mixto existen; el rechazo debe ser "
                "de exclusividad de modos (I5d), no getopt")
        self.assertEqual(
            proc.returncode, 2,
            msg=f"--reconcile-policy aceptó la opción ordinaria --input "
                f"y la descartó en silencio (R-1: la exención de --input "
                f"es solo del modo record): rc={proc.returncode} "
                f"{proc.stdout!r} {proc.stderr!r}")
        self.assertEqual(
            proc.stdout, "",
            msg="la invocación mixta rechazada escribió en stdout")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="la invocación mixta escribió el árbol (.cdad o docs) "
                "(R-1: rc≠0 sin escrituras)")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="la invocación mixta cambió el state (R-1)")
        self.assertEqual(
            history_text(self.root), history_before,
            msg="la invocación mixta hizo crecer el historial de política "
                "de la ejecución (policy_history sin crecer, R-1)")

        # Control positivo: el mismo argv SIN --input reconcilia.
        proc_ok = self.cli([
            "prepare", "--project-root", str(self.root),
            "--reconcile-policy", sha, "--decision-ref", decision_ref,
        ])
        self.assertEqual(
            proc_ok.returncode, 0,
            msg=f"control positivo: la reconciliación pura (sin --input) "
                f"debe aceptarse: {proc_ok.stdout!r} {proc_ok.stderr!r}")


# ---------------------------------------------------------------- R-2


class TestR2RetryCompletesPendingTransition(RecordCase):
    def test_r2_retry_after_crash_between_renames_completes_transition(
            self) -> None:
        """R-2 (PD-11/I8, rama de recuperación de B-1): siembra el estado
        de "muerte entre los dos renames" — el registro de despacho ya
        publicado en .cdad/executions/<eid>/dispatches/<attempt>.json
        con los bytes del registro, y el state con el paquete activo
        todavía `prepared` (siembra: registrar una vez y restaurar
        después los bytes previos del state). Un reintento idéntico de
        --record-dispatch debe dar rc=0, dejar el paquete `dispatched` y
        el registro con bytes idénticos.

        Contra M-B1b (`if already_recorded: return`): la mutación sale
        temprano cuando el registro ya existe y NO completa la
        transición prepared→dispatched; el status del paquete quedaría
        `prepared` y la aserción de status falla (con rc=0 del reintento
        temprano)."""
        root = self.root
        eid, pid = self.bootstrap_ready()
        obs = self.write_obs("obs-r2.json", observation_doc())
        argv = self.record_argv(pid, "a-r2", obs)
        state_prepared = state_bytes(root)

        # Siembra: publicar el registro una vez (rc 0, paquete dispatched).
        proc1 = self.cli(argv)
        self.assertEqual(
            proc1.returncode, 0,
            msg=f"precondición (siembra): el primer registro debe "
                f"aceptarse: {proc1.stdout!r} {proc1.stderr!r}")
        record = dispatch_path(root, eid, "a-r2")
        self.assertTrue(
            record.is_file(),
            msg="precondición: el registro de despacho no quedó publicado")
        record_bytes = record.read_bytes()

        # Estado de muerte entre renames: el registro queda publicado y
        # el state vuelve a sus bytes previos (paquete `prepared`).
        (root / STATE_FILE).write_bytes(state_prepared)
        self.assertEqual(
            read_state(root)["active_packet"]["status"], "prepared",
            msg="precondición: el state sembrado no dejó el paquete "
                "en prepared")
        self.assertEqual(
            record.read_bytes(), record_bytes,
            msg="precondición: el registro publicado se alteró al sembrar")

        # Reintento idéntico (mismo argv, mismo documento).
        proc2 = self.cli(argv)
        self.assertEqual(
            proc2.returncode, 0,
            msg=f"el reintento idéntico debe completar la transición "
                f"pendiente (R-2/B-1): {proc2.stdout!r} {proc2.stderr!r}")
        self.assertEqual(
            read_state(root)["active_packet"]["status"], "dispatched",
            msg="el reintento idéntico no dejó el paquete en dispatched "
                "(R-2: mata M-B1b `if already_recorded: return`, que "
                "sale temprano sin completar prepared→dispatched)")
        self.assertEqual(
            record.read_bytes(), record_bytes,
            msg="el reintento alteró los bytes del registro ya publicado "
                "(I8: repetir un registro idéntico es idempotente, "
                "bytes iguales)")


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
