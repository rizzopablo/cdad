#!/usr/bin/env python3
"""RED tests for 004-003 T2 (PD-2/PD-3/PD-4/PD-9): the reviewer gains the
`plan-review` subphase and its packet carries intention + restrictions + the
plan object (not only the spec); invocable from the installed product without
reading the source repository.

Contract: docs/specs/004-003-planning-procedures/spec.md (PD-2, PD-3, PD-4,
PD-9; §2 surface "Paquete de revisión de plan") + plan.md T2
("`ROLE_SUBSTAGES[reviewer]` gana `plan-review`; nuevo
`packets/substages/reviewer-plan-review.md`; el paquete del reviewer lleva
intención+restricciones+plan (no solo la spec); RED: un producto instalado
renderiza un paquete de revisión de plan sin leer el repo fuente").
Black-box: the CLI is invoked as a subprocess; implementation sources are
never read. Every project is a temporary fixture; the real HOME and the
repository state are never touched.

Oracle decisions (interfaces defined by this RED, derived from the spec):
- The pair (reviewer, plan-review) becomes a valid prepare pair; the request
  and the state binding record substage "plan-review" and role "reviewer".
- The plan-review packet's independent composition oracle (instruction_sources,
  the frozen 003-001 convention of common.md + roles/<role>.md +
  substages/<role>-<substage>.md) is exactly common.md + roles/reviewer.md +
  substages/reviewer-plan-review.md — the plan-review procedure itself,
  byte-for-byte sha-pinned — and never the plain review substage.
- "Intención + restricciones + plan (no solo la spec)": the packet carries the
  draft plan object itself — the contract is the draft plan (kind
  `draft-plan` with its declared version, the T1 surface) and the packet's
  inputs include the draft path; the declared objective carries the original
  intention; the substage source (pinned byte-for-byte) carries the
  restrictions/procedure.
- PD-3 (revisar ≠ aprobar): the plan-review emission carries no approval
  marking: the contract kind stays `draft-plan` (never `approved-*`) and the
  draft input's purpose is non-empty with no approval wording.
- PD-9 (encargo suficiente): the plan-review request declares a useful
  objective, contract + version, pertinent inputs, scopes, expected output
  and evidence; the autonomous decisions / validation strategy / return
  triggers are carried by the pinned substage source.
- PD-4 (instalado): an installed product (isolated CDAD_INSTALL_ROOT, no
  extra skill dirs) renders the plan-review packet for a consumer project
  that carries no CDAD product sources (no skills/, scripts/, .claude/),
  byte-identical to the repo CLI's render.
- Procedural facets not unit-testable black-box (a session distinct from the
  author; confidence ≥80% and the verdict-tuple) are carried by the substage
  source that the composition oracle pins; they are exercised end-to-end by
  T7 and audited procedurally.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.product_staging import product_root
from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
    DRAFT_PLAN_WITH_TASKS,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare, tree_snapshot
from tests.test_role_packet_render import (
    PACKETS_ROOT,
    PACKET_BEGIN,
    parse_packet,
    static_instruction_bytes,
)

APPROVAL_MARKING = re.compile(r"(?i)approv")
OBJECTIVE = "Review the plan draft: intention + restrictions + plan"
PLAN_REVIEW_SOURCE = "substages/reviewer-plan-review.md"


class PlanReviewCase(unittest.TestCase):
    def project(self, role: str = "reviewer", substage: str = "plan-review") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t2-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), role, substage)

    def write_draft_plan(self, project: PrepareProject) -> None:
        draft = project.root / DRAFT_PLAN_RELPATH
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(DRAFT_PLAN_WITH_TASKS)

    def draft_flags(self) -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )

    def prepare_ok(self, project: PrepareProject, *extra: str, objective: str = OBJECTIVE):
        result = run_prepare(PACKET_CLI, *project.args(*extra, objective=objective))
        self.assertEqual(
            result.returncode,
            0,
            "prepare failed: " + result.stderr.decode(errors="replace"),
        )
        return result


class TestPd2PlanReviewSubphaseCarriesThePlan(PlanReviewCase):
    def test_pd2_plan_review_packet_carries_plan_not_only_the_spec(self) -> None:
        """PD-2: the reviewer's plan-review pair is valid; its packet is
        composed of the plan-review procedure (instruction_sources = common +
        roles/reviewer + substages/reviewer-plan-review, sha-pinned
        byte-for-byte, and not the plain review substage) and carries the
        draft plan object itself (contract kind `draft-plan` with the
        declared version; inputs include the draft path); the declared
        objective carries the original intention."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(project, *self.draft_flags())

        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(request["role"], "reviewer")
        self.assertEqual(request["substage"], "plan-review")
        self.assertEqual(request["contract"]["kind"], "draft-plan")
        self.assertEqual(request["contract"]["plan_version"], DRAFT_PLAN_VERSION)
        self.assertIn(
            DRAFT_PLAN_RELPATH,
            [item.get("path") for item in request.get("inputs") or []],
            "the plan-review packet does not carry the plan object (spec only)",
        )

        packet_text = (packet_dir / "PACKET.md").read_text(encoding="utf-8")
        metadata, _, body = parse_packet(packet_text)
        self.assertEqual(metadata["substage"], "plan-review")
        self.assertEqual(metadata["contract"]["kind"], "draft-plan")
        self.assertEqual(metadata["contract"]["plan_version"], DRAFT_PLAN_VERSION)

        # Independent composition oracle: the plan-review procedure itself,
        # byte-for-byte (the frozen 003-001 convention: exactly three sources).
        plan_review_path = PACKETS_ROOT / PLAN_REVIEW_SOURCE
        self.assertTrue(
            plan_review_path.is_file(),
            f"plan-review substage source missing: {PLAN_REVIEW_SOURCE}",
        )
        source_paths = ["common.md", "roles/reviewer.md", PLAN_REVIEW_SOURCE]
        expected_sources = [
            {"path": path, "sha256": hashlib.sha256((PACKETS_ROOT / path).read_bytes()).hexdigest()}
            for path in source_paths
        ]
        self.assertEqual(metadata["instruction_sources"], expected_sources)
        expected_static = b"\n".join((PACKETS_ROOT / path).read_bytes() for path in source_paths)
        self.assertEqual(static_instruction_bytes(packet_text), expected_static)
        self.assertNotIn(
            "substages/reviewer-review.md",
            [source["path"] for source in metadata["instruction_sources"]],
            "the plan-review packet composes the plain review substage",
        )

        # The rendered packet carries the plan object and the declared intention.
        self.assertIn(DRAFT_PLAN_RELPATH, body)
        self.assertIn(OBJECTIVE, body)

        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["active_packet"]["substage"], "plan-review")
        self.assertEqual(state["active_packet"]["contract_kind"], "draft-plan")


