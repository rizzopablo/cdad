#!/usr/bin/env python3
"""PD-10 semantic permission-map checker (004-001 T7a, D7).

Replaces text-presence ("mechanism by text") asserts of the retained
path-barrier contract with SEMANTIC evaluation of the generated permission
frontmatter (agents/*.md — declared outputs of the generator, spec §2), using
findLast semantics.

Single evaluator rule (objective requirement): the findLast evaluator,
glob->regex translation, frontmatter parser, nested-block parser and rule
regex are REUSED by import from tests/test_opencode_read_map_and_steps.py —
nothing here re-implements evaluation semantics.

W-2 (2026-10-01, hallazgo del recorrido real; fuente documentada: sonda
en vivo de t7-live-walk.md §3): en OpenCode los permisos de `grep` y
`glob` se evalúan contra el PATRÓN DE BÚSQUEDA (la regex que se busca /
el glob que se busca), NO contra la ruta. El evaluador modela esa
semántica real:
  - `read` / `edit` (y el listado de directorio, que OpenCode media como
    `read`) → la sonda es la RUTA;
  - `grep` → la sonda es la REGEX DE BÚSQUEDA;
  - `glob` → la sonda es el PATRÓN GLOB de búsqueda.
Consecuencia: los mapas por ruta en `grep`/`glob` son inertes en
OpenCode. Una sonda de `grep` con forma de ruta (p. ej. "src/**")
acredita que la regla existe tal como se declara (caso esquina: alguien
que busca el texto literal "src/**"), no una barrera viva. Los derivados
por proyecto (004-002 I9) NO deben emitir entradas por ruta en
`grep`/`glob` — exigido en tests/test_004_002_t7_w2.py y en las
enmiendas de las aserciones T5; la corrección del generador global
(004-001) queda para 003-003 (friction-intake-004-001, adenda
2026-10-01).

Every check carries its trace 'PD-10: reemplaza <old-id>' (traceability of
the D7 replacement; the old text asserts retire in the same commit as their
passing replacement — mini-cycle T7, "sin borrar y ya").

Also consumed by tests/validate-consistency.sh (F009) and
tests/validate-odoo-specialization.sh (P1) via the CLI:
    python3 tests/pd10_permission_semantics.py [--set consistency|odoo|all]
        [--agents-dir PATH]  # default: <repo>/agents (mutation probes point
                             # at a MODIFIED COPY of the generated output)
Exit 0 iff every check passes. Prints one PASS/FAIL line per check.
Never installs to the real HOME; runs read-only against the tree.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO_ROOT / "tests"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent_frontmatter import permissions as v2_permissions  # noqa: E402

# --- reused evaluation machinery (NO second evaluator) ----------------------
from test_opencode_read_map_and_steps import (  # noqa: E402
    evaluate,     # findLast semantics: last matching rule wins, none=allow
    frontmatter,  # YAML frontmatter extractor
)

# --- parser composition (frontmatter maps -> rule lists) ---------------------
def perm_map(agent_text: str, key: str) -> list[tuple[str, str]]:
    """Rule list [(pattern, verb)] of the `<key>` frontmatter permission, in
    file order (findLast needs the order). Composed from the REUSED parsers.

    V2 `permissions` es una lista ordenada de entradas action/resource/effect."""
    action = "shell" if key == "bash" else key
    return [(entry["resource"], entry["effect"])
            for entry in v2_permissions(agent_text)
            if entry.get("action") == action]


def verdict(agent_text: str, tool: str, probe: str) -> str:
    """findLast verdict of `tool` for `probe` on one agent's frontmatter.

    Semántica real (W-2; sonda en vivo de t7-live-walk.md §3): para
    `read`/`edit` (y el listado, mediado como `read`) la sonda es la
    RUTA; para `grep` es la REGEX DE BÚSQUEDA y para `glob` el PATRÓN
    GLOB de búsqueda — OpenCode no evalúa estos dos permisos contra la
    ruta.
    """
    return evaluate(perm_map(agent_text, tool), probe)


def matcher_of(agent_text: str, needles: set[str]) -> str | None:
    """First PreToolUse hook matcher (CC agents) whose matched-tool set
    covers ALL of `needles`. Empty set -> the first matcher."""
    fm = frontmatter(agent_text)
    import re
    tools = None
    for line in fm.splitlines():
        m = re.match(r"\s*-\s*matcher:\s*(\S+)", line)
        if m:
            tools = frozenset(m.group(1).split("|"))
            if needles <= tools:
                return m.group(1)
    return None

# --- check sets --------------------------------------------------------------
# Each check: (trace, agent-file, tool, probe-path, expected-verdict)
READERS = ("cdad-architect", "cdad-reviewer", "cdad-scribe",
           "cdad-architect-odoo", "cdad-reviewer-odoo", "cdad-scribe-odoo")
READER_PROBES = (
    "docs/specs/004-001-canonical-runtime-artifacts/spec.md",
    "tests/test_a.py",
)

# Agent names are RELATIVE to the agents dir the runner is pointed at (the
# default is the repo's declared-output tree; mutation probes point at a
# MODIFIED COPY).
CONSISTENCY_CHECKS: list[tuple[str, str, str, str, str]] = []
# PD-10: reemplaza F009-readers-edit-deny — readers edit NOTHING (probe paths
# resolve deny on the edit map; mutation M2 in test_004_001_t7_pd10.py).
for _r in READERS:
    for _p in READER_PROBES:
        CONSISTENCY_CHECKS.append((
            f"PD-10: reemplaza F009-readers-edit-deny ({_r})",
            f"{_r}.md", "edit", _p, "deny"))
# PD-10: reemplaza F009-tw-edit-tests-allow — tests editable, non-test paths not.
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-tw-edit-tests-allow (allow side; NON-test-shaped "
     "file under tests/ — conftest.py matches no colocated-test glob, so the "
     "mutation dropping 'tests/**': allow provably kills this replacement)",
     "cdad-test-writer.md", "edit", "tests/conftest.py", "allow"),
    ("PD-10: reemplaza F009-tw-edit-tests-allow (deny side)",
     "cdad-test-writer.md", "edit", "skills/cdad-cycle/SKILL.md", "deny"),
    ("PD-10: reemplaza F009-tw-edit-tests-allow (colocated allow)",
     "cdad-test-writer.md", "edit", "src/pkg/app.test.ts", "allow"),
]
# PD-10: reemplaza F009-tw-read-src-deny — implementation invisible to read
# AND grep (same barrier, second channel; mutation M1).
# W-2 (t7-live-walk.md §3): la sonda de `grep` es la REGEX DE BÚSQUEDA —
# aquí acredita que la regla existe tal como se declara (el generador
# global 004-001 la declara; su corrección queda para 003-003). La
# barrera viva por ruta es `read`; los derivados por proyecto (004-002)
# no emiten entradas por ruta en grep/glob (tests/test_004_002_t7_w2.py).
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-tw-read-src-deny (read src)",
     "cdad-test-writer.md", "read", "src/app.py", "deny"),
    ("PD-10: reemplaza F009-tw-read-src-deny (control lib)",
     "cdad-test-writer.md", "read", "lib/x.py", "deny"),
    ("PD-10: reemplaza F009-tw-read-src-deny (grep src)",
     "cdad-test-writer.md", "grep", "src/**", "deny"),
]
# PD-10: reemplaza F009-tw-odoo-read-models-deny — odoo implementation dirs
# invisible (read + grep; mutation M5).
# W-2 (t7-live-walk.md §3): la sonda de `grep` es la REGEX DE BÚSQUEDA
# (caso esquina, igual que en F009-tw-read-src-deny arriba).
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-tw-odoo-read-models-deny (read)",
     "cdad-test-writer-odoo.md", "read", "addons/sale/models/sale.py", "deny"),
    ("PD-10: reemplaza F009-tw-odoo-read-models-deny (grep)",
     "cdad-test-writer-odoo.md", "grep", "**/models/**", "deny"),
]
# PD-10: reemplaza F009-imp-edit-catchall-allow — implementation editable.
CONSISTENCY_CHECKS.append((
    "PD-10: reemplaza F009-imp-edit-catchall-allow",
    "cdad-implementer.md", "edit", "src/lib.py", "allow"))
# PD-10: reemplaza F009-imp-edit-tests-deny (mutation M3).
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-imp-edit-tests-deny (tests path)",
     "cdad-implementer.md", "edit", "tests/test_a.py", "deny"),
    ("PD-10: reemplaza F009-imp-edit-tests-deny (co-located form)",
     "cdad-implementer.md", "edit", "src/pkg/test_mod.py", "deny"),
]
# PD-10: reemplaza F009-imp-no-models-deny — the odoo implementer's own scope
# (models/views) stays editable (bugfix 2026-09-29; mutations M4/M7).
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-imp-no-models-deny (models editable)",
     "cdad-implementer-odoo.md", "edit", "addons/sale/models/sale.py",
     "allow"),
    ("PD-10: reemplaza F009-imp-no-models-deny (views editable)",
     "cdad-implementer-odoo.md", "edit", "addons/sale/views/sale.xml",
     "allow"),
]
# PD-10: reemplaza F009-cc-tw-read-guard / F009-cc-imp-edit-guard — the CC
# path-guard hooks attach to the documented tool sets (set semantics over the
# matcher, not the literal string; mutations M9/M10).
CONSISTENCY_CHECKS += [
    ("PD-10: reemplaza F009-cc-tw-read-guard",
     "claude-code/cdad-test-writer.md", "matcher:Read|Grep|Glob", "", ""),
    ("PD-10: reemplaza F009-cc-imp-edit-guard",
     "claude-code/cdad-implementer.md", "matcher:Edit|Write", "", ""),
]

# --- odoo P1 check set --------------------------------------------------------
ODOO_CHECKS: list[tuple[str, str, str, str, str]] = []
# PD-10: reemplaza P1-tw-{models,views,controllers,wizards}-scope — presence of
# a word proves nothing (a body sentence containing 'Model: per profile' passed
# the old grep); the maps must DENY each odoo implementation dir (read+grep).
# W-2 (t7-live-walk.md §3): la sonda de `grep` es la REGEX DE BÚSQUEDA
# (caso esquina, igual que en el set consistency).
for _tool in ("read", "grep"):
    for _sub, _probe in (
        ("models", "addons/sale/models/sale.py"),
        ("views", "addons/sale/views/sale.xml"),
        ("controllers", "addons/sale/controllers/main.py"),
        ("wizards", "addons/sale/wizards/wiz.py"),
    ):
        ODOO_CHECKS.append((
            f"PD-10: reemplaza P1-tw-{_sub}-scope ({_tool})",
            "cdad-test-writer-odoo.md", _tool, _probe, "deny"))
# PD-10: reemplaza P1-tw-tests-allow — odoo-side tests path editable.
ODOO_CHECKS.append((
    "PD-10: reemplaza P1-tw-tests-allow",
    "cdad-test-writer-odoo.md", "edit",
    "addons/donation/tests/test_donation.py", "allow"))
# PD-10: reemplaza P1-tw-manifest-allow — no rule matches __manifest__.py, so
# the deny-list read map resolves it ALLOW by findLast default (the explicit
# allow the old assert demanded is unnecessary with deny-list ordering; the
# replacement guarantees the OBSERVABLE: reading a manifest resolves allow).
ODOO_CHECKS.append((
    "PD-10: reemplaza P1-tw-manifest-allow",
    "cdad-test-writer-odoo.md", "read", "addons/sale/__manifest__.py",
    "allow"))
# PD-10: reemplaza P1-imp-tests-deny — odoo implementer cannot edit tests.
ODOO_CHECKS.append((
    "PD-10: reemplaza P1-imp-tests-deny",
    "cdad-implementer-odoo.md", "edit",
    "addons/sale/tests/test_sale.py", "deny"))
# PD-10: reemplaza P1-imp-tests-deny (catch-all side) — its OWN scope editable
# (the 'models' word-presence assert said nothing about direction; the map
# semantics is what retains the bugfix of 80f9b90).
ODOO_CHECKS.append((
    "PD-10: reemplaza P1-imp-tests-deny (models own scope stays editable)",
    "cdad-implementer-odoo.md", "edit", "addons/sale/models/sale.py",
    "allow"))

SETS = {"consistency": CONSISTENCY_CHECKS, "odoo": ODOO_CHECKS}

# --- runner -------------------------------------------------------------------
def run_checks(agents_dir: Path, sets: list[str]) -> tuple[int, list[str]]:
    fails: list[str] = []
    n = 0
    for set_name in sets:
        for trace, agent, tool, probe, expect in SETS[set_name]:
            n += 1
            path = agents_dir / agent
            text = path.read_text(encoding="utf-8")
            if tool.startswith("matcher:"):
                needles = set(tool[len("matcher:"):].split("|"))
                got = matcher_of(text, needles)
                ok = got is not None
                detail = f"matcher covering {sorted(needles)} not declared" \
                    if not ok else ""
            else:
                try:
                    got = verdict(text, tool, probe)
                except (StopIteration, ValueError) as exc:
                    # robustness against mutated copies: a parser failure on
                    # one agent is a FAIL with a diagnostic, not a crash —
                    # the validator's FAIL line still carries the trace.
                    ok = False
                    detail = (f"checker parse error on {agent} "
                              f"({tool}/{probe!r}): {exc!r}")
                else:
                    ok = got == expect
                    detail = f"{tool}({probe!r}) resolved {got!r}, want {expect!r}"
            if ok:
                print(f"PASS: {trace} [{agent}]")
            else:
                fails.append(f"FAIL: {trace} [{agent}] — {detail}")
    return n, fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--set", dest="sets", action="append",
                    choices=["consistency", "odoo"],
                    help="which check-set(s) to run (repeatable; default all)")
    ap.add_argument("--agents-dir", type=Path,
                    default=REPO_ROOT / "agents",
                    help="directory holding the declared generated agents/")
    args = ap.parse_args()
    sets = args.sets or ["consistency", "odoo"]
    total, fails = run_checks(args.agents_dir, sets)
    for f in fails:
        print(f)
    print(f"PD-10 semantic checks: {total - len(fails)}/{total} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
