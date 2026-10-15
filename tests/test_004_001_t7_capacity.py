#!/usr/bin/env python3
"""004-001 T7b — PD-11 + PD-12: capacity walk FROM THE INSTALLED PRODUCT.

Contract: docs/specs/004-001-canonical-runtime-artifacts/spec.md (PD-11, PD-12,
acceptance criteria 1 and 4) + plan.md row T7. Packet
004-001-canonical-runtime-artifacts-test-writer-red-009 (substage red).

SEMANTICS OF THE EVIDENCE (static/installed, per the objective):
- OpenCode evidence = permission-MODEL evaluation over the INSTALLED agent
  bytes with the existing findLast evaluator — NOT a live OpenCode runtime.
- Claude Code evidence = REAL execution of the installed guard
  (<root>/.claude/cdad-scripts/path-guard.sh) with synthetic hook JSON.

ORACLE REUSE (per the objective: the evaluator is the existing one, not a
third party): the findLast verdict function is imported from
tests/pd10_permission_semantics.py (which itself reuses
tests/test_opencode_read_map_and_steps.py). Guard probes: the documented
PreToolUse hook interface (hook JSON `{tool_name, tool_input}` on stdin; exit
2 = block, exit 0 = allow; role passed as the CLI argument — documented in
findings/validation-cdad-002.md:41 and ADR-008).

BASH (negated boundary, owner decision 80f9b90 / commit of record): the bash
layer is a PERMISSIVE operational policy — the negative side of bash is N/A by
design; the retained barriers are PATH-based. Declared here explicitly instead
of skipped silently (PD-12 honesty): NO test asserts bash denials.

Test -> postcondition mapping (every test -> contract item):

  test_pd11_capacity_walk_and_exact_output_per_command -> PD-11
      (isolated install rc=0 -> synthetic consumer outside the checkout ->
       measure (`rtk wc -l` over the synthetic files), aggregate
       deterministically (the command's own TOTAL line vs the KNOWN fixture
       value, never hand-summed), agreed runner (`python3 -m pytest -q`)
       rc=0, non-mutating inspection git (`git status --porcelain`,
       `git log --oneline -1`, `git diff HEAD`: HEAD and index unchanged),
       installed CLI responds (--help rc=0; validate-request on a synthetic
       request), per-command exact output recorded to THIS run's own
       tempdir log (cdad-t7b-run.log under the run tempdir — no
       pre-existing environment directory, review fix)
       and printed — PD-11 output NOT mixed with the static evidence)
  test_pd12_opencode_boundaries_on_installed_agents              -> PD-12
      (legitimate operation ALLOWED: implementer edit src/x.py; test-writer
       edits tests/test_x.py and reads docs/specs/**; readers read src
       (base + odoo, without extra cost) AND out-of-role BLOCKED: reader
       edit ANY path deny; test-writer read/grep src deny; implementer
       edit tests deny — against <root>/.config/opencode/agents bytes)
  test_pd12_cc_guard_executes_real_synthetic_hooks               -> PD-12
      (REAL execution of the installed CC path-guard with synthetic hook
       JSON: out-of-role blocked (exit 2) and legitimate pass (exit 0) for
       the base and odoo role vocabularies; a legitimate path returning
       exit 2 is a PD-12 DEFECT — the report carries the diagnostic)

All execution happens through subprocesses with cwd = the synthetic consumer
repo; the CDAD checkout is absent from PATH and PYTHONPATH. CDAD_INSTALL_ROOT
is an isolated tempdir — the real HOME is NEVER touched (invariant).

Run from the repository root (cdad/):
    python3 -m pytest tests/test_004_001_t7_capacity.py -q
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "install.sh"
# Per-run evidence log (PD-11): derived from the test's OWN tempdir (created
# in T7bCapacityFixture.setUpClass). The test must not depend on ANY
# pre-existing directory of the environment (review fix: the old fixed path
# /tmp/opencode/cdad-t7b.log failed when the directory did not exist and
# accumulated evidence across separate runs). Set per class-run; each run
# gets its own fresh log inside its own tempdir.
LOG: "Path | None" = None

# --- evaluator reuse (NO second evaluator) -----------------------------------
sys.path.insert(0, str(REPO_ROOT))
from tests.pd10_permission_semantics import verdict, perm_map  # noqa: E402

ROLE_AGENTS = ("architect", "test-writer", "implementer", "reviewer", "scribe")

READERS = ("architect", "reviewer", "scribe")

# --- synthetic fixture (known values FROZEN in the source) -------------------
FIXTURE_TEXT = {
    "app.py": "RESULT_Z = 1\nRESULT_Z = 2\n",
    "config.py": "A = 1\nB = 2\nC = 3\n",
    "tests/test_first.py": "def test_one():\n    assert True\n\n",
}
# total = 2 + 3 + 3 = 8 (the KNOWN fixture value the walk compares against —
# the aggregation is never recomputed by hand in the test)
FIXTURE_TOTAL_LINES = 8
FIXTURE_FILES = ("app.py", "config.py", "tests/test_first.py")
RUNNER_CMD = ["python3", "-m", "pytest", "-q", "tests/test_first.py"]
NON_MUTATING_COMMIT_SUBJECT = "synthetic fixture"


def _log(command: list[str], proc: subprocess.CompletedProcess) -> None:
    """Exact per-command output to the evidence master (PD-11)."""
    if LOG is None:  # pragma: no cover — harness invariant, not a behavior path
        raise AssertionError("_log called before the run log was created")
    header = (f"=== {' '.join(command)} (cwd={proc._t7b_cwd}, "
              f"rc={proc.returncode})")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(header + "\n" + proc.stdout
                 + (("\n[stderr]\n" + proc.stderr) if proc.stderr else "")
                 + "\n" + ("-" * 60) + "\n")


def _run1(cmd: list[str], cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    """One test-visible subprocess run: captures output for the assertion and
    appends the exact per-command output to the evidence master (PD-11)."""
    env = env if env is not None else os.environ
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, text=True,
                          capture_output=True, check=False)
    proc._t7b_cwd = str(cwd)
    _log(cmd, proc)
    return proc


def _per_file_lines(stdout: str) -> list[int]:
    """The per-file line counts of a `rtk wc -l <files...>` output (the leading
    integer of every per-file line; the TOTAL line is excluded — the sum is
    the command's own, never the test's)."""
    lines = []
    for line in stdout.splitlines():
        if line and line[0].isdigit():
            lines.append(int(line.split()[0]))
    return lines


def _total_line_is(stdout: str, expected: int) -> bool:
    """The command's own mechanical TOTAL line, compared against the KNOWN
    fixture value (never recomputed by the test — PD-11/C0)."""
    total_lines = [line for line in stdout.splitlines()
                   if line.strip() and not line.lstrip()[0].isdigit()]
    return total_lines == [f"Σ {expected}"]


class T7bCapacityFixture(unittest.TestCase):
    """One isolated install + one synthetic consumer repo (out of checkout)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-t7b-")
        base = Path(cls._tmp.name).resolve()
        # Per-run evidence log: INSIDE this run's own tempdir, created here
        # (never a pre-existing environment directory). Each run gets a
        # fresh log — no accumulation across runs (review fix, PD-11).
        global LOG
        LOG = base / "cdad-t7b-run.log"
        LOG.touch()
        # (1) isolated install — CDAD_INSTALL_ROOT = an EMPTY tempdir; the
        # real HOME is NEVER touched (packet invariant).
        cls.install_root = base / "install-root"
        cls.install_root.mkdir()
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        install = subprocess.run(
            ["bash", str(INSTALLER), "--basic"],
            cwd=str(REPO_ROOT), env=env, text=True,
            capture_output=True, check=False)
        _write_log(f"bash install.sh --basic  # CDAD_INSTALL_ROOT="
                   f"{cls.install_root} (cwd={REPO_ROOT})", install)
        assert install.returncode == 0, (
            "E2E harness precondition: isolated install failed:\n"
            f"{install.stderr or install.stdout}")
        # (2) synthetic consumer repo — EVERYTHING below runs from there.
        cls.consumer = base / "consumer"
        cls._build_consumer_repo()
        # Env shared by the walk: the checkout must be OUT of the execution
        # path (never in PATH or PYTHONPATH).
        cls.walk_env = os.environ.copy()
        cls.walk_env.pop("PYTHONPATH", None)
        cls.walk_env.pop("CDAD_INSTALL_ROOT", None)
        # The walk must not leave bytecode caches behind in the consumer repo
        # (the inspection git asserts a clean index — PD-11 non-mutant).
        cls.walk_env["PYTHONDONTWRITEBYTECODE"] = "1"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    @classmethod
    def _build_consumer_repo(cls) -> None:
        c = cls.consumer
        for rel, text in FIXTURE_TEXT.items():
            path = c / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        cls._git(c, "init", "-q")
        cls._git(c, "config", "user.email", "t7b@example.invalid")
        cls._git(c, "config", "user.name", "T7b Fixture")
        cls._git(c, "add", "-A")
        cls._git(c, "commit", "-q", "-m", f"{NON_MUTATING_COMMIT_SUBJECT}: 8 known lines")
        cls.head = cls._git(c, "rev-parse", "HEAD").stdout.strip()

    @staticmethod
    def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        proc = subprocess.run(["git", *args], cwd=str(cwd), text=True,
                              capture_output=True, check=False)
        assert proc.returncode == 0, (
            f"fixture git {' '.join(args)} failed: {proc.stderr or proc.stdout}")
        return proc


