"""Black-box RED coverage for 009-001 agent model overlay.

Promise mapping: PC-1, PC-2, PC-3, PC-4, PC-5, PC-6 and PC-7 are exercised
as single user-visible outcomes below. Without these tests, the user can lose
their selected model, miss an update, be told a conflicted file is owned, get
misled by check/validation diagnostics, or lose their configuration on
uninstall.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MANIFEST = ".cdad-install-manifest.json"


def run(repo: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CDAD_INSTALL_ROOT"] = str(root)
    env["CDAD_SKILL_EXTRA_DIRS"] = ""
    return subprocess.run(
        ["bash", str(repo / "install.sh"), *args], cwd=repo, env=env,
        text=True, capture_output=True, check=False,
    )


class AgentOverlayContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="cdad-009-overlay-")
        cls.base = Path(cls.tmp.name)
        cls.repo = cls.base / "product"
        shutil.copytree(REPO, cls.repo, symlinks=True,
                        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        staging = cls.repo / "build/staging"
        if not (staging / "manifest.json").is_file():
            from tests.product_staging import product_root
            shutil.copytree(product_root() / "build/staging", staging)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.root_tmp = tempfile.TemporaryDirectory(prefix="cdad-009-root-")
        self.root = Path(self.root_tmp.name)

    def tearDown(self) -> None:
        self.root_tmp.cleanup()

    def staged_agent(self) -> tuple[Path, Path, str]:
        manifest = json.loads((self.repo / "build/staging/manifest.json").read_text())
        entries = [e for e in manifest["artifacts"]
                   if str(e.get("file", "")).startswith("agents/")
                   and Path(e["file"]).suffix == ".md"]
        self.assertTrue(entries, "fixture requires a staged installable agent")
        # Pick the opencode artifact explicitly: installed_agent() resolves the
        # corresponding runtime destination, so the staged source and target
        # always describe the same artifact regardless of manifest ordering.
        entry = next(e for e in sorted(entries, key=lambda e: e["file"])
                     if Path(e["file"]).parts[1] == "opencode"
                     and e["file"].endswith("cdad-reviewer.md"))
        source = self.repo / "build/staging" / entry["file"]
        return source, source.relative_to(self.repo / "build/staging"), entry["file"]

    def install(self, *args: str) -> subprocess.CompletedProcess[str]:
        return run(self.repo, self.root, *args)

    def installed_agent(self, name: str) -> Path:
        runtime = Path(name).parts[1]
        matches = sorted(
            (p for p in self.root.rglob(Path(name).name)
             if p.is_file() and runtime in p.parts),
            key=lambda p: p.as_posix(),
        )
        self.assertTrue(matches, f"expected installed agent at a path under arena: {name}")
        return matches[0]

    def test_pc1_preserves_valid_frontmatter_model_without_conflict(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        body = target.read_bytes()
        self.assertTrue(body.startswith(b"---\n"), "fixture agent needs delimited frontmatter")
        end = body.find(b"\n---\n", 4)
        self.assertGreater(end, 0, "fixture agent needs a closing frontmatter delimiter")
        target.write_bytes(body[:end] + b"\nmodel: user/chosen-model" + body[end:])
        result = self.install()
        actual = target.read_bytes()
        self.assertIn(b"model: user/chosen-model", actual,
                      "PC-1: installing must preserve the exact user model value")
        agent_conflict_lines = [
            line for line in (result.stdout + result.stderr).splitlines()
            if "cdad-reviewer.md" in line and "CONFLICT" in line.upper()
        ]
        self.assertEqual(agent_conflict_lines, [],
                         "PC-1: a valid frontmatter overlay is not a conflict for cdad-reviewer.md")

    def test_pc2_update_rebases_non_overlay_bytes_onto_new_staging(self) -> None:
        self.install().check_returncode()
        staged, _, name = self.staged_agent()
        target = self.installed_agent(name)
        original = staged.read_bytes()
        target.write_bytes(original.replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        upstream = original + b"\nUpstream update sentinel.\n"
        staged.write_bytes(upstream)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = target.read_bytes()
        self.assertIn(b"model: user/chosen-model", installed,
                      "PC-2: the installed user overlay must survive the update")
        self.assertIn(b"Upstream update sentinel.", installed,
                      "PC-2: an upstream staging change must reach the installed copy")

    def test_pc3_overlay_remains_owned_and_unchanged_check_is_successful(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        data = target.read_bytes()
        target.write_bytes(data.replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        manifest_path = self.root / MANIFEST
        self.assertTrue(manifest_path.is_file(), "PC-3: installed overlay must remain owned")
        manifest = json.loads(manifest_path.read_text())
        rel = target.relative_to(self.root).as_posix()
        self.assertEqual(manifest["artifacts"][rel]["sha256"], hashlib.sha256(target.read_bytes()).hexdigest(),
                         "PC-3: ownership digest must describe installed bytes")
        second = self.install()
        self.assertIn("sync", (second.stdout + second.stderr).lower(),
                      "PC-3: a second unchanged install reports SYNC")
        check = self.install("--check")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_pc4_non_overlay_local_edit_is_preserved_and_not_adopted(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        target.write_bytes(target.read_bytes() + b"\nlocal body edit\n")
        local = target.read_bytes()
        result = self.install()
        output = result.stdout + result.stderr
        self.assertEqual(target.read_bytes(), local, "PC-4: conflicting local bytes must not be overwritten")
        self.assertIn("conflict", output.lower(), "PC-4: local non-overlay drift must be diagnosed")
        manifest = json.loads((self.root / MANIFEST).read_text())
        self.assertNotIn(target.relative_to(self.root).as_posix(), manifest.get("artifacts", {}),
                         "PC-4: conflicted user content must not be adopted as owned")
        check = self.install("--check")
        self.assertNotEqual(check.returncode, 0, "PC-4: unresolved drift is not a successful check")

    def test_pc5_validator_rejects_installable_model_but_accepts_installed_overlay(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        target.write_bytes(target.read_bytes().replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        # Installable repository text may not distribute a model; restore every
        # modified byte before exercising the valid installed-user-overlay leg.
        staged, _, _ = self.staged_agent()
        original = staged.read_bytes()
        staged.write_bytes(original.replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        env = {**os.environ, "CDAD_INSTALL_ROOT": str(self.root)}
        rejected = subprocess.run(
            ["bash", "scripts/validate-subagents.sh"], cwd=self.repo, env=env,
            text=True, capture_output=True, check=False, timeout=300,
        )
        staged.write_bytes(original)
        self.assertNotEqual(rejected.returncode, 0,
                            "PC-5: validator must reject model declarations in installable text")
        accepted = subprocess.run(
            ["bash", "scripts/validate-subagents.sh"], cwd=self.repo, env=env,
            text=True, capture_output=True, check=False, timeout=300,
        )
        accepted_output = accepted.stdout + accepted.stderr
        # Other installable-text drift (for example, an unrelated agent) must
        # not make this assertion blame the valid user-owned installed overlay.
        self.assertNotIn(target.relative_to(self.root).as_posix(), accepted_output,
                         "PC-5: a valid installed overlay is not a validator failure")

    def test_pc6_check_diagnostics_name_installed_agent_and_overlay(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        target.write_bytes(target.read_bytes().replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        result = self.install("--check")
        output = result.stdout + result.stderr
        self.assertIn(target.relative_to(self.root).as_posix(), output,
                      "PC-6: diagnostics identify the installed destination path")
        self.assertIn("overlay", output.lower(), "PC-6: check explains the preserved overlay")

    def test_pc7_uninstall_preserves_owned_agent_with_overlay_byte_for_byte(self) -> None:
        initial = self.install()
        self.assertEqual(initial.returncode, 0, initial.stdout + initial.stderr)
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        target.write_bytes(target.read_bytes().replace(b"---\n", b"---\nmodel: user/chosen-model\n", 1))
        registered = self.install()
        self.assertEqual(registered.returncode, 0, registered.stdout + registered.stderr)
        before = target.read_bytes()
        result = self.install("--uninstall")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(target.exists(), "PC-7: uninstall must preserve the user-configured agent")
        self.assertEqual(target.read_bytes(), before, "PC-7: preserved overlay agent remains byte-identical")
        self.assertIn("preserv", (result.stdout + result.stderr).lower(),
                      "PC-7: uninstall communicates why the agent remains")

    def _set_model(self, target: Path, model: str | None) -> None:
        data = target.read_bytes()
        end = data.find(b"\n---\n", 4)
        self.assertGreater(end, 0, "fixture agent needs delimited frontmatter")
        front = data[:end]
        lines = [line for line in front.splitlines() if not line.startswith(b"model:")]
        if model is not None:
            lines.append(f"model: {model}".encode())
        target.write_bytes(b"\n".join(lines) + data[end:])

    def _assert_owned_clean_check(self, target: Path) -> None:
        manifest = json.loads((self.root / MANIFEST).read_text())
        rel = target.relative_to(self.root).as_posix()
        self.assertEqual(manifest["artifacts"][rel]["sha256"],
                         hashlib.sha256(target.read_bytes()).hexdigest(),
                         "PC-3: manifest digest must match installed bytes")
        check = self.install("--check")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_pc1a_changing_user_model_keeps_agent_owned_and_check_clean(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        self._set_model(target, "user/A")
        self.install().check_returncode()
        self._set_model(target, "user/B")
        result = self.install()
        output = result.stdout + result.stderr
        self.assertNotIn("CONFLICT", output.upper(), "PC-1/PC-3: changing model is not a conflict")
        self.assertIn(b"model: user/B", target.read_bytes(), "PC-1: latest user model is retained")
        self._assert_owned_clean_check(target)

    def test_pc1b_removing_user_model_rebases_to_staging_and_check_clean(self) -> None:
        self.install().check_returncode()
        staged, _, name = self.staged_agent()
        target = self.installed_agent(name)
        self._set_model(target, "user/A")
        self.install().check_returncode()
        self._set_model(target, None)
        result = self.install()
        output = result.stdout + result.stderr
        self.assertNotIn("CONFLICT", output.upper(), "PC-1/PC-3: removing model is not a conflict")
        self.assertEqual(target.read_bytes(), staged.read_bytes(),
                         "PC-2: with no overlay, installed bytes equal staging")
        self._assert_owned_clean_check(target)

    def test_pc3_legacy_unowned_overlay_conflict_is_adopted_on_update(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        self._set_model(target, "user/A")
        self.install().check_returncode()
        manifest_path = self.root / MANIFEST
        manifest = json.loads(manifest_path.read_text())
        del manifest["artifacts"][target.relative_to(self.root).as_posix()]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        result = self.install()
        output = result.stdout + result.stderr
        self.assertNotIn("CONFLICT", output.upper(), "PC-3: legacy overlay is repaired without conflict")
        self.assertIn(b"model: user/A", target.read_bytes(), "PC-1: legacy user model survives")
        self._assert_owned_clean_check(target)

    def test_pc6_check_summary_names_installed_path_for_outside_overlay_drift(self) -> None:
        self.install().check_returncode()
        _, _, name = self.staged_agent()
        target = self.installed_agent(name)
        target.write_bytes(target.read_bytes() + b"\nlocal drift outside overlay\n")
        result = self.install("--check")
        output = result.stdout + result.stderr
        summary = next((line for line in output.splitlines()
                        if line.startswith("Check: FAIL — ")), "")
        self.assertTrue(summary, "PC-6: failed check has a final Check: FAIL summary")
        self.assertIn(target.relative_to(self.root).as_posix(), summary,
                      "PC-6: summary names the installed destination")
        self.assertNotIn("build/staging", summary)
        self.assertNotIn("agents/opencode/", summary)

    def test_pc5_validator_uses_agent_overlay_for_installable_model_check(self) -> None:
        validator = (self.repo / "scripts/validate-subagents.sh").read_text()
        self.assertNotIn("^model:", validator,
                         "PC-5/INV-2: validator must not duplicate the model-key rule")
