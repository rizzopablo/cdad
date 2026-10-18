#!/usr/bin/env python3
"""RED tests for 004-001 T4: OpenCode adapter simplification (spec §2 contract).

Black-box tests: the generator `scripts/cdad-generate.py` is invoked as a
subprocess and only its published outputs are inspected. Mappings to the
approved contract (spec.md §2 + plan.md T4 row):

- test_postcondition_1a_* → PD-1 (bash policy per role is DERIVED from the
  canonical source; no rules retained without source justification; the
  landing-0 `wc` measurement pair is subsumed into the source)
- test_postcondition_1b_* → PD-1 ("pares completos": every allow the writer
  source declares as a complete pair is emitted with BOTH halves, ADR-009)
- test_postcondition_16_* → PD-16/R3 CONTROL: the architect/test-writer intake
  R3 correction is single-sourced in the canonical sources and propagates to
  both runtimes. Control is expected GREEN today (already landed by T2/T3);
  it isolates the RED verdicts above to the missing T4 behavior itself.

Installation is unchanged in T4 (cierre del aterrizaje A): no test touches
install.sh behavior; the suite runs from the repo root as today.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"

STACK = "odoo"
# 006-003 U1/PD-1f: el generador no tiene `--profile` (constante retirada).
RUNTIME = "opencode"  # T4 scope: OpenCode adapters first (plan.md T4)

ARCHITECT_SOURCE = REPO_ROOT / "sources" / "roles" / "architect.md"
TEST_WRITER_SOURCE = REPO_ROOT / "sources" / "roles" / "test-writer.md"
ADAPTER_SOURCE = REPO_ROOT / "sources" / "agents" / "adapters" / "opencode.md"

# Permissive operational policy (owner decision 2026-09-29, spec
# docs/specs/permissive-bash-policy-2026-09-29/spec.yaml): the composed bash
# block is EXACTLY the catch-all allow — no other operation rules exist.
CATCH_ALL_RULE = '"*": allow'
CATCH_ALL_DECL = 'rule "*"'
ROLE_AGENTS = (
    "cdad-architect", "cdad-test-writer", "cdad-implementer",
    "cdad-reviewer", "cdad-scribe",
)


def make_sandbox(base: Path) -> Path:
    """Sandbox copy of sources/ plus the generator.

    Same pattern as the T3 suite: the real sources/ is never mutated; the
    mutation cases run a COPY of the generator inside the sandbox. 006-003
    PD-1c: there is no model map to copy any more.
    """
    sandbox = base / "sandbox"
    sandbox.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "sources", sandbox / "sources")
    (sandbox / "scripts").mkdir()
    shutil.copy2(GENERATOR, sandbox / "scripts" / GENERATOR.name)
    return sandbox


def run_generator(
    out_dir: Path,
    *,
    sandbox: Path | None = None,
    runtime: str = RUNTIME,
    stack: str = STACK,
) -> subprocess.CompletedProcess[str]:
    generator = (sandbox or REPO_ROOT) / "scripts" / GENERATOR.name
    return subprocess.run(
        [
            sys.executable,
            str(generator),
            "--runtime",
            runtime,
            "--stack",
            stack,
            "--out",
            str(out_dir),
        ],
        cwd=str(sandbox or REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def bash_block(agent_text: str) -> str:
    """Extract the nested `permission.bash` block of a generated agent."""
    fm_end = agent_text.index("\n---", agent_text.index("---") + 3)
    frontmatter = agent_text[:fm_end]
    start = frontmatter.index("  bash:")
    lines = frontmatter[start:].splitlines()[1:]
    block = []
    for line in lines:
        if line.startswith("    "):
            block.append(line)
        else:
            break
    return "\n".join(block)


def frontmatter(agent_text: str) -> str:
    """The YAML frontmatter (between the first two `---` delimiters)."""
    parts = agent_text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("generated agent has no delimited frontmatter")
    return parts[1]


def allow_rules(agent_text: str) -> dict[str, str]:
    """Map rule pattern -> verb. A bare `*` (catch-all) keeps its key;
    trailing wildcards are stripped for the other patterns."""
    rules: dict[str, str] = {}
    for line in bash_block(agent_text).splitlines():
        m = re.match(r'^    "(.*)": (allow|deny)$', line)
        if m:
            pattern = m.group(1)
            cmd = pattern[:-1].strip() if pattern.endswith("*") and len(pattern) > 1 else pattern
            rules[cmd] = m.group(2)
    return rules


class TestOpencodeAdapterSimplification(unittest.TestCase):
    """T4 contract: the bash block is generated from the canonical sources."""

    def test_postcondition_1a_bash_policy_is_derived_from_the_canonical_sources(
        self,
    ) -> None:
        """PD-1/PD-3: the permissive bash policy is DERIVED from the canonical
        sources and never silent.

        Behavioral probes (owner decision 2026-09-29, spec
        docs/specs/permissive-bash-policy-2026-09-29/spec.yaml):
        1. Every generated role agent's bash block is EXACTLY the catch-all
           allow — no other operation rules.
        2. Removing the `rule "*"` declaration from a host source makes the
           generator FAIL LOUDLY (PD-3, non-zero exit, diagnostic naming the
           source) — the policy is never silently empty.
        """
        with tempfile.TemporaryDirectory(prefix="cdad-t4-derivation-") as tmp:
            base = Path(tmp)

            # Case 1: all role agents carry exactly one rule — the catch-all.
            with self.subTest(case="all-roles-single-catch-all"):
                out = base / "full" / "staging"
                result = run_generator(out)
                self.assertEqual(
                    result.returncode,
                    0,
                    "T4 control: generator run failed: %s" % result.stderr,
                )
                for name in ROLE_AGENTS:
                    generated = (out / "agents" / "opencode" / f"{name}.md").read_text(
                        encoding="utf-8"
                    )
                    rules = allow_rules(generated)
                    self.assertEqual(
                        rules,
                        {"*": "allow"},
                        "PD-1/permissive: %s must carry EXACTLY the catch-all "
                        "allow (owner decision 2026-09-29); got %r" % (name, rules),
                    )

            # Case 2: the host source's catch-all declaration is load-bearing.
            with self.subTest(case="missing-declaration-fails-loudly"):
                for host, role_agent in (
                    (ARCHITECT_SOURCE, "cdad-reviewer"),
                    (TEST_WRITER_SOURCE, "cdad-test-writer"),
                ):
                    sandbox = make_sandbox(base / host.stem)
                    src = sandbox / "sources" / "roles" / host.name
                    text = src.read_text(encoding="utf-8")
                    mutated = text.replace(CATCH_ALL_DECL, "rule \"placeholder\"")
                    self.assertNotEqual(
                        mutated,
                        text,
                        "fixture drift: %s no longer declares %r"
                        % (host, CATCH_ALL_DECL),
                    )
                    src.write_text(mutated, encoding="utf-8")
                    out = base / host.stem / "staging"
                    result = run_generator(out, sandbox=sandbox)
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        "PD-3: the generator accepted %s without the permissive "
                        "policy declaration — the policy would be silent" % host,
                    )
                    self.assertIn(
                        "PD-3",
                        result.stderr,
                        "PD-3: the failure diagnostic must name the policy "
                        "contract (got: %s)" % result.stderr,
                    )
                    self.assertFalse(
                        (out / "agents" / "opencode" / f"{role_agent}.md").exists(),
                        "PD-3: zero published files on failure (%s was written)"
                        % role_agent,
                    )

    def test_postcondition_1b_path_barriers_are_retained_in_the_generated_agents(
        self,
    ) -> None:
        """The permissive bash layer does NOT weaken the PATH barriers
        (owner decision 2026-09-29: the retained guard is edit/read scope).

        - Readers (architect/reviewer/scribe): permission.edit deny.
        - test-writer: edit allows tests paths only; read/grep keep the
          implementation invisible (src/**, lib/** + odoo variants).
        - implementer: edit catch-all ALLOW with tests blocklist; the odoo
          variant keeps the tests blocklist WITHOUT the models/views/
          controllers/wizards denial (bugfix 2026-09-29: those are the
          implementer's OWN scope).
        """
        with tempfile.TemporaryDirectory(prefix="cdad-t4-paths-") as tmp:
            out = Path(tmp) / "staging"
            result = run_generator(out)
            self.assertEqual(
                result.returncode,
                0,
                "T4 control: generator run failed: %s" % result.stderr,
            )
            for name in ("cdad-architect", "cdad-reviewer", "cdad-scribe"):
                with self.subTest(agent=name):
                    fm = frontmatter(
                        (out / "agents" / "opencode" / f"{name}.md").read_text(
                            encoding="utf-8"
                        )
                    )
                    self.assertIn("edit: deny", fm)
            tw = (out / "agents" / "opencode" / "cdad-test-writer.md").read_text(
                encoding="utf-8"
            )
            self.assertIn('"tests/**": allow', tw)
            self.assertIn('"src/**": deny', tw)
            self.assertIn('"lib/**": deny', tw)
            for name in ("cdad-implementer", "cdad-implementer-odoo"):
                with self.subTest(agent=name):
                    text = (out / "agents" / "opencode" / f"{name}.md").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn('"*": allow', text)
                    self.assertIn('"tests/**": deny', text)
                    self.assertNotIn(
                        '"**/models/**": deny',
                        text,
                        "%s must NOT deny models/** — that is the implementer's "
                        "own scope (bugfix 2026-09-29)" % name,
                    )
            two = (
                out / "agents" / "opencode" / "cdad-test-writer-odoo.md"
            ).read_text(encoding="utf-8")
            self.assertIn('"**/models/**": deny', two)

    def test_postcondition_16_r3_intake_correction_is_single_sourced_and_propagated(
        self,
    ) -> None:
        """PD-16/R3 CONTROL (expected GREEN today): the architect/test-writer
        intake legacy-loads correction is declared ONCE per role in the
        canonical sources and propagates to the generated agents of BOTH
        runtimes.
        """
        self.assertIn(
            "R3 fix",
            ARCHITECT_SOURCE.read_text(encoding="utf-8"),
            "PD-16/R3: the architect canonical source lost the R3 correction",
        )
        legacy_loads_re = re.compile(
            r"legacy-loads:\s*`cdad-cycle`\s*\+\s*`cdad-spec-and-test`"
        )
        for source in (ARCHITECT_SOURCE, TEST_WRITER_SOURCE):
            self.assertIsNotNone(
                legacy_loads_re.search(source.read_text(encoding="utf-8")),
                "PD-16/R3: %s lost the cdad-spec-and-test legacy load" % source.name,
            )
        for runtime in ("opencode", "claude-code"):
            with self.subTest(runtime=runtime):
                with tempfile.TemporaryDirectory(
                    prefix="cdad-t4-r3-control-"
                ) as tmp:
                    out = Path(tmp) / "staging"
                    result = run_generator(out, runtime=runtime)
                    self.assertEqual(
                        result.returncode,
                        0,
                        "T4 control: generator run failed: %s" % result.stderr,
                    )
                    for name in ("cdad-architect.md", "cdad-test-writer.md"):
                        generated = (
                            out / "agents" / runtime / name
                        ).read_text(encoding="utf-8")
                        self.assertIsNotNone(
                            legacy_loads_re.search(generated),
                            "PD-16/R3: %s/%s lost the cdad-spec-and-test "
                            "legacy load" % (runtime, name),
                        )


if __name__ == "__main__":
    unittest.main()
