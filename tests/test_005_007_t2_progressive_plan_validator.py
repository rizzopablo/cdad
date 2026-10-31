#!/usr/bin/env python3
"""RED tests for 005-007 T2 (PD-1/PD-2 + AC-1): the plan-tasks validator
accepts progressive detail without weakening the fail-closed behavior or the
mechanical checks.

Contract: docs/specs/005-007-progressive-planning/spec.md —
- **PD-1 (detalle progresivo):** the canonical plan-tasks block admits, per
  task, a closed field `detail` with values `"next"` (default) and
  `"planned"`. Every task ALWAYS declares a non-empty `objective` and its
  `depends_on`. A task with `detail == "planned"` additionally declares
  non-empty `uncertainty`, `owner` and `resolves_when`, and is NOT required
  to declare the per-task validation plan (`focal_tests`/
  `observable_checks`/`regressions`/`integration_gate`); a `"next"` or
  unmarked task keeps declaring the per-task validation plan.
- **PD-2 (el validador acepta el detalle progresivo sin debilitar el
  fail-closed):** `_check_plan_validation_plan` treats a
  `detail == "planned"` task by its own fields and demands the per-task
  validation plan only from `"next"`/unmarked tasks. The mechanical checks
  (input without producer, cycle, incompatible contract, unsafe parallelism)
  keep applying to ALL declared tasks, planned included. A `detail` outside
  the closed set fails closed naming the task and the value; a malformed or
  absent plan-tasks block keeps failing closed without publishing. A block
  without the marker behaves EXACTLY as today.

Oracle decisions (interfaces defined by this RED, derived only from the
contract — the test-writer never reads implementation):

- Surface: behavior through the public CLI — `prepare` over a temp project
  with a declared draft plan (contract kind `draft-plan`), the frozen
  fixture pattern of 004-003 T3/T4 (tests/test_004_003_t1_draft_contract.py,
  tests/test_004_003_t3_plan_checks.py,
  tests/test_004_003_t4_validation_fields.py). The plan-tasks block format
  (canonical fence + JSON object with a `tasks` array) is the already-green
  format of those fixtures; no new harness is invented and nothing depends
  on the real repository state or host-absolute paths.
- A progressive planned task declares: `detail: "planned"`, non-empty
  `objective`, `depends_on`, non-empty `uncertainty`/`owner`/
  `resolves_when`, and NO per-task validation fields. A `"next"`/unmarked
  code task keeps the PD-8 validation fields proven by the 004-003 T4
  fixtures.
- Positives: rc == 0 and the packet is published (PACKET.md exists).
- Negatives: rc != 0, an `ERROR: ...` diagnostic, empty stdout, no packet
  published, unchanged state, unchanged tree. Diagnostics are pinned to the
  offending tokens only (task ids, field names, producer ids, artifact
  names, the offending `detail` value) — never to exact wording.
- Honest control first (frozen 004-003 pattern): every negative test first
  proves a green surface — the valid unmarked plan renders — and the
  mechanical-check cases first prove the honest mixed progressive plan
  (planned producer + next consumer, matched contracts) is accepted, so a
  rejection can only come from the specific defect and never from the
  fixture shape or a missing feature.
- RED declaration (substage red): the tests demanding the missing
  progressive behavior fail TODAY with AssertionError (today every declared
  task still owes the per-task validation plan and the validator does not
  treat `planned` tasks by their own fields — the honest progressive
  surface is rejected, and the PD-1 field diagnostics do not exist). Cases
  5 and 6 are regression controls whose postconditions are "exactly as
  today"; they are green today BY DESIGN and their job is to forbid a
  behavior change when the progressive treatment lands.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tests.test_004_003_t1_draft_contract import (
    DRAFT_PLAN_BYTES,
    DRAFT_PLAN_RELPATH,
    DRAFT_PLAN_VERSION,
)
from tests.test_packet_prepare import PACKET_CLI, PrepareProject, run_prepare, tree_snapshot


PLAN_TASKS_FENCE_OPEN = "```plan-tasks\n"
PLAN_TASKS_FENCE_CLOSE = "```"

_SENTINEL = object()


def plan_bytes(tasks: list[dict]) -> bytes:
    """A declared draft plan whose task declarations live in the canonical
    fenced plan-tasks block (format proven green by 004-003 T3/T4)."""
    block = json.dumps({"tasks": tasks}, indent=2, sort_keys=True)
    return (
        DRAFT_PLAN_BYTES
        + PLAN_TASKS_FENCE_OPEN.encode()
        + block.encode()
        + b"\n"
        + PLAN_TASKS_FENCE_CLOSE.encode()
    )


def planned_task(
    task_id: str,
    *,
    detail: str = "planned",
    objective=_SENTINEL,
    uncertainty=_SENTINEL,
    owner=_SENTINEL,
    resolves_when=_SENTINEL,
    produce=_SENTINEL,
    consume=_SENTINEL,
    depends_on=_SENTINEL,
    parallel=_SENTINEL,
    files=_SENTINEL,
) -> dict:
    """A progressive task: objective + dependencies always; uncertainty +
    owner + resolves_when for the planned marking; NO per-task validation
    plan (PD-1). A `None` argument OMITS that field (the negative fixtures)."""
    entry: dict = {
        "id": task_id,
        "detail": detail,
        "produce": [
            {"artifact": "contract-a", "contract": "a-v1"}
        ] if produce is _SENTINEL else produce,
        "consume": [] if consume is _SENTINEL else consume,
        "depends_on": [] if depends_on is _SENTINEL else depends_on,
        "parallel": [] if parallel is _SENTINEL else parallel,
        "files": [] if files is _SENTINEL else files,
    }
    for field, value, default in (
        ("objective", objective, "Objetivo completo de la unidad planificada (sin detalle falso)."),
        ("uncertainty", uncertainty, "Incertidumbre declarada de la unidad planificada."),
        ("owner", owner, "orchestrator"),
        ("resolves_when", resolves_when, "revision de la tanda del epic"),
    ):
        if value is None:
            continue  # A name-as-absent field stays REALLY absent (negative fixtures).
        entry[field] = default if value is _SENTINEL else value
    for field in (
        "objective",
        "uncertainty",
        "owner",
        "resolves_when",
        "produce",
        "consume",
        "depends_on",
        "parallel",
        "files",
    ):
        if field in entry and entry[field] is None:
            del entry[field]
    return entry


# The per-task validation plan PD-8 demands from every "next"/unmarked task
# (the already-green shape of 004-003 T4's CODE_VALIDATION).
NEXT_CODE_VALIDATION = {
    "focal_tests": ["tests/only_next.py"],
    "regressions": [],
    "integration_gate": "suite completa una vez por GREEN",
    "owner": "RED: test-writer; GREEN: implementer",
}


def next_task(
    task_id: str,
    *,
    detail=_SENTINEL,
    produce=_SENTINEL,
    consume=_SENTINEL,
    depends_on=_SENTINEL,
    parallel=_SENTINEL,
    files=_SENTINEL,
) -> dict:
    """A next/unmarked code task keeping today's per-task validation plan."""
    entry: dict = {
        "id": task_id,
        "produce": [] if produce is _SENTINEL else produce,
        "consume": [] if consume is _SENTINEL else consume,
        "depends_on": [] if depends_on is _SENTINEL else depends_on,
        "parallel": [] if parallel is _SENTINEL else parallel,
        "files": ["tests/only_t1.py"] if files is _SENTINEL else files,
    }
    if detail is not _SENTINEL:
        entry["detail"] = detail
    entry.update(dict(NEXT_CODE_VALIDATION))
    return entry


