#!/usr/bin/env python3
"""cdad-doctrine-check — executable verification of the tests-by-contract doctrine.

Contract: docs/specs/008-006-contract-not-coverage/spec.md
(§"Siete reglas, siete hogares", PC-1..PC-6, AJ1-AJ4).

The doctrine lives in seven editable homes. This script is a CONSUMER of them
and never a second definition: it holds no rule text, only the markers that
prove a home still declares its rule. It fails closed:

- a home that cannot be read is a violation, never a skip;
- a marker missing from its home is a violation;
- a retired quota ("one test per (numbered) postcondition", "MINIMAL CODE", "the
  simplest implementation that makes the test pass") reappearing in sources,
  generated agents or the cycle's skill text is a violation;
- a template that loses `deferred-hardening` (or its promise/audit pointer) is a
  violation;
- a generated agent that lost the doctrine of its role, or that fixes a model,
  is a violation;
- a declared artifact missing from either runtime's generated set is a violation
  (both directories, every role): absence is never reported as success.

Usage:
    python3 scripts/cdad-doctrine-check.py [--repo-root PATH] [--quiet]

Exit codes: 0 every check passed; 1 at least one violation (diagnostics on
stderr, nothing on stdout except the summary); 2 usage error.

Scope limit (declared, PD-15): this verifies PRESENCE — the contractual markers of
each home, the declared generated artifacts of both runtimes, and the absence of
retired quotas. It does not prove integrity: it never judges the truth or
sufficiency of a user consequence (that judgment belongs to the review and the
gate, with recorded evidence), and it never proves a generated agent is
byte-equivalent to a fresh regeneration from the sources (that is `make agents`
plus the generation regressions).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_OK = 0
EXIT_VIOLATION = 1

SHARED_BLOCK_OPEN = "<!-- cdad-shared:%s -->"
SHARED_BLOCK_CLOSE = "<!-- /cdad-shared -->"


@dataclass(frozen=True)
class Home:
    """One rule and the markers its single editable home must keep declaring."""

    rule: str
    path: str
    requires: tuple[str, ...]
    shared_block: str | None = None


HOMES: tuple[Home, ...] = (
    Home(
        "R1 (specification)",
        "sources/roles/architect.md",
        ("observable promise", "same observable result", "deferred-hardening"),
    ),
    Home(
        "R2 (selection and justification)",
        "sources/roles/test-writer.md",
        (
            "observable promise",
            "without this test, the user",
            "postconditions it protects",
        ),
        shared_block="convention-rule",
    ),
    Home(
        "R3 (test findings)",
        "sources/roles/reviewer.md",
        ("user consequence", "deferred-hardening", "never restate it here"),
    ),
    Home(
        "R4 (gate and promotions)",
        "sources/roles/orchestrator.md",
        (
            "what breaks for the user without this test",
            "recorded reason",
            "security",
            "integrity",
        ),
    ),
    Home(
        "R5 (code robustness)",
        "sources/roles/implementer.md",
        ("reasonable robustness", "speculative", "even when no test demands them"),
    ),
    Home(
        "R6 (deferral persistence)",
        "sources/roles/scribe.md",
        ("deferred-hardening", "closure draft", "never omit it silently"),
    ),
    Home(
        "R7 (acceptance counterweight)",
        "skills/cdad-cycle/references/stage-3-tdd.md",
        (
            "reducing redundancy reduces the",
            "one test may verify several postconditions",
            "never allows postponing a committed promise",
        ),
    ),
)

# The quota and the restriction that 008-006 retires. A reappearance anywhere in
# the editable text (sources, generated agents, the cycle's skill) fails closed.
RETIRED: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\bMINIMAL\s+CODE\b"),
        "the retired 'MINIMAL CODE' restriction (R5 forbids limiting robustness)",
    ),
    (
        re.compile(r"(?i)minimal\s+code\s+that\s+makes\s+the\s+(?:approved\s+)?test\s+pass"),
        "the retired 'minimal code that makes the test pass' (R5)",
    ),
    (
        re.compile(r"(?i)simplest\s+implementation\s+that\s+makes\s+the\s+test\s+pass"),
        "the retired 'simplest implementation that makes the test pass' (R5)",
    ),
    (
        re.compile(r"(?i)one\s+test\s+per\s+(?:numbered\s+)?postconditions?\b"),
        "the retired quota 'one test per (numbered) postcondition' (R2 selects by promise)",
    ),
)

SCAN_ROOTS = ("sources/roles", "agents", "skills/cdad-cycle")
SCAN_SUFFIXES = (".md",)

SPEC_TEMPLATE = "skills/cdad-cycle/assets/spec-template/spec.md"
AUDIT_TEMPLATE = "skills/cdad-cycle/assets/spec-template/test-audit.md"
PLAN_TEMPLATE = "skills/cdad-cycle/assets/feature-plan-template.md"
PLAN_TASKS_FENCE = re.compile(r"(?m)^[ \t]{0,3}```plan-tasks[ \t]*$")

AGENT_DIRS = ("agents", "agents/claude-code")
MODEL_LINE = re.compile(r"(?m)^model\s*:")
AGENT_DOCTRINE: dict[str, str] = {
    "architect": "observable promise",
    "test-writer": "without this test, the user",
    "implementer": "reasonable robustness",
    "reviewer": "user consequence",
    "orchestrator": "what breaks for the user without this test",
    "scribe": "deferred-hardening",
}
# The declared artifact set of EACH runtime: every role of AGENT_DOCTRINE plus the
# `-odoo` variant of each stack-specializable role (the orchestrator has none).
# Mirrors scripts/cdad-generate.py (ROLES x role_stack_pairs("odoo"), the stack
# `make agents` publishes): an artifact absent from either directory is a
# violation, never a silent skip.
ORCHESTRATOR = "orchestrator"
EXPECTED_AGENTS: frozenset[str] = frozenset(
    ["cdad-%s.md" % role for role in AGENT_DOCTRINE]
    + [
        "cdad-%s-odoo.md" % role
        for role in AGENT_DOCTRINE
        if role != ORCHESTRATOR
    ]
)


class Unreadable(Exception):
    """A file the check must read is missing or unreadable (fail closed)."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise Unreadable("%s: cannot read (%s)" % (path, exc)) from exc


