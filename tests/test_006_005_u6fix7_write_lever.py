#!/usr/bin/env python3
"""006-005 U6-7 RED — la palanca `write` no anula el mapa `edit` (E2/PD-24).

Contract: `docs/specs/006-005-native-path-parity/spec.md` §2.9, §3 (E2,
PD-24), §4 (INV-3, INV-7, INV-16). Origen del hallazgo: `execution.md`
§«Re-recorrido …» — E1b y **U6-7**, con las sondas reales P1/P2/P3 contra
OpenCode v2.0.27.

HECHO DE CONTRATO MEDIDO (v2.0.27, execution.md U6-7)
-----------------------------------------------------
La herramienta de **escritura** evalúa la clave `write` del bloque
`permission` **junto con** `edit`, y gana la **última regla que coincide**
(findLast, la misma regla ya documentada en los tests de derivados). Una
entrada `write: ask` **posterior** al mapa `edit` vuelve `ask` *toda*
escritura:

  - con `--auto` se aprueba todo, incluidas las rutas que `edit` **niega**
    (sonda P1: un test-writer escribió `docs/…`, fuera de su mapa);
  - en una corrida no interactiva se rechaza todo, incluidas las que `edit`
    **permite** (E1b: `permission.rejected` incluso en `tests/**`);
  - sin esa entrada, `edit` rige: `docs/…` «Permission denied: edit» y
    `tests/…` escrito (sonda P2), y la vía nativa escribe el auxiliar y su
    test (sonda P3).

Superficie observable bajo prueba (artefactos, nunca implementación)
--------------------------------------------------------------------
  - `scripts/cdad-generate.py --runtime opencode --stack odoo --out D`
    invocado como proceso (como `test_cdad_generate.py`) →
    `D/agents/opencode/cdad-*.md`.
  - `scripts/cdad_packet.py prepare` en un proyecto descartable (como
    `test_004_002_t5_runtime.py` y `test_006_005_u3b_*`) →
    `.opencode/agents/cdad-*.md`.

El bloque `permission` se evalúa con la regla del runtime: para la escritura
cuentan `edit` **y** `write`, en orden de archivo, con el `evaluate` findLast
EXISTENTE (`tests/test_opencode_read_map_and_steps.py`, reutilizado por
import). El único parseo nuevo es el que conserva la posición relativa de las
dos claves y admite el verbo `ask` — ninguna semántica de evaluación se
reimplementa.

Mapa test → postcondición (docstrings «E2/PD-24 (U6-7)»)
--------------------------------------------------------
  TestGeneratedAgentsWriteLever
    test_u6_7_every_generated_agent_keeps_its_edit_verdict
        -> E2/PD-24 (U6-7): para CADA rol (architect, test-writer,
           implementer, reviewer, scribe) y su variante -odoo, y para el
           orchestrator, el veredicto efectivo de escritura coincide con el
           del mapa `edit` del rol. Ninguna clave posterior lo anula.
    test_u6_7_no_generated_agent_resolves_write_to_ask
        -> E2/PD-24 (U6-7): ninguna ruta de ningún agente generado resuelve
           `ask` (la anulación que las sondas P1/E1b midieron).
  TestGeneratedRoleBarriers
    test_u6_7_generated_test_writer_keeps_its_route_barriers
        -> test-writer: `tests/x.py` allow; `docs/x.md` deny (y -odoo).
    test_u6_7_generated_implementer_keeps_its_route_barriers
        -> implementer: `tests/x.py` deny; código allow (y -odoo).
    test_u6_7_generated_read_only_roles_deny_every_route
        -> architect/reviewer/scribe: toda ruta deny (y -odoo).
    test_u6_7_generated_orchestrator_permission_allow_is_preserved
        -> orchestrator (`permission: allow`): escritura allow, nunca `ask`.
  TestDerivedAgentsWriteLever
    test_u6_7_every_derived_agent_keeps_its_edit_verdict
        -> E2/PD-24 (U6-7): los derivados que publica `prepare` conservan su
           mapa también para la herramienta de escritura.
    test_u6_7_derived_test_writer_keeps_temporary_and_tests_writable
        -> PD-24: tests y `.cdad/tmp` (temporal declarado) allow; docs deny.
    test_u6_7_derived_implementer_and_readers_keep_their_maps
        -> implementer: código allow / tests deny; lectores: toda ruta deny.
  TestDerivedTemporaryRootKeepsBarriers
    test_u6_7_derived_temporary_root_keeps_policy_derived_and_private_denied
        -> PD-24/INV-16: el allow del temporal no abre la política, los
           derivados ni las rutas privadas.

A-1 — test reemplazado en este RED
----------------------------------
`tests/test_role_packet_consumers.py`
`test_p3_critical_opencode_permissions_survive_consumer_migration` fijaba la
**presencia** de `write: ask` (palanca cdad-010 P1). Se reformula, declarando
el reemplazo y la razón: la WATCH RULE que la propia palanca declaraba
(«if a future OpenCode version evaluates `write` at runtime, this lever
starts generating prompts — revisit on migration») **se cumplió** en v2.0.27,
así que la palanca se retira del generador. La búsqueda en `tests/` por
«write: ask» y «cdad-010» encontró sólo ese test (la mención de
`pd10_permission_semantics.py:72` es un docstring sobre `edit: deny`, no fija
la palanca).

Estado RED: hoy todos los agentes generados y sus derivados llevan
`write: ask` después del mapa `edit`, así que la herramienta de escritura
resuelve `ask` para cualquier ruta y las aserciones de veredicto fallan por
aserción de comportamiento ausente (no por ImportError ni por fixture).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.agent_frontmatter import permissions as v2_permissions

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
    policy_doc,
    derived_dir,
)
from test_opencode_read_map_and_steps import (  # noqa: E402
    evaluate,
    frontmatter,
)
from pd10_permission_semantics import perm_map  # noqa: E402

GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"

ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
GENERATED_AGENTS = tuple(
    [f"cdad-{role}.md" for role in ROLES]
    + [f"cdad-{role}-odoo.md" for role in ROLES]
    + ["cdad-orchestrator.md"]
)

# Ancla de la barrera "privados" del fixture: ficticia, propia de este test.
# Nunca se lee `tests/.sensitive-patterns.local` (packet `private_paths`).
FIXTURE_PRIVATE_PATH = "tests/.sensitive-patterns.fixture.local"

# Rutas de sondeo comunes. Se evalúan contra el mapa del rol: lo que importa
# es que la escritura resuelva EXACTAMENTE lo que el mapa `edit` resuelve.
PROBES = (
    "tests/x.py",
    "tests/test_x.py",
    "docs/x.md",
    "docs/cdad-policy.json",
    "scripts/x.py",
    "src/app.py",
    "README.md",
    "install.sh",
    ".cdad/tmp/x",
    ".opencode/agents/cdad-test-writer.md",
    "addons/m/models/m.py",
    "addons/m/tests/test_m.py",
)

# --- evaluación de la escritura con la regla del runtime ---------------------

# `  edit: deny` / `  write: ask` (escalar inline) y `  edit:` (apertura de
# bloque). El verbo `ask` sólo aparece en `write`; se admite para modelar el
# hecho medido, no como permiso válido del mapa `edit`.
KEY_LINE_RE = r"^  (edit|write):(?:[ \t]+(allow|deny|ask))?[ \t]*$"
RULE_RE_ANY = r'"([^"]*)"\s*:\s*(allow|deny|ask)'
BARE_VERB_RE = r"^\s+(allow|deny|ask)\s*$"


def write_rule_list(agent_text: str) -> list[tuple[str, str]]:
    """Reglas que el runtime evalúa para la HERRAMIENTA DE ESCRITURA.

    Devuelve `[(patrón, verbo)]` en el ORDEN DEL ARCHIVO: las claves `edit` y
    `write` del bloque `permission` cuentan para la escritura y la última
    regla que coincide gana (findLast). Por eso no se concatenan por clave:
    la posición relativa (p. ej. un `write: ask` posterior al mapa) es
    justamente lo que el hallazgo U6-7 mide.

    Formas serializadas soportadas, todas presentes en los artefactos:
      1. `permission: allow` escalar (orchestrator) -> allow para todo;
      2. clave escalar — `edit: deny` / `write: ask` -> regla catch-all;
      3. clave de bloque — líneas `"patrón": verbo` más indentadas;
      4. bloque escalar — `edit:` + `    deny`.
    """
    entries = v2_permissions(agent_text)
    if entries:
        return [(entry["resource"], entry["effect"])
                for entry in entries if entry.get("action") in {"edit", "write"}]
    fm = frontmatter(agent_text)
    lines = fm.splitlines()

    # 1. `permission: allow` escalar: el bloque no restringe nada.
    if any(re.fullmatch(r"permission:[ \t]+allow[ \t]*", line)
           for line in lines):
        return [("*", "allow")]

    rules: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        match = re.fullmatch(KEY_LINE_RE, line)
        if not match:
            continue
        key, scalar = match.group(1), match.group(2)
        if scalar is not None:  # 2. clave escalar
            rules.append((index, "*", scalar))
            continue
        # 3./4. bloque: líneas más indentadas hasta la próxima clave de 2.
        for nested_index in range(index + 1, len(lines)):
            nested = lines[nested_index]
            if not nested.startswith("    "):
                break
            rule = re.search(RULE_RE_ANY, nested)
            if rule:
                rules.append((nested_index, rule.group(1), rule.group(2)))
                continue
            bare = re.fullmatch(BARE_VERB_RE, nested)
            if bare:
                rules.append((nested_index, "*", bare.group(1)))

    rules.sort(key=lambda item: item[0])
    return [(pattern, verb) for _index, pattern, verb in rules]


def edit_verdict(agent_text: str, probe: str) -> str:
    """Veredicto del mapa `edit` SOLO, con el evaluador findLast existente."""
    return evaluate(perm_map(agent_text, "edit"), probe)


def write_verdict(agent_text: str, probe: str) -> str:
    """Veredicto EFECTIVO de la herramienta de escritura (`edit` + `write`)."""
    return evaluate(write_rule_list(agent_text), probe)


# --- fixtures ---------------------------------------------------------------


def run_generator(out_dir: Path) -> subprocess.CompletedProcess[str]:
    """`cdad-generate.py` como proceso (mismo patrón que test_cdad_generate)."""
    return subprocess.run(
        [sys.executable, str(GENERATOR),
         "--runtime", "opencode", "--stack", "odoo", "--out", str(out_dir)],
        cwd=str(REPO_ROOT), text=True, capture_output=True, check=False,
    )


def materialize_layout(root: Path) -> None:
    for rel in LAYOUT_FILES["cdad"]:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# fixture {rel}\n", encoding="utf-8")


class GeneratedAgentsCase(unittest.TestCase):
    """Genera los agentes OpenCode una vez por clase (proceso, sin leer impl)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u67-gen-")
        cls.addClassCleanup(lambda: subprocess.run(
            ["rm", "-rf", cls._tmp], check=False))
        out_dir = Path(cls._tmp) / "out"
        cls.generated = run_generator(out_dir)
        cls.agents: dict[str, str] = {}
        agents_dir = out_dir / "agents" / "opencode"
        if agents_dir.is_dir():
            cls.agents = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(agents_dir.glob("cdad-*.md"))
            }

    def require_generated(self) -> None:
        self.assertEqual(
            self.generated.returncode, 0,
            msg=f"E2/PD-24 (U6-7) (precondición): el generador debe correr; "
                f"rc={self.generated.returncode} "
                f"stderr={self.generated.stderr[:600]!r}")
        self.assertEqual(
            sorted(self.agents), sorted(GENERATED_AGENTS),
            msg=f"E2/PD-24 (U6-7) (precondición): la salida OpenCode debe "
                f"traer todos los roles y variantes; faltan "
                f"{sorted(set(GENERATED_AGENTS) - set(self.agents))}")

    def assert_write_matches_edit(self, agent: str, text: str,
                                  probes: tuple[str, ...]) -> None:
        for probe in probes:
            with self.subTest(agent=agent, probe=probe):
                expected = edit_verdict(text, probe)
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): la herramienta de escritura de "
                        f"{agent} resolvió {got!r} para {probe!r}; el mapa "
                        f"`edit` del rol resuelve {expected!r}. En OpenCode "
                        f"v2.0.27 las claves `edit` y `write` cuentan juntas "
                        f"y gana la última regla que coincide: ninguna clave "
                        f"posterior puede anular el mapa.")
                self.assertNotEqual(
                    got, "ask",
                    msg=f"E2/PD-24 (U6-7): {agent} dejó {probe!r} en `ask`; "
                        f"la palanca `write: ask` no puede anular el mapa "
                        f"`edit` (con `--auto` se aprueba lo denegado y sin "
                        f"interacción se rechaza lo permitido).")


