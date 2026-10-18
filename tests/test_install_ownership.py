#!/usr/bin/env python3
"""RED tests for 004-001 T5: installation with ownership (D4 manifest semantics).

Contract: docs/specs/004-001-canonical-runtime-artifacts/spec.md (PD-5, PD-6,
PD-7, PD-8, PD-18) + plan.md row T5 + review-3 R3-O2 (the install manifest
records the RESOLVED stack).

Black-box: `install.sh` runs as a subprocess and only its published effects
are inspected. The installer implementation is never read by these tests.

New observable interface pinned by these tests (the only new surface T5 adds):

  Ownership manifest: <CDAD_INSTALL_ROOT>/.cdad-install-manifest.json
    JSON object with at least:
      "runtime":   str  (equals staging manifest "runtime")
      "stack":     str  (RESOLVED stack, equals staging manifest "stack"; R3-O2)
      "artifacts": object mapping install-root-relative destination path ->
                   {"sha256": <hex of the installed bytes>,
                    "source": <staging-relative path of the deployed artifact>}

ORACLE REPLACEMENT (006-003 U2 — spec docs/specs/006-003-installer-single-
profile-delegation-config/spec.md, PD-1d/D1). The pinned interface above no
longer declares a `"profile"` key: D1 retires the profile surface from the
installer and from the staging manifest it consumes, so there is no profile for
the ownership manifest to record (it came from staging, install.sh:954). The
former assertion `manifest["profile"] == staging_manifest["profile"]` is
REPLACED by the stronger absence assertion in
`test_t5_r3o2_install_manifest_records_resolved_stack` below. The staging side of
PD-1d (the generator writes no `profile` key) is asserted on freshly generated
staging by `tests/test_006_003_u1_generator_without_profiles.py`; this file does
not depend on the possibly stale build/staging of the checkout.

Staging contract: the installer consumes build/staging/manifest.json next to
install.sh ({"artifacts": [{"file", "sha256", "sources", "regenerate"}]}) and
deploys the STAGED bytes; it never reads sources/ (PD-18).

Test -> postcondition mapping (plan T5 RED list; objective cases 1-10 + R3-O2):

  test_t5_case1_first_install_deploys_staged_set_and_registers_ownership -> PD-6
  test_t5_case2_modified_installed_file_reported_and_preserved           -> PD-7
  test_t5_case3_check_reports_staging_obsolete_artifact                  -> PD-5
  test_t5_case4_foreign_files_survive_reinstall                          -> PD-8
  test_t5_case5_symlink_at_destination_reported_not_followed             -> PD-7
  test_t5_case6_failed_install_reports_and_retry_heals_ownership         -> PD-6/D4
  test_t5_case7_uninstall_removes_only_manifest_entries                  -> PD-8
  test_t5_case8_install_deploys_staging_bytes_without_sources            -> PD-18
  test_t5_case9_dry_run_announces_exactly_the_staged_set                 -> plan T5 (dry-run exacto)
  test_t5_case10_check_reports_installed_drift_vs_staging                -> PD-5
  test_t5_r3o2_install_manifest_records_resolved_stack                   -> R3-O2
      (+ 006-003 PD-1d/D1: the manifest records no `profile`)

PD-9 note: the plan defers the public-layout / opt-in-flag decision to T6
("decision del flag ... despues de migrar fixtures"). The enforceable-today
slice (every destination confined to CDAD_INSTALL_ROOT) is already covered by
the 003-001 P6 suite, so no test here duplicates it.
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

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = REPO_ROOT / "install.sh"
INSTALL_MANIFEST_NAME = ".cdad-install-manifest.json"

FOREIGN_BYTES = b"user content that must survive\n"
CANARY_BYTES = b"canary target bytes\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def staging_product() -> Path:
    """Raíz de producto con staging garantizado (portabilidad, review-t1/T6).

    Devuelve el checkout real si ya tiene build/staging/manifest.json; si no,
    una copia temporal con staging generado por `make staging` (el fixture
    nunca escribe en el checkout real)."""
    from tests.product_staging import product_root

    return product_root()


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


def install_manifest_path(install_root: Path) -> Path:
    return install_root / INSTALL_MANIFEST_NAME


def load_install_manifest(install_root: Path) -> dict:
    path = install_manifest_path(install_root)
    assert path.is_file(), (
        f"T5 contract (PD-6): an install must publish the ownership manifest "
        f"{INSTALL_MANIFEST_NAME} at the install root; it is missing"
    )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AssertionError(
            f"T5 contract: ownership manifest is not valid JSON: {exc}"
        ) from exc


def assert_manifest_consistent(tc: unittest.TestCase, root: Path) -> dict:
    """The manifest claims exactly what is installed, byte for byte (no half state)."""
    manifest = load_install_manifest(root)
    artifacts = manifest.get("artifacts")
    tc.assertIsInstance(
        artifacts,
        dict,
        "T5 contract (PD-6): the ownership manifest must map destinations to "
        f"provenance; got: {type(artifacts).__name__}",
    )
    tc.assertTrue(
        artifacts,
        "T5 contract (PD-6): the ownership manifest must not be empty after "
        "a successful install",
    )
    for rel, record in artifacts.items():
        tc.assertIsInstance(
            record,
            dict,
            f"T5 contract: manifest entry for {rel} must carry provenance fields",
        )
        parts = Path(rel).parts
        tc.assertFalse(
            rel.startswith("/") or ".." in parts,
            f"T5 contract (PD-9/D4): manifest path escapes the install root: {rel}",
        )
        installed = root / rel
        tc.assertTrue(
            installed.is_file(),
            f"T5 contract (D4): manifest claims {rel} but the file is not "
            "installed (half state)",
        )
        tc.assertEqual(
            record.get("sha256"),
            sha256_bytes(installed.read_bytes()),
            f"T5 contract (D4): manifest sha256 mismatch for {rel} (half state)",
        )
    return manifest


class SandboxFixture(unittest.TestCase):
    """A full copy of the repository so tests can exercise the installer
    against a MUTABLE staging tree (and an inaccessible sources/) without ever
    touching the real repository. The copy is blind fixture data; the test
    never reads implementation files."""

    @classmethod
    def setUpClass(cls) -> None:
        assert INSTALLER.is_file(), (
            f"T5 precondition: installer missing at {INSTALLER}"
        )
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-t5-sandbox-")
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


class TestT5FirstInstallOwnership(unittest.TestCase):
    """Real-repo installer: first-install ownership semantics (D4)."""

    def test_t5_case1_first_install_deploys_staged_set_and_registers_ownership(self) -> None:
        """PD-6: without a prior manifest, the install registers ownership and
        deletes nothing; the complete staged set is deployed."""
        staging_manifest = load_staging_manifest(staging_product())
        with tempfile.TemporaryDirectory(prefix="cdad-t5-first-") as root_dir:
            root = Path(root_dir)
            foreign = root / "user-keep.txt"
            foreign.write_bytes(FOREIGN_BYTES)

            result = run_installer(staging_product(), root, "--basic")
            self.assertEqual(
                result.returncode, 0, result.stderr or result.stdout
            )

            self.assertEqual(
                foreign.read_bytes(),
                FOREIGN_BYTES,
                "PD-6: a first install must not delete anything that was "
                "already in the install root",
            )
            for entry in staging_manifest["artifacts"]:
                name = Path(entry["file"]).name
                deployed = [p for p in root.rglob(name) if p.is_file()]
                self.assertTrue(
                    deployed,
                    f"D4: the installer did not deploy staged artifact "
                    f"{entry['file']}",
                )

            # RED pivot: the ownership manifest does not exist yet.
            assert_manifest_consistent(self, root)

    def test_t5_r3o2_install_manifest_records_resolved_stack(self) -> None:
        """R3-O2 + PD-1d/D1: the install manifest records the resolved stack and
        runtime exactly as the staging manifest resolved them, and records NO
        `profile` (D1 retires the profile surface; there is no profile to
        record, so the R3-O2 'no machine-hidden effect' invariant is asserted
        over the surfaces that still exist and, for the retired one, as
        absence)."""
        staging_manifest = load_staging_manifest(staging_product())
        with tempfile.TemporaryDirectory(prefix="cdad-t5-stack-") as root_dir:
            root = Path(root_dir)
            result = run_installer(staging_product(), root, "--basic")
            self.assertEqual(
                result.returncode, 0, result.stderr or result.stdout
            )
            manifest = load_install_manifest(root)  # RED pivot: missing today
            for key in ("runtime", "stack"):
                self.assertIn(
                    key,
                    manifest,
                    f"R3-O2: the install manifest must record the resolved {key}",
                )
            self.assertEqual(
                manifest["stack"],
                staging_manifest["stack"],
                "R3-O2: the recorded stack must be the stack resolved in "
                "staging, not a machine-hidden effect",
            )
            self.assertEqual(
                manifest["runtime"], staging_manifest["runtime"],
                "R3-O2: the recorded runtime must match the staging manifest",
            )
            self.assertTrue(
                "profile" not in manifest,
                "PD-1d/D1 (ORACLE REPLACEMENT, 006-003 U2): the install "
                "manifest must no longer record a `profile`; the installer has "
                "no profiles and the staging manifest it consumes carries none, "
                "so the key can only be a leftover of the retired surface "
                "(manifest keys: %s)" % sorted(manifest),
            )


class TestT5ConflictSemantics(unittest.TestCase):
    """Real-repo installer: conflict reporting without destroying local work."""

    def test_t5_case2_modified_installed_file_reported_and_preserved(self) -> None:
        """PD-7: an installed file whose bytes differ from the registered hash
        is reported as a conflict by dry-run AND install; it is neither
        overwritten nor deleted without explicit resolution."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5-conflict-") as root_dir:
            root = Path(root_dir)
            first = run_installer(staging_product(), root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            installed = find_deployed(root, "cdad-architect.md")
            modified = installed.read_bytes() + b"\n<!-- local edit must survive -->\n"
            installed.write_bytes(modified)
            rel = str(installed.relative_to(root))

            dry = run_installer(staging_product(), root, "--dry-run", "--basic")
            dry_out = dry.stdout + dry.stderr
            self.assertRegex(
                dry_out,
                r"(?i)conflict",
                "PD-7: dry-run must report the locally modified installed "
                f"file ({rel}) as a conflict; dry-run output:\n{dry_out}",
            )
            self.assertIn(
                rel,
                dry_out,
                "PD-7: the conflict report must name the affected path",
            )

            second = run_installer(staging_product(), root, "--basic")
            second_out = second.stdout + second.stderr
            self.assertRegex(
                second_out,
                r"(?i)conflict",
                "PD-7: install must also report the modified file as a "
                f"conflict; install output:\n{second_out}",
            )
            self.assertEqual(
                installed.read_bytes(),
                modified,
                "PD-7: a conflicted file must be neither overwritten nor "
                "deleted without explicit resolution",
            )

    def test_t5_case5_symlink_at_destination_reported_not_followed(self) -> None:
        """PD-7/D4: a symlink sitting at an owned destination is reported as a
        conflict; the installer never writes through it nor silently replaces
        it."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5-symlink-") as root_dir:
            root = Path(root_dir)
            first = run_installer(staging_product(), root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            deployed = find_deployed(root, "cdad-test-writer.md")
            canary = root / "canary-target.md"
            canary.write_bytes(CANARY_BYTES)
            deployed.unlink()
            deployed.symlink_to(canary)

            dry = run_installer(staging_product(), root, "--dry-run", "--basic")
            dry_out = dry.stdout + dry.stderr
            self.assertRegex(
                dry_out,
                r"(?i)conflict",
                "D4/PD-7: a destination symlink must be reported as a "
                f"conflict, not silently followed; dry-run output:\n{dry_out}",
            )
            self.assertIn(
                "cdad-test-writer.md",
                dry_out,
                "D4/PD-7: the symlink conflict report must name the path",
            )

            second = run_installer(staging_product(), root, "--basic")
            second_out = second.stdout + second.stderr
            self.assertRegex(
                second_out,
                r"(?i)conflict",
                "D4/PD-7: install must report the destination symlink as a "
                f"conflict; install output:\n{second_out}",
            )
            self.assertEqual(
                canary.read_bytes(),
                CANARY_BYTES,
                "D4/PD-7: the installer must never write through a "
                "destination symlink",
            )
            self.assertTrue(
                deployed.is_symlink(),
                "D4/PD-7: the destination symlink must not be silently "
                "replaced without explicit resolution",
            )

    def test_t5_case6_failed_install_reports_and_retry_heals_ownership(self) -> None:
        """PD-6/D4: a partial failure is reported and leaves no half state;
        once the cause is fixed, a retry publishes ownership that matches the
        tree exactly."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5-partial-") as root_dir:
            root = Path(root_dir)
            blocked = root / ".config" / "opencode" / "agents"
            blocked.mkdir(parents=True, exist_ok=True)
            blocked.chmod(0o555)

            def _unblock() -> None:
                # Existence-conditional: the failed run may keep, empty or
                # remove the blocked directory (fixture detail, not contract).
                if blocked.exists():
                    blocked.chmod(0o755)

            self.addCleanup(_unblock)

            failed = run_installer(staging_product(), root, "--basic")
            self.assertNotEqual(
                failed.returncode,
                0,
                "D4: a partially failing install must be reported (non-zero "
                f"exit); output:\n{failed.stdout + failed.stderr}",
            )

            # Clear the failing condition defensively before the retry; the
            # half-state inspection below tolerates missing directories, and
            # the RED pivot is the missing ownership manifest, not a fixture
            # exception.
            _unblock()
            blocked.mkdir(parents=True, exist_ok=True)
            healed = run_installer(staging_product(), root, "--basic")
            self.assertEqual(
                healed.returncode, 0, healed.stderr or healed.stdout
            )
            # RED pivot: no ownership manifest exists today, so the healed
            # state cannot be verified as owned.
            assert_manifest_consistent(self, root)


