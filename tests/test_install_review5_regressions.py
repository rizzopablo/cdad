#!/usr/bin/env python3
"""RED tests for 004-001 T5 reviewfix-RED (review-5, 4 BLOCKING + 1 recommendation).

Contract: docs/specs/004-001-canonical-runtime-artifacts/spec.md (PD-5, PD-7, PD-8
+ D4 ownership semantics + the profile invariants recorded by the manifest:
R3-O2 and spec invariant "el stack/perfil es entrada explícita registrada en el
manifest, no efecto oculto de la máquina") + review-5 findings B1-B4 and the
explicit-resolution recommendation.

ORACLE REPLACEMENTS (006-003 U2 — spec docs/specs/
006-003-installer-single-profile-delegation-config/spec.md, §2.1/PD-1a/D1 and
orchestrator amendment A-1). What changed and why, so no assert is dropped
silently:

- review-5 B4 (`test_review5_b4_*`, class `TestReview5ProfileAgreement`) asserted
  the PROFILE INVARIANT: a requested profile disagreeing with the staged profile
  had to be reported before installing, and the published labels had to be
  coherent. D1 retires the profile surface: `--economical|--optimus|--premium`
  are rejected (PD-1a) and `--basic` survives only as a DEPRECATED, EFFECT-FREE
  alias (D1); `CDAD_MODEL_PROFILE` is accepted and ignored with the same
  one-line warning (A-1); the marker `.cdad-models-profile` is no longer written.
  There is therefore no profile to disagree with: the test is REPLACED by
  `test_review5_b4_no_profile_disagreement_and_no_retired_marker`, which pins the
  surviving invariants (a clean `--basic` install, the deprecation notice, no
  retired marker anywhere under the root, no `profile` key in the install
  manifest). The `DISAGREEMENT_WORDS` lexicon and its `dry-run`/install
  disagreement asserts are RETIRED with the object they described; the flag
  rejection surface itself (PD-1a) is asserted by
  `tests/test_006_003_u2_installer_without_profiles.py` (unit U2), not here.
- `install.sh --basic` in the remaining recipes of this file is UNCHANGED: D1
  keeps it accepted, so every other test here stays valid as written.

These are FULL-JOURNEY regression tests over ONE install root
(install -> mutate/withdraw/reinstall/check/uninstall), following the sandbox +
subprocess black-box pattern of tests/test_install_ownership.py. The installer
is never read by these tests; only its published effects (files, exit codes,
stdout/stderr) and the declared staging manifest are inspected.

Existing tests are NOT touched; every test here covers a transition none of
them exercises:

  test_review5_b1_check_reports_modified_installed_agent   -> PD-5 (review-5 B1,
      install.sh:1216: --check compared the historical manifest hash against
      staging without hashing the installed bytes; a modified install PASSed)
  test_review5_b2_modified_skill_and_guard_reported_and_preserved -> PD-7
      (review-5 B2, install.sh:822/885: skills and the guard were overwritten
      by a reinstall without conflict reporting; they are owned artifacts too)
  test_review5_b3_withdrawn_agent_pending_removal_visible_and_uninstalled -> PD-5/D4
      (review-5 B3, install.sh:733/744: reinstall forgot obsolete installed
      files — dropped from the manifest, --check PASSed, uninstall never freed
      them. They must stay REGISTERED as pending removal, stay visible to
      --check, and be retired by --uninstall)
  test_review5_b4_no_profile_disagreement_and_no_retired_marker -> 006-003 D1/PD-1a
      (replaces review-5 B4's profile invariant: with no profile surface there is
      no disagreement to report, `--basic` warns once and no retired marker is
      published; the "labels must be coherent" invariant survives as the
      absence of the retired label)
  test_review5_e1_uninstall_reports_modified_agent_and_preserves -> PD-7/D4
      (review-5 recommendation: historical ownership is not automatic
      authorization to discard later local changes; permanent-explicit
      resolution, same conflict-and-preserve policy as reinstall)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "install.sh"
INSTALL_MANIFEST_NAME = ".cdad-install-manifest.json"
PROFILE_MARKER_NAME = ".cdad-models-profile"

# Oracle note (red-005 adjustment): the installer reports in UPPERCASE
# ("CONFLICT: ..."), so the lexicon is case-insensitive.
# 006-003 U2 replacement: the `DISAGREEMENT_WORDS` lexicon (and its dry-run /
# install asserts) is RETIRED with the profile object it described — see the
# ORACLE REPLACEMENTS note in the module docstring. The uninstall lexicon below
# is untouched.
# --uninstall reports the local modification and its preservation decision
# ("CONFLICT: ... modified locally since the recorded install; PRESERVED for
# explicit resolution"); the lexicon covers the modification-report axis.
UNINSTALL_REPORT_WORDS = (
    r"(?i)(conflict|modified|preserv|explicit resolution|desacuerdo|disagree)"
)

# D1/§2.1: the deprecation notice that `--basic` (and `CDAD_MODEL_PROFILE`) must
# produce — one line, while the run stays accepted.
DEPRECATION_RE = re.compile(r"(?i)(deprecat|obsolet)")
BASIC_ALIAS = "--basic"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tail(text: str, lines: int = 5) -> str:
    """Last `lines` lines of an installer output (keeps failure logs small)."""
    return "\n".join(text.strip().splitlines()[-lines:])


def _basic_deprecation_notices(output: str) -> list[str]:
    """Deprecation notice lines of ONE installer run that name `--basic`."""
    return [
        line
        for line in output.splitlines()
        if DEPRECATION_RE.search(line) and BASIC_ALIAS in line
    ]


def run_installer(
    repo: Path, install_root: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    """Run the installer of `repo` black-box against an isolated root."""
    env = os.environ.copy()
    env["CDAD_INSTALL_ROOT"] = str(install_root)
    env["CDAD_SKILL_EXTRA_DIRS"] = ""
    return subprocess.run(
        ["bash", str(repo / "install.sh"), *args],
        cwd=str(repo),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def load_staging_manifest(repo: Path) -> dict:
    path = repo / "build" / "staging" / "manifest.json"
    assert path.is_file(), (
        "T5 precondition: build/staging/manifest.json (produced by T3) is a "
        "declared input of the T5 contract; regenerate staging first"
    )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(
            f"T5 precondition: staging manifest is not valid JSON: {exc}"
        ) from exc
    assert isinstance(data.get("artifacts"), list) and data["artifacts"], (
        "T5 precondition: staging manifest must declare a non-empty artifacts list"
    )
    return data


def staging_product() -> Path:
    """Raíz de producto con staging garantizado (portabilidad, review-t1/T6).

    Devuelve el checkout real si ya tiene build/staging/manifest.json; si no,
    una copia temporal con staging generado por `make staging` (el fixture
    nunca escribe en el checkout real)."""
    from tests.product_staging import product_root

    return product_root()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(
            f"T5 precondition: staging manifest is not valid JSON: {exc}"
        ) from exc
    assert isinstance(data.get("artifacts"), list) and data["artifacts"], (
        "T5 precondition: staging manifest must declare a non-empty artifacts list"
    )
    return data


def write_staging_manifest(repo: Path, data: dict) -> None:
    path = repo / "build" / "staging" / "manifest.json"
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def pick_staged_entry(staging_manifest: dict, prefix: str = "agents/opencode/") -> dict:
    entries = sorted(
        (a for a in staging_manifest["artifacts"]
         if str(a.get("file", "")).startswith(prefix)),
        key=lambda a: a["file"],
    )
    assert entries, f"T5 precondition: staging has no artifact under {prefix}"
    return entries[0]


def find_deployed(install_root: Path, filename: str) -> Path:
    matches = [p for p in install_root.rglob(filename) if p.is_file()]
    assert matches, (
        f"T5 contract: the installer did not deploy {filename} anywhere under "
        "the install root"
    )
    return matches[0]


def find_profile_markers(install_root: Path) -> list[Path]:
    """Discover the RETIRED profile label file(s) under an install root.

    The marker `.cdad-models-profile` was published surface (installer help:
    precedence `flag > env CDAD_MODEL_PROFILE > marker .cdad-models-profile >
    optimus`). 006-003 D1 retires it: the replacement oracle asserts it is never
    written (the exact destination directory never was part of the contract, so
    the file is discovered by name under the install root).
    """
    found: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(install_root):
        if PROFILE_MARKER_NAME in filenames:
            found.append(Path(dirpath) / PROFILE_MARKER_NAME)
    return sorted(found)


class SandboxFixture(unittest.TestCase):
    """A full copy of the repository so tests can exercise the installer
    against a MUTABLE staging tree without ever touching the real repository.
    The copy is blind fixture data; the test never reads implementation files."""

    @classmethod
    def setUpClass(cls) -> None:
        assert INSTALLER.is_file(), (
            f"T5 precondition: installer missing at {INSTALLER}"
        )
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-t5b-sandbox-")
        base = Path(cls._tmp.name)
        cls.sandbox = base / "sandbox"
        shutil.copytree(
            REPO_ROOT,
            cls.sandbox,
            symlinks=True,
            ignore=shutil.ignore_patterns(".pytest_cache", "__pycache__"),
        )
        cls.pristine_staging = base / "pristine-staging"
        if (cls.sandbox / "build" / "staging" / "manifest.json").is_file():
            shutil.copytree(cls.sandbox / "build" / "staging", cls.pristine_staging)
        else:
            # Portabilidad (review-t1/T6): un checkout limpio no trae
            # build/staging; el fixture lo genera en la COPIA (nunca en el
            # checkout real) y el sandbox lo obtiene de esa copia.
            from tests.product_staging import product_root

            shutil.copytree(
                product_root() / "build" / "staging",
                cls.sandbox / "build" / "staging",
            )
            shutil.copytree(cls.sandbox / "build" / "staging", cls.pristine_staging)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def setUp(self) -> None:
        staging = self.sandbox / "build" / "staging"
        shutil.rmtree(staging)
        shutil.copytree(self.pristine_staging, staging)


class TestReview5InstalledDrift(unittest.TestCase):
    """Real-repo installer: --check must observe the INSTALLED bytes (B1)."""

    def test_review5_b1_check_reports_modified_installed_agent(self) -> None:
        """PD-5 (review-5 B1): after a successful install, modifying the
        INSTALLED agent and running --check must report the drift (the check
        hashes the installed bytes, not only the historical manifest hash)."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5b-b1-") as root_dir:
            root = Path(root_dir)
            first = run_installer(staging_product(), root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            installed = find_deployed(root, "cdad-architect.md")
            modified = installed.read_bytes() + b"\n<!-- local edit post-install -->\n"
            installed.write_bytes(modified)
            name = installed.name

            check = run_installer(staging_product(), root, "--check")
            check_out = check.stdout + check.stderr
            # RED pivot (B1): today the check PASSes because it compares the
            # hash recorded at install time against staging — it never hashes
            # the actually-installed bytes. The must-observe behavior: exit
            # non-zero, naming the drifted installed file.
            self.assertNotEqual(
                check.returncode,
                0,
                f"review-5 B1 (PD-5): --check must report the modified "
                f"installed {name}; it passed silently:\n{check_out}",
            )
            self.assertIn(
                name,
                check_out,
                f"review-5 B1 (PD-5): the drift report must name the modified "
                f"installed file {name}; check output:\n{check_out}",
            )

            # The conflicted bytes stay preserved until explicit resolution.
            self.assertEqual(
                installed.read_bytes(),
                modified,
                "review-5 B1 (PD-7): --check must neither overwrite nor revert "
                "the locally modified installed file",
            )


class TestReview5SkillGuardConflicts(unittest.TestCase):
    """Real-repo installer: the modified skill and the guard are owned
    artifacts too — same conflict-and-preserve policy (B2)."""

    def test_review5_b2_modified_skill_and_guard_reported_and_preserved(self) -> None:
        """PD-7 (review-5 B2): a locally modified installed skill and a locally
        modified installed guard must be reported as conflicts by dry-run AND
        install, and must be preserved byte for byte."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5b-b2-") as root_dir:
            root = Path(root_dir)
            first = run_installer(staging_product(), root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            skill = find_deployed(root, "SKILL.md")
            guard = find_deployed(root, "path-guard.sh")
            skill_mod = skill.read_bytes() + b"\n<!-- local skill edit must survive -->\n"
            skill.write_bytes(skill_mod)
            guard_mod = guard.read_bytes() + b"\n# local guard edit must survive\n"
            guard.write_bytes(guard_mod)
            skill_rel = str(skill.relative_to(root))
            guard_rel = str(guard.relative_to(root))

            dry = run_installer(staging_product(), root, "--dry-run", "--basic")
            dry_out = dry.stdout + dry.stderr
            # RED pivot (B2): today the dry-run reports NO conflict for these
            # owned files and a later reinstall silently overwrites both.
            self.assertRegex(
                dry_out,
                r"(?i)conflict",
                "review-5 B2 (PD-7): dry-run must report the locally modified "
                f"skill ({skill_rel}) and guard ({guard_rel}) as conflicts; "
                f"dry-run output:\n{dry_out}",
            )
            for rel in (skill_rel, guard_rel):
                self.assertIn(
                    rel,
                    dry_out,
                    f"review-5 B2 (PD-7): the conflict report must name the "
                    f"affected path {rel}; dry-run output:\n{dry_out}",
                )

            second = run_installer(staging_product(), root, "--basic")
            second_out = second.stdout + second.stderr
            self.assertRegex(
                second_out,
                r"(?i)conflict",
                "review-5 B2 (PD-7): install must also report the modified "
                f"skill/guard as conflicts; install output:\n{second_out}",
            )
            self.assertEqual(
                skill.read_bytes(),
                skill_mod,
                "review-5 B2 (PD-7): the modified skill must be preserved, "
                "neither overwritten nor deleted without explicit resolution",
            )
            self.assertEqual(
                guard.read_bytes(),
                guard_mod,
                "review-5 B2 (PD-7): the modified guard must be preserved, "
                "neither overwritten nor deleted without explicit resolution",
            )


class TestReview5WithdrawnAgent(SandboxFixture):
    """Sandbox installer: reinstalling after a staged artifact is withdrawn
    must keep the obsolete installed file REGISTERED until uninstall retires it."""

    def test_review5_b3_withdrawn_agent_pending_removal_visible_and_uninstalled(self) -> None:
        """PD-5/D4 (review-5 B3): the full transition install -> withdraw the
        staged agent -> reinstall -> --check -> --uninstall must (1) keep the
        old installed file recorded as pending removal, (2) keep it VISIBLE to
        --check, and (3) retire it via --uninstall."""
        staging_manifest = load_staging_manifest(self.sandbox)
        entry = pick_staged_entry(staging_manifest)
        obsolete_rel = entry["file"]
        obsolete_name = Path(obsolete_rel).name

        with tempfile.TemporaryDirectory(prefix="cdad-t5b-b3-") as root_dir:
            root = Path(root_dir)
            first = run_installer(self.sandbox, root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
            old_installed = find_deployed(root, obsolete_name)
            old_rel = str(old_installed.relative_to(root))

            # Upstream withdraws the artifact: it disappears from staging.
            (self.sandbox / "build" / "staging" / obsolete_rel).unlink()
            staging_manifest["artifacts"] = [
                a for a in staging_manifest["artifacts"] if a["file"] != obsolete_rel
            ]
            write_staging_manifest(self.sandbox, staging_manifest)

            second = run_installer(self.sandbox, root, "--basic")
            second_out = second.stdout + second.stderr
            self.assertEqual(second.returncode, 0, second_out)
            # Pending retirement: the file waits for explicit resolution.
            self.assertTrue(
                old_installed.is_file(),
                f"review-5 B3 (D4): reinstalling after {obsolete_rel} was "
                f"withdrawn from staging must leave the old installed file "
                f"{old_rel} pending retirement (explicit resolution), it "
                f"already vanished; output:\n{second_out}",
            )

            check = run_installer(self.sandbox, root, "--check")
            check_out = check.stdout + check.stderr
            # RED pivot (B3): today the reinstall forgets the old file (it
            # leaves the manifest and --check PASSes silently.
            self.assertNotEqual(
                check.returncode,
                0,
                f"review-5 B3 (PD-5): --check must flag the pending-removal "
                f"installed file {old_rel} (registered but no longer staged); "
                f"it passed silently:\n{check_out}",
            )
            self.assertIn(
                obsolete_name,
                check_out,
                f"review-5 B3 (PD-5): the --check report must name the "
                f"pending-removal file {old_rel}; check output:\n{check_out}",
            )

            uninstall = run_installer(self.sandbox, root, "--uninstall")
            uninstall_out = uninstall.stdout + uninstall.stderr
            self.assertEqual(
                uninstall.returncode,
                0,
                f"review-5 B3: --uninstall must retire the registered "
                f"pending-removal file {old_rel}; output:\n{uninstall_out}",
            )
            self.assertFalse(
                old_installed.exists(),
                f"review-5 B3 (PD-5/D4): --uninstall must REMOVE the "
                f"registered pending-removal file {old_rel}; it survived:\n"
                f"{uninstall_out}",
            )


class TestReview5ProfileSurfacesRetired(SandboxFixture):
    """Sandbox installer: with D1 there is no profile any more — the former
    'requested profile vs staged profile' disagreement (review-5 B4) has no
    object, and the retired label surface must stay unpublished."""

    def test_review5_b4_no_profile_disagreement_and_no_retired_marker(self) -> None:
        """ORACLE REPLACEMENT (006-003 U2 — §2.1/PD-1a/D1/A-1). review-5 B4 asked
        that a `--basic` request disagreeing with a staged profile be reported
        and that the published profile labels stay coherent. D1 retires the
        profile surface, so the surviving oracle is its absence:

          1. the request is accepted (rc=0) and warns ONCE that `--basic` is a
             deprecated alias with no effect (D1, INV-7: nothing silent),
          2. no `.cdad-models-profile` marker is published anywhere under the
             root (the retired label cannot contradict anything),
          3. the install manifest records no `profile` key (nothing
             profile-shaped can be a machine-hidden effect either).

        The dry-run disagreement asserts and the `DISAGREEMENT_WORDS` lexicon are
        retired with the object they described; the rejection of the retired
        `--<profile>` flags (PD-1a) is asserted by the U2 focal test.
        """
        with tempfile.TemporaryDirectory(prefix="cdad-t5b-b4-") as root_dir:
            root = Path(root_dir)

            dry = run_installer(self.sandbox, root, "--dry-run", "--basic")
            dry_out = dry.stdout + dry.stderr
            self.assertEqual(dry.returncode, 0, dry_out)

            result = run_installer(self.sandbox, root, "--basic")
            result_out = result.stdout + result.stderr
            self.assertEqual(
                result.returncode,
                0,
                f"review-5 B4 (replacement, D1): `--basic` must stay accepted as "
                f"a deprecated alias so the existing recipes keep working; "
                f"install output:\n{result_out}",
            )

            dry_notices = _basic_deprecation_notices(dry_out)
            self.assertEqual(
                len(dry_notices),
                1,
                "review-5 B4 (replacement, D1/INV-7): `--dry-run --basic` must "
                "produce exactly one one-line deprecation notice, found "
                f"{len(dry_notices)} (dry-run tail:\n{tail(dry_out, 5)})",
            )

            result_notices = _basic_deprecation_notices(result_out)
            self.assertEqual(
                len(result_notices),
                1,
                "review-5 B4 (replacement, D1/INV-7): `--basic` must produce "
                "exactly one one-line deprecation notice on install, found "
                f"{len(result_notices)} (install tail:\n{tail(result_out, 5)})",
            )

            markers = find_profile_markers(root)
            self.assertEqual(
                markers,
                [],
                "review-5 B4 (replacement, D1): the install published the "
                f"retired profile marker(s) {markers}; the label surface is "
                "gone and cannot be coherent or contradictory any more",
            )

            manifest = json.loads(
                (root / INSTALL_MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertNotIn(
                "profile",
                manifest,
                "review-5 B4 (replacement, PD-1d/D1): the install manifest still "
                "records `profile`; the staged surface it comes from no longer "
                "has one",
            )


class TestReview5UninstallModified(unittest.TestCase):
    """Real-repo installer: uninstall reports a locally modified owned file."""

    def test_review5_e1_uninstall_reports_modified_agent_and_preserves(self) -> None:
        """PD-7/D4 (review-5 recommendation): historical ownership is not
        automatic authorization to discard later local changes — --uninstall
        must inform the local modification (naming the path) and preserve the
        file for explicit resolution."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5b-e1-") as root_dir:
            root = Path(root_dir)
            first = run_installer(staging_product(), root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            installed = find_deployed(root, "cdad-architect.md")
            modified = installed.read_bytes() + b"\n<!-- local edit pre-uninstall -->\n"
            installed.write_bytes(modified)
            rel = str(installed.relative_to(root))

            uninstall = run_installer(staging_product(), root, "--uninstall")
            uninstall_out = uninstall.stdout + uninstall.stderr
            self.assertRegex(
                uninstall_out,
                UNINSTALL_REPORT_WORDS,
                f"review-5 E (PD-7/D4): --uninstall must inform that "
                f"{rel} was locally modified; uninstall output:\n{uninstall_out}",
            )
            self.assertIn(
                rel,
                uninstall_out,
                "review-5 E (PD-7/D4): the uninstall report must name the "
                f"modified path {rel}; uninstall output:\n{uninstall_out}",
            )
            self.assertTrue(
                installed.is_file(),
                f"review-5 E (PD-7/D4): the locally modified {rel} must be "
                "preserved until explicit resolution, not silently deleted by "
                f"--uninstall; output:\n{uninstall_out}",
            )
            self.assertEqual(
                installed.read_bytes(),
                modified,
                "review-5 E (PD-7/D4): the preserved local modification must "
                "keep exactly the user's bytes",
            )


if __name__ == "__main__":
    unittest.main()