# --------------------------------------------------- agentes generados


class TestGeneratedAgentsWriteLever(GeneratedAgentsCase):
    """E2/PD-24 (U6-7): el `write` no anula el `edit` en NINGÚN agente."""

    def test_u6_7_every_generated_agent_keeps_its_edit_verdict(self) -> None:
        """E2/PD-24 (U6-7): para cada rol y variante -odoo (y el
        orchestrator), el veredicto efectivo de escritura coincide con el del
        mapa `edit` del rol para todas las rutas de sondeo."""
        self.require_generated()
        for agent in GENERATED_AGENTS:
            with self.subTest(agent=agent):
                self.assert_write_matches_edit(agent, self.agents[agent],
                                               PROBES)

    def test_u6_7_no_generated_agent_resolves_write_to_ask(self) -> None:
        """E2/PD-24 (U6-7): ninguna ruta de ningún agente generado resuelve
        `ask` — la anulación que midieron las sondas P1 (externa, escribió
        fuera de alcance) y E1b (nativa, rechazó todo)."""
        self.require_generated()
        for agent in GENERATED_AGENTS:
            for probe in PROBES:
                with self.subTest(agent=agent, probe=probe):
                    got = write_verdict(self.agents[agent], probe)
                    self.assertNotEqual(
                        got, "ask",
                        msg=f"E2/PD-24 (U6-7): {agent} resolvió `ask` para "
                            f"{probe!r}; la herramienta de escritura debe "
                            f"regirse por el mapa `edit` del rol.")


