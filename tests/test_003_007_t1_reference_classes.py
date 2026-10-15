#!/usr/bin/env python3
"""003-007 T1 RED — clases de referencia contract/living, proyección de
autoridad vía `fields` con fallos cerrados, legado por comparación y
aislamiento de rol (P1, P2, P3, P4, P7, P8 — plan.md T1 / spec.md §3).

Contract:
- docs/specs/003-007-living-continuity/spec.md (§3 `--update.references[]`,
  Envolturas, P1, P2, P3, P4/BL-3, P7/D6, P8; VERIFY V2; criterios de
  aceptación 2, 3, 4, 6, 7).
- docs/specs/003-007-living-continuity/plan.md (T1; focales declarados:
  este archivo + tests/test_003_004_t1_resume.py +
  tests/test_003_004_t1_checkpoint.py + tests/test_003_004_t4_real_context.py).

Superficie observable bajo prueba (§3 — misma firma; V6 de 003-004 se
mantiene):

    python3 scripts/cdad_continuity.py begin      --project-root ROOT \
        --execution-context EXEC.json --update UPDATE.json [--json]
    python3 ... resume     --project-root ROOT --execution-context EXEC.json \
        [--role ROLE] [--json]
    python3 ... reconcile  --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID [--json]
    python3 ... trigger    --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID [--json]

Decisiones de superficie fijadas por este RED (V2/V6 — declaradas para el
GREEN/reviewer):

S1. `--update.references[]` acepta un string (compat, `class` =
    `contract`) o un objeto {"path", "class"?, "fields"?};
    `class` ∈ {contract, living}; ausente/desconocido → `contract`
    (fallo cerrado, P3). El CLI NO clasifica por ruta: un archivo cuya
    ruta sugiere ledger/deuda es `contract` si no se declara `living`
    (P3 - el CLI no deriva la clase de rutas).
S2. La clase resuelta se ESTAMPA en el body del checkpoint: cada entrada
    de `references` en la envolvente de `begin`/`checkpoint` lleva
    {"path","sha256","class"} (+ "fields" cuando se declara), incluso
    para la forma string (compat).
S3. Envoltura de `resume`/`reconcile`/`trigger`: cada referencia visible
    se reporta como {"path","class","sha256","current_sha256","state"}
    con `state` ∈ unchanged|changed|missing. Referencia AUSENTE →
    `current_sha256: null` (cambiada → digest REAL de su contenido o
    proyección — invariante 2: nunca se fabrican digests). La envolvente
    que porta los reportes NO exige clave nominal (la spec no la fija):
    la entrada se busca recursivamente — el observable es la ENTRADA,
    no su camino en el árbol.
S4. `legacy: true` SOLO cuando la clase provino de un cuerpo legado sin
    `class` resuelto por comparación (D6): digest distinto o ausente →
    `changed`/`missing` con `legacy: true` y NO bloquea (P7). En el caso
    igual D6 solo exige "verificado como contract": NO se demanda
    `legacy` allí (subconjunto asertado mínimo que el texto fija).
S5. V2 — CANONICALIZACIÓN de `fields` (fijada en RED, determinista):
    fields K (lista) sobre un JSON top-level D → proyección
    P = {k: D[k] for k in sorted(K) if k in D} (solo las claves que
    SÍ resuelven; si NINGUNA resuelve → rc≠0 al escribir, BL-3);
    bytes canónicos = json.dumps(P, sort_keys=True, ensure_ascii=False,
    separators=(",", ":")).encode("utf-8");
    digest esperado = hex sha256 de esos bytes. Sin `fields` → digest de
    los bytes COMPLETOS del archivo (P4). `fields` sobre un archivo
    no-JSON → rc≠0 AL ESCRIBIR (validación de tiempo de escritura BL-3):
    se detecta en el propio `begin`/`checkpoint`, sin head/persistido
    nuevo y sin traceback (diagnóstico manejado, no crash).
S6. Store legado REAL y versionado (tests/fixtures/003-007-legacy-store/):
    generado UNA VEZ con el CLI del repo ANTES del GREEN (2026-10-08): en
    ese momento `scripts/cdad_continuity.py` es exactamente un escritor
    pre-003-007 — `begin` con referencias STRING congela entradas
    {"path","sha256"} sin `class`/`fields`, y la clase resuelta no
    existe en head NI en bodies/<sha>.json (verificado en la generación).
    Los tests P7 copian ese fixture a tmp (autocontenidos; NUNCA los
    stores reales de `.cdad/` del repo) y verifican D6 sobre la copia:
    intacto → verificado `contract`; divergido/ausente →
    changed/missing con `legacy: true` y NO bloquea. La generación
    EXACTA (comando y salida) queda documentada en
    tests/fixtures/003-007-legacy-store/README.md — irreproducible
    post-GREEN con este shape (el GREEN estampa la clase en el body).

Cobertura (un test por postcondición, cada uno la NOMBRA):

- P1  test_p01_*: referencia contract cambiada o ausente → rc≠0 citando
      path y digests esperado/real, en `resume`, `reconcile` Y `trigger`.
- P2  test_p02_*: referencia living cambiada o ausente NO bloquea:
      los tres comandos rinden (rc 0) y reportan
      state: changed|missing + current_sha256 (null si missing).
- P3  test_p03_*: string compat = contract estampada; class desconocida
      → contract (fallo cerrado); sin class en objeto → contract; el
      CLI no deriva la clase de rutas (ruta de ledger sin living →
      contract: bloquea).
- P4  test_p04_*: con `fields`, cambiar stage_history/active_packet
      (progreso) NO bloquea y la digestión coincide con la proyección
      canónica V2; cambiar hitl_delegation (autoridad) → rc≠0; sin
      `fields` → digest de archivo COMPLETO (progreso también bloquea);
      fields sobre no-JSON → rc≠0 al escribir; fields con proyección
      vacía → rc≠0 al escribir.
- P7  test_p07_*: legado por comparación — intacto → verificado
      `contract` (state unchanged); divergido/ausente →
      changed/missing con legacy: true, rc 0 (no bloquea).
- P8  test_p08_*: `resume --role test-writer` sigue filtrando
      referencias de implementación; los campos nuevos no las exponen.

Fixtures: proyecto y stores sintéticos en tmp (autocontenidos, corridos
con `env -u TMPDIR`); NUNCA los stores reales de `.cdad/` del repo;
stdin cerrado (DEVNULL), foreground SIEMPRE (nunca background); el repo
no recibe ninguna escritura del test.

RED (paquete): corre SOLO este archivo:
    env -u TMPDIR python3 -m pytest -q \
        tests/test_003_007_t1_reference_classes.py < /dev/null
Focales de regresión (verdes constantes):
    tests/test_003_004_t1_resume.py tests/test_003_004_t1_checkpoint.py
    tests/test_003_004_t4_real_context.py
La suite completa NO se corre (acotado). Nunca background.
"""

