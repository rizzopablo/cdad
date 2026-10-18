#!/usr/bin/env python3
"""U8 acceptance / E2E for 006-003 — the whole walk on a REDIRECTED root.

Contract: docs/specs/006-003-installer-single-profile-delegation-config/spec.md
(approved 2026-10-18, sha256
c25ebf0e0c7867c03de072439128e7a77e4b2a7dcd7f52228535ea9785d18890) — PD-8a
(`install.sh --check` PASSes on a fresh redirected install), PD-8b (`make
validate` PASSes), PD-8c (the full suite, green once — see the frontier note),
the acceptance face of PD-2a/PD-2b (the installer leaves `delegation.json` and
an empty-valued `opencode-server.env.example`), PD-3b (the external delegation
takes the model ONLY from `delegation.json`), PD-5c (a 0600 credential file is
used), PD-6a (the re-install retires its own obsolete file), INV-1 (the
credential value never leaves stdout/stderr/argv/registry), INV-3 (no
installable agent fixes a model), INV-6 (a redirected root is the ONLY thing
the install touches) and INV-7 (no silent model fallback). Orchestrator
amendments A-1..A-5 and plan U8 + amendment A-6.

Map test -> postcondition (one test per numbered postcondition):

- test_pd_8a_*        -> PD-8a + INV-3
    (generator without `--profile` over a product copy -> install -> `--check`
     PASS; every installed agent carries no `model:` line and the installed
     orchestrators name no concrete model; the installer left
     `delegation.json` (v1, destination key per A-2) and an
     `opencode-server.env.example` whose data lines are all `KEY=` with an
     EMPTY value)
- test_pd_3b_pd_5c_*  -> PD-3b + PD-5c + INV-1 + INV-7
    (the installed config is completed with a fixture model for the packet's
     role and a 0600 `opencode-server.env` carrying a SENTINEL; a `mode:
     server` dispatch against a loopback fixture that REQUIRES that credential
     reaches `completed`, the destination argv carries the `delegation.json`
     model and NOT the legacy exec-config model, and the sentinel appears in
     NO observable surface)
- test_pd_8b_*        -> PD-8b
    (`make validate`'s own validator, run against the acceptance install)
- test_pd_6a_*        -> PD-6a (bridge with U7) + PD-8a after the re-install
    (removing one of the product's own sources and re-installing retires the
     deployed copy, drops it from the manifest and `--check` still PASSes)
- test_inv_6_*        -> INV-6
    (the fake HOME stays byte for byte empty and nothing appears next to the
     redirected root / config dir across the full walk, dispatch included)

Frontier notes, declared (PD-15 — no promise of a sandbox):

- PD-8c ("suite completa verde, corrida una vez por quien cierra") is NOT run
  here: the packet's full-suite policy makes the closer run it once. This file
  maps PD-8c to that closing run, never to a partial run of this module.
- PD-8b is asserted through `tests/validate-consistency.sh` — the body of the
  `validate` target — with `CDAD_INSTALL_ROOT`/`HOME`/`XDG_CONFIG_HOME` pointed
  at the ACCEPTANCE install. Reason, declared: that validator's F011 block
  shells out to `scripts/validate-subagents.sh`, whose `[repo]` half runs
  `install.sh --check` against the OWNER'S installation; unredirected, it
  cross-checks a stale host copy (drift, not a product assert) and would make
  this oracle depend on the machine. Redirected, it is the same script suite
  over the install this acceptance just produced: hermetic and faithful.
- INV-6 is asserted over the FAKE home and the redirected config dir only. The
  suite cannot prove the absence of writes to a path it does not own without
  reading the owner's home; that limit is declared, not hidden.

Oracle discipline (black-box, no implementation is read):

- the installer runs as a SUBPROCESS against a PRODUCT COPY whose staging is
  regenerated IN THE COPY by `scripts/cdad-generate.py` (no `--profile`, the
  «generador equivalente» the U8 sheet allows when `make staging` is not used);
  `CDAD_INSTALL_ROOT`, `HOME` and `XDG_CONFIG_HOME` always live inside the
  test's temporary directory;
- the external delegation runs through the SAME staged interface the adapter
  suite uses (`test_005_009_t2_opencode_adapter.py::AdapterCase`, reused by
  import) against a LOOPBACK HTTP fixture (`test_006_001_t1_selection.py`,
  reused by import), never a live runtime and never the host config; the
  inherited `dispatch()` strips the host's `OPENCODE_PASSWORD` /
  `OPENCODE_SERVER_PASSWORD`;
- the observation of the deployed tree and of the ownership manifest uses the
  public surface the installer publishes; the manifest helpers are reused from
  the U7 focal (single definition).

Acceptance status: this walk is EXPECTED GREEN on the current tree (U1..U7
landed). A failure here is a finding to report WITH its evidence — it is never
weakened to force a green. Sentinel values and fixture models are test-local
(INV-1): no host value is read or written.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Reuse declared by import (fixture bases carry no test methods, so importing
# them imports no foreign tests).
from test_005_009_t1_interface import dispatch_records
from test_006_001_t1_selection import (
    OPENCODE_PASSWORD_ENV,
    basic_auth_header,
)
from test_006_003_u6_server_credential import ServerCredentialCase
from test_006_003_u7_prune_obsolete import (
    PENDING_RE,
    RETIRED_SOURCE,
    RETIRED_TAIL,
    deployed_paths_for_source,
    load_manifest,
    manifest_keys_referencing,
    snapshot_diff,
    snapshot_tree,
    tail,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# Public product entries the installer needs next to install.sh (the same set
# the U2/U4/U7 focals and the 004-001 acceptance matrix declare).
PRODUCT_ENTRIES = ("install.sh", "scripts", "skills", "sources", "agents")
RUNTIMES = ("opencode", "claude-code")
STACK = "odoo"
STAGING_REL = Path("build") / "staging"

# §2.2 layout under the redirected config dir (A-2: destination id = runtime id)
# and the role the packet of this fixture delegates (`prepare` publishes a
# test-writer packet, AdapterCase).
CONFIG_DIR_NAME = "cdad"
DELEGATION_NAME = "delegation.json"
ENV_EXAMPLE_NAME = "opencode-server.env.example"
ENV_FILE_NAME = "opencode-server.env"
DESTINATION_ID = "opencode"
ROLE = "test-writer"

# Test-local fixture values: no host value (INV-1).
DELEGATION_MODEL = "fixture-u8-delegation-model"
LEGACY_EXEC_MODEL = "fixture-u8-legacy-exec-model"
CREDENTIAL_SENTINEL = "cdad-006-003-u8-sentinel-password"

# PD-8a: the published PASS report.
PASS_RE = re.compile(r"(?i)\bpass\b")

# PD-1e/INV-3: an installed agent fixes no model (frontmatter line) and the
# installed orchestrators name no concrete model (mirrors PD-7a's token set).
MODEL_FRONTMATTER_RE = re.compile(r"(?m)^model:")
CONCRETE_MODEL_RE = re.compile(
    r"deepseek|glm-|qwen|minimax|sonnet|haiku|opus|mofgw/")

# PD-2b: a non-comment line is exactly `KEY=` with an EMPTY value.
ENV_LINE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=$")

ORCHESTRATOR_GLOBS = ("cdad-orchestrator.md", "cdad-orchestrator-odoo.md")


# --------------------------------------------------------------- product copy


class ProductCopyMixin:
    """Class-level PRODUCT COPY with the staging regenerated inside the copy.

    The copy is the «generador equivalente sobre una copia» of the U8 sheet:
    `scripts/cdad-generate.py --runtime <r> --stack odoo --out build/staging`
    without `--profile`. The repository itself is never installed into and the
    real HOME is never a destination.
    """

    maxDiff = None

    @classmethod
    def prepare_product(cls) -> None:
        cls._product_tmp = tempfile.TemporaryDirectory(
            prefix="cdad-u8-acceptance-")
        cls.base = Path(cls._product_tmp.name).resolve()
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

        # Pristine copy of the own source the PD-6a bridge retires.
        cls.retired_source_backup = cls.base / "retired-source.backup"
        shutil.copy2(cls.product / RETIRED_SOURCE, cls.retired_source_backup)

    @classmethod
    def cleanup_product(cls) -> None:
        cls._product_tmp.cleanup()


# ------------------------------------------------------------- walk fixture


class U8WalkCase(ServerCredentialCase, ProductCopyMixin):
    """The acceptance fixture: the adapter fixture of U6 (loopback server with
    Basic auth + staged interface) plus a product copy the installer can run.

    Every directory the walk touches is created under `self._tmp`: the install
    root, the config dir and the fake HOME (INV-6).
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.prepare_product()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.cleanup_product()

    # -- staging precondition ---------------------------------------------

    def assert_staging_ready(self) -> None:
        for runtime, result in self.generate_results.items():
            self.assertEqual(
                result.returncode,
                0,
                msg="precondición del fixture: el generador falló para "
                    "runtime=%s (sin `--profile`, PD-1f/PD-8a):\n%s"
                    % (runtime, tail(result.stderr or result.stdout)),
            )

    # -- walk layout -------------------------------------------------------

    def new_walk(self, name: str) -> dict:
        base = Path(self._tmp) / ("walk-%s" % name)
        walk = {
            "base": base,
            "root": base / "root",
            "xdg": base / "xdg",
            "home": base / "home",
        }
        for path in ("root", "xdg", "home"):
            walk[path].mkdir(parents=True)
        return walk

    def config_dir(self, walk: dict) -> Path:
        return walk["xdg"] / CONFIG_DIR_NAME

    def delegation_path(self, walk: dict) -> Path:
        return self.config_dir(walk) / DELEGATION_NAME

    def env_example_path(self, walk: dict) -> Path:
        return self.config_dir(walk) / ENV_EXAMPLE_NAME

    def env_file_path(self, walk: dict) -> Path:
        return self.config_dir(walk) / ENV_FILE_NAME

    # -- installer ---------------------------------------------------------

    def installer_env(self, walk: dict) -> dict:
        """`CDAD_INSTALL_ROOT`, fake `HOME` and `XDG_CONFIG_HOME`: the only
        three destinations of the walk, all inside the test tempdir."""
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(walk["root"])
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        env["HOME"] = str(walk["home"])
        env["XDG_CONFIG_HOME"] = str(walk["xdg"])
        env.pop("CDAD_MODEL_PROFILE", None)
        return env

    def run_installer(self, walk: dict, *args: str,
                      ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(self.product / "install.sh"), *args],
            cwd=str(self.product),
            env=self.installer_env(walk),
            text=True,
            capture_output=True,
            check=False,
        )

    def install_ok(self, walk: dict) -> str:
        result = self.run_installer(walk, "--force")
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            msg="precondición del fixture: la instalación redirigida falló "
                "(rc=%s):\n%s" % (result.returncode, tail(output)),
        )
        return output

    def check_ok(self, walk: dict, label: str) -> str:
        """PD-8a: `install.sh --check` PASSes on the redirected root."""
        result = self.run_installer(walk, "--check")
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            msg="%s: `install.sh --check` no PASSó sobre la raíz redirigida "
                "(PD-8a; rc=%s):\n%s"
                % (label, result.returncode, tail(output)),
        )
        self.assertRegex(
            output,
            PASS_RE,
            msg="%s: `--check` salió 0 pero no publicó el informe PASS "
                "(PD-8a):\n%s" % (label, tail(output)),
        )
        self.assertIsNone(
            PENDING_RE.search(output),
            msg="%s: `--check` reporta PENDING-REMOVAL sobre una raíz recién "
                "instalada (PD-8a/PD-6a):\n%s" % (label, tail(output)),
        )
        return output

    # -- user configuration (A-3: data, never owned) -----------------------

    def fill_delegation(self, walk: dict, models: dict) -> Path:
        """Complete the installer-created document for the packet's role.

        The document is the installer's own (PD-2a precondition, never a
        hand-written replacement): only the `models` map is completed.
        """
        path = self.delegation_path(walk)
        self.assertTrue(
            path.is_file(),
            msg="precondición: el instalador no creó %s (U4/PD-2a)"
                % path,
        )
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(doc, dict, msg="precondición: delegation.json")
        doc.setdefault("models", {}).setdefault(DESTINATION_ID, {}).update(
            models)
        path.write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return path

    def write_credential_file(self, walk: dict, value: str) -> Path:
        """PD-5c: the credential the walk uses, mode 0600, test-local value."""
        path = self.env_file_path(walk)
        path.write_text(
            "# fixture (U8 acceptance, INV-1: valor de prueba)\n"
            "%s=%s\n" % (OPENCODE_PASSWORD_ENV, value),
            encoding="utf-8")
        os.chmod(path, 0o600)
        return path

    # -- external delegation ----------------------------------------------

    def dispatch_walk(self, fake: dict, walk: dict,
                      ) -> subprocess.CompletedProcess:
        """The installed configuration + the fake destination binary.

        `XDG_CONFIG_HOME`/`HOME` are the walk's own directories, so the adapter
        reads the config the installer produced and never the host's (§2.2).
        """
        return self.dispatch(
            fake,
            env_overrides={
                "XDG_CONFIG_HOME": str(walk["xdg"]),
                "HOME": str(walk["home"]),
            },
            cwd=self.root,
        )

    def set_legacy_exec_model(self, fake: dict, model: str) -> Path:
        """PD-3b/INV-7: the retired exec-config key, present on purpose, so the
        walk proves it does NOT drive the effective model."""
        config = json.loads(fake["config"].read_text(encoding="utf-8"))
        config["model"] = model
        fake["config"].write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        return fake["config"]

    # -- observers ---------------------------------------------------------

    def installed_agent_files(self, walk: dict) -> list[Path]:
        return sorted(
            path
            for path in walk["root"].rglob("*.md")
            if path.is_file() and "agents" in path.parts
        )

    def assert_no_installed_agent_fixes_a_model(self, walk: dict) -> None:
        """PD-1e/INV-3: no deployed agent declares `model:` and the deployed
        orchestrators name no concrete model."""
        agents = self.installed_agent_files(walk)
        self.assertTrue(
            agents,
            msg="precondición: la instalación no desplegó ningún agente bajo "
                "una ruta `agents/` (el oráculo de INV-3 sería vacuo)",
        )
        offenders = [
            str(path.relative_to(walk["root"]))
            for path in agents
            if MODEL_FRONTMATTER_RE.search(
                path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            offenders,
            [],
            msg="PD-1e/INV-3: agentes instalados que fijan un modelo con "
                "`model:`: %s" % offenders,
        )
        orchestrators = [
            path for path in agents
            if path.name in ORCHESTRATOR_GLOBS
        ]
        self.assertTrue(
            orchestrators,
            msg="precondición: no se desplegó ningún orquestador "
                "(PD-7a/INV-3) — el oráculo de nombres de modelo sería vacuo",
        )
        named = [
            str(path.relative_to(walk["root"]))
            for path in orchestrators
            if CONCRETE_MODEL_RE.search(
                path.read_text(encoding="utf-8", errors="replace"))
        ]
        self.assertEqual(
            named,
            [],
            msg="PD-7a/INV-3: orquestadores instalados que nombran un modelo "
                "concreto: %s" % named,
        )

    def assert_sentinel_absent_everywhere(self, sentinel: str,
                                          proc: subprocess.CompletedProcess,
                                          out: dict, fake: dict,
                                          records_before: dict,
                                          walk: dict) -> None:
        """INV-1: the credential value lives in no observable surface."""
        for label, text in (
            ("stdout", proc.stdout),
            ("stderr", proc.stderr),
            ("diagnosis", out.get("diagnosis") or ""),
        ):
            self.assertNotIn(
                sentinel, text,
                msg="INV-1: la credencial aparece en %s: %r" % (label, text))
        for argv in self.destination_argv(fake):
            self.assertNotIn(
                sentinel, argv,
                msg="INV-1: la credencial aparece en el argv del destino: %r"
                    % (argv,))
        after = dispatch_records(self.root, self.execution_id)
        for stem, path in sorted(after.items()):
            if stem in records_before:
                continue
            self.assertNotIn(
                sentinel, path.read_text(encoding="utf-8"),
                msg="INV-1: la credencial aparece en el registro I8 %r" % stem)
        for path in sorted(self.results_base().rglob("*")):
            if not path.is_file():
                continue
            self.assertNotIn(
                sentinel.encode("utf-8"), path.read_bytes(),
                msg="INV-1: la credencial aparece en la entrega durable %s"
                    % path.name)
        self.assertNotIn(
            sentinel, self.delegation_path(walk).read_text(encoding="utf-8"),
            msg="INV-1: la credencial aparece en delegation.json")


# ------------------------------------------------------------------ PD-8a


class TestPd8aAcceptanceInstall(U8WalkCase):
    """PD-8a (+ the acceptance face of PD-2a/PD-2b and INV-3): a clean
    redirected install PASSes `--check`, fixes no model and leaves the user
    configuration empty."""

    def test_pd_8a_install_passes_check_without_models_and_with_empty_config(
            self) -> None:
        """PD-8a/PD-1e/PD-2a/PD-2b/INV-3: generator without `--profile` over
        the product copy → install into the redirected root → `install.sh
        --check` PASS; the installed agents carry no `model:` and the installed
        orchestrators name no concrete model; the installer left a valid v1
        `delegation.json` (destination `opencode`) and an
        `opencode-server.env.example` whose data lines are `KEY=` with an EMPTY
        value."""
        self.assert_staging_ready()
        walk = self.new_walk("pd8a")
        self.install_ok(walk)

        self.check_ok(walk, "PD-8a install")
        self.assert_no_installed_agent_fixes_a_model(walk)

        delegation = self.delegation_path(walk)
        example = self.env_example_path(walk)
        self.assertTrue(
            delegation.is_file(),
            msg="PD-2a (aceptación): falta %s tras la instalación"
                % delegation.relative_to(walk["xdg"]),
        )
        self.assertTrue(
            example.is_file(),
            msg="PD-2a (aceptación): falta %s tras la instalación"
                % example.relative_to(walk["xdg"]),
        )
        doc = json.loads(delegation.read_text(encoding="utf-8"))
        self.assertEqual(
            doc.get("version"), 1,
            msg="PD-2a/§2.2: delegation.json no declara `version: 1` (%r)"
                % doc.get("version"),
        )
        models = doc.get("models")
        self.assertIsInstance(
            models, dict,
            msg="PD-2a/§2.2: `models` no es un mapa por destino (%r)"
                % type(models),
        )
        self.assertIn(
            DESTINATION_ID, models,
            msg="PD-2a/A-2: `models` no tiene el destino `%s`: %s"
                % (DESTINATION_ID, sorted(models)),
        )

        data_lines = [
            stripped
            for line in example.read_text(encoding="utf-8").splitlines()
            if (stripped := line.strip()) and not stripped.startswith("#")
        ]
        self.assertTrue(
            data_lines,
            msg="PD-2b: el `.example` no declara ninguna clave",
        )
        bad = [line for line in data_lines if not ENV_LINE_RE.match(line)]
        self.assertEqual(
            bad,
            [],
            msg="PD-2b/§2.3: líneas del `.example` sin la forma `KEY=` con "
                "valor vacío (¿secreto?): %r" % bad,
        )


# --------------------------------------------- PD-3b / PD-5c / INV-1 / INV-7


class TestPd3bPd5cAcceptanceDelegation(U8WalkCase):
    """PD-3b/PD-5c/INV-1/INV-7: the installed configuration drives the model
    and the credential of a server-mode dispatch, and the credential value
    never leaves."""

    def test_pd_3b_pd_5c_server_dispatch_uses_installed_config_and_no_leak(
            self) -> None:
        """PD-3b/PD-5c/INV-1/INV-7: after installing, the walk completes
        `delegation.json` for the packet's role and writes a 0600
        `opencode-server.env` with a sentinel. A `mode: server` dispatch
        against a loopback fixture that REQUIRES that sentinel reaches
        `completed`; the destination argv carries the delegation model (and not
        the legacy exec-config model, which is present on purpose); the
        sentinel appears in no stdout/stderr/diagnosis/argv/I8/delivery/
        delegation.json surface."""
        self.assert_staging_ready()
        walk = self.new_walk("delegation")
        self.install_ok(walk)
        self.fill_delegation(walk, {ROLE: DELEGATION_MODEL})
        self.write_credential_file(walk, CREDENTIAL_SENTINEL)

        server = self.server_fixture(require=CREDENTIAL_SENTINEL)
        fake = self.fake_runtime("u8-walk", variant="succeeded")
        self.config_server(fake, server)
        self.set_legacy_exec_model(fake, LEGACY_EXEC_MODEL)
        records_before = dispatch_records(self.root, self.execution_id)

        proc = self.dispatch_walk(fake, walk)
        out = self.envelope(proc, "U8 aceptación: despacho server")
        self.assertEqual(
            out["termination"], "completed",
            msg="PD-5c/PD-8a: el despacho en modo server con la credencial del "
                "archivo 0600 instalado no llegó a `completed`: %r, diagnosis "
                "%r" % (out["termination"], out.get("diagnosis")),
        )

        # The credential WAS used (non-vacuity of the absence oracle, PD-5c).
        self.assertIn(
            basic_auth_header(CREDENTIAL_SENTINEL),
            self.fixture_authorizations(server),
            msg="PD-5c: el fixture no recibió la credencial del archivo 0600; "
                "autorizaciones vistas: %r"
                % (self.fixture_authorizations(server),),
        )

        # PD-3b/INV-7: the effective model is the delegation one, only.
        argv = self.packet_call(fake, "U8 aceptación")["argv"]
        paired = (
            "--model" in argv
            and argv.index("--model") + 1 < len(argv)
            and argv[argv.index("--model") + 1] == DELEGATION_MODEL
        )
        self.assertTrue(
            paired or ("--model=" + DELEGATION_MODEL) in argv,
            msg="PD-3b: el argv del destino no lleva el modelo de "
                "delegation.json (%r): %r" % (DELEGATION_MODEL, argv),
        )
        self.assertNotIn(
            LEGACY_EXEC_MODEL, argv,
            msg="PD-3b/INV-7/INV-1: el argv del destino lleva el `model` "
                "heredado de la exec-config (%r); la config de delegación es "
                "la única fuente: %r" % (LEGACY_EXEC_MODEL, argv),
        )

        self.assert_sentinel_absent_everywhere(
            CREDENTIAL_SENTINEL, proc, out, fake, records_before, walk)


# ------------------------------------------------------------------ PD-8b


class TestPd8bMakeValidate(U8WalkCase):
    """PD-8b: `make validate` PASSes — asserted on the acceptance install."""

    def test_pd_8b_make_validate_passes_on_the_acceptance_install(self) -> None:
        """PD-8b: `tests/validate-consistency.sh` (the body of `make validate`)
        run with the walk's root/HOME/config dir returns rc=0 and publishes
        zero failed asserts. Declared: run against the install this acceptance
        produced, because the validator's F011 block cross-checks the active
        installation through `install.sh --check`; unredirected it inspects the
        owner's (stale) copy — a host dependency, not a product assert."""
        self.assert_staging_ready()
        walk = self.new_walk("pd8b")
        self.install_ok(walk)
        self.check_ok(walk, "PD-8b precondición")

        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(walk["root"])
        env["HOME"] = str(walk["home"])
        env["XDG_CONFIG_HOME"] = str(walk["xdg"])
        env.pop("CDAD_MODEL_PROFILE", None)
        result = subprocess.run(
            ["bash", str(REPO_ROOT / "tests" / "validate-consistency.sh")],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            msg="PD-8b: `make validate` falló sobre la instalación de "
                "aceptación (rc=%s):\n%s"
                % (result.returncode, tail(output, 30)),
        )
        failing = [
            line for line in output.splitlines() if line.startswith("FAIL:")
        ]
        self.assertEqual(
            failing,
            [],
            msg="PD-8b: el validador reportó asserts fallidos:\n%s"
                % "\n".join(failing[:10]),
        )
        self.assertIn(
            "Assert FAIL: 0", output,
            msg="PD-8b: el validador no publicó `Assert FAIL: 0`:\n%s"
                % tail(output, 15),
        )


# --------------------------------------------------- PD-6a (bridge with U7)


class TestPd6aAcceptanceReinstall(U8WalkCase):
    """PD-6a (+ PD-8a after the re-install): the bridge with U7."""

    def test_pd_6a_reinstall_retires_own_obsolete_and_check_still_passes(
            self) -> None:
        """PD-6a/PD-8a: install #1 deploys and registers an own source; the
        source is then removed from the product copy (simulating «dejó de
        desplegarse») and install #2 retires the deployed copies and drops them
        from the manifest; `install.sh --check` still PASSes with no
        PENDING-REMOVAL."""
        self.assert_staging_ready()
        walk = self.new_walk("pd6a")
        self.install_ok(walk)

        paths = deployed_paths_for_source(load_manifest(walk["root"]),
                                          RETIRED_SOURCE)
        self.assertTrue(
            paths,
            msg="precondición del fixture: el manifiesto no registra ningún "
                "artefacto desplegado desde %s — no habría obsoleto propio "
                "que retirar" % RETIRED_SOURCE,
        )
        for rel in paths:
            self.assertTrue(
                (walk["root"] / rel).is_file(),
                msg="precondición del fixture: %s figura en el manifiesto "
                    "pero no está en disco" % rel,
            )

        source = self.product / RETIRED_SOURCE
        shutil.copy2(self.retired_source_backup, source)  # known pre-state
        source.unlink()
        try:
            self.install_ok(walk)

            surviving = [
                rel for rel in paths if (walk["root"] / rel).is_file()]
            self.assertEqual(
                surviving,
                [],
                msg="PD-6a: el archivo propio ya no se despliega y sus bytes "
                    "no cambiaron, así que la reinstalación debe retirarlo; "
                    "sigue en disco: %s" % surviving,
            )
            still_registered = manifest_keys_referencing(
                load_manifest(walk["root"]), RETIRED_TAIL)
            self.assertEqual(
                still_registered,
                [],
                msg="PD-6a: el obsoleto retirado sigue registrado en el "
                    "manifiesto: %s" % still_registered,
            )

            self.check_ok(walk, "PD-6a tras reinstalar")
        finally:
            shutil.copy2(self.retired_source_backup, source)


# ------------------------------------------------------------------ INV-6


class TestInv6RedirectedHome(U8WalkCase):
    """INV-6: the redirected root is the only destination of the walk."""

    def test_inv_6_full_walk_never_touches_the_fake_home(self) -> None:
        """INV-6: across install → `--check` → re-install → server-mode
        dispatch, the fake HOME stays byte for byte EMPTY, nothing appears
        next to the redirected root/config dir, and every file the walk creates
        outside the install root lives under `<XDG_CONFIG_HOME>/cdad/`."""
        self.assert_staging_ready()
        walk = self.new_walk("inv6")
        home_before = snapshot_tree(walk["home"])

        self.install_ok(walk)
        self.check_ok(walk, "INV-6 install")
        self.install_ok(walk)

        # A dispatch in the same redirected environment: the adapter must not
        # fall back to the host directories either.
        server = self.server_fixture(require=CREDENTIAL_SENTINEL)
        fake = self.fake_runtime("u8-inv6", variant="succeeded")
        self.config_server(fake, server)
        self.fill_delegation(walk, {ROLE: DELEGATION_MODEL})
        self.write_credential_file(walk, CREDENTIAL_SENTINEL)
        proc = self.dispatch_walk(fake, walk)
        self.envelope(proc, "INV-6 despacho")

        self.assertEqual(
            snapshot_diff(home_before, snapshot_tree(walk["home"])),
            [],
            msg="INV-6: el HOME falso no quedó intacto durante el recorrido",
        )
        self.assertEqual(
            sorted(path.name for path in walk["home"].iterdir()),
            [],
            msg="INV-6: la instalación creó entradas en el HOME falso",
        )
        self.assertEqual(
            sorted(path.name for path in walk["base"].iterdir()),
            ["home", "root", "xdg"],
            msg="INV-6: aparecieron entradas fuera de la raíz redirigida, del "
                "HOME falso y del config dir del test",
        )
        self.assertEqual(
            sorted(path.name for path in walk["xdg"].iterdir()),
            [CONFIG_DIR_NAME],
            msg="INV-6/§2.2: el config dir del test no contiene solo `%s/`"
                % CONFIG_DIR_NAME,
        )
        for path in self.config_dir(walk).iterdir():
            self.assertTrue(
                path.is_file(),
                msg="INV-6/§2.2: entrada inesperada en el config dir: %s"
                    % path.name,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
