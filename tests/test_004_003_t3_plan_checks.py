#!/usr/bin/env python3
"""RED tests for 004-003 T3 (acceptance criterion 3 + PD-2 separation):
mechanical producer/consumer and dependency checks over a draft plan object.

Contract: docs/specs/004-003-planning-procedures/spec.md — acceptance
criterion 3 ("Fixtures de un plan con entrada sin productor, dependencia
circular, contrato incompatible y paralelismo inválido ejercitan los checks
realmente implementados; un esquema no decide la calidad semántica") and
PD-2 (structural validation — schema/references/rules — is separated from
the semantic judgment the reviewer performs). The four defect fixtures are
the mechanical mirror of the planning contract's blocking findings
(planning-contract-draft.md §5: "entrada necesaria sin productor",
"contratos compatibles", "dependencias honestas — grafo sin ciclos",
"paralelismo seguro") and of the plan's consumer-journey row
("Por cada entrada, identificar productor, consumidor, formato y
verificación"). Test file + fixtures per plan.md T3: `cdad_packet.py`
(validador), `tests/test_004_003_t3_plan_checks.py`.

Black-box: the CLI is invoked as a subprocess; implementation sources are
never read. Every project is a temporary fixture; the real HOME and the
repository state are never touched.

Oracle decisions (interfaces defined by this RED, derived from the spec):
- Surface: the mechanical checks run at `prepare` over the declared
  `draft-plan` contract. `prepare` is the only producer of packets
  (spec invariant 1) and must not publish a packet whose plan object fails
  the structural checks — the same no-publication pattern as the forged
  `approved-*` rejection of T1. A fixture that fails a check is rejected:
  rc != 0, an `ERROR: ...` diagnostic, empty stdout, no packet published,
  unchanged state, unchanged tree.
- Plan task declarations: a fenced ```plan-tasks block (JSON object with a
  `tasks` array) inside the plan file — "una tabla o sección en el plan
  existente" (planning-contract-draft.md §4). The block carries ONLY
  structural facts: task ids, consume entries (artifact + producer +
  contract), produce entries (artifact + contract), depends_on ids,
  parallel ids and files. It carries no quality or semantic grading — the
  schema does not decide plan quality (the reviewer does, PD-2).
- Leniency boundary: a draft plan without a declared ```plan-tasks block is
  NOT rejected by these checks (the T1/T2 draft fixtures have none and stay
  green); requiring the field is T4's postcondition (plan de validación por
  unidad), not T3's.
- The four checks (one fixture per defect, minimal):
  1. input without producer: a consume entry names a producer id that no
     declared task provides → rejected; the diagnostic names the undeclared
     producer id and the unproduced artifact.
  2. circular dependency: depends_on declares a cycle (t1 -> t2 -> t1) →
     rejected; the diagnostic names the cycle members.
  3. incompatible contract: a consume entry demands a contract version that
     differs from the contract the named producer declares for the same
     artifact → rejected; the diagnostic names the artifact and both
     conflicting versions.
  4. invalid parallelism: two tasks declared parallel (mutual `parallel`
     ids) both declare edits to the same file → rejected; the diagnostic
     names the colliding file and both tasks.
  Diagnostics are pinned to the offending tokens only (task ids, artifact
  names, contract versions, file paths), never to exact wording.
- Honest control first (frozen T1/T2 pattern): in every negative test a
  valid plan — acyclic dependencies, matched consume/produce contracts, a
  declared-parallel pair with disjoint files — is accepted first, so a
  rejection can only come from the specific structural defect and not from
  a missing feature, a flag or the fixture shape.
"""

from __future__ import annotations

import hashlib
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


# PD-8 per-task validation fields present on every declared task of this
# file's fixtures (code tasks: non-empty focal_tests; regressions declared;
# gate + owner non-empty). Structural-only facts; the reviewer judges quality.
PLAN_TASKS_VALIDATION = {
    "focal_tests": ["tests/test_004_003_t3_plan_checks.py"],
    "regressions": [],
    "integration_gate": "suite completa una vez por GREEN",
    "owner": "RED: test-writer; GREEN: implementer",
}


def plan_bytes(tasks: list[dict]) -> bytes:
    """A draft plan whose task declarations live in a fenced plan-tasks block."""
    block = json.dumps({"tasks": tasks}, indent=2, sort_keys=True)
    return DRAFT_PLAN_BYTES + PLAN_TASKS_FENCE_OPEN.encode() + block.encode() + b"\n" + PLAN_TASKS_FENCE_CLOSE.encode()


