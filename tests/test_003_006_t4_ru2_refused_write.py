#!/usr/bin/env python3
"""003-006 T4 RED (RU-2) — un `begin`/`checkpoint` RECHAZADO no escribe
nada (t4-ru2-decision.md, delegación HITL del orquestador).

RE-ESPECIFICACIÓN BL-2 (003-007-living-continuity, plan.md T2, P5/D5;
hecha por el test-writer en el RED de T2): la faceta `checkpoint` de
este archivo cambió de resultado POR DISEÑO — un `checkpoint` con la
clave del head y cuerpo distinto ya NO se rechaza: SE APENDEA como
eslabón nuevo (`seq+1`, `prev_checkpoint_sha256` = body del head). P5
sustituye la semántica de RECHAZO del checkpoint, NO la del
todo-o-nada, que sobrevive intacta en la faceta `begin` divergente y en
los cierres R-B1/D4/P7 (tests de 003-004). Trazabilidad:
docs/specs/003-007-living-continuity/spec.md (P5, P6, D5, §3 Envolventes),
docs/specs/003-007-living-continuity/plan.md (T2, BL-2),
docs/specs/003-007-living-continuity/review-draft-001.md (BL-2) y
docs/specs/003-007-living-continuity/review-draft-001-decision.md.

Contract:
- docs/specs/003-006-runtime-adoption/spec.md (§2.4: `begin`/`checkpoint`
  /`reconcile` operativos en el ciclo; superficie V6 de 003-004).
- docs/specs/003-006-runtime-adoption/t4-ru2-decision.md (cierre RU-2,
  mapeo exacto de estos tests: "un `begin` o un `checkpoint` rechazado
  no escribe nada: ni cuerpo, ni cabeza, ni directorios nuevos. El
  cuerpo se escribe solo después de pasar todas las validaciones (todo
  o nada)"). Va como review-fix RED → GREEN.
- docs/specs/003-006-runtime-adoption/evidence/t4/rotation-2-split-brain.md
  (el cuerpo huérfano `2aee8d80…` escrito por el checkpoint rechazado
  deja DOS cuerpos para la misma clave y `reconcile --packet` falla
  para siempre con `divergent checkpoint heads` — un rechazo convierte
  un error de uso en un bloqueo permanente).

Defecto (RU-2, encontrado en el uso real de T4): un `checkpoint` con la
MISMA clave `(execution_id, packet_id, attempt)` que la cabeza y un
cuerpo distinto se rechaza (rc=1, split-brain — como corresponde), pero
ANTES de rechazar deja escrito su cuerpo en
`continuity/bodies/<sha>.json`. Faceta `begin`: el mismo leak con un
`begin` divergente de la misma clave.

Tests (uno por faceta del cierre RU-2, cada uno mapeado; proyecto
temporal con la forma REAL de contexto de ejecución de 001 — identidad
en `execution.id`, delegación activa en el state):

1. `test_t4_ru2_checkpoint_misma_clave_apendea_eslabon_p5` →
   RE-ESPECIFICADA por P5/D5 de 003-007 (BL-2; el cierre original RU-2
   exigía aquí el rechazo todo-o-nada): (a) `begin` válido; luego
   `checkpoint` con la MISMA clave `(packet_id, attempt)` y cuerpo
   distinto → rc 0 y SE APENDEA como eslabón nuevo (`seq+1`,
   `prev_checkpoint_sha256` = body del head, `body_sha256` nuevo, el
   eslabón previo permanece en `bodies/`, `head.json` refleja el
   eslabón nuevo); (b) después, `reconcile --packet` de esa clave NO da
   split-brain (rc=0, clasificación sin error de divergencia).
2. `test_t4_ru2_begin_divergente_no_escribe_nada_y_reconcile_no_split_brain`
   → RU-2 (faceta begin, escenario c del orquestador): lo mismo para un
   `begin` divergente con la misma clave.

RED hoy (probes observables del CLI actual, 2026-10-07): el rechazo
mismo existe (rc≠0) pero deja el cuerpo huérfano escrito → la aserción
del árbol intacto fracasa por comportamiento presente-incorrecto
(AssertionError que nombra el archivo filtrado), y `reconcile` queda
bloqueado en split-brain (rc=1) → fracasa la aserción rc=0 sin
divergencia. Nunca ImportError ni sintaxis: el test no importa el
módulo del CLI.

Nota para el GREEN (declarada en RED): el cierre RU-2 cambia el
comportamiento que `tests/test_003_004_t2_writeahead.py`
(TestO1BeginDivergenteMismaClave) fijó para 003-004 (reconcile rc≠0
split-brain tras un begin divergente): con RU-2 el cuerpo divergente
rechazado no queda, así que ese test de la feature anterior deberá ser
ajustado por el orquestador/implementer en el GREEN.
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

FEATURE_ID = "003-006-runtime-adoption"
EPIC_ID = "epic-003-context-efficiency"

# Ejecución y paquete SIMULADOS (fixtures en tmp; ninguna escritura en
# este repo, ningún incidente real).
EXEC_ID = "exec-003-006-runtime-adoption-001"
PACKET_ID = "003-006-runtime-adoption-t4-ru2-red-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

EXEC_DIR_REL = f".cdad/executions/{EXEC_ID}"
CONTINUITY_DIR_REL = f"{EXEC_DIR_REL}/continuity"
BODIES_DIR_REL = f"{CONTINUITY_DIR_REL}/bodies"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"

GOAL = "T4 RU-2 RED: el rechazo todo-o-nada de begin/checkpoint"
NEXT_ACTION = "reconciliar antes de cualquier reintento (D6)"
DECISION_TEXT = "El cuerpo se escribe solo tras pasar todas las validaciones"
DECISION_RATIONALE = "todo o nada: un rechazo no deja rastro en el store"


# ---------------------------------------------------------------- fixtures


def path_policy_fixture() -> dict:
    """path_policy REAL de la ejecución 001 (forma publicada por 001)."""
    return {
        "documentation_files": ["README.md"],
        "documentation_roots": ["docs"],
        "implementation_files": ["install.sh"],
        "implementation_roots": ["agents", "skills", "scripts",
                                 "sources", "build"],
        "private_paths": ["tests/.sensitive-patterns.local"],
        "test_roots": ["tests"],
    }


def policy_doc_fixture() -> dict:
    """docs/cdad-policy.json del proyecto (forma 002/004 reutilizada)."""
    return {
        "path_policy": path_policy_fixture(),
        "schema_version": 1,
    }


def real_exec_context_fixture(policy_sha256: str) -> dict:
    """Forma REAL del execution.json (RU-1 de 003-004 ya cerrada):
    identidad anidada en `execution.id`, SIN `hitl_delegation` (la
    autoridad vive en el state)."""
    return {
        "schema_version": 1,
        "execution": {
            "authority_ref": AUTHORITY_REF,
            "epic_id": EPIC_ID,
            "feature_id": FEATURE_ID,
            "id": EXEC_ID,
            "model_policy": "ordinary",
            "policy_sha256": policy_sha256,
            "scope": EPIC_ID,
        },
        "path_policy": path_policy_fixture(),
        "policy": {
            "path": POLICY_REL,
            "schema_version": 1,
            "sha256": policy_sha256,
            "snapshot": json.dumps(policy_doc_fixture(), sort_keys=True),
        },
        "policy_history": [],
    }


def state_fixture() -> dict:
    """Forma REAL del `hitl_delegation` del state: vence POR EVENTOS
    (prosa en `expires`, sin `expires_on` de fecha) → active."""
    return {
        "schema_version": 1,
        "hitl_delegation": {
            "delegated_to": "orchestrator",
            "requested_by": "user (pablo)",
            "requested_at": "2026-10-07T00:00:00Z",
            "scope": EPIC_ID,
            "expires": "vence por eventos; 001 valida la vigencia en "
                       "prepare",
            "publication": "docs/specs/003-006-runtime-adoption/spec.md",
            "source": AUTHORITY_REF,
        },
    }


def update_fixture(**overrides: object) -> dict:
    """Cuerpo D11 (forma de T1/T2 de 003-004): packet_id + attempt +
    contenido canónico."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": GOAL,
        "decisions": [
            {"decision": DECISION_TEXT, "rationale": DECISION_RATIONALE},
        ],
        "uncertainties": [],
        "next_action": NEXT_ACTION,
        "references": [],
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------- helpers


