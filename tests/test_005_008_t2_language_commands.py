#!/usr/bin/env python3
"""005-008 T2 RED — PD-10: comandos del proyecto en su lugar canónico.

Contract: docs/specs/005-008-project-path-capabilities/spec.md (PD-10,
INV-5/INV-7) + docs/specs/005-008-project-path-capabilities/plan.md (T2) +
docs/specs/005-008-project-path-capabilities/discovery.md (§1.5: el lugar
canónico de los comandos es el Makefile/systemPatterns del PROYECTO; el
esquema de docs/cdad-policy.json es de exactamente tres campos y rechaza
campos extra).

Superficie observable bajo prueba (solo escrituras en proyectos sintéticos
en tempdirs; NINGUNA lectura de implementación — ni skills/** ni el módulo
del CLI por import):

  python3 scripts/cdad_packet.py validate-policy --project-root <raíz>
    → rc y diagnóstico observables del CLI (fixture write_policy de
      004-002 T1 reutilizada por import).
  CDAD_OPENCODE_AGENTS_DIR=<copia agents/cdad-*.md> \
    python3 scripts/cdad_packet.py prepare --project-root <raíz> ...
    → publica .opencode/agents/cdad-*.md (arnés LayoutProject de 004-002
      T5 y el fixture Perl de 005-008 T1, reutilizados por import).

Mapa test → postcondición (UN test por postcondición de T2/PD-10):

  TestPd10bPolicySchemaThreeFields
    test_pd10b_extra_field_rejected_with_named_diagnostic -> PD-10(b)/INV-5
      (RED hoy: la política con campo extra se rechaza rc≠0 PERO el
      diagnóstico es genérico y NO nombra el campo ofensor)
  TestPd10aProjectMakefileCommands
    test_pd10a_perl_commands_declared_in_project_makefile -> PD-10(a)
      (LOCK de regresión: hoy debería pasar)

RED hoy: PD-10(b) falla por AssertionError de comportamiento (la aserción
del diagnóstico que nombra el campo extra); PD-10(a) pasa (LOCK). Toda
falla es AssertionError sobre el contrato — no ImportError/SyntaxError/
NameError/AttributeError; sin nombres de funciones internas ni mocks.
"""

from __future__ import annotations

import unittest

from test_004_002_t1_policy import (  # noqa: E402
    ProjectCase,
    run_validate,
    write_policy,
)
from test_004_002_t2_bootstrap import POLICY_FILE  # noqa: E402
from test_004_002_t5_runtime import require_derived  # noqa: E402
from test_005_008_t1_nested_tests import PerlLayoutProject  # noqa: E402

TEST_WRITER = "cdad-test-writer.md"
IMPLEMENTER = "cdad-implementer.md"


# ---------------------------------------------------------------- PD-10(b)


