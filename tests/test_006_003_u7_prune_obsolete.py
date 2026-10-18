#!/usr/bin/env python3
"""RED tests for 006-003 U7: the installer retires its own obsolete files.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18, sha256 c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890)
— PD-6a..PD-6e (retiro de obsoletos propios, decision D6), INV-2 (the installer
never deletes a locally modified file nor one it does not own) and the
orchestrator amendment A-3 (the two user configuration files are NOT in the
ownership manifest and are never removed, not even by `--uninstall`).

Unit: U7 of the approved plan (ficha U7), which depends on U2. The installer's
*manifest python* (PD-6e) is exercised behaviourally only: no implementation
file is read and the installer is never inspected, only run.

Oracle discipline (black-box): the installer runs as a subprocess against a
PRODUCT COPY whose staging is generated in the copy; `CDAD_INSTALL_ROOT` and
`HOME` always point inside a per-test temporary directory (never the repository,
never the real HOME). What is observed is the published surface: exit codes,
stdout/stderr, the deployed tree and the ownership manifest the installer itself
publishes (`<install root>/.cdad-install-manifest.json`, announced by `--help`).

Scenario (two real installs, no hand-edited manifest except in the PD-6e test,
where the hand-edit is declared in that test's docstring):

1. install #1 with the complete product — the retired source is deployed into
   the runtime trees and registered in the ownership manifest;
2. the product source that produced it is removed from the copy, simulating
   «este archivo propio dejó de desplegarse» (a retired/renamed own file) — the
   staging is NOT regenerated, because the installer mirrors `skills/` from the
   product copy and the retired source belongs to that mirror;
3. install #2 (`--dry-run` in PD-6d / `--uninstall` in A-3) is what U7 has to fix.

The deployed paths of the retired source are read FROM the manifest install #1
publishes (never hardcoded), so the oracle follows whatever layout the runtime
trees have.

Mapping (one test per numbered postcondition / amendment):

- test_pd_6a_* -> PD-6a (registered own file, not redeployed and byte-identical
                        to the registered sha256 -> removed from disk AND from the
                        manifest; `--check` reports no PENDING-REMOVAL and PASSes)
- test_pd_6b_* -> PD-6b (the same case, locally modified -> preserved, disclosed
                        as CONFLICT and still registered; the untouched sibling
                        deployments of the same source ARE retired, so the
                        preservation is attributable to the local change)
- test_pd_6c_* -> PD-6c / INV-2 (a file inside the installed tree that the
                        manifest does not register is never touched)
- test_pd_6d_* -> PD-6d (`--dry-run` lists the bajas and deletes nothing)
- test_pd_6e_* -> PD-6e (the manifest python resolves the recorded paths against
                        the redirected INSTALL_ROOT, absolute and relative: this
                        test registers absolute paths in the manifest — the only
                        hand-edit of the whole module, declared below; the
                        relative half is exercised by PD-6a in the same
                        redirected root)
- test_a_3_*    -> A-3 (delegation.json + opencode-server.env.example are user
                        data: never in the manifest, surviving reinstall (with
                        the prune active) and `--uninstall` byte for byte)

Expected RED against the current tree (declared, not accidental): the retired
file stays on disk, stays in `artifacts`/`pending_removal`, `--check` FAILs with
three `PENDING-REMOVAL` lines, the re-run publishes `0 conflict(s)` for the
locally modified copy, `--dry-run` never names the baja, and the absolute paths
registered by the PD-6e test are carried forward instead of pruned.

Expected GREEN controls today (declared, so a later failure is readable): PD-6c
(files the manifest does not register already survive re-install — the check
guards the harness, not the feature) and A-3 (the two config files already
survive re-install and `--uninstall`, because U4 creates them as user data).
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Public product entries the installer needs next to install.sh (same set the
# U2 oracle and the 004-001 acceptance matrix declare).
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"
STAGING_REL = Path("build") / "staging"

# The ownership manifest the installer publishes (announced by `--help`).
MANIFEST_NAME = ".cdad-install-manifest.json"

# PD-6a: the own source whose deployment is retired in the second install. Any
# product source works; this one is mirrored into every runtime tree and its
# basename is unique inside the installed tree, so the oracle cannot match a
# foreign file by accident.
RETIRED_SOURCE = "skills/cdad-cycle/assets/adr-template/ADR.md"
RETIRED_TAIL = "cdad-cycle/assets/adr-template/ADR.md"

# A-3: the two user configuration files (created by U4, never owned).
CONFIG_REL_PATHS = (
    Path(".config") / "cdad" / "delegation.json",
    Path(".config") / "cdad" / "opencode-server.env.example",
)

# PD-6a: `--check` must not report the retired file.
PENDING_RE = re.compile(r"(?i)pending-removal")
# PD-6a: the published PASS report.
PASS_RE = re.compile(r"(?i)\bpass\b")
# PD-6b: the conflict disclosure.
CONFLICT_RE = re.compile(r"(?i)conflict")


# --------------------------------------------------------------------- helpers


def tail(text: str, lines: int = 25) -> str:
    return "\n".join(text.strip().splitlines()[-lines:])


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def snapshot_tree(root: Path) -> dict[str, tuple]:
    """Content-level snapshot of a tree (dirs, sizes, sha256 of every file)."""
    snapshot: dict[str, tuple] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        base = Path(dirpath)
        for name in dirnames:
            snapshot[str((base / name).relative_to(root)) + "/"] = ("dir",)
        for name in filenames:
            path = base / name
            try:
                data = path.read_bytes()
            except OSError as exc:  # a file the test cannot read is not a change
                snapshot[str(path.relative_to(root))] = ("unreadable", str(exc))
                continue
            snapshot[str(path.relative_to(root))] = (
                "file",
                len(data),
                hashlib.sha256(data).hexdigest(),
            )
    return snapshot


def snapshot_diff(before: dict[str, tuple], after: dict[str, tuple]) -> list[str]:
    """Human-sized description of a changed tree (keys only, never contents)."""
    diff: list[str] = []
    for key in sorted(set(after) - set(before)):
        diff.append("created: %s" % key)
    for key in sorted(set(before) - set(after)):
        diff.append("removed: %s" % key)
    for key in sorted(set(before) & set(after)):
        if before[key] != after[key]:
            diff.append("modified: %s" % key)
    return diff


def load_manifest(root: Path) -> dict:
    path = root / MANIFEST_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_keys_referencing(manifest: dict, needle: str) -> list[str]:
    """Every `artifacts`/`pending_removal` key of the manifest citing `needle`.

    This is how the oracle asks «sigue registrado» / «deja de figurar en el
    manifiesto» without knowing which of the two maps the implementation uses.
    """
    keys: list[str] = []
    for section in ("artifacts", "pending_removal"):
        for key in manifest.get(section) or {}:
            if needle in key:
                keys.append(key)
    return sorted(set(keys))


def deployed_paths_for_source(manifest: dict, source_rel: str) -> list[str]:
    """Install-root-relative paths install #1 deployed from `source_rel`."""
    return sorted(
        key
        for key, meta in (manifest.get("artifacts") or {}).items()
        if isinstance(meta, dict) and meta.get("source") == source_rel
    )


