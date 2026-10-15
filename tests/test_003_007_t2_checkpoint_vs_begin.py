#!/usr/bin/env python3
"""003-007 T2 RED — `checkpoint` distinto de `begin` (P5, P6), el
discriminador de legado por ausencia de `record` (O-1) y la abstención
aceptada de `reconcile` tras un append (plan.md T2 / spec.md §3).

Contract:
- docs/specs/003-007-living-continuity/spec.md (P5 T4-CKPT, P6 integridad
  de cadena, §3 Envolventes `record`, D5, D6+O-1 de review-t1-decision.md;
  criterios de aceptación 5 y 10).
- docs/specs/003-007-living-continuity/plan.md (T2; focales declarados:
  este archivo + tests/test_003_006_t4_ru2_refused_write.py +
  tests/test_003_004_t2_writeahead.py; escenario de la abstención
  aceptada de review-draft-001-decision.md).
- docs/specs/003-007-living-continuity/review-t1-decision.md (O-1: entra
  en T2 — un body es legado SOLO si no tiene `record`).
- docs/specs/003-007-living-continuity/review-draft-001.md (abstención:
  "Comportamiento de `reconcile` bajo P5 con clave del packet viejo tras
  un append … el plan debería cubrirlo en el RED de T2").

Superficie observable bajo prueba (§3 — misma firma; V6 de 003-004 se
mantiene):

    python3 scripts/cdad_continuity.py begin      --project-root ROOT \
        --execution-context EXEC.json --update UPDATE.json [--json]
    python3 ... checkpoint --project-root ROOT --execution-context \
        EXEC.json --update UPDATE.json [--json]
    python3 ... reconcile  --project-root ROOT --execution-context \
        EXEC.json --packet PACKET_ID [--json]
    python3 ... resume     --project-root ROOT --execution-context \
        EXEC.json [--json]

Decisiones de superficie fijadas por este RED (declaradas para el
GREEN/reviewer):

S1 (P5, oración 1): un `checkpoint` con la clave del head
    `(execution_id, packet_id, attempt)` y cuerpo distinto se APENDEA
    como eslabón nuevo: rc 0, `seq` = head.seq + 1,
    `prev_checkpoint_sha256` = `body_sha256` del head previo,
    `body_sha256` nuevo, `attempt`/`packet_id` sin cambiar, y el
    eslabón previo PERMANECE en `bodies/` (evidencia intacta);
    `head.json` refleja la envolvente del eslabón nuevo. HOY el
    checkpoint misma-key se RECHAZA (split-brain, rc=1) → RED.
S2 (P5, oración 2): un `begin` divergente con la misma clave sigue
    fallando cerrado (despacho duplicado): rc≠0 nombrando
    `split-brain`, store byte-a-byte intacto y `reconcile` posterior
    sin split-brain (RU-2, faceta begin — intacta por BL-2).
S3 (P6): un `checkpoint` re-ejecutado con cuerpo idéntico (mismo
    `--update`, misma clave del eslabón que él mismo creó) es no-op:
    rc 0, `no_op: true`, store byte-a-byte intacto, `seq` estable.
S4 (P6 + §3 Envolventes): `record` viaja en el body (del checkpoint) y
    en el sobre. Se aserta: envolvente de `begin` → `record: "begin"`;
    envolvente de `checkpoint` (stdout y `head.json`) →
    `record: "checkpoint"`; body file del checkpoint (`bodies/<sha>.json`)
    → `record: "checkpoint"`. El body de BEGIN: la spec (D5) fija el
    `record` sólo para el body de checkpoint ("Body de checkpoint gana
    `record`") → NO se aserta ni presencia ni ausencia en el body de
    begin (sin sobre-especificación; `_detect_split_brain` cuenta
    `record != "checkpoint"`, que cubre ambas formas). Nota: la clave
    `record` de la envolvente de `resume` ("active-record-v1") es OTRO
    contrato y no se toca.
S5 (P6): `_detect_split_brain` sigue detectando ≥2 bodies con
    `record != "checkpoint"` por clave (huérfanos sin record sembrados
    como fixture de datos, forma pre-RU-2): rc≠0, `split-brain` nombrado
    y el digest divergente citado, sin borrar evidencia.
S6 (P5/abstención aceptada): `reconcile --packet` sobre un store
    post-append (sembrado como fixture de datos: eslabón begin + eslabón
    checkpoint con la MISMA clave, head en el checkpoint) rinde rc 0,
    `classification != "split-brain"`, `escalate: false` y SIN el error
    `divergent checkpoint heads`. La clasificación EXACTA no se fija
    (abstención aceptada — el observable es NO escalar un encadenado
    legítimo). HOY: rc=1 split-brain ("divergent checkpoint heads") → RED.
S7 (O-1, review-t1-decision.md + P7/D6): el discriminador de legado es
    la AUSENCIA de `record` en el body — un body CON `record` cuya
    referencia no trae `class` se trata como `contract` (P3): su cambio
    BLOQUEA (rc≠0 citando path y el digest congelado); control: body SIN
    `record` con la misma referencia sin class sigue siendo legado por
    comparación (rc 0, `legacy: true`, `state: changed`) — el fixture
    tests/fixtures/003-007-legacy-store/ y los tests P7 de T1 NO cambian.
S8 (V5, review-draft-001.md — abstención que queda para el RED): un
    update realista (goal, decisiones con rationale, uncertezas, ~10
    referencias como objetos con `class` y una con `fields`) se
    checkpointea bajo el default de 16 KiB: rc 0, `bytes <= max_bytes`,
    sin truncamiento (el margen de `record`+`class` ≈30 bytes/referencia
    se mide aquí por comportamiento).

Cobertura (un test por postcondición/decisión, cada uno la NOMBRA):

- P5  test_p05_*: append misma-key (S1) + begin divergente sigue
      cerrado (S2) + reconcile tras append sin escalar (S6).
- P6  test_p06_*: no-op idéntico (S3) + `record` en body y envolvente
      (S4) + split-brain para ≥2 bodies sin record (S5).
- O-1 test_o01_*: discriminador de legado por ausencia de `record`
      (S7), con control legado.
- V5  test_v05_*: headroom 16 KiB con `record`+`class` (S8).

Regresión declarada (BL-2, plan T2): la faceta `checkpoint` de
tests/test_003_006_t4_ru2_refused_write.py fue reescrita por este RED
para exigir el append (P5) con trazabilidad en su docstring; la faceta
`begin` divergente y el todo-o-nada de ese archivo quedan INTACTOS.

Fixtures: proyecto sintético y stores en tmp (autocontenidos, corridos
con `env -u TMPDIR`); los stores post-append/legado que el CLI aún no
produce se SIEMBRAN como datos (nombre del body = sha256 de sus bytes,
head.json consistente — misma convención content-addressed que el
store real, precedent: la siembra del cuerpo divergente en
tests/test_003_004_t2_reconcile.py D7); NUNCA los stores reales de
`.cdad/` del repo; stdin cerrado (DEVNULL), foreground SIEMPRE (nunca
background); el repo no recibe ninguna escritura del test.

RED (paquete): corre SOLO este archivo + el RU-2 reescrito:
    env -u TMPDIR python3 -m pytest -q \
        tests/test_003_007_t2_checkpoint_vs_begin.py \
        tests/test_003_006_t4_ru2_refused_write.py < /dev/null
Focales de regresión (verdes constantes):
    tests/test_003_007_t1_reference_classes.py tests/test_003_004_*.py
La suite completa NO se corre (acotado). Nunca background.
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

FEATURE_ID = "003-007-living-continuity"
EPIC_ID = "epic-003-context-efficiency"

EXEC_ID = "exec-003-007-t2-red-001"
PACKET_ID = "003-007-living-continuity-implementer-t2-red-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

# Tope duro: un CLI determinista nunca puede colgarse (acotado).
CLI_TIMEOUT_S = 120

# Cap por defecto declarado en la spec (V5/P7 de 003-004 se mantiene).
DEFAULT_MAX_BYTES = 16 * 1024

CONTINUITY_DIR_REL = f".cdad/executions/{EXEC_ID}/continuity"
BODIES_DIR_REL = f"{CONTINUITY_DIR_REL}/bodies"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"

REF_LIVING_LEDGER_REL = "fixture/work-ledger.md"
LIVING_LEDGER_TEXT = "Ledger vivo: rotacion de T2 registrada.\n"

GOAL_BEGIN = "T2 de 003-007: checkpoint distinto de begin (objetivo inicial)"
GOAL_CHECKPOINT = ("T2 de 003-007: checkpoint de limite con la clave del "
                   "begin (eslabon nuevo, P5)")
NEXT_ACTION = "Continuar el encargo con la cadena enlazada"
DECISION_TEXT = "Checkpoint con la clave del head apendea, no se rechaza"
DECISION_RATIONALE = "P5/D5 de la spec 003-007 (T4-CKPT)"
UNCERTAINTY = "V5: headroom 16 KiB con record+class medido en este RED"


# ---------------------------------------------------------------- fixtures


def exec_context_fixture(**extra: object) -> dict:
    """Execution context mínimo (forma plana de 001, forma T1 de
    003-004 reutilizada por el T1 GREEN de 003-007)."""
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


def state_doc_fixture() -> dict:
    """`docs/.cdad-state.json` sintético con autoridad (D1) + progreso."""
    return {
        "schema_version": 1,
        "hitl_delegation": {
            "delegated_to": "orchestrator",
            "requested_by": "user (pablo)",
            "requested_at": "2026-10-08T00:00:00Z",
            "scope": EPIC_ID,
            "expires": "vence por eventos; valida la vigencia en prepare",
            "publication": "docs/specs/003-007-living-continuity/spec.md",
            "source": AUTHORITY_REF,
        },
        "approver": "orchestrator (HITL delegation epic-003)",
        "execution": {
            "id": EXEC_ID,
            "packet_id": PACKET_ID,
            "scope": EPIC_ID,
        },
        "stage_history": [
            {"stage": 3, "substage": "red", "feature_id": FEATURE_ID},
        ],
        "active_packet": PACKET_ID,
    }


def policy_fixture() -> dict:
    """Política de rutas del proyecto (forma 002/004 reutilizada)."""
    return {
        "path_policy": {
            "documentation_roots": ["docs"],
            "implementation_roots": ["agents", "skills", "scripts",
                                     "sources", "build"],
            "test_roots": ["tests"],
        },
        "schema_version": 1,
    }


def update_fixture(**overrides: object) -> dict:
    """Contenido D11 del cuerpo (forma fijada por 003-004 T1/T2)."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": GOAL_BEGIN,
        "decisions": [
            {"decision": DECISION_TEXT, "rationale": DECISION_RATIONALE},
        ],
        "uncertainties": [UNCERTAINTY],
        "next_action": NEXT_ACTION,
        "references": [],
    }
    doc.update(overrides)
    return doc


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ------------------------------------------------------------ store sembrado


