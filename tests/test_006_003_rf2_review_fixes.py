#!/usr/bin/env python3
"""RED tests for the SECOND 006-003 review-fix round — B-1 and OPT-1 of
`docs/specs/006-003-installer-single-profile-delegation-config/rereview.md`
(focal re-review of 2026-10-18).

Contract: `docs/specs/006-003-installer-single-profile-delegation-config/spec.md`
(approved 2026-10-18, sha256
`c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890`), §2.3 (the
401/403 diagnosis is self-sufficient: it names the RESOLVED path of the
credential, never the value) and INV-2 («el instalador nunca borra un archivo
modificado localmente ni uno no registrado; solo retira lo propio con sha256 sin
cambios»), plus the orchestrator disposition that resolves B-1 and OPT-1 in this
round.

Mapping (one test per closing condition / finding; the finding IS the
postcondition):

- test_b1_a_*    -> B-1 · INV-2 + O-5 closing condition 1/4: a record whose
                    recorded digest is EMPTY and whose `source` is empty or
                    absent is NEVER removable. The file is preserved, disclosed
                    as CONFLICT and kept registered. Covers the two
                    representations the re-review probed as RETIRING today
                    (`sha` empty + `source` empty; `sha` empty + `source` key
                    absent). In the same run an intact sibling (correct digest)
                    IS retired: that in-run control makes the preservation
                    attributable to the degenerate record, not to a dead prune.
- test_b1_a2_*   -> B-1 · closing condition 1 on the OTHER surface: `--uninstall`
                    (the same decision function) does not remove the file of an
                    empty-digest record without explicit resolution.
- test_b1_b_*    -> B-1 · closing condition 2: digest empty + `source` present →
                    preserved AND the record the installer publishes stays
                    coherent — the source text sits in the `source` slot, never
                    in the `sha256` slot, and no message says
                    «registered <source>».
- test_b1_c_*    -> B-1 · closing condition 2 for the `null` digest: preserved
                    with a coherent record (the digest slot is not the literal
                    string `None`), not with the corrupt persistent record
                    (`{"sha256": "None", ...}`) the re-review reports.
- test_b1_control_* -> B-1 · the positive control, DECLARED PASSING today: a
                    correct digest on a file the install no longer deploys is
                    still retired (the healthy prune is not disabled by the
                    fix).
- test_opt1_*     -> OPT-1 · §2.3 (`spec.md:48`): with an environment value
                    that the server rejects (401 of the fixture), the diagnosis
                    names ALSO the default credential-file path as the
                    alternative, still never the value.

Mechanism the assertions are derived from (from the re-review, not from the
implementation): the published manifest records the shape
`{"sha256": <digest>, "source": <product-relative path>}` under `artifacts`,
and the prune publishes the records it keeps under `pending_removal`. A record
whose digest is empty collapses its columns when carried through a 4-column TSV
read with `IFS=$'\\t' read` (consecutive tabs are one delimiter in bash), so the
empty digest is either read as «no digest recorded» (→ removable) or as its
neighbouring column. The oracles below ask only what the spec asks: the file
survives and the published record keeps each value in its own slot.

Oracle discipline (black-box). NOTHING of the implementation is read:

- The installer runs as a subprocess against a PRODUCT COPY whose staging is
  regenerated in the copy (`tests/test_006_003_u4_delegation_config.py::
  InstallerHarness`, reused by import — the same declared fixture the U4/U7 and
  the first review-fix round use); `CDAD_INSTALL_ROOT` plus a tempdir `HOME`
  confine every write (INV-6). The host's `HOME`/`~/.config/cdad` is never read
  nor written.
- What is observed is the published surface only: exit codes, stdout/stderr,
  the deployed tree and the ownership manifest the installer itself publishes
  (`<install root>/.cdad-install-manifest.json`, announced by `--help`).
- The server credential is exercised against the LOCAL loopback HTTP fixture
  (`tests/test_006_001_t1_selection.py::FakeInfoServer`) that requires Basic
  auth; the host's `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` are stripped
  from every child environment by the inherited `dispatch()`.
- The retired own source (`skills/cdad-cycle/assets/adr-template/ADR.md`) is
  the U7 focal's declared subject: removing it from the product copy is how
  «este archivo propio dejó de desplegarse» is simulated. Only test-local
  sentinels are written (INV-1).

Declared hand-edit (minimal, and the only one): the manifest install #1
publishes is rewritten so the retired own file carries a DEGENERATE record —
`sha256` empty / `null`, `source` empty / absent / a test-local sentinel. This
is exactly the state the disposition declares reachable (a hand-edited
manifest); no product source and no installer text is touched. Every mutation
happens in a per-test temporary directory.

Expected RED against the current tree (declared, not accidental — each failure
is an AssertionError about missing behavior, never an import/syntax/fixture
error):

- test_b1_a: with `sha256: ""` and no `source` the file is REMOVED (the
  re-reviewed defect); the survival oracle fires.
- test_b1_a2: `--uninstall` removes it as well (rc=0, «372 of 372 removed»).
- test_b1_b: the file already survives, but by column collapse: the published
  record is `{"sha256": "<source text>", "source": ""}` and the message says
  «registered <source text>» → both coherence oracles fire.
- test_b1_c: the file survives with `{"sha256": "None", ...}` and the message
  says «registered None» → both coherence oracles fire.
- test_opt1: the environment branch of the 401 diagnosis names no candidate
  file path at all («no credential file was consulted») → the path oracle
  fires.
- test_b1_control: DECLARED PASSING today (the healthy prune works); it is the
  non-regression control that fails only if a fix disables the prune.

Fixtures use the declared bounds unchanged (the 300 s subprocess cap of the
installer harness and the shared `FAST_WAIT` of the 006-001 server focals): no
oracle is loosened, no timeout is retuned here.
"""