def task(
    task_id: str,
    *,
    consume: list[dict] | None = None,
    produce: list[dict] | None = None,
    depends_on: list[str] | None = None,
    parallel: list[str] | None = None,
    files: list[str] | None = None,
) -> dict:
    entry: dict = {
        "id": task_id,
        "consume": consume or [],
        "produce": produce or [],
        "depends_on": depends_on or [],
        "parallel": parallel or [],
        "files": files or [],
    }
    # PD-8 fixture migration (consecuencia de PD-8/T4 — packet
    # 004-003-planning-procedures-test-writer-red-008): every declared task
    # carries the per-task validation fields PD-8 requires so each block
    # remains a structurally valid plan once T4 makes the block mandatory;
    # the four defect fixtures are then rejected for their OWN structural
    # defect (unproduced input / cycle / contract conflict / file collision)
    # and never merely for a missing validation field. The values are not
    # graded: the checks are structural (PD-2), quality is the reviewer's
    # judgment.
    entry.update(dict(PLAN_TASKS_VALIDATION))
    return entry


# Valid plan: acyclic dependencies, matched consume/produce contracts, a
# declared-parallel pair (t1/t3) with disjoint files. This is the honest
# control — it must pass.
VALID_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        parallel=["t3"],
        files=["tests/only_t1.py"],
    ),
    task(
        "t2",
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
    task(
        "t3",
        produce=[{"artifact": "contract-b", "contract": "b-v1"}],
        parallel=["t1"],
        files=["tests/only_t3.py"],
    ),
]

# Defect 1 — input without producer: t2 consumes "contract-b" from producer
# "t9", which no declared task provides.
INPUT_WITHOUT_PRODUCER_TASKS = [
    task("t1", produce=[{"artifact": "contract-a", "contract": "a-v1"}], files=["tests/only_t1.py"]),
    task(
        "t2",
        consume=[{"artifact": "contract-b", "producer": "t9", "contract": "b-v1"}],
        files=["tests/only_t2.py"],
    ),
]

# Defect 2 — circular dependency: t1 depends_on t2 and t2 depends_on t1, with
# consume/produce contracts fully matched so the cycle is the only defect.
CIRCULAR_DEPENDENCY_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        consume=[{"artifact": "contract-b", "producer": "t2", "contract": "b-v1"}],
        depends_on=["t2"],
        files=["tests/only_t1.py"],
    ),
    task(
        "t2",
        produce=[{"artifact": "contract-b", "contract": "b-v1"}],
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v1"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
]

# Defect 3 — incompatible contract: t1 declares producing "contract-a" as
# "a-v1" while t2 consumes "contract-a" demanding "a-v2".
INCOMPATIBLE_CONTRACT_TASKS = [
    task("t1", produce=[{"artifact": "contract-a", "contract": "a-v1"}], files=["tests/only_t1.py"]),
    task(
        "t2",
        consume=[{"artifact": "contract-a", "producer": "t1", "contract": "a-v2"}],
        depends_on=["t1"],
        files=["tests/only_t2.py"],
    ),
]

# Defect 4 — invalid parallelism: t1 and t2 are declared parallel (mutual
# `parallel` ids, no dependency between them) and both declare edits to the
# same file.
INVALID_PARALLELISM_TASKS = [
    task(
        "t1",
        produce=[{"artifact": "contract-a", "contract": "a-v1"}],
        parallel=["t2"],
        files=["install.sh"],
    ),
    task(
        "t2",
        produce=[{"artifact": "contract-b", "contract": "b-v1"}],
        parallel=["t1"],
        files=["install.sh"],
    ),
]


class PlanChecksCase(unittest.TestCase):
    def project(self) -> PrepareProject:
        temp = tempfile.TemporaryDirectory(prefix="cdad-004-003-t3-")
        self.addCleanup(temp.cleanup)
        return PrepareProject(Path(temp.name).resolve(), "reviewer", "plan-review")

    def write_plan(self, project: PrepareProject, tasks: list[dict]) -> None:
        draft = project.root / DRAFT_PLAN_RELPATH
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(plan_bytes(tasks))

    def draft_flags(self) -> tuple[str, ...]:
        return (
            "--contract-kind",
            "draft-plan",
            "--contract-path",
            DRAFT_PLAN_RELPATH,
            "--plan-version",
            DRAFT_PLAN_VERSION,
        )

    def prepare_valid_control(self) -> None:
        """The honest surface is green: a valid declared-tasks plan renders."""
        control = self.project()
        self.write_plan(control, VALID_TASKS)
        result = run_prepare(PACKET_CLI, *control.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "honest valid-plan surface missing (T3 control): "
            + result.stderr.decode(errors="replace"),
        )
        packet_dir = control.out_dir / control.packet_id()
        self.assertTrue(
            (packet_dir / "PACKET.md").is_file(),
            "the valid plan did not render its packet",
        )

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
            f"plan fixture accepted despite a structural defect: {stderr!r}",
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


