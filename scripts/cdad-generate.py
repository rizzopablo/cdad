#!/usr/bin/env python3
"""cdad-generate.py — deterministic agent generator (004-001 T3, spec §2).

Composes the declared runtime agents from the canonical editable sources:

    scripts/cdad-generate.py --runtime <opencode|claude-code> \
        --stack <auto|odoo> --out <staging-dir>

Outputs ``<out>/agents/<runtime>/cdad-*.md`` (the 11 declared agents: 5 roles
× {base, -odoo} + orchestrator) plus ``<out>/manifest.json`` (per artifact:
sha256, contributing sources, regeneration command, stack).

Guarantees implemented here (docs/specs/004-001-canonical-runtime-artifacts):
- PD-2 determinism: same inputs → byte-identical outputs (no timestamps,
  sorted keys, content derived only from sources + explicit parameters).
- PD-1 (004-001 T4) derived bash policy: the OpenCode bash block is parsed
  from the role sources' own rule/pair declarations (reader class: architect;
  writer class: test-writer) plus the adapter's declared composition rules —
  no rule is retained without its source declaration.
- PD-3 explicit failure: incomplete/duplicated/empty source sections, text
  outside a section, duplicated shared blocks, or an unsupported
  runtime×stack → non-zero exit with a diagnostic naming the problem and
  ZERO published files (all validation happens before any write).
- PD-4 single source: shared blocks are hosted once (sources/roles) and
  composed into every consumer; the orchestrator's §2 is a COMPOSED artifact;
  the manifest references each contributing source.
- PD-1e/PD-1f/PD-7a (006-003) — no profile, no model map, no model:
  the generator has no `--profile` surface (the option is REJECTED with a
  diagnostic that points at the delegation configuration as the place where
  the model is chosen), it resolves no model (the retired model map is gone),
  it publishes no `model:` line in any agent and §2 of the orchestrator
  carries no model cell and names no model (INV-3). The model of a role is the
  one configured in the runtime; external delegation takes it from the
  delegation configuration.
- PD-15 honesty: no generated line may mention "sandbox" without an honest
  negation on the same line (self-checked before publishing).
- PD-16 legacy fallback: every generated agent declares its legacy loads.

Python stdlib only. No shell is invoked: the composition is pure text.

Staging merge (004-001 T5): the declared regeneration flow (`make staging`)
runs the generator once per runtime into the SAME --out directory. Each run
MERGES its artifacts into the existing manifest.json (entries of other
runtimes are kept verbatim; this runtime's entries are replaced; the header
records THIS run's runtime/stack). The per-runtime membership is
encoded in the artifact paths (agents/<runtime>/...), so the published
staging manifest covers the whole staged set and the installer can consume it
as its single entry. Re-running the SAME runtime into the same directory is
still byte-identical (PD-2): the merge replaces that runtime's entries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"

ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
REQUIRED_ROLE_SECTIONS = ("directive", "contract", "bash", "convention", "capacity", "odoo", "limits")
REQUIRED_ADAPTER_SECTIONS = ("frontmatter", "permissions", "tool-loading", "delegation")

# Shared blocks: single editable definitions (PD-4) and their host sources.
SHARED_HOSTS = {
    "intake-core": "architect",
    "limits-core": "architect",
    "convention-rule": "test-writer",
}

SOURCE_OPEN_RE = re.compile(r"<!-- cdad-source:(role|adapter):([a-z0-9-]+) -->")
SECTION_OPEN_RE = re.compile(r"<!-- cdad-section:([a-z0-9-]+) -->")
SECTION_CLOSE = "<!-- /cdad-section -->"
SOURCE_CLOSE = "<!-- /cdad-source -->"
FULL_LINE_COMMENT_RE = re.compile(r"(?m)^[ \t]*<!--.*-->[ \t]*$\n?")
BLANK_RUN_RE = re.compile(r"\n{3,}")

NEGATION_RE = re.compile(r"\b(no|not|never|sin|não)\b")
SANDBOX_SKILL_NAME = "odoo-sandbox-env"
COMPOSED_MARKER = "Roles-contract §2 table — composed"

# Domain skills per role for stack=odoo (declared in each role source's `odoo`
# section); the packet path keeps loading them (P6, packet lacks domain knowledge).
ODOO_SKILLS = {
    "architect": ("odoo-architect",),
    "test-writer": ("odoo-test-writer",),
    "implementer": ("odoo-expert", "odoo-make-env"),
    "reviewer": ("odoo-reviewer",),
    "scribe": ("odoo-make-env",),
}


class GenerateError(Exception):
    """PD-3: explicit, diagnosable failure with zero published output."""


def fail(message: str) -> None:
    raise GenerateError(message)


# ---------------------------------------------------------------------------
# Source parsing (grammar: cdad-source / cdad-section / cdad-shared)
# ---------------------------------------------------------------------------

def parse_source(path: Path, kind: str, required: tuple[str, ...]) -> dict[str, str]:
    """Parse one canonical source; fail loudly on any grammar violation."""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    opens = list(SOURCE_OPEN_RE.finditer(text))
    if len(opens) != 1 or opens[0].group(1) != kind:
        fail(f"{rel}: expected exactly one cdad-source:{kind} marker (PD-3)")
    start = opens[0].end()
    try:
        end = text.index(SOURCE_CLOSE, start)
    except ValueError:
        fail(f"{rel}: unterminated cdad-source (missing {SOURCE_CLOSE!r})")
    body = text[start:end]

    sections: dict[str, str] = {}
    consumed: list[tuple[int, int]] = []
    for match in SECTION_OPEN_RE.finditer(body):
        sec_name = match.group(1)
        if sec_name in sections:
            fail(f"{rel}: duplicated section '{sec_name}' (PD-3: a section may appear exactly once)")
        content_start = match.end()
        try:
            content_end = body.index(SECTION_CLOSE, content_start)
        except ValueError:
            fail(f"{rel}: section '{sec_name}' is unterminated (missing {SECTION_CLOSE!r})")
        content = body[content_start:content_end]
        if not content.strip():
            fail(f"{rel}: empty section '{sec_name}' (PD-3: a declared section cannot be empty)")
        sections[sec_name] = content
        consumed.append((match.start(), content_end + len(SECTION_CLOSE)))

    leftover = body
    for begin, finish in sorted(consumed, reverse=True):
        leftover = leftover[:begin] + leftover[finish:]
    if leftover.strip():
        shared = re.search(r"<!-- cdad-shared:([a-z0-9-]+) -->", leftover)
        if shared:
            fail(
                f"{rel}: duplicated cdad-shared block '{shared.group(1)}' outside a "
                "cdad-section — shared blocks are hosted exactly once (PD-3/PD-4)"
            )
        fail(f"{rel}: text outside any cdad-section (PD-3): {leftover.strip()[:60]!r}")

    for name in required:
        if name not in sections:
            fail(f"{rel}: missing required section '{name}' (PD-3: declared consumers need it)")
    return sections


def extract_shared_blocks(text: str) -> list[tuple[str, str]]:
    return re.findall(
        r"<!-- cdad-shared:([a-z0-9-]+) -->(.*?)<!-- /cdad-shared -->", text, re.S
    )


def compose_shared_pointer(section_text: str, shared_name: str, shared_body: str) -> str:
    """Consumer composition: the pointer line that cites the shared token
    (`Intake: shared core (...).` / `Shared limits core (...).`) is replaced
    by the shared block body — composed into the agent, not referenced (PD-4).
    Only the pointer sentence is replaced; the role's own rules stay intact."""
    pattern = re.compile(r"(?s)^.*?cdad-shared:%s.*?\)\." % re.escape(shared_name))
    if not pattern.search(section_text):
        return section_text
    return pattern.sub(shared_body.strip(), section_text, count=1)