class Ru2RefusedWriteCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con la forma REAL de contexto."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-006-t4ru2-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)
        self.build_real_project()

    # -- construcción del proyecto fixture -----------------------------

    def build_real_project(self) -> None:
        """Proyecto con el contexto REAL de 001 + policy + state."""
        policy_path = self.write_json(POLICY_REL, policy_doc_fixture())
        policy_sha = hashlib.sha256(policy_path.read_bytes()).hexdigest()
        self.exec_context = self.write_json(
            "fixture/exec.json", real_exec_context_fixture(policy_sha))
        self.write_json(STATE_REL, state_fixture())

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_update(self, doc: dict, name: str = "update.json") -> Path:
        return self.write_json(f"fixture/{name}", doc)

    # -- observación del store de continuity ---------------------------

    def continuity_snapshot(self) -> dict[str, bytes]:
        """Snapshot {rel: bytes} de TODO el árbol `continuity/`."""
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return {}
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in sorted(base.rglob("*")) if p.is_file()
        }

    def continuity_dirs(self) -> set[str]:
        """Set de directorios bajo `continuity/` (ni directorios nuevos)."""
        base = self.root / CONTINUITY_DIR_REL
        if not base.exists():
            return set()
        return {str(p.relative_to(self.root))
                for p in sorted(base.rglob("*")) if p.is_dir()}

    def head_bytes(self) -> bytes | None:
        head = self.root / HEAD_REL
        return head.read_bytes() if head.is_file() else None

    # -- corridas del CLI ----------------------------------------------

    def run_cli(self, *argv: str) -> subprocess.CompletedProcess:
        """Foreground SIEMPRE, stdin cerrado (nunca background, nunca
        pregunta interactiva)."""
        try:
            return subprocess.run(
                [sys.executable, str(CONTINUITY_SCRIPT), *argv],
                cwd=REPO_ROOT, capture_output=True, timeout=CLI_TIMEOUT_S,
                stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "RU-2 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca "
                f"puede colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path
                  ) -> subprocess.CompletedProcess:
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--packet", PACKET_ID, "--json")

    def combined_output(self, proc: subprocess.CompletedProcess) -> str:
        return (proc.stdout.decode("utf-8", errors="replace")
                + proc.stderr.decode("utf-8", errors="replace"))

    def assert_command_exists(self, proc: subprocess.CompletedProcess,
                              which: str) -> None:
        """RED: el fracaso debe ser comportamiento ausente/incorrecto con
        mensaje explícito — nunca CLI ausente, import ni traceback."""
        combined = self.combined_output(proc)
        self.assertNotIn(
            "invalid choice", combined,
            msg=f"RU-2: el comando `{which}` no existe (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                "` declarado en §3/V6 de 003-004 es obligatorio")
        self.assertNotIn(
            "Traceback", combined,
            msg=f"RU-2: `{which}` terminó con traceback sin manejar "
                f"(stderr={proc.stderr.decode('utf-8',
                                                  errors='replace')!r})")

    def begin_valid(self) -> bytes:
        """Precondición compartida: un `begin` válido deja el head."""
        update = self.write_update(update_fixture())
        proc = self.run_write("begin", update)
        self.assert_command_exists(proc, "begin")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"RU-2 (precondición): el `begin` válido debe terminar "
                f"rc=0; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        head = self.head_bytes()
        self.assertIsNotNone(
            head,
            msg="RU-2 (precondición): el `begin` válido persistió el "
                f"head en `{HEAD_REL}`")
        return head

    def assert_refused_writes_nothing(
            self, proc: subprocess.CompletedProcess, which: str,
            before: dict[str, bytes], dirs_before: set[str],
            head_before: bytes) -> None:
        """Cierre RU-2: el rechazo (rc≠0) NO escribe nada — el árbol
        `continuity/` queda byte a byte igual que antes (ni cuerpo, ni
        cabeza, ni directorios nuevos)."""
        combined = self.combined_output(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"RU-2: el `{which}` con la MISMA clave y cuerpo "
                f"distinto debe ser RECHAZADO (rc≠0, conflicto "
                f"split-brain como corresponde); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

        after = self.continuity_snapshot()
        added = sorted(set(after) - set(before))
        changed = sorted(k for k in set(after) & set(before)
                         if after[k] != before[k])
        removed = sorted(set(before) - set(after))
        self.assertEqual(
            after, before,
            msg=f"RU-2 (todo o nada): un `{which}` RECHAZADO no escribe "
                f"nada — el árbol `{CONTINUITY_DIR_REL}` queda BYTE-A-"
                f"BYTE igual que antes; archivos NUEVOS filtrados por el "
                f"rechazo: {added!r}; modificados: {changed!r}; "
                f"eliminados: {removed!r} (stdout+stderr={combined[:400]!r}"
                f")")
        self.assertEqual(
            self.continuity_dirs(), dirs_before,
            msg=f"RU-2: un `{which}` RECHAZADO no crea directorios "
                f"nuevos bajo `{CONTINUITY_DIR_REL}`; got "
                f"{self.continuity_dirs()!r} vs {dirs_before!r}")
        self.assertEqual(
            self.head_bytes(), head_before,
            msg=f"RU-2 (ni cabeza): el head `{HEAD_REL}` queda byte a "
                f"byte intacto tras el `{which}` rechazado")

    def assert_reconcile_no_split_brain(
            self, proc: subprocess.CompletedProcess) -> None:
        """Consecuencia RU-2: el rechazo no deja cuerpos duplicados, así
        que `reconcile --packet` de la clave NO da split-brain (rc=0,
        clasificación sin error de divergencia)."""
        combined = self.combined_output(proc)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"RU-2: tras un rechazo todo-o-nada, `reconcile --packet` "
                f"de la clave NO queda bloqueado en split-brain (rc=0); "
                f"got rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")
        env = json.loads(proc.stdout.decode("utf-8"))
        self.assertNotEqual(
            env.get("classification"), "split-brain",
            msg=f"RU-2: la clasificación NO es split-brain (no hay dos "
                f"cuerpos para la misma clave); got "
                f"{env.get('classification')!r} (full={env!r})")
        self.assertNotIn(
            "divergent checkpoint heads", combined,
            msg=f"RU-2: la salida de `reconcile` NO contiene el error de "
                f"divergencia permanente (`divergent checkpoint heads`); "
                f"got stdout+stderr={combined[:400]!r}")


# ---------------------------------------------------------------- tests


class TestRU2CheckpointFacetaP5(Ru2RefusedWriteCase):
    """Faceta checkpoint RE-ESPECIFICADA por P5/D5 de 003-007 (BL-2,
    plan.md T2): el `checkpoint` con la clave del head y cuerpo distinto
    se APENDEA como eslabón nuevo — ya no se rechaza. La semántica de
    rechazo todo-o-nada NO cambia: sobrevive intacta en la faceta
    `begin` divergente (abajo) y en los cierres R-B1/D4/P7 de 003-004."""

    def test_t4_ru2_checkpoint_misma_clave_apendea_eslabon_p5(self) -> None:
        """P5/D5 (BL-2; trazabilidad: spec.md 003-007 §3 P5/P6/D5, plan.md
        T2): `begin` válido; `checkpoint` con la MISMA clave
        `(packet_id, attempt)` y cuerpo distinto → rc 0 y se APENDEA
        como eslabón nuevo: `seq` crece exactamente 1,
        `prev_checkpoint_sha256` = body_sha256 del head previo,
        `body_sha256` nuevo, `attempt`/`packet_id` sin cambiar, el
        eslabón previo permanece byte a byte en `bodies/` y `head.json`
        refleja la envolvente del eslabón nuevo; después `reconcile
        --packet` de esa clave NO da split-brain (rc=0; el escenario
        post-append de la abstención aceptada vive en
        tests/test_003_007_t2_checkpoint_vs_begin.py).

        Cambio de resultado POR DISEÑO (BL-2): el cierre original RU-2
        exigía aquí rc≠0 con el árbol byte-a-byte intacto; P5 sustituye
        la semántica de rechazo del checkpoint. Hoy el checkpoint sigue
        rechazándose (rc=1, split-brain) → RED por comportamiento
        presente-incorrecto (AssertionError que nombra P5), nunca import
        ni sintaxis."""
        head_before = self.begin_valid()
        head_doc_before = json.loads(head_before)
        before = self.continuity_snapshot()
        dirs_before = self.continuity_dirs()
        self.assertIn(
            BODIES_DIR_REL, dirs_before,
            msg="P5 (precondición): el `begin` válido creó `bodies/` "
                "— el append compara contra un store real, no vacío")

        divergent = self.write_update(
            update_fixture(
                goal="CHECKPOINT de limite del MISMO attempt 1 (cuerpo "
                     "distinto, misma clave — P5 lo apendea)"),
            name="update-divergente.json")

        proc = self.run_write("checkpoint", divergent)
        self.assert_command_exists(proc, "checkpoint")
        combined = self.combined_output(proc)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"P5 (BL-2): el `checkpoint` con la clave del head y "
                f"cuerpo distinto se APENDEA como eslabón nuevo (rc 0) —"
                f" ya NO se rechaza como split-brain; got "
                f"rc={proc.returncode} stdout={proc.stdout!r} "
                f"stderr={proc.stderr!r}")

        env = json.loads(proc.stdout.decode("utf-8"))
        self.assertEqual(
            env.get("seq"), head_doc_before.get("seq", 0) + 1,
            msg=f"P5: el eslabón apendeado lleva `seq` = head.seq + 1 "
                f"({head_doc_before.get('seq', 0) + 1}); got "
                f"{env.get('seq')!r}")
        self.assertEqual(
            env.get("prev_checkpoint_sha256"),
            head_doc_before.get("body_sha256"),
            msg=f"P5: `prev_checkpoint_sha256` del eslabón nuevo es el "
                f"BODY del head previo "
                f"({head_doc_before.get('body_sha256')!r}); got "
                f"{env.get('prev_checkpoint_sha256')!r}")
        self.assertNotEqual(
            env.get("body_sha256"), head_doc_before.get("body_sha256"),
            msg="P5: el eslabón nuevo tiene `body_sha256` propio "
                "(content-addressed)")
        self.assertEqual(
            (env.get("packet_id"), env.get("attempt")),
            (PACKET_ID, 1),
            msg=f"P5: el eslabón apendeado conserva la clave "
                f"(packet_id={PACKET_ID!r}, attempt=1); got "
                f"{(env.get('packet_id'), env.get('attempt'))!r}")

        head_after = json.loads(self.head_bytes())
        head_after_keys = (head_after.get("seq"),
                           head_after.get("body_sha256"))
        self.assertEqual(
            (head_after.get("seq"), head_after.get("body_sha256")),
            (env.get("seq"), env.get("body_sha256")),
            msg=f"P5: `head.json` refleja el eslabón nuevo (seq/body); "
                f"got {head_after_keys!r}")

        after = self.continuity_snapshot()
        prev_body_rel = (f"{BODIES_DIR_REL}/"
                         f"{head_doc_before.get('body_sha256')}.json")
        self.assertIn(
            prev_body_rel, after,
            msg=f"P5: el eslabón previo ({prev_body_rel!r}) permanece en "
                f"`bodies/` tras el append (evidencia intacta)")
        self.assertEqual(
            after.get(prev_body_rel), before.get(prev_body_rel),
            msg="P5: el eslabón previo queda byte a byte intacto")

        proc_recon = self.run_reconcile()
        self.assert_command_exists(proc_recon, "reconcile")
        self.assert_reconcile_no_split_brain(proc_recon)


class TestRU2BeginDivergente(Ru2RefusedWriteCase):
    """RU-2 faceta begin (escenario c) — todo o nada."""

    def test_t4_ru2_begin_divergente_no_escribe_nada_y_reconcile_no_split_brain(
            self) -> None:
        """RU-2 (c): lo mismo para un `begin` divergente con la MISMA
        clave `(packet_id, attempt)` — rc≠0, árbol `continuity/` byte a
        byte intacto (ningún cuerpo huérfano, head intacto, ningún
        directorio nuevo) y `reconcile --packet` posterior sin
        split-brain. Hoy el cuerpo divergente QUEDA escrito → RED por
        comportamiento presente-incorrecto."""
        head_before = self.begin_valid()
        before = self.continuity_snapshot()
        dirs_before = self.continuity_dirs()

        divergent = self.write_update(
            update_fixture(
                goal="VARIANTE divergente del MISMO attempt 1 (sesión "
                     "bifurcada simulada — fixture de datos)"),
            name="update-divergente.json")

        proc = self.run_write("begin", divergent)
        self.assert_command_exists(proc, "begin")
        self.assert_refused_writes_nothing(
            proc, "begin", before, dirs_before, head_before)

        proc_recon = self.run_reconcile()
        self.assert_command_exists(proc_recon, "reconcile")
        self.assert_reconcile_no_split_brain(proc_recon)


if __name__ == "__main__":
    unittest.main()