class TestGeneratedRoleBarriers(GeneratedAgentsCase):
    """E2/PD-24 (U6-7): los casos concretos de cada rol, vía escritura."""

    def test_u6_7_generated_test_writer_keeps_its_route_barriers(self) -> None:
        """E2/PD-24 (U6-7): test-writer => `tests/x.py` allow, `docs/x.md`
        deny (y su variante -odoo sobre addons/)."""
        self.require_generated()
        cases = (
            ("cdad-test-writer.md", "tests/x.py", "allow"),
            ("cdad-test-writer.md", "docs/x.md", "deny"),
            ("cdad-test-writer-odoo.md", "addons/m/tests/test_m.py", "allow"),
            ("cdad-test-writer-odoo.md", "addons/m/models/m.py", "deny"),
        )
        for agent, probe, expected in cases:
            with self.subTest(agent=agent, probe=probe):
                got = write_verdict(self.agents[agent], probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): {agent} debe resolver "
                        f"{expected!r} para {probe!r}; resolvió {got!r}.")

    def test_u6_7_generated_implementer_keeps_its_route_barriers(self) -> None:
        """E2/PD-24 (U6-7): implementer => `tests/x.py` deny, código allow
        (y su variante -odoo: tests deny, models/views allow)."""
        self.require_generated()
        cases = (
            ("cdad-implementer.md", "tests/x.py", "deny"),
            ("cdad-implementer.md", "scripts/x.py", "allow"),
            ("cdad-implementer-odoo.md", "addons/m/tests/test_m.py", "deny"),
            ("cdad-implementer-odoo.md", "addons/m/models/m.py", "allow"),
        )
        for agent, probe, expected in cases:
            with self.subTest(agent=agent, probe=probe):
                got = write_verdict(self.agents[agent], probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): {agent} debe resolver "
                        f"{expected!r} para {probe!r}; resolvió {got!r}.")

    def test_u6_7_generated_read_only_roles_deny_every_route(self) -> None:
        """E2/PD-24 (U6-7): architect, reviewer y scribe (y -odoo) no
        escriben ninguna ruta — los tres roles de solo lectura."""
        self.require_generated()
        read_only = tuple(
            f"cdad-{role}{suffix}.md"
            for role in ("architect", "reviewer", "scribe")
            for suffix in ("", "-odoo")
        )
        for agent in read_only:
            for probe in ("docs/x.md", "tests/x.py", "scripts/x.py",
                          "addons/m/models/m.py"):
                with self.subTest(agent=agent, probe=probe):
                    got = write_verdict(self.agents[agent], probe)
                    self.assertEqual(
                        got, "deny",
                        msg=f"E2/PD-24 (U6-7): el rol de solo lectura "
                            f"{agent} resolvió {got!r} para {probe!r}; el "
                            f"contrato exige `deny` (el `write: ask` de la "
                            f"palanca lo convertía en `ask` y con `--auto` "
                            f"en escritura).")

    def test_u6_7_generated_orchestrator_permission_allow_is_preserved(
            self) -> None:
        """E2/PD-24 (U6-7): el orchestrator declara `permission: allow`; la
        escritura sigue siendo `allow` y nunca `ask` (control: no lleva la
        palanca, y el parser no inventa una barrera)."""
        self.require_generated()
        text = self.agents["cdad-orchestrator.md"]
        for probe in ("docs/x.md", "tests/x.py", "scripts/x.py"):
            with self.subTest(probe=probe):
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"E2/PD-24 (U6-7): el orchestrator declara "
                        f"`permission: allow`; la escritura de {probe!r} "
                        f"resolvió {got!r}.")
                self.assertEqual(got, edit_verdict(text, probe),
                                 msg="E2/PD-24 (U6-7): sin mapa `edit`, el "
                                     "default findLast es allow.")