def _write_log(command: str, proc: subprocess.CompletedProcess) -> None:
    """Exact per-command output of an ad-hoc (non-_run1) command."""
    if LOG is None:  # pragma: no cover — harness invariant, not a behavior path
        raise AssertionError("_write_log called before the run log was created")
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"=== {command} (rc={proc.returncode})\n{proc.stdout}"
                 + (("\n[stderr]\n" + proc.stderr) if proc.stderr else "")
                 + "\n" + ("-" * 60) + "\n")


class TestPD11CapacityWalk(T7bCapacityFixture):
    """PD-11: the complete positive walk, from installed product, no checkout."""

    def walk_env_fresh_checkout_free(self) -> dict:
        """The walk env: the checkout stays OUT of PATH and PYTHONPATH.

        The assertion is behavioral: any environment entry naming REPO_ROOT is
        removed, so no walk command can accidentally import or execute from
        the checkout (PD-11: 'sin el repo en el path').
        """
        env = {k: v for k, v in self.walk_env.items()}
        env["PATH"] = ":".join(
            seg for seg in env.get("PATH", "").split(":")
            if seg and not Path(seg).resolve().is_relative_to(REPO_ROOT))
        env.pop("PYTHONPATH", None)
        self.assertNotIn(
            str(REPO_ROOT), env["PATH"],
            "harness: the checkout leaked into the walk PATH")
        self.assertNotIn(
            str(REPO_ROOT), env.get("PYTHONPATH", ""),
            "harness: the checkout leaked into the walk PYTHONPATH")
        return env

    def test_pd11_capacity_walk_and_exact_output_per_command(self) -> None:
        """PD-11: every positive step succeeds FROM the synthetic consumer —
        isolated install (rc=0), measurement (rtk wc -l) with the command's
        own TOTAL vs the known fixture value, agreed runner rc=0,
        non-mutating git inspection, installed CLI answers, per-command exact
        output recorded and printed (never mixed with static evidence)."""
        env = self.walk_env_fresh_checkout_free()
        cwd = self.consumer
        install_deployment = (
            self.install_root / ".config/opencode/agents/cdad-architect.md")
        self.assertTrue(
            install_deployment.is_file(),
            "PD-11 harness: isolated install did not deploy the OpenCode agents")

        # (a) measure: `rtk wc -l` over the synthetic files.
        MEASURE_CMD = ["rtk", "wc", "-l", *FIXTURE_FILES]
        measure = _run1(MEASURE_CMD, cwd, env)
        self.assertEqual(
            measure.returncode, 0,
            f"PD-11 (PD-12 defect if this is a legitimate rejection): "
            f"`rtk wc -l` was rejected on the positive walk: "
            f"{measure.stderr or measure.stdout}")
        self.assertEqual(
            _per_file_lines(measure.stdout), [2, 3, 3],
            "PD-11: unexpected per-file line counts: " + repr(measure.stdout))

        # (b) aggregate deterministically: the total IS the command's own
        # total line — asserted against the KNOWN fixture value (the failure
        # mode of C0 was a hand-aggregated report; never repeated here).
        total = _run1(["rtk", "wc", "-l", *FIXTURE_FILES], cwd, env)
        self.assertEqual(total.returncode, 0, total.stderr)
        self.assertTrue(
            _total_line_is(total.stdout, FIXTURE_TOTAL_LINES),
            f"PD-11: `rtk wc -l` did not produce its own mechanical TOTAL "
            f"line equal to the KNOWN fixture value ({FIXTURE_TOTAL_LINES}); "
            f"output: {total.stdout!r} — the walk's aggregation must come "
            "from the command, never from a hand sum (C0 regression)")

        # (c) agreed runner: python3 -m pytest -q on the synthetic test, rc=0.
        runner = _run1(RUNNER_CMD, cwd, env)
        self.assertEqual(
            runner.returncode, 0,
            "PD-11: the agreed runner (`python3 -m pytest -q`) was rejected "
            "on the positive walk: " + (runner.stderr or runner.stdout))
        self.assertIn(
            "1 passed", runner.stdout,
            "PD-11: the synthetic test did not run via the agreed runner: "
            + runner.stdout)

        # (c) non-mutating inspection git: HEAD and index unchanged.
        for label, cmd, expect_rc in (
            ("git status --porcelain", ["git", "status", "--porcelain"], 0),
            ("git log --oneline -1", ["git", "log", "--oneline", "-1"], 0),
            ("git diff HEAD", ["git", "diff", "HEAD"], 0),
        ):
            proc = _run1(cmd, cwd, env)
            self.assertEqual(
                proc.returncode, expect_rc,
                f"PD-11: {label} was rejected on the walk: " + proc.stderr)
        self.assertEqual(
            _run1(["git", "status", "--porcelain"], cwd, env).stdout, "",
            "PD-11: the walk left the consumer's git tree dirty; the "
            "inspection git must stay non-mutating")
        diff = _run1(["git", "diff", "HEAD"], cwd, env)
        self.assertEqual(
            diff.stdout, "",
            "PD-11: `git diff HEAD` is non-empty after the walk; the "
            "inspection git must not mutate the tree")
        head_after = _run1(["git", "rev-parse", "HEAD"], cwd, env).stdout.strip()
        self.assertEqual(
            head_after, self.head,
            "PD-11: HEAD changed during the non-mutating inspection walk")
        log1 = _run1(["git", "log", "--oneline", "-1"], cwd, env).stdout
        self.assertIn(
            NON_MUTATING_COMMIT_SUBJECT, log1,
            "PD-11: the committed subject of the consumer fixture changed: " + log1)

        # (d) the installed CLI responds (--help rc=0); the subcommand
        # interface is intact from the consumer, without checkout
        # dependencies (the installed skills are self-contained). The packet
        # consumption ITSELF (render/prepare parity from the installed CLI)
        # is T6's GREEN contract
        # (test_004_001_t6.py::test_t6_smoke_render_from_install_without_checkout);
        # this walk records the interface response as exact per-command output.
        installed_cli = (self.install_root
                         / ".config/opencode/skills/cdad-cycle/scripts/cdad_packet.py")
        self.assertTrue(
            installed_cli.is_file(),
            f"PD-11 harness: installer omitted the installed CLI {installed_cli}")
        proc = _run1([sys.executable, str(installed_cli), "--help"], cwd, env)
        self.assertEqual(
            proc.returncode, 0,
            "PD-11: installed cdad_packet.py rejected --help from the "
            "consumer: " + (proc.stderr or proc.stdout))
        self.assertIn(
            "prepare", proc.stdout,
            "PD-11: installed CLI --help does not expose the documented "
            "prepare subcommand: " + proc.stdout[:400])

        # EXACT per-command output printed: the role report carries it
        # verbatim (PD-11: separate from static evidence). The log path is
        # printed too, so the evidence stays referenced to THIS run's
        # tempdir (review fix: per-run log, no pre-existing dirs).
        exact = LOG.read_text(encoding="utf-8")
        self.assertIn("rc=0", exact, "every walk command must be rc=0")
        print("\n--- PD-11 exact per-command output (evidence master: "
              f"{LOG}) ---")
        print(exact)


