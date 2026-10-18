#!/usr/bin/env python3
"""RED tests for the 006-003 review-fix round — three of the four findings the
orchestrator disposition resolves in ONE round: O-1, O-2 and O-4. **O-5 is NOT
tested here: it is not reproducible against the current tree** (see § «O-5
reportado, no testeado» at the end of this docstring; the scenario it describes
already holds, so no legitimate RED assertion exists and none was invented).

Contract: `docs/specs/006-003-installer-single-profile-delegation-config/spec.md`
(approved 2026-10-18, sha256
`c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890`), §2.2
(`delegation.json` v1, D3), §2.3 (credential file, D5), INV-2 (the installer
never deletes a locally modified file nor an unowned one: it only retires its
own with an unchanged sha256) — plus the review materialized in
`docs/specs/006-003-installer-single-profile-delegation-config/review.md` and its
«Disposición del orquestador (HITL delegada, 2026-10-18)»:
«O-1: una credencial de entorno vacía se trata como ausente (§2.3). O-2: el
lector de `delegation.json` y de la credencial resuelve la misma base que el
instalador (honra `CDAD_INSTALL_ROOT` cuando está definida, como §2.2). O-4: el
diagnóstico no imprime «credential file None»; nombra la fuente usada. O-5: un
registro con sha vacío no se retira; se conserva.» O-3 and O-6 stay as debt;
O-7 closes with the closing suite run (not this file).

Mapping (one test per reviewed finding — the finding IS the postcondition):

- test_o1_* -> O-1 · §2.3 (`spec.md:44`, the empty value is ABSENT) + PD-5d/PD-5e
               (the file the user configured supplies the credential; no empty
               `Authorization` header is ever sent)
- test_o2_g1_* -> O-2 · §2.2 (`spec.md:28`, `<INSTALL_ROOT>/.config/cdad/…` is
               the base when `XDG_CONFIG_HOME` is undefined) + D3 (the
               configured model is the ONLY source of `--model`)
- test_o2_g2_* -> O-2 · §2.2/§2.3 (the DEFAULT credential file
               `<config-dir>/cdad/opencode-server.env` lives under the same base)
- test_o4_* -> O-4 · §2.3 (`spec.md:48`, self-sufficient 401/403 diagnosis:
               provenance of the value, never the value)

Oracle discipline (black-box). NOTHING of the implementation is read:

- The external delegation runs through the SAME staged interface + fake
  destination binary the adapter suite already declares
  (`tests/test_005_009_t2_opencode_adapter.py::AdapterCase`, reused by import);
  the process frontier is the fake binary that records its argv, never a live
  runtime, never the host config.
- The installer runs as a subprocess against a PRODUCT COPY whose staging is
  regenerated in the copy (`tests/test_006_003_u4_delegation_config.py::
  InstallerHarness`, reused by import — the same declared fixture the U4/U7
  focals use); `CDAD_INSTALL_ROOT` plus a tempdir `HOME` confine every write
  (INV-6). The host's `HOME`/`~/.config/cdad` is NEVER read nor written.
- The server credential is exercised against the LOCAL loopback HTTP fixture
  (`tests/test_006_001_t1_selection.py::FakeInfoServer`) that requires Basic
  auth; the host's `OPENCODE_PASSWORD`/`OPENCODE_SERVER_PASSWORD` are stripped
  from every child environment by the inherited `dispatch()`.
- The manifest-record shape observed while probing O-5 (`{"sha256", "source"}`
  records under `artifacts`, plus an empty `pending_removal` map) was read from
  the manifest the installer PUBLISHES over a throwaway product copy — never by
  reading `install.sh`. Only test-local sentinels are written (INV-1).

Declared hand-edit (the only one, minimal and declared where it happens):

- O-2: the `delegation.json` the installer created is rewritten with a minimal
  v1 document (test-chosen models) at the SAME path the installer used — user
  data, A-3.

Expected RED against the current tree (declared, not accidental — each failure
is an AssertionError about missing behavior, never an import/syntax/fixture
error):

- O-1: `OPENCODE_PASSWORD=""` exported is taken as PRESENT (`os.environ.get`
  with no empty check) → an empty `Basic` header goes to the fixture → 401 →
  `blocked` != `completed`, and the empty-header oracle fires.
- O-2 g1: the reader resolves the config dir from `HOME` (`Path.home()/.config`)
  when `XDG_CONFIG_HOME` is undefined → the document the installer wrote under
  `<root>/.config/cdad/` is not read → no `--model` in the argv.
- O-2 g2: same base divergence for the DEFAULT credential file → not read →
  401 → `blocked` != `completed`.
- O-4: the 401 diagnosis of the environment branch interpolates the unset file
  path («credential file None») → the no-`None` oracle fires.

Fixtures use the declared bounds unchanged (the shared `FAST_WAIT` of the
006-001/006-003 server focals and the 300 s subprocess cap): no oracle is
loosened, no timeout is retuned here. The known fixture race of
`test_006_001_t1_selection.py::test_pd2_connection_refused_is_transport_error`
does not apply — every server fixture of this file is reachable, so no oracle
here is time-sensitive beyond those declared bounds.

O-5 reportado, no testeado (mismatch del pedido, con evidencia — NO se inventó
una postcondición sustituta). The packet asks for O-5 (INV-2): «un registro del
manifiesto con sha256 vacío, cuyo archivo ya no se despliega, NO se retira en la
reinstalación (se conserva y se reporta)». Probed black-box against this very
revision (`install.sh` is byte-identical to the reviewed HEAD `401d951`: only
`docs/` changed after the review), on a throwaway product copy with redirected
roots, by hand-editing the published manifest (the record's `sha256` left
empty / set to `null` / whitespace / a wrong digest / the key removed, in
`artifacts` and in `pending_removal`):

  - reinstall: the file ARRIVES INTACT and the run publishes
    `CONFLICT: <path> — preserved (obsolete own file modified locally since the
    recorded install …)`, rc=1, and the record is carried in `pending_removal`;
    the intact siblings of the same source ARE retired in the same run;
  - `--uninstall`: same preservation (`PRESERVED for explicit resolution`);
  - `--dry-run`: announces the same verdict (`DRY-RUN CONFLICT … preserved`)
    and deletes nothing;
  - `--check`: reports the preserved path as PENDING-REMOVAL.

  i.e. the requirement the disposition states for O-5 ALREADY HOLDS in every
  surface and representation probed, so a RED assertion for it would be a
  fabricated failure. Reported to the orchestrator for disposition (drop to
  debt, re-scope, or a new packet). Side observation of the same probe (NOT a
  postcondition of this packet, deliberately NOT asserted here): when the
  recorded `sha256` of a preserved record is EMPTY, the carried
  `pending_removal` entry is published with its fields swapped
  (`{"sha256": "<source path>", "source": ""}`) — a manifest-coherence defect
  worth a finding of its own; the clean locally-modified flow (PD-6b) publishes
  a coherent record.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

# Reuse declared by import (single definition; the imported bases carry no test
# methods, so importing them imports no foreign tests).
from test_006_001_t1_selection import (
    OPENCODE_PASSWORD_ENV,
    OPENCODE_SERVER_PASSWORD_ENV,
    basic_auth_header,
)
from test_006_003_u4_delegation_config import InstallerHarness
from test_006_003_u6_server_credential import ServerCredentialCase

# §2.2/§2.3 layout under the config dir (the same names the U4/U6 focals use).
CONFIG_DIR_REL = Path(".config") / "cdad"
DELEGATION_FILE_NAME = "delegation.json"
DEFAULT_ENV_FILE_NAME = "opencode-server.env"
ENV_EXAMPLE_FILE_NAME = "opencode-server.env.example"

# A-2: the destination id is the destination runtime identifier.
OPENCODE_DESTINATION = "opencode"
# The role the packet of this fixture declares (`AdapterCase.prepare_ok`).
PACKET_ROLE = "test-writer"

# Test-local sentinels: never a host value (INV-1).
O1_FILE_PASSWORD = "cdad-006-003-rf-o1-file-sentinel"
O2_CREDENTIAL_SENTINEL = "cdad-006-003-rf-o2-credential-sentinel"
O4_REQUIRED_PASSWORD = "cdad-006-003-rf-o4-required-sentinel"
O4_WRONG_ENV_PASSWORD = "cdad-006-003-rf-o4-wrong-env-sentinel"
# The model the test configures in the delegation config (never a real one).
O2_MODEL = "fixture-006-003-rf-delegation-model"


# ------------------------------------------------------------------ O-1 / O-4


class TestO1EmptyEnvCredentialIsAbsent(ServerCredentialCase):
    """O-1 · §2.3 (`spec.md:44`) + PD-5e: an EMPTY value is treated as absent —
    never an empty `Authorization` header — so the credential file the user
    configured supplies the value."""

    def test_o1_empty_environment_value_is_absent_and_the_file_is_used(self) -> None:
        """O-1: with `OPENCODE_PASSWORD=""` exported and a 0600 file at the
        default path carrying the required value, the dispatch reaches
        `completed` and the fixture receives the FILE credential; an empty
        `Basic` header is never sent. RED today: the empty environment value is
        taken as present → empty header → 401 (`blocked` != `completed`) and the
        empty-header oracle fires."""
        server = self.server_fixture(require=O1_FILE_PASSWORD)
        fake = self.fake_runtime("o1", variant="succeeded")
        config_home = self.new_config_home("o1-xdg")
        self.write_env_file(
            self.default_env_file(config_home),
            "# fixture (O-1): the file carries the credential the env leaves "
            "empty\n"
            f"{OPENCODE_PASSWORD_ENV}={O1_FILE_PASSWORD}\n",
            mode=0o600)
        self.config_server(fake, server)

        proc = self.dispatch_server(
            fake, config_home=config_home,
            env_overrides={OPENCODE_PASSWORD_ENV: ""})
        out = self.envelope(proc, "O-1 credencial de entorno vacía")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"`{OPENCODE_PASSWORD_ENV}=\"\"` exportado: la credencial debe "
                f"tratarse como AUSENTE (§2.3) y usarse la del archivo 0600; el "
                f"despacho no llegó a `completed`: {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")

        authorizations = self.fixture_authorizations(server)
        self.assertTrue(
            server.requests,
            msg="O-1: el servidor de fixture no recibió ninguna request — la "
                "observación del header sería vacua")
        self.assertIn(
            basic_auth_header(O1_FILE_PASSWORD), authorizations,
            msg=f"O-1: el fixture no recibió la credencial del ARCHIVO 0600 "
                f"(valor vacío de entorno ⇒ ausente, §2.3): {authorizations!r}")
        self.assertNotIn(
            basic_auth_header(""), authorizations,
            msg=f"O-1/§2.3: se envió un header Authorization VACÍO (valor vacío "
                f"⇒ ausente; nunca header vacío): {authorizations!r}")


class TestO4IncorrectEnvCredentialDiagnosis(ServerCredentialCase):
    """O-4 · §2.3 (`spec.md:48`): the 401 diagnosis is self-sufficient and
    names the provenance of the value — it never prints an unresolvable path
    («credential file None») when the value came from the environment."""

    def test_o4_401_diagnosis_omits_none_and_names_the_environment(self) -> None:
        """O-4: an INCORRECT `OPENCODE_PASSWORD` from the environment (the
        fixture requires another value, no credential file exists) → `blocked`
        with a diagnosis that (a) does not print `None` as the credential-file
        path and (b) names the ENVIRONMENT as the source of the value used. RED
        today: the environment branch interpolates the unset file path →
        «credential file None»."""
        server = self.server_fixture(require=O4_REQUIRED_PASSWORD)
        fake = self.fake_runtime("o4", variant="succeeded")
        # The document exists (normal post-install state); no credential file.
        config_home = self.new_config_home("o4-xdg")
        self.config_server(fake, server)

        proc = self.dispatch_server(
            fake, config_home=config_home,
            env_overrides={OPENCODE_PASSWORD_ENV: O4_WRONG_ENV_PASSWORD})
        out = self.envelope(proc, "O-4 credencial de entorno incorrecta")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"credencial de ENTORNO incorrecta contra un servidor que exige "
                f"otra: la terminación no es `blocked`: "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")

        diagnosis = out.get("diagnosis") or ""
        self.assertNotIn(
            "None", diagnosis,
            msg=f"O-4: el diagnóstico imprime `None` como ruta de la credencial "
                f"cuando el valor vino del ENTORNO: {diagnosis!r}")
        self.assertRegex(
            diagnosis, r"(?i)entorno|environment",
            msg=f"O-4/§2.3: el diagnóstico no nombra el ENTORNO como la fuente "
                f"usada del valor (procedencia): {diagnosis!r}")


# ----------------------------------------------------------------- ----- O-2


class RedirectedRootReaderCase(InstallerHarness, ServerCredentialCase):
    """O-2 fixture: the product copy of `InstallerHarness` (so the config is the
    one the INSTALLER writes) + the staged adapter/fake-binary machinery of
    `ServerCredentialCase` (so the READER is observed through the destination
    argv / the HTTP fixture). `XDG_CONFIG_HOME` is removed from the child
    environment and `HOME` points to yet another tempdir: the only base left for
    the reader is `<install-root>/.config/cdad/` (§2.2)."""

    def installer_config_dir(self, install_root: Path) -> Path:
        return install_root / CONFIG_DIR_REL

    def assert_installer_created_the_config(self, install_root: Path) -> None:
        """Precondition (PD-2a, GREEN since U4): the installer's own base."""
        for name in (DELEGATION_FILE_NAME, ENV_EXAMPLE_FILE_NAME):
            path = self.installer_config_dir(install_root) / name
            self.assertTrue(
                path.is_file(),
                msg=f"precondición (fixture, PD-2a): el instalador no creó "
                    f"{CONFIG_DIR_REL / name} bajo la raíz redirigida "
                    f"{install_root}")

    def write_delegation_document(self, install_root: Path,
                                  models: dict) -> Path:
        """Declared hand-edit: a minimal v1 document (test-chosen models, no
        `credential_env_file`) at the SAME path the installer used — user data
        (A-3)."""
        path = self.installer_config_dir(install_root) / DELEGATION_FILE_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"version": 1, "models": models}, indent=2,
                       sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def dispatch_from_redirected_root(
            self, fake: dict, *, install_root: Path,
            home: Path) -> subprocess.CompletedProcess:
        """Invoke the staged interface with `XDG_CONFIG_HOME` UNDEFINED and
        `HOME` at another tempdir, declaring `CDAD_INSTALL_ROOT` (§2.2/INV-6).
        The host credential variables are stripped (never the host config)."""
        home.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        for var in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV,
                    "XDG_CONFIG_HOME"):
            env.pop(var, None)
        env["HOME"] = str(home)
        env["CDAD_INSTALL_ROOT"] = str(install_root)
        env["PWD"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(self.staged),
             "--project-root", str(self.root),
             "--packet", self.packet_id,
             "--destination", OPENCODE_DESTINATION,
             "--exec-config", str(fake["config"])],
            capture_output=True, text=True, env=env, timeout=300)