class TestPd3PlanReviewDoesNotApprove(PlanReviewCase):
    def test_pd3_plan_review_emission_carries_no_approval_marking(self) -> None:
        """PD-3 (revisar ≠ aprobar): the plan-review emission keeps the
        reviewed object a draft: the contract kind is not `approved-*` and
        the draft input's purpose is non-empty with no approval wording."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(project, *self.draft_flags())

        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertFalse(
            request["contract"]["kind"].startswith("approved-"),
            "the plan-review emission approves the plan (approved-* kind)",
        )
        entries = [
            item for item in request.get("inputs") or [] if item.get("path") == DRAFT_PLAN_RELPATH
        ]
        self.assertTrue(entries, f"REQUEST.json lacks a draft inputs entry: {request.get('inputs')!r}")
        purpose = entries[0].get("purpose")
        self.assertIsInstance(purpose, str, f"input purpose is not a string: {purpose!r}")
        self.assertTrue(purpose.strip(), f"input purpose is empty: {purpose!r}")
        self.assertNotRegex(
            purpose,
            APPROVAL_MARKING,
            f"plan-review emission carries an approval marking: {purpose!r}",
        )


class TestPd4PlanReviewIsTheReviewerProcedure(PlanReviewCase):
    def test_pd4_plan_review_runs_on_the_reviewer_role_only(self) -> None:
        """PD-4 (es procedimiento, no un agente nuevo): the plan-review
        packet is dispatched to the existing reviewer role, and the pair is
        not offered to other roles (probe: test-writer/red) — no new agent,
        no generic substage."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(project, *self.draft_flags())
        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(request["role"], "reviewer")

        other = self.project("test-writer", "plan-review")
        before = tree_snapshot(other.root)
        state_before = other.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *other.args(objective=OBJECTIVE))
        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"plan-review pair offered to test-writer (generic substage): {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr lacks 'ERROR: ...': {stderr!r}")
        self.assertEqual(result.stdout, b"", "stdout must be empty")
        self.assertEqual(list(other.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertEqual(other.state_path.read_bytes(), state_before, "state changed")
        self.assertEqual(tree_snapshot(other.root), before, "project tree changed")


class TestPd9PlanReviewPacketIsASufficientEncargo(PlanReviewCase):
    def test_pd9_plan_review_request_declares_the_full_encargo(self) -> None:
        """PD-9: the plan-review request declares a useful objective, the
        contract + version, pertinent inputs, scopes, expected output and
        evidence (the remaining encargo facets — autonomous decisions,
        validation strategy, return triggers — live in the pinned substage
        source; full logs stay out of the packet)."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(project, *self.draft_flags())

        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(request["objective"], OBJECTIVE, "the encargo lacks its declared objective")
        self.assertEqual(request["contract"]["plan_version"], DRAFT_PLAN_VERSION, "contract lacks its version")
        self.assertTrue(request["inputs"], "the encargo has no pertinent inputs")
        self.assertIn(
            DRAFT_PLAN_RELPATH, [item.get("path") for item in request["inputs"]],
            "the encargo's pertinent inputs lack the plan object",
        )
        self.assertIsInstance(request["read_scope"], list, "no read scope")
        self.assertIsInstance(request["write_scope"], list, "no write scope")
        self.assertTrue(str(request["expected_output"]).strip(), "no expected output")
        self.assertTrue(request["evidence_required"], "no evidence required")


class InstalledProductCase(PlanReviewCase):
    """One isolated install (CDAD_INSTALL_ROOT, no extra skill dirs), P5 pattern."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.install_product = product_root()
        cls._install_tmp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t2-install-")
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


class TestPd4InstalledProductRendersPlanReview(InstalledProductCase):
    def test_pd4_installed_product_renders_plan_review_without_source_repo(self) -> None:
        """PD-4: an installed product renders the plan-review packet for a
        consumer project that carries no CDAD product sources (nothing to
        read from a source repository), byte-identical to the repo CLI's
        render of the same fixture."""
        outcomes: dict[str, tuple] = {}
        for label, cli in (("repo", PACKET_CLI), ("installed", self.installed_cli)):
            temp = tempfile.TemporaryDirectory(prefix=f"cdad-004-003-t2-{label}-")
            self.addCleanup(temp.cleanup)
            project = PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")
            self.write_draft_plan(project)
            # The consumer carries no CDAD product sources to read.
            for foreign in ("skills", "scripts", "sources", "agents", "build", ".claude"):
                self.assertFalse(
                    (project.root / foreign).exists(),
                    f"fixture polluted with product sources ({foreign}/)",
                )
            result = run_prepare(
                cli,
                *project.args(*self.draft_flags(), objective=OBJECTIVE),
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
            outcomes[label] = (result.returncode, result.stdout, result.stderr, request_bytes, packet_bytes)

        repo, installed = outcomes["repo"], outcomes["installed"]
        self.assertEqual(repo[0], 0, "repo control: " + repo[2].decode(errors="replace"))
        self.assertTrue(repo[1].startswith(PACKET_BEGIN.encode()))
        self.assertEqual(
            installed[0],
            0,
            "the installed product cannot render the plan-review packet: "
            + installed[2].decode(errors="replace"),
        )

        installed_packet = (installed[4] or b"").decode(errors="replace")
        metadata, _, body = parse_packet(installed_packet)
        self.assertEqual(metadata["contract"]["kind"], "draft-plan")
        self.assertEqual(metadata["substage"], "plan-review")
        self.assertIn(
            PLAN_REVIEW_SOURCE,
            [source["path"] for source in metadata["instruction_sources"]],
            "the installed plan-review packet does not compose the plan-review procedure",
        )
        self.assertIn(DRAFT_PLAN_RELPATH, body)

        self.assertEqual(installed[1], repo[1], "installed stdout differs from repo stdout")
        self.assertEqual(installed[3], repo[3], "REQUEST.json differs between installed and repo")
        self.assertEqual(installed[4], repo[4], "PACKET.md differs between installed and repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