class TestPD12OpenCodeBoundariesOnInstalledBytes(T7bCapacityFixture):
    """PD-12 (OpenCode): PATH-BASED barriers, BOTH directions, installed bytes.

    NOTE (evidence semantics): this is permission-MODEL evaluation of the
    INSTALLED agent frontmatter with the existing findLast evaluator —
    NOT a live OpenCode runtime.
    """

    AGENTS_DIR_NAME = ".config/opencode/agents"

    def agents_text(self, agent: str) -> str:
        path = self.install_root / self.AGENTS_DIR_NAME / f"cdad-{agent}.md"
        self.assertTrue(path.is_file(),
                        f"installed agents missing cdad-{agent}.md (PD-12)")
        return path.read_text(encoding="utf-8")

    def verdict_map(self, agent: str, tool: str, probe: str) -> str:
        text = self.agents_text(agent)
        try:
            rules = perm_map(text, tool)
        except StopIteration:
            # absent map = findLast default: ALLOW (evaluator semantics,
            # tests/test_opencode_read_map_and_steps.py::evaluate).
            return "allow"
        from tests.test_opencode_read_map_and_steps import evaluate
        return evaluate(rules, probe)

    def test_pd12_opencode_legitimate_operations_allowed(self) -> None:
        """PD-12 (positive): every leg operation per role is ALLOWED on the
        installed bytes — for base and odoo variants (same list, zero cost).
        A legitimate operation rejected here is a PD-12 DEFECT (reported, not
        hidden)."""
        # per-role legitimate operations, applied to the base AND odoo
        # variants of the same row (same list, zero extra cost).
        legit = {
            "implementer": [
                ("edit", "src/x.py"),
            ],
            "test-writer": [
                ("edit", "tests/test_x.py"),
                ("edit", "src/pkg/test_mod.py"),  # colocated-test exception
                ("read", "docs/specs/004-001-canonical-runtime-artifacts/spec.md"),
            ],
            "architect": [("read", "src/x.py")],
            "reviewer": [("read", "src/x.py")],
            "scribe": [("read", "src/x.py")],
        }
        for role, ops in legit.items():
            for variant in ("", "-odoo"):
                agent = role + variant
                for tool, probe in ops:
                    with self.subTest(agent=f"cdad-{agent}.md",
                                      op=f"{tool}({probe})"):
                        got = self.verdict_map(agent, tool, probe)
                        self.assertEqual(
                            got, "allow",
                            f"PD-12 DEFECT: the legitimate operation "
                            f"{tool}({probe!r}) of role {agent} "
                            f"({'base' if not variant else 'odoo'}) is "
                            "rejected by the installed permission map "
                            f"(got {got!r})")

    def test_pd12_opencode_out_of_role_operations_blocked(self) -> None:
        """PD-12 (negative): out-of-role effects stay blocked on the installed
        bytes: reader edits ANYTHING -> deny; test-writer read/grep src ->
        deny; implementer Edit tests/** -> deny (base and odoo both)."""
        out_of_role = [
            ("architect", "edit", "src/x.py"),
            ("architect", "edit", "tests/test_x.py"),
            ("architect", "edit", "anything.txt"),
            ("reviewer", "edit", "src/x.py"),
            ("reviewer", "edit", "docs/specs/x/spec.md"),
            ("scribe", "edit", "src/x.py"),
            ("test-writer", "read", "src/app.py"),
            ("test-writer", "grep", "src/**"),
            ("test-writer", "read", "lib/x.py"),
            ("test-writer-odoo", "read", "addons/m/models/a.py"),
            ("test-writer-odoo", "grep", "**/models/**"),
            ("implementer", "edit", "tests/test_a.py"),
            ("implementer", "edit", "src/pkg/test_mod.py"),
            ("implementer-odoo", "edit", "addons/m/tests/test_sale.py"),
        ]
        for agent, tool, probe in out_of_role:
            with self.subTest(agent=f"cdad-{agent}.md", op=f"{tool}({probe})"):
                got = self.verdict_map(agent, tool, probe)
                self.assertEqual(
                    got, "deny",
                    f"PD-12: out-of-role effect {tool}({probe!r}) on "
                    f"cdad-{agent}.md resolved {got!r}, want deny")