from __future__ import annotations

import hashlib
import json
import shutil
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

EXEC_ID = "exec-003-007-t1-red-001"
PACKET_ID = "003-007-living-continuity-implementer-red-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

# Tope duro: un CLI determinista nunca puede colgarse (acotado).
CLI_TIMEOUT_S = 120

CONTINUITY_DIR_REL = f".cdad/executions/{EXEC_ID}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"

# Referencias del fixture (bajo ningún root declarado → visibles a todo
# rol, EXCEPTO las declaradas bajo implementation_roots: clasificación de
# rol por POLÍTICA del proyecto — decisión B2 de 003-004, reutilizada).
REF_LIVING_LEDGER_REL = "fixture/work-ledger.md"
REF_LIVING_DEBT_REL = "fixture/idea-debt.md"
REF_CONTRACT_REL = "fixture/approved-note.md"
REF_PLAIN_REL = "fixture/legacy-note.md"
REF_TEST_REL = "fixture/notes-history.md"
REF_IMPL_REL = "build/impl-note.md"

# Claves de autoridad del state (subconjunto recomendado, D1/P4).
STATE_FIELDS = ["hitl_delegation", "approver", "execution"]

LIVING_LEDGER_TEXT = "Ledger vivo: rotacion 0021 registrada.\n"
LIVING_DEBT_TEXT = "Deuda viva: D1 defaults por policy.\n"
CONTRACT_TEXT = "Nota aprobada congelada en el checkpoint.\n"
PLAIN_TEXT = "Nota sin clase declarada (compat legada).\n"
TEST_REFERENCE_TEXT = "Historia L3 por referencia.\n"
IMPL_REFERENCE_TEXT = "Nota interna de implementacion.\n"

NO_JSON_TEXT = ("Fragmento en prosa, no es JSON: [{invalid ...\n")

# S6: store legado pre-003-007, versionado bajo tests/ (su generación con
# el CLI pre-GREEN y su salida exacta: README.md del fixture).
LEGACY_STORE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "003-007-legacy-store"

GOAL = "T1 de 003-007: clases de referencia y proyeccion de autoridad"
GOAL_AVANCE = GOAL + " (avance)"
NEXT_ACTION = "Pasar a GREEN con los focales declarados"
DECISION_TEXT = "Clase declarada en la referencia; sin clasificacion por rutas"
DECISION_RATIONALE = "D2/D3 de la spec 003-007"
UNCERTAINTY = "V2: canonicalizacion de fields fijada por este RED"


# ---------------------------------------------------------------- fixtures