class TestO2RedirectedRootIsTheReaderBase(RedirectedRootReaderCase):
    """O-2 · §2.2/§2.3: with `CDAD_INSTALL_ROOT` defined and `XDG_CONFIG_HOME`
    undefined, the reader resolves the SAME base the installer wrote to:
    `<root>/.config/cdad/`."""

    def test_o2_g1_model_configured_in_the_redirected_root_reaches_the_argv(
            self) -> None:
        """O-2/§2.2/D3: the model is configured in the `delegation.json` the
        installer created under the redirected root (its only named place),
        while `HOME` points to ANOTHER tempdir → the destination argv carries
        `--model <configured>`. RED today: the reader resolves
        `Path.home()/.config` → the document is not read → no `--model`."""
        self.assert_staging_ready()
        install_root = self.new_root("o2-g1-root")
        self.install_ok(install_root)
        self.assert_installer_created_the_config(install_root)
        self.write_delegation_document(
            install_root, {OPENCODE_DESTINATION: {PACKET_ROLE: O2_MODEL}})

        self.assert_derived_agents_published()
        fake = self.fake_runtime("o2-g1", variant="succeeded")
        home = Path(self._tmp) / "o2-g1-elsewhere-home"

        proc = self.dispatch_from_redirected_root(
            fake, install_root=install_root, home=home)
        out = self.envelope(proc, "O-2 modelo en raíz redirigida")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"precondición del argv: la delegación no llegó a `completed` "
                f"con la config del usuario en {CONFIG_DIR_REL} de la raíz "
                f"redirigida: {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")

        call = self.packet_call(fake, "O-2 modelo")
        argv = call["argv"]
        paired = (
            "--model" in argv
            and argv.index("--model") + 1 < len(argv)
            and argv[argv.index("--model") + 1] == O2_MODEL)
        self.assertTrue(
            paired or ("--model=" + O2_MODEL) in argv,
            msg=f"O-2/§2.2/D3: con `CDAD_INSTALL_ROOT` definida y "
                f"`XDG_CONFIG_HOME` indefinida, el lector debe resolver la "
                f"misma base que el instalador ({CONFIG_DIR_REL} de la raíz) y "
                f"llevar el modelo configurado en el argv del destino; argv: "
                f"{argv!r}")

    def test_o2_g2_default_credential_file_is_read_from_the_redirected_root(
            self) -> None:
        """O-2/§2.3: the DEFAULT credential file
        (`<config-dir>/cdad/opencode-server.env`) is resolved under the
        redirected root too: the user follows the installer's own instructions
        (copy the `.example`, `chmod 600`) under that base and the fixture
        receives the Basic auth → `completed`. RED today: the default path is
        resolved from `HOME` → not found → 401 → `blocked`."""
        self.assert_staging_ready()
        server = self.server_fixture(require=O2_CREDENTIAL_SENTINEL)
        install_root = self.new_root("o2-g2-root")
        self.install_ok(install_root)
        self.assert_installer_created_the_config(install_root)
        # v1 document without `credential_env_file`: the default path applies.
        self.write_delegation_document(install_root, {})
        self.write_env_file(
            self.installer_config_dir(install_root) / DEFAULT_ENV_FILE_NAME,
            "# fixture (O-2): the user's cp+chmod 600 of the installer's "
            ".example\n"
            f"{OPENCODE_PASSWORD_ENV}={O2_CREDENTIAL_SENTINEL}\n",
            mode=0o600)

        fake = self.fake_runtime("o2-g2", variant="succeeded")
        self.config_server(fake, server)
        home = Path(self._tmp) / "o2-g2-elsewhere-home"

        proc = self.dispatch_from_redirected_root(
            fake, install_root=install_root, home=home)
        out = self.envelope(proc, "O-2 credencial por defecto")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"O-2/§2.3: la credencial por DEFECTO vive donde el instalador "
                f"creó la config ({CONFIG_DIR_REL / DEFAULT_ENV_FILE_NAME} de "
                f"la raíz redirigida) y el lector debe resolverla ahí; el "
                f"despacho no llegó a `completed`: {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")
        self.assertIn(
            basic_auth_header(O2_CREDENTIAL_SENTINEL),
            self.fixture_authorizations(server),
            msg=f"O-2/§2.3: el fixture no recibió la credencial del archivo por "
                f"defecto de la raíz redirigida: "
                f"{self.fixture_authorizations(server)!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