class TestPD12CCGuardRealExecution(T7bCapacityFixture):
    """PD-12 (Claude Code): REAL execution of the installed path-guard with
    synthetic hook JSON. Exit 2 = block, exit 0 = pass (documented interface:
    findings/validation-cdad-002.md:41 + ADR-008:58)."""

    def guard(self) -> Path:
        path = self.install_root / ".claude/cdad-scripts/path-guard.sh"
        self.assertTrue(path.is_file(),
                        f"installed CC path-guard missing: {path}")
        return path

    @staticmethod
    def probe(guard: Path, role: str, tool: str, tool_input: dict,
              cwd: Path) -> subprocess.CompletedProcess[str]:
        hook = json.dumps({"tool_name": tool, "tool_input": tool_input})
        return subprocess.run(
            ["bash", str(guard), role],
            input=hook, cwd=str(cwd), text=True,
            capture_output=True, check=False)

    def test_pd12_cc_guard_out_of_role_blocked(self) -> None:
        """PD-12: real guard execution blocks the out-of-role effects
        (synthetic hook JSON; exit 2 = block)."""
        guard = self.install_root / ".claude/cdad-scripts/path-guard.sh"
        cases = [
            ("implementer", "Edit", {"file_path": "tests/foo_test.py"}),
            ("implementer", "Edit", {"file_path": "src/pkg/test_mod.py"}),
            ("test-writer-read", "Read", {"file_path": "src/main.py"}),
            ("test-writer-read", "Grep", {"file_path": "src/app.py"}),
            ("test-writer-read", "Glob", {"file_path": "src/**"}),
            ("test-writer-write", "Edit", {"file_path": "src/main.py"}),
        ]
        for role, tool, tool_input in cases:
            proc = self.probe(guard, role, tool, tool_input, self.consumer)
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                self.assertEqual(
                    proc.returncode, 2,
                    f"PD-12 (Claude Code): the installed guard must BLOCK the "
                    f"out-of-role effect {tool}({tool_input!r}) for role "
                    f"{role} (exit 2 per PreToolUse contract); got rc="
                    f"{proc.returncode}; stdout: {proc.stdout!r}; "
                    f"stderr: {proc.stderr!r}")

    def test_pd12_cc_guard_legitimate_operations_pass(self) -> None:
        """PD-12: real guard execution lets the legitimate operations pass
        (exit 0). A rejection here is a PD-12 DEFECT, diagnosed briefly and
        reported (not hidden). Includes the odoo variants (same list, zero
        cost) and the absolute-path fail-open fix (validation probe #6/#7)."""
        guard = self.install_root / ".claude/cdad-scripts/path-guard.sh"
        cases = [
            # base role set
            ("implementer", "Edit", {"file_path": "src/x.py"}),
            ("test-writer-read", "Read", {
                "file_path": "docs/specs/004-001-canonical-runtime-artifacts/spec.md"}),
            ("test-writer-write", "Edit", {"file_path": "tests/test_x.py"}),
            # odoo role variants (same list, zero cost)
            ("implementer-odoo", "Edit", {"file_path": "addons/x/models/m.py"}),
            ("test-writer-odoo-write", "Edit", {"file_path": "addons/x/tests/test_donation.py"}),
        ]
        for role, tool, tool_input in cases:
            proc = self.probe(guard, role, tool, tool_input, self.consumer)
            with self.subTest(role=role, tool=tool,
                              tool_input=tool_input):
                self.assertEqual(
                    proc.returncode, 0,
                    f"PD-12 DEFECT (Claude Code): the legitimate operation "
                    f"{tool}({tool_input!r}) for role {role} is BLOCKED by "
                    f"the installed guard (rc={proc.returncode}); "
                    f"stdout: {proc.stdout!r}; stderr: {proc.stderr!r}")

    def test_pd12_cc_guard_fail_open_fix_absolute_path(self) -> None:
        """PD-12 (no fail-out side bypass): absolute paths under the consumer
        tree resolve against PWD (the Fix B contract from validation) — they
        must not escape the role boundary."""
        guard = self.install_root / ".claude/cdad-scripts/path-guard.sh"
        blocked = [
            ("implementer", "Edit",
             {"file_path": str(self.consumer / "tests" / "foo_test.py")}),
            ("test-writer-read", "Read",
             {"file_path": str(self.consumer / "src" / "main.py")}),
        ]
        for role, tool, tool_input in blocked:
            proc = self.probe(guard, role, tool, tool_input, self.consumer)
            with self.subTest(role=role, tool=tool, tool_input=tool_input):
                self.assertEqual(
                    proc.returncode, 2,
                    f"PD-12: absolute path bypass REOPENED: the guard allowed "
                    f"{tool}({tool_input!r}) for role {role} (rc="
                    f"{proc.returncode}); the Fix B semantics must hold")


if __name__ == "__main__":
    unittest.main(verbosity=2)
