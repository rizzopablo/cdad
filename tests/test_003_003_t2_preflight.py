#!/usr/bin/env python3
"""003-003 T2 RED — pre-flight de capacidad/permisos + acotado de rechazos.

Contract:
- docs/specs/003-003-progress-guards/spec.md (P3; D6; O2; invariantes 1 y 2)
- docs/specs/003-003-progress-guards/plan.md (T2; test focal declarado
  `tests/test_003_003_t2_preflight.py`).

Superficie observable bajo prueba (V7: forma del CLI fijada en RED; §3):

    python3 scripts/cdad_guard.py preflight \
        --project-root ROOT \
        --execution-context EXEC.json \
        --role ROLE \
        --operation OP         # JSON string: {"tool": "...", "path": "..."}
        [--json]

Envolvente de salida (JSON en stdout con --json, contract `preflight-v1`):

    {
      "schema_version": 1,
      "preflight": "preflight-v1",
      "role": "test-writer",
      "operation": {"tool": "...", "path": "..."},
      "decision": "allow" | "deny",
      "denied_by": "policy" | "role-scope",   # solo en deny
      "reason": "<diagnóstico accionable no vacío>"
    }

Semántica fijada por este RED (spec §3 y D6):

- El pre-flight **lee** `ROOT/docs/cdad-policy.json` + execution context
  (rol + scopes) y prevalida la operación ANTES de llamarla. Es lectura,
  nunca escritura de la política (O2).
- Operación declarada denegada por la política (p. ej. `private_paths`)
  o fuera del scope del rol → **deny**: rc≠0, diagnóstico accionable por
  stderr y envolvente COMPLETA en stdout con --json (sin salida parcial).
- Operación legítima (dentro del write_scope del rol) → **allow**: rc 0.
  Un deny de operación legítima es un DEFECTO DEL PRODUCTO: este test lo
  captura como falla, no lo normaliza.
- Acotado: prevalidar la MISMA operación denegada N veces produce SIEMPRE
  la misma decisión única y acotada (determinista, sin deriva de
  contador). Nunca auto-grant ni auto-harden: un rechazo NO implica mala
  conducta y la política no se endurece ni se relaja sola (invariante 2,
  D3, ADR-011).

Fixtures: política y execution context PROPIOS en tmp — el test no
depende de `docs/cdad-policy.json` real del repo (nota del orquestador).
Los escenarios de denegación son simulación sobre un proyecto sintético:
no se provoca ningún incidente real (P6, plan.md:173-176).

Estado del ciclo (O-B, actualizado post-GREEN): el subcomando
`preflight` EXISTE y este RED T2 ya fue verificado en verde — commit
GREEN `2204bab` (verificado con `4 passed` en local). Esta suite ya no
está en fase RED: es la oráculo GREEN de P3/O2 vigente. La fase RED
activa de la ronda review-fix vive aparte en
`tests/test_003_003_t2_reviewfix.py` (F1 de `review-t2-decision.md`,
puntos 1-5 + caso positivo read-in-read_scope), cuyas aserciones
fracasan por AssertionError contra `2204bab`, nunca por ImportError —
el test no importa el módulo del guard.

Fuera de este RED (resuelto en review): la semántica read/write por
herramienta y las variantes de ruta mediadas por patrón (V6,
`t7-live-walk.md:38-66`) se fijaron en `review-t2-decision.md` (F1,
puntos 1-5) y sus focales están en el reviewfix RED citado. La
diferenciación del mapa de rol queda declarada como limitación en el
contrato `preflight-v1` (O-D, deuda baja), no reimplementada aquí.
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
CONTRACT = "preflight-v1"

# El pre-flight nunca debe colgarse: tope duro que demuestra terminación
# (acotado — "nunca existe loop ilimitado de la misma llamada denegada").
PREFLIGHT_TIMEOUT_S = 120

# ---------------------------------------------------------------- fixtures

POLICY_FIXTURE = {
    "schema_version": 1,
    "path_policy": {
        "documentation_roots": ["docs"],
        "documentation_files": ["README.md"],
        "implementation_roots": ["agents", "skills", "scripts", "sources",
                                 "build"],
        "implementation_files": ["install.sh"],
        "test_roots": ["tests"],
        "private_paths": ["secrets/credentials.local"],
        "temporary_roots": [],
    },
}

EXEC_CONTEXT_FIXTURE = {
    "schema_version": 1,
    "execution_id": "exec-003-003-t2-red-001",
    "packet_id": "003-003-progress-guards-test-writer-red-003",
    "runtime": "opencode",
    "role": "test-writer",
    "write_scope": [{"class": "tests", "root": "tests"}],
    "read_scope": [
        {"class": "contract", "root": "docs/specs/003-003-progress-guards"},
        {"class": "tests", "root": "tests"},
    ],
}

# Operación de prueba 1 — edición FUERA del scope del rol test-writer
# (raíz de implementación declarada en la política): prevalidable ANTES
# de llamar (D6: "operación declarada denegada o fuera de raíz").
OP_OUT_OF_ROLE = {"tool": "edit",
                  "path": "skills/cdad-cycle/scripts/cdad_guard.py"}

# Operación de prueba 2 — ruta PRIVADA declarada en la política: denegada
# por política con independencia del rol (prevalidación contra política).
OP_PRIVATE = {"tool": "read", "path": "secrets/credentials.local"}

# Operación de prueba 3 — LEGÍTIMA para el rol (dentro de su write_scope
# `tests`): el pre-flight NO debe denegarla (deny de legítima = defecto).
OP_LEGIT = {"tool": "edit", "path": "tests/test_003_003_t2_preflight.py"}


# ---------------------------------------------------------------- helpers


class EstablishedProjectCase(unittest.TestCase):
    """Proyecto sintético (tempdir) con política y contexto propios."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-003-003-t2-red-")
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        # Política PROPIA del fixture (O2: leída, nunca la real del repo).
        self.policy_path = self.root / "docs" / "cdad-policy.json"
        self.policy_path.parent.mkdir(parents=True, exist_ok=True)
        self.policy_path.write_text(
            json.dumps(POLICY_FIXTURE, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        # Execution context del rol (001): rol + scopes declarados.
        self.exec_context = self.root / "fixture" / "exec.json"
        self.exec_context.parent.mkdir(parents=True, exist_ok=True)
        self.exec_context.write_text(
            json.dumps(EXEC_CONTEXT_FIXTURE, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        # Árbol mínimo coherente con la política.
        (self.root / "tests").mkdir(exist_ok=True)
        (self.root / "tests" / "existing_test.py").write_text("# fixture\n",
                                                              encoding="utf-8")
        (self.root / "skills").mkdir(exist_ok=True)
        (self.root / "skills" / "lib.py").write_text("# fixture\n",
                                                     encoding="utf-8")
        (self.root / "secrets").mkdir(exist_ok=True)
        (self.root / "secrets" / "credentials.local").write_text(
            "# fixture privado\n", encoding="utf-8")

    def run_preflight(self, op: dict, *,
                      role: str = "test-writer",
                      json_out: bool = True) -> subprocess.CompletedProcess:
        """Corrida del CLI preflight (V7) con tope de tiempo (acotado)."""
        argv = [sys.executable, str(GUARD_SCRIPT), "preflight",
                "--project-root", str(self.root),
                "--execution-context", str(self.exec_context),
                "--role", role,
                "--operation", json.dumps(op, sort_keys=True)]
        if json_out:
            argv.append("--json")
        try:
            return subprocess.run(
                argv, cwd=REPO_ROOT, capture_output=True,
                timeout=PREFLIGHT_TIMEOUT_S)
        except subprocess.TimeoutExpired as exc:  # pragma: no cover
            self.fail(
                "P3 (acotado): el pre-flight no terminó dentro de "
                f"{PREFLIGHT_TIMEOUT_S}s — un prevalidador determinista "
                f"nunca puede colgarse; got timeout={exc!r}")

    def assert_command_exists(self, proc: subprocess.CompletedProcess) -> None:
        """RED: el fracaso debe ser el comportamiento ausente, con mensaje
        explícito — nunca un fallo de import o sintaxis."""
        out = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        combined = out + err
        self.assertNotIn(
            "invalid choice", combined,
            msg="P3: el comando `preflight` no existe aún (RED por CLI "
                "ausente): el argv `preflight --project-root "
                "--execution-context --role --operation` declarado en §3 "
                "es obligatorio")
        self.assertNotIn(
            "unrecognized", combined,
            msg="P3: el comando `preflight` no existe aún (RED por CLI "
                "ausente): el argv declarado en §3 es obligatorio")
        self.assertNotIn(
            "Traceback", err,
            msg="P3: preflight no puede terminar con traceback; "
                f"stderr={err!r}")

    def preflight_envelope(self, proc: subprocess.CompletedProcess) -> dict:
        """Exige envolvente `preflight-v1` COMPLETA y parseable en stdout."""
        self.assert_command_exists(proc)
        raw = proc.stdout.decode("utf-8", errors="replace").strip()
        self.assertTrue(
            raw,
            msg="P3: con --json el pre-flight debe emitir la envolvente "
                "preflight-v1 COMPLETA en stdout (sin salida parcial); "
                f"stdout vacío con rc={proc.returncode} "
                f"stderr={proc.stderr!r}")
        try:
            env = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.fail(
                "P3 (sin salida parcial): la salida de preflight --json "
                "debe ser un único documento JSON completo; got "
                f"{raw!r} ({exc})")
        self.assertEqual(
            env.get("preflight"), CONTRACT,
            msg=f"P3: la envolvente debe declarar el contrato {CONTRACT}; "
                f"got={env.get('preflight')!r}")
        self.assertEqual(
            env.get("schema_version"), 1,
            msg="P3: la envolvente preflight-v1 debe declarar "
                "schema_version=1")
        return env


# ---------------------------------------------------------------- tests


class TestP3BoundedPrevalidation(EstablishedProjectCase):
    """P3 — rechazos prevalidados contra política y rol, acotados, sin
    loop ilimitado de la misma llamada denegada."""

    def test_p03_operacion_fuera_de_rol_se_prevalida_acotada(self) -> None:
        """P3: edición en raíz de implementación por test-writer (fuera de
        su write_scope) → deny ANTES de llamar: rc≠0, diagnóstico accionable
        por stderr, envolvente completa con `decision=deny` y `reason` no
        vacía.

        Acotado (P3): repetir la MISMA prevalidación denegada produce la
        MISMA decisión única (rc y salida idénticos) — sin deriva por
        contador, sin escalada automática, sin loop."""
        before = tree_snapshot(self.root)

        proc = self.run_preflight(OP_OUT_OF_ROLE)
        self.assert_command_exists(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P3: operación fuera del scope del rol debe prevalidarse "
                "como deny (rc≠0) ANTES de ejecutarla; got "
                f"rc={proc.returncode} stdout={proc.stdout!r}")
        self.assertTrue(
            proc.stderr.strip(),
            msg="P3: el deny debe llevar diagnóstico accionable por stderr "
                "(spec §3: violación → rc≠0 con diagnóstico por stderr)")
        env = self.preflight_envelope(proc)

        self.assertEqual(
            env.get("decision"), "deny",
            msg="P3: la envolvente debe declarar decision=deny para una "
                "operación fuera del scope del rol")
        self.assertEqual(
            env.get("role"), "test-writer",
            msg="P3: la prevalidación es contra política Y ROL — la "
                "envolvente debe exponer el rol evaluado")
        self.assertEqual(
            env.get("operation"), OP_OUT_OF_ROLE,
            msg="P3: la envolvente debe exponer la operación evaluada "
                "(trazabilidad del rechazo)")
        reason = env.get("reason")
        self.assertIsInstance(
            reason, str, msg="P3: el deny debe traer un reason string")
        self.assertTrue(
            reason and reason.strip(),
            msg="P3: un rechazo acotado exige un diagnóstico (reason) no "
                "vacío y accionable — nunca un deny mudo")
        self.assertTrue(
            OP_OUT_OF_ROLE["path"] in reason or
            OP_OUT_OF_ROLE["path"] in proc.stderr.decode("utf-8",
                                                         errors="replace"),
            msg="P3: el diagnóstico debe referenciar la operación concreta "
                f"denegada ({OP_OUT_OF_ROLE['path']!r})")

        # Acotado: misma consulta repetida → misma decisión única, bytes
        # idénticos (determinista; la decisión NO crece ni se endurece).
        proc2 = self.run_preflight(OP_OUT_OF_ROLE)
        self.assertEqual(
            (proc2.returncode, proc2.stdout, proc2.stderr),
            (proc.returncode, proc.stdout, proc.stderr),
            msg="P3 (acotado): la MISMA llamada denegada prevalidada de "
                "nuevo debe producir la MISMA decisión única y acotada — "
                "sin loop, sin deriva de contador, sin escalada automática")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="P3 (invariante 1): el pre-flight es read-only — el árbol "
                "del proyecto no debe alterarse")

    def test_p03_ruta_privada_por_politica_se_deniega_antes_de_llamar(self) -> None:
        """P3 (prevalidación contra POLÍTICA): leer una ruta declarada en
        `private_paths` es deny por política con independencia del rol —
        detectada ANTES de ejecutar la operación (D6), con reason que lo
        declara (la política se lee, no se adivina)."""
        proc = self.run_preflight(OP_PRIVATE)
        self.assert_command_exists(proc)
        self.assertNotEqual(
            proc.returncode, 0,
            msg="P3: una ruta private_paths de la política debe "
                "prevalidarse como deny (rc≠0) antes de llamar; got "
                f"rc={proc.returncode} stdout={proc.stdout!r}")
        self.assertTrue(
            proc.stderr.strip(),
            msg="P3: el deny por política también exige diagnóstico por "
                "stderr")
        env = self.preflight_envelope(proc)
        self.assertEqual(
            env.get("decision"), "deny",
            msg="P3: la envolvente debe declarar decision=deny para una "
                "ruta privada de la política")
        self.assertEqual(
            env.get("denied_by"), "policy",
            msg="P3: la evidencia del rechazo debe distinguir POR QUÉ se "
                "deniega (política, no scope de rol) — campo `denied_by`")


class TestP3NoDenialOfLegitimateWork(EstablishedProjectCase):
    """P3 — el deny de una operación legítima es defecto del producto;
    el pre-flight no debe fabricarlo."""

    def test_p03_operacion_legitima_del_rol_se_permite(self) -> None:
        """P3: edición dentro del write_scope del rol (`tests/`) es una
        operación legítima → allow (rc 0). Un deny de operación legítima
        es un DEFECTO DEL PRODUCTO a escalar: el test lo captura como
        falla en vez de normalizarlo."""
        proc = self.run_preflight(OP_LEGIT)
        self.assert_command_exists(proc)
        self.assertEqual(
            proc.returncode, 0,
            msg="P3: deny de operación LEGÍTIMA (dentro del write_scope "
                "del rol) = defecto del producto — el pre-flight debe "
                f"permitirla (rc 0); got rc={proc.returncode} "
                f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        env = self.preflight_envelope(proc)
        self.assertEqual(
            env.get("decision"), "allow",
            msg="P3: la envolvente debe declarar decision=allow para una "
                "operación legítima del rol (sin falsos positivos)")


class TestP3PolicyIsReadNeverWritten(EstablishedProjectCase):
    """P3 + O2 + invariante 2 — la política se lee, no se escribe; nunca
    auto-grant ni auto-harden por repetición."""

    def test_p03_la_politica_no_se_escribe_y_nada_se_relaja_sola(self) -> None:
        """O2: tras prevalidar deny y allow, el archivo de política del
        proyecto queda BYTE A BYTE idéntico y el árbol read-only.

        Invariante 2 (sin auto-grant/auto-harden): tras repetir la
        operación denegada, esta SIGUE denegada con la misma decisión —
        ningún contador endurece ni relaja la política."""
        policy_before = self.policy_path.read_bytes()
        before = tree_snapshot(self.root)

        # Denegada dos veces (repetición de la misma llamada denegada)…
        proc_first = self.run_preflight(OP_OUT_OF_ROLE)
        self.assert_command_exists(proc_first)
        self.assertNotEqual(
            proc_first.returncode, 0,
            msg="P3 (precondición del oráculo): la operación fuera de rol "
                "debe prevalidarse como deny en la primera corrida; got "
                f"rc={proc_first.returncode} stdout={proc_first.stdout!r}")
        proc_denied = self.run_preflight(OP_OUT_OF_ROLE)
        self.assert_command_exists(proc_denied)
        # …y la legítima una vez.
        proc_legit = self.run_preflight(OP_LEGIT)
        self.assert_command_exists(proc_legit)
        self.assertEqual(
            proc_legit.returncode, 0,
            msg="P3 (precondición del oráculo): la operación legítima debe "
                "prevalidarse como allow (rc 0); got "
                f"rc={proc_legit.returncode} stdout={proc_legit.stdout!r}")

        self.assertEqual(
            self.policy_path.read_bytes(), policy_before,
            msg="O2 (P3): el pre-flight LEE docs/cdad-policy.json y nunca "
                "lo escribe — el archivo debe quedar idéntico byte a byte")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="O2/P3 (invariante 1): el pre-flight es read-only sobre el "
                "proyecto — sin escrituras colaterales")
        self.assertNotEqual(
            proc_denied.returncode, 0,
            msg="Invariante 2 (sin auto-grant/auto-harden): tras repetir "
                "la misma operación denegada, debe SEGUIR denegada con la "
                "misma decisión acotada — ningún contador concede o "
                "endurece permisos automáticamente")


if __name__ == "__main__":
    unittest.main()
