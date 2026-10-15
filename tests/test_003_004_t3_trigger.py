#!/usr/bin/env python3
"""003-004 T3 RED — `trigger` con unknowns + schema active-record-v1 (P6).

Contract:
- docs/specs/003-004-context-continuity/spec.md (P6; D5; invariante 2;
  criterios de aceptación 6, 7 y 11; §3 firma V6).
- docs/specs/003-004-context-continuity/plan.md (T3; focal declarado
  `tests/test_003_004_t3_trigger.py`; "sin contador/límite → `trigger:
  unknown` y `context_*: null` con `unknowns[]`"; "el presupuesto de
  intentos de una sesión nueva no se reinicia y se reporta con
  `source`"; "detener si: se pretende un número sin fuente").
- docs/specs/003-004-context-continuity/review-t2-rereview.md (Nit 1:
  cobertura del reclamo `record: active-record-v1` — focal
  `jsonschema.validate` del render de `resume` frío y caliente contra
  `active-record.schema.json`; hoy conforma en ambos, así que ese focal
  NO es RED: es la letra del patrón B sin test, y se declara tal cual).
- Forma de datos de guard: la REAL de 003 (nota del orquestador),
  tomada de `tests/test_003_003_t3_budget.py` (`guard-event-v1`); los
  eventos se siembran con la superficie real `scripts/cdad_guard.py
  record` (invariante 5: el presupuesto de 003 se REUTILIZA, no se
  redefine).

Superficie observable bajo prueba (V6: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_continuity.py trigger \
        --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID [--runtime opencode] [--json]

Decisiones de superficie fijadas por este RED (V6 — declaradas para el
GREEN/reviewer):

- El wrapper invocado es `scripts/cdad_continuity.py` (convención de
  T1/T2). El snapshot de presupuesto del RUNTIME viaja en el cuerpo D11
  del `--update` bajo la clave `budget` con `context_used_tokens`,
  `context_limit` y `source` (de dónde se reportó, ej. step-finish);
  `begin`/`checkpoint` lo congelan en el head y `trigger` lo LEE
  (plan T3: "el snapshot de presupuesto embebido en el checkpoint").
- Envolvente JSON (`--json`, contract `trigger-v1`; SIN asset de schema
  en plan T3 — esta envolvente declarada ES el schema en RED, mismo
  criterio que el RED de 003-003 T3):

      {
        "schema_version": 1,
        "trigger": "ok" | "prepare" | "rotate" | "unknown",
        "context_used_tokens": <int|null>,
        "context_limit": <int|null>,
        "context_source": <str|null>,
        "profile": {"limit": 200000, "reserve": 50000,
                    "prepare_at": 120000, "rotate_at": 150000} | null,
        "unknowns": [...],
        "budget": {"source": "<ruta durable guards/**>",
                   "consumed": <n>, "attempts": [...]} | null
      }

- La clave `trigger` lleva la SEÑAL (P6 literal: «trigger: unknown»);
  el perfil declarado es el 200k del plan T3: prepare_at=120000,
  rotate_at = limit − reserve = 200000 − 50000 = 150000, con fronteras
  `>=` fijadas por este RED (150000 usados → `rotate`; 130000 →
  `prepare`; 100000 → `ok`).
- `budget.source` NOMBRA el durable de 003
  (`.cdad/executions/<id>/guards/**`, clave
  `execution_id+packet_id+attempt`); una sesión nueva (proceso nuevo)
  NO lo reinicia (P4; criterio 6).
- `--packet` valida segmento seguro como `reconcile`/`begin` (cierre C
  de review-t2: `_safe_segment`): traversal → rc≠0, campo nombrado,
  store byte-intacto.
- `trigger` es read-only y determinista (invariante 1).

Este archivo (T3 trigger) cubre:
- P6 / criterios 6, 7, 11: sin contador o sin límite (y sin head) →
  `trigger: unknown`, `context_used_tokens`/`context_limit` null,
  `unknowns[]` explícito; contador no entero → unknown; PROHIBIDO
  derivar tokens de bytes — ningún número sin fuente (invariante 2).
- P6 / D5: con contador y límite enteros → `ok`/`prepare`/`rotate`
  según el perfil 200k; los umbrales viajan con fuente declarada.
- P4 (faceta T3): presupuesto de intentos leído del durable de 003 con
  `source`; una sesión nueva no lo reinicia.
- Cierre C (misma clase): `--packet` con traversal → rc≠0.
- Nit 1 de review-t2-rereview.md: `jsonschema.validate` del render de
  `resume` (frío y caliente) contra `active-record.schema.json`
  (reclamo `record: active-record-v1`) — cobertura declarada NO-RED.

Fuera de este archivo: P1/P2/P5/P7 (T1), P3/P8 (T2), adopción real (T4).

Fixtures: proyecto sintético en tmp con execution context, update y
eventos de guard PROPIOS y deterministas; los escenarios de fallo son
SIMULACIÓN sobre datos; ninguna escritura en este repo; no se provoca
ningún incidente real. Focales en primer plano con stdin cerrado
(DEVNULL); nunca background.

RED hoy (probe observable del CLI actual, 2026-10-07): `trigger` NO
existe (`invalid choice: 'trigger'`, rc 2) y `begin` SÍ acepta el
snapshot `budget` en el cuerpo (rc 0) — cada aserción de trigger fracasa
por comportamiento ausente (AssertionError con el mensaje «el comando
no existe aún»), nunca por ImportError ni sintaxis; el test no importa
el módulo del CLI. El focal de schema (Nit 1) pasa hoy por diseño y se
declara como cobertura, no como RED.
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
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"  # wrapper
GUARD_SCRIPT = REPO_ROOT / "scripts" / "cdad_guard.py"  # 003 (durables)
ASSETS_DIR = REPO_ROOT / "skills" / "cdad-cycle" / "assets"

FEATURE_ID = "003-004-context-continuity"

EXEC_ID = "exec-003-004-t3-red-001"
PACKET_ID = "003-004-context-continuity-implementer-green-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

EXEC_DIR_REL = f".cdad/executions/{EXEC_ID}"
CONTINUITY_DIR_REL = f"{EXEC_DIR_REL}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
GUARDS_DIR_REL = f"{EXEC_DIR_REL}/guards"
RECORD_CONTRACT = "active-record-v1"

# Perfil 200k declarado (plan T3: "perfil 200k/150k/120k"): entrada
# 150k, reserva 50k, preparar a 120k. rotate_at = limit − reserve.
PROFILE = {
    "limit": 200000,
    "reserve": 50000,
    "prepare_at": 120000,
    "rotate_at": 150000,
}

CONTEXT_SOURCE_TEXT = "step-finish runtime report (SIMULACIÓN T3)"


# ---------------------------------------------------------------- fixtures


def exec_context_fixture(**extra: object) -> dict:
    """Execution context mínimo (001) con delegación HITL vigente."""
    doc = {
        "schema_version": 1,
        "execution_id": EXEC_ID,
        "runtime": "opencode",
        "hitl_delegation": {
            "authority_ref": AUTHORITY_REF,
            "expires_on": "2099-12-31",
        },
    }
    doc.update(extra)
    return doc


def budget_snapshot(**overrides: object) -> dict:
    """Snapshot de presupuesto del runtime embebido en el cuerpo D11
    (forma fijada en RED, V6): tokens reportados por el runtime SI
    EXISTEN, con su `source` (nunca derivados de bytes)."""
    snap = {
        "context_used_tokens": 150000,
        "context_limit": 200000,
        "source": CONTEXT_SOURCE_TEXT,
    }
    snap.update(overrides)
    return snap


def update_fixture(**overrides: object) -> dict:
    """Cuerpo D11 válido (forma de T1) + snapshot `budget` opcional."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": "T3: trigger con unknowns de 003-004-context-continuity",
        "decisions": [
            {"decision": "trigger es señal, no límite duro",
             "rationale": "D5 de la spec: prepare_at sólo con contador y límite reales"},
        ],
        "uncertainties": ["V1: tokens de step-finish ¿por paso o acumulados?"],
        "next_action": "trigger antes de decidir rotación",
        "references": [],
    }
    doc.update(overrides)
    return doc


