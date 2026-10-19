#!/usr/bin/env python3
"""006-005 U6-7b RED — los derivados no heredan la palanca `write` (E2/PD-24).

Contract: `docs/specs/006-005-native-path-parity/spec.md` §2.9, §3 (E2,
PD-24), §4 (INV-3, INV-7, INV-16) + `docs/epics/epic-006-opencode-concurrency/
execution.md` hallazgo U6-7 (sondas reales P1/P2/P3 contra OpenCode v2.0.27)
y la aceptación del fix U6-7b.

HECHO DE CONTRATO MEDIDO (v2.0.27, execution.md U6-7)
-----------------------------------------------------
La herramienta de **escritura** evalúa las claves `edit` y `write` del bloque
`permission` **en orden de archivo** y gana la **última regla que coincide**
(findLast). Una instalación anterior al fix U6-7 lleva `  write: ask` dentro
del bloque `permission` (después del mapa `edit`); como la derivación
reemplaza `read`/`edit` y **conserva el resto** del bloque, ese `write: ask`
sobrevive en el derivado y anula su mapa recién derivado:

  - con `--auto` se aprueba toda escritura, incluidas las que `edit` niega;
  - en una corrida no interactiva se rechaza toda escritura, incluidas las
    que `edit` permite.

U6-7b exige que `prepare`, al construir los derivados desde una copia
INSTALADA que trae la palanca, **retire/reemplace** las reglas de la
herramienta de escritura: el veredicto efectivo de escritura del derivado
debe ser exactamente el de su mapa `edit` (E2/PD-24).

Superficie observable bajo prueba (artefactos, nunca implementación)
--------------------------------------------------------------------
  - `agents/cdad-*.md` de HEAD (salidas declaradas del generador) copiados a
    un directorio temporal de "instalación", con `  write: ask` reinsertado
    en el bloque `permission` (fixture de la instalación previa al fix).
  - `scripts/cdad_packet.py prepare` en un proyecto descartable, con
    `CDAD_OPENCODE_AGENTS_DIR` apuntando a esa copia instalada, como proceso
    (mismo patrón que `test_004_002_t5_runtime.py` y
    `test_006_005_u3b_derived_temporary_permission.py`).
  - Los derivados publicados en `.opencode/agents/` y su manifiesto.

El bloque `permission` se evalúa con la regla del runtime reutilizando, por
import, el evaluador de `tests/test_006_005_u6fix7_write_lever.py`
(`write_rule_list`/`write_verdict` = `edit` + `write` en orden de archivo,
findLast) y el de `tests/pd10_permission_semantics.py` (`edit_verdict`). No
se reimplementa ninguna semántica de evaluación.

Mapa test → postcondición (docstrings «E2/PD-24 (U6-7b)»)
---------------------------------------------------------
  TestDerivedAgentsIgnoreInstalledWriteLever
    test_u6_7b_every_derived_agent_ignores_the_installed_write_lever
        -> E2/PD-24 (U6-7b): para CADA rol publicado por `prepare`
           (architect, test-writer, implementer, reviewer, scribe y sus
           variantes -odoo) y para todas las rutas de sondeo, el veredicto
           efectivo de escritura coincide con el mapa `edit` del derivado y
           nunca es `ask`.
    test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary
        -> PD-24: test-writer: `tests/x.py` allow, `docs/x.md` deny, raíz
           temporal declarada (`.cdad/tmp/x`) allow; -odoo: tests allow,
           models deny.
    test_u6_7b_derived_implementer_and_readers_keep_their_maps
        -> PD-24: implementer: `tests/x.py` deny, código allow; lectores
           (architect/reviewer/scribe y -odoo): toda ruta deny.
    test_u6_7b_derived_orchestrator_control_stays_allow
        -> control: el orchestrator publica `permission: allow` y nunca
           llevó la palanca; la escritura sigue allow y nunca `ask`.
  TestDerivedAgentsIgnoreInstalledWriteLeverDrift
    test_u6_7b_second_prepare_does_not_claim_hand_edits
        -> E2/PD-24 (U6-7b): publicado el derivado, un `prepare` siguiente
           no reclama edición a mano (rc=0): el retiro de la palanca queda
           registrado en el manifiesto de deriva, no es una divergencia.

A-1 — test existente reformulado en este RED
--------------------------------------------
`tests/test_004_002_t5_runtime.py::without_maps` (usado por
`test_pd8_i9_derived_body_is_byte_identical_to_source` y por
`test_pd8_i9_reconciled_policy_regenerates_deriveds`) fijaba que la
derivación conserva byte a byte **todo** el frontmatter salvo los mapas
`read/grep/glob/edit` y la cabecera `permission:` — es decir, fijaba que la
clave `write` del origen se conserva. U6-7b exige lo contrario: la región
reemplazada incluye también `write` (la herramienta de escritura), porque
conservarla reinserta la palanca que anula el mapa derivado. Se reformula el
oráculo declarando el reemplazo: `write` pasa a la región de permisos que la
derivación reemplaza/retira; **el resto sigue comparándose byte a byte**. No
se encontró ningún otro test que fije esa conservación.

Estado RED: con la copia instalada del fixture, los derivados de HEAD
publicados por `prepare` conservan `  write: ask`, así que el veredicto
efectivo de escritura resuelve `ask` para cualquier ruta y las aserciones de
comportamiento fallan por AssertionError (no por ImportError ni por fixture).
"""