# --------------------------------------------------------------------- fixture


class PruneFixture(unittest.TestCase):
    """Product copy with staging generated in the copy + redirected install roots.

    Nothing is installed into HOME or into the repository: every install root is
    a per-test temporary directory passed as `CDAD_INSTALL_ROOT`, and the fake
    HOME used by the subprocess lives in the same temporary directory.
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="cdad-u7-prune-")
        cls.base = Path(cls._tmp.name).resolve()
        cls.product = cls.base / "product"
        cls.product.mkdir()
        for entry in PRODUCT_ENTRIES:
            source = REPO_ROOT / entry
            target = cls.product / entry
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

        cls.generate_results: dict[str, subprocess.CompletedProcess[str]] = {}
        for runtime in RUNTIMES:
            cls.generate_results[runtime] = subprocess.run(
                [
                    sys.executable,
                    str(cls.product / "scripts" / "cdad-generate.py"),
                    "--runtime",
                    runtime,
                    "--stack",
                    STACK,
                    "--out",
                    str(cls.product / STAGING_REL),
                ],
                cwd=str(cls.product),
                text=True,
                capture_output=True,
                check=False,
            )

        cls.fake_home = cls.base / "home"
        cls.fake_home.mkdir()
        # Pristine copy of the source the tests retire, restored after every use.
        cls.retired_source_backup = cls.base / "retired-source.backup"
        shutil.copy2(cls.product / RETIRED_SOURCE, cls.retired_source_backup)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    # -- helpers ----------------------------------------------------------

    def assert_staging_ready(self) -> None:
        for runtime, result in self.generate_results.items():
            self.assertEqual(
                result.returncode,
                0,
                "precondición del fixture: el generador falló para runtime=%s "
                "(PD-1f, unidad U1):\n%s" % (runtime, tail(result.stderr or result.stdout)),
            )

    def new_root(self, name: str) -> Path:
        root = self.base / name
        root.mkdir()
        return root

    def installer_env(self, root: Path) -> dict:
        env = os.environ.copy()
        for key in list(env):
            if key.startswith("CDAD_PREMIUM_MODEL_"):
                env.pop(key)
        env["CDAD_INSTALL_ROOT"] = str(root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        # INV-6: the fake HOME of the test, never the real one; the config dir
        # stays undefined so the config files land under the redirected root.
        env["HOME"] = str(self.fake_home)
        env.pop("XDG_CONFIG_HOME", None)
        env.pop("CDAD_MODEL_PROFILE", None)
        return env

    def run_installer(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.product / "install.sh"), *args],
            cwd=str(self.product),
            env=self.installer_env(root),
            text=True,
            capture_output=True,
            check=False,
        )

    def install(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        """Install #1: the complete product, both config files included (U4)."""
        result = self.run_installer(root, "--force", *args)
        self.assertEqual(
            result.returncode,
            0,
            "precondición del fixture: la instalación completa sobre %s falló "
            "(rc=%s):\n%s"
            % (root.name, result.returncode, tail(result.stdout + result.stderr)),
        )
        self.assertTrue(
            (root / MANIFEST_NAME).is_file(),
            "precondición del fixture: `install.sh` no publicó %s en %s — el "
            "oráculo del manifiesto sería vacuo" % (MANIFEST_NAME, root.name),
        )
        return result

    def retired_paths(self, root: Path) -> list[str]:
        """Paths install #1 deployed for the source U7 is asked to retire."""
        paths = deployed_paths_for_source(load_manifest(root), RETIRED_SOURCE)
        self.assertTrue(
            paths,
            "precondición del fixture: el manifiesto de %s no registra ningún "
            "artefacto desplegado desde %s — no habría obsoleto propio que "
            "retirar" % (root.name, RETIRED_SOURCE),
        )
        for rel in paths:
            self.assertTrue(
                (root / rel).is_file(),
                "precondición del fixture: %s quedó registrado en el manifiesto "
                "de %s pero no está en disco" % (rel, root.name),
            )
        return paths

    @contextlib.contextmanager
    def retired_source(self):
        """«Este archivo propio dejó de desplegarse»: retira la fuente del producto.

        The declaration is the installer's own manifest law: a registered
        artifact whose source the install no longer deploys becomes a
        `pending_removal` entry (observed today in a real second install). The
        product copy is restored afterwards, so no test depends on the order.
        """
        source = self.product / RETIRED_SOURCE
        shutil.copy2(self.retired_source_backup, source)  # known pre-state
        source.unlink()
        try:
            yield source
        finally:
            shutil.copy2(self.retired_source_backup, source)

    def config_bytes(self, root: Path) -> dict[str, str | None]:
        return {str(rel): sha256_file(root / rel) for rel in CONFIG_REL_PATHS}

    # -- PD-6a -----------------------------------------------------------

    def test_pd_6a_intact_retired_own_file_is_removed_from_disk_and_manifest(self) -> None:
        """PD-6a/D6/INV-2: a registered own file, byte-identical to the sha256 the
        manifest records and no longer redeployed, is removed from disk and stops
        figuring in the manifest; `install.sh --check` does not report it as
        PENDING-REMOVAL and the root PASSes."""
        self.assert_staging_ready()
        root = self.new_root("pd6a")
        self.install(root, "--basic")
        paths = self.retired_paths(root)

        with self.retired_source():
            self.run_installer(root, "--basic", "--force")

            surviving = [rel for rel in paths if (root / rel).is_file()]
            self.assertEqual(
                surviving,
                [],
                "PD-6a: el archivo propio %s ya no se despliega y sus bytes son "
                "idénticos al sha256 registrado, así que el instalador debe "
                "retirarlo; sigue en disco: %s"
                % (RETIRED_SOURCE, surviving),
            )

            manifest = load_manifest(root)
            still_registered = manifest_keys_referencing(manifest, RETIRED_TAIL)
            self.assertEqual(
                still_registered,
                [],
                "PD-6a: el archivo retirado no debe figurar en el manifiesto "
                "(artifacts/pending_removal); sigue registrado en: %s"
                % still_registered,
            )

            check = self.run_installer(root, "--check")
            output = check.stdout + check.stderr
            pending_lines = [
                line for line in output.splitlines() if PENDING_RE.search(line)
            ]
            self.assertEqual(
                pending_lines,
                [],
                "PD-6a: `install.sh --check` sigue reportando el archivo propio "
                "retirado como PENDING-REMOVAL:\n%s" % "\n".join(pending_lines[:5]),
            )
            self.assertEqual(
                check.returncode,
                0,
                "PD-6a: tras retirar el obsoleto propio, `install.sh --check` debe "
                "PASS sobre la raíz redirigida (rc=%s):\n%s"
                % (check.returncode, tail(output)),
            )
            self.assertRegex(
                output,
                PASS_RE,
                "PD-6a: `--check` salió 0 pero no publicó el informe PASS:\n%s"
                % tail(output),
            )

    # -- PD-6b -----------------------------------------------------------

    def test_pd_6b_locally_modified_retired_own_file_is_preserved_and_conflicted(self) -> None:
        """PD-6b/INV-2: the same retired own file, modified locally, is preserved,
        disclosed as CONFLICT and stays registered. Control of non-vacuity: the
        untouched deployments of the same source ARE retired, so the preservation
        is attributable to the local modification and not to a missing prune.

        Non-vacuity of the control: it needs at least two deployments of the
        retired source, asserted as a precondition."""
        self.assert_staging_ready()
        root = self.new_root("pd6b")
        self.install(root, "--basic")
        paths = self.retired_paths(root)
        self.assertGreaterEqual(
            len(paths),
            2,
            "precondición del fixture: PD-6b compara el hermano intacto contra el "
            "modificado, y este despliegue sólo tiene: %s" % paths,
        )

        modified_candidates = [rel for rel in paths if rel.startswith(".agents/")]
        modified_rel = (modified_candidates or paths)[0]
        modified_path = root / modified_rel
        modified_path.write_bytes(
            modified_path.read_bytes() + b"\n# local modification (PD-6b)\n"
        )
        modified_sha = sha256_file(modified_path)
        siblings = [rel for rel in paths if rel != modified_rel]

        with self.retired_source():
            result = self.run_installer(root, "--basic", "--force")
            output = result.stdout + result.stderr

            self.assertTrue(
                modified_path.is_file(),
                "PD-6b: el obsoleto propio modificado localmente (%s) fue borrado; "
                "la modificación del usuario debe preservarse" % modified_rel,
            )
            self.assertEqual(
                sha256_file(modified_path),
                modified_sha,
                "PD-6b: el obsoleto propio modificado localmente fue reescrito "
                "(%s) pese a no redesplegarse" % modified_rel,
            )

            manifest = load_manifest(root)
            output_conflicts = [
                line
                for line in output.splitlines()
                if CONFLICT_RE.search(line) and RETIRED_TAIL in line
            ]
            manifest_conflicts = json.dumps(manifest.get("conflicts") or [])
            self.assertTrue(
                output_conflicts or (RETIRED_TAIL in manifest_conflicts),
                "PD-6b: el obsoleto propio modificado localmente no se reportó como "
                "CONFLICT (ni en la salida ni en el manifiesto, junto a %s); la "
                "salida publicó: %s"
                % (RETIRED_TAIL, tail(output)),
            )
            self.assertNotEqual(
                manifest_keys_referencing(manifest, RETIRED_TAIL),
                [],
                "PD-6b: el obsoleto propio preservado debe seguir registrado en el "
                "manifiesto (artifacts o pending_removal)",
            )

            surviving_siblings = [rel for rel in siblings if (root / rel).is_file()]
            self.assertEqual(
                surviving_siblings,
                [],
                "PD-6b (control de no vacuidad): las copias intactas del mismo "
                "origen deben retirarse — la preservación de %s sólo se explica "
                "por su modificación local; siguen en disco: %s"
                % (modified_rel, surviving_siblings),
            )

    # -- PD-6c -------------------------------------------------------

    def test_pd_6c_unregistered_file_inside_the_installed_tree_is_never_touched(self) -> None:
        """PD-6c/INV-2: a file that lives inside the installed tree but that the
        manifest does not register is never touched, not even while the prune is
        active in the same run."""
        self.assert_staging_ready()
        root = self.new_root("pd6c")
        self.install(root, "--basic")
        self.retired_paths(root)

        foreign_rel = ".agents/skills/cdad-cycle/notes-local-ajenas.md"
        foreign_path = root / foreign_rel
        foreign_path.parent.mkdir(parents=True, exist_ok=True)
        foreign_bytes = b"# file foreign to the manifest (PD-6c)\n"
        foreign_path.write_bytes(foreign_bytes)
        foreign_sha = sha256_file(foreign_path)

        with self.retired_source():
            self.run_installer(root, "--basic", "--force")

            self.assertTrue(
                foreign_path.is_file(),
                "PD-6c/INV-2: el instalador borró %s, un archivo que el "
                "manifiesto no registra" % foreign_rel,
            )
            self.assertEqual(
                sha256_file(foreign_path),
                foreign_sha,
                "PD-6c/INV-2: el instalador modificó %s, un archivo que el "
                "manifiesto no registra" % foreign_rel,
            )

        self.assertEqual(
            manifest_keys_referencing(load_manifest(root), "notes-local-ajenas.md"),
            [],
            "PD-6c: el archivo ajeno no debe quedar registrado en el manifiesto",
        )

    # -- PD-6d -------------------------------------------------------

    def test_pd_6d_dry_run_lists_the_bajas_without_deleting_anything(self) -> None:
        """PD-6d: `--dry-run` lists the bajas of the prune (each retired own path
        is named) and changes nothing: the tree and the manifest stay byte for
        byte identical."""
        self.assert_staging_ready()
        root = self.new_root("pd6d")
        self.install(root, "--basic")
        paths = self.retired_paths(root)

        with self.retired_source():
            before_tree = snapshot_tree(root)
            before_manifest = sha256_file(root / MANIFEST_NAME)

            dry_run = self.run_installer(root, "--dry-run")
            output = dry_run.stdout + dry_run.stderr

            self.assertTrue(
                RETIRED_TAIL in output,
                "PD-6d: `--dry-run` no lista la baja del obsoleto propio %s "
                "(rc=%s); sin la lista, la corrida real no puede declararse "
                "previsualizada:\n%s"
                % (RETIRED_TAIL, dry_run.returncode, tail(output, 30)),
            )

            surviving = [rel for rel in paths if (root / rel).is_file()]
            self.assertEqual(
                surviving,
                paths,
                "PD-6d: `--dry-run` borró bajas (%s)"
                % [rel for rel in paths if rel not in surviving],
            )
            self.assertEqual(
                snapshot_diff(before_tree, snapshot_tree(root)),
                [],
                "PD-6d: `--dry-run` modificó el árbol instalado:\n%s"
                % "\n".join(snapshot_diff(before_tree, snapshot_tree(root))[:10]),
            )
            self.assertEqual(
                sha256_file(root / MANIFEST_NAME),
                before_manifest,
                "PD-6d: `--dry-run` reescribió el manifiesto de ownership",
            )

    # -- PD-6e -------------------------------------------------------

    def test_pd_6e_manifest_paths_are_resolved_against_the_redirected_root(self) -> None:
        """PD-6e: the manifest python resolves the recorded paths against
        INSTALL_ROOT, absolute and relative.

        Hand-edit (declared, the only one of this module): install #1's manifest
        is rewritten so that the retired own file is recorded under ABSOLUTE
        paths instead of install-root-relative ones — the same simulation,
        expressed the way a previous install that recorded absolute paths would.
        The relative half is exercised by PD-6a in an equally redirected root: if
        the manifest python did not receive INSTALL_ROOT, neither would resolve.
        """
        self.assert_staging_ready()
        root = self.new_root("pd6e")
        self.install(root, "--basic")
        paths = self.retired_paths(root)
        manifest_path = root / MANIFEST_NAME
        manifest = load_manifest(root)

        for rel in paths:
            meta = manifest["artifacts"].pop(rel)
            absolute = str(root / rel)
            manifest["artifacts"][absolute] = meta
            manifest["pending_removal"][absolute] = meta
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        with self.retired_source():
            self.run_installer(root, "--basic", "--force")

            surviving = [rel for rel in paths if (root / rel).is_file()]
            self.assertEqual(
                surviving,
                [],
                "PD-6e: las rutas ABSOLUTAS registradas en el manifiesto deben "
                "resolverse contra la raíz redirigida (%s) y su obsoleto propio "
                "retirarse; sigue en disco: %s" % (root, surviving),
            )

            after = load_manifest(root)
            leftovers = sorted(
                set(
                    manifest_keys_referencing(after, RETIRED_TAIL)
                    + [key for key in (after.get("artifacts") or {}) if str(root) in key]
                    + [key for key in (after.get("pending_removal") or {}) if str(root) in key]
                )
            )
            self.assertEqual(
                leftovers,
                [],
                "PD-6e: el manifiesto sigue registrando el obsoleto retirado "
                "(clave absoluta o relativa): %s" % leftovers,
            )

    # -- A-3 ---------------------------------------------------------

    def test_a_3_config_files_are_never_owned_removed_nor_registered(self) -> None:
        """A-3: `delegation.json` and `opencode-server.env.example` are user data:
        never registered in the ownership manifest, and surviving both the
        re-install that runs the prune and `--uninstall`, byte for byte."""
        self.assert_staging_ready()
        root = self.new_root("a3")
        self.install(root, "--basic")
        self.retired_paths(root)

        before = self.config_bytes(root)
        for rel, digest in before.items():
            self.assertIsNotNone(
                digest,
                "A-3 precondición: el instalador no creó %s en la raíz redirigida "
                "(unidad U4)" % rel,
            )
            self.assertEqual(
                manifest_keys_referencing(load_manifest(root), rel),
                [],
                "A-3: %s es dato del usuario y no puede figurar en el manifiesto "
                "de ownership" % rel,
            )

        with self.retired_source():
            self.run_installer(root, "--basic", "--force")

        after_reinstall = self.config_bytes(root)
        self.assertEqual(
            after_reinstall,
            before,
            "A-3: la reinstalación (con el retiro de obsoletos activo) modificó o "
            "borró los archivos de config del usuario",
        )
        self.assertEqual(
            manifest_keys_referencing(load_manifest(root), str(CONFIG_REL_PATHS[0]))
            + manifest_keys_referencing(load_manifest(root), str(CONFIG_REL_PATHS[1])),
            [],
            "A-3: la reinstalación registró los archivos de config del usuario en "
            "el manifiesto (quedarían al alcance del retiro y de --uninstall)",
        )

        uninstall = self.run_installer(root, "--uninstall", "--force")
        after_uninstall = self.config_bytes(root)
        self.assertEqual(
            after_uninstall,
            before,
            "A-3: `--uninstall` (rc=%s) modificó o borró los archivos de config del "
            "usuario:\n%s"
            % (uninstall.returncode, tail(uninstall.stdout + uninstall.stderr)),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
