#!/usr/bin/env python3
"""RED tests for 004-001 T4 reviewfix-RED (review-2 R2-B1 + review-1 B1 regression).

Two small behavior-level tests, no per-command battery (review-2 correction
about test debt). Black-box contract: `scripts/cdad-bash-allowlist.sh` and
`scripts/cdad-generate.py` are invoked as subprocesses and only their published
outputs are inspected. NO implementation file is read by this module.

Mappings to the approved contract (spec.md §2, PD-1) + review-2 R2-B1
(documented in docs/specs/004-001-canonical-runtime-artifacts/review-2.md)
+ review-1 B1 regression (fixed in be06c94):

- test_postcondition_1_adapter_selects_the_specialized_variant_for_odoo_stack
  → PD-1 preservation of the Odoo specialization: with `--stack odoo` the
    bash-policy adapter must extract the policy of the SPECIALIZED variant
    resolved for the stack and stay at parity with that variant. Contrast
    (RED today): at `297a77a` the adapter always extracts the generic variant
    and loses the odoo-declared `pylint` / `pre-commit` permits, including
    their rtk pairs (review-2 R2-B1, provenance scripts/cdad-bash-allowlist.sh:139).

- test_postcondition_1_generated_outputs_have_no_double_git_prefix
  → PD-1 (complete pairs emitted once, correctly expanded): the generated bash
    blocks of architect/reviewer/scribe — generic AND `-odoo` variants — must
    not contain a doubled `git git` prefix. review-1 B1 regression already
    fixed in `be06c94`; this test is expected GREEN (regression coverage).

Run from the repository root (cdad/):
    python3 -m pytest tests/test_bash_policy_selection.py -q
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"
ALLOWLIST = REPO_ROOT / "scripts" / "cdad-bash-allowlist.sh"

RUNTIME = "opencode"  # T4 scope: OpenCode adapters first (plan.md T4 row)
STACK = "odoo"
PROFILE = "optimus"

# Role used for the adapter-selection reproduction (review-2 R2-B1 was
# reproduced with `implementer --stack odoo` and with `implementer-odoo`).
ADAPTER_ROLE = "implementer"

# Git-expansion regression from review-1 B1: the doubled prefix corrupted the
# bash blocks derived from these roles' sources.
DOUBLE_PREFIX_ROLES = ("architect", "reviewer", "scribe")

# Permissive operational policy (owner decision 2026-09-29, spec
# docs/specs/permissive-bash-policy-2026-09-29/spec.yaml): the composed block
# is EXACTLY the catch-all allow — the former odoo-declared pylint/pre-commit
# permits and the toolchain tail are RETIRED (redundant under the catch-all).
CATCH_ALL_RULE = '"*": allow'


def run_allowlist(*args: str) -> subprocess.CompletedProcess[str]:
    """Invoke the bash-policy adapter black-box (published stdout only)."""
    return subprocess.run(
        ["bash", str(ALLOWLIST), *args],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def run_generator(out_dir: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the generator black-box with the odoo stack resolved."""
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--runtime",
            RUNTIME,
            "--stack",
            STACK,
            "--profile",
            PROFILE,
            "--out",
            str(out_dir),
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def parse_bash_rules(text: str) -> dict[str, str]:
    """Map emitted rule command -> verb (allow/deny) from adapter stdout."""
    rules: dict[str, str] = {}
    for match in re.finditer(r'"([^"]*)"\s*:\s*(allow|deny)', text):
        rules[match.group(1)] = match.group(2)
    return rules




def bash_block(agent_text: str) -> str:
    """Extract the nested `permission.bash` block of a generated agent.

    Same black-box extraction as tests/test_cdad_adapters_opencode.py.
    """
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