# --------------------------------------------------- agentes derivados


class DerivedProjectCase(unittest.TestCase):
    """Proyecto descartable con layout CDAD; `prepare` publica los derivados."""

    PRIVATE_PATHS: tuple[str, ...] | None = None

    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="cdad-006-005-u67-derived-")
        self.addCleanup(lambda: subprocess.run(
            ["rm", "-rf", self._tmp], check=False))
        self.root = Path(self._tmp) / "proj"
        build_project(self.root)
        materialize_layout(self.root)
        doc = policy_doc("cdad")
        if self.PRIVATE_PATHS is not None:
            doc["path_policy"]["private_paths"] = list(self.PRIVATE_PATHS)
        (self.root / POLICY_FILE).write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        # Fuente I9: copia temporal de los agentes generados del repo,
        # copiada sin inspección (salida declarada del generador).
        self.agents_src = Path(self._tmp) / "agents-src"
        self.agents_src.mkdir()
        for source in sorted((REPO_ROOT / "agents").glob("cdad-*.md")):
            shutil.copy2(source, self.agents_src / source.name)
        env = dict(os.environ)
        env[AGENTS_ENV] = str(self.agents_src)
        self.prepare = subprocess.run(
            [sys.executable, str(SCRIPT),
             *prepare_args(self.root, role="test-writer", substage="red",
                           objective="U6-7 write lever")],
            capture_output=True, text=True, cwd=str(REPO_ROOT), env=env,
        )
        self.derived: dict[str, str] = {}
        base = derived_dir(self.root)
        if base.is_dir():
            self.derived = {
                path.name: path.read_text(encoding="utf-8")
                for path in sorted(base.glob("cdad-*.md"))
            }

    def require_derived(self) -> None:
        self.assertEqual(
            self.prepare.returncode, 0,
            msg=f"E2/PD-24 (U6-7) (precondición): `prepare` debe publicar los "
                f"derivados; rc={self.prepare.returncode} "
                f"stdout={self.prepare.stdout[:400]!r} "
                f"stderr={self.prepare.stderr[:600]!r}")
        self.assertEqual(
            sorted(self.derived), sorted(GENERATED_AGENTS),
            msg=f"E2/PD-24 (U6-7) (precondición): faltan derivados en "
                f"{DERIVED_DIR}/: "
                f"{sorted(set(GENERATED_AGENTS) - set(self.derived))}")

    def assert_write_matches_edit(self, agent: str, text: str,
                                  probes: tuple[str, ...]) -> None:
        for probe in probes:
            with self.subTest(agent=agent, probe=probe):
                expected = edit_verdict(text, probe)
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): el derivado {agent} resolvió "
                        f"{got!r} para {probe!r}; su mapa `edit` resuelve "
                        f"{expected!r}. Con `write` evaluado junto a `edit` "
                        f"(findLast), ninguna clave posterior puede anular "
                        f"el mapa del derivado.")
                self.assertNotEqual(
                    got, "ask",
                    msg=f"E2/PD-24 (U6-7): el derivado {agent} dejó "
                        f"{probe!r} en `ask`.")


