#!/usr/bin/env python3
"""003-003 T3 RED — presupuesto durable + eventos (P4).

Contract:
- docs/specs/003-003-progress-guards/spec.md (P4; D3; D4; D7; invariantes
  1, 5, 11)
- docs/specs/003-003-progress-guards/plan.md (T3; test focal declarado
  `tests/test_003_003_t3_budget.py`; escritura SOLO bajo
  `.cdad/executions/<id>/guards/**`, nunca `docs/.cdad-state.json`).

Superficie observable bajo prueba (V7: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_guard.py record \
        --project-root ROOT \
        --event EVENT.json

    python3 scripts/cdad_guard.py budget \
        --project-root ROOT \
        --execution-context EXEC.json \
        --packet PACKET_ID

Envolventes de salida (JSON en stdout, contratos fijados en RED; los
schemas de evento/presupuesto quedan así declarados, §V7):

record (`record-v1`):

    {
      "schema_version": 1,
      "record": "record-v1",
      "event": {…guard-event-v1…},
      "durable": ".cdad/executions/<execution_id>/guards/…",
      "reconciled": <bool>,
      "receipt_ref": <str|null>,
      "do_not_repeat": <bool>
    }

budget (`budget-v1`):

    {
      "schema_version": 1,
      "budget": "budget-v1",
      "execution_id": "…",
      "packet_id": "…",
      "attempts": [{"attempt": 1, "cause": "…", "session": "…",
                    "at": "…"}],
      "consumed": <n>,
      "exhausted": <bool>,
      "reconsider": <bool>
    }

Semántica fijada por este RED:

- P4: cada recuperación (evento `recovery-attempt`) consume presupuesto
  durable y produce receipt/evento; el evento persiste bajo
  `.cdad/executions/<execution_id>/guards/**` (D4), keyed por
  `execution_id+packet_id+attempt`.
- P4 (reanudación): un restart o una sesión nueva NO reinicia el
  presupuesto; reanudar conserva intentos y causas anteriores
  (invariante 11).
- P4/D3: un límite de intentos es SEÑAL PARA RECONSIDERAR (escala), no
  prueba de incumplimiento — `reconsider: true`, rc 0 (sin auto-bloqueo
  duro nuevo).
- D7: antes de repetir, el guard consulta el receipt/journal de 002 bajo
  `.cdad/runtime/results/<execution_id>/<packet_id>/`; si la acción ya
  terminó, `do_not_repeat: true` y `receipt_ref` citan el receipt. El
  guard solo SEÑALA; no repite efectos ni redefinir 002 (invariante 5).
- Invariante 1/D4: `record` escribe SOLO bajo `.cdad/executions/<id>/guards/`
  (nunca `docs/.cdad-state.json`, single-writer = orquestador); `budget`
  es read-only y determinista.

Fixtures: proyecto sintético en tmp con execution context PROPIO (nota
del orquestador: proyecto tmp propio). Los eventos de recuperación son
simulación sobre fixtures deterministas: no se provoca ningún incidente
real (P6, plan.md:173-176). La validación del schema de evento es
estructural aquí (la envolvente fijada arriba ES el schema en RED; el
activo `skills/cdad-cycle/assets/guard-event.schema.json` se valida en
GREEN contra esta forma).

RED hoy: los subcomandos `record`/`budget` no existen aún en
`scripts/cdad_guard.py`; cada aserción positiva fracasa por
comportamiento ausente (AssertionError con el mensaje `el comando no
existe aún`), nunca por ImportError ni sintaxis — el test no importa el
módulo del guard.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import tree_snapshot

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # wrapper (T1)

FEATURE_ID = "003-003-progress-guards"

EXEC_ID = "exec-003-003-t3-red-001"
PACKET_ID = "003-003-progress-guards-implementer-green-001"
PACKET_ID_B = "003-003-progress-guards-implementer-green-002"

# Tope duro: un guard determinista nunca puede colgarse (acotado).
GUARD_TIMEOUT_S = 120

# Ruta durable del presupuesto (D4, plan T3).
GUARDS_DIR_REL = f".cdad/executions/{EXEC_ID}/guards"
RESULTS_DIR_REL = f".cdad/runtime/results/{EXEC_ID}/{PACKET_ID}"

# Límite declarado para el caso D3 (señal para reconsiderar).
MAX_ATTEMPTS = 2


# ---------------------------------------------------------------- fixtures


def guard_event(*, execution_id: str = EXEC_ID, packet_id: str = PACKET_ID,
                attempt: int = 1, kind: str = "recovery-attempt",
                cause: str = "session-died-without-result",
                session: str = "sess-A",
                action: str = "resume-same-session",
                at: str = "2026-10-06T00:00:00Z") -> dict:
    """Evento `guard-event-v1` (fixture determinista)."""
    return {
        "schema_version": 1,
        "event": "guard-event-v1",
        "execution_id": execution_id,
        "packet_id": packet_id,
        "attempt": attempt,
        "kind": kind,
        "cause": cause,
        "session": session,
        "action": action,
        "at": at,
    }


def exec_context_fixture(**extra: object) -> dict:
    """Execution context mínimo (001): el budget se keyea por execution_id."""
    doc = {
        "schema_version": 1,
        "execution_id": EXEC_ID,
        "runtime": "opencode",
    }
    doc.update(extra)
    return doc


def receipt_002_fixture(packet_id: str = PACKET_ID) -> dict:
    """Receipt de 002 (invariante 5: se REUTILIZA, no se redefine):
    presencia bajo `.cdad/runtime/results/<execution_id>/<packet_id>/`
    con `semantic_status` siempre `pending` (003-002 closure)."""
    return {
        "schema_version": 1,
        "packet_id": packet_id,
        "semantic_status": "pending",
        "received_at": "2026-10-06T00:05:00Z",
    }


# ---------------------------------------------------------------- helpers


class GuardProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con execution context propio."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t3-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.root / "fixture" / "exec.json"
        self.exec_context.parent.mkdir(parents=True, exist_ok=True)
        self.write_exec_context()

    def write_exec_context(self, **extra: object) -> Path:
        doc = exec_context_fixture(**extra)
        self.exec_context.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return self.exec_context

    def write_event(self, **overrides: object) -> tuple[Path, dict]:
        """Escribe el evento fixture y devuelve (path, evento)."""
        event = guard_event(**overrides)  # type: ignore[arg-type]
        path = self.root / "fixture" / "event.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path, event

    def run_record(self, event_path: Path) -> subprocess.CompletedProcess:
        """Corrida del CLI record (V7) con tope de tiempo."""
        try:
            return subprocess.run(
                [sys.executable, str(GUARD_SCRIPT), "record",
                 "--project-root", str(self.root),
                 "--event", str(event_path)],
                cwd=REPO_ROOT, capture_output=True, timeout=GUARD_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P4 (acotado): `record` no terminó dentro de "
                f"{GUARD_TIMEOUT_S}s — un registro determinista nunca "
                f"puede colgarse; got timeout={exc!r}")

    def run_budget(self, packet_id: str = PACKET_ID,
                   ) -> subprocess.CompletedProcess:
        """Corrida del CLI budget (V7) con tope de tiempo."""
        try:
            return subprocess.run(
                [sys.executable, str(GUARD_SCRIPT), "budget",
                 "--project-root", str(self.root),
                 "--execution-context", str(self.exec_context),
                 "--packet", packet_id],
                cwd=REPO_ROOT, capture_output=True, timeout=GUARD_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P4 (acotado): `budget` no terminó dentro de "
                f"{GUARD_TIMEOUT_S}s — un reporte read-only determinista "
                f"nunca puede colgarse; got timeout={exc!r}")

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser el comportamiento ausente, con mensaje
        explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        combined = out + err
        self.assertNotIn(
            "invalid choice", combined,
            msg=f"P4: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_guard.py " + which +
                " --project-root` declarado en §3 (V7) es obligatorio")
        self.assertNotIn(
            "unrecognized", combined,
            msg=f"P4: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv declarado en §3 (V7) es obligatorio")
        self.assertNotIn(
            "Traceback", err,
            msg=f"P4: `{which}` no puede terminar con traceback; "
                f"stderr={err!r}")

    def record_envelope(self, proc: subprocess.CompletedProcess) -> dict:
        """record → (rc 0, sin traceback, stdout JSON parseable)."""
        self.assert_command_exists(proc, "record")
        self.assertEqual(
            proc.returncode, 0,
            msg="P4: `record` debe registrar la recuperación con éxito "
                f"(rc 0); el comando no existe aún o falló (RED): "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        raw = proc.stdout.decode("utf-8", errors="replace").strip()
        self.assertTrue(
            raw,
            msg="P4: `record` debe emitir su receipt/evento en stdout; "
                "stdout vacío")
        env = json.loads(raw)
        self.assertEqual(
            env.get("record"), "record-v1",
            msg="P4: la envolvente de record debe declarar el contrato "
                f"record-v1; got={env.get('record')!r}")
        self.assertEqual(
            env.get("schema_version"), 1,
            msg="P4: la envolvente record-v1 debe declarar "
                "schema_version=1")
        return env

    def budget_envelope(self, proc: subprocess.CompletedProcess) -> dict:
        """budget → (rc 0, sin traceback, stdout JSON parseable)."""
        self.assert_command_exists(proc, "budget")
        self.assertEqual(
            proc.returncode, 0,
            msg="P4: `budget` debe reportar el presupuesto durable con "
                f"éxito (rc 0); el comando no existe aún o falló (RED): "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        raw = proc.stdout.decode("utf-8", errors="replace").strip()
        self.assertTrue(
            raw,
            msg="P4: `budget` debe emitir la envolvente budget-v1 en "
                "stdout; stdout vacío")
        env = json.loads(raw)
        self.assertEqual(
            env.get("budget"), "budget-v1",
            msg="P4: la envolvente de budget debe declarar el contrato "
                f"budget-v1; got={env.get('budget')!r}")
        self.assertEqual(
            env.get("schema_version"), 1,
            msg="P4: la envolvente budget-v1 debe declarar "
                "schema_version=1")
        return env


# ---------------------------------------------------------------- tests


class TestP4DurableBudgetConsumption(GuardProjectCase):
    """P4 — cada recuperación consume presupuesto durable y produce
    receipt/evento."""

    def test_p04_recuperacion_consume_y_emite_evento_durable(self) -> None:
        """P4: registrar una recuperación → evento persistido bajo
        `.cdad/executions/<execution_id>/guards/**` (D4) y visible en el
        presupuesto: `consumed == 1`, el intento con su causa."""
        event_path, event = self.write_event()

        proc = self.run_record(event_path)
        env = self.record_envelope(proc)

        # El evento se devuelve íntegro (trazabilidad del receipt/evento).
        self.assertEqual(
            env.get("event"), event,
            msg="P4: el receipt de record debe devolver el evento "
                "guard-event-v1 registrado, íntegro")

        # Persistencia durable bajo .cdad/executions/<id>/guards/ (D4).
        durable = env.get("durable")
        self.assertIsInstance(
            durable, str,
            msg="P4: el receipt debe declarar la ruta durable del evento")
        self.assertIn(
            ".cdad/executions/", durable,
            msg="P4 (D4): el presupuesto durable vive bajo "
                "`.cdad/executions/…`, no en otro árbol")
        self.assertIn(
            "guards/", durable,
            msg="P4 (D4): la persistencia del evento es bajo "
                "`.cdad/executions/<id>/guards/`")
        guards_dir = self.root / ".cdad" / "executions" / EXEC_ID / "guards"
        self.assertTrue(
            guards_dir.is_dir() and any(guards_dir.iterdir()),
            msg="P4 (D4): el evento debe estar persistido de forma durable "
                f"bajo {GUARDS_DIR_REL}/; el directorio no existe o está "
                "vacío")
        durable_hits = [
            p for p in sorted(guards_dir.rglob("*")) if p.is_file()
            and "session-died-without-result" in p.read_text(
                encoding="utf-8", errors="replace")
            and '"attempt": 1' in p.read_text(encoding="utf-8",
                                              errors="replace")
        ]
        self.assertTrue(
            durable_hits,
            msg="P4 (D4): el contenido del evento (attempt=1 y su causa) "
                "debe estar persistido durablmente bajo guards/ — la "
                "persistencia no puede ser efímera")

        # El presupuesto refleja el consumo.
        # Snapshot ANTES de budget y DESPUÉS de record: así la aserción
        # final aísla SOLO la corrida de budget (record ya escribió sus
        # durables bajo guards/ — no se le atribuyen a budget).
        before = tree_snapshot(self.root)
        benv = self.budget_envelope(self.run_budget())
        self.assertEqual(
            benv.get("execution_id"), EXEC_ID,
            msg="P4 (D4): el presupuesto está keyed por execution_id")
        self.assertEqual(
            benv.get("packet_id"), PACKET_ID,
            msg="P4 (D4): el presupuesto está keyed por packet_id")
        self.assertEqual(
            benv.get("consumed"), 1,
            msg="P4: cada recuperación consume presupuesto — una "
                f"recuperación registrada ⇒ consumed=1; "
                f"got={benv.get('consumed')!r}")
        attempts = benv.get("attempts")
        self.assertIsInstance(
            attempts, list,
            msg="P4: el presupuesto debe listar los intentos consumidos "
                "con sus causas (reanudar conserva intentos y causas)")
        self.assertEqual(
            len(attempts), 1,
            msg=f"P4: un intento registrado ⇒ un intento listado; "
                f"got={attempts!r}")
        self.assertEqual(
            attempts[0].get("cause"), event["cause"],
            msg="P4 (invariante 11): la CAUSA del intento debe conservarse "
                "en el presupuesto durable")
        self.assertEqual(
            attempts[0].get("session"), event["session"],
            msg="P4 (invariante 11): la sesión del intento debe "
                "conservarse en el presupuesto durable")
        self.assertIs(
            benv.get("exhausted"), False,
            msg="P4: con presupuesto por debajo del límite, "
                "exhausted debe ser False (sin falsos agotamientos)")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P4 (invariante 1): `budget` es read-only — el árbol del "
                "proyecto no debe alterarse al consultarlo")


class TestP4ResumePreservesAttemptsAndCauses(GuardProjectCase):
    """P4 + invariante 11 — reanudar/restart/sesión nueva NO reinicia el
    presupuesto: intentos y causas anteriores se conservan."""

    def test_p04_reanudar_conserva_intentos_y_causas(self) -> None:
        """P4: intento 1 (sess-A, causa C1) + restart simulado como
        sesión NUEVA (sess-B, causa C2, mismo execution+packet) → el
        presupuesto acumula 2 intentos y conserva AMBAS causas; la sesión
        nueva no resetea (D4: keyed por execution_id+packet_id+attempt)."""
        ev1_path, ev1 = self.write_event(
            attempt=1, cause="session-died-without-result", session="sess-A")
        self.record_envelope(self.run_record(ev1_path))

        # Restart / sesión nueva: nuevo proceso del guard, nueva sesión,
        # mismo execution_id+packet_id.
        ev2_path, ev2 = self.write_event(
            attempt=2, cause="repetition-without-new-info", session="sess-B")
        self.record_envelope(self.run_record(ev2_path))

        benv = self.budget_envelope(self.run_budget())
        self.assertEqual(
            benv.get("consumed"), 2,
            msg="P4 (invariante 11): reanudar NO reinicia el presupuesto — "
                "dos recuperaciones acumuladas ⇒ consumed=2; "
                f"got={benv.get('consumed')!r}")
        attempts = benv.get("attempts")
        self.assertIsInstance(attempts, list, msg="P4: lista de intentos")
        self.assertEqual(
            len(attempts), 2,
            msg="P4 (invariante 11): los DOS intentos (el anterior y el de "
                f"la sesión nueva) deben conservarse; got={attempts!r}")
        by_attempt = {a.get("attempt"): a for a in attempts}
        self.assertEqual(
            {1, 2}, set(by_attempt),
            msg="P4 (invariante 11): los intentos conservados son 1 y 2")
        self.assertEqual(
            by_attempt.get(1, {}).get("cause"),
            ev1["cause"],
            msg="P4 (invariante 11): la causa del intento ANTERIOR debe "
                "sobrevivir al restart/sesión nueva")
        self.assertEqual(
            by_attempt.get(2, {}).get("cause"),
            ev2["cause"],
            msg="P4 (invariante 11): la causa del intento nuevo debe "
                "registrarse junto a la anterior (reanudar conserva "
                "intentos y causas)")
        self.assertEqual(
            by_attempt.get(1, {}).get("session"), "sess-A",
            msg="P4 (invariante 11): la sesión del intento anterior se "
                "conserva (la sesión nueva no la borra)")

        # D4 (keying por packet): un paquete DISTINTO del mismo execution
        # tiene presupuesto propio — no comparte ni hereda contadores.
        evb_path, _ = self.write_event(
            packet_id=PACKET_ID_B, attempt=1,
            cause="poll-deadline-reached", session="sess-B")
        self.record_envelope(self.run_record(evb_path))
        benv_b = self.budget_envelope(self.run_budget(packet_id=PACKET_ID_B))
        self.assertEqual(
            benv_b.get("consumed"), 1,
            msg="P4 (D4): el presupuesto es keyed por "
                "execution_id+packet_id — un paquete distinto arranca con "
                "SU propio contador, sin heredar el del paquete A")
        benv_a = self.budget_envelope(self.run_budget())
        self.assertEqual(
            benv_a.get("consumed"), 2,
            msg="P4 (D4): consultar el paquete B no altera el contador "
                "durable del paquete A")

        # Invariante 1: budget es determinista y read-only.
        before = tree_snapshot(self.root)
        proc2 = self.run_budget()
        self.assertEqual(
            proc2.stdout, self.run_budget().stdout,
            msg="P4 (invariante 1): budget es determinista — dos corridas "
                "producen salida idéntica")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P4 (invariante 1): budget es read-only")


class TestP4WritesOnlyUnderGuards(GuardProjectCase):
    """P4 + D4 + invariante 1 — `record` escribe SOLO bajo
    `.cdad/executions/<id>/guards/**`; NUNCA `docs/.cdad-state.json`
    (single-writer = orquestador)."""

    def test_p04_escritura_solo_bajo_guards_y_state_intacto(self) -> None:
        """D4: tras registrar, TODO path nuevo/modificado del proyecto
        vive bajo `.cdad/executions/<execution_id>/guards/`; el state del
        orquestador queda byte a byte idéntico."""
        state_path = self.root / "docs" / ".cdad-state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps({"active_packet": {"status": "dispatched"}},
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        state_before = state_path.read_bytes()

        event_path, _ = self.write_event()
        # Snapshot DESPUÉS de los fixtures propios (event.json) y ANTES
        # de record: todo cambio restante se atribuye solo al guard — el
        # fixture no se le cuelga al guard como escritura suya.
        before = tree_snapshot(self.root)
        self.record_envelope(self.run_record(event_path))
        self.budget_envelope(self.run_budget())

        self.assertEqual(
            state_path.read_bytes(), state_before,
            msg="P4/D4: el guard NUNCA escribe docs/.cdad-state.json "
                "(single-writer = orquestador) — debe quedar idéntico "
                "byte a byte")

        after = tree_snapshot(self.root)
        changed = {p for p in set(before) | set(after)
                   if before.get(p) != after.get(p)}
        self.assertTrue(
            changed,
            msg="P4 (precondición del oráculo): `record` debe haber "
                "persistido algo de forma durable")
        for path in sorted(changed):
            self.assertTrue(
                path.startswith(f".cdad/executions/{EXEC_ID}/guards/"),
                msg="P4/D4: `record` solo escribe bajo "
                    f"`.cdad/executions/{EXEC_ID}/guards/**`; escritura "
                    f"fuera de guards: {path!r}")


class TestP4LimitIsSignalToReconsiderNotViolation(GuardProjectCase):
    """P4 + D3 — un límite de intentos es señal para reconsiderar
    (escala), no prueba de incumplimiento: sin auto-bloqueo duro nuevo."""

    def test_p04_limite_agotado_recomienda_reconsiderar_sin_bloqueo(self) -> None:
        """P4/D3: con `guard_budget.max_attempts=2` y dos recuperaciones
        registradas, `budget` marca `exhausted`/`reconsider` — pero rc 0:
        agotar el presupuesto NO es una violación del guard ni un bloqueo
        automático; es la señal para ESCALAR/reconsiderar estrategia."""
        self.write_exec_context(
            guard_budget={"max_attempts": MAX_ATTEMPTS})
        for attempt, cause in ((1, "session-died-without-result"),
                               (2, "repetition-without-new-info")):
            ev_path, _ = self.write_event(
                attempt=attempt, cause=cause, session=f"sess-{attempt}")
            self.record_envelope(self.run_record(ev_path))

        proc = self.run_budget()
        self.assert_command_exists(proc, "budget")
        self.assertEqual(
            proc.returncode, 0,
            msg="P4/D3: agotar el presupuesto NO es una violación — la "
                "señal para reconsiderar se emite con rc 0 (sin "
                f"auto-bloqueo duro); got rc={proc.returncode} "
                f"stderr={proc.stderr!r}")
        env = self.budget_envelope(proc)
        self.assertEqual(
            env.get("consumed"), MAX_ATTEMPTS,
            msg="P4 (precondición del oráculo): los dos intentos deben "
                "contar contra el límite")
        self.assertIs(
            env.get("exhausted"), True,
            msg="P4: alcanzado el límite declarado, exhausted debe ser "
                "True (la señal es observable)")
        self.assertIs(
            env.get("reconsider"), True,
            msg="P4/D3: el límite es SEÑAL PARA RECONSIDERAR (escala), "
                "no prueba de incumplimiento — el presupuesto debe marcar "
                "`reconsider` y el orquestador decide, sin auto-bloqueo "
                "duro nuevo")


class TestP4CheckReceiptBeforeRepeating(GuardProjectCase):
    """P4 + D7 — comprobar si la acción terminó (receipt de 002) antes de
    repetir: el guard consulta el journal de 002 y SOLO SEÑALA."""

    def test_p07_receipt_de_002_consultado_antes_de_repetir(self) -> None:
        """D7: (a) sin receipt de 002, `record` de un retry NO declara
        reconciliación; (b) con el receipt presente bajo
        `.cdad/runtime/results/<execution_id>/<packet_id>/`, `record` lo
        consulta y emite `do_not_repeat: true` con `receipt_ref` — la
        señal para reconciliar en vez de repetir el efecto (invariante 5:
        un receipt no es aprobación semántica; el guard no repite
        efectos)."""
        # (a) Control: sin receipt de 002 → no hay reconciliación.
        ev1_path, _ = self.write_event(attempt=1, action="retry",
                                       cause="silent-tool-failure")
        env_no_receipt = self.record_envelope(self.run_record(ev1_path))
        self.assertIsNot(
            env_no_receipt.get("do_not_repeat"), True,
            msg="D7 (control): sin receipt de 002 no puede declararse que "
                "el efecto ya terminó — do_not_repeat no debe ser True")
        self.assertIsNot(
            env_no_receipt.get("reconciled"), True,
            msg="D7 (control): sin receipt de 002, reconciled no debe ser "
                "True (no se fabrica una reconciliación inexistente)")

        # (b) Receipt de 002 presente (invariante 5: reutilizado).
        receipt_path = self.root / RESULTS_DIR_REL / "receipt.json"
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(receipt_002_fixture(), indent=2, sort_keys=True)
            + "\n", encoding="utf-8")

        ev2_path, _ = self.write_event(
            attempt=2, action="retry", cause="silent-tool-failure",
            session="sess-B")
        env = self.record_envelope(self.run_record(ev2_path))

        self.assertIs(
            env.get("reconciled"), True,
            msg="D7: antes de repetir, el guard debe consultar el "
                "receipt/journal de 002 y declarar `reconciled` cuando el "
                "efecto ya terminó")
        receipt_ref = env.get("receipt_ref")
        self.assertIsInstance(
            receipt_ref, str,
            msg="D7: la evidencia de reconciliación debe citar el receipt "
                "de 002 por REFERENCIA (no redefinirlo)")
        self.assertIn(
            "runtime/results", receipt_ref,
            msg="D7: la referencia debe apuntar al journal/receipt de 002 "
                "bajo `.cdad/runtime/results/…`; got "
                f"{receipt_ref!r}")
        self.assertIs(
            env.get("do_not_repeat"), True,
            msg="D7: si la acción ya terminó (receipt de 002), el guard "
                "señala NO repetir el efecto — 'comprobar si terminó "
                "antes de repetir' se satisface reconciliando, y el guard "
                "solo señala")


if __name__ == "__main__":
    unittest.main()