def exec_context_fixture(**extra: object) -> dict:
    """Execution context mínimo (forma plana de 001, forma T1 de
    003-004) con delegación HITL vigente CONSISTENTE con el state."""
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
    """`docs/.cdad-state.json` sintético: autoridad (D1) + progreso.

    Autoridad: hitl_delegation, approver, execution.
    Progreso (SUBORDINADO a la integridad cuando hay `fields`):
    stage_history, active_packet.
    """
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
            {"stage": 3, "substage": "audit", "feature_id": FEATURE_ID},
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
    """Contenido D11 del cuerpo (forma fijada por 003-004 T1)."""
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


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# V2 (S5): proyección canónica de `fields` sobre un JSON top-level.
def projection_digest(doc: dict, fields: list[str]) -> str:
    resolved = {k: doc[k] for k in sorted(fields) if k in doc}
    canonical = json.dumps(resolved, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- helpers


def find_reference_report(node: object, rel: str) -> dict | None:
    """Busca recursivamente la entrada de reporte de la referencia
    `rel` ({path, class, sha256, current_sha256, state, legacy?}):
    el contrato (S3) fija la FORMA DE LA ENTRADA, no su clave contenedora
    en la envolvente (no se adivina la envolvente; se exige la entrada)."""
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


class ReferenceClassCase(unittest.TestCase):
    """Proyecto sintético en tmp con stores de continuity PROPIOS."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-007-t1cls-red-")
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

    def write_update(self, doc: dict) -> Path:
        return self.write_json("fixture/update.json", doc)

    def write_state(self, doc: dict) -> Path:
        return self.write_json(STATE_REL, doc)

    def read_state(self) -> dict:
        return json.loads((self.root / STATE_REL).read_text(
            encoding="utf-8"))

    def build_project(self, references: list) -> dict:
        """Sistema base: policy + referencias existentes + begin rc 0."""
        self.write_json(POLICY_REL, policy_fixture())
        self.write_text(REF_LIVING_LEDGER_REL, LIVING_LEDGER_TEXT)
        self.write_text(REF_LIVING_DEBT_REL, LIVING_DEBT_TEXT)
        self.write_text(REF_CONTRACT_REL, CONTRACT_TEXT)
        self.write_text(REF_PLAIN_REL, PLAIN_TEXT)
        self.write_text(REF_TEST_REL, TEST_REFERENCE_TEXT)
        self.write_text(REF_IMPL_REL, IMPL_REFERENCE_TEXT)
        self.write_state(state_doc_fixture())
        return self.begin_env(references)

    def build_project_from_legacy_fixture(self) -> None:
        """S6: el proyecto ES la copia en tmp del store legado REAL y
        versionado `tests/fixtures/003-007-legacy-store/` (generado con
        el CLI pre-003-007 antes del GREEN; generación exacta en el
        README.md del fixture). Autocontenido: nunca los stores reales
        de `.cdad/` del repo."""
        self.assertTrue(
            LEGACY_STORE_FIXTURE.is_dir(),
            msg="P7 (precondición): el store legado versionado vive en "
                f"`{LEGACY_STORE_FIXTURE.relative_to(REPO_ROOT)}` (S6; "
                "generación exacta documentada en su README.md)")
        shutil.copytree(LEGACY_STORE_FIXTURE, self.root, dirs_exist_ok=True)
        self.exec_context = self.root / "fixture" / "exec.json"

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

    def run_resume(self, *, role: str | None = None,
                   ) -> subprocess.CompletedProcess:
        argv = ["resume", "--project-root", str(self.root),
                "--execution-context", str(self.exec_context), "--json"]
        if role is not None:
            argv += ["--role", role]
        return self.run_cli(*argv)

    def run_reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")

    def run_trigger(self) -> subprocess.CompletedProcess:
        return self.run_cli("trigger", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")

    def combined_output(self, proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout.decode("utf-8", errors="replace")
                + proc.stderr.decode("utf-8", errors="replace"))

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser comportamiento ausente con mensaje
        explícito — nunca import, sintaxis o traceback."""
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
        self.assertEqual(
            proc.returncode, 0,
            msg=f"RED: `{which}` no produce el comportamiento esperado "
                f"todavía; rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    def begin_raw(self, references: list) -> subprocess.CompletedProcess:
        """`begin` SIN aserción previa (para postcondiciones de fallo
        cerrado en tiempo de escritura)."""
        update = self.write_update(update_fixture(references=references))
        return self.run_write("begin", update)

    def begin_env(self, references: list) -> dict:
        return self.write_envelope(self.begin_raw(references), "begin")

    def head_document(self) -> dict:
        head = self.root / HEAD_REL
        self.assertTrue(
            head.is_file(),
            msg="precondición: el head vive en "
                f"`{HEAD_REL}` (superficie fijada en RED, V6)")
        return json.loads(head.read_text(encoding="utf-8"))

    def continuity_files(self) -> dict[str, bytes]:
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(base)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }

    def reference_report(self, env: dict, rel: str,
                         which: str) -> dict:
        """Exige la entrada de reporte de una referencia en la envolvente
        de `which` (S3)."""
        entry = find_reference_report(env, rel)
        self.assertIsNotNone(
            entry,
            msg=f"§3/Envolturas: `{which}` reporta CADA referencia visible "
                f"como {{path,class,sha256,current_sha256,state,legacy?}}; "
                f"falta la entrada de {rel!r}; got envolvente={env!r}")
        assert entry is not None  # para el tipado
        return entry


# ---------------------------------------------------------------- tests


class TestP1ContractBlocks(ReferenceClassCase):
    """P1 — contrato bloquea: cambio o ausencia → rc≠0 con path y
    digests esperado/real, en resume, reconcile y trigger."""

    def test_p01_resume_contract_changed_bloquea_con_path_y_digests(
            self) -> None:
        """P1: una referencia contract (explícita) con contenido
        DIVERGENTE del congelado → `resume` rc≠0 y el delta cita el
        `path` y los DOS digests (esperado/congelado y real/actual)."""
        self.build_project([{"path": REF_CONTRACT_REL,
                             "class": "contract"},
                            {"path": REF_LIVING_LEDGER_REL,
                             "class": "living"}])
        frozen_sha = sha256_of((self.root / REF_CONTRACT_REL
                               ).read_bytes())
        tamper = CONTRACT_TEXT + "enmienda divergente posterior.\n"
        self.write_text(REF_CONTRACT_REL, tamper)
        real_sha = sha256_of(tamper.encode("utf-8"))

        proc = self.run_resume()
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P1: una referencia contract cambiada BLOQUEA (rc≠0); "
                f"got rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertIn(
            REF_CONTRACT_REL, combined,
            msg=f"P1: el delta cita el path de la referencia violada "
                f"({REF_CONTRACT_REL!r}); got {combined[:800]!r}")
        self.assertIn(
            frozen_sha, combined,
            msg=f"P1: el delta cita el digest esperado/congelado "
                f"({frozen_sha}); got {combined[:800]!r}")
        self.assertIn(
            real_sha, combined,
            msg=f"P1: el delta cita el digest real/actual ({real_sha!r}); "
                f"got {combined[:800]!r}")

    def test_p01_resume_contract_missing_bloquea_con_path(self) -> None:
        """P1: una referencia contract AUSENTE (archivo eliminado tras el
        checkpoint) también bloquea citando el path."""
        self.build_project([{"path": REF_CONTRACT_REL,
                             "class": "contract"}])
        (self.root / REF_CONTRACT_REL).unlink()

        proc = self.run_resume()
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P1: una referencia contract AUSENTE falla cerrado "
                f"(rc≠0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertIn(
            REF_CONTRACT_REL, combined,
            msg=f"P1: el delta de la ausencia cita el path "
                f"({REF_CONTRACT_REL!r}); got {combined[:800]!r}")

    def test_p01_reconcile_y_trigger_tambien_bloquean_contrato(
            self) -> None:
        """P1: no solo `resume` — `reconcile` y `trigger` también
        verifican cada referencia contract: cambio o ausencia → rc≠0
        con el delta que nombra el path."""
        commands = (("reconcile", self.run_reconcile),
                    ("trigger", self.run_trigger))
        for name, run in commands:
            with self.subTest(comando=name):
                self.setUp()
                self.build_project([{"path": REF_CONTRACT_REL,
                                     "class": "contract"}])
                # divergida
                self.write_text(REF_CONTRACT_REL,
                                CONTRACT_TEXT + "tamper\n")
                proc_div = run()
                combined_div = self.combined_output(proc_div)
                self.assertNotEqual(
                    proc_div.returncode, 0,
                    msg=f"P1: `{name}` con referencia contract divergida "
                        f"falla cerrado; got rc={proc_div.returncode} "
                        f"stdout+stderr={combined_div[:600]!r}")
                self.assertIn(
                    REF_CONTRACT_REL, combined_div,
                    msg=f"P1: `{name}` nombra la referencia violada; got "
                        f"{combined_div[:600]!r}")

                # ausente
                self.setUp()
                self.build_project([{"path": REF_CONTRACT_REL,
                                     "class": "contract"}])
                (self.root / REF_CONTRACT_REL).unlink()
                proc_miss = run()
                combined_miss = self.combined_output(proc_miss)
                self.assertNotEqual(
                    proc_miss.returncode, 0,
                    msg=f"P1: `{name}` con referencia contract AUSENTE "
                        f"falla cerrado; got rc={proc_miss.returncode} "
                        f"stdout={combined_miss[:600]!r}")
                self.assertIn(
                    REF_CONTRACT_REL, combined_miss,
                    msg=f"P1: `{name}` nombra la referencia ausente; got "
                        f"{combined_miss[:600]!r}")


