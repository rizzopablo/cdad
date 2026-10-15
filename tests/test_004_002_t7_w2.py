#!/usr/bin/env python3
"""004-002 T7 W-2 RED — semántica real de grep/glob en OpenCode (derivados).

Contrato: docs/specs/004-002-project-execution-bootstrap/spec.md
(PD-7/PD-8/PD-5) + docs/specs/004-002-project-execution-bootstrap/
t7-live-walk.md §3–4 (sondas en vivo) + plan.md I9; disposición firmada del
orquestador (paquete red-020).

Hallazgo W-2 (sonda en vivo, t7-live-walk.md §3): en OpenCode los permisos
de `grep` y `glob` se evalúan contra el PATRÓN DE BÚSQUEDA (la regex o el
glob que se busca), NO contra la ruta. Los mapas por ruta que los derivados
I9 emiten para grep/glob son inertes: declaran una barrera que no existe.
Disposición: los derivados dejan de emitir entradas por ruta en
`grep`/`glob`; `read`/`edit` conservan sus mapas por ruta (verificados en
vivo). En Claude Code el guard SÍ media Grep/Glob por path/pattern (C2) —
esas pruebas no cambian.

Superficie observable: derivados publicados por `prepare` en proyectos
sintéticos (tempdirs); ninguna escritura fuera de ellos; no se lee
implementación (los únicos archivos de producto leídos son las salidas
publicadas del prepare y la copia temporal de agents/cdad-*.md, salidas
declaradas del generador — mismo precedente que test_004_002_t5_runtime.py).
No se lee tests/.sensitive-patterns.local.

Mapa test → postcondición:

  TestW2ANoPathSearchEntriesCdad / …Conventional / …Odoo
    test_w2_a_no_path_entries_in_grep_glob
      -> W-2(a) (PD-7/PD-8, enmienda de oráculo): NINGÚN derivado publicado
         contiene entradas por ruta de raíces de la política en `grep` ni
         `glob`. RED hoy: los derivados I9 emiten esas entradas inertes.
  TestW2BReadEditRoleMapsRetained
    test_w2_b_read_edit_maps_retained
      -> W-2(b) (PD-7/I9, parte NO enmendada): `read` y `edit` conservan sus
         mapas por rol (impl. denegada al test-writer, tests y co-ubicados
         permitidos, política no editable, lectores sin escritura).
  TestW2CStaleDerivationRegeneration
    test_w2_c_stale_derivation_regenerated_without_reconciliation
      -> W-2(c) (PD-5/PD-8/I9): derivados publicados por una derivación
         ANTERIOR (bytes en disco = manifiesto, pero distintos de la
         derivación actual) se REGENERAN en el siguiente prepare sin pedir
         reconciliación (la política no cambió). RED hoy.
    test_w2_c_hand_modified_contrast_still_fails
      -> W-2(c) contraste (PD-8/I9): derivado editado a mano (bytes ≠
         manifiesto) sigue fallando SIN sobrescribir. Control verde.

La "derivación anterior" se simula sin leer implementación: se escriben un
derivado + manifiesto AUTOCONSISTENTES (los bytes en disco y el hash que el
manifiesto declara para ese derivado coinciden) con contenido distinto al
que la derivación actual produce. El producto no puede distinguir ese
estado de una derivación publicada por una revisión anterior de la
herramienta sin re-derivar; la postcondición exige que re-derive,
regenere y no pida reconciliación (PD-1: ninguna escritura por una
reconciliación que no ocurrió; PD-5: los derivados deben corresponder a la
derivación aceptada antes del próximo despacho).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest

from pd10_permission_semantics import verdict  # noqa: E402
from test_004_002_t5_runtime import (  # noqa: E402
    DERIVED_DIR,
    LayoutProject,
    MANIFEST,
    TEST_WRITER,
    assert_no_search_path_entries,
    derived_dir,
    mark_active_packet,
    policy_path_probes,
    policy_sha,
    published_derived,
    require_derived,
    sha256_bytes,
)

POLICY_REL = "docs/cdad-policy.json"

SIM_MARKER = "<!-- W-2: derivación anterior simulada -->"

STALE_MSG = (
    "W-2(c): el prepare pidió reconciliación (o falló) ante derivados "
    "publicados por una derivación ANTERIOR autoconsistente (bytes = "
    "manifiesto, política sin cambios) — debe regenerarlos sin pedir "
    "reconciliación")


# ------------------------------------------------------------------- (a)


class _W2NoPathEntriesMixin:
    """W-2(a): ningún derivado publicado contiene entradas por ruta de
    raíces de la política en `grep`/`glob` (mixin; cada layout es una
    clase con su propio fixture)."""

    def test_w2_a_no_path_entries_in_grep_glob(self) -> None:
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = {n: b.decode("utf-8")
               for n, b in published_derived(self.root).items()}
        self.assertTrue(
            pub, msg="precondición: el prepare no publicó derivados")
        assert_no_search_path_entries(
            self, pub, policy_path_probes(self.LAYOUT))


class TestW2ANoPathSearchEntriesCdad(_W2NoPathEntriesMixin, LayoutProject):
    """W-2(a) layout CDAD (el de este repo)."""
    LAYOUT = "cdad"


class TestW2ANoPathSearchEntriesConventional(_W2NoPathEntriesMixin,
                                             LayoutProject):
    """W-2(a) layout convencional."""
    LAYOUT = "conventional"


class TestW2ANoPathSearchEntriesOdoo(_W2NoPathEntriesMixin, LayoutProject):
    """W-2(a) layout Odoo."""
    LAYOUT = "odoo"


# ------------------------------------------------------------------- (b)


class TestW2BReadEditRoleMapsRetained(LayoutProject):
    """W-2(b): `read` y `edit` conservan sus mapas por rol (PD-7/I9, la
    parte del contrato que W-2 NO enmienda)."""
    LAYOUT = "cdad"

    def assert_verdicts(self, agent_text: str, agent: str,
                        expectations: tuple[tuple[str, str, str], ...]) -> None:
        for tool, probe, expected in expectations:
            with self.subTest(agent=agent, tool=tool, probe=probe):
                got = verdict(agent_text, tool, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"W-2(b): {agent} — {tool}({probe!r}) resolvió "
                        f"{got!r}, la política exige {expected!r}")

    def test_w2_b_read_edit_maps_retained(self) -> None:
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: el prepare del fixture debe tener éxito: "
                f"{proc.stdout} {proc.stderr}")
        pub = require_derived(self, self.root,
                              ("cdad-test-writer.md", "cdad-implementer.md",
                               "cdad-reviewer.md"))
        self.assert_verdicts(pub["cdad-test-writer.md"],
                             "cdad-test-writer.md", (
            ("read", "scripts/x.py", "deny"),        # implementación
            ("read", "agents/y.md", "deny"),         # implementación
            ("read", "scripts/test_h.py", "allow"),  # co-ubicado declarado
            ("read", "tests/test_a.py", "allow"),
            ("edit", "tests/test_a.py", "allow"),
            ("edit", "scripts/test_h.py", "allow"),
            ("edit", "scripts/x.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        self.assert_verdicts(pub["cdad-implementer.md"],
                             "cdad-implementer.md", (
            ("edit", "scripts/x.py", "allow"),
            ("edit", "scripts/test_h.py", "deny"),   # co-ubicado es test
            ("edit", "tests/test_a.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))
        self.assert_verdicts(pub["cdad-reviewer.md"], "cdad-reviewer.md", (
            ("edit", "scripts/x.py", "deny"),
            ("edit", "tests/test_a.py", "deny"),
            ("edit", "docs/cdad-policy.json", "deny"),
        ))


# ------------------------------------------------------------------- (c)


class TestW2CStaleDerivationRegeneration(LayoutProject):
    """W-2(c): regeneración de una derivación anterior (PD-5/PD-8/I9) y su
    contraste con el derivado editado a mano."""
    LAYOUT = "cdad"

    def _first_prepare(self) -> dict[str, bytes]:
        proc = self.prepare()
        self.assertEqual(
            proc.returncode, 0,
            msg=f"precondición: primer prepare falló: "
                f"{proc.stdout} {proc.stderr}")
        pub = published_derived(self.root)
        self.assertIn(
            TEST_WRITER, pub,
            msg="precondición: el derivado test-writer no fue publicado")
        return pub

    def test_w2_c_stale_derivation_regenerated_without_reconciliation(
            self) -> None:
        """W-2(c): con bytes en disco IGUALES al manifiesto pero distintos
        de la derivación actual (simulación de derivación anterior), el
        siguiente prepare regenera el derivado (vuelve a la derivación
        actual) SIN pedir reconciliación: rc 0, marcador simulado ausente,
        manifiesto actualizado."""
        snapshot1 = self._first_prepare()
        manifest_path = derived_dir(self.root) / MANIFEST
        self.assertTrue(
            manifest_path.is_file(),
            msg="precondición: el manifiesto de derivados no fue publicado")
        # Simulación de "derivación anterior" sin leer implementación:
        # derivado con contenido distinto al que el producto genera
        # (marcador en el cuerpo, fuera del frontmatter) + manifiesto
        # AUTOCONSISTENTE (registra el hash de esos bytes simulados).
        fabricated = snapshot1[TEST_WRITER] + \
            f"\n{SIM_MARKER}\n".encode("utf-8")
        fab_sha = sha256_bytes(fabricated)
        old_sha = sha256_bytes(snapshot1[TEST_WRITER])
        manifest_text = manifest_path.read_text(encoding="utf-8")
        self.assertIn(
            old_sha, manifest_text,
            msg="precondición: el manifiesto no registra el hash del "
                "derivado publicado (contrato PD-8/I9)")
        manifest_path.write_text(
            manifest_text.replace(old_sha, fab_sha), encoding="utf-8")
        (derived_dir(self.root) / TEST_WRITER).write_bytes(fabricated)
        self.assertEqual(
            sha256_bytes((derived_dir(self.root) / TEST_WRITER)
                         .read_bytes()),
            fab_sha,
            msg="fixture: los bytes simulados no quedaron en disco")
        # Estado simulado: bytes en disco == manifiesto; la política NO
        # cambió; el contenido NO es el que la derivación actual produce.
        mark_active_packet(self.root, "completed")
        second = self.prepare(role="implementer", substage="green",
                              objective="encargo tras derivación anterior")
        self.assertEqual(
            second.returncode, 0,
            msg=f"{STALE_MSG} (rc={second.returncode}: "
                f"{second.stdout} {second.stderr})")
        # Regenerado: los bytes vuelven a la derivación actual (el marcador
        # simulado desaparece) y el manifiesto registra la derivación viva.
        restored = (derived_dir(self.root) / TEST_WRITER).read_bytes()
        self.assertNotIn(
            SIM_MARKER.encode("utf-8"), restored,
            msg="W-2(c): el derivado publicado por una derivación anterior "
                "NO se regeneró en el siguiente prepare (los bytes "
                "simulados siguen en disco)")
        self.assertEqual(
            restored, snapshot1[TEST_WRITER],
            msg="W-2(c): tras regenerar, el derivado no coincide con la "
                "derivación actual (bytes de referencia del primer prepare "
                "con la misma fuente y política)")
        new_manifest = manifest_path.read_text(encoding="utf-8")
        self.assertNotIn(
            fab_sha, new_manifest,
            msg="W-2(c): el manifiesto sigue registrando el hash de los "
                "bytes de la derivación anterior")
        self.assertIn(
            sha256_bytes(restored), new_manifest,
            msg="W-2(c): el manifiesto no registra el hash del derivado "
                "regenerado")

    def test_w2_c_hand_modified_contrast_still_fails(self) -> None:
        """W-2(c) contraste (PD-8/I9): derivado editado a mano (bytes ≠
        manifiesto) hace fallar el siguiente prepare SIN sobrescribirlo.
        Distingue la regeneración legítima de la mutación manual."""
        self._first_prepare()
        derived = derived_dir(self.root) / TEST_WRITER
        derived.write_bytes(derived.read_bytes() + b"\n<!-- mano -->\n")
        mutated = derived.read_bytes()  # los bytes a mano que deben conservarse
        mark_active_packet(self.root, "completed")
        second = self.prepare(role="implementer", substage="green",
                              objective="encargo tras derivado a mano")
        self.assertNotEqual(
            second.returncode, 0,
            msg="W-2(c) contraste: prepare aceptó un derivado editado a "
                "mano (bytes ≠ manifiesto)")
        self.assertEqual(
            derived.read_bytes(), mutated,
            msg="W-2(c) contraste: el derivado editado a mano fue "
                "sobrescrito")
        self.assertEqual(
            second.stdout, "",
            msg="W-2(c) contraste: el fallo imprimió un paquete despachable")


if __name__ == "__main__":
    unittest.main(verbosity=2)
