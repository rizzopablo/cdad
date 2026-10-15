#!/usr/bin/env python3
"""003-004 T2 review-fix RED — cierres A, B, C, E1, E2 del review-t2.

Contract:
- docs/specs/003-004-context-continuity/spec.md (§2/§3, P1, P3, criterio 2).
- docs/specs/003-004-context-continuity/review-t2.md (hallazgos A, B, C, E).
- docs/specs/003-004-context-continuity/review-t2-decision.md
  (disposición del orquestador: la fuente de verdad de este RED
  review-fix; un test focal por cierre, archivo nuevo).

Un test focal por cierre (packet
003-004-context-continuity-test-writer-red-004):

- **A** (review-t2 A, decisión del orquestador): `expired-authority`
  SIGUE siendo la clasificación dominante, pero la envolvente agrega
  `signals` con el estado del receipt, de la materialización y del
  dispatch; los `unknowns` se preservan SIEMPRE (ya existan, sin
  importar la clasificación). Test: autoridad vencida + receipt válido +
  journal de materialización → `signals` reporta receipt `received`,
  materialización cerrada y el despacho, rc 0; y con receipt ILEGIBLE la
  señal inconclusa viaja en `unknowns[]` aunque la clasificación no sea
  `unknown` (no se puede ocultar el efecto ya aplicado ni el no-fiable).
- **B** (review-t2 B, tratado como requerido por coherencia con B1 de
  T1): NINGÚN render de `resume`, frío o caliente, reclama el contrato
  `continuity-checkpoint-v1`. El render declara SOLO
  `record: active-record-v1` (el checkpoint es el L2 PERSISTIDO, no el
  render; decisión B1 ya tomada en T1). El arranque en frío (sin head)
  devuelve rc 0 con una envolvente que O valida contra el schema que
  declara (`continuity-checkpoint.schema.json`, vía `jsonschema`) O
  declara un estado explícito `no-checkpoint` — jamás un reclamo de
  contrato violado por sus propios nulls (probe del review).
- **C** (review-t2 C): `--packet` y `update.packet_id` pasan por la
  validación de segmento seguro (`_safe_segment`, igual que
  `execution_id`): `--packet "../../x"` → rc≠0; `update.packet_id` con
  traversal o con slash interno → rc≠0 begin/checkpoint, NADA
  persistido (el oráculo de `reconcile` no se puede alimentar desde
  fuera del store; «no se fabrica éxito»).
- **E1** (review-t2 E-1): `decision` NO vacía (vacío = vacío tras
  recorte, misma convención de la suite que `rationale`) → rc≠0 con el
  campo nombrado y NADA persistido; en `begin` Y en `checkpoint`.
- **E2** (review-t2 E-2 / criterio 2): focal de `reconcile` para los
  tres negativos de P1 que solo se testeaban vía `resume`: cadena rota,
  referencia inexistente y digest de referencia alterado → rc≠0 con el
  delta que NOMBRA el elemento violado. (El cuarto negativo, tamper de
  cuerpo, ya tiene su focal de `reconcile` en
  `test_003_004_t2_reconcile.py::TestP1StaleTamperReconcile`.)

Mapeo a postcondiciones: A → P3/§2 señal fiable caso a caso + D4
(co-ocurrencia vencido ∧ efecto aplicado observable); B → §3 contratos
alineados (B1, P1, criterio 4); C → P3 «no se fabrica éxito» + invariante
1; E1 → D11 (decisión+razón, R-B1 sibling); E2 → criterio 2 (los cuatro
negativos de P1, completados vía `reconcile`).

Cambio DECLARADO en tests preexistentes (B): `tests/test_003_004_t1_resume.py`
(new p02 ya no exige el tag `checkpoint:` en el render — el render
declara `record: active-record-v1` y NO reclama
`continuity-checkpoint-v1`; decisión B del orquestador). El head
persistido por `begin`/`checkpoint` (test_003_004_t1_checkpoint.py:293)
SÍ sigue declarando `continuity-checkpoint-v1` legítimamente: decisión B
es sobre renders de `resume`, no sobre el setter L2.

Fixtures: proyecto sintético en tmp (execution context, update, política
y stores 002/004 sembrados como DATOS — plantillas SIMULACIÓN de
`tests/fixtures/003_004`); ningún incidente real; ninguna escritura en
este repo; todas las corridas foreground con stdin cerrado (DEVNULL).

RED hoy (probes del review-t2 sobre GREEN `02bc021`): cada focale
fracasa por el DEFECTO observado en review-t2 (AssertionError que nombra
el elemento violado), nunca por ImportError ni sintaxis: el test no
importa el módulo del CLI y `jsonschema` se importa perezosamente.
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
ASSETS_DIR = REPO_ROOT / "skills" / "cdad-cycle" / "assets"

FEATURE_ID = "003-004-context-continuity"

EXEC_ID = "exec-003-004-t2-reviewfix-red-001"
PACKET_ID = "003-004-context-continuity-implementer-t2-reviewfix-001"

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

CHECKPOINT_CONTRACT = "continuity-checkpoint-v1"
RECORD_CONTRACT = "active-record-v1"

REF_TEST_REL = "fixture/notes.md"
REF_TEXT = "Historia L3 por referencia: state 001, receipts 002.\n"

GOAL = "Reanudar 003-004 sin repetir objetivo ni autorizaciones"
NEXT_ACTION = "Reconciliar antes de cualquier reintento (D6)"
DECISION_TEXT = "Señal preservada en expired-authority"
DECISION_RATIONALE = "A: el orquestador distingue expirado de cerrado"
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
    """Cuerpo D11 válido (forma de T1): packet_id + attempt + contenido."""
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
    """Política de rutas del proyecto (forma `path_policy`, 002/004)."""
    return {
        "path_policy": {
            "documentation_roots": ["docs"],
            "implementation_roots": ["agents", "skills", "scripts",
                                     "sources", "build"],
            "test_roots": ["tests"],
        },
        "schema_version": 1,
    }


def template(name: str) -> str:
    """Texto de la plantilla SIMULACIÓN declarada en tests/fixtures/003_004."""
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def substitute(text: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text


# ---------------------------------------------------------------- helpers


class ReviewFixCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con stores sembrados como DATOS."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t2rf-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())

    # -- construcción del proyecto fixture --------------------------------

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

    def write_bytes(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_update(self, doc: dict, name: str = "update.json") -> Path:
        return self.write_json(f"fixture/{name}", doc)

    def build_valid_project(self, *, chain: bool = False) -> None:
        """Proyecto con head válido (referencia real existente); `chain`
        encadena un segundo eslabón vía `checkpoint` (attempt 2)."""
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())
        self.write_text(REF_TEST_REL, REF_TEXT)
        self.write_json("docs/cdad-policy.json", policy_fixture())
        update_path = self.write_update(update_fixture(
            references=[REF_TEST_REL]))
        self.write_envelope(self.run_write("begin", update_path), "begin")
        if not chain:
            return
        update2_path = self.write_update(
            update_fixture(
                attempt=2,
                goal=GOAL + " (avance)",
                references=[REF_TEST_REL]),
            name="update2.json")
        self.write_envelope(self.run_write("checkpoint", update2_path),
                            "checkpoint")

    # -- seeds (SIMULACIÓN: datos, nunca flujos reales 002/004) ------------

    def seed_part(self) -> bytes:
        """Part staged bajo el inbox del results dir (forma 002)."""
        part_bytes = b"Role report SIMULACION (review-fix T2 de 003-004).\n"
        path = self.root / PART_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(part_bytes)
        return part_bytes

    def seed_dispatch(self) -> None:
        """Registro I8 del despacho (forma 004) como DATO."""
        text = substitute(template("dispatch-dispatched.simulacion.json"), {
            "@EXECUTION_ID@": EXEC_ID,
            "@PACKET_ID@": PACKET_ID,
        })
        self.write_bytes(DISPATCH_REL, text)

    def seed_receipt(self) -> None:
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
        self.write_bytes(RECEIPT_REL, text)
        self.write_json(BUNDLE_REL, {
            "schema_version": 1,
            "execution_id": EXEC_ID,
            "packet_id": PACKET_ID,
            "bundle_sha256": bundle_sha,
            "source": "SIMULACIÓN fixture 003-004 (review-fix T2)",
        })

    def seed_materialization(self) -> None:
        """Journal de materialización de 002 (tarea cerrada) como DATO."""
        part_bytes = self.seed_part()
        target_path = self.root / "fixture/closed-target.md"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text("Target ya cerrado — SIMULACIÓN.\n",
                               encoding="utf-8")
        text = substitute(template("materialization-closed.simulacion.json"), {
            "@EXECUTION_ID@": EXEC_ID,
            "@PACKET_ID@": PACKET_ID,
            "@AUTH_SHA256@": AUTH_SHA,
            "@BUNDLE_SHA256@": hashlib.sha256(
                part_bytes + b"# bundle SIMULACION\n").hexdigest(),
            "@TARGET_SHA256@": hashlib.sha256(
                "Target ya cerrado — SIMULACIÓN.\n"
                .encode("utf-8")).hexdigest(),
        })
        self.write_bytes(MAT_REL, text)

    def seed_receipt_unreadable(self) -> None:
        """Receipt CORIZADO (JSON inválido): señal NO fiable."""
        self.write_bytes(RECEIPT_REL,
                         template("receipt-unreadable.simulacion.json"))

    # -- corridas del CLI ---------------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        """Corrida acotada, stdin cerrado, foreground real (sin background)."""
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P3 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca puede "
                f"colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path) -> (
            subprocess.CompletedProcess):
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_reconcile(self, packet: str = PACKET_ID) -> (
            subprocess.CompletedProcess):
        return self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", packet, "--json")

    def run_resume(self) -> subprocess.CompletedProcess:
        return self.run_cli("resume", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--json")

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str, *, rc_zero: bool = True) -> None:
        """RED: el fracaso debe ser comportamiento ausente o el defecto
        bajo prueba, con mensaje explícito — nunca import ni sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        self.assertNotIn(
            "invalid choice", out + err,
            msg=f"P3: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                "` declarado en §3 (V6) es obligatorio")
        self.assertNotIn(
            "Traceback", err,
            msg=f"P1: `{which}` terminó con traceback stderr={err!r}")
        if rc_zero:
            self.assertEqual(
                proc.returncode, 0,
                msg=f"P1: el comando `{which}` debía terminar rc 0; got "
                    f"rc={proc.returncode} stdout={out!r} stderr={err!r}")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    # -- observación de stores ---------------------------------------------

    def continuity_store(self) -> dict[str, bytes]:
        """Snapshot {rel: bytes} del store de continuity."""
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }

    def head_document(self) -> dict:
        head = self.root / HEAD_REL
        self.assertTrue(
            head.is_file(),
            msg="P1 (precondición): el head inmutable vive en "
                f"`{HEAD_REL}` (superficie fijada en RED, V6)")
        return json.loads(head.read_text(encoding="utf-8"))

    # -- validación de schemas (jsonschema perezoso) ------------------------

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

    def schema_validate_or_shape(self, envelope: dict, schema: dict | None,
                                 label: str, contract_id: str) -> None:
        """B: la envolvente fría que declara `{contract_id}` DEBE validar
        contra su schema. Con `jsonschema` disponible (dependencia de la
        suite) se valida exactamente; sin él, aserciones de forma sobre
        las claves duras del contrato (decisión B del orquestador:
        «jsonschema.validate o, si no hay dependencia, aserciones de
        forma»). Cualquier violación es AssertionError con el delta
        exacto — nunca ValidationError crudo ni ImportError."""
        self.assertIsInstance(
            schema, dict,
            msg=f"B: el contrato `{contract_id}` ({label}) debe tener "
                f"schema en `{ASSETS_DIR.relative_to(REPO_ROOT)}` con "
                f"$id `{contract_id}`")
        try:
            import jsonschema  # perezoso: el RED no falla por ImportError
        except Exception as exc:  # pragma: no cover
            # Fallback de forma (decisión B): claves duras del contrato.
            self.assertEqual(
                1, envelope.get("schema_version"),
                msg=f"B ({label}, forma sin jsonschema: {exc!r}): "
                    "schema_version = 1")
            self.assertIsInstance(
                envelope.get("seq"), int,
                msg=f"B ({label}, forma sin jsonschema): `seq` entero "
                    "(≥1), no null")
            self.assertIsInstance(
                envelope.get("packet_id"), str,
                msg=f"B ({label}, forma sin jsonschema): `packet_id` "
                    "string, no null")
            body_sha = envelope.get("body_sha256")
            self.assertIsInstance(
                body_sha, str, msg=f"B ({label}, forma sin jsonschema): "
                                   "`body_sha256` 64-hex, no null")
            self.assertRegex(
                body_sha, r"^[0-9a-f]{64}$",
                msg=f"B ({label}, forma sin jsonschema): `body_sha256` "
                    "64-hex")
            return
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        errors = sorted(
            validator_cls(schema).iter_errors(envelope), key=str)
        self.assertEqual(
            [],
            [f"{list(e.absolute_path)}: {e.message}" for e in errors],
            msg=f"B: {label} reclama el contrato `{contract_id}` y DEBE "
                "validar contra su schema (o reclamar otro estado); "
                "violaciones: "
                f"{[f'{list(e.absolute_path)}: {e.message}' for e in errors]!r}")


# ---------------------------------------------------------------- tests


class TestASenalesEnExpiredAuthority(ReviewFixCase):
    """A — `expired-authority` dominante + `signals` + `unknowns` siempre."""

    def test_a_expired_authority_reporta_signals_y_preserva_unknowns(
            self) -> None:
        """A (decisión del orquestador): con autoridad vencida la
        clasificación SIGUE siendo `expired-authority` (dominante), pero
        la envolvente agrega `signals` — objeto con el estado del
        receipt, de la materialización y del dispatch — y NUNCA descarta
        los `unknowns`. Sembrado vencido + receipt recibido +
        materialización cerrada → `signals` reporta los tres hechos
        (subTest 1); receipt ILEGIBLE → la señal inconclusa viaja en
        `unknowns[]` NO vacío pese a la clasificación dominante
        (subTest 2). Ambos con rc 0. Hoy el envelope de
        `expired-authority` omite receipt/materialización (sin
        `signals`) y descarta los unknowns salvo clasificación
        `unknown` — RED por la señal perdida de review-t2 A."""
        # subTest 1: vencido ∧ receipt recibido ∧ materialización cerrada.
        with self.subTest(foco="signals-reported"):
            self.setUp()
            self.exec_context = self.exec_context_path_expirado()
            self.seed_dispatch()
            self.seed_receipt()
            self.seed_materialization()

            proc = self.run_reconcile()
            env = self.write_envelope(proc, "reconcile")
            rendered = json.dumps(env, ensure_ascii=False)
            signals = env.get("signals")

            self.assertEqual(
                env.get("classification"), "expired-authority",
                msg=f"A: `expired-authority` sigue siendo la clasificación "
                    f"dominante; got {env.get('classification')!r} "
                    f"(full={env!r})")
            self.assertIsInstance(
                signals, dict,
                msg=f"A: la envolvente agrega el objeto `signals`; got "
                    f"keys={sorted(env)!r} (full={env!r})")
            sig_text = json.dumps(signals, ensure_ascii=False).lower()
            self.assertIn(
                "receipt", sig_text,
                msg=f"A: `signals` reporta el estado del receipt; got "
                    f"{signals!r}")
            self.assertIn(
                "received", sig_text,
                msg=f"A: `signals` reporta la recepción del receipt "
                    f"(estado real: recibido); got {signals!r}")
            self.assertIn(
                "dispatch", sig_text,
                msg=f"A: `signals` reporta el estado del dispatch; got "
                    f"{signals!r}")
            self.assertIn(
                "materializ", sig_text,
                msg=f"A: `signals` reporta el hecho de materialización; "
                    f"got {signals!r}")
            self.assertIn(
                "closed", sig_text,
                msg=f"A: `signals` reporta la materialización CERRADA "
                    f"(journal de 002 = tarea cerrada); got {signals!r}")
            self.assertEqual(
                proc.returncode, 0,
                msg=f"A: el cierre A corre rc 0 (solo AGREGA la señal; "
                    f"no cambia la clasificación); got "
                    f"rc={proc.returncode}")
            # El hecho también es visible en la envolvente completa.
            self.assertIn(
                "receipt", rendered,
                msg=f"A: el envelope menciona el estado del receipt "
                    f"(probe vencido+receipt+mat del review); got "
                    f"render={rendered[:600]!r}")

        # subTest 2: vencido ∧ receipt ilegible → unknowns preservados.
        with self.subTest(foco="unknowns-preserved"):
            self.setUp()
            self.exec_context = self.exec_context_path_expirado()
            self.seed_dispatch()
            self.seed_receipt_unreadable()

            proc = self.run_reconcile()
            env = self.write_envelope(proc, "reconcile")

            self.assertEqual(
                env.get("classification"), "expired-authority",
                msg=f"A: la clasificación dominante no se cambia por el "
                    f"receipt ilegible; got {env.get('classification')!r} "
                    f"(full={env!r})")
            unknowns = env.get("unknowns")
            self.assertIsInstance(
                unknowns, list,
                msg=f"A: los `unknowns` se preservan SIEMPRE (lista); got "
                    f"{unknowns!r} (full={env!r})")
            self.assertTrue(
                unknowns,
                msg=f"A: con receipt ilegible la señal inconclusa NO se "
                    f"descarta aunque la clasificación sea "
                    f"`expired-authority` (decisión A: los unknowns se "
                    f"preservan siempre); got unknowns={unknowns!r} "
                    f"(full={env!r})")
            self.assertEqual(
                proc.returncode, 0, msg="A: rc 0 también en co-ocurrencia")

    def exec_context_path_expirado(self) -> Path:
        """Execution context con delegación HITL vencida (2020)."""
        return self.write_json("fixture/exec.json", exec_context_fixture(
            hitl_delegation={
                "authority_ref": AUTHORITY_REF,
                "expires_on": "2020-01-01",
            }))


class TestBResumeNoReclamaCheckpoint(ReviewFixCase):
    """B — ningún render de `resume` (frío o caliente) reclama el
    contrato `continuity-checkpoint-v1`; declara solo `record`."""

    def test_b_render_de_resume_no_reclama_checkpoint_contract(self) -> None:
        """B (decisión del orquestador, coherente con B1 de T1):
        - Caliente (con head): el render declara SÓLO
          `record: active-record-v1` y NO contiene
          `continuity-checkpoint-v1` (el checkpoint es el L2 persistido;
          su contrato no valida este render — probe del review: tag +
          null.variant violan `additionalProperties: false` / no_op).
        - Frío (sin head): rc 0 (criterio 4 fijado en T2) y la envolvente
          O valida contra el schema que declara
          (`continuity-checkpoint.schema.json`) O declara un estado
          explícito `no-checkpoint` — donde sea, jamás un contrato
          reclamado y violado por sus propios nulls."""
        # --- caliente -----------------------------------------------------
        self.build_valid_project()
        proc = self.run_resume()
        env_hot = self.write_envelope(proc, "resume")
        rendered_hot = json.dumps(env_hot, ensure_ascii=False)

        self.assertNotIn(
            CHECKPOINT_CONTRACT, rendered_hot,
            msg=f"B: el render caliente de `resume` NO reclama "
                f"`{CHECKPOINT_CONTRACT}` (decisión B; el checkpoint es "
                f"el L2 persistido, el render es el registro L1); got "
                f"render={rendered_hot[:600]!r}")
        self.assertIsNone(
            env_hot.get("checkpoint"),
            msg=f"B: el render caliente no lleva la clave `checkpoint`; "
                f"declara solo `record`; got "
                f"{env_hot.get('checkpoint')!r} keys={sorted(env_hot)!r}")
        self.assertEqual(
            env_hot.get("record"), RECORD_CONTRACT,
            msg=f"B: el render declara solo `record: {RECORD_CONTRACT}` "
                f"(decisión B); got {env_hot.get('record')!r} "
                f"(full={env_hot!r})")

        # --- frío (sin head, proyecto recién creado) ----------------------
        self.setUp()
        self.assertFalse(
            (self.root / HEAD_REL).exists(),
            msg="B (precondición del subTest frío): proyecto SIN head")
        proc_cold = self.run_resume()
        self.assert_command_exists(proc_cold, "resume", rc_zero=True)
        env_cold = json.loads(proc_cold.stdout.decode("utf-8"))
        rendered_cold = json.dumps(env_cold, ensure_ascii=False)

        if f'"{CHECKPOINT_CONTRACT}"' in rendered_cold:
            # Rama (a): reclama el contrato → DEBE conformar su schema.
            self.schema_validate_or_shape(
                env_cold, self.load_schema(CHECKPOINT_CONTRACT),
                "la envolvente fría de resume", CHECKPOINT_CONTRACT)
        else:
            # Rama (b): no reclama → estado explícito `no-checkpoint`.
            self.assertIn(
                "no-checkpoint", rendered_cold,
                msg=f"B: la envolvente fría de `resume` declara un "
                    f"estado explícito `no-checkpoint` (decisión B); "
                    f"got render={rendered_cold[:600]!r}")


class TestCPacketSegmentoSeguro(ReviewFixCase):
    """C — `--packet` y `update.packet_id` atraviesan la validación de
    segmento seguro (igual que `execution_id`)."""

    def test_c_packet_traversal_y_update_packet_id_fallan_cerrado(
            self) -> None:
        """C (decisión del orquestador): ningún packet_id incumplidor
        llega al store ni al results dir: `reconcile --packet
        "../../x"` → rc≠0 (probe del review: hoy rc 0 y el receipt se
        lee FUERA del store — oráculo alimentable); `begin`/`checkpoint`
        con `update.packet_id` con traversal o con slash interno → rc≠0
        con el campo nombrado y NADA persistido («no se fabrica
        éxito»)."""
        traversal_values = ("../../x", "..", "a/b")
        for bad in traversal_values:
            # -- reconcile con --packet incumplidor → rc≠0 ---------------
            with self.subTest(foco="reconcile", packet=bad):
                self.setUp()
                update = self.write_update(update_fixture())
                self.write_envelope(self.run_write("begin", update), "begin")
                head_bytes_before = (
                    self.root / HEAD_REL).read_bytes()

                proc = self.run_reconcile(packet=bad)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"C: `reconcile --packet {bad!r}` falla cerrado "
                        f"(rc≠0; el packet_id DEBE validar segmento "
                        f"seguro; probe del review: rc 0 lee el receipt "
                        f"fuera del store); got rc={proc.returncode} "
                        f"stdout={out!r} stderr={err!r}")
                self.assertEqual(
                    (self.root / HEAD_REL).read_bytes(), head_bytes_before,
                    msg=f"C: el fallo del packet incumplidor NO toca el "
                        f"store (read-only, invariante 1)")

            # -- update.packet_id incumplidor → rc≠0, NADA persistido ----
            with self.subTest(foco="begin", packet=bad):
                self.setUp()
                bad_update = self.write_update(
                    update_fixture(packet_id=bad))
                proc = self.run_write("begin", bad_update)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"C: `begin` con `update.packet_id == {bad!r}` "
                        f"falla cerrado (rc≠0; O2 valida pero el segmento "
                        f"seguro se extiende a packet_id, decisión C); "
                        f"got rc={proc.returncode} stdout={out!r} "
                        f"stderr={err!r}")
                self.assertIn(
                    "packet_id", out + err,
                    msg=f"C: el diagnóstico nombra el campo violado "
                        f"(`packet_id`); got stdout={out!r} stderr={err!r}")
                self.assertFalse(
                    self.continuity_store(),
                    msg=f"C: NADA persistido para `update.packet_id == "
                        f"{bad!r}` (fail-closed: sin head ni body); "
                        f"store={self.continuity_store()!r}")
                # El write-ahead posterior comparte el mismo guard.
                proc_ckpt = self.run_write("checkpoint", bad_update)
                self.assertNotEqual(
                    proc_ckpt.returncode, 0,
                    msg=f"C: `checkpoint` también rechaza `packet_id == "
                        f"{bad!r}`; got rc={proc_ckpt.returncode} "
                        f"stdout={proc_ckpt.stdout!r}")