def normalized(text: str) -> str:
    """Collapse whitespace so a marker survives the source's line wrapping."""
    return re.sub(r"\s+", " ", text).lower()


def shared_block(text: str, name: str) -> str | None:
    start = text.find(SHARED_BLOCK_OPEN % name)
    if start < 0:
        return None
    end = text.find(SHARED_BLOCK_CLOSE, start)
    if end < 0:
        return None
    return text[start:end]


def check_homes(root: Path) -> list[str]:
    violations: list[str] = []
    for home in HOMES:
        path = root / home.path
        try:
            text = read_text(path)
        except Unreadable as exc:
            violations.append("%s: home does not exist/unreadable — %s" % (home.rule, exc))
            continue
        if home.shared_block is not None:
            block = shared_block(text, home.shared_block)
            if block is None:
                violations.append(
                    "%s: %s lost the shared block '%s' (the rule must live there)"
                    % (home.rule, home.path, home.shared_block)
                )
                continue
            text = block
        lowered = normalized(text)
        for marker in home.requires:
            if normalized(marker) not in lowered:
                violations.append(
                    "%s: %s does not declare its rule — missing marker %r"
                    % (home.rule, home.path, marker)
                )
    return violations


def scan_retired(root: Path) -> tuple[list[str], int]:
    violations: list[str] = []
    scanned = 0
    for rel_root in SCAN_ROOTS:
        base = root / rel_root
        if not base.is_dir():
            violations.append("scan root does not exist: %s" % rel_root)
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            scanned += 1
            try:
                text = read_text(path)
            except Unreadable as exc:
                violations.append("unreadable file in scope — %s" % exc)
                continue
            for pattern, reason in RETIRED:
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    violations.append(
                        "%s:%d: %s" % (path.relative_to(root), line, reason)
                    )
    return violations, scanned