class TestT5UninstallAndForeign(unittest.TestCase):
    """Real-repo installer: foreign files survive; uninstall is manifest-scoped."""

    def _install_with_foreign_files(self, root: Path) -> list[Path]:
        result = run_installer(staging_product(), root, "--basic")
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        agents_dir = find_deployed(root, "cdad-architect.md").parent
        foreign_user = agents_dir / "cdad-my-own-notes.md"
        foreign_user.write_bytes(FOREIGN_BYTES)
        foreign_plain = agents_dir / "zz-foreign-not-ours.txt"
        foreign_plain.write_bytes(FOREIGN_BYTES)
        return [foreign_user, foreign_plain]

    def test_t5_case4_foreign_files_survive_reinstall(self) -> None:
        """PD-8/D4: files that do not belong to the install (including a
        user-created cdad-*.md that never came from the repo) survive a
        reinstall untouched."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5-foreign-") as root_dir:
            root = Path(root_dir)
            self._install_with_foreign_files(root)

            again = run_installer(staging_product(), root, "--basic")
            self.assertEqual(again.returncode, 0, again.stderr or again.stdout)

            for name in ("cdad-my-own-notes.md", "zz-foreign-not-ours.txt"):
                survivors = [p for p in root.rglob(name) if p.is_file()]
                self.assertTrue(
                    survivors,
                    f"PD-8: foreign file {name} must survive a reinstall",
                )
                self.assertEqual(
                    survivors[0].read_bytes(),
                    FOREIGN_BYTES,
                    f"PD-8: foreign file {name} must survive untouched",
                )

    def test_t5_case7_uninstall_removes_only_manifest_entries(self) -> None:
        """PD-8: --uninstall deletes only manifest entries; foreign files
        (including a user-created cdad-*.md) survive; it is idempotent."""
        with tempfile.TemporaryDirectory(prefix="cdad-t5-uninstall-") as root_dir:
            root = Path(root_dir)
            self._install_with_foreign_files(root)

            manifest = load_install_manifest(root)  # RED pivot: missing today
            artifacts = manifest.get("artifacts")
            self.assertIsInstance(
                artifacts,
                dict,
                "PD-8: uninstall is scoped by the ownership manifest",
            )
            self.assertTrue(artifacts, "PD-8: manifest must list owned files")

            uninstall = run_installer(staging_product(), root, "--uninstall")
            self.assertEqual(
                uninstall.returncode,
                0,
                "PD-8: --uninstall must succeed against an owned install "
                f"root; output:\n{uninstall.stdout + uninstall.stderr}",
            )
            for rel in artifacts:
                self.assertFalse(
                    (root / rel).exists(),
                    f"PD-8: uninstall must remove manifest-owned {rel}",
                )
            for name in ("cdad-my-own-notes.md", "zz-foreign-not-ours.txt"):
                survivors = [p for p in root.rglob(name) if p.is_file()]
                self.assertTrue(
                    survivors,
                    f"PD-8: foreign file {name} must survive uninstall",
                )
                self.assertEqual(
                    survivors[0].read_bytes(),
                    FOREIGN_BYTES,
                    f"PD-8: foreign file {name} must survive uninstall "
                    "untouched",
                )

            again = run_installer(staging_product(), root, "--uninstall")
            self.assertEqual(
                again.returncode,
                0,
                "PD-8: uninstall must be idempotent; output:\n"
                f"{again.stdout + again.stderr}",
            )


class TestT5StagingIsSourceOfTruth(SandboxFixture):
    """Sandbox installer: staging is the only input; sources/ is never read."""

    def test_t5_case8_install_deploys_staging_bytes_without_sources(self) -> None:
        """PD-18 (b)+(c): the install completes with staging present and
        sources/ inaccessible, and deploys the STAGED bytes (a change outside
        staging cannot alter the deployed content)."""
        staging_manifest = load_staging_manifest(self.sandbox)
        entry = pick_staged_entry(staging_manifest)
        artifact = self.sandbox / "build" / "staging" / entry["file"]
        mutated = (
            artifact.read_bytes()
            + b"\n<!-- T5 staging sentinel: deployed bytes must come from staging -->\n"
        )
        artifact.write_bytes(mutated)
        entry["sha256"] = sha256_bytes(mutated)
        write_staging_manifest(self.sandbox, staging_manifest)

        sources = self.sandbox / "sources"
        away = Path(self._tmp.name) / "sources-inaccessible"

        def _restore_sources() -> None:
            if not sources.exists() and away.exists():
                away.rename(sources)

        sources.rename(away)
        self.addCleanup(_restore_sources)

        with tempfile.TemporaryDirectory(prefix="cdad-t5-nosrc-") as root_dir:
            root = Path(root_dir)
            result = run_installer(self.sandbox, root, "--basic")
            self.assertEqual(
                result.returncode,
                0,
                "PD-18: the install must complete with staging present and "
                f"sources/ inaccessible; installer failed:\n"
                f"{result.stderr or result.stdout}",
            )
            deployed = find_deployed(root, Path(entry["file"]).name)
            self.assertEqual(
                deployed.read_bytes(),
                mutated,
                "PD-18: the installer must deploy the STAGED bytes; the "
                "deployed content does not come from build/staging (it read "
                "sources/ or the repo copies instead)",
            )

    def test_t5_case9_dry_run_announces_exactly_the_staged_set(self) -> None:
        """Plan T5 (dry-run exacto): the dry-run plan announces every staged
        artifact (including a staging-only fixture), the real install deploys
        it with the staged bytes, and the dry-run itself changes nothing."""
        extra_rel = "agents/opencode/cdad-zz-t5-extra.md"
        extra_name = Path(extra_rel).name
        extra_bytes = b"# T5 dry-run exactness fixture artifact\n"
        staging_manifest = load_staging_manifest(self.sandbox)
        extra_path = self.sandbox / "build" / "staging" / extra_rel
        extra_path.parent.mkdir(parents=True, exist_ok=True)
        extra_path.write_bytes(extra_bytes)
        staging_manifest["artifacts"].append(
            {
                "file": extra_rel,
                "regenerate": "T5 dry-run exactness fixture",
                "sha256": sha256_bytes(extra_bytes),
                "sources": [],
            }
        )
        write_staging_manifest(self.sandbox, staging_manifest)

        with tempfile.TemporaryDirectory(prefix="cdad-t5-dry-") as dry_dir, \
                tempfile.TemporaryDirectory(prefix="cdad-t5-real-") as real_dir:
            dry_root, real_root = Path(dry_dir), Path(real_dir)

            dry = run_installer(self.sandbox, dry_root, "--dry-run", "--basic")
            self.assertEqual(dry.returncode, 0, dry.stderr or dry.stdout)
            dry_out = dry.stdout + dry.stderr
            self.assertIn(
                extra_name,
                dry_out,
                "dry-run exacto: the plan must announce every staged "
                f"artifact, including the staging-only fixture {extra_rel}; "
                f"dry-run output:\n{dry_out}",
            )
            self.assertEqual(
                list(dry_root.rglob("*")),
                [],
                "dry-run exacto: a dry-run must not create, modify or delete "
                "anything under its install root",
            )

            real = run_installer(self.sandbox, real_root, "--basic")
            self.assertEqual(real.returncode, 0, real.stderr or real.stdout)
            deployed = find_deployed(real_root, extra_name)
            self.assertEqual(
                deployed.read_bytes(),
                extra_bytes,
                "dry-run exacto: the real install must deploy the staged "
                "fixture bytes exactly as announced",
            )

    def test_t5_case3_check_reports_staging_obsolete_artifact(self) -> None:
        """PD-5: --check detects an installed artifact that is no longer
        present in staging (renamed/obsolete upstream)."""
        staging_manifest = load_staging_manifest(self.sandbox)
        entry = pick_staged_entry(staging_manifest)
        obsolete_rel = entry["file"]
        obsolete_name = Path(obsolete_rel).name

        with tempfile.TemporaryDirectory(prefix="cdad-t5-obsolete-") as root_dir:
            root = Path(root_dir)
            first = run_installer(self.sandbox, root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            # Upstream renames/removes the artifact: it disappears from staging.
            (self.sandbox / "build" / "staging" / obsolete_rel).unlink()
            staging_manifest["artifacts"] = [
                a for a in staging_manifest["artifacts"]
                if a["file"] != obsolete_rel
            ]
            write_staging_manifest(self.sandbox, staging_manifest)

            check = run_installer(self.sandbox, root, "--check")
            check_out = check.stdout + check.stderr
            self.assertNotEqual(
                check.returncode,
                0,
                f"PD-5: --check must flag the installed artifact {obsolete_rel} "
                "that is no longer present in staging; it passed silently:\n"
                f"{check_out}",
            )
            self.assertIn(
                obsolete_name,
                check_out,
                "PD-5: the --check report must name the obsolete installed "
                "artifact by path",
            )

    def test_t5_case10_check_reports_installed_drift_vs_staging(self) -> None:
        """PD-5: --check detects an installed copy that differs from staging
        (drift after a staging regeneration)."""
        staging_manifest = load_staging_manifest(self.sandbox)
        entry = pick_staged_entry(staging_manifest)

        with tempfile.TemporaryDirectory(prefix="cdad-t5-drift-") as root_dir:
            root = Path(root_dir)
            first = run_installer(self.sandbox, root, "--basic")
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)

            # Staging moves on: the staged artifact is regenerated upstream.
            staged = self.sandbox / "build" / "staging" / entry["file"]
            mutated = staged.read_bytes() + b"\n<!-- regenerated upstream -->\n"
            staged.write_bytes(mutated)
            entry["sha256"] = sha256_bytes(mutated)
            write_staging_manifest(self.sandbox, staging_manifest)

            check = run_installer(self.sandbox, root, "--check")
            check_out = check.stdout + check.stderr
            self.assertNotEqual(
                check.returncode,
                0,
                f"PD-5: --check must report the drift between the installed "
                f"copy and staging for {entry['file']}; it passed silently:\n"
                f"{check_out}",
            )
            self.assertIn(
                Path(entry["file"]).name,
                check_out,
                "PD-5: the drift report must name the affected path",
            )


if __name__ == "__main__":
    unittest.main()
