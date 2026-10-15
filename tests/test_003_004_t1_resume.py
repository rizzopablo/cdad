#!/usr/bin/env python3
"""003-004 T1 RED — `resume`: reanudación frío, tamper y rol (P1, P2, P5).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§3 firma V6, P1, P2, P5;
  criterios de aceptación 2 y 5).
- docs/specs/003-004-context-continuity/plan.md (T1; focales declarados
  `tests/test_003_004_t1_checkpoint.py` y `tests/test_003_004_t1_resume.py`;
  "los 4 negativos de tamper vía `resume`" y "`resume --role test-writer`
  no expone `implementation_roots` de la política").

Superficie observable bajo prueba (V6: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_continuity.py resume \
        --project-root ROOT --execution-context EXEC.json \
        [--role ROLE] [--max-bytes N] [--json]

El checkpoint previo se crea con la MISMA superficie declarada en §3
(`begin`, y `checkpoint` para el segundo eslabón de la cadena).

Decisiones de superficie fijadas por este RED (V6 — declaradas para el
GREEN/reviewer) — AMENDMENT B (review-t2-decision.md, 2026-10-07):
el RENDER de `resume` ya NO reclama `continuity-checkpoint-v1`;
declara solo `record: active-record-v1` (el tag `checkpoint:` solo
corresponde al L2 persistido por begin/checkpoint):

- Envolvente JSON (`--json`, contract `continuity-checkpoint-v1`, render
  de `resume`): además de los campos del checkpoint
  (`checkpoint`, `execution_id`, `packet_id`, `attempt`, `seq`,
  `body_sha256`, `prev_checkpoint_sha256`, `references`, `bytes`,
  `max_bytes`), expone la proyección L1 on-demand bajo `projection` con
  campos cerrados: `goal`, `authority` (de la delegación HITL del
  execution context), `decisions` (cada una con `rationale`),
  `uncertainties`, `next_action`.
- "Sin pedir al usuario" es observable: el CLI corre con stdin cerrado
  (DEVNULL) y termina rc 0 — ninguna pregunta interactiva.
- P1: `resume` verifica el digest del cuerpo canónico, el eslabón
  `prev_checkpoint_sha256` y la existencia+digest de cada referencia;
  cada negativo → rc≠0 con el delta que NOMBRA el elemento violado.
- P5: el render para `--role test-writer` excluye rutas de
  `implementation_roots` declaradas en la política del proyecto
  (`ROOT/docs/cdad-policy.json`); las referencias dentro del scope del
  rol (tests) sí se exponen.

Este archivo (T1 resume) cubre:
- P2 / criterio 5: reanudación en frío reconstruye objetivo, decisiones
  con razón, autoridad, incertidumbres y próxima acción sin preguntar.
- P1 / criterio 2: los CUATRO negativos de tamper detectados vía
  `resume` (sha alterado, cadena rota, referencia inexistente, digest de
  referencia alterado), cada uno rc≠0 con delta nombrado.
- P5: `resume --role test-writer` nunca incluye implementación ni rutas
  fuera del scope del rol.

El cap `--max-bytes` de la proyección (P7/criterio 8) se cubre en el
focal `test_003_004_t1_checkpoint.py`; el conflicto de `begin`
divergente es T2.

Fixtures: proyecto sintético en tmp (execution context, update,
referencias y política PROPIOS), deterministas; ninguna escritura en
este repo; ningún incidente real provocado.

RED hoy: `scripts/cdad_continuity.py` no existe aún; cada aserción
positiva fracasa por comportamiento ausente (AssertionError con el
mensaje `el comando no existe aún`), nunca por ImportError ni sintaxis —
el test no importa el módulo del CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------- contrato

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_SCRIPT = REPO_ROOT / "scripts" / "cdad_continuity.py"  # wrapper

FEATURE_ID = "003-004-context-continuity"

EXEC_ID = "exec-003-004-t1-red-001"
PACKET_ID = "003-004-context-continuity-implementer-green-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

CONTINUITY_DIR_REL = f".cdad/executions/{EXEC_ID}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"

REF_TEST_REL = "fixture/notes-history.md"
# Fixture de implementación bajo un root DECLARADO por `policy_fixture`
# (`build` ∈ implementation_roots): la clasificación por rol proviene de
# la política del proyecto, no de un token del nombre (decisión B2 de
# review-t1-decision.md; el fixture `fixture/impl-note.md` original no
# está bajo ningún root declarado y el GREEN B2 lo expone
# correctamente).
REF_IMPL_REL = "build/impl-note.md"

TEST_REFERENCE_TEXT = "Historia L3 por referencia: state 001, receipts 002.\n"
IMPL_REFERENCE_TEXT = "Nota interna de implementación (scope exclusión).\n"

GOAL = "Reanudar T1 de 003-004 sin repetir objetivo ni autorizaciones"
NEXT_ACTION = "Ejecutar reconcile antes de cualquier reintento"
DECISION_TEXT = "Proyección on-demand sin ACTIVE.json"
DECISION_RATIONALE = "O1: su ausencia no es error de resume"
UNCERTAINTY = "V2: el status de sesión no distingue vivo-estancado"


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
    """Contenido D11 del cuerpo: lo que queda congelado en el checkpoint."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": GOAL,
        "decisions": [
            {"decision": DECISION_TEXT, "rationale": DECISION_RATIONALE},
        ],
        "uncertainties": [UNCERTAINTY],
        "next_action": NEXT_ACTION,
        "references": [],
    }
    doc.update(overrides)
    return doc