class TestP2LivingInforms(ReferenceClassCase):
    """P2 — vivo informa, no bloquea: changed/missing con
    current_sha256 y rc 0 en los tres comandos."""

    def test_p02_living_changed_y_missing_informan_sin_bloquear(
            self) -> None:
        """P2: una referencia living DIVERGIDA y una AUSENTE no bloquean:
        `resume`, `reconcile` y `trigger` rinden (rc 0) y reportan cada
        una como {"state: changed|missing", "current_sha256": digest real
        o null si missing} — progreso reportado, nunca despacho
        bloqueado ni digest fabricado."""
        self.build_project([{"path": REF_LIVING_LEDGER_REL,
                             "class": "living"},
                            {"path": REF_LIVING_DEBT_REL,
                             "class": "living"}])
        nuevo = LIVING_LEDGER_TEXT + "rotacion 0022: T1 continues.\n"
        self.write_text(REF_LIVING_LEDGER_REL, nuevo)
        real_sha = sha256_of(nuevo.encode("utf-8"))
        (self.root / REF_LIVING_DEBT_REL).unlink()

        commands = (("resume", self.run_resume,
                     lambda: self.run_resume()),
                    ("reconcile", self.run_reconcile,
                     self.run_reconcile),
                    ("trigger", self.run_trigger, self.run_trigger))
        commands = ((name, run) for name, run, _ in commands)
        for name, run in commands:
            with self.subTest(comando=name):
                proc = run()
                env = self.write_envelope(proc, name)
                env_text = json.dumps(env, ensure_ascii=False)

                entry_ledger = self.reference_report(
                    env, REF_LIVING_LEDGER_REL, name)
                self.assertEqual(
                    entry_ledger.get("state"), "changed",
                    msg=f"P2/{name}: la living divergida se reporta "
                        f"`state: changed` (el render NO se detiene); got "
                        f"{entry_ledger!r}")
                self.assertEqual(
                    entry_ledger.get("current_sha256"), real_sha,
                    msg=f"P2: `current_sha256` de la living divergida es el "
                        f"digest REAL de su contenido actual ({real_sha!r});"
                        f" got {entry_ledger.get('current_sha256')!r}")

                entry_debt = self.reference_report(
                    env, REF_LIVING_DEBT_REL, name)
                self.assertEqual(
                    entry_debt.get("state"), "missing",
                    msg=f"P2: la living AUSENTE se reporta `missing`; got "
                        f"{entry_debt!r}")
                self.assertIsNone(
                    entry_debt.get("current_sha256"),
                    msg=f"P2: sin señal fiable no hay digest: la ausente "
                        f"reporta `current_sha256` null (invariante 2: "
                        f"nunca se fabrican digests); got "
                        f"{entry_debt.get('current_sha256')!r}")