class TestBashPolicySelectionReviewfix(unittest.TestCase):
    """004-001 T4 reviewfix-RED: adapter specialization + double-prefix guard."""

    def test_postcondition_1_adapter_selects_the_specialized_variant_for_odoo_stack(
        self,
    ) -> None:
        """PD-1 / review-2 R2-B1: with `--stack odoo` the adapter must extract
        the bash policy of the specialized variant resolved for the stack, at
        parity with it (identical rule set). Under the permissive policy
        (owner decision 2026-09-29) both emissions are EXACTLY the catch-all
        allow — no odoo-specific operation rules remain.
        """
        stack_run = run_allowlist(ADAPTER_ROLE, "--stack", STACK)
        variant_run = run_allowlist(ADAPTER_ROLE + "-odoo")

        # Controls (each with an explicit, behavior-level message so any
        # non-assertion-environment failure is diagnosable and attributable):
        with self.subTest(control="adapter-accepts-resolved-stack-flag"):
            self.assertEqual(
                stack_run.returncode,
                0,
                "PD-1/R2-B1: the bash-policy adapter must accept the resolved "
                "stack ('--stack %s' for role '%s') — it exited %s: %s"
                % (STACK, ADAPTER_ROLE, stack_run.returncode, stack_run.stderr),
            )
        with self.subTest(control="specialized-variant-path-usable"):
            self.assertEqual(
                variant_run.returncode,
                0,
                "PD-1/R2-B1: the specialized variant path ('%s-odoo') must be "
                "usable by the adapter — it exited %s: %s"
                % (ADAPTER_ROLE, variant_run.returncode, variant_run.stderr),
            )

        stack_rules = parse_bash_rules(stack_run.stdout)
        variant_rules = parse_bash_rules(variant_run.stdout)

        # Postcondition 1: parity — the policy emitted for the resolved
        # odoo stack IS the specialized variant's policy (same rule set).
        with self.subTest(
            postcondition="adapter-parity-with-specialized-variant"
        ):
            self.assertEqual(
                stack_rules,
                variant_rules,
                "PD-1/R2-B1: with --stack %s the adapter extracts the GENERIC "
                "variant instead of the specialized one (provenance "
                "scripts/cdad-bash-allowlist.sh, commit 297a77a): "
                "stack-emitted rules %r != specialized-variant rules %r"
                % (STACK, sorted(stack_rules.items()), sorted(variant_rules.items())),
            )

        # Postcondition 2: permissive policy — both emissions carry exactly
        # the catch-all allow (owner decision 2026-09-29; the former
        # odoo-declared pylint/pre-commit permits are retired).
        for label, rules in (
            ("stack-odoo-emitted", stack_rules),
            ("specialized-variant", variant_rules),
        ):
            with self.subTest(label=label):
                self.assertEqual(
                    rules,
                    {"*": "allow"},
                    "PD-1/permissive: %s output must be EXACTLY the catch-all "
                    "allow (owner decision 2026-09-29); got %r" % (label, rules),
                )

    def test_postcondition_1_generated_outputs_have_no_double_git_prefix(
        self,
    ) -> None:
        """PD-1 / review-1 B1 regression (fixed in be06c94, expected GREEN):
        generator expansion must not re-prefix git companions — no emitted
        bash rule may contain the doubled `git git` prefix, in the generic OR
        the `-odoo` generated variants (review-1 confirmed the defect reached
        the odoo variants).
        """
        with tempfile.TemporaryDirectory(prefix="cdad-t4-rf-gitprefix-") as tmp:
            out = Path(tmp) / "staging"
            result = run_generator(out)
            self.assertEqual(
                result.returncode,
                0,
                "T4 reviewfix control: generator run failed "
                "(black-box probe, no source inspected): %s" % result.stderr,
            )
            for role in DOUBLE_PREFIX_ROLES:
                for name in ("cdad-%s.md" % role, "cdad-%s-odoo.md" % role):
                    with self.subTest(agent=name):
                        path = out / "agents" / RUNTIME / name
                        self.assertTrue(
                            path.is_file(),
                            "T4 reviewfix control: the generator did not emit "
                            "%s (cannot protect the review-1 B1 regression)"
                            % path.name,
                        )
                        block = bash_block(path.read_text(encoding="utf-8"))
                        self.assertNotIn(
                            "git git",
                            block,
                            "PD-1/review-1 B1 regression: %s reintroduces the "
                            "doubled 'git git' prefix in its generated bash "
                            "block" % name,
                        )


if __name__ == "__main__":
    unittest.main()