# Case 1 / honest progressive surface: one planned task with its own fields
# and NO per-task validation plan. Accepted by PD-1/PD-2; rejected today.
PLANNED_ONLY_TASKS = [planned_task("t1")]

# Honest mixed surface (mechanical-check controls): the planned task produces
# "contract-b"; the next code task consumes it from producer t1 — contracts
# matched, dependencies acyclic, disjoint files. Must be accepted (PD-2 keeps
# the planned task inside the same declared block).
MIXED_MATCHED_TASKS = [
    planned_task("t1", produce=[{"artifact": "contract-b", "contract": "b-v1"}]),
    next_task(
        "t2",
        consume=[{"artifact": "contract-b", "producer": "t1", "contract": "b-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
]

# Mechanical defect 1 — input without producer: the next task consumes
# "contract-b" from producer "t9", which no declared task provides.
UNPRODUCED_INPUT_TASKS = [
    planned_task("t1", produce=[{"artifact": "contract-b", "contract": "b-v1"}]),
    next_task(
        "t2",
        consume=[{"artifact": "contract-b", "producer": "t9", "contract": "b-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
]

# Mechanical defect 2 — circular dependency including the planned task:
# planned t1 depends_on t2 and next t2 depends_on t1, with consume/produce
# contracts matched so the cycle is the only defect.
CYCLE_WITH_PLANNED_TASKS = [
    planned_task("t1", depends_on=["t2"]),
    next_task(
        "t2",
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
]


class T2ValidatorCase(unittest.TestCase):
    def project(self) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-005-007-t2-")
        self.addCleanup(temp.cleanup)
        project = PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")
        # 010-004 T2 POST-AUDIT (PC-04/§4.1): contexto canónico materializado
        # en la construcción (ver ObjectFormCase.project para la convención).
        _ = project.execution_path
        return project

    @staticmethod
    def draft_flags() -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )

    def write_plan_bytes(self, project: PrepareProject, data: bytes) -> None:
        draft = project.root / DRAFT_PLAN_RELPATH
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(data)

    def write_plan(self, project: PrepareProject, tasks: list[dict]) -> None:
        self.write_plan_bytes(project, plan_bytes(tasks))

    def assert_accepted_and_published(self, project: PrepareProject) -> None:
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "the honest progressive plan was rejected: "
            + result.stderr.decode(errors="replace"),
        )
        packet_dir = project.out_dir / project.packet_id()
        self.assertTrue(
            (packet_dir / "PACKET.md").is_file(),
            "the accepted plan did not render its packet",
        )

    def prepare_valid_control(self) -> None:
        """The honest unmarked surface is green: a plan whose declared tasks
        carry today's per-task validation plan renders its packet."""
        control = self.project()
        self.write_plan(control, [next_task("t1")])
        self.assert_accepted_and_published(control)

    def assert_rejected_without_publication(
        self, project: PrepareProject, tokens: tuple[str, ...]
    ) -> None:
        before = tree_snapshot(project.root)
        state_before = project.state_path.read_bytes()
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))

        stderr = result.stderr.decode(errors="replace")
        self.assertNotEqual(
            result.returncode,
            0,
            f"plan accepted despite a required postcondition: {stderr!r}",
        )
        self.assertRegex(stderr, r"(?m)^ERROR: ", f"stderr lacks 'ERROR: ...': {stderr!r}")
        for token in tokens:
            self.assertIn(
                token,
                stderr,
                f"the diagnostic does not name the offending token {token!r}: {stderr!r}",
            )
        self.assertEqual(result.stdout, b"", "stdout must be empty")
        self.assertEqual(list(project.out_dir.iterdir()), [], "out-dir gained entries")
        self.assertEqual(project.state_path.read_bytes(), state_before, "state changed")
        self.assertEqual(tree_snapshot(project.root), before, "project tree changed")


class TestPd2ProgressivePlannedIsAccepted(T2ValidatorCase):
    def test_pd2_planned_task_without_validation_plan_is_accepted(self) -> None:
        """PD-1/PD-2 + AC-1 (positive): a plan whose plan-tasks block declares
        a task with `detail: "planned"` + non-empty objective + depends_on +
        uncertainty + owner + resolves_when, WITHOUT the per-task validation
        plan, is ACCEPTED by `prepare` (rc == 0) and its packet is published.
        Today the validator still demands the per-task validation plan from
        every declared task, so the honest progressive surface is missing."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, PLANNED_ONLY_TASKS)
        self.assert_accepted_and_published(project)


class TestPd1PlannedFieldNegativesAreRejected(T2ValidatorCase):
    def test_pd2_planned_missing_progressive_field_is_rejected(self) -> None:
        """PD-1/PD-2 + AC-1 (negative): a `"planned"` task missing one of its
        own fields — objective / uncertainty / owner / resolves_when, one
        case each — is rejected (rc != 0) with a diagnostic naming the task
        and the missing field; nothing is published."""
        self.prepare_valid_control()

        for field in ("objective", "uncertainty", "owner", "resolves_when"):
            with self.subTest(missing=field):
                project = self.project()
                self.write_plan(project, [planned_task("t1", **{field: None})])
                self.assert_rejected_without_publication(
                    project, ("t1", field)
                )


class TestPd2UnknownDetailFailsClosed(T2ValidatorCase):
    def test_pd2_detail_outside_closed_set_is_rejected(self) -> None:
        """PD-2 + INV-4 + AC-1: a `detail` value outside the closed set
        ("next" | "planned") fails closed: rc != 0 with a diagnostic naming
        the task and the offending value; nothing is published. Today the
        validator does not know the closed set, so the value is never named."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, [planned_task("t1", detail="later")])
        self.assert_rejected_without_publication(project, ("t1", "later"))


class TestPd2MechanicalChecksApplyToPlanned(T2ValidatorCase):
    def test_pd2_mechanical_checks_apply_to_planned_tasks(self) -> None:
        """PD-2 + AC-1: the mechanical checks keep applying to ALL declared
        tasks, planned included. Two defects over otherwise-valid progressive
        plans:
        1. input without producer: the next task consumes "contract-b" from
           undeclared producer "t9" → rejected naming the producer and the
           artifact;
        2. cycle: the planned t1 depends_on t2 and t2 depends_on t1 →
           rejected naming the cycle members.
        Both cases first require the honest mixed progressive plan (matched
        contracts, acyclic) to be ACCEPTED, so a rejection can only come
        from the specific mechanical defect and never from the planned
        marking itself."""
        self.prepare_valid_control()

        with self.subTest(defect="input-without-producer"):
            control = self.project()
            self.write_plan(control, MIXED_MATCHED_TASKS)
            self.assert_accepted_and_published(control)

            project = self.project()
            self.write_plan(project, UNPRODUCED_INPUT_TASKS)
            self.assert_rejected_without_publication(project, ("t9", "contract-b"))

        with self.subTest(defect="circular-dependency"):
            control = self.project()
            self.write_plan(control, MIXED_MATCHED_TASKS)
            self.assert_accepted_and_published(control)

            project = self.project()
            self.write_plan(project, CYCLE_WITH_PLANNED_TASKS)
            self.assert_rejected_without_publication(project, ("t1", "t2"))


class TestPd2NoMarkerRegression(T2ValidatorCase):
    def test_pd2_unmarked_code_task_without_validation_plan_is_rejected(self) -> None:
        """PD-2 (regresión): a plan-tasks block WITHOUT the `detail` marker
        behaves exactly as today — a code task declaring neither focal_tests
        nor observable_checks is rejected for the missing per-task validation
        plan, with a diagnostic naming the task and the field; nothing is
        published."""
        self.prepare_valid_control()

        project = self.project()
        unmarked_without_validation_plan = {
            "id": "t1",
            "produce": [{"artifact": "contract-a", "contract": "a-v1"}],
            "consume": [],
            "depends_on": [],
            "parallel": [],
            "files": ["tests/only_t1.py"],
        }
        self.write_plan(project, [unmarked_without_validation_plan])
        self.assert_rejected_without_publication(project, ("t1", "focal_tests"))


class TestPd2NextAndUnmarkedStillAccepted(T2ValidatorCase):
    def test_pd2_next_and_unmarked_valid_plans_still_accepted(self) -> None:
        """PD-1/PD-2 (regresión): a plan whose tasks are all `"next"` (or
        carry no marker at all) with the complete per-task validation plan is
        still accepted exactly like today — both variants render their
        packets."""
        self.prepare_valid_control()

        for variant, tasks in (
            ("detail next explicit", [next_task("t1", detail="next")]),
            ("no marker", [next_task("t1")]),
        ):
            with self.subTest(variant=variant):
                project = self.project()
                self.write_plan(project, tasks)
                self.assert_accepted_and_published(project)


if __name__ == "__main__":
    unittest.main(verbosity=2)