class TestP3ClassSourceDefaultCerrado(ReferenceClassCase):
    """P3 — clase desde la declaración; default cerrado; sin
    clasificación por rutas."""

    def test_p03_string_compat_es_contract_y_se_estampa(self) -> None:
        """P3: la forma STRING (compat) se resuelve `contract` — se
        ESTAMPA en la envolvente de `begin` ({path,sha256,class}) y un
        cambio posterior BLOQUEA (como contract)."""
        env = self.build_project([REF_PLAIN_REL])
        stamps = {
            entry.get("path"): entry
            for entry in env.get("references", []) if isinstance(entry, dict)
        }
        self.assertEqual(
            stamps.get(REF_PLAIN_REL, {}).get("class"), "contract",
            msg=f"P3/S2: la referencia string (compat) se sella con "
                f"`class: contract` en el body; got estampa="
                f"{stamps.get(REF_PLAIN_REL)!r} (full={env!r})")
        self.assertEqual(
            stamps.get(REF_PLAIN_REL, {}).get("sha256"),
            sha256_of(PLAIN_TEXT.encode("utf-8")),
            msg="P3: el estampa lleva el digest real del contenido")

        self.write_text(REF_PLAIN_REL, PLAIN_TEXT + "cambio posterior\n")
        proc = self.run_resume()
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P3: la forma string es `contract`: su cambio bloquea "
                f"rc≠0; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

    def test_p03_clase_desconocida_se_cierra_como_contract(self) -> None:
        """P3 (fallo cerrado del default): una `class` NO reconocida no
        se respeta como living ni como algo nuevo — se congela
        `contract`: `begin` acepta y sella `contract`, y un cambio
        posterior BLOQUEA."""
        env = self.build_project([{"path": REF_LIVING_LEDGER_REL,
                                   "class": "espiritu-vivo"}])
        stamps = {
            entry.get("path"): entry
            for entry in env.get("references", []) if isinstance(entry, dict)
        }
        self.assertEqual(
            stamps.get(REF_LIVING_LEDGER_REL, {}).get("class"), "contract",
            msg=f"P3: class desconocida → contract (fallo cerrado); got "
                f"estampa={stamps.get(REF_LIVING_LEDGER_REL)!r}")
        self.write_text(REF_LIVING_LEDGER_REL,
                        LIVING_LEDGER_TEXT + "divergencia\n")
        proc = self.run_resume()
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P3: la clase desconocida NO se trata como living — se "
                f"congela contract y su cambio bloquea rc≠0; got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")

    def test_p03_el_cli_no_deriva_la_clase_de_rutas(self) -> None:
        """P3 (no clasificación por rutas, D2): un objeto SIN `class`
        sobre una ruta que SUGIERE documento vivo (ledger) NO es living:
        se congela `contract` y su cambio BLOQUEA. La clase solo viene de
        la declaración."""
        env = self.build_project([{"path": REF_LIVING_LEDGER_REL}])
        stamps = {
            entry.get("path"): entry
            for entry in env.get("references", []) if isinstance(entry, dict)
        }
        self.assertEqual(
            stamps.get(REF_LIVING_LEDGER_REL, {}).get("class"), "contract",
            msg=f"P3/D2: sin class declarada la clase resuelta es "
                f"`contract` (la ruta NO deriva living); got "
                f"estampa={stamps.get(REF_LIVING_LEDGER_REL)!r}")
        self.write_text(REF_LIVING_LEDGER_REL,
                        LIVING_LEDGER_TEXT + "avance posterior\n")
        proc = self.run_resume()
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P3/D2: el CLI NO clasifica por ruta — la referencia sin "
                f"class es contract y su cambio bloquea rc≠0; got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")