def strip_full_line_comments(text: str) -> str:
    cleaned = FULL_LINE_COMMENT_RE.sub("", text)
    cleaned = BLANK_RUN_RE.sub("\n\n", cleaned)
    return cleaned.strip("\n")


# ---------------------------------------------------------------------------
# OpenCode frontmatter (permission block: role source's bash policy + adapter
# mechanics; the bash policy is the permissive catch-all allow — owner
# decision 2026-09-29, reverses 002-009)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# T4 (004-001): the bash policy is DERIVED from the canonical role sources
# (PD-1: no rule retained without source justification). Each role class
# composes its policy from its declared host: readers (architect/reviewer/
# scribe) from sources/roles/architect.md; writers (test-writer/implementer)
# from sources/roles/test-writer.md. Owner decision 2026-09-29 (reverses
# 002-009 bash-allowlist-hardening): the policy is PERMISSIVE — one catch-all
# allow, declared in the host source; the retained barriers are PATH-based
# (edit/read/glob maps, CC path-guard) and contract-level, never
# operation-based. The generator owns the mechanics only (declaration
# detection, honest effect comments).
# ---------------------------------------------------------------------------

_READER_BASE_HOST = "architect"
_WRITER_POLICY_HOST = "test-writer"

# PD-4 manifest traceability: role classes composing a policy from a host
# other than their own source.
_BASH_POLICY_HOSTS = {"reviewer": _READER_BASE_HOST, "scribe": _READER_BASE_HOST, "implementer": _WRITER_POLICY_HOST}

# Declared structure of the host sources' bash sections. Owner decision
# 2026-09-29 (reverses 002-009 bash-allowlist-hardening): the operational
# policy is PERMISSIVE — the canonical mini-language reduces to the mandatory
# catch-all allow declaration `rule "*"` in each host source; the retained
# barriers are PATH-based (edit/read/glob maps, CC path-guard) and
# contract-level, never operation-based.
_CATCH_ALL_ALLOW_DECL = 'rule "*"'

# Adapter composition rule for the path-glob maps, per runtime: the writer's
# PATH barriers must stay adapter-declared (PD-1/PD-3) — opencode composes the
# read/edit/grep YAML maps; claude-code composes the path-guard hooks.
_ADAPTER_PATH_GLOBS_DECL = {
    "opencode": "Path globs for",
    "claude-code": "Read|Grep|Glob",
}


def reader_policy_lines(sections: dict[str, str]) -> list[str]:
    """Reader policy, derived from the architect source (shared host).

    Permissive operational policy (owner decision 2026-09-29): the source must
    declare the catch-all allow (`rule "*"`); the adapter emits it as the only
    bash rule. A source without the declaration is a PD-3 failure — the policy
    is never silent.
    """
    if _CATCH_ALL_ALLOW_DECL not in sections["bash"]:
        fail(
            "sources/roles/architect.md: permissive bash policy declaration "
            f"({_CATCH_ALL_ALLOW_DECL!r}) missing (PD-3: policy never silent)"
        )
    return ['    "*": allow']