def canonical_body_bytes(doc: dict) -> bytes:
    """Bytes canónicos del body file (convención content-addressed
    observada en el store real: sort_keys + separadores compactos)."""
    return json.dumps(doc, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def seeded_body_doc(goal: str, references: list, *,
                    record: str | None = None, attempt: int = 1) -> dict:
    """Documento de body sintético con la forma del store real
    (mirrors del body del fixture legado) + `record` opcional."""
    doc = {
        "schema_version": 1,
        "execution_id": EXEC_ID,
        "packet_id": PACKET_ID,
        "attempt": attempt,
        "goal": goal,
        "decisions": [
            {"decision": DECISION_TEXT, "rationale": DECISION_RATIONALE},
        ],
        "uncertainties": [UNCERTAINTY],
        "next_action": NEXT_ACTION,
        "references": references,
        "authority": {
            "authority_ref": AUTHORITY_REF,
            "expires_on": "2099-12-31",
        },
    }
    if record is not None:
        doc["record"] = record
    return doc


def seed_chain(root: Path, links: list[tuple[dict, int]]) -> dict:
    """Siembra una cadena en `continuity/` como DATOS: cada eslabón es un
    body content-addressed (`bodies/<sha256(bytes)>.json`) y `head.json`
    es la envolvente del ÚLTIMO eslabón (seq/prev encadenados). Devuelve
    el head sembrado. El head porta `record` cuando el body lo porta
    (P6: `record` viaja en el body y en el sobre)."""
    shas: list[str] = []
    for doc, _seq in links:
        raw = canonical_body_bytes(doc)
        sha = sha256_of(raw)
        shas.append(sha)
        body_path = root / BODIES_DIR_REL / f"{sha}.json"
        body_path.parent.mkdir(parents=True, exist_ok=True)
        body_path.write_bytes(raw)

    head: dict = {}
    prev: str | None = None
    for (doc, seq), sha in zip(links, shas):
        head = {
            "schema_version": 1,
            "checkpoint": "continuity-checkpoint-v1",
            "execution_id": EXEC_ID,
            "packet_id": PACKET_ID,
            "attempt": doc.get("attempt", 1),
            "seq": seq,
            "body_sha256": sha,
            "prev_checkpoint_sha256": prev,
            "references": doc.get("references", []),
            "bytes": len(canonical_body_bytes(doc)),
            "max_bytes": DEFAULT_MAX_BYTES,
            "no_op": False,
        }
        if "record" in doc:
            head["record"] = doc["record"]
        prev = sha
    head_path = root / HEAD_REL
    head_path.parent.mkdir(parents=True, exist_ok=True)
    head_path.write_text(json.dumps(head, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    return head


# ---------------------------------------------------------------- helpers


def find_reference_report(node: object, rel: str) -> dict | None:
    """Busca recursivamente la entrada de reporte de la referencia
    `rel` (el observable es la ENTRADA, no su camino en el árbol —
    misma convención que el T1 GREEN)."""
    if isinstance(node, dict):
        if (node.get("path") == rel and "state" in node
                and "sha256" in node):
            return node
        for value in node.values():
            found = find_reference_report(value, rel)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_reference_report(value, rel)
            if found is not None:
                return found
    return None


class CheckpointVsBeginCase(unittest.TestCase):
    """Proyecto sintético en tmp con stores de continuity PROPIOS."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-007-t2ck-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.exec_context = self.write_json("fixture/exec.json",
                                            exec_context_fixture())

    # -- construcción del proyecto fixture -----------------------------

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

    def write_update(self, doc: dict, name: str = "update.json") -> Path:
        return self.write_json(f"fixture/{name}", doc)

    def write_state(self, doc: dict) -> Path:
        return self.write_json(STATE_REL, doc)

    def build_project(self, references: list) -> dict:
        """Sistema base: policy + referencias existentes + begin rc 0."""
        self.write_json(POLICY_REL, policy_fixture())
        self.write_text(REF_LIVING_LEDGER_REL, LIVING_LEDGER_TEXT)
        self.write_state(state_doc_fixture())
        return self.begin_env(references)

    # -- corridas del CLI ----------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        """Foreground SIEMPRE, stdin cerrado (nunca background, nunca
        pregunta interactiva), tope duro de tiempo."""
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "acotado: el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca puede "
                f"colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path,
                  ) -> subprocess.CompletedProcess:
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")

    def run_resume(self) -> subprocess.CompletedProcess:
        return self.run_cli("resume", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--json")

    def combined_output(self, proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout.decode("utf-8", errors="replace")
                + proc.stderr.decode("utf-8", errors="replace"))

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser comportamiento ausente/incorrecto con
        mensaje explícito — nunca import, sintaxis o traceback."""
        combined = self.combined_output(proc)
        self.assertNotIn(
            "invalid choice", combined,
            msg=f"RED: el comando `{which}` no existe aún (CLI ausente): "
                "el argv `cdad_continuity.py " + which +
                "` declarado en §3 es obligatorio")
        self.assertNotIn(
            "Traceback", combined,
            msg=f"RED: `{which}` terminó con traceback sin manejar "
                f"(stderr={combined!r})")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"RED (precondición de `{which}`): rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        return json.loads(proc.stdout.decode("utf-8"))

    def begin_env(self, references: list) -> dict:
        update = self.write_update(update_fixture(references=references))
        return self.write_envelope(self.run_write("begin", update), "begin")

    def head_document(self) -> dict:
        head = self.root / HEAD_REL
        self.assertTrue(
            head.is_file(),
            msg="precondición: el head vive en "
                f"`{HEAD_REL}` (superficie fijada en RED, V6)")
        return json.loads(head.read_text(encoding="utf-8"))

    def body_file_of(self, body_sha: str) -> Path:
        path = self.root / BODIES_DIR_REL / f"{body_sha}.json"
        self.assertTrue(
            path.is_file(),
            msg=f"precondición: el body content-addressed vive en "
                f"`{BODIES_DIR_REL}/{body_sha}.json`")
        return path

    def continuity_files(self) -> dict[str, bytes]:
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }

    def continuity_dirs(self) -> set[str]:
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return set()
        return {str(p.relative_to(base))
                for p in sorted(base.rglob("*")) if p.is_dir()}


# ---------------------------------------------------------------- tests


class TestP5CheckpointAppend(CheckpointVsBeginCase):
    """P5 (oración 1, T4-CKPT) — el checkpoint con la clave del head se
    APENDEA como eslabón nuevo, no se rechaza como split-brain."""

    def test_p05_checkpoint_misma_clave_apendea_eslabon_nuevo(self) -> None:
        """P5: `begin` (attempt 1); luego `checkpoint` con la MISMA clave
        `(packet_id, attempt)` y cuerpo distinto → rc 0 y APENDEA:
        `seq` crece exactamente 1, `prev_checkpoint_sha256` =
        body_sha256 del head previo, `body_sha256` nuevo (no reusa el
        eslabón), el eslabón previo permanece en `bodies/` y `head.json`
        refleja la envolvente del eslabón nuevo.

        RED hoy: el checkpoint misma-key con cuerpo distinto se RECHAZA
        como split-brain (rc=1, "refusing to overwrite the head") → el
        fracaso es comportamiento presente-incorrecto (AssertionError
        que nombra P5), nunca import ni sintaxis."""
        env1 = self.build_project([
            {"path": REF_LIVING_LEDGER_REL, "class": "living"}])
        head1 = self.head_document()
        self.assertEqual(
            (head1.get("seq"), head1.get("attempt")), (1, 1),
            msg="P5 (precondición): el head arranca con seq 1 y la clave "
                "en juego tiene attempt 1")
        body_a = head1.get("body_sha256")
        before = self.continuity_files()

        update2 = self.write_update(
            update_fixture(goal=GOAL_CHECKPOINT),  # misma clave, otro body
            name="update-checkpoint.json")
        proc = self.run_write("checkpoint", update2)
        self.assert_command_exists(proc, "checkpoint")

        combined = self.combined_output(proc)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P5: un `checkpoint` con la clave del head y cuerpo "
                f"distinto se APENDEA como eslabón nuevo (rc 0) — NO se "
                f"rechaza como split-brain; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

        env2 = json.loads(proc.stdout.decode("utf-8"))
        self.assertEqual(
            env2.get("seq"), head1.get("seq", 0) + 1,
            msg=f"P5: el eslabón apendeado lleva `seq` = head.seq + 1 "
                f"({head1.get('seq', 0) + 1}); got {env2.get('seq')!r}")
        self.assertEqual(
            env2.get("prev_checkpoint_sha256"), body_a,
            msg=f"P5: `prev_checkpoint_sha256` del eslabón nuevo es el "
                f"BODY del head previo ({body_a!r}); got "
                f"{env2.get('prev_checkpoint_sha256')!r}")
        self.assertNotEqual(
            env2.get("body_sha256"), body_a,
            msg="P5: el eslabón nuevo tiene body_sha256 PROPIO "
                "(content-addressed), no reusa el eslabón previo")
        self.assertEqual(
            (env2.get("packet_id"), env2.get("attempt")),
            (PACKET_ID, 1),
            msg=f"P5: el eslabón apendeado CONSERVA la clave del head "
                f"(packet_id={PACKET_ID!r}, attempt=1); got "
                f"{(env2.get('packet_id'), env2.get('attempt'))!r}")

        # head.json refleja la envolvente del eslabón nuevo.
        head2 = self.head_document()
        head2_keys = {k: head2.get(k) for k in
                      ("seq", "body_sha256", "prev_checkpoint_sha256")}
        self.assertEqual(
            (head2.get("seq"), head2.get("body_sha256"),
             head2.get("prev_checkpoint_sha256")),
            (env2.get("seq"), env2.get("body_sha256"),
             env2.get("prev_checkpoint_sha256")),
            msg=f"P5: `head.json` refleja el eslabón apendeado (seq/prev/"
                f"body); got head={head2_keys!r}")

        # el eslabón previo permanece en bodies/ (evidencia intacta).
        after = self.continuity_files()
        prev_rel = f"bodies/{body_a}.json"
        self.assertIn(
            prev_rel, after,
            msg=f"P5: el eslabón previo ({prev_rel!r}) permanece en "
                f"`bodies/` tras el append (evidencia intacta)")
        self.assertEqual(
            after.get(prev_rel), before.get(prev_rel),
            msg="P5: el eslabón previo queda byte a byte intacto")


class TestP5BeginDivergenteSigueCerrado(CheckpointVsBeginCase):
    """P5 (oración 2) — el `begin` divergente con la misma clave sigue
    fallando cerrado (despacho duplicado; RU-2 begin facet intacta)."""

    def test_p05_begin_divergente_misma_clave_sigue_cerrado(self) -> None:
        """P5: `begin` válido; `begin` DIVERGENTE con la MISMA clave →
        rc≠0 nombrando `split-brain`, el store de continuity queda
        byte-a-byte intacto (todo-o-nada RU-2) y `reconcile --packet`
        posterior NO da split-brain."""
        self.build_project([])
        head_before = (self.root / HEAD_REL).read_bytes()
        before = self.continuity_files()
        dirs_before = self.continuity_dirs()
        self.assertIn(
            "bodies", dirs_before,
            msg="P5 (precondición): el begin válido creó `bodies/`")

        divergent = self.write_update(
            update_fixture(
                goal="VARIANTE divergente del MISMO attempt 1 (sesión "
                     "bifurcada simulada — fixture de datos)"),
            name="update-divergente.json")
        proc = self.run_write("begin", divergent)
        self.assert_command_exists(proc, "begin")

        combined = self.combined_output(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P5: un `begin` divergente con la misma clave sigue "
                f"fallando cerrado (rc≠0, despacho duplicado); got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertIn(
            "split-brain", combined,
            msg=f"P5: el rechazo del begin divergente nombra el conflicto "
                f"(split-brain); got {combined[:400]!r}")
        self.assertEqual(
            self.continuity_files(), before,
            msg="P5/RU-2 (todo o nada): el begin divergente RECHAZADO no "
                "escribe nada — el store queda byte a byte igual")
        self.assertEqual(
            self.continuity_dirs(), dirs_before,
            msg="P5/RU-2: el rechazo no crea directorios nuevos")
        self.assertEqual(
            (self.root / HEAD_REL).read_bytes(), head_before,
            msg="P5/RU-2: el head queda byte a byte intacto")

        proc_recon = self.run_reconcile()
        self.assert_command_exists(proc_recon, "reconcile")
        self.assertEqual(
            proc_recon.returncode, 0,
            msg=f"P5: tras el rechazo todo-o-nada, `reconcile --packet` "
                f"NO queda bloqueado en split-brain (rc=0); got "
                f"rc={proc_recon.returncode}")
        env_recon = json.loads(proc_recon.stdout.decode("utf-8"))
        self.assertNotEqual(
            env_recon.get("classification"), "split-brain",
            msg=f"P5: la clasificación NO es split-brain; got "
                f"{env_recon.get('classification')!r}")


class TestP6CheckpointIdenticoNoop(CheckpointVsBeginCase):
    """P6 — un `checkpoint` re-ejecutado con cuerpo idéntico es no-op."""

    def test_p06_checkpoint_identico_re_ejecutado_es_noop(self) -> None:
        """P6: `begin` (attempt 1); `checkpoint` (attempt 2, cuerpo
        nuevo); RE-ejecutar el MISMO `checkpoint` (mismo `--update`,
        misma clave del eslabón que él mismo creó) → rc 0, `no_op:
        true`, el store de continuity queda byte-a-byte intacto y `seq`
        estable (no se apendea un duplicado).

        Este no-op DEBE sobrevivir al GREEN aunque el body gane
        `record`: la re-ejecución byte-idéntica nunca se convierte en
        eslabón nuevo."""
        self.build_project([
            {"path": REF_LIVING_LEDGER_REL, "class": "living"}])
        update2 = self.write_update(
            update_fixture(attempt=2, goal=GOAL_CHECKPOINT),
            name="update-ckpt2.json")
        env2 = self.write_envelope(self.run_write("checkpoint", update2),
                                   "checkpoint")
        self.assertEqual(
            env2.get("seq"), 2,
            msg="P6 (precondición): el checkpoint de avance encadena seq 2")
        before = self.continuity_files()

        proc3 = self.run_write("checkpoint", update2)
        env3 = self.write_envelope(proc3, "checkpoint")

        self.assertIs(
            env3.get("no_op"), True,
            msg=f"P6: el `checkpoint` re-ejecutado con cuerpo idéntico es "
                f"no-op (`no_op: true`); got {env3.get('no_op')!r}")
        self.assertEqual(
            env3.get("seq"), env2.get("seq"),
            msg=f"P6: el no-op devuelve el eslabón existente (misma seq "
                f"{env2.get('seq')!r}), no uno nuevo; got "
                f"{env3.get('seq')!r}")
        self.assertEqual(
            self.continuity_files(), before,
            msg="P6: el no-op NO escribe: el store de continuity queda "
                "byte a byte idéntico (sin eslabón duplicado)")


class TestP6RecordEnBodyYEnvolvente(CheckpointVsBeginCase):
    """P6 + §3 Envolventes — `record` viaja en el body (checkpoint) y en
    el sobre; begin envolvente `record: "begin"`."""

    def test_p06_record_viaja_en_body_y_envolvente(self) -> None:
        """P6/§3 (D5): los escritores nuevos EMITEN `record`. Se aserta
        (encadenado normal attempt 1 → attempt 2, que ya funciona):
        (a) envolvente de `begin` → `record: "begin"`; (b) envolvente de
        `checkpoint` (stdout) → `record: "checkpoint"`; (c) `head.json`
        (el sobre persistido) → `record: "checkpoint"`; (d) el body file
        del checkpoint (`bodies/<body_sha256>.json`) →
        `record: "checkpoint"`. El body de BEGIN no se aserta: D5 fija
        el `record` sólo para el body de checkpoint (S4 — sin
        sobre-especificar la forma no fijada).

        RED hoy: la envolvente no lleva `record` (None) y el body file
        tampoco → AssertionError que nombra el campo ausente."""
        env1 = self.build_project([
            {"path": REF_LIVING_LEDGER_REL, "class": "living"}])
        self.assertEqual(
            env1.get("record"), "begin",
            msg=f"P6/§3: la envolvente de `begin` gana `record` con el "
                f"valor `begin` (los escritores nuevos lo emiten); got "
                f"{env1.get('record')!r}")

        update2 = self.write_update(
            update_fixture(attempt=2, goal=GOAL_CHECKPOINT),
            name="update-ckpt2.json")
        env2 = self.write_envelope(self.run_write("checkpoint", update2),
                                   "checkpoint")
        self.assertEqual(
            env2.get("record"), "checkpoint",
            msg=f"P6/§3: la envolvente de `checkpoint` lleva "
                f"`record: \"checkpoint\"`; got {env2.get('record')!r}")

        head = self.head_document()
        self.assertEqual(
            head.get("record"), "checkpoint",
            msg=f"P6 (el sobre): `head.json` persiste `record: "
                f"\"checkpoint\"`; got {head.get('record')!r}")

        body_doc = json.loads(
            self.body_file_of(env2.get("body_sha256") or "")
            .read_text(encoding="utf-8"))
        self.assertEqual(
            body_doc.get("record"), "checkpoint",
            msg=f"P6 (el body): el body file del checkpoint lleva "
                f"`record: \"checkpoint\"` (el discriminador de legado "
                f"de O-1 vive en el body); got {body_doc.get('record')!r}; "
                f"body={body_doc!r}")


class TestP6SplitBrainRedefinido(CheckpointVsBeginCase):
    """P6 — `_detect_split_brain` sigue detectando ≥2 bodies con
    `record != "checkpoint"` por clave (huérfanos sin record)."""

    def test_p06_split_brain_dos_bodies_sin_record_misma_clave_escal(
            self) -> None:
        """P6: dos bodies de la MISMA clave SIN `record` (forma
        pre-RU-2: begin + huérfano divergente sembrado como fixture de
        datos, precedente D7 de test_003_004_t2_reconcile.py) →
        `reconcile` escala rc≠0 nombrando `split-brain` y citando el
        digest divergente, sin borrar la evidencia. La redefinición NO
        debilita la detección de begins/legados divergentes."""
        self.build_project([])
        body_b_doc = seeded_body_doc(
            "VARIANTE divergente huérfana (fixture de datos — misma "
            "clave, sin record)", [], record=None)
        raw_b = canonical_body_bytes(body_b_doc)
        sha_b = sha256_of(raw_b)
        body_b_path = self.root / BODIES_DIR_REL / f"{sha_b}.json"
        body_b_path.write_bytes(raw_b)

        proc = self.run_reconcile()
        self.assert_command_exists(proc, "reconcile")
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P6: ≥2 bodies con `record != \"checkpoint\"` por clave "
                f"siguen escalando split-brain (rc≠0); got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertIn(
            "split-brain", combined,
            msg=f"P6: el delta nombra el conflicto (split-brain); got "
                f"{combined[:400]!r}")
        self.assertIn(
            sha_b, combined,
            msg=f"P6: el delta cita el digest divergente ({sha_b!r}); "
                f"got {combined[:400]!r}")
        self.assertTrue(
            body_b_path.exists(),
            msg="P6: el cuerpo divergente NO se borra para esconder la "
                "divergencia (evidencia intacta para escalar)")


class TestP5ReconcileTrasAppend(CheckpointVsBeginCase):
    """P5/abstención aceptada (review-draft-001-decision.md) —
    `reconcile` de un paquete cuya clave ya no es el head tras un
    append NO escala split-brain."""

    def test_p05_reconcile_paquete_con_clave_con_dos_eslabones_no_escal(
            self) -> None:
        """P5/abstención: store post-append sembrado como fixture de
        datos (eslabón begin SIN record + eslabón checkpoint CON
        `record: "checkpoint"`, misma clave, head en seq 2 sobre el
        checkpoint) → `reconcile --packet` rinde rc 0 con
        `classification != "split-brain"`, `escalate: false` y SIN el
        error `divergent checkpoint heads`. La clasificación exacta NO
        se fija (abstención aceptada: el observable es NO convertir el
        encadenado legítimo en un bloqueo permanente).

        RED hoy: la detección vigente cuenta los DOS bodies (≥2) y
        escala rc=1 `divergent checkpoint heads` → AssertionError que
        nombra el escalamiento indebido."""
        doc_a = seeded_body_doc(GOAL_BEGIN, [], record=None)
        doc_b = seeded_body_doc(GOAL_CHECKPOINT, [], record="checkpoint")
        seed_chain(self.root, [(doc_a, 1), (doc_b, 2)])
        head = self.head_document()
        self.assertEqual(
            (head.get("seq"), head.get("record")), (2, "checkpoint"),
            msg="P5 (precondición del fixture): el head sembrado es el "
                "eslabón checkpoint (seq 2, record checkpoint)")

        proc = self.run_reconcile()
        self.assert_command_exists(proc, "reconcile")
        combined = self.combined_output(proc)

        self.assertEqual(
            proc.returncode, 0,
            msg=f"P5/abstención: tras un append, `reconcile --packet` de "
                f"la clave con DOS eslabones (begin + checkpoint) NO "
                f"escala split-brain (rc=0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "divergent checkpoint heads", combined,
            msg=f"P5/abstención: la salida NO contiene el error de "
                f"divergencia permanente (`divergent checkpoint heads`);"
                f" got {combined[:500]!r}")
        env = json.loads(proc.stdout.decode("utf-8"))
        self.assertNotEqual(
            env.get("classification"), "split-brain",
            msg=f"P5/abstención: la clasificación NO es split-brain (el "
                f"encadenado begin→checkpoint NO es un fork); got "
                f"{env.get('classification')!r} (full={env!r})")
        self.assertFalse(
            env.get("escalate"),
            msg=f"P5/abstención: un encadenado legítimo no se escala; got "
                f"{env.get('escalate')!r}")


class TestO1DiscriminadorLegadoPorRecord(CheckpointVsBeginCase):
    """O-1 (review-t1-decision.md, entra en T2) — un body es legado SOLO
    si no tiene `record`; una referencia sin `class` dentro de un body
    CON `record` se trata como `contract` (P3) y bloquea si cambia."""

    def test_o01_body_con_record_y_ref_sin_class_bloquea_control_legad(
            self) -> None:
        """O-1: store sembrado (fixture de datos) con un body CON
        `record: "checkpoint"` cuya referencia NO trae `class` (la forma
        pre-003-007 dentro de un body nuevo) — el archivo referenciado
        CAMBIA → `resume` BLOQUEA rc≠0 citando el path y el digest
        congelado (contract, fallo cerrado — NO legacy). Control (mismo
        montaje con body SIN `record`): la referencia sin class sigue
        siendo legado por comparación → rc 0, `state: changed` con
        `legacy: true` (P7/D6 intacto; el fixture versionado de T1 no
        cambia). El par fija el discriminador: legado = body SIN record.

        RED hoy: el discriminador vigente mira la ausencia de `class` en
        la REFERENCIA (ignora el `record` del body) → el caso afirmativo
        rinde rc 0 con legacy: true → AssertionError que nombra O-1."""
        frozen_note = "Nota congelada en el body con record.\n"
        for caso in ("con-record", "sin-record-control"):
            with self.subTest(caso=caso):
                self.setUp()
                self.write_json(POLICY_REL, policy_fixture())
                self.write_state(state_doc_fixture())
                nota = self.write_text("fixture/nota.md", frozen_note)
                frozen_sha = sha256_of(frozen_note.encode("utf-8"))
                refs_sin_class = [{"path": "fixture/nota.md",
                                   "sha256": frozen_sha}]
                record = "checkpoint" if caso == "con-record" else None
                doc = seeded_body_doc(
                    "body con record y referencia sin class"
                    if record else "body legado y referencia sin class",
                    refs_sin_class, record=record)
                seed_chain(self.root, [(doc, 1)])

                self.write_text("fixture/nota.md",
                                frozen_note + "edicion posterior.\n")

                proc = self.run_resume()
                combined = self.combined_output(proc)

                if caso == "con-record":
                    self.assertNotEqual(
                        proc.returncode, 0,
                        msg=f"O-1: una referencia sin `class` dentro de un "
                            f"body CON `record` se trata como `contract` "
                            f"(P3): su cambio BLOQUEA rc≠0; got "
                            f"rc={proc.returncode} stdout={proc.stdout!r} "
                            f"stderr={proc.stderr!r}")
                    self.assertIn(
                        "fixture/nota.md", combined,
                        msg=f"O-1: el delta cita el path; got "
                            f"{combined[:500]!r}")
                    self.assertIn(
                        frozen_sha, combined,
                        msg=f"O-1: el delta cita el digest esperado/"
                            f"congelado ({frozen_sha!r}); got "
                            f"{combined[:500]!r}")
                else:
                    env = self.write_envelope(proc, "resume")
                    entry = find_reference_report(env, "fixture/nota.md")
                    self.assertIsNotNone(
                        entry,
                        msg=f"O-1 (control): la envolvente reporta la "
                            f"referencia; got {env!r}")
                    assert entry is not None  # para el tipado
                    self.assertEqual(
                        (entry.get("state"), entry.get("legacy")),
                        ("changed", True),
                        msg=f"O-1 (control/P7): el body SIN `record` "
                            f"sigue siendo legado por comparación — rc 0, "
                            f"`state: changed` con `legacy: true`; got "
                            f"{entry!r}")


class TestV5Headroom16KiB(CheckpointVsBeginCase):
    """V5 (review-draft-001.md, abstención que queda para el RED) — un
    update realista con `record`+`class`+`fields` cabe bajo el default
    de 16 KiB sin truncamiento."""

    def test_v05_update_realista_con_clases_cabe_en_16kib(self) -> None:
        """V5: un D11 realista (goal largo, 3 decisiones con rationale,
        5 uncertezas y 10 referencias como objetos con `class`, una de
        ellas el state con `fields` de autoridad) se checkpointea con el
        cap DEFAULT (sin --max-bytes): rc 0, `seq 2`, `no_op false` y
        `bytes <= max_bytes` (16384) — el margen que suma `record` más la
        clase estampada (~30 bytes/referencia) NO empuja la proyección
        fuera del cap; nunca un checkpoint truncado."""
        refs = []
        for i in range(8):
            rel = f"fixture/nota-{i}.md"
            self.write_text(rel, f"Nota referenciada {i} (fixture).\n")
            refs.append({"path": rel,
                         "class": "contract" if i % 2 else "living"})
        self.write_text(REF_LIVING_LEDGER_REL, LIVING_LEDGER_TEXT)
        refs.append({"path": REF_LIVING_LEDGER_REL, "class": "living"})
        refs.append({"path": STATE_REL, "class": "contract",
                     "fields": ["hitl_delegation", "approver",
                                "execution"]})

        self.build_project([])
        update2 = self.write_update(
            update_fixture(
                attempt=2,
                goal=("Encargo realista: " + "avance del encargo, " * 40),
                decisions=[
                    {"decision": f"Decision {i} con detalle",
                     "rationale": f"Rationale {i} con su motivo completo"}
                    for i in range(3)],
                uncertainties=[f"Incertidumbre {i} abierta"
                               for i in range(5)],
                references=refs),
            name="update-realista.json")
        env = self.write_envelope(self.run_write("checkpoint", update2),
                                  "checkpoint")

        self.assertEqual(
            env.get("seq"), 2,
            msg="V5 (precondición): el checkpoint realista encadena seq 2")
        self.assertEqual(
            env.get("max_bytes"), DEFAULT_MAX_BYTES,
            msg=f"V5: el cap DEFAULT aplicado es {DEFAULT_MAX_BYTES}; got "
                f"{env.get('max_bytes')!r}")
        self.assertIsInstance(
            env.get("bytes"), int,
            msg="V5: la envolvente expone `bytes` (tamaño de la "
                "proyección)")
        self.assertLessEqual(
            env.get("bytes"), env.get("max_bytes"),
            msg=f"V5: el update realista con record+class+fields cabe "
                f"bajo el cap default ({env.get('bytes')} <= "
                f"{env.get('max_bytes')}) — sin truncamiento")


if __name__ == "__main__":
    unittest.main()