class TestDerivedAgentsWriteLever(DerivedProjectCase):
    """E2/PD-24 (U6-7): los derivados conservan su mapa para la escritura."""

    def test_u6_7_every_derived_agent_keeps_its_edit_verdict(self) -> None:
        """E2/PD-24 (U6-7): para cada derivado publicado por `prepare`, el
        veredicto efectivo de escritura coincide con su mapa `edit`."""
        self.require_derived()
        for agent in GENERATED_AGENTS:
            with self.subTest(agent=agent):
                self.assert_write_matches_edit(agent, self.derived[agent],
                                               PROBES)

    def test_u6_7_derived_test_writer_keeps_temporary_and_tests_writable(
            self) -> None:
        """E2/PD-24 (U6-7): el derivado test-writer conserva `tests/x.py`
        allow, `.cdad/tmp/x` allow (temporal declarado por la política) y
        `docs/x.md` deny, también para la herramienta de escritura."""
        self.require_derived()
        text = self.derived["cdad-test-writer.md"]
        cases = (
            ("tests/x.py", "allow"),
            (".cdad/tmp/x", "allow"),
            ("docs/x.md", "deny"),
            ("scripts/x.py", "deny"),
        )
        for probe, expected in cases:
            with self.subTest(probe=probe):
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): el derivado test-writer debe "
                        f"resolver {expected!r} para {probe!r}; resolvió "
                        f"{got!r}. El temporal declarado tiene que ser "
                        f"escribible de verdad (E2) y el resto del mapa "
                        f"conservarse.")

    def test_u6_7_derived_implementer_and_readers_keep_their_maps(self) -> None:
        """E2/PD-24 (U6-7): implementer => código allow / tests deny;
        architect, reviewer y scribe => toda ruta deny."""
        self.require_derived()
        cases = (
            ("cdad-implementer.md", "scripts/x.py", "allow"),
            ("cdad-implementer.md", "tests/x.py", "deny"),
            ("cdad-implementer-odoo.md", "addons/m/models/m.py", "allow"),
            ("cdad-implementer-odoo.md", "addons/m/tests/test_m.py", "deny"),
        )
        for agent, probe, expected in cases:
            with self.subTest(agent=agent, probe=probe):
                got = write_verdict(self.derived[agent], probe)
                self.assertEqual(
                    got, expected,
                    msg=f"E2/PD-24 (U6-7): el derivado {agent} debe resolver "
                        f"{expected!r} para {probe!r}; resolvió {got!r}.")
        for role in ("architect", "reviewer", "scribe"):
            for suffix in ("", "-odoo"):
                agent = f"cdad-{role}{suffix}.md"
                for probe in ("docs/x.md", "tests/x.py", "scripts/x.py"):
                    with self.subTest(agent=agent, probe=probe):
                        got = write_verdict(self.derived[agent], probe)
                        self.assertEqual(
                            got, "deny",
                            msg=f"E2/PD-24 (U6-7): el derivado de solo "
                                f"lectura {agent} resolvió {got!r} para "
                                f"{probe!r}; exige `deny`.")


