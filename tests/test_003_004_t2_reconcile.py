#!/usr/bin/env python3
"""003-004 T2 RED — `reconcile` sobre la matriz §2 (P3, P8-fixtures, R-B2).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§2 caso a caso, §3 D6/D10,
  criterios 3 y 4; P3; P8 parte fixtures).
- docs/specs/003-004-context-continuity/plan.md (T2; focales declarados;
  "con receipt válido el CLI NO ofrece repetir el efecto", "cabezas
  divergentes → escalar", regreso `tests/validate-consistency.sh`).
- docs/specs/003-004-context-continuity/review-t1-rereview.md (R-B2:
  `--role` sin política → rc≠0 fail-closed, antes de T4/adopción).

Superficie observable (V6; forma completa de `reconcile-v1` y del
protocolo read-only declaradas en `tests/test_003_004_t2_writeahead.py`
— mismo contract, archivo hermano):

    python3 scripts/cdad_continuity.py reconcile \
        --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID [--json]

Este archivo cubre la MATRIZ de clasificación de §2 con fixtures
etiquetados SIMULACIÓN (`tests/fixtures/003_004/`, stores reales 002/004
sembrados SÓLO como datos):

- `not-started` (sin despacho, sin receipt) — matriz y write-ahead.
- `dispatched-unknown` (dispatch I8 sin `receipt.json`) → NO se clasifica
  como fracaso y NO autoriza repetir (invariante 3).
- `received` (receipt 002 válido) → el efecto ya aplicado NO se ofrece
  repetir (`repeat_effect: false`, D10; un receipt NO es aprobación
  semántica, invariante 4).
- `already-closed` (receipt + materializaciones/** de 002) → tarea
  cerrada sin retrabajo (D6).
- `expired-authority` (delegación hitl vencida) → se reporta la vigencia
  y NO se autoriza dispatch/materialize (D4).
- `unknown` (receipt ilegible / ausencia de señal fiable) → estado
  `unknown` con `unknowns[]` explícito, SIN fabricar éxito ni fracaso
  (§2: "no se fabrica éxito ni fracaso"; plan T2 "detener si: no se
  puede leer un receipt sin ambigüedad → unknown, escalar").
- `stale`/tamper del store de continuuity → rc≠0 con el delta exacto
  (P1 vía `reconcile`, V4 sin `--allow-stale`).
- split-brain (cuerpos divergentes de la MISMA clave en
  `continuity/bodies/`) → escalar, rc≠0 (D7).
- La ausencia de `ACTIVE.json` (proyección on-demand, O1) NUNCA es error
  de `reconcile` ni de `resume` (criterio 4).
- R-B2: `resume --role` SIN política (`docs/cdad-policy.json` ausente)
  → fail-closed rc≠0 (control positivo con política → rc 0).
- UN escenario continuo legítimo completo que NO dispara intervención
  (P8/O4, plan §2): write-ahead → despacho simulado → receipt →
  reconcile → checkpoint de avance → reconcile, sin escalado y sin
  duplicar el efecto.

Fixtures: proyecto sintético en tmp; los JSON de `tests/fixtures/003_004`
son plantillas de datos (marcadores `@EXECUTION_ID@`/`@PACKET_ID@` y los
digests se recalculan sobre los bytes sembrados) — ningún incidente
real, ninguna escritura en este repo.

RED hoy (probes observables del CLI actual, 2026-10-07): `reconcile` no
existe (invalid choice) y `resume --role` sin política acepta rc=0; cada
aserción fracasa por comportamiento ausente (AssertionError con el ele-
mento violado nombrado), nunca por ImportError ni sintaxis.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"  # wrapper
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "003_004"

FEATURE_ID = "003-004-context-continuity"

EXEC_ID = "exec-003-004-t2-red-001"
PACKET_ID = "003-004-context-continuity-implementer-t2-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

EXEC_DIR_REL = f".cdad/executions/{EXEC_ID}"
CONTINUITY_DIR_REL = f"{EXEC_DIR_REL}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
BODIES_DIR_REL = f"{CONTINUITY_DIR_REL}/bodies"
DISPATCH_REL = f"{EXEC_DIR_REL}/dispatches/attempt-1.json"
RESULTS_DIR_REL = f".cdad/runtime/results/{EXEC_ID}/{PACKET_ID}"
RECEIPT_REL = f"{RESULTS_DIR_REL}/receipt.json"
PART_REL = f"{RESULTS_DIR_REL}/parts/role-report.utf8"
BUNDLE_REL = f"{RESULTS_DIR_REL}/bundle.json"
MAT_DIR_REL = f".cdad/runtime/materializations/{EXEC_ID}/{PACKET_ID}"
AUTH_SHA = "0" * 64  # nombre del journal de materialización (SIMULACIÓN)
MAT_REL = f"{MAT_DIR_REL}/{AUTH_SHA}.json"
STATE_REL = "docs/.cdad-state.json"
ACTIVE_REL = "ACTIVE.json"
POLICY_REL = "docs/cdad-policy.json"

REPORT_TEXT = "Role report SIMULACIÓN (matriz T2 de 003-004).\n"
TARGET_TEXT = "Target de tarea ya cerrada — SIMULACIÓN, sin retrabajo.\n"

# Clasificaciones que NO disparan intervención (escenario continuo O4).
NON_INTERVENTIONAL = {"not-started", "dispatched-unknown", "received",
                      "already-closed", "unknown"}


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


def update_fixture(**overrides: object) -> dict:
    """Cuerpo D11 válido (forma de T1)."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": "T2: reconcile de la matriz §2 de 003-004-validación",
        "decisions": [
            {"decision": "reconcile read-only",
             "rationale": "el CLI reporta; el orquestador jueza y escribe"},
        ],
        "uncertainties": ["V2: status de sesión no distingue vivo-estancado"],
        "next_action": "reconciliar antes de reintentar (D6)",
        "references": [],
    }
    doc.update(overrides)
    return doc


