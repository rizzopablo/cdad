#!/usr/bin/env python3
"""Tests for 004-001 T3: the deterministic generator (spec §2 contract).

Black-box tests: the generator `scripts/cdad-generate.py` is invoked as a
subprocess and only its published outputs are inspected. Every test's FIRST
assertion is the contract assertion that the generator exists and runs
(AssertionError with the contract message, never ImportError). Mappings to the
approved postconditions:

- test_postcondition_2_*  → PD-2  (determinism)
- test_postcondition_3a_* → PD-3  (explicit failure, incomplete/duplicated source)
- test_postcondition_3b_* → PD-3  (explicit failure, duplicated shared block)
- test_postcondition_3c_* → PD-3  (explicit failure, unsupported runtime/stack)
- test_postcondition_4_*  → PD-4  (single source: manifest references + composed §2)
- test_pd_1e_generated_*  → 006-003 PD-1e/INV-3 (no `model:` in generated agents)
- test_pd_7a_generated_*  → 006-003 PD-7a/INV-3 (generated orchestrators name no model)
- test_postcondition_15_* → PD-15 (honesty: no unbacked sandbox promises)
- test_postcondition_16_* → PD-16 (legacy fallback declared in generated agents)

ORACLE REPLACEMENT (006-003 U1, spec docs/specs/006-003-installer-single-
profile-delegation-config/spec.md, PD-1/PD-1c/PD-1e/PD-7a/INV-3): this file was
profile-coupled. What changed and why, so no assert is dropped silently:

- `PROFILE = "optimus"` and the `--profile` argument are GONE from every run:
  the generator no longer has profiles (PD-1f).
- `test_postcondition_3c` no longer exercises the `unknown-profile` case: there
  is no profile argument left to validate (PD-1f). Runtime/stack validation is
  kept unchanged.
- `test_postcondition_4` asserted that the manifest RECORDS the profile used.
  That assert is REPLACED by its inverse: the manifest must not carry the
  profile (PD-1d). Nothing else of PD-4 changes.
- `test_postcondition_14_*` (PD-14: "each runtime mentions only the models its
  own map produces") is REPLACED by PD-1e/PD-7a/INV-3: no generated agent fixes
  a `model:` line and no generated orchestrator names a model at all — there is
  no runtime model map left to be coherent with (the map is retired, PD-1c).
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"
GENERATOR_REF = "scripts/cdad-generate.py"

STACK = "odoo"
RUNTIMES = ("opencode", "claude-code")
ROLES = ("architect", "test-writer", "implementer", "reviewer", "scribe")
AGENT_NAMES = tuple(
    ["cdad-%s.md" % role for role in ROLES]
    + ["cdad-%s-odoo.md" % role for role in ROLES]
    + ["cdad-orchestrator.md"]
)

# 006-003 U1 replaced the per-runtime model map (scripts/cdad-models.sh, PD-14)
# with the absence invariant INV-3: no installable text fixes or names a model.
MODEL_LINE_RE = re.compile(r"^model:")
MODEL_NAME_RE = re.compile(r"deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/")

MISSING_GENERATOR_MSG = (
    "T3 contract: %s is a declared artifact of this feature "
    "(PD-2/3/4/1e/7a/15/16) and does not exist — RED contract not yet honored"
    % GENERATOR_REF
)

# Negation cues that make a 'sandbox' mention an honest-limitation (PD-15).
NEGATION_RE = re.compile(r"\b(no|not|never|sin|não)\b")
# The Odoo environment skill legitimately carries 'sandbox' in its NAME.
SANDBOX_SKILL_NAME = "odoo-sandbox-env"

_SECTION_OPEN = "<!-- cdad-section:%s -->"
_SECTION_CLOSE = "<!-- /cdad-section -->"
_SOURCE_CLOSE = "<!-- /cdad-source -->"
COMPOSED_MARKER = "Roles-contract §2 table — composed"
SHARED_BLOCK_RE = re.compile(
    r"(?s)<!-- cdad-shared:intake-core -->.*?<!-- /cdad-shared -->"
)


def run_generator(
    runtime: str,
    out_dir: Path,
    *,
    cwd: Path | None = None,
    stack: str = STACK,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--runtime",
            runtime,
            "--stack",
            stack,
            "--out",
            str(out_dir),
        ],
        cwd=str(cwd or REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def make_sandbox(base: Path) -> Path:
    """Sandbox copy of sources/ plus the generator.

    Never mutates the real sources/: the mutation cases run a COPY of the
    generator inside the sandbox so the source-resolution sees the mutated
    copy regardless of whether the generator resolves sources from its own
    location or from the working directory. The model map is no longer part of
    the sandbox (006-003 PD-1c: the generator has no model map to copy).
    """
    assert GENERATOR.is_file(), MISSING_GENERATOR_MSG
    sandbox = base / "sandbox"
    sandbox.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "sources", sandbox / "sources")
    (sandbox / "scripts").mkdir()
    shutil.copy2(GENERATOR, sandbox / "scripts" / GENERATOR.name)
    return sandbox


def run_generator_in_sandbox(sandbox: Path, out_dir: Path, runtime: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(sandbox / "scripts" / GENERATOR.name),
            "--runtime",
            runtime,
            "--stack",
            STACK,
            "--out",
            str(out_dir),
        ],
        cwd=str(sandbox),
        text=True,
        capture_output=True,
        check=False,
    )


def assert_no_publication(testcase: unittest.TestCase, out: Path) -> None:
    published = (
        [str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()]
        if out.exists()
        else []
    )
    testcase.assertEqual(
        published,
        [],
        "PD-3: partial publication on failure — files left in %s: %s" % (out, published),
    )


def cut_section(text: str, name: str) -> str:
    start = text.index(_SECTION_OPEN % name)
    end = text.index(_SECTION_CLOSE, start) + len(_SECTION_CLOSE)
    return text[:start] + text[end:]


def empty_section(text: str, name: str) -> str:
    start = text.index(_SECTION_OPEN % name) + len(_SECTION_OPEN % name)
    end = text.index(_SECTION_CLOSE, start)
    return text[:start] + "\n\n" + text[end:]


def duplicate_section(text: str, name: str) -> str:
    start = text.index(_SECTION_OPEN % name)
    end = text.index(_SECTION_CLOSE, start) + len(_SECTION_CLOSE)
    return text[:end] + "\n\n" + text[start:end] + text[end:]


class TestDeterministicGenerator(unittest.TestCase):
    """Generator contract (spec §2): deterministic, explicit-failure, single-source."""

    def test_postcondition_2_identical_runs_are_byte_identical(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-t3-determinism-") as tmp:
            out = Path(tmp) / "staging"
            first = run_generator("opencode", out)
            self.assertEqual(first.returncode, 0, "generator run failed: %s" % first.stderr)
            first_tree = tree_hashes(out)
            self.assertTrue(first_tree, "PD-2: the generator published no artifacts")
            second = run_generator("opencode", out)
            self.assertEqual(second.returncode, 0, "generator run failed: %s" % second.stderr)
            second_tree = tree_hashes(out)
            self.assertEqual(
                sorted(first_tree),
                sorted(second_tree),
                "PD-2: identical inputs produced different file sets",
            )
            for rel in sorted(first_tree):
                self.assertEqual(
                    first_tree[rel],
                    second_tree[rel],
                    "PD-2: %s is not byte-identical across identical runs" % rel,
                )

    def test_postcondition_3a_incomplete_or_duplicated_section_fails_cleanly(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        source_text = (REPO_ROOT / "sources" / "roles" / "scribe.md").read_text(encoding="utf-8")
        mutations = {
            "missing-section": cut_section(source_text, "limits"),
            "empty-section": empty_section(source_text, "limits"),
            "duplicated-section": duplicate_section(source_text, "directive"),
        }
        with tempfile.TemporaryDirectory(prefix="cdad-t3-fail-") as tmp:
            base = Path(tmp)
            for label, mutated in mutations.items():
                with self.subTest(case=label):
                    sandbox = make_sandbox(base / label)
                    (sandbox / "sources" / "roles" / "scribe.md").write_text(mutated, encoding="utf-8")
                    out = base / label / "staging"
                    result = run_generator_in_sandbox(sandbox, out, "opencode")
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        "PD-3: a source with a %s was accepted" % label,
                    )
                    self.assertTrue(
                        result.stderr.strip(),
                        "PD-3: rejection of a %s lacked a diagnostic" % label,
                    )
                    self.assertIn(
                        "scribe",
                        result.stderr.lower(),
                        "PD-3: the error does not name the problem (role id)",
                    )
                    assert_no_publication(self, out)

    def test_postcondition_3b_duplicated_shared_block_fails(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        architect_text = (REPO_ROOT / "sources" / "roles" / "architect.md").read_text(encoding="utf-8")
        match = SHARED_BLOCK_RE.search(architect_text)
        self.assertIsNotNone(
            match,
            "fixture drift: cdad-shared:intake-core is no longer in sources/roles/architect.md",
        )
        block = match.group(0)
        with tempfile.TemporaryDirectory(prefix="cdad-t3-fail-shared-") as tmp:
            base = Path(tmp)
            sandbox = make_sandbox(base)
            implementer_path = sandbox / "sources" / "roles" / "implementer.md"
            text = implementer_path.read_text(encoding="utf-8")
            self.assertEqual(
                text.count(_SOURCE_CLOSE),
                1,
                "fixture drift: unexpected cdad-source structure in implementer.md",
            )
            implementer_path.write_text(
                text.replace(_SOURCE_CLOSE, block + "\n\n" + _SOURCE_CLOSE),
                encoding="utf-8",
            )
            out = base / "staging"
            result = run_generator_in_sandbox(sandbox, out, "opencode")
            self.assertNotEqual(result.returncode, 0, "PD-3: a duplicated cdad-shared block was accepted")
            self.assertTrue(result.stderr.strip(), "PD-3: rejection lacked a diagnostic")
            self.assertTrue(
                any(token in result.stderr.lower() for token in ("shared", "intake-core", "duplicate", "duplicated")),
                "PD-3: the error does not name the problem (duplicated shared block)",
            )
            assert_no_publication(self, out)

    def test_postcondition_3c_unsupported_combinations_fail(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        # 006-003 PD-1f: the `unknown-profile` case is RETIRED here — the
        # generator has no profile argument left to validate (that surface is
        # asserted by tests/test_006_003_u1_generator_without_profiles.py).
        cases = {
            "unknown-runtime": ("cursor", STACK),
            "unknown-stack": ("opencode", "golang"),
        }
        with tempfile.TemporaryDirectory(prefix="cdad-t3-fail-combo-") as tmp:
            base = Path(tmp)
            for label, (runtime, stack) in cases.items():
                with self.subTest(case=label):
                    out = base / label / "staging"
                    result = run_generator(runtime, out, stack=stack)
                    self.assertNotEqual(
                        result.returncode,
                        0,
                        "PD-3: unsupported combination (%s) was accepted" % label,
                    )
                    self.assertTrue(result.stderr.strip(), "PD-3: rejection lacked a diagnostic")
                    bad_value = {"unknown-runtime": "cursor", "unknown-stack": "golang"}[label]
                    self.assertIn(
                        bad_value,
                        result.stderr,
                        "PD-3: the error does not name the invalid value",
                    )
                    assert_no_publication(self, out)

    def test_postcondition_4_manifest_hashes_sources_and_regeneration_command(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-t3-manifest-") as tmp:
            out = Path(tmp) / "staging"
            result = run_generator("opencode", out)
            self.assertEqual(result.returncode, 0, "generator run failed: %s" % result.stderr)
            manifest_path = out / "manifest.json"
            self.assertTrue(manifest_path.is_file(), "PD-4: the generator did not publish manifest.json")
            raw = manifest_path.read_text(encoding="utf-8")
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                self.fail("PD-4: manifest.json is not valid JSON: %s" % exc)
            for agent_name in AGENT_NAMES:
                self.assertIn(agent_name, raw, "PD-4: manifest does not reference %s" % agent_name)
                digest = hashlib.sha256((out / "agents" / "opencode" / agent_name).read_bytes()).hexdigest()
                self.assertIn(digest, raw, "PD-4: manifest does not carry the sha256 of %s" % agent_name)
            for role in ROLES:
                self.assertIn(
                    role + ".md",
                    raw,
                    "PD-4: manifest does not reference the contributing source of role %s" % role,
                )
            self.assertIn("cdad-generate.py", raw, "PD-4: manifest does not carry the regeneration command")
            self.assertIn(STACK, raw, "PD-4: manifest does not record the stack used")
            # ORACLE REPLACEMENT (006-003 U1 / PD-1d): PD-4 used to assert that
            # the manifest recorded the profile used. The profile is gone from
            # the generator, so the assert is inverted: the manifest must not
            # carry it. (The focal file asserts the JSON key; here the raw
            # bytes are checked so a leftover value cannot survive either.)
            self.assertNotIn(
                "optimus",
                raw,
                "PD-1d (reemplazo del oráculo PD-4 'registra el perfil'): manifest.json "
                "todavía registra el perfil de generación",
            )

    def test_postcondition_4_orchestrator_contract_is_composed_once_with_all_role_rows(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                with tempfile.TemporaryDirectory(prefix="cdad-t3-composed-") as tmp:
                    out = Path(tmp) / "staging"
                    result = run_generator(runtime, out)
                    self.assertEqual(result.returncode, 0, "generator run failed: %s" % result.stderr)
                    orchestrator = out / "agents" / runtime / "cdad-orchestrator.md"
                    self.assertTrue(
                        orchestrator.is_file(),
                        "PD-4: generator did not publish cdad-orchestrator.md for %s" % runtime,
                    )
                    text = orchestrator.read_text(encoding="utf-8")
                    self.assertEqual(
                        text.count(COMPOSED_MARKER),
                        1,
                        "PD-4/D7: %s orchestrator §2 must be the composed artifact, marked exactly once" % runtime,
                    )
                    for role in ROLES + ("orchestrator",):
                        self.assertRegex(
                            text,
                            r"(?m)^\|\s*%s\b" % role,
                            "PD-4: %s orchestrator §2 is missing the composed row of role %s" % (runtime, role),
                        )

    def test_pd_1e_generated_agents_carry_no_model_line(self) -> None:
        """PD-1e/INV-3 (replaces PD-14): generated agents fix no `model:`.

        ORACLE REPLACEMENT (006-003 U1): PD-14 verified that each runtime
        mentioned only the models its own map produced. The map is retired
        (PD-1c), so the invariant becomes stronger and simpler: NO generated
        agent of either runtime may carry a `model:` line (PD-1e, INV-3).
        """
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                with tempfile.TemporaryDirectory(prefix="cdad-t3-cc-models-") as tmp:
                    out = Path(tmp) / "staging"
                    result = run_generator(runtime, out)
                    self.assertEqual(
                        result.returncode, 0, "generator run failed: %s" % result.stderr
                    )
                    agents = sorted((out / "agents" / runtime).glob("cdad-*.md"))
                    self.assertEqual(
                        [a.name for a in agents],
                        sorted(AGENT_NAMES),
                        "PD-4: %s runtime must publish exactly the 11 declared agents" % runtime,
                    )
                    for agent in agents:
                        lines = [
                            number
                            for number, line in enumerate(
                                agent.read_text(encoding="utf-8").splitlines(), start=1
                            )
                            if MODEL_LINE_RE.match(line)
                        ]
                        self.assertEqual(
                            lines,
                            [],
                            "PD-1e/INV-3: generated %s/%s still carries a model: line "
                            "(lines %s)" % (runtime, agent.name, lines),
                        )

    def test_pd_7a_generated_orchestrators_name_no_model(self) -> None:
        """PD-7a/INV-3 (replaces PD-14): generated orchestrators name no model.

        ORACLE REPLACEMENT (006-003 U1): PD-14 checked that the §2 model cells
        of each runtime belonged to its own map. The cells are retired
        (PD-7a: no installable text names a model), so the assert is inverted:
        the generated orchestrator must name no model of either family.
        """
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-t3-oc-models-") as tmp:
            base = Path(tmp)
            for runtime in RUNTIMES:
                with self.subTest(runtime=runtime):
                    out = base / runtime
                    result = run_generator(runtime, out)
                    self.assertEqual(
                        result.returncode, 0, "generator run failed: %s" % result.stderr
                    )
                    orchestrator = out / "agents" / runtime / "cdad-orchestrator.md"
                    matches = MODEL_NAME_RE.findall(
                        orchestrator.read_text(encoding="utf-8")
                    )
                    self.assertEqual(
                        matches,
                        [],
                        "PD-7a/INV-3: generated %s orchestrator names models %s"
                        % (runtime, sorted(set(matches))),
                    )

    def test_postcondition_15_generated_agents_make_no_unbacked_sandbox_promises(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                with tempfile.TemporaryDirectory(prefix="cdad-t3-honesty-") as tmp:
                    out = Path(tmp) / "staging"
                    result = run_generator(runtime, out)
                    self.assertEqual(result.returncode, 0, "generator run failed: %s" % result.stderr)
                    for agent in (out / "agents" / runtime).glob("cdad-*.md"):
                        for line in agent.read_text(encoding="utf-8").splitlines():
                            stripped = line.replace(SANDBOX_SKILL_NAME, "")
                            if "sandbox" not in stripped.lower():
                                continue
                            self.assertIsNotNone(
                                NEGATION_RE.search(stripped),
                                "PD-15: %s mentions 'sandbox' without an honest-limitation negation: %r"
                                % (agent.name, line.strip()),
                            )

    def test_postcondition_16_generated_agents_declare_legacy_loads_and_dual_path(self) -> None:
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        for runtime in RUNTIMES:
            with self.subTest(runtime=runtime):
                with tempfile.TemporaryDirectory(prefix="cdad-t3-legacy-") as tmp:
                    out = Path(tmp) / "staging"
                    result = run_generator(runtime, out)
                    self.assertEqual(result.returncode, 0, "generator run failed: %s" % result.stderr)
                    agents = {
                        a.name: a.read_text(encoding="utf-8")
                        for a in (out / "agents" / runtime).glob("cdad-*.md")
                    }
                    self.assertEqual(
                        sorted(agents),
                        sorted(AGENT_NAMES),
                        "PD-4: %s runtime must publish exactly the 11 declared agents" % runtime,
                    )
                    for name, text in agents.items():
                        self.assertIn(
                            "cdad-cycle",
                            text,
                            "PD-16: %s does not declare its legacy loads" % name,
                        )
                    for name in (
                        "cdad-architect.md",
                        "cdad-architect-odoo.md",
                        "cdad-test-writer.md",
                        "cdad-test-writer-odoo.md",
                    ):
                        self.assertIn(
                            "cdad-spec-and-test",
                            agents[name],
                            "PD-16/R3: %s must declare cdad-spec-and-test in its legacy loads" % name,
                        )
                    orchestrator_text = agents["cdad-orchestrator.md"]
                    self.assertIn(
                        "prepared",
                        orchestrator_text.lower(),
                        "PD-16: the orchestrator lost the prepared-execution path",
                    )
                    self.assertIn(
                        "legacy",
                        orchestrator_text.lower(),
                        "PD-16: the orchestrator lost the legacy fallback path",
                    )


if __name__ == "__main__":
    unittest.main()