from __future__ import annotations

import contextlib
import json
import re
import shutil
import unittest
from pathlib import Path

# Reuse declared by import (single definition; none of the imported names is a
# TestCase, so importing imports no foreign tests).
from test_006_001_t1_selection import OPENCODE_PASSWORD_ENV
from test_006_003_u4_delegation_config import InstallerHarness
from test_006_003_u6_server_credential import ServerCredentialCase
from test_006_003_u7_prune_obsolete import (
    MANIFEST_NAME,
    RETIRED_SOURCE,
    RETIRED_TAIL,
    deployed_paths_for_source,
    load_manifest,
    sha256_file,
    tail,
)

# ------------------------------------------------------------------ oracles
# The disclosure vocabulary the manifest/prune surfaces already use (PD-6b and
# the first review-fix round): a preserved record is CONFLICT on re-install and
# PRESERVED for explicit resolution on `--uninstall`.
CONFLICT_RE = r"(?i)conflict"
PRESERVED_RE = r"(?i)preserv|explicit resolution"
# The digest slot must never receive a non-digest token: the re-review reports
# `"None"` (the Python repr of a null digest) leaking into the published record
# and into the message.
NULL_TOKENS = ("none", "null")

# Test-local sentinel used as the `source` column of the hand-edited records
# (never a host value, INV-1).
SOURCE_SENTINEL = "rf2-hand-edit-source-sentinel"

# OPT-1 sentinels: the fixture requires one value, the environment carries
# another (test-local, INV-1).
OPT1_REQUIRED_PASSWORD = "cdad-006-003-rf2-opt1-required-sentinel"
OPT1_WRONG_ENV_PASSWORD = "cdad-006-003-rf2-opt1-wrong-env-sentinel"


# ------------------------------------------------------------------- fixture