def policy_fixture() -> dict:
    """Política de rutas del proyecto (002/004: se REUTILIZA la forma)."""
    return {
        "path_policy": {
            "documentation_roots": ["docs"],
            "implementation_roots": ["agents", "skills", "scripts",
                                     "sources", "build"],
            "test_roots": ["tests"],
        },
        "schema_version": 1,
    }


# ---------------------------------------------------------------- helpers


class ResumeProjectCase(unittest.TestCase):
    """Proyecto sintético con head válido creado por la MISMA superficie."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t1res-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    # -- construcción del proyecto fixture -----------------------------

    def build_valid_project(self, *, references: list[str] | None = None,
                            chain: bool = False) -> None:
        """Proyecto con head válido (1 eslabón, o 2 con `chain`)."""
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())
        self.write_text(REF_TEST_REL, TEST_REFERENCE_TEXT)
        self.write_text(REF_IMPL_REL, IMPL_REFERENCE_TEXT)
        self.write_json("docs/cdad-policy.json", policy_fixture())

        update = update_fixture(
            references=references if references is not None else [])
        update_path = self.write_json("fixture/update.json", update)
        env1 = self.write_envelope(self.run_write("begin", update_path),
                                   "begin")
        if not chain:
            self.head_env = env1
            return
        update2 = update_fixture(
            attempt=2, goal=GOAL + " (avance)",
            references=references if references is not None else [])
        update2_path = self.write_json("fixture/update2.json", update2)
        self.head_env = self.write_envelope(
            self.run_write("checkpoint", update2_path), "checkpoint")

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_text(self, rel: str, content: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def write_update(self, doc: dict) -> Path:
        return self.write_json("fixture/update.json", doc)

    # -- corridas del CLI ----------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P1 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca puede "
                f"colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path,
                  ) -> subprocess.CompletedProcess:
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_resume(self, *, role: str | None = None,
                   ) -> subprocess.CompletedProcess:
        argv = ["resume", "--project-root", str(self.root),
                "--execution-context", str(self.exec_context), "--json"]
        if role is not None:
            argv += ["--role", role]
        return self.run_cli(*argv)

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser el comportamiento ausente, con mensaje
        explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P1: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                "` declarado en §3 (V6) es obligatorio")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P1: el comando `{which}` no existe aún (RED por CLI "
                f"ausente); rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", err,
            msg=f"P1: `{which}` terminó con traceback stderr={err!r}")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    def head_document(self) -> dict:
        head = self.root / HEAD_REL
        self.assertTrue(
            head.is_file(),
            msg="P1 (precondición): el head inmutable vive en "
                f"`{HEAD_REL}` (superficie fijada en RED, V6)")
        return json.loads(head.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- tests


class TestP2ResumeFrio(ResumeProjectCase):
    """P2 / criterio 5 — reanudación en frío sin preguntar al usuario."""

    def test_p02_resume_frio_reconstruye_paquete_completo_sin_preguntar(
            self) -> None:
        """P2/criterio 5: con un head válido, `resume --json` reconstruye
        objetivo, decisiones CON razón, autoridad, incertidumbres y
        próxima acción; corre con stdin cerrado y termina rc 0 (ninguna
        pregunta interactiva: el usuario no repite objetivo ni
        aprobaciones)."""
        self.build_valid_project(references=[REF_TEST_REL])

        proc = self.run_resume()
        env = self.write_envelope(proc, "resume")
        rendered = json.dumps(env, ensure_ascii=False)

        # --- B (review-t2-decision.md, review-fix T2 2026-10-07) ---
        # Cambio explícito y DECLARADO por el test-writer del RED
        # review-fix (cierre B): la aserción previa DEMANDABA
        # `checkpoint: continuity-checkpoint-v1` en el render de
        # `resume` — exactamente el defecto B del review-t2. La
        # decisión del orquestador invierte ese reclamo: NINGÚN render
        # de `resume` (frío o caliente) reclama
        # `continuity-checkpoint-v1`; el render declara SOLO
        # `record: active-record-v1` (el checkpoint es el L2
        # persistido). La aserción NO se debilita: pasa a exigir la
        # forma B (record + ausencia del reclamo).
        self.assertIsNone(
            env.get("checkpoint"),
            msg=f"B (review-t2-decision.md): el render de `resume` NO "
                f"lleva la clave `checkpoint` (declara solo `record`); "
                f"got {env.get('checkpoint')!r} keys={sorted(env)!r}")
        self.assertNotIn(
            "continuity-checkpoint-v1", json.dumps(env, ensure_ascii=False),
            msg=f"B (review-t2-decision.md): el render de `resume` no "
                f"reclama en ningún punto el contrato "
                f"`continuity-checkpoint-v1`; got "
                f"render={json.dumps(env, ensure_ascii=False)[:600]!r}")
        self.assertEqual(
            env.get("record"), "active-record-v1",
            msg=f"B (review-t2-decision.md): el render declara solo "
                f"`record: active-record-v1`; got {env.get('record')!r} "
                f"(full={env!r})")

        projection = env.get("projection")
        self.assertIsInstance(
            projection, dict,
            msg=f"P2: el render expone la proyección L1 on-demand bajo "
                f"`projection`; got keys={sorted(env)!r}")

        self.assertEqual(
            projection.get("goal"), GOAL,
            msg=f"P2: el objetivo se reconstruye SIN repetirlo; got "
                f"{projection.get('goal')!r}")
        self.assertEqual(
            projection.get("next_action"), NEXT_ACTION,
            msg=f"P2: la próxima acción se reconstruye; got "
                f"{projection.get('next_action')!r}")

        decisions = projection.get("decisions")
        self.assertIsInstance(
            decisions, list,
            msg=f"P2: las decisiones viajan como lista; got {decisions!r}")
        self.assertTrue(
            decisions,
            msg="P2: al menos una decisión congelada (D11) se reconstruye")
        for decision in decisions:
            self.assertIsInstance(
                decision, dict, msg="P2: cada decisión es un objeto")
            self.assertEqual(
                decision.get("decision"), DECISION_TEXT,
                msg=f"P2: la decisión se reconstruye; got {decision!r}")
            self.assertTrue(
                str(decision.get("rationale") or "").strip(),
                msg=f"P2: cada decisión viaja CON su razón (D11); got "
                    f"{decision!r}")

        uncertainties = projection.get("uncertainties")
        self.assertIsInstance(
            uncertainties, list,
            msg=f"P2: las incertidumbres se reconstruyen; got "
                f"{uncertainties!r}")
        self.assertIn(
            UNCERTAINTY, uncertainties,
            msg=f"P2: la incertidumbre declarada (V2) viaja al render; "
                f"got {uncertainties!r}")

        self.assertIn(
            AUTHORITY_REF, rendered,
            msg=f"P2: la autoridad (delegación HITL, authority_ref "
                f"{AUTHORITY_REF!r}) se reconstruye en el render; got "
                f"render={rendered[:600]!r}")


class TestP1TamperNegativos(ResumeProjectCase):
    """P1 / criterio 2 — los cuatro negativos de tamper vía `resume`."""

    def test_p1_resume_detecta_los_cuatro_negativos_con_delta(self) -> None:
        """P1/criterio 2: sha del cuerpo alterado, cadena rota,
        referencia inexistente y digest de referencia alterado → cada uno
        rc≠0 con el delta que NOMBRA el elemento violado (nunca silencio
        ni éxito fabricado)."""
        cases = (
            ("sha-alterado", "body_sha256"),
            ("cadena-rota", "prev_checkpoint_sha256"),
            ("referencia-inexistente", REF_TEST_REL),
            ("digest-referencia-alterado", REF_TEST_REL),
        )
        for name, needle in cases:
            with self.subTest(negativo=name):
                self.setUp()
                self.build_valid_project(
                    references=[REF_TEST_REL], chain=True)
                head = self.head_document()
                self.assertEqual(
                    head.get("seq"), 2,
                    msg="P1 (precondición): la cadena tiene 2 eslabones "
                        "para poder romperse")

                if name == "sha-alterado":
                    head["body_sha256"] = "0" * 64
                elif name == "cadena-rota":
                    head["prev_checkpoint_sha256"] = "1" * 64
                elif name == "referencia-inexistente":
                    (self.root / REF_TEST_REL).unlink()
                else:  # digest-referencia-alterado
                    self.write_text(REF_TEST_REL,
                                    TEST_REFERENCE_TEXT + "tamper\n")
                self.write_json(HEAD_REL, head)

                proc = self.run_resume()
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                combined = out + err

                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"P1: el negativo `{name}` debe fallar cerrado "
                        f"(rc≠0); got rc={proc.returncode} "
                        f"stdout={out!r} stderr={err!r}")
                self.assertIn(
                    needle, combined,
                    msg=f"P1: el delta exacto nombra el elemento violado "
                        f"({needle!r}) para el negativo `{name}`; got "
                        f"stdout={out!r} stderr={err!r}")


class TestP5RoleRestrictionsSurvive(ResumeProjectCase):
    """P5 — las restricciones de rol sobreviven al checkpoint."""

    def test_p05_resume_role_test_writer_no_expone_implementacion(
            self) -> None:
        """P5: `resume --role test-writer` expone las referencias dentro
        del scope del rol (tests) y NUNCA rutas de `implementation_roots`
        de la política (aislamiento conservado, plan.md:106-107)."""
        self.build_valid_project(
            references=[REF_TEST_REL, REF_IMPL_REL])

        proc = self.run_resume(role="test-writer")
        env = self.write_envelope(proc, "resume")
        rendered = proc.stdout.decode("utf-8", errors="replace")

        self.assertIn(
            REF_TEST_REL, rendered,
            msg=f"P5: la referencia dentro del scope del rol (tests: "
                f"{REF_TEST_REL!r}) SÍ se expone al test-writer")
        self.assertNotIn(
            "impl-note", rendered,
            msg=f"P5: `resume --role test-writer` NUNCA expone rutas de "
                f"implementation_roots de la política "
                f"({REF_IMPL_REL!r} excluida); got render={rendered[:600]!r}")
        self.assertIn(
            "test-writer", json.dumps(env, ensure_ascii=False),
            msg="P5: el render declara el rol aplicado (`--role` "
                "sobrevive al repackage)")


if __name__ == "__main__":
    unittest.main()