def check_templates(root: Path) -> list[str]:
    violations: list[str] = []
    try:
        spec = read_text(root / SPEC_TEMPLATE)
        audit = read_text(root / AUDIT_TEMPLATE)
        plan = read_text(root / PLAN_TEMPLATE)
    except Unreadable as exc:
        return ["template does not exist/unreadable — %s" % exc]

    if not re.search(r"(?m)^#{2,6}\s+deferred-hardening\s*$", spec):
        violations.append(
            "%s: no '## deferred-hardening' heading (R1: every spec carries it)"
            % SPEC_TEMPLATE
        )
    if "observable promise" not in normalized(spec):
        violations.append(
            "%s: the contract does not group postconditions by observable promise (R1)"
            % SPEC_TEMPLATE
        )
    if "without this test, the user" not in normalized(audit):
        violations.append(
            "%s: no 'without this test, the user' declaration (R2)" % AUDIT_TEMPLATE
        )
    if "postconditions protected" not in normalized(audit):
        violations.append(
            "%s: no 'postconditions protected' traceability (R2)" % AUDIT_TEMPLATE
        )
    if "deferred-hardening" not in normalized(plan):
        violations.append(
            "%s: the plan does not reference the spec's deferred-hardening (PC-1)"
            % PLAN_TEMPLATE
        )
    if "promise" not in normalized(plan):
        violations.append(
            "%s: the plan does not reference the spec's promises (PC-1)" % PLAN_TEMPLATE
        )
    fences = len(PLAN_TASKS_FENCE.findall(plan))
    if fences != 1:
        violations.append(
            "%s: expected exactly 1 canonical plan-tasks block (schema unchanged), found %d"
            % (PLAN_TEMPLATE, fences)
        )
    return violations


def check_agents(root: Path) -> tuple[list[str], int]:
    """Every runtime must carry the declared artifact set, each with its role marker."""
    violations: list[str] = []
    scanned = 0
    for rel_dir in AGENT_DIRS:
        base = root / rel_dir
        if not base.is_dir():
            violations.append("generated agents directory does not exist: %s" % rel_dir)
            continue
        present = {path.name for path in base.glob("cdad-*.md") if path.is_file()}
        for name in sorted(EXPECTED_AGENTS - present):
            violations.append(
                "%s: missing declared artifact %s (PC-6: every runtime receives every role)"
                % (rel_dir, name)
            )
        for path in sorted(base.glob("cdad-*.md")):
            if not path.is_file():
                continue
            scanned += 1
            rel = path.relative_to(root)
            try:
                text = read_text(path)
            except Unreadable as exc:
                violations.append("unreadable agent — %s" % exc)
                continue
            if MODEL_LINE.search(text):
                violations.append("%s: fixes a model: line (model policy preserved)" % rel)
            role = next(
                (name for name in AGENT_DOCTRINE if path.stem.startswith("cdad-%s" % name)),
                None,
            )
            if role is None:
                violations.append("%s: role not declared in AGENT_DOCTRINE" % rel)
                continue
            marker = AGENT_DOCTRINE[role]
            if normalized(marker) not in normalized(text):
                violations.append(
                    "%s: the generated %s agent lost the doctrine — missing marker %r"
                    % (rel, role, marker)
                )
    return violations, scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify the tests-by-contract doctrine of 008-006 (fail closed).",
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="repository root (default: the parent of scripts/)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print nothing on success",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        print("cdad-doctrine-check: repo root does not exist: %s" % root, file=sys.stderr)
        return EXIT_VIOLATION

    violations = check_homes(root)
    scan_violations, scanned = scan_retired(root)
    agent_violations, agents = check_agents(root)
    violations += scan_violations + check_templates(root) + agent_violations

    if violations:
        print(
            "cdad-doctrine-check: %d violation(s) — a marker, an artifact or a "
            "retirement is missing (presence check, not full integrity):" % len(violations),
            file=sys.stderr,
        )
        for violation in violations:
            print("  - %s" % violation, file=sys.stderr)
        return EXIT_VIOLATION

    if not args.quiet:
        print(
            "cdad-doctrine-check: OK — presence check, not full integrity: "
            "%d homes declare their markers, %d files scanned for retired quotas, "
            "%d/%d declared generated artifacts present with their role marker"
            % (
                len(HOMES),
                scanned,
                agents,
                len(AGENT_DIRS) * len(EXPECTED_AGENTS),
            )
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