class Rf2ManifestFixture(InstallerHarness):
    """`InstallerHarness` (product copy + staging in the copy + redirected,
    tempdir-only install roots) plus the two pieces this round needs: the U7
    simulation of «este archivo propio dejó de desplegarse» and the declared
    hand-edit of the manifest install #1 publishes."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.retired_source_backup = cls.base / "retired-source.backup"
        shutil.copy2(cls.product / RETIRED_SOURCE, cls.retired_source_backup)

    # -- install ---------------------------------------------------------

    def install(self, root: Path) -> str:
        """Install #1 over the complete product; returns the published output."""
        output = self.install_ok(root, "--force")
        self.assertTrue(
            (root / MANIFEST_NAME).is_file(),
            "precondición del fixture: `install.sh` no publicó %s en %s — el "
            "oráculo del manifiesto sería vacuo"
            % (MANIFEST_NAME, root.name))
        return output

    def retired_paths(self, root: Path) -> list[str]:
        """Paths install #1 deployed from `RETIRED_SOURCE` (never hardcoded)."""
        paths = deployed_paths_for_source(load_manifest(root), RETIRED_SOURCE)
        self.assertGreaterEqual(
            len(paths),
            3,
            "precondición del fixture: el manifiesto de %s registra %d "
            "despliegue(s) de %s — las representaciones de B-1 necesitan al "
            "menos 3 (2 degeneradas + 1 control en la misma corrida): %s"
            % (root.name, len(paths), RETIRED_SOURCE, paths))
        for rel in paths:
            self.assertTrue(
                (root / rel).is_file(),
                "precondición del fixture: %s quedó registrado en el manifiesto "
                "de %s pero no está en disco" % (rel, root.name))
        return paths

    @contextlib.contextmanager
    def retired_source(self):
        """«Este archivo propio dejó de desplegarse»: the product source is
        removed from the copy for the duration of the block (restored after),
        so the install no longer deploys it and the prune must decide."""
        source = self.product / RETIRED_SOURCE
        shutil.copy2(self.retired_source_backup, source)  # known pre-state
        source.unlink()
        try:
            yield source
        finally:
            shutil.copy2(self.retired_source_backup, source)

    # -- declared hand-edit of the published manifest --------------------

    def edit_manifest(self, root: Path, mutate) -> None:
        """Rewrite the manifest install #1 published (declared hand-edit).

        `mutate` receives the decoded document; only the per-test temporary
        copy is written.
        """
        path = root / MANIFEST_NAME
        document = json.loads(path.read_text(encoding="utf-8"))
        mutate(document)
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def publish_degenerate_records(self, root: Path, records: dict) -> None:
        """Set one degenerate `artifacts` record per path (declared hand-edit).

        `records` maps an install-root-relative path to the record the manifest
        must carry from now on: `{"sha256": "", "source": ""}`,
        `{"sha256": ""}` (source key absent), `{"sha256": None, ...}`.
        """
        def mutate(document: dict) -> None:
            artifacts = document["artifacts"]
            for rel, record in records.items():
                self.assertIn(
                    rel, artifacts,
                    "precondición del hand-edit: el manifiesto no registra %s "
                    "— no habría registro que degenerar" % rel)
                artifacts[rel] = dict(record)
        self.edit_manifest(root, mutate)

    # -- observers -------------------------------------------------------

    def manifest_record(self, root: Path, rel: str) -> dict | None:
        """The record the installer PUBLISHES for `rel` after the run.

        Either map is accepted (`artifacts` / `pending_removal`): the spec's
        language is «sigue registrado». Keys are matched relative to the
        install root and absolute, as the two shapes the manifest has carried.
        """
        document = load_manifest(root)
        for key in (rel, str(root / rel)):
            for section in ("artifacts", "pending_removal"):
                record = (document.get(section) or {}).get(key)
                if isinstance(record, dict):
                    return record
        return None

    def assert_disclosed_as(self, output: str, root: Path, rel: str,
                            pattern: str, label: str) -> None:
        """The run discloses `rel` with the given verdict, either in its output
        or in the manifest's `conflicts` list (both surfaces are declared)."""
        output_lines = [
            line for line in output.splitlines()
            if rel in line and re.search(pattern, line)
        ]
        conflicts = json.dumps(load_manifest(root).get("conflicts") or [])
        self.assertTrue(
            output_lines or (rel in conflicts and re.search(pattern, conflicts)),
            f"{label}: la corrida no reporta {rel} como preservado/conflicto "
            f"(ni en la salida ni en el manifiesto; se buscó {pattern!r}); "
            f"salida:\n{tail(output)}")

    def assert_record_is_coherent(self, record: dict | None, rel: str,
                                  declared_source: str, label: str) -> None:
        """B-1 closing condition 2: each published value in its own slot.

        - the `source` slot carries the declared source (never the digest, never
          the empty hole the collapse leaves behind);
        - the `sha256` slot never receives the source text, and never the
          literal `None`/`null` token (a null digest is published as null/empty,
          not as a string).
        """
        self.assertIsNotNone(
            record,
            f"{label}: el registro preservado de {rel} no se publicó en el "
            f"manifiesto (ni en artifacts ni en pending_removal)")
        self.assertEqual(
            record.get("source"), declared_source,
            f"{label}: el registro publicado de {rel} no lleva la fuente "
            f"declarada en el slot `source` (columnas permutadas): {record!r}")
        digest = record.get("sha256")
        if isinstance(digest, str) and digest.strip():
            self.assertNotEqual(
                digest, declared_source,
                f"{label}: el registro publicado de {rel} lleva el texto de la "
                f"FUENTE en el slot del digest: {record!r}")
            self.assertNotIn(
                digest.strip().lower(), NULL_TOKENS,
                f"{label}: el registro publicado de {rel} lleva el token "
                f"{digest!r} en el slot del digest en lugar de un digest "
                f"vacío/null: {record!r}")