class TestP4StateAuthorityProjection(ReferenceClassCase):
    """P4/BL-3 — proyección de autoridad del state y sus dos modos de
    fallo cerrados (tiempo de escritura)."""

    def test_p04_fields_progreso_no_bloquea_y_autoridad_bloquea(
            self) -> None:
        """P4/D1: con `fields` [hitl_delegation, approver, execution], el
        digest cubre SOLO la proyección canónica (V2, S5): cambiar
        stage_history/active_packet (progreso) NO bloquea; cambiar
        hitl_delegation (autoridad) BLOQUEA citando path y los digests
        esperado/real."""
        self.build_project([{"path": STATE_REL, "class": "contract",
                             "fields": STATE_FIELDS}])
        estado_inicial = self.read_state()
        frozen = projection_digest(estado_inicial, STATE_FIELDS)

        # digerido al escribir: la envolvente congela el digest de la
        # proyección V2 (S5) y el estampa con forma completa.
        env = self.head_document()
        stamps = {
            entry.get("path"): entry
            for entry in env.get("references", []) if isinstance(entry, dict)
        }
        entry = stamps.get(STATE_REL, {})
        self.assertEqual(
            entry.get("sha256"), frozen,
            msg=f"P4/V2 (S5): el digest congelado del state con `fields` "
                f"es el de la proyección canónica V2 ({frozen!r}); got "
                f"estampa={entry!r}")
        self.assertEqual(
            sorted(entry.get("fields") or []), sorted(STATE_FIELDS),
            msg=f"P4: el estampa `fields` replica los campos declarados; "
                f"got {entry.get('fields')!r}")
        self.assertEqual(
            entry.get("class"), "contract",
            msg=f"P4: el state con `fields` es contract; got "
                f"{entry.get('class')!r}")

        # baseline: sin tocar el state → unchanged.
        proc0 = self.run_resume()
        env0 = self.write_envelope(proc0, "resume")
        rep0 = self.reference_report(env0, STATE_REL, "resume")
        self.assertEqual(
            rep0.get("state"), "unchanged",
            msg=f"P4: con `fields` el state intacto se reporta unchanged; "
                f"got {rep0!r}")

        # progreso: stage_history + active_packet cambian → NO bloquea.
        progreso = dict(estado_inicial)
        progreso["stage_history"] = estado_inicial["stage_history"] + [
            {"stage": 3, "substage": "post-audit",
             "feature_id": FEATURE_ID},
        ]
        progreso["active_packet"] = PACKET_ID + "-siguiente"
        self.write_state(progreso)
        proc1 = self.run_resume()
        env1 = self.write_envelope(proc1, "resume")
        rep1 = self.reference_report(env1, STATE_REL, "resume")
        self.assertEqual(
            rep1.get("state"), "unchanged",
            msg=f"P4/D1: con `fields` subir stage_history/active_packet "
                f"(PROGRESO) no afecta la integridad: unchanged y rc 0; "
                f"got {rep1!r} rc={proc1.returncode}")

        # autoridad: hitl_delegation cambia → BLOQUEA con delta.
        alterado = dict(progreso)
        alterado["hitl_delegation"] = dict(
            progreso["hitl_delegation"], requested_by="user (falsificado)")
        self.write_state(alterado)
        fallado = projection_digest(alterado, STATE_FIELDS)
        proc2 = self.run_resume()
        combined2 = self.combined_output(proc2)

        self.assertNotEqual(
            proc2.returncode, 0,
            msg=f"P4: cambiar hitl_delegation (AUTORIDAD proyectada) "
                f"bloquea rc≠0; got rc={proc2.returncode} "
                f"stdout={proc2.stdout!r} stderr={proc2.stderr!r}")
        self.assertIn(STATE_REL, combined2,
                      msg=f"P4: el delta cita el path del state; got "
                          f"{combined2[:800]!r}")
        self.assertIn(frozen, combined2,
                      msg=f"P4: el delta cita el digest esperado "
                          f"(proyección congelada {frozen!r}); got "
                          f"{combined2[:800]!r}")
        self.assertIn(fallado, combined2,
                      msg=f"P4: el delta cita el digest real de la "
                          f"proyección mutada ({fallado!r}); got "
                          f"{combined2[:800]!r}")

    def test_p04_sin_fields_el_digest_cubre_el_archivo_completo(
            self) -> None:
        """P4 (contrafáctico V2): SIN `fields`, el digest es de los bytes
        COMPLETOS del archivo: cambiar stage_history (solo progreso)
        TAMBIÉN bloquea, porque el archivo completo divergió."""
        self.build_project([{"path": STATE_REL, "class": "contract"}])
        env = self.head_document()
        stamps = {
            entry.get("path"): entry
            for entry in env.get("references", []) if isinstance(entry, dict)
        }
        full_sha = sha256_of(
            (self.root / STATE_REL).read_bytes())
        self.assertEqual(
            stamps.get(STATE_REL, {}).get("sha256"), full_sha,
            msg=f"P4: sin `fields` el digest congelado es de los bytes "
                f"COMPLETOS ({full_sha!r}); got "
                f"estampa={stamps.get(STATE_REL)!r}")

        estado = self.read_state()
        estado["stage_history"] = estado["stage_history"] + [
            {"stage": 3, "substage": "red", "feature_id": FEATURE_ID}]
        self.write_state(estado)

        proc = self.run_resume()
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P4: sin `fields`, cualquier byte divergente del archivo "
                f"(incluso progreso) bloquea rc≠0; got rc="
                f"{proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")

    def test_p04_fields_sobre_no_json_falla_cerrado_al_escribir(
            self) -> None:
        """P4/BL-3: `fields` sobre un archivo NO-JSON → rc≠0 AL ESCRIBIR
        (`begin` falla), con diagnóstico manejado (sin traceback) y SIN
        persistir nada en el store de continuity."""
        self.write_text(REF_TEST_REL, NO_JSON_TEXT)
        proc = self.begin_raw([{"path": REF_TEST_REL, "class": "contract",
                                "fields": ["cualquier_clave"]}])
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P4/BL-3: `fields` sobre un archivo no-JSON falla cerrado "
                f"AL ESCRIBIR (rc≠0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", combined,
            msg=f"P4/BL-3: el fallo cerrado NO es un traceback (crash); "
                f"el diagnóstico es manejado; got {combined[:800]!r}")
        self.assertIn(
            REF_TEST_REL, combined,
            msg=f"P4/BL-3: el delta nombra el archivo no-JSON "
                f"({REF_TEST_REL!r}); got {combined[:800]!r}")
        self.assertFalse(
            self.continuity_files(),
            msg="P4/BL-3: validación de tiempo de ESCRITURA — nada queda "
                "persistido en continuity/** cuando `fields` se declara "
                "sobre un no-JSON")

    def test_p04_fields_con_proyeccion_vacia_falla_cerrado(self) -> None:
        """P4/BL-3: `fields` que no resuelve NINGUNA clave (proyección
        vacía) → rc≠0 AL ESCRIBIR: nunca un digest constante de
        integridad cero en silencio; sin traceback y sin persistencia."""
        self.build_project([])
        escr = self.continuity_files()
        proc = self.begin_raw([{"path": STATE_REL, "class": "contract",
                                "fields": ["clave_inexistente_uno",
                                           "clave_inexistente_dos"]}])
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"P4/BL-3: una proyección VACÍA falla cerrado al escribir "
                f"(rc≠0): nunca un digest constante de integridad cero; "
                f"got rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        self.assertNotIn(
            "Traceback", combined,
            msg=f"P4/BL-3: el fallo cerrado NO es un traceback; got "
                f"{combined[:800]!r}")
        self.assertIn(
            "fields", combined,
            msg=f"P4/BL-3: el delta nombra el mecanismo violado (`fields` "
                f"con proyección vacía — no un rechazo genérico de la "
                f"forma); got {combined[:800]!r}")
        self.assertEqual(
            self.continuity_files(), escr,
            msg="P4/BL-3: proyección vacía → NADA persistido (falló antes "
                "de congelar el head)")