def template(name: str) -> str:
    """Texto de la plantilla SIMULACIÓN declarada en tests/fixtures/003_004."""
    path = FIXTURES_DIR / name
    return path.read_text(encoding="utf-8")


def substitute(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------- helpers


class MatrixCase(unittest.TestCase):
    """Proyecto sintético con stores 002/004 sembrados como DATOS."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t2rec-red-")
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

    def write_update(self, doc: dict, name: str = "update.json") -> Path:
        return self.write_json(f"fixture/{name}", doc)

    def exec_context_path(self, **overrides: object) -> Path:
        return self.write_json("fixture/exec.json",
                               exec_context_fixture(**overrides))

    def snapshot(self) -> dict[str, bytes]:
        """Snapshot completo del proyecto (read-only se verifica contra isto)."""
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in sorted(self.root.rglob("*")) if p.is_file()
        }

    # -- seeds (SIMULACIÓN: datos, nunca flujos reales 002/004) -------------

    def seed_part(self) -> bytes:
        """Part staged bajo el inbox del results dir (forma 002)."""
        part_bytes = REPORT_TEXT.encode("utf-8")
        path = self.root / PART_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(part_bytes)
        return part_bytes

    def seed_dispatch(self) -> Path:
        """Registro I8 del despacho (forma 004) como DATO."""
        text = substitute(template("dispatch-dispatched.simulacion.json"), {
            "@EXECUTION_ID@": EXEC_ID,
            "@PACKET_ID@": PACKET_ID,
        })
        path = self.root / DISPATCH_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def seed_receipt(self) -> Path:
        """Receipt 002 válido + bundle.json (forma de results dir)."""
        part_bytes = self.seed_part()
        report_sha = hashlib.sha256(part_bytes).hexdigest()
        bundle_sha = hashlib.sha256(
            part_bytes + b"# bundle SIMULACION\n").hexdigest()
        text = substitute(template("receipt-received.simulacion.json"), {
            "@EXECUTION_ID@": EXEC_ID,
            "@PACKET_ID@": PACKET_ID,
            "@REPORT_SHA256@": report_sha,
            "@REPORT_BYTES@": str(len(part_bytes)),
            "@BUNDLE_SHA256@": bundle_sha,
        })
        receipt_path = self.write_bytes(RECEIPT_REL, text)
        bundle = {
            "schema_version": 1,
            "execution_id": EXEC_ID,
            "packet_id": PACKET_ID,
            "bundle_sha256": bundle_sha,
            "source": "SIMULACIÓN fixture 003-004 (matriz T2)",
        }
        self.write_json(BUNDLE_REL, bundle)
        return receipt_path

    def seed_materialization(self) -> Path:
        """Journal de materialización de 002 (tarea cerrada) como DATO."""
        part_bytes = self.seed_part()
        target_path = self.root / "fixture/closed-target.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(TARGET_TEXT, encoding="utf-8")
        target_sha = hashlib.sha256(
            TARGET_TEXT.encode("utf-8")).hexdigest()
        bundle_sha = hashlib.sha256(
            part_bytes + b"# bundle SIMULACION\n").hexdigest()
        text = substitute(template("materialization-closed.simulacion.json"), {
            "@EXECUTION_ID@": EXEC_ID,
            "@PACKET_ID@": PACKET_ID,
            "@AUTH_SHA256@": AUTH_SHA,
            "@BUNDLE_SHA256@": bundle_sha,
            "@TARGET_SHA256@": target_sha,
        })
        return self.write_bytes(MAT_REL, text)

    def seed_receipt_unreadable(self) -> Path:
        """Receipt CORIZADO (JSON inválido): señal NO fiable → unknown."""
        text = template("receipt-unreadable.simulacion.json")
        return self.write_bytes(RECEIPT_REL, text)

    def write_bytes(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    # -- corridas del CLI ----------------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P3 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s; got timeout={exc!r}")

    def run_reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")

    def run_write(self, command: str, update: Path) -> (
            subprocess.CompletedProcess):
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_resume(self, *, role: str | None = None) -> (
            subprocess.CompletedProcess):
        argv = ["resume", "--project-root", str(self.root),
                "--execution-context", str(self.exec_context), "--json"]
        if role is not None:
            argv += ["--role", role]
        return self.run_cli(*argv)

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser comportamiento ausente, mensaje
        explícito — nunca import ni sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P3: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                " --project-root --execution-context --packet` declarado "
                "en §3 (V6) es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P3: el comando `{which}` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={out!r} stderr={err!r}")
        self.assertNotIn(
            "Traceback", err, msg=f"P1: `{which}` terminó con traceback")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))


# ---------------------------------------------------------------- tests


class TestP3MatrizReconcile(MatrixCase):
    """P3/P8-fixtures — los estados de §2 clasificados por fixtures."""

    def test_p03_matriz_de_reconcile_clasifica_los_estados_de_spec(
            self) -> None:
        """P3/P8: la clasificación cerrada de §2, caso por caso (subTests),
        cada uno en un proyecto sintético con el store SEMBRADO como
        datos (SIMULACIÓN). En TODOS los casos: rc 0, envolvente
        `reconcile-v1`, `repeat_effect: false`, el proyecto queda SIN
        cambios (read-only e invariante 1: nunca escribe el producto ni
        el state) y `reasons` justifica la clasificación. La ausencia de
        ACTIVE.json NUNCA es un error (O1: se verifica al final de cada
        caso)."""
        matrix = {
            "not-started": (False, False, False),
            "dispatched-unknown": (True, False, False),
            "received": (True, True, False),
            "already-closed": (True, True, True),
        }
        for name, (dispatch, receipt, close) in matrix.items():
            with self.subTest(estado=name):
                self.setUp()
                if dispatch:
                    self.seed_dispatch()
                if receipt:
                    self.seed_receipt()
                if close:
                    self.seed_materialization()
                self.assertFalse(
                    (self.root / ACTIVE_REL).exists(),
                    msg="O1 (control del fixture): ningún proyecto "
                        "persiste ACTIVE.json")

                before = self.snapshot()
                proc = self.run_reconcile()
                env = self.write_envelope(proc, "reconcile")

                self.assertEqual(
                    env.get("reconcile"), "reconcile-v1",
                    msg=f"P3: envolvente declara `reconcile-v1`; got {env!r}")
                self.assertEqual(
                    env.get("classification"), name,
                    msg=f"P3/§2: el estado sembrado `{name}` se clasifica "
                        f"exactamente así; got "
                        f"{env.get('classification')!r} (full={env!r})")
                self.assertIs(
                    env.get("repeat_effect"), False,
                    msg=f"P3/D10: el CLI NUNCA ofrece repetir un efecto "
                        f"(`repeat_effect` false) para `{name}`; got "
                        f"{env.get('repeat_effect')!r}")
                reasons = env.get("reasons")
                self.assertIsInstance(
                    reasons, list,
                    msg=f"P3: la clasificación viaja justificada; got "
                        f"{reasons!r}")
                self.assertTrue(
                    reasons, msg=f"P3: `reasons` no queda vacío para {name}")
                self.assertEqual(
                    self.snapshot(), before,
                    msg=f"P3/invariante 1: reconcile es READ-ONLY — el "
                        f"proyecto estaba byte a byte igual tras "
                        f"clasificar `{name}` (nunca escribe el producto "
                        f"ni docs/.cdad-state.json)")
                self.assertFalse(
                    (self.root / ACTIVE_REL).exists(),
                    msg="O1/criterio 4: la ausencia de ACTIVE.json NO es "
                        "un error de reconcile (sigue sin existir)")

    def test_p03_expirada_y_unknown_completan_la_matriz(self) -> None:
        """P3/§2: los dos estados restantes de la matriz —
        `expired-authority` (la delegación HITL vencida NO autoriza
        dispatch/materialize (D4) y `unknown` (receipt ilegible SIN
        señal fiable: `unknowns[]` explícito, SIN fabricar éxito ni
        fracaso; plan T2 "detener si: receipt ilegible → unknown,
        escalar")."""
        with self.subTest(estado="expired-authority"):
            self.setUp()
            self.exec_context = self.exec_context_path(
                hitl_delegation={
                    "authority_ref": AUTHORITY_REF,
                    "expires_on": "2020-01-01",
                })
            before = self.snapshot()
            env = self.write_envelope(self.run_reconcile(), "reconcile")
            self.assertEqual(
                env.get("classification"), "expired-authority",
                msg=f"P3/D4: la delegación vencida se marca "
                    f"`expired-authority`; got "
                    f"{env.get('classification')!r} (full={env!r})")
            authority = env.get("authority")
            self.assertIsInstance(
                authority, dict,
                msg=f"P3/D4: la envolvente expone `authority` con vigencia; "
                    f"got {authority!r}")
            self.assertEqual(
                (authority or {}).get("state"), "expired",
                msg=f"P3/D4: `authority.state` = `expired`; got "
                    f"{(authority or {}).get('state')!r}")
            self.assertIs(
                env.get("repeat_effect"), False,
                msg="P3/D4: con autoridad vencida NADA se autoriza "
                    "(repeat/dispatch/materialize quedan fuera)")
            self.assertEqual(
                self.snapshot(), before,
                msg="P3/invariante 1: read-only también con autoridad "
                    "vencida")

        with self.subTest(estado="unknown"):
            self.setUp()
            self.seed_dispatch()
            self.seed_receipt_unreadable()
            before = self.snapshot()
            env = self.write_envelope(self.run_reconcile(), "reconcile")
            self.assertEqual(
                env.get("classification"), "unknown",
                msg=f"P3/§2: receipt ilegible SIN señal fiable se clasifica "
                    f"`unknown` (ni `received` ni fracaso fabricado); got "
                    f"{env.get('classification')!r} (full={env!r})")
            self.assertIs(
                env.get("repeat_effect"), False,
                msg="P3/D6: `unknown` tampoco autoriza repetir")
            unknowns = env.get("unknowns")
            self.assertIsInstance(
                unknowns, list,
                msg=f"P3: los unknowns viajan explícitos; got {unknowns!r}")
            self.assertTrue(
                unknowns,
                msg="P3/§2: `unknown` exige `unknowns[]` explícito "
                    "(no se fabrica éxito ni fracaso)")
            self.assertEqual(
                self.snapshot(), before,
                msg="P3/invariante 1: read-only también en `unknown`")


class TestP3SinSenalNiFallaFabricada(MatrixCase):
    """Criterio 4 — sin señal fiable: `unknown`, nunca rc-neutro con
    estado inventado; y la ausencia de ACTIVE.json no es error (O1)."""

    def test_criterio4_active_json_ausente_no_es_error_ni_en_resume(
            self) -> None:
        """Criterio/O1 (spec §2): «Un ACTIVE.json persistido NO existe:
        la memoria activa es proyección on-demand (O1), por lo que su
        ausencia no es error de reconcile ni de resume.» Ambos comandos
        corren rc 0 en un proyecto sin ACTIVE.json y sin fabricar
        artefacto persistido (el CLI no crea uno para "completar")."""
        self.seed_dispatch()
        self.seed_receipt()
        self.assertFalse((self.root / ACTIVE_REL).exists())

        env = self.write_envelope(self.run_reconcile(), "reconcile")
        self.assertEqual(
            env.get("classification"), "received",
            msg="P3 (precondición del control): el estado `received` se "
                "reconcilia sin ACTIVE.json")
        proc = self.run_resume()
        self.write_envelope(proc, "resume")

        self.assertFalse(
            (self.root / ACTIVE_REL).exists(),
            msg="O1/criterio 4: ni `reconcile` nor `resume` crea ni "
                "exige un ACTIVE.json persistido (proyección on-demand)")


class TestP1StaleTamperReconcile(MatrixCase):
    """P1 vía reconcile / V4 — stale/tamper → rc≠0 con delta exacto."""

    def test_p1_stale_tamper_del_store_falla_cerrado_con_delta(
            self) -> None:
        """P1/V4: el head del store de continuuity queda TAMPERADO a nivel
        de cuerpo (bytes del archivo de body alterados, nombre
        ≠ sha256(contenido)) → `reconcile` falla cerrado (rc≠0) y el
        delta NOMBRA el elemento violado (el nombre del archivo y su
        digest; sin `--allow-stale`, eliminado O3)."""
        update = self.write_update(update_fixture())
        self.write_envelope(self.run_write("begin", update), "begin")

        bodies = sorted((self.root / BODIES_DIR_REL).glob("*.json"))
        self.assertEqual(
            len(bodies), 1,
            msg="precondición: un único cuerpo content-addressed")
        body_file = bodies[0]
        body_file.write_bytes(body_file.read_bytes() + b"\n")
        tampered = body_file.read_bytes()

        proc = self.run_reconcile()
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P1/V4: reconcile con el cuerpo tamperado falla cerrado "
                f"(rc≠0; `--allow-stale` eliminado); got "
                f"rc={proc.returncode} stdout={out!r} stderr={err!r}")
        self.assertIn(
            body_file.name, out + err,
            msg=(f"P1: el delta exacto NOMBRA el elemento violado "
                 f"({body_file.name!r} con su digest); got stdout={out!r} "
                 f"stderr={err!r}"))
        self.assertIn(
            hashlib.sha256(tampered).hexdigest()[:8], out + err,
            msg="P1: el delta cita el digest real del contenido "
                "(nombre ≠ contenido = tamper)")
        self.assertEqual(
            body_file.read_bytes(), tampered,
            msg="P1: reconcile NO repara: el tamper permanece para el "
                "orquestador (el CLI es read-only)")


class TestD7SplitBrainReconcile(MatrixCase):
    """D7 — igual-clave-con-cuerpo-distinto → escalar (split-brain)."""

    def test_d7_cuerpos_divergentes_de_la_misma_clave_escalan(self) -> None:
        """D7: dos cuerpos de la MISMA clave
        `(execution_id, packet_id, attempt)` en `continuity/bodies/`
        (nombre = sha256 de los bytes del archivo, store content-addressed
        de T1) → `reconcile` escala: rc≠0 y el delta nombra AL MENOS uno
        de los dos digests en conflicto (los dos candidatos a cabeza)."""
        update = self.write_update(update_fixture())
        self.write_envelope(self.run_write("begin", update), "begin")

        body_a_file = sorted((self.root / BODIES_DIR_REL).glob("*.json"))[0]
        doc = json.loads(body_a_file.read_text(encoding="utf-8"))
        self.assertEqual(
            (doc.get("attempt"), doc.get("packet_id")),
            (1, PACKET_ID),
            msg="precondición: el cuerpo sembrado porta la clave")
        doc["goal"] = (
            "VARIANTE divergente simulada (segunda sesión bifurcada — "
            "fixture de datos SIMULACIÓN, split-brain de §2)")
        body_b_bytes = json.dumps(
            doc, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False).encode("utf-8")
        sha_b = hashlib.sha256(body_b_bytes).hexdigest()
        (self.root / BODIES_DIR_REL / f"{sha_b}.json").write_bytes(
            body_b_bytes)

        proc = self.run_reconcile()
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"D7: divergencia de la misma clave escala (rc≠0); got "
                f"rc={proc.returncode} stdout={out!r} stderr={err!r}")
        self.assertIn(
            sha_b, out + err,
            msg=f"D7: el delta nombra el digest en conflicto "
                f"({sha_b!r}); got stdout={out!r} stderr={err!r}")
        self.assertIn(
            "split-brain", out + err,
            msg="D7/§2: la divergencia de cabezas se REPORTA (split-brain "
                "→ escalar; el CLI no elige un ganador ni continúa)")

        # Sin sobrescribir: ambos candidatos siguen en el store para el
        # orquestador (evidencia completa, no resolución silenciosa).
        self.assertTrue(
            (self.root / CONTINUITY_DIR_REL / "bodies" / f"{sha_b}.json")
            .exists(),
            msg="D7: el cuerpo divergente NO se borró para esconder la "
                "divergencia (evidencia intacta para escalar)")


class TestRB2RoleSinPolitica(MatrixCase):
    """R-B2 (residuo rereview B2) — `--role` sin política → fail-closed."""

    def test_rb2_role_sin_politica_falla_cerrado(self) -> None:
        """R-B2: hoy `_load_policy` devuelve `{}` sin
        `docs/cdad-policy.json` y `resume --role test-writer` expone
        referencias de implementación con rc=0 (probe A2). Fail-closed:
        con `--role` presente y la política AUSENTE → rc≠0; control
        positivo (con política → rc 0) para que el fallo sea inequívoco
        por la política faltante."""
        # Proyecto SIN política: un head válido existe (begin no la exige).
        update = self.write_update(update_fixture())
        self.write_envelope(self.run_write("begin", update), "begin")

        proc = self.run_resume(role="test-writer")
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"R-B2: `--role` sin política falla cerrado (rc≠0); got "
                f"rc={proc.returncode} stdout={out!r} stderr={err!r}")
        self.assertIn(
            "cdad-policy", out + err,
            msg=f"R-B2: el delta nombra la política ausente; got "
                f"stdout={out!r} stderr={err!r}")

        # Control positivo: la MISMA construcción con la política
        # materializada termina rc 0 (el fallo anterior era la política).
        (self.root / POLICY_REL).parent.mkdir(parents=True, exist_ok=True)
        (self.root / POLICY_REL).write_text(
            json.dumps({
                "path_policy": {
                    "documentation_roots": ["docs"],
                    "implementation_roots": ["agents", "skills", "scripts",
                                             "sources", "build"],
                    "test_roots": ["tests"],
                },
                "schema_version": 1,
            }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        proc_ok = self.run_resume(role="test-writer")
        self.assertEqual(
            proc_ok.returncode, 0,
            msg=f"R-B2 (control): con la política presente `resume "
                f"--role` tiene éxito; got rc={proc_ok.returncode} "
                f"stdout={proc_ok.stdout!r} stderr={proc_ok.stderr!r}")


class TestP8EscenarioContinuoLegitimo(MatrixCase):
    """P8/O4 — UN escenario continuo completo SIN intervención."""

    def test_p08_escenario_continuo_legitimo_no_dispara_intervencion(
            self) -> None:
        """P8/O4 (plan §2: "un escenario continuo etiquetado SIMULACIÓN:
        varias llamadas y artefactos que progresan, un reconcile sin
        efecto nuevo y una reconstrucción intermedia NO disparan
        intervención ni retrabajo"): corrida completa write-ahead →
        despacho simulado → receipt → reconcile → checkpoint de avance
        → segundo reconcile — ambos reconciles en el conjunto NO
        intervencional (rc 0, sin escalado, sin `repeat_effect`), el
        efecto queda SIN duplicar y el flujo conduce sin pedir al
        usuario (stdin cerrado en TODO)."""
        update1 = self.write_update(update_fixture())
        env1 = self.write_envelope(self.run_write("begin", update1), "begin")
        self.assertEqual(
            env1.get("seq"), 1,
            msg="P8 (precondición): el write-ahead persiste el head")

        self.seed_dispatch()
        receipt = self.seed_receipt()
        self.seed_materialization()

        before = self.snapshot()
        env_r1 = self.write_envelope(self.run_reconcile(), "reconcile")
        self.assertIn(
            env_r1.get("classification"),
            NON_INTERVENTIONAL,
            msg=f"P8/O4: la clasificación NO dispara intervención "
                f"(first pass sobre el trabajo ya recibido); got "
                f"{env_r1.get('classification')!r} (full={env_r1!r})")
        self.assertIs(
            env_r1.get("repeat_effect"), False,
            msg="P8/D10: con receipt válido el CLI NO ofrece repetir")
        self.assertEqual(
            self.snapshot(), before,
            msg="P8: reconcile NO duplica el efecto ni escribe (read-only)")

        # El orquestador avanza (checkpoint de avance, attempt 2).
        update2 = self.write_update(
            update_fixture(
                attempt=2,
                goal="Avance tras reconciliar el trabajo ya recibido"),
            name="update2.json")
        env2 = self.write_envelope(self.run_write("checkpoint", update2),
                                   "checkpoint")
        self.assertEqual(
            env2.get("seq"), 2,
            msg="P8: el avance del orquestador encadena `seq` 2 (la "
                "reconciliación NO bloqueó un flujo legítimo)")
        self.assertEqual(
            receipt.read_bytes(),
            (self.root / RECEIPT_REL).read_bytes(),
            msg="P8/D10: el receipt durable queda INTACTO (el CLI "
                "consume, no materializa ni reescribe)")

        env_r2 = self.write_envelope(self.run_reconcile(), "reconcile")
        self.assertIn(
            env_r2.get("classification"), NON_INTERVENTIONAL,
            msg=f"P8/O4: el segundo reconcile tampoco dispara "
                f"intervención; got {env_r2.get('classification')!r}")

        # Reconstrucción intermedia (resume, stdin cerrado, sin preguntar).
        proc = self.run_resume()
        self.write_envelope(proc, "resume")
        self.assertFalse(
            (self.root / STATE_REL).exists(),
            msg="P8/invariante 1: ni el CLI toca docs/.cdad-state.json — "
                "el orquestador es su único escritor")
        receipts_after = [
            p for p in (self.root / RESULTS_DIR_REL).rglob("receipt.json")]
        self.assertEqual(
            len(receipts_after), 1,
            msg="P8/D6: ningún segundo efecto — UN solo receipt (sin "
                "duplicar el trabajo ya aplicado)")


if __name__ == "__main__":
    unittest.main()
