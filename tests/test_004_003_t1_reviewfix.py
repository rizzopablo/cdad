#!/usr/bin/env python3
"""RED review-fix T1 for 004-003 — findings F1 and F2 of review-t1.md.

Contract: docs/specs/004-003-planning-procedures/spec.md (PD-1; §3 invariant
4: "la revisión de plan **no** concede permiso de implementación") +
docs/specs/004-003-planning-procedures/review-t1.md (remedios estructurales
F1/F2 del reviewer). Black-box: the CLI is invoked as a subprocess;
implementation sources are never read. Every project is a temporary fixture;
the real HOME and the repository state are never touched.

Oracle decisions (interfaces defined by this RED, from the review remedies):
- F1: the `draft-plan` surface (`--contract-kind draft-plan` /
  `--contract-path` / `--plan-version`) is restricted to the reviewer role:
  prepare for any other role (the reproduced defect probes
  `implementer/green`; `test-writer/red` pins the "reviewer only" rule) is
  rejected rc != 0 with an ERROR diagnostic, empty stdout, no packet
  published and unchanged state. The reviewer probe is the honest control:
  it succeeds, so any rejection is role-based, not flag-based.
- F2: the emission of a draft-plan contract carries NO approval marking: the
  `purpose` of the draft's inputs entry in REQUEST.json is non-empty, is not
  "approved contract" and contains no approval wording; the rendered
  PACKET.md Inputs line for the draft path carries that same non-approving
  purpose.
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
    DRAFT_PLAN_WITH_TASKS,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare, tree_snapshot

APPROVAL_MARKING = re.compile(r"(?i)approv")


class ReviewFixCase(unittest.TestCase):
    def project(self, role: str = "reviewer", substage: str = "plan-review") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t1-rfix-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), role, substage)
        # 010-004 T2 POST-AUDIT (PC-04/§4.1): contexto canónico materializado
        # en la construcción (ver ObjectFormCase.project para la convención).
        _ = project.execution_path
        return project

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

    def prepare_ok(self, project: PrepareProject, *extra: str):
        result = run_prepare(PACKET_CLI, *project.args(*extra))
        self.assertEqual(
            result.returncode,
            0,
            "prepare failed: " + result.stderr.decode(errors="replace"),
        )
        return result


class TestF1DraftPlanIsReviewerOnly(ReviewFixCase):
    def test_f1_draft_plan_contract_rejected_for_non_reviewer_roles(self) -> None:
        """F1 (PD-1 + §3 invariant 4): a draft-plan contract binds to the
        reviewer only. prepare for a non-reviewer role (implementer/green —
        the gate bypass reproduced by the reviewer — and test-writer/red) is
        rejected: rc != 0, ERROR diagnostic, empty stdout, no packet
        published, unchanged state. The reviewer probe succeeds first, so a
        rejection can only come from the role restriction and not from a
        missing feature."""
        reviewer = self.project("reviewer", "plan-review")
        self.write_draft_plan(reviewer)
        self.prepare_ok(reviewer, *self.draft_flags())

        for role, substage in (("implementer", "green"), ("test-writer", "red")):
            with self.subTest(role=role, substage=substage):
                project = self.project(role, substage)
                self.write_draft_plan(project)
                before = tree_snapshot(project.root)
                state_before = project.state_path.read_bytes()

                result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
                stderr = result.stderr.decode(errors="replace")

                self.assertNotEqual(
                    result.returncode,
                    0,
                    f"draft-plan contract dispatched to {role}/{substage} "
                    f"(approval-gate bypass): {stderr!r}",
                )
                self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr lacks 'ERROR: ...': {stderr!r}")
                self.assertEqual(result.stdout, b"", "stdout must be empty")
                self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
                self.assertEqual(project.state_path.read_bytes(), state_before, "state changed")
                self.assertEqual(tree_snapshot(project.root), before, "project tree changed")


class TestF2DraftEmissionCarriesNoApprovalMarking(ReviewFixCase):
    def test_f2_draft_plan_input_purpose_is_not_an_approval(self) -> None:
        """F2 (PD-1: "la emisión lleva el sha/versión del borrador, no una
        aprobación"): the emitted draft-plan packet must not mark the draft
        input as an approval. The `purpose` of the draft path's inputs entry
        in REQUEST.json is non-empty, is not "approved contract" and carries
        no approval wording; the rendered PACKET.md Inputs line for the draft
        path carries that same non-approving purpose."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(project, *self.draft_flags())

        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        entries = [
            item for item in request.get("inputs") or [] if item.get("path") == DRAFT_PLAN_RELPATH
        ]
        self.assertTrue(
            entries,
            f"REQUEST.json lacks an inputs entry for {DRAFT_PLAN_RELPATH}: "
            f"{request.get('inputs')!r}",
        )
        purpose = entries[0].get("purpose")
        self.assertIsInstance(purpose, str, f"input purpose is not a string: {purpose!r}")
        self.assertTrue(purpose.strip(), f"input purpose is empty: {purpose!r}")
        self.assertNotEqual(
            purpose,
            "approved contract",
            f"draft-plan emission carries an approval marking: {purpose!r}",
        )
        self.assertNotRegex(
            purpose,
            APPROVAL_MARKING,
            f"draft-plan emission carries an approval marking: {purpose!r}",
        )

        packet_text = (packet_dir / "PACKET.md").read_text(encoding="utf-8")
        block = self._inputs_block(packet_text)
        lines = [
            line for line in block.splitlines() if line.startswith(f"- {DRAFT_PLAN_RELPATH}:")
        ]
        self.assertTrue(lines, f"PACKET.md Inputs lacks the draft path line: {block!r}")
        rendered_purpose = lines[0][len(f"- {DRAFT_PLAN_RELPATH}:") :].strip()
        self.assertEqual(
            rendered_purpose,
            purpose,
            f"PACKET.md Inputs purpose {rendered_purpose!r} != REQUEST.json purpose {purpose!r}",
        )
        self.assertNotRegex(
            rendered_purpose,
            APPROVAL_MARKING,
            f"rendered draft-plan emission carries an approval marking: {rendered_purpose!r}",
        )

    @staticmethod
    def _inputs_block(packet_text: str) -> str:
        marker = "## Inputs"
        start = packet_text.find(marker)
        assert start != -1, "PACKET.md lacks an '## Inputs' section"
        rest = packet_text[start + len(marker) :]
        nxt = rest.find("\n## ")
        return rest[:nxt] if nxt != -1 else rest


if __name__ == "__main__":
    unittest.main(verbosity=2)