class TestP7LegacyComparison(ReferenceClassCase):
    """P7/D6 — legado por comparación (R-1): sin `class` en el body,
    igual → verificado contract; divergido/ausente → changed/missing con
    legacy: true y NO bloquea."""

    def test_p07_legacy_intacto_se_verifica_como_contract(self) -> None:
        """P7/D6: store legado REAL (fixture versionado pre-003-007, S6):
        si el archivo NO cambió desde el congelado, la referencia se
        VERIFICA como `contract` (state unchanged, class contract) — su
        integridad sigue afirmándose."""
        self.build_project_from_legacy_fixture()

        proc = self.run_resume()
        env = self.write_envelope(proc, "resume")
        entry = self.reference_report(env, REF_PLAIN_REL, "resume")

        self.assertEqual(
            entry.get("state"), "unchanged",
            msg=f"P7/D6 (igual): la referencia legada intacta se resuelve "
                f"por comparación y se verifica (state unchanged); got "
                f"{entry!r}")
        self.assertEqual(
            entry.get("class"), "contract",
            msg=f"P7/D6: en el caso igual la clase resuelta es `contract` "
                f"(su integridad se afirma); got {entry.get('class')!r}")
        self.assertEqual(
            entry.get("current_sha256"),
            sha256_of((self.root / REF_PLAIN_REL).read_bytes()),
            msg="P7/D6: `current_sha256` reporta el digest real del "
                "contenido (igual al congelado)")

    def test_p07_legacy_divergido_reporta_changed_legacy_true_sin_bloquear(
            self) -> None:
        """P7/D6 (R-1): sobre una COPIA en tmp del store legado real
        (fixture versionado, S6 — cuerpo sin `class`), la referencia
        DIVERGIDA o AUSENTE se RESUELVE por comparación: resume rc 0,
        reporte `changed`/`missing` con `legacy: true` y current_sha256
        real (null si missing) — NO bloquea (progreso legítimo de
        documentos escritos tras el checkpoint)."""
        for caso in ("changed", "missing"):
            with self.subTest(caso=caso):
                self.setUp()
                self.build_project_from_legacy_fixture()
                if caso == "changed":
                    nuevo = PLAIN_TEXT + "ledger escrito tras el head.\n"
                    self.write_text(REF_PLAIN_REL, nuevo)
                    esperado_current = sha256_of(nuevo.encode("utf-8"))
                else:
                    (self.root / REF_PLAIN_REL).unlink()
                    esperado_current = None

                proc = self.run_resume()
                env = self.write_envelope(proc, "resume")
                entry = self.reference_report(
                    env, REF_PLAIN_REL, "resume")

                self.assertEqual(
                    entry.get("state"), caso,
                    msg=f"P7/D6: legado {caso} se reporta `state == "
                        f"{caso}`; got {entry!r}")
                self.assertIs(
                    entry.get("legacy"), True,
                    msg=f"P7/D6: la clase vino de un cuerpo legado "
                        f"resuelto por comparación → `legacy: true`; got "
                        f"{entry.get('legacy')!r}")
                self.assertEqual(
                    entry.get("current_sha256"), esperado_current,
                    msg=f"P7: `current_sha256` = digest real del contenido "
                        f"({esperado_current!r}); got "
                        f"{entry.get('current_sha256')!r}")