class TestEDecisionNoVacia(ReviewFixCase):
    """E1 — `decision` no vacía (hermana de la exigencia de `rationale`)."""

    def test_e1_decision_vacia_falla_cerrado_en_begin_y_checkpoint(
            self) -> None:
        """E1 (decisión del orquestador): hoy `_require_content_fields`
        admite `decision: ""` mientras exige `rationale` no vacía
        (review-t2 E-1); D11 exige «decision+razón», así que `decision`
        vacía (vacío tras recorte: "" y "   ", misma convención de
        rationale) → rc≠0 en `begin` Y en `checkpoint`, campo nombrado y
        NADA persistido."""
        empty_values = ("", "   ")
        for value in empty_values:
            with self.subTest(decision=repr(value)):
                self.setUp()
                bad_update = self.write_update(update_fixture(
                    decisions=[{"decision": value,
                                "rationale": DECISION_RATIONALE}]))
                proc = self.run_write("begin", bad_update)
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"E1: `begin` con `decision == {value!r}` falla "
                        f"cerrado (rc≠0; D11 exige decision+razón, "
                        f"review-t2 E-1); got rc={proc.returncode} "
                        f"stdout={out!r} stderr={err!r}")
                self.assertIn(
                    "decision", out + err,
                    msg=f"E1: el diagnóstico nombra el campo violado "
                        f"(`decision`); got stdout={out!r} stderr={err!r}")
                self.assertFalse(
                    self.continuity_store(),
                    msg=f"E1: NADA persistido con `decision {value!r}` "
                        f"(fail-closed); store={self.continuity_store()!r}")

                proc_ckpt = self.run_write("checkpoint", bad_update)
                self.assertNotEqual(
                    proc_ckpt.returncode, 0,
                    msg=f"E1: `checkpoint` también rechaza `decision == "
                        f"{value!r}`; got rc={proc_ckpt.returncode} "
                        f"stdout={proc_ckpt.stdout!r}")