class TestDerivedTemporaryRootKeepsBarriers(DerivedProjectCase):
    """PD-24/INV-16: el temporal no abre la política, derivados ni privados."""

    # Ruta privada FICTICIA del fixture (no se lee
    # `tests/.sensitive-patterns.local`): la política del fixture la declara
    # fuera de las regiones de producto y convive con la raíz temporal.
    PRIVATE_PATHS = (FIXTURE_PRIVATE_PATH,)

    def test_u6_7_derived_temporary_root_keeps_policy_derived_and_private_denied(
            self) -> None:
        """PD-24/INV-16 (U6-7): con el temporal declarado, el derivado
        test-writer sigue permitiendo el temporal y su scope de tests, y
        mantiene `deny` para la política, los derivados y las rutas privadas
        —también en el veredicto efectivo de escritura."""
        self.require_derived()
        text = self.derived["cdad-test-writer.md"]
        allow_cases = (
            (".cdad/tmp/aux.py", "el temporal declarado por la política"),
            ("tests/test_u67_fixture.py", "el scope de tests del rol"),
        )
        deny_cases = (
            ("docs/cdad-policy.json", "la política es dato del dueño (INV-7)"),
            (".opencode/agents/cdad-test-writer.md",
             "los derivados no son editables por el rol"),
            ("scripts/x.py", "producto: implementación de la política"),
            (FIXTURE_PRIVATE_PATH,
             "ruta privada declarada por la política del fixture"),
        )
        for probe, why in allow_cases:
            with self.subTest(probe=probe, expected="allow"):
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, "allow",
                    msg=f"PD-24 (U6-7): {why}: la escritura de {probe!r} "
                        f"resolvió {got!r}.")
        for probe, why in deny_cases:
            with self.subTest(probe=probe, expected="deny"):
                got = write_verdict(text, probe)
                self.assertEqual(
                    got, "deny",
                    msg=f"PD-24 (U6-7)/INV-16: {why}: la escritura de "
                        f"{probe!r} resolvió {got!r}; exige `deny`.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