class TestB1ShalessManifestRecords(Rf2ManifestFixture):
    """B-1 · INV-2: a record without a usable sha256 is never treated as
    «own file, unchanged bytes». It is preserved and disclosed; only a record
    with a real digest that still matches the bytes is retirable."""

    def test_b1_a_empty_digest_without_source_is_preserved_and_disclosed(self) -> None:
        """B-1 · closing conditions 1 and 4 (`rereview.md:34-35,42`): with the
        digest EMPTY and the `source` column empty in one record and absent in
        the other, the re-install must NOT remove either file: both survive
        byte for byte, are disclosed as CONFLICT and stay registered.

        In-run control (non-vacuity): a third record of the same source keeps
        its correct digest → it IS retired in the same run, so the preservation
        is attributable to the degenerate record and not to a dead prune.
        RED today: the two degenerate records are classified «removable» and the
        files are deleted with `rm -f` («Obsolete prune: 3 own file(s)
        retired»)."""
        self.assert_staging_ready()
        root = self.new_root("rf2-b1a")
        self.install(root)
        paths = self.retired_paths(root)
        empty_source, absent_source, control = paths[0], paths[1], paths[2]

        expected = {
            rel: sha256_file(root / rel) for rel in (empty_source, absent_source)
        }
        self.publish_degenerate_records(root, {
            empty_source: {"sha256": "", "source": ""},
            absent_source: {"sha256": ""},
        })

        with self.retired_source():
            result = self.run_installer(root, "--force")
            output = result.stdout + result.stderr

            for rel in (empty_source, absent_source):
                self.assertTrue(
                    (root / rel).is_file(),
                    f"B-1/INV-2: {rel} tiene un registro con sha256 VACÍO —sin "
                    f"digest verificable no hay archivo propio «sin cambios»— y "
                    f"el instalador lo borró. Un registro sin digest se "
                    f"conserva y se reporta, nunca se retira. (rc="
                    f"{result.returncode})\n{tail(output)}")
                self.assertEqual(
                    sha256_file(root / rel), expected[rel],
                    f"B-1/INV-2: el registro sin digest de {rel} no fue "
                    f"retirado, pero el instalador reescribió el archivo")
                self.assert_disclosed_as(
                    output, root, rel, CONFLICT_RE, "B-1/INV-2")
                self.assertIsNotNone(
                    self.manifest_record(root, rel),
                    f"B-1: el registro preservado de {rel} desapareció del "
                    f"manifiesto — sin registro no hay resolución explícita "
                    f"posible")

            # In-run control (declared passing today): correct digest on a file
            # that is no longer deployed is still retired.
            self.assertFalse(
                (root / control).is_file(),
                f"B-1 (control positivo en la misma corrida): {control} "
                f"conserva su digest correcto y ya no se despliega, así que "
                f"debe retirarse; sigue en disco.\n{tail(output)}")
            self.assertIsNone(
                self.manifest_record(root, control),
                f"B-1 (control positivo): el obsoleto retirado {control} sigue "
                f"registrado en el manifiesto")

    def test_b1_a2_uninstall_does_not_remove_an_empty_digest_record(self) -> None:
        """B-1 · closing condition 1 on the `--uninstall` surface: the same
        decision function decides both surfaces, so an empty-digest record is
        not removed there either — the file survives byte for byte and the run
        discloses it as preserved for explicit resolution.

        RED today: «UNINSTALL …/adr-template/ADR.md» for all three and
        «Uninstall complete: 372 of 372 registered file(s) removed, 0
        preserved»."""
        self.assert_staging_ready()
        root = self.new_root("rf2-b1a2")
        self.install(root)
        paths = self.retired_paths(root)
        expected = {rel: sha256_file(root / rel) for rel in paths}
        self.publish_degenerate_records(
            root, {rel: {"sha256": "", "source": ""} for rel in paths})

        with self.retired_source():
            result = self.run_installer(root, "--uninstall", "--force")
            output = result.stdout + result.stderr

            surviving = [rel for rel in paths if (root / rel).is_file()]
            self.assertEqual(
                surviving, paths,
                f"B-1/INV-2: `--uninstall` borró archivos cuyos registros no "
                f"tienen digest («sin resolución explícita» no hay retiro); "
                f"borrados: {[rel for rel in paths if rel not in surviving]}"
                f"\n{tail(output)}")
            for rel in paths:
                self.assertEqual(
                    sha256_file(root / rel), expected[rel],
                    f"B-1/INV-2: `--uninstall` reescribió {rel} pese a no "
                    f"poder decidir su retiro")
                self.assert_disclosed_as(
                    output, root, rel, PRESERVED_RE, "B-1/`--uninstall`")

    def test_b1_b_empty_digest_with_present_source_publishes_a_coherent_record(self) -> None:
        """B-1 · closing condition 2 (`rereview.md:35`): digest EMPTY with a
        PRESENT `source` → the file is preserved AND the record the installer
        publishes stays coherent: the source text sits in the `source` slot,
        the digest slot is not filled with it, and no message says «registered
        <source>».

        RED today: the preservation happens by column collapse — the published
        record is `{"sha256": "<source text>", "source": ""}` and the CONFLICT
        says «registered <source text>»."""
        self.assert_staging_ready()
        root = self.new_root("rf2-b1b")
        self.install(root)
        paths = self.retired_paths(root)
        expected = {rel: sha256_file(root / rel) for rel in paths}
        self.publish_degenerate_records(
            root, {rel: {"sha256": "", "source": SOURCE_SENTINEL}
                   for rel in paths})

        with self.retired_source():
            result = self.run_installer(root, "--force")
            output = result.stdout + result.stderr

            for rel in paths:
                self.assertTrue(
                    (root / rel).is_file(),
                    f"B-1: {rel} tiene un registro con digest vacío y fuente "
                    f"presente; debe conservarse.\n{tail(output)}")
                self.assertEqual(
                    sha256_file(root / rel), expected[rel],
                    f"B-1: {rel} se conservó pero fue reescrito")
                self.assert_record_is_coherent(
                    self.manifest_record(root, rel), rel, SOURCE_SENTINEL,
                    "B-1 (digest vacío + fuente presente)")

            self.assertNotIn(
                f"registered {SOURCE_SENTINEL}", output,
                f"B-1: el CONFLICT publica el texto de la FUENTE como digest "
                f"registrado («registered {SOURCE_SENTINEL}») — las columnas "
                f"están permutadas en el mensaje:\n{tail(output)}")

    def test_b1_c_null_digest_publishes_a_coherent_record(self) -> None:
        """B-1 · closing condition 2 for the `null` digest (`rereview.md:36`):
        the file is preserved and the record is coherent — a null digest is not
        published (nor reported) as the literal string `None`.

        RED today: the record is `{"sha256": "None", ...}` and the CONFLICT says
        «registered None»."""
        self.assert_staging_ready()
        root = self.new_root("rf2-b1c")
        self.install(root)
        paths = self.retired_paths(root)
        expected = {rel: sha256_file(root / rel) for rel in paths}
        self.publish_degenerate_records(
            root, {rel: {"sha256": None, "source": SOURCE_SENTINEL}
                   for rel in paths})

        with self.retired_source():
            result = self.run_installer(root, "--force")
            output = result.stdout + result.stderr

            for rel in paths:
                self.assertTrue(
                    (root / rel).is_file(),
                    f"B-1: {rel} tiene un registro con digest null; debe "
                    f"conservarse.\n{tail(output)}")
                self.assertEqual(
                    sha256_file(root / rel), expected[rel],
                    f"B-1: {rel} se conservó pero fue reescrito")
                self.assert_record_is_coherent(
                    self.manifest_record(root, rel), rel, SOURCE_SENTINEL,
                    "B-1 (digest null)")

            self.assertNotRegex(
                output, r"(?i)registered\s+none\b",
                f"B-1: el CONFLICT publica «registered None» (el repr Python "
                f"del digest nulo) en lugar de declarar el digest ausente:\n"
                f"{tail(output)}")

    def test_b1_control_correct_digest_still_retires_the_obsolete_own_file(self) -> None:
        """B-1 · positive control, DECLARED PASSING today (`rereview.md:37`):
        with the manifest untouched (correct digest) and the source no longer
        deployed, the own obsolete file is still retired from disk and from the
        manifest. The fix must remove the escape of the degenerate
        representation, not the healthy prune."""
        self.assert_staging_ready()
        root = self.new_root("rf2-b1control")
        self.install(root)
        paths = self.retired_paths(root)

        with self.retired_source():
            result = self.run_installer(root, "--force")
            output = result.stdout + result.stderr

            surviving = [rel for rel in paths if (root / rel).is_file()]
            self.assertEqual(
                surviving, [],
                f"B-1 (control positivo): el obsoleto propio con digest "
                f"correcto y bytes intactos ya no se despliega y debe "
                f"retirarse; sigue en disco: {surviving}\n{tail(output)}")
            leftovers = [
                rel for rel in paths if self.manifest_record(root, rel) is not None
            ]
            self.assertEqual(
                leftovers, [],
                f"B-1 (control positivo): el archivo retirado sigue registrado "
                f"en el manifiesto: {leftovers}")


