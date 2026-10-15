#!/usr/bin/env python3
"""005-008 T3 RED — Recorrido del PRODUCTO INSTALADO (aceptación, PD-11).

Contract: docs/specs/005-008-project-path-capabilities/spec.md (PD-11, INV-6,
INV-9) + docs/specs/005-008-project-path-capabilities/plan.md (T3, gate de
integración: recorrido del producto instalado) +
docs/specs/005-008-project-path-capabilities/discovery.md (fixtures §4; límites
honestos §1.8).

Superficie observable (NADA se escribe fuera del tempdir del test; el HOME
real del dueño queda intacto y NO es leído por este fixture):

  Instalación aislada (perfil --basic, raíz redirigida):
    CDAD_INSTALL_ROOT=<tempdir>/install bash install.sh --basic
    → el producto queda íntegramente bajo <tempdir>/install (version.txt,
    CLI en skills/cdad-cycle/scripts/cdad_packet.py, agentes cdad-*.md).

  Recorrido con EL CLI INSTALADO (no el del árbol de trabajo):
    CDAD_OPENCODE_AGENTS_DIR=<install>/.config/opencode/agents \
      python3 <install>/.config/opencode/skills/cdad-cycle/scripts/cdad_packet.py \
      prepare --project-root <proyecto fixture> ...
    → publica .opencode/agents/cdad-*.md para el proyecto fixture con la
    política del caso Perl/Webmin (raíz de tests ANIDADA
    webmin-module/module/t dentro de implementation_roots) y el CASO FOCAL
    test_files bajo implementación; los mapas read/grep/glob/edit de cada
    derivado se evalúan con el ORÁCULO findLast ÚNICO
    (tests/pd10_permission_semantics.verdict, reutilizado por import; NO se
    reimplementa ningún evaluador).

Mapa test → postcondición:

  TestPd11AccIsolatedInstall
    test_pd11_isolated_install_of_basic_profile          -> PD-11 (el
      recorrido EXISTE) + INV-9 (instalación en tempdir; ni HOME ni
      producción: reservado al dueño)
  TestPd11AccPositiveCapabilities
    test_pd11_positive_capabilities_end_to_end          -> PD-11 positivas
      (ancladas a PD-1 leída del árbol anidado, PD-3 edit, PD-4
      implementer edita implementación y NO tests)
  TestPd11AccPositiveDeclaredTestFiles
    test_pd11_declared_test_files_under_impl_positive   -> PD-11/PD-5 (focal
      test_files bajo implementación: allow read+edit al test-writer, deny
      al implementer)
  TestPd11AccNegativeCapabilities
    test_pd11_negative_capabilities_end_to_end          -> PD-11 negativas
      (ancladas a PD-2 deny de lectura de implementación, PD-5 archivo con
      forma de test NO declarado sigue deny, PD-6 ruta privada anidada en
      la raíz de tests denegada en read y edit para TODO rol; hermano no
      privado sigue allow)
  TestPd11AccNoSearchPathEntries
    test_pd11_no_grep_glob_path_entries                 -> PD-11/PD-9/W-2
      (ningún derivado gana entradas por ruta en grep/glob)

========================================================== LÍMITES HONESTOS
Este test ejercita el PRODUCTO INSTALADO y sus MAPAS PUBLICADOS (los
derivados que `prepare` publica para el proyecto fixture), evaluados por el
oráculo findLast único. En particular:

  - La comprobación NO ejercita la MEDIACIÓN de un proceso OpenCode real:
    OpenCode (el runtime que lee el frontmatter de los agentes derivados al
    decidir read/edit/grep/glob) no se ejecuta aquí; el oráculo pd10 es el
    modelo declarado de esa mediación, siendo el recorrido real con el
    dueño la evidencia complementaria (VERIFY 3; la sonda prueba los mapas
    generados, no los en vivo de OpenCode).
  - `grep`, el shell y una sesión separada NO SON SANDBOX: ninguna lectura
    por shell está aislada por una regla `read` y no se promete aislamiento
    (INV-6). Este test no reintroduce allowlists por comando (retraídas,
    decisión del dueño 2026-09-29): la barrera viva por ruta es
    `read`/`edit`.
  - CDAD_INSTALL_ROOT es un MECANISMO DE INSTALACIÓN, no un sandbox: solo
    acredita que el producto instala en la raíz pedida dentro del tempdir
    del test (ni HOME ni producción: INV-9, reservado al dueño).
  - La localización del CLI instalado lee la ESTRUCTURA del árbol instalado
    (rutas, no contenido de implementación); el contenido del CLI no se lee
    por este fixture.
  - Si el entorno no permite construir la instalación aislada, el test hace
    SKIP LIMPIO con mensaje explícito (no se fabrica un verde).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import POLICY_FILE, build_project
from test_004_002_t5_runtime import (  # noqa: E402
    AGENTS_ENV,
    assert_no_search_path_entries,
    prepare_args,
    published_derived,
    require_derived,
)
from pd10_permission_semantics import verdict  # noqa: E402
from test_005_008_t1_nested_tests import (  # noqa: E402
    BASIC,
    CGI,
    DECLARED_FILE,
    HELPER,
    IMPL,
    MAIN,
    PerlLayoutProject,
    TEST_TREE,
)

TEST_WRITER = "cdad-test-writer.md"
IMPLEMENTER = "cdad-implementer.md"
SECRET = f"{TEST_TREE}/secret.local"
# Forma de test bajo implementación y NO declarado (fuera del árbol de
# tests declarado y fuera de cualquier test_files): con test_roots anidada
# (por defecto del fixture), t/undeclared.t YA quedaría bajo el árbol
# declarado, así que la sonda negativa correcta del recorrido es un .t bajo
# la RAÍZ de implementación, no declarado.
UNDECLARED_PROBE = f"{IMPL}/extra.t"
CLI_RELPATH = "skills/cdad-cycle/scripts/cdad_packet.py"
MARKER = "agents/cdad-test-writer.md"

REPO_ROOT = Path(__file__).resolve().parents[1]

PROBES_W2 = (
    IMPL, f"{IMPL}/w2_probe", TEST_TREE, f"{TEST_TREE}/w2_probe",
    MAIN, CGI, BASIC, HELPER, SECRET, "docs", "docs/w2_probe",
)


# ------------------------------------------------------------------ fixture


class InstalledProductProject(PerlLayoutProject):
    """Proyecto fixture ejercitando el PRODUCTO INSTALADO (recorrido real,
    no unitario): instala con perfil --basic en un tempdir aislado
    (CDAD_INSTALL_ROOT; el HOME real queda intacto) y corre `prepare` con EL
    CLI INSTALADO y los agentes instalados como origen de derivados.

    Reutiliza el fixture T1 (política de tests anidados del caso Perl/Webmin
    + `prepare_perl`) y el arnés de T5 de 004-002 (`build_project`,
    `prepare_args`, `require_derived`) por import. Solo se sustituye la
    MECÁNICA de invocación: el CLI del árbol de trabajo por el instalado.
    """

    def setUp(self) -> None:
        tmp = tempfile.mkdtemp(prefix="cdad-t3-accept-")
        self._tmp = tmp
        self.addCleanup(
            lambda: subprocess.run(["rm", "-rf", tmp], check=False))
        self.install_root = Path(tmp) / "install"
        self._install_isolated_product()
        self.installed_cli = self._locate_installed(CLI_RELPATH)
        self.installed_agents_dir = self._locate_installed(
            MARKER).parent
        self.root = Path(tmp) / "proj"
        build_project(self.root)
        self.apply_layout(self.LAYOUT)

    # ------------------------------------------------------- instalación

    def _install_isolated_product(self) -> None:
        """PD-11/INV-9: instalación aislada con el perfil básico; todo bajo
        el tempdir. SKIP limpio si el entorno no permite construirla."""
        env = dict(os.environ)
        env["CDAD_INSTALL_ROOT"] = str(self.install_root)
        self.install_root.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            ["bash", "install.sh", "--basic"],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            self.skipTest(
                "PD-11 (skip limpio, sin fabricar verde): el entorno no "
                "permitió construir la instalación aislada "
                "(bash install.sh --basic rc="
                f"{proc.returncode}): {proc.stderr.strip()[:400]!r}")

    def _locate_installed(self, relpath: str) -> Path:
        """Localiza un artefacto del producto INSTALADO por su RUTA relativa
        declarada (no se lee contenido de implementación). Preferencia
        determinista: el árbol de configuración de OpenCode del install
        root. Si no existe, AssertionError (defecto del producto)."""
        candidates = sorted(self.install_root.rglob(relpath))
        openconf = self.install_root / ".config" / "opencode"
        preferred = [p for p in candidates
                     if str(p).startswith(str(openconf))]
        ordered = preferred or candidates
        self.assertTrue(
            ordered,
            msg=f"PD-11: el producto instalado no contiene {relpath!r} "
                f"(install root: {self.install_root}; árbol del install: "
                f"{sorted(p.name for p in self.install_root.iterdir())!r})")
        return ordered[0]

    # ------------------------------------------- recorrido con EL INSTALADO

    def prepare(self, *extra: str, role: str = "test-writer",
                substage: str = "red",
                objective: str = "T3 recorrido producto instalado",
                ) -> subprocess.CompletedProcess:
        """`prepare` del arnés estándar sustituyendo la mecánica: EL CLI
        INSTALADO (tempdir) y como origen de derivados los agentes
        INSTALADOS (no los del árbol de trabajo)."""
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.installed_agents_dir)
        args = prepare_args(self.root, role=role, substage=substage,
                            objective=objective, extra=extra)
        return subprocess.run(
            [sys.executable, str(self.installed_cli), *args],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env)


# --------------------------------------------------------------- PD-11


class TestPd11AccIsolatedInstall(InstalledProductProject):
    """PD-11: el recorrido del producto instalado EXISTE y es aislado."""

    def test_pd11_isolated_install_of_basic_profile(self) -> None:
        """PD-11/INV-9: `install.sh --basic` con CDAD_INSTALL_ROOT=<tempdir>
        construye el producto bajo el tempdir (marker de versión, EL CLI
        instalado y los agentes instalados), y TODO el producto queda bajo
        la raíz pedida (HOME real intocado: la instalación es mecanismo, no
        sandbox; la operación en producción queda reservada al dueño)."""
        self.assertTrue(
            (self.install_root / "version.txt").is_file(),
            msg="PD-11: la instalación aislada no dejó el marker de "
                "versión bajo CDAD_INSTALL_ROOT")
        self.assertTrue(
            self.installed_cli.is_file(),
            msg=f"PD-11: el CLI instalado no existe en el árbol instalado "
                f"({self.installed_cli})")
        self.assertTrue(
            (self.installed_agents_dir / TEST_WRITER).is_file(),
            msg=f"PD-11: los agentes instalados no incluyen {TEST_WRITER!r} "
                f" bajo {self.installed_agents_dir}")
        for artifact in (self.install_root, self.installed_cli,
                         self.installed_agents_dir):
            self.assertTrue(
                str(artifact).startswith(str(self.install_root)),
                msg=f"PD-11/INV-9: el artefacto {artifact!r} quedó fuera de "
                    f"la raíz de instalación pedida (aislamiento del "
                    f"recorrido)")


class TestPd11AccPositiveCapabilities(InstalledProductProject):
    """PD-11 (capacidades POSITIVAS) sobre el producto instalado, con la
    política del caso Perl/Webmin de RAÍZ DE TESTS ANIDADA."""

    def test_pd11_positive_capabilities_end_to_end(self) -> None:
        """PD-11 positivas (el CLI INSTALADO publica los derivados del
        proyecto fixture): el test-writer LEE (PD-1) y EDITA (PD-3) su
        árbol de tests anidado — incluido el auxiliar helper.pl; el
        implementer EDITA implementación y NO edita los tests (PD-4; y su
        `read` no deniega los tests, allow por defecto)."""
        proc = self.prepare_perl()
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        for tool, probe in (("read", BASIC), ("read", HELPER),
                            ("edit", BASIC), ("edit", HELPER)):
            with self.subTest(agent=TEST_WRITER, tool=tool, probe=probe):
                got = verdict(tw, tool, probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-11 (positiva): el producto instalado publica "
                        f"para el test-writer {tool}({probe!r}) = {got!r}, "
                        f"la política exige 'allow' (árbol de tests "
                        f"anidado declarado)")
        for tool, probe, expected in (
                ("read", BASIC, "allow"),     # PD-4: su read no deniega tests
                ("edit", MAIN, "allow"),      # PD-4: edita implementación
                ("edit", BASIC, "deny"),      # PD-4: NO edita tests
        ):
            with self.subTest(agent=IMPLEMENTER, tool=tool, probe=probe,
                              expected=expected):
                got = verdict(imp, tool, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"PD-11 (positiva): el producto instalado publica "
                        f"para el implementer {tool}({probe!r}) = {got!r}, "
                        f"la política exige {expected!r}")


class TestPd11AccPositiveDeclaredTestFiles(InstalledProductProject):
    """PD-11/PD-5 (focal positivo): un archivo DECLARADO en test_files bajo
    la raíz de implementación queda habilitado al test-writer del producto
    instalado y denegado al implementer."""

    def test_pd11_declared_test_files_under_impl_positive(self) -> None:
        """PD-11/PD-5 (focal test_files): con test_roots vacía y
        test_files=[<archivo .t bajo implementación>], el producto
        instalado publica al test-writer allow de LEER y EDITAR ese archivo
        declarado, y al implementer DENY en edit (los test_files declarados
        son tests)."""
        proc = self.prepare_perl(
            test_roots=(), test_files=(DECLARED_FILE,))
        pub = require_derived(self, self.root, (TEST_WRITER, IMPLEMENTER))
        tw, imp = pub[TEST_WRITER], pub[IMPLEMENTER]
        for tool in ("read", "edit"):
            with self.subTest(agent=TEST_WRITER, tool=tool,
                              probe=DECLARED_FILE):
                got = verdict(tw, tool, DECLARED_FILE)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-11/PD-5 (positiva): el producto instalado "
                        f"resuelve {tool}({DECLARED_FILE!r}) como {got!r} "
                        f"para el test-writer — el archivo DECLARADO en "
                        f"test_files (bajo implementación) debe quedar "
                        f"abierto al test-writer")
        with self.subTest(agent=IMPLEMENTER, tool="edit",
                          probe=DECLARED_FILE):
            got = verdict(imp, "edit", DECLARED_FILE)
            self.assertEqual(
                got, "deny",
                msg=f"PD-11/PD-5 (positiva): el producto instalado resuelve "
                    f"edit({DECLARED_FILE!r}) como {got!r} para el "
                    f"implementer — los test_files declarados son tests")


class TestPd11AccNegativeCapabilities(InstalledProductProject):
    """PD-11 (capacidades NEGATIVAS) sobre el producto instalado."""

    def test_pd11_negative_capabilities_end_to_end(self) -> None:
        """PD-11 negativas (recorrido real del CLI instalado): el test-writer
        NO lee implementación (PD-2); un archivo con forma de test NO
        declarado bajo la implementación sigue denegado en read y edit
        (PD-5, sin convenciones globales); una ruta PRIVADA anidada en la
        raíz de tests queda denegada en read y edit para TODO rol (PD-6,
        precedencia findLast); el hermano no privado del árbol de tests
        sigue abierto al test-writer (control PD-6)."""
        proc = self.prepare_perl(
            private=(SECRET,),
            extra_files=(SECRET, UNDECLARED_PROBE))
        pub = require_derived(
            self, self.root, tuple(sorted(published_derived(self.root))))
        tw = pub[TEST_WRITER]
        for tool in ("read", "edit"):
            with self.subTest(agent=TEST_WRITER, tool=tool,
                              probe=MAIN, neg="implementación"):
                got = verdict(tw, tool, MAIN)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-11 (negativa): el producto instalado resuelve "
                        f"{tool}({MAIN!r}) como {got!r} para el test-writer "
                        f"— la implementación declarada (barrera mediada "
                        f"de lectura) debe permanecer denegada")
            with self.subTest(agent=TEST_WRITER, tool=tool,
                              probe=UNDECLARED_PROBE, neg="no declarado"):
                got = verdict(tw, tool, UNDECLARED_PROBE)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-11 (negativa): el producto instalado resuelve "
                        f"{tool}({UNDECLARED_PROBE!r}) como {got!r} para el "
                        f"test-writer — un archivo con forma de test NO "
                        f"declarado bajo la implementación sigue denegado")

        for name, text in sorted(pub.items()):
            for tool in ("read", "edit"):
                with self.subTest(agent=name, tool=tool, probe=SECRET,
                                  neg="ruta privada"):
                    got = verdict(text, tool, SECRET)
                    self.assertEqual(
                        got, "deny",
                        msg=f"PD-11/PD-6 (negativa): el producto instalado "
                            f"resuelve {tool}({SECRET!r}) como {got!r} para "
                            f"el derivado {name} — una ruta privada anidada "
                            f"en la raíz de tests debe quedar denegada para "
                            f"TODO rol")
        for tool in ("read", "edit"):
            with self.subTest(agent=TEST_WRITER, tool=tool, probe=BASIC,
                              neg="hermano no privado"):
                got = verdict(tw, tool, BASIC)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-11/PD-6 (control): el hermano no privado "
                        f"{BASIC!r} resolvió {tool} como {got!r} para el "
                        f"test-writer del producto instalado")


class TestPd11AccNoSearchPathEntries(InstalledProductProject):
    """PD-11/PD-9/W-2: ningún derivado del recorrido instalado gana entradas
    por ruta en `grep`/`glob` (barrera inexistente en OpenCode)."""

    def test_pd11_no_grep_glob_path_entries(self) -> None:
        """PD-11/PD-9/W-2: para TODOS los derivados publicados por el CLI
        instalado con la política de tests anidados, los mapas `grep` y
        `glob` NO contienen entradas por ruta de la política (helper
        reusable de T5 de 004-002)."""
        proc = self.prepare_perl(private=(SECRET,),
                                 extra_files=(SECRET,))
        pub = require_derived(
            self, self.root, tuple(sorted(published_derived(self.root))))
        assert_no_search_path_entries(self, pub, PROBES_W2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