class TestE2ReconcileNegativosP1(ReviewFixCase):
    """E2 — los 3 negativos de P1 restantes, vía `reconcile` (criterio 2)."""

    def test_e2_reconcile_detecta_cadena_rota_referencia_inexistente_y_digest(
            self) -> None:
        """E2 (criterio 2, review-t2 E-2): de los cuatro negativos de P1
        solo el tamper de cuerpo tenía focal vía `reconcile`
        (TestP1StaleTamperReconcile); los otros tres corren los mismos
        `_verify_*` desde `reconcile` pero solo se testeaban vía
        `resume`. Este focale los cubre: cadena rota, referencia
        inexistente y digest de referencia alterado → rc≠0 con el delta
        que NOMBRA el elemento violado."""
        cases = (
            ("cadena-rota", "prev_checkpoint_sha256"),
            ("referencia-inexistente", REF_TEST_REL),
            ("digest-referencia-alterado", REF_TEST_REL),
        )
        for name, needle in cases:
            with self.subTest(negativo=name):
                self.setUp()
                self.build_valid_project(chain=True)
                head = self.head_document()
                self.assertEqual(
                    head.get("seq"), 2,
                    msg="E2 (precondición): la cadena tiene 2 eslabones "
                        "para poder romperse")
                digest_real = hashlib.sha256(
                    REF_TEXT.encode("utf-8")).hexdigest()
                self.assertEqual(
                    head["references"][-1]["sha256"], digest_real,
                    msg="E2 (precondición): la referencia viaja con el "
                        "digest real del contenido")

                if name == "cadena-rota":
                    head["prev_checkpoint_sha256"] = "1" * 64
                elif name == "referencia-inexistente":
                    (self.root / REF_TEST_REL).unlink()
                else:  # digest-referencia-alterado
                    self.write_text(REF_TEST_REL, REF_TEXT + "tamper\n")
                self.write_json(HEAD_REL, head)
                tampered_head_bytes = (self.root / HEAD_REL).read_bytes()

                proc = self.run_reconcile()
                out = proc.stdout.decode("utf-8", errors="replace")
                err = proc.stderr.decode("utf-8", errors="replace")
                combined = out + err

                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"E2/criterio 2: `reconcile` detecta el negativo "
                        f"`{name}` y falla cerrado (rc≠0); got "
                        f"rc={proc.returncode} stdout={out!r} "
                        f"stderr={err!r}")
                self.assertIn(
                    needle, combined,
                    msg=f"E2/criterio 2: el delta exacto de `reconcile` "
                        f"nombra el elemento violado ({needle!r}) para "
                        f"`{name}`; got stdout={out!r} stderr={err!r}")
                self.assertEqual(
                    (self.root / HEAD_REL).read_bytes(), tampered_head_bytes,
                    msg=f"E2: `reconcile` NO repara el tamper `{name}` "
                        "(read-only: el head alterado permanece para el "
                        "orquestador)")


if __name__ == "__main__":
    unittest.main()