# --------------------------------------------------------------------- OPT-1


class TestOpt1EnvBranchNamesTheDefaultFile(ServerCredentialCase):
    """OPT-1 · §2.3 (`spec.md:48`): the 401/403 diagnosis names the resolved
    path of the credential file — including when the value that failed came
    from the ENVIRONMENT, where the file is the documented alternative."""

    def test_opt1_wrong_env_credential_diagnosis_also_names_the_default_file(self) -> None:
        """OPT-1: with an environment value the fixture rejects (401) and no
        credential file present, the diagnosis names the ENVIRONMENT as the
        provenance AND the default credential-file path
        (`<config-dir>/cdad/opencode-server.env`) as the alternative — so the
        user can resolve it without another document. The value never appears
        (INV-1).

        RED today: the environment branch says «…no credential file was
        consulted» without naming any candidate path."""
        server = self.server_fixture(require=OPT1_REQUIRED_PASSWORD)
        fake = self.fake_runtime("rf2-opt1", variant="succeeded")
        config_home = self.new_config_home("rf2-opt1-xdg")
        self.config_server(fake, server)

        proc = self.dispatch_server(
            fake, config_home=config_home,
            env_overrides={OPENCODE_PASSWORD_ENV: OPT1_WRONG_ENV_PASSWORD})
        out = self.envelope(proc, "OPT-1 credencial de entorno incorrecta")
        self.assertEqual(
            out["termination"], "blocked",
            f"OPT-1 precondición: credencial de ENTORNO incorrecta contra un "
            f"fixture que exige otra debe terminar `blocked`: "
            f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")

        diagnosis = out.get("diagnosis") or ""
        self.assertRegex(
            diagnosis, r"(?i)entorno|environment",
            f"OPT-1/§2.3: el diagnóstico no nombra el ENTORNO como la fuente "
            f"del valor rechazado: {diagnosis!r}")
        self.assert_names_path(
            diagnosis, self.default_env_file(config_home), "OPT-1/§2.3")
        self.assertNotIn(
            OPT1_WRONG_ENV_PASSWORD, diagnosis,
            f"OPT-1/INV-1: el diagnóstico imprime el VALOR de la credencial: "
            f"{diagnosis!r}")
        self.assertNotIn(
            OPT1_WRONG_ENV_PASSWORD, proc.stdout + proc.stderr,
            f"OPT-1/INV-1: el valor de la credencial aparece en la salida del "
            f"proceso")


if __name__ == "__main__":
    unittest.main(verbosity=2)
