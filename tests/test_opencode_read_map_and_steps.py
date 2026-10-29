#!/usr/bin/env python3
"""RED tests for the light cycle `opencode-read-map-and-steps` (2026-09-29).

Contract: docs/specs/opencode-read-map-and-steps-2026-09-29/spec.yaml (legacy
handoff: the contract is that file, not an approved feature spec).

Black-box: `scripts/cdad-generate.py` and `install.sh` are invoked as
subprocesses and only their published outputs are inspected. NO implementation
file is read by this module. The ONLY implementation-tree file read is
`sources/agents/adapters/opencode.md`, which the spec itself declares a
DECLARATION SOURCE (machine-readable `steps: 300` line), not code — the spec
postconditions P2/P3 are defined against it.

Test -> postcondition mapping (spec.yaml `verification`):

  test_p1_read_map_no_catch_all_and_probes         -> P1 (read map, both variants)
  test_p2_steps_declared_on_role_agents_only       -> P2 (10 role agents + orchestrator)
  test_p3_fail_loud_when_steps_declaration_invalid -> P3 (PD-3 fail-loud)
  test_p4_install_preserves_steps_line             -> P4 (install preserves `steps`)

Controls (labeled, expected GREEN today and useful as regressions): the
implementation-path DENY probes on src/app.py / lib/x.py (generic) and
addons/m/models|views (odoo) — the catch-all deny makes them pass today; the
postcondition keeps them true after the fix. The orchestrator-has-no-steps
check is also a control today.

Run from the repository root (cdad/):
    python3 -m pytest tests/test_opencode_read_map_and_steps.py -q
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agent_frontmatter import permissions

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"
ADAPTER_DECL = REPO_ROOT / "sources" / "agents" / "adapters" / "opencode.md"
INSTALLER = REPO_ROOT / "install.sh"

RUNTIME = "opencode"
STACK = "odoo"  # an odoo run emits BOTH the base and the -odoo variants
# 006-003 U1/PD-1f: el generador no tiene `--profile` (constante retirada);
# los agentes ya no traen `model:`, así que el oráculo de este archivo
# (bloques de permisos/read-map) no depende de un perfil.

ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")


def frontmatter(agent_text: str) -> str:
    """Return serialized frontmatter through the closing delimiter/newline."""
    parts = agent_text.split("---", 2)
    if len(parts) != 3:
        raise AssertionError("generated agent has no delimited frontmatter")
    return "---" + parts[1] + "---\n"


RULE_RE = re.compile(r'^\s*"([^"\n]*)"\s*:\s*(allow|deny|ask)\s*$')


def test_shared_frontmatter_helpers_preserve_importer_contract():
    """PC-1/PC-2 compatibility: shared consumers need the delimiters and regex.

    Without this compatibility contract, t5 slices the body at the wrong byte
    boundary and t7 cannot import its shared rule matcher.
    """
    text = "---\nname: sample\n---\nbody\n"
    parsed = frontmatter(text)
    assert parsed == "---\nname: sample\n---\n"
    assert "RULE_RE" in globals(), "t7 importer requires shared RULE_RE"
    assert isinstance(RULE_RE, re.Pattern)

# --- P1 probe set (spec P1, verbatim paths) --------------------------------
ALLOW_PROBES = (
    "docs/specs/x/spec.md",
    "tests/test_a.py",
    "README.md",
    "src/pkg/test_a.py",  # colocated test exception
)
DENY_PROBES_BASE = ("src/app.py", "lib/x.py")
DENY_PROBES_ODOO = ("addons/m/models/a.py", "addons/m/views/v.xml")

# The `steps` declaration the implementer must create in the adapter source:
# a line inside the frontmatter section containing exactly the code span
# `steps: 300` (regex `steps:\s*(\d+)` inside backticks).
STEPS_DECL_RE = re.compile(r"steps:\s*(\d+)")
STEPS_LINE_RE = re.compile(r"^steps:\s*(\d+)\s*$")


# --- harness ----------------------------------------------------------------
def run_generator(cwd: Path, out_dir: Path) -> subprocess.CompletedProcess[str]:
    """Invoke the generator black-box as a subprocess."""
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--runtime", RUNTIME,
            "--stack", STACK,
            "--out", str(out_dir),
        ],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def read_map(agent_text: str) -> list[tuple[str, str]]:
    """The V2 read rules as (resource, effect), preserving serialized order."""
    return [(rule["resource"], rule["effect"])
            for rule in permissions(agent_text) if rule["action"] == "read"]


def glob_to_regex(pattern: str) -> str:
    """Pattern -> regex: `*` -> `.*`, `?` -> `.`, every other char escaped."""
    return "".join(
        ".*" if c == "*" else "." if c == "?" else re.escape(c)
        for c in pattern
    )


def evaluate(rules: list[tuple[str, str]], path: str) -> str:
    """findLast semantics: the LAST matching rule wins; none -> ALLOW."""
    verdict = "allow"  # no matching rule means ALLOW
    for pattern, verb in rules:
        if re.fullmatch(glob_to_regex(pattern), path):
            verdict = verb
    return verdict


def read_steps_declaration() -> str:
    """The declared `steps: N` value in the adapter declaration source.

    That file is a DECLARATION source (spec P2/P3 define the contract against
    it), not implementation code — this is the spec-authorized read.
    """
    text = ADAPTER_DECL.read_text(encoding="utf-8")
    m = STEPS_DECL_RE.search(text)
    if not m:
        raise AssertionError(
            "P2/P3 contract: the adapter declaration source "
            f"{ADAPTER_DECL.relative_to(REPO_ROOT)} must declare a machine "
            "readable step ceiling (line `steps: 300` in the frontmatter "
            "section); the declaration is absent"
        )
    return m.group(1)


def assert_steps_line(tc: unittest.TestCase, path: Path, expected: int = 300) -> None:
    """A generated role agent carries exactly one `steps: N` frontmatter line."""
    fm = frontmatter(path.read_text(encoding="utf-8"))
    matches = [m.group(1) for line in fm.splitlines()
               if (m := STEPS_LINE_RE.match(line))]
    tc.assertEqual(
        matches, [str(expected)],
        f"P2 contract: {path.name} frontmatter must declare `steps: "
        f"{expected}` (a forced text-only ceiling for runaway loops); "
        f"found {matches!r}",
    )


def assert_no_steps_line(tc: unittest.TestCase, path: Path, label: str) -> None:
    fm = frontmatter(path.read_text(encoding="utf-8"))
    offenders = [l for l in fm.splitlines() if l.strip().startswith("steps:")]
    tc.assertFalse(
        offenders,
        f"P2 contract: {label} must have no `steps:` line (mode:all, "
        f"long-running); found {offenders!r}",
    )


class GeneratedOutputs(unittest.TestCase):
    """Class fixture: one odoo-stack generator run (base + -odoo variants)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-readmap-steps-")
        cls.out = Path(cls._tmp.name) / "staging"
        result = run_generator(REPO_ROOT, cls.out)
        if result.returncode != 0:
            raise AssertionError(
                "Fixture precondition: the generator run failed (black-box "
                "probe, no source inspected): "
                + (result.stderr or result.stdout)
            )
        cls.agent_dir = cls.out / "agents" / RUNTIME

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def agent_path(self, name: str) -> Path:
        path = self.agent_dir / f"cdad-{name}.md"
        self.assertTrue(
            path.is_file(),
            f"Fixture precondition: the generator did not emit {path.name}",
        )
        return path


