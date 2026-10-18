#!/usr/bin/env python3
"""RED tests for 006-003 U1: the generator has no profiles and no model map.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18) — PD-1b (staging recipe), PD-1c (model map retired),
PD-1d (manifest without `profile`), PD-1e (committed agents without `model:`),
PD-1f (no `--profile` in the generator CLI), PD-7a for GENERATED agents, and
INV-3 ("ningún texto instalable fija modelos").

Unit: U1 of the approved plan (ficha U1) — the generator/agent artifacts only.
The installer flag surface (PD-1a: `--economical|--optimus|--premium` rejected,
`--basic` kept as a deprecated no-op) and the ownership-manifest `profile` key
belong to other units and are NOT asserted here.

Black-box discipline: the generator is invoked as a subprocess and only its
published outputs (staging tree + manifest) are inspected; the Makefile and the
committed agent artifacts are read as the postcondition's own subject, never as
implementation guidance. No implementation module is imported.

Mapping (one test per numbered postcondition):

- test_pd_1b_*  -> PD-1b  (Makefile: no `PROFILE`; `staging` recipe passes no
                            `--profile`)
- test_pd_1c_*  -> PD-1c  (`scripts/cdad-models.sh` absent and unreferenced
                            from `install.sh` / `scripts/`)
- test_pd_1d_*  -> PD-1d  (staging manifest carries no `profile` key)
- test_pd_1e_*  -> PD-1e  (no `^model:` line in the committed agents)
- test_pd_1f_*  -> PD-1f  (generator: without `--profile` rc=0; with
                            `--profile X` rc!=0 plus a diagnostic)
- test_pd_7a_*  -> PD-7a (generated part) + INV-3 (generated agents fix no
                            model: no `model:` line, and the generated
                            orchestrators name no model)

Expected RED against the current tree (declared, not accidental): the model map
exists and is sourced, the manifest carries `profile`, 21 committed agent files
carry `model:`, the generator REQUIRES `--profile`, the staging recipe passes
it, and generated orchestrators name design models.

Sequencing note: while the generator still requires `--profile` (PD-1f), the
tests that need a successful profile-less run (PD-1d, PD-7a) stop at that
precondition and report PD-1f in their message; the moment U1 removes the flag
they assert their own postcondition. This is a declared ordering, not a hidden
dependency.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "cdad-generate.py"
GENERATOR_REF = "scripts/cdad-generate.py"
MODELS_SH = REPO_ROOT / "scripts" / "cdad-models.sh"
MAKEFILE = REPO_ROOT / "Makefile"

RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"

# PD-1e: `grep -rc '^model:' agents/cdad-*.md agents/claude-code/*.md` -> 0.
MODEL_LINE_RE = re.compile(r"^model:")

# PD-7a (generated part): names no installable artifact may fix any more.
MODEL_NAME_RE = re.compile(r"deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/")

MISSING_GENERATOR_MSG = (
    "fixture drift: %s is the declared generator of the contract (%s) and is "
    "missing — the U1 postconditions cannot be observed" % (GENERATOR_REF, GENERATOR)
)


def run_generator(out_dir: Path, *extra: str, runtime: str = "opencode") -> subprocess.CompletedProcess[str]:
    """Invoke the generator black-box (no `--profile` unless explicitly passed)."""
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--runtime",
            runtime,
            "--stack",
            STACK,
            *extra,
            "--out",
            str(out_dir),
        ],
        cwd=str(REPO_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )


def collect_keys(value: object) -> list[str]:
    """Every JSON object key of a parsed document, at any depth."""
    keys: list[str] = []
    if isinstance(value, dict):
        for key, inner in value.items():
            keys.append(key)
            keys.extend(collect_keys(inner))
    elif isinstance(value, list):
        for inner in value:
            keys.extend(collect_keys(inner))
    return keys


class TestGeneratorWithoutProfiles(unittest.TestCase):
    """PD-1b..f and the generated part of PD-7a (INV-3)."""

    maxDiff = None

    def test_pd_1b_makefile_has_no_profile_and_staging_recipe_passes_none(self) -> None:
        """PD-1b: `PROFILE` is gone from the Makefile and `staging` passes no `--profile`."""
        self.assertTrue(MAKEFILE.is_file(), "PD-1b: the declared Makefile is missing")
        text = MAKEFILE.read_text(encoding="utf-8")

        definitions = [
            line
            for line in text.splitlines()
            if re.match(r"^\s*(export\s+)?PROFILE\s*[?:+]?=", line)
        ]
        self.assertEqual(
            definitions,
            [],
            "PD-1b: the Makefile still defines the generation profile: %s" % definitions,
        )

        lines = text.splitlines()
        recipe: list[str] = []
        for index, line in enumerate(lines):
            if re.match(r"^staging\s*:", line):
                for follower in lines[index + 1 :]:
                    if not follower.startswith("\t"):
                        break
                    recipe.append(follower)
                break
        self.assertTrue(
            recipe,
            "fixture drift: the Makefile no longer declares a `staging:` recipe "
            "— PD-1b cannot be observed",
        )
        recipe_text = "\n".join(recipe)
        self.assertIn(
            "cdad-generate.py",
            recipe_text,
            "fixture drift: the `staging:` recipe no longer invokes the generator",
        )
        self.assertNotIn(
            "--profile",
            recipe_text,
            "PD-1b: the `staging:` recipe still passes a profile to the generator:\n%s"
            % recipe_text,
        )

    def test_pd_1c_model_map_script_is_absent_and_unreferenced(self) -> None:
        """PD-1c: `scripts/cdad-models.sh` is retired and nothing in the product names it."""
        self.assertFalse(
            MODELS_SH.exists(),
            "PD-1c: the model map scripts/cdad-models.sh still exists; the generator "
            "and the installer must carry no model map",
        )
        self.assertTrue(
            (REPO_ROOT / "scripts").is_dir(),
            "fixture drift: scripts/ is missing — PD-1c cannot be observed",
        )
        result = subprocess.run(
            ["grep", "-rn", "cdad-models.sh", str(REPO_ROOT / "install.sh"), str(REPO_ROOT / "scripts")],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.stdout,
            "",
            "PD-1c: install.sh/scripts/ still reference the retired model map:\n%s"
            % result.stdout,
        )

    def test_pd_1d_staging_manifest_has_no_profile_key(self) -> None:
        """PD-1d: the manifest produced by the generator has no `profile` key."""
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-u1-manifest-") as tmp:
            out = Path(tmp) / "staging"
            result = run_generator(out)
            self.assertEqual(
                result.returncode,
                0,
                "PD-1f/PD-1d: the generator failed without `--profile` (rc=%s):\n%s"
                % (result.returncode, result.stderr or result.stdout),
            )
            manifest_path = out / "manifest.json"
            self.assertTrue(
                manifest_path.is_file(),
                "PD-1d: the generator published no manifest.json under the staging tree",
            )
            raw = manifest_path.read_text(encoding="utf-8")
            try:
                manifest = json.loads(raw)
            except json.JSONDecodeError as exc:
                self.fail("PD-1d: manifest.json is not valid JSON: %s" % exc)
            keys = collect_keys(manifest)
            self.assertNotIn(
                "profile",
                keys,
                "PD-1d: the staging manifest still records the generation profile "
                "(keys: %s)" % sorted(set(keys)),
            )

    def test_pd_1e_committed_agents_carry_no_model_line(self) -> None:
        """PD-1e: no committed agent artifact carries a `model:` line."""
        agent_files = sorted((REPO_ROOT / "agents").glob("cdad-*.md")) + sorted(
            (REPO_ROOT / "agents" / "claude-code").glob("*.md")
        )
        self.assertTrue(
            agent_files,
            "fixture drift: no committed agent artifact under agents/ — PD-1e "
            "cannot be observed",
        )
        offenders: dict[str, list[int]] = {}
        for agent in agent_files:
            bad = [
                number
                for number, line in enumerate(
                    agent.read_text(encoding="utf-8").splitlines(), start=1
                )
                if MODEL_LINE_RE.match(line)
            ]
            if bad:
                offenders[str(agent.relative_to(REPO_ROOT))] = bad
        self.assertEqual(
            offenders,
            {},
            "PD-1e: committed agent artifacts still fix a model (line numbers): %s"
            % offenders,
        )

    def test_pd_1f_generator_requires_no_profile_and_rejects_the_flag(self) -> None:
        """PD-1f: no `--profile` -> rc=0; `--profile X` -> rc!=0 with a diagnostic."""
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-u1-cli-") as tmp:
            accepted = run_generator(Path(tmp) / "without-profile")
            self.assertEqual(
                accepted.returncode,
                0,
                "PD-1f: the generator rejected a run without `--profile` "
                "(rc=%s):\n%s" % (accepted.returncode, accepted.stderr or accepted.stdout),
            )
            rejected = run_generator(
                Path(tmp) / "with-profile", "--profile", "optimus"
            )
            self.assertNotEqual(
                rejected.returncode,
                0,
                "PD-1f: `--profile optimus` was accepted; the generator no longer "
                "knows profiles and must fail explicitly",
            )
            diagnostic = (rejected.stderr or rejected.stdout).strip()
            self.assertTrue(
                diagnostic,
                "PD-1f: rejection of `--profile` carried no diagnostic",
            )
            self.assertIn(
                "profile",
                diagnostic.lower(),
                "PD-1f: the diagnostic does not name the rejected option: %r" % diagnostic,
            )

    def test_pd_7a_generated_agents_fix_no_model(self) -> None:
        """PD-7a (generated) + INV-3: generated agents carry no model at all."""
        self.assertTrue(GENERATOR.is_file(), MISSING_GENERATOR_MSG)
        with tempfile.TemporaryDirectory(prefix="cdad-u1-generated-") as tmp:
            base = Path(tmp)
            for runtime in RUNTIMES:
                with self.subTest(runtime=runtime):
                    out = base / runtime
                    result = run_generator(out, runtime=runtime)
                    self.assertEqual(
                        result.returncode,
                        0,
                        "the generator failed for runtime=%s (rc=%s):\n%s"
                        % (runtime, result.returncode, result.stderr or result.stdout),
                    )
                    agents = sorted((out / "agents" / runtime).glob("cdad-*.md"))
                    self.assertTrue(
                        agents,
                        "fixture drift: runtime %s published no agents" % runtime,
                    )
                    for agent in agents:
                        text = agent.read_text(encoding="utf-8")
                        with self.subTest(runtime=runtime, agent=agent.name):
                            self.assertEqual(
                                [
                                    number
                                    for number, line in enumerate(
                                        text.splitlines(), start=1
                                    )
                                    if MODEL_LINE_RE.match(line)
                                ],
                                [],
                                "INV-3/PD-1e: generated %s/%s still fixes a model "
                                "in its frontmatter" % (runtime, agent.name),
                            )
                    orchestrator = out / "agents" / runtime / "cdad-orchestrator.md"
                    self.assertTrue(
                        orchestrator.is_file(),
                        "fixture drift: runtime %s published no orchestrator" % runtime,
                    )
                    matches = MODEL_NAME_RE.findall(
                        orchestrator.read_text(encoding="utf-8")
                    )
                    self.assertEqual(
                        matches,
                        [],
                        "PD-7a/INV-3: generated orchestrator for %s names models %s; "
                        "no installable text fixes or names a model any more"
                        % (runtime, sorted(set(matches))),
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