class TestAc3ValidPlanPasses(PlanChecksCase):
    def test_ac3_valid_declared_tasks_plan_renders_and_validates(self) -> None:
        """AC-3 (positive): a plan whose declared tasks have acyclic
        dependencies, matched consume/produce contracts and a declared
        parallel pair with disjoint files is accepted: prepare renders the
        plan-review packet and validate-packet accepts the emission. The
        checks do not reject a plan merely for declaring structure."""
        project = self.project()
        self.write_plan(project, VALID_TASKS)
        result = run_prepare(PACKET_CLI, *project.args(*self.draft_flags()))
        self.assertEqual(
            result.returncode,
            0,
            "a valid declared-tasks plan was rejected: " + result.stderr.decode(errors="replace"),
        )

        packet_dir = project.out_dir / project.packet_id()
        request_path = packet_dir / "REQUEST.json"
        packet_path = packet_dir / "PACKET.md"
        self.assertTrue(request_path.is_file(), "REQUEST.json missing")
        self.assertTrue(packet_path.is_file(), "PACKET.md missing")

        request = json.loads(request_path.read_text(encoding="utf-8"))
        self.assertEqual(request["contract"]["kind"], "draft-plan")
        self.assertEqual(
            request["contract"]["sha256"],
            hashlib.sha256(plan_bytes(VALID_TASKS)).hexdigest(),
        )

        common = [
            "--project-root",
            str(project.root),
            "--execution-context",
            str(project.execution_path),
            "--request",
            str(request_path),
        ]
        from tests.test_packet_prepare import run_cli_bytes

        validated = run_cli_bytes(
            PACKET_CLI, "validate-packet", *common, "--packet", str(packet_path)
        )
        self.assertEqual(
            validated.returncode,
            0,
            "validate-packet rejected the emission of a valid plan: "
            + validated.stderr.decode(errors="replace"),
        )


class TestAc3InputWithoutProducerIsRejected(PlanChecksCase):
    def test_ac3_unproduced_input_rejected_with_specific_diagnostic(self) -> None:
        """AC-3 (defect 1) + planning contract blocking finding "entrada
        necesaria sin productor": a consume entry naming a producer that no
        declared task provides is rejected with a diagnostic naming the
        undeclared producer id and the unproduced artifact; nothing is
        published."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, INPUT_WITHOUT_PRODUCER_TASKS)
        self.assert_rejected_without_publication(project, ("t9", "contract-b"))


class TestAc3CircularDependencyIsRejected(PlanChecksCase):
    def test_ac3_circular_dependency_rejected_with_specific_diagnostic(self) -> None:
        """AC-3 (defect 2) + planning contract "grafo sin ciclos no
        resueltos": a depends_on cycle (t1 -> t2 -> t1) with otherwise
        consistent contracts is rejected with a diagnostic naming the cycle
        members; nothing is published."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, CIRCULAR_DEPENDENCY_TASKS)
        self.assert_rejected_without_publication(project, ("t1", "t2"))


class TestAc3IncompatibleContractIsRejected(PlanChecksCase):
    def test_ac3_incompatible_contract_rejected_with_specific_diagnostic(self) -> None:
        """AC-3 (defect 3) + planning contract "contratos compatibles": a
        consume entry demanding "a-v2" of "contract-a" while its declared
        producer produces "a-v1" is rejected with a diagnostic naming the
        artifact and both conflicting versions; nothing is published."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, INCOMPATIBLE_CONTRACT_TASKS)
        self.assert_rejected_without_publication(project, ("contract-a", "a-v1", "a-v2"))


class TestAc3InvalidParallelismIsRejected(PlanChecksCase):
    def test_ac3_invalid_parallelism_rejected_with_specific_diagnostic(self) -> None:
        """AC-3 (defect 4) + planning contract "paralelismo seguro": two
        tasks declared parallel (mutual `parallel` ids, no dependency) that
        both declare edits to the same file are rejected with a diagnostic
        naming the colliding file and both tasks; nothing is published."""
        self.prepare_valid_control()

        project = self.project()
        self.write_plan(project, INVALID_PARALLELISM_TASKS)
        self.assert_rejected_without_publication(project, ("install.sh", "t1", "t2"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
