#!/usr/bin/env python3
"""004-002 T5/T6 REVIEW-FIX RED — hallazgos B6, B7/I11 y OPT-4 (review-t56.md).

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-2, PD-4, PD-5, PD-7/PD-8, PD-12) + review-t56.md ("Disposición del
orquestador": B6, B7, OPT-4) + plan.md (I11, I10).

Cada test deriva de un hallazgo del dictamen T5/T6 y su disposición
aprobada; cada aserción expresa la postcondición observable (comportamiento
del guard CC o del CLI), no la mecánica interna. Reutiliza por import los
fixtures de test_004_002_t5_runtime.py (LayoutProject), test_004_002_t3_durable.py
(DurableProjectCase: run_prepare/run_resume/run_reconcile argv puro) y
test_004_002_t2_bootstrap.py SIN modificarlos. No lee implementación: solo
la interfaz (CLI, guard con la forma real del JSON de hook).

Mapa test → hallazgo/postcondición (review-t56 → spec):

  TestB6GuardTildePaths (guard CC v2, HOME fijado a un tempdir):
    test_reviewfix_b6_guard_blocks_tilde_paths
      -> B6 (PD-2: una ruta `~` está fuera del proyecto, no es clasificable
         y no puede ampliar un scope → bloqueo; PD-8 "Fronteras": prueba
         negativa por las herramientas que realmente median — Read, Write,
         Grep, Glob; controles: rutas relativas internas siguen su regla
         de clase).
  TestB7ResumeAfterReconcile (CLI, I11):
    test_reviewfix_b7_resume_after_reconcile_names_revisions_and_new_packet
      -> B7/I11 (PD-4/PD-5 + plan I11: `--resume-packet` solo reanuda
         paquetes renderizados bajo la revisión de política aceptada; un
         paquete de una revisión anterior → rc 2, stdout vacío, diagnóstico
         que nombra ambas revisiones y pide preparar un paquete nuevo, sin
         escrituras; bytes de P1 conservados; un paquete posterior P2 se
         reanuda rc 0 con bytes idénticos).
  TestOpt4ArchitectWithoutEpic (CLI):
    test_reviewfix_opt4_architect_without_active_epic_diagnostic
      -> OPT-4 (PD-12: architect standalone sigue el camino legacy/intake;
         el rechazo explicita la falta de epic activo, sin fabricar la
         ruta «docs/epics/None/plan.md»).

RED hoy (post T5/T6 GREEN): B6 falla porque el guard v2 deja pasar rutas
`~` (rc 0 en vez de 2); B7 ya tiene rc 2, así que falla por el diagnóstico
(no menciona las dos revisiones de política); OPT-4 ya es rc≠0, así que
falla por el diagnóstico (contiene la ruta fabricada con `None`). Ninguna
falta de import ni de sintaxis: cada fallo es una AssertionError sobre la
postcondición ausente.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (  # noqa: E402
    POLICY_FILE,
    SCRIPT,
    policy_hash,
    published_packets,
    read_state,
    tree_snapshot,
)
from test_004_002_t3_durable import (  # noqa: E402
    DurableProjectCase,
    set_active_packet_status,
    state_bytes,
)
from test_004_002_t5_runtime import (  # noqa: E402
    CLI_ENV,
    GUARD,
    LayoutProject,
)

NEW_PACKET_RE = re.compile(
    r"(?i)new\s+packet|nuevo\s+paquete"
    r"|prepare\s+a\s+new\s+packet|preparar\s+(un|uno)\s+nuevo"
    r"|preparar\s+un\s+paquete\s+nuevo")


def run_guard_home(root: Path, role: str, tool_name: str, tool_input: dict,
                   *, home: Path) -> subprocess.CompletedProcess:
    """Guard CC con la forma REAL del hook JSON (fixture T5) y HOME fijado
    al tempdir indicado: B6 exige no depender del HOME real."""
    env = dict(os.environ)
    env[CLI_ENV] = str(SCRIPT)
    env["HOME"] = str(home)
    env.pop("CLAUDE_PROJECT_DIR", None)
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        ["bash", str(GUARD), role],
        input=payload, capture_output=True, text=True,
        cwd=str(root), env=env,
    )


# ------------------------------------------------------- guard CC: B6


class TestB6GuardTildePaths(LayoutProject):
    """B6 (PD-2, PD-8): con política presente, el guard v2 bloquea rutas
    cuyo texto empieza con `~` (fuera del proyecto, no clasificable)."""
    LAYOUT = "cdad"

    def setUp(self) -> None:
        super().setUp()
        self.home = Path(self._tmp) / "home-aislado"
        self.home.mkdir(exist_ok=True)

    def test_reviewfix_b6_guard_blocks_tilde_paths(self) -> None:
        """B6 (PD-2/PD-8): con política presente y HOME aislado en un
        tempdir, el guard bloquea (exit 2) Read/Write/Grep/Glob sobre rutas
        `~/…`, `~` y `~usuario` para los roles mediados. Controles: rutas
        relativas dentro del proyecto siguen su regla de clase."""
        blocked_cases = (
            ("test-writer-read", "Read", {"file_path": "~/x"}),
            ("test-writer-read", "Read",
             {"file_path": "~/.claude/credentials.json"}),
            ("implementer", "Write",
             {"file_path": "~/.claude/skills/cdad-cycle/scripts/"
                           "cdad_packet.py"}),
            ("test-writer-read", "Grep", {"pattern": "x", "path": "~/"}),
            ("test-writer-read", "Grep", {"pattern": "x", "path": "~"}),
            ("test-writer-read", "Glob", {"pattern": "**", "path": "~/"}),
            ("test-writer-read", "Glob", {"pattern": "**", "path": "~"}),
            ("test-writer-read", "Read", {"file_path": "~otro/x"}),
        )
        for role, tool, tool_input in blocked_cases:
            with self.subTest(caso="bloqueo", role=role, tool=tool,
                              entrada=tool_input):
                proc = run_guard_home(self.root, role, tool, tool_input,
                                      home=self.home)
                self.assertEqual(
                    proc.returncode, 2,
                    msg=f"B6: el guard v2 permitió {tool}({tool_input}) "
                        f"para {role} con HOME aislado (rc={proc.returncode}"
                        f": {proc.stderr.strip()}) — una ruta `~` está "
                        f"fuera del proyecto, no es clasificable y no "
                        f"puede ampliar un scope (PD-2)")
        controls = (
            ("test-writer-read", "Read",
             {"file_path": "tests/test_a.py"}, 0),
            ("test-writer-read", "Read", {"file_path": "scripts/x.py"}, 2),
            ("implementer", "Write", {"file_path": "scripts/x.py"}, 0),
            ("test-writer-read", "Grep",
             {"pattern": "x", "path": "tests"}, 0),
        )
        for role, tool, tool_input, expected in controls:
            with self.subTest(caso="control", role=role, tool=tool,
                              entrada=tool_input):
                proc = run_guard_home(self.root, role, tool, tool_input,
                                      home=self.home)
                self.assertEqual(
                    proc.returncode, expected,
                    msg=f"B6 control: el guard con HOME aislado dio "
                        f"rc={proc.returncode} para {tool}({tool_input}) "
                        f"de {role}, esperado {expected} "
                        f"({proc.stderr.strip()}) — las rutas relativas "
                        f"internas siguen su regla de clase")


# ------------------------------------------------------- CLI: B7 / I11


class TestB7ResumeAfterReconcile(DurableProjectCase):
    """B7 / I11: un paquete renderizado bajo una revisión de política
    distinta de la aceptada no se reanuda tras reconciliar."""

    def test_reviewfix_b7_resume_after_reconcile_names_revisions_and_new_packet(self) -> None:
        """B7/I11 (PD-4/PD-5): bootstrap → P1 → control resume rc 0 con
        bytes idénticos → el dueño cambia la política y reconcilia →
        resume P1: rc 2, stdout vacío, diagnóstico que nombra la revisión
        del paquete y la aceptada y pide preparar un paquete nuevo, sin
        ninguna escritura (árbol .cdad/docs y state byte a byte) → un
        paquete nuevo P2 preparado tras la reconciliación se reanuda rc 0
        con bytes idénticos."""
        # 1) bootstrap → P1
        self.prepare_bootstrap(self.root)
        p1 = read_state(self.root)["active_packet"]["id"]
        p1_bytes = published_packets(self.root)[p1]
        old_sha = policy_hash(self.root)
        # 2) control: resume P1 → rc 0, bytes idénticos
        control, _ = self.run_resume(self.root, p1)
        self.assertEqual(
            control.returncode, 0,
            msg=f"B7 control (precondición): resume de P1 antes del cambio "
                f"de política debe ser rc 0: {control.stdout} {control.stderr}")
        self.assertEqual(
            control.stdout, p1_bytes.decode("utf-8"),
            msg="B7 control: el resume de P1 no devolvió bytes idénticos "
                "al paquete publicado")
        # 3) el dueño cambia la política y reconcilia
        doc = json.loads((self.root / POLICY_FILE).read_text(encoding="utf-8"))
        doc["path_policy"]["implementation_roots"].append("vendor")
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        new_sha = policy_hash(self.root)
        self.assertNotEqual(
            old_sha, new_sha,
            msg="fixture: la revisión de la política debe cambiar")
        decision_path = "docs/decision-policy-revision.md"
        (self.root / decision_path).write_text(
            f"# Decisión del dueño — revisión de política aceptada\n"
            f"sha256: {new_sha}\n", encoding="utf-8")
        set_active_packet_status(self.root, "completed")
        rec, _ = self.run_reconcile(self.root, new_sha, decision_path)
        self.assertEqual(
            rec.returncode, 0,
            msg=f"B7 precondición: la reconciliación debe aceptarse: "
                f"{rec.stdout} {rec.stderr}")
        self.assertEqual(
            published_packets(self.root)[p1], p1_bytes,
            msg="B7 precondición (PD-5): la reconciliación alteró los "
                "bytes del paquete P1 existente")
        # 4) resume P1 → rc 2, stdout vacío, diagnóstico I11, sin escrituras
        before = tree_snapshot(self.root)
        state_before = state_bytes(self.root)
        blocked, _ = self.run_resume(self.root, p1)
        out = blocked.stdout + blocked.stderr
        self.assertEqual(
            blocked.returncode, 2,
            msg=f"B7/I11: --resume-packet de un paquete renderizado bajo "
                f"la revisión anterior dio rc={blocked.returncode} "
                f"({out.strip()[:200]!r})")
        self.assertEqual(
            blocked.stdout, "",
            msg="B7/I11: el rechazo imprimió contenido por stdout")
        names_revisions = old_sha in out and new_sha in out
        self.assertTrue(
            names_revisions or re.search(r"(?i)policy\s+revision", out),
            msg=f"B7/I11: el diagnóstico no nombra la revisión del paquete "
                f"({old_sha[:12]}…) ni la aceptada ({new_sha[:12]}…) ni la "
                f"revisión de política: {out!r}")
        self.assertRegex(
            out, NEW_PACKET_RE,
            msg=f"B7/I11: el diagnóstico no pide preparar un paquete "
                f"nuevo: {out!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="B7/I11: el resume rechazado escribió el árbol "
                "(.cdad / docs)")
        self.assertEqual(
            state_bytes(self.root), state_before,
            msg="B7/I11: el resume rechazado cambió el state")
        self.assertEqual(
            published_packets(self.root)[p1], p1_bytes,
            msg="B7/I11: los bytes de P1 en disco no se conservaron")
        # 5) paquete nuevo P2 tras reconciliar → resume rc 0, bytes idénticos
        prep2, _ = self.run_prepare(self.root, role="implementer",
                                    substage="green",
                                    objective="paquete P2 tras reconciliar")
        self.assertEqual(
            prep2.returncode, 0,
            msg=f"B7/I11 precondición: preparar P2 tras reconciliar debe "
                f"funcionar: {prep2.stdout} {prep2.stderr}")
        p2 = read_state(self.root)["active_packet"]["id"]
        self.assertNotEqual(
            p2, p1, msg="fixture: P2 debe ser un paquete nuevo distinto de P1")
        resumed2, _ = self.run_resume(self.root, p2)
        self.assertEqual(
            resumed2.returncode, 0,
            msg=f"B7/I11 control: el paquete P2 (renderizado bajo la "
                f"revisión aceptada) debe reanudarse: {resumed2.stdout} "
                f"{resumed2.stderr}")
        self.assertEqual(
            resumed2.stdout,
            published_packets(self.root)[p2].decode("utf-8"),
            msg="B7/I11 control: el resume de P2 no devolvió bytes "
                "idénticos al paquete publicado")


# ------------------------------------------------------- CLI: OPT-4


class TestOpt4ArchitectWithoutEpic(DurableProjectCase):
    """OPT-4 (PD-12): architect standalone sin epic activo → rechazo con
    diagnóstico explícito, sin ruta fabricada con `None`."""

    def test_reviewfix_opt4_architect_without_active_epic_diagnostic(self) -> None:
        """OPT-4 (PD-12): con `active_epic: null`, `prepare --role architect
        --substage discovery` se rechaza (rc≠0) con un diagnóstico que NO
        contiene la cadena «None» (no fabrica «docs/epics/None/plan.md») y
        que nombra la falta de epic activo; sin traceback."""
        root = self.new_project(epic=None)
        self.assertIsNone(
            read_state(root).get("active_epic"),
            msg="fixture: el proyecto debe tener active_epic null")
        proc, _ = self.run_prepare(
            root, role="architect", substage="discovery",
            objective="OPT-4: architect standalone sin epic activo")
        out = proc.stdout + proc.stderr
        self.assertNotEqual(
            proc.returncode, 0,
            msg=f"OPT-4: el prepare de architect sin epic activo fue "
                f"aceptado ({out!r}) — el architect standalone sigue el "
                f"camino legacy/intake (PD-12)")
        self.assertNotIn(
            "None", out,
            msg=f"OPT-4: el diagnóstico fabrica una ruta con 'None' en "
                f"vez de diagnosticar la falta de epic activo: {out!r}")
        self.assertRegex(
            out, re.compile(r"(?i)\bepic\b"),
            msg=f"OPT-4: el diagnóstico no menciona el epic: {out!r}")
        self.assertRegex(
            out,
            re.compile(r"(?i)(active\s+epic|epic\s+activo|requires\s+an?\s+"
                       r"active\s+epic|requiere\s+(un\s+)?epic|missing\s+"
                       r"epic|no\s+hay\s+epic|sin\s+epic|falta\s+epic)"),
            msg=f"OPT-4: el diagnóstico no nombra la falta de epic activo: "
                f"{out!r}")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg="OPT-4: el rechazo terminó con traceback")


if __name__ == "__main__":
    unittest.main(verbosity=2)