from __future__ import annotations

import json
import os
import re
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
    derived_dir,
    mark_active_packet,
    policy_doc,
    published_derived,
)
from test_006_005_u6fix7_write_lever import (  # noqa: E402
    edit_verdict,
    write_verdict,
)

ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
ROLE_AGENTS = tuple(
    [f"cdad-{role}.md" for role in ROLES]
    + [f"cdad-{role}-odoo.md" for role in ROLES]
)
ORCHESTRATOR = "cdad-orchestrator.md"

# Sondas comunes: se comparan contra el mapa `edit` del propio derivado; lo
# que importa es que la herramienta de escritura resuelva EXACTAMENTE eso.
PROBES = (
    "tests/x.py",
    "docs/x.md",
    ".cdad/tmp/x",
    "scripts/x.py",
    ".opencode/agents/cdad-test-writer.md",
    "addons/m/tests/test_m.py",
    "addons/m/models/m.py",
)


def reinsert_write_lever(agent_text: str) -> str:
    """Copia instalada PRE-FIX: `  write: ask` dentro del bloque `permission`.

    Reproduce la instalación anterior al fix U6-7 (`execution.md`: la palanca
    cdad-010 P1 se emitía dentro del bloque, después del mapa `edit`). Se
    inserta al cierre del mapa `edit` (misma profundidad que las claves del
    bloque), de modo que la herramienta de escritura la evalúe DESPUÉS del
    mapa. Los agentes sin bloque `permission` (orchestrator: `permission:
    allow`) no llevaban la palanca y quedan intactos.
    """
    lines = agent_text.splitlines(keepends=True)
    end = next(
        index for index in range(1, len(lines)) if lines[index].strip() == "---"
    )
    frontmatter = lines[:end]
    if not any(line.rstrip("\n") == "permission:" for line in frontmatter):
        return agent_text
    if any(re.fullmatch(r"  write:.*\n?", line) for line in frontmatter):
        return agent_text
    edit_index = next(
        index for index, line in enumerate(frontmatter)
        if re.fullmatch(r"  edit:.*\n?", line)
    )
    if re.fullmatch(r"  edit:\s+\S.*\n?", lines[edit_index]):
        insert_at = edit_index + 1
    else:
        insert_at = edit_index + 1
        while insert_at < end and lines[insert_at].startswith("    "):
            insert_at += 1
    return "".join(
        lines[:insert_at] + ["  write: ask\n"] + lines[insert_at:]
    )


