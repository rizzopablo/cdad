#!/usr/bin/env python3
"""RED review-fix T2 for 004-003 — blocking findings B1 and B2 of
review-t2.md: the `draft-plan` ⇔ `plan-review` pairing is enforced in BOTH
directions for the reviewer role.

Contract: docs/specs/004-003-planning-procedures/spec.md (PD-2: the reviewer's
plan-review subphase reviews the draft plan object; acceptance criterion 1:
negatives verify that no packet is produced for an unsupported contract) +
docs/specs/004-003-planning-procedures/review-t2.md (remedies B1/B2:
"pairing bidireccional en un solo lugar (`draft-plan` ⇔ `plan-review` para el
rol reviewer); cubrir ambas direcciones con negativos"). B3
(`packets/roles/reviewer.md` reconciliation, G4) is NOT tested here as a
phrase: it is verified by review.

Black-box: the CLI is invoked as a subprocess; implementation sources are
never read. Every project is a temporary fixture; the real HOME and the
repository state are never touched.

Oracle decisions (interfaces defined by this RED, from the review remedies):
- B1: a `draft-plan` contract is admissible ONLY with the `plan-review`
  subphase. `reviewer/review` + draft-plan (the reproduced escape: Sonda A)
  is rejected: rc != 0 with an ERROR diagnostic, empty stdout, no packet
  published and unchanged state.
- B2: the `plan-review` subphase is admissible ONLY with a `draft-plan`
  contract. `reviewer/plan-review` over the default derived
  `approved-feature-spec` contract (the reproduced misroute: Sonda B) is
  rejected with the same no-publication guarantees.
- The honest control (reviewer/plan-review + draft-plan) succeeds in both
  tests first, so any rejection is pairing-based and not flag- or
  feature-based.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
    DRAFT_PLAN_WITH_TASKS,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare, tree_snapshot


class ReviewFixCase(unittest.TestCase):
    def project(self, role: str = "reviewer", substage: str = "plan-review") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t2-rfix-")
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


class TestB1DraftPlanRequiresPlanReviewSubphase(ReviewFixCase):
    def test_b1_draft_plan_contract_rejected_outside_plan_review(self) -> None:
        """B1 (PD-2 + acceptance criterion 1): a draft-plan contract is
        admissible only with the plan-review subphase. The honest control
        (reviewer/plan-review + draft-plan) is accepted first, so a rejection
        can only come from the subphase pairing and not from a missing or
        broken draft surface. Then the reproduced escape — reviewer/review +
        draft-plan (Sonda A) — is rejected: rc != 0, ERROR diagnostic, empty
        stdout, no packet published, unchanged state."""
        control = self.project("reviewer", "plan-review")
        self.write_draft_plan(control)
        result = run_prepare(PACKET_CLI, *control.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "honest draft-plan/plan-review surface missing (T2 control): "
            + result.stderr.decode(errors="replace"),
        )

        project = self.project("reviewer", "review")
        self.write_draft_plan(project)
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()

        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"draft-plan contract accepted by the review subphase "
            f"(B1 escape of PD-2): {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr lacks 'ERROR: ...': {stderr!r}")
        self.assertEqual(result.stdout, b"", "stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, "state changed")
        self.assertEqual(tree_snapshot(project.root), before, "project tree changed")


class TestB2PlanReviewRequiresDraftPlanContract(ReviewFixCase):
    def test_b2_plan_review_subphase_rejected_over_approved_contract(self) -> None:
        """B2 (PD-2 + acceptance criterion 1: "no se produce un paquete para
        un contrato no soportado"): the plan-review subphase is admissible
        only with a draft-plan contract. The honest control
        (reviewer/plan-review + draft-plan) is accepted first. Then the
        reproduced misroute — reviewer/plan-review with the default derived
        approved-feature-spec contract (Sonda B, no draft flags) — is
        rejected: rc != 0, ERROR diagnostic, empty stdout, no packet
        published, unchanged state."""
        control = self.project("reviewer", "plan-review")
        self.write_draft_plan(control)
        result = run_prepare(PACKET_CLI, *control.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "honest draft-plan/plan-review surface missing (T2 control): "
            + result.stderr.decode(errors="replace"),
        )

        project = self.project("reviewer", "plan-review")
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()

        # No draft flags: prepare derives the default approved-feature-spec
        # contract for the fixture's spec path (the reproduced misroute).
        result = run_prepare(PACKET_CLI, *project.args())
        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"plan-review subphase accepted over an approved contract "
            f"(B2 misroute): {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr lacks 'ERROR: ...': {stderr!r}")
        self.assertEqual(result.stdout, b"", "stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, "state changed")
        self.assertEqual(tree_snapshot(project.root), before, "project tree changed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