class TestP8RoleIsolation(ReferenceClassCase):
    """P8 — aislamiento de rol preservado con los campos nuevos."""

    def test_p08_resume_role_test_writer_sigue_filtrando_implementacion(
            self) -> None:
        """P8: `resume --role test-writer` sigue filtrando referencias
        de implementation_roots (build/impl-note.md); los campos nuevos
        (class/fields/state/legacy) NO ripen material de
        implementación al render; la referencia en scope del rol (tests)
        sigue expuesta."""
        self.build_project([
            {"path": REF_TEST_REL, "class": "living"},
            {"path": REF_IMPL_REL, "class": "contract"},
        ])

        proc = self.run_resume(role="test-writer")
        env = self.write_envelope(proc, "resume")
        rendered = proc.stdout.decode("utf-8", errors="replace")

        self.assertIn(
            REF_TEST_REL, rendered,
            msg=f"P8: la referencia dentro del scope del rol "
                f"({REF_TEST_REL!r}) sigue expuesta al test-writer con "
                "los campos nuevos")
        self.assertNotIn(
            "impl-note", rendered,
            msg=f"P8: `resume --role test-writer` NUNCA expone rutas de "
                f"implementation_roots ({REF_IMPL_REL!r}) — los campos "
                f"nuevos (class/fields/state/legacy) no filtran material "
                f"de implementación; got render={rendered[:600]!r}")


if __name__ == "__main__":
    unittest.main()