def materialize_layout(root: Path) -> None:
    for rel in LAYOUT_FILES["cdad"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# fixture {rel}\n", encoding="utf-8")


class InstalledLeverProject(unittest.TestCase):
    """Proyecto descartable + copia INSTALADA pre-fix; `prepare` publica."""

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u67b-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        materialize_layout(self.root)
        (self.root / POLICY_FILE).write_text(
            json.dumps(policy_doc("cdad"), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        # Copia instalada de FIXTURE: agentes generados de HEAD + palanca
        # reinsertada (nunca la copia real del HOME).
        self.installed = Path(self._tmp) / "installed-agents"
        self.installed.mkdir()
        self.installed_texts: dict[str, str] = {}
        for source in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            text = reinsert_write_lever(source.read_text(encoding="utf-8"))
            (self.installed / source.name).write_text(
                text, encoding="utf-8")
            self.installed_texts[source.name] = text
        self.prepare = self.run_prepare(
            role="test-writer", substage="red",
            objective="U6-7b installed copy with write lever",
        )
        self.derived: dict[str, str] = {}
        base = derived_dir(self.root)
        if base.is_dir():
            self.derived = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(base.glob("cdad-*.md"))
            }

    def run_prepare(self, *extra: str, role: str = "test-writer",
                    substage: str = "red",
                    objective: str = "U6-7b") -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.installed)
        return subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(self.root, role=role, substage=substage,
                           objective=objective, extra=extra)],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )

    def require_derived(self) -> None:
        self.assertEqual(
            self.prepare.returncode, 0,
            msg=f"E2/PD-24 (U6-7b) (precondición): `prepare` debe aceptar la "
                f"copia instalada y publicar los derivados; "
                f"rc={self.prepare.returncode} "
                f"stdout={self.prepare.stdout[:400]!r} "
                f"stderr={self.prepare.stderr[:600]!r}")
        self.assertEqual(
            sorted(self.derived),
            sorted(self.installed_texts),
            msg=f"E2/PD-24 (U6-7b) (precondición): los derivados publicados "
                f"en {DERIVED_DIR}/ deben espejar la copia instalada; faltan "
                f"{sorted(set(self.installed_texts) - set(self.derived))}")
        # Precondición del fixture: la copia instalada SÍ trae la palanca.
        for agent in ROLE_AGENTS:
            with self.subTest(agent=agent, fixture="installed-write-ask"):
                self.assertIn(
                    "  write: ask",
                    self.installed_texts[agent],
                    msg=f"E2/PD-24 (U6-7b) (precondición del fixture): "
                        f"{agent} de la copia instalada no lleva la palanca "
                        f"`write: ask`; el caso no probaría nada.")

    def assert_write_matches_edit(self, agent: str,
                                  probes: tuple[str, ...]) -> None:
        text = self.derived[agent]
        for probe in probes:
            with self.subTest(agent=agent, probe=probe):
                expected = edit_verdict(text, probe)
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7b): el derivado {agent} resolvió "
                        f"{got!r} para {probe!r}; su mapa `edit` resuelve "
                        f"{expected!r}. El derivado se construyó desde una "
                        f"copia instalada que trae `write: ask`: la "
                        f"derivación debe reemplazar/retirar las reglas de "
                        f"la herramienta de escritura (v2.0.27 evalúa "
                        f"`edit` y `write` juntas, findLast) para que el "
                        f"mapa derivado no quede anulado.")
                self.assertNotEqual(
                    got, "ask",
                    msg=f"E2/PD-24 (U6-7b): el derivado {agent} dejó "
                        f"{probe!r} en `ask`; la palanca de la copia "
                        f"instalada no puede sobrevivir a la derivación.")


