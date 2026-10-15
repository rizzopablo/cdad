#!/usr/bin/env python3
"""005-004 T4 RED — decisiones del guard CC y mapa de hooks declarado una vez.

Contrato (oráculo):
- `docs/specs/005-004-claude-code-roles/spec.md` — §2 (tabla de contrato),
  §3 PD-4 (y PD-9), §4 INV-2/INV-3, §5 AC-4, §10 (VERIFY 1/2/4)  sha256 79d57e0a…
- `docs/specs/005-004-claude-code-roles/plan.md` — ficha T4 y su bloque
  `plan-tasks` (focal declarado: `tests/test_005_004_t4_cc_guard_decisions.py`;
  regresiones declaradas: `tests/validate-consistency.sh`,
  `tests/test_005_008_t1_nested_tests.py`, `tests/test_004_002_t5_runtime.py`).

El oráculo NO se deriva de la implementación: no se lee
`scripts/claude-code-path-guard.sh`, ni `sources/` ni `skills/` para
escribirlo. Se EJECUTA el guard como PROGRAMA con cargas PreToolUse
sintéticas (JSON por stdin con la forma real de cada herramienta; `cwd` y
`CLAUDE_PROJECT_DIR` = proyecto fixture propio) y se leen las superficies que
el contrato declara por su ruta: los artefactos GENERADOS
`agents/claude-code/*.md` (salida declarada del generador, `Makefile:1-6`;
mismo precedente que el focal T1 de esta feature) y —como superficies
DECLARADAS del contrato, nunca por detalle interno de función— el dueño del
mapa (`sources/agents/adapters/claude-code.md`, `scripts/cdad-generate.py`) y
el consumidor (`skills/cdad-cycle/references/claude-code-delegation.md`).

Alcance acotado (enmienda de la revisión, 2026-10-13): NO se repiten las
decisiones del guard ya cubiertas —implementer/test-writer contra
implementación y tests— de `tests/test_004_002_t5_runtime.py`
(`pd8_i10_c2_*`) y `tests/test_005_008_t1_nested_tests.py`; esos siguen siendo
las regresiones declaradas del paquete. Este focal sólo agrega: rol
desconocido, roles sin hooks, y la coincidencia del frontmatter de hooks con
el mapa declarado en su dueño (más la reconciliación del consumidor y del
`exit 2`).

Mapa test → postcondición/criterio (un test por afirmación observable):

- `test_pd4_unknown_role_fails_open`                      → PD-4 (rol
  desconocido: fail-open declarado) + AC-4
- `test_pd4_roles_without_hooks_have_no_route_barrier`    → PD-4 (roles sin
  hooks: sin barrera de ruta) + AC-4
- `test_pd4_generated_hook_frontmatter_is_coherent`       → PD-4 (el
  frontmatter de hooks generado: matcher, modo y comando) + AC-4
- `test_pd4_generated_hook_map_matches_its_owner`         → PD-4/PD-9 (esa
  declaración COINCIDE con el mapa declarado una vez en su dueño) + AC-4
- `test_pd4_consumer_references_the_guard_contract`       → PD-4/PD-9 (el
  consumidor referencia el contrato del guard y no repite globs legacy como
  mecanismo vigente) + AC-4
- `test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown`  → PD-8/§10 VERIFY 1
  (la afirmación sobre `exit 2` acotada a su alcance observado, sin contradecir
  el desconocido del modo no interactivo)

RED hoy (observado): `test_pd4_generated_hook_map_matches_its_owner` (el
dueño declarado del mapa —el adaptador fuente— no declara los pares
(matcher, modo) que los derivados llevan; hoy describe el mecanismo con los
globs legacy), `test_pd4_consumer_references_the_guard_contract` (el
consumidor describe los globs legacy como mecanismo y no referencia el
clasificador) y `test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown` (la
afirmación no está acotada) fallan por AssertionError. Los controles de
no-regresión (rol desconocido fail-open, roles sin hooks, coherencia del
frontmatter generado, y los pares de los guardados como control positivo)
quedan verdes hoy. Ningún fallo es ImportError/SyntaxError/NameError: las
superficies declaradas faltantes son aserción de contrato, no error de
entorno.

Declarado (PD-8, sin extrapolar): estos tests verifican las DECISIONES del
guard y el mapa declarado; NO afirman que Claude Code honre `exit 2` ni que
los hooks del frontmatter se apliquen a los subagentes nativos. No se habilita
ningún hook `Bash` (decisión del dueño 2026-09-29). El proyecto fixture es
propio (tempdir); HOME nunca se usa como política.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

# Arnés de fixtures y de invocación del guard (reutilizado, no reimplementado):
# proyecto sintético + política válida + carga PreToolUse sintética real.
from test_004_002_t2_bootstrap import SCRIPT as PACKET_CLI
from test_004_002_t5_runtime import CLI_ENV, LayoutProject
# Parser de frontmatter único del suite (reutilizado; no se escribe otro).
from test_opencode_read_map_and_steps import frontmatter

REPO = Path(__file__).resolve().parents[1]

# Superficies declaradas por el contrato (§3 PD-4, §9 y la ficha T4 del plan).
CC_AGENTS = REPO / "agents" / "claude-code"
ADAPTER = REPO / "sources" / "agents" / "adapters" / "claude-code.md"
GENERATOR = REPO / "scripts" / "cdad-generate.py"
CONSUMER = REPO / "skills" / "cdad-cycle" / "references" / "claude-code-delegation.md"
GUARD = REPO / "scripts" / "claude-code-path-guard.sh"

POLICY_REL = "docs/cdad-policy.json"   # política del fixture (layout CDAD)
IMPLEMENTATION_PROBE = "scripts/x.py"      # clasifica implementación (layout CDAD)
TEST_PROBE = "tests/test_a.py"             # clasifica tests (layout CDAD)

# Roles que el contrato declara SIN hooks (§3 PD-4 y la tabla de guardas
# vigente de `tests/test_packet_prepare.py:675-688`, citada por el contrato):
# read-only (architect/reviewer/scribe, base y -odoo) + el orchestrator.
ROLES_WITHOUT_HOOKS = (
    "cdad-architect",
    "cdad-architect-odoo",
    "cdad-reviewer",
    "cdad-reviewer-odoo",
    "cdad-scribe",
    "cdad-scribe-odoo",
    "cdad-orchestrator",
)

# Cargas que un modo DECLARADO bloquea (control positivo: la carga es viva).
BLOCKED_FOR_DECLARED_MODE = (
    ("test-writer-read", "Read", {"file_path": IMPLEMENTATION_PROBE}),
    ("implementer", "Edit", {"file_path": TEST_PROBE}),
)

# Roles que NO son modos declarados del mapa (el guard debe hacer fail-open).
UNKNOWN_ROLES = ("unknown-cdad-role", "cdad-no-such-role")

# Roles read-only nombrados por el contrato (no son modos del mapa).
READ_ONLY_ROLE_NAMES = ("architect", "reviewer", "scribe", "orchestrator")

TOOL_NAMES = (
    "Read", "Write", "Edit", "MultiEdit", "NotebookEdit",
    "Grep", "Glob", "Bash", "Skill",
)
TOOL_TOKEN_RE = re.compile(r"\b(" + "|".join(TOOL_NAMES) + r")\b")
MATCHER_ENTRY_RE = re.compile(r"(?m)^\s*-\s*matcher:\s*(?P<matcher>[^\n]+)$")
COMMAND_RE = re.compile(r"(?m)^\s*command:\s*(?P<command>[^\n]+)$")
MODE_IN_COMMAND_RE = re.compile(r"path-guard\.sh\s+([A-Za-z][\w-]*)")
HOOK_SECTION_RE = re.compile(r"PreToolUse|path-?guard|\bhooks?\b", re.IGNORECASE)


# ------------------------------------------------------------------- helpers


def read_declared(path: Path, why: str) -> str:
    """Lee una superficie declarada por el contrato. Su ausencia es una
    aserción de contrato (AssertionError), nunca un error de entorno."""
    assert path.is_file(), (
        f"{why}: la superficie declarada por el contrato no existe: "
        f"{path.relative_to(REPO) if path.is_absolute() else path}"
    )
    return path.read_text(encoding="utf-8")


def run_guard_in(root: Path, role: str, tool_name: str,
                 tool_input: dict) -> subprocess.CompletedProcess:
    """Ejecuta el guard CC con la forma real del JSON de hook, con el proyecto
    fixture como `cwd` y como `CLAUDE_PROJECT_DIR` (PD-4: las decisiones del
    guard se ejecutan sin una sesión CC viva)."""
    env = dict(os.environ)
    env[CLI_ENV] = str(PACKET_CLI)
    env["CLAUDE_PROJECT_DIR"] = str(root)
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run(
        ["bash", str(GUARD), role],
        input=payload, capture_output=True, text=True, cwd=str(root), env=env,
    )


def hook_entries(agent_text: str) -> list[dict]:
    """Entradas de hook del frontmatter de un agente CC declarado: por cada
    `- matcher:` su conjunto de herramientas, su(s) modo(s) del guard y su(s)
    comando(s). El modo se toma de la invocación declarada
    (`path-guard.sh <modo>`), nunca de un nombre interno."""
    fm = frontmatter(agent_text)
    starts = list(MATCHER_ENTRY_RE.finditer(fm))
    entries: list[dict] = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(fm)
        chunk = fm[match.start():end]
        matcher = match.group("matcher").strip().strip("\"'")
        tools = frozenset(TOOL_TOKEN_RE.findall(matcher)) or frozenset(
            token for token in re.split(r"[|,\s]+", matcher) if token
        )
        commands = [m.group("command").strip()
                    for m in COMMAND_RE.finditer(chunk)]
        entries.append({
            "matcher": matcher,
            "tools": tools,
            "modes": MODE_IN_COMMAND_RE.findall(chunk),
            "commands": commands,
        })
    return entries


def generated_hook_map() -> dict[str, list[dict]]:
    """Mapa de hooks de los artefactos GENERADOS: agente → entradas."""
    result: dict[str, list[dict]] = {}
    for path in sorted(CC_AGENTS.glob("cdad-*.md")):
        result[path.stem] = hook_entries(read_declared(path, "PD-4"))
    return result


def command_root(command: str) -> str:
    """Raíz que resuelve el comando del hook (lo anterior al script del guard):
    parte del mapa declarado (PD-4)."""
    return command.split("path-guard.sh", 1)[0].strip()


def declares_mode_and_matcher(text: str, tools: frozenset[str],
                              mode: str) -> str:
    """¿La superficie declara el par (matcher, modo) del derivado?

    Tolerante a la forma (tabla, lista, comentario o literal del generador):
    busca una línea con el modo y exige que su ventana (±2 líneas) nombre
    TODAS las herramientas de su matcher. Devuelve `ok`, `mode-missing` o
    `matcher-missing` para el diagnóstico del RED."""
    lines = text.splitlines()
    hits = [
        index for index, line in enumerate(lines)
        if re.search(rf"(?<![\w-]){re.escape(mode)}(?![\w-])", line)
    ]
    if not hits:
        return "mode-missing"
    for index in hits:
        window = " ".join(lines[max(0, index - 2):index + 3])
        if tools <= set(TOOL_TOKEN_RE.findall(window)):
            return "ok"
    return "matcher-missing"


def blocks(text: str) -> list[str]:
    """Bloques del documento (párrafo / ítem separados por línea en blanco)."""
    return [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]


def hook_section_blocks(consumer: str) -> list[str]:
    """Bloques del consumidor que tratan el mecanismo de hooks del guard."""
    return [block for block in blocks(consumer) if HOOK_SECTION_RE.search(block)]


# ------------------------------------------------- PD-4 — rol desconocido


class TestUnknownRole(LayoutProject):
    """PD-4: el rol desconocido hace fail-open (la carga pasa)."""

    LAYOUT = "cdad"

    def test_pd4_unknown_role_fails_open(self) -> None:
        """PD-4/AC-4: con política válida del proyecto, un rol que no es un
        modo declarado del mapa NO bloquea la carga: el guard deja pasar
        (rc 0) el mismo Read/Edit que un modo declarado sí bloquea (rc 2,
        control positivo: la carga es viva y bloqueable)."""
        self.assertTrue(
            (self.root / POLICY_REL).is_file(),
            msg=f"PD-4 (control): el fixture no tiene {POLICY_REL} — sin "
                f"clasificador el guard falla cerrado y el fail-open del rol "
                f"desconocido no sería atribuible al rol",
        )
        for role, tool_name, tool_input in BLOCKED_FOR_DECLARED_MODE:
            with self.subTest(control=role, tool=tool_name):
                control = run_guard_in(self.root, role, tool_name, tool_input)
                self.assertEqual(
                    control.returncode, 2,
                    msg=f"PD-4 (control positivo): el modo declarado {role!r} "
                        f"no bloqueó {tool_name}({tool_input}) "
                        f"(rc={control.returncode}: "
                        f"{control.stderr.strip()}) — la carga del fixture no "
                        f"es la que el contrato declara bloqueable"
                )
        for role in UNKNOWN_ROLES:
            for _declared_role, tool_name, tool_input in BLOCKED_FOR_DECLARED_MODE:
                with self.subTest(unknown_role=role, tool=tool_name):
                    proc = run_guard_in(self.root, role, tool_name, tool_input)
                    self.assertEqual(
                        proc.returncode, 0,
                        msg=f"PD-4/AC-4: el guard bloqueó "
                            f"{tool_name}({tool_input}) para el rol "
                            f"DESCONOCIDO {role!r} (rc={proc.returncode}: "
                            f"{proc.stderr.strip()}) — el contrato declara "
                            f"fail-open para un rol fuera del mapa; la misma "
                            f"carga queda bloqueada por un modo declarado"
                    )


# ---------------------------------------------------- PD-4 — roles sin hooks


class TestRolesWithoutHooks(LayoutProject):
    """PD-4: los roles sin hooks no tienen barrera de ruta."""

    LAYOUT = "cdad"

    def test_pd4_roles_without_hooks_have_no_route_barrier(self) -> None:
        """PD-4/AC-4: los roles read-only del adaptador CC y el orchestrator
        NO declaran hooks de ruta en su frontmatter generado (sin
        `PreToolUse`/`matcher`), y su carga de edición sobre una ruta de tests
        no queda bloqueada — mientras el modo declarado del implementer sí la
        bloquea (control positivo)."""
        for name in ROLES_WITHOUT_HOOKS:
            with self.subTest(agent=name):
                text = read_declared(CC_AGENTS / f"{name}.md", "PD-4")
                fm = frontmatter(text)
                offenders = [
                    line for line in fm.splitlines()
                    if re.search(r"PreToolUse|\bmatcher\b", line)
                ]
                self.assertEqual(
                    offenders, [],
                    msg=f"PD-4/AC-4: {name}.md declara hooks de ruta "
                        f"({offenders!r}) — el contrato declara ese rol SIN "
                        f"hooks (la barrera de ruta es de los roles que "
                        f"editan/leen el producto)"
                )
        control = run_guard_in(self.root, "implementer", "Edit",
                               {"file_path": TEST_PROBE})
        self.assertEqual(
            control.returncode, 2,
            msg=f"PD-4 (control positivo): el modo declarado 'implementer' no "
                f"bloqueó Edit({TEST_PROBE}) (rc={control.returncode}) — la "
                f"carga del fixture no es bloqueable"
        )
        for role in READ_ONLY_ROLE_NAMES:
            with self.subTest(read_only_role=role):
                proc = run_guard_in(self.root, role, "Edit",
                                    {"file_path": TEST_PROBE})
                self.assertEqual(
                    proc.returncode, 0,
                    msg=f"PD-4/AC-4: el guard bloqueó Edit({TEST_PROBE}) para "
                        f"{role!r} (rc={proc.returncode}: "
                        f"{proc.stderr.strip()}) — un rol sin hooks declarados "
                        f"no tiene barrera de ruta"
                )


# ------------------------------------------- PD-4 — frontmatter generado


class TestGeneratedHookFrontmatter(unittest.TestCase):
    """PD-4: el frontmatter de hooks de los agentes CC generados."""

    def test_pd4_generated_hook_frontmatter_is_coherent(self) -> None:
        """PD-4/AC-4: cada entrada de hook de los derivados generados declara
        exactamente un matcher con herramientas conocidas, exactamente un modo
        del guard y su comando; ningún matcher habilita `Bash` (decisión del
        dueño 2026-09-29) y todos los comandos resuelven UNA sola raíz (la
        raíz se declara una vez)."""
        hook_map = generated_hook_map()
        self.assertTrue(
            hook_map,
            msg=f"PD-4: no hay artefactos generados en "
                f"{CC_AGENTS.relative_to(REPO)}",
        )
        agents_with_hooks = {
            name: entries for name, entries in hook_map.items() if entries
        }
        self.assertTrue(
            agents_with_hooks,
            msg="PD-4/AC-4: ningún agente CC generado declara hooks de ruta — "
                "el mapa declarado por el contrato tiene roles con guard",
        )
        roots: set[str] = set()
        for name, entries in sorted(agents_with_hooks.items()):
            for entry in entries:
                with self.subTest(agent=name, matcher=entry["matcher"]):
                    self.assertTrue(
                        entry["tools"],
                        msg=f"PD-4: la entrada de hooks de {name} no declara "
                            f"herramientas en su matcher "
                            f"({entry['matcher']!r})",
                    )
                    unknown = sorted(
                        tool for tool in entry["tools"]
                        if tool not in TOOL_NAMES and tool != "*"
                    )
                    self.assertEqual(
                        unknown, [],
                        msg=f"PD-4: el matcher de {name} nombra herramientas "
                            f"desconocidas {unknown!r} (declara "
                            f"{entry['matcher']!r})",
                    )
                    self.assertNotIn(
                        "Bash", entry["tools"],
                        msg=f"PD-4/AC-4: el matcher de {name} habilita `Bash` "
                            f"({entry['matcher']!r}) — ningún hook `Bash` se "
                            f"habilita (decisión del dueño 2026-09-29)",
                    )
                    self.assertEqual(
                        len(entry["modes"]), 1,
                        msg=f"PD-4: la entrada de hooks de {name} declara "
                            f"{len(entry['modes'])} modos del guard "
                            f"({entry['modes']!r}) para el matcher "
                            f"{entry['matcher']!r} — el mapa declara un modo "
                            f"por entrada",
                    )
                    self.assertEqual(
                        len(entry["commands"]), 1,
                        msg=f"PD-4: la entrada de hooks de {name} declara "
                            f"{len(entry['commands'])} comandos "
                            f"({entry['commands']!r})",
                    )
                    self.assertIn(
                        f"path-guard.sh {entry['modes'][0]}",
                        entry["commands"][0],
                        msg=f"PD-4: el comando de {name} no invoca el guard "
                            f"con su modo declarado "
                            f"({entry['commands'][0]!r})",
                    )
                    roots.add(command_root(entry["commands"][0]))
        self.assertEqual(
            len(roots), 1,
            msg=f"PD-4: los comandos de hooks resuelven {len(roots)} raíces "
                f"distintas {sorted(roots)!r} — la raíz que resuelve el "
                f"comando se declara una vez en su dueño",
        )

    def test_pd4_generated_hook_map_matches_its_owner(self) -> None:
        """PD-4/PD-9: los pares (matcher, modo) que lleva cada derivado
        generado están declarados en el dueño del mapa (adaptador fuente y
        generador) — y ningún modo declarado en el dueño queda huérfano. Hoy
        el enunciado vigente describe globs legacy y no los pares que los
        derivados llevan: falla por aserción."""
        hook_map = generated_hook_map()
        owner_surfaces = (
            ("adaptador fuente", ADAPTER),
            ("generador", GENERATOR),
        )
        adapter_text = read_declared(ADAPTER, "PD-9")
        generator_text = read_declared(GENERATOR, "PD-9")
        text_by_label = {
            "adaptador fuente": adapter_text,
            "generador": generator_text,
        }

        pairs = [
            (name, entry["tools"], entry["modes"][0])
            for name, entries in sorted(hook_map.items())
            for entry in entries
        ]
        self.assertTrue(pairs, (
            "PD-9: el mapa generado está vacío — el contrato declara roles con "
            "guard (control)"
        ))
        # Diagnóstico del RED/GREEN: modos que cada superficie del dueño
        # declara en la forma de invocación del guard (`path-guard.sh <modo>`).
        invocation_modes = {
            label: sorted(set(MODE_IN_COMMAND_RE.findall(text_by_label[label])))
            for label, _path in owner_surfaces
        }
        undeclared: set[str] = set()
        for name, tools, mode in pairs:
            verdicts = {
                label: declares_mode_and_matcher(text_by_label[label],
                                                 tools, mode)
                for label, _path in owner_surfaces
            }
            undeclared.update(
                f"{label}: {name} ({sorted(tools)} → {mode!r}) [{verdict}]"
                for label, verdict in verdicts.items() if verdict != "ok"
            )
        self.assertEqual(
            sorted(undeclared), [],
            msg=f"PD-4/PD-9: el artefacto generado lleva pares (matcher, modo) "
                f"que el dueño del mapa NO declara: {sorted(undeclared)!r} "
                f"(ok = matcher y modo co-declarados; mode-missing = el modo "
                f"no se declara; matcher-missing = se declara el modo sin su "
                f"matcher) — el mapa se declara una vez en su dueño "
                f"(adaptador fuente + generador) y los consumidores lo "
                f"referencian, no describen globs legacy "
                f"(modos en forma de invocación por superficie: "
                f"{invocation_modes!r})",
        )

        declared_modes: set[str] = set()
        for label, _path in owner_surfaces:
            with self.subTest(orphans=label):
                declared_modes |= set(invocation_modes[label])
        generated_modes = {
            entry["modes"][0] for entries in hook_map.values() for entry in entries
        }
        orphans = sorted(declared_modes - generated_modes)
        self.assertEqual(
            orphans, [],
            msg=f"PD-9: el dueño del mapa declara modos que ningún derivado "
                f"generado lleva: {orphans!r} (derivados: "
                f"{sorted(generated_modes)!r})",
        )


# ------------------------------------------- PD-4/PD-9 — el consumidor


class TestConsumerReference(unittest.TestCase):
    """PD-4/PD-9: el consumidor referencia el contrato del guard."""

    def test_pd4_consumer_references_the_guard_contract(self) -> None:
        """PD-4/PD-9/AC-4: el consumidor `claude-code-delegation.md` describe
        el mecanismo del guard —no los globs legacy—, referenciando el
        clasificador de la política del proyecto, las búsquedas acotadas y el
        fail-closed sin clasificador; y no presenta `src/**`/`lib/**` como el
        mecanismo vigente (una mención histórica debe declararse como
        superada)."""
        consumer = read_declared(CONSUMER, "PD-4")
        region = hook_section_blocks(consumer)
        self.assertTrue(
            region,
            msg=f"PD-4/PD-9: {CONSUMER.relative_to(REPO)} no declara el "
                f"mecanismo de hooks del guard (ningún bloque lo trata) — el "
                f"consumidor referencia el contrato del guard",
        )
        joined = "\n\n".join(region)
        self.assertRegex(
            joined,
            r"clasificad|classifier|cdad-policy|pol[íi]tica|policy",
            msg=f"PD-4/PD-9: el bloque de hooks del consumidor no referencia "
                f"el clasificador de la política del proyecto — el guard v2 "
                f"clasifica con la política del proyecto, no con globs fijos",
        )
        self.assertRegex(
            joined,
            r"fail[ -]?clos|falla cerrad|cerrado sin clasificador|"
            r"sin clasificador|no classifier",
            msg=f"PD-4/PD-9: el bloque de hooks del consumidor no declara que "
                f"sin clasificador el guard falla cerrado (INV-3)",
        )
        self.assertRegex(
            joined,
            r"acot|scop|bounded|narrow",
            msg=f"PD-4/PD-9: el bloque de hooks del consumidor no declara que "
                f"las búsquedas (`Grep`/`Glob`) se acotan a un `path`",
        )
        legacy = re.compile(r"src/\*\*|lib/\*\*")
        superseded = re.compile(
            r"legacy|obsolet|hist[óo]ric|retirad|superseded|ya no|antigu|v1\b",
            re.IGNORECASE,
        )
        offenders = [
            block for block in region
            if legacy.search(block) and not superseded.search(block)
        ]
        self.assertEqual(
            offenders, [],
            msg=f"PD-4/PD-9/AC-4: el consumidor presenta los globs legacy "
                f"`src/**`/`lib/**` como el mecanismo vigente del guard "
                f"({offenders!r}) — el mecanismo vigente es el clasificador "
                f"de la política del proyecto, declarado en su dueño",
        )

    def test_pd4_exit2_claim_is_scoped_and_keeps_the_unknown(self) -> None:
        """PD-8/§10 VERIFY 1: la afirmación del consumidor sobre `exit 2`
        queda acotada a su alcance observado (sesión interactiva) y declara lo
        NO verificado en modo no interactivo, sin contradecir el desconocido
        conservado por PD-8 (VERIFY 1). Hoy el enunciado no lleva ese alcance:
        falla por aserción.

        El oráculo es de contenido declarado: la ventana de cada bloque que
        trata `exit 2` (el bloque y sus vecinos inmediatos) debe llevar las
        tres marcas —alcance interactivo, modo no interactivo y desconocido
        declarado— y ninguna afirmación de que el runtime honra/confía en
        `exit 2` puede quedar fuera de ese alcance."""
        consumer = read_declared(CONSUMER, "PD-8")
        doc_blocks = blocks(consumer)
        exit2_indexes = [
            index for index, block in enumerate(doc_blocks)
            if re.search(r"exit\s*(code\s*)?2", block)
        ]
        self.assertTrue(
            exit2_indexes,
            msg=f"PD-8/§10 (VERIFY 1): {CONSUMER.relative_to(REPO)} ya no "
                f"declara el `exit 2` del guard — la afirmación que el "
                f"contrato manda acotar no está tratada",
        )

        def window(index: int) -> str:
            return "\n\n".join(doc_blocks[max(0, index - 1):index + 2])

        def head(index: int) -> str:
            return doc_blocks[index].splitlines()[0][:60]

        interactive = r"interactiv"
        non_interactive = (
            r"no[ -]?interactiv|non-interactiv|-p\b|print mode|headless"
        )
        unknown = (
            r"unknown|desconocid|no verificad|sin verificar|"
            r"not verified|no observad"
        )
        marks = (("alcance interactivo", interactive),
                 ("modo no interactivo", non_interactive),
                 ("desconocido declarado", unknown))

        scoped = [
            index for index in exit2_indexes
            if all(re.search(pattern, window(index), re.IGNORECASE)
                   for _label, pattern in marks)
        ]
        self.assertTrue(
            scoped,
            msg=f"PD-8/§10 (VERIFY 1): el tratamiento del `exit 2` en "
                f"{CONSUMER.relative_to(REPO)} no está acotado: ninguna "
                f"ventana declara a la vez el alcance observado (sesión "
                f"interactiva), el modo no interactivo (`-p`) y el "
                f"desconocido conservado con causa — el primer bloque con "
                f"`exit 2` es {head(exit2_indexes[0])!r}",
        )

        honoring = re.compile(
            r"honor|honour|trust|confiar|conf[íi]a|respet|respect|rely on|"
            r"verified|verific|empiric",
            re.IGNORECASE,
        )
        claims = [
            index for index in exit2_indexes if honoring.search(doc_blocks[index])
        ]
        for index in claims:
            for label, pattern in marks:
                with self.subTest(claim=head(index), mark=label):
                    self.assertRegex(
                        window(index),
                        pattern,
                        msg=f"PD-8/§10 (VERIFY 1): la afirmación sobre `exit 2` "
                            f"({head(index)!r}) no declara {label} — la "
                            f"afirmación queda acotada al alcance observado y "
                            f"conserva el desconocido del modo no interactivo",
                    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
