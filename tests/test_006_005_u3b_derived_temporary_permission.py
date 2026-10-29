#!/usr/bin/env python3
"""006-005 U3b RED — el temporal es escribible por el agente derivado (PD-24).

Contract: `docs/specs/006-005-native-path-parity/spec.md` §2.9, §3 PD-24, §4
INV-16, §5 D-5 (extendida); O-4 de la review por escenarios (precedencia
probada con dos fixtures de colisión). Plan: §3 ficha U3 y su bloque
`plan-tasks`.

Superficie observable bajo prueba (la que el contrato declara):

    CDAD_OPENCODE_AGENTS_DIR=<copia de agents/cdad-*.md> \
      python3 scripts/cdad_packet.py prepare --project-root R --role test-writer \
          --substage red --objective ...
    → publica `.opencode/agents/cdad-*.md` + `.opencode/agents/.cdad-derived.json`

El mapa `edit` del derivado se evalúa con el evaluador findLast EXISTENTE
(`tests/pd10_permission_semantics.py`, reutilizado por import): la ÚLTIMA
regla que coincide gana. Ese es el oráculo de precedencia que el contrato
nombra (O-4), no un evaluador nuevo.

Mapa test → postcondición:

  TestPd24DeclaredRootIsEditable
    test_pd24_declared_temporary_root_is_allow_in_edit_map
        -> PD-24: con una raíz temporal declarada por la política aceptada, el
           `edit` del derivado test-writer la lista como `allow`; el scope de
           tests y los co-ubicados se conservan.
    test_pd24_no_other_path_gains_permission
        -> PD-24/INV-16: ninguna otra ruta gana permiso — producto, la
           política, el directorio de derivados y las rutas privadas siguen
           `deny`.
    test_pd24_publication_path_and_manifest_are_unchanged
        -> PD-24: la superficie publicada no cambia (mismos nombres, mismo
           manifiesto con el sha de la política y el sha de cada derivado).
  TestPd24EmptyTemporaryRootsIsByteIdentical
    test_pd24_empty_list_keeps_todays_edit_map
        -> PD-24 (control negativo): con `temporary_roots: []` el mapa `edit`
           del derivado no lleva ninguna entrada de temporal y el resto del
           derivado es byte-idéntico al de un proyecto con la misma política
           donde la única diferencia es la raíz temporal declarada (una vez
           descontadas las líneas de esa raíz).
  TestPd24PrivatePathOverTemporaryRoot
    test_pd24_private_path_overlapping_temporary_root_wins
        -> PD-24/O-4(a): una raíz temporal que solapa una ruta privada
           declarada FUERA de las regiones de producto (el validador la
           admite) ⇒ el `deny` privado gana por findLast.
  TestPd24DerivedDirOverTemporaryRoot
    test_pd24_derived_directory_overlapping_temporary_root_wins
        -> PD-24/O-4(b): una raíz temporal que solapa el directorio de
           derivados (`.opencode/agents/`) ⇒ el `deny` de derivados gana.

Estado RED: hoy el mapa `edit` del derivado test-writer no lleva ninguna raíz
temporal (probe declarado en el plan: `temporary_roots: []` en la política
vigente), así que los casos positivos —incluido el control positivo del
fixture de colisión privada— fallan en su aserción de permiso (AssertionError
de comportamiento ausente, no ImportError ni error de fixture). El control
negativo y las dos colisiones son anclas en su parte de precedencia: hoy
`deny` gana porque no hay `allow` que lo preceda; deben seguir ganando después
de U3 (esa es exactamente la regresión que O-4 vigila).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_004_002_t2_bootstrap import (  # noqa: E402
    POLICY_FILE,
    REPO_ROOT,
    SCRIPT,
    build_project,
    prepare_args,
)
from test_004_002_t5_runtime import (  # noqa: E402
    AGENTS_ENV,
    DERIVED_DIR,
    LAYOUT_FILES,
    MANIFEST,
    TEST_WRITER,
    derived_dir,
    policy_doc,
    published_derived,
    require_derived,
)
from pd10_permission_semantics import perm_map, verdict  # noqa: E402

# Raíz temporal del caso: subdirectorio de primer nivel, disjunto de producto
# (D-5 C2: subdirectorio, nunca una raíz de producto ni `.cdad/` raíz).
TEMPORARY_ROOT = "scratch"
SELECTOR = "scratch/work"
PRIVATE_PATH = "scratch/secret"
DERIVED_TEMP_ROOT = ".opencode/agents/tmp"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_policy(root: Path, *, temporary_roots: list[str],
                 private_paths: list[str] | None = None) -> dict:
    """Política válida del layout CDAD con las raíces del caso."""
    doc = policy_doc("cdad")
    doc["temporary_roots"] = list(temporary_roots)
    if private_paths is not None:
        doc["path_policy"]["private_paths"] = list(private_paths)
    (root / POLICY_FILE).write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return doc


def materialize_layout(root: Path) -> None:
    for rel in LAYOUT_FILES["cdad"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# fixture {rel}\n", encoding="utf-8")


def edit_rules(agent_text: str) -> list[tuple[str, str]]:
    """Reglas del mapa `edit` en orden de archivo (findLast necesita el orden)."""
    return perm_map(agent_text, "edit")


class DerivedProjectCase(unittest.TestCase):
    """Proyecto sintético con layout CDAD, política del caso y prepare real."""

    TEMPORARY_ROOTS: tuple[str, ...] = ()
    PRIVATE_PATHS: tuple[str, ...] | None = None

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u3b-red-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        materialize_layout(self.root)
        write_policy(self.root, temporary_roots=list(self.TEMPORARY_ROOTS),
                     private_paths=(list(self.PRIVATE_PATHS)
                                    if self.PRIVATE_PATHS is not None
                                    else None))
        # Fuente I9: copia temporal de los agentes generados del repo, copiada
        # sin inspección (salida declarada del generador, mismo precedente que
        # test_004_002_t5_runtime.py).
        self.agents_src = Path(self._tmp) / "agents-src"
        self.agents_src.mkdir()
        for source in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            shutil.copy2(source, self.agents_src / source.name)

    def prepare(self) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.agents_src)
        return subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(self.root, role="test-writer", substage="red",
                           objective="U3b derived temporary permission")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )

    def published_test_writer(self) -> str:
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-24 (precondición): el prepare del fixture debe publicar "
                f"los derivados; rc={proc.returncode} "
                f"stdout={proc.stdout[:400]!r} stderr={proc.stderr[:600]!r}")
        return require_derived(self, self.root, (TEST_WRITER,))[TEST_WRITER]

    def assert_verdict(self, agent_text: str, probe: str, expected: str,
                       *, why: str) -> None:
        got = verdict(agent_text, "edit", probe)
        self.assertEqual(
            got, expected,
            msg=f"PD-24: edit({probe!r}) resolvió {got!r}, el contrato exige "
                f"{expected!r} — {why}")


# --------------------------------------------------- PD-24 lado positivo


class TestPd24DeclaredRootIsEditable(DerivedProjectCase):
    """PD-24: la raíz temporal declarada es `allow` en el `edit` del derivado."""

    TEMPORARY_ROOTS = (TEMPORARY_ROOT,)
    # Ruta privada FICTICIA del fixture (no se lee ni usa
    # `tests/.sensitive-patterns.local`): sirve de control de que el allow del
    # temporal no abre una barrera declarada por la política.
    PRIVATE_PATHS = ("tests/.sensitive-patterns.fixture.local",)

    def test_pd24_declared_temporary_root_is_allow_in_edit_map(self) -> None:
        """PD-24: con `temporary_roots: ["scratch"]`, el `edit` del derivado
        test-writer permite escribir dentro de la raíz temporal (y el scope de
        tests del rol sigue permitido)."""
        tw = self.published_test_writer()
        rules = edit_rules(tw)
        self.assertIn(
            "allow", [verb for _pattern, verb in rules],
            msg=f"PD-24: el mapa `edit` del derivado no tiene ninguna regla "
                f"`allow`; reglas: {rules!r}")
        for probe in (f"{TEMPORARY_ROOT}/aux.py", f"{SELECTOR}/probe.txt"):
            with self.subTest(probe=probe):
                self.assert_verdict(
                    tw, probe, "allow",
                    why="la raíz temporal declarada por la política aceptada "
                        "debe ser escribible por el agente del rol (§2.9)")
        # Control: el permiso del rol no se perdió al emitir el temporal.
        self.assert_verdict(
            tw, "tests/test_u3_fixture.py", "allow",
            why="el scope de tests del test-writer se conserva")
        self.assert_verdict(
            tw, "scripts/test_helper.py", "allow",
            why="el co-ubicado declarado por la política se conserva")

    def test_pd24_no_other_path_gains_permission(self) -> None:
        """PD-24/INV-16: ninguna otra ruta gana permiso — producto, la
        política, el directorio de derivados y las rutas privadas siguen
        `deny` con la raíz temporal declarada."""
        tw = self.published_test_writer()
        cases = (
            ("scripts/x.py", "producto: implementación declarada por la política"),
            ("agents/y.md", "producto: implementación declarada por la política"),
            ("install.sh", "producto: archivo de implementación de la política"),
            ("docs/cdad-policy.json", "la política es dato del dueño (INV-7)"),
            (f"{DERIVED_DIR}/cdad-test-writer.md",
             "los derivados no son editables por el rol"),
            ("tests/.sensitive-patterns.fixture.local",
             "ruta privada declarada por la política del fixture"),
        )
        for probe, why in cases:
            with self.subTest(probe=probe):
                self.assert_verdict(tw, probe, "deny", why=why)

    def test_pd24_publication_path_and_manifest_are_unchanged(self) -> None:
        """PD-24: la superficie publicada no cambia — mismos nombres de
        derivado, mismo manifiesto, con el sha de la política aceptada y el
        sha de cada derivado publicado."""
        tw = self.published_test_writer()
        published = published_derived(self.root)
        expected = sorted(p.name for p in self.agents_src.glob("cdad-*.md"))
        self.assertEqual(
            sorted(published), expected,
            msg=f"PD-24: la publicación debe espejar la fuente; publicados "
                f"{sorted(published)} vs esperados {expected}")
        manifest_path = derived_dir(self.root) / MANIFEST
        self.assertTrue(
            manifest_path.is_file(),
            msg=f"PD-24: falta el manifiesto {DERIVED_DIR}/{MANIFEST}")
        blob = manifest_path.read_text(encoding="utf-8")
        policy_sha = sha256_bytes((self.root / POLICY_FILE).read_bytes())
        self.assertIn(
            policy_sha, blob,
            msg="PD-24: el manifiesto no registra el sha de la política "
                "aceptada (la raíz temporal declarada cambia ese sha)")
        self.assertIn(
            sha256_bytes(tw.encode("utf-8")), blob,
            msg="PD-24: el manifiesto no registra el sha del derivado "
                "test-writer publicado")


# -------------------------------------------- PD-24 control negativo


class TestPd24EmptyTemporaryRootsIsByteIdentical(DerivedProjectCase):
    """PD-24 (control negativo): con `temporary_roots: []` nada cambia."""

    TEMPORARY_ROOTS = ()
    # Ruta privada del fixture FUERA de la raíz temporal, para que el control
    # negativo mida sólo la lista vacía (no mezcle barreras privadas).
    PRIVATE_PATHS = ("docs/private-notes",)

    def _prepare_clone(self, name: str, temporary_roots: list[str]) -> str:
        """Proyecto hermano con el MISMO layout y política, salvo las raíces
        temporales; devuelve el derivado test-writer publicado."""
        tmp = Path(self._tmp) / name
        root = tmp / "proj"
        build_project(root)
        materialize_layout(root)
        write_policy(root, temporary_roots=temporary_roots,
                     private_paths=list(self.PRIVATE_PATHS))
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.agents_src)
        proc = subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(root, role="test-writer", substage="red",
                           objective="U3b control negativo")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )
        self.assertEqual(
            proc.returncode, 0,
            msg=f"PD-24 (precondición del control): el prepare del proyecto "
                f"{name} debe publicar los derivados; rc={proc.returncode} "
                f"stderr={proc.stderr[:600]!r}")
        published = published_derived(root)
        self.assertIn(TEST_WRITER, published,
                      msg=f"PD-24: el proyecto {name} no publicó {TEST_WRITER}")
        return published[TEST_WRITER].decode("utf-8")

    def test_pd24_empty_list_keeps_todays_edit_map(self) -> None:
        """PD-24: con `temporary_roots: []` el mapa `edit` del derivado es el
        de hoy — no aparece ninguna entrada de temporal, `scratch/` sigue
        denegado, y el mapa es idéntico al de un proyecto con la misma
        política donde la ÚNICA diferencia es la raíz temporal declarada, una
        vez descontadas las entradas de esa raíz.

        Oráculo elegido (declarado): comparación de las listas ORDENADAS de
        reglas entre los dos proyectos, en vez de una lista dorada fija — la
        lista dorada se rompería por cualquier cambio de layout ajeno a esta
        PD, y el contenido de la PD es «la lista vacía no emite nada y nada
        más cambia»."""
        tw = self.published_test_writer()
        rules = edit_rules(tw)
        temporary_rules = [
            rule for rule in rules
            if rule[0] == TEMPORARY_ROOT or rule[0].startswith(f"{TEMPORARY_ROOT}/")
        ]
        self.assertEqual(
            temporary_rules, [],
            msg=f"PD-24: con `temporary_roots: []` el mapa `edit` no puede "
                f"tener ninguna entrada de la raíz temporal; obtenidas "
                f"{temporary_rules!r} (mapa completo: {rules!r})")
        self.assert_verdict(
            tw, f"{SELECTOR}/probe.txt", "deny",
            why="la lista vacía no autoriza temporales")
        self.assert_verdict(
            tw, "tests/test_u3_fixture.py", "allow",
            why="el scope de tests del rol no cambia")

        declared = self._prepare_clone("declared", [TEMPORARY_ROOT])
        declared_bytes = declared.encode("utf-8")
        # Se descuentan EXACTAMENTE las líneas de la raíz temporal declarada
        # (`"scratch": allow` / `"scratch/**": allow`); todo lo demás debe
        # coincidir byte a byte con el derivado de la lista vacía.
        # Remove only complete V2 edit entries for the declared root. Keep
        # every other byte (including frontmatter/body and line endings).
        lines = declared_bytes.splitlines(keepends=True)
        stripped_lines: list[bytes] = []
        i = 0
        while i < len(lines):
            if re.match(rb"^  - action: ", lines[i]):
                end = i + 1
                while end < len(lines) and not re.match(rb"^  - action: ", lines[end]):
                    end += 1
                entry = b"".join(lines[i:end])
                action = re.search(rb"^  - action: (.+)$", entry, re.M)
                resource = re.search(rb"^    resource: ['\"]?([^'\"\r\n]+)", entry, re.M)
                if not (action and action.group(1).strip() == b"edit" and resource and
                        resource.group(1) in (b"scratch", b"scratch/**")):
                    stripped_lines.extend(lines[i:end])
                i = end
            else:
                stripped_lines.append(lines[i])
                i += 1
        stripped = b"".join(stripped_lines)
        self.assertEqual(
            tw.encode("utf-8"), stripped,
            msg="PD-24: declarar una raíz temporal sólo puede agregar las "
                "líneas de esa raíz; el resto del derivado debe ser "
                "byte-idéntico al de `temporary_roots: []`")
        self.assertNotEqual(
            tw.encode("utf-8"), stripped.replace(b"mode: subagent", b"mode: changed", 1),
            msg="PD-24 control negativo: una diferencia fuera de la entrada temporal debe detectarse")
        declared_rules = edit_rules(declared)
        without_temporary = [
            rule for rule in declared_rules
            if not (rule[0] == TEMPORARY_ROOT
                    or rule[0].startswith(f"{TEMPORARY_ROOT}/"))
        ]
        self.assertEqual(
            rules, without_temporary,
            msg=f"PD-24: el resto del mapa `edit` debe ser idéntico (sin "
                f"raíz: {rules!r} / con raíz descontada: "
                f"{without_temporary!r})")


# ------------------------------------------------ PD-24 precedencia (O-4)


class TestPd24PrivatePathOverTemporaryRoot(DerivedProjectCase):
    """PD-24/O-4(a): una raíz temporal que solapa una ruta privada."""

    TEMPORARY_ROOTS = (TEMPORARY_ROOT,)
    PRIVATE_PATHS = (PRIVATE_PATH,)

    def test_pd24_private_path_overlapping_temporary_root_wins(self) -> None:
        """PD-24/O-4(a): la ruta privada `scratch/secret` está declarada fuera
        de las regiones de producto (el validador de raíces temporales la
        admite) y solapa la raíz temporal `scratch` ⇒ el `deny` privado gana
        por findLast; el resto de la raíz temporal sigue escribible."""
        # Precondición del fixture: la política es válida (el validador sólo
        # garantiza disjunción con producto, no con rutas privadas).
        validated = subprocess.run(
            [sys.executable, str(SCRIPT), "validate-policy",
             "--project-root", str(self.root)],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        self.assertEqual(
            validated.returncode, 0,
            msg=f"PD-24/O-4(a) (precondición): la política del fixture debe "
                f"validar; salida={validated.stdout!r} "
                f"{validated.stderr!r}")
        tw = self.published_test_writer()
        # Control positivo: la raíz temporal declarada es escribible.
        self.assert_verdict(
            tw, f"{TEMPORARY_ROOT}/aux.py", "allow",
            why="la raíz temporal declarada es escribible por el rol")
        # La colisión: la barrera privada se emite después y gana.
        for probe in (PRIVATE_PATH, f"{PRIVATE_PATH}/notes.md"):
            with self.subTest(probe=probe):
                self.assert_verdict(
                    tw, probe, "deny",
                    why="la ruta privada declarada por la política conserva "
                        "su precedencia sobre el allow del temporal "
                        "(findLast: las barreras se emiten después de las "
                        "reglas de permiso del rol)")


class TestPd24DerivedDirOverTemporaryRoot(DerivedProjectCase):
    """PD-24/O-4(b): una raíz temporal que solapa `.opencode/agents/`."""

    TEMPORARY_ROOTS = (DERIVED_TEMP_ROOT,)

    def test_pd24_derived_directory_overlapping_temporary_root_wins(self) -> None:
        """PD-24/O-4(b): la raíz temporal `.opencode/agents/tmp` solapa el
        directorio de derivados ⇒ el `deny` de derivados gana por findLast y
        ningún archivo de derivado queda editable."""
        tw = self.published_test_writer()
        for probe in (f"{DERIVED_TEMP_ROOT}/x.md",
                      f"{DERIVED_TEMP_ROOT}/deep/y.md",
                      f"{DERIVED_DIR}/cdad-test-writer.md"):
            with self.subTest(probe=probe):
                self.assert_verdict(
                    tw, probe, "deny",
                    why="el directorio de derivados conserva su barrera sobre "
                        "el allow del temporal (findLast)")
        # Control: el permiso del rol no se perdió.
        self.assert_verdict(
            tw, "tests/test_u3_fixture.py", "allow",
            why="el scope de tests del test-writer se conserva")


if __name__ == "__main__":
    unittest.main()