class TestDerivedAgentsIgnoreInstalledWriteLever(InstalledLeverProject):
    """E2/PD-24 (U6-7b): la palanca instalada no rige el derivado."""

    def test_u6_7b_every_derived_agent_ignores_the_installed_write_lever(
            self) -> None:
        """E2/PD-24 (U6-7b): para cada rol publicado y su variante -odoo, el
        veredicto efectivo de escritura coincide con el mapa `edit` derivado
        para todas las sondas y nunca es `ask`, aunque la copia instalada de
        la que se derivó lleve `write: ask` después del mapa."""
        self.require_derived()
        for agent in ROLE_AGENTS:
            with self.subTest(agent=agent):
                self.assert_write_matches_edit(agent, PROBES)

    def test_u6_7b_derived_test_writer_keeps_tests_docs_and_temporary(
            self) -> None:
        """E2/PD-24 (U6-7b): test-writer derivado: `tests/x.py` allow,
        `docs/x.md` deny y la raíz temporal declarada (`.cdad/tmp/x`) allow;
        su variante -odoo: tests allow, models deny."""
        self.require_derived()
        cases = (
            ("cdad-test-writer.md", "tests/x.py", "allow"),
            ("cdad-test-writer.md", "docs/x.md", "deny"),
            ("cdad-test-writer.md", ".cdad/tmp/x", "allow"),
            ("cdad-test-writer.md", "scripts/x.py", "deny"),
            ("cdad-test-writer-odoo.md", "addons/m/tests/test_m.py", "allow"),
            ("cdad-test-writer-odoo.md", "addons/m/models/m.py", "deny"),
        )
        for agent, probe, expected in cases:
            with self.subTest(agent=agent, probe=probe):
                got = write_verdict(self.derived[agent], probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7b): el derivado {agent} debe resolver "
                        f"{expected!r} para {probe!r} por la herramienta de "
                        f"escritura; resolvió {got!r}.")

    def test_u6_7b_derived_implementer_and_readers_keep_their_maps(
            self) -> None:
        """E2/PD-24 (U6-7b): implementer: `tests/x.py` deny y código allow
        (odoo: tests deny, models allow); architect, reviewer y scribe (y
        -odoo): toda ruta deny."""
        self.require_derived()
        cases = (
            ("cdad-implementer.md", "tests/x.py", "deny"),
            ("cdad-implementer.md", "scripts/x.py", "allow"),
            ("cdad-implementer-odoo.md", "addons/m/tests/test_m.py", "deny"),
            ("cdad-implementer-odoo.md", "addons/m/models/m.py", "allow"),
        )
        for agent, probe, expected in cases:
            with self.subTest(agent=agent, probe=probe):
                got = write_verdict(self.derived[agent], probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7b): el derivado {agent} debe resolver "
                        f"{expected!r} para {probe!r}; resolvió {got!r}.")
        for role in ("architect", "reviewer", "scribe"):
            for suffix in ("", "-odoo"):
                agent = f"cdad-{role}{suffix}.md"
                for probe in ("docs/x.md", "tests/x.py", "scripts/x.py",
                              ".cdad/tmp/x", "addons/m/models/m.py"):
                    with self.subTest(agent=agent, probe=probe):
                        got = write_verdict(self.derived[agent], probe)
                        self.assertEqual(
                            got, "deny",
                            msg=f"E2/PD-24 (U6-7b): el derivado de solo "
                                f"lectura {agent} resolvió {got!r} para "
                                f"{probe!r}; el contrato exige `deny`.")

    def test_u6_7b_derived_orchestrator_control_stays_allow(self) -> None:
        """E2/PD-24 (U6-7b) (control): el orchestrator declara
        `permission: allow`, nunca llevó la palanca; la escritura sigue
        allow y nunca `ask`. Aísla que el fixture no introduce una barrera
        espuria."""
        self.require_derived()
        text = self.derived[ORCHESTRATOR]
        for probe in ("docs/x.md", "tests/x.py", "scripts/x.py"):
            with self.subTest(probe=probe):
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"E2/PD-24 (U6-7b) (control): el orchestrator declara "
                        f"`permission: allow`; la escritura de {probe!r} "
                        f"resolvió {got!r}.")
                self.assertNotEqual(got, "ask")


class TestDerivedAgentsIgnoreInstalledWriteLeverDrift(InstalledLeverProject):
    """E2/PD-24 (U6-7b): el retiro de la palanca no rompe la deriva."""

    def test_u6_7b_second_prepare_does_not_claim_hand_edits(self) -> None:
        """E2/PD-24 (U6-7b): tras publicar los derivados desde la copia
        instalada con `write: ask`, un `prepare` siguiente termina rc=0 (no
        reclama edición a mano: el retiro de la palanca quedó registrado en
        el manifiesto) y regenera los mismos bytes."""
        self.require_derived()
        before = published_derived(self.root)
        self.assertTrue(before, msg="precondición: no hay derivados publicados")
        mark_active_packet(self.root, "completed")
        second = self.run_prepare(
            role="implementer", substage="green",
            objective="U6-7b deriva tras el retiro de la palanca",
        )
        self.assertEqual(
            second.returncode, 0,
            msg=f"E2/PD-24 (U6-7b): el `prepare` siguiente reclamó una "
                f"edición a mano sobre los derivados (rc="
                f"{second.returncode}); el retiro de `write` debe quedar "
                f"registrado en el manifiesto, no ser una divergencia. "
                f"stdout={second.stdout[:400]!r} "
                f"stderr={second.stderr[:600]!r}")
        after = published_derived(self.root)
        self.assertEqual(
            sorted(after), sorted(before),
            msg="E2/PD-24 (U6-7b): la regeneración cambió el conjunto de "
                "derivados publicados")
        self.assertEqual(
            after, before,
            msg="E2/PD-24 (U6-7b): la regeneración no es determinista para "
                "la misma copia instalada y la misma política")


if __name__ == "__main__":
    unittest.main(verbosity=2)
