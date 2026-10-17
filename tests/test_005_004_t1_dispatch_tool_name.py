#!/usr/bin/env python3
"""005-004 T1 RED — la herramienta de despacho real de Claude Code (PD-1, AC-1).

Contrato (oráculo):
- `docs/specs/005-004-claude-code-roles/spec.md` — §2 (tabla de contrato),
  §3 PD-1 (i)-(iv), §4 INV-2/INV-4, §5 AC-1 (sha256 79d57e0a…).
- `docs/specs/005-004-claude-code-roles/plan.md` — ficha T1 y su bloque
  `plan-tasks` (focal declarado: `tests/test_005_004_t1_dispatch_tool_name.py`).

El oráculo NO se deriva de la implementación: no se leen `scripts/`,
`sources/` ni `skills/` para escribirlo. Se leen los artefactos GENERADOS
(`agents/claude-code/**`), que el contrato declara salida del generador
(`Makefile:1-6`), y las superficies que PD-1(iii) nombra por su ruta. Las
aserciones usan los nombres y las superficies que el contrato fija, no
frases del prompt ni detalles internos (middleware, funciones, mocks).

Mapa test → postcondición/criterio (un test por afirmación observable):

- `test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool` → PD-1(i) / AC-1
- `test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool`  → PD-1(ii) / AC-1
- `test_pd1_ii_opencode_side_keeps_its_tool_name`           → PD-1 / AC-1 (control de no-regresión)
- `test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name`     → PD-1(iii) / AC-1
- `test_pd1_iii_reference_and_owners_name_the_same_tool`    → PD-1(iii) / AC-1
  (reformulado en el RED de 006-002 U2: el tercer dueño del nombre ya no es
  `SKILL.md`, que queda abstracto por 006-002 PD-1/PD-3; el dueño es el
  orquestador derivado — enmienda A-1, cobertura conservada)
- `test_pd1_iv_generator_staging_is_idempotent`             → PD-1(iv) / INV-4
- `test_pd1_iv_ten_cc_agents_keep_their_tools_lines`        → PD-1(iv) / INV-4
  (control de no-regresión)

RED esperado: `test_pd1_i_*`, `test_pd1_ii_no_cc_*` y `test_pd1_iii_adapter_*`
fallan por AssertionError porque hoy el derivado
`agents/claude-code/cdad-orchestrator.md` declara `Task` (spec PD-1, plan T1);
los tres controles (`opencode` conserva su nombre, idempotencia del generador y
las líneas `tools:` de los diez agentes con/sin guard) quedan verdes hoy.
Ningún fallo es ImportError/SyntaxError/NameError.

Superposición declarada con 006-002 U2 (PD-1/PD-3): la aserción de coherencia
del nombre exige `Agent` en el reference, el adaptador y el derivado, y exige
que `SKILL.md` NO lo nombre como herramienta — esa mitad es la que el GREEN de
006-002 U2 satisface al neutralizar §4.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Tabla congelada "como hoy" de las líneas `tools:` de los diez agentes CC
# con/sin guard: se reusa la de `tests/test_packet_prepare.py:675-688` (el
# contrato la cita como la fijación vigente) en vez de duplicarla (PD-9).
from tests.test_packet_prepare import (
    EDIT_TOOLS,
    EXPECTED_GUARDS,
    READ_ONLY_TOOLS,
)

REPO = Path(__file__).resolve().parents[1]

# Superficies declaradas por PD-1 (§3, §9) y por la ficha T1 del plan.
CC_AGENTS = REPO / "agents" / "claude-code"
CC_ORCHESTRATOR = CC_AGENTS / "cdad-orchestrator.md"
ADAPTER = REPO / "sources" / "agents" / "adapters" / "claude-code.md"
CC_REF = REPO / "skills" / "cdad-cycle" / "references" / "claude-code-delegation.md"
SKILL = REPO / "skills" / "cdad-cycle" / "SKILL.md"
OC_REF = REPO / "skills" / "cdad-cycle" / "references" / "opencode-delegation.md"
GENERATOR = REPO / "scripts" / "cdad-generate.py"

# Parámetros con los que el repo genera `agents/claude-code/**`
# (precedente: `tests/test_cdad_generate.py`; `Makefile` `PROFILE ?= optimus`).
GENERATOR_RUNTIME = "claude-code"
GENERATOR_STACK = "odoo"
GENERATOR_PROFILE = "optimus"

# La herramienta de despacho que el contrato fija para Claude Code (la
# observada en ejecuciones reales) y la que el lado OpenCode conserva.
CC_DISPATCH_TOOL = "Agent"
OC_DISPATCH_TOOL = "Task"


# ------------------------------------------------------------------ helpers


def read(path: Path, why: str) -> str:
    """Lee una superficie declarada por el contrato; si falta, es una
    aserción de contrato (AssertionError), nunca un ImportError."""
    assert path.is_file(), (
        f"{why}: la superficie declarada por el contrato no existe: "
        f"{path.relative_to(REPO) if path.is_absolute() else path}"
    )
    return path.read_text(encoding="utf-8")


def tools_from_block(block: str) -> set[str]:
    """Herramientas declaradas en un bloque con líneas `tools:`.

    Una entrada por coma y se toma la palabra inicial de cada entrada
    (`Task for orchestrator` → `Task`): el oráculo nombra la herramienta, no
    la glosa que la acompaña.
    """
    tools: set[str] = set()
    for line in block.splitlines():
        match = re.match(r"\s*tools:\s*(.+?)\s*$", line)
        if not match:
            continue
        for entry in match.group(1).split(","):
            word = re.match(r"[`*]*([A-Za-z_][A-Za-z0-9_]*)", entry.strip())
            if word:
                tools.add(word.group(1))
    return tools


def frontmatter_tools(text: str) -> set[str]:
    """Herramientas del frontmatter del agente generado (su única declaración
    `tools:`; el cuerpo del documento no cuenta)."""
    parts = text.split("---", 2)
    assert len(parts) == 3, (
        "PD-1: el agente generado no tiene frontmatter delimitado por `---`"
    )
    return tools_from_block(parts[1])


def names_task_as_a_cc_tool(text: str) -> bool:
    """¿El documento nombra `Task` como herramienta de Claude Code, en
    cualquiera de sus formas (`Task`, `` `Task` ``, `Task for orchestrator`,
    `Task,`)? Las líneas que explican el lado OpenCode —que conserva ese
    nombre (PD-1)— no cuentan. La pregunta es de contenido declarado, no de
    forma: el contrato enuncia el nombre de la herramienta, no su plantilla.
    """
    for line in text.splitlines():
        if re.search(r"opencode", line, re.IGNORECASE):
            continue
        if re.search(rf"\b{OC_DISPATCH_TOOL}\b", line):
            return True
    return False


def names_the_cc_tool_form(text: str) -> bool:
    """¿El documento nombra la herramienta de despacho de Claude Code en alguna
    de sus FORMAS de herramienta (``Agent`` en code-span, «Agent tool»,
    ``Agent`` asociada a ``subagent_type``)? La palabra suelta *Agent* en otra
    acepción no cuenta (el oráculo apunta a formas, no a prosa).
    """
    return bool(
        re.search(r"`\s*Agent\s*`", text)
        or re.search(r"Agent\s+tool", text)
        or re.search(r"Agent[^\n]{0,60}subagent_type", text)
    )


def run_generator(out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--runtime",
            GENERATOR_RUNTIME,
            "--stack",
            GENERATOR_STACK,
            "--profile",
            GENERATOR_PROFILE,
            "--out",
            str(out),
        ],
        cwd=str(REPO),
        text=True,
        capture_output=True,
        check=False,
    )


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


# ------------------------------------------------- PD-1(i) — el derivado CC


def test_pd1_i_cc_orchestrator_declares_agent_dispatch_tool():
    """PD-1(i)/AC-1: el derivado `agents/claude-code/cdad-orchestrator.md`
    declara como herramienta de despacho de subagentes la real observada
    (`Agent`, con `subagent_type: cdad-<role>`), no `Task`."""
    text = read(CC_ORCHESTRATOR, "PD-1(i)")
    tools = frontmatter_tools(text)
    assert CC_DISPATCH_TOOL in tools, (
        "PD-1(i)/AC-1: el derivado de Claude Code del orchestrator no declara "
        f"'{CC_DISPATCH_TOOL}' como herramienta de despacho (declara: "
        f"{sorted(tools)})"
    )
    assert OC_DISPATCH_TOOL not in tools, (
        "PD-1(i)/AC-1: el derivado de Claude Code del orchestrator declara "
        f"'{OC_DISPATCH_TOOL}' como herramienta de despacho; la real observada "
        f"es '{CC_DISPATCH_TOOL}' (declara: {sorted(tools)})"
    )
    assert re.search(
        r"Agent[^\n]{0,60}subagent_type|subagent_type[^\n]{0,60}Agent", text
    ), (
        "PD-1(i): el orchestrator de Claude Code no asocia su herramienta de "
        "despacho con `subagent_type: cdad-<role>`"
    )


# ---------------------------------------- PD-1(ii) — ninguna salida CC + OC


def test_pd1_ii_no_cc_agent_declares_task_as_dispatch_tool():
    """PD-1(ii)/AC-1: ninguna salida de Claude Code declara `Task` como
    herramienta de despacho (la línea `tools:` del orchestrator es hoy la
    única fuera de la tabla congelada de `tests/test_packet_prepare.py`)."""
    agents = sorted(CC_AGENTS.glob("cdad-*.md"))
    assert agents, (
        "PD-1(ii): no hay salidas de Claude Code en "
        f"{CC_AGENTS.relative_to(REPO)} — el contrato las declara salida del "
        "generador"
    )
    offenders = sorted(
        agent.name
        for agent in agents
        if OC_DISPATCH_TOOL in frontmatter_tools(read(agent, "PD-1(ii)"))
    )
    assert offenders == [], (
        "PD-1(ii)/AC-1: agentes de Claude Code que declaran "
        f"'{OC_DISPATCH_TOOL}' como herramienta de despacho: {offenders} "
        f"(la real observada es '{CC_DISPATCH_TOOL}')"
    )


def test_pd1_ii_opencode_side_keeps_its_tool_name():
    """PD-1/AC-1 (control de no-regresión): el lado OpenCode CONSERVA su
    propio nombre de herramienta de despacho."""
    text = read(OC_REF, "PD-1/AC-1 (control OpenCode)")
    assert re.search(rf"\b{OC_DISPATCH_TOOL}\b", text), (
        "PD-1/AC-1 (control): el reference de delegación de OpenCode ya no "
        f"nombra '{OC_DISPATCH_TOOL}' — el cambio de T1 es sólo del lado "
        "Claude Code"
    )


# --------------------------------------------- PD-1(iii) — la misma herramienta


def test_pd1_iii_adapter_owns_the_cc_dispatch_tool_name():
    """PD-1(iii)/AC-1: el adaptador fuente de Claude Code es el dueño del
    enunciado y nombra la misma herramienta que los derivados (`Agent`), sin
    declarar `Task` como herramienta de despacho de Claude Code."""
    text = read(ADAPTER, "PD-1(iii)")
    assert re.search(rf"\b{CC_DISPATCH_TOOL}\b", text), (
        "PD-1(iii)/AC-1: el adaptador fuente "
        f"({ADAPTER.relative_to(REPO)}) no nombra '{CC_DISPATCH_TOOL}' como "
        "herramienta de despacho de Claude Code"
    )
    assert names_task_as_a_cc_tool(text) is False, (
        "PD-1(iii)/AC-1: el adaptador fuente "
        f"({ADAPTER.relative_to(REPO)}) declara '{OC_DISPATCH_TOOL}' como "
        "herramienta de despacho de Claude Code; la herramienta real es "
        f"'{CC_DISPATCH_TOOL}'"
    )


def test_pd1_iii_reference_and_owners_name_the_same_tool():
    """PD-1(iii)/AC-1 (reformulado por 006-002 U2, PD-1/PD-3 — enmienda A-1):
    el reference de delegación de Claude Code, el adaptador fuente y el
    orquestador derivado nombran la MISMA herramienta (`Agent`), y la skill
    instalable YA NO es dueña de ese nombre: el nombre runtime-específico vive
    en la capa del agente (§4 neutral de `cdad-cycle`; antes esta aserción pedía
    `Agent` también en `SKILL.md`)."""
    for label, path in (
        ("claude-code-delegation.md", CC_REF),
        ("adaptador fuente", ADAPTER),
        ("orchestrator derivado", CC_ORCHESTRATOR),
    ):
        text = read(path, "PD-1(iii)")
        assert re.search(rf"\b{CC_DISPATCH_TOOL}\b", text), (
            f"PD-1(iii)/AC-1: {label} no nombra la herramienta de despacho "
            f"'{CC_DISPATCH_TOOL}' de Claude Code"
        )
    # 006-002 PD-1/PD-3: la skill no nombra la herramienta de ningún runtime en
    # contexto de delegación — el dueño del nombre es el agente del runtime.
    skill = read(SKILL, "PD-1(iii)/006-002 PD-1")
    assert not names_the_cc_tool_form(skill), (
        "PD-1(iii) + 006-002 PD-1/PD-3 (U2): SKILL.md nombra la herramienta de "
        f"despacho '{CC_DISPATCH_TOOL}' de Claude Code; el mecanismo pertenece a "
        "la capa del agente del runtime (el §4 de la skill queda abstracto)"
    )


# ------------------------------- PD-1(iv) — idempotencia y no-regresión


def test_pd1_iv_generator_staging_is_idempotent():
    """PD-1(iv)/INV-4: la regeneración de los agentes de Claude Code
    (`make agents` / el generador de staging) es idempotente: una segunda
    corrida no cambia bytes de los derivados."""
    assert GENERATOR.is_file(), (
        "PD-1(iv): el generador declarado scripts/cdad-generate.py no existe "
        "— la idempotencia de los derivados no es verificable"
    )
    with tempfile.TemporaryDirectory(prefix="cdad-005-004-t1-idem-") as tmp:
        out = Path(tmp) / "staging"
        first_run = run_generator(out)
        assert first_run.returncode == 0, (
            "PD-1(iv): la primera regeneración de los agentes de Claude Code "
            f"falló: {first_run.stderr!r}"
        )
        first = tree_hashes(out)
        assert first, "PD-1(iv): el generador no publicó ningún derivado"
        second_run = run_generator(out)
        assert second_run.returncode == 0, (
            "PD-1(iv): la segunda regeneración de los agentes de Claude Code "
            f"falló: {second_run.stderr!r}"
        )
        second = tree_hashes(out)
        changed = sorted(
            rel
            for rel in set(first) | set(second)
            if first.get(rel) != second.get(rel)
        )
        assert changed == [], (
            "PD-1(iv)/INV-4: la segunda corrida cambió bytes de los derivados: "
            f"{changed}"
        )
        assert (out / "agents" / GENERATOR_RUNTIME / "cdad-orchestrator.md").is_file(), (
            "PD-1(iv): la regeneración no publicó el orchestrator de Claude Code"
        )
        # Paridad declarada: los derivados del repo SON la salida del generador
        # (INV-2/INV-4: `agents/` es salida declarada, nunca editada a mano).
        # Es la misma igualdad que hace verificable «una segunda corrida no
        # cambia bytes de los derivados».
        staged = out / "agents" / GENERATOR_RUNTIME
        committed = REPO / "agents" / GENERATOR_RUNTIME
        staged_files = sorted(
            str(path.relative_to(staged)) for path in staged.rglob("*") if path.is_file()
        )
        committed_files = sorted(
            str(path.relative_to(committed))
            for path in committed.rglob("*")
            if path.is_file()
        )
        assert staged_files == committed_files, (
            "PD-1(iv)/INV-4: el conjunto de derivados de Claude Code del repo no "
            f"coincide con el del generador (repo={committed_files}, "
            f"generador={staged_files})"
        )
        mismatched = [
            rel
            for rel in staged_files
            if (staged / rel).read_bytes() != (committed / rel).read_bytes()
        ]
        assert mismatched == [], (
            "PD-1(iv)/INV-4: derivados de Claude Code editados a mano o no "
            f"regenerados: {mismatched}"
        )


def test_pd1_iv_ten_cc_agents_keep_their_tools_lines():
    """PD-1(iv)/INV-4 (control de no-regresión): las líneas `tools:` de los
    diez agentes de Claude Code con/sin guard siguen exactamente como hoy."""
    assert EXPECTED_GUARDS, "fixture drift: la tabla congelada de guardas está vacía"
    for name, guards in EXPECTED_GUARDS.items():
        expected = EDIT_TOOLS if guards else READ_ONLY_TOOLS
        tools = frontmatter_tools(read(CC_AGENTS / f"{name}.md", "PD-1(iv)"))
        assert tools == {token.strip() for token in expected.split(",")}, (
            f"PD-1(iv)/INV-4: la línea `tools:` de {name}.md cambió — "
            f"esperado {sorted(token.strip() for token in expected.split(','))}, "
            f"obtenido {sorted(tools)}"
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