class TestP1ReadMap(GeneratedOutputs):
    """P1: the test-writer read map is a deny-list, not an inverted allow-list."""

    def test_p1_read_map_no_catch_all_and_probes(self) -> None:
        """P1 (behavioral oracle, findLast semantics): for cdad-test-writer and
        cdad-test-writer-odoo, the contract/docs paths resolve ALLOW, the
        colocated test under src/ resolves ALLOW, the implementation paths
        resolve DENY, and no rule pattern is exactly `*`.
        """
        cases = [
            ("base", self.agent_path("test-writer"), DENY_PROBES_BASE),
            ("odoo", self.agent_path("test-writer-odoo"), DENY_PROBES_ODOO),
        ]
        for label, path, deny_probes in cases:
            rules = read_map(path.read_text(encoding="utf-8"))
            with self.subTest(variant=label, check="no-catch-all-rule"):
                self.assertNotIn(
                    "*",
                    {pattern for pattern, _ in rules},
                    f"P1 contract: the read map of cdad-test-writer ({label}) "
                    "must not contain the catch-all rule \"*\" — read is a "
                    "deny-list: the contract, docs and tests are readable by "
                    f"default; rules found: {rules!r}",
                )
            for probe in ALLOW_PROBES:
                with self.subTest(variant=label, probe=probe):
                    self.assertEqual(
                        evaluate(rules, probe), "allow",
                        f"P1 contract: cdad-test-writer ({label}) must be able "
                        f"to READ '{probe}' with the read tool (approved "
                        "contract / tests are readable by default); the map "
                        f"resolves it to {evaluate(rules, probe)!r}",
                    )
            for probe in deny_probes:
                with self.subTest(variant=label, probe=probe, control="deny"):
                    self.assertEqual(
                        evaluate(rules, probe), "deny",
                        f"P1 contract (control): cdad-test-writer ({label}) "
                        f"must still DENY the read of '{probe}' "
                        "(implementation paths stay invisible); the map "
                        f"resolves it to {evaluate(rules, probe)!r}",
                    )


