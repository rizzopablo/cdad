#!/usr/bin/env python3
"""003-004 T4 RED (RU-1) — CLI con el contexto REAL de 001 y autoridad
desde el state (P2/D4; review-t4-ru1-decision.md; continuity-ledger RU-1).

Contract:
- docs/specs/003-004-context-continuity/spec.md (§3 firma V6; D4: "Autoridad
  y vigencia se leen del estado estructurado; no se parsea la prosa";
  P2: "no hereda delegaciones expiradas"; criterio 9/P8: adopción real).
- docs/specs/003-004-context-continuity/review-t4-ru1-decision.md
  (decisión del orquestador: identidad desde `execution.id` con compat
  del `execution_id` plano; autoridad desde `docs/.cdad-state.json`
  (`hitl_delegation`) SOLO por campos estructurados; `authority_ref` =
  `source`; revoked_at o status≠active → expired; sin delegación →
  unknown; sin ninguna identidad → falla cerrado).
- docs/specs/003-004-context-continuity/continuity-ledger.md (RU-1:
  `begin` real → rc 1 "execution_id must be a safe path segment … None":
  defecto de integración que los fixtures sintéticos no detectaron).

Defecto (RU-1): el contexto real que publica 001 tiene la forma
`{"execution": {"id": …, …}, "path_policy": …, "policy": …,
"policy_history": …}` — SIN `execution_id` plano y SIN
`hitl_delegation` — y la delegación vive en el state con la forma
`{delegated_to, requested_by, requested_at, scope, expires (texto por
eventos), publication, source}`, sin `expires_on` de fecha. Este RED
clava esa forma REAL como superficie observable.

Superficie bajo prueba (§3/V6, ya fijada por T1–T3):

    python3 scripts/cdad_continuity.py begin \
        --project-root ROOT --execution-context EXEC.json --update U.json
    python3 … resume  --project-root ROOT --execution-context EXEC.json
    python3 … reconcile --project-root ROOT --execution-context EXEC.json \
        --packet PACKET_ID

Tests (uno por caso de la decisión, cada uno mapeado):

1. `test_ru1_active_begin_rc0_con_forma_real_de_001`
   → P8/criterio 9 + D4: `begin` con la forma real de 001 y un state
   con delegación activa POR EVENTOS (prosa en `expires`, sin
   `expires_on`) termina rc 0, crea el head bajo
   `.cdad/executions/<execution.id>/continuity/` y NUNCA escribe el
   state (D3).
2. `test_ru1_active_resume_reporta_autoridad_active_desde_state`
   → P2/D4: `resume` reconstruye la autoridad desde el STATE (el
   contexto no trae `hitl_delegation`): `authority.state = "active"` y
   `authority_ref` = el `source` de la delegación. La prosa de
   `expires` no se parsea como fecha (la delegación vence por eventos
   y sigue activa).
3. `test_ru1_revocado_begin_falla_cerrado_y_reconcile_expired_authority`
   → D4/P2 (§2 "Autoridad vencida"): state con `revoked_at` → `begin`
   falla cerrado (rc≠0, delta que NOMBRA la vigencia vencida, sin head)
   y `reconcile` clasifica `expired-authority` con
   `authority.state = "expired"` y `repeat_effect: false` (read-only).
4. `test_ru1_sin_identidad_ejecucion_falla_cerrado`
   → RU-1 ("Si faltan ambos, falla cerrado"): contexto sin
   `execution.id` NI `execution_id` → rc≠0 con delta que nombra la
   identidad faltante, sin traceback.

Focales con stdin cerrado (DEVNULL), SIEMPRE foreground (nunca
background); fixtures en tmp (SIMULACIÓN), ninguna escritura en este
repo, ningún incidente real.

RED hoy (probes observables del CLI actual, 2026-10-07): el CLI existe
(T1–T3 cerrados) pero RECHAZA la forma real de 001 (rc≠0 "execution_id
must be a safe path segment … None"): los casos 1–3 fracasan por
comportamiento ausente (AssertionError que nombra el elemento violado);
el caso 4 es el guard de falla-cerrado que NO debe regresar cuando el
GREEN agregue la forma anidada. Nunca ImportError ni sintaxis: el test
no importa el módulo del CLI.
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

FEATURE_ID = "003-004-context-continuity"
EPIC_ID = "epic-003-context-efficiency"

# La ejecución REAL de la adopción (continuity-ledger RU-1): mismo id,
# misma autoridad — el fixture vive en tmp (SIMULACIÓN, sin efectos).
EXEC_ID = "exec-003-004-context-continuity-001"
PACKET_ID = "003-004-context-continuity-implementer-ru1-001"

AUTHORITY_REF = "docs/epics/epic-003-context-efficiency/execution.md"

CLI_TIMEOUT_S = 120

EXEC_DIR_REL = f".cdad/executions/{EXEC_ID}"
CONTINUITY_DIR_REL = f"{EXEC_DIR_REL}/continuity"
HEAD_REL = f"{CONTINUITY_DIR_REL}/head.json"
STATE_REL = "docs/.cdad-state.json"
POLICY_REL = "docs/cdad-policy.json"

GOAL = "Adopción real RU-1: begin con el contexto real de 001"
NEXT_ACTION = "Repetir begin real y la reanudación en frío"
DECISION_TEXT = "Autoridad leída del state estructurado (D4)"
DECISION_RATIONALE = "La prosa del archivo de autoridad no se parsea"


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
    """Forma REAL del execution.json que publica 001 (RU-1): identidad
    anidada en `execution.id`, SIN `execution_id` plano, SIN
    `hitl_delegation`, con `policy_history` como lista."""
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


def state_fixture(**delegation_overrides: object) -> dict:
    """Forma REAL del `hitl_delegation` del state (review-t4-ru1):
    vence POR EVENTOS (prosa en `expires`, sin `expires_on` de fecha)."""
    delegation = {
        "delegated_to": "orchestrator",
        "requested_by": "user (pablo)",
        "requested_at": "2026-10-07T00:00:00Z",
        "scope": EPIC_ID,
        "expires": "vence por eventos; 001 valida la vigencia en prepare",
        "publication": "docs/specs/003-004-context-continuity/spec.md",
        "source": AUTHORITY_REF,
    }
    delegation.update(delegation_overrides)
    return {"schema_version": 1, "hitl_delegation": delegation}


def update_fixture(**overrides: object) -> dict:
    """Cuerpo D11 (forma de T1/T2)."""
    doc = {
        "packet_id": PACKET_ID,
        "attempt": 1,
        "goal": GOAL,
        "decisions": [
            {"decision": DECISION_TEXT, "rationale": DECISION_RATIONALE},
        ],
        "uncertainties": ["V2: el status de sesión no distingue "
                          "vivo-estancado"],
        "next_action": NEXT_ACTION,
        "references": [],
    }
    doc.update(overrides)
    return doc


# ---------------------------------------------------------------- helpers


class RealContextCase(unittest.TestCase):
    """Proyecto sintético con la forma REAL de 001 y state con
    delegación (la autoridad NUNCA viaja en el execution context)."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-004-t4ru1-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        self.root.mkdir(parents=True, exist_ok=True)

    # -- construcción del proyecto fixture -----------------------------

    def build_real_project(
            self, *, state_overrides: dict | None = None) -> None:
        """Proyecto con el contexto REAL de 001 + policy + state."""
        policy_path = self.write_json(POLICY_REL, policy_doc_fixture())
        policy_sha = hashlib.sha256(policy_path.read_bytes()).hexdigest()
        self.exec_context = self.write_json(
            "fixture/exec.json", real_exec_context_fixture(policy_sha))
        state = state_fixture(**(state_overrides or {}))
        self.state_path = self.write_json(STATE_REL, state)

    def build_real_project_without_identity(self) -> None:
        """Variante: el contexto pierde TANTA `execution.id` como el
        `execution_id` plano (falla cerrado, RU-1)."""
        self.build_real_project()
        context = json.loads(
            (self.root / "fixture/exec.json").read_text(encoding="utf-8"))
        del context["execution"]["id"]
        self.exec_context = self.write_json("fixture/exec.json", context)

    def write_json(self, rel: str, doc: dict) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        return path

    def write_update(self, doc: dict) -> Path:
        return self.write_json("fixture/update.json", doc)

    def snapshot(self) -> dict[str, bytes]:
        """Snapshot de archivos del proyecto (read-only de `reconcile`
        y D3 "el CLI nunca escribe el state" se verifican contra esto)."""
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in sorted(self.root.rglob("*")) if p.is_file()
        }

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
                "RU-1 (acotado): el CLI no terminó dentro de "
                f"{CLI_TIMEOUT_S}s — un comando determinista nunca "
                f"puede colgarse; got timeout={exc!r}")

    def run_write(self, command: str, update: Path) -> (
            subprocess.CompletedProcess):
        return self.run_cli(command, "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--update", str(update), "--json")

    def run_resume(self) -> subprocess.CompletedProcess:
        return self.run_cli("resume", "--project-root", str(self.root),
                            "--execution-context", str(self.exec_context),
                            "--json")

    def run_reconcile(self) -> subprocess.CompletedProcess:
        return self.run_cli("reconcile", "--project-root", str(self.root),
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
            msg=f"RU-1: el comando `{which}` no existe aún (RED por CLI "
                "ausente): el argv `cdad_continuity.py " + which +
                "` declarado en §3 (V6) es obligatorio")
        self.assertNotIn(
            "Traceback", combined,
            msg=f"RU-1: `{which}` terminó con traceback "
                f"(stderr={proc.stderr.decode('utf-8', errors='replace')!r})")
        self.assertEqual(
            proc.returncode, 0,
            msg=f"RU-1/LEDGER: `{which}` con la forma REAL de 001 "
                f"(execution.id, sin execution_id plano, sin "
                f"hitl_delegation) no existe en comportamiento aún — "
                f"defecto RU-1: rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")

    def write_envelope(self, proc: subprocess.CompletedProcess,
                       which: str) -> dict:
        self.assert_command_exists(proc, which)
        return json.loads(proc.stdout.decode("utf-8"))

    def head_document(self) -> dict:
        head = self.root / HEAD_REL
        self.assertTrue(
            head.is_file(),
            msg="RU-1 (precondición): el head vive bajo "
                f"`{HEAD_REL}` (la identidad sale de `execution.id` "
                "anidado, no de un execution_id plano)")
        return json.loads(head.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- tests


class TestRU1FormaRealActiva(RealContextCase):
    """RU-1 caso activo — begin rc 0 con la forma real de 001 y
    autoridad por eventos desde el state (P8/criterio 9, D4, D3)."""

    def test_ru1_active_begin_rc0_con_forma_real_de_001(self) -> None:
        """P8/criterio 9 + D4/D3: `begin` con el execution.json REAL de
        001 (identidad en `execution.id`, sin `execution_id` plano, sin
        `hitl_delegation`) y un state con delegación activa POR EVENTOS
        termina rc 0, crea el head bajo
        `.cdad/executions/<execution.id>/continuity/` y el state queda
        BYTE-A-BYTE intacto (el CLI nunca lo escribe, D3)."""
        self.build_real_project()
        before = self.snapshot()

        proc = self.run_write("begin", self.write_update(update_fixture()))
        env = self.write_envelope(proc, "begin")

        self.assertEqual(
            env.get("execution_id"), EXEC_ID,
            msg="RU-1: la identidad del head sale del `execution.id` "
                f"anidado del contexto real; got {env!r}")
        self.head_document()

        after = self.snapshot()
        self.assertEqual(
            after.get(STATE_REL), before.get(STATE_REL),
            msg="D3/LEDGER: `begin` NUNCA escribe docs/.cdad-state.json "
                "(único escritor: el orquestador); got cambio en el "
                "state tras begin")

    def test_ru1_active_resume_reporta_autoridad_active_desde_state(
            self) -> None:
        """P2/D4: con el contexto SIN `hitl_delegation`, `resume` lee la
        autoridad del STATE estructurado y la reporta activa con
        `authority_ref` = el `source` de la delegación. La prosa de
        `expires` (vencimiento por eventos) NO se parsea como fecha:
        sigue `active`."""
        self.build_real_project()
        self.write_envelope(
            self.run_write("begin", self.write_update(update_fixture())),
            "begin")

        proc = self.run_resume()
        env = self.write_envelope(proc, "resume")
        projection = env.get("projection")
        self.assertIsInstance(
            projection, dict,
            msg=f"P2: `resume` expone la proyección L1; got {env!r}")

        authority = projection.get("authority")
        self.assertIsInstance(
            authority, dict,
            msg=f"D4/LEDGER: la autoridad se reconstruye DESDE EL STATE "
                f"(el contexto real no trae hitl_delegation); got "
                f"projection={projection!r}")
        self.assertEqual(
            (authority or {}).get("state"), "active",
            msg="D4/LEDGER: delegación presente con `source` y sin fecha "
                "(vence por eventos) → `active`; la prosa de `expires` "
                f"NUNCA se parsea como fecha; got {(authority or {})!r}")
        self.assertEqual(
            (authority or {}).get("authority_ref"), AUTHORITY_REF,
            msg="D4: `authority_ref` = el `source` de la delegación del "
                f"state ({AUTHORITY_REF!r}); got {(authority or {})!r}")


class TestRU1Revocado(RealContextCase):
    """RU-1 caso revocado — `revoked_at` en el state: begin falla
    cerrado (D4) y reconcile clasifica `expired-authority` (P2, §2)."""

    def test_ru1_revocado_begin_falla_cerrado_y_reconcile_expired_authority(
            self) -> None:
        """D4/P2: state con `revoked_at` → (a) `begin` falla cerrado
        rc≠0 con un delta que NOMBRA la vigencia vencida (nunca un
        rc≠0 incidental por otra causa) y SIN crear head; (b)
        `reconcile` clasifica `expired-authority` con
        `authority.state = "expired"` y `repeat_effect: false`,
        read-only (invariante 1)."""
        overrides = {"revoked_at": "2026-10-07T09:00:00Z"}

        # (a) begin falla cerrado POR LA VIGENCIA (no por otra causa).
        self.build_real_project(state_overrides=overrides)
        before = self.snapshot()
        proc = self.run_write("begin", self.write_update(update_fixture()))
        combined = self.combined_output(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="D4/§2: con la delegación REVOCADA en el state `begin` "
                f"falla cerrado; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertIn(
            "expired", combined.lower(),
            msg="D4/§2: el delta de `begin` revocado NOMBRA la vigencia "
                "vencida (expired) — no un rc≠0 incidental por otra "
                f"causa; got stdout+stderr={combined[:800]!r}")
        self.assertFalse(
            (self.root / HEAD_REL).exists(),
            msg="D4: `begin` revocado falla ANTES de escribir "
                "(sin head en el store de continuity)")
        self.assertEqual(
            self.snapshot().get(STATE_REL), before.get(STATE_REL),
            msg="D3: el CLI nunca escribe el state, tampoco al fallar")

        # (b) reconcile clasifica `expired-authority` desde el state.
        self.build_real_project(state_overrides=overrides)
        before = self.snapshot()
        proc = self.run_reconcile()
        env = self.write_envelope(proc, "reconcile")
        self.assertEqual(
            env.get("classification"), "expired-authority",
            msg="D4/§2: la delegación revocada (revoked_at en el state) "
                "se clasifica `expired-authority`; got "
                f"{env.get('classification')!r} (full={env!r})")
        authority = env.get("authority")
        self.assertEqual(
            (authority or {}).get("state"), "expired",
            msg=f"D4: `authority.state` = `expired` (desde el state); "
                f"got {(authority or {})!r}")
        self.assertIs(
            env.get("repeat_effect"), False,
            msg="D4/P2: con autoridad vencida NADA se autoriza "
                "(repeat/dispatch/materialize quedan fuera)")
        self.assertEqual(
            self.snapshot(), before,
            msg="invariante 1: `reconcile` read-only también con "
                "autoridad vencida")


class TestRU1SinIdentidad(RealContextCase):
    """RU-1 caso sin identidad — ni `execution.id` ni `execution_id`
    plano: falla cerrado (nunca adivinar ni fabricar)."""

    def test_ru1_sin_identidad_ejecucion_falla_cerrado(self) -> None:
        """RU-1/LEDGER: contexto sin `execution.id` NI `execution_id` →
        `begin` rc≠0 con delta que NOMBRA la identidad faltante y sin
        traceback (falla cerrado, no un crash)."""
        self.build_real_project_without_identity()
        proc = self.run_write("begin", self.write_update(update_fixture()))
        combined = self.combined_output(proc)

        self.assertNotEqual(
            proc.returncode, 0,
            msg="RU-1: sin ninguna identidad de ejecución `begin` falla "
                f"cerrado; got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertIn(
            "execution_id", combined,
            msg="RU-1: el delta nombra la identidad faltante "
                "(execution_id/execution.id); got "
                f"stdout+stderr={combined[:800]!r}")
        self.assertNotIn(
            "Traceback", combined,
            msg="RU-1: la falla cerrada NO es un traceback sin manejar")


if __name__ == "__main__":
    unittest.main()