def writer_policy_lines(
    sections: dict[str, str], adapter_permissions: str, runtime: str
) -> list[str]:
    """Writer policy, derived from the test-writer source (shared host).

    Same permissive policy as the reader class (owner decision 2026-09-29);
    the former reading-denies (B1) and base/suite/commit pair lists are
    retired from the bash layer. The writer's retained barriers are the
    PATH maps, composed by the runtime adapter (declared — PD-1/PD-3).
    """
    if _CATCH_ALL_ALLOW_DECL not in sections["bash"]:
        fail(
            "sources/roles/test-writer.md: permissive bash policy declaration "
            f"({_CATCH_ALL_ALLOW_DECL!r}) missing (PD-3: policy never silent)"
        )
    marker = _ADAPTER_PATH_GLOBS_DECL[runtime]
    if marker not in adapter_permissions:
        fail(
            f"sources/agents/adapters/{runtime}.md: the path-glob composition "
            f"rule ({marker!r}) is missing (PD-3: the writer's path barriers "
            "must stay adapter-declared)"
        )
    return ['    "*": allow']


def bash_policy_lines(
    role: str,
    stack: str,
    role_sections: dict[str, dict[str, str]],
    adapter_permissions: str,
    runtime: str = "opencode",
) -> list[str]:
    """Complete `bash:` block for one OpenCode role agent: the permissive
    operational policy composed from the role class's declared host source
    (reader: architect; writer: test-writer). Owner decision 2026-09-29
    (reverses 002-009): NO operation filtering — one catch-all allow; the
    guards live at the path layer and the role contracts (declared, not a
    sandbox).
    """
    if role in ("test-writer", "implementer"):
        policy = writer_policy_lines(
            role_sections[_WRITER_POLICY_HOST], adapter_permissions, runtime
        )
    else:
        policy = reader_policy_lines(role_sections[_READER_BASE_HOST])
    lines = [
        "    # Generated by scripts/cdad-generate.py from the canonical role",
        "    # sources (PD-1: every rule is declared there) + the OpenCode adapter",
        "    # (mechanics). Permissive operational policy (owner decision",
        "    # 2026-09-29, reverses 002-009): NO operation filtering — the",
        "    # barriers are PATH-based (edit/read/glob maps) and contract-level.",
        "    # Mechanism limit: declared, NOT a sandbox — bash can read/write",
        "    # anything; the edit-path maps are the systematic guard.",
    ] + policy
    return lines


_TEST_GLOBS = [
    "src/**/*_test.go", "src/**/test_*.py",
    "src/**/*.test.js", "src/**/*.test.ts", "src/**/*.test.mjs", "src/**/*.test.cjs",
    "src/**/*.spec.ts", "src/**/*.spec.js",
    "lib/**/*_test.go", "lib/**/test_*.py",
    "lib/**/*.test.js", "lib/**/*.test.ts", "lib/**/*.test.mjs", "lib/**/*.test.cjs",
    "lib/**/*.spec.ts", "lib/**/*.spec.js",
]
_IMPL_TEST_GLOBS = [
    "tests/**", "**/tests/**", "**/*_test.go",
    "**/*.test.js", "**/*.test.ts", "**/*.test.mjs", "**/*.test.cjs",
    "**/*.spec.ts", "**/*.spec.js", "**/test_*.py",
]
# Odoo implementation paths: the test-writer's read/grep invisibility barrier
# (NOT an edit barrier — the implementer edits these; bugfix 2026-09-29).
_ODOO_IMPL_GLOBS = ["**/models/**", "**/views/**", "**/controllers/**", "**/wizards/**"]


def _globs_block(key: str, pairs: list[tuple[str, str]], comment: str) -> list[str]:
    lines = [f"  {key}:", f"    # {comment}"]
    lines += [f'    "{pattern}": {action}' for pattern, action in pairs]
    return lines


def _write_key_note_lines() -> list[str]:
    # 006-005 U6-7: the cdad-010 P1 lever is RETIRED. OpenCode v2.0.27 evaluates
    # `write` for the write tool together with `edit` (findLast), so a trailing
    # `write: ask` voided every role's path map.
    return [
        "  # la clave `write` no se emite: v2.0.27 la evalua para la escritura y",
        "  # anularia el mapa `edit` (U6-7).",
    ]


_STEPS_DECL_RE = re.compile(r"steps:\s*(\d+)")


def steps_ceiling(frontmatter_section: str) -> int:
    """The OpenCode step ceiling, declared ONCE in the adapter (P2/P3).

    Read from the `frontmatter` section of sources/agents/adapters/opencode.md
    (a line containing `steps: N`); the value is never hardcoded in this file.
    PD-3: an absent or non-numeric declaration fails loudly, naming the source.
    """
    decl_path = "sources/agents/adapters/opencode.md"
    match = _STEPS_DECL_RE.search(frontmatter_section)
    if not match:
        fail(
            f"{decl_path}: the machine-readable step ceiling is absent or "
            "non-numeric in the `frontmatter` section (expected a line "
            "containing `steps: N`, e.g. `steps: 300`) (PD-3)"
        )
    return int(match.group(1))