class TestPd10bPolicySchemaThreeFields(ProjectCase):
    """PD-10(b)/INV-5: el esquema de la política sigue de EXACTAMENTE tres
    campos; una política con un campo extra se rechaza con diagnóstico
    NOMBRADO, sin cambios silenciosos."""

    def test_pd10b_extra_field_rejected_with_named_diagnostic(self) -> None:
        """PD-10(b): una política con un campo extra (p. ej. `commands`
        declarando los comandos de sintaxis/tests Perl, o `models`) se
        RECHAZA (rc≠0) y el diagnóstico NOMBRA el campo ofensor. Control
        interno: la política exacta (tres campos) sigue dando rc=0. La
        política rechazada queda sin cambios (sin cambios silenciosos)."""
        extras = (
            ("commands", {"commands": {"syntax": "perl -c",
                                       "test": "prove -lr t"}}),
            ("models", {"models": {"policy": "cheap"}}),
        )
        for label, extra in extras:
            with self.subTest(campo=label):
                write_policy(self.root,
                             path_policy={"test_roots": ["tests"]},
                             temporary_roots=["tmp"], extra=extra)
                before = (self.root / POLICY_FILE).read_bytes()
                proc = run_validate(self.root)
                output = proc.stdout + proc.stderr
                self.assertNotIn(
                    "Traceback", output,
                    msg=f"PD-10(b): el rechazo de {label!r} fue un fallo "
                        f"del CLI (crash), no una validación de esquema")
                self.assertNotEqual(
                    proc.returncode, 0,
                    msg=f"PD-10(b): la política con campo extra {label!r} "
                        f"fue aceptada (rc=0) — el esquema es de exactamente "
                        f"tres campos (schema_version, path_policy, "
                        f"temporary_roots); los comandos son del proyecto, "
                        f"no de la política (INV-5)")
                self.assertIn(
                    label, output,
                    msg=f"PD-10(b): el diagnóstico del rechazo NO nombra el "
                        f"campo ofensor {label!r} — hoy es genérico "
                        f"({output.strip()!r}); el rechazo debe indicar "
                        f"QUÉ campo sobra (diagnóstico nombrado, sin "
                        f"cambios silenciosos)")
                self.assertEqual(
                    (self.root / POLICY_FILE).read_bytes(), before,
                    msg=f"PD-10(b): el rechazo de {label!r} modificó la "
                        f"política (cambio silencioso)")
        with self.subTest(control="exacta"):
            write_policy(self.root,
                         path_policy={"test_roots": ["tests"]},
                         temporary_roots=["tmp"])
            proc = run_validate(self.root)
            self.assertEqual(
                proc.returncode, 0,
                msg=f"PD-10(b) control: la política exacta de tres campos "
                    f"ya no valida: {proc.stdout} {proc.stderr}")


# ---------------------------------------------------------------- PD-10(a)


class TestPd10aProjectMakefileCommands(PerlLayoutProject):
    """PD-10(a): el proyecto declara sus comandos Perl en su lugar canónico
    (su Makefile); el CLI no exige nada en la política y sigue publicando
    los derivados (LOCK de regresión: hoy debería pasar)."""

    def test_pd10a_perl_commands_declared_in_project_makefile(self) -> None:
        """PD-10(a): un proyecto sintético con los comandos de sintaxis y
        tests Perl declarados en SU Makefile (`perl -c` para sintaxis,
        `prove` para tests) publica los agentes derivados con prepare rc=0
        y su docs/cdad-policy.json queda byte a byte sin cambios — los
        comandos viven en el Makefile y NUNCA entran a la política
        (INV-5: sin campo de comandos en la política)."""
        self.apply_perl()
        makefile = self.root / "Makefile"
        makefile.write_text(
            "# Comandos del PROYECTO (lugar canónico, PD-10a);\n"
            "# NUNCA en docs/cdad-policy.json (esquema de tres campos).\n"
            "syntax:\n"
            "\tperl -c webmin-module/module/main.pl\n"
            "test:\n"
            "\tprove -lr webmin-module/module/t\n",
            encoding="utf-8")
        self.assertTrue(makefile.is_file(), msg="precondición: Makefile")
        policy_before = (self.root / POLICY_FILE).read_bytes()
        self.assertNotIn(
            "commands", policy_before.decode("utf-8"),
            msg="precondición rota: la política declara un campo commands "
                "(los comandos deben vivir en el Makefile del proyecto)")
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-10(a): el CLI no publicó los agentes derivados para un "
                f"proyecto que declara sus comandos Perl en su Makefile "
                f"(rc={proc.returncode}): {proc.stdout} {proc.stderr}")
        self.assertEqual(
            (self.root / POLICY_FILE).read_bytes(), policy_before,
            msg="PD-10(a): la política cambió — los comandos son del "
                "proyecto (Makefile), nunca de docs/cdad-policy.json "
                "(INV-5)")
        require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))


if __name__ == "__main__":
    unittest.main(verbosity=2)
