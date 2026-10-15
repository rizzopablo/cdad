#!/usr/bin/env python3
"""RED tests for 004-003 T1 (PD-1): the draft-plan contract kind is first
class and does not approve.

Contract: docs/specs/004-003-planning-procedures/spec.md (PD-1, §2 surface
"Contract-kind para un objeto borrador"). Black-box: the CLI is invoked as a
subprocess; implementation sources are never read. Every project is a
temporary fixture; the real HOME and the repository state are never touched.

Oracle decisions (interfaces defined by this RED, derived from the spec):
- The request contract object gains an optional `plan_version` field: the
  DECLARED plan version of a draft plan object ("una versión de plan
  declarada").
- `draft-plan` is a valid contract kind (D1): contract
  {kind: "draft-plan", path, sha256, commit, plan_version}; the emission
  carries the draft's sha/version and never an approval marking; the
  authority reference of the review is the execution binding's
  `authority_ref` ("quién pidió la revisión").
- Forgery: an `approved-*` kind declared together with a declared
  `plan_version` (i.e. over a draft object) is detected and rejected:
  rc != 0 with an ERROR diagnostic and no publication (no packet directory,
  unchanged state, empty stdout).
- `prepare` accepts the draft contract explicitly via
  `--contract-kind draft-plan --contract-path <relpath> --plan-version
  <version>`; without these flags the role default derivation is unchanged.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tests.test_packet_prepare import (
    PACKET_CLI,
    PrepareProject,
    run_cli_bytes,
    run_prepare,
    tree_snapshot,
)
from tests.test_role_packet_render import PACKET_BEGIN, parse_packet
from tests.test_role_packets import AUTHORITY_REF


DRAFT_PLAN_RELPATH = "docs/planning-contract-draft.md"
DRAFT_PLAN_VERSION = "draft-001"
DRAFT_PLAN_BYTES = b"# Plan draft fixture\n\nEstado: borrador para revision\n"

# PD-8 fixture migration (consecuencia de PD-8/T4 — packet
# 004-003-planning-procedures-test-writer-red-008): the draft plan fixtures
# must keep being VALID plans once T4 makes the plan-tasks block mandatory,
# so every write of the draft carries a canonical ```plan-tasks block
# declaring the per-task validation fields PD-8 demands (focal_tests /
# observable_checks, regressions, integration_gate, owner) and satisfying
# the T3 structural checks (no input without producer, no cycles, matched
# contracts, disjoint files). DRAFT_PLAN_BYTES itself is NOT extended: T4
# builds its own blocks on that base and owns the no-block defect fixture.
_PLAN_TASKS_BLOCK_OPEN = b"```plan-tasks\n"
_PLAN_TASKS_BLOCK_CLOSE = b"```"
_DRAFT_PLAN_TASKS = [
    {
        "id": "t1",
        "consume": [],
        "produce": [{"artifact": "contract-a", "contract": "a-v1"}],
        "depends_on": [],
        "parallel": [],
        "files": ["tests/only_t1.py"],
        "focal_tests": ["tests/test_004_003_t1_draft_contract.py"],
        "regressions": [],
        "integration_gate": "suite completa una vez por GREEN",
        "owner": "RED: test-writer; GREEN: implementer",
    },
    {
        "id": "t2",
        "consume": [{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        "produce": [],
        "depends_on": ["t1"],
        "parallel": [],
        "files": ["tests/only_t2.py"],
        "focal_tests": ["tests/test_004_003_t1_draft_contract.py"],
        "regressions": [],
        "integration_gate": "suite completa una vez por GREEN",
        "owner": "RED: test-writer; GREEN: implementer",
    },
]
DRAFT_PLAN_WITH_TASKS = (
    DRAFT_PLAN_BYTES
    + _PLAN_TASKS_BLOCK_OPEN
    + json.dumps({"tasks": _DRAFT_PLAN_TASKS}, indent=2, sort_keys=True).encode()
    + b"\n"
    + _PLAN_TASKS_BLOCK_CLOSE
)


class DraftContractTestCase(unittest.TestCase):
    def project(self, role: str = "reviewer", substage: str = "plan-review") -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t1-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), role, substage)

    def write_draft_plan(self, project: PrepareProject) -> None:
        draft = project.root / DRAFT_PLAN_RELPATH
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(DRAFT_PLAN_WITH_TASKS)

    def prepare_ok(self, project: PrepareProject, *extra: str):
        result = run_prepare(PACKET_CLI, *project.args(*extra))
        self.assertEqual(
            result.returncode,
            0,
            "prepare failed: " + result.stderr.decode(errors="replace"),
        )
        return result


class TestPd1DraftPlanIsFirstClass(DraftContractTestCase):
    def test_pd1_prepare_renders_draft_plan_reviewer_packet(self) -> None:
        """PD-1: prepare renders a reviewer packet whose contract object is a
        declared draft plan (kind `draft-plan`, version + authority ref),
        without any approval marking; the emission carries the draft's
        sha/version; validate-packet accepts it; the state binding records
        the draft kind."""
        project = self.project()
        self.write_draft_plan(project)
        self.prepare_ok(
            project,
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )

        expected_contract = {
            "kind": "draft-plan",
            "path": DRAFT_PLAN_RELPATH,
            "sha256": hashlib.sha256(DRAFT_PLAN_WITH_TASKS).hexdigest(),
            "commit": None,
            "plan_version": DRAFT_PLAN_VERSION,
        }

        packet_dir = project.out_dir / project.packet_id()
        request = json.loads((packet_dir / "REQUEST.json").read_text(encoding="utf-8"))
        self.assertEqual(request["contract"], expected_contract)

        metadata, _, _ = parse_packet((packet_dir / "PACKET.md").read_text(encoding="utf-8"))
        # The emitted contract is the draft: same kind/version/sha, non-approved.
        self.assertEqual(metadata["contract"], expected_contract)
        self.assertFalse(
            metadata["contract"]["kind"].startswith("approved-"),
            "draft-plan emission must not carry an approved marking",
        )
        # The review carries its authority reference (who requested the review).
        self.assertEqual(metadata["execution"]["authority_ref"], AUTHORITY_REF)

        state = json.loads(project.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["active_packet"]["contract_kind"], "draft-plan")
        self.assertEqual(state["active_packet"]["contract_sha256"], expected_contract["sha256"])

        common = [
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(packet_dir / "REQUEST.json"),
        ]
        rendered = run_cli_bytes(PACKET_CLI, "render", *common)
        self.assertEqual(rendered.returncode, 0, rendered.stderr.decode(errors="replace"))
        self.assertTrue(rendered.stdout.startswith(PACKET_BEGIN.encode()))
        validated = run_cli_bytes(
            PACKET_CLI, "validate-packet", *common, "--packet", str(packet_dir / "PACKET.md")
        )
        self.assertEqual(validated.returncode, 0, validated.stderr.decode(errors="replace"))


class TestPd1ForgedApprovedKindIsRejected(DraftContractTestCase):
    def test_pd1_forged_approved_kind_over_draft_is_rejected_without_publication(self) -> None:
        """PD-1 (negative): reusing `approved-*` to pass the guard over a
        declared draft plan is detected and rejected: rc != 0 with an ERROR
        diagnostic, empty stdout, no packet published and the state unchanged.

        The test first requires the honest `draft-plan` surface to exist (the
        same object declared as draft is accepted on its own project), so the
        rejection can only come from the forge detection and not from a
        missing feature."""
        project = self.project()
        self.write_draft_plan(project)

        surface = self.project()
        self.write_draft_plan(surface)
        honest = run_prepare(
            PACKET_CLI,
            *surface.args(
                "--contract-kind",
                "draft-plan",
                "--contract-path",
                DRAFT_PLAN_RELPATH,
                "--plan-version",
                DRAFT_PLAN_VERSION,
            ),
        )
        self.assertEqual(
            honest.returncode,
            0,
            "honest draft-plan surface missing (T1 positive): "
            + honest.stderr.decode(errors="replace"),
        )

        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()

        result = run_prepare(
            PACKET_CLI,
            *project.args(
                "--contract-kind",
                "approved-feature-spec",
                "--contract-path",
                DRAFT_PLAN_RELPATH,
                "--plan-version",
                DRAFT_PLAN_VERSION,
            ),
        )

        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"forged approved-* over a declared draft was accepted: {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", "stderr lacks 'ERROR: ...'")
        self.assertEqual(result.stdout, b"", "stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, "state changed")
        self.assertEqual(tree_snapshot(project.root), before, "project tree changed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
