#!/usr/bin/env python3
"""005-009 T4 RED — Aceptación determinista: ENTREGA ≠ GATE e
interrupción/recuperación (PD-6 segunda mitad); PD-10 DECLARADO como gate de
integración (no simulado).

Contract: docs/specs/005-009-cli-delegation/spec.md (PD-6; PD-10) +
plan.md T4 (tests/test_005_009_t4_acceptance.py, checks deterministas; el
recorrido real es el integration_gate del orquestador + dueño) +
discovery.md §8 (mecanismo de reconciliación: `_classify` distingue
`dispatched-unknown` (no fallo) de éxito; `reconcile` es read-only y no
repite efecto).

FRONTERA DECLARADA — PD-10 (el RECORRIDO REAL NO se simula):
el recorrido REAL "Claude (coordinador) → OpenCode (worker de rol) →
recepción CDAD desde la instalación elegida" NO se simula aquí: es el
GATE DE INTEGRACIÓN/ACEPTACIÓN que corre el ORQUESTADOR CON EL DUEÑO y se
registra como EVIDENCIA (I8 + recibo durable + re-entry del coordinador;
plan T4 `integration_gate`; spec §2 «aceptación», §8 VERIFY-8). Una prueba
que solo llama al script desde un shell NO demuestra por sí sola la
orquestación desde Claude. Este módulo la declara y la OMITE con skip
limpio y mensaje explícito (T4 es determinista y agnóstico de entorno; sin
instalación aislada real disponible, no se fabrica un verde).

Superficie observable reutilizada POR IMPORT (cero reimplementación,
ninguna lectura de implementación skills/**): la fixture de T2
(TestAdapterCwdIndependent precedent — `AdapterCase`, binario OpenCode
falso con variantes de hecho material) y las utilidades de T1
(`dispatch_records`, forma cerrada I8) + el bytestate del mecanismo
reutilizado (`tree_snapshot` de 004-002). La reconciliación se ejercita
por la CLI de producto ya existente y ORÁCULO INDEPENDIENTE del transporte
`cdad_continuity.py reconcile --project-root <root> --execution-context
<execution.json publicado> --packet <id> --json` (discovery §8.6).

Mapa test → postcondición:

  1  TestPd6DeliveryIsNotGate::test_pd6_completed_delivery_receipt_pending_…   PD-6 (entrega ≠ gate)
  2  TestPd6InterruptionRecovery::test_pd6_timeout_effects_reconciled_…        PD-6 (interrupción/recuperación)
  3  TestPd10RealPathIsOwnerIntegrationGate::test_pd10_real_path_…             PD-10 — SKIP DECLARADO

RED (por qué es RED y por qué es honesto): T4 no agrega producto
(plan: «GREEN es de T1/T2; aquí no hay producto nuevo»). Su RED es el
oráculo de borde: CADA unidad determinista fallaría por AssertionError de
comportamiento en su PUERTA declarada si el comportamiento esperado
estuviera ausente/roto — (1) un recibo que NO queda `pending`, un state
cerrado por la propia delegación o un re-entry que se contradice; (2) un
`timeout` que niega los hechos materiales o un `reconcile` que autoriza
repetir (repeat_effect ≠ false), los declara éxito/fallo, borra hechos o
fabrica recibo; (3) el skip de PD-10 queda REGISTRADO en la corrida como
frontera declarada (no verde fabricado). Si T1/T2 están en GREEN, los
checks deterministas pasan: la aceptación T4 se satisface y el pasaje es
evidencia de aceptación, no una repetición del RED de producto.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot
from test_005_009_t1_interface import I8_RECORD_KEYS, dispatch_records
from test_005_009_t2_opencode_adapter import (
    AdapterCase,
    durable_session_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"

TERMINATION_DONE = "completed"
TERMINATION_TIMEOUT = "timeout"
RECEIVED = "received"
DISPATCHED_UNKNOWN = "dispatched-unknown"


class AcceptanceCase(AdapterCase):
    """Base de aceptación: hereda la fixture COMPLETA de T2 (proyecto
    sintético + agentes derivados publicados `mode: all` + adaptador
    OpenCode + binario falso). `SEED_MODE = "all"`: la entry soportada
    despacha — la interrupción simulada es material (sobre un intento REAL
    del adaptador), no un store sembrado a mano."""

    SEED_MODE = "all"

    # -- re-entry del responsable (flujo EXISTENTE, oráculo independiente) --

    def run_reconcile(self) -> dict:
        """El responsable del ciclo reconcilia ANTES de repetir:
        `cdad_continuity.py reconcile` sobre el proyecto sintético con el
        execution-context publicado por el mecanismo real (discovery §8.6).
        El envelope debe ser del esquema conocido (`reconcile-v1`) con la
        clasificación justificada; cada unidad aserte luego sobre qué
        clasificación espera y lo que NUNCA puede hacer."""
        exec_context = (
            self.root / ".cdad" / "executions" / self.execution_id
            / "execution.json")
        self.assertTrue(
            exec_context.is_file(),
            msg="precondición (fixture): el mecanismo real no publicó el "
                "execution-context del ciclo "
                f"({exec_context.relative_to(self.root)})")
        proc = subprocess.run(
            [sys.executable, str(CONTINUITY_SCRIPT),
             "reconcile",
             "--project-root", str(self.root),
             "--execution-context", str(exec_context),
             "--packet", self.packet_id,
             "--json"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
            timeout=300, stdin=subprocess.DEVNULL)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"reconcile (re-entry del responsable) terminó con error: "
                f"{(proc.stdout + proc.stderr)[:600]}")
        try:
            env = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(
                msg=f"reconcile no emitió su envelope JSON en stdout: "
                    f"{proc.stdout[:400]!r}")
        self.assertEqual(
            env.get("reconcile"), "reconcile-v1",
            msg=f"el envelope de reconcile no es del esquema conocido "
                f"`reconcile-v1`: {env!r}")
        reasons = env.get("reasons")
        self.assertIsInstance(
            reasons, list,
            msg=f"la clasificación viaja sin justificación (`reasons` no es "
                f"lista): {reasons!r}")
        self.assertTrue(
            reasons, msg="`reasons` vacío: la clasificación está sin "
                         "justificar")
        return env


# ------------------------------------------------------------------ PD-6


class TestPd6DeliveryIsNotGate(AcceptanceCase):
    """PD-6 segunda mitad — ENTREGA ≠ GATE: una delegación que termina
    `completed` deja el recibo durable en `semantic_status:"pending"`; el
    rc=0 del cliente (y de esta misma corrida) NO aprueba un gate; el
    responsable del ciclo decide en el re-entry (reconcile → la entrega
    recibida es `received` y repetirla NO está autorizada; el recibo jamás
    es aprobación semántica); el
    state del ciclo NO cambia por la delegación."""

    def test_pd6_completed_delivery_receipt_pending_state_untouched_reentry_received(self) -> None:
        """PD-6/INV-5: la delegación completa (`completed` desde la señal
        durable del binario falso) declara su entrega durable pero el GATE
        sigue ABIERTO — el recibo queda `pending`; el state del ciclo no
        cambia por la delegación (sin cierres; único escritor el
        orquestador); el re-entry del responsable (reconcile)
        clasifica la entrega como `received` (ya efecto material: NO se
        repite, `repeat_effect` false) y el recibo sigue `pending` (no es
        aprobación semántica): aprobar el gate lo decide el responsable."""
        fake = self.fake_runtime("pd6-gate", variant="succeeded")
        out = self.envelope(self.run_opencode(fake), "PD-6 entrega ≠ gate")

        # La delegación SÍ terminó `completed` (hecho material: señal
        # durable): rc=0 y terminación declarada... y PERO ninguna de esas
        # dos cosas es aprobación de gate — el recibo lo acredita abajo.
        self.assertEqual(
            out["termination"], TERMINATION_DONE,
            msg=f"precondición del caso: la delegación no terminó "
                f"completed (señal durable presente): {out['termination']!r}")
        self.assert_durable_delivery_ref(out)

        # ENTREGA ≠ GATE: el recibo durable queda `semantic_status:"pending"`
        # (rc=0/entregada NO aprueba el gate; cdad_result.py:574).
        self.assert_receipt_no_gate()

        # El state del ciclo NO cambia por la delegación: ni status
        # completed/failed, ni ningún campo fuera de la frontera del
        # mecanismo reutilizado (INV-1: único escritor el orquestador).
        state_before = json.loads(self.state_before_bytes.decode("utf-8"))
        self.assert_state_untouched_beyond_dispatch_frontier(state_before)

        # Re-entry del responsable: reconcile clasifica la entrega como
        # `received` (ha habido efecto material) y NO ofrece repetirla.
        env = self.run_reconcile()
        self.assertEqual(
            env.get("classification"), RECEIVED,
            msg=f"la entrega ya recibida no se clasificó `received` "
                f"(entrega durable pero no duplicable): "
                f"{env.get('classification')!r}")
        self.assertIs(
            env.get("repeat_effect"), False,
            msg=f"reconcile con recibo presente ofrece repetir el efecto "
                f"(repeat_effect): {env.get('repeat_effect')!r}")
        # El recibo sigue `pending` tras el re-entry: NADIE aprobó el gate
        # por el mero hecho de recibir la entrega (decisión del dueño).
        self.assert_receipt_no_gate()
        self.assert_state_untouched_beyond_dispatch_frontier(state_before)


# ------------------------------------------------------------------ PD-6


class TestPd6InterruptionRecovery(AcceptanceCase):
    """PD-6 segunda mitad — INTERRUPCIÓN/RECUPERACIÓN: tras un intento
    interrumpido, los efectos se RECONCILIAN antes de repetir: la
    reconciliación clasifica el intento EN VUELO como `dispatched-unknown`
    (no fallo, distinto de éxito `received`) y NO autoriza repetir ni
    fabrica entrega; el timeout NO prueba ausencia de cambios: los hechos
    materiales del intento (intento I8 en el ledger, bytes transportados)
    quedan en el proyecto."""

    def test_pd6_timeout_effects_reconciled_before_repeating_no_delivery_fabricated(self) -> None:
        """PD-6: un intento que nunca recibe la señal durable (el cliente
        retorna rc=0 e imprime texto por stdout, pero NO hay señal) termina
        `timeout` SIN entrega durable fabricada; el timeout NO niega los
        efectos materiales (el intento queda en el ledger I8 y los bytes
        transportados persisten); la reconciliación del responsable ANTES
        de repetir clasifica `dispatched-unknown` — el intento EN VUELO no
        es un fallo y no se clasifica como éxito (`received`) — con
        `repeat_effect` false (la repetición NO está autorizada por el
        clasificador: la decide el responsable con las facts), read-only
        byte a byte y sin fabricar recibo."""
        # Interrupción simulada CON INTENTO REAL: variante no-idle del
        # binario falso (el cliente retorna rc=0, el texto final por
        # stdout, pero la señal durable nunca aparece).
        fake = self.fake_runtime("pd6-interru", variant="no-idle")
        records_before = dispatch_records(self.root, self.execution_id)
        out = self.envelope(self.run_opencode(fake), "PD-6 interrupción")

        self.assertEqual(
            out["termination"], TERMINATION_TIMEOUT,
            msg=f"el intento interrumpido (sin señal durable) no terminó "
                f"timeout — una espera que otra cosa declare: "
                f"{out['termination']!r}")
        self.assertNotEqual(
            out["termination"], TERMINATION_DONE,
            msg="rc=0 del cliente + texto por stdout produjeron una "
                "entrega declarada (ni entrega ni señal durable hubo)")
        # La interrupción jamás fabrica entrega.
        self.assert_no_receipt_fabricated("timeout (interrupción)")

        # TIMEOUT ≠ AUSENCIA DE CAMBIOS: los hechos materiales del intento
        # quedan — el intento en el MISMO ledger I8 (forma cerrada, del
        # paquete) y los bytes transportados al worker.
        record = self.assert_attempt_is_in_ledger(out, records_before)
        data = json.loads(record.read_bytes().decode("utf-8"))
        self.assertEqual(
            set(data), I8_RECORD_KEYS,
            msg=f"el intento del ledger no tiene la forma cerrada I8: "
                f"{sorted(data)}")
        self.assertEqual(
            data["packet_id"], self.packet_id,
            msg="el intento en el ledger no corresponde al paquete "
                "despachado")
        self.assertTrue(
            fake["sent"].is_file(),
            msg="los hechos materiales del intento no quedaron: el paquete "
                "transportado (bytes al worker) no persiste")
        call = self.packet_call(fake, "hechos materiales del timeout")
        self.assertEqual(
            call.get("rc"), 0,
            msg="fixture: el cliente no retornó rc=0 (el rc del cliente no "
                "prueba ni entrega ni ausencia: es solo un hecho)")
        self.assertTrue(
            call.get("emitted_final_text") is True,
            msg="fixture: el texto final no fue emitido por stdout (hecho "
                "material: stdout ≠ señal durable ≠ entrega, PD-5)")
        self.assertEqual(
            [row.get("idle_outcome")
             for row in durable_session_rows(fake["sessions_db"])],
            [None],
            msg="fixture: la variante no-idle escribió idle en el "
                "store SQLite (precondición del caso rota)")

        # RECONCILIAR antes de repetir: la clasificación del intento EN
        # VUELO es `dispatched-unknown` (no fallo; distinto de éxito).
        project_before = tree_snapshot(self.root)
        env = self.run_reconcile()
        self.assertEqual(
            env.get("classification"), DISPATCHED_UNKNOWN,
            msg=f"la reconciliación no distingue el intento en vuelo "
                f"(`dispatched-unknown`): {env.get('classification')!r}")
        self.assertNotEqual(
            env.get("classification"), RECEIVED,
            msg=f"la interrupción se clasificó como ÉXITO "
                f"(`received`); el caso en vuelo no es recibido ni fallo")
        # NO autoriza repetir (ni fabrica entrega): repetir lo decide el
        # responsable con las facts; el clasificador jamás lo ofrece.
        self.assertIs(
            env.get("repeat_effect"), False,
            msg=f"reconcile autoriza repetir el efecto tras la "
                f"interrupción (repeat_effect): "
                f"{env.get('repeat_effect')!r}")
        # Read-only (invariante 1): byte a byte; los hechos del intento
        # NO se borraron por la interrupción ni por la reconciliación.
        self.assertEqual(
            tree_snapshot(self.root), project_before,
            msg="reconcile NO es read-only (invariante 1): el proyecto "
                "cambió al clasificar el intento en vuelo")
        self.assert_no_receipt_fabricated("tras reconcile (interrupción)")
        self.assertTrue(
            record.is_file(),
            msg="la reconciliación borró los hechos materiales del intento "
                "(ledger I8)")


# ------------------------------------------------------------------ PD-10


class TestPd10RealPathIsOwnerIntegrationGate(unittest.TestCase):
    """PD-10 — FRONTERA DECLARADA del módulo: el recorrido real Claude →
    OpenCode → recepción CDAD desde la instalación elegida NO se simula
    aquí; es el gate de integración/aceptación del orquestador + dueño."""

    def test_pd10_real_path_claude_to_opencode_reception_is_owner_gate(self) -> None:
        """PD-10: SKIP DECLARADO (plan T4 — gate de integración real, no
        unitario: «lo corre el orquestador con el dueño y se registra como
        evidencia»; «una prueba que solo llama al script desde un shell no
        demuestra por sí sola la orquestación desde Claude»). Las partes
        DETERMINISTAS y verificables de PD-10 a caja negra — la interfaz
        (T1), el adaptador con binario falso (T2), la entrega durable por
        `receive` y el re-entry por `reconcile`/`resume` — están cubiertas
        en T1/T2 y en las unidades 1 y 2 de ESTE módulo; el RESTO del
        recorrido real (una sesión de Claude coordinador REAL despachando a
        un worker OpenCode REAL sobre una instalación elegida para la
        aceptación, y el re-entry del coordinador) no es determinista ni
        simulable en esta prueba: NO se fabrica un verde, se omite con
        mensaje explícito y queda declarada como evidencia del gate."""
        self.skipTest(
            "PD-10 (gate de integración, no simulado): el recorrido real "
            "Claude → OpenCode → recepción CDAD desde la instalación "
            "elegida lo corre el ORQUESTADOR CON EL DUEÑO y se registra "
            "como evidencia (I8 + recibo durable + re-entry del "
            "coordinador; plan T4 integration_gate, spec PD-10 §2/§8 "
            "VERIFY-8). Este módulo no construye una instalación aislada "
            "ni ejecuta sesiones reales de CLI; una prueba que solo llama "
            "al script desde un shell no demuestra por sí sola la "
            "orquestación desde Claude — no se fabrica verde.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
