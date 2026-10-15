#!/usr/bin/env python3
"""003-004 T1 review-fix RED — cierres B1, B2, O2 (P1, P5, P3).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§3 V6, P1, P3, P5,
  criterio 1).
- docs/specs/003-004-context-continuity/review-t1.md (hallazgos B1, B2,
  O2 con probes B/A/D).
- docs/specs/003-004-context-continuity/review-t1-decision.md
  (disposición del orquestador: la fuente de verdad de este RED
  review-fix; substage RED del ciclo corto B1→GREEN).

Un test focal por cierre (packet
003-004-context-continuity-test-writer-red-002):

- **B1 (P1/§3, review-t1 B1):** el head persistido por `begin` valida
  contra `continuity-checkpoint.schema.json` ($id
  `continuity-checkpoint-v1`), y el render de `resume` DECLARA el
  contrato del registro L1 (`active-record-v1`) cuya proyección expuesta
  valida contra `active-record.schema.json`. Hoy (probe B del review) el
  render declara sólo `continuity-checkpoint-v1` con una `projection`
  extra y sin `no_op`: un contrato que rechaza a su propio render. El
  render NO valida contra el contrato del checkpoint; la proyección L1
  es un registro propio con su propio contrato (decisión B1).
- **B2 (P5, review-t1 B2):** la clasificación de rutas por rol proviene
  de la POLÍTICA del proyecto (`ROOT/docs/cdad-policy.json`, misma forma
  de `path_policy`), no de un token del nombre del archivo. Un fixture
  de implementación bajo un root declarado (`build/impl-note.md`) se
  oculta a `--role test-writer`, y el control negativo
  `docs/impl-decisiones.md` (documentación por política, nombre con
  `impl`) es VISIBLE — hoy la heurística de token lo oculta (probe D).
- **O2 (P1/P3, review-t1 O2):** `begin` exige `packet_id` string no
  vacío y `attempt` entero en `--update`; si falta o es de otro tipo →
  rc≠0 con el campo nombrado y NADA persistido (fail-closed: no se
  persiste un head schema-inválido ni se pierde la discriminación de la
  clave `(execution_id, packet_id, attempt)` de P3).

Mapeo a postcondiciones: B1 → P1 (head íntegro y contratos §3
alineados); B2 → P5 (restricciones de rol desde la política); O2 → P1
(head siempre schema-válido) y P3 (clave de idempotencia
discriminante).

Fixtures: proyecto sintético en tmp (execution context, update,
referencias y política PROPIOS, deterministas); ninguna escritura en
este repo; ningún incidente real provocado.

RED hoy (review-fix): la implementación EXISTE (T1 GREEN) y cada focale
fracasa por el DEFECTO observado en review-t1 (AssertionError sobre la
conducta esperada según la decisión del orquestador) — nunca por
ImportError ni sintaxis: el test no importa el módulo del CLI y
`jsonschema` se importa de forma perezosa dentro del helper (si
faltara, el fallo también sería una aserción con diagnóstico, no un
error de import).
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
STATE_REL = "docs/.cdad-state.json"

ASSETS_DIR = REPO_ROOT / "skills" / "cdad-cycle" / "assets"

CHECKPOINT_CONTRACT = "continuity-checkpoint-v1"
RECORD_CONTRACT = "active-record-v1"

REF_TEST_REL = "fixture/notes.md"
REF_IMPL_IN_ROOT_REL = "build/impl-note.md"      # root DECLARADO por la política
REF_DOCS_WITH_IMPL_NAME = "docs/impl-decisiones.md"  # control negativo B2

TEST_REFERENCE_TEXT = "Historia L3 por referencia: state 001, receipts 002.\n"
IMPL_IN_ROOT_TEXT = "Nota interna de implementación bajo root declarado.\n"
IMPL_NAME_DOCS_TEXT = "Decisiones de implementación registradas como docs.\n"

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
    """Política de rutas del proyecto (forma `path_policy`, 002/004).

    La clasificación por rol se declara AQUÍ (fuente única de verdad,
    decisión B2): `build/` es implementación y `docs/` es documentación
    — INDEPENDIENTE del nombre del archivo.
    """
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


class ReviewFixProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con policy/execution context propios."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t1rf-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    # -- construcción del proyecto fixture -----------------------------

    def build_valid_project(self, *, references: list[str] | None = None,
                            chain: bool = False) -> dict:
        """Proyecto con head válido (1 eslabón, o 2 con `chain`);
        devuelve la envolvente del head actual."""
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())
        self.write_text(REF_TEST_REL, TEST_REFERENCE_TEXT)
        self.write_json("docs/cdad-policy.json", policy_fixture())
        update = update_fixture(
            references=references if references is not None else [])
        update_path = self.write_json("fixture/update.json", update)
        env1 = self.write_envelope(self.run_write("begin", update_path),
                                   "begin")
        if not chain:
            return env1
        update2 = update_fixture(
            attempt=2, goal=GOAL + " (avance)",
            references=references if references is not None else [])
        update2_path = self.write_json("fixture/update2.json", update2)
        return self.write_envelope(
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
        """RED: el fracaso debe ser el comportamiento bajo prueba, con
        mensaje explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P1: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                "` declarado en §3 (V6) es obligatorio")
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

    def continuity_store(self) -> dict[str, bytes]:
        """Snapshot {ruta relativa: bytes} del store de continuity."""
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }

    # -- validación de schemas (jsonschema perezoso) --------------------

    def load_schema(self, contract_id: str) -> dict | None:
        """Schema de assets cuyo `$id` es `contract_id` (artefactos de
        contrato declarados en spec §7; NO es código de implementación)."""
        for path in sorted(ASSETS_DIR.glob("*.schema.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):  # pragma: no cover
                continue
            if doc.get("$id") == contract_id:
                return doc
        return None

    def assert_validates(self, document: object, schema: dict | None,
                         label: str, contract_id: str) -> None:
        """`document` valida contra `schema` (draft-07) → lista de
        errores vacía; cualquier violación es AssertionError con el
        delta exacto (nunca ValidationError crudo ni ImportError)."""
        self.assertIsInstance(
            schema, dict,
            msg=f"B1: el contrato `{contract_id}` ({label}) debe tener "
                f"schema en `{ASSETS_DIR.relative_to(REPO_ROOT)}/` con "
                f"$id `{contract_id}`; la envolvente no puede declarar un "
                "contrato que su propio repo no define")
        try:
            import jsonschema  # perezoso: el RED no falla por ImportError
        except Exception as exc:  # pragma: no cover
            self.fail(
                f"B1: `jsonschema` indisponible ({exc!r}); la validación "
                "de contrato declarada en review-t1-decision.md (B1) "
                "requiere el validador de la suite")
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        errors = sorted(
            validator_cls(schema).iter_errors(document), key=str)
        self.assertEqual(
            [],
            [f"{list(e.absolute_path)}: {e.message}" for e in errors],
            msg=f"B1: {label} valida contra el contrato `{contract_id}` "
                f"que declara (decisión B1: alinear render, schema y "
                f"spec); violaciones: "
                f"{[f'{list(e.absolute_path)}: {e.message}' for e in errors]!r}")


# ---------------------------------------------------------------- tests


class TestB1HeadYRenderSatisfacenSusContratos(ReviewFixProjectCase):
    """B1 (P1/§3) — head de `begin` y render de `resume` contra schemas."""

    def test_b01_head_de_begin_y_render_de_resume_satisfacen_su_contrato(
            self) -> None:
        """B1 (decisión del orquestador): el head persistido por `begin`
        valida contra `continuity-checkpoint-v1`, y el render de
        `resume` declara el contrato del registro L1
        (`active-record-v1`) con su proyección validando contra
        `active-record.schema.json` — un contrato no puede rechazar a su
        propio render (review-t1 B1, probe B)."""
        self.build_valid_project(references=[REF_TEST_REL])

        # (a) head de begin: documento del checkpoint L2 declarado.
        head = self.head_document()
        self.assertEqual(
            head.get("checkpoint"), CHECKPOINT_CONTRACT,
            msg=f"P1: el head declara `{CHECKPOINT_CONTRACT}`; got "
                f"{head.get('checkpoint')!r}")
        self.assert_validates(
            head, self.load_schema(CHECKPOINT_CONTRACT),
            "el head persistido por begin", CHECKPOINT_CONTRACT)

        # (b) render de resume: declara el contrato del registro L1 y la
        # proyección expuesta satisface ese schema.
        proc = self.run_resume()
        env = self.write_envelope(proc, "resume")
        rendered = json.dumps(env, ensure_ascii=False)

        self.assertIn(
            RECORD_CONTRACT, rendered,
            msg=f"B1: el render de `resume` declara el contrato del "
                f"registro L1 `{RECORD_CONTRACT}` (decisión B1); hoy "
                f"sólo declara `{CHECKPOINT_CONTRACT}` con una "
                f"`projection` que ningún contrato cubre (probe B); got "
                f"render={rendered[:600]!r}")

        projection = env.get("projection")
        self.assertIsInstance(
            projection, dict,
            msg=f"B1: el render expone la proyección L1 bajo "
                f"`projection`; got keys={sorted(env)!r}")
        self.assert_validates(
            projection, self.load_schema(RECORD_CONTRACT),
            "la proyección L1 expuesta por el render de resume",
            RECORD_CONTRACT)


class TestB2ClasificacionPorPoliticaNoPorToken(ReviewFixProjectCase):
    """B2 (P5) — la política del proyecto es la única fuente de verdad."""

    def test_b02_impl_en_root_declarado_se_oculta_y_doc_declarada_es_visible(
            self) -> None:
        """B2 (decisión del orquestador): el fixture de implementación
        vive bajo un root DECLARADO en la política (`build/`) y se
        oculta a `--role test-writer`; el control negativo
        `docs/impl-decisiones.md` (documentación por política, pese a su
        nombre con `impl`) es VISIBLE — la clasificación proviene de la
        política, no de un token del nombre (review-t1 B2, probe D)."""
        # Los fixtures de referencia EXISTEN antes de que `begin` los
        # registre (un begin con referencia inexistente debe fallar
        # cerrado por P1; el objetivo aquí es la clasificación de rol).
        self.write_text(REF_IMPL_IN_ROOT_REL, IMPL_IN_ROOT_TEXT)
        self.write_text(REF_DOCS_WITH_IMPL_NAME, IMPL_NAME_DOCS_TEXT)
        self.build_valid_project(
            references=[REF_TEST_REL, REF_IMPL_IN_ROOT_REL,
                        REF_DOCS_WITH_IMPL_NAME])

        proc = self.run_resume(role="test-writer")
        env = self.write_envelope(proc, "resume")
        rendered = proc.stdout.decode("utf-8", errors="replace")

        self.assertIn(
            REF_TEST_REL, rendered,
            msg=f"P5/B2 (control positivo): la referencia dentro del "
                f"scope del rol ({REF_TEST_REL!r}) SÍ se expone al "
                f"test-writer")

        self.assertIn(
            REF_DOCS_WITH_IMPL_NAME, rendered,
            msg=f"B2 (control negativo): `{REF_DOCS_WITH_IMPL_NAME}` es "
                f"documentación según la política "
                f"(documentation_roots) y DEBE ser visible para "
                f"test-writer aunque su nombre contenga `impl`; la "
                f"heurística de token la oculta hoy (probe D); got "
                f"render={rendered[:600]!r}")

        self.assertNotIn(
            REF_IMPL_IN_ROOT_REL, rendered,
            msg=f"P5/B2: `{REF_IMPL_IN_ROOT_REL}` vive bajo un root de "
                f"implementación DECLARADO por la política y NUNCA se "
                f"expone a test-writer; got render={rendered[:600]!r}")
        self.assertNotIn(
            "Nota interna de implementación", rendered,
            msg="P5/B2: ni siquiera el CONTENIDO del fixture de "
                "implementación (bajo root declarado) se filtra al rol")

        self.assertIn(
            "test-writer", json.dumps(env, ensure_ascii=False),
            msg="P5: el render declara el rol aplicado (`--role` "
                "sobrevive al repackage)")


class TestO2BeginExigeClaveDeContrato(ReviewFixProjectCase):
    """O2 (P1/P3) — `packet_id` string no vacío y `attempt` entero."""

    def test_o02_begin_sin_packet_id_o_attempt_invalido_falla_cerrado(
            self) -> None:
        """O2 (decisión del orquestador): `begin` con un `--update` sin
        `packet_id` (string no vacío) o sin `attempt` (entero) → rc≠0
        con el CAMPO nombrado en el diagnóstico, y sin persistir nada:
        no queda un head schema-inválido en silencio (probe A) ni se
        pierde la discriminación de la clave P3
        `(execution_id, packet_id, attempt)`."""
        invalid_cases = (
            ("packet_id ausente", "packet_id", {"packet_id": None}),
            ("packet_id vacío", "packet_id", {"packet_id": ""}),
            ("packet_id no-string", "packet_id", {"packet_id": 123}),
            ("attempt ausente", "attempt", {"attempt": None}),
            ("attempt no-entero", "attempt", {"attempt": "1"}),
            ("attempt float", "attempt", {"attempt": 1.5}),
        )
        for name, field, overrides in invalid_cases:
            with self.subTest(caso=name):
                self.setUp()
                doc = update_fixture()
                for key, value in overrides.items():
                    if value is None:
                        doc.pop(key, None)
                    else:
                        doc[key] = value
                update_path = self.write_json("fixture/update.json", doc)
                self.exec_context = self.write_json(
                    "fixture/exec.json", exec_context_fixture())

                proc = self.run_write("begin", update_path)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")

                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"O2: `{name}` → rc≠0 (fail-closed, probe A "
                        f"mostró rc=0 con head inválido); got "
                        f"rc={proc.returncode} stdout={out!r} "
                        f"stderr={err!r}")
                self.assertIn(
                    field, out + err,
                    msg=f"O2: el diagnóstico nombra el campo violado "
                        f"(`{field}`); got stdout={out!r} stderr={err!r}")
                self.assertFalse(
                    self.continuity_store(),
                    msg=f"O2: fail-closed — NADA se persiste cuando el "
                        f"update viola el contrato de la clave "
                        f"({name}); store={self.continuity_store()!r}")
                self.assertFalse(
                    (self.root / STATE_REL).exists(),
                    msg="O2/Invariante 1: el CLI nunca escribe "
                        "docs/.cdad-state.json")


if __name__ == "__main__":
    unittest.main()
