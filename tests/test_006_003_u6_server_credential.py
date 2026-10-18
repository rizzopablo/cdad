#!/usr/bin/env python3
"""RED tests for 006-003 U6 — the OpenCode server credential.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18, amendments A-4/A-5), §2.3 (D5), postconditions PD-5a..e,
invariant INV-1, decision D5, and amendment A-4 (the two config files are
created by U4; U6 never touches `install.sh`). Plan: the approved U6 sheet of
docs/specs/006-003-installer-single-profile-delegation-config/plan.md.

Mapping (one test per numbered postcondition):

- TestPd5aMissingCredential / test_pd_5a_*
    -> PD-5a  (no credential at all, 401 from the fixture: the diagnosis names
               both `OPENCODE_PASSWORD` / `OPENCODE_SERVER_PASSWORD`, the
               RESOLVED default file path, and the provenance of the value —
               it must live in the environment of the dispatching process)
- TestPd5bInsecurePermissions / test_pd_5b_*
    -> PD-5b  (`.env` with mode 0644 → rejected with a diagnosis naming the
               path and the found mode; the fixture receives NO Authorization)
- TestPd5cSecureFileUsed / test_pd_5c_*
    -> PD-5c  (`.env` with mode 0600 and a sentinel value → the fixture
               receives the right credential and the dispatch continues; the
               sentinel NEVER appears in stdout/stderr/destination argv/I8)
- TestPd5dEnvWinsOverFile / test_pd_5d_*
    -> PD-5d  (env var and file both present with different values → the
               environment wins)
- TestPd5eEmptyValueIsAbsent / test_pd_5e_*
    -> PD-5e  (`KEY=` with an empty value is treated as ANOTHER key's absence:
               never an empty header — the next key in the file is used)
- TestPd5CredentialEnvFileRedirect / test_pd_5_credential_env_file_*
    -> §2.2/§2.3/D5 (`credential_env_file` in `delegation.json` redirects the
               credential source; the default path is not used)

Oracle discipline (black-box). The adapter runs as a SUBPROCESS (the same
staged interface the rest of the suite uses, reused by import from
006-001 T1 / 005-009 T2 — no implementation is read) in `mode: server`
against a LOCAL loopback HTTP fixture of this test file (`FakeInfoServer`,
reused by import) that requires Basic auth. NEVER a live runtime, NEVER the
host config: the config dir is redirected with `XDG_CONFIG_HOME` to the test
tempdir and the host's `OPENCODE_PASSWORD` / `OPENCODE_SERVER_PASSWORD` are
stripped from the child environment by the inherited `dispatch()`. Only
test-local sentinels are written (INV-1).

Expected RED against the current tree (declared, not accidental). Today the
adapter resolves the server credential from the two environment variables
only (006-001 GREEN); it never reads a credential file nor `delegation.json`:

  - PD-5a: the 401 diagnosis already names both variables, but NOT the
    resolved file path nor the provenance → the path assertion fails.
  - PD-5b: with the file ignored, the fixture gets no Authorization (that
    part already holds) but the diagnosis names neither the path nor the
    mode → those assertions fail.
  - PD-5c: the 0600 file is ignored → no header → 401 → `blocked` !=
    `completed` → the precondition assertion fails before the absence
    oracle (declared).
  - PD-5d: the environment already wins over a file that is not read at all,
    so this non-regression MAY pass today (declared, not hidden; it is the
    anchor that a future file-reading path must not break).
  - PD-5e: the empty `OPENCODE_PASSWORD=` line plus a non-empty
    `OPENCODE_SERVER_PASSWORD=` line requires reading the file → today the
    file is ignored → `blocked` != `completed` → fails.
  - `credential_env_file`: the configured path is ignored → no header → 401
    → `blocked` != `completed` → fails.

Every failure is an AssertionError about missing behavior, never an
ImportError/syntax/fixture error. If the shared server fixture turns out to
be flaky under load (a known race debt), this file uses the fixture's
defaults unchanged and reports it instead of loosening the oracle silently.
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

# Reuse declared by import (single definition; the fixture bases carry no test
# methods, so importing them imports no foreign tests).
from test_005_009_t1_interface import dispatch_records
from test_006_001_t1_selection import (
    FAST_WAIT,
    MATCHING_CLIENT_SEMVER,
    OPENCODE_PASSWORD_ENV,
    OPENCODE_SERVER_PASSWORD_ENV,
    FakeInfoServer,
    Pd600T1Case,
    basic_auth_header,
)

# Test-local sentinels: never a host value (INV-1).
ENV_PASSWORD = "cdad-006-003-u6-env-sentinel-password"
FILE_PASSWORD = "cdad-006-003-u6-file-sentinel-password"
ALT_FILE_PASSWORD = "cdad-006-003-u6-alt-file-sentinel-password"
OTHER_PASSWORD = "cdad-006-003-u6-other-sentinel-password"

# §2.2/§2.3 layout under the redirected config dir.
CONFIG_DIR_NAME = "cdad"
DEFAULT_ENV_FILE_NAME = "opencode-server.env"
DELEGATION_FILE_NAME = "delegation.json"

SERVER_BODY = json.dumps({"version": MATCHING_CLIENT_SEMVER}).encode()


# --------------------------------------------------------------- fixture base


class ServerCredentialCase(Pd600T1Case):
    """Base of the U6 focal: server-mode dispatch against a loopback HTTP
    fixture that requires Basic auth, with the config dir redirected to the
    test tempdir (never the host config; `HOME` also redirected, INV-6)."""

    # -- config layout --------------------------------------------------

    def new_config_home(self, name: str, *,
                        with_delegation: bool = True) -> Path:
        """Fresh `XDG_CONFIG_HOME` for one test.

        `with_delegation=False` leaves no `delegation.json` (the credential
        file must still be found: its default path does not depend on that
        document). Otherwise a minimal valid v1 document is written, matching
        the normal post-install state produced by U4/PD-2a.
        """
        config_home = Path(self._tmp) / name
        config_home.mkdir(parents=True, exist_ok=True)
        if with_delegation:
            self.write_delegation(config_home)
        return config_home

    def default_env_file(self, config_home: Path) -> Path:
        """§2.3 default: `<config-dir>/cdad/opencode-server.env`."""
        return config_home / CONFIG_DIR_NAME / DEFAULT_ENV_FILE_NAME

    def write_env_file(self, path: Path, text: str, *,
                       mode: int = 0o600) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        os.chmod(path, mode)
        return path

    def write_delegation(self, config_home: Path, *,
                         credential_env_file: Path | None = None,
                         models: dict | None = None) -> Path:
        doc: dict = {"version": 1, "models": models or {}}
        if credential_env_file is not None:
            doc["credential_env_file"] = str(credential_env_file)
        path = config_home / CONFIG_DIR_NAME / DELEGATION_FILE_NAME
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    # -- server fixture --------------------------------------------------

    def server_fixture(self, *, require: str | None = None) -> FakeInfoServer:
        """Loopback `/api/info` fixture (never a live runtime). With
        `require` it answers 401 unless the Basic auth matches."""
        expected = basic_auth_header(require) if require is not None else None
        server = FakeInfoServer(
            body=SERVER_BODY, expected_authorization=expected)
        self.addCleanup(server.stop)
        return server

    def config_server(self, fake: dict, server: FakeInfoServer) -> dict:
        return self.patch_config(
            fake, {"mode": "server", "server": server.url, "wait": FAST_WAIT})

    # -- dispatch --------------------------------------------------------

    def dispatch_server(self, fake: dict, *, config_home: Path,
                        env_overrides: dict | None = None,
                        ) -> subprocess.CompletedProcess:
        """Stage the adapter in `mode: server` with the config dir (and HOME)
        redirected to the test tempdir; the inherited `dispatch()` already
        strips the host credential variables."""
        home = Path(self._tmp) / "home"
        home.mkdir(parents=True, exist_ok=True)
        overrides = {
            "XDG_CONFIG_HOME": str(config_home),
            "HOME": str(home),
        }
        if env_overrides:
            overrides.update(env_overrides)
        return self.dispatch(fake, env_overrides=overrides, cwd=self.root)

    # -- observers -------------------------------------------------------

    def fixture_authorizations(self, server: FakeInfoServer) -> list:
        return [request.get("authorization") for request in server.requests]

    def assert_no_authorization(self, server: FakeInfoServer,
                                label: str) -> None:
        sent = [auth for auth in self.fixture_authorizations(server) if auth]
        self.assertEqual(
            sent, [],
            msg=f"{label}: el fixture recibió un header Authorization pese a "
                f"que la credencial no debía usarse (PD-5b): {sent!r}")

    def destination_argv(self, fake: dict) -> list[list]:
        return [list(call.get("argv", [])) for call in self.binary_calls(fake)]

    def assert_names_path(self, text: str, path: Path, label: str) -> None:
        candidates = sorted({str(path), str(path.resolve())})
        self.assertTrue(
            any(candidate in text for candidate in candidates),
            msg=f"{label}: el diagnóstico no nombra la ruta del archivo "
                f"({candidates}): {text!r}")

    def ledger_text(self, out: dict, records_before: dict) -> str:
        record_path = self.assert_attempt_is_in_ledger(out, records_before)
        return record_path.read_text(encoding="utf-8")


# ------------------------------------------------------------------ PD-5a


class TestPd5aMissingCredential(ServerCredentialCase):
    """PD-5a/§2.3/D5: without any credential, the 401 diagnosis is
    self-sufficient: both variables, the resolved file path, and the
    provenance of the value (it must be in the environment of the process
    that dispatches)."""

    def test_pd_5a_401_diagnosis_names_vars_path_and_provenance(self) -> None:
        """PD-5a: a server fixture that requires a credential and no env var
        nor file → `blocked`; the diagnosis names `OPENCODE_PASSWORD` and
        `OPENCODE_SERVER_PASSWORD`, the RESOLVED default path
        (`<config>/cdad/opencode-server.env`), and where the value comes from
        (the `opencode serve` in use, living in the dispatching process's
        environment). Concept oracle, never the value. RED today: the
        diagnosis names the two variables but neither the path nor the
        provenance."""
        server = self.server_fixture(require=ENV_PASSWORD)
        fake = self.fake_runtime("pd5a", variant="succeeded")
        config_home = self.new_config_home("pd5a-xdg")
        self.config_server(fake, server)

        proc = self.dispatch_server(fake, config_home=config_home)
        out = self.envelope(proc, "PD-5a sin credencial")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"servidor con credencial y ninguna provista: la terminación "
                f"no es `blocked` (PD-5a/§2.3): {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")

        diagnosis = out.get("diagnosis") or ""
        for var in (OPENCODE_PASSWORD_ENV, OPENCODE_SERVER_PASSWORD_ENV):
            self.assertIn(
                var, diagnosis,
                msg=f"PD-5a: el diagnóstico no nombra {var!r}: {diagnosis!r}")
        self.assert_names_path(
            diagnosis, self.default_env_file(config_home), "PD-5a")
        self.assertRegex(
            diagnosis, r"(?i)entorno|environment",
            msg=f"PD-5a: el diagnóstico no sitúa la credencial en el ENTORNO "
                f"del proceso que despacha: {diagnosis!r}")
        self.assertRegex(
            diagnosis, r"(?i)despach|dispatch|proceso|process",
            msg=f"PD-5a: el diagnóstico no nombra el PROCESO que despacha "
                f"como el lugar donde debe estar el valor: {diagnosis!r}")
        self.assertRegex(
            diagnosis, r"(?i)serve",
            msg=f"PD-5a: el diagnóstico no declara la procedencia del valor "
                f"(la contraseña del `opencode serve` en uso): {diagnosis!r}")


# ------------------------------------------------------------------ PD-5b


class TestPd5bInsecurePermissions(ServerCredentialCase):
    """PD-5b/§2.3/D5: a group/world-readable `.env` (0644) is rejected with a
    diagnosis that names the path and the found mode; no header is sent."""

    def test_pd_5b_world_readable_file_rejected_naming_path_and_mode(
            self) -> None:
        """PD-5b: `.env` at the default path with mode 0644 and the right
        value → `blocked`, diagnosis naming the path and the found mode
        (0644), and the fixture receives NO Authorization header. RED today:
        the file is ignored, so the diagnosis names neither path nor mode."""
        server = self.server_fixture(require=FILE_PASSWORD)
        fake = self.fake_runtime("pd5b", variant="succeeded")
        config_home = self.new_config_home("pd5b-xdg")
        env_file = self.write_env_file(
            self.default_env_file(config_home),
            "# fixture (U6/PD-5b)\n"
            f"{OPENCODE_PASSWORD_ENV}={FILE_PASSWORD}\n",
            mode=0o644)
        self.config_server(fake, server)

        proc = self.dispatch_server(fake, config_home=config_home)
        out = self.envelope(proc, "PD-5b archivo 0644")
        self.assertEqual(
            out["termination"], "blocked",
            msg=f"archivo de credencial con bits 0o077 (0644): la terminación "
                f"no es `blocked` (PD-5b/§2.3): {out['termination']!r}, "
                f"diagnosis {out.get('diagnosis')!r}")

        diagnosis = out.get("diagnosis") or ""
        self.assert_names_path(diagnosis, env_file, "PD-5b")
        self.assertRegex(
            diagnosis, r"0?644|rw-r--r--",
            msg=f"PD-5b: el diagnóstico no nombra el MODO encontrado (0644): "
                f"{diagnosis!r}")
        self.assert_no_authorization(server, "PD-5b")


# ------------------------------------------------------------------ PD-5c


class TestPd5cSecureFileUsed(ServerCredentialCase):
    """PD-5c/§2.3/D5: a `.env` with mode 0600 supplies the credential (the
    dispatch continues) and the value never leaves stdout/stderr/argv/I8."""

    def test_pd_5c_0600_file_credential_is_used_and_never_leaks(self) -> None:
        """PD-5c: `.env` at the default path with mode 0600 and a sentinel
        value → the fixture receives Basic auth with the sentinel and the
        dispatch reaches `completed`; the sentinel NEVER appears in
        stdout, stderr, the destination argv nor the I8 record. RED today:
        the file is ignored → no header → 401 (`blocked` != `completed`)."""
        server = self.server_fixture(require=FILE_PASSWORD)
        fake = self.fake_runtime("pd5c", variant="succeeded")
        config_home = self.new_config_home("pd5c-xdg")
        self.write_env_file(
            self.default_env_file(config_home),
            "# cdad server credential (fixture, U6/PD-5c)\n"
            f"{OPENCODE_PASSWORD_ENV}={FILE_PASSWORD}\n",
            mode=0o600)
        self.config_server(fake, server)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_server(fake, config_home=config_home)
        out = self.envelope(proc, "PD-5c archivo 0600")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"archivo de credencial 0600 con valor: el despacho no llegó "
                f"a `completed` (PD-5c: la credencial se usa): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        self.assertIn(
            basic_auth_header(FILE_PASSWORD),
            self.fixture_authorizations(server),
            msg=f"PD-5c: el fixture no recibió la credencial del archivo "
                f"0600; autorizaciones vistas: "
                f"{self.fixture_authorizations(server)!r}")

        # INV-1: the value never appears in any observable surface.
        for label, text in (
                ("stdout", proc.stdout), ("stderr", proc.stderr),
                ("diagnosis", out.get("diagnosis") or "")):
            self.assertNotIn(
                FILE_PASSWORD, text,
                msg=f"PD-5c/INV-1: la credencial aparece en {label}: "
                    f"{text!r}")
        for argv in self.destination_argv(fake):
            self.assertNotIn(
                FILE_PASSWORD, argv,
                msg=f"PD-5c/INV-1: la credencial aparece en el argv del "
                    f"destino: {argv!r}")
        self.assertNotIn(
            FILE_PASSWORD, self.ledger_text(out, records_before),
            msg="PD-5c/INV-1: la credencial aparece en el registro I8")


# ------------------------------------------------------------------ PD-5d


class TestPd5dEnvWinsOverFile(ServerCredentialCase):
    """PD-5d/§2.3/D5: with the env var and the file both present and
    different, the environment wins."""

    def test_pd_5d_environment_wins_over_file(self) -> None:
        """PD-5d: env `OPENCODE_PASSWORD` = A and a 0600 file whose
        `OPENCODE_PASSWORD` = B (B != A), with the fixture requiring A → the
        dispatch reaches `completed` and every request carries A, never B.
        Declared: may PASS today (the adapter already resolves from env and
        does not read the file); it is the anchor that the new file-reading
        path must respect."""
        server = self.server_fixture(require=ENV_PASSWORD)
        fake = self.fake_runtime("pd5d", variant="succeeded")
        config_home = self.new_config_home("pd5d-xdg")
        self.write_env_file(
            self.default_env_file(config_home),
            f"{OPENCODE_PASSWORD_ENV}={FILE_PASSWORD}\n",
            mode=0o600)
        self.config_server(fake, server)

        proc = self.dispatch_server(
            fake, config_home=config_home,
            env_overrides={OPENCODE_PASSWORD_ENV: ENV_PASSWORD})
        out = self.envelope(proc, "PD-5d env sobre archivo")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"env y archivo presentes con valores distintos: la "
                f"terminación no es `completed` — la VARIABLE DE ENTORNO debe "
                f"ganar (PD-5d): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        authorizations = self.fixture_authorizations(server)
        self.assertIn(
            basic_auth_header(ENV_PASSWORD), authorizations,
            msg=f"PD-5d: el fixture no recibió la credencial de la VARIABLE DE "
                f"ENTORNO: {authorizations!r}")
        self.assertNotIn(
            basic_auth_header(FILE_PASSWORD), authorizations,
            msg=f"PD-5d: el fixture recibió la credencial del ARCHIVO pese a "
                f"haber variable de entorno (gana el entorno): "
                f"{authorizations!r}")


# ------------------------------------------------------------------ PD-5e


class TestPd5eEmptyValueIsAbsent(ServerCredentialCase):
    """PD-5e/§2.3/D5: `KEY=` with an empty value is treated as absent (never
    an empty header): the next key of the file supplies the credential."""

    def test_pd_5e_empty_value_is_absent_never_an_empty_header(self) -> None:
        """PD-5e: a 0600 `.env` whose first key is `OPENCODE_PASSWORD=`
        (empty) and whose second key is `OPENCODE_SERVER_PASSWORD=<sentinel>`,
        with the fixture requiring the sentinel → the dispatch reaches
        `completed` and never sends an empty header. RED today: the file is
        ignored → no header → 401 (`blocked` != `completed`)."""
        server = self.server_fixture(require=FILE_PASSWORD)
        fake = self.fake_runtime("pd5e", variant="succeeded")
        config_home = self.new_config_home("pd5e-xdg")
        self.write_env_file(
            self.default_env_file(config_home),
            "# fixture (U6/PD-5e): empty first key must be treated as absent\n"
            f"{OPENCODE_PASSWORD_ENV}=\n"
            f"{OPENCODE_SERVER_PASSWORD_ENV}={FILE_PASSWORD}\n",
            mode=0o600)
        self.config_server(fake, server)

        proc = self.dispatch_server(fake, config_home=config_home)
        out = self.envelope(proc, "PD-5e valor vacío")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"`{OPENCODE_PASSWORD_ENV}=` vacío: la credencial debe "
                f"tratarse como AUSENTE y usarse la siguiente clave no vacía "
                f"del archivo; el despacho no llegó a `completed` (PD-5e): "
                f"{out['termination']!r}, diagnosis {out.get('diagnosis')!r}")
        authorizations = self.fixture_authorizations(server)
        self.assertIn(
            basic_auth_header(FILE_PASSWORD), authorizations,
            msg=f"PD-5e: el fixture no recibió la credencial de la clave no "
                f"vacía: {authorizations!r}")
        self.assertNotIn(
            basic_auth_header(""), authorizations,
            msg=f"PD-5e: se envió un header Authorization VACÍO (valor vacío "
                f"⇒ ausente, nunca header vacío): {authorizations!r}")


# ------------------------------------- §2.2/§2.3: credential_env_file


class TestPd5CredentialEnvFileRedirect(ServerCredentialCase):
    """§2.2/§2.3/D5: `credential_env_file` in `delegation.json` redirects the
    credential source (the default path is not used)."""

    def test_pd_5_credential_env_file_redirects_the_source(self) -> None:
        """§2.2/§2.3/D5: with `credential_env_file` pointing to another 0600
        file (which carries the required value) while the DEFAULT path holds
        a different value, the dispatch reaches `completed` using the
        CONFIGURED path. RED today: `delegation.json` is ignored → no header
        → 401 (`blocked` != `completed`)."""
        server = self.server_fixture(require=ALT_FILE_PASSWORD)
        fake = self.fake_runtime("pd5-envfile", variant="succeeded")
        config_home = self.new_config_home(
            "pd5-envfile-xdg", with_delegation=False)
        # The default path exists with a DIFFERENT (wrong) value...
        self.write_env_file(
            self.default_env_file(config_home),
            f"{OPENCODE_PASSWORD_ENV}={OTHER_PASSWORD}\n", mode=0o600)
        # ...and the configured path carries the required value.
        alt = Path(self._tmp) / "alt-cred" / "server.env"
        self.write_env_file(
            alt, f"{OPENCODE_PASSWORD_ENV}={ALT_FILE_PASSWORD}\n", mode=0o600)
        self.write_delegation(config_home, credential_env_file=alt)
        self.config_server(fake, server)

        proc = self.dispatch_server(fake, config_home=config_home)
        out = self.envelope(proc, "credential_env_file")
        self.assertEqual(
            out["termination"], "completed",
            msg=f"`credential_env_file` apunta a otra ruta con el valor "
                f"requerido: el despacho no llegó a `completed` (§2.2/§2.3/"
                f"D5): {out['termination']!r}, diagnosis "
                f"{out.get('diagnosis')!r}")
        authorizations = self.fixture_authorizations(server)
        self.assertIn(
            basic_auth_header(ALT_FILE_PASSWORD), authorizations,
            msg=f"§2.2/§2.3: el fixture no recibió la credencial de la ruta "
                f"configurada en `credential_env_file`: {authorizations!r}")
        self.assertNotIn(
            basic_auth_header(OTHER_PASSWORD), authorizations,
            msg=f"§2.2/§2.3: el fixture recibió la credencial de la ruta por "
                f"DEFECTO pese a que `credential_env_file` apunta a otra: "
                f"{authorizations!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
