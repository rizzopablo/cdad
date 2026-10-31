#!/usr/bin/env python3
"""RED tests for 006-006 U1 (PD-1, PD-2, PD-3, PD-4, PD-5, PD-15, PD-16(a)):
the reviewed object is DECLARED in the contract (`object_kind`), the companion
spec is fixed by digest (`spec_path`/`spec_sha256`/`spec_version`), the plan
checks apply ONLY to a document of form `plan`, `inputs` carries one entry per
fixed document, and the render names the form and the companion.

Contract: docs/specs/006-006-spec-plan-review/spec.md (PD-1, PD-2, PD-3, PD-4,
PD-5, PD-15, PD-16(a); §2.1 R-1..R-10, §2.2, §2.3) + plan.md §3 ficha U1 (su
bloque `plan-tasks` y §4 A-1).

Black-box: the CLI is invoked as a subprocess; implementation sources are never
read. Every project is a DISPOSABLE temporary fixture (the `PrepareProject`
pattern of `tests/test_004_003_t2_plan_review.py`); the real HOME and the
repository state are never touched. The fixtures are OWN (`DRAFT_PLAN_RELPATH`
is NOT reused): the eleven files that share it are untouched (plan §4, A-1).

Oracle decisions (interfaces defined by this RED, derived from the spec):
- `object_kind` is the FORM of the PRINCIPAL document, `spec` | `plan`, absent
  => `plan` (R-4, fail-closed). It travels to the `REQUEST.json` contract AND
  to the packet metadata (PD-1).
- The companion is ALWAYS the spec and only exists when the principal is the
  plan (R-7/R-8); its digest is COMPUTED by `prepare` from the file's bytes
  (R-5) and equals the value `sha256sum` prints; `spec_path`, `spec_sha256`
  and `spec_version` appear together or not at all (R-6).
- A rejection is a BEHAVIOURAL rejection: the product's own `ERROR: ...`
  convention, NOT an argparse usage error. The helper therefore refuses a
  stderr carrying "unrecognized arguments" — a CLI that does not know the flag
  has not exercised the postcondition (and the test must fail for that reason,
  not silently pass on a usage error).
- The intra-revision byte identity (PD-2, PD-5, PD-16(a)) is observed on the
  two blocks the spec declares ADDITIVE (`## Contract` and `## Inputs`): with
  the new keys absent they keep their exact bytes. The whole `PACKET.md` is
  NOT frozen: it embeds the instruction sources and their digests, which
  legitimately change between revisions (R-10). This RED asserts NOTHING
  between revisions — that is the declaration of U3 and the case of U6
  (PD-16(b)/(c)); here the comparison is always inside ONE revision (one
  product, one run).
- The `purpose` of an `inputs` entry names the FORM of its document
  ("draft spec for review" / "draft plan for review", R-9) and the entries
  are ordered principal first, companion second.
- The render's `## Contract` section names the form as `- form: spec` |
  `- form: plan` (R-9, literal) and, with a companion, its path, digest and
  version.

Declared CONTROLS (green with the product in force; they pin the vigente
oracles instead of only not breaking them — plan §3 U1, PD-2, PD-15, and the
A-1 rule of plan §4: this RED ADDS cases, it REPLACES no oracle):
- PD-2: without `--object-kind` the form is `plan`, so a draft without the
  `plan-tasks` block is STILL rejected naming `plan-tasks` (the vigente
  oracle of `tests/test_004_003_t4_validation_fields.py`:427 is preserved) and
  a malformed `plan-tasks` block is STILL rejected.
- PD-15: the three vigente pairing/role guards (draft-plan with another
  substage; plan-review over an approved kind; draft-plan for a role other
  than the reviewer) stay green. They are ALSO pinned by the vigente
  regression files (004-003 T1/T2 reviewfix), which this RED does not touch.
  The fourth guard (the forge, extended to the new keys) is the new case and
  lives in the PD-1 and PD-4 cases of this same file.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from tests.product_staging import product_root
from tests.test_packet_prepare import (
    PACKET_CLI,
    PrepareProject,
    run_cli_bytes,
    run_prepare,
    tree_snapshot,
)
from tests.test_role_packet_render import parse_packet


# --- OWN fixtures (never the shared DRAFT_PLAN_RELPATH) --------------------

SPEC_RELPATH = "docs/drafts/006-006-u1-spec-draft.md"
PLAN_RELPATH = "docs/drafts/006-006-u1-plan-draft.md"
SPEC_VERSION = "spec-draft-001"
PLAN_VERSION = "plan-draft-001"

# A spec draft: it declares no `plan-tasks` block (a spec has no tasks).
SPEC_DRAFT_BYTES = (
    b"# 006-006 U1 - spec draft (fixture propia)\n\n"
    b"## 0. Intencion\n\n"
    b"El objeto revisado se declara en el contrato.\n\n"
    b"## 1. Postcondiciones\n\n"
    b"- PD-1: la forma del objeto se declara.\n"
    b"- PD-3: una spec se revisa sin tareas artificiales.\n"
)

# A plan draft: it carries a canonical `plan-tasks` block with the per-task
# validation plan the vigente rules demand (a code task and a code-less one).
_PLAN_TASKS = [
    {
        "id": "u1",
        "consume": [],
        "produce": [{"artifact": "contract-u1", "contract": "u1-v1"}],
        "depends_on": [],
        "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
        "focal_tests": ["tests/test_006_006_u1_draft_object_form.py"],
        "regressions": ["tests/test_004_003_t4_validation_fields.py"],
        "integration_gate": "make validate",
        "owner": "RED: test-writer; GREEN: implementer",
    },
    {
        "id": "u2",
        "consume": [{"artifact": "contract-u1", "producer": "u1", "contract": "u1-v1"}],
        "produce": [],
        "depends_on": ["u1"],
        "files": [],
        "observable_checks": ["el render nombra la forma declarada y la identidad del acompanante"],
        "regressions": [],
        "integration_gate": "make validate",
        "owner": "RED: test-writer; GREEN: implementer",
    },
]
PLAN_DRAFT_BYTES = (
    b"# 006-006 U1 - plan draft (fixture propia)\n\n```plan-tasks\n"
    + json.dumps({"tasks": _PLAN_TASKS}, indent=2, sort_keys=True).encode()
    + b"\n```\n"
)

# A malformed `plan-tasks` block: the block is there but its task declares no
# per-task validation plan (the shape the vigente rule rejects).
MALFORMED_PLAN_DRAFT_BYTES = (
    b"# 006-006 U1 - plan draft malformado (fixture propia)\n\n```plan-tasks\n"
    + json.dumps(
        {
            "tasks": [
                {
                    "id": "u1",
                    "consume": [],
                    "produce": [],
                    "depends_on": [],
                    "files": ["skills/cdad-cycle/scripts/cdad_packet.py"],
                }
            ]
        },
        indent=2,
        sort_keys=True,
    ).encode()
    + b"\n```\n"
)

MISSING_COMPANION_RELPATH = "docs/drafts/006-006-u1-absent-spec-draft.md"

# The byte shape of the two additive blocks with the new keys ABSENT (the
# HEAD of this revision). Built from this file's own fixture, so the digest
# is deterministic.
EXPECTED_CONTRACT_SECTION = (
    "\n- kind: draft-plan\n"
    f"- path: {PLAN_RELPATH}\n"
    f"- sha256: {hashlib.sha256(PLAN_DRAFT_BYTES).hexdigest()}\n"
    "- commit: null\n"
)
EXPECTED_INPUTS_SECTION = f"\n- {PLAN_RELPATH}: draft plan for review\n"

VIGENTE_CONTRACT_KEYS = {"kind", "path", "sha256", "commit", "plan_version"}


def packet_section(packet_text: str, name: str) -> str:
    """The exact bytes of a `## <name>` section of the rendered packet."""
    marker = f"## {name}"
    start = packet_text.find(marker)
    if start == -1:
        raise AssertionError(f"PACKET.md lacks a '{marker}' section")
    rest = packet_text[start + len(marker) :]
    nxt = rest.find("\n## ")
    return rest[:nxt] if nxt != -1 else rest


class ObjectFormCase(unittest.TestCase):
    def project(self, role: str = "reviewer", substage: str = "plan-review") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-006-006-u1-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), role, substage)
        # 010-004 T2 POST-AUDIT (PC-04/§4.1): el contexto canónico de la
        # preparación nueva (mismo documento, .cdad/executions/<id>/) se
        # materializa en la construcción para que los oráculos de árbol
        # existentes reflejen la convención migrada sin atribuírsela a
        # prepare.
        _ = project.execution_path
        return project

    @staticmethod
    def write_document(project: PrepareProject, relpath: str, data: bytes) -> None:
        target = project.root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def write_spec(self, project: PrepareProject) -> None:
        self.write_document(project, SPEC_RELPATH, SPEC_DRAFT_BYTES)

    def write_plan(self, project: PrepareProject) -> None:
        self.write_document(project, PLAN_RELPATH, PLAN_DRAFT_BYTES)

    def write_malformed_plan(self, project: PrepareProject) -> None:
        self.write_document(project, PLAN_RELPATH, MALFORMED_PLAN_DRAFT_BYTES)

    @staticmethod
    def draft_flags(path: str, version: str) -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            path,
            "--plan-version",
            version,
        )

    def prepare_ok(self, project: PrepareProject, *extra: str):
        result = run_prepare(PACKET_CLI, *project.args(*extra))
        self.assertEqual(
            result.returncode,
            0,
            "prepare failed: " + result.stderr.decode(errors="replace"),
        )
        return result

    def assert_rejected(
        self,
        project: PrepareProject,
        args: tuple[str, ...] | list[str],
        *,
        patterns: tuple[str, ...] = (),
        label: str = "case",
    ):
        """A rejection that publishes nothing (the `assert_rejected_without_
        publication` control of `tests/test_004_003_t4_validation_fields.py`:
        399-423) and that is a BEHAVIOURAL rejection, not a usage error."""
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *project.args(*args))
        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"{label}: expected a rejection: {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"{label}: stderr lacks 'ERROR: ...': {stderr!r}")
        self.assertNotIn(
            "unrecognized arguments",
            stderr,
            f"{label}: the CLI does not know the flag — a usage error is not a "
            f"behavioural rejection: {stderr!r}",
        )
        for pattern in patterns:
            self.assertRegex(
                stderr,
                pattern,
                f"{label}: the diagnostic does not name {pattern!r}: {stderr!r}",
            )
        self.assertEqual(result.stdout, b"", f"{label}: stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], f"{label}: out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, f"{label}: state changed")
        self.assertEqual(tree_snapshot(project.root), before, f"{label}: project tree changed")
        return result

    def request_of(self, project: PrepareProject) -> dict:
        path = project.out_dir / project.packet_id() / "REQUEST.json"
        self.assertTrue(path.is_file(), f"prepare did not write {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def packet_text(self, project: PrepareProject) -> str:
        path = project.out_dir / project.packet_id() / "PACKET.md"
        self.assertTrue(path.is_file(), f"prepare did not write {path}")
        return path.read_text(encoding="utf-8")


class TestPd1ObjectKindIsDeclaredInTheContract(ObjectFormCase):
    def test_pd1_object_kind_is_carried_in_the_request_and_in_the_packet_metadata(self) -> None:
        """PD-1: the declared form travels to the `REQUEST.json` contract AND to
        the packet metadata — `object_kind: spec` over a spec draft and
        `object_kind: plan` over a plan draft; the rest of the contract (kind,
        path, sha256, commit, plan_version) is unchanged."""
        for form, path, version, payload in (
            ("spec", SPEC_RELPATH, SPEC_VERSION, SPEC_DRAFT_BYTES),
            ("plan", PLAN_RELPATH, PLAN_VERSION, PLAN_DRAFT_BYTES),
        ):
            with self.subTest(object_kind=form):
                project = self.project()
                self.write_document(project, path, payload)
                self.prepare_ok(
                    project, *self.draft_flags(path, version), "--object-kind", form
                )

                request = self.request_of(project)
                self.assertEqual(
                    request["contract"].get("object_kind"),
                    form,
                    "the REQUEST.json contract does not carry the declared form: "
                    f"{request['contract']!r}",
                )
                metadata, _, _ = parse_packet(self.packet_text(project))
                self.assertEqual(
                    metadata["contract"].get("object_kind"),
                    form,
                    "the packet metadata does not carry the declared form: "
                    f"{metadata['contract']!r}",
                )
                self.assertEqual(
                    {k: v for k, v in request["contract"].items() if k != "object_kind"},
                    {
                        "kind": "draft-plan",
                        "path": path,
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "commit": None,
                        "plan_version": version,
                    },
                    "the declared form changed the rest of the contract",
                )

    def test_pd1_object_kind_outside_the_closed_set_is_rejected_naming_the_value(self) -> None:
        """PD-1 (R-3): a value outside the closed set {spec, plan} is rejected
        with a diagnostic that NAMES the offending value; nothing is published
        and the state is unchanged."""
        project = self.project()
        self.write_spec(project)
        self.assert_rejected(
            project,
            (*self.draft_flags(SPEC_RELPATH, SPEC_VERSION), "--object-kind", "borrador"),
            patterns=(r"borrador",),
            label="object_kind outside the closed set",
        )

    def test_pd1_the_contract_key_set_stays_closed(self) -> None:
        """PD-1 (R-1, declared CONTROL): the contract's key set stays closed —
        a request whose contract carries an unknown key is rejected. The
        extension is additive, so this case must stay green before and after
        the change."""
        project = self.project()
        self.write_plan(project)
        self.prepare_ok(project, *self.draft_flags(PLAN_RELPATH, PLAN_VERSION))
        request = self.request_of(project)
        request["contract"]["object_kind_typo"] = "spec"
        tampered = project.root / "tampered-request.json"
        tampered.write_text(json.dumps(request, indent=2), encoding="utf-8")
        common = [
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(tampered),
        ]
        rendered = run_cli_bytes(PACKET_CLI, "render", *common)
        self.assertNotEqual(
            rendered.returncode,
            0,
            "a request with an unknown contract key was rendered: "
            + rendered.stderr.decode(errors="replace"),
        )
        validated = run_cli_bytes(
            PACKET_CLI,
            "validate-packet",
            *common,
            "--packet",
            str(project.out_dir / project.packet_id() / "PACKET.md"),
        )
        self.assertNotEqual(
            validated.returncode,
            0,
            "a request with an unknown contract key was validated: "
            + validated.stderr.decode(errors="replace"),
        )

    def test_pd1_an_approved_kind_declaring_object_kind_is_rejected_before_publishing(self) -> None:
        """PD-1 (R-2, the forge) + PD-15 (guard 4, extended): an `approved-*`
        kind that declares `object_kind` is rejected BEFORE publishing anything
        — rc != 0 with the product's `ERROR:` diagnostic, empty stdout, no
        packet published and the state unchanged. The honest draft-plan
        surface passes first, so the rejection can only come from the forge
        guard and not from a missing feature."""
        control = self.project()
        self.write_spec(control)
        self.prepare_ok(
            control,
            *self.draft_flags(SPEC_RELPATH, SPEC_VERSION),
            "--object-kind",
            "spec",
        )

        project = self.project()
        self.write_spec(project)
        self.assert_rejected(
            project,
            (
                "--contract-kind",
                "approved-feature-spec",
                "--object-kind",
                "spec",
            ),
            label="approved-* declaring object_kind",
        )


class TestPd2ControlsWithoutTheNewKeys(ObjectFormCase):
    def test_pd2_without_object_kind_a_draft_without_plan_tasks_is_still_rejected(self) -> None:
        """PD-2 (declared CONTROL, the vigente oracle pinned): WITHOUT
        `--object-kind` the form is `plan` (fail-closed, R-4), so a draft
        without the `plan-tasks` block is STILL rejected with the vigente
        diagnostic that names `plan-tasks`; nothing is published and the state
        is unchanged. The oracle of `tests/test_004_003_t4_validation_fields.py`
        :427 is preserved — this case re-checks it with OWN fixtures, it does
        not replace it."""
        project = self.project()
        self.write_spec(project)
        self.assert_rejected(
            project,
            self.draft_flags(SPEC_RELPATH, SPEC_VERSION),
            patterns=(r"plan-tasks",),
            label="no --object-kind, no plan-tasks",
        )

    def test_pd2_without_object_kind_a_malformed_plan_tasks_block_is_still_rejected(self) -> None:
        """PD-2 (declared CONTROL): WITHOUT `--object-kind` a draft whose
        `plan-tasks` block is malformed (its task declares no per-task
        validation plan) is STILL rejected, naming the offending task and the
        missing field; nothing is published and the state is unchanged."""
        project = self.project()
        self.write_malformed_plan(project)
        self.assert_rejected(
            project,
            self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            patterns=(r"u1", r"focal_tests"),
            label="no --object-kind, malformed plan-tasks",
        )

    def test_pd2_the_render_without_the_new_keys_is_byte_identical_to_this_revision(self) -> None:
        """PD-2 + PD-5 + PD-16(a): WITHOUT the new keys the render is byte
        identical to the HEAD of this revision — the two blocks the spec
        declares additive (`## Contract` and `## Inputs`) keep their exact
        bytes, the contract carries no new key, and neither block mentions the
        form or the companion. The comparison is INTRA-revision (one product,
        one run): this RED asserts NOTHING between revisions (PD-16(b)/(c) are
        the declaration of U3 and the case of U6)."""
        project = self.project()
        self.write_plan(project)
        self.prepare_ok(project, *self.draft_flags(PLAN_RELPATH, PLAN_VERSION))

        text = self.packet_text(project)
        contract_section = packet_section(text, "Contract")
        inputs_section = packet_section(text, "Inputs")
        self.assertEqual(
            contract_section,
            EXPECTED_CONTRACT_SECTION,
            "the `## Contract` block changed without the new keys (it must only "
            "GROW when the contract declares something new, R-9)",
        )
        self.assertEqual(
            inputs_section,
            EXPECTED_INPUTS_SECTION,
            "the `## Inputs` block changed without the new keys (it must only "
            "GROW when the contract declares something new, R-9)",
        )
        self.assertNotIn(
            "form",
            contract_section,
            "the render names the form although the contract declares no form",
        )
        self.assertNotIn("spec_path", contract_section, "the render names a companion that was not declared")
        self.assertNotIn("spec_version", contract_section, "the render names a companion that was not declared")
        self.assertEqual(
            set(self.request_of(project)["contract"]),
            VIGENTE_CONTRACT_KEYS,
            "the contract carries a key it did not declare (the key set is closed)",
        )


class TestPd3TheSpecFormIsAccepted(ObjectFormCase):
    def test_pd3_a_spec_without_plan_tasks_is_accepted_with_object_kind_spec(self) -> None:
        """PD-3: with `--object-kind spec` a spec draft WITHOUT the `plan-tasks`
        block is accepted and publishes its package; the contract declares the
        form; the `REQUEST.json` carries NO `plan-tasks` token (no artificial
        tasks are injected) and the reviewed document is not modified."""
        project = self.project()
        self.write_spec(project)
        self.prepare_ok(
            project, *self.draft_flags(SPEC_RELPATH, SPEC_VERSION), "--object-kind", "spec"
        )

        packet_dir = project.out_dir / project.packet_id()
        self.assertTrue(
            (packet_dir / "PACKET.md").is_file(),
            "the spec draft published no packet",
        )
        request = self.request_of(project)
        self.assertEqual(request["contract"].get("object_kind"), "spec")
        self.assertNotIn(
            "plan-tasks",
            (packet_dir / "REQUEST.json").read_text(encoding="utf-8"),
            "the spec's request carries an artificial plan-tasks block",
        )
        self.assertEqual(
            (project.root / SPEC_RELPATH).read_bytes(),
            SPEC_DRAFT_BYTES,
            "the reviewed spec was modified (a plan-tasks block was injected)",
        )

    def test_pd3_the_same_bytes_declared_plan_are_rejected_by_the_plan_tasks_gate(self) -> None:
        """PD-3: the SAME bytes declared as `plan` are rejected — the plan
        checks apply to a `plan`-form document — with the diagnostic that
        names `plan-tasks`; nothing is published and the state is unchanged."""
        project = self.project()
        self.write_spec(project)
        self.assert_rejected(
            project,
            (*self.draft_flags(SPEC_RELPATH, SPEC_VERSION), "--object-kind", "plan"),
            patterns=(r"plan-tasks",),
            label="the same bytes declared plan",
        )


class TestPd4TheCompanionIsFixedByDigest(ObjectFormCase):
    def test_pd4_the_companion_identity_is_carried_in_the_contract(self) -> None:
        """PD-4: with the companion declared, the contract carries
        `spec_path`, `spec_sha256` (the digest of the file's bytes — the same
        value `sha256sum` prints) and `spec_version`, and the three keys
        appear TOGETHER (R-6: all or none)."""
        project = self.project()
        self.write_plan(project)
        self.write_spec(project)
        self.prepare_ok(
            project,
            *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            "--object-kind",
            "plan",
            "--spec-path",
            SPEC_RELPATH,
            "--spec-version",
            SPEC_VERSION,
        )

        contract = self.request_of(project)["contract"]
        self.assertEqual(
            contract.get("spec_path"), SPEC_RELPATH, "the contract does not carry the companion's path"
        )
        self.assertEqual(
            contract.get("spec_version"),
            SPEC_VERSION,
            "the contract does not carry the companion's version",
        )
        expected_digest = hashlib.sha256(SPEC_DRAFT_BYTES).hexdigest()
        self.assertEqual(
            contract.get("spec_sha256"),
            expected_digest,
            "the contract's companion digest is not the digest of the file's bytes",
        )
        if shutil.which("sha256sum"):
            printed = subprocess.run(
                ["sha256sum", str(project.root / SPEC_RELPATH)],
                capture_output=True,
                text=True,
                check=False,
            ).stdout.split()[0]
            self.assertEqual(
                contract.get("spec_sha256"),
                printed,
                "the contract's companion digest differs from `sha256sum` of the file",
            )
        for key in ("spec_path", "spec_sha256", "spec_version"):
            self.assertIn(
                key,
                contract,
                f"the companion's identity is incomplete (R-6: all or none): {contract!r}",
            )

    def test_pd4_a_missing_companion_file_is_rejected_naming_the_path(self) -> None:
        """PD-4: a companion that does not exist is rejected with a diagnostic
        that names the path; nothing is published and the state is unchanged."""
        project = self.project()
        self.write_plan(project)
        self.assert_rejected(
            project,
            (
                *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
                "--object-kind",
                "plan",
                "--spec-path",
                MISSING_COMPANION_RELPATH,
                "--spec-version",
                SPEC_VERSION,
            ),
            patterns=(re.escape(MISSING_COMPANION_RELPATH),),
            label="missing companion",
        )

    def test_pd4_the_companion_identity_is_all_or_none(self) -> None:
        """PD-4 (R-6): `spec_path` without `spec_version` (and the inverse) is
        rejected with a diagnostic that names the missing key; nothing is
        published and the state is unchanged."""
        cases = (
            ("--spec-path", SPEC_RELPATH, r"spec[-_]version", "spec_path without spec_version"),
            ("--spec-version", SPEC_VERSION, r"spec[-_]path", "spec_version without spec_path"),
        )
        for flag, value, missing, label in cases:
            with self.subTest(case=label):
                project = self.project()
                self.write_plan(project)
                self.write_spec(project)
                self.assert_rejected(
                    project,
                    (
                        *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
                        "--object-kind",
                        "plan",
                        flag,
                        value,
                    ),
                    patterns=(missing,),
                    label=label,
                )

    def test_pd4_a_companion_over_a_spec_principal_is_rejected(self) -> None:
        """PD-4 (R-7/R-8): the companion is the spec and only exists when the
        principal is the plan; a companion declared over a `spec`-form
        principal is rejected — nothing is published and the state is
        unchanged."""
        project = self.project()
        self.write_spec(project)
        self.assert_rejected(
            project,
            (
                *self.draft_flags(SPEC_RELPATH, SPEC_VERSION),
                "--object-kind",
                "spec",
                "--spec-path",
                SPEC_RELPATH,
                "--spec-version",
                SPEC_VERSION,
            ),
            label="companion over a spec principal",
        )

    def test_pd4_an_approved_kind_declaring_the_companion_is_rejected(self) -> None:
        """PD-4 (R-2, the forge) + PD-15 (guard 4, extended): an `approved-*`
        kind that declares the companion is rejected BEFORE publishing
        anything — rc != 0 with the product's `ERROR:` diagnostic, empty
        stdout, no packet published and the state unchanged."""
        project = self.project()
        self.write_plan(project)
        self.write_spec(project)
        self.assert_rejected(
            project,
            (
                "--contract-kind",
                "approved-feature-spec",
                "--spec-path",
                SPEC_RELPATH,
                "--spec-version",
                SPEC_VERSION,
            ),
            label="approved-* declaring the companion",
        )


class TestPd5ThePackageCarriesTheDocumentsAndTheirForm(ObjectFormCase):
    def test_pd5_inputs_carry_one_entry_per_fixed_document_in_order(self) -> None:
        """PD-5 (R-9): `inputs` carries ONE entry per fixed document, the
        principal first and the companion second, and each entry's `purpose`
        names the FORM of its document — "draft plan for review" for the plan
        and "draft spec for review" for the spec. A spec-only review carries
        the single spec entry."""
        project = self.project()
        self.write_plan(project)
        self.write_spec(project)
        self.prepare_ok(
            project,
            *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            "--object-kind",
            "plan",
            "--spec-path",
            SPEC_RELPATH,
            "--spec-version",
            SPEC_VERSION,
        )
        self.assertEqual(
            self.request_of(project)["inputs"],
            [
                {"path": PLAN_RELPATH, "purpose": "draft plan for review"},
                {"path": SPEC_RELPATH, "purpose": "draft spec for review"},
            ],
            "the inputs do not carry one entry per fixed document, in order, "
            "with the purpose that names each document's form",
        )

        spec_only = self.project()
        self.write_spec(spec_only)
        self.prepare_ok(
            spec_only,
            *self.draft_flags(SPEC_RELPATH, SPEC_VERSION),
            "--object-kind",
            "spec",
        )
        self.assertEqual(
            self.request_of(spec_only)["inputs"],
            [{"path": SPEC_RELPATH, "purpose": "draft spec for review"}],
            "the spec-only review does not carry the single spec entry",
        )

    def test_pd5_the_render_names_the_form_and_the_companion_identity(self) -> None:
        """PD-5 (R-9): the `## Contract` section of the render names the form
        (`- form: spec` | `- form: plan`) and, when there is a companion, its
        path, digest and version; the `## Inputs` section carries one line per
        document, in the same order."""
        project = self.project()
        self.write_plan(project)
        self.write_spec(project)
        self.prepare_ok(
            project,
            *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            "--object-kind",
            "plan",
            "--spec-path",
            SPEC_RELPATH,
            "--spec-version",
            SPEC_VERSION,
        )

        text = self.packet_text(project)
        contract_section = packet_section(text, "Contract")
        inputs_section = packet_section(text, "Inputs")
        self.assertRegex(
            contract_section,
            r"(?m)^\s*-\s*form:\s*plan\s*$",
            "the render does not name the declared form: " + contract_section,
        )
        self.assertIn(
            SPEC_RELPATH,
            contract_section,
            "the render does not name the companion's path: " + contract_section,
        )
        self.assertIn(
            hashlib.sha256(SPEC_DRAFT_BYTES).hexdigest(),
            contract_section,
            "the render does not name the companion's digest: " + contract_section,
        )
        self.assertIn(
            SPEC_VERSION,
            contract_section,
            "the render does not name the companion's version: " + contract_section,
        )
        self.assertEqual(
            inputs_section,
            f"\n- {PLAN_RELPATH}: draft plan for review\n- {SPEC_RELPATH}: draft spec for review\n",
            "the rendered inputs do not carry one line per document, in order: "
            + inputs_section,
        )

        spec_only = self.project()
        self.write_spec(spec_only)
        self.prepare_ok(
            spec_only,
            *self.draft_flags(SPEC_RELPATH, SPEC_VERSION),
            "--object-kind",
            "spec",
        )
        spec_contract_section = packet_section(self.packet_text(spec_only), "Contract")
        self.assertRegex(
            spec_contract_section,
            r"(?m)^\s*-\s*form:\s*spec\s*$",
            "the render does not name the declared form: " + spec_contract_section,
        )

    def test_pd5_the_published_package_carrying_the_new_keys_is_valid(self) -> None:
        """PD-5: the package that carries the new contract keys is a VALID
        package — `validate-packet` accepts the published packet and the
        metadata carries the full contract (the new keys included)."""
        project = self.project()
        self.write_plan(project)
        self.write_spec(project)
        self.prepare_ok(
            project,
            *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            "--object-kind",
            "plan",
            "--spec-path",
            SPEC_RELPATH,
            "--spec-version",
            SPEC_VERSION,
        )

        packet_dir = project.out_dir / project.packet_id()
        common = [
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(packet_dir / "REQUEST.json"),
        ]
        validated = run_cli_bytes(
            PACKET_CLI, "validate-packet", *common, "--packet", str(packet_dir / "PACKET.md")
        )
        self.assertEqual(
            validated.returncode,
            0,
            "the package carrying the new contract keys is not valid: "
            + validated.stderr.decode(errors="replace"),
        )
        metadata, _, _ = parse_packet(self.packet_text(project))
        self.assertEqual(metadata["contract"].get("object_kind"), "plan")
        self.assertEqual(metadata["contract"].get("spec_path"), SPEC_RELPATH)


class TestPd15TheVigenteGuardsStayGreen(ObjectFormCase):
    """PD-15: the vigente pairing/role guards stay green (declared CONTROLS).
    The fourth guard — the forge, extended to the new keys — is the new case
    and lives in the PD-1 and PD-4 cases of this same file (an `approved-*`
    kind declaring `object_kind` / the companion is rejected before
    publishing). The same three guards are ALSO pinned by the vigente
    regression files `tests/test_004_003_t1_reviewfix.py` (F1) and
    `tests/test_004_003_t2_reviewfix.py` (B1, B2), which this RED does not
    touch."""

    def test_pd15_draft_plan_with_another_substage_is_rejected(self) -> None:
        """PD-15 (guard 1, declared CONTROL): a `draft-plan` contract with a
        substage other than `plan-review` is still rejected; nothing is
        published and the state is unchanged."""
        project = self.project("reviewer", "review")
        self.write_plan(project)
        self.assert_rejected(
            project,
            self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            label="draft-plan with another substage",
        )

    def test_pd15_plan_review_over_an_approved_kind_is_rejected(self) -> None:
        """PD-15 (guard 2, declared CONTROL): the `plan-review` subphase over an
        approved contract is still rejected; nothing is published and the
        state is unchanged."""
        project = self.project()
        self.assert_rejected(
            project,
            (),
            label="plan-review over an approved kind",
        )

    def test_pd15_draft_plan_for_a_role_other_than_the_reviewer_is_rejected(self) -> None:
        """PD-15 (guard 3, declared CONTROL): a `draft-plan` contract for a role
        other than the reviewer is still rejected; nothing is published and the
        state is unchanged."""
        project = self.project("implementer", "green")
        self.write_plan(project)
        self.assert_rejected(
            project,
            self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
            label="draft-plan for a non-reviewer role",
        )


class InstalledProductCase(ObjectFormCase):
    """One isolated install (CDAD_INSTALL_ROOT, no extra skill dirs), P5 pattern."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-006-006-u1-install-")
        cls.install_root = Path(cls._install_tmp.name).resolve()
        env = os.environ.copy()
        env["CDAD_INSTALL_ROOT"] = str(cls.install_root)
        env["CDAD_SKILL_EXTRA_DIRS"] = ""
        cls.install_result = subprocess.run(
            ["bash", str(cls.install_product / "install.sh"), "--basic"],
            cwd=cls.install_product,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        cls.installed_cli = cls.install_root / ".claude/skills/cdad-cycle/scripts/cdad_packet.py"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._install_tmp.cleanup()

    def setUp(self) -> None:
        self.assertEqual(
            self.install_result.returncode,
            0,
            self.install_result.stderr or self.install_result.stdout,
        )

    def test_pd5_the_installed_product_renders_the_declared_form_like_the_repo(self) -> None:
        """PD-5 + V-1 (the U1 gate): the INSTALLED product renders the package
        with the declared form, byte for byte like the repo CLI (the pattern
        of `tests/test_004_003_t2_plan_review.py`:290)."""
        outcomes: dict[str, tuple] = {}
        for label, cli in (("repo", PACKET_CLI), ("installed", self.installed_cli)):
            project = self.project()
            self.write_plan(project)
            self.write_spec(project)
            result = run_prepare(
                cli,
                *project.args(
                    *self.draft_flags(PLAN_RELPATH, PLAN_VERSION),
                    "--object-kind",
                    "plan",
                    "--spec-path",
                    SPEC_RELPATH,
                    "--spec-version",
                    SPEC_VERSION,
                ),
                cwd=project.root,
            )
            packet_dir = project.out_dir / project.packet_id()
            request_bytes = (
                (packet_dir / "REQUEST.json").read_bytes()
                if (packet_dir / "REQUEST.json").is_file()
                else None
            )
            packet_bytes = (
                (packet_dir / "PACKET.md").read_bytes()
                if (packet_dir / "PACKET.md").is_file()
                else None
            )
            outcomes[label] = (
                result.returncode,
                result.stdout,
                result.stderr,
                request_bytes,
                packet_bytes,
            )

        repo, installed = outcomes["repo"], outcomes["installed"]
        self.assertEqual(repo[0], 0, "repo control: " + repo[2].decode(errors="replace"))
        self.assertEqual(
            installed[0],
            0,
            "the installed product cannot render the package with the declared "
            "form: " + installed[2].decode(errors="replace"),
        )
        self.assertEqual(installed[1], repo[1], "installed stdout differs from repo stdout")
        self.assertEqual(installed[3], repo[3], "REQUEST.json differs between installed and repo")
        self.assertEqual(installed[4], repo[4], "PACKET.md differs between installed and repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
