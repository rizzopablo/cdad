#!/usr/bin/env python3
"""004-002 T5 REVIEW-FIX RED — hallazgos B1–B5, R1/R2/R3/R6/R7/R9 de review-t5.

Contract: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-7, PD-8, PD-5; invariante 3) + review-t5.md ("Disposición del
orquestador") + plan.md (I9, I10, C2).

Cada test deriva de un hallazgo del dictamen T5 y su disposición aprobada;
cada aserción expresa la postcondición observables (comportamiento del guard
CC / de los derivados OpenCode / del prepare), no la mecánica interna.
Reutiliza por import los fixtures de test_004_002_t5_runtime.py
(LayoutProject, run_guard forma real del JSON de hook, helpers) SIN
modificarlos, y el evaluador findLast único de pd10_permission_semantics.py.
No lee implementación: solo la interfaz (CLI, guard, JSON de hook, derivados
publicados como salidas observables del prepare).

Mapa test → hallazgo/postcondición (review-t5 → spec):

  TestT5ReviewFixGuardCc (guard de Claude Code, forma real del hook JSON):
    test_reviewfix_b1_guard_blocks_policy_and_derived_edits   -> B1 (inv.3, PD-7)
    test_reviewfix_b2_unscoped_paths_block_with_narrow_msg    -> B2 (PD-8/I10/C2)
    test_reviewfix_b4_glob_pattern_escaping_blocked           -> B4 (I10/C2)
    test_reviewfix_b5_guard_uses_claude_project_dir           -> B5 (PD-8/I10)
    test_reviewfix_r1_sibling_prefix_collision_blocked        -> R1 (PD-2/I10)
    test_reviewfix_r6_multiedit_notebookedit_mediated         -> R6 (PD-8/I10)
  TestT5ReviewFixDeriveds (derivados OpenCode + prepare):
    test_reviewfix_b1_derived_edit_deny_on_agents_dir         -> B1 (inv.3, PD-7)
    test_reviewfix_b3_nested_tests_dir_not_amplified          -> B3 (PD-7, PD-2)
    test_reviewfix_r2_removed_source_orphan_derived_retired   -> R2 (PD-8/PD-5)
    test_reviewfix_r3_source_without_frontmatter_fails_clean  -> R3 (PD-8)
    test_reviewfix_r7_manifest_records_source_provenance      -> R7 (PD-8/§2)
    test_reviewfix_r9_missing_agents_dir_warns_on_stderr      -> R9 (PD-8)

RED hoy (post T5 GREEN): cada test falla por la postcondición del hallazgo
ausente (AssertionError), no por errores de fixture; los controles positivos
de cada caso quedan documentados en el docstring.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from test_004_002_t5_runtime import (  # noqa: E402
    AGENTS_ENV,
    CLI_ENV,
    DERIVED_DIR,
    GUARD,
    MANIFEST,
    POLICY_FILE,
    LayoutProject,
    mark_active_packet,
    published_derived,
    require_derived,
)
from pd10_permission_semantics import verdict  # noqa: E402
from test_004_002_t1_policy import parse_classify, run_classify  # noqa: E402
from test_004_002_t2_bootstrap import (  # noqa: E402
    SCRIPT,
    read_state,
    tree_snapshot,
    write_state,
)

TEST_WRITER = "cdad-test-writer.md"
IMPLEMENTER = "cdad-implementer.md"
IMPLEMENTER_ODOO = "cdad-implementer-odoo.md"

# Roles mediados con escritura declarados por los tests T5 existentes
# (interfaz del guard CC: rol como argumento).
WRITE_ROLES = ("test-writer-write", "implementer", "implementer-odoo")
POLICY_REL = "docs/cdad-policy.json"
DERIVED_AGENT_REL = ".opencode/agents/cdad-implementer.md"
DERIVED_MANIFEST_REL = ".opencode/agents/.cdad-derived.json"
NARROW_RE = r"acot|narrow|scope|tests|docs"


def run_guard_env(root: Path, role: str, tool_name: str, tool_input: dict,
                  *, cwd: Path | None = None,
                  project_dir: Path | None = None) -> subprocess.CompletedProcess:
    """run_guard (fixture T5) con control explícito de CLAUDE_PROJECT_DIR:
    la variable del entorno externo se retira salvo que se pase project_dir."""
    env = dict(os.environ)
    env[CLI_ENV] = str(SCRIPT)
    if project_dir is None:
        env.pop("CLAUDE_PROJECT_DIR", None)
    else:
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        ["bash", str(GUARD), role],
        input=payload, capture_output=True, text=True,
        cwd=str(cwd or root), env=env,
    )


def json_scalar_values(doc: object):
    """Todos los strings (claves y valores) de un documento JSON, en orden."""
    if isinstance(doc, dict):
        for key, value in doc.items():
            yield key
            yield from json_scalar_values(value)
    elif isinstance(doc, list):
        for value in doc:
            yield from json_scalar_values(value)
    elif isinstance(doc, str):
        yield doc


# ------------------------------------------------- guard CC (I10 / C2)


class TestT5ReviewFixGuardCc(LayoutProject):
    """Hallazgos del guard CC (B1 lado guard, B2, B4, B5, R1, R6)."""
    LAYOUT = "cdad"

    def test_reviewfix_b1_guard_blocks_policy_and_derived_edits(self) -> None:
        """B1 (inv. 3, PD-7): con política presente, el guard bloquea
        Edit/Write de docs/cdad-policy.json y de todo lo publicado bajo
        .opencode/agents/ (derivados y .cdad-derived.json) para todos los
        roles mediados. Controles: Write de implementación permitido."""
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"prepare del fixture (precondición): {proc.stdout} {proc.stderr}")
        cases: list[tuple[str, str, dict]] = []
        for role in WRITE_ROLES:
            cases.append((role, "Write", {"file_path": POLICY_REL}))
            cases.append((role, "Edit", {"file_path": DERIVED_AGENT_REL}))
            cases.append((role, "Edit", {"file_path": DERIVED_MANIFEST_REL}))
        for role, tool, tool_input in cases:
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                blocked = run_guard_env(self.root, role, tool, tool_input)
                self.assertEqual(
                    blocked.returncode, 2,
                    msg=f"B1: el guard permitió {tool}({tool_input['file_path']!r}) "
                        f"al {role} (rc={blocked.returncode}) — inv. 3: ningún "
                        f"rol edita su política ni los derivados")
        with self.subTest(control="implementer Write scripts/x.py"):
            allowed = run_guard_env(self.root, "implementer", "Write",
                                    {"file_path": "scripts/x.py"})
            self.assertEqual(
                allowed.returncode, 0,
                msg=f"B1 control: el guard bloqueó Write de implementación "
                    f"(rc={allowed.returncode}: {allowed.stderr.strip()})")

    def test_reviewfix_b2_unscoped_paths_block_with_narrow_msg(self) -> None:
        """B2 (PD-8/I10/C2): para el test-writer, Grep/Glob con path ".", "./",
        path vacío o la raíz del proyecto (absoluta) es una búsqueda NO acotada
        → bloqueo con el mensaje que pide acotar a tests/docs. Control: path
        'tests' → permitido."""
        cases: list[tuple[str, dict]] = [
            ("Grep", {"pattern": "def ", "path": "."}),
            ("Grep", {"pattern": "def ", "path": "./"}),
            ("Grep", {"pattern": "def ", "path": ""}),
            ("Grep", {"pattern": "def ", "path": str(self.root)}),
            ("Glob", {"pattern": "**/*.py", "path": "."}),
            ("Glob", {"pattern": "**/*.py", "path": str(self.root)}),
        ]
        for tool, tool_input in cases:
            with self.subTest(tool=tool, tool_input=tool_input):
                blocked = run_guard_env(self.root, "test-writer-read", tool,
                                        tool_input)
                out = blocked.stdout + blocked.stderr
                self.assertEqual(
                    blocked.returncode, 2,
                    msg=f"B2: el guard permitió {tool} con path "
                        f"{tool_input['path']!r} (rc={blocked.returncode}) — "
                        f"búsqueda de todo el proyecto incluyendo implementación")
                self.assertRegex(
                    out, NARROW_RE,
                    msg=f"B2: el bloqueo de {tool} con path "
                        f"{tool_input['path']!r} no pide acotar la búsqueda: "
                        f"{out!r}")
        with self.subTest(control="path tests"):
            allowed = run_guard_env(self.root, "test-writer-read", "Grep",
                                    {"pattern": "def ", "path": "tests"})
            self.assertEqual(
                allowed.returncode, 0,
                msg=f"B2 control: el guard bloqueó Grep acotado a tests "
                    f"(rc={allowed.returncode}: {allowed.stderr.strip()})")

    def test_reviewfix_b4_glob_pattern_escaping_blocked(self) -> None:
        """B4 (I10/C2): Glob se media por path + pattern: un pattern con '..',
        absoluto, o cuyo prefijo literal es una raíz de implementación
        ('skills/**'), sale del ámbito → bloqueo. Controles: pattern neutral
        con path 'tests' → permitido (y el caso sin path ya bloquea por la
        regla unscoped declarada)."""
        cases = (
            {"pattern": "../skills/**", "path": "tests"},
            {"pattern": str(self.root / "skills" / "**"), "path": "tests"},
            {"pattern": "skills/**", "path": "tests"},
        )
        for tool_input in cases:
            with self.subTest(tool_input=tool_input):
                blocked = run_guard_env(self.root, "test-writer-read", "Glob",
                                        tool_input)
                self.assertEqual(
                    blocked.returncode, 2,
                    msg=f"B4: el guard permitió Glob {tool_input} al "
                        f"test-writer (rc={blocked.returncode}) — el pattern "
                        f"escapa del ámbito acotado")
        for control in ({"pattern": "**/*.py", "path": "tests"},
                        {"pattern": "tests/**", "path": "tests"}):
            with self.subTest(control=control):
                allowed = run_guard_env(self.root, "test-writer-read", "Glob",
                                        control)
                self.assertEqual(
                    allowed.returncode, 0,
                    msg=f"B4 control: el guard bloqueó Glob {control} "
                        f"(rc={allowed.returncode}: {allowed.stderr.strip()})")

    def test_reviewfix_b5_guard_uses_claude_project_dir(self) -> None:
        """B5 (PD-8/I10): el guard toma la raíz del proyecto de
        CLAUDE_PROJECT_DIR: con cwd en un subdirectorio y la variable puesta,
        aplica la política (bloquea la lectura de implementación); con cwd=raíz
        y sin la variable conserva pwd (comportamiento actual); con cwd en un
        subdirectorio y sin la variable no puede aplicar la política del
        proyecto (cae a legacy: 'vendor' no es una raíz legacy → permitido)."""
        self.apply_layout("cdad")
        # Raíz de implementación propia de la política (no legacy): vendor/.
        doc = json.loads((self.root / POLICY_FILE).read_text(encoding="utf-8"))
        doc["path_policy"]["implementation_roots"].append("vendor")
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (self.root / "vendor").mkdir()
        (self.root / "vendor" / "v.py").write_text("# vendor\n",
                                                   encoding="utf-8")
        subdir = self.root / "tests"
        with self.subTest(caso="cwd=raíz, sin variable (conserva pwd)"):
            at_root = run_guard_env(self.root, "test-writer-read", "Read",
                                    {"file_path": "vendor/v.py"})
            self.assertEqual(
                at_root.returncode, 2,
                msg=f"B5: con cwd=raíz el guard no aplica la política "
                    f"(rc={at_root.returncode})")
        with self.subTest(caso="cwd=subdir + CLAUDE_PROJECT_DIR=raíz"):
            with_var = run_guard_env(self.root, "test-writer-read", "Read",
                                     {"file_path": "vendor/v.py"},
                                     cwd=subdir, project_dir=self.root)
            self.assertEqual(
                with_var.returncode, 2,
                msg=f"B5: el guard no tomó la raíz de CLAUDE_PROJECT_DIR — "
                    f"desde un subdirectorio no aplicó la política "
                    f"(rc={with_var.returncode}: {with_var.stderr.strip()})")
        with self.subTest(caso="cwd=subdir + variable, path permitido"):
            ok_path = run_guard_env(self.root, "test-writer-read", "Read",
                                    {"file_path": "tests/test_a.py"},
                                    cwd=subdir, project_dir=self.root)
            self.assertEqual(
                ok_path.returncode, 0,
                msg=f"B5 control: el guard bloqueó un path de tests con la "
                    f"raíz de CLAUDE_PROJECT_DIR (rc={ok_path.returncode}: "
                    f"{ok_path.stderr.strip()})")
        with self.subTest(caso="cwd=subdir, sin variable (legacy en pwd)"):
            no_var = run_guard_env(self.root, "test-writer-read", "Read",
                                   {"file_path": "vendor/v.py"}, cwd=subdir)
            self.assertEqual(
                no_var.returncode, 0,
                msg=f"B5: sin la variable el guard NO conserva pwd como raíz "
                    f"(rc={no_var.returncode}: {no_var.stderr.strip()}) — "
                    f"el legacy no clasifica vendor/, debe permitirlo")

    def test_reviewfix_r1_sibling_prefix_collision_blocked(self) -> None:
        """R1 (PD-2/I10): una ruta absoluta hermana con prefijo colisionante
        (<raíz>x/skills/x.py) está FUERA del proyecto → bloqueo, no un camino
        fantasma recortado. Control: ruta absoluta real dentro del proyecto
        permitida (tests)."""
        sibling = str(self.root) + "x/skills/x.py"
        blocked = run_guard_env(self.root, "test-writer-read", "Read",
                                {"file_path": sibling})
        self.assertEqual(
            blocked.returncode, 2,
            msg=f"R1: el guard permitió leer fuera del proyecto "
                f"({sibling!r}) por colisión de prefijo (rc={blocked.returncode})")
        with self.subTest(control="absoluto dentro del proyecto"):
            inside = run_guard_env(self.root, "test-writer-read", "Read",
                                   {"file_path": str(self.root /
                                                     "tests/test_a.py")})
            self.assertEqual(
                inside.returncode, 0,
                msg=f"R1 control: el guard bloqueó una ruta absoluta interna "
                    f"(rc={inside.returncode}: {inside.stderr.strip()})")

    def test_reviewfix_r6_multiedit_notebookedit_mediated(self) -> None:
        """R6 (PD-8/I10): MultiEdit (file_path) y NotebookEdit
        (notebook_path) entran a la mediación v2: al implementer se le
        bloquea MultiEdit sobre un test; a test-writer-write se le bloquea
        NotebookEdit sobre implementación. Controles: cada herramienta sobre
        su scope propio pasa."""
        cases = (
            ("implementer", "MultiEdit", {"file_path": "tests/test_a.py"}, 2),
            ("test-writer-write", "NotebookEdit",
             {"notebook_path": "scripts/x.py"}, 2),
        )
        for role, tool, tool_input, expected in cases:
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                blocked = run_guard_env(self.root, role, tool, tool_input)
                self.assertEqual(
                    blocked.returncode, expected,
                    msg=f"R6: el guard no medió {tool} ({tool_input}) para "
                        f"{role} (rc={blocked.returncode}, esperado {expected})")
        controls = (
            ("implementer", "MultiEdit", {"file_path": "scripts/x.py"}, 0),
            ("test-writer-write", "NotebookEdit",
             {"notebook_path": "tests/test_a.py"}, 0),
        )
        for role, tool, tool_input, expected in controls:
            with self.subTest(control=role, tool=tool, tool_input=tool_input):
                allowed = run_guard_env(self.root, role, tool, tool_input)
                self.assertEqual(
                    allowed.returncode, expected,
                    msg=f"R6 control: el guard bloqueó {tool}({tool_input}) "
                        f"para {role} (rc={allowed.returncode}: "
                        f"{allowed.stderr.strip()})")


# --------------------------------------- derivados OpenCode + prepare (I9)


class TestT5ReviewFixDeriveds(LayoutProject):
    """Hallazgos sobre los derivados publicados y el prepare (B1 lado
    OpenCode, B3, R2, R3, R7, R9)."""
    LAYOUT = "cdad"

    def require_prepare_ok(self, *extra: str, role: str = "test-writer",
                           substage: str = "red", label: str
                           ) -> subprocess.CompletedProcess:
        proc = self.prepare(*extra, role=role, substage=substage,
                            objective=label)
        self.assertEqual(
            proc.returncode, 0,
            msg=f"{label}: prepare del fixture falló (precondición): "
                f"{proc.stdout} {proc.stderr}")
        return proc

    def test_reviewfix_b1_derived_edit_deny_on_agents_dir(self) -> None:
        """B1 (inv. 3, PD-7): en TODOS los derivados OpenCode publicados,
        edit sobre .opencode/agents/** (un derivado y el manifiesto) resuelve
        deny — los derivados no son fuentes editables por ningún rol
        (evaluador único de pd10). Control: el edit de tests sigue allow."""
        self.require_prepare_ok(label="B1 derivados")
        pub_names = tuple(sorted(published_derived(self.root)))
        pub = require_derived(self, self.root, pub_names)  # str decodificado
        self.assertTrue(
            pub, msg="B1: no hay derivados publicados (precondición)")
        for name, text in sorted(pub.items()):
            with self.subTest(agent=name, probe=DERIVED_AGENT_REL):
                self.assertEqual(
                    verdict(text, "edit", DERIVED_AGENT_REL), "deny",
                    msg=f"B1: el derivado {name} permite editar "
                        f"{DERIVED_AGENT_REL} (su propia fuente derivada)")
            with self.subTest(agent=name, probe=DERIVED_MANIFEST_REL):
                self.assertEqual(
                    verdict(text, "edit", DERIVED_MANIFEST_REL), "deny",
                    msg=f"B1: el derivado {name} permite editar el manifiesto "
                        f"{DERIVED_MANIFEST_REL}")
        with self.subTest(control="tw edit tests"):
            self.assertEqual(
                verdict(pub[TEST_WRITER], "edit", "tests/test_a.py"), "allow",
                msg="B1 control: el derivado test-writer sigue pudiendo "
                    "editar tests")
        with self.subTest(control="imp edit tests"):
            self.assertEqual(
                verdict(pub[IMPLEMENTER], "edit", "tests/test_a.py"), "deny",
                msg="B1 control: el derivado implementer no edita tests")

    def test_reviewfix_b3_nested_tests_dir_not_amplified(self) -> None:
        """B3 (PD-7, PD-2): con un directorio literal tests/ anidado bajo una
        raíz de implementación (src/tests/x.py, que el clasificador da como
        implementation), el derivado test-writer DENIEGA edit y read, y el del
        implementer PERMITE editarlo: los mapas expresan exactamente al
        clasificador (ni amplificación ni sobre-restricción). Control:
        validate-policy --classify. Conventional: colocated bajo src es por
        prefijo/sufijo, no por nombre de directorio."""
        self.apply_layout("conventional")
        nested = self.root / "src" / "tests" / "x.py"
        nested.parent.mkdir(parents=True, exist_ok=True)
        nested.write_text("# fixture src/tests/x.py\n", encoding="utf-8")
        cls = run_classify(self.root, "src/tests/x.py")
        classes = parse_classify(cls.stdout)
        self.assertEqual(
            classes.get("src/tests/x.py"), "implementation",
            msg=f"B3 control: el clasificador no da 'implementation' para "
                f"src/tests/x.py (rc={cls.returncode}: {cls.stdout} {cls.stderr})")
        self.require_prepare_ok(role="test-writer", label="B3 prepare")
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        for tool in ("edit", "read"):
            with self.subTest(agent=TEST_WRITER, tool=tool):
                self.assertEqual(
                    verdict(tw, tool, "src/tests/x.py"), "deny",
                    msg=f"B3: el mapa del test-writer resuelve {tool} "
                        f"('src/tests/x.py') permitido — amplifica la "
                        f"política (PD-7: nunca ampliar)")
        with self.subTest(agent=IMPLEMENTER, tool="edit"):
            self.assertEqual(
                verdict(imp, "edit", "src/tests/x.py"), "allow",
                msg="B3: el mapa del implementer deniega editar "
                    "src/tests/x.py que la política clasifica implementación "
                    "— sobre-restricción")

    def test_reviewfix_r2_removed_source_orphan_derived_retired(self) -> None:
        """R2 (PD-8/PD-5): si una fuente desaparece del origen y se regenera
        (nuevo prepare tras completar el paquete), el derivado previo listado
        en el manifiesto se RETIRA de .opencode/agents/ y del manifiesto; un
        archivo ajeno sobrevive."""
        self.require_prepare_ok(label="R2 primer prepare")
        foreign = self.root / DERIVED_DIR / "mi-agente-ajeno.md"
        foreign.write_text("# ajeno\n", encoding="utf-8")
        mark_active_packet(self.root, "completed")
        (self.agents_src / "cdad-architect.md").unlink()
        second = self.require_prepare_ok(role="implementer", substage="green",
                                         label="R2 regeneración")
        pub = published_derived(self.root)
        self.assertNotIn(
            "cdad-architect.md", pub,
            msg=f"R2: el derivado huérfano cdad-architect.md (sin fuente en "
                f"el origen) sigue activo tras regenerar (rc regeneración="
                f"{second.returncode})")
        manifest = self.root / DERIVED_DIR / MANIFEST
        self.assertTrue(manifest.is_file(), msg="R2: manifiesto ausente")
        self.assertNotIn(
            "cdad-architect.md", manifest.read_text(encoding="utf-8"),
            msg="R2: el manifiesto nuevo aún declara el derivado retirado")
        self.assertEqual(
            foreign.read_text(encoding="utf-8"), "# ajeno\n",
            msg="R2: la regeneración tocó un archivo ajeno")

    def test_reviewfix_r3_source_without_frontmatter_fails_cleanly(self) -> None:
        """R3 (PD-8): una fuente instalada sin frontmatter produce rc 2 con
        diagnóstico, SIN traceback y SIN ninguna escritura (ni derivados ni
        paquete ni state)."""
        (self.agents_src / "cdad-architect.md").write_text(
            "# sin frontmatter\n", encoding="utf-8")
        before = tree_snapshot(self.root)
        proc = self.prepare()
        out = proc.stdout + proc.stderr
        self.assertEqual(
            proc.returncode, 2,
            msg=f"R3: fuente sin frontmatter no produce rc 2 "
                f"(rc={proc.returncode}: {out.strip()[:200]!r})")
        self.assertNotIn(
            "Traceback", proc.stderr,
            msg="R3: el fallo de la fuente sin frontmatter imprime traceback")
        self.assertRegex(
            out, r"frontmatter|fuente|source|inválid|invalid",
            msg=f"R3: sin diagnóstico sobre la fuente inválida: {out!r}")
        self.assertEqual(
            tree_snapshot(self.root), before,
            msg="R3: el fallo publicó algo (escrituras parciales)")

    def test_reviewfix_r7_manifest_records_source_provenance(self) -> None:
        """R7 (PD-8, §2 artefactos): el manifiesto registra la PROCEDENCIA de
        cada derivado. Supuesto documentado: la procedencia se observa como
        cualquier clave o valor del manifiesto cuyo texto contiene la ruta del
        directorio de origen (el dir fuente pasado por CDAD_OPENCODE_AGENTS_DIR)."""
        self.require_prepare_ok(label="R7 prepare")
        manifest = self.root / DERIVED_DIR / MANIFEST
        self.assertTrue(manifest.is_file(), msg="R7: manifiesto ausente")
        doc = json.loads(manifest.read_text(encoding="utf-8"))
        values = list(json_scalar_values(doc))
        self.assertIn(
            str(self.agents_src), values,
            msg=f"R7: el manifiesto no registra el directorio de origen de "
                f"los derivados ({str(self.agents_src)!r} ausente en "
                f"{values[:12]}…)")

    def test_reviewfix_r9_missing_agents_dir_warns_on_stderr(self) -> None:
        """R9 (PD-8): con política presente y CDAD_OPENCODE_AGENTS_DIR
        apuntando a un directorio inexistente, prepare tiene rc 0 y emite por
        stderr un aviso de que NO publicó derivados (un proyecto puede usar
        solo Claude Code). Control: no publica derivados."""
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.root / "directorio-agentes-inexistente")
        args = ["prepare", "--project-root", str(self.root),
                "--role", "test-writer", "--substage", "red",
                "--objective", "R9: agents dir inexistente"]
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True, text=True,
            cwd=Path(SCRIPT).parent.parent, env=env,
        )
        self.assertEqual(
            proc.returncode, 0,
            msg=f"R9: prepare con agents dir inexistente no es rc 0 "
                f"(rc={proc.returncode}: {proc.stdout} {proc.stderr})")
        self.assertRegex(
            proc.stderr, r"deriv|agent",
            msg=f"R9: el stderr no avisa sobre los derivados: "
                f"{proc.stderr!r}")
        self.assertRegex(
            proc.stderr, r"no\s+se\s+public|no\s+public|sin\s+deriv|sin\s+agent|"
                         r"not\s+publish|without|no\s+agents",
            msg=f"R9: el stderr no dice que NO se publicaron derivados: "
                f"{proc.stderr!r}")
        self.assertEqual(
            published_derived(self.root), {},
            msg="R9 control: se publicaron derivados con el dir inexistente")


if __name__ == "__main__":
    unittest.main(verbosity=2)