def guard_event(*, attempt: int, cause: str, session: str) -> dict:
    """Evento `guard-event-v1` — la forma REAL de 003 (nota del
    orquestador; idéntica a `guard_event()` de
    tests/test_003_003_t3_budget.py, que RED-declaró esa envolvente)."""
    return {
        "schema_version": 1,
        "event": "guard-event-v1",
        "execution_id": EXEC_ID,
        "packet_id": PACKET_ID,
        "attempt": attempt,
        "kind": "recovery-attempt",
        "cause": cause,
        "session": session,
        "action": "resume-same-session",
        "at": "2026-10-07T00:00:00Z",
    }


# ---------------------------------------------------------------- helpers


class TriggerProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con execution context y update propios."""

    def setUp(self) -> None:
        self.reset_project()

    def reset_project(self) -> None:
        """Proyecto sintético fresco (Nit 2 de review-t2-rereview.md:
        helper directo en vez de llamar setUp() dentro de los tests)."""
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t3-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())

    # -- escritura de fixtures ---------------------------------------------

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_update(self, doc: dict) -> Path:
        return self.write_json("fixture/update.json", doc)

    def build_head(self, **update_overrides: object) -> dict:
        """Head válido creado por la MISMA superficie declarada en §3
        (`begin`), con el snapshot `budget` congelado si el override lo
        lleva. Devuelve la envolvente de `begin`."""
        update = self.write_update(update_fixture(**update_overrides))
        env = self.write_envelope(self.run_write("begin", update), "begin")
        return env

    def snapshot(self) -> dict[str, bytes]:
        """Snapshot completo del proyecto (read-only contra esto)."""
        return tree_snapshot(self.root)

    # -- corridas del CLI ----------------------------------------------------

    def run_cli(self, script: Path, *argv: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [sys.executable, str(script), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P6 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s; got timeout={exc!r}")

    def run_write(self, command: str, update: Path) -> (
            subprocess.CompletedProcess):
        return self.run_cli(CONTINUITY_SCRIPT, command,
                            "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_trigger(self, *, packet_id: str = PACKET_ID) -> (
            subprocess.CompletedProcess):
        return self.run_cli(
            CONTINUITY_SCRIPT, "trigger",
            "--project-root", str(self.root),
            "--execution-context", str(self.exec_context),
            "--packet", packet_id, "--json")

    def run_guard_record(self, event: dict) -> subprocess.CompletedProcess:
        """Siembra un evento durable de 003 con la superficie REAL
        (`scripts/cdad_guard.py record`; invariante 5: se reutiliza)."""
        event_path = self.write_json("fixture/guard-event.json", event)
        return self.run_cli(GUARD_SCRIPT, "record",
                            "--project-root", str(self.root),
                            "--event", str(event_path))

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser comportamiento ausente, mensaje
        explícito — nunca import ni sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P6: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                " --project-root --execution-context --packet` declarado "
                "en §3 (V6) es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P6: el comando `{which}` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={out!r} stderr={err!r}")
        self.assertNotIn(
            "Traceback", err, msg=f"P6: `{which}` terminó con traceback")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    def assert_unknown_envelope(self, env: dict, missing: tuple[str, ...],
                                label: str) -> None:
        """P6/criterios 6, 7, 11 — la envolvente de un trigger SIN señal:
        `trigger: unknown`, `context_*` null (NUNCA un número fabricado,
        invariante 2) y `unknowns[]` explícito que nombra lo ausente."""
        self.assertEqual(
            env.get("trigger"), "unknown",
            msg=f"P6/{label}: sin señal el trigger es `unknown`; got "
                f"{env.get('trigger')!r} (full={env!r})")
        self.assertIsNone(
            env.get("context_used_tokens"),
            msg=f"P6/{label}/criterio 7,11: `context_used_tokens` queda "
                f"null (PROHIBIDO fabricar un número ni derivarlo de "
                f"bytes — invariante 2); got "
                f"{env.get('context_used_tokens')!r}")
        self.assertIsNone(
            env.get("context_limit"),
            msg=f"P6/{label}: `context_limit` queda null (sin señal no "
                f"hay límite declarado); got "
                f"{env.get('context_limit')!r}")
        unknowns = env.get("unknowns")
        self.assertIsInstance(
            unknowns, list,
            msg=f"P6/{label}: `unknowns[]` viaja explícito; got "
                f"{unknowns!r}")
        self.assertTrue(
            unknowns,
            msg=f"P6/{label}: `unknown` exige `unknowns[]` explícito "
                f"(no se fabrica éxito)")
        unknowns_text = json.dumps(unknowns, ensure_ascii=False)
        for field in missing:
            self.assertIn(
                field, unknowns_text,
                msg=f"P6/{label}: `unknowns[]` nombra el campo ausente "
                    f"`{field}`; got {unknowns!r}")


# ---------------------------------------------------------------- tests


class TestP6TriggerUnknownSinSenal(TriggerProjectCase):
    """P6 / criterios 6, 7, 11 — trigger SIN señal: unknown + nulls +
    unknowns[] explícito; prohibido derivar tokens de bytes."""

    def test_p06_sin_contador_o_sin_limite_trigger_unknown_con_nulls(
            self) -> None:
        """P6 (subTests): cada caso sin señal → rc 0 (reporte, no crash),
        `trigger: unknown`, `context_*: null`, `unknowns[]` nombrando lo
        ausente:
        - sin head (nada durable, nada reportado);
        - head sin snapshot `budget` (ni contador ni límite);
        - snapshot con SÓLO contador (sin límite);
        - snapshot con SÓLO límite (sin contador);
        - snapshot con contador NO entero (float → P6 exige enteros);
        - prohibido derivar tokens de bytes (invariante 2): el head
          conoce el tamaño en BYTES de su cuerpo y AUN así el trigger
          reporta null — ningún número sin fuente."""
        # (a) sin head: proyecto recién creado, sin checkpoint alguno.
        with self.subTest(caso="sin-head"):
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_used_tokens", "context_limit"), "sin-head")

        # (b) head SIN snapshot budget (ni contador ni límite).
        with self.subTest(caso="sin-contador-ni-limite"):
            self.reset_project()
            self.build_head()
            before = self.snapshot()
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_used_tokens", "context_limit"),
                "sin-contador-ni-limite")
            self.assertEqual(
                self.snapshot(), before,
                msg="P6/invariante 1: trigger es read-only (proyecto "
                    "byte a byte igual tras reportar unknown)")

        # (c) snapshot con SÓLO contador (sin límite).
        with self.subTest(caso="solo-contador"):
            self.reset_project()
            self.build_head(budget=budget_snapshot(
                context_limit=None))
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_limit",), "solo-contador")

        # (d) snapshot con SÓLO límite (sin contador).
        with self.subTest(caso="solo-limite"):
            self.reset_project()
            self.build_head(budget=budget_snapshot(
                context_used_tokens=None))
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_used_tokens",), "solo-limite")

        # (e) contador NO entero (P6: sólo enteros preparan/rotan).
        with self.subTest(caso="contador-no-entero"):
            self.reset_project()
            self.build_head(budget=budget_snapshot(
                context_used_tokens=150000.5))
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_used_tokens",), "contador-no-entero")

        # (f) prohibido derivar tokens de bytes: hay un head con su
        # campo `bytes` (tamaño en bytes del cuerpo) y un archivo de
        # referencia de 1000 bytes — AUN ASÍ null (ningún número sin
        # fuente declarada; invariante 2).
        with self.subTest(caso="bytes-no-son-tokens"):
            self.reset_project()
            ref = self.root / "fixture" / "referencia.md"
            ref.parent.mkdir(parents=True, exist_ok=True)
            ref.write_bytes(b"x" * 1000)
            self.build_head(references=["fixture/referencia.md"])
            head_doc = json.loads(
                (self.root / HEAD_REL).read_text(encoding="utf-8"))
            self.assertIsInstance(
                head_doc.get("bytes"), int,
                msg="precondición: el head porta el tamaño en BYTES")
            env = self.write_envelope(self.run_trigger(), "trigger")
            self.assert_unknown_envelope(
                env, ("context_used_tokens", "context_limit"),
                "bytes-no-son-tokens")
            self.assertNotIn(
                head_doc.get("bytes"), (env.get("context_used_tokens"),
                                        env.get("context_limit")),
                msg="P6/invariante 2: el trigger NO convierte bytes en "
                    "tokens (ni el `bytes` del head ni el de ninguna "
                    "referencia aparecen como contexto)")

    def test_p06_trigger_determinista_y_read_only(self) -> None:
        """P6/invariante 1: dos corridas de `trigger` sobre el mismo
        proyecto producen salida idéntica (determinista) y el proyecto
        queda byte a byte igual (read-only)."""
        self.build_head()
        before = self.snapshot()
        first = self.run_trigger()
        env1 = self.write_envelope(first, "trigger")
        second = self.run_trigger()
        self.assertEqual(
            second.stdout, first.stdout,
            msg="P6/invariante 1: trigger es determinista — dos corridas "
                "producen salida idéntica")
        self.assertEqual(
            self.snapshot(), before,
            msg="P6/invariante 1: trigger es read-only")


class TestP6Perfil200kPrepareRotate(TriggerProjectCase):
    """P6/D5 — con contador y límite enteros: ok/prepare/rotate según el
    perfil 200k (entrada 150k, reserva 50k, preparar a 120k)."""

    def test_p06_con_contador_y_limite_la_senal_sigue_el_perfil_200k(
            self) -> None:
        """P6/D5: con `context_used_tokens` y `context_limit` enteros el
        trigger SÍ señala — tabla cerrada del perfil 200k (fronteras
        `>=`, fijadas por este RED):
        100000 → `ok` (< prepare_at); 130000 → `prepare`
        (≥ prepare_at, < rotate_at); 150000 → `rotate`
        (≥ limit − reserve = 150000). Los `context_*` del render son los
        enteros reportados (con su `source`), y los umbrales viajan en
        `profile` — todo número con fuente declarada."""
        table = (
            (100000, "ok"),
            (130000, "prepare"),
            (150000, "rotate"),
        )
        for used, expected_signal in table:
            with self.subTest(used=used, señal=expected_signal):
                self.reset_project()
                self.build_head(budget=budget_snapshot(
                    context_used_tokens=used))
                before = self.snapshot()
                env = self.write_envelope(self.run_trigger(), "trigger")

                self.assertEqual(
                    env.get("trigger"), expected_signal,
                    msg=f"P6/D5: con contador={used} y límite=200000 "
                        f"enteros, la señal del perfil 200k es "
                        f"`{expected_signal}`; got {env.get('trigger')!r} "
                        f"(full={env!r})")
                self.assertEqual(
                    env.get("context_used_tokens"), used,
                    msg=f"P6: el render reporta el contador ENTERO "
                        f"reportado ({used}); got "
                        f"{env.get('context_used_tokens')!r}")
                self.assertEqual(
                    env.get("context_limit"), 200000,
                    msg=f"P6: el render reporta el límite ENTERO "
                        f"reportado (200000); got "
                        f"{env.get('context_limit')!r}")
                profile = env.get("profile")
                self.assertIsInstance(
                    profile, dict,
                    msg=f"P6/D5: los umbrales aplicados viajan en "
                        f"`profile` (números con fuente declarada); got "
                        f"{profile!r}")
                self.assertEqual(
                    (profile or {}).get("prepare_at"),
                    PROFILE["prepare_at"],
                    msg=f"P6/D5: `prepare_at` del perfil 200k es 120000; "
                        f"got {(profile or {}).get('prepare_at')!r}")
                self.assertEqual(
                    (profile or {}).get("rotate_at"), PROFILE["rotate_at"],
                    msg=f"P6/D5: `rotate_at` = limit − reserve = "
                        f"200000 − 50000 = 150000; got "
                        f"{(profile or {}).get('rotate_at')!r}")
                self.assertEqual(
                    (profile or {}).get("limit"), PROFILE["limit"],
                    msg="P6/D5: `limit` del perfil es 200000")
                self.assertEqual(
                    (profile or {}).get("reserve"), PROFILE["reserve"],
                    msg="P6/D5: `reserve` del perfil es 50000")
                self.assertEqual(
                    self.snapshot(), before,
                    msg="P6/invariante 1: trigger read-only también al "
                        "señalar")


class TestP4IntentosDelDurableConSource(TriggerProjectCase):
    """P4 (faceta T3) — intentos y causas leídos del durable de 003,
    reportados con `source`; una sesión nueva NO los reinicia."""

    def test_p04_intentos_del_durable_no_se_reinician_con_sesion_nueva(
            self) -> None:
        """P4: dos recuperaciones sembradas con la superficie REAL de
        003 (`cdad_guard.py record`; intento 1 sess-A, intento 2 sess-B
        — 'sesión nueva' sobre el mismo execution+packet) → `trigger`
        reporta el presupuesto durable con `source` que nombra
        `.cdad/executions/<id>/guards/**` (clave
        `execution_id+packet_id+attempt`), `consumed == 2` y AMBAS
        causas; re-consultar con un proceso NUEVO (sesión nueva) NO
        reinicia el contador (sigue 2, mismas causas)."""
        ev1 = guard_event(attempt=1, cause="session-died-without-result",
                          session="sess-A")
        ev2 = guard_event(attempt=2, cause="repetition-without-new-info",
                          session="sess-B")  # sesión nueva, mismo packet
        rec1 = self.run_guard_record(ev1)
        self.assertEqual(
            rec1.returncode, 0,
            msg="precondición: `cdad_guard record` (superficie real de "
                f"003) registra el intento 1; got rc={rec1.returncode} "
                f"stderr={rec1.stderr!r}")
        rec2 = self.run_guard_record(ev2)
        self.assertEqual(
            rec2.returncode, 0,
            msg="precondición: la 'sesión nueva' registra el intento 2 "
                f"en el MISMO durable; got rc={rec2.returncode} "
                f"stderr={rec2.stderr!r}")

        before = self.snapshot()
        env = self.write_envelope(self.run_trigger(), "trigger")

        budget = env.get("budget")
        self.assertIsInstance(
            budget, dict,
            msg=f"P4: el trigger reporta el presupuesto de intentos "
                f"leído del durable de 003; got keys={sorted(env)!r} "
                f"(full={env!r})")
        source = (budget or {}).get("source")
        self.assertIsInstance(
            source, str,
            msg=f"P4: el presupuesto se reporta CON `source` (nota del "
                f"orquestador); got {source!r}")
        self.assertIn(
            ".cdad/executions/", source,
            msg=f"P4: `budget.source` nombra el durable de 003 bajo "
                f"`.cdad/executions/…`; got {source!r}")
        self.assertIn(
            "guards", source,
            msg=f"P4: `budget.source` nombra `guards/**` "
                f"({GUARDS_DIR_REL}/…); got {source!r}")
        self.assertEqual(
            (budget or {}).get("consumed"), 2,
            msg=f"P4: los DOS intentos del durable cuentan "
                f"(consumed=2); got {(budget or {}).get('consumed')!r}")
        attempts = (budget or {}).get("attempts")
        self.assertIsInstance(
            attempts, list, msg="P4: los intentos viajan como lista")
        causes = {a.get("cause") for a in attempts} if attempts else set()
        self.assertEqual(
            causes, {"session-died-without-result",
                     "repetition-without-new-info"},
            msg=f"P4 (invariante 11): las causas de AMBOS intentos se "
                f"conservan en el reporte; got {attempts!r}")

        # Sesión NUEVA (proceso nuevo del trigger): el durable NO se
        # reinicia — mismos intentos, mismas causas, mismo source.
        env2 = self.write_envelope(self.run_trigger(), "trigger")
        budget2 = env2.get("budget") or {}
        self.assertEqual(
            budget2.get("consumed"), 2,
            msg=f"P4/criterio 6: una sesión nueva NO reinicia el "
                f"presupuesto durable de 003 (sigue consumed=2); got "
                f"{budget2.get('consumed')!r}")
        self.assertEqual(
            budget2.get("source"), source,
            msg="P4: la segunda consulta reporta el MISMO `source` "
                "durable (la sesión nueva no lo sustituye)")
        self.assertEqual(
            {a.get("cause") for a in (budget2.get("attempts") or [])},
            causes,
            msg="P4: las causas también sobreviven a la sesión nueva")

        # Read-only: el durable de 003 y el resto del proyecto intactos.
        self.assertEqual(
            self.snapshot(), before,
            msg="P4/invariante 1: el trigger NO escribe (el presupuesto "
                "es del guard 003 y el trigger sólo lo lee)")


class TestCPacketSegmentoSeguroTrigger(TriggerProjectCase):
    """Cierre C (misma clase, `trigger`) — `--packet` valida segmento
    seguro: traversal → rc≠0, campo nombrado, store byte-intacto."""

    def test_c_packet_traversal_falla_cerrado_en_trigger(self) -> None:
        """C: `trigger --packet "../../x"` (y `..`, `a/b`) → rc≠0 con el
        campo `packet` nombrado en el delta; NADA escrito (read-only,
        invariante 1; «no se fabrica éxito»). Control positivo primero:
        con un packet válido el trigger corre rc 0 (el fallo del
        incumplidor es la validación, no el comando)."""
        self.build_head()
        control = self.write_envelope(self.run_trigger(), "trigger")
        self.assertEqual(
            control.get("schema_version"), 1,
            msg="C (control): con packet válido el trigger corre rc 0")

        head_bytes = (self.root / HEAD_REL).read_bytes()
        for bad in ("../../x", "..", "a/b"):
            with self.subTest(packet=bad):
                proc = self.run_trigger(packet_id=bad)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"C: `trigger --packet {bad!r}` falla cerrado "
                        f"(rc≠0; el packet_id DEBE validar segmento "
                        f"seguro, cierre C de review-t2); got "
                        f"rc={proc.returncode} stdout={out!r} "
                        f"stderr={err!r}")
                self.assertIn(
                    "packet", out + err,
                    msg=f"C: el delta nombra el campo (`packet`) para "
                        f"{bad!r}; got stdout={out!r} stderr={err!r}")
                self.assertEqual(
                    (self.root / HEAD_REL).read_bytes(), head_bytes,
                    msg="C: el packet incumplidor NO toca el store "
                        "(read-only, invariante 1)")


class TestNit1ActiveRecordSchemaConformance(TriggerProjectCase):
    """Nit 1 (review-t2-rereview.md, clase B cobertura) — el reclamo
    `record: active-record-v1` de los renders de `resume` se valida con
    `jsonschema` contra `active-record.schema.json`, frío y caliente.
    El objeto validado es la PROYECCIÓN (`env["projection"]`), que es lo
    que el reclamo `record` describe (nit literal: "un focal
    `jsonschema.validate(projection, active-record.schema.json)`").
    NO es RED (los probes del review muestran conformancia real en
    ambos): es la letra del patrón B sin test, declarada tal cual."""

    def _validate_against_active_record(self, env: dict, label: str) -> None:
        """El objeto validado es la proyección L1 del render
        (`env["projection"]`): es lo que el reclamo `record:
        active-record-v1` describe (nit literal)."""
        projection = env.get("projection")
        self.assertIsInstance(
            projection, dict,
            msg=f"Nit 1 ({label}): el render de `resume` expone la "
                f"proyección L1 bajo `projection`; got keys={sorted(env)!r}")
        schema = self._load_active_record_schema()
        try:
            import jsonschema  # perezoso: nunca ImportError del RED
        except Exception as exc:  # pragma: no cover
            self.fail(
                f"Nit 1 ({label}): `jsonschema` es dependencia de la "
                f"suite y debe estar disponible; got {exc!r}")
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        errors = sorted(
            validator_cls(schema).iter_errors(projection), key=str)
        self.assertEqual(
            [],
            [f"{list(e.absolute_path)}: {e.message}" for e in errors],
            msg=f"Nit 1 ({label}): la proyección del render de `resume` "
                f"que declara `record: {RECORD_CONTRACT}` DEBE validar "
                f"contra `active-record.schema.json` "
                "(review-t2-rereview Nit 1); violaciones: "
                f"{[f'{list(e.absolute_path)}: {e.message}' for e in errors]!r}")

    def _load_active_record_schema(self) -> dict:
        """Schema `active-record.schema.json` por su `$id` (artefacto de
        CONTRATO declarado en spec §7 y plan T1 — no es código de
        implementación; patrón idéntico a test_003_004_t2_reviewfix)."""
        for path in sorted(ASSETS_DIR.glob("*.schema.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):  # pragma: no cover
                continue
            if doc.get("$id") == RECORD_CONTRACT:
                return doc
        self.fail(
            f"Nit 1: el schema del contrato `{RECORD_CONTRACT}` debe "
            f"existir bajo `{ASSETS_DIR.relative_to(REPO_ROOT)}` con "
            f"$id `{RECORD_CONTRACT}`")

    def test_nit1_render_de_resume_conforma_active_record_v1_frio_y_caliente(
            self) -> None:
        """Nit 1: el render caliente (con head, `record:
        active-record-v1` + proyección L1) y el frío (sin head, rc 0,
        estado `no-checkpoint`) validan ambos contra
        `active-record.schema.json` — el reclamo de contrato del render
        tiene test (cierre de la letra del patrón B)."""
        # --- caliente (con head) ---------------------------------------
        self.build_head()
        proc_hot = self.run_resume()
        env_hot = self.write_envelope(proc_hot, "resume")
        self.assertEqual(
            env_hot.get("record"), RECORD_CONTRACT,
            msg=f"Nit 1 (precondición): el render caliente declara "
                f"`record: {RECORD_CONTRACT}`; got "
                f"{env_hot.get('record')!r}")
        self._validate_against_active_record(env_hot, "caliente")

        # --- frío (sin head) ---------------------------------------------
        self.reset_project()
        self.assertFalse(
            (self.root / HEAD_REL).exists(),
            msg="Nit 1 (precondición): proyecto SIN head (frío)")
        proc_cold = self.run_resume()
        self.assert_command_exists(proc_cold, "resume")
        self.assertEqual(
            proc_cold.returncode, 0,
            msg="Nit 1: el resume frío corre rc 0 (criterio 4, T2)")
        env_cold = json.loads(proc_cold.stdout.decode("utf-8"))
        self.assertIn(
            "no-checkpoint", json.dumps(env_cold, ensure_ascii=False),
            msg="Nit 1 (precondición): el render frío declara el estado "
                "explícito `no-checkpoint` (decisión B)")
        self._validate_against_active_record(env_cold, "frío")

    # -- reuso de la superficie de `resume` (§3, T1) --------------------

    def run_resume(self) -> subprocess.CompletedProcess:
        return self.run_cli(
            CONTINUITY_SCRIPT, "resume",
            "--project-root", str(self.root),
            "--execution-context", str(self.exec_context), "--json")


if __name__ == "__main__":
    unittest.main()