def oc_frontmatter(
    role: str, description: str, stack: str, bash_lines: list[str],
    steps: int,
) -> str:
    lines = ["---", f"description: {description}", "mode: subagent"]
    lines.append(f"steps: {steps}")
    if role == "reviewer":
        lines.append("temperature: 0.1")
    if role not in ("test-writer", "implementer"):
        lines += [
            "# edit: deny — top-level mirror of permission.edit below (cdad-010 P2/A6).",
            "# INERT at runtime; it stays only as a marker of the role's read-only state.",
            "edit: deny",
        ]
    lines += ["permission:"] + _write_key_note_lines()
    if role == "test-writer":
        read_denies = _ODOO_IMPL_GLOBS if stack == "odoo" else ["src/**", "lib/**"]
        read_pairs = [(glob, "deny") for glob in read_denies] + [
            (glob, "allow") for glob in _TEST_GLOBS
        ]
        edit_pairs = [("*", "deny"), ("tests/**", "allow"), ("**/tests/**", "allow")] + [
            (glob, "allow") for glob in _IMPL_TEST_GLOBS[2:]
        ]
        grep_pairs = [(glob, "deny") for glob in read_denies]
        lines += _globs_block("read", read_pairs, "deny-list: implementation paths denied, colocated tests allowed; the contract, docs and tests are readable by default (cdad-010 P2/A4).")
        lines += _globs_block("edit", edit_pairs, "tests-only edits, expanded globs — the matcher escapes { } (audit 3.3); never braces.")
        lines += ["  bash:"] + bash_lines
        lines += _globs_block("grep", grep_pairs, "content search scoped: the implementation is invisible to Grep too (B1).")
    elif role == "implementer":
        # Implementer reads broadly; the hard barrier is on EDITS (never tests/**,
        # including colocated tests — anti-gaming invariant, ADR-011:94).
        # Odoo stack (bugfix 2026-09-29): models/views/controllers/wizards are
        # the implementer's OWN scope — only tests stay denied.
        edit_denies = ["tests/**", "**/tests/**"] + _IMPL_TEST_GLOBS[2:]
        lines += _globs_block(
            "edit",
            [("*", "allow")] + [(glob, "deny") for glob in edit_denies],
            "catch-all ALLOW (self-containment: never inherited) + tests blocklist;"
            " findLast order: catch-all first, denies after; no braces (audit 3.3).",
        )
        lines += ["  bash:"] + bash_lines
    else:
        lines += [
            "  edit: deny",
            "  # Read-only by CDAD design (anti-confirmation-bias): the artifact is delivered",
            "  # as the delegate's final text; the ORCHESTRATOR materializes it (ADR-003).",
            "  bash:",
        ] + bash_lines
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Claude Code frontmatter (adapter: tools + PreToolUse path-guard hooks; the
# installer deploys the staged bytes untransformed — no `model:` line is
# generated for either runtime since 006-003 PD-1e, baseline PD-13)
# ---------------------------------------------------------------------------

def cc_tools(role: str) -> str:
    tools = ["Read", "Grep", "Glob", "Bash"]
    if role in ("test-writer", "implementer"):
        tools += ["Edit", "Write"]
    if role == "orchestrator":
        tools += ["Edit", "Write", "Agent"]
    tools.append("Skill")
    return ", ".join(tools)


# Claude Code PreToolUse path-guard wiring — the retained methodological
# barriers (barriers at base ddd3109: tools + guards do not change). Guard
# names are the path-guard matcher modes, exactly as installed today.
# Owner decision 2026-09-29 (reverses 002-009): NO operation filtering — the
# Bash content-guard hooks (test-writer-bash / implementer-bash and odoo
# variants) are RETIRED; only path-based Read/Grep/Glob and Edit/Write guards
# remain.
CC_GUARDS: dict[str, list[tuple[str, str, str]]] = {
    # role-variant: [(matcher, guard mode, hook key)] in installation order.
    "test-writer": [
        ("Read|Grep|Glob", "test-writer-read", "read"),
        ("Edit|Write", "test-writer-write", "write"),
    ],
    "test-writer-odoo": [
        ("Read|Grep|Glob", "test-writer-odoo-read", "read"),
        ("Edit|Write", "test-writer-odoo-write", "write"),
    ],
    "implementer": [
        ("Edit|Write", "implementer", "write"),
    ],
    "implementer-odoo": [
        ("Edit|Write", "implementer-odoo", "write"),
    ],
}


def cc_hooks(role: str, stack: str) -> list[tuple[str, str]]:
    """(matcher, guard mode) pairs — path-scoping lives in the guard script."""
    return [(matcher, guard) for matcher, guard, _ in CC_GUARDS.get(f"{role}{'-odoo' if stack == 'odoo' else ''}", [])]


def cc_frontmatter(role: str, stack: str, name: str, description: str) -> str:
    lines = ["---", f"name: {name}", f"description: {description}", f"tools: {cc_tools(role)}"]
    hooks = cc_hooks(role, stack)
    if hooks:
        lines += ["hooks:", "  PreToolUse:"]
        for matcher, guard in hooks:
            lines += [
                f"    - matcher: {matcher}",
                "      hooks:",
                "        - type: command",
                f"          command: ~/.claude/cdad-scripts/path-guard.sh {guard}",
                "          timeout: 5",
            ]
    lines += [
        "# Path-scoping is enforced by ~/.claude/cdad-scripts/path-guard.sh (the",
        "# installed CC destination; repo source: scripts/claude-code-path-guard.sh):",
        "# fail-open on unknown role; prevention of accidents, not isolation",
        "# (declared, PD-15).",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Role metadata (one-line descriptions composed from the role sources)
# ---------------------------------------------------------------------------

ROLE_META = {
    "architect": {
        "description": "CDAD architect — stages 1 (Discovery) and 2 (Spec). Read-only. Socratic brainstorm + spec draft (+ plan draft for complex features).",
        "stage": "You operate in stage 1 (Discovery) and stage 2 (Specification).",
    },
    "test-writer": {
        "description": "CDAD test-writer — stage 3 (AUDIT, POST-AUDIT, RED, Properties, E2E). Edits tests/ only; never sees implementation code.",
        "stage": "You operate in stage 3 (anti-gaming TDD): audit, post-audit, red, properties, e2e.",
    },
    "implementer": {
        "description": "CDAD implementer — stage 3 GREEN (+ REFACTOR/review-fix sub-modes). Minimal code that makes the approved test pass; never edits tests.",
        "stage": "You operate in stage 3 (TDD), GREEN sub-phase, with optional REFACTOR sub-mode.",
    },
    "reviewer": {
        "description": "CDAD reviewer — stage 4. Read-only adversarial review of the diff against the approved spec; different model from the implementer (anti-confirmation-bias).",
        "stage": "You operate in stage 4 (Review).",
    },
    "scribe": {
        "description": "CDAD scribe — stage 5. Memory Bank update drafts faithful to the evidence; drafts only, the user approves, the orchestrator commits.",
        "stage": "You operate in stage 5 (Merge + Memory Bank).",
    },
}

ORCHESTRATOR_DESCRIPTION = (
    "CDAD orchestrator — detects the stage, validates gates, prepares/delegates role "
    "packets, materializes read-only artifacts and updates the state file. Primary "
    "agent to start/resume/advance CDAD features or epics."
)


def reviewer_method_fragment() -> str:
    return (
        "## Review method (5 axes) and severity (addyosmani)\n"
        "\n"
        "- Axes: 1 Correctness — spec/task fit, edge cases, error paths · "
        "2 Readability & Simplicity — names, direct control flow, fewest lines · "
        "3 Architecture — patterns, boundaries, complexity reduced (not relocated) · "
        "Axis 4: Security — input validation, secrets, authz, parameterized SQL, "
        "encoded outputs · 5 Performance — N+1, unbounded loops, pagination, hot paths.\n"
        "- Severity (addyosmani): **Critical:** Blocks merge (vulnerability, data loss, "
        "broken functionality) · Required (no prefix) · **Nit** (minor, optional) · "
        "**Optional/Consider** · **FYI**. Lead with what matters: order by leverage.\n"
        "- Structural remedies: propose the move, not just the problem. Detail: "
        "`skills/cdad-cycle/references/stage-4-review.md`.\n"
    )


def test_writer_red_fragment() -> str:
    return (
        "## RED discipline\n"
        "\n"
        "RED verifies the requirement, it does not maximize coverage: one test per\n"
        "numbered postcondition, failing for the right reason (AssertionError, not\n"
        "ImportError); exhaustive coverage and edge cases not demanded by a\n"
        "postcondition belong to a later hardening stage. Detail: "
        "`skills/cdad-cycle/references/stage-3-tdd.md`.\n"
    )


def model_note() -> str:
    """§2's model note (006-003 PD-1/PD-7a/INV-3; A-5, §9).

    One line, and it fixes nothing: the model of each role is the one
    configured in the runtime, and external delegation reads it from the
    delegation configuration; CDAD does not choose it. The reviewer/model
    requirement is retired (A-5).
    """
    return (
        "Model choice. The model of each role is the one configured in the runtime; "
        "this skill names no model and no installable text fixes one. External "
        "delegation takes the model from the delegation configuration (per "
        "destination and role); a destination or role without an entry runs the "
        "destination's own default and the model is reported as not verifiable, never "
        "invented. CDAD does not choose it."
    )


# ---------------------------------------------------------------------------
# PD-15 honesty normalization + self-check
# ---------------------------------------------------------------------------

def normalize_honesty(text: str) -> str:
    """Every line mentioning 'sandbox' (except the skill name) must carry an
    honest negation on the same line. Mechanical normalization: standalone
    negation tokens in caps are lowercased; anything still lacking a negation
    is a source defect and fails loudly."""
    out = []
    for line in text.splitlines():
        stripped = line.replace(SANDBOX_SKILL_NAME, "")
        if "sandbox" in stripped.lower() and not NEGATION_RE.search(stripped):
            line = re.sub(r"\b(NO|NOT|NEVER)\b", lambda m: m.group(0).lower(), line)
        out.append(line)
    return "\n".join(out)


def assert_honesty(text: str, label: str) -> None:
    for line in text.splitlines():
        stripped = line.replace(SANDBOX_SKILL_NAME, "")
        if "sandbox" in stripped.lower() and not NEGATION_RE.search(stripped):
            fail(f"PD-15: {label} mentions 'sandbox' without an honest negation: {line.strip()!r}")


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def compose_role_agent(
    role: str,
    stack: str,
    sections: dict[str, str],
    shared_blocks: dict[str, str],
    runtime: str,
    bash_lines: list[str],
    steps: int,
) -> tuple[str, str]:
    """Return (agent_name, agent_text) for one role × stack × runtime."""
    name = f"cdad-{role}{'-odoo' if stack == 'odoo' else ''}.md"
    meta = ROLE_META[role]
    display = "Test-Writer" if role == "test-writer" else role.capitalize()
    title = f"# CDAD {display} Agent" + (" — Odoo variant" if stack == "odoo" else "")

    directive = sections["directive"]
    if role != "architect":  # the architect hosts the intake; consumers get it composed
        directive = compose_shared_pointer(directive, "intake-core", shared_blocks["intake-core"])
    if stack == "odoo":
        # P6: the packet path keeps loading the role's domain skills (the packet
        # lacks domain knowledge) — appended INSIDE the Validated-packet bullet
        # so it stays in the same branch block.
        anchor_re = re.compile(r"the\s+packet does not carry domain knowledge\.")
        if not anchor_re.search(directive):
            fail(f"sources/roles/{role}.md: the packet-path anchor is missing (P6 composition)")
        skills = ", ".join(f"`{skill}`" for skill in ODOO_SKILLS[role])
        directive = anchor_re.sub(
            lambda m: m.group(0)
            + "\n  In the packet path the role also loads its domain skills (%s)"
            " without loading or reloading `cdad-cycle` (declared in the odoo"
            " stack delta below)." % skills,
            directive,
            count=1,
        )

    limits = sections["limits"]
    if "<!-- cdad-shared:limits-core -->" not in limits:
        limits = compose_shared_pointer(limits, "limits-core", shared_blocks["limits-core"])

    body = [
        title,
        "",
        "You are the **%s** role of the Contract-Driven AI Development (CDAD) cycle. %s%s" % (
            role, meta["stage"], " Specialized for Odoo projects (stack=odoo)." if stack == "odoo" else ""
        ),
        "",
        "## Main directive",
        "",
        strip_full_line_comments(directive),
        "",
        "## Roles-contract row (§2)",
        "",
        strip_full_line_comments(sections["contract"]),
    ]
    if role == "reviewer":
        body += ["", reviewer_method_fragment().rstrip("\n")]
    if role == "test-writer":
        body += ["", test_writer_red_fragment().rstrip("\n")]
    body += [
        "",
        "## Bash policy",
        "",
        strip_full_line_comments(sections["bash"]),
        "",
        "## Test convention",
        "",
        strip_full_line_comments(sections["convention"]),
        "",
        "## Capacity (ADR-011)",
        "",
        strip_full_line_comments(sections["capacity"]),
    ]
    if stack == "odoo":
        body += ["", "## Odoo stack delta (declared)", "", strip_full_line_comments(sections["odoo"])]
    body += [
        "",
        "## Honest limitations (PD-15)",
        "",
        strip_full_line_comments(limits),
        "",
        "## Tool loading and delegation (adapter)",
        "",
        strip_full_line_comments(ADAPTER_SECTIONS["tool-loading"]),
        "",
    ]
    frontmatter = (
        oc_frontmatter(role, meta["description"], stack, bash_lines, steps)
        if runtime == "opencode"
        else cc_frontmatter(role, stack, name.removesuffix(".md"), meta["description"])
    )
    text = normalize_honesty(frontmatter + "\n---\n\n" + "\n".join(body))
    return name, text.rstrip("\n") + "\n"


def extract_contract_row(contract_text: str, role: str) -> str:
    """The role's own §2 row line, from its source's contract section."""
    pattern = r"^\|\s*%s\s*\|" % re.escape(role)
    for line in contract_text.splitlines():
        stripped = line.strip()
        if re.match(pattern, stripped):
            return stripped
    fail(
        f"sources/roles/: contract table row for '{role}' not found "
        "(PD-4: the orchestrator §2 is composed from the role sources)"
    )
    return ""


def compose_orchestrator_agent(
    sections: dict[str, str],
    role_sections: dict[str, dict[str, str]],
    shared_blocks: dict[str, str],
    runtime: str,
) -> tuple[str, str]:
    """Return (agent_name, agent_text) for the orchestrator (§2 COMPOSED)."""
    contract_paras = [p.strip() for p in sections["contract"].split("\n\n") if p.strip()]
    composed_prose = contract_paras[0]
    if COMPOSED_MARKER not in composed_prose:
        fail("sources/roles/orchestrator.md: the contract section lost the composed §2 marker (PD-4)")
    anti_bias = [p for p in contract_paras if p.startswith("Anti-bias invariants")]
    if not anti_bias:
        fail("sources/roles/orchestrator.md: the contract section lost its anti-bias invariants (PD-4)")
    anti_bias_text = anti_bias[0].rstrip()

    header = "| Role | Stages | Does | May read | May edit | Never touches | Artifact |"
    separator = "|---|---|---|---|---|---|---|"
    rows = []
    for role in ROLES:
        rows.append(extract_contract_row(role_sections[role]["contract"], role))
    rows.append(extract_contract_row(sections["contract"], "orchestrator"))

    limits = sections["limits"]
    if "<!-- cdad-shared:limits-core -->" not in limits:
        limits = compose_shared_pointer(limits, "limits-core", shared_blocks["limits-core"])

    body = [
        "# CDAD Orchestrator Agent",
        "",
        "You are the **orchestrator** of the Contract-Driven AI Development (CDAD) "
        "cycle. Primary agent: the user (a human or a higher-hierarchy autonomous "
        "agent) selects you to start/resume/advance a feature or epic with CDAD. The "
        "model is chosen by the user when selecting you; there is deliberately no "
        "hardcoded model.",
        "",
        "## Main directive (packet-renderer driver)",
        "",
        strip_full_line_comments(sections["directive"]),
        "",
        "### 2. Contract of each role",
        "",
        composed_prose,
        "",
        "Composed rows (sources/roles/*.md — composed by the generator; every row "
        "is the role's own §2 line, restated nowhere):",
        "",
        header,
        separator,
        *rows,
        "",
        anti_bias_text,
        "",
        model_note(),
        "",
        "## Delegation",
        "",
        strip_full_line_comments(ADAPTER_SECTIONS["delegation"]),
        "",
        "## Bash policy (supervisor — no allowlist is generated)",
        "",
        strip_full_line_comments(sections["bash"]),
        "",
        "## Test convention",
        "",
        strip_full_line_comments(sections["convention"]),
        "",
        "## Capacity (ADR-011)",
        "",
        strip_full_line_comments(sections["capacity"]),
        "",
        "## Stack resolution (declared delta)",
        "",
        strip_full_line_comments(sections["odoo"]),
        "",
        "## Honest limitations (PD-15)",
        "",
        strip_full_line_comments(limits),
        "",
        "## Tool loading and delegation (adapter)",
        "",
        strip_full_line_comments(ADAPTER_SECTIONS["tool-loading"]),
        "",
    ]
    if runtime == "opencode":
        frontmatter = (
            "---\n"
            f"description: {ORCHESTRATOR_DESCRIPTION}\n"
            "mode: all\n"
            "permission: allow\n"
            "---\n"
        )
    else:
        frontmatter = (
            cc_frontmatter("orchestrator", "", "cdad-orchestrator", ORCHESTRATOR_DESCRIPTION)
            + "\n---\n"
        )
    text = normalize_honesty(frontmatter + "\n" + "\n".join(body))
    return "cdad-orchestrator.md", text.rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Assembly + manifest
# ---------------------------------------------------------------------------

def role_stack_pairs(effective_stack: str) -> list[str]:
    """stack=odoo emits base + odoo variants; a non-odoo resolution emits the
    generic (base) agents only."""
    return ["", "odoo"] if effective_stack == "odoo" else [""]


def regeneration_command(stack_arg: str, runtime: str) -> str:
    return (
        "python3 scripts/cdad-generate.py --runtime %s --stack %s --out <staging-dir>"
        % (runtime, stack_arg)
    )


def build(stack_arg: str, runtime: str) -> dict[str, bytes]:
    if stack_arg == "odoo":
        effective_stack = "odoo"
    elif stack_arg == "generic":
        # Explicit generic resolution (004-001 T4 review-fix: the install-time
        # adapter detects the machine's stack and passes the resolved value —
        # never the state binding hidden behind "auto").
        effective_stack = "generic"
    else:  # auto → resolve from the declared state binding
        effective_stack = "generic"
        state_path = ROOT / "docs" / ".cdad-state.json"
        if state_path.is_file():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                fail(f"cannot read docs/.cdad-state.json for --stack auto: {exc}")
            if state.get("stack") == "odoo":
                effective_stack = "odoo"

    role_sections: dict[str, dict[str, str]] = {}
    for role in ROLES:
        role_sections[role] = parse_source(
            SOURCES / "roles" / f"{role}.md", "role", REQUIRED_ROLE_SECTIONS
        )
    # The orchestrator is a role source too (kind=role id=orchestrator), but its
    # agent is composed differently (§2 composed from all 5 role sources).
    orchestrator_sections = parse_source(
        SOURCES / "roles" / "orchestrator.md", "role", REQUIRED_ROLE_SECTIONS
    )

    # Shared blocks: exactly one editable host each (PD-4); a shared block
    # hosted (or re-hosted) anywhere else is a PD-3 failure.
    shared_blocks: dict[str, str] = {}
    for block, host in SHARED_HOSTS.items():
        found = []
        for sec_name in REQUIRED_ROLE_SECTIONS:
            for name, body in extract_shared_blocks(role_sections[host].get(sec_name, "")):
                if name == block:
                    found.append(body)
        if len(found) != 1:
            fail(
                f"sources/roles/{host}.md: shared block '{block}' must be hosted exactly "
                f"once (PD-4), found {len(found)}"
            )
        shared_blocks[block] = found[0]
    for role in (*ROLES, "orchestrator"):
        sections_map = orchestrator_sections if role == "orchestrator" else role_sections[role]
        for sec_name, content in sections_map.items():
            for name, _ in extract_shared_blocks(content):
                if SHARED_HOSTS.get(name) != role:
                    fail(
                        f"sources/roles/{role}.md: duplicated cdad-shared block '{name}' "
                        f"(hosted by sources/roles/{SHARED_HOSTS.get(name, '?')}.md) — PD-3/PD-4"
                    )

    adapters: dict[str, dict[str, str]] = {}
    for adapter in ("opencode", "claude-code"):
        adapters[adapter] = parse_source(
            SOURCES / "agents" / "adapters" / f"{adapter}.md", "adapter", REQUIRED_ADAPTER_SECTIONS
        )
    globals()["ADAPTER_SECTIONS"] = adapters[runtime]

    artifacts: dict[str, str] = {}
    artifact_sources: dict[str, list[str]] = {}
    adapter_path = f"sources/agents/adapters/{runtime}.md"
    adapter_permissions = adapters[runtime]["permissions"]
    steps = steps_ceiling(adapters[runtime]["frontmatter"]) if runtime == "opencode" else 0

    for stack in role_stack_pairs(effective_stack):
        for role in ROLES:
            bash_lines = bash_policy_lines(
                role, stack, role_sections, adapter_permissions, runtime
            )
            name, text = compose_role_agent(
                role, stack, role_sections[role], shared_blocks, runtime,
                bash_lines,
                steps,
            )
            assert_honesty(text, name)
            artifacts[name] = text
            # PD-4: the manifest references every contributing source — the
            # bash policy of reader/writer classes is composed from the
            # declared host source, not only from the role's own file.
            policy_host = _BASH_POLICY_HOSTS.get(role)
            artifact_sources[f"agents/{runtime}/{name}"] = [
                f"sources/roles/{role}.md",
                *([f"sources/roles/{policy_host}.md"] if policy_host else []),
                adapter_path,
            ]

    name, text = compose_orchestrator_agent(
        orchestrator_sections, role_sections, shared_blocks, runtime,
    )
    assert_honesty(text, name)
    artifacts[name] = text
    artifact_sources[f"agents/{runtime}/{name}"] = [
        "sources/roles/orchestrator.md",
        *[f"sources/roles/{role}.md" for role in ROLES],  # §2 composed from all 5
        adapter_path,
    ]

    manifest = {
        "generator": "scripts/cdad-generate.py",
        "manifest_version": 1,
        "runtime": runtime,
        "stack": effective_stack,
        "stack_arg": stack_arg,
        "artifacts": [
            {
                "file": f"agents/{runtime}/{agent_name}",
                "sha256": hashlib.sha256(artifacts[agent_name].encode("utf-8")).hexdigest(),
                "sources": artifact_sources[f"agents/{runtime}/{agent_name}"],
                "regenerate": regeneration_command(stack_arg, runtime),
            }
            for agent_name in sorted(artifacts)
        ],
    }
    files = {
        f"agents/{runtime}/{agent_name}": artifacts[agent_name].encode("utf-8")
        for agent_name in artifacts
    }
    files["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return files


def merge_staging_manifest(existing_path: Path, fresh: bytes, runtime: str) -> bytes:
    """Staging merge (T5): accumulate per-runtime artifacts in one manifest.

    When <out>/manifest.json already exists (the declared `make staging` flow
    runs one generation per runtime into the same directory), the entries of
    OTHER runtimes are kept verbatim and this runtime's entries are replaced.
    The header records THIS run's resolution. Same-runtime re-runs into the
    same directory remain byte-identical (PD-2). An absent or unreadable
    existing manifest means a fresh staging: the fresh manifest is published
    as-is (PD-3: validation already succeeded before any write).
    """
    prefix = f"agents/{runtime}/"
    kept: list[dict] = []
    if existing_path.is_file():
        try:
            previous = json.loads(existing_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None
        if isinstance(previous, dict) and isinstance(previous.get("artifacts"), list):
            for entry in previous["artifacts"]:
                if (
                    isinstance(entry, dict)
                    and isinstance(entry.get("file"), str)
                    and not entry["file"].startswith(prefix)
                ):
                    kept.append(entry)
    fresh_manifest = json.loads(fresh.decode("utf-8"))
    fresh_manifest["artifacts"] = sorted(
        kept + fresh_manifest["artifacts"], key=lambda e: e["file"]
    )
    return (
        json.dumps(fresh_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


STAGING_COMMAND = (
    "scripts/cdad-generate.py --runtime <opencode|claude-code> "
    "--stack <auto|generic|odoo> --out <staging-dir>"
)

PROFILE_REJECTED_MSG = (
    "ERROR: `--profile` (and any profile name) is no longer a generator option: "
    "the generator and the installer have no model profiles and no model map "
    "(006-003 PD-1f/PD-1c). The model of a role is the one configured in the "
    "runtime, and external delegation takes it from the delegation configuration "
    "(delegation.json, per destination and role). Run: " + STAGING_COMMAND
)


def main(argv: list[str] | None = None) -> int:
    args_in = list(sys.argv[1:] if argv is None else argv)
    # PD-1f: the option is REJECTED explicitly (rc != 0) with a diagnostic that
    # names it and points at the delegation configuration — never a silent
    # "unrecognized argument" and never an accepted no-op.
    if any(a == "--profile" or a.startswith("--profile=") for a in args_in):
        print(PROFILE_REJECTED_MSG, file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser(
        prog="cdad-generate.py", description=__doc__.splitlines()[0]
    )
    parser.add_argument("--runtime", required=True, choices=("opencode", "claude-code"))
    parser.add_argument("--stack", required=True, choices=("auto", "generic", "odoo"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args(args_in)

    try:
        files = build(args.stack, args.runtime)
    except GenerateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    out_root = Path(args.out)
    files["manifest.json"] = merge_staging_manifest(
        out_root / "manifest.json", files["manifest.json"], args.runtime
    )
    for rel, content in sorted(files.items()):
        target = out_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    print(
        "cdad-generate: %d files -> %s (+ manifest.json)"
        % (len(files), out_root / "agents" / args.runtime)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