class TestP2StepsCeiling(GeneratedOutputs):
    """P2: every OpenCode role subagent declares `steps: 300`; orchestrator none."""

    def test_p2_steps_declared_on_role_agents_only(self) -> None:
        """P2: the 10 generated role agents (5 roles x base/odoo) carry
        `steps: 300` equal to the adapter declaration; the orchestrator
        carries none (control: already true today).
        """
        declared = read_steps_declaration()
        self.assertEqual(
            declared, "300",
            "P2 contract: the adapter declaration source "
            "sources/agents/adapters/opencode.md must declare 300 "
            "(~1.5x the highest legitimate session observed); it declares "
            f"{declared!r}",
        )
        for role in ROLES:
            for name in (f"cdad-{role}.md", f"cdad-{role}-odoo.md"):
                with self.subTest(agent=name):
                    assert_steps_line(self, self.agent_dir / name, 300)
        # Control: the orchestrator (mode: all, long-running) has no steps.
        with self.subTest(agent="cdad-orchestrator.md", control="no-steps"):
            assert_no_steps_line(
                self, self.agent_path("orchestrator"), "the orchestrator"
            )


class TestP3FailLoud(unittest.TestCase):
    """P3 (PD-3): an absent or non-numeric `steps` declaration fails loudly."""

    def _sandbox(self, base: Path) -> Path:
        copy = base / "copy"
        shutil.copytree(
            REPO_ROOT, copy, symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "node_modules",
            ),
        )
        return copy

    def _mutate(self, tree: Path, kind: str) -> None:
        """Remove the `steps:` declaration line, or make it non-numeric.

        Preconditions (harness, AssertionError with a diagnostic if broken):
        the declaration source must exist and the mutation must find a
        placement (an existing line to remove/replace, or the frontmatter
        section marker to insert after).
        """
        decl = tree / "sources" / "agents" / "adapters" / "opencode.md"
        self.assertTrue(decl.is_file(), f"P3 harness: {decl} missing")
        text = decl.read_text(encoding="utf-8")
        if kind == "remove":
            new_lines = [l for l in text.splitlines()
                         if not STEPS_DECL_RE.search(l)]
            if len(new_lines) == len(text.splitlines()):
                # Declaration already absent: the tree is ALREADY in the
                # "removed" state (the defect this cycle fixes), so the
                # mutation is a no-op and the postcondition still applies.
                return
            decl.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        elif kind == "non_numeric":
            new_text, n = STEPS_DECL_RE.subn("steps: many", text)
            if n == 0:
                marker = "<!-- cdad-section:frontmatter -->"
                if marker not in text:
                    raise AssertionError(
                        "P3 harness precondition: no `steps:` line to make "
                        f"non-numeric and no frontmatter marker in {decl} to "
                        "insert after"
                    )
                new_text = text.replace(marker, marker + "\nsteps: many", 1)
            decl.write_text(new_text, encoding="utf-8")
        else:
            raise AssertionError(f"P3 harness: unknown mutation kind {kind!r}")

    def test_p3_fail_loud_when_steps_declaration_invalid(self) -> None:
        """P3: with the `steps:` line removed or non-numeric in the adapter
        source, the generator exits non-zero with a diagnostic naming
        sources/agents/adapters/opencode.md.
        """
        for kind in ("remove", "non_numeric"):
            with self.subTest(mutation=kind):
                with tempfile.TemporaryDirectory(prefix=f"cdad-p3-{kind}-") as raw:
                    base = Path(raw)
                    tree = self._sandbox(base)
                    self._mutate(tree, kind)
                    out = base / "out"
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(tree / "scripts" / "cdad-generate.py"),
                            "--runtime", RUNTIME,
                            "--stack", STACK,
                            "--out", str(out),
                        ],
                        cwd=str(tree),
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertNotEqual(
                        result.returncode, 0,
                        f"P3 contract (PD-3): with the `steps:` declaration "
                        f"{kind} in sources/agents/adapters/opencode.md the "
                        "generator must fail loudly; it exited 0",
                    )
                    self.assertIn(
                        "sources/agents/adapters/opencode.md",
                        result.stderr,
                        f"P3 contract (PD-3): the generator's diagnostic must "
                        "name the broken declaration source "
                        f"sources/agents/adapters/opencode.md; stderr: "
                        f"{result.stderr!r}",
                    )


class TestP4InstallPreservesSteps(unittest.TestCase):
    """P4: install.sh rewrites `model:` but must not drop `steps:`."""

    def test_p4_install_preserves_steps_line(self) -> None:
        """P4: after an install into an isolated root (CDAD_INSTALL_ROOT, the
        tests/test_install_ownership.py pattern; the real HOME is never
        touched), the installed opencode role agent still contains `steps: 300`.
        """
        with tempfile.TemporaryDirectory(prefix="cdad-p4-install-") as raw:
            root = Path(raw) / "install-root"
            root.mkdir()
            env = os.environ.copy()
            env["CDAD_INSTALL_ROOT"] = str(root)
            env["CDAD_SKILL_EXTRA_DIRS"] = ""
            result = subprocess.run(
                ["bash", str(INSTALLER), "--basic"],
                cwd=str(REPO_ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                result.returncode, 0,
                "P4 harness precondition: the install into the isolated root "
                f"failed: {result.stderr or result.stdout}",
            )
            installed = root / ".config" / "opencode" / "agents" / "cdad-test-writer.md"
            self.assertTrue(
                installed.is_file(),
                "P4 harness precondition: the installer did not deploy "
                f"{installed.relative_to(root)}",
            )
            text = installed.read_text(encoding="utf-8")
            fm = frontmatter(text)
            self.assertTrue(
                any(STEPS_LINE_RE.match(l) for l in fm.splitlines()),
                "P4 contract: the installed cdad-test-writer must still "
                "declare `steps: 300` after install — the installer rewrites "
                "the `model:` line and must not drop the steps ceiling; "
                f"frontmatter: {fm!r}",
            )


if __name__ == "__main__":
    unittest.main()
